# Outil « Limites et asymptotes » (3e Ms, Mr)

URL : `/limites-asymptotes/` · moteur : `limites-asymptotes/limites_asymptotes.py` (+ noyau).

## Fonctionnel

- Bornes étudiées, déduites de l'ED : ±∞ si l'ED n'est pas borné de ce côté ; chaque borne finie
  ouverte (côté utile seulement) ; valeur interdite isolée : à gauche et à droite.
- **f rationnelle, en ±∞** (exact, sans SymPy) : mise en évidence du terme de plus haut degré au
  numérateur et au dénominateur, chaque terme écrit explicitement ; deg N < deg D ⇒ y = 0 ;
  égalité ⇒ rapport des coefficients dominants ; deg N = deg D + 1 ⇒ division polynomiale et
  asymptote oblique ; écart ≥ 2 ⇒ branche parabolique.
- **f rationnelle, pôle fini** : factorisation par (x − a), simplification des facteurs communs ;
  limite finie ℓ ⇒ trou dans le graphique en (a ; ℓ) (formulation Q7 ci-dessous) ; sinon signe de
  chaque côté (0⁺ / 0⁻) ⇒ asymptote verticale. Pôle irrationnel : sonde numérique + SymPy.
- **Cas non rationnel (ln, exp, racines mélangés à x)** : valeur par SymPy (racine réelle pour
  x^(p/q), q impair), narration simple ; en ±∞ avec limite infinie, recherche
  d'asymptote oblique (a = lim f/x, b = lim f − ax).
- **Valeur interdite isolée, cas non rationnel** (correction `70e6b1e`) : au moins une limite
  latérale infinie ⇒ asymptote verticale ; deux limites finies égales ⇒ trou ; finies et
  différentes ⇒ pas de limite en a ; limite non déterminée ⇒ aucune conclusion
  (formulations Q7 ci-dessous ; le genre « saut » de `70e6b1e` est remplacé, tâche T08b).
- Bilan des asymptotes en fin de corrigé.

## Conventions

### Croissance comparée (tranché le 14.10.2026, Q1)

- Citée **uniquement** face à une forme indéterminée entre une puissance x^n (n > 0 réel) et une
  exponentielle e^(ax) (a > 0) ou un logarithme : ∞/∞, 0·∞, ou ∞ − ∞ levée par factorisation
  (e^x − x² = e^x(1 − x²/e^x) ; x − ln x = x(1 − ln(x)/x)).
- En ±∞, et en 0⁺ pour le logarithme.
- Limites de référence : en +∞, e^(ax)/x^n → +∞, x^n·e^(−ax) → 0, ln(x)/x^n → 0 ; en −∞,
  x^n·e^(ax) → 0 ; en 0⁺, x^n·ln(x) → 0.
- La phrase **nomme toujours la limite de référence utilisée**, par ex.
  « x²·e^(−x) → 0 en +∞ par croissance comparée (lim x^n e^(−x) = 0) ».
- Jamais ailleurs (x·e^x en +∞ : pas de forme indéterminée ; e^x/x en 0 : pas une croissance comparée).

### Limite finie en une valeur interdite (tranché le 14.10.2026, Q7)

Ne jamais écrire « point de discontinuité » quand a ∉ ED.
- Limites latérales finies et égales à ℓ : « f n'est pas définie en a, mais sa limite y est
  finie (= ℓ) : pas d'asymptote verticale, trou dans le graphique en (a ; ℓ) ».
- Limites latérales finies et différentes : « limites à gauche et à droite différentes : f n'a
  pas de limite en a ; pas d'asymptote verticale ».
- Valeur interdite au bord de l'ED (un seul côté), limite finie ℓ : même formulation que le
  premier cas, avec la limite latérale.

### Rédaction détaillée (tranché le 14.10.2026, Q9)

Chaque limite affichée est rédigée par la **première méthode du cours qui s'applique** :

0. **Opérations et composition**, sans forme indéterminée : chaque sous-expression avec sa limite,
   puis la règle (somme, produit, quotient, composée avec e^u, ln u, √u, u^n).
1. **Mise en évidence** du terme dominant (en ±∞) ou factorisation par (x − a) (en une valeur) ;
   la forme indéterminée est **nommée** (« ∞ − ∞ », « ∞/∞ », « 0·∞ », « 0/0 »).
2. **Expression conjuguée** (∞ − ∞ et 0/0 avec une racine).
3. **Termes dominants** : seulement en ±∞, quotient dont un membre est une composée ; jamais quand les
   termes dominants se compensent ; la justification du remplacement est écrite.
4. **Limites de référence et croissance comparée** (Q1 seulement, voir plus haut).
5. **Bernoulli-L'Hôpital**, en dernier recours, avec ses quatre hypothèses écrites :
   (a) forme 0/0 ou ∞/∞ (0·∞ et ∞ − ∞ d'abord mis en quotient) ; (b) f et g dérivables au voisinage de a
   (sauf peut-être en a) ; (c) g'(x) ≠ 0 au voisinage de a (sauf peut-être en a) ; (d) lim f'/g' existe
   (finie ou infinie), alors lim f/g = lim f'/g'. Au plus deux applications de suite. Si une hypothèse
   n'est pas vérifiée ou si lim f'/g' n'existe pas, la règle n'est pas appliquée et ne conclut rien.

Autres cas rédigés :
- **Valeur interdite sans forme indéterminée** : limite du numérateur, signe du dénominateur à gauche et
  à droite (« 8/0⁻ = −∞ »), conclusion « asymptote verticale d'équation x = a » ;
- **Forme 0/0 en une valeur** : factoriser, simplifier, passer à la limite (avant L'Hôpital) ;
- **Racine en −∞** : « x < 0 donc √(x²) = |x| = −x » chaque fois que x² sort d'une racine ;
- **Asymptote oblique** : division euclidienne (fraction rationnelle) ; sinon a = lim f(x)/x puis
  b = lim (f(x) − ax), chaque limite rédigée ; position relative au voisinage de ±∞ seulement, quand le
  signe de f(x) − (ax + b) se lit directement ;
- **Conclusion de chaque borne** : « asymptote horizontale d'équation y = ℓ », « asymptote verticale
  d'équation x = a », « asymptote oblique d'équation y = ax + b », ou « pas d'asymptote … ».

**Garde-fou.** La valeur de chaque limite est celle du calcul de référence (exact pour les fractions
rationnelles, SymPy sinon). La rédaction calcule sa propre valeur : si elle ne coïncide pas, si une
étape ne peut être justifiée ou si aucune méthode n'aboutit, toutes ses étapes sont abandonnées et la
page écrit « Le calcul détaillé de cette limite n'est pas rédigé ici ; résultat : lim f(x) = … »,
suivie de la conclusion habituelle. Jamais d'étape fausse. Une limite non déterminée (« ? ») reste
sans asymptote (LA-03). Le détail technique va dans la console (clé `detail`, C6).

### Style de rédaction (tranché le 14.10.2026)

Public visé : un élève moyen de gymnase. Une idée par ligne, le vocabulaire du cours, aucun détail de la
mécanique interne (le détail technique va dans la clé `detail` / `controles_detail`, non affichée).

1. **Phrases interdites** : « par continuité de », « est une constante », « la somme / la différence /
   le produit tend vers » quand c'est évident. Une constante se remplace directement ; une limite
   évidente s'écrit en une fois (« x² − 2 → 0 »). Une valeur définie se dit « vaut » (« le numérateur
   vaut 3² − 1 = 8 »).
2. **Le signe d'un dénominateur qui tend vers 0 est toujours justifié** (de même celui d'un argument de ln
   qui tend vers 0), **par un tableau de signes**, construit par le même moteur de signe et rendu comme
   dans les outils « Ensemble de définition » et « Dérivée » (lignes des facteurs, puis le produit ; valeur
   interdite en double barre centrée). Un seul tableau par dénominateur et par argument de ln, en tête de
   l'étude (carte « Tableaux de signes », clé `tableaux_signe`), puis deux lignes courtes lues dans le
   tableau, avec un renvoi explicite : « À gauche de 2, le dénominateur est négatif (cf. tableau de signes de x − 2) :
   il tend vers 0⁻, donc f(x) → 3/0⁻ = −∞. » ; chaque tableau est titré « Signe de x − 2 ».
   Si le tableau ne peut pas être construit, la justification reste en texte (factorisation, signe du
   trinôme, « x − 3 < 0 pour x < 3 », monotonie) ; si rien ne justifie le signe, la limite est donnée avec la
   phrase de repli. Jamais « x vaut 4 » pour une variable qui tend vers 4.
3. **Valeur interdite** : la partie commune une seule fois (valeur interdite, limite du numérateur, signe du
   dénominateur), puis une ligne courte « À gauche : … » et « À droite : … ». Si les deux côtés donnent la
   même limite, une seule conclusion.

4. **Conclusion de chaque valeur interdite** : asymptote verticale, trou ou absence de limite. Quand une
   seule limite latérale est infinie (e^(1/x) en 0 : 0 à gauche, +∞ à droite), on écrit « asymptote verticale
   d'équation x = 0 (du côté droit) ; à gauche, f(x) → 0 ».

Modèle (1/(x² − 2) en −√2) :
> x = −√2 est une valeur interdite.
> Le numérateur vaut 1 et le dénominateur x² − 2 tend vers 0 (voir le tableau de signes).
> (tableau de signes de x² − 2, racines ±√2, en tête de l'étude)
> À gauche de −√2, le dénominateur est positif (cf. tableau de signes de x² − 2) : il tend vers 0⁺, donc f(x) → 1/0⁺ = +∞.
> À droite de −√2, le dénominateur est négatif (cf. tableau de signes de x² − 2) : il tend vers 0⁻, donc f(x) → 1/0⁻ = −∞.
> Asymptote verticale d'équation x = −√2.

## Critères d'acceptation

| Id | Critère | Vérif. |
|---|---|---|
| LA-01 | Aucune asymptote « verticale » n'est annoncée sans au moins une limite latérale infinie | [auto-py] (existe : `test_limites_deux_cotes.py`) |
| LA-02 | (e^x−1)/x et x·ln(x²) en 0 : limite finie, trou en (0 ; 1) et (0 ; 0) ; x/√(x²) en 0 : limites −1 et 1, pas de limite en 0 ; jamais d'asymptote verticale | [auto-py] (existe : `test_limites_deux_cotes.py`, à adapter en T08b) |
| LA-03 | Une limite non déterminée (« ? ») n'est jamais enregistrée comme asymptote, en ±∞ comme en un point | [auto-py] |
| LA-04 | Pour ≥ 40 fonctions, chaque limite annoncée est confirmée par une sonde numérique (x = ±10⁶, a ± 10⁻⁶) ou par `sympy.limit` indépendamment | [auto-py] |
| LA-05 | Fonctions rationnelles : asymptote oblique y = ax + b telle que f(x) − (ax + b) → 0 numériquement | [auto-py] |
| LA-06 | Sorties des exemples et exercices identiques aux instantanés | [auto-py] |
| LA-07 | « croissance comparée » apparaît pour x²·e^(−x) (+∞), x^(1/2)·e^(−x) (+∞), ln(x)/x (+∞), x·ln(x) (0⁺), e^x − x² (+∞), x − ln(x) (+∞), x·e^x (−∞), avec la limite de référence nommée ; jamais pour x·e^x (+∞), e^x/x (0), e^(2x) (±∞) | [auto-py] |
| LA-09 | x^(2/3), x^(1/3), x^(-1/3), x^(4/3), (x−2)^(1/3), x·x^(1/3) : limites en −∞ et en un point négatif justes dans ℝ (racine réelle) ; aucun `Infinity` ni `NaN` dans une sortie (JSON strict) | [auto-py] (`test_racines_reelles.py`, `test_json_strict.py`) |
| LA-08 | Aucune sortie ne contient « point de discontinuité » ni le genre « saut » ; les deux formulations Q7 apparaissent mot pour mot pour (e^x−1)/x, (x²−1)/(x−1) et x/√(x²) en 0 ou 1 | [auto-py] |
| LA-10 | Toute limite étudiée est rédigée (méthode du cours) ou suivie de la phrase de repli mot pour mot ; jamais « lim f(x) = v » seul | [auto-py] |
| LA-11 | Garde-fou : la valeur rédigée égale la valeur de référence ; sinon repli, aucune étape de la méthode, `detail` en console | [auto-py] |
| LA-12 | Chaque limite intermédiaire écrite est confirmée par l'oracle haute précision (corpus de `test_proprietes_limites.py`) | [auto-py] |
| LA-13 | Une forme indéterminée levée est toujours nommée ; aucune forme indéterminée n'est annoncée quand il n'y en a pas | [auto-py] |
| LA-14 | Valeur interdite sans forme indéterminée : limite du numérateur, signe du dénominateur de chaque côté, « ℓ/0^± », asymptote x = a | [auto-py] |
| LA-15 | Ordre des méthodes : la première qui s'applique ; jamais L'Hôpital pour une fraction rationnelle ni quand une limite de référence s'applique | [auto-py] |
| LA-16 | L'Hôpital : hypothèses (a) à (d) écrites ; non appliquée hors 0/0 et ∞/∞, si g' ≠ 0 n'est pas établi, ou si lim f'/g' n'est pas obtenue | [auto-py] |
| LA-17 | Oblique : division sans « + 0 » ni « + − » (rationnelles) ; a et b rédigés (autres) ; position relative au voisinage de ±∞ quand elle se lit | [auto-py] |
| LA-18 | Chaque borne se conclut par une phrase avec l'équation de l'asymptote, ou « pas d'asymptote … » | [auto-py] |
| LA-19 | Écriture : coefficient 3/(2x) (pas de fraction dans une fraction) ; polynôme jamais écrit en quotient « /1 » | [auto-py] |
| LA-20 | Racines en ±∞ : « x < 0 donc √(x²) = \|x\| = −x » en −∞ ; √(4x²+1)/(x+2) → 2 en +∞ et → −2 en −∞ ; √(x²−4x+5) : a = 1, b = −2 en +∞ et a = −1, b = 2 en −∞ ; √(x²+x) − x en −∞ : pas de forme indéterminée, +∞ | [auto-py] |
| LA-21 | Aucune phrase interdite (« par continuité de », « est une constante », « la somme / la différence / le produit tend vers », « Par substitution ») dans les instantanés, les exemples, les exercices et le corpus de tests | [auto-py] |
| LA-22 | Tout dénominateur qui tend vers 0 est suivi d'une ligne « Signe de … » ; tout argument de ln qui tend vers 0 en est précédé | [auto-py] |
| LA-23 | Valeur interdite à deux côtés : « est une valeur interdite », « Le numérateur », « Signe de » une seule fois ; au plus une ligne « À gauche » et une « À droite » ; une seule conclusion si les limites sont égales | [auto-py] |
| LA-24 | Aucun mot de la mécanique interne (SymPy, Abandon, exception, nœud, arbre) dans un texte affiché | [auto-py] |
| LA-25 | Tableau de signes en tête (clé `tableaux_signe`) pour 1/(x²−2), (x+1)/(x²−4), (eˣ+1)/(eˣ−1), ln(x²−4x)/(x−5), (x²−1)/(x−3) : colonnes = valeurs interdites ou zéros, double barre pour un dénominateur ; la lecture du tableau coïncide avec le signe calculé ; sans tableau possible, justification en texte | [auto-py] ; rendu [manuel] |
| LA-26 | Jamais « x est positif (il vaut 4) » : une variable ne « vaut » pas la valeur vers laquelle elle tend (« proche de » si besoin), y compris dans la justification en texte | [auto-py] |
| LA-27 | Chaque valeur interdite se termine par sa conclusion ; une seule limite latérale infinie : « asymptote verticale d'équation x = 0 (du côté droit) ; à gauche, f(x) → 0 » | [auto-py] |
| LA-28 | Toute ligne qui lit un signe dans un tableau renvoie à lui (« cf. tableau de signes de X ») ; chaque tableau est titré « Signe de X » ; ln(x²−4x)/(x−5) : phrase de repli seulement en ±∞ | [auto-py] |
| LA-29 | Termes dominants (L5) : en ±∞, quotient ou produit dont un membre est une racine ; chaque membre est remplacé par son terme dominant avec la justification « rapport → 1 » ; « x < 0 donc √(x²) = \|x\| = −x » en −∞ ; jamais pour une fraction rationnelle ni quand les termes dominants d'une somme se compensent | [auto-py] |
| LA-30 | Expression conjuguée (L4) : ∞ − ∞ avec une racine en ±∞ (√(x²+x) − x → 1/2 en +∞ ; en −∞ pas de forme indéterminée, +∞) ; 0/0 avec une racine en une valeur ((√(x+3) − 2)/(x − 1) → 1/4) ; jamais sans racine | [auto-py] |
| LA-31 | Croissance comparée (L6, T09, Q1) : citée seulement devant une forme indéterminée, limite de référence nommée ; mise en évidence de l'exponentielle (e^x − x² = e^x(1 − x²e^(−x)), (e^x+1)/(e^x−1)) ; jamais pour x·e^x en +∞, e^x/x en 0, e^(2x) | [auto-py] |
| LA-32 | Bernoulli-L'Hôpital (L7) : en dernier recours, hypothèses (a) à (d) écrites (ln(x²−4x)/(x−5) en ±∞, (e^x−1)/x en 0, ln(x)/(x−1) en 1, x·ln(x²) en 0) ; jamais hors forme 0/0 ou ∞/∞, jamais pour une fraction rationnelle ni quand une limite de référence s'applique ; non appliquée (phrase de repli) si g' ≠ 0 ou lim f'/g' n'est pas établi ; au plus deux applications de suite | [auto-py] |
