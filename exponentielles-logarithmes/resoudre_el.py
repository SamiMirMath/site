"""
resoudre_el.py — Adaptateur « format de sortie commun » (moteur/sortie.py) de l'outil Exponentielles et logarithmes.

Une carte par application de méthode (« Étape k », badge = la méthode), dans l'ordre où le moteur les rédige, puis la carte finale
« Solution » (équation : S = {…}, puis le contrôle à la calculatrice quand une solution rationnelle est écrite avec des logarithmes) ou « Résultat »
(calcul de log_a(y)). Une équation exponentielle a deux résolutions calculées en une fois (`variantes`) : « Même base / définition » et
« Logarithmes » (défaut) ; quand la première ne s'applique pas, sa dernière carte le dit et il n'y a pas de carte finale. Quand aucune méthode
ne s'applique, une erreur au message prévu (EL-11) : jamais une étape fausse ni une valeur donnée comme solution. Tout le TeX vient de l'arbre
de exp_log.py.
"""
from html import escape

from noyau import ErreurSaisie, json_strict
import sortie as so
import exp_log as el
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


def _cartes(r):
    cartes = []
    for k, c in enumerate(r["etapes"], 1):
        blocs = [_ligne(ligne) for ligne in c["lignes"]]
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
    """La carte « Interprétation » : les lignes du calcul, puis la phrase de la fin dans un encadré."""
    blocs = [_ligne(ligne) for ligne in inter["carte"]["lignes"]]
    blocs.append(so.resultat(r"\text{" + inter["conclusion"] + "}"))
    return so.carte("Interprétation", blocs, style="final")


def _option(s, r):
    """La case « Problème d'application (temps en années) » de la sortie, ou None quand l'interprétation n'a pas de sens ; pré-cochée avec un
    paramètre ou l'inconnue n (`suggere_interpretation`)."""
    inter = el.interpretation(r)
    if inter is None:
        return None
    return so.option("interpretation", el.LIBELLE_INTERPRETATION, [_carte_interpretation(inter)], el.suggere_interpretation(s))


def resoudre(entree):
    try:
        s = el.analyser_saisie(entree)
    except ErreurSaisie as e:
        return so.sortie_erreur(str(e))
    if s.genre == "calcul":
        r = el.calculer_logarithme(s.g)
        if r is None:
            return so.sortie_erreur(el.message_calcul_non_resolu(s.g))
        final = so.carte("Résultat", [so.resultat(el.tex_resultat(r))], style="final")
        return so.sortie_ok(el.tex_saisie(s.g, s.d), _cartes(r) + [final])
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


def resoudre_json(entree):
    return json_strict(resoudre(entree))
