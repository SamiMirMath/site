# Outil « Exponentielles et logarithmes » (3C)

URL : `/exponentielles-logarithmes/` · moteur : `exponentielles-logarithmes/exp_log.py` (SymPy obligatoire pour décider,
jamais pour écrire) · adaptateur : `resoudre_el.py`. Spécification du 26.10.2026, validée par étapes par l'enseignant (questions Q10 à Q12 tranchées le 26.10.2026).

Références : polycopié 3C (chapitre 2), *Mathématiques 3 ECG*, « Exponentielles et logarithmes », pages imprimées 17 à 40
(pages 18 à 41 du PDF, version du 14.04.2026) ; corrigé détaillé de l'enseignant (`3C_Exponentielles_Logarithmes_Corrige.pdf`,
exercices 2.1 à 2.27), qui fait foi pour la rédaction.

## Périmètre

**Cette version : 3C seulement**, pour le test sur le chapitre 2. Le moteur est écrit pour servir aussi les 2M (voir la fin), mais
rien de 2M n'est codé ici : ni ensemble de définition, ni équations à plusieurs logarithmes, ni inéquations, ni pool M.

| Id | Type | Exercices du polycopié | Priorité |
|---|---|---|---|
| E1 | Même base : a^A = a^B ⇔ A = B | 2.13 a-o, exemples p. 22-23 | 1 |
| E2 | Isoler l'exponentielle, puis logarithme ; ∅ si le second membre est ≤ 0 ; produit nul | 2.18, 2.21, 2.23, p. 26 n° 1-2, p. 29 | 2 |
| E3 | Bases différentes des deux côtés | 2.24, p. 26 n° 3 | 3 |
| E4 | Équation logarithmique en une étape (définition du logarithme), logarithmes imbriqués, base inconnue | 2.15 e-g j-l, 2.18 c d f, 2.21 d, 2.22 | 4 |
| C1 | Calculer log_a(y) (saisie sans « = ») | 2.15 a-d h i, 2.20 | 5 |
| C2, C3, E5 | Propriétés avec log 2 ≈ 0,301 (2.25) ; encadrement (2.16) ; inconnue dans la base a¹² = 1,5 (2.5) | | si le temps le permet |

**Entrées hors programme** (x·2^x = 8…) : l'outil affiche « Cette équation ne se résout pas avec les méthodes du cours. » (EL-11). À poser à l'étape 7, quand
l'adaptateur `resoudre_el.py` décide ce qui s'affiche : tant que les méthodes E2 à E4 manquent, le moteur renvoie seulement « méthode non applicable » en interne.

Hors de cette version : interprétation des applications en années entières (l'outil résout, n ≈ 14,6, et s'arrête), mode « problème
en mots », tâtonnement (2.14), graphiques (2.1, 2.9, 2.12), écrire un nombre comme puissance de 10 ou de e (2.17, 2.19).

## Notations

- **log = logarithme en base 10** (10ˣ = y ⇔ x = log(y), p. 24) ; **ln = logarithme en base e** (p. 25) ; **log_a** pour la base a (p. 25).
  Le moteur de l'Ensemble de définition lit `log` comme `ln` : le nouvel outil a sa propre lecture et n'y touche pas.
- Saisie : `log(x)`, `ln(x)`, `log2(x)` ou `log_2(x)`, `log10(x)`, `exp(x)`, `e^x`, `sqrt(x)`, `^`, `*`, `/`, multiplication implicite
  (`2x`, `3ln(x)`), virgule ou point décimal, un seul « = », une seule lettre pour l'inconnue.
- **`e` est toujours le nombre e** et ne peut pas être l'inconnue : message « La lettre e désigne le nombre e ≈ 2,718 : choisis une
  autre lettre pour l'inconnue. » Les noms de fonction (`sqrt`, `exp`, `ln`, `log_a`, `log2`, `log`) sont reconnus **avant** les lettres
  isolées, du plus long au plus court.
- **Notation suisse** (Q5, Q12) : apostrophe typographique ’ dès 4 chiffres, **partie entière seulement** (−99’999’995, 1’234,567, 0,0001), `\text{’}` en TeX ; saisie de ' et ’ lue 1000 ;
  « 1 000 » refusé (« Pas d'espace dans un nombre : écrivez 1000 ou 1’000. »). Fonctions dans `moteur/nombres.py`, réutilisables par T23.
- Affichage : `\log`, `\ln`, `\log_{2}` écrits **par notre arbre**, jamais par SymPy (SymPy écrit `log` pour `ln`). Virgule décimale.
  Valeurs approchées avec « ≈ », jamais avec « ≅ » ni « ~ ». L'expression « valeur approchée » n'est pas écrite (SOC-15).

## Rédaction

Une carte par application de méthode, comme la Factorisation (T21) : « Étape k », méthode en badge, chaîne de « ⇔ » une étape par ligne,
**propriété nommée entre parenthèses (1 à 5 mots)** à chaque ligne, carte finale « Solution ».

**Une équation à même base tient en deux cartes au plus** (validé le 26.10.2026) : « Isoler l'exponentielle » (seulement si l'équation
s'écrit k·a^f + c = d…), puis « Même base », qui contient la réécriture des membres (lignes de « = ») **et** la chaîne unique de ⇔
`a^A = a^B ⇔ A = B ⇔ … ⇔ solutions`, comme l'encadré « se ramener à la même base » du corrigé. Quand les deux membres sont déjà écrits
avec la même base (7^(2x+1) = 7^9), il n'y a que la carte « Même base », réduite à la chaîne de ⇔. Pour un trinôme de discriminant
non carré, les lignes « Δ = … » et « x = … ou x = … » suivent la chaîne dans la même carte.

Propriétés nommées (liste fermée, testée) : (on isole le terme exponentiel), (même base : a^A = a^B ⇔ A = B), ((aᵐ)ⁿ = aᵐⁿ),
(aᵐ · aⁿ = aᵐ⁺ⁿ), (1 = a⁰), (log des deux membres), (log(a^A) = A · log(a)), (ln(a^A) = A · ln(a)), (log a − log b = log(a/b)),
(définition du logarithme), (log(10ᵏ) = k), (ln(1) = 0), (une exponentielle est strictement positive), (aucune solution),
(un produit est nul si l'un des facteurs est nul), (formule du discriminant), (changement de base).

**Cartes de la méthode « logarithme »** (étape 3) : « Isoler l'exponentielle » (si besoin), puis « Définition du logarithme » (base 10 ou base e : `10^f = b ⇔ f = log(b)`,
`e^f = b ⇔ f = ln(b)`) ou « Logarithme des deux membres » (toute autre base) ou « Aucune solution » (second membre ≤ 0). Un produit nul donne « Produit nul » (la ligne
`P₁·P₂ = 0 ⇔ P₁ = 0 ou P₂ = 0`), puis une carte « Facteur 1 », « Facteur 2 »… qui reprend les lignes de la résolution de chaque facteur. Une équation du premier
degré dont le second membre contient un logarithme (x = ln 3, 2x = ln(0,1)) a la carte « Équation du premier degré » (aucune carte quand x est déjà isolé).

**Valeur exacte d'abord, puis ≈** à 3 décimales (corrigé p. 1), jamais un « ≈ » sans la valeur exacte juste avant sur la même ligne.
log(10^k) = k et ln(e^k) = k sont évalués ; log a − log b est regroupé en log(a/b) seulement dans les bases différentes (E3) ; sinon la valeur exacte
est gardée **telle que la donne la chaîne** : `ln(25/37)/(−0,02)` n'est pas simplifié en `−50 · ln(25/37)` (Q11).

**Pas d'ensemble de définition en 3C** : le polycopié n'en parle nulle part. Seules deux justifications, celles de ton corrigé :
- logarithme dont l'argument contient l'inconnue : **Vérification** après la résolution, « 5 − x = 10⁸ > 0 : le logarithme est bien défini. ✓ » ;
  une solution qui donnerait un argument ≤ 0 est rejetée avec sa raison ;
- base inconnue : condition annoncée avant, « x > 0 et x ≠ 1 (une base de logarithme est strictement positive et différente de 1) », puis
  « seule la solution positive convient ».

**log(x²)** : s'il apparaît (log(x²) = 2), l'équation se résout par la **définition** (x² = 10², x = 10 ou x = −10, vérification x² > 0) ;
on n'écrit jamais 2 log|x|, et 2 log(x) ne s'écrit que quand x > 0 est justifié (2M, plus tard).

**Sens d'une inégalité** : aucune inégalité à résoudre en 3C (pas d'inéquation). Les seules inégalités sont les vérifications d'argument
(« > 0 ») et l'encadrement C3, justifié par « log est croissante » (corrigé 2.16).

## Exemples de rédaction (valeurs vérifiées avec mpmath le 26.10.2026)

**1. Même base — 3^(x+1) − 27 = 0** (p. 22)
Étape 1 · Isoler l'exponentielle : `3^(x+1) − 27 = 0 ⇔ 3^(x+1) = 27` (on isole le terme exponentiel).
Étape 2 · Même base : `27 = 3³`, donc `3^(x+1) = 3³ ⇔ x + 1 = 3` (même base : a^A = a^B ⇔ A = B) `⇔ x = 2`.
Solution : `S = {2}`.

**2. Même base, degré 2 — 2^(x²) · 4^x = 8** (2.13 o)
Étape 1 · Même base : `4^x = (2²)^x = 2^(2x)` ((aᵐ)ⁿ = aᵐⁿ) ; `2^(x²) · 2^(2x) = 2^(x²+2x)` (aᵐ · aⁿ = aᵐ⁺ⁿ) ; `8 = 2³` ;
puis, dans la même carte, une seule chaîne de ⇔ :
`2^(x²+2x) = 2³ ⇔ x² + 2x = 3` (même base) `⇔ x² + 2x − 3 = 0 ⇔ (x + 3)(x − 1) = 0 ⇔ x = −3 ou x = 1`.
Solution : `S = {−3 ; 1}`.

**3. Logarithme — 2^x = 100** (2.23 a)
`2^x = 100 ⇔ log(2^x) = log(100)` (log des deux membres) `⇔ x · log(2) = log(100)` (log(a^A) = A · log(a)) `⇔ x · log(2) = 2` (log(10ᵏ) = k)
`⇔ x = 2 / log(2) ≈ 6,644`. Solution : `S = {2 / log(2)}`, soit `x ≈ 6,644`.

**4. Aucune solution — 5^(8x) = −25** (2.23 h)
`5^(8x) > 0` pour tout x (une exponentielle est strictement positive), alors que `−25 < 0` : aucune solution. `S = ∅`.

**5. Bases différentes — 2^(x−1) = 3^x** (2.24 a)
`log(2^(x−1)) = log(3^x)` (log des deux membres) `⇔ (x − 1) · log(2) = x · log(3)` (log(a^A) = A · log(a))
`⇔ x · log(2) − log(2) = x · log(3) ⇔ x · log(2) − x · log(3) = log(2) ⇔ x · (log(2) − log(3)) = log(2)`
`⇔ x = log(2) / (log(2) − log(3)) = log(2) / log(2/3)` (log a − log b = log(a/b)) `≈ −1,710`.

**6. Logarithme — log(5 − x) = 8** (2.15 l)
`log(5 − x) = 8 ⇔ 5 − x = 10⁸` (définition du logarithme) `⇔ x = 5 − 10⁸ = −99’999’995`.
Vérification : `5 − x = 10⁸ > 0`, le logarithme est bien défini ✓. `S = {−99’999’995}`.

**7. Base inconnue — log_x(256) = 4** (2.22 b)
Condition : `x > 0` et `x ≠ 1` (une base de logarithme est strictement positive et différente de 1).
`log_x(256) = 4 ⇔ x⁴ = 256` (définition du logarithme) `⇔ x = 4 ou x = −4` ; seule la solution positive convient. `S = {4}`.

**8. Calcul — log_4(√2)** (2.20 h) et **log_2(50)**
`√2 = 2^(1/2) = (4^(1/2))^(1/2) = 4^(1/4)`, donc `log_4(√2) = 1/4`.
`50` n'est pas une puissance de 2 (`2⁵ = 32 < 50 < 64 = 2⁶`) : `log_2(50) = log(50) / log(2)` (changement de base) `≈ 5,644`.

**9. Application — 37 · e^(−0,02t) = 25** (p. 29)
`37 · e^(−0,02t) = 25 ⇔ e^(−0,02t) = 25/37` (on isole le terme exponentiel) `⇔ −0,02t = ln(25/37)` (définition du logarithme)
`⇔ t = ln(25/37) / (−0,02) ≈ 19,602` (la forme que donne la chaîne, non simplifiée en −50 · ln(25/37) : Q11).

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

## Critères d'acceptation

| Id | Critère | Vérif. |
|---|---|---|
| EL-01 | Pour chaque entrée de la batterie (`tests/python/cas_el.py` : 2.13 a-o, 2.15, 2.18, 2.20, 2.21, 2.22, 2.23, 2.24, 2.26, 2.27 et les exemples p. 22-23, 26, 28-29), l'ensemble solution exact et la valeur ≈ à 10⁻³ sont ceux attendus ; la batterie est vérifiée une fois contre les solutions p. 38-40 et contre le corrigé | [auto-py] |
| EL-02 | Oracle indépendant : chaque solution, substituée dans l'équation de l'énoncé avec mpmath, donne un écart < 10⁻⁹ ; `solveset` sur ℝ donne le même nombre de solutions ; S = ∅ confirmé ; tirages aléatoires a^(px+q) = a^(rx+s), k·a^f = b, log_b(u) = c comparés à l'oracle | [auto-py] |
| EL-03 | Tokeniseur : `ln`, `exp`, `log2`, `log_3`, `log10`, `sqrt` lus comme fonctions avant les lettres ; `2x`, `3ln(x)`, `xlog(x)` multiplication implicite ; `e^x = 7` : e est la constante ; `e` comme seule lettre, `2e = 5`, `e^2 = e` : refusés avec le message prévu ; `x + e = 3` accepté | [auto-py] |
| EL-04 | Tout le TeX vient de l'arbre : une équation en e^x ne produit que `\ln`, une équation en base 10 que `\log` ; `exp_log.py` et `resoudre_el.py` ne contiennent ni `latex(` ni `arbre_depuis_sympy` | [auto-py] (analyse du texte source) |
| EL-05 | `log` = base 10, `ln` = base e, `log_a` = base a, sur toute la batterie (valeur numérique de chaque membre) | [auto-py] |
| EL-06 | Chaque ligne « ⇔ » porte une propriété tirée de la liste fermée ci-dessus ; aucune ligne sans justification, sauf l'arithmétique évidente (x + 1 = 3 ⇔ x = 2) | [auto-py] |
| EL-07 | Exact puis ≈ : chaque « ≈ » suit une valeur exacte sur la même ligne ; 3 décimales ; virgule décimale ; aucun point décimal (SOC-12) ; **notation suisse (Q5, Q12) : ’ dès 4 chiffres sur la partie entière seulement** (−99’999’995, 1’234,567, 0,0001), `\text{’}` en TeX ; saisie de ' et ’ lue 1000, « 1 000 » refusé avec un message (`moteur/nombres.py`) | [auto-py] |
| EL-08 | Second membre ≤ 0 (a^f = b, b ≤ 0, k·a^f = b avec b/k ≤ 0) : S = ∅ justifié par « une exponentielle est strictement positive », jamais par un logarithme d'un nombre négatif | [auto-py] |
| EL-09 | Équations logarithmiques : aucune carte d'ensemble de définition ; une vérification de chaque solution (argument > 0) ; base inconnue : condition annoncée, solution rejetée si x ≤ 0 ou x = 1 (log_x(256) = 4 : S = {4}) | [auto-py] |
| EL-10 | `log(x^2) = 2` donne S = {−10 ; 10} par la définition ; aucune sortie ne contient « 2 log|x| » ni « 2\log\left|x\right| » | [auto-py] |
| EL-11 | **Entrée hors programme** (x·2^x = 8, 2^x + 3^x = 5, x^x = 4, 2^(x³) = 8, plusieurs logarithmes sommés, inconnue dans une base et dans un exposant à la fois) : le texte affiché à l'élève est exactement « Cette équation ne se résout pas avec les méthodes du cours. » (décision du 26.10.2026) ; jamais « non applicable », jamais une étape fausse ni une valeur numérique donnée comme solution ; détail technique dans `detail` seulement. Une inéquation garde son message de lecture (« Les inéquations ne sont pas traitées par cet outil : écrivez une équation avec =. ») | [auto-py] |
| EL-12 | Aucune sortie ne contient le vocabulaire interdit de SOC-15 (`test_vocabulaire.py` étendu) ; JSON strict | [auto-py] |
| EL-13 | `exercice(niveau, graine)` est déterministe, produit un gabarit du niveau, et le moteur le résout (oracle EL-02) pour 500 graines | [auto-py] |
| EL-14 | Manifeste (`test_manifeste`, `test_resoudre_import`) et instantanés de l'outil ; **les instantanés de tous les autres moteurs sont inchangés** | [auto-py] |
| EL-15 | Page : rendu de la batterie égal à `tests/pages/references/exponentielles-logarithmes.json` ; clavier avec log, ln, log_, e, = ; exercice au hasard (pool C) et corrigé | [auto-page] |
| EL-16 | Registre et accueil (cellule III/C) : description « Équations exponentielles et logarithmiques, calcul de logarithmes, étape par étape. » identique dans `commun/registre.json` et `index.html` (ACC-01) ; posés après relecture des exemples | [auto-py] + [manuel] |
| EL-17 | Les exemples de rédaction 1 à 9 ci-dessus, relus à l'écran sur téléphone et comparés au corrigé, sont validés | [manuel] |

## Pour les 2M (plus tard, hors de cette version)

Même moteur, paramètre interne `filiere="M"` : carte « Ensemble de définition » **avant** de résoudre (cartes de condition de l'outil ED,
`analyser_complet` de `moteur/noyau.py`), puis vérification contre l'ED ; équations à plusieurs logarithmes (ln(u) + ln(v) = c) ; log(x²) = 2 log(x)
écrit avec « x > 0 » ; inéquations avec le sens justifié (croissance de ln et de exp ; base entre 0 et 1) ; pool d'exercices M séparé.
