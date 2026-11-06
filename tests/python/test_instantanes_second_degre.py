"""Instantanés de la rédaction du 2e degré (chantier equations-2e-degre, dès P2b : decisions.md § 13.2 ; plan, P2b à P5).

Depuis P5, l'instantané est celui de l'outil : tests/python/instantanes/equations-2e-degre.json, figé par
`test_instantanes.TestInstantanes.test_equations_2e_degre` (clé = la saisie ; `test_instantanes.instantane_equation` : la saisie lue
par l'outil, la résolution de `second_degre.resoudre_equation` et ses cartes, une par étape (R1), la variante « formule » quand elle
est proposée), lu par `dump_sorties.py` et contrôlé, comme les autres instantanés, par `test_json_strict` (JSON strict) et
`test_vocabulaire` (C6, R12). Ce fichier garde ce que ces contrôles communs ne voient pas : chaque exercice du § 8 a son instantané, résolu ; chaque
entrée du corpus (`RESOLUES`, `NON_RESOLUES`, `STRUCTURES_NON_ECRITES`) est figée avec son statut ; les cartes figées forment une
sortie conforme au schéma commun."""
import json
import os
import unittest

import moteurs  # noqa: F401  (chemins des moteurs)

import sortie
from corpus_second_degre import NON_RESOLUES, RESOLUES, SECTION_8, STRUCTURES_NON_ECRITES
from test_instantanes import DOSSIER

CHEMIN = os.path.join(DOSSIER, "equations-2e-degre.json")


class TestInstantanesSecondDegre(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        with open(CHEMIN, encoding="utf-8") as f:
            cls.reference = json.load(f)

    def test_section_8_complete(self):
        """Chaque exercice du § 8 a un instantané (et il est résolu : l'oracle le contrôle dans test_redaction_second_degre)."""
        for nom in SECTION_8:
            with self.subTest(nom=nom):
                self.assertIn(nom, RESOLUES)
                self.assertIn(RESOLUES[nom], self.reference)
                self.assertEqual(self.reference[RESOLUES[nom]]["cours"]["statut"], "resolu")
        self.assertEqual(len(SECTION_8), 52)

    def test_corpus_fige_avec_son_statut(self):
        """Tout le corpus de la rédaction est figé (P2b à P4b), chaque entrée avec son statut : résolue, ou le message attendu."""
        attendus = {s: "resolu" for s in RESOLUES.values()}
        attendus.update({s: statut for s, statut in NON_RESOLUES.values()})
        attendus.update({s: "forme_non_traitee" for s in STRUCTURES_NON_ECRITES})
        for saisie, statut in attendus.items():
            with self.subTest(saisie=saisie):
                self.assertIn(saisie, self.reference)
                self.assertEqual(self.reference[saisie]["cours"]["statut"], statut)

    def test_sorties_conformes(self):
        """Les cartes figées (une par étape, R1, puis la solution) forment une sortie conforme au schéma commun (sortie.valider) ;
        chaque étape figée est dans une carte, dans l'ordre."""
        for saisie, v in self.reference.items():
            for cle in ("cours", "formule"):
                if cle in v and v[cle]["statut"] == "resolu":
                    with self.subTest(entree=saisie, chemin=cle):
                        r = v[cle]
                        cartes = [sortie.carte(f"Étape {k}", c["blocs"], badge="badge") for k, c in enumerate(r["cartes"], 1)]
                        s = sortie.sortie_ok("x", cartes + [sortie.carte("Solution", r["solution"])])
                        self.assertEqual(sortie.valider(s), [])
                        self.assertEqual([i for c in r["cartes"] for i in c["etapes"]], list(range(len(r["etapes"]))))


if __name__ == "__main__":
    unittest.main()
