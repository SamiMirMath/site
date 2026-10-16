"""Bug : les étapes de la dérivée annonçaient « f'(x) = … » pour un morceau de f
(produit sous un facteur constant, terme d'une somme, signe moins devant) ;
la ligne contredisait alors le résultat final."""
import unittest

from moteurs import ensemble_def as ed, derivee_numerique, proches
import derivee_variations as dv

DEBUT = r"\(f'(x) = "
FIN = r"\)."

CAS = ["3(x*ln(x))", "-(x*ln(x))", "(x+1)/(x-1)/2", "(x*ln(x))*3", "x*ln(x)+x",
       "2(x^2+ln(x))", "-x^2", "3x^2-4x", "x*ln(x)", "(x^2-1)/(x-3)", "x^2-4x+3",
       "x^2*e^(-x)-x/(x^2+1)", "-(x^2-1)/(x-3)", "1/2*sqrt(x)*ln(x)"]


class TestNarrationDerivee(unittest.TestCase):
    def test_lignes_f_prime_egales_au_resultat(self):
        for entree in CAS:
            r = dv.etudier(entree)
            self.assertTrue(r["ok"] and r["deriv_resolu"], entree)
            for it in r["deriv_etapes"]:
                h = it["html"]
                if h.startswith(DEBUT):
                    with self.subTest(f=entree, ligne=h):
                        self.assertTrue(h.endswith(FIN))
                        self.assertEqual(h[:-len(FIN)].rsplit(" = ", 1)[1], r["deriv_tex"])

    def test_resultat_juste(self):
        for entree in CAS:
            f = ed.lire(entree)
            fp = dv._simplifier(dv.derivee_narree(f, [], top=True))
            for t in (0.7, 1.9, 4.3):
                attendu = derivee_numerique(f, t)
                if attendu is None:
                    continue
                with self.subTest(f=entree, x=t):
                    self.assertTrue(proches(ed.evaluer(fp, t), attendu))


class TestSansOperationNeutre(unittest.TestCase):
    """Guide R11 : jamais de « + 0 », « - 0 », « · 1 », « / 1 » dans les étapes (u'(x) = 8x, pas 8x + 0)."""
    ENTREES = CAS + ["sqrt(4x^2+1)/(x+2)", "ln(x^2+1)/x", "(x^3+2x)^4*e^x", "sqrt(x^2-3x+2)", "(2x+1)/(x^2+1)",
                     "e^(x^2+1)", "ln(x^2+1)", "(x^2+1)^3", "x/(x^2+4)", "sqrt(x^2+1)*e^x", "x^(1/3)*(x^2+1)"]

    def test_aucune_operation_neutre(self):
        import re
        motif = re.compile(r"(?:[+-] 0(?![\d.,{])|\\cdot 1(?![\d.,{])|\\frac\{[^{}]*\}\{1\}|\\dfrac\{[^{}]*\}\{1\})")
        for entree in self.ENTREES:
            r = dv.etudier(entree)
            for it in r["deriv_etapes"]:
                with self.subTest(f=entree, ligne=it["html"]):
                    self.assertIsNone(motif.search(it["html"]), it["html"])

    def test_derivee_interne_sans_zero(self):
        h = " ".join(it["html"] for it in dv.etudier("sqrt(4x^2+1)/(x+2)")["deriv_etapes"])
        self.assertIn(r"u'(x) = 8x\)", h)
        self.assertNotIn("8x + 0", h)

    def test_justification_d_une_derivee_de_reference_presente(self):
        """Guide R11 : les justifications restent TOUJOURS (les élèves les oublient)."""
        def etapes(entree):
            return " ".join(it["html"] for it in dv.etudier(entree)["deriv_etapes"])
        self.assertIn(r"\(\left(x^{2}\right)' = 2x\) (règle de la puissance)", etapes("x^2*ln(x)"))
        self.assertIn(r"\(\left(x^{3}\right)' = 3x^{2}\) (règle de la puissance)", etapes("(x^3+2x)^4*e^x"))
        self.assertIn(r"\(\left(\ln(x)\right)' = \frac{1}{x}\) (règle de base)", etapes("x^2*ln(x)"))
        self.assertIn(r"\(\left(e^{x}\right)' = e^{x}\) (règle de base)", etapes("(x^3+2x)^4*e^x"))
        self.assertIn("règle du quotient", etapes("sqrt(4x^2+1)/(x+2)"))
        self.assertIn("règle du produit", etapes("x^2*ln(x)"))
        self.assertIn(r"est de la forme \(\sqrt{u}\)", etapes("sqrt(4x^2+1)/(x+2)"))

    def test_pas_de_den_dans_les_libelles_du_tableau(self):
        for entree in ("sqrt(4x^2+1)/(x+2)", "(2x+1)/(x^2+1)", "ln(x^2+1)/x"):
            for ligne in dv.etudier(entree)["table_signe"]["rows"]:
                with self.subTest(f=entree, ligne=ligne["label"]):
                    self.assertNotIn("dén", ligne["label"])


if __name__ == "__main__":
    unittest.main()
