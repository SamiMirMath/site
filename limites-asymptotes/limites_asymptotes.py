"""
limites_asymptotes.py — Limites aux bornes de l'ED et asymptotes.

Réutilise ensemble_def.py (parseur, arbre, ED, système de polynômes exacts, pont
SymPy). Ne dépend pas de derivee_variations.py : les asymptotes portent sur f,
pas sur f'.

Méthode (décidée avec l'enseignant) :
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
from fractions import Fraction as F

from ensemble_def import (
    Nb, X, E, Neg, Op, Fn,
    lire, tex, prec, valeur_constante, Num, Iv, REELS, fusion, inter, ens_tex,
    contient, proche, evaluer, sans_x, qtex, ptex, pn, deg, peval, pdivlin, pmul, nul,
    decomposer, r_norm, json_strict, ajouter_saisie,
    _sympy, en_sympy_reel, arbre_depuis_sympy, num_sympy, _SP,
    txt, NonPrisEnCharge, ErreurSaisie, _analyser, apercu_json,
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
    sp = _sympy()
    return sp.sympify(num.py, locals={"sqrt": sp.sqrt, "exp": sp.exp, "log": sp.log, "pi": sp.pi})


def _limite_sympy(f, point, direction=None):
    """point : sp.oo, -sp.oo, ou objet SymPy exact. direction : '+', '-' ou None."""
    sp = _sympy()
    if sp is None:
        return None
    try:
        fe = en_sympy_reel(f)
        r = sp.limit(fe, _SP["x"], point, dir=direction) if direction else sp.limit(fe, _SP["x"], point)
    except Exception:
        return None
    if r.has(sp.oo, -sp.oo, sp.zoo, sp.nan) and r not in (sp.oo, -sp.oo):
        return None   # infini « complexe » (oo*(-1)**(2/3)…) : on ne conclut pas (ne devrait plus arriver, cf. en_sympy_reel)
    return r


def _valeur_tex(res_sympy):
    """Valeur SymPy (finie, +oo, -oo, ou autre) → (texte tex, est_infinie, est_plus, valeur_num)."""
    sp = _sympy()
    if res_sympy is None:
        return "?", False, None, None
    if res_sympy == sp.oo:
        return r"+\infty", True, True, None
    if res_sympy == -sp.oo:
        return r"-\infty", True, False, None
    try:
        n = num_sympy(res_sympy)
        return n.tex, False, None, n.val
    except Exception:
        return sp.latex(res_sympy), False, None, None


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


def _phrases_polynome_infini(P, s, n_tex):
    """Somme de plusieurs termes en s∞ : limite de chaque terme, puis règle de la somme ; si deux termes
    divergent en sens contraire (∞ − ∞), mise en évidence du terme de plus haut degré.
    Renvoie (phrases, Lim)."""
    vers = r"+\infty" if s > 0 else r"-\infty"
    ks = _polynome_a_termes(P)
    non_const = [k for k in ks if k >= 1]
    parts = [rf"\({_terme_signe_tex(P, k)} \to {Lim.infini(_signe(P[k]) * (s if k % 2 else 1)).tex()}\)"
             for k in non_const]
    if 0 in ks:
        parts.append(rf"\({qtex(P[0])}\) est une constante")
    enum = _enumerer(parts)
    signes = {_signe(P[k]) * (s if k % 2 else 1) for k in non_const}
    n = deg(P)
    tete_lim = Lim.infini(_signe(P[n]) * (s if n % 2 else 1))
    if len(signes) == 1:
        return [enum + rf" : la somme tend vers \({tete_lim.tex()}\)."], tete_lim
    tete, interieur, complet, termes = _facteur_detaille(P, n)
    nuls = _enumerer([rf"\({t} \to 0\)" for _, t in termes])
    phrases = [
        enum + r" : forme indéterminée « \(\infty - \infty\) ».",
        rf"On met en évidence le terme de plus haut degré : \({n_tex} = {complet}\).",
        rf"Quand \(x \to {vers}\), {nuls}, donc \({interieur} \to 1\).",
        rf"Comme \({tete} \to {tete_lim.tex()}\) et que le facteur entre parenthèses tend vers 1, "
        rf"\({n_tex} \to {tete_lim.tex()}\).",
    ]
    return phrases, tete_lim


def _phrases_fraction_infini(N, D, s, n_tex):
    """Quotient de deux polynômes (D non constant) en s∞. Renvoie (phrases, Lim)."""
    vers = r"+\infty" if s > 0 else r"-\infty"
    n, m = deg(N), deg(D)
    LD = _limite_polynome_infini(D, s)
    if n == 0:
        c = N[0]
        lim = Lim.fin(0, _signe(c) * LD.inf)
        return [rf"Le numérateur est la constante \({qtex(c)}\) et le dénominateur tend vers \({LD.tex()}\) "
                rf"(limite de son terme de plus haut degré) : le quotient tend vers \(0\)."], lim
    LN = _limite_polynome_infini(N, s)
    an, bm = N[n], D[m]
    ratio = an / bm
    teteN, intN, Nf, termesN = _facteur_detaille(N, n)
    teteD, intD, Df, termesD = _facteur_detaille(D, m)
    phrases = [rf"Le numérateur tend vers \({LN.tex()}\) et le dénominateur tend vers \({LD.tex()}\) "
               r"(limite de leur terme de plus haut degré) : forme indéterminée « \(\infty/\infty\) »."]
    equations = []
    if intN != "1":
        equations.append(rf"\({ptex(N, 'x')} = {Nf}\)")
    if intD != "1":
        equations.append(rf"\({ptex(D, 'x')} = {Df}\)")
    if equations:
        phrases.append("On met en évidence le terme de plus haut degré : " + " et ".join(equations) + ".")
    tete = _terme_tex(ratio, n - m)
    tete_prod = "" if tete == "1" else tete + r" \cdot "
    if intN == "1" and intD == "1":
        phrases.append(rf"Donc \({n_tex} = \dfrac{{{Nf}}}{{{Df}}} = {tete}\).")
    else:
        phrases.append(rf"Donc \({n_tex} = \dfrac{{{Nf}}}{{{Df}}} = {tete_prod}\dfrac{{{intN}}}{{{intD}}}\).")
        nuls = []
        for _, t in termesN + termesD:
            if t not in nuls:
                nuls.append(t)
        liste = _enumerer([rf"\({t} \to 0\)" for t in nuls])
        phrases.append(rf"Quand \(x \to {vers}\), {liste} : le quotient "
                       rf"\(\dfrac{{{intN}}}{{{intD}}}\) tend vers 1.")
    k = n - m
    if k < 0:
        sgn = _signe(ratio) * (s if (-k) % 2 else 1)
        lim = Lim.fin(0, sgn)
        phrases.append(rf"Le quotient tend vers 1 et \({tete} \to 0\) : la limite est \(0\).")
    elif k == 0:
        lim = Lim.fin(ratio)
        phrases.append(rf"Le quotient tend vers 1 : la limite est \({qtex(ratio)}\) "
                       r"(rapport des coefficients dominants).")
    else:
        lim = Lim.infini(_signe(ratio) * (s if k % 2 else 1))
        phrases.append(rf"Le quotient tend vers 1 et \({tete} \to {lim.tex()}\) : la limite est \({lim.tex()}\).")
    return phrases, lim


def _etude_rationnelle_infini(f, N, D, signe, items):
    n, m = deg(N), deg(D)
    an, bm = N[-1], D[-1]
    ratio = an / bm
    vers = r"+\infty" if signe > 0 else r"-\infty"
    k = n - m
    k_signe_xk = signe if k % 2 else 1
    if n < m:
        ref, vtex = _sympy().Integer(0), "0"
        res = {"genre": "horizontale", "valeur_tex": "0", "valeur_val": 0.0}
    elif n == m:
        ref, vtex = _sympy().Rational(ratio.numerator, ratio.denominator), qtex(ratio)
        res = {"genre": "horizontale", "valeur_tex": vtex, "valeur_val": float(ratio)}
    else:
        signe_final = 1 if (ratio > 0) == (k_signe_xk > 0) else -1
        val_tex = r"+\infty" if signe_final > 0 else r"-\infty"
        ref, vtex = (_sympy().oo if signe_final > 0 else -_sympy().oo), val_tex
        res = None
    pt = Pt({"type": "inf", "signe": signe})
    # f est d'abord rédigée telle qu'elle est écrite ; si sa forme ne s'y prête pas (somme de fractions…),
    # on la ramène à une seule fraction N/D
    _narrer_limite(f, pt, ref, vtex, items,
                   alternative=(_arbre_fraction(N, D), r"On écrit \(f\) sous la forme d'une seule fraction : "
                                rf"\(f(x) = {tex(_arbre_fraction(N, D))}\)."))
    if n <= m:
        items.append(txt(rf"Asymptote horizontale d'équation \(y = {vtex}\)."))
        return res
    items.append(txt("La limite est infinie : pas d'asymptote horizontale."))
    if k == 1:
        Q, R = _pdiv(N, D)
        if deg(D) == 0:
            items.append(txt(rf"Le polynôme est de degré 1 : sa courbe est la droite d'équation "
                             rf"\(y = {ptex(Q,'x')}\), qui est son propre asymptote oblique."))
        else:
            debut = (r"Le degré du numérateur dépasse celui du dénominateur de 1 : il y a une asymptote oblique. "
                     r"On effectue la division polynomiale du numérateur par le dénominateur, "
                     rf"\({ptex(N,'x')}\) par \({ptex(D,'x')}\) (voir le chapitre « Division polynomiale ») : ")
            if nul(R):
                items.append(txt(debut + rf"\({ptex(N,'x')} = \left({ptex(D,'x')}\right)\left({ptex(Q,'x')}\right)\), "
                                 rf"donc \(f(x) = {ptex(Q,'x')}\) là où f est définie : la courbe est contenue dans la droite."))
            else:
                items.append(txt(
                    debut + rf"\({ptex(N,'x')} = \left({ptex(D,'x')}\right)\left({ptex(Q,'x')}\right) + {ptex(R,'x')}\), "
                    rf"donc \(f(x) = {ptex(Q,'x')} + \dfrac{{{ptex(R,'x')}}}{{{ptex(D,'x')}}}\), "
                    r"et ce dernier terme tend vers 0."
                ))
        a = Q[1] if len(Q) > 1 else F(0)
        b = Q[0] if Q else F(0)
        return {"genre": "oblique", "a": qtex(a), "b": qtex(b), "a_val": float(a), "b_val": float(b),
                "equation_tex": ptex(Q, "x"), "valeur_tex": vtex}
    if deg(D) == 0:
        items.append(txt(rf"Le polynôme est de degré {n} \(\geq 2\) : pas d'asymptote oblique (branche parabolique)."))
    else:
        items.append(txt(
            rf"Le degré du numérateur dépasse celui du dénominateur de {k} \(\geq 2\) : "
            r"pas d'asymptote oblique (branche parabolique)."
        ))
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
        sp = _sympy()
        borne = {"type": "fini", "point": point, "cote": cote}
        items.append(txt(rf"\(x={point.tex}\) est une valeur interdite : on étudie la limite de \(f\) "
                         rf"quand \(x \to {point.tex}\)."))

        def ref_de(pt):
            v = res["gauche_tex" if pt.d < 0 else "droite_tex"]
            return (sp.oo if v == r"+\infty" else -sp.oo), v, None

        _narrer_cotes(f, borne, items, ref_de, cotes=tuple(c for c in ("gauche", "droite") if c + "_tex" in res))
        items.append(txt(rf"Asymptote verticale d'équation \(x = {point.tex}\)."))
        return res
    items.append(txt(rf"Le numérateur s'annule aussi en \(x={point.tex}\) : forme indéterminée "
                     r"\(0/0\). On factorise et on simplifie avant de passer à la limite."))
    val = _limite_sympy(f, _sympify_point(point))
    vtex, _, _, vval = _valeur_tex(val)
    if vtex == "?":
        items.append(txt("La limite n'a pas pu être déterminée automatiquement : on ne conclut pas sur une éventuelle asymptote."))
        return None
    items.append(txt(rf"\(\displaystyle\lim_{{x\to {point.tex}}} f(x) = {vtex}\) : "
                     + _phrase_trou(point.tex, vtex)))
    return {"genre": "trou", "point_tex": point.tex, "point_val": a, "valeur_tex": vtex, "valeur_val": vval}


NON_DETERMINEE_TEX = r"\text{limite non déterminée automatiquement}"


def _affichable(v):
    """« ? » est le marqueur interne d'une limite que SymPy n'a pas donnée."""
    return NON_DETERMINEE_TEX if v == "?" else v


def _phrase_trou(point_tex, valeur_tex):
    """Formulation Q7 : valeur interdite où la limite (éventuellement latérale) est finie."""
    return (rf"f n'est pas définie en \(x={point_tex}\), mais sa limite y est finie "
            rf"(\(={valeur_tex}\)) : pas d'asymptote verticale, trou dans le graphique "
            rf"en \(({point_tex}\,;\,{valeur_tex})\).")


def _x_moins(a):
    """tex de (x - a), correctement signé : a peut être négatif."""
    if a == 0:
        return "x"
    return f"x-{qtex(a)}" if a > 0 else f"x+{qtex(-a)}"


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
    sp = _sympy()
    a = point.q
    xa = _x_moins(a)
    N2, multN = _facteur_racine(N, a)
    D2, multD = _facteur_racine(D, a)
    N2a, D2a = peval(N2, a), peval(D2, a)
    mult = min(multN, multD)
    diff = multN - multD
    borne = {"type": "fini", "point": point, "cote": cote}
    items.append(txt(rf"\(x={point.tex}\) est une valeur interdite : on étudie la limite de \(f\) "
                     rf"quand \(x \to {point.tex}\)."))
    g = f
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
        items.append(txt(rf"Le numérateur et le dénominateur tendent vers \(0\) quand \(x \to {point.tex}\) : "
                         r"forme indéterminée « \(0/0\) »."))
        items.append(txt(rf"On factorise le numérateur et le dénominateur par \(\left({xa}\right)\) et l'on simplifie "
                         rf"(pour \(x \neq {point.tex}\)) : "
                         rf"\(f(x) = \dfrac{{{num_chaine}}}{{{den_chaine}}} = {simplifie}\)."))
        g = _arbre_fraction(pmul(N2, _puissance_binome(a, max(diff, 0))),
                            pmul(D2, _puissance_binome(a, max(-diff, 0))))

    if diff >= 0:
        valeur = N2a / D2a if diff == 0 else F(0)
        vtex = qtex(valeur)
        _narrer_limite(g, Pt(borne), sp.Rational(valeur.numerator, valeur.denominator), vtex, items)
        items.append(txt(_phrase_trou(point.tex, vtex)))
        return {"genre": "trou", "point_tex": point.tex, "point_val": float(a),
                "valeur_tex": vtex, "valeur_val": float(valeur)}

    # pôle : signe du facteur (x − a)^k de chaque côté, signe de N2(a)/D2(a)
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
    items.append(txt(rf"Asymptote verticale d'équation \(x = {point.tex}\)."))
    return res


# =====================================================================
# Rédaction détaillée (Q9, étape 0) : algèbre des limites sur l'arbre.
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
    def __init__(self, nom, noeud=None):
        super().__init__(nom)
        self.nom, self.noeud = nom, noeud


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


class Lim:
    """Limite d'une expression en un point : infinie (inf = ±1) ou finie (val : nombre exact SymPy).
    ap = signe de (expression − limite) au voisinage du point (+1 : par valeurs supérieures, −1 :
    inférieures), 0 s'il est inconnu, None pour une constante exacte. montre : écrire ℓ⁺ / ℓ⁻ (x → a⁺)."""
    __slots__ = ("inf", "val", "ap", "montre")

    def __init__(self, inf=0, val=None, ap=0, montre=False):
        self.inf, self.val, self.ap, self.montre = inf, val, ap, montre

    @staticmethod
    def fin(val, ap=0, montre=False):
        return Lim(0, _sympy().sympify(val), ap, montre)

    @staticmethod
    def infini(s):
        return Lim(1 if s > 0 else -1)

    def nul(self):
        return self.inf == 0 and _est_nul(self.val)

    def tex(self):
        if self.inf:
            return r"+\infty" if self.inf > 0 else r"-\infty"
        if self.nul():
            return "0^{+}" if self.ap and self.ap > 0 else "0^{-}" if self.ap and self.ap < 0 else "0"
        n = num_sympy(self.val)
        if n.approx:
            raise Abandon("valeur sans écriture exacte")
        if self.montre and self.ap:
            return n.tex + ("^{+}" if self.ap > 0 else "^{-}")
        return n.tex


def _lim_depuis_sympy(r):
    sp = _sympy()
    if r == sp.oo:
        return Lim.infini(1)
    if r == -sp.oo:
        return Lim.infini(-1)
    if r.has(sp.oo, -sp.oo, sp.zoo, sp.nan) or r.is_finite is not True or r.is_real is False:
        raise Abandon(f"limite SymPy inexploitable : {r}")
    return Lim.fin(r)


def _meme_valeur(a, b):
    sp = _sympy()
    if a.inf or b.inf:
        return a.inf == b.inf
    return abs(sp.N(a.val - b.val, 30)) < sp.Float("1e-20")


class Pt:
    """Point d'étude : ±∞ ou valeur finie approchée par la droite (d = +1) ou par la gauche (d = −1)."""

    def __init__(self, borne, d=0):
        if borne["type"] == "inf":
            self.s, self.a, self.d, self.a_tex = borne["signe"], None, 0, None
        else:
            self.s, self.a, self.d = 0, _sympify_point(borne["point"]), d
            self.a_tex = borne["point"].tex

    def cible(self):
        sp = _sympy()
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
    sp = _sympy()
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
    sp = _sympy()
    if U.inf:
        return Lim.infini(1) if U.inf > 0 else Lim.fin(0, 1)
    return Lim.fin(sp.exp(U.val), U.ap)


def _ln_lim(U):
    sp = _sympy()
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


class _Contexte:
    """État d'une rédaction : point d'étude, phrases écrites, limites de référence (SymPy) déjà vues."""

    def __init__(self, pt, f, ref_f):
        self.pt, self.phrases, self.refs, self.ap_vus, self.dites = pt, [], {}, set(), set()
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
            sp = _sympy()
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

    def phrases_de(self, n, liste):
        cle = n.key()
        if cle not in self.dites:
            self.dites.add(cle)
            self.phrases.extend(liste)

    def phrase(self, n, s):
        """Une phrase par sous-expression : si n a déjà été commentée, on ne la répète pas."""
        cle = n.key()
        if cle not in self.dites:
            self.dites.add(cle)
            self.phrases.append(s)


def _const_sympy(n):
    return en_sympy_reel(n)


def _texl(t):
    return rf"\({t}\)"


def _phrase_operation(n, A, B, LA, LB, L):
    """Phrase d'une somme, différence, produit ou quotient dont on connaît les limites des deux termes."""
    ta, tb = tex(n.a), tex(n.b)
    ca, cb = sans_x(n.a), sans_x(n.b)
    if n.op == "*" and (ca or cb):
        c, u, Lu = (n.a, n.b, LB) if ca else (n.b, n.a, LA)
        if Lu.inf:
            signe = ">" if _signe(_const_sympy(c)) > 0 else "<"
            return (rf"Comme \({tex(u)} \to {Lu.tex()}\) et \({tex(c)} {signe} 0\), "
                    rf"on a \({tex(n)} \to {L.tex()}\).")
    if ca and not cb:
        debut = rf"\({ta}\) est une constante et \({tb} \to {LB.tex()}\)"
    elif cb and not ca:
        debut = rf"\({ta} \to {LA.tex()}\) et \({tb}\) est une constante"
    else:
        debut = rf"\({ta} \to {LA.tex()}\) et \({tb} \to {LB.tex()}\)"
    if n.op == "/" and LB.nul() and not LA.inf:
        fin = rf"\(\dfrac{{{LA.tex()}}}{{{LB.tex()}}} = {L.tex()}\)"
    else:
        mot = {"+": "la somme", "-": "la différence", "*": "le produit", "/": "le quotient"}[n.op]
        fin = rf"{mot} tend vers \({L.tex()}\)"
    return debut + " : " + fin + "."


def _phrase_fonction(n, g_tex, LU, L):
    if not LU.inf and not L.inf and not L.nul():
        return (rf"Par continuité de \({g_tex}\) en \({num_sympy(LU.val).tex}\), "
                rf"\({tex(n)} \to {L.tex()}\).")
    return rf"Or \({g_tex} \to {L.tex()}\) quand \(t \to {LU.tex()}\) : \({tex(n)} \to {L.tex()}\)."


def _binome(a):
    """tex de x − a (a rationnel)."""
    if a == 0:
        return "x"
    return f"x - {qtex(a)}" if a > 0 else f"x + {qtex(-a)}"


def _atome_subst(a):
    t = qtex(a)
    return r"\left(" + t + r"\right)" if (a < 0 or a.denominator != 1) else t


def _subst_tex(P, a):
    r"""P(a) écrit terme à terme : 3^{2} - 1, 2 \cdot 3 + 5…  (a rationnel)."""
    base = _atome_subst(a)
    termes = []
    for k in range(len(P) - 1, -1, -1):
        c = P[k]
        if c == 0:
            continue
        m = "" if k == 0 else (base if k == 1 else f"{base}^{{{k}}}")
        if k == 0:
            t = qtex(abs(c))
        elif abs(c) == 1:
            t = m
        else:
            t = qtex(abs(c)) + r" \cdot " + m
        termes.append(("-" if c < 0 else "+", t))
    if not termes:
        return "0"
    out = ("-" if termes[0][0] == "-" else "") + termes[0][1]
    for sg, t in termes[1:]:
        out += f" {sg} {t}"
    return out


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
    return _arbre_poly(N) if deg(D) == 0 and D[0] == 1 else Op("/", _arbre_poly(N), _arbre_poly(D))


def _poly_ou_const(n):
    """Coefficients d'un polynôme en x ou d'une constante rationnelle non nulle ; None sinon."""
    if sans_x(n):
        v = valeur_constante(n)
        return [F(v)] if v else None
    return _polynome_de(n)


def _noeud_polynome(n, ctx):
    """Polynôme en un point rationnel : la limite est la valeur P(a) (substitution) ; si P(a) = 0, le signe
    d'approche vient de la factorisation P = (x − a)^m Q(x). Renvoie None si n n'est pas un tel polynôme."""
    pt = ctx.pt
    if pt.s or not pt.a.is_Rational:
        return None
    P = _polynome_de(n)
    if P is None:
        return None
    a = F(int(pt.a.p), int(pt.a.q))
    v = peval(P, a)
    if v != 0 or not pt.d:         # (pt.d = 0 : limite des deux côtés, sans signe d'approche à donner)
        sub = _subst_tex(P, a)
        egal = rf"{sub} = {qtex(v)}" if sub != qtex(v) else sub
        ctx.phrase(n, rf"Par substitution, \({tex(n)} \to {egal}\).")
        L = Lim.fin(v)
        ctx.verifier(n, L, exact=True)
        return L
    Q, m = _facteur_racine(P, a)
    c = peval(Q, a)
    d = pt.d
    sg = _signe(c) * (d if m % 2 else 1)
    xa = _binome(a)
    sd = "-" if d < 0 else "+"
    zero = rf"0^{{{'+' if sg > 0 else '-'}}}"
    if m == 1 and deg(Q) == 0:
        cote = "<" if d < 0 else ">"
        fact = xa if c == 1 else (rf"-\left({xa}\right)" if c == -1 else rf"{qtex(c)}\left({xa}\right)")
        egal = "" if fact == tex(n) else rf"\({tex(n)} = {fact}\), "
        ctx.phrase(n, rf"Pour \(x {cote} {qtex(a)}\), " + egal
                   + rf"\({tex(n)} {'>' if sg > 0 else '<'} 0\) : \({tex(n)} \to {zero}\).")
    else:
        pa = xa if m == 1 else rf"\left({xa}\right)^{{{m}}}"
        pa_lim = rf"{'-' if (d < 0 and m % 2) else '+'}"
        if deg(Q) == 0:
            cq = "" if c == 1 else rf"{qtex(c)}\,"
            fact = cq + (rf"\left({xa}\right)" if m == 1 else pa)
            verbe = "" if c == 1 else rf"\({qtex(c)}\) est {'positif' if c > 0 else 'négatif'} et "
        else:
            q_tex = ptex(Q, "x")
            q_par = r"\left(" + q_tex + r"\right)" if (" + " in q_tex or " - " in q_tex) else q_tex
            pa_prod = rf"\left({xa}\right)" if m == 1 else pa
            fact = pa_prod + r"\," + q_par if a == 0 else q_par + r"\," + pa_prod
            if a == 0:
                fact = (xa if m == 1 else f"x^{{{m}}}") + r"\," + q_par
            verbe = rf"\({q_tex} \to {qtex(c)}\) et "
        if fact == tex(n) or (deg(Q) == 0 and c == 1 and pa == tex(n)):
            remarque = "" if m % 2 else (" (carré)" if m == 2 else " (puissance paire)")
            ctx.phrase(n, rf"Quand \(x \to {qtex(a)}^{{{sd}}}\), \({tex(n)} \to {zero}\){remarque}.")
        else:
            ctx.phrase(n, rf"\({tex(n)} = {fact}\) ; quand \(x \to {qtex(a)}^{{{sd}}}\), {verbe}"
                          rf"\({pa} \to 0^{{{pa_lim}}}\) : \({tex(n)} \to {zero}\).")
    L = Lim.fin(0, sg)
    ctx.verifier(n, L, exact=True)
    return L


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
        phrases, L = _phrases_polynome_infini(P, s, tex(n))
    elif isinstance(n, Op) and n.op == "/":
        A, B = _poly_ou_const(n.a), _poly_ou_const(n.b)
        if A is None or B is None or deg(B) < 1:
            return None
        phrases, L = _phrases_fraction_infini(A, B, s, tex(n))
    else:
        return None
    ctx.verifier(n, L, exact=True)
    ctx.phrases_de(n, phrases)
    return L


def _lever(n, ctx, fi):
    """Lève une forme indéterminée par une méthode du cours (mise en évidence, conjuguée, références…).
    Aucune n'est encore rédigée : Abandon, donc phrase de repli."""
    raise Abandon(f"forme indéterminée {fi.nom} non levée en {tex(n)}")


def _noeud(n, ctx):
    """Limite de n (arbre) au point d'étude, avec une phrase par opération ; Abandon si l'on ne peut
    pas la justifier."""
    sp = _sympy()
    if sans_x(n):
        return Lim.fin(_const_sympy(n), ap=None)
    if isinstance(n, X):
        return ctx.pt.lim_x()
    L = _noeud_polynome(n, ctx) if not ctx.pt.s else _noeud_rationnel_infini(n, ctx)
    if L is not None:
        return L
    try:
        if isinstance(n, Neg):
            LU = _noeud(n.a, ctx)
            L = _oppose(LU)
            ctx.verifier(n, L)
            ctx.phrase(n, rf"\({tex(n.a)} \to {LU.tex()}\), donc \({tex(n)} \to {L.tex()}\).")
            return L
        if isinstance(n, Op) and n.op in "+-*/":
            A, B = _noeud(n.a, ctx), _noeud(n.b, ctx)
            L = {"+": lambda: _somme(A, B), "-": lambda: _somme(A, _oppose(B)),
                 "*": lambda: _produit(A, B), "/": lambda: _quotient(A, B)}[n.op]()
            ctx.verifier(n, L)
            ctx.phrase(n, _phrase_operation(n, n.a, n.b, A, B, L))
            return L
        if isinstance(n, Op) and n.op == "^":
            alpha = valeur_constante(n.b)
            if alpha is None:
                raise Abandon("exposant non rationnel")
            U = _noeud(n.a, ctx)
            if alpha.denominator == 1:
                if alpha == 0 or abs(alpha) > 64 or alpha == 1:
                    raise Abandon("exposant 0, 1 ou trop grand")
                L = _puissance_entiere(U, int(alpha))
            else:
                L = _puissance_reelle(U, alpha)
            ctx.verifier(n, L)
            ctx.phrase(n, _phrase_fonction(n, rf"t^{{{qtex(alpha)}}}", U, L))
            return L
        if isinstance(n, Fn):
            U = _noeud(n.a, ctx)
            if n.nom == "exp":
                L, g = _exp_lim(U), r"e^{t}"
            elif n.nom == "ln":
                L, g = _ln_lim(U), r"\ln t"
            else:
                L, g = _puissance_reelle(U, F(1, 2)), r"\sqrt{t}"
            ctx.verifier(n, L)
            ctx.phrase(n, _phrase_fonction(n, g, U, L))
            return L
    except FormeIndeterminee as fi:
        fi.noeud = n
        return _lever(n, ctx, fi)
    raise Abandon(f"sous-expression non prise en charge : {tex(n)}")


def _rediger(f, pt, ref):
    """(phrases, None) si la limite de f en pt est rédigée et coïncide avec ref (valeur SymPy), sinon
    (None, raison technique)."""
    try:
        R = _lim_depuis_sympy(ref)
        ctx = _Contexte(pt, f, R)
        L = _noeud(f, ctx)
        if not _meme_valeur(L, R):
            raise Abandon(f"valeur rédigée {L.tex()} ≠ référence {R.tex()}")
        return ctx.phrases, None
    except Exception as e:      # rien ne doit faire échouer l'étude : on retombe sur le résultat seul
        return None, f"{type(e).__name__} : {e}"


def _narrer_limite(f, pt, ref, vtex, items, alternative=None):
    """Étapes de lim f en pt : rédigées si possible, sinon phrase de repli et résultat de référence.
    alternative = (arbre équivalent, phrase d'introduction) : essayée si f, telle qu'elle est écrite, résiste."""
    lim = rf"\displaystyle\lim_{{x\to {pt.tex()}}} f(x) = {vtex}"
    phrases, detail = _rediger(f, pt, ref)
    if phrases is None and alternative is not None:
        g, intro = alternative
        phrases2, detail2 = _rediger(g, pt, ref)
        if phrases2 is not None:
            phrases, detail = [intro] + phrases2, None
        else:
            detail = f"{detail} ; sous forme de fraction : {detail2}"
    if phrases is None:
        item = txt(PHRASE_REPLI + rf"\({lim}\).")
        item["detail"] = detail
        items.append(item)
    else:
        items.extend(txt(p) for p in phrases)
        items.append(txt(rf"Donc \({lim}\)."))


def _equation_affine(a_tex, b_tex, var="x"):
    """Combine a et b (déjà en tex) en « ax + b » proprement (signes, a=±1)."""
    partie_a = var if a_tex == "1" else ("-" + var if a_tex == "-1" else a_tex + var)
    if b_tex.startswith("-"):
        return partie_a + " - " + b_tex[1:]
    if b_tex == "0":
        return partie_a
    return partie_a + " + " + b_tex


def _oblique_generale(f, signe, items):
    """Cherche une asymptote oblique d'une fonction quelconque (pas seulement
    rationnelle) : a = lim f(x)/x, b = lim [f(x) - ax], via le calcul formel."""
    sp = _sympy()
    if sp is None:
        return None
    x = _SP["x"]
    cible = sp.oo if signe > 0 else -sp.oo
    try:
        fe = en_sympy_reel(f)
        a_val = sp.limit(fe / x, x, cible)
        if not a_val.is_finite or a_val == 0:
            return None
        b_val = sp.limit(fe - a_val * x, x, cible)
        if not b_val.is_finite:
            return None
    except Exception:
        return None
    a_tex, b_tex = num_sympy(a_val).tex, num_sympy(b_val).tex
    items.append(txt(
        rf"On compare \(f(x)\) à une droite : \(a = \displaystyle\lim \frac{{f(x)}}{{x}} = {a_tex}\) et "
        rf"\(b = \displaystyle\lim \left(f(x) - {a_tex}x\right) = {b_tex}\) sont finis (et \(a \neq 0\)) : "
        r"asymptote oblique."
    ))
    return {"genre": "oblique", "a": a_tex, "b": b_tex, "a_val": float(a_val), "b_val": float(b_val),
            "equation_tex": _equation_affine(a_tex, b_tex)}


def _narrer_cotes(f, borne, items, ref_de, cotes=("gauche", "droite")):
    """Limites à gauche et à droite d'une valeur interdite : un bloc par côté. ref_de(pt) donne la valeur
    de référence (SymPy ou exacte), son écriture tex et sa valeur numérique. Renvoie [(tex, valeur), …]."""
    sortie = []
    for cle, d in (("gauche", -1), ("droite", 1)):
        if cle not in cotes:
            continue
        pt = Pt(borne, d)
        val, vt, vv = ref_de(pt)
        items.append(txt(rf"Limite à {cle} (\(x \to {pt.tex()}\)) :"))
        if vt == "?":
            items.append(txt(rf"\(\displaystyle\lim_{{x\to {pt.tex()}}} f(x) = {NON_DETERMINEE_TEX}\)."))
        else:
            _narrer_limite(f, pt, val, vt, items)
        sortie.append((vt, vv))
    return sortie


def _etude_transcendante(f, borne, items):
    if borne["type"] == "inf":
        cote = None
    else:
        point, cote = borne["point"], borne["cote"]
        if cote == "deux":
            vers = point.tex
        else:
            vers = Pt(borne, {"gauche": -1, "droite": 1}[cote]).tex()
        items.append(txt(rf"\(x={point.tex}\) est une valeur interdite : on étudie la limite de \(f\) "
                         rf"quand \(x \to {vers}\)."))
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
                items.append(txt("La limite est infinie : pas d'asymptote horizontale."))
                extra = _oblique_generale(f, borne["signe"], items)
            else:
                items.append(txt(rf"Asymptote horizontale d'équation \(y = {vtex}\)."))
        elif inf:
            items.append(txt(rf"Asymptote verticale d'équation \(x = {point.tex}\)."))
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
    if r"\infty" in vg or r"\infty" in vd:
        items.append(txt(rf"Au moins une des deux limites est infinie : asymptote verticale d'équation \(x = {point.tex}\)."))
        return dict(base, genre="verticale", gauche_tex=_affichable(vg), droite_tex=_affichable(vd),
                    gauche_val=vg_val, droite_val=vd_val)
    if "?" in (vg, vd):
        items.append(txt("Ces limites n'ont pas pu être déterminées automatiquement : "
                         "on ne conclut pas sur une éventuelle asymptote."))
        return None
    if vg == vd or (vg_val is not None and vd_val is not None and proche(vg_val, vd_val)):
        items.append(txt(rf"Les deux limites sont finies et égales à \({vg}\) : "
                         + _phrase_trou(point.tex, vg)))
        return dict(base, genre="trou", valeur_tex=vg, valeur_val=vg_val)
    items.append(txt("Limites à gauche et à droite différentes : f n'a pas de limite en "
                     rf"\(x={point.tex}\) ; pas d'asymptote verticale."))
    return dict(base, genre="sans_limite", gauche_tex=vg, droite_tex=vd, gauche_val=vg_val, droite_val=vd_val)


# =====================================================================
# Point d'entrée
# =====================================================================
def etudier(entree):
    try:
        f = lire(entree)
    except ErreurSaisie as e:
        return {"ok": False, "erreur": str(e)}

    res_ed, _, ED = _analyser(entree)
    if not res_ed.get("ok"):
        return {"ok": False, "erreur": res_ed["erreur"]}
    if not res_ed.get("complet"):
        return {"ok": False, "erreur": "L'ensemble de définition n'a pas pu être calculé pour cette fonction."}

    res = ajouter_saisie({"ok": True, "f_tex": tex(f), "ed_tex": res_ed["ED_tex"], "etudes": [], "asymptotes": []}, f)

    try:
        dec = decomposer(f)
        rationnelle = (dec[0] == "x")
    except NonPrisEnCharge:
        rationnelle = False
    if rationnelle:
        N, D = r_norm(dec[1])

    for borne in _bornes(ED):
        items = []
        if borne["type"] == "inf":
            cote_tex = r"x \to +\infty" if borne["signe"] > 0 else r"x \to -\infty"
            if rationnelle:
                asym = _etude_rationnelle_infini(f, N, D, borne["signe"], items)
                asym["ou"] = cote_tex
                res["asymptotes"].append(asym)
            else:
                val_tex, inf, extra, vval = _etude_transcendante(f, borne, items)
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
            else:
                val, inf, _, vval = _etude_transcendante(f, borne, items)
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

        res["etudes"].append({"ou": cote_tex, "etapes": items})

    return res


def etudier_json(entree):
    return json_strict(etudier(entree))


if __name__ == "__main__":
    import sys
    for arg in sys.argv[1:] or ["(x^2-1)/(x-3)"]:
        print(json.dumps(etudier(arg), ensure_ascii=False, indent=2))
        print("=" * 60)
