"""Graphique de l'Étude complète : la trace des appels canvas de chaque scénario (3 fonctions × 2 vues × 8 états : tracé
initial, boutons, molette, glisser, pincer, impression) est égale à l'empreinte enregistrée dans
references/graphique-traces.json. Aucune police n'entre dans la trace (le dessin n'appelle pas measureText), donc
elle est la même en local et en CI. Voir graphique.py pour le détail des niveaux de preuve.

    OUTILS=etude-complete uv run … python -m unittest tests/pages/test_graphique.py

Après un changement VOULU du dessin : graphique.py references, puis relire le diff git. Pour voir quels appels ont
changé : graphique.py enregistrer <avant> / <après> puis comparer."""
import json
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(__file__))
from graphique import FONCTIONS_SUITE, REFERENCES, VUES_SUITE, empreintes, jouer
from navigateur import Navigateur

CHOISIS = [o for o in os.environ.get("OUTILS", "").split(",") if o]


class TestGraphique(unittest.TestCase):
    def test_traces_egales_aux_references(self):
        if CHOISIS and "etude-complete" not in CHOISIS:
            self.skipTest("hors de OUTILS")
        with open(REFERENCES, encoding="utf-8") as f:
            attendu = json.load(f)
        with Navigateur() as nav:
            obtenu = jouer(nav, FONCTIONS_SUITE, VUES_SUITE)
        self.assertEqual(obtenu["__console_erreurs"], [])
        empr = empreintes(obtenu)
        self.assertEqual(sorted(empr), sorted(attendu), "scénarios différents : relancer graphique.py references")
        for cle in sorted(attendu):
            with self.subTest(scenario=cle):
                self.assertEqual(empr[cle], attendu[cle])


if __name__ == "__main__":
    unittest.main()
