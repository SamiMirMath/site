"""
resoudre_fa.py — Adaptateur « format de sortie commun » (moteur/sortie.py) de la factorisation.

T21 : une carte par application de méthode (« Étape k », badge = la méthode), dans l'ordre où le moteur les rédige ; des applications
consécutives de la même méthode sont dans la même carte. La dernière carte (« Factorisation », badge = toutes les méthodes) donne
l'expression et le résultat. Une étape sans méthode propre (« ne se factorise pas davantage ») suit la carte de la méthode précédente.
"""
from noyau import json_strict
import sortie as so
from factorisation import _factoriser, apercu_json, exercice_json

__all__ = ["resoudre", "resoudre_json", "apercu_json", "exercice_json"]


def groupes_consecutifs(etapes, methodes):
    """[(méthode, [html])] : suites consécutives de même méthode ; `methodes[i]` est la méthode de `etapes[i]` (None : pas de méthode
    propre, l'étape suit le groupe précédent, ou précède le premier). Renvoie aussi les étapes sans groupe (aucune méthode du tout)."""
    groupes, libres = [], []
    for e, m in zip(etapes, methodes):
        if m is None:
            (groupes[-1][1] if groupes else libres).append(e["html"])
        elif groupes and groupes[-1][0] == m:
            groupes[-1][1].append(e["html"])
        else:
            groupes.append((m, libres + [e["html"]]))
            libres = []
    return groupes, libres


def resoudre(entree):
    r, ctx = _factoriser(entree)
    if not r["ok"]:
        return so.sortie_erreur(r["erreur"], r.get("detail"))
    groupes, libres = groupes_consecutifs(r["etapes"], ctx.groupes)
    cartes = [so.carte(f"Étape {k}", [so.texte(h, style="etape") for h in htmls], badge=m)
              for k, (m, htmls) in enumerate(groupes, 1)]
    blocs = [so.formule(r["expr_tex"])] + [so.texte(h, style="etape") for h in libres]
    blocs.append(so.resultat(r["expr_tex"] + " = " + r["resultat_tex"]))
    cartes.append(so.carte("Factorisation", blocs, style="final", badge=r["methode"]))
    return so.sortie_ok(r["expr_tex"], cartes)


def resoudre_json(entree):
    return json_strict(resoudre(entree))
