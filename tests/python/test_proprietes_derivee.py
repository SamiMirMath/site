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
        """DV-05 (sens direct) : chaque extremum intérieur annoncé est un point de l'ED où f' change
        de signe dans le bon sens ; en une borne fermée de l'ED (DV-09), le sens de variation de
        l'intervalle adjacent donne la nature ; la valeur annoncée est f(x)."""
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
                    maxi = e["genre"] == "maximum local"
                    if g is not None and dr is not None:   # extremum intérieur (i)
                        self.assertTrue(g > 0 > dr if maxi else g < 0 < dr, (g, dr))
                    elif g is None and dr is not None:      # borne fermée gauche de l'ED (ii, DV-09)
                        self.assertTrue(dr < 0 if maxi else dr > 0, dr)
                    elif dr is None and g is not None:      # borne fermée droite de l'ED (ii)
                        self.assertTrue(g > 0 if maxi else g < 0, g)
                    else:
                        self.fail("extremum sans intervalle adjacent dans l'ED")
                    self.assertLessEqual(abs(oracle.valeur(arbre, x) - e["f_val"]), 1e-9 * (1 + abs(e["f_val"])))

    def test_aucun_extremum_manque(self):
        """DV-04 (T06, bug n° 4 corrigé) : en un point de l'ED de f où f' n'est pas définie mais
        change de signe (√(x²) en 0, x^(2/3) en 0), l'extremum est annoncé."""
        for f in ["sqrt(x^2)", "x^(2/3)", "sqrt(x^2-2x+1)"]:
            r = dv.etudier(f)
            with self.subTest(f=f):
                self.assertTrue(any(abs(e["x_val"] - (1 if "2x" in f else 0)) < 1e-9 for e in r["extrema"]))


    # Critère (ii) de Q3 (tranché le 14.10.2026) : extremum local en toute borne fermée de l'ED,
    # nature donnée par le sens de variation sur l'intervalle adjacent (DV-09).
    BORNES_FERMEES = {
        "sqrt(x^2-4)": [("minimum local", -2, 0), ("minimum local", 2, 0)],
        "sqrt(4-x^2)": [("minimum local", -2, 0), ("maximum local", 0, 2), ("minimum local", 2, 0)],
        "sqrt(x)": [("minimum local", 0, 0)],
        "x*sqrt(x)": [("minimum local", 0, 0)],
        "-sqrt(x-1)": [("maximum local", 1, 0)],
    }

    def test_extrema_bornes_fermees(self):
        """DV-09 (T06) : un extremum local est annoncé en toute borne fermée de l'ED
        (±2 pour √(x²−4), 0 pour √x)."""
        for f, attendus in self.BORNES_FERMEES.items():
            r = dv.etudier(f)
            obtenus = sorted((e["genre"], round(e["x_val"], 9), round(e["f_val"], 9)) for e in r["extrema"])
            with self.subTest(f=f):
                self.assertEqual(obtenus, sorted((g, float(x), float(v)) for g, x, v in attendus))

    def test_pas_d_extremum_en_borne_ouverte(self):
        """Une borne ouverte de l'ED (ln x en 0, 1/x en 0) n'est jamais un extremum."""
        for f, borne in [("ln(x)", 0), ("x*ln(x)", 0), ("1/x", 0), ("ln(x)/x", 0)]:
            r = dv.etudier(f)
            with self.subTest(f=f):
                self.assertFalse(any(abs(e["x_val"] - borne) < 1e-9 for e in r["extrema"]))


if __name__ == "__main__":
    unittest.main()
