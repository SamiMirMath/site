"""Atome (ln, exp, racine) au degré 1 : on l'isole en écrivant chaque étape, sans poser t = … ; la substitution
est réservée au degré ≥ 2. Seule la rédaction change : conditions, ensembles et tableaux sont identiques."""
import re
import unittest

from moteurs import ensemble_def as ed
import derivee_variations as dv


def textes(entree):
    res = ed.analyser(entree)
    return [re.sub(r"\s+", " ", e["html"]) for c in res["conditions"] for e in c["etapes"] if "html" in e], res


def contient(entree, *morceaux):
    t, _ = textes(entree)
    return all(any(m in x for x in t) for m in morceaux), t


class TestIsolerAtome(unittest.TestCase):
    def verifie(self, entree, *morceaux, sans_pose=True, ed_tex=None):
        ok, t = contient(entree, *morceaux)
        self.assertTrue(ok, t)
        if sans_pose:
            self.assertFalse(any("On pose" in x for x in t), t)
        if ed_tex is not None:
            self.assertEqual(ed.analyser(entree)["ED_tex"], ed_tex)

    def test_ln_coefficient_negatif_isole_en_une_etape(self):
        self.verifie("ln(1-ln(x))",
                     r"\(1 - \ln(x) > 0 \iff \ln(x) < 1\) (on isole \(\ln(x)\) du côté où son coefficient est positif)",
                     r"\(\ln(x) < 1 \iff 0 < x < e\) (exp est croissante ; \(\ln\) n'est définie que sur \(\left]0 \,;\, +\infty\right[\))",
                     ed_tex=r"\left]0 \,;\, e\right[")

    def test_ln_moins_2(self):
        self.verifie("ln(ln(x)-2)", r"\(\ln(x) - 2 > 0 \iff \ln(x) > 2\) (on ajoute 2)",
                     r"\(\ln(x) > 2 \iff x > e^{2}\) (exp est croissante)", ed_tex=r"\left]e^{2} \,;\, +\infty\right[")

    def test_ln_avec_division_par_un_nombre_positif(self):
        self.verifie("ln(3-2ln(x))", r"\(3 - 2\ln(x) > 0 \iff 2\ln(x) < 3\)", r"\(2\ln(x) < 3 \iff \ln(x) < \frac{3}{2}\) (on divise par 2 > 0)")
        # le sens ne change jamais : on n'écrit pas « le sens change »
        t, _ = textes("ln(3-2ln(x))")
        self.assertFalse(any("le sens change" in x for x in t))

    def test_exp(self):
        self.verifie("ln(e^x-3)", r"\(e^{x} - 3 > 0 \iff e^{x} > 3\) (on ajoute 3)", r"\(e^{x} > 3 \iff x > \ln(3)\) (ln est croissante)",
                     ed_tex=r"\left]\ln(3) \,;\, +\infty\right[")
        self.verifie("ln(2-e^x)", r"\(2 - e^{x} > 0 \iff e^{x} < 2\)", r"\(e^{x} < 2 \iff x < \ln(2)\) (ln est croissante ; une exponentielle est strictement positive)")
        self.verifie("ln(e^(2x-1)-1)", r"\(e^{2x - 1} > 1 \iff 2x - 1 > 0\) (ln est croissante)", r"\(2x - 1 > 0 \iff x > \frac{1}{2}\)")

    def test_exp_constante_negative_ou_nulle(self):
        self.verifie("ln(e^x+3)", r"\(e^{x} > -3\) est toujours vrai : une exponentielle est strictement positive", ed_tex=r"\mathbb{R}")
        self.verifie("ln(-3-e^x)", r"\(e^{x} < -3\) est impossible : une exponentielle est strictement positive", ed_tex=r"\varnothing")
        self.verifie("ln(e^x)", sans_pose=True)

    def test_racine(self):
        self.verifie("ln(sqrt(x)-2)", r"\(\sqrt{x} - 2 > 0 \iff \sqrt{x} > 2\) (on ajoute 2)", r"\(\sqrt{x} > 2 \iff x > 4\) (la fonction carré est croissante sur",
                     ed_tex=r"\left]4 \,;\, +\infty\right[")
        self.verifie("ln(sqrt(x+1)+3)", r"\(\sqrt{x + 1} > -3\) est vrai dès que \(\sqrt{x + 1}\) est définie : une racine carrée est positive ou nulle",
                     ed_tex=r"\left[-1 \,;\, +\infty\right[")
        self.verifie("ln(-1-sqrt(x))", r"\(\sqrt{x} < -1\) est impossible : une racine carrée est positive ou nulle", ed_tex=r"\varnothing")

    def test_substitution_conservee_au_degre_2(self):
        for entree in ("ln((ln(x))^2-1)", "ln(e^(2x)-3e^x+2)"):
            t, res = textes(entree)
            with self.subTest(f=entree):
                self.assertTrue(any(x.startswith("On pose") for x in t), t)
        t, _ = textes("ln((ln(x))^2-1)")
        self.assertTrue(any("(exp est croissante" in x for x in t), t)          # même formulation après substitution
        t, _ = textes("ln(e^(2x)-3e^x+2)")
        self.assertTrue(any("(ln est croissante" in x for x in t), t)

    def test_cas_de_la_derivee(self):
        r = dv.etudier("ln(x)/x")                                      # f' = −(ln x − 1)/x²
        textes_dv = " ".join(e.get("html", "") for e in r["signe_etapes"])
        self.assertIn(r"\ln(x) - 1 > 0 \iff \ln(x) > 1\) (on ajoute 1)", textes_dv)
        self.assertNotIn("On pose", textes_dv)
        r = dv.etudier("x*ln(x)")                                      # f' = ln x + 1
        textes_dv = " ".join(e.get("html", "") for e in r["signe_etapes"])
        self.assertIn(r"\ln(x) + 1 = 0 \iff \ln(x) = -1\) (on soustrait 1)", textes_dv)
        r = dv.etudier("e^x-3")
        self.assertNotIn("On pose", " ".join(e.get("html", "") for e in r["signe_etapes"]))

    def test_ensembles_identiques_avec_ou_sans_redaction(self):
        """Mêmes ensembles que la méthode par substitution (resoudre_dans) sur une famille de conditions."""
        for a in (-3, -2, -1, 1, 2, 3):
            for b in (-4, -1, 0, 1, 5):
                for fonction in ("ln(x)", "e^x", "sqrt(x)"):
                    expr = f"({a}*{fonction}+({b}))"
                    with self.subTest(expr=expr):
                        res = ed.analyser(f"ln{expr}")
                        self.assertTrue(res["complet"])
                        _, arbre, ED = ed._analyser(f"ln{expr}")
                        import oracle
                        for x in (-5, -1, 0, 0.3, 1, 2, 7, 30):
                            self.assertEqual(oracle.definie(arbre, x), ed.contient(ED, x), (expr, x, res["ED_tex"]))


if __name__ == "__main__":
    unittest.main()
