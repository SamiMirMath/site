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
| P5 | T5 : cache de `racines` | **faite** (commit « Tests rapides P5 : … ») : `memo_racines.py` ; 9 appels de 4 fichiers passent par le cache ; `racines` inchangée (empreinte gardée) ; avec et sans cache : 563 clés, 695 racines, 0 écart ; 11 tests ajoutés ; listes identiques (seuls écarts : les ajouts de P4 et P5) ; Python 570 s (P4 : 660 s) |
| P6 | T7 : `rapide` et pages des moteurs | **faite** (commit « Tests rapides P6 : … ») : un `.py` modifié d'un dossier d'outil ou de `moteur/` relance les pages (corpus réduit) des outils qui le chargent d'après `moteur/manifeste.json`, « tous » si on ne sait pas borner ; filière M avec la page des exponentielles ; `complet` inchangé (commandes identiques octet pour octet) ; suite complète code 0, listes identiques à P5 nom par nom (seuls écarts à la référence : les 17 de P4 et P5) ; Python 588 s, pages 974 s |
| P7 | T9 : étude du chargement de Pyodide (rapport seul) | **faite** (commit « Tests rapides P7 : … ») : rapport [`etude-pyodide.md`](etude-pyodide.md), aucun code modifié ; 122 chargements par suite, 6,9 s à chaud, 18,2 s pour la 1ʳᵉ page de chaque Chrome ; environ 47 % du temps des tests de pages. **Recommandation** : ne pas partager Pyodide entre les tests ; si l'on veut gagner, onglet de réserve puis cache de Chrome gardé d'une classe à la suivante (environ 1,5 min sur la suite de pages) |

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

- **P5, module à part.** Le cache de `racines` est dans `tests/python/memo_racines.py` et non dans `memo.py` : les 4 fichiers appelants
  créent des méthodes de test par `setattr(TestX, "test_…", …)`, mot que la garde de P4 interdit dans un fichier qui importe `memo`.
  La garde de P4 n'est pas touchée ; `test_memo_racines_garde.py` admet `setattr` seulement sous cette forme (classe `TestCase` du
  fichier, nom en `test_`). À confirmer.

- **P6, filière M.** `rapide` ajoute `exponentielles-logarithmes-M` à `OUTILS` dès que la page des exponentielles est relancée (moteur
  ou page) : sans ce nom, `test_rendu.py::test_exponentielles_logarithmes_filiere_m` était sauté, aussi pour une page modifiée (avant
  P6). Un test de plus, jamais de moins. À confirmer.
- **P6, corpus des pages.** Un module de `tests/python` importé par les tests de pages (`cas.py`, `cas_el.py`, `moteurs.py`) relance
  maintenant toutes les pages (corpus réduit), comme un fichier de `tests/pages/`. Un `.py` d'un dossier d'outil que le manifeste ne
  cite pas (`moteur/construire_roues.py`, nouveau fichier) donne aussi « tous » (option la plus sûre). À confirmer.
- **P6, pas de test dans la suite.** La règle de `rapide` n'est couverte par aucun test de la suite (les listes doivent rester celles de
  la référence + 17) : seulement par le banc de simulations noté dans `journal.md`, « P6 ». Faut-il un test (`test_lancer.py`) dans un
  chantier suivant ?
- **P6 et `--depuis`.** P6 rend `--depuis HEAD~1` **plus utile** (il relancerait aussi les pages des moteurs du commit, au prix de
  quelques minutes de plus) ; toujours pas ajouté (non tranché).

- **P7, Pyodide (décision à prendre, `etude-pyodide.md` §5).** Faire dans une partie suivante (a) l'onglet de réserve (environ 35 s,
  risque très faible, `navigateur.py` seul) ? (b) le cache de Chrome gardé d'une classe à la suivante (environ 45 à 60 s), ou rouvrir
  T8 (Chrome partagé) au vu des mesures (T8 ne comptait pas les 11 s de la 1ʳᵉ page à froid de chaque Chrome) ? Confirmer l'abandon
  du partage de Pyodide entre les tests (M8). Hors chantier : la pause de 0,7 s avant SymPy et `invalidate_caches` (0,3 s), qui
  coûtent aussi à l'élève. En attendant (option qui affiche le moins) : rien n'est changé.

## Injectivité de la clé (P5, décision T5)

Clé de `memo_racines.racines(s)` = (contexte de l'oracle, instantané de `s`). L'instantané est un tuple immuable qui commence par le
**type exact** de chaque objet et contient **tous** ses champs (nœuds d'`exp_log` d'une liste fermée, sans sous-classe ni `__dict__` ;
`Saisie` entière ; `Fraction` par numérateur et dénominateur ; `str` ; `None` ; `tuple`) ; tout autre type (flottant, entier, booléen,
SymPy…) n'a pas de clé et l'oracle est appelé directement. Le contexte contient les fonctions `racines`, `ecart`, `evaluer`, l'objet `MP`
avec sa précision et son arrondi, et les classes que lit `evaluer`. Deux clés égales désignent donc des arguments indiscernables, le même
code et le même contexte ; `racines` (un seul paramètre, sans défaut) étant déterministe, le résultat est le même. Démonstration
détaillée et pièges écartés (1 == 1.0 == True, assomptions SymPy, arbre modifié après l'appel) : `journal.md`, « P5 », « Clé ».

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

- P5 : aucun instantané ni aucun moteur modifié ; `racines`, `ecart`, `evaluer` inchangées. Nouveaux : `tests/python/memo_racines.py`,
  `tests/python/test_memo_racines.py`, `tests/python/test_memo_racines_garde.py`. Tests modifiés (seulement `racines(s)` →
  `memo_racines.racines(s)` et les imports) : `test_exp_log_m`, `test_exp_log_m_t36`, `test_exercices_el_m`, `test_explog_3c`.
  Détail : `journal.md`, « P5 ».

- P6 : aucun instantané, aucun test ni aucun moteur modifié. Outil de test modifié : `tests/lancer.py` (chemin de `rapide` / `liste`
  seulement : `outils_des_moteurs`, `corpus_des_pages`, `outils_de_pages`). Simulations avant / après et preuve de `complet` inchangé :
  `journal.md`, « P6 ».

- P7 : aucun instantané, aucun test, aucun code modifié. Nouveau : [`etude-pyodide.md`](etude-pyodide.md) (mesures, options classées,
  recommandation, décisions). Mesures et scripts : `journal.md`, « P7 ».

## À reporter par l'enseignant dans CLAUDE.md

Texte proposé (décision T10 : Claude Code ne modifie pas `CLAUDE.md`), pour la section « Commandes de test », à la place de la ligne
« Mesures du 29.10.2026 … » :

```
- `rapide` (à la place de la ligne actuelle) : les tests Python des fichiers modifiés (`git diff HEAD` + fichiers non suivis, dépendances
  d'import comprises) plus les tests de fumée (manifeste, accueil, source unique) ; les tests de pages à corpus réduit si une page, un
  fichier commun ou un test de page est touché, et aussi pour chaque outil dont un moteur Python chargé par la page change (d'après
  `moteur/manifeste.json` : un module partagé relance tous les outils qui le chargent ; toutes les pages si on ne sait pas borner, ou
  si un module du corpus des pages, `cas.py`, `cas_el.py`, `moteurs.py`, change). La page des exponentielles vient avec sa filière M.
  `liste` affiche ce que `rapide` lancerait, sans rien lancer. Pour travailler : ne remplace pas la suite complète avant un commit.
- `complet --rapport <dossier>` : comme `complet` (mêmes commandes, même code de retour), et écrit en plus dans <dossier> (hors du
  dépôt, par exemple le scratchpad) les JUnit, les listes de tests (collectés, issues, sous-tests) et rapport.json (commit de départ,
  empreintes des fichiers modifiés ou non suivis au début et à la fin, codes, durées, CORPUS/OUTILS/MEMO). C'est la forme à utiliser
  pour la suite complète d'avant commit dans un chantier.
- `verifier <dossier> [--reference <dossier>]` : après le commit, contrôle sans rien relancer que le rapport porte exactement sur ce
  commit (empreintes), qu'aucun autre fichier n'était modifié ou non suivi pendant le lancement (hors suivi.md / journal.md de chantier
  et CLAUDE.md), que les codes valent 0 et qu'aucun test n'a disparu, n'est sauté en plus, ne se dégrade ni ne perd de sous-tests par
  rapport à la référence (par défaut docs/chantiers/tests-rapides/reference). Verdict final ACCEPTÉ (code 0) ou REFUSÉ (1, ou 2 si un
  fichier manque). `python3 tests/comparer_listes.py <référence> <dossier>` compare deux dossiers nom par nom.
- `MEMO=0` (variable d'environnement) : coupe les caches de test `tests/python/memo.py` (sorties de l'outil Limites) et
  `tests/python/memo_racines.py` (oracle `racines` des exponentielles et logarithmes), gardés par processus, copie profonde à chaque
  appel : chaque appel devient un appel direct du moteur ou de l'oracle. Ces caches ne servent qu'aux fichiers sans aucun mock
  (`test_memo_garde.py`, `test_memo_racines_garde.py` le vérifient). Une fois par session de chantier, lancer aussi `MEMO=0 python3 tests/lancer.py complet --rapport
  <dossier>` : les listes doivent être les mêmes qu'avec le cache.
- Mesures du 04.11.2026 sur le Mac de l'enseignant (2 cœurs physiques ; 1312 tests Python et 103 033 sous-tests, 122 tests de pages et
  2 554 sous-tests) : suite Python 715 à 803 s ; suite de pages 938 à 994 s ; `complet` environ 28 à 30 min.
```

Procédure allégée du chef d'orchestre (décision T1 ; écrite aussi dans `docs/methode-chantiers.md`, « Organisation de nuit ») :
1. le sous-agent lance `python3 tests/lancer.py complet --rapport <dossier>` avant son commit et donne `<dossier>` dans son rapport ;
2. le chef d'orchestre : `git log --oneline -3`, puis `python3 tests/lancer.py verifier <dossier>` (`VERDICT : ACCEPTÉ` exigé), puis
   `python3 tests/lancer.py rapide` (sur l'arbre propre d'après le commit : tests de fumée seulement) ; une ligne dans `journal.md`, « Contrôles du chef d'orchestre » ;
3. un test disparu fait refuser `verifier` ; seul un renommage justifié dans `suivi.md` (ancien nom → nouveau nom, raison) est accepté,
   et les parties suivantes se comparent alors au dossier de cette partie (`--reference`) ;
4. une seule suite complète relancée par le chef d'orchestre, en fin de session (et une avec `MEMO=0`, decisions §3).

## Reprise après compactage

P0 à P7 (P2 en deux commits) commitées sur `tests-rapides` (rien poussé). Toutes les parties de `decisions.md` §3 sont faites ; reste la
fin de session du chef d'orchestre (suite complète normale, puis avec `MEMO=0`, comparaison à la référence, résumé). Contrôle d'une partie : `python3 tests/lancer.py verifier <dossier de complet --rapport>`. Pour reprendre : lire ce fichier, `decisions.md`, puis `git log --oneline main..HEAD` ; le détail est dans
`journal.md`. Chaque partie compare son rapport à `reference/` avec la commande ci-dessus.
