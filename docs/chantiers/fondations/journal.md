# Chantier « Fondations » — journal

Détail du chantier (plans, tableaux, temps, rapports). La fiche courte est `suivi.md`.

## Consigne du chantier

Chantier fondations, sur le PC. Principe : AUCUN changement visible pour les élèves. Toutes les suites avec PROCESSUS_PAGES=4. Parties, dans cet ordre :
F0. Fiche suivi.md (courte) et journal.md. Rafraîchir la référence (lancer.py reference) sur ce main. Créer tests/outils/dump_sorties.py : il écrit la sortie BRUTE de resoudre_json pour tout le corpus (entrées des instantanés, exemples et exercices des pages, toutes filières et variantes) dans un dossier hors du dépôt. Faire un dump de départ.
F1. verifier : (a) ignore les fichiers non suivis ou modifiés sous docs/, comme la commande reference ; (b) une baisse de sous-tests ne fait plus refuser : elle doit être justifiée dans suivi.md (section « Variations de sous-tests » : test, avant → après, raison), sinon refus ; un test disparu, échoué ou sauté en plus reste toujours un refus. Ajouter tests/python/test_lancer.py (dépôt git temporaire) pour verifier.
F2. lancer.py rapide (reste de R4, sans refaire ce que tests-rapides a déjà fait) : git diff -z / ls-files -z (noms à espaces et non ASCII), fichiers supprimés qui relancent leurs dépendants, tests/python/donnees/, une page, cas*.py ou un JSON d'instantané modifié relancent test_instantanes* et test_json_strict. Compléter test_lancer.py.
F3. R1 : une seule liste des outils (manifeste + registre) dont dérivent les listes des tests ; les données propres à un outil restent écrites à la main mais leurs clés sont vérifiées (un oubli échoue). Exp-log entre dans le jeu moteur, test_json_strict et MIGREES, sauf raison écrite.
F4. R6 : test_noyau étendu (exp_log, exp_log_m, redaction_bh) ; graphe d'imports figé par ast, avec les exceptions nommées de docs/architecture.md §5 ; aucun nom de fichier en double dans un manifeste.
F5. R3, ménage : « anciennes » du manifeste et leurs fonctions, code mort du rapport §2.4, copies (qtex_, « Ni logarithme… »), docstrings et commentaires périmés, README (R1–R20, commandes par lancer.py), fichiers fantômes de taches.md et choix-techniques.md, .gitignore (docs/chantiers/**/*.pdf), §6 de quiz.md (onglet = chantier séparé). NE PAS retirer les références à docs/methode-chantiers.md (il existe).
F6. Copie locale de KaTeX pour les tests de pages (sur le modèle de pyodide_local.py) : plus aucun test ne dépend de jsDelivr. Le site publié ne change pas.
VÉRIFICATIONS après chaque partie : dump_sorties identique au dump de départ (cmp), instantanés et références inchangés, listes de tests égales à la référence (sauf ajouts annoncés).
FIN : suite complète relancée par le chef d'orchestre ; si tout est vert et le dump identique, fusion dans main (--no-ff --no-edit) et push ; sinon push de la branche seule.

## F0 — fiches, référence, dump brut

### Plan

1. `suivi.md` (court) et ce journal, seuls fichiers modifiés (sous `docs/`) pendant la suite de référence.
2. Référence : `PROCESSUS_PAGES=4 python3 tests/lancer.py complet --rapport <scratchpad>/rapports/F0-ref` sur 96f183c, puis
   `python3 tests/lancer.py reference <ce dossier>` ; contrôle par `git diff --stat tests/reference`.
3. `tests/outils/dump_sorties.py` (après la référence, puisqu'il est hors de `docs/`).
4. Dump de départ et second dump (déterminisme), comparaison.
5. Suite complète d'avant commit (`complet --rapport <scratchpad>/rapports/F0`), commit, `verifier`.

### Référence rafraîchie (étape 2)

- `PROCESSUS_PAGES=4 python3 tests/lancer.py complet --rapport <scratchpad>/rapports/F0-ref` sur 96f183c, arbre propre (seuls
  `docs/chantiers/fondations/` non suivi) : code 0. Python 1 334 passés + 1 xfail (1 335 collectés), 105 807 sous-tests, 97,5 s ;
  pages 123 passés, 2 386 sous-tests, 297,8 s.
- `python3 tests/lancer.py reference <ce dossier>` : acceptée. Différences avec l'ancienne référence (c9b257f) : 17 tests nouveaux,
  tous des chantiers fusionnés depuis (`test_doubles_signes.py` ×4, `test_explog_doubles_signes.py` ×5, `test_explog_q4_q6.py` ×8),
  et des sous-tests en hausse sur Exp-log (101 952 → 105 807) ; pages : aucune différence.
  `git diff --stat tests/reference` : `collecte-python.txt` (+17), `origine.txt`, `resultats-python.txt`.

### Dump brut : `tests/outils/dump_sorties.py` (étapes 3 et 4)

- Outils lus dans `moteur/manifeste.json` (6 outils à moteur Python), recoupés avec `commun/registre.json` (le simplexe n'a pas de moteur
  Python : noté dans `index.txt`). Fonctions appelées : celles du manifeste moins les « anciennes » (que F5 retirera) ; `fenetre`
  (zoom du graphique) n'est pas appelée ; `exercice` est tiré à part (30 graines par niveau, niveaux lus dans les `poids` de la page).
- Corpus d'un outil : clés de ses instantanés (`tests/python/instantanes/**`), constantes `EXEMPLES*` / `EXOS*` de sa page, corpus des
  tests de pages (`rendu.entrees`, saisies d'erreur comprises), corpus de l'enseignant (`tests/python/donnees/`), énoncés des
  exercices tirés. Filières d'Exp-log : C et M (registre + défaut de `resoudre`), chacune sur tout le corpus de l'outil.
- Un oubli échoue : outil du manifeste absent du registre ou de `rendu.py`, instantané sans outil, module de `donnees/` non lu,
  fonction `_json` absente, page sans `poids` pour un outil à exercices.
- Dump de départ : `/tmp/claude-1000/-home-sami-ubuntu-site/b574d683-7da7-4c53-a00c-237ca55256c7/scratchpad/dumps/depart`
  (17 fichiers, 4 148 sorties, 8,9 Mo, 4 s de mur avec 12 processus).

| Fichier | Entrées |
|---|---|
| resoudre/ensemble-definition.txt (et apercu, controle) | 42 |
| resoudre/derivee-variations.txt (et apercu) | 33 |
| resoudre/limites-asymptotes.txt (et apercu) | 66 |
| resoudre/etude-complete.txt (et apercu) | 22 |
| resoudre/factorisation.txt (et apercu) | 309 |
| resoudre/exponentielles-logarithmes.C.txt, .M.txt (et apercu) | 914 chacun |
| exercices/factorisation.txt | 120 (4 niveaux × 30) |
| exercices/exponentielles-logarithmes.C.txt | 120 (4 niveaux × 30) |
| exercices/exponentielles-logarithmes.M.txt | 180 (6 niveaux × 30) |

- Déterminisme : `depart-bis` (même commande), `un-processus` (`--processus 1`) et `graine-hash` (lancé directement sous uv avec
  `PYTHONHASHSEED=12345`) : `diff -r --exclude=temps` identique (code 0) pour les trois.
- **Commande de comparaison pour les parties suivantes** (dossier de sortie absent ou vide, hors du dépôt) :

      python3 tests/outils/dump_sorties.py /tmp/claude-1000/-home-sami-ubuntu-site/b574d683-7da7-4c53-a00c-237ca55256c7/scratchpad/dumps/<partie>
      diff -r --exclude=temps /tmp/claude-1000/-home-sami-ubuntu-site/b574d683-7da7-4c53-a00c-237ca55256c7/scratchpad/dumps/depart /tmp/claude-1000/-home-sami-ubuntu-site/b574d683-7da7-4c53-a00c-237ca55256c7/scratchpad/dumps/<partie>

  Code 0 et aucune sortie exigés. Exception prévue : F5 retire les « anciennes » du manifeste, qui ne sont déjà pas appelées ; si F3
  ou F5 change le corpus (instantanés, pages, `rendu.py`), la liste des entrées change aussi : le signaler, ne pas « réparer » le dump.

### Suite d'avant commit (étape 5)

`PROCESSUS_PAGES=4 python3 tests/lancer.py complet --rapport <scratchpad>/rapports/F0` : code 0. Python 1 334 passés + 1 xfail,
105 807 sous-tests, 108,4 s ; pages 123 passés, 2 386 sous-tests, 298,3 s. Mêmes listes que la référence posée à l'étape 2 (aucun test
ajouté par F0 : `dump_sorties.py` n'est pas collecté).

## F1 — verifier : docs/ ignoré, baisses de sous-tests justifiées, test_lancer.py

### Plan

1. `tests/verifier.py` : (a)/(b) ignorent tout `docs/` (motif `IGNORES`, comme `HORS_TESTS` de `lancer.py reference`), CLAUDE.md
   toujours permis hors du commit seulement ; la liste des fichiers ignorés est toujours affichée (« aucun » sinon).
2. (d) justifications lues dans le suivi.md du chantier ; refus si absentes, aux mauvais nombres, ou si le suivi.md est introuvable.
3. `tests/python/test_lancer.py` (dépôt git temporaire), docstrings de lancer.py et verifier.py, `docs/methode-chantiers.md`.
4. Vérifications : `verifier` sur F0, dump, instantanés, suite complète, commit, `verifier` sur F1.

### Choix

- **Ignorés** : tout fichier sous `docs/` (dans le commit avec une autre empreinte, ou hors du commit) ; `CLAUDE.md` hors du commit
  (dans le commit avec une autre empreinte : toujours refusé, comme avant). Aucun test ne lit `docs/` (vérifié : seules des
  docstrings le citent ; `test_accueil.py` l'exclut de ses parcours). Le verdict affiche toujours
  « fichiers ignorés (docs/ ; CLAUDE.md hors du commit) : N » et la liste, ou « aucun ».
- **Suivi.md lu** : `--suivi <fichier>`, sinon `docs/chantiers/<branche courante>/suivi.md` dans l'arbre de travail (branche du lancement,
  `branche` de rapport.json, si HEAD est détaché). Introuvable, ou sans la section : toute baisse est refusée (motif affiché).
- **Format d'une ligne** (section « ## Variations de sous-tests », jusqu'au « ## » suivant) :
  `` - `<identifiant pytest complet>` : <avant> → <après> : <raison> `` (« -> » accepté pour « → » ; raison non vide). Expression :
  ``^- `([^`]+)` : (\d+) (?:→|->) (\d+) : (\S.*)$``. Les nombres doivent être exactement ceux que verifier mesure (sous-tests passés,
  référence → lancement). Plusieurs lignes pour un test : une seule doit correspondre (une par partie). Une ligne « - ` » hors format
  et une justification sans baisse correspondante sont listées, sans effet. La justification ne vaut que pour un test dont l'issue ne
  change pas : disparu, échoué, sauté en plus restent des refus.
- **Choix « qui affiche le moins »** : rien d'affiché aux élèves n'est touché par F1.

### test_lancer.py

- Dépôt jetable (tempfile) : copies de `tests/lancer.py`, `verifier.py`, `comparer_listes.py`, un `.gitignore` (`__pycache__/`),
  `src/calcul.py`, `CLAUDE.md`, le suivi.md du chantier `essai`. git sans configuration de l'utilisateur (`GIT_CONFIG_GLOBAL=/dev/null`,
  `GIT_CONFIG_NOSYSTEM`), `GIT_CEILING_DIRECTORIES`, contrôle que la racine git est bien le dossier temporaire ; timeout 60 s à chaque
  sous-processus. Modèle construit une fois par processus puis copié pour chaque test.
- Rapports écrits par le vrai `complet_avec_rapport` du lancer.py copié ; seuls `lancer.python` et `lancer.pages` sont remplacés par
  un faux pytest qui écrit le JSON de `rapport_pytest.py` et un JUnit de la forme de pytest (`testsuites/testsuite/testcase`,
  `skipped type="pytest.xfail"` ou `"pytest.skip"`, `failure`, `error`). La référence est posée par la vraie commande `reference`.
- 20 tests (6 sous-tests) : nominal ; test ajouté et sous-tests en hausse ; docs/ modifié, non suivi, apparu, changé après le lancement
  et CLAUDE.md hors commit ignorés (et listés) ; CLAUDE.md dans le commit changé après le lancement ; fichier non suivi ; fichier
  apparu pendant le lancement ; commit différent des empreintes ; commit qui n'est pas l'enfant du départ ; test disparu (même
  justifié) ; échec (pages, et Python : code 2, pages non lancées) ; sauté en plus (même justifié) ; nouveau test sauté ; baisse sans
  justification ; baisse justifiée (→ et ->) ; mauvais nombres (×2) ; ligne hors format ; suivi.md introuvable puis `--suivi` ;
  suivi.md sans la section ; code de retour non nul ; fichier manquant (code 2). Durée : 2,9 s seul, 1,3 s avec `-n auto`.
- Pour F2 : `Depot` (git, ecrire, commiter, `lancer(*args)`), `Depot.rapport`, `ModeleDepot.copie`. À noter : `rapide` ne relance pas
  `test_lancer.py` quand `tests/lancer.py` ou `tests/verifier.py` change (ils ne sont pas dans `modules_du_depot`, et le test les copie
  au lieu de les importer) : à régler par F2.

### Vérifications

- `verifier` sur le rapport F0 (HEAD = 0cb5a64, arbre modifié par F1) : ACCEPTÉ ; les empreintes ne portent que sur les fichiers notés
  au lancement de F0, les fichiers de F1 n'entrent pas en compte. Ignorés listés : journal.md et suivi.md de F0.
- Dump (`dumps/F1`) : `diff -r --exclude=temps` avec le départ, aucune sortie, code 0. Temps (`--processus 1`) : identiques au
  tableau « Temps » (limites 5,93 s, étude 2,00 s, factorisation 1,95 s, autres < 1 s).
- `git diff --exit-code main -- tests/python/instantanes tests/pages/references` : rien.
- Suite d'avant commit : `PROCESSUS_PAGES=4 python3 tests/lancer.py complet --rapport <scratchpad>/rapports/F1` : code 0. Python
  1 354 passés + 1 xfail (1 355 collectés), 105 813 sous-tests, 91,4 s ; pages 123 passés, 2 386 sous-tests, 296,6 s. Aucun fichier
  changé pendant le lancement. `comparer_listes.py tests/reference <F1>` : seuls ajouts, les 20 tests de
  `tests/python/test_lancer.py::TestVerifier` (passés, 6 sous-tests : 105 807 → 105 813) ; pages identiques nom par nom.

## F2 — `lancer.py rapide` (reste de R4)

### Plan

1. Noms de fichiers lus avec `-z` partout où lancer.py (et verifier.py, qui compare au rapport) lit des noms : `noms_git` dans
   verifier.py (découpage sur `\0`, `os.fsdecode`), utilisé par `fichiers_modifies`, `etat_fichiers` et la liste du commit de
   `verifier` ; `--no-renames` partout (un déplacement donne l'ancien chemin, supprimé, et le nouveau).
2. Fichiers supprimés gardés (marqués « (supprimé) » par `liste`), et règles de `rapide` (ci-dessous).
3. `tests/python/test_lancer.py` : `TestRapide` (dépôt modèle `ModeleRapide`) et trois tests `verifier` (noms, déplacement).
4. Docstring de lancer.py (règles détaillées de `rapide`), docstring de verifier.py (a), `docs/methode-chantiers.md` (point 3 du
   contrôle allégé) ; CLAUDE.md non touché (phrase proposée dans suivi.md).

### Ce que tests-rapides avait déjà fait (non refait)

P6 (ebe2c22) : un `.py` de moteur chargé par une page (d'après `moteur/manifeste.json`) relance les pages à corpus réduit de l'outil,
la filière M avec la page des exponentielles, « toutes » si on ne sait pas borner ; une page, un fichier commun, un test de pages ou un
module de leur corpus relancent les pages. **Point 5 de la consigne** (« un .py de moteur ou une référence de page change → test_rendu
de l'outil ») : la moitié moteur était couverte par P6 (`test_rendu` est dans la suite de pages, filtré par `OUTILS`) ; la moitié
référence ne l'était pas (un `.json` de `tests/pages/references/` ne relançait rien) : faite ici.

### Règles ajoutées à `rapide`

| Changement (modifié, supprimé, déplacé ou nouveau) | Tests Python relancés en plus | Pages (corpus réduit) |
|---|---|---|
| tout fichier : noms à espaces ou non ASCII (`-z`) | (comme avant, mais le fichier n'est plus perdu) | (idem) |
| `.py` supprimé des moteurs, de tests/python ou de donnees/ | ses importeurs, même de loin (son nom reste un nœud du graphe) | celles des outils qui le chargent (manifeste) |
| test_*.py supprimé | aucun (il n'existe plus ; seulement listé) | — |
| `tests/python/donnees/*` | `.py` : ses importeurs ; tout fichier : les modules dont une chaîne nomme `donnees`, puis leurs dépendants ; aucun : **tous** | — |
| `tests/python/instantanes/**` | `test_instantanes*.py`, `test_json_strict.py`, et les modules qui nomment `instantanes` (test_vocabulaire, test_doubles_signes, test_redaction_limites…) | `instantanes/resoudre/<outil>.json` : la page de l'outil (test_comportement le lit) |
| page d'outil (fichier non `.py` d'un dossier d'outil) | `test_instantanes*.py`, `test_json_strict.py` | l'outil (déjà) |
| `tests/python/cas*.py` | `test_instantanes*.py`, `test_json_strict.py` (en plus des importeurs) | toutes (corpus des pages, déjà) |
| `tests/pages/references/<outil>.json` | les modules qui nomment `references` (test_doubles_signes…) | l'outil (filière M : avec la page des exponentielles) ; `graphique-traces.json` ou autre : toutes |
| autre fichier non `.py` de `tests/pages/` | — | toutes (élargi) |
| `tests/lancer.py`, `verifier.py`, `comparer_listes.py`, `rapport_pytest.py` | `test_lancer.py` | — |

Choix :
- **Graphe sur l'état présent, noms des supprimés gardés** (« équivalent sûr » de l'état d'avant) : un module qui importe encore le
  supprimé est atteint ; un module qui ne l'importe plus a été modifié, donc atteint lui aussi, avec ses dépendants.
- **Lecteurs par chemin** : une chaîne qui a le nom du dossier pour élément de chemin (`"donnees"`, `"…/references/…"`), puis
  propagation par le graphe ; si aucun module ne le nomme, tous les tests Python (on élargit).
- **Page → test_instantanes\* et test_json_strict seulement**, comme la consigne, et non tous les importeurs de cas.py (23 fichiers,
  dont des oracles lents) : un exemple ajouté ou changé dans une page change les instantanés, qui échouent ; `complet` reste
  obligatoire avant un commit.
- **`complet` inchangé** : mêmes commandes ; seuls les noms notés dans rapport.json changent pour un nom non ASCII (en clair au lieu de
  l'échappement octal de git, que `verifier` notait « supprimé » des deux côtés et acceptait donc sans comparer d'empreinte) ou un
  déplacement indexé (l'ancien chemin manquait : `verifier` refusait). Deux tests le vérifient.
- `modules_du_depot` tolère un dossier absent (tous les fichiers d'un dossier supprimés) : les supprimés sont pris dans la liste de git.

### test_lancer.py (ajouts)

- `ModeleRapide` : dépôt de forme réelle, petit (manifeste, trois dossiers d'outils avec page et moteur, `commun/`, tests/python avec
  cas.py, cas_el.py, donnees/, instantanes/, tests/pages et ses références), noms `factorisation/a b.py`, `tests/python/é.py`,
  `tests/python/test_a b.py`, `exponentielles-logarithmes/moteur ê.py`, `tests/python/test_nouveau é.py` (non suivi).
- `TestRapide`, 14 tests (24 sous-tests) : rien de modifié ; noms à espaces et non ASCII (non suivis, indexés, commités puis
  `--depuis HEAD~1`) ; module supprimé (arbre puis `--depuis`) ; test supprimé et module de moteur supprimé ; fichier déplacé (indexé
  puis `--depuis`) ; donnees/ (module, JSON supprimé et nouveau, dossier nommé par aucun module → tous) ; page (trois outils) ; page
  commitée `--depuis` ; cas_el.py modifié, cas.py supprimé ; instantané (simple, resoudre de deux outils, supprimé) ; référence de page
  (outil, filière M, graphique → toutes) ; moteur → page de l'outil (trois) ; les quatre scripts de commande → test_lancer.py ; un
  test isolé et un fichier commun (rien d'autre).
- `TestVerifier`, 3 tests de plus : nom « é b » dans le commit (accepté, empreinte contrôlée) ; nom « é » changé après le lancement
  (refusé) ; déplacement indexé (accepté).
- Contre-épreuve : le nouveau test_lancer.py lancé sur les scripts de d4837d6 (worktree jetable) : 33 échecs (tests et sous-tests),
  dont tous les cas de règles et les trois de `verifier`.
- Durée : 1,6 s avec `-n auto` (37 tests, 30 sous-tests).

### Vérifications

- Dump (`dumps/F2`) : `diff -r --exclude=temps` avec le départ, aucune sortie, code 0 ; `dumps/F2-p1` (`--processus 1`) aussi. Temps
  (`--processus 1`) : identiques au tableau « Temps » (limites 5,85 s, étude 1,99 s, factorisation 1,89 s, autres < 1 s).
- `git diff --exit-code main -- tests/python/instantanes tests/pages/references` : rien.
- `liste` sur l'arbre réel avant commit : fichiers `docs/chantiers/fondations/journal.md`, `docs/methode-chantiers.md`, `tests/lancer.py`,
  `tests/python/test_lancer.py`, `tests/verifier.py` ; tests Python : fumée + `test_lancer.py` ; pages : aucune. Cohérent (avant F2,
  `tests/lancer.py` et `tests/verifier.py` modifiés n'auraient pas relancé `test_lancer.py`).
- Suite d'avant commit : `PROCESSUS_PAGES=4 python3 tests/lancer.py complet --rapport <scratchpad>/rapports/F2` : code 0. Python
  1 371 passés + 1 xfail (1 372 collectés), 105 837 sous-tests, 100,4 s ; pages 123 passés, 2 386 sous-tests, 300,3 s (un premier
  lancement, vert lui aussi, a été refait : une docstring de lancer.py retouchée pendant qu'il tournait). Pendant le lancement, deux
  fichiers non suivis sont apparus sous `docs/chantiers/equations-2e-degre/` (`decisions (1).md:Zone.Identifier`,
  `decisions.md.md`), pas de F2 : ignorés par `verifier` (docs/), laissés hors du commit. `comparer_listes.py tests/reference <F2>` :
  seuls ajouts, les 20 tests de F1 (`TestVerifier`) et les 17 de F2 (14 `TestRapide`, 3 `TestVerifier`), tous passés ; sous-tests
  105 807 → 105 837 (+6 de F1, +24 de F2) ; pages identiques nom par nom.

## F3 — R1 : une seule liste des outils

### Plan

1. `tests/python/outils_du_site.py` (json, os, urllib.parse : aucune dépendance) : lit `commun/registre.json` et `moteur/manifeste.json`,
   expose `outils()` (registre), `outils_pyodide()` (manifeste), `pages()`, `dossiers_moteurs()`, `filieres()`, `variantes()`
   (`exponentielles-logarithmes-M`, tiré de `?filiere=M` du registre), `nom_de_test()`. Placé dans `tests/python` (et non `tests/`) :
   les tests Python et de pages l'importent sans toucher à `sys.path`, et le graphe de `rapide` le voit comme un module (ses
   dépendants sont relancés quand il change). `lancer.py` le charge par son chemin (`importlib`, `sys.path` inchangé).
2. Listes dérivées (ci-dessous), en gardant tous les noms de tests et de classes.
3. Données propres à un outil : clés vérifiées par deux nouveaux fichiers, `tests/python/test_outils_du_site.py` et
   `tests/pages/test_donnees_des_pages.py` (sans navigateur ; deux noms distincts pour ne pas créer un second doublon comme
   `test_accueil.py`).
4. Exp-log : décision au cas par cas (ci-dessous). 5. Butée « 16 liens / 7 outils » gardée (docstring complétée). 6. architecture.md § 4.

### Listes dérivées

| Où | Avant | Après |
|---|---|---|
| `tests/python/moteurs.py` | 7 dossiers écrits | `outils_du_site.dossiers_moteurs()` : même ordre, `sys.path` identique (comparé avant / après, et figé par `test_ordre_de_sys_path`) |
| `tests/lancer.py` | `DOSSIERS_MOTEURS`, `OUTILS_PAGES`, `OUTIL_M`, `MANIFESTE` | dérivés (`VARIANTES` remplace `OUTIL_M`) ; liste illisible → `rapide` relance tout |
| `test_vocabulaire.py` | `TestVouvoiement.DOSSIERS_MOTEURS`, `TestVocabulairePages.PAGES` | dossiers du manifeste ; registre + accueil (**+ simplexe** : 1 sous-test de plus) |
| `test_style_commun.py` | `OUTILS` (6) | `outils_pyodide()` (le simplexe, page autonome, n'a pas `composants.css`) |
| `test_source_unique.py` | `MIGREES` (5) | `outils_pyodide()` : **exp-log ajouté** (13 sous-tests de plus) |
| `test_tableaux_css.py` | `OUTILS` (4 à tableaux) | `outils_pyodide()` : factorisation et exp-log contrôlées aussi (2 sous-tests de plus) |
| `test_memo_garde.py` | `DOSSIERS_MOTEURS` (7) | dossiers du manifeste (même ensemble ; aussi lu par `test_memo_racines_garde`) |
| `test_resoudre_import.py` | `OUTILS` : copie des fichiers et modules du manifeste | fichiers et module lus au manifeste ; reste `EXEMPLE` par outil (mêmes sous-tests, mêmes fichiers) |
| `tests/pages/rendu.py` | `OUTILS` (6) | `outils_pyodide()` (même liste, même ordre) |
| `tests/pages/test_largeurs.py` | `TOUS = OUTILS + ["simplexe"]` | `outils()` (même ensemble) |
| `tests/pages/captures.py` | `CALCUL` (5, sans exp-log : `KeyError` sur sa page) | `test_comportement.CALCUL` (une seule liste) |

Restent écrites à la main, clés vérifiées : `test_instantanes.OUTILS`, `test_instantanes_resoudre.OUTILS` (et une méthode par clé, un
fichier d'instantané par clé), `test_json_strict.OUTILS_ENTREES` et `ENTREES_FILIERE_M`, `test_resoudre_import.EXEMPLE` et `FILIERE_M`,
`test_source_unique.TestDispositionDuClavier.PAGES`, `test_vocabulaire.TestVocabulaireEleve.ANALYSES` + `METHODES` (sortis de la méthode
en attributs de classe ; les méthodes existent), `cas.CAS_LIMITES` (⊆) ; pages : `rendu.REDUIT` (outils + variante), `test_comportement`
`CALCUL`, `EXEMPLE`, `INVALIDE`, `rendu.ERREURS` et `test_comportement.ANALYSE` (⊆), une méthode par outil dans `TestRendu` et
`TestLargeurs`, une référence de page par outil et variante (exception nommée : `graphique-traces.json`), la variante du registre =
`[rendu.OUTIL_M]`.

### Exp-log (point 4)

- **`test_json_strict`** : déjà présent (`test_exponentielles_logarithmes_json`, filière C) ; ajouté à `OUTILS_ENTREES` (la méthode le lit
  là, mêmes sous-tests) ; **ajoutés** : `test_exponentielles_logarithmes_json_filiere_m` (entrées de l'instantané M, `resoudre_json(…, "M")`
  strict et sans non-fini) et `test_exercices_d_exponentielles_logarithmes` (filières C et M, chaque niveau, 20 tirages : l'exercice et son
  corrigé en JSON strict).
- **`MIGREES`** : **ajouté** (la page passe les trois tests : aucune phrase de corrigé, `outil.js`, SOC-10).
- **Jeu moteur (`test_instantanes.py`)** : **exception nommée** (`test_outils_du_site.EXCEPTIONS`, vérifiée utile par
  `test_exceptions_utiles`). Raison : les exponentielles n'ont pas de sortie de moteur unique, l'aiguillage entre `exp_log` et `exp_log_m`
  (filières, variantes, voie des exposants) est dans l'adaptateur `resoudre_el.py` ; un instantané « moteur » obligerait à recopier cet
  aiguillage dans le test (copie d'une fonction, CLAUDE.md) ou à figer des structures internes ; le jeu moteur (T01) a servi de référence
  aux migrations T17 à T20, que l'outil, né avec `resoudre()`, n'a pas eues ; le jeu resoudre (`instantanes/resoudre/exponentielles-
  logarithmes.json` et `-M.json`, 914 entrées chacun) couvre déjà tout l'outil. Donc aucun nouvel instantané.

### Tests ajoutés (aucun retiré ni renommé)

- `tests/python/test_outils_du_site.py` : `TestSourcesDesOutils::test_registre_et_manifeste`, `::test_ordre_de_sys_path` ;
  `TestClesDesDonnees::test_cles`, `::test_exceptions_utiles`, `::test_une_methode_par_outil`, `::test_un_instantane_par_outil`.
- `tests/python/test_json_strict.py` : `test_exponentielles_logarithmes_json_filiere_m`, `test_exercices_d_exponentielles_logarithmes`.
- `tests/python/test_lancer.py` (`TestRapide`) : `test_manifeste_et_registre_relancent_les_listes_derivees`,
  `test_liste_des_outils_illisible_relance_tout` ; `test_scripts_de_commande_relancent_test_lancer` a un sous-test de plus
  (`outils_du_site.py`, copié dans les dépôts jetables : `SCRIPTS`) ; le dépôt modèle a un `commun/registre.json`.
- `tests/pages/test_donnees_des_pages.py` : `TestDonneesDesPages::test_outils_et_variante_de_filiere`,
  `::test_cles_des_donnees_propres_a_un_outil`, `::test_une_methode_par_outil`, `::test_une_reference_par_outil`.

### Contre-épreuve (clés retirées ou ajoutées, en mémoire, aucun fichier touché)

Script `scratchpad/F3/contre_epreuve.py` : charge les modules, retire une clé, lance les classes de clés, remet la clé.

| Changement | Résultat |
|---|---|
| état réel (avant et après chaque essai) | passe |
| sans `factorisation` dans `test_instantanes.OUTILS` | échoue (`test_cles`, `test_un_instantane_par_outil`) |
| sans `exponentielles-logarithmes-M` dans `test_instantanes_resoudre.OUTILS` | échoue (`test_cles`, `test_un_instantane_par_outil`) |
| sans `exponentielles-logarithmes` dans `test_json_strict.OUTILS_ENTREES` | échoue (`test_cles`) |
| sans `etude-complete` dans `test_resoudre_import.EXEMPLE` | échoue (`test_cles`) |
| sans `factorisation` dans `TestDispositionDuClavier.PAGES` | échoue (`test_cles`) |
| sans `exponentielles-logarithmes` dans `test_vocabulaire.METHODES` | échoue (`test_cles`) |
| exp-log ajouté à `test_instantanes.OUTILS` (exception devenue inutile) | échoue (4 tests, dont `test_exceptions_utiles`) |
| outil « nouvel-outil » ajouté au manifeste, données non complétées | échoue (Python : 6 sous-tests de `test_cles` ; pages : 4 tests) |
| sans `exponentielles-logarithmes-M` dans `rendu.REDUIT` ; sans `factorisation` dans `CALCUL` ; sans `limites-asymptotes` dans `EXEMPLE` ; sans exp-log dans `INVALIDE` | échoue (`test_cles_des_donnees_propres_a_un_outil`), chacun |
| `simplexe` ajouté à `CALCUL` (outil en trop) | échoue |

### `liste` : mêmes sélections

- `scratchpad/F3/selections.py` (fonctions de `rapide`) sur 262 jeux : chaque fichier suivi seul, 16 fichiers fictifs (supprimés, nouvel
  outil, variante, référence inconnue…) et 5 combinaisons, avant (HEAD, avant toute modification) et après. Différences : le manifeste,
  le registre et leur couple (+62 tests Python : les dépendants de `outils_du_site`, voulu), `tests/python/outils_du_site.py` (n'existait
  pas), et 45 jeux à +1 test qui est toujours `test_outils_du_site.py` (nouveau test, dépendant des modules qu'il lit) ; pages identiques
  partout sauf `outils_du_site.py` (→ toutes : `rendu.py` l'importe).
- Ancien `lancer.py` (HEAD) et nouveau sur le **même arbre** (`scratchpad/F3/meme_arbre.py`, 185 jeux) : 3 différences seulement,
  `outils_du_site.py` (+ `test_lancer.py`, script copié), le manifeste et le registre (+62) ; `DOSSIERS_MOTEURS` et `OUTILS_PAGES`
  égaux, ordre des clés compris.

### Vérifications

- Dump (`dumps/F3`) : `diff -r --exclude=temps` avec le départ, aucune sortie, code 0 ; `dumps/F3-p1` (`--processus 1`) aussi. Temps
  (`--processus 1`) : identiques au tableau « Temps » (limites 5,97 s, étude 2,01 s, factorisation 1,90 s, exp-log 0,89 / 0,77 s,
  autres < 0,3 s).
- `git diff --exit-code main -- tests/python/instantanes tests/pages/references` : rien ; aucun nouveau fichier d'instantané.
- `sys.path` après `import moteurs` : identique (comparé avant / après).
- Suite d'avant commit : `PROCESSUS_PAGES=4 python3 tests/lancer.py complet --rapport <scratchpad>/rapports/F3` : code 0. Python
  1 381 passés + 1 xfail (1 382 collectés), 106 160 sous-tests, 86,1 s ; pages 127 passés, 2 407 sous-tests, 288,9 s. Aucun fichier
  changé pendant le lancement (empreintes de début = fin). `comparer_listes.py tests/reference <F3>` : seuls ajouts, les 37 tests de
  F1 et F2 et les 14 de F3 (10 Python, 4 pages), tous passés ; aucun test disparu ni renommé ; sous-tests en hausse seulement
  (Python 105 837 → 106 160 depuis F2 : `test_soc10` 5 → 6, `test_aucune_phrase_de_corrige_en_js` 88 → 99,
  `test_pages_migrees_sans_rendu_local` 5 → 6, `test_pages_utilisent_la_feuille_commune` 4 → 6, `TestVocabulairePages::test_pages`
  7 → 8, plus ceux des tests nouveaux ; pages 2 386 → 2 407, ceux de `test_donnees_des_pages.py`).

## F4 — R6 : garde-fous d'architecture

### Plan

1. `test_noyau.MOTEURS` étendu à `redaction_bh`, `exp_log`, `exp_log_m` ; un test réclame tout nouveau moteur d'outil.
2. `tests/python/test_imports.py` : graphe des imports internes extrait par `ast`, liste blanche exacte (`ARETES` + `EXCEPTIONS`
   nommées), couches de `docs/architecture.md` § 1 vérifiées mécaniquement, aucun cycle hors exception.
3. `test_manifeste.py` : aucun nom de fichier en double dans un manifeste (A8).
4. `rapide` : un `.py` des dossiers des moteurs relance `test_imports.py` et `test_noyau.py` (ils lisent les moteurs par leur chemin,
   sans les importer : le graphe de `rapide` ne les aurait pas trouvés).
5. Docs : `docs/architecture.md` (§ 1, A1, A8, § 4, § 5), `docs/choix-techniques.md` (fichiers à plat), docstring de `tests/lancer.py`.

### test_noyau (point 1)

- `MOTEURS` : 5 → 8 fichiers (`limites-asymptotes/redaction_bh.py`, `exponentielles-logarithmes/exp_log.py`, `exp_log_m.py`) ; aucun
  test renommé ni retiré ; les trois respectent déjà la frontière (aucun `ensemble_def`, aucun nom privé du noyau).
- **Ajouté** : `TestNoyau::test_tous_les_moteurs_d_outil_sont_surveilles` : les moteurs d'outil (les `.py` des dossiers d'outil du
  manifeste, sauf l'adaptateur, `module` du manifeste, et le dossier de la base `ensemble-definition`) = `MOTEURS`, dans les deux sens.

### Graphe des imports (point 2) : `tests/python/test_imports.py`

- **Modules** : tous les `.py` de `moteur/` et des dossiers d'outil du manifeste (`outils_du_site.dossiers_moteurs()`), 19 modules,
  `moteur/construire_roues.py` compris (script de construction des roues : aucun import interne, il compte comme une brique).
- **Extraction** (`ast`, rien n'est importé) : `import x`, `import x.y`, `from x import y`, relatifs (`from . import x`,
  `from .x import y`), `importlib.import_module("x")` et `__import__("x")`. « a -> b » : import exécuté au chargement (tête, corps de
  classe, `if`/`try` de tête, décorateurs, valeurs par défaut) ; « a ~> b » : paresseux (corps d'une fonction). Seules les cibles qui
  sont des modules du moteur font des arêtes. `TestExtraction::test_formes` vérifie chaque forme sur un source construit.
- **Liste blanche exacte : 45 arêtes**, 33 dans `ARETES` (chacune avec sa raison) et 12 dans 5 exceptions nommées (`EXCEPTIONS` :
  arêtes, motifs, règle, chantier) :

| Exception | Arêtes | Motif | Règle | Chantier |
|---|---|---|---|---|
| assemblage de l'Étude complète | `etude_complete -> derivee_variations`, `etude_complete -> limites_asymptotes`, `parties ~> derivee_variations`, `resoudre_ec -> resoudre_dv`, `resoudre_ec -> resoudre_la` | couches | A1, § 1 (voulue) | aucun : voulue |
| cycle `limites_asymptotes` ⇄ `redaction_bh` | `limites_asymptotes -> redaction_bh` (import de fin de fichier, l. 3839), `redaction_bh -> limites_asymptotes` | cycle | A1, A6 | R11 |
| cycle `exp_log` ⇄ `exp_log_m` | `exp_log ~> exp_log_m`, `exp_log_m -> exp_log`, `exp_log_m ~> exp_log` (`_GABARITS`, redondant) | cycle | A1, A6 | R11 |
| `parties` importe l'adaptateur `resoudre_ed` | `parties -> resoudre_ed` | couches | A1 | R11 |
| `resoudre_el` importe l'adaptateur `resoudre_ed` | `resoudre_el -> resoudre_ed` | couches | A1 | R11 |

- **Couches exprimées mécaniquement** (`couche`, `violation`) : couche 1 = `moteur/` et la base `ensemble_def` (rangée avec l'outil
  ED) ; couche 3 = le `module` de l'outil au manifeste ; couche 2 = les autres `.py` d'un dossier d'outil. Violations : importer une
  couche au-dessus ; un moteur ou un adaptateur qui importe un moteur ou un adaptateur d'un autre outil ; la base importée sans sa façade
  `noyau` par un module d'un autre outil (couche 2 ou 3). `test_couches` : aucune arête ne viole les couches hors exception de motif
  « couches » ; `test_aucun_cycle_hors_exceptions` : aucune arête sur un cycle hors exception de motif « cycle » ;
  `test_exceptions_utiles` : chaque arête d'une exception enfreint vraiment chacun de ses motifs (sinon elle va dans `ARETES`) ;
  `test_liste_bien_formee` ; `test_noms_de_modules_uniques` (un nom de module = un fichier, A8 étendu à tout le moteur).
- **Aucune violation nouvelle** : les seules arêtes qui violent les couches ou sont sur un cycle sont celles de § 1 (assemblage EC) et
  § 5 (cycles, `resoudre_ed`). Une seule n'était pas écrite nommément dans `docs/architecture.md` : `parties ~> derivee_variations`
  (paresseuse, rapport de la revue § 1.2, l. 1225) ; c'est le moteur de l'EC qui importe celui de DV, donc l'assemblage voulu de § 1 :
  rangée dans cette exception, et § 1 complété pour le dire.
- **Lecture des couches** : la table de § 1 permet à un moteur d'outil d'importer « les briques », dont `sortie` ; `redaction_bh` et
  `parties` importent `sortie` (blocs de leur rédaction). Le schéma de § 1 dit pourtant de la couche 3 « seule couche qui fabrique la
  sortie affichée (moteur/sortie.py) ». J'ai suivi la table (arêtes permises, dans `ARETES`) ; question pour l'enseignant.
- **Message** d'une arête nouvelle (relevé dans la contre-épreuve) : « arête(s) nouvelle(s) : factorisation -> exp_log
  (factorisation/factorisation.py l. 1887). Une arête nouvelle s'ajoute exprès, avec sa raison : dans ARETES de
  tests/python/test_imports.py si elle respecte les couches (docs/architecture.md, § 1 et règle A1) ; sinon elle se discute avant d'être
  écrite (CLAUDE.md, Architecture) et n'entre que comme exception nommée dans EXCEPTIONS (règle enfreinte, chantier qui la résorbe), après
  accord de l'enseignant, et dans docs/architecture.md § 5. Une arête disparue se retire de ARETES ou EXCEPTIONS (la liste reste
  exacte). »
- Le test ne lit pas `docs/` (choix de F1 : aucun test ne lit `docs/`) ; les exceptions de § 5 sont recopiées dans `EXCEPTIONS`, et
  § 5 renvoie au test.

### Noms à plat (point 3)

`TestManifeste::test_aucun_nom_de_fichier_en_double` (une vérification de `noms_en_double` sur une liste construite, puis un sous-test
par outil). Aucun doublon aujourd'hui.

### rapide (point 4)

`LECTEURS_DES_MOTEURS = (test_imports.py, test_noyau.py)` dans `tests/lancer.py`, relancés quand un `.py` d'un dossier des moteurs
(`DOSSIERS_MOTEURS`) est modifié, nouveau ou supprimé ; filtrés par `existe`, donc sans effet sur les dépôts d'essai qui ne les ont
pas. `TestRapide::test_moteur_relance_les_lecteurs_des_moteurs` (6 sous-tests : moteur d'outil, brique, page et module de tests sans
effet, module nouveau non suivi, module supprimé puis `--depuis HEAD~1`). Phrase de CLAUDE.md proposée dans `suivi.md`.

### Contre-épreuve

Script `scratchpad/F4/contre_epreuve.py` : pour chaque cas, copie du dépôt (sans `.git`, `docs/`, roues) dans un dossier jetable, une
modification, les tests visés ; le dépôt réel n'est pas touché.

| Modification (dans la copie) | Résultat |
|---|---|
| aucune (état réel) | passe (13 tests, 478 sous-tests) |
| `import exp_log` en tête de `factorisation.py` | échoue : `test_aretes_figees`, `test_couches` (moteur d'un autre outil) |
| `import resoudre_ed` dans une fonction de `exp_log.py` | échoue : `test_aretes_figees`, `test_couches` (`exp_log ~> resoudre_ed`) |
| `import sortie` dans une fonction de `noyau.py` (permise par les couches) | échoue : `test_aretes_figees` seul |
| `from . import resoudre_la` dans `derivee_variations.py` | échoue : `test_aretes_figees`, `test_couches` |
| `importlib.import_module('limites_asymptotes')` dans `factorisation.py` | échoue : `test_aretes_figees`, `test_couches` |
| `parties.py` sans son `from nombres import` (arête disparue) | échoue : `test_aretes_figees` |
| `factorisation -> exp_log` dans le code ET dans `ARETES` | échoue : `test_couches` |
| `parties ~> etude_complete` dans le code ET dans `ARETES` (cycle dans un outil) | échoue : `test_aucun_cycle_hors_exceptions` (2 arêtes) |
| `exp_log` sans son import de `exp_log_m`, arête retirée de l'exception | échoue : `test_exceptions_utiles` (les 2 arêtes restantes ne sont plus sur un cycle) |
| `resoudre_dv -> sortie` déplacée dans une exception « couches » | échoue : `test_exceptions_utiles` |
| `limites-asymptotes/sortie.py` créé | échoue : `test_noms_de_modules_uniques` |
| `factorisation/noyau.py` ajouté au manifeste de la factorisation | échoue : `test_aucun_nom_de_fichier_en_double` (factorisation) |
| `exponentielles-logarithmes/nouveau.py` créé | échoue : `test_tous_les_moteurs_d_outil_sont_surveilles` |
| `import ensemble_def` dans `exp_log_m.py` | échoue : `test_les_moteurs_n_importent_que_de_noyau` (exp_log_m) |
| `from noyau import _prive` dans `redaction_bh.py` | échoue : `test_aucun_nom_prive_importe_du_noyau`, `test_les_noms_pris_par_les_moteurs_existent_dans_le_noyau` |

### Tests ajoutés (aucun retiré ni renommé)

- `tests/python/test_imports.py` (nouveau) : `TestGrapheDesImports::test_noms_de_modules_uniques`, `::test_aretes_figees`,
  `::test_liste_bien_formee`, `::test_couches`, `::test_aucun_cycle_hors_exceptions`, `::test_exceptions_utiles` ;
  `TestExtraction::test_formes`. Durée : environ 1,4 s avec `test_noyau.py` et le test du manifeste.
- `tests/python/test_noyau.py` : `TestNoyau::test_tous_les_moteurs_d_outil_sont_surveilles` ; sous-tests en hausse (MOTEURS 5 → 8).
- `tests/python/test_manifeste.py` : `TestManifeste::test_aucun_nom_de_fichier_en_double`.
- `tests/python/test_lancer.py` : `TestRapide::test_moteur_relance_les_lecteurs_des_moteurs`.

### Vérifications

- Dump (`dumps/F4`) : `diff -r --exclude=temps` avec le départ, aucune sortie, code 0 ; `dumps/F4-p1` (`--processus 1`) aussi. Temps
  (`--processus 1`) : identiques au tableau « Temps » (limites 5,92 s, étude 2,02 s, factorisation 1,89 s, exp-log 0,89 / 0,77 s,
  autres < 0,3 s). Aucun code de moteur touché.
- `git diff --exit-code main -- tests/python/instantanes tests/pages/references` : rien ; aucun nouvel instantané.
- `rapide` sur l'arbre avant la suite : 75 passés, 756 sous-tests, 4 s (fumée, `test_imports`, `test_lancer`, `test_noyau`).
- Suite d'avant commit : `PROCESSUS_PAGES=4 python3 tests/lancer.py complet --rapport <scratchpad>/rapports/F4` : code 0. Python
  1 391 passés + 1 xfail (1 392 collectés), 106 298 sous-tests, 93,5 s ; pages 127 passés, 2 407 sous-tests, 291,9 s. Aucun fichier
  touché pendant le lancement. `comparer_listes.py tests/reference <F4>` : seuls ajouts, ceux de F1 à F3 et les 10 de F4 ci-dessus, tous
  passés ; aucun test disparu ni renommé ; sous-tests en hausse seulement (depuis F3 : `test_les_moteurs_n_importent_que_de_noyau`
  5 → 8, `test_aucun_nom_prive_importe_du_noyau` et `test_les_noms_pris_par_les_moteurs_existent_dans_le_noyau` 141 → 155, plus ceux
  des tests nouveaux : 106 160 → 106 298) ; pages identiques à F3 nom par nom.

## Contrôles du chef d'orchestre

- F0 `0cb5a64` : verifier ACCEPTÉ (Python 1 335 / 105 807 sous-tests, pages 123 / 2 386, identiques à la référence) ; rapide --depuis HEAD~1 : 22 passés, 224 sous-tests, 2 s (seuls fumée + docs) ; dump = départ.
- F1 `d4837d6` : verifier ACCEPTÉ (Python 1 354 + 1 xfail / 105 813 sous-tests, pages 123 / 2 386 ; +20 tests test_lancer annoncés) ; rapide --depuis HEAD~1 : 42 passés, 230 sous-tests, 4 s ; dump = départ ; instantanés/références inchangés.
- F2 `7838091` : verifier ACCEPTÉ (Python 1 371 + 1 xfail / 105 837 sous-tests, pages 123 / 2 386 ; +17 tests annoncés) ; rapide --depuis HEAD~1 : 59 passés, 254 sous-tests, 4 s ; dump = départ ; instantanés/références inchangés. Deux fichiers non suivis apparus sous docs/chantiers/equations-2e-degre/ (pas du chantier, laissés tels quels).
- F3 `d936027` : verifier ACCEPTÉ (Python 1 381 + 1 xfail / 106 160 sous-tests, pages 127 / 2 407 ; +14 tests annoncés) ; rapide --depuis HEAD~1 : manifeste/outils touchés donc presque tout (Python 1 377 + 1 xfail, pages 127 à corpus réduit), vert, 359 s ; dump = départ ; instantanés/références inchangés.

## Temps

Temps natif de `resoudre_json` sur le corpus (somme des appels, `temps/temps.json`, `--processus 1`, PC, 05.11.2026) : la référence
pour la règle « hausse de plus de 50 % au-dessus de 0,1 s ». Ne comparer qu'à un lancement avec le même `--processus`.

| Outil | Filière | Entrées | Total (s) | Plus long appel (s) |
|---|---|---|---|---|
| ensemble-definition | – | 42 | 0,033 | 0,022 |
| derivee-variations | – | 33 | 0,27 | 0,08 |
| limites-asymptotes | – | 66 | 5,84 | 1,20 (`x*e^x/(1-e^x)`) |
| etude-complete | – | 22 | 2,05 | 0,33 |
| factorisation | – | 309 | 1,95 | 0,07 |
| exponentielles-logarithmes | C | 914 | 0,89 | 0,005 |
| exponentielles-logarithmes | M | 914 | 0,77 | 0,003 |

Mur : dump 4 s (12 processus), 13 s (1 processus) ; suite de référence 6 min 35 (Python 97,5 s, pages 297,8 s).
