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

## Contrôles du chef d'orchestre

- F0 `0cb5a64` : verifier ACCEPTÉ (Python 1 335 / 105 807 sous-tests, pages 123 / 2 386, identiques à la référence) ; rapide --depuis HEAD~1 : 22 passés, 224 sous-tests, 2 s (seuls fumée + docs) ; dump = départ.

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
