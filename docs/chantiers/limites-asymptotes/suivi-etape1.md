# Limites et asymptotes (3M) : suivi de l'étape 1 (urgente, 29.10.2026)

Demande : l'outil est utilisé le 30.10.2026 au matin par des élèves de 3M. Objectifs : rien de faux à l'écran ; la règle du podium n'est plus jamais une justification ; la page est cohérente avec le cours. Pas d'autre refonte de la rédaction.

## Fait (trois commits locaux, rien poussé)

| Commit | Contenu |
|---|---|
| `f6b130a` (points 1, 2, 3) | Bug 8.13e corrigé (+∞ aux deux pôles, asymptote verticale). Garde-fou générique sur tous les résultats SymPy (`_rejete`) + sonde mpmath dans le moteur = détecteur de contradiction (`_contradit_par_sonde`). Message « La fonction cos n'est pas encore prise en charge par cet outil. » (sin, cos, tan, cot, arc…, sinh…, log_a). |
| `879abd4` (point 5) | `_comparee_pure` et `_evidence_ln` retirées de `METHODES` ; BH jusqu'à 3 de suite, profondeur 8 ; 0·∞ en quotient (ln en haut, eᵘ → 1/e^(−u), xᵏ → 1/x^(−k), constante sortie) ; LA-07, LA-15, LA-31, LA-32, LA-34 réécrites, R19 du guide ; test « aucune rédaction ne contient croissance comparée, podium, limite de référence ». |
| `d675b96` (points 6 et 4) | Page : 9 exemples du corpus rédigés par BH sans repli ; encadré « Rappel de la méthode » = mode d'emploi en 7 points + phrase sur le podium ; second encadré « Rappel : les asymptotes » ; corpus + oracle mpmath (`tests/python/donnees/corpus_limites_3m.py`, `test_corpus_limites_3m.py`) ; test de page à 360 px. |

## Bornes en phrase de repli sur le corpus (mesure du 29.10.2026)

- **Avant** (état du dépôt au départ) : **16** bornes.
- **Après le point 5** : **13** bornes. Basculées vers une rédaction complète : 8.12e (−∞, 3 BH), Ex5c (−∞), 3.8g (+∞). Aucune borne n'est tombée en repli à cause de la sonde ou de la doctrine ; 8.13e était déjà en repli (sa valeur est maintenant juste).
- Liste des 13 et raison technique :
  1. Ex5b `x·e^(1/x)` en −∞ et +∞ : asymptote oblique, `b = lim (f − x)` (∞ − ∞ non levée) ; la limite elle-même est rédigée.
  2. Fd (même fonction) en −∞ et +∞ : idem.
  3. Fc `x·e^x/(1−e^x)` en +∞ : asymptote oblique, même raison.
  4. 8.12f `e^(1/x)/x²` en 0⁻ : 0/0 non levée.
  5. 8.12h `e^(−1/x)/x` en 0⁻ : 0/0 non levée (« BH tourne en rond »).
  6. 8.13e `ln((3x²−3x+2)/(x²−5x+2))` aux deux pôles irrationnels : signe du dénominateur inconnu (valeur +∞ juste).
  7. 3.8g `ln(x²)/ln(x)²` en 0⁺ : ∞/∞ non levée.
  8. 3.8g′ `(8ˣ − 2ˣ)/(4x)` en −∞, +∞ et 0 : `aˣ` non rédigé (exposant non rationnel).
- Cliquet : `REPLIS_MAXIMUM = 13` dans `test_corpus_limites_3m.py` (il ne doit jamais monter).

## Choix pour la page (rédaction complète, sans repli, par BH)

8.11a `e^x/ln(x)`, 8.12a `ln(x)/e^(2x)`, 8.14 `ln(1+e^x)/e^x`, 3.8a `ln(x+1)/x`, 3.8c `(ln(x)−1)/(x−e)`, 3.8d `ln(x²−3)/(2−x)`, feuille a `(e^x−e^2)/(x−2)`, 3.11e `(ln(x)−2)/(ln(x)−1)`, 8.12e `x³e^(3x−5)` (trois BH). Écartés : 3.10e (rédigé, mais par mise en évidence, pas par BH) ; feuille c (repli en +∞) ; 3.8b, feuille b, 3.8h′ (fonction non prise en charge).
Temps dans Pyodide (page, SymPy précompilé) : de 0,9 s à 3,4 s par exemple (3.8d : 3,4 s, le plus long, comme avant).

## Ce qui reste (étapes 2 à 9 de la feuille de route de `audit-etape0.md`)

- Étape 2 (décision ouverte) : « BH partout » ? Aujourd'hui, fractions rationnelles : mise en évidence/factorisation (LA-15).
- Étape 5 du chantier : écrire 0⁺ / 0⁻ dans les résultats (test `test_signe_zero_plus_ou_moins_ecrit` marqué « échec attendu »).
- Étape 6 : prédiction du podium dans un encadré à part (+∞, −∞, signe, tableau de valeurs de 8.14).
- Étapes 3, 4, 7, 8, 9 : spécification 3M complète, table de dérivées maison, format « Étape n » numérotées, haut → dérivée / bas → dérivée, simplification à part, détection de « BH tourne en rond » (8.12h), e^(…) et ln(…) avec limite de l'exposant à part, `sin`/`cos`/`log_a`/`aˣ`, relecture à l'écran.
- Nettoyage : supprimer le code mort `_comparee_pure`, `_comparee_avec_polynomes`, `REFERENCES`, `_reference`, `_ligne_reference`, `_evidence_ln`.
- Rédaction à améliorer (hors périmètre ce soir) : les 0·∞ en cascade s'écrivent en blocs imbriqués (sous-limite d'abord), non en « BH (1re fois), (2e fois) » ; « −0 = 0 » ; l'hypothèse (d) n'est pas écrite.
- Un `3.10e` rédigé par mise en évidence et l'asymptote oblique de x·e^(1/x) (repli) à reprendre avec la décision de l'étape 2.
