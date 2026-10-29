"""T30 — les tests de pages chargent Pyodide depuis la copie locale (tests/pages/pyodide-local/), pas depuis le CDN.

    python tests/pages/pyodide_local.py     # télécharge la copie si elle manque"""
import json
import os
import shutil
import sys
import hashlib
import io
import ssl
import tempfile
import unittest
from unittest import mock
import urllib.error

sys.path.insert(0, os.path.dirname(__file__))
import pyodide_local
from navigateur import Navigateur
from rendu import attendre_pret


class _Reponse(io.BytesIO):
    def __init__(self, octets, annonce=None):
        super().__init__(octets)
        self.headers = {} if annonce is None else {"Content-Length": str(annonce)}

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


class TestTelechargementRobuste(unittest.TestCase):
    """Une coupure réseau pendant le téléchargement de la copie ne fait pas échouer la CI : nouvel essai (attente croissante), fichier vérifié."""

    def lire(self, reponses, **options):
        suite = iter(reponses)

        def urlopen(url, timeout):
            r = next(suite)
            if isinstance(r, Exception):
                raise r
            return r
        with mock.patch.object(pyodide_local.urllib.request, "urlopen", urlopen), mock.patch.object(pyodide_local.time, "sleep") as dodo:
            try:
                return pyodide_local._lire("https://exemple/fichier", **options), dodo
            except RuntimeError as e:
                return e, dodo

    def test_coupure_ssl_puis_succes(self):
        octets, dodo = self.lire([ssl.SSLError("UNEXPECTED_EOF_WHILE_READING"), urllib.error.URLError("coupure"), _Reponse(b"abc", 3)])
        self.assertEqual(octets, b"abc")
        self.assertEqual([c.args[0] for c in dodo.call_args_list], [2, 4])                    # attente croissante

    def test_lecture_tronquee_refusee_puis_reprise(self):
        octets, _ = self.lire([_Reponse(b"ab", 3), _Reponse(b"abc", 3)])
        self.assertEqual(octets, b"abc")

    def test_empreinte_fausse_refusee(self):
        bon = hashlib.sha256(b"abc").hexdigest()
        octets, _ = self.lire([_Reponse(b"abX"), _Reponse(b"abc")], sha256=bon)
        self.assertEqual(octets, b"abc")

    def test_echec_apres_toutes_les_tentatives(self):
        e, dodo = self.lire([OSError("coupure")] * pyodide_local.TENTATIVES)
        self.assertIsInstance(e, RuntimeError)
        self.assertIn("téléchargement impossible après 5 essais", str(e))
        self.assertEqual(dodo.call_count, pyodide_local.TENTATIVES - 1)

    def test_controle_de_forme(self):
        self.assertRaises(OSError, pyodide_local._verification("pyodide.asm.wasm"), b"<html>")
        pyodide_local._verification("pyodide.asm.wasm")(b"\0asm\1\0\0\0")
        self.assertRaises(OSError, pyodide_local._verification("python_stdlib.zip"), b"pas une archive")
        self.assertRaises(OSError, pyodide_local._verification("pyodide.js"), b"")


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
