"""T12 — Instantanés de `resoudre()` : la sortie du format commun de chaque outil, pour chaque
entrée de cas.py, est comparée à instantanes/resoudre/<outil>.json (référence des migrations
T17 à T20). Même mécanisme que test_instantanes.py :

    REGENERER=1 uv run -q --no-project --python 3.12 --with sympy==1.13.3 \
        python -m unittest discover -s tests/python -p test_instantanes_resoudre.py
"""
import json
import os
import unittest

import moteurs  # noqa: F401  (chemins des moteurs)
from test_instantanes import normaliser, resumer_segments, REGENERER
from cas import CAS_LIMITES, entrees_factorisation, entrees_page
import resoudre_fa
import resoudre_ed
import resoudre_dv
import resoudre_la

DOSSIER = os.path.join(os.path.dirname(__file__), "instantanes", "resoudre")

OUTILS = {
    "ensemble-definition": (resoudre_ed.resoudre, lambda: entrees_page("ensemble-definition") + CAS_LIMITES["ensemble-definition"]),
    "derivee-variations": (resoudre_dv.resoudre, lambda: entrees_page("derivee-variations") + CAS_LIMITES["derivee-variations"]),
    "limites-asymptotes": (resoudre_la.resoudre, lambda: entrees_page("limites-asymptotes") + CAS_LIMITES["limites-asymptotes"]),
    "factorisation": (resoudre_fa.resoudre, entrees_factorisation),
}


def sortie(fn, entree):
    try:
        return normaliser(resumer_segments(fn(entree)))
    except Exception as e:   # comportement actuel figé, y compris les plantages connus
        return {"exception": type(e).__name__, "message": str(e)}


class TestInstantanesResoudre(unittest.TestCase):
    def verifier_outil(self, outil):
        fn, entrees = OUTILS[outil]
        actuel = {}
        for e in entrees():
            actuel.setdefault(e, sortie(fn, e))
        chemin = os.path.join(DOSSIER, outil + ".json")
        if REGENERER:
            os.makedirs(DOSSIER, exist_ok=True)
            with open(chemin, "w", encoding="utf-8") as f:
                json.dump(actuel, f, ensure_ascii=False, indent=1, sort_keys=True, allow_nan=False)
                f.write("\n")
            self.skipTest(f"instantané régénéré : {chemin}")
        self.assertTrue(os.path.exists(chemin), f"instantané absent : lancer avec REGENERER=1 ({chemin})")
        with open(chemin, encoding="utf-8") as f:
            reference = json.load(f)
        self.assertEqual(sorted(actuel), sorted(reference),
                         "liste des entrées modifiée : régénérer avec REGENERER=1")
        for entree in actuel:
            with self.subTest(outil=outil, entree=entree):
                self.assertEqual(actuel[entree], reference[entree])

    def test_ensemble_definition(self):
        self.verifier_outil("ensemble-definition")

    def test_derivee_variations(self):
        self.verifier_outil("derivee-variations")

    def test_limites_asymptotes(self):
        self.verifier_outil("limites-asymptotes")

    def test_factorisation(self):
        self.verifier_outil("factorisation")


if __name__ == "__main__":
    unittest.main()
