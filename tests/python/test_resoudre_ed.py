"""T12 — ensemble-definition/resoudre_ed.py : sortie du format commun, sans rien perdre de l'ancienne,
et textes que la page composait en JS (en-tête, « Condition non résolue », valeurs ≈)."""
import json
import unittest

import moteurs  # noqa: F401  (chemins des moteurs)
import ensemble_def as ed
import resoudre_ed as red
from aides_sortie import manquantes, valide, blocs_de_type
from cas import entrees_page, CAS_LIMITES

ENTREES = list(dict.fromkeys(entrees_page("ensemble-definition") + CAS_LIMITES["ensemble-definition"]))
TECHNIQUE = ("detail", "ok", "genre", "source_tex", "E_tex", "besoin_sympy")


class TestResoudreED(unittest.TestCase):
    def test_schema_et_rien_de_perdu(self):
        for entree in ENTREES:
            with self.subTest(entree=entree):
                s = red.resoudre(entree)
                valide(self, s)
                self.assertEqual(manquantes(ed.analyser(entree), s, TECHNIQUE), [])

    def test_ordre_et_nombre_de_cartes(self):
        for entree in ENTREES:
            ancien = ed.analyser(entree)
            if ancien["ok"]:
                with self.subTest(entree=entree):
                    s = red.resoudre(entree)
                    self.assertEqual(len(s["cartes"]), len(ancien["conditions"]) + 1)
                    self.assertEqual([c["badge"] for c in s["cartes"][:-1]], [c["titre"] for c in ancien["conditions"]])
                    self.assertEqual(s["cartes"][-1]["style"], "final")
                    self.assertEqual(s["besoin_sympy"], ancien["besoin_sympy"])

    def test_entete(self):
        e = red.resoudre("ln(x^2-4x)/(x-5)")["entete"]
        self.assertEqual(e["blocs"][1]["html"], "2 conditions d'existence : logarithme, dénominateur.")
        e = red.resoudre("ln(x-1)")["entete"]
        self.assertEqual(e["blocs"][1]["html"], "1 condition d'existence : logarithme.")
        e = red.resoudre("x^2+1")["entete"]
        self.assertEqual(e["blocs"][1]["html"], "Ni logarithme, ni dénominateur, ni racine : aucune condition.")

    def test_carte_finale(self):
        self.assertEqual(red.resoudre("x^2+1")["cartes"][-1]["blocs"][0]["tex"], "ED = \\mathbb{R}")
        ancien = ed.analyser("ln(x^2-4x)/(x-5)")
        fin = red.resoudre("ln(x^2-4x)/(x-5)")["cartes"][-1]["blocs"][0]["tex"]
        self.assertEqual(fin, "ED = " + ancien["inter_tex"] + " = " + ancien["ED_tex"])

    def test_condition_non_resolue_et_detail(self):
        from unittest import mock
        with mock.patch.object(ed, "resoudre_condition", side_effect=ValueError("boum")):
            s = red.resoudre("ln(x)")
        valide(self, s)
        c = s["cartes"][0]
        self.assertEqual(c["blocs"][-1], {"type": "erreur", "texte": "Condition non résolue."})
        self.assertEqual(c["detail"], "ValueError : boum")
        self.assertEqual(s["cartes"][-1]["blocs"][0]["texte"], "Une condition n'a pas pu être résolue : l'ED n'est pas calculé.")

    def test_valeurs_numeriques(self):
        trouve = False
        for entree in ENTREES:
            ancien = ed.analyser(entree)
            if ancien["ok"] and ancien.get("complet") and "approx" in ancien["ED_tex"]:
                trouve = True
                textes = [b["html"] for b in red.resoudre(entree)["cartes"][-1]["blocs"] if b["type"] == "texte"]
                self.assertEqual(textes, ["Les valeurs précédées de ≈ ont été obtenues numériquement."])
        self.assertTrue(trouve, "aucun exemple à valeurs numériques dans les cas")

    def test_tableaux_conservent_leur_format(self):
        for entree in ENTREES:
            ancien = ed.analyser(entree)
            if ancien["ok"]:
                anciens = [it for c in ancien["conditions"] for it in c["etapes"] if it["type"] == "tableau"]
                nouveaux = [dict(b) for b in blocs_de_type(red.resoudre(entree), "tableau")]
                self.assertEqual(nouveaux, anciens, entree)

    def test_erreurs_en_francais(self):
        for entree in ("", "ln(", "x+*2"):
            with self.subTest(entree=entree):
                s = red.resoudre(entree)
                valide(self, s)
                self.assertFalse(s["ok"])
                self.assertNotIn("Traceback", json.dumps(s))

    def test_json(self):
        self.assertEqual(json.loads(red.resoudre_json("ln(x-1)")), red.resoudre("ln(x-1)"))


if __name__ == "__main__":
    unittest.main()
