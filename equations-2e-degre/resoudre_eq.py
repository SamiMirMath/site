"""
resoudre_eq.py — Adaptateur « format de sortie commun » (moteur/sortie.py) de l'outil Équations du 2e degré (chantier
equations-2e-degre, P5 ; decisions.md, § 5 et § 13).

La saisie est lue par equations.analyser (messages du § 4 et du § 13.5), puis résolue par second_degre.resoudre_equation. La page est
construite uniquement à partir des étapes (§ 5) : une carte « Résolution » avec les blocs de `second_degre.blocs` (la chaîne du
corrigé, concaténation des lignes de toutes les étapes ; S encadré, D29 ; la ligne ≈, E14). Quand le chemin du cours n'utilise pas la
formule, une seconde résolution « Par la formule » (E12) est proposée par le sélecteur de méthode de la page (`sortie_ok_variantes`,
« Méthodes du cours » par défaut). Une équation non résolue (bicarrée, hors du cours, forme non traitée par l'outil, bornes, garde-fou
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

__all__ = ["resoudre", "resoudre_json", "apercu_json", "LIBELLES", "VARIANTE_DEFAUT"]

VARIANTE_DEFAUT = "cours"
LIBELLES = {"cours": "Méthodes du cours", "formule": "Par la formule"}         # D2, E12


def _cartes(res):
    return [so.carte("Résolution", sd.blocs(res))]


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
        return so.sortie_ok(enonce, _cartes(res))
    formule = sd.resoudre_equation(gauche, droite, x, dec, sd.ORDRE_PAR_LA_FORMULE)
    if formule["statut"] != "resolu":                                   # jamais une variante qui ne conclut pas : le chemin du cours seul
        return so.sortie_ok(enonce, _cartes(res))
    return so.sortie_ok_variantes(enonce, [so.variante("cours", LIBELLES["cours"], _cartes(res)),
                                           so.variante("formule", LIBELLES["formule"], _cartes(formule))], VARIANTE_DEFAUT)


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
