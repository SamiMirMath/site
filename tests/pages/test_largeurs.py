"""Chantier « Mise en page fluide » (30.10.2026) — balayage des largeurs de TOUS les outils du registre (sauf l'accueil).

Pour chaque outil : ouvrir la page, lancer un exemple, puis vérifier à 320, 360, 375, 390, 430, 768 et 1100 px :
  debordement        la page défile horizontalement ;
  hors-ecran         un bouton, champ, liste, résumé ou onglet visible sort de l'écran (hors d'un bloc qui défile lui-même) ;
  cible-44           (≤ 430 px) un de ces éléments a moins de 44 px de haut ;
  insecable-coupe    un bloc `.insecable` est coupé (éléments sur deux lignes, ou bloc plus large que son conteneur ou que l'écran).
Le même parcours vérifie qu'aucune exception non attrapée ni aucune erreur de console ou de journal n'a eu lieu (passage des pages en module ES).

« xfail » au nom de l'outil : le tableau CONNUS liste les échecs actuels, outil par outil. Il est STRICT : un échec absent du tableau fait
échouer la suite (nouvel échec), et une entrée qui ne se produit plus la fait échouer aussi (« corrigé : retirer de CONNUS »).
BALAYAGE_RAPPORT=<fichier> : n'affirme rien et ajoute au fichier une ligne JSON par outil (toutes les fautes, avec l'état et l'élément)."""
import json
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(__file__))
from navigateur import Navigateur
from rendu import OUTIL_M, OUTILS, attendre_pret, page_de
import outils_du_site  # noqa: E402  (tests/python est sur le chemin : rendu.py l'y met)

LARGEURS = (320, 360, 375, 390, 430, 768, 1100)
TOUS = outils_du_site.outils()          # tous les outils du registre (F3) ; méthodes test_balayage_* : test_donnees_des_pages.py
CHOISIS = [o for o in os.environ.get("OUTILS", "").split(",") if o] or TOUS

# Échecs connus : {outil: {critère: [largeurs]}}. Vide depuis la fin du chantier mise-en-page-fluide (rapport initial :
# docs/chantiers/mise-en-page-fluide/suivi.md) et doit le rester (CLAUDE.md) ; une entrée corrigée qui y resterait fait échouer la suite.
CONNUS = {}

JS_MESURE = r"""
(async () => {
  await new Promise(r => setTimeout(r, 150));
  const L = innerWidth, fautes = [];
  const nom = n => {
    const t = (n.getAttribute('aria-label') || n.textContent || n.value || '').trim().replace(/\s+/g, ' ').slice(0, 28);
    const c = typeof n.className === 'string' && n.className.trim() ? '.' + n.className.trim().split(/\s+/).join('.') : '';
    return (n.tagName.toLowerCase() + (n.id ? '#' + n.id : '') + c + (t ? ' « ' + t + ' »' : '')).slice(0, 110);
  };
  const visible = n => { const s = getComputedStyle(n); if (s.visibility === 'hidden' || s.display === 'none') return false;
                         const r = n.getBoundingClientRect(); return r.width > 0 && r.height > 0; };
  const defile = n => { for (let m = n.parentElement; m; m = m.parentElement) { const o = getComputedStyle(m).overflowX; if (o === 'auto' || o === 'scroll') return true; } return false; };
  if (document.documentElement.scrollWidth > L)
    fautes.push({critere: 'debordement', cible: 'page', detail: document.documentElement.scrollWidth + ' > ' + L});
  const interactifs = 'button, input:not([type=hidden]), select, textarea, summary, [role=tab]';
  for (const n of document.querySelectorAll(interactifs)) {
    if (!visible(n) || n.closest('.imprime-seulement, .katex')) continue;
    const cible = (n.matches('input[type=checkbox], input[type=radio]') && n.closest('label')) || n;      // case à cocher : l'étiquette est la cible
    const r = cible.getBoundingClientRect();
    if (!defile(n) && (r.left < -1 || r.right > L + 1))
      fautes.push({critere: 'hors-ecran', cible: nom(n), detail: Math.round(r.left) + '…' + Math.round(r.right) + ' sur ' + L});
    if (L <= 430 && r.height < 43.9)
      fautes.push({critere: 'cible-44', cible: nom(n), detail: Math.round(r.height * 10) / 10 + ' px'});
  }
  for (const n of document.querySelectorAll('.insecable')) {
    if (!visible(n)) continue;
    const r = n.getBoundingClientRect(), enfants = [...n.children].map(c => c.getBoundingClientRect()).filter(e => e.width > 0);
    const surDeuxLignes = enfants.some(a => enfants.some(b => a.top >= b.bottom - 1));
    const p = n.parentElement;
    const trop = n.scrollWidth > n.clientWidth + 1 || r.right > L + 1 || r.left < -1 || (!defile(n) && r.width > p.clientWidth + 1 && p.clientWidth > 0);
    if (surDeuxLignes || trop)
      fautes.push({critere: 'insecable-coupe', cible: nom(n), detail: (surDeuxLignes ? 'sur deux lignes' : 'bloc ' + Math.round(r.width) + ' px, conteneur ' + p.clientWidth + ' px, écran ' + L)});
  }
  return fautes;
})()
"""


# Tableaux u, v / u′, v′ visibles : débordement de la carte ou de l'écran, colonnes côte à côte (cote), lignes alignées si côte à côte ou
# colonne v sous la colonne u si empilées (aligne), u au-dessus de u′ (ordre).
JS_UV = r"""
(async () => {
  await new Promise(r => setTimeout(r, 150));
  return [...document.querySelectorAll('#cartes .uv')].filter(u => u.getBoundingClientRect().width > 0).map(u => {
    const r = u.getBoundingClientRect(), carte = u.closest('.card').getBoundingClientRect();
    const cols = [...u.children].map(c => [...c.children].map(d => d.getBoundingClientRect()));
    const cote = Math.abs(cols[0][0].top - cols[1][0].top) < 1;
    return {deborde: r.right > carte.right + 1 || r.left < carte.left - 1 || r.right > innerWidth + 1, cote,
            aligne: cote ? Math.abs(cols[0][1].top - cols[1][1].top) < 1 : cols[1][0].top >= cols[0][1].bottom - 1,
            ordre: cols[0][0].bottom <= cols[0][1].top + 1 && cols[1][0].bottom <= cols[1][1].top + 1};
  });
})()
"""


def erreurs_a_signaler(page):
    """Erreurs de la page, sans le bruit de ressources extérieures (compteur, polices…) ni l'icône de l'onglet."""
    return [e for e in page.erreurs if "favicon" not in e
            and not (e.startswith("journal : ") and "(http" in e and "127.0.0.1" not in e)]


class TestLargeurs(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.nav = Navigateur().__enter__()

    @classmethod
    def tearDownClass(cls):
        cls.nav.__exit__(None, None, None)

    # ---------- mesures ----------
    def balayer(self, page, etat, fautes):
        """Mesure l'état courant de la page à chaque largeur ; ajoute les fautes à `fautes`."""
        try:
            for w in LARGEURS:
                page.taille(w, 800)
                for f in page.evaluer(JS_MESURE):
                    fautes.append({**f, "largeur": w, "etat": etat})
        finally:
            page.taille(1100, 800)

    def conclure(self, nom, page, fautes):
        """Compare les fautes au tableau CONNUS (strict), puis vérifie la console."""
        if os.environ.get("BALAYAGE_RAPPORT"):
            with open(os.environ["BALAYAGE_RAPPORT"], "a", encoding="utf-8") as f:
                f.write(json.dumps({"outil": nom, "fautes": fautes, "erreurs": erreurs_a_signaler(page)}, ensure_ascii=False) + "\n")
            return
        observe = {}
        for f in fautes:
            observe.setdefault(f["critere"], set()).add(f["largeur"])
        connu = {c: set(ws) for c, ws in CONNUS.get(nom, {}).items()}
        nouveaux = {c: sorted(ws - connu.get(c, set())) for c, ws in observe.items() if ws - connu.get(c, set())}
        corriges = {c: sorted(ws - observe.get(c, set())) for c, ws in connu.items() if ws - observe.get(c, set())}
        with self.subTest(outil=nom, controle="nouvel échec"):
            exemples = [f"{f['critere']} {f['largeur']} px [{f['etat']}] {f['cible']} ({f['detail']})"
                        for f in fautes if f["largeur"] in nouveaux.get(f["critere"], [])]
            self.assertEqual(nouveaux, {}, f"{nom} : nouvel échec (largeurs par critère) ; premiers éléments :\n  " + "\n  ".join(exemples[:10]))
        with self.subTest(outil=nom, controle="CONNUS exact"):
            self.assertEqual(corriges, {}, f"{nom} : corrigé, retirer de CONNUS : {corriges}")
        with self.subTest(outil=nom, controle="console"):
            self.assertEqual(erreurs_a_signaler(page), [], f"{nom} : exception ou erreur de console")

    # ---------- outils à cartes (commun/outil.js) ----------
    def balayage_outil_a_cartes(self, outil):
        if outil.replace("-M", "") not in CHOISIS:
            self.skipTest("hors de OUTILS")
        dossier, requete = page_de(outil)
        page = self.nav.ouvrir(f"{dossier}/index.html{requete}")
        attendre_pret(page)
        page.taille(1100, 800)
        page.evaluer("document.querySelector('#exemples button[data-ex]').click()")
        page.attendre("document.querySelector('#cartes').children.length > 0 && !document.querySelector('#calculer').disabled", 120)
        fautes = []
        self.balayer(page, "première carte", fautes)               # le bouton « Étape suivante » flottant est visible
        page.evaluer("document.querySelector('#tout') && !document.querySelector('#tout').disabled && document.querySelector('#tout').click()")
        self.balayer(page, "corrigé complet", fautes)
        self.conclure(outil, page, fautes)

    # ---------- tableau u, v / u′, v′ (D8) et sous-carte « Dérivée de l'exposant » (D7), chantier étude complète P7a ----------
    def test_tableau_uv_et_derivee_de_l_exposant(self):
        """Une saisie dont le tableau u/v est large (Dérivée) et Ex7 (Étude complète : sous-carte et tableau dans la sous-carte) : aucune
        faute du balayage à aucune largeur ; chaque tableau reste dans sa carte ; colonnes côte à côte avec les lignes u | v et u′ | v′
        alignées, ou empilées dans l'ordre u, u′, v, v′ ; côte à côte à 1100 px, empilées à 320 px pour le tableau large."""
        cas = {"derivee-variations": ("(x^3+2x)^4*e^x", True), "etude-complete": ("e^((x^2+x-2)/(6x-12))", False)}
        for outil, (entree, empile_a_320) in cas.items():
            if outil not in CHOISIS:
                continue
            with self.subTest(outil=outil):
                dossier, requete = page_de(outil)
                page = self.nav.ouvrir(f"{dossier}/index.html{requete}")
                attendre_pret(page)
                page.taille(1100, 800)
                page.evaluer(f"document.querySelector('#entree').value = {json.dumps(entree)}; document.querySelector('#calculer').click()")
                page.attendre("document.querySelector('#cartes').children.length > 0 && !document.querySelector('#calculer').disabled", 120)
                page.evaluer("document.querySelector('#tout') && !document.querySelector('#tout').disabled && document.querySelector('#tout').click()")
                fautes = []
                self.balayer(page, "corrigé complet : " + entree, fautes)
                self.assertEqual(fautes, [], fautes[:5])
                mesures = {}
                try:
                    for w in LARGEURS:
                        page.taille(w, 800)
                        mesures[w] = page.evaluer(JS_UV)
                finally:
                    page.taille(1100, 800)
                for w, tableaux in mesures.items():
                    self.assertTrue(tableaux, f"aucun tableau u/v visible à {w} px")
                    for t in tableaux:
                        with self.subTest(largeur=w):
                            self.assertFalse(t["deborde"], t)
                            self.assertTrue(t["aligne"] and t["ordre"], t)
                self.assertTrue(all(t["cote"] for t in mesures[1100]), mesures[1100])
                if empile_a_320:
                    self.assertTrue(any(not t["cote"] for t in mesures[320]), mesures[320])
                if outil == "etude-complete":
                    self.assertTrue(page.evaluer("[...document.querySelectorAll('#cartes .sous-t')].some(t => t.textContent === \"Dérivée de l'exposant\")"))
                self.assertEqual(erreurs_a_signaler(page), [])

    # ---------- valeurs des extremums dans la ligne f(x) du tableau de variations (D10), chantier étude complète P7b ----------
    def test_tableau_de_variations_avec_valeurs(self):
        """Dérivée ((x² − 1)/(x − 3) : 6 − 4√2 et 4√2 + 6) et Étude complète (Ex7 : e^{1/6}, e^{3/2} avec les limites ; d : quatre
        limites et e^{−1/2}) : aucune faute du balayage à aucune largeur ; chaque tableau de variations reste dans sa carte (il défile
        lui-même s'il est plus large : `.tsigne`) ; chaque valeur d'extremum est une formule dans une case de la ligne f(x)."""
        cas = {"derivee-variations": [("(x^2-1)/(x-3)", 2)], "etude-complete": [("e^((x^2+x-2)/(6x-12))", 2), ("e^(2/(x^2-4))", 1)]}
        js = r"""
        (async () => {
          await new Promise(r => setTimeout(r, 150));
          return [...document.querySelectorAll('#cartes .tsigne')].filter(t => t.getBoundingClientRect().width > 0
                     && t.querySelector('tr.variation')).map(t => {
            const r = t.getBoundingClientRect(), carte = t.closest('.card').getBoundingClientRect();
            return {deborde: r.right > carte.right + 1 || r.left < carte.left - 1 || r.right > innerWidth + 1,
                    defile: t.scrollWidth > t.clientWidth + 1,
                    valeurs: [...t.querySelectorAll('tr.variation td.pt')].filter(c => c.querySelector('.katex')).length};
          });
        })()"""
        for outil, entrees in cas.items():
            if outil not in CHOISIS:
                continue
            for entree, n_valeurs in entrees:
                with self.subTest(outil=outil, entree=entree):
                    dossier, requete = page_de(outil)
                    page = self.nav.ouvrir(f"{dossier}/index.html{requete}")
                    attendre_pret(page)
                    page.taille(1100, 800)
                    page.evaluer(f"document.querySelector('#entree').value = {json.dumps(entree)}; document.querySelector('#calculer').click()")
                    page.attendre("document.querySelector('#cartes').children.length > 0 && !document.querySelector('#calculer').disabled", 120)
                    page.evaluer("document.querySelector('#tout') && !document.querySelector('#tout').disabled && document.querySelector('#tout').click()")
                    fautes = []
                    self.balayer(page, "corrigé complet : " + entree, fautes)
                    self.assertEqual(fautes, [], fautes[:5])
                    mesures = {}
                    try:
                        for w in LARGEURS:
                            page.taille(w, 800)
                            mesures[w] = page.evaluer(js)
                    finally:
                        page.taille(1100, 800)
                    if os.environ.get("BALAYAGE_RAPPORT"):                 # le tableau défile-t-il, à chaque largeur ?
                        with open(os.environ["BALAYAGE_RAPPORT"], "a", encoding="utf-8") as f:
                            f.write(json.dumps({"variations": entree, "mesures": mesures}) + "\n")
                    for w, tableaux in mesures.items():
                        self.assertEqual(len(tableaux), 1, (w, tableaux))
                        self.assertFalse(tableaux[0]["deborde"], (w, tableaux))
                        self.assertEqual(tableaux[0]["valeurs"], n_valeurs, (w, tableaux))
                    self.assertEqual(erreurs_a_signaler(page), [])

    # ---------- lignes de calcul des extremums et valeurs approchées dans la formule, chantier étude complète R2 (Q15, Q41) ----------
    def test_lignes_de_calcul_et_valeurs_approchees(self):
        """Étude complète, b du corrigé ((x² − 6)e^{−2x} : substitution en chaîne, points avec « ≈ » dans la formule) et 1/(x² − 3x + 2)
        (condition par Somme-Produit, x₀ = 3/2) : aucune faute du balayage à aucune largeur ; aucune formule ne sort de sa carte (hors
        d'un bloc qui défile lui-même)."""
        js = r"""
        (async () => {
          await new Promise(r => setTimeout(r, 150));
          const out = [];
          for (const k of document.querySelectorAll('#cartes .katex')) {
            const c = k.closest('.card'); if (!c) continue;
            let defile = false;
            for (let m = k.parentElement; m && m !== c; m = m.parentElement) {
              const o = getComputedStyle(m).overflowX; if (o === 'auto' || o === 'scroll') defile = true; }
            const r = k.getBoundingClientRect(), rc = c.getBoundingClientRect();
            if (!defile && r.width > 0 && (r.right > rc.right + 1 || r.left < rc.left - 1)) out.push(k.textContent.slice(0, 60));
          }
          return out;
        })()"""
        if "etude-complete" not in CHOISIS:
            self.skipTest("hors de OUTILS")
        for entree in ("(x^2-6)e^(-2x)", "1/(x^2-3x+2)"):
            with self.subTest(entree=entree):
                dossier, requete = page_de("etude-complete")
                page = self.nav.ouvrir(f"{dossier}/index.html{requete}")
                attendre_pret(page)
                page.taille(1100, 800)
                page.evaluer(f"document.querySelector('#entree').value = {json.dumps(entree)}; document.querySelector('#calculer').click()")
                page.attendre("document.querySelector('#cartes').children.length > 0 && !document.querySelector('#calculer').disabled", 120)
                page.evaluer("document.querySelector('#tout') && !document.querySelector('#tout').disabled && document.querySelector('#tout').click()")
                self.assertTrue(page.evaluer(r"document.querySelector('#cartes').textContent.includes('≈')"))
                fautes = []
                self.balayer(page, "corrigé complet : " + entree, fautes)
                self.assertEqual(fautes, [], fautes[:5])
                try:
                    for w in LARGEURS:
                        page.taille(w, 800)
                        self.assertEqual(page.evaluer(js), [], w)
                finally:
                    page.taille(1100, 800)
                self.assertEqual(erreurs_a_signaler(page), [])

    # ---------- Équations du 2e degré (chantier equations-2e-degre, P5 ; decisions.md § 6) ----------
    def test_equations_2e_degre_chaque_exemple(self):
        """Chaque exemple de la page (tableau S-P, étiquettes longues d'Id. rem., cadres D29, lignes de Δ, produit nul à trois
        facteurs), chemin du cours et variante « Par la formule » : aucune faute du balayage à aucune largeur, aucune formule hors de
        sa carte (hors d'un bloc qui défile lui-même), aucune erreur de console. Le balayage commun ne lance que le premier exemple."""
        js = r"""
        (async () => {
          await new Promise(r => setTimeout(r, 150));
          const out = [];
          for (const k of document.querySelectorAll('#cartes .katex')) {
            const c = k.closest('.card'); let defile = false;
            for (let m = k.parentElement; m && m !== c; m = m.parentElement) {
              const o = getComputedStyle(m).overflowX; if (o === 'auto' || o === 'scroll') defile = true; }
            const r = k.getBoundingClientRect(), rc = c.getBoundingClientRect();
            if (!defile && r.width > 0 && (r.right > rc.right + 1 || r.left < rc.left - 1)) out.push(k.textContent.slice(0, 60));
          }
          return out;
        })()"""
        if "equations-2e-degre" not in CHOISIS:
            self.skipTest("hors de OUTILS")
        page = self.nav.ouvrir("equations-2e-degre/index.html")
        attendre_pret(page)
        exemples = page.evaluer("[...document.querySelectorAll('#exemples button[data-ex]')].map(b => b.dataset.ex)")
        self.assertEqual(len(exemples), 10)
        variantes_vues = 0
        for entree in exemples:
            page.taille(1100, 800)
            page.evaluer(f"document.querySelector('#exemples button[data-ex={json.dumps(entree)}]').click()")
            page.attendre("document.querySelector('#cartes .card') && !document.querySelector('#calculer').disabled", 120)
            cles = page.evaluer("document.querySelector('#variantes') && !document.querySelector('#variantes').hidden ? "
                                "[...document.querySelectorAll('#variantes button')].map(b => b.dataset.variante) : [null]")
            for cle in cles:
                with self.subTest(entree=entree, variante=cle):
                    if cle is not None:
                        variantes_vues += 1
                        page.evaluer(f"document.querySelector('#variantes button[data-variante={json.dumps(cle)}]').click()")
                    page.evaluer("document.querySelector('#tout') && !document.querySelector('#tout').disabled && document.querySelector('#tout').click()")
                    self.assertFalse(page.evaluer("!!document.querySelector('#cartes .err')"))
                    fautes = []
                    self.balayer(page, f"{entree} ({cle})", fautes)
                    self.assertEqual(fautes, [], fautes[:5])
                    try:
                        for w in LARGEURS:
                            page.taille(w, 800)
                            self.assertEqual(page.evaluer(js), [], w)
                    finally:
                        page.taille(1100, 800)
            if cles != [None]:
                page.evaluer("document.querySelector('#variantes button[data-variante=\"cours\"]').click()")     # le choix est gardé
        self.assertGreater(variantes_vues, 0)
        self.assertEqual(erreurs_a_signaler(page), [])

    # ---------- fonctions du corrigé (D18) et carte « Bilan de l'étude » (D20), chantier étude complète P9 ----------
    def test_corrige_et_bilan_de_l_etude(self):
        """Étude complète, Ex7 (exemple de la page) et a–d (exercices) du corrigé, corrigé complet : aucune faute du balayage à aucune
        largeur (320 à 1100 px) ; aucune formule ne sort de sa carte (hors d'un bloc qui défile lui-même) ; la carte « Bilan de
        l'étude » est visible, juste avant le graphique, et chacune de ses lignes tient dans la carte."""
        js_formules = r"""
        (async () => {
          await new Promise(r => setTimeout(r, 150));
          const out = [];
          for (const k of document.querySelectorAll('#cartes .katex')) {
            const c = k.closest('.card'); if (!c) continue;
            let defile = false;
            for (let m = k.parentElement; m && m !== c; m = m.parentElement) {
              const o = getComputedStyle(m).overflowX; if (o === 'auto' || o === 'scroll') defile = true; }
            const r = k.getBoundingClientRect(), rc = c.getBoundingClientRect();
            if (!defile && r.width > 0 && (r.right > rc.right + 1 || r.left < rc.left - 1)) out.push(k.textContent.slice(0, 60));
          }
          const cartes = [...document.querySelectorAll('#cartes > *')];
          const i = cartes.findIndex(c => (c.querySelector('h3') || {}).textContent === "Bilan de l'étude");
          const b = cartes[i];
          const lignes = b ? [...b.querySelectorAll('ul.bilan li')] : [];
          const rb = b ? b.getBoundingClientRect() : null;
          return {formules: out, bilan: i >= 0 && rb.width > 0, avant_graphique: i >= 0 && !!(cartes[i + 1] && cartes[i + 1].querySelector('canvas')),
                  lignes: lignes.length, hors: lignes.filter(l => { const r = l.getBoundingClientRect(); return r.right > rb.right + 1 || r.left < rb.left - 1; }).length};
        })()"""
        if "etude-complete" not in CHOISIS:
            self.skipTest("hors de OUTILS")
        dossier, requete = page_de("etude-complete")
        page = self.nav.ouvrir(f"{dossier}/index.html{requete}")
        attendre_pret(page)
        for entree in ("e^((x^2+x-2)/(6x-12))", "e^(-x^2)", "(x^2-6)e^(-2x)", "e^x(6-e^x)", "e^(2/(x^2-4))"):
            with self.subTest(entree=entree):
                page.taille(1100, 800)
                page.evaluer("document.querySelector('#cartes').innerHTML = ''")
                page.evaluer(f"document.querySelector('#entree').value = {json.dumps(entree)}; document.querySelector('#calculer').click()")
                page.attendre("document.querySelector('#cartes').children.length > 0 && !document.querySelector('#calculer').disabled", 120)
                page.evaluer("document.querySelector('#tout') && !document.querySelector('#tout').disabled && document.querySelector('#tout').click()")
                fautes = []
                self.balayer(page, "corrigé complet : " + entree, fautes)
                self.assertEqual(fautes, [], fautes[:5])
                try:
                    for w in LARGEURS:
                        page.taille(w, 800)
                        m = page.evaluer(js_formules)
                        self.assertEqual(m["formules"], [], (w, m))
                        self.assertTrue(m["bilan"] and m["avant_graphique"] and m["lignes"] >= 7, (w, m))
                        self.assertEqual(m["hors"], 0, (w, m))
                finally:
                    page.taille(1100, 800)
        self.assertEqual(erreurs_a_signaler(page), [])

    # ---------- simplexe (page autonome) ----------
    def clic(self, page, selecteur):
        page.evaluer(f"document.querySelector({selecteur!r}).click()")

    def balayage_simplexe(self):
        if "simplexe" not in CHOISIS:
            self.skipTest("hors de OUTILS")
        page = self.nav.ouvrir("simplexe/index.html")
        page.attendre("document.readyState === 'complete' && document.querySelector('#objRow input')", 30)
        page.taille(1100, 800)
        fautes = []

        def lancer(selecteur_exemple, application):
            self.clic(page, selecteur_exemple)
            self.clic(page, "#launch")
            self.assertEqual(page.evaluer("document.querySelector('#err').textContent"), "")
            page.attendre(f"!document.querySelector('{application}').hidden", 10)

        self.clic(page, '[data-ex="Exemple 2D"]')
        self.balayer(page, "algébrique : formulaire 2D", fautes)
        self.clic(page, '[data-ex="Exemple 3D"]')
        self.balayer(page, "algébrique : formulaire 3D", fautes)
        lancer('[data-ex="Exemple 3D"]', "#app")
        self.balayer(page, "algébrique 3D : solution", fautes)
        self.clic(page, "#editBtn")
        lancer('[data-ex="Exemple 2D"]', "#app")
        for mode, libelle in (("sol", "solution"), ("sim", "pas à pas"), ("exp", "explorer")):
            self.clic(page, f'[data-mode="{mode}"]')
            self.balayer(page, f"algébrique 2D : {libelle}", fautes)
        self.clic(page, "#editBtn")
        self.clic(page, '[data-meth="para"]')
        self.clic(page, '[data-ex="Parallèles : max"]')
        self.balayer(page, "géométrique : formulaire", fautes)
        lancer('[data-ex="Parallèles : max"]', "#appPara")
        for mode, libelle in (("sol", "solution"), ("sim", "pas à pas")):
            self.clic(page, f'[data-modep="{mode}"]')
            self.balayer(page, f"géométrique : {libelle}", fautes)
        self.conclure("simplexe", page, fautes)

    # ---------- le script de mesure lui-même ----------
    def test_la_mesure_voit_un_bloc_insecable_coupe(self):
        """Auto-test : sur un gabarit, le script signale un `.insecable` plus large que l'écran et ne signale pas un bloc qui tient."""
        if "simplexe" not in CHOISIS:
            self.skipTest("hors de OUTILS")
        page = self.nav.ouvrir("simplexe/index.html")
        page.attendre("document.readyState === 'complete' && document.querySelector('#objRow input')", 30)
        page.taille(360, 800)
        page.evaluer("""new Promise(ok => { const l = document.createElement('link'); l.rel = 'stylesheet'; l.href = '../commun/composants.css';
            l.onload = ok; l.onerror = ok; document.head.appendChild(l); })""")
        page.evaluer("""(() => { const g = document.createElement('div'); g.id = 'gabarit';
            g.innerHTML = '<div class="flux"><span class="insecable" id="petit">a b</span></div>'
              + '<div><span class="insecable" id="large"><b>' + 'm'.repeat(90) + '</b><b>y</b></span></div>';
            document.body.prepend(g); })()""")
        fautes = [f for f in page.evaluer(JS_MESURE) if f["critere"] == "insecable-coupe"]
        self.assertEqual([f["cible"].split(" ")[0] for f in fautes], ["span#large.insecable"], fautes)


def _methode(outil):
    return lambda self: self.balayage_outil_a_cartes(outil)


for _o in OUTILS + [OUTIL_M]:
    setattr(TestLargeurs, "test_balayage_" + _o.replace("-", "_"), _methode(_o))
TestLargeurs.test_balayage_simplexe = lambda self: self.balayage_simplexe()

if __name__ == "__main__":
    unittest.main()
