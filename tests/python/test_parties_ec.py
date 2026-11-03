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
            r"\(f(1) = -5e^{-2}\) ≈ −0,68", r"\(f(-1) = -5e^{2}\) ≈ −36,95", r"\(f(-1) \neq f(1)\) : f n'est pas paire.", parties.NI])],
        "e^x(6-e^x)": [SYM, ("Pas impaire", [
            r"\(f(0) = 5 \neq 0\)", r"Une fonction impaire vérifie \(f(0) = 0\) : f n'est pas impaire."]), ("Pas paire", [
            r"\(f(1) = e\,\left(6 - e\right)\) ≈ 8,92", r"\(f(-1) = e^{-1}\,\left(6 - e^{-1}\right)\) ≈ 2,07",
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
            r"\(f(1) = e\) ≈ 2,72, donc \(-f(1)\) ≈ −2,72", r"\(f(-1) = e^{-1}\) ≈ 0,37",
            r"\(f(-1) \neq -f(1)\) : f n'est pas impaire."]), ("Pas paire", [
            r"\(f(1) = e\) ≈ 2,72", r"\(f(-1) = e^{-1}\) ≈ 0,37", r"\(f(-1) \neq f(1)\) : f n'est pas paire.", parties.NI])],
        "x^2-4x+3": [SYM, ("Pas impaire", [
            r"\(f(0) = 3 \neq 0\)", r"Une fonction impaire vérifie \(f(0) = 0\) : f n'est pas impaire."]), ("Pas paire", [
            r"\(f(1) = 0\)", r"\(f(-1) = 8\)", r"\(f(-1) \neq f(1)\) : f n'est pas paire.", parties.NI])],
        "x^3-x": [SYM, ("Calcul de f(−x)", [
            r"\(f(-x) = \left(-x\right)^{3} - \left(-x\right)\) (on remplace x par −x)",
            r"\( = -x^{3} + x\) (car \(\left(-x\right)^{3} = -x^{3}\) ; règle des signes)",
            r"\( = -\left(x^{3} - x\right)\) (mise en évidence de −1)", r"\( = -f(x)\)", parties.IMPAIRE])],
        "x^2*e^x": [SYM, ("Pas impaire", [
            r"\(f(1) = e\) ≈ 2,72, donc \(-f(1)\) ≈ −2,72", r"\(f(-1) = e^{-1}\) ≈ 0,37",
            r"\(f(-1) \neq -f(1)\) : f n'est pas impaire."]), ("Pas paire", [
            r"\(f(1) = e\) ≈ 2,72", r"\(f(-1) = e^{-1}\) ≈ 0,37", r"\(f(-1) \neq f(1)\) : f n'est pas paire.", parties.NI])],
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
        self.assertEqual(pas_paire[:2], [r"\(f(5) = \frac{5001}{200}\) ≈ 25,01", r"\(f(-5) = \frac{4999}{200}\) ≈ 25,00"])

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
    return Decimal(t.replace("−", "-").replace(",", "."))


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
                m = re.match(r"\\\(f\((.*?)\) = (.*?)( \\neq 0)?\\\)(?: \(?≈ ([−0-9]+(?:,[0-9]+)?)\)?)?", h)
                if not m:
                    continue
                a = lire_rationnel(m.group(1))
                v = oracle.valeur(f, mp.mpf(a.numerator) / a.denominator)
                self.assertIsNotNone(v, (entree, a))
                if m.group(4):                                            # valeur approchée : l'arrondi de l'oracle
                    self.assertEqual(decimal_affiche(m.group(4)), arrondi_oracle(v), (entree, h))
                    affiche = decimal_affiche(m.group(4))
                else:                                                     # entier exact
                    self.assertTrue(re.fullmatch(r"-?\d+", m.group(2)), h)
                    self.assertLess(abs(v - int(m.group(2))), mp.mpf(10) ** -40, (entree, h))
                    affiche = Decimal(int(m.group(2)))
                if m.group(3):
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
        self.assertIsNone(parties.arrondi(Decimal("1234.5")))
        self.assertEqual(parties.ecrire_decimal(Decimal("-0.68")), "−0,68")
        self.assertEqual(parties.ecrire_decimal(-Decimal(0)), "0")

    def test_parite_lue_et_plier(self):
        for entree, p in (("e^(-x^2)", 1), ("x^3-3x", -1), ("x/(x^2+1)", -1), ("x^(2/3)", 1), ("x^(1/3)", None), ("e^x+e^(-x)", None),
                          ("x^3+1", None), ("2^x", None), ("(x^3-x)^2", None), ("sqrt(x^2-4)", 1), ("ln(x^2+1)/x", -1)):
            with self.subTest(entree=entree):
                self.assertEqual(parties.parite_lue(lire(entree)), p)
        for entree, a, ecrit in (("(x^2-6)e^(-2x)", 1, "-5e^{-2}"), ("e^x(6-e^x)", 0, "5"), ("e^(1/x)", 1, "e"), ("x^2*e^(-x)", -1, "e"),
                                 ("ln(x)+x", 1, "1")):
            with self.subTest(entree=entree, a=a):
                self.assertEqual(parties.tex(parties.plier(parties.substituer(lire(entree), parties.nombre(a)))), ecrit)


if __name__ == "__main__":
    unittest.main()
