# Outil « Étude complète de fonction » (3e Ms, Mr)

URL : `/etude-complete/` · moteur : `etude-complete/etude_complete.py`, qui assemble le noyau,
la dérivée et les limites ; adaptateur `etude-complete/resoudre_ec.py`. Les parties propres à l'Étude complète (aujourd'hui les parties 1, 2 et 3, les extremums de la partie 5 et les ronds vides de la
partie 6 ; plus tard le bilan) sont dans `etude-complete/parties.py` (créé au chantier `etude-complete`, P3, déclaré dans
`moteur/manifeste.json` avec `ensemble-definition/resoudre_ed.py`, dont il reprend les cartes de condition). Décisions de rédaction : `docs/chantiers/etude-complete/decisions.md`.

## Fonctionnel

- **Six parties titrées, dans l'ordre du corrigé** (D1) : 1. Domaine de définition · 2. Parité · 3. Zéros, signe, ordonnée à
  l'origine · 4. Limites et asymptotes · 5. Dérivée, tableau de variation, extremums · 6. Graphe. Chaque partie s'ouvre par un
  intertitre (carte de style `partie` du format commun : un titre sans cadre, affiché avec la carte qui le suit, hors du compteur
  d'étapes). Une partie que l'outil ne sait pas encore rédiger reste vide (son intertitre seul) : rien plutôt qu'une affirmation
  non démontrée (EC-15). Aujourd'hui : parties 1, 2 et 3 = voir ci-dessous ; 4 = cartes de l'outil Limites
  (tableaux de signes, une carte par borne, bilan des asymptotes) ; 5 = cartes de l'outil Dérivée (dérivée, signe de f′ et variations,
  avec les limites et les valeurs des extremums dans le tableau, T06c et D10), extremums rédigés selon D11 (voir ci-dessous) ;
  6 = graphique (D15, voir ci-dessous). Jamais d'intertitre seul sous « 5. » (R2, Q7) : la carte « Dérivée » est toujours affichée
  (dérivée hors du cadre : la phrase de l'outil Dérivée, « Cette fonction sort du cadre de l'outil : la dérivée n'a pas été
  calculée. ») ; signe de f′ non étudié : la carte d'erreur « Signe de f′ et variations » de l'outil Dérivée.
- **Valeurs approchées** (R2, Q15, Q28) : écrites **dans la formule**, après « ≈ » (`f(1) = −5e^{−2} ≈ −0,68`, `x = √6 ≈ 2,45`,
  `(0 ; e^{1/6}) ≈ (0 ; 1,18)`), comme les autres outils : 2 décimales, 2 chiffres significatifs entre 10⁻³ et 0,01, séparateur des
  milliers ’ dès 1000 (`moteur/nombres.py`, convention du site : ≈ 1’234,57), notation scientifique de R13 sous 10⁻³ et dès 10⁶ ;
  un entier exact s'écrit sans « ≈ ». Partie 2 : les contre-exemples restent pris dans [10⁻³ ; 1000[ (question 19).
- **Partie 1, domaine de définition** (D1, D3 ; P3) : carte « Fonction » (f seule) ; carte « Mise en forme » quand f(x) = e^{haut/bas},
  haut et bas polynômes de degré ≥ 1 écrits développés à coefficients entiers, dont l'un au moins se factorise par mise en évidence de
  c·xᵏ ou par Somme-Produit (trinôme unitaire, deux racines entières distinctes, facteurs par racine croissante) : une ligne par
  méthode, la méthode entre parenthèses, puis « On note g(x) = …, donc f(x) = e^{g(x)}. » (`e^((x^2+x-2)/(6x-12))`, Ex7 du corrigé) ;
  rien à factoriser : pas de carte (`e^(2/(x^2-4))`). Une carte par condition (titre et badge de l'outil ED) ; un dénominateur affine ou
  de la forme ax² + c écrit développé est résolu en chaîne courte, « On résout 6x − 12 = 0 ⇔ 6x = 12 ⇔ x = 2. », « x² − 4 = 0 ⇔ x² = 4
  ⇔ x = −2 ou x = 2 » (racines rationnelles ou k√m) ; un trinôme unitaire x² + bx + c (b ≠ 0, c ≠ 0) à deux racines entières
  distinctes, par Somme-Produit (R2, Q11) : « On résout x² − 3x + 2 = 0 ⇔ (x − 1)(x − 2) = 0 (Somme-Produit) ⇔ x = 1 ou x = 2 (produit
  nul). » (`1/(x^2-3x+2)`) ; un dénominateur x s'écrit « x ≠ 0 » seul ; toute autre condition garde les lignes de l'outil ED. Carte « Ensemble de définition » : l'ED encadré (conclusion de l'outil ED), précédé de « Ni logarithme, ni
  dénominateur, ni racine : aucune condition. » quand il n'y a pas de condition. Garde-fous (EC-15) : la factorisation développée
  redonne le polynôme et une sonde numérique compare les deux écritures ; les racines de la chaîne donnent exactement l'ensemble de
  l'outil ED et annulent le dénominateur ; sinon la ligne n'est pas écrite (mise en forme) ou la condition garde la rédaction de l'outil ED.
- **Partie 2, parité** (D4 ; P4) : carte « Symétrie de l'ED ». ED non symétrique : un point a ∈ ED avec −a ∉ ED, d'abord le
  symétrique d'une borne rationnelle, sinon 1, 2, 1/2, 3… (« −2 ∈ ED, mais 2 ∉ ED : ED n'est pas symétrique par rapport à 0. »), puis
  « Donc f n'est ni paire ni impaire. ». ED symétrique (« ED est symétrique par rapport à 0. ») et f paire ou impaire : carte « Calcul
  de f(−x) », une étape par ligne (substitution « (on remplace x par −x) », forme simplifiée avec les propriétés « car (−x)² = x² » et
  « règle des signes », « −(…) (mise en évidence de −1) » pour une somme impaire, « = f(x) » ou « = −f(x) »), puis « Donc f est paire. »
  (ou impaire) ; la chaîne n'est écrite que si la parité se lit sur l'arbre (puissances de x, sommes, produits, quotients, exp / ln / √
  d'une expression paire), sinon un message clair (`e^x+e^(-x)`). Ni paire ni impaire : carte « Pas impaire » (« f(0) = −6 ≠ 0 » si
  0 ∈ ED et f(0) ≠ 0, sinon un contre-exemple f(−a) ≠ −f(a)) et carte « Pas paire » (contre-exemple f(−a) ≠ f(a)), a dans 1, 2, 1/2, 3,
  4, 1/3, 5 avec ±a ∈ ED, valeurs exactes puis approchées (decisions.md §2 ; un entier exact sans « ≈ » ; valeurs hors de
  [10⁻³ ; 1000[ évitées), les deux valeurs arrondies affichées différentes, sinon a suivant, sinon un message clair. Garde-fous (EC-15,
  principe 0.2 de decisions.md) : l'ED (symétrie, appartenance) est décidé exactement ; toute affirmation est confirmée par SymPy (f(−x) ∓
  f(x) se simplifie en 0, chaque ligne de la chaîne vaut f(−x), chaque valeur écrite vaut f(a)) **et** par une sonde mpmath (l'arbre
  évalué à 30 chiffres en ±x) ; un désaccord, une borne approchée ou SymPy absent donnent « La parité de f n'a pas pu être établie avec
  certitude : l'outil ne conclut pas. », sans conclusion. Calculée par `resoudre` (hors d'`etudier()`), sur l'analyse en cache.
- **Partie 3, zéros, signe, ordonnée à l'origine** (D5 ; P5) : carte « Zéros de f » (ou « Zéros et signe de f »). Chaque facteur
  e^{…} : « e^{−2x} > 0 pour tout x (une exponentielle est strictement positive) ; il ne s'annule jamais. » (« pour tout x ∈ ED » si
  ED ≠ ℝ ; « e^{g(x)} » quand la partie 1 a nommé g ; f = e^{…} seule : sans « il ne s'annule jamais »). Puis f(x) = 0 en chaîne, une
  étape par ligne, la propriété nommée entre parenthèses : « (x² − 6)e^{−2x} = 0 ⇔ x² − 6 = 0 (car e^{−2x} > 0) ⇔ x² = 6 ⇔ x = −√6
  ≈ −2,45 ou x = √6 ≈ 2,45 » ; « numérateur nul », « on divise par 3 », « produit nul » (facteurs menés ensemble ; un facteur x − r
  s'écrit directement x = r, R2, Q11 : « (x − 1)(x − 3) = 0 (Somme-Produit) ⇔ x = 1 ou x = 3 (produit nul) »), « mise en
  évidence », « Somme-Produit » (comme la partie 1), lignes « A ⇔ B (propriété) » de l'outil ED pour un facteur non polynomial
  (« e^{x} = 6 (on isole e^{x} …) ») ; un zéro hors de l'ED est rejeté (« x = 0 est rejeté, car 0 ∉ ED. ») ; une forme que la chaîne
  ne couvre pas (√(x² − 4), x² + 1) garde les lignes de l'outil ED, puis « Donc x = … ». Valeur exacte puis approchée (decisions.md §2 ;
  voir « Valeurs approchées »). Sans zéro et de signe constant :
  « Donc f n'a pas de zéro et f(x) > 0 sur ED. », pas de tableau ; sinon carte « Signe de f » : le tableau de signes de f, construit
  par la machinerie R7 du tableau de f′ (`derivee_variations.tableau_signes` : une ligne par facteur, constante à part, zéros et valeurs
  interdites, zones hors de l'ED barrées), avec **une ligne par facteur de la factorisation écrite dans la chaîne** (R2, Q23 :
  x² − 4x + 3 → x − 1, x − 3 ; x³ − 3x → x, x² − 3) ; garde-fou : la constante fois le produit des lignes est égal à f (SymPy exact
  et sonde mpmath), sinon les facteurs saisis. Zéros non exacts (x³ + x + 1) : « Les zéros de f ne se calculent pas exactement : l'outil ne
  dresse pas le tableau de signes de f. » ; zéros non calculés : « Les zéros de f n'ont pas pu être calculés par l'outil : le signe de
  f n'est pas traité. ». Carte « Ordonnée à l'origine » : « f(0) = −6. » (exact puis ≈ ; « g(0) = −2/(−12) = 1/6, donc f(0) =
  e^{1/6} ≈ 1,18 » quand g est nommé), puis « Le graphe coupe l'axe des y au point (0 ; f(0)). » ; « 0 ∉ ED : le graphe ne coupe pas
  l'axe des y. ». Garde-fous (EC-15, principe 0.2) : les zéros sont confirmés par SymPy (f(z) = 0, et `solveset` ne trouve aucun autre
  zéro dans l'ED, appartenance décidée exactement) et par la sonde (|f(z)| < 10⁻²⁰ à 30 chiffres) ; le signe de chaque intervalle de
  l'ED est le signe exact (SymPy) de f en un point rationnel et celui de la sonde en 9 points ; la chaîne doit finir sur les zéros
  calculés (sinon les lignes de l'outil ED) ; f(0) écrit = valeur SymPy = sonde. Au moindre désaccord : « Le signe de f n'a pas pu
  être établi avec certitude : l'outil ne conclut pas. » (ou « L'ordonnée à l'origine n'a pas pu être établie avec certitude… »).
  Calculée une fois par étude (`etude_complete.etude_et_partie3`, sur l'analyse en cache) : ses cartes pour `resoudre`, ses zéros
  et f(0) pour le graphique (P8).
- **Partie 5, extremums** (D11 ; P7b, R2) : à la place de la liste de l'outil Dérivée, dans la carte « Signe de f′ et variations ».
  D'abord une ligne de calcul pour **chaque** extremum (R2, Q41) : quand la carte « Dérivée » a nommé g (f = e^{u/v}) et x₀ est
  entier, « g(4) = 18/12 = 3/2, donc f(4) = e^{3/2} ≈ 4,48. » ; sinon, pour x₀ rationnel, ln(q) ou e^{q}, la substitution en chaîne
  « f(−2) = ((−2)² − 6)e^{−2(−2)} = (4 − 6)e⁴ = −2e⁴ ≈ −109,20. » (substitution, x₀ entre parenthèses s'il est négatif ou
  fractionnaire ; puis puissances, produits et quotients de nombres calculés, avec e^{ln q} = q, ln(e^{q}) = q, e⁰ = 1, 1·a = a,
  0·a = 0 ; puis les sommes ; puis l'écriture de l'extremum), chaque membre vérifié égal à f(x₀) par SymPy et par la sonde mpmath ;
  une écriture ambiguë (chiffre collé à une fraction) ou un doute : pas de ligne. Puis une ligne par extremum (§2 révisé, Q43) :
  « **Maximum global** en x = 0 : (0 ; 1) (f′ passe de + à −). Les autres valeurs de f sont plus petites (limites 0⁺ en ±∞). » quand
  f(x₀) dépasse strictement les autres extremums du même genre et toutes les limites aux bornes de l'ED (±∞ et chaque côté ouvert de
  chaque borne, celles du tableau T06c) ; « **Maximum local** en x = 0 : (0 ; e^{1/6}) ≈ (0 ; 1,18) (f′ passe de + à −). Pas global :
  f(x) → +∞ quand x → 2⁺. » (raison : la limite ou l'extremum le plus extrême, le premier dans l'ordre du tableau à égalité) ;
  « **Maximum local** … » seul si une limite vaut « ? » ou manque, en cas d'égalité, si une borne fermée de l'ED n'est pas un extremum ou si la
  valeur n'est pas exacte. Garde-fous (EC-15, principe 0.2) : chaque comparaison est faite par SymPy (signe exact de la différence) et
  par mpmath ; « global » est confirmé par une sonde de f sur l'ED (grille, points près de chaque borne et lointains : aucune valeur
  au-delà de f(x₀)), « pas global » par une valeur de f au-delà de f(x₀) près de la borne nommée ; les limites sont lues sur une liste
  fermée d'écritures (±∞, entiers, fractions, avec signe d'approche) ; au moindre doute, « local » seul. Sans SymPy : la liste de l'outil
  Dérivée. Calculée par `resoudre`, sur l'analyse en cache.
- **Une seule analyse par saisie** (D19) : le résultat de `analyser_complet` (ED) est gardé en cache (`functools.lru_cache`, clé =
  saisie aux espaces réduits et présence de SymPy) ; `etudier()` le passe aux outils Dérivée et Limites (paramètre facultatif
  `analyse` de leur `etudier`, sans effet sur ces outils seuls), et `fenetre()` (zoom) le relit sans recalcul.
- **Partie 6, graphe** (D15, decisions.md §3 ; P8) : courbe tracée par morceaux de l'ED ; asymptotes en pointillé ; extremums,
  zéros et point (0 ; f(0)) en points pleins avec leurs coordonnées (zéros et f(0) : ceux qu'écrit la partie 3, calculée une seule
  fois par étude, `etude_complete.etude_et_partie3` ; rien en cas de doute ; un point déjà extremum n'est pas repris) ; **rond vide**
  à chaque point exclu dont la limite est finie, d'un côté ou des deux : trous de l'outil Limites (limites finies égales, ou bord de
  l'ED) et `ronds_vides` (`parties.ronds_vides` : limite finie d'un seul côté, Ex7 (2 ; 0), d (±2 ; 0), ou deux limites finies
  différentes, x/√(x²) (0 ; ±1)). Garde-fous (EC-15, principe 0.2) : la limite du tableau T06c se lit sur la liste fermée
  (entiers, fractions, avec signe d'approche ; « e » : pas de rond), le point est hors de l'ED (exact), SymPy donne exactement la
  limite latérale (règles des limites : e^{lim u}, produit et somme de limites finies ; sinon `limit`) et une sonde mpmath
  (f(a ± 10⁻ᵏ), k = 3 … 12, 30 chiffres) s'en approche du bon côté ; sinon pas de rond. **Cadrage** : la fenêtre contient les
  extremums, les zéros, (0 ; f(0)), les ronds vides, les trous et les bornes finies de l'ED ; en y, les échantillons (bande centrale de
  chaque morceau) sont ramenés dans [min − e ; max + e] des ordonnées de ces points et des AH (e = max(étendue/4 ; 1)) : une branche
  qui file vers ±∞ ne fixe pas l'échelle ; pour chaque AH y = L en ±∞, le côté de l'AH est élargi (25 % de la largeur, 6 fois au
  plus) jusqu'à ce qu'un échantillon au-delà de tous les points à montrer et des valeurs interdites soit à moins de 5 % de la hauteur
  de la fenêtre de L, sinon la fenêtre des points reste (ln(x)/x). La courbe est tracée une largeur de fenêtre au-delà de chaque côté
  (l'écran, à échelle égale, montre souvent plus large). Rééchantillonnage de la fenêtre visible au zoom (`fenetre`, inchangé). Pas
  de seconde figure : le zoom la remplace.
  **Souris** : molette et boutons (zoom), glisser (déplacement). **Écran tactile** : un doigt fait défiler la page (la courbe ne
  bouge pas), deux doigts déplacent et zooment la courbe, le point sous le milieu des doigts y reste (T19, EC-05).
- Les valeurs communes (ED, f′, zéros de f′, limites) sont exactement celles des outils séparés (EC-01).

## Conventions

- Celles des outils séparés. Limite finie ℓ en une valeur interdite a : rond vide en (a ; ℓ)
  (« trou dans le graphique », Q7) ; limite finie d'un seul côté, ou limites latérales finies et différentes : un rond vide par
  limite finie (D15, P8), aucune asymptote.
- Graduations du graphique en notation suisse (virgule décimale).

## Tableau de variations avec limites (T06c) — validée le 16.10.2026

Décidé le 14.10.2026 (limites contre les doubles barres), précisé le 16.10.2026 (limites aussi en ±∞
quand l'ED y va). **Étude complète seulement** : le tableau de l'outil Dérivée garde les flèches seules.

### Règles

- **Où** : ligne f(x) du tableau de variations de l'Étude complète, et nulle part ailleurs. Les lignes
  de signe (facteurs, f'(x)) ne changent pas.
- **Contre une double barre** (valeur interdite de f, y compris borne ouverte de l'ED comme ln x en 0) :
  la limite à gauche s'écrit à gauche de la barre, la limite à droite à droite. **Seul le côté de l'ED
  porte une valeur** : à côté d'une zone hachurée, rien (ln(x²−4) : −∞ à gauche de la colonne −2,
  zone hachurée à droite ; l'inverse en 2).
- **En ±∞** : si l'ED atteint −∞ (resp. +∞), la limite s'écrit sous l'en-tête −∞ (resp. +∞), au bout de
  la première (resp. dernière) flèche. Les autres lignes restent vides à cet endroit.
- **Inchangé** : la valeur f(a) sans barre en un point de l'ED où f' n'est pas définie ou en une borne
  fermée (T06) ; une borne finie fermée de l'ED n'a jamais de limite (on y a f(a)).
- **Notation** : la valeur seule, exacte (−∞, +∞, 0, 2, ln 2, √2), sans « lim » ni « x → a » : la flèche
  adjacente dit déjà de quel côté on vient. Limites latérales finies égales = trou : la même valeur des
  deux côtés de la barre, sans autre marque (le trou est dit par la partie Limites et dessiné sur le
  graphique).
- **Une seule source** : les valeurs viennent de la même fonction de calcul que la partie Limites et
  asymptotes, jamais d'un second calcul indépendant (EC-01 : aucun calcul mathématique nouveau). Une limite que SymPy ne détermine pas : « ? » à sa place, et une
  seule ligne sous le tableau, « Limite non déterminée automatiquement en a⁻. » (resp. a⁺, +∞, −∞).
- **Aucune ligne de justification ajoutée** (guide de rédaction R1, R5) : le tableau est le résumé de
  ce qui est calculé plus haut.
- **Double barre sur toutes les lignes** de la colonne d'une valeur interdite, y compris f'(x) quand
  elle n'a aucune ligne de facteur, **trou compris** (cas C : le moteur écrivait « + + + » au lieu de
  « + ‖ + » ; corrigé avec T06c, **y compris dans l'outil Dérivée**, qui garde pour le reste ses
  flèches seules).
- **Présentation** (validée) : une seule ligne de texte par ligne de tableau, les valeurs ne sont pas
  décalées en hauteur selon la flèche (tableau classique papier), pour tenir à 380 px.

### Exemples (validés)

**A. Pôle simple, limites de signes opposés : f(x) = 1/(x − 2)**

```
f'(x) = −1/(x − 2)² : ne s'annule jamais ; valeur interdite : x = 2.

x        | −∞          2          +∞
−1       |      −      ‖      −
(x − 2)² |      +      ‖      +
f'(x)    |      −      ‖      −
f(x)     | 0    ↘   −∞ ‖ +∞   ↘    0
```

**B. Pôle, limites de même signe : f(x) = 1/(x − 2)²**

```
f'(x) = −2/(x − 2)³ : ne s'annule jamais ; valeur interdite : x = 2.

x        | −∞          2          +∞
−2       |      −      ‖      −
(x − 2)³ |      −      ‖      +
f'(x)    |      +      ‖      −
f(x)     | 0    ↗   +∞ ‖ +∞   ↘    0
```

**C. Trou : f(x) = (x² − 1)/(x − 1)**

```
f'(x) = 1 : ne s'annule jamais ; valeur interdite : x = 1.

x        | −∞          1          +∞
f'(x)    |      +      ‖      +
f(x)     | −∞   ↗    2 ‖ 2    ↗   +∞
```

**Bord d'une zone hachurée (rappel des règles) : f(x) = ln(x² − 4)**, ligne f(x) seulement :

```
x        | −∞      −2           2       +∞
f(x)     | +∞  ↘  −∞ ‖  ░░░░░░  ‖ −∞  ↗  +∞
```

### Critères d'acceptation (T06c)

| Id | Critère | Vérif. |
|---|---|---|
| EC-08 | Ligne f(x) de A : 0, ↘, −∞ ‖ +∞, ↘, 0 ; de B : 0, ↗, +∞ ‖ +∞, ↘, 0 ; de C : −∞, ↗, 2 ‖ 2, ↗, +∞ | [auto-py] (JSON de l'Étude complète) |
| EC-09 | ln(x²−4) : −∞ à gauche de la colonne −2 et à droite de la colonne 2, aucune valeur dans la zone hachurée ; ln x : −∞ à droite de la colonne 0, +∞ en +∞ ; √x : f(0) = 0, pas de limite en 0 | [auto-py] |
| EC-10 | Sur le corpus (liste DV-01 et exemples), chaque valeur écrite contre une barre ou en ±∞ est égale à la limite correspondante de la partie Limites quand celle-ci la donne ; sinon « ? » et la phrase | [auto-py] (propriété) |
| EC-11 | La double barre est sur toutes les lignes de la colonne interdite, f'(x) comprise (C) | [auto-py] |
| EC-12 | Les sorties de l'outil Dérivée sont identiques à avant T06c, sauf la double barre sur f'(x) à toute valeur interdite (instantanés relus un par un) | [auto-py] |
| EC-13 | Rendu à 360 px **sans défilement horizontal** pour les tableaux à 1 ou 2 valeurs critiques (A, B, C, ln(x²−4)) ; plus larges : défilement avec la 1re colonne (libellés) fixe ; double barre continue ; même feuille `tableaux.css` pour les quatre outils ; valeurs jamais sous 0,85 em, aucune information supprimée | [manuel] (captures 360 et 900 px, 16.10.2026) ; feuille commune [auto-py] (`test_tableaux_css.py`) |

## Critères d'acceptation

| Id | Critère | Vérif. |
|---|---|---|
| EC-01 | Les valeurs communes (ED, f′, zéros de f′, limites) sont identiques à celles des outils séparés. La rédaction peut différer, par paramètre (D2) | [auto-py] (`test_resoudre_ec.py`, `test_corpus_etude_complete.py`) |
| EC-02 | L'ED n'est calculé qu'une fois par étude, et `fenetre()` ne recalcule pas l'ED (mise en cache par entrée, D19) | [auto-py] (`test_corpus_etude_complete.py::test_P2_analyse_calculee_une_seule_fois`, compteur des calculs réels, cache vidé avant) |
| EC-03 | `fenetre("e^x", -10, 800)`, `fenetre("e^(-x)", -1000, 10)`, `fenetre("x^2*e^(-x)", -2000, 2000)` réussissent ; les points non calculables sont omis | [auto-py] |
| EC-04 | En cas d'échec de `fenetre`, la courbe affichée reste celle de la dernière fenêtre réussie et un message discret l'indique | [auto-page] (`test_graphique.py`, crochet `window.__echecFenetre`) |
| EC-05 | Sur téléphone, un glissement vertical à un doigt sur le graphique fait défiler la page ; deux doigts zooment et déplacent, sans faire défiler la page, et le point de la courbe sous le milieu des doigts y reste quel que soit le nombre de mouvements livrés par le navigateur | [auto-page] (`test_graphique.py`, émulation tactile de Chrome) + [manuel] (14 vérifications sur téléphone, 21.10.2026) |
| EC-06 | Graduations et coordonnées du graphique sans point décimal (virgule), par la seule fonction `etiquette()` | [auto-page] (`test_graphique.py`) |
| EC-07 | Le graphique est imprimé (image) dans le PDF, en clair même en mode sombre | [manuel] (vérifié sur téléphone, 21.10.2026) |
| EC-14 | `resoudre()` (T12) respecte le schéma de sortie commun, ses cartes sont dans l'ordre des six parties (D1, intertitres compris), celles de la dérivée et des limites sont les cartes des outils séparés, les limites figurent dans le tableau de variations ; instantanés `instantanes/resoudre/etude-complete.json` | [auto-py] (`test_resoudre_ec.py`) |
| EC-15 | Toute partie propre à l'EC a un garde-fou numérique et un message clair en cas de doute (D2) ; tant qu'une partie n'est pas rédigée, elle reste vide | [auto-py] (`test_corpus_etude_complete.py` : oracle mpmath indépendant ; parties 1 à 3, 5 et 6 : `test_parties_ec.py`, garde-fous forcés en échec) |
| EC-16 | Graphe (D15, decisions.md §3) : la fenêtre contient les extremums, les zéros, (0 ; f(0)) et les ronds vides ; pour chaque AH y = L, un x de la fenêtre au-delà de tous ces points et des valeurs interdites où \|f(x) − L\| < 5 % de la hauteur ; un rond vide à chaque point exclu à limite finie et nulle part ailleurs ; zéros, (0 ; f(0)) et extremums marqués | [auto-py] (`test_corpus_etude_complete.py` P8, `test_parties_ec.py` : oracle mpmath, garde-fous forcés) + [auto-page] (`test_graphique.py::test_d15_ronds_vides_et_points_marques`) |
