"""C5 : ED de x^α pour un exposant constant α (règle validée le 14.10.2026)."""
import unittest

from moteurs import ensemble_def as ed
import derivee_variations as dv
import oracle

R = r"\mathbb{R}"
RSTAR = r"\mathbb{R} \setminus \left\{0\right\}"
POS0 = r"\left[0 \,;\, +\infty\right["      # [0 ; +∞[
POS = r"\left]0 \,;\, +\infty\right["        # ]0 ; +∞[

REGLE = [
    # α = 0 : ℝ ; entier ≥ 1 : ℝ ; entier ≤ −1 : ℝ*
    ("x^0", R), ("x^1", R), ("x^3", R), ("x^(-1)", RSTAR), ("x^(-3)", RSTAR),
    # p/q irréductible, q impair : ℝ (ℝ* si α < 0)
    ("x^(1/3)", R), ("x^(2/3)", R), ("x^(4/3)", R), ("x^(-1/3)", RSTAR), ("x^(-2/3)", RSTAR),
    # p/q, q pair : [0 ; +∞[ si α > 0, ]0 ; +∞[ si α < 0
    ("x^(1/2)", POS0), ("x^(3/2)", POS0), ("x^(1/4)", POS0), ("x^(-1/2)", POS), ("x^(-3/2)", POS),
    # α irrationnel : [0 ; +∞[ si α > 0, ]0 ; +∞[ si α < 0
    ("x^(ln(2))", POS0), ("x^(sqrt(2))", POS0), ("x^e", POS0), ("x^(ln(3)-1)", POS0),
    ("x^(-ln(2))", POS), ("x^(-sqrt(2))", POS), ("x^(1-ln(3))", POS),
    # exposant constant qui vaut un rationnel sans le montrer
    ("x^(ln(4)-2ln(2))", R), ("x^(2ln(2)-ln(4))", R), ("x^(ln(4)-2*ln(2)+1)", R),
    ("x^(ln(2)/ln(4))", POS0), ("x^(ln(8)/ln(2))", R), ("x^(-ln(8)/ln(2))", RSTAR), ("x^(sqrt(2)*sqrt(2)-2)", R),
    # exposant variable : base > 0
    ("x^x", POS),
]


class TestEDdePuissance(unittest.TestCase):
    def test_regle(self):
        for entree, attendu in REGLE:
            with self.subTest(f=entree):
                res = ed.analyser(entree)
                self.assertTrue(res["complet"], res)
                self.assertEqual(res["ED_tex"], attendu)

    def test_base_affine(self):
        self.assertEqual(ed.analyser("(x-1)^(sqrt(2))")["ED_tex"], r"\left[1 \,;\, +\infty\right[")
        self.assertEqual(ed.analyser("(x-1)^(-sqrt(2))")["ED_tex"], r"\left]1 \,;\, +\infty\right[")

    def test_conforme_oracle_haute_precision(self):
        grille = [-30, -8, -2.5, -1, -0.5, -1e-3, 0, 1e-3, 0.5, 1, 1.5, 2.5, 8, 30]
        for entree, _ in REGLE:
            res, arbre, ED = ed._analyser(entree)
            for x in grille:
                with self.subTest(f=entree, x=x):
                    self.assertEqual(oracle.definie(arbre, x), ed.contient(ED, x), res["ED_tex"])

    def test_controle_numerique_d_accord(self):
        for entree, _ in REGLE:
            with self.subTest(f=entree):
                self.assertTrue(ed.verifier(entree)["accord"])


class TestExposantSimplifie(unittest.TestCase):
    def test_normalisation_et_saisie(self):
        res = ed.analyser("x^(ln(4)-2ln(2))")
        self.assertEqual(res["f_tex"], "x^{0}")
        self.assertEqual(res["f_saisie_tex"], r"x^{\ln(4) - 2\ln(2)}")     # la saisie reste montrée
        self.assertEqual(res["conditions"], [])

    def test_exposant_irrationnel_a_une_condition_dediee(self):
        res = ed.analyser("x^(ln(2))")
        puiss = [c for c in res["conditions"] if c["genre"] in ("pos", "pos0")]
        self.assertEqual([c["genre"] for c in puiss], ["pos0"])
        self.assertEqual(puiss[0]["cond_tex"], r"x \geq 0")
        res = ed.analyser("x^(-ln(2))")
        self.assertEqual([c["genre"] for c in res["conditions"] if c["genre"] in ("pos", "pos0")], ["pos"])

    def test_indecidable_garde_le_comportement_prudent(self):
        # exposant non constant ou dont la nullité n'est pas démontrable : x > 0
        self.assertEqual(ed.classer_exposant(ed.lire("x^x").b), None)

    def test_derivee_d_une_puissance_simplifiee(self):
        r = dv.etudier("x^(ln(4)-2ln(2))")                 # x^0 = 1 : constante
        self.assertEqual(r["deriv_tex"], "0")
        self.assertTrue(r.get("f_constante"))

    def test_sans_sympy_comportement_prudent(self):
        from unittest import mock
        with mock.patch.object(ed, "_sympy", return_value=None), mock.patch.dict(ed._CLASSES_EXPOSANT, clear=True):
            res = ed.analyser("x^(ln(4)-2ln(2))")
            self.assertEqual(res["ED_tex"], POS)           # prudent : ]0 ; +∞[
            self.assertTrue(res["besoin_sympy"])           # la page recharge avec SymPy


if __name__ == "__main__":
    unittest.main()
