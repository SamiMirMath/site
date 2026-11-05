"""T12 — Les adaptateurs `resoudre_*.py` s'importent avec les seuls fichiers qu'une page aurait à
charger dans Pyodide (système de fichiers à plat), et `resoudre()` y fonctionne."""
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

import outils_du_site
from moteurs import RACINE

# fichiers et module de chaque outil : ceux du manifeste (outils_du_site, F3 ; plus de copie de ses listes de fichiers) ; ici, seulement
# l'exemple résolu par outil (clés vérifiées par test_outils_du_site.py : chaque outil du manifeste)
EXEMPLE = {"ensemble-definition": "ln(x-1)", "derivee-variations": "x^2", "limites-asymptotes": "1/x", "etude-complete": "1/x",
           "factorisation": "x^2-1", "exponentielles-logarithmes": "3^(x+1)=27"}
OUTILS = {outil: (o["fichiers"], o["module"], EXEMPLE.get(outil)) for outil, o in outils_du_site.manifeste().items()}
FILIERE_M = {"exponentielles-logarithmes": "log_x(256)=4"}      # outils qui ont une filière M : même import à plat, `resoudre(exemple, "M")`


class TestResoudreImport(unittest.TestCase):
    def test_import_a_plat(self):
        for outil, (fichiers, module, exemple) in OUTILS.items():
            with self.subTest(outil=outil), tempfile.TemporaryDirectory() as fs:
                for chemin in fichiers:
                    shutil.copy(os.path.join(RACINE, chemin), os.path.join(fs, os.path.basename(chemin)))
                code = (
                    "import sys; sys.path.insert(0, sys.argv[1]); sys.dont_write_bytecode = True\n"
                    f"import {module} as m, sortie\n"
                    f"s = m.resoudre({exemple!r})\n"
                    "assert s['ok'] and sortie.valider(s) == [], sortie.valider(s)\n"
                    "import json; assert json.loads(m.resoudre_json(" + repr(exemple) + "))['ok']\n"
                    + (f"s = m.resoudre({FILIERE_M[outil]!r}, 'M'); assert s['ok'] and sortie.valider(s) == [], sortie.valider(s)\n"
                       f"assert s['cartes'][0]['badge'] == 'Ensemble de définition'\n" if outil in FILIERE_M else "") +
                    "assert json.loads(m.apercu_json(" + repr(exemple) + "))['ok']\n"
                )
                p = subprocess.run([sys.executable, "-I", "-c", code, fs], capture_output=True, text=True, timeout=120)
                self.assertEqual(p.returncode, 0, (p.stderr.strip().splitlines() or [""])[-1])


if __name__ == "__main__":
    unittest.main()
