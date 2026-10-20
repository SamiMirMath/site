"""Graphique de l'Étude complète : la trace des appels canvas de chaque scénario (3 fonctions × 2 vues × 8 états : tracé
initial, boutons, molette, glisser, pincer, impression) est égale à l'empreinte enregistrée dans
references/graphique-traces.json. EC-04 : si le calcul de la fenêtre échoue, la courbe reste celle de la dernière fenêtre
réussie et un message discret l'indique. EC-06 : aucun nombre du graphique n'est écrit avec un point décimal. EC-05 : sur écran tactile, un doigt fait défiler la
page (la courbe ne bouge pas) ; deux doigts déplacent et zooment la courbe sans faire défiler la page, et le point de la
courbe sous le milieu des doigts reste sous le milieu des doigts, quel que soit le nombre de mouvements livrés par le navigateur. Aucune police n'entre dans la trace (le dessin n'appelle pas measureText), donc
elle est la même en local et en CI. Voir graphique.py pour le détail des niveaux de preuve.

    OUTILS=etude-complete uv run … python -m unittest tests/pages/test_graphique.py

Après un changement VOULU du dessin : graphique.py references, puis relire le diff git. Pour voir quels appels ont
changé : graphique.py enregistrer <avant> / <après> puis comparer."""
import json
import math
import os
import re
import sys
import time
import unittest

sys.path.insert(0, os.path.dirname(__file__))
from graphique import (FONCTIONS_SUITE, JS_TRACE, PAGE, REFERENCES, VUES_SUITE, attendre_calme, calculer, centre, cliquer, doigts,
                       empreintes, jouer)
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

    def test_ec06_graduations_sans_point_decimal(self):
        if CHOISIS and "etude-complete" not in CHOISIS:
            self.skipTest("hors de OUTILS")
        with Navigateur() as nav:
            page = nav.ouvrir(PAGE, JS_TRACE)
            attendre_pret(page)
            etiquettes = page.evaluer("""(async () => {
                const { etiquette } = await import('/commun/graphique.js');
                return [0, 3, -2, 0.5, 2.25, -1.5, 0.54, 10.5, 1e-12, 0.004, 100.1].map(etiquette);
            })()""")
            self.assertEqual(etiquettes, ["0", "3", "-2", "0,5", "2,25", "-1,5", "0,54", "10,5", "0", "0", "100,1"])
            # sur le canvas : x^2*e^(-x) a un extremum en (2 ; 0,54) ; deux zooms avant donnent des graduations fractionnaires
            calculer(page, "x^2*e^(-x)")
            for _ in range(3):
                cliquer(page, "#zoomPlus")
                attendre_calme(page)
            textes = page.evaluer("window.__trace.filter(e => e[0] === 'fillText').map(e => String(e[1]))")
            self.assertTrue(textes)
            self.assertEqual([t for t in textes if re.search(r"\d\.\d", t)], [], "point décimal sur le graphique")
            self.assertTrue([t for t in textes if re.search(r"\d,\d", t)], "aucune virgule : la vérification serait vide")

    def test_ec05_un_doigt_defile_deux_doigts_deplacent_et_zooment(self):
        if CHOISIS and "etude-complete" not in CHOISIS:
            self.skipTest("hors de OUTILS")
        with Navigateur() as nav:
            page = nav.ouvrir(PAGE, JS_TRACE)
            attendre_pret(page)
            page.taille(360, 740)                                            # téléphone : la page est bien plus haute que la fenêtre
            calculer(page, "x^2*e^(-x)")
            attendre_calme(page)
            canvas = lambda champ: json.loads(page.evaluer(f"JSON.stringify(document.querySelector('#graphique').{champ})"))
            defilement = lambda: page.evaluer("scrollY")

            # 1. un doigt qui glisse sur le graphique fait défiler la page ; la courbe ne bouge pas
            c = centre(page)
            y0, vista0 = defilement(), canvas("__vista")
            doigts(page, [[(c["x"], c["y"] - 80 + 16 * k)] for k in range(11)], pause=0.03)
            time.sleep(0.5)
            self.assertLess(defilement(), y0 - 50, "un doigt doit faire défiler la page")
            self.assertEqual(canvas("__vista"), vista0, "un doigt ne doit pas déplacer la courbe")

            # 2. deux doigts : la courbe se déplace et zoome, la page ne défile pas, et le point de la courbe sous le milieu
            #    des doigts y reste, que le navigateur livre 3 ou 60 mouvements
            finaux = []
            for etapes in (3, 60):
                cliquer(page, "#zoomReset")
                attendre_calme(page)
                c = centre(page)
                gauche, haut = c["x"] - c["w"] / 2, c["y"] - c["h"] / 2
                r0, y0 = canvas("__rendu"), defilement()
                depart = [(c["x"] - 30, c["y"]), (c["x"] + 30, c["y"])]
                arrivee = [(c["x"] - 70, c["y"] - 20), (c["x"] + 50, c["y"] + 30)]
                images = [[(a[0] + (b[0] - a[0]) * k / etapes, a[1] + (b[1] - a[1]) * k / etapes) for a, b in zip(depart, arrivee)]
                          for k in range(etapes + 1)]
                doigts(page, images, pause=0.01)
                attendre_calme(page)
                r1 = canvas("__rendu")
                with self.subTest(mouvements=etapes):
                    self.assertEqual(defilement(), y0, "deux doigts ne doivent pas faire défiler la page")
                    milieu0 = (c["x"] - gauche, c["y"] - haut)                  # milieu des doigts au départ, dans le canvas
                    milieu1 = (c["x"] - 10 - gauche, c["y"] + 5 - haut)         # et à l'arrivée
                    x = lambda r, m: r["xmin"] + (m[0] - r["padL"]) / r["echelle"]
                    y = lambda r, m: r["ymin"] + (r["availH"] - (m[1] - r["padT"])) / r["echelle"]
                    self.assertAlmostEqual(x(r0, milieu0), x(r1, milieu1), delta=1e-6 * (r0["xmax"] - r0["xmin"]))
                    self.assertAlmostEqual(y(r0, milieu0), y(r1, milieu1), delta=1e-6 * (r0["ymax"] - r0["ymin"]))
                    self.assertAlmostEqual(r1["echelle"] / r0["echelle"], math.hypot(120, 50) / 60, delta=1e-6)
                finaux.append(canvas("__vista"))
            for champ in ("xmin", "xmax", "ymin", "ymax"):
                self.assertAlmostEqual(finaux[0][champ], finaux[1][champ], delta=1e-6 * abs(finaux[0]["xmax"] - finaux[0]["xmin"]),
                                       msg=f"la fenêtre finale ({champ}) dépend du nombre de mouvements")


if __name__ == "__main__":
    unittest.main()
