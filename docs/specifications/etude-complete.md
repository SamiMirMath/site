# Outil « Étude complète de fonction » (3e Ms, Mr)

URL : `/etude-complete/` · moteur : `etude-complete/etude_complete.py`, qui assemble le noyau,
la dérivée et les limites (aucun calcul mathématique nouveau).

## Fonctionnel

- Enchaîne : ED → dérivée, signe, variations, extrema → limites et asymptotes → graphique.
- **Graphique** : cadrage automatique (bornes de l'ED, extrema, asymptotes horizontales) ;
  courbe tracée par morceaux de l'ED ; asymptotes en pointillé ; extrema en points pleins ;
  trous (limite finie en une valeur interdite) en ronds vides ; zoom (boutons, molette, pincement), déplacement
  (glisser) ; rééchantillonnage de la fenêtre visible.
- Les résultats des trois étapes sont exactement ceux des outils séparés.

## Conventions

- Celles des outils séparés. Limite finie ℓ en une valeur interdite a : rond vide en (a ; ℓ)
  (« trou dans le graphique », Q7) ; limites latérales finies et différentes : rien n'est dessiné
  comme une asymptote (comportement actuel du graphique).
- Graduations du graphique en notation suisse (virgule décimale).

## Tableau de variations avec limites (T06c) — validée le 16.10.2026

Décidé le 14.10.2026 (limites contre les doubles barres), précisé le 16.10.2026 (limites aussi en ±∞
quand l'ED y va). **Étude complète seulement** : le tableau de l'outil Dérivée garde les flèches seules.

### Règles

- **Où** : ligne f(x) du tableau de variations de l'Étude complète, et nulle part ailleurs. Les lignes
  de signe (facteurs, f'(x)) ne changent pas.
- **Contre une double barre** (valeur interdite de f, y compris borne ouverte de l'ED comme ln x en 0) :
  la limite à gauche s'écrit à gauche de la barre, la limite à droite à droite. **Seul le côté de l'ED
  porte une valeur** : à côté d'une zone hachurée, rien (ln(x²−4) : −∞ à gauche de la colonne −2,
  zone hachurée à droite ; l'inverse en 2).
- **En ±∞** : si l'ED atteint −∞ (resp. +∞), la limite s'écrit sous l'en-tête −∞ (resp. +∞), au bout de
  la première (resp. dernière) flèche. Les autres lignes restent vides à cet endroit.
- **Inchangé** : la valeur f(a) sans barre en un point de l'ED où f' n'est pas définie ou en une borne
  fermée (T06) ; une borne finie fermée de l'ED n'a jamais de limite (on y a f(a)).
- **Notation** : la valeur seule, exacte (−∞, +∞, 0, 2, ln 2, √2), sans « lim » ni « x → a » : la flèche
  adjacente dit déjà de quel côté on vient. Limites latérales finies égales = trou : la même valeur des
  deux côtés de la barre, sans autre marque (le trou est dit par la partie Limites et dessiné sur le
  graphique).
- **Une seule source** : les valeurs viennent de la même fonction de calcul que la partie Limites et
  asymptotes, jamais d'un second calcul indépendant (EC-01 : aucun calcul mathématique nouveau). Une limite que SymPy ne détermine pas : « ? » à sa place, et une
  seule ligne sous le tableau, « Limite non déterminée automatiquement en a⁻. » (resp. a⁺, +∞, −∞).
- **Aucune ligne de justification ajoutée** (guide de rédaction R1, R5) : le tableau est le résumé de
  ce qui est calculé plus haut.
- **Double barre sur toutes les lignes** de la colonne d'une valeur interdite, y compris f'(x) quand
  elle n'a aucune ligne de facteur, **trou compris** (cas C : le moteur écrivait « + + + » au lieu de
  « + ‖ + » ; corrigé avec T06c, **y compris dans l'outil Dérivée**, qui garde pour le reste ses
  flèches seules).
- **Présentation** (validée) : une seule ligne de texte par ligne de tableau, les valeurs ne sont pas
  décalées en hauteur selon la flèche (tableau classique papier), pour tenir à 380 px.

### Exemples (validés)

**A. Pôle simple, limites de signes opposés : f(x) = 1/(x − 2)**

```
f'(x) = −1/(x − 2)² : ne s'annule jamais ; valeur interdite : x = 2.

x        | −∞          2          +∞
−1       |      −      ‖      −
(x − 2)² |      +      ‖      +
f'(x)    |      −      ‖      −
f(x)     | 0    ↘   −∞ ‖ +∞   ↘    0
```

**B. Pôle, limites de même signe : f(x) = 1/(x − 2)²**

```
f'(x) = −2/(x − 2)³ : ne s'annule jamais ; valeur interdite : x = 2.

x        | −∞          2          +∞
−2       |      −      ‖      −
(x − 2)³ |      −      ‖      +
f'(x)    |      +      ‖      −
f(x)     | 0    ↗   +∞ ‖ +∞   ↘    0
```

**C. Trou : f(x) = (x² − 1)/(x − 1)**

```
f'(x) = 1 : ne s'annule jamais ; valeur interdite : x = 1.

x        | −∞          1          +∞
f'(x)    |      +      ‖      +
f(x)     | −∞   ↗    2 ‖ 2    ↗   +∞
```

**Bord d'une zone hachurée (rappel des règles) : f(x) = ln(x² − 4)**, ligne f(x) seulement :

```
x        | −∞      −2           2       +∞
f(x)     | +∞  ↘  −∞ ‖  ░░░░░░  ‖ −∞  ↗  +∞
```

### Critères d'acceptation (T06c)

| Id | Critère | Vérif. |
|---|---|---|
| EC-08 | Ligne f(x) de A : 0, ↘, −∞ ‖ +∞, ↘, 0 ; de B : 0, ↗, +∞ ‖ +∞, ↘, 0 ; de C : −∞, ↗, 2 ‖ 2, ↗, +∞ | [auto-py] (JSON de l'Étude complète) |
| EC-09 | ln(x²−4) : −∞ à gauche de la colonne −2 et à droite de la colonne 2, aucune valeur dans la zone hachurée ; ln x : −∞ à droite de la colonne 0, +∞ en +∞ ; √x : f(0) = 0, pas de limite en 0 | [auto-py] |
| EC-10 | Sur le corpus (liste DV-01 et exemples), chaque valeur écrite contre une barre ou en ±∞ est égale à la limite correspondante de la partie Limites quand celle-ci la donne ; sinon « ? » et la phrase | [auto-py] (propriété) |
| EC-11 | La double barre est sur toutes les lignes de la colonne interdite, f'(x) comprise (C) | [auto-py] |
| EC-12 | Les sorties de l'outil Dérivée sont identiques à avant T06c, sauf la double barre sur f'(x) à toute valeur interdite (instantanés relus un par un) | [auto-py] |
| EC-13 | Rendu à 360 px **sans défilement horizontal** pour les tableaux à 1 ou 2 valeurs critiques (A, B, C, ln(x²−4)) ; plus larges : défilement avec la 1re colonne (libellés) fixe ; double barre continue ; même feuille `tableaux.css` pour les quatre outils ; valeurs jamais sous 0,85 em, aucune information supprimée | [manuel] (captures 360 et 900 px, 16.10.2026) ; feuille commune [auto-py] (`test_tableaux_css.py`) |

## Critères d'acceptation

| Id | Critère | Vérif. |
|---|---|---|
| EC-01 | Pour chaque exemple, les parties dérivée et limites sont identiques aux sorties des outils séparés | [auto-py] |
| EC-02 | L'ED n'est calculé qu'une fois par étude, et `fenetre()` ne recalcule pas l'ED (mise en cache par entrée) | [auto-py] (compteur d'appels) |
| EC-03 | `fenetre("e^x", -10, 800)`, `fenetre("e^(-x)", -1000, 10)`, `fenetre("x^2*e^(-x)", -2000, 2000)` réussissent ; les points non calculables sont omis | [auto-py] |
| EC-04 | En cas d'échec de `fenetre`, la courbe affichée reste celle de la dernière fenêtre réussie et un message discret l'indique | [auto-page] |
| EC-05 | Sur téléphone, un glissement vertical à un doigt sur le graphique fait défiler la page ; deux doigts zooment et déplacent | [manuel] |
| EC-06 | Graduations sans point décimal | [auto-page] |
| EC-07 | Le graphique est imprimé (image) dans le PDF | [manuel] |
| EC-13 | `resoudre()` (T12) respecte le schéma de sortie commun, ses cartes sont dans l'ordre de la page, celles de la dérivée et des limites sont les cartes des outils séparés, les limites figurent dans le tableau de variations ; instantanés `instantanes/resoudre/etude-complete.json` | [auto-py] (`test_resoudre_ec.py`) |
