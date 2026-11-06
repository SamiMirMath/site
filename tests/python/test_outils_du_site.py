"""Chantier fondations, F3 (revue de structure, R1 ; docs/architecture.md, A3) : une seule liste des outils, tests/python/outils_du_site.py
(registre et manifeste), dont les tests dérivent leurs listes.

- Les deux sources s'accordent, et l'ordre de sys.path posé par moteurs.py suit les dossiers du manifeste.
- Les données des tests Python propres à un outil, écrites à la main (fonction et corpus des instantanés, entrées du JSON strict,
  exemple de l'import à plat, clavier, vocabulaire…), ont pour clés exactement les outils du manifeste (et ses variantes de filière là
  où elles ont des données à part), sauf EXCEPTIONS, nommées avec leur raison ; chaque outil a sa méthode de test là où il y en a une
  par outil, et son fichier d'instantanés. Un outil oublié ou en trop fait échouer ce test.

Le pendant pour les tests de pages est tests/pages/test_donnees_des_pages.py."""
import os
import sys
import unittest

import outils_du_site
from moteurs import RACINE
import cas
import test_instantanes
import test_instantanes_resoudre
import test_json_strict
import test_resoudre_import
import test_source_unique
import test_vocabulaire

DOSSIER_INSTANTANES = os.path.join(os.path.dirname(__file__), "instantanes")

# (données, outil) -> raison : un outil du manifeste volontairement absent de ces données
EXCEPTIONS = {
    ("test_instantanes.OUTILS", "exponentielles-logarithmes"):
        "jeu moteur (T01) : les exponentielles n'ont pas de sortie de moteur unique (l'aiguillage entre exp_log et exp_log_m, filières, "
        "variantes et voie des exposants, est dans l'adaptateur resoudre_el.py) ; nées avec resoudre(), elles n'ont pas eu de migration "
        "T17 à T20 à vérifier ; le jeu resoudre (instantanes/resoudre/exponentielles-logarithmes.json et -M.json) couvre tout l'outil, "
        "filières C et M",
}


def attendus(donnees, outils):
    """Les outils attendus comme clés de `donnees`, moins les exceptions nommées."""
    return sorted(o for o in outils if (donnees, o) not in EXCEPTIONS)


class TestSourcesDesOutils(unittest.TestCase):
    def test_registre_et_manifeste(self):
        outils, pyodide = outils_du_site.outils(), outils_du_site.outils_pyodide()
        self.assertEqual(len(set(outils)), len(outils), "id en double dans le registre")
        self.assertLessEqual(set(pyodide), set(outils), "outil du manifeste absent du registre")
        self.assertEqual(outils_du_site.pages(), {o: o for o in outils}, "chemin du registre différent de « <id>/ »")
        for d in outils_du_site.dossiers_moteurs():
            self.assertTrue(os.path.isdir(os.path.join(RACINE, d)), d)
        self.assertLessEqual(set(outils_du_site.variantes().values()), set(pyodide), "variante de filière d'un outil sans moteur")
        self.assertEqual(outils_du_site.nom_de_test("exponentielles-logarithmes-M"), "test_exponentielles_logarithmes_filiere_m")

    def test_ordre_de_sys_path(self):
        """moteurs.py insère en tête de sys.path chaque dossier de dossiers_moteurs(), dans l'ordre : le dernier est le premier."""
        dossiers = outils_du_site.dossiers_moteurs()
        self.assertEqual(dossiers, ["ensemble-definition", "moteur", "derivee-variations", "limites-asymptotes", "etude-complete",
                                    "factorisation", "exponentielles-logarithmes",
                                    "equations-2e-degre"])      # l'ordre d'avant F3 (butée explicite), puis equations-2e-degre (P5)
        positions = [sys.path.index(os.path.join(RACINE, d)) for d in dossiers]
        self.assertEqual(positions, sorted(positions, reverse=True))


class TestClesDesDonnees(unittest.TestCase):
    """Données propres à un outil, écrites à la main : clés = outils du manifeste (et variantes), sauf EXCEPTIONS."""

    def setUp(self):
        self.pyodide = outils_du_site.outils_pyodide()
        self.variantes = outils_du_site.variantes()

    def verifier(self, nom, donnees, outils):
        with self.subTest(donnees=nom):
            self.assertEqual(sorted(donnees), attendus(nom, outils), f"{nom} : clés différentes des outils (outils_du_site.py)")

    def test_cles(self):
        avec_filiere = sorted(set(self.variantes.values()))
        self.verifier("test_instantanes.OUTILS", test_instantanes.OUTILS, self.pyodide)
        self.verifier("test_instantanes_resoudre.OUTILS", test_instantanes_resoudre.OUTILS, self.pyodide + list(self.variantes))
        self.verifier("test_json_strict.OUTILS_ENTREES", test_json_strict.OUTILS_ENTREES, self.pyodide)
        self.verifier("test_json_strict.ENTREES_FILIERE_M", test_json_strict.ENTREES_FILIERE_M, avec_filiere)
        self.verifier("test_resoudre_import.EXEMPLE", test_resoudre_import.EXEMPLE, self.pyodide)
        self.verifier("test_resoudre_import.FILIERE_M", test_resoudre_import.FILIERE_M, avec_filiere)
        self.verifier("test_source_unique.TestDispositionDuClavier.PAGES", test_source_unique.TestDispositionDuClavier.PAGES, self.pyodide)
        vocabulaire = test_vocabulaire.TestVocabulaireEleve
        self.verifier("test_vocabulaire.TestVocabulaireEleve (ANALYSES + METHODES)",
                      list(vocabulaire.ANALYSES) + list(vocabulaire.METHODES), self.pyodide)
        with self.subTest(donnees="cas.CAS_LIMITES"):          # corpus des outils d'analyse : seulement des outils du manifeste
            self.assertLessEqual(set(cas.CAS_LIMITES), set(self.pyodide))

    def test_exceptions_utiles(self):
        """Chaque exception nomme un outil du manifeste et a sa raison : une exception devenue inutile (outil ajouté aux données) échoue."""
        for (donnees, outil), raison in EXCEPTIONS.items():
            with self.subTest(donnees=donnees, outil=outil):
                self.assertIn(outil, self.pyodide)
                self.assertTrue(raison.strip())
                module, nom = donnees.split(".", 1)
                self.assertNotIn(outil, getattr(sys.modules[module], nom))

    def test_une_methode_par_outil(self):
        for classe, cles in ((test_instantanes.TestInstantanes, test_instantanes.OUTILS),
                             (test_instantanes_resoudre.TestInstantanesResoudre, test_instantanes_resoudre.OUTILS),
                             (test_vocabulaire.TestVocabulaireEleve, test_vocabulaire.TestVocabulaireEleve.METHODES)):
            presentes = {n for n in dir(classe) if n.startswith("test_")}
            for cle in cles:
                methode = classe.METHODES[cle] if classe is test_vocabulaire.TestVocabulaireEleve else outils_du_site.nom_de_test(cle)
                with self.subTest(classe=classe.__name__, methode=methode):
                    self.assertIn(methode, presentes)

    def test_un_instantane_par_outil(self):
        """Fichiers d'instantanés : exactement un par clé de leur test (jeu moteur, jeu resoudre)."""
        for dossier, cles in ((DOSSIER_INSTANTANES, test_instantanes.OUTILS),
                              (os.path.join(DOSSIER_INSTANTANES, "resoudre"), test_instantanes_resoudre.OUTILS)):
            with self.subTest(dossier=os.path.relpath(dossier, RACINE)):
                fichiers = {n for n in os.listdir(dossier) if n.endswith(".json")}
                self.assertEqual(fichiers, {c + ".json" for c in cles})


if __name__ == "__main__":
    unittest.main()
