# Outil « Exponentielles et logarithmes » (3C)

URL : `/exponentielles-logarithmes/` · moteur : `exponentielles-logarithmes/exp_log.py` (SymPy obligatoire pour décider,
jamais pour écrire) · adaptateur : `resoudre_el.py`. Spécification du 26.10.2026, validée par étapes par l'enseignant (questions Q10 à Q12 tranchées le 26.10.2026).

Références : polycopié 3C (chapitre 2), *Mathématiques 3 ECG*, « Exponentielles et logarithmes », pages imprimées 17 à 40
(pages 18 à 41 du PDF, version du 14.04.2026) ; corrigé détaillé de l'enseignant (`3C_Exponentielles_Logarithmes_Corrige.pdf`,
exercices 2.1 à 2.27), qui fait foi pour la rédaction.

## Périmètre

**Les sections ci-dessous décrivent la 3C** (test sur le chapitre 2). La **filière M (2Ms, 2Mr)** est décrite à la fin (section « Filière M », T35, 28.10.2026) :
ensemble de définition, plusieurs logarithmes, changement de variable, pool M. Les inéquations restent hors de l'outil.

| Id | Type | Exercices du polycopié | Priorité |
|---|---|---|---|
| E1 | Même base : a^A = a^B ⇔ A = B | 2.13 a-o, exemples p. 22-23 | 1 |
| E2 | Isoler l'exponentielle, puis logarithme ; ∅ si le second membre est ≤ 0 ; produit nul | 2.18, 2.21, 2.23, p. 26 n° 1-2, p. 29 | 2 |
| E3 | Bases différentes des deux côtés (facteurs constants et base e compris) | 2.24, p. 26 n° 3 | 3 |
| E4 | Équation logarithmique en une étape (définition du logarithme), logarithmes imbriqués, base inconnue | 2.15 e-g j-l, 2.18 c d f, 2.21 d, 2.22 | 4 |
| C1 | Calculer log_a(y) (saisie sans « = ») | 2.15 a-d h i, 2.20 | 5 |
| C2, C3, E5 | Propriétés avec log 2 ≈ 0,301 (2.25) ; encadrement (2.16) ; inconnue dans la base a¹² = 1,5 (2.5) | | si le temps le permet |

**Quand aucune méthode ne s'applique** (EL-11), deux messages distincts (décision du 26.10.2026) : « Cette équation ne se résout pas avec les méthodes du cours. » seulement pour un vrai
hors-programme (x·2^x = 8…), « Cet outil ne traite pas encore ce type d'équation. » pour une forme du programme que l'outil ne gère pas encore. Le moteur fournit le choix
(`message_non_resolu`) ; l'adaptateur `resoudre_el.py` l'affiche comme erreur de la sortie (étape 7).
Pour un **calcul** sans « = » que le moteur ne traite pas (`message_calcul_non_resolu`) : « Cet outil ne traite pas encore ce type de calcul. » (2 log 5, log 2 + log 3, log₂(e)) ;
« Le logarithme d'un nombre négatif ou nul n'est pas défini. » (log(0), log(−5)) ; « Écrivez une équation (avec =) ou un logarithme à calculer, par exemple log_2(50). » quand la saisie ne contient aucun logarithme (2 + 3, √2).

Hors de cette version : mode « problème
en mots » (l'élève met le problème en équation lui-même ; l'interprétation en années, mois et jours est faite depuis le 28.10.2026, section « Problèmes d'application »), tâtonnement (2.14), graphiques (2.1, 2.9, 2.12), écrire un nombre comme puissance de 10 ou de e (2.17, 2.19).

## Notations

- **log = logarithme en base 10** (10ˣ = y ⇔ x = log(y), p. 24) ; **ln = logarithme en base e** (p. 25) ; **log_a** pour la base a (p. 25).
  Le moteur de l'Ensemble de définition lit `log` comme `ln` : le nouvel outil a sa propre lecture et n'y touche pas.
- Saisie : `log(x)`, `ln(x)`, `log2(x)` ou `log_2(x)`, `log10(x)`, `exp(x)`, `e^x`, `sqrt(x)`, `^` (ou ² et ³), `*`, `/`, multiplication implicite
  (`2x`, `3ln(x)`), virgule ou point décimal, un seul « = », une seule lettre pour l'inconnue.
- **`e` est toujours le nombre e** et ne peut pas être l'inconnue : message « La lettre e désigne le nombre e ≈ 2,718 : choisis une
  autre lettre pour l'inconnue. » Les noms de fonction (`sqrt`, `exp`, `ln`, `log_a`, `log2`, `log`) sont reconnus **avant** les lettres
  isolées, du plus long au plus court.
- **Notation suisse** (Q5, Q12) : apostrophe typographique ’ dès 4 chiffres, **partie entière seulement** (−99’999’995, 1’234,567, 0,0001), `\text{’}` en TeX ; saisie de ' et ’ lue 1000 ;
  « 1 000 » refusé (« Pas d'espace dans un nombre : écrivez 1000 ou 1’000. »). Fonctions dans `moteur/nombres.py`, réutilisables par T23.
- Affichage : `\log`, `\ln`, `\log_{2}` écrits **par notre arbre**, jamais par SymPy (SymPy écrit `log` pour `ln`). Virgule décimale.
- **Fractions et notation scientifique** (décision du 26.10.2026 corrigée le même jour, règle R13 du guide de rédaction, valable pour tous les outils) : toute valeur exacte que l'outil **calcule à partir d'entiers ou de puissances** s'écrit en **fraction** (5/2, 1/10, `log(3/2)`, log₉(27) = 3/2), jamais en décimal ; un décimal **écrit dans l'énoncé** (0,7 ; 1,045 ; −0,02) garde son écriture, **exposant compris** (`log(x) = −0,27` donne `x = 10^(−0,27) ≈ 0,537`) ; quand le calcul part de décimaux de l'énoncé et donne un **décimal fini**, on garde le décimal comme le corrigé (`2000 · 1,045ⁿ = 3805` donne `1,045ⁿ = 1,9025`, pas 761/400 ; `log₄(0,5) = −0,5`) ; un résultat qui n'est pas un décimal fini reste une fraction (13/60). Dans le code : `_nb_exact` (fraction ou décimal selon `_avec_decimaux`), `_nb_ecrit`. Les très grands et très petits nombres restent en **notation scientifique** : une puissance de 10 sous 10⁻³ ou dès 10⁶ n'est pas développée (`x = 10¹⁰`, `x = 10⁻⁴`), et une valeur approchée sous 10⁻³ ou dès 10⁶ s'écrit `3,162 × 10⁻⁵`, `1 × 10¹⁰`. Un rationnel n'a pas de ligne « soit x ≈ … ».
  Valeurs approchées avec « ≈ », jamais avec « ≅ » ni « ~ ». L'expression « valeur approchée » n'est pas écrite (SOC-15).

## Sélecteur de méthode (décision du 27.10.2026)

**Chaque équation exponentielle** (a^f = b, k·a^f = m·b^h, produit nul d'exponentielles, tout ce que résolvent aujourd'hui E1, E2 et E3) se résout de **deux façons**, calculées en une fois ;
la page affiche deux boutons côte à côte au-dessus de la résolution, dans le style des boutons « Méthode géométrique / Méthode algébrique » du simplexe : **« Même base / définition »** (A) et **« Logarithmes »** (B, **défaut**).
Cliquer un bouton affiche l'autre résolution instantanément, sans relancer le calcul ; le choix est gardé d'une équation à l'autre (`localStorage`, dans un `try/catch`, défaut « Logarithmes »). Les équations logarithmiques et les calculs de log_a(y) n'ont pas de sélecteur. Les exercices au hasard ont le même sélecteur.
Boutons accessibles au clavier (`aria-pressed`), lisibles à 360 px ; l'impression montre la méthode affichée (ligne « Méthode : … »). Le format de sortie (`variantes`, `variante_defaut`) est décrit dans le [socle commun](socle-commun.md) ; les autres outils n'en sont pas changés.

**Méthode A « Même base / définition »**, dans l'ordre : (1) la méthode « même base » (E1) : `10^(x+1) = 10^8 ⇔ x + 1 = 8` (même base : a^A = a^B ⇔ A = B) `⇔ x = 7`, e comprise (`e^x = e^3 ⇔ x = 3`, `e^x = e^(x+1) ⇔ 0 = 1`, S = ∅) ;
(2) base 10 ou e **seule** avec un second membre > 0 : la définition du logarithme (`10^x = 8 ⇔ x = log(8)`, `e^x = 7 ⇔ x = ln(7)`) ; (3) second membre ≤ 0 ou membres de signes contraires : la carte « Aucune solution », la même qu'en B ;
(4) un produit nul : chaque facteur se résout par A ; (5) sinon la méthode ne s'applique pas : le bouton reste cliquable et la carte « Même base / définition » (une étape comme les autres) affiche
« **b n'est pas une puissance de a : il faut les logarithmes.** » (`3^x = 20` : « 20 n'est pas une puissance de 3 » ; `2^(x−1) = 3^x` : « 3 n'est pas une puissance de 2 » ; `e^x = 2^x` : « 2 n'est pas une puissance de e » ;
`2^x = 100` : « 100 n'est pas une puissance de 2 ») ; si l'exponentielle doit d'abord être isolée (`3·2^x = 5`), la carte « Isoler l'exponentielle » vient avant le message (« 5/3 n'est pas une puissance de 2 »). Il n'y a alors pas de carte « Solution ».

**Méthode B « Logarithmes »** (toujours disponible) : le logarithme des deux membres (**ln dès qu'une base e apparaît**, log sinon), puis `log(a^A) = A·log(a)` **sur toute puissance écrite**, puis `log(10) = 1` ou `ln(e) = 1` (propriété « car log(10) = 1 », « car ln(e) = 1 », écrite comme la justification « car D ≠ 0 »).
On applique les propriétés **à ce qui est écrit** : `log(10^8) = 8·log(10)`, mais `log(32)` reste `log(32)`.
- `10^(x+1) = 10^8 ⇔ log(10^(x+1)) = log(10^8)` (log des deux membres) `⇔ (x + 1)·log(10) = 8·log(10)` (log(a^A) = A · log(a)) `⇔ x + 1 = 8` (car log(10) = 1) `⇔ x = 7`.
- `10^x = 8 ⇔ log(10^x) = log(8) ⇔ x·log(10) = log(8) ⇔ x = log(8)` (car log(10) = 1).
- `e^x = 7 ⇔ ln(e^x) = ln(7) ⇔ x·ln(e) = ln(7) ⇔ x = ln(7)` (car ln(e) = 1) ; `e^x = e^3 ⇔ x·ln(e) = 3·ln(e) ⇔ x = 3` (car ln(e) = 1).
- **Une puissance de 10 dans un log** (une puissance de e dans un ln) **est réécrite** pour que la propriété s'applique : `log(100) = log(10²) = 2·log(10)`, `log(0,01) = log(10⁻²) = −2·log(10)`, puis `log(10) = 1`. Ainsi `2^x = 100 ⇔ log(2^x) = log(100)` (log des deux membres) `⇔ x·log(2) = log(10²) = 2·log(10)` (log(a^A) = A · log(a)) `⇔ x·log(2) = 2` (car log(10) = 1) `⇔ x = 2/log(2)` (corrigé 2.23 a), et `10^(2x) = 0,01` donne `x = −1`, sans contrôle à la calculatrice.
- **Jamais** `log(10ᵏ) = k`, `ln(e^A) = A` ni la définition du logarithme en B : ces propriétés ne servent qu'en A et pour les calculs de log_a(y).
- Ensuite comme avant : développement, termes en x du côté qui laisse la constante positive, `x(D) = C`, `x = C/D (car D ≠ 0)`, regroupement en un seul logarithme pour des bases différentes (2.24, inchangé). Les autres nombres restent des logarithmes : `2^(x−1) = 32 ⇔ … ⇔ x = 1 + log(32)/log(2)`.
- **x² en exposant** : `2^(x²)·4^x = 8 ⇔ x²·log(2) + x·log(4) = log(8)` (les logarithmes de 4 et de 8 restent écrits), puis `x²·log(2) + x·log(4) − log(8) = 0`, `Δ = (log(4))² − 4·log(2)·(−log(8))` (formule du discriminant), puis `x₁ = (−log(4) − √Δ)/(2·log(2))` et `x₂ = (−log(4) + √Δ)/(2·log(2))` (Δ, x₁ et x₂ portent un nom : les lignes tiennent à 360 px), la ligne finale `S = {x₁ ; x₂}`, puis le contrôle à la calculatrice (x = −3 ou x = 1). Sans terme constant (`2^(x²) = 8^x`) : `x²·log(2) − x·log(8) = 0 ⇔ x(x·log(2) − log(8)) = 0` (un produit est nul si l'un des facteurs est nul).
  Le signe de Δ est décidé exactement quand tous les logarithmes sont des multiples rationnels d'un même log(r), sinon en virgule flottante avec une marge de 10⁻¹² ; Δ < 0 donne la remarque « Δ < 0 : l'équation n'a aucune solution réelle. ».
- Un cas où B diviserait par un coefficient nul alors que les bases sont écrites différemment (4^x = 2^(2x)) reste « pas encore » en B (aucune entrée de la batterie ni du pool).

**Contrôle à la calculatrice** (règle R15 du guide) : quand une solution est un **rationnel** (valeur exacte décidée exactement, jamais par un arrondi) mais que la carte « Solution » l'écrit avec des logarithmes (S = {1 + log(32)/log(2)}), la ligne « soit x ≈ … » est remplacée par
« **Contrôlez à la calculatrice : log(32)/log(2) = 5, on retrouve x = 6.** » (le plus petit sous-arbre à logarithmes dont la valeur est rationnelle ; avec le discriminant : « Contrôlez à la calculatrice : on retrouve x = −3 ou x = 1. »). La carte « Solution » garde `S = {valeur exacte}`.
Une solution non rationnelle garde « soit x ≈ … ». Aucun contrôle quand la solution s'écrit sans logarithme (`10^(2x) = 0,01` : `S = {−1}`).

## Rédaction

Une carte par application de méthode, comme la Factorisation (T21) : « Étape k », méthode en badge, chaîne de « ⇔ » une étape par ligne,
**propriété nommée entre parenthèses (1 à 5 mots)** à chaque ligne, carte finale « Solution ».
**Mise en page (décision du 26.10.2026, règle R14 du guide)** : une chaîne s'affiche **une étape par ligne** comme le corrigé, le ⇔ en début de ligne et aligné, la propriété à droite de la ligne, sous l'expression
sur un écran étroit (≤ 820 px) : aucun défilement horizontal à 360 px, y compris la ligne du discriminant et `−99’999’995` (test de page sur toute la batterie). Réalisation : `rangees_chaine` (moteur : `[(lien, expression, propriété)]`),
puis une grille CSS `.chaine` (page) ; ce n'est pas l'environnement `aligned` de KaTeX, parce qu'une ligne d'`aligned` ne peut pas passer à la ligne ni la propriété passer sous l'expression à 360 px.
Dans la sortie de `resoudre_el.py` : chaque chaîne est un bloc `texte` (style `etape`) `<div class="chaine">` de lignes `<div class="ligne">` (lien, expression et propriété en trois `span`), chaque TeX entre `\(` et `\)` (le « < » est écrit `&lt;`), la remarque du moteur
(« Δ < 0 : l'équation n'a aucune solution réelle. ») est le dernier bloc de la dernière carte d'étapes, et la carte finale est « Solution » (bloc `resultat` = `tex_solution`) pour une équation,
« Résultat » (`tex_resultat`) pour un calcul.
Pour une équation exponentielle, la sortie porte en plus `variantes` (« Même base / définition », « Logarithmes ») et `variante_defaut` = « logarithmes » ; `cartes` est celle de la variante par défaut. Dans la carte « Solution » d'une solution rationnelle écrite avec des logarithmes,
le bloc `texte` qui suit `S = {…}` est la phrase « Contrôlez à la calculatrice : … » (`controle_calculatrice`). Quand la méthode « Même base / définition » ne s'applique pas, sa dernière carte (« Étape k », badge « Même base / définition ») contient la phrase « b n'est pas une puissance de a : il faut les logarithmes. » et il n'y a pas de carte « Solution ».

**Une équation à même base tient en deux cartes au plus** (validé le 26.10.2026) : « Isoler l'exponentielle » (seulement si l'équation
s'écrit k·a^f + c = d…), puis « Même base », qui contient la réécriture des membres (lignes de « = ») **et** la chaîne unique de ⇔
`a^A = a^B ⇔ A = B ⇔ … ⇔ solutions`, comme l'encadré « se ramener à la même base » du corrigé. Quand les deux membres sont déjà écrits
avec la même base (7^(2x+1) = 7^9), il n'y a que la carte « Même base », réduite à la chaîne de ⇔. Pour un trinôme de discriminant
non carré, les lignes « Δ = … » et « x = … ou x = … » suivent la chaîne dans la même carte.

Propriétés nommées (liste fermée, testée) : (on isole le terme exponentiel), (même base : a^A = a^B ⇔ A = B), ((aᵐ)ⁿ = aᵐⁿ),
(aᵐ · aⁿ = aᵐ⁺ⁿ), (1 = a⁰), (log des deux membres), (log(a^A) = A · log(a)), (ln(a^A) = A · ln(a)), (log a − log b = log(a/b)), (log a + log b = log(ab)), (propriétés des logarithmes),
(log_a(a^k) = k), (ln(e^k) = k), (on isole le logarithme), (le logarithme est bien défini), (une base de logarithme est strictement positive et différente de 1), (seule la solution positive convient),
(définition du logarithme), (log(10ᵏ) = k), (ln(1) = 0), (une exponentielle est strictement positive), (aucune solution),
(un produit est nul si l'un des facteurs est nul), (formule du discriminant), (changement de base), (log(ab) = log a + log b), (ln des deux membres), (ln(e^A) = A),
(ln(a^A) = A · ln(a)), (exponentielle des deux membres), (10^(log(A)) = A, A > 0), (e^(ln(A)) = A, A > 0), (a^(log_a(A)) = A, A > 0),
ainsi que les justifications (car log(10) = 1), (car ln(e) = 1) et de division (car D ≠ 0), où D est le coefficient logarithmique (1 − ln 2, log 2 − log 3). « définition du logarithme », « log(10ᵏ) = k » et « ln(e^k) = k » ne servent plus qu'en méthode A et pour les calculs de log_a(y), jamais en méthode B.

**Cartes de la méthode « logarithme »** (étape 3 ; depuis le 27.10.2026 la méthode « Logarithmes » (B) ci-dessus remplace le log des deux membres de cette rédaction, la définition du logarithme ne reste qu'en méthode A) : « Isoler l'exponentielle » (si besoin), puis « Définition du logarithme » (base 10 ou base e : `10^f = b ⇔ f = log(b)`,
`e^f = b ⇔ f = ln(b)`) ou « Logarithme des deux membres » (toute autre base) ou « Aucune solution » (second membre ≤ 0). Un produit nul donne « Produit nul » (la ligne
`P₁·P₂ = 0 ⇔ P₁ = 0 ou P₂ = 0`), puis une carte « Facteur 1 », « Facteur 2 »… qui reprend les lignes de la résolution de chaque facteur. Une équation du premier
degré dont le second membre contient un logarithme (x = ln 3, 2x = ln(0,1)) a la carte « Équation du premier degré » (aucune carte quand x est déjà isolé).

**Carte de la méthode « bases différentes »** (étape 4, corrigé 2.24 ; reprise par la méthode B, avec `log(10)` et `ln(e)` remplacés par 1 par la propriété « car … » et non plus par `log(10ᵏ) = k`) : `k · a^f = m · b^h` (k et m constantes facultatives, f et h du 1er degré). Une carte « Bases différentes », une seule chaîne :
`k·a^f = m·b^h ⇔ log(k·a^f) = log(m·b^h)` (log des deux membres), puis, s'il y a des facteurs constants, `⇔ log(k) + log(a^f) = log(m) + log(b^h)` (log(ab) = log a + log b),
`⇔ log(k) + f · log(a) = log(m) + h · log(b)` (log(a^A) = A · log(a)), le développement `x · log(2) − log(2) = …`, puis les termes en x mis en facteur **du côté qui laisse la constante positive**
(`x(log 2 − log 3) = log 2` en 2.24 a ; `log 4 = x(3 log 6 − log 4)` en b ; `log 3 + 4 log 2 = x(log 3 − log 2)` en c), les termes positifs d'abord, les constantes de même logarithme réunies
(2 · 2^(x−1) = 3^x donne x log 2 = x log 3), `x = N / D (car D ≠ 0)`, puis `= log(N') / log(D')` avec N et D regroupés en un seul logarithme. La propriété de ce dernier lien est
(log a − log b = log(a/b)) quand il n'y a que des différences de deux logarithmes, (log a + log b = log(ab)) pour des sommes de deux logarithmes, (propriétés des logarithmes) sinon, et chaque
regroupement non immédiat est montré dans une ligne « car » en dessous (`3 log 6 − log 4 = log(6³/4) = log 54`). log(10ᵏ) = k : une base ou un facteur 10ᵏ n'écrit pas de logarithme
(`x(1 − log 3) = log 3`), et aucun regroupement n'est alors fait. Les bases sont écrites comme dans l'énoncé ((1/2)^x garde log(1/2)). Quand il n'y a pas de constante (3^x = 2^x), la chaîne se
termine par `x(log 3 − log 2) = 0 ⇔ x = 0 (car log 3 − log 2 ≠ 0)`.

**Base e** : dès qu'une base e apparaît, on applique **ln** (pas log) aux deux membres, avec ln(e^A) = A (la ligne `ln(e^x) = ln(2^x) ⇔ x = x · ln(2)` porte cette seule propriété ; ln(2^x) = x · ln(2) y est implicite),
et les termes en x sont réunis sur une ligne à part avant la mise en facteur : `e^x = 2^x ⇔ ln(e^x) = ln(2^x) ⇔ x = x·ln(2) ⇔ x − x·ln(2) = 0 ⇔ x(1 − ln(2)) = 0 ⇔ x = 0` (car 1 − ln(2) ≠ 0), S = {0} ;
`e^x = 2^(x+1)` donne `x = ln(2) / (1 − ln(2))`, soit x ≈ 2,259. Avec une base e, aucun regroupement en un seul logarithme (le dénominateur contient le nombre 1 = ln e).

**Signes** : `k · a^f` et `m · b^h` de signes contraires donnent S = ∅ (« une exponentielle est strictement positive », carte « Aucune solution ») ; deux membres négatifs (−2^x = −3^(x+1)) sont multipliés par −1 (carte « Isoler les exponentielles », corrections de l'audit, groupe 3).
Hors de la méthode (message « pas encore », jamais « hors programme ») : un exposant du 2ᵉ degré ou plus (2^(x³) = 8), une somme d'exponentielles (message hors-programme si les bases diffèrent, EL-11). La base e est traitée depuis le 27.10.2026 (e^x = e^3, e^x = e^(x+1)).

**Cartes de la méthode « définition du logarithme »** (étape 5, corrigé 2.15, 2.18, 2.21, 2.22 ; **remplacée le 27.10.2026 par l'exponentielle des deux membres**, voir la section suivante ; ce qui suit décrit les cartes avant ce changement, les écritures exactes et la Vérification restent) : « Isoler le logarithme » (si besoin : `2 log x − 5 = 0 ⇔ 2 log x = 5 ⇔ log x = 5/2`, propriété « on isole le logarithme »),
puis « Définition du logarithme » : une seule chaîne `log_a(u) = c ⇔ u = a^c` (définition du logarithme), l'écriture exacte de a^c ajoutée par « = » quand le cours la donne
(`x = 10³ = 1’000`, `10⁻¹ = 1/10`, `10^(5/2) = 100√10`, `10^1,5 = 10√10` quand l'énoncé écrit 1,5, `10^0 = 1`, `2⁴ = 16` ; jamais pour e^c, ni pour 10¹⁰ et 10⁻⁴, laissés en notation scientifique). Les logarithmes imbriqués s'épluchent de l'extérieur vers l'intérieur, une étape par logarithme
(`log(log(log x)) = 0 ⇔ log(log x) = 10⁰ = 1 ⇔ log x = 10¹ = 10 ⇔ x = 10¹⁰`). Un argument du 1er degré se résout comme à la main : `5 − x = 10⁸ ⇔ x = 5 − 10⁸ = −99’999’995` (q − x = c donne x = q − c), `2x + 1 = 10⁸ ⇔ 2x = 10⁸ − 1 ⇔ x = (10⁸ − 1)/2` ;
un argument du 2ᵈ degré (`log(x²) = 2`) continue dans la même chaîne comme la méthode « même base » (`x² = 10² = 100 ⇔ x² − 100 = 0 ⇔ (x + 10)(x − 10) = 0 ⇔ x = −10 ou x = 10`), S = ∅ si Δ < 0.
**Vérification** (carte à part, seulement quand l'argument d'un seul logarithme n'est pas x seul) : `5 − x = 10⁸ > 0 (le logarithme est bien défini) ✓`.
**Base inconnue** `log_x(n) = k` (k entier de 1 à 12 ; si n n'est pas une puissance k-ième, la racine reste écrite : `x² = 255 ⇔ x = √255 ou x = −√255`, S = {√255}, soit x ≈ 15,969 ; `x³ = 2 ⇔ x = 2^(1/3)`) : carte « Condition » (`x > 0 et x ≠ 1`, une base de logarithme est strictement positive et différente de 1), puis `x^k = n`, `x = r ou x = −r` pour k pair, et une ligne
« seule la solution positive convient ». Pas encore traités (message « pas encore ») : second membre avec un logarithme, plusieurs logarithmes, base inconnue d'exposant non entier, trinôme à coefficients non entiers (`log(x²) = −1`), argument de degré 3 ou plus (exposants négatifs ou nuls et argument 1 : corrections de l'audit, groupe 6).

**Équations logarithmiques : l'exponentielle des deux membres** (décision du 27.10.2026, pas de sélecteur) : la définition du logarithme est remplacée par l'application de l'exponentielle aux deux membres, puis `10^(log(A)) = A`. Badge de la carte : « Exponentielle des deux membres ».
`log(x+1) = 7 ⇔ 10^(log(x+1)) = 10^7` (exponentielle des deux membres) `⇔ x + 1 = 10^7` (10^(log(A)) = A, A > 0) `⇔ x = 10^7 − 1`, puis la Vérification (`x + 1 = 10^7 > 0` ✓). Avec ln : `e^(ln(A)) = A` ; avec une base a : `a^(log_a(A)) = A`.
Base inconnue : `log_x(256) = 4 ⇔ x^(log_x(256)) = x^4 ⇔ 256 = x^4`, puis la condition sur la base et la solution positive comme avant. Logarithmes imbriqués : **une paire de lignes par couche** (`log(log(x)) = 1 ⇔ 10^(log(log(x))) = 10^1 ⇔ log(x) = 10 ⇔ 10^(log(x)) = 10^10 ⇔ x = 10^10`).
Les écritures exactes (`= 10³ = 1’000`, `10^1,5 = 10√10`) et les cas « pas encore » restent.

**Calcul de log_a(y)** (étape 6, corrigé 2.15 a-d h i, 2.20 ; saisie sans « = », `calculer_logarithme`, résultat par `tex_resultat`) : une carte « Calcul ».
Si y = aᵏ (k entier ou rationnel : 64 = 8², 1/25 = 5⁻², 1 = 7⁰, 20 = 20¹) : une ligne `y = aᵏ`, puis `log_a(y) = log_a(aᵏ) = k` (log_a(a^k) = k, ou log(10ᵏ) = k en base 10),
résultat `log₈(64) = 2`. Quand k n'est pas entier, la première ligne passe par la racine de la base : `√2 = 2^(1/2) = (4^(1/2))^(1/2) = 4^(1/4)` (corrigé 2.20 h), `27 = 3³ = (9^(1/2))³ = 9^(3/2)`,
`3 = 27^(1/3)`. `ln(1) = 0` (ln(1) = 0), `ln(e) = 1` et `ln(e^k) = k` (ln(e^k) = k). Sinon : « y n'est pas une puissance de a (aʲ = … < y < … = aʲ⁺¹) » (encadrement entre deux puissances
consécutives, pour un rationnel y et une base > 1), puis `log_a(y) = log(y)/log(a)` (changement de base), résultat `log₂(50) = log(50)/log(2) ≈ 5,644` ; en base 10 ou e, aucune ligne de changement de
base : `log(50) ≈ 1,699`, `ln(7) ≈ 1,946`. Pas encore traités : plusieurs logarithmes (2 log 5, log 2 + log 3, calcul avec log 2 ≈ 0,301 : C2), argument contenant e (hors ln(e^k)), argument nul, négatif ou non rationnel (sauf racine carrée et puissance rationnelle).

**Isoler x** : `x − a = c` donne `x = a + c` (corrigé 2.23 d : x = 1 + 1/log(3), jamais c + a) ; `x + a = c` donne `x = c − a` ; `p·x = c` donne `x = c/p` (non simplifié : Q11).

**Valeur exacte d'abord, puis ≈** à 3 décimales (corrigé p. 1 ; en notation scientifique sous 10⁻³ et dès 10⁶), jamais un « ≈ » sans la valeur exacte juste avant sur la même ligne.
log(10^k) = k et ln(e^k) = k sont évalués ; log a − log b est regroupé en log(a/b) seulement dans les bases différentes (E3) ; sinon la valeur exacte
est gardée **telle que la donne la chaîne** : `ln(25/37)/(−0,02)` n'est pas simplifié en `−50 · ln(25/37)` (Q11).

**Pas d'ensemble de définition en 3C** : le polycopié n'en parle nulle part. Seules deux justifications, celles de ton corrigé :
- logarithme dont l'argument contient l'inconnue : **Vérification** après la résolution, « 5 − x = 10⁸ > 0 : le logarithme est bien défini. ✓ » ;
  une solution qui donnerait un argument ≤ 0 est rejetée avec sa raison ;
- base inconnue : condition annoncée avant, « x > 0 et x ≠ 1 (une base de logarithme est strictement positive et différente de 1) », puis
  « seule la solution positive convient ».

**log(x²)** : s'il apparaît (log(x²) = 2), l'équation se résout par la **définition** (x² = 10², x = 10 ou x = −10, vérification x² > 0) ;
on n'écrit jamais 2 log|x|, et 2 log(x) ne s'écrit jamais non plus, même en filière M (on regroupe, on ne développe pas : section « Filière M »).

**Sens d'une inégalité** : aucune inégalité à résoudre en 3C (pas d'inéquation). Les seules inégalités sont les vérifications d'argument
(« > 0 ») et l'encadrement C3, justifié par « log est croissante » (corrigé 2.16).

## Exemples de rédaction (valeurs vérifiées avec mpmath le 26.10.2026 ; mis à jour le 27.10.2026 pour le sélecteur)

Les exemples 1 et 2 sont la méthode A (« Même base / définition »), les exemples 3, 5, 9 à 12 la méthode B (« Logarithmes »), les exemples 6, 7 et 13 des équations logarithmiques (exponentielle des deux membres).

**1. Méthode A, même base — 3^(x+1) − 27 = 0** (p. 22)
Étape 1 · Isoler l'exponentielle : `3^(x+1) − 27 = 0 ⇔ 3^(x+1) = 27` (on isole le terme exponentiel).
Étape 2 · Même base : `27 = 3³`, donc `3^(x+1) = 3³ ⇔ x + 1 = 3` (même base : a^A = a^B ⇔ A = B) `⇔ x = 2`.
Solution : `S = {2}`.

**2. Méthode A, même base, degré 2 — 2^(x²) · 4^x = 8** (2.13 o)
Étape 1 · Même base : `4^x = (2²)^x = 2^(2x)` ((aᵐ)ⁿ = aᵐⁿ) ; `2^(x²) · 2^(2x) = 2^(x²+2x)` (aᵐ · aⁿ = aᵐ⁺ⁿ) ; `8 = 2³` ;
puis, dans la même carte, une seule chaîne de ⇔ :
`2^(x²+2x) = 2³ ⇔ x² + 2x = 3` (même base) `⇔ x² + 2x − 3 = 0 ⇔ (x + 3)(x − 1) = 0 ⇔ x = −3 ou x = 1`.
Solution : `S = {−3 ; 1}`.

**3. Méthode B — 2^x = 100** (2.23 a)
`2^x = 100 ⇔ log(2^x) = log(100)` (log des deux membres) `⇔ x · log(2) = log(100) = log(10²) = 2 · log(10)` (log(a^A) = A · log(a)) `⇔ x · log(2) = 2` (car log(10) = 1)
`⇔ x = 2 / log(2)`. Solution : `S = {2 / log(2)}`, soit `x ≈ 6,644`. Méthode A : « 100 n'est pas une puissance de 2 : il faut les logarithmes. »

**4. Aucune solution — 5^(8x) = −25** (2.23 h)
`5^(8x) > 0` pour tout x (une exponentielle est strictement positive), alors que `−25 < 0` : aucune solution. `S = ∅`.

**5. Bases différentes — 2^(x−1) = 3^x** (2.24 a), comme le moteur le produit (une carte « Bases différentes »)
`2^(x−1) = 3^x ⇔ log(2^(x−1)) = log(3^x)` (log des deux membres) `⇔ (x − 1) · log(2) = x · log(3)` (log(a^A) = A · log(a))
`⇔ x · log(2) − log(2) = x · log(3) ⇔ x(log(2) − log(3)) = log(2)`
`⇔ x = log(2) / (log(2) − log(3))` (car log(2) − log(3) ≠ 0) `= log(2) / log(2/3)` (log a − log b = log(a/b)). Solution : `S = {log(2) / log(2/3)}`, soit `x ≈ −1,710`.
Variante 2.24 b, 4^(x+1) = 6^(3x) : `… ⇔ log(4) = x(3 log(6) − log(4)) ⇔ x = log(4) / (3 log(6) − log(4)) = log(4) / log(54)` (propriétés des logarithmes),
suivi de la ligne `3 log(6) − log(4) = log(6³/4) = log(54)`.

**6. Équation logarithmique — log(5 − x) = 8** (2.15 l)
`log(5 − x) = 8 ⇔ 10^(log(5 − x)) = 10⁸` (exponentielle des deux membres) `⇔ 5 − x = 10⁸` (10^(log(A)) = A, A > 0) `⇔ x = 5 − 10⁸ = −99’999’995`.
Vérification : `5 − x = 10⁸ > 0`, le logarithme est bien défini ✓. `S = {−99’999’995}`.

**7. Base inconnue — log_x(256) = 4** (2.22 b)
Condition : `x > 0` et `x ≠ 1` (une base de logarithme est strictement positive et différente de 1).
`log_x(256) = 4 ⇔ x^(log_x(256)) = x⁴` (exponentielle des deux membres) `⇔ 256 = x⁴` (a^(log_a(A)) = A, A > 0) `⇔ x = 4 ou x = −4` ; seule la solution positive convient. `S = {4}`.

**8. Calcul — log_4(√2)** (2.20 h) et **log_2(50)**
`√2 = 2^(1/2) = (4^(1/2))^(1/2) = 4^(1/4)`, donc `log_4(√2) = 1/4`.
`50` n'est pas une puissance de 2 (`2⁵ = 32 < 50 < 64 = 2⁶`) : `log_2(50) = log(50) / log(2)` (changement de base) `≈ 5,644`.

**9. Application, méthode B — 37 · e^(−0,02t) = 25** (p. 29)
`37 · e^(−0,02t) = 25 ⇔ e^(−0,02t) = 25/37` (on isole le terme exponentiel) `⇔ ln(e^(−0,02t)) = ln(25/37)` (ln des deux membres) `⇔ −0,02t · ln(e) = ln(25/37)` (ln(a^A) = A · ln(a))
`⇔ −0,02t = ln(25/37)` (car ln(e) = 1) `⇔ t = ln(25/37) / (−0,02) ≈ 19,602` (la forme que donne la chaîne, non simplifiée en −50 · ln(25/37) : Q11). Méthode A : `e^(−0,02t) = 25/37 ⇔ −0,02t = ln(25/37)` (définition du logarithme).

**10. Méthode B, solution rationnelle — 2^(x−1) = 32**
`2^(x−1) = 32 ⇔ log(2^(x−1)) = log(32)` (log des deux membres) `⇔ (x − 1) · log(2) = log(32)` (log(a^A) = A · log(a)) `⇔ x − 1 = log(32)/log(2)` (car log(2) ≠ 0) `⇔ x = 1 + log(32)/log(2)`.
Solution : `S = {1 + log(32)/log(2)}`. Contrôlez à la calculatrice : `log(32)/log(2) = 5`, on retrouve `x = 6`. Méthode A : `32 = 2⁵`, `2^(x−1) = 2⁵ ⇔ x − 1 = 5 ⇔ x = 6`, `S = {6}`.

**11. Méthode B, x² en exposant — 2^(x²) · 4^x = 8**
`log(2^(x²) · 4^x) = log(8)` (log des deux membres) `⇔ log(2^(x²)) + log(4^x) = log(8)` (log(ab) = log a + log b) `⇔ x² · log(2) + x · log(4) = log(8)` (log(a^A) = A · log(a)) `⇔ x² · log(2) + x · log(4) − log(8) = 0`,
`Δ = (log(4))² − 4 · log(2) · (−log(8))` (formule du discriminant), `x₁ = (−log(4) − √Δ) / (2 · log(2))`, `x₂ = (−log(4) + √Δ) / (2 · log(2))`. Solution : `S = {x₁ ; x₂}`. Contrôlez à la calculatrice : on retrouve `x = −3` ou `x = 1`.

**12. Méthode A qui ne s'applique pas — 3 · 2^x = 5**
Étape 1 · Isoler l'exponentielle : `3 · 2^x = 5 ⇔ 2^x = 5/3`. Étape 2 · Même base / définition : « 5/3 n'est pas une puissance de 2 : il faut les logarithmes. » Méthode B : `2^x = 5/3 ⇔ log(2^x) = log(5/3) ⇔ x · log(2) = log(5/3) ⇔ x = log(5/3)/log(2)`, soit `x ≈ 0,737`.

**13. Imbriqués — log(log(x)) = 1**
`log(log(x)) = 1 ⇔ 10^(log(log(x))) = 10^1` (exponentielle des deux membres) `⇔ log(x) = 10` (10^(log(A)) = A, A > 0) `⇔ 10^(log(x)) = 10^10` `⇔ x = 10^10` (10^(log(A)) = A, A > 0). `S = {10^10}`.

## Problèmes d'application (décision du 28.10.2026)

Les problèmes de capitalisation et de dépréciation reviennent souvent au test (`3Q = Q(1+3,75/100)^x` : « à partir de combien de temps un capital triple-t-il à 3,75 % ? »). Trois ajouts, validés par l'enseignant le 28.10.2026.

**1. Paramètre** (Q, C, C0, C_0, V0, V_0…). La **casse des lettres est gardée** (Q ≠ q ; les noms de fonction restent insensibles à la casse ; `E` reste le nombre e). Une **majuscule suivie de chiffres** (`C0`, `V0`) ou une lettre suivie de `_` et de chiffres
(`C_0`) est **un seul nom** (écrit `C_{0}` en TeX) ; `x2` garde son message actuel. **L'inconnue est la lettre de l'exposant** ; toute autre lettre est un **paramètre** s'il est un facteur (puissance 1) de chaque membre
(`3Q`, `Q·(…)^x`, `V0/2`, `Q` seul) : il se simplifie. Sinon, message clair : « Cette équation contient deux inconnues : Q et x. » (plusieurs : « … : Q, r et n. »). Sans lettre en exposant, le message « Une seule inconnue… » reste.
Carte **« Simplifier par Q »** : `3Q = Q · 1,0375^x ⇔ 3 = 1,0375^x` (on divise les deux membres par Q, Q > 0 : une quantité de départ est positive). Valable aussi pour un paramètre au dénominateur (`V0/2 = V0 · 0,8^n ⇔ 1/2 = 0,8^n`).

**2. Base calculée.** Une base constante écrite avec un taux (`1 + 3,75/100`, `1 − 20/100`, `1 + 0,035`, `1 + 3,75 %`) devient **un décimal** (ou une fraction si le décimal ne s'arrête pas) sur une ligne à part :
`1 + 3,75/100 = 1,0375` (carte **« Calculer la base »**, commune aux deux méthodes, avant « Simplifier par Q »). Le signe **%** est accepté après un nombre (`3,75 %` vaut 3,75/100, écrit `3{,}75\,\%`) ; ailleurs il est refusé par un message de lecture. Ensuite, les deux méthodes (« Même base / définition », « Logarithmes ») s'appliquent comme d'habitude.
Exception assumée à R13 : un taux `t/100` ou `t %` donne un décimal (1,0375), pas une fraction (1 + 3,75/100 = 163/160) ; une base écrite avec des entiers seulement (`1 + 1/3`) reste une fraction (4/3).

**3. Interprétation en années, mois et jours** (carte « Interprétation », **après** la carte « Solution »). Conventions : **1 an = 12 mois, 1 mois = 30 jours** (usance commerciale) ; les jours sont **arrondis à l'entier supérieur** (« au bout de »), avec une phrase qui le justifie ;
**les restes sont calculés à pleine précision, jamais à partir des valeurs arrondies affichées** ; les lignes affichent **3 décimales**. Exemple `3Q = Q(1+3,75/100)^x`, x = log(3)/log(1,0375) ≈ 29,842 (valeur vérifiée avec mpmath : 29,842263…) :
`29 ans ; reste 0,842 an` · `0,842 · 12 ≈ 10,107 mois → 10 mois ; reste 0,107 mois` · `0,107 · 30 ≈ 3,215 jours → 4 jours` · phrase d'arrondi · **« Au bout de 29 ans, 10 mois et 4 jours. »**
Cas limites : 0 mois et 0 jour sont écrits ; un arrondi qui donne 30 jours se reporte sur le mois, 12 mois sur l'année (`2C = C·1,045ⁿ` : n ≈ 15,747 → 29,029 jours → 30 jours = 1 mois → « 15 ans, 9 mois et 0 jour ») ;
solution exacte (`2^x = 8`) : « = » au lieu de « ≈ » ; solution négative : « La solution est négative : la situation décrite n'arrive jamais. » ; S = ∅ : « Aucune solution : la situation décrite n'arrive jamais. » ; x = 0 : « La situation est atteinte dès le départ. »
Valable en croissance (base > 1) et en dépréciation (base < 1).

**Case à cocher** (question 4, option (a) retenue) : la page affiche, sous les boutons de méthode, la case « Problème d'application (temps en années) » **seulement quand l'interprétation a un sens** (équation exponentielle à une solution ou sans solution ; pas d'équation logarithmique, pas de calcul, pas de x² à deux solutions, pas de méthode A sans carte « Solution »).
Elle est **pré-cochée** quand l'équation contient un paramètre ou que l'inconnue est n (pas t : le temps peut être en minutes), décochable. Cocher ou décocher ajoute ou retire la carte « Interprétation » sans appel au moteur, en gardant le nombre de cartes visibles ;
le choix de l'élève vaut pour l'équation affichée (mémoire de la page, pas de `localStorage` : le défaut dépend de l'équation ; il se garde au changement de méthode et quand on recalcule la même saisie, une nouvelle saisie reprend l'état de départ). La case est `no-print` ; la carte s'imprime si elle est cochée. Format de sortie : `option` (socle commun, SOC-18). La carte finale est un texte en gras (« Au bout de 29 ans, 10 mois et 4 jours. »), pas une formule : elle passe à la ligne à 360 px. Clavier de la page : touches %, n, t, Q, C, V ; deux exemples ajoutés.

**Exemples** (valeurs vérifiées avec mpmath) : `3Q = Q(1+3,75/100)^x` → 29,842 → 29 ans, 10 mois, 4 jours · `2C = C(1+0,04)^n` → 17,673 → 17 ans, 8 mois, 3 jours · `C0·1,05^n = 2·C0` → 14,207 → 14 ans, 2 mois, 15 jours ·
`V0/2 = V0(1−20/100)^n` → 3,106 → 3 ans, 1 mois, 9 jours · `2000·1,045^n = 3805` (sans paramètre, inconnue n) → 14,612 → 14 ans, 7 mois, 11 jours · `37e^(−0,02t) = 25` → 19,602 (t non pré-cochée) → 19 ans, 7 mois, 7 jours.

## Exercices au hasard (pool C)

Générés en Python (`exercice(niveau, graine)`, déterministe), inconnue **x**, énoncés **variantes** de ceux du polycopié. Pool M séparé, plus
tard (clé prévue, rien de codé). Gabarits **validés (Q10, 26.10.2026)** :

| Niveau (poids) | Gabarit | Exemple |
|---|---|---|
| facile (30 %) | a^(px+q) = a^k avec a ∈ {2, 3, 5, 10}, p ∈ [1 ; 3], solution entière ; ou log(x) = k, ln(x) = c, log_a(x) = k | 3^(2x+1) = 81 ; log₂(x) = 5 |
| moyen (30 %) | k · a^(px+q) = b avec b/k puissance exacte ; bases puissances d'une même base (4, 8, 9, 25, 27) ; log(5 − x) = k | 4^(3x+1) = 8 ; 2 · 3^(x−1) = 18 |
| logarithme (30 %) | a^(px+q) = b sans puissance exacte ; k · e^(cx) = b ; a^x = −b (∅) | 4^(2x+1) = 60 ; 5^(8x) = −25 |
| difficile (10 %) | bases différentes a^(x+p) = b^(qx) ; a^(x²)·b^x = c ; log_x(n) = k avec n = m^k ; log(log(x)) = c | 2^(x−1) = 3^x ; log_x(256) = 4 |

Contraintes du générateur (Q10, 26.10.2026) : quand x² est en exposant, le trinôme obtenu a des racines **entières ou rationnelles simples, jamais un
discriminant non carré** (le moteur sait écrire des racines irrationnelles, le générateur n'en propose pas) ; environ **1 exercice sur 10 du niveau
« logarithme »** a un second membre ≤ 0 (S = ∅, par exemple 5^(8x) = −25).
**Réalisation** (`exercice(niveau, graine)` dans `exp_log.py`, `exercice_json(niveau)` pour la page ; niveaux `facile`, `moyen`, `logarithme`, `difficile`, énoncé « Résoudre : … ») : a^(x²)·b^x = c n'est tiré qu'avec b et c puissances de a (2^(x²)·4^x = 8, 3^(x²)·27^x = 81 : même base, racines entières −3 et 1 ou −4 et 1), jamais avec des bases différentes ;
les bases différentes viennent de a^(x+p) = b^(qx) avec a et b deux nombres de {2, 3, 5, 6, 7, 10} (jamais une puissance de l'autre) ; le niveau « logarithme » n'a jamais un second membre qui soit une puissance de la base (ni b/k pour k·a^f = b).
**Applications** (niveau « logarithme », environ 30 % de ses tirages, inconnue n) : `f·C = C·(1 + t/100)^n` (f = 2 ou 3, t de 0,5 % à 8 %), `C/2 = C·(1 − t/100)^n` et `C/4` (t de 5 % à 25 %), paramètres C, Q, C0, V0, écritures `(1+t/100)`, `(1+t %)`, `1,0t` ; `A·1,0t^n = B` sans paramètre. Les 10 % de second membre ≤ 0 restent.
**Le pool n'a jamais d'exposant de degré 3 ou plus** (2^(x³) = 8, décision du 26.10.2026) : le logarithme le résoudrait, mais ce n'est pas un exercice du cours. Le degré 2 ne vient que de a^(x²)·b^x = c et de a^(x²) = a^(rx+s) avec des racines simples (Q10).

## Critères d'acceptation

| Id | Critère | Vérif. |
|---|---|---|
| EL-01 | Pour chaque entrée de la batterie (`tests/python/cas_el.py` : 2.13 a-o, 2.15, 2.18, 2.20, 2.21, 2.22, 2.23, 2.24, 2.26, 2.27 et les exemples p. 22-23, 26, 28-29), l'ensemble solution exact et la valeur ≈ à 10⁻³ sont ceux attendus ; la batterie est vérifiée une fois contre les solutions p. 38-40 et contre le corrigé | [auto-py] |
| EL-02 | Oracle indépendant : chaque solution, substituée dans l'équation de l'énoncé avec mpmath, donne un écart < 10⁻⁹ ; `solveset` sur ℝ donne le même nombre de solutions ; S = ∅ confirmé ; tirages aléatoires a^(px+q) = a^(rx+s), k·a^f = b, log_b(u) = c comparés à l'oracle | [auto-py] |
| EL-03 | Tokeniseur : `ln`, `exp`, `log2`, `log_3`, `log10`, `sqrt` lus comme fonctions avant les lettres ; `2x`, `3ln(x)`, `xlog(x)` multiplication implicite ; `e^x = 7` : e est la constante ; `e` comme seule lettre, `2e = 5`, `e^2 = e` : refusés avec le message prévu ; `x + e = 3` accepté | [auto-py] |
| EL-04 | Tout le TeX vient de l'arbre : une équation en e^x ne produit que `\ln`, une équation en base 10 que `\log` ; `exp_log.py` et `resoudre_el.py` ne contiennent ni `latex(` ni `arbre_depuis_sympy` | [auto-py] (analyse du texte source) |
| EL-05 | `log` = base 10, `ln` = base e, `log_a` = base a, sur toute la batterie (valeur numérique de chaque membre) | [auto-py] |
| EL-06 | Chaque ligne « ⇔ » porte une propriété tirée de la liste fermée ci-dessus (y compris « car log(10) = 1 » et « car ln(e) = 1 ») (la division par un coefficient logarithmique porte « car D ≠ 0 », D ≠ 0 vérifié) ; aucune ligne sans justification, sauf l'arithmétique évidente (x + 1 = 3 ⇔ x = 2) | [auto-py] |
| EL-07 | Exact puis ≈ : chaque « ≈ » suit une valeur exacte sur la même ligne ; 3 décimales ; virgule décimale ; aucun point décimal (SOC-12) ; **notation suisse (Q5, Q12) : ’ dès 4 chiffres sur la partie entière seulement** (−99’999’995, 1’234,567, 0,0001), `\text{’}` en TeX ; saisie de ' et ’ lue 1000, « 1 000 » refusé avec un message (`moteur/nombres.py`) | [auto-py] |
| EL-08 | Second membre ≤ 0 (a^f = b, b ≤ 0, k·a^f = b avec b/k ≤ 0) : S = ∅ justifié par « une exponentielle est strictement positive », jamais par un logarithme d'un nombre négatif | [auto-py] |
| EL-09 | Équations logarithmiques (par l'exponentielle des deux membres, jamais la définition) : aucune carte d'ensemble de définition ; une vérification de chaque solution (argument > 0) ; base inconnue : condition annoncée, solution rejetée si x ≤ 0 ou x = 1 (log_x(256) = 4 : S = {4}) | [auto-py] |
| EL-10 | `log(x^2) = 2` donne S = {−10 ; 10} par la définition ; aucune sortie ne contient « 2 log|x| » ni « 2\log\left|x\right| » | [auto-py] |
| EL-11 | **Deux messages quand aucune méthode ne s'applique** (décision du 26.10.2026). (a) **Vrai hors-programme** (x·2^x = 8, 2^x + 3^x = 5, x^x = 4, 2^√x = 4, 2^x = x + 1, inconnue dans une base et dans un exposant à la fois) : le texte est exactement « Cette équation ne se résout pas avec les méthodes du cours. ». (b) **Forme du programme pas encore gérée** (2^(x³) = 8 : le logarithme donne une équation du 3ᵉ degré, résoluble, mais l'outil ne la traite pas encore ; log(x) = log(5), log(x) + log(x − 1) = 1, plusieurs logarithmes sommés, 2M ; −2^x = −3^(x+1) et 10^x·(x − 4) = 0 sont résolues depuis l'audit du 27.10.2026) : « Cet outil ne traite pas encore ce type d'équation. ». Le moteur choisit (`message_non_resolu`) : hors-programme = l'inconnue dans une base et un exposant, un exposant qui n'est pas un polynôme (2^√x), une exponentielle multipliée ou divisée par un facteur en x (sauf produit égal à 0), une somme d'exponentielles de bases différentes, une exponentielle et un terme en x sans exponentielle de part et d'autre du signe =. Jamais « non applicable », jamais une étape fausse ni une valeur numérique donnée comme solution ; détail technique dans `detail` seulement. Une inéquation garde son message de lecture (« Les inéquations ne sont pas traitées par cet outil : écrivez une équation avec =. ») | [auto-py] |
| EL-12 | Aucune sortie ne contient le vocabulaire interdit de SOC-15 (`test_vocabulaire.py` étendu) ; JSON strict | [auto-py] |
| EL-13 | `exercice(niveau, graine)` est déterministe, produit un gabarit du niveau, aucun exposant de degré supérieur à 2, et le moteur le résout (oracle EL-02) pour 500 graines | [auto-py] |
| EL-14 | Manifeste (`test_manifeste`, `test_resoudre_import`) et instantanés de l'outil ; **les instantanés de tous les autres moteurs sont inchangés** | [auto-py] |
| EL-15 | Page : rendu de la batterie, **dans chaque méthode du sélecteur**, égal à `tests/pages/references/exponentielles-logarithmes.json` ; clavier avec log, ln, log_, e, = ; exercice au hasard (pool C) et corrigé ; une étape par ligne et aucun défilement horizontal à 360 px pour toute la batterie ; propriété à droite sur grand écran, sous l'expression sur écran étroit | [auto-page] |
| EL-16 | Registre et accueil (cellule III/C) : description « Équations exponentielles et logarithmiques, calcul de logarithmes, étape par étape. » identique dans `commun/registre.json` et `index.html` (ACC-01) ; posés après relecture des exemples | [auto-py] + [manuel] |
| EL-17 | Les exemples de rédaction 1 à 13 ci-dessus, relus à l'écran sur téléphone et comparés au corrigé, sont validés | [manuel] |
| EL-18 | **Ligne finale** : toute équation résolue se termine par « S = {valeur exacte} », suivie de « , soit x ≈ … » (3 décimales, virgule, ’ dès 4 chiffres) quand une solution n'est pas un rationnel (avec plusieurs solutions : « soit x ≈ −0,903 ou x = 0 ») ; S = ∅ et S = ℝ ont aussi leur ligne. **Elle existe même quand x est déjà isolé** : x = ln(3) n'a aucune carte de méthode, mais la sortie élève contient la carte finale « S = {ln(3)}, soit x ≈ 1,099 ». La composition est testée dès l'étape 3 (`tex_solution`) ; la carte finale de la sortie de `resoudre_el` l'est à l'étape 7 | [auto-py] |
| EL-19 | **Sélecteur** : toute équation exponentielle a deux variantes calculées en une fois (`variantes`, défaut « logarithmes ») ; une équation logarithmique, un calcul, un message d'erreur n'en ont pas et leur sortie, hors changement de rédaction des équations logarithmiques, est inchangée ; sur la page, un clic change les cartes sans appel au moteur, le choix est gardé (`localStorage` dans un `try/catch`), les boutons sont accessibles au clavier (`aria-pressed`), côte à côte et sans débordement à 360 px, l'impression montre la méthode affichée | [auto-py] + [auto-page] |
| EL-20 | **Méthode B n'utilise jamais** « définition du logarithme », « log(10ᵏ) = k », « ln(e^A) = A » ni « ln(e^k) = k » ; une puissance de 10 (de e) dans un log (ln) passe par log(a^A) = A · log(a) puis « car log(10) = 1 » ; les deux méthodes donnent le **même S** (oracle mpmath, batterie et 500 graines par niveau) ; le message de la méthode A est exactement « b n'est pas une puissance de a : il faut les logarithmes. » | [auto-py] |
| EL-21 | **Exponentielle des deux membres** : une équation logarithmique s'écrit par `a^(log_a(A)) = A` (A > 0), une paire de lignes par logarithme imbriqué, Vérification et Condition inchangées ; **contrôle à la calculatrice** (R15) si et seulement si une solution rationnelle est écrite avec des logarithmes, décidé exactement | [auto-py] |
| EL-22 | **Paramètre et base calculée** : la casse est gardée, `C0`, `V0`, `C_0` sont un seul nom ; une autre lettre que celle de l'exposant, facteur de chaque membre, est simplifiée par la carte « Simplifier par Q » ; sinon « Cette équation contient deux inconnues : Q et x. » ; `1 + 3,75/100`, `1 − 20/100`, `1 + 0,035`, `1 + 3,75 %` deviennent un décimal par la carte « Calculer la base », dans les deux méthodes ; la solution, substituée dans l'énoncé avec Q = 1, 7 et 1234,5, donne un écart < 10⁻⁹ (oracle mpmath) | [auto-py] |
| EL-23 | **Interprétation** : ans, mois et jours recalculés indépendamment à pleine précision (mpmath, 50 chiffres) sur une grille de facteurs (2, 3, 1/2, 1/4) et de taux (0,5 % à 8 %, 5 % à 25 %) et sur des cas fabriqués ; report des 30 jours sur le mois et des 12 mois sur l'année ; 0 mois et 0 jour écrits ; solution négative, S = ∅ et x = 0 sans interprétation chiffrée ; restes jamais calculés à partir des valeurs arrondies ; 3 décimales ; vouvoiement | [auto-py] |
| EL-24 | **Case à cocher** : présente seulement quand `option` est dans la sortie, pré-cochée avec un paramètre ou l'inconnue n, décochable ; ajoute et retire la carte « Interprétation » sans appel au moteur ; état gardé au changement de méthode ; absente de la méthode A sans carte « Solution » et des autres outils ; sans débordement à 360 px ; à l'impression, la case est masquée et la carte présente si cochée | [auto-page] |
| EL-25 | **Pool** : les formes d'application sont dans le niveau « logarithme », avec des taux dans les bornes, le moteur les résout (oracle) et l'interprétation est exacte pour 500 graines | [auto-py] |

## Corrections après la chasse aux trous (27.10.2026)

Audit sur 8 260 saisies générées (formes du chapitre, variantes de saisie des exercices 2.13 à 2.27), oracle mpmath. Corrections décidées par l'enseignant le 27.10.2026,
un commit par groupe ; les entrées sont dans `BATTERIE_AUDIT` (`tests/python/cas_el.py`), les tests dans `test_audit_el.py`.

1. **Racine double et écritures** : Δ = 0 donne la ligne « Δ = 0 : une seule solution », puis `x = −b/(2a) = …` (S à un élément), dans les deux méthodes ; en méthode B la ligne du discriminant se termine par `= 0`.
   `a·x² = 0` donne `x² = 0 ⇔ x = 0` (méthode A) et `x²·log(a) = 0 ⇔ x² = 0 (car log(a) ≠ 0) ⇔ x = 0` (méthode B), jamais `±√0` ni `S = {0 ; 0/log(2)}`.
   `a + (−b)` s'écrit `a − b` (jamais « + − »). Aucune saisie ne lève d'exception (`log(x) + log(2) = 1` : « pas encore »). Le signe de Δ est décidé exactement quand Δ est un rationnel (même écrit avec des logarithmes), sinon à 60 chiffres ;
   un coefficient de x² ou de x écrit avec des logarithmes différents mais nul ((log 0,5 + log 2)·x²) reste « pas encore » en méthode B, comme au premier degré.
2. **Messages** : un logarithme avec un terme en x ou une exponentielle, de part et d'autre du signe = ou en facteur (`log(x) = x − 1`, `ln(x) = x`, `x · log(x) = 1`, `e^x = ln(x)`,
   `log(x) = 2^x`), est un vrai hors-programme (« Cette équation ne se résout pas avec les méthodes du cours. ») ; aucune forme que l'outil résout n'est classée hors programme.
3. **Isoler les exponentielles** (carte « Isoler les exponentielles », avant toute méthode, dans les deux méthodes) : `a^P − b^Q = 0 ⇔ a^P = b^Q` et `a^P + b^Q = 0 ⇔ a^P = −b^Q`
   (on passe un terme de l'autre côté), puis la carte « Aucune solution » (`a^P > 0`, `−b^Q < 0`) ; `−a^P = −b^Q ⇔ a^P = b^Q` (on multiplie les deux membres par −1) ;
   `u/v = c ⇔ u = c · v` (on multiplie les deux membres par le dénominateur : `3^(x+1)/2^x = 1 ⇔ 3^(x+1) = 2^x`). Quand la suite commence par isoler l'exponentielle (`8 = 2 · 2^x ⇔ 4 = 2^x`),
   la chaîne continue dans la même carte. Un facteur d'un produit nul s'isole de la même façon (`(2^x − 3^x)(5^x − 25) = 0`). Trois propriétés de plus dans la liste fermée :
   (on passe un terme de l'autre côté), (on multiplie les deux membres par −1), (on multiplie les deux membres par le dénominateur).
4. **Exponentielle au dénominateur** : méthode A, `aᵐ / aⁿ = aᵐ⁻ⁿ` quand les bases sont des puissances d'une même base (`8/2^x = 2^3/2^x = 2^(−x+3)`, propriété (aᵐ / aⁿ = aᵐ⁻ⁿ)),
   sinon on multiplie les deux membres par le dénominateur (`3/e^x = 6 ⇔ 3 = 6e^x ⇔ e^x = 1/2`), puis la définition ou le message ; méthode B, `log(u/v) = log u − log v`
   (`log(8/2^x) = log(2) ⇔ log(8) − log(2^x) = log(2)`, propriétés (log(a/b) = log a − log b), (ln(a/b) = ln a − ln b), (propriétés des logarithmes) avec un produit en plus).
   Un coefficient de x purement numérique et négatif fait passer les termes en x de l'autre côté (`ln(3) − x = ln(6)` donne `x = ln(3) − ln(6)`, jamais `x(−1)`).
   Quand la méthode B diviserait par un coefficient nul (`4^x = 2^(2x)`, `2^(2x)/4^(x−1) = 8`), la méthode A est donnée seule, sans sélecteur (avant : « pas encore »).
5. **Exposant du 2e degré, second membre quelconque** (méthode B, et méthode A par la définition pour la base 10 ou e) : `a^(P(x)) = c ⇔ P(x) · log(a) = log(c) ⇔ P(x) = log(c)/log(a)` (car log(a) ≠ 0).
   Forme `x² = k` (pas de terme en x) : `x = −√k ou x = √k` (`2^(x²) = 5 ⇔ x² = log(5)/log(2)`, `2^(x²−1) = 5 ⇔ x² = 1 + log(5)/log(2)`, `e^(x²) = 2 ⇔ x² = ln(2)`) ;
   quand √k n'est pas un nombre exact, `x₁ = −√k` et `x₂ = √k` portent un nom et la ligne finale est `S = {x₁ ; x₂}, soit x ≈ …` (elle tient à 360 px, test de page) ; `x² = 4 ⇔ x = −2 ou x = 2` reste en ligne ;
   k < 0 : lignes `x² ≥ 0` (un carré est positif ou nul) et `k < 0` (aucune solution) ; k = 0 : `x = 0`. Forme générale : `P(x) − c = 0`, puis
   `Δ = b² − 4 · a · (q − c) = …` (formule du discriminant), `x₁`, `x₂` nommés, Δ < 0 : la remarque habituelle (`2^(x²+x) = 5`). Un second membre rationnel garde la résolution
   de la méthode « même base » (`10^(x²+x) = 100 ⇔ x² + x = 2 ⇔ (x + 2)(x − 1) = 0`). Plusieurs facteurs (`2^(x²) = 3^x`, `2^(x²) · 3^x = 6`) : le trinôme à coefficients
   logarithmiques (section « Sélecteur »), sans la condition « même base » d'avant. La méthode A garde sa rédaction validée (`x² + 1 = 0`, Δ = −4) ; nouvelle propriété (un carré est positif ou nul).
6. **Base inconnue, exposant négatif ou nul, argument 1** (`log_x(n) = k`, k entier de −12 à 12) : k < 0, `8 = x⁻¹ ⇔ 8 = 1/x` (a⁻ᵐ = 1/aᵐ) `⇔ x = 1/8` ; `4 = x⁻² ⇔ 4 = 1/x² ⇔ x² = 1/4 ⇔ x = 1/2 ou x = −1/2`,
   seule la solution positive convient ; k = 0, `5 = x⁰ ⇔ 5 = 1` (a⁰ = 1) : aucune solution, et `log_x(1) = 0` est vraie pour toute base, `S = ]0 ; 1[ ∪ ]1 ; +∞[` ;
   n = 1 et k ≠ 0 : `1 = x² ⇔ x = 1 ou x = −1`, puis « x = 1 et x = −1 ne conviennent pas » (une base de logarithme est strictement positive et différente de 1), S = ∅.
   La carte « Condition » vient toujours d'abord. Propriétés (a⁰ = 1) et (a⁻ᵐ = 1/aᵐ) ajoutées à la liste fermée.
7. **Produit nul polynôme × exponentielle** : `x · 2^x = 0 ⇔ x = 0 ou 2^x = 0` (un produit est nul si l'un des facteurs est nul), puis une carte par facteur : le facteur polynôme
   (1er ou 2e degré) se résout comme dans la méthode « même base » (`x − 4 = 0 ⇔ x = 4`, `x² − 1 = 0 ⇔ (x + 1)(x − 1) = 0`, Δ < 0 avec sa remarque), le facteur exponentiel
   par la carte « Aucune solution » (`2^x > 0`, `2^x = 0` : aucune solution). Un facteur constant non nul est omis (`3x · 2^x = 0`). Même rédaction dans les deux méthodes.
8. **log(x²) = c, ln(x²) = c, log_a(x²) = c** (second membre quelconque) : l'exponentielle des deux membres, `x² = 10^c` (avec l'écriture exacte quand le cours la donne : `10^(−1) = 1/10`,
   `10^1,5 = 10√10`), puis `x = −√(10^c) ou x = √(10^c)`, écrits `x₁ = −√(1/10)`, `x₂ = √(1/10)` comme au point 5 (`log(x²) = −1`, `ln(x²) = 1 ⇔ x² = e`), puis la Vérification ; jamais `2 log(x)`.
   Un second membre entier garde la factorisation (`x² − 100 = 0 ⇔ (x + 10)(x − 10) = 0`). Les trinômes généraux à coefficients non entiers (`log(x² − 1) = 1/2`) restent « pas encore ».
9. **Saisie de ² et ³** (clavier d'un téléphone) : lus `^2` et `^3` (`2^(x²)·4^x = 8` est `2^(x^2)·4^x = 8`) ; `2^x²` demande toujours des parenthèses.
10. **2e degré en aˣ : hors programme pour les 3C** (décision du 27.10.2026) : `4^x − 2^x − 6 = 0`, `e^(2x) − 3e^x + 2 = 0`, `e^x + e^(−x) = 3`, `2^x + 1 = 3^x` donnent « Cette équation ne se résout pas
   avec les méthodes du cours. », quelle que soit la base (avant : « hors programme » pour 4 et 2, « pas encore » pour e). Deux exponentielles seules (`a^P ± b^Q = 0`) se résolvent (point 3).
   La mise en facteur d'une somme de termes de même base dont les exposants diffèrent d'un entier est, elle, au programme (point 14).
11. **Méthode A, produit ou quotient de puissances de 10 ou de e** : `e^(2x)/e^x = 5 ⇔ e^x = 5` (aᵐ / aⁿ = aᵐ⁻ⁿ) `⇔ x = ln(5)` (définition du logarithme) ; `e^x · e^(x+1) = 5 ⇔ e^(2x+1) = 5` (aᵐ · aⁿ = aᵐ⁺ⁿ).
   Plus de message « il faut les logarithmes » quand la définition peut conclure ; les autres bases (`2^(2x)/2^x = 5`) gardent le message.
12. **Base inconnue, argument négatif ou nul** (`log_x(−8) = 3`, `log_x(0) = 2`) : carte « Condition », `log_x(−8) = 3 ⇔ x³ = −8` (définition du logarithme), puis carte « Aucune solution » :
   `x³ > 0` (une base admissible est strictement positive, donc xᵏ > 0) et `−8 < 0` (aucune solution) ; S = ∅. Vaut pour tout exposant rationnel.
13. **Équation sans exponentielle ni logarithme** (`x² = 4`, `2x + 1 = 9`, `√x = 3`) : le message « Cet outil traite les équations exponentielles et logarithmiques. » (`MESSAGE_SANS_EXP_LOG`) remplace
   « pas encore » ; dès qu'un logarithme ou une puissance d'exposant variable apparaît, les messages d'avant (hors programme / pas encore) restent.
14. **Mise en évidence** (D1, au programme 3C) : somme de termes de même base dont les exposants diffèrent d'un entier (`2^x + 2^x`, `2^x + 2^(x+1)`, `2^(x+2) − 2^x`, `5^x + 5^(x+1) + 5^(x+2)`),
   avec coefficients (`3 · 2^x + 2^(x+2)`) et constante éventuels, égale à une constante. **Carte « Mise en évidence » commune aux deux méthodes**, au début des deux variantes : une ligne par exposant décalé
   (`2^(x+1) = 2^x · 2`, aᵐ⁺ⁿ = aᵐ · aⁿ ; `2^(x+2) = 2^x · 2^2`), puis une chaîne : `2^x + 2^(x+1) = 12 ⇔ 2^x · (1 + 2) = 12` (mise en évidence de la plus petite puissance)
   `⇔ 3 · 2^x = 12 ⇔ 2^x = 4` (la dernière étape est celle d'« Isoler l'exponentielle », fusionnée dans la chaîne). Une constante s'isole d'abord (`2^x + 2^(x+1) + 3 = 15 ⇔ 2^x + 2^(x+1) = 12`).
   Si le coefficient obtenu est une puissance de la base (≥ 1), on le fond : `2^x + 2^x = 8 ⇔ 2^x · (1 + 1) = 8 ⇔ 2^x · 2 = 8 ⇔ 2^(x+1) = 8` (aᵐ · aⁿ = aᵐ⁺ⁿ ; `2^x · 4 ⇔ 2^x · 2^2 ⇔ 2^(x+2)`) ;
   coefficient 1 : `2^(x+1) − 2^x = 4 ⇔ 2^x · (2 − 1) = 4 ⇔ 2^x = 4` ; coefficient nul : `2^x − 2^x = 3 ⇔ 2^x · 0 = 3 ⇔ 0 = 3`, S = ∅ (ou `0 = 0`, S = ℝ) ; coefficient négatif :
   `2^x − 2^(x+1) = 4 ⇔ 2^x · (1 − 2) = 4 ⇔ −2^x = 4 ⇔ 2^x = −4`, puis la carte « Aucune solution ». Base e avec décalage : le coefficient est irrationnel (`e^x + e^(x+1) = 5 ⇔ e^x · (1 + e) = 5 ⇔ e^x = 5/(1 + e)`, puis A : `⇔ x = ln(5/(1 + e))` par la définition du logarithme, B : `ln(e^x) = ln(5/(1 + e)) ⇔ x · ln(e) = … ⇔ x = ln(5/(1 + e))`, soit x ≈ 0,296) ;
   les termes semblables se réduisent (`1 + e + e` ⇒ `1 + 2e`) ; coefficient négatif ou quotient négatif ou nul : carte « Aucune solution » (`e^x = 5/(1 − e)` : `5/(1 − e) < 0`) ; exposant du 1er ou du 2e degré. Tout coefficient positif suffit, quel qu'il soit (rationnel ou irrationnel). Exposants qui ne diffèrent pas d'un entier constant (`e^x + e^(−x) = 3`), bases différentes et 2e degré en aˣ : hors programme (point 10).
15. **Ordre des solutions : toujours croissant**, dans les deux méthodes : S, les lignes `x = a ou x = b` (`log_x(256) = 4 ⇔ x = −4 ou x = 4`) et x₁ < x₂ (avec un coefficient de x² négatif, x₁ s'écrit avec « + √Δ »).
   Test : pour toute équation du corpus, A et B donnent S dans le même ordre.
16. **Regrouper les termes de même base** (D4, au programme 3C) : équation dont chaque terme est `k · a^P`, au plus deux bases distinctes (valeurs égales ; une base n'est pas réécrite comme puissance d'une autre), des deux côtés,
   un membre pouvant être 0, exposants de même partie variable et décalés d'un entier dans un même groupe de base. Carte « Regrouper les termes de même base » (les termes de la base du 1ᵉʳ terme à gauche, ceux de l'autre base à droite,
   chaque terme déplacé change de signe) : `2^x − 3^(x+1) = 3^x ⇔ 2^x = 3^x + 3^(x+1)` (on regroupe les termes de même base) ; puis la carte « Mise en évidence » de chaque côté (`3^(x+1) = 3^x · 3`, `2^x = 3^x · (1 + 3) ⇔ 2^x = 4 · 3^x`) ;
   puis `k · a^P = m · b^Q` comme d'habitude (méthode B ; méthode A : le message « il faut les logarithmes »), ou la carte « Aucune solution » si un membre est ≤ 0 (`2^x − 3^x = 2^x − 3^(x+1)`), ou S = ℝ (`2^x − 2^x = 3^x − 3^x`).
   Une seule base des deux côtés (`2^x + 2^(x+1) = 2^(x+2)`) : tout à gauche, égal à 0, puis la mise en évidence du point 14. Pas de carte de regroupement quand les termes sont déjà regroupés.
   Deux bases **et** une constante additive (`2^x + 3^x = 5`, `2^x − 3^(x+1) = 3^x + 1`) : hors programme. La base e avec des exposants décalés dans un même groupe (`e^x + e^(x+1) = 2^x`) : hors programme.

## Filière M (2Ms, 2Mr) — décision du 28.10.2026 (T35)

Même moteur, paramètre **`filiere`** (`"C"` par défaut, `"M"`) de `resoudre(entree, filiere)` et `exercice(niveau, graine, filiere)` ; module `exponentielles-logarithmes/exp_log_m.py` (importe les briques de `exp_log.py`, qui n'est modifié que par des ajouts neutres).
**Les sorties C sont strictement identiques** (instantané `exponentielles-logarithmes.json` inchangé, `resoudre(e) == resoudre(e, "C")` sur tout le corpus). Références : polycopié Javet 2M (chap. 3 : ex. 3.3, 3.5, 3.11, 3.12, 3.15 ; solutions p. VIII-IX), brochure Amaudruz 2M (ex. 6.1, 7.4, 7.7 à 7.9).

**Choix de la filière sur la page** : `?filiere=M` (cartes 2Ms et 2Mr de l'accueil, champ `parametres` du registre) d'abord, sinon la filière mémorisée par l'accueil (`samimir-track` : Ms et Mr → M, C ou « tous » → C), sinon C ; un **interrupteur visible « 3C / 2M »** (style du sélecteur de méthode, `aria-pressed`, au clavier) change la filière, met `?filiere=` à jour (`history.replaceState`) et recalcule la saisie affichée ; pas de `localStorage` propre ; à l'impression, la ligne « Filière : 2M ».
Le worker accepte un tableau d'arguments (`fn_json(*arg)`) : `[entree, filiere]`, `[niveau, filiere]`.

**1. Équation logarithmique : l'ensemble de définition d'abord.** Une seule carte « Étape 1 · Ensemble de définition » : une sous-section par condition (cartes de l'outil Ensemble de définition, `blocs_condition` de `resoudre_ed.py` : « Condition k (logarithme) », lignes, tableau de signes), puis `ED = E₁ ∩ E₂ = …` (`blocs_ensemble`). L'ED se calcule sur **l'équation de départ** : l'arbre EL est traduit en saisie ED (`log`, `log_a` → `ln(…)` : la condition u > 0 ne dépend pas de la base ; logarithme d'une constante omis).
Base inconnue : la condition « x > 0 et x ≠ 1 » (une base de logarithme est strictement positive et différente de 1) entre dans la même carte. Un logarithme dans un logarithme n'est traité qu'en base e (`ln(ln(x)) = 1` : l'outil ED écrit `ln(x) > 0 ⇔ x > 1`, exp est croissante) ; en base 10 ou a (`log(log(x)) = 1`), la filière M répond « Cet outil ne traite pas encore ce type d'équation. » plutôt que le corrigé de la 3C sans ensemble de définition. ED vide : « L'ensemble de définition est vide : l'équation n'a aucune solution. », S = ∅, rien d'autre.

**2. On regroupe toujours, on ne développe jamais** (méthode du cours). Membres = Σ cᵢ·log_b(uᵢ) + une constante, **même base b** (bases mélangées : « pas encore ») :
`k·log(u) = log(u^k)`, `log(u) + log(v) = log(uv)`, `log(u) − log(v) = log(u/v)`, `c = log(10^c)` (ln : `c = ln(e^c)`, log_a : `c = log_a(a^c)`), chacune notée **« sur l'ED »** dans sa propriété ; puis
`log(A) = log(B) ⇔ A = B` (sur l'ED), ou, quand un membre n'a aucun logarithme, l'exponentielle des deux membres de la 3C (`log(A) = c ⇔ A = 10^c`). Une constante et des logarithmes des deux côtés : `log(5+x) = log(4−x) + 1 ⇔ log(5+x) = log(4−x) + log(10) ⇔ log(5+x) = log(10(4−x)) ⇔ 5 + x = 10(4 − x)`.
**`log(x²)` n'est jamais réécrit** (ni 2 log x, ni 2 log|x| : notion non vue en cours) : `log(x²) + log(3) = 10 ⇔ log(3x²) = 10 ⇔ 3x² = 10¹⁰ ⇔ x = −√(10¹⁰/3) ou x = √(10¹⁰/3)`. Le regroupement élargit l'ensemble de définition, d'où la carte suivante.
Résolution de A = B : multiplier par un dénominateur (« ≠ 0 sur l'ED »), développer, réduire ; degré ≤ 2 (Δ, x₁ et x₂ nommés comme en 3C), `xⁿ = c` (racine, ±√), identité → S = ED, contradiction → ∅ ; le reste « pas encore ».

**3. Carte « Vérification »** (après la résolution) : chaque solution est confrontée à l'ED, **une ligne par solution** : `x₂ = (1 + √41)/2 ≈ 3,702 ∈ ED ✓` ou `x₁ = (1 − √41)/2 ≈ −2,702 ∉ ED : rejetée` suivie de la raison (la première condition violée : `x − 1 < 0 : log(x − 1) n'est pas défini`). L'appartenance est décidée **exactement** (rationnel exact ; sinon signe à 60 chiffres avec marge, puis SymPy près de 0), jamais par un arrondi. La carte « Solution » ne garde que les solutions retenues ; toutes rejetées → S = ∅ avec la phrase « Aucune solution de l'équation n'est dans l'ensemble de définition. ».
Remplace, en M, la carte « Condition » de la base inconnue et l'ancienne « Vérification » de la 3C. Base inconnue : les deux candidats de `x⁴ = 256` (x = −4 ou x = 4) sont gardés par la résolution et la vérification rejette −4 (« x est la base d'un logarithme : x doit être strictement positif et différent de 1 »), au lieu de la ligne « seule la solution positive convient » de la 3C.
Les lignes sont `x = 35/11 (dans l'ensemble de définition ✓)` ou `x = −4 ∉ ED (rejetée : …)` : la raison est du texte simple (une formule de KaTeX ne passe pas à la ligne à 360 px). Toute équation de la filière M qui contient un logarithme de l'inconnue et que M ne traite pas donne un message (« pas encore » ou « hors programme »), jamais le corrigé de la 3C.

**4. Changement de variable (2ᵉ degré en aˣ), M seulement** : `a^(2f) + p·a^f + q = 0` et ses écritures (4ˣ = (2ˣ)², 9ˣ = (3ˣ)², e^(2x) = (eˣ)², a^(x+1) = a·aˣ, a^(−x) = 1/aˣ en multipliant par aˣ, constantes des deux côtés, t = e^(2x) quand e^(4x) apparaît). Carte « Changement de variable » **commune aux deux méthodes** : `t = aˣ`, `t > 0` (une exponentielle est strictement positive), le trinôme en t (Δ, t₁, t₂), les racines t ≤ 0 rejetées avec leur raison ; puis une carte par retour `aˣ = tₖ` dans la méthode choisie (A ou B), enfin « Solution ». En C, ces équations gardent le message « Cette équation ne se résout pas avec les méthodes du cours. ».
Reste « pas encore » en M (au programme mais hors de l'outil) : exposant √x ou 1/x, `x·ln(x) = 0`, `(ln x)²`, inéquations, systèmes (Javet 3.13), base polynomiale (`log_(x+1)`), `e^(−ln x)`.

**5. Pool M** (`exercice(niveau, graine, "M")`, racines construites à l'envers, entières ou rationnelles simples, Δ carré) : niveaux **exponentielle** 25 % (tirages du pool C), **définition** 15 % (`log_a(u) = c` avec ED), **sommes** 20 % (`log(u) ± log(v) = c`, souvent une solution rejetée), **log = log** 15 % (`k·log(u) = log(v)`, `log(u) = log(v) + c`, logarithmes numériques façon Javet 3.11), **changement de variable** 15 % (une racine en t négative ou deux positives), **difficile** 10 % (ED vide, toutes rejetées, ln et log_a, trois logarithmes façon 3.12 g). Énoncé « Résoudre : … ».

**Registre** : `filieres {"2": ["Ms", "Mr"], "3": ["C"]}`, `parametres {"Ms": "?filiere=M", "Mr": "?filiere=M"}`, `descriptions` : « Équations exponentielles et logarithmiques avec ensemble de définition, étape par étape. » pour Ms et Mr (ACC-01).

**Exemples de rédaction M** (valeurs vérifiées avec mpmath le 28.10.2026)

**M1. `log(x) + log(x − 1) = 1`** : ED x > 1 (x > 0 et x − 1 > 0). `log(x) + log(x − 1) = 1 ⇔ log(x(x − 1)) = 1` (log a + log b = log(ab), sur l'ED) `⇔ 10^(log(x(x−1))) = 10¹` (exponentielle des deux membres) `⇔ x(x − 1) = 10` (10^(log(A)) = A, A > 0) `⇔ x² − x − 10 = 0` ; Δ = 41, x₁ = (1 − √41)/2 ≈ −2,702 ∉ ED : rejetée ; x₂ = (1 + √41)/2 ≈ 3,702 ∈ ED ✓. S = {(1 + √41)/2}.
**M2. `log(x + 1) + log(2x) = log(3)`** : ED x > 0. `⇔ log((x + 1)·2x) = log(3) ⇔ (x + 1)·2x = 3` (log A = log B ⇔ A = B, sur l'ED) `⇔ 2x² + 2x − 3 = 0` ; x₁ ≈ −1,823 ∉ ED : rejetée ; x₂ ≈ 0,823 ∈ ED ✓.
**M3. `log(5 + x) = log(4 − x) + 1`** : ED ]−5 ; 4[. `1 = log(10)`, `log(4 − x) + log(10) = log(10(4 − x))` (log a + log b = log(ab)), `5 + x = 10(4 − x) ⇔ x = 35/11 ≈ 3,182` ∈ ED ✓.
**M4. `log(x²) + log(3) = 10`** : ED x ≠ 0. `log(3x²) = 10 ⇔ 3x² = 10¹⁰ ⇔ x = −√(10¹⁰/3) ou x = √(10¹⁰/3)`, les deux ∈ ED ✓.
**M5. `3 log(x) = 2 log(8)`** (Javet 3.11 a) : ED x > 0. `log(x³) = log(8²) = log(64) ⇔ x³ = 64 ⇔ x = 4` ✓.
**M6. `log₂(3x − 4) + log₂(10x − 4) = 2 log₂(5x − 2)`** : ED x > 4/3. `5x² − 32x + 12 = 0` ; x = 2/5 ∉ ED : rejetée ; x = 6 ✓.
**M7. `log(x − 3) + log(1 − x) = 0`** : ED = ∅, S = ∅.
**M8. `3ˣ + 9ˣ = 90`** : `t = 3ˣ > 0`, `t² + t − 90 = 0`, t = −10 rejetée (une exponentielle est strictement positive), t = 9 ⇔ 3ˣ = 9 ⇔ x = 2. **`e^(4x) − 29e^(2x) = −100`** : `t = e^(2x)`, `t² − 29t + 100 = 0`, t = 4 ou t = 25, x = ln(4)/2 ≈ 0,693 ou x = ln(25)/2 ≈ 1,609.

## Critères d'acceptation de la filière M

| Id | Critère | Vérif. |
|---|---|---|
| EL-26 | **C inchangé** : `resoudre(e) == resoudre(e, "C")` pour tout le corpus, instantanés C (`exponentielles-logarithmes.json`) et ED inchangés ; filière inconnue → message en français | [auto-py] |
| EL-27 | **ED d'abord** : toute équation logarithmique en M commence par la carte « Ensemble de définition » (cartes de l'outil ED), avant toute transformation ; ED = celui de l'outil ED pour l'équation de départ (comparaison avec `analyser_complet` sur le corpus) ; ED vide → S = ∅ immédiat | [auto-py] |
| EL-28 | **Vérification** : une ligne par solution, appartenance décidée exactement ; toute solution rejetée est hors de l'ED (oracle mpmath), toute retenue est dans l'ED et vérifie l'équation de départ (écart < 10⁻⁹) ; la raison de chaque rejet est une condition de l'ED réellement violée | [auto-py] |
| EL-29 | **Regroupement** : jamais de log(u) développé (pas de « 2 log », pas de « log|x| » dans une sortie M) ; chaque ligne porte une propriété de la liste fermée avec « sur l'ED » ; log(x²) reste log(x²) ; log(A) = log(B) ⇔ A = B seulement après regroupement en un seul logarithme par membre | [auto-py] |
| EL-30 | **Aucune racine perdue** : pour tout le corpus M, les racines de l'équation de départ trouvées numériquement et indépendamment (balayage de chaque intervalle de l'ED, mpmath) sont exactement S | [auto-py] |
| EL-31 | **Changement de variable** : t = aˣ, t > 0, t ≤ 0 rejetée avec sa raison, retour dans la méthode choisie ; mêmes S dans les deux méthodes (oracle mpmath) ; en C, les mêmes équations donnent le message hors programme | [auto-py] |
| EL-32 | **Pool M** : déterministe, niveaux et poids du plan, le moteur résout (oracle) pour 500 graines par niveau, aucun discriminant non carré, au moins une solution rejetée dans le niveau « sommes » pour une part des tirages | [auto-py] |
| EL-33 | **Page** : `?filiere=M`, filière de l'accueil, interrupteur au clavier (`aria-pressed`), recalcul, exercice M, rendu de `BATTERIE_M` égal aux références, aucun débordement à 360 px, impression avec « Filière : 2M », les autres outils sans interrupteur | [auto-page] |
| EL-34 | **Registre et accueil** : cartes 2Ms et 2Mr avec le lien `?filiere=M` et la description M identique dans `commun/registre.json` et `index.html` (ACC-01) | [auto-py] |
