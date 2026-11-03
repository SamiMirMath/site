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


class TestFormesDuCorrige(unittest.TestCase):
    """Chantier étude complète, P1 (decisions.md D6, D7, D17) : e^(somme) gardé entier, une exponentielle par exposant
    distinct ; facteur négatif entre parenthèses ; une phrase écrite une seule fois ; 3e^{−6} ; signe dans le facteur eˣ − 3."""
    FAMILLE = ["e^((x^2+x-2)/(6x-12))", "e^(2x)-4e^x", "e^x(6-e^x)", "e^(-x)-e^x", "(x+1)e^(x^2+x)", "e^x*e^(x+1)",
               "x*e^(1/x)", "ln(x)/x", "(x^2-6)e^(-2x)", "(1-e^x)/(1+e^x)"]

    def test_resultat_juste(self):
        for entree in self.FAMILLE:
            f = ed.lire(entree)
            r = dv.etudier(entree)
            fp = dv._simplifier(dv.derivee_narree(f, [], top=True))
            self.assertEqual(ed.tex(fp), r["deriv_tex"], entree)
            for t in (-1.3, 0.7, 1.9, 2.6):
                attendu = derivee_numerique(f, t)
                if attendu is None:
                    continue
                with self.subTest(f=entree, x=t):
                    self.assertTrue(proches(ed.evaluer(fp, t), attendu))

    def test_une_exponentielle_par_exposant(self):
        attendus = {"e^((x^2+x-2)/(6x-12))": [r"e^{\frac{x^{2} + x - 2}{6x - 12}}"], "e^(2x)-4e^x": ["e^{x}"],
                    "(x+1)e^(x^2+x)": ["e^{x^{2} + x}"], "x*e^(1/x)": [r"e^{\frac{1}{x}}"]}
        for entree, exps in attendus.items():
            t = dv.etudier(entree)["deriv_tex"]
            with self.subTest(f=entree):
                for e in exps:
                    self.assertIn(e, t)
                self.assertEqual(t.count("e^{"), sum(t.count(e) for e in exps), t)     # aucune autre exponentielle

    def test_facteur_negatif_entre_parentheses(self):
        r = dv.etudier("(x^2-6)e^(-2x)")
        ligne = next(it["html"] for it in r["deriv_etapes"] if "u'(x)v(x) + u(x)v'(x)" in it["html"])
        self.assertIn(r"\left(x^{2} - 6\right)\,\left(-2e^{-2x}\right)", ligne)
        self.assertNotIn(r"\cdot -", ligne)

    def test_phrase_ecrite_une_fois(self):
        etapes = [it["html"] for it in dv.etudier("e^x(6-e^x)")["deriv_etapes"]]
        self.assertEqual(len(etapes), len(set(etapes)), etapes)
        self.assertEqual(sum(r"\left(e^{x}\right)' = e^{x}" in h for h in etapes), 1, etapes)

    def test_formes_exactes(self):
        self.assertEqual(dv.etudier("e^x(6-e^x)")["deriv_tex"], r"2e^{x}\,\left(3 - e^{x}\right)")
        self.assertEqual(dv.etudier("ln(x)/x")["deriv_tex"], r"\frac{1 - \ln(x)}{x^{2}}")
        self.assertEqual(dv.etudier("(x^2-6)e^(-2x)")["deriv_tex"], r"-2\left(x - 3\right)\,\left(x + 2\right)\,e^{-2x}")
        valeurs = {e["x_tex"]: e["f_tex"] for e in dv.etudier("(x^2-6)e^(-2x)")["extrema"]}
        self.assertEqual(valeurs, {"-2": "- 2 e^{4}", "3": "3 e^{-6}"})
        self.assertEqual(dv.etudier("x*e^x")["extrema"][0]["f_tex"], "- e^{-1}")
        self.assertEqual(dv.etudier("x*e^(2x)")["extrema"][0]["f_tex"], r"- \frac{1}{2 e}")        # coefficient non entier : inchangé
        # somme sans terme négatif : le signe reste devant (jamais −e^{2x} − 1)
        self.assertEqual(dv.etudier("e^(-x)-e^x")["deriv_tex"], r"-\left(e^{2x} + 1\right)\,e^{-x}")


if __name__ == "__main__":
    unittest.main()
