"""Toute sortie de moteur est du JSON strict (pas de Infinity ni NaN) : la page appelle JSON.parse.
Bug : x^(2/3) en −∞ (SymPy : oo*(-1)**(2/3)) donnait valeur_val = Infinity, donc une erreur du moteur."""
import json
import math
import random
import unittest

from moteurs import ensemble_def as ed  # noqa: F401  (chemins + SymPy)
import derivee_variations as dv
import etude_complete as ec
import factorisation as fa
import limites_asymptotes as la
import resoudre_el

import os
from cas import CAS_LIMITES, entrees_page, entrees_factorisation
from cas_el import entrees_el

OUTILS_ENTREES = {
    nom: entrees_page(nom) + CAS_LIMITES[nom]
    for nom in ("ensemble-definition", "derivee-variations", "limites-asymptotes", "etude-complete")
}
OUTILS_ENTREES["factorisation"] = entrees_factorisation()
DOSSIER_INSTANTANES = os.path.join(os.path.dirname(__file__), "instantanes")


def fichiers_json(dossier):
    """Chemins relatifs des .json du dossier, sous-dossiers compris (instantanes/resoudre/…)."""
    return sorted(os.path.relpath(os.path.join(d, n), dossier)
                  for d, _, noms in os.walk(dossier) for n in noms if n.endswith(".json"))


def refuse(constante):
    raise AssertionError(f"constante JSON non standard : {constante}")


def strict(texte):
    return json.loads(texte, parse_constant=refuse)


def non_finis(o, chemin=""):
    if isinstance(o, float) and not math.isfinite(o):
        yield chemin
    elif isinstance(o, dict):
        for k, v in o.items():
            yield from non_finis(v, f"{chemin}/{k}")
    elif isinstance(o, (list, tuple)):
        for i, v in enumerate(o):
            yield from non_finis(v, f"{chemin}/{i}")


class TestJsonStrict(unittest.TestCase):
    def test_x_puissance_2_sur_3(self):
        r = ec.etudier("x^(2/3)")
        self.assertEqual(list(non_finis(r)), [])
        self.assertEqual(r["limites"]["asymptotes"], [])        # f → +∞ des deux côtés
        for et in r["limites"]["etudes"]:                       # chaque borne donne la limite +∞
            self.assertTrue(any(r"= +\infty" in e["html"] and r"\lim" in e["html"] for e in et["etapes"]), et)
        strict(ec.etudier_json("x^(2/3)"))

    def test_garde_fou_remplace_les_infinis_par_null(self):
        for valeur in (math.inf, -math.inf, math.nan):
            sortie = ed.json_strict({"a": [valeur], "b": {"c": valeur}})
            self.assertEqual(strict(sortie), {"a": [None], "b": {"c": None}})

    def test_aucun_non_fini_dans_les_moteurs(self):
        """Le garde-fou ne doit pas masquer un bug : les dictionnaires eux-mêmes sont finis."""
        for entree in OUTILS_ENTREES["etude-complete"]:
            with self.subTest(f=entree):
                self.assertEqual(list(non_finis(ec.etudier(entree))), [])
                strict(ec.etudier_json(entree))

    def test_toutes_les_sorties_json(self):
        fonctions = {"ensemble-definition": [ed.analyser_json, ed.verifier_json, ed.apercu_json],
                     "derivee-variations": [dv.etudier_json],
                     "limites-asymptotes": [la.etudier_json],
                     "etude-complete": [ec.etudier_json]}
        for outil, appels in fonctions.items():
            for entree in OUTILS_ENTREES[outil]:
                for appel in appels:
                    with self.subTest(outil=outil, f=entree, appel=appel.__name__):
                        strict(appel(entree))

    def test_factorisation_json(self):
        for entree in OUTILS_ENTREES["factorisation"]:
            with self.subTest(f=entree):
                strict(fa.factoriser_json(entree))

    def test_fichiers_d_instantanes_en_json_strict(self):
        for nom in fichiers_json(DOSSIER_INSTANTANES):
            with self.subTest(fichier=nom), open(os.path.join(DOSSIER_INSTANTANES, nom), encoding="utf-8") as f:
                strict(f.read())

    def test_exponentielles_logarithmes_json(self):
        for entree in entrees_el():
            for appel in (resoudre_el.resoudre_json, resoudre_el.apercu_json):
                with self.subTest(f=entree, appel=appel.__name__):
                    strict(appel(entree))
            self.assertEqual(list(non_finis(resoudre_el.resoudre(entree))), [], entree)

    def test_exercices_de_factorisation(self):
        random.seed(2026_10_29)                   # tirages reproductibles, quel que soit l'ordre des tests
        for niveau in ("facile", "moyen", "difficile", "tresDifficile"):
            for _ in range(60):
                strict(fa.exercice_json(niveau))


if __name__ == "__main__":
    unittest.main()
