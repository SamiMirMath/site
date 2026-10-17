"""
sortie.py — Format de sortie commun des outils (D2) : constructeurs et validateur.

Python pur, bibliothèque standard seulement. Une sortie de `resoudre()` est un dict :

    {ok, erreur, detail?, enonce_tex, entete?, cartes: [carte], besoin_sympy?}
    carte = {titre, titre_tex?, badge?, style, blocs: [bloc]}
    bloc  = texte | formule | resultat | erreur | liste | tableau | graphique

`valider(sortie)` renvoie la liste des écarts au schéma (vide si la sortie est conforme).
"""

STYLES_CARTE = ("normal", "etape", "final", "erreur")
STYLES_TEXTE = ("etape", "discret", "indice")
STYLES_LISTE = ("extrema", "bilan")
CASES = ("+", "-", "0", "|", "||", "x", "asym", "extremum", "",
         "\\nearrow", "\\searrow", "\\rightarrow")

# type de bloc → (clés obligatoires, clés facultatives)
BLOCS = {
    "texte": ({"html"}, {"style", "detail"}),
    "formule": ({"tex"}, set()),
    "resultat": ({"tex"}, set()),
    "erreur": ({"texte"}, set()),
    "liste": ({"items"}, {"style"}),
    "tableau": ({"var", "crit", "rows"}, {"limites"}),
    "graphique": ({"xmin", "xmax", "ymin", "ymax", "segments", "extrema", "asymptotes"}, {"recalculable"}),
}
CARTE = ({"titre", "style", "blocs"}, {"titre_tex", "badge"})
LIGNE = ({"label", "cells"}, {"final", "variation"})
SORTIE_OK = ({"ok", "erreur", "enonce_tex", "cartes"}, {"entete", "besoin_sympy", "detail"})
SORTIE_KO = ({"ok", "erreur"}, {"detail"})


# ---------- constructeurs ----------
def texte(html, style=None, detail=None):
    b = {"type": "texte", "html": html}
    if style:
        b["style"] = style
    if detail:
        b["detail"] = detail
    return b


def formule(tex):
    return {"type": "formule", "tex": tex}


def resultat(tex):
    return {"type": "resultat", "tex": tex}


def erreur(texte_):
    return {"type": "erreur", "texte": texte_}


def liste(items, style=None):
    b = {"type": "liste", "items": list(items)}
    if style:
        b["style"] = style
    return b


def carte(titre, blocs, style="normal", badge=None, titre_tex=None):
    c = {"titre": titre, "style": style, "blocs": list(blocs)}
    if badge:
        c["badge"] = badge
    if titre_tex:
        c["titre_tex"] = titre_tex
    return c


def sortie_ok(enonce_tex, cartes, entete=None, besoin_sympy=None):
    s = {"ok": True, "erreur": None, "enonce_tex": enonce_tex, "cartes": list(cartes)}
    if entete is not None:
        s["entete"] = entete
    if besoin_sympy is not None:
        s["besoin_sympy"] = besoin_sympy
    return s


def sortie_erreur(message, detail=None):
    s = {"ok": False, "erreur": message}
    if detail:
        s["detail"] = detail
    return s


# ---------- validateur ----------
def _cles(d, obligatoires, facultatives, chemin, ecarts):
    if not isinstance(d, dict):
        ecarts.append(f"{chemin} : dict attendu")
        return False
    for k in obligatoires - set(d):
        ecarts.append(f"{chemin} : clé « {k} » manquante")
    for k in set(d) - obligatoires - facultatives:
        ecarts.append(f"{chemin} : clé « {k} » inconnue")
    return True


def _texte_non_vide(v):
    return isinstance(v, str) and v != ""


def _valider_tableau(b, chemin, ecarts):
    if not isinstance(b.get("crit"), list) or not isinstance(b.get("rows"), list):
        ecarts.append(f"{chemin} : crit et rows doivent être des listes")
        return
    n = 2 * len(b["crit"]) + 1
    for i, r in enumerate(b["rows"]):
        cp = f"{chemin}.rows[{i}]"
        if not _cles(r, *LIGNE, cp, ecarts):
            continue
        cells = r.get("cells")
        if not isinstance(cells, list):
            ecarts.append(f"{cp} : cells doit être une liste")
            continue
        if len(cells) != n:
            ecarts.append(f"{cp} : {len(cells)} cases, {n} attendues")
        for j, c in enumerate(cells):
            if not isinstance(c, str) or not (c in CASES or c.startswith("val:")):
                ecarts.append(f"{cp}.cells[{j}] : case « {c} » hors vocabulaire")
    lim = b.get("limites")
    if lim is not None:
        _cles(lim, {"colonnes", "moins_inf", "plus_inf", "non_determinees"}, set(), chemin + ".limites", ecarts)


def _valider_bloc(b, chemin, ecarts):
    if not isinstance(b, dict) or b.get("type") not in BLOCS:
        ecarts.append(f"{chemin} : type de bloc inconnu ({b.get('type') if isinstance(b, dict) else b!r})")
        return
    obl, fac = BLOCS[b["type"]]
    avant = len(ecarts)
    if not _cles({k: v for k, v in b.items() if k != "type"}, obl, fac, chemin, ecarts) or len(ecarts) > avant:
        return
    t = b["type"]
    if t == "texte":
        if not _texte_non_vide(b["html"]):
            ecarts.append(f"{chemin} : html vide")
        if "style" in b and b["style"] not in STYLES_TEXTE:
            ecarts.append(f"{chemin} : style « {b['style']} » inconnu")
    elif t in ("formule", "resultat"):
        if not _texte_non_vide(b["tex"]):
            ecarts.append(f"{chemin} : tex vide")
    elif t == "erreur":
        if not _texte_non_vide(b["texte"]):
            ecarts.append(f"{chemin} : texte vide")
    elif t == "liste":
        if not isinstance(b["items"], list) or not all(_texte_non_vide(x) for x in b["items"]):
            ecarts.append(f"{chemin} : items doit être une liste de textes non vides")
        if "style" in b and b["style"] not in STYLES_LISTE:
            ecarts.append(f"{chemin} : style « {b['style']} » inconnu")
    elif t == "tableau":
        _valider_tableau(b, chemin, ecarts)


def valider(s):
    ecarts = []
    if not isinstance(s, dict) or "ok" not in s:
        return ["sortie : dict avec « ok » attendu"]
    if s["ok"] is not True and s["ok"] is not False:
        return ["sortie : ok doit être un booléen"]
    if not s["ok"]:
        _cles(s, *SORTIE_KO, "sortie", ecarts)
        if not _texte_non_vide(s.get("erreur")):
            ecarts.append("sortie : erreur (texte français) obligatoire quand ok est faux")
        elif "Traceback" in s["erreur"]:
            ecarts.append("sortie : erreur contient une trace Python")
        return ecarts
    _cles(s, *SORTIE_OK, "sortie", ecarts)
    if s.get("erreur") is not None:
        ecarts.append("sortie : erreur doit être null quand ok est vrai")
    if not _texte_non_vide(s.get("enonce_tex")):
        ecarts.append("sortie : enonce_tex vide")
    if "entete" in s:
        _valider_carte(s["entete"], "entete", ecarts)
    if not isinstance(s.get("cartes"), list):
        ecarts.append("sortie : cartes doit être une liste")
        return ecarts
    for i, c in enumerate(s["cartes"]):
        _valider_carte(c, f"cartes[{i}]", ecarts)
    return ecarts


def _valider_carte(c, chemin, ecarts):
    if not _cles(c, *CARTE, chemin, ecarts):
        return
    if c.get("style") not in STYLES_CARTE:
        ecarts.append(f"{chemin} : style « {c.get('style')} » inconnu")
    if not isinstance(c.get("blocs"), list):
        ecarts.append(f"{chemin} : blocs doit être une liste")
        return
    for j, b in enumerate(c["blocs"]):
        _valider_bloc(b, f"{chemin}.blocs[{j}]", ecarts)
