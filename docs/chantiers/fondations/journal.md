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

## Contrôles du chef d'orchestre

(vide)

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
