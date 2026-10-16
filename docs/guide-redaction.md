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
dernière ligne « ED = E₁ ∩ E₂ = … ».

**R11. Dérivée** : pas de ligne pour une dérivée de référence (x², affine) ni de « + 0 » ; u, u', v, v'
sur une ligne ; l'étape délicate (chasser une racine du numérateur) est écrite.

Inchangé : interdiction des équivalents, phrase de repli, virgule décimale, garde-fou des valeurs.

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
Logarithme : x + 1 > 0 ⇔ x > −1.

Racine au dénominateur : 4 − x² > 0.
4 − x² = (2 + x)(2 − x) : zéros −2 et 2.
x       | −∞    −2     2     +∞
2 + x   |   −   0   +   |   +
2 − x   |   +   |   +   0   −
4 − x²  |   −   0   +   0   −
4 − x² > 0 ⇔ x ∈ ]−2 ; 2[.

ED = ]−1 ; +∞[ ∩ ]−2 ; 2[ = ]−1 ; 2[
```
Trinôme sans factorisation visible : une seule ligne « Δ = 16 : zéros −2 et 2, donc −x² + 4 =
(x + 2)(2 − x) » ; jamais Δ deux fois.
