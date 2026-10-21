"""T12 — etude-complete/resoudre_ec.py : sortie du format commun, sans rien perdre de l'ancienne,
cartes dans l'ordre de la page (EC-14), et cohérence avec les sorties des outils séparés (EC-01)."""
import json
import unittest

import moteurs  # noqa: F401  (chemins des moteurs)
import etude_complete as ec
import resoudre_dv as rdv
import resoudre_la as rla
import resoudre_ec as rec
from aides_sortie import manquantes, valide, blocs_de_type
from cas import entrees_page, CAS_LIMITES

ENTREES = list(dict.fromkeys(entrees_page("etude-complete") + CAS_LIMITES["etude-complete"]))
TECHNIQUE = ("detail", "ok", "genre", "a", "b", "domaine_etude_tex", "ed_deriv_tex", "deriv_detail", "signe_detail")


def carte(s, titre):
    return next(c for c in s["cartes"] if c["titre"] == titre)


def titres(s):
    return [c["titre"] for c in s["cartes"]]


class TestResoudreEC(unittest.TestCase):
    def test_schema_et_rien_de_perdu(self):
        for entree in ENTREES:
            with self.subTest(entree=entree):
                s = rec.resoudre(entree)
                valide(self, s)
                self.assertEqual(manquantes(ec.etudier(entree), s, TECHNIQUE), [])

    def test_ordre_des_cartes_comme_la_page(self):
        for entree in ENTREES:
            ancien = ec.etudier(entree)
            if not ancien["ok"]:
                continue
            dv, lim = ancien["derivee"], ancien["limites"]
            attendu = ["Fonction"]
            if dv["deriv_resolu"]:
                attendu.append("Dérivée")
                if dv["signe_resolu"]:
                    attendu.append("Signe de f' et variations")
            if lim.get("tableaux_signe"):
                attendu.append("Tableaux de signes")
            attendu += ["Limite"] * len(lim["etudes"]) + ["Bilan des asymptotes", "Graphique"]
            with self.subTest(entree=entree):
                self.assertEqual(titres(rec.resoudre(entree)), attendu)

    def test_cartes_identiques_aux_outils_separes(self):
        """EC-01 : dérivée et limites sont les mêmes cartes que dans les outils séparés
        (le tableau de variations ajoute les limites, le rappel ne renvoie pas à l'ED)."""
        for entree in ENTREES:
            if not ec.etudier(entree)["ok"]:
                continue
            with self.subTest(entree=entree):
                s, d, l = rec.resoudre(entree), rdv.resoudre(entree), rla.resoudre(entree)
                self.assertEqual(s["cartes"][1], d["cartes"][1])
                self.assertEqual([c for c in s["cartes"] if c["titre"] == "Limite"],
                                 [c for c in l["cartes"] if c["titre"] == "Limite"])

    def test_phrases_propres_a_l_etude_complete(self):
        s = rec.resoudre("x^3")
        self.assertEqual(carte(s, "Signe de f' et variations")["blocs"][-1]["html"], "Aucun extremum local.")
        s = rec.resoudre("ln(x)/x")
        self.assertEqual(s["cartes"][0]["blocs"][1]["html"], "\\(ED = \\left]0 \\,;\\, +\\infty\\right[\\)")
        self.assertEqual(s["cartes"][-2]["style"], "normal")

    def test_graphique(self):
        s = rec.resoudre("ln(x)/x")
        g = blocs_de_type(s, "graphique")[0]
        ancien = ec.etudier("ln(x)/x")
        self.assertEqual((g["xmin"], g["xmax"]), (ancien["graphique"]["xmin"], ancien["graphique"]["xmax"]))
        self.assertEqual(g["segments"], ancien["graphique"]["segments"])
        self.assertEqual(g["extrema"], ancien["derivee"]["extrema"])
        self.assertEqual(g["asymptotes"], ancien["limites"]["asymptotes"])
        self.assertTrue(g["recalculable"])

    def test_limites_dans_le_tableau_de_variations(self):
        s = rec.resoudre("e^(1/x)")
        tab = [b for b in carte(s, "Signe de f' et variations")["blocs"] if b["type"] == "tableau"][-1]
        self.assertEqual(tab["limites"], ec.etudier("e^(1/x)")["variations_limites"])

    def test_erreurs_en_francais(self):
        for entree in ("", "ln(", "x+*2"):
            with self.subTest(entree=entree):
                s = rec.resoudre(entree)
                valide(self, s)
                self.assertFalse(s["ok"])
                self.assertNotIn("Traceback", json.dumps(s))

    def test_json(self):
        self.assertEqual(json.loads(rec.resoudre_json("x^2")), rec.resoudre("x^2"))


if __name__ == "__main__":
    unittest.main()
