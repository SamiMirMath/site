"""T11 — moteur/noyau.py : interface publique du noyau (ensemble_def.py).

Les moteurs des outils n'importent que de `noyau`, et aucun nom commençant par « _ » ne
traverse la frontière du noyau. `noyau` ne fait que réexporter : mêmes objets que ceux de
ensemble_def (donc mêmes comportements, mêmes instantanés).

Chantier fondations, F4 (revue de structure, R6) : MOTEURS étendu à redaction_bh, exp_log et
exp_log_m ; `test_tous_les_moteurs_d_outil_sont_surveilles` réclame tout nouveau moteur d'outil
(fichier du manifeste ou de son dossier). Le graphe complet des imports est figé par
test_imports.py (règle A1 de docs/architecture.md)."""
import ast
import os
import unittest

import moteurs  # noqa: F401  (chemins des moteurs)
from moteurs import RACINE

import ensemble_def
import noyau
import outils_du_site

MOTEURS = [
    "derivee-variations/derivee_variations.py",
    "limites-asymptotes/limites_asymptotes.py",
    "etude-complete/etude_complete.py",
    "etude-complete/parties.py",
    "factorisation/factorisation.py",
    "limites-asymptotes/redaction_bh.py",                # F4 (R6)
    "exponentielles-logarithmes/exp_log.py",             # F4 (R6)
    "exponentielles-logarithmes/exp_log_m.py",           # F4 (R6)
    "equations-2e-degre/equations.py",                   # equations-2e-degre, P5
]
# dossier de la base (ensemble_def.py) et de son adaptateur : ils la prennent directement, sans noyau (resoudre_ed, légitime)
DOSSIER_DE_LA_BASE = "ensemble-definition"


def moteurs_d_outil():
    """Moteurs d'outil (couche 2 de docs/architecture.md) : les .py des dossiers d'outil du manifeste, sauf l'adaptateur de
    l'outil (son `module`) et le dossier de la base."""
    manifeste = outils_du_site.manifeste()
    moteurs = set()
    for dossier in outils_du_site.dossiers_moteurs():
        if dossier == "moteur" or dossier == DOSSIER_DE_LA_BASE:
            continue
        adaptateur = manifeste[dossier]["module"] + ".py" if dossier in manifeste else None
        moteurs |= {f"{dossier}/{nom}" for nom in os.listdir(os.path.join(RACINE, dossier))
                    if nom.endswith(".py") and nom != adaptateur}
    return moteurs


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

    def test_tous_les_moteurs_d_outil_sont_surveilles(self):
        """F4 : un nouveau moteur d'outil (fichier .py d'un dossier du manifeste, hors adaptateur) doit entrer dans MOTEURS."""
        self.assertEqual(moteurs_d_outil() - set(MOTEURS), set(), "à ajouter à MOTEURS (tests/python/test_noyau.py)")
        self.assertEqual(set(MOTEURS) - moteurs_d_outil(), set(), "MOTEURS nomme un fichier qui n'est pas un moteur d'outil")

    def test_les_noms_pris_par_les_moteurs_existent_dans_le_noyau(self):
        for chemin in MOTEURS:
            for module, nom, _ in imports_de(chemin):
                if module == "noyau":
                    with self.subTest(moteur=chemin, nom=nom):
                        self.assertTrue(hasattr(noyau, nom))


if __name__ == "__main__":
    unittest.main()
