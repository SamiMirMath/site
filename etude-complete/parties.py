"""
parties.py — Parties propres à l'Étude complète (decisions.md D2), rédigées ici et nulle part ailleurs : les outils séparés (Ensemble de
définition, Dérivée, Limites) ne changent pas. Chaque affirmation nouvelle a un garde-fou exact et numérique (EC-15) ; en cas de doute,
la ligne n'est pas écrite (Mise en forme) ou l'outil reprend la rédaction de l'outil ED (condition), jamais une ligne douteuse.

Partie 1. Domaine de définition (D1, D3) :
- carte « Mise en forme » quand f(x) = e^{g(x)}, g = haut / bas (deux polynômes de degré ≥ 1, écrits développés à coefficients entiers) :
  haut et bas factorisés une ligne par méthode (mise en évidence, Somme-Produit), puis « On note g(x) = …, donc f(x) = e^{g(x)}. » ;
  aucune carte quand rien ne se factorise ;
- une carte par condition (cartes de l'outil ED, R10) ; un dénominateur affine ou de la forme ax² + c, écrit développé, est résolu en
  chaîne, version courte : « On résout 6x − 12 = 0 ⇔ 6x = 12 ⇔ x = 2. » ; sinon les lignes de l'outil ED, telles quelles ;
- carte « Ensemble de définition » : ED encadré (conclusion de l'outil ED).

Partie 2. Parité (D4). Toute affirmation est confirmée deux fois (principe 0.2) : par SymPy (calcul exact) et par une sonde mpmath
(l'arbre évalué à 30 chiffres, `valeur_mp`) ; au moindre doute, un message clair et aucune conclusion :
- ED non symétrique : un point a ∈ ED avec −a ∉ ED (« −2 ∈ ED, mais 2 ∉ ED »), donc ni paire ni impaire ;
- ED symétrique, f paire ou impaire : f(−x) en chaîne, une étape par ligne, la propriété nommée (« car (−x)² = x² ») ; la chaîne n'est
  écrite que si la parité se lit sur l'arbre (puissances de x, sommes, produits, quotients, exp / ln / √ d'une expression paire) ;
- sinon : « pas impaire » par f(0) ≠ 0 (ou un contre-exemple f(−a) ≠ −f(a)), « pas paire » par un contre-exemple f(−a) ≠ f(a), valeurs
  exactes puis approchées, les deux valeurs arrondies affichées différentes.

Partie 3. Zéros, signe, ordonnée à l'origine (D5), mêmes garde-fous (SymPy et sonde mpmath ; au moindre doute, un message clair) :
- un facteur e^{…} : « e^{…} > 0 pour tout x (une exponentielle est strictement positive) ; il ne s'annule jamais » ;
- f(x) = 0 résolue en chaîne, une étape par ligne, la propriété nommée (« car e^{−2x} > 0 », « produit nul », « mise en évidence »,
  « Somme-Produit ») ; les zéros calculés par le moteur de l'outil ED (`preimage`), valeur exacte puis approchée ; un zéro hors de l'ED est
  rejeté ; une forme que la chaîne ne couvre pas garde les lignes de l'outil ED ; zéros non exacts ou non calculés : message, pas de tableau ;
- sans zéro et de signe constant : « Donc f n'a pas de zéro et f(x) > 0 sur ED » ; sinon le tableau de signes de f, construit par la
  machinerie R7 du tableau de f′ (`derivee_variations.tableau_signes`) ;
- f(0) exact puis approché, et le point (0 ; f(0)) ; « 0 ∉ ED : le graphe ne coupe pas l'axe des y ».
"""
import re
from decimal import Decimal, ROUND_HALF_UP, localcontext
from fractions import Fraction as F
from math import gcd, isqrt

from noyau import (X, E, Nb, Neg, Fn, Op, Num, tex, ptex, qtex, decomposer, deg, pn, pmul, evaluer, conditions, valeur_constante,
                   sans_x, fusion, points, proche, preimage, aplatir, en_sympy_reel, charger_sympy, SYMPY, NonPrisEnCharge, ErreurSaisie)
import sortie as so
import resoudre_ed

__all__ = ["cartes_domaine", "cartes_parite", "cartes_zeros_signe", "mise_en_forme", "resolution_denominateur"]

AUCUNE_CONDITION = "Ni logarithme, ni dénominateur, ni racine : aucune condition."     # phrase de l'outil ED (en-tête)
POINTS_DE_CONTROLE = (-2.7, -0.6, 0.35, 1.45, 3.2)                                    # sondes numériques (garde-fou)


# ---------------------------------------------------------------------------------------------------------------------------
# Polynômes écrits développés
# ---------------------------------------------------------------------------------------------------------------------------
def polynome_ecrit(A):
    """Coefficients (Fraction, du degré 0 au plus haut) du polynôme A quand A est écrit développé (tex(A) = son écriture réduite, à
    coefficients entiers) ; None sinon (produit, fraction, coefficient non entier, autre fonction)."""
    try:
        d = decomposer(A)                           # ('x', R) si A est rationnelle en x ; ('t', …) si A dépend de ln, e^…, √…
    except (NonPrisEnCharge, ErreurSaisie, ZeroDivisionError):
        return None
    if d[0] != "x":
        return None
    R = d[1]
    if deg(R[1]) != 0 or R[1][0] == 0:
        return None
    P = pn([F(c) / R[1][0] for c in R[0]])
    if any(c.denominator != 1 for c in P) or ptex(P, "x") != tex(A):
        return None
    return P


def _proches(a, b):
    return a is not None and b is not None and abs(a - b) <= 1e-9 * (1 + abs(a) + abs(b))


def _accord_numerique(A, valeur):
    """Garde-fou numérique : A et l'écriture proposée (fonction float → float) ont la même valeur aux points de contrôle."""
    return all(_proches(evaluer(A, x), valeur(x)) for x in POINTS_DE_CONTROLE)


# ---------------------------------------------------------------------------------------------------------------------------
# Carte « Mise en forme » (D1)
# ---------------------------------------------------------------------------------------------------------------------------
def _facteur_tex(r):
    """(x − r) pour une racine entière r."""
    return "(" + ptex([-r, F(1)], "x") + ")"


def _factoriser(P):
    """P = c·xᵏ·∏ facteurs (polynômes) par les méthodes du cours, avec les lignes de la chaîne : (lignes, c, k, facteurs), ou None
    quand rien ne se factorise (ou si le garde-fou exact refuse : le produit développé doit redonner P)."""
    P = pn(P)
    if deg(P) < 1 or P[-1] <= 0:
        return None
    k = next(i for i, a in enumerate(P) if a != 0)
    c = 0
    for a in P:
        c = gcd(c, int(a))
    c = F(c)
    Q = [a / c for a in P[k:]]                      # P = c·xᵏ·Q
    devant = ("" if c == 1 else qtex(c)) + ("" if k == 0 else ("x" if k == 1 else f"x^{{{k}}}"))
    lignes = []
    if devant and sum(1 for a in P if a != 0) > 1:
        lignes.append((devant + "(" + ptex(Q, "x") + ")", "mise en évidence"))
    facteurs = [Q]                                  # P = c·xᵏ·(produit des facteurs)
    if deg(Q) == 2 and Q[2] == 1:
        s, p = -Q[1], Q[0]                          # x² − s·x + p : deux nombres de somme s et de produit p
        delta = s * s - 4 * p
        if delta > 0 and delta.denominator == 1 and isqrt(int(delta)) ** 2 == delta:
            r1, r2 = (s - isqrt(int(delta))) / 2, (s + isqrt(int(delta))) / 2
            if r1.denominator == 1 and r2.denominator == 1:
                facteurs = [[-r1, F(1)], [-r2, F(1)]]
                lignes.append((devant + _facteur_tex(r1) + _facteur_tex(r2), "Somme-Produit"))
    if not lignes:
        return None
    produit = [F(0)] * k + [c]                      # garde-fou exact : le produit développé redonne P
    for h in facteurs:
        produit = pmul(produit, h)
    if pn(produit) != P:
        return None
    return lignes, c, k, facteurs


def factorisation(P):
    """Factorisation d'un polynôme à coefficients entiers, coefficient dominant positif, avec les méthodes du cours :
    mise en évidence de c·xᵏ (c = pgcd des coefficients), puis Somme-Produit pour un trinôme unitaire à deux racines entières
    distinctes (facteurs rangés par racine croissante : (x + 2)(x − 1)).
    Résultat : ([(écriture, méthode)], écriture finale, valeur) : les lignes de la chaîne (vide si rien ne se factorise) et la valeur de
    l'écriture finale calculée à partir de ses facteurs (fonction float → float, pour la sonde numérique) ; None quand rien ne se factorise."""
    P = pn(P)
    r = _factoriser(P)
    if r is None:
        return [], ptex(P, "x"), None
    lignes, c, k, facteurs = r
    flottants = [[float(a) for a in h] for h in facteurs]

    def valeur(x):
        v = float(c) * x ** k
        for h in flottants:
            v *= sum(a * x ** i for i, a in enumerate(h))
        return v
    return lignes, lignes[-1][0], valeur


def mise_en_forme(f):
    """Carte « Mise en forme » (D1) ou None : f = e^{g}, g = haut / bas, haut et bas polynômes de degré ≥ 1 écrits développés ;
    une ligne par méthode, la méthode entre parenthèses (R3), puis g(x) nommé avec le haut et le bas factorisés."""
    if not (isinstance(f, Fn) and f.nom == "exp" and isinstance(f.a, Op) and f.a.op == "/"):
        return None
    haut, bas = f.a.a, f.a.b
    ecritures, blocs = [], []
    for A in (haut, bas):
        P = polynome_ecrit(A)
        if P is None or deg(P) < 1:
            return None
        lignes, finale, valeur = factorisation(P)
        if lignes and not _accord_numerique(A, valeur):
            lignes, finale = [], tex(A)                              # sonde en désaccord : la ligne n'est pas écrite
        for i, (ecriture, methode) in enumerate(lignes):
            gauche = tex(A) if i == 0 else ""
            blocs.append(so.texte(f"\\({gauche} = {ecriture}\\) ({methode})", style="etape"))
        ecritures.append(finale)
    if not blocs:
        return None
    blocs.append(so.texte(f"On note \\(g(x) = \\dfrac{{{ecritures[0]}}}{{{ecritures[1]}}}\\), donc \\(f(x) = e^{{g(x)}}\\).", style="etape"))
    return so.carte("Mise en forme", blocs)


# ---------------------------------------------------------------------------------------------------------------------------
# Conditions (D3)
# ---------------------------------------------------------------------------------------------------------------------------
def _racine_tex(q):
    """√q écrit exactement (q rationnel > 0) : q carré d'un rationnel → ce rationnel ; q entier → k√m (m sans facteur carré) ;
    None sinon (la condition garde alors la rédaction de l'outil ED)."""
    n, d = q.numerator, q.denominator
    if isqrt(n) ** 2 == n and isqrt(d) ** 2 == d:
        return qtex(F(isqrt(n), isqrt(d)))
    if d != 1:
        return None
    k, m = 1, n
    for p in range(2, isqrt(n) + 1):
        while m % (p * p) == 0:
            m //= p * p
            k *= p
    return ("" if k == 1 else str(k)) + f"\\sqrt{{{m}}}"


def resolution_denominateur(A):
    """Chaîne courte de « A = 0 » (D3) pour un dénominateur A écrit développé, affine ou de la forme ax² + c (c/a < 0) :
    (membres de la chaîne, [(écriture de la racine, valeur flottante)]), ou None (autre forme : rédaction de l'outil ED)."""
    P = polynome_ecrit(A)
    if P is None or P == [F(0), F(1)]:              # x = 0 : la condition « x ≠ 0 » est déjà la solution
        return None
    return resolution_polynome(P)


def resolution_polynome(P):
    """Chaîne courte de « P = 0 » pour un polynôme P (coefficients, du degré 0 au plus haut) affine ou de la forme ax² + c (c/a < 0) :
    (membres de la chaîne, [(écriture de la racine, valeur flottante)]), ou None."""
    membres = [ptex(P, "x") + " = 0"]
    if deg(P) == 1:
        b, a = P
        if a != 1 and b != 0:
            membres.append(f"{ptex([F(0), a], 'x')} = {qtex(-b)}")
        racine = -b / a
        membres.append(f"x = {qtex(racine)}")
        return membres, [(qtex(racine), float(racine))]
    if deg(P) == 2 and P[1] == 0:
        c, _, a = P
        q = -c / a
        if q <= 0:
            return None
        s = _racine_tex(q)
        if s is None:
            return None
        if a != 1:
            membres.append(f"{ptex([F(0), F(0), a], 'x')} = {qtex(-c)}")
        membres.append(f"x^{{2}} = {qtex(q)}")
        membres.append(f"x = -{s} \\text{{ ou }} x = {s}")
        v = float(q) ** 0.5
        return membres, [("-" + s, -v), (s, v)]
    return None


def _ensemble_prive_de(racines):
    return r"\mathbb{R} \setminus \left\{" + r" \,;\, ".join(t for t, _ in racines) + r"\right\}"


def blocs_condition(c, A):
    """Les blocs d'une condition (`c` : condition de l'outil ED, `A` : son arbre) : un dénominateur résolu en chaîne courte (D3) quand
    la chaîne existe et que ses deux garde-fous passent (même ensemble que l'outil ED, valeur nulle aux racines) ; sinon les blocs de
    l'outil ED, tels quels."""
    if c["genre"] == "den" and c["resolu"] and A is not None and tex(A) == c["source_tex"]:
        if isinstance(A, X):
            return [so.formule(c["cond_tex"])]
        res = resolution_denominateur(A)
        if res is not None:
            membres, racines = res
            if _ensemble_prive_de(racines) == c["E_tex"] and all(_proches(evaluer(A, v), 0.0) for _, v in racines):
                return [so.formule(c["cond_tex"]), so.texte("On résout \\(" + r" \iff ".join(membres) + "\\).", style="etape")]
    return resoudre_ed.blocs_condition(c)


def cartes_domaine(enonce, analyse):
    """Les cartes de la partie 1 (D1, D3) : la fonction (sans l'ED, établi plus bas), la mise en forme (s'il y a lieu), une carte par
    condition, l'ED encadré. `enonce` : « f(x) = … » (tex) ; `analyse` : (résultat de l'outil ED, arbre, ED), celle que `etudier` a
    utilisée (en cache, aucun nouveau calcul)."""
    res_ed, f, _ = analyse
    cartes = [so.carte("Fonction", [so.formule(enonce)], titre_masque=True)]
    mef = mise_en_forme(f)
    if mef is not None:
        cartes.append(mef)
    arbres = []
    conditions(f, arbres)
    for c in res_ed["conditions"]:
        genre, A = arbres[c["num"] - 1] if c["num"] <= len(arbres) else (None, None)
        cartes.append(so.carte(f"Condition {c['num']}", blocs_condition(c, A if genre == c["genre"] else None), badge=c["titre"],
                               detail=c.get("detail")))
    fin = [] if res_ed["conditions"] else [so.texte(AUCUNE_CONDITION, style="etape")]
    cartes.append(so.carte("Ensemble de définition", fin + resoudre_ed.blocs_ensemble(res_ed)))
    return cartes


# ---------------------------------------------------------------------------------------------------------------------------
# Partie 2. Parité (D4)
# ---------------------------------------------------------------------------------------------------------------------------
CANDIDATS = (F(1), F(2), F(1, 2), F(3), F(4), F(1, 3), F(5))              # a des contre-exemples (D4 : 1, 2, 1/2, 3…)
POINTS_SONDE = ("0.05", "0.13", "0.23", "0.37", "0.52", "0.64", "0.81", "0.93", "1.3", "1.9", "2.71", "3.6", "4.2", "5.5", "7.9",
                "12.3")                                                    # la sonde compare f(−x) et f(x) en ±x (x ∈ ED)
CHIFFRES = 30                                                              # précision de la sonde mpmath
EGAL, DIFFERENT = "1e-20", "1e-8"                                          # écarts relatifs : égal / clairement différent
LONGUEUR_MAX = 60                                                          # écriture exacte plus longue : a suivant

DOUTE = "La parité de f n'a pas pu être établie avec certitude : l'outil ne conclut pas."
NON_REDIGEE = "Le calcul de f(−x) n'a pas pu être rédigé par l'outil : la parité n'est pas traitée."
SANS_CONTRE_EXEMPLE = "Aucun contre-exemple simple n'a été trouvé (x = 1, 2, 1/2, 3…) : la parité n'est pas traitée."
PAIRE, IMPAIRE, NI = "Donc <b>f est paire</b>.", "Donc <b>f est impaire</b>.", "Donc <b>f n'est ni paire ni impaire</b>."
SYMETRIQUE = "ED est symétrique par rapport à 0."

MOINS_X = Nb(F(0), r"\left(-x\right)")      # « (−x) » pour ÉCRIRE la substitution (jamais évalué : sa valeur n'est pas −x)


class Doute(Exception):
    """Un garde-fou refuse : SymPy et la sonde ne confirment pas tous deux (la partie affiche alors un message clair)."""


def _ligne(html):
    return so.texte(html, style="etape")


def _message(texte):
    return [so.carte("Parité", [_ligne(texte)], titre_masque=True)]


def nombre(q):
    """L'arbre d'un rationnel : 3, 1/2, −(2)."""
    q = F(q)
    return Nb(q) if q >= 0 else Neg(Nb(-q))


def substituer(n, par):
    """L'arbre n où x est remplacé par l'arbre `par`."""
    if isinstance(n, X):
        return par
    if isinstance(n, (Nb, E)):
        return n
    if isinstance(n, Neg):
        return Neg(substituer(n.a, par))
    if isinstance(n, Fn):
        return Fn(n.nom, substituer(n.a, par))
    return Op(n.op, substituer(n.a, par), substituer(n.b, par))


def plier(n):
    """Calcule les morceaux rationnels d'un arbre sans x (f(1) de (x² − 6)e^{−2x} : (1² − 6)e^{−2·1} devient −5e^{−2}) ; e⁰ = 1,
    e¹ = e, ln(1) = 0, ln(e) = 1, facteurs 1 et termes 0 retirés. L'égalité avec f(a) est vérifiée par SymPy et par la sonde."""
    v = valeur_constante(n)
    if v is not None:
        return nombre(v)
    if isinstance(n, (Nb, E, X)):
        return n
    if isinstance(n, Neg):
        a = plier(n.a)
        return a.a if isinstance(a, Neg) else Neg(a)
    if isinstance(n, Fn):
        a = plier(n.a)
        va = valeur_constante(a)
        if n.nom == "exp" and va in (0, 1):
            return Nb(1) if va == 0 else E()
        if n.nom == "ln" and (va == 1 or isinstance(a, E)):
            return Nb(0) if va == 1 else Nb(1)
        return Fn(n.nom, a)
    a, b = plier(n.a), plier(n.b)
    va, vb = valeur_constante(a), valeur_constante(b)
    if n.op == "*":
        if va == 0 or vb == 0:
            return Nb(0)
        if va in (1, -1):
            return b if va == 1 else plier(Neg(b))
        if vb in (1, -1):
            return a if vb == 1 else plier(Neg(a))
    elif n.op == "/":
        if va == 0:
            return Nb(0)
        if vb in (1, -1):
            return a if vb == 1 else plier(Neg(a))
    elif n.op in "+-":
        if vb == 0:
            return a
        if va == 0:
            return b if n.op == "+" else plier(Neg(b))
    elif n.op == "^":
        if vb == 1:
            return a
        if va == 1 or (va == 0 and vb is not None and vb > 0):            # 1^p = 1, 0^p = 0 (p > 0) : ∛(0²) = 0
            return Nb(va)
        if isinstance(a, E):
            return Fn("exp", b)
    m = Op(n.op, a, b)
    v = valeur_constante(m)                     # 6 − e⁰ : rationnel une fois e⁰ calculé
    return m if v is None else nombre(v)


def valeur_mp(n, x):
    """Sonde : valeur de l'arbre n en x (mpf) avec mpmath, à la précision courante ; None hors de l'ensemble de définition. Mêmes
    conventions que le cours (et que `evaluer`, sans ses arrondis de flottants) : ln u (u > 0), √u (u ≥ 0), dénominateur ≠ 0,
    u^(p/q) constant : racine réelle si q est impair, u ≥ 0 si q est pair ; exposant non constant : u > 0."""
    import mpmath
    mp = mpmath.mp
    if isinstance(n, Nb):
        return mp.mpf(n.v.numerator) / n.v.denominator
    if isinstance(n, X):
        return x
    if isinstance(n, E):
        return mp.e
    if isinstance(n, Neg):
        a = valeur_mp(n.a, x)
        return None if a is None else -a
    if isinstance(n, Fn):
        a = valeur_mp(n.a, x)
        if a is None:
            return None
        if n.nom == "ln":
            return mp.log(a) if a > 0 else None
        if n.nom == "sqrt":
            return mp.sqrt(a) if a >= 0 else None
        return mp.exp(a)
    a = valeur_mp(n.a, x)
    if a is None:
        return None
    if n.op == "^":
        e = valeur_constante(n.b)
        if e is None:
            b = valeur_mp(n.b, x)
            return None if (b is None or a <= 0) else mp.exp(b * mp.log(a))
        if e == 0:
            return mp.mpf(1)
        if a == 0:
            return mp.mpf(0) if e > 0 else None
        if e.denominator == 1:
            return a ** int(e)
        if a < 0:
            if e.denominator % 2 == 0:
                return None
            r = (-a) ** (mp.mpf(e.numerator) / e.denominator)
            return -r if e.numerator % 2 else r
        return a ** (mp.mpf(e.numerator) / e.denominator)
    b = valeur_mp(n.b, x)
    if b is None:
        return None
    if n.op == "+":
        return a + b
    if n.op == "-":
        return a - b
    if n.op == "*":
        return a * b
    return None if b == 0 else a / b


# ---------- ensemble de définition : symétrie, appartenance (exactes) ----------
def _sympy_de(borne, sp):
    return sp.sympify(borne.py, locals={"sqrt": sp.sqrt, "exp": sp.exp, "log": sp.log})


def _signe_ecart(q, borne, sp):
    """Signe exact de q − borne (q rationnel) : −1, 0 ou 1 ; Doute si la borne est approchée ou si SymPy ne tranche pas."""
    if borne.approx:
        raise Doute()
    if borne.q is not None:
        d = q - borne.q
        return (d > 0) - (d < 0)
    d = sp.Rational(q.numerator, q.denominator) - _sympy_de(borne, sp)
    if d.is_zero:
        return 0
    if d.is_positive or d.is_negative:
        return 1 if d.is_positive else -1
    raise Doute()


def dans_ed(ivs, q, sp):
    """q ∈ ED, décidé exactement (ivs : intervalles de l'ED, après fusion)."""
    for iv in ivs:
        if iv.lo is not None:
            s = _signe_ecart(q, iv.lo, sp)
            if s < 0 or (s == 0 and not iv.lf):
                continue
        if iv.hi is not None:
            s = _signe_ecart(q, iv.hi, sp)
            if s > 0 or (s == 0 and not iv.hf):
                continue
        return True
    return False


def _opposees(p, r, sp):
    """p = −r (bornes finies), décidé exactement."""
    if p.approx or r.approx:
        raise Doute()
    if p.q is not None and r.q is not None:
        return p.q == -r.q
    s = sp.simplify(_sympy_de(p, sp) + _sympy_de(r, sp))
    if s.is_zero:
        return True
    if s.is_zero is False:
        return False
    raise Doute()


def ed_symetrique(ivs, sp):
    """L'ED est symétrique par rapport à 0 : la liste de ses intervalles est sa propre image par x ↦ −x."""
    if len(ivs) == 0:
        raise Doute()
    for iv, im in zip(ivs, reversed(ivs)):            # l'image de iv = [−im.hi ; −im.lo] doit être iv
        for b, cb, c, cc in ((iv.lo, iv.lf, im.hi, im.hf), (iv.hi, iv.hf, im.lo, im.lf)):
            if (b is None) != (c is None):
                return False
            if b is not None and (cb != cc or not _opposees(b, c, sp)):
                return False
    return True


def point_non_symetrique(ivs, sp):
    """a ∈ ED avec −a ∉ ED : d'abord le symétrique d'une borne rationnelle (Ex7 : −2, car 2 ∉ ED), sinon 1, 2, 1/2, 3… ; None sinon."""
    bornes = sorted({b.q for iv in ivs for b in (iv.lo, iv.hi) if b is not None and b.q is not None}, key=lambda q: (abs(q), q))
    candidats = [c for p in bornes for c in (-p, p)] + [c for a in CANDIDATS for c in (a, -a)]
    for a in candidats:
        if dans_ed(ivs, a, sp) and not dans_ed(ivs, -a, sp):
            return a
    return None


# ---------- sonde : f paire, impaire ou ni l'une ni l'autre ----------
def classer_par_la_sonde(f, mpmath):
    """'paire', 'impaire' ou 'ni' d'après f(−x) et f(x) aux points de la sonde (ED symétrique) ; Doute si les points ne suffisent pas,
    si f est définie en x mais pas en −x, ou si un écart n'est ni nul ni clairement non nul."""
    mp = mpmath.mp
    egal, diff = mp.mpf(EGAL), mp.mpf(DIFFERENT)
    pair, impair, n = [], [], 0
    for t in POINTS_SONDE:
        x = mp.mpf(t)
        u, v = valeur_mp(f, x), valeur_mp(f, -x)
        if (u is None) != (v is None):
            raise Doute()
        if u is None:
            continue
        n += 1
        echelle = 1 + abs(u) + abs(v)
        pair.append(abs(v - u) / echelle)
        impair.append(abs(v + u) / echelle)
    if n < 3:
        raise Doute()
    est_paire, est_impaire = max(pair) <= egal, max(impair) <= egal
    if est_paire != est_impaire:
        return "paire" if est_paire else "impaire"
    if max(pair) > diff and max(impair) > diff:
        return "ni"
    raise Doute()


def _verifier_egalite(T, cible, cible_sp, sp, mpmath):
    """Garde-fou d'une ligne de la chaîne : l'arbre T vaut `cible` (arbre de f(−x), en fonction de x) exactement (SymPy) et à la sonde."""
    d = en_sympy_reel(T) - cible_sp
    if not (d == 0 or sp.simplify(d) == 0):
        raise Doute()
    mp = mpmath.mp
    for t in POINTS_SONDE:
        x = mp.mpf(t)
        for s in (x, -x):
            u, v = valeur_mp(T, s), valeur_mp(cible, s)
            if (u is None) != (v is None) or (u is not None and abs(u - v) > mp.mpf(EGAL) * (1 + abs(v))):
                raise Doute()


# ---------- chaîne f(−x) (règle 2) ----------
def parite_lue(n):
    """Parité lisible sur l'arbre : 1 (paire), −1 (impaire), None (pas lisible). x est impaire, une constante paire ; une somme de
    termes de même parité, un produit ou un quotient (règle des signes) ; x^(p/q) (q impair, p ≠ 1 si q > 1) a la parité de p ;
    une puissance, une exponentielle, un ln ou une racine d'une expression paire est paire ; rien d'autre (exposant avec x…)."""
    if sans_x(n):
        return 1
    if isinstance(n, X):
        return -1
    if isinstance(n, Neg):
        return parite_lue(n.a)
    if isinstance(n, Fn):
        return 1 if parite_lue(n.a) == 1 else None
    if n.op == "^":
        e = valeur_constante(n.b) if sans_x(n.b) else None
        if e is None:
            return None
        if isinstance(n.a, X):
            if e.denominator % 2 == 0 or (e.numerator == 1 and e.denominator > 1):
                return None
            return 1 if e.numerator % 2 == 0 else -1
        return 1 if parite_lue(n.a) == 1 else None
    pa, pb = parite_lue(n.a), parite_lue(n.b)
    if pa is None or pb is None:
        return None
    if n.op in "+-":
        return pa if pa == pb else None
    return pa * pb


def proprietes(n):
    """Les propriétés qui mènent de f(−x) à la forme simplifiée : « (−x)^k = x^k » (k pair) ou « (−x)^k = −x^k » (k impair) pour chaque
    puissance de x, et la règle des signes pour un x seul (hors d'une puissance)."""
    faits, seul = [], [False]

    def rec(m):
        if isinstance(m, Op) and m.op == "^" and isinstance(m.a, X):
            p = valeur_constante(m.b).numerator
            fait = tex(Op("^", MOINS_X, Nb(p))) + " = " + ("" if p % 2 == 0 else "-") + tex(Op("^", X(), Nb(p)))
            if fait not in faits:
                faits.append(fait)
        elif isinstance(m, X):
            seul[0] = True
        elif isinstance(m, (Neg, Fn)):
            rec(m.a)
        elif isinstance(m, Op):
            rec(m.a)
            rec(m.b)
    rec(n)
    return faits, seul[0]


def _termes(n, s, out):
    if isinstance(n, Op) and n.op in "+-":
        _termes(n.a, s, out)
        _termes(n.b, s if n.op == "+" else -s, out)
    elif isinstance(n, Neg):
        _termes(n.a, -s, out)
    else:
        out.append((s, n))
    return out


def _somme(termes):
    s, t = termes[0]
    out = t if s > 0 else Neg(t)
    for s, t in termes[1:]:
        out = Op("+" if s > 0 else "-", out, t)
    return out


def chaine_f_moins_x(f, p):
    """Lignes (html) de la chaîne f(−x) = … = ±f(x) pour f de parité p (1 ou −1, lue sur l'arbre), avec les arbres à vérifier :
    [(html, arbre ou None)]. Substitution, forme simplifiée (propriétés nommées), pour une somme impaire −(…), puis ±f(x)."""
    lignes = [(rf"\(f(-x) = {tex(substituer(f, MOINS_X))}\) (on remplace x par −x)", None)]
    faits, seul = proprietes(f)
    morceaux = (["car " + " et ".join(rf"\({fait}\)" for fait in faits)] if faits else []) + (["règle des signes"] if seul or p < 0 else [])
    raison = " (" + " ; ".join(morceaux) + ")" if morceaux else ""
    if p > 0:
        if tex(f) != tex(substituer(f, MOINS_X)):
            lignes.append((rf"\( = {tex(f)}\){raison}", f))
        lignes.append((r"\( = f(x)\)", None))
        return lignes
    if isinstance(f, Op) and f.op in "+-":
        oppose = _somme([(-s, t) for s, t in _termes(f, 1, [])])
        lignes.append((rf"\( = {tex(oppose)}\){raison}", oppose))
        lignes.append((rf"\( = {tex(Neg(f))}\) (mise en évidence de −1)", Neg(f)))
    else:
        oppose = f.a if isinstance(f, Neg) else Neg(f)
        lignes.append((rf"\( = {tex(oppose)}\){raison}", oppose))
    lignes.append((r"\( = -f(x)\)", None))
    return lignes


# ---------- valeurs de f en un point (règle 3) ----------
def arrondi(d):
    """Valeur arrondie affichée (decisions.md §2) d'un Decimal : 2 décimales si |d| ≥ 0,01, 2 chiffres significatifs si
    10⁻³ ≤ |d| < 0,01 ; None hors de [10⁻³ ; 1000[ (notation scientifique et séparateur des milliers : questions ouvertes)."""
    if d == 0:
        return Decimal(0)
    if not Decimal("0.001") <= abs(d) < 1000:
        return None
    q = Decimal("0.01") if abs(d) >= Decimal("0.01") else Decimal(1).scaleb(d.adjusted() - 1)
    return d.quantize(q, rounding=ROUND_HALF_UP)


def ecrire_decimal(d):
    """−0,68 (virgule décimale, signe moins typographique) ; l'opposé de 0 s'écrit 0."""
    return format(d if d != 0 else Decimal(0), "f").replace(".", ",").replace("-", "−")


def valeur_verifiee(f, fe, a, sp, mpmath):
    """f(a) pour a rationnel de l'ED : (écriture exacte tex, valeur SymPy, Decimal à 30 chiffres), ou None si un garde-fou refuse
    (valeur non réelle ou infinie, désaccord entre l'écriture, la valeur SymPy et la sonde)."""
    T = plier(substituer(f, nombre(a)))
    V = fe.subs(SYMPY["x"], sp.Rational(a.numerator, a.denominator))
    if V.has(sp.zoo, sp.nan, sp.oo, -sp.oo) or V.is_real is not True:
        return None
    d = en_sympy_reel(T) - V
    if not (d == 0 or sp.simplify(d) == 0):
        return None
    mp = mpmath.mp
    reference = mp.mpf(str(sp.N(V, CHIFFRES + 5)))
    for sonde in (valeur_mp(f, mp.mpf(a.numerator) / a.denominator), valeur_mp(T, mp.mpf(0))):
        if sonde is None or abs(sonde - reference) > mp.mpf(EGAL) * (1 + abs(reference)):
            return None
    with localcontext() as ctx:
        ctx.prec = 50
        if V.is_Rational:
            dec = Decimal(int(V.p)) / Decimal(int(V.q))
        else:
            dec = Decimal(mpmath.nstr(reference, CHIFFRES, min_fixed=-mp.inf, max_fixed=mp.inf))
    return tex(T), V, dec


def valeur_en(f, fe, a, sp, mpmath):
    """f(a) pour a rationnel de l'ED : {tex (écriture exacte), entier (bool), arrondi (Decimal), approx (texte ou None)}, ou None si
    un garde-fou refuse (écriture trop longue, désaccord entre l'écriture, la valeur SymPy et la sonde, valeur non affichable)."""
    if len(tex(plier(substituer(f, nombre(a))))) > LONGUEUR_MAX:
        return None
    v = valeur_verifiee(f, fe, a, sp, mpmath)
    if v is None:
        return None
    ecrit, V, dec = v
    entier = bool(V.is_Integer)
    r = (dec if abs(dec) < 1000 else None) if entier else arrondi(dec)
    if r is None:
        return None
    return {"tex": ecrit, "entier": entier, "arrondi": r, "approx": None if entier else ecrire_decimal(r)}


def _egalite(nom, v):
    """« f(1) = −5e^{−2} ≈ −0,68 » (entier exact : sans « ≈ »)."""
    return rf"\({nom} = {v['tex']}\)" + ("" if v["approx"] is None else f" ≈ {v['approx']}")


def contre_exemple(f, fe, ivs, differe, sp, mpmath):
    """Premier a de CANDIDATS avec ±a ∈ ED, f(a) et f(−a) écrits et vérifiés, et `differe(f(a), f(−a))` vrai sur les valeurs
    arrondies affichées : (a, f(a), f(−a)) ou None."""
    for a in CANDIDATS:
        if not (dans_ed(ivs, a, sp) and dans_ed(ivs, -a, sp)):
            continue
        va, vm = valeur_en(f, fe, a, sp, mpmath), valeur_en(f, fe, -a, sp, mpmath)
        if va is not None and vm is not None and differe(va["arrondi"], vm["arrondi"]):
            return a, va, vm
    return None


def _pas_impaire(f, fe, ivs, sp, mpmath):
    """Blocs de la carte « Pas impaire » : f(0) ≠ 0 si 0 ∈ ED (D4), sinon un contre-exemple f(−a) ≠ −f(a) ; None si rien n'est sûr."""
    if dans_ed(ivs, F(0), sp):
        v0 = valeur_en(f, fe, F(0), sp, mpmath)
        if v0 is not None and v0["arrondi"] != 0:
            approx = "" if v0["approx"] is None else f" (≈ {v0['approx']})"
            return [_ligne(rf"\(f(0) = {v0['tex']} \neq 0\){approx}"),
                    _ligne(r"Une fonction impaire vérifie \(f(0) = 0\) : f n'est pas impaire.")]
    ce = contre_exemple(f, fe, ivs, lambda u, v: -u != v, sp, mpmath)
    if ce is None:
        return None
    a, va, vm = ce
    ta, tm = qtex(a), qtex(-a)
    oppose = -va["arrondi"] if va["arrondi"] != 0 else va["arrondi"]
    moins = (rf"\(-f({ta}) = {ecrire_decimal(oppose).replace('−', '-')}\)" if va["entier"]
             else rf"\(-f({ta})\) ≈ {ecrire_decimal(oppose)}")
    return [_ligne(_egalite(f"f({ta})", va) + ", donc " + moins), _ligne(_egalite(f"f({tm})", vm)),
            _ligne(rf"\(f({tm}) \neq -f({ta})\) : f n'est pas impaire.")]


def _pas_paire(f, fe, ivs, sp, mpmath):
    ce = contre_exemple(f, fe, ivs, lambda u, v: u != v, sp, mpmath)
    if ce is None:
        return None
    a, va, vm = ce
    ta, tm = qtex(a), qtex(-a)
    return [_ligne(_egalite(f"f({ta})", va)), _ligne(_egalite(f"f({tm})", vm)), _ligne(rf"\(f({tm}) \neq f({ta})\) : f n'est pas paire.")]


# ---------- les cartes ----------
def _cartes_parite(f, ivs, sp, mpmath):
    if not ed_symetrique(ivs, sp):
        a = point_non_symetrique(ivs, sp)
        if a is None:
            raise Doute()
        x = mpmath.mp.mpf(a.numerator) / a.denominator
        if valeur_mp(f, x) is None or valeur_mp(f, -x) is not None:          # sonde : f(a) existe, f(−a) n'existe pas
            raise Doute()
        return [so.carte("Symétrie de l'ED", [
            _ligne(rf"\({qtex(a)} \in ED\), mais \({qtex(-a)} \notin ED\) : ED n'est pas symétrique par rapport à 0."), _ligne(NI)])]
    cartes = [so.carte("Symétrie de l'ED", [_ligne(SYMETRIQUE)])]
    genre = classer_par_la_sonde(f, mpmath)
    fe = en_sympy_reel(f)
    if genre in ("paire", "impaire"):
        p = 1 if genre == "paire" else -1
        fm = fe.subs(SYMPY["x"], -SYMPY["x"])
        d = fm - p * fe
        if not (d == 0 or sp.simplify(d) == 0):                                # SymPy ne confirme pas la sonde
            raise Doute()
        if parite_lue(f) != p:
            return cartes + _message(NON_REDIGEE)
        lignes = chaine_f_moins_x(f, p)
        cible = substituer(f, Neg(X()))
        for _, T in lignes:
            if T is not None:
                _verifier_egalite(T, cible, fm, sp, mpmath)
        blocs = [_ligne(html) for html, _ in lignes] + [_ligne(PAIRE if p > 0 else IMPAIRE)]
        return cartes + [so.carte("Calcul de f(−x)", blocs)]
    impaire, paire = _pas_impaire(f, fe, ivs, sp, mpmath), _pas_paire(f, fe, ivs, sp, mpmath)
    if impaire is None or paire is None:
        return cartes + _message(SANS_CONTRE_EXEMPLE)
    return cartes + [so.carte("Pas impaire", impaire), so.carte("Pas paire", paire + [_ligne(NI)])]


def cartes_parite(analyse):
    """Les cartes de la partie 2 (D4) ; `analyse` : (résultat de l'outil ED, arbre, ED), celle de `etudier` (en cache). Sans SymPy ou
    mpmath, ou si un garde-fou doute : un message clair, aucune conclusion (principe 0.2)."""
    _, f, ED = analyse
    sp = charger_sympy()
    try:
        import mpmath
    except ImportError:
        mpmath = None
    if sp is None or mpmath is None:
        return _message(DOUTE)
    try:
        with mpmath.workdps(CHIFFRES):
            return _cartes_parite(f, fusion(ED), sp, mpmath)
    except Exception:                       # Doute, ou SymPy / mpmath en échec : rien plutôt qu'une affirmation non confirmée
        return _message(DOUTE)


# ---------------------------------------------------------------------------------------------------------------------------
# Partie 3. Zéros, signe, ordonnée à l'origine (D5)
# ---------------------------------------------------------------------------------------------------------------------------
DOUTE_SIGNE = "Le signe de f n'a pas pu être établi avec certitude : l'outil ne conclut pas."
ZEROS_NON_EXACTS = "Les zéros de f ne se calculent pas exactement : l'outil ne dresse pas le tableau de signes de f."
ZEROS_NON_TRAITES = "Les zéros de f n'ont pas pu être calculés par l'outil : le signe de f n'est pas traité."
DOUTE_F0 = "L'ordonnée à l'origine n'a pas pu être établie avec certitude : l'outil ne conclut pas."
NUMERATEUR_CONSTANT = "Le numérateur de f est une constante non nulle : f n'a pas de zéro."
PAS_DE_ZERO = "Donc f n'a pas de zéro."
NE_COUPE_PAS = r"\(0 \notin ED\) : le graphe ne coupe pas l'axe des y."
SONDES_RELATIVES = ("0.001", "0.01", "0.1", "0.3", "0.5", "0.7", "0.9", "0.99", "0.999")    # sonde du signe sur un intervalle borné
SONDES_INFINIES = ("0.001", "0.01", "0.1", "1", "10", "100")                               # écarts à la borne d'un intervalle infini
NUL = "1e-20"                                                                               # |f(z)| à la sonde : zéro


class NonTraite(Exception):
    """Les zéros de f ne sont pas calculés par l'outil (message : ZEROS_NON_TRAITES ou ZEROS_NON_EXACTS)."""
    def __init__(self, message):
        super().__init__(message)
        self.message = message


def est_exponentielle(h):
    """e^{u} (u non constant) : strictement positive pour tout x où u est définie."""
    return (isinstance(h, Fn) and h.nom == "exp" and not sans_x(h.a)) or \
        (isinstance(h, Op) and h.op == "^" and isinstance(h.a, E) and not sans_x(h.b))


def _produit(facteurs):
    """L'arbre de ∏ hᵏ (k > 0)."""
    out = None
    for h, k in facteurs:
        t = h if k == 1 else Op("^", h, Nb(k))
        out = t if out is None else Op("*", out, t)
    return out


# ---------- zéros d'un facteur : valeurs (outil ED) et chaîne d'équivalences ----------
def zeros_facteur(h):
    """Zéros de h (h = 0) par le moteur de l'outil ED : ([Num] exacts, isolés, croissants, lignes de l'outil ED). NonTraite si le moteur
    ne résout pas, si un zéro n'est connu qu'en valeur approchée ou si h s'annule sur un intervalle."""
    items = []
    try:
        Z = preimage(h, points([Num.rat(0)]), items)
    except Exception:
        raise NonTraite(ZEROS_NON_TRAITES)
    zeros = []
    for iv in fusion(Z):
        if iv.lo is None or iv.hi is None or not (iv.lf and iv.hf and proche(iv.lo.val, iv.hi.val)):
            raise NonTraite(ZEROS_NON_TRAITES)
        if iv.lo.approx:
            raise NonTraite(ZEROS_NON_EXACTS)
        zeros.append(iv.lo)
    return zeros, items


def _etapes_items(h, items):
    """Chaîne lue dans les lignes de l'outil ED quand chacune est « A ⇔ B (propriété) » et qu'elles s'enchaînent
    (6 − eˣ = 0 ⇔ eˣ = 6 ⇔ x = ln(6)) : [(alternatives, propriété)] ; None sinon."""
    etapes = []
    for it in items:
        m = re.fullmatch(r"\\\((.+?) \\iff (.+?)\\\)(?: \((.+)\))?\.?", it.get("html", ""))
        if not m:
            return None
        a, b, p = m.groups()
        if not etapes:
            if a != tex(h) + " = 0":
                return None
            etapes.append(([a], None))
        elif etapes[-1][0] != [a]:
            return None
        etapes.append((b.split(r" \text{ ou } "), p))
    return etapes or None


def _en_parallele(chaines, propriete):
    """Chaînes de plusieurs facteurs menées ensemble : « h₁ = 0 ou h₂ = 0 (produit nul) ⇔ … », chacune avance d'un pas par ligne."""
    etapes = [([a for ch in chaines for a in ch[0][0]], propriete)]
    for j in range(1, max(len(ch) for ch in chaines)):
        alternatives, proprietes = [], []
        for ch in chaines:
            alt, p = ch[min(j, len(ch) - 1)]
            alternatives += alt
            if j < len(ch) and p and p not in proprietes:
                proprietes.append(p)
        etapes.append((alternatives, " ; ".join(proprietes) or None))
    return etapes


def etapes_polynome(P):
    """Chaîne de « P = 0 » (P écrit développé) : x = 0 ; affine ou ax² + c en chaîne courte (partie 1) ; sinon mise en évidence et
    Somme-Produit (carte « Mise en forme »), produit nul, puis chaque facteur de même. None si P ne se résout pas ainsi."""
    P = pn(P)
    if P == [F(0), F(1)]:
        return [(["x = 0"], None)]
    res = resolution_polynome(P) if deg(P) in (1, 2) else None
    if res is not None:
        membres = res[0]
        return [([membres[0]], None)] + [(m.split(r" \text{ ou } "), None) for m in membres[1:]]
    r = _factoriser(P)
    if r is None:
        return None
    lignes, _, k, facteurs = r
    etapes = [([ptex(P, "x") + " = 0"], None)] + [([e + " = 0"], methode) for e, methode in lignes]
    chaines = ([[(["x = 0"], None)]] if k > 0 else []) + [etapes_polynome(h) for h in facteurs]
    if any(ch is None for ch in chaines):
        return None
    if len(chaines) == 1:
        return etapes + chaines[0][1:]
    return etapes + _en_parallele(chaines, "produit nul")


def etapes_facteur(h, items):
    """Chaîne de « h = 0 » : polynôme (etapes_polynome) ou lignes de l'outil ED enchaînées ; None sinon (l'outil ED rédige)."""
    if isinstance(h, X):
        return [(["x = 0"], None)]
    P = polynome_ecrit(h)
    if P is not None:
        return etapes_polynome(P)
    return _etapes_items(h, items)


# ---------- valeurs exactes (SymPy) et approchées ----------
def _sympy_num(p, sp):
    if p.approx or p.py is None:
        raise Doute()
    return _sympy_de(p, sp)


def _signe_sp(v):
    if v.is_zero:
        return 0
    if v.is_positive:
        return 1
    if v.is_negative:
        return -1
    raise Doute()


def appartient(ivs, v, sp):
    """v (nombre SymPy réel) ∈ ED, décidé exactement ; Doute si une comparaison n'est pas tranchée."""
    for iv in ivs:
        if iv.lo is not None:
            s = _signe_sp(sp.simplify(v - _sympy_num(iv.lo, sp)))
            if s < 0 or (s == 0 and not iv.lf):
                continue
        if iv.hi is not None:
            s = _signe_sp(sp.simplify(v - _sympy_num(iv.hi, sp)))
            if s > 0 or (s == 0 and not iv.hf):
                continue
        return True
    return False


def approchee(v, sp):
    """Valeur approchée affichée d'un nombre SymPy (texte, à écrire après « ≈ »), None pour un entier exact (écrit tel quel) ou une
    valeur sans écriture convenue : decisions.md §2 entre 10⁻³ et 1000 ; R13 sous 10⁻³ et dès 10⁶ (3,162 × 10⁻⁵, notation
    scientifique, question 1 de suivi.md) ; entre 1000 et 10⁶, aucune (séparateur des milliers pas encore tranché pour l'EC)."""
    if v.is_Integer:
        return None
    with localcontext() as ctx:
        ctx.prec = 50
        d = Decimal(str(sp.N(v, CHIFFRES)))
        if Decimal("0.001") <= abs(d) < 1000:
            return ecrire_decimal(arrondi(d))
        if Decimal(1000) <= abs(d) < Decimal(10) ** 6:
            return None
        e = d.adjusted()
        m = (d.scaleb(-e)).quantize(Decimal("0.001"), rounding=ROUND_HALF_UP)
        if abs(m) >= 10:
            e += 1
            m = (d.scaleb(-e)).quantize(Decimal("0.001"), rounding=ROUND_HALF_UP)
    t = format(m, "f")
    t = t[:-4] if t.endswith(".000") else t
    return r"\(" + t.replace(".", "{,}") + r" \times 10^{" + str(e) + r"}\)"


def _avec_approx(texte, v, sp):
    a = approchee(v, sp)
    return texte if a is None else f"{texte} ≈ {a}"


# ---------- confirmation du signe (principe 0.2) ----------
def _rationnel_entre(a, b):
    """Un rationnel simple strictement entre a et b (flottants, a < b, ±∞ permis)."""
    if a == -float("inf") and b == float("inf"):
        return F(0)
    if a == -float("inf"):
        return F(int(b) - 1) if int(b) - 1 < b else F(int(b) - 2)
    if b == float("inf"):
        return F(int(a) + 1) if int(a) + 1 > a else F(int(a) + 2)
    for den in (1, 2, 4, 10, 100, 1000, 10 ** 6):
        q = F(round((a + b) / 2 * den), den)
        if a < q < b:
            return q
    return F((a + b) / 2)


def _sondes(a, b, mp):
    """Points de la sonde dans ]a ; b[ (mpf ; a ou b infinis permis)."""
    if a is None and b is None:
        return [s * mp.mpf(t) for t in SONDES_INFINIES for s in (-1, 1)] + [mp.mpf(0)]
    if a is None:
        return [b - mp.mpf(t) for t in SONDES_INFINIES]
    if b is None:
        return [a + mp.mpf(t) for t in SONDES_INFINIES]
    return [a + (b - a) * mp.mpf(t) for t in SONDES_RELATIVES]


def confirmer_signe(f, fe, crit, cellules, zeros, ivs, sp, mpmath):
    """Garde-fous de la ligne f(x) du tableau (principe 0.2) ; Doute au moindre désaccord :
    - SymPy : les zéros de f sur l'ED (solveset) sont exactement `zeros` ; f(z) = 0 exactement ; sur chaque intervalle de l'ED, le
      signe exact de f en un point rationnel est celui de la case (f est continue sur chaque intervalle de son ED : entre deux zéros
      ou valeurs interdites consécutifs, son signe ne change pas) ; chaque point critique est dans l'ED ou non, exactement ;
    - sonde mpmath (30 chiffres) : f(z) ≈ 0 ; le signe de la case en 9 points de chaque intervalle ; f non définie hors de l'ED."""
    mp, x = mpmath.mp, SYMPY["x"]
    zs = [_sympy_num(z, sp) for z in zeros]
    for z, zsp in zip(zeros, zs):
        if not (fe.subs(x, zsp) == 0 or sp.simplify(fe.subs(x, zsp)) == 0):
            raise Doute()
        v = valeur_mp(f, mp.mpf(str(sp.N(zsp, CHIFFRES + 5))))
        if v is None or abs(v) > mp.mpf(NUL):
            raise Doute()
    S = sp.solveset(fe, x, sp.S.Reals)
    if S == sp.S.EmptySet:
        S = []
    elif not isinstance(S, sp.FiniteSet):
        raise Doute()
    dans = [s for s in S if appartient(ivs, s, sp)]
    if len(dans) != len(zs) or any(not any(sp.simplify(s - z) == 0 for z in zs) for s in dans):
        raise Doute()
    bornes = [None] + [_sympy_num(p, sp) for p in crit] + [None]
    valeurs = [None] + [p.val for p in crit] + [None]
    for i in range(len(crit) + 1):
        case = cellules[2 * i]
        a, b = valeurs[i], valeurs[i + 1]
        milieu = _rationnel_entre(-float("inf") if a is None else a, float("inf") if b is None else b)
        q = sp.Rational(milieu.numerator, milieu.denominator)
        if (bornes[i] is not None and _signe_sp(sp.simplify(q - bornes[i])) <= 0) or \
                (bornes[i + 1] is not None and _signe_sp(sp.simplify(bornes[i + 1] - q)) <= 0):
            raise Doute()
        if case == "x":
            if appartient(ivs, q, sp) or valeur_mp(f, mp.mpf(milieu.numerator) / milieu.denominator) is not None:
                raise Doute()
            continue
        if case not in ("+", "-") or not appartient(ivs, q, sp):
            raise Doute()
        s = 1 if case == "+" else -1
        if _signe_sp(sp.simplify(fe.subs(x, q))) != s:
            raise Doute()
        ma = None if a is None else mp.mpf(str(sp.N(bornes[i], CHIFFRES + 5)))
        mb = None if b is None else mp.mpf(str(sp.N(bornes[i + 1], CHIFFRES + 5)))
        for t in _sondes(ma, mb, mp):
            v = valeur_mp(f, t)
            if v is None or v == 0 or (v > 0) != (s > 0):
                raise Doute()
    for j, (p, psp) in enumerate(zip(crit, bornes[1:-1])):
        case = cellules[2 * j + 1]
        est_zero = any(sp.simplify(psp - z) == 0 for z in zs)
        if appartient(ivs, psp, sp):
            if (case == "0") != est_zero or (not est_zero and case not in ("+", "-")):
                raise Doute()
            if not est_zero and _signe_sp(sp.simplify(fe.subs(x, psp))) != (1 if case == "+" else -1):
                raise Doute()
        elif case not in ("||", "x"):
            raise Doute()


# ---------- les cartes ----------
def _ligne_chaine(i, alternatives, propriete):
    corps = r" \text{ ou } ".join(alternatives)
    return _ligne((r"\(" if i == 0 else r"\(\iff ") + corps + r"\)" + (f" ({propriete})" if propriete else ""))


def _positives(expos, f, ivs, seule):
    """« e^{…} > 0 pour tout x (une exponentielle est strictement positive) ; il ne s'annule jamais. » (D5) ; « e^{g(x)} » quand la
    partie 1 a nommé g ; f = e^{…} seule : sans « il ne s'annule jamais » (la conclusion suit)."""
    partout = len(ivs) == 1 and ivs[0].lo is None and ivs[0].hi is None
    pour_tout = r"pour tout \(x\)" if partout else r"pour tout \(x \in ED\)"
    lignes = []
    for h in expos:
        ecrit = "e^{g(x)}" if (h is f and mise_en_forme(f) is not None) else tex(h)
        fin = "." if seule else " ; il ne s'annule jamais."
        lignes.append(_ligne(rf"\({ecrit} > 0\) {pour_tout} (une exponentielle est strictement positive){fin}"))
    return lignes


def _zeros_et_signe(f, ivs, ED, sp, mpmath):
    """(blocs de la carte des zéros, tableau ou None, signe constant ou None). NonTraite / Doute remontent."""
    import derivee_variations as dv
    c, facs = aplatir(f)
    expos = []
    for h, _ in facs:
        if est_exponentielle(h) and not any(h.key() == e.key() for e in expos):
            expos.append(h)
    numerateur = [(h, k) for h, k in facs if k > 0 and not est_exponentielle(h)]
    denominateur = [(h, k) for h, k in facs if k < 0 and not est_exponentielle(h)]
    blocs = _positives(expos, f, ivs, seule=not numerateur and not denominateur and c > 0)
    zeros, rejetes, chaines, items = [], [], [], []
    for h, _ in numerateur:
        zh, it = zeros_facteur(h)
        zeros += zh
        items.append(it)
        chaines.append(etapes_facteur(h, it))
    vus = []
    for z in sorted(zeros, key=lambda p: p.val):
        if not any(proche(z.val, w.val) for w in vus):
            vus.append(z)
    zeros = vus
    fe = en_sympy_reel(f)
    for z in zeros:
        dedans = appartient(ivs, _sympy_num(z, sp), sp)
        if dedans != (valeur_mp(f, mpmath.mp.mpf(str(sp.N(_sympy_num(z, sp), CHIFFRES + 5)))) is not None):
            raise Doute()                                    # l'appartenance exacte et la sonde ne s'accordent pas
        if not dedans:
            rejetes.append(z)
    finale = " ou ".join(_avec_approx(rf"\(x = {z.tex}\)", _sympy_num(z, sp), sp) for z in zeros)
    if numerateur:
        etapes = [([tex(f) + " = 0"], None)]
        proprietes = (["car " + " et ".join(rf"\({tex(h)} > 0\)" for h in expos)] if expos else []) + \
                     (["numérateur nul"] if denominateur else []) + ([rf"on divise par \({qtex(c)}\)"] if c != 1 else [])
        N = _produit(numerateur)
        if tex(N) + " = 0" != etapes[0][0][0]:
            etapes.append(([tex(N) + " = 0"], " ; ".join(proprietes) or None))
        if len(numerateur) == 1:
            h, k = numerateur[0]
            if k > 1:
                etapes.append(([tex(h) + " = 0"], None))
            tout = None if chaines[0] is None else etapes + chaines[0][1:]        # etapes finit sur « h = 0 », 1ʳᵉ étape de sa chaîne
        else:
            tout = None if any(ch is None for ch in chaines) else etapes + _en_parallele(chaines, "produit nul")
        if tout is not None and sorted(set(tout[-1][0])) != sorted({rf"x = {z.tex}" for z in zeros}):
            tout = None                                      # la chaîne ne finit pas sur les zéros calculés : rédaction de l'outil ED
        if tout is not None:
            blocs += [_ligne_chaine(i, alt, p) for i, (alt, p) in enumerate(tout[:-1])]
            fin = (r"\(\iff\) " if len(tout) > 1 else "") + (finale or "")
            blocs.append(_ligne(fin + (f" ({tout[-1][1]})" if tout[-1][1] else "")))
        else:
            if len(numerateur) > 1:
                etapes.append(([tex(h) + " = 0" for h, _ in numerateur], "produit nul"))
            if len(etapes) > 1:
                blocs += [_ligne_chaine(i, alt, p) for i, (alt, p) in enumerate(etapes)]
            for it in items:
                blocs += [_ligne(b["html"]) for b in it]
            if finale:
                blocs.append(_ligne("Donc " + finale + "."))
        for z in rejetes:
            blocs.append(_ligne(rf"\(x = {z.tex}\) est rejeté, car \({z.tex} \notin ED\)."))
    elif not expos:
        blocs.append(_ligne(NUMERATEUR_CONSTANT))
    zeros_ed = [z for z in zeros if z not in rejetes]
    D = fusion(ED)
    Z = points(zeros_ed)
    crit, lignes, _ = dv.tableau_signes(f, Z, D, ED, "f(x)", c, facs)
    cellules = lignes[-1]["cells"]
    confirmer_signe(f, fe, crit, cellules, zeros_ed, ivs, sp, mpmath)
    signes = {cellules[2 * i] for i in range(len(crit) + 1)} - {"x"}
    constant = not zeros_ed and len(signes) == 1
    if constant:
        s = signes.pop()
        blocs.append(_ligne(rf"Donc f n'a pas de zéro et \(f(x) {'>' if s == '+' else '<'} 0\) sur ED."))
        return blocs, None
    if not zeros_ed and blocs and blocs[-1]["html"] not in (NUMERATEUR_CONSTANT, PAS_DE_ZERO):
        blocs.append(_ligne(PAS_DE_ZERO))
    tableau = {"type": "tableau", "var": "x", "crit": [p.tex for p in crit], "rows": lignes}
    return blocs, tableau


def _ordonnee(f, ivs, sp, mpmath):
    """Blocs de la carte « Ordonnée à l'origine » : f(0) exact puis ≈ et le point (0 ; f(0)), ou « 0 ∉ ED » ; Doute sinon.
    Quand la partie 1 a nommé g (f = e^{g(x)}), g(0) est calculé d'abord (« g(0) = −2/(−12) = 1/6, donc f(0) = e^{1/6} »)."""
    if not dans_ed(ivs, F(0), sp):
        if valeur_mp(f, mpmath.mp.mpf(0)) is not None:
            raise Doute()
        return [_ligne(NE_COUPE_PAS)]
    v = valeur_verifiee(f, en_sympy_reel(f), F(0), sp, mpmath)
    if v is None:
        raise Doute()
    ecrit, V, _ = v
    egalite = _avec_approx(rf"\(f(0) = {ecrit}\)", V, sp)
    if mise_en_forme(f) is not None:
        P, Q = polynome_ecrit(f.a.a), polynome_ecrit(f.a.b)
        h0, b0 = P[0], Q[0]
        g0 = h0 / b0
        if tex(Fn("exp", nombre(g0))) == ecrit and abs(valeur_mp(f.a, mpmath.mp.mpf(0)) - mpmath.mp.mpf(g0.numerator) / g0.denominator) \
                <= mpmath.mp.mpf(EGAL):
            calcul = qtex(g0) if b0 == 1 else rf"\frac{{{qtex(h0)}}}{{{qtex(b0)}}} = {qtex(g0)}"
            egalite = _avec_approx(rf"\(g(0) = {calcul}\), donc \(f(0) = {ecrit}\)", V, sp)
    return [_ligne(egalite + "."), _ligne(rf"Le graphe coupe l'axe des y au point \((0\,;\,{ecrit})\).")]


def cartes_zeros_signe(analyse):
    """Les cartes de la partie 3 (D5) ; `analyse` : (résultat de l'outil ED, arbre, ED), celle de `etudier` (en cache).
    Carte des zéros (exponentielle strictement positive, résolution en chaîne avec la propriété nommée, valeurs approchées), tableau
    de signes de f (machinerie R7 de l'outil Dérivée) ou, sans zéro et de signe constant, la phrase « f n'a pas de zéro et f(x) > 0
    sur ED » ; carte de l'ordonnée à l'origine. Chaque affirmation confirmée par SymPy et par la sonde (principe 0.2) ; sinon un
    message clair, sans conclusion."""
    _, f, ED = analyse
    sp = charger_sympy()
    try:
        import mpmath
    except ImportError:
        mpmath = None
    if sp is None or mpmath is None:
        return [so.carte("Zéros et signe de f", [_ligne(DOUTE_SIGNE)]), so.carte("Ordonnée à l'origine", [_ligne(DOUTE_F0)])]
    ivs = fusion(ED)
    with mpmath.workdps(CHIFFRES):
        try:
            blocs, tableau = _zeros_et_signe(f, ivs, ED, sp, mpmath)
            if tableau is None:
                cartes = [so.carte("Zéros et signe de f", blocs)]
            else:
                cartes = [so.carte("Zéros de f", blocs), so.carte("Signe de f", [tableau], badge="tableau")]
        except NonTraite as e:
            cartes = [so.carte("Zéros et signe de f", _positives_seules(f, ivs) + [_ligne(e.message)])]
        except Exception:                   # Doute, ou SymPy / mpmath en échec : rien plutôt qu'une affirmation non confirmée
            cartes = [so.carte("Zéros et signe de f", _positives_seules(f, ivs) + [_ligne(DOUTE_SIGNE)])]
        try:
            ordonnee = _ordonnee(f, ivs, sp, mpmath)
        except Exception:
            ordonnee = [_ligne(DOUTE_F0)]
    return cartes + [so.carte("Ordonnée à l'origine", ordonnee)]


def _positives_seules(f, ivs):
    """Les phrases « e^{…} > 0 » restent vraies quand la suite échoue (aucune conclusion sur f)."""
    try:
        _, facs = aplatir(f)
    except Exception:
        return []
    expos = []
    for h, _ in facs:
        if est_exponentielle(h) and not any(h.key() == e.key() for e in expos):
            expos.append(h)
    return _positives(expos, f, ivs, seule=False)
