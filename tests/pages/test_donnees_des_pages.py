"""Chantier fondations, F3 (revue de structure, R1 ; docs/architecture.md, A3) : les données des tests de pages propres à un outil,
écrites à la main (corpus réduit, calcul, exemple, saisie invalide…), ont pour clés exactement les outils du site lus par
tests/python/outils_du_site.py (registre et manifeste), et chaque outil a sa méthode de test là où il y en a une par outil : un outil
oublié ou en trop fait échouer ce test. Aucun navigateur n'est ouvert.

Le pendant pour les tests Python est tests/python/test_outils_du_site.py."""
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(__file__))
import rendu  # noqa: E402  (met aussi tests/python sur le chemin)
import outils_du_site  # noqa: E402
import test_comportement  # noqa: E402
import test_largeurs  # noqa: E402
import test_rendu  # noqa: E402

DOSSIER_REFERENCES = os.path.join(os.path.dirname(__file__), "references")
REFERENCES_SANS_OUTIL = {"graphique-traces.json": "tracés du graphique (test_graphique.py), commun à l'Étude complète"}


class TestDonneesDesPages(unittest.TestCase):
    def setUp(self):
        self.pyodide = outils_du_site.outils_pyodide()
        self.variantes = list(outils_du_site.variantes())

    def test_outils_et_variante_de_filiere(self):
        self.assertEqual(rendu.OUTILS, self.pyodide)
        self.assertEqual(self.variantes, [rendu.OUTIL_M], "variante de filière du registre (?filiere=…) inconnue de rendu.py")
        dossier, requete = rendu.page_de(rendu.OUTIL_M)
        self.assertIn(requete, next(o for o in outils_du_site.registre() if o["id"] == dossier).get("parametres", {}).values())

    def test_cles_des_donnees_propres_a_un_outil(self):
        for nom, donnees, attendus in (
                ("rendu.REDUIT", rendu.REDUIT, self.pyodide + self.variantes),
                ("test_comportement.CALCUL", test_comportement.CALCUL, self.pyodide),
                ("test_comportement.EXEMPLE", test_comportement.EXEMPLE, self.pyodide),
                ("test_comportement.INVALIDE", test_comportement.INVALIDE, self.pyodide)):
            with self.subTest(donnees=nom):
                self.assertEqual(sorted(donnees), sorted(attendus), f"{nom} : clés différentes des outils à moteur Python du manifeste")
        for nom, partie in (("rendu.ERREURS", rendu.ERREURS), ("test_comportement.ANALYSE", test_comportement.ANALYSE)):
            with self.subTest(donnees=nom):                   # parties choisies d'outils : seulement des outils du manifeste
                self.assertLessEqual(set(partie), set(self.pyodide), nom)

    def test_une_methode_par_outil(self):
        for classe, attendues in (
                (test_rendu.TestRendu, [outils_du_site.nom_de_test(o) for o in self.pyodide + self.variantes]),
                (test_largeurs.TestLargeurs, ["test_balayage_" + o.replace("-", "_") for o in outils_du_site.outils() + self.variantes])):
            presentes = {n for n in dir(classe) if n.startswith("test_")}
            for methode in attendues:
                with self.subTest(classe=classe.__name__, methode=methode):
                    self.assertIn(methode, presentes)

    def test_une_reference_par_outil(self):
        """tests/pages/references : une référence par page à moteur Python et par variante de filière, rien d'autre (hors exceptions
        nommées)."""
        fichiers = {n for n in os.listdir(DOSSIER_REFERENCES) if n.endswith(".json")}
        attendus = {o + ".json" for o in self.pyodide + self.variantes} | set(REFERENCES_SANS_OUTIL)
        self.assertEqual(fichiers, attendus)


if __name__ == "__main__":
    unittest.main()
