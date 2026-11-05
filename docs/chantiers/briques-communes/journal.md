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

## B1 — `moteur/expr.py` : arbre, TeX, parseur

### Plan

1. Lecture : `exp_log.py` § 1 à 4 (arbre, TeX, tokeniseur, analyseur). L'état décimal (`_DECIMAUX`) n'est lu que par `_nb_exact`
   (§ 8 et suivants) et posé par `_avec_decimaux` et `preparer_application` : ni l'arbre, ni le TeX, ni le parseur ne le lisent. Il
   ne traverse donc pas : il reste dans `exp_log`, la brique n'a aucun état (A7).
2. `moteur/expr.py` (générique, n'importe que `noyau` pour `ErreurSaisie` et `nombres`) : `Noeud`, `Nb`, `Var`, `Pi`, `Neg`, `Op`,
   `Pow`, `Fn`, `Defini`, `variables` ; `tex`, `tex_saisie` et leurs aides ; `Tok`, `tokeniser`, `Parseur`, `lire_membres`
   (« membre = membre » : déjà lu par `lire_membres`, rien à ajouter), avec un **lexique** explicite (`Lexique`, paramètre des
   fonctions de lecture) : fonctions lues, construction de leurs nœuds, lettres réservées, π, %, messages à exemple.
3. Ce qui est propre à Exp-log reste dans `exp_log` et s'y branche : `E` et `Log` (sous-classes de `expr.Noeud`, qui s'écrivent
   elles-mêmes par `ecrire_tex` ; deux attributs de classe remplacent les `isinstance(…, E)` / `Log` du TeX), `contient_e`, la
   lecture de log/ln/exp/log_a (`_fonction`, `_base`, `_base_entre_parentheses`), `LEXIQUE` d'Exp-log ; `tokeniser`,
   `lire_membres` et `_Parseur` deviennent des enveloppes d'une ligne (même nom, même signature, `LEXIQUE` d'Exp-log).
4. Réexport : chaque nom déplacé reste accessible dans `exp_log` sous son nom (`exp_log.X is expr.X`), les noms privés compris
   (`_nom_tex`, lu par `exp_log_m`, etc.).
5. Manifeste (`moteur/expr.py` pour l'outil EL), `test_imports` (`exp_log -> expr`, `expr -> noyau`, `expr -> nombres`),
   `architecture.md` (§ 1, § 5), docstrings ; `tests/python/test_expr.py`.
6. Vérifications : dump `B1` comparé au départ, temps (`B1-1`), `test_imports`, `test_manifeste`, tests EL, puis suite complète.

### Exécution

- **`moteur/expr.py`** (nouveau, 511 lignes) : `Noeud` (avec `ecrire_tex` et deux attributs de classe, `LETTRE` et
  `BASE_ENTRE_PARENTHESES`), `Nb`, `Var`, `Pi`, `Neg`, `Op`, `Pow`, `Fn`, `Defini`, `variables` ; `tex`, `tex_saisie`, `nb_tex`,
  `comme_somme`, `entre_parentheses`, `nom_tex`, `DEBUT_COLLABLE` ; `Tok`, `Lexique`, `LEXIQUE_COMMUN`, `lire_fonction`,
  `fonction_inconnue`, `lire_nom`, `tokeniser`, `lire_nombre`, `lire_pourcentage`, `Parseur`, `lire_membres`, tables `MINUSCULES`,
  `NOM_INDEXE`, `SYMBOLES`, `OPERATEURS`, `INEGALITES` et trois messages (`MESSAGE_INEQUATION`, et les messages par défaut du lexique
  commun `MESSAGE_EXPOSANT_COMMUN`, `MESSAGE_VIDE_COMMUN`, affichés par aucun outil aujourd'hui). Code repris tel quel d'exp_log ;
  seuls changements : les `isinstance(…, (Var, E))` et `isinstance(…, (Op, Neg, Log, Pow))` du TeX deviennent les attributs de classe ;
  les nœuds inconnus de la brique passent par `ecrire_tex` (TeX) et par leurs champs-nœuds (`variables`) ; ce que la lecture savait
  d'Exp-log devient un champ du `Lexique` ; `MINUSCULES` et `SYMBOLES` sont en lecture seule (`MappingProxyType`, même lecture).
- **Lexique** (paramètre explicite, `namedtuple` immuable) : `fonctions`, `lire_fonction` (hook de lecture d'un nom de fonction),
  `noeud_fonction`, `lettres_reservees`, `noeud_lettre`, `lire_pi`, `message_pourcentage` (None : % non lu), `message_exposant`,
  `message_vide`. Le lexique commun ne lit que sqrt et √ : ni log, ln, exp, ni e (une lettre comme une autre), ni π, ni %.
- **« membre = membre »** : `lire_membres(texte, lexique)` le lisait déjà (`(g, d)`, ou `(expression, None)` sans « = ») : aucune
  fonction nouvelle ; testé dans la brique (`x^2 + 7x = 18`, `4x + 32 = x²`, `(x + 1)(x + 3) = 15`, `45u + 12 = 12u^2`, erreurs).
- **exp_log** : garde `E`, `Log` (sous-classes de `expr.Noeud`, avec `ecrire_tex`), `contient_e`, `_fonction`, `_base`,
  `_base_entre_parentheses`, `_BASE_SOULIGNEE`, `_BASE_COLLEE`, et ajoute `_FONCTIONS`, `_lire_fonction`, `_noeud_fonction`,
  `_noeud_lettre`, `LEXIQUE` ; `tokeniser(texte)`, `_Parseur(toks)`, `lire_membres(texte)` deviennent des enveloppes d'une ligne
  (même signature). Réexport : tous les noms déplacés sont les mêmes objets (`exp_log.X is expr.X`), y compris les privés
  (`_nb_tex`, `_comme_somme`, `_entre_parentheses`, `_nom_tex` lu par exp_log_m, `_DEBUT_COLLABLE`, `_MINUSCULES`, `_NOM_INDEXE`,
  `_SYMBOLES`, `_OPERATEURS`, `_INEGALITES`, `_nombre`, `_pourcentage`). Non réexportés, faute d'utilisateur et parce que leur
  signature prend maintenant le lexique : `_fonction_inconnue` et `_lire_nom` (devenus `expr.fonction_inconnue` et `expr.lire_nom`).
  L'import de `nombres` d'exp_log est gardé tel quel (noms `MOTIF_*`, `nettoyer_saisie` toujours accessibles).
- **État décimal** : `_DECIMAUX` n'est lu que par `_nb_exact` ; ni l'arbre, ni le TeX, ni la lecture ne le lisent. Il ne traverse
  donc pas : il reste dans exp_log, la brique n'a aucune variable de module modifiée ni aucun conteneur modifiable (testé). Pas
  d'exception nouvelle ; la ligne `exp_log._DECIMAUX` de `architecture.md` § 5 le précise.
- **Arêtes** (ARETES de `test_imports.py`, aucune exception) : `exp_log -> expr`, `expr -> noyau` (`ErreurSaisie`, même classe que
  celle qu'attrapent les adaptateurs), `expr -> nombres`. Aucune arête `moteur/` → un outil (la brique n'importe pas exp_log).
- **Manifeste** : `moteur/expr.py` ajouté à l'outil exponentielles-logarithmes (seul outil qui charge exp_log), après `nombres.py` ;
  aucun nom en double (A8) ; `test_manifeste` vert (complet et minimal).
- **test_noyau** : rien à changer (il surveille les moteurs d'outil, `MOTEURS` calculé ; une brique n'y entre pas). Son équivalent pour
  la brique (aucun nom privé importé d'`expr` par un moteur d'outil) est dans `test_expr.py`.
- **Docs** : `architecture.md` § 1 (expr au présent) et § 5 (lignes `_DECIMAUX` et « 3 parseurs, 2 arbres » : mêmes nombres, l'arbre
  et le parseur d'EL sont maintenant ceux d'`expr`) ; docstrings d'exp_log et d'expr.

### Tests ajoutés

`tests/python/test_expr.py` : 21 tests, 144 sous-tests. La brique seule (`TestArbre` 4, `TestTex` 4, `TestLecture` 5 : arbre, TeX,
« membre = membre », 23 erreurs de saisie, lexique commun sans Exp-log, lexique d'un outil fictif), l'absence d'état (`TestSansEtat` 2),
le réexport (`TestReexportParExpLog` 6 : 25 noms identiques, exp_log_m, nœuds `E`/`Log`, noms propres à EL absents de la brique,
enveloppes, aucun nom privé importé d'`expr`). `test_imports` : 3 arêtes de plus (sous-tests de `test_liste_bien_formee`).

### Vérifications

- Dump `B1` (`--processus 6`) : `diff -r --exclude=temps depart B1` code 0, aucune sortie (fait deux fois : avant et après le passage
  de `MINUSCULES`/`SYMBOLES` en lecture seule). Dump `B1-1` (`--processus 1`) : identique aussi.
- Tests EL, instantanés, json_strict, vocabulaire, source unique (20 fichiers, `-n 6`) : 492 passés, 66 220 sous-tests.
  `test_imports`, `test_manifeste`, `test_noyau` : 20 passés, 538 sous-tests.
- Temps natif (`resoudre_json`, somme sur le corpus, 1 processus, comparé à `un-processus` de B0) :

| Outil | Filière | B0 (s) | B1 (s) | Plus long appel B0 / B1 (s) |
|---|---|---|---|---|
| ensemble-definition | – | 0,033 | 0,032 | 0,022 / 0,022 |
| derivee-variations | – | 0,265 | 0,265 | 0,081 / 0,082 |
| limites-asymptotes | – | 5,895 | 5,826 | 1,177 / 1,185 |
| etude-complete | – | 1,998 | 2,014 | 0,29 / 0,318 |
| factorisation | – | 1,883 | 1,888 | 0,063 / 0,063 |
| exponentielles-logarithmes | C | 0,888 | 0,911 (+2,6 %) | 0,005 / 0,005 |
| exponentielles-logarithmes | M | 0,764 | 0,772 (+1 %) | 0,003 / 0,004 |

  Aucune hausse de plus de 50 %. Mur du dump : 12,8 s (1 processus), 4,1 s (6 processus).
- Suite d'avant commit : `PROCESSUS_PAGES=4 python3 tests/lancer.py complet --rapport <scratchpad>/briques/rapports/B1`, code 0,
  17 h 02 → 17 h 08 (6 min 11). Python 1 413 collectés, 1 412 passés + 1 xfail, 106 250 sous-tests ; pages 138 passés, 2 407
  sous-tests, 284,2 s (identiques nom par nom). `comparer_listes` contre `tests/reference` : 21 tests nouveaux (`test_expr.py`), aucun
  disparu ; sous-tests : `test_imports` (liste bien formée) 83 → 89, `test_manifeste_minimal` 34 → 35, gardes `memo` et
  `memo_racines` 19 → 20 (un module de plus), `test_vocabulaire` (littéraux des moteurs) 8 652 → 8 694 ; une baisse justifiée dans
  `suivi.md` : `test_exp_log` (littéraux d'exp_log.py) 1 215 → 1 026, les littéraux déplacés étant lus dans moteur/expr.py par
  `test_vocabulaire` avec le même détecteur.

## Contrôles du chef d'orchestre

- B0 `b296741` : verifier ACCEPTÉ (Python 1 392 / 106 244 sous-tests, pages 138 / 2 407, identiques à la référence) ; rapide --depuis HEAD~1 : 23 passés, 243 sous-tests, 3 s (fumée + docs).

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
