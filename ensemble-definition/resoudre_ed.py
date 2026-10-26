"""
resoudre_ed.py — Adaptateur « format de sortie commun » (moteur/sortie.py) de l'Ensemble de définition.

Reproduit les cartes que la page affiche aujourd'hui à partir de `analyser` : l'en-tête (hors
compteur d'étapes), une carte par condition, la carte finale. Les textes que la page composait
en JS (nombre de conditions, « Condition non résolue », valeurs ≈) sont écrits ici.
Le contrôle numérique (`controle`, qui compose sa phrase) reste un appel séparé, lancé après l'affichage.
"""
from ensemble_def import analyser, apercu_json, json_strict, verifier
from ensemble_def import analyser_json, verifier_json   # noqa: F401  encore appelés par d'anciennes pages restées en cache
import sortie as so

__all__ = ["resoudre", "resoudre_json", "controle", "controle_json", "apercu_json", "analyser_json", "verifier_json"]


def _enonce(r):
    return "f(x) = " + (r["f_saisie_tex"] + " = " if r.get("f_saisie_tex") else "") + r["f_tex"]


def _entete(r):
    n = len(r["conditions"])
    if n:
        phrase = f"{n} condition{'s' if n > 1 else ''} d'existence : " + ", ".join(c["titre"] for c in r["conditions"]) + "."
    else:
        phrase = "Ni logarithme, ni dénominateur, ni racine : aucune condition."
    return so.carte("Fonction", [so.formule(_enonce(r)), so.texte(phrase, style="discret")], titre_masque=True)


def _carte_condition(c):
    # le titre ne porte pas l'inégalité quand la première ligne l'écrit déjà (« condition ⇔ solution »)
    ecrite = any(it["type"] == "texte" and it["html"].startswith("\\(" + c["cond_tex"]) for it in c["etapes"])
    blocs = [] if ecrite else [so.formule(c["cond_tex"])]
    for it in c["etapes"]:
        if it["type"] == "tableau":
            blocs.append(dict(it))
        else:
            blocs.append(so.texte(it["html"], style="etape"))
    if not c["resolu"]:
        blocs.append(so.erreur("Condition non résolue."))
    return so.carte(f"Condition {c['num']}", blocs, badge=c["titre"], detail=c.get("detail"))


def _carte_finale(r):
    if not r["complet"]:
        return so.carte("Ensemble de définition", [so.erreur("Une condition n'a pas pu être résolue : l'ED n'est pas calculé.")], style="final", titre_masque=True)
    if not r["conditions"]:
        return so.carte("Ensemble de définition", [so.resultat("ED = \\mathbb{R}")], style="final", titre_masque=True)
    blocs = [so.resultat("ED = " + (r["inter_tex"] + " = " if r.get("inter_tex") else "") + r["ED_tex"])]
    if "approx" in r["ED_tex"]:
        blocs.append(so.texte("Les valeurs précédées de ≈ ont été obtenues numériquement.", style="indice"))
    return so.carte("Ensemble de définition", blocs, style="final", titre_masque=True)


def resoudre(entree):
    r = analyser(entree)
    if not r["ok"]:
        return so.sortie_erreur(r["erreur"], r.get("detail"))
    cartes = [_carte_condition(c) for c in r["conditions"]] + [_carte_finale(r)]
    return so.sortie_ok(_enonce(r), cartes, entete=_entete(r), besoin_sympy=r["besoin_sympy"])


def resoudre_json(entree):
    return json_strict(resoudre(entree))


def controle(entree):
    """Contrôle numérique indépendant, avec la phrase affichée sous la dernière carte :
    {ok, accord, texte} (ok faux : rien à afficher, l'ED n'est pas calculé)."""
    v = verifier(entree)
    if not v["ok"]:
        return {"ok": False, "accord": False, "texte": v["msg"]}
    if v["accord"]:
        texte = (f"✓ Contrôle numérique indépendant : f est bien définie aux {v['n_in']} points testés dans l'ED "
                 f"et non définie aux {v['n_out']} points testés hors de l'ED.")
    else:
        texte = ("⚠ Le contrôle numérique signale un désaccord près de x ≈ " + " ; ".join(str(x) for x in v["erreurs"])
                 + ". Vérifiez ce résultat à la main.")
    return {"ok": True, "accord": v["accord"], "texte": texte}


def controle_json(entree):
    return json_strict(controle(entree))
