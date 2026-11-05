# Chantier « Fondations » — suivi

Branche `fondations` (depuis `main` 96f183c), PC (WSL2), `PROCESSUS_PAGES=4`. Principe : aucun changement visible pour les élèves.
Consigne complète, plan et détails : `journal.md`. La consigne du chantier tient lieu de `decisions.md`.

## État des parties

| Partie | Contenu | État | Commit |
|---|---|---|---|
| F0 | Fiches, référence rafraîchie, `tests/outils/dump_sorties.py`, dump de départ | faite (suite verte) | voir `git log` |
| F1 | `verifier` : docs/ ignoré, baisse de sous-tests justifiée ici ; `test_lancer.py` | faite (suite verte) | voir `git log` |
| F2 | `lancer.py rapide` (reste de R4) : `-z`, supprimés, donnees/, instantanés, pages, références, scripts | faite (suite verte) | voir `git log` |
| F3 | R1 : `tests/python/outils_du_site.py` (registre + manifeste), listes dérivées, clés vérifiées ; exp-log dans `MIGREES` et `test_json_strict` (filière M, exercices), exception nommée pour le jeu moteur | faite (suite verte) | voir `git log` |
| F4 | R6 : `test_noyau` étendu, graphe d'imports figé, noms à plat uniques | à faire | — |
| F5 | R3 : ménage | à faire | — |
| F6 | Copie locale de KaTeX pour les tests de pages | à faire | — |

## Vérification après chaque partie

Dump brut comparé au dump de départ (commande exacte dans `journal.md`, section F0), instantanés et références inchangés, listes de
tests égales à la référence (sauf ajouts annoncés).

## Questions pour l'enseignant

- **F1, `CLAUDE.md` (description de `verifier`, devenue inexacte)** : remplacer « qu'aucun autre fichier n'était modifié ou non suivi
  pendant le lancement (hors suivi.md / journal.md de chantier et CLAUDE.md), que les codes valent 0 et qu'aucun test n'a disparu,
  n'est sauté en plus, ne se dégrade ni ne perd de sous-tests par rapport à la référence (par défaut tests/reference) » par :
  « qu'aucun autre fichier n'était modifié ou non suivi pendant le lancement (hors `docs/`, et CLAUDE.md hors du commit : ignorés,
  toujours listés), que les codes valent 0 et qu'aucun test n'a disparu, n'est sauté en plus ni ne se dégrade par rapport à la
  référence (par défaut tests/reference) ; une baisse de sous-tests n'est acceptée que justifiée dans le suivi.md du chantier
  (section « Variations de sous-tests », ligne `` - `<test>` : <avant> → <après> : <raison> ``, nombres exacts ; `--suivi <fichier>`
  pour un autre fichier) » ; et `verifier <dossier> [--reference <dossier>] [--suivi <fichier>]` en tête de la ligne.

- **F2, `CLAUDE.md` (description de `rapide`, devenue incomplète)** : remplacer « dépendances d'import comprises) plus les tests de
  fumée (manifeste, accueil, source unique) ; » par « dépendances d'import comprises, fichiers supprimés aussi, noms lus avec `-z`)
  plus les tests de fumée (manifeste, accueil, source unique) ; un fichier de `tests/python/donnees/`, d'instantanés ou de références
  de pages relance les tests qui nomment ce dossier (tous s'il n'y en a aucun) ; une page, un `cas*.py` ou un instantané relance aussi
  `test_instantanes*` et `test_json_strict` ; un script de commande (`lancer.py`, `verifier.py`, `comparer_listes.py`,
  `rapport_pytest.py`) relance `test_lancer.py` ; » ; et « dont un moteur Python chargé par la page change » par « dont un moteur
  Python chargé par la page, la référence de page ou l'instantané resoudre change ».

- **F3, `CLAUDE.md` (description de `rapide`)** : ajouter après « un script de commande (…) relance `test_lancer.py` ; » (phrase de
  F2) : « `moteur/manifeste.json` ou `commun/registre.json` relance les dépendants de `tests/python/outils_du_site.py` (la liste des
  outils, dont dérivent les listes des tests) ; » et, dans la liste des scripts de commande, `outils_du_site.py`.

## À relire par l'enseignant

- Aucun instantané ni texte affiché modifié (F0 à F3) ; aucun nouvel instantané.
- **F3, `docs/architecture.md`** (document validé) : § 4 « Ajouter un outil » réécrit (environ 4 fichiers côté site et 10 côté tests,
  tous réclamés par un test ; ce qui dérive désormais) et garde-fou de A3 (« à créer » → les fichiers de F3).
- **F3, exp-log hors du jeu moteur** (`test_instantanes.py`) : exception nommée dans `tests/python/test_outils_du_site.py`
  (`EXCEPTIONS`), raison dans `journal.md` (pas de sortie de moteur unique ; le jeu resoudre C et M couvre l'outil). Répond à la
  question 4 de la revue de structure ; à confirmer.

## Variations de sous-tests

Lue par `verifier` (depuis F1 ; voir sa docstring, point (d)). Format, une ligne par test, commençant en début de ligne par un
tiret : `` - `<identifiant pytest complet>` : <avant> → <après> : <raison> `` (« -> » vaut « → »), par exemple
`` - `tests/python/test_x.py::TestY::test_z` : 120 → 118 : deux entrées en double retirées (F5) ``. <avant> et <après> sont les
nombres de sous-tests passés de la référence et du lancement, exactement ceux que `verifier` affiche ; sinon refus. Une baisse non
justifiée ici fait refuser `verifier` ; un test disparu, échoué ou sauté en plus est refusé même justifié.

(aucune)

## Reprise après compactage

- Lire `CLAUDE.md`, ce fichier, puis `journal.md` (consigne du chantier, plan, section de la dernière partie).
- `git log --oneline main..fondations` : un commit par partie faite.
- Dump de départ : `/tmp/claude-1000/-home-sami-ubuntu-site/b574d683-7da7-4c53-a00c-237ca55256c7/scratchpad/dumps/depart`
  (hors du dépôt ; s'il a disparu, le refaire sur le commit F0 avec `tests/outils/dump_sorties.py`).
