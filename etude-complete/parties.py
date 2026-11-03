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
"""
from fractions import Fraction as F
from math import gcd, isqrt

from noyau import X, Fn, Op, tex, ptex, qtex, decomposer, deg, pn, pmul, evaluer, conditions, NonPrisEnCharge, ErreurSaisie
import sortie as so
import resoudre_ed

__all__ = ["cartes_domaine", "mise_en_forme", "resolution_denominateur"]

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


def factorisation(P):
    """Factorisation d'un polynôme à coefficients entiers, coefficient dominant positif, avec les méthodes du cours :
    mise en évidence de c·xᵏ (c = pgcd des coefficients), puis Somme-Produit pour un trinôme unitaire à deux racines entières
    distinctes (facteurs rangés par racine croissante : (x + 2)(x − 1)).
    Résultat : ([(écriture, méthode)], écriture finale, valeur) : les lignes de la chaîne (vide si rien ne se factorise) et la valeur de
    l'écriture finale calculée à partir de ses facteurs (fonction float → float, pour la sonde numérique) ; None quand rien ne se factorise."""
    P = pn(P)
    if deg(P) < 1 or P[-1] <= 0:
        return [], ptex(P, "x"), None
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
        return [], ptex(P, "x"), None
    produit = [F(0)] * k + [c]                      # garde-fou exact : le produit développé redonne P
    for h in facteurs:
        produit = pmul(produit, h)
    if pn(produit) != P:
        return [], ptex(P, "x"), None
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
