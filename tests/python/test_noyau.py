"""T11 — moteur/noyau.py : interface publique du noyau (ensemble_def.py).

Les moteurs des outils n'importent que de `noyau`, et aucun nom commençant par « _ » ne
traverse la frontière du noyau. `noyau` ne fait que réexporter : mêmes objets que ceux de
ensemble_def (donc mêmes comportements, mêmes instantanés)."""
import ast
import os
import unittest

import moteurs  # noqa: F401  (chemins des moteurs)
from moteurs import RACINE

import ensemble_def
import noyau

MOTEURS = [
    "derivee-variations/derivee_variations.py",
    "limites-asymptotes/limites_asymptotes.py",
    "etude-complete/etude_complete.py",
    "factorisation/factorisation.py",
]


def imports_de(chemin):
    """[(module, nom, alias)] de tous les `from … import …` du fichier (y compris dans les fonctions)."""
    with open(os.path.join(RACINE, chemin), encoding="utf-8") as f:
        arbre = ast.parse(f.read())
    return [(n.module, a.name, a.asname or a.name)
            for n in ast.walk(arbre) if isinstance(n, ast.ImportFrom) for a in n.names]


def modules_importes(chemin):
    with open(os.path.join(RACINE, chemin), encoding="utf-8") as f:
        arbre = ast.parse(f.read())
    return {a.name for n in ast.walk(arbre) if isinstance(n, ast.Import) for a in n.names}


class TestNoyau(unittest.TestCase):
    def test_les_moteurs_n_importent_que_de_noyau(self):
        for chemin in MOTEURS:
            with self.subTest(moteur=chemin):
                self.assertNotIn("ensemble_def", {m for m, _, _ in imports_de(chemin)})
                self.assertNotIn("ensemble_def", modules_importes(chemin))

    def test_aucun_nom_prive_importe_du_noyau(self):
        for chemin in MOTEURS:
            for module, nom, _ in imports_de(chemin):
                if module == "noyau":
                    with self.subTest(moteur=chemin, nom=nom):
                        self.assertFalse(nom.startswith("_"), f"{nom} est privé")

    def test_noms_exportes_publics_et_memes_objets(self):
        for module, nom, alias in imports_de("moteur/noyau.py"):
            with self.subTest(nom=nom):
                self.assertEqual(module, "ensemble_def")
                self.assertFalse(alias.startswith("_"), f"{alias} est privé")
                self.assertIs(getattr(noyau, alias), getattr(ensemble_def, nom))

    def test_les_noms_pris_par_les_moteurs_existent_dans_le_noyau(self):
        for chemin in MOTEURS:
            for module, nom, _ in imports_de(chemin):
                if module == "noyau":
                    with self.subTest(moteur=chemin, nom=nom):
                        self.assertTrue(hasattr(noyau, nom))


if __name__ == "__main__":
    unittest.main()
