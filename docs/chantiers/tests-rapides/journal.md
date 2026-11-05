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

## P1 (04.11.2026) : harnais du toucher (T2)

### Plan

1. `tests/pages/navigateur.py` seulement (audit §2.3, décision T2) ; ni la page, ni `test_clavier.py`, ni aucun autre test ne changent :
   - `Page._centre_immobile` : attendre l'immobilité **avant** le `scrollIntoView` (un défilement doux de la page en cours ne se bat plus
     avec le défilement instantané du harnais) ; après l'immobilité, vérifier que le rectangle de l'élément est **entièrement dans
     l'écran** ; sinon recentrer et attendre de nouveau, **3 essais au plus** ;
   - `Page.toucher` : avant l'appui, vérifier que `document.elementFromPoint(x, y)` est l'élément visé ou l'un de ses descendants ;
     sinon lever une erreur explicite (« la touche n'est pas sous le doigt »), au lieu d'un appui perdu.
2. Vérification propre : `test_a_deux_formules…` lancé 20 fois seul, puis 20 fois sous charge (2 processus qui occupent le processeur),
   chaque lancement sous `subprocess` avec une limite de 5 min ; 40 sur 40 exigés, sinon la partie est un échec.
3. Temps de `test_clavier.py` avant / après (le recentrage ajoute au plus une attente d'immobilité de 0,3 s par appui).
4. Suite complète `--rapport` (code 0), `comparer_listes.py` contre `reference/` (identique nom par nom), `--collect-only -q` de chaque
   suite comparé à la référence ; murs notés ici.
5. `suivi.md` (état de P1), commit « Tests rapides P1 : … ».

### Code

`tests/pages/navigateur.py` seulement (la page, `test_clavier.py` et les autres tests sont inchangés) :
- nouvelle `Page._immobile(position)` : la boucle d'immobilité d'avant, sortie telle quelle (6 mesures identiques à 50 ms, 10 s au plus) ;
- `Page._centre_immobile` : une attente d'immobilité **avant** le centrage, puis jusqu'à **3** centrages (`scrollIntoView` instantané,
  puis attente d'immobilité) ; on s'arrête dès que le rectangle de l'élément est entièrement dans la partie visible
  (`0 ≤ left, top` et `right ≤ clientWidth`, `bottom ≤ clientHeight`). Après 3 essais, on rend le centre mesuré : c'est le contrôle de
  `toucher` qui décide ;
- `Page.toucher` : avant l'appui, `document.elementFromPoint(x, y)` doit être l'élément visé ou l'un de ses descendants ; sinon
  `ErreurPage("la touche n'est pas sous le doigt : <sélecteur> visé en (x, y), sous le doigt : <élément trouvé ou « aucun élément »>")`.
- `Page.glisser` profite du recentrage (même `_centre_immobile`) ; le contrôle `elementFromPoint` n'y est pas ajouté (audit §2.3 : `toucher`).

Sonde du contrôle (scratchpad, hors du dépôt) : page du simplexe en tactile, un `div` fixe posé sur toute la page, `toucher("#launch")`
→ `ErreurPage : la touche n'est pas sous le doigt : #launch visé en (82, 725), sous le doigt : <div id="cache" …>` ; cache retiré,
même appui accepté. Le contrôle n'est donc pas vide.

### Vérification propre (test du clavier, 40 lancements)

`tests/pages/test_clavier.py::TestClavierIntegre::test_a_deux_formules_aux_touches_donnent_le_corrige_de_la_saisie_directe`, chaque
lancement dans son propre processus pytest sous `subprocess` (limite 5 min), par lots de 5 (seul) ou de 4 (sous charge) :

| | Lancements | Réussites | Durée d'un lancement |
|---|---|---|---|
| Seul | 20 | **20** (1 passé, 2 sous-tests, à chaque fois) | 41,2 à 43,1 s |
| Sous charge (2 processus `while True: pass` pendant tout le lot) | 20 | **20** (1 passé, 2 sous-tests, à chaque fois) | 49,7 à 52,8 s |

**40 sur 40.** Autres tests tactiles avec le nouveau harnais : `test_simplexe.py -k "test_f_ or test_g_"` : 8 passés (53 s).

Temps de `test_clavier.py` entier (7 tests, 20 sous-tests), seul : 218 s avant, 241 s après (+ 23 s, environ 0,35 s de plus par appui :
l'attente d'immobilité avant le centrage).

### Suite complète (`complet --rapport`, HEAD 1feb6cf + `navigateur.py` modifié)

| | Mur (pytest) | Résultat |
|---|---|---|
| Python | **715 s** | 1311 passés, 1 xfail, 103 033 sous-tests ; code 0 ; JUnit / extension : 0 écart |
| Pages | **994 s** (993 s) | 122 passés, 2 554 sous-tests ; code 0 ; JUnit / extension : 0 écart |

Code global 0. `python3 tests/comparer_listes.py docs/chantiers/tests-rapides/reference <P1-rapport>` : Python et pages **identiques,
nom par nom** (code 0). `--collect-only -q` de chaque suite, lancée séparément : 1312 et 122 identifiants, **identiques** à
`reference/collecte-*.txt`. Empreintes notées au début et à la fin du lancement : `navigateur.py` 52a0966…, `journal.md` (plan seul).

Mur des pages : 994 s contre 938 à 967 s en P0 (+ 3 à 6 %), cohérent avec le surcoût du toucher (`test_clavier` + 23 s) et le bruit
de mesure.

### Temps natif

P1 ne touche aucun moteur. `mesurer_temps.py` : Ex7 0,59 s ; a 0,03 s ; b 0,36 s ; c 0,25 s ; d 0,22 s (P0 : 0,61 ; 0,03 ; 0,35 ;
0,25 ; 0,22) : aucune hausse.

### Écarts

Aucun. Charge de la vérification : deux processus qui occupent chacun un cœur, comme dans l'audit §2.2 (« 2 processus qui occupent le
processeur, comme à `-n 2` »).

## P2 (04.11.2026) : `lancer.py verifier` (T1) et méthode (T10)

### Plan

1. Nouveau module `tests/verifier.py` (sans dépendance, Python du système, comme `comparer_listes.py`), appelé par
   `python3 tests/lancer.py verifier <dossier> [--reference <dossier>] [--commit <rév>]` ; il relit le dossier écrit par
   `complet --rapport` et contrôle, après le commit, les points (a), (b), (c) de l'audit §M1 et de la décision T1 (règles exactes
   ci-dessous). Verdict final explicite ; code 0 = accepté, 1 = refusé, 2 = dossier ou fichier manquant (refusé aussi).
2. `complet --rapport` note en plus dans `rapport.json` les variables `CORPUS`, `OUTILS` et `MEMO` (environnement du lancement).
3. Essais sur les rapports déjà écrits (P1, contrôle du chef d'orchestre sur a8d6ab6), avant la suite complète.
4. Suite complète `--rapport` vers `…/scratchpad/P2-rapport`, `comparer_listes.py`, `--collect-only -q` des deux suites.
5. `suivi.md` (état, texte proposé pour `CLAUDE.md`, procédure allégée), commit 1, puis `verifier` sur ce commit (doit accepter).
6. Les trois essais de l'audit §M1 sur des copies du dossier P2-rapport et sur une branche jetable (supprimée ensuite) ; notés ici.
7. Commit 2 (séparé, T10) : `docs/methode-chantiers.md`, « Organisation de nuit » ; suite complète `--rapport` vers
   `…/scratchpad/P2b-rapport` avant le commit, puis `verifier` sur le commit 2.

### Code

- **`tests/verifier.py`** (nouveau, sans dépendance, comme `comparer_listes.py`, dont il réutilise les lecteurs) ; appelé par
  `python3 tests/lancer.py verifier <dossier> [--reference <dossier>] [--commit <rév>]`. Il ne relance aucun test.
- **`tests/lancer.py`** : commande `verifier` (renvoi à `verifier.main`) ; `complet --rapport` note en plus dans `rapport.json`
  `environnement` = valeurs de `CORPUS`, `OUTILS` et `MEMO` au lancement (`null` si non définies). Sans `--rapport`, `complet` ne change pas.
- `--commit <rév>` (par défaut `HEAD`) sert à vérifier un commit plus ancien (essais ci-dessous sur les rapports de P0 et P1) ;
  `--reference <dossier>` désigne la référence de la partie précédente quand ce n'est plus `reference/` (après un renommage accepté).

### Règles exactes de `verifier`

Notations : D = commit de départ du lancement (`head` de `rapport.json`) ; C = commit vérifié (`HEAD`) ; M = empreintes
`git hash-object` des fichiers modifiés (indexés ou non) ou non suivis **au début** du lancement (`fichiers_modifies`, `null` =
supprimé) ; F = le même relevé **à la fin** (`fichiers_modifies_fin`). Les fichiers ignorés par git (`.gitignore`) n'y sont jamais.

**(a) Le commit.**
- C = D (aucun commit depuis le lancement), ou C a **un seul parent**, et c'est D. Sinon REFUS (« ni le commit de départ ni son enfant
  direct ») : un commit de plus, une fusion ou un commit modifié (`--amend` après un autre commit) sont refusés.
- Pour chaque fichier changé entre D et C (`git diff --no-renames --name-only D C`) : il doit être dans M, avec dans C
  (`git rev-parse C:<fichier>`) l'empreinte notée dans M (absent de C s'il est noté supprimé), et la même empreinte dans F (pas changé
  pendant le lancement). Sinon REFUS, avec le motif : « non testé » (absent de M), « empreinte différente », « changé pendant le lancement ».
- Ensemble, (a) et (b) disent que C contient **exactement** les fichiers de M, avec les empreintes testées, à la liste permise près.

**(b) Les autres fichiers.** Tout fichier de M ou de F qui n'est **pas** changé entre D et C (modifié, non suivi, ou apparu pendant le
lancement, puis laissé hors du commit) fait REFUSER : la suite a tourné avec un état local que le commit ne contient pas.

**Liste permise** (seulement listée, jamais refusée) — deux règles, rien d'autre :
1. `DOCS_APRES` = `docs/chantiers/<chantier>/suivi.md` et `docs/chantiers/<chantier>/journal.md`, dans (a) comme dans (b). Raison : le
   sous-agent y écrit les murs et les résultats **après** le lancement (P0 et P1 l'ont fait : `suivi.md` absent de M, `journal.md` changé
   ensuite). Aucun test ne lit `docs/chantiers/` : `grep` des tests (les seules mentions sont des docstrings), et les deux `os.walk` de
   `test_accueil.py` écartent `docs/`.
2. `PERMIS_HORS_COMMIT` = `CLAUDE.md`, dans (b) seulement (audit §M1 : l'enseignant peut être en train de le modifier). Aucun test n'en
   lit le contenu ; `test_les_fichiers_internes_ne_sont_pas_publies` n'en voit que le nom, qui ne change pas. Dans un commit, `CLAUDE.md`
   reste soumis à la règle (a) (le sous-agent ne le modifie pas).

**(c) Les résultats.**
- Codes : `code` global, Python et pages valent 0, et les pages ont été lancées.
- Environnement : `CORPUS` et `OUTILS` non définis au lancement (sinon la suite n'est pas complète) ; `MEMO` est affiché (P4). Un rapport
  antérieur à P2 (sans `environnement`) le signale.
- Concordance des témoins du dossier : listes texte (`collecte-*`, `resultats-*`) = listes de `rapport.json` (passés, xfail, sautés,
  autres ; nombre de collectés) ; JUnit (`python.xml`, `pages.xml`) = listes texte (`comparer_listes.ecarts_junit`) ; `ecarts_junit` de
  `rapport.json` vide. Un dossier retouché à la main d'un seul côté est refusé.
- Comparaison avec la référence (par défaut `docs/chantiers/tests-rapides/reference/`, ou `--reference <dossier>`), suite par suite,
  nom par nom. REFUS si : un identifiant collecté, ou un résultat, **disparaît** ; un test est **sauté en plus** (sauté alors qu'il ne
  l'était pas, ou nouveau et sauté) ; une **issue change**, sauf xfail → passé et sauté → passé (acceptées, listées) ; un test a des
  sous-tests en échec ; le nombre de **sous-tests passés** d'un test **baisse** (sauf tests de `soustests-variables.txt`, aucun
  aujourd'hui). Accepté mais **listé** : un test **ajouté** (passé ou xfail), un nombre de sous-tests en hausse.
- Sortie : un résumé de quelques lignes ((a), (b), (c) par suite), les listes acceptées, les motifs de refus avec leurs éléments (25 au
  plus par motif, le compte reste exact), puis `VERDICT : ACCEPTÉ (code 0)` ou `VERDICT : REFUSÉ (code 1) : n motif(s)` ;
  code 2 (REFUSÉ aussi) si un fichier du dossier ou de la référence manque.

### Essais de mise au point (rapports déjà écrits, avant la suite complète)

| Dossier | Commit vérifié | Verdict | Motif / remarque |
|---|---|---|---|
| contrôle du chef sur P1 (départ a8d6ab6, arbre propre) | a8d6ab6 (= D) | ACCEPTÉ | 0 fichier ; listes identiques |
| P1 du sous-agent (départ 1feb6cf ; M = `navigateur.py`, `journal.md`) | a8d6ab6 (enfant) | ACCEPTÉ | `navigateur.py` conforme ; `journal.md`, `suivi.md` listés |
| même dossier | 1feb6cf (= D) | REFUSÉ | (b) `navigateur.py` modifié pendant le lancement, absent du commit |
| 2ᵉ lancement de P0 (départ 7268412) | 1feb6cf (enfant) | REFUSÉ | codes (pages 1) ; issue passé → échoué et sous-tests 2 → 0 du test du clavier |
| contrôle du chef sur P0 | 1feb6cf (= D) | ACCEPTÉ | |
| copie du contrôle P1, 8 tests de `test_nombres.py` retirés des listes texte seulement | a8d6ab6 | REFUSÉ | 8 disparus ; listes / `rapport.json` et listes / JUnit discordants |
| sans argument ; dossier absent | — | code 2 | aide ; « fichier absent » puis `VERDICT : REFUSÉ (code 2)` |

### Suite complète (`complet --rapport …/scratchpad/P2-rapport`, départ a8d6ab6 + `lancer.py`, `verifier.py`, `journal.md`)

| | Mur (pytest) | Résultat |
|---|---|---|
| Python | **735 s** (732 s) | 1311 passés, 1 xfail, 103 033 sous-tests ; code 0 ; JUnit / extension : 0 écart |
| Pages | **994 s** (993 s) | 122 passés, 2 554 sous-tests ; code 0 ; JUnit / extension : 0 écart |

Code global 0 (23:09 → 23:38). `environnement` : `CORPUS`, `OUTILS`, `MEMO` non définis. Empreintes au début et à la fin : `lancer.py`
c4282f3, `verifier.py` e429b39 (inchangées) ; `journal.md` changé pendant le lancement (rédaction de cette section : liste permise).
`python3 tests/comparer_listes.py docs/chantiers/tests-rapides/reference <P2-rapport>` : Python et pages **identiques, nom par nom**
(code 0). `--collect-only -q` de chaque suite, lancée séparément : 1312 et 122 identifiants, **identiques** à `reference/collecte-*.txt`.

### Temps natif

P2 ne touche aucun moteur. `mesurer_temps.py` : Ex7 0,58 s ; a 0,03 s ; b 0,36 s ; c 0,25 s ; d 0,22 s (P1 : 0,59 ; 0,03 ; 0,36 ;
0,25 ; 0,22) : aucune hausse.

### Remarques

- Libellés de (b) : « apparu pendant le lancement » = absent du relevé du début, présent dans celui de la fin (fichier créé, ou fichier
  suivi modifié après le début) ; « modifié au début, changé ou retiré pendant le lancement » = empreintes du début et de la fin différentes.
- Après le commit, l'arbre est propre : `rapide` (qui lit `git diff HEAD` et les fichiers non suivis) ne relance alors que les tests de
  fumée. Le contrôle indépendant de l'audit §M1 (« puis `rapide` ») est donc faible tant que `rapide` n'a pas de base de comparaison
  (question pour l'enseignant, à traiter avec P6 si vous le voulez).

### Vérification propre (audit §M1) : essais sur le commit 1 (55daa1f) et le rapport P2

Commande de chaque essai : `python3 tests/lancer.py verifier <dossier>` (sous `subprocess`, limite 5 min ; chacun dure moins de 2 s).
Les dossiers des essais 2 et 3 sont des **copies** de `…/scratchpad/P2-rapport`, modifiées par un script du scratchpad
(`fabriquer.py`) ; aucun test du dépôt n'est retiré ni touché. Les essais du point 1 se font sur deux branches jetables créées depuis
55daa1f, supprimées ensuite (`git branch -D`).

**Cas normal** — `verifier …/P2-rapport` sur 55daa1f :
```
  (a) commit 55daa1f : enfant direct du commit de départ a8d6ab6 ; 4 fichier(s) changé(s)
      empreintes conformes pour les 2 fichier(s) testé(s)
  (b) aucun autre fichier modifié ou non suivi pendant le lancement
  (c) environnement : CORPUS=(non défini), MEMO=(non défini), OUTILS=(non défini)
  (c) python : 1312 collectés ; 1311 passé, 1 xfail ; 103033 sous-tests
      identique à la référence, nom par nom (collecte, issues, sous-tests)
  (c) pages : 122 collectés ; 122 passé ; 2554 sous-tests
      identique à la référence, nom par nom (collecte, issues, sous-tests)
  (a) documentation de chantier changée après le début du lancement (aucun test ne la lit) : 2
      docs/chantiers/tests-rapides/journal.md
      docs/chantiers/tests-rapides/suivi.md
VERDICT : ACCEPTÉ (code 0)
```

**Essai 1 — commit modifié sans relancer → REFUSÉ.**
- 1a, branche `essai-verifier-p2-amend` : une ligne de commentaire ajoutée à `tests/lancer.py`, `git commit --amend` (même parent
  a8d6ab6) :
  ```
    - (a) fichier(s) du commit différent(s) de ce que le lancement a testé : 1
      tests/lancer.py : empreinte dans le commit 4ddea94, au lancement c4282f3
  VERDICT : REFUSÉ (code 1) : 1 motif(s) ci-dessus
  ```
- 1b, branche `essai-verifier-p2-dessus` : même changement dans un commit de plus, au-dessus de 55daa1f :
  ```
    - (a) 633dd82 n'est ni le commit de départ du lancement (a8d6ab6) ni son enfant direct (parents : 55daa1f) : le lancement ne porte pas sur ce commit
  VERDICT : REFUSÉ (code 1) : 1 motif(s) ci-dessus
  ```
- Retour sur `tests-rapides` (55daa1f, arbre propre), puis `git branch -D` des deux branches.

**Essai 2 — fichier non suivi ajouté pendant le lancement → signalé et REFUSÉ.** Copie où `tests/python/brouillon_essai.py` figure
dans le relevé de fin seulement :
```
  MOTIFS DE REFUS : 1
    - (b) fichier(s) modifié(s) ou non suivi(s) pendant le lancement, hors du commit et hors de la liste permise : 1
      tests/python/brouillon_essai.py : apparu pendant le lancement, absent du commit
VERDICT : REFUSÉ (code 1) : 1 motif(s) ci-dessus
```
Variantes : présent dès le début et laissé hors du commit → REFUSÉ (« modifié ou non suivi pendant le lancement, absent du commit ») ;
`CLAUDE.md` changé pendant le lancement → ACCEPTÉ, listé (« (b) fichier(s) de la liste permise … : CLAUDE.md »).

**Essai 3 — test disparu → REFUSÉ.** Copie où `tests/python/test_nombres.py::TestSaisie::test_nettoyer` est retiré de **tous** les
témoins du dossier (collecte, résultats, `rapport.json`, JUnit), comme s'il n'avait jamais été collecté :
```
  (c) python : 1311 collectés ; 1310 passé, 1 xfail ; 103033 sous-tests
  MOTIFS DE REFUS : 1
    - (c) python : test(s) disparu(s) par rapport à la référence : 1
      tests/python/test_nombres.py::TestSaisie::test_nettoyer
VERDICT : REFUSÉ (code 1) : 1 motif(s) ci-dessus
```
Variantes (copies) : le même test passé → sauté dans tous les témoins → REFUSÉ (« test(s) sauté(s) en plus : … passé -> sauté ») ;
un sous-test de moins à `test_goatcounter_…` → REFUSÉ (« nombre de sous-tests passés en baisse : … 3 -> 2 ») ; un test **ajouté**
(`test_nouveau_essai`, passé) → ACCEPTÉ, listé (« test(s) ajouté(s) (acceptés) : 1 ») ; la copie « disparu » comparée avec
`--reference` à la copie « ajouté » → REFUSÉ, 2 disparus ; `verifier …/P2-rapport --reference <contrôle du chef sur P1>` → ACCEPTÉ.

### Commit 2 (méthode, T10) : suite complète `--rapport …/scratchpad/P2b-rapport`

Départ 55daa1f + `docs/methode-chantiers.md` (« Organisation de nuit » : contrôle allégé ; consigne du sous-agent : donner le dossier de
`complet --rapport`) + `journal.md`. Python **710 s** (pytest 707 s) : 1311 passés, 1 xfail, 103 033 sous-tests ; pages **968 s**
(967 s) : 122 passés, 2 554 sous-tests ; codes 0 ; JUnit / extension : 0 écart. `comparer_listes.py` : **identique, nom par nom** ;
`--collect-only -q` des deux suites : 1312 et 122, identiques à la référence. `verifier …/P2b-rapport` est lancé sur le commit 2
(résultat dans `suivi.md` et dans le rapport de la partie).

## P3 (05.11.2026) : `TestStructure` calculé une fois par classe (T3)

### Plan

1. Temps du fichier `tests/python/test_redaction_bh_3m.py` **avant** (lancé seul, `-n auto` comme `complet`, limite 5 min, extension
   `rapport_pytest` pour les sous-tests).
2. `TestStructure` : la liste des rédactions descendantes `(saisie, ou, descente)` est calculée **une fois par classe** (au premier
   test qui en a besoin, mêmes entrées `ENTREES`, même filtre `r["ok"]`, même ordre) ; chaque test reçoit sa **copie profonde**
   (`copy.deepcopy`) au premier appel de `toutes()`. Corps des tests inchangés (mêmes vérifications, mêmes boucles, mêmes `subTest`) ;
   les trois tests qui appellent `descentes()` ne changent pas. Aucun moteur modifié, aucun autre fichier de test touché.
3. Temps du fichier **après**, mêmes conditions ; sous-tests test par test identiques à la référence.
4. Suite complète `complet --rapport …/scratchpad/P3-rapport` ; `comparer_listes.py` ; `--collect-only -q` de chaque suite (séparément)
   contre `reference/collecte-*.txt` ; murs comparés à P0–P2.
5. Temps natif (`mesurer_temps.py`) ; `suivi.md` ; commit ; `verifier …/P3-rapport`.

### Code

`tests/python/test_redaction_bh_3m.py`, classe `TestStructure` seulement (`git diff` : `import copy` et la méthode `toutes`) :
- `_redactions()` (méthode de classe) calcule la liste `(saisie, ou, descente)` **une fois** et la garde dans `TestStructure._REDACTIONS` :
  mêmes `ENTREES`, même `la.etudier(saisie)`, même filtre `r["ok"]`, même parcours `etudes` → `etapes` → `type == "descente"`, même
  ordre. Calcul paresseux (au premier test qui appelle `toutes()`) plutôt que `setUpClass` : un processus xdist qui ne reçoit que des
  tests de la classe sans `toutes()` (`test_ln_de_x_cube…`, `test_ln_reste_en_haut…`, `test_les_derivees_composees…`) ne le paie pas.
  Si `la.etudier` lève une exception, rien n'est gardé et chaque test qui appelle `toutes()` échoue, comme avant.
- `toutes()` devient une méthode d'instance : au premier appel dans un test, `copy.deepcopy` de la liste commune (copie propre au
  test, `setUp` la remet à `None`), puis un itérateur sur cette copie. `test_les_deux_signes_zero_sont_ecrits` appelle toujours
  `toutes()` une fois par cas du corpus : il parcourt sa propre copie à chaque fois, sans recalcul.
- Corps des 12 tests de la classe (dont 9 appellent `toutes()`) inchangés (mêmes vérifications, mêmes boucles, mêmes `subTest` et leurs paramètres) ; `descentes()` et les autres
  classes inchangées. Aucun moteur modifié. Aucun autre fichier n'appelle `TestStructure.toutes`.

### Vérification propre : fichier lancé seul (`-n auto`, extension `rapport_pytest`, limite 5 min)

| | Mur (pytest) | Tests | Sous-tests | Test le plus long |
|---|---|---|---|---|
| Avant (1f34e3c) | **121 s** | 25 passés | 1 681 | `test_les_deux_signes_zero_sont_ecrits` 110,7 s |
| Après | **44 s** | 25 passés | 1 681 | 27,5 s (le premier test de chaque processus paie le calcul commun) |

Collecte, issues et sous-tests **identiques test par test** entre avant et après, et identiques aux 25 lignes de
`reference/resultats-python.txt` pour ce fichier (issue et nombre de sous-tests). Après : 4 tests de 23 à 28 s (le calcul commun,
une fois par processus, 4 processus), les autres tests de `TestStructure` de 0,02 à 1 s.

### Temps natif

P3 ne touche aucun moteur. `mesurer_temps.py` : Ex7 0,58 s ; a 0,03 s ; b 0,36 s ; c 0,26 s ; d 0,22 s (P2 : 0,58 ; 0,03 ; 0,36 ;
0,25 ; 0,22) : aucune hausse.

### Suite complète (`complet --rapport …/scratchpad/P3-rapport`, départ 1f34e3c + `test_redaction_bh_3m.py`, `journal.md`)

| | Mur (pytest) | Résultat |
|---|---|---|
| Python | **670 s** (668 s) | 1311 passés, 1 xfail, 103 033 sous-tests ; code 0 ; JUnit / extension : 0 écart |
| Pages | **985 s** (984 s) | 122 passés, 2 554 sous-tests ; code 0 ; JUnit / extension : 0 écart |

Code global 0 (00:16 → 00:44). `environnement` : `CORPUS`, `OUTILS`, `MEMO` non définis. `python3 tests/comparer_listes.py
docs/chantiers/tests-rapides/reference <P3-rapport>` : Python et pages **identiques, nom par nom** (code 0). `--collect-only -q` de
chaque suite, lancée séparément : 1312 et 122 identifiants, **identiques** à `reference/collecte-*.txt`.

Mur Python comparé aux parties précédentes (même machine, `-n auto`) : P0 737 et 755 s ; P1 715 s (contrôle du chef 801 s) ; P2 735 s
et 710 s. P3 : **670 s**, soit 40 à 85 s de moins que P0–P2 (sans compter le 801 s), dans l'ordre de grandeur de l'audit (environ 50 s
de mur). Le bruit d'un lancement à l'autre (environ ± 40 s) reste du même ordre : le gain du fichier seul (121 s → 44 s) est la mesure
nette. Pages : 985 s (P1–P2 : 967 à 994 s), sans changement attendu.

## P4 (05.11.2026) : cache explicite des sorties de l'outil Limites (T4)

### Plan

1. Mesure préalable (outil de mesure du scratchpad, rien dans le dépôt) : appels de `la.etudier` et `rla.resoudre` par entrée, dans
   chaque processus, sur les fichiers sans mock qui appellent l'outil Limites ; temps évitable par un cache par processus.
2. `tests/python/memo.py` (module de test, aucun moteur modifié) : `etudier_la(entree, avec_bornes=False)` garde la sortie de
   `la.etudier` par processus et rend **une copie profonde à chaque appel** (le résultat gardé est lui-même une copie) ; une exception
   n'est jamais gardée ; `MEMO=0` (lue à chaque appel) : appel direct du moteur, rien n'est gardé. `la.etudier` n'est jamais remplacé.
3. Choix des fichiers, **par fichier entier** : les fichiers de `tests/python` qui appellent `la.etudier` et ne contiennent aucun mock
   (ni `mock`, ni `patch`, ni monkeypatch, ni `setattr`/`delattr`, ni affectation d'un attribut du moteur), sauf ceux qu'importe un
   fichier avec mock. Dans ces fichiers, `la.etudier(…)` → `memo.etudier_la(…)` (mêmes entrées, mêmes arguments) ; rien d'autre ne change.
4. Tests ajoutés : `test_memo.py` (copie profonde égale au moteur, un seul appel du moteur avec le cache, un appel par appel avec
   `MEMO=0`, comptés par `sys.setprofile` sans rien remplacer) et `test_memo_garde.py` (garde statique). Essais négatifs de la garde.
5. Groupe des fichiers concernés lancé avec et sans `MEMO=0` (limite 5 min) ; puis deux suites complètes `--rapport` (normale et
   `MEMO=0`), comparées à la référence et entre elles ; `--collect-only -q` de chaque suite contre la référence.
6. Temps natif ; `suivi.md` (état, ligne `MEMO=0` du texte pour `CLAUDE.md`) ; commit ; `verifier` sur les deux dossiers.

### Mesure préalable (scratchpad, `-n auto`, limite 5 min)

Compteur par processus (extension de mesure hors du dépôt) sur les 10 fichiers sans mock qui appellent l'outil Limites : `la.etudier`
1 338 appels, 307,5 s de somme, dont **757 appels répétés (même entrée, même processus) pour 119,0 s évitables** ; `rla.resoudre`
205 appels, 39,3 s, dont 81 répétés pour 11,1 s évitables. Seul `la.etudier` est mis en cache (ce que prévoit l'audit §M4) ;
`rla.resoudre` (11 s de somme, environ 3 s de mur) est laissé hors du cache.

### Code

- **`tests/python/memo.py`** (nouveau) : `etudier_la(entree, avec_bornes=False)`, `actif()` (faux si `MEMO=0`), `vider()`. Clé
  `(entree, avec_bornes)` : ce sont les seuls arguments acceptés (l'argument `analyse` du moteur, qui porte des objets, n'est jamais
  passé par les tests ; `etudier_la` ne l'accepte pas). La clé est injective sur ce que le moteur reçoit : `la.etudier` est appelé avec
  exactement `(entree, avec_bornes=avec_bornes)`. Valeur gardée = `copy.deepcopy` de la sortie ; chaque appel rend un nouveau
  `copy.deepcopy` de la valeur gardée. Exception du moteur : rien n'est gardé, elle remonte. `MEMO=0` (lue à chaque appel) :
  `return la.etudier(entree, avec_bornes=avec_bornes)`, rien n'est gardé. Aucun attribut d'aucun moteur n'est touché.
- **Fichiers qui importent `memo`** (9, plus `test_memo.py`) : `test_corpus_limites_3m`, `test_doctrine_bh`, `test_instantanes`,
  `test_limites_deux_cotes`, `test_racines_reelles`, `test_rappel_methode`, `test_redaction_bh_3m`, `test_resoudre_la`,
  `test_tableau_limites`. Changement : `la.etudier(…)` → `memo.etudier_la(…)` (22 appels ou références, mêmes arguments), et
  `import limites_asymptotes as la` → `import memo` là où `la` ne sert plus (7 fichiers ; `test_rappel_methode` et `test_racines_reelles`
  gardent `la` pour `la.METHODES` et `la.etudier_json`). Aucune vérification, entrée, boucle ni `subTest` modifiés.
- **Exclus** (contiennent un mock) : `test_redaction_limites`, `test_garde_fou_limites`, `test_limites_d12_d16`, `test_limite_indeterminee`,
  `test_vocabulaire`, `test_corpus_etude_complete` (et les autres fichiers avec mock, hors Limites). **Exclu sans mock** :
  `test_proprietes_limites` (10,8 s de somme), parce que `test_redaction_limites` (avec mock) l'importe : la garde interdit qu'un fichier
  avec mock atteigne, même de loin, un fichier qui importe `memo` (option la plus prudente). `test_doctrine_bh` importe `TestStyle` de
  `test_redaction_limites` (fichier avec mock) : il est gardé, car il ne contient lui-même aucun mock et `TestStyle` (sans mock) appelle
  `la.etudier` directement, jamais `memo` (voir « Questions » de `suivi.md`).
- **Tests ajoutés** (seuls ajouts aux listes) :
  - `tests/python/test_memo.py::TestMemo::test_copie_profonde_egale_au_moteur`, `::test_cache_actif_le_moteur_n_est_appele_qu_une_fois`,
    `::test_memo_0_appelle_vraiment_le_moteur_a_chaque_fois` (6 entrées, dont une avec `avec_bornes=True` et une saisie refusée ; les
    appels du moteur sont comptés par `sys.setprofile`, observateur qui ne remplace rien ; `MEMO` est remis à sa valeur d'avant) ;
  - `tests/python/test_memo_garde.py::TestGardeMemo::test_aucun_fichier_qui_importe_memo_ne_contient_de_mock` (texte entier :
    `mock|patch|monkeypatch|setattr|delattr`, sans casse ; et, par l'arbre syntaxique, aucune affectation ni suppression d'un attribut
    ou d'un élément d'un module du moteur ou de `memo` ; la liste des fichiers est `FICHIERS_MEMO`, explicite),
    `::test_aucun_fichier_avec_mock_n_importe_un_fichier_qui_importe_memo` (imports transitifs dans `tests/python`),
    `::test_memo_reste_un_module_de_test` (aucun moteur n'importe `memo` ; `memo.py` n'affecte aucun attribut du moteur).
  `test_memo_garde.py` n'importe pas `memo` (il contient les mots qu'il cherche).
- **Essais négatifs de la garde** (arbre remis ensuite) : `import memo` ajouté à `test_garde_fou_limites.py` → les deux premiers tests de
  garde échouent (fichier hors `FICHIERS_MEMO` ; fichier avec mock qui atteint `memo`) ; fichier factice avec `la.METHODES = []`,
  `ed.x.y += 1`, `del la.W`, `etudier.cache = 3`, `la.T['a'] = 1` → 5 remplacements trouvés, `os.environ['MEMO'] = '0'` et un appel
  `la.etudier(…)` non signalés.

### Groupe des fichiers concernés (11 fichiers, `-n auto`, limite 5 min)

| | Mur (pytest) | Résultat |
|---|---|---|
| cache actif | **88 s** | 125 passés, 14 509 sous-tests |
| `MEMO=0` | **108 s** | 125 passés, 14 509 sous-tests |

### Temps natif

P4 ne touche aucun moteur. `mesurer_temps.py` : Ex7 0,59 s ; a 0,03 s ; b 0,37 s ; c 0,25 s ; d 0,22 s (P3 : 0,58 ; 0,03 ; 0,36 ;
0,26 ; 0,22) : aucune hausse.

### Suites complètes (départ f140f1c + `memo.py`, `test_memo.py`, `test_memo_garde.py`, 9 fichiers de test, `journal.md`)

| | Python : mur | Python : résultat | Pages : mur | Pages : résultat | Code |
|---|---|---|---|---|---|
| `complet --rapport …/scratchpad/P4-rapport` (cache actif, `MEMO` non défini) | **660 s** | 1317 passés, 1 xfail, 103 098 sous-tests | **970 s** | 122 passés, 2 554 sous-tests | 0 |
| `MEMO=0 complet --rapport …/scratchpad/P4-memo0-rapport` | **672 s** | 1317 passés, 1 xfail, 103 098 sous-tests | **971 s** | 122 passés, 2 554 sous-tests | 0 |

JUnit / extension : 0 écart dans les deux. `environnement` : `MEMO` non défini, puis `MEMO='0'` (CORPUS et OUTILS non définis).

**Comparaisons** :
- `comparer_listes.py reference P4-rapport` et `reference P4-memo0-rapport` : pages identiques nom par nom ; Python : **les seuls
  écarts sont les 6 tests ajoutés** (collecte et résultats, tous passés : les 3 de `test_memo.py`, les 3 de `test_memo_garde.py`) ;
  les 1312 tests de la référence ont la même issue et le même nombre de sous-tests (103 098 = 103 033 + 65 sous-tests des tests ajoutés).
- `comparer_listes.py P4-rapport P4-memo0-rapport` : Python et pages **identiques, nom par nom** (code 0).
- `--collect-only -q` de chaque suite, lancée séparément, avec et sans `MEMO=0` : Python 1318 identifiants = référence + les 6 ajoutés ;
  pages 122 identifiants identiques à la référence.

**Gain du cache** : dans la suite complète, 672 s → 660 s (12 s, dans le bruit d'un lancement à l'autre, environ ± 40 s) ; mesure nette
sur le groupe des 11 fichiers : 108 s → 88 s (20 s de mur). C'est moins que l'estimation de l'audit (1 à 1,5 min) : les plus gros
appelants de l'outil Limites (`test_redaction_limites`, `test_vocabulaire`, `test_limites_d12_d16`, `test_garde_fou_limites`) contiennent
des mock et restent hors du cache (décision T4, par fichier entier), et P3 avait déjà pris la plus grosse répétition (`TestStructure`).
Murs des quatre suites : Python 660 / 672 s, pages 970 / 971 s (P3 : 670 et 985 s).

## P5 (05.11.2026) : cache de l'oracle `racines` (T5)

### Plan

1. `racines(s)` (`tests/python/test_exp_log_m.py`) n'est **pas modifiée** (ni signature, ni corps, ni tolérances, ni grille). Elle lit
   `s.g` et `s.d` (par `ecart`), les arbres de `exp_log` (par `evaluer`) et le contexte `MP` (30 chiffres).
2. Nouveau module de test `tests/python/memo_racines.py`, sur le modèle de `memo.py` : `racines(s)` appelle
   `test_exp_log_m.racines(s)` une fois par clé et par processus, garde une copie profonde du résultat et **rend une copie profonde à
   chaque appel** ; une exception n'est jamais gardée ; `MEMO=0` (lue à chaque appel) : appel direct, rien n'est gardé. Aucun
   attribut n'est remplacé. Module à part (et non `memo.py`) : les quatre fichiers appelants créent leurs méthodes de test par
   `setattr(ClasseDeTest, …)`, et la garde de P4 interdit le mot `setattr` dans un fichier qui importe `memo` ; on ne touche pas à
   cette garde (ce serait l'affaiblir).
3. Clé : instantané **immuable et structurel** de tout l'argument (la `Saisie` entière : genre, g, d, inconnue, paramètres ; chaque
   nœud par son **type exact** pris dans une liste fermée et **tous** ses champs ; feuilles : `str`, `None`, `Fraction` par numérateur
   et dénominateur, `tuple`), plus le contexte de l'oracle (fonctions `racines`, `ecart`, `evaluer`, objet `MP`, sa précision et son
   arrondi, classes de nœuds lues dans `exp_log` au moment de l'appel). Tout autre type (flottant, entier, SymPy, sous-classe…) :
   pas de clé, **appel direct** de l'oracle. Démonstration d'injectivité : ci-dessous, « Clé ».
4. Appelants : `racines(s)` → `memo_racines.racines(s)` aux 9 appels des 4 fichiers (`test_exp_log_m`, `test_exp_log_m_t36`,
   `test_exercices_el_m`, `test_explog_3c`) ; rien d'autre ne change (mêmes entrées, mêmes boucles, mêmes `subTest`, mêmes tolérances).
5. Test ajouté `tests/python/test_memo_racines.py` : copie profonde égale à l'oracle ; un seul appel de l'oracle par clé (cache actif) ;
   `MEMO=0` appelle l'oracle à chaque fois et ne garde rien ; clé (types hors liste → appel direct ; arbre modifié après l'appel →
   nouvelle clé) ; `racines` non modifiée (empreinte SHA-256 de son texte) ; et, comme en P4, un fichier de garde statique à part
   (`test_memo_racines_garde.py`, qui n'importe pas `memo_racines`) : fichiers qui importent `memo_racines`, aucun mock, `setattr`
   seulement sur une classe de test du fichier, aucun fichier avec mock ne l'atteint, aucun moteur ne l'importe.
6. Vérification propre : les 4 fichiers lancés avec une extension de mesure (scratchpad) qui, en fin de session de chaque processus,
   reconstruit l'argument de **chaque clé gardée**, rappelle l'oracle sans cache et compare résultat par résultat (longueur, chaque `mpf`
   exactement égal) ; appels directs (hors clé) comptés par `sys.monitoring`. Lots sous 5 minutes.
7. Suite complète `--rapport …/scratchpad/P5-rapport`, `comparer_listes.py`, `--collect-only -q` de chaque suite ; temps natif ;
   `suivi.md` ; commit ; `verifier`.

### Code

- **`tests/python/memo_racines.py`** (nouveau) : `racines(s)`, `cle(s)`, `figer(v)`, `contexte(o)`, `actif()` (faux si `MEMO=0`, même
  interrupteur que `memo.py`), `vider()`, `oracle()` (importe `test_exp_log_m` à l'appel : ce fichier importe `memo_racines`). Valeur
  gardée = `copy.deepcopy(test_exp_log_m.racines(s))` ; chaque appel rend un nouveau `copy.deepcopy` (les `mpf` copiés gardent leur type
  et leur contexte `MP`, essai fait). Exception de l'oracle : rien n'est gardé. `MEMO=0` ou argument hors clé : `return o.racines(s)`.
  Le module n'importe pas `memo` et ne remplace aucun attribut.
- **Appelants** (9 appels dans 4 fichiers) : `racines(s)` → `memo_racines.racines(s)` ; `from test_exp_log_m import …, racines` →
  `import memo_racines` + même import sans `racines` (3 fichiers) ; `import memo_racines` ajouté à `test_exp_log_m.py`. Corps de
  `racines`, de `ecart` et d'`evaluer` inchangés (`git diff` : seules les lignes d'import et d'appel changent).
- **Pourquoi pas dans `memo.py`** : les 4 fichiers créent des méthodes de test par `setattr(TestX, "test_…", …)` ; la garde de P4
  (`test_memo_garde.py`) interdit le mot `setattr` dans un fichier qui importe `memo`. Elle n'est pas modifiée. `import memo_racines`
  n'est pas lu comme `import memo` par cette garde (`memo\b`).

### Clé (démonstration d'injectivité)

Clé = `(contexte(o), figer(s))`, où `o` est le module `test_exp_log_m` au moment de l'appel.

1. **`figer` est injectif.** `figer(v)` commence toujours par le **type exact** de `v`, puis : pour un nœud (`Nb`, `Var`, `E`, `Pi`,
   `Neg`, `Op`, `Pow`, `Fn`, `Log`, `Defini`, par `type(v) in …`, donc sans sous-classe), `figer` de **tous** ses champs (`__slots__`
   de la classe et de ses parents ; ces classes n'ont pas de `__dict__`, ce qui est vérifié : un objet qui en aurait un est hors clé) ;
   pour la `Saisie` (namedtuple : genre, g, d, inconnue, paramètres) et un `tuple`, `figer` de chaque élément ; pour une `Fraction`, son
   numérateur et son dénominateur (forme réduite, donc égalité de valeur ⇔ égalité des deux entiers) ; pour une `str`, sa valeur ; pour
   `None`, rien. **Tout autre type lève `HorsCle`** et l'oracle est appelé directement (aucune clé, rien de gardé). Par récurrence sur la
   profondeur : `figer(u) == figer(v)` ⇒ `type(u) is type(v)` et champs égaux un à un ⇒ `u` et `v` sont indiscernables pour toute
   fonction qui ne lit que leurs types et leurs champs.
2. **Pièges écartés.** Flottants, entiers, booléens (`1 == 1.0 == True`, mêmes hachages) : hors clé, jamais confondus. SymPy : aucun
   objet SymPy dans les arbres d'`exp_log` (`Nb.val` est une `Fraction`) ; un objet SymPy serait hors clé, donc la question des
   assomptions (deux expressions égales en texte, différentes en assomptions) ne se pose pas. L'égalité `Noeud.__eq__` d'`exp_log`
   (qui ignore `Nb.dec` et compare les noms de types) n'est **pas** utilisée : la clé est plus fine (elle distingue même `dec` et
   `pct`, ce qui ne coûte que des appels en plus).
3. **Arguments.** `racines(s)` a un seul paramètre, sans valeur par défaut ni mot-clé ; `memo_racines.racines(s)` a la même signature
   et passe `s` tel quel. `racines` ne lit de `s` que `s.g` et `s.d` (par `ecart`) ; la clé contient toute la `Saisie`.
4. **Contexte.** Hors de `s`, `racines` dépend de `ecart` et `evaluer` (noms globaux lus à l'appel), du contexte `MP` (objet, précision
   103 bits, 30 chiffres, arrondi `'n'`) et des classes de nœuds qu'`evaluer` lit dans `exp_log` à l'appel : tout est dans la clé
   (fonctions et objet `MP` par identité). La grille, la bissection et les tolérances sont des constantes du corps de `racines`, dont
   l'empreinte est gardée par `test_memo_racines.py` (et la fonction elle-même est dans la clé).
5. **Déterminisme.** `racines` est une fonction pure de ce qui précède : pas de hasard, ensemble de points trié, mpmath déterministe à
   précision fixée.
6. **Instantané.** La clé est un tuple immuable construit à l'appel ; modifier l'arbre ensuite ne change pas la clé gardée (test
   `test_un_arbre_modifie_apres_l_appel_donne_une_nouvelle_cle`), alors qu'un arbre (mutable) pris comme clé l'aurait faussée.

Donc deux appels de clés égales ont des arguments indiscernables, le même code et le même contexte : ils donnent nécessairement le même
résultat.

### Tests ajoutés

- `tests/python/test_memo_racines.py` : `TestOracleIntact::test_racines_n_est_pas_modifiee` (SHA-256 du texte de `racines` =
  `99e567c5…1383`, le même que les lignes 122–147 de `test_exp_log_m.py` au commit 7186b6d ; signature `(s)` ; c'est bien elle que le
  cache appelle) ; `TestMemoRacines::test_copie_profonde_egale_a_l_oracle`, `::test_cache_actif_l_oracle_n_est_appele_qu_une_fois_par_cle`,
  `::test_memo_0_appelle_vraiment_l_oracle_a_chaque_fois` ; `TestCle::test_saisies_egales_meme_cle_saisies_differentes_cles_differentes`,
  `::test_un_objet_hors_des_types_prevus_n_a_pas_de_cle`, `::test_un_arbre_modifie_apres_l_appel_donne_une_nouvelle_cle`,
  `::test_le_contexte_mpmath_fait_partie_de_la_cle`. Appels de l'oracle comptés par `sys.monitoring` (événement `PY_START` posé sur le
  seul code de `racines` : observateur, rien n'est remplacé ; avec `sys.setprofile`, le fichier prenait 52 s, 15 s ainsi).
- `tests/python/test_memo_racines_garde.py` (n'importe pas `memo_racines`) :
  `TestGardeMemoRacines::test_aucun_fichier_qui_importe_memo_racines_ne_contient_de_mock` (liste explicite `FICHIERS_MEMO_RACINES` ;
  ni `mock|patch|monkeypatch|delattr` ; `setattr` seulement en appel `setattr(C, "test_…", …)` avec `C` classe `TestCase` du fichier ;
  aucune affectation d'attribut d'un moteur, de `memo_racines` ou de `test_exp_log_m`), `::test_aucun_fichier_avec_mock_n_importe_un_fichier_qui_importe_memo_racines`,
  `::test_memo_racines_reste_un_module_de_test`. Fonctions communes reprises de `test_memo_garde.py` (import, sans le modifier).
- **Essais négatifs** (arbre remis ensuite) : `import memo_racines` ajouté à `test_garde_fou_limites.py` (avec mock) → les deux premiers
  tests échouent ; fichier factice → `setattr(el, …)`, `setattr(TestFoo, "pas_test", …)`, `setattr(Autre, "test_y", …)` (classe non
  `TestCase`), `f = setattr` signalés ; `el.Nb = None`, `MP.dps = 40` (MP importé de `test_exp_log_m`), `memo_racines._RACINES = {}`,
  `del racines.x` signalés.

### Vérification propre : avec et sans cache, pour toutes les clés (4 lots, `-n auto`, limite 5 min chacun)

Extension de vérification hors du dépôt (`scratchpad/p5plugin/p5_verif.py`, chargée par `-p p5_verif`). Dans chaque processus :
entrées dans `memo_racines.racines` et dans l'oracle comptées par `sys.monitoring` ; en fin de session, pour **chaque clé gardée**,
l'argument est reconstruit depuis la clé (types exacts, champs un à un), `figer(reconstruit) == clé` et `contexte` inchangé sont
vérifiés, l'oracle est rappelé **sans cache** et comparé au résultat gardé (longueur ; pour chaque racine : même type, `==` exact et
même `repr` à 30 chiffres).

| Lot | Mur (vérification comprise) | Code | Appels du cache | Appels de l'oracle | Clés | Racines comparées | Écarts |
|---|---|---|---|---|---|---|---|
| `test_exp_log_m.py` | 149 s | 0 | 138 | 136 | 136 | 165 | 0 |
| `test_explog_3c.py` | 184 s | 0 | 320 | 221 | 221 | 266 | 0 |
| `test_exp_log_m_t36.py` | 95 s | 0 | 152 | 112 | 112 | 130 | 0 |
| `test_exercices_el_m.py` | 113 s | 0 | 100 | 94 | 94 | 134 | 0 |
| **Total** | | | **710** | **563** | **563** | **695** | **0** |

(Clés comptées par processus, sommées sur les 4 processus de chaque lot.) Appels de l'oracle = clés partout : **aucun appel hors clé**
(tous les arguments de la suite sont dans les types prévus) et aucune exception. 147 appels sur 710 sont servis par le cache quand
chaque fichier est lancé seul ; dans la suite complète, les fichiers partagent en plus le cache d'un même processus.

### Temps natif

P5 ne touche aucun moteur. `mesurer_temps.py` : Ex7 0,58 s ; a 0,03 s ; b 0,36 s ; c 0,25 s ; d 0,23 s (P4 : 0,59 ; 0,03 ; 0,37 ;
0,25 ; 0,22) : aucune hausse.

### Suite complète (`complet --rapport …/scratchpad/P5-rapport`, départ 7186b6d + `memo_racines.py`, 2 tests ajoutés, 4 fichiers de test, `journal.md`)

| | Python : mur | Python : résultat | Pages : mur | Pages : résultat | Code |
|---|---|---|---|---|---|
| `complet --rapport …/scratchpad/P5-rapport` (`MEMO` non défini) | **570 s** | 1328 passés, 1 xfail, 103 161 sous-tests | **979 s** | 122 passés, 2 554 sous-tests | 0 |

JUnit / extension : 0 écart. `environnement` : CORPUS, OUTILS, MEMO non définis.

**Comparaisons** :
- `comparer_listes.py reference P5-rapport` : pages identiques nom par nom ; Python : **les seuls écarts sont les 17 tests ajoutés**
  (6 de P4, 11 de P5 : les 8 de `test_memo_racines.py` et les 3 de `test_memo_racines_garde.py`, tous passés) ; les 1312 tests de la
  référence ont la même issue et le même nombre de sous-tests.
- `comparer_listes.py P4-rapport P5-rapport` : pages identiques ; Python : les 11 ajouts de P5, et **un sous-test de plus** (18 → 19)
  dans `test_memo_garde.py::TestGardeMemo::test_aucun_fichier_avec_mock_n_importe_un_fichier_qui_importe_memo`, qui parcourt chaque
  fichier contenant un mot de mock : le nouveau `test_memo_racines_garde.py` en est un (il n'atteint pas `memo`). Sous-tests :
  103 161 = 103 098 + 62 (tests ajoutés) + 1.
- `--collect-only -q` de chaque suite, lancée séparément (code 0) : Python 1329 identifiants = référence + les 17 ajoutés (aucun
  manquant) ; pages 122 identifiants identiques à la référence.

**Gain** : Python 660 s (P4, cache Limites) / 672 s (P4, `MEMO=0`) → **570 s** : environ 1,5 min de mur, au-delà du bruit d'un lancement
à l'autre (environ ± 40 s). L'audit prévoyait environ 1 min. Pages : 979 s (P4 : 970 s), inchangé. Pas de regroupement `xdist_group`
(décision T6).

## Contrôles du chef d'orchestre

P0 (1feb6cf) : suite complète --rapport, code 0 ; Python 1311 passés + 1 xfail, 103 033 sous-tests, 737 s ; pages 122 passés, 2 554 sous-tests, 950 s ; comparer_listes identique nom par nom ; --collect-only -q des deux suites identique à la référence.

P1 (a8d6ab6) : suite complète --rapport, code 0 ; Python 1311 passés + 1 xfail, 103 033 sous-tests, 801 s ; pages 122 passés, 2 554 sous-tests, 967 s ; comparer_listes identique nom par nom ; --collect-only -q des deux suites identique à la référence.

P2 (55daa1f, 1f34e3c) : verifier ACCEPTÉ sur les deux commits ; essai du chef d'orchestre « test disparu » (copie du rapport P2b) REFUSÉ avec le motif « disparu » ; rapide code 0 en 9 s (tests de fumée seulement, l'arbre étant propre après le commit).

P3 (f140f1c) : verifier ACCEPTÉ ; rapide code 0 (8 s) ; sélection de rapide appliquée aux fichiers du commit (test_redaction_bh_3m.py + fumée) code 0 en 54 s ; diff relu (mêmes entrées, même filtre, copie profonde).

P4 (7186b6d) : verifier ACCEPTÉ sur les deux rapports (MEMO lu correctement, 6 tests ajoutés listés) ; rapide code 0 ; sélection de rapide appliquée aux 15 fichiers du commit : code 0 en 105 s, et avec MEMO=0 code 0 en 129 s ; memo.py relu.
