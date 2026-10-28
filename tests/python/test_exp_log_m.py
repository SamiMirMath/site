"""T35 (étape 1) — Paramètre « filière » de l'outil « Exponentielles et logarithmes » (EL-26) : C est le défaut et reste strictement identique,
une filière inconnue donne un message en français. Les étapes suivantes ajoutent ici l'ensemble de définition, le regroupement et la vérification."""
import json
import unittest

import moteurs  # noqa: F401  (chemins des moteurs)
import exp_log as el
import resoudre_el as rel
import resoudre_ed
import sortie as so
from cas_el import entrees_el, entrees_el_m


class TestFiliereParDefaut(unittest.TestCase):
    def test_c_est_le_defaut_pour_toutes_les_entrees(self):
        for entree in entrees_el():
            with self.subTest(entree=entree):
                self.assertEqual(rel.resoudre(entree), rel.resoudre(entree, "C"))
                self.assertEqual(rel.resoudre_json(entree), rel.resoudre_json(entree, "C"))

    def test_l_exercice_par_defaut_est_celui_de_la_filiere_c(self):
        for niveau in ("facile", "moyen", "logarithme", "difficile"):
            for graine in range(20):
                self.assertEqual(el.exercice(niveau, graine), el.exercice(niveau, graine, "C"))
        self.assertTrue(json.loads(el.exercice_json("facile", "C"))["ok"])
        self.assertTrue(json.loads(el.exercice_json("facile"))["ok"])

    def test_la_filiere_m_donne_une_sortie_valide_pour_son_corpus(self):
        for entree in entrees_el_m():
            with self.subTest(entree=entree):
                self.assertEqual(so.valider(rel.resoudre(entree, "M")), [])


class TestFiliereInconnue(unittest.TestCase):
    def test_message_en_francais(self):
        for filiere in ("", "c", "m", "Ms", "3C", None):
            with self.subTest(filiere=filiere):
                s = rel.resoudre("2^x=8", filiere)
                self.assertEqual(s, {"ok": False, "erreur": el.MESSAGE_FILIERE})
                self.assertEqual(json.loads(rel.resoudre_json("2^x=8", filiere)), s)
                self.assertEqual(el.exercice("facile", 1, filiere), {"ok": False, "erreur": el.MESSAGE_FILIERE})
                self.assertEqual(json.loads(el.exercice_json("facile", filiere)), {"ok": False, "erreur": el.MESSAGE_FILIERE})

    def test_le_message_vouvoie(self):
        self.assertNotRegex(el.MESSAGE_FILIERE, r"\b(tu|ton|ta|tes|toi)\b")


class TestCartesEDReutilisables(unittest.TestCase):
    """resoudre_ed expose les blocs d'une condition et de la conclusion « ED = … » (réutilisés par la filière M) ; l'outil ED en garde la sortie."""

    def test_les_cartes_de_l_outil_ed_sont_faites_de_ces_blocs(self):
        import ensemble_def
        for f in ("ln(x)+ln(x-1)", "ln(x^2-4)+ln(x+3)", "ln(x-3)+ln(1-x)", "ln(x)+x^2", "x^2+1"):
            with self.subTest(f=f):
                r = ensemble_def.analyser(f)
                self.assertEqual([resoudre_ed._carte_condition(c)["blocs"] for c in r["conditions"]], [resoudre_ed.blocs_condition(c) for c in r["conditions"]])
                self.assertEqual(resoudre_ed._carte_finale(r)["blocs"], resoudre_ed.blocs_ensemble(r))

    def test_le_cas_sans_condition_et_le_cas_non_resolu(self):
        self.assertEqual(resoudre_ed.blocs_ensemble({"complet": True, "conditions": []}), [so.resultat("ED = \\mathbb{R}")])
        self.assertEqual(resoudre_ed.blocs_ensemble({"complet": False, "conditions": []}),
                         [so.erreur("Une condition n'a pas pu être résolue : l'ED n'est pas calculé.")])


if __name__ == "__main__":
    unittest.main()
