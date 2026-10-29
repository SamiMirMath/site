"""Chantier « Limites et asymptotes » 3M, étape 1, point 5 : la règle du podium ne justifie plus rien (LA-07, LA-15, LA-32, LA-34).

Sur le corpus de l'enseignant, les cas figés, les exemples et exercices de la page, et le corpus de style : aucune rédaction (outil Limites,
corrigé `resoudre` de la page, Étude complète) ne contient « croissance comparée », « podium » ni « limite de référence ».
Étude complète : elle fonctionne encore sur 3.10e et 3.11e."""
import os
import sys
import unittest

from moteurs import ensemble_def  # noqa: F401  (chemins + SymPy)
import limites_asymptotes as la
import resoudre_la as rla
import resoudre_ec as rec
import etude_complete as ec
from cas import CAS_LIMITES, entrees_page
from test_redaction_limites import TestStyle

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "donnees"))
from corpus_limites_3m import CAS, ETUDES, PAS_PRIS_EN_CHARGE  # noqa: E402

MOTS = ("croissance comparée", "podium", "limite de référence")
ENTREES = list(dict.fromkeys(
    entrees_page("limites-asymptotes") + CAS_LIMITES["limites-asymptotes"] + TestStyle.CORPUS
    + [c.saisie for c in CAS if c.id not in PAS_PRIS_EN_CHARGE] + [e[1] for e in ETUDES]))


def chaines(o):
    """Toutes les chaînes d'une sortie JSON (récursivement)."""
    if isinstance(o, str):
        yield o
    elif isinstance(o, dict):
        for v in o.values():
            yield from chaines(v)
    elif isinstance(o, (list, tuple)):
        for v in o:
            yield from chaines(v)


class TestAucuneJustificationParLePodium(unittest.TestCase):
    def verifier(self, sortie, nom):
        for t in chaines(sortie):
            for mot in MOTS:
                self.assertNotIn(mot, t, nom)

    def test_outil_limites(self):
        for entree in ENTREES:
            with self.subTest(f=entree):
                self.verifier(la.etudier(entree), entree)

    def test_corrige_de_la_page(self):
        for entree in dict.fromkeys(entrees_page("limites-asymptotes") + [e[1] for e in ETUDES]):
            with self.subTest(f=entree):
                self.verifier(rla.resoudre(entree), entree)

    def test_etude_complete(self):
        for entree in dict.fromkeys(entrees_page("etude-complete") + [e[1] for e in ETUDES]):
            with self.subTest(f=entree):
                self.verifier(rec.resoudre(entree), entree)

    def test_etude_complete_fonctionne_sur_3_10e_et_3_11e(self):
        for entree in ("(e^x+2)/(1-3e^x)", "(ln(x)-2)/(ln(x)-1)"):
            with self.subTest(f=entree):
                r = ec.etudier(entree)
                self.assertTrue(r["ok"], r.get("erreur"))
                s = rec.resoudre(entree)
                self.assertTrue(s["ok"], s)
                self.verifier(s, entree)


if __name__ == "__main__":
    unittest.main()
