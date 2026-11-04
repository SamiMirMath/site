# Correctif Exp-log : Δ et second membre calculé (04.11.2026)

Branche `correctif-explog-delta` (depuis `main`, 351fb77). Un seul commit. Rien n'est poussé ni fusionné.
Origine : audit Équations du 2e degré, `docs/chantiers/equations-2e-degre/audit-etape0.md`, § 0, point 4.

## Résumé

**Cause.**
- Dans la méthode B « Logarithmes » (`_alpha`, `exponentielles-logarithmes/exp_log.py`), le second membre de « P(x) = c » est l'exposant tel qu'il est écrit.
  Pour `2^(-6)`, c'est l'arbre `Neg(6)`, et non le nombre −6.
- `_suite_polynome` ne reconnaissait un nombre que par `isinstance(c, Nb)`.
  - `Neg(6)` partait donc dans la branche « coefficients logarithmiques ».
  - Cette branche écrit `P(x) − c = 0` et `Δ = b² − 4a(q − c) = r0 + 4a·c` sans rien calculer.
  - D'où « x² − 5x − (−6) = 0 », « 4·1·(−−6) », « 25 + 4(−6) », puis S = {x₁ ; x₂} et un contrôle à la calculatrice.
- Même cause au 1er degré : `2^(x-5)=2^(-6)` donnait `x = 5 − 6` et `S = {5 − 6}`.
- Avec `1/64`, c = log(1/64)/log(2) restait un quotient de logarithmes : Δ = 25 + 4·log(1/64)/log(2), jamais calculé.
- Défaut voisin, dans la même branche : avec a < 0 ou un c écrit avec un signe moins, on lisait « 9 + (−4)·ln(2) » et « −(−3)/log(2) ».

**Correction** (`exp_log.py` seulement ; l'outil Exp-log est le seul à importer ce module).
1. `_second_membre_calcule` : un second membre rationnel sans logarithme (−6, 3/2, −6,5) devient un nombre avant la suite.
   - La suite passe alors par la résolution de la méthode « même base » : `x² − 5x + 6 = 0 ⇔ (x − 2)(x − 3) = 0`.
   - C'est ce que la spécification prévoyait déjà (point 5 du 27.10 : « Un second membre rationnel garde la résolution de la méthode « même base » »).
2. `_puissance_de_la_base` (2e degré avec un terme en x seulement, c'est-à-dire là où Δ apparaîtrait) : quand la constante b vaut exactement a^k, la puissance est écrite dans le logarithme.
   - Exemple : `(x² − 5x)·log(2) = log(2⁻⁶) = −6·log(2)`, avec la propriété log(a^A) = A · log(a), puis `x² − 5x = −6` (car log(2) ≠ 0).
   - C'est la règle de la méthode B pour les puissances de 10 (`log(100) = log(10²) = 2·log(10)`).
   - On n'utilise ni log_a(a^k) = k ni le changement de base, que EL-20 interdit en méthode B.
   - L'exactitude est décidée par décomposition en facteurs premiers (`_exposant_de_la_base`), jamais numériquement.
3. Sinon (b n'est pas une puissance de a), Δ s'écrit avec les logarithmes, sans double signe.
   - « 25 − 4·log(3)/log(2) », « 25 − 4·3/log(2) », « x² − 5x + 3/log(2) = 0 ».
   - Un Δ rationnel non entier est calculé : `Δ = (−5)² − 4·1·(−3/2) = 31`, `Δ = … = 0`, puis « une seule solution ».
   - Le terme constant décimal reste décimal (6,5 ; R13).
4. La spécification (`docs/specifications/exponentielles-logarithmes.md`, « Corrections après la chasse aux trous », point 5) est amendée en conséquence.
   - Le choix de la variante par défaut n'est pas modifié.

**Entrées touchées.**
- Toute équation `a^P(x) = constante` avec P du 2e degré et un terme en x, quand le second membre est :
  - une puissance de a à exposant négatif ou fractionnaire (`2^(-6)`, `e^(-6)`, `10^(-6)`, `2^(3/2)`, `2^(-6,5)`) ;
  - ou une constante qui est exactement une puissance de a (`1/64`, `4^3`, `4^(-3)`, `8^(1/3)`, `1/2^6`, `3·2^P = 3/64`, base 1/2 ou 0,5, base 4 avec `2^(-12)`).
- Ces cas valent en 3C comme en 2Ms/2Mr : les deux filières passent par le même `variantes_equation`, et leurs sorties sont identiques (test).
- Le 1er degré avec un exposant négatif (`2^(x-5)=2^(-6)` donne x = −1).
- Le Δ à logarithmes avec a < 0 : 3 entrées du corpus, seul changement visible du corpus existant.
- Non touchés :
  - un second membre positif entier (`2^6`, `64` passaient déjà) ;
  - b = 0 (x² = k) ;
  - la méthode « Même base / définition » ;
  - les équations à plusieurs facteurs (`3^(x^2)=3^(x+6)`, `_beta`) ;
  - le 1er degré écrit avec des logarithmes (`2^(x-5)=1/64` garde S = {5 + log(1/64)/log(2)} et son contrôle, R15).

**Rendu de l'exemple cible (méthode « Logarithmes », par défaut).**

| | Avant | Après |
|---|---|---|
| `2^(x^2-5x)=2^(-6)` | … ⇔ x² − 5x = −6 ⇔ x² − 5x − (−6) = 0 ; Δ = (−5)² − 4·1·(−−6) = 25 + 4(−6) ; x₁ = (5 − √Δ)/2 ; x₂ = … ; S = {x₁ ; x₂} ; « Contrôlez à la calculatrice : on retrouve x = 2 ou x = 3. » | … ⇔ x² − 5x = −6 (car log(2) ≠ 0) ⇔ x² − 5x + 6 = 0 ⇔ (x − 2)(x − 3) = 0 ⇔ x = 2 ou x = 3 ; S = {2 ; 3} |
| `2^(x^2-5x)=1/64` | (x² − 5x)·log(2) = log(1/64) ⇔ x² − 5x = log(1/64)/log(2) ⇔ x² − 5x − log(1/64)/log(2) = 0 ; Δ = (−5)² − 4·1·(−log(1/64)/log(2)) = 25 + 4·log(1/64)/log(2) ; S = {x₁ ; x₂} + contrôle | (x² − 5x)·log(2) = log(1/64) ⇔ (x² − 5x)·log(2) = log(2⁻⁶) = −6·log(2) (log(a^A) = A · log(a)) ⇔ x² − 5x = −6 (car log(2) ≠ 0) ⇔ x² − 5x + 6 = 0 ⇔ (x − 2)(x − 3) = 0 ⇔ x = 2 ou x = 3 ; S = {2 ; 3} |
| `2^(2x^2-5x)=2^(-3)` | Δ = (−5)² − 4·2·(−−3) = 25 + 8(−3) ; S = {x₁ ; x₂} | 2x² − 5x + 3 = 0 ; Δ = (−5)² − 4·2·3 = 1 ; S = {1 ; 3/2} |
| `2^(x-5)=2^(-6)` | x − 5 = −6 ⇔ x = 5 − 6 ; S = {5 − 6} | x − 5 = −6 ⇔ x = −1 ; S = {−1} |

La consigne demandait d'écrire « Δ = (−5)² − 4·1·6 = 1 ». Pour a = 1 et un Δ carré parfait, l'outil factorise, comme la méthode « même base » : « x² − 5x + 6 = 0 ⇔ (x − 2)(x − 3) = 0 ».
C'est la résolution qu'il donne déjà pour `2^(x^2-5x)=2^6` et `10^(x²+x)=100` (spécification, point 5). La ligne Δ apparaît quand a ≠ 1 ou quand Δ n'est pas un carré parfait (voir question 1).

## Pourquoi « Même base » n'est pas la variante par défaut (`2^(x^2-5x)=2^(-6)`, `3^(x^2)=3^(x+6)`) : choix non modifié

- **Code.**
  - `exponentielles-logarithmes/resoudre_el.py`, `_resoudre` : toute équation exponentielle qui a deux résolutions est rendue par `so.sortie_ok_variantes(…, el.METHODE_LOGARITHMES, …)`.
    `variante_defaut` vaut donc toujours « logarithmes », quelle que soit l'équation.
  - Il n'existe aucune règle « par équation » : le moteur ne regarde jamais si la méthode A s'applique pour choisir le défaut.
  - Sur la page, `commun/outil.js` (`varianteAffichee`) affiche d'abord la variante mémorisée. C'est le dernier clic de l'élève, gardé dans `localStorage` « variante:exponentielles-logarithmes ».
    Le défaut « logarithmes » ne sert qu'à la première visite, ou quand le stockage est absent.
- **Doctrine.**
  - Décision de l'enseignant du 27.10.2026 (`docs/specifications/exponentielles-logarithmes.md`, « Sélecteur de méthode » ; commit 3a63331 ; `docs/taches.md`, suite du 27.10 ; suivi T33) :
    « Chaque équation exponentielle se résout de deux façons […] « Même base / définition » (A) et « Logarithmes » (B, **défaut**) ; le choix est gardé d'une équation à l'autre (localStorage […], défaut « Logarithmes ») ».
  - EL-19 l'écrit aussi : « toute équation exponentielle a deux variantes calculées en une fois (`variantes`, défaut « logarithmes ») ».
  - La raison de fond est dans la même section : B est « **toujours disponible** », A ne l'est pas.
    - A affiche « b n'est pas une puissance de a : il faut les logarithmes. » pour `3^x = 20`, `2^(x−1) = 3^x`, `2^(x^2-5x)=2^(-1/2)`, sans carte « Solution ».
    - Un défaut stable, que l'élève change une fois et qui reste, évite que la méthode affichée change d'une équation à l'autre.
    - Ce défaut est gardé d'une saisie à l'autre et ne dépend donc pas de l'équation. La case « Problème d'application », elle, dépend de l'équation, et son état est oublié à la saisie suivante.
- **Suivis.**
  - T35 (2M) a repris le même sélecteur sans le changer.
  - Le correctif explog-3c (02.11.2026, `docs/chantiers/explog-3c/suivi.md`) a aligné la 3C sur la 2M sans toucher au défaut.
  - Aucun de ces documents ne prévoit un défaut « même base quand elle s'applique ».
- **Pour `3^(x^2)=3^(x+6)`.**
  - Les deux membres ont une inconnue : la méthode B passe par `_beta` (« x² en exposant », spécification).
  - Le trinôme y a des coefficients logarithmiques : `x²·log(3) − x·log(3) − 6log(3) = 0`, puis `Δ = (−log(3))² − 4log(3)·(−6log(3))`, x₁, x₂ et un contrôle à la calculatrice.
  - C'est la rédaction prévue (« les logarithmes de 4 et de 8 restent écrits ») ; elle n'est pas touchée par ce correctif (question 3).

## Instantanés modifiés (à relire par l'enseignant)

Seul l'outil Exp-log est concerné : aucun autre outil n'importe `exp_log.py`, et seuls ses instantanés et ses références ont été régénérés.

| Fichier | Avant → après | Modifiées | Ajoutées | Retirées |
|---|---|---|---|---|
| `tests/python/instantanes/resoudre/exponentielles-logarithmes.json` (3C) | 583 → 625 | 3 | 42 (`BATTERIE_DELTA` + `DELTA_PAS_ENCORE`) | 0 |
| `tests/python/instantanes/resoudre/exponentielles-logarithmes-M.json` (2M) | 276 → 318 | 0 | 42 | 0 |
| `tests/pages/references/exponentielles-logarithmes.json` (page 3C) | 582 → 624 | 3 (les mêmes) | 42 | 0 |
| `tests/pages/references/exponentielles-logarithmes-M.json` (page 2M) | 276 → 318 | 0 | 42 | 0 |

Les trois entrées modifiées ont toutes la même différence, la ligne Δ : « + (−4)· » devient « − 4 ».

| Entrée (fichier 3C ; variantes) | Avant | Après |
|---|---|---|
| `10^(-x)/10^(x^2)=1/4` (Même base / définition) | `Δ = (-1)^{2} - 4(-1) \cdot \left(-\log\left(\frac{1}{4}\right)\right) = 1 + (-4) \cdot \log\left(\frac{1}{4}\right)` | `Δ = (-1)^{2} - 4(-1) \cdot \left(-\log\left(\frac{1}{4}\right)\right) = 1 - 4\log\left(\frac{1}{4}\right)` |
| `e^(-x^2+3x)=2` (sortie, Même base / définition, Logarithmes) | `Δ = 3^{2} - 4(-1) \cdot (-\ln(2)) = 9 + (-4) \cdot \ln(2)` | `Δ = 3^{2} - 4(-1) \cdot (-\ln(2)) = 9 - 4\ln(2)` |
| `e^(x/2)/e^(x^2+x)=1/4` (Même base / définition) | `Δ = \left(-\frac{1}{2}\right)^{2} - 4(-1) \cdot \left(-\ln\left(\frac{1}{4}\right)\right) = \frac{1}{4} + (-4) \cdot \ln\left(\frac{1}{4}\right)` | `… = \frac{1}{4} - 4\ln\left(\frac{1}{4}\right)` |

Dans `tests/pages/references/exponentielles-logarithmes.json`, les champs `texte` des mêmes cartes changent de la même façon (KaTeX entre ⟦ ⟧).

Les 42 entrées ajoutées sont celles de `BATTERIE_DELTA`, dans `tests/python/cas_el.py` (rendus ci-dessus pour les principales).

## Tests ajoutés

`tests/python/test_explog_delta.py` (15 tests, environ 590 sous-tests) :
- **Oracle** : `tests/python/oracle.py`, sur les membres lus par l'outil ED, jamais par le parseur d'Exp-log.
  - Chaque solution des deux méthodes annule g − d (< 10⁻²⁰) et vaut la valeur attendue.
  - Aucune racine simple n'est perdue (balayage de [−20 ; 20] et bissection).
- **Égalités des chaînes** : chaque égalité de la méthode B est vraie en chaque racine (≥ 300 vérifications), y compris log(2⁻⁶) = −6·log(2) et Δ = formule = valeur.
- **Filières** : même sortie en C et en M, défaut « logarithmes ».
- **Rédaction** :
  - aucun double signe (`--`, `- (-`, `+ (-`, `+ -`) ;
  - textes exacts du constat, de 1/64, de Δ entier, de Δ rationnel (31, 23, 0, −1, −5 avec 6,5 et 7,5 décimaux) ;
  - Δ à logarithmes ; autres bases (4³, 2⁻¹², (1/2)⁻⁶, 8^(1/3), 1/2) ; base 10 avec 1000⁻² ;
  - 1er degré ; 1er degré avec log gardé (R15) ;
  - EL-20 sur toute la famille.
- Contrôle : sur le moteur d'avant, 49 échecs (sous-tests compris) ; après, tous passent.
- Largeurs : les tests de page `test_t33_el_une_etape_par_ligne_sans_defilement_a_360_px` et `test_t35_el_filiere_m_une_etape_par_ligne_sans_defilement_a_360_px` parcourent tout le corpus, nouvelles entrées comprises. Ils sont verts (625 et 318 sous-tests).

## Temps natif du moteur (`resoudre_el.resoudre` sur le corpus de l'instantané)

| | 3C | 2M |
|---|---|---|
| Avant, ancien corpus (583 / 276 entrées) | 1,25 s (2,1 ms/entrée) | 0,42 s (1,5 ms/entrée) |
| Avant, nouveau corpus (625 / 318) | 1,38 à 1,40 s (2,2 ms) | 0,54 à 0,55 s (1,7 ms) |
| Après, nouveau corpus (625 / 318) | 1,36 à 1,38 s (2,2 ms) | 0,52 à 0,53 s (1,6 ms) |

Aucune hausse.

## Suite complète

`python3 tests/lancer.py complet` (04.11.2026, environ 29 min) :
- Python : 1 311 passed, 1 xfailed (déjà présent), 103 038 sous-tests, en 739 s.
- Pages : 121 passed, 1 failed, 2 552 sous-tests, en 955 s (code 1).
  - L'échec est le test instable connu `test_clavier.py::test_a_deux_formules_aux_touches_donnent_le_corrige_de_la_saisie_directe`.
  - Relancé seul, sans modification : 1 passed (32 s).
- Second passage, après le retrait d'un doublon dans `BATTERIE_DELTA` et la mise à jour d'un commentaire : code 0.
  - Python : 1 311 passed, 1 xfailed, 103 033 sous-tests, en 724 s.
  - Pages : 122 passed, 2 554 sous-tests, en 966 s.
- Suite verte.

## Questions pour l'enseignant

Option prise à chaque fois : celle qui affiche le moins.

1. **Δ attendu ou factorisation ?** Pour `2^(x^2-5x)=2^(-6)`, l'outil écrit maintenant « x² − 5x + 6 = 0 ⇔ (x − 2)(x − 3) = 0 », comme la méthode « même base » et comme `2^(x^2-5x)=2^6` aujourd'hui.
   La consigne parlait de « Δ = (−5)² − 4·1·6 = 1 ». Faut-il, en méthode B, toujours passer par Δ ?
2. **b = 0 avec une constante puissance de la base** (`2^(x^2-4)=1/8`) : la méthode B garde `x² = 4 + log(1/8)/log(2)`, puis x₁ = −√(…), S = {x₁ ; x₂} et le contrôle « on retrouve x = −1 ou x = 1 ».
   Ce n'est pas faux, mais c'est lourd. Faut-il y appliquer aussi log(1/8) = log(2⁻³) = −3·log(2) ? Non fait : il n'y a pas de Δ.
3. **Équations à plusieurs facteurs** (`3^(x^2)=3^(x+6)`, `_beta`) : Δ reste écrit `(−log(3))² − 4log(3)·(−6log(3))`, sans valeur, puis S = {x₁ ; x₂} et le contrôle.
   Faut-il diviser par log(3) quand tous les coefficients en sont des multiples ?
4. **`2^(x^2-5x)=2^0`** : la méthode B donne S = {0 ; 5log(2)/log(2)}, avec le contrôle « on retrouve x = 0 ou x = 5 » (`_beta`, mise en facteur de x). C'est juste mais non simplifié ; non touché.
5. **Base 10 et autre base** (`10^(x^2-5x)=1000^(-2)`) : log(1000) n'est pas calculé, parce que log(10ᵏ) = k est interdit en méthode B (EL-20).
   Δ s'écrit `25 − 4·2log(1’000)`, sans faute. Faut-il écrire `log(1000) = log(10³) = 3·log(10)` ?
6. **Méthode A et exposant fractionnaire** : pour `2^(x^2-5x)=2^(-1/2)`, `2^(x^2-x)=2^(-1/4)` et `2^(x^2-5x)=2^(-6,5)`, la méthode « Même base / définition » affiche « Il faut les logarithmes. ».
   Les bases sont pourtant les mêmes : son trinôme à coefficients non entiers n'est pas traité. Non touché.
7. **a < 0 dans x₁, x₂** (`2^(-x^2+5x)=3`) : `x₁ = (−5 + √Δ)/(−2)`. C'est juste, mais un dénominateur négatif est inhabituel. Non touché.
8. **Hors de cette famille (ticket à ouvrir)** : la carte « Contrôle » de la 3C écrit des doubles signes en remplaçant x par une valeur négative dans −x.
   On lit `log(--100)` (`log(-x)=2`), `log_{--2}(4)` (`log_(-x)(4)=2`) et `-\log(1/100) = --2` (`-log(x)=2`). C'est juste, mais mal écrit.
   Le test « aucun double signe » de ce correctif ne couvre donc que la famille Δ.

## Reprise après compactage

- Branche `correctif-explog-delta`. Un seul commit est prévu, après la suite complète verte.
- Fichiers de la tâche :
  - `exponentielles-logarithmes/exp_log.py` ;
  - `tests/python/cas_el.py` ;
  - `tests/python/test_explog_delta.py` ;
  - les 4 fichiers d'instantanés et de références listés plus haut ;
  - `docs/specifications/exponentielles-logarithmes.md` ;
  - ce fichier.
- `docs/chantiers/tests-rapides/` ne fait pas partie de la tâche : ne pas l'ajouter.
