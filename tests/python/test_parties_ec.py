"""Chantier « etude-complete », partie P3 : etude-complete/parties.py, partie 1 de l'Étude complète (decisions.md D1, D3).

- Carte « Mise en forme » : lignes exactes (Ex7 du corrigé et autres cas), absence de carte quand rien ne se factorise ; chaque
  factorisation est recoupée par l'oracle mpmath (tests/python/oracle.py : 50 chiffres, sans `evaluer` ni SymPy).
- Chaîne courte d'un dénominateur (« On résout 6x − 12 = 0 ⇔ 6x = 12 ⇔ x = 2. ») : chaînes exactes ; racines annulant le
  dénominateur selon l'oracle, et seules (balayage) ; formes non traitées laissées à l'outil ED.
- Garde-fous (EC-15) : une sonde numérique en désaccord retire la ligne (mise en forme) ou rend la rédaction de l'outil ED (condition).
"""
import random
import re
import unittest
from fractions import Fraction as F
from unittest import mock

import mpmath

import moteurs  # noqa: F401  (chemins des moteurs)
import oracle
import parties
import resoudre_ed as red
import ensemble_def as ed
from noyau import lire, ptex, conditions

mp = mpmath.mp


def lignes_mise_en_forme(entree):
    c = parties.mise_en_forme(lire(entree))
    return None if c is None else [b["html"] for b in c["blocs"]]


def arbre_denominateur(entree):
    out = []
    conditions(lire(entree), out)
    return out[0][1]


class TestMiseEnForme(unittest.TestCase):
    def test_exemple_7_du_corrige(self):
        self.assertEqual(lignes_mise_en_forme("e^((x^2+x-2)/(6x-12))"), [
            r"\(x^{2} + x - 2 = (x + 2)(x - 1)\) (Somme-Produit)",
            r"\(6x - 12 = 6(x - 2)\) (mise en évidence)",
            r"On note \(g(x) = \dfrac{(x + 2)(x - 1)}{6(x - 2)}\), donc \(f(x) = e^{g(x)}\).",
        ])

    def test_mise_en_evidence_puis_somme_produit(self):
        self.assertEqual(lignes_mise_en_forme("e^((2x^2+2x-4)/(x^2-4x))"), [
            r"\(2x^{2} + 2x - 4 = 2(x^{2} + x - 2)\) (mise en évidence)",
            r"\( = 2(x + 2)(x - 1)\) (Somme-Produit)",
            r"\(x^{2} - 4x = x(x - 4)\) (mise en évidence)",
            r"On note \(g(x) = \dfrac{2(x + 2)(x - 1)}{x(x - 4)}\), donc \(f(x) = e^{g(x)}\).",
        ])

    def test_haut_seul_factorise(self):
        self.assertEqual(lignes_mise_en_forme("e^((x^2-9)/(x+1))"), [
            r"\(x^{2} - 9 = (x + 3)(x - 3)\) (Somme-Produit)",
            r"On note \(g(x) = \dfrac{(x + 3)(x - 3)}{x + 1}\), donc \(f(x) = e^{g(x)}\).",
        ])

    def test_pas_de_carte(self):
        """Rien à factoriser, haut constant (d du corrigé), écriture non développée, coefficient dominant négatif, racine double,
        racines non entières, f qui n'est pas e^{haut/bas} : pas de carte (l'option qui affiche le moins)."""
        for entree in ("e^(2/(x^2-4))", "e^((x^2+1)/(x-2))", "e^((x^2+x-2)/(2(x-3)))", "e^((-x^2+1)/(x-1))", "e^((x^2-2x+1)/(x+3))",
                       "e^((x^2-2)/(x+3))", "e^(-x^2)", "x^2*e^(-x)", "(x^2-1)/(x-3)", "2e^((x^2-1)/(x-3))",
                       "e^(x/2)", "e^((x^2-1)/(x-3))+1", "e^((e^x-1)/(x-2))", "e^((x^2-1)/(ln(x)-1))"):
            with self.subTest(entree=entree):
                self.assertIsNone(parties.mise_en_forme(lire(entree)))

    def test_factorisations_confirmees_par_l_oracle(self):
        """Polynômes c·xᵏ·(x − r₁)(x − r₂) et autres, développés : chaque factorisation écrite a la valeur du polynôme (oracle mpmath,
        50 chiffres) en 7 points ; les racines annoncées par Somme-Produit annulent le polynôme."""
        hasard = random.Random(3)
        vus = 0
        for _ in range(150):
            P = [F(hasard.randint(-12, 12)) for _ in range(hasard.randint(2, 4))]
            if hasard.random() < 0.5:                                   # un trinôme unitaire à racines entières, multiplié
                r1, r2 = hasard.randint(-6, 6), hasard.randint(-6, 6)
                c, k = hasard.randint(1, 4), hasard.randint(0, 1)
                P = [F(0)] * k + [F(c * r1 * r2), F(-c * (r1 + r2)), F(c)]
            if P[-1] <= 0:
                continue
            ecrit = ptex(P, "x").replace("{", "(").replace("}", ")")
            A = lire(ecrit)
            if parties.polynome_ecrit(A) is None:
                continue
            lignes, finale, valeur = parties.factorisation(P)
            with self.subTest(P=ecrit):
                if not lignes:
                    self.assertIsNone(valeur)
                    continue
                vus += 1
                for x in (-3.5, -1.25, -0.4, 0.3, 1.7, 2.2, 4.9):
                    self.assertTrue(mp.almosteq(oracle.valeur(A, x), mp.mpf(valeur(x)), rel_eps=1e-12, abs_eps=1e-9))
                if lignes[-1][1] == "Somme-Produit":
                    racines = [-int(n) if s == "+" else int(n) for s, n in re.findall(r"\(x ([+-]) (\d+)\)", finale)]
                    self.assertEqual(len(racines), 2, finale)
                    for r in racines:
                        self.assertEqual(oracle.valeur(A, r), 0)
        self.assertGreater(vus, 40)

    def test_garde_fou_numerique(self):
        """EC-15 : une sonde en désaccord (évaluation faussée) retire les lignes : plus de carte pour l'Ex7."""
        with mock.patch.object(parties, "evaluer", lambda A, x: 12345.0):
            self.assertIsNone(parties.mise_en_forme(lire("e^((x^2+x-2)/(6x-12))")))


class TestResolutionDenominateur(unittest.TestCase):
    CHAINES = {
        "e^((x^2+x-2)/(6x-12))": r"On résout \(6x - 12 = 0 \iff 6x = 12 \iff x = 2\).",
        "e^(2/(x^2-4))": r"On résout \(x^{2} - 4 = 0 \iff x^{2} = 4 \iff x = -2 \text{ ou } x = 2\).",
        "(x^2-1)/(x-3)": r"On résout \(x - 3 = 0 \iff x = 3\).",
        "1/(2x-3)": r"On résout \(2x - 3 = 0 \iff 2x = 3 \iff x = \frac{3}{2}\).",
        "1/(-x+3)": r"On résout \(-x + 3 = 0 \iff -x = -3 \iff x = 3\).",
        "1/(5x)": r"On résout \(5x = 0 \iff x = 0\).",
        "1/(2x^2-8)": r"On résout \(2x^{2} - 8 = 0 \iff 2x^{2} = 8 \iff x^{2} = 4 \iff x = -2 \text{ ou } x = 2\).",
        "1/(x^2-8)": r"On résout \(x^{2} - 8 = 0 \iff x^{2} = 8 \iff x = -2\sqrt{2} \text{ ou } x = 2\sqrt{2}\).",
        "1/(4x^2-1)": r"On résout \(4x^{2} - 1 = 0 \iff 4x^{2} = 1 \iff x^{2} = \frac{1}{4} \iff x = -\frac{1}{2} \text{ ou } x = \frac{1}{2}\).",
        "1/(-x^2+3)": r"On résout \(-x^{2} + 3 = 0 \iff -x^{2} = -3 \iff x^{2} = 3 \iff x = -\sqrt{3} \text{ ou } x = \sqrt{3}\).",
    }
    # formes laissées à l'outil ED : aucune racine, trinôme complet, x seul, écriture factorisée, coefficient fractionnaire, x² = 2/3
    OUTIL_ED = ("x/(x^2+1)", "1/(x^2-3x+2)", "e^(1/x)", "1/(2(x-3))", "1/(x/2-1)", "1/(3x^2-2)", "1/x^2", "1/(x^3-1)",
                "x/(1-3e^x)", "1/(ln(x)-1)", "1/(e^x-2)")

    def blocs(self, entree):
        c = ed.analyser(entree)["conditions"][0]
        return c, parties.blocs_condition(c, arbre_denominateur(entree))

    def test_chaines_courtes(self):
        for entree, chaine in self.CHAINES.items():
            with self.subTest(entree=entree):
                c, blocs = self.blocs(entree)
                self.assertEqual(blocs, [{"type": "formule", "tex": c["cond_tex"]}, {"type": "texte", "html": chaine, "style": "etape"}])

    def test_racines_confirmees_par_l_oracle(self):
        """Chaque racine annoncée annule le dénominateur (oracle mpmath, valeur exacte de la racine reconstruite en 50 chiffres), et le
        dénominateur ne s'annule nulle part ailleurs (changements de signe sur une grille fine de [−10 ; 10])."""
        for entree in self.CHAINES:
            with self.subTest(entree=entree):
                A = arbre_denominateur(entree)
                _, racines = parties.resolution_denominateur(A)
                exactes = [mp.findroot(lambda x: oracle.valeur(A, x), v) for _, v in racines]
                for (_, v), r in zip(racines, exactes):
                    self.assertLess(abs(r - v), 1e-12)
                grille = [mp.mpf(k) / 64 + mp.mpf(1) / 1000 for k in range(-640, 641)]
                changements = [a for a, b in zip(grille, grille[1:]) if oracle.valeur(A, a) * oracle.valeur(A, b) <= 0]
                self.assertEqual(len(changements), len(racines), changements)
                for a in changements:
                    self.assertTrue(any(a - 0.02 <= v <= a + 0.02 for _, v in racines), (a, racines))

    def test_formes_laissees_a_l_outil_ed(self):
        for entree in self.OUTIL_ED:
            with self.subTest(entree=entree):
                c, blocs = self.blocs(entree)
                attendu = [{"type": "formule", "tex": "x \\neq 0"}] if entree == "e^(1/x)" else red.blocs_condition(c)
                self.assertEqual(blocs, attendu)

    def test_garde_fous(self):
        """EC-15 : ensemble différent de celui de l'outil ED, ou sonde en désaccord → rédaction de l'outil ED."""
        c, _ = self.blocs("(x^2-1)/(x-3)")
        A = arbre_denominateur("(x^2-1)/(x-3)")
        faux = dict(c, E_tex=r"\mathbb{R} \setminus \left\{4\right\}")
        self.assertEqual(parties.blocs_condition(faux, A), red.blocs_condition(faux))
        with mock.patch.object(parties, "evaluer", lambda A, x: 1.0):
            self.assertEqual(parties.blocs_condition(c, A), red.blocs_condition(c))
        self.assertEqual(parties.blocs_condition(c, None), red.blocs_condition(c))
        self.assertEqual(parties.blocs_condition(c, lire("x-4")), red.blocs_condition(c))       # arbre d'une autre condition


class TestCartesDomaine(unittest.TestCase):
    def test_sans_condition(self):
        import etude_complete as ec
        cartes = parties.cartes_domaine("f(x) = e^{-x^{2}}", ec.analyse("e^(-x^2)"))
        self.assertEqual([c["titre"] for c in cartes], ["Fonction", "Ensemble de définition"])
        self.assertEqual(cartes[-1]["blocs"], [{"type": "texte", "html": parties.AUCUNE_CONDITION, "style": "etape"},
                                               {"type": "resultat", "tex": "ED = \\mathbb{R}"}])

    def test_plusieurs_conditions(self):
        import etude_complete as ec
        cartes = parties.cartes_domaine("f(x) = …", ec.analyse("ln(x)/(x-2)"))
        self.assertEqual([(c["titre"], c.get("badge")) for c in cartes],
                         [("Fonction", None), ("Condition 1", "logarithme"), ("Condition 2", "dénominateur"), ("Ensemble de définition", None)])
        self.assertIn(r"On résout \(x - 2 = 0 \iff x = 2\).", [b.get("html") for b in cartes[2]["blocs"]])


if __name__ == "__main__":
    unittest.main()
