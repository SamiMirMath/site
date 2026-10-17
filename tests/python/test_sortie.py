"""T12 — moteur/sortie.py : le validateur du format de sortie commun accepte les sorties
conformes et refuse les écarts (type inconnu, clé inconnue, case hors vocabulaire, ligne de
mauvaise longueur, trace Python dans un message d'erreur)."""
import copy
import unittest

import moteurs  # noqa: F401  (chemins des moteurs)
import sortie as so


def tableau(cells=("+", "0", "-")):
    return {"type": "tableau", "var": "x", "crit": ["1"],
            "rows": [{"label": "x - 1", "cells": list(cells), "final": True}]}


def exemple():
    return so.sortie_ok("f(x) = x", [
        so.carte("Condition 1", [
            so.texte("On résout \\(x > 0\\)."),
            so.formule("x > 0"),
            tableau(),
            so.liste(["a", "b"], style="bilan"),
            so.resultat("E_1 = \\mathbb{R}"),
        ], badge="logarithme"),
        so.carte("Fin", [so.erreur("Condition non résolue.")], style="erreur"),
    ], entete=so.carte("Rappel", [so.formule("f(x) = x")]), besoin_sympy=False)


class TestValidateur(unittest.TestCase):
    def test_sortie_conforme(self):
        self.assertEqual(so.valider(exemple()), [])

    def test_sortie_erreur_conforme(self):
        self.assertEqual(so.valider(so.sortie_erreur("Entrez une expression.")), [])
        self.assertEqual(so.valider(so.sortie_erreur("Oups.", detail="KeyError: 'x'")), [])

    def test_erreur_sans_message_ou_avec_trace(self):
        self.assertTrue(so.valider({"ok": False}))
        self.assertTrue(so.valider(so.sortie_erreur("")))
        self.assertTrue(so.valider(so.sortie_erreur("Traceback (most recent call last):")))

    def test_ok_avec_erreur(self):
        s = exemple()
        s["erreur"] = "x"
        self.assertTrue(so.valider(s))

    def _refuse(self, modifier, fragment):
        s = copy.deepcopy(exemple())
        modifier(s)
        ecarts = so.valider(s)
        self.assertTrue(any(fragment in e for e in ecarts), ecarts)

    def test_type_de_bloc_inconnu(self):
        self._refuse(lambda s: s["cartes"][0]["blocs"].append({"type": "video"}), "type de bloc inconnu")

    def test_cle_inconnue(self):
        self._refuse(lambda s: s["cartes"][0]["blocs"][0].update(couleur="rouge"), "clé « couleur » inconnue")
        self._refuse(lambda s: s["cartes"][0].update(autre=1), "clé « autre » inconnue")
        self._refuse(lambda s: s.update(autre=1), "clé « autre » inconnue")

    def test_cle_manquante(self):
        self._refuse(lambda s: s["cartes"][0]["blocs"][1].pop("tex"), "clé « tex » manquante")

    def test_style_inconnu(self):
        self._refuse(lambda s: s["cartes"][0].update(style="rose"), "style « rose » inconnu")
        self._refuse(lambda s: s["cartes"][0]["blocs"][3].update(style="x"), "style « x » inconnu")

    def test_case_hors_vocabulaire(self):
        self._refuse(lambda s: s["cartes"][0]["blocs"][2]["rows"][0]["cells"].__setitem__(1, "?"), "hors vocabulaire")

    def test_cases_du_vocabulaire(self):
        for c in ("+", "-", "0", "|", "||", "x", "asym", "extremum", "", "\\nearrow", "val:\\frac{1}{2}"):
            b = tableau((c, "0", "-"))
            self.assertEqual(so.valider(so.sortie_ok("f", [so.carte("t", [b])])), [], c)

    def test_ligne_de_mauvaise_longueur(self):
        self._refuse(lambda s: s["cartes"][0]["blocs"][2]["rows"][0].update(cells=["+", "-"]), "2 cases, 3 attendues")

    def test_texte_vide(self):
        self._refuse(lambda s: s["cartes"][0]["blocs"][0].update(html=""), "html vide")

    def test_limites_du_tableau(self):
        s = exemple()
        s["cartes"][0]["blocs"][2]["limites"] = {"colonnes": [], "moins_inf": "1", "plus_inf": "1", "non_determinees": []}
        self.assertEqual(so.valider(s), [])
        s["cartes"][0]["blocs"][2]["limites"]["x"] = 1
        self.assertTrue(so.valider(s))


if __name__ == "__main__":
    unittest.main()
