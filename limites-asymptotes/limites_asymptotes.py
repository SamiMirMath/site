"""
limites_asymptotes.py — Limites aux bornes de l'ED et asymptotes.

Réutilise ensemble_def.py (parseur, arbre, ED, système de polynômes exacts, pont
SymPy). Ne dépend pas de derivee_variations.py : les asymptotes portent sur f,
pas sur f'.

Méthode :
  - Fonction rationnelle en x, en ±∞ : on factorise numérateur et dénominateur par
    leur terme de plus haut degré, explicitement — pas juste « on compare les
    degrés ». Donne directement l'asymptote horizontale ou oblique (avec la
    division polynomiale exacte pour l'oblique), sans recours au calcul formel.
  - Pôle fini d'une fonction rationnelle : on factorise, on détermine le signe de
    chaque côté ⇒ asymptote verticale ; si le numérateur s'annule aussi au même
    point (forme 0/0), f n'y est pas définie mais sa limite est finie : un trou, pas une asymptote —
    le calcul formel (SymPy) tranche cette limite indéterminée.
  - Cas transcendants (ln, exp, racine mélangés à x) : le calcul formel donne la
    valeur de référence ; la rédaction (Q9) applique les règles du cours sur l'arbre
    (opérations et composition de limites), nomme la forme indéterminée, recoupe chaque
    limite écrite avec le calcul formel, et se replie sur le résultat seul, avec une
    phrase honnête, dès qu'une étape ne peut pas être justifiée.
"""
import json
import re
from fractions import Fraction as F

from noyau import (
    Nb, X, E, Neg, Op, Fn,
    lire, tex, prec, valeur_constante, Num, Iv, REELS, fusion, inter, ens_tex,
    contient, proche, evaluer, sans_x, qtex, ptex, pn, deg, peval, pdivlin, pmul, nul, padd, pscal,
    decomposer, r_norm, json_strict, ajouter_saisie,
    charger_sympy, en_sympy_reel, arbre_depuis_sympy, num_sympy, SYMPY,
    txt, NonPrisEnCharge, ErreurSaisie, analyser_complet, apercu_json,
    signe_facteur, tableau_facteurs, en_sympy, aplatir, domaine, complement,
)


__all__ = ["etudier", "etudier_json", "apercu_json"]


# =====================================================================
# Petits outils
# =====================================================================
def _pdiv(N, D):
    """Division polynomiale exacte N = D·Q + R, deg(R) < deg(D)."""
    N, D = pn(N), pn(D)
    dD = deg(D)
    R = list(N)
    Q = [F(0)] * max(1, deg(pn(N)) - dD + 1)
    while True:
        R = pn(R)
        dR = deg(R)
        if dR < dD or (len(R) == 1 and R[0] == 0):
            break
        c = R[-1] / D[-1]
        k = dR - dD
        if k >= len(Q):
            Q += [F(0)] * (k - len(Q) + 1)
        Q[k] += c
        for i, d in enumerate(D):
            R[i + k] -= c * d
    return pn(Q), pn(R)


def _sympify_point(num):
    sp = charger_sympy()
    return sp.sympify(num.py, locals={"sqrt": sp.sqrt, "exp": sp.exp, "log": sp.log, "pi": sp.pi})


def _rejete(r):
    """Résultat SymPy inutilisable : absent, symbole libre, i, zoo, nan, AccumBounds, partie imaginaire, ou infini mêlé à autre chose
    (oo·(−1)^(2/3)…). ±∞ seuls sont acceptés."""
    sp = charger_sympy()
    if r is None:
        return True
    if r == sp.oo or r == -sp.oo:
        return False
    if r.free_symbols or r.has(sp.I, sp.zoo, sp.nan, sp.AccumBounds, sp.oo, -sp.oo) or r.is_real is False:
        return True
    if r.is_real is None:
        try:
            return abs(complex(sp.N(r, 30)).imag) > 1e-20
        except Exception:
            return True
    return False


def _limite_brute(fe, point, direction):
    """Limite SymPy de fe (expression SymPy) ; une réponse inutilisable (point irrationnel : SymPy laisse parfois x, i·π…) est
    reprise par composition quand fe est ln(u) ou e^u. None si l'on ne conclut pas."""
    sp = charger_sympy()
    try:
        r = sp.limit(fe, SYMPY["x"], point, dir=direction) if direction else sp.limit(fe, SYMPY["x"], point)
    except Exception:
        r = None
    if not _rejete(r):
        return r
    if isinstance(fe, (sp.log, sp.exp)):
        return _par_composition(fe, point, direction)
    return None


def _par_composition(fe, point, direction):
    """ln(u) ou e^u : limite de u (calculée à part), puis de la fonction extérieure ; None si le cas n'est pas net."""
    sp = charger_sympy()
    u = fe.args[0]
    ru = _limite_brute(u, point, direction)
    if ru is None:
        return None
    if isinstance(fe, sp.exp):
        return sp.oo if ru == sp.oo else sp.Integer(0) if ru == -sp.oo else sp.exp(ru)
    if ru == sp.oo:
        return sp.oo
    if ru == -sp.oo:
        return None
    if ru == 0:
        return -sp.oo if _limite_brute(1 / u, point, direction) == sp.oo else None     # u → 0⁺
    return sp.log(ru) if ru.is_positive else None


def _contient_ln(n):
    if isinstance(n, Fn):
        return n.nom == "ln" or _contient_ln(n.a)
    if isinstance(n, Neg):
        return _contient_ln(n.a)
    return isinstance(n, Op) and (_contient_ln(n.a) or _contient_ln(n.b))


def _sonde_lointaine(n):
    """Les sondes 10^100 et 10^1000 ne servent qu'aux fonctions avec ln (convergence lente), sans exponentielle."""
    return _contient_ln(n) and not _contient_exp(n)


def _contient_exp(n):
    """Exponentielle ou exposant variable : e^(10^1000) coûte cher à évaluer, la sonde se limite alors aux points ordinaires."""
    if isinstance(n, Fn):
        return n.nom == "exp" or _contient_exp(n.a)
    if isinstance(n, Neg):
        return _contient_exp(n.a)
    return isinstance(n, Op) and (_contient_exp(n.a) or _contient_exp(n.b) or (n.op == "^" and not sans_x(n.b)))


def _val_mp(mp, n, x):
    """Valeur de l'arbre n en x (mpmath, haute précision) ; None si n n'est pas défini en x (mêmes conventions que le cours)."""
    if isinstance(n, Nb):
        return mp.mpf(n.v.numerator) / n.v.denominator
    if isinstance(n, X):
        return x
    if isinstance(n, E):
        return mp.e
    if isinstance(n, Neg):
        a = _val_mp(mp, n.a, x)
        return None if a is None else -a
    if isinstance(n, Fn):
        a = _val_mp(mp, n.a, x)
        if a is None:
            return None
        if n.nom == "ln":
            return mp.log(a) if a > 0 else None
        if n.nom == "sqrt":
            return mp.sqrt(a) if a >= 0 else None
        return mp.exp(a)
    a = _val_mp(mp, n.a, x)
    b_exp = valeur_constante(n.b) if n.op == "^" else None
    if a is None:
        return None
    if n.op == "^":
        if b_exp is None or isinstance(b_exp, float):
            b = _val_mp(mp, n.b, x)
            return None if (b is None or a <= 0) else mp.exp(b * mp.log(a))
        if b_exp == 0:
            return mp.mpf(1)
        if a == 0:
            return mp.mpf(0) if b_exp > 0 else None
        if b_exp.denominator == 1:
            return a ** int(b_exp)
        if a < 0:
            if b_exp.denominator % 2 == 0:
                return None
            r = (-a) ** (mp.mpf(b_exp.numerator) / b_exp.denominator)
            return -r if b_exp.numerator % 2 else r
        return a ** (mp.mpf(b_exp.numerator) / b_exp.denominator)
    b = _val_mp(mp, n.b, x)
    if b is None:
        return None
    if n.op == "+":
        return a + b
    if n.op == "-":
        return a - b
    if n.op == "*":
        return a * b
    return None if b == 0 else a / b


def _quotient_mp(mp, f, t):
    v = _val_mp(mp, f, t)
    return None if v is None else v / t


def _moins_ax_mp(mp, f, a, t):
    v = _val_mp(mp, f, t)
    return None if v is None else v - mp.mpf(str(a)) * t


def _contradit_par_sonde(g, avec_ln, point, direction, r):
    """True si la sonde haute précision CONTREDIT nettement la valeur SymPy r (signe opposé, infini contre fini, fini contre infini,
    écart qui ne décroît pas). Une convergence lente (ln) n'est pas une contradiction ; en cas de doute (mpmath absent, trop peu de points
    évaluables) : False. g(mp, x) = valeur de la fonction sondée ; x → point, du côté de `direction` (les deux si None)."""
    sp = charger_sympy()
    try:
        import mpmath
        infini = point in (sp.oo, -sp.oo)
        rationnel = (not infini) and point.is_Rational
        valeur_infinie = r == sp.oo or r == -sp.oo
        # sondes très lointaines (10^100, 10^1000) pour les logarithmes, qui convergent lentement ; inutiles (et fragiles : les
        # compensations s'arrondissent à 0) pour une valeur infinie, qui se juge sur la croissance
        fin_ln = [100, 1000] if avec_ln and not valeur_infinie and (infini or rationnel) else []
        ks = [2, 4, 8, 16, 30] + fin_ln if infini else [3, 6, 12, 30] + fin_ln
        mp = mpmath.MPContext()
        mp.dps = 60 + 2 * max(ks)
        if infini:
            centre, signe = None, 1 if point == sp.oo else -1
        else:
            centre = mp.mpf(point.p) / point.q if rationnel else mp.mpf(str(sp.N(point, mp.dps)))
        cotes = (1,) if direction == "+" else (-1,) if direction == "-" else (-1, 1)
        if r == sp.oo or r == -sp.oo:
            s = 1 if r == sp.oo else -1
            cible = None
        else:
            s, cible = 0, mp.mpf(str(sp.N(r, mp.dps)))
        for cote in (cotes if not infini else (1,)):
            vals = []
            for k in ks:
                x = signe * mp.mpf(10) ** k if infini else centre + cote * mp.mpf(10) ** (-k)
                try:
                    v = g(mp, x)
                except (ArithmeticError, ValueError, OverflowError):
                    v = None
                if v is not None:
                    vals.append(v)
            if len(vals) < 2:
                continue
            if cible is None:
                if s * vals[-1] <= 0 or abs(vals[-1]) <= abs(vals[-2]):
                    return True
            else:
                ecarts = [abs(v - cible) for v in vals]       # le meilleur écart : les sondes extrêmes peuvent s'arrondir à 0
                if min(ecarts) > max(ecarts[0] / 2, mp.mpf(10) ** -25 * (1 + abs(cible))):
                    return True
        return False
    except Exception:
        return False


def _limite_sympy(f, point, direction=None):
    """point : sp.oo, -sp.oo, ou objet SymPy exact. direction : '+', '-' ou None. Renvoie la valeur SymPy (±oo ou nombre réel
    exact), jamais un résultat avec symbole libre, i, zoo, nan… ; None si l'on ne conclut pas ou si la sonde la contredit."""
    sp = charger_sympy()
    if sp is None:
        return None
    try:
        r = _limite_brute(en_sympy_reel(f), point, direction)
    except Exception:
        return None
    if _rejete(r) or _contradit_par_sonde(lambda mp, x: _val_mp(mp, f, x), _sonde_lointaine(f), point, direction, r):
        return None
    return r


def _valeur_tex(res_sympy):
    """Valeur SymPy (finie, +oo, -oo) → (texte tex, est_infinie, est_plus, valeur_num) ; « ? » si elle est absente ou inutilisable."""
    sp = charger_sympy()
    if _rejete(res_sympy):
        return "?", False, None, None
    if res_sympy == sp.oo:
        return r"+\infty", True, True, None
    if res_sympy == -sp.oo:
        return r"-\infty", True, False, None
    try:
        n = num_sympy(res_sympy)
        return n.tex, False, None, n.val
    except Exception:
        return "?", False, None, None


# =====================================================================
# Bornes à étudier (déduites de l'ED, déjà calculée)
# =====================================================================
def _bornes(ED):
    ivs = fusion(ED)
    out = []
    if not ivs:
        return out
    if ivs[0].lo is None:
        out.append({"type": "inf", "signe": -1})
    elif not ivs[0].lf:
        out.append({"type": "fini", "point": ivs[0].lo, "cote": "droite"})
    if ivs[-1].hi is None:
        out.append({"type": "inf", "signe": 1})
    elif not ivs[-1].hf:
        out.append({"type": "fini", "point": ivs[-1].hi, "cote": "gauche"})
    for i in range(len(ivs) - 1):
        a, b = ivs[i].hi, ivs[i + 1].lo
        if a is not None and b is not None and proche(a.val, b.val):
            out.append({"type": "fini", "point": a, "cote": "deux"})
        else:
            if a is not None and not ivs[i].hf:
                out.append({"type": "fini", "point": a, "cote": "gauche"})
            if b is not None and not ivs[i + 1].lf:
                out.append({"type": "fini", "point": b, "cote": "droite"})
    return out


# =====================================================================
# Cas 1 : f rationnelle en x, étude en ±∞ (toujours exact, jamais SymPy)
# =====================================================================
def _monome_tex(c, k):
    """c·x^k (k ≥ 0), coefficient 1 ou puissance 0/1 simplifiés à l'affichage."""
    if k == 0:
        return qtex(c)
    p = "x" if k == 1 else f"x^{{{k}}}"
    if c == 1:
        return p
    if c == -1:
        return "-" + p
    return qtex(c) + r"\," + p


def _terme_tex(ratio, k):
    """ratio·x^k, k pouvant être négatif (écrit alors comme une fraction : 3/(2x), 1/x², -5/x)."""
    if k >= 0:
        return _monome_tex(ratio, k)
    p = "x" if k == -1 else f"x^{{{-k}}}"
    signe = "-" if ratio < 0 else ""
    num, den = abs(ratio.numerator), ratio.denominator
    return rf"{signe}\dfrac{{{num}}}{{{p if den == 1 else str(den) + p}}}"


def _facteur_detaille(P, n):
    """P(x) = a_n·x^n·(1 + ... ), avec CHAQUE terme restant écrit explicitement
    (jamais de « ... ») : ex. x^2 - 1 = x^2(1 - 1/x^2).
    Renvoie (tête a_n·x^n, parenthèse intérieure, expression complète, termes intérieurs [(signe, tex)])."""
    an = P[n]
    interieur = "1"
    termes = []
    for k in range(n - 1, -1, -1):
        c = P[k] if k < len(P) else F(0)
        if c == 0:
            continue
        ratio = c / an
        t = _terme_tex(abs(ratio), k - n)
        termes.append(("-" if ratio < 0 else "+", t))
        interieur += (" - " if ratio < 0 else " + ") + t
    tete = _monome_tex(an, n)
    complet = tete if interieur == "1" else tete + r"\left(" + interieur + r"\right)"
    return tete, interieur, complet, termes


def _enumerer(elements):
    """A ; A et B ; A, B et C."""
    return elements[0] if len(elements) == 1 else ", ".join(elements[:-1]) + " et " + elements[-1]


def _terme_signe_tex(P, k):
    """Terme c·x^k de P, avec son signe (-3x, x^{3}, 5)."""
    return ptex(pn([F(0)] * k + [P[k]]), "x")


def _polynome_a_termes(P):
    return [k for k in range(len(P) - 1, -1, -1) if P[k] != 0]


def _limite_polynome_infini(P, s):
    """Limite en s∞ d'un polynôme : celle de son terme de plus haut degré (Lim)."""
    n = deg(P)
    if n == 0:
        return Lim.fin(P[0], None)
    return Lim.infini(_signe(P[n]) * (s if n % 2 else 1))


def _polynome_infini(P, s, n, ctx):
    """Somme de plusieurs termes en s∞. Termes de même sens : la limite est celle du terme de plus haut degré (rien à écrire).
    Termes opposés : si n est la limite étudiée, forme indéterminée « ∞ − ∞ » levée par une chaîne (mise en évidence) ; sinon
    le terme dominant donne la limite (remarque en mots, voir _atome). Renvoie (Lim, lignes)."""
    ks = [k for k in _polynome_a_termes(P) if k >= 1]
    signes = {_signe(P[k]) * (s if k % 2 else 1) for k in ks}
    tete_lim = Lim.infini(_signe(P[deg(P)]) * (s if deg(P) % 2 else 1))
    if len(signes) == 1 or n is not ctx.f:
        return tete_lim, []
    A = _membre_en_evidence(n, s)
    g = A["evid"]
    ch = ctx.chaine(n)
    ctx.remarques = []
    ch.annoncer(_guil(_atome(n, ctx, True)) + r"\text{ : forme indéterminée}")
    ch.lim(tex(g), r"\text{mise en évidence}", g)
    avant = _conclure(ch, g, tete_lim, ctx)
    return tete_lim, avant + [ch]


def _fraction_const_infini(N, D, s):
    """Constante sur polynôme non constant en s∞ : la limite est 0 (la chaîne écrit « c/±∞ » = 0)."""
    LD = _limite_polynome_infini(D, s)
    return Lim.fin(0, _signe(N[0]) * LD.inf)


def _suite_signee(P):
    """« + 3x - 2 » ou « - x + 4 » : le polynôme P à la suite d'une expression, jamais « + - »."""
    s = ptex(P, "x")
    return " - " + s[1:].lstrip() if s.startswith("-") else " + " + s


def _fraction_signee(R, D):
    """« + \\dfrac{8}{x - 3} » ou « - \\dfrac{x - 4}{x^2 + 1} » : le signe de R sort de la fraction."""
    if R[-1] < 0:
        return rf" - \dfrac{{{ptex(pscal(R, F(-1)), 'x')}}}{{{ptex(D, 'x')}}}"
    return rf" + \dfrac{{{ptex(R, 'x')}}}{{{ptex(D, 'x')}}}"


def _signe_en_infini(P, s):
    """Signe de P(x) près de s∞ (terme de plus haut degré)."""
    return _signe(P[deg(P)]) * (s if deg(P) % 2 else 1)


def _mot_signe(sg):
    return "positif" if sg > 0 else "négatif"


def _egalites(gauche, droites):
    """Formule affichée : A = B = C, une égalité par ligne (le signe = aligné)."""
    return (r"\[\begin{aligned}" + gauche + " &= " + droites[0] + "".join(r" \\ &= " + l for l in droites[1:])
            + r"\end{aligned}\]")


def _facteur_poly(P):
    """Polynôme écrit comme facteur d'un produit : entre parenthèses seulement s'il a plusieurs termes."""
    s = ptex(P, "x")
    return rf"\left({s}\right)" if len(_polynome_a_termes(P)) > 1 else s


def _borne_signe(R, D, s):
    """Borne au-delà de laquelle R/D garde son signe près de s∞ (plus grande racine réelle de R et D en +∞, plus petite en −∞) :
    (tex de la borne, None) ; (None, None) si R et D n'ont aucune racine réelle ; ("", None) si la borne n'a pas d'écriture exacte."""
    sp = charger_sympy()
    x = SYMPY["x"]
    racines = []
    for P in (R, D):
        if deg(P) >= 1:
            racines += list(sp.real_roots(sp.Poly(sum(_rat(c) * x ** i for i, c in enumerate(P)), x)))
    if not racines:
        return None, None
    r = max(racines, key=lambda r: float(sp.N(r))) if s > 0 else min(racines, key=lambda r: float(sp.N(r)))
    n = num_sympy(r)
    return ("" if n.approx else n.tex), None


def _oblique_rationnelle(items, N, D, Q, R, s, vues):
    """deg N = deg D + 1 : division euclidienne N = D·Q + R (sans « + 0 » ni « + - »), f(x) − (ax + b) = R/D → 0,
    puis position relative de la courbe et de la droite. La division n'est écrite qu'une fois (−∞ puis +∞)."""
    vers = r"+\infty" if s > 0 else r"-\infty"
    ntex, dtex, qtex_, rtex = ptex(N, "x"), ptex(D, "x"), ptex(Q, "x"), ptex(R, "x")
    produit = rf"{_facteur_poly(D)}\,{_facteur_poly(Q)}"
    cle = (tuple(N), tuple(D))
    deja = cle in vues
    vues[cle] = True
    if nul(R):
        if deja:
            items.append(txt(rf"Même division : \(f(x) = {qtex_}\) là où f est définie."))
        else:
            items.append(txt(rf"Division euclidienne : \({ntex} = {produit}\), donc \(f(x) = {qtex_}\) là où f est définie."))
        items.append(txt(rf"Asymptote oblique : \(y = {qtex_}\) (la courbe est contenue dans cette droite)."))
        return
    reste = rf"\dfrac{{{rtex}}}{{{dtex}}}"
    sg = _signe_en_infini(R, s) * _signe_en_infini(D, s)
    borne, _ = _borne_signe(R, D, s)
    pour = rf" pour \(x {'>' if s > 0 else '<'} {borne}\)" if borne else ""
    position = rf"\({reste} {'>' if sg > 0 else '<'} 0\){pour} : la courbe est " + ("au-dessus" if sg > 0 else "au-dessous")
    if deja:
        items.append(txt(rf"Même division : \(f(x) - {_facteur_poly(Q)} = {reste}\) tend vers \(0\) : asymptote oblique \(y = {qtex_}\) ; "
                         + position + " de l'asymptote."))
        return
    items.append(txt(rf"Division euclidienne : \({ntex} = {produit}{_suite_signee(R)}\), "
                     rf"donc \(f(x) = {qtex_}{_fraction_signee(R, D)}\)."))
    pt = Pt({"type": "inf", "signe": s})
    ch = Chaine(pt, rf"f(x) - {_facteur_poly(Q)}", Op("+", X(), X()))
    ch.lim(reste)
    conclusion = rf"0 \text{{ : asymptote oblique }} y = {qtex_}"
    if deg(R) >= 1:
        ch.val(conclusion, r"\text{le degré du numérateur est inférieur à celui du dénominateur}")
    else:
        ch.val(_guil(rf"\dfrac{{{rtex}}}{{{_limite_polynome_infini(D, s).tex()}}}"))
        ch.val(conclusion)
    ch.complete = True
    items.append(txt(ch.html()))
    items.append(txt(position + " de l'asymptote."))


def _etude_rationnelle_infini(f, N, D, signe, items, vues=None):
    n, m = deg(N), deg(D)
    an, bm = N[-1], D[-1]
    ratio = an / bm
    k = n - m
    k_signe_xk = signe if k % 2 else 1
    if n < m:
        ref, vtex = charger_sympy().Integer(0), "0"
        res = {"genre": "horizontale", "valeur_tex": "0", "valeur_val": 0.0}
    elif n == m:
        ref, vtex = charger_sympy().Rational(ratio.numerator, ratio.denominator), qtex(ratio)
        res = {"genre": "horizontale", "valeur_tex": vtex, "valeur_val": float(ratio)}
    else:
        signe_final = 1 if (ratio > 0) == (k_signe_xk > 0) else -1
        val_tex = r"+\infty" if signe_final > 0 else r"-\infty"
        ref, vtex = (charger_sympy().oo if signe_final > 0 else -charger_sympy().oo), val_tex
        res = None
    pt = Pt({"type": "inf", "signe": signe})
    # f est d'abord rédigée telle qu'elle est écrite ; si sa forme ne s'y prête pas (somme de fractions…),
    # on la ramène à une seule fraction N/D
    _narrer_limite(f, pt, ref, vtex, items,
                   alternative=(_arbre_fraction(N, D), r"On écrit \(f\) sous la forme d'une seule fraction : "
                                rf"\(f(x) = {tex(_arbre_fraction(N, D))}\)."))
    if n <= m:
        items.append(txt(rf"Asymptote horizontale : \(y = {vtex}\)."))
        return res
    if k == 1:
        Q, R = _pdiv(N, D)
        if deg(D) == 0:
            items.append(txt(rf"Asymptote oblique : \(y = {ptex(Q,'x')}\) (la courbe est cette droite)."))
        else:
            _oblique_rationnelle(items, N, D, Q, R, signe, {} if vues is None else vues)
        a = Q[1] if len(Q) > 1 else F(0)
        b = Q[0] if Q else F(0)
        return {"genre": "oblique", "a": qtex(a), "b": qtex(b), "a_val": float(a), "b_val": float(b),
                "equation_tex": ptex(Q, "x"), "valeur_tex": vtex}
    items.append(txt("Pas d'asymptote oblique : branche parabolique."))
    return {"genre": "aucune", "valeur_tex": vtex}


# =====================================================================
# Cas 2 : f rationnelle en x, pôle fini — toujours exact quand le pôle est
# rationnel (la quasi-totalité des cas de ce niveau) ; calcul formel en repli
# pour un pôle irrationnel.
# =====================================================================
def _facteur_racine(P, a):
    """P(x) = (x-a)^mult · P2(x), avec P2(a) ≠ 0 (a : Fraction exacte)."""
    mult = 0
    reste = pn(P)
    borne = deg(reste) + 1
    while mult < borne:
        Q, R = pdivlin(reste, a)
        if R == 0:
            reste = Q
            mult += 1
        else:
            break
    return reste, mult


def _etude_pole_numerique(f, N, D, point, cote, items):
    """Repli (pôle irrationnel, rare à ce niveau) : sonde numérique + calcul formel."""
    a = point.val
    Na = peval(N, a)
    if abs(Na) > 1e-9:
        def _signe_tex(x):
            return r"+\infty" if peval(N, x) / peval(D, x) > 0 else r"-\infty"
        res = {"genre": "verticale", "point_tex": point.tex, "point_val": a}
        for cle, dx in (("gauche", -1e-6), ("droite", 1e-6)):
            if cote in (cle, "deux"):
                res[cle + "_tex"] = _signe_tex(a + dx)
        sp = charger_sympy()
        borne = {"type": "fini", "point": point, "cote": cote}

        def ref_de(pt):
            v = res["gauche_tex" if pt.d < 0 else "droite_tex"]
            return (sp.oo if v == r"+\infty" else -sp.oo), v, None

        _narrer_cotes(f, borne, items, ref_de, cotes=tuple(c for c in ("gauche", "droite") if c + "_tex" in res))
        items.append(txt(rf"Asymptote verticale : \(x = {point.tex}\)."))
        return res
    val = _limite_sympy(f, _sympify_point(point))
    vtex, _, _, vval = _valeur_tex(val)
    if vtex == "?":
        items.append(txt("La limite n'a pas pu être déterminée automatiquement : on ne conclut pas sur une éventuelle asymptote."))
        return None
    item = txt(PHRASE_REPLI + rf"\(\displaystyle\lim_{{x\to {point.tex}}} f(x) = {vtex}\).")
    item["detail"] = "factorisation par un facteur irrationnel non rédigée"
    items.append(item)
    items.append(txt(_phrase_trou(point.tex, vtex)))
    return {"genre": "trou", "point_tex": point.tex, "point_val": a, "valeur_tex": vtex, "valeur_val": vval}


NON_DETERMINEE_TEX = r"\text{limite non déterminée automatiquement}"


def _affichable(v):
    """« ? » est le marqueur interne d'une limite que SymPy n'a pas donnée."""
    return NON_DETERMINEE_TEX if v == "?" else v


def _phrase_trou(point_tex, valeur_tex):
    """Valeur interdite où la limite (éventuellement latérale) est finie."""
    return (rf"Limite finie : pas d'asymptote verticale, trou dans le graphique "
            rf"en \(({point_tex}\,;\,{valeur_tex})\).")


def _x_moins(a):
    """tex de (x - a), correctement signé : a peut être négatif."""
    if a == 0:
        return "x"
    return f"x - {qtex(a)}" if a > 0 else f"x + {qtex(-a)}"


def _facteur_tex(base_tex, k):
    """tex de (base)^k — toujours entre parenthèses (sert de facteur dans un produit
    ou de base d'une puissance, jamais ambigu)."""
    t = r"\left(" + base_tex + r"\right)"
    return t if k == 1 else t + "^{" + str(k) + "}"


def _produit_tex(*parts):
    parts = [p for p in parts if p and p != "1"]
    return r"\,".join(parts) if parts else "1"


def _sans_parentheses(t):
    """Retire \\left( … \\right) quand ils entourent à eux seuls toute l'expression."""
    d, g = r"\left(", r"\right)"
    if not (t.startswith(d) and t.endswith(g)):
        return t
    prof, i = 0, 0
    while i < len(t):
        if t.startswith(d, i):
            prof, i = prof + 1, i + len(d)
        elif t.startswith(g, i):
            prof, i = prof - 1, i + len(g)
            if prof == 0 and i < len(t):
                return t
        else:
            i += 1
    return t[len(d):-len(g)]


def _puissance_binome(a, k):
    """Coefficients de (x − a)^k."""
    P = [F(1)]
    for _ in range(k):
        P = pmul(P, [-F(a), F(1)])
    return P


def _etude_rationnelle_pole(f, N, D, point, cote, items):
    if point.q is None:
        return _etude_pole_numerique(f, N, D, point, cote, items)
    sp = charger_sympy()
    a = point.q
    xa = _x_moins(a)
    N2, multN = _facteur_racine(N, a)
    D2, multD = _facteur_racine(D, a)
    N2a, D2a = peval(N2, a), peval(D2, a)
    mult = min(multN, multD)
    diff = multN - multD
    borne = {"type": "fini", "point": point, "cote": cote}
    g = f
    chaine0 = None
    if mult > 0:
        # facteur(s) (x − a) communs au numérateur et au dénominateur : forme indéterminée 0/0
        fac_N2 = qtex(N2a) if deg(N2) == 0 else ptex(N2, "x")
        fac_D2 = qtex(D2a) if deg(D2) == 0 else ptex(D2, "x")
        fac_N2_prod = fac_N2 if deg(N2) == 0 else r"\left(" + fac_N2 + r"\right)"
        fac_D2_prod = fac_D2 if deg(D2) == 0 else r"\left(" + fac_D2 + r"\right)"
        commun = _facteur_tex(xa, mult)
        barre = r"\cancel{" + commun + "}"
        reste_haut = _produit_tex(_facteur_tex(xa, diff) if diff > 0 else "", fac_N2_prod)
        num_chaine = _produit_tex(reste_haut, barre)
        den_chaine = _produit_tex(barre, fac_D2_prod if diff >= 0 else _produit_tex(_facteur_tex(xa, -diff), fac_D2_prod))
        simplifie_haut = reste_haut if reste_haut else "1"
        simplifie_bas = fac_D2 if diff >= 0 else _produit_tex(_facteur_tex(xa, -diff), fac_D2)
        haut, bas = _sans_parentheses(simplifie_haut), _sans_parentheses(simplifie_bas)
        simplifie = haut if bas == "1" else r"\dfrac{" + haut + "}{" + bas + "}"
        g = _arbre_fraction(pmul(N2, _puissance_binome(a, max(diff, 0))),
                            pmul(D2, _puissance_binome(a, max(-diff, 0))))
        chaine0 = Chaine(Pt(borne), tex(f), f)
        chaine0.annoncer(_guil(r"\dfrac{0}{0}") + r"\text{ : forme indéterminée}")
        chaine0.lim(rf"\dfrac{{{num_chaine}}}{{{den_chaine}}}", rf"\text{{on factorise par }} \left({xa}\right)")
        chaine0.lim(simplifie, r"\text{on simplifie}", g)

    if diff >= 0:
        valeur = N2a / D2a if diff == 0 else F(0)
        vtex = qtex(valeur)
        Ng, Dg = pmul(N2, _puissance_binome(a, max(diff, 0))), pmul(D2, _puissance_binome(a, 0))
        pt0 = Pt(borne)
        sub = _tex_en(g, pt0)
        if peval(Ng, a) / peval(Dg, a) == valeur and chaine0 is not None:
            chaine0.val(sub)
            chaine0.val(vtex, force=sub == vtex)
            items.append(txt(chaine0.html()))
        else:
            items.append(_repli(pt0, vtex, "valeur simplifiée incohérente"))
        items.append(txt(_phrase_trou(point.tex, vtex)))
        return {"genre": "trou", "point_tex": point.tex, "point_val": float(a),
                "valeur_tex": vtex, "valeur_val": float(valeur)}

    # pôle : signe du facteur (x − a)^k de chaque côté, signe de N2(a)/D2(a)
    if chaine0 is not None:
        items.append(txt(chaine0.html()))
    k = -diff
    ratio = N2a / D2a
    res = {"genre": "verticale", "point_tex": point.tex, "point_val": float(a)}
    for sens, cle in ((-1, "gauche"), (1, "droite")):
        if cote not in (cle, "deux"):
            continue
        signe_facteur = 1 if (k % 2 == 0 or sens > 0) else -1
        signe_final = 1 if (ratio > 0) == (signe_facteur > 0) else -1
        res[cle + "_tex"] = r"+\infty" if signe_final > 0 else r"-\infty"

    def ref_de(pt):
        v = res["gauche_tex" if pt.d < 0 else "droite_tex"]
        return (sp.oo if v == r"+\infty" else -sp.oo), v, None

    _narrer_cotes(g, borne, items, ref_de, cotes=tuple(c for c in ("gauche", "droite") if c + "_tex" in res))
    items.append(txt(rf"Asymptote verticale : \(x = {point.tex}\)."))
    return res


# =====================================================================
# Rédaction détaillée : algèbre des limites sur l'arbre.
#
# La valeur de chaque limite reste celle du calcul de référence (SymPy pour une
# fonction non rationnelle). La rédaction recalcule chaque sous-expression avec les
# règles du cours (somme, produit, quotient, composée avec e^u, ln u, √u, u^n), nomme
# la forme indéterminée quand il y en a une, et recoupe chaque limite écrite avec
# SymPy. Au moindre doute (forme indéterminée non levée, signe inconnu, écart avec
# la référence, exception), elle abandonne TOUTES ses étapes : la page écrit alors la
# phrase de repli et le résultat de référence, jamais une étape fausse.
# =====================================================================
class Abandon(Exception):
    """La rédaction détaillée n'aboutit pas : on garde le résultat avec la phrase de repli."""


class FormeIndeterminee(Exception):
    """Forme indéterminée rencontrée en un nœud : son nom, le nœud, les limites et les lignes des deux opérandes."""

    def __init__(self, nom, noeud=None):
        super().__init__(nom)
        self.nom, self.noeud = nom, noeud
        self.A = self.B = None
        self.la, self.lb = [], []


PHRASE_REPLI = "Le calcul détaillé de cette limite n'est pas rédigé ici ; résultat : "


def _est_nul(v):
    return v == 0 or v.is_zero is True


def _signe(v):
    """Signe d'un nombre exact non nul (Fraction ou SymPy) ; Abandon si SymPy ne le connaît pas."""
    if isinstance(v, (int, F)):
        return 1 if v > 0 else -1
    if v.is_positive:
        return 1
    if v.is_negative:
        return -1
    raise Abandon(f"signe de {v} inconnu")


_LN_SYMPY = re.compile(r"\\ln\{\\left\(([^()]*?) \\right\)\}")


def _joli(t):
    r"""\ln{\left(5 \right)} (SymPy) s'écrit \ln 5."""
    return _LN_SYMPY.sub(r"\\ln \1", t)


class Lim:
    """Limite d'une expression en un point : infinie (inf = ±1) ou finie (val : nombre exact SymPy).
    ap = signe de (expression − limite) au voisinage du point (+1 : par valeurs supérieures, −1 :
    inférieures), 0 s'il est inconnu, None pour une constante exacte. montre : écrire ℓ⁺ / ℓ⁻ (x → a⁺)."""
    __slots__ = ("inf", "val", "ap", "montre")

    def __init__(self, inf=0, val=None, ap=0, montre=False):
        self.inf, self.val, self.ap, self.montre = inf, val, ap, montre

    @staticmethod
    def fin(val, ap=0, montre=False):
        return Lim(0, charger_sympy().sympify(val), ap, montre)

    @staticmethod
    def infini(s):
        return Lim(1 if s > 0 else -1)

    def nul(self):
        return self.inf == 0 and _est_nul(self.val)

    def tex(self, signe=True):
        if self.inf:
            return r"+\infty" if self.inf > 0 else r"-\infty"
        if self.nul():
            if not signe:
                return "0"
            return "0^{+}" if self.ap and self.ap > 0 else "0^{-}" if self.ap and self.ap < 0 else "0"
        n = num_sympy(self.val)
        if n.approx:
            raise Abandon("valeur sans écriture exacte")
        if self.montre and self.ap:
            return _joli(n.tex) + ("^{+}" if self.ap > 0 else "^{-}")
        return _joli(n.tex)


def _lim_depuis_sympy(r):
    sp = charger_sympy()
    if r == sp.oo:
        return Lim.infini(1)
    if r == -sp.oo:
        return Lim.infini(-1)
    if r.has(sp.oo, -sp.oo, sp.zoo, sp.nan) or r.is_finite is not True or r.is_real is False:
        raise Abandon(f"limite SymPy inexploitable : {r}")
    return Lim.fin(r)


def _meme_valeur(a, b):
    sp = charger_sympy()
    if a.inf or b.inf:
        return a.inf == b.inf
    return abs(sp.N(a.val - b.val, 30)) < sp.Float("1e-20")


class Pt:
    """Point d'étude : ±∞ ou valeur finie approchée par la droite (d = +1) ou par la gauche (d = −1)."""

    def __init__(self, borne, d=0):
        self.deux = borne.get("cote") == "deux"      # valeur interdite étudiée des deux côtés
        if borne["type"] == "inf":
            self.s, self.a, self.d, self.a_tex = borne["signe"], None, 0, None
        else:
            self.s, self.a, self.d = 0, _sympify_point(borne["point"]), d
            self.a_tex = borne["point"].tex

    def cible(self):
        sp = charger_sympy()
        return (sp.oo if self.s > 0 else -sp.oo) if self.s else self.a

    def direction(self):
        return None if (self.s or not self.d) else ("+" if self.d > 0 else "-")

    def tex(self):
        if self.s:
            return r"+\infty" if self.s > 0 else r"-\infty"
        if not self.d:
            return self.a_tex
        base = self.a_tex if self.a_tex.lstrip("-").isdigit() else "{" + self.a_tex + "}"
        return base + ("^{+}" if self.d > 0 else "^{-}")

    def lim_x(self):
        if self.s:
            return Lim.infini(self.s)
        return Lim.fin(self.a, ap=self.d, montre=True)


# --- règles d'opérations ------------------------------------------------------
def _ap_somme(A, B):
    if A.ap is None:
        return B.ap
    if B.ap is None:
        return A.ap
    return A.ap if (A.ap and A.ap == B.ap) else 0


def _ap_signe(c, ap):
    """Signe de c·ε quand ε est de signe ap (None : ε est exactement 0)."""
    if ap is None:
        return None
    return _signe(c) * ap if ap else 0


def _oppose(A):
    if A.inf:
        return Lim.infini(-A.inf)
    return Lim.fin(-A.val, -A.ap if A.ap else A.ap)


def _somme(A, B):
    if A.inf and B.inf:
        if A.inf != B.inf:
            raise FormeIndeterminee("∞ − ∞")
        return Lim.infini(A.inf)
    if A.inf or B.inf:
        return Lim.infini(A.inf or B.inf)
    return Lim.fin(A.val + B.val, _ap_somme(A, B))


def _produit(A, B):
    if A.inf and B.inf:
        return Lim.infini(A.inf * B.inf)
    if A.inf or B.inf:
        inf, autre = (A, B) if A.inf else (B, A)
        if autre.nul():
            raise FormeIndeterminee("0 · ∞")
        return Lim.infini(inf.inf * _signe(autre.val))
    v = A.val * B.val
    if A.ap is None and B.ap is None:
        ap = None
    elif A.ap is None or B.ap is None:
        c, u = (A, B) if A.ap is None else (B, A)
        ap = None if c.nul() else _ap_signe(c.val, u.ap)
    elif A.nul() and B.nul():
        ap = A.ap * B.ap
    elif A.nul():
        ap = _ap_signe(B.val, A.ap)
    elif B.nul():
        ap = _ap_signe(A.val, B.ap)
    else:
        t1, t2 = _ap_signe(A.val, B.ap), _ap_signe(B.val, A.ap)
        ap = t1 if (t1 and t1 == t2) else 0
    return Lim.fin(v, ap)


def _quotient(A, B):
    if A.inf and B.inf:
        raise FormeIndeterminee("∞/∞")
    if A.inf:
        if B.nul():
            if not B.ap:
                raise Abandon("signe du dénominateur inconnu")
            return Lim.infini(A.inf * B.ap)
        return Lim.infini(A.inf * _signe(B.val))
    if B.inf:
        return Lim.fin(0, 0 if A.nul() else _signe(A.val) * B.inf)
    if B.nul():
        if A.nul():
            raise FormeIndeterminee("0/0")
        if not B.ap:
            raise Abandon("signe du dénominateur inconnu")
        return Lim.infini(_signe(A.val) * B.ap)
    v = A.val / B.val
    if B.ap is None:
        ap = None if A.ap is None else _ap_signe(B.val, A.ap)
    elif A.ap is None:
        ap = None if A.nul() else (-_ap_signe(A.val, B.ap) if B.ap else 0)
    elif A.nul():
        ap = _ap_signe(B.val, A.ap)
    else:
        t1 = _ap_signe(B.val, A.ap)
        t2 = -_ap_signe(A.val, B.ap) if B.ap else 0
        ap = t1 if (t1 and t1 == t2) else 0
    return Lim.fin(v, ap)


def _puissance_entiere(U, n):
    pair = (n % 2 == 0)
    if U.inf:
        s = 1 if (U.inf > 0 or pair) else -1
        return Lim.infini(s) if n > 0 else Lim.fin(0, s)
    if U.nul():
        if n > 0:
            return Lim.fin(0, 1 if pair else U.ap)
        if pair:
            return Lim.infini(1)
        if not U.ap:
            raise Abandon("signe de la base inconnu")
        return Lim.infini(U.ap)
    ap = None if U.ap is None else (_signe(n * U.val ** (n - 1)) * U.ap if U.ap else 0)
    return Lim.fin(U.val ** n, ap)


def _puissance_reelle(U, alpha):
    """u^α, α rationnel non entier (ou 1/2) : seulement pour une base positive."""
    sp = charger_sympy()
    if U.inf:
        if U.inf < 0:
            raise Abandon("base négative")
        return Lim.infini(1) if alpha > 0 else Lim.fin(0, 1)
    if U.nul():
        if U.ap != 1:
            raise Abandon("base nulle de signe inconnu")
        return Lim.fin(0, 1) if alpha > 0 else Lim.infini(1)
    if _signe(U.val) < 0:
        raise Abandon("base négative")
    ap = None if U.ap is None else (U.ap * (1 if alpha > 0 else -1) if U.ap else 0)
    return Lim.fin(U.val ** sp.Rational(alpha.numerator, alpha.denominator), ap)


def _exp_lim(U):
    sp = charger_sympy()
    if U.inf:
        return Lim.infini(1) if U.inf > 0 else Lim.fin(0, 1)
    return Lim.fin(sp.exp(U.val), U.ap)


def _ln_lim(U):
    sp = charger_sympy()
    if U.inf:
        if U.inf < 0:
            raise Abandon("ln d'une quantité négative")
        return Lim.infini(1)
    if U.nul():
        if U.ap != 1:
            raise Abandon("ln de 0 de signe inconnu")
        return Lim.infini(-1)
    if _signe(U.val) < 0:
        raise Abandon("ln d'une quantité négative")
    return Lim.fin(sp.log(U.val), U.ap)


# --- tableaux de signes (même moteur que l'outil « Ensemble de définition ») -------------------------
class TableauSigne:
    """Tableau de signes du dénominateur ou de l'argument d'un ln, construit par le moteur de l'outil ED."""

    def __init__(self, genre, A, c, infos, items):
        self.genre, self.A, self.c, self.infos = genre, A, c, infos
        self.crit = []
        for (h, k), (D, P, Z) in infos:
            for S in (D, P, Z):
                for iv in S:
                    for pt in (iv.lo, iv.hi):
                        if pt is not None and not any(proche(pt.val, q.val) for q in self.crit):
                            self.crit.append(pt)
        self.crit.sort(key=lambda q: q.val)
        T = tex(A)
        titre = rf"Signe de \({T}\) :"
        tab, hach = None, []
        for i in items:
            if i.get("type") == "tableau":
                lignes = [dict(r, label=r["label"].replace(r" \ (\text{dén.})", "")) for r in i["rows"]]
                if len(lignes) == 2 and lignes[0]["cells"] == lignes[1]["cells"]:
                    lignes = [dict(lignes[1], label=lignes[0]["label"])]    # un seul facteur : une seule ligne
                tab = dict(i, rows=lignes)
            elif str(i.get("html", "")).startswith("Les zones hachurées"):
                hach.append(i)
        self.items = [] if tab is None else [txt(titre), tab] + hach

    def renvoi(self):
        """« cf. tableau de signes »."""
        return "cf. tableau de signes"

    def signe_en(self, v):
        s = 1 if self.c > 0 else -1
        for (h, k), (D, P, Z) in self.infos:
            if not contient(D, v) or contient(Z, v):
                return None
            sf = 1 if contient(P, v) else -1
            s *= 1 if (sf < 0 and k % 2 == 0) else sf
        return s

    def lire(self, pt):
        """Signe de l'expression juste à gauche / à droite du point d'étude (pt.d = ∓1), ou None."""
        if pt.s or not pt.d:
            return None
        try:
            a = float(pt.a)
        except Exception:
            return None
        if not any(proche(q.val, a) for q in self.crit):
            return None
        autres = [q.val for q in self.crit if not proche(q.val, a) and (q.val - a) * pt.d > 0]
        v = (a + (min(autres) if pt.d > 0 else max(autres))) / 2 if autres else a + pt.d
        return self.signe_en(v)


def _construire_tableau(genre, A):
    """Tableau de signes de A (genre « den » : dénominateur, les zéros sont des valeurs interdites ; genre
    « ln » : argument d'un logarithme). None si le moteur de signe ne peut pas le construire."""
    if sans_x(A):
        return None
    c, facs = aplatir(A)
    sp = charger_sympy()
    if len(facs) == 1 and facs[0][1] == 1 and sp is not None:
        try:
            A2 = arbre_depuis_sympy(sp.factor(en_sympy(A)))
            c2, facs2 = aplatir(A2)
            if len(facs2) > 1 or any(abs(k) > 1 for _, k in facs2):
                c, facs = c2, facs2
        except Exception:
            pass
    if not facs:
        return None
    infos = []
    for h, k in facs:
        D, P, Z, _, mode = signe_facteur(h, "x")
        infos.append(((h, -k if genre == "den" else k), (D, P, Z)))
    items = []
    tableau_facteurs(c, infos, ">", tex(A), items)
    return TableauSigne(genre, A, c, infos, items)


class _RegistreTableaux:
    """Les tableaux de signes construits pendant une étude, et ceux que la rédaction a réellement utilisés."""

    def __init__(self):
        self.reset()

    def reset(self):
        self.tables, self.utilises = {}, []

    def chercher(self, genre, A):
        cle = (genre, A.key())
        if cle not in self.tables:
            try:
                self.tables[cle] = _construire_tableau(genre, A)
            except Exception:
                self.tables[cle] = None
        return self.tables[cle]

    def utiliser(self, genre, A):
        cle = (genre, A.key())
        if cle not in self.utilises:
            self.utilises.append(cle)

    def items(self):
        return [i for cle in self.utilises for i in self.tables[cle].items]


TABLEAUX = _RegistreTableaux()


class _Contexte:
    """État d'une rédaction : point d'étude, limites de référence (SymPy) déjà vues, signes déjà justifiés."""

    def __init__(self, pt, f, ref_f, prefixe=None):
        self.pt, self.f, self.prefixe = pt, f, prefixe
        self.refs, self.ap_vus, self.justifies = {}, set(), set()
        self.demandes = []
        self.lims = {}                 # limite de chaque morceau déjà étudié
        self.cf = []                   # justifications de signe (« x − 3 < 0 : cf. tableau de signes »)
        self.remarques = []            # « le terme dominant de … est … »
        self.sz = True                 # écrire 0⁺ / 0⁻ dans les niveaux de substitution
        self.liste = False             # un morceau a montré ses termes (« +∞ + ∞ »)
        self.sans_liste = False        # ne pas montrer les termes d'un morceau : sa limite seulement
        self.profondeur = 0
        self.nb_lhopital = 0
        if ref_f is not None:
            self.refs[f.key()] = ref_f

    def ref(self, n):
        """Limite de n selon SymPy (et signe de l'approche de 0), pour recouper la rédaction."""
        cle = n.key()
        L = self.refs.get(cle)
        if L is None:
            r = _limite_sympy(n, self.pt.cible(), self.pt.direction())
            if r is None:
                raise Abandon("SymPy ne conclut pas pour une sous-expression")
            L = self.refs[cle] = _lim_depuis_sympy(r)
        if L.nul() and cle not in self.ap_vus:
            self.ap_vus.add(cle)
            inv = _limite_sympy(Op("/", Nb(1), n), self.pt.cible(), self.pt.direction())
            sp = charger_sympy()
            L.ap = 1 if inv == sp.oo else -1 if inv == -sp.oo else 0
        return L

    def verifier(self, n, L, exact=False):
        """La limite écrite pour n doit être celle de SymPy (signe d'approche de 0 compris), sauf si elle
        vient d'un calcul exact (substitution dans un polynôme, factorisation par x − a)."""
        if exact:
            return
        R = self.ref(n)
        if not _meme_valeur(L, R):
            raise Abandon(f"limite écrite {L.tex()} ≠ référence {R.tex()} pour {tex(n)}")
        if L.nul() and L.ap and L.ap != R.ap:
            raise Abandon(f"signe d'approche de 0 non confirmé pour {tex(n)}")

    def lecture(self, genre, n, L):
        """Signe de n (qui tend vers 0 avec un signe d'approche) lu dans le tableau de signes : +1 / −1,
        ou None s'il n'y a pas de tableau (on garde alors la justification en texte)."""
        t = TABLEAUX.chercher(genre, n)
        s = t.lire(self.pt) if t is not None else None
        if s is None:
            return None
        if s != L.ap:
            raise Abandon("le tableau de signes contredit le signe calculé")
        self.demandes.append((genre, n))
        return s

    def chaine(self, n):
        """Chaîne d'égalités pour la limite de n (la tête est n lui-même)."""
        ch = Chaine(self.pt, tex(n), n, self.prefixe if n is self.f else None)
        ch.est_f = n is self.f
        ch.noeud = n
        return ch

    def lim_de(self, n):
        """Limite d'un morceau déjà étudié (ou étudié maintenant)."""
        L = self.lims.get(n.key())
        if L is None:
            L = _noeud(n, self)[0]
        return L

    def remarque(self, t):
        if t not in self.remarques:
            self.remarques.append(t)

    def noter(self, expr, s, tableau):
        """Justification de signe de la dernière ligne de la chaîne : « x − 3 < 0 : cf. tableau de signes »."""
        t = rf"{tex(expr)} {'>' if s > 0 else '<'} 0" + (r" \text{ : cf. tableau de signes}" if tableau else "")
        if t not in self.cf:
            self.cf.append(t)

    def signe_de(self, expr, U, genre):
        """Signe de expr (qui tend vers 0 avec un signe d'approche) : lu dans le tableau de signes, sinon justifié par une
        ligne de texte. Renvoie les lignes de texte éventuelles."""
        lu = self.lecture(genre, expr, U)
        if lu is not None:
            self.noter(expr, lu, True)
            return []
        lignes = self.justifier(expr, U, force=True)
        self.noter(expr, U.ap, False)
        return lignes

    def justifier(self, n, L, force=False):
        """Lignes qui justifient le signe de n, qui tend vers 0 (force : même pour la variable x seule).
        Abandon si le signe ne peut pas être justifié avec les outils du cours."""
        cle = n.key()
        if cle in self.justifies:
            return []
        if isinstance(n, Fn) and n.nom == "exp":
            return []                                    # e^u > 0 : connu
        if isinstance(n, X) and not force:
            return []
        pt = self.pt
        if pt.s:
            ligne = self._signe_infini(n, L)
        else:
            P = _polynome_de(n)
            ligne = self._signe_polynome(n, P, L) if P is not None else self._signe_monotone(n, L)
        if ligne is None:
            raise Abandon(f"signe de {tex(n)} non justifiable")
        self.justifies.add(cle)
        return [ligne]

    def _enonce_signes(self, sl, sr, a_tex):
        """« négatif pour x < a, positif pour x > a » (ou le seul côté étudié)."""
        pt = self.pt
        mot = lambda s: "positif" if s > 0 else "négatif"
        gauche = rf"{mot(sl)} pour \(x < {a_tex}\)"
        droite = rf"{mot(sr)} pour \(x > {a_tex}\)"
        if pt.deux:
            return f"{gauche}, {droite}"
        return gauche if pt.d < 0 else droite

    def _controle_signe(self, sl, sr, L):
        if (sl if self.pt.d < 0 else sr) != L.ap and self.pt.d:
            raise Abandon("signe justifié ≠ signe d'approche calculé")

    def _signe_polynome(self, n, P, L):
        pt = self.pt
        T = tex(n)
        mot = lambda s: "positif" if s > 0 else "négatif"
        if pt.a.is_Rational:
            a = F(int(pt.a.p), int(pt.a.q))
            Q, m = _facteur_racine(P, a)
            c = peval(Q, a)
            sr = _signe(c)
            sl = sr * (-1) ** m
            self._controle_signe(sl, sr, L)
            xa, a_tex = _binome(a), qtex(a)
            enonce = self._enonce_signes(sl, sr, a_tex)
            if a == 0:
                facteur_a = "x" if m == 1 else f"x^{{{m}}}"
            else:
                facteur_a = rf"\left({xa}\right)" if m == 1 else rf"\left({xa}\right)^{{{m}}}"
            if deg(Q) == 0:
                q_tex = qtex(c)
                if m == 1:
                    fact = xa if c == 1 else (rf"-\left({xa}\right)" if c == -1 else rf"{q_tex}\left({xa}\right)")
                else:
                    fact = facteur_a if c == 1 else rf"{q_tex}\,{facteur_a}"
                eg = "" if fact == T else rf" = {fact}"
                if m % 2 == 0:
                    parce = ("car une puissance paire est positive" if c == 1 else
                             rf"car \({q_tex}\) est {mot(sr)} et \({facteur_a}\) est positif")
                    return rf"Signe de \({T}{eg}\) : {mot(sr)} pour \(x \neq {a_tex}\), {parce}."
                return rf"Signe de \({T}{eg}\) : {enonce}."
            q_tex = ptex(Q, "x")
            q_par = r"\left(" + q_tex + r"\right)" if (" + " in q_tex or " - " in q_tex) else q_tex
            if a == 0:
                fact = (xa if m == 1 else f"x^{{{m}}}") + r"\," + q_par
            else:
                fact = q_par + r"\," + facteur_a
            proche = "" if q_tex == "x" else rf" (proche de \({qtex(c)}\))"
            if m % 2 == 0:
                fin = (rf"donc \({T}\) est {mot(sr)} de part et d'autre de \({a_tex}\)" if pt.deux
                       else rf"donc \({T}\) est {mot(sr)}")
                return (rf"Signe de \({T} = {fact}\) : \({facteur_a}\) est positif et près de \({a_tex}\), "
                        rf"\({q_tex}\) est {mot(sr)}{proche}, {fin}.")
            return (rf"Signe de \({T} = {fact}\) : près de \({a_tex}\), \({q_tex}\) est {mot(sr)}{proche}, "
                    rf"donc \({T}\) est {enonce}.")
        # point irrationnel : trinôme à deux racines réelles
        sp = charger_sympy()
        if deg(P) != 2:
            return None
        x = SYMPY["x"]
        expr = sum(sp.Rational(c.numerator, c.denominator) * x ** k for k, c in enumerate(P))
        racines = sorted(sp.solve(expr, x), key=lambda r: float(sp.N(r)))
        if len(racines) != 2 or not all(r.is_real for r in racines):
            return None
        r1, r2 = racines
        alpha = _signe(P[2])
        if abs(sp.N(pt.a - r1, 30)) < sp.Float("1e-25"):
            sl, sr, a_est_r1 = alpha, -alpha, True
        elif abs(sp.N(pt.a - r2, 30)) < sp.Float("1e-25"):
            sl, sr, a_est_r1 = -alpha, alpha, False
        else:
            return None
        self._controle_signe(sl, sr, L)
        t1, t2 = num_sympy(r1).tex, num_sympy(r2).tex
        gauche = rf"{mot(sl)} pour \(x < {t1}\)" if a_est_r1 else rf"{mot(sl)} entre \({t1}\) et \({t2}\)"
        droite = rf"{mot(sr)} entre \({t1}\) et \({t2}\)" if a_est_r1 else rf"{mot(sr)} pour \(x > {t2}\)"
        enonce = f"{gauche}, {droite}" if pt.deux else (gauche if pt.d < 0 else droite)
        return rf"Signe de \({T}\) (trinôme, racines \({t1}\) et \({t2}\)) : {enonce}."

    def _signe_monotone(self, n, L):
        """n = F(x) − c, F(x) + c, c − F(x), c + F(x) ou F(x) seul, avec F monotone et la bonne valeur en a :
        le signe de n vient de la monotonie de F."""
        pt = self.pt
        sp = charger_sympy()
        facteur = 1
        if isinstance(n, Op) and n.op in "+-" and sans_x(n.a) != sans_x(n.b):
            c = _const_sympy(n.a if sans_x(n.a) else n.b)
            F_ = n.b if sans_x(n.a) else n.a
            cible = c if n.op == "-" else -c
            if sans_x(n.a) and n.op == "-":
                facteur = -1                                 # c − F(x)
        else:
            F_, cible = n, sp.Integer(0)
        mu = _monotonie(F_)
        if not mu:
            return None
        valeur = en_sympy_reel(F_).subs(SYMPY["x"], pt.a)
        if abs(sp.N(valeur - cible, 30)) > sp.Float("1e-25"):
            return None
        mu_n = mu * facteur
        sl, sr = -mu_n, mu_n
        self._controle_signe(sl, sr, L)
        croiss = "croissante" if mu > 0 else "décroissante"
        return (rf"Signe de \({tex(n)}\) : \({tex(F_)}\) est {croiss} et vaut \({num_sympy(valeur).tex}\) "
                rf"en \(x = {pt.a_tex}\), donc \({tex(n)}\) est {self._enonce_signes(sl, sr, pt.a_tex)}.")

    def _signe_infini(self, n, L):
        """c/u avec u → ±∞ : le signe est celui de c fois celui de u au voisinage de l'infini."""
        pt = self.pt
        if isinstance(n, Op) and n.op == "/" and sans_x(n.a):
            U = _noeud(n.b, self)[0]
            c = _const_sympy(n.a)
            if U.inf and c != 0:
                mot = "positif" if U.inf > 0 else "négatif"
                s = _signe(c) * U.inf
                if s != L.ap:
                    raise Abandon("signe justifié ≠ signe d'approche calculé")
                return (rf"Signe de \({tex(n)}\) : \({tex(n.b)}\) est {mot} au voisinage de \({pt.tex()}\), "
                        rf"donc \({tex(n)}\) est {'positif' if s > 0 else 'négatif'}.")
        return None


def _monotonie(F_):
    """+1 / −1 si F_ est croissante / décroissante au voisinage du point (règles du cours), None sinon."""
    if isinstance(F_, X):
        return 1
    if isinstance(F_, Neg):
        m = _monotonie(F_.a)
        return -m if m else None
    if isinstance(F_, Fn):
        return _monotonie(F_.a)              # e^u, ln u, √u : croissantes
    if isinstance(F_, Op) and F_.op in "+-":
        if sans_x(F_.b):
            return _monotonie(F_.a)
        if sans_x(F_.a):
            m = _monotonie(F_.b)
            return (m if F_.op == "+" else -m) if m else None
    if isinstance(F_, Op) and F_.op in "*/":
        if sans_x(F_.b):
            c, m = valeur_constante(F_.b), _monotonie(F_.a)
        elif sans_x(F_.a) and F_.op == "*":
            c, m = valeur_constante(F_.a), _monotonie(F_.b)
        else:
            return None
        return m * (1 if c > 0 else -1) if (m and c) else None
    return None


def _const_sympy(n):
    return en_sympy_reel(n)


def _defini_en(n, ctx):
    """Vrai si n a une valeur au point d'étude (point fini) : sa limite est alors sa valeur."""
    pt = ctx.pt
    if pt.s:
        return False
    try:
        v = evaluer(n, float(pt.a))
    except Exception:
        return False
    return v is not None


def _binome(a):
    """tex de x − a (a rationnel)."""
    if a == 0:
        return "x"
    return f"x - {qtex(a)}" if a > 0 else f"x + {qtex(-a)}"


def _substituer(n, rep):
    if isinstance(n, X):
        return rep
    if isinstance(n, (Nb, E)):
        return n
    if isinstance(n, Neg):
        return Neg(_substituer(n.a, rep))
    if isinstance(n, Fn):
        return Fn(n.nom, _substituer(n.a, rep))
    return Op(n.op, _substituer(n.a, rep), _substituer(n.b, rep))


def _tex_en(n, pt):
    r"""n écrit avec la valeur du point à la place de x : 3^{2} - 1, \ln(5^{2} - 4 \cdot 5)…"""
    if pt.a.is_Rational:
        a = F(int(pt.a.p), int(pt.a.q))
        rep = Nb(a) if a >= 0 else Neg(Nb(-a))
    else:
        rep = Nb(F(-1, 2) if pt.a.is_negative else F(1, 2), pt.a_tex)
    return tex(_substituer(n, rep))


def _polynome_de(n):
    """Coefficients rationnels (Fraction, du degré 0 au plus haut) si n est un polynôme en x de degré ≥ 1."""
    try:
        dec = decomposer(n)
        if dec[0] != "x":
            return None
        N, D = dec[1]
        if deg(D) != 0 or D[0] == 0:
            return None
        P = pn([t / D[0] for t in N])
    except Exception:
        return None
    return P if deg(P) >= 1 else None


def _arbre_poly(P):
    """Arbre d'un polynôme à coefficients rationnels (pour réécrire une fraction rationnelle N/D)."""
    P = pn(P)
    termes = []
    for k in range(len(P) - 1, -1, -1):
        c = P[k]
        if c == 0:
            continue
        puiss = X() if k == 1 else Op("^", X(), Nb(F(k)))
        if k == 0:
            t = Nb(abs(c))
        elif abs(c) == 1:
            t = puiss
        else:
            t = Op("*", Nb(abs(c)), puiss)
        termes.append((c < 0, t))
    if not termes:
        return Nb(F(0))
    arbre = Neg(termes[0][1]) if termes[0][0] else termes[0][1]
    for neg, t in termes[1:]:
        arbre = Op("-" if neg else "+", arbre, t)
    return arbre


def _arbre_fraction(N, D):
    if deg(D) == 0 and D[0] in (1, -1):
        return _arbre_poly(pscal(N, D[0]))
    return Op("/", _arbre_poly(N), _arbre_poly(D))


def _poly_ou_const(n):
    """Coefficients d'un polynôme en x ou d'une constante rationnelle non nulle ; None sinon."""
    if sans_x(n):
        v = valeur_constante(n)
        return [F(v)] if v else None
    return _polynome_de(n)


def _noeud_polynome(n, ctx):
    """Polynôme en un point rationnel : sa limite est sa valeur P(a) ; si P(a) = 0, le signe d'approche vient
    de la factorisation P = (x − a)^m Q(x). Aucune ligne : c'est le consommateur (quotient, ln…) qui écrit
    « vaut » ou le signe. Renvoie None si n n'est pas un tel polynôme."""
    pt = ctx.pt
    if pt.s or not pt.a.is_Rational:
        return None
    P = _polynome_de(n)
    if P is None:
        return None
    a = F(int(pt.a.p), int(pt.a.q))
    v = peval(P, a)
    if v != 0 or not pt.d:
        L = Lim.fin(v)
    else:
        Q, m = _facteur_racine(P, a)
        L = Lim.fin(0, _signe(peval(Q, a)) * (pt.d if m % 2 else 1))
    ctx.verifier(n, L, exact=True)
    return L, []


def _noeud_rationnel_infini(n, ctx):
    """Polynôme à plusieurs termes ou quotient de deux polynômes en ±∞ : règle de la somme, ou mise en
    évidence du terme de plus haut degré quand les termes se compensent (∞ − ∞, ∞/∞).
    Renvoie None si n n'est pas de cette forme."""
    s = ctx.pt.s
    if not s:
        return None
    P = _polynome_de(n)
    if P is not None:
        if len(_polynome_a_termes(P)) < 2:
            return None
        L, phrases = _polynome_infini(P, s, n, ctx)
    elif isinstance(n, Op) and n.op == "/":
        A, B = _poly_ou_const(n.a), _poly_ou_const(n.b)
        if A is None or B is None or deg(B) < 1:
            return None
        if deg(A) == 0:
            phrases, L = [], _fraction_const_infini(A, B, s)
        else:
            fi = FormeIndeterminee("∞/∞", n)
            fi.A, fi.B = _limite_polynome_infini(A, s), _limite_polynome_infini(B, s)
            L, phrases = _evidence_quotient(n, ctx, fi)
            fi.la = fi.lb = []
            phrases = phrases
    else:
        return None
    ctx.verifier(n, L, exact=True)
    return L, phrases


FI_TEX = {"∞ − ∞": r"\infty - \infty", "0 · ∞": r"0 \cdot \infty", "∞/∞": r"\infty/\infty", "0/0": "0/0"}


def _guil(t):
    """Substitution des limites, entre guillemets : « +∞/−∞ »."""
    return r"\text{« }" + t + r"\text{ »}"


class _Ecr:
    """Écriture d'un morceau : jeton (nombre, ±∞, 0⁺ …), somme (entre parenthèses dans un produit) ou autre."""
    __slots__ = ("t", "genre")

    def __init__(self, t, genre=None):
        self.t = t
        self.genre = genre or ("somme" if " " in t else "jeton")

    def neg(self):
        return self.t.startswith("-")


_HAUTEURS = {}


def _est_atome(n):
    """Constante ou polynôme en x : une seule pièce dont on écrit la limite."""
    return sans_x(n) or isinstance(n, X) or _polynome_de(n) is not None


def _hauteur(n):
    """Nombre de couches d'opérations au-dessus des pièces (constantes et polynômes) : 0 pour une pièce."""
    cle = n.key()
    h = _HAUTEURS.get(cle)
    if h is None:
        if _est_atome(n):
            h = 0
        elif isinstance(n, (Neg, Fn)):
            h = _hauteur(n.a) + 1
        elif isinstance(n, Op):
            h = max(_hauteur(n.a), _hauteur(n.b)) + 1
        else:
            h = 0
        _HAUTEURS[cle] = h
    return h


def _somme_de_limites(lims):
    """« +∞ + ∞ », « +∞ − ∞ » : limites des termes d'une somme, signes gardés."""
    t = lims[0].tex()
    for l in lims[1:]:
        t += (" + " if l.inf > 0 else " - ") + r"\infty"
    return t


def _atome(n, ctx, haut):
    """Écriture, au niveau 1, de la limite d'une constante ou d'un polynôme. En ±∞, une somme dont les termes vont dans le même
    sens (ou la limite étudiée elle-même, haut) montre ses termes : « +∞ + ∞ » ; des termes opposés dans un morceau :
    le terme dominant donne la limite (remarque entre parenthèses, en mots)."""
    pt = ctx.pt
    if sans_x(n):
        return tex(n)
    if isinstance(n, X):
        if pt.s:
            return pt.lim_x().tex()
        return Lim.fin(0, pt.d).tex(ctx.sz) if pt.a == 0 else Lim.fin(pt.a).tex()
    if not pt.s:
        return ctx.lim_de(n).tex(ctx.sz)
    P = _polynome_de(n)
    L = _limite_polynome_infini(P, pt.s)
    ks = [k for k in _polynome_a_termes(P) if k >= 1]
    if len(ks) < 2:
        return L.tex()
    lims = [Lim.infini(_signe(P[k]) * (pt.s if k % 2 else 1)) for k in ks]
    if len({l.inf for l in lims}) == 1 or haut:
        if ctx.sans_liste:
            return L.tex()
        ctx.liste = True
        return _somme_de_limites(lims)
    k = deg(P)
    ctx.remarque(rf"\text{{le terme dominant de }} {tex(n)} \text{{ est }} {tex(_tete_tex(P[k], k))}")
    return L.tex()


def _signe_terme(e):
    """(négatif ?, valeur absolue en tex) d'un terme écrit avec son signe."""
    if e.genre == "jeton" and e.t[:1] in "+-":
        return e.t[0] == "-", e.t[1:]
    return False, e.t


def _somme_ecr(a, b, op):
    neg, mag = _signe_terme(b)
    if b.genre == "somme" and op == "-":
        mag, neg = rf"\left({b.t}\right)", False
    return _Ecr(a.t + (" - " if neg != (op == "-") else " + ") + mag, "somme")


def _facteur(e, premier):
    return rf"\left({e.t}\right)" if (e.genre == "somme" or (not premier and e.neg())) else e.t


def _niveau(n, j, ctx):
    """Écriture de n au niveau j : les morceaux de hauteur < j sont remplacés par leur limite, les autres gardent leur forme."""
    h = _hauteur(n)
    if h <= j - 1:
        if (h == 0 and j == 1) or isinstance(n, X):
            return _Ecr(_atome(n, ctx, False))
        return _Ecr(ctx.lim_de(n).tex(ctx.sz))
    if isinstance(n, Neg):
        a = _niveau(n.a, j, ctx)
        return _Ecr("-" + (rf"\left({a.t}\right)" if a.genre == "somme" or a.neg() else a.t), "autre")
    if isinstance(n, Fn):
        a = _niveau(n.a, j, ctx)
        if n.nom == "ln":
            if a.genre == "jeton" and not a.neg() and r"\infty" not in a.t and "^{" not in a.t:
                return _Ecr(rf"\ln {a.t}", "autre")
            return _Ecr(rf"\ln\left({a.t}\right)", "autre")
        if n.nom == "sqrt":
            return _Ecr(rf"\sqrt{{{a.t}}}", "autre")
        return _Ecr(rf"e^{{{a.t}}}", "autre")
    if isinstance(n, Op):
        a, b = _niveau(n.a, j, ctx), _niveau(n.b, j, ctx)
        if n.op == "/":
            return _Ecr(rf"\dfrac{{{a.t}}}{{{b.t}}}", "autre")
        if n.op == "*":
            return _Ecr(_facteur(a, True) + r" \cdot " + _facteur(b, False), "autre")
        if n.op == "^":
            base = rf"\left({a.t}\right)" if (a.genre != "jeton" or a.neg() or r"\infty" in a.t or "^" in a.t) else a.t
            return _Ecr(rf"{base}^{{{tex(n.b)}}}", "autre")
        return _somme_ecr(a, b, n.op)
    raise Abandon(f"écriture de {tex(n)} impossible")


def _niveaux(n, ctx, signes_zero=True):
    """Écritures successives de n avec les limites substituées (le dernier niveau est la « forme » : limite de chaque
    opérande), sans répétition. signes_zero : écrire 0⁺ / 0⁻ (sinon 0, pour la forme 0/0)."""
    ctx.sz = signes_zero
    ctx.liste = False
    try:
        H = _hauteur(n)
        if H == 0:
            res = [_atome(n, ctx, True)] if (ctx.pt.s and not sans_x(n)) else []
        else:
            res = [_niveau(n, j, ctx).t for j in range(1, H + 1)]
            if H == 1 and ctx.liste and isinstance(n, Op):                  # la forme montre des sommes de termes : on écrit aussi leurs limites
                ctx.sans_liste = True
                res.append(_niveau(n, 1, ctx).t)
    finally:
        ctx.sz = True
        ctx.sans_liste = False
    out = []
    for t in res:
        if not out or out[-1] != t:
            out.append(t)
    return out


def _annoncer(ch, n, fi, ctx):
    """Tête de la chaîne : lim n = « substitution » = « forme » : forme indéterminée (guide de rédaction, R2)."""
    ctx.remarques = []
    niv = _niveaux(n, ctx, signes_zero=(fi.nom != "0/0"))
    if not niv:
        niv = [FI_TEX[fi.nom]]
    ch.cf_tete = list(getattr(fi, "cf_tete", []))
    ch.annoncer(" = ".join(_guil(t) for t in niv) + r"\text{ : forme indéterminée}", ctx.remarques + ch.cf_tete)
    ctx.remarques = []
    return ch


def _facteurs(n, out):
    """Facteurs d'un produit (les produits imbriqués sont aplatis)."""
    if isinstance(n, Op) and n.op == "*":
        _facteurs(n.a, out)
        _facteurs(n.b, out)
    else:
        out.append(n)


def _forme_conclusion(g, ctx):
    """Limite de chaque facteur de g, signes gardés : « +∞ · 1 » (un dénominateur de limite 1 n'est pas écrit)."""
    if isinstance(g, Op) and g.op in "*/":
        haut, bas = [], []
        _facteurs(g.a if g.op == "/" else g, haut)
        if g.op == "/":
            _facteurs(g.b, bas)
        haut = [_Ecr(ctx.lim_de(f).tex()) for f in haut]
        bas = [_Ecr(ctx.lim_de(f).tex()) for f in bas]
        t = r" \cdot ".join(_facteur(e, i == 0) for i, e in enumerate(haut))
        if bas and not (len(bas) == 1 and bas[0].t == "1"):
            t = rf"\dfrac{{{t}}}{{{r' \cdot '.join(_facteur(e, i == 0) for i, e in enumerate(bas))}}}"
        return t
    if isinstance(g, Neg):
        t = _forme_conclusion(g.a, ctx)
        return None if t is None else "-" + rf"\left({t}\right)"
    H = _hauteur(g)
    return _niveau(g, H, ctx).t if H >= 1 else None


def _chaine_directe(f, L, ctx):
    """Chaîne de f quand aucune méthode n'est nécessaire : lim f = « substitution » = « limites » = valeur (justifications)."""
    pt = ctx.pt
    ch = ctx.chaine(f)
    ctx.remarques = []
    niv = _niveaux(f, ctx)
    valeur = L.tex(False)
    if len(niv) == 1 and niv[0] == valeur:
        niv = []
    if not niv and not pt.s and _defini_en(f, ctx):
        sub = _tex_en(f, pt)
        if sub != valeur:
            ch.val(sub)
    for t in niv:
        ch.val(_guil(t))
    just = list(ctx.cf) + list(ctx.remarques)
    ch.val(valeur, r" \; ;\; ".join(just) if just else None, force=True)
    ch.complete = True
    ctx.remarques = []
    ctx.cf = []
    return ch


def _meme_fonction(n, g, ctx):
    """Garde-fou numérique : n et g (réécriture de n) prennent les mêmes valeurs près du point d'étude."""
    pt = ctx.pt
    if pt.s:
        xs = [pt.s * t for t in (7.0, 23.0, 61.0, 310.0)]
    else:
        a = float(pt.a)
        h = (0.013, 0.037, 0.11, 0.23)
        xs = [a + (pt.d or 1) * t for t in h] + ([a - t for t in h] if not pt.d else [])
    bons = 0
    for x in xs:
        try:
            u, v = evaluer(n, x), evaluer(g, x)
        except Exception:
            continue
        if u is None or v is None:
            continue
        if abs(u - v) > 1e-7 * (1 + abs(u) + abs(v)):
            raise Abandon(f"la réécriture n'est pas équivalente en x = {x}")
        bons += 1
    if bons < 2:
        raise Abandon("réécriture non vérifiable numériquement")


MAX_LHOPITAL = 3       # au plus trois applications de BH de suite (8.12e en demande trois)
MAX_PROFONDEUR = 8     # réécritures imbriquées ; réduit si une page devient lente (un repli vaut mieux qu'une attente)
METHODES = []          # méthodes du cours, dans l'ordre : chacune renvoie (Lim, lignes) ou None si elle ne s'applique pas


def _lever(n, ctx, fi, n0=None):
    """Lève une forme indéterminée par la première méthode du cours qui s'applique ; Abandon sinon. Les signes lus pour
    les opérandes de n vont sur la ligne d'annonce de sa chaîne, ceux lus ensuite sur sa dernière ligne."""
    if ctx.profondeur >= MAX_PROFONDEUR:
        raise Abandon("trop de réécritures successives")
    n0 = len(ctx.cf) if n0 is None else n0
    fi.cf_tete = ctx.cf[n0:]
    del ctx.cf[n0:]
    ctx.profondeur += 1
    try:
        for methode in METHODES:
            r = methode(n, ctx, fi)
            if r is None:
                del ctx.cf[n0:]
                continue
            L, lignes = r
            ctx.verifier(n, L)
            queue = ctx.cf[n0:]
            del ctx.cf[n0:]
            ch = next((l for l in lignes if isinstance(l, Chaine) and l.noeud is n), None)
            if ch is not None:
                ch.cf += queue
            else:
                ctx.cf.extend(queue)
            return L, fi.la + fi.lb + lignes
    finally:
        ctx.profondeur -= 1
    raise Abandon(f"forme indéterminée {fi.nom} non levée en {tex(n)}")


# --- chaîne d'égalités : lim f(x) = lim … = … = valeur (une seule formule, justifications entre parenthèses) ----
class Chaine:
    """Calcul d'une limite écrit comme au tableau (guide de rédaction, R3) :
        lim f = « substitution » = « forme » : forme indéterminée
              = lim A         (justification)
              = valeur.
    pas = [(genre, tex, justification, arbre)] ; genre « lim » (nouvelle ligne) ou « val » (même ligne, après « = »).
    prefixe : « a » ou « b » (a = lim …) ; annonce : suite de la tête de la chaîne ; cf : justifications de la dernière ligne
    (signe d'un dénominateur lu dans un tableau)."""

    def __init__(self, pt, debut, arbre=None, prefixe=None):
        self.pt = pt
        self.pas = [("lim", debut, None, arbre)]
        self.complete = False                      # la dernière égalité est la valeur de la limite
        self.prefixe = prefixe
        self.annonce = None
        self.est_f = False                         # c'est la chaîne de la limite étudiée (pas celle d'un morceau)
        self.noeud = None                          # le morceau dont la chaîne calcule la limite
        self.cf_tete = []                          # justifications de signe de la ligne d'annonce
        self.cf = []                               # justifications de signe de la dernière ligne

    def lim(self, tex_, just=None, arbre=None):
        if self.pas[-1][1] == tex_ and self.pas[-1][0] == "lim":
            if just:                               # même expression : la justification s'ajoute
                g, t_, j, a = self.pas[-1]
                self.pas[-1] = (g, t_, rf"{j}\; ;\; {just}" if j else just, a)
            return self
        self.pas.append(("lim", tex_, just, arbre))
        return self

    def val(self, tex_, just=None, force=False):
        if self.pas[-1][1] == tex_ and not force:
            if just:
                g, t_, j, a = self.pas[-1]
                self.pas[-1] = (g, t_, rf"{j}\; ;\; {just}" if j else just, a)
            return self
        self.pas.append(("val", tex_, just, None))
        return self

    def suite(self, autre):
        """Prolonge cette chaîne par une autre qui commence par la même expression (méthode appelée sur le reste)."""
        self.pas += autre.pas[1:]
        self.complete = autre.complete
        self.cf += autre.cf_tete + autre.cf
        return self

    def annoncer(self, tex_, remarques=None):
        """Tête de la chaîne : « substitution » = « forme » : forme indéterminée (+ remarques entre parenthèses)."""
        self.annonce = tex_
        if remarques:
            g, t_, j, a = self.pas[0]
            self.pas[0] = (g, t_, r" \; ;\; ".join(remarques), a)
        return self

    def html(self):
        lim = rf"\lim_{{x\to {self.pt.tex()}}}"

        def arg(tex_, arbre):
            somme = isinstance(arbre, Op) and arbre.op in "+-" or (isinstance(arbre, Neg) and isinstance(arbre.a, Op)
                                                                   and arbre.a.op in "+-")
            return rf"\left({tex_}\right)" if somme else tex_
        lignes = []                                 # [gauche, corps, [justifications], ligne d'annonce ?]
        for i, (genre, tex_, just, arbre) in enumerate(self.pas):
            js = [just] if just else []
            if i == 0:
                gauche = (rf"{self.prefixe} = " if self.prefixe else "") + f"{lim} {arg(tex_, arbre)}"
                lignes.append([gauche, self.annonce, js, bool(self.annonce)])
            elif genre == "lim":
                corps = f"{lim} {arg(tex_, arbre)}"
                if lignes[-1][1] is None:
                    lignes[-1][1] = corps
                    lignes[-1][2] += js
                else:
                    lignes.append(["", corps, js, False])
            elif lignes[-1][3]:                     # la ligne d'annonce est close : la valeur a sa propre ligne
                lignes.append(["", tex_, js, False])
            elif lignes[-1][1] is None:
                lignes[-1][1] = tex_
                lignes[-1][2] += js
            else:
                lignes[-1][1] += f" = {tex_}"
                lignes[-1][2] += js
        lignes[-1][2] += self.cf

        def ecrit(l):
            gauche, corps, js, _ = l
            return corps + ((r" \qquad \left(" + r" \; ;\; ".join(js) + r"\right)") if js else "")
        if len(lignes) == 1:
            g, c, js, _ = lignes[0]
            corps = f"{g} = {ecrit(lignes[0])}" if c is not None else g
        else:
            corps = r" \\ ".join((f"{l[0]} &= {ecrit(l)}" if l[0] else f"&= {ecrit(l)}") for l in lignes)
        return r"\[\begin{aligned}" + corps + r"\end{aligned}\]"


def _est_forme_indeterminee(g, ctx):
    """True si g est, à sa racine, une forme indéterminée (une méthode du cours la lève)."""
    if not (isinstance(g, Op) and g.op in "+-*/"):
        return False
    A, _ = _noeud(g.a, ctx)
    B, _ = _noeud(g.b, ctx)
    try:
        _combine(g.op, A, B)
    except FormeIndeterminee:
        return True
    except Exception:
        return False
    return False


def _prolonger(ch, g, L, narration, ctx):
    """Prolonge la chaîne ch (qui s'arrête à « lim g ») : par la chaîne qu'une méthode a écrite pour g quand g est lui-même
    une forme indéterminée (fusion), sinon par les dernières égalités (limite de chaque facteur, puis la valeur). Renvoie les
    lignes à écrire autour : (avant la chaîne, après la chaîne) ; avant : chaînes des morceaux de g levés à part."""
    if _est_forme_indeterminee(g, ctx):
        idx = next((i for i in range(len(narration) - 1, -1, -1) if isinstance(narration[i], Chaine)), None)
        if idx is not None:
            ch.suite(narration[idx])
            return [l for l in narration[:idx]], [l for l in narration[idx + 1:]]
    _conclure(ch, g, L, ctx)
    return [l for l in narration], []


def _tout_texte(lignes):
    """Les lignes d'une rédaction, la chaîne d'égalités (si présente) écrite en formule."""
    return [l.html() if isinstance(l, Chaine) else l for l in lignes]


def _combine(op, A, B):
    """Limite de A op B (règles d'opérations) ; FormeIndeterminee si l'on ne peut pas conclure."""
    return {"+": lambda: _somme(A, B), "-": lambda: _somme(A, _oppose(B)),
            "*": lambda: _produit(A, B), "/": lambda: _quotient(A, B)}[op]()


def _conclure(ch, g, L, ctx):
    """Dernières égalités de la chaîne ch pour la limite de g (de valeur L) : la limite de chaque facteur quand elle apprend
    quelque chose (±∞, 0⁺, 0⁻), puis la valeur. Renvoie [] (compatibilité : les chaînes des morceaux sont dans la narration)."""
    pt = ctx.pt
    valeur = L.tex(False)
    if pt.s:
        saved, ctx.remarques = ctx.remarques, []
        try:
            t = _forme_conclusion(g, ctx)
        finally:
            ctx.remarques = saved
        if t is not None and (r"\infty" in t or "0^{" in t) and t != valeur:
            ch.val(_guil(t))
    elif _defini_en(g, ctx):
        sub = _tex_en(g, pt)
        if sub != valeur:
            ch.val(sub)
    ch.val(valeur, force=ch.pas[-1][0] == "lim" and ch.pas[-1][1] == valeur)
    ch.complete = True
    return []


# --- méthode : mise en évidence sous une racine (en ±∞, quotient ou produit dont un membre contient une racine)
def _est_racine(n):
    """L'argument de n s'il s'agit d'une racine carrée (√u ou u^(1/2)), sinon None."""
    if isinstance(n, Fn) and n.nom == "sqrt":
        return n.a
    if isinstance(n, Op) and n.op == "^" and valeur_constante(n.b) == F(1, 2):
        return n.a
    return None


def _contient_racine(n):
    if _est_racine(n) is not None:
        return True
    if isinstance(n, (Neg, Fn)):
        return _contient_racine(n.a)
    if isinstance(n, Op):
        return _contient_racine(n.a) or _contient_racine(n.b)
    return False


def _rat(q):
    return charger_sympy().Rational(q.numerator, q.denominator)


def _dominant(n, s):
    """Terme dominant (c, k) de n en s∞ (n = c·x^k·(1 + …), c exact SymPy) ; None si n n'est pas de cette forme ou
    si les termes de plus haut degré d'une somme se compensent. √Q (Q de degré 2k, coefficient dominant q > 0) a
    pour terme dominant √q·|x|^k = √q·(s x)^k. Sert de garde-fou : la rédaction écrit sa propre mise en évidence."""
    sp = charger_sympy()
    if sans_x(n):
        v = valeur_constante(n)
        return (_rat(v), 0) if v else None
    P = _polynome_de(n)
    if P is not None:
        return _rat(P[-1]), deg(P)
    r = _est_racine(n)
    if r is not None:
        Q = _poly_ou_const(r)
        if Q is None or deg(Q) == 0 or deg(Q) % 2 or Q[-1] <= 0:
            return None
        k = deg(Q) // 2
        return sp.sqrt(_rat(Q[-1])) * (s ** k), k
    if isinstance(n, Neg):
        d = _dominant(n.a, s)
        return (-d[0], d[1]) if d else None
    if isinstance(n, Op):
        da, db = _dominant(n.a, s), _dominant(n.b, s)
        if da is None or db is None:
            return None
        if n.op == "*":
            return da[0] * db[0], da[1] + db[1]
        if n.op == "/":
            return da[0] / db[0], da[1] - db[1]
        if n.op in "+-":
            sg = 1 if n.op == "+" else -1
            if da[1] != db[1]:
                return da if da[1] > db[1] else (sg * db[0], db[1])
            c = da[0] + sg * db[0]
            return (c, da[1]) if c != 0 else None
    return None


def _feuilles(n, signe=1):
    """Termes d'une somme (ou d'une différence) : [(terme, signe)]."""
    if isinstance(n, Op) and n.op in "+-":
        return _feuilles(n.a, signe) + _feuilles(n.b, signe if n.op == "+" else -signe)
    if isinstance(n, Neg):
        return _feuilles(n.a, -signe)
    return [(n, signe)]


def _puissance_x(e):
    return X() if e == 1 else Op("^", X(), Nb(F(e)))


def _terme_laurent(c, e):
    """(négatif ?, arbre) de |c|·x^e pour un exposant entier e ; si e < 0 : |c|/x^|e| avec le coefficient en haut
    et en bas (3/(2x), jamais une fraction dans une fraction)."""
    a = abs(F(c))
    if e == 0:
        return c < 0, Nb(a)
    if e > 0:
        return c < 0, (_puissance_x(e) if a == 1 else Op("*", Nb(a), _puissance_x(e)))
    bas = _puissance_x(-e) if a.denominator == 1 else Op("*", Nb(F(a.denominator)), _puissance_x(-e))
    return c < 0, Op("/", Nb(F(a.numerator)), bas)


def _somme_termes(termes):
    """Somme de [(négatif ?, arbre)] écrite avec + et - (un premier terme négatif devient Neg)."""
    arbre = Neg(termes[0][1]) if termes[0][0] else termes[0][1]
    for neg, t in termes[1:]:
        arbre = Op("-" if neg else "+", arbre, t)
    return arbre


def _produit_arbres(facteurs):
    arbre = facteurs[0]
    for f in facteurs[1:]:
        arbre = Op("*", arbre, f)
    return arbre


def _est_un(t):
    return isinstance(t, Nb) and t.v == 1


def _abs_tex(m):
    return "|x|" if m == 1 else rf"|x|^{{{m}}}"


def _just_racine(s, m):
    """Justification de √(x^{2m}) = |x|^m = ±x^m selon le signe de x (en ±∞)."""
    xm = "x" if m == 1 else f"x^{{{m}}}"
    racine = r"\sqrt{x^{2}}" if m == 1 else rf"\sqrt{{x^{{{2 * m}}}}}"
    if s > 0:
        return rf"x > 0 \text{{ : }} {racine} = {_abs_tex(m)} = {xm}"
    return rf"x < 0 \text{{ : }} {racine} = {_abs_tex(m)} = {'-' if m % 2 else ''}{xm}"


def _racine_en_evidence(t, Q, s):
    """√Q (Q de degré 2m, coefficient dominant q > 0) en s∞ : √Q = √(x^{2m}(q + …)) = |x|^m√(q + …) = ±x^m√(q + …).
    Renvoie un dictionnaire : m ; stades t0, t1 (tex, sans signe) ; coef (±√q si q est un carré, sinon ±1) ; facteur
    (arbre de √(q + …), Nb(1) si le coefficient sort) ; eq (égalité de la mise en évidence, ou None)."""
    m = deg(Q) // 2
    interieur = _somme_termes([_terme_laurent(Q[j], j - 2 * m) for j in range(2 * m, -1, -1) if Q[j] != 0])
    absx = _abs_tex(m)
    seul = len(_polynome_a_termes(Q)) == 1
    q = Q[-1]
    racine_q = charger_sympy().sqrt(_rat(q))
    signe = -1 if (s < 0 and m % 2) else 1
    if seul and racine_q.is_Rational:                    # √(4x²) = 2|x| : le coefficient sort tel quel
        rq = F(int(racine_q.p), int(racine_q.q))
        t1 = ("" if rq == 1 else num_sympy(racine_q).tex) + absx
        return {"m": m, "t0": tex(t), "t1": t1, "coef": signe * rq, "facteur": Nb(F(1)), "eq": None}
    if seul:
        return {"m": m, "t0": tex(t), "t1": rf"\sqrt{{{qtex(q)}}}\,{absx}", "coef": F(signe),
                "facteur": Fn("sqrt", Nb(q)), "eq": None}
    t0 = rf"\sqrt{{{_monome_tex(F(1), 2 * m)}\left({tex(interieur)}\right)}}"
    eq = rf"{tex(_arbre_poly(Q))} = {_monome_tex(F(1), 2 * m)}\left({tex(interieur)}\right)"
    return {"m": m, "t0": t0, "t1": rf"{absx}\sqrt{{{tex(interieur)}}}", "coef": F(signe),
            "facteur": Fn("sqrt", interieur), "eq": eq}


def _tete_tex(coef, k):
    """Arbre de coef·x^k (coef Fraction signé)."""
    facteurs = [t for t in (Nb(abs(coef)) if abs(coef) != 1 else None, _puissance_x(k) if k else None) if t is not None]
    tete = _produit_arbres(facteurs or [Nb(F(1))])
    return Neg(tete) if coef < 0 else tete


def _somme_tex(termes):
    """[(négatif ?, tex)] → « a + b - c »."""
    out = ""
    for i, (neg, t) in enumerate(termes):
        out += ("-" if neg else "") + t if i == 0 else (" - " if neg else " + ") + t
    return out


def _membre_en_evidence(M, s):
    """Mise en évidence de x^k dans un membre M (somme de monômes et de racines de polynômes de degré pair) en s∞ :
    M = coef·x^k·R, où R vaut (constante non nulle) + (termes en 1/x^j). Renvoie un dictionnaire : coef, k, R (arbre),
    evid (arbre coef·x^k·R), stades (tex des écritures successives, de la racine mise en évidence à M = x^k·R),
    eqs (égalités de mise en évidence), absm (exposants m des |x|^m), somme (plusieurs termes) ; None si M n'est pas
    de cette forme ou si ses termes de plus haut degré se compensent."""
    if _dominant(M, s) is None:
        return None
    feuilles = _feuilles(M)
    termes = []                                           # [(genre, signe, feuille, polynôme)] dans l'ordre de M
    for t, sg in feuilles:
        r = _est_racine(t)
        if r is not None:
            Q = _poly_ou_const(r)
            if Q is None or deg(Q) == 0 or deg(Q) % 2 or Q[-1] <= 0:
                return None
            termes.append(("racine", sg, t, Q))
            continue
        P = _poly_ou_const(t)
        if P is None:
            if sans_x(t):
                continue                                  # constante nulle
            return None
        termes.append(("poly", sg, t, P))
    if not termes:
        return None
    if all(genre == "poly" for genre, _, _, _ in termes):            # polynôme : M = c·x^k(1 + …)
        P = [F(0)]
        for _, sg, _, Pi in termes:
            P = padd(P, pscal(Pi, F(sg)))
        k, c = deg(P), P[deg(P)]
        if len(_polynome_a_termes(P)) == 1:               # monôme c·x^k
            R = Nb(F(1))
            evid = _tete_tex(c, k)
            return {"coef": c, "lead": c, "k": k, "R": R, "evid": evid, "stades": [tex(evid)] * 4, "eqs": [],
                    "absm": [], "somme": False}
        t = [_terme_laurent(P[j], j - k) for j in range(k, -1, -1) if P[j] != 0]     # x^k(c + … ) : le coefficient reste dans la parenthèse
        R = _somme_termes(t)
        evid = Op("*", _puissance_x(k), R) if k else R
        return {"coef": F(1), "lead": c, "k": k, "R": R, "evid": evid, "stades": [tex(evid)] * 4,
                "eqs": [rf"{tex(M)} = {tex(evid)}"], "absm": [], "somme": False}
    k = max(deg(P) // 2 if genre == "racine" else deg(P) for genre, _, _, P in termes)
    if len(termes) == 1:                                  # un seul terme : une racine
        _, sg, t, Q = termes[0]
        rac = _racine_en_evidence(t, Q, s)
        coef = sg * rac["coef"]
        R = rac["facteur"]
        evid = _produit_arbres([_tete_tex(coef, rac["m"]), R]) if not _est_un(R) else _tete_tex(coef, rac["m"])
        neg = "-" if sg < 0 else ""
        return {"coef": coef, "k": rac["m"], "R": R, "evid": evid, "somme": False, "absm": [rac["m"]],
                "stades": [neg + rac["t0"], neg + rac["t1"], tex(evid), tex(evid)],
                "eqs": [rac["eq"]] if rac["eq"] else []}
    # somme dont une racine : chaque terme divisé par x^k
    s0, s1, s2, eqs, absm, t_arbres = [], [], [], [], [], []
    for genre, sg, t, P in termes:
        if genre == "racine":
            rac = _racine_en_evidence(t, P, s)
            m = rac["m"]
            absm.append(m)
            if rac["eq"]:
                eqs.append(rac["eq"])
            coef = sg * rac["coef"]
            reste = _produit_arbres([_tete_tex(abs(coef), m), rac["facteur"]]) if not _est_un(rac["facteur"]) else _tete_tex(abs(coef), m)
            s0.append((sg < 0, rac["t0"]))
            s1.append((sg < 0, rac["t1"]))
            s2.append((coef < 0, tex(reste)))
            if _est_un(rac["facteur"]):
                t_arbres.append(_terme_laurent(coef, m - k))
            else:
                r_ = rac["facteur"] if m == k else Op("/", rac["facteur"], _puissance_x(k - m))
                t_arbres.append((coef < 0, r_))
        else:
            ts = []
            for j in range(deg(P), -1, -1):
                if P[j] != 0:
                    neg_, a_ = _terme_laurent(sg * P[j], j)
                    ts.append((neg_, tex(a_)))
                    t_arbres.append(_terme_laurent(sg * P[j], j - k))
            for lst in (s0, s1, s2):
                lst.extend(ts)
    R = _somme_termes(t_arbres)
    evid = Op("*", _puissance_x(k), R) if k else R
    return {"coef": F(1), "k": k, "R": R, "evid": evid, "somme": True, "absm": absm,
            "stades": [_somme_tex(s0), _somme_tex(s1), _somme_tex(s2), tex(evid)],
            "eqs": eqs + [rf"{tex(M)} = {tex(evid)}"]}


def _forme(op, a, b):
    """Quotient ou produit de deux écritures (tex) de membres."""
    if op == "/":
        return rf"\dfrac{{{a}}}{{{b}}}"
    return rf"{a}\,{b}"


def _evidence_racine(n, ctx, fi):
    """En ±∞, quotient ou produit dont un membre contient une racine : chaîne d'égalités
    √(4x² + 1) = √(x²(4 + 1/x²)) = |x|√(4 + 1/x²) = ±x√(4 + 1/x²), simplification, puis limite de ce qui reste.
    Jamais quand les termes de plus haut degré d'une somme se compensent (alors : expression conjuguée)."""
    if not _contient_racine(n):
        return None
    return _evidence_quotient(n, ctx, fi)


def _evidence_quotient(n, ctx, fi):
    """Quotient ou produit de deux membres (polynômes, racines de polynômes) en ±∞ : on met x^k en évidence dans chaque
    membre, on simplifie, puis on calcule la limite de ce qui reste (chaîne d'égalités)."""
    s = ctx.pt.s
    if not s or not isinstance(n, Op) or n.op not in "*/":
        return None
    A, B = _membre_en_evidence(n.a, s), _membre_en_evidence(n.b, s)
    if A is None or B is None:
        return None
    coef = A["coef"] / B["coef"] if n.op == "/" else A["coef"] * B["coef"]
    d = A["k"] - B["k"] if n.op == "/" else A["k"] + B["k"]
    haut, bas = [], []
    if abs(coef.numerator) != 1:
        haut.append(Nb(F(abs(coef.numerator))))
    if coef.denominator != 1:
        bas.append(Nb(F(coef.denominator)))
    if d > 0:
        haut.append(_puissance_x(d))
    elif d < 0:
        bas.append(_puissance_x(-d))
    if not _est_un(A["R"]):
        haut.append(A["R"])
    if not _est_un(B["R"]):
        (bas if n.op == "/" else haut).append(B["R"])
    num = _produit_arbres(haut) if haut else Nb(F(1))
    g = Op("/", num, _produit_arbres(bas)) if bas else num
    if coef < 0:
        g = Neg(g)
    _meme_fonction(n, g, ctx)
    L, narration = _noeud(g, ctx)
    ch = ctx.chaine(n)
    stades = [_forme(n.op, A["stades"][i] if not (n.op == "*" and A["somme"]) else rf"\left({A['stades'][i]}\right)",
                     B["stades"][i] if not (n.op == "*" and B["somme"]) else rf"\left({B['stades'][i]}\right)")
              for i in range(4)]
    if stades[0].replace(r"\dfrac", r"\frac") != tex(n).replace(r"\dfrac", r"\frac"):
        ch.lim(stades[0], r"\text{mise en évidence}")
    ms = sorted(set(A["absm"] + B["absm"]))
    if ms:
        ch.lim(stades[2], r" ,\; ".join(_just_racine(s, m) for m in ms))
    elif stades[3] != stades[0]:
        ch.lim(stades[3], r"\text{mise en évidence}")
    ch.lim(tex(g), None, g)
    _conclure(ch, g, L, ctx)
    _annoncer(ch, n, fi, ctx)
    return L, list(narration) + [ch]


def _evidence_ln(n, ctx, fi):
    """ln(u)/v en ±∞ avec u et v polynômes : ln(u) = k ln|x| + ln(c + …), puis croissance comparée
    (ln x / x^p → 0) pour le terme en ln|x| ; avant Bernoulli-L'Hôpital. Seulement si u = x^k(c + …) avec x^k > 0."""
    s = ctx.pt.s
    if not s or not isinstance(n, Op) or n.op != "/" or not (isinstance(n.a, Fn) and n.a.nom == "ln"):
        return None
    u, v = _polynome_de(n.a.a), _polynome_de(n.b)
    if u is None or v is None or deg(v) < 1:
        return None
    k, c = deg(u), u[deg(u)]
    if c <= 0 or (s < 0 and k % 2):
        return None
    V = _membre_en_evidence(n.b, s)
    if V is None:
        return None
    p = V["k"]
    termes = [_terme_laurent(u[j], j - k) for j in range(k, -1, -1) if u[j] != 0]
    ru = _somme_termes(termes) if len(termes) > 1 else None
    xp = "x" if p == 1 else f"x^{{{p}}}"
    lnx = r"\ln x" if s > 0 else r"\ln|x|"
    absx = lnx if k == 1 else rf"{k}{lnx}"
    ln_c = rf"\ln {qtex(c)}"
    # numérateur : ln(x^k(c + …)) = k ln|x| + ln(c + …)
    if ru is not None:
        f0 = rf"\ln\left({_monome_tex(F(1), k)}\left({tex(ru)}\right)\right)"
        f1 = rf"{absx} + \ln\left({tex(ru)}\right)"
        B = rf"\dfrac{{\ln\left({tex(ru)}\right)}}{{{xp}}}"
    else:
        f0 = rf"\ln\left({tex(n.a.a)}\right)"
        f1 = absx if c == 1 else rf"{ln_c} + {absx}"
        B = rf"\dfrac{{{ln_c}}}{{{xp}}}" if c != 1 else None
    den_evid = V["stades"][3]
    ch = ctx.chaine(n)
    ch.lim(rf"\dfrac{{{f0}}}{{{den_evid}}}", r"\text{mise en évidence}")
    ch.lim(rf"\dfrac{{{f1}}}{{{den_evid}}}", r"\text{propriétés de } \ln")
    A_ = rf"\dfrac{{{lnx}}}{{{xp}}}"
    corps = (A_ if k == 1 else rf"{k}\,{A_}") + (f" + {B}" if B else "")
    sans_pref = V["coef"] == 1 and _est_un(V["R"])
    if sans_pref:
        f2 = corps
    else:
        den = _produit_arbres([t for t in (Nb(abs(V["coef"])) if abs(V["coef"]) != 1 else None,
                                            None if _est_un(V["R"]) else V["R"]) if t is not None])
        f2 = rf"{'-' if V['coef'] < 0 else ''}\dfrac{{1}}{{{tex(den)}}}\left({corps}\right)"
    ch.lim(f2)
    # croissance comparée pour ln|x|/x^p
    ref = REFERENCES["ln_sur_puissance"][0]
    if s > 0:
        j_cc = rf"\text{{croissance comparée : }} {ref}"
    else:
        tp = "t" if p == 1 else f"t^{{{p}}}"
        signe = "" if p % 2 == 0 else "-"
        j_cc = (rf"t = -x \to +\infty ,\; {A_} = {signe}\dfrac{{\ln t}}{{{tp}}} \text{{ : croissance comparée, }} "
                r"\lim_{t\to +\infty} \dfrac{\ln t}{t^{n}} = 0")
    nul = r"2 \cdot 0" if k == 2 else (r"0" if k == 1 else rf"{k} \cdot 0")
    valeur = nul + (" + 0" if B else "")
    if not sans_pref and abs(V["coef"]) != 1:
        valeur = rf"{'-' if V['coef'] < 0 else ''}\dfrac{{1}}{{{qtex(abs(V['coef']))}}}\left({valeur}\right)"
    elif V["coef"] < 0:
        valeur = rf"-\left({valeur}\right)"
    ap = _signe(V.get("lead", V["coef"])) * (s if p % 2 else 1)
    L = Lim.fin(0, ap)
    ch.val(valeur, j_cc)
    ch.val("0")
    ch.complete = True
    _annoncer(ch, n, fi, ctx)
    return L, [ch]


# --- méthode : √(u²) = |u| (en une valeur, d'un seul côté) ---------------------------------------
def _racine_carree_de(Q):
    """Polynôme P (Fractions) tel que P² = Q, ou None si Q n'est pas le carré d'un polynôme à coefficients rationnels."""
    sp = charger_sympy()
    x = SYMPY["x"]
    c, facteurs = sp.factor_list(sum(_rat(co) * x ** i for i, co in enumerate(Q)))
    r = sp.sqrt(c)
    if not r.is_Rational or any(m % 2 for _, m in facteurs):
        return None
    P = r * sp.Mul(*[f ** (m // 2) for f, m in facteurs])
    coefs = sp.Poly(P, x).all_coeffs()[::-1]
    return pn([F(int(co.p), int(co.q)) for co in coefs])


def _remplacer_racines(n, table):
    """n où chaque racine de la table {clé : arbre} est remplacée par son arbre."""
    if isinstance(n, (Nb, X, E)):
        return n
    if n.key() in table:
        return table[n.key()]
    if isinstance(n, Neg):
        return Neg(_remplacer_racines(n.a, table))
    if isinstance(n, Fn):
        return Fn(n.nom, _remplacer_racines(n.a, table))
    return Op(n.op, _remplacer_racines(n.a, table), _remplacer_racines(n.b, table))


def _racines_a_remplacer(n, out):
    r = _est_racine(n)
    if r is not None:
        Q = _poly_ou_const(r)
        if Q is not None and deg(Q) >= 2 and deg(Q) % 2 == 0:
            P = _racine_carree_de(Q)
            if P is not None:
                out.append((n, P))
                return
    if isinstance(n, (Neg, Fn)):
        _racines_a_remplacer(n.a, out)
    elif isinstance(n, Op):
        _racines_a_remplacer(n.a, out)
        _racines_a_remplacer(n.b, out)


def _simplifier_par_x_moins_a(N, D, a):
    """Fraction N/D de deux polynômes (Fractions) : (m, N2, D2) après simplification par (x − a)^m, m maximal."""
    m = min(_facteur_racine(N, a)[1], _facteur_racine(D, a)[1])
    if m == 0:
        return 0, N, D
    return m, _diviser_binome(N, a, m), _diviser_binome(D, a, m)


def _racine_carre_parfait(n, ctx, fi):
    """En une valeur, d'un seul côté : √(u²) = |u|, et |u| = u ou −u selon le signe de u de ce côté (u s'annule en
    a : son signe se lit sur la factorisation en (x − a)). Chaîne d'égalités, puis simplification si possible."""
    pt = ctx.pt
    if pt.s or not pt.d or not pt.a.is_Rational:
        return None
    trouvees = []
    _racines_a_remplacer(n, trouvees)
    if not trouvees:
        return None
    a = F(int(pt.a.p), int(pt.a.q))
    table, avec_abs, vus, justs = {}, tex(n), set(), []
    for racine, P in trouvees:
        if racine.key() in vus:
            continue
        vus.add(racine.key())
        reste, mult = _facteur_racine(P, a)
        sg = _signe(peval(reste, a)) * (pt.d if mult % 2 else 1)
        arbre = _arbre_poly(P)
        table[racine.key()] = arbre if sg > 0 else Neg(arbre)
        u = tex(arbre)
        avec_abs = avec_abs.replace(tex(racine), rf"|{u}|")
        justs.append(rf"{u} {'>' if sg > 0 else '<'} 0 \text{{ : }} |{u}| = "
                     + (u if sg > 0 else rf"-{_entre_parentheses(u)}"))
    g = _remplacer_racines(n, table)
    _meme_fonction(n, g, ctx)
    ch = ctx.chaine(n)
    ch.lim(avec_abs, r" ,\; ".join(rf"\sqrt{{{_entre_parentheses(tex(_arbre_poly(P)))}^{{2}}}} = |{tex(_arbre_poly(P))}|"
                                    for P in dict((r.key(), P) for r, P in trouvees).values()))
    ch.lim(tex(g), r" ,\; ".join(justs), g)
    # g est une fraction de polynômes avec un facteur commun (x − a) : on simplifie dans la même chaîne
    N, D = (_poly_ou_const(g.a), _poly_ou_const(g.b)) if isinstance(g, Op) and g.op == "/" else (None, None)
    g2 = g
    if N is not None and D is not None:
        m, N2, D2 = _simplifier_par_x_moins_a(N, D, a)
        if m:
            g2 = _arbre_fraction(N2, D2)
            ch.lim(tex(g2), r"\text{on simplifie}", g2)
    L, narration = _noeud(g2, ctx)
    _conclure(ch, g2, L, ctx)
    _annoncer(ch, n, fi, ctx)
    return L, list(narration) + [ch]


# --- méthode : expression conjuguée (∞ − ∞ en ±∞ ; 0/0 en une valeur) -----------------------------
def _carre_poly(n):
    """Polynôme P tel que n² = P, pour n polynôme, √(polynôme) ou l'opposé de l'un d'eux ; None sinon."""
    if isinstance(n, Neg):
        return _carre_poly(n.a)
    r = _est_racine(n)
    if r is not None:
        return _poly_ou_const(r)
    W = _poly_ou_const(n)
    return pmul(W, W) if W is not None else None


def _entre_parentheses(t):
    return r"\left(" + t + r"\right)" if (" + " in t or " - " in t) else t


def _carre_tex(n):
    """Écriture de n² une fois la racine disparue : x^{2} + x pour √(x^2 + x), x^{2} pour x."""
    r = _est_racine(n)
    if r is not None:
        return tex(r)
    return tex(Op("^", n.a if isinstance(n, Neg) else n, Nb(F(2))))


def _diviser_binome(P, a, m):
    """P / (x − a)^m (division exacte, a rationnel)."""
    for _ in range(m):
        P, reste = pdivlin(P, a)
        if reste != 0:
            raise Abandon("division par (x − a) non exacte")
    return P


def _conjuguee_difference(n, ctx, fi):
    """U ± V avec ∞ − ∞ : (U ± V)(U ∓ V)/(U ∓ V) = (U² − V²)/(U ∓ V), puis on continue avec cette fraction."""
    if fi.nom != "∞ − ∞" or not ctx.pt.s:
        return None
    U, V = n.a, n.b
    PU, PV = _carre_poly(U), _carre_poly(V)
    if PU is None or PV is None or not (_est_racine(U) is not None or _est_racine(V) is not None):
        return None
    R = padd(PU, pscal(PV, -1))
    if nul(R):
        return None
    sigma = 1 if n.op == "+" else -1
    conj = Op("-", U, V) if sigma > 0 else Op("+", U, V)
    g = Op("/", _arbre_poly(R), conj)
    _meme_fonction(n, g, ctx)
    L, narration = _noeud(g, ctx)
    ch = ctx.chaine(n)
    ch.lim(tex(g), r"\text{conjuguée}", g)
    avant, apres = _prolonger(ch, g, L, narration, ctx)
    _annoncer(ch, n, fi, ctx)
    return L, avant + [ch] + apres


def _facteur_ou_vide(P):
    """tex d'un polynôme sauf s'il vaut 1 (facteur neutre d'un produit)."""
    return "" if (deg(P) == 0 and P[0] == 1) else _entre_parentheses(tex(_arbre_poly(P)))


def _conjuguee_zero_sur_zero(n, ctx, fi):
    """0/0 en un point rationnel, avec une différence de racines au numérateur (ou au dénominateur) sur un
    polynôme : on multiplie par la conjuguée, on factorise et on simplifie par (x − a)."""
    pt = ctx.pt
    if fi.nom != "0/0" or pt.s or not pt.a.is_Rational or not (isinstance(n, Op) and n.op == "/"):
        return None
    a = F(int(pt.a.p), int(pt.a.q))
    for racine_au_numerateur in (True, False):
        W, Z = (n.a, n.b) if racine_au_numerateur else (n.b, n.a)       # W : différence avec racine, Z : l'autre
        if not (isinstance(W, Op) and W.op in "+-"):
            continue
        PU, PV, PZ = _carre_poly(W.a), _carre_poly(W.b), _poly_ou_const(Z)
        if PU is None or PV is None or PZ is None or not (_est_racine(W.a) is not None or _est_racine(W.b) is not None):
            continue
        R = padd(PU, pscal(PV, -1))
        if nul(R) or peval(R, a) != 0:
            continue
        m = min(_facteur_racine(R, a)[1], _facteur_racine(PZ, a)[1])
        if m == 0:
            continue
        conj = Op("-", W.a, W.b) if W.op == "+" else Op("+", W.a, W.b)
        R2, Z2 = _diviser_binome(R, a, m), _diviser_binome(PZ, a, m)
        xa = _x_moins(a)
        barre = r"\cancel{" + (_facteur_tex(xa, m) if a != 0 else ("x" if m == 1 else f"x^{{{m}}}")) + "}"
        carres = _entre_parentheses(_carre_tex(W.a)) + " - " + _entre_parentheses(_carre_tex(W.b))
        tz, tw = _facteur_ou_vide(PZ), tex(W)
        tc = _entre_parentheses(tex(conj))
        R_tex = tex(_arbre_poly(R))
        if racine_au_numerateur:
            g = Op("/", _arbre_poly(R2), conj if not _facteur_ou_vide(Z2) else Op("*", _arbre_poly(Z2), conj))
            egalites = (rf"\dfrac{{\left({tw}\right){tc}}}{{{_produit_tex(tz, tc)}}}",
                        rf"\dfrac{{{carres}}}{{{_produit_tex(tz, tc)}}}", rf"\dfrac{{{R_tex}}}{{{_produit_tex(tz, tc)}}}")
            haut = _produit_tex(barre, _facteur_ou_vide(R2))
            bas = _produit_tex(barre, _facteur_ou_vide(Z2), tc)
        else:
            haut_g = Op("*", _arbre_poly(Z2), conj) if _facteur_ou_vide(Z2) else conj
            g = haut_g if not _facteur_ou_vide(R2) else Op("/", haut_g, _arbre_poly(R2))
            egalites = (rf"\dfrac{{{_produit_tex(tz, tc)}}}{{\left({tw}\right){tc}}}",
                        rf"\dfrac{{{_produit_tex(tz, tc)}}}{{{carres}}}", rf"\dfrac{{{_produit_tex(tz, tc)}}}{{{R_tex}}}")
            haut = _produit_tex(barre, _facteur_ou_vide(Z2), tc)
            bas = _produit_tex(barre, _facteur_ou_vide(R2))
        _meme_fonction(n, g, ctx)
        L, narration = _noeud(g, ctx)
        ch = ctx.chaine(n)
        ch.lim(rf"\dfrac{{{haut}}}{{{bas}}}", rf"\text{{conjuguée, puis factorisation par }} \left({xa}\right)")
        ch.lim(tex(g), r"\text{on simplifie}", g)
        avant, apres = _prolonger(ch, g, L, narration, ctx)
        _annoncer(ch, n, fi, ctx)
        return L, avant + [ch] + apres
    return None


def _conjuguee(n, ctx, fi):
    if isinstance(n, Op) and n.op in "+-":
        return _conjuguee_difference(n, ctx, fi)
    return _conjuguee_zero_sur_zero(n, ctx, fi)




# --- méthode : croissance comparée et mise en évidence d'une exponentielle ---------------------
def _classer_facteur(h, k):
    """Facteur h^k d'un produit : ('x', exposant) | ('exp', b) pour e^{bx} | ('ln', exposant) | ('poly', P, k)."""
    if isinstance(h, X):
        return ("x", F(k))
    r = _est_racine(h)
    if r is not None and isinstance(r, X):
        return ("x", F(k, 2))
    if isinstance(h, Op) and h.op == "^" and isinstance(h.a, X):
        alpha = valeur_constante(h.b)
        return ("x", k * alpha) if alpha is not None else None
    if isinstance(h, Fn) and h.nom == "exp":
        P = _polynome_de(h.a)
        return ("exp", P[1] * k) if (P is not None and deg(P) == 1 and P[0] == 0) else None
    if isinstance(h, Fn) and h.nom == "ln" and isinstance(h.a, X):
        return ("ln", F(k))
    P = _polynome_de(h)
    return ("poly", P, k) if P is not None else None


def _params_pur(n):
    """n = C·x^N·e^{Bx}·(ln x)^q·∏ P_i^k_i : (C, N, B, q, [(P_i, k_i)]) ; None si n n'est pas de cette forme."""
    try:
        c, facs = aplatir(n)
    except Exception:
        return None
    C, N, B, q, polys = F(c), F(0), F(0), F(0), []
    for h, k in facs:
        cl = _classer_facteur(h, k)
        if cl is None:
            return None
        if cl[0] == "x":
            N += cl[1]
        elif cl[0] == "exp":
            B += cl[1]
        elif cl[0] == "ln":
            q += cl[1]
        else:
            P, kk = cl[1], cl[2]
            if len(_polynome_a_termes(P)) == 1:         # monôme c·x^m
                C *= P[-1] ** kk
                N += deg(P) * kk
            else:
                polys.append((P, kk))
    return C, N, B, q, polys


def _arbre_pur(N, B, q):
    """x^N · e^{Bx} · (ln x)^q  (q = ±1) sous forme de quotient d'arbres ; Nb(1) si tout est nul."""
    haut, bas = [], []
    if N != 0:
        puiss = X() if abs(N) == 1 else Op("^", X(), Nb(abs(N)))
        (haut if N > 0 else bas).append(puiss)
    if B != 0:
        arg = X() if B == 1 else (Neg(X()) if B == -1 else (Op("*", Nb(B), X()) if B > 0 else Neg(Op("*", Nb(-B), X()))))
        haut.append(Fn("exp", arg))
    if q != 0:
        if abs(q) != 1:
            raise Abandon("puissance de ln non prise en charge")
        (haut if q > 0 else bas).append(Fn("ln", X()))

    def produit(L):
        t = L[0]
        for u in L[1:]:
            t = Op("*", t, u)
        return t
    if not haut and not bas:
        return Nb(F(1))
    if not bas:
        return produit(haut)
    return Op("/", produit(haut) if haut else Nb(F(1)), produit(bas))


def _arbre_avec_coefficient(C, pur):
    if C == 1:
        return pur
    if isinstance(pur, Nb):
        return Nb(abs(C)) if C > 0 else Neg(Nb(-C))
    return Op("*", Nb(C), pur) if C > 0 else Neg(Op("*", Nb(-C), pur))


REFERENCES = {
    "exp_sur_puissance": (r"\lim_{x\to +\infty} \dfrac{e^{ax}}{x^{n}} = +\infty", r"a > 0 \text{ et } n > 0"),
    "puissance_exp_neg": (r"\lim_{x\to +\infty} x^{n}e^{-ax} = 0", r"a > 0 \text{ et } n > 0"),
    "puissance_exp_moins_inf": (r"\lim_{x\to -\infty} x^{n}e^{ax} = 0", r"a > 0 \text{ et } n \text{ entier positif}"),
    "ln_sur_puissance": (r"\lim_{x\to +\infty} \dfrac{\ln x}{x^{n}} = 0", r"n > 0"),
    "puissance_sur_ln": (r"\lim_{x\to +\infty} \dfrac{x^{n}}{\ln x} = +\infty", r"n > 0"),
    "puissance_ln_zero": (r"\lim_{x\to 0^{+}} x^{n}\ln x = 0", r"n > 0"),
}


def _reference(N, B, q, pt):
    """(nom de la limite de référence, limite) pour C·x^N e^{Bx} (ln x)^q au point d'étude, ou None."""
    s = pt.s
    if s and q == 0 and B != 0:
        if s > 0 and B > 0 and N < 0:
            return "exp_sur_puissance", Lim.infini(1)
        if s > 0 and B < 0 and N > 0:
            return "puissance_exp_neg", Lim.fin(0, 1)
        if s < 0 and B > 0 and N > 0 and N.denominator == 1:
            return "puissance_exp_moins_inf", Lim.fin(0, 1 if int(N) % 2 == 0 else -1)
    elif s and B == 0 and q == 1 and N < 0 and s > 0:
        return "ln_sur_puissance", Lim.fin(0, 1)
    elif s and B == 0 and q == -1 and N > 0 and s > 0:
        return "puissance_sur_ln", Lim.infini(1)
    elif not s and pt.a == 0 and pt.d > 0 and B == 0 and q == 1 and N > 0:
        return "puissance_ln_zero", Lim.fin(0, -1)
    return None


def _ligne_reference(nom):
    lim, cond = REFERENCES[nom]
    return rf"limite de référence : \({lim}\) pour \({cond}\)"


def _comparee_pure(n, ctx, fi):
    """Produit ou quotient de x^n, e^{ax}, ln x : on nomme la limite de référence utilisée ; un facteur
    polynôme est d'abord mis sous la forme c·x^m(1 + …)."""
    if not isinstance(n, Op) or n.op not in "*/":
        return None
    r = _params_pur(n)
    if r is None:
        return None
    C, N, B, q, polys = r
    if polys:
        # un facteur polynôme est mis sous la forme c·x^m(1 + …) seulement en ±∞ et si une limite de référence suit
        if not ctx.pt.s or _reference(N + sum(deg(P) * k for P, k in polys), B, q, ctx.pt) is None:
            return None
        return _comparee_avec_polynomes(n, ctx, fi, C, N, B, q, polys)
    ref = _reference(N, B, q, ctx.pt)
    if ref is None or C == 0:
        return None
    nom, Lref = ref
    pur = _arbre_pur(N, B, q)
    L = Lref if C > 0 else (_oppose(Lref) if not Lref.nul() else Lim.fin(0, -Lref.ap))
    if L.nul():
        L = Lim.fin(0, Lref.ap * (1 if C > 0 else -1))
    lim_ref, cond = REFERENCES[nom]
    ch = ctx.chaine(n)
    just = rf"\text{{croissance comparée : }} {lim_ref}"
    if C != 1 or tex(pur) != tex(n):
        ch.lim(rf"{tex(_arbre_avec_coefficient(C, pur))}", None)
    ch.val(L.tex(False), just)
    ch.complete = True
    _annoncer(ch, n, fi, ctx)
    return L, [ch]


def _comparee_avec_polynomes(n, ctx, fi, C, N, B, q, polys):
    """(x + 1)e^{-x} : on met x en évidence dans le polynôme, puis on conclut avec le produit sans polynôme."""
    sp = charger_sympy()
    egalites, crochets = [], None
    x = SYMPY["x"]
    for P, k in polys:
        m = deg(P)
        tete, interieur, complet, termes = _facteur_detaille(P, m)
        egalites.append(rf"{ptex(P, 'x')} = {complet}")
        C, N = C * P[-1] ** k, N + m * k
        bt = _somme_termes([(False, Nb(F(1)))] + [_terme_laurent(P[j] / P[-1], j - m) for j in range(m - 1, -1, -1) if P[j] != 0]) \
            if len(_polynome_a_termes(P)) > 1 else Nb(F(1))
        if k == 1:
            facteur = bt
        elif k == -1:
            facteur = Op("/", Nb(F(1)), bt)
        else:
            facteur = Op("^", bt, Nb(F(k))) if k > 0 else Op("/", Nb(F(1)), Op("^", bt, Nb(F(-k))))
        crochets = facteur if crochets is None else Op("*", crochets, facteur)
    g = Op("*", _arbre_avec_coefficient(C, _arbre_pur(N, B, q)), crochets)
    _meme_fonction(n, g, ctx)
    L, narration = _noeud(g, ctx)
    ch = ctx.chaine(n)
    ch.lim(tex(g), r"\text{mise en évidence}")
    avant, apres = _prolonger(ch, g, L, narration, ctx)
    _annoncer(ch, n, fi, ctx)
    return L, avant + [ch] + apres


def _termes_de_somme(S, s):
    """[(signe, (C, N, B, q))] des termes purs de S, ou None."""
    out = []
    for t, sg in _feuilles(S):
        r = _params_pur(t)
        if r is None or r[4]:
            return None
        C, N, B, q, _ = r
        out.append((sg, (C, N, B, q)))
    return out


def _evidence_somme(S, s):
    """Met en évidence le terme dominant d'une somme de termes purs (exponentielle, puissance, ln) en s∞ :
    S = D·(1 + …). Renvoie (paramètres de D, arbre de D, arbre du crochet) ou None."""
    termes = _termes_de_somme(S, s)
    if termes is None or len(termes) < 2:
        return None
    cle = lambda p: (p[2] * s, p[1], p[3])
    ordre = sorted(range(len(termes)), key=lambda i: cle(termes[i][1]), reverse=True)
    i0 = ordre[0]
    if cle(termes[i0][1]) == cle(termes[ordre[1]][1]):
        return None
    sg0, (C0, N0, B0, q0) = termes[i0]
    exp_dominante = B0 * s > 0
    poly_sur_ln = B0 == 0 and q0 == 0 and N0 > 0 and any(p[3] != 0 for _, p in termes)
    if not (exp_dominante or poly_sur_ln):
        return None
    coef0 = sg0 * C0
    crochet = Nb(F(1))
    for i, (sg, (C, N, B, q)) in enumerate(termes):
        if i == i0:
            continue
        c = (sg * C) / coef0
        if abs(q - q0) > 1:
            return None
        pur = _arbre_pur(N - N0, B - B0, q - q0)
        t = _arbre_avec_coefficient(abs(c), pur)
        crochet = Op("+" if c > 0 else "-", crochet, t)
    D = _arbre_avec_coefficient(abs(coef0), _arbre_pur(N0, B0, q0))
    if coef0 < 0:
        D = Neg(D)
    return (C0 * sg0, N0, B0, q0), D, crochet


def _evidence_exp(n, ctx, fi):
    """∞ − ∞ ou ∞/∞ avec une somme dont le terme dominant est une exponentielle (ou x devant ln x) : on met
    ce terme en évidence ; les termes restants se traitent par croissance comparée."""
    s = ctx.pt.s
    if not s or not isinstance(n, Op):
        return None
    if n.op in "+-" and fi.nom == "∞ − ∞":
        r = _evidence_somme(n, s)
        if r is None:
            return None
        _, D, crochet = r
        g = Op("*", D, crochet)
        just = r"\text{mise en évidence}"
    elif n.op == "/" and fi.nom == "∞/∞":
        cotes = []
        for S in (n.a, n.b):
            r = _evidence_somme(S, s) if (isinstance(S, Op) and S.op in "+-") else None
            if r is not None:
                cotes.append((S, r[0], r[1], r[2]))
            else:
                p = _params_pur(S)
                if p is None or p[4]:
                    return None
                cotes.append((S, (p[0], p[1], p[2], p[3]), None, None))
        if cotes[0][2] is None and cotes[1][2] is None:
            return None
        (C1, N1, B1, q1), (C2, N2, B2, q2) = cotes[0][1], cotes[1][1]
        pur = _arbre_avec_coefficient(C1 / C2, _arbre_pur(N1 - N2, B1 - B2, q1 - q2))
        neutre = isinstance(pur, Nb) and pur.v == 1
        haut = [t for t in (None if neutre else pur, cotes[0][3]) if t is not None]
        g = haut[0] if len(haut) == 1 else (Op("*", haut[0], haut[1]) if haut else Nb(F(1)))
        if cotes[1][3] is not None:
            g = Op("/", g, cotes[1][3])
        just = r"\text{mise en évidence}"
    else:
        return None
    _meme_fonction(n, g, ctx)
    L, narration = _noeud(g, ctx)
    ch = ctx.chaine(n)
    ch.lim(tex(g), just, g)
    avant, apres = _prolonger(ch, g, L, narration, ctx)
    _annoncer(ch, n, fi, ctx)
    return L, avant + [ch] + apres


# --- méthode : règle de Bernoulli-L'Hôpital (dernier recours), hypothèses vérifiées et écrites ---------
def _racines_de(n, out):
    r = _est_racine(n)
    if r is not None:
        out.append(r)
    if isinstance(n, (Neg, Fn)):
        _racines_de(n.a, out)
    elif isinstance(n, Op):
        _racines_de(n.a, out)
        _racines_de(n.b, out)
    return out


def _intervalle_derivable(f, g, ctx):
    """Intervalles ouverts, au voisinage du point d'étude, où f et g sont définies et dérivables (une racine
    carrée n'est pas dérivable là où son argument s'annule) ; None si on ne peut pas l'affirmer. Pour une valeur
    interdite étudiée des deux côtés, les deux côtés sont réunis."""
    pt = ctx.pt
    try:
        D = fusion(inter(domaine(f), domaine(g)))
    except Exception:
        return None
    for h in (f, g):
        for arg in _racines_de(h, []):
            if sans_x(arg):
                continue
            try:
                Z = signe_facteur(arg, "x")[2]
            except Exception:
                return None
            D = fusion(inter(D, complement(Z)))
    ouverts = [Iv(iv.lo, False, iv.hi, False) for iv in D if iv.lo is None or iv.hi is None or iv.lo.val < iv.hi.val]
    if pt.s:
        voisins = [iv for iv in ouverts if (iv.hi is None if pt.s > 0 else iv.lo is None)]
        return voisins or None
    a = float(pt.a)

    def a_gauche(iv):
        return (iv.hi is not None and proche(iv.hi.val, a)) or ((iv.lo is None or iv.lo.val < a) and (iv.hi is None or iv.hi.val > a))

    def a_droite(iv):
        return (iv.lo is not None and proche(iv.lo.val, a)) or ((iv.lo is None or iv.lo.val < a) and (iv.hi is None or iv.hi.val > a))

    cotes = (-1, 1) if pt.deux else (pt.d,)
    voisins = []
    for d in cotes:
        trouves = [iv for iv in ouverts if (a_gauche(iv) if d < 0 else a_droite(iv))]
        if not trouves:
            return None
        voisins += [iv for iv in trouves if iv not in voisins]
    return voisins


def _g_prime_non_nul(g, gp, I, ctx):
    """Tex qui établit que la dérivée du dénominateur ne s'annule pas au voisinage du point d'étude (sauf peut-être en lui),
    écrite (g)' = … ≠ 0 (f désigne déjà la fonction étudiée : ni « g'(x) » ni « f'/g' »), ou None."""
    pt = ctx.pt
    deriv = rf"{tex(g)}'" if isinstance(g, X) else rf"\left({tex(g)}\right)'"
    if sans_x(gp):
        v = valeur_constante(gp)
        return rf"{deriv} = {tex(gp)} \neq 0" if v else None
    try:
        D, P, Z, _, _ = signe_facteur(gp, "x")
        Z = fusion(inter(Z, I))
        if not pt.s:
            a = float(pt.a)
            Z = [iv for iv in Z if not (iv.lo is not None and proche(iv.lo.val, a))]
    except Exception:
        return None
    if Z and pt.s:
        # en ±∞ il suffit que g' ne s'annule pas au voisinage : après son dernier zéro (x > z en +∞, x < z en −∞)
        if any(iv.lo is None or iv.hi is None or iv.lo.val != iv.hi.val for iv in Z):
            return None
        z = max((iv.lo for iv in Z), key=lambda m: m.val) if pt.s > 0 else min((iv.lo for iv in Z), key=lambda m: m.val)
        I = [Iv(z, False, None, False)] if pt.s > 0 else [Iv(None, False, z, False)]
        Z = []
    if Z:
        return None
    return rf"{deriv} = {tex(gp)} \text{{ ne s'annule pas sur }} {ens_tex(I)}"


def _nettoyer_arbre(t):
    """-1·u devient -u, 1·u devient u (sortie de arbre_depuis_sympy)."""
    if isinstance(t, Neg):
        return Neg(_nettoyer_arbre(t.a))
    if isinstance(t, Fn):
        return Fn(t.nom, _nettoyer_arbre(t.a))
    if isinstance(t, Op):
        a, b = _nettoyer_arbre(t.a), _nettoyer_arbre(t.b)
        if t.op == "*":
            if isinstance(a, Neg) and isinstance(a.a, Nb) and a.a.v == 1:
                return Neg(b)
            if isinstance(a, Nb) and a.v == 1:
                return b
            if isinstance(b, Nb) and b.v == 1:
                return a
        return Op(t.op, a, b)
    return t


def _arbre_propre(arbre):
    """Une fraction rationnelle revient sous la forme N/D de polynômes développés (2x - 4)/(x^2 - 4x)."""
    try:
        dec = decomposer(arbre)
        if dec[0] == "x":
            N, D = dec[1]
            if not nul(N):
                return _arbre_fraction(N, D) if not (deg(D) == 0) else _arbre_poly([c / D[0] for c in N])
    except Exception:
        pass
    return _nettoyer_arbre(arbre)


def _derivee(h):
    sp = charger_sympy()
    e = en_sympy_reel(h)
    return sp.diff(e, SYMPY["x"])


def _oppose_arbre(u):
    """Arbre de −u : −(−v) = v, −(c·v) = (−c)·v."""
    if isinstance(u, Neg):
        return u.a
    if isinstance(u, Nb):
        return Nb(-u.v)
    if isinstance(u, Op) and u.op == "*" and isinstance(u.a, Nb):
        return Op("*", Nb(-u.a.v), u.b)
    return Neg(u)


def _inverse_en_bas(z):
    """Dénominateur g tel que z = 1/g, écrit comme dans le corrigé : eᵘ = 1/e^(−u), xᵏ = 1/x^(−k), x = 1/(1/x) ; sinon 1/z."""
    if isinstance(z, Fn) and z.nom == "exp":
        return Fn("exp", _oppose_arbre(z.a))
    if isinstance(z, X):
        return Op("/", Nb(F(1)), X())
    if isinstance(z, Op) and z.op == "^" and isinstance(z.a, X):
        k = valeur_constante(z.b)
        if k is not None and not isinstance(k, float) and k > 0:
            return Op("^", X(), Nb(-k))
    return Op("/", Nb(F(1)), z)


def _est_ln(h):
    return isinstance(h, Fn) and h.nom == "ln"


def _candidats_lhopital(n, ctx, fi):
    """(f, g, lignes d'introduction) : f/g est une forme 0/0 ou ∞/∞ égale à n. Produit 0·∞ (règle du corrigé, 29.10.2026) : le facteur
    qui tend vers 0 passe en bas, l'autre reste en haut (un ln reste toujours en haut) ; l'ordre de saisie ne compte pas."""
    if isinstance(n, Op) and n.op == "/" and fi.nom in ("0/0", "∞/∞"):
        return [(n.a, n.b, [], fi.nom)]
    if isinstance(n, Op) and n.op == "*" and fi.nom == "0 · ∞":
        out = []
        zero_a = fi.A is not None and fi.A.nul()
        z, u = (n.a, n.b) if zero_a else (n.b, n.a)                # z tend vers 0, u vers ±∞
        ordres = []
        if not _est_ln(z):
            ordres.append((u, z))
        ordres += [(n.b, n.a), (n.a, n.b)]                         # repli : l'ancien ordre
        for haut, bas in ordres:
            g = _inverse_en_bas(bas)
            if any(tex(haut) == tex(c[0]) and tex(g) == tex(c[1]) for c in out):
                continue
            out.append((haut, g, [rf"On écrit \({tex(n)} = \dfrac{{{tex(haut)}}}{{{tex(g)}}}\) pour obtenir un quotient."], None))
        return out
    return []


def _sortir_constante(n, ctx, fi):
    """0·(±∞) avec une constante multiplicative (x³e^(3x−5) = e^(−5)·x³e^(3x)) : on la sort du produit, elle ne change ni le résultat 0 ou ∞
    ni (si elle est positive) son signe ; la limite du reste se fait à part (Bernoulli-L'Hôpital)."""
    if fi.nom != "0 · ∞" or not (isinstance(n, Op) and n.op == "*"):
        return None
    facteurs = []
    _facteurs(n, facteurs)
    cstes, autres, change = [], [], False
    for h in facteurs:
        if sans_x(h):
            cstes.append(h)
            change = True
        elif isinstance(h, Fn) and h.nom == "exp" and (P := _polynome_de(h.a)) is not None and deg(P) == 1 and P[0] != 0:
            cstes.append(Fn("exp", Nb(P[0])))
            autres.append(Fn("exp", _arbre_poly([F(0), P[1]])))
            change = True
        else:
            autres.append(h)
    if not change or not autres:
        return None
    produit = lambda L: L[0] if len(L) == 1 else Op("*", produit(L[:-1]), L[-1])
    g = Op("*", produit(cstes), produit(autres))
    _meme_fonction(n, g, ctx)
    L, narration = _noeud(g, ctx)
    ch = ctx.chaine(n)
    ch.lim(tex(g), r"\text{on sort la constante}", g)
    avant, apres = _prolonger(ch, g, L, narration, ctx)
    _annoncer(ch, n, fi, ctx)
    return L, avant + [ch] + apres


def _lhopital(n, ctx, fi):
    if ctx.nb_lhopital >= MAX_LHOPITAL:
        return None
    if isinstance(n, Op) and n.op == "/" and _poly_ou_const(n.a) is not None and _poly_ou_const(n.b) is not None:
        return None                                  # fraction rationnelle : mise en évidence ou factorisation, jamais L'Hôpital
    for f, g, intro, nom in _candidats_lhopital(n, ctx, fi):
        c0, d0 = len(ctx.cf), len(ctx.demandes)
        try:
            r = _lhopital_avec(n, f, g, intro, nom, ctx, fi)
        except Abandon:
            r = None
        if r is not None:
            return r
        del ctx.cf[c0:]
        del ctx.demandes[d0:]
    return None


def _lhopital_avec(n, f, g, intro, nom, ctx, fi):
    sp = charger_sympy()
    pt = ctx.pt
    # (a) forme indéterminée 0/0 ou ∞/∞
    if nom is None:
        c0, d0 = len(ctx.cf), len(ctx.demandes)
        Lf, _ = _noeud(f, ctx)
        Lg, _ = _noeud(g, ctx)
        del ctx.cf[c0:]                                  # les signes lus ici ne servent qu'à reconnaître la forme
        del ctx.demandes[d0:]                            # ... ni les tableaux de signes (aucun tableau sans renvoi)
        if Lf.nul() and Lg.nul():
            nom = "0/0"
        elif Lf.inf and Lg.inf:
            nom = "∞/∞"
        else:
            return None
    # (b) dérivabilité au voisinage du point
    I = _intervalle_derivable(f, g, ctx)
    if I is None:
        return None
    # dérivées et leur quotient
    fp, gp = _derivee(f), _derivee(g)
    try:
        f_arbre, g_arbre = _arbre_propre(arbre_depuis_sympy(fp)), _arbre_propre(arbre_depuis_sympy(gp))
        q_arbre = _arbre_propre(arbre_depuis_sympy(sp.simplify(fp / gp)))
    except Exception:
        return None
    # (c) g' ≠ 0 au voisinage
    texte_c = _g_prime_non_nul(g, g_arbre, I, ctx)
    if texte_c is None:
        return None
    ctx.nb_lhopital += 1
    brut = None
    try:
        if sans_x(g_arbre):                              # g' constante : on garde f'/g' tel quel, (1/x)/1, si la substitution suffit
            brut = Op("/", f_arbre, g_arbre)
            c0 = len(ctx.cf)
            try:
                Lb, lgb = _noeud(brut, ctx)
            except Abandon:
                Lb = None
            if Lb is not None and not any(isinstance(l, Chaine) for l in lgb):
                q_arbre = brut
            else:
                brut = None
                del ctx.cf[c0:]
        L, lg = _noeud(q_arbre, ctx)
        ch = ctx.chaine(n)
        if intro:                                        # produit mis en quotient : u·v = u/(1/v)
            ch.lim(rf"\dfrac{{{tex(f)}}}{{{tex(g)}}}", rf"\text{{on écrit un quotient de la forme }} « \infty/\infty »"
                   if nom == "∞/∞" else r"\text{on écrit un quotient de la forme } « 0/0 »", Op("/", f, g))
        hyp = (rf"\text{{Bernoulli-L'Hôpital : }} {tex(f)} \text{{ et }} {tex(g)} \text{{ dérivables sur }} {ens_tex(I)} ,\; "
               rf"{texte_c}")
        ch.lim(tex(q_arbre), hyp, q_arbre)
        if brut is not None:                             # (1/x)/1 = 1 : la valeur suit directement, sans substitution
            ch.val(L.tex(False), force=True)
            ch.complete = True
            avant, apres = list(lg), []
        else:
            avant, apres = _prolonger(ch, q_arbre, L, lg, ctx)
    finally:
        ctx.nb_lhopital -= 1
    _annoncer(ch, n, fi, ctx)
    return L, avant + [ch] + apres


def _simplifier_zero_sur_zero(n, ctx, fi):
    """Quotient de deux polynômes en 0/0 en un point rationnel : on factorise par (x − a), on simplifie, puis on continue."""
    pt = ctx.pt
    if fi.nom != "0/0" or pt.s or not pt.a.is_Rational or not (isinstance(n, Op) and n.op == "/"):
        return None
    N, D = _poly_ou_const(n.a), _poly_ou_const(n.b)
    if N is None or D is None:
        return None
    a = F(int(pt.a.p), int(pt.a.q))
    m = min(_facteur_racine(N, a)[1], _facteur_racine(D, a)[1])
    if m == 0:
        return None
    N2, D2 = _diviser_binome(N, a, m), _diviser_binome(D, a, m)
    xa = _x_moins(a)
    barre = r"\cancel{" + _facteur_tex(xa, m) + "}"
    g = _arbre_fraction(N2, D2)
    haut = ("-" if N2 == [-1] else "") + _produit_tex(barre, "" if N2 in ([1], [-1]) else _facteur_ou_vide(N2))
    bas = ("-" if D2 == [-1] else "") + _produit_tex(barre, "" if D2 in ([1], [-1]) else _facteur_ou_vide(D2))
    L, narration = _noeud(g, ctx)
    ch = ctx.chaine(n)
    ch.lim(rf"\dfrac{{{haut}}}{{{bas}}}", rf"\text{{on factorise par }} \left({xa}\right)")
    ch.lim(tex(g), r"\text{on simplifie}", g)
    _conclure(ch, g, L, ctx)
    _annoncer(ch, n, fi, ctx)
    return L, list(narration) + [ch]


# ordre du cours : mise en évidence, conjuguée, mise en évidence sous une racine, constante sortie du produit, L'Hôpital.
# Depuis le 29.10.2026 (doctrine du chantier 3M) la croissance comparée ne justifie plus rien : _comparee_pure et _evidence_ln ne sont plus
# dans la liste (leur code reste, à supprimer plus tard) ; les limites eˣ/xⁿ, xⁿ/eˣ, ln x/xⁿ, xⁿ ln x passent par Bernoulli-L'Hôpital.
METHODES[:] = [_racine_carre_parfait, _simplifier_zero_sur_zero, _evidence_exp, _conjuguee, _evidence_racine, _sortir_constante, _lhopital]





def _noeud(n, ctx):
    """(limite de n au point d'étude, chaînes d'égalités qui la justifient) ; Abandon si l'on ne peut pas la justifier."""
    L, lignes = _noeud_calcul(n, ctx)
    ctx.lims[n.key()] = L
    return L, lignes


def _noeud_calcul(n, ctx):
    pt = ctx.pt
    n0 = len(ctx.cf)
    if sans_x(n):
        return Lim.fin(_const_sympy(n), None), []
    if isinstance(n, X):
        return pt.lim_x(), []
    r = _noeud_polynome(n, ctx) if not pt.s else _noeud_rationnel_infini(n, ctx)
    if r is not None:
        return r
    try:
        if isinstance(n, Neg):
            U, lu = _noeud(n.a, ctx)
            L = _oppose(U)
            ctx.verifier(n, L)
            return L, lu
        if isinstance(n, Op) and n.op in "+-*/":
            A, la = _noeud(n.a, ctx)
            B, lb = _noeud(n.b, ctx)
            if n.op == "/" and B.nul() and not A.nul():
                if not B.ap:
                    raise Abandon("signe du dénominateur inconnu")
                L = _quotient(A, B)
                ctx.verifier(n, L)
                return L, la + lb + ctx.signe_de(n.b, B, "den")
            try:
                L = {"+": lambda: _somme(A, B), "-": lambda: _somme(A, _oppose(B)),
                     "*": lambda: _produit(A, B), "/": lambda: _quotient(A, B)}[n.op]()
            except FormeIndeterminee as fi:
                fi.A, fi.B, fi.la, fi.lb = A, B, la, lb
                raise
            ctx.verifier(n, L)
            return L, la + lb
        if isinstance(n, Op) and n.op == "^":
            alpha = valeur_constante(n.b)
            if alpha is None:
                raise Abandon("exposant non rationnel")
            U, lu = _noeud(n.a, ctx)
            if alpha.denominator == 1:
                if alpha == 0 or abs(alpha) > 64 or alpha == 1:
                    raise Abandon("exposant 0, 1 ou trop grand")
                L = _puissance_entiere(U, int(alpha))
            else:
                L = _puissance_reelle(U, alpha)
        elif isinstance(n, Fn):
            U, lu = _noeud(n.a, ctx)
            if n.nom == "exp":
                L = _exp_lim(U)
            elif n.nom == "ln":
                L = _ln_lim(U)
            else:
                L = _puissance_reelle(U, F(1, 2))
        else:
            raise Abandon(f"sous-expression non prise en charge : {tex(n)}")
        ctx.verifier(n, L)
        # le signe d'un argument qui tend vers 0 ne sert que pour ln et pour une puissance
        besoin_signe = U.nul() and U.ap and not (isinstance(n, Fn) and n.nom in ("exp", "sqrt"))
        pre = []
        if besoin_signe and not isinstance(n.a, X):
            genre = "ln" if isinstance(n, Fn) else ("den" if valeur_constante(n.b) < 0 else "ln")
            pre = ctx.signe_de(n.a, U, genre)
        return L, lu + pre
    except FormeIndeterminee as fi:
        fi.noeud = n
        return _lever(n, ctx, fi, n0)


def _sans_doublons(lignes):
    vues, out = set(), []
    for l in lignes:
        cle = l.html() if isinstance(l, Chaine) else l
        if cle not in vues:
            vues.add(cle)
            out.append(l)
    return out


def _rediger(f, pt, ref, prefixe=None):
    """(lignes, None) si la limite de f en pt est rédigée et coïncide avec ref (valeur SymPy), sinon
    (None, raison technique)."""
    try:
        R = _lim_depuis_sympy(ref)
        ctx = _Contexte(pt, f, R, prefixe)
        L, lignes = _noeud(f, ctx)
        if not _meme_valeur(L, R):
            raise Abandon(f"valeur rédigée {L.tex()} ≠ référence {R.tex()}")
        lignes = _sans_doublons(lignes)
        chaine_f = next((l for l in lignes if isinstance(l, Chaine) and l.est_f), None)
        if chaine_f is None:
            lignes = lignes + [_chaine_directe(f, L, ctx)]
        else:
            chaine_f.cf += ctx.cf
        lignes = _tout_texte(lignes)
        for genre, noeud in ctx.demandes:
            TABLEAUX.utiliser(genre, noeud)
        return lignes, None
    except Exception as e:      # rien ne doit faire échouer l'étude : on retombe sur le résultat seul
        return None, f"{type(e).__name__} : {e}"


def _repli(pt, vtex, detail, label="f(x)"):
    lim = rf"\displaystyle\lim_{{x\to {pt.tex()}}} {label} = {vtex}"
    item = txt(PHRASE_REPLI + rf"\({lim}\).")
    item["detail"] = detail
    return item


def _narrer_limite(f, pt, ref, vtex, items, alternative=None, label="f(x)", prefixe=None):
    """Étapes de lim f en pt : rédigées si possible, sinon phrase de repli et résultat de référence.
    alternative = (arbre équivalent, phrase d'introduction) : essayée si f, telle qu'elle est écrite, résiste."""
    lignes, detail = _rediger(f, pt, ref, prefixe)
    if lignes is None and alternative is not None:
        g, intro = alternative
        lignes2, detail2 = _rediger(g, pt, ref, prefixe)
        if lignes2 is not None:
            lignes, detail = [intro] + lignes2, None
        else:
            detail = f"{detail} ; sous forme de fraction : {detail2}"
    if lignes is None:
        items.append(_repli(pt, vtex, detail, label))
    else:
        items.extend(txt(l) for l in lignes)


def _equation_affine(a_tex, b_tex, var="x"):
    """Combine a et b (déjà en tex) en « ax + b » proprement (signes, a=±1)."""
    partie_a = var if a_tex == "1" else ("-" + var if a_tex == "-1" else a_tex + var)
    if b_tex.startswith("-"):
        return partie_a + " - " + b_tex[1:].lstrip()
    if b_tex == "0":
        return partie_a
    return partie_a + " + " + b_tex


def _oblique_generale(f, signe, items):
    """Cherche une asymptote oblique d'une fonction quelconque (pas seulement
    rationnelle) : a = lim f(x)/x, b = lim [f(x) - ax], via le calcul formel."""
    sp = charger_sympy()
    if sp is None:
        return None
    x = SYMPY["x"]
    cible = sp.oo if signe > 0 else -sp.oo
    try:
        fe = en_sympy_reel(f)
        a_val = _limite_brute(fe / x, cible, None)
        if _rejete(a_val) or not a_val.is_finite or a_val == 0:
            return None
        b_val = _limite_brute(fe - a_val * x, cible, None)
        if _rejete(b_val) or not b_val.is_finite:
            return None
    except Exception:
        return None
    a_mp, avec_ln = sp.N(a_val, 30), _sonde_lointaine(f)
    if (_contradit_par_sonde(lambda mp, t: _quotient_mp(mp, f, t), avec_ln, cible, None, a_val)
            or _contradit_par_sonde(lambda mp, t: _moins_ax_mp(mp, f, a_mp, t), avec_ln, cible, None, b_val)):
        return None
    a_tex, b_tex = num_sympy(a_val).tex, num_sympy(b_val).tex
    eq = _equation_affine(a_tex, b_tex)
    pt = Pt({"type": "inf", "signe": signe})
    a_rat = F(int(a_val.p), int(a_val.q)) if a_val.is_Rational else None
    if a_rat is None:
        items.append(txt(rf"Asymptote oblique : \(y = {eq}\) (\(a = {a_tex}\), \(b = {b_tex}\))."))
    else:
        _narrer_limite(Op("/", f, X()), pt, a_val, a_tex, items, label=r"\dfrac{f(x)}{x}", prefixe="a")
        fb = _arbre_moins_ax(f, a_rat)
        coef = "" if abs(a_rat) == 1 else qtex(abs(a_rat))
        _narrer_limite(fb, pt, b_val, b_tex, items, label=rf"f(x) {'-' if a_rat > 0 else '+'} {coef}x", prefixe="b")
        items.append(txt(rf"Asymptote oblique : \(y = {eq}\)."))
        items.extend(_position_racine(f, a_rat, F(int(b_val.p), int(b_val.q)) if b_val.is_Rational else None, signe))
    return {"genre": "oblique", "a": a_tex, "b": b_tex, "a_val": float(a_val), "b_val": float(b_val),
            "equation_tex": eq}


def _arbre_moins_ax(f, a):
    """f(x) − a·x écrit en regroupant le polynôme : √(x² + x) − x + 2x devient √(x² + x) + x. Arbre générique sinon."""
    terme = X() if abs(a) == 1 else Op("*", Nb(abs(a)), X())
    generique = Op("-" if a > 0 else "+", f, terme)
    feuilles = _feuilles(f)
    racines = [(u, sg) for u, sg in feuilles if _est_racine(u) is not None]
    if not racines:
        return generique
    v = [F(0)]
    for u, sg in feuilles:
        if _est_racine(u) is None:
            P = _poly_ou_const(u)
            if P is None:
                if sans_x(u):
                    continue
                return generique
            v = padd(v, pscal(P, F(sg)))
    v = padd(v, [F(0), -a])
    arbre = None
    for u, sg in racines:
        arbre = (Neg(u) if sg < 0 else u) if arbre is None else Op("-" if sg < 0 else "+", arbre, u)
    if nul(v):
        return arbre
    return Op("-", arbre, _arbre_poly(pscal(v, F(-1)))) if v[deg(v)] < 0 else Op("+", arbre, _arbre_poly(v))


def _position_racine(f, a, b, s):
    """Position relative de la courbe de f = ±√Q + (affine), Q du second degré, et de son asymptote y = ax + b près de s∞,
    quand le signe de f(x) − (ax + b) se lit directement : ±(√Q − W) = ±r/(√Q + W), r constante, √Q + W > 0.
    Renvoie une liste d'items (vide si le cas n'est pas de cette forme ou si le signe n'est pas confirmé)."""
    if b is None:
        return []
    feuilles = _feuilles(f)
    racines = [(u, sg) for u, sg in feuilles if _est_racine(u) is not None]
    if len(racines) != 1:
        return []
    rac, ur = racines[0]
    Q = _poly_ou_const(_est_racine(rac))
    if Q is None or deg(Q) != 2:
        return []
    v = [F(0)]
    for u, sg in feuilles:
        if _est_racine(u) is None:
            P = _poly_ou_const(u)
            if P is not None:
                v = padd(v, pscal(P, F(sg)))
    if deg(v) > 1:
        return []
    w = padd([b, a], pscal(v, F(-1)))                    # ax + b − v
    W = pscal(w, F(ur))                                  # f(x) − (ax + b) = ur·(√Q − W)
    r = padd(Q, pscal(pmul(W, W), F(-1)))
    if deg(r) != 0 or r[0] == 0:
        return []
    sg = ur * (1 if r[0] > 0 else -1)
    for x in (s * 1e3, s * 1e5):                          # le signe annoncé est confirmé numériquement
        val = evaluer(f, x)
        if val is None or (val - (float(a) * x + float(b))) * sg <= 0:
            return []
    qt, rt = ptex(Q, "x"), qtex(r[0])
    racine = rf"\sqrt{{{qt}}}"
    gauche = racine + ("" if nul(W) else _suite_signee(pscal(W, F(-1))))                    # √Q − W
    conj = racine + ("" if nul(W) else _suite_signee(W))                                    # √Q + W
    gauche_h = rf"f(x) - \left({_equation_affine(qtex(a), qtex(b))}\right)"
    droite0 = gauche if ur > 0 else rf"-\left({gauche}\right)"
    ligne3 = rf"\dfrac{{{rt}}}{{{conj}}}" if ur > 0 else rf"-\dfrac{{{rt}}}{{{conj}}}"
    formule = (r"\[\begin{aligned}" + gauche_h + " &= " + droite0 + r" \\ &= " + ligne3
               + r" \qquad \left(\text{conjuguée}\right)\end{aligned}\]")
    # √Q + W est positif là où W l'est : région de W > 0 qui contient le voisinage de s∞
    w1 = W[1] if len(W) > 1 else F(0)
    pour = ""
    if w1 != 0 and (w1 > 0) == (s > 0):
        pour = rf" pour \(x {'>' if s > 0 else '<'} {qtex(-W[0] / w1)}\)"
    return [txt(formule),
            txt(rf"\(f(x) - \left({_equation_affine(qtex(a), qtex(b))}\right) {'>' if sg > 0 else '<'} 0\){pour} : "
                "la courbe est " + ("au-dessus" if sg > 0 else "au-dessous") + " de l'asymptote.")]


def _narrer_cotes(f, borne, items, ref_de, cotes=("gauche", "droite")):
    """Limites à gauche et à droite d'une valeur interdite : une ligne par côté (chaque ligne porte son côté dans lim) ; si les
    deux côtés s'écrivent de la même façon, une seule ligne (limite en a).
    ref_de(pt) donne la valeur de référence (SymPy ou exacte), son écriture tex et sa valeur numérique.
    Renvoie [(tex, valeur), …]."""
    cas = []
    for cle, d in (("gauche", -1), ("droite", 1)):
        if cle in cotes:
            pt = Pt(borne, d)
            val, vt, vv = ref_de(pt)
            cas.append((cle, pt, val, vt, vv))
    sortie = [(vt, vv) for _, _, _, vt, vv in cas]
    if len(cas) == 1:
        _, pt, val, vt, _ = cas[0]
        if vt == "?":
            items.append(txt(rf"\(\displaystyle\lim_{{x\to {pt.tex()}}} f(x) = {NON_DETERMINEE_TEX}\)."))
        else:
            _narrer_limite(f, pt, val, vt, items)
        return sortie
    (_, pg, vg_ref, vg, _), (_, pd, vd_ref, vd, _) = cas
    if "?" not in (vg, vd):
        lg, dg = _rediger(f, pg, vg_ref)
        ld, dd = _rediger(f, pd, vd_ref)
        if lg is not None and ld is not None:
            for ligne in _fusion_cotes(lg, ld, pg, pd, Pt(borne, 0)):
                items.append(txt(ligne))
            return sortie
        if lg is None and ld is None and vg == vd:
            items.append(_repli(Pt(borne, 0), vg, f"{dg} | {dd}"))
            return sortie
    for cle, pt, val, vt, _ in cas:
        if vt == "?":
            items.append(txt(rf"\(\displaystyle\lim_{{x\to {pt.tex()}}} f(x) = {NON_DETERMINEE_TEX}\)."))
        else:
            _narrer_limite(f, pt, val, vt, items)
    return sortie


def _fusion_cotes(gauche, droite, pg, pd, p0):
    """Lignes des deux côtés : si elles ne diffèrent que par le côté, elles sont écrites une fois (limite en a) ; sinon
    celles de gauche, puis celles de droite (chaque ligne porte son côté dans lim)."""
    def neutre(lignes, p):
        return [l.replace(rf"\lim_{{x\to {p.tex()}}}", rf"\lim_{{x\to {p0.tex()}}}") for l in lignes]
    ng, nd = neutre(gauche, pg), neutre(droite, pd)
    return ng if ng == nd else list(gauche) + list(droite)


def _etude_transcendante(f, borne, items):
    if borne["type"] == "inf":
        cote = None
    else:
        point, cote = borne["point"], borne["cote"]
    if cote != "deux":
        pt = Pt(borne, {"gauche": -1, "droite": 1}.get(cote, 0))
        val = _limite_sympy(f, pt.cible(), pt.direction())
        vtex, inf, _, vval = _valeur_tex(val)
        if vtex == "?":
            items.append(txt("La limite n'a pas pu être déterminée automatiquement : on ne conclut pas sur une éventuelle asymptote."))
            return vtex, False, None, None
        _narrer_limite(f, pt, val, vtex, items)
        extra = None
        if borne["type"] == "inf":
            if inf:
                extra = _oblique_generale(f, borne["signe"], items)
            else:
                items.append(txt(rf"Asymptote horizontale : \(y = {vtex}\)."))
        elif inf:
            items.append(txt(rf"Asymptote verticale : \(x = {point.tex}\)."))
        else:
            items.append(txt(_phrase_trou(point.tex, vtex)))
        return vtex, inf, extra, vval

    def ref_de(pt):
        val = _limite_sympy(f, pt.cible(), pt.direction())
        vt, _, _, vv = _valeur_tex(val)
        return val, vt, vv

    (vg, vg_val), (vd, vd_val) = _narrer_cotes(f, borne, items, ref_de)
    return (vg, vd), False, None, (vg_val, vd_val)


def _bilan_deux_cotes(point, cote_tex, val, vval, items):
    """Valeur interdite isolée (cas transcendant) : on ne conclut à une asymptote
    verticale que si l'une des deux limites latérales est infinie."""
    (vg, vd), (vg_val, vd_val) = val, vval
    base = {"point_tex": point.tex, "point_val": point.val, "ou": cote_tex}
    inf_g, inf_d = r"\infty" in vg, r"\infty" in vd
    if inf_g or inf_d:
        if inf_g and inf_d:
            conclusion = rf"Asymptote verticale : \(x = {point.tex}\)."
        else:
            cote, autre, v_autre = ("droit", "gauche", vg) if inf_d else ("gauche", "droite", vd)
            conclusion = (rf"Asymptote verticale : \(x = {point.tex}\) (du côté {cote}) ; "
                          rf"à {autre}, \(f(x) \to {_affichable(v_autre)}\).")
        items.append(txt(conclusion))
        return dict(base, genre="verticale", gauche_tex=_affichable(vg), droite_tex=_affichable(vd),
                    gauche_val=vg_val, droite_val=vd_val)
    if "?" in (vg, vd):
        items.append(txt("Ces limites n'ont pas pu être déterminées automatiquement : "
                         "on ne conclut pas sur une éventuelle asymptote."))
        return None
    if vg == vd or (vg_val is not None and vd_val is not None and proche(vg_val, vd_val)):
        items.append(txt(_phrase_trou(point.tex, vg)))
        return dict(base, genre="trou", valeur_tex=vg, valeur_val=vg_val)
    items.append(txt("Limites à gauche et à droite différentes : f n'a pas de limite en "
                     rf"\(x={point.tex}\) ; pas d'asymptote verticale."))
    return dict(base, genre="sans_limite", gauche_tex=vg, droite_tex=vd, gauche_val=vg_val, droite_val=vd_val)


# =====================================================================
# Point d'entrée
# =====================================================================
def _valeurs_pole(asym, cote):
    """Limites latérales (gauche/droite, selon `cote`) d'une étude rationnelle en un point fini :
    trou = même valeur des deux côtés, pôle = signe de chaque côté, étude sans conclusion = « ? »."""
    cotes = ("gauche", "droite") if cote == "deux" else (cote,)
    if asym is None:
        return {c: "?" for c in cotes}
    if asym["genre"] == "trou":
        return {c: asym["valeur_tex"] for c in cotes}
    return {c: asym[c + "_tex"] for c in cotes}


def etudier(entree, avec_bornes=False):
    try:
        f = lire(entree)
    except ErreurSaisie as e:
        return {"ok": False, "erreur": str(e)}

    res_ed, _, ED = analyser_complet(entree)
    if not res_ed.get("ok"):
        return {"ok": False, "erreur": res_ed["erreur"]}
    if not res_ed.get("complet"):
        return {"ok": False, "erreur": "L'ensemble de définition n'a pas pu être calculé pour cette fonction."}

    TABLEAUX.reset()
    res = ajouter_saisie({"ok": True, "f_tex": tex(f), "ed_tex": res_ed["ED_tex"], "etudes": [], "asymptotes": []}, f)
    bornes_val = []

    try:
        dec = decomposer(f)
        rationnelle = (dec[0] == "x")
    except NonPrisEnCharge:
        rationnelle = False
    if rationnelle:
        N, D = r_norm(dec[1])

    vues = {}                                   # divisions euclidiennes déjà écrites (−∞ puis +∞)
    for borne in _bornes(ED):
        items = []
        if borne["type"] == "inf":
            cote_tex = r"x \to +\infty" if borne["signe"] > 0 else r"x \to -\infty"
            if rationnelle:
                asym = _etude_rationnelle_infini(f, N, D, borne["signe"], items, vues)
                asym["ou"] = cote_tex
                res["asymptotes"].append(asym)
                val_borne = asym["valeur_tex"]
            else:
                val_tex, inf, extra, vval = _etude_transcendante(f, borne, items)
                val_borne = val_tex
                if val_tex == "?":
                    pass  # limite non déterminée : jamais une asymptote
                elif inf is False:
                    res["asymptotes"].append({"genre": "horizontale", "ou": cote_tex,
                                               "valeur_tex": val_tex, "valeur_val": vval})
                elif extra is not None:
                    extra["ou"] = cote_tex
                    res["asymptotes"].append(extra)
        else:
            point, cote = borne["point"], borne["cote"]
            if cote == "deux":
                cote_tex = rf"x \to {point.tex}"
            else:
                cote_tex = rf"x \to {point.tex}^{'-' if cote=='gauche' else '+'}"
            if rationnelle:
                asym = _etude_rationnelle_pole(f, N, D, point, cote, items)
                if asym is not None:
                    asym["ou"] = cote_tex
                    res["asymptotes"].append(asym)
                val_borne = _valeurs_pole(asym, cote)
            else:
                val, inf, _, vval = _etude_transcendante(f, borne, items)
                val_borne = val if cote == "deux" else {cote: val}
                if cote == "deux":
                    asym = _bilan_deux_cotes(point, cote_tex, val, vval, items)
                else:
                    est_asymptote = r"\infty" in val
                    asym = None if val == "?" else {
                        "genre": "verticale" if est_asymptote else "trou",
                        "point_tex": point.tex, "point_val": point.val, "ou": cote_tex,
                        (cote + "_tex"): val}
                    if asym is not None and not est_asymptote:
                        asym["valeur_tex"] = val
                        asym["valeur_val"] = vval
                if asym is not None:
                    res["asymptotes"].append(asym)

        # Valeurs de cette borne, reprises telles quelles par le tableau de variations de l'Étude complète
        # (T06c) : une seule source de calcul, jamais un second calcul indépendant. « ? » : non déterminée.
        if borne["type"] == "inf":
            bornes_val.append({"type": "inf", "signe": borne["signe"], "tex": val_borne})
        else:
            cotes = {"gauche": val_borne[0], "droite": val_borne[1]} if isinstance(val_borne, tuple) else val_borne
            bornes_val.append({"type": "fini", "point_tex": point.tex, "point_val": point.val,
                               "gauche": cotes.get("gauche"), "droite": cotes.get("droite")})

        res["etudes"].append({"ou": cote_tex, "etapes": items})

    res["tableaux_signe"] = TABLEAUX.items()
    if avec_bornes:       # réservé à l'Étude complète : la sortie de l'outil Limites reste inchangée
        res["limites_bornes"] = bornes_val
    return res


def etudier_json(entree):
    return json_strict(etudier(entree))


if __name__ == "__main__":
    import sys
    for arg in sys.argv[1:] or ["(x^2-1)/(x-3)"]:
        print(json.dumps(etudier(arg), ensure_ascii=False, indent=2))
        print("=" * 60)
