"""Tests rapides, décision T4 : garde du cache `memo` (sorties de l'outil Limites).

Seuls les fichiers de test sans aucun mock importent `memo`, décision par fichier entier (jamais classe par classe) :
- un fichier qui importe `memo` ne contient ni `mock` (dont `unittest.mock`, `MagicMock`), ni `patch`, ni `monkeypatch`, ni
  `setattr` / `delattr` (recherche dans tout le texte, commentaires compris), et n'affecte ni ne supprime aucun attribut d'un module
  du moteur (ou de `memo`) ;
- aucun fichier qui contient un mock n'importe, même de loin (par d'autres modules de `tests/python`), un fichier qui importe `memo` :
  un résultat gardé ne peut donc pas être demandé sous un remplacement ;
- `memo.py` reste dans `tests/python` (aucun moteur ne l'importe) et ne touche à aucun attribut du moteur ;
- la liste des fichiers qui importent `memo` est celle décidée en P4 (`FICHIERS_MEMO`) : en ajouter un est un choix explicite.

Ce fichier n'importe pas `memo` (il contient les mots qu'il cherche). Le comportement du cache (copie profonde, `MEMO=0`) est vérifié
dans `test_memo.py`."""
import ast
import os
import re
import unittest

import outils_du_site
from moteurs import RACINE

ICI = os.path.dirname(os.path.abspath(__file__))
DOSSIERS_MOTEURS = tuple(outils_du_site.dossiers_moteurs())      # dossiers des fichiers du manifeste (F3)
MOCK = re.compile(r"mock|patch|monkeypatch|setattr|delattr", re.IGNORECASE)
IMPORTE_MEMO = re.compile(r"^\s*(?:import\s+memo\b|from\s+memo\s+import\b)", re.MULTILINE)

# P4 (05.11.2026) : les fichiers sans mock qui appellent l'outil Limites, sauf test_proprietes_limites.py (importé par
# test_redaction_limites.py, qui contient des mock) ; plus test_memo.py
FICHIERS_MEMO = {"test_corpus_limites_3m.py", "test_doctrine_bh.py", "test_instantanes.py", "test_limites_deux_cotes.py",
                 "test_racines_reelles.py", "test_rappel_methode.py", "test_redaction_bh_3m.py", "test_resoudre_la.py",
                 "test_tableau_limites.py", "test_memo.py"}


def texte(chemin):
    with open(chemin, encoding="utf-8") as f:
        return f.read()


def modules_tests():
    """{nom de module: chemin} des .py de tests/python."""
    return {n[:-3]: os.path.join(ICI, n) for n in sorted(os.listdir(ICI)) if n.endswith(".py")}


def modules_moteurs():
    return {n[:-3] for d in DOSSIERS_MOTEURS for n in os.listdir(os.path.join(RACINE, d)) if n.endswith(".py")}


def imports_locaux(chemin, locaux):
    """Modules de tests/python importés par le fichier (import x, from x import …)."""
    return set(re.findall(r"^\s*(?:import|from)\s+(\w+)", texte(chemin), re.MULTILINE)) & set(locaux)


def importe_memo(chemin):
    return bool(IMPORTE_MEMO.search(texte(chemin)))


def noms_de_modules(arbre, surveilles):
    """Noms liés par un import à un module surveillé (import la as x ; from moteurs import ensemble_def as ed ;
    from limites_asymptotes import etudier)."""
    noms = set()
    for n in ast.walk(arbre):
        if isinstance(n, ast.Import):
            for a in n.names:
                if a.name.split(".")[0] in surveilles:
                    noms.add((a.asname or a.name).split(".")[0])
        elif isinstance(n, ast.ImportFrom) and n.module:
            for a in n.names:
                if n.module in surveilles or a.name in surveilles:
                    noms.add(a.asname or a.name)
    return noms


def racine(cible):
    while isinstance(cible, (ast.Attribute, ast.Subscript)):
        cible = cible.value
    return cible.id if isinstance(cible, ast.Name) else None


def remplacements(chemin, surveilles):
    """Affectations ou suppressions d'un attribut (ou d'un élément) d'un module surveillé : `la.X = …`, `ed.Y.z += …`, `del la.W`."""
    arbre = ast.parse(texte(chemin))
    noms = noms_de_modules(arbre, surveilles)
    trouves = []
    for n in ast.walk(arbre):
        cibles = (n.targets if isinstance(n, (ast.Assign, ast.Delete)) else
                  [n.target] if isinstance(n, (ast.AugAssign, ast.AnnAssign)) else [])
        for c in cibles:
            for e in (c.elts if isinstance(c, (ast.Tuple, ast.List)) else [c]):
                if isinstance(e, (ast.Attribute, ast.Subscript)) and racine(e) in noms:
                    trouves.append(f"ligne {n.lineno}")
    return trouves


class TestGardeMemo(unittest.TestCase):

    def test_aucun_fichier_qui_importe_memo_ne_contient_de_mock(self):
        locaux = modules_tests()
        utilisateurs = {os.path.basename(c) for nom, c in locaux.items() if nom != "memo" and importe_memo(c)}
        self.assertEqual(utilisateurs, FICHIERS_MEMO)
        surveilles = modules_moteurs() | {"memo"}
        for nom in sorted(utilisateurs):
            with self.subTest(fichier=nom):
                chemin = locaux[nom[:-3]]
                trouves = [f"ligne {texte(chemin)[:m.start()].count(chr(10)) + 1} : {m.group(0)}"
                           for m in MOCK.finditer(texte(chemin))]
                self.assertEqual(trouves, [], "mock dans un fichier qui importe memo")
                self.assertEqual(remplacements(chemin, surveilles), [], "attribut du moteur remplacé")

    def test_aucun_fichier_avec_mock_n_importe_un_fichier_qui_importe_memo(self):
        locaux = modules_tests()
        deps = {nom: imports_locaux(c, locaux) for nom, c in locaux.items()}
        avec_memo = {nom for nom, c in locaux.items() if nom == "memo" or importe_memo(c)}
        for nom, c in locaux.items():
            if not MOCK.search(texte(c)):
                continue
            atteints, a_voir = set(), list(deps[nom])
            while a_voir:
                m = a_voir.pop()
                if m not in atteints:
                    atteints.add(m)
                    a_voir.extend(deps[m])
            with self.subTest(fichier=nom):
                self.assertEqual(sorted(atteints & avec_memo), [], "un fichier avec mock atteint memo")

    def test_memo_reste_un_module_de_test(self):
        self.assertTrue(os.path.exists(os.path.join(ICI, "memo.py")))
        for d in DOSSIERS_MOTEURS:
            for n in sorted(os.listdir(os.path.join(RACINE, d))):
                if n.endswith(".py"):
                    with self.subTest(moteur=f"{d}/{n}"):
                        self.assertFalse(importe_memo(os.path.join(RACINE, d, n)))
        self.assertEqual(remplacements(os.path.join(ICI, "memo.py"), modules_moteurs()), [])


if __name__ == "__main__":
    unittest.main()
