"""
resoudre_el.py — Adaptateur « format de sortie commun » (moteur/sortie.py) de l'outil Exponentielles et logarithmes.

Une carte par application de méthode (« Étape k », badge = la méthode), dans l'ordre où le moteur les rédige, puis la carte finale
« Solution » (équation : S = {…}, soit x ≈ …) ou « Résultat » (calcul de log_a(y)). Quand aucune méthode ne s'applique, une erreur au
message prévu (EL-11) : jamais une étape fausse ni une valeur donnée comme solution. Tout le TeX vient de l'arbre de exp_log.py.
"""
from html import escape

from noyau import ErreurSaisie, json_strict
import sortie as so
import exp_log as el
from exp_log import apercu_json

__all__ = ["resoudre", "resoudre_json", "apercu_json"]


def _ligne(chaine):
    """Une ligne du corrigé : sa chaîne de « ⇔ » ou de « = » en TeX, dans une carte d'étapes (comme la Factorisation)."""
    return so.texte(r"\(" + escape(el.tex_chaine(chaine), quote=False) + r"\)", style="etape")


def _cartes(r):
    cartes = []
    for k, c in enumerate(r["etapes"], 1):
        blocs = [_ligne(ligne) for ligne in c["lignes"]]
        if r["remarque"] and k == len(r["etapes"]):
            blocs.append(so.texte(escape(r["remarque"], quote=False), style="etape"))
        cartes.append(so.carte(f"Étape {k}", blocs, badge=c["titre"]))
    return cartes


def resoudre(entree):
    try:
        s = el.analyser_saisie(entree)
    except ErreurSaisie as e:
        return so.sortie_erreur(str(e))
    if s.genre == "calcul":
        r = el.calculer_logarithme(s.g)
        if r is None:
            return so.sortie_erreur(el.message_calcul_non_resolu(s.g))
        final = so.carte("Résultat", [so.resultat(el.tex_resultat(r))], style="final")
    else:
        r = el.corriger_equation(s.g, s.d, s.inconnue)
        if r is None:
            return so.sortie_erreur(el.message_non_resolu(s.g, s.d, s.inconnue))
        final = so.carte("Solution", [so.resultat(el.tex_solution(r))], style="final")
    return so.sortie_ok(el.tex_saisie(s.g, s.d), _cartes(r) + [final])


def resoudre_json(entree):
    return json_strict(resoudre(entree))
