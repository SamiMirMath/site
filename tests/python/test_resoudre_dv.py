"""T12 — derivee-variations/resoudre_dv.py : sortie du format commun, sans rien perdre de l'ancienne,
et textes que la page composait en JS (extrema, « Aucun extremum… », cartes d'erreur)."""
import json
import unittest
from unittest import mock

import moteurs  # noqa: F401  (chemins des moteurs)
import derivee_variations as dv
import resoudre_dv as rdv
from aides_sortie import manquantes, valide, blocs_de_type
from cas import entrees_page, CAS_LIMITES

ENTREES = list(dict.fromkeys(entrees_page("derivee-variations") + CAS_LIMITES["derivee-variations"]))
TECHNIQUE = ("detail", "ok", "deriv_detail", "signe_detail", "domaine_etude_tex", "ed_deriv_tex")


class TestResoudreDV(unittest.TestCase):
    def test_schema_et_rien_de_perdu(self):
        for entree in ENTREES:
            with self.subTest(entree=entree):
                s = rdv.resoudre(entree)
                valide(self, s)
                self.assertEqual(manquantes(dv.etudier(entree), s, TECHNIQUE), [])

    def test_ordre_et_nombre_de_cartes(self):
        for entree in ENTREES:
            ancien = dv.etudier(entree)
            if not ancien["ok"]:
                continue
            with self.subTest(entree=entree):
                titres = [c["titre"] for c in rdv.resoudre(entree)["cartes"]]
                attendu = ["Fonction", "Dérivée"] + (["Signe de f' et variations"] if ancien["deriv_resolu"] else [])
                self.assertEqual(titres, attendu)

    def test_extrema_comme_la_page(self):
        s = rdv.resoudre("ln(x)/x")
        liste = blocs_de_type(s, "liste")[0]
        self.assertEqual(liste["style"], "extrema")
        self.assertEqual(liste["items"], ["maximum local en \\(x=e\\) : \\(f(e)=e^{-1}\\)"])

    def test_aucun_extremum_et_constante(self):
        s = rdv.resoudre("x^3")
        self.assertEqual(blocs_de_type(s, "texte")[-1]["html"],
                         "Aucun extremum local : f est strictement monotone (ou n'a que des points où f' s'annule sans changer de signe).")
        s = rdv.resoudre("x^(2-2)")
        self.assertEqual(blocs_de_type(s, "texte")[-1]["html"],
                         "f' est nulle sur son ensemble de définition : f est constante sur chaque intervalle, aucun extremum.")

    def test_rappel(self):
        c = rdv.resoudre("ln(x)/x")["cartes"][0]
        self.assertTrue(c["blocs"][1]["html"].endswith(" — détail dans l'outil « Ensemble de définition »."))
        self.assertTrue(c["blocs"][1]["html"].startswith("\\(ED = "))

    def test_cartes_d_erreur(self):
        with mock.patch.object(rdv, "etudier", return_value={
                "ok": True, "f_tex": "f", "ed_tex": "E", "deriv_resolu": False,
                "deriv_erreur": "Hors cadre.", "deriv_detail": "KeyError"}):
            s = rdv.resoudre("x")
        valide(self, s)
        self.assertEqual(len(s["cartes"]), 2)
        self.assertEqual((s["cartes"][1]["style"], s["cartes"][1]["detail"]), ("erreur", "KeyError"))
        self.assertEqual(s["cartes"][1]["blocs"], [{"type": "erreur", "texte": "Hors cadre."}])

    def test_erreurs_en_francais(self):
        for entree in ("", "ln(", "x+*2"):
            with self.subTest(entree=entree):
                s = rdv.resoudre(entree)
                valide(self, s)
                self.assertFalse(s["ok"])
                self.assertNotIn("Traceback", json.dumps(s))

    def test_json(self):
        self.assertEqual(json.loads(rdv.resoudre_json("x^2")), rdv.resoudre("x^2"))


if __name__ == "__main__":
    unittest.main()
