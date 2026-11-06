"""
resoudre_eq.py — Adaptateur « format de sortie commun » (moteur/sortie.py) de l'outil Équations du 2e degré (chantier
equations-2e-degre, P5 ; decisions.md, § 5 et § 13).

La saisie est lue par equations.analyser (messages du § 4 et du § 13.5), puis résolue par second_degre.resoudre_equation. La page est
construite uniquement à partir des étapes (§ 5) : une carte par étape (R1, question 36 de suivi.md), « Étape k » avec un badge court
(comme Exp-log et Factorisation ; noms du rappel de la page), dévoilées une à une par « Étape suivante » : les cartes de
`second_degre.cartes` (la chaîne du corrigé coupée aux étapes, le pivot en membre de gauche), puis la carte « Solution » (S encadré,
D29 ; la ligne ≈, E14 ; carte normale, § 13.3). Quand le chemin du cours n'utilise pas la formule, une seconde résolution « Par la
formule » (E12), découpée de même, est proposée par le sélecteur de méthode de la page (`sortie_ok_variantes`, « Méthodes du cours »
par défaut). Une équation non résolue (bicarrée, hors du cours, forme non traitée par l'outil, bornes, garde-fou
en échec) donne une erreur au message du § 4 : jamais une étape fausse ni une valeur donnée comme solution. L'énoncé est écrit par
`second_degre.ecrire_enonce` (ses produits côte à côte, comme le corrigé : question 26 de suivi.md).

    resoudre(entree)      la sortie commune (dict)
    resoudre_json(entree) la même, en JSON strict (la page appelle JSON.parse)
    apercu_json(texte)    l'aperçu de la saisie pendant la frappe : seulement la lecture (syntaxe) ; {ok, tex} ou {ok: false, erreur}

Aucun état : aucune variable de module n'est modifiée (A7).
"""
from chaine import Eq, tex_element
from expr import lire_membres, tex
from noyau import ErreurSaisie, json_strict
import second_degre as sd
import sortie as so
from equations import LEXIQUE_EQ, analyser

__all__ = ["resoudre", "resoudre_json", "apercu_json", "LIBELLES", "VARIANTE_DEFAUT", "TITRES", "titre"]

VARIANTE_DEFAUT = "cours"
LIBELLES = {"cours": "Méthodes du cours", "formule": "Par la formule"}         # D2, E12

# badge de la carte d'une étape (phase, méthode) ; {x} : l'inconnue
TITRES = {("ramener", "RAMENER"): "Ramener à 0", ("ramener", "DEVELOPPER"): "Développer", ("isoler", "ISOLER"): "Isoler {x}",
          ("factoriser", "ME"): "Mise en évidence", ("factoriser", "ME_PUISSANCE"): "Mise en évidence",
          ("factoriser", "IDREM_DIFF"): "Identité remarquable", ("factoriser", "IDREM_PLUS"): "Identité remarquable",
          ("factoriser", "IDREM_MOINS"): "Identité remarquable", ("factoriser", "SP"): "Somme-Produit",
          ("factoriser", "TATONNEMENT"): "Tâtonnement", ("factoriser", "FORMULE"): "Formule",
          ("delta_valeur", "FORMULE"): "Discriminant", ("delta_nombre", "FORMULE"): "Valeurs de {x}",
          ("produit_nul", "PRODUIT_NUL"): "Produit nul"}


def titre(etape, x):
    """Le badge de la carte d'une étape (KeyError pour une étape inconnue : jamais un badge faux)."""
    return TITRES[(etape["phase"], etape["methode"])].format(x=x)


def _cartes(res, x):
    """Une carte par étape (`second_degre.cartes`), badge de l'étape qui a des lignes (une étape vide rejoint une autre carte), puis
    la carte « Solution »."""
    cartes = []
    for k, c in enumerate(sd.cartes(res), 1):
        etape = next(res["etapes"][i] for i in c["etapes"] if res["etapes"][i]["lignes"])
        cartes.append(so.carte(f"Étape {k}", c["blocs"], badge=titre(etape, x)))
    return cartes + [so.carte("Solution", sd.blocs_solution(res))]


def resoudre(entree):
    try:
        gauche, droite, x, dec = analyser(entree)
    except ErreurSaisie as e:
        return so.sortie_erreur(str(e))
    res = sd.resoudre_equation(gauche, droite, x, dec)
    if res["statut"] != "resolu":
        return so.sortie_erreur(res["message"])
    enonce = tex_element(sd.ecrire_enonce(gauche, droite, x))
    if "formule" not in res["variantes"]:
        return so.sortie_ok(enonce, _cartes(res, x))
    formule = sd.resoudre_equation(gauche, droite, x, dec, sd.ORDRE_PAR_LA_FORMULE)
    if formule["statut"] != "resolu":                                   # jamais une variante qui ne conclut pas : le chemin du cours seul
        return so.sortie_ok(enonce, _cartes(res, x))
    return so.sortie_ok_variantes(enonce, [so.variante("cours", LIBELLES["cours"], _cartes(res, x)),
                                           so.variante("formule", LIBELLES["formule"], _cartes(formule, x))], VARIANTE_DEFAUT)


def resoudre_json(entree):
    return json_strict(resoudre(entree))


def apercu_json(texte):
    """L'aperçu syntaxique : la saisie lue (lexique de l'outil), écrite comme l'énoncé quand l'analyse l'accepte ; une expression sans
    « = » (x+1) est montrée telle quelle (le message « pas de = » vient au calcul) ; seule une erreur de lecture est un message."""
    try:
        gauche, droite = lire_membres(texte, LEXIQUE_EQ)
    except ErreurSaisie as e:
        return json_strict({"ok": False, "erreur": str(e)})
    if droite is None:
        return json_strict({"ok": True, "tex": tex(gauche)})
    try:
        g, d, x, _ = analyser(texte)
        return json_strict({"ok": True, "tex": tex_element(sd.ecrire_enonce(g, d, x))})
    except ErreurSaisie:
        return json_strict({"ok": True, "tex": tex_element(Eq(gauche, droite))})
