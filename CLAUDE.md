# Instructions pour Claude

- Avant chaque commit, lancer la suite complète sans pipe (ou avec `set -o pipefail`) et vérifier le
  code de retour ; ne jamais commiter si un test échoue.
- Jamais `git add -A` ni `git add .` : ajouter explicitement les fichiers de la tâche ; jamais de commit
  lancé en arrière-plan ; vérifier `git status` et `git diff --cached` avant chaque commit.

# Commandes de test

Toutes se lancent depuis la racine du dépôt avec `python3 tests/lancer.py <commande>` (le script appelle `uv`, qui fournit Python 3.12,
SymPy 1.13.3, mpmath, websockets, pytest et pytest-xdist ; rien n'est installé dans le projet) :

- `rapide` : les tests Python des fichiers modifiés (`git diff HEAD` + fichiers non suivis, dépendances d'import comprises) plus les tests de
  fumée (manifeste, accueil, source unique) ; si une page, un fichier commun ou un test de page est touché, les tests de pages à corpus réduit.
  `liste` affiche ce que `rapide` lancerait, sans rien lancer. Pour travailler : ne remplace pas la suite complète avant un commit.
- `complet` : toute la suite Python (`-n auto`) puis toute la suite de pages (`-n 2`, corpus complet). Le code de retour est celui de pytest,
  sans pipe : c'est la commande à lancer avant chaque commit (règle ci-dessus). `python` et `pages` lancent chaque suite seule.
- Ne jamais collecter `tests/python` et `tests/pages` dans la même commande (deux `test_accueil.py`).
- Mesures du 29.10.2026 sur le Mac de l'enseignant (2 cœurs physiques) : suite Python 595 s → 322 s ; suite de pages 1 102 s → 589 s.
