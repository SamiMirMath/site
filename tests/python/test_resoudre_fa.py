"""T12 — factorisation/resoudre_fa.py : sortie du format commun, sans rien perdre de l'ancienne."""
import json
import unittest

import moteurs  # noqa: F401  (chemins des moteurs)
import factorisation as fa
import resoudre_fa as rfa
from aides_sortie import manquantes, valide, blocs_de_type
from cas import entrees_factorisation


class TestResoudreFactorisation(unittest.TestCase):
    def test_schema_et_rien_de_perdu(self):
        for entree in entrees_factorisation():
            with self.subTest(entree=entree):
                s = rfa.resoudre(entree)
                valide(self, s)
                self.assertEqual(manquantes(fa.factoriser_expr(entree), s, ("detail", "ok", "secours", "erreur")), [])

    def test_carte_comme_la_page(self):
        s = rfa.resoudre("x^2+5x-14")
        self.assertTrue(s["ok"])
        self.assertEqual([(c["titre"], c["style"], c["badge"]) for c in s["cartes"]],
                         [("Étape 1", "normal", "Somme-Produit"), ("Factorisation", "final", "Somme-Produit")])
        c = s["cartes"][-1]
        self.assertEqual(c["blocs"][0]["type"], "formule")
        self.assertEqual(c["blocs"][-1]["type"], "resultat")
        self.assertTrue(all(b["style"] == "etape" for k in s["cartes"] for b in k["blocs"] if b["type"] == "texte"))

    def test_fa04_une_carte_par_application(self):
        """FA-04 : cartes = groupes consécutifs de même méthode + le bilan ; aucune étape perdue ni déplacée."""
        for entree in entrees_factorisation():
            with self.subTest(entree=entree):
                r, ctx = fa._factoriser(entree)
                s = rfa.resoudre(entree)
                valide(self, s)
                if not r["ok"]:
                    self.assertFalse(s["ok"])
                    continue
                *etapes, bilan = s["cartes"]
                self.assertEqual(bilan["titre"], "Factorisation")
                self.assertEqual(bilan["badge"], r["methode"])
                badges = [c["badge"] for c in etapes]
                self.assertTrue(all(x != y for x, y in zip(badges, badges[1:])), badges)
                self.assertEqual(set(badges), set(ctx.groupes) - {None})
                dites = [b["html"] for c in etapes for b in c["blocs"]] + [b["html"] for b in bilan["blocs"] if b["type"] == "texte"]
                self.assertEqual(dites, [e["html"] for e in r["etapes"]])     # aucune étape perdue, dans l'ordre

    def test_fa04_changement_de_variable(self):
        s = rfa.resoudre("x^4-13x^2+36")
        self.assertEqual([c["badge"] for c in s["cartes"][:-1]],
                         ["Changement de variable", "Somme-Produit", "Changement de variable", "Différence de carrés"])
        self.assertEqual(len(s["cartes"][3]["blocs"]), 2)          # x²−4 et x²−9 : une seule carte
        self.assertIn("On revient à", s["cartes"][2]["blocs"][0]["html"])

    def test_fa04_etape_sans_methode_suit_la_carte_precedente(self):
        s = rfa.resoudre("x^3-8y^3")
        self.assertEqual([c["badge"] for c in s["cartes"]], ["Différence de cubes", "Différence de cubes"])
        self.assertIn("ne se factorise pas davantage", s["cartes"][0]["blocs"][-1]["html"])
        s = rfa.resoudre("x^4-1")
        self.assertEqual([c["badge"] for c in s["cartes"][:-1]], ["Différence de carrés", "Non factorisable dans ℝ (Δ < 0)"])

    def test_sans_methode_une_seule_carte(self):
        for entree in ("x+1", "(x+1)(x-2)", "7"):
            with self.subTest(entree=entree):
                self.assertEqual(len(rfa.resoudre(entree)["cartes"]), 1)

    def test_fa05_difference_de_carres_sur_les_termes_ecrits(self):
        r = fa.factoriser_expr("(x+1)^2-(x-1)^2")
        self.assertEqual((r["methode"], r["resultat_tex"], r["secours"]), ("Différence de carrés", "4x", False))
        self.assertEqual(fa.factoriser_expr("(x+2)^2-(x-2)^2")["resultat_tex"], "8x")

    def test_zero_evident_seulement_entier(self):
        """Pas de zéro p/q : un trinôme a ≠ 1 passe par le discriminant ; au-delà, on teste les diviseurs du terme constant."""
        for entree in ("6x^2-7x-3", "3x^2+2x-1", "2x^2+5x+2"):
            with self.subTest(entree=entree):
                r = fa.factoriser_expr(entree)
                self.assertNotIn("Zéro évident", r["methode"])
                self.assertNotIn("Racine évidente", r["methode"])
        r = fa.factoriser_expr("x^3-2x^2-5x+6")
        self.assertTrue(r["methode"].startswith("Racine évidente"))

    def test_erreurs_en_francais(self):
        for entree, debut in (("sqrt(x)", "Pas de fonction"), ("x/y", "La division"), ("x^2-1'000", "Caractère")):
            with self.subTest(entree=entree):
                s = rfa.resoudre(entree)
                valide(self, s)
                self.assertFalse(s["ok"])
                self.assertTrue(s["erreur"].startswith(debut))
                self.assertNotIn("Traceback", json.dumps(s))

    def test_json(self):
        self.assertEqual(json.loads(rfa.resoudre_json("x^2-1")), rfa.resoudre("x^2-1"))


if __name__ == "__main__":
    unittest.main()
