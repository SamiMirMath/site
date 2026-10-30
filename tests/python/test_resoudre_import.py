"""T12 — Les adaptateurs `resoudre_*.py` s'importent avec les seuls fichiers qu'une page aurait à
charger dans Pyodide (système de fichiers à plat), et `resoudre()` y fonctionne."""
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

from moteurs import RACINE

BASE = ["ensemble-definition/ensemble_def.py", "moteur/noyau.py", "moteur/sortie.py"]
DV = "derivee-variations/derivee_variations.py"
LA = "limites-asymptotes/limites_asymptotes.py"
RB = "limites-asymptotes/redaction_bh.py"
OUTILS = {
    "ensemble-definition": (["ensemble-definition/ensemble_def.py", "moteur/sortie.py", "ensemble-definition/resoudre_ed.py"],
                            "resoudre_ed", "ln(x-1)"),
    "derivee-variations": (BASE + [DV, "derivee-variations/resoudre_dv.py"], "resoudre_dv", "x^2"),
    "limites-asymptotes": (BASE + [LA, RB, "limites-asymptotes/resoudre_la.py"], "resoudre_la", "1/x"),
    "etude-complete": (BASE + [DV, LA, RB, "derivee-variations/resoudre_dv.py", "limites-asymptotes/resoudre_la.py",
                               "etude-complete/etude_complete.py", "etude-complete/resoudre_ec.py"], "resoudre_ec", "1/x"),
    "factorisation": (BASE + ["factorisation/factorisation.py", "factorisation/resoudre_fa.py"], "resoudre_fa", "x^2-1"),
    "exponentielles-logarithmes": (BASE + ["moteur/nombres.py", "ensemble-definition/resoudre_ed.py", "exponentielles-logarithmes/exp_log.py",
                                           "exponentielles-logarithmes/exp_log_m.py", "exponentielles-logarithmes/resoudre_el.py"],
                                   "resoudre_el", "3^(x+1)=27"),
}
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
