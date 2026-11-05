# Chantier « Fondations » — suivi

Branche `fondations` (depuis `main` 96f183c), PC (WSL2), `PROCESSUS_PAGES=4`. Principe : aucun changement visible pour les élèves.
Consigne complète, plan et détails : `journal.md`. La consigne du chantier tient lieu de `decisions.md`.

## Résumé (05.11.2026, PC, 12 h 09 → 14 h 50)

Sept parties, sept commits, toutes acceptées par le contrôle allégé (`verifier` ACCEPTÉ, `rapide --depuis HEAD~1` vert, dump brut
identique au départ à l'octet, instantanés et références de pages inchangés). Aucun changement visible pour les élèves : aucune page,
aucun texte affiché, aucune sortie de moteur ne change (4 148 sorties brutes de `resoudre_json`, `apercu_json`, `controle_json`,
`exercice_json` comparées après chaque partie).

| Partie | Commit | Sous-agent | Tests ajoutés |
|---|---|---|---|
| F0 fiches, référence rafraîchie, `dump_sorties.py` | `0cb5a64` | 16 min | — |
| F1 `verifier` (docs/ ignoré, baisses justifiées) | `d4837d6` | 14 min | 20 |
| F2 `rapide` (reste de R4) | `7838091` | 22 min | 17 |
| F3 R1 une seule liste des outils | `d936027` | 22 min | 14 |
| F4 R6 garde-fous d'architecture | `86207df` | 16 min | 10 |
| F5 R3 ménage | `df8ff3b` | 18 min | 0 (3 baisses de sous-tests justifiées ci-dessous) |
| F6 copie locale de KaTeX, garde-fou réseau | `fedc264` | 17 min | 11 |

Suite finale (chef d'orchestre, sur `fedc264`, `PROCESSUS_PAGES=4`) : Python 1 391 passés + 1 xfail, 106 244 sous-tests (97 s) ; pages
138 passés, 2 407 sous-tests (295 s) ; 6 min 34 de mur ; `verifier` ACCEPTÉ ; `comparer_listes` avec `tests/reference` : seulement des
ajouts et les 3 baisses justifiées. Même suite avec `MEMO=0` : listes identiques nom par nom (6 min 50).

Questions : neuf, ci-dessous. Six sont des phrases proposées pour CLAUDE.md (non modifié) ; trois à trancher : renommer les « (R14) »
internes en RL (F5), `sortie.py` permis aux moteurs d'outil ou non (F4), Google Fonts en copie locale ou non (F6). À confirmer (« À relire ») :
l'exception exp-log du jeu moteur (F3), le maintien d'`etudier_json` de DV et LA (F5).
Hors chantier : deux fichiers non suivis sont apparus pendant la session sous `docs/chantiers/equations-2e-degre/`
(`decisions (1).md:Zone.Identifier`, `decisions.md.md`) ; non touchés, non commités.

## État des parties

| Partie | Contenu | État | Commit |
|---|---|---|---|
| F0 | Fiches, référence rafraîchie, `tests/outils/dump_sorties.py`, dump de départ | faite (suite verte) | voir `git log` |
| F1 | `verifier` : docs/ ignoré, baisse de sous-tests justifiée ici ; `test_lancer.py` | faite (suite verte) | voir `git log` |
| F2 | `lancer.py rapide` (reste de R4) : `-z`, supprimés, donnees/, instantanés, pages, références, scripts | faite (suite verte) | voir `git log` |
| F3 | R1 : `tests/python/outils_du_site.py` (registre + manifeste), listes dérivées, clés vérifiées ; exp-log dans `MIGREES` et `test_json_strict` (filière M, exercices), exception nommée pour le jeu moteur | faite (suite verte) | voir `git log` |
| F4 | R6 : `test_noyau` étendu (+ moteurs réclamés), `tests/python/test_imports.py` (45 arêtes figées, 5 exceptions nommées, couches et cycles vérifiés), noms à plat uniques (`test_manifeste`) ; `rapide` relance ces tests quand un moteur change | faite (suite verte) | voir `git log` |
| F5 | R3, ménage : « anciennes » retirées (manifeste, `analyser_json`, `verifier_json`, `etudier_json` de l'EC), code mort du § 2.4, `qtex_` → `qtex`, « Ni logarithme… » à une source, docstrings, README, fantômes, RL1–RL20, `.gitignore`, quiz.md § 6 | faite (suite verte) | voir `git log` |
| F6 | Copie locale de KaTeX (`tests/pages/katex_local.py`, copie dans `tests/pages/katex-local/`, empreintes npm et jsDelivr) ; garde-fou réseau de `navigateur.py` (HTTPS interceptées, mandataire local qui refuse le reste, échec si une requête extérieure n'est pas servie) ; `test_katex_local.py` (11 tests) ; site publié inchangé | faite (suite verte) | voir `git log` |

## Vérification après chaque partie

Dump brut comparé au dump de départ (commande exacte dans `journal.md`, section F0), instantanés et références inchangés, listes de
tests égales à la référence (sauf ajouts annoncés).

## Questions pour l'enseignant

- **F1, `CLAUDE.md` (description de `verifier`, devenue inexacte)** : remplacer « qu'aucun autre fichier n'était modifié ou non suivi
  pendant le lancement (hors suivi.md / journal.md de chantier et CLAUDE.md), que les codes valent 0 et qu'aucun test n'a disparu,
  n'est sauté en plus, ne se dégrade ni ne perd de sous-tests par rapport à la référence (par défaut tests/reference) » par :
  « qu'aucun autre fichier n'était modifié ou non suivi pendant le lancement (hors `docs/`, et CLAUDE.md hors du commit : ignorés,
  toujours listés), que les codes valent 0 et qu'aucun test n'a disparu, n'est sauté en plus ni ne se dégrade par rapport à la
  référence (par défaut tests/reference) ; une baisse de sous-tests n'est acceptée que justifiée dans le suivi.md du chantier
  (section « Variations de sous-tests », ligne `` - `<test>` : <avant> → <après> : <raison> ``, nombres exacts ; `--suivi <fichier>`
  pour un autre fichier) » ; et `verifier <dossier> [--reference <dossier>] [--suivi <fichier>]` en tête de la ligne.

- **F2, `CLAUDE.md` (description de `rapide`, devenue incomplète)** : remplacer « dépendances d'import comprises) plus les tests de
  fumée (manifeste, accueil, source unique) ; » par « dépendances d'import comprises, fichiers supprimés aussi, noms lus avec `-z`)
  plus les tests de fumée (manifeste, accueil, source unique) ; un fichier de `tests/python/donnees/`, d'instantanés ou de références
  de pages relance les tests qui nomment ce dossier (tous s'il n'y en a aucun) ; une page, un `cas*.py` ou un instantané relance aussi
  `test_instantanes*` et `test_json_strict` ; un script de commande (`lancer.py`, `verifier.py`, `comparer_listes.py`,
  `rapport_pytest.py`) relance `test_lancer.py` ; » ; et « dont un moteur Python chargé par la page change » par « dont un moteur
  Python chargé par la page, la référence de page ou l'instantané resoudre change ».

- **F3, `CLAUDE.md` (description de `rapide`)** : ajouter après « un script de commande (…) relance `test_lancer.py` ; » (phrase de
  F2) : « `moteur/manifeste.json` ou `commun/registre.json` relance les dépendants de `tests/python/outils_du_site.py` (la liste des
  outils, dont dérivent les listes des tests) ; » et, dans la liste des scripts de commande, `outils_du_site.py`.

- **F4, CLAUDE.md (description de `rapide`)** : ajouter après la phrase de F3 : « un `.py` des dossiers des moteurs relance
  `test_imports.py` et `test_noyau.py` (ils lisent les moteurs par leur chemin) ; ».

- **F5, CLAUDE.md (ligne « Suite au 05.11.2026 »)** : elle cite encore l'ancienne référence (c9b257f : 1 318 tests Python,
  101 952 sous-tests ; 123 tests de pages, 2 386 sous-tests) ; la référence de ce chantier (F0) est 1 335 tests Python (dont 1 xfail),
  105 807 sous-tests, 123 tests de pages, 2 386 sous-tests ; après F5 : 1 392 (dont 1 xfail), 106 244 ; 127, 2 407. R1–R20 y est déjà juste.
- **F5, RL1–RL20** : les règles de `redaction-limites-3m.md` sont renommées dans les documents actifs et les commentaires ; restent sous
  l'ancien nom les chaînes internes du moteur (« (R14) », « (R18) ») et l'identifiant `viole_r14` (sorties à l'octet), et les archives de
  chantier. Les renommer aussi (sans effet visible) ?
- **F4, couches : un moteur d'outil peut-il importer `moteur/sortie.py` ?** `redaction_bh` et `parties` le font. La table de
  `docs/architecture.md` § 1 le permet (« les briques ») ; le schéma de § 1 dit des adaptateurs « seule couche qui fabrique la sortie
  affichée ». J'ai suivi la table : ces deux arêtes sont dans `ARETES` (permises). Si la règle est « sortie réservée aux adaptateurs »,
  elles deviennent une exception nommée (motif « couches ») et `violation` le vérifie.

- **F6, CLAUDE.md (Commandes de test)** : remplacer « Première installation sur une machine : python3 tests/pages/pyodide_local.py (une
  fois par version de Pyodide). » par « Première installation sur une machine : python3 tests/pages/pyodide_local.py et python3
  tests/pages/katex_local.py (une fois par version de Pyodide ou de KaTeX ; sans ces copies, les tests de pages échouent avec la commande à
  lancer). Aucune requête des tests de pages ne quitte la machine : une ressource extérieure non servie par ces copies fait échouer. »
- **F6, Google Fonts de l'accueil** : pendant les tests, la feuille est servie vide (police de repli), comme la balise GoatCounter ; aucun
  test ne mesure l'accueil au pixel. Faut-il plutôt une copie locale de Source Serif 4 (pas d'empreinte publiée par Google) ?

## À relire par l'enseignant

- **F6** : aucun instantané, aucune référence, aucune page modifiée. Ressources extérieures des pages et ce qui les sert pendant les tests :
  tableau dans `journal.md` (F6). Chrome des tests lancé avec un mandataire local et sans services de Google (options listées dans
  `journal.md`) ; `.github/workflows/tests.yml` : copie de KaTeX en cache (à voir à la prochaine CI).

- **F5** : aucun instantané, aucune référence, aucun texte affiché modifié (dump identique à l'octet). Documents changés : `docs/README.md`
  (sommaire complet, commandes par `lancer.py`, R1–R20, `[auto-js]` « prévu »), `ensemble-definition/README.md`, `docs/taches.md` et
  `docs/choix-techniques.md` (fichiers fantômes), `redaction-limites-3m.md` (règles **RL1–RL20**, et leurs renvois dans `a-valider.md` et
  `limites-asymptotes.md`), `quiz.md` § 6 (l'onglet = chantier séparé, P5b abandonnée). Gardé, à confirmer : `etudier_json` de DV et LA
  (interface de test, raison dans `journal.md`).

- Aucun instantané ni texte affiché modifié (F0 à F4) ; aucun nouvel instantané.
- **F3, `docs/architecture.md`** (document validé) : § 4 « Ajouter un outil » réécrit (environ 4 fichiers côté site et 10 côté tests,
  tous réclamés par un test ; ce qui dérive désormais) et garde-fou de A3 (« à créer » → les fichiers de F3).
- **F3, exp-log hors du jeu moteur** (`test_instantanes.py`) : exception nommée dans `tests/python/test_outils_du_site.py`
  (`EXCEPTIONS`), raison dans `journal.md` (pas de sortie de moteur unique ; le jeu resoudre C et M couvre l'outil). Répond à la
  question 4 de la revue de structure ; à confirmer.
- **F4, `docs/architecture.md`** (document validé) : garde-fous de A1 et A8 (« à créer » → les tests de F4), § 5 (« le test d'imports »
  → `tests/python/test_imports.py`, `EXCEPTIONS`), § 4 (arêtes nouvelles dans `ARETES`), § 1 : `parties ~> derivee_variations`
  (import paresseux, non nommé jusqu'ici) rangé dans l'exception voulue « assemblage de l'Étude complète ». Aucune violation nouvelle.

## Variations de sous-tests

Lue par `verifier` (depuis F1 ; voir sa docstring, point (d)). Format, une ligne par test, commençant en début de ligne par un
tiret : `` - `<identifiant pytest complet>` : <avant> → <après> : <raison> `` (« -> » vaut « → »), par exemple
`` - `tests/python/test_x.py::TestY::test_z` : 120 → 118 : deux entrées en double retirées (F5) ``. <avant> et <après> sont les
nombres de sous-tests passés de la référence et du lancement, exactement ceux que `verifier` affiche ; sinon refus. Une baisse non
justifiée ici fait refuser `verifier` ; un test disparu, échoué ou sauté en plus est refusé même justifié.

- `tests/python/test_exp_log.py::TestVouvoiement::test_aucun_texte_du_fichier_ne_tutoie` : 1216 → 1215 : un littéral de moins dans exp_log.py, `MESSAGE_PI_EN_3C` (code mort retiré, F5)
- `tests/python/test_noyau.py::TestNoyau::test_noms_exportes_publics_et_memes_objets` : 59 → 58 : réexport `racine_rationnelle` retiré de moteur/noyau.py, importé par personne (F5)
- `tests/python/test_vocabulaire.py::TestVouvoiement::test_litteraux_des_moteurs` : 8706 → 8652 : 54 littéraux de code retiré (F5) : ensemble_def 23 (`INFO`, `POURQUOI`, `analyser_json`, `verifier_json`, `__all__`), limites_asymptotes 13, exp_log_m 7, redaction_bh 5, resoudre_ed 2, etude_complete, parties, resoudre_ec et exp_log 1 chacun

## Reprise après compactage

- Lire `CLAUDE.md`, ce fichier, puis `journal.md` (consigne du chantier, plan, section de la dernière partie).
- `git log --oneline main..fondations` : un commit par partie faite.
- Dump de départ : `/tmp/claude-1000/-home-sami-ubuntu-site/b574d683-7da7-4c53-a00c-237ca55256c7/scratchpad/dumps/depart`
  (hors du dépôt ; s'il a disparu, le refaire sur le commit F0 avec `tests/outils/dump_sorties.py`).
