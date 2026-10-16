"""Guide de rédaction (docs/guide-redaction.md, R7) : un tableau de signes a TOUJOURS une ligne par facteur du numérateur et du
dénominateur, puis la ligne du quotient — même pour un facteur évident (exponentielle, racine d'une expression positive, carré,
polynôme sans zéro) et même pour une constante (positive ou négative). Aucune phrase ne justifie le signe d'un facteur, aucun
« donc f'(x) est du signe de … », « Bilan » ni « Un produit est nul si et seulement si … » : avant le tableau, une seule ligne
(zéros et valeurs interdites). Remplace la règle du 15.10.2026 (commit 2bfcc1a : facteurs évidents hors du tableau)."""
import unittest

from moteurs import ensemble_def as ed
import derivee_variations as dv
import etude_complete as ec


def phrases(items):
    return [i["html"] for i in items if i.get("type") == "texte"]


INTERDITES = ["est du signe de", "il ne change jamais de signe", "Bilan", "Un produit est nul", "On étudie le signe", "Signe de",
              "On cherche d'abord", "> 0 pour"]


def sans_phrase_de_signe(test, textes):
    for p in textes:
        for interdit in INTERDITES:
            test.assertNotIn(interdit, p)


class TestDerivee(unittest.TestCase):
    def test_racine_positive_et_carre_au_denominateur(self):                # exemple 4 du guide
        r = dv.etudier("sqrt(4x^2+1)/(x+2)")
        labels = [l["label"] for l in r["table_signe"]["rows"]]
        self.assertEqual(labels, [r"\left(8x - 1\right)", r"\sqrt{4x^{2} + 1}",
                                  r"\left(x + 2\right)^{2}", "f'(x)", "f(x)"])
        self.assertEqual(r["table_signe"]["crit"], ["-2", r"\frac{1}{8}"])
        lignes = {l["label"]: l["cells"] for l in r["table_signe"]["rows"]}
        self.assertEqual(lignes["f'(x)"], ["-", "||", "-", "0", "+"])      # double barre en −2
        self.assertEqual(lignes[r"\sqrt{4x^{2} + 1}"], ["+", "||", "+", "+", "+"])
        self.assertEqual(lignes[r"\left(x + 2\right)^{2}"], ["+", "||", "+", "+", "+"])
        t = phrases(r["signe_etapes"])
        self.assertEqual(t, [r"\(f'(x) = \frac{8x - 1}{\sqrt{4x^{2} + 1}\,\left(x + 2\right)^{2}} = 0 \iff 8x - 1 = 0 \iff "
                             r"x = \frac{1}{8}\) ; valeur interdite : \(x = -2\)."])
        sans_phrase_de_signe(self, t)

    def test_exponentielle_et_constante_negative(self):
        r = dv.etudier("x^2*e^(-x)")
        labels = [l["label"] for l in r["table_signe"]["rows"]]
        self.assertEqual(labels, ["-1", "x", r"\left(x - 2\right)", "e^{-x}", "f'(x)", "f(x)"])
        lignes = {l["label"]: l["cells"] for l in r["table_signe"]["rows"]}
        self.assertEqual(lignes["-1"], ["-"] * 5)
        self.assertEqual(lignes["e^{-x}"], ["+"] * 5)
        sans_phrase_de_signe(self, phrases(r["signe_etapes"]))

    def test_constante_positive_a_sa_ligne(self):
        r = dv.etudier("x^3")                                               # f' = 3x²
        lignes = {l["label"]: l["cells"] for l in r["table_signe"]["rows"]}
        self.assertEqual(lignes["3"], ["+"] * 3)
        self.assertEqual(lignes["x^{2}"], ["+", "0", "+"])
        r = dv.etudier("x^2")                                               # f' = 2x : constante 2, facteur x
        self.assertEqual([l["label"] for l in r["table_signe"]["rows"]][:2], ["2", "x"])

    def test_tous_les_facteurs_evidents(self):
        r = dv.etudier("e^(2x)")
        labels = [l["label"] for l in r["table_signe"]["rows"]]
        self.assertEqual(labels, ["2", "e^{2x}", "f'(x)", "f(x)"])
        self.assertEqual(phrases(r["signe_etapes"]), [r"\(f'(x) = 2e^{2x}\) ne s'annule jamais."])

    def test_facteur_qui_change_de_signe_garde_sa_ligne(self):
        r = dv.etudier("sqrt(x-2)*(x-3)")
        labels = [l["label"] for l in r["table_signe"]["rows"]]
        self.assertIn(r"\sqrt{x - 2}", " ".join(labels))

    def test_aucune_phrase_de_signe_sur_tous_les_exemples(self):
        from cas import CAS_LIMITES, entrees_page
        for entree in dict.fromkeys(entrees_page("derivee-variations") + CAS_LIMITES["derivee-variations"]):
            r = dv.etudier(entree)
            if r.get("signe_resolu"):
                with self.subTest(f=entree):
                    sans_phrase_de_signe(self, phrases(r["signe_etapes"]))
                    labels = [l["label"] for l in r["table_signe"]["rows"]]
                    self.assertEqual(labels[-2:], ["f'(x)", "f(x)"])

    def test_etude_complete_suit(self):
        r = ec.etudier("sqrt(4x^2+1)/(x+2)")
        labels = [l["label"] for l in r["derivee"]["table_signe"]["rows"]]
        self.assertEqual(labels, [r"\left(8x - 1\right)", r"\sqrt{4x^{2} + 1}",
                                  r"\left(x + 2\right)^{2}", "f'(x)", "f(x)"])


class TestEnsembleDefinition(unittest.TestCase):
    def conditions(self, entree):
        return ed.analyser(entree)["conditions"]

    def tableaux(self, entree):
        return [i for c in self.conditions(entree) for i in c["etapes"] if i.get("type") == "tableau"]

    def test_carre_garde_sa_ligne(self):
        (tab,) = self.tableaux("sqrt((x+2)^2*(x-1))")
        self.assertEqual(tab["crit"], ["-2", "1"])
        self.assertEqual([l["label"] for l in tab["rows"]], ["x - 1", r"\left(x + 2\right)^{2}", "x^{3} + 3x^{2} - 4"])
        self.assertEqual(tab["rows"][1]["cells"], ["+", "0", "+", "+", "+"])
        self.assertEqual(tab["rows"][-1]["cells"], ["-", "0", "-", "0", "+"])      # zéro du carré : colonne conservée

    def test_constantes_positive_et_negative_ont_leur_ligne(self):
        (tab,) = self.tableaux("ln(2x^2-8)")
        self.assertEqual([l["label"] for l in tab["rows"]], ["2", "x + 2", "x - 2", "2x^{2} - 8"])
        self.assertEqual(tab["rows"][0]["cells"], ["+"] * 5)
        (tab,) = self.tableaux("sqrt(4-x^2)")
        self.assertEqual([l["label"] for l in tab["rows"]], ["-1", "x + 2", "x - 2", "-x^{2} + 4"])
        self.assertEqual(tab["rows"][0]["cells"], ["-"] * 5)

    def test_polynome_toujours_positif_sans_tableau(self):                  # aucune colonne : rien à lire
        self.assertEqual(self.tableaux("ln(x^2+1)"), [])
        self.assertEqual(self.tableaux("sqrt(4x^2+1)"), [])

    def test_exemple_7_du_guide(self):
        (tab,) = self.tableaux("ln(x+1)/sqrt(4-x^2)")
        self.assertEqual([l["label"] for l in tab["rows"]], ["-1", "x + 2", "x - 2", "-x^{2} + 4"])
        self.assertEqual(self.conditions("ln(x+1)/sqrt(4-x^2)")[0]["etapes"][1]["html"], r"\(x + 1 > 0 \iff x > -1\).")

    def test_aucune_phrase_de_signe_sur_tous_les_exemples(self):
        from cas import CAS_LIMITES, entrees_page
        for entree in dict.fromkeys(entrees_page("ensemble-definition") + CAS_LIMITES["ensemble-definition"]):
            r = ed.analyser(entree)
            if not r.get("ok"):
                continue
            with self.subTest(f=entree):
                # le titre « Signe de ln(x + 2) » reste devant l'étude d'un facteur qui n'est ni évident ni affine (étape délicate)
                sans_phrase_de_signe(self, [i["html"] for c in r["conditions"] for i in c["etapes"]
                                            if i.get("type") == "texte" and not i["html"].startswith("<b>Signe de")])
                for c in r["conditions"]:
                    for i in c["etapes"]:
                        if i.get("type") == "tableau":
                            self.assertEqual(i["rows"][-1].get("final"), True)


if __name__ == "__main__":
    unittest.main()
