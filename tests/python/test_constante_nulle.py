"""Bug : plantage sur une constante nulle (x^(2-2)), valeur_constante rendait le flottant 0.0."""
import json
import unittest
from fractions import Fraction as F

from moteurs import ensemble_def as ed


def ed_de(entree):
    r = json.loads(ed.analyser_json(entree))
    assert r["ok"], r
    return r["ED_tex"]


class TestConstanteNulle(unittest.TestCase):
    def test_exposants_nuls_sans_exception(self):  # ED-03
        reference = ed_de("x^0")
        for entree in ["x^(2-2)", "x^(1/2-1/2)", "x^(0,5-0,5)", "(ln(x))^(2-2)"]:
            with self.subTest(f=entree):
                self.assertEqual(ed_de(entree), ed_de(entree.split("^")[0] + "^0"))
        self.assertEqual(reference, r"\mathbb{R}")

    def test_valeur_constante_reste_rationnelle(self):
        v = ed.valeur_constante(ed.Op("-", ed.Nb(F(2)), ed.Nb(F(2))))
        self.assertEqual(v, 0)
        self.assertIsInstance(v, F)

    def test_constante_exacte_non_nulle_jamais_arrondie(self):
        """Le seuil 1e-12 ne vaut que pour les flottants : 1000000000001/1000000000000 − 1 = 10⁻¹²."""
        grand = F(10) ** 12
        v = ed.valeur_constante(ed.Op("-", ed.Nb((grand + 1) / grand), ed.Nb(F(1))))
        self.assertEqual(v, 1 / grand)
        self.assertEqual(ed_de("x^(1000000000001/1000000000000-1)"), ed_de("x^(1/1000000000000)"))
        self.assertEqual(ed_de("x^(1/1000000000000)"), r"\left[0 \,;\, +\infty\right[")

    def test_exposants_transcendants_sans_plantage(self):
        for entree in ["x^(ln 2)", "x^(ln(4)-2ln(2))"]:
            with self.subTest(f=entree):
                self.assertEqual(ed_de(entree), r"\left]0 \,;\, +\infty\right[")

    def test_valeur_constante_jamais_flottante(self):
        for entree in ["2-2", "1/3-1/3", "2^(1-1)", "1000000000001/1000000000000-1", "ln(2)", "2*ln(2)-ln(4)"]:
            v = ed.valeur_constante(ed.lire(entree))
            with self.subTest(f=entree):
                self.assertTrue(v is None or isinstance(v, F), v)

    def test_base_exigee_avec_exposant_zero(self):  # ED-08 (Q6), comportement déjà conforme
        attendu = {
            "x^0": r"\mathbb{R}",
            "(ln(x))^0": r"\left]0 \,;\, +\infty\right[",
            "(1/x)^0": r"\mathbb{R} \setminus \left\{0\right\}",
            "(sqrt(x-1))^0": r"\left[1 \,;\, +\infty\right[",
        }
        for entree, tex in attendu.items():
            with self.subTest(f=entree):
                self.assertEqual(ed_de(entree), tex)


if __name__ == "__main__":
    unittest.main()
