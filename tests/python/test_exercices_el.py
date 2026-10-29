"""T33 (étape 8) — Exercices au hasard de l'outil « Exponentielles et logarithmes » (pool C, EL-13) : `exercice(niveau, graine)` est déterministe,
produit un gabarit du niveau, n'a jamais d'exposant de degré supérieur à 2, et le moteur le résout (oracle mpmath, EL-02) pour 500 graines."""
import json
import random
import re
import unittest
from fractions import Fraction as F

import mpmath as mp

import moteurs  # noqa: F401  (chemins des moteurs)
import exp_log as el
import resoudre_el as rel
import sortie as so
from exp_log import Eq
from test_exp_log import vrai, evaluer
from test_applications_el import substituer, duree_de_reference, duree_du_texte, OR

GRAINES = range(500)
PARAMETRE = r"(?:C|Q|C0|V0|C_0|V_0)"
HAUSSE = r"(?:\(1\+[\d,]+(?:/100|%)\)|\(1\+0,\d+\)|1,\d+)"            # 1 + t/100 écrit de quatre façons
BAISSE = r"(?:\(1-[\d,]+(?:/100|%)\)|\(1-0,\d+\)|0,\d+)"
APPLICATIONS = [rf"[23]{PARAMETRE}={PARAMETRE}\*{HAUSSE}\^n", rf"{PARAMETRE}\*{HAUSSE}\^n=[23]{PARAMETRE}",
                rf"{PARAMETRE}/[24]={PARAMETRE}\*{BAISSE}\^n", rf"{PARAMETRE}\*{BAISSE}\^n={PARAMETRE}/[24]",
                rf"\d+\*{HAUSSE}\^n=\d+"]
GABARITS = {
    "facile": [r"\d+\^(x|\(\d?x([+-]\d)?\))=\d+", r"log\(x\)=-?\d", r"ln\(x\)=-?\d", r"log_\d\(x\)=-?\d"],
    "moyen": [r"\d+\^(x|\(\d?x([+-]\d)?\))=\d+", r"\d\*\d+\^(x|\(\d?x([+-]\d)?\))=\d+", r"log\(\d-x\)=\d", r"log\(\dx\+\d\)=\d"],
    "logarithme": [r"\d+\^\(\d?x\)=-\d+", r"\d+\*e\^\(-?0,\d+x\)=\d+", r"\d+\^(x|\(\d?x([+-]\d)?\))=\d+", r"\d\*\d+\^(x|\(\d?x([+-]\d)?\))=\d+",
                   r"e\^(x|\(\d?x([+-]\d)?\))=\d+"] + APPLICATIONS,
    "difficile": [r"\d+\^\(x[+-]\d\)=\d+\^(x|\(\dx\))", r"\d+\^\(x\^2\)\*\d+\^x=\d+", r"log_x\(\d+\)=\d", r"log\(log\(x\)\)=\d"],
}


def corrige(expr):
    s = el.analyser_saisie(expr)
    return s, el.corriger_equation(s.g, s.d, s.inconnue, parametres=s.parametres)


class TestExercices(unittest.TestCase):
    def test_deterministe(self):
        for niveau in el.NIVEAUX:
            for graine in range(50):
                self.assertEqual(el.exercice(niveau, graine), el.exercice(niveau, graine))
            self.assertGreater(len({el.exercice(niveau, g)["expr"] for g in range(50)}), 10, niveau)

    def test_gabarit_du_niveau(self):
        for niveau, motifs in GABARITS.items():
            for graine in GRAINES:
                e = el.exercice(niveau, graine)
                self.assertTrue(e["ok"] and e["niveau"] == niveau)
                with self.subTest(niveau=niveau, expr=e["expr"]):
                    self.assertTrue(any(re.fullmatch(m, e["expr"]) for m in motifs), e["expr"])

    def test_jamais_d_exposant_de_degre_3_ou_plus(self):
        for niveau in el.NIVEAUX:
            for graine in GRAINES:
                expr = el.exercice(niveau, graine)["expr"]
                with self.subTest(expr=expr):
                    self.assertIsNone(re.search(r"x\^\(?[3-9]", expr))
                    self.assertIsNone(re.search(r"x\^\(", expr))                  # x² s'écrit x^2 : jamais d'exposant composé en x
                    if "x^2" in expr:
                        self.assertEqual(niveau, "difficile")

    def test_le_moteur_resout_et_l_oracle_confirme(self):
        for niveau in el.NIVEAUX:
            for graine in GRAINES:
                expr = el.exercice(niveau, graine)["expr"]
                with self.subTest(niveau=niveau, expr=expr):
                    s, r = corrige(expr)
                    self.assertIsNotNone(r, expr)
                    if r["solutions"] == []:
                        self.assertRegex(expr, r"=-\d+$")                       # seul le second membre négatif donne S = ∅
                        continue
                    self.assertTrue(r["solutions"], expr)
                    for n in r["solutions"]:
                        g, d = s.g, s.d
                        for p in s.parametres:                                   # un paramètre vaut ce qu'on veut : l'énoncé reste vérifié
                            g, d = substituer(g, p, 7), substituer(d, p, 7)
                        self.assertTrue(vrai(Eq(g, d), evaluer(n)), (expr, el.tex(n)))
                    if "x^2" in expr:                                           # racines entières (jamais de discriminant non carré)
                        self.assertTrue(all(el._valeur_rationnelle(n) is not None and el._valeur_rationnelle(n).denominator == 1 for n in r["solutions"]), expr)

    def test_les_deux_methodes_donnent_le_meme_S(self):
        """Sélecteur (27.10.2026) : « Même base / définition » et « Logarithmes » ont le même ensemble solution ; quand la méthode A ne s'applique pas,
        elle le dit (message) au lieu de donner des solutions ; les équations logarithmiques n'ont pas de variantes."""
        for niveau in el.NIVEAUX:
            for graine in GRAINES:
                expr = el.exercice(niveau, graine)["expr"]
                with self.subTest(niveau=niveau, expr=expr):
                    s = el.analyser_saisie(expr)
                    v = el.variantes_equation(s.g, s.d, s.inconnue, s.parametres)
                    if expr.startswith(("log", "ln")):
                        self.assertIsNone(v, expr)
                        continue
                    a, b = v[el.METHODE_MEME_BASE], v[el.METHODE_LOGARITHMES]
                    self.assertIsNone(b.get("message"), expr)
                    if a.get("message"):
                        self.assertEqual(a["solutions"], [])
                        self.assertRegex(a["message"].texte(), r" n'est pas une puissance de .* : il faut les logarithmes\.$")
                        continue
                    valeurs = lambda r: None if r["solutions"] is None else sorted(el.valeur(n) for n in r["solutions"])
                    va, vb = valeurs(a), valeurs(b)
                    self.assertEqual(len(va), len(vb), expr)
                    for x, y in zip(va, vb):
                        self.assertAlmostEqual(x, y, places=9, msg=expr)

    def test_le_niveau_logarithme_n_est_jamais_une_meme_base(self):
        for graine in GRAINES:
            expr = el.exercice("logarithme", graine)["expr"]
            s = el.analyser_saisie(expr)
            g, d, _ = el.preparer_application(s.g, s.d, s.inconnue, s.parametres)
            self.assertIsNone(el.meme_base(g, d, s.inconnue), expr)

    def test_un_exercice_sur_dix_du_niveau_logarithme_n_a_pas_de_solution(self):
        vides = sum(1 for g in range(2000) if el.exercice("logarithme", g)["expr"].count("=-") == 1)
        self.assertTrue(120 <= vides <= 280, vides)                              # 10 % de 2000

    def test_un_tiers_du_niveau_logarithme_est_un_probleme_d_application(self):
        n = sum(1 for g in range(2000) if re.search(r"\^n", el.exercice("logarithme", g)["expr"]))
        self.assertTrue(480 <= n <= 720, n)                                      # 30 % de 2000
        for niveau in ("facile", "moyen", "difficile"):
            self.assertFalse(any("^n" in el.exercice(niveau, g)["expr"] for g in range(300)), niveau)

    def test_les_enonces_s_affichent(self):
        for niveau in el.NIVEAUX:
            for graine in range(100):
                expr = el.exercice(niveau, graine)["expr"]
                self.assertTrue(el.apercu(expr)["ok"], expr)

    def test_niveau_inconnu(self):
        self.assertFalse(el.exercice("tresDifficile", 1)["ok"])
        self.assertFalse(json.loads(rel.exercice_json("n'importe quoi"))["ok"])

    def test_exercice_json_est_du_json_strict_au_hasard(self):
        random.seed(2026_10_29)                   # exercice_json tire sa graine dans le générateur global : tirages reproductibles
        for niveau in el.NIVEAUX:
            for _ in range(30):
                r = json.loads(rel.exercice_json(niveau))
                self.assertTrue(r["ok"] and r["niveau"] == niveau)
                self.assertTrue(rel.resoudre(r["expr"])["ok"], r["expr"])
                self.assertEqual(so.valider(rel.resoudre(r["expr"])), [])


def base_et_rapport(g, d):
    """(b, r) de l'équation préparée k·b^n = c (ou b^n = c) : la base b (Fraction) et r = c/k, lus sur l'arbre."""
    membre, autre = (g, d) if el.variables(g) else (d, g)
    coefficient = F(1)
    if isinstance(membre, el.Op):                                                  # k · b^n
        pw, k = (membre.b, membre.a) if isinstance(membre.b, el.Pow) else (membre.a, membre.b)
        coefficient = el._const(k)
    else:
        pw = membre
    return pw.a.val, el._const(autre) / coefficient


class TestApplicationsDuPool(unittest.TestCase):
    """EL-25 : les exercices d'application du niveau « logarithme » : taux réalistes, solution exacte, durée en années, mois et jours exacte."""

    def exercices(self):
        vus = []
        for graine in range(1500):
            expr = el.exercice("logarithme", graine)["expr"]
            if "^n" in expr:
                vus.append(expr)
        return vus

    def test_taux_et_facteurs_realistes(self):
        formes = set()
        for expr in self.exercices():
            s = el.analyser_saisie(expr)
            g2, d2, _ = el.preparer_application(s.g, s.d, s.inconnue, s.parametres)
            b, rapport = base_et_rapport(g2, d2)                                 # après préparation : k · b^n = c, sans paramètre ni taux écrit
            if s.parametres:
                if b > 1:
                    self.assertIn(rapport, (2, 3), expr)
                    self.assertTrue(F(5, 1000) <= b - 1 <= F(8, 100), (expr, b))
                    formes.add("croissance")
                else:
                    self.assertIn(rapport, (F(1, 2), F(1, 4)), expr)
                    self.assertTrue(F(5, 100) <= 1 - b <= F(25, 100), (expr, b))
                    formes.add("depreciation")
            else:
                self.assertTrue(F(6, 5) <= rapport <= 3, expr)
                self.assertTrue(F(5, 1000) <= b - 1 <= F(8, 100), (expr, b))
                formes.add("sans_parametre")
        self.assertEqual(formes, {"croissance", "depreciation", "sans_parametre"})

    def test_toutes_les_ecritures_de_la_base_et_tous_les_parametres_apparaissent(self):
        exercices = self.exercices()
        for motif in [r"\(1[+-][\d,]+/100\)", r"\(1[+-][\d,]+%\)", r"\(1[+-]0,\d+\)", r"\^n", r"\*[01],\d+\^n"]:
            self.assertTrue(any(re.search(motif, e) for e in exercices), motif)
        for p in ["C", "Q", "C0", "V0", "C_0", "V_0"]:
            self.assertTrue(any(re.search(rf"(?<![A-Za-z_]){p}(?![0-9_])", e) for e in exercices), p)

    def test_duree_exacte_et_phrase(self):
        """La durée du moteur est celle de l'oracle (mpmath, 50 chiffres) recalculée à partir de l'énoncé, pas du moteur."""
        for expr in self.exercices():
            with self.subTest(expr=expr):
                s = el.analyser_saisie(expr)
                g, d, _ = el.preparer_application(s.g, s.d, s.inconnue, s.parametres)
                b, rapport = base_et_rapport(g, d)
                x = OR.log(OR.mpf(rapport.numerator) / rapport.denominator) / OR.log(OR.mpf(b.numerator) / b.denominator)
                self.assertGreater(x, 0)
                r = el.corriger_equation(s.g, s.d, s.inconnue, parametres=s.parametres)
                inter = el.interpretation(r)
                self.assertEqual(inter["duree"], duree_de_reference(x))
                self.assertEqual(duree_du_texte(inter["conclusion"]), duree_de_reference(x))
                self.assertTrue(el.suggere_interpretation(s))

    def test_la_sortie_a_la_case_pre_cochee(self):
        for expr in self.exercices()[:60]:
            o = rel.resoudre(expr)["option"]
            self.assertTrue(o["cochee"], expr)


if __name__ == "__main__":
    unittest.main()
