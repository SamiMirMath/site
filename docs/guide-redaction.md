# Guide de rédaction (corrigés visibles par l'élève)

Décidé avec l'enseignant le 15.10.2026. Public : un élève moyen de gymnase, sur téléphone. Il se
perd dans les détails : **le minimum de lignes qui reste rigoureux**. Ce guide prime sur les
formulations plus anciennes des specs (`socle-commun.md` 7c, `limites-asymptotes.md` « Style de
rédaction », `derivee-variations.md` point 4, `ensemble-definition.md` « une carte par condition »)
et annule la règle « facteurs évidents hors du tableau » (commit `2bfcc1a`).

Notation : `« … »` = substitution des limites, signes gardés (ce n'est pas un calcul dans ℝ).
Dans les exemples, `lim_(x→a)` se rend en TeX par `\lim_{x\to a}`.

## Règles

**R1. Ne justifier que ce qui est nouveau ou délicat.** Jamais justifié : limite d'un polynôme ou
d'une affine, 1/xⁿ → 0, constante/∞ → 0, substitution d'une valeur, signe d'une affine (seulement
son zéro), signe d'un carré, d'une exponentielle, d'une racine, d'un polynôme sans zéro.
Toujours justifié, en quelques mots : √(x²) = |x| = −x (x < 0) ; un 0⁺ ou 0⁻ (« cf. tableau de
signes ») ; le signe d'une constante qui décide (ln 5 > 0) ; la méthode (mise en évidence,
conjuguée, croissance comparée avec sa limite de référence, Bernoulli-L'Hôpital).

**R2. Annoncer une forme en UNE ligne**, par substitution des limites, signes gardés, entre « » :
`lim … = « √(+∞)/(−∞) » = « +∞/−∞ » : forme indéterminée`. Sans forme indéterminée, la même ligne
conclut : `lim … = « 8/0⁻ » = −∞`. Plus de lignes « le numérateur … tend vers … et le dénominateur … »,
« Or √t → +∞ quand t → +∞ », « x → −∞, donc x + 2 → −∞ ». On peut dire « le terme dominant est x² »
(en mots, entre parenthèses) ; remplacer par le terme dominant, ∼, « équivalent » et « se comporte
comme » restent interdits.

**R3. Chaîne d'égalités, une étape par ligne**, la forme annoncée en tête de chaîne. Justification
entre parenthèses, en un à cinq mots : (mise en évidence), (conjuguée), (x < 0 : √(x²) = −x),
(propriétés de ln), (croissance comparée : lim …). On ne recopie pas la factorisation dans la
justification, ni « on simplifie par x ; 1/x² → 0 » : la dernière ligne montre déjà la valeur.

**R4. Mise en évidence de la puissance de x seule** : x(−4 + 5/x), x²(1 − 4/x + 5/x²) ; jamais le
coefficient avec elle (−4x(1 − 5/(4x))).

**R5. Une ligne par limite, jamais de répétition.** Une sous-limite n'est pas recalculée avant chaque
chaîne ; un calcul commun (division euclidienne, tableau de signes, Δ) est écrit une fois et réutilisé
(la division vaut en −∞ et en +∞). Limites latérales : deux lignes `lim_(x→a⁻) …`, `lim_(x→a⁺) …`.
`x→a` est écrit sur chaque `lim`.

**R6. Conclusions courtes, en une ligne** : « Asymptote verticale : x = 3. », « Asymptote horizontale :
y = 0. », « Asymptote oblique : y = −x + 2. », « Limite finie : pas d'asymptote verticale, trou dans le
graphique en (1 ; 1). ». Supprimées : « x = a est une valeur interdite », « La limite est infinie : pas
d'asymptote horizontale », « Le degré du numérateur dépasse … », « a et b sont finis (et a ≠ 0) »,
« Les deux limites sont finies et égales ». Position relative : f(x) − (ax + b) en chaîne, puis
« > 0 pour x … : la courbe est au-dessus de l'asymptote ».

**R7. Tableau de signes : TOUJOURS une ligne par facteur du numérateur et du dénominateur, puis la ligne
du quotient**, même pour un facteur évident (x² + 1, √(4x² + 1), (x + 2)², eˣ) et même pour une
constante (positive : « 3 : + + + » ; négative : « −1 : − − − »). Aucune phrase ne justifie le signe d'un
facteur évident ou affine (seulement le zéro d'une affine) : la ligne du tableau suffit. Plus de « donc
f'(x) est du signe de … », de « Bilan », de « Un produit est nul si et seulement si … », de « On étudie le
signe de chaque facteur ». Avant le tableau, une seule ligne : zéros et valeurs interdites.

**R8. Limites : le tableau de signes est TOUJOURS donné pour un dénominateur ou un argument de ln qui
tend vers 0, même affine** (x − 3, x − 5), en tête de l'étude. Justification courte dans la ligne de la
limite : `(x − 3 < 0 : cf. tableau de signes)`.

**R9. Bernoulli-L'Hôpital** : forme annoncée (R2), puis `= lim` du quotient des dérivées, avec les
hypothèses toutes nommées en une parenthèse (dérivables sur …, `(dénominateur)' ≠ 0`). f désigne déjà
la fonction étudiée : jamais « f'/g' » ni « g'(x) » dans la sortie ; le dénominateur est nommé par son
expression, `(x − 1)' = 1 ≠ 0`. Quand la dérivée du dénominateur est une constante, le quotient est
écrit tel quel, `(1/x)/1`, et la valeur suit directement. Chaque membre de la chaîne garde son
`lim_(x→a)`. L'existence de la limite du quotient des dérivées est la chaîne elle-même (pas de phrase).
Si une hypothèse n'est pas vérifiée, la règle n'est pas appliquée (phrase de repli).

**R10. Ensemble de définition** : une carte par condition, sans phrase de rappel de la règle, « condition
⇔ solution » ; une racine au dénominateur = une seule condition A > 0 ; Δ au plus une fois, en une ligne ;
ordre des termes de l'élève (4 − x², pas −x² + 4) ; a² − b² factorisé directement ((2 − x)(2 + x)), sinon
Δ ; un seul tableau ; aucune répétition : le titre de la carte ne porte pas l'inégalité (« Condition 1
(logarithme) »), elle s'écrit une seule fois, dans la première ligne « x + 1 > 0 ⇔ x > −1 », et il n'y a pas de ligne
« E₁ = … » ; dernière ligne avec les ensembles : « ED = ]−1 ; +∞[ ∩ ]−2 ; 2[ = ]−1 ; 2[ ». Dans un tableau,
« ‖ » est réservé aux valeurs interdites ; une ligne de facteur qui ne s'annule pas sur la colonne d'une valeur
critique y porte un trait simple « | » (en −2 pour 2 − x, en 2 pour 2 + x).

**R11. Dérivée** : les justifications restent TOUJOURS, car les élèves les oublient : « (x²)' = 2x (règle de la
puissance) », « (ln x)' = 1/x (règle de base) », règle du produit, du quotient, de la chaîne (« de la forme √u »).
Seules les opérations neutres sont supprimées : jamais « + 0 », « − 0 », « · 1 », « 1 · » ni équivalents
(u'(x) = 8x, pas 8x + 0). u, u', v, v' sur une ligne ; l'étape délicate (chasser une racine du numérateur) est écrite.

**R12. Vouvoiement.** L'enseignant vouvoie ses élèves : tout texte qui leur est destiné vouvoie — messages d'erreur
(« Écrivez une équation », « Ouvrez une parenthèse : ln(x). », « Choisissez une autre lettre »), invites des pages (« Cliquez sur … »,
« à résoudre vous-même »), accroches, rappels de méthode, boutons. Jamais tu, ton, ta, tes, toi, ni impératif en -e ou -s
(« choisis », « écris », « ouvre », « mets », « clique », « réessaie »). Le corrigé reste à la forme impersonnelle (« on », infinitif).
Vérifié par `tests/python/test_vocabulaire.py` (`TestVouvoiement` : littéraux des moteurs, pages, `commun/*.js`, registre ;
les corrigés de tous les instantanés) avec le détecteur `aides_sortie.TUTOIEMENT`, qui ne signale un impératif en -e qu'en début de phrase (« Utilise la règle »), jamais « on utilise la règle ».

**R13. Fractions et notation scientifique** (décision du 26.10.2026, corrigée le même jour, pour tous les outils). L'enseignant privilégie les
fractions : toute valeur exacte que l'outil **calcule à partir d'entiers ou de puissances** s'écrit en fraction (log x = 5/2, 10⁻¹ = 1/10, log₉(27) = 3/2),
jamais en décimal. Les **décimaux de l'énoncé gardent leur écriture partout, exposant compris** : log(x) = −0,27 donne x = 10^(−0,27) ≈ 0,537 (pas 10^(−27/100)).
Quand le calcul part de décimaux de l'énoncé et donne un **décimal fini**, on garde le décimal comme le corrigé : 2000 · 1,045ⁿ = 3805 donne 1,045ⁿ = 1,9025 (pas 761/400) ;
un résultat qui n'est pas un décimal fini reste une fraction (3e^x = 0,65 donne e^x = 13/60). Les très grands et très petits nombres s'écrivent en **notation scientifique** :
puissances de 10 laissées telles quelles (10¹⁰, 10⁻⁴) et valeurs approchées en `3,162 × 10⁻⁵` ou `1 × 10¹⁰` sous 10⁻³ et dès 10⁶. Les valeurs
approchées « ≈ » restent à virgule décimale. Appliquée à l'outil Exponentielles et logarithmes (`tex_approx`, `_nb_exact`) ; **les autres outils
n'ont pas encore été relus avec cette règle.**

Inchangé : interdiction des équivalents, phrase de repli, virgule décimale, garde-fou des valeurs.

**R14. Une chaîne de ⇔ s'écrit une étape par ligne** (décision du 26.10.2026, outil « Exponentielles et logarithmes »), comme le corrigé de
l'enseignant : le ⇔ en début de ligne, les ⇔ alignés les uns sous les autres, l'expression à côté, la **propriété nommée à droite de la ligne**
(sous l'expression sur un écran étroit, jamais de défilement horizontal à 360 px). Des égalités qui se suivent sans propriété restent sur la même
ligne (`√2 = 2^(1/2) = 4^(1/4)`, `Δ = 1² − 4·1·2 = −7`) ; une suite d'égalités qui a une propriété repart sur une nouvelle ligne dont le « = » est
aligné sous celui de la ligne d'au-dessus (`x = log(2)/(log(2) − log(3))` puis `= log(2)/log(2/3)`). Les autres outils ne sont pas encore concernés.


---

## Exemples de référence

### 1. (x² − 1)/(x − 3), en 3 et en +∞

```
Signe de x − 3
x − 3 | −∞   3   +∞
x − 3 |  −   ‖   +

lim_(x→3⁻) (x² − 1)/(x − 3) = « 8/0⁻ » = −∞    (x − 3 < 0 : cf. tableau de signes)
lim_(x→3⁺) (x² − 1)/(x − 3) = « 8/0⁺ » = +∞    (x − 3 > 0 : cf. tableau de signes)
Asymptote verticale : x = 3.
```
```
lim_(x→+∞) (x² − 1)/(x − 3) = « +∞/+∞ » : forme indéterminée
   = lim_(x→+∞) x²(1 − 1/x²) / (x(1 − 3/x))      (mise en évidence)
   = lim_(x→+∞) x(1 − 1/x²)/(1 − 3/x) = « +∞ · 1 » = +∞
Division euclidienne : x² − 1 = (x − 3)(x + 3) + 8, donc f(x) = x + 3 + 8/(x − 3).
lim_(x→+∞) (f(x) − (x + 3)) = lim_(x→+∞) 8/(x − 3) = « 8/+∞ » = 0 : asymptote oblique y = x + 3.
8/(x − 3) > 0 pour x > 3 : la courbe est au-dessus de l'asymptote.
```
En −∞ : la chaîne de la limite seule, puis « même division : asymptote oblique y = x + 3 ;
8/(x − 3) < 0 pour x < 3 : la courbe est au-dessous ».

### 2. √(x² − 4x + 5) en −∞ (f, a, b, position)

```
lim_(x→−∞) √(x² − 4x + 5) = « √(+∞ + ∞) » = +∞

a = lim_(x→−∞) √(x² − 4x + 5)/x = « √(+∞ + ∞)/(−∞) » = « +∞/−∞ » : forme indéterminée
  = lim_(x→−∞) √(x²(1 − 4/x + 5/x²))/x                      (mise en évidence)
  = lim_(x→−∞) −x√(1 − 4/x + 5/x²)/x                         (x < 0 : √(x²) = |x| = −x)
  = lim_(x→−∞) −√(1 − 4/x + 5/x²) = −1

b = lim_(x→−∞) (√(x² − 4x + 5) + x) = « +∞ − ∞ » : forme indéterminée
  = lim_(x→−∞) (−4x + 5)/(√(x² − 4x + 5) − x)                (conjuguée)
  = lim_(x→−∞) x(−4 + 5/x)/(−x√(1 − 4/x + 5/x²) − x)         (mise en évidence ; x < 0 : √(x²) = −x)
  = lim_(x→−∞) (−4 + 5/x)/(−√(1 − 4/x + 5/x²) − 1) = −4/(−2) = 2
Asymptote oblique : y = −x + 2.

f(x) − (−x + 2) = √(x² − 4x + 5) + x − 2 = 1/(√(x² − 4x + 5) − x + 2)   (conjuguée)
> 0 pour x < 2 : la courbe est au-dessus de l'asymptote.
```

### 3. ln(x² − 4x)/(x − 5), en 4⁺, en 5 et en +∞

```
Signe de x² − 4x
x        | −∞      0       4      +∞
x        |    −    0   +   |   +
x − 4    |    −    |   −   0   +
x² − 4x  |    +    0   −   0   +

Signe de x − 5
x − 5    | −∞   5   +∞
x − 5    |  −   ‖   +

lim_(x→4⁺) ln(x² − 4x)/(x − 5) = « ln(0⁺)/(−1) » = « −∞/(−1) » = +∞    (x² − 4x > 0 : cf. tableau de signes)
Asymptote verticale : x = 4.

lim_(x→5⁻) ln(x² − 4x)/(x − 5) = « ln 5/0⁻ » = −∞    (ln 5 > 0 ; x − 5 < 0 : cf. tableau de signes)
lim_(x→5⁺) ln(x² − 4x)/(x − 5) = « ln 5/0⁺ » = +∞    (x − 5 > 0 : cf. tableau de signes)
Asymptote verticale : x = 5.

lim_(x→+∞) ln(x² − 4x)/(x − 5) = « ln(+∞)/(+∞) » = « +∞/+∞ » : forme indéterminée    (le terme dominant de x² − 4x est x²)
   = lim_(x→+∞) ln(x²(1 − 4/x))/(x(1 − 5/x))                 (mise en évidence)
   = lim_(x→+∞) (2 ln x + ln(1 − 4/x))/(x(1 − 5/x))          (propriétés de ln)
   = lim_(x→+∞) (2 · ln(x)/x + ln(1 − 4/x)/x)/(1 − 5/x)
   = (2 · 0 + 0)/1 = 0                                        (croissance comparée : lim_(x→+∞) ln(x)/x = 0)
Asymptote horizontale : y = 0.
```

### 4. √(4x² + 1)/(x + 2) : signe de f' (Dérivée) et limite en −∞

```
f'(x) = (8x − 1)/(√(4x² + 1)(x + 2)²) = 0 ⇔ 8x − 1 = 0 ⇔ x = 1/8 ; valeur interdite : x = −2.

x           | −∞     −2     1/8     +∞
8x − 1      |    −   ‖   −   0   +
√(4x² + 1)  |    +   ‖   +   |   +
(x + 2)²    |    +   ‖   +   |   +
f'(x)       |    −   ‖   −   0   +
f(x)        |    ↘   ‖   ↘  min  ↗

Minimum local en x = 1/8 : f(1/8) = 2√17/17.
```
```
u = √(4x² + 1), u' = 4x/√(4x² + 1) ; v = x + 2, v' = 1
f'(x) = (u'v − uv')/v² = (4x(x + 2)/√(4x² + 1) − √(4x² + 1))/(x + 2)²
      = (4x(x + 2) − (4x² + 1))/(√(4x² + 1)(x + 2)²)        (on multiplie par √(4x² + 1))
      = (8x − 1)/(√(4x² + 1)(x + 2)²)
```
```
lim_(x→−∞) √(4x² + 1)/(x + 2) = « √(+∞)/(−∞) » = « +∞/−∞ » : forme indéterminée
   = lim_(x→−∞) √(x²(4 + 1/x²))/(x(1 + 2/x))        (mise en évidence)
   = lim_(x→−∞) −x√(4 + 1/x²)/(x(1 + 2/x))          (x < 0 : √(x²) = |x| = −x)
   = lim_(x→−∞) −√(4 + 1/x²)/(1 + 2/x) = −2
Asymptote horizontale : y = −2.
```

### 5. x²e^(−x) en +∞

```
lim_(x→+∞) x²e^(−x) = « +∞ · 0⁺ » : forme indéterminée
   = 0          (croissance comparée : lim_(x→+∞) xⁿe^(−x) = 0)
Asymptote horizontale : y = 0.
```

### 6. ln(x)/(x − 1) en 1 (Bernoulli-L'Hôpital)

```
lim_(x→1) ln(x)/(x − 1) = « ln 1/0 » = « 0/0 » : forme indéterminée
   = lim_(x→1) (1/x)/1 = 1      (Bernoulli-L'Hôpital : ln x et x − 1 dérivables sur ]0 ; +∞[, (x − 1)' = 1 ≠ 0)
Limite finie : pas d'asymptote verticale, trou dans le graphique en (1 ; 1).
```

### 7. Ensemble de définition : ln(x + 1)/√(4 − x²)

```
Condition 1 (logarithme)
x + 1 > 0 ⇔ x > −1

Condition 2 (racine au dénominateur)
4 − x² = (2 − x)(2 + x) : zéros −2 et 2.
x       | −∞    −2     2     +∞
2 − x   |   +   |   +   0   −
2 + x   |   −   0   +   |   +
4 − x²  |   −   0   +   0   −
4 − x² > 0 ⇔ x ∈ ]−2 ; 2[

ED = ]−1 ; +∞[ ∩ ]−2 ; 2[ = ]−1 ; 2[
```
Trinôme sans factorisation visible : une seule ligne « Δ = 16 : zéros −2 et 2, donc −x² + 4 =
(x + 2)(2 − x) » ; jamais Δ deux fois.

### 8. Exponentielles et logarithmes : 2^(x − 1) = 3^x (bases différentes)

```
Étape 1 · Bases différentes
        2^(x−1) = 3^x
⇔       log(2^(x−1)) = log(3^x)                       (log des deux membres)
⇔       (x − 1)·log(2) = x·log(3)                     (log(a^A) = A · log(a))
⇔       x·log(2) − log(2) = x·log(3)
⇔       x(log(2) − log(3)) = log(2)
⇔       x = log(2)/(log(2) − log(3))                  (car log(2) − log(3) ≠ 0)
          = log(2)/log(2/3)                           (log a − log b = log(a/b))
Solution : S = { log(2)/log(2/3) }, soit x ≈ −1,710
```
Les neuf exemples de rédaction de la spécification (`specifications/exponentielles-logarithmes.md`) suivent la même mise en page.
