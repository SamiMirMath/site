# Outil « Dérivée, signe et variations » (3e Ms, Mr)

URL : `/derivee-variations/` · moteur : `derivee-variations/derivee_variations.py`
(+ noyau `ensemble_def.py`).

## Fonctionnel

1. **Rappel** : f(x) et son ED (détail renvoyé à l'outil « Ensemble de définition »).
2. **Dérivée** (méthode décidée avec l'enseignant) :
   - somme/différence : terme à terme ;
   - produit u·v et quotient u/v (facteurs non constants) : u, v, u', v' nommés, puis la formule,
     **au premier niveau seulement** (f ou chaque terme d'une somme) ;
   - composée ln(u), e^u, √u, u^n : u et u' nommés dans la même phrase que le résultat, sans tableau ;
   - facteur constant c·g, g·c, g/c, signe moins : on dérive g, puis une ligne conclut
     « f'(x) = c · (g)' = … » (correction `a9b2a6e`) ;
   - toute ligne qui conclut porte le nom de ce qu'elle dérive : « f'(x) = » pour f entière,
     « (morceau)' = » sinon ;
   - SymPy ne sert qu'à mettre f' sous forme **factorisée** (jamais développée).
3. **ED de f'** : si l'ED de f' diffère de celui de f, il est **calculé et affiché** comme une étape
   (validé). Exemple : √(x²−4), ED(f) = ]−∞;−2] ∪ [2;+∞[, ED(f') = ]−∞;−2[ ∪ ]2;+∞[.
4. **Signe de f'** : zéros de f' d'abord (narration), puis tableau de signes avec une ligne par
   facteur de f' et la ligne f'(x).
5. **Variations** : ligne f(x) en **flèches seules** (validé), points d'extremum marqués ;
   en un point où f est définie mais pas f', la ligne f(x) porte la valeur f(a) (Q3) ;
   liste des extrema locaux avec valeur exacte de f quand c'est possible (sinon ≈).

## Conventions

- Tableau de variations : flèches seules, sans valeurs ni limites (validé).
- Point a où f est définie mais pas f' (±2 pour √(x²−4), 0 pour √(x²)) : l'ED de f' est calculé
  (validé) ; dans le tableau (tranché le 14.10.2026, Q3) :
  - ligne f'(x) : **double barre** ;
  - ligne f(x) : **la valeur f(a), sans barre**.
- Extremum local (tranché le 14.10.2026, Q3) :
  - **(i)** en un point **intérieur** de l'ED de f où f' change de signe, même si f' n'y est pas
    définie (√(x²) en 0, x^(2/3) en 0) ;
  - **(ii)** en toute **borne fermée** de l'ED de f (±2 pour √(x²−4), ±2 pour √(4−x²), 0 pour √x
    et x√x) : extremum local dont la nature vient du sens de variation sur l'intervalle adjacent
    (borne gauche : croissante à droite ⇒ minimum, décroissante ⇒ maximum ; borne droite :
    croissante à gauche ⇒ maximum, décroissante ⇒ minimum).
- Fonction constante (décidé le 14.10.2026, T06b) : sur chaque intervalle de l'ED où f' est
  identiquement nulle, la ligne f'(x) porte « 0 » et la ligne f(x) une **flèche horizontale →** ;
  la valeur constante figure en toute borne de l'intervalle qui appartient à l'ED ; **aucun
  extremum** n'est annoncé sur cet intervalle. À ne pas confondre avec un zéro **isolé** de f'
  (x³ en 0) : « 0 » dans la colonne de 0, ↗ ↗ de part et d'autre, aucun extremum.
- Coefficients fractionnaires : affichage à alléger (`\frac{1}{2\sqrt{x}}` plutôt que
  `\frac{\frac{1}{2}}{\sqrt{x}}`), sans changer la valeur.

## Critères d'acceptation

| Id | Critère | Vérif. |
|---|---|---|
| DV-01 | Pour une liste de ≥ 60 fonctions (dont x^(p/q), produits sous facteur constant, quotients, composées), f' du moteur = dérivée numérique de f en 4 points de l'ED (écart relatif ≤ 1e-5) | [auto-py] (existe en partie : `test_derivee_puissances.py`, `test_derivee_narration.py`) |
| DV-02 | Toute ligne d'étape commençant par « f'(x) = » se termine par le résultat final | [auto-py] (existe : `test_derivee_narration.py`) |
| DV-03 | Si ED(f') ≠ ED(f), une étape « ED de f' » donne ED(f') et il est égal (à 1e-9 près sur les bornes) à l'ED calculé par le noyau | [auto-py] |
| DV-04 | Critère (i) : √(x²) : minimum local en 0, f(0) = 0 ; x^(2/3) : minimum en 0 ; √(x²−2x+1) : minimum en 1 | [auto-py] (existe : `test_aucun_extremum_manque`, échec attendu jusqu'à T06) |
| DV-05 | Pour chaque extremum **intérieur** annoncé, f' change de signe et f est définie au point ; pour chaque changement de signe de f' en un point intérieur de l'ED de f, un extremum est annoncé | [auto-py] (propriété sur la liste DV-01) |
| DV-06 | Les sorties des exemples et exercices de la page sont identiques aux instantanés | [auto-py] |
| DV-07 | Aucun coefficient affiché sous la forme `\frac{\frac{…}{…}}{…}` pour la liste DV-01 | [auto-py] |
| DV-08 | Exercices générés : f' et tableau obtenus sans valeur approchée de zéro de f' | [auto-py] |
| DV-09 | Critère (ii) : √(x²−4) : minimum local en −2 et en 2 (f = 0) ; √(4−x²) : minimum local en −2 et en 2 (f = 0), maximum en 0 (f = 2) ; √x : minimum en 0 ; x√x : minimum en 0 ; aucun extremum de bord pour une borne ouverte (ln x en 0) | [auto-py] (`test_extrema_bornes_fermees`, échec attendu jusqu'à T06) |
| DV-10 | Tableau de √(x²−4) : ligne f'(x) avec double barre en ±2 ; ligne f(x) avec la valeur 0 en ±2, sans barre | [auto-py] |
| DV-11 | x^(2−2) : ligne f'(x) « 0 », ligne f(x) →, aucun extremum ; √(x²)/x : « 0 » et → sur chaque intervalle, double barre en 0 (hors de l'ED) | [auto-py] (`test_tableau_variations.py`) |
| DV-12 | x³ : ligne f'(x) « + 0 + », ligne f(x) « ↗ ↗ », aucun extremum (zéro isolé de f') | [auto-py] (`test_tableau_variations.py`) |
| DV-13 | f constante sur [0 ; +∞[ ((√x)⁰) : la valeur 1 figure en 0 sur la ligne f(x), puis →, aucun extremum | [auto-py] (`test_tableau_variations.py`) |
