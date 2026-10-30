"""
resoudre_ec.py — Adaptateur « format de sortie commun » (moteur/sortie.py) de l'Étude complète.

Assemble les cartes de `resoudre_dv` (dérivée, signe et variations, avec les limites dans le
tableau) et de `resoudre_la` (tableaux de signes, limites, bilan), puis la carte du graphique,
dans l'ordre où la page les affiche aujourd'hui. La recalculation du graphique au zoom reste
l'appel séparé `fenetre_json`.

`etudier_json` (ancienne page, avant T19) est réexportée : une page restée en cache qui lit le nouveau
manifeste continue de fonctionner. À retirer à la clôture, après quelques jours en ligne.
"""
from noyau import json_strict
import sortie as so
import resoudre_dv as rdv
import resoudre_la as rla
from etude_complete import etudier, etudier_json, apercu_json, fenetre_json

__all__ = ["resoudre", "resoudre_json", "apercu_json", "fenetre_json", "etudier_json"]

AIDE_GRAPHIQUE = ("Courbe (trait plein), asymptotes (pointillé), extrema (points pleins), trou (rond vide). "
                  "Molette ou boutons pour zoomer, cliquer-glisser pour déplacer.")


def carte_graphique(r):
    g = r["graphique"]
    bloc = {"type": "graphique", "xmin": g["xmin"], "xmax": g["xmax"], "ymin": g["ymin"], "ymax": g["ymax"],
            "segments": g["segments"], "extrema": r["derivee"].get("extrema") or [],
            "asymptotes": r["limites"].get("asymptotes") or [], "recalculable": True}
    return so.carte("Graphique", [bloc, so.texte(AIDE_GRAPHIQUE, style="indice")])


def resoudre(entree):
    r = etudier(entree)
    if not r["ok"]:
        return so.sortie_erreur(r["erreur"], r.get("detail"))
    dv, lim = r["derivee"], r["limites"]
    cartes = [rdv.carte_rappel(r)]
    if dv["deriv_resolu"]:
        cartes.append(rdv.carte_derivee(dv))
        if dv["signe_resolu"]:
            cartes.append(rdv.carte_signe(dv, r["variations_limites"], ec=True))
    if lim.get("tableaux_signe"):
        cartes.append(rla.carte_tableaux(lim["tableaux_signe"]))
    for et in lim["etudes"]:
        cartes += rla.cartes_etude(et)
    cartes.append(rla.carte_bilan(lim["asymptotes"], style="normal"))
    cartes.append(carte_graphique(r))
    return so.sortie_ok(rdv.enonce(r), cartes)


def resoudre_json(entree):
    return json_strict(resoudre(entree))
