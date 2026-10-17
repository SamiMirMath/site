"""
resoudre_fa.py — Adaptateur « format de sortie commun » (moteur/sortie.py) de la factorisation.

Reproduit les cartes que la page affiche aujourd'hui à partir de `factoriser_expr` : une carte
finale (titre « Factorisation », badge = méthode), l'expression, les étapes, le résultat.
"""
from noyau import json_strict
import sortie as so
from factorisation import factoriser_expr, apercu_json

__all__ = ["resoudre", "resoudre_json", "apercu_json"]


def resoudre(entree):
    r = factoriser_expr(entree)
    if not r["ok"]:
        return so.sortie_erreur(r["erreur"], r.get("detail"))
    blocs = [so.formule(r["expr_tex"])]
    blocs += [so.texte(e["html"], style="etape") for e in r["etapes"]]
    blocs.append(so.resultat(r["expr_tex"] + " = " + r["resultat_tex"]))
    return so.sortie_ok(r["expr_tex"], [so.carte("Factorisation", blocs, style="final", badge=r["methode"])])


def resoudre_json(entree):
    return json_strict(resoudre(entree))
