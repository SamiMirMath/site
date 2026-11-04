# Chantier « Tests rapides » — suivi

## Résumé de session

*(À remplir par le chef d'orchestre en fin de session.)*

## Cadre

Branche `tests-rapides`, créée depuis `main` à jour (7268412). Rien n'est poussé ni fusionné.
Ordre de priorité : `CLAUDE.md` > [`decisions.md`](decisions.md) (validé le 04.11.2026) > [`audit.md`](audit.md). Méthode : `docs/methode-chantiers.md`.
Un commit « Tests rapides P{N} : … » par partie, suite complète verte avant chaque commit. Tout le détail (plans, tableaux, temps,
rapports) : [`journal.md`](journal.md).

## État des parties

| Partie | Contenu | État |
|---|---|---|
| P0 | `suivi.md`, `journal.md`, deux lancements de référence, `lancer.py complet --rapport` | **faite** (commit « Tests rapides P0 : … ») |
| P1 | T2 : harnais du toucher (test du clavier) | **faite** (commit « Tests rapides P1 : … ») : test du clavier 20/20 seul et 20/20 sous charge ; listes identiques |
| P2 | T1 : `lancer.py verifier`, texte proposé pour `CLAUDE.md`, méthode (commit séparé) | **faite** (commit « Tests rapides P2 : lancer.py verifier … », `verifier` ACCEPTÉ ; méthode : commit séparé « Tests rapides P2 (méthode) : … ») : commit modifié refusé, fichier non suivi signalé et refusé, test disparu refusé ; listes identiques |
| P3 | T3 : `TestStructure` (calcul une fois par classe) | **faite** (commit « Tests rapides P3 : … ») : copie profonde par test ; fichier seul 121 s → 44 s ; mur Python 670 s ; listes et sous-tests identiques |
| P4 | T4 : `memo.py`, test de garde, `MEMO=0` | à faire |
| P5 | T5 : cache de `racines` | à faire |
| P6 | T7 : `rapide` et pages des moteurs | à faire |
| P7 | T9 : étude du chargement de Pyodide (rapport seul) | à faire |

## Référence (P0)

- Listes du 1ᵉʳ lancement (commit 7268412, code inchangé) : [`reference/`](reference/) — `collecte-{python,pages}.txt`,
  `resultats-{python,pages}.txt` (identifiant, issue, nombre de sous-tests).
- Python : **1312 collectés, 1311 passés, 1 xfail** (`test_P10_pente_au_point_exclu`), 0 sauté, **103 033 sous-tests**.
- Pages : **122 collectés, 122 passés**, 0 xfail, 0 sauté, **2 554 sous-tests**.
- **Sous-tests stables** : identiques test par test entre les deux lancements (Python et pages), sauf le test instable connu du
  clavier, qui a échoué au 2ᵉ lancement (2 → 0 sous-tests) et passe relancé seul (2 sous-tests). Les seuls tirages au hasard des pages
  (`Math.random`, `commun/outil.js:343` et `:363`, « exercice au hasard ») sont dans des tests sans `subTest` : ils ne changent pas les
  nombres. Aucun fichier `reference/soustests-variables.txt` n'est donc nécessaire.
- Comparer un lancement à la référence (code 0 si identique nom par nom) :
  `python3 tests/lancer.py complet --rapport <dossier hors du dépôt>` puis
  `python3 tests/comparer_listes.py docs/chantiers/tests-rapides/reference <dossier>`.
- Murs : Python 737 s puis 755 s ; pages 967 s puis 938 s (détail : `journal.md`, « P0 »).

## Questions pour l'enseignant

- **P2, `rapide` après le commit.** L'audit §M1 prévoit que le chef d'orchestre lance `rapide` après `verifier`. Mais sur l'arbre propre
  d'après le commit, `rapide` ne voit aucun fichier modifié et ne relance que les tests de fumée (3 fichiers). Faut-il lui ajouter une
  base (par exemple `rapide --depuis HEAD~1`, avec P6) ? En attendant (option qui affiche le moins), la méthode dit seulement ce que
  `rapide` relance aujourd'hui.
- **P2, liste permise de `verifier`.** Proposée et justifiée dans `journal.md` (« Règles exactes ») : `docs/chantiers/<chantier>/suivi.md`
  et `journal.md` (écrits après le lancement), `CLAUDE.md` hors du commit. À confirmer.

## À relire par l'enseignant

- P0 : aucun instantané modifié. Outil de test modifié : `tests/lancer.py` (option `complet --rapport` ; sans l'option, mêmes
  commandes et même code de retour) ; nouveaux : `tests/rapport_pytest.py` (extension pytest passive, chargée seulement avec
  `--rapport`) et `tests/comparer_listes.py`.
- P1 : aucun instantané ni aucun test modifié. Harnais modifié : `tests/pages/navigateur.py` (`toucher` : attente d'immobilité avant le
  centrage, recentrage borné à 3 essais, erreur « la touche n'est pas sous le doigt » si `elementFromPoint` n'est pas l'élément visé).
  Coût : `test_clavier.py` 218 s → 241 s ; mur des pages 994 s (P0 : 938 à 967 s). Détail : `journal.md`, « P1 ».
- P2 : aucun instantané ni aucun test modifié. Outil de test modifié : `tests/lancer.py` (commande `verifier` ; `rapport.json` note
  `CORPUS`, `OUTILS`, `MEMO`) ; nouveau : `tests/verifier.py`. Les règles exactes de (a), (b), (c) et la liste permise sont dans
  `journal.md`, « P2 ». Méthode (`docs/methode-chantiers.md`, « Organisation de nuit ») : commit séparé, à relire.
- P3 : aucun instantané ni aucun moteur modifié. Test modifié : `tests/python/test_redaction_bh_3m.py`, classe `TestStructure`
  (`toutes()` : calcul commun gardé par classe, copie profonde par test ; corps des tests inchangés). Détail : `journal.md`, « P3 ».

## À reporter par l'enseignant dans CLAUDE.md

Texte proposé (décision T10 : Claude Code ne modifie pas `CLAUDE.md`), pour la section « Commandes de test », à la place de la ligne
« Mesures du 29.10.2026 … » :

```
- `complet --rapport <dossier>` : comme `complet` (mêmes commandes, même code de retour), et écrit en plus dans <dossier> (hors du
  dépôt, par exemple le scratchpad) les JUnit, les listes de tests (collectés, issues, sous-tests) et rapport.json (commit de départ,
  empreintes des fichiers modifiés ou non suivis au début et à la fin, codes, durées, CORPUS/OUTILS/MEMO). C'est la forme à utiliser
  pour la suite complète d'avant commit dans un chantier.
- `verifier <dossier> [--reference <dossier>]` : après le commit, contrôle sans rien relancer que le rapport porte exactement sur ce
  commit (empreintes), qu'aucun autre fichier n'était modifié ou non suivi pendant le lancement (hors suivi.md / journal.md de chantier
  et CLAUDE.md), que les codes valent 0 et qu'aucun test n'a disparu, n'est sauté en plus, ne se dégrade ni ne perd de sous-tests par
  rapport à la référence (par défaut docs/chantiers/tests-rapides/reference). Verdict final ACCEPTÉ (code 0) ou REFUSÉ (1, ou 2 si un
  fichier manque). `python3 tests/comparer_listes.py <référence> <dossier>` compare deux dossiers nom par nom.
- `MEMO=0` : … (à compléter en P4).
- Mesures du 04.11.2026 sur le Mac de l'enseignant (2 cœurs physiques ; 1312 tests Python et 103 033 sous-tests, 122 tests de pages et
  2 554 sous-tests) : suite Python 715 à 803 s ; suite de pages 938 à 994 s ; `complet` environ 28 à 30 min.
```

Procédure allégée du chef d'orchestre (décision T1 ; écrite aussi dans `docs/methode-chantiers.md`, « Organisation de nuit ») :
1. le sous-agent lance `python3 tests/lancer.py complet --rapport <dossier>` avant son commit et donne `<dossier>` dans son rapport ;
2. le chef d'orchestre : `git log --oneline -3`, puis `python3 tests/lancer.py verifier <dossier>` (`VERDICT : ACCEPTÉ` exigé), puis
   `python3 tests/lancer.py rapide` ; une ligne dans `journal.md`, « Contrôles du chef d'orchestre » ;
3. un test disparu fait refuser `verifier` ; seul un renommage justifié dans `suivi.md` (ancien nom → nouveau nom, raison) est accepté,
   et les parties suivantes se comparent alors au dossier de cette partie (`--reference`) ;
4. une seule suite complète relancée par le chef d'orchestre, en fin de session (et une avec `MEMO=0`, decisions §3).

## Reprise après compactage

P0, P1, P2 (deux commits) et P3 commitées sur `tests-rapides` (rien poussé). Prochaine partie : **P4** (`memo.py`), puis P5 à P7
dans l'ordre de `decisions.md` §3. Contrôle d'une partie : `python3 tests/lancer.py verifier <dossier de complet --rapport>`. Pour reprendre : lire ce fichier, `decisions.md`, puis `git log --oneline main..HEAD` ; le détail est dans
`journal.md`. Chaque partie compare son rapport à `reference/` avec la commande ci-dessus.
