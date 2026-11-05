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

## B2 — `moteur/chaine.py` : chaînes du corrigé, propriétés génériques, trois options

### Plan

1. Lecture : `exp_log.py` § 8 (`Eq`, `Rel`, `Positif`, `Texte`, `Ou`, `Chaine`, `tex_element`, `LIENS_TEX`, `tex_chaine`, `_gauche`,
   `rangees_chaine`, `PROP_*`) et § 10 (`Message`, `Car`, `Divise`). Trois choses propres à Exp-log y sont lues par le rendu commun :
   l'élément `Positif` (« u = valeur > 0 »), les justifications `Car` et `Divise`, et la coche après la note `PROP_BIEN_DEFINI`.
2. `moteur/chaine.py` (n'importe que `expr`) : `Eq`, `Rel`, `Ou`, `Texte`, `Chaine`, `Message`, `tex_element`, `LIENS_TEX`,
   `tex_chaine`, `rangees_chaine` (et `_gauche`), les trois propriétés génériques `PROP_AUTRE_COTE`, `PROP_PRODUIT_NUL`,
   `PROP_MISE_EN_EVIDENCE`. Ce qui est propre à Exp-log reste dans exp_log et se branche sans que la brique le connaisse (A7, sur le
   modèle des nœuds `E`/`Log` de B1) : `Positif` hérite de `chaine.Element` (il s'écrit lui-même, `ecrire_tex`) ; `Car` et `Divise`
   héritent de `chaine.Justification` (`ecrire_tex` après `\quad`, `ecrire_rangee` pour la colonne de droite) ; la coche devient un
   champ de la chaîne, `Chaine(…, coche=True)`, posé par exp_log là où la note est `PROP_BIEN_DEFINI` (et gardé par
   `exp_log_m._convertir_chaine`, qui recopie les chaînes). `LIENS_TEX` et `Rel.SIGNES` en lecture seule (`MappingProxyType`).
3. Trois options nouvelles, désactivées par défaut (sortie d'Exp-log identique) :
   - `etiquette_grise=False` (`tex_chaine`, `rangees_chaine`) : la propriété et la note sans parenthèses ; en TeX
     `\quad \textcolor{gray}{\text{ME}}` ;
   - `impossible=False` (`tex_element`, `tex_chaine`, `rangees_chaine`) : dans un « ou », une égalité entre deux nombres différents
     (le facteur constant du produit nul, `6 = 0`) s'écrit `\underbrace{6 = 0}_{\text{impossible}}`, comme le corrigé (Id_rem.pdf,
     2.9 a, c, e, f) ; le moteur ne marque rien lui-même : seule une égalité fausse entre deux nombres reçoit la mention ;
   - texte au milieu : `Chaine(…, textes={i: [contenu]})` ou `ajouter(…, texte_avant=contenu)` : une ligne pleine largeur avant
     l'élément i, dont le lien (⇔) relie toujours l'élément i − 1 à l'élément i ; dans les rangées, `LigneTexte(contenu)` (contenu
     tel quel : `Message`, texte, ou un bloc, pour B3) ; dans `tex_chaine`, `\quad <texte> \quad` avant le lien.
4. exp_log réexporte chaque nom déplacé (même objet) ; `Message.html` emporte son `escape` dans la brique (exp_log garde le sien,
   lu ailleurs).
5. Manifeste (`moteur/chaine.py` pour l'outil EL, après `expr.py`), arêtes `chaine -> expr` et `exp_log -> chaine` ;
   `architecture.md` § 1 et § 5 ; docstrings ; `tests/python/test_chaine.py` (brique seule, options activées et désactivées,
   branchements, absence d'état, réexport).
6. Vérifications : dump `B2` et `B2-1`, temps, `test_imports`, `test_manifeste`, tests EL ; suite complète ; variations de sous-tests.

### Exécution

- **`moteur/chaine.py`** (nouveau, n'importe que `expr` et la bibliothèque standard) : `Eq`, `Rel` (`SIGNES` en lecture seule), `Ou`,
  `Texte`, `Element`, `Justification`, `Chaine` (avec `coche` et `textes`), `Message`, `LigneTexte`, `tex_element`, `tex_message`,
  `LIENS_TEX` (lecture seule), `tex_chaine`, `_gauche`, `rangees_chaine`, `est_impossible`, `PROP_AUTRE_COTE`, `PROP_PRODUIT_NUL`,
  `PROP_MISE_EN_EVIDENCE`. Code repris tel quel d'exp_log ; seuls changements, sans effet sur la sortie : les `isinstance(…, Positif)`,
  `Divise`, `Car` deviennent `Element` / `Justification` (l'objet s'écrit lui-même), et la coche est lue sur `c.coche` au lieu de
  `c.note == PROP_BIEN_DEFINI`.
- **exp_log** : garde `Positif` (sous-classe de `chaine.Element`, `ecrire_tex`), `Car` et `Divise` (sous-classes de
  `chaine.Justification`, `ecrire_tex` et `ecrire_rangee`, mêmes textes qu'avant), les 44 autres `PROP_*` et `PROPRIETES` (qui
  contient toujours les trois génériques) ; la seule chaîne à note `PROP_BIEN_DEFINI` (carte « Vérification » de `logarithmique`)
  reçoit `coche=True`. Réexport : 13 noms, mêmes objets (`exp_log.X is chaine.X`) ; aucun nom privé de la brique n'est importé
  (`_gauche` n'était lu que par `rangees_chaine`). `exp_log_m._convertir_chaine` recopie aussi `coche` et `textes`. `_echapper` reste
  importé par exp_log (lu aussi plus bas, l. ~2800).
- **Arêtes** (ARETES, aucune exception) : `chaine -> expr`, `exp_log -> chaine`. Aucune arête `chaine -> exp_log`, aucune arête
  `moteur/` → un outil.
- **Manifeste** : `moteur/chaine.py` pour l'outil exponentielles-logarithmes (seul outil qui charge exp_log), après `moteur/expr.py`.
- **Docs** : `architecture.md` § 1 (chaine au présent) et § 5 (ligne « 2 classes `Chaine` » : `moteur/chaine.py` reprise d'EL, et
  celle de LA) ; docstrings d'exp_log et de chaine.

### Les trois options : forme proposée (à relire par l'enseignant)

Toutes désactivées par défaut ; corpus : Id_rem.pdf (2.9 a, c), decisions.md § 7.

1. **Étiquette grise** — `etiquette_grise=True` (`tex_chaine`, `rangees_chaine`). Rangées : la propriété sans parenthèses
   (`(r"\iff", "6(x^{2} - 1) = 0", "ME")`), le gris étant celui de la colonne `.prop` de la page (déjà `var(--muted)` dans la page EL ;
   B3/B4 pour la page commune) ; avec une note sur la même ligne : `"a ; b"` (au lieu de `"(a) (b)"`), coche comprise
   (`"a ; b \(\checkmark\)"`). TeX d'une ligne : `… = 0 \quad \textcolor{gray}{\text{ME}}` (au lieu de `\quad \text{(ME)}`). Une
   justification d'outil (`Car`, `Divise`) garde sa propre écriture.
2. **« impossible » sous le facteur constant** — `impossible=True` (`tex_element`, `tex_chaine`, `rangees_chaine`). Dans un « ou », une
   égalité entre deux nombres écrits différents (`Nb` ou `Neg(Nb)` : 6 = 0, −1 = 0) s'écrit
   `\underbrace{6 = 0}_{\text{impossible}}`, comme l'accolade du corrigé (2.9 a, c, e, f). La brique décide seule et ne marque qu'une
   égalité fausse entre deux nombres (`est_impossible`) : 0 = 0, x = 0, une égalité hors d'un « ou » ou avec un milieu ne reçoivent
   rien. Même TeX dans les rangées (colonne de l'expression).
3. **Ligne de texte au milieu** — `Chaine(…, textes={i: [contenu, …]})` ou `Chaine.ajouter(…, texte_avant=contenu ou [contenus])` :
   lignes pleine largeur avant l'élément i (1 ≤ i < nombre d'éléments, vérifié) ; le ⇔ de l'élément i le relie toujours à l'élément
   i − 1 (2.9 c : « Id. rem. A² − 2AB + B² avec A = 4z, B = 9. Vérification : … ✓ » entre la ME et `⇔ 3(4z − 9)² = 0`). Rangées : une
   rangée `LigneTexte(contenu)` (namedtuple à un champ : une page qui lit des triplets échoue au lieu de l'ignorer), contenu tel quel
   (`Message`, texte, ou un bloc comme le futur tableau S-P, pour B3) ; un lien « = » qui la suit commence une nouvelle ligne alignée
   (`\phantom`). TeX d'une ligne : `… \quad \text{Id. rem. }A^{2} - … \quad \iff 3(4z - 9)^{2} = 0` ; un bloc n'a pas de TeX : `TypeError`
   (rien de faux).

### Tests ajoutés

`tests/python/test_chaine.py` : 30 tests, 76 sous-tests. La brique seule (`TestElements` 3, `TestChaine` 5 : liens, égalités alignées,
note et coche, deux chaînes d'Exp-log écrites telles qu'avant la brique, options désactivées par défaut), les branchements
(`TestBranchements` 3 : élément et justification d'un outil fictif, `Positif`, `Car`, `Divise`), les options activées et désactivées
(`TestEtiquetteGrise` 3, `TestImpossible` 3, `TestTexteAuMilieu` 5, sorties attendues d'après Id_rem.pdf 2.9 a et c), l'absence d'état
et les imports (`TestSansEtat` 3), le réexport (`TestReexportParExpLog` 5 : 13 noms identiques, exp_log_m, noms propres à EL absents de
la brique, la coche posée exactement sur les notes `PROP_BIEN_DEFINI`, aucun nom privé importé de `chaine`). `test_imports` : 2 arêtes de
plus.

### Vérifications

- Dump `B2` (`--processus 6`) : `diff -r --exclude=temps depart B2` code 0, aucune sortie (fait deux fois, avant et après les
  dernières retouches). Dump `B2-1` (`--processus 1`) : identique aussi.
- Suite Python seule avant la suite complète (`-n 6`) : 1 412 passés + 1 xfail (sans test_chaine), puis test_chaine 30 passés.
- Temps natif (`resoudre_json`, somme sur le corpus, 1 processus, comparé à `un-processus` de B0) :

| Outil | Filière | B0 (s) | B2 (s) | Plus long appel B0 / B2 (s) |
|---|---|---|---|---|
| ensemble-definition | – | 0,033 | 0,034 | 0,022 / 0,022 |
| derivee-variations | – | 0,265 | 0,261 | 0,081 / 0,079 |
| limites-asymptotes | – | 5,895 | 5,888 | 1,177 / 1,2 |
| etude-complete | – | 1,998 | 1,978 | 0,29 / 0,275 |
| factorisation | – | 1,883 | 1,862 | 0,063 / 0,062 |
| exponentielles-logarithmes | C | 0,888 | 0,923 (+3,9 %) | 0,005 / 0,005 |
| exponentielles-logarithmes | M | 0,764 | 0,782 (+2,4 %) | 0,003 / 0,003 |

  Aucune hausse de plus de 50 %. Mur du dump : 13 s (1 processus), 4 s (6 processus).
- Suite d'avant commit : `PROCESSUS_PAGES=4 python3 tests/lancer.py complet --rapport <scratchpad>/briques/rapports/B2`, code 0,
  17 h 29 → 17 h 36 (6 min 44). Python 1 443 collectés, 1 442 passés + 1 xfail, 106 301 sous-tests (101,5 s) ; pages 138 passés,
  2 407 sous-tests, 300,7 s (identiques nom par nom). `comparer_listes` contre `tests/reference` (B0) : 51 tests nouveaux
  (`test_expr.py` 21, `test_chaine.py` 30), aucun disparu ; sous-tests : `test_imports` (liste bien formée) 83 → 93, `test_manifeste_minimal`
  34 → 36, gardes `memo` et `memo_racines` 19 → 21, `test_vocabulaire` (littéraux des moteurs) 8 652 → 8 728 ; une baisse justifiée
  dans `suivi.md` : `test_exp_log` (littéraux d'exp_log.py) 1 215 → 960 (B1 puis B2 : les 66 littéraux des chaînes passent à
  moteur/chaine.py, 100 littéraux, lus par `test_vocabulaire` avec le même détecteur).

## B3 — type de bloc « chaine » (A4)

### Plan

1. Lecture : `moteur/sortie.py` (`BLOCS`, `valider`), `moteur/chaine.py` (`rangees_chaine`, `LigneTexte`), `commun/rendu.js` (`BLOCS`,
   `rendreBloc`), `commun/composants.css`, `resoudre_el._ligne` (grille `.etape > .chaine > .ligne > .lien/.expr/.prop`) et le CSS
   `.chaine` de la page EL ; corrigés Id_rem.pdf (2.9 a, b, c) et tatonement.pdf (2.11) : quatre colonnes (membre gauche, ⇔, membre
   droit, étiquette grise), une ligne de texte pleine largeur entre deux rangées (2.9 c), ⇔ alignés avant et après.
2. Schéma (`sortie.py`) : `{"type": "chaine", "rangees": [rangée]}` ; rangée = ligne `{lien, expr, prop?, gauche?}` (lien « », `\iff`
   ou `\Rightarrow` ; expr, gauche : TeX ; prop : texte avec le TeX entre `\(` `\)`), ou ligne pleine largeur `{texte}` (même forme
   de texte) ou `{bloc}` (bloc imbriqué parmi `texte`, `formule`, `tableau`, validé récursivement ; jamais une chaîne dans une chaîne).
   `gauche` seulement sur la première ligne, avec un lien. Aucun HTML dans un champ (balise ou entité : écart). Constructeurs
   `chaine`, `rangee`, `rangee_texte`, `rangee_bloc`.
3. Depuis une `chaine.Chaine` : `chaine.bloc_chaine(c, etiquette_grise=False, impossible=False, membre_gauche=False)` (les rangées de
   `rangees_chaine`, une `LigneTexte` devient une ligne pleine largeur : texte, `Message` ou bloc ; `membre_gauche` : le premier
   élément passe dans la colonne de gauche de la première ligne à ⇔, comme le corrigé). Arête nouvelle `chaine -> sortie` (brique ->
   brique ; sortie n'importe rien) ; manifeste inchangé (EL charge déjà sortie.py).
4. Rendu (`commun/rendu.js`) : `<div class="etape"><div class="chaine">` puis `.ligne` (`.gauche`?, `.lien`, `.expr`, `.prop`) et
   `.pleine`, mêmes classes que la grille d'EL (un seul CSS en B4) ; textes échappés par le rendu (aucun HTML venu du moteur), TeX par
   KaTeX. `commun/composants.css` : ce que le bloc ajoute (`.chaine>.pleine` sur toute la largeur, `.chaine.avec-gauche` à quatre
   colonnes et son repli sur un conteneur étroit) ; rien qui touche une chaîne d'EL. Le CSS `.chaine` reste dans la page EL (B4).
5. Tests : Python (`test_sortie.py` : constructeurs, `valider` accepte et refuse ; `test_chaine.py` : `bloc_chaine` sur 2.9 a et 2.9 c,
   options, `test_imports` de la brique) ; pages (nouveau `tests/pages/test_bloc_chaine.py`, sur une page existante comme SOC-22 :
   structure, KaTeX, textes échappés, tableau imbriqué, thème sombre, balayage 320–1100 px ; alignement, repli étroit et étiquette
   grise en `xfail` strict « B4 » s'ils ne peuvent passer qu'avec le CSS `.chaine` commun).
6. Docs : `architecture.md` (A4, § 1, § 5 : ligne « HTML de la grille `.chaine` »), docstrings ; puis dump, temps, suite complète.

### Exécution

- **Schéma** (`moteur/sortie.py`, `BLOCS["chaine"] = ({"rangees"}, set())`) :

      {"type": "chaine", "rangees": [rangée, …]}
      rangée = {"lien": "" | "\\iff" | "\\Rightarrow", "expr": TeX, "prop"?: texte, "gauche"?: TeX}     ligne de la grille
             | {"texte": texte}                                                                      ligne pleine largeur (texte)
             | {"bloc": bloc}                                                                        ligne pleine largeur (bloc)

  texte = du texte, le TeX entre `\(` `\)` (comme la colonne des propriétés d'Exp-log) ; bloc imbriqué : `texte`, `formule` ou
  `tableau` (`BLOCS_DANS_CHAINE`), validé récursivement par `_valider_bloc` ; une chaîne dans une chaîne, un `resultat`, une `liste`,
  un type inconnu sont refusés. `gauche` : seulement sur la première ligne de la grille, qui a un lien (des lignes pleine largeur
  peuvent la précéder). Au moins une ligne. **Aucun HTML** dans `expr`, `prop`, `gauche`, `texte` : `valider` refuse une balise
  (`</?nom …>`) ou une entité (`&amp;`, `&#60;`) ; « x < y » et `\(a<b\)` passent. Le bloc `texte` imbriqué garde son `html` (type
  existant). Constructeurs : `chaine(rangees)`, `rangee(lien, expr, prop=None, gauche=None)`, `rangee_texte(texte)`, `rangee_bloc(bloc)`.
- **Depuis une `Chaine`** (`moteur/chaine.py`) : `bloc_chaine(c, etiquette_grise=False, impossible=False, membre_gauche=False)` prend
  les rangées de `rangees_chaine` (mêmes options) ; une `LigneTexte` devient `rangee_texte` (texte, ou `Message` par
  `texte_message` : texte tel quel, arbres en TeX entre `\(` `\)`) ou `rangee_bloc` (un dict de sortie.py). `membre_gauche=True` :
  le premier élément passe dans la colonne de gauche de la première ligne à ⇔/⇒ (« 6x² − 6 = 0 ⇔ 6(x² − 1) = 0  ME », Id_rem.pdf),
  les lignes pleine largeur d'avant restent au-dessus (2.9 b) ; sans effet si la première rangée a une propriété ou si la ligne
  suivante n'a pas de lien (suite de « = »). Les trois options de B2 passent donc dans le bloc : étiquette grise (le texte sans
  parenthèses ; le gris est celui de la colonne `.prop`, CSS de B4), « impossible » (TeX de l'expression), texte au milieu (`.pleine`).
- **Arête** `chaine -> sortie` (ARETES, brique → brique ; sortie.py n'importe que `re`) ; `test_chaine.TestSansEtat.test_imports`
  attend maintenant `{collections, html, types, expr, sortie}` (changement voulu, l'égalité reste exacte). Manifeste inchangé : l'outil
  EL, seul à charger chaine.py, charge déjà sortie.py (`test_manifeste` vert, complet et minimal).
- **Rendu** (`commun/rendu.js`, `BLOCS.chaine` → `rendreChaine`) : `<div class="etape"><div class="chaine[ avec-gauche]">`, une
  `<div class="ligne">` par ligne avec `<span class="gauche">` (seulement avec un membre de gauche), `.lien`, `.expr`, `.prop`, et une
  `<div class="pleine">` par ligne pleine largeur (texte échappé, ou le bloc rendu par `rendreBloc`). Mêmes classes et même structure
  que la grille écrite par `resoudre_el._ligne` (le CSS d'EL s'applique tel quel). Formules par `K()` (KaTeX) ; textes échappés
  (`&`, `<`, `>`) puis leur TeX rendu par `math()`.
- **CSS** (`commun/composants.css`, ajouts seulement) : `.chaine>.pleine{grid-column:1 / -1;min-width:0}` ; `.chaine.avec-gauche` à
  quatre colonnes (`auto auto minmax(0,1fr) minmax(0,max-content)`), `.gauche` alignée à droite ; sur un conteneur étroit
  (`@container (max-width: 47rem)`, le même seuil que la page EL) deux colonnes, `.gauche` seule sur sa ligne au-dessus, vide cachée.
  Aucune règle ne touche une chaîne d'EL (ni `.pleine` ni `.avec-gauche` n'y existent) ; le CSS `.chaine` reste dans la page EL (B4).
- **Docs** : `architecture.md` § 1 (chaine : « et leur bloc »), A4 (garde-fou : HTML refusé par `valider`, texte échappé par le rendu),
  § 5 (ligne « HTML de la grille `.chaine` » : le bloc existe, CSS en B4, migration d'Exp-log : chantier à décider) ; docstrings de
  sortie.py, chaine.py, rendu.js.

### Tests ajoutés

- `tests/python/test_sortie.py::TestBlocChaine` (7 tests) : constructeurs ; forme correcte acceptée (membre de gauche, texte et tableau
  pleine largeur, bloc texte imbriqué, ⇒, ligne `\phantom` sans lien ; chaque type de `BLOCS_DANS_CHAINE` ; dans un sous-calcul) ;
  refus : HTML (balises dans expr, prop, gauche, texte ; entités), bloc imbriqué non permis (inconnu, chaîne, resultat, liste, texte
  nu, None) et bloc imbriqué invalide (validé récursivement), rangée mal formée (dict vide, texte, liste, texte + bloc, clés en trop ou
  manquantes, lien inconnu dont « ⇔ » et « = », champs vides), `gauche` hors de la première ligne ou sans lien, liste vide ou sans ligne.
- `tests/python/test_chaine.py::TestBlocChaine` (6 tests) : rangées par défaut égales à `rangees_chaine` (2.9 c), 2.9 a avec membre de
  gauche, étiquettes grises et « impossible » (sortie attendue écrite), lignes pleine largeur avant le membre de gauche (2.9 b, tableau
  passé tel quel), `membre_gauche` sans effet (propriété en tête, suite de « = »), `texte_message`, Exp-log inchangé (aucun bloc
  `chaine` dans ses sorties).
- `tests/pages/test_bloc_chaine.py::TestBlocChaine` (7 tests), sur la page Ensemble de définition comme SOC-22 (aucune page nouvelle),
  trois chaînes construites par `bloc_chaine` (2.9 c avec membre de gauche et étiquettes grises, 2.9 c comme Exp-log, chaîne avec un
  texte, un tableau et un bloc texte pleine largeur) et une chaîne de texte qui ressemble à du HTML. Dès B3 : `test_blocs_valides`,
  `test_structure_et_formules` (classes, ordre des rangées, colonnes, KaTeX partout, « impossible »), `test_textes_echappes` (aucune
  balise créée, aucun script lancé), `test_largeurs_et_theme_sombre` (320 à 1100 px, clair et sombre : `test_largeurs.JS_MESURE` sans
  faute, rien hors de la carte, couleurs du thème ; console vide). **xfail stricts « B4 »** (sans sous-test, pour échouer en entier) :
  `test_colonnes_alignees_avant_et_apres_la_ligne_pleine` (1100 px), `test_repli_sur_ecran_etroit` (360 et 390 px : propriété sous
  l'expression, membre de gauche au-dessus, pas de défilement), `test_etiquette_grise` (couleur `--muted`, plus petite, clair et
  sombre). Contrôle fait : avec le CSS `.chaine` de la page EL injecté dans la page (simulation de B4, script dans le scratchpad
  `b3/simuler_b4.py`), les trois passent, et les tests de B3 aussi.
- `test_imports` : une arête de plus. `test_largeurs` inchangé (aucun outil nouveau, `CONNUS` vide) ; `test_style_commun` inchangé
  (aucune page touchée) ; `test_composants` lit les règles ajoutées (sous-tests en plus).

### Vérifications

- Dump `B3` (`--processus 6`) et `B3-1` (`--processus 1`) : `diff -r --exclude=temps` avec `depart` code 0, aucune sortie
  (17 fichiers, 4 148 sorties).
- Tests ciblés (`-n 6`) : test_sortie, test_chaine, test_imports, test_manifeste, test_composants, test_noyau, test_vocabulaire,
  test_style_commun, test_source_unique : 122 passés, 12 150 sous-tests ; `tests/pages/test_bloc_chaine.py` : 4 passés, 3 xfail.
- Temps natif (`resoudre_json`, 1 processus, comparé à `un-processus` de B0) :

| Outil | Filière | B0 (s) | B3 (s) | Plus long appel B0 / B3 (s) |
|---|---|---|---|---|
| ensemble-definition | – | 0,033 | 0,035 | 0,022 / 0,024 |
| derivee-variations | – | 0,265 | 0,270 | 0,081 / 0,082 |
| limites-asymptotes | – | 5,895 | 5,953 (+1 %) | 1,177 / 1,212 |
| etude-complete | – | 1,998 | 2,050 (+2,6 %) | 0,29 / 0,288 |
| factorisation | – | 1,883 | 1,904 | 0,063 / 0,066 |
| exponentielles-logarithmes | C | 0,888 | 0,928 (+4,5 %) | 0,005 / 0,005 |
| exponentielles-logarithmes | M | 0,764 | 0,780 (+2,1 %) | 0,003 / 0,003 |

  Aucune hausse de plus de 50 % (aucun moteur ne produit le bloc). Mur du dump : 13 s (1 processus), 4 s (6 processus).
- Captures (scratchpad, hors du dépôt) : `b3/sans-b4-390.png`, `b3/sans-b4-1100.png` (B3 seul : la grille n'a pas encore son CSS
  dans cette page), `b3/avec-b4-320.png`, `b3/avec-b4-390.png`, `b3/avec-b4-390-sombre.png`, `b3/avec-b4-1100.png` (CSS d'EL injecté).
- Suite d'avant commit : `PROCESSUS_PAGES=4 python3 tests/lancer.py complet --rapport <scratchpad>/briques/rapports/B3`, code 0,
  départ 17 h 58 (environ 6 min 45 de mur). Python 1 456 collectés, 1 455 passés + 1 xfail, 106 391 sous-tests (89,2 s) ; pages
  145 collectés, 142 passés + 3 xfail (les trois « B4 »), 2 421 sous-tests (311 s). `comparer_listes` contre `tests/reference` (B0) :
  64 tests Python nouveaux (B1 21, B2 30, B3 13) et 7 tests de pages nouveaux (`test_bloc_chaine.py`), aucun disparu ; sous-tests :
  hausses seulement (`test_composants` 7 → 8 et 35 → 41, `test_imports` 83 → 95, `test_manifeste_minimal` 34 → 36, gardes `memo`
  19 → 21, `test_vocabulaire` 8 652 → 8 792 : les littéraux de sortie.py et chaine.py ajoutés), plus la baisse déjà justifiée de
  `test_exp_log` (1 215 → 960, inchangée depuis B2) ; pages : 2 407 → 2 421 (les 14 sous-tests de `test_bloc_chaine.py`), références
  des autres pages identiques.

## B4 — CSS commun : `.chaine` dans `commun/composants.css`, `details ol` dans `commun/style.css`

### Plan

1. Lecture : `<style>` des pages (EL : `details ol,details ul` et la grille `.chaine` ; Factorisation et Limites : `details ol`
   identique ; Limites : `details li`), `commun/style.css` (`details ul` y est déjà, mêmes valeurs), `commun/composants.css` (les
   compléments de B3), qui charge quoi (les six pages outils : style.css puis composants.css puis leur `<style>` ; simplexe :
   composants.css seule ; accueil : aucune), tests de style (`test_style_commun`, `test_composants`, `test_tableaux_css`).
2. Mesure **avant** (sur 9cee0c4, arbre sans autre modification que ce journal) : script du scratchpad `b4/styles.py` (Chrome des tests
   de pages) ; pour chaque page qui charge style.css ou composants.css (six outils, EL filière M, simplexe), quelques entrées (corpus
   réduit de `rendu.py`, plus des entrées d'EL à chaînes), corrigé complet affiché (`#tout`), tous les `<details>` ouverts, puis à 320,
   360, 390, 768 et 1100 px, en clair et en sombre : **tous** les styles calculés (`getComputedStyle`, toutes les propriétés) de
   **tous** les éléments de la page ; en entier pour les éléments `.chaine` (et leurs descendants, et le `.etape` qui la contient) et
   les `details ol`/`ul`/`li`, par empreinte pour les autres. Sortie JSON dans `b4/avant/`.
3. Déplacement : `details ol` rejoint `details ul` dans style.css (`details ol,details ul{…}`, mêmes valeurs) ; les règles
   `details ol` des pages EL, Factorisation, Limites sont retirées (doublons) ; la grille `.chaine` d'EL (règles de base, `.etape:has`,
   repli `@container`) passe dans la section B3 de composants.css, fondue avec `.pleine` et `.avec-gauche` (une seule section, un seul
   `@container`) ; la page EL ne garde aucune règle `.chaine` ni `details ol`.
4. Mesure **après**, même script (`b4/apres/`), comparaison : identique exigé (sinon, la règle ne bouge pas et la question va sous
   « Questions pour l'enseignant »).
5. Tests : les trois xfail stricts « B4 » de `tests/pages/test_bloc_chaine.py` perdent leur marque (docstring du module ajustée) ;
   `test_style_commun` : `details ol` sort de la liste des règles propres à une page, et un test nouveau vérifie qu'aucune page ne garde
   de règle `.chaine` ni `details ol` (CSS commun seulement) ; `test_composants` : `.chaine` dans les composants demandés.
6. Docs : `architecture.md` § 5 (ligne « HTML de la grille `.chaine` » : le CSS est commun, reste la migration d'Exp-log), commentaires
   de composants.css ; dump, temps, suite complète, commit, `verifier`.

### Exécution

- **`commun/style.css`** : `details ul{…}` devient `details ol,details ul{margin:.4em 0 0;padding-left:1.2em}` (mêmes valeurs que les
  trois pages). Aucune règle de style.css ni de composants.css ne visait `ol` : rien d'autre ne change de place dans la cascade.
- **Pages** : EL perd `details ol,details ul` et toute la grille `.chaine` (11 lignes ; il garde `.final .res` et `.final .c`) ;
  Factorisation et Limites perdent leur `details ol` (doublon ; Limites garde `details li` et `.rappel`). Aucune autre page n'avait de
  `details ol` ni de règle `.chaine` (Ensemble de définition et Dérivée : un `<ul>` dans leur `<details>`, déjà réglé par style.css ;
  Étude complète : aucun `<details>` ; simplexe : ne charge pas style.css, aucun `.chaine`).
- **`commun/composants.css`** : une seule section « Chaîne de ⇔ du corrigé » : les quatre règles de base de la grille (`.chaine`,
  `.ligne`, `.lien`, `.prop`), puis `.pleine` et `.avec-gauche` (B3), le conteneur `.etape:has(>.chaine)`, et **un seul**
  `@container (max-width: 47rem)` avec le repli de base (3 règles d'EL) puis celui de `.avec-gauche` (3 règles de B3). Aucune règle en
  double ; la seule redite voulue, `.chaine.avec-gauche{grid-template-columns:…}` dans le `@container`, est commentée (le sélecteur
  plus précis l'emporterait sinon sur `.chaine` du repli). Commentaire de tête réécrit (une seule description de la grille).
- **Docs** : `architecture.md` § 5 (le CSS est commun, reste la migration d'Exp-log vers le bloc, à décider) ;
  `docs/specifications/exponentielles-logarithmes.md` (« grille CSS `.chaine` » : dans composants.css depuis B4).
- `moteur/`, `nombres.py`, `oracle.py` : non touchés.

### Rendu identique : méthode et résultat

- Script `<scratchpad>/b4/styles.py` (Chrome et serveur des tests de pages, `tests/pages/navigateur.py`), comparaison
  `<scratchpad>/b4/comparer.py avant apres`, lancement `<scratchpad>/b4/mesurer.sh <dossier>` (quatre pages à la fois, chacune limitée à
  5 minutes). Pages : les six outils (qui chargent style.css et composants.css), EL en filière M (`?filiere=M`), simplexe (composants.css
  seule). États : page prête, puis chaque entrée du corpus réduit de `rendu.py` (3 par outil ; EL C : + `7^(2x+1)=7^9`, `3^x=27`,
  `ln(x)+ln(x-1)=ln(6)`, `e^(2x)-3e^x+2=0` ; EL M : + `log(x)=3`, `log(x)=-1`), corrigé complet (`#tout`), **tous les `<details>`
  ouverts** (rappels d'EL C et M, de Factorisation, de Limites…). Pour chaque état, à 320, 360, 390, 768 et 1100 px, en clair et en
  sombre : `getComputedStyle` de **tous** les éléments de la page, **toutes** les propriétés (triées par nom), une empreinte FNV-1a par
  élément ; les éléments de la grille (chaque `.chaine`, ses descendants, son `.etape`) et les `ol`/`ul`/`li` d'un `<details>` sont
  aussi relevés à part, par leur chemin dans le DOM.
- **Avant** : sur 9cee0c4 (les cinq fichiers de page et de CSS remis à HEAD, le reste de l'arbre : ce journal et les tests seulement) ;
  **après** : avec B4.
- Écueil levé en route : un premier essai, propriétés dans l'ordre de `getComputedStyle`, donnait des écarts partout, même entre deux
  lancements sur le même arbre (l'ordre d'énumération change d'un Chrome à l'autre) ; avec les propriétés triées, deux lancements sur le
  même arbre sont identiques (Dérivée et simplexe, 41 920 éléments), et la comparaison avant / après est faite ainsi.
- **Résultat : identique**, 0 écart. 350 mesures (état × largeur × thème), 826 300 éléments mesurés, **413 137 700 valeurs** comparées, dont
  56 680 relevés d'éléments de la grille `.chaine` ou de listes d'un `<details>` (EL C : 34 280 ; EL M : 20 960 ; Limites 640 ;
  Factorisation 400 ; Dérivée 240 ; Ensemble 160).

  | Page | Mesures | Éléments | Valeurs | Relevés .chaine / details | Résultat |
  |---|---|---|---|---|---|
  | exponentielles-logarithmes (C) | 80 | 283 290 | 141 645 000 | 34 280 | identique |
  | exponentielles-logarithmes (M) | 60 | 210 640 | 105 320 000 | 20 960 | identique |
  | limites-asymptotes | 40 | 99 580 | 49 790 000 | 640 | identique |
  | etude-complete | 40 | 97 700 | 48 850 000 | 0 | identique |
  | factorisation | 40 | 67 540 | 33 770 000 | 400 | identique |
  | derivee-variations | 40 | 39 870 | 19 935 000 | 240 | identique |
  | ensemble-definition | 40 | 25 630 | 12 815 000 | 160 | identique |
  | simplexe | 10 | 2 050 | 1 012 700 | 0 | identique |

- Références de pages : `tests/pages/test_rendu.py` (corpus complet) dans la suite complète ; aucun fichier de `tests/pages/references/`
  ni d'instantané modifié (`git status`).

### Tests

- `tests/pages/test_bloc_chaine.py` : les trois xfail stricts « B4 » (`test_colonnes_alignees_avant_et_apres_la_ligne_pleine`,
  `test_repli_sur_ecran_etroit`, `test_etiquette_grise`) perdent leur marque et passent (la page Ensemble de définition a maintenant la
  grille par composants.css, sans CSS injecté) ; `xfail_b4` et l'import de pytest retirés, docstrings ajustées. Aucune simulation de
  B4 dans les tests (celle de B3 était un script du scratchpad, `b3/simuler_b4.py`). Seul : 7 passés, 14 sous-tests, 12 s.
- `tests/python/test_style_commun.py` : `details ol` sort de la liste des règles propres à une page (une page qui la redéfinirait
  échouerait) ; **test nouveau** `test_grille_chaine_et_listes_des_rappels_dans_les_feuilles_communes` : la grille est dans
  composants.css, `details ol` dans style.css, et aucun `<style>` de page (six outils et simplexe, 7 sous-tests) n'a de sélecteur
  `.chaine` ni `details … ol` (contrôlé : sur 9cee0c4 il aurait relevé les 9 sélecteurs d'EL et le `details ol` de Factorisation et de
  Limites).
- `tests/python/test_composants.py` : `.chaine` dans les composants demandés (un sous-test de plus).
- Ciblés (`-n 6`) : test_style_commun, test_composants, test_tableaux_css, test_imports, test_manifeste, test_vocabulaire,
  test_source_unique, test_rappel_methode : 51 passés, 12 606 sous-tests.

### Vérifications

- Dump `B4` (`--processus 6`) et `B4-1` (`--processus 1`) : `diff -r --exclude=temps` avec `depart` code 0, aucune sortie
  (17 fichiers, 4 148 sorties).
- Temps natif (`resoudre_json`, 1 processus, comparé à `un-processus` de B0 ; B4 ne touche aucun moteur, écarts de bruit) :

| Outil | Filière | B0 (s) | B4 (s) | Plus long appel B0 / B4 (s) |
|---|---|---|---|---|
| ensemble-definition | – | 0,033 | 0,035 | 0,022 / 0,023 |
| derivee-variations | – | 0,265 | 0,277 (+4,5 %) | 0,081 / 0,085 |
| limites-asymptotes | – | 5,895 | 6,244 (+5,9 %) | 1,177 / 1,259 |
| etude-complete | – | 1,998 | 2,074 (+3,8 %) | 0,29 / 0,301 |
| factorisation | – | 1,883 | 1,938 (+2,9 %) | 0,063 / 0,064 |
| exponentielles-logarithmes | C | 0,888 | 0,933 (+5,1 %) | 0,005 / 0,005 |
| exponentielles-logarithmes | M | 0,764 | 0,843 (+10,3 %) | 0,003 / 0,003 |

  Aucune hausse de plus de 50 %. Mur du dump : 13,5 s (1 processus), 5 s (6 processus).
- Suite d'avant commit : `PROCESSUS_PAGES=4 python3 tests/lancer.py complet --rapport <scratchpad>/briques/rapports/B4`, code 0,
  18 h 47 → 18 h 54 (6 min 54 de mur). Python 1 457 collectés, 1 456 passés + 1 xfail, 106 407 sous-tests (99,2 s) ; pages 145
  collectés, **145 passés** (les trois anciens xfail « B4 » compris), 2 421 sous-tests (312,7 s). `comparer_listes` contre
  `tests/reference` (B0) : 65 tests Python nouveaux (B1 21, B2 30, B3 13, B4 1) et 7 tests de pages nouveaux (`test_bloc_chaine.py`),
  aucun disparu ; sous-tests : hausses seulement (`test_composants` : `test_composants_demandes_sont_presents` 10 → 11,
  `test_ne_redefinit_aucune_regle_de_style_css` 35 → 49, `test_aucune_largeur_d_ecran_en_pixels` 7 → 8 ; et celles de B1–B3), plus la
  baisse déjà justifiée de `test_exp_log` (1 215 → 960) ; pages : 2 421 sous-tests comme en B3, références des pages identiques.

## B5 — `nombres.approx` et `nombres.exact` (E14, R13, D25)

### Plan

1. Lecture : `decisions.md` du 2e degré (D13, D25, E14, § 5 `approx`, § 6 cas limites, § 11 ticket (e)), R13 du guide, A5, A7 et § 5
   d'`architecture.md` ; `moteur/nombres.py` et `test_nombres.py` ; `exp_log.tex_approx` (et son test
   `test_approximation_en_notation_scientifique`), `exp_log._nb_exact`, `_DECIMAUX` et `_avec_decimaux` ; les autres formats de « ≈ »
   (rapport de revue-structure § 2.2 : `ensemble_def.dec`, `parties.arrondi`/`decimal_tex`/`approchee`, `redaction_bh.fmt_approx` et
   `fmt_val`) et l'écriture des entiers (`qtex` de l'ED et ses copies).
2. `moteur/nombres.py` : deux fonctions **ajoutées**, aucune fonction existante modifiée, aucune variable de module nouvelle sinon des
   constantes, bibliothèque standard seulement (aucune arête d'import) :
   - `approx(x, decimales=3)` : TeX de la valeur approchée, calculé sur `float(x)` avec la même arithmétique que `tex_approx` (égalité à
     l'octet hors écarts voulus) ; entre 10⁻³ et 10⁶ : 3 décimales, virgule, apostrophe dès 4 chiffres (D25, par `formater_decimal`) ;
     sous 10⁻³ et dès 10⁶ : mantisse à 3 décimales (4 chiffres significatifs) `× 10ⁿ`, mantisse 10,000 → 1,000 × 10ⁿ⁺¹ (E14) ;
     valeur non finie : `ValueError` (rien de faux) ;
   - `exact(x, decimaux_enonce=False)` : TeX d'une valeur exacte (int, Fraction, Decimal ; un float est refusé) : entier, fraction
     (signe devant), ou décimal fini si `decimaux_enonce` (R13) ; même règle que `_nb_exact` (au plus 8 décimales).
3. Tests (`tests/python/test_nombres.py`) : l'échantillon de la consigne (0, ±1, ±0,5, 1/3, 2/3, π, √2, 0,001, 0,000999…, 0,0009995,
   999 999,4, 999 999,6, 10⁶, 9,9995 × 10⁶, 1234,5678, 4913, 10⁻⁵, −3,162 × 10⁻⁵, 10¹⁰, racine positive de x² + 1000x − 1 = 0, plus
   les cas qui séparent les deux fonctions) : `approx` attendu, et `tex_approx` égal ou **écart nommé** ; `exact` contre
   `tex(_nb_exact(v))` sous `_DECIMAUX` False et True (remis après), entiers, fractions négatives, décimaux finis, fraction non décimale
   avec `decimaux_enonce=True`, entiers à 4 chiffres et plus ; pureté (aucun état de module changé, A7) ; erreurs.
4. D25 : vérifier dans `nombres.py` et dans les sorties (dump de départ, instantanés, références de pages) ; liste des outils et
   instantanés qui changeraient si D25 était appliqué partout, sans rien changer.
5. Docs : `architecture.md` (A5, § 5 « 5 formats de ≈ »), docstrings de `nombres.py` ; `suivi.md` (état, écarts, D25, questions).
6. Vérifications : dump `B5` et `B5-1` identiques au départ, temps, `test_imports`, `test_manifeste`, `test_largeurs` ; suite complète
   (`complet --rapport <scratchpad>/briques/rapports/B5`), commit, `verifier`.

### Exécution

- **Signatures** (`moteur/nombres.py`, ajoutées en fin de fichier ; `grouper`, `formater_entier`, `formater_decimal`,
  `nettoyer_saisie`, les motifs et constantes existants **inchangés**) :

      approx(x, decimales=3) -> str      # TeX, à écrire après \approx
      exact(x, decimaux_enonce=False) -> str   # TeX d'une valeur exacte calculée

  Deux constantes (`PLAFOND_DECIMAL = 10 ** 6`, `DECIMALES_EXACTES_MAX = 8`) et quatre aides privées (`_valeur_exacte_de`, `_arrondi`,
  `_ecrire`, `_decimales_finies`) ; aucune variable de module modifiée (A7, testé) ; imports : `math`, `decimal.Decimal`,
  `fractions.Fraction` (bibliothèque standard ; aucune arête nouvelle, `test_imports` inchangé). Aucun outil ne les appelle.
- **`approx`** : la valeur est prise **exactement** (int, Fraction, Decimal ; un float par sa valeur binaire ; SymPy et mpmath par
  `float()`), l'arrondi est calculé en fractions (pas d'erreur de la division `v / 10 ** e` en flottant). Entre 10⁻³ et 10⁶ :
  3 décimales, `formater_decimal` (virgule `{,}`, apostrophe `\text{’}` dès 4 chiffres : D25). Sous 10⁻³, ou dès 10⁶ **après
  arrondi** : mantisse à 3 décimales (4 chiffres significatifs), zéros gardés, `\times 10^{n}` ; une mantisse arrondie à 10,000 devient
  1,000 × 10ⁿ⁺¹ (E14). Mi-chemin : au-dessus (arrondi usuel, comme `parties.arrondi`, ROUND_HALF_UP, et `exp_log._trois_decimales`).
  Signe « - » comme `tex_approx` et l'arbre (`nb_tex`). Valeur non finie : `ValueError` (rien de faux). `decimales` (entier ≥ 1)
  règle aussi le seuil bas (10^(−decimales)) et la mantisse ; le seuil haut reste 10⁶.
  Premier essai écarté : la même arithmétique flottante que `tex_approx` (`f"{v / 10 ** e:.3f}"`) donnait 9,999 × 10⁶ pour
  9 999 500 (9,9995 n'est pas représentable : la division tombe en dessous) et 0,062 pour 0,0625 (arrondi au pair de Python), alors
  que la consigne attend la mantisse 10,000 pour 9,9995 × 10⁶.
- **`exact`** : int, Fraction, Decimal fini (ou chaîne que `Fraction` lit) ; un float est refusé (`TypeError`). Entier :
  `formater_entier` ; fraction : `\frac{…}{…}`, signe devant ; `decimaux_enonce=True` : décimal fini d'au plus 8 décimales en décimal
  (`formater_decimal`), sinon fraction : exactement la règle de `_nb_exact`, sans son état. Les décimaux de l'énoncé gardent leur
  écriture par l'arbre (`Nb.dec`), pas par cette fonction (docstring).
- **D13 sur le corpus d'Exp-log** (script du scratchpad `b5/d13.py`, lecture seule : `tex_approx` enveloppé dans le processus) :
  `resoudre_json` C et M et `apercu_json` sur les entrées du dump de départ, 2 742 appels, **1 341 valeurs** passées à `tex_approx`
  (362 distinctes, de 1,1 × 10⁻¹⁶ à 5,8 × 10⁴) : `approx(v) == tex_approx(v)` **pour toutes** (0 écart). Rebrancher Exp-log sur
  `approx` (R9) laisserait donc son dump identique sur ce corpus. La valeur 1,1 × 10⁻¹⁶ (un reste de calcul flottant) n'est affichée
  nulle part (aucune notation scientifique dans le dump).
- **Docs** : `architecture.md` A5 (les deux fonctions, `test_nombres`) et § 5 (ligne « 5 formats de ≈ » : la fonction unique existe,
  outils pas encore rebranchés, R9 ; `exp_log._trois_decimales` ajouté à la liste, sixième écriture d'un « ≈ », celle de
  l'interprétation R16) ; docstring du module `nombres.py`.

### Échantillon : `approx` et `tex_approx` (à relire par l'enseignant)

Tableau tiré de `ECHANTILLON` (`tests/python/test_nombres.py`) ; « égal » : `tex_approx` donne exactement la même chaîne.

| Valeur | `approx` | `tex_approx` |
|---|---|---|
| 0 | `0{,}000` | égal |
| −0,0 | `0{,}000` | `-0{,}000` : **zéro négatif** |
| 1 ; −1 | `1{,}000` ; `-1{,}000` | égal |
| 0,5 ; −0,5 | `0{,}500` ; `-0{,}500` | égal |
| 1/3 ; 2/3 ; −2/3 | `0{,}333` ; `0{,}667` ; `-0{,}667` | égal |
| π ; √2 | `3{,}142` ; `1{,}414` | égal |
| −√5 ; −2 − √5 ; −2 + √5 (exemples d'E14) | `-2{,}236` ; `-4{,}236` ; `0{,}236` | égal |
| 6,644 ; −0,693 | `6{,}644` ; `-0{,}693` | égal |
| 0,001 ; 0,0010004 | `0{,}001` | égal |
| 0,000999 | `9{,}990 \times 10^{-4}` | égal |
| 0,0009999 | `9{,}999 \times 10^{-4}` | égal |
| 0,0009995 (4 chiffres significatifs : reste sous 10⁻³) | `9{,}995 \times 10^{-4}` | égal |
| 0,00099995 ; 0,00099999 (mantisse 10,000) | `1{,}000 \times 10^{-3}` | `1 \times 10^{-3}` : **zéros de la mantisse** |
| x² + 1000x − 1 = 0, racine positive (9,99999 × 10⁻⁴ ; mantisse 10,000) | `1{,}000 \times 10^{-3}` | `1 \times 10^{-3}` : **zéros de la mantisse** |
| x² + 1000x − 1 = 0, racine négative | `-1\text{’}000{,}001` | égal |
| 1234,5678 | `1\text{’}234{,}568` | égal |
| 4913 | `4\text{’}913{,}000` | égal |
| 123 456,789 | `123\text{’}456{,}789` | égal |
| 999 999,4 ; 999 999,6 ; 999 999,9994 | `999\text{’}999{,}400` ; `…{,}600` ; `…{,}999` | égal |
| ±999 999,9996 (arrondi à 10⁶) | `1{,}000 \times 10^{6}` (signe « - » devant pour la valeur négative) | `1\text{’}000\text{’}000{,}000` : **arrondi à 10⁶** |
| 10⁶ ; −10⁶ | `1{,}000 \times 10^{6}` ; `-1{,}000 \times 10^{6}` | `1 \times 10^{6}` : **zéros de la mantisse** |
| 4,5 × 10⁶ | `4{,}500 \times 10^{6}` | égal |
| 9,99949 × 10⁶ | `9{,}999 \times 10^{6}` | égal |
| 9,9995 × 10⁶ (mantisse 10,000) | `1{,}000 \times 10^{7}` | `9{,}999 \times 10^{6}` : **mi-chemin** |
| 2 × 10⁷ | `2{,}000 \times 10^{7}` | `2 \times 10^{7}` : **zéros de la mantisse** |
| −2,5 × 10⁷ | `-2{,}500 \times 10^{7}` | égal |
| 10¹⁰ | `1{,}000 \times 10^{10}` | `1 \times 10^{10}` : **zéros de la mantisse** |
| 10⁻⁴ ; 10⁻⁵ | `1{,}000 \times 10^{-4}` ; `1{,}000 \times 10^{-5}` | `1 \times 10^{-4}` ; `1 \times 10^{-5}` : **zéros de la mantisse** |
| 3,1623 × 10⁻⁵ ; −3,162 × 10⁻⁵ | `3{,}162 \times 10^{-5}` ; `-3{,}162 \times 10^{-5}` | égal |
| 0,0625 ; 2,0625 (mi-chemin) | `0{,}063` ; `2{,}063` | `0{,}062` ; `2{,}062` : **mi-chemin** |
| 0,1875 (mi-chemin, même arrondi) | `0{,}188` | égal |

Les quatre écarts voulus (constantes `ECART_*` du test, chacun illustré) :
1. **Zéros de la mantisse** : 4 chiffres significatifs gardés, `1{,}000 \times 10^{n}` (E14 : « 1,000 × 10ⁿ⁺¹ ») ; `tex_approx` retire
   « ,000 » (`1 \times 10^{n}`, l'exemple « 1 × 10¹⁰ » de R13). Seul écart sur les valeurs de son propre test
   (`test_approximation_en_notation_scientifique` : 1e10, 1e-4, 0.00099999).
2. **Arrondi à 10⁶** : une valeur que l'arrondi porte à 10⁶ passe en notation scientifique (R13, E14 : « dès 10⁶ ») ; `tex_approx`
   décide avant l'arrondi et écrit 1’000’000,000.
3. **Mi-chemin** : arrondi au-dessus, calculé exactement ; `tex_approx` arrondit la valeur binaire du float (au pair à mi-chemin, ou en
   dessous après la division par 10ⁿ). E14 ne met « ≈ » que sur des irrationnels : sans effet sur le 2e degré.
4. **Zéro négatif** : `0{,}000`, jamais `-0{,}000`.
Aucun ne touche une valeur du corpus d'Exp-log (D13 ci-dessus).

### `exact` et `_nb_exact`

Égalité exacte partout avec `tex(exp_log._nb_exact(v))` sous `_DECIMAUX` = `decimaux_enonce` (mis puis remis par le test, exp_log non
modifié), sur 28 valeurs × 2 états : 0, ±1, −3, 999, 1000, ±4913, 1 234 567 (entiers : `formater_entier`, apostrophe dès 4 chiffres
dans les deux états) ; ±1/2, −5/2, −27/100, 761/400 (décimaux finis : `0{,}5`, `-2{,}5`, `-0{,}27`, `1{,}9025` avec
`decimaux_enonce`) ; 1/3, 2/3, −13/60, 1/3000, 1/512, 1/1024 (pas de décimal fini, ou plus de 8 décimales : fraction gardée avec
`decimaux_enonce=True`) ; 2469/2 (`\frac{2\text{’}469}{2}` ou `1\text{’}234{,}5`), 1/1000, 1/256 (8 décimales), 3/10⁸ (8) et 3/10⁹ (9 :
fraction), 123456789/1000 ; `Decimal("0.50")`, `Decimal("-1.25")`, `"13/60"`. Aucun écart.

### D25 (apostrophe dès 4 chiffres) : état et ce qui changerait

- **Dans `nombres.py` : en place** depuis Q5 (14.10.2026) : `grouper` dès 4 chiffres, `formater_entier` et `formater_decimal` (partie
  entière seulement, `\text{’}` en TeX). `formater_entier` groupe aussi au-delà de 10⁶ (1’234’567) : D25 dit « au-delà, notation
  scientifique (R13) », ce qui vise les valeurs approchées (R13 : « valeurs approchées … dès 10⁶ ») ; une valeur **exacte** entière
  garde son écriture groupée (`exact`, comme l'arbre d'Exp-log). Rien n'est changé dans les fonctions existantes.
- **Outils qui l'appliquent** : Exp-log (arbre `expr.nb_tex`, `tex_approx`, `_trois_decimales`), Étude complète (`parties.decimal_tex`,
  `formater_entier`). **Qui ne l'appliquent pas** : Ensemble de définition (`qtex`, `dec`, texte des nombres de la saisie), Factorisation
  (`qtx` sur `qtex`, `tex_arbre`), Limites (`qtex_`, `fmt_val`, `fmt_approx`, `decimal_tex` de `redaction_bh`) ; côté JS : simplexe
  (`plain`, `nomGrad`) et `graphique.js` (`etiquette`) ; Dérivée écrit ses nombres par SymPy (aucun nombre de 4 chiffres dans son corpus).
- **Ce qui changerait si D25 était appliqué partout** (relevé sur le dump de départ, les instantanés et les références de pages :
  tout entier d'au moins 4 chiffres sans apostrophe dans un champ affiché ; script `b5/d25.py` du scratchpad, lecture seule) :

  | Outil | Où | Entrées touchées | Exemples | Instantanés et références qui changeraient |
  |---|---|---|---|---|
  | Factorisation | Δ de la formule, valeurs P(k) du test des diviseurs | 7 | `= 370881`, `= 84100`, `= 4489`, `P(25) = 152589843775` | `instantanes/factorisation.json`, `instantanes/resoudre/factorisation.json` (7 entrées chacun) ; `tests/pages/references/factorisation.json` |
  | Limites et asymptotes | tableau de valeurs (`fmt_val`) | 4 (dump), 2 (instantanés) | `2202{,}5466`, `-19998{,}99998`, `2752{,}3846` | `instantanes/limites-asymptotes.json`, `instantanes/resoudre/limites-asymptotes.json` (2 entrées) ; `tests/pages/references/limites-asymptotes.json` |
  | Étude complète | tableau de valeurs (même `fmt_val`) | 1 | `(e^x-1)/x` : `2202{,}5466` | `instantanes/etude-complete.json`, `instantanes/resoudre/etude-complete.json` ; `tests/pages/references/etude-complete.json` |
  | Exp-log (C et M) | carte « Interprétation », texte hors TeX | 2 (+ 1 en M) | « 1000 ans », « Au bout de 100000 ans » (le TeX à côté a déjà `1\text{’}000`) ; M : « (rejetée : log_(2x)(1296) … » (saisie recopiée) | `instantanes/resoudre/exponentielles-logarithmes.json` (2), `…-M.json` (3) ; `tests/pages/references/exponentielles-logarithmes.json` et `-M.json` |
  | Ensemble de définition | carte de contrôle numérique (`controle_json`) | 36 | « bien définie aux 5173 points testés » | aucun instantané ; `tests/pages/references/ensemble-definition.json` (52 occurrences) |

  Non compté : le message d'erreur « écrivez 1000 ou 1’000 » (voulu), les empreintes, les énoncés d'exercices (`10^(x-1)=1000`, saisie
  affichée en TeX groupé). Dérivée, simplexe (pas de moteur Python) : rien dans le dump.

### Tests ajoutés

`tests/python/test_nombres.py` (8 → 21 tests ; importe `exp_log` depuis les tests, jamais depuis `moteur/`) :
- `TestApprox` (8) : `test_echantillon` (48 valeurs), `test_croise_avec_tex_approx` (égal, ou écart nommé avec la sortie exacte de
  `tex_approx`), `test_tous_les_ecarts_sont_illustres`, `test_valeurs_du_test_de_tex_approx` (les 10 valeurs de
  `test_exp_log.test_approximation_en_notation_scientifique`), `test_valeur_prise_exactement` (Fraction, Decimal, 10⁴⁰⁰, SymPy, mpmath),
  `test_decimales` (1, 2, 5 décimales), `test_refuse_ce_qui_serait_faux` (∞, NaN, `decimales` invalide), `test_virgule_apostrophe_et_signe`
  (D25 sur tout l'échantillon) ;
- `TestExact` (3) : `test_cas` (28 valeurs, deux états), `test_croise_avec_nb_exact` (56 comparaisons, `_DECIMAUX` remis), refus d'un
  float et de l'infini ;
- `TestPurete` (2) : aucune variable de module changée (A7) ; `exact` ne lit pas `_DECIMAUX`, le code de `nombres.py` ne le nomme pas
  et n'importe que la bibliothèque standard (`ast`).
Seul : 21 passés, 305 sous-tests, 0,2 s. Ciblés (`-n 6`) avec test_exp_log, test_imports, test_manifeste, test_vocabulaire, test_expr :
202 passés, 16 473 sous-tests.

### Vérifications

- Dump `B5` (`--processus 6`) et `B5-1` (`--processus 1`) : `diff -r --exclude=temps` avec `depart` code 0, aucune sortie
  (17 fichiers, 4 148 sorties). Aucun instantané ni référence de page modifié (`git status`).
- Temps natif (`resoudre_json`, 1 processus, comparé à `un-processus` de B0 ; B5 n'ajoute aucun appel dans les outils, écarts de
  bruit) : ensemble-definition 0,033 → 0,033 s ; derivee-variations 0,265 → 0,263 ; limites-asymptotes 5,895 → 5,932 (+0,6 %) ;
  etude-complete 1,998 → 1,982 ; factorisation 1,883 → 1,900 ; EL C 0,888 → 0,933 (+5,1 %) ; EL M 0,764 → 0,784 (+2,6 %). Aucune hausse
  de plus de 50 %. Mur du dump : 12,9 s (1 processus), 4 s (6 processus). Coût propre : `approx` 7,7 µs, `exact` 2,3 µs par appel.
- `test_imports` (aucune arête nouvelle : bibliothèque standard), `test_manifeste` verts ; `test_largeurs` : `CONNUS = {}`.
- Suite d'avant commit : `PROCESSUS_PAGES=4 python3 tests/lancer.py complet --rapport <scratchpad>/briques/rapports/B5`, code 0,
  19 h 14 → 19 h 21 (6 min 51 de mur). Python 1 470 collectés, 1 469 passés + 1 xfail, 106 696 sous-tests (98,0 s) ; pages 145 passés,
  2 421 sous-tests (313,3 s). `comparer_listes` contre le dossier de B4 : 13 tests Python nouveaux (`test_nombres`), aucun disparu ;
  sous-tests : `test_vocabulaire::test_litteraux_des_moteurs` 8 792 → 8 812 (hausse : les littéraux de `nombres.py`) ; pages identiques
  nom par nom. Contre `tests/reference` (B0) : 78 tests Python nouveaux (B1 21, B2 30, B3 13, B4 1, B5 13), 7 de pages, hausses
  seulement, plus la baisse déjà justifiée de `test_exp_log` (1 215 → 960).

## Contrôles du chef d'orchestre

- B0 `b296741` : verifier ACCEPTÉ (Python 1 392 / 106 244 sous-tests, pages 138 / 2 407, identiques à la référence) ; rapide --depuis HEAD~1 : 23 passés, 243 sous-tests, 3 s (fumée + docs).
- B1 `6be8865` : verifier ACCEPTÉ (Python 1 413 / 106 250 sous-tests, 21 tests nouveaux de test_expr, 5 hausses, 1 baisse justifiée ; pages 138 / 2 407 identiques) ; rapide --depuis HEAD~1 : Python 1 368 passés + 1 xfail, 106 194 sous-tests (87 s), pages 138 passés, 1 242 sous-tests (276 s), mur 6 min 06 ; dump identique au départ.
- B2 `572f751` : verifier ACCEPTÉ (Python 1 443 / 106 301 sous-tests, 51 tests ajoutés depuis B0, 5 hausses, 1 baisse justifiée ; pages 138 / 2 407 identiques) ; rapide --depuis HEAD~1 : Python 1 398 passés + 1 xfail, 106 245 sous-tests (97 s), pages 138 passés, 1 242 sous-tests (279 s), mur 6 min 19 ; dump identique au départ (B2).
- B3 `9cee0c4` : verifier ACCEPTÉ (Python 1 456 / 106 391 sous-tests, 64 tests ajoutés depuis B0, 1 baisse justifiée ; pages 145 : 142 passés + 3 xfail stricts « B4 », 2 421 sous-tests) ; rapide --depuis HEAD~1 : Python 1 278 passés + 1 xfail, 96 451 sous-tests (89 s), pages 142 passés + 3 xfail, 1 256 sous-tests (307 s), mur 6 min 38 ; dump identique au départ (B3).
- B4 `d3b7661` : verifier ACCEPTÉ (Python 1 457 / 106 407 sous-tests, 65 tests ajoutés depuis B0, 1 baisse justifiée ; pages 145 passés, 2 421 sous-tests, les 3 xfail « B4 » passés) ; rapide --depuis HEAD~1 : Python 58 passés, 3 756 sous-tests (12 s), pages 145 passés, 1 256 sous-tests (310 s), mur 5 min 23 ; dump identique au départ (B4).

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
