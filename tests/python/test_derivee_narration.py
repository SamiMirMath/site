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


if __name__ == "__main__":
    unittest.main()
