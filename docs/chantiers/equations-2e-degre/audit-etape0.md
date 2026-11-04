# Équations du 2e degré, étape 0 : rapport d'audit (aucun autre fichier du dépôt modifié)

Date : 04.11.2026. Ce rapport est le seul fichier écrit ; il n'y a ni branche ni commit.

**Méthode**
- L'inventaire (point 1) a été fait par trois sous-agents en lecture seule : A (moteur et outils), B (documentation) et C (tests). Leurs rapports sont résumés ici.
- Le corrigé a été lu en entier. Le moteur a été lancé avec `uv` (Python 3.12, SymPy 1.13.3), au moyen de scripts placés dans le bloc-notes de la session, hors du dépôt.
- Les valeurs ont été contrôlées par un oracle mpmath écrit à la main, à 30 ou 40 chiffres. Il n'utilise ni le parseur ni SymPy :
  - `polyroots` sur les coefficients recopiés à la main ;
  - pour les équations rationnelles et à racines, un balayage de [−60 ; 60] suivi de `findroot` sur le résidu.
- Chaque commande a duré moins de 5 minutes.

## 0. Constats préalables (à régler avant toute partie)

1. **La référence n'est pas où la consigne l'attend.**
   - `docs/reference/equations-2e-degre/` n'existe pas.
   - Le corrigé se trouve dans `docs/chantiers/equations-2e-degre/`, qui n'est pas suivi par git et **n'est pas ignoré** : un `git add` du dossier publierait les PDF, dont un polycopié de 163 pages sous droits (J.-Ph. Javet).
   - Il faut les déplacer dans `docs/reference/equations-2e-degre/` (D0).
   - Les quatre PDF :

     | Fichier | Contenu |
     |---|---|
     | `Id_rem.pdf` | Corrigé de l'enseignant, exercices 2.9 (identités remarquables) et 2.10 (Somme-Produit). 8 p. |
     | `tatonement.pdf` | Corrigé de l'enseignant, exercices 2.11 (tâtonnement) et 2.12 (mélange). 7 p. |
     | `1MRe Notion elem copie.pdf` | Polycopié Javet 1MRenf (163 p.). Chap. 2, § 2.2 à 2.4 : les 5 méthodes, la formule, Δ, les inéquations, les équations « maquillées ». Chap. 3 : degré 3 et plus. Chap. 4 : équations rationnelles. Annexe A.2 à A.4 : réponses seules, sans rédaction. |
     | `1M_Algebre_Az_2019 (glissé(e)s).pdf` | Énoncés 4.1 à 4.4 (ED + S : polynomiales, rationnelles, à racines, formules littérales), sans corrigé. 1 p. |

2. **`docs/methode-chantiers.md` n'existe pas.**
   - Il est absent du dépôt et de l'historique, alors qu'il est cité dans `docs/chantiers/tests-rapides/decisions-tests-rapides.md` (l. 4, 32 et 50).
   - Ce qui en tient lieu :
     - CLAUDE.md ;
     - le « Gabarit d'une tâche d'outil », dans `docs/taches.md`, Phase F ;
     - les modèles d'audit `etude-complete/audit-etape0.md` et `limites-asymptotes/audit-etape0.md` ;
     - après l'audit, un `decisions.md` validé par vous. L'ordre de priorité est CLAUDE.md > decisions > audit.
   - J'ai suivi ces modèles.

3. **Aucun outil n'accepte aujourd'hui une équation du 2e degré « nue ».**

   | Saisie | Outil | Réponse |
   |---|---|---|
   | `x^2=16` | Exp-log | « Cet outil traite les équations exponentielles et logarithmiques. » |
   | `x^2+7x=18` | Factorisation | « Écrivez seulement l'expression à factoriser (sans « = »). » |

   Les briques de résolution existent, mais elles sont enfouies dans quatre outils, avec trois rédactions concurrentes.

4. **Défaut vu en passant (hors chantier ; ticket à ouvrir).** Exp-log, filière C, variante par défaut, `2^(x^2-5x)=2^(-6)` :
   - la page affiche « x² − 5x − (−6) = 0 », puis « Δ = (−5)² − 4·1·(−−6) = 25 + 4(−6) » ;
   - la ligne Δ est donc mal écrite (double signe moins) ;
   - le résultat final reste juste (« on retrouve x = 2 ou x = 3 »).

   Avec `1/64` au second membre, Δ reste écrit avec des log, sans être calculé. À vérifier : pourquoi la variante « même base » n'est pas celle par défaut, ici comme pour `3^(x^2)=3^(x+6)`. Ce défaut relève de la règle « rien de faux à l'écran ».

5. **Piège des tests relevé par C.** `tests/lancer.py::fichiers_modifies` découpe la sortie de git avec `.split()` : les fichiers dont le nom contient des espaces ou des caractères non ASCII sont ignorés en silence par `rapide`. C'est le cas de deux des PDF. Ticket hors chantier.

## Synthèse

1. **Toutes les valeurs du corrigé sont justes (oracle).**
   - 2.9 a–l, 2.10 a–j, 2.11 a–j, 2.12 a–h ;
   - côté Javet : 2.17 a–f, ex. 13, bicarrées 2.31 et 2.32, ex. 22 et 23, racines 2.33 et ex. 24 et 25, rationnelles 4.6 et ex. 8 ;
   - Az 4.1 et 4.2 (sans corrigé) : les valeurs de l'oracle sont notées au § 3.

   Aucune erreur dans le matériel de référence.
2. **Le moteur trouve toujours les bonnes factorisations et les bons zéros, mais pas avec les méthodes du corrigé** :
   - **aucun tâtonnement** : pour a ≠ 1, l'outil Factorisation passe à Δ par décision écrite (FA-09, commentaire de `trinome_methodes`). Le corrigé, lui, fait un tâtonnement, y compris sur des fractions (2.12 b) ;
   - `x² − 5` est traité par Δ, alors que le corrigé utilise l'identité remarquable avec B = √5 ;
   - **pas de tableau « produit | somme »** pour Somme-Produit ;
   - **pas de ligne « Vérification : 2AB = … ✓ »** ;
   - **pas de chaîne d'équivalences « … = 0 ⇔ … »**. La Factorisation factorise, elle ne résout pas.
3. **Le corrigé a une forme très régulière, qu'une brique peut produire** :
   1. on ramène à « … = 0 » ;
   2. on essaie dans l'ordre ME, Id. rem., S-P (a = 1), tâtonnement (a ≠ 1) ;
   3. on écrit le produit nul : « c = 0 (impossible) ou facteur = 0 ou … », avec des solutions dans l'ordre des facteurs ;
   4. on termine par `S = {… ; …}` encadré, en ordre croissant.

   La formule (Δ) n'apparaît que dans le polycopié, en 5e méthode, avec Δ < 0 ⇒ S = ∅.
4. **La meilleure base est le couple `_resoudre_polynome` + objets `Chaine` d'Exp-log**, qu'il faut extraire dans `moteur/`. On y ajoute les méthodes de factorisation rédigées « à la manière du corrigé ».

   Il ne faut **pas** brancher les autres outils dans ce chantier : environ 50 + 43 entrées d'instantanés pour EL, 68 pour FA, 10 pour EC, 7 pour ED et 5 pour DV bougeraient.

## 1. Inventaire de l'existant

### 1.1 Briques du moteur (rapport A, vérifié par des essais)

| Brique | Où | Ce qu'elle couvre | Rédaction actuelle | Qui l'utilise | Ce qu'un changement casserait |
|---|---|---|---|---|---|
| `_resoudre_polynome`, `_racines_du_second_degre`, `_une_seule_solution`, `tex_solution` | `exponentielles-logarithmes/exp_log.py` (l. 1375 à 1470 environ) | A = B de degré ≤ 2. Identité / égalité fausse, 1er degré rationnel, **2e degré à coefficients entiers seulement** (`_Hors` sinon). a·x² = 0 ⇔ x = 0. Somme-Produit implicite si a = 1 et Δ carré, sinon Δ. Radicaux simplifiés k√m/d | Objets `Chaine` : « ⇔ (x−2)(x−3) = 0 ⇔ x = 2 ou x = 3 (produit nul) », « Δ = b² − 4ac = … », « Δ = 0 : une seule solution », x₁/x₂ nommés, `S = {…}`, « soit x ≈ … » | EL 3C, EL-M (`_resoudre_egalite`), `meme_base`, `_suite_polynome`, `_produit_nul`, `_degre_zero` | Instantanés EL (583 entrées) et EL-M (276) ; environ 164 assertions de texte (test_exp_log), 83 (test_audit_el), test_exp_log_m, test_explog_3c |
| Modèle de chaîne : `Eq`, `Rel`, `Ou`, `Texte`, `Positif`, `Chaine`, `Message`, `Defini`, `tex_chaine`, `rangees_chaine`, constantes `PROP_*` | exp_log.py, section 8 ; `_ligne` dans resoudre_el.py ; CSS `.chaine` **local** à `exponentielles-logarithmes/index.html` l. 17–26 | Grille lien ⇔ \| expression \| propriété ; repli sur 2 colonnes à petite largeur | Exactement la mise en page du corrigé (⇔ alignés, annotation « ME » ou « Id. rem. A = x, B = 1 » à droite) | EL, EL-M | Références de pages EL si le CSS change |
| Bicarrée et changement de variable : `_bicarre`, `_plan_apres`, `variantes_changement` | `exp_log_m.py` | u = t², u > 0 ; t = aˣ, t > 0, carte « Valeurs de t » retenue / rejetée. **Racines rationnelles seulement** (sinon « pas encore ») | Cartes par étape | EL-M, EL 3C | Instantanés EL-M |
| Vérification : `verification`, `controler_3c`, `_controle_candidat`, `controle_calculatrice` | exp_log_m.py, exp_log.py | Substitution exacte dans l'équation de départ (R20), rejet motivé, R15 | Carte « Vérification » (M), carte « Contrôle » (3C) | EL | — |
| `trinome(P, v, lignes, entier, nom, compact)` | `ensemble-definition/ensemble_def.py` (via `moteur/noyau.py`, seule frontière autorisée) | Δ et zéros exacts (`Num.quad`), approximations `dec` | Phrases : « Trinôme … : Δ = b² − 4ac = … = 1, √Δ = 1 : zéros x₁ = −4 et x₂ = −3. » Toujours Δ, même pour x² + 7x + 12 (essai) | ED, DV, LA, EC, EL-M, **Factorisation** (`trinome_methodes`) | Instantanés de **six** outils |
| `factoriser`, `racine_rationnelle`, `racines_numeriques`, `difference_de_carres`, `resoudre_rat`, `racines_quad_r`, `preimage`, `decomposer`, `retour_atome`, `tableau_facteurs`, `resoudre_general`, `Num` | ensemble_def.py | Factorisation et équation / inéquation rationnelle (« une fraction est nulle lorsque son numérateur est nul », exclusion de la valeur interdite), tableau de signes R7, changement de variable t = ln B, eᴮ, √B | Phrases et tableau de signes | ED, DV, LA, EC | Idem |
| Cascade de factorisation : `mise_en_evidence`, `reconnaitre_identite`, `appliquer_identite`, `trinome_methodes`, `somme_produit`, `_forme_sans_fraction`, `changement_variable`, `groupements_essai`, `racine_evidente` (entière, degré ≥ 3), `completer_carre`, `repli` | `factorisation/factorisation.py` + `resoudre_fa.py` | Tout polynôme, plusieurs lettres. Garde-fou : redéveloppement SymPy puis repli. **SymPy obligatoire** | Une carte « Étape k » par méthode (badge), phrases « On met 6 en évidence… », « On reconnaît une différence de deux carrés … avec A = x et B = 1 », « Trinôme unitaire … on cherche deux nombres u et v… On trouve u = 4 et v = −9, car… » | Factorisation (1C, 1Ms, 1Mr) | Instantanés FA (194 entrées, dont 68 touchées), test_resoudre_fa, test_proprietes_factorisation |
| `_factoriser`, `resolution_polynome`, `resolution_somme_produit`, `etapes_polynome`, `_en_parallele`, `chaine_en_ligne`, `zeros_facteur`, sondes `_accord_numerique`, `valeur_mp`, `confirmer_signe` | `etude-complete/parties.py` | Mise en évidence pgcd·xᵏ, Somme-Produit à racines entières (garde-fou exact), ax² + c = 0 ⇔ x = ±√ | « On résout x² − 3x + 2 = 0 ⇔ (x − 1)(x − 2) = 0 (Somme-Produit) ⇔ x = 1 ou x = 2 (produit nul) » sur une ligne | EC | Instantanés EC, test_parties_ec (111 tests) |
| `_ligne_zeros`, `_chaine_annotee` (doublon de `chaine_en_ligne`) | `derivee-variations/derivee_variations.py` | f′ = 0 : numérateur nul, division par c, e^… > 0, produit nul, zéro hors ED rejeté | Essai : « f′(x) = 0 ⇔ (2x + 3)(x + 5) = 0 ⇔ 2x + 3 = 0 ou x = −5 (produit nul) ⇔ x = −5 ou x = −3/2 ». Factorisation de f′ **non justifiée**. Δ < 0 : « f′(x) = x² + x + 1 ne s'annule jamais », sans Δ | DV, EC | Instantanés DV (5 entrées), test_derivee_narration |
| Nombres | `moteur/nombres.py` (notation suisse) ; exp_log `_nb_exact` (R13, état global `_DECIMAUX`) et `tex_approx` (3 décimales) ; ED `qtex`, `dec` | — | Deux formats de ≈ différents | — | — |
| Sortie et page | `moteur/sortie.py` (aucun bloc « chaîne » : le HTML passe dans un bloc texte) ; `commun/outil.js` `monterOutil` (exemples, exercices, filières, variantes, option) ; `rendu.js` (KaTeX 0.16.11) ; `composants.js` (clavier, onglets) | — | — | Tous | — |
| Lecture d'une saisie avec « = » | exp_log `lire_membres` / `analyser_saisie` seulement (arbre `Var`/`Pow`/`Log`, différent de celui de l'ED). Les parseurs de l'ED (`lire`) et de la Factorisation ne lisent pas « = » | — | — | EL | — |

**Branchement d'un outil** (A et C) :
- `dossier/index.html` (EXEMPLES et EXOS lus par `tests/python/cas.py`) ;
- un moteur `.py` et un `resoudre_xx.py` (`resoudre_json`, `apercu_json`, `exercice_json`) ;
- `moteur/manifeste.json` (fichiers chargés **à plat**) ;
- `commun/registre.json` et la carte de l'accueil ;
- SymPy en roues précompilées, chargé après une pause de frappe.

### 1.2 Documentation (rapport B)

- **Prévu.**
  - `docs/futur_outils.md`, outil n° 1 « Équations et inéquations » : degré 1 et 2, ramenées au 2e degré, rationnelles, tableau de signes ; 1re Ms/Mr.
  - `docs/taches.md`, N02 : brique « analyse d'équations, inéquations, systèmes et ensemble solution ». Elle dépend de N01 (Tangente, non fait) et serait réutilisée par N03 à N21. T33 s'est fait sans N02 (précédent).
- **Décisions déjà tranchées qui touchent le chantier.**
  - FA-09 : pas de zéro évident p/q, Δ pour a ≠ 1. **Elle contredit le corrigé** (D1).
  - FA-10 : forme sans fraction (2x + 1)(3x + 1), comme la remarque du corrigé en 2.12 b.
  - FA-05.
  - FA-11 : jamais « ne se factorise pas davantage » sans justification.
  - EL : Δ écrit une seule fois ; Δ = 0 donne « une seule solution » puis x = −b/(2a) ; a·x² = 0 ⇔ x = 0 ; ordre croissant (§ 15) ; « S = {…}, soit x ≈ … » (EL-18) ; S = ∅ et S = ℝ ; deux messages, « ne se résout pas avec les méthodes du cours » et « pas encore » (EL-11).
  - EC : Somme-Produit seulement pour un trinôme unitaire à racines entières ; « x − r » s'écrit directement x = r ; « x² = 6 ⇔ x = −√6 ≈ … ou x = √6 ≈ … » ; zéro hors ED rejeté avec sa raison ; garde-fous EC-15 (SymPy + mpmath, sinon « ne conclut pas »).
  - DV-18 : ligne des zéros.
- **Guide de rédaction.**
  - R1 : ne justifier que le nouveau.
  - R3 et R14 : chaîne de ⇔ alignés, propriété à droite. La règle dit encore « les autres outils ne sont pas encore concernés ».
  - R5 et R10 : Δ une fois ; a² − b² factorisé directement.
  - R7 : tableau de signes.
  - R12 : vouvoiement dans les invites, corrigé à l'impersonnel.
  - R13 : fractions et notation scientifique.
  - R15 : contrôle à la calculatrice.
  - R17, R18 et R20 : ED, multiplication par le dénominateur « en le disant », élévation au carré après isolement de la racine, ⇒ contre ⇔, Contrôle, rejet motivé.
- **Écarts de documentation.** `docs/README.md` annonce « R1–R12 », CLAUDE.md « R1–R19 », alors que le guide va jusqu'à R20.
- **Tâches ouvertes liées.**
  - T34 : R13 dans tous les outils.
  - T23 : notation suisse dans le tokeniseur de la Factorisation.
  - T37.3 : nommer une solution longue x₁ / x₂.
  - Q8 : racine double des gabarits.

### 1.3 Tests (rapport C)

- **Oracle.** `tests/python/oracle.py` (mpmath, 50 chiffres : `valeur`, `definie`, `derivee` sur l'arbre ED) n'a **pas de fonction de racines**. Chaque test cherche lui-même les racines (`findroot`, changements de signe). Exp-log a son propre oracle (`test_exp_log.py::evaluer/vrai`), car son arbre est différent.
- **Instantanés.**
  - Jeux : `tests/python/instantanes/<outil>.json` (5 moteurs) et `instantanes/resoudre/<outil>.json` (7). Les entrées sont lues dans les EXEMPLES et EXOS des pages, plus `cas.py` et `cas_el.py`.
  - Entrées touchées par Δ / Somme-Produit / produit nul : FA 68/194, EL 50/583, EL-M 43/276, EC 10/21, ED 7/42, DV 5/32, LA 0.
  - Les références de pages (`tests/pages/references/*.json`) ont à peu près les mêmes comptes.
- **Tests à texte exact.** test_resoudre_fa, test_proprietes_factorisation (relit le LaTeX avec SymPy), test_facteurs_evidents (« Δ une seule fois »), test_derivee_narration, test_parties_ec, test_exp_log, test_audit_el, test_exp_log_m, test_explog_3c ; aussi test_vocabulaire et le contrôle TUTOIEMENT.
- **Listes à compléter pour un nouvel outil.**
  - `lancer.py` : `DOSSIERS_MOTEURS` et `OUTILS_PAGES`.
  - `tests/python/moteurs.py` (sys.path).
  - test_resoudre_import, test_source_unique::MIGREES, test_style_commun, test_json_strict::OUTILS_ENTREES, test_instantanes*::OUTILS.
  - `tests/pages/rendu.py` : OUTILS et REDUIT (3 entrées dont une erreur).
  - test_largeurs (automatique, CONNUS vide), manifeste et registre.
  - `tests/pages/test_accueil.py::test_le_registre_donne_16_liens` est **codé en dur** : il cassera au branchement sur l'accueil.

## 2. Le corrigé, étape par étape, comparé au moteur

### 2.1 La méthode du corrigé de l'enseignant (2.9 à 2.12)

**Encadré de tête :**
- « Pour factoriser, on procède dans l'ordre : ① ME ; ② Id. rem. ; ③ S-P, uniquement si le trinôme est unitaire ; ④ Tâtonnement si a ≠ 1. »
- Puis « un produit est nul si et seulement si l'un des facteurs est nul ».
- En 2.9, les trois identités sont rappelées : A² − B² = (A + B)(A − B), etc.

| Étape | Forme exacte dans le corrigé | Ce que produisent les briques existantes (essais) | Écart |
|---|---|---|---|
| 0. Ramener à « … = 0 » | « On ramène d'abord l'équation à la forme … = 0 : x² + 7x = 18 ⇔ x² + 7x − 18 = 0 » (2.10 h, j ; 2.11 f, h, j ; 2.9 d, f, k, l). Membre de droite passé à gauche, termes ordonnés, **a pas forcément positif** (j : x² − 4x − 32 = 0, depuis 4x + 32 = x²) | EL `_resoudre_polynome` écrit la forme standard. FA refuse « = » | Lecture du « = » à créer (hors EL) |
| 1. ME | « 6x² − 6 = 0 ⇔ 6(x² − 1) = 0 » avec **« ME »** en marge ; « −y² + 10y − 9 = 0 ⇔ −(y² − 10y + 9) = 0 ME » précédé de « Le trinôme n'est pas unitaire (a = −1) : on met d'abord −1 en évidence » ; ME d'un facteur commun binôme (2.12 e : (x − 1)[(2 − x) − (x + 3)] = 0, avec « Attention : on ne divise pas par (x − 1), car ce facteur peut être nul ! ») ; ME de x (2.12 c) | FA : ME juste et identique en contenu (6, 3, 4, 8, 18, −1, x², binôme) ; phrase « On met 6 en évidence (facteur commun à tous les termes) : … » | Rédaction : chaîne ⇔ + « ME » contre phrase. L'avertissement « on ne divise pas » est absent |
| 2. Id. rem. | Phrase avant la chaîne : « Id. rem. A² + 2AB + B² avec A = t, B = 10. **Vérification : 2AB = 2·t·10 = 20t ✓** » ; pour A² − B², annotation en marge « Id. rem. A = x, B = 1 ». Cas particuliers : B = 1/3 (h), **B = √5 (j : x² − 5)**, A = 2(x − 2) « (car A² = 4(x − 2)²) » puis développement (2x − 4 + 1)(2x − 4 − 1) (k), A = x + 1 (l), A = 4, B = 3x + 2 (2.12 h), et x² = 16 via x² − 16 (2.12 g). Ordre des facteurs **(A + B)(A − B)**. Le carré (t + 10)² est réécrit (t + 10)(t + 10) puis « t + 10 = 0 » une seule fois | FA reconnaît A et B dans tous ces cas, **sauf x² − 5 (→ Δ)**. Ordre **(A − B)(A + B)**. Pas de ligne « Vérification : 2AB ». 16 − (3x + 2)² donne 3(2 − 3x)(x + 2) (ME de 3 en plus), contre (3x + 6)(2 − 3x) dans le corrigé | Ligne de vérification, B = √k, ordre des facteurs, pas de ME après coup |
| 3. S-P (a = 1) | « Rappel. Si a = 1 : x² + bx + c = (x + p)(x + q) où p·q = c et p + q = b. » Puis « Pas de ME, pas d'Id. rem. ; le trinôme est unitaire (a = 1) : S-P. On cherche deux nombres dont le produit vaut −36 et la somme vaut −5 : » suivi d'un **tableau « produit = −36 \| somme »** qui liste les paires de diviseurs dans l'ordre (1, −36 → −35 ; 2, −18 → −16 ; …) jusqu'à « −5 ✓ ». Le signe des paires est choisi selon le cas (b : −1, 18 ; e : −1, −9) | FA : « Trinôme unitaire … on cherche deux nombres u et v tels que u + v = −5 et u·v = −36. On trouve u = 4 et v = −9, car… » (pas d'essais). EL : (x − 2)(x − 3) = 0 direct, sans nommer S-P. EC : « (Somme-Produit) » en propriété | Tableau des essais à créer |
| 4. Tâtonnement (a ≠ 1) | Encadré : « 1. On cherche une solution entière r en testant les diviseurs de c. 2. (x − r) est un facteur : ax² + bx + c = (x − r)(ax + △). 3. On complète △ grâce au dernier terme : (−r)·△ = c. » Exemple : « x = −5 est solution, car 2·(−5)² + 13·(−5) + 15 = 50 − 65 + 15 = 0. Donc 2x² + 13x + 15 = (x + 5)(2x + △) avec 5·△ = 15, donc △ = 3. » En 2.12 b : « On teste les entiers ±1 : … ≠ 0. Il n'y a pas de solution entière : on teste des fractions. x = −1/2 est solution… **Remarque.** Pour éviter les fractions, on écrit (2x + 1) » puis (2x + 1)(3x + △) « car 2x·3x = 6x² ». Après une ME (2.11 h, j ; 2.12 d), le tâtonnement porte sur le trinôme réduit | **Absent partout.** FA : Δ par décision (FA-09 ; commentaire « les zéros p/q ne se testent pas à la main » dans `trinome_methodes`). `racine_entiere` / `racine_evidente` testent bien les diviseurs entiers du terme constant, mais seulement pour le degré ≥ 3 | **Écart principal** (D1) |
| 5. Produit nul | « ⇔ 6 = 0 (accolade « impossible ») ou x + 1 = 0 ou x − 1 = 0 ⇔ x = −1 ou x = 1 ». Un facteur constant (y compris −1) est écrit puis déclaré impossible ; facteur x : « x = 0 » direct. Solutions dans **l'ordre des facteurs** dans la chaîne (« x = 3 ou x = −6 »). Étape intermédiaire si a ≠ 1 seulement quand elle aide (2.9 h : « 3x = −1/3 ou 3x = 1/3 ») | EL : « (produit nul) » en propriété ; constante jamais écrite. DV : « 2x + 3 = 0 ou x = −5 (produit nul) ⇔ x = −5 ou x = −3/2 ». EC : facteur par facteur (`_en_parallele`) | « c = 0 impossible » à créer ; propriété « produit nul » absente du corrigé (dite une fois dans l'encadré) |
| 6. Ensemble solution | `S = {−6 ; 3}` **encadré**, ordre croissant, séparateur « ; ». Aucune approximation | EL : `S = \left\{… \,;\, …\right\}`, croissant, « soit x ≈ … » si irrationnel ; ED : idem | Conforme (le cadre est un style de bloc `resultat`) |
| 7. Vérification | Pas de vérification des solutions (chaîne d'équivalences). Les seules vérifications sont celles de 2AB (Id. rem.) et du candidat r (tâtonnement) | EL : Contrôle / Vérification par substitution (3C / M) | À ne **pas** ajouter pour le polynomial (R1) ; à garder pour ⇒ (racines) |
| 8. Δ < 0 | **Absent du corrigé de l'enseignant.** Polycopié § 2.2.5 : formule x₁,₂ = (−b ± √Δ)/2a, « Si Δ < 0, l'équation n'admet aucune solution réelle : S = ∅ » ; ex. 2.17 d (3t² + 5t + 12 = 0, S = ∅) ; « En résumé : 5 méthodes dans l'ordre : ME, produits remarquables, S-P, tâtonnement, formule ». Aussi « compléter le carré » (§ 2.2.4) comme démonstration de la formule | FA : « Non factorisable dans ℝ (Δ < 0) … toujours positif ». ED : « ne s'annule jamais : aucune valeur interdite ». EL : « Δ < 0 : l'équation n'a aucune solution réelle. » puis S = ∅. DV : « ne s'annule jamais », sans Δ | Formulation à fixer (D7) ; EL est la plus proche du polycopié |

### 2.2 Résultats du moteur, exercice par exercice (essais Factorisation, plus EL, ED et DV sur quelques cas)

| Exercice | Méthode du corrigé | Moteur (FA) | Valeurs (oracle) |
|---|---|---|---|
| 2.9 a, c, e, f, i | ME + carré parfait / A² − B² | ME + identité ✓ | ✓ |
| 2.9 b, d, g, h, l | Id. rem. | Id. rem. ✓ (ordre (A − B)(A + B)) | ✓ |
| 2.9 j x² − 5 | Id. rem. B = √5 | **Δ = 20** puis (x + √5)(x − √5) | ✓ |
| 2.9 k 4(x − 2)² = 1 | A = 2(x − 2), développement | A = 2(x − 2) ✓, résultat (2x − 5)(2x − 3) | ✓ |
| 2.10 a, b, d, f–j | S-P, tableau | S-P sans tableau ✓ | ✓ |
| 2.10 c, e | ME (2, −1) + S-P | ME + S-P ✓ | ✓ |
| 2.11 a–g, i | Tâtonnement (r entier) | **Δ** (49, 100, 4356, 225, 16, 81, 84100, 484) | ✓ |
| Javet ex. 8 b x³ − 4x² + 4x | ME + Id. rem. | ME + carré parfait ✓ | — |
| 2.11 h, j | ME + tâtonnement | ME + **Δ** | ✓ |
| 2.12 a, f | S-P | S-P ✓ | ✓ |
| 2.12 b 6x² + 5x + 1 | Tâtonnement sur fractions | **Δ = 1** | ✓ |
| 2.12 c x³ − x | ME + Id. rem. | ME + Id. rem. ✓ | ✓ |
| 2.12 d | ME + tâtonnement | ME + **Δ** | ✓ |
| 2.12 e (x − 1)(2 − x) = (x − 1)(x + 3) | Tout à gauche, ME (x − 1) | ME ✓ (saisie sans « = » seulement) | ✓ |
| 2.12 g x² = 16, h 16 − (3x + 2)² | Id. rem. | Id. rem. (+ ME de 3 pour h) | ✓ |
| Javet 2.17 a–c, e (Δ > 0 irrationnel) | Formule | Δ ✓, radicaux simplifiés, ≈ | ✓ |
| Javet 2.17 d (Δ < 0) | S = ∅ | « Non factorisable dans ℝ » | ✓ |

## 3. Équations « qui se ramènent au second degré » présentes dans le matériel

| Famille | Où | Exemples (valeurs de l'oracle) | Ce qu'il faudrait |
|---|---|---|---|
| Degré 3 et plus par ME ou Id. rem. | Corrigé 2.12 c ; Javet ex. 8 b, § 3.3, 3.5 ; Az 4.1 f | x³ − x = 0 → {−1 ; 0 ; 1} ; x³ + 8x² = 0 → {−8 ; 0} ; x³ − 4x² + 4x = 0 | ME de xᵏ (FA sait) ; le produit nul avec « x = 0 » et « x² = 0 ⇔ x = 0 ». Peu de travail |
| Produit déjà factorisé, facteur commun aux deux membres | Corrigé 2.12 e ; Az 4.1 d (x − 1)(2 − x)(5 − 3x) = 0 | 2.12 e → {−1/2 ; 1} | Produit nul direct (sans développer) ; ME d'un binôme commun avec l'avertissement « on ne divise pas ». Lecture d'un produit écrit |
| Identité ou équation dégénérée | Az 4.1 g (2x − 1)² − 4x(x − 1) = 1 | Se réduit à 1 = 1 : S = ℝ | EL sait (« vraie pour tout réel ») |
| Bicarrées (u = x²) | Javet § 2.4.1, ex. 22–23, 2.31 a–d | x⁴ − 13x² + 36 → {±2 ; ±3} ; x⁴ = 1 → {±1} ; x⁴ + 2x² + 1 → ∅ ; 4x⁴ + 11x² − 3 → {±1/2} ; x⁴ − 5x² − 36 → {±3} ; 2x⁴ − 5x² − 12 → {±2} | « On pose u = x² » (FA `changement_variable` sait factoriser ; EL-M `_bicarre` rédige, mais racines rationnelles seulement) ; puis u = k ⇒ x² = k ⇒ x = ±√k ou « impossible » si k < 0. Il faut les **racines irrationnelles** (x² = 2) |
| Changement de variable sur une expression | Javet 2.32 a, b | (x² − 1)² − 2(x² − 1) + 1 = 0 → {±√2} ; (x² − 2)² − 5(x² − 2) − 14 = 0 → {−3 ; 0 ; 3} | Reconnaître A = x² − 1 comme inconnue auxiliaire. FA reconnaît (x² − 1)² − 2(x² − 1) + 1 comme carré parfait (A = x² − 1), **mais garde x² − 2 « tel quel »** (zéros irrationnels gardés en factorisation) : pour résoudre, il faut aller jusqu'à ±√2 |
| Équations rationnelles | Javet § 4.3 (méthode en 4 points : ED, p/q = 0, numérateur nul, rejet des valeurs interdites), ex. 8, 4.6 a–f ; Az 4.2 a–h | 4.6 a {−3/2 ; 1/4}, b {3/7 ; 4}, c {−3 ; 10}, d {2} (3 rejeté), e {6}, f {(21 ± √73)/23} ; ex. 8 : {3/5 ; 1} et ∅ (3 rejeté) ; Az 4.2 d {−1/2}, e {±1}, f {1 ; 4}, g ∅, h {−1} | ED (outil ED, R17) + mise au même dénominateur ou multiplication « en le disant » (R18) + brique du 2e degré sur le numérateur + rejet motivé (« 3 ∉ ED »). `ensemble_def.resoudre_rat` fait déjà « fraction nulle ⇔ numérateur nul » avec rejet. Travail moyen |
| Équations avec racines carrées | Javet § 2.4.2 (isoler, élever au carré, **tester obligatoirement**), ex. 24–25, 2.33 a–f ; Az 4.3 a–h (g, h : Mr) | 2.33 a {6}, b {5 ; 7}, c {−1 ; −3/4}, d ∅, e {−5/4}, f {23} ; ex. 24 {−2} ; ex. 25 {−1} | Chaîne ⇒ (pas ⇔), contrôle par substitution exacte (EL `_controle_candidat`, R20), parfois deux élévations au carré (e, f, Az g, h). Travail important |
| Formules littérales | Az 4.4 (v = d/t par rapport à t, E = ½mv² par rapport à v…) | — | Hors sujet (paramètres) : à exclure |
| Inéquations du 2e degré | Javet § 2.3, 2.21, 2.22 ; futur_outils n° 1 | — | Tableau de signes (ED `tableau_facteurs`). Chantier séparé |

## 4. Proposition d'architecture

**Principe : réutiliser plutôt que réécrire, sans toucher aux sorties des outils existants dans ce chantier.**

1. **`moteur/chaine.py`** : extraction **pure** du modèle de chaîne d'Exp-log (`Eq`, `Rel`, `Ou`, `Texte`, `Chaine`, `Message`, `Defini`, `tex_chaine`, `rangees_chaine`, `PROP_*`, plus le `_ligne` HTML de resoudre_el).
   - `exp_log.py` le réimporte.
   - Critère d'acceptation : instantanés EL, EL-M et références de pages **identiques à l'octet** ; aucune ligne de test modifiée.
   - Le CSS `.chaine` passe dans `commun/composants.css` (SOC-19), sans changement visuel.
2. **`moteur/second_degre.py`** : la brique commune de résolution rédigée, en Python pur (`fractions.Fraction`, radicaux exacts repris de `_racines_du_second_degre`), sans SymPy, donc sans délai de chargement. Interface proposée :

   ```
   resoudre_polynome(coeffs, inconnue="x", ecrit=None, methodes=ORDRE_DU_COURS, depart=None) -> Resolution
       coeffs   : liste croissante de Fraction (degré ≤ 2, plus xᵏ en facteur et carré de binôme reconnus)
       ecrit    : l'expression telle que saisie (pour « ramener à … = 0 » et l'ordre des termes de l'élève)
       methodes : sous-liste ordonnée de ("ME", "IDREM", "SP", "TATONNEMENT", "FORMULE") ; un outil appelant peut restreindre
       depart   : les deux membres d'origine (ligne « … ⇔ … = 0 »)
   Resolution = {chaines: [Chaine], tableaux: [essais S-P ou tâtonnement], solutions: [nombre exact], methodes: [str],
                 forme_factorisee, remarque}   # tout est exact, aucun flottant affiché sans « ≈ »
   ```

   - Chaque méthode produit une **factorisation rédigée** (même objet que la chaîne), puis un produit nul commun : « c = 0 (impossible) ou … ».
   - **Garde-fou** : le produit est redéveloppé exactement (Fraction) et comparé aux coefficients, puis chaque solution est substituée exactement. Sinon, un message « ne conclut pas », jamais un résultat douteux.
   - L'oracle mpmath reste dans les tests.
3. **Lecture de la saisie** : sur l'arbre de l'ED (le parseur `lire` via `moteur/noyau.py`), avec un découpage au « = ». C'est ce que lit `tests/python/oracle.py::valeur` : l'oracle existant s'applique tel quel aux nouveaux tests. Le polynôme s'obtient par développement exact. Le parseur d'Exp-log reste à Exp-log.
4. **Nouvel outil** `equations-2e-degre/` (nom à fixer, D10) :
   - `equations.py` : le choix de la famille (polynôme, puis bicarrée, rationnelle, racines dans les parties suivantes) et les messages EL-11 ;
   - `resoudre_eq.py` : l'adaptateur `sortie.py` ;
   - `index.html` : `monterOutil`, exemples = exercices du corrigé, clavier commun.
5. **Reprise plus tard par les outils qui résolvent déjà** : un chantier par outil, chacun avec une régénération relue de ses trois jeux (instantanés moteur, instantanés resoudre, références de pages).

   | Outil | Ce qu'il reprendrait | Entrées touchées par jeu |
   |---|---|---|
   | EL | `_resoudre_polynome` → `second_degre` | ≈ 93, plus des centaines d'assertions de texte |
   | EC et DV | lignes de zéros | 10 et 5 |
   | ED | trinôme des conditions | 7 |
   | FA | `trinome_methodes`, tâtonnement si D1 l'étend | 68 |

   Ordre conseillé : EC/DV d'abord (petits), EL en dernier.

**Risques**
- Exp-log : `_DECIMAUX` est un état global, et un import circulaire est possible si `chaine.py` dépend de `tex` d'exp_log. Il faut donc déplacer aussi le `tex` des nœuds utilisés, ou faire accepter à `chaine.py` une fonction de rendu.
- Trois formats de ≈ : `dec` (ED), `tex_approx` (EL), 2 décimales (EC). La brique doit en choisir un (D13).
- Si `trinome` de l'ED est touché, six outils bougent : interdit dans ce chantier.
- `tests/pages/test_accueil.py` compte 16 liens en dur.
- Les exemples de page sont des entrées d'instantanés : les fixer tôt.
- Largeurs à 320 px : la grille `.chaine` à 3 colonnes tient (repli à 2 colonnes) ; le tableau S-P est à vérifier (cibles ≥ 44 px non concernées).

## 5. Décisions à prendre (avec ma recommandation)

| # | Question | Recommandation |
|---|---|---|
| D0 | Emplacement des PDF de référence | Les déplacer dans `docs/reference/equations-2e-degre/` (ignoré) avant toute branche ; ne jamais les commiter |
| D1 | **Tâtonnement contre FA-09** (pas de zéro p/q, Δ pour a ≠ 1) | Dans le nouvel outil, suivre le corrigé : tâtonnement sur les diviseurs entiers de c (ligne « x = r est solution, car … = 0 » et △), **puis** sur les fractions ±p/q avec p \| c et q \| a (comme 2.12 b, avec la remarque « pour éviter les fractions »), en nombre borné ; sinon la formule. FA-09 reste valable pour l'outil Factorisation (décision séparée, plus tard) |
| D2 | Place de la formule (Δ) | 5e méthode, après les quatre du corrigé, comme dans le polycopié (« En résumé : 5 méthodes dans l'ordre »). Plus une **variante** « Par la formule » toujours proposée (SOC-17), utile pour se contrôler |
| D3 | S-P quand il échoue ou quand Δ n'est pas un carré | Le moteur sait d'avance si S-P aboutit : ne dresser le tableau que s'il aboutit ; sinon une phrase « Pas de ME, pas d'Id. rem. ; aucun couple d'entiers ne convient : on utilise la formule ». À valider, car le corrigé ne montre aucun échec |
| D4 | Tableau S-P | Le reproduire (colonnes « produit = c » \| « somme », essais dans l'ordre des diviseurs jusqu'à ✓, signes choisis comme dans le corrigé). Composant commun (tableau simple) |
| D5 | Annotations | Colonne de droite de la chaîne : « ME », « Id. rem. A = x, B = 1 ». Abréviations du corrigé ou mots entiers (« mise en évidence ») ? Je recommande les abréviations du corrigé, avec un rappel unique en tête (l'encadré « Rappel de la méthode ») |
| D6 | Ligne « Vérification : 2AB = … ✓ » | La garder pour A² ± 2AB + B², comme dans le corrigé |
| D7 | Facteur constant | « 6 = 0 (impossible) » avec l'accolade (`\underbrace`), y compris pour −1, comme dans le corrigé |
| D8 | x² − k avec k non carré, et x² = k | Id. rem. avec B = √k (2.9 j) ; x² = 16 passe par x² − 16 (2.12 g). Pas de raccourci ±√k, sauf décision contraire |
| D9 | Rédaction de Δ | Celle d'Exp-log (« Δ = b² − 4ac = … », une fois ; « Δ = 0 : une seule solution » ; « Δ < 0 : l'équation n'a aucune solution réelle », S = ∅ ; x₁ et x₂ nommés si la ligne est longue ; « S = {…}, soit x ≈ … »), qui est conforme au polycopié |
| D10 | Nom, filières et registre | Dossier `equations-2e-degre`, années 1Ms et 1Mr (futur_outils). 1C aussi ? À décider. Branchement au registre en dernière partie, après relecture à l'écran |
| D11 | Périmètre du chantier | Parties 1 à 7 ci-dessous : polynomial, degré 3 par ME, bicarrées et changement de variable. Rationnelles et racines en parties 8 et 9 (ou chantier suivant). Inéquations et formules littérales hors chantier |
| D12 | Vérification des solutions | Aucune pour une chaîne d'équivalences (R1, conforme au corrigé). Contrôle obligatoire pour les racines (⇒, R20). Rejet motivé par l'ED pour les rationnelles (R17) |
| D13 | Approximations | ≈ à 3 décimales, comme EL (`tex_approx`) ; notation suisse |
| D14 | Ordres | Facteurs (A + B)(A − B) comme le corrigé ; solutions dans l'ordre des facteurs dans la chaîne, S croissant |
| D15 | Brique placée dans `moteur/` et réutilisée plus tard | Oui (`moteur/chaine.py`, `moteur/second_degre.py`). **Aucun outil existant n'est rebranché dans ce chantier**, sauf l'extraction pure d'Exp-log (partie 1) |
| D16 | Lien avec N01 et N02 | Traiter ce chantier comme la première pièce de N02 (brique « équations »), sans attendre N01 (précédent T33). Mettre à jour `docs/taches.md` |
| D17 | Tickets hors chantier | (a) le Δ « (−−6) » d'Exp-log (§ 0.4) ; (b) les noms à espaces ignorés par `lancer.py rapide` ; (c) `docs/methode-chantiers.md` à créer ou à retirer des références ; (d) README et CLAUDE.md, « R1–R19 » contre R20 |

## 6. Découpage en parties (une branche `equations-2e-degre` depuis `main` à jour, un commit par partie, suite complète verte avant chaque commit)

| Partie | Contenu | Tests | Dépend de |
|---|---|---|---|
| P0 | `decisions.md` validé ; PDF déplacés (D0) ; `suivi.md` (court, avec « Reprise après compactage ») et `journal.md` | — | Ce rapport |
| P1 | Extraction pure de `moteur/chaine.py` depuis exp_log (+ manifeste) | Instantanés EL et EL-M et références de pages **inchangés** ; test_manifeste, test_resoudre_import | P0 |
| P2 | CSS `.chaine` → `commun/composants.css` ; la page EL l'utilise | Références de pages inchangées ; test_largeurs (CONNUS vide) ; test_style_commun | P1 |
| P3 | `moteur/second_degre.py` : ramener à 0, ME (constante, −1, xᵏ), Id. rem. (3 formes, B = √k, vérification 2AB), S-P (tableau), tâtonnement (D1), formule (Δ > 0, = 0, < 0), produit nul, S | `test_second_degre.py` : chaque exercice 2.9 à 2.12 et Javet 2.17 et ex. 13, avec l'oracle mpmath (racines, et aucune autre) ; propriétés sur des polynômes générés (`generateurs.poly`) ; garde-fou exact ; R12, R13, vocabulaire | P1 |
| P4 | Lecture « membre = membre » sur l'arbre de l'ED, développement exact, choix de la famille, messages EL-11 | Erreurs de saisie, notation suisse, décimaux de l'énoncé (R13) | P0 (en parallèle de P3) |
| P5 | Outil `equations-2e-degre/` : `equations.py`, `resoudre_eq.py`, `index.html` (exemples = exercices du corrigé), clavier ; manifeste, `lancer.py`, `moteurs.py`, toutes les listes du § 1.3 ; **pas** de registre | Instantanés resoudre, rendu.OUTILS et REDUIT, références de pages, test_largeurs, test_json_strict, test_source_unique | P2, P3, P4 |
| P6 | Degré ≥ 3 par ME ou Id. rem. ; produit déjà factorisé ; facteur commun aux deux membres (« on ne divise pas ») ; identité (S = ℝ) | Az 4.1 d, f, g ; 2.12 c, e ; Javet ex. 8 b | P5 |
| P7 | Bicarrées et changement de variable (u = x², u = x² − 1), u < 0 rejeté, ±√ irrationnel | Javet 2.31, 2.32, ex. 22–23, avec l'oracle | P5 |
| P8 | Équations rationnelles : ED d'abord (brique ED), multiplication « en le disant » (R18), numérateur, rejet motivé | Javet 4.6, ex. 8 ; Az 4.2 | P5 (optionnelle selon D11) |
| P9 | Équations à racines : isoler, élever au carré (⇒), Contrôle (R20) | Javet 2.33, ex. 24–25 ; Az 4.3 | P5 (optionnelle selon D11) |
| P10 | Relecture à l'écran, puis registre et accueil (ACC-01 à 08), compteur de `tests/pages/test_accueil.py` | test_accueil (python et pages) | Toutes |

Commande de fusion à donner en fin de chantier (c'est vous qui fusionnez) : `git checkout main && git merge --no-ff equations-2e-degre`.
