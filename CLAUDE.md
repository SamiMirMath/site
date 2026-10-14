# Instructions pour Claude

- Avant chaque commit, lancer la suite complète sans pipe (ou avec `set -o pipefail`) et vérifier le
  code de retour ; ne jamais commiter si un test échoue.
- Jamais `git add -A` ni `git add .` : ajouter explicitement les fichiers de la tâche ; jamais de commit
  lancé en arrière-plan ; vérifier `git status` et `git diff --cached` avant chaque commit.
