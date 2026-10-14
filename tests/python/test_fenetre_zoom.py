"""Bug : le graphique se figeait au dézoom (e^x sur [-10 ; 800] levait Incertain). EC-03."""
import unittest

import moteurs  # noqa: F401  (chemins des moteurs)
import etude_complete as ec

FENETRES = [("e^x", -10, 800), ("e^(-x)", -1000, 10), ("x^2*e^(-x)", -2000, 2000)]


class TestFenetreDezoom(unittest.TestCase):
    def test_fenetres_larges_reussissent(self):
        for entree, xmin, xmax in FENETRES:
            with self.subTest(f=entree, xmin=xmin, xmax=xmax):
                r = ec.fenetre(entree, xmin, xmax)
                self.assertTrue(r["ok"], r)
                self.assertTrue(r["segments"])

    def test_points_non_calculables_omis(self):
        r = ec.fenetre("e^x", -10, 800)
        pts = [p for seg in r["segments"] for p in seg]
        self.assertTrue(any(v is None for _, v in pts), "les points hors flottants doivent valoir None")
        self.assertTrue(any(v is not None for _, v in pts), "les points calculables sont conservés")

    def test_fenetre_json_ne_leve_pas(self):
        import json
        r = json.loads(ec.fenetre_json(json.dumps({"f": "e^x", "xmin": -10, "xmax": 800})))
        self.assertTrue(r["ok"])


if __name__ == "__main__":
    unittest.main()
