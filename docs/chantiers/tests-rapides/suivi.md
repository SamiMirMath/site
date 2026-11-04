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
| P2 | T1 : `lancer.py verifier`, texte proposé pour `CLAUDE.md`, méthode (commit séparé) | à faire |
| P3 | T3 : `TestStructure` (calcul une fois par classe) | à faire |
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

Aucune pour P0 ni P1.

## À relire par l'enseignant

- P0 : aucun instantané modifié. Outil de test modifié : `tests/lancer.py` (option `complet --rapport` ; sans l'option, mêmes
  commandes et même code de retour) ; nouveaux : `tests/rapport_pytest.py` (extension pytest passive, chargée seulement avec
  `--rapport`) et `tests/comparer_listes.py`.
- P1 : aucun instantané ni aucun test modifié. Harnais modifié : `tests/pages/navigateur.py` (`toucher` : attente d'immobilité avant le
  centrage, recentrage borné à 3 essais, erreur « la touche n'est pas sous le doigt » si `elementFromPoint` n'est pas l'élément visé).
  Coût : `test_clavier.py` 218 s → 241 s ; mur des pages 994 s (P0 : 938 à 967 s). Détail : `journal.md`, « P1 ».

## Reprise après compactage

P0 et P1 commitées sur `tests-rapides` (rien poussé). Prochaine partie : **P2** (`lancer.py verifier`), puis P3 à P7 dans l'ordre de
`decisions.md` §3. Pour reprendre : lire ce fichier, `decisions.md`, puis `git log --oneline main..HEAD` ; le détail est dans
`journal.md`. Chaque partie compare son rapport à `reference/` avec la commande ci-dessus.
