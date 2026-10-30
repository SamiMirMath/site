"""Tests de page — « Programmation linéaire » (simplexe/index.html, page autonome sans Pyodide) :
A. formulaire vide à l'ouverture, les exemples ne remplissent qu'au clic (chantier du 30.10.2026)."""
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(__file__))
from navigateur import Navigateur

CHOISI = not os.environ.get("OUTILS") or "simplexe" in os.environ["OUTILS"].split(",")

CHAMPS = "[...document.querySelectorAll('#objRow input, #consRows input')]"
LARGEURS = (360, 1100)


@unittest.skipUnless(CHOISI, "hors de OUTILS")
class TestSimplexe(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.nav = Navigateur().__enter__()

    @classmethod
    def tearDownClass(cls):
        cls.nav.__exit__(None, None, None)

    def ouvrir(self, largeur=1100, requete=""):
        page = self.nav.ouvrir(f"simplexe/index.html{requete}")
        page.attendre("document.readyState === 'complete' && document.querySelector('#objRow input')", 30)
        page.taille(largeur, 800)
        return page

    def clic(self, page, selecteur):
        page.evaluer(f"document.querySelector({selecteur!r}).click()")

    def defile_horizontalement(self, page):
        return page.evaluer("document.documentElement.scrollWidth - innerWidth") > 0

    # ---------- A. aucun champ prérempli ----------
    def test_a_formulaire_vide_a_l_ouverture_et_exemple_au_clic(self):
        for largeur in LARGEURS:
            with self.subTest(largeur=largeur):
                page = self.ouvrir(largeur)
                # fonction économique vide, trois contraintes vides (≤), 2 variables, « Maximiser », méthode algébrique
                self.assertEqual(page.evaluer(f"{CHAMPS}.map(i => i.value)"), [""] * (2 + 3 * 3))
                self.assertEqual(page.evaluer("document.querySelectorAll('#objRow input').length"), 2)
                self.assertEqual(page.evaluer("document.querySelectorAll('#consRows .coefs').length"), 3)
                self.assertEqual(page.evaluer("[...document.querySelectorAll('#consRows .opb')].map(b => b.textContent)"), ["≤"] * 3)
                self.assertEqual(page.evaluer("[...document.querySelectorAll('.row button.on')].map(b => b.textContent.trim())"),
                                 ["2Mr/OS · Méthode algébrique", "2 variables (polygone)", "Maximiser"])
                self.assertFalse(self.defile_horizontalement(page))
                # un exemple ne remplit qu'au clic
                self.clic(page, '[data-ex="Exemple 2D"]')
                self.assertEqual(page.evaluer(f"{CHAMPS}.map(i => i.value)"), ["100", "120", "3", "4", "4200", "1", "3", "2400", "2", "2", "2600"])
                self.clic(page, '[data-ex="Exemple 3D"]')
                self.assertEqual(page.evaluer("document.querySelectorAll('#objRow input').length"), 3)
                self.assertEqual(page.evaluer("document.querySelector('#objRow input').value"), "6")
                self.assertFalse(self.defile_horizontalement(page))

    def test_a_lancer_a_vide_donne_des_messages_clairs_au_vouvoiement(self):
        page = self.ouvrir(360)
        for methode in ("simplexe", "para"):
            with self.subTest(methode=methode):
                self.clic(page, f'[data-meth="{methode}"]')
                self.clic(page, "#launch")
                self.assertEqual(page.evaluer("document.querySelector('#err').textContent"),
                                 "✗ Fonction économique vide : entrez au moins un coefficient non nul.")
                page.evaluer("(() => { const i = document.querySelector('#objRow input'); i.value = '2'; i.dispatchEvent(new Event('input')); })()")
                self.clic(page, "#launch")
                msg = page.evaluer("document.querySelector('#err').textContent")
                self.assertTrue(msg.startswith("✗ Il faut au moins une contrainte"), msg)
                self.assertIn("remplissez", msg)
                self.assertTrue(page.evaluer("document.querySelector('#app').hidden && document.querySelector('#appPara').hidden"))
                self.clic(page, '[data-ex="Exemple 2D"]' if methode == "simplexe" else '[data-ex="Parallèles : max"]')
                page.evaluer("[...document.querySelectorAll('#consRows input')].forEach(i => { i.value = ''; i.dispatchEvent(new Event('input')); })")
                self.clic(page, "#launch")
                msg = page.evaluer("document.querySelector('#err').textContent")
                self.assertTrue(msg.startswith("✗ Il faut au moins une contrainte"), msg)
                page.evaluer("location.reload()")                       # saisie remise à zéro pour la méthode suivante
                page.attendre("document.readyState === 'complete' && document.querySelector('#objRow input')", 30)

    def test_a_modifier_le_probleme_garde_la_saisie(self):
        for methode, exemple, apres in (("simplexe", "Exemple 2D", "#app"), ("para", "Parallèles : max", "#appPara")):
            with self.subTest(methode=methode):
                page = self.ouvrir(360)
                self.clic(page, f'[data-ex="{exemple}"]')
                page.evaluer("(() => { const i = document.querySelector('#objRow input'); i.value = '7'; i.dispatchEvent(new Event('input')); })()")
                saisie = page.evaluer(f"{CHAMPS}.map(i => i.value)")
                self.clic(page, "#launch")
                self.assertFalse(page.evaluer(f"document.querySelector({apres!r}).hidden"))
                self.clic(page, "#editBtn" if methode == "simplexe" else "#editBtnP")
                self.assertFalse(page.evaluer("document.querySelector('#formCard').hidden"))
                self.assertEqual(page.evaluer(f"{CHAMPS}.map(i => i.value)"), saisie)
                self.assertEqual(saisie[0], "7")
                if methode == "simplexe":                                # un redessin du formulaire (changement de variables) garde aussi les valeurs
                    self.clic(page, "[data-dim='3']")
                    self.assertEqual(page.evaluer("document.querySelector('#objRow input').value"), "7")


if __name__ == "__main__":
    unittest.main()
