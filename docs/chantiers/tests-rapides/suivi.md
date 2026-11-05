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
| P4 | T4 : `memo.py`, test de garde, `MEMO=0` | **faite** (commit « Tests rapides P4 : … ») : 9 fichiers sans mock passent par `memo` ; 6 tests ajoutés (`test_memo.py`, `test_memo_garde.py`) ; listes identiques avec et sans `MEMO=0` (seuls écarts à la référence : les 6 ajoutés) ; Python 660 s (cache) / 672 s (`MEMO=0`) |
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

- **P4, `test_doctrine_bh.py`.** Il ne contient aucun mock et importe `memo`, mais il importe aussi `TestStyle` de
  `test_redaction_limites.py` (qui contient des mock), classe recollectée dans `test_doctrine_bh` (9 tests, sans mock, qui appellent
  `la.etudier` directement). Lecture retenue : la décision T4 porte sur le texte du fichier. La garde interdit seulement le sens dangereux
  (un fichier avec mock qui atteint un fichier qui importe `memo`), d'où l'exclusion de `test_proprietes_limites.py`. À confirmer.
- **P4, gain.** 20 s de mur sur le groupe des fichiers concernés, 12 s dans la suite complète (dans le bruit) : bien moins que l'audit
  (1 à 1,5 min), car les gros appelants de l'outil Limites ont des mock. Garder le cache tel quel ?

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

- P4 : aucun instantané ni aucun moteur modifié. Nouveaux : `tests/python/memo.py`, `tests/python/test_memo.py`,
  `tests/python/test_memo_garde.py`. Tests modifiés (seulement `la.etudier(…)` → `memo.etudier_la(…)`, et l'import) : `test_corpus_limites_3m`,
  `test_doctrine_bh`, `test_instantanes`, `test_limites_deux_cotes`, `test_racines_reelles`, `test_rappel_methode`, `test_redaction_bh_3m`,
  `test_resoudre_la`, `test_tableau_limites`. Détail : `journal.md`, « P4 ».

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
- `MEMO=0` (variable d'environnement) : coupe le cache de test `tests/python/memo.py` (sorties de l'outil Limites, gardées par processus,
  copie profonde à chaque appel) : chaque appel devient un appel direct du moteur. Le cache ne sert qu'aux fichiers sans aucun mock
  (`test_memo_garde.py` le vérifie). Une fois par session de chantier, lancer aussi `MEMO=0 python3 tests/lancer.py complet --rapport
  <dossier>` : les listes doivent être les mêmes qu'avec le cache.
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

P0, P1, P2 (deux commits), P3 et P4 commitées sur `tests-rapides` (rien poussé). Prochaine partie : **P5** (cache de `racines`), puis P6 et P7
dans l'ordre de `decisions.md` §3. Contrôle d'une partie : `python3 tests/lancer.py verifier <dossier de complet --rapport>`. Pour reprendre : lire ce fichier, `decisions.md`, puis `git log --oneline main..HEAD` ; le détail est dans
`journal.md`. Chaque partie compare son rapport à `reference/` avec la commande ci-dessus.
