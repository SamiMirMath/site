"""Bloc « chaine » (chantier briques-communes, B3 ; docs/architecture.md, A4) rendu par commun/rendu.js dans Chrome.

Une chaîne de ⇔ du corrigé, construite en Python par moteur/chaine.py (`bloc_chaine`) et moteur/sortie.py, sur le modèle des corrigés du
2e degré (Id_rem.pdf, 2.9 a et c) : membre de gauche, ⇔ alignés, étiquettes grises, « impossible » sous le facteur constant, une ligne
pleine largeur au milieu (un texte, ou un bloc : tableau, texte), puis d'autres ⇔. Aucune page nouvelle (rien de publié, rien dans le
registre) : comme le test SOC-22 (test_comportement.py), les cartes sont rendues dans la page d'un outil existant (Ensemble de
définition), qui charge KaTeX, commun/style.css, commun/composants.css et commun/rendu.js, mais pas le CSS de la grille .chaine (encore
dans la page Exponentielles et logarithmes).

Ce qui passe dès B3 : structure (mêmes classes que la grille d'Exp-log), formules rendues par KaTeX, textes échappés, blocs imbriqués,
sortie validée par `sortie.valider`, aucune faute du balayage des largeurs (320 à 1100 px, clair et sombre : test_largeurs.JS_MESURE),
rien hors de la carte, couleurs du thème. Ce qui ne peut passer qu'avec le CSS .chaine commun (B4 : il passe de la page Exp-log à
commun/composants.css) est marqué xfail STRICT « B4 » : colonnes alignées avant et après la ligne pleine largeur, repli sur un écran
étroit (propriété sous l'expression, membre de gauche au-dessus, pas de défilement), étiquette grise."""
import json
import os
import sys
import unittest
from fractions import Fraction as F

import pytest

sys.path.insert(0, os.path.dirname(__file__))
from navigateur import Navigateur  # noqa: E402
from rendu import attendre_pret  # noqa: E402  (met aussi tests/python sur le chemin)
from test_largeurs import JS_MESURE, LARGEURS, erreurs_a_signaler  # noqa: E402
import moteurs  # noqa: E402,F401  (chemins des moteurs)
import sortie as so  # noqa: E402
from chaine import Chaine, Eq, Message, Ou, Texte, bloc_chaine  # noqa: E402
from expr import LEXIQUE_COMMUN, Nb, Var, lire_membres  # noqa: E402

PAGE = "ensemble-definition"                 # n'importe quelle page d'outil qui charge KaTeX et commun/rendu.js


def xfail_b4(quoi):
    return pytest.mark.xfail(strict=True, reason=f"B4 : {quoi} (CSS .chaine de la page Exp-log vers commun/composants.css)")


def eq(texte):
    g, d = lire_membres(texte, LEXIQUE_COMMUN)
    return Eq(g, d)


def chaine_2_9_c():
    """Id_rem.pdf, 2.9 c : la ligne « Id. rem. … Vérification … ✓ » pleine largeur entre la ME et 3(4z − 9)² = 0."""
    c = Chaine([eq("48z^2 - 216z + 243 = 0"), eq("3(16z^2 - 72z + 81) = 0")], ["⇔"], ["ME"])
    verification = Message("Id. rem. ", Texte("A^{2} - 2AB + B^{2}"), " avec ", Texte("A = 4z"), ", ", Texte("B = 9"),
                           ". Vérification : ", Texte(r"2AB = 2 \cdot 4z \cdot 9 = 72z"), " ✓")
    c.ajouter(eq("3(4z - 9)^2 = 0"), "⇔", texte_avant=verification)
    c.ajouter(Ou([Eq(Nb(3), Nb(0)), eq("4z - 9 = 0")]), "⇔", "produit nul")
    c.ajouter(Eq(Var("z"), Nb(F(9, 4))), "⇔")
    return c


TABLEAU = {"type": "tableau", "var": "x", "crit": ["-6", "7"],
           "rows": [{"label": "x + 6", "cells": ["-", "0", "+", "|", "+"]},
                    {"label": "x - 7", "cells": ["-", "|", "-", "0", "+"]},
                    {"label": "(x + 6)(x - 7)", "cells": ["+", "0", "-", "0", "+"], "final": True}]}


def chaine_avec_tableau():
    """Une ligne de texte puis un bloc (tableau) pleine largeur au milieu de la chaîne, et un bloc texte imbriqué."""
    c = Chaine([eq("x^2 - x - 42 = 0"), eq("(x + 6)(x - 7) = 0")], ["⇔"], [None],
               textes={1: ["On cherche deux nombres dont le produit vaut −42 et la somme vaut −1 :", TABLEAU]})
    c.ajouter(Ou([eq("x + 6 = 0"), eq("x - 7 = 0")]), "⇔", "produit nul",
              texte_avant=so.texte("Le <strong>produit</strong> est nul :"))
    c.ajouter(Ou([Eq(Var("x"), Nb(-6)), Eq(Var("x"), Nb(7))]), "⇔")
    return c


def cartes():
    """Les cartes du test : 2.9 c avec membre de gauche et étiquettes grises, 2.9 c comme Exp-log (trois colonnes, parenthèses), et la
    chaîne au tableau ; plus une carte dont le texte ressemble à du HTML (le rendu l'échappe ; `valider` la refuserait)."""
    blocs = [bloc_chaine(chaine_2_9_c(), etiquette_grise=True, impossible=True, membre_gauche=True),
             bloc_chaine(chaine_2_9_c()),
             bloc_chaine(chaine_avec_tableau(), etiquette_grise=True, membre_gauche=True)]
    valides = [so.carte(f"Chaîne {i + 1}", [b]) for i, b in enumerate(blocs)]
    echappe = so.carte("Échappement", [so.chaine([so.rangee("", "x < y", prop="a < b & c"),
                                                  so.rangee_texte('<img src="x" onerror="window.__injecte = 1"> &amp; 1 < 2')])])
    return valides, echappe


JS_RENDRE = r"""
(async (cartes) => {
  const { rendreCarte } = await import('/commun/rendu.js');
  document.querySelector('#resultat').hidden = false;
  const zone = document.querySelector('#cartes');
  zone.innerHTML = '';
  for (const c of cartes) zone.appendChild(rendreCarte(c));
  return zone.children.length;
})
"""

# Pour chaque chaîne : ses rangées dans l'ordre (classe), les boîtes de chaque colonne de chaque ligne, des lignes pleine largeur et de la
# chaîne, si son bloc défile, et la couleur de chaque colonne.
JS_CHAINES = r"""
(async () => {
  await new Promise(r => setTimeout(r, 150));
  const boite = e => { const r = e.getBoundingClientRect(); return {g: r.left, d: r.right, h: r.top, b: r.bottom}; };
  return [...document.querySelectorAll('#cartes .chaine')].map(ch => {
    const col = (l, k) => { const e = l.querySelector(':scope > .' + k); if (!e) return null;
      const st = getComputedStyle(e);
      return {...boite(e), vide: !e.textContent.trim(), affiche: st.display !== 'none', couleur: st.color, taille: parseFloat(st.fontSize)}; };
    const enfants = [...ch.children];
    return {
      ordre: enfants.map(e => e.className),
      lignes: enfants.filter(e => e.classList.contains('ligne')).map(l => ({gauche: col(l, 'gauche'), lien: col(l, 'lien'), expr: col(l, 'expr'), prop: col(l, 'prop')})),
      pleines: enfants.filter(e => e.classList.contains('pleine')).map(p => ({...boite(p), couleur: getComputedStyle(p).color})),
      chaine: boite(ch), carte: boite(ch.closest('.card')), defile: ch.parentElement.scrollWidth > ch.parentElement.clientWidth + 1,
      muted: getComputedStyle(document.documentElement).getPropertyValue('--muted').trim(),
      fg: getComputedStyle(document.body).color, fond: getComputedStyle(ch.closest('.card')).backgroundColor,
    };
  });
})()
"""

# Formules et lignes pleine largeur hors de leur carte (hors d'un bloc qui défile lui-même).
JS_HORS_CARTE = r"""
(async () => {
  await new Promise(r => setTimeout(r, 150));
  const out = [];
  for (const k of document.querySelectorAll('#cartes .chaine .katex, #cartes .chaine > .pleine, #cartes .chaine')) {
    const c = k.closest('.card');
    let defile = false;
    for (let m = k.parentElement; m && m !== c; m = m.parentElement) {
      const o = getComputedStyle(m).overflowX; if (o === 'auto' || o === 'scroll') defile = true; }
    const r = k.getBoundingClientRect(), rc = c.getBoundingClientRect();
    if (!defile && r.width > 0 && (r.right > rc.right + 1 || r.left < rc.left - 1)) out.push(k.className + ' ' + k.textContent.slice(0, 40));
  }
  return out;
})()
"""


def rgb(couleur_css):
    """« #5b6478 » → « rgb(91, 100, 120) » (forme de getComputedStyle)."""
    h = couleur_css.lstrip("#")
    return "rgb({}, {}, {})".format(*(int(h[i:i + 2], 16) for i in (0, 2, 4)))


def egaux(valeurs, tolerance=1.0):
    return max(valeurs) - min(valeurs) <= tolerance


class TestBlocChaine(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.nav = Navigateur().__enter__()
        cls.valides, cls.echappe = cartes()
        cls.page = cls.nav.ouvrir(f"{PAGE}/index.html")
        attendre_pret(cls.page)
        cls.page.taille(1100, 800)
        n = cls.page.evaluer(JS_RENDRE + "(" + json.dumps(cls.valides + [cls.echappe]) + ")")
        assert n == len(cls.valides) + 1, n

    @classmethod
    def tearDownClass(cls):
        cls.nav.__exit__(None, None, None)

    def mesurer(self, largeur, sombre=False):
        self.page.taille(largeur, 800, sombre=sombre)
        try:
            return self.page.evaluer(JS_CHAINES)
        finally:
            self.page.taille(1100, 800)

    # ---------- dès B3 ----------
    def test_blocs_valides(self):
        """Les blocs construits par `chaine.bloc_chaine` passent `sortie.valider` ; celui dont le texte ressemble à du HTML est refusé."""
        self.assertEqual(so.valider(so.sortie_ok("x", self.valides)), [])
        self.assertTrue(any("HTML interdit" in e for e in so.valider(so.sortie_ok("x", [self.echappe]))))

    def test_structure_et_formules(self):
        """Mêmes classes que la grille d'Exp-log (.etape > .chaine > .ligne > .lien, .expr, .prop ; .gauche en tête avec un membre de
        gauche) ; une rangée .pleine par ligne pleine largeur, à sa place ; toutes les formules rendues par KaTeX (aucun \\( ni \\iff
        resté en texte) ; le tableau et le bloc texte imbriqués rendus comme ailleurs ; « impossible » sous 3 = 0."""
        res = self.page.evaluer(r"""(() => {
          const ch = [...document.querySelectorAll('#cartes .chaine')];
          const brut = e => { const c = e.cloneNode(true); c.querySelectorAll('.katex').forEach(k => k.remove()); return c.textContent; };
          return ch.map(c => ({
            parent: c.parentElement.className, classes: c.className, ordre: [...c.children].map(e => e.className),
            colonnes: [...c.querySelectorAll(':scope > .ligne')].map(l => [...l.children].map(s => s.tagName.toLowerCase() + '.' + s.className)),
            formules: [...c.querySelectorAll(':scope > .ligne > .expr')].map(e => e.querySelectorAll(':scope > .katex').length),
            liens: [...c.querySelectorAll(':scope > .ligne > .lien')].map(e => e.querySelector('annotation') ? e.querySelector('annotation').textContent : ''),
            gauche: [...c.querySelectorAll(':scope > .ligne > .gauche')].map(e => e.querySelector('annotation') ? e.querySelector('annotation').textContent : ''),
            props: [...c.querySelectorAll(':scope > .ligne > .prop')].map(e => e.textContent),
            pleines: [...c.querySelectorAll(':scope > .pleine')].map(p => ({texte: p.textContent.slice(0, 30), katex: p.querySelectorAll('.katex').length,
                       tableau: p.querySelectorAll('.tsigne table tr').length, etape: !!p.querySelector('.etape strong')})),
            brut: brut(c), impossible: [...c.querySelectorAll('annotation')].some(a => a.textContent.includes('\\underbrace{3 = 0}_{\\text{impossible}}')),
            vide: /undefined|\[object|NaN/.test(c.innerHTML),
          }));
        })()""")
        self.assertEqual(len(res), 4)
        gauche_grise, el, tableau = res[:3]
        for r in res:
            self.assertEqual(r["parent"], "etape")
            self.assertFalse(r["vide"], r)
            self.assertNotIn("\\(", r["brut"])
            self.assertNotIn("\\iff", r["brut"])
        # 2.9 c, membre de gauche, étiquettes grises, « impossible »
        self.assertEqual(gauche_grise["classes"], "chaine avec-gauche")
        self.assertEqual(gauche_grise["ordre"], ["ligne", "pleine", "ligne", "ligne", "ligne"])
        self.assertEqual(gauche_grise["colonnes"], [["span.gauche", "span.lien", "span.expr", "span.prop"]] * 4)
        self.assertEqual(gauche_grise["gauche"], ["48z^{2} - 216z + 243 = 0", "", "", ""])
        self.assertEqual(gauche_grise["liens"], ["\\iff"] * 4)
        self.assertEqual(gauche_grise["formules"], [1] * 4)
        self.assertEqual(gauche_grise["props"], ["ME", "", "produit nul", ""])
        self.assertTrue(gauche_grise["impossible"])
        self.assertEqual(gauche_grise["pleines"][0]["katex"], 4)
        self.assertTrue(gauche_grise["pleines"][0]["texte"].startswith("Id. rem. "))
        # 2.9 c comme Exp-log : trois colonnes, première ligne sans lien, propriétés entre parenthèses
        self.assertEqual(el["classes"], "chaine")
        self.assertEqual(el["ordre"], ["ligne", "ligne", "pleine", "ligne", "ligne", "ligne"])
        self.assertEqual(el["colonnes"], [["span.lien", "span.expr", "span.prop"]] * 5)
        self.assertEqual(el["liens"], [""] + ["\\iff"] * 4)
        self.assertEqual(el["props"], ["", "(ME)", "", "(produit nul)", ""])
        self.assertFalse(el["impossible"])
        # texte puis tableau pleine largeur avant la ligne au membre de gauche, puis un bloc texte imbriqué
        self.assertEqual(tableau["ordre"], ["pleine", "pleine", "ligne", "pleine", "ligne", "ligne"])
        self.assertEqual(tableau["gauche"], ["x^{2} - x - 42 = 0", "", ""])
        self.assertEqual([p["tableau"] for p in tableau["pleines"]], [0, 4, 0])
        self.assertEqual([p["etape"] for p in tableau["pleines"]], [False, False, True])
        self.assertTrue(tableau["pleines"][0]["texte"].startswith("On cherche deux nombres"))

    def test_textes_echappes(self):
        """Propriété et ligne pleine largeur : du texte, jamais du HTML (A4) ; le rendu l'échappe (aucune balise créée, aucun script)."""
        res = self.page.evaluer(r"""(() => {
          const c = [...document.querySelectorAll('#cartes .card')].find(c => c.textContent.includes('Échappement'));
          return {img: c.querySelectorAll('img').length, injecte: window.__injecte || 0,
                  prop: c.querySelector('.prop').textContent, pleine: c.querySelector('.pleine').textContent};
        })()""")
        self.assertEqual(res, {"img": 0, "injecte": 0, "prop": "a < b & c",
                               "pleine": '<img src="x" onerror="window.__injecte = 1"> &amp; 1 < 2'})

    def test_largeurs_et_theme_sombre(self):
        """À 320, 360, 375, 390, 430, 768 et 1100 px, en clair et en sombre : aucune faute du balayage de test_largeurs (page qui défile,
        élément hors de l'écran, cible < 44 px, bloc insécable coupé), aucune formule ni ligne pleine largeur hors de sa carte ; textes
        de la couleur du thème (pas de couleur écrite en dur) ; aucune erreur de console."""
        for sombre in (False, True):
            for w in LARGEURS:
                with self.subTest(largeur=w, sombre=sombre):
                    self.page.taille(w, 800, sombre=sombre)
                    try:
                        self.assertEqual(self.page.evaluer(JS_MESURE), [])
                        self.assertEqual(self.page.evaluer(JS_HORS_CARTE), [])
                        for ch in self.page.evaluer(JS_CHAINES):
                            self.assertNotEqual(ch["fg"], ch["fond"])
                            for l in ch["lignes"]:
                                self.assertEqual(l["expr"]["couleur"], ch["fg"])
                            for p in ch["pleines"]:
                                self.assertEqual(p["couleur"], ch["fg"])
                    finally:
                        self.page.taille(1100, 800)
        self.assertEqual(erreurs_a_signaler(self.page), [])

    # ---------- avec le CSS .chaine commun (B4) ----------
    @xfail_b4("colonnes de la grille .chaine")
    def test_colonnes_alignees_avant_et_apres_la_ligne_pleine(self):
        """Écran large (1100 px) : une seule grille ; les ⇔ alignés (même bord droit de la colonne .lien), les expressions alignées (même
        bord gauche), les propriétés alignées, avant comme après la ligne pleine largeur ; le membre de gauche avant le premier ⇔ ; la
        ligne pleine largeur occupe toute la largeur de la chaîne, entre les lignes qui l'entourent."""
        for ch in self.mesurer(1100):
            lignes = ch["lignes"]
            self.assertTrue(egaux([l["lien"]["d"] for l in lignes]), lignes)
            self.assertTrue(egaux([l["expr"]["g"] for l in lignes]), lignes)
            self.assertTrue(egaux([l["prop"]["g"] for l in lignes]), lignes)
            for l in lignes:
                self.assertGreaterEqual(l["expr"]["g"], l["lien"]["d"] - 1)
                self.assertGreaterEqual(l["prop"]["g"], l["expr"]["d"] - 1)
                self.assertTrue(l["lien"]["h"] < l["expr"]["b"] and l["lien"]["b"] > l["expr"]["h"], l)   # même rangée (lignes de base)
                if l["gauche"]:
                    self.assertLessEqual(l["gauche"]["d"], l["lien"]["g"] + 1)
            for p in ch["pleines"]:
                self.assertAlmostEqual(p["g"], ch["chaine"]["g"], delta=1)
                self.assertAlmostEqual(p["d"], ch["chaine"]["d"], delta=1)

    @xfail_b4("repli de la grille .chaine sur un conteneur étroit")
    def test_repli_sur_ecran_etroit(self):
        """Écran étroit (360 et 390 px) : deux colonnes, la propriété sous l'expression (même bord gauche), les ⇔ toujours alignés, le membre
        de gauche seul sur sa ligne au-dessus du premier ⇔ ; la chaîne tient dans sa carte sans défiler. (Sans sous-test : un xfail strict
        doit échouer en entier.)"""
        fautes = []
        for w in (360, 390):
            for ch in self.mesurer(w):
                lignes, ou = ch["lignes"], (w, ch["ordre"])
                if ch["defile"]:
                    fautes.append((ou, "défile"))
                if not egaux([l["lien"]["d"] for l in lignes]) or not egaux([l["expr"]["g"] for l in lignes]):
                    fautes.append((ou, "⇔ ou expressions non alignés"))
                for l in lignes:
                    if not l["prop"]["vide"] and (l["prop"]["h"] < l["expr"]["b"] - 1 or abs(l["prop"]["g"] - l["expr"]["g"]) > 1):
                        fautes.append((ou, "propriété pas sous l'expression", l))
                    if l["gauche"] and not l["gauche"]["vide"] and l["gauche"]["b"] > l["lien"]["h"] + 1:
                        fautes.append((ou, "membre de gauche pas au-dessus du ⇔", l))
        self.assertEqual(fautes, [])

    @xfail_b4("couleur de la colonne .prop")
    def test_etiquette_grise(self):
        """La propriété (étiquette grise sans parenthèses, ou entre parenthèses comme Exp-log) est grise (--muted du thème) et plus petite
        que l'expression, en clair et en sombre. (Sans sous-test : un xfail strict doit échouer en entier.)"""
        fautes = []
        for sombre in (False, True):
            for ch in self.mesurer(1100, sombre=sombre):
                for l in ch["lignes"]:
                    if not l["prop"]["vide"] and (l["prop"]["couleur"] != rgb(ch["muted"]) or l["prop"]["taille"] >= l["expr"]["taille"]):
                        fautes.append((sombre, ch["ordre"], l["prop"]))
        self.assertEqual(fautes, [])

if __name__ == "__main__":
    unittest.main()
