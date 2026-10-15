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
    contient, proche, evaluer, sans_x, qtex, ptex, pn, deg, peval, pdivlin, pmul, nul, padd, pscal,
    decomposer, r_norm, json_strict, ajouter_saisie,
    _sympy, en_sympy_reel, arbre_depuis_sympy, num_sympy, _SP,
    txt, NonPrisEnCharge, ErreurSaisie, _analyser, apercu_json,
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


def _phrases_polynome_infini(P, s, n, ctx):
    """Somme de plusieurs termes en s∞ : limite de chaque terme, puis règle de la somme ; si deux termes
    divergent en sens contraire (∞ − ∞), chaîne d'égalités avec mise en évidence du terme de plus haut degré.
    Renvoie (lignes, Lim)."""
    n_tex = tex(n)
    ks = _polynome_a_termes(P)
    non_const = [k for k in ks if k >= 1]
    parts = [rf"\({_terme_signe_tex(P, k)} \to {Lim.infini(_signe(P[k]) * (s if k % 2 else 1)).tex()}\)"
             for k in non_const]
    enum = _enumerer(parts)
    signes = {_signe(P[k]) * (s if k % 2 else 1) for k in non_const}
    deg_ = deg(P)
    tete_lim = Lim.infini(_signe(P[deg_]) * (s if deg_ % 2 else 1))
    if len(signes) == 1:
        return [enum + rf", donc \({n_tex} \to {tete_lim.tex()}\)."], tete_lim
    A = _membre_en_evidence(n, s)
    g = A["evid"]
    ch = ctx.chaine(n)
    ch.lim(tex(g), rf"\text{{on met }} {tex(_tete_tex(A['coef'], A['k']))} \text{{ en évidence}}", g)
    avant = _conclure(ch, g, tete_lim, ctx)
    if ch.complete and n is ctx.f:
        ctx.racine_dite = True
    return [enum + r" : forme indéterminée « \(\infty - \infty\) »."] + avant + [ch], tete_lim


def _phrases_fraction_infini(N, D, s, n_tex):
    """Quotient de deux polynômes (D non constant) en s∞. Renvoie (phrases, Lim)."""
    vers = r"+\infty" if s > 0 else r"-\infty"
    n, m = deg(N), deg(D)
    LD = _limite_polynome_infini(D, s)
    if n == 0:
        c = N[0]
        lim = Lim.fin(0, _signe(c) * LD.inf)
        parenthese = "" if len(_polynome_a_termes(D)) == 1 else " (limite de son terme de plus haut degré)"
        return [rf"Le numérateur vaut \({qtex(c)}\) et le dénominateur \({ptex(D, 'x')}\) tend vers \({LD.tex()}\)"
                rf"{parenthese}, donc \({n_tex} \to 0\)."], lim
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


def _oblique_rationnelle(items, N, D, Q, R, s):
    """deg N = deg D + 1 : division euclidienne N = D·Q + R (sans « + 0 » ni « + - »), f(x) − (ax + b) = R/D → 0,
    puis position relative de la courbe et de la droite."""
    vers = r"+\infty" if s > 0 else r"-\infty"
    ntex, dtex, qtex_, rtex = ptex(N, "x"), ptex(D, "x"), ptex(Q, "x"), ptex(R, "x")
    items.append(txt(r"Le degré du numérateur dépasse celui du dénominateur de 1 : il y a une asymptote oblique. "
                     r"On effectue la division euclidienne de \(" + ntex + r"\) par \(" + dtex + r"\) :"))
    produit = rf"{_facteur_poly(D)}\,{_facteur_poly(Q)}"
    if nul(R):
        items.append(txt(rf"\[{ntex} = {produit}\]"))
        items.append(txt(rf"Donc \(f(x) = {qtex_}\) là où f est définie : la courbe est contenue dans la droite "
                         rf"\(y = {qtex_}\)."))
        return
    items.append(txt(rf"\[{ntex} = {produit}{_suite_signee(R)}\]"))
    items.append(txt(rf"Donc \(f(x) = {qtex_}{_fraction_signee(R, D)}\), d'où :"))
    reste = rf"\dfrac{{{rtex}}}{{{dtex}}}"
    pt = Pt({"type": "inf", "signe": s})
    ch = Chaine(pt, rf"f(x) - {_facteur_poly(Q)}", Op("+", X(), X()))
    ch.lim(reste, rf"f(x) - {_facteur_poly(Q)} = {reste}")
    ch.val("0", r"\text{le degré du numérateur est inférieur à celui du dénominateur}"
           if deg(R) >= 1 else rf"\text{{numérateur constant, dénominateur }} \to {vers}")
    ch.complete = True
    items.append(txt(ch.html()))
    items.append(txt(rf"Asymptote oblique d'équation \(y = {qtex_}\)."))
    # position relative : signe de R/D près de s∞
    sr, sd = _signe_en_infini(R, s), _signe_en_infini(D, s)
    sg = sr * sd
    items.append(txt(
        rf"Position relative, près de \({vers}\) : \({rtex}\) est {_mot_signe(sr)} et \({dtex}\) est {_mot_signe(sd)}, "
        rf"donc \(f(x) - {_facteur_poly(Q)}\) est {_mot_signe(sg)} : la courbe est "
        + ("au-dessus" if sg > 0 else "au-dessous") + " de la droite."))


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
            _oblique_rationnelle(items, N, D, Q, R, signe)
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
        items.append(txt(rf"\(x = {point.tex}\) est une valeur interdite."))

        def ref_de(pt):
            v = res["gauche_tex" if pt.d < 0 else "droite_tex"]
            return (sp.oo if v == r"+\infty" else -sp.oo), v, None

        _narrer_cotes(f, borne, items, ref_de, cotes=tuple(c for c in ("gauche", "droite") if c + "_tex" in res))
        items.append(txt(rf"Asymptote verticale d'équation \(x = {point.tex}\)."))
        return res
    items.append(txt(rf"\(x = {point.tex}\) est une valeur interdite."))
    items.append(txt(rf"Le numérateur et le dénominateur tendent vers \(0\) quand \(x \to {point.tex}\) : "
                     r"forme indéterminée « \(0/0\) »."))
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
    items.append(txt(rf"\(x = {point.tex}\) est une valeur interdite."))
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
        items.append(txt(rf"Le numérateur et le dénominateur tendent vers \(0\) quand \(x \to {point.tex}\) : "
                         r"forme indéterminée « \(0/0\) »."))
        g = _arbre_fraction(pmul(N2, _puissance_binome(a, max(diff, 0))),
                            pmul(D2, _puissance_binome(a, max(-diff, 0))))
        chaine0 = Chaine(Pt(borne), "f(x)")
        chaine0.lim(rf"\dfrac{{{num_chaine}}}{{{den_chaine}}}", rf"\text{{on factorise par }} \left({xa}\right)")
        chaine0.lim(simplifie, rf"\text{{on simplifie}} \; (x \neq {point.tex})", g)

    if diff >= 0:
        valeur = N2a / D2a if diff == 0 else F(0)
        vtex = qtex(valeur)
        Ng, Dg = pmul(N2, _puissance_binome(a, max(diff, 0))), pmul(D2, _puissance_binome(a, 0))
        pt0 = Pt(borne)
        sub = _tex_en(g, pt0)
        if peval(Ng, a) / peval(Dg, a) == valeur:
            if chaine0 is not None:
                chaine0.val(sub)
                chaine0.val(vtex, force=sub == vtex)
                items.append(txt(chaine0.html()))
            else:
                egal = vtex if sub == vtex else rf"{sub} = {vtex}"
                g_tex = tex(g) if isinstance(g, Op) and g.op in "*/" else r"\left(" + tex(g) + r"\right)"
                items.append(txt(rf"Donc \(\displaystyle\lim_{{x\to {point.tex}}} f(x) = "
                                 rf"\lim_{{x\to {point.tex}}} {g_tex} = {egal}\)."))
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
        self.deux = borne.get("cote") == "deux"      # valeur interdite étudiée des deux côtés
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
        avant, tab, hach = [], None, []
        for i in items:
            if i.get("type") == "tableau":
                lignes = i["rows"]
                if len(lignes) == 2 and lignes[0]["cells"] == lignes[1]["cells"]:
                    i = dict(i, rows=[lignes[1]])          # un seul facteur : la ligne du facteur répète celle du produit
                tab = i
            elif str(i.get("html", "")).startswith("Les zones hachurées"):
                hach.append(i)
            elif not str(i.get("html", "")).startswith("On lit"):
                avant.append(i)                            # phrases des facteurs de signe évident
        # tous les facteurs sont évidents : pas de tableau, la lecture renvoie à la phrase qui les justifie
        self.sans_tableau = tab is None
        self.phrase = avant[0]["html"].rstrip(".") if avant else None
        self.items = [] if tab is None else [txt(titre)] + avant + [tab] + hach

    def renvoi(self):
        """« cf. tableau de signes de A », ou la phrase d'évidence quand il n'y a pas de tableau."""
        if self.sans_tableau and self.phrase:
            return self.phrase
        return rf"cf. tableau de signes de \({tex(self.A)}\)"

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
    sp = _sympy()
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
    """État d'une rédaction : point d'étude, limites de référence (SymPy) déjà vues, signes déjà justifiés.
    mode : "limite" (conclusion « lim f(x) = … »), "fleche" (une des deux lignes à gauche / à droite)."""

    def __init__(self, pt, f, ref_f, mode="limite", label="f(x)", label_somme=False):
        self.pt, self.f, self.mode = pt, f, mode
        self.label, self.label_somme = label, label_somme           # ce dont on prend la limite : f(x), f(x)/x, f(x) - x…
        self.refs, self.ap_vus, self.justifies = {}, set(), set()
        self.racine_dite = False
        self.demandes = []
        self.renvois = {}
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
        self.renvois[(genre, n.key())] = t.renvoi()
        return s

    def chaine(self, n):
        """Chaîne d'égalités pour la limite de n (« lim f(x) = … » pour f elle-même)."""
        if n is self.f:
            return Chaine(self.pt, self.label, Op("+", X(), X()) if self.label_somme else None)
        return Chaine(self.pt, tex(n), n)

    def cote(self):
        mot = "À gauche" if self.pt.d < 0 else "À droite"
        return rf"{mot} de \({self.pt.a_tex}\)"

    # --- écriture -------------------------------------------------------------
    def dire(self, n, L):
        """(« n → L » en tex, lignes de justification). Pour f elle-même : la conclusion du mode
        (« lim f(x) = L » ou « f(x) → L »). Un zéro de signe connu est toujours justifié."""
        pre = []
        if L.nul() and L.ap and not isinstance(n, X) and n is not self.f:
            try:
                pre = self.justifier(n, L)
            except Abandon:
                L = Lim.fin(0, 0)           # le signe n'est pas justifiable : on ne l'affirme pas
        if n is self.f:
            self.racine_dite = True
            if self.mode == "limite":
                return rf"\(\displaystyle\lim_{{x\to {self.pt.tex()}}} {self.label} = {L.tex(False)}\)", pre
            return rf"\({self.label} \to {L.tex(False)}\)", pre
        return rf"\({tex(n)} \to {L.tex()}\)", pre

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
        sp = _sympy()
        if deg(P) != 2:
            return None
        x = _SP["x"]
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
        sp = _sympy()
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
        valeur = en_sympy_reel(F_).subs(_SP["x"], pt.a)
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
        phrases, L = _phrases_polynome_infini(P, s, n, ctx)
    elif isinstance(n, Op) and n.op == "/":
        A, B = _poly_ou_const(n.a), _poly_ou_const(n.b)
        if A is None or B is None or deg(B) < 1:
            return None
        if deg(A) == 0:
            phrases, L = _phrases_fraction_infini(A, B, s, tex(n))
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


def _ligne_fi(n, fi, ctx=None):
    """« Le numérateur tend vers … et le dénominateur tend vers … : forme indéterminée « ∞/∞ ». »"""
    nom = rf"« \({FI_TEX[fi.nom]}\) »"

    def lim(noeud, L):
        evident = isinstance(noeud, X) or (isinstance(noeud, Fn) and noeud.nom == "exp")
        deux_cotes = ctx is not None and ctx.pt.deux and not ctx.pt.s        # le signe dépend du côté : pas de ligne propre à un côté
        return L.tex(bool(evident and L.nul() and L.ap and not deux_cotes))

    a, b = lim(n.a, fi.A), lim(n.b, fi.B)
    if isinstance(n, Op) and n.op == "/":
        return (rf"Le numérateur \({tex(n.a)}\) tend vers \({a}\) et le dénominateur "
                rf"\({tex(n.b)}\) tend vers \({b}\) : forme indéterminée {nom}.")
    return rf"\({tex(n.a)} \to {a}\) et \({tex(n.b)} \to {b}\) : forme indéterminée {nom}."


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


METHODES = []          # méthodes du cours, dans l'ordre : chacune renvoie (Lim, lignes) ou None si elle ne s'applique pas


def _lever(n, ctx, fi):
    """Lève une forme indéterminée par la première méthode du cours qui s'applique (Q9) ; Abandon sinon."""
    if ctx.profondeur >= 4:
        raise Abandon("trop de réécritures successives")
    ctx.profondeur += 1
    try:
        for methode in METHODES:
            r = methode(n, ctx, fi)
            if r is not None:
                L, lignes = r
                ctx.verifier(n, L)
                return L, fi.la + fi.lb + lignes
    finally:
        ctx.profondeur -= 1
    raise Abandon(f"forme indéterminée {fi.nom} non levée en {tex(n)}")


# --- chaîne d'égalités : lim f(x) = lim … = … = valeur (une seule formule, justifications entre parenthèses) ----
class Chaine:
    """Pas d'un calcul de limite écrits comme au tableau :
        lim f(x) = lim A         (justification)
                 = lim B         (justification)
                 = valeur.
    pas = [(genre, tex, justification, arbre)] ; genre « lim » (nouvelle ligne) ou « val » (même ligne, après « = »)."""

    def __init__(self, pt, debut, arbre=None):
        self.pt = pt
        self.pas = [("lim", debut, None, arbre)]
        self.complete = False                      # la dernière égalité est la valeur de la limite

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
        return self

    def html(self):
        lim = rf"\lim_{{x\to {self.pt.tex()}}}"

        def arg(tex_, arbre):
            somme = isinstance(arbre, Op) and arbre.op in "+-" or (isinstance(arbre, Neg) and isinstance(arbre.a, Op)
                                                                   and arbre.a.op in "+-")
            return rf"\left({tex_}\right)" if somme else tex_
        groupes = []                                # [[tex, [justifications]]]
        for genre, tex_, just, arbre in self.pas:
            if genre == "lim":
                groupes.append([f"{lim} {arg(tex_, arbre)}", []])
            else:
                groupes[-1][0] += f" = {tex_}"
            if just:
                groupes[-1][1].append(just)

        def ecrit(g):
            return g[0] + ((r" \qquad \left(" + r" \; ;\; ".join(g[1]) + r"\right)") if g[1] else "")
        if len(groupes) == 1:
            corps = ecrit(groupes[0])
        else:
            corps = r" \\ ".join([f"{groupes[0][0]} &= {ecrit(groupes[1])}"] + [f"&= {ecrit(g)}" for g in groupes[2:]])
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
    une forme indéterminée (fusion), sinon par les dernières égalités (g avec la limite de chaque morceau, puis la
    valeur). Renvoie les lignes à écrire autour : (avant la chaîne, après la chaîne)."""
    if _est_forme_indeterminee(g, ctx):
        idx = next((i for i in range(len(narration) - 1, -1, -1) if isinstance(narration[i], Chaine)), None)
        if idx is not None:
            ch.suite(narration[idx])
            return [l for l in narration[:idx]], [l for l in narration[idx + 1:]]
    avant = _conclure(ch, g, L, ctx)
    return avant, ([] if ch.complete else [l for l in narration])


def _tout_texte(lignes):
    """Les lignes d'une rédaction, la chaîne d'égalités (si présente) écrite en formule."""
    return [l.html() if isinstance(l, Chaine) else l for l in lignes]


def _petite(n):
    """True si n vaut c/x^j (j ≥ 1) : un infiniment petit en ±∞."""
    if not (isinstance(n, Op) and n.op == "/" and sans_x(n.a)):
        return False
    b = n.b
    while isinstance(b, Op) and b.op == "*" and sans_x(b.a):
        b = b.b
    return isinstance(b, X) or (isinstance(b, Op) and b.op == "^" and isinstance(b.a, X) and valeur_constante(b.b) is not None
                                and valeur_constante(b.b) > 0)


def _combine(op, A, B):
    """Limite de A op B (règles d'opérations) ; FormeIndeterminee si l'on ne peut pas conclure."""
    return {"+": lambda: _somme(A, B), "-": lambda: _somme(A, _oppose(B)),
            "*": lambda: _produit(A, B), "/": lambda: _quotient(A, B)}[op]()


def _avec_limites(n, ctx, notes, avant):
    """n écrit avec la limite de chaque morceau : c/x^j → 0 (terme nul supprimé d'une somme), x → ±∞, un morceau qui
    demandait une méthode (forme indéterminée) → sa valeur, sa chaîne écrite à part (avant). Renvoie (tex, infini ?)
    ou None si n n'est pas ainsi évaluable. notes : justifications « c/x^j → 0 »."""
    pt = ctx.pt

    def note(t):
        if t not in notes:
            notes.append(t)

    def par(t, infini):
        return rf"\left({t}\right)" if (infini or t.startswith("-") or t.startswith("+")) else t

    def feuille(m):
        Lm, lg = _noeud(m, ctx)
        avant.extend(lg)
        note(rf"{tex(m)} \to {Lm.tex(False)}")
        return Lm.tex(False), bool(Lm.inf)
    if sans_x(n):
        return tex(n), False
    if isinstance(n, X):
        return pt.lim_x().tex(), True
    if pt.s and _petite(n):
        note(rf"{tex(n)} \to 0")
        return "0", False
    if isinstance(n, Neg):
        r = _avec_limites(n.a, ctx, notes, avant)
        if r is None:
            return None
        t, inf = r
        return "-" + (rf"\left({t}\right)" if (" + " in t or " - " in t or inf) else t), inf
    if isinstance(n, Fn):
        r = _avec_limites(n.a, ctx, notes, avant)
        if r is None:
            return None
        t, inf = r
        if inf:                                       # e^{+∞}, ln(+∞) : on écrit la limite du morceau
            Lm, _ = _noeud(n, ctx)
            note(rf"{tex(n)} \to {Lm.tex(False)}")
            return Lm.tex(False), bool(Lm.inf)
        return {"sqrt": rf"\sqrt{{{t}}}", "ln": rf"\ln {t if t.lstrip('-').isdigit() else par(t, False)}",
                "exp": rf"e^{{{t}}}"}[n.nom], False
    if isinstance(n, Op) and n.op == "^" and valeur_constante(n.b) is not None:
        r = _avec_limites(n.a, ctx, notes, avant)
        if r is None:
            return None
        t, inf = r
        if inf:                                       # x^3 → +∞ : on écrit la limite du morceau
            Lm, _ = _noeud(n, ctx)
            return Lm.tex(False), bool(Lm.inf)
        return rf"{par(t, False) if (' ' in t or t.startswith('-')) else t}^{{{tex(n.b)}}}", False
    if isinstance(n, Op) and n.op in "+-*/":
        A, _ = _noeud(n.a, ctx)
        B, _ = _noeud(n.b, ctx)
        if n.op == "/" and B.nul() and not A.nul():
            return None
        try:
            _combine(n.op, A, B)
        except FormeIndeterminee:                     # ce morceau est une forme indéterminée : une méthode le lève
            return feuille(n)
        ra, rb = _avec_limites(n.a, ctx, notes, avant), _avec_limites(n.b, ctx, notes, avant)
        if ra is None or rb is None:
            return None
        (ta, ia), (tb, ib) = ra, rb
        if n.op in "+-":
            if tb == "0":
                return ta, ia
            if ta == "0":
                return ("-" + par(tb, False) if n.op == "-" else tb), ib
            return ta + (" + " if n.op == "+" else " - ") + (rf"\left({tb}\right)" if (ib or tb.startswith("-")) else tb), ia or ib
        if n.op == "*":
            return par(ta, ia) + r" \cdot " + par(tb, ib), ia or ib
        return rf"\dfrac{{{ta}}}{{{tb}}}", ia or ib
    return None


def _conclure(ch, g, L, ctx):
    """Dernières égalités de la chaîne ch pour la limite de g (de valeur L) : g avec la limite de chaque morceau, puis la
    valeur. Renvoie les lignes à écrire AVANT la chaîne (chaînes des morceaux déjà levés) ; ch.complete si la valeur est
    écrite."""
    pt = ctx.pt
    avant, notes = [], []
    if pt.s:
        r = _avec_limites(g, ctx, notes, avant)
        sub = r[0] if r is not None else None
    else:
        sub = _tex_en(g, pt) if _defini_en(g, ctx) else None
    if sub is None:
        return []
    just = (r" \; ;\; ".join(notes)) if notes else None
    v = L.tex(False)
    ch.val(sub, just)
    ch.val(v, force=ch.pas[-1][0] == "lim" and ch.pas[-1][1] == v)
    ch.complete = True
    return avant


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
    return _sympy().Rational(q.numerator, q.denominator)


def _dominant(n, s):
    """Terme dominant (c, k) de n en s∞ (n = c·x^k·(1 + …), c exact SymPy) ; None si n n'est pas de cette forme ou
    si les termes de plus haut degré d'une somme se compensent. √Q (Q de degré 2k, coefficient dominant q > 0) a
    pour terme dominant √q·|x|^k = √q·(s x)^k. Sert de garde-fou : la rédaction écrit sa propre mise en évidence."""
    sp = _sympy()
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


def _just_abs(s, m):
    """Justification de |x|^m = ±x^m selon le signe de x."""
    if s > 0:
        return rf"x > 0 \text{{ donc }} {_abs_tex(m)} = x" + ("" if m == 1 else f"^{{{m}}}")
    if m % 2:
        return rf"x < 0 \text{{ donc }} {_abs_tex(m)} = -x" + ("" if m == 1 else f"^{{{m}}}")
    return rf"x < 0 \text{{ et }} {m} \text{{ est pair, donc }} {_abs_tex(m)} = x^{{{m}}}"


def _racine_en_evidence(t, Q, s):
    """√Q (Q de degré 2m, coefficient dominant q > 0) en s∞ : √Q = √(x^{2m}(q + …)) = |x|^m√(q + …) = ±x^m√(q + …).
    Renvoie un dictionnaire : m ; stades t0, t1 (tex, sans signe) ; coef (±√q si q est un carré, sinon ±1) ; facteur
    (arbre de √(q + …), Nb(1) si le coefficient sort) ; eq (égalité de la mise en évidence, ou None)."""
    m = deg(Q) // 2
    interieur = _somme_termes([_terme_laurent(Q[j], j - 2 * m) for j in range(2 * m, -1, -1) if Q[j] != 0])
    absx = _abs_tex(m)
    seul = len(_polynome_a_termes(Q)) == 1
    q = Q[-1]
    racine_q = _sympy().sqrt(_rat(q))
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
        t = [(False, Nb(F(1)))] + [_terme_laurent(P[j] / c, j - k) for j in range(k - 1, -1, -1) if P[j] != 0]
        R = _somme_termes(t) if len(t) > 1 else Nb(F(1))
        evid = _produit_arbres([_tete_tex(c, k), R]) if not _est_un(R) else _tete_tex(c, k)
        eqs = [rf"{tex(M)} = {tex(evid)}"] if not _est_un(R) else []
        return {"coef": c, "k": k, "R": R, "evid": evid, "stades": [tex(evid)] * 4, "eqs": eqs, "absm": [],
                "somme": False}
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
    eqs = A["eqs"] + [e for e in B["eqs"] if e not in A["eqs"]]
    ch.lim(stades[0], r" ,\; ".join(eqs) if eqs else None)
    ms = sorted(set(A["absm"] + B["absm"]))
    if ms:
        ch.lim(stades[1], r"\sqrt{x^{2}} = |x|")
        ch.lim(stades[2], r" ,\; ".join(_just_abs(s, m) for m in ms))
    if stades[3] != stades[2]:
        ch.lim(stades[3], rf"\text{{on met }} {tex(_puissance_x(max(A['k'], B['k'])))} \text{{ en évidence}}")
    commun = min(A["k"], B["k"]) if n.op == "/" else 0
    just_simpl = rf"\text{{on simplifie par }} {tex(_puissance_x(commun))}" if commun and n.op == "/" else None
    ch.lim(tex(g), just_simpl, g)
    avant = _conclure(ch, g, L, ctx)
    if ch.complete and n is ctx.f:
        ctx.racine_dite = True
    return L, [_ligne_fi(n, fi, ctx)] + avant + [ch] + ([] if ch.complete else narration)


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
    absx = r"\ln|x|" if k == 1 else rf"{k}\ln|x|"
    ln_c = rf"\ln {qtex(c)}"
    # numérateur : ln(x^k(c + …)) = k ln|x| + ln(c + …)
    if ru is not None:
        f0 = rf"\ln\left({_monome_tex(F(1), k)}\left({tex(ru)}\right)\right)"
        f1 = rf"{absx} + \ln\left({tex(ru)}\right)"
        eq_u = rf"{tex(n.a.a)} = {_monome_tex(F(1), k)}\left({tex(ru)}\right)"
        B = rf"\dfrac{{\ln\left({tex(ru)}\right)}}{{{xp}}}"
    else:
        f0 = rf"\ln\left({tex(n.a.a)}\right)"
        f1 = absx if c == 1 else rf"{ln_c} + {absx}"
        eq_u = None
        B = rf"\dfrac{{{ln_c}}}{{{xp}}}" if c != 1 else None
    den_evid = V["stades"][3]
    ch = ctx.chaine(n)
    just0 = (", ".join([e for e in ([eq_u] if eq_u else []) + V["eqs"]])) or None
    ch.lim(rf"\dfrac{{{f0}}}{{{den_evid}}}", just0)
    just1 = r"\ln(ab) = \ln a + \ln b" + (rf" ,\; \ln x^{{{k}}} = {k}\ln|x|" if k > 1 else "")
    ch.lim(rf"\dfrac{{{f1}}}{{{den_evid}}}", just1)
    A_ = rf"\dfrac{{\ln|x|}}{{{xp}}}"
    corps = (A_ if k == 1 else rf"{k}\,{A_}") + (f" + {B}" if B else "")
    sans_pref = V["coef"] == 1 and _est_un(V["R"])
    if sans_pref:
        f2 = corps
    else:
        den = _produit_arbres([t for t in (Nb(abs(V["coef"])) if abs(V["coef"]) != 1 else None,
                                            None if _est_un(V["R"]) else V["R"]) if t is not None])
        f2 = rf"{'-' if V['coef'] < 0 else ''}\dfrac{{1}}{{{tex(den)}}}\left({corps}\right)"
    ch.lim(f2, rf"\text{{on divise par }} {xp}")
    # limites : croissance comparée pour ln|x|/x^p, puis le reste
    ref = REFERENCES["ln_sur_puissance"][0]
    if s > 0:
        j_cc = rf"{A_} \to 0 \text{{ : croissance comparée, }} {ref}"
    else:
        tp = "t" if p == 1 else f"t^{{{p}}}"
        signe = "" if p % 2 == 0 else "-"
        j_cc = (rf"t = -x \to +\infty ,\; {A_} = {signe}\dfrac{{\ln t}}{{{tp}}} \to 0 \text{{ : croissance comparée, }} "
                r"\lim_{t\to +\infty} \dfrac{\ln t}{t^{n}} = 0")
    justs = [j_cc]
    if B:
        justs.append(rf"{B} \to 0 \text{{ (numérateur fini, dénominateur }} \to \pm\infty \text{{)}}")
    nul = r"2 \cdot 0" if k == 2 else (r"0" if k == 1 else rf"{k} \cdot 0")
    valeur = nul + (" + 0" if B else "")
    if not sans_pref and abs(V["coef"]) != 1:
        valeur = rf"{'-' if V['coef'] < 0 else ''}\dfrac{{1}}{{{qtex(abs(V['coef']))}}}\left({valeur}\right)"
    elif V["coef"] < 0:
        valeur = rf"-\left({valeur}\right)"
    ap = _signe(V["coef"]) * (s if p % 2 else 1)
    L = Lim.fin(0, ap)
    ch.val(valeur, r" ;\; ".join(justs))
    ch.val("0")
    ch.complete = True
    math, pre = ctx.dire(n, L)
    if n is ctx.f:
        ctx.racine_dite = True
    return L, [_ligne_fi(n, fi, ctx), ch] + pre


# --- méthode : √(u²) = |u| (en une valeur, d'un seul côté) ---------------------------------------
def _racine_carree_de(Q):
    """Polynôme P (Fractions) tel que P² = Q, ou None si Q n'est pas le carré d'un polynôme à coefficients rationnels."""
    sp = _sympy()
    x = _SP["x"]
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
        cote = "gauche" if pt.d < 0 else "droite"
        justs.append(rf"{u} {'>' if sg > 0 else '<'} 0 \text{{ à {cote} de }} {pt.a_tex} \text{{, donc }} |{u}| = "
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
            fx = tex(_arbre_poly([-a, F(1)])) if a else "x"
            ch.lim(tex(g2), rf"\text{{on simplifie par }} {fx} \text{{ (}} x \neq {pt.a_tex}\text{{)}}", g2)
    L, narration = _noeud(g2, ctx)
    avant = _conclure(ch, g2, L, ctx)
    if ch.complete and n is ctx.f:
        ctx.racine_dite = True
    if ch.complete:
        return L, [_ligne_fi(n, fi, ctx)] + avant + [ch]
    return L, [_ligne_fi(n, fi, ctx)] + avant + [ch] + [l for l in narration if not _est_ligne_fi(l)]


def _est_ligne_fi(l):
    return isinstance(l, str) and "forme indéterminée" in l


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
    carres = rf"{_entre_parentheses(_carre_tex(U))} - {_entre_parentheses(_carre_tex(V))}"
    L, narration = _noeud(g, ctx)
    ch = ctx.chaine(n)
    ch.lim(rf"\dfrac{{\left({tex(n)}\right)\left({tex(conj)}\right)}}{{{tex(conj)}}}",
           rf"\text{{on multiplie et on divise par la conjuguée }} {tex(conj)}")
    ch.lim(rf"\dfrac{{{carres}}}{{{tex(conj)}}}", r"(a - b)(a + b) = a^{2} - b^{2}")
    ch.lim(tex(g), None, g)
    avant, apres = _prolonger(ch, g, L, narration, ctx)
    if ch.complete and n is ctx.f:
        ctx.racine_dite = True
    return L, [_ligne_fi(n, fi, ctx)] + avant + [ch] + apres


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
        cote = "numérateur" if racine_au_numerateur else "dénominateur"
        L, narration = _noeud(g, ctx)
        ch = ctx.chaine(n)
        etapes = egalites                              # (S1, S2, S3) selon la position de la racine
        ch.lim(etapes[0], rf"\text{{on multiplie par la conjuguée }} {tex(conj)} \text{{ du {cote}}}")
        ch.lim(etapes[1], r"(a - b)(a + b) = a^{2} - b^{2}")
        ch.lim(etapes[2], None)
        ch.lim(rf"\dfrac{{{haut}}}{{{bas}}}", rf"\text{{on factorise par }} \left({xa}\right)")
        ch.lim(tex(g), rf"\text{{on simplifie}} \; (x \neq {pt.a_tex})", g)
        avant, apres = _prolonger(ch, g, L, narration, ctx)
        if ch.complete and n is ctx.f:
            ctx.racine_dite = True
        return L, [_ligne_fi(n, fi, ctx)] + avant + [ch] + apres
    return None


def _conjuguee(n, ctx, fi):
    if isinstance(n, Op) and n.op in "+-":
        return _conjuguee_difference(n, ctx, fi)
    return _conjuguee_zero_sur_zero(n, ctx, fi)




# --- méthode : croissance comparée (Q1) et mise en évidence d'une exponentielle ---------------------
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
    """Produit ou quotient de x^n, e^{ax}, ln x (Q1) : on nomme la limite de référence utilisée ; un facteur
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
    just = rf"{tex(pur)} \to {Lref.tex(False)} \text{{ : croissance comparée, }} {lim_ref} \text{{ pour }} {cond}"
    if C != 1 or tex(pur) != tex(n):
        ch.lim(rf"{tex(_arbre_avec_coefficient(C, pur))}", None)
    ch.val(L.tex(False), just)
    ch.complete = True
    if n is ctx.f:
        ctx.racine_dite = True
    return L, [_ligne_fi(n, fi, ctx), ch]


def _comparee_avec_polynomes(n, ctx, fi, C, N, B, q, polys):
    """(x + 1)e^{-x} : on met x en évidence dans le polynôme, puis on conclut avec le produit sans polynôme."""
    sp = _sympy()
    egalites, crochets = [], None
    x = _SP["x"]
    for P, k in polys:
        m = deg(P)
        tete, interieur, complet, termes = _facteur_detaille(P, m)
        egalites.append(rf"{ptex(P, 'x')} = {complet}")
        C, N = C * P[-1] ** k, N + m * k
        expr = sum(_rat(c) * x ** i for i, c in enumerate(P)) / (_rat(P[-1]) * x ** m)
        bt = arbre_depuis_sympy(sp.expand(expr))
        facteur = bt if k == 1 else (Op("^", bt, Nb(F(k))) if k > 0 else Op("/", Nb(F(1)), Op("^", bt, Nb(F(-k)))))
        crochets = facteur if crochets is None else Op("*", crochets, facteur)
    g = Op("*", _arbre_avec_coefficient(C, _arbre_pur(N, B, q)), crochets)
    _meme_fonction(n, g, ctx)
    L, narration = _noeud(g, ctx)
    ch = ctx.chaine(n)
    ch.lim(tex(g), ", ".join(egalites))
    avant, apres = _prolonger(ch, g, L, narration, ctx)
    if ch.complete and n is ctx.f:
        ctx.racine_dite = True
    return L, [_ligne_fi(n, fi, ctx)] + avant + [ch] + apres


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
        just = rf"\text{{on met }} {tex(D)} \text{{ en évidence}}"
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
        morceaux = [(S, d, cr) for S, _, d, cr in cotes if d is not None]
        evid = " ,\\; ".join(rf"{tex(S)} = {tex(Op('*', d, cr))}" for S, d, cr in morceaux)
        cle_dom = tex(morceaux[0][1])
        neutre = isinstance(pur, Nb) and pur.v == 1
        haut = [t for t in (None if neutre else pur, cotes[0][3]) if t is not None]
        g = haut[0] if len(haut) == 1 else (Op("*", haut[0], haut[1]) if haut else Nb(F(1)))
        if cotes[1][3] is not None:
            g = Op("/", g, cotes[1][3])
        just = rf"\text{{on met }} {cle_dom} \text{{ en évidence}} ,\; {evid}"
    else:
        return None
    _meme_fonction(n, g, ctx)
    L, narration = _noeud(g, ctx)
    ch = ctx.chaine(n)
    ch.lim(tex(g), just, g)
    avant, apres = _prolonger(ch, g, L, narration, ctx)
    if ch.complete and n is ctx.f:
        ctx.racine_dite = True
    return L, [_ligne_fi(n, fi, ctx)] + avant + [ch] + apres


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


def _g_prime_non_nul(gp, I, ctx):
    """Texte qui établit g'(x) ≠ 0 au voisinage du point d'étude (sauf peut-être en lui), ou None."""
    pt = ctx.pt
    if sans_x(gp):
        v = valeur_constante(gp)
        return (rf"\(g'(x) = {tex(gp)} \neq 0\)", False) if v else None
    try:
        D, P, Z, _, _ = signe_facteur(gp, "x")
        Z = fusion(inter(Z, I))
        if not pt.s:
            a = float(pt.a)
            Z = [iv for iv in Z if not (iv.lo is not None and proche(iv.lo.val, a))]
    except Exception:
        return None
    if Z:
        return None
    return rf"\(g'(x) = {tex(gp)}\) ne s'annule pas sur \({ens_tex(I)}\)", True


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
    sp = _sympy()
    e = en_sympy_reel(h)
    return sp.diff(e, _SP["x"])


def _candidats_lhopital(n, ctx, fi):
    """(f, g, lignes d'introduction) : f/g est une forme 0/0 ou ∞/∞ égale à n."""
    if isinstance(n, Op) and n.op == "/" and fi.nom in ("0/0", "∞/∞"):
        return [(n.a, n.b, [], fi.nom)]
    if isinstance(n, Op) and n.op == "*" and fi.nom == "0 · ∞":
        out = []
        for u, v in ((n.b, n.a), (n.a, n.b)):            # u/(1/v) : on met d'abord au dénominateur le facteur qui tend vers 0
            g = Op("/", Nb(F(1)), v)
            out.append((u, g, [rf"On écrit \({tex(n)} = \dfrac{{{tex(u)}}}{{{tex(g)}}}\) pour obtenir un quotient."], None))
        return out
    return []


def _lhopital(n, ctx, fi):
    if ctx.nb_lhopital >= 2:
        return None
    if isinstance(n, Op) and n.op == "/" and _poly_ou_const(n.a) is not None and _poly_ou_const(n.b) is not None:
        return None                                  # fraction rationnelle : mise en évidence ou factorisation, jamais L'Hôpital
    for f, g, intro, nom in _candidats_lhopital(n, ctx, fi):
        try:
            r = _lhopital_avec(n, f, g, intro, nom, ctx, fi)
        except Abandon:
            r = None
        if r is not None:
            return r
    return None


def _lhopital_avec(n, f, g, intro, nom, ctx, fi):
    sp = _sympy()
    pt = ctx.pt
    # (a) forme indéterminée 0/0 ou ∞/∞
    if nom is None:
        Lf, _ = _noeud(f, ctx)
        Lg, _ = _noeud(g, ctx)
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
    res_c = _g_prime_non_nul(g_arbre, I, ctx)
    if res_c is None:
        return None
    texte_c, avec_donc = res_c
    ctx.nb_lhopital += 1
    try:
        L, lg = _noeud(q_arbre, ctx)
        chA = Chaine(pt, r"\dfrac{f'(x)}{g'(x)}")
        chA.lim(tex(q_arbre), None, q_arbre)
        avant, apres = _prolonger(chA, q_arbre, L, lg, ctx)
    finally:
        ctx.nb_lhopital -= 1
    vers = pt.tex()
    ens = ens_tex(I)
    point = rf"\({vers}\)" if pt.s else rf"\({pt.a_tex}\) (sauf peut-être en \({pt.a_tex}\))"
    nom_tex = rf"« \({FI_TEX[nom]}\) »"
    chB = ctx.chaine(n)
    if tex(n) != tex(Op("/", f, g)) and n is not ctx.f:
        chB.lim(rf"\dfrac{{f(x)}}{{g(x)}}", None)
    elif n is ctx.f and tex(n) != tex(Op("/", f, g)):
        chB.lim(rf"\dfrac{{{tex(f)}}}{{{tex(g)}}}", None)
    chB.lim(r"\dfrac{f'(x)}{g'(x)}", r"\text{règle de Bernoulli-L'Hôpital}")
    chB.val(L.tex(False))
    chB.complete = True
    if n is ctx.f:
        ctx.racine_dite = True
    lignes = intro + [
        rf"On applique la règle de Bernoulli-L'Hôpital avec \(f(x) = {tex(f)}\) et \(g(x) = {tex(g)}\). "
        r"Vérifions les hypothèses :",
        rf"(a) forme indéterminée {nom_tex} : vérifiée ;",
        rf"(b) \(f\) et \(g\) sont dérivables sur \({ens}\), donc au voisinage de {point} : vérifiée ;",
        rf"On calcule \(f'(x) = {tex(f_arbre)}\) et \(g'(x) = {tex(g_arbre)}\).",
        (rf"(c) {texte_c}, donc \(g'(x) \neq 0\) au voisinage de {point} : vérifiée ;" if avec_donc
         else rf"(c) {texte_c} au voisinage de {point} : vérifiée ;"),
        r"(d) Calculons la limite de \(\dfrac{f'(x)}{g'(x)}\) :",
    ] + avant + [chA] + apres + [
        rf"La limite de \(\dfrac{{f'(x)}}{{g'(x)}}\) existe et vaut \({L.tex(False)}\) : (d) est vérifiée, "
        r"donc la règle s'applique :",
        chB,
    ]
    return L, [_ligne_fi(n, fi, ctx)] + lignes


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
    ch.lim(tex(g), rf"\text{{on simplifie}} \; (x \neq {pt.a_tex})", g)
    avant = _conclure(ch, g, L, ctx)
    if ch.complete and n is ctx.f:
        ctx.racine_dite = True
    return L, [_ligne_fi(n, fi, ctx)] + avant + [ch] + ([] if ch.complete else narration)


# ordre du cours : mise en évidence, conjuguée, mise en évidence sous une racine, croissance comparée, L'Hôpital
METHODES[:] = [_racine_carre_parfait, _simplifier_zero_sur_zero, _evidence_exp, _conjuguee, _evidence_racine, _comparee_pure, _evidence_ln, _lhopital]


def _silencieux(n, L, ctx):
    """Un nœud défini au point d'étude, de limite finie, n'a rien à raconter : sa limite est sa valeur."""
    return not ctx.pt.s and not L.inf and _defini_en(n, ctx)


def _lignes_pole(n, ctx, A, la, B, L):
    """Quotient dont le dénominateur tend vers 0 : numérateur, puis le signe du dénominateur lu dans le tableau
    de signes (ou justifié en texte si le tableau est impossible), puis la limite."""
    pt = ctx.pt
    lignes = []
    if sans_x(n.a):
        num = rf"Le numérateur vaut \({A.tex(False)}\)"
    elif not A.inf and _defini_en(n.a, ctx):
        sub, val = _tex_en(n.a, pt), A.tex(False)
        num = rf"Le numérateur \({tex(n.a)}\) vaut \({sub if sub == val else sub + ' = ' + val}\)"
    else:
        lignes += la
        num = rf"Le numérateur \({tex(n.a)}\) tend vers \({A.tex(False)}\)"
    lu = ctx.lecture("den", n.b, B)
    lignes.append(num + rf" et le dénominateur \({tex(n.b)}\) tend vers \(0\).")
    s = "+" if B.ap > 0 else "-"
    fraction = rf"\dfrac{{{A.tex(False)}}}{{0^{{{s}}}}} = {L.tex(False)}"
    if n is ctx.f:
        ctx.racine_dite = True
        if ctx.mode == "limite":
            fin = rf"\(\displaystyle\lim_{{x\to {pt.tex()}}} f(x) = {fraction}\)"
        else:
            fin = rf"\(f(x) \to {fraction}\)"
    else:
        fin = rf"\({tex(n)} \to {fraction}\)"
    if lu is not None:
        mot = "positif" if lu > 0 else "négatif"
        lignes.append(rf"{ctx.cote()}, le dénominateur est {mot} ({ctx.renvois[('den', n.b.key())]}) : "
                      rf"il tend vers \(0^{{{s}}}\), donc {fin}.")
    else:
        lignes += ctx.justifier(n.b, B, force=True)
        lignes.append(rf"\({tex(n.b)} \to 0^{{{s}}}\), donc {fin}.")
    return lignes


def _noeud(n, ctx):
    """(limite de n au point d'étude, lignes qui l'expliquent) ; Abandon si l'on ne peut pas la justifier."""
    pt = ctx.pt
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
            if _silencieux(n, L, ctx):
                return L, []
            math, pre = ctx.dire(n, L)
            debut = rf"Quand \(x \to {pt.tex()}\), " if isinstance(n.a, X) and n is not ctx.f else ""
            return L, lu + pre + [debut + math + "."]
        if isinstance(n, Op) and n.op in "+-*/":
            A, la = _noeud(n.a, ctx)
            B, lb = _noeud(n.b, ctx)
            if n.op == "/" and B.nul() and not A.nul():
                if not B.ap:
                    raise Abandon("signe du dénominateur inconnu")
                L = _quotient(A, B)
                ctx.verifier(n, L)
                return L, _lignes_pole(n, ctx, A, la, B, L)
            try:
                L = {"+": lambda: _somme(A, B), "-": lambda: _somme(A, _oppose(B)),
                     "*": lambda: _produit(A, B), "/": lambda: _quotient(A, B)}[n.op]()
            except FormeIndeterminee as fi:
                fi.A, fi.B, fi.la, fi.lb = A, B, la, lb
                raise
            ctx.verifier(n, L)
            if _silencieux(n, L, ctx):
                return L, []
            math, pre = ctx.dire(n, L)
            ca, cb = sans_x(n.a), sans_x(n.b)
            if ca or cb:        # une constante se remplace directement : on ne répète pas l'autre terme
                autre = n.b if ca else n.a
                debut = rf"Quand \(x \to {pt.tex()}\), " if isinstance(autre, X) and n is not ctx.f else ""
                return L, la + lb + pre + [debut + math + "."]
            ma, pa = ctx.dire(n.a, A)
            mb, pb = ctx.dire(n.b, B)
            la = [l for l in la if l != ma + "."]
            lb = [l for l in lb if l != mb + "."]
            return L, la + lb + pa + pb + pre + [f"{ma} et {mb}, donc {math}."]
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
            g = r"\sqrt{t}" if alpha == F(1, 2) else rf"t^{{{qtex(alpha)}}}"
        elif isinstance(n, Fn):
            U, lu = _noeud(n.a, ctx)
            if n.nom == "exp":
                L, g = _exp_lim(U), r"e^{t}"
            elif n.nom == "ln":
                L, g = _ln_lim(U), r"\ln t"
            else:
                L, g = _puissance_reelle(U, F(1, 2)), r"\sqrt{t}"
        else:
            raise Abandon(f"sous-expression non prise en charge : {tex(n)}")
        ctx.verifier(n, L)
        if _silencieux(n, L, ctx):
            return L, []
        # le signe d'un argument qui tend vers 0 ne sert que pour ln et pour une puissance
        besoin_signe = U.nul() and U.ap and not (isinstance(n, Fn) and n.nom in ("exp", "sqrt"))
        pre, rappel = [], ""
        if besoin_signe and not isinstance(n.a, X):
            if isinstance(n, Fn):
                genre, quoi, accord = "ln", "l'argument", ("positif", "négatif", "il")
            else:
                genre, quoi, accord = ("den" if valeur_constante(n.b) < 0 else "ln"), "la base", ("positive", "négative", "elle")
            lu_signe = ctx.lecture(genre, n.a, U)
            if lu_signe is not None:
                s0 = "+" if U.ap > 0 else "-"
                pre = [rf"{ctx.cote()}, {quoi} \({tex(n.a)}\) est {accord[0] if lu_signe > 0 else accord[1]} "
                       rf"({ctx.renvois[(genre, n.a.key())]}) : {accord[2]} tend vers \(0^{{{s0}}}\)."]
            else:
                pre = ctx.justifier(n.a, U)
                rappel = rf" et \({tex(n.a)} \to {U.tex()}\)"
        u_tex = U.tex(bool(besoin_signe))
        math, pre_n = ctx.dire(n, L)
        return L, lu + pre + pre_n + [rf"Or \({g} \to {L.tex()}\) quand \(t \to {u_tex}\){rappel}, donc {math}."]
    except FormeIndeterminee as fi:
        fi.noeud = n
        return _lever(n, ctx, fi)


def _sans_doublons(lignes):
    vues, out = set(), []
    for l in lignes:
        cle = l.html() if isinstance(l, Chaine) else l
        if cle not in vues:
            vues.add(cle)
            out.append(l)
    return out


def _rediger(f, pt, ref, mode="limite", label="f(x)", label_somme=False):
    """(lignes, None) si la limite de f en pt est rédigée et coïncide avec ref (valeur SymPy), sinon
    (None, raison technique)."""
    try:
        R = _lim_depuis_sympy(ref)
        ctx = _Contexte(pt, f, R, mode, label, label_somme)
        L, lignes = _noeud(f, ctx)
        if not _meme_valeur(L, R):
            raise Abandon(f"valeur rédigée {L.tex()} ≠ référence {R.tex()}")
        lignes = _tout_texte(_sans_doublons(lignes))
        for genre, noeud in ctx.demandes:
            TABLEAUX.utiliser(genre, noeud)
        if mode == "limite" and not ctx.racine_dite:
            lignes.append(rf"Donc \(\displaystyle\lim_{{x\to {pt.tex()}}} {label} = {L.tex(False)}\).")
        return lignes, None
    except Exception as e:      # rien ne doit faire échouer l'étude : on retombe sur le résultat seul
        return None, f"{type(e).__name__} : {e}"


def _repli(pt, vtex, detail, label="f(x)"):
    lim = rf"\displaystyle\lim_{{x\to {pt.tex()}}} {label} = {vtex}"
    item = txt(PHRASE_REPLI + rf"\({lim}\).")
    item["detail"] = detail
    return item


def _narrer_limite(f, pt, ref, vtex, items, alternative=None, label="f(x)", label_somme=False):
    """Étapes de lim f en pt : rédigées si possible, sinon phrase de repli et résultat de référence.
    alternative = (arbre équivalent, phrase d'introduction) : essayée si f, telle qu'elle est écrite, résiste."""
    lignes, detail = _rediger(f, pt, ref, "limite", label, label_somme)
    if lignes is None and alternative is not None:
        g, intro = alternative
        lignes2, detail2 = _rediger(g, pt, ref, "limite", label, label_somme)
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
    eq = _equation_affine(a_tex, b_tex)
    items.append(txt(r"On cherche une asymptote oblique d'équation \(y = ax + b\) : \(a = \displaystyle\lim \frac{f(x)}{x}\), "
                     r"puis \(b = \displaystyle\lim \left(f(x) - ax\right)\)."))
    pt = Pt({"type": "inf", "signe": signe})
    a_rat = F(int(a_val.p), int(a_val.q)) if a_val.is_Rational else None
    if a_rat is None:
        items.append(txt(rf"\(a = {a_tex}\) et \(b = {b_tex}\) sont finis (et \(a \neq 0\)) : asymptote oblique d'équation \(y = {eq}\)."))
    else:
        _narrer_limite(Op("/", f, X()), pt, a_val, a_tex, items, label=r"\dfrac{f(x)}{x}")
        fb = _arbre_moins_ax(f, a_rat)
        coef = "" if abs(a_rat) == 1 else qtex(abs(a_rat))
        _narrer_limite(fb, pt, b_val, b_tex, items, label=rf"f(x) {'-' if a_rat > 0 else '+'} {coef}x", label_somme=True)
        items.append(txt(rf"\(a = {a_tex}\) et \(b = {b_tex}\) sont finis (et \(a \neq 0\)) : "
                         rf"asymptote oblique d'équation \(y = {eq}\)."))
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
    vers = r"+\infty" if s > 0 else r"-\infty"
    qt, wt, rt = ptex(Q, "x"), ptex(W, "x"), qtex(r[0])
    racine = rf"\sqrt{{{qt}}}"
    gauche = rf"\sqrt{{{qt}}} - \left({wt}\right)"
    gauche_h = rf"f(x) - \left({_equation_affine(qtex(a), qtex(b))}\right)"
    droite0 = gauche if ur > 0 else rf"-\left({gauche}\right)"
    suite = rf"\dfrac{{{qt} - \left({wt}\right)^{{2}}}}{{{racine} + {_entre_parentheses(wt)}}}"
    ligne2 = (suite if ur > 0 else "-" + suite)
    ligne3 = rf"\dfrac{{{rt}}}{{{racine} + {_entre_parentheses(wt)}}}" if ur > 0 else rf"-\dfrac{{{rt}}}{{{racine} + {_entre_parentheses(wt)}}}"
    return [txt(_egalites(gauche_h, [droite0, ligne2, ligne3])),
            txt(rf"Près de \({vers}\), \({racine} + {_entre_parentheses(wt)}\) est positif (\({racine} - {_entre_parentheses(wt)}\) tend vers 0 "
                rf"et \({racine} > 0\)), et {_mot_signe_r(ur, r[0])} : \(f(x) - \left({_equation_affine(qtex(a), qtex(b))}\right)\) est "
                f"{_mot_signe(sg)} : la courbe est " + ("au-dessus" if sg > 0 else "au-dessous") + " de la droite.")]


def _mot_signe_r(u, r):
    """« la constante 8 est positive » (précédée du signe − pour −√Q…)."""
    return (rf"la constante \({qtex(r)}\) est {'positive' if r > 0 else 'négative'}" + ("" if u > 0 else ", précédée du signe −"))


def _narrer_cotes(f, borne, items, ref_de, cotes=("gauche", "droite")):
    """Limites à gauche et à droite d'une valeur interdite : la partie commune une seule fois, puis une
    ligne courte par côté ; une seule conclusion si les deux côtés donnent la même limite.
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
        lg, dg = _rediger(f, pg, vg_ref, "fleche")
        ld, dd = _rediger(f, pd, vd_ref, "fleche")
        if lg is not None and ld is not None:
            fusion = _fusion_cotes(lg, ld)
            for ligne in fusion:
                items.append(txt(ligne))
            if vg == vd and not any(r"\lim_{x\to" in ligne for ligne in fusion):
                items.append(txt(rf"Donc \(\displaystyle\lim_{{x\to {borne['point'].tex}}} f(x) = {vg}\)."))
            return sortie
        if lg is None and ld is None and vg == vd:
            items.append(_repli(Pt(borne, 0), vg, f"{dg} | {dd}"))
            return sortie
    for (cle, pt, val, vt, _), prefixe in zip(cas, ("À gauche : ", "À droite : ")):
        if vt == "?":
            items.append(txt(prefixe + rf"\(\displaystyle\lim_{{x\to {pt.tex()}}} f(x) = {NON_DETERMINEE_TEX}\)."))
            continue
        bloc = []
        _narrer_limite(f, pt, val, vt, bloc)
        premier = bloc[0]["html"]
        if premier.startswith(PHRASE_REPLI):
            premier = "l" + premier[1:]
        morceaux = _avec_prefixe(prefixe, premier)
        bloc[:1] = [txt(l) for l in morceaux[:-1]] + [dict(bloc[0], html=morceaux[-1])]
        items.extend(bloc)
    return sortie


def _avec_prefixe(prefixe, ligne):
    """« À gauche : » devant une ligne ; devant une formule affichée (chaîne d'égalités), sur sa propre ligne."""
    if ligne.startswith("\\["):
        return [prefixe.strip(), ligne]
    return [prefixe + ligne]


def _fusion_cotes(gauche, droite):
    """Lignes communes une seule fois, lignes propres à chaque côté précédées de « À gauche : » / « À droite : »
    (sauf si elles commencent déjà par « À gauche de a, … »). Deux lignes qui ne diffèrent que par le côté
    deviennent « De part et d'autre de a, … »."""
    import difflib
    import re
    motif = re.compile(r"^À (?:gauche|droite) de (.+?), ")

    unilatere = re.compile(r"\\lim_\{x\\to ([^{}]+?)\^\{[+-]\}\}")

    def normal(l):
        if l.startswith("\\["):                  # chaîne d'égalités : la même calcul des deux côtés s'écrit une fois
            return unilatere.sub(r"\\lim_{x\\to \1}", l)
        return motif.sub(r"@ de \1, ", l)

    sortie = []
    ng, nd = [normal(l) for l in gauche], [normal(l) for l in droite]
    for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(None, ng, nd, autojunk=False).get_opcodes():
        if tag == "equal":
            for lg, ld in zip(gauche[i1:i2], droite[j1:j2]):
                m = motif.match(lg)
                if lg.startswith("\\["):
                    sortie.append(normal(lg))
                else:
                    sortie.append(lg if lg == ld else motif.sub(rf"De part et d'autre de \1, ", lg) if m else lg)
            continue
        for lignes, prefixe in ((gauche[i1:i2], "À gauche : "), (droite[j1:j2], "À droite : ")):
            if lignes:
                if motif.match(lignes[0]):
                    sortie.append(lignes[0])
                else:
                    sortie.extend(_avec_prefixe(prefixe, lignes[0]))
                sortie.extend(lignes[1:])
    return sortie


def _etude_transcendante(f, borne, items):
    if borne["type"] == "inf":
        cote = None
    else:
        point, cote = borne["point"], borne["cote"]
        if cote == "deux":
            items.append(txt(rf"\(x = {point.tex}\) est une valeur interdite."))
        else:
            vers = Pt(borne, {"gauche": -1, "droite": 1}[cote]).tex()
            items.append(txt(rf"\(x = {point.tex}\) est une valeur interdite : on étudie la limite de \(f\) "
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
    inf_g, inf_d = r"\infty" in vg, r"\infty" in vd
    if inf_g or inf_d:
        if inf_g and inf_d:
            conclusion = rf"Asymptote verticale d'équation \(x = {point.tex}\)."
        else:
            cote, autre, v_autre = ("droit", "gauche", vg) if inf_d else ("gauche", "droite", vd)
            conclusion = (rf"Asymptote verticale d'équation \(x = {point.tex}\) (du côté {cote}) ; "
                          rf"à {autre}, \(f(x) \to {_affichable(v_autre)}\).")
        items.append(txt(conclusion))
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

    TABLEAUX.reset()
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

    res["tableaux_signe"] = TABLEAUX.items()
    return res


def etudier_json(entree):
    return json_strict(etudier(entree))


if __name__ == "__main__":
    import sys
    for arg in sys.argv[1:] or ["(x^2-1)/(x-3)"]:
        print(json.dumps(etudier(arg), ensure_ascii=False, indent=2))
        print("=" * 60)
