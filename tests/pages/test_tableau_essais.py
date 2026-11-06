"""Tableau d'essais (bloc « tableau_essais ») et valeurs trouvées encadrées (\\fbox, D29) rendus par commun/rendu.js dans Chrome (chantier
equations-2e-degre, P2a ; decisions.md D3, D4, D29, E6, § 13.3).

Sur le modèle de test_bloc_chaine.py : aucune page nouvelle (l'outil vient en P5), les cartes sont rendues dans la page d'un outil
existant (Ensemble de définition), qui charge KaTeX, commun/style.css, commun/composants.css et commun/rendu.js. Les cartes sont écrites
ici à la main, avec moteur/chaine.py et moteur/sortie.py, d'après les exemples rédigés de decisions.md (§ 7) ; les tableaux S-P sont
tirés de `second_degre.essais_sp` (calcul de P1), leurs nombres écrits par `nombres.exact` (A5). Ce n'est pas la rédaction de l'outil
(P2b) : seulement l'affichage commun.

Cartes : 2.10 a (S-P, ✓ à la 4e ligne) ; S-P en échec puis la formule (x² + 4x − 1, Δ encadré) ; x² + 4 (S-P avec b = 0 en échec,
Δ < 0) ; une étiquette grise « Id. rem. A² − B² avec ⟦A = 4z, B = 9⟧ » ; produits nuls à trois facteurs (2.11 h, avec r et △ encadrés ;
Az 4.1 d), coupés seulement après « ou » (`coupure_ou`). Contrôles : structure du tableau (groupes, ✓ seulement sur la ligne ok, aucune
✓ en échec), bordures et fonds calculés = --good et --ok-soft du thème (clair et sombre), encadrés insécables, aucune faute du balayage
des largeurs (320 à 1100 px), rien hors de sa carte, aucune erreur de console."""
import json
import os
import sys
import unittest
from fractions import Fraction as F

sys.path.insert(0, os.path.dirname(__file__))
from navigateur import Navigateur  # noqa: E402
from rendu import attendre_pret  # noqa: E402  (met aussi tests/python sur le chemin)
from test_bloc_chaine import JS_RENDRE, rgb  # noqa: E402
from test_largeurs import JS_MESURE, LARGEURS, erreurs_a_signaler  # noqa: E402
import moteurs  # noqa: E402,F401  (chemins des moteurs)
import sortie as so  # noqa: E402
from chaine import Chaine, Eq, LigneTexte, Ou, bloc_chaine, bloc_rangees, rangees_chaine  # noqa: E402
from expr import LEXIQUE_COMMUN, Nb, Var, lire_membres  # noqa: E402
from nombres import exact  # noqa: E402
from second_degre import essais_sp  # noqa: E402

PAGE = "ensemble-definition"                 # n'importe quelle page d'outil qui charge KaTeX et commun/rendu.js
OPTIONS = {"etiquette_grise": True, "impossible": True, "coupure_ou": True}


def eq(texte):
    g, d = lire_membres(texte, LEXIQUE_COMMUN)
    return Eq(g, d)


def solutions(x, *valeurs):
    return Ou([Eq(Var(x), Nb(v)) for v in valeurs])


def tableau_sp(b, c):
    """Le tableau S-P de x² + bx + c (E6) : produit = c | somme, lignes de `second_degre.essais_sp`, ✓ sur la ligne qui aboutit."""
    e = essais_sp(b, c)
    assert not e["trop"]
    return so.tableau_essais([(r"produit \(= " + exact(c) + r"\)", 2), ("somme", 1)],
                             [[exact(u), exact(v), exact(s)] for u, v, s in e["lignes"]], ok=e["ok"])


def on_cherche(b, c):
    return rf"On cherche deux nombres dont le produit vaut \({exact(c)}\) et la somme vaut \({exact(b)}\) :"


SP = r"Pas de ME, pas d'Id. rem. ; le trinôme est unitaire (\(a = 1\)) : S-P."
FORMULE = "Aucun couple ne convient : on utilise la formule."


def carte_2_10_a():
    """2.10 a : phrase de choix et tableau d'abord, puis la chaîne dont le membre de gauche est l'équation (§ 13.3)."""
    c = Chaine([eq("x^2 - 5x - 36 = 0"), eq("(x + 4)(x - 9) = 0")], ["⇔"], [None])
    c.ajouter(Ou([eq("x + 4 = 0"), eq("x - 9 = 0")]), "⇔", "produit nul")
    c.ajouter(solutions("x", -4, 9), "⇔")
    rangees = [LigneTexte(SP), LigneTexte(on_cherche(-5, -36)), LigneTexte(tableau_sp(-5, -36))] + rangees_chaine(c, **OPTIONS)
    return so.carte("2.10 a", [bloc_rangees(rangees, membre_gauche=True), so.resultat_lim(r"S = \{-4\,;\,9\}")])


def carte_sp_en_echec():
    """x² + 4x − 1 = 0 (decisions.md § 7) : tableau complet sans ✓, puis la formule, rangées sans lien, valeur de Δ encadrée."""
    rangees = [LigneTexte(SP), LigneTexte(on_cherche(4, -1)), LigneTexte(tableau_sp(4, -1)), LigneTexte(FORMULE),
               ("", r"\Delta = b^{2} - 4ac = 4^{2} - 4 \cdot 1 \cdot (-1) = 16 + 4 = \fbox{$20$}", None),
               ("", r"\Delta > 0 \text{ : deux solutions.} \quad \sqrt{\Delta} = \sqrt{20} = 2\sqrt{5}", None),
               ("", r"x_{1} = \frac{-b - \sqrt{\Delta}}{2a} = \frac{-4 - 2\sqrt{5}}{2} = -2 - \sqrt{5}", None),
               ("", r"x_{2} = \frac{-b + \sqrt{\Delta}}{2a} = \frac{-4 + 2\sqrt{5}}{2} = -2 + \sqrt{5}", None)]
    return so.carte("S-P en échec", [bloc_rangees(rangees, membre_gauche=True),
                                     so.resultat_lim(r"S = \{-2 - \sqrt{5}\,;\,-2 + \sqrt{5}\}"),
                                     so.texte(r"soit \(x_{1} \approx -4{,}236\) et \(x_{2} \approx 0{,}236\)")])


def carte_x2_plus_4():
    """x² + 4 = 0 (§ 6) : S-P avec b = 0 (deux nombres positifs), tableau en échec, puis Δ < 0."""
    rangees = [LigneTexte(SP), LigneTexte(on_cherche(0, 4)), LigneTexte(tableau_sp(0, 4)), LigneTexte(FORMULE),
               ("", r"\Delta = b^{2} - 4ac = 0^{2} - 4 \cdot 1 \cdot 4 = \fbox{$-16$}", None),
               LigneTexte(r"\(\Delta < 0\) : l'équation n'a aucune solution réelle.")]
    return so.carte("x² + 4", [bloc_rangees(rangees, membre_gauche=True), so.resultat_lim(r"S = \varnothing")])


def carte_etiquette():
    """Étiquette grise d'une Id. rem. avec A et B encadrés (D29 : « avec ⟦A = 4z, B = 9⟧ »)."""
    c = Chaine([eq("16z^2 - 81 = 0"), eq("(4z + 9)(4z - 9) = 0")], ["⇔"],
               [r"Id. rem. \(A^{2} - B^{2}\) avec \(\fbox{$A = 4z,\ B = 9$}\)"])
    c.ajouter(Ou([eq("4z + 9 = 0"), eq("4z - 9 = 0")]), "⇔", "produit nul")
    c.ajouter(solutions("z", F(-9, 4), F(9, 4)), "⇔")
    return so.carte("Étiquette", [bloc_chaine(c, membre_gauche=True, **OPTIONS), so.resultat_lim(r"S = \{-\frac{9}{4}\,;\,\frac{9}{4}\}")])


def carte_2_11_h():
    """2.11 h (exemple cible du § 7) : tâtonnement, r et △ encadrés, produit nul à trois facteurs dont « 2 = 0 impossible »."""
    c = Chaine([eq("4x^2 + 2x = 56"), eq("4x^2 + 2x - 56 = 0")], ["⇔"], [None])
    c.ajouter(eq("2(2x^2 + x - 28) = 0"), "⇔", "ME")
    c.ajouter(eq("2(x + 4)(2x - 7) = 0"), "⇔", texte_avant=[
        r"Le trinôme \(2x^{2} + x - 28\) n'est pas unitaire : tâtonnement.",
        r"\(\fbox{$x = -4$}\) est solution de \(2x^{2} + x - 28 = 0\), car \(2 \cdot (-4)^{2} - 4 - 28 = 32 - 4 - 28 = 0\).",
        r"Donc \(2x^{2} + x - 28 = (x + 4)(2x + \triangle)\) avec \(4 \cdot \triangle = -28\), donc \(\fbox{$\triangle = -7$}\)."])
    c.ajouter(Ou([Eq(Nb(2), Nb(0)), eq("x + 4 = 0"), eq("2x - 7 = 0")]), "⇔", "produit nul")
    c.ajouter(solutions("x", -4, F(7, 2)), "⇔")
    return so.carte("2.11 h", [bloc_chaine(c, membre_gauche=True, **OPTIONS), so.resultat_lim(r"S = \{-4\,;\,\frac{7}{2}\}")])


def carte_az_4_1_d():
    """Az 4.1 d : produit déjà factorisé, trois facteurs non constants (la ligne la plus longue du produit nul)."""
    c = Chaine([eq("(x - 1)(2 - x)(5 - 3x) = 0"), Ou([eq("x - 1 = 0"), eq("2 - x = 0"), eq("5 - 3x = 0")])], ["⇔"], ["produit nul"])
    c.ajouter(solutions("x", 1, 2, F(5, 3)), "⇔")
    return so.carte("Az 4.1 d", [bloc_chaine(c, membre_gauche=True, **OPTIONS), so.resultat_lim(r"S = \{1\,;\,\frac{5}{3}\,;\,2\}")])


def cartes():
    return [carte_2_10_a(), carte_sp_en_echec(), carte_x2_plus_4(), carte_etiquette(), carte_2_11_h(), carte_az_4_1_d()]


# Tableaux d'essais : en-tête (texte, colspan, filet), lignes (classe, cases, ✓), couleurs calculées de la ligne ok.
JS_ESSAIS = r"""
(async () => {
  await new Promise(r => setTimeout(r, 150));
  const st = e => getComputedStyle(e);
  return [...document.querySelectorAll('#cartes .essais')].map(t => ({
    carte: t.closest('.card').querySelector('h3').textContent,
    dans_chaine: !!t.closest('.chaine > .pleine'),
    entete: [...t.querySelectorAll('thead th')].map(th => ({texte: th.textContent, colspan: th.colSpan, groupe: th.classList.contains('groupe'),
                                                         filet: st(th).borderLeftColor, bas: st(th).borderBottomColor})),
    lignes: [...t.querySelectorAll('tbody tr')].map(tr => ({
      ok: tr.classList.contains('ok'),
      cases: [...tr.children].map(td => td.querySelector('annotation') ? td.querySelector('annotation').textContent : td.textContent),
      katex: [...tr.children].filter(td => td.querySelector('.katex')).length,
      coches: (tr.textContent.match(/✓/g) || []).length,
      haut: [...tr.children].map(td => st(td).borderTopColor), bas: [...tr.children].map(td => st(td).borderBottomColor),
      fond: [...tr.children].map(td => st(td).backgroundColor),
      gauche: st(tr.firstElementChild).borderLeftColor, droite: st(tr.lastElementChild).borderRightColor,
      filets: [...tr.children].map(td => td.classList.contains('groupe') ? st(td).borderLeftColor : null),
    })),
    brut: (() => { const c = t.cloneNode(true); c.querySelectorAll('.katex').forEach(k => k.remove()); return c.textContent; })(),
    good: st(document.documentElement).getPropertyValue('--good').trim(),
    soft: st(document.documentElement).getPropertyValue('--ok-soft').trim(),
    border: st(document.documentElement).getPropertyValue('--border').trim(),
  }));
})()
"""

# Valeurs encadrées (\fbox de KaTeX) : couleurs calculées, boîtes (une seule : jamais coupée), place dans la carte.
JS_FBOX = r"""
(async () => {
  await new Promise(r => setTimeout(r, 150));
  const st = e => getComputedStyle(e);
  return [...document.querySelectorAll('#cartes .card')].map(c => ({
    carte: c.querySelector('h3').textContent,
    boites: [...c.querySelectorAll('.katex .fbox')].map(f => {
      f.scrollIntoView({block: 'center'});
      const r = f.getBoundingClientRect(), rc = c.getBoundingClientRect(), s = st(f);
      // la valeur encadrée est visible : au centre de son contenu, l'élément du dessus est ce contenu, pas le cadre (D29)
      const pad = f.closest('.vlist').querySelector('.boxpad'), rp = pad.getBoundingClientRect();
      const dessus = document.elementFromPoint(rp.left + rp.width / 2, rp.top + rp.height / 2);
      return {bords: [s.borderTopColor, s.borderRightColor, s.borderBottomColor, s.borderLeftColor], style: s.borderTopStyle,
              largeur: parseFloat(s.borderTopWidth), fond: s.backgroundColor, rects: f.getClientRects().length, w: r.width, h: r.height,
              dedans: r.left >= rc.left - 1 && r.right <= rc.right + 1, gris: !!f.closest('.prop'),
              texte: st(f.closest('.katex')).color, visible: !!dessus && pad.contains(dessus), contenu: pad.textContent};
    }),
    good: st(document.documentElement).getPropertyValue('--good').trim(),
    soft: st(document.documentElement).getPropertyValue('--ok-soft').trim(),
  }));
})()
"""

# Lignes de produit nul (coupure après « ou ») : morceaux insécables de KaTeX (.base) de chaque expression qui contient « ou », leurs
# boîtes et le nombre de lignes occupées.
JS_OU = r"""
(async () => {
  await new Promise(r => setTimeout(r, 150));
  const out = [];
  for (const e of document.querySelectorAll('#cartes .chaine > .ligne > .expr')) {
    const a = e.querySelector('annotation');
    if (!a || !a.textContent.includes('\\text{ ou }')) continue;
    const c = e.closest('.card').getBoundingClientRect();
    const bases = [...e.querySelectorAll('.katex-html > .base')].map(b => b.getBoundingClientRect());
    out.push({carte: e.closest('.card').querySelector('h3').textContent, tex: a.textContent, n: bases.length,
              rangs: new Set(bases.map(b => Math.round(b.top))).size,
              dedans: bases.every(b => b.left >= c.left - 1 && b.right <= c.right + 1)});
  }
  return out;
})()
"""

# Formules, tableaux, résultats et lignes pleine largeur hors de leur carte (hors d'un bloc qui défile lui-même).
JS_HORS_CARTE = r"""
(async () => {
  await new Promise(r => setTimeout(r, 150));
  const out = [];
  for (const k of document.querySelectorAll('#cartes .katex, #cartes .essais, #cartes .rbox, #cartes .chaine > .pleine, #cartes .chaine')) {
    const c = k.closest('.card');
    let defile = false;
    for (let m = k.parentElement; m && m !== c; m = m.parentElement) {
      const o = getComputedStyle(m).overflowX; if (o === 'auto' || o === 'scroll') defile = true; }
    const r = k.getBoundingClientRect(), rc = c.getBoundingClientRect();
    if (!defile && r.width > 0 && (r.right > rc.right + 1 || r.left < rc.left - 1)) out.push(k.className + ' ' + k.textContent.slice(0, 40));
  }
  for (const t of document.querySelectorAll('#cartes .essais'))
    if (t.scrollWidth > t.clientWidth + 1) out.push('essais défile ' + t.textContent.slice(0, 30));
  return out;
})()
"""


def avec_largeurs(page, largeurs=LARGEURS, sombres=(False, True)):
    """Itère (largeur, sombre) en réglant la page ; la remet à 1100 px, clair, à la fin."""
    try:
        for sombre in sombres:
            for w in largeurs:
                page.taille(w, 800, sombre=sombre)
                yield w, sombre
    finally:
        page.taille(1100, 800)


class TestTableauEssais(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.nav = Navigateur().__enter__()
        cls.cartes = cartes()
        cls.page = cls.nav.ouvrir(f"{PAGE}/index.html")
        attendre_pret(cls.page)
        cls.page.taille(1100, 800)
        n = cls.page.evaluer(JS_RENDRE + "(" + json.dumps(cls.cartes) + ")")
        assert n == len(cls.cartes), n

    @classmethod
    def tearDownClass(cls):
        cls.nav.__exit__(None, None, None)

    def test_cartes_valides(self):
        """Les cartes passent `sortie.valider` ; chaque tableau est dans une chaîne (rangee_bloc), entre les lignes de texte."""
        self.assertEqual(so.valider(so.sortie_ok("x", self.cartes)), [])
        tableaux = [r["bloc"] for c in self.cartes for b in c["blocs"] if b["type"] == "chaine" for r in b["rangees"] if "bloc" in r]
        self.assertEqual([t["type"] for t in tableaux], ["tableau_essais"] * 3)

    def test_structure_des_tableaux(self):
        """En-tête « produit = c | somme » (deux groupes, filet au début du second, colonne ✓ seulement s'il y a une ligne ok) ; lignes
        de `essais_sp` dans l'ordre, cases rendues par KaTeX ; ✓ seulement sur la ligne ok (2.10 a : (4, −9 | −5)), aucune en échec."""
        res = self.page.evaluer(JS_ESSAIS)
        self.assertEqual([t["carte"] for t in res], ["2.10 a", "S-P en échec", "x² + 4"])
        a, echec, plus4 = res
        for t in res:
            self.assertTrue(t["dans_chaine"])
            self.assertNotIn("\\(", t["brut"])
            self.assertEqual([(h["colspan"], h["groupe"]) for h in t["entete"]][1:], [(2 if t is a else 1, True)])
            self.assertEqual(t["entete"][1]["texte"], "somme")
            self.assertTrue(t["entete"][0]["texte"].startswith("produit "))
            self.assertEqual(t["entete"][1]["filet"], rgb(t["border"]))
            for l in t["lignes"]:
                self.assertEqual(l["katex"], 3)
                self.assertEqual(l["filets"][2], rgb(t["border"]))         # filet au début du groupe « somme »
        self.assertEqual([l["cases"][:3] for l in a["lignes"]],
                         [["1", "-36", "-35"], ["2", "-18", "-16"], ["3", "-12", "-9"], ["4", "-9", "-5"]])
        self.assertEqual([(l["ok"], l["coches"]) for l in a["lignes"]], [(False, 0)] * 3 + [(True, 1)])
        self.assertEqual([len(l["cases"]) for l in a["lignes"]], [4] * 4)               # 3 cases + la colonne ✓
        self.assertEqual(a["lignes"][3]["cases"][3], "✓")
        self.assertEqual([l["cases"] for l in echec["lignes"]], [["-1", "1", "0"]])
        self.assertEqual([l["cases"] for l in plus4["lignes"]], [["1", "4", "5"], ["2", "2", "4"]])
        for t in (echec, plus4):
            self.assertEqual(t["entete"][1]["colspan"], 1)
            self.assertFalse(any(l["ok"] or l["coches"] for l in t["lignes"]))

    def test_ligne_ok_encadree(self):
        """La ligne ok : bordure calculée = --good (haut, bas, gauche de la première case, droite de la dernière), fond --ok-soft, en clair
        et en sombre ; les autres lignes n'ont ni bordure verte ni fond."""
        fautes = []
        for w, sombre in avec_largeurs(self.page, (390, 1100)):
            for t in self.page.evaluer(JS_ESSAIS):
                good, soft = rgb(t["good"]), rgb(t["soft"])
                for i, l in enumerate(t["lignes"]):
                    ou = (w, sombre, t["carte"], i)
                    if l["ok"]:
                        if set(l["haut"]) != {good} or set(l["bas"]) != {good} or l["gauche"] != good or l["droite"] != good:
                            fautes.append((ou, "bordure", l))
                        if set(l["fond"]) != {soft}:
                            fautes.append((ou, "fond", l["fond"]))
                    elif good in l["haut"] + l["bas"] or soft in l["fond"]:
                        fautes.append((ou, "ligne non ok encadrée", l))
        self.assertEqual(fautes, [])

    def test_valeurs_encadrees(self):
        """Chaque \\fbox du TeX est une boîte de KaTeX : bordure pleine des quatre côtés = --good (même dans l'étiquette grise, où
        « .katex * » la mettrait grise), fond --ok-soft, en clair et en sombre ; la valeur reste visible au-dessus du fond (le cadre de
        \\fbox suit le contenu dans le HTML de KaTeX) ; une seule boîte (jamais coupée), dans sa carte, de 320 à 1100 px."""
        attendu = {c["titre"]: json.dumps(c).count("\\\\fbox") for c in self.cartes}
        self.assertEqual(sum(attendu.values()), 5)
        fautes = []
        for w, sombre in avec_largeurs(self.page):
            for c in self.page.evaluer(JS_FBOX):
                good, soft = rgb(c["good"]), rgb(c["soft"])
                ou = (w, sombre, c["carte"])
                if len(c["boites"]) != attendu[c["carte"]]:
                    fautes.append((ou, "nombre", len(c["boites"])))
                for f in c["boites"]:
                    if set(f["bords"]) != {good} or f["style"] != "solid" or f["largeur"] <= 0 or f["fond"] != soft:
                        fautes.append((ou, "couleurs", f))
                    if f["rects"] != 1 or not f["dedans"] or f["w"] <= 0 or f["h"] <= 0:
                        fautes.append((ou, "coupée ou hors de la carte", f))
                    if not f["visible"] or not f["contenu"].strip():
                        fautes.append((ou, "valeur cachée par le cadre", f))
        self.assertEqual(fautes, [])
        gris = [f for c in self.page.evaluer(JS_FBOX) for f in c["boites"] if f["gris"]]
        self.assertEqual(len(gris), 1)                                                 # l'étiquette « avec ⟦A = 4z, B = 9⟧ »
        self.assertNotEqual(gris[0]["texte"], gris[0]["bords"][0])                     # texte gris, cadre vert

    def test_coupure_seulement_apres_ou(self):
        """Produits nuls (coupure_ou) : un morceau insécable de KaTeX par équation du « ou » (la ligne ne peut se couper qu'après un
        « ou »), tous dans la carte ; à 320 px, la ligne de trois facteurs d'Az 4.1 d passe sur plusieurs lignes."""
        fautes, rangs_320 = [], {}
        for w, sombre in avec_largeurs(self.page, sombres=(False,)):
            for l in self.page.evaluer(JS_OU):
                membres = l["tex"].count("\\text{ ou }") + 1
                if l["n"] != membres or not l["dedans"]:
                    fautes.append((w, l))
                if w == 320:
                    rangs_320[l["tex"]] = l["rangs"]
        self.assertEqual(fautes, [])
        self.assertEqual(len(rangs_320), 8)
        self.assertGreater(rangs_320[r"{x - 1 = 0} \text{ ou } \allowbreak {2 - x = 0} \text{ ou } \allowbreak {5 - 3x = 0}"], 1)

    def test_largeurs_et_theme_sombre(self):
        """À 320, 360, 375, 390, 430, 768 et 1100 px, en clair et en sombre : aucune faute du balayage de test_largeurs (page qui défile,
        élément hors de l'écran, cible < 44 px, bloc insécable coupé) ; aucune formule, aucun tableau, aucun résultat ni aucune ligne
        pleine largeur hors de sa carte ; aucun tableau qui défile ; aucune erreur de console."""
        for w, sombre in avec_largeurs(self.page):
            with self.subTest(largeur=w, sombre=sombre):
                self.assertEqual(self.page.evaluer(JS_MESURE), [])
                self.assertEqual(self.page.evaluer(JS_HORS_CARTE), [])
        self.assertEqual(erreurs_a_signaler(self.page), [])


if __name__ == "__main__":
    unittest.main()
