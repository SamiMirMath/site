# Outil « Limites et asymptotes » (3e Ms, Mr)

URL : `/limites-asymptotes/` · moteur : `limites-asymptotes/limites_asymptotes.py` (+ noyau).

## Fonctionnel

- Bornes étudiées, déduites de l'ED : ±∞ si l'ED n'est pas borné de ce côté ; chaque borne finie
  ouverte (côté utile seulement) ; valeur interdite isolée : à gauche et à droite.
- **f rationnelle, en ±∞** (exact, sans SymPy) : mise en évidence du terme de plus haut degré au
  numérateur et au dénominateur, chaque terme écrit explicitement ; deg N < deg D ⇒ y = 0 ;
  égalité ⇒ rapport des coefficients dominants ; deg N = deg D + 1 ⇒ division polynomiale et
  asymptote oblique ; écart ≥ 2 ⇒ branche parabolique.
- **f rationnelle, pôle fini** : factorisation par (x − a), simplification des facteurs communs ;
  limite finie ℓ ⇒ trou dans le graphique en (a ; ℓ) (formulation Q7 ci-dessous) ; sinon signe de
  chaque côté (0⁺ / 0⁻) ⇒ asymptote verticale. Pôle irrationnel : sonde numérique + SymPy.
- **Cas non rationnel (ln, exp, racines mélangés à x)** : valeur par SymPy (racine réelle pour
  x^(p/q), q impair), narration simple ; en ±∞ avec limite infinie, recherche
  d'asymptote oblique (a = lim f/x, b = lim f − ax).
- **Valeur interdite isolée, cas non rationnel** (correction `70e6b1e`) : au moins une limite
  latérale infinie ⇒ asymptote verticale ; deux limites finies égales ⇒ trou ; finies et
  différentes ⇒ pas de limite en a ; limite non déterminée ⇒ aucune conclusion
  (formulations Q7 ci-dessous ; le genre « saut » de `70e6b1e` est remplacé, tâche T08b).
- Bilan des asymptotes en fin de corrigé.

## Conventions

### Croissance comparée (tranché le 14.10.2026, Q1)

- Citée **uniquement** face à une forme indéterminée entre une puissance x^n (n > 0 réel) et une
  exponentielle e^(ax) (a > 0) ou un logarithme : ∞/∞, 0·∞, ou ∞ − ∞ levée par factorisation
  (e^x − x² = e^x(1 − x²/e^x) ; x − ln x = x(1 − ln(x)/x)).
- En ±∞, et en 0⁺ pour le logarithme.
- Limites de référence : en +∞, e^(ax)/x^n → +∞, x^n·e^(−ax) → 0, ln(x)/x^n → 0 ; en −∞,
  x^n·e^(ax) → 0 ; en 0⁺, x^n·ln(x) → 0.
- La phrase **nomme toujours la limite de référence utilisée**, par ex.
  « x²·e^(−x) → 0 en +∞ par croissance comparée (lim x^n e^(−x) = 0) ».
- Jamais ailleurs (x·e^x en +∞ : pas de forme indéterminée ; e^x/x en 0 : pas une croissance comparée).

### Limite finie en une valeur interdite (tranché le 14.10.2026, Q7)

Ne jamais écrire « point de discontinuité » quand a ∉ ED.
- Limites latérales finies et égales à ℓ : « f n'est pas définie en a, mais sa limite y est
  finie (= ℓ) : pas d'asymptote verticale, trou dans le graphique en (a ; ℓ) ».
- Limites latérales finies et différentes : « limites à gauche et à droite différentes : f n'a
  pas de limite en a ; pas d'asymptote verticale ».
- Valeur interdite au bord de l'ED (un seul côté), limite finie ℓ : même formulation que le
  premier cas, avec la limite latérale.

## Critères d'acceptation

| Id | Critère | Vérif. |
|---|---|---|
| LA-01 | Aucune asymptote « verticale » n'est annoncée sans au moins une limite latérale infinie | [auto-py] (existe : `test_limites_deux_cotes.py`) |
| LA-02 | (e^x−1)/x et x·ln(x²) en 0 : limite finie, trou en (0 ; 1) et (0 ; 0) ; x/√(x²) en 0 : limites −1 et 1, pas de limite en 0 ; jamais d'asymptote verticale | [auto-py] (existe : `test_limites_deux_cotes.py`, à adapter en T08b) |
| LA-03 | Une limite non déterminée (« ? ») n'est jamais enregistrée comme asymptote, en ±∞ comme en un point | [auto-py] |
| LA-04 | Pour ≥ 40 fonctions, chaque limite annoncée est confirmée par une sonde numérique (x = ±10⁶, a ± 10⁻⁶) ou par `sympy.limit` indépendamment | [auto-py] |
| LA-05 | Fonctions rationnelles : asymptote oblique y = ax + b telle que f(x) − (ax + b) → 0 numériquement | [auto-py] |
| LA-06 | Sorties des exemples et exercices identiques aux instantanés | [auto-py] |
| LA-07 | « croissance comparée » apparaît pour x²·e^(−x) (+∞), x^(1/2)·e^(−x) (+∞), ln(x)/x (+∞), x·ln(x) (0⁺), e^x − x² (+∞), x − ln(x) (+∞), x·e^x (−∞), avec la limite de référence nommée ; jamais pour x·e^x (+∞), e^x/x (0), e^(2x) (±∞) | [auto-py] |
| LA-09 | x^(2/3), x^(1/3), x^(-1/3), x^(4/3), (x−2)^(1/3), x·x^(1/3) : limites en −∞ et en un point négatif justes dans ℝ (racine réelle) ; aucun `Infinity` ni `NaN` dans une sortie (JSON strict) | [auto-py] (`test_racines_reelles.py`, `test_json_strict.py`) |
| LA-08 | Aucune sortie ne contient « point de discontinuité » ni le genre « saut » ; les deux formulations Q7 apparaissent mot pour mot pour (e^x−1)/x, (x²−1)/(x−1) et x/√(x²) en 0 ou 1 | [auto-py] |
