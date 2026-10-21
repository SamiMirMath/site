"""T30 — les tests de pages chargent Pyodide depuis la copie locale (tests/pages/pyodide-local/), pas depuis le CDN.

    python tests/pages/pyodide_local.py     # télécharge la copie si elle manque"""
import json
import os
import shutil
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(__file__))
import pyodide_local
from navigateur import Navigateur
from rendu import attendre_pret


class TestPyodideLocal(unittest.TestCase):
    def test_version_de_la_copie_egale_a_celle_des_pages(self):
        pyodide_local.verifier()
        self.assertEqual(pyodide_local._lock()["info"]["version"], pyodide_local.version_attendue())

    def test_une_copie_d_une_autre_version_fait_echouer(self):
        with tempfile.TemporaryDirectory() as t:
            copie = os.path.join(t, "copie")
            shutil.copytree(pyodide_local.DOSSIER, copie)
            chemin = os.path.join(copie, "pyodide-lock.json")
            with open(chemin, encoding="utf-8") as f:
                lock = json.load(f)
            lock["info"]["version"] = "0.0.0"
            with open(chemin, "w", encoding="utf-8") as f:
                json.dump(lock, f)
            with self.assertRaisesRegex(RuntimeError, "0.0.0"):
                pyodide_local.verifier(copie)

    def test_une_copie_incomplete_fait_echouer(self):
        with tempfile.TemporaryDirectory() as t:
            copie = os.path.join(t, "copie")
            shutil.copytree(pyodide_local.DOSSIER, copie)
            os.remove(os.path.join(copie, "pyodide.asm.wasm"))
            with self.assertRaisesRegex(RuntimeError, "incomplète"):
                pyodide_local.verifier(copie)

    def test_une_page_se_charge_sans_le_cdn(self):
        with Navigateur() as nav:
            attendre_pret(nav.ouvrir("factorisation/index.html"))
            self.assertIn("pyodide.asm.wasm", nav.intercepteur.servies)
            self.assertIn("sympy-1.13.3-py3-none-any.whl", nav.intercepteur.servies)
            self.assertEqual(nav.intercepteur.refusees, [])


if __name__ == "__main__":
    unittest.main()
