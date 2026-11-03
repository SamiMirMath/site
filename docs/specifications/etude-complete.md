# Outil « Étude complète de fonction » (3e Ms, Mr)

URL : `/etude-complete/` · moteur : `etude-complete/etude_complete.py`, qui assemble le noyau,
la dérivée et les limites ; adaptateur `etude-complete/resoudre_ec.py`. Les parties propres à l'Étude complète (aujourd'hui les parties 1 et 2 ; plus tard
zéros, signe, ordonnée à l'origine ; bilan) sont dans `etude-complete/parties.py` (créé au chantier `etude-complete`, P3, déclaré dans
`moteur/manifeste.json` avec `ensemble-definition/resoudre_ed.py`, dont il reprend les cartes de condition). Décisions de rédaction : `docs/chantiers/etude-complete/decisions.md`.

## Fonctionnel

- **Six parties titrées, dans l'ordre du corrigé** (D1) : 1. Domaine de définition · 2. Parité · 3. Zéros, signe, ordonnée à
  l'origine · 4. Limites et asymptotes · 5. Dérivée, tableau de variation, extremums · 6. Graphe. Chaque partie s'ouvre par un
  intertitre (carte de style `partie` du format commun : un titre sans cadre, affiché avec la carte qui le suit, hors du compteur
  d'étapes). Une partie que l'outil ne sait pas encore rédiger reste vide (son intertitre seul) : rien plutôt qu'une affirmation
  non démontrée (EC-15). Aujourd'hui : parties 1 et 2 = voir ci-dessous ; 3 vide ; 4 = cartes de l'outil Limites
  (tableaux de signes, une carte par borne, bilan des asymptotes) ; 5 = cartes de l'outil Dérivée (dérivée, signe de f′ et variations,
  avec les limites dans le tableau, T06c) ; 6 = graphique.
- **Partie 1, domaine de définition** (D1, D3 ; P3) : carte « Fonction » (f seule) ; carte « Mise en forme » quand f(x) = e^{haut/bas},
  haut et bas polynômes de degré ≥ 1 écrits développés à coefficients entiers, dont l'un au moins se factorise par mise en évidence de
  c·xᵏ ou par Somme-Produit (trinôme unitaire, deux racines entières distinctes, facteurs par racine croissante) : une ligne par
  méthode, la méthode entre parenthèses, puis « On note g(x) = …, donc f(x) = e^{g(x)}. » (`e^((x^2+x-2)/(6x-12))`, Ex7 du corrigé) ;
  rien à factoriser : pas de carte (`e^(2/(x^2-4))`). Une carte par condition (titre et badge de l'outil ED) ; un dénominateur affine ou
  de la forme ax² + c écrit développé est résolu en chaîne courte, « On résout 6x − 12 = 0 ⇔ 6x = 12 ⇔ x = 2. », « x² − 4 = 0 ⇔ x² = 4
  ⇔ x = −2 ou x = 2 » (racines rationnelles ou k√m) ; un dénominateur x s'écrit « x ≠ 0 » seul ; toute autre condition garde les lignes
  de l'outil ED. Carte « Ensemble de définition » : l'ED encadré (conclusion de l'outil ED), précédé de « Ni logarithme, ni
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
- **Une seule analyse par saisie** (D19) : le résultat de `analyser_complet` (ED) est gardé en cache (`functools.lru_cache`, clé =
  saisie aux espaces réduits et présence de SymPy) ; `etudier()` le passe aux outils Dérivée et Limites (paramètre facultatif
  `analyse` de leur `etudier`, sans effet sur ces outils seuls), et `fenetre()` (zoom) le relit sans recalcul.
- **Graphique** : cadrage automatique (bornes de l'ED, extrema, asymptotes horizontales) ;
  courbe tracée par morceaux de l'ED ; asymptotes en pointillé ; extrema en points pleins ;
  trous (limite finie en une valeur interdite) en ronds vides ; rééchantillonnage de la fenêtre visible.
  **Souris** : molette et boutons (zoom), glisser (déplacement). **Écran tactile** : un doigt fait défiler la page (la courbe ne
  bouge pas), deux doigts déplacent et zooment la courbe, le point sous le milieu des doigts y reste (T19, EC-05).
- Les valeurs communes (ED, f′, zéros de f′, limites) sont exactement celles des outils séparés (EC-01).

## Conventions

- Celles des outils séparés. Limite finie ℓ en une valeur interdite a : rond vide en (a ; ℓ)
  (« trou dans le graphique », Q7) ; limites latérales finies et différentes : rien n'est dessiné
  comme une asymptote (comportement actuel du graphique).
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
| EC-15 | Toute partie propre à l'EC a un garde-fou numérique et un message clair en cas de doute (D2) ; tant qu'une partie n'est pas rédigée, elle reste vide | [auto-py] (`test_corpus_etude_complete.py` : oracle mpmath indépendant ; parties 1 et 2 : `test_parties_ec.py`, garde-fous forcés en échec) |
