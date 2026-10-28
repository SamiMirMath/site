"""
sortie.py — Format de sortie commun des outils (D2) : constructeurs et validateur.

Python pur, bibliothèque standard seulement. Une sortie de `resoudre()` est un dict :

    {ok, erreur, detail?, enonce_tex, entete?, cartes: [carte], besoin_sympy?, variantes?, variante_defaut?, option?}
    carte = {titre, titre_tex?, titre_masque?, badge?, style, blocs: [bloc]}
    bloc  = texte | formule | resultat | erreur | liste | tableau | graphique
    variante = {cle, libelle, cartes: [carte], option?: false}   (facultatif : plusieurs résolutions de la même entrée, au choix de l'élève ;
               `cartes` de la sortie est alors celles de la variante par défaut ; `option: false` : pas de case à cocher pour cette variante)
    option = {cle, libelle, cochee, cartes: [carte]}   (facultatif : une case à cocher dont les cartes s'ajoutent à la fin des cartes affichées ;
               `cochee` est son état au départ)

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
CARTE = ({"titre", "style", "blocs"}, {"titre_tex", "badge", "detail", "titre_masque"})
LIGNE = ({"label", "cells"}, {"final", "variation"})
SORTIE_OK = ({"ok", "erreur", "enonce_tex", "cartes"}, {"entete", "besoin_sympy", "detail", "variantes", "variante_defaut", "option"})
VARIANTE = ({"cle", "libelle", "cartes"}, {"option"})
OPTION = ({"cle", "libelle", "cochee", "cartes"}, set())
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


def carte(titre, blocs, style="normal", badge=None, titre_tex=None, detail=None, titre_masque=False):
    c = {"titre": titre, "style": style, "blocs": list(blocs)}
    if titre_masque:
        c["titre_masque"] = True      # le titre reste dans les données mais la page ne l'affiche pas
    if detail:
        c["detail"] = detail
    if badge:
        c["badge"] = badge
    if titre_tex:
        c["titre_tex"] = titre_tex
    return c


def variante(cle, libelle, cartes, option=True):
    """Une résolution au choix de l'élève ; `option=False` : la case de la sortie (`option(...)`) n'existe pas pour cette résolution."""
    v = {"cle": cle, "libelle": libelle, "cartes": list(cartes)}
    if not option:
        v["option"] = False
    return v


def option(cle, libelle, cartes, cochee=False):
    """Une case à cocher : quand elle est cochée, les `cartes` s'ajoutent à la fin des cartes affichées ; `cochee` : son état au départ."""
    return {"cle": cle, "libelle": libelle, "cochee": cochee, "cartes": list(cartes)}


def sortie_ok(enonce_tex, cartes, entete=None, besoin_sympy=None, option=None):
    s = {"ok": True, "erreur": None, "enonce_tex": enonce_tex, "cartes": list(cartes)}
    if entete is not None:
        s["entete"] = entete
    if besoin_sympy is not None:
        s["besoin_sympy"] = besoin_sympy
    if option is not None:
        s["option"] = option
    return s


def sortie_ok_variantes(enonce_tex, variantes, defaut, option=None):
    """Sortie à plusieurs résolutions : `variantes` (liste de `variante(...)`), `defaut` = la clé de celle qui s'affiche d'abord ;
    `cartes` de la sortie est celle de la variante par défaut (un lecteur qui ignore les variantes affiche donc la bonne)."""
    par_cle = {v["cle"]: v for v in variantes}
    s = sortie_ok(enonce_tex, par_cle[defaut]["cartes"], option=option)
    s["variantes"] = list(variantes)
    s["variante_defaut"] = defaut
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
    _valider_variantes(s, ecarts)
    _valider_option(s, ecarts)
    return ecarts


def _valider_option(s, ecarts):
    if "option" not in s:
        if any("option" in v for v in s.get("variantes", []) if isinstance(v, dict)):
            ecarts.append("sortie : une variante déclare option sans que la sortie en ait une")
        return
    o = s["option"]
    if not _cles(o, *OPTION, "option", ecarts):
        return
    if not _texte_non_vide(o.get("cle")) or not _texte_non_vide(o.get("libelle")):
        ecarts.append("option : cle et libelle sont des textes non vides")
    if o.get("cochee") is not True and o.get("cochee") is not False:
        ecarts.append("option : cochee doit être un booléen")
    if not isinstance(o.get("cartes"), list) or not o["cartes"]:
        ecarts.append("option : cartes doit être une liste non vide")
        return
    for j, c in enumerate(o["cartes"]):
        _valider_carte(c, f"option.cartes[{j}]", ecarts)
    for i, v in enumerate(s.get("variantes", [])):
        if isinstance(v, dict) and "option" in v and v["option"] is not False:
            ecarts.append(f"variantes[{i}] : option doit être false")


def _valider_variantes(s, ecarts):
    if ("variantes" in s) != ("variante_defaut" in s):
        ecarts.append("sortie : variantes et variante_defaut vont ensemble")
        return
    if "variantes" not in s:
        return
    if not isinstance(s["variantes"], list) or not s["variantes"]:
        ecarts.append("sortie : variantes doit être une liste non vide")
        return
    cles = []
    for i, v in enumerate(s["variantes"]):
        chemin = f"variantes[{i}]"
        if not _cles(v, *VARIANTE, chemin, ecarts):
            continue
        if not _texte_non_vide(v.get("cle")) or not _texte_non_vide(v.get("libelle")):
            ecarts.append(f"{chemin} : cle et libelle sont des textes non vides")
        cles.append(v.get("cle"))
        if not isinstance(v.get("cartes"), list):
            ecarts.append(f"{chemin} : cartes doit être une liste")
            continue
        for j, c in enumerate(v["cartes"]):
            _valider_carte(c, f"{chemin}.cartes[{j}]", ecarts)
    if len(set(cles)) != len(cles):
        ecarts.append("sortie : deux variantes ont la même clé")
    defaut = s["variante_defaut"]
    if defaut not in cles:
        ecarts.append(f"sortie : variante_defaut « {defaut} » inconnue")
    elif s["cartes"] != next(v["cartes"] for v in s["variantes"] if v.get("cle") == defaut):
        ecarts.append("sortie : cartes doit être celle de la variante par défaut")


def _valider_carte(c, chemin, ecarts):
    if not _cles(c, *CARTE, chemin, ecarts):
        return
    if c.get("style") not in STYLES_CARTE:
        ecarts.append(f"{chemin} : style « {c.get('style')} » inconnu")
    if "titre_masque" in c and c["titre_masque"] is not True:
        ecarts.append(f"{chemin} : titre_masque doit être true")
    if not isinstance(c.get("blocs"), list):
        ecarts.append(f"{chemin} : blocs doit être une liste")
        return
    for j, b in enumerate(c["blocs"]):
        _valider_bloc(b, f"{chemin}.blocs[{j}]", ecarts)
