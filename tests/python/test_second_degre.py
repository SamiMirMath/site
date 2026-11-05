"""Brique moteur/second_degre.py, P1 du chantier equations-2e-degre : le calcul seul, sans texte (decisions.md §§ 3, 6, 8 et 13).

- Oracle : sur le corpus du § 8 (polynômes développés) et sur des polynômes générés à graine fixe (entiers, fractions, décimaux ;
  jamais de float), les solutions de `chemin` sont celles d'`oracle.racines` (mpmath, indépendant), et aucune autre.
- Garde-fou : chaque factorisation (étape réussie, facteurs finals, résultat de `calculer`) est redéveloppée par une multiplication
  écrite ici, dans Q(√m), et comparée au polynôme ; chaque solution est substituée exactement ; un calcul faussé exprès donne
  « ne_conclut_pas ».
- Méthodes : `s_applique` ⇔ `calculer` rend un résultat ; il se redéveloppe (Δ ≥ 0) ; Δ < 0 : S = ∅ par l'oracle ; S-P et tâtonnement
  confrontés à l'oracle (racines entières).
- D28 : la méthode prise est la première de l'ordre du cours qui aboutit, sauf l'exception nommée du point 5 du plan (S-P de plus
  de 12 lignes affichées : la formule).
- Valeurs ≈ du § 8 (E14) par `approx_garantie`, dont x² + 1000x − 1 ; bornes du § 13.5 ; chaque test sous 10 s."""
import random
import time
import unittest
from decimal import Decimal
from fractions import Fraction as F
from unittest import mock

from mpmath import mp

import moteurs  # noqa: F401  (chemins des moteurs)

import expr
import nombres
import oracle
import second_degre as sd
from second_degre import Nombre, Polynome


def R(m):
    return Nombre(0, 1, m)


# Corpus du § 8, développé (P = 0, coefficients en ordre croissant). chemin : [(méthode, aboutit)] attendu (None : forme structurée,
# P4a, dont le chemin sur l'arbre n'est pas encore écrit ; seules les solutions sont contrôlées). S : solutions exactes, croissantes.
CORPUS = {
    "2.9 a": ([-6, 0, 6], [("ME", True), ("IDREM_DIFF", True)], [-1, 1]),
    "2.9 b": ([100, 20, 1], [("IDREM_PLUS", True)], [-10]),
    "2.9 c": ([243, -216, 48], [("ME", True), ("IDREM_MOINS", True)], [F(9, 4)]),
    "2.9 d": ([-9, 0, 4], [("IDREM_DIFF", True)], [F(-3, 2), F(3, 2)]),
    "2.9 e": ([392, -112, 8], [("ME", True), ("IDREM_MOINS", True)], [7]),
    "2.9 f": ([100, 280, 196], [("ME", True), ("IDREM_PLUS", True)], [F(-5, 7)]),
    "2.9 g": ([F(1, 4), 1, 1], [("IDREM_PLUS", True)], [F(-1, 2)]),
    "2.9 h": ([F(-1, 9), 0, 9], [("IDREM_DIFF", True)], [F(-1, 9), F(1, 9)]),
    "2.9 i": ([72, 72, 18], [("ME", True), ("IDREM_PLUS", True)], [-2]),
    "2.9 j": ([-5, 0, 1], [("IDREM_DIFF", True)], [-R(5), R(5)]),
    "2.9 k": ([15, -16, 4], None, [F(3, 2), F(5, 2)]),
    "2.9 l": ([-15, 2, 1], None, [-5, 3]),
    "2.10 a": ([-36, -5, 1], [("SP", True)], [-4, 9]),
    "2.10 b": ([-18, 3, 1], [("SP", True)], [-6, 3]),
    "2.10 c": ([64, 24, 2], [("ME", True), ("SP", True)], [-8, -4]),
    "2.10 d": ([6, 7, 1], [("SP", True)], [-6, -1]),
    "2.10 e": ([-9, 10, -1], [("ME", True), ("SP", True)], [1, 9]),
    "2.10 f": ([30, 11, 1], [("SP", True)], [-6, -5]),
    "2.10 g": ([10, -11, 1], [("SP", True)], [1, 10]),
    "2.10 h": ([-18, 7, 1], [("SP", True)], [-9, 2]),
    "2.10 i": ([45, 18, 1], [("SP", True)], [-15, -3]),
    "2.10 j": ([-32, -4, 1], [("SP", True)], [-4, 8]),
    "2.11 a": ([15, 13, 2], [("TATONNEMENT", True)], [-5, F(-3, 2)]),
    "2.11 b": ([-1, 8, 9], [("TATONNEMENT", True)], [-1, F(1, 9)]),
    "2.11 c": ([-72, -54, 5], [("TATONNEMENT", True)], [F(-6, 5), 12]),
    "2.11 d": ([-28, -1, 2], [("TATONNEMENT", True)], [F(-7, 2), 4]),
    "2.11 e": ([-1, 2, 3], [("TATONNEMENT", True)], [-1, F(1, 3)]),
    "2.11 f": ([-2, 7, 4], [("TATONNEMENT", True)], [-2, F(1, 4)]),
    "2.11 g": ([-17, 288, 17], [("TATONNEMENT", True)], [-17, F(1, 17)]),
    "2.11 h": ([-56, 2, 4], [("ME", True), ("TATONNEMENT", True)], [-4, F(7, 2)]),
    "2.11 i": ([-35, -8, 3], [("TATONNEMENT", True)], [F(-7, 3), 5]),
    "2.11 j": ([-12, -45, 12], [("ME", True), ("TATONNEMENT", True)], [F(-1, 4), 4]),
    "2.12 a": ([12, -8, 1], [("SP", True)], [2, 6]),
    "2.12 b": ([1, 5, 6], [("TATONNEMENT", False), ("FORMULE", True)], [F(-1, 2), F(-1, 3)]),
    "2.12 c": ([0, -1, 0, 1], [("ME", True), ("IDREM_DIFF", True)], [-1, 0, 1]),
    "2.12 d": ([-6, 16, 6], [("ME", True), ("TATONNEMENT", True)], [-3, F(1, 3)]),
    "2.12 e": ([1, 1, -2], None, [F(-1, 2), 1]),
    "2.12 f": ([-48, 8, 1], [("SP", True)], [-12, 4]),
    "2.12 g": ([-16, 0, 1], [("IDREM_DIFF", True)], [-4, 4]),
    "2.12 h": ([12, -12, -9], None, [-2, F(2, 3)]),
    "Javet 2.17 a": ([2, 5, 1], [("SP", False), ("FORMULE", True)], [Nombre(F(-5, 2), F(-1, 2), 17), Nombre(F(-5, 2), F(1, 2), 17)]),
    "Javet 2.17 b": ([2, 4, 1], [("SP", False), ("FORMULE", True)], [-2 - R(2), -2 + R(2)]),
    "Javet 2.17 c": ([-4, -4, 2], [("ME", True), ("SP", False), ("FORMULE", True)], [1 - R(3), 1 + R(3)]),
    "Javet 2.17 d": ([12, 5, 3], [("TATONNEMENT", False), ("FORMULE", True)], []),
    "Javet 2.17 e": ([-1, -4, F(3, 2)], [("FORMULE", True)], [Nombre(F(4, 3), F(-1, 3), 22), Nombre(F(4, 3), F(1, 3), 22)]),
    "Javet 2.17 f": ([1, 3, F(5, 4)], [("FORMULE", True)], [-2, F(-2, 5)]),
    "Az 4.1 c": ([12, 7, 1], [("SP", True)], [-4, -3]),
    "Az 4.1 d": ([-10, 21, -14, 3], None, [1, F(5, 3), 2]),
    "Az 4.1 e": ([4, 0, 3], [("TATONNEMENT", False), ("FORMULE", True)], []),
    "Az 4.1 f": ([0, 0, 8, 1], [("ME", True)], [-8, 0]),
    "(x + 1)(x + 3) = 15": ([-12, 4, 1], [("SP", True)], [-6, 2]),
    # cas limites du § 6
    "x² + 1000x − 1": ([-1, 1000, 1], [("SP", False), ("FORMULE", True)], [Nombre(-500, -1, 250001), Nombre(-500, 1, 250001)]),
    "−6x² + 12x − 6": ([-6, 12, -6], [("ME", True), ("IDREM_MOINS", True)], [1]),
    "0,5x² − 2": ([-2, 0, F(1, 2)], [("FORMULE", True)], [-2, 2]),
    "x² + 4": ([4, 0, 1], [("SP", False), ("FORMULE", True)], []),
    # § 7 et § 13.4
    "x² + 4x − 1": ([-1, 4, 1], [("SP", False), ("FORMULE", True)], [-2 - R(5), -2 + R(5)]),
    "25x² − 3": ([-3, 0, 25], [("IDREM_DIFF", True)], [Nombre(0, F(-1, 5), 3), Nombre(0, F(1, 5), 3)]),
    "3x² − 12x": ([0, -12, 3], [("ME", True)], [0, 4]),
    "12x² − 12x + 3": ([3, -12, 12], [("ME", True), ("IDREM_MOINS", True)], [F(1, 2)]),
    "3x² + 10x − 8": ([-8, 10, 3], [("TATONNEMENT", True)], [-4, F(2, 3)]),
    "x² − x − 42": ([-42, -1, 1], [("SP", True)], [-6, 7]),
    "4x² − 12x + 9": ([9, -12, 4], [("IDREM_MOINS", True)], [F(3, 2)]),
    "2x² + x + 3": ([3, 1, 2], [("TATONNEMENT", False), ("FORMULE", True)], []),
    "3x²": ([0, 0, 3], [], [0]),
    "x² − 8": ([-8, 0, 1], [("IDREM_DIFF", True)], [-2 * R(2), 2 * R(2)]),
    "x² − 1/2": ([F(-1, 2), 0, 1], [("IDREM_DIFF", True)], [Nombre(0, F(-1, 2), 2), Nombre(0, F(1, 2), 2)]),
    "x⁴ − 16": ([-16, 0, 0, 0, 1], [("IDREM_DIFF", True), ("SP", False), ("FORMULE", True), ("IDREM_DIFF", True)], [-2, 2]),
    "x³ − 5x": ([0, -5, 0, 1], [("ME", True), ("IDREM_DIFF", True)], [-R(5), 0, R(5)]),
    "2x + 4": ([4, 2], [("ISOLER", True)], [-2]),
}

# lignes du tableau S-P (§ 8, E6)
LIGNES_SP = {"2.10 a": [(1, -36, -35), (2, -18, -16), (3, -12, -9), (4, -9, -5)], "2.10 b": [(-1, 18, 17), (-2, 9, 7), (-3, 6, 3)],
             "2.10 d": [(1, 6, 7)], "x² − x − 42": [(1, -42, -41), (2, -21, -19), (3, -14, -11), (6, -7, -1)],
             "(x + 1)(x + 3) = 15": [(-1, 12, 11), (-2, 6, 4)], "x² + 4x − 1": [(-1, 1, 0)], "Javet 2.17 c": [(1, -2, -1)],
             "x² + 4": [(1, 4, 5), (2, 2, 4)]}
# tâtonnement (E7) : r et △
TATONNEMENT = {"2.11 a": (-5, 3), "2.11 b": (-1, -1), "2.11 c": (12, 6), "2.11 d": (4, 7), "2.11 e": (-1, -1), "2.11 f": (-2, -1),
               "2.11 g": (-17, -1), "2.11 h": (-4, -7), "2.11 i": (5, 7), "2.11 j": (4, 1), "2.12 d": (-3, -1), "3x² + 10x − 8": (-4, -2)}
# valeurs ≈ (§ 7, § 8, E14), dans l'ordre croissant des solutions
APPROX = {"2.9 j": ["-2{,}236", "2{,}236"], "Javet 2.17 a": ["-4{,}562", "-0{,}438"], "Javet 2.17 b": ["-3{,}414", "-0{,}586"],
          "Javet 2.17 c": ["-0{,}732", "2{,}732"], "Javet 2.17 e": ["-0{,}230", "2{,}897"], "x² + 4x − 1": ["-4{,}236", "0{,}236"],
          "25x² − 3": ["-0{,}346", "0{,}346"], "x² + 1000x − 1": [r"-1\text{’}000{,}001", r"1 \times 10^{-3}"]}


# ---------------------------------------------------------------------------------------------------------------------------
# Outils du test, indépendants de la brique : nombres a + b√m en couples (Fraction, Fraction), produit de polynômes
# ---------------------------------------------------------------------------------------------------------------------------
def couple(x, m):
    """Nombre → (a, b) avec x = a + b√m (m commun)."""
    if x.q == 0:
        return (x.p, F(0))
    assert x.m == m, (x, m)
    return (x.p, x.q)


def radicande(polys):
    ms = {c.m for p in polys for c in p if c.q != 0}
    assert len(ms) <= 1, ms
    return ms.pop() if ms else 1


def produit_test(polys):
    """Produit des polynômes (coefficients Nombre, ordre croissant), réécrit ici : coefficients (a, b) de a + b√m."""
    m = radicande(polys)
    r = [(F(1), F(0))]
    for p in polys:
        q = [couple(c, m) for c in p]
        s = [(F(0), F(0))] * (len(r) + len(q) - 1)
        for i, (a, b) in enumerate(r):
            for j, (c, d) in enumerate(q):
                x, y = s[i + j]
                s[i + j] = (x + a * c + b * d * m, y + a * d + b * c)
        r = s
    while len(r) > 1 and r[-1] == (0, 0):
        r.pop()
    return r


def egal_au_polynome(polys, P):
    return produit_test(polys) == [(F(c), F(0)) for c in Polynome(P)]


def valeur_mp(x):
    with mp.workdps(80):
        return mp.mpf(x.p.numerator) / x.p.denominator + mp.mpf(x.q.numerator) / x.q.denominator * mp.sqrt(x.m)


def solutions_oracle(P):
    """Racines distinctes (mpf) d'oracle.racines (coefficients du plus haut degré au terme constant)."""
    return [r for r, _ in oracle.racines(list(reversed(Polynome(P))))]


class OracleMixin:
    def assertSolutionsOracle(self, P, solutions, nom=""):
        attendues = solutions_oracle(P)
        self.assertEqual(len(solutions), len(attendues), f"{nom} : {solutions} contre {attendues}")
        for x, r in zip(solutions, attendues):
            with mp.workdps(60):
                self.assertLessEqual(abs(valeur_mp(x) - r), mp.mpf(10) ** -40 * max(1, abs(r)), f"{nom} : {x} contre {r}")


# ---------------------------------------------------------------------------------------------------------------------------
# Polynômes générés (graine fixe ; jamais de float)
# ---------------------------------------------------------------------------------------------------------------------------
def generes(n=240, graine=20261105):
    hasard = random.Random(graine)
    rat = lambda: F(hasard.randint(-12, 12), hasard.randint(1, 6))
    dec = lambda: F(Decimal(hasard.choice(["0.5", "-0.25", "1.5", "2.4", "-3.75", "0.2", "-1.2", "4", "-0.1"])))
    polys = []
    for i in range(n):
        genre = i % 8
        if genre == 0:                                   # a(x − r1)(x − r2), racines entières
            a, r1, r2 = hasard.choice([-3, -2, -1, 1, 2, 3, 5]), hasard.randint(-15, 15), hasard.randint(-15, 15)
            P = [a * r1 * r2, -a * (r1 + r2), a]
        elif genre == 1:                                 # trinôme entier quelconque
            P = [hasard.randint(-60, 60), hasard.randint(-40, 40), hasard.choice([i for i in range(-12, 13) if i])]
        elif genre == 2:                                 # racines rationnelles, rendu entier
            p1, q1, p2, q2 = hasard.randint(-9, 9), hasard.randint(1, 7), hasard.randint(-9, 9), hasard.randint(1, 7)
            k = hasard.choice([1, 2, 3, -1])
            P = [k * p1 * p2, -k * (p1 * q2 + p2 * q1), k * q1 * q2]
        elif genre == 3:                                 # fractions
            P = [rat(), rat(), rat() or F(1, 3)]
        elif genre == 4:                                 # décimaux de l'énoncé
            P = [dec(), dec(), dec()]
        elif genre == 5:                                 # Id. rem. : k²x² − m, (kx ± B)²
            k, B = F(hasard.randint(1, 6), hasard.choice([1, 1, 2, 3])), F(hasard.randint(1, 9), hasard.choice([1, 1, 2]))
            P = hasard.choice([[-hasard.randint(1, 30), 0, k * k], [B * B, 2 * k * B, k * k], [B * B, -2 * k * B, k * k],
                               [-B * B, 0, k * k]])
        elif genre == 6:                                 # degré 3 ou 4 : xʲ · trinôme · k
            j, k = hasard.randint(1, 2), hasard.choice([1, 2, -3])
            t = [hasard.randint(-20, 20), hasard.randint(-10, 10), hasard.choice([1, 1, 2, 3])]
            P = [0] * j + [k * c for c in t]
        else:                                            # bicarrés A² − B² et unitaires à grand c
            P = hasard.choice([[-hasard.randint(1, 9) ** 2, 0, 0, 0, hasard.choice([1, 4, 9])],
                               [hasard.randint(-500, 500), hasard.randint(-60, 60), 1]])
        if all(F(c) == 0 for c in P[1:]):
            P[-1] = 1
        polys.append(Polynome(P))
    return polys


GENERES = generes()


def tous():
    return [(nom, Polynome(P)) for nom, (P, _, _) in CORPUS.items()] + [(f"généré {i} {P!r}", P) for i, P in enumerate(GENERES)]


# ---------------------------------------------------------------------------------------------------------------------------
class TestOracleCorpus(OracleMixin, unittest.TestCase):
    def test_corpus_chemin_et_solutions(self):
        for nom, (P, attendu, S) in CORPUS.items():
            with self.subTest(nom):
                r = sd.chemin(Polynome(P))
                if attendu is None:
                    self.assertIn(r["statut"], ("resolu", "hors_cours"))
                    if r["statut"] == "hors_cours":
                        self.assertGreaterEqual(Polynome(P).degre, 3)        # le produit Az 4.1 d développé : P4a, sur l'arbre
                        self.assertSolutionsOracle(P, [Nombre(x) for x in S], nom)
                        continue
                else:
                    self.assertEqual([(e["methode"], e["aboutit"]) for e in r["etapes"]], attendu)
                self.assertEqual(r["statut"], "resolu")
                self.assertEqual(r["solutions"], [sd.nombre(x) for x in S])
                self.assertEqual(r["ensemble"], "fini" if S else "vide")
                self.assertSolutionsOracle(P, r["solutions"], nom)

    def test_lignes_sp(self):
        for nom, lignes in LIGNES_SP.items():
            with self.subTest(nom):
                r = sd.chemin(Polynome(CORPUS[nom][0]))
                sp = next(e for e in r["etapes"] if e["methode"] == "SP")
                self.assertEqual(sp["resultat"]["essais"]["lignes"], lignes)
                self.assertFalse(sp["resultat"]["essais"]["trop"])
                ok = sp["resultat"]["essais"]["ok"]
                if sp["aboutit"]:
                    self.assertEqual(ok, len(lignes) - 1)
                    self.assertEqual((sp["resultat"]["p"], sp["resultat"]["q"]), lignes[-1][:2])
                else:
                    self.assertIsNone(ok)

    def test_tatonnement(self):
        for nom, (r_attendu, triangle) in TATONNEMENT.items():
            with self.subTest(nom):
                e = next(e for e in sd.chemin(Polynome(CORPUS[nom][0]))["etapes"] if e["methode"] == "TATONNEMENT")
                self.assertTrue(e["aboutit"])
                self.assertEqual((e["resultat"]["r"], e["resultat"]["triangle"]), (r_attendu, triangle))
                c = e["cible"][0]
                self.assertEqual(-r_attendu * triangle, c)                   # (−r)·△ = c (E7)

    def test_tatonnement_en_echec_diviseurs(self):
        e = sd.chemin(Polynome([12, 5, 3]))["etapes"][0]                    # Javet 2.17 d : 12 diviseurs, une seule ligne (D1)
        self.assertEqual(e["resultat"]["diviseurs"], [1, -1, 2, -2, 3, -3, 4, -4, 6, -6, 12, -12])
        self.assertEqual(sd.chemin(Polynome([1, 5, 6]))["etapes"][0]["resultat"]["diviseurs"], [1, -1])     # 2.12 b

    def test_formule(self):
        r = sd.racines_formule(Polynome([-1, 4, 1]))                         # E10 : Δ = 20, √Δ = 2√5
        self.assertEqual((r["a"], r["b"], r["c"], r["delta"]), (1, 4, -1, 20))
        self.assertEqual(r["racine_delta"], 2 * R(5))
        self.assertEqual((r["x1"], r["x2"]), (-2 - R(5), -2 + R(5)))
        self.assertEqual(r["x1"].forme_reduite(), (-2, -1, 5, 1))
        e = sd.racines_formule(Polynome([-1, -4, F(3, 2)]))                  # (4 − √22)/3
        self.assertEqual(e["x1"].forme_reduite(), (4, -1, 22, 3))
        d = sd.racines_formule(Polynome([9, -12, 4]))                        # Δ = 0 : x = 3/2 (variante E12)
        self.assertEqual((d["delta"], d["x"], d["x1"], d["solutions"]), (0, Nombre(F(3, 2)), None, [Nombre(F(3, 2))]))
        n = sd.racines_formule(Polynome([12, 5, 3]))
        self.assertEqual((n["delta"], n["solutions"], n["facteurs"]), (-119, [], None))
        a = sd.racines_formule(Polynome([1, 2, -3]))                         # a < 0 : x₁ avec −√Δ, S croissant (§ 13.4)
        self.assertEqual((a["x1"], a["x2"], a["solutions"]), (Nombre(1), Nombre(F(-1, 3)), [Nombre(F(-1, 3)), Nombre(1)]))
        u = sd.racines_formule(Polynome([1, 5, 6]))                          # 2.12 b : √Δ = 1
        self.assertEqual((u["delta"], u["racine_delta"]), (1, Nombre(1)))

    def test_identite_parametres(self):
        cas = {"2.9 c": ((4, 1), 9), "2.9 d": ((2, 1), 3), "2.9 g": ((1, 1), F(1, 2)), "2.9 h": ((3, 1), F(1, 3)),
               "2.9 j": ((1, 1), R(5)), "x² − 8": ((1, 1), 2 * R(2)), "x² − 1/2": ((1, 1), Nombre(0, F(1, 2), 2)),
               "x⁴ − 16": ((1, 2), 4), "25x² − 3": ((5, 1), R(3))}
        for nom, (A, B) in cas.items():
            with self.subTest(nom):
                e = next(e for e in sd.chemin(Polynome(CORPUS[nom][0]))["etapes"] if e["methode"].startswith("IDREM"))
                self.assertEqual((e["resultat"]["A"], e["resultat"]["B"]), (A, sd.nombre(B)))
        self.assertIsNone(sd.identite(Polynome([243, -216, 48])))            # pas une Id. rem. avant la ME (E5)
        self.assertIsNone(sd.identite(Polynome([4, 6, 1])))                  # 2AB = 4x ≠ 6x
        self.assertIsNone(sd.identite(Polynome([-2, 0, 0, 0, 1])))           # x⁴ − 2 : B = √2 seulement pour A = kx

    def test_mise_en_evidence(self):
        cas = {"2.9 a": (6, 0, [-1, 0, 1]), "2.10 e": (-1, 0, [9, -10, 1]), "2.12 c": (1, 1, [-1, 0, 1]),
               "Az 4.1 f": (1, 2, [8, 1]), "3x² − 12x": (3, 1, [-4, 1]), "−6x² + 12x − 6": (-6, 0, [1, -2, 1])}
        for nom, (k, j, reste) in cas.items():
            with self.subTest(nom):
                r = sd.mise_en_evidence(Polynome(CORPUS[nom][0]))
                self.assertEqual((r["k"], r["j"], r["reste"]), (k, j, Polynome(reste)))
        self.assertIsNone(sd.mise_en_evidence(Polynome([F(-1, 9), 0, 9])))  # coefficients non entiers : aucune ME (§ 13.4)
        self.assertIsNone(sd.mise_en_evidence(Polynome([0, 0, 3])))         # 3x² : un seul terme (3x² = 0 ⇔ x = 0)
        self.assertIsNone(sd.mise_en_evidence(Polynome([2, 5, 6])))
        v = sd.mise_en_evidence(Polynome([0, 6, -2]), constante=False)      # E12 : seulement x
        self.assertEqual((v["k"], v["j"], v["reste"]), (1, 1, Polynome([6, -2])))

    def test_produit_nul(self):
        x = (Nombre(10), Nombre(1))
        r = sd.produit_nul([(Nombre(3),), (Nombre(0), Nombre(0), Nombre(2)), x, x])          # D24 : un seul x + 10
        self.assertEqual([g for _, g, _ in r["facteurs"]], ["constante", "monome", "lineaire"])
        self.assertEqual(r["solutions"], [Nombre(-10), Nombre(0)])
        r = sd.produit_nul([(Nombre(-1), Nombre(1)), Polynome([-2, -2, 1])])                  # E9 : la formule sur un facteur
        self.assertEqual([g for _, g, _ in r["facteurs"]], ["lineaire", "formule"])
        self.assertEqual(r["solutions"], [1 - R(3), Nombre(1), 1 + R(3)])

    def test_identite_et_egalite_fausse(self):
        self.assertEqual((sd.chemin(Polynome([0]))["statut"], sd.chemin(Polynome([0]))["ensemble"]), ("resolu", "reels"))
        self.assertEqual(sd.chemin(Polynome([3]))["ensemble"], "vide")
        self.assertEqual(sd.chemin(Polynome([4, 0, -5, 0, 1]))["statut"], "hors_cours")      # x⁴ − 5x² + 4 : P4b (bicarrée)


class TestOracleGeneres(OracleMixin, unittest.TestCase):
    def test_chemin_sur_les_generes(self):
        resolus = 0
        for i, P in enumerate(GENERES):
            with self.subTest(i=i, P=P):
                r = sd.chemin(P)
                self.assertNotEqual(r["statut"], "ne_conclut_pas")
                if P.degre <= 2:
                    self.assertEqual(r["statut"], "resolu")
                if r["statut"] == "hors_cours":
                    continue
                resolus += 1
                self.assertSolutionsOracle(P, r["solutions"], repr(P))
                self.assertEqual(r["ensemble"], "fini" if r["solutions"] else "vide")
        self.assertGreater(resolus, 200)

    def test_jamais_de_float(self):
        with self.assertRaises(TypeError):
            Polynome([0.5, 1])
        with self.assertRaises(TypeError):
            Nombre(1.5)
        for P in GENERES:
            for c in P:
                self.assertIs(type(c), F)


class TestGardeFou(unittest.TestCase):
    """Chaque factorisation affichée se redéveloppe exactement (produit réécrit ici) ; chaque solution annule P exactement."""

    def test_etapes_et_facteurs_se_redeveloppent(self):
        for nom, P in tous():
            r = sd.chemin(P)
            if r["statut"] != "resolu" or r["ensemble"] == "reels":
                continue
            with self.subTest(nom):
                for e in r["etapes"]:
                    f = e["resultat"].get("facteurs") if e["aboutit"] else None
                    if f is not None:
                        self.assertTrue(egal_au_polynome(f, e["cible"]), f"{e['methode']} : {f} contre {e['cible']}")
                if r["facteurs"]:
                    self.assertTrue(egal_au_polynome(r["facteurs"], P))
                for x in r["solutions"]:
                    self.assertTrue(sd.verifier_solution(P, x))

    def test_redevelopper_comme_le_test(self):
        for nom, P in tous():
            r = sd.chemin(P)
            if r["facteurs"]:
                with self.subTest(nom):
                    m = radicande(r["facteurs"])
                    self.assertEqual([couple(c, m) for c in sd.redevelopper(r["facteurs"])], produit_test(r["facteurs"]))

    def test_un_calcul_fausse_ne_conclut_pas(self):
        vrai = sd.racines_formule

        def faux(P):
            r = vrai(P)
            if r["x1"] is not None:
                r["x1"] = r["x1"] + 1
                r["solutions"] = sd.croissant([r["x1"], r["x2"]])
                r["facteurs"] = [(Nombre(r["a"]),), (-r["x1"], Nombre(1)), (-r["x2"], Nombre(1))]
            return r
        with mock.patch.object(sd, "racines_formule", faux):
            r = sd.chemin(Polynome([-1, 4, 1]))
        self.assertEqual((r["statut"], r["solutions"]), ("ne_conclut_pas", []))

        vraie = sd.identite

        def fausse(P):
            r = vraie(P)
            if r is not None and r["methode"] == "IDREM_DIFF":
                r["facteurs"] = [(r["facteurs"][0][0] + 1,) + r["facteurs"][0][1:], r["facteurs"][1]]
            return r
        with mock.patch.object(sd, "identite", fausse):
            self.assertEqual(sd.chemin(Polynome([-9, 0, 4]))["statut"], "ne_conclut_pas")
        self.assertEqual(sd.chemin(Polynome([-9, 0, 4]))["statut"], "resolu")

    def test_verifier_solution(self):
        self.assertTrue(sd.verifier_solution(Polynome([-1, 4, 1]), -2 + R(5)))
        self.assertFalse(sd.verifier_solution(Polynome([-1, 4, 1]), -2 + R(3)))
        self.assertFalse(sd.verifier_solution(Polynome([-1, 4, 1]), Nombre(F(236, 1000))))


class TestMethodes(OracleMixin, unittest.TestCase):
    """§ 6 et § 13.4 : s_applique ⇔ calculer aboutit ; le résultat se redéveloppe (Δ ≥ 0) ; Δ < 0 : S = ∅ par l'oracle."""

    def test_s_applique_et_calculer(self):
        for nom, P in tous():
            for methode in sd.METHODES:
                with self.subTest(nom, methode=methode):
                    r = sd.calculer(methode, P)
                    self.assertEqual(sd.s_applique(methode, P), r is not None)
                    if r is None:
                        continue
                    if r["facteurs"] is not None:
                        self.assertTrue(egal_au_polynome(r["facteurs"], P))
                    else:
                        self.assertEqual(methode, "FORMULE")
                        self.assertLess(r["delta"], 0)
                        self.assertEqual(solutions_oracle(P), [])

    def test_sp_et_tatonnement_contre_l_oracle(self):
        """S-P : un couple d'entiers existe ⇔ deux racines entières (oracle) ; tâtonnement : une racine entière (oracle)."""
        for nom, P in tous():
            if P.degre != 2 or not P.entiers() or P[0] == 0:
                continue
            with self.subTest(nom):
                racines = oracle.racines(list(reversed(P)))
                entieres = [r for r, _ in racines if abs(r - mp.nint(r)) < mp.mpf(10) ** -30]
                multiplicites = sum(m for r, m in racines if abs(r - mp.nint(r)) < mp.mpf(10) ** -30)
                self.assertEqual(sd.s_applique("SP", P), P[2] == 1 and multiplicites == 2)
                self.assertEqual(sd.s_applique("TATONNEMENT", P), P[2] >= 2 and bool(entieres))
                if sd.s_applique("TATONNEMENT", P):
                    r = sd.racine_entiere_unique(P)
                    self.assertIn(r, [int(mp.nint(x)) for x in entieres])
                    self.assertEqual(r, min((int(mp.nint(x)) for x in entieres), key=lambda v: (abs(v), v < 0)))

    def test_formule_s_applique_toujours(self):
        for nom, P in tous():
            if P.degre == 2:
                with self.subTest(nom):
                    self.assertTrue(sd.s_applique("FORMULE", P))
        self.assertFalse(sd.s_applique("FORMULE", Polynome([0, -1, 0, 1])))
        self.assertFalse(sd.s_applique("ME", Polynome([4, 2])))              # degré 1 : on isole (E13)

    def test_methode_inconnue(self):
        with self.assertRaises(ValueError):
            sd.calculer("DELTA", Polynome([1, 2, 1]))


class TestOrdreDuCours(unittest.TestCase):
    """D28 : la méthode prise sur chaque cible est la première de l'ordre du cours qui aboutit (s_applique), sauf l'exception
    nommée du point 5 du plan : S-P de plus de 12 lignes affichées, où le chemin prend la formule alors qu'un couple existe."""

    @staticmethod
    def premiere(cible, methodes=sd.ORDRE_DU_COURS):
        return next((m for m in methodes if sd.s_applique(m, cible)), None)

    def test_d28(self):
        exceptions = 0
        for nom, P in tous():
            r = sd.chemin(P)
            for e in r["etapes"]:
                if not e["aboutit"]:                                         # tentative en échec : la méthode n'aboutit pas…
                    with self.subTest(nom, echec=e["methode"], cible=e["cible"]):
                        trop = e["methode"] == "SP" and e["resultat"]["essais"]["trop"]
                        self.assertTrue(trop or not sd.s_applique(e["methode"], e["cible"]))      # … sauf l'exception nommée
                    continue
                if e["methode"] == "ISOLER":
                    continue
                with self.subTest(nom, cible=e["cible"]):
                    famille = "IDREM" if e["methode"].startswith("IDREM") else e["methode"]
                    attendue = self.premiere(e["cible"])
                    if attendue == "SP" and famille == "FORMULE":
                        c, b, _ = e["cible"]
                        self.assertTrue(sd.essais_sp(b, c)["trop"], "exception D28 : seulement au-delà de 12 lignes")
                        exceptions += 1
                    else:
                        self.assertEqual(famille, attendue)
        self.assertEqual(exceptions, 0)                                      # aucune dans le corpus ni les générés

    def test_exception_nommee_plus_de_12_lignes(self):
        """720 720 a pour diviseurs 1, 2, …, 13 : le couple (13, 55 440) est à la 13e ligne, (12, 60 060) à la 12e."""
        trop = Polynome([720720, 13 + 55440, 1])
        self.assertTrue(sd.s_applique("SP", trop))                          # un couple existe…
        essais = sd.essais_sp(13 + 55440, 720720)
        self.assertTrue(essais["trop"])
        self.assertEqual(len(essais["lignes"]), 13)
        r = sd.chemin(trop)
        self.assertEqual([(e["methode"], e["aboutit"]) for e in r["etapes"]], [("SP", False), ("FORMULE", True)])   # … la formule
        self.assertTrue(r["etapes"][0]["resultat"]["essais"]["trop"])
        self.assertEqual(r["solutions"], [Nombre(-55440), Nombre(-13)])
        juste = Polynome([720720, 12 + 60060, 1])
        r = sd.chemin(juste)
        self.assertEqual([(e["methode"], e["aboutit"]) for e in r["etapes"]], [("SP", True)])
        self.assertEqual(len(r["etapes"][0]["resultat"]["essais"]["lignes"]), 12)
        echec = sd.essais_sp(1, 720720)                                     # aucun couple : plus de 12 lignes, pas de tableau
        self.assertTrue(echec["trop"])
        self.assertIsNone(echec["ok"])

    def test_x2_plus_4_par_d28(self):
        """Point 4 du plan : x² + 4 passe par le S-P (b = 0, tableau en échec), puis Δ < 0."""
        r = sd.chemin(Polynome([4, 0, 1]))
        self.assertEqual([(e["methode"], e["aboutit"]) for e in r["etapes"]], [("SP", False), ("FORMULE", True)])
        self.assertEqual(r["etapes"][1]["resultat"]["delta"], -16)

    def test_variante_par_la_formule(self):
        """E12 : seulement xʲ en évidence, puis la formule ; Δ = 0 avec des coefficients entiers."""
        r = sd.chemin(Polynome([9, -12, 4]), sd.ORDRE_PAR_LA_FORMULE)
        self.assertEqual([e["methode"] for e in r["etapes"]], ["FORMULE"])
        self.assertEqual(r["etapes"][0]["resultat"]["delta"], 0)
        r = sd.chemin(Polynome([0, 6, -2, 4]), sd.ORDRE_PAR_LA_FORMULE)
        self.assertEqual([e["methode"] for e in r["etapes"]], ["ME", "FORMULE"])
        self.assertEqual(r["etapes"][0]["resultat"]["k"], 1)


class TestNombre(unittest.TestCase):
    def test_arithmetique(self):
        a, b = 1 + R(3), 1 - R(3)
        self.assertEqual(a * b, Nombre(-2))
        self.assertEqual(a + b, Nombre(2))
        self.assertEqual((a / b) * b, a)
        self.assertEqual(Nombre(0, 2, 12), Nombre(0, 4, 3))                 # √12 = 2√3 : écriture unique
        self.assertEqual(Nombre(5, 3, 1), Nombre(8))
        self.assertEqual(Nombre(5, 0, 7).m, 1)
        with self.assertRaises(TypeError):
            R(2) + R(3)

    def test_racine(self):
        self.assertEqual(Nombre.racine(20), 2 * R(5))
        self.assertEqual(Nombre.racine(F(1, 2)), Nombre(0, F(1, 2), 2))
        self.assertEqual(Nombre.racine(F(9, 4)), Nombre(F(3, 2)))
        self.assertEqual(Nombre.racine(0), Nombre(0))
        with self.assertRaises(ValueError):
            Nombre.racine(-1)

    def test_signe_et_comparaison(self):
        self.assertEqual((1 - R(3)).signe(), -1)
        self.assertEqual((2 - R(3)).signe(), 1)
        self.assertEqual((-2 + R(3)).signe(), -1)
        self.assertEqual(Nombre(0).signe(), 0)
        valeurs = [R(2), -R(3), Nombre(F(3, 2)), 1 + R(5), Nombre(-2), R(3) - 1, Nombre(0, -1, 2), Nombre(F(7, 5))]
        triees = sd.croissant(valeurs)
        with mp.workdps(50):
            self.assertEqual([valeur_mp(x) for x in triees], sorted(valeur_mp(x) for x in valeurs))
        self.assertLess(R(2), Nombre(F(3, 2)))
        self.assertGreater(R(3), R(2))

    def test_forme_reduite(self):
        self.assertEqual(((-4 - 2 * R(5)) / 2).forme_reduite(), (-2, -1, 5, 1))      # E11
        self.assertEqual(((2 - 2 * R(3)) / 2).forme_reduite(), (1, -1, 3, 1))
        self.assertEqual(Nombre(F(-5, 2), F(-1, 2), 17).forme_reduite(), (-5, -1, 17, 2))
        self.assertEqual(Nombre(0, F(1, 5), 3).forme_reduite(), (0, 1, 3, 5))
        self.assertEqual(Nombre(F(-1, 2)).forme_reduite(), (-1, 0, 1, 2))

    def test_encadrement(self):
        for x in (R(2), -2 - R(5), Nombre(F(4, 3), F(-1, 3), 22), Nombre(-500, 1, 250001)):
            for chiffres in (5, 20, 60):
                bas, haut = x.encadrement(chiffres)
                with mp.workdps(100):
                    v = valeur_mp(x)
                    self.assertLessEqual(mp.mpf(bas.numerator) / bas.denominator, v)
                    self.assertLessEqual(v, mp.mpf(haut.numerator) / haut.denominator)
                self.assertLessEqual(haut - bas, abs(x.q) * F(1, 10 ** chiffres))


class TestApprox(unittest.TestCase):
    def test_valeurs_du_corpus(self):
        for nom, attendu in APPROX.items():
            with self.subTest(nom):
                r = sd.chemin(Polynome(CORPUS[nom][0]))
                self.assertEqual([sd.approx_garantie(x) for x in r["solutions"]], attendu)

    def test_comme_approx_de_la_valeur(self):
        """approx_garantie(x) = nombres.approx de x calculé à 60 chiffres (oracle), et approx_garantie d'un rationnel = approx."""
        for nom, P in tous():
            r = sd.chemin(P)
            for x in r["solutions"]:
                with self.subTest(nom, x=x):
                    with mp.workdps(60):
                        v = F(mp.nstr(valeur_mp(x), 60, strip_zeros=False, min_fixed=-mp.inf, max_fixed=mp.inf)) if x.q else x.p
                    self.assertEqual(sd.approx_garantie(x), nombres.approx(v))
        self.assertEqual(sd.approx_garantie(Nombre(F(1, 16))), "0{,}063")


class TestBornes(unittest.TestCase):
    """§ 13.5 : degré ≤ 8, numérateurs et dénominateurs ≤ 9 chiffres ; message des bornes (HorsBornes) au-delà."""

    @staticmethod
    def lire(texte):
        g, d = expr.lire_membres(texte)
        return expr.Op("-", g, d)

    def test_vers_polynome(self):
        self.assertEqual(sd.vers_polynome(self.lire("(x+1)(x+3)=15"), "x"), Polynome([-12, 4, 1]))
        self.assertEqual(sd.vers_polynome(self.lire("t^2+t+1/4=0"), "t"), Polynome([F(1, 4), 1, 1]))
        self.assertEqual(sd.vers_polynome(self.lire("x^8=1"), "x").degre, 8)
        self.assertEqual(sd.vers_polynome(self.lire("123456789x^2=1/987654321"), "x")[2], 123456789)
        for texte in ("x^9=0", "(x+1)^9=0", "x^4*x^5=1", "1234567890x=1", "x/1234567890=1", "x^2=1/1234567890",
                      "(x+99999)^2=0"):
            with self.subTest(texte):
                with self.assertRaises(sd.HorsBornes):
                    sd.vers_polynome(self.lire(texte), "x")
        with self.assertRaises(ValueError):
            sd.vers_polynome(self.lire("x+y=1"), "x")

    def test_essais_et_diviseurs(self):
        with self.assertRaises(sd.HorsBornes):
            sd.essais_sp(1, 10 ** 9)
        with self.assertRaises(sd.HorsBornes):
            sd.diviseurs_signes(-10 ** 9)
        self.assertEqual(len(sd.diviseurs_signes(999999937)), 4)            # premier : ±1, ±999 999 937 (pas de borne d'affichage)
        with self.assertRaises(sd.HorsBornes):
            Nombre.racine(F(10 ** 12 + 39, 10 ** 9 + 7))
        self.assertEqual(Nombre.racine(F(10 ** 20)), Nombre(10 ** 10))      # un carré se lit sans borne

    def test_plus_grands_coefficients_sous_10_s(self):
        """Le plus lent permis par les bornes : coefficients de 9 chiffres ; Δ premier juste sous 10¹² (noyau.squarefree, environ
        0,1 s) ; au-delà, un Δ non carré donne le message des bornes (HorsBornes), jamais un calcul sans fin ni un résultat douteux."""
        debut = time.perf_counter()
        r = sd.chemin(Polynome([-499997, 999999, 1]))                        # Δ = 999 999 999 989, premier
        self.assertEqual(r["etapes"][-1]["resultat"]["delta"], 999999999989)
        self.assertEqual(r["solutions"][0], Nombre(F(-999999, 2), F(-1, 2), 999999999989))
        for P in ([-999999937, 999999999, 999999998], [999999999, 1, 1], [-1, 999999999, 1], [999999893, 0, -1],
                  [-999999937, 0, 1], [-999999937, 999999999, 1]):
            with self.subTest(P=P):
                try:
                    r = sd.chemin(Polynome(P))
                except sd.HorsBornes:
                    continue
                self.assertEqual(r["statut"], "resolu")
        self.assertLess(time.perf_counter() - debut, 10)
        with self.assertRaises(sd.HorsBornes):
            sd.chemin(Polynome([-999999937, 999999999, 999999998]))           # Δ ≈ 5 × 10¹⁸, non carré

if __name__ == "__main__":
    unittest.main()
