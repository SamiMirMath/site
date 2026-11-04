# Correctif Exp-log : Δ « (−−6) » — journal

## Cause

Méthode « Logarithmes », a^P = a^k avec le même a des deux côtés : `_alpha` (exp_log.py) divise par log(a) et passe à `_suite_polynome`
le second membre **tel qu'il est écrit** : l'arbre de l'exposant (`_expo_arbre`), par exemple Neg(Nb(6)) pour 2^(−6), Op("/", 1, 2) pour 2^(1/2).
`_suite_polynome` ne reconnaît un nombre que par `isinstance(c, Nb)` : il prend alors la branche « c contient un logarithme », qui écrit
P − c = 0 sans calcul (« x² − 5x − (−6) = 0 »), Δ = r0 + 4a·c (« 25 + 4(−6) ») et la formule avec −c (« (−−6) »), puis x₁, x₂ avec √Δ.
Au 1er degré, `_suite_lineaire` écrivait « x = 5 − 6 ».

Deuxième défaut, sur la même branche : avec un second membre nombre **non entier** (2^(−1/4), 2^(0,5)), `_resoudre_polynome` refuse
(coefficients entiers seulement, `_Hors`), et la branche « logarithmes » était aussi prise.

## Correctif (exponentielles-logarithmes/exp_log.py)

1. `_alpha` : après la ligne « P = c » (écrite comme avant), si `_const(c)` est un rationnel, c devient `_nb_exact(_const(c))` (fraction, ou
   décimal si l'énoncé en contient) pour la suite du calcul.
2. `_suite_polynome`, branche du discriminant : quand c est un nombre (rationnel non entier, après le refus de `_resoudre_polynome`),
   a·x² + b·x + (q − c) = 0 est écrit calculé, Δ = b² − 4a(q − c) = valeur (une seule fois « = 0 » si Δ = 0), puis x = r₁ ou x = r₂ quand √Δ est
   rationnel, sinon x₁ et x₂ avec √(valeur). La branche « c contient un logarithme » est inchangée.

## Recherche des entrées touchées

Sonde sur `_suite_polynome` et `_suite_lineaire` (c pas un Nb mais rationnel), sur tout le corpus C (583) et M (276) et sur des variantes
(signes, bases 10, e, 0,5, membres inversés, exposants fractionnaires et décimaux, 1er degré) :

- corpus : aucune entrée en degré 2 ; au 1er degré, seules des puissances de 10 écrites (`log(2x+1)=3` : 2x + 1 = 10³), voulues
  (« x = (10³ − 1)/2 »), non touchées car le correctif est dans `_alpha` seulement ;
- variantes : toutes par `_alpha`, filières C et M (la M réutilise `variantes_equation`) ; couvertes par le nouveau fichier de tests.

Non touchés : 1/64 et 64 au second membre (log(64)/log(2), voulu par la spécification) ; `3^(x^2)=3^(x+6)` et `2^(2x^2)=2^(x+1/2)`
(les deux membres dépendent de x : `_beta`, Δ à coefficients logarithmiques, exemple 11 de la spécification).

## Tests

- `tests/python/test_correctif_explog_delta.py` : 12 entrées × 2 filières. Rédaction : lignes exactes attendues, motifs interdits (« -- »,
  « − (− », « + 4(− », « x = 5 − 6 », √Δ). Oracle (`oracle.py`, mpmath 50 chiffres, arbre de l'outil ED) : chaque racine exacte annule
  g − d à 10⁻⁴⁰ près, aucun autre changement de signe sur [−20 ; 20] au pas 1/64, solutions de l'outil = racines (12 chiffres).
  Aussi : 1/64 inchangé, variante par défaut « Logarithmes » inchangée.
- Sans le correctif : 22 sous-tests de rédaction échouent sur 24 (seul `2^(x^2)=2^(-6)`, sans solution, passait) ; l'oracle passait déjà
  (les solutions étaient justes).
- Instantanés (`test_instantanes.py`, `test_instantanes_resoudre.py`) : aucun changement.

## Temps (resoudre() sur le corpus Exp-log, PC WSL2)

| | C (583) | M (276) |
|---|---|---|
| avant | 0,55 s (0,9 ms/entrée) | 0,21 s |
| après | 0,55 s (0,9 ms/entrée) | 0,20 s |
