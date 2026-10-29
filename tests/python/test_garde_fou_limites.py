"""Chantier « Limites et asymptotes » 3M, étape 1 : garde-fou générique sur les résultats de SymPy.

- Bug 8.13e : ln((3x²−3x+2)/(x²−5x+2)) aux pôles irrationnels (5 ± √17)/2 affichait une limite avec x et iπ puis « trou ».
- Tout résultat avec symbole libre, i, zoo, nan, AccumBounds ou partie imaginaire est rejeté, partout où SymPy est appelé.
- La sonde mpmath ne refuse une valeur que sur une contradiction nette ; une convergence lente (logarithmes) n'en est pas une.
- Fonctions non prises en charge (sin, cos, tan, log_a…) : message compréhensible, jamais « Symbole inconnu « s » »."""
import unittest
from unittest import mock

from moteurs import ensemble_def as ed
import limites_asymptotes as la

sp = ed._sympy()
X = ed._SP["x"]
POLE_G = r"\frac{5 - \sqrt{17}}{2}"
POLE_D = r"\frac{5 + \sqrt{17}}{2}"
F_8_13E = "ln((3x^2-3x+2)/(x^2-5x+2))"


def verticale_en(r, point_tex):
    return [a for a in r["asymptotes"] if a["genre"] == "verticale" and a.get("point_tex") == point_tex]


class TestBug813e(unittest.TestCase):
    def test_pole_gauche_plus_l_infini_asymptote_verticale(self):
        r = la.etudier(F_8_13E)
        (a,) = verticale_en(r, POLE_G)
        self.assertEqual(a["gauche_tex"], r"+\infty")

    def test_pole_droit_plus_l_infini_asymptote_verticale(self):
        r = la.etudier(F_8_13E)
        (a,) = verticale_en(r, POLE_D)
        self.assertEqual(a["droite_tex"], r"+\infty")

    def test_aucun_symbole_libre_ni_i_ni_trou(self):
        r = la.etudier(F_8_13E)
        self.assertEqual([a for a in r["asymptotes"] if a["genre"] == "trou"], [])
        for e in r["etudes"]:
            for it in e["etapes"]:
                t = it.get("html", "")
                self.assertNotIn(r"\pi", t)
                self.assertNotIn("log{", t)
                self.assertNotIn("trou", t)

    def test_en_plus_et_moins_l_infini_ln_3(self):
        r = la.etudier(F_8_13E)
        hz = {a["ou"]: a["valeur_tex"] for a in r["asymptotes"] if a["genre"] == "horizontale"}
        self.assertEqual(set(hz), {r"x \to -\infty", r"x \to +\infty"})
        self.assertTrue(all("3" in v for v in hz.values()), hz)

    def test_limites_par_la_fonction_interne(self):
        f = ed.lire(F_8_13E)
        a_g = sp.Rational(5, 2) - sp.sqrt(17) / 2
        a_d = sp.Rational(5, 2) + sp.sqrt(17) / 2
        self.assertEqual(la._limite_sympy(f, a_g, "-"), sp.oo)
        self.assertEqual(la._limite_sympy(f, a_d, "+"), sp.oo)


class TestRejet(unittest.TestCase):
    def test_resultats_inutilisables(self):
        for r in [X, sp.log(X) + sp.I * sp.pi, sp.zoo, sp.nan, sp.AccumBounds(-1, 1), sp.I, 2 + sp.I,
                  sp.oo * (-1) ** sp.Rational(2, 3), None]:
            with self.subTest(r=r):
                self.assertTrue(la._rejete(r))

    def test_resultats_acceptes(self):
        for r in [sp.oo, -sp.oo, sp.Integer(0), sp.log(3), sp.exp(2), sp.Rational(1, 2), sp.sqrt(2) / 2]:
            with self.subTest(r=r):
                self.assertFalse(la._rejete(r))

    def test_limite_sympy_ne_renvoie_jamais_un_resultat_rejete(self):
        f = ed.lire("1/x")
        for faux in [X, sp.log(X) + sp.I * sp.pi, sp.zoo, sp.nan, sp.AccumBounds(-1, 1)]:
            with self.subTest(r=faux), mock.patch.object(sp, "limit", return_value=faux):
                self.assertIsNone(la._limite_sympy(f, sp.Integer(0), "+"))

    def test_valeur_tex_ne_laisse_jamais_passer_un_symbole(self):
        for faux in [X, sp.log(X) + sp.I * sp.pi, sp.zoo, sp.nan, None]:
            with self.subTest(r=faux):
                self.assertEqual(la._valeur_tex(faux)[0], "?")

    def test_valeur_tex_n_utilise_plus_latex_brut(self):
        import inspect
        self.assertNotIn("sp.latex(", inspect.getsource(la._valeur_tex))

    def test_message_sans_valeur_quand_sympy_ne_conclut_pas(self):
        with mock.patch.object(sp, "limit", return_value=sp.log(X) + sp.I * sp.pi):
            r = la.etudier("ln(x)/x")
        textes = " ".join(it.get("html", "") for e in r["etudes"] for it in e["etapes"])
        self.assertNotIn(r"\pi", textes)
        self.assertNotIn("log{", textes)


class TestSonde(unittest.TestCase):
    """La sonde refuse une valeur fausse (contradiction nette) mais jamais une convergence lente."""

    def contredit(self, entree, point, direction, valeur):
        f = ed.lire(entree)
        return la._contradit_par_sonde(lambda mp, x: la._val_mp(mp, f, x), la._sonde_lointaine(f), point, direction, valeur)

    def test_contradictions_nettes(self):
        self.assertTrue(self.contredit("1/x", sp.Integer(0), "+", -sp.oo))        # signe opposé
        self.assertTrue(self.contredit("1/x", sp.Integer(0), "+", sp.Integer(3)))  # infini contre fini
        self.assertTrue(self.contredit("x^2", sp.oo, None, sp.Integer(5)))
        self.assertTrue(self.contredit("1/x", sp.oo, None, sp.oo))                # fini contre infini
        self.assertTrue(self.contredit("(2x+1)/(x-1)", sp.oo, None, sp.Integer(3)))

    def test_valeurs_justes_acceptees(self):
        self.assertFalse(self.contredit("1/x", sp.Integer(0), "+", sp.oo))
        self.assertFalse(self.contredit("(2x+1)/(x-1)", sp.oo, None, sp.Integer(2)))
        self.assertFalse(self.contredit("e^x", -sp.oo, None, sp.Integer(0)))

    def test_anti_faux_rejet_convergence_lente(self):
        """Cas imposés : aucune valeur juste ne doit être refusée parce que les logarithmes convergent lentement."""
        cas = [("(ln(x)-2)/(ln(x)-1)", sp.Integer(0), "+", sp.Integer(1)),        # 3.11e en 0⁺
               ("(ln(x)-2)/(ln(x)-1)", sp.oo, None, sp.Integer(1)),                # 3.11e en +∞
               ("ln(x^2)/ln(x)^2", sp.oo, None, sp.Integer(0)),                    # 3.8g
               ("ln(x)/x", sp.oo, None, sp.Integer(0)),
               ("1/ln(x)", sp.oo, None, sp.Integer(0)),
               ("x*ln(x)", sp.Integer(0), "+", sp.Integer(0)),
               ("ln(x)/e^x", sp.oo, None, sp.Integer(0)),
               ("ln(x^2+1)/x", sp.oo, None, sp.Integer(0)),
               ("ln(x^2+1)/x", -sp.oo, None, sp.Integer(0)),
               ("ln(x)", sp.oo, None, sp.oo),
               ("ln(x)", sp.Integer(0), "+", -sp.oo),
               ("(ln(x)+1)/(1-ln(x))", sp.oo, None, sp.Integer(-1)),
               ("ln(x+1)/x", sp.Integer(0), None, sp.Integer(1)),
               ("ln(1+e^x)/e^x", -sp.oo, None, sp.Integer(1))]
        for entree, point, direction, valeur in cas:
            with self.subTest(f=entree, point=point, valeur=valeur):
                self.assertFalse(self.contredit(entree, point, direction, valeur))
                self.assertEqual(la._limite_sympy(ed.lire(entree), point, direction), valeur)


class TestFonctionsNonPrisesEnCharge(unittest.TestCase):
    def message(self, entree):
        r = la.etudier(entree)
        self.assertFalse(r["ok"], entree)
        return r["erreur"]

    def test_fonctions_trigonometriques(self):
        for nom in ["sin", "cos", "tan", "cot", "arcsin", "arccos", "arctan", "sinh", "cosh", "tanh"]:
            with self.subTest(nom=nom):
                self.assertEqual(self.message(f"{nom}(x)"), f"La fonction {nom} n'est pas encore prise en charge par cet outil.")

    def test_cas_du_cours(self):
        self.assertEqual(self.message("ln(cos(x))/x^2"), "La fonction cos n'est pas encore prise en charge par cet outil.")   # 3.8b
        self.assertEqual(self.message("(e^x-1)/sin(x)"), "La fonction sin n'est pas encore prise en charge par cet outil.")   # feuille b
        self.assertEqual(self.message("log_5(x+2)/(x+1)"),                                                                  # 3.8 h'
                         "La fonction log_a (logarithme de base a) n'est pas encore prise en charge par cet outil.")

    def test_apercu_meme_message(self):
        import json
        r = json.loads(la.apercu_json("cos(x)"))
        self.assertFalse(r["ok"])
        self.assertIn("n'est pas encore prise en charge", r["erreur"])

    def test_autres_symboles_inchanges(self):
        self.assertIn("Symbole inconnu « y »", self.message("y+x"))


if __name__ == "__main__":
    unittest.main()
