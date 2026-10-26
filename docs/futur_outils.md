# Futurs outils à implémenter

Propositions établies le 17.10.2026 à partir du chapitre Mathématiques de la brochure du plan d'études
(pp. 76-94 : niveau standard, niveau renforcé, cours d'appui 3C→2M,
applications des mathématiques).

**Statut : liste de propositions, rien n'est spécifié ni décidé.** Aucun de ces outils n'a de
spécification dans `specifications/` ni de tâche dans [taches.md](taches.md). Avant d'en
commencer un : le choisir, rédiger sa spécification (critères d'acceptation avec identifiants et
mode de vérification, voir le [README](README.md)), puis le découper en tâches.

Outils déjà en place : factorisation (1re), programmation linéaire (2e), ensemble de définition,
dérivée-variations, limites-asymptotes, étude complète (3e).

Ordre de réalisation conseillé : **1, 4, 6, 8, 9**, puis **13 et 14**, puis **20**. Le placement
exact (dépendances, briques communes, vagues N01 à N26) est dans [taches.md](taches.md), phase F ;
l'ordre y diffère légèrement de cette liste, parce que certains outils en supposent d'autres
(par exemple 9 a besoin de la résolution d'équations de 1).

## Priorité haute : proches de l'existant (moteur SymPy, étapes rédigées)

| # | Outil | Année / niveau | Référence au plan d'études |
|---|---|---|---|
| 1 | **Équations et inéquations** : degré 1 ou 2, ramenées au 2e degré, rationnelles, avec tableau de signes | 1re Ms/Mr | « résolution d'équations se ramenant au premier ou au deuxième degré » ; « signe de fonctions polynomiales et rationnelles ; inéquations » |
| 2 | **Division euclidienne de polynômes** (et Horner) | 1re Ms/Mr | « factorisation par division euclidienne » ; réutilisable pour les asymptotes obliques et les primitives de 3e |
| 3 | **Systèmes d'équations** : linéaires à 2 ou 3 inconnues, puis un système linéaire/quadratique | 1re Ms/Mr | « systèmes à une, deux ou trois inconnues et de deux équations de degré ≤ 2 » |
| 4 | **Équations et fonctions trigonométriques** : équations du 1er et du 2e degré en sin, cos, tan, avec cercle trigonométrique | 1re (Mr), 2e (Ms et Mr) | « équations trigonométriques du premier et du second degré » ; « étude de fonctions du premier degré en sin, cos, tan » |
| 5 | **Équations exponentielles et logarithmiques** | 2e Ms/Mr | « résolution d'équations exponentielles et logarithmiques » |
| 6 | **Tangente en un point** (équation, et tangente passant par un point extérieur) | 2e Ms/Mr | « équation de la tangente au graphe d'une fonction » |
| 7 | **Optimisation** : modéliser, dériver, justifier le max/min | 2e Ms/Mr | « résolution de problèmes d'optimisation » |
| 8 | **Primitives et intégrale définie** : polynômes, puissances, exp, sin, cos, composée linéaire, division euclidienne puis ln | 3e Ms/Mr | bloc « Analyse » de 3e |
| 9 | **Aire entre courbes et volume de révolution** | 3e Ms/Mr | « aire d'un domaine borné compris entre des courbes ; volume autour de l'axe horizontal » |

L'outil 4 comble le manque de trigonométrie. Les outils 8 et 9 complètent la chaîne
dérivée → étude → intégrale.

## Priorité moyenne : géométrie, probabilités, statistique

| # | Outil | Année / niveau | Référence |
|---|---|---|---|
| 10 | **Droites du plan** : équations paramétrique et cartésienne, distance point-droite, angle, parallèle/perpendiculaire, médiatrice, bissectrices | 2e Ms/Mr | bloc « Géométrie » de 2e |
| 11 | **Vecteurs** : norme, produit scalaire, angle, colinéarité ; produit vectoriel et mixte pour Mr | 1re (+ cours d'appui 3C→2M) | « Géométrie » de 1re |
| 12 | **Cercle et tangentes** : position relative droite/cercle, tangentes issues d'un point | 3e Ms/Mr | « équation de droites passant par un point et tangentes à un cercle » |
| 13 | **Dénombrement** : arrangements, permutations, combinaisons, avec formule justifiée | 3e Ms/Mr | « Analyse combinatoire » |
| 14 | **Probabilités** : arbre, probabilité conditionnelle, processus binomial | 3e Ms/Mr | « Probabilités » |
| 15 | **Statistique descriptive** : fréquences, moyenne, médiane, variance, écart type | 1re Ms/Mr | « Statistique descriptive » |
| 16 | **Trigonométrie du triangle** : théorèmes du sinus, du cosinus et de l'aire | 1re Ms/Mr | « résolution de triangles » |

## Réservé au niveau renforcé (Mr)

| # | Outil | Année | Référence |
|---|---|---|---|
| 17 | **Nombres complexes** : forme algébrique et trigonométrique, Moivre, équations | 2e Mr | « Nombres complexes » |
| 18 | **Suites et limites** : convergence, récurrence | 2e Mr | « suites de nombres réels, limite et convergence » |
| 19 | **Convexité et points d'inflexion**, à ajouter à l'outil « Étude complète » | 2e Mr | « étude de la croissance et de la courbure » |
| 20 | **Algèbre linéaire** : matrices, déterminants, systèmes (Gauss), valeurs propres, diagonalisation | 3e Mr | bloc « Algèbre linéaire » (une grande partie de l'année) |
| 21 | **Géométrie dans l'espace** : droites et plans, distances, projections ; sphères et plans tangents | 2e et 3e Mr | « dans l'espace » |
| 22 | **Intégration avancée** : par parties, changement de variable, éléments simples | 3e Mr | « intégration par parties, changement de variable… » |

## Option : applications des mathématiques

| # | Outil | Référence |
|---|---|---|
| 23 | **Résolution approchée d'équations** : dichotomie, Newton, avec l'erreur affichée | « garantir la qualité d'une estimation en analysant les sources d'erreurs » ; méthodes numériques |
| 24 | **Simulateur de modèles** : croissance exponentielle ou logistique, suites récurrentes | « exprimer des processus dynamiques et utiliser des simulations » ; modélisation |
| 25 | **Projections** : axonométrie et perspective (tracé interactif, plus lourd) | méthodes géométriques |
