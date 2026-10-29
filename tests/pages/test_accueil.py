"""T22 — Accueil, tests de page (ACC-03 sans JavaScript, ACC-04 choix de filière, ACC-06 animation sobre, changement de thème).
Pas de Pyodide : chaque test ouvre l'accueil, quelques secondes en tout.

    uv run -q --no-project --python 3.12 --with sympy==1.13.3 --with websockets python -m unittest discover -s tests/pages -p test_accueil.py"""
import json
import os
import sys
import time
import unittest

sys.path.insert(0, os.path.dirname(__file__))
from navigateur import Navigateur, RACINE

with open(os.path.join(RACINE, "commun", "registre.json"), encoding="utf-8") as f:
    REGISTRE = json.load(f)
LIENS = sum(len(fs) for o in REGISTRE["outils"] for fs in o["filieres"].values())     # une carte par (outil, année, filière)

COMPTEUR_IMAGES = """window.__images = 0; (function () { var r = window.requestAnimationFrame.bind(window);
  window.requestAnimationFrame = function (cb) { window.__images++; return r(cb); }; })();"""

ANNEES_VISIBLES = """[...document.querySelectorAll('section.level')].map(s => s.offsetParent !== null && getComputedStyle(s).display !== 'none')"""
LIENS_VISIBLES = """[...document.querySelectorAll('.tool a')].filter(a => a.offsetParent !== null && getComputedStyle(a).visibility !== 'hidden').length"""


class TestAccueil(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.nav = Navigateur().__enter__()

    @classmethod
    def tearDownClass(cls):
        cls.nav.__exit__(None, None, None)

    def ouvrir(self, script_initial=None, largeur=1100, hauteur=900, sombre=False):
        page = self.nav.ouvrir("index.html", script_initial)
        page.attendre("document.readyState === 'complete'", 30)
        page.taille(largeur, hauteur, sombre=sombre)
        return page

    def test_goatcounter_la_balise_est_demandee_a_gc_zgo_at_sans_rien_envoyer_a_goatcounter(self):
        """La balise de comptage (29.10.2026) demande gc.zgo.at/count.js, que le navigateur de test sert vide (aucune requête sortante, aucune visite comptée) ;
        rien ne part vers goatcounter.com. Elle est asynchrone : la page se charge sans l'attendre."""
        intercepteur = self.nav.intercepteur
        for chemin in ("index.html", "factorisation/", "exponentielles-logarithmes/"):
            with self.subTest(page=chemin):
                avant = len(intercepteur.comptage)
                page = self.nav.ouvrir(chemin)
                page.attendre("document.readyState === 'complete'", 60)
                fin = time.time() + 15
                while len(intercepteur.comptage) == avant and time.time() < fin:
                    time.sleep(0.05)
                self.assertEqual([u.split("//", 1)[1] for u in intercepteur.comptage[avant:]], ["gc.zgo.at/count.js"])
                self.assertTrue(page.evaluer("[...document.scripts].some(s => s.hasAttribute('data-goatcounter') && s.async)"))
                self.assertEqual(page.evaluer("performance.getEntriesByType('resource').filter(r => r.name.includes('goatcounter.com')).length"), 0)
        self.assertEqual(intercepteur.fuites, [])

    def test_le_registre_donne_16_liens(self):
        """Année I : 3 (C, Ms, Mr) ; année II : 4 (simplexe en C et Mr, Exponentielles et logarithmes en Ms et Mr) ; année III : 9 (4 outils × Ms, Mr + 1 en C)
        = 16 cartes pour 7 outils distincts."""
        self.assertEqual((LIENS, len(REGISTRE["outils"])), (16, 7))

    def test_acc03_sans_javascript_tous_les_liens_sont_visibles(self):
        page = self.ouvrir()
        page.evaluer("localStorage.clear()")
        page.appel("Emulation.setScriptExecutionDisabled", value=True)
        page.appel("Page.reload")
        page.attendre("document.readyState === 'complete'", 30)
        self.assertEqual(page.evaluer("document.documentElement.hasAttribute('data-js')"), False)     # le script n'a pas tourné
        self.assertEqual(page.evaluer(LIENS_VISIBLES), LIENS)
        self.assertEqual(page.evaluer("document.querySelector('#gate').offsetParent"), None)           # la porte (boutons sans effet) est cachée
        self.assertEqual(page.evaluer(ANNEES_VISIBLES), [True, True, True])
        hrefs = page.evaluer("[...document.querySelectorAll('.tool a')].map(a => a.getAttribute('href'))")
        attendus = {o["chemin"] + q for o in REGISTRE["outils"] for q in [""] + list(o.get("parametres", {}).values())}
        self.assertEqual({h.split("?")[0] for h in hrefs}, {o["chemin"] for o in REGISTRE["outils"]})
        self.assertLessEqual(set(hrefs), attendus)                                    # chaque lien est un chemin du registre, avec la requête de sa filière s'il y en a une
        page.appel("Emulation.setScriptExecutionDisabled", value=False)

    def test_acc04_choix_de_la_filiere(self):
        page = self.ouvrir()
        page.evaluer("localStorage.clear()")
        page.appel("Page.reload")
        page.attendre("document.readyState === 'complete'", 30)
        # sans choix : la porte, pas les outils
        self.assertEqual(page.evaluer("document.querySelector('#gate').offsetParent !== null"), True)
        self.assertEqual(page.evaluer(LIENS_VISIBLES), 0)
        # Ms : les trois années (l'année II porte Exponentielles et logarithmes, lien ?filiere=M), filière affichée
        page.evaluer("document.querySelector('[data-choose=\"Ms\"]').click()")
        self.assertEqual(page.evaluer(ANNEES_VISIBLES), [True, True, True])
        self.assertEqual(page.evaluer("document.querySelector('#currentTrack').textContent"), "Ms")
        self.assertEqual(page.evaluer(LIENS_VISIBLES), 1 + 1 + 4)
        self.assertEqual(page.evaluer("[...document.querySelectorAll('.track[data-track=Ms] .tool a')].map(a => a.getAttribute('href')).filter(h => h.includes('exponentielles'))"),
                         ["exponentielles-logarithmes/?filiere=M"])
        # C : trois années (l'année III porte Exponentielles et logarithmes)
        page.evaluer("document.querySelector('#switchBtn').click()")
        self.assertEqual(page.evaluer("document.querySelector('#gate').offsetParent !== null"), True)
        page.evaluer("document.querySelector('[data-choose=\"C\"]').click()")
        self.assertEqual(page.evaluer(ANNEES_VISIBLES), [True, True, True])
        self.assertEqual(page.evaluer(LIENS_VISIBLES), 1 + 1 + 1)
        # Mr : trois années
        page.evaluer("document.querySelector('#switchBtn').click()")
        page.evaluer("document.querySelector('[data-choose=\"Mr\"]').click()")
        self.assertEqual(page.evaluer(ANNEES_VISIBLES), [True, True, True])
        # le choix survit à un rechargement, sans repasser par la porte
        page.appel("Page.reload")
        page.attendre("document.readyState === 'complete'", 30)
        self.assertEqual(page.evaluer("document.documentElement.getAttribute('data-track')"), "Mr")
        self.assertEqual(page.evaluer("document.querySelector('#gate').offsetParent"), None)
        self.assertEqual(page.evaluer("document.querySelector('#currentTrack').textContent"), "Mr")
        # « tous » : tout le registre
        page.evaluer("document.querySelector('#switchBtn').click()")
        page.evaluer("document.querySelector('[data-choose=\"tous\"]').click()")
        self.assertEqual(page.evaluer(LIENS_VISIBLES), LIENS)
        page.evaluer("localStorage.clear()")

    def images(self, page, duree=0.7):
        avant = page.evaluer("window.__images")
        time.sleep(duree)
        return page.evaluer("window.__images") - avant

    def test_acc06_le_ruban_ne_consomme_rien_hors_ecran(self):
        page = self.ouvrir(COMPTEUR_IMAGES, largeur=360, hauteur=300)
        page.evaluer("localStorage.clear()")
        page.appel("Page.reload")
        page.attendre("document.readyState === 'complete'", 30)
        self.assertGreater(self.images(page), 10, "le ruban est à l'écran : il s'anime")
        # hors écran : la page est défilée jusqu'au pied
        page.evaluer("window.scrollTo(0, document.body.scrollHeight)")
        time.sleep(0.4)
        self.assertLessEqual(self.images(page), 2, "le ruban n'est plus à l'écran : plus d'image")
        page.evaluer("window.scrollTo(0, 0)")
        time.sleep(0.4)
        self.assertGreater(self.images(page), 10, "de retour à l'écran, il repart")
        # onglet caché (événement visibilitychange et document.hidden simulés)
        page.evaluer("""Object.defineProperty(document, 'hidden', { configurable: true, get: () => true });
                        document.dispatchEvent(new Event('visibilitychange'))""")
        time.sleep(0.4)
        self.assertLessEqual(self.images(page), 2, "onglet caché : plus d'image")
        page.evaluer("""Object.defineProperty(document, 'hidden', { configurable: true, get: () => false });
                        document.dispatchEvent(new Event('visibilitychange'))""")
        time.sleep(0.3)
        self.assertGreater(self.images(page), 10, "onglet de nouveau visible : il repart")

    def test_mouvement_reduit_image_fixe(self):
        page = self.nav.ouvrir("index.html", COMPTEUR_IMAGES)
        page.appel("Emulation.setEmulatedMedia", media="screen", features=[{"name": "prefers-reduced-motion", "value": "reduce"}])
        page.appel("Page.reload")
        page.attendre("document.readyState === 'complete'", 30)
        time.sleep(0.3)
        self.assertLessEqual(self.images(page), 1)
        self.assertTrue(self.pixels_du_ruban(page) > 0, "l'image fixe est dessinée")

    @staticmethod
    def pixels_du_ruban(page):
        return page.evaluer("""(() => { const c = document.querySelector('#mobius'), d = c.getContext('2d').getImageData(0, 0, c.width, c.height).data;
                                       let n = 0; for (let i = 3; i < d.length; i += 4) if (d[i] > 0) n++; return n; })()""")

    @staticmethod
    def empreinte_du_ruban(page):
        return page.evaluer("""(() => { const c = document.querySelector('#mobius'), d = c.getContext('2d').getImageData(0, 0, c.width, c.height).data;
                                       const vus = {}; for (let i = 0; i < d.length; i += 4) if (d[i + 3] > 250) vus[d[i] + ',' + d[i + 1] + ',' + d[i + 2]] = 1;
                                       return Object.keys(vus).sort().join(';'); })()""")

    def test_le_ruban_suit_le_theme_sans_recharger(self):
        page = self.nav.ouvrir("index.html")
        page.appel("Emulation.setEmulatedMedia", media="screen", features=[{"name": "prefers-reduced-motion", "value": "reduce"},
                                                                            {"name": "prefers-color-scheme", "value": "light"}])
        page.appel("Page.reload")
        page.attendre("document.readyState === 'complete'", 30)
        clair = self.empreinte_du_ruban(page)
        self.assertTrue(clair)
        page.appel("Emulation.setEmulatedMedia", media="screen", features=[{"name": "prefers-reduced-motion", "value": "reduce"},
                                                                            {"name": "prefers-color-scheme", "value": "dark"}])
        time.sleep(0.3)
        sombre = self.empreinte_du_ruban(page)
        self.assertNotEqual(clair, sombre, "les couleurs du ruban suivent le thème, sans recharger la page")


if __name__ == "__main__":
    unittest.main()
