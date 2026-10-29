"""
resoudre_el.py — Adaptateur « format de sortie commun » (moteur/sortie.py) de l'outil Exponentielles et logarithmes.

Une carte par application de méthode (« Étape k », badge = la méthode), dans l'ordre où le moteur les rédige, puis la carte finale
« Solution » (équation : S = {…}, puis le contrôle à la calculatrice quand une solution rationnelle est écrite avec des logarithmes) ou « Résultat »
(calcul de log_a(y)). Une équation exponentielle a deux résolutions calculées en une fois (`variantes`) : « Même base / définition » et
« Logarithmes » (défaut) ; quand la première ne s'applique pas, sa dernière carte le dit et il n'y a pas de carte finale. Quand aucune méthode
ne s'applique, une erreur au message prévu (EL-11) : jamais une étape fausse ni une valeur donnée comme solution. Tout le TeX vient de l'arbre
de exp_log.py.
"""
import re
from html import escape

from noyau import ErreurSaisie, json_strict
import sortie as so
import exp_log as el
import exp_log_m as elm
import resoudre_ed
from exp_log import apercu_json, exercice_json

__all__ = ["resoudre", "resoudre_json", "apercu_json", "exercice_json"]

LIBELLES = {el.METHODE_MEME_BASE: "Même base / définition", el.METHODE_LOGARITHMES: "Logarithmes"}


def _ligne(chaine):
    """Une chaîne du corrigé, une étape par ligne : le lien (⇔) à gauche, l'expression, la propriété à droite (commun à la page :
    grille `.chaine` de exponentielles-logarithmes/index.html, la propriété passe sous l'expression sur un écran étroit).
    Une phrase (méthode « même base » qui ne s'applique pas) est un simple texte."""
    if isinstance(chaine, el.Message):
        return so.texte(chaine.html(), style="etape")
    rangees = "".join(
        '<div class="ligne"><span class="lien">' + (r"\(" + lien + r"\)" if lien else "") + '</span>'
        '<span class="expr">' + r"\(" + escape(expr, quote=False) + r"\)" + '</span>'
        '<span class="prop">' + (escape(prop, quote=False) if prop else "") + "</span></div>"
        for lien, expr, prop in el.rangees_chaine(chaine))
    return so.texte('<div class="chaine">' + rangees + "</div>", style="etape")


_TEXTE = re.compile(r"(\\text\{[^{}]*\})")
_X = re.compile(r"(?<![\\A-Za-z])x(?![A-Za-z])")


def _tex_renomme(tex, nom):
    """Le TeX de l'outil ED (qui écrit toujours x) avec l'inconnue `nom` ; les mots d'un \\text{…} et les commandes ne changent pas."""
    return "".join(p if p.startswith(r"\text{") else _X.sub(nom, p) for p in _TEXTE.split(tex))


def _renomme(b, nom):
    """Le bloc de l'outil ED avec l'inconnue `nom` à la place de x (formules, texte entre \\( et \\), tableaux)."""
    if nom == "x":
        return b
    b = dict(b)
    for cle in ("tex", "cond_tex"):
        if cle in b:
            b[cle] = _tex_renomme(b[cle], nom)
    if "html" in b:
        b["html"] = re.sub(r"\\\((.*?)\\\)", lambda m: "\\(" + _tex_renomme(m.group(1), nom) + "\\)", b["html"])
    if b.get("type") == "tableau":
        b["var"] = nom
        b["crit"] = [_tex_renomme(c, nom) for c in b["crit"]]
        b["rows"] = [{**r, "label": _tex_renomme(r["label"], nom)} for r in b["rows"]]
    return b


def _blocs_ed(ed):
    """Les blocs de la carte « Ensemble de définition » : une rubrique par condition (cartes de l'outil ED), puis « ED = … »."""
    if ed.res is None:                                   # base inconnue : la condition est celle du corrigé de la 3C
        return [_ligne(ed.base), so.resultat("ED = " + ed.ed_tex)]
    blocs = []
    for c in ed.res["conditions"]:
        blocs.append(so.texte(f"<strong>Condition {c['num']}</strong> · {escape(c['titre'], quote=False)}", style="etape"))
        blocs += resoudre_ed.blocs_condition(c)
    blocs += resoudre_ed.blocs_ensemble(ed.res)
    return [_renomme(b, ed.inconnue) for b in blocs]


def _cartes(r):
    cartes = []
    for k, c in enumerate(r["etapes"], 1):
        blocs = _blocs_ed(c["ed"]) + [_ligne(ligne) for ligne in c["apres"]] if "ed" in c else [_ligne(ligne) for ligne in c["lignes"]]
        if r["remarque"] and k == len(r["etapes"]):
            blocs.append(so.texte(escape(r["remarque"], quote=False), style="etape"))
        cartes.append(so.carte(f"Étape {k}", blocs, badge=c["titre"]))
    return cartes


def _carte_solution(r):
    """La carte finale d'une équation : S = {…}, puis « Contrôlez à la calculatrice : … » quand une solution rationnelle s'écrit avec des logarithmes."""
    blocs = [so.resultat(el.tex_solution(r))]
    controle = el.controle_calculatrice(r)
    if controle is not None:
        blocs.append(so.texte(controle, style="etape"))
    return so.carte("Solution", blocs, style="final")


def _cartes_equation(r):
    """Les cartes d'une résolution : les étapes, puis la carte finale (aucune quand la méthode ne s'applique pas)."""
    return _cartes(r) + ([] if r.get("message") else [_carte_solution(r)])


def _carte_interpretation(inter):
    """La carte « Interprétation » : les lignes du calcul, puis la phrase de la fin en gras (un texte, pas une formule : elle passe à la ligne sur
    un écran étroit)."""
    blocs = [_ligne(ligne) for ligne in inter["carte"]["lignes"]]
    blocs.append(so.texte("<strong>" + escape(inter["conclusion"], quote=False) + "</strong>", style="etape"))
    return so.carte("Interprétation", blocs, style="final")


def _option(s, r):
    """La case « Problème d'application (temps en années) » de la sortie, ou None quand l'interprétation n'a pas de sens ; pré-cochée avec un
    paramètre ou l'inconnue n (`suggere_interpretation`)."""
    inter = el.interpretation(r)
    if inter is None:
        return None
    return so.option("interpretation", el.LIBELLE_INTERPRETATION, [_carte_interpretation(inter)], el.suggere_interpretation(s))


def _sortie_equation(s, r):
    """La sortie d'une équation sans variantes : ses cartes, la case d'interprétation, et `besoin_sympy` quand l'ensemble de définition en demande."""
    return so.sortie_ok(el.tex_saisie(s.g, s.d), _cartes_equation(r), option=_option(s, r), besoin_sympy=r.get("besoin_sympy") or None)


def resoudre(entree, filiere="C"):
    """`filiere` : "C" (3C, sans ensemble de définition) ou "M" (2Ms et 2Mr : ensemble de définition, vérification des solutions)."""
    if filiere not in el.FILIERES:
        return so.sortie_erreur(el.MESSAGE_FILIERE)
    try:
        return _resoudre(entree, filiere)
    except OverflowError:                                # log(log(log(x))) = 1 : x = 10^(10^10), que l'arithmétique flottante ne peut pas écrire
        return so.sortie_erreur(el.MESSAGE_TROP_GRAND)


def _resoudre(entree, filiere):
    try:
        s = el.analyser_saisie(entree, filiere)
    except ErreurSaisie as e:
        return so.sortie_erreur(str(e))
    if s.genre == "calcul":
        r = el.calculer_logarithme(s.g)
        if r is None:
            return so.sortie_erreur(el.message_calcul_non_resolu(s.g))
        final = so.carte("Résultat", [so.resultat(el.tex_resultat(r))], style="final")
        return so.sortie_ok(el.tex_saisie(s.g, s.d), _cartes(r) + [final])
    if filiere == "M":
        variantes = elm.variantes_changement(s.g, s.d, s.inconnue)
        if variantes is not None:
            return so.sortie_ok_variantes(el.tex_saisie(s.g, s.d), [so.variante(m, LIBELLES[m], _cartes_equation(variantes[m])) for m in el.METHODES],
                                          el.METHODE_LOGARITHMES)
        if elm.reconnu_changement(s.g, s.d, s.inconnue):          # au programme M (e^x + e^(−x) = 3 : racines irrationnelles) mais pas encore traité
            return so.sortie_erreur(el.MESSAGE_PAS_ENCORE)
        variantes = elm.variantes_exposant(s.g, s.d, s.inconnue)  # e^(6/x) = e^(x − 1), 7^√x = 3, e^(−ln x) = 3 : l'ensemble de définition d'abord
        if variantes is not None:
            return so.sortie_ok_variantes(el.tex_saisie(s.g, s.d), [so.variante(m, LIBELLES[m], _cartes_equation(variantes[m])) for m in el.METHODES],
                                          el.METHODE_LOGARITHMES)
        if elm.reconnu_exposant(s.g, s.d, s.inconnue):
            return so.sortie_erreur(el.MESSAGE_PAS_ENCORE)
        r = elm.corriger_equation(s.g, s.d, s.inconnue)
        if r is not None:
            return _sortie_equation(s, r)
        if elm.contient_log_en_x(s.g, s.d):              # jamais le corrigé de la 3C (sans ensemble de définition) pour un 2M
            return so.sortie_erreur(el.message_non_resolu(s.g, s.d, s.inconnue))
    variantes = el.variantes_equation(s.g, s.d, s.inconnue, s.parametres)
    if variantes is not None:
        option = _option(s, variantes[el.METHODE_LOGARITHMES])
        return so.sortie_ok_variantes(
            el.tex_saisie(s.g, s.d),
            [so.variante(m, LIBELLES[m], _cartes_equation(variantes[m]), option=option is None or el.interpretation(variantes[m]) is not None)
             for m in el.METHODES],
            el.METHODE_LOGARITHMES, option=option)
    r = el.corriger_equation(s.g, s.d, s.inconnue, parametres=s.parametres)
    if r is None:
        g, d, _ = el.preparer_application(s.g, s.d, s.inconnue, s.parametres)
        return so.sortie_erreur(el.message_non_resolu(g, d, s.inconnue))
    return so.sortie_ok(el.tex_saisie(s.g, s.d), _cartes_equation(r), option=_option(s, r))


def resoudre_json(entree, filiere="C"):
    return json_strict(resoudre(entree, filiere))
