"""
resoudre_ec.py — Adaptateur « format de sortie commun » (moteur/sortie.py) de l'Étude complète.

Six parties titrées, dans l'ordre du corrigé (decisions.md D1), chacune ouverte par un intertitre (`so.partie`) :
1. Domaine de définition (`parties.cartes_domaine` : fonction, mise en forme, une carte par condition, ED encadré, D3) ;
2. Parité (`parties.cartes_parite`, D4) ; 3. Zéros, signe, ordonnée à l'origine (`parties.cartes_zeros_signe`, D5 : zéros en chaîne,
tableau de signes de f, f(0)) ; 4. Limites et asymptotes (cartes de `resoudre_la` : tableaux de signes, limites, bilan) ;
5. Dérivée, tableau de variation, extremums (cartes de `resoudre_dv`, avec les limites dans le tableau et les valeurs des extremums,
D10 ; extremums rédigés par `parties.partie5`, D11 : valeur en chaîne, point exact puis ≈, global ou non) ; 6. Graphe : carte « Bilan
de l'étude » (D20 : `parties.carte_bilan`, les résultats des parties 1 à 5, une ligne chacun, sans calcul nouveau), puis le graphique
(D15 : courbe, asymptotes, extremums, zéros et (0 ; f(0)) marqués, ronds vides aux points exclus à limite finie, cadrage de
decisions.md §3).
La recalculation du graphique au zoom reste l'appel séparé `fenetre_json`.
"""
from noyau import json_strict
import sortie as so
import resoudre_dv as rdv
import resoudre_la as rla
import parties
from etude_complete import analyse, etude_et_partie3, apercu_json, fenetre_json

__all__ = ["resoudre", "resoudre_json", "apercu_json", "fenetre_json"]

PARTIES = ("1. Domaine de définition", "2. Parité", "3. Zéros, signe, ordonnée à l'origine", "4. Limites et asymptotes",
           "5. Dérivée, tableau de variation, extremums", "6. Graphe")

AIDE_GRAPHIQUE = ("Courbe (trait plein), asymptotes (pointillé), extremums, zéros et point (0 ; f(0)) (points pleins), "
                  "points exclus du graphe (ronds vides). Molette ou boutons pour zoomer, cliquer-glisser pour déplacer.")


def carte_graphique(r):
    g = r["graphique"]
    bloc = {"type": "graphique", "xmin": g["xmin"], "xmax": g["xmax"], "ymin": g["ymin"], "ymax": g["ymax"],
            "segments": g["segments"], "extrema": r["derivee"].get("extrema") or [],
            "asymptotes": r["limites"].get("asymptotes") or [], "points": g["points"], "ronds_vides": g["ronds_vides"],
            "recalculable": True}
    return so.carte("Graphique", [bloc, so.texte(AIDE_GRAPHIQUE, style="indice")])


AUCUNE_ASYMPTOTE = "Aucune asymptote détectée"                         # phrase du bilan des asymptotes (outil Limites), sans le point


def lignes_extremums(dv, p5, carte_signe):
    """Lignes du bilan (D20) pour la partie 5 : celles de `parties.partie5` (nature et point, sans la justification) ; sans rédaction
    D11 (repli), les lignes de la liste de l'outil Dérivée, telles que la carte les affiche ; aucun extremum : la phrase de la carte."""
    if dv["extrema"]:
        if p5 is not None:
            return p5["bilan"]
        return [i for b in carte_signe["blocs"] if b["type"] == "liste" and b.get("style") == "extrema" for i in b["items"]]
    return ["Aucun extremum" if dv.get("f_constante") else "Aucun extremum local"]


def resoudre(entree):
    r, p3 = etude_et_partie3(entree)                                       # partie 3 calculée une fois, avec le graphique (D15)
    if not r["ok"]:
        return so.sortie_erreur(r["erreur"], r.get("detail"))
    dv, lim = r["derivee"], r["limites"]
    domaine = parties.cartes_domaine(rdv.enonce(r), analyse(entree))    # analyse en cache : celle d'etudier (D19)
    p2 = parties.partie2(analyse(entree))
    parite = p2["cartes"]
    zeros = p3["cartes"]
    limites = [rla.carte_tableaux(lim["tableaux_signe"])] if lim.get("tableaux_signe") else []
    limites += rla.cartes_limites(lim["etudes"])                        # ordre et regroupement de x → ±∞ de l'outil Limites (D16)
    limites.append(rla.carte_bilan(lim["asymptotes"], style="normal"))
    # carte « Dérivée » toujours (hors du cadre : la phrase de l'outil Dérivée, Q7) ; signe non étudié : la carte d'erreur de l'outil
    # Dérivée (un résultat non traité donne un message clair) : jamais d'intertitre seul
    derivee = [rdv.carte_derivee(dv)]
    bilan_extremums = None                                              # partie 5 non conclue : pas de ligne au bilan
    if dv["deriv_resolu"]:
        p5 = None
        if dv["signe_resolu"]:
            p5 = parties.partie5(dv, r["variations_limites"], analyse(entree))     # D11 (EC seule)
        signe = rdv.carte_signe(dv, r.get("variations_limites"), ec=True, extremums=p5 and p5["blocs"])
        derivee.append(signe)
        if dv["signe_resolu"]:
            bilan_extremums = lignes_extremums(dv, p5, signe)
    asymptotes = [rla.ligne_asymptote(a) for a in lim["asymptotes"]] or [AUCUNE_ASYMPTOTE]     # celles du bilan de la partie 4
    bilan = parties.carte_bilan(r["ed_tex"], p2["conclusion"], p3, asymptotes, bilan_extremums)          # D20
    cartes = []
    for titre, contenu in zip(PARTIES, (domaine, parite, zeros, limites, derivee, [bilan, carte_graphique(r)])):
        cartes += [so.partie(titre)] + contenu
    return so.sortie_ok(rdv.enonce(r), cartes)


def resoudre_json(entree):
    return json_strict(resoudre(entree))
