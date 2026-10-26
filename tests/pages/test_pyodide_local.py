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
        """Pyodide vient de la copie locale ; SymPy et mpmath des roues précompilées du site (T32), donc pas de roue SymPy demandée au CDN."""
        with Navigateur() as nav:
            attendre_pret(nav.ouvrir("factorisation/index.html"))
            self.assertIn("pyodide.asm.wasm", nav.intercepteur.servies)
            self.assertNotIn("sympy-1.13.3-py3-none-any.whl", nav.intercepteur.servies)
            self.assertEqual(nav.intercepteur.refusees, [])

    def modifier_manifeste(self, modification):
        """Script exécuté avant la page : le manifeste reçu par la page est modifié par `modification` (JavaScript sur `m`)."""
        return f"""(() => {{ const f = window.fetch.bind(window);
            window.fetch = async (u, o) => {{ const r = await f(u, o);
              if (String(u).endsWith('manifeste.json')) {{ const m = await r.json(); {modification}
                return new Response(JSON.stringify(m), {{ headers: {{ 'content-type': 'application/json' }} }}); }}
              return r; }}; }})()"""

    def test_roues_absentes_repli_sur_le_cdn(self):
        """Une roue précompilée introuvable ne bloque rien : SymPy est pris dans le CDN de Pyodide, la page arrive à « Prêt. »."""
        with Navigateur() as nav:
            attendre_pret(nav.ouvrir("factorisation/index.html", self.modifier_manifeste("m.roues.fichiers.push('moteur/roues/absente.zip');")))
            self.assertIn("sympy-1.13.3-py3-none-any.whl", nav.intercepteur.servies)

    def test_bytecode_d_une_autre_version_de_python_repli_sur_le_cdn(self):
        """Si Pyodide change de version de Python (autre numéro magique), les roues précompilées ne sont pas utilisées."""
        with Navigateur() as nav:
            attendre_pret(nav.ouvrir("factorisation/index.html", self.modifier_manifeste("m.roues.pyc = '00000000';")))
            self.assertIn("sympy-1.13.3-py3-none-any.whl", nav.intercepteur.servies)

if __name__ == "__main__":
    unittest.main()
