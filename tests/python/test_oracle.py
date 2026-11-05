"""Briques communes B6 : `oracle.racines(coeffs)`, racines réelles d'un polynôme avec leur multiplicité, par mpmath seul.

Valeurs attendues exactes (entiers, fractions, racines carrées calculées à 100 chiffres), comparées à 45 chiffres au moins. Cas
demandés : (x − 1)², x²(x + 8), x² + 1, 17x² + 288x − 17 ; plus Fraction, décimaux, degrés 1 et 3, multiplicités 3 à 10, tête
nulle, constante, refus des entrées invalides, nombre de racines réelles (suite de Sturm exacte), contexte mpmath global inchangé,
indépendance du code (aucun moteur).

Ne pas confondre avec l'oracle `racines(s)` de test_exp_log_m.py (une saisie d'Exp-log, grille et bissection) et son cache
`memo_racines` : ce fichier ne les importe pas."""
import ast
import inspect
import unittest
from decimal import Decimal
from fractions import Fraction as F

from mpmath import mp

import oracle


def produit(*facteurs):
    """Coefficients (du plus haut degré au terme constant) du produit des polynômes donnés."""
    p = [F(1)]
    for f in facteurs:
        q = [F(0)] * (len(p) + len(f) - 1)
        for i, x in enumerate(p):
            for j, y in enumerate(f):
                q[i + j] += x * F(y)
        p = q
    return p


def valeur_exacte(v):
    """Une valeur attendue à 100 chiffres : int, Fraction, ou fonction sans argument (calculée sous 100 chiffres)."""
    with mp.workdps(100):
        if callable(v):
            return +v()
        v = F(v)
        return mp.mpf(v.numerator) / v.denominator


class CasRacines(unittest.TestCase):
    def assertRacines(self, coeffs, attendu, chiffres=45):
        """attendu : [(valeur, multiplicité)] dans l'ordre croissant."""
        r = oracle.racines(coeffs)
        self.assertEqual([m for _, m in r], [m for _, m in attendu], f"{coeffs} : {r}")
        for (x, _), (v, _) in zip(r, attendu):
            v = valeur_exacte(v)
            with mp.workdps(100):
                self.assertLessEqual(abs(x - v), mp.mpf(10) ** -chiffres * max(1, abs(v)), f"{coeffs} : {x} au lieu de {v}")
        return r


class TestCasDemandes(CasRacines):
    def test_x_moins_1_au_carre(self):
        r = self.assertRacines([1, -2, 1], [(1, 2)])
        self.assertEqual(r[0][0], 1)

    def test_x_carre_fois_x_plus_8(self):
        self.assertRacines(produit([1, 0], [1, 0], [1, 8]), [(-8, 1), (0, 2)])
        self.assertEqual(produit([1, 0], [1, 0], [1, 8]), [1, 8, 0, 0])

    def test_x_carre_plus_1_aucune_racine_reelle(self):
        self.assertEqual(oracle.racines([1, 0, 1]), [])

    def test_17x2_288x_moins_17(self):
        # (−144 ± √(144² + 17²))/17, comparées à 45 chiffres ; 144² + 17² = 145² : −17 et 1/17 (2.11 g)
        self.assertRacines([17, 288, -17], [(lambda: (-144 - mp.sqrt(144 ** 2 + 17 ** 2)) / 17, 1),
                                            (lambda: (-144 + mp.sqrt(144 ** 2 + 17 ** 2)) / 17, 1)])
        self.assertRacines([17, 288, -17], [(-17, 1), (F(1, 17), 1)], chiffres=48)


class TestEntrees(CasRacines):
    def test_fractions(self):
        # Javet 2.17 e et f
        self.assertRacines([F(3, 2), -4, -1], [(lambda: (4 - mp.sqrt(22)) / 3, 1), (lambda: (4 + mp.sqrt(22)) / 3, 1)])
        self.assertRacines([F(5, 4), 3, 1], [(-2, 1), (F(-2, 5), 1)])
        self.assertRacines([1, 1, F(1, 4)], [(F(-1, 2), 2)])                   # 2.9 g
        self.assertRacines([9, 0, F(-1, 9)], [(F(-1, 9), 1), (F(1, 9), 1)])     # 2.9 h

    def test_decimaux(self):
        attendu = [(-2, 1), (2, 1)]                                             # 0,5x² − 2 = 0
        for coeffs in (["0.5", 0, -2], [Decimal("0.5"), 0, Decimal("-2")], ["0.50", "0", "-2.0"], [" 1/2 ", 0, "-2"],
                       ["5e-1", 0, -2]):
            with self.subTest(coeffs=coeffs):
                self.assertRacines(coeffs, attendu)
        self.assertEqual(oracle.racines(["1.5", -4, -1]), oracle.racines([F(3, 2), -4, -1]))
        self.assertRacines(["0.1", "-0.3", "0.2"], [(1, 1), (2, 1)])           # 0,1 exact : (x − 1)(x − 2) / 10

    def test_coefficients_proportionnels(self):
        self.assertEqual(oracle.racines([2, -4, 2]), oracle.racines([1, -2, 1]))
        self.assertEqual(oracle.racines([-17, -288, 17]), oracle.racines([17, 288, -17]))

    def test_tete_nulle_retiree(self):
        self.assertRacines([0, 0, 1, -1], [(1, 1)])
        self.assertEqual(oracle.racines([0, 17, 288, -17]), oracle.racines([17, 288, -17]))
        self.assertEqual(oracle.racines(("0", Decimal(0), F(0), 1, 0, 1)), [])

    def test_constante(self):
        for coeffs in ([5], [0, 3], ["-2.5"], (F(1, 3),)):
            with self.subTest(coeffs=coeffs):
                self.assertEqual(oracle.racines(coeffs), [])

    def test_polynome_nul_refuse(self):
        for coeffs in ([], [0], [0, 0, 0], ["0", Decimal("0.0"), F(0)]):
            with self.subTest(coeffs=coeffs):
                with self.assertRaises(ValueError):
                    oracle.racines(coeffs)

    def test_refus_des_entrees_invalides(self):
        types = ([1.0, -2, 1], [1, -2, 0.5], [True, 0, -1], [1, None], [1, 1j], [mp.mpf(1), -1], [1, [2]])
        for coeffs in types:
            with self.subTest(coeffs=coeffs):
                with self.assertRaises(TypeError):
                    oracle.racines(coeffs)
        for coeffs in ([1, "abc"], [1, "1,5"], [1, "1/0"], [1, ""], [Decimal("NaN"), 1], [1, Decimal("Infinity")]):
            with self.subTest(coeffs=coeffs):
                with self.assertRaises(ValueError):
                    oracle.racines(coeffs)
        for coeffs in ("121", 5, {1: 2}, (c for c in [1, -1]), None):
            with self.subTest(coeffs=coeffs):
                with self.assertRaises(TypeError):
                    oracle.racines(coeffs)


class TestDegres(CasRacines):
    def test_degre_1(self):
        self.assertRacines([2, -3], [(F(3, 2), 1)])
        self.assertRacines([-1, 0], [(0, 1)])
        self.assertRacines(["0.25", 1], [(-4, 1)])

    def test_degre_2(self):
        self.assertRacines([1, 0, -5], [(lambda: -mp.sqrt(5), 1), (lambda: mp.sqrt(5), 1)])                     # 2.9 j
        self.assertRacines([1, 5, 2], [(lambda: (-5 - mp.sqrt(17)) / 2, 1), (lambda: (-5 + mp.sqrt(17)) / 2, 1)])  # Javet 2.17 a
        self.assertRacines([1, 1000, -1], [(lambda: (-1000 - mp.sqrt(1000004)) / 2, 1),                           # mantisse 10,000 (E14)
                                           (lambda: (-1000 + mp.sqrt(1000004)) / 2, 1)])
        self.assertRacines([-6, 12, -6], [(1, 2)])                                                                # « −6 = 0 impossible »
        for coeffs in ([3, 5, 12], [3, 0, 4], [1, 0, 4]):                                                         # Δ < 0 : ∅
            with self.subTest(coeffs=coeffs):
                self.assertEqual(oracle.racines(coeffs), [])

    def test_degre_3(self):
        self.assertRacines([1, 0, -1, 0], [(-1, 1), (0, 1), (1, 1)])                       # 2.12 c
        self.assertEqual(produit([1, -1], [-1, 2], [-3, 5]), [3, -14, 21, -10])
        self.assertRacines([3, -14, 21, -10], [(1, 1), (F(5, 3), 1), (2, 1)])              # Az 4.1 d
        self.assertRacines([1, 0, 0, -2], [(lambda: mp.cbrt(2), 1)])                       # deux racines non réelles
        self.assertRacines(produit([1, -1], [1, 0, 1]), [(1, 1)])

    def test_racines_distinctes_proches_non_regroupees(self):
        e = F(1, 10 ** 10)
        self.assertRacines(produit([1, -1], [1, -1 - e]), [(1, 1), (1 + e, 1)])
        self.assertRacines(produit([1, -1], [1, -1 - e], [1, -1 + e]), [(1 - e, 1), (1, 1), (1 + e, 1)])


class TestMultiplicites(CasRacines):
    """Le seuil 10⁻²⁰ tient pour toute multiplicité m ≤ degré : la précision interne (30 × degré + 40 chiffres) laisse un groupe de
    m racines à environ 10^(−précision/m) ≤ 10⁻³⁰ près."""

    def test_multiplicite_3_et_plus(self):
        cas = [(produit(*[[1, -1]] * 3), [(1, 3)]),
               (produit(*[[1, 2]] * 4), [(-2, 4)]),
               (produit(*[[1, -2]] * 5), [(2, 5)]),
               (produit(*[[1, -1]] * 6), [(1, 6)]),
               ([1] + [0] * 10, [(0, 10)]),
               (produit(*[[2, -3]] * 3), [(F(3, 2), 3)]),
               (produit(*[[1, -1]] * 3, *[[1, 2]] * 2), [(-2, 2), (1, 3)])]
        for coeffs, attendu in cas:
            with self.subTest(coeffs=coeffs):
                self.assertRacines(coeffs, attendu)

    def test_multiplicites_irrationnelles_et_non_reelles(self):
        self.assertRacines(produit([1, 0, -2], [1, 0, -2]), [(lambda: -mp.sqrt(2), 2), (lambda: mp.sqrt(2), 2)])
        self.assertRacines(produit([1, 0, 1], [1, 0, 1], [1, -3]), [(3, 1)])                # ±i doubles : non rendues

    def test_somme_des_multiplicites(self):
        for coeffs, toutes_reelles in (([1, -2, 1], True), ([1, 8, 0, 0], True), ([1, 0, 1], False),
                                       (produit([1, 0, 1], [1, -3]), False), (produit(*[[1, 2]] * 4), True)):
            with self.subTest(coeffs=coeffs):
                total = sum(m for _, m in oracle.racines(coeffs))
                self.assertEqual(total == len(coeffs) - 1, toutes_reelles)


class TestSturm(unittest.TestCase):
    """La contre-vérification exacte du nombre de racines réelles distinctes (aucune racine réelle perdue ni ajoutée)."""

    def test_nombre_de_racines_reelles_distinctes(self):
        cas = [([1, -2, 1], 1), ([1, 8, 0, 0], 2), ([1, 0, 1], 0), ([17, 288, -17], 2), ([1, 0, 0, -2], 1), ([1, 0, -1, 0], 3),
               ([2, -3], 1), ([1] + [0] * 10, 1), (produit([1, 0, 1], [1, 0, 1]), 0), (produit(*[[1, -1]] * 3, *[[1, 2]] * 2), 2),
               ([3, -14, 21, -10], 3), (produit([1, 0, -2], [1, 0, -2]), 2), ([1, 1000, -1], 2), ([3, 5, 12], 0)]
        for coeffs, attendu in cas:
            with self.subTest(coeffs=coeffs):
                self.assertEqual(oracle._racines_sturm([int(c) for c in coeffs]), attendu)
                self.assertEqual(len(oracle.racines(coeffs)), attendu)


class TestResultat(unittest.TestCase):
    def test_forme(self):
        r = oracle.racines([1, 8, 0, 0])
        self.assertIsInstance(r, list)
        for x, m in r:
            self.assertIsInstance(x, mp.mpf)
            self.assertIs(type(m), int)
        self.assertEqual(r, sorted(r))
        self.assertLess(r[0][0], r[1][0])

    def test_cinquante_chiffres(self):
        for x, _ in oracle.racines([17, 288, -17]) + oracle.racines([1, 0, -5]):
            with mp.workdps(50):
                self.assertEqual(+x, x)                                  # déjà arrondie à 50 chiffres

    def test_independant_de_la_precision_globale(self):
        attendu = oracle.racines([1, 5, 2])
        for chiffres in (15, 30, 200):
            with mp.workdps(chiffres):
                r = oracle.racines([1, 5, 2])
            with self.subTest(chiffres=chiffres):
                self.assertEqual(r, attendu)


class TestContexteEtIndependance(unittest.TestCase):
    def test_contexte_global_inchange(self):
        avant = (mp.prec, mp.dps, tuple(mp._prec_rounding))
        oracle.racines(produit(*[[1, -1]] * 3))
        self.assertEqual((mp.prec, mp.dps, tuple(mp._prec_rounding)), avant)
        with self.assertRaises(ValueError):
            oracle.racines([0, 0])
        with self.assertRaises(TypeError):
            oracle.racines([1, 0.5])
        self.assertEqual((mp.prec, mp.dps, tuple(mp._prec_rounding)), avant)

    def test_code_independant_des_moteurs(self):
        """Les fonctions de `racines` ne nomment aucun module de moteur (`ed`) ni SymPy : Fraction, Decimal, lcm et mpmath seuls."""
        arbre = ast.parse(inspect.getsource(oracle))
        importes = set()
        for n in arbre.body:
            if isinstance(n, ast.Import):
                importes |= {a.asname or a.name.split(".")[0] for a in n.names}
            elif isinstance(n, ast.ImportFrom):
                importes |= {a.asname or a.name for a in n.names}
        self.assertIn("ed", importes)                                     # l'oracle des arbres d'ED, à côté
        fonctions = [n for n in arbre.body if isinstance(n, ast.FunctionDef)
                     and (n.name == "racines" or n.name.startswith("_racines"))]
        self.assertGreaterEqual(len(fonctions), 6)
        for f in fonctions:
            noms = {n.id for n in ast.walk(f) if isinstance(n, ast.Name)}
            with self.subTest(fonction=f.name):
                self.assertLessEqual(noms & importes, {"Decimal", "F", "lcm"})
                self.assertNotIn("ed", noms)
                attributs = {n.attr for n in ast.walk(f) if isinstance(n, ast.Attribute)}
                self.assertFalse({nom.lower() for nom in noms | attributs} & {"sympy", "sp", "ed"})


if __name__ == "__main__":
    unittest.main()
