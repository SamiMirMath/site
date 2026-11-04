"""
parties.py — Parties propres à l'Étude complète (decisions.md D2), rédigées ici et nulle part ailleurs : les outils séparés (Ensemble de
définition, Dérivée, Limites) ne changent pas. Chaque affirmation nouvelle a un garde-fou exact et numérique (EC-15) ; en cas de doute,
la ligne n'est pas écrite (Mise en forme) ou l'outil reprend la rédaction de l'outil ED (condition), jamais une ligne douteuse.

Partie 1. Domaine de définition (D1, D3) :
- carte « Mise en forme » quand f(x) = e^{g(x)}, g = haut / bas (deux polynômes de degré ≥ 1, écrits développés à coefficients entiers) :
  haut et bas factorisés une ligne par méthode (mise en évidence, Somme-Produit), puis « On note g(x) = …, donc f(x) = e^{g(x)}. » ;
  aucune carte quand rien ne se factorise ;
- une carte par condition (cartes de l'outil ED, R10) ; un dénominateur affine ou de la forme ax² + c, écrit développé, est résolu en
  chaîne, version courte : « On résout 6x − 12 = 0 ⇔ 6x = 12 ⇔ x = 2. » ; un trinôme unitaire à deux racines entières, par
  Somme-Produit (R2, Q11) ; sinon les lignes de l'outil ED, telles quelles ;
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
  machinerie R7 du tableau de f′ (`derivee_variations.tableau_signes`), une ligne par facteur de la factorisation écrite dans la
  chaîne (R2, Q23 ; garde-fou : le produit des lignes est f, SymPy et sonde) ;
- f(0) exact puis approché, et le point (0 ; f(0)) ; « 0 ∉ ED : le graphe ne coupe pas l'axe des y ».

Partie 5. Extremums (D11), à la place de la liste de l'outil Dérivée (la ligne f(x) du tableau porte les valeurs, D10, outil Dérivée) :
- une ligne de calcul pour chaque extremum (R2, Q41) : par l'exposant quand la carte « Dérivée » a nommé g, « g(4) = 18/12 = 3/2,
  donc f(4) = e^{3/2} ≈ 4,48 » ; sinon par substitution, « f(−2) = ((−2)² − 6)e^{−2(−2)} = (4 − 6)e⁴ = −2e⁴ ≈ −109,20 », chaque
  membre vérifié (SymPy et sonde) ;
- « Maximum global en x = 0 : (0 ; 1) (f′ passe de + à −). Les autres valeurs de f sont plus petites (limites 0⁺ en ±∞). » si f(x₀)
  dépasse strictement les autres extremums du même genre et toutes les limites aux bornes de l'ED, « Maximum local … Pas global :
  f(x) → +∞ quand x → 2⁺. » si l'une d'elles dépasse f(x₀), « Maximum local … » seul sinon (« ? », égalité, doute) (§2 révisé, Q43).
  Comparaisons par SymPy et par mpmath, « global » confirmé par une sonde de f sur l'ED, « pas global » par une valeur de f au-delà
  de f(x₀).

Valeurs approchées (R2, Q15, Q28) : dans la formule, après « \\approx » ; séparateur des milliers ’ entre 1000 et 10⁶.

Partie 6. Graphe (D15) : `partie3` donne aussi au graphique les zéros et f(0) que ses cartes écrivent (rien en cas de doute) ;
`ronds_vides` : un rond vide en (a ; L) pour chaque point exclu a dont la limite L d'un côté est finie (en plus des « trous » de
l'outil Limites), confirmé par SymPy (limite latérale exacte) et par une sonde mpmath (approche de L du bon côté) ; sinon pas de rond.
Carte « Bilan de l'étude » (D20, P9), avant le graphique : une ligne par résultat (ED, parité, zéros, signe, f(0), asymptotes avec la
position, extremums avec nature et ≈), chacune suivie de « (partie k) » ; aucun calcul nouveau : chaque ligne reprend ce que sa partie
a écrit et confirmé (`partie2`, `partie3`, `partie5` rendent ces données avec leurs cartes) ; une partie qui ne conclut pas n'a pas de
ligne.
"""
import re
from decimal import Decimal, ROUND_HALF_UP, localcontext
from fractions import Fraction as F
from math import gcd, isqrt

from nombres import formater_decimal, formater_entier
from noyau import (X, E, Nb, Neg, Fn, Op, Num, Iv, ens_tex, tex, ptex, qtex, decomposer, deg, pn, peval, pmul, evaluer, conditions, valeur_constante,
                   sans_x, fusion, points, proche, preimage, aplatir, en_sympy_reel, charger_sympy, SYMPY, NonPrisEnCharge, ErreurSaisie)
import sortie as so
import resoudre_ed

__all__ = ["cartes_domaine", "cartes_parite", "partie2", "cartes_zeros_signe", "partie3", "blocs_extremums", "partie5", "carte_bilan",
           "lignes_bilan", "ronds_vides", "mise_en_forme", "resolution_denominateur"]

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
    """Chaîne courte de « A = 0 » (D3) pour un dénominateur A écrit développé, affine ou de la forme ax² + c (c/a < 0), ou trinôme
    unitaire à deux racines entières (Somme-Produit, question 11) : (membres de la chaîne, [(écriture de la racine, valeur flottante)]),
    un membre étant une écriture ou (écriture, propriété) ; None (autre forme : rédaction de l'outil ED)."""
    P = polynome_ecrit(A)
    if P is None or P == [F(0), F(1)]:              # x = 0 : la condition « x ≠ 0 » est déjà la solution
        return None
    return resolution_polynome(P) or resolution_somme_produit(P)


def resolution_somme_produit(P):
    """« x² − 3x + 2 = 0 ⇔ (x − 1)(x − 2) = 0 (Somme-Produit) ⇔ x = 1 ou x = 2 (produit nul) » (question 11) pour un trinôme unitaire
    x² + bx + c (b ≠ 0, c ≠ 0) à deux racines entières distinctes ; garde-fou exact de `_factoriser` (le produit développé redonne P).
    None sinon."""
    P = pn(P)
    if deg(P) != 2 or P[2] != 1 or P[1] == 0 or P[0] == 0:
        return None
    r = _factoriser(P)
    if r is None:
        return None
    lignes, c, k, facteurs = r
    if c != 1 or k != 0 or len(facteurs) != 2 or [m for _, m in lignes] != ["Somme-Produit"]:
        return None
    racines = sorted(-h[0] for h in facteurs)
    membres = [ptex(P, "x") + " = 0", (lignes[0][0] + " = 0", "Somme-Produit"),
               (r" \text{ ou } ".join(f"x = {qtex(q)}" for q in racines), "produit nul")]
    return membres, [(qtex(q), float(q)) for q in racines]


def chaine_en_ligne(membres):
    """« A ⇔ B ⇔ C » sur une ligne, la propriété d'un membre à droite de ce membre : « \\(A \\iff B\\) (Somme-Produit) \\(\\iff C\\) (produit
    nul) » (un membre : écriture ou (écriture, propriété))."""
    morceaux, courant = [], ""
    for i, m in enumerate(membres):
        ecrit, propriete = (m, None) if isinstance(m, str) else m
        courant += (r" \iff " if i else "") + ecrit
        if propriete:
            morceaux.append(rf"\({courant.strip()}\) ({propriete})")
            courant = ""
    if courant:
        morceaux.append(rf"\({courant.strip()}\)")
    return " ".join(morceaux)


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
    if c["genre"] == "den" and c["resolu"] and A is not None and tex(A) == c["source_tex"] and isinstance(A, X):
        return [so.formule(c["cond_tex"])]
    res = _chaine_condition(c, A)
    if res is not None:
        return [so.formule(c["cond_tex"]), so.texte("On résout " + chaine_en_ligne(res[0]) + ".", style="etape")]
    return resoudre_ed.blocs_condition(c)


def _chaine_condition(c, A):
    """La chaîne courte (D3) que `blocs_condition` écrit pour la condition `c` d'arbre `A` : (membres, racines) quand elle existe et
    que ses deux garde-fous passent (même ensemble que l'outil ED, valeur nulle aux racines) ; None sinon (lignes de l'outil ED)."""
    if not (c["genre"] == "den" and c["resolu"] and A is not None and tex(A) == c["source_tex"]) or isinstance(A, X):
        return None
    res = resolution_denominateur(A)
    if res is None:
        return None
    membres, racines = res
    if _ensemble_prive_de(racines) == c["E_tex"] and all(_proches(evaluer(A, v), 0.0) for _, v in racines):
        return res
    return None


MISE_EN_EVIDENCE_ED = re.compile(r"On met \\\((.+?)\\\) en évidence : \\\((.+?) = (.+?)\\\)\.?")


def _sans_mise_en_page(t):
    return re.sub(r"\\left|\\right|\\,|\s", "", t)


def denominateurs_ecrits(analyse):
    """Question 66 (decisions.md §8) : les dénominateurs que les cartes de condition de la partie 1 écrivent factorisés, {écriture tex
    du dénominateur : (c, k, facteurs)} (dénominateur = c·xᵏ·∏ facteurs, polynômes), lus comme `cartes_domaine` les écrit : chaîne
    Somme-Produit de l'EC (« x² − 3x + 2 = 0 ⇔ (x − 1)(x − 2) = 0 (Somme-Produit) ») ou première ligne de l'outil ED « On met x en
    évidence : x² − 4x = x(x − 4) » (alors xᵏ et le facteur restant, tel que cette ligne l'écrit ; les lignes suivantes de l'outil
    ED ne sont pas suivies : x³ − 4x → x, x² − 4). Rien d'autre : un dénominateur résolu sans factorisation (x² − 4 = 0 ⇔ x² = 4,
    Δ) garde sa ligne. Le garde-fou (produit des lignes = f) est celui de `lignes_du_tableau`."""
    res_ed, f, _ = analyse
    arbres, out = [], {}
    try:
        conditions(f, arbres)
    except Exception:
        return out
    for c in res_ed.get("conditions", []):
        genre, A = arbres[c["num"] - 1] if c["num"] <= len(arbres) else (None, None)
        if genre != c["genre"] or genre != "den" or A is None or not c.get("resolu") or tex(A) != c["source_tex"]:
            continue
        P = polynome_ecrit(A)
        if P is None:
            continue
        chaine = _chaine_condition(c, A)
        if chaine is not None:
            if any(not isinstance(m, str) and m[1] == "Somme-Produit" for m in chaine[0]):
                r = _factoriser(P)
                if r is not None:
                    out[tex(A)] = r[1:]
            continue
        etapes = [e for e in c.get("etapes", []) if e.get("type") == "texte"]
        m = MISE_EN_EVIDENCE_ED.fullmatch(etapes[0]["html"]) if etapes else None
        if m is None or m.group(2) != tex(A):
            continue
        P = pn(P)
        k = next(i for i, a in enumerate(P) if a != 0)
        Q = P[k:]                                    # l'outil ED met xᵏ seul en évidence : P = xᵏ·Q
        devant = "x" if k == 1 else f"x^{{{k}}}"
        if k == 0 or deg(Q) < 1 or m.group(1) != devant or \
                _sans_mise_en_page(devant + "(" + ptex(Q, "x") + ")") != _sans_mise_en_page(m.group(3)):
            continue
        out[tex(A)] = (F(1), k, [Q])
    return out


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
def arrondi(d, plafond=1000):
    """Valeur arrondie affichée (decisions.md §2) d'un Decimal : 2 décimales si |d| ≥ 0,01, 2 chiffres significatifs si
    10⁻³ ≤ |d| < 0,01 ; None hors de [10⁻³ ; plafond[ (partie 2 : 1000, question 19 ; parties 3 et 5 : 10⁶, question 28)."""
    if d == 0:
        return Decimal(0)
    if not Decimal("0.001") <= abs(d) < plafond:
        return None
    q = Decimal("0.01") if abs(d) >= Decimal("0.01") else Decimal(1).scaleb(d.adjusted() - 1)
    return d.quantize(q, rounding=ROUND_HALF_UP)


def decimal_tex(d):
    """Un Decimal écrit en TeX, notation suisse (`moteur/nombres.py`) : −0{,}68, 1\\text{’}234{,}57 ; l'opposé de 0 s'écrit 0. Les
    valeurs approchées s'écrivent dans la formule, après « \\approx » (question 15)."""
    return formater_decimal(format(d if d != 0 else Decimal(0), "f"), tex=True)


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
    return {"tex": ecrit, "entier": entier, "arrondi": r, "approx": None if entier else decimal_tex(r)}


def _egalite(nom, v):
    """« f(1) = −5e^{−2} ≈ −0,68 », la valeur approchée dans la formule (entier exact : sans « ≈ »)."""
    return rf"\({nom} = {v['tex']}" + ("" if v["approx"] is None else rf" \approx {v['approx']}") + r"\)"


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
            approx = "" if v0["approx"] is None else rf" \approx {v0['approx']}"
            return [_ligne(rf"\(f(0) = {v0['tex']}{approx} \neq 0\)"),
                    _ligne(r"Une fonction impaire vérifie \(f(0) = 0\) : f n'est pas impaire.")]
    ce = contre_exemple(f, fe, ivs, lambda u, v: -u != v, sp, mpmath)
    if ce is None:
        return None
    a, va, vm = ce
    ta, tm = qtex(a), qtex(-a)
    oppose = -va["arrondi"] if va["arrondi"] != 0 else va["arrondi"]
    moins = rf"\(-f({ta}) {'=' if va['entier'] else chr(92) + 'approx'} {decimal_tex(oppose)}\)"
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
            _ligne(rf"\({qtex(a)} \in ED\), mais \({qtex(-a)} \notin ED\) : ED n'est pas symétrique par rapport à 0."), _ligne(NI)])], "ni"
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
            return cartes + _message(NON_REDIGEE), None
        lignes = chaine_f_moins_x(f, p)
        cible = substituer(f, Neg(X()))
        for _, T in lignes:
            if T is not None:
                _verifier_egalite(T, cible, fm, sp, mpmath)
        blocs = [_ligne(html) for html, _ in lignes] + [_ligne(PAIRE if p > 0 else IMPAIRE)]
        return cartes + [so.carte("Calcul de f(−x)", blocs)], genre
    impaire, paire = _pas_impaire(f, fe, ivs, sp, mpmath), _pas_paire(f, fe, ivs, sp, mpmath)
    if impaire is None or paire is None:
        return cartes + _message(SANS_CONTRE_EXEMPLE), None
    return cartes + [so.carte("Pas impaire", impaire), so.carte("Pas paire", paire + [_ligne(NI)])], "ni"


def partie2(analyse):
    """La partie 2 (D4) : {"cartes", "conclusion"} ; `analyse` : (résultat de l'outil ED, arbre, ED), celle de `etudier` (en cache).
    "conclusion" : "paire", "impaire" ou "ni", celle qu'écrivent les cartes (« Donc f est paire. »…) ; None quand elles ne concluent
    pas (sans SymPy ou mpmath, garde-fou en doute, chaîne non rédigée, aucun contre-exemple : un message clair, principe 0.2)."""
    _, f, ED = analyse
    sp = charger_sympy()
    try:
        import mpmath
    except ImportError:
        mpmath = None
    if sp is None or mpmath is None:
        return {"cartes": _message(DOUTE), "conclusion": None}
    try:
        with mpmath.workdps(CHIFFRES):
            cartes, conclusion = _cartes_parite(f, fusion(ED), sp, mpmath)
    except Exception:                       # Doute, ou SymPy / mpmath en échec : rien plutôt qu'une affirmation non confirmée
        return {"cartes": _message(DOUTE), "conclusion": None}
    return {"cartes": cartes, "conclusion": conclusion}


def cartes_parite(analyse):
    """Les cartes de la partie 2 (D4) : voir `partie2`."""
    return partie2(analyse)["cartes"]


# ---------------------------------------------------------------------------------------------------------------------------
# Partie 3. Zéros, signe, ordonnée à l'origine (D5)
# ---------------------------------------------------------------------------------------------------------------------------
DOUTE_SIGNE = "Le signe de f n'a pas pu être établi avec certitude : l'outil ne conclut pas."
ZEROS_NON_EXACTS = "Les zéros de f ne se calculent pas exactement : l'outil ne dresse pas le tableau de signes de f."
ZEROS_NON_TRAITES = "Les zéros de f n'ont pas pu être calculés par l'outil : le signe de f n'est pas traité."
DOUTE_F0 = "L'ordonnée à l'origine n'a pas pu être établie avec certitude : l'outil ne conclut pas."
HORS_ED = "0 ∉ ED"                                                                          # bilan : pas d'ordonnée à l'origine
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
    chaines = ([[(["x = 0"], None)]] if k > 0 else []) + [_dans_un_produit(h) for h in facteurs]
    if any(ch is None for ch in chaines):
        return None
    if len(chaines) == 1:
        return etapes + chaines[0][1:]
    return etapes + _en_parallele(chaines, "produit nul")


def _dans_un_produit(P):
    """Chaîne du facteur P d'un produit nul : un facteur x − r s'écrit directement x = r (« (x − 1)(x − 3) = 0 ⇔ x = 1 ou x = 3
    (produit nul) », question 11, comme la ligne des zéros de f′, Q56) ; sinon `etapes_polynome`."""
    P = pn(P)
    if deg(P) == 1 and P[1] == 1:
        return [([f"x = {qtex(-P[0])}"], None)]
    return etapes_polynome(P)


def _x_moins_r(h):
    """h est écrit x − r (ou x + r)."""
    P = polynome_ecrit(h)
    return P is not None and deg(P) == 1 and P[1] == 1


def facteurs_ecrits(h):
    """La factorisation de h que la chaîne de la partie 3 écrit (mise en évidence, Somme-Produit : `etapes_polynome`) : (c, k,
    facteurs), h = c·xᵏ·∏ facteurs (polynômes) ; None si la chaîne n'en écrit pas (affine, ax² + c, x, autre fonction)."""
    if isinstance(h, X):
        return None
    P = polynome_ecrit(h)
    if P is None or P == [F(0), F(1)] or (deg(P) in (1, 2) and resolution_polynome(P) is not None):
        return None
    r = _factoriser(P)
    return None if r is None else r[1:]


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
    """Valeur approchée affichée d'un nombre SymPy, en TeX (à écrire dans la formule, après « \\approx », question 15), None pour un
    entier exact (écrit tel quel) : decisions.md §2 entre 10⁻³ et 10⁶ (séparateur des milliers ’ dès 1000 : 1’234,57, question 28) ;
    R13 sous 10⁻³ et dès 10⁶ (3,162 × 10⁻⁵, notation scientifique, question 1)."""
    if v.is_Integer:
        return None
    with localcontext() as ctx:
        ctx.prec = 50
        d = Decimal(str(sp.N(v, CHIFFRES)))
        r = arrondi(d, plafond=Decimal(10) ** 6)
        if r is not None:
            return decimal_tex(r)
        e = d.adjusted()
        m = (d.scaleb(-e)).quantize(Decimal("0.001"), rounding=ROUND_HALF_UP)
        if abs(m) >= 10:
            e += 1
            m = (d.scaleb(-e)).quantize(Decimal("0.001"), rounding=ROUND_HALF_UP)
    t = format(m, "f")
    t = t[:-4] if t.endswith(".000") else t
    return t.replace(".", "{,}") + r" \times 10^{" + str(e) + "}"


def formule_approx(corps, v, sp):
    """« \\(corps \\approx a\\) » : la formule, puis la valeur approchée de v dans la formule (question 15) ; sans « ≈ » pour un
    entier exact ou une valeur sans écriture convenue."""
    a = approchee(v, sp)
    return rf"\({corps}" + ("" if a is None else rf" \approx {a}") + r"\)"


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


def _zeros_et_signe(f, ivs, ED, sp, mpmath, denominateurs=None):
    """(blocs de la carte des zéros, tableau ou None, zéros de f dans l'ED : points confirmés). NonTraite / Doute remontent.
    `denominateurs` : les dénominateurs factorisés en partie 1 (`denominateurs_ecrits`, question 66)."""
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
    ecrite = False                                           # la chaîne de f(x) = 0 est écrite (et non les lignes de l'outil ED)
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
    finale = " ou ".join(formule_approx(rf"x = {z.tex}", _sympy_num(z, sp), sp) for z in zeros)
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
            directes = [_dans_un_produit(polynome_ecrit(h)) if _x_moins_r(h) else ch for (h, _), ch in zip(numerateur, chaines)]
            tout = None if any(ch is None for ch in directes) else etapes + _en_parallele(directes, "produit nul")
        if tout is not None and sorted(set(tout[-1][0])) != sorted({rf"x = {z.tex}" for z in zeros}):
            tout = None                                      # la chaîne ne finit pas sur les zéros calculés : rédaction de l'outil ED
        if tout is not None:
            ecrite = True
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
    denominateurs = denominateurs or {}
    if ecrite or any(k < 0 and tex(h) in denominateurs for h, k in facs):
        c_tab, facs_tab = lignes_du_tableau(f, c, facs, sp, mpmath, numerateur=ecrite, denominateurs=denominateurs)
    else:
        c_tab, facs_tab = c, facs
    crit, lignes, _ = dv.tableau_signes(f, Z, D, ED, "f(x)", c_tab, facs_tab)
    cellules = lignes[-1]["cells"]
    confirmer_signe(f, fe, crit, cellules, zeros_ed, ivs, sp, mpmath)
    signes = {cellules[2 * i] for i in range(len(crit) + 1)} - {"x"}
    constant = not zeros_ed and len(signes) == 1
    if constant:
        s = signes.pop()
        blocs.append(_ligne(rf"Donc f n'a pas de zéro et \(f(x) {'>' if s == '+' else '<'} 0\) sur ED."))
        return blocs, None, zeros_ed, (rf"\(f(x) {'>' if s == '+' else '<'} 0\) sur ED", None)
    if not zeros_ed and blocs and blocs[-1]["html"] not in (NUMERATEUR_CONSTANT, PAS_DE_ZERO):
        blocs.append(_ligne(PAS_DE_ZERO))
    tableau = {"type": "tableau", "var": "x", "crit": [p.tex for p in crit], "rows": lignes}
    positif, negatif = ensembles_du_signe(crit, cellules)
    morceaux = [rf"\(f(x) {o} 0\) sur \({ens_tex(S)}\)" for o, S in ((">", positif), ("<", negatif)) if S]
    return blocs, tableau, zeros_ed, (" ; ".join(morceaux) or None, (positif, negatif))


def ensembles_du_signe(crit, cellules):
    """Bilan (D20) : (ensemble où f > 0, ensemble où f < 0), listes d'intervalles réunis (`fusion`), lus dans la ligne f(x) du tableau
    de signes, une fois celle-ci confirmée (`confirmer_signe` : le signe de chaque intervalle et de chaque point critique de l'ED,
    SymPy et sonde). Un intervalle entre deux points critiques consécutifs est entièrement dans l'ED ou entièrement dehors (« x ») ;
    un point critique de l'ED où f ne s'annule pas (borne fermée de l'ED) prend le signe de sa case. Le bilan les écrit comme l'ED
    (`ens_tex`) : « f(x) > 0 sur … ; f(x) < 0 sur … »."""
    k = len(crit)
    positif, negatif = [], []
    for i in range(k + 1):
        if cellules[2 * i] in ("+", "-"):
            iv = Iv(crit[i - 1] if i > 0 else None, False, crit[i] if i < k else None, False)
            (positif if cellules[2 * i] == "+" else negatif).append(iv)
    for j in range(k):
        if cellules[2 * j + 1] in ("+", "-"):
            (positif if cellules[2 * j + 1] == "+" else negatif).append(Iv(crit[j], True, crit[j], True))
    return fusion(positif), fusion(negatif)


def arbre_polynome(P):
    """L'arbre d'un polynôme à coefficients entiers, écrit comme `ptex` (x² − 3, x − 1) ; None si l'écriture diffère."""
    P = pn(P)
    out = None
    for i in range(len(P) - 1, -1, -1):
        a = P[i]
        if a == 0:
            continue
        mono = Nb(abs(a)) if i == 0 else (X() if i == 1 else Op("^", X(), Nb(i)))
        if i > 0 and abs(a) != 1:
            mono = Op("*", Nb(abs(a)), mono)
        out = (mono if a > 0 else Neg(mono)) if out is None else Op("+" if a > 0 else "-", out, mono)
    return out if out is not None and tex(out) == ptex(P, "x") else None


def lignes_du_tableau(f, c, facs, sp, mpmath, numerateur=True, denominateurs=None):
    """Lignes du tableau de signes de f (question 23) : chaque facteur que la chaîne de f(x) = 0 a factorisé (mise en évidence,
    Somme-Produit) est remplacé par les facteurs écrits (x² − 4x + 3 → x − 1, x − 3 ; x³ − 3x → x, x² − 3) ; de même chaque
    facteur du dénominateur que la partie 1 a factorisé (question 66, `denominateurs` : `denominateurs_ecrits` ; 1/(x² − 3x + 2) →
    x − 1, x − 2). `numerateur` : la chaîne de f(x) = 0 est écrite (sinon les facteurs du numérateur restent). Garde-fou : la
    constante fois le produit des lignes est égal à f, exactement (SymPy) et à la sonde (mpmath) ; sinon les lignes d'avant, (c, facs).
    Un facteur du dénominateur dont un facteur écrit est déjà au numérateur ((x − 1)/(x² − 3x + 2)) reste entier."""
    denominateurs = denominateurs or {}

    def ecrits_de(h, k):
        """(constante, [(arbre, exposant)]) qui remplacent hᵏ, ou None (h reste une ligne)."""
        if k > 0:
            e = facteurs_ecrits(h) if numerateur and not est_exponentielle(h) else None
        else:
            e = denominateurs.get(tex(h))
        if e is None:
            return None
        arbres = [arbre_polynome(Q) for Q in e[2]]
        if any(a is None for a in arbres):
            return None
        return F(e[0]) ** k, ([(X(), e[1] * k)] if e[1] else []) + [(a, k) for a in arbres]

    remplaces = {}
    for i, (h, k) in enumerate(facs):                       # le numérateur d'abord
        if k > 0 and ecrits_de(h, k) is not None:
            remplaces[i] = ecrits_de(h, k)
    au_numerateur = {g.key() for i, (h, k) in enumerate(facs) if k > 0 for g, _ in remplaces.get(i, (None, [(h, k)]))[1]}
    for i, (h, k) in enumerate(facs):                       # un facteur écrit déjà au numérateur : le dénominateur reste entier
        r = ecrits_de(h, k) if k < 0 else None
        if r is not None and not any(g.key() in au_numerateur for g, _ in r[1]):
            remplaces[i] = r
    nouvelles, cn, change = [], F(c), bool(remplaces)

    def ajouter(h, k):
        for i, (g, kg) in enumerate(nouvelles):
            if g.key() == h.key():
                if (kg > 0) != (k > 0):
                    raise ValueError("facteur au numérateur et au dénominateur")
                nouvelles[i] = (g, kg + k)
                return
        nouvelles.append((h, k))
    try:
        for i, (h, k) in enumerate(facs):
            if i not in remplaces:
                ajouter(h, k)
                continue
            c2, lignes = remplaces[i]
            cn *= c2
            for a, ka in lignes:
                ajouter(a, ka)
    except ValueError:
        return c, facs
    if not change:
        return c, facs
    try:
        produit = sp.Rational(cn.numerator, cn.denominator)
        for h, k in nouvelles:
            produit *= en_sympy_reel(h) ** k
        d = produit - en_sympy_reel(f)
        if not (d == 0 or sp.simplify(d) == 0):
            return c, facs
        mp, vues = mpmath.mp, 0
        for t in POINTS_SONDE:
            for x in (mp.mpf(t), -mp.mpf(t)):
                v = valeur_mp(f, x)
                if v is None:
                    continue
                p = mp.mpf(cn.numerator) / cn.denominator
                for h, k in nouvelles:
                    w = valeur_mp(h, x)
                    if w is None or (w == 0 and k < 0):
                        return c, facs
                    p *= w ** k
                if abs(p - v) > mp.mpf(EGAL) * (1 + abs(v)):
                    return c, facs
                vues += 1
        if vues < 3:
            return c, facs
    except Exception:
        return c, facs
    return cn, nouvelles


def _ordonnee(f, ivs, sp, mpmath):
    """(blocs de la carte « Ordonnée à l'origine », valeur SymPy de f(0) ou None si 0 ∉ ED, écriture « f(0) = … ≈ … » du bilan ou
    HORS_ED) : f(0) exact puis ≈ et le point
    (0 ; f(0)), ou « 0 ∉ ED » ; Doute sinon. Quand la partie 1 a nommé g (f = e^{g(x)}), g(0) est calculé d'abord (« g(0) =
    −2/(−12) = 1/6, donc f(0) = e^{1/6} »)."""
    if not dans_ed(ivs, F(0), sp):
        if valeur_mp(f, mpmath.mp.mpf(0)) is not None:
            raise Doute()
        return [_ligne(NE_COUPE_PAS)], None, HORS_ED
    v = valeur_verifiee(f, en_sympy_reel(f), F(0), sp, mpmath)
    if v is None:
        raise Doute()
    ecrit, V, _ = v
    egalite = valeur = formule_approx(rf"f(0) = {ecrit}", V, sp)
    if mise_en_forme(f) is not None:
        P, Q = polynome_ecrit(f.a.a), polynome_ecrit(f.a.b)
        h0, b0 = P[0], Q[0]
        g0 = h0 / b0
        if tex(Fn("exp", nombre(g0))) == ecrit and abs(valeur_mp(f.a, mpmath.mp.mpf(0)) - mpmath.mp.mpf(g0.numerator) / g0.denominator) \
                <= mpmath.mp.mpf(EGAL):
            calcul = qtex(g0) if b0 == 1 else rf"\frac{{{qtex(h0)}}}{{{qtex(b0)}}} = {qtex(g0)}"
            egalite = rf"\(g(0) = {calcul}\), donc " + formule_approx(rf"f(0) = {ecrit}", V, sp)
    return [_ligne(egalite + "."), _ligne(rf"Le graphe coupe l'axe des y au point \((0\,;\,{ecrit})\).")], V, valeur


def partie3(analyse):
    """La partie 3 (D5) : {"cartes", "zeros", "f0"} ; `analyse` : (résultat de l'outil ED, arbre, ED), celle de `etudier` (en cache).
    Cartes : carte des zéros (exponentielle strictement positive, résolution en chaîne avec la propriété nommée, valeurs approchées),
    tableau de signes de f (machinerie R7 de l'outil Dérivée) ou, sans zéro et de signe constant, la phrase « f n'a pas de zéro et
    f(x) > 0 sur ED » ; carte de l'ordonnée à l'origine. Chaque affirmation confirmée par SymPy et par la sonde (principe 0.2) ;
    sinon un message clair, sans conclusion. Données du graphique (D15, partie 6), celles des cartes et rien d'autre : "zeros", les
    zéros de f dans l'ED (flottants) quand la carte des zéros conclut, sinon [] ; "f0", f(0) (flottant) quand la carte de l'ordonnée
    à l'origine l'écrit, sinon None. Données du bilan (D20, partie 6), écritures des cartes et rien d'autre : "bilan" = {"zeros" :
    les zéros écrits (« x = √6 ≈ 2,45 »), [] si aucun, None si la carte ne conclut pas ; "signe" : « f(x) > 0 sur ED », ou les
    ensembles lus dans la ligne f(x) confirmée du tableau, None si elle ne conclut pas ; "ensembles" : ces ensembles (positif, négatif),
    listes d'intervalles, None sans tableau ; "f0" : « f(0) = e^{1/6} ≈ 1,18 », HORS_ED si
    0 ∉ ED, None si la carte ne conclut pas}."""
    _, f, ED = analyse
    sp = charger_sympy()
    try:
        import mpmath
    except ImportError:
        mpmath = None
    bilan = {"zeros": None, "signe": None, "ensembles": None, "f0": None}
    if sp is None or mpmath is None:
        return {"cartes": [so.carte("Zéros et signe de f", [_ligne(DOUTE_SIGNE)]), so.carte("Ordonnée à l'origine", [_ligne(DOUTE_F0)])],
                "zeros": [], "f0": None, "bilan": bilan}
    ivs = fusion(ED)
    zeros, f0 = [], None
    with mpmath.workdps(CHIFFRES):
        try:
            blocs, tableau, zs, signe = _zeros_et_signe(f, ivs, ED, sp, mpmath, denominateurs_ecrits(analyse))
            if tableau is None:
                cartes = [so.carte("Zéros et signe de f", blocs)]
            else:
                cartes = [so.carte("Zéros de f", blocs), so.carte("Signe de f", [tableau], badge="tableau")]
            zeros = [float(sp.N(_sympy_num(z, sp), 20)) for z in zs]
            bilan["zeros"] = [formule_approx(rf"x = {z.tex}", _sympy_num(z, sp), sp) for z in zs]
            bilan["signe"], bilan["ensembles"] = signe
        except NonTraite as e:
            cartes = [so.carte("Zéros et signe de f", _positives_seules(f, ivs) + [_ligne(e.message)])]
            zeros, bilan["zeros"], bilan["signe"], bilan["ensembles"] = [], None, None, None
        except Exception:                   # Doute, ou SymPy / mpmath en échec : rien plutôt qu'une affirmation non confirmée
            cartes = [so.carte("Zéros et signe de f", _positives_seules(f, ivs) + [_ligne(DOUTE_SIGNE)])]
            zeros, bilan["zeros"], bilan["signe"], bilan["ensembles"] = [], None, None, None
        try:
            ordonnee, V, bilan["f0"] = _ordonnee(f, ivs, sp, mpmath)
            f0 = None if V is None else float(sp.N(V, 20))
        except Exception:
            ordonnee, f0, bilan["f0"] = [_ligne(DOUTE_F0)], None, None
    return {"cartes": cartes + [so.carte("Ordonnée à l'origine", ordonnee)], "zeros": zeros, "f0": f0, "bilan": bilan}


def cartes_zeros_signe(analyse):
    """Les cartes de la partie 3 (D5) : voir `partie3`."""
    return partie3(analyse)["cartes"]


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


# ---------------------------------------------------------------------------------------------------------------------------
# Partie 5. Extremums (D11)
# ---------------------------------------------------------------------------------------------------------------------------
LIMITE_LUE = re.compile(r"([+-]?)(?:(\d+)|\\d?frac\{(\d+)\}\{(\d+)\}|(\\infty))(?:\^\{[+-]\})?")
TOLERANCE = "1e-20"                     # sonde : écart relatif sous lequel deux valeurs sont tenues pour égales
DEPASSE = "1e-15"                       # sonde : écart relatif au-delà duquel une valeur dépasse clairement f(x₀)
GRILLE = 400                            # points de la grille de la sonde « global », par intervalle de l'ED
DEMI_LARGEUR = 20                       # grille sur [x₀ − 20 ; x₀ + 20] (bornée par l'intervalle), plus des points lointains


def lire_limite(t, sp):
    """Valeur SymPy d'une limite du tableau T06c (liste fermée d'écritures : ±∞, entier, fraction, avec signe d'approche ^{±}) ;
    None pour toute autre écriture (« ? », racine, exponentielle…) : la comparaison n'est alors pas faite (doute)."""
    if t is None:
        return None
    m = LIMITE_LUE.fullmatch(t.replace(" ", ""))
    if m is None:
        return None
    signe = -1 if m.group(1) == "-" else 1
    if m.group(5):
        return signe * sp.oo
    if m.group(2):
        return signe * sp.Integer(int(m.group(2)))
    if int(m.group(4)) == 0:
        return None
    return signe * sp.Rational(int(m.group(3)), int(m.group(4)))


def _mp_de(v, sp, mp):
    return mp.mpf(str(sp.N(v, CHIFFRES + 5)))


def _sympy_de_py(py, sp):
    return sp.sympify(py, locals={"sqrt": sp.sqrt, "exp": sp.exp, "log": sp.log, "E": sp.E})


def _comparer(v, y, s, sp, mp):
    """Signe exact de s·(v − y) (v : limite ou valeur d'un autre extremum, y = f(x₀), s = 1 pour un maximum, −1 pour un minimum),
    confirmé par mpmath ; Doute si SymPy ne tranche pas ou si la sonde n'est pas d'accord."""
    if v in (sp.oo, -sp.oo):
        return 1 if s * (1 if v == sp.oo else -1) > 0 else -1
    exact = _signe_sp(sp.simplify(v - y))
    ecart = _mp_de(v, sp, mp) - _mp_de(y, sp, mp)
    seuil = mp.mpf(TOLERANCE) * (1 + abs(_mp_de(y, sp, mp)))
    if exact == 0:
        if abs(ecart) > seuil:
            raise Doute()
        return 0
    if abs(ecart) <= seuil or (ecart > 0) != (exact > 0):
        raise Doute()
    return s * exact


def _bornes_de_l_ed(ivs, crit, limites, x_extremums):
    """[(où, limite tex)] dans l'ordre du tableau : −∞, chaque côté ouvert de chaque borne finie de l'ED, +∞ (D11 : « toutes les
    limites aux bornes de l'ED ») ; Doute si une limite manque, si une borne fermée n'est pas un extremum ou si un intervalle est un point."""
    colonnes = {c["j"]: c for c in limites.get("colonnes", [])}

    def cote(borne, nom):
        if borne.tex not in crit:
            raise Doute()
        c = colonnes.get(2 * crit.index(borne.tex) + 1)
        if c is None or c.get(nom) is None:
            raise Doute()
        return c[nom]

    out = []
    for iv in ivs:
        if iv.lo is not None and iv.hi is not None and proche(iv.lo.val, iv.hi.val):
            raise Doute()
        for borne, ferme, infini, nom, signe in ((iv.lo, iv.lf, "moins_inf", "droite", "+"), (iv.hi, iv.hf, "plus_inf", "gauche", "-")):
            if borne is None:
                if limites.get(infini) is None:
                    raise Doute()
                out.append((r"-\infty" if infini == "moins_inf" else r"+\infty", limites[infini], None))
            elif ferme:
                if borne.tex not in x_extremums:
                    raise Doute()
            else:
                out.append((f"{borne.tex}^{{{signe}}}", cote(borne, nom), (borne, signe)))
    return out


def _points_grille(a, b, x0, mp):
    """Points de la sonde « global » dans l'intervalle ]a ; b[ de l'ED (a, b : mpf ou None pour ∓∞)."""
    bas = a if a is not None else (x0 if b is None else min(b, x0)) - DEMI_LARGEUR
    haut = b if b is not None else (x0 if a is None else max(a, x0)) + DEMI_LARGEUR
    pts = [bas + (haut - bas) * mp.mpf(k) / GRILLE for k in range(1, GRILLE)]
    for k in range(1, 11):
        h = mp.mpf(10) ** -k
        if a is not None:
            pts.append(a + h)
        if b is not None:
            pts.append(b - h)
    for k in range(0, 7):
        h = mp.mpf(10) ** k
        if a is None:
            pts.append((b if b is not None else x0) - h)
        if b is None:
            pts.append((a if a is not None else x0) + h)
    return pts


def _sonde_globale(f, ivs, x0, y, s, sp, mp):
    """Sonde de « global » : aucune valeur de f sur l'ED (grille, points près de chaque borne et lointains) ne dépasse f(x₀)."""
    seuil = mp.mpf(TOLERANCE) * (1 + abs(y))
    vues = 0
    for iv in ivs:
        a = None if iv.lo is None else _mp_de(_sympy_num(iv.lo, sp), sp, mp)
        b = None if iv.hi is None else _mp_de(_sympy_num(iv.hi, sp), sp, mp)
        pts = _points_grille(a, b, x0, mp) + [p for p in (a if iv.lf else None, b if iv.hf else None) if p is not None]
        for t in pts:
            v = valeur_mp(f, t)
            if v is None:
                continue
            vues += 1
            if s * (v - y) > seuil:
                raise Doute()
    if vues < GRILLE // 2:
        raise Doute()


def _sonde_depasse(f, raison, y, s, sp, mp):
    """Sonde de « pas global » : un x de l'ED, près de la borne de la raison (ou l'autre extremum), où f dépasse clairement f(x₀)."""
    seuil = mp.mpf(DEPASSE) * (1 + abs(y))
    if raison["genre"] == "extremum":
        pts = [raison["x_mp"]]
    elif raison["borne"] is None:
        sg = -1 if raison["ou"] == r"-\infty" else 1
        pts = [sg * mp.mpf(10) ** k for k in range(0, 9)]
    else:
        borne, signe = raison["borne"]
        a = _mp_de(_sympy_num(borne, sp), sp, mp)
        pts = [a + (1 if signe == "+" else -1) * mp.mpf(10) ** -k for k in range(1, 13)]
    for t in pts:
        v = valeur_mp(f, t)
        if v is not None and s * (v - y) > seuil:
            return
    raise Doute()


def _liste_tex(morceaux):
    return morceaux[0] if len(morceaux) == 1 else ", ".join(morceaux[:-1]) + " et " + morceaux[-1]


def _justification_globale(e, s, bornes, autres):
    """« (limites 0⁺ en ±∞) », avec les autres extremums du même genre ; une limite égale en −∞ et en +∞ s'écrit « en ±∞ »."""
    groupes = []
    for ou, t, _ in bornes:
        g = next((g for g in groupes if g[0] == t), None)
        if g is None:
            groupes.append((t, [ou]))
        else:
            g[1].append(ou)
    morceaux = []
    for t, ous in groupes:
        if ous == [r"-\infty", r"+\infty"]:
            morceaux.append(rf"\({t}\) en \(\pm\infty\)")
        else:
            morceaux += [rf"\({t}\) en \({ou}\)" for ou in ous]
    une_seule = len(bornes) == 1
    parties_j = []
    if autres:
        nom = ("autre maximum local" if s > 0 else "autre minimum local") if len(autres) == 1 else \
              ("autres maximums locaux" if s > 0 else "autres minimums locaux")
        parties_j.append(nom + " : " + _liste_tex([rf"\(f({a['x_tex']}) = {a['f_tex']}\)" for a in autres]))
    if morceaux:
        parties_j.append(("limite " if une_seule else "limites ") + _liste_tex(morceaux))
    comparatif = "plus petites" if s > 0 else "plus grandes"
    precision = f" ({' ; '.join(parties_j)})" if parties_j else ""          # ED fermé (√(4 − x²)) : aucune limite à citer
    return f"Les autres valeurs de f sont {comparatif}{precision}."          # après « Maximum global … » (§2 révisé, question 43)


def statut_global(e, extrema, ivs, crit, cellules, limites, f, sp, mp):
    """D11 : (« global » | « pas global », texte), ou None ou Doute (« local » seul : limite « ? » ou absente, égalité, doute). Chaque comparaison
    est faite par SymPy et par mpmath ; « global » est confirmé par une sonde de f sur l'ED, « pas global » par une sonde qui trouve
    une valeur de f au-delà de f(x₀)."""
    if any(cellules[2 * i] not in ("+", "-", "x") for i in range(len(crit) + 1)):
        return None                                       # f constante sur un intervalle, signe inconnu : rien d'affirmé
    s = 1 if e["genre"].startswith("maximum") else -1
    y = _sympy_de_py(e["f_py"], sp)
    bornes = _bornes_de_l_ed(ivs, crit, limites, {a["x_tex"] for a in extrema})
    concurrents = []
    for ou, t, borne in bornes:
        v = lire_limite(t, sp)
        if v is None:
            return None
        concurrents.append({"genre": "limite", "ou": ou, "tex": t, "borne": borne, "v": v})
    autres = [a for a in extrema if a is not e and a["genre"] == e["genre"]]
    for a in autres:
        if "f_py" not in a:
            return None
        concurrents.append({"genre": "extremum", "e": a, "v": _sympy_de_py(a["f_py"], sp),
                            "x_mp": _mp_de(_sympy_de_py(a["x_py"], sp), sp, mp)})
    signes = [_comparer(c["v"], y, s, sp, mp) for c in concurrents]
    y_mp = _mp_de(y, sp, mp)
    if any(g > 0 for g in signes):
        candidats = [c for c, g in zip(concurrents, signes) if g > 0]
        rang = [(1 if c["v"] == s * sp.oo else 0) for c in candidats]
        if max(rang) == 0:                                   # valeurs finies : la plus extrême (SymPy), la première à égalité
            meilleure = candidats[0]
            for c in candidats[1:]:
                if _comparer(c["v"], meilleure["v"], s, sp, mp) > 0:
                    meilleure = c
        else:
            meilleure = candidats[rang.index(1)]
        _sonde_depasse(f, meilleure, y_mp, s, sp, mp)
        if meilleure["genre"] == "limite":
            return "pas global", rf"Pas global : \(f(x) \to {meilleure['tex']}\) quand \(x \to {meilleure['ou']}\)."
        a = meilleure["e"]
        return "pas global", (rf"Pas global : le {a['genre']} en \(x = {a['x_tex']}\) est "
                              + ("plus grand." if s > 0 else "plus petit."))
    if any(g == 0 for g in signes):
        return None                                          # cas limite (une limite égale à f(x₀)) : « local » seul
    x0 = _mp_de(_sympy_de_py(e["x_py"], sp), sp, mp)
    _sonde_globale(f, ivs, x0, y_mp, s, sp, mp)
    return "global", _justification_globale(e, s, bornes, autres)


def _approchee_point(e, X, Y, sp):
    """« \\approx \\left(1{,}10\\,;\\,9\\right) » (dans la formule du point, question 15) : chaque coordonnée non entière arrondie
    (approchee : decisions.md §2 et R13), l'entière telle quelle ; "" si les deux sont entières ou si une valeur n'a pas d'écriture
    approchée convenue."""
    if X.is_Integer and Y.is_Integer:
        return ""
    morceaux = []
    for V in (X, Y):
        if V.is_Integer:
            morceaux.append(formater_entier(int(V), tex=True))
        else:
            a = approchee(V, sp)
            if a is None:
                return ""
            morceaux.append(a)
    return rf" \approx \left({morceaux[0]}\,;\,{morceaux[1]}\right)"


def valeur_par_l_exposant(f, e, sp, mp):
    """« g(4) = 18/12 = 3/2, donc f(4) = e^{3/2} ≈ 4,48. » (D11, valeur calculée en chaîne) quand f = e^{u/v} (u, v polynômes écrits
    développés) et x₀ entier ; vérifié : e^{g(x₀)} = f(x₀) (SymPy) et la sonde ; None sinon."""
    if not (isinstance(f, Fn) and f.nom == "exp" and isinstance(f.a, Op) and f.a.op == "/"):
        return None
    P, Q = polynome_ecrit(f.a.a), polynome_ecrit(f.a.b)
    X, Y = _sympy_de_py(e["x_py"], sp), _sympy_de_py(e["f_py"], sp)
    if P is None or Q is None or deg(Q) < 1 or not X.is_Integer:
        return None
    x0 = F(int(X))
    h0, b0 = peval(P, x0), peval(Q, x0)
    if b0 == 0:
        return None
    g0 = h0 / b0
    if sp.simplify(sp.exp(sp.Rational(g0.numerator, g0.denominator)) - Y) != 0:
        return None
    g_mp = mp.mpf(g0.numerator) / g0.denominator
    sonde_g, sonde_f = valeur_mp(f.a, mp.mpf(x0.numerator)), valeur_mp(f, mp.mpf(x0.numerator))
    if sonde_g is None or sonde_f is None or abs(sonde_g - g_mp) > mp.mpf(EGAL) * (1 + abs(g_mp)) \
            or abs(sonde_f - mp.exp(g_mp)) > mp.mpf(EGAL) * (1 + abs(sonde_f)):
        return None
    if b0 == 1 or (g0.numerator == h0 and g0.denominator == b0):
        calcul = qtex(g0)
    else:
        calcul = rf"\frac{{{qtex(h0)}}}{{{qtex(b0)}}} = {qtex(g0)}"
    x = e["x_tex"]
    return _ligne(rf"\(g({x}) = {calcul}\), donc " + formule_approx(rf"f({x}) = {e['f_tex']}", Y, sp) + ".")


# ---------- valeur d'un extremum par substitution (question 41) ----------
def _x0_arbre(X, sp):
    """L'arbre de x₀ (nombre SymPy) quand il est rationnel, ln(q) ou e^{q} (q rationnel) : ce que la substitution sait écrire et
    calculer ; None sinon (3 − 2√2…)."""
    def rationnel(v):
        return v.is_Rational and v.is_finite
    if rationnel(X):
        return nombre(F(int(X.p), int(X.q)))
    if X.func == sp.log and len(X.args) == 1 and rationnel(X.args[0]) and X.args[0] > 0:
        return Fn("ln", nombre(F(int(X.args[0].p), int(X.args[0].q))))
    if X == sp.E:
        return E()
    if X.func == sp.exp and rationnel(X.args[0]):
        return Fn("exp", nombre(F(int(X.args[0].p), int(X.args[0].q))))
    return None


def _feuille(texte):
    """Une feuille qui s'écrit `texte` (substitution ÉCRITE, comme MOINS_X : jamais évaluée)."""
    return Nb(F(0), texte)


def substitution_ecrite(f, x0):
    """L'arbre de f(x₀) tel qu'il s'écrit : x₀ entre parenthèses quand il est négatif, fractionnaire ou base d'une puissance (sauf
    entier positif ou e) ; sans parenthèses en argument d'une fonction ou en exposant (e^{ln(3)}, ln(e^{−1}))."""
    t = tex(x0)
    nu = _feuille(t)
    simple = isinstance(x0, E) or (isinstance(x0, Nb) and x0.v.denominator == 1)
    entre = nu if simple or isinstance(x0, Fn) else _feuille(r"\left(" + t + r"\right)")
    base = nu if simple else _feuille(r"\left(" + t + r"\right)")

    def rec(n, place):
        if isinstance(n, X):
            return {"nu": nu, "base": base}.get(place, entre)
        if isinstance(n, (Nb, E)):
            return n
        if isinstance(n, Neg):
            return Neg(rec(n.a, None))
        if isinstance(n, Fn):
            return Fn(n.nom, rec(n.a, "nu"))
        if n.op == "^":
            return Op("^", rec(n.a, "base"), rec(n.b, "nu"))
        return Op(n.op, rec(n.a, None), rec(n.b, None))
    return rec(f, "nu")


def _sans_somme(n):
    """n ne contient aucune somme ni différence (seulement puissances, produits, quotients, opposés, fonctions)."""
    if isinstance(n, Op):
        return n.op not in "+-" and _sans_somme(n.a) and _sans_somme(n.b)
    if isinstance(n, (Neg, Fn)):
        return _sans_somme(n.a)
    return True


def calculer_produits(n):
    """Première étape du calcul de f(x₀) : les puissances, produits et quotients de nombres sont calculés ((−2)² = 4,
    −2·(−2) = 4), ainsi que e^{ln q} = q, ln(e^{q}) = q, ln(e) = 1, e⁰ = 1, 1·a = a et 0·a = 0 (jamais « 1e^{−1} », qui se lirait
    comme une notation scientifique) ; les sommes restent ((4 − 6)e⁴)."""
    if isinstance(n, (Nb, E, X)):
        return n
    if isinstance(n, Neg):
        a = calculer_produits(n.a)
        m = a.a if isinstance(a, Neg) and isinstance(a.a, Nb) else Neg(a)
    elif isinstance(n, Fn):
        a = calculer_produits(n.a)
        if n.nom == "exp" and isinstance(a, Fn) and a.nom == "ln":
            return a.a
        if n.nom == "ln" and isinstance(a, E):
            return Nb(1)
        if n.nom == "ln" and isinstance(a, Fn) and a.nom == "exp":
            return a.a
        if n.nom == "exp" and valeur_constante(a) == 0:
            return Nb(1)
        m = Fn(n.nom, a)
    else:
        a, b = calculer_produits(n.a), calculer_produits(n.b)
        va, vb = valeur_constante(a), valeur_constante(b)
        if n.op == "^" and isinstance(a, E) and isinstance(b, Fn) and b.nom == "ln":
            return b.a
        if n.op == "^" and isinstance(a, E) and vb == 0:
            return Nb(1)
        if n.op == "*" and (va == 0 or vb == 0):
            return Nb(0)
        if n.op == "*" and (va == 1 or vb == 1):
            return b if va == 1 else a
        m = Op(n.op, a, b)
    if _sans_somme(m) and not isinstance(m, (Nb, E)):
        v = valeur_constante(m)
        if v is not None:
            return nombre(v)
    return m


NOMBRE_FRACTIONNAIRE = re.compile(r"\d\s*\\d?frac")        # un chiffre collé à une fraction : 4\frac{2}{3} (« quatre et deux tiers »)


def _ecriture(t):
    return re.sub(r"\s+", "", t)


def valeur_par_substitution(f, e, sp, mpmath):
    """« f(−2) = ((−2)² − 6)e^{−2·(−2)} = (4 − 6)e⁴ = −2e⁴ ≈ −109,20. » (question 41) : substitution, puis puissances et produits de
    nombres calculés, puis le reste (`plier`), puis l'écriture de l'extremum (f_tex) ; x₀ rationnel, ln(q) ou e^{q}. Chaque membre
    est vérifié égal à f(x₀) par SymPy (calcul exact) et par la sonde mpmath ; None sinon (aucune ligne)."""
    mp = mpmath.mp
    X, Y = _sympy_de_py(e["x_py"], sp), _sympy_de_py(e["f_py"], sp)
    x0 = _x0_arbre(X, sp)
    if x0 is None or _ecriture(tex(x0)) != _ecriture(e["x_tex"]):
        return None
    fe = en_sympy_reel(f)
    V = fe.subs(SYMPY["x"], X)
    if V.has(sp.zoo, sp.nan, sp.oo, -sp.oo) or V.is_real is not True or sp.simplify(V - Y) != 0:
        return None
    reference = _mp_de(V, sp, mp)
    seuil = mp.mpf(EGAL) * (1 + abs(reference))
    sonde_f = valeur_mp(f, _mp_de(X, sp, mp))
    if sonde_f is None or abs(sonde_f - reference) > seuil:
        return None
    reel = substituer(f, x0)
    etape = calculer_produits(reel)
    membres = [(tex(substitution_ecrite(f, x0)), reel), (tex(etape), etape)]
    fin = plier(etape)                      # les sommes calculées : écrites si elles donnent un nombre ou l'écriture de l'extremum
    if valeur_constante(fin) is not None or _ecriture(tex(fin)) == _ecriture(e["f_tex"]):
        membres.append((tex(fin), fin))
    for _, T in membres:                     # chaque membre égal à f(x₀) : SymPy exact, puis la sonde
        d = en_sympy_reel(T) - V
        if not (d == 0 or sp.simplify(d) == 0):
            return None
        sonde = valeur_mp(T, mp.mpf(0))
        if sonde is None or abs(sonde - reference) > seuil:
            return None
    ecrits = []
    for t, _ in membres:
        if NOMBRE_FRACTIONNAIRE.search(t):
            return None                     # « 2\frac{1}{2} » se lirait 2 + 1/2 : aucune ligne plutôt qu'une écriture ambiguë
        if not ecrits or _ecriture(t) != _ecriture(ecrits[-1]):
            ecrits.append(t)
    if _ecriture(ecrits[-1]) == _ecriture(e["f_tex"]):
        ecrits[-1] = e["f_tex"]
    else:
        ecrits.append(e["f_tex"])           # égale à f(x₀) : f_py = Y, vérifié ci-dessus (SymPy et sonde)
    if len(ecrits) < 2:
        return None
    return _ligne(formule_approx(rf"f({e['x_tex']}) = " + " = ".join(ecrits), Y, sp) + ".")


def _ligne_extremum(e, crit, cellules, statut, sp, mp, f):
    """(ligne, ligne du bilan) : « Maximum global en x = 0 : (0 ; 1) (f′ passe de + à −). Les autres valeurs … » quand c'est
    prouvé, « Maximum local en … Pas global : … », sinon « Maximum local en … » seul (decisions.md §2 révisé, question 43) ; le bilan
    (D20) en garde la nature et le point, sans la justification : « Maximum local en x = 0 : (0 ; e^{1/6}) ≈ (0 ; 1,18) »."""
    x = e["x_tex"]
    t = ""
    if "f_py" in e:
        X, Y = _sympy_de_py(e["x_py"], sp), _sympy_de_py(e["f_py"], sp)
        sonde = valeur_mp(f, _mp_de(X, sp, mp))
        if sonde is not None and abs(sonde - _mp_de(Y, sp, mp)) <= mp.mpf(EGAL) * (1 + abs(sonde)):
            t += rf" : \(\left({x}\,;\,{e['f_tex']}\right){_approchee_point(e, X, Y, sp)}\)"
        else:
            t += rf" : \(\left({x}\,;\,{e['f_tex']}\right)\)"
            statut = None                                    # la sonde ne retrouve pas f(x₀) : ni ≈ ni « global »
    elif e["f_tex"] != "?":
        t += rf" : \(f({x}) {'' if e['f_tex'].startswith('{' + chr(92) + 'approx}') else '= '}{e['f_tex']}\)"
    point = t
    if x in crit:
        i = crit.index(x)
        g, d = cellules[2 * i], cellules[2 * i + 2]
        if g in ("+", "-") and d in ("+", "-") and g != d:
            t += rf" (\(f'\) passe de \({g}\) à \({d}\))"
    t += "."
    portee = "global" if statut is not None and statut[0] == "global" else "local"
    nom = ("Maximum " if e["genre"].startswith("maximum") else "Minimum ") + portee
    debut = rf"<b>{nom}</b> en \(x = {x}\)"
    t = debut + t
    if statut is not None:
        t += " " + statut[1]
    return t, debut + point


def blocs_extremums(dv, limites, analyse):
    """Partie 5 (D11) : les blocs qui remplacent la liste des extremums de l'outil Dérivée dans la carte « Signe de f′ et variations »
    de l'Étude complète : valeurs calculées en chaîne par l'exposant (quand la carte « Dérivée » a nommé g), puis une ligne par
    extremum « Maximum local en x = 0 : (0 ; e^{1/6}) ≈ (0 ; 1,18) (f′ passe de + à −). Pas global : … » ; None (liste de l'outil
    Dérivée) si SymPy ou mpmath manque ou si la rédaction échoue."""
    r = partie5(dv, limites, analyse)
    return None if r is None else r["blocs"]


def partie5(dv, limites, analyse):
    """Les extremums de la partie 5 (D11) : {"blocs" (voir `blocs_extremums`), "bilan" (une ligne par extremum, nature et point,
    D20)} ; None si la rédaction D11 n'est pas faite (liste de l'outil Dérivée)."""
    extrema = dv.get("extrema") or []
    if not extrema or not dv.get("signe_resolu"):
        return None
    _, f, ED = analyse
    sp = charger_sympy()
    try:
        import mpmath
    except ImportError:
        return None
    if sp is None:
        return None
    mp = mpmath.mp
    ivs = fusion(ED)
    crit = dv["table_signe"]["crit"]
    cellules = next(l["cells"] for l in dv["table_signe"]["rows"] if l.get("final"))
    g_nomme = any(b.get("type") == "sous_calcul" and b.get("titre") == "Dérivée de l'exposant" for b in dv.get("deriv_etapes", []))
    with mpmath.workdps(CHIFFRES):
        try:
            blocs, items, bilan = [], [], []
            for e in extrema:
                ligne, statut = None, None
                if "f_py" in e:
                    try:                                  # g nommé : g(x₀) d'abord (P7b) ; sinon la substitution (question 41)
                        ligne = (valeur_par_l_exposant(f, e, sp, mp) if g_nomme else None) or valeur_par_substitution(f, e, sp, mpmath)
                    except Exception:
                        ligne = None
                    try:
                        statut = statut_global(e, extrema, ivs, crit, cellules, limites or {}, f, sp, mp)
                    except Exception:                     # Doute, SymPy ou mpmath en échec : « local » seul
                        statut = None
                if ligne is not None:
                    blocs.append(ligne)
                ligne_e, court = _ligne_extremum(e, crit, cellules, statut, sp, mp, f)
                items.append(ligne_e)
                bilan.append(court)
        except Exception:
            return None
    return {"blocs": blocs + [so.liste(items, style="extrema")], "bilan": bilan}


# ---------------------------------------------------------------------------------------------------------------------------
# Partie 6. Bilan de l'étude (D20)
# ---------------------------------------------------------------------------------------------------------------------------
TITRE_BILAN = "Bilan de l'étude"
PARITES = {"paire": "f est paire", "impaire": "f est impaire", "ni": "f n'est ni paire ni impaire"}      # mots de la partie 2


def lignes_bilan(ed_tex, parite, partie3, asymptotes, extremums):
    """Les lignes de la carte « Bilan de l'étude » (D20), dans l'ordre de D20, chacune terminée par la partie d'où elle vient :
    ED (partie 1) ; parité (partie 2) ; zéros, signe, f(0) (partie 3) ; chaque asymptote, avec la position (partie 4) ; chaque
    extremum, nature et point (partie 5). Aucun calcul : chaque ligne reprend un résultat que sa partie a écrit et confirmé
    (`ed_tex` de l'étude ; `partie2(…)["conclusion"]` ; `partie3(…)["bilan"]` ; les lignes du bilan des asymptotes de l'outil
    Limites ; `partie5(…)["bilan"]` ou la liste de l'outil Dérivée). Une donnée None (la partie ne conclut pas) : pas de ligne."""
    lignes = [(rf"\(ED = {ed_tex}\)", 1)]
    if parite in PARITES:
        lignes.append((f"Parité : {PARITES[parite]}", 2))
    p3 = partie3.get("bilan") or {}
    if p3.get("zeros") is not None:
        lignes.append(("Zéros : " + (" ; ".join(p3["zeros"]) or "aucun"), 3))
    if p3.get("signe") is not None:
        lignes.append(("Signe : " + p3["signe"], 3))
    if p3.get("f0") == HORS_ED:
        lignes.append((r"Ordonnée à l'origine : aucune, car \(0 \notin ED\)", 3))
    elif p3.get("f0") is not None:
        lignes.append(("Ordonnée à l'origine : " + p3["f0"], 3))
    lignes += [(a, 4) for a in asymptotes]
    lignes += [(e, 5) for e in extremums or []]
    return [f"{t[:-1] if t.endswith('.') else t} (partie {k})" for t, k in lignes]          # « … parabolique. » : sans le point


def carte_bilan(ed_tex, parite, partie3, asymptotes, extremums):
    """La carte « Bilan de l'étude » (D20), avant le graphique : voir `lignes_bilan`. Style `final` (cadre du résultat final)."""
    return so.carte(TITRE_BILAN, [so.liste(lignes_bilan(ed_tex, parite, partie3, asymptotes, extremums), style="bilan")], style="final")


# ---------------------------------------------------------------------------------------------------------------------------
# Partie 6. Graphe (D15) : ronds vides
# ---------------------------------------------------------------------------------------------------------------------------
SIGNE_D_APPROCHE = re.compile(r"\^\{([+-])\}$")
SONDES_ROND = range(3, 13)              # f(a ± 10⁻ᵏ), k = 3 … 12
PRES_DU_ROND = "1e-6"                   # écart relatif à L, au plus près de a, sous lequel la sonde tient la limite pour atteinte


def _reelle_ou_infinie(L, sp):
    if L in (sp.oo, -sp.oo) or (L.is_real and L.is_finite):
        return L
    raise Doute()                               # bornes oscillantes, nombre complexe, limite non trouvée…


def limite_laterale(fe, a, cote, sp):
    """Limite de fe (SymPy) en a (exact) du côté `cote` ('-' ou '+'), calculée par SymPy, par les règles de calcul des limites
    quand elles s'appliquent : e^{u} donne e^{lim u} (exp est continue, e^{−∞} = 0, e^{+∞} = +∞) ; un produit (une somme) dont chaque
    facteur (terme) a une limite finie, le produit (la somme) des limites ; sinon la limite de l'expression entière. Beaucoup plus
    rapide que la limite de e^{u} elle-même (Ex7 : 3 ms au lieu de 200 ; x·e^{1/(x − 1)} : 10 ms au lieu de 1,2 s). Doute si le
    résultat n'est ni un réel ni ±∞."""
    x = SYMPY["x"]
    if fe.func == sp.exp:
        return sp.exp(limite_laterale(fe.args[0], a, cote, sp))
    if fe.is_Mul or fe.is_Add:
        try:
            morceaux = [limite_laterale(t, a, cote, sp) for t in fe.args]
        except Doute:
            morceaux = None                     # un morceau sans limite : la limite de l'expression entière décide
        if morceaux is not None and all(m.is_finite for m in morceaux):
            return _reelle_ou_infinie(sp.Mul(*morceaux) if fe.is_Mul else sp.Add(*morceaux), sp)
    return _reelle_ou_infinie(sp.limit(fe, x, a, cote), sp)


def _sonde_rond(f, a, cote, L, signe, mp):
    """Sonde mpmath (30 chiffres) : f(a ± 10⁻ᵏ) est définie, s'approche de L (écarts qui ne croissent pas, le plus proche sous
    10⁻⁶ en relatif) et, si le tableau écrit un signe d'approche (0⁺), se trouve du bon côté de L ; Doute sinon."""
    s = 1 if cote == "+" else -1
    ecarts = []
    for k in SONDES_ROND:
        v = valeur_mp(f, a + s * mp.mpf(10) ** -k)
        if v is None:
            raise Doute()
        e = v - L
        if signe is not None and (e == 0 or (e > 0) != (signe == "+")):
            raise Doute()
        ecarts.append(abs(e))
    if ecarts[-1] > mp.mpf(PRES_DU_ROND) * (1 + abs(L)) or any(b > a_ for a_, b in zip(ecarts[-5:], ecarts[-4:])):
        raise Doute()


def ronds_vides(analyse, bornes, asymptotes):
    """D15 : [[a, L]], un rond vide en (a ; L) pour chaque point exclu a dont la limite L d'un côté est finie (Ex7 : (2 ; 0) à gauche ;
    d : (−2 ; 0) et (2 ; 0) ; x/√(x²) : (0 ; −1) et (0 ; 1)), en plus des « trous » de l'outil Limites (déjà dessinés, non repris).
    `bornes` : les limites aux bornes finies de l'ED (celles du tableau T06c, une seule source) ; `asymptotes` : celles de la partie
    Limites. Le rond est une affirmation nouvelle (principe 0.2) : L se lit sur la liste fermée de `lire_limite`, a est exclu de l'ED
    (décidé exactement), SymPy donne exactement L (`limite_laterale`) et la sonde mpmath s'en approche du bon côté ; sinon pas de
    rond. Sans SymPy ou sans mpmath : aucun rond."""
    _, f, ED = analyse
    sp = charger_sympy()
    try:
        import mpmath
    except ImportError:
        return []
    if sp is None:
        return []
    mp = mpmath.mp
    ivs = fusion(ED)
    trous = [a["point_val"] for a in asymptotes if a.get("genre") == "trou" and a.get("point_val") is not None]
    exclus = [p for iv in ivs for p in (iv.lo, iv.hi) if p is not None]
    out = []
    with mpmath.workdps(CHIFFRES):
        fe = None
        for b in bornes:
            if b.get("type") != "fini" or any(proche(b["point_val"], t) for t in trous):
                continue
            borne = next((p for p in exclus if proche(p.val, b["point_val"])), None)
            for nom, cote in (("gauche", "-"), ("droite", "+")):
                t = b.get(nom)
                if borne is None or t is None:
                    continue
                L = lire_limite(t, sp)
                if L is None or L in (sp.oo, -sp.oo):
                    continue
                try:
                    a = _sympy_num(borne, sp)
                    if appartient(ivs, a, sp):
                        continue                                # a ∈ ED : pas un point exclu
                    fe = en_sympy_reel(f) if fe is None else fe
                    if sp.simplify(limite_laterale(fe, a, cote, sp) - L) != 0:
                        continue
                    m = SIGNE_D_APPROCHE.search(t.replace(" ", ""))
                    _sonde_rond(f, _mp_de(a, sp, mp), cote, _mp_de(L, sp, mp), m.group(1) if m else None, mp)
                except Exception:                               # Doute, SymPy ou mpmath en échec : pas de rond
                    continue
                point = [float(b["point_val"]), float(L)]
                if point not in out:
                    out.append(point)
    return out
