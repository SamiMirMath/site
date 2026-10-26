"""T33 (étape 8) — Exercices au hasard de l'outil « Exponentielles et logarithmes » (pool C, EL-13) : `exercice(niveau, graine)` est déterministe,
produit un gabarit du niveau, n'a jamais d'exposant de degré supérieur à 2, et le moteur le résout (oracle mpmath, EL-02) pour 500 graines."""
import json
import re
import unittest

import moteurs  # noqa: F401  (chemins des moteurs)
import exp_log as el
import resoudre_el as rel
import sortie as so
from exp_log import Eq
from test_exp_log import vrai, evaluer

GRAINES = range(500)
GABARITS = {
    "facile": [r"\d+\^(x|\(\d?x([+-]\d)?\))=\d+", r"log\(x\)=-?\d", r"ln\(x\)=-?\d", r"log_\d\(x\)=-?\d"],
    "moyen": [r"\d+\^(x|\(\d?x([+-]\d)?\))=\d+", r"\d\*\d+\^(x|\(\d?x([+-]\d)?\))=\d+", r"log\(\d-x\)=\d", r"log\(\dx\+\d\)=\d"],
    "logarithme": [r"\d+\^\(\d?x\)=-\d+", r"\d+\*e\^\(-?0,\d+x\)=\d+", r"\d+\^(x|\(\d?x([+-]\d)?\))=\d+", r"\d\*\d+\^(x|\(\d?x([+-]\d)?\))=\d+",
                   r"e\^(x|\(\d?x([+-]\d)?\))=\d+"],
    "difficile": [r"\d+\^\(x[+-]\d\)=\d+\^(x|\(\dx\))", r"\d+\^\(x\^2\)\*\d+\^x=\d+", r"log_x\(\d+\)=\d", r"log\(log\(x\)\)=\d"],
}


def corrige(expr):
    s = el.analyser_saisie(expr)
    return s, el.corriger_equation(s.g, s.d, s.inconnue)


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
                        self.assertTrue(vrai(Eq(s.g, s.d), evaluer(n)), (expr, el.tex(n)))
                    if "x^2" in expr:                                           # racines entières (jamais de discriminant non carré)
                        self.assertTrue(all(el._const(n) is not None and el._const(n).denominator == 1 for n in r["solutions"]), expr)

    def test_le_niveau_logarithme_n_est_jamais_une_meme_base(self):
        for graine in GRAINES:
            expr = el.exercice("logarithme", graine)["expr"]
            s, _ = corrige(expr)
            self.assertIsNone(el.meme_base(s.g, s.d, s.inconnue), expr)

    def test_un_exercice_sur_dix_du_niveau_logarithme_n_a_pas_de_solution(self):
        vides = sum(1 for g in range(2000) if el.exercice("logarithme", g)["expr"].count("=-") == 1)
        self.assertTrue(120 <= vides <= 280, vides)                              # 10 % de 2000

    def test_les_enonces_s_affichent(self):
        for niveau in el.NIVEAUX:
            for graine in range(100):
                expr = el.exercice(niveau, graine)["expr"]
                self.assertTrue(el.apercu(expr)["ok"], expr)

    def test_niveau_inconnu(self):
        self.assertFalse(el.exercice("tresDifficile", 1)["ok"])
        self.assertFalse(json.loads(rel.exercice_json("n'importe quoi"))["ok"])

    def test_exercice_json_est_du_json_strict_au_hasard(self):
        for niveau in el.NIVEAUX:
            for _ in range(30):
                r = json.loads(rel.exercice_json(niveau))
                self.assertTrue(r["ok"] and r["niveau"] == niveau)
                self.assertTrue(rel.resoudre(r["expr"])["ok"], r["expr"])
                self.assertEqual(so.valider(rel.resoudre(r["expr"])), [])


if __name__ == "__main__":
    unittest.main()
