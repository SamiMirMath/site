"""Tests rapides, décision T5 : garde du cache `memo_racines` (oracle `racines` de test_exp_log_m), sur le modèle de `test_memo_garde.py`.

- la liste des fichiers qui importent `memo_racines` est celle décidée en P5 (`FICHIERS_MEMO_RACINES`) : en ajouter un est un choix
  explicite ;
- un fichier qui importe `memo_racines` ne contient ni `mock` (dont `unittest.mock`, `MagicMock`), ni `patch`, ni `monkeypatch`, ni
  `delattr` (recherche dans tout le texte, commentaires compris) ; `setattr` n'y sert qu'à ajouter une méthode de test à une classe de
  test définie dans le même fichier (`setattr(TestX, "test_…", …)`, les tranches et familles de l'oracle) ; aucun attribut d'un module
  du moteur, de `memo_racines` ou de `test_exp_log_m` n'y est affecté ni supprimé ;
- aucun fichier qui contient un mock (ou un `setattr` hors de ce cas) n'importe, même de loin, `memo_racines` ou un fichier qui l'importe :
  un résultat gardé ne peut donc pas être demandé sous un remplacement ;
- `memo_racines.py` reste dans `tests/python` (aucun moteur ne l'importe), n'importe pas `memo` et ne touche à aucun attribut.

Ce fichier n'importe pas `memo_racines` (il contient les mots qu'il cherche). Le comportement du cache (copie profonde, `MEMO=0`, clé,
oracle intact) est vérifié dans `test_memo_racines.py`."""
import ast
import os
import re
import unittest
import warnings

from moteurs import RACINE
from test_memo_garde import DOSSIERS_MOTEURS, ICI, imports_locaux, modules_moteurs, modules_tests, remplacements, texte

MOCK_SAUF_SETATTR = re.compile(r"mock|patch|monkeypatch|delattr", re.IGNORECASE)
IMPORTE_MEMO_RACINES = re.compile(r"^\s*(?:import\s+memo_racines\b|from\s+memo_racines\s+import\b)", re.MULTILINE)

# P5 (05.11.2026) : les quatre fichiers qui appellent l'oracle `racines`, plus test_memo_racines.py
FICHIERS_MEMO_RACINES = {"test_exp_log_m.py", "test_exp_log_m_t36.py", "test_exercices_el_m.py", "test_explog_3c.py",
                         "test_memo_racines.py"}


def importe_memo_racines(chemin):
    return bool(IMPORTE_MEMO_RACINES.search(texte(chemin)))


def setattr_hors_classe_de_test(chemin):
    """Les emplois de `setattr` qui ne sont pas `setattr(C, "test_…", …)` avec C une classe de test définie au premier niveau du fichier."""
    with warnings.catch_warnings():                      # un autre fichier de tests peut contenir une séquence « \\c » (SyntaxWarning)
        warnings.simplefilter("ignore", SyntaxWarning)
        arbre = ast.parse(texte(chemin))
    classes = {n.name for n in arbre.body if isinstance(n, ast.ClassDef)
               and any((isinstance(b, ast.Attribute) and b.attr == "TestCase") or (isinstance(b, ast.Name) and b.id == "TestCase")
                       for b in n.bases)}
    appels = {id(n.func) for n in ast.walk(arbre) if isinstance(n, ast.Call)}
    trouves = []
    for n in ast.walk(arbre):
        if isinstance(n, ast.Name) and n.id == "setattr" and id(n) not in appels:
            trouves.append(f"ligne {n.lineno} : setattr hors d'un appel")
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == "setattr":
            cible, nom = (n.args + [None, None])[:2]
            nom_texte = nom.values[0].value if isinstance(nom, ast.JoinedStr) and nom.values and isinstance(nom.values[0], ast.Constant) \
                else nom.value if isinstance(nom, ast.Constant) else ""
            if not (isinstance(cible, ast.Name) and cible.id in classes and str(nom_texte).startswith("test_")):
                trouves.append(f"ligne {n.lineno} : setattr hors d'une classe de test du fichier")
    return trouves


def contient_un_remplacement(chemin):
    return bool(MOCK_SAUF_SETATTR.search(texte(chemin))) or bool(setattr_hors_classe_de_test(chemin))


class TestGardeMemoRacines(unittest.TestCase):

    def test_aucun_fichier_qui_importe_memo_racines_ne_contient_de_mock(self):
        locaux = modules_tests()
        utilisateurs = {os.path.basename(c) for nom, c in locaux.items() if nom != "memo_racines" and importe_memo_racines(c)}
        self.assertEqual(utilisateurs, FICHIERS_MEMO_RACINES)
        surveilles = modules_moteurs() | {"memo_racines", "test_exp_log_m"}
        for nom in sorted(utilisateurs):
            with self.subTest(fichier=nom):
                chemin = locaux[nom[:-3]]
                trouves = [f"ligne {texte(chemin)[:m.start()].count(chr(10)) + 1} : {m.group(0)}"
                           for m in MOCK_SAUF_SETATTR.finditer(texte(chemin))]
                self.assertEqual(trouves, [], "mock dans un fichier qui importe memo_racines")
                self.assertEqual(setattr_hors_classe_de_test(chemin), [])
                self.assertEqual(remplacements(chemin, surveilles), [], "attribut du moteur ou de l'oracle remplacé")

    def test_aucun_fichier_avec_mock_n_importe_un_fichier_qui_importe_memo_racines(self):
        locaux = modules_tests()
        deps = {nom: imports_locaux(c, locaux) for nom, c in locaux.items()}
        avec_memo = {nom for nom, c in locaux.items() if nom == "memo_racines" or importe_memo_racines(c)}
        for nom, c in locaux.items():
            if not contient_un_remplacement(c):
                continue
            atteints, a_voir = set(), list(deps[nom])
            while a_voir:
                m = a_voir.pop()
                if m not in atteints:
                    atteints.add(m)
                    a_voir.extend(deps[m])
            with self.subTest(fichier=nom):
                self.assertEqual(sorted(atteints & avec_memo), [], "un fichier avec mock atteint memo_racines")

    def test_memo_racines_reste_un_module_de_test(self):
        chemin = os.path.join(ICI, "memo_racines.py")
        self.assertTrue(os.path.exists(chemin))
        self.assertFalse(contient_un_remplacement(chemin))
        self.assertNotIn("memo", imports_locaux(chemin, modules_tests()))
        for d in DOSSIERS_MOTEURS:
            for n in sorted(os.listdir(os.path.join(RACINE, d))):
                if n.endswith(".py"):
                    with self.subTest(moteur=f"{d}/{n}"):
                        self.assertFalse(importe_memo_racines(os.path.join(RACINE, d, n)))
        self.assertEqual(remplacements(chemin, modules_moteurs() | {"test_exp_log_m"}), [])


if __name__ == "__main__":
    unittest.main()
