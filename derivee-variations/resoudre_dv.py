"""
resoudre_dv.py — Adaptateur « format de sortie commun » (moteur/sortie.py) de la Dérivée.

Reproduit les cartes que la page affiche aujourd'hui à partir de `etudier` : rappel, dérivée,
signe de f' et variations. Les fonctions `carte_*` sont partagées avec l'Étude complète
(`resoudre_ec.py`), qui affiche les mêmes cartes avec ses propres phrases (`ec=True`) et les
limites dans le tableau.
"""
from noyau import json_strict
import sortie as so
from derivee_variations import etudier, apercu_json

__all__ = ["resoudre", "resoudre_json", "apercu_json"]

TITRE_SIGNE = "Signe de f' et variations"


def enonce(r):
    return "f(x) = " + (r["f_saisie_tex"] + " = " if r.get("f_saisie_tex") else "") + r["f_tex"]


def carte_rappel(r, suffixe_ed=""):
    return so.carte("Fonction", [so.formule(enonce(r)), so.texte("\\(ED = " + r["ed_tex"] + "\\)" + suffixe_ed, style="discret")],
                    titre_masque=True)


def carte_derivee(r):
    if not r["deriv_resolu"]:
        return so.carte("Dérivée", [so.erreur(r["deriv_erreur"])], style="erreur", detail=r.get("deriv_detail"))
    blocs = [so.texte(e["html"], style="etape") for e in r["deriv_etapes"]]
    blocs.append(so.resultat("f'(x) = " + r["deriv_tex"]))
    return so.carte("Dérivée", blocs, badge="calcul")


def carte_signe(r, limites=None, ec=False):
    if not r["signe_resolu"]:
        return so.carte(TITRE_SIGNE, [so.erreur(r["signe_erreur"])], style="erreur", detail=r.get("signe_detail"))
    blocs = [dict(e) if e["type"] == "tableau" else so.texte(e["html"], style="etape") for e in r["signe_etapes"]]
    tab = dict(r["table_signe"], type="tableau")
    if limites:
        tab["limites"] = limites
    blocs.append(tab)
    for o in (limites or {}).get("non_determinees", []):
        blocs.append(so.texte(f"Limite non déterminée automatiquement en \\({o}\\).", style="indice"))
    if r["extrema"]:
        blocs.append(so.liste([f"{e['genre']} en \\(x={e['x_tex']}\\) : \\(f({e['x_tex']})={e['f_tex']}\\)" for e in r["extrema"]],
                              style="extrema"))
    elif r.get("f_constante"):
        blocs.append(so.texte("f est constante sur chaque intervalle de son ensemble de définition : aucun extremum." if ec else
                              "f' est nulle sur son ensemble de définition : f est constante sur chaque intervalle, aucun extremum.",
                              style="indice"))
    else:
        blocs.append(so.texte("Aucun extremum local." if ec else
                              "Aucun extremum local : f est strictement monotone (ou n'a que des points où f' s'annule sans changer de signe).",
                              style="indice"))
    return so.carte(TITRE_SIGNE, blocs, badge="tableau")


def resoudre(entree):
    r = etudier(entree)
    if not r["ok"]:
        return so.sortie_erreur(r["erreur"], r.get("detail"))
    cartes = [carte_rappel(r, " — détail dans l'outil « Ensemble de définition ».")]
    cartes.append(carte_derivee(r))
    if r["deriv_resolu"]:
        cartes.append(carte_signe(r))
    return so.sortie_ok(enonce(r), cartes)


def resoudre_json(entree):
    return json_strict(resoudre(entree))
