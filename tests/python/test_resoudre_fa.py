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
        self.assertEqual(len(s["cartes"]), 1)
        c = s["cartes"][0]
        self.assertEqual((c["titre"], c["style"], c["badge"]), ("Factorisation", "final", "Somme-Produit"))
        self.assertEqual(c["blocs"][0]["type"], "formule")
        self.assertEqual(c["blocs"][-1]["type"], "resultat")
        self.assertTrue(all(b["style"] == "etape" for b in c["blocs"] if b["type"] == "texte"))

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
