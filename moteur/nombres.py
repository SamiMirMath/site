"""
nombres.py — Notation suisse des nombres (décision Q5 du 14.10.2026, appliquée à l'outil Exponentielles et logarithmes le 26.10.2026).

    Séparateur de milliers : apostrophe typographique ’ (U+2019) dès 4 chiffres, sur la PARTIE ENTIÈRE seulement :
        1’000    99’999’995    1’234,567    0,0001 (jamais de séparateur dans les décimales)
    Virgule décimale : « , » en texte, « {,} » en TeX. Séparateur de milliers en TeX : \\text{’}.
    Saisie : « 1'000 » et « 1’000 » sont lus 1000 (apostrophe suivie d'exactement 3 chiffres) ; « 1 000 » est refusé par l'outil
    (message clair) plutôt que lu 1·000.

Valeurs affichées (règle R13 du guide de rédaction ; décisions D13, D25 et E14 du 2e degré ; chantier briques-communes, B5) :
    approx(x, decimales=3)            valeur approchée « ≈ » en TeX : 1{,}414 ; 1\\text{’}234{,}568 ; 3{,}162 \\times 10^{-5}
    exact(x, decimaux_enonce=False)   valeur exacte en TeX : \\frac{1}{3}, -\\frac{5}{2}, 4\\text{’}913 ; 1{,}9025 si l'énoncé a des décimaux
Ce sont les fonctions uniques que les nouveaux outils appellent (A5). Aucun outil existant ne les appelle encore : les cinq formats
de « ≈ » des outils (`exp_log.tex_approx`, `ensemble_def.dec`, `parties.approchee`, `redaction_bh.fmt_approx` et `fmt_val`) se
rebrancheront outil par outil (R9). Les écarts voulus avec `exp_log.tex_approx` sont nommés dans `tests/python/test_nombres.py`.

Python pur, bibliothèque standard seulement. Fonctions réutilisables par les autres outils (T23). Aucun état : tout réglage est un
paramètre (A7), aucune variable de module n'est modifiée.
"""
import math
import re
from decimal import Decimal
from fractions import Fraction

SEPARATEUR = "’"
SEPARATEUR_TEX = r"\text{’}"
VIRGULE_TEX = "{,}"

# un nombre saisi : milliers avec apostrophe (1'000, 1’234,5), sinon chiffres avec décimales éventuelles, sinon « ,5 »
MOTIF_SAISIE = re.compile(r"\d{1,3}(?:['’]\d{3})+(?:[.,]\d+)?|\d+(?:[.,]\d+)?|[.,]\d+")
# un nombre entier suivi d'un espace puis de 3 chiffres (« 1 000 », « 7 200 000 ») : à refuser
MOTIF_ESPACE_DANS_UN_NOMBRE = re.compile(r"[^\S\n]+\d{3}(?!\d)")


def grouper(chiffres, separateur=SEPARATEUR):
    """Regroupe par 3 en partant de la droite, dès 4 chiffres : '1234567' → '1’234’567' ; '999' → '999'."""
    n = len(chiffres)
    if n < 4:
        return chiffres
    tete = n % 3 or 3
    return separateur.join([chiffres[:tete]] + [chiffres[i:i + 3] for i in range(tete, n, 3)])


def formater_entier(n, tex=False):
    """Un entier (int) en notation suisse ; tex=True : séparateur \\text{’} pour une formule TeX."""
    sep = SEPARATEUR_TEX if tex else SEPARATEUR
    chiffres = grouper(str(abs(int(n))), sep)
    return "-" + chiffres if n < 0 else chiffres


def formater_decimal(texte, tex=False):
    """Un nombre écrit avec « . » ou « , » (« -1234.567 », « 0,01 ») en notation suisse : milliers sur la partie entière seulement,
    virgule décimale (« {,} » en TeX). Les décimales ne sont jamais séparées."""
    s = texte.strip().replace(".", ",")
    signe = "-" if s.startswith("-") else ""
    entier, _, decimales = s.lstrip("-").partition(",")
    sep = SEPARATEUR_TEX if tex else SEPARATEUR
    r = signe + grouper(entier or "0", sep)
    if decimales or "," in s:
        r += (VIRGULE_TEX if tex else ",") + decimales
    return r


def nettoyer_saisie(texte):
    """« 1’234,5 » ou « 1'234.5 » → « 1234.5 » (chaîne lisible par Fraction)."""
    return texte.replace("'", "").replace("’", "").replace(",", ".")


# ---------------------------------------------------------------------------------------------------------------------
# Valeurs affichées : approchées (« ≈ ») et exactes (R13, E14, D25)
# ---------------------------------------------------------------------------------------------------------------------
PLAFOND_DECIMAL = 10 ** 6         # dès 10⁶ (valeur arrondie comprise) : notation scientifique (R13, E14)
DECIMALES_EXACTES_MAX = 8        # un décimal fini plus long reste une fraction (même règle qu'Exp-log, `_nb_exact`)


def _valeur_exacte_de(x):
    """La valeur de x en Fraction, exactement (int, Fraction, Decimal, float : sa valeur binaire) ; un autre nombre réel (SymPy,
    mpmath) par float(x). ValueError si elle n'est pas finie."""
    if isinstance(x, (int, Fraction)):
        return Fraction(x)
    if isinstance(x, Decimal):
        if not x.is_finite():
            raise ValueError(f"valeur non finie : {x!r}")
        return Fraction(x)
    try:
        v = float(x)
    except OverflowError:
        raise ValueError(f"valeur trop grande : {x!r}") from None
    if not math.isfinite(v):
        raise ValueError(f"valeur non finie : {x!r}")
    return Fraction(v)


def _arrondi(q, decimales):
    """|q| arrondi à `decimales` décimales, compté en unités de 10^(−decimales) (entier) ; la moitié est arrondie au-dessus."""
    a = abs(q) * 10 ** decimales
    return (2 * a.numerator + a.denominator) // (2 * a.denominator)


def _ecrire(k, decimales, signe):
    """k unités de 10^(−decimales) en TeX : 1234568, 3 → 1\\text{’}234{,}568."""
    chiffres = str(k).rjust(decimales + 1, "0")
    return formater_decimal(signe + chiffres[:-decimales] + "," + chiffres[-decimales:], tex=True)


def approx(x, decimales=3):
    """Valeur approchée de x en TeX, pour l'écrire après « \\approx » (R13, E14 ; D25 pour l'apostrophe).

    - Entre 10^(−decimales) et 10⁶ : `decimales` décimales (3 par défaut), virgule décimale, apostrophe dès 4 chiffres sur la partie
      entière : 1{,}414 ; -0{,}500 ; 1\\text{’}234{,}568 ; 999\\text{’}999{,}600.
    - Sous 10^(−decimales) et dès 10⁶ (la valeur arrondie compte : 999 999,9996 s'écrit 1 \\times 10^{6}) : notation scientifique,
      mantisse à `decimales` décimales (4 chiffres significatifs par défaut) : 3{,}162 \\times 10^{-5} ; 4{,}500 \\times 10^{6} ; une
      mantisse entière perd ses décimales nulles, comme R13 et `exp_log.tex_approx` : 1 \\times 10^{10} ; 2 \\times 10^{7} ; une mantisse
      arrondie à 10 devient 1 × 10ⁿ⁺¹ : 0,00099999 s'écrit 1 \\times 10^{-3}.
    - Arrondi calculé exactement (fractions) ; une valeur exactement à mi-chemin est arrondie au-dessus en valeur absolue (arrondi
      usuel : 0,0625 ≈ 0,063 ; 9 999 500 ≈ 1,000 × 10⁷), et comme `parties.arrondi` d'Étude complète (ROUND_HALF_UP).
    - 0 s'écrit 0{,}000 (et −0,0 aussi). Signe moins « - » de TeX, comme le reste du site.

    x : int, Fraction, Decimal ou float (valeur prise exactement : la valeur binaire du float), ou un autre nombre réel que float()
    convertit (SymPy, mpmath). decimales : entier ≥ 1. ValueError pour une valeur non finie (infinie, NaN), ou trop grande
    pour un float quand elle passe par float() : rien de faux à l'écran.
    Égal à `exp_log.tex_approx` hors des écarts voulus, nommés dans `tests/python/test_nombres.py`."""
    if isinstance(decimales, bool) or not isinstance(decimales, int) or decimales < 1:
        raise ValueError(f"decimales doit être un entier ≥ 1, pas {decimales!r}")
    q = _valeur_exacte_de(x)
    signe = "-" if q < 0 else ""
    if q == 0:
        return _ecrire(0, decimales, "")
    if abs(q) * 10 ** decimales >= 1:
        k = _arrondi(q, decimales)
        if k < PLAFOND_DECIMAL * 10 ** decimales:
            return _ecrire(k, decimales, signe)
    a = abs(q)
    e = len(str(a.numerator)) - len(str(a.denominator))           # 10^e ≤ |q| < 10^(e+1), exactement
    if a < Fraction(10) ** e:
        e -= 1
    k = _arrondi(a / Fraction(10) ** e, decimales)
    if k >= 10 ** (decimales + 1):                                # mantisse arrondie à 10 : 1 × 10ⁿ⁺¹
        e += 1
        k = _arrondi(a / Fraction(10) ** e, decimales)
    if k % 10 ** decimales == 0:                                  # mantisse entière : sans décimales nulles (R13 : 1 × 10¹⁰)
        mantisse = signe + str(k // 10 ** decimales)
    else:
        mantisse = _ecrire(k, decimales, signe)
    return mantisse + r" \times 10^{" + str(e) + "}"


def _decimales_finies(denominateur):
    """Nombre de décimales de l'écriture décimale finie d'une fraction de ce dénominateur (positif), None s'il n'y en a pas."""
    d, k2, k5 = denominateur, 0, 0
    while d % 2 == 0:
        d, k2 = d // 2, k2 + 1
    while d % 5 == 0:
        d, k5 = d // 5, k5 + 1
    return max(k2, k5) if d == 1 else None


def exact(x, decimaux_enonce=False):
    """Valeur exacte de x en TeX (R13, E14), notation suisse (apostrophe dès 4 chiffres, D25), signe « - » devant :

    - un entier : 4\\text{’}913 ; -3 ;
    - sinon une fraction : \\frac{1}{3} ; -\\frac{5}{2} ; \\frac{1}{1\\text{’}000} (valeur calculée à partir d'entiers) ;
    - decimaux_enonce=True (l'énoncé contient un décimal ; réglé par la lecture de la saisie, A7) : un décimal fini d'au plus
      8 décimales s'écrit en décimal (1{,}9025 ; -0{,}27 ; 1\\text{’}234{,}5) ; une valeur qui n'est pas un décimal fini (13/60), ou plus
      longue, reste une fraction.

    Les décimaux de l'énoncé gardent leur écriture (« 0,50 ») : c'est l'arbre de la saisie qui la garde (`expr.Nb.dec`), pas cette
    fonction, qui écrit les valeurs calculées (même règle qu'`exp_log._nb_exact`, sans son état `_DECIMAUX`).
    x : int, Fraction ou Decimal fini (ou une chaîne que Fraction lit, « 13/60 ») ; un float est refusé (TypeError) : sa valeur binaire
    n'est pas la valeur exacte."""
    if isinstance(x, float):
        raise TypeError(f"valeur exacte attendue (int, Fraction, Decimal), pas un float : {x!r}")
    if isinstance(x, Decimal) and not x.is_finite():
        raise ValueError(f"valeur non finie : {x!r}")
    v = Fraction(x)
    signe = "-" if v < 0 else ""
    a = abs(v)
    if a.denominator == 1:
        return signe + formater_entier(a.numerator, tex=True)
    k = _decimales_finies(a.denominator) if decimaux_enonce else None
    if k is not None and k <= DECIMALES_EXACTES_MAX:
        chiffres = str(a.numerator * 10 ** k // a.denominator).rjust(k + 1, "0")
        return signe + formater_decimal(chiffres[:-k] + "," + chiffres[-k:], tex=True)
    return signe + r"\frac{" + formater_entier(a.numerator, tex=True) + "}{" + formater_entier(a.denominator, tex=True) + "}"
