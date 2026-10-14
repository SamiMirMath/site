"""Tableau de signes de l'outil Ensemble de définition : même présentation que l'outil Dérivée
(double barre sur toute la colonne d'une valeur interdite, zones hors du domaine hachurées sur
toutes les lignes, pas de colonne au milieu d'une zone hachurée)."""
import unittest

from moteurs import ensemble_def as ed


def tableaux(entree):
    res = ed.analyser(entree)
    return [e for c in res.get("conditions", []) for e in c["etapes"] if e.get("type") == "tableau"], res


class TestTableauED(unittest.TestCase):
    def test_denominateur_barre_sur_toute_la_colonne(self):
        (t,), res = tableaux("ln((x-1)/(x+2))")
        self.assertEqual(t["crit"], ["-2", "1"])
        for ligne in t["rows"]:
            self.assertEqual(ligne["cells"][1], "||", ligne["label"])          # colonne −2 : valeur interdite
        self.assertEqual(t["rows"][-1]["cells"], ["+", "||", "-", "0", "+"])
        self.assertEqual(res["ED_tex"], r"\left]-\infty \,;\, -2\right[ \cup \left]1 \,;\, +\infty\right[")

    def test_zone_hors_du_domaine_hachuree_sur_toutes_les_lignes(self):
        (t,), _ = tableaux("sqrt((x-1)*ln(x))")
        for ligne in t["rows"]:
            self.assertEqual(ligne["cells"][0], "x", ligne["label"])           # ]−∞ ; 0[ hachurée partout
            self.assertEqual(ligne["cells"][1], "||", ligne["label"])          # 0 : borne exclue, barre partout

    def test_pas_de_colonne_au_milieu_d_une_zone_hachuree(self):
        for entree in ("sqrt(x*ln(x+2))", "sqrt(ln(x)-x+2)", "sqrt((x-1)*ln(x))", "ln((x-1)/(x+2))"):
            (t,), _ = tableaux(entree)
            fin = t["rows"][-1]["cells"]
            for j in range(1, len(fin) - 1, 2):
                with self.subTest(f=entree, colonne=t["crit"][j // 2]):
                    self.assertFalse(fin[j - 1] == "x" and fin[j + 1] == "x" and fin[j] in ("x", "||"), fin)

    def test_toutes_les_lignes_ont_la_meme_longueur(self):
        for entree in ("sqrt(x*ln(x+2))", "sqrt(ln(x)-x+2)", "ln((x-1)/(x+2))", "sqrt(x*ln(x+2)+x)"):
            (t,), _ = tableaux(entree)
            self.assertEqual({len(w["cells"]) for w in t["rows"]}, {2 * len(t["crit"]) + 1})

    def test_valeur_interdite_barree_sur_toutes_les_lignes_des_exemples(self):
        from cas import CAS_LIMITES, entrees_page
        from generateurs import fonctions
        for entree in list(dict.fromkeys(entrees_page("ensemble-definition") + CAS_LIMITES["ensemble-definition"])) + fonctions(200, graine=11):
            ts, _ = tableaux(entree)
            for t in ts:
                fin = t["rows"][-1]["cells"]
                for j in range(1, len(fin), 2):
                    if fin[j] == "||":
                        with self.subTest(f=entree, colonne=t["crit"][j // 2]):
                            self.assertTrue(all(w["cells"][j] == "||" for w in t["rows"]), [w["cells"][j] for w in t["rows"]])
                    elif fin[j] == "x":
                        self.assertTrue(all(w["cells"][j] == "||" for w in t["rows"]))


if __name__ == "__main__":
    unittest.main()
