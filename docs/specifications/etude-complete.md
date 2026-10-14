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
