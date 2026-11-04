# Correctif Exp-log : Δ « (−−6) » — suivi

Ticket D17 (a) de l'audit `docs/chantiers/equations-2e-degre/audit-etape0.md` § 0.4. Une seule partie, faite par la session principale (PC, 04.11.2026).
Détail (cause, essais, temps) : `journal.md`.

## État

| Partie | État | Commit |
|---|---|---|
| Correctif (`exp_log.py`, `_alpha` et `_suite_polynome`) + `tests/python/test_correctif_explog_delta.py` | fait, suite complète verte | « Correctif Exp-log : … » |

## Ce qui change à l'écran (variante « Logarithmes », filières C et M)

| Entrée | Avant | Après |
|---|---|---|
| `2^(x^2-5x)=2^(-6)` (aussi `2^(-6)=2^(x^2-5x)`, bases 10, e, 0,5) | x² − 5x − (−6) = 0 ; Δ = (−5)² − 4·1·(−−6) = 25 + 4(−6) ; x₁, x₂ avec √Δ ; S = {x₁ ; x₂} | x² − 5x + 6 = 0 ⇔ (x − 2)(x − 3) = 0 ⇔ x = 2 ou x = 3 ; S = {2 ; 3} |
| `2^(x^2+5x)=2^(-6)` | même défaut | x² + 5x + 6 = 0 ⇔ (x + 3)(x + 2) = 0 ; S = {−3 ; −2} |
| `2^(x-5)=2^(-6)` | x = 5 − 6 ; S = {5 − 6} | x = −1 ; S = {−1} |
| `2^(x^2-1)=2^(1/2)` | x² = 1 + 1/2 ; x₁ = −√(1 + 1/2) | x² = 3/2 ; x₁ = −√(3/2) |
| `2^(x^2-x)=2^(-1/4)` | x² − x − (−1/4) = 0 ; Δ = … (−−1/4) = 1 + 4(−1/4) = 0 | x² − x + 1/4 = 0 ; Δ = (−1)² − 4·1·1/4 = 0 |
| `2^(x^2-x)=2^(0,5)` | Δ = (−1)² − 4·1·(−0,5) = 1 + 4·0,5 ; x₁ = (1 − √Δ)/2 | Δ = (−1)² − 4·1·(−0,5) = 3 ; x₁ = (1 − √3)/2 |
| `2^(x^2-x)=2^(-2/9)` | Δ non calculé, x₁ et x₂ avec √Δ | Δ = … = 1/9 ; x = 1/3 ou x = 2/3 |

Les solutions n'étaient pas fausses avant (contrôle à la calculatrice juste) ; seule la rédaction l'était. Elles sont confirmées par l'oracle.

## À relire par l'enseignant

- **Instantanés modifiés : aucun.** Aucune entrée du corpus (`cas_el.py`, 583 entrées C, 276 M) ne passait par ce chemin ; les instantanés
  des autres outils ne bougent pas non plus. Les nouveaux cas sont couverts par `test_correctif_explog_delta.py` (rédaction exacte et oracle) ;
  ils n'ont pas été ajoutés à `cas_el.py` pour ne pas régénérer les instantanés Exp-log pendant le chantier tests-rapides du Mac.
- **Question 1 (option qui affiche le moins).** La consigne écrivait « Δ = (−5)² − 4·1·6 = 1 » pour `2^(x^2-5x)=2^(-6)`. L'outil, une fois le
  second membre devenu un nombre, résout comme d'habitude pour un trinôme à coefficients entiers : factorisation (somme-produit) quand a = 1
  et Δ est un carré, sinon Δ = b² − 4ac = valeur. C'est ce qu'affichent déjà `2^(x^2-5x)=2^6` (variante « Logarithmes ») et la variante
  « Même base » de la même équation ; on obtient donc (x − 2)(x − 3) = 0, sans ligne Δ. Pour écrire Δ ici, il faudrait le décider pour tous les
  trinômes de l'outil.
- **Question 2.** `2^(x^2-5x)=1/64` n'est pas changé : la méthode « Logarithmes » applique les propriétés à ce qui est écrit
  (spécification, exemple 10 : « log(32) reste log(32) ») ; x² − 5x = log(1/64)/log(2), Δ écrit avec des log (comme l'exemple 11,
  `2^(x²)·4^x = 8`), puis « Contrôlez à la calculatrice : on retrouve x = 2 ou x = 3 ». C'est juste, mais long. Le simplifier
  (log(1/64) = log(2⁻⁶) = −6·log(2)), comme on le fait déjà pour log(100) = log(10²) = 2·log(10), serait une nouvelle règle de rédaction.
- **Hors correctif, vu en passant.** La ligne « (x² − 5x) · log(2) = (−6) · log(2) » garde des parenthèses autour de −6, alors que
  l'exposant positif donne « 6log(2) ». Ce n'est pas faux ; non changé.

## Pourquoi « Même base » n'est pas la variante par défaut (ici et pour `3^(x^2)=3^(x+6)`)

Ce n'est pas un défaut, c'est la décision du 27.10.2026 (spécification `exponentielles-logarithmes.md`, « Sélecteur de méthode », commit 3a63331) :
« Logarithmes » (B) est la variante par défaut de **toutes** les équations exponentielles, sans choix équation par équation.

1. B est la seule méthode **toujours disponible** ; A (« Même base / définition ») ne s'applique que si les deux membres s'écrivent dans la même
   base (ou base 10 / e seule), sinon elle affiche « b n'est pas une puissance de a : il faut les logarithmes ». Une valeur par défaut fixe
   montre toujours une résolution complète.
2. Le choix de l'élève est **gardé d'une équation à l'autre** (`localStorage`, défaut « Logarithmes ») : un défaut qui changerait selon
   l'équation ferait sauter l'affichage d'une méthode à l'autre et contredirait ce choix.
3. Le code le dit explicitement : `resoudre_el._resoudre` passe `el.METHODE_LOGARITHMES` à `sortie_ok_variantes`, sans regarder si A s'applique.

Pour `3^(x^2)=3^(x+6)`, B donne x²·log(3) − x·log(3) − 6·log(3) = 0, puis Δ écrit avec des log (exemple 11 de la spécification) : c'est juste,
mais moins lisible que A (x² − x − 6 = 0 ⇔ (x + 2)(x − 3) = 0). Rendre A prioritaire quand elle s'applique serait une nouvelle décision ;
la variante par défaut **n'a pas été changée** (un test le vérifie).

## Suite

- Suite complète (`python3 tests/lancer.py complet`, code de retour 0) verte avant le commit : 1 300 Python (dont les 4 nouveaux), 1 xfail
  (existant), 123 pages ; PC WSL2, 147 s + 534 s.

## Reprise après compactage

Correctif terminé si le commit « Correctif Exp-log : … » est sur `correctif-explog-delta` et la suite verte. Il reste les questions 1 et 2 pour l'enseignant.
