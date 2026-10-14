# Outil « Ensemble de définition » (3e Ms, Mr)

URL : `/ensemble-definition/` · moteur : `ensemble-definition/ensemble_def.py` (noyau partagé, intact).

## Fonctionnel

- Entrée : f(x) avec `x`, nombres (virgule ou point), `+ − * / ^`, parenthèses, multiplication
  implicite (`2x`, `3ln(x)`, `(x+1)(x-2)`), `ln`/`log`, `exp`/`e^(…)`, `sqrt`/`√`/`racine`.
  « f(x) = » ou « y = » en tête est ignoré.
- Conditions d'existence repérées dans l'ordre d'apparition, sans doublon :
  argument de logarithme > 0 ; dénominateur ≠ 0 ; contenu de racine carrée ≥ 0 ;
  base > 0 pour une puissance d'exposant non constant ou de dénominateur pair négatif.
- Une carte par condition : rappel de la règle, résolution détaillée (factorisation, Δ, racines
  évidentes, tableau de signes, substitution t = ln(B), e^B, √B puis retour à x, sommes de ln),
  ensemble E_i.
- Carte finale : ED = combinaison des E_i (les conditions « ≠ » sont écrites comme des
  exclusions `\ {…}`), forme simplifiée, contrôle numérique indépendant (≈ 5 000 points).
- Repli : SymPy pour un facteur non traité exactement, puis dichotomie numérique (valeurs ≈).

## Conventions

- x^(1/3) et plus généralement x^(p/q) avec q impair : **défini sur ℝ** (validé).
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
