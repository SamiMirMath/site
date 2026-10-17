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
  3. trinôme : Somme-Produit (a = 1), zéro évident (a ≠ 1), formule du discriminant ;
  4. changement de variable u = x^n ;
  5. groupements ;
  6. zéro évident et division (degré ≥ 3) ; compléter le carré en dernier recours.
- Contrôle final : le produit affiché, redéveloppé, redonne exactement l'expression ; sinon repli
  sur la factorisation directe de SymPy, annoncée comme telle.
- **Une carte par méthode appliquée** (validé, après les corrections et les tests) : chaque carte
  porte le nom de la méthode en badge, l'expression traitée, les étapes, l'expression obtenue ;
  la dernière carte donne la factorisation complète.
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
| FA-04 | Une carte par méthode appliquée ; le nombre de cartes = nombre de méthodes listées dans le badge + 1 (bilan) | [auto-py] + [auto-page] |
| FA-05 | `(x+1)^2-(x-1)^2` : la méthode annoncée n'est pas « Déjà factorisé » | [auto-py] |
| FA-06 | Saisie d'une fonction (ln, sqrt…) ou division par une lettre : message en français | [auto-py] |
| FA-07 | Aucun calcul de la batterie FA-01 ne dépasse 2 s en natif (≈ 10 s dans Pyodide) | [auto-py] |
| FA-08 | `resoudre()` (T12) respecte le schéma de sortie commun pour toute la batterie FA-01 : une carte finale (badge = méthode), aucun texte perdu, erreurs en français ; instantanés `instantanes/resoudre/factorisation.json` | [auto-py] (`test_resoudre_fa.py`) |
