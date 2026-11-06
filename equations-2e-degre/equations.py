"""
equations.py — Outil « Équations du 2e degré » : lecture et analyse de la saisie (chantier equations-2e-degre, P3 ; decisions.md,
D23, § 4 et § 13.5).

    LEXIQUE_EQ        la lecture commune (moteur/expr.py) avec les messages de l'outil : saisie vide, exposant (exemple x^2) ; sqrt
                      et √ restent lus (fonctions=("sqrt",)) pour que l'analyse refuse une racine avec son propre message
    analyser(texte)   (gauche, droite, inconnue, decimaux_enonce), ou ErreurSaisie avec le premier message du § 13.5, dans cet ordre :
                      saisie vide, syntaxe, pas de « = », aucune lettre, plusieurs lettres, inconnue en exposant, inconnue sous une
                      racine ou au dénominateur ou exposant non entier ou négatif, racine sans l'inconnue, division par 0, bornes

L'inconnue est la lettre saisie (D23 : x, t, y, z, u…), une seule. `decimaux_enonce` dit si la saisie contient un nombre écrit en
décimal (E14 : les résultats qui en découlent restent décimaux quand ils le sont) ; la résolution le reçoit en paramètre (A7).
La résolution elle-même est `second_degre.resoudre_equation` ; l'adaptateur de la page vient en P5.

Aucun état : aucune variable de module n'est modifiée (A7).
"""
from expr import Fn, Lexique, Neg, Op, Pow, a_des_decimaux, lire_membres, variables
from noyau import ErreurSaisie
from polynomes import const
from second_degre import HorsBornes, vers_polynome

__all__ = ["LEXIQUE_EQ", "analyser", "MESSAGES_SAISIE"]

MESSAGE_EXPOSANT = "Mettez l'exposant entre parenthèses, ou séparez-le du facteur suivant avec * : x^2*(x+1)."

LEXIQUE_EQ = Lexique(fonctions=("sqrt",), message_vide="Écrivez une équation.", message_exposant=MESSAGE_EXPOSANT)

MESSAGES_SAISIE = {                                                       # § 4 et § 13.5, dans l'ordre de priorité (vouvoiement, R12)
    "sans_egal": "Écrivez une équation, avec le signe « = ».",
    "sans_lettre": "Écrivez une équation avec une inconnue.",
    "plusieurs_lettres": "Écrivez une équation avec une seule inconnue.",
    "exposant": "L'inconnue est en exposant : utilisez l'outil « Exponentielles et logarithmes ».",
    "prochaine_version": ("Les équations avec une fraction ou une racine contenant l'inconnue seront traitées dans une prochaine "
                          "version."),
    "racine": "Écrivez une équation dont les coefficients n'ont pas de racine.",
    "division_par_0": "Division par 0 : vérifiez la saisie.",
    "bornes": "Cette équation dépasse ce que l'outil sait traiter.",
}
ORDRE = ("exposant", "prochaine_version", "racine", "division_par_0")       # les problèmes lus dans l'arbre, du plus prioritaire


def _problemes(n, x):
    """Les problèmes de l'arbre n (inconnue x) : sous-ensemble d'ORDRE."""
    if isinstance(n, Neg):
        return _problemes(n.a, x)
    if isinstance(n, Fn):                                                 # sqrt, seule fonction lue
        return _problemes(n.a, x) | {"prochaine_version" if x in variables(n.a) else "racine"}
    if isinstance(n, Op):
        p = _problemes(n.a, x) | _problemes(n.b, x)
        if n.op == "/":
            if x in variables(n.b):
                p.add("prochaine_version")
            elif not p and const(n.b) == 0:
                p.add("division_par_0")
        return p
    if isinstance(n, Pow):
        p = _problemes(n.a, x) | _problemes(n.b, x)
        if x in variables(n.b):
            return p | {"exposant"}
        if p:
            return p
        k = const(n.b)
        if k is None:                                                     # exposant constant hors des rationnels (2^(2^100) : bornes)
            return p
        if x in variables(n.a):
            if k.denominator != 1 or k < 0:
                p.add("prochaine_version")
        elif k.denominator != 1:                                          # 2^(1/2) : une racine écrite comme une puissance
            p.add("racine")
        elif k < 0 and const(n.a) == 0:
            p.add("division_par_0")
        return p
    return set()


def analyser(texte):
    """(gauche, droite, inconnue, decimaux_enonce) d'une équation saisie, ou ErreurSaisie (message du § 13.5, le premier dans
    l'ordre de priorité). La résolution (degré, structure, méthodes) n'est pas faite ici."""
    g, d = lire_membres(texte, LEXIQUE_EQ)                                # saisie vide, syntaxe
    if d is None:
        raise ErreurSaisie(MESSAGES_SAISIE["sans_egal"])
    lettres = sorted(variables(g) | variables(d))
    if not lettres:
        raise ErreurSaisie(MESSAGES_SAISIE["sans_lettre"])
    if len(lettres) > 1:
        raise ErreurSaisie(MESSAGES_SAISIE["plusieurs_lettres"])
    x = lettres[0]
    problemes = _problemes(g, x) | _problemes(d, x)
    for p in ORDRE:
        if p in problemes:
            raise ErreurSaisie(MESSAGES_SAISIE[p])
    try:
        for membre in (g, d, Op("-", g, d)):
            vers_polynome(membre, x)
    except HorsBornes:
        raise ErreurSaisie(MESSAGES_SAISIE["bornes"]) from None
    return g, d, x, a_des_decimaux(g) or a_des_decimaux(d)
