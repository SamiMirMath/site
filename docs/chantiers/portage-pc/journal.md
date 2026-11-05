# Chantier « Portage PC » — journal

## Lancement de départ (référence)

`python3 tests/lancer.py complet --rapport <scratchpad>/ref-main` sur `main` (c9b257f), sans `PROCESSUS_PAGES` (donc `-n 2`), avant toute
modification : code 0. Python 1317 passés + 1 xfail, 101 952 sous-tests, 96 s ; pages 123 passés, 2 386 sous-tests, 545 s.
Fichiers non suivis pendant le lancement (non lus par les tests) : `docs/architecture.md`, `docs/chantiers/equations-2e-degre/quiz.md`,
`docs/chantiers/portage-pc/diagnostic.md`, `docs/chantiers/revue-structure/rapport.md`.

Comparé à l'ancienne référence `docs/chantiers/tests-rapides/reference` (commit 7268412) : 89 différences Python, 6 de pages, celles déjà
décrites dans le résumé de `tests-rapides` (§0 : réconciliation avec `origin/main`). Ce lancement sert de nouvelle référence (point 2).

## Point 1 — PROCESSUS_PAGES

- Valeurs refusées avec le code 2 et un message, avant tout lancement (rapide, pages, complet) : `''`, `0`, `-1`, `abc`, `4.0`, `' 4'`,
  `04`. Acceptées : absente → 2, `1`, `4`, `12`. `liste` et `verifier` ne lisent pas la variable.
- Commande des pages (fonction `lancer` remplacée par un relevé) : sans la variable, `-n 2` et le reste identique à `main` (complet et
  rapide à corpus réduit) ; avec 4, seul `-n 4` change.
- Suites complètes (`--rapport`, scratchpad) sur l'arbre du point 1 :

| Lancement | Code | Python | Pages | Listes |
|---|---|---|---|---|
| `p1-n4` (`PROCESSUS_PAGES=4`) | 0 | 92 s | **299 s** | identiques à la référence, nom par nom |
| `p1-n2` (absente) | 1 | 94 s | 548 s | test instable du clavier échoué (KaTeX non chargé depuis jsDelivr : `net::ERR_CERT_VERIFIER_CHANGED`, cause réseau) ; relancé seul : passé, 2 sous-tests |
| `p1-n2b` (absente, relancé) | 0 | 87 s | 548 s | identiques à `p1-n4`, nom par nom |

Contrôle de 5a3b737 : `verifier <p1-n4> --reference <ref-main>` : listes identiques nom par nom, empreintes conformes ; REFUSÉ pour le seul
motif (b) (4 fichiers non suivis de l'enseignant dans `docs/`, hors du commit).

## Point 2 — référence du dépôt

- `python3 tests/lancer.py reference <dossier>` accepte un dossier de `complet --rapport` si : les 4 listes et `rapport.json` sont là
  (sinon code 2) ; le commit du lancement existe et est dans l'historique de HEAD ; codes 0 partout, pages lancées ; `CORPUS` et `OUTILS`
  non définis ; JUnit et extension concordants ; aucun fichier modifié ou non suivi, au début ni à la fin du lancement, hors de `docs/` et
  de `CLAUDE.md` (aucun test ne lit ces fichiers : vérifié par recherche dans `tests/python` et `tests/pages`, seulement des mentions dans
  des docstrings). Sinon REFUSÉ (code 1), rien n'est changé. Il affiche les différences avec l'ancienne référence, copie les 4 listes,
  écrit `origine.txt` (commit, dates, durées, environnement, résumé) et garde `soustests-variables.txt` s'il existe.
- Essais : `p1-n4` refusé (`tests/lancer.py` modifié) ; `p1-n2` refusé (codes 1 et `tests/lancer.py`) ; dossier absent : code 2 ; sans
  argument : aide, code 2 ; `ref-main` (c9b257f, `main`) accepté → `tests/reference/` ; relancé : 0 différence.
- `verifier <p1-n4> --commit 5a3b737` sans `--reference` : prend `tests/reference`, identique nom par nom.
- Suite d'avant commit `p2` (`PROCESSUS_PAGES=4`) : code 0 ; Python 94 s, pages 294 s ; identique à `tests/reference` nom par nom.

Contrôle de 012b202 : `verifier <p2>` (référence par défaut, `tests/reference`) : empreintes conformes (10 fichiers testés), listes
identiques ; REFUSÉ pour le seul motif (b) (mêmes 4 fichiers non suivis).

## Point 3 — rapide --depuis

- `git diff --name-only <commit>` (arbre de travail comparé au commit : changements commités depuis, indexés ou non) plus les non
  suivis ; le reste de `rapide` (dépendances, manifeste, pages) est inchangé. Sans l'option : `HEAD`, comme avant.
- Essais (`liste`) : sans option, comme avant ; `--depuis HEAD~1` et `HEAD~2` : fichiers des commits en plus ; `--depuis nimporte` :
  « commit introuvable », code 2 ; `--depuis` sans valeur, `--depui HEAD~1`, `foo` : aide, code 2 ; `--depuis b6aacef~1` (le correctif
  Exp-log touche `exp_log.py`) : tests Python d'Exp-log et pages « tous » (la plage contient aussi `tests/pages/navigateur.py`, P1 de
  tests-rapides).
- Docstring de `verifier.py` : une ligne trop longue du point 2 recoupée (texte inchangé).
- Suite d'avant commit `p3` (`PROCESSUS_PAGES=4`) : code 0 ; Python 98 s, pages 300 s ; identique à `tests/reference` nom par nom.
