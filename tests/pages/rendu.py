"""Capture du rendu d'une page outil : le contenu de chaque carte affichée, sous une forme comparable
avant/après une migration (T15 à T20) — texte et formules (LaTeX lu dans les <annotation> KaTeX),
structure des tableaux (classes de lignes et de cases), nombre de cartes, compteur d'étapes.

Les entrées du corpus sont celles de tests/python/cas.py (exemples des pages, cas limites, batterie
de factorisation) : mêmes entrées que les instantanés des moteurs."""
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "python"))
from cas import CAS_LIMITES, entrees_page, entrees_factorisation  # noqa: E402
from cas_el import entrees_el  # noqa: E402

DOSSIER_REFERENCES = os.path.join(os.path.dirname(__file__), "references")
OUTILS = ["ensemble-definition", "derivee-variations", "limites-asymptotes", "etude-complete", "factorisation",
          "exponentielles-logarithmes"]


# Entrées de page ajoutées au corpus des moteurs : une saisie invalide par outil (la carte d'erreur est un rendu à part entière).
ERREURS = {"derivee-variations": ["ln("], "limites-asymptotes": ["ln("], "etude-complete": ["ln("]}

# Corpus réduit (CI) : 3 entrées par outil, dont une erreur ; le corpus complet reste pour le local.
REDUIT = {
    "ensemble-definition": ["ln(x^2-4x)/(x-5)", "sqrt(ln(x)-x+2)", "ln("],
    "derivee-variations": ["ln(x)/x", "x^(2-2)", "ln("],
    "limites-asymptotes": ["(x^2-1)/(x-3)", "(x^2-1)/(x-1)", "ln("],
    "etude-complete": ["e^(1/x)", "x^2*e^(-x)", "ln("],
    "factorisation": ["x^2+5x-14", "(a + b)^2 - 7(a + b)", "sqrt(x)"],
    "exponentielles-logarithmes": ["2^(x-1)=3^x", "log(5-x)=8", "x*2^x=8"],
}


def entrees(outil):
    if outil == "factorisation":
        liste = entrees_factorisation()
    elif outil == "exponentielles-logarithmes":
        liste = entrees_el()
    else:
        liste = entrees_page(outil) + CAS_LIMITES[outil]
    liste = liste + ERREURS.get(outil, [])
    liste = [e for e in dict.fromkeys(liste) if e.strip()]      # champ vide : le bouton ne fait rien
    if os.environ.get("CORPUS") == "reduit":
        liste = [e for e in liste if e in REDUIT[outil]]
        assert len(liste) == len(REDUIT[outil]), f"corpus réduit de {outil} : entrée absente du corpus"
    return liste


# Contenu normalisé de #cartes (injecté dans la page).
JS_CAPTURE = r"""
(() => {
  const norm = el => {
    const c = el.cloneNode(true);
    c.querySelectorAll('.katex').forEach(k => {
      const a = k.querySelector('annotation[encoding="application/x-tex"]');
      k.replaceWith(document.createTextNode('⟦' + (a ? a.textContent : k.textContent) + '⟧'));
    });
    c.querySelectorAll('canvas').forEach(k => k.replaceWith(document.createTextNode('[canvas]')));
    return c;
  };
  const txt = el => norm(el).textContent.replace(/\s+/g, ' ').trim();
  const cartes = [...document.querySelectorAll('#cartes > *')].map(card => ({
    classes: [...card.classList].filter(c => c !== 'cache').sort(),
    titre: (card.querySelector('h3') ? txt(card.querySelector('h3')) : null),
    texte: txt(card),
    tableaux: [...card.querySelectorAll('.tsigne table')].map(t => [...t.rows].map(r => ({
      classe: r.className, cases: [...r.cells].map(c => [c.className, txt(c)])
    }))),
    listes: [...card.querySelectorAll('ul')].map(u => [u.className, [...u.children].map(txt)]),
  }));
  return {
    cartes,
    visibles: [...document.querySelectorAll('#cartes > *')].filter(c => !c.classList.contains('cache')).length,
    progression: (document.querySelector('#progression') || {}).textContent || '',
  };
})()
"""


# Boutons du sélecteur de méthode : [{cle, texte, choisi}], ou None quand la sortie n'a pas de variantes.
JS_BOUTONS = r"""
(() => {
  const barre = document.querySelector('#variantes');
  if (!barre || barre.hidden) return null;
  return [...barre.querySelectorAll('button')].map(b => ({ cle: b.dataset.variante, texte: b.textContent, choisi: b.getAttribute('aria-pressed') === 'true' }));
})()
"""


def attendre_pret(page, delai=240):
    """Attend « Prêt. ». À l'expiration, le message dit où en est le chargement : texte de #etat (« Chargement de Python… »,
    « Chargement du moteur de calcul… », ou rien) et dernières lignes de la console. Une page lente laisse #etat avancer,
    une page bloquée le laisse figé."""
    try:
        page.attendre("document.querySelector('#etat') && document.querySelector('#etat').textContent === 'Prêt.' "
                      "&& !document.querySelector('#calculer').disabled", delai)
    except TimeoutError as e:
        try:
            etat = page.evaluer("(document.querySelector('#etat') || {}).textContent")
        except Exception as ex:                  # page plantée ou fermée
            etat = f"(illisible : {ex})"
        raise TimeoutError(f"{e}\n  #etat : {etat!r}\n  console : {page.console[-5:]}") from None


def capturer(page, entree):
    """Calcule `entree` dans la page et renvoie le rendu (toutes les cartes dépliées)."""
    page.evaluer("document.querySelector('#cartes').innerHTML = ''")
    page.evaluer(f"document.querySelector('#entree').value = {json.dumps(entree)}; document.querySelector('#calculer').click()")
    page.attendre("document.querySelector('#cartes').children.length > 0 && !document.querySelector('#calculer').disabled", 120)
    page.evaluer("document.querySelector('#cartes').getAttribute('data-x')")           # laisse l'affichage se poser
    # Ensemble de définition : le badge « contrôle numérique » arrive après l'affichage
    if page.evaluer("!!document.querySelector('#cartes .card.final .res') && !document.querySelector('#cartes .card.final .res.err')"
                    " && /ensemble-definition/.test(location.pathname)"):
        try:
            page.attendre("document.querySelector('#cartes .verif')", 20)
        except TimeoutError:
            pass
    debut = page.evaluer(JS_CAPTURE)
    boutons = page.evaluer(JS_BOUTONS)
    page.evaluer("document.querySelector('#tout') && !document.querySelector('#tout').disabled && document.querySelector('#tout').click()")
    fin = page.evaluer(JS_CAPTURE)
    res = {"au_depart": {"visibles": debut["visibles"], "progression": debut["progression"]},
           "cartes": fin["cartes"], "progression_finale": fin["progression"]}
    if boutons:                       # sélecteur de méthode (outil.js) : les boutons, puis le corrigé complet de chaque variante
        res["boutons"] = boutons
        res["variantes"] = {}
        for b in boutons:
            page.evaluer(f"document.querySelector('#variantes button[data-variante=\"{b['cle']}\"]').click()")
            page.evaluer("document.querySelector('#tout').click()")
            vue = page.evaluer(JS_CAPTURE)
            res["variantes"][b["cle"]] = {"cartes": vue["cartes"], "progression_finale": vue["progression"],
                                          "imprimee": page.evaluer("document.querySelector('#methodeImprimee').textContent")}
        defaut = next(b["cle"] for b in boutons if b["choisi"])
        page.evaluer(f"document.querySelector('#variantes button[data-variante=\"{defaut}\"]').click()")          # le choix est gardé d'une saisie à l'autre
        assert res["variantes"][defaut]["cartes"] == res["cartes"]
    return res


def capturer_outil(nav, outil, filtre=None):
    page = nav.ouvrir(f"{outil}/index.html")
    attendre_pret(page)
    res = {}
    for e in entrees(outil):
        if filtre and e not in filtre:
            continue
        res[e] = capturer(page, e)
    return res
