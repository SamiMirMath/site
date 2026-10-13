"""T04 — moteur/manifeste.json : la liste des fichiers Python que chaque outil charge dans
Pyodide est complète, minimale et conforme à ce que font réellement les pages.

Le système de fichiers de Pyodide est simulé par un dossier temporaire où les fichiers du
manifeste sont copiés à plat (comme `py.FS.writeFile(nom, …)`), puis le module de l'outil
est importé dans un Python isolé : un fichier manquant fait échouer l'import."""
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest

from moteurs import RACINE

with open(os.path.join(RACINE, "moteur", "manifeste.json"), encoding="utf-8") as f:
    MANIFESTE = json.load(f)
OUTILS = MANIFESTE["outils"]
VERSIONS = MANIFESTE["versions"]


def page(dossier):
    with open(os.path.join(RACINE, dossier, "index.html"), encoding="utf-8") as f:
        return f.read()


def importer_isole(fichiers, module, fonctions):
    """Copie `fichiers` à plat dans un dossier vide et importe `module` dans un Python isolé
    (-I : ni le dossier courant, ni PYTHONPATH, ni les dossiers du dépôt sur le chemin).
    Renvoie (succès, message)."""
    with tempfile.TemporaryDirectory() as fs:
        for chemin in fichiers:
            shutil.copy(os.path.join(RACINE, chemin), os.path.join(fs, os.path.basename(chemin)))
        code = (
            "import sys; sys.path.insert(0, sys.argv[1]); sys.dont_write_bytecode = True\n"
            f"import {module} as m\n"
            f"manquantes = [f for f in {fonctions!r} if not callable(getattr(m, f + '_json', None))]\n"
            "assert not manquantes, manquantes\n"
            "import json; assert json.loads(m.apercu_json('x+1'))['ok']\n"
        )
        p = subprocess.run([sys.executable, "-I", "-c", code, fs], capture_output=True, text=True, timeout=120)
        return p.returncode == 0, (p.stderr.strip().splitlines() or [""])[-1]


class TestManifeste(unittest.TestCase):
    def test_tous_les_outils_pyodide_sont_declares(self):
        avec_pyodide = {d for d in os.listdir(RACINE)
                        if os.path.isfile(os.path.join(RACINE, d, "index.html")) and "loadPyodide" in page(d)}
        self.assertEqual(set(OUTILS), avec_pyodide)

    def test_conforme_aux_pages(self):
        for dossier, o in OUTILS.items():
            s = page(dossier)
            with self.subTest(outil=dossier):
                charges = {os.path.normpath(os.path.join(dossier, c)) for c in re.findall(r'fetch\("([^"]+\.py)"', s)}
                self.assertEqual(charges, {os.path.normpath(c) for c in o["fichiers"]}, "fichiers téléchargés")
                ecrits = set(re.findall(r'writeFile\("([^"]+)"', s))
                self.assertEqual(ecrits, {os.path.basename(c) for c in o["fichiers"]}, "fichiers écrits dans Pyodide")
                self.assertIn(f'runPython("import {o["module"]}")', s)
                self.assertEqual(set(re.findall(r'appelPy\("([a-z_]+)"', s)), set(o["fonctions"]), "fonctions appelées")

    def test_import_avec_les_seuls_fichiers_du_manifeste(self):
        for dossier, o in OUTILS.items():
            with self.subTest(outil=dossier):
                ok, msg = importer_isole(o["fichiers"], o["module"], o["fonctions"])
                self.assertTrue(ok, msg)

    def test_manifeste_minimal(self):
        """Retirer n'importe quel fichier (autre que le module lui-même) casse l'import :
        le manifeste ne fait rien télécharger d'inutile à l'élève."""
        for dossier, o in OUTILS.items():
            for retire in o["fichiers"]:
                if os.path.basename(retire) == o["module"] + ".py":
                    continue
                with self.subTest(outil=dossier, sans=retire):
                    ok, _ = importer_isole([c for c in o["fichiers"] if c != retire], o["module"], o["fonctions"])
                    self.assertFalse(ok, f"{retire} n'est pas nécessaire")

    def test_versions_coherentes(self):
        """La version de Pyodide des pages et celles de la CI sont celles du manifeste."""
        for dossier in OUTILS:
            with self.subTest(page=dossier):
                self.assertIn(f'const PYODIDE="https://cdn.jsdelivr.net/pyodide/v{VERSIONS["pyodide"]}/full/"', page(dossier))
        with open(os.path.join(RACINE, ".github", "workflows", "tests.yml"), encoding="utf-8") as f:
            ci = f.read()
        self.assertIn(f'python-version: "{VERSIONS["python"]}"', ci)
        self.assertIn(f'sympy=={VERSIONS["sympy"]}', ci)
        self.assertIn(f'mpmath=={VERSIONS["mpmath"]}', ci)


if __name__ == "__main__":
    unittest.main()
