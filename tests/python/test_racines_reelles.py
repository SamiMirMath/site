"""C1 : x^(p/q), q impair, est défini sur ℝ (racine réelle) ; SymPy le lit dans ℂ pour x < 0.
Le pont SymPy d'analyse écrit real_root(u, q)**p ; les résultats doivent être justes sur ℝ."""
import json
import unittest
from fractions import Fraction as F

from moteurs import ensemble_def as ed
import derivee_variations as dv
import limites_asymptotes as la
import etude_complete as ec
import oracle

CAS = ["x^(1/3)", "x^(2/3)", "x^(-1/3)", "x^(4/3)", "(x-2)^(1/3)", "x*x^(1/3)"]
GRILLE = [-30, -8, -2.5, -1, -0.5, -0.01, 0.01, 0.5, 1, 2.5, 8, 30]


class TestPontReel(unittest.TestCase):
    def test_ecriture_real_root(self):
        f = ed.lire("x^(2/3)")
        self.assertIn("real_root(x, 3)", ed.en_py(f, reel=True))
        self.assertNotIn("real_root", ed.en_py(f))            # le pont formel (factor) ne change pas
        self.assertNotIn("real_root", ed.en_py(ed.lire("x^(1/2)"), reel=True))   # q pair : inchangé
        self.assertNotIn("real_root", ed.en_py(ed.lire("x^3"), reel=True))

    def test_valeur_sympy_negative_reelle(self):
        sp = ed._sympy()
        for entree in CAS:
            f = ed.lire(entree)
            for x in (-8, -2, -27):
                attendu = oracle.valeur(f, x)
                if attendu is None:
                    continue
                with self.subTest(f=entree, x=x):
                    v = ed.en_sympy_reel(f).subs(ed._SP["x"], x)
                    self.assertTrue(v.is_real, v)
                    self.assertAlmostEqual(float(sp.N(v)), float(attendu), places=9)

    def test_ed_conforme_oracle(self):
        for entree in CAS:
            res, arbre, ED = ed._analyser(entree)
            with self.subTest(f=entree):
                for x in GRILLE:
                    self.assertEqual(oracle.definie(arbre, x), ed.contient(ED, x), x)

    def test_pas_de_nombre_complexe_dans_les_sorties(self):
        for entree in CAS:
            for sortie in (la.etudier_json(entree), dv.etudier_json(entree), ec.etudier_json(entree)):
                with self.subTest(f=entree):
                    self.assertNotIn("(-1)", sortie)
                    json.loads(sortie)


class TestLimitesReelles(unittest.TestCase):
    def finies(self, entree):
        r = la.etudier(entree)
        return [(e["ou"], e["etapes"][-1]["html"]) for e in r["etudes"]], r["asymptotes"]

    def test_x_puissance_2_sur_3(self):
        etudes, asym = self.finies("x^(2/3)")
        self.assertEqual(asym, [])
        self.assertTrue(all("+\\infty" in h for _, h in etudes))

    def test_x_puissance_1_sur_3(self):
        etudes, asym = self.finies("x^(1/3)")
        self.assertEqual(asym, [])
        self.assertIn("-\\infty", etudes[0][1])
        self.assertIn("+\\infty", etudes[1][1])

    def test_x_puissance_moins_1_sur_3(self):
        _, asym = self.finies("x^(-1/3)")
        genres = sorted((a["genre"], a.get("ou")) for a in asym)
        self.assertIn(("verticale", "x \\to 0"), genres)
        self.assertEqual(sum(1 for g, _ in genres if g == "horizontale"), 2)

    def test_limite_en_un_point_negatif(self):
        """(x+2)^(1/3) en −2 : valeur interdite inexistante ; f(−2) = 0 ; limite en −∞ : −∞."""
        etudes, asym = self.finies("(x+2)^(1/3)")
        self.assertEqual(asym, [])
        self.assertIn("-\\infty", etudes[0][1])


class TestSigneEtVariations(unittest.TestCase):
    def test_x_puissance_2_sur_3(self):
        r = dv.etudier("x^(2/3)")
        L = {l["label"]: l["cells"] for l in r["table_signe"]["rows"]}
        self.assertEqual(L["f'(x)"], ["-", "||", "+"])
        self.assertEqual(L["f(x)"], [r"\searrow", "val:0", r"\nearrow"])
        self.assertEqual([(e["genre"], e["x_tex"]) for e in r["extrema"]], [("minimum local", "0")])

    def test_x_puissance_1_sur_3(self):
        r = dv.etudier("x^(1/3)")
        L = {l["label"]: l["cells"] for l in r["table_signe"]["rows"]}
        self.assertEqual(L["f'(x)"], ["+", "||", "+"])
        self.assertEqual(L["f(x)"], [r"\nearrow", "val:0", r"\nearrow"])
        self.assertEqual(r["extrema"], [])

    def test_x_puissance_4_sur_3(self):
        r = dv.etudier("x^(4/3)")
        self.assertEqual([(e["genre"], e["x_tex"]) for e in r["extrema"]], [("minimum local", "0")])

    def test_x_puissance_3_sur_2_minimum_en_0(self):   # Q3 (ii), borne fermée de l'ED
        r = dv.etudier("x^(3/2)")
        self.assertEqual([(e["genre"], e["x_tex"], e["f_tex"]) for e in r["extrema"]],
                         [("minimum local", "0", "0")])


if __name__ == "__main__":
    unittest.main()
