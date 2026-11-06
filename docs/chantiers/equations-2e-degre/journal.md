# Chantier « Équations du 2e degré » — journal

Détail du chantier (plan, tableaux, temps, rapports). La fiche courte est `suivi.md`. Le plan approuvé
(`/home/sami-ubuntu/.claude/plans/pasted-content-id-3dec-chantier-equatio-quizzical-rocket.md`, 05.11.2026, consignes de nuit comprises)
est recopié intégralement ci-dessous, entre les deux filets doubles ; le journal des parties suit.

<!-- ======================== début du plan approuvé (recopié tel quel) ======================== -->

# Chantier equations-2e-degre : plan d'exécution final (05.11.2026, après decisions.md § 13)

## Contexte

L'outil « Équations du 2e degré » et la brique `moteur/second_degre.py` sont décrits par `decisions.md`. Son § 13 (commit b72fe2e sur
`main`) prime sur le reste du fichier. Ce plan les réalise en P0 · P1 · P2a · P2b · P3 · P4a · P4b · P5, puis P6 après relecture.
Il respecte CLAUDE.md, A1–A9, `methode-chantiers.md` (organisation de nuit) et R1–R20.

**Invariant de la nuit (§ 13.1).** `dump_sorties.py` des outils existants est identique à l'octet après chaque partie. P5 n'y ajoute
que le nouvel outil.

L'exploration (3 sous-agents Explore, puis 3 sous-agents Plan Opus, et mes relectures) est décrite dans la version précédente de ce
plan. P0 recopie le plan en tête de `journal.md` : le § 13 y renvoie (Q1–Q13, (a) 1–19).

---

## Consignes d'exécution de nuit (de l'enseignant, 05.11.2026)

Chantier equations-2e-degre : exécution de nuit, sans l'enseignant.

**Ce qui fait foi.**
- `decisions.md` (`docs/chantiers/equations-2e-degre/`), § 13 compris. Ordre : CLAUDE.md > decisions.md > suivi.md > audit-etape0.md.
- Méthode : `docs/methode-chantiers.md`. Architecture : `docs/architecture.md` (A1–A9).
- Ce plan est recopié en tête de `journal.md` et sert de base à chaque partie.

**PARTIES** : P0, P1, P2a, P2b, P3, P4a, P4b, P5 (decisions.md § 13.1), dans cet ordre.

**NE PAS faire** :
- P6 (filières du registre, carte de l'accueil) ;
- changer une sortie d'un outil existant ;
- toucher `trinome` de l'ED autrement que par la façade noyau ;
- l'onglet « S'entraîner » ;
- bicarrées, équations rationnelles, équations à racines ;
- modifier quiz.md ou decisions.md ;
- corriger les tickets du § 11 ;
- commiter un PDF.

**INVARIANT** : après chaque partie, `dump_sorties.py` des outils existants identique à l'octet (seul le nouvel outil s'ajoute en P5).

**Dépendances** : chaque partie dépend de la précédente. Si P0 constate qu'un prérequis manque ou que la suite de départ est rouge,
arrêter toute la session.

**ORGANISATION** : section « Organisation de nuit » de la méthode :
- chef d'orchestre qui ne code pas ;
- un sous-agent general-purpose avec model "opus" par partie, l'un après l'autre ;
- contrôle allégé avec `verifier` et `rapide --depuis HEAD~1` en arrière-plan ;
- ligne dans `journal.md`.

Toutes les suites avec `PROCESSUS_PAGES=4`.

**PRÉCISIONS** :
- Aucune question pendant la nuit : à chaque doute, prends l'option qui affiche le moins ou ne touche à rien d'existant, note-la sous
  « Questions pour l'enseignant » et continue.
- Les 7 points restants du plan sont validés par l'enseignant avec leur option par défaut :
  - `resultat_lim` ;
  - `\fbox` sur la valeur finale de Δ ;
  - rangées sans lien ;
  - D28 pour x² + 4 ;
  - lignes affichées comptées ;
  - liste de `polynomes.py` ;
  - pas de touche √.
- Référence du corrigé : `docs/reference/equations-2e-degre/` (Id_rem et tatonement font foi pour la rédaction ; Javet pour la
  formule). Chaque sous-agent lit decisions.md §§ 3, 5, 7 et 13.
- Écarts voulus au corrigé, à ne pas « corriger » :
  - pas de fractions au tâtonnement (D1) ;
  - étiquette « produit nul » (D5) ;
  - « double distribution » et « distribution » (D27) ;
  - encadrés D29.
- Python pur, sans SymPy, dans `moteur/second_degre.py`. Toute valeur affichée est contrôlée par le garde-fou exact ; `oracle.racines`
  (corrigé en tête de P1) contrôle tous les tests.
- Étapes structurées (§ 5) : la page est construite uniquement à partir des étapes ; la concaténation des rangées est la chaîne
  affichée (test, en JSON).
- Nombres : uniquement par `nombres.approx`, `nombres.exact` et `nombres.py` (A5, R13).
- Toute nouvelle arête d'import est déclarée dans le graphe figé, avec sa raison (A1).
- Temps natif de `resoudre_equation` sur le corpus § 8 après chaque partie (objectif < 0,1 s).

**RÈGLES** : section « Règles d'exécution » de la méthode, recopiée mot pour mot dans la consigne de chaque sous-agent.

**Fin** :
- suite complète par le chef d'orchestre (aussi avec `MEMO=0`) ;
- résumé en tête de `suivi.md`, avec le texte rendu de 2.11 h et la liste « À relire par l'enseignant » (captures à 390 px copiées hors
  de /tmp, chemins dans `suivi.md`) ;
- branche poussée ; pas de fusion.

---

## Ce qui reste contradictoire ou impossible après le § 13

Chaque point a une option par défaut, celle qui affiche le moins ou qui ne touche à rien d'existant. Le chef d'orchestre la prend si
vous ne tranchez pas, et la note sous « Questions pour l'enseignant ».

1. **S « dans `sortie.resultat` (`.rbox`) ».** `sortie.resultat` est rendu `.res` (filet pointillé, `rendu.js:127`). C'est
   `sortie.resultat_lim(tex)` qui est rendu `.rbox` (`rendu.js:136`, le cadre vert de Limites).
   - **Défaut** : `resultat_lim`, dans une carte normale, avec une docstring élargie à « résultat encadré ».
   - Aucun code nouveau, aucune sortie existante changée.
2. **« Δ = 20 encadré en entier ».** Dans la ligne d'E10, `Δ = b² − 4ac = 4² − 4 · 1 · (−1) = 16 + 4 = 20`, Δ et 20 ne sont pas
   côte à côte. Encadrer la ligne entière ferait une boîte insécable trop large pour 320 px (`test_largeurs` échouerait).
   - **Défaut** : `\fbox` sur la seule valeur finale (« = ⟦20⟧ »).
   - Autre possibilité, si vous la préférez : « ⟦Δ = 20⟧ > 0 : deux solutions. » à la ligne suivante. Elle réécrit Δ une 2e fois
     (R5).
3. **Chaîne sans aucun ⇔** (2.12 b, Javet 2.17 d, x² + 4 = 0, variante Δ = 0, où l'équation n'est pas répétée, § 13.3). Si toutes les
   rangées sont des lignes pleine largeur, `sortie.valider` refuse le bloc (« une chaîne a au moins une ligne {lien, expr} »,
   `sortie.py:349`).
   - **Défaut** : les lignes de Δ, √Δ, x₁ et x₂ sont des rangées `{lien: "", expr: TeX}` (les mots en `\text{}`). Elles sont au bord
     gauche quand la chaîne n'a pas de ⇔, et dans la colonne des expressions sinon (à juger à la relecture).
   - Les phrases seules (« Δ < 0 : … », identité, phrase de choix, diviseurs) restent des `rangee_texte`.
   - Le validateur n'est pas touché.
4. **x⁴ − 16, facteur x² + 4 « par la formule ».** D28 et le § 6 (cas limite x² + 4 = 0 : S-P avec b = 0, tableau puis Δ < 0) font
   passer un trinôme unitaire à coefficients entiers par le tableau S-P d'abord.
   - **Défaut** : une seule règle, D28 : tableau S-P en échec, puis E9 « Δ < 0 : x² + 4 = 0 n'a aucune solution réelle ».
5. **Tableau S-P de plus de 12 lignes.**
   - Le texte ne dit pas ce qui est compté : les lignes affichées jusqu'à ✓, ou tous les diviseurs ≤ √|c|.
   - `s_applique(SP)` = « un couple existe » reste vrai alors que le chemin prend la formule (D28 ; QZ-05 plus tard).
   - **Défaut** : on compte les lignes qui seraient affichées. Au-delà de 12, la phrase du § 13.5, puis la formule. Le test D28
     nomme cette exception.
6. **Déplacement de `_pq` (Q2) : liste à compléter, sans contradiction.**
   - `_const` dépend de `_puissance_rationnelle_exacte`, `_racine_entiere_exacte` et `_racine_carree` (`exp_log.py:417–437`) ;
     `_pq` dépend de `_pmul_n` et `DEGRE_MAX` (`exp_log_m.py:534–537`).
   - Ces fonctions partent aussi dans `moteur/polynomes.py`, car une brique ne peut pas importer `exp_log` (A1).
   - `_pq` lève `_Hors` sans raison : l'analyse d'`equations.py` diagnostique avant (lettres, √, dénominateur, exposant). Un `_Hors`
     qui arrive ensuite ne peut plus venir que du degré > 8, et donne le message des bornes.
7. **Clavier, « √ gardé ailleurs ».** Les trois rangées communes (`test_source_unique.TROIS_RANGEES`) n'ont pas de √. Avec la dernière
   rangée `0 , x =`, il n'y a donc **aucune** touche √. C'est cohérent avec l'outil, qui refuse √ (§ 13.5) ; à confirmer seulement.

Rien d'autre n'est impossible : les autres réponses du § 13 se réalisent avec le code existant (vérifié ci-dessous).

---

## Conventions de la nuit

- **Branche** `equations-2e-degre`, créée depuis `main` à jour (b72fe2e).
- **Chef d'orchestre** : la session principale, qui ne code pas.
- **Sous-agents** : un sous-agent general-purpose Opus par partie, l'un après l'autre. La consigne recopie les « Règles d'exécution »
  de la méthode mot pour mot.
- **Fin de partie (sous-agent)** :
  1. `PROCESSUS_PAGES=4 python3 tests/lancer.py complet --rapport <S>/rapports/Pn`, sans pipe, code 0 exigé ;
  2. `python3 tests/outils/dump_sorties.py <S>/dumps/Pn --processus 6`, puis `diff -r --exclude=temps <S>/dumps/depart <S>/dumps/Pn`,
     vide exigé (de P5 à P6 : seuls les fichiers du nouvel outil apparaissent) ;
  3. le temps natif de `resoudre_equation` sur le corpus va dans `journal.md` ;
  4. `git status`, `git add` des fichiers nommés un par un, `git diff --cached`, commit au premier plan.
- **Contrôle du chef** :
  1. `git log --oneline -3` ;
  2. `python3 tests/lancer.py verifier <S>/rapports/Pn` → ACCEPTÉ ;
  3. `PROCESSUS_PAGES=4 python3 tests/lancer.py rapide --depuis HEAD~1`, en arrière-plan : il dépasse 5 min de P1 à P4, ce que le
     § 13.2 accepte ;
  4. une ligne dans `journal.md`, section « Contrôles du chef d'orchestre ».
- **Test instable `test_clavier`** : on le relance seul, puis on relance toute la suite.
- **Signatures vérifiées** :
  - `expr` : `Nb(val, dec=None, pct=None)`, `Var`, `Neg`, `Op(op, a, b)`, `Pow`, `Fn(nom, a)`, `Defini(nom, arbre)`,
    `variables(n)`, `tex(n)`, `Lexique(fonctions=("sqrt",), …, message_exposant, message_vide)`,
    `lire_membres(texte, lexique) -> (g, d|None)`, `MESSAGE_INEQUATION` ;
  - `chaine` : `Eq`, `Ou`, `Texte`, `Message`, `Chaine(elements, liens, props, note, coche, textes)` et
    `.ajouter(element, lien, prop=None, texte_avant=None)`, `LigneTexte`, `rangees_chaine(c, etiquette_grise, impossible)`,
    `bloc_chaine(c, etiquette_grise, impossible, membre_gauche)` ;
  - `sortie` : `chaine`, `rangee(lien, expr, prop=None, gauche=None)`, `rangee_texte`, `rangee_bloc`, `carte(...)`, `resultat_lim(tex)`,
    `variante(cle, libelle, cartes, option=True)`, `sortie_ok_variantes(enonce_tex, variantes, defaut)`, `sortie_erreur`, `valider` ;
  - `nombres` : `approx(x, decimales=3)`, `exact(x, decimaux_enonce=False)` ;
  - `noyau` : `pn`, `deg`, `nul`, `padd`, `pscal`, `pmul`, `peval`, `pdivlin` (Fraction, ordre croissant), `ErreurSaisie` ;
  - tests : `oracle.racines(coeffs)` (ordre décroissant).

---

## P0 : prérequis et référence

- **Prérequis** : tous présents sur `main` (vérifié : `chaine.py` avec ses options, `expr.lire_membres`, bloc `chaine` avec `{bloc}`,
  `nombres.approx`/`exact`, `oracle.racines`, `.chaine` dans `composants.css`). S'il en manquait un : arrêt.
- **PDF** : `git check-ignore -v docs/reference/equations-2e-degre/*`. Ils sont déjà rangés.
- **Fichiers** :
  - `docs/chantiers/equations-2e-degre/suivi.md`, sur le modèle de briques-communes : État, Questions (les 7 points ci-dessus),
    À relire, Exceptions, Variations de sous-tests (vide), Reprise après compactage ;
  - `journal.md`, avec ce plan recopié en tête ;
  - `tests/reference/*`.
- **Séquence** :
  1. `complet --rapport <S>/rapports/P0-ref`. Rouge : arrêt.
  2. `reference <S>/rapports/P0-ref`.
  3. **Dump de départ obligatoire** : `dump_sorties.py <S>/dumps/depart --processus 6`, puis `--processus 1` pour les temps natifs.
  4. 2e suite : `complet --rapport <S>/rapports/P0`, avec `tests/reference` modifié. Sans elle, `verifier.py:135` refuse.
  5. Commit.
  6. `verifier`.
- **Session** : un `MEMO=0 … complet --rapport` une fois, en fin de session.

## P1 : calcul, sans texte

**1. Correction de l'oracle, en tête (Q11).**
- `tests/python/oracle.py::racines` retire d'abord les racines nulles : termes constants nuls, multiplicité connue.
- Test `[7, -19, 0]` dans `test_oracle.py`. C'est un renforcement, à noter sous « À relire ».

**2. Déplacements (Q2), avec réexport sous les mêmes noms et assertions d'identité (`assertIs`, modèle
`test_expr.TestReexportParExpLog`).**
- Nouveau `moteur/polynomes.py`, qui reçoit :
  - d'`exp_log_m` : `pq`, `pmul_n`, `DEGRE_MAX` ;
  - d'`exp_log` : `const`, `puissance_rationnelle_exacte`, `racine_entiere_exacte`, `racine_carree`, `padd`, `pnet`, `Hors`. `_Hors`
    reste le même objet.
- `exp_log.py` et `exp_log_m.py` les réexportent sous leurs noms privés.
- Manifeste d'EL : + `moteur/polynomes.py`, placé avant `exp_log.py`.
- `moteur/noyau.py` : + `squarefree`, `racine_q` dans la façade (deux réexports).
- `docs/architecture.md` § 5 : les 4 copies de la simplification k√m/d deviennent une dette nommée (« nombres partout »).

**3. `moteur/second_degre.py`.**

| Élément | Rôle |
|---|---|
| `Polynome` | tuple de Fraction, ordre croissant |
| `vers_polynome(arbre, inconnue)` | `polynomes.pq`, puis le contrôle des bornes du § 13.5 : degré ≤ 8, numérateurs et dénominateurs ≤ 9 chiffres |
| `Nombre(p, q, m)` | p + q√m, sur `noyau.squarefree`/`racine_q` ; arithmétique ; comparaison exacte ; `forme_reduite()` (E11) ; `encadrement()` par `isqrt` |
| `mise_en_evidence(P, constante=True)` | pgcd, xᵏ, −pgcd (D21) ; rien si les coefficients ne sont pas entiers (§ 13.4) |
| `identite(P)` | A = k·xʲ (x⁴ − 16 : A = x², § 13.4) ; B rationnel ou sous forme simplifiée (2√2, √2/2) |
| `essais_sp(b, c)` | E6, arrêt à ✓, liste complète si échec, borne de 12 lignes (point 5) |
| `diviseurs_signes(c)` | sans borne |
| `racine_entiere_unique(P)` | décidée par Δ, aucune borne silencieuse ; on ne réutilise **pas** `factorisation.somme_produit`/`racine_entiere` |
| `racines_formule(P)` | Δ et racines |
| `s_applique(methode, P)` | « aboutit » (§ 13.4) |
| `calculer(methode, P)` | le calcul seul (sans texte) |
| `chemin(P, methodes=ORDRE_DU_COURS)` | ordre fixe (D28) |
| `produit_nul` | D14, D24 ; 3x² = 0 ⇔ x = 0 |
| `redevelopper`, `verifier_solution` | garde-fou dans Q(√m) |
| `approx_garantie(x, decimales=3)` | `nombres.approx` sur les deux bornes de l'encadrement, raffiné jusqu'à l'égalité |

**4. Tests.**
- `tests/python/test_second_degre.py` :
  - oracle sur le corpus § 8 (développé) et sur des polynômes générés (graine fixe ; entiers, fractions, décimaux ; jamais de float) ;
  - garde-fou (multiplication réécrite dans le test) ;
  - `s_applique` ⇒ `calculer` se redéveloppe (Δ ≥ 0), et S = ∅ contrôlé par l'oracle (Δ < 0) ;
  - D28, avec l'exception nommée du point 5 ;
  - valeurs ≈ du § 8, dont x² + 1000x − 1 (`1 × 10⁻³` et `−1’000,001`) ;
  - bornes ;
  - tranches de moins de 10 s.
- `tests/python/test_polynomes.py` : réexports, et identité de `pq` sur le corpus d'EL.
- **Dump EL identique** (invariant).

**5. Arêtes nouvelles.** `polynomes -> expr`, `exp_log -> polynomes`, `exp_log_m -> polynomes`, `second_degre -> polynomes`,
`second_degre -> noyau`, `second_degre -> nombres`.

## P2a : affichage commun

- **`moteur/sortie.py`** :
  - `BLOCS["tableau_essais"] = ({"groupes", "lignes"}, set())` ;
  - constructeur `tableau_essais(groupes, lignes, ok=None)` ;
  - `_valider_essais` : sans HTML (A4), colonnes cohérentes, au plus une ligne ok ;
  - `BLOCS_DANS_CHAINE += ("tableau_essais",)` ;
  - docstring de `resultat_lim` élargie (point 1).
- **`commun/rendu.js`** : `BLOCS.tableau_essais` (tableau dans `.essais`, ✓ ajouté par le rendu sur `ok`).
- **`commun/composants.css`** :
  - `.essais` ; `tr.ok` en `--good` / `--ok-soft` ;
  - D29 : `.katex .fbox{border-color:var(--good);background:var(--ok-soft);…}`, au moins aussi précis que `.katex *`.
- **`moteur/chaine.py`**, sans effet sur Exp-log, qui n'appelle pas `bloc_chaine` :
  - `bloc_rangees(rangees, membre_gauche=False)`, sorti de `bloc_chaine` ;
  - option `coupure_ou=False` de `tex_element`, passée par `rangees_chaine`, `bloc_chaine` et `bloc_rangees` : coupure permise après
    « ou » (`\allowbreak`), désactivée par défaut.
- **Tests** :
  - `test_sortie` : l. 165 et le dictionnaire de la l. 169, plus les refus ;
  - `test_chaine` : `bloc_chaine == bloc_rangees(rangees_chaine)` ; l'option désactivée garde le même TeX ;
  - `test_composants` ;
  - nouveau `tests/pages/test_tableau_essais.py`, sur le modèle de `test_bloc_chaine` (cartes rendues dans la page de l'ED) :
    2.10 a, S-P en échec, x² + 4, une étiquette « avec ⟦A = 4z, B = 9⟧ », un produit nul à 3 facteurs ; 320–1100 px, clair et sombre ;
    bordure calculée = `--good` ; rien ne déborde.

## P2b : rédaction dans `second_degre`

- **API du § 5** : `resoudre_equation(gauche, droite, inconnue, decimaux_enonce=False, methodes=ORDRE_DU_COURS) -> Resolution`, et
  `appliquer(methode, P) -> Etape | None` (calcul P1 + rédaction).
- **`Etape.lignes`** = rangées (`rangees_chaine` et `LigneTexte`). Chaque étape est un segment `Chaine([pivot, …])` dont le premier
  lien est ⇔.
- **Disposition (§ 13.3)** :
  - phrase de choix et tableau d'abord, puis l'équation en membre de gauche ;
  - lignes de Δ en rangées (point 3) ;
  - aucune répétition de l'équation quand aucun ⇔ ne suit.
- **Rédaction** :
  - E3–E12 : Δ selon le § 7, identité selon Exp-log (« Cette égalité est vraie pour tout nombre réel. ») ;
  - E14 : `nombres.exact` et `approx_garantie` ;
  - D20, D24 ;
  - D29 : `\fbox{$…$}` sur A et B (y compris dans l'étiquette grise), sur la ligne ✓, sur r et △, sur la valeur de Δ (point 2) ;
  - S en `resultat_lim`, carte normale ;
  - x₁ et x₂ par `Defini` (variante a < 0 : x₁ avec −√Δ, S croissant) ;
  - un `Nb` exact selon `decimaux_enonce` (sans état ; test croisé avec `exp_log._nb_exact`) ;
  - étiquettes en texte (« ME », « produit nul », « double distribution »).
- **Arêtes** : `second_degre -> chaine`, `-> sortie`, `-> expr`.
- **Instantanés dès P2b (§ 13.2)** :
  - `tests/python/test_instantanes_second_degre.py` (motif `test_instantanes*`, `normaliser` de `test_instantanes`) ;
  - JSON **hors d'`instantanes/`** jusqu'en P5 : `tests/python/donnees/equations-2e-degre/instantanes.json`. C'est la voie la plus
    simple : `dump_sorties` n'est pas touché ;
  - le test contrôle lui-même le JSON strict et le vocabulaire, puisque les contrôles de `instantanes/` ne le voient pas encore.
- **Autres tests** :
  - invariant : JSON du bloc affiché = `bloc_rangees(concaténation des lignes, membre_gauche=True)`, et repliement des segments
    = `rangees_chaine` de la chaîne entière ;
  - R12 et vocabulaire ;
  - cas limites du § 6 ;
  - 2.9–2.12 développés, Javet 2.17.

## P3 : saisie

- **`second_degre`** :
  - E1 (ramener : côté du coefficient de tête positif, ordre décroissant, ligne de réordonnancement, phrase seulement avant une phrase
    de choix) ;
  - E2 (développer en montrant les produits, « double distribution » / « distribution », « − (…) » puis sans parenthèses).
  - Le cas 3 d'E1 passe par le développement seulement.
- **`moteur/expr.py`** : + `a_des_decimaux(n)`, déplacé d'`exp_log._a_des_decimaux` (l. 754) et réexporté (`assertIs`).
- **`equations-2e-degre/equations.py`**, créé ici et chargé par chemin dans ses tests jusqu'en P5 :
  - `LEXIQUE_EQ = Lexique(message_vide="Écrivez une équation.", message_exposant=<exemple x^2>)`, en **gardant
    `fonctions=("sqrt",)`** ;
  - `analyser(texte) -> (gauche, droite, inconnue, decimaux_enonce)` ou `ErreurSaisie`, dans l'ordre du § 13.5 : vide, syntaxe,
    pas de « = », aucune lettre, plusieurs lettres, inconnue en exposant, inconnue sous √ ou au dénominateur ou exposant non entier
    ou négatif, √ sans l'inconnue, division par 0, bornes ;
  - D23.
- **Tests** : `tests/python/test_equations_saisie.py` :
  - chaque message, et l'ordre de priorité sur des saisies mixtes ;
  - notation suisse ; décimaux de l'énoncé ;
  - (x + 1)(x + 3) = 15 ; Az 4.1 g ;
  - e^x = 2 donne « une seule inconnue ».
- **Arêtes** (déclarées en P5, quand `equations.py` entre dans le graphe) : `equations -> expr`, `-> noyau`, `-> second_degre`.

## P4a : formes structurées, sur l'arbre avant tout développement

- (binôme)² − m, k(binôme)² − m, m − (binôme)² : 2.9 k (« car A² = 4(x − 2)² »), 2.9 l, 2.12 h ((3x + 6)(2 − 3x), sans ME après
  coup).
- Facteur commun aux deux membres, avec l'avertissement (2.12 e).
- Produit déjà factorisé (Az 4.1 d).
- E1.3 (ramener sans développer).
- Le tout dans `second_degre`, sur P1.
- **Tests** : oracle et instantanés de ces cas.

## P4b : degrés ≠ 2 et reste du corpus

- ME de xᵏ en degré ≥ 3 (2.12 c, Az 4.1 f).
- Id. rem. en degré 4 (x⁴ − 16, facteurs par D28 et E9, point 4).
- E9.
- Degré 1 : ramener, puis isoler en une ou deux lignes (D20).
- Identité et égalité fausse.
- Message « bicarrée », seulement si ni ME ni Id. rem. ne s'applique (x⁴ − 5x² + 4) ; sinon « hors du cours ».
- Garde-fou en échec : message « ne conclut pas ».
- **Tests** : oracle et instantanés sur **tout** le corpus § 8 et les cas limites du § 6.

## P5 : l'outil (un sous-agent, liste à cocher)

| Fichier | À écrire |
|---|---|
| `equations-2e-degre/index.html` | `monterOutil` ; `const EXEMPLES=[10 entrées du § 13.3];` ; GoatCounter ; `style.css` puis `composants.css` ; aria-live ; `<details class="card">` « Rappel de la méthode » fermé (E15) ; clavier, dernière rangée `0 , x =` ; aucun `exercicePython` |
| `equations-2e-degre/resoudre_eq.py` | `resoudre`, `resoudre_json`, `apercu_json` (aperçu syntaxique : `apercu_json('x+1')` doit rendre ok) ; variante E12 par `sortie_ok_variantes` |
| `moteur/manifeste.json` | `module: resoudre_eq` ; fichiers : `ensemble_def`, `noyau`, `nombres`, `expr`, `polynomes`, `chaine`, `sortie`, `second_degre`, `equations`, `resoudre_eq` ; fonctions `["resoudre", "apercu"]` |
| `commun/registre.json` | option A : entrée `"filieres": {}` |
| `tests/pages/test_accueil.py:61` | butée (16, 7) → (16, 8) |
| `tests/python/test_imports.py` ARETES | `equations -> …` (P3), `resoudre_eq -> equations / sortie / second_degre / chaine`, chacune avec sa raison |
| `tests/python/test_noyau.py` MOTEURS | `equations-2e-degre/equations.py` |
| `tests/python/test_outils_du_site.py:56` | butée `test_ordre_de_sys_path` + `"equations-2e-degre"` |
| `test_instantanes.py` et `instantanes/equations-2e-degre.json` | le JSON de P2b déplacé ici, entrée `OUTILS` et méthode |
| `test_instantanes_resoudre.py` et `instantanes/resoudre/equations-2e-degre.json` | entrée, méthode, `REGENERER=1` |
| `cas.py` `CAS_LIMITES` (ou `cas_eq.py` avec une branche de `rendu.entrees`) | corpus § 8 et § 6 |
| `test_vocabulaire.METHODES` | méthode `test_equations_2e_degre` |
| `test_json_strict` | `OUTILS_ENTREES` et une méthode |
| `test_resoudre_import.EXEMPLE` | `x^2-5x-36=0` |
| `test_source_unique.TestDispositionDuClavier.PAGES` | `["0", ",", "x", "="]` |
| `tests/pages/rendu.py` REDUIT | 2.10 a, 2.11 h, `x^2+1` (erreur) |
| `tests/pages/test_comportement.py` | `CALCUL` = Javet 2.17 c (sans variante, `test_t33`), `EXEMPLE` = 2.9 a, `INVALIDE` |
| `tests/pages/test_rendu.py` | `test_equations_2e_degre` |
| `tests/pages/references/equations-2e-degre.json` | `capturer_references.py equations-2e-degre` |
| `docs/architecture.md` § 1, § 4 (avec les oublis relevés), § 5 ; `docs/taches.md` (D16) | — |
| rien à écrire (vérifié) | `test_largeurs` (méthode générée, vu le registre), `test_style_commun`, `test_tableaux_css`, `MIGREES`, `TestVouvoiement`, `test_memo_garde`, `captures.py`, `lancer.py` |

L'état « Chargement… » tant que SymPy n'est pas prêt est accepté (Q7, ticket (g)).

## P6 : après la relecture (pas de nuit)

- Corrections de relecture.
- Filières au registre (1M : Ms et Mr ; 1C ; 2C).
- Carte de l'accueil.
- Butée de `test_accueil` (nombre de liens).
- `test_acc01`.

---

## Vérification

- **Chaque partie** : `complet --rapport`, code 0 ; dump identique au départ ; `verifier` ACCEPTÉ ; `rapide --depuis HEAD~1`.
- **Fin de session** :
  1. `complet --rapport FIN`, puis `verifier` et `comparer_listes.py tests/reference FIN` ;
  2. `MEMO=0 … complet --rapport FIN-memo0`, listes identiques ;
  3. dump final : identique pour les outils existants, seul le nouvel outil en plus.
- **Relecture** : résumé en tête de `suivi.md`, avec :
  - le texte rendu de 2.11 h ;
  - des captures à 390 px de 2.11 h, 2.10 a, Javet 2.17 c, 2.12 e et (x + 1)(x + 3) = 15 ;
  - les instantanés ;
  - le ⏸ de la ligne du tâtonnement en échec ;
  - les 7 points ci-dessus.
- **Fusion** (par vous) : `git checkout main && git merge --no-ff --no-edit equations-2e-degre`.

<!-- ======================== fin du plan approuvé ======================== -->

---

# Journal des parties

## P0 — prérequis, fiches, référence, dump de départ

### Plan

1. Prérequis (liste du plan et « Signatures vérifiées ») vérifiés sur la branche ; PDF de référence ignorés par git.
2. `suivi.md` (court) et ce journal, seuls fichiers modifiés (sous `docs/`) pendant la suite de référence.
3. `PROCESSUS_PAGES=4 python3 tests/lancer.py complet --rapport S/rapports/P0-ref` sur b72fe2e, puis
   `python3 tests/lancer.py reference S/rapports/P0-ref`.
4. Dump de départ : `dump_sorties.py S/dumps/depart --processus 6`, puis `S/dumps/depart-p1 --processus 1` (temps natifs) ;
   `diff -r --exclude=temps` (déterminisme).
5. 2e suite `complet --rapport S/rapports/P0` (avec `tests/reference/` modifié), commit, `verifier S/rapports/P0`.

`S` = `/home/sami-ubuntu/nuits/equations-2e-degre`.

### Prérequis

Tous présents sur b72fe2e (lecture des sources, 05.11.2026) :

- `moteur/chaine.py` : `Eq`, `Rel`, `Texte`, `Ou`, `Chaine(elements, liens=(), props=(), note=None, coche=False, textes=None)` et
  `.ajouter(element, lien, prop=None, texte_avant=None)`, `Message`, `LigneTexte`, `tex_element(e, impossible=False)`,
  `tex_chaine(c, etiquette_grise=False, impossible=False)`, `rangees_chaine(c, etiquette_grise=False, impossible=False)`,
  `bloc_chaine(c, etiquette_grise=False, impossible=False, membre_gauche=False)`.
- `moteur/expr.py` : `Nb(val, dec=None, pct=None)`, `Var(nom)`, `Neg(a)`, `Op(op, a, b)`, `Pow(a, b)`, `Fn(nom, a)`,
  `Defini(nom, arbre)`, `variables(n)`, `tex(n)`, `MESSAGE_INEQUATION`, `Lexique` (champs `fonctions` (défaut `("sqrt",)`), …,
  `message_exposant`, `message_vide`), `lire_membres(texte, lexique=LEXIQUE_COMMUN)`.
- `moteur/sortie.py` : `BLOCS["chaine"] = ({"rangees"}, set())`, `chaine(rangees)`, `rangee(lien, expr, prop=None, gauche=None)`,
  `rangee_texte`, `rangee_bloc(bloc)` (`{bloc}`), `carte(...)`, `resultat_lim(tex)`, `variante(cle, libelle, cartes, option=True)`,
  `sortie_ok_variantes(enonce_tex, variantes, defaut, option=None)` (un paramètre facultatif de plus que la signature du plan, sans
  effet), `sortie_erreur(message, detail=None)`, `valider(s)`.
- `moteur/nombres.py` : `approx(x, decimales=3)`, `exact(x, decimaux_enonce=False)`.
- `moteur/noyau.py` (façade) : `pn`, `deg`, `peval`, `pdivlin`, `pmul`, `padd`, `pscal`, `nul`, `ErreurSaisie`.
- `tests/python/oracle.py::racines(coeffs)`.
- `commun/composants.css` : section « Chaîne de ⇔ du corrigé » (`.chaine`, l. 58 et suivantes).

PDF de référence : `git check-ignore -v docs/reference/equations-2e-degre/*` (code 0) : les 4 fichiers (`1MRe Notion elem copie.pdf`,
`1M_Algebre_Az_2019 (glissé(e)s).pdf`, `Id_rem.pdf`, `tatonement.pdf`) sont ignorés par `.gitignore:6:docs/reference/` ; aucun
fichier de `docs/reference/` n'est suivi (`git ls-files docs/reference` vide).

### Référence rafraîchie

- 1er lancement : `PROCESSUS_PAGES=4 python3 tests/lancer.py complet --rapport S/rapports/P0-ref` sur b72fe2e (seules les deux fiches
  non suivies), 22 h 43 → 22 h 50 (6 min 52 de mur) : **code 1**. Python vert (1 493 passés + 1 xfail, 106 768 sous-tests, 99 s) ;
  pages 145 passés et **1 sous-test échoué** : `tests/pages/test_comportement.py::TestComportement::test_soc04_parametre_f`
  (`outil='ensemble-definition'`), `TypeError: Cannot read properties of null (reading 'children')` sur
  `document.querySelector('#cartes')` : la page n'était pas encore chargée quand le test l'a lue (course au chargement sous charge,
  pas une sortie). Rapport et console gardés dans `S/rapports/P0-ref-rouge1/`.
- Diagnostic : le test relancé seul (`uv run … pytest tests/pages/test_comportement.py::TestComportement::test_soc04_parametre_f`)
  passe : 1 passé, 6 sous-tests, 12 s. Instabilité traitée comme celle de `test_clavier` (relancé seul, puis suite relancée), sans
  rien modifier ; notée sous « Questions pour l'enseignant » de `suivi.md`.
- 2e lancement, même commande, même arbre : 22 h 55 → 23 h 02 (6 min 43 de mur) : **code 0**. Python 1 494 collectés, 1 493 passés
  + 1 xfail, 106 768 sous-tests, 92,1 s ; pages 145 passés, 2 421 sous-tests, 311,1 s.
- `python3 tests/lancer.py reference S/rapports/P0-ref` : acceptée (code 0). Différences avec l'ancienne référence (5ce3f8c, B0 de
  briques-communes) : uniquement le chantier briques-communes fusionné depuis (102 tests Python et 7 tests de pages nouveaux, aucun
  retiré ; 9 lignes de sous-tests changées, dont la baisse justifiée de `test_exp_log.py::TestVouvoiement` 1215 → 960). Mêmes nombres
  que la suite finale de briques-communes (f607702). `git diff --stat tests/reference` : `collecte-pages.txt` (+7),
  `collecte-python.txt` (+102), `origine.txt`, `resultats-pages.txt` (+7), `resultats-python.txt` (+111 −9).

### Dump de départ

- Commandes (sur b72fe2e, arbre : fiches et `tests/reference/`) :

      python3 tests/outils/dump_sorties.py S/dumps/depart --processus 6
      python3 tests/outils/dump_sorties.py S/dumps/depart-p1 --processus 1
      diff -r --exclude=temps S/dumps/depart S/dumps/depart-p1

- Résultat : 17 fichiers, **4 148 sorties**, 9,0 Mo ; 4 s de mur (6 processus), 13 s (1 processus) ; `diff` code 0, aucune sortie
  (**déterministe**). Mêmes 17 fichiers et 4 148 sorties qu'au départ de briques-communes.
- **Commande de comparaison pour les parties suivantes** (`<Pn>` = P1, P2a…, dossier absent ou vide) :

      python3 tests/outils/dump_sorties.py S/dumps/<Pn> --processus 6
      diff -r --exclude=temps S/dumps/depart S/dumps/<Pn>

  Code 0 et aucune sortie exigés (en P5, seuls les fichiers du nouvel outil s'ajoutent). Temps : `--processus 1` (dossier
  `<Pn>-p1`), à comparer au tableau « Temps » ci-dessous.

### Suite d'avant commit

`PROCESSUS_PAGES=4 python3 tests/lancer.py complet --rapport S/rapports/P0` sur b72fe2e (fiches et `tests/reference/` modifiés, non
commités) : **code 0**, 23 h 03 → 23 h 10 (6 min 39 de mur). Python 1 494 collectés, 1 493 passés + 1 xfail, 106 768 sous-tests,
89,8 s ; pages 145 passés, 2 421 sous-tests, 309,5 s. `python3 tests/comparer_listes.py tests/reference S/rapports/P0` : identique nom
par nom (Python et pages). Aucun test ajouté par P0. Commit : « equations-2e-degre P0 : fiches, référence, dump de départ » ;
`verifier S/rapports/P0` après le commit (verdict dans le rapport au chef d'orchestre et dans « Contrôles du chef d'orchestre »).

## P1 — calcul, sans texte

### Plan

1. **Oracle (Q11)** : `oracle.racines` retire d'abord les termes constants nuls (racine 0 de multiplicité connue), puis cherche les
   autres racines sur le quotient ; test `[7, -19, 0]` (et `[1, 8, 0, 0]`, `[3, 0, 0]`) dans `test_oracle.py`. Renforcement : « À relire ».
2. **`moteur/polynomes.py`** (déplacement verbatim, Q2 et point 6) : `Hors`, `racine_carree`, `racine_entiere_exacte`,
   `puissance_rationnelle_exacte`, `const`, `pnet`, `padd` (d'`exp_log`) ; `DEGRE_MAX`, `pmul_n`, `pq` (d'`exp_log_m`). Réexport sous les
   noms privés d'avant (`exp_log._Hors is polynomes.Hors`, etc.) ; `exp_log_m` garde ses imports depuis `exp_log` et prend `_pq`,
   `_pmul_n`, `DEGRE_MAX` de la brique. Manifeste d'EL : `moteur/polynomes.py` avant `exp_log.py`. `noyau` : + `squarefree`, `racine_q`.
   `architecture.md` § 5 : ligne « 4 copies de k√m/d » (chantier « nombres partout »).
3. **`moteur/second_degre.py`** (Python pur, sans texte) : `Polynome`, `HorsBornes`, `vers_polynome` (bornes § 13.5), `Nombre`
   (p + q√m, sur `noyau.racine_q`), `mise_en_evidence`, `identite`, `essais_sp` (12 lignes affichées au plus, point 5),
   `diviseurs_signes`, `racine_entiere_unique` (décidée par Δ), `racines_formule`, `s_applique`, `calculer`, `chemin` (D28),
   `produit_nul`, `redevelopper`, `verifier_solution`, `approx_garantie`.
4. **Tests** : `test_polynomes.py` (réexports `assertIs`, aucun nom privé importé de la brique, identité de `pq` sur les saisies d'EL) ;
   `test_second_degre.py` (corpus § 8 développé : chemin et S exacts, oracle ; polynômes générés à graine fixe ; garde-fou avec une
   multiplication réécrite dans le test ; `s_applique` ⇒ `calculer` se redéveloppe, S = ∅ par l'oracle ; D28 et l'exception nommée
   « S-P de plus de 12 lignes » ; valeurs ≈ du § 8 ; bornes ; chaque test < 10 s).
5. **Arêtes** : `polynomes -> expr`, `exp_log -> polynomes`, `exp_log_m -> polynomes`, `second_degre -> polynomes`, `-> noyau`, `-> nombres`.
6. Suite complète, dump identique, temps natif de `chemin` sur le corpus § 8, commit.

### Réalisé

- **Oracle** : `racines` retire les termes constants nuls avant tout calcul (racine 0, multiplicité = nombre de termes retirés), Sturm
  et contre-vérification sur le quotient ; `[7, -19, 0]` donnait « racine de multiplicité 1 non confirmée » (la contre-vérification
  relative à Σ|aᵢ||r|ⁱ ne peut pas conclure en r = 0). Test `test_racine_nulle_retiree_d_abord` (7x² − 19x, 3x², 2x³, x(x² + 1),
  x³ − x, x²(x − 2)²).
- **`moteur/polynomes.py`** : les dix noms, recopiés à l'identique (seuls les noms internes perdent leur « _ ») ; `exp_log.py`
  (`from polynomes import Hors as _Hors, …`) et `exp_log_m.py` (`from polynomes import DEGRE_MAX, pmul_n as _pmul_n, pq as _pq`) ;
  `exp_log_m` garde ses autres imports d'`exp_log` (mêmes objets). Manifeste d'EL : `moteur/polynomes.py` avant `exp_log.py`
  (`test_manifeste_minimal` le réclame). `noyau` : `squarefree`, `racine_q`.
- **`moteur/second_degre.py`** (≈ 690 lignes, sans texte) : tout le tableau du plan. Précisions prises :
  - `Polynome` est un `tuple` (sous-classe) de Fraction ; les facteurs sont des tuples de `Nombre` (Q(√m)) ;
  - `vers_polynome` : autre lettre → ValueError (pq prend toute lettre pour l'inconnue) ; `polynomes.Hors` → `HorsBornes` (point 6) ;
  - `Nombre` : écriture unique (m sans facteur carré), `signe` exact, `comparer` entre radicandes différents par encadrements,
    `forme_reduite` (A, B, m, d), `encadrement` par `isqrt` ; `BORNE_RADICANDE` = 10¹² (question 9 de suivi.md) ;
  - `essais_sp` s'arrête à la 13e ligne (« trop ») ; `s_applique("SP")` décide l'existence du couple par Δ (point 5 : vrai même
    au-delà de 12 lignes) ;
  - `chemin` : étapes `{methode, cible, aboutit, resultat}`, tentatives en échec comprises (S-P en échec ou « trop », tâtonnement en
    échec), un trinôme résolu par la formule reste un facteur entier (E9) ; méthode « ME_PUISSANCE » et `ORDRE_PAR_LA_FORMULE` pour
    la variante E12 (étape notée « ME ») ; garde-fou (étapes, facteurs finals, solutions) → « ne_conclut_pas » ;
  - `produit_nul(facteurs, formules=None)` reprend la formule déjà calculée par le chemin (une seule simplification de √Δ).
- **Tests** : `test_polynomes.py` (6 tests : réexports `assertIs`, définitions absentes d'EL, noms publics, `pq` sur 251 sous-arbres
  du corpus d'EL contre un évaluateur exact écrit dans le test) ; `test_second_degre.py` (33 tests : corpus § 8 développé et § 6/§ 7,
  69 entrées, chemin et S exacts, oracle ; 240 polynômes générés, graine 20261105 ; garde-fou par un produit dans Q(√m) réécrit dans
  le test, et deux calculs faussés exprès → « ne_conclut_pas » ; `s_applique` ⇔ `calculer` pour les 9 méthodes ; S-P et tâtonnement
  confrontés aux racines entières de l'oracle ; D28 avec l'exception nommée (x² + 55 453x + 720 720 : couple à la 13e ligne) ;
  valeurs ≈ du § 8 dont x² + 1000x − 1 ; bornes ; le plus lent : 0,3 s). `tests/lancer.py liste` les voit sans modification.
- **Arêtes** (`test_imports.ARETES`) : `polynomes -> expr`, `exp_log -> polynomes`, `exp_log_m -> polynomes`,
  `second_degre -> polynomes`, `-> noyau`, `-> nombres`, et **`second_degre -> expr`** (en plus de la liste du plan : `variables`,
  pour refuser une autre lettre ; prévue en P2b de toute façon).
- **Docs** : `architecture.md` § 1 (polynomes, second_degre) et § 5 (dette « 4 copies de k√m/d », chantier « nombres partout »).

### Suite d'avant commit et dump

- `PROCESSUS_PAGES=4 python3 tests/lancer.py complet --rapport S/rapports/P1` : **code 0**, 23 h 29 → 23 h 36 (6 min 44 de mur).
  Python 1 534 collectés, 1 533 passés + 1 xfail, 112 356 sous-tests, 90,0 s ; pages 145 passés, 2 421 sous-tests, 311,0 s.
  Aucun échec instable.
- `comparer_listes.py tests/reference S/rapports/P1` : 40 tests Python nouveaux (33 de `test_second_degre`, 6 de `test_polynomes`,
  1 de `test_oracle`), aucun disparu ; pages identiques nom par nom. Sous-tests : une baisse, justifiée dans suivi.md
  (`test_exp_log::TestVouvoiement::test_aucun_texte_du_fichier_ne_tutoie` 960 → 957, littéraux déplacés dans `polynomes.py`) ; hausses :
  `test_imports::test_liste_bien_formee` 95 → 109, `test_manifeste::test_manifeste_minimal` 36 → 37, `test_noyau::…memes_objets`
  58 → 60, `test_vocabulaire::test_litteraux_des_moteurs` 8 812 → 9 012, gardes de memo (+1 ou +2 chacune).
- **Dump** : `dump_sorties.py S/dumps/P1 --processus 6` (17 fichiers, 4 148 sorties, 4 s), `diff -r --exclude=temps S/dumps/depart
  S/dumps/P1` : **code 0, aucune sortie** (invariant tenu ; Exp-log identique à l'octet après le déplacement).
- xfail stricts ajoutés : aucun.

## P2a — affichage commun

### Plan

1. **`moteur/sortie.py`** : bloc `tableau_essais` = `{groupes: [{titre, colonnes}], lignes: [{cases, ok?}]}` (`BLOCS` : `({"groupes",
   "lignes"}, set())`) ; constructeur `tableau_essais(groupes, lignes, ok=None)` (`groupes` : couples (titre, nombre de colonnes),
   titre en texte avec le TeX entre `\(` `\)` ; `lignes` : listes de cases TeX ; `ok` : indice de la ligne qui aboutit, ou None pour un
   échec) ; `_valider_essais` (titres et cases sans HTML, A4 ; `colonnes` entier ≥ 1 ; chaque ligne a autant de cases que la somme des
   colonnes ; `ok` vaut true ; au plus une ligne ok) ; `BLOCS_DANS_CHAINE += ("tableau_essais",)` ; docstring de `resultat_lim`
   élargie (« résultat encadré », point 1) ; docstring du module.
2. **`commun/rendu.js`** : `BLOCS.tableau_essais` (`.essais > table`, en-tête `th colspan` par groupe, filet `.groupe` au début de
   chaque groupe sauf le premier ; si une ligne est ok, une colonne `.coche` de plus, ✓ seulement sur la ligne ok, `tr.ok`) ; titres
   échappés (`echapper`, comme les rangées), cases par `K()`. Aucun autre bloc touché.
3. **`commun/composants.css`** : `.essais` (défile seul s'il est trop large, nombres à droite, filets `--border`) ; `tr.ok` : bordure
   `--good`, fond `--ok-soft` ; D29 : `.katex .fbox{border-color:var(--good);background:var(--ok-soft)}` (spécificité 0,2,0 > `.katex *`
   0,1,0). Vérifié avant : aucune page, aucun moteur, aucun instantané ni référence de page n'écrit `\fbox` ni `\boxed` (seuls les docs du
   chantier) : le sélecteur général ne change aucun rendu existant.
4. **`moteur/chaine.py`** : `bloc_rangees(rangees, membre_gauche=False)` sorti de `bloc_chaine` (`bloc_chaine = bloc_rangees(
   rangees_chaine(…), membre_gauche)`), généralisé sans effet sur `bloc_chaine` : le membre de gauche est la première rangée-ligne
   (pas forcément la première rangée : des lignes pleine largeur peuvent la précéder, phrase de choix et tableau d'abord, § 13.3), et
   seulement si elle n'a ni lien ni propriété. Option `coupure_ou=False` de `tex_element`, passée par `rangees_chaine` et `bloc_chaine` :
   chaque membre d'un « ou » entre accolades (insécable) et `\allowbreak` après « ou ». **Écart au plan** : pas d'option `coupure_ou`
   dans `bloc_rangees`, qui reçoit des rangées déjà écrites en TeX (l'option se donne à `rangees_chaine`).
5. **Tests** : `test_sortie` (constructeur, `BLOCS_DANS_CHAINE`, conforme dans une chaîne et dans une carte, refus) ; `test_chaine`
   (`bloc_chaine == bloc_rangees(rangees_chaine)` sur toutes les chaînes du fichier et d'Exp-log ; option désactivée = même TeX ;
   activée ; membre de gauche après des lignes pleines en tête) ; `test_composants` (`.essais`, `tr.ok`, `.katex .fbox`, rendu.js) ;
   nouveau `tests/pages/test_tableau_essais.py` (page de l'ED) : 2.10 a, S-P en échec (x² + 4x − 1), x² + 4, étiquette « avec ⟦A = 4z,
   B = 9⟧ », produit nul à 3 facteurs (2.11 h) ; tableaux tirés de `second_degre.essais_sp`, nombres par `nombres.exact` ;
   320–1100 px clair et sombre ; bordures calculées = `--good` ; rien ne déborde ; coupure seulement après « ou ».
6. Captures 390 px (clair, sombre) → `S/captures/P2a/` ; suite complète, dump, temps natif, commit.

### Réalisé

- **`sortie.py`** : `BLOCS["tableau_essais"]`, `GROUPE_ESSAIS`, `LIGNE_ESSAIS`, `tableau_essais(groupes, lignes, ok=None)` (`ok` hors
  des indices, booléen ou non entier → ValueError), `_valider_essais`, `BLOCS_DANS_CHAINE` + `"tableau_essais"` ; docstrings du module
  et de `resultat_lim` (« résultat encadré » : limite, ou S d'une équation dans une carte normale).
- **`rendu.js`** : `rendreEssais` et `BLOCS.tableau_essais` ; titres échappés (`echapper`), cases par `K()`, `colspan` = colonnes du
  groupe (+ 1 sur le dernier groupe s'il y a une colonne ✓) ; aucun autre bloc touché.
- **`composants.css`** : `.essais` (bordures séparées, transparentes sauf l'en-tête, le filet `.groupe` et la ligne ok), `tr.ok`
  (bordure `--good` sur le pourtour, fond `--ok-soft`), `.coche` ; D29 `.katex .fbox{border-color:var(--good)}`.
  **Piège trouvé à la capture** : dans le HTML de KaTeX 0.16.11, le span du cadre de `\fbox` vient **après** le contenu (pour
  `\colorbox`, avant) ; un fond sur `.fbox` cachait la valeur (cadres vides sur la 1re capture). Correction, sans toucher une règle
  existante : `@supports selector(:has(+ *)) { .katex .fbox{background:var(--ok-soft)} .katex .vlist>span:has(+ span>.fbox){z-index:1} }`
  (le contenu passe au-dessus du cadre) ; sans `:has`, cadre vert sans fond, valeur visible (question 12 de suivi.md). Le test de pages
  vérifie au centre de chaque valeur encadrée (`elementFromPoint`) que l'élément du dessus est la valeur ; contre-épreuve : la règle
  `z-index` retirée, les 5 valeurs sont signalées cachées.
- **`\fbox` ailleurs** : `grep` de `fbox`, `boxed`, `colorbox`, `boxpad` dans tout le dépôt (hors copies de KaTeX et de Pyodide) : seuls
  les docs du chantier. Le sélecteur général ne change donc aucun rendu existant (pas de limitation à `.chaine`).
- **`chaine.py`** : `bloc_rangees(rangees, membre_gauche=False)` (dans `__all__`) ; `bloc_chaine` = `bloc_rangees(rangees_chaine(…))` ;
  membre de gauche = la première rangée-ligne, seulement sans lien ni propriété (dans `bloc_chaine`, c'est toujours la première
  rangée, sans lien : même résultat) ; `coupure_ou` dans `tex_element`, `rangees_chaine`, `bloc_chaine` (pas dans `bloc_rangees`,
  écart noté au plan). Rendu mesuré : sans l'option, KaTeX coupe aussi après chaque « = » (7 morceaux pour Az 4.1 d) ; avec, 3 morceaux,
  un par équation.
- **Tests** : `test_sortie.TestTableauEssais` (7 tests) + l. 165 et 169 ; `test_chaine.TestBlocRangees` (6 tests, dont
  `bloc_chaine == bloc_rangees(rangees_chaine)` pour les 16 combinaisons d'options sur 6 chaînes et celles d'Exp-log) ;
  `test_composants.test_tableau_essais_et_valeur_encadree` ; `tests/pages/test_tableau_essais.py` (6 tests ; contre-épreuves faites à
  part : sans `coupure_ou`, sans la règle `.fbox`, sans la règle `z-index`, chacune détectée).
- **Captures** (`S/tmp/p2a_essai.py`, cartes seules) : `S/captures/P2a/cartes-390-clair.png`, `cartes-390-sombre.png`,
  `cartes-320-clair.png`. Les cartes sont écrites à la main dans le test (illustration de l'affichage commun, pas la rédaction de P2b :
  par exemple « 2(x + 4) · (2x − 7) », écrit par `expr.tex`).
- Aucun instantané, aucune référence de page, aucune sortie existante modifiés. xfail stricts ajoutés : aucun. Arête d'import nouvelle :
  aucune (le test de pages importe `second_degre` et `nombres` ; les tests ne sont pas dans le graphe).

### Suite d'avant commit et dump

- `PROCESSUS_PAGES=4 python3 tests/lancer.py complet --rapport S/rapports/P2a` : **code 0**, 23 h 57 → 00 h 04 (≈ 7 min de mur).
  Python 1 548 collectés, 1 547 passés + 1 xfail, 112 699 sous-tests, 93,2 s ; pages 151 passés, 2 435 sous-tests, 327,9 s. Aucun
  échec instable.
- `comparer_listes.py tests/reference S/rapports/P2a` : par rapport à P1, 14 tests Python nouveaux (7 `test_sortie.TestTableauEssais`,
  6 `test_chaine.TestBlocRangees`, 1 `test_composants`) et 6 tests de pages (`test_tableau_essais`) ; aucun disparu. Sous-tests : seule
  baisse, celle de P1 déjà justifiée (`test_exp_log::…::test_aucun_texte_du_fichier_ne_tutoie` 960 → 957) ; hausses :
  `test_composants` (49 → 62, 9 → 11), `test_sortie::TestBlocChaine::test_conforme` 3 → 4, `test_vocabulaire::test_litteraux_des_moteurs`
  9 012 → 9 058.
- **Dump** : `dump_sorties.py S/dumps/P2a --processus 6` (17 fichiers, 4 148 sorties, 4 s), `diff -r --exclude=temps S/dumps/depart
  S/dumps/P2a` : **code 0, aucune sortie** (invariant tenu).
- xfail stricts ajoutés : aucun.

## P2b — rédaction dans `second_degre`

### Plan

1. **Entrée de P2b** : `resoudre_equation(gauche, droite, inconnue, decimaux_enonce=False, methodes=ORDRE_DU_COURS)` n'accepte encore
   que « P = 0 » **développée et ordonnée** (somme de monômes k·xʲ, degrés strictement décroissants, droite = 0) et de degré 2 ; tout
   le reste donne le statut **`non_traite`** (message clair, aucune étape) : ramener et développer (P3), formes structurées (P4a),
   degrés ≠ 2, identité, égalité fausse (P4b). Les tests de ces cas sont des xfail stricts nommés « P3 », « P4a », « P4b ».
2. **Rédaction** sur le calcul de P1 (`chemin`, `produit_nul`, `essais_sp`, `racines_formule`), sans nouveau calcul : un constructeur
   de rangées (`_Redaction`) écrit chaque étape comme un segment `Chaine([pivot, …])` dont le premier lien est ⇔ (énoncé écrit au
   premier ⇔ seulement, § 13.3), les phrases et le tableau en `LigneTexte`, les lignes de Δ, √Δ, x₁, x₂ en rangées sans lien
   (point 3). E3 (phrases de a < 0), E4, E5 (étiquette ou ligne de vérification, D24), E6 (tableau, D3, § 13.5 « trop de couples »),
   E7 (r, △, diviseurs en une ligne, D1), E8 (D7, D20), E9, E10 (§ 7 : Δ écrit une fois, valeur finale encadrée), E11, E12 (variante
   « formule », a < 0 : x₁ avec −√Δ), E14 (`nb_exact` sans état, `nombres.exact`, `approx_garantie`, « soit … ≈ … »), D29 (`\fbox`
   sur A et B en un seul cadre comme D29 l'écrit, r, △, Δ ; ligne ✓ par le bloc), S en `resultat_lim`.
3. **API** : `Resolution` (§ 5, plus `message` pour un statut non résolu), `Etape` (§ 5, plus `segment`), `appliquer(methode, P)`,
   `blocs(resolution)` (chaîne par `bloc_rangees(…, membre_gauche=True)`, S, ligne ≈), `nb_exact`, `arbre_polynome`, `arbre_nombre`.
   Arêtes `second_degre -> chaine`, `-> sortie`.
4. **Tests** : `tests/python/corpus_second_degre.py` (entrées), `test_redaction_second_degre.py` (invariants JSON et repliement des
   segments, oracle, garde-fou, `appliquer`, R12 et vocabulaire, cas limites du § 6, `nb_exact` croisé avec `exp_log._nb_exact`,
   xfail stricts), `test_instantanes_second_degre.py` (JSON `tests/python/donnees/equations-2e-degre/instantanes.json`, JSON strict,
   vocabulaire). `lancer.py liste` contrôlé.
5. Texte rendu de 2.11 h développé ci-dessous ; suite complète, dump, temps natif, commit.

### Réalisé

- **`moteur/second_degre.py`, section 7** (≈ 600 lignes, sur le calcul de P1, aucun calcul nouveau) :
  - `resoudre_equation(gauche, droite, inconnue, decimaux_enonce=False, methodes=ORDRE_DU_COURS) -> Resolution` ; `Resolution` =
    `{statut, etapes, solutions, S, approx, variantes, message}`. **Précisions au § 5** : deux statuts de plus, `non_traite`
    (« Cette forme d'équation n'est pas encore traitée par l'outil. », temporaire : disparaît quand P3, P4a et P4b sont faites) et
    `hors_bornes` (message du § 13.5 ; radicande > 10¹², question 9) ; `message` (texte du statut, None si résolu) ; `Etape` a en plus
    `segment` (sa `Chaine`, ou None quand l'étape n'écrit aucun ⇔). `pas_encore` (fraction, racine, bicarrée) reste pour P3 et P4b.
  - Entrée de P2b : `termes_developpes(arbre, x)` (somme de monômes k·xʲ écrits, degrés strictement décroissants, sans coefficient
    nul) et droite = 0, degré 2 ; sinon `non_traite`. L'énoncé est écrit tel que saisi (décimaux de la saisie gardés, E14).
  - Étapes : `factoriser` (ME, IDREM_*, SP, TATONNEMENT, FORMULE choisie d'emblée), `produit_nul`, puis `delta_valeur` (ligne de Δ) et
    `delta_nombre` (Δ > 0, x₁, x₂ ; ou Δ = 0 ; ou Δ < 0) pour la formule (phases de quiz.md QZ-04). Une tentative en échec (S-P,
    tâtonnement) est l'étape `factoriser` de la méthode du cours (ses lignes : phrase, tableau ou diviseurs, « on utilise la
    formule ») ; E9 : la ligne ⇔ x = … finale appartient à l'étape `delta_nombre`.
  - Disposition (§ 13.3) : chaque étape est un segment `Chaine([pivot, …])` (premier lien ⇔, tous ⇔) ; l'énoncé n'est écrit qu'au
    premier ⇔ ; phrases et tableau en `LigneTexte` ; lignes de Δ, √Δ, x₁, x₂ en rangées sans lien (`SansLien` dans le segment,
    rendues ("", tex, None) par `rangees`, point 3). `blocs(res)` = `bloc_rangees(concaténation, membre_gauche=True)`, `resultat_lim(S)`,
    `texte(« soit … »)`.
  - Rédaction : E3 (a < 0 : « Le trinôme n'est pas unitaire (a = −1) » si a = −1, sinon « Le coefficient de x² est négatif (a = …) »,
    avec le facteur mis en évidence, −x compris) ; E4 ; E5 (A² − B² en étiquette, A² ± 2AB + B² par la ligne « Vérification … ✓ »,
    puis le carré et D24) ; E6 (tableau par `sortie.tableau_essais`, D3, § 13.5) ; E7 (calcul « 2 · (−4)² − 4 − 28 », b · r direct si
    b = ±1 ; échec : une ligne, chaque ±d dans son propre `\(…\)` pour que la ligne passe à la ligne) ; E8 (D7, D14, D20, D24) ; E9 ;
    E10 (§ 7, Δ = b² − 4ac = subst. = b² ± 4ac = ⟦Δ⟧, sans le calcul intermédiaire quand b = 0, « 0 − 16 ») ; E11 (`arbre_nombre`,
    une seule fraction réduite) ; E12 (variante sans phrase de choix ; proposée seulement si le chemin du cours n'a pas de formule **et**
    si la variante en a une : pas pour 3x² − 12x) ; E14 (`nb_exact` sans état, `approx_garantie`, x₁/x₂ nommés si toutes les solutions
    le sont, sinon x et « ou ») ; D29 (`\fbox{$…$}` : A et B dans un seul cadre, comme D29 l'écrit, question 13 ; r ; △ ; valeur
    finale de Δ ; jamais la vérification, les calculs ni les étiquettes).
  - Garde-fou d'écriture : chaque valeur écrite est recalculée (ligne ✓ = facteurs du S-P, r annule le trinôme, (−r)·△ = c, Δ, x₁ et
    x₂ par la formule) ; un écart lève `_Incoherent` → `ne_conclut_pas` (jamais un résultat douteux). Aucun cas du corpus ni des
    polynômes générés ne le déclenche.
  - `appliquer(methode, P)` : l'étape de la méthode seule (sans phrase de choix, P = 0 en tête dès qu'un ⇔ est écrit), ou None ; la
    formule donne toutes ses lignes dans une seule étape ; le S-P de plus de 12 lignes, la phrase du § 13.5 (pas de tableau).
  - `PHRASE_IDENTITE` et `PHRASE_EGALITE_FAUSSE` (celles d'Exp-log, test qui les cherche dans exp_log.py) sont prêtes pour P4b :
    l'identité ne peut pas encore se produire en P2b (degré 0 → `non_traite`). **Écart au plan** : « identité selon Exp-log » est
    préparée, pas branchée (option qui affiche le moins : sans ⇔ avant elle, le bloc « chaine » n'aurait aucune rangée-ligne et serait
    refusé par `sortie.valider`).
- **Tests** :
  - `tests/python/corpus_second_degre.py` : `P2B` (72 équations : § 8 développé, § 6, § 7, § 13.4–13.5, décimaux, a < 0, Δ = 0) et
    `A_VENIR` (21 formes, partie et coefficients développés).
  - `tests/python/test_redaction_second_degre.py` (32 tests + 22 xfail stricts) : invariants (JSON du bloc = `bloc_rangees` de la
    concaténation ; repliement des segments = `rangees_chaine` de la chaîne entière ; pivots enchaînés, liens ⇔, énoncé une fois et
    seulement si un ⇔ suit) sur le corpus, les variantes et les 196 polynômes générés de degré 2 de P1 (décimaux de l'énoncé pour un
    tiers) ; oracle et substitution exacte (écrite dans le test) ; valeurs ≈ contre mpmath ; textes rendus (2.11 h, 2.10 a, Javet
    2.17 c, x² + 4x − 1, 2.12 b, Javet 2.17 d, x² + 4, −6x² + 12x − 6, 2.10 e, 2.9 b, 2.9 h, 25x² − 3, 2.9 d, x² − 8, x² − 1/2,
    monômes, Javet 2.17 e, Δ = 0, décimaux, S-P de plus de 12 lignes, E14, variante dont a < 0) ; D29 ; R12 et C6 sur tous les
    textes ; `nb_exact` croisé avec `exp_log._nb_exact` (sous `_avec_decimaux`, sans toucher à l'état) et `nombres.exact` ;
    `appliquer` ⇔ `s_applique` pour les 9 méthodes, redéveloppement ; `non_traite`, `hors_bornes`. xfail stricts : 10 « P3 »,
    5 « P4a », 7 « P4b » (dont la bicarrée).
  - `tests/python/test_instantanes_second_degre.py` (4 tests) et `tests/python/donnees/equations-2e-degre/instantanes.json` (72
    entrées, variante « formule » comprise) : `normaliser` de `test_instantanes`, JSON strict, `sortie.valider`, vocabulaire et R12.
  - `python3 tests/lancer.py liste` : `rapide` relance `test_instantanes_second_degre.py` quand le JSON change (il nomme `donnees`)
    et quand `second_degre.py` change (import) ; vérifié aussi par `tests_python_concernes` sur chacun des deux fichiers seul.
- **Arêtes** (`test_imports.ARETES`) : `second_degre -> chaine`, `second_degre -> sortie` (`second_degre -> expr` existe depuis P1).
- Aucun fichier partagé modifié (`chaine.py`, `sortie.py`, `rendu.js`, CSS intacts) : aucun instantané existant ni aucune référence de
  page ne change.

### Texte rendu de 2.11 h (forme développée), comparé au § 7

Rangées du bloc « chaine » (`blocs`, JSON ; `gauche` : le membre de gauche de la première ligne), puis S :

    gauche 4x^{2} + 2x - 56 = 0   \iff  2(2x^{2} + x - 28) = 0                                         ME
    texte  Le trinôme \(2x^{2} + x - 28\) n'est pas unitaire : tâtonnement.
    texte  \(\fbox{$x = -4$}\) est solution de \(2x^{2} + x - 28 = 0\), car \(2 \cdot (-4)^{2} - 4 - 28 = 32 - 4 - 28 = 0\).
    texte  Donc \(2x^{2} + x - 28 = (x + 4)(2x + \triangle)\) avec \(4 \cdot \triangle = -28\), donc \(\fbox{$\triangle = -7$}\).
           \iff  2(x + 4)(2x - 7) = 0
           \iff  {\underbrace{2 = 0}_{\text{impossible}}} \text{ ou } \allowbreak {x + 4 = 0} \text{ ou } \allowbreak {2x - 7 = 0}
                                                                                                       produit nul
           \iff  {x = -4} \text{ ou } \allowbreak {x = \frac{7}{2}}
    resultat_lim  S = \{-4\,;\,\frac{7}{2}\}

Étapes : factoriser (ME, cible 4x² + 2x − 56) · factoriser (TATONNEMENT, cible 2x² + x − 28, r = −4, △ = −7) · produit_nul.
**Comparaison au § 7** : mêmes lignes, dans le même ordre, à partir de « 4x² + 2x − 56 = 0 » ; la ligne « 4x² + 2x = 56 ⇔ » et l'étape
« ramener » viennent en P3. Écarts voulus : étiquette « produit nul » (D5) ; x = −4 et △ = −7 encadrés (D29). Les parenthèses de la ME
sont ordinaires (le corrigé les agrandit : rendu seulement).

### Suite d'avant commit et dump

- `PROCESSUS_PAGES=4 python3 tests/lancer.py complet --rapport S/rapports/P2b` : **code 0** (≈ 7 min de mur). Python 1 607 collectés,
  1 584 passés + 23 xfail (1 d'avant + 22 stricts de P2b), 122 989 sous-tests, 92,4 s ; pages 151 passés, 2 435 sous-tests, 329,0 s.
  Aucun échec instable.
- `comparer_listes.py tests/reference S/rapports/P2b` : par rapport à P2a, 59 tests Python nouveaux (33 passés et 22 xfail stricts de
  `test_redaction_second_degre`, 4 de `test_instantanes_second_degre`), aucun disparu ; pages identiques à P2a. Sous-tests : seule
  baisse, celle de P1 déjà justifiée (960 → 957) ; hausses : `test_imports::test_liste_bien_formee` 109 → 113,
  `test_vocabulaire::test_litteraux_des_moteurs` 9 058 → 9 447, gardes de memo (+1 chacune).
- **Dump** : `dump_sorties.py S/dumps/P2b --processus 6` (17 fichiers, 4 148 sorties, 4 s), `diff -r --exclude=temps S/dumps/depart
  S/dumps/P2b` : **code 0, aucune sortie** (invariant tenu).
- xfail stricts ajoutés : 22 (10 « P3 », 5 « P4a », 7 « P4b »), dans `test_redaction_second_degre.py` (`test_a_venir[…]`,
  `test_P4b_bicarree`).

### Temps

Voir « Temps » ci-dessous (P2b).

## P3 — saisie

### Plan

1. **`moteur/expr.py`** : `a_des_decimaux(n)` déplacé verbatim d'`exp_log._a_des_decimaux` (docstring comprise), réexporté par
   `exp_log` sous l'ancien nom (`from expr import a_des_decimaux as _a_des_decimaux`) ; `test_expr.DEPLACES` + la paire (`assertIs`).
   Dump d'EL identique. Baisse attendue de 1 littéral dans `test_exp_log::TestVouvoiement` (docstring partie), justifiée dans suivi.md.
2. **`second_degre`, E1 et E2** (section 7, sur `vers_polynome`, aucun calcul nouveau des méthodes) :
   - lecture de chaque membre en termes signés : monômes écrits (`_monome_ecrit`), parenthèse précédée de « − » (gardée jusqu'à la
     ligne qui l'enlève ; précédée de « + », elle s'écrit sans parenthèses), produit à développer : nombre ou monôme × parenthèse
     (« distribution »), deux parenthèses sans autre facteur (« double distribution », tous les produits partiels), carré d'un binôme
     écrit A ± B, A non négatif (« Id. rem. (A ± B)² avec A = …, B = … », développé en A² ± 2AB + B²) ; toute autre forme : `non_traite`
     (option qui affiche le moins) ;
   - lignes, chacune seulement si elle change quelque chose : (1) développement (étiquettes séparées par « ; », sans doublon ; un
     produit précédé de « − » s'écrit développé entre parenthèses), (2) parenthèses enlevées, (3) réduction de chaque membre (termes
     de même degré ou coefficient nul), (4) E1.2 : tout du côté où le coefficient de tête est positif (à gauche s'il l'est des deux
     côtés), ordre décroissant ; second membre nul : seulement réordonner (E1.1, a < 0 gardé) ;
   - étapes (§ 5) : (1)–(3) phase « ramener », méthode « DEVELOPPER » ; (4) phase « ramener », méthode « RAMENER » (avec (3) s'il
     n'y a rien à développer) ; une ligne **seulement réordonnée** appartient à l'étape qui suit (`_Redaction` : ligne d'en-tête de
     l'étape suivante) ;
   - phrase « On ramène d'abord l'équation à la forme \(\ldots = 0\) : » en tête de la première étape « ramener », seulement si une
     phrase de choix (E4 : S-P, tâtonnement, formule d'emblée) suit directement, sur le chemin du cours ;
   - garde-fou : chaque ligne écrite est relue par `vers_polynome` (membres inchangés pour (1)–(3), P ou −P pour (4)) ; un écart lève
     `_Incoherent` (`ne_conclut_pas`) ;
   - **structures de P4a laissées en `non_traite`** (E1.3, « si une structure s'applique, sans développer ») : produit ou puissance
     égal à 0 (produit nul direct) ; facteur non monôme commun aux deux membres (proportionnel) ; un seul carré de binôme k(B)² avec
     des constantes de signe opposé (ou nulles), ou deux carrés de signes opposés sans constante (Id. rem. structurée). Tout le reste
     se développe ;
   - après E1/E2 : degré ≠ 2 (identité, degré 1, degré ≥ 3) reste `non_traite` (P4b), sans étape.
3. **`equations-2e-degre/equations.py`** (nouveau dossier, sans page, hors du manifeste et du registre jusqu'en P5) : `LEXIQUE_EQ`
   (fonctions=("sqrt",), message_vide « Écrivez une équation. », message_exposant avec l'exemple x^2) ; `analyser(texte)` →
   `(gauche, droite, inconnue, decimaux_enonce)` ou `ErreurSaisie`, dans l'ordre du § 13.5 (vide, syntaxe, pas de « = », aucune lettre,
   plusieurs lettres, inconnue en exposant, inconnue sous √ / au dénominateur / exposant non entier ou négatif, √ sans l'inconnue,
   division par 0, bornes par `second_degre.vers_polynome`) ; D23. Constantes évaluées par `polynomes.const` (arête de plus que le plan,
   `equations -> polynomes`, à déclarer en P5 avec les autres ; `test_imports` ne lit pas encore ce dossier, vérifié).
4. **Tests** : `tests/python/test_equations_saisie.py` (chargé par chemin : chaque message, ordre de priorité sur des saisies mixtes,
   notation suisse, décimaux de l'énoncé, (x + 1)(x + 3) = 15, Az 4.1 g, e^x = 2 ; R12 sur les messages ; puis la résolution des saisies
   lues) ; `corpus_second_degre.P3` (énoncés à ramener ou à développer : les 10 de `A_VENIR` marqués P3 et d'autres formes) ;
   `test_redaction_second_degre` : marque xfail retirée des 10 « P3 » (`PARTIES_FAITES`), invariants, oracle et textes rendus sur `P3`
   (2.11 h complet, 2.10 h, 2.10 j, (x + 1)(x + 3) = 15, réordonner, « − (…) ») ; `non_traite` contrôlé sur les formes de P4a/P4b et
   sur les structures de P4a ; instantanés : `P2B` + `P3` (entrées ajoutées, aucune modifiée).
5. Contrôles : `lancer.py liste` (le nouveau dossier), énumérations de dossiers des tests (`test_accueil`, `test_manifeste`,
   `test_outils_du_site`, `test_noyau`, `test_imports`, `test_vocabulaire`, `test_memo_garde` : tous lisent le registre, le manifeste
   ou les dossiers à `index.html`) ; suite complète, dump, temps natif, commit.

### Réalisé

- **`moteur/expr.py`** : `a_des_decimaux` (verbatim, docstring comprise) ; `exp_log` le réexporte (`from expr import …,
  a_des_decimaux as _a_des_decimaux`, docstring du module complétée) ; `test_expr.DEPLACES` + la paire (`assertIs`). Exp-log :
  dump identique à l'octet.
- **`moteur/second_degre.py`**, section 7 (« E1 et E2 », ≈ 290 lignes, aucun calcul nouveau des méthodes) :
  - `ramener(gauche, droite, inconnue, decimaux_enonce)` → `{P, pas: [(méthode, parametres, [(Eq, étiquette)])], en_tete}` ou
    None ; `forme_structuree(gauche, droite, inconnue)` (E1.3) ; `PHRASE_RAMENER` ; `_Redaction.en_tete` (ligne seulement
    réordonnée, posée en tête de l'étape suivante) ; `_ecrire_ramener` ; `resoudre_equation` passe par `ramener` (les deux membres
    contrôlés pour une autre lettre, pas seulement la gauche) ; `_rediger(…, prep)`.
  - Lecture d'un membre en termes signés (`_termes_signes` : une somme précédée de « − » est un groupe, précédée de « + » elle se
    lit comme ses termes, ce que `expr.tex` écrit aussi) ; `_developper` : distribution (nombre ou monôme × une parenthèse, facteurs
    monômes multipliés, signe des `Neg` compris), double distribution (deux parenthèses sans autre facteur ; produits partiels dans
    l'ordre écrit : x² + 3x + x + 3), carré d'un binôme écrit A ± B (A sans signe, deux degrés différents ; « Id. rem. \((A - B)^{2}\)
    avec \(A = 2x,\ B = 1\) », A et B écrits comme saisis, sans cadre) ; tout le reste → None → `non_traite`.
  - Lignes : (1) développement (étiquettes « ; », sans doublon ; produit précédé de « − » écrit développé entre parenthèses),
    (2) parenthèses enlevées, (3) réduction de chaque membre (`arbre_polynome` des deux membres), (4) E1 (`arbre_polynome(P) = 0`).
    Chaque ligne n'est écrite que si elle change le TeX. Garde-fou : (1)–(3) relues par `vers_polynome` = membres d'origine, (4) = P ;
    sinon `_Incoherent` (test : une écriture faussée exprès donne « ne_conclut_pas »).
  - Côté (E1.2) : P = gauche − droite ; si le second membre n'est pas nul et que le coefficient de tête de P est négatif, −P
    (« droite ») ; second membre nul : P gardé, même avec a < 0 (E1.1 : la ME de −1 suit).
  - Étapes : (1)–(3) « ramener / DEVELOPPER » (`parametres` : `developpements`) ; (4) « ramener / RAMENER » (`cote`, `polynome`), avec
    (3) quand rien n'est développé (x² + x² = 8) ; (4) seulement réordonnée (second membre nul) : en tête de l'étape suivante (§ 5) ;
    la phrase d'E1 en tête de la première étape « ramener », si la première méthode est S-P, tâtonnement ou formule d'emblée, sur le
    chemin du cours.
  - Structures laissées à P4a (`forme_structuree`) : produit ou puissance (non monôme) égal à 0 ; facteur non monôme commun aux deux
    membres, proportionnel (`vers_polynome` de chaque facteur), si l'un des membres est un produit ou une puissance (2.12 e,
    (x − 1)(x + 2) = x − 1) ; termes (tout ramené d'un côté) faits d'un carré de binôme k(B)² et de constantes de signe opposé ou
    nulles, ou de deux carrés de signes opposés sans constante (2.9 k, 2.9 l, 2.12 h, (x + 1)² = (2x − 3)²). (x + 1)² = −16 se développe.
  - Après E1/E2, degré ≠ 2 → `non_traite` sans étape (Az 4.1 g : les lignes de développement existent, 1 = 1, identité en P4b).
- **`equations-2e-degre/equations.py`** (nouveau dossier, un seul fichier, pas d'`index.html`) : `LEXIQUE_EQ`, `MESSAGE_EXPOSANT`
  (« Mettez l'exposant entre parenthèses, ou séparez-le du facteur suivant avec * : x^2*(x+1). » : les erreurs d'exposant de la
  lecture sont x^-2, x^2x, x^2(x+1)), `MESSAGES_SAISIE` (§ 4, § 13.5), `ORDRE`, `analyser`. Problèmes lus dans l'arbre (`_problemes`) :
  inconnue dans un exposant ; sous √, dans un dénominateur, exposant (constant) non entier ou négatif sur une base qui contient
  l'inconnue ; √ sans l'inconnue, ou puissance d'un nombre d'exposant non entier (2^(1/2), 9^(1/2)) ; division par une constante nulle
  (aussi 0^(−1)) ; bornes : `vers_polynome` de chaque membre et de leur différence (`HorsBornes`). Constantes par `polynomes.const`.
- **Énumérations de dossiers** (vérifié à la lecture, puis par la suite) : `test_accueil` et `test_manifeste` ne voient que les
  dossiers à `index.html` ; `test_imports`, `test_noyau`, `test_vocabulaire`, `test_memo_garde`, `lancer.py` lisent les dossiers du
  manifeste (`outils_du_site.dossiers_moteurs`) : le nouveau dossier n'y est pas avant P5. Aucune arête déclarée en P3 (le graphe
  ne lit pas encore `equations.py` ; une arête déclarée sans être lue ferait échouer `test_aretes_figees`). **Arêtes à déclarer en
  P5** : `equations -> expr`, `-> noyau`, `-> second_degre` (plan) et **`equations -> polynomes`** (`const` : écart au plan, noté).
  `second_degre` : aucune arête nouvelle (`polynomes.const` passe par l'arête `second_degre -> polynomes` de P1).
- **`rapide`** : le test de la saisie est relancé quand il change, ou quand `second_degre`/`expr` changent (il les importe) ; pas
  quand `equations.py` seul change, tant que son dossier n'est pas au manifeste (P5 : le test l'importe par son nom, `import
  equations`, l'arête du graphe de `lancer.py` viendra avec le manifeste).
- **Tests** :
  - `corpus_second_degre` : `P3` (26 équations : les 10 « P3 » d'`A_VENIR` sous leur forme d'énoncé et 16 formes d'E1/E2),
    `RESOLUES = P2B + P3`, `PARTIES_FAITES = ("P3",)`.
  - `test_redaction_second_degre` : invariants, oracle, D29, R12 sur `RESOLUES` ; `polynome(saisie)` = gauche − droite ;
    `TestRamener` (10 tests : 2.11 h complet, phrase seulement avant une phrase de choix (liste exacte des 15 entrées), côté du
    coefficient de tête, ligne seulement réordonnée (étape suivante), (x + 1)(x + 3) = 15 du § 7, « − (…) », Id. rem. et
    distribution, Az 4.1 g (lignes du § 7), réduction et premier membre nul, chaque ligne relue + écriture faussée) ;
    `TestNonResolu` : `non_traite` vérifié sur les parties pas encore faites, `test_structures_laissees_a_p4a` (12 formes oui, 8 non),
    `test_hors_de_ce_que_e2_developpe` (10 formes) ; marque xfail retirée des 10 `test_a_venir[P3-…]` (mêmes noms de tests).
  - `test_instantanes_second_degre` : sur `RESOLUES` ; JSON régénéré : **26 entrées nouvelles, aucune des 72 de P2b modifiée**
    (comparaison JSON entrée par entrée ; le diff git ligne à ligne paraît plus gros à cause du tri des clés).
  - `tests/python/test_equations_saisie.py` (22 tests) : lexique ; chaque message (vide, syntaxe dont l'exposant, pas de « = »,
    aucune lettre, plusieurs lettres dont e^x = 2, exposant, prochaine version, racine, division par 0, bornes) ; ordre de priorité
    sur 13 saisies mixtes ; messages du § 4 mot pour mot ; R12 et C6 sur tous les littéraux d'`equations.py` ; inconnue saisie (D23) ;
    notation suisse ; décimaux de l'énoncé (et `exp_log._a_des_decimaux is expr.a_des_decimaux`) ; (x + 1)(x + 3) = 15 ; Az 4.1 g ;
    même lecture que le corpus pour les 98 saisies de `RESOLUES`, même S.

### Texte rendu de 2.11 h (à partir de « 4x² + 2x = 56 »), comparé au § 7

Rangées du bloc « chaine » (`equations.analyser("4x^2+2x=56")`, `resoudre_equation`, `blocs` ; `gauche` : le membre de gauche de la
première ligne), puis S :

    gauche 4x^{2} + 2x = 56   \iff  4x^{2} + 2x - 56 = 0
                              \iff  2(2x^{2} + x - 28) = 0                                          ME
    texte  Le trinôme \(2x^{2} + x - 28\) n'est pas unitaire : tâtonnement.
    texte  \(\fbox{$x = -4$}\) est solution de \(2x^{2} + x - 28 = 0\), car \(2 \cdot (-4)^{2} - 4 - 28 = 32 - 4 - 28 = 0\).
    texte  Donc \(2x^{2} + x - 28 = (x + 4)(2x + \triangle)\) avec \(4 \cdot \triangle = -28\), donc \(\fbox{$\triangle = -7$}\).
                              \iff  2(x + 4)(2x - 7) = 0
                              \iff  {\underbrace{2 = 0}_{\text{impossible}}} \text{ ou } \allowbreak {x + 4 = 0} \text{ ou } \allowbreak {2x - 7 = 0}
                                                                                                    produit nul
                              \iff  {x = -4} \text{ ou } \allowbreak {x = \frac{7}{2}}
    resultat_lim  S = \{-4\,;\,\frac{7}{2}\}

Étapes : ramener (RAMENER, cible 4x² + 2x = 56, côté gauche) · factoriser (ME, cible 4x² + 2x − 56) · factoriser (TATONNEMENT, cible
2x² + x − 28, r = −4, △ = −7) · produit_nul ; variante « formule » proposée.
**Comparaison au § 7** : mêmes lignes, dans le même ordre, et mêmes étapes que l'exemple cible (« ramener · factoriser (ME) ·
factoriser (TATONNEMENT) · produit_nul ») ; la ligne ramenée ouvre la chaîne sans phrase (une ME suit, E1). Écarts voulus : étiquette
« produit nul » (D5) ; x = −4 et △ = −7 encadrés (D29) ; parenthèses de la ME ordinaires (rendu seulement).

### Suite d'avant commit et dump

- `PROCESSUS_PAGES=4 python3 tests/lancer.py complet --rapport S/rapports/P3` : **code 0** (≈ 7 min de mur ; console
  `S/rapports/P3-console.log`). Python 1 641 collectés, 1 628 passés + 13 xfail (1 d'avant + 12 stricts P4a/P4b), 124 615 sous-tests,
  88,6 s ; pages 151 passés, 2 435 sous-tests, 328,6 s. Aucun échec instable.
- `comparer_listes.py S/rapports/P2b S/rapports/P3` : 34 tests Python nouveaux (22 `test_equations_saisie`, 10 `TestRamener`,
  2 `TestNonResolu`), aucun disparu ; les 10 `test_a_venir[P3-…]` passent de xfail à passé (mêmes noms) ; pages identiques nom par nom.
  Sous-tests en baisse : `test_exp_log::…::test_aucun_texte_du_fichier_ne_tutoie` 957 → 955 (960 → 955 contre `tests/reference`,
  littéraux « __slots__ » et « nom » de `_a_des_decimaux` déplacés) et `TestNonResolu::test_formes_pas_encore_traitees` 21 → 11
  (formes P3 résolues), justifiées dans suivi.md ; hausses : instantanés 72 → 98, invariants 317 → 361, oracle 121 → 165,
  `test_expr` (+1 et +1), `test_vocabulaire::test_litteraux_des_moteurs` 9 447 → 9 508.
- **Dump** : `dump_sorties.py S/dumps/P3 --processus 6` (17 fichiers, 4 148 sorties, 4 s), `diff -r --exclude=temps S/dumps/depart
  S/dumps/P3` : **code 0, aucune sortie** (invariant tenu ; Exp-log identique après le déplacement de `_a_des_decimaux`).
- xfail stricts : **10 retirés** (« P3 ») ; aucun ajouté ; restent 12 (5 « P4a », 7 « P4b »).

## P4a — formes structurées

### Plan

Corrigé relu (`Id_rem.pdf` 2.9 k, l ; `tatonement.pdf` 2.12 e, h ; Az 4.1 d : énoncé seul, sans corrigé).

1. **`second_degre`, chemin structuré** (section 7, nouvelle sous-section « P4a », sur le calcul de P1 : `Nombre`, `produit_nul`,
   `redevelopper`, `verifier_solution` ; aucune méthode recalculée) : `resoudre_equation` essaie d'abord la structure quand
   `forme_structuree` (P3, inchangée) est vraie ; une structure reconnue mais hors de ce que P4a écrit donne `non_traite` (message
   clair, on ne développe pas : E1.3, option qui affiche le moins) ; sinon P3 (ramener, développer) comme avant.
   - **Produit déjà nul** (E13, Az 4.1 d) : produit écrit (constante, monômes, sommes réduites de degré 1, carré d'une telle somme)
     égal à 0 (ou 0 égal au produit : ligne ramenée « produit = 0 ») ; D24 : un carré est réécrit `(B)(B)` dans l'arbre de la saisie
     (décimaux gardés) ; puis le produit nul de P2b, les facteurs écrits comme dans la saisie (`2 − x = 0`, D14 : ordre écrit).
   - **Id. rem. sur une forme structurée** (E5, 2.9 k, l, 2.12 h) : termes (tout ramené à gauche, E1.3 « on soustrait le second
     membre sans développer », constantes regroupées sur une 2e ligne s'il y en a plusieurs) = un carré k(B)² (B somme réduite de degré
     1, √k rationnel) et une constante de signe opposé, ou deux carrés de signes opposés ; A = le terme positif, B = le négatif. B
     constant peut être irrationnel (√5, D8) ; A constant, rationnel. Étiquette en marge (2.9 l, E5), ou ligne de texte « (car A² = …) »
     quand √k ≠ 1 (2.9 k) ; A et B dans un seul cadre (D29, comme P2b). Lignes : `(A + B)(A − B)` avec les parenthèses du corrigé,
     puis les parenthèses enlevées (seulement si un « − » précède une parenthèse ou si √k ≠ 1 : 2.9 l n'a pas cette ligne, 2.9 k et
     2.12 h l'ont), puis les facteurs réduits (E5 : terme en x d'abord, sauf coefficient négatif et constante positive : `2 − 3x`) ;
     pas de ME après coup ; P de degré 2 exigé (sinon `non_traite` : degré 1, P4b).
   - **Facteur commun aux deux membres** (E3, 2.12 e) : un facteur de degré 1 **égal** (même polynôme) dans les deux membres, chaque
     membre étant un produit écrit (ou une somme seule), le reste de chaque membre de degré ≤ 1 et leur différence de degré 1 ;
     l'avertissement d'E3 mot pour mot, `g − d = 0`, `F[(G) − (H)] = 0` (ME), parenthèses enlevées, facteur réduit, produit nul.
   - Garde-fou (principe 1) : chaque ligne écrite est relue dans Q(√m) (évaluateur des arbres écrits, nœuds `Groupe` et `Crochet`
     compris) et doit donner ±P (P = gauche − droite) ; facteurs redéveloppés = P ; chaque solution annule P ; sinon `ne_conclut_pas`.
   - Étapes (§ 5) : ramener (RAMENER, avertissement compris) · factoriser (IDREM_DIFF ou ME) · produit_nul ; pas de variante
     « formule » sur une forme structurée (elle demanderait de développer, ce qu'E1.3 exclut ; option qui affiche le moins, notée).
2. **Petits ajouts sans effet sur l'existant** : `_Contexte.ecrits` (facteurs écrits comme dans la saisie), `Produit` écrit un
   `Crochet` sans parenthèses, constante « impossible » par `nb_exact` (identique pour un entier, seul cas de P2b/P3).
3. **Tests** : `corpus_second_degre.P4A` (les 5 entrées « P4a » d'`A_VENIR` et d'autres formes), `RESOLUES += P4A`,
   `PARTIES_FAITES = ("P3", "P4a")` (les 5 xfail stricts « P4a » passent, mêmes noms) ; `test_redaction_second_degre` : invariants,
   oracle, D29, R12 sur `RESOLUES` ; textes rendus de 2.9 k, 2.9 l, 2.12 e, 2.12 h, Az 4.1 d et des autres formes ; garde-fou (ligne
   faussée → `ne_conclut_pas`) ; formes structurées non écrites → `non_traite` ; `test_structures_laissees_a_p4a` devient
   `test_structures_sans_developper` (justifié dans suivi.md) ; instantanés : entrées nouvelles seulement.
4. Suite complète, dump, temps natif, commit.

### Réalisé

- **`moteur/second_degre.py`**, sous-section « P4a » de la section 7 (≈ 450 lignes ; aucun calcul de méthode refait : `Nombre`,
  `produit_nul`, `redevelopper`, `verifier_solution`, `_ecrire_produit_nul` de P2b) :
  - `resoudre_equation` : si `forme_structuree` (P3, inchangée), `_rediger_structure` (produit déjà nul, puis facteur commun, puis
    Id. rem. structurée) ; None → `non_traite` (jamais développée) ; sinon P3 comme avant. Pas de variante sur une forme structurée.
  - Nœuds de l'outil : `Groupe` (parenthèse du corrigé : ((x + 1) + 4)), `Crochet` ((x − 1)[(2 − x) − (x + 3)]), `Juxtaposition`
    (un produit écrit côte à côte : expr.tex écrit « (x − 1)(2 − x) · (5 − 3x) », « 2x · (x − 3) », « \frac{1}{4} · (x + 1)² » ; « · »
    seulement devant un nombre). `ecrire_enonce(g, d, x)` : l'énoncé d'une forme structurée en `Juxtaposition`, celui des autres
    formes inchangé (instantanés de P2b et P3 identiques ; « \frac{3}{2} \cdot x^{2} » de P3 reste tel quel).
  - Lecture : `_binome_ecrit` (somme écrite réduite de degré 1, termes dans l'ordre écrit), `_produit_ecrit` (k·xʲ·Π(Bᵢ)^eᵢ, eᵢ ≤ 2),
    `_membre_en_facteurs`, `_carre_ecrit` (k(B)²), `_commun` (facteur **égal** dans les deux membres, restes de degré ≤ 1, différence
    de degré 1).
  - Écriture : `_ecrire_produit_ecrit` (D24 : `_sans_carres` dans l'arbre de la saisie, décimaux gardés), `_ecrire_commun`
    (avertissement d'E3 mot pour mot, `g − d = 0` (ou `g + d` si la droite commence par « − »), crochet, parenthèses enlevées,
    facteur réduit), `_ecrire_carres` (ligne `g − d`, constantes regroupées sur une 2e ligne s'il y en a plusieurs ; une constante nulle :
    produit nul direct ; `_terme_idrem` pour A et B ; étiquette ou ligne « (car A² = … et B² = …) » quand √k ≠ 1 ; ligne des
    parenthèses enlevées seulement si √k ≠ 1 ou si B est un carré, « − » devant une parenthèse : 2.9 l n'en a pas, 2.9 k et 2.12 h en
    ont une), `_facteur_reduit` (E5 : 2 − 3x, mais −2x − 1 ; x + 1 − √5), `_ligne_produit` (un facteur monôme en tête : x(x + 2)).
  - Garde-fou (`_Structuree`) : l'énoncé réécrit et chaque ligne sont relus dans Q(√m) (`_ecrit_en_nombres` : Nb, l'inconnue, Neg,
    Op, Pow entier, √ d'une constante, nœuds de l'outil) et doivent valoir ±P (P = gauche − droite, `vers_polynome`) ; facteurs
    redéveloppés = ±P ; chaque solution annule P ; sinon `_Incoherent` → `ne_conclut_pas`. Test : trois écritures faussées exprès
    (facteur réduit, reste du facteur commun, énoncé) → `ne_conclut_pas` ; la 3e a fait ajouter la relecture de l'énoncé (oubliée au
    premier jet : un `Juxtaposition` faux serait passé).
  - Petites retouches sans effet sur l'existant : `_Contexte.ecrits` (facteurs écrits comme dans la saisie, None ailleurs) ; constante
    « impossible » par `nb_exact` (entier : même `Nb`) ; ligne finale du produit nul sans doublon (« x = −1 » une fois, facteurs
    proportionnels) ; paramètre `reecriture` de `_ecrire_produit_nul` (ligne D24 en tête de l'étape). **Écart au plan** : `Produit`
    n'est pas modifié (les lignes de P4a sont des `Juxtaposition`).
  - Étapes : ramener (RAMENER, `cote` « gauche », ou « droite » pour « 0 = produit » ; l'avertissement d'E3 en tête) · factoriser
    (IDREM_DIFF : `parametres` {A, B (TeX), forme « structuree », facteurs} ; ME : {facteur, facteurs}) · produit_nul (la ligne D24
    comprise).
- **Tests** :
  - `corpus_second_degre` : `P4A` (33 équations : les 5 « P4a » d'`A_VENIR` sous la même saisie, 9 produits déjà nuls, 11 Id. rem.
    structurées, 8 facteurs communs), `RESOLUES = P2B + P3 + P4A`, `PARTIES_FAITES = ("P3", "P4a")`, `STRUCTURES_NON_ECRITES`
    (10 formes, avec la raison).
  - `test_redaction_second_degre` : `ENONCES` par `sd.ecrire_enonce` ; `TestStructures` (11 tests : textes rendus de 2.9 k, 2.9 l,
    2.12 h, 2.12 e, Az 4.1 d comparés au corrigé ; autres produits, Id. rem. et facteurs communs ; aucune variante ni développement ;
    énoncé ; chaque ligne relue et trois écritures faussées) ; `TestNonResolu.test_structures_laissees_a_p4a` devient
    `test_structures_sans_developper` (mêmes formes, plus `STRUCTURES_NON_ECRITES` : résolues sans DEVELOPPER, ou `non_traite`) ;
    invariants, oracle (`oracle.racines`), D29, R12 et C6 : sur `RESOLUES` (33 entrées de plus) ; les 5 `test_a_venir[P4a-…]`
    passent (marque xfail retirée par `PARTIES_FAITES`, mêmes noms).
  - Instantanés (`tests/python/donnees/equations-2e-degre/instantanes.json`) : **33 entrées nouvelles, aucune des 98 de P2b et P3
    modifiée** (comparaison JSON entrée par entrée).
  - `test_second_degre` : commentaire du corpus seulement.
- **Arêtes** : aucune nouvelle (`comme_somme` vient d'`expr`, arête de P1).

### Texte rendu de 2.9 k, 2.9 l, 2.12 e, 2.12 h et Az 4.1 d, comparé au corrigé

Rangées de `textes(res)` (« lien | expr | étiquette » ; une ligne de texte seule), puis S.

    2.9 k   | 4(x - 2)^{2} = 1 |
            \iff | 4(x - 2)^{2} - 1 = 0 |
            Id. rem. \(A^{2} - B^{2}\) avec \(\fbox{$A = 2(x - 2),\ B = 1$}\) (car \(A^{2} = 4(x - 2)^{2}\)).
            \iff | (2(x - 2) + 1)(2(x - 2) - 1) = 0 |
            \iff | (2x - 4 + 1)(2x - 4 - 1) = 0 |
            \iff | (2x - 3)(2x - 5) = 0 |
            \iff | 2x - 3 = 0 ou 2x - 5 = 0 | produit nul
            \iff | x = 3/2 ou x = 5/2 |                                     S = {3/2 ; 5/2}
    2.9 l   | (x + 1)^{2} = 16 |  \iff (x + 1)^{2} - 16 = 0
            \iff | ((x + 1) + 4)((x + 1) - 4) = 0 | Id. rem. A² − B² avec ⟦A = x + 1, B = 4⟧
            \iff (x + 5)(x - 3) = 0  \iff x + 5 = 0 ou x - 3 = 0 (produit nul)  \iff x = -5 ou x = 3         S = {−5 ; 3}
    2.12 e  Attention : on ne divise pas par (x − 1), car ce facteur peut être nul ! On ramène tout dans le membre de gauche, puis on
            met (x − 1) en évidence.
            (x - 1)(2 - x) = (x - 1)(x + 3)  \iff (x - 1)(2 - x) - (x - 1)(x + 3) = 0
            \iff (x - 1)[(2 - x) - (x + 3)] = 0 (ME)  \iff (x - 1)(2 - x - x - 3) = 0  \iff (x - 1)(-2x - 1) = 0
            \iff x - 1 = 0 ou -2x - 1 = 0 (produit nul)  \iff x = 1 ou x = -1/2                           S = {−1/2 ; 1}
    2.12 h  16 - (3x + 2)^{2} = 0  \iff (4 + (3x + 2))(4 - (3x + 2)) = 0 | Id. rem. A² − B² avec ⟦A = 4, B = 3x + 2⟧
            \iff (4 + 3x + 2)(4 - 3x - 2) = 0  \iff (3x + 6)(2 - 3x) = 0
            \iff 3x + 6 = 0 ou 2 - 3x = 0 (produit nul)  \iff x = -2 ou x = 2/3                             S = {−2 ; 2/3}
    Az 4.1 d  (x - 1)(2 - x)(5 - 3x) = 0  \iff x - 1 = 0 ou 2 - x = 0 ou 5 - 3x = 0 (produit nul)
            \iff x = 1 ou x = 2 ou x = 5/3                                                                 S = {1 ; 5/3 ; 2}

**Comparaison** : mêmes lignes que le corrigé, dans le même ordre, pour 2.9 k, 2.9 l, 2.12 e (avertissement, crochet, « 2 − x − x − 3 »,
−2x − 1, solutions dans l'ordre des facteurs) et 2.12 h (« 4 − 3x − 2 », (3x + 6)(2 − 3x), sans ME après coup). Écarts : étiquette
« produit nul » (D5, voulu) ; A et B encadrés (D29, voulu) ; **2.12 h : A et B en étiquette en marge** (E5 : la ligne de texte n'est
écrite que si A doit être justifié ; le corrigé en écrit une, « Id. rem. A² − B² avec A = 4 et B = 3x + 2. » : question 22 de
suivi.md) ; « (car …) » avec « , » entre A et B dans le cadre (D29 : un seul cadre) au lieu de « et ». Az 4.1 d : énoncé seul dans la
référence (pas de corrigé) ; produit nul direct (E13).

### Suite d'avant commit et dump

- `PROCESSUS_PAGES=4 python3 tests/lancer.py complet --rapport S/rapports/P4a` : **code 0** (≈ 7 min de mur ; console
  `S/rapports/P4a-console.log`). Python 1 652 collectés, 1 644 passés + 8 xfail (1 d'avant + 7 stricts P4b), 125 662 sous-tests,
  100,4 s ; pages 151 passés, 2 435 sous-tests, 328,4 s. Aucun échec instable.
- `comparer_listes.py S/rapports/P3 S/rapports/P4a` : 12 tests Python nouveaux (11 `TestStructures`, `test_structures_sans_developper`),
  1 disparu par renommage (`test_structures_laissees_a_p4a`, justifié dans suivi.md, « Tests renommés ») ; les 5 `test_a_venir[P4a-…]`
  passent de xfail à passé (mêmes noms) ; pages identiques nom par nom. Sous-tests : une baisse, `TestNonResolu::
  test_formes_pas_encore_traitees` 11 → 6 (formes P4a résolues, justifiée dans suivi.md) ; hausses : instantanés et invariants
  (+33 chacun), oracle 165 → 198, vouvoiement 6 139 → 6 651, `test_vocabulaire::test_litteraux_des_moteurs` 9 508 → 9 635, gardes
  de memo (+1 chacune).
- **Dump** : `dump_sorties.py S/dumps/P4a --processus 6` (17 fichiers, 4 148 sorties, 4 s), `diff -r --exclude=temps S/dumps/depart
  S/dumps/P4a` : **code 0, aucune sortie** (invariant tenu).
- xfail stricts : **5 retirés** (« P4a ») ; aucun ajouté ; restent 7 (« P4b »).

## P4b — degrés ≠ 2 et reste du corpus

### Plan

Corrigé relu : `tatonement.pdf` 2.12 c (x³ − x = 0 ⇔ x(x² − 1) = 0 ME ⇔ x(x + 1)(x − 1) = 0 Id. rem. ⇔ x = 0 ou x + 1 = 0 ou
x − 1 = 0 ⇔ x = 0 ou x = −1 ou x = 1) ; Az 4.1 a, f, g (énoncés seuls) ; x⁴ − 16 : § 13.4 et point 4 du plan (D28). Aucun calcul nouveau
des méthodes : `chemin` (P1) traite déjà les degrés ≥ 3 (ME, Id. rem. de A = x², facteurs récursifs) ; P4b écrit ce calcul.

1. **Degrés ≥ 3, chemin développé** (`_rediger`, sur `chemin`) :
   - `_Contexte.courants` : les facteurs écrits du produit courant (après le préfixe k·xʲ de la ME) ; chaque factorisation d'un facteur
     Q le remplace sur place par ses facteurs (ME : préfixe et reste ; Id. rem. A² − B² : (A + B)(A − B) ; A² ± 2AB + B² : le carré puis
     D24 ; S-P et tâtonnement : leurs deux facteurs) ; chaque ligne écrite est redéveloppée et comparée à P (garde-fou). En degré 2,
     `courants` = [Q] à chaque factorisation : mêmes lignes qu'avant (instantanés de P2b–P4a inchangés, contrôlé).
   - Ordre d'écriture : les tentatives en échec et la formule d'un facteur (S-P ou tâtonnement en échec, formule) viennent après les
     autres factorisations (x⁴ − 16 : Id. rem. de x² − 4, puis le tableau S-P de x² + 4 en échec, puis le produit nul et Δ, E9) ; en
     degré 2, elles sont déjà les dernières.
   - Phrase de choix sur un facteur : celle d'après une ME (« Le trinôme x² + 4 est unitaire : S-P. ») dès qu'une factorisation est
     écrite ; formule d'emblée sur un facteur non entier : « Les coefficients du trinôme … ne sont pas entiers : on utilise la
     formule. » ; ME de a < 0 en degré ≠ 2 : « Le coefficient de x³ est négatif : on met d'abord … en évidence. » (pas de « trinôme »).
   - Produit nul (E8, E9) : plusieurs trinômes par la formule (leurs lignes de Δ dans l'ordre du produit), D20 avec un trinôme ; la
     formule seule (sans ligne de produit nul) seulement si le trinôme est P.
   - Variante E12 inchangée (proposée si elle a une formule : 2.12 c).
2. **Degré 1** : ramener (E1), puis l'étape « isoler » (ISOLER) : x = … en une ligne, ou kx = … puis x = … (D20).
3. **Identité, égalité fausse** (E13, § 13.4) : après E1/E2, la ligne des constantes (« 1 = 1 », « 1 = 2 ») au lieu de « 0 = 0 »
   ramenée (Exp-log), puis la phrase d'Exp-log ; S = ℝ ou S = ∅. Sur une forme structurée (P nul) : « g − d = 0 », puis « 0 = 0 ».
4. **Messages** : degré ≥ 3 que le cours ne résout pas : « bicarrée » (statut `pas_encore`) si P = ax⁴ + bx² + c (c ≠ 0) et que ni
   ME ni Id. rem. ne s'applique (§ 13.4, à la lettre) ; sinon « hors du cours ». Le statut temporaire `non_traite` disparaît : une forme
   que l'outil n'écrit pas (E2 hors de ce qu'il développe, structure non écrite) reçoit « hors du cours » (consigne de la nuit, option qui
   affiche le moins ; question pour l'enseignant). Autres lettres que l'inconnue : ValueError (la saisie, P3, les refuse avant).
5. **Formes structurées laissées à P4b** (`STRUCTURES_NON_ECRITES`, « (P4b) ») : facteur de degré 2 dans un produit déjà nul
   ((x² − 1)(x + 2) = 0, 3(x² − 4) = 0 : le facteur factorisé par le cours, `courants`) ; degré 1 une fois factorisée ((x + 1)² = (x − 3)²,
   (x − 1)(x + 2) = (x − 1)(x + 5) : le facteur constant écrit en tête, « 4 = 0 » impossible). Si ce n'est pas possible proprement :
   « hors du cours », noté.
6. **Tests** : `corpus_second_degre.P4B` (2.12 c, Az 4.1 f, Az 4.1 g, x⁴ − 16, x³ − 5x, degré 1, identités, égalités fausses, a < 0
   en degré 3, Id. rem. de A = x², formes structurées de P4b), `NON_RESOLUES` (bicarrée, hors du cours), `SECTION_8` (les noms du § 8) ;
   oracle sur `RESOLUES` (S = ℝ / ∅ contrôlés à part) ; instantanés de `RESOLUES` et `NON_RESOLUES` (entrées nouvelles seulement ;
   toute entrée de P2b–P4a modifiée justifiée ici, avant / après) ; chaque entrée du § 8 a un instantané et l'oracle ; les 7 xfail
   stricts « P4b » passent (marques retirées) ; `test_formes_pas_encore_traitees` (test d'attente devenu vide) remplacé.
7. Suite complète, dump, temps natif, commit.

### Réalisé

- **`moteur/second_degre.py`** (aucun calcul de méthode nouveau : `chemin`, `produit_nul`, `racines_formule`, `identite`,
  `mise_en_evidence` de P1) :
  - `_Contexte.suivre`, `remplacer`, `deplier`, `produit_courant` : le produit écrit (préfixe k·xʲ et facteurs) ; chaque factorisation
    remplace son facteur sur place ; chaque produit écrit est **relu dans Q(√m)** (`_ecrit_en_nombres`) et doit valoir ±P (garde-fou
    nouveau pour les lignes de factorisation du chemin développé). `_ecrire_me`, `_ecrire_idrem`, `_ecrire_sp`, `_ecrire_tatonnement`
    passent par `remplacer` (sans suivi, pour `appliquer` : mêmes lignes qu'avant).
  - `_rediger` : `_ordre_d_ecriture` (tentatives en échec et formule d'un facteur en dernier), `_ecrire_chemin` (la boucle des
    méthodes, partagée avec les formes structurées), produit nul sur les facteurs **dans l'ordre écrit** (contrôlé : mêmes solutions
    que le chemin, produit = P), formule seule seulement si le trinôme est P ; `_noms_formule` (x₁, x₂ si une seule formule les nomme).
  - `_ecrire_produit_nul` : plusieurs trinômes (E9, lignes de Δ dans l'ordre du produit), D20 avec un trinôme ; `_choix` : formule
    d'emblée sur un facteur ; `_ecrire_me` : a < 0 en degré ≠ 2 sans « trinôme ».
  - `ramener` : P de degré ≤ 0, la ligne des constantes (« 1 = 2 ») relue, sans changement de côté ; `_ecrire_isoler`,
    `_rediger_bas_degre` (degré 1, identité, égalité fausse) ; `bicarree(P)` ; `MESSAGES` : `non_traite` retiré, `pas_encore` (le
    message « bicarrée » du § 4) ajouté ; `resoudre_equation` : degré ≥ 3 par le chemin, `hors_cours` → `pas_encore` si bicarrée,
    forme non écrite → `hors_cours`, autre lettre → `ValueError`.
  - Formes structurées : `_trinome_ecrit`, `_produit_ecrit(…, trinomes=True)` et `_factoriser_produit_ecrit` (facteur de degré 2 d'un
    produit déjà nul, factorisé par le cours sur le produit écrit) ; `_commun` (G − H constant) et `_ecrire_carres` (un facteur
    constant) : degré 1 une fois factorisée, `_constante_reduite`, `_ligne_produit` (une constante en tête comme un monôme) ;
    `_ecrire_identite_structuree` ; `_Structuree.fin` accepte S = ∅ (trinôme de Δ < 0) et nomme x₁, x₂ comme le chemin développé.
  - **Écart au plan** : aucun (point 5 fait pour les quatre formes « (P4b) » de `STRUCTURES_NON_ECRITES` ; les six autres et deux
    nouvelles restent « hors du cours », question 29).
- **Tests** :
  - `corpus_second_degre` : `P4B` (36), `NON_RESOLUES` (16, avec le statut attendu), `SECTION_8` (52 noms), `STRUCTURES_NON_ECRITES`
    (8 : quatre formes résolues retirées, deux ajoutées), `PARTIES_FAITES = ("P3", "P4a", "P4b")`.
  - `test_redaction_second_degre` : `TestDegres` (11 tests : 2.12 c comparé au corrigé, Az 4.1 f, x⁴ − 16 (D28, E9), degré 3, Id. rem.
    de A = x², degré 1, identité et égalité fausse, formes structurées de P4b, messages, polynômes générés de degré 3 et 4 de P1 (44 :
    oracle, invariants, sortie conforme), produits écrits relus et deux écritures faussées → « ne_conclut_pas ») ;
    `TestOracle.test_corpus_et_variantes` : P de degré 0 contrôlé à part (S = ℝ ⇔ P nul, sinon ∅) ; `test_aucun_statut_temporaire`
    (renommage, suivi.md) ; `test_structures_sans_developper` (+5 formes résolues ; non écrites : « hors_cours ») ;
    `test_hors_de_ce_que_e2_developpe` (« hors_cours », degré 1 et identité résolus) ; `test_az_4_1_g_developpement` (S = ℝ) ;
    les 6 `test_a_venir[P4b-…]` et `test_P4b_bicarree` passent : **7 xfail stricts retirés**, aucun ajouté ; il ne reste que l'xfail
    d'avant le chantier.
  - `test_instantanes_second_degre` : `RESOLUES` et `NON_RESOLUES` ; `test_section_8_complete` (chaque exercice du § 8 a un instantané,
    résolu ; l'oracle les contrôle tous par `TestOracle`). JSON régénéré : **52 entrées nouvelles, aucune des 131 de P2b–P4a modifiée**
    (comparaison JSON entrée par entrée).
- **Arêtes** : aucune nouvelle.

### Texte rendu de 2.12 c, Az 4.1 f, Az 4.1 g et x⁴ − 16, comparé au corrigé

    2.12 c   | x^{3} - x = 0 |  \iff x(x^{2} - 1) = 0 (ME)
             \iff x(x + 1)(x - 1) = 0 | Id. rem. A² − B² avec ⟦A = x, B = 1⟧
             \iff x = 0 ou x + 1 = 0 ou x - 1 = 0 (produit nul)  \iff x = 0 ou x = -1 ou x = 1          S = {−1 ; 0 ; 1}
    Az 4.1 f | x^{3} + 8x^{2} = 0 |  \iff x^{2}(x + 8) = 0 (ME)  \iff x² = 0 ou x + 8 = 0 (produit nul)  \iff x = 0 ou x = -8
                                                                                                      S = {−8 ; 0}
    Az 4.1 g | (2x - 1)^{2} - 4x \cdot (x - 1) = 1 |
             \iff 4x² − 4x + 1 − (4x² − 4x) = 1 | Id. rem. (A − B)² avec A = 2x, B = 1 ; distribution
             \iff 4x² − 4x + 1 − 4x² + 4x = 1  \iff 1 = 1
             Cette égalité est vraie pour tout nombre réel.                                           S = ℝ
    x⁴ − 16  | x^{4} - 16 = 0 |  \iff (x² + 4)(x² − 4) = 0 | Id. rem. A² − B² avec ⟦A = x², B = 4⟧
             \iff (x² + 4)(x + 2)(x − 2) = 0 | Id. rem. A² − B² avec ⟦A = x, B = 2⟧
             Le trinôme x² + 4 est unitaire : S-P.
             On cherche deux nombres dont le produit vaut 4 et la somme vaut 0 :  [tableau 1 4 | 5 ; 2 2 | 4]
             Aucun couple ne convient : on utilise la formule.
             \iff x² + 4 = 0 ou x + 2 = 0 ou x − 2 = 0 (produit nul)
             Δ = b² − 4ac = 0² − 4 · 1 · 4 = ⟦−16⟧
             Δ < 0 : x² + 4 = 0 n'a aucune solution réelle.
             \iff x = −2 ou x = 2                                                                    S = {−2 ; 2}

**Comparaison** : 2.12 c a les lignes du corrigé (`tatonement.pdf`), dans le même ordre ; écarts voulus : étiquettes D5
(« Id. rem. A² − B² avec … » au lieu de « Id. rem. A = x, B = 1 », « produit nul » sur la ligne des facteurs), A et B encadrés
(D29). Az 4.1 f, g : énoncés seuls dans la référence ; Az 4.1 g suit l'exemple du § 7, avec la phrase d'Exp-log (§ 13.4) au lieu de
« L'égalité est vraie pour tout réel x. ». x⁴ − 16 : § 13.4 et point 4 du plan (D28 puis E9) ; ordre d'écriture : question 31. L'énoncé
d'Az 4.1 g garde le « · » d'expr.tex (forme développée, P3 ; question 26 : P5).

### Suite d'avant commit et dump

- `PROCESSUS_PAGES=4 python3 tests/lancer.py complet --rapport S/rapports/P4b` : **code 0** (≈ 7 min 30 de mur ; console
  `S/rapports/P4b-console.log`). Python 1 664 collectés, 1 663 passés + 1 xfail (celui d'avant le chantier), 127 242 sous-tests,
  109,8 s ; pages 151 passés, 2 435 sous-tests, 328,1 s. Aucun échec instable.
- `comparer_listes.py S/rapports/P4a S/rapports/P4b` : 13 tests Python nouveaux (11 `TestDegres`, `test_section_8_complete`,
  `test_aucun_statut_temporaire`), 1 disparu par renommage (`test_formes_pas_encore_traitees`, justifié dans suivi.md, « Tests
  renommés ») ; les 7 xfail stricts « P4b » passent (mêmes noms) ; pages identiques nom par nom. Sous-tests : **aucune baisse** ;
  hausses : instantanés 131 → 183, invariants et oracle 394 → 437 et 198 → 241, `test_structures_sans_developper` 30 → 33,
  vouvoiement 6 651 → 7 361, `test_vocabulaire::test_litteraux_des_moteurs` 9 635 → 9 691, lecture de la saisie 131 → 167.
- **Dump** : `dump_sorties.py S/dumps/P4b --processus 6` (17 fichiers, 4 148 sorties, 4 s), `diff -r --exclude=temps S/dumps/depart
  S/dumps/P4b` : **code 0, aucune sortie** (invariant tenu).
- xfail stricts : **7 retirés** (« P4b ») ; aucun ajouté ; il n'en reste aucun du chantier.

## P5 — l'outil

### Plan

**0. Message vrai pour ce que l'outil n'écrit pas** (question 29, décision du chef ; CLAUDE.md « rien de faux » prime) : nouveau
statut `forme_non_traitee`, message « Cette forme d'équation n'est pas traitée par l'outil. » (un statut de plus, le reste ne change
pas : ce qui change le moins). Il remplace « hors du cours » pour : E2 hors de ce qu'il développe (`ramener` → None), structure non
écrite (`_rediger_structure` → None), et tout degré ≥ 3 **douteux**. « Hors du cours » n'est gardé que s'il est vrai : polynôme
développé de degré ≥ 3, coefficients entiers, pas une bicarrée, et aucune méthode du cours n'aboutit (le chemin de D28 n'a fait
qu'une ME de constante, rien sur xʲ ni d'Id. rem.) et le facteur qui reste n'est pas une bicarrée. Instantanés concernés : liste
avant / après ci-dessous et sous « À relire ». Question 29 laissée ouverte.

**1. Liste à cocher du plan (section P5)** :

- [x] `equations-2e-degre/index.html` (monterOutil ; `const EXEMPLES=[…]` des 10 entrées du § 13.3 ; GoatCounter ; `style.css` puis
  `composants.css` ; aria-live ; `<details class="card">` « Rappel de la méthode » fermé (E15) ; clavier, dernière rangée `0 , x =` ;
  aucun `exercicePython`)
- [x] `equations-2e-degre/resoudre_eq.py` (`resoudre`, `resoudre_json`, `apercu_json` ; `apercu_json('x+1')` ok ; variante E12 par
  `sortie_ok_variantes` ; l'énoncé par `second_degre.ecrire_enonce`, question 26) ; une carte « Résolution » (blocs de
  `second_degre.blocs` : la chaîne, S encadré, la ligne ≈)
- [x] `moteur/manifeste.json` (fichiers du plan ; fonctions `resoudre`, `apercu`)
- [x] `commun/registre.json` (option A, `"filieres": {}`) ; `tests/pages/test_accueil.py` butée (16, 7) → (16, 8) (et ACC-03 : seuls
  les outils à carte ont un lien)
- [x] `test_imports.py` ARETES (`equations -> expr / noyau / second_degre / polynomes`, `resoudre_eq -> equations / sortie /
  second_degre / chaine`…, chacune avec sa raison) ; `test_noyau.py` MOTEURS ; `test_outils_du_site.py` butée de sys.path
- [x] instantanés : le JSON provisoire déplacé dans `tests/python/instantanes/equations-2e-degre.json` (clé = saisie ; entrée `OUTILS`
  et méthode de `test_instantanes.py`), `test_instantanes_resoudre.py` + `instantanes/resoudre/equations-2e-degre.json`
- [x] `cas.py` : `CAS_LIMITES["equations-2e-degre"]` (§ 8 et § 6) et `entrees_equations()` (corpus complet de la rédaction et
  saisies invalides) ; `test_vocabulaire.METHODES` ; `test_json_strict` ; `test_resoudre_import.EXEMPLE` = `x^2-5x-36=0` ;
  `test_source_unique.TestDispositionDuClavier.PAGES`
- [x] pages : `rendu.py` REDUIT (2.10 a, 2.11 h, une saisie invalide) et ERREURS ; `test_comportement.py` (CALCUL = Javet 2.17 c,
  EXEMPLE = 2.9 a, INVALIDE) ; `test_rendu.py::test_equations_2e_degre` ; `references/equations-2e-degre.json` par
  `capturer_references.py`
- [x] `docs/architecture.md` § 1, § 4, § 5 ; `docs/taches.md` (D16)
- [x] vérifié sans rien écrire : `test_largeurs` (méthode générée, `CONNUS` vide), `test_style_commun`, `test_tableaux_css`, `MIGREES`,
  `TestVouvoiement`, `test_memo_garde`, `captures.py`, `lancer.py`

**2.** Le dossier provisoire `tests/python/donnees/equations-2e-degre/` retiré ; `test_instantanes_second_degre.py` garde ce qui
n'est pas couvert ailleurs (§ 8 complet, sorties conformes), sur le nouveau fichier ; justifications dans suivi.md.

**3.** Captures à 390 px (clair ; sombre pour 2.11 h) de 2.11 h, 2.10 a, Javet 2.17 c, 2.12 e, (x + 1)(x + 3) = 15 dans
`S/captures/P5/`. **4.** Contrôle de la page (chargement, exemples, clavier, message d'erreur, variante E12). Puis suite complète,
dump, temps natif, commit.

### Réalisé

- **0. Message vrai** (`moteur/second_degre.py`) : `MESSAGES["forme_non_traitee"]` = « Cette forme d'équation n'est pas traitée par
  l'outil. » ; `hors_du_cours(P, chemin)` (public) ; `resoudre_equation` : `_rediger_structure` → None et `ramener` → None donnent
  « forme_non_traitee » ; `chemin` en « hors_cours » : « pas_encore » si bicarrée, « hors_cours » si `hors_du_cours`, sinon
  « forme_non_traitee ». Docstrings mises à jour. Tests : `corpus_second_degre.NON_RESOLUES` (11 statuts), `STRUCTURES_NON_ECRITES`
  (« forme_non_traitee »), `test_aucun_statut_temporaire` (5 statuts), `test_structures_sans_developper`,
  `test_hors_de_ce_que_e2_developpe`, `test_polynomes_generes_de_degre_3_et_4` (un « hors_cours » y est contrôlé par `hors_du_cours`),
  nouveau `TestNonResolu.test_hors_du_cours_seulement_si_vrai` (11 polynômes : x³ − x − 1, 2x³ + 2x + 2, Az 4.1 d développé, x⁴ + x + 1
  → hors du cours ; 2x⁴ − 10x² + 8, x⁶ − 64, 0,5x³ − 2x, −x⁴ + 5x² − 4, x⁵ − 5x³ + 4x, x⁴ + x → forme non traitée ; x⁴ − 5x² + 4 →
  bicarrée ; puis chaque « hors_cours » du corpus relu : degré ≥ 3, entier, pas bicarrée, seulement une ME de constante).
  **Instantanés modifiés (11, statut et message seulement ; avant : `hors_cours` / « Cette équation ne se résout pas avec les méthodes
  du cours. » ; après : `forme_non_traitee` / « Cette forme d'équation n'est pas traitée par l'outil. »)** : Az 4.1 b
  `(3x-2)/6=(x+1)/4+5`, Az 4.1 h `x^2+1-(10-x^2)/8=(6x-3)/4`, `(x^2+x+1)^2=x`, `(x+1)^3=8+x`, `x^2/2=1+x`, `0,5(x+2)^2=x+3`,
  `x*3+x^2=1`, `2(x+1)(x+3)=5`, `x^6-64=0`, `0,5x^3-2x=0`, `2x^4-10x^2+8=0`. Gardés « hors du cours » (vrai) : `x^3=x+1`,
  `-3x^3+14x^2-21x+10=0`. Les 8 `STRUCTURES_NON_ECRITES` (pas d'instantané avant P5) reçoivent aussi « forme_non_traitee ».
  Comparaison entrée par entrée (`S/tmp/P5/comparer.py`) : les 183 entrées d'avant sont toutes là ; seules ces 11 changent ;
  21 nouvelles (les 8 structures, 13 saisies invalides).
- **`equations-2e-degre/resoudre_eq.py`** : `resoudre` (analyser → message ; statut non résolu → `sortie_erreur(message)` ; sinon une
  carte « Résolution » = `second_degre.blocs`, énoncé `tex_element(ecrire_enonce(…))` ; variante E12 « Méthodes du cours » (défaut) /
  « Par la formule » par `sortie_ok_variantes` quand `variantes == ["formule"]` et que la formule conclut), `resoudre_json`,
  `apercu_json` (lecture seule ; « x+1 » : ok, `tex` de l'expression ; une équation que l'analyse accepte : l'énoncé de
  `ecrire_enonce`, sinon « g = d »).
- **`equations-2e-degre/index.html`** : `monterOutil({outil, titrePdf, prefixe: "", exemples})`, sans `exercicePython` ni `poids` ;
  `const EXEMPLES` = 2.9 a, 2.9 b, 2.9 j, 2.10 a, 2.10 e, 2.11 h, 2.12 b, 2.12 c, 2.12 e, Javet 2.17 c (§ 13.3, Q6) ; balise GoatCounter ;
  `style.css` puis `composants.css`, aucun `<style>` ; `aria-live` sur `#etat` et `#apercu` ; clavier commun, dernière rangée
  `0 , x =` ; `<details class="card">` fermé « Rappel de la méthode » (E15, les cinq méthodes en liste numérotée, puis le produit nul).
- **Manifeste** : `equations-2e-degre` (10 fichiers du plan, `resoudre`, `apercu`). **Registre** : entrée `"filieres": {}` (note du
  registre complétée) ; `tests/pages/test_accueil.py` : butée (16, 8) et ACC-03 (les liens de l'accueil = les chemins des outils
  **qui ont une filière** : un outil sans filière n'a pas de carte, Q1).
- **Arêtes** (10, `test_imports.ARETES`, chacune avec sa raison) : `equations -> expr / noyau / polynomes / second_degre`,
  `resoudre_eq -> equations / second_degre / sortie / chaine / expr / noyau`. **Écart au plan** : `resoudre_eq -> expr` (aperçu
  syntaxique, `lire_membres` et `tex`) et `resoudre_eq -> noyau` (`ErreurSaisie`, `json_strict`) en plus des quatre du plan ; toutes
  respectent les couches.
- **Tests Python** : `test_noyau.MOTEURS` + `equations.py` ; `test_outils_du_site.test_ordre_de_sys_path` + `equations-2e-degre` ;
  `cas.py` : `CAS_LIMITES["equations-2e-degre"]` (les 52 du § 8 et les 4 « § 6 », sous leur forme d'énoncé), `SAISIES_INVALIDES_EQ`
  (13, une par message de la lecture), `entrees_equations()` (204 : page, § 8, § 6, `RESOLUES`, `NON_RESOLUES`,
  `STRUCTURES_NON_ECRITES`, saisies invalides) ; `test_instantanes` : `resume_resolution`, `instantane_equation` (lecture par
  `equations.analyser`, comme la page), `OUTILS` et `test_equations_2e_degre` → `instantanes/equations-2e-degre.json` (clé = saisie ;
  le JSON provisoire déplacé, `REGENERER=1` sur ce seul test) ; `test_instantanes_resoudre` : entrée, méthode,
  `instantanes/resoudre/equations-2e-degre.json` ; `test_json_strict` (`OUTILS_ENTREES`, `test_equations_2e_degre_json` : resoudre et
  aperçu) ; `test_vocabulaire` (`METHODES`, `test_equations_2e_degre` : sortie et aperçu) ; `test_resoudre_import.EXEMPLE` =
  `x^2-5x-36=0` ; `test_source_unique...PAGES` = `["0", ",", "x", "="]`.
- **Dossier provisoire** `tests/python/donnees/equations-2e-degre/` retiré (git rm). `test_instantanes_second_degre.py` garde
  `test_section_8_complete` et `test_sorties_conformes` (sur le nouveau fichier) et gagne `test_corpus_fige_avec_son_statut` ; ses
  `test_instantanes`, `test_json_strict` et `test_vocabulaire` sont retirés (faits par `test_instantanes.test_equations_2e_degre`,
  `test_json_strict.test_fichiers_d_instantanes_en_json_strict`, `test_vocabulaire.test_instantanes`, qui lisent
  `instantanes/**.json`). Aucun contrôle perdu (oracle : `test_redaction_second_degre`, inchangé).
- **Tests de pages** : `rendu.REDUIT` = 2.10 a, 2.11 h, `x^2+1` ; `rendu.ERREURS` = `x^2+1` (**vérifié** : sans « = », c'est bien une
  erreur, « Écrivez une équation, avec le signe « = ». » ; x² + 1 = 0, lui, donne S = ∅) ; `test_comportement` : `CALCUL` = Javet
  2.17 c (pas de variante), `EXEMPLE` = 2.9 a, `INVALIDE` = `x+y=1` ; `test_rendu.test_equations_2e_degre` ;
  `references/equations-2e-degre.json` (57 entrées, `capturer_references.py equations-2e-degre`, 9 s) ; **nouveau**
  `test_largeurs.test_equations_2e_degre_chaque_exemple` (les 10 exemples, chemin du cours et variante « Par la formule » : balayage
  de 320 à 1100 px, aucune formule hors de sa carte, console vide), car le balayage généré ne lance que le premier exemple (2.9 a,
  sans tableau S-P) et le § 6 demande le tableau S-P et une étiquette longue d'Id. rem.
- **Vérifié sans rien écrire** : `test_largeurs.test_balayage_equations_2e_degre` (généré, `CONNUS` vide, vert) ; `test_style_commun`,
  `test_tableaux_css`, `test_source_unique.MIGREES`, `TestVouvoiement` (page, littéraux de `resoudre_eq.py`), `test_memo_garde`,
  `captures.py` (prend `CALCUL`), `lancer.py`, `dump_sorties.py` (lit manifeste, registre, instantanés et `rendu.entrees`) : rien
  à changer, tous verts.
- **Docs** : `architecture.md` § 1 (second_degre ; l'outil comme exemple des couches), § 4 (oublis relevés : balise et feuilles de la
  page, butée de `sys.path`, `rendu.ERREURS`, registre dès que la page existe avec `"filieres": {}` et la butée du nombre d'outils,
  `test_largeurs` qui ne lance que le premier exemple, `dump_sorties.py`), § 5 (le nouvel outil n'écrit ses nombres que par
  `nombres.approx`/`exact`) ; `taches.md` : N02 (D16).

### Contrôle de la page (`S/tmp/P5/captures_p5.py`, `S/tmp/P5/largeurs_p5.py`)

- Chargement : « Chargement de Python… » puis « Prêt. » en 2,8 s (copie locale de Pyodide ; SymPy chargé après, Q7 accepté).
- Exemples : les 10 boutons, dans l'ordre du § 13.3 ; un clic calcule. Rappel fermé au départ.
- Clavier : 2 x ^ 2 = 8 écrit `2x^2=8`, aperçu `2x^{2} = 8`. Cibles : 44 px de haut au moins (clavier, exemples, Résoudre).
- Messages (vouvoyés ou impersonnels) : `x^2+1` « Écrivez une équation, avec le signe « = ». » ; `x+y=1` « Écrivez une équation avec une
  seule inconnue. » ; `2^x=8` « L'inconnue est en exposant : utilisez l'outil « Exponentielles et logarithmes ». » ;
  `2(x+1)(x+3)=5` « Cette forme d'équation n'est pas traitée par l'outil. » ; `x^4-5x^2+4=0` bicarrée ; `x^3=x+1` hors du cours.
- Variante E12 : 2.10 a affiche « Méthodes du cours » (pressé) et « Par la formule » ; un clic passe à la formule (Δ = 169…), puis
  retour. Console : seulement le favicon absent (filtré par les tests).
- Largeurs (JS du balayage commun) : 18 équations (les 10 exemples, (x + 1)(x + 3) = 15, x⁴ − 16, 2.12 h, 2.9 k, Az 4.1 d, x² + 1000x − 1,
  Javet 2.17 d et e), chemin du cours et variante, 320 à 1100 px : **aucune faute**.
- Aucune requête hors de la machine : les tests de pages passent par l'intercepteur (copies locales ; GoatCounter servi vide).

### Captures à 390 px (`S/captures/P5/`)

`2.11-h-390-clair.png`, `2.11-h-390-sombre.png`, `2.10-a-390-clair.png`, `javet-2.17-c-390-clair.png`, `2.12-e-390-clair.png`,
`x+1-x+3-egal-15-390-clair.png` (carte « Résolution » seule, corrigé complet). Regardées : rien ne déborde (page sans défilement
horizontal à 320, 360 et 390 px) ; cadres D29 lisibles en clair et en sombre (x = −4, △ = −7, ligne ✓ du S-P, Δ = 12, S) ; tableau
S-P lisible (filets, ✓). **À juger** : à 390 px, la ligne de Δ de Javet 2.17 c se coupe dans « 4 · 1 · (−2) » et celle de √Δ après
« √Δ = » (rangées sans lien, coupure de KaTeX : rien ne déborde) ; une seule carte, donc « Étape 1 / 1 » et « Étape suivante »
grisé (questions 36 et 37 de suivi.md).

### Suite d'avant commit et dump

- `PROCESSUS_PAGES=4 python3 tests/lancer.py complet --rapport S/rapports/P5` : **code 0** (console `S/rapports/P5-console.log`).
  Python 1 667 collectés, 1 666 passés + 1 xfail (celui d'avant le chantier), 128 686 sous-tests, 94,0 s ; pages 154 passés,
  2 520 sous-tests, 333,3 s. Aucun échec instable.
- `comparer_listes.py S/rapports/P4b S/rapports/P5` : tests Python nouveaux (méthodes `test_equations_2e_degre` des instantanés, du JSON
  strict et du vocabulaire, `test_hors_du_cours_seulement_si_vrai`, `test_corpus_fige_avec_son_statut`), 3 disparus
  (`test_instantanes_second_degre` : `test_instantanes`, `test_json_strict`, `test_vocabulaire`, justifiés dans suivi.md, « Tests
  renommés ») ; pages : 3 nouveaux (`test_balayage_equations_2e_degre`, `test_equations_2e_degre_chaque_exemple`,
  `test_rendu::test_equations_2e_degre`). Sous-tests : **aucune baisse** (hausses : un outil de plus dans chaque test par outil ;
  `test_vocabulaire::test_instantanes` 1 511 → 1 919).
- **Dump** : `dump_sorties.py S/dumps/P5 --processus 6` (19 fichiers, 4 556 sorties, 4 s), `diff -r --exclude=temps S/dumps/depart
  S/dumps/P5` : seulement `Only in …/P5/apercu: equations-2e-degre.txt`, `Only in …/P5/resoudre: equations-2e-degre.txt` et, dans
  `index.txt`, les deux lignes de ces fichiers (204 entrées chacun) ; **aucune autre différence** (les 17 fichiers et 4 148 sorties
  des outils existants identiques à l'octet).
- xfail stricts : aucun ajouté, aucun retiré.

### Temps

Voir « Temps » ci-dessous (P5).

## R1 — une carte par étape

Correction de relecture (question 36 de suivi.md, tranchée par l'enseignant le 06.11.2026 : « une carte par étape », dévoilées une à
une par « Étape suivante » ; la suite des cartes redonne la chaîne entière). Seul le nouvel outil change.

### Plan

1. **Relevé des étapes** (`S/tmp/R1/etapes.py`, corpus de `cas.entrees_equations`, chemin du cours et variante) : toutes les étapes
   ont des lignes, sauf `factoriser`/`FORMULE` **vide** (variante « Par la formule », 72 cas) ; quelques étapes n'ont **aucune
   rangée-ligne** (seulement des lignes pleine largeur) : tentative en échec (S-P avec son tableau, tâtonnement), phrase de choix de
   la formule (coefficients non entiers), « Δ < 0 : … » (`delta_nombre` sans ⇔).
2. **Moteur** (`moteur/second_degre.py`) : `cartes(resolution)` = une carte par étape, `[{etapes: [indices], blocs}]` ; une étape
   vide rejoint la carte de l'étape suivante (la précédente si elle est la dernière) ; une carte dont la première rangée-ligne
   commence par ⇔ reçoit en membre de gauche le pivot de son segment (le dernier élément écrit, `rangees(segment)[0]`, comme Exp-log
   écrit l'équation d'arrivée en tête de la carte suivante, une seule fois : colonne de gauche de la première ligne, R5) ; sinon (la
   première carte, qui porte l'énoncé ; lignes de Δ sans lien) rien n'est ajouté. Bloc : `bloc_rangees(lignes, membre_gauche=True)`.
   Une étape **sans rangée-ligne** : une chaîne serait refusée par `sortie.valider` (« au moins une ligne {lien, expr} ») et A4
   interdit le HTML dans un bloc texte : ses lignes deviennent des blocs `texte` (le texte tel quel, TeX entre \( \), comme la ligne
   ≈ et les textes des autres outils) et `tableau_essais` ; question nouvelle pour l'enseignant (autre possibilité : la joindre à la
   carte suivante). `blocs_solution(resolution)` : S (`resultat_lim`) et la ligne ≈ ; `blocs` (chaîne entière) inchangé, garde
   l'invariant du § 5.
3. **Adaptateur** (`resoudre_eq.py`) : cartes « Étape k » avec un badge court (comme Exp-log et Factorisation ; noms du rappel de la
   page) : Ramener à 0, Développer, Isoler x, Mise en évidence, Identité remarquable, Somme-Produit, Tâtonnement, Formule,
   Discriminant (`delta_valeur`), Valeurs de x (`delta_nombre`), Produit nul ; puis la carte « Solution » (S, ligne ≈), normale
   (§ 13.3, pas de double cadre). Même découpage pour « Par la formule ». Erreurs : une seule carte, inchangées.
4. **Tests** : invariant du § 5 adapté (JSON) : les rangées des cartes mises bout à bout = les rangées de la chaîne entière, membre
   de gauche mis à part ; chaque carte à rangée-ligne est un bloc « chaine » valide, son membre de gauche est le dernier élément ⇔
   écrit avant elle (ou l'énoncé) ; une carte de textes seulement pour une étape sans rangée-ligne ; chaque étape non vide a sa carte,
   dans l'ordre ; sur tout le corpus, les variantes et les polynômes générés. Textes de 2.11 h (cinq cartes) et des badges.
   Instantanés : `resume_resolution` fige les cartes (et la solution) au lieu du bloc unique ; `test_sorties_conformes` sur les
   cartes. Pages : test de comportement des cinq cartes de 2.11 h (« Étape 1 / 5 », un clic : 2 / 5) ; `test_largeurs` inchangé
   (il clique déjà « Tout afficher »). Références de pages par `capturer_references.py equations-2e-degre`.
5. Captures à 390 px (2.11 h et 2.10 a « Tout afficher », 2.11 h après un clic), suite complète, dump, temps natif, commit.

### Réalisé

- **`moteur/second_degre.py`** : `cartes(resolution)` (plan, point 2) et `blocs_solution(resolution)` ; `blocs` inchangé (même
  sortie, la chaîne entière). **Écart trouvé par le test d'invariant** : une carte qui commence par une ligne de Δ suivie d'un ⇔
  (Δ = 0 dans un produit, variante de 2x³ − 4x² + 2x = 0 : « x = −b/2a = 1 », puis « ⇔ x = 0 ou x = 1 ») aurait vu `bloc_rangees`
  mettre la ligne de Δ en membre de gauche (« x = −b/2a = 1 ⇔ x = 0 ou x = 1 », faux) : le membre de gauche n'est permis que pour le
  pivot ajouté ou l'énoncé (test dédié).
- **`equations-2e-degre/resoudre_eq.py`** : `TITRES`, `titre(etape, x)` (KeyError pour une étape inconnue), `_cartes(res, x)` :
  « Étape k » + badge, puis « Solution ». Badges sur le corpus (241 résolutions, 645 cartes d'étape) : Produit nul 135,
  Discriminant 110, Valeurs de x/t/y/z/u/s 110, Ramener à 0 73, Identité remarquable 55, Mise en évidence 52, Somme-Produit 44,
  Tâtonnement 26, Développer 21, Formule 13, Isoler x 6.
- **Tests Python** (`test_redaction_second_degre.TestInvariants`, 3 nouveaux) : `test_une_carte_par_etape` (corpus, variantes et 196
  polynômes générés : concaténation = chaîne entière en JSON, membre de gauche mis à part ; carte à rangée-ligne = un bloc « chaine »
  valide, membre de gauche = dernier élément ⇔ écrit ou l'énoncé, écrit une fois ; carte de textes seulement pour une étape sans
  rangée-ligne, sans HTML (`sortie._sans_html`) ; chaque étape dans une carte, dans l'ordre, aucune carte vide ; `blocs_solution`),
  `test_cartes_de_2_11_h`, `test_carte_d_une_etape_sans_rangee` (Javet 2.17 c, 2.12 b, Javet 2.17 e, 3t² + 5t + 12, Δ = 0 du
  produit). `test_instantanes.resume_resolution` fige `cartes` et `solution` au lieu de `blocs` ;
  `test_instantanes_second_degre.test_sorties_conformes` construit la sortie des cartes figées.
- **Test de pages** : `test_comportement.test_equations_2e_degre_une_carte_par_etape` (2.11 h : « Étape 1 / 5 », un clic : 2 / 5 et
  deux badges, « Tout afficher » : les cinq titres et badges, membres de gauche des quatre cartes ; variante : Ramener à 0,
  Discriminant, Valeurs de x, Solution). `test_soc07_etapes`, `test_bouton_etape_suivante_flottant` (CALCUL = Javet 2.17 c, maintenant
  6 cartes) et `test_largeurs` (il clique « Tout afficher ») : rien à changer, verts.
- **Instantanés et références** (régénérés : `REGENERER=1` sur `test_equations_2e_degre` de `test_instantanes` et
  `test_instantanes_resoudre` ; `capturer_references.py equations-2e-degre`, 57 entrées). Recoupés entrée par entrée
  (`S/tmp/R1/comparer.py`) : mêmes 204 clés ; erreurs et statuts identiques ; pour chaque résolution (241), les rangées des cartes
  mises bout à bout = l'ancienne chaîne (membre de gauche mis à part), la carte « Solution » = les anciens blocs après la chaîne,
  tous les autres champs identiques. Exemples avant / après (sortie de la page) :
  - **2.11 h** `4x^2+2x=56` : avant, une carte « Résolution » (la chaîne, S) et « Étape 1 / 1 » ; après, « Étape 1 / 5 » : Étape 1
    Ramener à 0 (`4x² + 2x = 56` ⇔ `4x² + 2x − 56 = 0`), Étape 2 Mise en évidence (`4x² + 2x − 56 = 0` ⇔ `2(2x² + x − 28) = 0` ME),
    Étape 3 Tâtonnement (les trois phrases, puis `2(2x² + x − 28) = 0` ⇔ `2(x + 4)(2x − 7) = 0`), Étape 4 Produit nul
    (`2(x + 4)(2x − 7) = 0` ⇔ … produit nul ⇔ `x = −4 ou x = 7/2`), Solution (S). Variante : Ramener à 0, Discriminant (Δ = … = ⟦900⟧),
    Valeurs de x (√Δ, x₁, x₂), Solution.
  - **Javet 2.17 c** `2x^2-4x-4=0` : avant, une carte ; après, Mise en évidence, Somme-Produit (phrase, tableau, « Aucun couple ne
    convient : on utilise la formule. », blocs texte et tableau), Produit nul (`2(x² − 2x − 2) = 0` ⇔ 2 = 0 impossible ou …), Discriminant
    (Δ = … = ⟦12⟧, sans membre de gauche), Valeurs de x (√Δ, x₁, x₂, puis ⇔ x = 1 − √3 ou x = 1 + √3), Solution (S, ligne ≈).
  - **(x + 2)(x − 2) = x² − 4** : avant, une carte ; après, Développer (… ⇔ x² − 4 = x² − 4), Ramener à 0 (`x² − 4 = x² − 4` ⇔ −4 = −4,
    « Cette égalité est vraie pour tout nombre réel. »), Solution (S = ℝ).

### Captures à 390 px (`S/captures/R1/`, clair ; `S/tmp/R1/captures_r1.py`)

`2.11-h-tout-390-clair.png` (« Étape 5 / 5 »), `2.11-h-apres-un-clic-390-clair.png` (« Étape 2 / 5 », bouton flottant),
`2.10-a-tout-390-clair.png`, `javet-2.17-c-tout-390-clair.png`. Regardées : rien ne déborde (aucun défilement horizontal à 320, 360
et 390 px ; seuls les éléments MathML cachés de KaTeX, rognés, sortent du cadre ; aucun bloc qui défile, `S/tmp/R1/defile.py`) ; dans
chaque carte, les ⇔ ont le même bord droit (mesuré) ; à 390 px, le membre de gauche passe seul sur sa ligne, au-dessus du ⇔ (règle
commune d'un conteneur étroit, comme en P5). À juger (question 40) : textes de la carte Somme-Produit de Javet 2.17 c un peu plus
grands que ceux d'une chaîne (bloc texte : 1,06 rem ; texte d'une chaîne étroite : 0,92 rem).

### Temps (`S/tmp/R1/temps_r1.py`, même mesure que P5, python3 natif 3.14.4, 3e de trois tours)

`resoudre_eq.resoudre_json` sur le corpus complet de l'outil (204 entrées) **290,7 ms** (P5 : 276 ms, + 5 %), la plus longue
**4,1 ms** (2x⁴ + x³ − 28x² = 0 ; P5 : 3,9 ms) ; § 8 et § 6 (56) 101,7 ms (P5 : 96,7 ms) ; `resoudre_equation` seule 66,8 ms
(inchangé) ; `apercu_json` 36,0 ms ; pire cas des bornes 93 ms (P5 : 89 ms). Aucune hausse de plus de 50 %, tout sous 0,1 s.

### Suite d'avant commit et dump

- `PROCESSUS_PAGES=4 python3 tests/lancer.py complet --rapport S/rapports/R1` : **code 0** (console `S/rapports/R1-console.log`).
  Python 1 670 collectés, 1 669 passés + 1 xfail (celui d'avant le chantier), 129 187 sous-tests, 100 s ; pages 155 passés, 2 520
  sous-tests, 335 s. Aucun échec instable.
- `comparer_listes.py S/rapports/P5 S/rapports/R1` : 3 tests Python nouveaux (`TestInvariants` : `test_une_carte_par_etape`,
  `test_cartes_de_2_11_h`, `test_carte_d_une_etape_sans_rangee`), 1 de pages (`test_equations_2e_degre_une_carte_par_etape`) ; aucun
  disparu ni renommé ; sous-tests : aucune baisse (`test_vocabulaire::TestVouvoiement::test_litteraux_des_moteurs` 9 772 → 9 836).
- **Dump** : `dump_sorties.py S/dumps/R1 --processus 6` (19 fichiers, 4 556 sorties, 4 s) ; `diff -r --exclude=temps S/dumps/depart
  S/dumps/R1` : seulement `Only in …/R1/apercu: equations-2e-degre.txt`, `Only in …/R1/resoudre: equations-2e-degre.txt` et les deux
  lignes d'`index.txt` ; **aucune autre différence** (outils existants identiques à l'octet). Par rapport à P5, seul
  `resoudre/equations-2e-degre.txt` change (les cartes) ; l'aperçu est identique.
- xfail stricts : aucun ajouté, aucun retiré.

## Contrôles du chef d'orchestre

- P0 `0fd0060` : verifier ACCEPTÉ (Python 1 494 / 106 768 sous-tests, pages 145 / 2 421, identiques à la nouvelle référence) ; rapide --depuis HEAD~1 : 23 passés, 245 sous-tests, 3 s (fumée + docs). Échec instable de `test_comportement::test_soc04_parametre_f` (ensemble-definition, `#cartes` absent : page pas encore chargée) au 1er lancement de référence : accepté par le chef comme instabilité de chargement (relancé seul vert, deux suites complètes vertes ensuite, aucune sortie en cause, Python vert) ; question 8 de suivi.md. Branche poussée.
- P1 `5f21ac0` : verifier ACCEPTÉ (Python 1 534 / 112 356 sous-tests, 1 baisse justifiée test_exp_log::…::test_aucun_texte_du_fichier_ne_tutoie 960 → 957 ; pages 145 / 2 421 identiques) ; rapide --depuis HEAD~1 : Python 1 489 passés + 1 xfail, 112 300 sous-tests (95 s), pages 145 passés, 1 256 sous-tests (306 s), mur 6 min 44 ; dump identique au départ (P1). Branche poussée.
- P2a `5b9254c` : verifier ACCEPTÉ (Python 1 548 / 112 699 sous-tests, pages 151 / 2 435, ajouts seulement, baisse de P1 toujours justifiée) ; rapide --depuis HEAD~1 : Python 1 327 passés + 1 xfail, 97 492 sous-tests (89 s), pages 151 passés, 1 270 sous-tests (324 s), mur 6 min 55 ; dump identique au départ (P2a). Capture 390 clair regardée par le chef : cadres D29 lisibles, rien ne déborde. Branche poussée.
- P2b `a52b58a` : verifier ACCEPTÉ (Python 1 607 collectés, 1 584 passés + 23 xfail dont 22 stricts P3/P4a/P4b, 122 989 sous-tests ; pages 151 / 2 435) ; rapide --depuis HEAD~1 : 385 passed, 23 xfailed, 28288 subtests passed in 25.14s ; 151 passed, 1270 subtests passed in 324.52s (0:05:24) (code=0 mur=351s) ; dump identique au départ (P2b). Texte rendu de 2.11 h (forme développée) relu par le chef : conforme au § 7 hors étape « ramener » (P3). Branche poussée.
- P3 `8e838be` : verifier ACCEPTÉ (Python 1 641 collectés, 1 628 passés + 13 xfail, 124 615 sous-tests, 2 baisses justifiées ; pages 151 / 2 435 identiques) ; rapide --depuis HEAD~1 : 1003 passed, 13 xfailed, 97209 subtests passed in 79.13s (0:01:19) ; 151 passed, 1270 subtests passed in 324.21s (0:05:24) (code=0 mur=405s) ; dump identique au départ (P3). Branche poussée.
- P4a `06f3daf` : verifier ACCEPTÉ (Python 1 652 collectés, 1 644 passés + 8 xfail, 125 662 sous-tests ; pages 151 / 2 435 identiques ; renommage justifié test_structures_laissees_a_p4a → test_structures_sans_developper, hors référence) ; rapide --depuis HEAD~1 : 445 passed, 8 xfailed, 30771 subtests passed in 26.08s ; 151 passed, 1270 subtests passed in 323.99s (0:05:23) (code=0 mur=351s) ; dump identique au départ (P4a). Branche poussée.
- P4b `88ea64e` : verifier ACCEPTÉ (Python 1 664 collectés, 1 663 passés + 1 xfail d'avant le chantier, 127 242 sous-tests ; pages 151 / 2 435 identiques ; renommage justifié test_formes_pas_encore_traitees → test_aucun_statut_temporaire, hors référence) ; rapide --depuis HEAD~1 : 464 passed, 1 xfailed, 32295 subtests passed in 24.10s ; 151 passed, 1270 subtests passed in 324.85s (0:05:24) (code=0 mur=349s) ; dump identique au départ (P4b). Décision du chef sur la question 29 : le message « hors du cours » donné à des équations du cours que l'outil n'écrit pas serait faux à l'écran (CLAUDE.md, « rien de faux », prime sur decisions.md) ; corrigé en tête de P5 par un message vrai, question gardée pour l'enseignant. Branche poussée.
- P5 `f65131b` : verifier ACCEPTÉ (Python 1 667 collectés, 1 666 passés + 1 xfail, 128 686 sous-tests ; pages 154 / 2 520 ; 3 tests provisoires de test_instantanes_second_degre retirés, hors référence, justifiés) ; rapide --depuis HEAD~1 : 1666 passed, 1 xfailed, 128686 subtests passed in 112.83s (0:01:52) ; 154 passed, 1301 subtests passed in 328.82s (0:05:28) (code=0 mur=445s) ; dump : seuls les fichiers du nouvel outil s'ajoutent. Adaptation de test_acc03 (outil sans filière exclu des cartes) acceptée par le chef : couverture des outils existants inchangée, imposée par l'option A. Capture 2.11 h à 390 px regardée. Branche poussée.
- Fin, sur `f65131b` : `complet --rapport …/rapports/FIN` code 0 (Python 1 666 passés + 1 xfail, 128 686 sous-tests, 113 s ; pages 154 passés, 2 520 sous-tests, 332 s ; mur 7 min 28) ; verifier ACCEPTÉ ; `comparer_listes tests/reference FIN` : seulement des ajouts (173 tests Python, 9 de pages), des hausses de sous-tests et la baisse justifiée de `test_exp_log::…::test_aucun_texte_du_fichier_ne_tutoie` (960 → 955) ; `comparer_listes P5 FIN` : identique. Même suite avec `MEMO=0` (`…/rapports/FIN-memo0`) : code 0, verifier ACCEPTÉ, listes identiques à FIN nom par nom (Python 140 s, pages 331 s, mur 7 min 54). Dump FIN identique à P5 ; par rapport au départ, seuls `apercu/equations-2e-degre.txt`, `resoudre/equations-2e-degre.txt` et leurs deux lignes d'`index.txt` s'ajoutent.

## Temps

Temps natif de `resoudre_equation` sur le corpus § 8 (objectif < 0,1 s) : **sans objet en P0** (la fonction n'existe pas encore).

**P1** (`resoudre_equation` n'existe pas encore : mesuré sur son équivalent, `second_degre.chemin` puis `approx_garantie` de chaque
solution ; script `S/tmp/temps_p1.py`, Python natif 3.12, 3e de trois tours) : corpus § 8 développé, § 6 et § 7 (69 entrées de
`test_second_degre.CORPUS`) **16,6 ms en tout**, la plus longue 0,45 ms (x⁴ − 16) : bien sous 0,1 s par équation. Pire cas permis
par les bornes : x² + 999 999x − 499 997 (Δ = 999 999 999 989, premier, `noyau.squarefree` jusqu'à 10⁶) **105 ms** ; au-delà de 10¹²,
message des bornes (question 9 de suivi.md).

**P2a** (même mesure, `S/tmp/temps_p1.py` ; P2a ne touche pas `second_degre`) : 69 entrées, **16,4 ms en tout**, la plus longue
0,45 ms (x⁴ − 16) ; pire cas des bornes 91 ms. Aucune hausse.

**P2b** (`S/tmp/temps_p2b.py`, python3 natif 3.14.4, 3 tours ; `resoudre_equation`, variante « formule » quand elle est proposée,
et `blocs`) : 93 entrées (les 72 de `corpus_second_degre.P2B` et les 21 formes `A_VENIR`, qui répondent `non_traite`) **77 ms en tout**
(3e tour), la plus longue 1,6 ms (−9x² − 12x + 12 = 0, avec sa variante) : bien sous 0,1 s par équation. Pire cas des bornes :
x² + 999 999x − 499 997 = 0 **88 ms** (P1 : 91 ms pour le seul calcul ; la rédaction ne compte pas). Aucune hausse au-delà de 0,1 s.

**P3** (`S/tmp/temps_p3.py`, python3 natif 3.14.4, 3 tours ; `equations.analyser`, puis `resoudre_equation`, variante « formule »
quand elle est proposée, et `blocs`) : 119 entrées (les 98 de `corpus_second_degre.RESOLUES` et les 21 formes `A_VENIR`, dont les
11 de P4a/P4b répondent `non_traite`) **149 ms en tout** (3e tour), la plus longue **2,6 ms** (x² − x(x + 1) + 3x² = 4 : quatre lignes
de développement, tâtonnement, variante) : bien sous 0,1 s par équation. Pire cas des bornes : x² + 999 999x − 499 997 = 0 **88 ms**
(comme en P2b). Aucune hausse au-delà de 0,1 s (P2b : 77 ms pour 93 entrées sans l'analyse de la saisie ; la plus longue 1,6 ms).

**P4a** (`S/tmp/temps_p4a.py`, même mesure que P3, python3 natif 3.14.4, 3 tours) : 162 entrées (les 131 de
`corpus_second_degre.RESOLUES`, dont les 33 formes structurées de `P4A` ; les 21 formes `A_VENIR`, dont les 6 de P4b répondent
`non_traite` ; les 10 `STRUCTURES_NON_ECRITES`, `non_traite`) **212 ms en tout** (3e tour), la plus longue **2,6 ms**
(x² − x(x + 1) + 3x² = 4, comme en P3) : bien sous 0,1 s par équation. Pire cas des bornes : x² + 999 999x − 499 997 = 0 **98 ms**
(P3 : 88 ms ; écart de mesure, chemin inchangé). Aucune hausse au-delà de 0,1 s.

**P4b** (`S/tmp/temps_p4b.py`, même mesure que P4a, python3 natif 3.14.4, 3 tours) : 212 entrées (les 167 de
`corpus_second_degre.RESOLUES`, dont les 36 de `P4B` ; les 16 `NON_RESOLUES` ; les 21 formes `A_VENIR`, toutes résolues ; les 8
`STRUCTURES_NON_ECRITES`, « hors_cours ») **301 ms en tout** (3e tour), la plus longue **3,9 ms** (2x⁴ + x³ − 28x² = 0 : ME de x²,
tâtonnement, variante) : bien sous 0,1 s par équation. Pire cas des bornes : x² + 999 999x − 499 997 = 0 **88 ms** (P4a : 98 ms ;
écart de mesure, chemin inchangé). Aucune hausse au-delà de 0,1 s (P4a : 212 ms pour 162 entrées, la plus longue 2,6 ms).

**P5** (`S/tmp/temps_p5.py`, python3 natif 3.14.4, 3 tours, 3e tour) : `equations.analyser` + `resoudre_equation` sur le § 8 et le
§ 6 (56 saisies) **67,8 ms en tout**, la plus longue 2,0 ms ((x − 1)(2 − x) = (x − 1)(x + 3)) ; `resoudre_eq.resoudre_json` (analyse,
résolution, variante « formule », blocs, sortie, JSON) sur les mêmes 56 : **96,7 ms**, la plus longue 2,8 ms (x³ − x = 0) ; sur le
corpus complet de l'outil (204 entrées, `cas.entrees_equations`) : **276 ms**, la plus longue **3,9 ms** (2x⁴ + x³ − 28x² = 0) ;
`apercu_json` sur les 204 : 36 ms, la plus longue 0,3 ms. Pire cas des bornes (x² + 999 999x − 499 997 = 0, `resoudre`) : **89 ms**.
Bien sous 0,1 s par équation ; aucune hausse (P4b : 301 ms pour 212 entrées, la plus longue 3,9 ms).

Temps natifs des outils existants au départ (`S/dumps/depart-p1/temps/temps.json`, `--processus 1`, sur b72fe2e ; somme des appels de
`resoudre_json` et plus long appel ; 12,9 s de mur) :

| Outil | Filière | Entrées | Total (s) | Plus long (s) | Entrée la plus longue |
|---|---|---|---|---|---|
| derivee-variations | — | 33 | 0,266 | 0,080 | `e^((-2x^2+3x-1)/(3x-6))` |
| ensemble-definition | — | 42 | 0,032 | 0,022 | `sqrt(ln(x)-x+2)` |
| etude-complete | — | 22 | 1,996 | 0,280 | `e^((x^2+x-2)/(6x-12))` |
| exponentielles-logarithmes | C | 914 | 0,919 | 0,005 | `ln(ln(x^2))=1` |
| exponentielles-logarithmes | M | 914 | 0,780 | 0,003 | `ln(ln(x^2))=1` |
| factorisation | — | 309 | 1,870 | 0,064 | `x^3 - 9x^2 + 23x - 15` |
| limites-asymptotes | — | 66 | 5,916 | 1,203 | `x*e^x/(1-e^x)` |
