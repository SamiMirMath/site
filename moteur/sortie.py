"""
sortie.py — Format de sortie commun des outils (D2) : constructeurs et validateur.

Python pur, bibliothèque standard seulement. Une sortie de `resoudre()` est un dict :

    {ok, erreur, detail?, enonce_tex, entete?, cartes: [carte], besoin_sympy?, variantes?, variante_defaut?, option?}
    carte = {titre, titre_tex?, titre_masque?, badge?, style, blocs: [bloc]}
            style « partie » : intertitre d'une partie (Étude complète, D1), sans bloc ; la page l'affiche avec la carte qui le suit
    bloc  = texte | formule | resultat | erreur | liste | tableau | graphique | uv (tableau u, v / u′, v′) | bh, encadre, resultat_lim,
            valeurs, sous_calcul (corrigé des limites ; sous_calcul aussi pour la dérivée de l'exposant) | chaine (chaîne du corrigé)
            | tableau_essais (tableau S-P du 2e degré)
    variante = {cle, libelle, cartes: [carte], option?: false}   (facultatif : plusieurs résolutions de la même entrée, au choix de l'élève ;
               `cartes` de la sortie est alors celles de la variante par défaut ; `option: false` : pas de case à cocher pour cette variante)
    option = {cle, libelle, cochee, cartes: [carte]}   (facultatif : une case à cocher dont les cartes s'ajoutent à la fin des cartes affichées ;
               `cochee` est son état au départ)

    chaine = {rangees: [rangée]}   chaîne de ⇔ du corrigé, une étape par ligne, les ⇔ alignés (chantier briques-communes, B3)
            rangée = ligne {lien, expr, prop?, gauche?}  lien : « », \\iff ou \\Rightarrow (TeX) ; expr, gauche : TeX ; prop : la
                                                         propriété (texte, le TeX entre \\( et \\)) ; gauche : le membre de gauche,
                                                         seulement sur la première ligne, avant son lien (le corrigé : « A ⇔ B »)
                   | {texte}                             ligne pleine largeur au milieu de la chaîne (texte, le TeX entre \\( et \\))
                   | {bloc}                              ligne pleine largeur qui contient un bloc (BLOCS_DANS_CHAINE)
    tableau_essais = {groupes: [{titre, colonnes}], lignes: [{cases, ok?}]}   tableau d'essais du corrigé (S-P du 2e degré, E6, D4) :
            groupes : l'en-tête, un titre (texte, le TeX entre \\( et \\)) par groupe de `colonnes` colonnes (« produit = −42 » sur deux
            colonnes, « somme » sur une) ; lignes : une ligne par essai, `cases` en TeX (autant que de colonnes) ; `ok: true` sur la
            ligne qui aboutit (au plus une ; le rendu l'encadre et y ajoute ✓, D29) ; aucune ligne ok : échec (D3)
            Jamais de HTML dans un champ (A4) : le rendu (commun/rendu.js) échappe les textes et fabrique le HTML.

`valider(sortie)` renvoie la liste des écarts au schéma (vide si la sortie est conforme).
"""
import re


STYLES_CARTE = ("normal", "etape", "final", "erreur", "partie")
STYLES_TEXTE = ("etape", "discret", "indice", "confirme")
STYLES_LISTE = ("extrema", "bilan")
GENRES_ENCADRE = ("prediction", "attention", "piege", "autre")
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
    # blocs du corrigé des limites (refonte 3M, 30.10.2026)
    "bh": ({"haut", "dhaut", "bas", "dbas"}, set()),
    "encadre": ({"genre", "titre", "lignes"}, set()),
    "resultat_lim": ({"tex"}, set()),
    "valeurs": ({"expr", "xs", "fs"}, set()),
    "sous_calcul": ({"titre", "etapes"}, set()),
    # tableau u | v / u′ | v′ des règles du produit et du quotient (Étude complète, D8 ; outil Dérivée)
    "uv": ({"u", "du", "v", "dv"}, set()),
    "graphique": ({"xmin", "xmax", "ymin", "ymax", "segments", "extrema", "asymptotes"}, {"recalculable", "points", "ronds_vides"}),
    # chaîne de ⇔ du corrigé, avec des lignes pleine largeur au milieu (chantier briques-communes, B3 ; docs/architecture.md, A4)
    "chaine": ({"rangees"}, set()),
    # tableau d'essais du corrigé : S-P du 2e degré (chantier equations-2e-degre, E6, D3, D4, D29)
    "tableau_essais": ({"groupes", "lignes"}, set()),
}
# bloc « chaine » : une ligne de la chaîne, ses liens, et les blocs qu'une ligne pleine largeur peut contenir
RANGEE = ({"lien", "expr"}, {"prop", "gauche"})
LIENS_CHAINE = ("", "\\iff", "\\Rightarrow")
BLOCS_DANS_CHAINE = ("texte", "formule", "tableau", "tableau_essais")
# bloc « tableau_essais » : un groupe de colonnes de l'en-tête, une ligne d'essai
GROUPE_ESSAIS = ({"titre", "colonnes"}, set())
LIGNE_ESSAIS = ({"cases"}, {"ok"})
# HTML dans un champ de texte ou de TeX (A4) : une balise ouvrante ou fermante, ou une entité ; « x < y » et « \(a<b\) » n'en sont pas
HTML = re.compile(r"</?[A-Za-z][A-Za-z0-9-]*(?:\s[^<>]*)?/?>|&(?:[A-Za-z][A-Za-z0-9]*|#[0-9]+|#[xX][0-9A-Fa-f]+);")
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


def bh(haut, dhaut, bas, dbas):
    """Tableau BH du corrigé : « haut : f ⟶ dérivée : f′ » / « bas : g ⟶ dérivée : g′ » (tex)."""
    return {"type": "bh", "haut": haut, "dhaut": dhaut, "bas": bas, "dbas": dbas}


def encadre(genre, titre, lignes):
    """Encadré du corrigé (genre : prediction, attention, piege, autre) ; `lignes` : html (formules entre \\( \\))."""
    return {"type": "encadre", "genre": genre, "titre": titre, "lignes": list(lignes)}


def resultat_lim(tex):
    """Résultat encadré vert (cadre .rbox) : le résultat d'une limite (« lim … = … ») ; l'ensemble des solutions d'une équation
    (« S = {…} », 2e degré, D29), dans une carte normale (pas de double cadre)."""
    return {"type": "resultat_lim", "tex": tex}


def valeurs(expr, xs, fs):
    """Tableau de valeurs (8.14) : ligne des x et ligne des valeurs de l'expression (tex)."""
    return {"type": "valeurs", "expr": expr, "xs": list(xs), "fs": list(fs)}


def sous_calcul(titre, etapes):
    """Sous-limite calculée à part (« On calcule à part … ») : étapes = [{titre, blocs}]."""
    return {"type": "sous_calcul", "titre": titre, "etapes": list(etapes)}


def uv(u, du, v, dv):
    """Tableau 2 × 2 des règles du produit et du quotient (D8) : colonnes u | v, lignes fonction | dérivée ; chaque case est une
    formule complète (« u = x^{2} - 6 », « u' = 2x »). La page empile les deux colonnes (u, u′, v, v′) si elles ne tiennent pas côte à côte."""
    return {"type": "uv", "u": u, "du": du, "v": v, "dv": dv}


def chaine(rangees):
    """Chaîne de ⇔ du corrigé (une étape par ligne, ⇔ alignés) : `rangees` est une liste de `rangee(...)`, `rangee_texte(...)` et
    `rangee_bloc(...)`. Depuis une chaîne de moteur/chaine.py : `chaine.bloc_chaine(c)`."""
    return {"type": "chaine", "rangees": list(rangees)}


def rangee(lien, expr, prop=None, gauche=None):
    """Une ligne de la chaîne : `lien` (« », « \\iff » ou « \\Rightarrow »), `expr` (TeX), `prop` (texte de la propriété, le TeX entre
    \\( et \\), ou None) ; `gauche` : le membre de gauche, avant le lien (première ligne seulement)."""
    r = {"lien": lien, "expr": expr}
    if prop:
        r["prop"] = prop
    if gauche:
        r["gauche"] = gauche
    return r


def rangee_texte(texte_):
    """Une ligne pleine largeur au milieu de la chaîne : un texte, le TeX entre \\( et \\) (jamais de HTML)."""
    return {"texte": texte_}


def rangee_bloc(bloc):
    """Une ligne pleine largeur au milieu de la chaîne qui contient un bloc (types de BLOCS_DANS_CHAINE, par exemple un tableau)."""
    return {"bloc": bloc}


def tableau_essais(groupes, lignes, ok=None):
    """Tableau d'essais du corrigé (S-P du 2e degré, E6 ; D4) : `groupes` = [(titre, colonnes)] pour l'en-tête (titre : texte, le TeX
    entre \\( et \\) ; un filet vertical sépare deux groupes), `lignes` = [[case TeX, …]] (une ligne par essai), `ok` = l'indice de la
    ligne qui aboutit (le rendu l'encadre et y ajoute ✓, D29), ou None pour un échec (aucune ✓, D3). Se place dans une chaîne par
    `rangee_bloc` (ou `LigneTexte` de moteur/chaine.py)."""
    lignes = [list(cases) for cases in lignes]
    if ok is not None and (isinstance(ok, bool) or not isinstance(ok, int) or not 0 <= ok < len(lignes)):
        raise ValueError(f"ok : indice d'une ligne attendu (0 à {len(lignes) - 1}), pas {ok!r}")
    return {"type": "tableau_essais", "groupes": [{"titre": titre, "colonnes": n} for titre, n in groupes],
            "lignes": [dict(cases=cases, **({"ok": True} if i == ok else {})) for i, cases in enumerate(lignes)]}


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


def partie(titre):
    """Intertitre d'une partie (« 4. Limites et asymptotes ») : une carte sans bloc, que la page affiche comme un titre, sans cadre, avec
    la carte qui la suit (ce n'est pas une étape)."""
    return carte(titre, [], style="partie")


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
    elif t in ("bh", "resultat_lim", "uv"):
        for k in obl:
            if not _texte_non_vide(b[k]):
                ecarts.append(f"{chemin} : {k} vide")
    elif t == "encadre":
        if b["genre"] not in GENRES_ENCADRE:
            ecarts.append(f"{chemin} : genre « {b['genre']} » inconnu")
        if not _texte_non_vide(b["titre"]) or not isinstance(b["lignes"], list) or not all(_texte_non_vide(x) for x in b["lignes"]):
            ecarts.append(f"{chemin} : titre et lignes (textes non vides) attendus")
    elif t == "valeurs":
        if not _texte_non_vide(b["expr"]) or not isinstance(b["xs"], list) or not isinstance(b["fs"], list) or len(b["xs"]) != len(b["fs"]):
            ecarts.append(f"{chemin} : valeurs : expr, xs et fs de même longueur attendus")
    elif t == "sous_calcul":
        if not _texte_non_vide(b["titre"]) or not isinstance(b["etapes"], list):
            ecarts.append(f"{chemin} : sous_calcul : titre et étapes attendus")
        else:
            for i, e in enumerate(b["etapes"]):
                if not isinstance(e, dict) or not _texte_non_vide(e.get("titre")) or not isinstance(e.get("blocs"), list):
                    ecarts.append(f"{chemin}.etapes[{i}] : titre et blocs attendus")
                else:
                    for j, bb in enumerate(e["blocs"]):
                        _valider_bloc(bb, f"{chemin}.etapes[{i}].blocs[{j}]", ecarts)
    elif t == "chaine":
        _valider_chaine(b, chemin, ecarts)
    elif t == "tableau_essais":
        _valider_essais(b, chemin, ecarts)


def _sans_html(v, chemin, ecarts):
    """Un champ de texte ou de TeX non vide, sans HTML (A4)."""
    if not _texte_non_vide(v):
        ecarts.append(f"{chemin} : texte non vide attendu")
    elif HTML.search(v):
        ecarts.append(f"{chemin} : HTML interdit dans un champ (A4) : « {HTML.search(v).group(0)} »")


def _valider_chaine(b, chemin, ecarts):
    """Bloc « chaine » : au moins une ligne ; chaque rangée est une ligne {lien, expr, prop?, gauche?} ou une ligne pleine largeur
    {texte} ou {bloc} ; `gauche` seulement sur la première ligne, avec un lien ; un bloc imbriqué est d'un type de BLOCS_DANS_CHAINE."""
    rangees = b["rangees"]
    if not isinstance(rangees, list) or not rangees:
        ecarts.append(f"{chemin} : rangees doit être une liste non vide")
        return
    lignes = 0
    for i, r in enumerate(rangees):
        cr = f"{chemin}.rangees[{i}]"
        if isinstance(r, dict) and set(r) == {"texte"}:
            _sans_html(r["texte"], cr + ".texte", ecarts)
        elif isinstance(r, dict) and set(r) == {"bloc"}:
            bb = r["bloc"]
            if not isinstance(bb, dict) or bb.get("type") not in BLOCS_DANS_CHAINE:
                genre = bb.get("type") if isinstance(bb, dict) else bb
                ecarts.append(f"{cr}.bloc : bloc « {genre} » non permis dans une chaîne ({', '.join(BLOCS_DANS_CHAINE)})")
            else:
                _valider_bloc(bb, cr + ".bloc", ecarts)
        elif isinstance(r, dict) and ("lien" in r or "expr" in r):
            if not _cles(r, *RANGEE, cr, ecarts) or not {"lien", "expr"} <= set(r):
                continue
            if r["lien"] not in LIENS_CHAINE:
                ecarts.append(f"{cr} : lien « {r['lien']} » inconnu")
            for cle in ("expr", "prop", "gauche"):
                if cle in r:
                    _sans_html(r[cle], f"{cr}.{cle}", ecarts)
            if "gauche" in r and (lignes or not r["lien"]):
                ecarts.append(f"{cr} : gauche seulement sur la première ligne, avant un lien")
            lignes += 1
        else:
            ecarts.append(f"{cr} : rangée mal formée (ligne {{lien, expr, prop?, gauche?}}, {{texte}} ou {{bloc}})")
    if not lignes:
        ecarts.append(f"{chemin} : une chaîne a au moins une ligne {{lien, expr}}")


def _valider_essais(b, chemin, ecarts):
    """Bloc « tableau_essais » : au moins un groupe {titre, colonnes} (titre sans HTML, colonnes entier ≥ 1) et une ligne {cases, ok?} ;
    chaque ligne a autant de cases (TeX sans HTML, A4) que l'en-tête a de colonnes ; ok vaut true, sur une ligne au plus."""
    groupes, lignes = b["groupes"], b["lignes"]
    if not isinstance(groupes, list) or not groupes or not isinstance(lignes, list) or not lignes:
        ecarts.append(f"{chemin} : groupes et lignes doivent être des listes non vides")
        return
    colonnes = 0
    for i, g in enumerate(groupes):
        cg = f"{chemin}.groupes[{i}]"
        if not _cles(g, *GROUPE_ESSAIS, cg, ecarts) or not set(GROUPE_ESSAIS[0]) <= set(g):
            colonnes = None
            continue
        _sans_html(g["titre"], cg + ".titre", ecarts)
        n = g["colonnes"]
        if isinstance(n, bool) or not isinstance(n, int) or n < 1:
            ecarts.append(f"{cg} : colonnes doit être un entier ≥ 1")
            colonnes = None
        elif colonnes is not None:
            colonnes += n
    nb_ok = 0
    for i, ligne in enumerate(lignes):
        cl = f"{chemin}.lignes[{i}]"
        if not _cles(ligne, *LIGNE_ESSAIS, cl, ecarts) or "cases" not in ligne:
            continue
        cases = ligne["cases"]
        if not isinstance(cases, list):
            ecarts.append(f"{cl} : cases doit être une liste")
            continue
        if colonnes is not None and len(cases) != colonnes:
            ecarts.append(f"{cl} : {len(cases)} cases, {colonnes} attendues (colonnes de l'en-tête)")
        for j, c in enumerate(cases):
            _sans_html(c, f"{cl}.cases[{j}]", ecarts)
        if "ok" in ligne:
            if ligne["ok"] is not True:
                ecarts.append(f"{cl} : ok doit être true (absent sur les autres lignes)")
            nb_ok += 1
    if nb_ok > 1:
        ecarts.append(f"{chemin} : {nb_ok} lignes ok, une au plus")


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
    if c.get("style") == "partie" and (c["blocs"] or set(c) - {"titre", "style", "blocs"}):
        ecarts.append(f"{chemin} : un intertitre (style partie) n'a que titre, style et blocs vides")
    for j, b in enumerate(c["blocs"]):
        _valider_bloc(b, f"{chemin}.blocs[{j}]", ecarts)
