"""Q5 / Q12 — moteur/nombres.py : notation suisse des nombres, réutilisable par T23 (tokeniseurs, graduations, commun/nombres.js)."""
import unittest

import moteurs  # noqa: F401  met moteur/ sur le chemin d'import
import nombres as nb


class TestGrouper(unittest.TestCase):
    def test_a_partir_de_4_chiffres(self):
        for chiffres, attendu in [("0", "0"), ("7", "7"), ("99", "99"), ("999", "999"), ("1000", "1’000"), ("9999", "9’999"),
                                  ("12345", "12’345"), ("123456", "123’456"), ("1234567", "1’234’567"), ("99999995", "99’999’995"),
                                  ("100000000", "100’000’000")]:
            with self.subTest(chiffres):
                self.assertEqual(nb.grouper(chiffres), attendu)

    def test_separateur_typographique(self):
        self.assertEqual(nb.SEPARATEUR, "’")
        self.assertNotIn("'", nb.grouper("1234567"))


class TestFormater(unittest.TestCase):
    def test_entiers(self):
        for n, texte, tex in [(0, "0", "0"), (999, "999", "999"), (1000, "1’000", r"1\text{’}000"), (-1000, "-1’000", r"-1\text{’}000"),
                              (-99999995, "-99’999’995", r"-99\text{’}999\text{’}995"), (1234567, "1’234’567", r"1\text{’}234\text{’}567")]:
            with self.subTest(n):
                self.assertEqual(nb.formater_entier(n), texte)
                self.assertEqual(nb.formater_entier(n, tex=True), tex)

    def test_decimaux_partie_entiere_seulement(self):
        for s, texte, tex in [("1234,567", "1’234,567", r"1\text{’}234{,}567"), ("1234.567", "1’234,567", r"1\text{’}234{,}567"),
                              ("0,0001", "0,0001", r"0{,}0001"), ("0.01", "0,01", r"0{,}01"), ("-1234,5", "-1’234,5", r"-1\text{’}234{,}5"),
                              ("123456,78901", "123’456,78901", r"123\text{’}456{,}78901"), ("12", "12", "12"), ("1000", "1’000", r"1\text{’}000"),
                              (",5", "0,5", r"0{,}5")]:
            with self.subTest(s):
                self.assertEqual(nb.formater_decimal(s), texte)
                self.assertEqual(nb.formater_decimal(s, tex=True), tex)

    def test_jamais_de_separateur_dans_les_decimales(self):
        for s in ["0,123456789", "1234,123456789", "1234567,1234567"]:
            decimales = nb.formater_decimal(s).partition(",")[2]
            self.assertTrue(decimales.isdigit(), decimales)


class TestSaisie(unittest.TestCase):
    def lit(self, s):
        m = nb.MOTIF_SAISIE.match(s)
        return m.group(0) if m else None

    def test_motif_de_saisie(self):
        for s, lu in [("1'000", "1'000"), ("1’000", "1’000"), ("1'234'567x", "1'234'567"), ("1’234,5+2", "1’234,5"), ("12", "12"),
                      ("0,01", "0,01"), (",5", ",5"), ("1234", "1234"), ("1'00", "1"), ("1'0000", "1'000")]:
            with self.subTest(s):
                self.assertEqual(self.lit(s), lu)

    def test_nettoyer(self):
        self.assertEqual(nb.nettoyer_saisie("1’234,567"), "1234.567")
        self.assertEqual(nb.nettoyer_saisie("1'234'567"), "1234567")
        self.assertEqual(nb.nettoyer_saisie("0,01"), "0.01")

    def test_espace_dans_un_nombre(self):
        for s in [" 000", "  123", " 999+1"]:
            self.assertIsNotNone(nb.MOTIF_ESPACE_DANS_UN_NOMBRE.match(s), s)
        for s in [" 3x", " 12", " 1234", " x", "\n123"]:
            self.assertIsNone(nb.MOTIF_ESPACE_DANS_UN_NOMBRE.match(s), s)


if __name__ == "__main__":
    unittest.main()
