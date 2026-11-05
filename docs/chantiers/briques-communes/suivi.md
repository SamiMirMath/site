# Chantier « Briques communes » — suivi

Branche `briques-communes` (depuis `main` 5ce3f8c), PC (WSL2), `PROCESSUS_PAGES=4`. R5 de la revue de structure
(`docs/chantiers/revue-structure/rapport.md` § 4.2), prérequis de `docs/chantiers/equations-2e-degre/decisions.md`.
Principe : **aucune sortie existante ne change** (dump brut identique à l'octet au dump de départ, instantanés et références de pages
inchangés). Consigne complète, plans et détails : `journal.md`. La consigne du chantier et `decisions.md` du 2e degré (Prérequis, D13,
D25, E14, § 5, P3) tiennent lieu de décisions.

## Résumé (05.11.2026, PC)

Sept parties, sept commits, toutes acceptées par le contrôle allégé (`verifier` ACCEPTÉ, `rapide --depuis HEAD~1` vert, dump brut
identique au départ à l'octet après chaque partie : 4 148 sorties). Aucune sortie existante ne change : aucun instantané, aucune
référence de page modifiés ; aucun outil n'est rebranché sur `approx`, `exact` ni le bloc « chaine » (détail : `journal.md`,
« Contrôles du chef d'orchestre »).

| Partie | Contenu | Commit | Suite d'avant commit | Tests ajoutés |
|---|---|---|---|---|
| B0 | fiches, référence rafraîchie, dump de départ | `b296741` | 6 min 19 | — |
| B1 | `moteur/expr.py` : arbre, TeX, lecture avec un `Lexique` | `6be8865` | 6 min 11 | 21 (`test_expr`) |
| B2 | `moteur/chaine.py` : chaînes du corrigé, 3 propriétés génériques, 3 options | `572f751` | 6 min 44 | 30 (`test_chaine`) |
| B3 | type de bloc « chaine » (`sortie.py`, `rendu.js`, `bloc_chaine`) | `9cee0c4` | 6 min 45 env. | 13 Python, 7 de pages (dont 3 xfail stricts « B4 ») |
| B4 | CSS `.chaine` dans `composants.css`, `details ol` dans `style.css` | `d3b7661` | 6 min 54 | 1 (et les 3 xfail « B4 » passent) |
| B5 | `nombres.approx` et `nombres.exact` (E14, R13, D25) | `abb21fa` | 6 min 51 | 13 (`test_nombres`) |
| B6 | `oracle.racines(coeffs)` (mpmath, 50 chiffres, Sturm) | `f607702` | 6 min 46 | 24 (`test_oracle`) |

Suite finale (chef d'orchestre, sur `f607702`, `PROCESSUS_PAGES=4`) : Python 1 493 passés + 1 xfail, 106 768 sous-tests (108 s) ;
pages 145 passés, 2 421 sous-tests (310 s) ; 6 min 58 de mur ; `verifier` ACCEPTÉ ; `comparer_listes` avec `tests/reference` :
seulement des ajouts (102 tests Python, 7 de pages), des hausses de sous-tests et la baisse justifiée ci-dessous. Même suite avec
`MEMO=0` : code 0, `verifier` ACCEPTÉ, listes identiques nom par nom (7 min 26). Dump de B6 identique au départ à l'octet.

Questions pour l'enseignant (option retenue en attendant) :
1. **B5, zéros de la mantisse** : E14 écrit « 1,000 × 10ⁿ⁺¹ », R13 et `exp_log.tex_approx` « 1 × 10ⁿ⁺¹ ». Retenu : `approx` suit E14
   (zéros gardés) ; aucune sortie actuelle concernée ; à trancher avant de rebrancher Exp-log (R9).
2. **B5, D25 au-delà de 10⁶** : la notation scientifique est lue pour les valeurs approchées seulement. Retenu : une valeur exacte
   entière garde son écriture groupée (`exact(1234567)` = 1’234’567, comme `formater_entier`). À confirmer.
3. **B3–B4, migration d'Exp-log vers le bloc « chaine »** : Exp-log écrit encore sa grille en HTML dans un bloc `texte`. Retenu :
   Exp-log inchangé ; chantier à décider (instantanés et références de pages d'EL à relire), noté dans `architecture.md` § 5.

Exceptions (`architecture.md`) : aucune exception d'import nouvelle. § 5, lignes changées : `exp_log._DECIMAUX` (B1 : la brique ne le
lit pas), « 3 parseurs, 2 arbres, 2 classes `Chaine` » (B1–B2 : les briques communes nommées), « 5 formats de ≈ » (B5 : la fonction
unique existe, outils pas encore rebranchés, R9), « HTML de la grille `.chaine` » (B3–B4 : bloc et CSS communs, reste la migration).
Aussi § 1 (expr, chaine), A4 (HTML refusé dans les champs des blocs récents) et A5 (`approx`, `exact`). Arêtes nouvelles de
`test_imports` : `expr -> noyau`, `expr -> nombres`, `chaine -> expr`, `chaine -> sortie`, `exp_log -> expr`, `exp_log -> chaine`.

À relire par l'enseignant (détail ci-dessous, section « À relire ») :
- B1 : forme du `Lexique` de `moteur/expr.py` et ses deux messages par défaut (`journal.md`, B1).
- B2 : les trois options de `moteur/chaine.py` : étiquette grise, « impossible », texte au milieu (`journal.md`, B2, « Les trois options »).
- B3 : forme du bloc « chaine » et son rendu ; captures dans `/tmp/claude-1000/-home-sami-ubuntu-site/4164342b-a2d3-4999-80ff-850ac94e5e5e/scratchpad/b3/`
  (`sans-b4-390.png`, `sans-b4-1100.png`, `avec-b4-320.png`, `avec-b4-390.png`, `avec-b4-390-sombre.png`, `avec-b4-1100.png`)
  (`journal.md`, B3, « Exécution »).
- B4 : `details ol` retiré aussi de Factorisation et de Limites (doublons) ; section « Chaîne de ⇔ » de `commun/composants.css`
  (`journal.md`, B4, « Rendu identique »).
- B5 : les quatre écarts voulus d'`approx` avec `tex_approx` et l'état de D25 (ce qui changerait, outil par outil) (`journal.md`, B5,
  « Échantillon » et « D25 »).
- B6 : choix d'`oracle.racines` (float refusé, polynôme nul refusé, non réelles non rendues, Sturm, seuil absolu 10⁻²⁰)
  (`journal.md`, B6).

Variations de sous-tests : une seule baisse, justifiée dans la section « Variations de sous-tests » ci-dessous (lue par `verifier`).

## État des parties

| Partie | Contenu | État | Commit |
|---|---|---|---|
| B0 | Fiches, référence rafraîchie (1 392 tests Python dont 1 xfail, 106 244 sous-tests ; 138 tests de pages, 2 407 sous-tests), dump de départ (4 148 sorties, déterministe) | faite (suite verte) | voir `git log` |
| B1 | `moteur/expr.py` : arbre d'Exp-log, `tex`, parseur avec un `Lexique` explicite (« membre = membre » : `lire_membres`) ; e et log restent dans `exp_log` (nœuds `E`, `Log`, `LEXIQUE`) ; réexport par `exp_log` ; manifeste ; `_DECIMAUX` ne traverse pas ; tests ajoutés : `test_expr.py` (21 tests, 144 sous-tests) | faite (suite verte) | voir `git log` |
| B2 | `moteur/chaine.py` : Eq, Rel, Ou, Texte, Chaine, Message, `tex_element`, `tex_chaine`, `rangees_chaine`, 3 propriétés génériques ; `Positif`, `Car`, `Divise` et les 44 autres `PROP_*` restent dans exp_log (s'écrivent eux-mêmes : `chaine.Element`, `chaine.Justification`), coche par `Chaine(coche=True)` ; trois options désactivées par défaut (`etiquette_grise`, `impossible`, `textes`/`texte_avant`) ; réexport ; manifeste ; arêtes `chaine -> expr`, `exp_log -> chaine` ; tests ajoutés : `test_chaine.py` (30 tests, 76 sous-tests) | faite (suite verte) | voir `git log` |
| B3 | Type de bloc « chaine » : `{rangees: [{lien, expr, prop?, gauche?} \| {texte} \| {bloc}]}` (`sortie.chaine`, `rangee`, `rangee_texte`, `rangee_bloc` ; `valider` : HTML refusé, blocs imbriqués `texte`/`formule`/`tableau` validés récursivement) ; `chaine.bloc_chaine(c, etiquette_grise, impossible, membre_gauche)` ; rendu `commun/rendu.js` (mêmes classes que la grille d'EL, `.pleine`, `.avec-gauche`), compléments dans `commun/composants.css` ; arête `chaine -> sortie` ; Exp-log inchangé ; tests ajoutés : `test_sortie.TestBlocChaine` (7), `test_chaine.TestBlocChaine` (6), `tests/pages/test_bloc_chaine.py` (7, dont 3 xfail stricts « B4 ») | faite (suite verte) | voir `git log` |
| B4 | CSS : la grille `.chaine` d'EL dans `commun/composants.css` (une section avec `.pleine`, `.avec-gauche`, un seul `@container`), `details ol` dans `commun/style.css` (avec `details ul`) ; retirés des pages EL, Factorisation, Limites ; rendu identique (styles calculés de toutes les pages, 413 M valeurs, 0 écart) ; les 3 xfail stricts « B4 » de `test_bloc_chaine.py` passent ; test ajouté : `test_style_commun::test_grille_chaine_et_listes_des_rappels_dans_les_feuilles_communes` | faite (suite verte) | voir `git log` |
| B5 | `nombres.approx(x, decimales=3)` et `nombres.exact(x, decimaux_enonce=False)` (TeX), fonctions pures, calcul exact en fractions, aucune fonction existante changée, aucun outil rebranché ; croisées avec `tex_approx` (4 écarts voulus nommés) et `_nb_exact` (égal partout) ; sur les 1 341 valeurs que le corpus d'EL passe à `tex_approx`, `approx` est identique ; D25 vérifié (en place dans `nombres.py`, pas dans ED, FA, LA ni le texte de l'interprétation d'EL) ; tests ajoutés : `test_nombres` (13 tests : `TestApprox`, `TestExact`, `TestPurete`) | faite (suite verte) | voir `git log` |
| B6 | `oracle.racines(coeffs)` dans `tests/python/oracle.py` : coefficients du plus haut degré au terme constant (int, Fraction, Decimal, str ; float refusé ; tête nulle retirée ; polynôme nul refusé) ; liste triée de (racine réelle `mpf` à 50 chiffres, multiplicité), non réelles non rendues (x² + 1 : `[]`) ; compagne `mp.eig` à 30 × degré + 40 chiffres, seuils 10⁻²⁰ tenus pour toute multiplicité ; Newton et nombre de racines réelles par la suite de Sturm exacte ; tests ajoutés : `test_oracle.py` (24 tests, 72 sous-tests) | faite (suite verte) | voir `git log` |

## Vérification après chaque partie

Dump brut comparé au dump de départ (commandes exactes dans `journal.md`, section B0), instantanés et références inchangés, listes de
tests égales à la référence (sauf ajouts annoncés), `test_imports` à jour (aucune arête `chaine` → `exp_log`, aucune arête `moteur/` → un
outil), `test_manifeste` vert, `test_largeurs` avec `CONNUS` vide.

## Questions pour l'enseignant

- B5, mantisse entière : E14 écrit « 1,000 × 10ⁿ⁺¹ » (4 chiffres significatifs, suivi par `nombres.approx` : `1{,}000 \times 10^{10}`),
  R13 et `exp_log.tex_approx` « 1 × 10¹⁰ ». Aucune sortie actuelle n'est concernée (aucune notation scientifique dans le dump d'EL) ;
  à trancher avant de rebrancher Exp-log (R9) : garder les zéros partout, ou les retirer dans `approx`.
- B5, D25 au-delà de 10⁶ : « au-delà, notation scientifique » est lu pour les valeurs **approchées** (R13) ; une valeur exacte entière
  garde son écriture groupée (`exact(1234567)` = 1’234’567, comme `formater_entier` et l'arbre d'EL). À confirmer.
- B3–B4, migration d'Exp-log vers le bloc « chaine » : chantier à décider (Exp-log inchangé en attendant).

## À relire par l'enseignant

- B1 : aucun instantané, aucune référence de page, aucune sortie modifiés (dump identique). À relire : le `Lexique` de
  `moteur/expr.py` (forme du paramètre que le 2e degré passera en P3) et les deux messages par défaut du lexique commun,
  affichés par aucun outil aujourd'hui (`MESSAGE_EXPOSANT_COMMUN`, `MESSAGE_VIDE_COMMUN`) ; détail dans `journal.md`, section B1.
- B2 : aucun instantané, aucune référence de page, aucune sortie modifiés (dump identique). À relire : la forme des trois options de
  `moteur/chaine.py` (détail et exemples dans `journal.md`, section B2, « Les trois options ») :
  - étiquette grise (`etiquette_grise=True`) : propriété sans parenthèses dans les rangées (« ME » ; avec une note : « a ; b ») ; en
    TeX d'une ligne, `\quad \textcolor{gray}{\text{ME}}` ;
  - « impossible » (`impossible=True`) : `\underbrace{6 = 0}_{\text{impossible}}`, seulement dans un « ou » et seulement pour une
    égalité fausse entre deux nombres écrits (6 = 0, −1 = 0) ;
  - texte au milieu (`Chaine(textes=…)`, `ajouter(texte_avant=…)`) : rangée `LigneTexte(contenu)` pleine largeur avant l'élément,
    dont le ⇔ reste relié à l'élément d'avant ; en TeX d'une ligne, `\quad \text{…} \quad` avant le lien.
- B3 : aucun instantané, aucune référence de page, aucune sortie modifiés (dump identique ; aucun outil ne produit encore le bloc).
  À relire : la forme du bloc et son rendu (détail dans `journal.md`, section B3, « Exécution ») :
  - quatre colonnes comme le corrigé (membre de gauche, ⇔, membre de droite, étiquette) avec `membre_gauche=True`, trois comme
    Exp-log sans ; sur un écran étroit, le membre de gauche seul au-dessus, la propriété sous l'expression ;
  - ligne pleine largeur : un texte (TeX entre `\(` `\)`) ou un bloc `texte`, `formule` ou `tableau` (le futur `tableau_essais` de
    P2 s'ajoutera à `BLOCS_DANS_CHAINE`) ;
  - captures à 390 et 1100 px avec le CSS de B4 simulé : `/tmp/claude-1000/-home-sami-ubuntu-site/4164342b-a2d3-4999-80ff-850ac94e5e5e/scratchpad/b3/avec-b4-390.png` et
    `avec-b4-1100.png` dans le même dossier (hors du dépôt).
- B4 : aucun instantané, aucune référence de page, aucune sortie modifiés (dump identique) ; styles calculés identiques avant / après
  sur toutes les pages (méthode et tableau : `journal.md`, section B4). À relire : le `details ol` retiré aussi de Factorisation et de
  Limites (doublons de la règle commune, rendu identique), et la section « Chaîne de ⇔ » de `commun/composants.css`.

- B5 : aucun instantané, aucune référence de page, aucune sortie modifiés (dump identique ; aucun outil n'appelle `approx` ni
  `exact`). À relire (tableau complet de l'échantillon : `journal.md`, section B5) :
  - les quatre écarts voulus avec `tex_approx` : **zéros de la mantisse** (`1{,}000 \times 10^{-3}` au lieu de `1 \times 10^{-3}` :
    10⁶, 10¹⁰, 10⁻⁴, 10⁻⁵, 2 × 10⁷, 0,00099999 et la racine positive de x² + 1000x − 1 = 0) ; **arrondi à 10⁶** (999 999,9996 :
    `1{,}000 \times 10^{6}` au lieu de `1\text{’}000\text{’}000{,}000`) ; **mi-chemin** (arrondi au-dessus : 0,0625 ≈ 0,063 au lieu
    de 0,062 ; 9 999 500 ≈ `1{,}000 \times 10^{7}` au lieu de `9{,}999 \times 10^{6}`) ; **zéro négatif** (`0{,}000`, jamais `-0{,}000`) ;
  - 0,0009995 reste `9{,}995 \times 10^{-4}` (4 chiffres significatifs) : la mantisse n'atteint 10,000 que dès 0,00099995 ;
  - D25 appliqué partout changerait (sans rien changer ici) : Factorisation (Δ et P(k), 7 entrées), Limites et Étude complète (tableau
    de valeurs, 4 et 1), Exp-log (« 1000 ans » de l'interprétation, 2 entrées, et la saisie recopiée `log_(2x)(1296)` en M), contrôle
    numérique de l'ED (« 5173 points testés », 36 entrées, sans instantané) ; liste des instantanés et références : `journal.md`, B5.

- B6 : aucun instantané, aucune référence de page, aucune sortie modifiés (dump identique ; seul `tests/python/` change). À relire : la
  forme de `oracle.racines` (docstring ; détail dans `journal.md`, section B6) : float refusé même exact, tête nulle retirée, polynôme
  nul refusé (ValueError : l'identité, Az 4.1 g, se teste à part), racines non réelles non rendues, et la contre-vérification ajoutée
  (suite de Sturm exacte : un oracle qui ne conclut pas lève ValueError). Limite : deux racines distinctes à moins de 10⁻²⁰ seraient
  regroupées (seuil demandé, absolu).

## Exceptions ajoutées ou changées

- B1–B2 : `architecture.md` § 1 (expr, chaine) et § 5, lignes `exp_log._DECIMAUX` (la brique ne le lit pas) et « 3 parseurs, 2 arbres
  d'expressions, 2 classes `Chaine` » (les briques communes nommées). Aucune exception d'import nouvelle ; arêtes ajoutées à
  ARETES : `expr -> noyau`, `expr -> nombres`, `exp_log -> expr` (B1), `chaine -> expr`, `exp_log -> chaine` (B2).
- B3 : ligne « HTML de la grille `.chaine` écrit dans un bloc `texte` (`resoudre_el.py`) » de `architecture.md` § 5 ajustée : le type de
  bloc `chaine` existe, le CSS passe en B4, la migration d'Exp-log vers le bloc est un chantier **à décider**. Aucune exception
  d'import nouvelle (arête `chaine -> sortie` dans ARETES, brique → brique).
- B4 : même ligne : le CSS `.chaine` est commun (`commun/composants.css`, la page EL n'en garde aucune règle) ; reste seulement la
  migration d'Exp-log vers le bloc (à décider). Liste des règles propres à une page de `test_style_commun` : `details ol` en sort.
- B4, listes de tests : les 3 tests xfail stricts « B4 » de `tests/pages/test_bloc_chaine.py` deviennent passés (voulu) ; un test
  Python ajouté (`test_style_commun`, 7 sous-tests), un sous-test de plus à `test_composants`.
- B5 : `architecture.md` A5 (les deux fonctions) et § 5 (ligne « 5 formats de ≈ » : la fonction unique existe, outils pas encore
  rebranchés, R9 ; `exp_log._trois_decimales` nommé). Aucune exception d'import nouvelle (bibliothèque standard seulement).

## Variations de sous-tests

Lue par `verifier` (voir sa docstring, point (d)). Format, une ligne par test, commençant en début de ligne par un tiret :
`` - `<identifiant pytest complet>` : <avant> → <après> : <raison> `` (« -> » vaut « → »). <avant> et <après> sont les nombres de
sous-tests passés de la référence et du lancement, exactement ceux que `verifier` affiche ; sinon refus.

- `tests/python/test_exp_log.py::TestVouvoiement::test_aucun_texte_du_fichier_ne_tutoie` : 1215 → 960 : B1 (1215 → 1026), les littéraux de l'arbre, du TeX et de la lecture (messages d'erreur de saisie) passent d'exp_log.py à moteur/expr.py ; puis B2 (1026 → 960), les 66 littéraux des chaînes du corrigé (Eq, Chaine, Message, TeX, rangées, 3 propriétés génériques) passent à moteur/chaine.py (100 littéraux ; « car » et « on divise » restent dans exp_log.py, sans le `\quad` de tête). `test_vocabulaire.py::TestVouvoiement::test_litteraux_des_moteurs` les lit dans les deux briques avec le même détecteur (`aides_sortie.TUTOIEMENT`, 8652 → 8694 en B1, 8728 en B2 : + 100 − 66)

## Reprise après compactage

- **Chantier terminé** : B0–B6 faites, suite finale verte sur `f607702` (avec et sans `MEMO=0`), résumé ci-dessus ; reste la fusion
  dans `main`, faite par le chef d'orchestre, et les réponses aux questions ci-dessus.
- Lire `CLAUDE.md`, ce fichier, puis `journal.md` (consigne du chantier, section B0 pour les commandes, section de la dernière partie).
- `git log --oneline main..briques-communes` : un commit par partie faite, puis celui de ce résumé.
- Dump de départ : `/tmp/claude-1000/-home-sami-ubuntu-site/4164342b-a2d3-4999-80ff-850ac94e5e5e/scratchpad/briques/dumps/depart`
  (hors du dépôt ; s'il a disparu, le refaire sur le commit B0 avec `tests/outils/dump_sorties.py`, commande dans `journal.md`).
- Depuis B6, scratchpad : `/tmp/claude-1000/-home-sami-ubuntu-site/a4deaf70-1c56-43d6-bbe6-eeb2ee49f756/scratchpad/briques/`
  (dumps et rapports recopiés, dump de départ vérifié) ; les chemins ci-dessous sont l'ancien emplacement.
- Rapports `complet --rapport` : `/tmp/claude-1000/-home-sami-ubuntu-site/4164342b-a2d3-4999-80ff-850ac94e5e5e/scratchpad/briques/rapports/<partie>`.
