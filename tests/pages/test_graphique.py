"""Graphique de l'Étude complète : la trace des appels canvas de chaque scénario (3 fonctions × 2 vues × 8 états : tracé
initial, boutons, molette, glisser, pincer, impression) est égale à l'empreinte enregistrée dans
references/graphique-traces.json. EC-04 : si le calcul de la fenêtre échoue, la courbe reste celle de la dernière fenêtre
réussie et un message discret l'indique. Aucune police n'entre dans la trace (le dessin n'appelle pas measureText), donc
elle est la même en local et en CI. Voir graphique.py pour le détail des niveaux de preuve.

    OUTILS=etude-complete uv run … python -m unittest tests/pages/test_graphique.py

Après un changement VOULU du dessin : graphique.py references, puis relire le diff git. Pour voir quels appels ont
changé : graphique.py enregistrer <avant> / <après> puis comparer."""
import json
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(__file__))
from graphique import FONCTIONS_SUITE, JS_TRACE, PAGE, REFERENCES, VUES_SUITE, attendre_calme, calculer, cliquer, empreintes, jouer
from navigateur import Navigateur
from rendu import attendre_pret

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

    def test_ec04_echec_de_fenetre(self):
        if CHOISIS and "etude-complete" not in CHOISIS:
            self.skipTest("hors de OUTILS")
        with Navigateur() as nav:
            page = nav.ouvrir(PAGE, JS_TRACE)
            attendre_pret(page)
            calculer(page, "x^2*e^(-x)")
            attendre_calme(page)
            segments = lambda: page.evaluer("JSON.stringify(document.querySelector('#graphique').__g.segments)")
            vista = lambda: page.evaluer("JSON.stringify(document.querySelector('#graphique').__vista)")
            message = lambda: page.evaluer("!document.querySelector('#msgFenetre').hidden")
            depart, vista0 = segments(), vista()
            self.assertFalse(message())
            for mode in ("refus", "exception"):         # le moteur répond ok:false, ou le calcul lève une erreur
                with self.subTest(mode=mode):
                    page.evaluer(f"window.__echecFenetre = {mode!r}")
                    cliquer(page, "#zoomPlus")
                    attendre_calme(page)
                    self.assertTrue(message(), "message discret absent")
                    self.assertEqual(segments(), depart, "la courbe doit rester celle de la dernière fenêtre réussie")
                    self.assertNotEqual(vista(), vista0, "le zoom doit s'appliquer à la courbe affichée")
            page.evaluer("window.__echecFenetre = null")        # le moteur répond de nouveau
            cliquer(page, "#zoomPlus")
            attendre_calme(page)
            self.assertFalse(message(), "le message doit disparaître quand la fenêtre est recalculée")
            self.assertNotEqual(segments(), depart, "la courbe doit être recalculée pour la nouvelle fenêtre")


if __name__ == "__main__":
    unittest.main()
