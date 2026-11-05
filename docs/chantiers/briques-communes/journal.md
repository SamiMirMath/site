# Chantier « Briques communes » — journal

Détail du chantier (plans, tableaux, temps, rapports). La fiche courte est `suivi.md`.

## Consigne du chantier

Chantier `briques-communes` (R5 de la revue de structure), sur le PC, toutes les suites avec `PROCESSUS_PAGES=4`. Font foi :
`CLAUDE.md`, `docs/architecture.md` (A1–A9, § 5), `docs/chantiers/equations-2e-degre/decisions.md` (« Prérequis », D13, D25, E14, § 5,
P3), `docs/chantiers/revue-structure/rapport.md` (R5, § 4.2), `docs/methode-chantiers.md`.

PRINCIPE : aucune sortie existante ne change. Après chaque partie, `tests/outils/dump_sorties.py` est identique à l'octet au dump de
départ ; instantanés et références de pages inchangés.

- B0. Fiches suivi.md (courte) et journal.md ; référence rafraîchie (lancer.py reference) ; dump de départ.
- B1. moteur/expr.py : l'arbre d'Exp-log, son tex ET le parseur (lecture d'une expression, y compris « membre = membre ») ; exp_log
  réexporte tout sous les mêmes noms, et les fonctions propres à Exp-log (log, ln, e) restent accessibles sans changer de nom. État
  décimal : aucune nouvelle variable globale dans moteur/ (A7) ; si l'état actuel d'Exp-log doit traverser, la solution est documentée
  et ajoutée aux exceptions nommées de docs/architecture.md §5. Manifeste mis à jour.
- B2. moteur/chaine.py : Eq, Rel, Ou, Texte, Chaine, Message, tex_element, tex_chaine, rangees_chaine, et seulement les propriétés
  génériques (autre côté, produit nul, mise en évidence) ; les PROP_* d'Exp-log restent dans exp_log. Options nouvelles, désactivées par
  défaut (donc Exp-log inchangé) : étiquette grise sans parenthèses, « impossible » sous un facteur constant, ligne de texte au milieu
  d'une chaîne.
- B3. Un vrai type de bloc « chaine » (A4 : constructeur dans sortie.py, schéma dans valider, rendu dans commun/rendu.js, test) pour les
  nouveaux outils. Le schéma permet une ligne pleine largeur au milieu de la chaîne, qui contient un texte ou un autre bloc (par exemple
  un tableau), sans casser l'alignement des ⇔ avant et après. Exp-log garde sa façon actuelle (HTML dans un bloc texte) : exception
  nommée dans architecture.md §5, à migrer plus tard.
- B4. CSS : .chaine passe de la page Exp-log à commun/composants.css (rendu identique) ; details ol passe dans commun/style.css.
- B5. Dans moteur/nombres.py, deux fonctions pures, avec paramètres explicites (A7), sans rebrancher aucun outil existant :
  approx(x, decimales=3) (TeX, E14/R13, D25) ; exact(x, decimaux_enonce=False). Tests croisés avec exp_log.tex_approx et
  exp_log._nb_exact ; écarts voulus listés nommément. Si D25 demande de changer une fonction existante de nombres.py et que cela change
  une sortie : ne pas le faire, poser la question.
- B6. oracle.racines(coeffs) dans tests/python/oracle.py (mpmath 50 chiffres, réelle si |Im| < 10⁻²⁰, regroupement à 10⁻²⁰ en
  multiplicité). Tests avec (x − 1)², x²(x + 8), x² + 1 et 17x² + 288x − 17.

VÉRIFICATIONS après chaque partie : dump identique, listes de tests égales à la référence (sauf ajouts annoncés), test_imports à jour
(nouvelles arêtes déclarées avec leur raison ; aucune arête chaine → exp_log, aucune arête moteur/ → un outil), test_manifeste vert,
test_largeurs avec CONNUS vide.

FIN : suite complète relancée par le chef d'orchestre, aussi avec MEMO=0, puis fusion dans main et push si tout est vert (fait par le
chef d'orchestre).

Organisation : section « Organisation de nuit » de `docs/methode-chantiers.md` (un sous-agent par partie, contrôle allégé par le chef
d'orchestre) ; règles d'exécution de la méthode, recopiées dans chaque consigne de sous-agent.

## B0 — fiches, référence, dump de départ

### Plan

1. `suivi.md` (court) et ce journal, seuls fichiers modifiés (sous `docs/`) pendant la suite de référence.
2. Référence : `PROCESSUS_PAGES=4 python3 tests/lancer.py complet --rapport <scratchpad>/briques/rapports/B0-ref` sur 5ce3f8c, puis
   `python3 tests/lancer.py reference <ce dossier>` ; contrôle par `git diff --stat tests/reference`.
3. Dump de départ (`tests/outils/dump_sorties.py`, `--processus 6`) et second dump, `diff -r --exclude=temps` (déterminisme) ; temps
   natif (`temps/temps.json`) noté comme référence de temps.
4. Suite complète d'avant commit (`complet --rapport <scratchpad>/briques/rapports/B0`), commit avec les deux fiches et
   `tests/reference/`.

`<scratchpad>` = `/tmp/claude-1000/-home-sami-ubuntu-site/4164342b-a2d3-4999-80ff-850ac94e5e5e/scratchpad`.

### Référence rafraîchie (étape 2)

- `PROCESSUS_PAGES=4 python3 tests/lancer.py complet --rapport <scratchpad>/briques/rapports/B0-ref` sur 5ce3f8c, arbre propre
  (seul `docs/chantiers/briques-communes/` non suivi) : code 0, 16 h 30 → 16 h 37 (6 min 25 de mur). Python 1 392 collectés,
  1 391 passés + 1 xfail, 106 244 sous-tests, 91,0 s ; pages 138 passés, 2 407 sous-tests, 294,5 s.
- `python3 tests/lancer.py reference <ce dossier>` : acceptée (code 0). Différences avec l'ancienne référence (96f183c, F0 de
  fondations) : uniquement le chantier fondations fusionné depuis, soit 57 tests Python et 15 tests de pages nouveaux (aucun retiré),
  et 11 lignes de sous-tests changées (dont les 3 baisses justifiées de F5 et les hausses de F3–F4 : `test_noyau`, `test_source_unique`,
  `test_tableaux_css`, `test_vocabulaire`). Mêmes nombres que la suite finale de fondations (fedc264).
  `git diff --stat tests/reference` : `collecte-pages.txt` (+15), `collecte-python.txt` (+57), `origine.txt`,
  `resultats-pages.txt` (+15), `resultats-python.txt` (+68 −11).

### Dump de départ (étape 3)

- Commandes (sur 5ce3f8c, arbre sans autre modification que `docs/chantiers/briques-communes/`) :

      python3 tests/outils/dump_sorties.py /tmp/claude-1000/-home-sami-ubuntu-site/4164342b-a2d3-4999-80ff-850ac94e5e5e/scratchpad/briques/dumps/depart --processus 6
      python3 tests/outils/dump_sorties.py /tmp/claude-1000/-home-sami-ubuntu-site/4164342b-a2d3-4999-80ff-850ac94e5e5e/scratchpad/briques/dumps/depart-2 --processus 6
      diff -r --exclude=temps /tmp/claude-1000/-home-sami-ubuntu-site/4164342b-a2d3-4999-80ff-850ac94e5e5e/scratchpad/briques/dumps/depart /tmp/claude-1000/-home-sami-ubuntu-site/4164342b-a2d3-4999-80ff-850ac94e5e5e/scratchpad/briques/dumps/depart-2

- Résultat : 17 fichiers, 4 148 sorties, 8,9 Mo, 4 s de mur chacun ; `diff` code 0, aucune sortie (déterminisme). Un troisième dump
  `un-processus` (`--processus 1`, 13 s) est aussi identique (`diff` code 0). Mêmes 17 fichiers et 4 148 sorties qu'au départ de
  fondations.
- **Commande de comparaison pour les parties suivantes** (dossier de sortie absent ou vide, hors du dépôt ; `<partie>` = B1, B2…) :

      python3 tests/outils/dump_sorties.py /tmp/claude-1000/-home-sami-ubuntu-site/4164342b-a2d3-4999-80ff-850ac94e5e5e/scratchpad/briques/dumps/<partie> --processus 6
      diff -r --exclude=temps /tmp/claude-1000/-home-sami-ubuntu-site/4164342b-a2d3-4999-80ff-850ac94e5e5e/scratchpad/briques/dumps/depart /tmp/claude-1000/-home-sami-ubuntu-site/4164342b-a2d3-4999-80ff-850ac94e5e5e/scratchpad/briques/dumps/<partie>

  Code 0 et aucune sortie exigés. Si une partie change le corpus (instantanés, pages, `rendu.py`), la liste des entrées change aussi :
  le signaler, ne pas « réparer » le dump. Pour le temps, relancer aussi avec `--processus 1` (dossier `<partie>-1`) et comparer au
  tableau « Temps » ci-dessous.

### Suite d'avant commit (étape 4)

`PROCESSUS_PAGES=4 python3 tests/lancer.py complet --rapport <scratchpad>/briques/rapports/B0` sur 5ce3f8c (fiches et
`tests/reference/` modifiés, non commités) : code 0, 16 h 39 → 16 h 45 (6 min 19 de mur). Python 1 391 passés + 1 xfail,
106 244 sous-tests, 94,3 s ; pages 138 passés, 2 407 sous-tests, 285,3 s. `python3 tests/comparer_listes.py tests/reference
<ce dossier>` : identique nom par nom (Python et pages). Aucun test ajouté par B0.

## Contrôles du chef d'orchestre

## Temps

Temps natif de `resoudre_json` sur le corpus (somme des appels, `temps/temps.json`, PC, 05.11.2026, commit 5ce3f8c) : la référence pour
la règle « hausse de plus de 50 % au-dessus de 0,1 s ». **Ne comparer qu'à un lancement avec le même `--processus`** (à 6 processus,
les temps sont environ 1,4 fois plus longs qu'à 1).

| Outil | Filière | Entrées | Total, 1 processus (s) | Plus long appel, 1 processus (s) | Total, 6 processus (s), `depart` / `depart-2` |
|---|---|---|---|---|---|
| ensemble-definition | – | 42 | 0,033 | 0,022 | 0,054 / 0,056 |
| derivee-variations | – | 33 | 0,265 | 0,081 | 0,365 / 0,364 |
| limites-asymptotes | – | 66 | 5,895 | 1,177 (`x*e^x/(1-e^x)`) | 7,89 / 8,35 |
| etude-complete | – | 22 | 1,998 | 0,29 (`sqrt(x^2-4)`) | 2,94 / 3,07 |
| factorisation | – | 309 | 1,883 | 0,063 | 2,72 / 3,02 |
| exponentielles-logarithmes | C | 914 | 0,888 | 0,005 | 1,235 / 1,239 |
| exponentielles-logarithmes | M | 914 | 0,764 | 0,003 | 1,055 / 1,056 |

Mur : dump 4,2 s (6 processus), 12,8 s (1 processus) ; suite de référence 6 min 25 (Python 91,0 s, pages 294,5 s).
