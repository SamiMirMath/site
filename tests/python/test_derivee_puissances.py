"""Bug : dérivée de x^(p/q) fausse (fraction mal transmise à SymPy, en_py)."""
import unittest

from moteurs import ensemble_def as ed, derivee_numerique, proches
from fractions import Fraction as F
import derivee_variations as dv


def derivee_outil(entree):
    f = ed.lire(entree)
    fp = dv._simplifier(dv.derivee_narree(f, [], top=True))
    return f, fp


class TestPontSympyFractions(unittest.TestCase):
    def test_exposant_fraction(self):
        sp = ed._sympy()
        x = ed._SP["x"]
        self.assertEqual(ed.en_sympy(ed.Op("^", ed.X(), ed.Nb(F(1, 2)))), sp.sqrt(x))
        self.assertEqual(ed.en_sympy(ed.Op("^", ed.X(), ed.Nb(F(-1, 3)))), x ** sp.Rational(-1, 3))

    def test_diviseur_fraction(self):
        x = ed._SP["x"]
        self.assertEqual(ed.en_sympy(ed.Op("/", ed.X(), ed.Nb(F(1, 3)))), 3 * x)


class TestDeriveePuissancesFractionnaires(unittest.TestCase):
    CAS = ["x^(1/2)", "x^(3/2)", "x^(2/3)", "x^(-1/2)", "(x^2+1)^(1/2)", "x^0,5",
           "(x-1)^(5/2)", "x^(1/3)+x", "x^(3/2)/(x+1)",
           "x^(1/3)", "x^(-1/3)", "x^(4/3)", "(x-2)^(1/3)", "x*x^(1/3)"]
    POINTS = [0.37, 1.3, 2.9, 5.5, -0.37, -1.3, -2.9, -5.5]   # négatifs : racine réelle (q impair)

    def test_derivee_juste(self):
        for entree in self.CAS:
            f, fp = derivee_outil(entree)
            for t in self.POINTS:
                attendu = derivee_numerique(f, t)
                obtenu = ed.evaluer(fp, t)
                if attendu is None:
                    continue
                with self.subTest(f=entree, x=t):
                    self.assertIsNotNone(obtenu)
                    self.assertTrue(proches(obtenu, attendu),
                                    f"f'({t}) = {obtenu}, attendu ≈ {attendu} ; f' = {ed.tex(fp)}")


if __name__ == "__main__":
    unittest.main()
