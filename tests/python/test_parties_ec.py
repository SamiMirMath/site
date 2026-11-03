"""Chantier « etude-complete », partie P3 : etude-complete/parties.py, partie 1 de l'Étude complète (decisions.md D1, D3).

- Carte « Mise en forme » : lignes exactes (Ex7 du corrigé et autres cas), absence de carte quand rien ne se factorise ; chaque
  factorisation est recoupée par l'oracle mpmath (tests/python/oracle.py : 50 chiffres, sans `evaluer` ni SymPy).
- Chaîne courte d'un dénominateur (« On résout 6x − 12 = 0 ⇔ 6x = 12 ⇔ x = 2. ») : chaînes exactes ; racines annulant le
  dénominateur selon l'oracle, et seules (balayage) ; formes non traitées laissées à l'outil ED.
- Garde-fous (EC-15) : une sonde numérique en désaccord retire la ligne (mise en forme) ou rend la rédaction de l'outil ED (condition).

Partie 2, parité (D4, P4) : cartes exactes du corrigé et des entrées de la page ; chaque conclusion recoupée par l'oracle mpmath
(f(−x) = ±f(x) sur une grille, point a ∈ ED avec −a ∉ ED, valeurs des contre-exemples et leurs arrondis), sur les entrées de la page et
une famille tirée au hasard ; garde-fous forcés (SymPy et sonde en désaccord dans les deux sens, sonde dans la zone grise, borne
approchée, ligne de la chaîne ou valeur écrite fausse, arrondis affichés égaux, SymPy absent) : un message clair, jamais de conclusion.

Partie 6, graphe (D15, P8) : ronds vides recoupés par l'oracle mpmath (limites latérales par sondes, 50 chiffres) sur une famille de
fonctions (un côté fini, deux limites finies différentes, trous et bords laissés à l'outil Limites, limites infinies) ; garde-fous forcés
(limite SymPy fausse ou en échec, sonde qui s'éloigne, du mauvais côté ou non définie, point dans l'ED, écriture illisible, SymPy
absent) : pas de rond ; cadrage (decisions.md §3) recoupé par l'oracle : points à montrer dans la fenêtre, approche de chaque AH.
"""
import random
import re
import sys
import unittest
from contextlib import ExitStack
from decimal import Decimal, ROUND_HALF_UP
from fractions import Fraction as F
from unittest import mock

import mpmath

import moteurs  # noqa: F401  (chemins des moteurs)
import oracle
import parties
import resoudre_ed as red
import ensemble_def as ed
from noyau import lire, ptex, conditions, Num, Iv, Nb
import etude_complete as ec
import resoudre_ec as rec
from cas import entrees_page, CAS_LIMITES

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
        # trinôme unitaire à racines entières : Somme-Produit (question 11), facteurs par racine croissante
        "1/(x^2-3x+2)": r"On résout \(x^{2} - 3x + 2 = 0 \iff (x - 1)(x - 2) = 0\) (Somme-Produit) \(\iff x = 1 \text{ ou } x = 2\) (produit nul).",
        "x/(x^2+x-6)": r"On résout \(x^{2} + x - 6 = 0 \iff (x + 3)(x - 2) = 0\) (Somme-Produit) \(\iff x = -3 \text{ ou } x = 2\) (produit nul).",
        "e^(1/(x^2-7x+10))": r"On résout \(x^{2} - 7x + 10 = 0 \iff (x - 2)(x - 5) = 0\) (Somme-Produit) \(\iff x = 2 \text{ ou } x = 5\) (produit nul).",
    }
    # formes laissées à l'outil ED : aucune racine, trinôme à racines non entières, racine double, sans terme constant, non unitaire,
    # x seul, écriture factorisée, coefficient fractionnaire, x² = 2/3
    OUTIL_ED = ("x/(x^2+1)", "1/(x^2-3x+1)", "1/(x^2-2x+1)", "1/(x^2-4x)", "1/(2x^2-6x+4)", "e^(1/x)", "1/(2(x-3))", "1/(x/2-1)", "1/(3x^2-2)", "1/x^2", "1/(x^3-1)",
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

    def test_garde_fous_somme_produit(self):
        """Question 11 : ensemble différent de celui de l'outil ED, sonde en désaccord, ou produit développé qui ne redonne pas le
        trinôme (garde-fou exact de la factorisation) → rédaction de l'outil ED."""
        c, blocs = self.blocs("1/(x^2-3x+2)")
        A = arbre_denominateur("1/(x^2-3x+2)")
        self.assertIn("Somme-Produit", blocs[1]["html"])
        faux = dict(c, E_tex=r"\mathbb{R} \setminus \left\{1 \,;\, 3\right\}")
        self.assertEqual(parties.blocs_condition(faux, A), red.blocs_condition(faux))
        with mock.patch.object(parties, "evaluer", lambda A, x: 1.0):
            self.assertEqual(parties.blocs_condition(c, A), red.blocs_condition(c))
        with mock.patch.object(parties, "pmul", lambda p, q: [F(7)]):
            self.assertIsNone(parties.resolution_somme_produit([F(2), F(-3), F(1)]))
            self.assertEqual(parties.blocs_condition(c, A), red.blocs_condition(c))

    def test_chaine_en_ligne(self):
        self.assertEqual(parties.chaine_en_ligne(["a = 0", "b = 0"]), r"\(a = 0 \iff b = 0\)")
        self.assertEqual(parties.chaine_en_ligne(["a = 0", ("b = 0", "P"), "c = 0", ("d = 0", "Q")]),
                         r"\(a = 0 \iff b = 0\) (P) \(\iff c = 0 \iff d = 0\) (Q)")


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


# ---------------------------------------------------------------------------------------------------------------------------
# Partie 2. Parité (D4)
# ---------------------------------------------------------------------------------------------------------------------------
def cartes_parite(entree):
    return parties.cartes_parite(ec.analyse(entree))


def resume(cartes):
    return [(c["titre"], [b["html"] for b in c["blocs"]]) for c in cartes]


SYM = ("Symétrie de l'ED", [parties.SYMETRIQUE])
MESSAGES = (parties.DOUTE, parties.NON_REDIGEE, parties.SANS_CONTRE_EXEMPLE)


def message(texte):
    return [("Parité", [texte])]


class TestParite(unittest.TestCase):
    CARTES = {
        "e^((x^2+x-2)/(6x-12))": [("Symétrie de l'ED", [
            r"\(-2 \in ED\), mais \(2 \notin ED\) : ED n'est pas symétrique par rapport à 0.", parties.NI])],
        "e^(-x^2)": [SYM, ("Calcul de f(−x)", [
            r"\(f(-x) = e^{-\left(-x\right)^{2}}\) (on remplace x par −x)",
            r"\( = e^{-x^{2}}\) (car \(\left(-x\right)^{2} = x^{2}\))",
            r"\( = f(x)\)", parties.PAIRE])],
        "(x^2-6)e^(-2x)": [SYM, ("Pas impaire", [
            r"\(f(0) = -6 \neq 0\)", r"Une fonction impaire vérifie \(f(0) = 0\) : f n'est pas impaire."]), ("Pas paire", [
            r"\(f(1) = -5e^{-2} \approx -0{,}68\)", r"\(f(-1) = -5e^{2} \approx -36{,}95\)", r"\(f(-1) \neq f(1)\) : f n'est pas paire.", parties.NI])],
        "e^x(6-e^x)": [SYM, ("Pas impaire", [
            r"\(f(0) = 5 \neq 0\)", r"Une fonction impaire vérifie \(f(0) = 0\) : f n'est pas impaire."]), ("Pas paire", [
            r"\(f(1) = e\,\left(6 - e\right) \approx 8{,}92\)", r"\(f(-1) = e^{-1}\,\left(6 - e^{-1}\right) \approx 2{,}07\)",
            r"\(f(-1) \neq f(1)\) : f n'est pas paire.", parties.NI])],
        "e^(2/(x^2-4))": [SYM, ("Calcul de f(−x)", [
            r"\(f(-x) = e^{\frac{2}{\left(-x\right)^{2} - 4}}\) (on remplace x par −x)",
            r"\( = e^{\frac{2}{x^{2} - 4}}\) (car \(\left(-x\right)^{2} = x^{2}\))", r"\( = f(x)\)", parties.PAIRE])],
        "x^3-3x": [SYM, ("Calcul de f(−x)", [
            r"\(f(-x) = \left(-x\right)^{3} - 3\left(-x\right)\) (on remplace x par −x)",
            r"\( = -x^{3} + 3x\) (car \(\left(-x\right)^{3} = -x^{3}\) ; règle des signes)",
            r"\( = -\left(x^{3} - 3x\right)\) (mise en évidence de −1)", r"\( = -f(x)\)", parties.IMPAIRE])],
        "x/(x^2+1)": [SYM, ("Calcul de f(−x)", [
            r"\(f(-x) = \frac{\left(-x\right)}{\left(-x\right)^{2} + 1}\) (on remplace x par −x)",
            r"\( = -\frac{x}{x^{2} + 1}\) (car \(\left(-x\right)^{2} = x^{2}\) ; règle des signes)", r"\( = -f(x)\)", parties.IMPAIRE])],
        "x^4-2x^2": [SYM, ("Calcul de f(−x)", [
            r"\(f(-x) = \left(-x\right)^{4} - 2\left(-x\right)^{2}\) (on remplace x par −x)",
            r"\( = x^{4} - 2x^{2}\) (car \(\left(-x\right)^{4} = x^{4}\) et \(\left(-x\right)^{2} = x^{2}\))",
            r"\( = f(x)\)", parties.PAIRE])],
        "e^(1/x)": [SYM, ("Pas impaire", [
            r"\(f(1) = e \approx 2{,}72\), donc \(-f(1) \approx -2{,}72\)", r"\(f(-1) = e^{-1} \approx 0{,}37\)",
            r"\(f(-1) \neq -f(1)\) : f n'est pas impaire."]), ("Pas paire", [
            r"\(f(1) = e \approx 2{,}72\)", r"\(f(-1) = e^{-1} \approx 0{,}37\)", r"\(f(-1) \neq f(1)\) : f n'est pas paire.", parties.NI])],
        "x^2-4x+3": [SYM, ("Pas impaire", [
            r"\(f(0) = 3 \neq 0\)", r"Une fonction impaire vérifie \(f(0) = 0\) : f n'est pas impaire."]), ("Pas paire", [
            r"\(f(1) = 0\)", r"\(f(-1) = 8\)", r"\(f(-1) \neq f(1)\) : f n'est pas paire.", parties.NI])],
        "x^3-x": [SYM, ("Calcul de f(−x)", [
            r"\(f(-x) = \left(-x\right)^{3} - \left(-x\right)\) (on remplace x par −x)",
            r"\( = -x^{3} + x\) (car \(\left(-x\right)^{3} = -x^{3}\) ; règle des signes)",
            r"\( = -\left(x^{3} - x\right)\) (mise en évidence de −1)", r"\( = -f(x)\)", parties.IMPAIRE])],
        "x^2*e^x": [SYM, ("Pas impaire", [
            r"\(f(1) = e \approx 2{,}72\), donc \(-f(1) \approx -2{,}72\)", r"\(f(-1) = e^{-1} \approx 0{,}37\)",
            r"\(f(-1) \neq -f(1)\) : f n'est pas impaire."]), ("Pas paire", [
            r"\(f(1) = e \approx 2{,}72\)", r"\(f(-1) = e^{-1} \approx 0{,}37\)", r"\(f(-1) \neq f(1)\) : f n'est pas paire.", parties.NI])],
        "x^3+x^2": [SYM, ("Pas impaire", [
            r"\(f(1) = 2\), donc \(-f(1) = -2\)", r"\(f(-1) = 0\)", r"\(f(-1) \neq -f(1)\) : f n'est pas impaire."]), ("Pas paire", [
            r"\(f(1) = 2\)", r"\(f(-1) = 0\)", r"\(f(-1) \neq f(1)\) : f n'est pas paire.", parties.NI])],
        "ln(x)/x": [("Symétrie de l'ED", [
            r"\(1 \in ED\), mais \(-1 \notin ED\) : ED n'est pas symétrique par rapport à 0.", parties.NI])],
        "(x^2-1)/(x-3)": [("Symétrie de l'ED", [
            r"\(-3 \in ED\), mais \(3 \notin ED\) : ED n'est pas symétrique par rapport à 0.", parties.NI])],
        "sqrt(x+1)": [("Symétrie de l'ED", [
            r"\(2 \in ED\), mais \(-2 \notin ED\) : ED n'est pas symétrique par rapport à 0.", parties.NI])],
        "sqrt(x-1)": [("Symétrie de l'ED", [
            r"\(1 \in ED\), mais \(-1 \notin ED\) : ED n'est pas symétrique par rapport à 0.", parties.NI])],
        "e^x+e^(-x)": [SYM] + message(parties.NON_REDIGEE),
        "x^2+x/10000": [SYM] + message(parties.SANS_CONTRE_EXEMPLE),
    }

    def test_cartes_exactes(self):
        """D4 : cartes du corrigé (decisions.md §4–5 : Ex7, a–d) et d'autres formes : ED non symétrique (borne puis 1, 2…), chaîne paire
        ou impaire (une étape par ligne, propriété nommée), f(0) ≠ 0 et contre-exemples (entier exact sans « ≈ »), messages."""
        for entree, attendu in self.CARTES.items():
            with self.subTest(entree=entree):
                self.assertEqual(resume(cartes_parite(entree)), attendu)

    def test_contre_exemple_a_suivant_si_les_arrondis_coincident(self):
        """x² + x/1000 : pour a = 1, 2, 1/2, 3, 4, 1/3, f(a) et f(−a) ont le même arrondi (1,00 et 1,00…) ; a = 5 : 25,01 et 25,00."""
        pas_paire = dict(resume(cartes_parite("x^2+x/1000")))["Pas paire"]
        self.assertEqual(pas_paire[:2], [r"\(f(5) = \frac{5001}{200} \approx 25{,}01\)", r"\(f(-5) = \frac{4999}{200} \approx 25{,}00\)"])

    def test_f0_non_entier_dans_la_formule(self):
        """« f(0) = e^{−1/2} ≈ 0,61 ≠ 0 » : la valeur approchée dans la formule (question 15)."""
        pas_impaire = dict(resume(cartes_parite("e^(x-1/2)")))["Pas impaire"]
        self.assertEqual(pas_impaire[0], r"\(f(0) = e^{-\frac{1}{2}} \approx 0{,}61 \neq 0\)")

    def test_resoudre_place_la_parite_sous_son_intertitre(self):
        for entree in ("e^(-x^2)", "e^((x^2+x-2)/(6x-12))", "(x^2-6)e^(-2x)"):
            with self.subTest(entree=entree):
                cartes = rec.resoudre(entree)["cartes"]
                i, j = [c["titre"] for c in cartes].index(rec.PARTIES[1]), [c["titre"] for c in cartes].index(rec.PARTIES[2])
                self.assertEqual(cartes[i + 1:j], cartes_parite(entree))

    def test_analyse_en_cache(self):
        """D19 : la parité relit l'analyse d'etudier() ; resoudre() ne relance pas analyser_complet."""
        import noyau
        original, appels = noyau.analyser_complet, []

        def espion(*args, **kwargs):
            appels.append(args)
            return original(*args, **kwargs)
        ec.vider_cache()
        with ExitStack() as pile:
            for module in list(sys.modules.values()):
                if getattr(module, "analyser_complet", None) is original:
                    pile.enter_context(mock.patch.object(module, "analyser_complet", espion))
            self.assertTrue(rec.resoudre("e^(2/(x^2-4))")["ok"])
        self.assertEqual(len(appels), 1)


# ---------- oracle : chaque conclusion et chaque valeur affichée ----------
def lire_rationnel(t):
    m = re.fullmatch(r"(-?)\\frac\{(\d+)\}\{(\d+)\}", t)
    if m:
        return F(int(m.group(2)), int(m.group(3))) * (-1 if m.group(1) else 1)
    return F(int(t))


def arrondi_oracle(v):
    """Arrondi de decisions.md §2, calculé ici (mpmath 50 chiffres, Decimal) : 2 décimales, ou 2 chiffres significatifs sous 0,01."""
    d = Decimal(mp.nstr(v, 45, min_fixed=-mp.inf, max_fixed=mp.inf))
    if d == 0:
        return d
    q = Decimal("0.01") if abs(d) >= Decimal("0.01") else Decimal(1).scaleb(d.adjusted() - 1)
    return d.quantize(q, rounding=ROUND_HALF_UP)


def decimal_affiche(t):
    """« −0,68 », « -0{,}68 » ou « 1\\text{’}234{,}57 » (TeX, séparateur des milliers ’) → Decimal."""
    return Decimal(t.replace(r"\text{’}", "").replace("{,}", ".").replace("−", "-").replace(",", "."))


class TestPariteOracle(unittest.TestCase):
    GRILLE = [mp.mpf(k) / 13 for k in range(1, 80)]

    def verifier(self, entree):
        """La conclusion de la partie 2 recoupée par l'oracle mpmath (tests/python/oracle.py : ni `evaluer`, ni SymPy, ni la sonde)."""
        f = lire(entree)
        cartes = resume(cartes_parite(entree))
        tout = "\n".join(h for _, hs in cartes for h in hs)
        conclusions = [c for c in (parties.PAIRE, parties.IMPAIRE, parties.NI) if c in tout]
        if not conclusions:
            self.assertTrue(any(m in tout for m in MESSAGES), tout)
            return None
        self.assertEqual(len(conclusions), 1, tout)
        self.assertFalse(any(m in tout for m in MESSAGES), tout)
        if conclusions[0] in (parties.PAIRE, parties.IMPAIRE):
            s = 1 if conclusions[0] == parties.PAIRE else -1
            vus = 0
            for x in self.GRILLE:
                u, v = oracle.valeur(f, x), oracle.valeur(f, -x)
                self.assertEqual(u is None, v is None, (entree, x))
                if u is not None:
                    vus += 1
                    self.assertLess(abs(v - s * u), mp.mpf(10) ** -35 * (1 + abs(u)), (entree, x))
            self.assertGreater(vus, 10, entree)
            return conclusions[0]
        lignes = dict(cartes)
        if "Symétrie de l'ED" in lignes and lignes["Symétrie de l'ED"][0] != parties.SYMETRIQUE:
            m = re.fullmatch(r"\\\((.*) \\in ED\\\), mais \\\((.*) \\notin ED\\\) : ED n'est pas symétrique par rapport à 0\.",
                             lignes["Symétrie de l'ED"][0])
            a, b = lire_rationnel(m.group(1)), lire_rationnel(m.group(2))
            self.assertEqual(b, -a)
            self.assertIsNotNone(oracle.valeur(f, mp.mpf(a.numerator) / a.denominator), entree)
            self.assertIsNone(oracle.valeur(f, mp.mpf(b.numerator) / b.denominator), entree)
            return parties.NI
        valeurs = {}
        for titre in ("Pas impaire", "Pas paire"):
            for h in lignes[titre]:
                m = re.match(r"\\\(f\((.*?)\) = (.*?)(?: \\approx (-?[0-9]+(?:\{,\}[0-9]+)?))?( \\neq 0)?\\\)", h)
                if not m:
                    continue
                a = lire_rationnel(m.group(1))
                v = oracle.valeur(f, mp.mpf(a.numerator) / a.denominator)
                self.assertIsNotNone(v, (entree, a))
                if m.group(3):                                            # valeur approchée (dans la formule) : l'arrondi de l'oracle
                    self.assertEqual(decimal_affiche(m.group(3)), arrondi_oracle(v), (entree, h))
                    affiche = decimal_affiche(m.group(3))
                else:                                                     # entier exact
                    self.assertTrue(re.fullmatch(r"-?\d+", m.group(2)), h)
                    self.assertLess(abs(v - int(m.group(2))), mp.mpf(10) ** -40, (entree, h))
                    affiche = Decimal(int(m.group(2)))
                if m.group(4):
                    self.assertNotEqual(affiche, 0, (entree, h))
                valeurs[(titre, a)] = affiche
        pi = {a: v for (t, a), v in valeurs.items() if t == "Pas impaire"}
        if 0 not in pi:                                                   # contre-exemple f(−a) ≠ −f(a)
            (a,) = [a for a in pi if a > 0]
            self.assertNotEqual(pi[-a], -pi[a], entree)
        pp = {a: v for (t, a), v in valeurs.items() if t == "Pas paire"}
        (a,) = [a for a in pp if a > 0]
        self.assertNotEqual(pp[-a], pp[a], entree)
        return parties.NI

    def test_entrees_de_la_page(self):
        vues = set()
        for entree in dict.fromkeys(entrees_page("etude-complete") + CAS_LIMITES["etude-complete"] + list(TestParite.CARTES)):
            if not ec.etudier(entree)["ok"]:
                continue
            with self.subTest(entree=entree):
                vues.add(self.verifier(entree))
        self.assertEqual(vues, {parties.PAIRE, parties.IMPAIRE, parties.NI, None})

    def test_famille_au_hasard(self):
        """Polynômes (puissances paires, impaires ou mêlées), exponentielles d'un polynôme, quotients par x² + c : la conclusion et
        les valeurs affichées sont celles de l'oracle."""
        hasard = random.Random(4)
        vues = {}

        def poly(degres):
            termes = [f"{hasard.choice([1, 2, 3, 5])}x^{k}" for k in degres]
            return "+".join(termes).replace("+-", "-")
        for _ in range(60):
            genre = hasard.choice(["pair", "impair", "mêlé"])
            degres = {"pair": [2, 4], "impair": [1, 3, 5], "mêlé": [0, 1, 2, 3]}[genre]
            p = poly(sorted(hasard.sample(degres, hasard.randint(1, min(3, len(degres))))))
            if hasard.random() < 0.5:
                p = p.replace("+", "-", hasard.randint(0, 1))
            forme = hasard.choice(["{p}", "e^(-({p})/10)", "({p})/(x^2+{c})", "x*e^(-x^2)+{p}"])
            entree = forme.format(p=p, c=hasard.randint(1, 4))
            r, _, _ = ec.analyse(entree)
            if not (r.get("ok") and r.get("complet")):
                continue
            with self.subTest(entree=entree):
                conclusion = self.verifier(entree)
                vues[conclusion] = vues.get(conclusion, 0) + 1
        self.assertGreaterEqual(min(vues.get(c, 0) for c in (parties.PAIRE, parties.IMPAIRE, parties.NI)), 5, vues)


# ---------- garde-fous forcés (principe 0.2) ----------
class TestGardeFousParite(unittest.TestCase):
    def doute(self, entree):
        self.assertEqual(resume(cartes_parite(entree)), message(parties.DOUTE))

    def test_sonde_et_sympy_en_desaccord(self):
        """La sonde annonce une parité que SymPy ne confirme pas : aucune conclusion."""
        with mock.patch.object(parties, "classer_par_la_sonde", lambda f, m: "impaire"):
            self.doute("e^(-x^2)")
        with mock.patch.object(parties, "classer_par_la_sonde", lambda f, m: "paire"):
            self.doute("(x^2-6)e^(-2x)")
            self.doute("x^3-3x")

    def test_sympy_contredit_la_sonde(self):
        """SymPy calcule une autre fonction (f + x) : la sonde dit paire, SymPy ne trouve pas 0 ; aucune conclusion."""
        vrai = parties.en_sympy_reel
        with mock.patch.object(parties, "en_sympy_reel", lambda T: vrai(T) + parties.SYMPY["x"]):
            self.doute("e^(-x^2)")
            self.doute("x^3-3x")

    def test_sonde_dans_la_zone_grise(self):
        """f(−x) et f(x) diffèrent de 10⁻¹² en relatif : ni égaux ni clairement différents, aucune conclusion."""
        vrai = parties.valeur_mp

        def sonde(n, x):
            v = vrai(n, x)
            return v if (v is None or x > 0) else v * (1 + mp.mpf("1e-12"))
        with mock.patch.object(parties, "valeur_mp", sonde):
            self.doute("e^(-x^2)")
            self.doute("x^4-2x^2")

    def test_sonde_contredit_l_ed(self):
        """Ex7 : la sonde trouve f définie en 2 (−a) : l'ED non symétrique n'est pas confirmé ; aucune conclusion."""
        with mock.patch.object(parties, "valeur_mp", lambda n, x: mp.mpf(1)):
            self.doute("e^((x^2+x-2)/(6x-12))")

    def test_ligne_de_la_chaine_fausse(self):
        """Une ligne de la chaîne qui ne vaut pas f(−x) : aucune conclusion."""
        with mock.patch.object(parties, "chaine_f_moins_x", lambda f, p: [("faux", lire("x^2")), (r"\( = f(x)\)", None)]):
            self.doute("e^(-x^2)")

    def test_valeur_ecrite_fausse(self):
        """Une valeur exacte écrite qui ne vaut pas f(a) (SymPy et la sonde la refusent) : pas de contre-exemple, message clair."""
        with mock.patch.object(parties, "plier", lambda n: Nb(7)):
            self.assertEqual(resume(cartes_parite("(x^2-6)e^(-2x)")), [SYM] + message(parties.SANS_CONTRE_EXEMPLE))

    def test_valeur_sonde_en_desaccord(self):
        """La sonde donne une autre valeur de f(1) que SymPy : a = 1 est écarté, le contre-exemple suivant (a = 2) est pris."""
        vrai = parties.valeur_mp

        def sonde(n, x):
            v = vrai(n, x)
            return v + 1 if (v is not None and x == 1) else v
        with mock.patch.object(parties, "valeur_mp", sonde):
            pas_paire = dict(resume(cartes_parite("(x^2-6)e^(-2x)")))["Pas paire"]
        self.assertTrue(pas_paire[0].startswith(r"\(f(2) = "), pas_paire)

    def test_sans_sympy(self):
        with mock.patch.object(parties, "charger_sympy", lambda: None):
            self.doute("e^(-x^2)")
            self.doute("e^((x^2+x-2)/(6x-12))")

    def test_borne_approchee(self):
        """Une borne de l'ED connue seulement en valeur approchée : symétrie et appartenance indécidables (Doute)."""
        sp = parties.charger_sympy()
        approchee = Num.approche(1.234)
        ivs = [Iv(None, False, Num(-1.234, "-1{,}234", approx=True), False), Iv(approchee, False, None, False)]
        with self.assertRaises(parties.Doute):
            parties.ed_symetrique(ivs, sp)
        with self.assertRaises(parties.Doute):
            parties.dans_ed(ivs, F(2), sp)
        with mock.patch.object(parties, "fusion", lambda ED: ivs):
            self.doute("e^(-x^2)")

    def test_arrondis(self):
        self.assertEqual(parties.arrondi(Decimal("-36.94528")), Decimal("-36.95"))
        self.assertEqual(parties.arrondi(Decimal("0.0074363")), Decimal("0.0074"))
        self.assertEqual(parties.arrondi(Decimal("0.125")), Decimal("0.13"))
        self.assertIsNone(parties.arrondi(Decimal("0.00045")))
        self.assertIsNone(parties.arrondi(Decimal("1234.5")))                          # partie 2 : [10⁻³ ; 1000[ (question 19)
        self.assertEqual(parties.arrondi(Decimal("1234.567"), plafond=10 ** 6), Decimal("1234.57"))
        self.assertIsNone(parties.arrondi(Decimal("1234567"), plafond=10 ** 6))
        self.assertEqual(parties.decimal_tex(Decimal("-0.68")), "-0{,}68")
        self.assertEqual(parties.decimal_tex(-Decimal(0)), "0")
        self.assertEqual(parties.decimal_tex(Decimal("-1234.57")), r"-1\text{’}234{,}57")      # séparateur des milliers (question 28)
        self.assertEqual(parties.decimal_tex(Decimal("999999.99")), r"999\text{’}999{,}99")

    def test_parite_lue_et_plier(self):
        for entree, p in (("e^(-x^2)", 1), ("x^3-3x", -1), ("x/(x^2+1)", -1), ("x^(2/3)", 1), ("x^(1/3)", None), ("e^x+e^(-x)", None),
                          ("x^3+1", None), ("2^x", None), ("(x^3-x)^2", None), ("sqrt(x^2-4)", 1), ("ln(x^2+1)/x", -1)):
            with self.subTest(entree=entree):
                self.assertEqual(parties.parite_lue(lire(entree)), p)
        for entree, a, ecrit in (("(x^2-6)e^(-2x)", 1, "-5e^{-2}"), ("e^x(6-e^x)", 0, "5"), ("e^(1/x)", 1, "e"), ("x^2*e^(-x)", -1, "e"),
                                 ("ln(x)+x", 1, "1")):
            with self.subTest(entree=entree, a=a):
                self.assertEqual(parties.tex(parties.plier(parties.substituer(lire(entree), parties.nombre(a)))), ecrit)


# ---------------------------------------------------------------------------------------------------------------------------
# Partie 3. Zéros, signe, ordonnée à l'origine (D5)
# ---------------------------------------------------------------------------------------------------------------------------
def cartes_zeros(entree):
    return parties.cartes_zeros_signe(ec.analyse(entree))


def resume_zeros(cartes):
    """Titres et lignes ; un tableau devient ('TABLEAU', crit, [(étiquette, cases accolées, « [||] » pour une case de 2 signes)])."""
    out = []
    for c in cartes:
        blocs = []
        for b in c["blocs"]:
            if b["type"] == "tableau":
                blocs.append(("TABLEAU", b["crit"], [(r["label"], "".join(x if len(x) == 1 else "[" + x + "]" for x in r["cells"]))
                                                    for r in b["rows"]]))
            else:
                blocs.append(b["html"])
        out.append((c["titre"], blocs))
    return out


POSITIVE = "(une exponentielle est strictement positive)"
MESSAGES_ZEROS = (parties.DOUTE_SIGNE, parties.ZEROS_NON_EXACTS, parties.ZEROS_NON_TRAITES)


def ordonnee(*lignes):
    return ("Ordonnée à l'origine", list(lignes))


COUPE_PAS = ordonnee(parties.NE_COUPE_PAS)


class TestZerosSigne(unittest.TestCase):
    CARTES = {
        "e^((x^2+x-2)/(6x-12))": [
            ("Zéros et signe de f", [rf"\(e^{{g(x)}} > 0\) pour tout \(x \in ED\) {POSITIVE}.", r"Donc f n'a pas de zéro et \(f(x) > 0\) sur ED."]),
            ordonnee(r"\(g(0) = \frac{-2}{-12} = \frac{1}{6}\), donc \(f(0) = e^{\frac{1}{6}} \approx 1{,}18\).",
                     r"Le graphe coupe l'axe des y au point \((0\,;\,e^{\frac{1}{6}})\).")],
        "e^(-x^2)": [
            ("Zéros et signe de f", [rf"\(e^{{-x^{{2}}}} > 0\) pour tout \(x\) {POSITIVE}.", r"Donc f n'a pas de zéro et \(f(x) > 0\) sur ED."]),
            ordonnee(r"\(f(0) = 1\).", r"Le graphe coupe l'axe des y au point \((0\,;\,1)\).")],
        "(x^2-6)e^(-2x)": [
            ("Zéros de f", [rf"\(e^{{-2x}} > 0\) pour tout \(x\) {POSITIVE} ; il ne s'annule jamais.",
                            r"\(\left(x^{2} - 6\right)\,e^{-2x} = 0\)", r"\(\iff x^{2} - 6 = 0\) (car \(e^{-2x} > 0\))", r"\(\iff x^{2} = 6\)",
                            r"\(\iff\) \(x = -\sqrt{6} \approx -2{,}45\) ou \(x = \sqrt{6} \approx 2{,}45\)"]),
            ("Signe de f", [("TABLEAU", [r"-\sqrt{6}", r"\sqrt{6}"], [(r"\left(x^{2} - 6\right)", "+0-0+"), ("e^{-2x}", "+++++"),
                                                                       ("f(x)", "+0-0+")])]),
            ordonnee(r"\(f(0) = -6\).", r"Le graphe coupe l'axe des y au point \((0\,;\,-6)\).")],
        "e^x(6-e^x)": [
            ("Zéros de f", [rf"\(e^{{x}} > 0\) pour tout \(x\) {POSITIVE} ; il ne s'annule jamais.", r"\(e^{x}\,\left(6 - e^{x}\right) = 0\)",
                            r"\(\iff 6 - e^{x} = 0\) (car \(e^{x} > 0\))",
                            r"\(\iff e^{x} = 6\) (on isole \(e^{x}\) du côté où son coefficient est positif)", r"\(\iff\) \(x = \ln(6) \approx 1{,}79\)"]),
            ("Signe de f", [("TABLEAU", [r"\ln(6)"], [("e^{x}", "+++"), (r"\left(6 - e^{x}\right)", "+0-"), ("f(x)", "+0-")])]),
            ordonnee(r"\(f(0) = 5\).", r"Le graphe coupe l'axe des y au point \((0\,;\,5)\).")],
        "e^(2/(x^2-4))": [
            ("Zéros et signe de f", [rf"\(e^{{\frac{{2}}{{x^{{2}} - 4}}}} > 0\) pour tout \(x \in ED\) {POSITIVE}.",
                                     r"Donc f n'a pas de zéro et \(f(x) > 0\) sur ED."]),
            ordonnee(r"\(f(0) = e^{-\frac{1}{2}} \approx 0{,}61\).", r"Le graphe coupe l'axe des y au point \((0\,;\,e^{-\frac{1}{2}})\).")],
        "x*ln(x)": [
            ("Zéros de f", [r"\(x\,\ln(x) = 0\)", r"\(\iff x = 0 \text{ ou } \ln(x) = 0\) (produit nul)", r"\(\iff\) \(x = 0\) ou \(x = 1\)",
                            r"\(x = 0\) est rejeté, car \(0 \notin ED\)."]),
            ("Signe de f", [("TABLEAU", ["0", "1"], [("x", "x[||]+++"), (r"\ln(x)", "x[||]-0+"), ("f(x)", "x[||]-0+")])]), COUPE_PAS],
        "x/sqrt(x^2)": [
            ("Zéros de f", [r"\(\frac{x}{\sqrt{x^{2}}} = 0\)", r"\(\iff\) \(x = 0\) (numérateur nul)",
                            r"\(x = 0\) est rejeté, car \(0 \notin ED\).", parties.PAS_DE_ZERO]),
            ("Signe de f", [("TABLEAU", ["0"], [("x", "-[||]+"), (r"\sqrt{x^{2}}", "+[||]+"), ("f(x)", "-[||]+")])]), COUPE_PAS],
        "(e^x-1)/x": [
            ("Zéros et signe de f", [r"\(\frac{e^{x} - 1}{x} = 0\)", r"\(\iff e^{x} - 1 = 0\) (numérateur nul)", r"\(\iff e^{x} = 1\) (on ajoute 1)",
                                     r"\(\iff\) \(x = 0\)", r"\(x = 0\) est rejeté, car \(0 \notin ED\).",
                                     r"Donc f n'a pas de zéro et \(f(x) > 0\) sur ED."]), COUPE_PAS],
        # Somme-Produit puis x = 1 ou x = 3 directement (question 11) ; une ligne du tableau par facteur écrit (question 23)
        "x^2-4x+3": [
            ("Zéros de f", [r"\(x^{2} - 4x + 3 = 0\)", r"\(\iff (x - 1)(x - 3) = 0\) (Somme-Produit)",
                            r"\(\iff\) \(x = 1\) ou \(x = 3\) (produit nul)"]),
            ("Signe de f", [("TABLEAU", ["1", "3"], [(r"\left(x - 1\right)", "-0+++"), (r"\left(x - 3\right)", "---0+"),
                                                     ("f(x)", "+0-0+")])]),
            ordonnee(r"\(f(0) = 3\).", r"Le graphe coupe l'axe des y au point \((0\,;\,3)\).")],
        "x^4-2x^2": [
            ("Zéros de f", [r"\(x^{4} - 2x^{2} = 0\)", r"\(\iff x^{2}(x^{2} - 2) = 0\) (mise en évidence)",
                            r"\(\iff x = 0 \text{ ou } x^{2} - 2 = 0\) (produit nul)", r"\(\iff x = 0 \text{ ou } x^{2} = 2\)",
                            r"\(\iff\) \(x = -\sqrt{2} \approx -1{,}41\) ou \(x = 0\) ou \(x = \sqrt{2} \approx 1{,}41\)"]),
            ("Signe de f", [("TABLEAU", [r"-\sqrt{2}", "0", r"\sqrt{2}"], [("x^{2}", "+++0+++"), (r"\left(x^{2} - 2\right)", "+0---0+"),
                                                                           ("f(x)", "+0-0-0+")])]),
            ordonnee(r"\(f(0) = 0\).", r"Le graphe coupe l'axe des y au point \((0\,;\,0)\).")],
        "1/x": [
            ("Zéros de f", [parties.NUMERATEUR_CONSTANT]), ("Signe de f", [("TABLEAU", ["0"], [("x", "-[||]+"), ("f(x)", "-[||]+")])]),
            COUPE_PAS],
        "e^x/x": [
            ("Zéros de f", [rf"\(e^{{x}} > 0\) pour tout \(x \in ED\) {POSITIVE} ; il ne s'annule jamais.", parties.PAS_DE_ZERO]),
            ("Signe de f", [("TABLEAU", ["0"], [("e^{x}", "+[||]+"), ("x", "-[||]+"), ("f(x)", "-[||]+")])]), COUPE_PAS],
        "-e^x": [
            ("Zéros et signe de f", [rf"\(e^{{x}} > 0\) pour tout \(x\) {POSITIVE} ; il ne s'annule jamais.",
                                     r"Donc f n'a pas de zéro et \(f(x) < 0\) sur ED."]),
            ordonnee(r"\(f(0) = -1\).", r"Le graphe coupe l'axe des y au point \((0\,;\,-1)\).")],
        "sqrt(x^2-4)": [
            ("Zéros de f", [r"\(\sqrt{x^{2} - 4} = 0 \iff x^{2} - 4 = 0\)", r"On résout \(x^{2} - 4 = 0\).",
                            r"\(x^{2} - 4 = (x - 2)(x + 2)\) : zéros \(-2\) et \(2\).", r"Solutions : \(x = -2\), \(x = 2\).",
                            r"Donc \(x = -2\) ou \(x = 2\)."]),
            ("Signe de f", [("TABLEAU", ["-2", "2"], [(r"\sqrt{x^{2} - 4}", "+0x0+"), ("f(x)", "+0x0+")])]), COUPE_PAS],
        "x^3+x+1": [("Zéros et signe de f", [parties.ZEROS_NON_EXACTS]), ordonnee(r"\(f(0) = 1\).",
                                                                              r"Le graphe coupe l'axe des y au point \((0\,;\,1)\).")],
        "x^3-3x^2+2x": [
            ("Zéros de f", [r"\(x^{3} - 3x^{2} + 2x = 0\)", r"\(\iff x(x^{2} - 3x + 2) = 0\) (mise en évidence)",
                            r"\(\iff x(x - 1)(x - 2) = 0\) (Somme-Produit)", r"\(\iff\) \(x = 0\) ou \(x = 1\) ou \(x = 2\) (produit nul)"]),
            ("Signe de f", [("TABLEAU", ["0", "1", "2"], [("x", "-0+++++"), (r"\left(x - 1\right)", "---0+++"),
                                                          (r"\left(x - 2\right)", "-----0+"), ("f(x)", "-0+0-0+")])]),
            ordonnee(r"\(f(0) = 0\).", r"Le graphe coupe l'axe des y au point \((0\,;\,0)\).")],
        "2x^2-6x+4": [
            ("Zéros de f", [r"\(2x^{2} - 6x + 4 = 0\)", r"\(\iff 2(x^{2} - 3x + 2) = 0\) (mise en évidence)",
                            r"\(\iff 2(x - 1)(x - 2) = 0\) (Somme-Produit)", r"\(\iff\) \(x = 1\) ou \(x = 2\) (produit nul)"]),
            ("Signe de f", [("TABLEAU", ["1", "2"], [("2", "+++++"), (r"\left(x - 1\right)", "-0+++"), (r"\left(x - 2\right)", "---0+"),
                                                     ("f(x)", "+0-0+")])]),
            ordonnee(r"\(f(0) = 4\).", r"Le graphe coupe l'axe des y au point \((0\,;\,4)\).")],
        # facteurs x − r saisis : x = r directement, « produit nul » (comme la ligne des zéros de f′)
        "(x-1)(x+2)e^x": [
            ("Zéros de f", [rf"\(e^{{x}} > 0\) pour tout \(x\) {POSITIVE} ; il ne s'annule jamais.",
                            r"\(\left(x - 1\right)\,\left(x + 2\right)\,e^{x} = 0\)",
                            r"\(\iff \left(x - 1\right)\,\left(x + 2\right) = 0\) (car \(e^{x} > 0\))",
                            r"\(\iff\) \(x = -2\) ou \(x = 1\) (produit nul)"]),
            ("Signe de f", [("TABLEAU", ["-2", "1"], [(r"\left(x - 1\right)", "---0+"), (r"\left(x + 2\right)", "-0+++"), ("e^{x}", "+++++"),
                                                      ("f(x)", "+0-0+")])]),
            ordonnee(r"\(f(0) = -2\).", r"Le graphe coupe l'axe des y au point \((0\,;\,-2)\).")],
        "x^(2/3)": [
            ("Zéros de f", [r"\(\sqrt[3]{x^{2}} = 0\)", r"\(\iff \left(\sqrt[3]{x}\right)^{2} = 0\)", r"\(\iff \sqrt[3]{x} = 0\)",
                            r"\(\iff\) \(x = 0\)"]),
            ("Signe de f", [("TABLEAU", ["0"], [(r"\left(\sqrt[3]{x}\right)^{2}", "+0+"), ("f(x)", "+0+")])]),
            ordonnee(r"\(f(0) = 0\).", r"Le graphe coupe l'axe des y au point \((0\,;\,0)\).")],
    }

    def test_cartes_exactes(self):
        """D5 : corrigé (decisions.md §4–5 : Ex7, a–d) et autres formes : exponentielle seule ou en facteur, chaîne avec la propriété
        nommée, Somme-Produit, mise en évidence, zéro rejeté, lignes de l'outil ED, zéros non exacts, numérateur constant, f(0)."""
        for entree, attendu in self.CARTES.items():
            with self.subTest(entree=entree):
                self.assertEqual(resume_zeros(cartes_zeros(entree)), attendu)

    def test_tableau_par_la_machinerie_du_tableau_de_f_prime(self):
        """Le tableau de f est celui de `derivee_variations.tableau_signes` (R7), la ligne f(x) en dernier (« final »)."""
        import derivee_variations as dv
        from noyau import aplatir, fusion
        _, f, ED = ec.analyse("(x^2-6)e^(-2x)")
        c, facs = aplatir(f)
        Z = parties.points([z for h, _ in facs if not parties.est_exponentielle(h) for z in parties.zeros_facteur(h)[0]])
        crit, lignes, _ = dv.tableau_signes(f, Z, fusion(ED), ED, "f(x)", c, facs)
        tableau = dict(cartes_zeros("(x^2-6)e^(-2x)")[1]["blocs"][0])
        self.assertEqual(tableau, {"type": "tableau", "var": "x", "crit": [p.tex for p in crit], "rows": lignes})
        self.assertTrue(lignes[-1]["final"])

    def test_chaines(self):
        self.assertEqual(parties.etapes_polynome([F(-3), F(2)]), [(["2x - 3 = 0"], None), (["2x = 3"], None), ([r"x = \frac{3}{2}"], None)])
        self.assertEqual(parties.etapes_polynome([F(0), F(-3), F(0), F(1)]), [
            (["x^{3} - 3x = 0"], None), (["x(x^{2} - 3) = 0"], "mise en évidence"), (["x = 0", "x^{2} - 3 = 0"], "produit nul"),
            (["x = 0", "x^{2} = 3"], None), (["x = 0", r"x = -\sqrt{3}", r"x = \sqrt{3}"], None)])
        self.assertEqual(parties.etapes_polynome([F(3), F(-4), F(1)]), [                                     # question 11
            (["x^{2} - 4x + 3 = 0"], None), (["(x - 1)(x - 3) = 0"], "Somme-Produit"), (["x = 1", "x = 3"], "produit nul")])
        self.assertIsNone(parties.etapes_polynome([F(1), F(1), F(1)]))           # x² + x + 1 : rédaction de l'outil ED
        h = lire("ln(x)+1")
        self.assertEqual(parties.etapes_facteur(h, parties.zeros_facteur(h)[1]), [
            ([r"\ln(x) + 1 = 0"], None), ([r"\ln(x) = -1"], "on soustrait 1"), (["x = e^{-1}"], None)])

    def test_valeurs_approchees(self):
        """decisions.md §2 entre 10⁻³ et 10⁶, séparateur des milliers ’ dès 1000 (question 28), entier exact tel quel (question 2),
        R13 sous 10⁻³ et dès 10⁶ (question 1) ; en TeX, pour la formule (question 15)."""
        sp = parties.charger_sympy()
        for v, attendu in ((sp.sqrt(6), "2{,}45"), (-sp.sqrt(6), "-2{,}45"), (3 * sp.exp(-6), "0{,}0074"), (sp.Integer(9), None),
                           (sp.Integer(-6), None), (sp.Rational(1, 3), "0{,}33"), (sp.Rational(1, 8), "0{,}13"),
                           (sp.exp(-10), r"4{,}540 \times 10^{-5}"), (sp.Rational(10 ** 10, 3), r"3{,}333 \times 10^{9}"),
                           (sp.Rational(10 ** 6 - 1, 10 ** 6 * 10 ** 4), r"1 \times 10^{-4}"),
                           (sp.exp(8), r"2\text{’}980{,}96"), (-sp.Rational(1234567, 1000), r"-1\text{’}234{,}57"),
                           (sp.exp(14), r"1{,}203 \times 10^{6}")):
            with self.subTest(v=v):
                self.assertEqual(parties.approchee(v, sp), attendu)

    def test_resoudre_place_la_partie_3_sous_son_intertitre(self):
        for entree in ("e^(-x^2)", "e^((x^2+x-2)/(6x-12))", "(x^2-6)e^(-2x)", "ln(x)/x"):
            with self.subTest(entree=entree):
                cartes = rec.resoudre(entree)["cartes"]
                t = [c["titre"] for c in cartes]
                self.assertEqual(cartes[t.index(rec.PARTIES[2]) + 1:t.index(rec.PARTIES[3])], cartes_zeros(entree))


class TestLignesDuTableau(unittest.TestCase):
    """Question 23 : une ligne du tableau de signes de f par facteur de la factorisation écrite dans la chaîne (mise en évidence,
    Somme-Produit) ; la constante fois le produit des lignes est f (oracle mpmath, 50 chiffres) ; garde-fous forcés (ligne fausse :
    SymPy la refuse ; SymPy aveuglé : la sonde la refuse) : les lignes d'avant."""
    ENTREES = ("x^2-4x+3", "x^3-3x", "x^4-2x^2", "2x^2-6x+4", "x^3-3x^2+2x", "(x^2-3x+2)/(x-5)", "(x^2+x-6)e^(-x)", "(x^2-5x+6)^2")

    def lignes(self, entree):
        from noyau import aplatir
        _, f, _ = ec.analyse(entree)
        c, facs = aplatir(f)
        with mpmath.workdps(parties.CHIFFRES):
            return f, c, facs, parties.lignes_du_tableau(f, c, facs, parties.charger_sympy(), mpmath)

    def test_produit_des_lignes_egal_a_f(self):
        for entree in self.ENTREES:
            with self.subTest(entree=entree):
                f, c, facs, (cn, nouvelles) = self.lignes(entree)
                self.assertNotEqual([h.key() for h, _ in nouvelles], [h.key() for h, _ in facs])
                vus = 0
                for k in range(-40, 41):
                    x = mp.mpf(k) / 7 + mp.mpf(1) / 1000
                    v = oracle.valeur(f, x)
                    if v is None:
                        continue
                    produit = mp.mpf(cn.numerator) / cn.denominator
                    for h, e in nouvelles:
                        produit *= oracle.valeur(h, x) ** e
                    self.assertTrue(mp.almosteq(produit, v, rel_eps=mp.mpf(10) ** -40, abs_eps=mp.mpf(10) ** -40), (entree, x))
                    vus += 1
                self.assertGreater(vus, 50)

    def test_lignes_du_tableau_dans_la_carte(self):
        """Les étiquettes des lignes sont les facteurs écrits dans la chaîne, dans l'ordre, puis f(x)."""
        attendu = {"(x^2-3x+2)/(x-5)": [r"\left(x - 1\right)", r"\left(x - 2\right)", r"\left(x - 5\right)", "f(x)"],
                   "(x^2+x-6)e^(-x)": [r"\left(x + 3\right)", r"\left(x - 2\right)", "e^{-x}", "f(x)"],
                   "(x^2-5x+6)^2": [r"\left(x - 2\right)^{2}", r"\left(x - 3\right)^{2}", "f(x)"]}
        for entree, etiquettes in attendu.items():
            with self.subTest(entree=entree):
                (tableau,) = [b for c in cartes_zeros(entree) for b in c["blocs"] if b["type"] == "tableau"]
                self.assertEqual([r["label"] for r in tableau["rows"]], etiquettes)

    def test_ligne_fausse_refusee(self):
        with mock.patch.object(parties, "arbre_polynome", lambda P: lire("x-7")):
            for entree in ("x^2-4x+3", "x^3-3x"):
                with self.subTest(entree=entree):
                    f, c, facs, resultat = self.lignes(entree)
                    self.assertEqual(resultat, (c, facs))
            (tableau,) = [b for c in cartes_zeros("x^2-4x+3") for b in c["blocs"] if b["type"] == "tableau"]
            self.assertEqual([r["label"] for r in tableau["rows"]], [r"\left(x^{2} - 4x + 3\right)", "f(x)"])

    def test_sympy_aveugle_la_sonde_refuse(self):
        sp = parties.charger_sympy()
        with mock.patch.object(parties, "arbre_polynome", lambda P: lire("x-7")), \
                mock.patch.object(parties, "en_sympy_reel", lambda T: sp.Integer(0)):
            f, c, facs, resultat = self.lignes("x^2-4x+3")
        self.assertEqual(resultat, (c, facs))

    def test_sans_chaine_ecrite_lignes_d_avant(self):
        """Lignes de l'outil ED (chaîne non écrite) : le tableau garde les facteurs saisis."""
        with mock.patch.object(parties, "etapes_facteur", lambda h, items: [([parties.tex(h) + " = 0"], None), (["x = 7"], None)]):
            (tableau,) = [b for c in cartes_zeros("x^2-4x+3") for b in c["blocs"] if b["type"] == "tableau"]
        self.assertEqual([r["label"] for r in tableau["rows"]], [r"\left(x^{2} - 4x + 3\right)", "f(x)"])

    def test_arbre_polynome(self):
        for P, ecrit in (([F(-1), F(1)], "x - 1"), ([F(-3), F(0), F(1)], "x^{2} - 3"), ([F(2), F(-3), F(1)], "x^{2} - 3x + 2"),
                         ([F(0), F(1)], "x"), ([F(5), F(2)], "2x + 5")):
            with self.subTest(P=P):
                self.assertEqual(parties.tex(parties.arbre_polynome(P)), ecrit)


# ---------- oracle : zéros, signe et f(0) affichés ----------
def nombre_affiche(t):
    """Valeur mpmath (50 chiffres) d'une écriture LaTeX de l'outil : entiers, fractions, racines, ln, e^{…}. Lecture écrite à la main
    (liste fermée de motifs), ni parseur de l'outil ni SymPy ; ValueError sinon."""
    s = t.replace(r"\left(", "(").replace(r"\right)", ")").replace(r"\,", "").replace(r"\cdot", "*").replace(" ", "")
    for _ in range(8):
        s = re.sub(r"\\d?frac\{([^{}]*)\}\{([^{}]*)\}", r"((\1)/(\2))", s)
        s = re.sub(r"\\sqrt\{([^{}]*)\}", r"sqrt(\1)", s)
        s = re.sub(r"\\sqrt\[(\d+)\]\{([^{}]*)\}", r"root(\2,\1)", s)
        s = re.sub(r"\\ln\(([^()]*)\)", r"log(\1)", s)
        s = re.sub(r"e\^\{([^{}]*)\}", r"exp(\1)", s)
        s = re.sub(r"\^\{([^{}]*)\}", r"**(\1)", s)                        # puissance (après e^{…}) : (−2)^{2}, 3^{2}
    s = re.sub(r"(?<![a-z])e(?![a-z(])", "exp(1)", s)
    if not re.fullmatch(r"(?:[0-9+\-*/().,]|exp|log|sqrt|root)*", s):
        raise ValueError(t)
    s = re.sub(r"(\d|\))(?=[a-z(])", r"\1*", s)
    s = re.sub(r"\d+", lambda m: f"mpf({m.group(0)})", s)                  # entiers en mpf : 1/6 calculé à 50 chiffres
    return eval(s, {"__builtins__": {}}, {"exp": mp.exp, "log": mp.log, "sqrt": mp.sqrt, "root": mp.root, "mpf": mp.mpf})


class TestZerosSigneOracle(unittest.TestCase):
    def verifier(self, entree):
        """Ce que la partie 3 affiche, recoupé par l'oracle mpmath (tests/python/oracle.py : ni `evaluer`, ni SymPy, ni la sonde) :
        chaque zéro annule f (et un zéro rejeté est hors de l'ED), son arrondi est celui de l'oracle ; le signe de chaque case du
        tableau (ou « f(x) > 0 sur ED ») est celui de f sur une grille de 60 points par intervalle, sans autre zéro ; f(0) ou 0 ∉ ED."""
        f = lire(entree)
        cartes = cartes_zeros(entree)
        lignes = [b["html"] for c in cartes for b in c["blocs"] if b["type"] == "texte"]
        tout = "\n".join(lignes)
        tableaux = [b for c in cartes for b in c["blocs"] if b["type"] == "tableau"]
        issue = "message" if any(m in tout for m in MESSAGES_ZEROS) else "tableau" if tableaux else "constant"
        if issue == "message":
            self.assertFalse(tableaux or "n'a pas de zéro" in tout, tout)
        zeros = list(re.finditer(r"\\\(x = (.+?)(?: \\approx (-?[0-9]+(?:\{,\}[0-9]+)?))?\\\)( est rejeté)?", tout))
        rejetes = {m.group(1) for m in zeros if m.group(3)}
        for m in zeros:
            z = nombre_affiche(m.group(1))
            v = oracle.valeur(f, z)
            if m.group(1) in rejetes:                                     # zéro d'un facteur hors de l'ED
                self.assertIsNone(v, (entree, m.group(0)))
            else:
                self.assertIsNotNone(v, (entree, m.group(0)))
                self.assertLess(abs(v), mp.mpf(10) ** -35, (entree, m.group(0)))
            if m.group(2):
                self.assertEqual(decimal_affiche(m.group(2)), arrondi_oracle(z), (entree, m.group(0)))
            else:
                self.assertEqual(z, mp.nint(z), (entree, m.group(0)))
        if issue == "tableau":
            (tab,) = tableaux
            ligne = tab["rows"][-1]
            self.assertEqual(ligne["label"], "f(x)")
            crit = [nombre_affiche(t) for t in tab["crit"]]
            bornes = [None] + crit + [None]
            for i in range(len(crit) + 1):
                a, b = bornes[i], bornes[i + 1]
                lo = a if a is not None else (b if b is not None else mp.mpf(0)) - 30
                hi = b if b is not None else (a if a is not None else mp.mpf(0)) + 30
                case = ligne["cells"][2 * i]
                for j in range(1, 60):
                    v = oracle.valeur(f, lo + (hi - lo) * j / 60)
                    if case == "x":
                        self.assertIsNone(v, (entree, i))
                    else:
                        self.assertIsNotNone(v, (entree, i))
                        self.assertEqual("+" if v > 0 else "-", case, (entree, i, j))
            for c, case in zip(crit, ligne["cells"][1::2]):
                v = oracle.valeur(f, c)
                if case == "0":
                    self.assertLess(abs(v), mp.mpf(10) ** -35, (entree, c))
                elif case in ("||", "x"):
                    self.assertIsNone(v, (entree, c))
                else:
                    self.assertEqual("+" if v > 0 else "-", case, (entree, c))
        if issue == "constant":
            s = 1 if r"\(f(x) > 0\)" in tout else -1
            self.assertIn(r"\(f(x) " + (">" if s > 0 else "<") + r" 0\) sur ED", tout)
            for k in range(-300, 301):
                v = oracle.valeur(f, mp.mpf(k) / 10 + mp.mpf(1) / 7)
                if v is not None:
                    self.assertGreater(s * v, 0, (entree, k))
        ordo = [b["html"] for b in cartes[-1]["blocs"]]
        if ordo == [parties.NE_COUPE_PAS]:
            self.assertIsNone(oracle.valeur(f, 0), entree)
        elif ordo != [parties.DOUTE_F0]:
            m = re.search(r"\\\(f\(0\) = (.+?)(?: \\approx (-?[0-9]+(?:\{,\}[0-9]+)?))?\\\)\.$", ordo[0])
            v0 = oracle.valeur(f, 0)
            self.assertLess(abs(nombre_affiche(m.group(1)) - v0), mp.mpf(10) ** -40, (entree, ordo))
            if m.group(2):
                self.assertEqual(decimal_affiche(m.group(2)), arrondi_oracle(v0), (entree, ordo))
            else:
                self.assertEqual(v0, mp.nint(v0), (entree, ordo))
        return issue

    def test_entrees_de_la_page(self):
        vues = set()
        for entree in dict.fromkeys(entrees_page("etude-complete") + CAS_LIMITES["etude-complete"] + list(TestZerosSigne.CARTES)):
            if not ec.etudier(entree)["ok"]:
                continue
            with self.subTest(entree=entree):
                vues.add(self.verifier(entree))
        self.assertEqual(vues, {"message", "tableau", "constant"})

    def test_famille_au_hasard(self):
        """Polynômes à racines entières (développés), produits par une exponentielle, eˣ(k − eˣ), quotients, x·ln(x) − k·x…"""
        hasard = random.Random(5)
        vues = {}
        formes = ["x^2-{s}x+{p}", "(x^2-{k})e^({c}x)", "e^x({k}-e^x)", "(x-{a})/(x-{b})", "(x^2-{k})/(x-{b})", "x*e^({c}x)",
                  "(x-{a})*ln(x)", "e^(({a})/(x-{b}))", "x^3-{k}x"]
        for _ in range(45):
            a, b = hasard.sample(range(-4, 5), 2)
            valeurs = dict(a=a, b=b, s=a + b, p=a * b, k=hasard.randint(1, 9), c=hasard.choice([-2, -1, 1, 3]))
            entree = hasard.choice(formes).format(**valeurs).replace("--", "+").replace("+-", "-").replace("-+", "-")
            r, _, _ = ec.analyse(entree)
            if not (r.get("ok") and r.get("complet")):
                continue
            with self.subTest(entree=entree):
                issue = self.verifier(entree)
                vues[issue] = vues.get(issue, 0) + 1
        self.assertGreaterEqual(vues.get("tableau", 0), 15, vues)
        self.assertGreaterEqual(vues.get("constant", 0), 3, vues)


# ---------- garde-fous forcés (principe 0.2) ----------
class TestGardeFousZerosSigne(unittest.TestCase):
    def doute(self, entree, positives=()):
        attendu = ("Zéros et signe de f", list(positives) + [parties.DOUTE_SIGNE])
        self.assertEqual(resume_zeros(cartes_zeros(entree))[0], attendu)
        self.assertEqual(len(cartes_zeros(entree)), 2)

    POS_B = rf"\(e^{{-2x}} > 0\) pour tout \(x\) {POSITIVE} ; il ne s'annule jamais."

    def test_sonde_contredit_le_signe(self):
        """La sonde trouve un signe opposé sur ]√6 ; +∞[ : aucune conclusion (ni tableau, ni phrase)."""
        vrai = parties.valeur_mp
        for entree, positives in (("(x^2-6)e^(-2x)", [self.POS_B]),
                                  ("e^(-x^2)", [rf"\(e^{{-x^{{2}}}} > 0\) pour tout \(x\) {POSITIVE} ; il ne s'annule jamais."])):
            haut = parties.tex(lire(entree))

            def sonde(n, x):
                v = vrai(n, x)                                             # la valeur de f seule est faussée (pas ses sous-arbres)
                return -v if (v is not None and x > 3 and parties.tex(n) == haut) else v
            with mock.patch.object(parties, "valeur_mp", sonde), self.subTest(entree=entree):
                self.doute(entree, positives)

    def test_sonde_ne_trouve_pas_le_zero(self):
        vrai = parties.valeur_mp
        with mock.patch.object(parties, "valeur_mp", lambda n, x: (vrai(n, x) or 0) + mp.mpf("1e-15")):
            self.doute("x^2-4x+3")

    def test_tableau_faux(self):
        """Une case de la ligne f(x) fausse (la machinerie du tableau se trompe) : SymPy et la sonde la refusent."""
        import derivee_variations as dv
        vrai = dv.tableau_signes

        def faux(*args):
            crit, lignes, hors = vrai(*args)
            lignes[-1]["cells"][-1] = "-" if lignes[-1]["cells"][-1] == "+" else "+"
            return crit, lignes, hors
        with mock.patch.object(dv, "tableau_signes", faux):
            self.doute("(x^2-6)e^(-2x)", [self.POS_B])
            self.doute("e^(2/(x^2-4))", [rf"\(e^{{\frac{{2}}{{x^{{2}} - 4}}}} > 0\) pour tout \(x \in ED\) {POSITIVE} ; il ne s'annule jamais."])

    def test_sympy_trouve_un_autre_zero(self):
        sp = parties.charger_sympy()
        vrai = sp.solveset
        with mock.patch.object(sp, "solveset", lambda e, x, d: vrai(e, x, d) | sp.FiniteSet(sp.Rational(1, 2))):
            self.doute("(x^2-6)e^(-2x)", [self.POS_B])
            self.doute("x^2-4x+3")

    def test_sympy_ne_conclut_pas(self):
        sp = parties.charger_sympy()
        x = parties.SYMPY["x"]
        with mock.patch.object(sp, "solveset", lambda e, v, d: sp.ConditionSet(x, sp.Eq(e, 0), d)):
            self.doute("x^2-4x+3")

    def test_sympy_contredit_la_sonde(self):
        """SymPy calcule une autre fonction (f + 1) : f(z) ≠ 0 exactement, aucune conclusion."""
        vrai = parties.en_sympy_reel
        with mock.patch.object(parties, "en_sympy_reel", lambda T: vrai(T) + 1):
            self.doute("x^2-4x+3")

    def test_zeros_non_calcules(self):
        def refus(*a, **k):
            raise parties.NonPrisEnCharge("forcé")
        with mock.patch.object(parties, "preimage", refus):
            self.assertEqual(resume_zeros(cartes_zeros("(x^2-6)e^(-2x)"))[0],
                             ("Zéros et signe de f", [self.POS_B, parties.ZEROS_NON_TRAITES]))

    def test_chaine_qui_ne_finit_pas_sur_les_zeros(self):
        """Une chaîne qui ne mène pas aux zéros calculés n'est pas écrite : lignes de l'outil ED, puis « Donc … »."""
        with mock.patch.object(parties, "etapes_facteur", lambda h, items: [([parties.tex(h) + " = 0"], None), (["x = 7"], None)]):
            lignes = resume_zeros(cartes_zeros("x^2-4x+3"))[0][1]
        self.assertEqual(lignes[0], r"On résout \(x^{2} - 4x + 3 = 0\).")
        self.assertEqual(lignes[-1], r"Donc \(x = 1\) ou \(x = 3\).")
        self.assertFalse(any("x = 7" in l for l in lignes))

    def test_ordonnee_en_doute(self):
        with mock.patch.object(parties, "valeur_verifiee", lambda *a: None):
            self.assertEqual(resume_zeros(cartes_zeros("(x^2-6)e^(-2x)"))[-1], ordonnee(parties.DOUTE_F0))
        vrai = parties.valeur_mp
        with mock.patch.object(parties, "valeur_mp", lambda n, x: mp.mpf(1) if x == 0 else vrai(n, x)):
            self.assertEqual(resume_zeros(cartes_zeros("ln(x)/x"))[-1], ordonnee(parties.DOUTE_F0))

    def test_sans_sympy(self):
        with mock.patch.object(parties, "charger_sympy", lambda: None):
            self.assertEqual(resume_zeros(cartes_zeros("e^(-x^2)")),
                             [("Zéros et signe de f", [parties.DOUTE_SIGNE]), ordonnee(parties.DOUTE_F0)])

    def test_borne_approchee(self):
        sp = parties.charger_sympy()
        ivs = [Iv(Num.approche(1.234), False, None, False)]
        with self.assertRaises(parties.Doute):
            parties.appartient(ivs, sp.Integer(2), sp)


if __name__ == "__main__":
    unittest.main()


# ---------------------------------------------------------------------------------------------------------------------------
# Partie 5. Extremums (D11, P7b) ; les valeurs dans la ligne f(x) du tableau (D10) sont testées dans test_tableau_variations.py
# ---------------------------------------------------------------------------------------------------------------------------
def carte_signe_ec(entree):
    return next(c for c in rec.resoudre(entree)["cartes"] if c["titre"] == "Signe de f' et variations")


def lignes_extremums(entree):
    """(lignes de valeur en chaîne, lignes des extremums) de la carte « Signe de f′ et variations » de l'Étude complète."""
    blocs = carte_signe_ec(entree)["blocs"]
    i = next(k for k, b in enumerate(blocs) if b["type"] == "tableau")
    chaine = [b["html"] for b in blocs[i + 1:] if b["type"] == "texte"]
    items = [it for b in blocs[i + 1:] if b["type"] == "liste" for it in b["items"]]
    return chaine, items


def blocs_d11(entree, limites=None):
    r = ec.etudier(entree)
    return parties.blocs_extremums(r["derivee"], r["variations_limites"] if limites is None else limites, ec.analyse(entree))


def items_d11(entree, limites=None):
    return [it for b in blocs_d11(entree, limites) if b["type"] == "liste" for it in b["items"]]


MAX, MIN = "<b>Maximum local</b>", "<b>Minimum local</b>"
MAX_G, MIN_G = "<b>Maximum global</b>", "<b>Minimum global</b>"          # §2 révisé (question 43)
PLUS_MOINS, MOINS_PLUS = r"(\(f'\) passe de \(+\) à \(-\))", r"(\(f'\) passe de \(-\) à \(+\))"


class TestExtremums(unittest.TestCase):
    ATTENDU = {
        "e^((x^2+x-2)/(6x-12))": ([
            r"\(g(0) = \frac{-2}{-12} = \frac{1}{6}\), donc \(f(0) = e^{\frac{1}{6}} \approx 1{,}18\).",
            r"\(g(4) = \frac{18}{12} = \frac{3}{2}\), donc \(f(4) = e^{\frac{3}{2}} \approx 4{,}48\).",
        ], [
            r"<b>Maximum local</b> en \(x = 0\) : \(\left(0\,;\,e^{\frac{1}{6}}\right) \approx \left(0\,;\,1{,}18\right)\) (\(f'\) passe de \(+\) à \(-\)). Pas global : \(f(x) \to +\infty\) quand \(x \to 2^{+}\).",
            r"<b>Minimum local</b> en \(x = 4\) : \(\left(4\,;\,e^{\frac{3}{2}}\right) \approx \left(4\,;\,4{,}48\right)\) (\(f'\) passe de \(-\) à \(+\)). Pas global : \(f(x) \to 0^{+}\) quand \(x \to -\infty\).",
        ]),
        "e^(-x^2)": ([
            r"\(f(0) = e^{-0^{2}} = 1\).",
        ], [
            r"<b>Maximum global</b> en \(x = 0\) : \(\left(0\,;\,1\right)\) (\(f'\) passe de \(+\) à \(-\)). Les autres valeurs de f sont plus petites (limites \(0^{+}\) en \(\pm\infty\)).",
        ]),
        "(x^2-6)e^(-2x)": ([
            r"\(f(-2) = \left(\left(-2\right)^{2} - 6\right)\,e^{-2\left(-2\right)} = \left(4 - 6\right)\,e^{4} = - 2 e^{4} \approx -109{,}20\).",
            r"\(f(3) = \left(3^{2} - 6\right)\,e^{-2 \cdot 3} = \left(9 - 6\right)\,e^{-6} = 3 e^{-6} \approx 0{,}0074\).",
        ], [
            r"<b>Minimum global</b> en \(x = -2\) : \(\left(-2\,;\,- 2 e^{4}\right) \approx \left(-2\,;\,-109{,}20\right)\) (\(f'\) passe de \(-\) à \(+\)). Les autres valeurs de f sont plus grandes (limites \(+\infty\) en \(-\infty\) et \(0^{+}\) en \(+\infty\)).",
            r"<b>Maximum local</b> en \(x = 3\) : \(\left(3\,;\,3 e^{-6}\right) \approx \left(3\,;\,0{,}0074\right)\) (\(f'\) passe de \(+\) à \(-\)). Pas global : \(f(x) \to +\infty\) quand \(x \to -\infty\).",
        ]),
        "e^x(6-e^x)": ([
            r"\(f(\ln(3)) = e^{\ln(3)}\,\left(6 - e^{\ln(3)}\right) = 3\left(6 - 3\right) = 9\).",
        ], [
            r"<b>Maximum global</b> en \(x = \ln(3)\) : \(\left(\ln(3)\,;\,9\right) \approx \left(1{,}10\,;\,9\right)\) (\(f'\) passe de \(+\) à \(-\)). Les autres valeurs de f sont plus petites (limites \(0^{+}\) en \(-\infty\) et \(-\infty\) en \(+\infty\)).",
        ]),
        "e^(2/(x^2-4))": ([
            r"\(g(0) = \frac{2}{-4} = -\frac{1}{2}\), donc \(f(0) = e^{- \frac{1}{2}} \approx 0{,}61\).",
        ], [
            r"<b>Maximum local</b> en \(x = 0\) : \(\left(0\,;\,e^{- \frac{1}{2}}\right) \approx \left(0\,;\,0{,}61\right)\) (\(f'\) passe de \(+\) à \(-\)). Pas global : \(f(x) \to +\infty\) quand \(x \to -2^{-}\).",
        ]),
        # cas limites (D11 : « local » seul) : égalité avec une limite (0 et 0⁺), deux minimums égaux, bornes fermées de l'ED
        "x^2*e^(-x)": ([
            r"\(f(0) = 0^{2}\,e^{-0} = 0\).",
            r"\(f(2) = 2^{2}\,e^{-2} = 4 e^{-2} \approx 0{,}54\).",
        ], [
            r"<b>Minimum local</b> en \(x = 0\) : \(\left(0\,;\,0\right)\) (\(f'\) passe de \(-\) à \(+\)).",
            r"<b>Maximum local</b> en \(x = 2\) : \(\left(2\,;\,4 e^{-2}\right) \approx \left(2\,;\,0{,}54\right)\) (\(f'\) passe de \(+\) à \(-\)). Pas global : \(f(x) \to +\infty\) quand \(x \to -\infty\).",
        ]),
        "x^4-2x^2": ([
            r"\(f(-1) = \left(-1\right)^{4} - 2\left(-1\right)^{2} = 1 - 2 = -1\).",
            r"\(f(0) = 0^{4} - 2 \cdot 0^{2} = 0 - 0 = 0\).",
            r"\(f(1) = 1^{4} - 2 \cdot 1^{2} = 1 - 2 = -1\).",
        ], [
            r"<b>Minimum local</b> en \(x = -1\) : \(\left(-1\,;\,-1\right)\) (\(f'\) passe de \(-\) à \(+\)).",
            r"<b>Maximum local</b> en \(x = 0\) : \(\left(0\,;\,0\right)\) (\(f'\) passe de \(+\) à \(-\)). Pas global : \(f(x) \to +\infty\) quand \(x \to -\infty\).",
            r"<b>Minimum local</b> en \(x = 1\) : \(\left(1\,;\,-1\right)\) (\(f'\) passe de \(-\) à \(+\)).",
        ]),
        "sqrt(x^2-4)": ([
            r"\(f(-2) = \sqrt{\left(-2\right)^{2} - 4} = \sqrt{4 - 4} = 0\).",
            r"\(f(2) = \sqrt{2^{2} - 4} = \sqrt{4 - 4} = 0\).",
        ], [
            r"<b>Minimum local</b> en \(x = -2\) : \(\left(-2\,;\,0\right)\).",
            r"<b>Minimum local</b> en \(x = 2\) : \(\left(2\,;\,0\right)\).",
        ]),
        # ED fermé : aucune limite à citer ; deux autres valeurs (minimums de bord) sous le maximum
        "sqrt(4-x^2)": ([
            r"\(f(-2) = \sqrt{4 - \left(-2\right)^{2}} = \sqrt{4 - 4} = 0\).",
            r"\(f(0) = \sqrt{4 - 0^{2}} = \sqrt{4 - 0} = 2\).",
            r"\(f(2) = \sqrt{4 - 2^{2}} = \sqrt{4 - 4} = 0\).",
        ], [
            r"<b>Minimum local</b> en \(x = -2\) : \(\left(-2\,;\,0\right)\).",
            r"<b>Maximum global</b> en \(x = 0\) : \(\left(0\,;\,2\right)\) (\(f'\) passe de \(+\) à \(-\)). Les autres valeurs de f sont plus petites.",
            r"<b>Minimum local</b> en \(x = 2\) : \(\left(2\,;\,0\right)\).",
        ]),
        # deux maximums égaux (« local » seul), minimum égal à la limite 0⁺ ; 1·e^{−1} écrit e^{−1}
        "x^2e^(-x^2)": ([
            r"\(f(-1) = \left(-1\right)^{2}\,e^{-\left(-1\right)^{2}} = e^{-1} \approx 0{,}37\).",
            r"\(f(0) = 0^{2}\,e^{-0^{2}} = 0\).",
            r"\(f(1) = 1^{2}\,e^{-1^{2}} = e^{-1} \approx 0{,}37\).",
        ], [
            r"<b>Maximum local</b> en \(x = -1\) : \(\left(-1\,;\,e^{-1}\right) \approx \left(-1\,;\,0{,}37\right)\) (\(f'\) passe de \(+\) à \(-\)).",
            r"<b>Minimum local</b> en \(x = 0\) : \(\left(0\,;\,0\right)\) (\(f'\) passe de \(-\) à \(+\)).",
            r"<b>Maximum local</b> en \(x = 1\) : \(\left(1\,;\,e^{-1}\right) \approx \left(1\,;\,0{,}37\right)\) (\(f'\) passe de \(+\) à \(-\)).",
        ]),
        # borne ouverte de l'ED (0⁺) et limite 0⁻ ; x₀ = e^{−1} : ln(e^{−1}) = −1
        "x*ln(x)": ([
            r"\(f(e^{-1}) = e^{-1}\ln(e^{-1}) = e^{-1}\,\left(-1\right) = - e^{-1} \approx -0{,}37\).",
        ], [
            r"<b>Minimum global</b> en \(x = e^{-1}\) : \(\left(e^{-1}\,;\,- e^{-1}\right) \approx \left(0{,}37\,;\,-0{,}37\right)\) (\(f'\) passe de \(-\) à \(+\)). Les autres valeurs de f sont plus grandes (limites \(0^{-}\) en \(0^{+}\) et \(+\infty\) en \(+\infty\)).",
        ]),
        "x/(x^2+1)": ([
            r"\(f(-1) = \frac{\left(-1\right)}{\left(-1\right)^{2} + 1} = \frac{-1}{1 + 1} = - \frac{1}{2} \approx -0{,}50\).",
            r"\(f(1) = \frac{1}{1^{2} + 1} = \frac{1}{1 + 1} = \frac{1}{2} \approx 0{,}50\).",
        ], [
            r"<b>Minimum global</b> en \(x = -1\) : \(\left(-1\,;\,- \frac{1}{2}\right) \approx \left(-1\,;\,-0{,}50\right)\) (\(f'\) passe de \(-\) à \(+\)). Les autres valeurs de f sont plus grandes (limites \(0\) en \(\pm\infty\)).",
            r"<b>Maximum global</b> en \(x = 1\) : \(\left(1\,;\,\frac{1}{2}\right) \approx \left(1\,;\,0{,}50\right)\) (\(f'\) passe de \(+\) à \(-\)). Les autres valeurs de f sont plus petites (limites \(0\) en \(\pm\infty\)).",
        ]),
        "x^(2/3)": ([
            r"\(f(0) = \sqrt[3]{0^{2}} = 0\).",
        ], [
            r"<b>Minimum global</b> en \(x = 0\) : \(\left(0\,;\,0\right)\) (\(f'\) passe de \(-\) à \(+\)). Les autres valeurs de f sont plus grandes (limites \(+\infty\) en \(\pm\infty\)).",
        ]),
        # x₀ = 3 − 2√2 : pas de substitution en chaîne (question 41 : x₀ rationnel, ln q ou e^q)
        "(x^2-1)/(x-3)": ([
        ], [
            r"<b>Maximum local</b> en \(x = 3 - 2\sqrt{2}\) : \(\left(3 - 2\sqrt{2}\,;\,6 - 4 \sqrt{2}\right) \approx \left(0{,}17\,;\,0{,}34\right)\) (\(f'\) passe de \(+\) à \(-\)). Pas global : \(f(x) \to +\infty\) quand \(x \to 3^{+}\).",
            r"<b>Minimum local</b> en \(x = 3 + 2\sqrt{2}\) : \(\left(3 + 2\sqrt{2}\,;\,4 \sqrt{2} + 6\right) \approx \left(5{,}83\,;\,11{,}66\right)\) (\(f'\) passe de \(-\) à \(+\)). Pas global : \(f(x) \to -\infty\) quand \(x \to -\infty\).",
        ]),
    }

    def test_lignes_exactes(self):
        for entree, attendu in self.ATTENDU.items():
            with self.subTest(entree=entree):
                self.assertEqual(lignes_extremums(entree), attendu)

    def test_l_outil_derivee_garde_sa_liste(self):
        """D11 est propre à l'EC : l'outil Dérivée garde la liste « maximum local en x = … : f(…) = … »."""
        import resoudre_dv as rdv
        c = next(c for c in rdv.resoudre("e^((x^2+x-2)/(6x-12))")["cartes"] if c["titre"] == rdv.TITRE_SIGNE)
        self.assertEqual(c["blocs"][-1]["items"], [r"maximum local en \(x=0\) : \(f(0)=e^{\frac{1}{6}}\)",
                                                   r"minimum local en \(x=4\) : \(f(4)=e^{\frac{3}{2}}\)"])

    def test_sans_extremum_inchange(self):
        for entree in ("e^(2x)", "e^(1/x)", "(e^x-1)/x"):
            with self.subTest(entree=entree):
                self.assertEqual(carte_signe_ec(entree)["blocs"][-1]["html"], "Aucun extremum local.")
                self.assertIsNone(blocs_d11(entree))

    def test_lecture_des_limites(self):
        sp = ed._sympy()
        lues = {r"+\infty": sp.oo, r"-\infty": -sp.oo, "0^{+}": 0, "0^{-}": 0, "1": 1, "1^{+}": 1, "-3": -3, r"\frac{1}{2}": sp.Rational(1, 2),
                r"- \frac{3}{4}^{-}": sp.Rational(-3, 4), r"\dfrac{5}{2}": sp.Rational(5, 2)}
        for t, v in lues.items():
            with self.subTest(t=t):
                self.assertEqual(parties.lire_limite(t, sp), v)
        for t in ("?", None, r"\sqrt{2}", "e^{2}", r"\frac{1}{0}", r"\ln(2)", "1{,}5", "x"):
            with self.subTest(t=t):
                self.assertIsNone(parties.lire_limite(t, sp))


def arrondi_scientifique(v):
    """R13 (question 1 de suivi.md) : notation scientifique à 4 chiffres significatifs, « 9{,}119 \\times 10^{-4} », calculée ici."""
    d = Decimal(mp.nstr(v, 45, min_fixed=-mp.inf, max_fixed=mp.inf))
    e = d.adjusted()
    m = d.scaleb(-e).quantize(Decimal("0.001"), rounding=ROUND_HALF_UP)
    if abs(m) >= 10:
        e += 1
        m = d.scaleb(-e).quantize(Decimal("0.001"), rounding=ROUND_HALF_UP)
    t = format(m, "f")
    t = t[:-4] if t.endswith(".000") else t
    return t.replace(".", "{,}") + r" \times 10^{" + str(e) + "}"


def verifier_approchee(test, t, v, contexte):
    """t : valeur approchée affichée, en TeX dans la formule (« 1{,}18 », « -109{,}20 », « 2\\text{’}980{,}96 » ou notation
    scientifique) ; v : valeur de l'oracle. Séparateur des milliers ’ exactement dès 1000 (question 28)."""
    if r"\times" in t:
        test.assertEqual(t, arrondi_scientifique(v), contexte)
        test.assertTrue(abs(v) < mp.mpf("0.001") or abs(v) >= 10 ** 6, contexte)
    else:
        test.assertEqual(decimal_affiche(t), arrondi_oracle(v), contexte)
        test.assertEqual(r"\text{’}" in t, abs(v) >= 1000, contexte)


LIGNE_EXTREMUM = re.compile(
    r"<b>(?P<genre>Maximum|Minimum) (?P<portee>local|global)</b> en \\\(x = (?P<x>.+?)\\\)"
    r"(?: : \\\(\\left\((?P<px>.+?)\\,;\\,(?P<py>.+?)\\right\)(?: \\approx \\left\((?P<ax>.+?)\\,;\\,(?P<ay>.+?)\\right\))?\\\))?"
    r"(?: \(\\\(f'\\\) passe de \\\((?P<g>[+-])\\\) à \\\((?P<d>[+-])\\\)\))?\.(?: (?P<fin>.*))?$")


def oracle_x_y(item, f):
    """Ligne d'extremum relue à la main (format de decisions.md §2 révisé, question 43)."""
    m = LIGNE_EXTREMUM.match(item)
    assert m, item
    return m


class TestExtremumsOracle(unittest.TestCase):
    """Ce que la partie 5 affiche (D11), recoupé par l'oracle mpmath (tests/python/oracle.py : ni `evaluer`, ni SymPy, ni la sonde) :
    point exact (f(x₀) de l'oracle), arrondis, changement de signe de f′, « Maximum global » (aucune valeur de f plus grande, ou plus
    petite, sur une grille dense de l'ED et des points lointains), « pas global » (la raison : une valeur de f au-delà de f(x₀) près de
    la borne nommée, la limite écrite retrouvée), valeur en chaîne : par l'exposant (g nommé) ou par substitution (question 41), chaque
    membre de la chaîne relu et évalué, une ligne pour chaque extremum à x₀ entier."""
    GRILLE = [mp.mpf(k) / 20 - 60 + mp.mpf(1) / 977 for k in range(0, 2401)] + \
        [s * mp.mpf(10) ** k for k in range(2, 7) for s in (-1, 1)]

    def verifier(self, entree):
        f = lire(entree)
        chaine, items = lignes_extremums(entree)
        statuts, points = [], {}
        for it in items:
            m = oracle_x_y(it, f)
            s = 1 if m["genre"] == "Maximum" else -1
            x0 = nombre_affiche(m["x"])
            y = oracle.valeur(f, x0)
            self.assertIsNotNone(y, (entree, it))
            if m["px"] is not None:
                self.assertEqual(m["px"], m["x"])
                self.assertLess(abs(nombre_affiche(m["py"]) - y), mp.mpf(10) ** -35 * (1 + abs(y)), (entree, it))
                points[m["x"]] = m["py"]
            for t, v in ((m["ax"], x0), (m["ay"], y)):
                if t is None:
                    continue
                if v == mp.nint(v) and abs(v) < 10 ** 6:
                    self.assertEqual(decimal_affiche(t), Decimal(int(mp.nint(v))), (entree, it))
                else:
                    verifier_approchee(self, t, v, (entree, it))
            if m["ax"] is None and m["px"] is not None:
                self.assertTrue(x0 == mp.nint(x0) and y == mp.nint(y), (entree, it))          # sans ≈ : deux entiers
            if m["g"]:
                h = mp.mpf(10) ** -6
                avant, apres = oracle.derivee(f, x0 - h), oracle.derivee(f, x0 + h)
                self.assertEqual(("+" if avant > 0 else "-", "+" if apres > 0 else "-"), (m["g"], m["d"]), (entree, it))
                self.assertEqual(m["g"], "+" if s > 0 else "-", (entree, it))
            fin = m["fin"] or ""
            self.assertNotIn("Global :", fin)
            self.assertEqual(m["portee"] == "global", fin.startswith("Les autres valeurs de f sont"), (entree, it))
            if m["portee"] == "global":
                statuts.append("global")
                pire = max((s * (v - y) for v in (oracle.valeur(f, t) for t in self.GRILLE) if v is not None), default=None)
                self.assertIsNotNone(pire)
                self.assertLessEqual(pire, mp.mpf(10) ** -30, (entree, it))
                self.assertIn("plus petites" if s > 0 else "plus grandes", fin)
                self.assertNotIn("()", fin)
            elif fin.startswith("Pas global"):
                statuts.append("pas global")
                r = re.fullmatch(r"Pas global : \\\(f\(x\) \\to (.+?)\\\) quand \\\(x \\to (.+?)\\\)\.", fin)
                self.assertIsNotNone(r, (entree, fin))
                lim, ou = r.groups()
                if ou in (r"-\infty", r"+\infty"):
                    pts = [(-1 if ou == r"-\infty" else 1) * mp.mpf(10) ** k for k in range(1, 9)]
                else:
                    a, cote = nombre_affiche(ou[:-4]), ou[-2]
                    pts = [a + (1 if cote == "+" else -1) * mp.mpf(10) ** -k for k in range(2, 14)]
                vals = [v for v in (oracle.valeur(f, t) for t in pts) if v is not None]
                self.assertTrue(any(s * (v - y) > 0 for v in vals), (entree, it))
                if lim in (r"+\infty", r"-\infty"):
                    self.assertGreater((1 if lim == r"+\infty" else -1) * vals[-1], 10 ** 6, (entree, it))
                else:
                    self.assertLess(abs(vals[-1] - nombre_affiche(lim.replace("^{+}", "").replace("^{-}", ""))), mp.mpf("0.01"))
                    self.assertGreater(s * (nombre_affiche(lim.replace("^{+}", "").replace("^{-}", "")) - y), 0, (entree, it))
            else:
                self.assertEqual(fin, "", (entree, it))
                statuts.append("local")
        calcules = set()
        for ligne in chaine:
            m = re.fullmatch(r"\\\(g\((.+?)\) = (?:\\frac\{(-?\d+)\}\{(-?\d+)\} = )?(.+?)\\\), donc \\\(f\(\1\) = (.+?)"
                             r"(?: \\approx (.+?))?\\\)\.", ligne)
            if m:                                                         # par l'exposant (g nommé, P7b)
                x0 = mp.mpf(int(m.group(1)))
                g = oracle.valeur(f.a, x0)
                if m.group(2):
                    self.assertEqual(mp.mpf(int(m.group(2))) / int(m.group(3)), g)
                    self.assertEqual(oracle.valeur(f.a.a, x0), int(m.group(2)))                 # haut et bas calculés en x₀
                    self.assertEqual(oracle.valeur(f.a.b, x0), int(m.group(3)))
                self.assertLess(abs(nombre_affiche(m.group(4)) - g), mp.mpf(10) ** -40)
                membres, approx = [m.group(5)], m.group(6)
            else:                                                         # par substitution (question 41)
                m = re.fullmatch(r"\\\(f\((.+?)\) = (.+?)(?: \\approx (.+?))?\\\)\.", ligne)
                self.assertIsNotNone(m, ligne)
                x0 = nombre_affiche(m.group(1))
                membres, approx = m.group(2).split(" = "), m.group(3)
                self.assertGreaterEqual(len(membres), 2, ligne)
                self.assertNotRegex(m.group(2), r"\d\s*\\d?frac", ligne)                  # jamais « 4\frac{2}{3} »
            y = oracle.valeur(f, x0)
            for membre in membres:
                self.assertLess(abs(nombre_affiche(membre) - y), mp.mpf(10) ** -35 * (1 + abs(y)), (ligne, membre))
            self.assertEqual(membres[-1], points.get(m.group(1)), ligne)                   # l'écriture de l'extremum
            if approx:
                verifier_approchee(self, approx, y, ligne)
            else:
                self.assertEqual(y, mp.nint(y), ligne)
            calcules.add(m.group(1))
        for x in points:                                                  # question 41 : une ligne pour chaque extremum à x₀ entier
            if re.fullmatch(r"-?\d+", x):
                self.assertIn(x, calcules, (entree, x))
        return statuts

    def test_corpus_et_entrees_de_la_page(self):
        vus = []
        for entree in dict.fromkeys(list(TestExtremums.ATTENDU) + entrees_page("etude-complete") + CAS_LIMITES["etude-complete"]):
            r = ec.etudier(entree)
            if not (r["ok"] and r["derivee"].get("extrema")):
                continue
            with self.subTest(entree=entree):
                vus += self.verifier(entree)
        self.assertGreaterEqual(min(vus.count(s) for s in ("global", "pas global", "local")), 4, vus)

    def test_famille_au_hasard(self):
        """Polynômes, produits par une exponentielle, eˣ(k − eˣ), quotients, e^{(x² − k)/(x − b)}, x·ln(x) − k·x…"""
        hasard = random.Random(11)
        formes = ["x^3-{k}x", "x^2-{s}x+{p}", "(x^2-{k})e^({c}x)", "e^x({k}-e^x)", "x*e^({c}x)", "(x-{a})/(x^2+{k})",
                  "e^((x^2-{k})/(x-{b}))", "x^4-{k}x^2", "x*ln(x)-{k}x", "(x^2+{k})/(x-{b})", "e^({k}/(x^2-{q}))", "x^2e^(-x^2)"]
        vus = []
        for _ in range(30):
            a, b = hasard.sample(range(-4, 5), 2)
            valeurs = dict(a=a, b=b, s=a + b, p=a * b, k=hasard.randint(1, 9), q=hasard.choice([1, 4, 9]), c=hasard.choice([-2, -1, 1, 3]))
            entree = hasard.choice(formes).format(**valeurs).replace("--", "+").replace("+-", "-").replace("-+", "-")
            r = ec.etudier(entree)
            if not (r["ok"] and r["derivee"].get("extrema")):
                continue
            with self.subTest(entree=entree):
                vus += self.verifier(entree)
        self.assertGreaterEqual(vus.count("global"), 5, vus)
        self.assertGreaterEqual(vus.count("pas global"), 10, vus)


class TestGardeFousExtremums(unittest.TestCase):
    """Principe 0.2 : au moindre doute (SymPy et sonde en désaccord, sonde qui contredit, limite illisible ou absente, borne fermée qui
    n'est pas un extremum, erreur), « local » seul, jamais « global » ni « pas global » ; sans SymPy, la liste de l'outil Dérivée."""

    def locales_seules(self, items):
        for it in items:
            self.assertNotIn("global", it.lower(), it)

    def test_sonde_globale_contredit(self):
        """a : une valeur de f plus grande que 1 trouvée par la sonde (fausse ici, au-delà de x = 5) : pas de « global »."""
        vraie = parties.valeur_mp

        def fausse(n, x):
            v = vraie(n, x)
            return v + 2 if (v is not None and x > 5) else v
        with mock.patch.object(parties, "valeur_mp", fausse):
            items = items_d11("e^(-x^2)")
        self.assertEqual(items, [rf"{MAX} en \(x = 0\) : \(\left(0\,;\,1\right)\) {PLUS_MOINS}."])

    def test_sonde_pas_global_ne_trouve_rien(self):
        """b, maximum en 3 : la sonde (faussée) ne trouve aucune valeur au-delà de f(3) près de −∞ : pas de « pas global »."""
        vraie = parties.valeur_mp

        def fausse(n, x):
            v = vraie(n, x)
            return mp.mpf(-1000) if (v is not None and x < -1) else v
        with mock.patch.object(parties, "valeur_mp", fausse):
            items = items_d11("(x^2-6)e^(-2x)")
        self.assertTrue(items[1].endswith(rf"\approx \left(3\,;\,0{{,}}0074\right)\) {PLUS_MOINS}."), items[1])
        self.assertNotIn("global", items[1].lower())

    def test_sympy_contredit_la_sonde(self):
        """x/(x² + 1) : le signe exact de f(x₀) − 0 inversé : SymPy et mpmath en désaccord, « local » seul."""
        with mock.patch.object(parties, "_signe_sp", lambda v: -1 if v > 0 else 1):
            self.locales_seules(items_d11("x/(x^2+1)"))

    def test_sympy_ne_tranche_pas(self):
        def indecis(v):
            raise parties.Doute()
        with mock.patch.object(parties, "_signe_sp", indecis):
            self.locales_seules(items_d11("x/(x^2+1)"))

    def test_limite_illisible_ou_absente(self):
        lim = ec.etudier("e^((x^2+x-2)/(6x-12))")["variations_limites"]
        for modif in ({"moins_inf": "?"}, {"moins_inf": r"\sqrt{2}"}, {"plus_inf": None},
                      {"colonnes": [dict(lim["colonnes"][0], droite=None)]}, {"colonnes": []}):
            with self.subTest(modif=modif):
                items = items_d11("e^((x^2+x-2)/(6x-12))", dict(lim, **modif))
                self.locales_seules(items)
                self.assertEqual(len(items), 2)

    def test_limite_qui_cache_un_depassement(self):
        """D11 littéral : une limite « ? » suffit pour « local » seul, même si une autre borne prouverait « pas global »."""
        lim = ec.etudier("(x^2-6)e^(-2x)")["variations_limites"]
        self.locales_seules(items_d11("(x^2-6)e^(-2x)", dict(lim, plus_inf="?")))

    def test_valeur_exacte_contredite_par_la_sonde(self):
        """f_py faux : ni ≈, ni « global », ni valeur en chaîne (ni par l'exposant, ni par substitution)."""
        r = ec.etudier("e^((x^2+x-2)/(6x-12))")
        dv = dict(r["derivee"], extrema=[dict(e, f_py="exp(2)") for e in r["derivee"]["extrema"]])
        blocs = parties.blocs_extremums(dv, r["variations_limites"], ec.analyse("e^((x^2+x-2)/(6x-12))"))
        self.assertEqual([b["type"] for b in blocs], ["liste"])
        for it in blocs[0]["items"]:
            self.assertNotIn(r"\approx", it)
            self.assertNotIn("global", it.lower())

    def test_valeur_inconnue(self):
        """Valeur non exacte (pas de f_py) : le point n'est pas écrit en coordonnées, aucune affirmation."""
        r = ec.etudier("x^2-4x+3")
        e = {k: v for k, v in r["derivee"]["extrema"][0].items() if k not in ("x_py", "f_py")}
        for f_tex, attendu in ((r"{\approx}\,-1{,}00", rf"{MIN} en \(x = 2\) : \(f(2) {{\approx}}\,-1{{,}}00\) {MOINS_PLUS}."),
                               ("?", rf"{MIN} en \(x = 2\) {MOINS_PLUS}.")):
            dv = dict(r["derivee"], extrema=[dict(e, f_tex=f_tex)])
            blocs = parties.blocs_extremums(dv, r["variations_limites"], ec.analyse("x^2-4x+3"))
            self.assertEqual(blocs[-1]["items"], [attendu])

    def test_erreur_pendant_le_statut(self):
        with mock.patch.object(parties, "_bornes_de_l_ed", side_effect=RuntimeError("panne")):
            items = items_d11("e^(-x^2)")
        self.assertEqual(items, [rf"{MAX} en \(x = 0\) : \(\left(0\,;\,1\right)\) {PLUS_MOINS}."])

    def test_sans_sympy(self):
        """Sans SymPy : la liste de l'outil Dérivée, telle quelle."""
        with mock.patch.object(parties, "charger_sympy", return_value=None):
            self.assertIsNone(blocs_d11("e^(-x^2)"))
            c = carte_signe_ec("e^(-x^2)")
        self.assertEqual(c["blocs"][-1]["items"], [r"maximum local en \(x=0\) : \(f(0)=1\)"])

    def test_borne_fermee_qui_n_est_pas_un_extremum(self):
        """sqrt(x² − 4) privé de son minimum en 2 : la borne fermée 2 n'est plus un extremum connu, « local » seul pour l'autre."""
        r = ec.etudier("sqrt(x^2-4)")
        dv = dict(r["derivee"], extrema=r["derivee"]["extrema"][:1])
        sp = ed._sympy()
        with mpmath.workdps(parties.CHIFFRES):
            _, f, ED = ec.analyse("sqrt(x^2-4)")
            crit = dv["table_signe"]["crit"]
            cellules = dv["table_signe"]["rows"][-2]["cells"]
            with self.assertRaises(parties.Doute):
                parties._bornes_de_l_ed(ed.fusion(ED), crit, r["variations_limites"], {"-2"})
            with self.assertRaises(parties.Doute):
                parties.statut_global(dv["extrema"][0], dv["extrema"], ed.fusion(ED), crit, cellules, r["variations_limites"], f, sp, mp)
        self.locales_seules(parties.blocs_extremums(dv, r["variations_limites"], ec.analyse("sqrt(x^2-4)"))[-1]["items"])

    def test_chaine_refusee_sans_g_nomme_ou_x_non_entier(self):
        sp = ed._sympy()
        f = lire("e^((x^2+x-2)/(6x-12))")
        with mpmath.workdps(parties.CHIFFRES):
            self.assertIsNone(parties.valeur_par_l_exposant(f, {"x_tex": r"\frac{1}{2}", "x_py": "1/2", "f_py": "exp(3/4)",
                                                               "f_tex": "?"}, sp, mp))
            self.assertIsNone(parties.valeur_par_l_exposant(lire("x^2-4x+3"), {"x_tex": "2", "x_py": "2", "f_py": "-1", "f_tex": "-1"},
                                                            sp, mp))
            self.assertIsNone(parties.valeur_par_l_exposant(f, {"x_tex": "4", "x_py": "4", "f_py": "exp(2)", "f_tex": "e^{2}"}, sp, mp))


class TestValeurParSubstitution(unittest.TestCase):
    """Question 41 : « f(−2) = ((−2)² − 6)e^{−2·(−2)} = (4 − 6)e⁴ = −2e⁴ ≈ −109,20 » ; garde-fous forcés : aucune ligne."""

    def ligne(self, entree, i=0, **modif):
        r = ec.etudier(entree)
        e = dict(r["derivee"]["extrema"][i], **modif)
        with mpmath.workdps(parties.CHIFFRES):
            b = parties.valeur_par_substitution(lire(entree), e, ed._sympy(), mpmath)
        return None if b is None else b["html"]

    def test_lignes_du_corrige(self):
        self.assertEqual(self.ligne("(x^2-6)e^(-2x)"), r"\(f(-2) = \left(\left(-2\right)^{2} - 6\right)\,e^{-2\left(-2\right)} = "
                                                       r"\left(4 - 6\right)\,e^{4} = - 2 e^{4} \approx -109{,}20\).")
        self.assertEqual(self.ligne("e^x(6-e^x)"), r"\(f(\ln(3)) = e^{\ln(3)}\,\left(6 - e^{\ln(3)}\right) = 3\left(6 - 3\right) = 9\).")

    def test_x0_fractionnaire_entre_parentheses(self):
        """x₀ = 3/2 : « 2(3/2)² − 6(3/2) + 4 », jamais « 6\frac{3}{2} » (lu « six et trois demis »)."""
        t = self.ligne("2x^2-6x+4")
        self.assertEqual(t, r"\(f(\frac{3}{2}) = 2\left(\frac{3}{2}\right)^{2} - 6\left(\frac{3}{2}\right) + 4 = \frac{9}{2} - 9 + 4 = "
                            r"- \frac{1}{2} \approx -0{,}50\).")

    def test_produits_par_0_et_1(self):
        """1·e^{−1} s'écrit e^{−1} (« 1e^{−1} » se lirait comme une notation scientifique), 0·a = 0, e⁰ = 1."""
        self.assertEqual(self.ligne("x^2e^(-x^2)"), r"\(f(-1) = \left(-1\right)^{2}\,e^{-\left(-1\right)^{2}} = e^{-1} \approx 0{,}37\).")
        self.assertEqual(self.ligne("x^2*e^(-x)"), r"\(f(0) = 0^{2}\,e^{-0} = 0\).")
        for entree in ("x^2e^(-x^2)", "x^2*e^(-x)", "x*ln(x)", "3(x*ln(x))"):
            for i in range(len(ec.etudier(entree)["derivee"]["extrema"])):
                with self.subTest(entree=entree, i=i):
                    self.assertNotRegex(self.ligne(entree, i), r"(?<![\d^{])[01]e\^")

    def test_refus(self):
        """x₀ irrationnel (3 − 2√2), valeur fausse, écriture de x₀ différente : aucune ligne."""
        self.assertIsNone(self.ligne("(x^2-1)/(x-3)"))
        self.assertIsNone(self.ligne("(x^2-6)e^(-2x)", f_py="-2*exp(5)"))
        self.assertIsNone(self.ligne("(x^2-6)e^(-2x)", x_tex="-3"))

    def test_garde_fous_forces(self):
        """Un membre faux (SymPy le refuse), SymPy aveuglé (la sonde le refuse), une écriture ambiguë « 4\\frac{2}{3} » : aucune ligne."""
        self.assertIsNotNone(self.ligne("(x^2-6)e^(-2x)"))
        with mock.patch.object(parties, "calculer_produits", lambda n: lire("7")):
            self.assertIsNone(self.ligne("(x^2-6)e^(-2x)"))
        vrai = parties.en_sympy_reel
        juste = vrai(lire("(x^2-6)e^(-2x)")).subs(parties.SYMPY["x"], -2)
        with mock.patch.object(parties, "calculer_produits", lambda n: lire("7")), \
                mock.patch.object(parties, "en_sympy_reel", lambda T: juste if parties.tex(T) == "7" else vrai(T)):
            self.assertIsNone(self.ligne("(x^2-6)e^(-2x)"))
        with mock.patch.object(parties, "substitution_ecrite", lambda f, x0: Nb(F(0), r"4\frac{2}{3}")):
            self.assertIsNone(self.ligne("(x^2-6)e^(-2x)"))

    def test_chaque_extremum_a_sa_ligne(self):
        """Une ligne de calcul pour chaque extremum (x₀ rationnel, ln q ou e^q), avant la liste, dans l'ordre des extremums."""
        for entree, nombre in (("x^4-2x^2", 3), ("(x^2-6)e^(-2x)", 2), ("e^((x^2+x-2)/(6x-12))", 2), ("ln(x)/x", 1), ("x^x", 1),
                               ("(x^2-1)/(x-3)", 0)):
            with self.subTest(entree=entree):
                chaine, items = lignes_extremums(entree)
                self.assertEqual(len(chaine), nombre, chaine)



# ---------------------------------------------------------------------------------------------------------------------------
# Partie 6. Graphe (D15, P8) : ronds vides, points marqués, cadrage (decisions.md §3)
# ---------------------------------------------------------------------------------------------------------------------------
# saisie : points exclus de l'ED (écrits à la main, pour l'oracle)
EXCLUS = {
    "e^((x^2+x-2)/(6x-12))": [2], "e^(2/(x^2-4))": [-2, 2], "e^(1/x)": [0], "e^(-1/x)": [0], "x/sqrt(x^2)": [0],
    "e^(1/(x-1))+3": [1], "e^(x/(x^2-1))": [-1, 1], "(x+1)e^(1/x)": [0], "1/x": [0], "(x^2-1)/(x-1)": [1], "(e^x-1)/x": [0],
    "x*ln(x)": [0], "ln(x)/x": [0], "e^(1/x^2)": [0], "e^(-1/x^2)": [0], "(x^2-1)/(x-3)": [3],
}
ILLISIBLE = {"e^(1/(x-1))+e": [1]}          # limite finie e en 1⁻ : écriture hors de la liste fermée de lire_limite, pas de rond


def limite_oracle(f, a, s):
    """Limite latérale de l'arbre f en a (côté s = ±1) par l'oracle (50 chiffres, sans SymPy ni `evaluer`) : nombre, ±inf, ou None
    si f n'est pas définie de ce côté."""
    vs = [oracle.valeur(f, mp.mpf(a) + s * mp.mpf(10) ** -k) for k in (6, 9, 12, 15)]
    if any(v is None for v in vs):
        return None
    if abs(vs[-1]) > 10 ** 6 and abs(vs[-1]) > abs(vs[0]):
        return mp.inf if vs[-1] > 0 else -mp.inf
    assert abs(vs[-1] - vs[-2]) < mp.mpf("1e-5"), (a, s, vs)
    return vs[-1]


def ronds_attendus(entree, exclus):
    """(ronds vides, trous) d'après l'oracle : un point exclu dont toutes les limites latérales définies sont finies et égales est un
    trou (dessiné d'après l'outil Limites) ; sinon chaque côté de limite finie donne un rond vide."""
    f = lire(entree)
    ronds, trous = [], []
    for a in exclus:
        assert oracle.valeur(f, a) is None, (entree, a)
        lims = [L for L in (limite_oracle(f, a, -1), limite_oracle(f, a, 1)) if L is not None]
        finies = [L for L in lims if mp.isfinite(L)]
        if lims and len(finies) == len(lims) and all(abs(L - finies[0]) < mp.mpf("1e-6") for L in finies):
            trous.append((float(a), float(finies[0])))
        else:
            ronds += [(float(a), float(L)) for L in finies]
    return sorted(ronds), sorted(trous)


def proche_liste(test, obtenu, attendu, contexte):
    test.assertEqual(len(obtenu), len(attendu), (contexte, obtenu, attendu))
    for (x, y), (a, b) in zip(sorted(obtenu), sorted(attendu)):
        test.assertAlmostEqual(x, a, delta=1e-9, msg=contexte)
        test.assertAlmostEqual(y, b, delta=1e-6, msg=contexte)


class TestRondsVides(unittest.TestCase):
    def test_oracle(self):
        """Chaque point exclu à limite finie d'un côté (ou deux limites finies différentes) a un rond vide, et seulement lui ; un trou
        (limites finies égales, ou bord de l'ED) est dessiné d'après l'outil Limites, sans rond en double."""
        for entree, exclus in EXCLUS.items():
            with self.subTest(entree=entree):
                r = ec.etudier(entree)
                ronds, trous = ronds_attendus(entree, exclus)
                proche_liste(self, [tuple(p) for p in r["graphique"]["ronds_vides"]], ronds, entree)
                trous_outil = [(a["point_val"], a["valeur_val"]) for a in r["limites"]["asymptotes"] if a["genre"] == "trou"]
                proche_liste(self, trous_outil, trous, entree)

    def test_valeurs_attendues(self):
        attendu = {"e^((x^2+x-2)/(6x-12))": [[2.0, 0.0]], "e^(2/(x^2-4))": [[-2.0, 0.0], [2.0, 0.0]], "x/sqrt(x^2)": [[0.0, -1.0], [0.0, 1.0]],
                   "e^(1/(x-1))+3": [[1.0, 3.0]], "e^(x/(x^2-1))": [[-1.0, 0.0], [1.0, 0.0]], "1/x": [], "(x^2-1)/(x-1)": []}
        for entree, ronds in attendu.items():
            with self.subTest(entree=entree):
                self.assertEqual(ec.etudier(entree)["graphique"]["ronds_vides"], ronds)

    def test_limite_illisible_pas_de_rond(self):
        """La limite finie existe (oracle), mais s'écrit hors de la liste fermée (e) : pas de rond (rien plutôt qu'un rond non
        confirmé)."""
        for entree, exclus in ILLISIBLE.items():
            with self.subTest(entree=entree):
                self.assertTrue(ronds_attendus(entree, exclus)[0])
                self.assertEqual(ec.etudier(entree)["graphique"]["ronds_vides"], [])

    def test_limite_laterale_par_les_regles(self):
        """Les règles (e^{lim u}, produit et somme de limites finies) donnent la limite de SymPy, beaucoup plus vite."""
        sp = parties.charger_sympy()
        x = parties.SYMPY["x"]
        for expr, a, cote in ((sp.exp((x ** 2 + x - 2) / (6 * x - 12)), 2, "-"), (x * sp.exp(1 / (x - 1)), 1, "-"),
                              (sp.exp(1 / (x - 1)) + 3, 1, "-"), (sp.exp(2 / (x ** 2 - 4)), -2, "+"), (sp.exp(1 / x), 0, "+"),
                              (x / sp.sqrt(x ** 2), 0, "-"), ((x + 1) * sp.exp(1 / x), 0, "-")):
            with self.subTest(expr=expr, a=a, cote=cote):
                self.assertEqual(parties.limite_laterale(expr, sp.Integer(a), cote, sp), sp.limit(expr, x, a, cote))


def ronds_d(entree, **faux):
    """Ronds vides d'etudier() avec des fonctions de parties.py remplacées."""
    with ExitStack() as pile:
        for nom, valeur in faux.items():
            pile.enter_context(mock.patch.object(parties, nom, valeur))
        return ec.etudier(entree)["graphique"]["ronds_vides"]


class TestGardeFousRondsVides(unittest.TestCase):
    """Principe 0.2 : un rond vide n'est dessiné que si SymPy et la sonde confirment la limite ; au moindre doute, pas de rond."""
    EX7, D = "e^((x^2+x-2)/(6x-12))", "e^(2/(x^2-4))"

    def test_limite_sympy_differente(self):
        vraie = parties.limite_laterale
        self.assertEqual(ronds_d(self.EX7, limite_laterale=lambda fe, a, cote, sp: vraie(fe, a, cote, sp) + 1), [])

    def test_limite_sympy_en_echec(self):
        def echec(*args):
            raise parties.Doute()
        self.assertEqual(ronds_d(self.D, limite_laterale=echec), [])

    def test_limite_sympy_d_un_seul_cote_fausse(self):
        """d : SymPy se trompe en −2⁺ seulement ; le rond (2 ; 0) reste."""
        vraie = parties.limite_laterale
        fausse = lambda fe, a, cote, sp: vraie(fe, a, cote, sp) + (1 if a == -2 else 0)
        self.assertEqual(ronds_d(self.D, limite_laterale=fausse), [[2.0, 0.0]])

    def sonde(self, transformer):
        vraie = parties.valeur_mp

        def fausse(n, x):
            v = vraie(n, x)
            return transformer(v) if (v is not None and abs(x - 2) < mp.mpf("0.01") and parties.tex(n) == parties.tex(lire(self.EX7))) else v
        return fausse

    def test_sonde_qui_ne_s_approche_pas(self):
        self.assertEqual(ronds_d(self.EX7, valeur_mp=self.sonde(lambda v: v + mp.mpf("0.001"))), [])

    def test_sonde_du_mauvais_cote(self):
        """Le tableau écrit 0⁺ ; la sonde trouve des valeurs négatives : pas de rond."""
        self.assertEqual(ronds_d(self.EX7, valeur_mp=self.sonde(lambda v: -v)), [])

    def test_sonde_non_definie(self):
        self.assertEqual(ronds_d(self.EX7, valeur_mp=self.sonde(lambda v: None)), [])

    def test_point_dans_l_ed(self):
        self.assertEqual(ronds_d(self.EX7, appartient=lambda ivs, v, sp: True), [])

    def test_ecriture_illisible(self):
        self.assertEqual(ronds_d(self.EX7, lire_limite=lambda t, sp: None), [])

    def test_sans_sympy(self):
        self.assertEqual(ronds_d(self.EX7, charger_sympy=lambda: None), [])

    def test_sans_rond_le_graphique_reste_juste(self):
        """Sans rond (doute), la fenêtre contient toujours les points à montrer et le bloc de la page n'a pas de rond."""
        with mock.patch.object(parties, "lire_limite", lambda t, sp: None):
            s = rec.resoudre(self.EX7)
        g = next(b for c in s["cartes"] for b in c["blocs"] if b["type"] == "graphique")
        self.assertEqual(g["ronds_vides"], [])
        self.assertTrue(g["xmin"] < 0 < 4 < g["xmax"] and g["ymin"] < 0 < 4.49 < g["ymax"], g)


class TestPointsMarques(unittest.TestCase):
    def test_zeros_et_f0_de_la_partie_3(self):
        """Les points marqués sont les zéros et f(0) écrits par la partie 3 (oracle : f s'y annule, f(0) juste), sans les extremums."""
        for entree in ("(x^2-6)e^(-2x)", "e^x(6-e^x)", "x^3-3x", "x^2-4x+3", "(x^2-1)/(x-3)", "ln(x)/x", "x^2*e^(-x)", "e^(1/x)"):
            with self.subTest(entree=entree):
                r = ec.etudier(entree)
                f = lire(entree)
                extremums = {(e["x_val"], e["f_val"]) for e in r["derivee"]["extrema"]}
                for p in r["graphique"]["points"]:
                    x, y = mp.mpf(p["x_val"]), mp.mpf(p["f_val"])
                    self.assertAlmostEqual(float(oracle.valeur(f, x)), float(y), delta=1e-9)
                    self.assertTrue(y == 0 or x == 0, p)
                    self.assertNotIn((p["x_val"], p["f_val"]), extremums)

    def test_doute_de_la_partie_3_rien_de_marque(self):
        """La partie 3 doute (sonde du signe contredite) : aucun zéro marqué ; f(0), confirmé à part, reste."""
        def doute(*args):
            raise parties.Doute()
        with mock.patch.object(parties, "confirmer_signe", doute):
            r, p3 = ec.etude_et_partie3("(x^2-6)e^(-2x)")
        self.assertEqual(p3["zeros"], [])
        self.assertEqual(r["graphique"]["points"], [{"x_val": 0.0, "f_val": -6.0}])
        with mock.patch.object(parties, "charger_sympy", lambda: None):
            r = ec.etudier("(x^2-6)e^(-2x)")
        self.assertEqual(r["graphique"]["points"], [])

    def test_partie_3_calculee_une_fois(self):
        """resoudre() : une seule partie 3 (cartes et données du graphique du même calcul)."""
        vraie, appels = parties.partie3, []

        def espion(a):
            appels.append(a)
            return vraie(a)
        with mock.patch.object(parties, "partie3", espion):
            s = rec.resoudre("(x^2-6)e^(-2x)")
        self.assertEqual(len(appels), 1)
        t = [c["titre"] for c in s["cartes"]]
        self.assertEqual(s["cartes"][t.index(rec.PARTIES[2]) + 1:t.index(rec.PARTIES[3])], cartes_zeros("(x^2-6)e^(-2x)"))


CADRAGE = ["e^((x^2+x-2)/(6x-12))", "e^(-x^2)", "(x^2-6)e^(-2x)", "e^x(6-e^x)", "e^(2/(x^2-4))", "e^x", "e^(-x)", "x*e^x",
           "x^2*e^(-x)", "e^(1/x)", "e^(-1/x)", "1/(x^2+1)", "x/(x^2+1)", "(x^2-1)/(x-3)", "e^(x/(x^2-1))", "(e^x-1)/x", "1/x",
           "x^3-3x", "x/sqrt(x^2)", "e^(1/(x-1))+3"]


class TestCadrage(unittest.TestCase):
    """decisions.md §3, recoupé par l'oracle : la fenêtre contient les extremums, les zéros, (0 ; f(0)) et les ronds vides ; pour chaque
    AH y = L en ±∞, un x de la fenêtre, au-delà de tous les points à montrer et des valeurs interdites (lecture de la question 3),
    où |f(x) − L| < 5 % de la hauteur de la fenêtre."""

    def test_criteres_du_graphe(self):
        for entree in CADRAGE:
            with self.subTest(entree=entree):
                r = ec.etudier(entree)
                f, g = lire(entree), r["graphique"]
                montres = [(e["x_val"], e["f_val"]) for e in r["derivee"]["extrema"]] + \
                          [(p["x_val"], p["f_val"]) for p in g["points"]] + [tuple(p) for p in g["ronds_vides"]]
                for x, y in montres:
                    self.assertTrue(g["xmin"] < x < g["xmax"] and g["ymin"] < y < g["ymax"], (x, y, g["xmin"], g["xmax"], g["ymin"], g["ymax"]))
                reperes = [x for x, _ in montres] + EXCLUS.get(entree, [])           # points à montrer et valeurs interdites
                hauteur = g["ymax"] - g["ymin"]
                for a in r["limites"]["asymptotes"]:
                    if a["genre"] != "horizontale":
                        continue
                    L, droite = a["valeur_val"], a["ou"].endswith(r"+\infty")
                    self.assertAlmostEqual(float(oracle.valeur(f, mp.mpf(10) ** 6 * (1 if droite else -1))), L, delta=1e-3)
                    bas, haut = (max(reperes), g["xmax"]) if droite else (g["xmin"], min(reperes))
                    xs = [mp.mpf(bas) + (mp.mpf(haut) - bas) * k / 200 for k in range(201)]
                    vs = [v for v in (oracle.valeur(f, x) for x in xs) if v is not None]
                    self.assertTrue(any(abs(v - L) < mp.mpf("0.05") * hauteur for v in vs), (entree, droite, bas, haut))

    def test_c_l_ah_gauche_se_voit(self):
        """c : avant P8, la branche qui file vers −∞ fixait l'échelle (y de −51 à 21) ; maintenant la fenêtre en y suit les points à
        montrer (entre 0 et 9) et l'approche de y = 0 à gauche se voit."""
        g = ec.etudier("e^x(6-e^x)")["graphique"]
        self.assertLess(g["ymax"] - g["ymin"], 20)
        self.assertLessEqual(g["xmin"], -2)

    def test_approche_trop_lente_fenetre_des_points(self):
        """ln(x)/x : l'approche de y = 0 demanderait une fenêtre plus de 3,8 fois plus large : la fenêtre reste celle des points à
        montrer (le graphe n'est pas écrasé)."""
        g = ec.etudier("ln(x)/x")["graphique"]
        self.assertLess(g["xmax"], 6)

    def test_fenetre_ne_recalcule_rien(self):
        """Le zoom (fenetre) ne relance ni la partie 3 ni les ronds vides."""
        with mock.patch.object(parties, "partie3", side_effect=AssertionError), \
                mock.patch.object(parties, "ronds_vides", side_effect=AssertionError):
            self.assertTrue(ec.fenetre("e^((x^2+x-2)/(6x-12))", -5, 5)["ok"])
