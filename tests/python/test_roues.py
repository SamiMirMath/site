"""T32 — roues précompilées de SymPy et mpmath (moteur/roues/*.zip, construites par moteur/construire_roues.py).

Elles remplacent le source par le bytecode pour que Python n'ait plus à compiler SymPy à chaque ouverture de page. Ces tests vérifient qu'elles
viennent bien du SymPy et du mpmath du manifeste (même code, module par module), qu'elles ont le bytecode de Python 3.12, et qu'elles sont
complètes : un module qui manque dans la roue reste utilisable (il est compilé à l'import), mais un module compilé avec un autre code serait faux."""
import importlib.util
import json
import marshal
import os
import re
import sys
import unittest
import zipfile

import mpmath
import sympy

from moteurs import RACINE

with open(os.path.join(RACINE, "moteur", "manifeste.json"), encoding="utf-8") as f:
    MANIFESTE = json.load(f)
ROUES = MANIFESTE["roues"]


def roue(paquet):
    chemins = [c for c in ROUES["fichiers"] if os.path.basename(c).startswith(paquet + "-")]
    assert len(chemins) == 1, (paquet, ROUES["fichiers"])
    return os.path.join(RACINE, chemins[0])


class TestRoues(unittest.TestCase):
    def test_manifeste_et_fichiers(self):
        v = MANIFESTE["versions"]
        self.assertEqual(sympy.__version__, v["sympy"])
        self.assertEqual(mpmath.__version__, v["mpmath"])
        self.assertEqual(len(ROUES["fichiers"]), 2)
        for paquet in ("sympy", "mpmath"):
            nom = os.path.basename(roue(paquet))
            self.assertRegex(nom, rf"^{paquet}-{re.escape(v[paquet])}-pyc312-[0-9a-f]{{8}}\.zip$")
        dans_le_dossier = sorted(n for n in os.listdir(os.path.join(RACINE, "moteur", "roues")) if n.endswith(".zip"))
        self.assertEqual(dans_le_dossier, sorted(os.path.basename(c) for c in ROUES["fichiers"]), "une ancienne roue traîne ou une roue manque")

    def test_licences_redistribuees(self):
        """SymPy et mpmath sont sous licence BSD : leur licence est à côté des roues, identique à celle qui est dans chaque roue."""
        dossier = os.path.join(RACINE, "moteur", "roues")
        for paquet, fichiers in (("sympy", ("LICENSE", "AUTHORS")), ("mpmath", ("LICENSE",))):
            with zipfile.ZipFile(roue(paquet)) as z:
                for base in fichiers:
                    with self.subTest(paquet=paquet, fichier=base):
                        interne = [n for n in z.namelist() if n.endswith(".dist-info/" + base)]
                        self.assertEqual(len(interne), 1)
                        with open(os.path.join(dossier, f"{base}-{paquet}.txt"), "rb") as f:
                            self.assertEqual(f.read(), z.read(interne[0]))
        with open(os.path.join(dossier, "LICENSE-sympy.txt"), encoding="utf-8") as f:
            self.assertIn("Redistribution", f.read())

    def test_numero_magique_du_bytecode(self):
        """Le manifeste annonce le numéro magique de Python 3.12 ; chaque .pyc de chaque roue commence par lui."""
        self.assertEqual(sys.version_info[:2], (3, 12))
        self.assertEqual(ROUES["pyc"], importlib.util.MAGIC_NUMBER.hex())
        magique = importlib.util.MAGIC_NUMBER
        for paquet in ("sympy", "mpmath"):
            with zipfile.ZipFile(roue(paquet)) as z:
                pyc = [n for n in z.namelist() if n.endswith(".pyc")]
                self.assertGreater(len(pyc), 40, paquet)
                for n in pyc:
                    self.assertEqual(z.read(n)[:4], magique, n)

    def test_meme_code_que_le_source_installe(self):
        """Chaque .pyc de la roue est exactement le bytecode du .py du paquet installé (même version) : la roue n'est pas périmée."""
        for paquet, module in (("sympy", sympy), ("mpmath", mpmath)):
            racine = os.path.dirname(os.path.dirname(module.__file__))
            with zipfile.ZipFile(roue(paquet)) as z:
                for n in z.namelist():
                    if not n.endswith(".pyc"):
                        continue
                    with self.subTest(module=n):
                        with open(os.path.join(racine, n[:-1]), "rb") as f:
                            source = f.read()
                        attendu = compile(source, n[:-1], "exec", dont_inherit=True)
                        self.assertEqual(marshal.loads(z.read(n)[16:]), attendu)

    def test_pas_de_source_en_double_et_rien_d_autre_ne_change(self):
        """Un module précompilé n'a plus son .py (sinon Python préférerait le source) ; les fichiers qui ne sont pas du Python sont copiés tels quels."""
        for paquet, module in (("sympy", sympy), ("mpmath", mpmath)):
            racine = os.path.dirname(os.path.dirname(module.__file__))
            with zipfile.ZipFile(roue(paquet)) as z:
                noms = set(z.namelist())
                for n in noms:
                    if n.endswith(".pyc"):
                        self.assertNotIn(n[:-1], noms, n)
                    elif not n.endswith(".py") and not n.endswith("/") and ".dist-info/" not in n and ".data/" not in n:
                        with open(os.path.join(racine, n), "rb") as f:
                            self.assertEqual(z.read(n), f.read(), n)

    def test_sympy_precompile_s_importe_et_calcule(self):
        """Python 3.12 charge SymPy depuis la roue seule (sans le source installé) et calcule."""
        import subprocess
        import tempfile
        with tempfile.TemporaryDirectory() as t:
            for paquet in ("mpmath", "sympy"):
                with zipfile.ZipFile(roue(paquet)) as z:
                    z.extractall(t)
            code = ("import sys; sys.path.insert(0, sys.argv[1]); sys.dont_write_bytecode = True\n"
                    "import sympy, mpmath\n"
                    "assert sympy.__file__.endswith('__init__.pyc') or 'site-packages' not in sympy.__file__\n"
                    "x = sympy.Symbol('x')\n"
                    "assert sympy.factor(x**2 - 1) == (x - 1) * (x + 1)\n"
                    "assert sympy.limit(sympy.sin(x) / x, x, 0) == 1\n")
            p = subprocess.run([sys.executable, "-I", "-S", "-c", code, t], capture_output=True, text=True, timeout=300)
            self.assertEqual(p.returncode, 0, p.stderr[-800:])


if __name__ == "__main__":
    unittest.main()
