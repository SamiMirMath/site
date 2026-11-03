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
            ordonnee(r"\(g(0) = \frac{-2}{-12} = \frac{1}{6}\), donc \(f(0) = e^{\frac{1}{6}}\) ≈ 1,18.",
                     r"Le graphe coupe l'axe des y au point \((0\,;\,e^{\frac{1}{6}})\).")],
        "e^(-x^2)": [
            ("Zéros et signe de f", [rf"\(e^{{-x^{{2}}}} > 0\) pour tout \(x\) {POSITIVE}.", r"Donc f n'a pas de zéro et \(f(x) > 0\) sur ED."]),
            ordonnee(r"\(f(0) = 1\).", r"Le graphe coupe l'axe des y au point \((0\,;\,1)\).")],
        "(x^2-6)e^(-2x)": [
            ("Zéros de f", [rf"\(e^{{-2x}} > 0\) pour tout \(x\) {POSITIVE} ; il ne s'annule jamais.",
                            r"\(\left(x^{2} - 6\right)\,e^{-2x} = 0\)", r"\(\iff x^{2} - 6 = 0\) (car \(e^{-2x} > 0\))", r"\(\iff x^{2} = 6\)",
                            r"\(\iff\) \(x = -\sqrt{6}\) ≈ −2,45 ou \(x = \sqrt{6}\) ≈ 2,45"]),
            ("Signe de f", [("TABLEAU", [r"-\sqrt{6}", r"\sqrt{6}"], [(r"\left(x^{2} - 6\right)", "+0-0+"), ("e^{-2x}", "+++++"),
                                                                       ("f(x)", "+0-0+")])]),
            ordonnee(r"\(f(0) = -6\).", r"Le graphe coupe l'axe des y au point \((0\,;\,-6)\).")],
        "e^x(6-e^x)": [
            ("Zéros de f", [rf"\(e^{{x}} > 0\) pour tout \(x\) {POSITIVE} ; il ne s'annule jamais.", r"\(e^{x}\,\left(6 - e^{x}\right) = 0\)",
                            r"\(\iff 6 - e^{x} = 0\) (car \(e^{x} > 0\))",
                            r"\(\iff e^{x} = 6\) (on isole \(e^{x}\) du côté où son coefficient est positif)", r"\(\iff\) \(x = \ln(6)\) ≈ 1,79"]),
            ("Signe de f", [("TABLEAU", [r"\ln(6)"], [("e^{x}", "+++"), (r"\left(6 - e^{x}\right)", "+0-"), ("f(x)", "+0-")])]),
            ordonnee(r"\(f(0) = 5\).", r"Le graphe coupe l'axe des y au point \((0\,;\,5)\).")],
        "e^(2/(x^2-4))": [
            ("Zéros et signe de f", [rf"\(e^{{\frac{{2}}{{x^{{2}} - 4}}}} > 0\) pour tout \(x \in ED\) {POSITIVE}.",
                                     r"Donc f n'a pas de zéro et \(f(x) > 0\) sur ED."]),
            ordonnee(r"\(f(0) = e^{-\frac{1}{2}}\) ≈ 0,61.", r"Le graphe coupe l'axe des y au point \((0\,;\,e^{-\frac{1}{2}})\).")],
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
        "x^2-4x+3": [
            ("Zéros de f", [r"\(x^{2} - 4x + 3 = 0\)", r"\(\iff (x - 1)(x - 3) = 0\) (Somme-Produit)",
                            r"\(\iff x - 1 = 0 \text{ ou } x - 3 = 0\) (produit nul)", r"\(\iff\) \(x = 1\) ou \(x = 3\)"]),
            ("Signe de f", [("TABLEAU", ["1", "3"], [(r"\left(x^{2} - 4x + 3\right)", "+0-0+"), ("f(x)", "+0-0+")])]),
            ordonnee(r"\(f(0) = 3\).", r"Le graphe coupe l'axe des y au point \((0\,;\,3)\).")],
        "x^4-2x^2": [
            ("Zéros de f", [r"\(x^{4} - 2x^{2} = 0\)", r"\(\iff x^{2}(x^{2} - 2) = 0\) (mise en évidence)",
                            r"\(\iff x = 0 \text{ ou } x^{2} - 2 = 0\) (produit nul)", r"\(\iff x = 0 \text{ ou } x^{2} = 2\)",
                            r"\(\iff\) \(x = -\sqrt{2}\) ≈ −1,41 ou \(x = 0\) ou \(x = \sqrt{2}\) ≈ 1,41"]),
            ("Signe de f", [("TABLEAU", [r"-\sqrt{2}", "0", r"\sqrt{2}"], [(r"\left(x^{4} - 2x^{2}\right)", "+0-0-0+"), ("f(x)", "+0-0-0+")])]),
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
        self.assertIsNone(parties.etapes_polynome([F(1), F(1), F(1)]))           # x² + x + 1 : rédaction de l'outil ED
        h = lire("ln(x)+1")
        self.assertEqual(parties.etapes_facteur(h, parties.zeros_facteur(h)[1]), [
            ([r"\ln(x) + 1 = 0"], None), ([r"\ln(x) = -1"], "on soustrait 1"), (["x = e^{-1}"], None)])

    def test_valeurs_approchees(self):
        """decisions.md §2 entre 10⁻³ et 1000, entier exact tel quel (question 2), R13 sous 10⁻³ et dès 10⁶ (question 1)."""
        sp = parties.charger_sympy()
        for v, attendu in ((sp.sqrt(6), "2,45"), (-sp.sqrt(6), "−2,45"), (3 * sp.exp(-6), "0,0074"), (sp.Integer(9), None),
                           (sp.Integer(-6), None), (sp.Rational(1, 3), "0,33"), (sp.Rational(1, 8), "0,13"),
                           (sp.exp(-10), r"\(4{,}540 \times 10^{-5}\)"), (sp.Rational(10 ** 10, 3), r"\(3{,}333 \times 10^{9}\)"),
                           (sp.Rational(10 ** 6 - 1, 10 ** 6 * 10 ** 4), r"\(1 \times 10^{-4}\)"), (sp.exp(8), None)):
            with self.subTest(v=v):
                self.assertEqual(parties.approchee(v, sp), attendu)

    def test_resoudre_place_la_partie_3_sous_son_intertitre(self):
        for entree in ("e^(-x^2)", "e^((x^2+x-2)/(6x-12))", "(x^2-6)e^(-2x)", "ln(x)/x"):
            with self.subTest(entree=entree):
                cartes = rec.resoudre(entree)["cartes"]
                t = [c["titre"] for c in cartes]
                self.assertEqual(cartes[t.index(rec.PARTIES[2]) + 1:t.index(rec.PARTIES[3])], cartes_zeros(entree))


# ---------- oracle : zéros, signe et f(0) affichés ----------
def nombre_affiche(t):
    """Valeur mpmath (50 chiffres) d'une écriture LaTeX de l'outil : entiers, fractions, racines, ln, e^{…}. Lecture écrite à la main
    (liste fermée de motifs), ni parseur de l'outil ni SymPy ; ValueError sinon."""
    s = t.replace(r"\left(", "(").replace(r"\right)", ")").replace(" ", "")
    for _ in range(6):
        s = re.sub(r"\\d?frac\{([^{}]*)\}\{([^{}]*)\}", r"((\1)/(\2))", s)
        s = re.sub(r"\\sqrt\{([^{}]*)\}", r"sqrt(\1)", s)
        s = re.sub(r"\\ln\(([^()]*)\)", r"log(\1)", s)
        s = re.sub(r"e\^\{([^{}]*)\}", r"exp(\1)", s)
    s = re.sub(r"(?<![a-z])e(?![a-z(])", "exp(1)", s)
    if not re.fullmatch(r"(?:[0-9+\-*/().]|exp|log|sqrt)*", s):
        raise ValueError(t)
    s = re.sub(r"(\d|\))(?=[a-z(])", r"\1*", s)
    s = re.sub(r"\d+", lambda m: f"mpf({m.group(0)})", s)                  # entiers en mpf : 1/6 calculé à 50 chiffres
    return eval(s, {"__builtins__": {}}, {"exp": mp.exp, "log": mp.log, "sqrt": mp.sqrt, "mpf": mp.mpf})


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
        zeros = list(re.finditer(r"\\\(x = ([^()]+?)\\\)(?: ≈ ([−0-9,]+))?( est rejeté)?", tout))
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
            m = re.search(r"\\\(f\(0\) = (.+?)\\\)(?: ≈ ([−0-9,]+))?\.$", ordo[0])
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
