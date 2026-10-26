"""Tests de pages — le rendu de chaque page outil est égal à la référence enregistrée dans
tests/pages/references/<outil>.json (cartes, textes et formules, structure des tableaux, compteur).

Chrome sans interface ; Pyodide vient de la copie locale (pyodide_local.py), KaTeX de jsDelivr ; ~ 1 min par page.

    uv run -q --no-project --python 3.12 --with sympy==1.13.3 --with websockets \
        python -m unittest discover -s tests/pages
    OUTILS=etude-complete uv run … python -m unittest discover -s tests/pages    # une seule page
    CORPUS=reduit uv run …                                                       # 3 entrées par outil (celui de la CI)

Après un changement VOULU du rendu : capturer_references.py, puis relire le diff git."""
import json
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(__file__))
from navigateur import Navigateur
from rendu import DOSSIER_REFERENCES, OUTILS, attendre_pret, capturer, entrees

CHOISIS = [o for o in os.environ.get("OUTILS", "").split(",") if o] or OUTILS


class TestRendu(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.nav = Navigateur().__enter__()

    @classmethod
    def tearDownClass(cls):
        cls.nav.__exit__(None, None, None)

    def verifier_outil(self, outil):
        if outil not in CHOISIS:
            self.skipTest("hors de OUTILS")
        with open(os.path.join(DOSSIER_REFERENCES, outil + ".json"), encoding="utf-8") as f:
            reference = json.load(f)
        page = self.nav.ouvrir(f"{outil}/index.html")
        attendre_pret(page)
        if os.environ.get("CORPUS") != "reduit":
            self.assertEqual(sorted(reference), sorted(entrees(outil)),
                             "références et corpus différents : relancer capturer_references.py")
        for entree in entrees(outil):             # CORPUS=reduit : 3 entrées par outil (CI)
            with self.subTest(outil=outil, entree=entree):
                self.assertEqual(capturer(page, entree), reference[entree])

    def test_ensemble_definition(self):
        self.verifier_outil("ensemble-definition")

    def test_derivee_variations(self):
        self.verifier_outil("derivee-variations")

    def test_limites_asymptotes(self):
        self.verifier_outil("limites-asymptotes")

    def test_etude_complete(self):
        self.verifier_outil("etude-complete")

    def test_factorisation(self):
        self.verifier_outil("factorisation")

    def test_exponentielles_logarithmes(self):
        self.verifier_outil("exponentielles-logarithmes")


if __name__ == "__main__":
    unittest.main()
