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


def lire(chemin):
    with open(os.path.join(RACINE, chemin), encoding="utf-8") as f:
        return f.read()


def page(dossier):
    with open(os.path.join(RACINE, dossier, "index.html"), encoding="utf-8") as f:
        return f.read()


CLIENT = "../commun/moteur-python.js"
OUTIL = "../commun/outil.js"          # page générique (T16) : monterOutil({outil: …}) ; le client est dans outil.js


def utilise_pyodide(src):
    return "loadPyodide" in src or CLIENT in src or OUTIL in src


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
                        if os.path.isfile(os.path.join(RACINE, d, "index.html")) and utilise_pyodide(page(d))}
        self.assertEqual(set(OUTILS), avec_pyodide)

    def test_conforme_aux_pages(self):
        for dossier, o in OUTILS.items():
            s = page(dossier)
            with self.subTest(outil=dossier):
                if OUTIL in s:
                    # page générique : la page ne nomme que l'outil ; les appels sont ceux d'outil.js et de sa config
                    self.assertIn(f'outil:"{dossier}"', s)
                    self.assertNotIn("loadPyodide", s)
                    self.assertNotIn("new Worker", s)
                    greffons = lire("commun/graphique.js") if "graphique.js" in s else ""         # greffon de bloc : ses appels sont ceux de la page
                    appels = set(re.findall(r'appelPy\("([a-z_]+)"', s + lire("commun/outil.js") + greffons))
                    self.assertTrue(appels <= set(o["fonctions"]), appels - set(o["fonctions"]))
                    self.assertEqual(set(o["fonctions"]) - appels, set(o.get("anciennes", [])),
                                     "fonctions non appelées = anciennes (pages en cache)")
                    continue
                if CLIENT in s:
                    # client commun : les fichiers viennent du manifeste, la page ne nomme que l'outil et ses appels
                    self.assertIn(f'new MoteurPython("{dossier}"', s)
                    self.assertNotIn("loadPyodide", s)
                    self.assertNotIn("writeFile(", s)
                else:
                    charges = {os.path.normpath(os.path.join(dossier, c)) for c in re.findall(r'fetch\("([^"]+\.py)"', s)}
                    self.assertEqual(charges, {os.path.normpath(c) for c in o["fichiers"]}, "fichiers téléchargés")
                    ecrits = set(re.findall(r'writeFile\("([^"]+)"', s))
                    self.assertEqual(ecrits, {os.path.basename(c) for c in o["fichiers"]}, "fichiers écrits dans Pyodide")
                    self.assertIn(f'runPython("import {o["module"]}")', s)
                self.assertEqual(set(re.findall(r'appelPy\("([a-z_]+)"', s)), set(o["fonctions"]), "fonctions appelées")

    def test_outil_utilise_le_client_commun(self):
        outil = lire("commun/outil.js")
        self.assertIn('from "./moteur-python.js"', outil)
        self.assertNotIn("loadPyodide", outil)

    def test_client_commun_et_worker(self):
        client, worker = lire("commun/moteur-python.js"), lire("commun/worker-pyodide.js")
        self.assertIn('manifeste.json', client)
        self.assertIn('new Worker(new URL("worker-pyodide.js", import.meta.url))', client)
        self.assertNotIn("Blob", client + worker)                      # vrai fichier, plus de Blob
        self.assertNotRegex(client + worker, r"pyodide/v\d")           # la version vient du manifeste seulement
        self.assertIn("importScripts(arg.indexURL", worker)

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
        """La version de Pyodide (pages à worker intégré, client commun) et celles de la CI sont celles du manifeste."""
        for dossier in OUTILS:
            with self.subTest(page=dossier):
                if CLIENT not in page(dossier) and OUTIL not in page(dossier):
                    self.assertIn(f'const PYODIDE="https://cdn.jsdelivr.net/pyodide/v{VERSIONS["pyodide"]}/full/"', page(dossier))
                else:
                    self.assertNotRegex(page(dossier), r"pyodide/v\d")
        with open(os.path.join(RACINE, ".github", "workflows", "tests.yml"), encoding="utf-8") as f:
            ci = f.read()
        self.assertIn(f'python-version: "{VERSIONS["python"]}"', ci)
        self.assertIn(f'sympy=={VERSIONS["sympy"]}', ci)
        self.assertIn(f'mpmath=={VERSIONS["mpmath"]}', ci)


if __name__ == "__main__":
    unittest.main()
