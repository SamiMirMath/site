"""T02 — Dérivée, signe, variations : propriétés vérifiées par l'oracle haute précision
(critères DV-01, DV-02, DV-05 de docs/specifications/derivee-variations.md)."""
import unittest

import mpmath

from moteurs import ensemble_def as ed
import derivee_variations as dv
import oracle
from generateurs import fonctions

mp = mpmath.mp

MAIN = [
    # polynômes
    "x^2-4x+3", "x^3-3x", "x^4-2x^2", "(x-1)^3", "-x^2+6x-5", "2x^3-9x^2+12x", "x^5-5x", "3x^2-4x",
    "-(x^3-3x)", "1/2*x^2-x", "(x^2-1)^2", "x^3",
    # rationnelles
    "(x^2-1)/(x-3)", "x/(x^2+1)", "1/(x^2+1)", "(x+1)/(x-1)", "(x^2+1)/x", "x^2/(x-1)", "1/x^2",
    "(2x-1)/(x+2)/3", "(x^2-4)/(x^2-1)", "-(x^2-1)/(x-3)", "x+1/x", "(x^3+1)/(x^2-4)",
    # puissances fractionnaires et racines
    "x^(1/2)", "x^(3/2)", "x^(2/3)", "x^(-1/2)", "(x^2+1)^(1/2)", "x^0,5", "(x-1)^(5/2)", "x^(1/3)+x",
    "sqrt(x^2-4x+5)", "sqrt(x^2-4)", "x*sqrt(x)", "sqrt(x)/(x+1)", "1/sqrt(x^2+1)", "sqrt(4-x^2)",
    # ln
    "x*ln(x)", "ln(x)/x", "ln(x^2-4)", "ln(x^2+1)", "x-ln(x)", "ln(x)^2", "(ln(x))^2-ln(x)",
    "3(x*ln(x))", "-(x*ln(x))", "x*ln(x)+x", "2(x^2+ln(x))", "ln((x-1)/(x+1))", "x^2*ln(x)", "1/ln(x)",
    # exp
    "e^(2x)", "x^2*e^(-x)", "x*e^x", "e^(x^2)", "e^x/x", "(x-1)*e^x", "e^(-x^2)", "e^x-x",
    "x^2*e^(-x)-x/(x^2+1)", "e^(1/x)", "(e^x-1)/(e^x+1)",
    # mélanges
    "1/2*sqrt(x)*ln(x)", "sqrt(x)*e^(-x)", "ln(x)*e^x", "x^x", "(x+1)/(x-1)/2", "(x*ln(x))*3", "-x^2",
]
N_GENERES = 120
POINTS = [-3.71, -1.93, -0.62, 0.37, 0.81, 1.47, 2.59, 4.33, 6.85]


def derivee_moteur(f_arbre):
    return dv._simplifier(dv.derivee_narree(f_arbre, [], top=True))


def cas():
    return MAIN + [f for f in fonctions(N_GENERES, graine=11) if "ln(" in f or "e^" in f or "/" in f]


class TestProprietesDerivee(unittest.TestCase):
    def test_derivee_conforme_oracle(self):
        """DV-01 : f' du moteur = dérivée numérique haute précision de f (points de l'ED)."""
        for f in cas():
            arbre = ed.lire(f)
            fp = derivee_moteur(arbre)
            testes = 0
            for x in POINTS:
                attendu = oracle.derivee(arbre, x)
                if attendu is None or oracle.valeur(fp, x) is None:
                    continue
                testes += 1
                with self.subTest(f=f, x=x):
                    obtenu = oracle.valeur(fp, x)
                    self.assertLessEqual(abs(obtenu - attendu), mp.mpf("1e-12") * (1 + abs(attendu)),
                                         f"f' = {ed.tex(fp)}")
            if f in MAIN:   # une fonction générée peut avoir un ED vide ou hors de la grille
                with self.subTest(f=f):
                    self.assertGreater(testes, 0, "aucun point de test dans l'ED")

    def test_narration_f_prime_coherente(self):
        """DV-02 : toute ligne « f'(x) = … » se termine par le résultat final."""
        for f in MAIN:
            r = dv.etudier(f)
            self.assertTrue(r["ok"] and r["deriv_resolu"], f)
            for it in r["deriv_etapes"]:
                h = it["html"]
                if h.startswith(r"\(f'(x) = "):
                    with self.subTest(f=f, ligne=h):
                        self.assertEqual(h[:-len(r"\).")].rsplit(" = ", 1)[1], r["deriv_tex"])

    def test_extrema_annonces_justes(self):
        """DV-05 (sens direct) : chaque extremum annoncé est un point de l'ED où f' change de
        signe dans le bon sens, et la valeur annoncée est f(x)."""
        for f in MAIN:
            r = dv.etudier(f)
            if not r.get("signe_resolu"):
                continue
            arbre = ed.lire(f)
            for e in r["extrema"]:
                x = e["x_val"]
                d = 1e-6 * (1 + abs(x))
                with self.subTest(f=f, extremum=e["x_tex"]):
                    self.assertTrue(oracle.definie(arbre, x))
                    g, dr = oracle.derivee(arbre, x - d), oracle.derivee(arbre, x + d)
                    self.assertIsNotNone(g)
                    self.assertIsNotNone(dr)
                    if e["genre"] == "maximum local":
                        self.assertTrue(g > 0 > dr, (g, dr))
                    else:
                        self.assertTrue(g < 0 < dr, (g, dr))
                    self.assertLessEqual(abs(oracle.valeur(arbre, x) - e["f_val"]), 1e-9 * (1 + abs(e["f_val"])))

    @unittest.expectedFailure
    def test_aucun_extremum_manque(self):
        """BUG CONNU n° 4 (tâche T06) : en un point de l'ED de f où f' n'est pas définie mais
        change de signe (√(x²) en 0, x^(2/3) en 0), l'extremum n'est pas annoncé.
        Quand ce test passera, retirer @expectedFailure."""
        for f in ["sqrt(x^2)", "x^(2/3)", "sqrt(x^2-2x+1)"]:
            r = dv.etudier(f)
            with self.subTest(f=f):
                self.assertTrue(any(abs(e["x_val"] - (1 if "2x" in f else 0)) < 1e-9 for e in r["extrema"]))


if __name__ == "__main__":
    unittest.main()
