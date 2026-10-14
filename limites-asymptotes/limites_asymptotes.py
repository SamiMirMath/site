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
    valeur ; la narration reste simple (substitution directe), avec mention
    explicite d'une croissance comparée quand un facteur polynomial et un facteur
    exponentiel sont en compétition.
"""
import json
from fractions import Fraction as F

from ensemble_def import (
    Nb, X, E, Neg, Op, Fn,
    lire, tex, prec, valeur_constante, Num, Iv, REELS, fusion, inter, ens_tex,
    contient, proche, evaluer, aplatir, qtex, ptex, pn, deg, peval, pdivlin,
    decomposer, r_norm,
    _sympy, en_sympy, arbre_depuis_sympy, num_sympy, _SP,
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
        fe = en_sympy(f)
        r = sp.limit(fe, _SP["x"], point, dir=direction) if direction else sp.limit(fe, _SP["x"], point)
        return r
    except Exception:
        return None


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
    """ratio·x^k, k pouvant être négatif (écrit alors comme une fraction)."""
    if k >= 0:
        return _monome_tex(ratio, k)
    p = "x" if k == -1 else f"x^{{{-k}}}"
    if ratio == 1:
        return rf"\dfrac{{1}}{{{p}}}"
    if ratio == -1:
        return rf"-\dfrac{{1}}{{{p}}}"
    return rf"\dfrac{{{qtex(ratio)}}}{{{p}}}"


def _facteur_detaille(P, n):
    """P(x) = a_n·x^n·(1 + ... ), avec CHAQUE terme restant écrit explicitement
    (jamais de « ... ») : ex. x^2 - 1 = x^2(1 - 1/x^2).
    Renvoie (tête a_n·x^n, parenthèse intérieure, expression complète)."""
    an = P[n]
    interieur = "1"
    for k in range(n - 1, -1, -1):
        c = P[k] if k < len(P) else F(0)
        if c == 0:
            continue
        ratio = c / an
        if ratio < 0:
            interieur += " - " + _terme_tex(-ratio, k - n)
        else:
            interieur += " + " + _terme_tex(ratio, k - n)
    tete = _monome_tex(an, n)
    complet = tete if interieur == "1" else tete + r"\left(" + interieur + r"\right)"
    return tete, interieur, complet


def _etude_rationnelle_infini(N, D, signe, items):
    n, m = deg(N), deg(D)
    an, bm = N[-1], D[-1]
    vers = r"+\infty" if signe > 0 else r"-\infty"
    teteN, intN, Nf = _facteur_detaille(N, n)
    teteD, intD, Df = _facteur_detaille(D, m)
    items.append(txt(
        rf"On factorise le numérateur et le dénominateur par leur terme de plus haut degré : "
        rf"\({ptex(N,'x')} = {Nf}\) et \({ptex(D,'x')} = {Df}\)."
    ))
    ratio = an / bm
    non_triviaux = [t for t in (intN, intD) if t != "1"]
    if intN == "1" and intD == "1":
        items.append(txt(rf"Donc \(f(x) = \dfrac{{{Nf}}}{{{Df}}} = {_terme_tex(ratio, n - m)}\) exactement."))
    else:
        items.append(txt(
            rf"Donc \(f(x) = \dfrac{{{Nf}}}{{{Df}}} = {_terme_tex(ratio, n - m)} \cdot "
            rf"\dfrac{{{intN}}}{{{intD}}}\)."
        ))
        sujet, verbe = ("ces expressions", "tendent") if len(non_triviaux) > 1 else ("cette expression", "tend")
        items.append(txt(
            rf"Quand \(x\to{vers}\), chaque terme en \(1/x^k\) dans "
            + " et dans ".join(rf"\({t}\)" for t in non_triviaux) +
            rf" tend vers 0 : {sujet} {verbe} donc vers 1, "
            r"et le quotient \(\dfrac{" + intN + r"}{" + intD + r"}\) tend vers 1 aussi."
        ))
    if n < m:
        items.append(txt(
            rf"Il reste \(f(x) \to {_terme_tex(ratio, n-m)}\) avec un exposant négatif : "
            r"la limite est 0."
        ))
        return {"genre": "horizontale", "valeur_tex": "0", "valeur_val": 0.0}
    if n == m:
        items.append(txt(rf"Il reste \(f(x) \to {qtex(ratio)}\) : même degré, la limite est le rapport "
                         r"des coefficients dominants."))
        return {"genre": "horizontale", "valeur_tex": qtex(ratio), "valeur_val": float(ratio)}
    # n > m : signe de x^(n-m) selon la parité et la direction
    k = n - m
    signe_xk = 1 if (signe > 0 or k % 2 == 0) else -1
    signe_final = 1 if (ratio > 0) == (signe_xk > 0) else -1
    val_tex = r"+\infty" if signe_final > 0 else r"-\infty"
    if k == 1:
        Q, R = _pdiv(N, D)
        items.append(txt(
            rf"Il reste \(f(x) \to {_terme_tex(ratio, k)}\) : la limite est \({val_tex}\), et il y a une "
            r"asymptote oblique. On effectue la division polynomiale du numérateur par le dénominateur, "
            rf"\({ptex(N,'x')}\) par \({ptex(D,'x')}\) (voir le chapitre « Division polynomiale ») : "
            rf"\({ptex(N,'x')} = \left({ptex(D,'x')}\right)\left({ptex(Q,'x')}\right) + {ptex(R,'x')}\), "
            rf"donc \(f(x) = {ptex(Q,'x')} + \dfrac{{{ptex(R,'x')}}}{{{ptex(D,'x')}}}\), "
            r"et ce dernier terme tend vers 0."
        ))
        a = Q[1] if len(Q) > 1 else F(0)
        b = Q[0] if Q else F(0)
        return {"genre": "oblique", "a": qtex(a), "b": qtex(b), "a_val": float(a), "b_val": float(b),
                "equation_tex": ptex(Q, "x"), "valeur_tex": val_tex}
    items.append(txt(
        rf"Il reste \(f(x) \to {_terme_tex(ratio, k)}\) : le degré du numérateur dépasse celui du "
        rf"dénominateur de {k} \(\geq 2\), la limite est \({val_tex}\) "
        r"(branche parabolique, pas d'asymptote oblique)."
    ))
    return {"genre": "aucune", "valeur_tex": val_tex}


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
        items.append(txt(rf"Le numérateur ne s'annule pas en \(x={point.tex}\) (seul le dénominateur "
                         r"s'y annule) : asymptote verticale."))
        res = {"genre": "verticale", "point_tex": point.tex, "point_val": a}
        for cle, dx in (("gauche", -1e-6), ("droite", 1e-6)):
            if cote in (cle, "deux"):
                v = _signe_tex(a + dx)
                items.append(txt(rf"À {cle}, \(f(x) \to {v}\)."))
                res[cle + "_tex"] = v
        return res
    items.append(txt(rf"Le numérateur s'annule aussi en \(x={point.tex}\) : forme indéterminée "
                     r"\(0/0\). On factorise (calcul formel) pour simplifier avant de passer à la limite."))
    val = _limite_sympy(f, _sympify_point(point))
    vtex, _, _, vval = _valeur_tex(val)
    if vtex == "?":
        items.append(txt("La limite n'a pas pu être déterminée automatiquement : on ne conclut pas sur une éventuelle asymptote."))
        return None
    items.append(txt(rf"\(\displaystyle\lim_{{x\to {point.tex}}} f(x) = {vtex}\) : "
                     + _phrase_trou(point.tex, vtex)))
    return {"genre": "trou", "point_tex": point.tex, "point_val": a, "valeur_tex": vtex, "valeur_val": vval}


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


def _etude_rationnelle_pole(f, N, D, point, cote, items):
    if point.q is None:
        return _etude_pole_numerique(f, N, D, point, cote, items)
    a = point.q
    xa = _x_moins(a)
    N2, multN = _facteur_racine(N, a)
    D2, multD = _facteur_racine(D, a)
    N2a, D2a = peval(N2, a), peval(D2, a)
    fac_N2 = qtex(N2a) if deg(N2) == 0 else ptex(N2, "x")
    fac_D2 = qtex(D2a) if deg(D2) == 0 else ptex(D2, "x")
    f_tex = tex(f)
    mult = min(multN, multD)
    diff = multN - multD

    if mult > 0:
        # facteur(s) (x-a) communs au numérateur et au dénominateur : on les barre.
        fac_N2_prod = fac_N2 if deg(N2) == 0 else r"\left(" + fac_N2 + r"\right)"
        fac_D2_prod = fac_D2 if deg(D2) == 0 else r"\left(" + fac_D2 + r"\right)"
        commun = _facteur_tex(xa, mult)
        barre = r"\cancel{" + commun + "}"
        reste_haut = _produit_tex(_facteur_tex(xa, diff) if diff > 0 else "", fac_N2_prod)
        num_chaine = _produit_tex(reste_haut, barre)
        den_chaine = _produit_tex(barre, fac_D2_prod if diff >= 0 else _facteur_tex(xa, -diff) + r"\," + fac_D2_prod)
        simplifie_haut = reste_haut if reste_haut else "1"
        simplifie_bas = fac_D2 if diff >= 0 else _produit_tex(_facteur_tex(xa, -diff), fac_D2)
        simplifie = simplifie_haut if simplifie_bas == "1" else r"\dfrac{" + simplifie_haut + "}{" + simplifie_bas + "}"
        chaine = (
            rf"\displaystyle\lim_{{x\to {point.tex}}} f(x) = "
            rf"\lim_{{x\to {point.tex}}}\dfrac{{{num_chaine}}}{{{den_chaine}}} = "
            rf"\lim_{{x\to {point.tex}}} {simplifie}"
        )
    else:
        chaine = rf"\displaystyle\lim_{{x\to {point.tex}}} f(x) = \lim_{{x\to {point.tex}}} {f_tex}"

    if diff >= 0:
        valeur_val = 0.0 if diff > 0 else float(N2a / D2a)
        valeur = "0" if diff > 0 else qtex(N2a / D2a)
        items.append(txt(rf"\({chaine} = {valeur}\) : " + _phrase_trou(point.tex, valeur)))
        return {"genre": "trou", "point_tex": point.tex, "point_val": float(a),
                "valeur_tex": valeur, "valeur_val": valeur_val}

    k = -diff
    ratio = N2a / D2a
    res = {"genre": "verticale", "point_tex": point.tex, "point_val": float(a)}
    for sens, cle in ((-1, "gauche"), (1, "droite")):
        if cote not in (cle, "deux"):
            continue
        signe_facteur = 1 if (k % 2 == 0 or sens > 0) else -1
        signe_final = 1 if (ratio > 0) == (signe_facteur > 0) else -1
        zero_tex = "0^{+}" if signe_facteur > 0 else "0^{-}"
        v = r"+\infty" if signe_final > 0 else r"-\infty"
        exposant = "^-" if sens < 0 else "^+"
        items.append(txt(
            rf"\(\displaystyle\lim_{{x\to {point.tex}{exposant}}} f(x) = "
            + (rf"\lim_{{x\to {point.tex}{exposant}}}\dfrac{{{num_chaine}}}{{{den_chaine}}} = " if mult > 0 else "")
            + rf"\dfrac{{{qtex(ratio)}}}{{{zero_tex}}} = {v}\)."
        ))
        res[cle + "_tex"] = v
    return res


# =====================================================================
# Cas transcendant (ln, exp, racine mélangés à x) : calcul formel pour la valeur
# =====================================================================
def _croissance_comparee(f):
    """Détecte un produit « polynôme × exponentielle » (ou inverse) pour citer la
    croissance comparée dans la narration ; renvoie un texte ou None."""
    try:
        _, facs = aplatir(f)
    except Exception:
        return None
    a_exp = any(isinstance(h, Fn) and h.nom == "exp" for h, k in facs)
    a_poly = any(not (isinstance(h, Fn) and h.nom == "exp") for h, k in facs)
    if a_exp and a_poly and len(facs) > 1:
        return (r"Produit d'une puissance de \(x\) et d'une exponentielle : par croissance comparée, "
                r"l'exponentielle « domine » — la limite du produit est déterminée par elle.")
    return None


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
        fe = en_sympy(f)
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


def _etude_transcendante(f, borne, items):
    sp = _sympy()
    if borne["type"] == "inf":
        cible = sp.oo if borne["signe"] > 0 else -sp.oo
        direction, cote = None, None
    else:
        point, cote = borne["point"], borne["cote"]
        cible = _sympify_point(point)
        direction = {"gauche": "-", "droite": "+"}.get(cote)
        flèche = "-" if cote == "gauche" else "+" if cote == "droite" else None
        suffixe = f"^{{{flèche}}}" if flèche else ""
        items.append(txt(rf"\(x={point.tex}\) est une valeur interdite : on étudie la limite de \(f\) "
                         rf"quand \(x \to {point.tex}{suffixe}\)."))
    note = _croissance_comparee(f)
    if note:
        items.append(txt(note))
    if cote != "deux":
        val = _limite_sympy(f, cible, direction)
        vtex, inf, _, vval = _valeur_tex(val)
        if vtex == "?":
            items.append(txt("La limite n'a pas pu être déterminée automatiquement : on ne conclut pas sur une éventuelle asymptote."))
            return vtex, False, None, None
        if borne["type"] != "inf" and inf:
            fin = " : asymptote verticale."
        elif borne["type"] != "inf":
            fin = " : " + _phrase_trou(point.tex, vtex)
        else:
            fin = "."
        items.append(txt(rf"\(\displaystyle\lim f(x) = {vtex}\)" + fin))
        extra = _oblique_generale(f, borne["signe"], items) if (borne["type"] == "inf" and inf) else None
        return vtex, inf, extra, vval
    vg, _, _, vg_val = _valeur_tex(_limite_sympy(f, cible, "-"))
    vd, _, _, vd_val = _valeur_tex(_limite_sympy(f, cible, "+"))
    items.append(txt(rf"À gauche, \(\displaystyle\lim f(x) = {vg}\) ; à droite, "
                     rf"\(\displaystyle\lim f(x) = {vd}\)."))
    return (vg, vd), False, None, (vg_val, vd_val)


def _bilan_deux_cotes(point, cote_tex, val, vval, items):
    """Valeur interdite isolée (cas transcendant) : on ne conclut à une asymptote
    verticale que si l'une des deux limites latérales est infinie."""
    (vg, vd), (vg_val, vd_val) = val, vval
    base = {"point_tex": point.tex, "point_val": point.val, "ou": cote_tex}
    if r"\infty" in vg or r"\infty" in vd:
        items.append(txt("Au moins une des deux limites est infinie : asymptote verticale."))
        return dict(base, genre="verticale", gauche_tex=vg, droite_tex=vd,
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

    res = {"ok": True, "f_tex": tex(f), "ed_tex": res_ed["ED_tex"], "etudes": [], "asymptotes": []}

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
                asym = _etude_rationnelle_infini(N, D, borne["signe"], items)
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
    return json.dumps(etudier(entree), ensure_ascii=False)


if __name__ == "__main__":
    import sys
    for arg in sys.argv[1:] or ["(x^2-1)/(x-3)"]:
        print(json.dumps(etudier(arg), ensure_ascii=False, indent=2))
        print("=" * 60)
