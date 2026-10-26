"""
nombres.py — Notation suisse des nombres (décision Q5 du 14.10.2026, appliquée à l'outil Exponentielles et logarithmes le 26.10.2026).

    Séparateur de milliers : apostrophe typographique ’ (U+2019) dès 4 chiffres, sur la PARTIE ENTIÈRE seulement :
        1’000    99’999’995    1’234,567    0,0001 (jamais de séparateur dans les décimales)
    Virgule décimale : « , » en texte, « {,} » en TeX. Séparateur de milliers en TeX : \\text{’}.
    Saisie : « 1'000 » et « 1’000 » sont lus 1000 (apostrophe suivie d'exactement 3 chiffres) ; « 1 000 » est refusé par l'outil
    (message clair) plutôt que lu 1·000.

Python pur, bibliothèque standard seulement. Fonctions réutilisables par les autres outils (T23).
"""
import re

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
