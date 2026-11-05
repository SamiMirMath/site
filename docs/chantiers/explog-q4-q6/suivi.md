# Chantier explog-q4-q6 (PC, 05.11.2026)

Branche `explog-q4-q6`, depuis `main` à jour (a4884b0, fusion d'explog-suite). Une seule session, sans sous-agent.
Origine : questions Q4 et Q6 de `docs/chantiers/explog-suite/suivi.md`. Détail : `journal.md`.

## État

| Question | Objet | État |
|---|---|---|
| Q6 | Méthode « Même base / définition » : jamais « Il faut les logarithmes. » quand les bases sont les mêmes | ✓ commité, suite verte |
| Q4 | k·log(a)/log(a) se simplifie en k dans l'ensemble solution (S = {0 ; 5}) | ✓ commité, suite verte |

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

## Q4

- **Avant** : méthode « Logarithmes », un quotient p·log(a)/(q·log(a)) restait écrit, avec un contrôle à la calculatrice :
  S = {0 ; 5log(2)/log(2)} (`2^(x^2-5x)=2^0`), x = log(2)/log(2), x² = log(2)/log(2) puis x₁ = −√(log(2)/log(2)), x = −b/(2a) = 2log(2)/(2log(2)),
  et au 1er degré x = 3log(2)/log(2) = log(8)/log(2) (regroupement), x = (log(4) − log(2))/(log(4) − log(2)) = log(2)/log(2).
- **Correction** (`exp_log.py`) : `_quotient_de_logs` donne k quand le numérateur et le dénominateur sont p·L et q·L avec le même logarithme L
  écrit à l'identique, ou sont écrits à l'identique. **Garde-fou** : la sonde à 60 chiffres (`_valeur_rationnelle`) doit donner le même k,
  sinon rien n'est simplifié. Appelée là où le quotient est écrit : `_alpha` (x² = log(2)/log(2) = 1, puis x = −1 ou x = 1),
  `_second_degre` (x en facteur ; Δ = 0), `_premier_degre` (avant le regroupement). La chaîne gagne « = k », la solution est le nombre k,
  le contrôle à la calculatrice disparaît (plus de logarithme à contrôler).
- **Non touché** (spécification, exemples 10 et 11) : log(32)/log(2), log(1/64)/log(2), log(9)/log(3) : logarithmes différents, écrits tels quels, avec le contrôle.
- **Test** : `test_explog_q4_q6.py`, classe `TestQ4QuotientDeLogs` (rédaction de 9 cas, oracle, solutions exactes, garde-fou, spécification
  inchangée, balayage du corpus C et M et des voisines de Q6).
- **Test modifié** (nouvelle rédaction attendue, rien d'affaibli) : `test_audit_el.py::TestRacineDouble::test_delta_nul_methode_b`.
  Avant : dernière ligne « x = −b/(2a) = 2log(2)/(2log(2)) », une solution, contrôle « … = 1 ». Après : « … = 2log(2)/(2log(2)) = 1 »,
  S = {1}, aucun contrôle.

## À relire par l'enseignant

- **Q4, instantanés modifiés** : `tests/python/instantanes/resoudre/exponentielles-logarithmes.json` (20 entrées) et `-M.json` (8),
  `tests/pages/references/exponentielles-logarithmes.json` (20) et `-M.json` (8) : les mêmes entrées. Ensemble solution de la méthode
  « Logarithmes » (lignes complètes avant / après : `journal.md`) :

| Entrée | Filières | S avant | S après |
|---|---|---|---|
| `25^x-6*5^x+5=0` | C, M | `S = \left\{0 \,;\, \frac{\log(5)}{\log(5)}\right\}` + contrôle | `S = \left\{0 \,;\, 1\right\}` |
| `2^(2t)-3*2^t=-2` | C, M | `S = \left\{0 \,;\, \frac{\log(2)}{\log(2)}\right\}` + contrôle | `S = \left\{0 \,;\, 1\right\}` |
| `2^(x+1)+2^(x-1)=10` | C | `S = \left\{1 + \frac{\log(2)}{\log(2)}\right\}` + contrôle | `S = \left\{2\right\}` |
| `2^(x^2)=2^(2x-1)` | C | `S = \left\{\frac{2\log(2)}{2\log(2)}\right\}` + contrôle | `S = \left\{1\right\}` |
| `2^x+2^(x-1)=6` | C | `S = \left\{1 + \frac{\log(2)}{\log(2)}\right\}` + contrôle | `S = \left\{2\right\}` |
| `2^x+3^x=2^(x+1)+3^(x-1)` | C | `S = \left\{1\right\}` | `S = \left\{1\right\}` |
| `2^x-2^(2x-3)=0` | C | `S = \left\{\frac{\log(8)}{\log(2)}\right\}` + contrôle | `S = \left\{3\right\}` |
| `2^x/3+2^(x+1)/3=2` | C | `S = \left\{\frac{\log(2)}{\log(2)}\right\}` + contrôle | `S = \left\{1\right\}` |
| `2^x=2*4^(x-1)` | C | `S = \left\{1\right\}` | `S = \left\{1\right\}` |
| `3(2^x+1)=9` | C | `S = \left\{\frac{\log(2)}{\log(2)}\right\}` + contrôle | `S = \left\{1\right\}` |
| `3^x+3^(x+2)=30` | C | `S = \left\{\frac{\log(3)}{\log(3)}\right\}` + contrôle | `S = \left\{1\right\}` |
| `4*2^(-3x)-5*2^(-x)+2^x=0` | C, M | `S = \left\{0 \,;\, \frac{\log(2)}{\log(2)}\right\}` + contrôle | `S = \left\{0 \,;\, 1\right\}` |
| `4^x+4^(x+1)=20` | C | `S = \left\{\frac{\log(4)}{\log(4)}\right\}` + contrôle | `S = \left\{1\right\}` |
| `5*2^(x^2)-3=7` | C | `S = \left\{x_{1} \,;\, x_{2}\right\}` + contrôle | `S = \left\{-1 \,;\, 1\right\}` |
| `5^(3x)-26*5^x+25*5^(-x)=0` | C, M | `S = \left\{0 \,;\, \frac{\log(5)}{\log(5)}\right\}` + contrôle | `S = \left\{0 \,;\, 1\right\}` |
| `5^(3x+2)=(5^x)^2` | C | `S = \left\{\frac{\log(25)}{\log\left(\frac{1}{5}\right)}\right\}` + contrôle | `S = \left\{-2\right\}` |
| `5^x+5^(x+1)+5^(x+2)=155` | C | `S = \left\{\frac{\log(5)}{\log(5)}\right\}` + contrôle | `S = \left\{1\right\}` |
| `9*3^(-3x)-10*3^(-x)+3^x=0` | C, M | `S = \left\{0 \,;\, \frac{\log(3)}{\log(3)}\right\}` + contrôle | `S = \left\{0 \,;\, 1\right\}` |
| `9^x-3^x=6` | C | `S = \left\{\frac{\log(3)}{\log(3)}\right\}` + contrôle | `S = \left\{1\right\}` |
| `9^x-4*3^(x+1)+27=0` | C, M | `S = \left\{\frac{\log(3)}{\log(3)} \,;\, \frac{\log(9)}{\log(3)}\right\}` + contrôle | `S = \left\{1 \,;\, \frac{\log(9)}{\log(3)}\right\}` + contrôle |
| `2^(x+6)=2^(3x+4)` | M | `S = \left\{1\right\}` | `S = \left\{1\right\}` |
| `3^x=3*9^(x-1)` | M | `S = \left\{1\right\}` | `S = \left\{1\right\}` |


- Aucun instantané modifié par Q6.
- Rédaction nouvelle, à juger à l'écran : `2^(x^2-5x)=2^(-1/2)`, méthode « Même base » (identique à la méthode B après l'égalité des exposants).
- Écriture mêlée fraction / décimal (R13, comportement existant de la suite B et de la réécriture des bases, non changé) :
  `0,5^(x^2-x)=0,5^(-1/4)` : « −x² + x = 1/4 ⇔ −x² + x − 0,25 = 0 » ; `(1/2)^(x^2-x)=(1/2)^(0,5)` : « = 2^(−1/2) », « −x² + x + 0,5 = 0 ».
- a < 0 : x₁ = (−5 + √23)/(−2) (question Q7, non traitée).

## Écarts

- **`verifier` Q6** (82dc0ba) : seul motif, les fichiers non suivis de l'enseignant (vaut accepté). Sous-tests en hausse (acceptés) :
  `test_audit_el.py` (deux tests, des équations générées en plus sont résolues), vouvoiement (littéraux ajoutés).
- **`verifier` Q4** (390ad22) : **REFUSÉ, deux motifs.**
  1. Fichiers non suivis de l'enseignant : vaut accepté.
  2. **Sous-tests en baisse** : `test_resoudre_el.py::TestLignesAlignees::test_les_liens_les_elements_et_les_proprietes_du_moteur` et
     `::test_rien_ne_se_perd_par_rapport_a_la_ligne_unique`, 324 → 322 (un sous-test par chaîne affichée). `5^(3x+2)=(5^x)^2` affichait
     3 chaînes (la résolution, puis le regroupement « 2log(5) = log(5²) = log(25) » et « −log(5) = log(1/5) » de x = log(25)/log(1/5)) ;
     il n'en affiche plus qu'une (x = 2log(5)/(−log(5)) = −2) : texte retiré du corrigé, aucun test modifié.
     Ce ne sont pas des sous-tests de vocabulaire : hors de l'exception de la consigne, donc **pas de fusion**, branche poussée seule.
- Commande de fusion, si l'enseignant accepte ce motif : `git switch main && git merge --no-ff --no-edit explog-q4-q6`, puis `git push`,
  puis `git branch -d explog-q4-q6` ; puis, au prochain chantier, rafraîchir `tests/reference/` (`lancer.py reference`).

## Reprise après compactage

- Branche `explog-q4-q6` ; un commit par question (Q6, puis Q4) ; suite d'avant commit :
  `PROCESSUS_PAGES=4 python3 tests/lancer.py complet --rapport <scratchpad>/q<N>` puis `verifier`.
- Fichiers non suivis de l'enseignant (`docs/architecture.md`, `docs/chantiers/equations-2e-degre/quiz.md`, `docs/chantiers/revue-structure/`) :
  ne pas y toucher ; un refus de `verifier` pour ce seul motif vaut accepté ; de même une variation des sous-tests de vocabulaire liée
  à un texte retiré du code (consigne du 05.11). Tout autre refus : pousser la branche seule.
