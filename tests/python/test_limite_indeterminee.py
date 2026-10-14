"""LA-03 : une limite que SymPy ne détermine pas (« ? ») n'est jamais enregistrée
comme asymptote, ni en ±∞ ni en un point ; l'étape correspondante le dit."""
import unittest
from unittest import mock

from moteurs import ensemble_def  # noqa: F401  (chemins + SymPy)
import limites_asymptotes as la

# couvre : ±∞ transcendant, valeur interdite à un côté (ln), aux deux côtés, pôle irrationnel
ENTREES = ["e^x", "e^(-x)", "x*e^x", "ln(x)/x", "x*ln(x)", "ln(x)", "ln(x^2)", "x/sqrt(x^2)",
           "(e^x-1)/x", "e^x/x", "e^(1/x)", "sqrt(x)", "(x^2-2)/(x^4-4)", "(x^2-2)/(x^2-2)", "ln(x+1)/(x-2)"]


def sans_sympy():
    return mock.patch.object(la, "_limite_sympy", return_value=None)


def valeurs(asymptote):
    return [v for v in asymptote.values() if isinstance(v, str)]


class TestLimiteIndeterminee(unittest.TestCase):
    def test_aucune_asymptote_issue_d_un_point_d_interrogation(self):
        for entree in ENTREES:
            with self.subTest(f=entree), sans_sympy():
                r = la.etudier(entree)
                self.assertTrue(r["ok"], r)
                for a in r["asymptotes"]:
                    self.assertFalse(any("?" in v for v in valeurs(a)), a)

    def test_la_conclusion_ne_pretend_pas_une_limite_finie(self):
        for entree in ENTREES:
            with self.subTest(f=entree), sans_sympy():
                r = la.etudier(entree)
                for etude in r["etudes"]:
                    for e in etude["etapes"]:
                        if "?" in e["html"]:
                            self.assertNotIn("limite est finie", e["html"], e["html"])
                            self.assertNotIn("se prolonge", e["html"], e["html"])

    def test_indetermine_est_signale(self):
        with sans_sympy():
            r = la.etudier("ln(x)/x")
        textes = " ".join(e["html"] for et in r["etudes"] for e in et["etapes"])
        self.assertIn("pas pu être déterminée", textes)


if __name__ == "__main__":
    unittest.main()
