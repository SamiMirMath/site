"""
resoudre_la.py — Adaptateur « format de sortie commun » (moteur/sortie.py) de Limites et asymptotes.

Construit, à partir de `etudier`, les cartes que la page affiche : rappel, tableaux de
signes, une carte par limite, bilan des asymptotes. La phrase de chaque asymptote, que la page
composait en JS (`ligneAsymptote`), est écrite ici une seule fois ; les fonctions `carte_*` sont
partagées avec l'Étude complète (`resoudre_ec.py`).
"""
import re

from noyau import json_strict, txt
import sortie as so
from limites_asymptotes import etudier, apercu_json, phrase_horizontale

__all__ = ["resoudre", "resoudre_json", "apercu_json"]


def enonce(r):
    return "f(x) = " + (r["f_saisie_tex"] + " = " if r.get("f_saisie_tex") else "") + r["f_tex"]


def carte_rappel(r, suffixe_ed=""):
    return so.carte("Fonction", [so.formule(enonce(r)), so.texte("\\(ED = " + r["ed_tex"] + "\\)" + suffixe_ed, style="discret")],
                    titre_masque=True)


def _blocs(items):
    return [dict(it) if it["type"] == "tableau" else so.texte(it["html"], style="etape", detail=it.get("detail")) for it in items]


def carte_tableaux(items):
    return so.carte("Tableaux de signes", _blocs(items), badge="tableau")


def carte_etude(et):
    return so.carte("Limite", _blocs(et["etapes"]), badge="limite", titre_tex=et["ou"])


def cartes_etude(et):
    """Cartes d'une borne : une seule carte « Limite » (ancienne rédaction) ou, pour une rédaction descendante, l'énoncé puis
    une carte « Étape n : titre. » par étape ; les lignes qui suivent (asymptote…) rejoignent la dernière carte."""
    items = et["etapes"]
    if not any(it.get("type") == "descente" for it in items):
        return [carte_etude(et)]
    cartes, reste = [], []

    def vider():
        if reste:
            cartes.append(so.carte("Limite", _blocs(reste), badge="limite", titre_tex=et["ou"]))
            reste.clear()

    for it in items:
        if it.get("type") == "descente":
            vider()
            cartes.append(so.carte("Limite", [so.texte("\\[" + it["enonce_tex"] + "\\]", style="etape")], badge="limite", titre_tex=et["ou"]))
            for i, e in enumerate(it["etapes"], 1):
                cartes.append(so.carte(f"Étape {i} : {e['titre']}.", e["blocs"]))
        elif cartes and cartes[-1]["titre"].startswith("Étape"):
            cartes[-1]["blocs"] += _blocs([it])
        else:
            reste.append(it)
    vider()
    return cartes


_VERS_INFINI = re.compile(r"(x\s*\\to\s*)[+-]\\infty")


def _neutre(v):
    """Le même contenu, le point « x → −∞ » / « x → +∞ » écrit « x → ±∞ » (pour comparer, puis écrire, les deux bornes infinies)."""
    if isinstance(v, str):
        return _VERS_INFINI.sub(r"\1\\pm\\infty", v)
    if isinstance(v, dict):
        return {k: _neutre(x) for k, x in v.items()}
    if isinstance(v, list):
        return [_neutre(x) for x in v]
    return v


def _sans_conclusion(et):
    return [it for it in et["etapes"] if "conclusion" not in it]


def _conclusions(et):
    return [it["conclusion"] for it in et["etapes"] if "conclusion" in it]


def etudes_affichees(etudes):
    """Études dans l'ordre d'affichage (celui d'`etudier` : −∞, valeurs interdites, +∞, EC D16), x → −∞ et x → +∞ en une seule étude
    « x → ±∞ » quand leurs étapes sont identiques au symbole près (le point de la limite) et leurs conclusions identiques au côté près ;
    la conclusion devient alors celle « des deux côtés ». Sinon, les études telles quelles."""
    ou = {e["ou"]: i for i, e in enumerate(etudes)}
    i, j = ou.get(r"x \to -\infty"), ou.get(r"x \to +\infty")
    if i is None or j is None:
        return list(etudes)
    g, d = etudes[i], etudes[j]
    corps = _neutre(_sans_conclusion(g))
    cg, cd = _conclusions(g), _conclusions(d)
    if corps != _neutre(_sans_conclusion(d)) or cg != cd or len(cg) > 1:
        return list(etudes)
    etapes = corps
    if cg:
        c = cg[0]
        etapes = etapes + [txt(phrase_horizontale(c["valeur_tex"], 0, c["signee"], c["position"]))]
    groupe = {"ou": r"x \to \pm\infty", "etapes": etapes}
    return [groupe if k == i else e for k, e in enumerate(etudes) if k != j]


def cartes_limites(etudes):
    """Cartes de toutes les bornes, dans l'ordre d'affichage (partagé par l'outil Limites et l'Étude complète)."""
    return [c for et in etudes_affichees(etudes) for c in cartes_etude(et)]


def ligne_asymptote(a):
    m = lambda t: "\\(" + t + "\\)"
    g = a["genre"]
    if g == "horizontale":
        position = f", graphe {a['position']}" if a.get("position") else ""
        return f"Asymptote horizontale ({m(a['ou'])}) : {m('y = ' + a['valeur_tex'])}{position}"
    if g == "oblique":
        return f"Asymptote oblique ({m(a['ou'])}) : {m('y = ' + a['equation_tex'])}"
    if g == "verticale":
        p = a["point_tex"]
        bouts = []
        if a.get("gauche_tex"):
            bouts.append(m("\\lim_{x\\to " + p + "^-} f(x) = " + a["gauche_tex"]))
        if a.get("droite_tex"):
            bouts.append(m("\\lim_{x\\to " + p + "^+} f(x) = " + a["droite_tex"]))
        return f"Asymptote verticale : {m('x = ' + p)} ({' ; '.join(bouts)})"
    if g == "trou" and a.get("bord"):
        p, v = a["point_tex"], a["valeur_tex"]
        return (f"Bord du graphe : f n'est pas définie en {m('x = ' + p)}, mais {m('f(x) \\to ' + v)} ; le graphe s'arrête au point "
                f"{m('(' + p + '\\,;\\,' + v + ')')}, qui n'en fait pas partie (pas une asymptote verticale)")
    if g == "trou":
        p, v = a["point_tex"], a["valeur_tex"]
        return (f"Trou en {m('(' + p + '\\,;\\,' + v + ')')} : f n'est pas définie en {m('x = ' + p)}, "
                f"mais {m('f(x) \\to ' + v)} (pas une asymptote verticale)")
    if g == "sans_limite":
        p = a["point_tex"]
        return (f"Pas de limite en {m('x = ' + p)} (pas d'asymptote verticale) : "
                f"{m('\\lim_{x\\to ' + p + '^-} f(x) = ' + a['gauche_tex'])} ; {m('\\lim_{x\\to ' + p + '^+} f(x) = ' + a['droite_tex'])}")
    return f"Pas d'asymptote ({m(a['ou'])}) — branche parabolique."


def carte_bilan(asymptotes, style="final"):
    if asymptotes:
        blocs = [so.liste([ligne_asymptote(a) for a in asymptotes], style="bilan")]
    else:
        blocs = [so.texte("Aucune asymptote détectée.", style="discret")]
    return so.carte("Bilan des asymptotes", blocs, style=style)


def resoudre(entree):
    r = etudier(entree)
    if not r["ok"]:
        return so.sortie_erreur(r["erreur"], r.get("detail"))
    cartes = [carte_rappel(r, " — détail dans l'outil « Ensemble de définition ».")]
    if r.get("tableaux_signe"):
        cartes.append(carte_tableaux(r["tableaux_signe"]))
    cartes += cartes_limites(r["etudes"])
    cartes.append(carte_bilan(r["asymptotes"]))
    return so.sortie_ok(enonce(r), cartes)


def resoudre_json(entree):
    return json_strict(resoudre(entree))
