"""Dérivée de u^α avec α constant irrationnel : α·u^(α−1)·u' (et non e^(α ln u))."""
import unittest

from moteurs import ensemble_def as ed, derivee_numerique, proches
import derivee_variations as dv
import oracle

CAS = ["x^(ln(2))", "x^(sqrt(2))", "x^(-ln(2))", "x^e", "x^(ln(3)-1)", "(x^2+1)^(sqrt(2))", "(x+1)^(ln(2))",
       "2*x^(sqrt(2))+x", "x^(sqrt(2))*ln(x)", "ln(x)/x^(ln(2))"]
POINTS = [0.37, 1.3, 2.9, 5.5]


class TestDeriveeExposantIrrationnel(unittest.TestCase):
    def test_derivee_juste(self):
        for entree in CAS:
            f = ed.lire(entree)
            fp = dv._simplifier(dv.derivee_narree(f, [], top=True))
            for t in POINTS:
                attendu = derivee_numerique(f, t)
                if attendu is None:
                    continue
                with self.subTest(f=entree, x=t):
                    obtenu = ed.evaluer(fp, t)
                    self.assertIsNotNone(obtenu)
                    self.assertTrue(proches(obtenu, attendu), f"f'({t}) = {obtenu}, attendu ≈ {attendu} ; f' = {ed.tex(fp)}")

    def test_regle_de_la_puissance_pas_exponentielle(self):
        for entree in ("x^(ln(2))", "x^(sqrt(2))", "(x^2+1)^(sqrt(2))"):
            r = dv.etudier(entree)
            textes = " ".join(e["html"] for e in r["deriv_etapes"])
            with self.subTest(f=entree):
                self.assertIn("règle de la puissance", textes + " ") if entree != "(x^2+1)^(sqrt(2))" else self.assertIn(r"\alpha\,u^{\alpha - 1}u'", textes)
                self.assertNotIn(r"e^{", textes)
                self.assertNotIn(r"\ln(x)", r["deriv_tex"])

    def test_formes(self):
        self.assertEqual(dv.etudier("x^(sqrt(2))")["deriv_tex"], r"\sqrt{2}\,x^{\sqrt{2} - 1}")
        self.assertEqual(dv.etudier("x^e")["deriv_tex"], r"e\,x^{e - 1}")

    def test_exposant_variable_inchange(self):
        r = dv.etudier("x^x")
        self.assertIn(r"s'écrit", " ".join(e["html"] for e in r["deriv_etapes"]))

    def test_f_prime_non_definie_en_zero_pour_alpha_inferieur_a_1(self):    # Q3 : double barre sur f', f(0) sur la ligne f
        r = dv.etudier("x^(ln(2))")
        L = {l["label"]: l["cells"] for l in r["table_signe"]["rows"]}
        self.assertEqual(L["f'(x)"], ["x", "||", "+"])
        self.assertEqual(L["f(x)"], ["x", "val:0", r"\nearrow"])
        self.assertEqual([(e["genre"], e["x_tex"]) for e in r["extrema"]], [("minimum local", "0")])

    def test_alpha_superieur_a_1_derivee_nulle_en_zero(self):
        r = dv.etudier("x^(sqrt(2))")
        L = {l["label"]: l["cells"] for l in r["table_signe"]["rows"]}
        self.assertEqual(L["f'(x)"], ["x", "0", "+"])
        self.assertEqual([(e["genre"], e["x_tex"]) for e in r["extrema"]], [("minimum local", "0")])

    def test_ordre_naturel_constante_en_dernier(self):
        """« ln 3 − 1 », jamais « −1 + ln 3 » : constantes positives avant négatives, après les termes en x."""
        r = dv.etudier("x^(ln(3)-1)")
        self.assertEqual(r["deriv_tex"], r"\frac{\ln(3) - 1}{x^{2 - \ln(3)}}")
        for entree in CAS + ["x^(ln(3)-1)", "x^(ln(3)-1)+x", "x^(ln(3)-2)*ln(x)", "(ln(3)-1)*x^2", "x^2+ln(2)-3"]:
            r = dv.etudier(entree)
            textes = [r.get("deriv_tex", "")] + [e["html"] for e in r.get("deriv_etapes", [])]
            for t in textes:
                with self.subTest(f=entree):
                    self.assertNotRegex(t, r"(?<![\w}])-\d+ \+ \\(ln|sqrt)", t)

    def test_conforme_oracle(self):
        for entree in CAS:
            res, arbre, ED = ed._analyser(entree)
            r = dv.etudier(entree)
            for e in r.get("extrema", []):
                with self.subTest(f=entree, x=e["x_tex"]):
                    self.assertTrue(oracle.definie(arbre, e["x_val"]))


if __name__ == "__main__":
    unittest.main()
