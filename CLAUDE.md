# Instructions pour Claude

## Git
- Toujours une branche dédiée par chantier, créée depuis `main` à jour ; un commit par partie (ou par phase).
- Avant chaque commit, lancer la suite complète (`python3 tests/lancer.py complet`) sans pipe (ou avec
  `set -o pipefail`) et vérifier le code de retour ; ne jamais commiter si un test échoue.
- Jamais `git add -A` ni `git add .` : ajouter explicitement les fichiers de la tâche ; jamais de commit
  lancé en arrière-plan ; vérifier `git status` et `git diff --cached` avant chaque commit.
- Ne jamais pousser ni fusionner : c'est l'enseignant qui le fait (donner la commande de fusion en fin de chantier).
- `docs/reference/` ne doit jamais être commité (il est dans `.gitignore` : jamais de `git add -f`).

## Contenu affiché
- Rien de faux à l'écran : un résultat incertain ou non traité donne un message clair, jamais un résultat douteux.
  Les garde-fous (valeur de référence, replis, sondes numériques) ne sont jamais affaiblis pour faire passer un cas.
- Vouvoiement des élèves dans tout texte qui leur est destiné (R12) ; conventions de rédaction de
  `docs/guide-redaction.md` (R1–R19).

## Mise en page
- Mise en page fluide : cible 390 px (iPhone), filet de sécurité 320–360 px (rien ne déborde ni ne sort de
  l'écran) ; cibles tactiles ≥ 44 px ; composants communs (`commun/composants.css`, `commun/composants.js`)
  plutôt que du code propre à une page (SOC-19, `docs/specifications/socle-commun.md`).

## Tests
- Oracle numérique (`tests/python/oracle.py`) pour les valeurs calculées ; instantanés (`test_instantanes*.py`)
  pour la rédaction ; balayage des largeurs (`tests/pages/test_largeurs.py`, 320 à 1100 px), `CONNUS` vide.
  Toute nouveauté est couverte par l'un de ces tests.

## Suivi
- Une fiche de suivi par chantier : `docs/chantiers/<chantier>/suivi.md`, créée au début, tenue à jour à chaque
  commit (décisions, état des parties, suite verte, écarts), avec une section « Reprise après compactage ».

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
- Fiche de chantier : suivi.md reste court (état, questions ouvertes, à
  relire) ; tout le détail (plans, tableaux avant/après, temps, rapports)
  va dans journal.md, que les sous-agents ne lisent qu'en cas de besoin.
