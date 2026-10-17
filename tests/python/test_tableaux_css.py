"""Tableaux de signe et de variations : une seule feuille de style (commun/style.css) pour tous les outils,
resserrée à 360 px, 1re colonne (libellés) fixe pendant le défilement. Le rendu à 360 px et à 900 px se
vérifie en capture (voir docs/specifications/etude-complete.md, EC-13)."""
import os
import re
import unittest

from moteurs import RACINE

OUTILS = ["ensemble-definition", "derivee-variations", "limites-asymptotes", "etude-complete"]


def lire(chemin):
    with open(os.path.join(RACINE, chemin), encoding="utf-8") as f:
        return f.read()


class TestFeuilleCommune(unittest.TestCase):
    def test_pages_utilisent_la_feuille_commune(self):
        for outil in OUTILS:
            with self.subTest(outil=outil):
                page = lire(outil + "/index.html")
                self.assertIn('<link rel="stylesheet" href="../commun/style.css">', page)
                self.assertEqual(re.findall(r"^\.tsigne[^\n]*", page, re.M), [],
                                 "règle .tsigne dans la page : elle doit être dans commun/style.css")

    def test_feuille(self):
        css = lire("commun/style.css")
        self.assertIn("position:sticky;left:0", css)                       # libellés fixes
        self.assertIn("@media (max-width:480px)", css)                     # petit écran
        petit = css[css.index("@media (max-width:480px)"):css.index("@media print")]
        taille = float(re.search(r"font-size:([\d.]+)rem", petit).group(1))
        self.assertGreaterEqual(taille, 0.85)                              # valeurs : jamais sous 0,85
        self.assertIn(".tsigne{overflow-x:auto", css)                      # défilement des tableaux larges
        self.assertIn("@media print", css)


if __name__ == "__main__":
    unittest.main()
