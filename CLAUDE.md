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
  `docs/guide-redaction.md` (R1–R20).

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
- Méthode de travail par chantier : docs/methode-chantiers.md.
- Fiche de chantier : suivi.md reste court (état, questions ouvertes, à
  relire) ; tout le détail (plans, tableaux avant/après, temps, rapports)
  va dans journal.md, que les sous-agents ne lisent qu'en cas de besoin.

# Commandes de test

Toutes se lancent depuis la racine du dépôt avec `python3 tests/lancer.py <commande>` (le script appelle `uv`, qui fournit Python 3.12,
SymPy 1.13.3, mpmath, websockets, pytest et pytest-xdist ; rien n'est installé dans le projet) :

- `rapide` : les tests Python des fichiers modifiés (`git diff HEAD` + fichiers non suivis, dépendances
  d'import comprises) plus les tests de fumée (manifeste, accueil, source unique) ; les tests de pages à corpus réduit si une page, un
  fichier commun ou un test de page est touché, et aussi pour chaque outil dont un moteur Python chargé par la page change (d'après
  `moteur/manifeste.json` : un module partagé relance tous les outils qui le chargent ; toutes les pages si on ne sait pas borner, ou
  si un module du corpus des pages, `cas.py`, `cas_el.py`, `moteurs.py`, change). La page des exponentielles vient avec sa filière M.
  `liste` affiche ce que `rapide` lancerait, sans rien lancer. Pour travailler : ne remplace pas la suite complète avant un commit.
- `rapide --depuis <commit>` (de même `liste --depuis <commit>`) : les fichiers modifiés depuis ce commit (commités ensuite, plus ceux de
  l'arbre et les non suivis) au lieu de `HEAD` ; après un commit, `rapide --depuis HEAD~1` relance les tests de ce commit (contrôle du
  chef d'orchestre, procédure allégée de docs/methode-chantiers.md).
- `complet` : toute la suite Python (`-n auto`) puis toute la suite de pages (`-n` PROCESSUS_PAGES, 2 par défaut, corpus complet). Le
  code de retour est celui de pytest, sans pipe : c'est la commande à lancer avant chaque commit (règle ci-dessus). `python` et `pages` lancent chaque suite seule.
- Ne jamais collecter `tests/python` et `tests/pages` dans la même commande (deux `test_accueil.py`).
- Première installation sur une machine : python3 tests/pages/pyodide_local.py (une fois par version de Pyodide).
- `complet --rapport <dossier>` : comme `complet` (mêmes commandes, même code de retour), et écrit en plus dans <dossier> (hors du
  dépôt, par exemple le scratchpad) les JUnit, les listes de tests (collectés, issues, sous-tests) et rapport.json (commit de départ,
  empreintes des fichiers modifiés ou non suivis au début et à la fin, codes, durées, CORPUS/OUTILS/MEMO). C'est la forme à utiliser
  pour la suite complète d'avant commit dans un chantier.
- `verifier <dossier> [--reference <dossier>]` : après le commit, contrôle sans rien relancer que le rapport porte exactement sur ce
  commit (empreintes), qu'aucun autre fichier n'était modifié ou non suivi pendant le lancement (hors suivi.md / journal.md de chantier
  et CLAUDE.md), que les codes valent 0 et qu'aucun test n'a disparu, n'est sauté en plus, ne se dégrade ni ne perd de sous-tests par
  rapport à la référence (par défaut tests/reference). Verdict final ACCEPTÉ (code 0) ou REFUSÉ (1, ou 2 si un
  fichier manque). `python3 tests/comparer_listes.py <référence> <dossier>` compare deux dossiers nom par nom.
- `reference <dossier>` : remplace la référence du dépôt, `tests/reference/` (celle de `verifier` par défaut), par les listes d'un
  dossier de `complet --rapport` lancé sur un commit de la branche, vert, complet, sans autre fichier modifié que dans `docs/` ou
  CLAUDE.md (sinon REFUSÉ, rien n'est changé). Jamais automatique : à lancer au P0 de chaque chantier, avant toute modification, puis
  commiter `tests/reference/`. docs/chantiers/tests-rapides/reference est une archive.
- `PROCESSUS_PAGES` (variable d'environnement, entier ≥ 1) : nombre de processus (Chrome) de la suite de pages, pour `rapide`, `pages`
  et `complet` ; absente : 2. Sur le Mac (2 cœurs physiques) : 2, donc rien à écrire ; sur le PC : 4
  (`PROCESSUS_PAGES=4 python3 tests/lancer.py complet --rapport <dossier>`). Une valeur invalide arrête la commande avant tout
  lancement (code 2). Les listes de tests sont les mêmes avec 2 et 4.
- `MEMO=0` (variable d'environnement) : coupe les caches de test `tests/python/memo.py` (sorties de l'outil Limites) et
  `tests/python/memo_racines.py` (oracle `racines` des exponentielles et logarithmes), gardés par processus, copie profonde à chaque
  appel : chaque appel devient un appel direct du moteur ou de l'oracle. Ces caches ne servent qu'aux fichiers sans aucun mock
  (`test_memo_garde.py`, `test_memo_racines_garde.py` le vérifient). Une fois par session de chantier, lancer aussi `MEMO=0 python3 tests/lancer.py complet --rapport
  <dossier>` : les listes doivent être les mêmes qu'avec le cache.
- Suite au 05.11.2026 (tests/reference, commit c9b257f) : 1 318 tests Python (dont 1 xfail) et 101 952 sous-tests ; 123 tests de pages
  et 2 386 sous-tests.
- Mesures du 05.11.2026 sur le Mac de l'enseignant (2 cœurs physiques, PROCESSUS_PAGES absente) : suite Python 556 à 588 s (660 s avec
  `MEMO=0`) ; suite de pages 966 à 999 s ; `complet` environ 25 à 27 min (avant le chantier tests-rapides, le 04.11.2026 : Python 737
  à 755 s, pages 938 à 967 s).
- Mesures du 05.11.2026 sur le PC (WSL2 Ubuntu, Ryzen 5 5600X, 6 cœurs physiques) : suite Python 87 à 98 s ; suite de pages 294 à
  300 s avec PROCESSUS_PAGES=4 (544 à 548 s avec 2) ; `complet` environ 6 min 30 s avec 4 (11 min avec 2).
