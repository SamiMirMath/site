# Outil « Factorisation » (1re C, Ms, Mr)

URL : `/factorisation/` · moteur : `factorisation/factorisation.py` (SymPy obligatoire ; utilise
quelques fonctions du noyau). Références : Javet, *Notions élémentaires d'algèbre*, §2.2 ;
Amaudruz, *Algèbre 1M*, §2.4, exercices 2.11 à 2.16.

## Fonctionnel

- Entrée : polynôme en une ou plusieurs lettres (a…z, « ab » = a·b), coefficients entiers,
  décimaux ou fractions, puissances entières, division par un nombre seulement.
- Méthodes essayées dans l'ordre du cours, puis récursivement sur chaque facteur :
  1. mise en évidence (y compris d'un facteur composé comme (a − b)) ;
  2. identités remarquables (différence de carrés, carré parfait, somme/différence de cubes,
     cube d'un binôme) ;
  3. trinôme : Somme-Produit (a = 1), sinon formule du discriminant (pas de « zéro évident » p/q : on ne teste pas à la main
     des valeurs fractionnaires, décision du 25.10.2026), puis écriture sans fraction c(q₁x − p₁)(q₂x − p₂) si les zéros sont rationnels (FA-10) ;
  4. changement de variable u = x^n ;
  5. groupements ;
  6. racine évidente et division (degré ≥ 3) : on teste les diviseurs entiers du terme constant, ± (jamais p/q) ;
     compléter le carré en dernier recours.
- Contrôle final : le produit affiché, redéveloppé, redonne exactement l'expression ; sinon repli
  sur la factorisation directe de SymPy, annoncée comme telle.
- **Une carte par application de méthode** (validé, T21, 25.10.2026) : « Étape k » avec la méthode en badge, les étapes de
  cette application (chaque phrase écrit déjà l'expression traitée et l'expression obtenue), dans l'ordre du calcul ; des
  applications consécutives de la même méthode (x² − 4 puis x² − 9, deux différences de carrés) sont dans une même carte, et
  une étape sans méthode propre (un facteur dont on a justifié qu'il ne se factorise pas) suit la carte précédente. La dernière carte
  « Factorisation » (badge = toutes les méthodes) donne l'expression et la factorisation complète.
- Exercices au hasard générés en Python, 4 niveaux (gabarits ci-dessous, acceptés le 14.10.2026, Q4).

## Gabarits (acceptés le 14.10.2026, Q4)

Règles : pondérations 35 % / 35 % / 20 % / 10 % ; paramètres entiers petits ; **racines
distinctes, toutes exactes** (racines irrationnelles écrites avec √, jamais approchées).
Le carré parfait (niveau difficile) a une racine double par construction : **à valider (Q8)** ;
d'ici là, le gabarit est conservé tel quel.

| Niveau | Gabarit | Exemple |
|---|---|---|
| facile | x² + bx + c, deux racines entières distinctes non nulles dans [−9 ; 9] | x² + 5x − 14 |
| moyen | (p₁x + q₁)(p₂x + q₂) développé, p ∈ [1 ; 4], q ∈ [−7 ; 7]\{0}, a ≠ 1 | 6x² − 7x − 3 |
| difficile | carré parfait (px + q)² ; ou différence de carrés a²x² − c² ; ou trinôme à Δ > 0 non carré | 9x² + 24x + 16 ; x² + 4x + 2 |
| très difficile | trinôme à Δ < 0 (non factorisable) ; ou cubique à trois racines entières ; ou (x − r)(x² + bx + c) avec Δ < 0 ; coefficient commun 1 ou 2 | x³ − 2x² − 5x + 6 |

Absents aujourd'hui des exercices (mais traités en saisie) : plusieurs lettres, cubes, groupements,
changement de variable, mise en évidence composée.

## Critères d'acceptation

| Id | Critère | Vérif. |
|---|---|---|
| FA-01 | Pour toute entrée de la batterie (exercices Amaudruz 2.11–2.16, Javet §2.2, exemples de la page, 500 exercices générés), le résultat redéveloppé = l'entrée et `secours` est faux | [auto-py] |
| FA-02 | Chaque facteur du résultat est irréductible sur ℚ (sur ℝ pour un trinôme seul à Δ > 0) | [auto-py] |
| FA-03 | `exercice(niveau, graine)` est déterministe et produit l'un des gabarits validés du niveau | [auto-py] |
| FA-04 | Une carte par application de méthode : nombre de cartes = nombre de suites consécutives de même méthode + 1 (bilan) ; deux cartes voisines n'ont jamais la même méthode ; aucune étape perdue ni déplacée ; exemple x⁴ − 13x² + 36 : Changement de variable, Somme-Produit, Changement de variable, Différence de carrés, bilan | [auto-py] (`test_resoudre_fa.py`) + [auto-page] |
| FA-05 | `(x+1)^2-(x-1)^2` : méthode « Différence de carrés », rédigée [(x + 1) − (x − 1)] · [(x + 1) + (x − 1)] = 2 · 2x = 4x (A et B sont des sommes : on écrit les crochets tels quels, puis on réduit), pas « Déjà factorisé » ; de même (x+3)² − (x−1)² = 4 · (2x + 2) = 8(x + 1) (et non « degré 1 : rien à factoriser ») | [auto-py] |
| FA-09 | Le zéro évident ne teste que les diviseurs entiers du terme constant (degré ≥ 3) ; un trinôme a ≠ 1 passe par le discriminant | [auto-py] |
| FA-10 | Zéros rationnels p₁/q₁ et p₂/q₂ (discriminant) : après « a(x − p₁/q₁)(x − p₂/q₂) », le coefficient se découpe en q₁·q₂ (c = a/(q₁q₂) = 1 par le lemme de Gauss, coefficients premiers entre eux) : ex. 6(x + 1/3)(x − 3/2) = 3(x + 1/3) · 2(x − 3/2) = (3x + 1)(2x − 3) ; zéros irrationnels : on garde a(x − x₁)(x − x₂) | [auto-py] |
| FA-11 | Jamais « ne se factorise pas davantage » ni « forme la plus simple » : une conclusion « on garde tel quel » est justifiée (Δ < 0 au degré 2 ; sinon « On peut montrer que … n'a pas de facteur à coefficients rationnels »). Degré ≥ 3 sans racine entière : on écrit les valeurs P(±d) pour les diviseurs d du terme constant (x³ − 2 : P(1) = −1, P(−1) = −3, P(2) = 6, P(−2) = −10), « Aucun diviseur entier du terme constant n'annule P : la recherche d'une racine entière ne permet pas de conclure », puis « On peut montrer que … » (irréductible) ou « … se factorise quand même : » + résultat + « Vérification : en développant, on retrouve … » avec le développement (30x³ − 19x² + 1 = (2x − 1)(3x − 1)(5x + 1)). Plusieurs lettres : « Aucune méthode du cours ne s'applique (…) : on ne peut pas conclure avec ces méthodes. » Badge « Aucune méthode du cours ». Jamais « SymPy » ni « calcul exact » dans le texte de l'élève | [auto-py] |
| FA-06 | Saisie d'une fonction (ln, sqrt…) ou division par une lettre : message en français | [auto-py] |
| FA-07 | Aucun calcul de la batterie FA-01 ne dépasse 2 s en natif (≈ 10 s dans Pyodide) | [auto-py] |
| FA-08 | `resoudre()` (T12) respecte le schéma de sortie commun pour toute la batterie FA-01 : une carte finale (badge = méthode), aucun texte perdu, erreurs en français ; instantanés `instantanes/resoudre/factorisation.json` | [auto-py] (`test_resoudre_fa.py`) |
