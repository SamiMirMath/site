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

## Contrôles du chef d'orchestre

P0 (1feb6cf) : suite complète --rapport, code 0 ; Python 1311 passés + 1 xfail, 103 033 sous-tests, 737 s ; pages 122 passés, 2 554 sous-tests, 950 s ; comparer_listes identique nom par nom ; --collect-only -q des deux suites identique à la référence.

P1 (a8d6ab6) : suite complète --rapport, code 0 ; Python 1311 passés + 1 xfail, 103 033 sous-tests, 801 s ; pages 122 passés, 2 554 sous-tests, 967 s ; comparer_listes identique nom par nom ; --collect-only -q des deux suites identique à la référence.

P2 (55daa1f, 1f34e3c) : verifier ACCEPTÉ sur les deux commits ; essai du chef d'orchestre « test disparu » (copie du rapport P2b) REFUSÉ avec le motif « disparu » ; rapide code 0 en 9 s (tests de fumée seulement, l'arbre étant propre après le commit).
