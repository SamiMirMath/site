# Outil « Ensemble de définition » (3e Ms, Mr)

URL : `/ensemble-definition/` · moteur : `ensemble-definition/ensemble_def.py` (noyau partagé, intact).

## Fonctionnel

- Entrée : f(x) avec `x`, nombres (virgule ou point), `+ − * / ^`, parenthèses, multiplication
  implicite (`2x`, `3ln(x)`, `(x+1)(x-2)`), `ln`/`log`, `exp`/`e^(…)`, `sqrt`/`√`/`racine`.
  « f(x) = » ou « y = » en tête est ignoré.
- Conditions d'existence repérées dans l'ordre d'apparition, sans doublon :
  argument de logarithme > 0 ; dénominateur ≠ 0 ; contenu de racine carrée ≥ 0 ;
  base > 0 pour une puissance d'exposant non constant ou de dénominateur pair négatif ;
  base ≥ 0 pour une puissance d'exposant constant irrationnel positif (règle de x^α ci-dessous).
- Une carte par condition (guide R10 : titre « Condition i (genre) » sans l'inégalité, qui s'écrit une seule
  fois dans la première ligne ; sans rappel de la règle, « condition ⇔ solution » ; une racine au dénominateur
  est UNE condition A > 0 ; ordre des termes de l'élève ; a² − b² factorisé, sinon Δ écrit une seule fois) :
  résolution détaillée (factorisation, Δ, racines évidentes, tableau de signes avec « | » pour un facteur non
  nul et « ‖ » réservé aux valeurs interdites, substitution t = ln(B), e^B, √B puis retour à x, sommes de ln).
  Pas de ligne « E_i = … » : la dernière ligne écrit les ensembles.
- Carte finale : ED = intersection écrite avec les ensembles eux-mêmes (« ]−1 ; +∞[ ∩ ]−2 ; 2[ = ]−1 ; 2[ » ;
  les conditions « ≠ » sont écrites comme des exclusions `\ {…}`), forme simplifiée, contrôle numérique indépendant (≈ 5 000 points).
- Repli (sans en nommer la méthode à l'élève) : pour un facteur qui ne se résout pas avec les méthodes du
  cours, « solution obtenue numériquement : x ≈ … » ; un mélange de x et d'un ln ou exp est annoncé
  comme tel (« on ne peut pas isoler x »).
- **Atome au degré 1** (ln, exp ou racine, par ex. 1 − ln x > 0, e^x − 3 > 0, √x − 2 > 0) : pas de « On pose
  t = … ». On isole l'atome du côté où son coefficient est positif (« 1 − ln x > 0 ⇔ ln x < 1 »), on
  divise par ce coefficient (> 0), puis on applique la réciproque en l'écrivant : « ln x < 1 ⇔ x < e
  (exp est croissante) », « e^x > 3 ⇔ x > ln 3 (ln est croissante) », « √u > c ⇔ u > c² si c ≥ 0 »
  (« toujours vrai » si c < 0). e^u > c : toujours vrai si c ≤ 0 ; e^u < c ou e^u = c : impossible si c ≤ 0
  (« une exponentielle est strictement positive »). La substitution t = … est réservée à l'atome au
  degré ≥ 2 ((ln x)² − 1, e^(2x) − 3e^x + 2), avec les mêmes formulations des réciproques.
- Quand on chasse les dénominateurs, la condition est d'abord écrite telle qu'elle découle de la fonction,
  puis l'étape est montrée : « x²/3 − 1/2 > 0 ⇔ 2x² − 3 > 0 (on multiplie par 6 > 0) » ; le facteur est
  toujours strictement positif (le sens d'une inégalité ne change jamais).

## Conventions

- **ED de x^α, α constant** (validé le 14.10.2026) : α = 0 : ℝ ; α entier ≥ 1 : ℝ ; α entier ≤ −1 : ℝ* ;
  α = p/q irréductible, q impair : ℝ (ℝ* si α < 0) ; α = p/q avec q pair, ou α irrationnel :
  [0 ; +∞[ si α > 0, ]0 ; +∞[ si α < 0. Un exposant constant est d'abord simplifié exactement
  (ln 4 − 2 ln 2 = 0 ⇒ ℝ) ; si l'on ne peut pas trancher, comportement prudent ]0 ; +∞[.
- Une racine ou puissance fractionnaire s'affiche en racine : f(x) = x^{3/2} = √(x³) (la saisie reste
  montrée à côté). Un exposant constant qui vaut un rationnel sans le montrer est remplacé par ce
  rationnel (saisie conservée).
- x^(1/3) et plus généralement x^(p/q) avec q impair : **défini sur ℝ** (validé).
- u⁰ = 1 sur ℝ (0⁰ compris), mais **l'ED de la base reste exigé** : (ln x)⁰ pour x > 0,
  (1/x)⁰ pour x ≠ 0 (tranché le 14.10.2026, Q6 ; comportement actuel conforme).
- Valeurs exactes en priorité (fractions, racines, e, ln) ; une valeur approchée est toujours
  marquée ≈ et accompagnée de sa méthode.

## Cas limites à couvrir

`x^(2-2)` (crash actuel, bug 5), `1/(1-1)` (division par zéro), `ln(-x^2-1)` (∅),
`sqrt(-x^2)` ({0}), `ln(ln(ln(x)))`, `x^x`, `sqrt(x-1)/sqrt(x-1)`, saisies avec « 1'000 ».

## Critères d'acceptation

| Id | Critère | Vérif. |
|---|---|---|
| ED-01 | Pour tous les exemples et exercices de la page, la sortie est identique à l'instantané de référence | [auto-py] |
| ED-02 | Pour ≥ 1 000 fonctions générées avec graine fixe, l'ED trouvé est en accord avec le contrôle numérique (`verifier`) | [auto-py] |
| ED-03 | `x^(2-2)` et `x^(1/2-1/2)` ne provoquent pas d'exception et donnent le même ED que `x^0` | [auto-py] |
| ED-04 | Toute entrée de la liste des saisies invalides donne `ok: false` et un message en français | [auto-py] |
| ED-05 | Les exercices générés (toutes graines testées, tous niveaux) sont résolus sans valeur approchée de zéro ou de borne | [auto-py] |
| ED-06 | Le format de sortie commun est respecté (schéma) | [auto-py] |
| ED-07 | Le contrôle numérique ne signale aucun désaccord quand l'ED est juste, y compris près d'un zéro double (ln(x²−10x+25), 1/(x²−6x+9)) | [auto-py] (`test_controle_numerique_sans_fausse_alerte`) |
| ED-09 | Règle de l'ED de x^α (30 exposants : 0, entiers, p/q, irrationnels, exposants simplifiables) conforme à l'oracle haute précision | [auto-py] (`test_exposant_constant.py`) |
| ED-08 | `x^0` : ED = ℝ ; `(ln(x))^0` : ]0 ; +∞[ ; `(1/x)^0` : ℝ \ {0} ; `(sqrt(x-1))^0` : [1 ; +∞[ | [auto-py] |
