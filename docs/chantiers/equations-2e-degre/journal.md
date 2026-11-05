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

## P3 — saisie

## P4a — formes structurées

## P4b — degrés ≠ 2 et reste du corpus

## P5 — l'outil

## Contrôles du chef d'orchestre

- P0 `0fd0060` : verifier ACCEPTÉ (Python 1 494 / 106 768 sous-tests, pages 145 / 2 421, identiques à la nouvelle référence) ; rapide --depuis HEAD~1 : 23 passés, 245 sous-tests, 3 s (fumée + docs). Échec instable de `test_comportement::test_soc04_parametre_f` (ensemble-definition, `#cartes` absent : page pas encore chargée) au 1er lancement de référence : accepté par le chef comme instabilité de chargement (relancé seul vert, deux suites complètes vertes ensuite, aucune sortie en cause, Python vert) ; question 8 de suivi.md. Branche poussée.
- P1 `5f21ac0` : verifier ACCEPTÉ (Python 1 534 / 112 356 sous-tests, 1 baisse justifiée test_exp_log::…::test_aucun_texte_du_fichier_ne_tutoie 960 → 957 ; pages 145 / 2 421 identiques) ; rapide --depuis HEAD~1 : Python 1 489 passés + 1 xfail, 112 300 sous-tests (95 s), pages 145 passés, 1 256 sous-tests (306 s), mur 6 min 44 ; dump identique au départ (P1). Branche poussée.

## Temps

Temps natif de `resoudre_equation` sur le corpus § 8 (objectif < 0,1 s) : **sans objet en P0** (la fonction n'existe pas encore).

**P1** (`resoudre_equation` n'existe pas encore : mesuré sur son équivalent, `second_degre.chemin` puis `approx_garantie` de chaque
solution ; script `S/tmp/temps_p1.py`, Python natif 3.12, 3e de trois tours) : corpus § 8 développé, § 6 et § 7 (69 entrées de
`test_second_degre.CORPUS`) **16,6 ms en tout**, la plus longue 0,45 ms (x⁴ − 16) : bien sous 0,1 s par équation. Pire cas permis
par les bornes : x² + 999 999x − 499 997 (Δ = 999 999 999 989, premier, `noyau.squarefree` jusqu'à 10⁶) **105 ms** ; au-delà de 10¹²,
message des bornes (question 9 de suivi.md).

**P2a** (même mesure, `S/tmp/temps_p1.py` ; P2a ne touche pas `second_degre`) : 69 entrées, **16,4 ms en tout**, la plus longue
0,45 ms (x⁴ − 16) ; pire cas des bornes 91 ms. Aucune hausse.

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
