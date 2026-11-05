"""Q5 / Q12 — moteur/nombres.py : notation suisse des nombres, réutilisable par T23 (tokeniseurs, graduations, commun/nombres.js).

Briques communes B5 : `approx` (valeur approchée, R13, E14, D25) et `exact` (valeur exacte, R13), croisées avec `exp_log.tex_approx` et
`exp_log._nb_exact` (importés ici, depuis les tests : la brique n'importe aucun outil). Les écarts voulus avec `tex_approx` sont
nommés (constantes ECART_*) dans ECHANTILLON ; partout ailleurs, égalité à l'octet."""
import ast
import math
import unittest
from decimal import Decimal as D
from fractions import Fraction as F

import mpmath

import moteurs  # noqa: F401  met moteur/ sur le chemin d'import
import nombres as nb
import exp_log as el


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


# ---------------------------------------------------------------------------------------------------------------------
# B5 : approx et exact
# ---------------------------------------------------------------------------------------------------------------------
# Écarts voulus avec exp_log.tex_approx (E14 et « rien de faux ») ; aucun ne touche une valeur du corpus d'Exp-log (journal, B5)
ECART_ARRONDI_A_10_6 = ("valeur arrondie à 10⁶ : notation scientifique (R13, E14 : dès 10⁶) ; tex_approx décide avant l'arrondi et "
                        "écrit 1’000’000,000")
ECART_MI_CHEMIN = ("valeur exactement à mi-chemin : arrondie au-dessus (calcul exact, arrondi usuel, comme Étude complète) ; "
                   "tex_approx arrondit la valeur binaire du float (au pair, ou en dessous après la division par 10ⁿ)")
ECART_ZERO_NEGATIF = "−0,0 s'écrit 0{,}000 ; tex_approx écrit -0{,}000"
ECARTS = (ECART_ARRONDI_A_10_6, ECART_MI_CHEMIN, ECART_ZERO_NEGATIF)

RACINE_1000 = math.sqrt(1_000_004)                      # x² + 1000x − 1 = 0 : x = (−1000 ± √1000004)/2 (cas limite, § 6 du 2e degré)

# (nom, valeur, approx attendu, None si tex_approx donne la même chose, sinon (écart nommé, tex_approx attendu))
ECHANTILLON = [
    ("0", 0.0, "0{,}000", None),
    ("−0,0", -0.0, "0{,}000", (ECART_ZERO_NEGATIF, "-0{,}000")),
    ("1", 1.0, "1{,}000", None),
    ("−1", -1.0, "-1{,}000", None),
    ("0,5", 0.5, "0{,}500", None),
    ("−0,5", -0.5, "-0{,}500", None),
    ("1/3", 1 / 3, "0{,}333", None),
    ("2/3", 2 / 3, "0{,}667", None),
    ("−2/3", -2 / 3, "-0{,}667", None),
    ("π", math.pi, "3{,}142", None),
    ("√2", math.sqrt(2), "1{,}414", None),
    ("−√5 (E14)", -math.sqrt(5), "-2{,}236", None),
    ("−2 − √5 (E14)", -2 - math.sqrt(5), "-4{,}236", None),
    ("−2 + √5 (E14)", -2 + math.sqrt(5), "0{,}236", None),
    ("6,644", 6.644, "6{,}644", None),
    ("−0,693", -0.693, "-0{,}693", None),
    ("0,001", 0.001, "0{,}001", None),
    ("0,0010004", 0.0010004, "0{,}001", None),
    ("0,000999", 0.000999, r"9{,}990 \times 10^{-4}", None),
    ("0,0009999", 0.0009999, r"9{,}999 \times 10^{-4}", None),
    ("0,0009995 (4 chiffres significatifs : reste sous 10⁻³)", 0.0009995, r"9{,}995 \times 10^{-4}", None),
    ("0,00099995 (mantisse arrondie à 10)", 0.00099995, r"1 \times 10^{-3}", None),
    ("0,00099999 (mantisse arrondie à 10)", 0.00099999, r"1 \times 10^{-3}", None),
    ("x² + 1000x − 1 = 0, racine positive (mantisse arrondie à 10)", 2 / (1000 + RACINE_1000), r"1 \times 10^{-3}",
     None),
    ("x² + 1000x − 1 = 0, racine négative", (-1000 - RACINE_1000) / 2, r"-1\text{’}000{,}001", None),
    ("1234,5678", 1234.5678, r"1\text{’}234{,}568", None),
    ("4913", 4913.0, r"4\text{’}913{,}000", None),
    ("123 456,789", 123456.789, r"123\text{’}456{,}789", None),
    ("999 999,4", 999999.4, r"999\text{’}999{,}400", None),
    ("999 999,6", 999999.6, r"999\text{’}999{,}600", None),
    ("999 999,9994", 999999.9994, r"999\text{’}999{,}999", None),
    ("999 999,9996 (arrondi à 10⁶)", 999999.9996, r"1 \times 10^{6}", (ECART_ARRONDI_A_10_6, r"1\text{’}000\text{’}000{,}000")),
    ("−999 999,9996 (arrondi à −10⁶)", -999999.9996, r"-1 \times 10^{6}", (ECART_ARRONDI_A_10_6, r"-1\text{’}000\text{’}000{,}000")),
    ("10⁶", 1e6, r"1 \times 10^{6}", None),
    ("−10⁶", -1e6, r"-1 \times 10^{6}", None),
    ("4,5 × 10⁶", 4.5e6, r"4{,}500 \times 10^{6}", None),
    ("9,99949 × 10⁶", 9.99949e6, r"9{,}999 \times 10^{6}", None),
    ("9,9995 × 10⁶ (mantisse arrondie à 10)", 9.9995e6, r"1 \times 10^{7}", (ECART_MI_CHEMIN, r"9{,}999 \times 10^{6}")),
    ("2 × 10⁷", 2e7, r"2 \times 10^{7}", None),
    ("−2,5 × 10⁷", -2.5e7, r"-2{,}500 \times 10^{7}", None),
    ("10¹⁰", 1e10, r"1 \times 10^{10}", None),
    ("10⁻⁴", 1e-4, r"1 \times 10^{-4}", None),
    ("10⁻⁵", 1e-5, r"1 \times 10^{-5}", None),
    ("3,1623 × 10⁻⁵", 3.1623e-5, r"3{,}162 \times 10^{-5}", None),
    ("−3,162 × 10⁻⁵", -3.162e-5, r"-3{,}162 \times 10^{-5}", None),
    ("0,0625 (mi-chemin)", 0.0625, "0{,}063", (ECART_MI_CHEMIN, "0{,}062")),
    ("2,0625 (mi-chemin)", 2.0625, "2{,}063", (ECART_MI_CHEMIN, "2{,}062")),
    ("0,1875 (mi-chemin, même arrondi)", 0.1875, "0{,}188", None),
]


class TestApprox(unittest.TestCase):
    """nombres.approx (R13, E14, D25) sur l'échantillon, et contre exp_log.tex_approx : égal, ou écart nommé."""

    def test_echantillon(self):
        for nom, v, attendu, _ in ECHANTILLON:
            with self.subTest(nom):
                self.assertEqual(nb.approx(v), attendu)

    def test_croise_avec_tex_approx(self):
        for nom, v, attendu, ecart in ECHANTILLON:
            with self.subTest(nom):
                if ecart is None:
                    self.assertEqual(el.tex_approx(v), attendu)
                else:
                    self.assertIn(ecart[0], ECARTS)
                    self.assertEqual(el.tex_approx(v), ecart[1])
                    self.assertNotEqual(ecart[1], attendu)

    def test_tous_les_ecarts_sont_illustres(self):
        self.assertEqual({e[0] for *_, e in ECHANTILLON if e}, set(ECARTS))

    def test_valeurs_du_test_de_tex_approx(self):
        """Les valeurs de test_exp_log.test_approximation_en_notation_scientifique : égales à tex_approx, toutes."""
        for v, attendu in [(6.644, "6{,}644"), (-0.693, "-0{,}693"), (0.0, "0{,}000"), (1e10, r"1 \times 10^{10}"),
                           (1e-4, r"1 \times 10^{-4}"), (3.1623e-5, r"3{,}162 \times 10^{-5}"), (-2.5e7, r"-2{,}500 \times 10^{7}"),
                           (0.00099999, r"1 \times 10^{-3}"), (123456.789, r"123\text{’}456{,}789"), (4.5e6, r"4{,}500 \times 10^{6}")]:
            with self.subTest(v):
                self.assertEqual(nb.approx(v), attendu)
                self.assertEqual(el.tex_approx(v), attendu)

    def test_valeur_prise_exactement(self):
        """int, Fraction, Decimal sans passer par un float ; SymPy et mpmath par float() ; mêmes écritures."""
        for v, attendu in [(F(1, 3), "0{,}333"), (F(-2, 3), "-0{,}667"), (4913, r"4\text{’}913{,}000"), (D("0.0625"), "0{,}063"),
                           (D("-0.0009995"), r"-9{,}995 \times 10^{-4}"), (D("0.00099995"), r"1 \times 10^{-3}"),
                           (F(19999, 20_000_000), r"1 \times 10^{-3}"), (10 ** 400, r"1 \times 10^{400}"),
                           (F(-1, 3 * 10 ** 400), r"-3{,}333 \times 10^{-401}"), (mpmath.sqrt(2), "1{,}414"),
                           (mpmath.mpf("-3.1622776e-5"), r"-3{,}162 \times 10^{-5}"), (moteurs.ensemble_def._sympy().sqrt(5), "2{,}236")]:
            with self.subTest(repr(v)[:40]):
                self.assertEqual(nb.approx(v), attendu)

    def test_decimales(self):
        for v, d, attendu in [(math.pi, 1, "3{,}1"), (math.pi, 2, "3{,}14"), (math.pi, 5, "3{,}14159"), (0.005, 2, r"5 \times 10^{-3}"),
                              (0.01, 2, "0{,}01"), (0.0, 2, "0{,}00"), (1234.5, 1, r"1\text{’}234{,}5"), (9.96e6, 1, r"1 \times 10^{7}")]:
            with self.subTest((v, d)):
                self.assertEqual(nb.approx(v, decimales=d), attendu)

    def test_refuse_ce_qui_serait_faux(self):
        for v in [math.inf, -math.inf, math.nan, D("NaN"), D("Infinity"), mpmath.inf]:
            with self.subTest(repr(v)):
                with self.assertRaises(ValueError):
                    nb.approx(v)
        for d in [0, -1, 1.5, True, "3"]:
            with self.subTest(decimales=d):
                with self.assertRaises(ValueError):
                    nb.approx(1.0, d)

    def test_virgule_apostrophe_et_signe(self):
        """D25 : apostrophe dès 4 chiffres sur la partie entière, jamais dans les décimales ; virgule {,} ; jamais « −−», ni point."""
        for _, v, attendu, _ in ECHANTILLON:
            with self.subTest(v):
                self.assertNotIn(".", attendu)
                entier = attendu.split("{,}")[0].lstrip("-")
                if r"\times" not in attendu:
                    self.assertEqual(entier, nb.grouper(entier.replace(nb.SEPARATEUR_TEX, ""), nb.SEPARATEUR_TEX))
                self.assertEqual(attendu.startswith("-"), v < 0 and attendu.strip("-0{,}") != "")


def _tex_nb_exact(v, decimaux):
    """TeX de exp_log._nb_exact(v) sous l'état _DECIMAUX voulu, remis ensuite (exp_log n'est pas modifié)."""
    avant = el._DECIMAUX
    el._DECIMAUX = decimaux
    try:
        return el.tex(el._nb_exact(v))
    finally:
        el._DECIMAUX = avant


class TestExact(unittest.TestCase):
    """nombres.exact (R13, E14) contre tex(exp_log._nb_exact(v)) sous _DECIMAUX = decimaux_enonce : égal partout."""
    CAS = [  # (valeur, sans décimaux de l'énoncé, avec)
        (0, "0", "0"), (1, "1", "1"), (-1, "-1", "-1"), (-3, "-3", "-3"), (999, "999", "999"),
        (1000, r"1\text{’}000", r"1\text{’}000"), (4913, r"4\text{’}913", r"4\text{’}913"), (-4913, r"-4\text{’}913", r"-4\text{’}913"),
        (1234567, r"1\text{’}234\text{’}567", r"1\text{’}234\text{’}567"),
        (F(1, 2), r"\frac{1}{2}", "0{,}5"), (F(-1, 2), r"-\frac{1}{2}", "-0{,}5"), (F(1, 3), r"\frac{1}{3}", r"\frac{1}{3}"),
        (F(2, 3), r"\frac{2}{3}", r"\frac{2}{3}"), (F(-5, 2), r"-\frac{5}{2}", "-2{,}5"), (F(-13, 60), r"-\frac{13}{60}", r"-\frac{13}{60}"),
        (F(761, 400), r"\frac{761}{400}", "1{,}9025"), (F(-27, 100), r"-\frac{27}{100}", "-0{,}27"),
        (F(2469, 2), r"\frac{2\text{’}469}{2}", r"1\text{’}234{,}5"), (F(1, 1000), r"\frac{1}{1\text{’}000}", "0{,}001"),
        (F(1, 3000), r"\frac{1}{3\text{’}000}", r"\frac{1}{3\text{’}000}"), (F(1, 256), r"\frac{1}{256}", "0{,}00390625"),
        (F(1, 512), r"\frac{1}{512}", r"\frac{1}{512}"), (F(3, 10 ** 8), r"\frac{3}{100\text{’}000\text{’}000}", "0{,}00000003"),
        (F(3, 10 ** 9), r"\frac{3}{1\text{’}000\text{’}000\text{’}000}", r"\frac{3}{1\text{’}000\text{’}000\text{’}000}"),
        (F(123456789, 1000), r"\frac{123\text{’}456\text{’}789}{1\text{’}000}", r"123\text{’}456{,}789"),
        (D("0.50"), r"\frac{1}{2}", "0{,}5"), (D("-1.25"), r"-\frac{5}{4}", "-1{,}25"), ("13/60", r"\frac{13}{60}", r"\frac{13}{60}"),
    ]

    def test_cas(self):
        for v, sans, avec in self.CAS:
            with self.subTest(v=v):
                self.assertEqual(nb.exact(v), sans)
                self.assertEqual(nb.exact(v, decimaux_enonce=False), sans)
                self.assertEqual(nb.exact(v, decimaux_enonce=True), avec)

    def test_croise_avec_nb_exact(self):
        for v, *_ in self.CAS:
            for decimaux in (False, True):
                with self.subTest(v=v, decimaux_enonce=decimaux):
                    self.assertEqual(nb.exact(v, decimaux_enonce=decimaux), _tex_nb_exact(F(v), decimaux))
        self.assertFalse(el._DECIMAUX)

    def test_refuse_un_float_et_l_infini(self):
        with self.assertRaises(TypeError):
            nb.exact(0.5)
        with self.assertRaises(ValueError):
            nb.exact(D("Infinity"))


class TestPurete(unittest.TestCase):
    """A7 : approx et exact ne changent aucune variable de module et ne lisent pas l'état d'Exp-log (`_DECIMAUX`)."""

    def test_aucun_etat_change(self):
        avant = {k: v for k, v in vars(nb).items() if not k.startswith("__")}
        for _, v, *_ in ECHANTILLON:
            nb.approx(v)
        for v, *_ in TestExact.CAS:
            nb.exact(v, decimaux_enonce=True)
            nb.exact(v)
        apres = {k: v for k, v in vars(nb).items() if not k.startswith("__")}
        self.assertEqual(avant.keys(), apres.keys())
        for k in avant:
            self.assertIs(avant[k], apres[k], k)

    def test_ne_lit_pas_l_etat_d_exp_log(self):
        avant = el._DECIMAUX
        el._DECIMAUX = True
        try:
            self.assertEqual(nb.exact(F(1, 2)), r"\frac{1}{2}")
        finally:
            el._DECIMAUX = avant
        with open(nb.__file__, encoding="utf-8") as f:
            arbre = ast.parse(f.read())
        noms = {n.id for n in ast.walk(arbre) if isinstance(n, ast.Name)} | {n.attr for n in ast.walk(arbre) if isinstance(n, ast.Attribute)}
        self.assertNotIn("_DECIMAUX", noms)                                       # le code ne le nomme pas (la docstring, si)
        modules = {a.name for n in ast.walk(arbre) if isinstance(n, ast.Import) for a in n.names}
        modules |= {n.module for n in ast.walk(arbre) if isinstance(n, ast.ImportFrom)}
        self.assertEqual(modules, {"math", "re", "decimal", "fractions"})        # bibliothèque standard seulement


if __name__ == "__main__":
    unittest.main()
