"""Règle de style (15.10.2026) : un facteur de signe évident (exponentielle, racine d'une expression strictement positive,
carré ou puissance paire, polynôme sans zéro, constante) n'a PAS de ligne dans un tableau de signes ; il est justifié en
une phrase, puis « donc f'(x) est du signe de … ». La valeur interdite ou le zéro d'un facteur retiré garde sa colonne."""
import unittest

from moteurs import ensemble_def as ed
import derivee_variations as dv
import etude_complete as ec


def phrases(items):
    return [i["html"] for i in items if i.get("type") == "texte"]


class TestDerivee(unittest.TestCase):
    def test_racine_positive_et_carre_au_denominateur(self):
        r = dv.etudier("sqrt(4x^2+1)/(x+2)")
        labels = [l["label"] for l in r["table_signe"]["rows"]]
        self.assertEqual(labels, [r"\left(8x - 1\right)", "f'(x)", "f(x)"])
        self.assertEqual(r["table_signe"]["crit"], ["-2", r"\frac{1}{8}"])
        fp = next(l for l in r["table_signe"]["rows"] if l["label"] == "f'(x)")
        self.assertEqual(fp["cells"], ["-", "||", "-", "0", "+"])      # double barre en −2 : colonne conservée
        t = phrases(r["signe_etapes"])
        self.assertIn(r"\(\sqrt{4x^{2} + 1} > 0\) ; \(\left(x + 2\right)^{2} > 0\) pour \(x \neq -2\).", t)
        self.assertIn(r"Donc \(f'(x)\) est du signe de \(8x - 1\).", t)
        self.assertFalse(any("Signe de \\(\\sqrt{4x^{2} + 1}\\)" in p for p in t))

    def test_exponentielle_et_constante_negative(self):
        r = dv.etudier("x^2*e^(-x)")
        labels = [l["label"] for l in r["table_signe"]["rows"]]
        self.assertEqual(labels, ["x", r"\left(x - 2\right)", "f'(x)", "f(x)"])
        t = phrases(r["signe_etapes"])
        self.assertIn(r"\(e^{-x} > 0\) ; \(-1 < 0\).", t)
        self.assertTrue(any(p.startswith(r"Donc \(f'(x)\) est du signe contraire de") for p in t))

    def test_tous_les_facteurs_evidents(self):
        r = dv.etudier("e^(2x)")
        labels = [l["label"] for l in r["table_signe"]["rows"]]
        self.assertEqual(labels, ["f'(x)", "f(x)"])
        self.assertIn(r"Donc \(f'(x)\) est positif : il ne change jamais de signe.", phrases(r["signe_etapes"]))

    def test_facteur_qui_change_de_signe_garde_sa_ligne(self):
        r = dv.etudier("sqrt(x-2)*(x-3)")
        labels = [l["label"] for l in r["table_signe"]["rows"]]
        self.assertIn(r"\sqrt{x - 2}", " ".join(labels))               # √(x − 2) s'annule en 2 : pas évident

    def test_etude_complete_suit(self):
        r = ec.etudier("sqrt(4x^2+1)/(x+2)")
        labels = [l["label"] for l in r["derivee"]["table_signe"]["rows"]]
        self.assertEqual(labels, [r"\left(8x - 1\right)", "f'(x)", "f(x)"])


class TestEnsembleDefinition(unittest.TestCase):
    def tableaux(self, entree):
        r = ed.analyser(entree)
        return [i for c in r["conditions"] for i in c["etapes"] if i.get("type") == "tableau"]

    def test_carre_retire_mais_zero_conserve(self):
        (tab,) = self.tableaux("sqrt((x+2)^2*(x-1))")
        self.assertEqual(tab["crit"], ["-2", "1"])
        self.assertEqual([l["label"] for l in tab["rows"]][0], "x - 1")
        self.assertEqual(tab["rows"][-1]["cells"], ["-", "0", "-", "0", "+"])      # zéro de (x+2)² : colonne conservée
        self.assertEqual(len(tab["rows"]), 2)

    def test_polynome_toujours_positif_sans_tableau(self):
        self.assertEqual(self.tableaux("ln(x^2+1)"), [])
        self.assertEqual(self.tableaux("sqrt(4x^2+1)"), [])


if __name__ == "__main__":
    unittest.main()
