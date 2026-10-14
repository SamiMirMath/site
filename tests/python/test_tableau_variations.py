"""T06 / T06b : tableau de variations (Q3, 14.10.2026) — ED de f', double barre sur f',
valeur de f sans barre, extrema (i) et (ii), fonction constante."""
import unittest

from moteurs import ensemble_def as ed
import derivee_variations as dv


def lignes(entree):
    r = dv.etudier(entree)
    assert r["signe_resolu"], r
    t = r["table_signe"]
    return r, t, {l["label"]: l["cells"] for l in t["rows"]}


class TestEDdeFPrime(unittest.TestCase):
    def test_etape_ed_de_f_prime(self):  # DV-03
        for entree in ["sqrt(x^2-4)", "sqrt(x)", "sqrt(x^2)", "x^(2/3)", "sqrt(4-x^2)"]:
            with self.subTest(f=entree):
                r = dv.etudier(entree)
                f = ed.lire(entree)
                attendu = ed.ens_tex(ed.inter(ed._analyser(entree)[2], ed.domaine(
                    dv._simplifier(dv.derivee_narree(f, [], top=True)))))
                self.assertEqual(r["ed_deriv_tex"], attendu)
                etapes = [e["html"] for e in r["signe_etapes"] if "html" in e]
                self.assertTrue(any(h.startswith("ED de f'") and attendu in h for h in etapes), etapes)

    def test_pas_d_etape_si_meme_ed(self):
        for entree in ["x^3", "x^2-4x+3", "ln(x)"]:
            with self.subTest(f=entree):
                r = dv.etudier(entree)
                self.assertNotIn("ed_deriv_tex", r)
                self.assertFalse(any(h.get("html", "").startswith("ED de f'") for h in r["signe_etapes"]))


class TestTableauQ3(unittest.TestCase):
    def test_racine_x2_moins_4(self):  # DV-10
        r, t, L = lignes("sqrt(x^2-4)")
        self.assertEqual(t["crit"], ["-2", "2"])
        self.assertEqual(L["f'(x)"][1], "||")
        self.assertEqual(L["f'(x)"][3], "||")
        self.assertEqual(L["f(x)"][1], "val:0")     # valeur f(−2) = 0, sans barre
        self.assertEqual(L["f(x)"][3], "val:0")
        self.assertEqual([(e["genre"], e["x_tex"], e["f_tex"]) for e in r["extrema"]],
                         [("minimum local", "-2", "0"), ("minimum local", "2", "0")])

    def test_extremum_interieur_sans_derivee(self):  # DV-04
        for entree, genre in [("sqrt(x^2)", "minimum local"), ("x^(2/3)", "minimum local")]:
            with self.subTest(f=entree):
                r, _, L = lignes(entree)
                self.assertEqual(L["f'(x)"][1], "||")
                self.assertEqual(L["f(x)"][1], "val:0")
                self.assertEqual([(e["genre"], e["x_tex"]) for e in r["extrema"]], [(genre, "0")])

    def test_point_sans_derivee_sans_changement_de_signe(self):
        r, _, L = lignes("x^(1/3)")        # f' > 0 de part et d'autre de 0
        self.assertEqual(r["extrema"], [])
        self.assertEqual(L["f(x)"], [r"\nearrow", "val:0", r"\nearrow"])

    def test_borne_ouverte_sans_extremum_barre(self):
        r, _, L = lignes("ln(x)")
        self.assertEqual(r["extrema"], [])
        self.assertEqual(L["f(x)"][1], "asym")     # f non définie en 0 : double barre

    def test_zero_isole_de_f_prime(self):  # x³ : 0 dans la colonne de 0, ↗ ↗, aucun extremum
        r, _, L = lignes("x^3")
        self.assertEqual(L["f'(x)"], ["+", "0", "+"])
        self.assertEqual(L["f(x)"], [r"\nearrow", "", r"\nearrow"])
        self.assertEqual(r["extrema"], [])
        self.assertNotIn("f_constante", r)


class TestFonctionConstante(unittest.TestCase):
    def test_constante_sur_R(self):  # x^(2-2)
        r, t, L = lignes("x^(2-2)")
        self.assertEqual(L["f'(x)"], ["0"])
        self.assertEqual(L["f(x)"], [r"\rightarrow"])
        self.assertEqual(r["extrema"], [])
        self.assertTrue(r["f_constante"])

    def test_constante_par_morceaux(self):  # √(x²)/x : −1 pour x < 0, 1 pour x > 0
        r, _, L = lignes("sqrt(x^2)/x")
        self.assertEqual(L["f'(x)"], ["0", "||", "0"])
        self.assertEqual(L["f(x)"], [r"\rightarrow", "asym", r"\rightarrow"])
        self.assertEqual(r["extrema"], [])

    def test_constante_hors_ed_barree(self):  # ln(x²) − 2 ln(x), ED = ]0 ; +∞[
        r, _, L = lignes("ln(x^2)-2ln(x)")
        self.assertEqual(L["f'(x)"], ["x", "||", "0"])
        self.assertEqual(L["f(x)"], ["", "asym", r"\rightarrow"])
        self.assertEqual(r["extrema"], [])

    def test_valeur_constante_a_la_borne_dans_l_ed(self):
        # f = (√x)⁰ : ED = [0 ; +∞[ (bord fermé), f ≡ 1.
        r, _, L = lignes("sqrt(x)^0")
        self.assertEqual(r["extrema"], [])
        self.assertTrue(r["f_constante"])
        self.assertEqual(L["f(x)"][1], "val:1")
        self.assertEqual(L["f(x)"][2], r"\rightarrow")


if __name__ == "__main__":
    unittest.main()
