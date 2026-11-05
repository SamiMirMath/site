# Chantier explog-q4-q6 (PC, 05.11.2026)

Branche `explog-q4-q6`, depuis `main` à jour (a4884b0, fusion d'explog-suite). Une seule session, sans sous-agent.
Origine : questions Q4 et Q6 de `docs/chantiers/explog-suite/suivi.md`. Détail : `journal.md`.

## État

| Question | Objet | État |
|---|---|---|
| Q6 | Méthode « Même base / définition » : jamais « Il faut les logarithmes. » quand les bases sont les mêmes | ✓ commité, suite verte |
| Q4 | k·log(a)/log(a) se simplifie en k dans l'ensemble solution (S = {0 ; 5}) | à faire |

## Q6

- **Causes** (toutes dans `exponentielles-logarithmes/exp_log.py`) :
  1. `_isoler` refuse un membre constant irrationnel (2^(−1/2)) ; `_meme_base` l'appelait même pour a^A = b^B, où il n'y a rien à isoler ;
  2. `_resoudre_polynome` refuse un trinôme à coefficients non entiers (x² − 5x + 1/2 = 0) : la méthode A tombait alors sur le message
     de repli « Il faut les logarithmes. » ; la méthode B, elle, résout ce trinôme (`_suite_polynome`) ;
  3. `_facteur` : un membre constant (1/2)^(−1/2) (base rationnelle écrite en quotient, valeur irrationnelle) n'était pas reconnu comme
     une puissance : les deux méthodes répondaient « pas encore ».
- **Corrections** :
  1. `_meme_base` : `_isoler` n'est plus appelé quand les deux membres sont des puissances ;
  2. `_resoudre_polynome_rationnel` (nouvelle) : `_resoudre_polynome`, et pour un trinôme à coefficients non entiers la suite de la méthode B
     (même rédaction : x² − 5x = −1/2 ⇔ x² − 5x + 1/2 = 0, Δ = (−5)² − 4·1·1/2 = 23, x₁, x₂). Utilisée par la méthode A (`_meme_base`,
     `_meme_base_e`) et par la méthode B quand log(10) = 1 ou ln(e) = 1 a rendu le trinôme numérique (e^(x²) = e^(x + 1/2), « pas encore » avant) ;
  3. `_facteur` : la même lecture que pour le membre de l'inconnue (base rationnelle), seulement là où `_Hors` était levé.
- **Entrées touchées** (balayage, 387 voisines × 2 filières, voir `journal.md`) : avant, 274 en C et 274 en M affichaient
  « Il faut les logarithmes. », et 43 par filière « pas encore » ; après, aucune des deux. Corpus : **aucune entrée touchée**,
  aucun instantané ni aucune référence de page modifiés.
- Filière M : même moteur (`variantes_equation`), mêmes sorties.
- **Test** : `tests/python/test_explog_q4_q6.py` (rédaction de 15 cas, oracle : racines exactes, aucune autre racine, solutions de l'outil ;
  balayage : jamais le message, solutions de A = solutions de B, chacune annule g − d). Sur le moteur d'avant : 656 échecs (sous-tests).

## À relire par l'enseignant

- Aucun instantané modifié par Q6.
- Rédaction nouvelle, à juger à l'écran : `2^(x^2-5x)=2^(-1/2)`, méthode « Même base » (identique à la méthode B après l'égalité des exposants).
- Écriture mêlée fraction / décimal (R13, comportement existant de la suite B et de la réécriture des bases, non changé) :
  `0,5^(x^2-x)=0,5^(-1/4)` : « −x² + x = 1/4 ⇔ −x² + x − 0,25 = 0 » ; `(1/2)^(x^2-x)=(1/2)^(0,5)` : « = 2^(−1/2) », « −x² + x + 0,5 = 0 ».
- a < 0 : x₁ = (−5 + √23)/(−2) (question Q7, non traitée).

## Écarts

## Reprise après compactage

- Branche `explog-q4-q6` ; un commit par question (Q6, puis Q4) ; suite d'avant commit :
  `PROCESSUS_PAGES=4 python3 tests/lancer.py complet --rapport <scratchpad>/q<N>` puis `verifier`.
- Fichiers non suivis de l'enseignant (`docs/architecture.md`, `docs/chantiers/equations-2e-degre/quiz.md`, `docs/chantiers/revue-structure/`) :
  ne pas y toucher ; un refus de `verifier` pour ce seul motif vaut accepté ; de même une variation des sous-tests de vocabulaire liée
  à un texte retiré du code (consigne du 05.11). Tout autre refus : pousser la branche seule.
