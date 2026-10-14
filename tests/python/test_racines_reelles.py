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


class TestRacinesExactes(unittest.TestCase):
    """C2 : x^(p/q) = (racine q-ième de x)^p est traité par les méthodes du cours, sans calcul formel."""

    def textes(self, entree):
        r = dv.etudier(entree)
        return " ".join(e.get("html", "") for e in r["deriv_etapes"] + r["signe_etapes"])

    def test_aucune_phrase_de_calcul_formel_pour_une_racine(self):
        for entree in CAS + ["x^(3/2)", "x^(-3/2)", "x^(1/4)", "(x-1)^(2/3)", "x^(5/3)"]:
            with self.subTest(f=entree):
                t = self.textes(entree)
                for mot in ("calcul formel", "transcend", "SymPy"):
                    self.assertNotIn(mot, t)

    def test_zero_et_valeur_interdite_ne_sont_pas_confondus(self):
        t = self.textes("x^(2/3)")                       # f' = 2/(3∛x) : le numérateur ne s'annule jamais
        self.assertIn("Le numérateur vaut", t)
        self.assertIn("aucune solution", t)
        self.assertNotIn("= 0 \\iff x", t)               # on ne résout pas ∛x = 0 comme un zéro de f'
        r = dv.etudier("x^(2/3)")
        self.assertEqual(r["domaine_etude_tex"], ed.ens_tex(ed.inter(ed.REELS, ed.complement(ed.points([ed.Num.rat(0)])))))

    def test_racine_cubique_quand_le_numerateur_s_annule(self):
        t = self.textes("x^(4/3)")                       # f' = (4/3)∛x : zéro en 0
        self.assertIn(r"\sqrt[3]{x} = 0 \iff x = 0", t)

    def test_ecriture_en_racines(self):
        self.assertEqual(ed.tex(ed.lire("x^(1/3)")), r"\sqrt[3]{x}")
        self.assertEqual(ed.tex(ed.lire("x^(2/3)")), r"\sqrt[3]{x^{2}}")
        self.assertEqual(ed.tex(ed.lire("x^(1/4)")), r"\sqrt[4]{x}")
        self.assertEqual(ed.tex(ed.lire("x^(3/2)")), r"\sqrt{x^{3}}")
        self.assertEqual(ed.tex(ed.lire("x^(5/3)")), r"\sqrt[3]{x^{5}}")
        self.assertEqual(ed.tex(ed.lire("x^(-1/3)")), r"x^{\frac{-1}{3}}")   # inchangé (exposant négatif)

    def test_aplatir_u_puissance_p_sur_q(self):
        c, facs = ed.aplatir(ed.lire("x^(2/3)"))
        self.assertEqual((c, [(ed.tex(h), k) for h, k in facs]), (F(1), [(r"\sqrt[3]{x}", 2)]))
        c, facs = ed.aplatir(ed.lire("x^(-4/3)"))
        self.assertEqual([(ed.tex(h), k) for h, k in facs], [(r"\sqrt[3]{x}", -4)])

    def test_ed_et_signe_des_racines_q_impaires_sont_exacts(self):
        for entree in ("x^(1/3)", "x^(5/3)", "(x-2)^(1/3)", "x^(1/5)"):
            with self.subTest(f=entree):
                res = ed.analyser(entree)
                self.assertTrue(res["complet"])
                self.assertEqual(res["ED_tex"], r"\mathbb{R}")
        res = ed.analyser("1/x^(1/3)")
        self.assertEqual(res["ED_tex"], r"\mathbb{R} \setminus \left\{0\right\}")
        self.assertFalse(res["besoin_sympy"])


class TestDeriveeEnQuotient(unittest.TestCase):
    """C3 : f' écrite en un quotient numérateur / dénominateur (DV-07)."""
    ATTENDU = {
        "x^(2/3)": r"\frac{2}{3\sqrt[3]{x}}",
        "x^(1/3)": r"\frac{1}{3\sqrt[3]{x^{2}}}",
        "x^(-1/3)": r"\frac{-1}{3\sqrt[3]{x^{4}}}",
        "x^(4/3)": r"\frac{4\sqrt[3]{x}}{3}",
        "x^(1/2)": r"\frac{1}{2\sqrt{x}}",
        "x^(3/2)": r"\frac{3\sqrt{x}}{2}",
        "x^(-1/2)": r"\frac{-1}{2\sqrt{x^{3}}}",
        "sqrt(x^2)": r"\frac{x}{\sqrt{x^{2}}}",
        "x^3": "3x^{2}",                       # entier : inchangé
        "(x^2-1)/(x-3)": r"\frac{x^{2} - 6x + 1}{\left(x - 3\right)^{2}}",
    }

    def test_forme_attendue(self):
        for entree, tex in self.ATTENDU.items():
            with self.subTest(f=entree):
                self.assertEqual(dv.etudier(entree)["deriv_tex"], tex)

    def test_aucune_fraction_imbriquee(self):
        for entree in list(self.ATTENDU) + ["x^(5/3)", "x^(-5/3)", "x^(1/3)+x^(2/3)", "(x-1)^(5/2)"]:
            r = dv.etudier(entree)
            with self.subTest(f=entree):
                self.assertNotIn(r"\frac{\frac", r["deriv_tex"])
                for e in r["deriv_etapes"]:
                    self.assertNotIn(r"\frac{\frac", e["html"])

    def test_dv07_tous_les_exemples(self):   # DV-07 : f' sans fraction imbriquée, pour les exemples et cas limites
        from cas import CAS_LIMITES, entrees_page
        for entree in dict.fromkeys(entrees_page("derivee-variations") + CAS_LIMITES["derivee-variations"]):
            r = dv.etudier(entree)
            if r.get("deriv_resolu"):
                with self.subTest(f=entree):
                    self.assertNotIn(r"\frac{\frac", r["deriv_tex"])

    def test_zero_du_numerateur_valeur_interdite_du_denominateur(self):
        r = dv.etudier("x^(2/3)")
        self.assertEqual(r["ed_deriv_tex"], r"\mathbb{R} \setminus \left\{0\right\}")   # 0 : valeur interdite de f'
        self.assertTrue(any("Le numérateur vaut" in e.get("html", "") for e in r["signe_etapes"]))   # 2 ne s'annule jamais


if __name__ == "__main__":
    unittest.main()
