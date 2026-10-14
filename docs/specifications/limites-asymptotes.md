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
  limite finie ⇒ point de discontinuité ; sinon signe de chaque côté (0⁺ / 0⁻) ⇒ asymptote
  verticale. Pôle irrationnel : sonde numérique + SymPy.
- **Cas transcendant** : valeur par SymPy, narration simple ; en ±∞ avec limite infinie, recherche
  d'asymptote oblique (a = lim f/x, b = lim f − ax).
- **Valeur interdite isolée, cas transcendant** (correction `70e6b1e`) : au moins une limite
  latérale infinie ⇒ asymptote verticale ; deux limites finies égales ⇒ point de discontinuité ;
  finies et différentes ⇒ **saut** ; limite non déterminée ⇒ aucune conclusion.
- Bilan des asymptotes en fin de corrigé.

## Conventions

- « Croissance comparée » : **à valider** (Q1). D'ici là, la phrase actuelle est conservée.
- Vocabulaire « point de discontinuité (pas une asymptote) » conservé.

## Critères d'acceptation

| Id | Critère | Vérif. |
|---|---|---|
| LA-01 | Aucune asymptote « verticale » n'est annoncée sans au moins une limite latérale infinie | [auto-py] (existe : `test_limites_deux_cotes.py`) |
| LA-02 | (e^x−1)/x et x·ln(x²) en 0 : point de discontinuité, valeurs 1 et 0 ; x/√(x²) en 0 : saut −1 / 1 | [auto-py] (existe) |
| LA-03 | Une limite non déterminée (« ? ») n'est jamais enregistrée comme asymptote, en ±∞ comme en un point | [auto-py] |
| LA-04 | Pour ≥ 40 fonctions, chaque limite annoncée est confirmée par une sonde numérique (x = ±10⁶, a ± 10⁻⁶) ou par `sympy.limit` indépendamment | [auto-py] |
| LA-05 | Fonctions rationnelles : asymptote oblique y = ax + b telle que f(x) − (ax + b) → 0 numériquement | [auto-py] |
| LA-06 | Sorties des exemples et exercices identiques aux instantanés | [auto-py] |
| LA-07 | (après décision Q1) la mention « croissance comparée » n'apparaît que dans les cas validés | [auto-py] |
