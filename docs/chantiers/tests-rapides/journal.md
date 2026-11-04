# Chantier « Tests rapides » — journal

Le détail de chaque partie (plans, tableaux, temps, rapports). L'état court est dans [`suivi.md`](suivi.md).

## P0 (04.11.2026) : référence et `lancer.py complet --rapport`

### Plan

1. Collecte (`--collect-only -q`) de chaque suite, séparément, sur le commit de départ 7268412 (code inchangé).
2. 1ᵉʳ lancement de référence, **avant toute modification de code** : mêmes commandes que `lancer.py complet`, plus `--junitxml` et
   l'extension de comptage `rapport_pytest.py` (copie hors du dépôt, chargée par `PYTHONPATH` ; seul moyen d'avoir les sous-tests par
   test, que le JUnit de pytest 9.2 ne note pas).
3. Ajout de l'option `--rapport` à `tests/lancer.py`, de l'extension `tests/rapport_pytest.py` et du script `tests/comparer_listes.py`.
4. 2ᵉ lancement avec `python3 tests/lancer.py complet --rapport <dossier du scratchpad>` (il sert aussi de suite complète avant le commit).
5. Comparaison nom par nom du rapport du 2ᵉ lancement avec les listes du 1ᵉʳ.

### Outils écrits

- **`tests/rapport_pytest.py`** : extension pytest passive, chargée par `-p tests.rapport_pytest --rapport-json=<fichier>`. Elle n'agit
  que dans le processus principal (le contrôleur de xdist reçoit tous les comptes rendus) : collecte (`pytest_xdist_node_collection_finished`),
  issue de chaque test (passé, échoué, erreur, sauté, xfail, xpass) et nombre de sous-tests par test et par issue. Un sous-test en échec
  marque son test « échoué » (pytest 9 laisse le parent « passé »). Rien n'est changé aux tests ; sans `--rapport-json`, elle ne fait rien.
- **`tests/comparer_listes.py`** (sans dépendance, Python du système) :
  - `ecrire_listes` écrit `collecte-<suite>.txt` (un identifiant par ligne, trié) et `resultats-<suite>.txt`
    (« identifiant ⇥ issue ⇥ sous-tests », trié ; sous-tests = nombre de passés, ou `passé:n,échoué:m`) ;
  - `ecarts_junit` recoupe les issues de l'extension avec le JUnit (second témoin ; liste vide si les deux concordent) ;
  - `python3 tests/comparer_listes.py <référence> <dossier>` compare deux dossiers suite par suite : identifiants collectés, issues,
    sous-tests ; code 0 si tout est identique, 1 s'il y a une différence (chacune est listée), 2 s'il manque un fichier. Un fichier
    facultatif `soustests-variables.txt` dans la référence exclurait de la comparaison des sous-tests les tests à tirages variables
    (inutile aujourd'hui : voir plus bas).
- **`tests/lancer.py complet --rapport <dossier>`** : mêmes commandes pytest que `complet`, avec en plus
  `-p tests.rapport_pytest --rapport-json=<dossier>/<suite>.json --junitxml=<dossier>/<suite>.xml` ; pages lancées seulement si Python est
  vert (comme `complet`) ; code de retour inchangé. Le dossier doit être hors du dépôt ou ignoré par git (sinon refus, code 2, rien n'est
  lancé). Il contient ensuite `python.xml`, `pages.xml`, `python.json`, `pages.json`, les listes texte et `rapport.json` :
  `head`, `branche`, `debut`, `fin`, `fichiers_modifies` (empreinte `git hash-object` de chaque fichier modifié ou non suivi au début ;
  `null` pour un fichier supprimé), `fichiers_modifies_fin` (même relevé à la fin, pour voir un fichier changé pendant le lancement),
  par suite : `code`, `duree_s`, `collectes`, `nombres` par issue, `passes`, `xfail`, `sautes`, `autres` (échoués, erreurs, xpass),
  `sous_tests` (par test), `sous_tests_total`, `ecarts_junit` ; et `code` final. Les fichiers d'un lancement précédent dans le même
  dossier sont effacés au départ. Sans l'option, `complet` ne change pas (mêmes arguments, `en_plus` vide).

### Essais de l'option

- `python3 tests/lancer.py complet --rapport docs/chantiers/tests-rapides/essai` (dans le dépôt, non ignoré) : refus, code 2, rien lancé.
- `lancer.python([...test_nombres.py, ...test_roues.py], en_plus=...)` puis `bilan_suite` : 14 passés, 510 sous-tests (= résumé de pytest),
  `ecarts_junit` vide, `-p tests.rapport_pytest` bien chargé dans les workers et le contrôleur.
- `python3 tests/lancer.py liste` : inchangé (les nouveaux fichiers de `tests/` ne déclenchent que la fumée).

### Résultats des deux lancements (commit 7268412)

| | 1ᵉʳ lancement (avant le code) | 2ᵉ lancement (`complet --rapport`) |
|---|---|---|
| Python : mur | **737 s** (pytest : 735 s) | **755 s** (pytest : 753 s) |
| Python : résultat | 1311 passés, 1 xfail, 103 033 sous-tests ; code 0 | 1311 passés, 1 xfail, 103 033 sous-tests ; code 0 |
| Pages : mur | **967 s** (pytest : 966 s) | **938 s** (pytest : 937 s) |
| Pages : résultat | 122 passés, 2 554 sous-tests ; code 0 | 121 passés, **1 échoué** (test instable connu), 2 552 sous-tests ; code 1 |
| JUnit / extension | concordent (0 écart) | concordent (0 écart) |

Collecte (`--collect-only -q`) : 1312 tests Python, 122 tests de pages ; identique à la collecte vue par l'extension dans chacun des
deux lancements. Le seul xfail est `tests/python/test_corpus_etude_complete.py::test_P10_pente_au_point_exclu` (strict, P10 du chantier
Étude complète). Aucun test sauté.

**Test instable connu** : au 2ᵉ lancement, `tests/pages/test_clavier.py::TestClavierIntegre::test_a_deux_formules_aux_touches_donnent_le_corrige_de_la_saisie_directe`
a échoué hors de ses sous-tests, à « effacer » (`AssertionError: '(x^2-1)/(x-3)' != ''`, `test_clavier.py:87` → `toucher_valeur`) :
c'est le symptôme décrit dans l'audit §2. Relancé seul (sans le modifier), avec l'extension : **passé, 2 sous-tests**, 32 s.

**Comparaison** (`python3 tests/comparer_listes.py docs/chantiers/tests-rapides/reference <dossier du 2ᵉ lancement>`) :
- Python : **identique, nom par nom** (collecte, issues, sous-tests de chacun des 1312 tests) ;
- pages : 2 différences, toutes deux sur le test instable du clavier (issue passé → échoué, sous-tests 2 → 0) ; avec sa relance seule
  (passé, 2 sous-tests), les 122 tests sont identiques nom par nom. La vérification propre de P0 est donc faite.

### Stabilité des sous-tests

Identiques test par test entre les deux lancements, pour les deux suites (hors l'échec du test instable). Sources de hasard cherchées :
- pages : `Math.random` de `commun/outil.js` (lignes 343 et 363 : niveau et exercice « au hasard ») ; les tests qui s'en servent
  (`test_comportement.py` : `test_t20_…`, `test_t33_el_exercice_tire_en_python`, `test_t33_el_selecteur_…`, `test_t33_el_case_…`,
  `test_t35_el_exercice_au_hasard_…`) n'ont pas de `subTest` : le hasard change leur durée, pas les nombres ;
- Python : les tests qui tirent au hasard fixent leur graine (`random.seed(2026_10_29)`, `random.Random(n)`), et `factorisation.py`
  ne tire qu'à travers eux.
On ne change rien aux tirages. Pas de `soustests-variables.txt`.

### Sous-tests par fichier (référence)

Pages : `test_accueil` 7 tests / 3 sous-tests ; `test_clavier` 7 / 20 ; `test_comportement` 35 / 1034 ; `test_graphique` 7 / 60 ;
`test_largeurs` 13 / 50 ; `test_pyodide_local` 11 / 0 ; `test_rendu` 7 / 1270 ; `test_simplexe` 35 / 117.

Python (les plus gros) : `test_audit_el` 57 / 18 962 ; `test_redaction_limites` 120 / 12 036 ; `test_vocabulaire` 9 / 11 330 ;
`test_doctrine_bh` 14 / 10 491 ; `test_exercices_el_m` 14 / 9 155 ; `test_exercices_el` 15 / 8 441 ; `test_exp_log` 136 / 4 804 ;
`test_resoudre_el` 37 / 3 263 ; `test_tableau_variations` 24 / 2 992. Le détail test par test est dans `reference/resultats-*.txt`.

### Temps natif

P0 ne touche aucun moteur (`git diff --stat` : `tests/` et `docs/` seulement). Mesure de base, `docs/chantiers/etude-complete/mesurer_temps.py`
(médiane de 3 processus neufs) : Ex7 0,61 s ; a 0,03 s ; b 0,35 s ; c 0,25 s ; d 0,22 s. L'équivalent propre à ce chantier est le mur
des suites (tableau ci-dessus).

### Écarts

- Le 1ᵉʳ lancement n'est pas passé par `lancer.py` (l'option n'existait pas encore) : script du scratchpad, mêmes commandes pytest que
  `complet`, plus `--junitxml` et l'extension (copie identique, alors hors du dépôt, chargée via `PYTHONPATH`).
- `suivi.md` et `journal.md` ont été écrits après le début du 2ᵉ lancement : ils n'apparaissent donc pas dans son `fichiers_modifies`
  (documentation seulement). Les empreintes des fichiers de code (`tests/lancer.py`, `tests/rapport_pytest.py`, `tests/comparer_listes.py`)
  et des listes de référence notées au début du 2ᵉ lancement sont celles du commit.
- Les mesures de `CLAUDE.md` (322 s et 589 s) ne valent plus (suite plus grosse) ; le texte proposé pour `CLAUDE.md` est prévu en P2 (T10).
