"""T16 — resoudre_ed.controle : la phrase du contrôle numérique (écrite en Python, plus en JS) est celle
que la page composait, mot pour mot ; les anciennes fonctions *_json restent exposées (pages en cache)."""
import json
import unittest

import moteurs  # noqa: F401  (chemins des moteurs)
import resoudre_ed as red


class TestControleED(unittest.TestCase):
    def test_accord(self):
        c = red.controle("ln(x-1)")
        self.assertTrue(c["ok"] and c["accord"])
        self.assertRegex(c["texte"], r"^✓ Contrôle numérique indépendant : f est bien définie aux \d+ points testés dans l'ED "
                                     r"et non définie aux \d+ points testés hors de l'ED\.$")

    def test_desaccord(self):
        faux = {"ok": True, "accord": False, "n_in": 3, "n_out": 4, "erreurs": ["1,5", "2"]}
        original, red.verifier = red.verifier, lambda e: faux
        try:
            c = red.controle("x")
        finally:
            red.verifier = original
        self.assertEqual(c, {"ok": True, "accord": False,
                             "texte": "⚠ Le contrôle numérique signale un désaccord près de x ≈ 1,5 ; 2. Vérifiez ce résultat à la main."})

    def test_ed_non_calculee(self):
        c = red.controle("ln(")
        self.assertFalse(c["ok"])

    def test_json_et_anciennes_fonctions(self):
        self.assertTrue(json.loads(red.controle_json("x+1"))["ok"])
        for nom in ("analyser_json", "verifier_json", "apercu_json", "resoudre_json"):
            self.assertTrue(callable(getattr(red, nom)), nom)


if __name__ == "__main__":
    unittest.main()
