# Questions à valider

Tant qu'une question est ouverte, **le comportement actuel est conservé** et les tâches qui en
dépendent sont bloquées (voir [taches.md](taches.md)).

## Q1 — « Croissance comparée » dans l'outil Limites

**Rappel.** Les croissances comparées sont les limites de référence qui lèvent les formes
indéterminées entre puissances, exponentielle et logarithme :

- en +∞ : e^x / x^n → +∞ et x^n · e^(−x) → 0 (« l'exponentielle l'emporte sur toute puissance ») ;
- en −∞ : x^n · e^x → 0 ;
- en +∞ : ln(x) / x^n → 0 (n > 0) (« toute puissance l'emporte sur le logarithme ») ;
- en 0⁺ : x^n · ln(x) → 0 (n > 0).

On ne les invoque que face à une **forme indéterminée** (∞/∞ ou 0·∞) entre ces deux familles.

**Aujourd'hui** (`limites_asymptotes.py:362-374`) : la phrase « par croissance comparée,
l'exponentielle domine » apparaît dès que f est un produit d'une exponentielle et d'autre chose,
y compris sans forme indéterminée (x·e^x en +∞ : ∞·∞ ; e^x/x en 0), et jamais pour ln.

**Proposition.** Ne citer la croissance comparée que si : (a) la limite est en ±∞, ou en 0⁺ pour
ln ; (b) il y a une forme indéterminée entre une puissance de x et e^(…) ou ln ; (c) la phrase nomme
la limite de référence utilisée (par ex. « x² e^(−x) → 0 en +∞ par croissance comparée »).

**À décider :** la proposition convient-elle ? Faut-il couvrir aussi ln ?

## ~~Q2 — Simplexe~~ (tranchée le 13.10.2026)

- **2C : méthode graphique ; 2Mr (OS) : méthode algébrique ; 2Ms : pas d'outil de programmation linéaire.**
- **Exercices au hasard : oui** (gabarits à valider, voir Q4).

Voir [specifications/simplexe.md](specifications/simplexe.md).

## Q3 — Notation dans le tableau quand f est définie mais pas f'

Validé : l'ED de f' est calculé et affiché quand il diffère de celui de f.
Ouvert : en un tel point (±2 pour √(x²−4), 0 pour √(x²)), que montrer ?
- ligne f'(x) : double barre (f' non définie) — proposition ;
- ligne f(x) : pas de double barre (f est définie) ; point d'extremum si f' change de signe.
D'ici la décision, l'affichage actuel (double barre sur les deux lignes) est conservé, mais
l'extremum mathématique sera annoncé dans la liste des extrema (bug 4).

## Q4 — Gabarits et niveaux des exercices au hasard

Validé : génération en Python avec graine, niveaux conservés, chaque exercice résolu exactement
dans les tests. **À valider : les gabarits.** Propositions dérivées des listes actuelles :

| Outil | facile | moyen | difficile | très difficile |
|---|---|---|---|---|
| Ensemble de définition | ln(ax+b) ; ln(x²−k²) ; 1/(e^x−k) ; ln(x−a)+ln(x−b) | 1/ln(x+a) ; ln(x)/(ln(x)+k) ; ln((x−a)/(x−b)) ; √(trinôme à racines entières) ; e^(1/trinôme) | k·ln(x)/((ln x)²−1) ; ln(trinôme)/(x−c) ; 1/(e^(2x)−s·e^x+p) | √(x·ln(x+a)+x) ; 1/(ln(x−a)+ln(x−b)) |
| Dérivée | trinôme ; x³−3k²x ; e^(ax) | x⁴−2k²x² ; x·ln(x) ; ln(x)/x ; √(trinôme à Δ<0) | (x²−a²)/(x−c) ; x/(x²+k) ; ln(x²−k²) | x²·e^(−x) |
| Limites | 1/(x−a) ; e^(ax) ; ln(x) | (x²−a²)/(x−c) ; ln(x−a) ; 1/x² | x²/(x−a) ; √(trinôme) ; x²·e^(−x) | ln(x²−ax)/(x−c) |
| Étude complète | comme Dérivée, facile | x⁴−2k²x² ; x·ln(x) ; ln(x)/x | (x²−a²)/(x−c) ; x/(x²+k) | x²·e^(−x) |
| Factorisation | voir [specifications/factorisation.md](specifications/factorisation.md) |
| Simplexe — graphique (2C) | 2 contraintes ≤, maximiser, sommets entiers | 3 contraintes dont une ≥, sommets entiers ou demi-entiers | minimiser avec contraintes ≥ ; coefficient de y négatif dans f | région non bornée ou infinité de solutions (côté parallèle aux droites f = c) |
| Simplexe — algébrique (2Mr/OS) | 2 variables, 2 contraintes ≤ (b ≥ 0), 1 à 2 pivots | 2 variables, 3 contraintes, 2 pivots | 3 variables, 3 contraintes ≤ | 3 variables, 4 contraintes, 3 pivots ou plus ; minimisation |

Paramètres (a, b, c, k, s, p) entiers petits, choisis pour que toutes les racines et bornes
soient exactes. Les pondérations actuelles (35 % / 35 % / 20 % / 10 %) sont conservées sauf avis
contraire.

## Q5 — Séparateur de milliers

Apostrophe ’ dès 4 chiffres (1’000, comme le simplexe aujourd'hui) ou dès 5 chiffres (10’000) ?

## Q6 — x⁰ en x = 0

Aujourd'hui `x^0` a pour ED ℝ (0⁰ traité comme 1). Convention du cours : ℝ ou ℝ\{0} ?

## Q7 — Vocabulaire des discontinuités

Les outils écrivent « point de discontinuité (pas une asymptote) » quand la limite est finie.
La correction `70e6b1e` ajoute « saut » (limites latérales finies et différentes, ex. x/√(x²) en 0).
Ces deux formulations conviennent-elles au cours ?
