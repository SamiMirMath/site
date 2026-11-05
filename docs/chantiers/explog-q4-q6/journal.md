# Journal — explog-q4-q6 (PC, 05.11.2026)

## Q6

### Balayage (scratchpad `q6.py`)

Voisines : bases 2, 3, 10, e, 0,5, (1/2), 4 ; exposants −1/2, 1/2, −1/4, −2/9, 0,5, −6,5, −6, 3/2, −3 ; trinômes x² − 5x, x² − x,
2x² − 5x, x², −x² + 5x, x² − 1 ; plus a^(x²) = a^(x + 1/2), 4^(x² − 5x) = 2^(−1), 8^(x²) = 2^(x + 1), 4^(x² − x) = 8^(−1/2),
9^(x²) = 3^(x + 1/2), 2^(x² − x/2) = 2^1, 2^(x²/2 − x) = 2^(−1/2) ; 387 entrées, filières C et M.

| | « Il faut les logarithmes. » (A) | « … n'est pas une puissance de … » sur une voisine | « pas encore » |
|---|---|---|---|
| Avant (main a4884b0) | 274 C + 274 M | 4 (`4^(x^2-x)=8^(-1/2)`, `9^(x^2)=3^(x+1/2)`, C et M) | 43 C + 43 M |
| Après les corrections 1 et 2 | 0 | 0 | 42 + 42 (base (1/2), exposant non entier) |
| Après la correction 3 | 0 | 0 | 0 |

Corpus (`entrees_el`, `entrees_el_m`) : aucune entrée n'affichait le message ; la régénération des instantanés ne change rien.

Messages qui restent dans le corpus : « b n'est pas une puissance de a » pour des bases réellement différentes (2 et 3, e et 2, 10 et 3…).

### Exemple (méthode « Même base / définition », C et M)

`2^(x^2-5x)=2^(-1/2)` : 2^(x² − 5x) = 2^(−1/2) ⇔ x² − 5x = −1/2 ⇔ x² − 5x + 1/2 = 0 ; Δ = (−5)² − 4·1·1/2 = 23 ;
x₁ = (5 − √23)/2 ; x₂ = (5 + √23)/2 ; S = {x₁ ; x₂}, soit x ≈ 0,102 ou x ≈ 4,898.

### Tests

`tests/python/test_explog_q4_q6.py` : 3 tests, 864 sous-tests, 4 s. Moteur d'avant : 656 échecs.

### Suite complète d'avant commit (Q6)

`PROCESSUS_PAGES=4 python3 tests/lancer.py complet --rapport /tmp/claude-1000/-home-sami-ubuntu-site/3d463e14-8256-47e9-b8e9-912fa4c5bc5c/scratchpad/q6` : code 0 ; Python 1 329 passed, 1 xfailed, 104 566 sous-tests (113 s) ; pages 123 passed, 2 386 sous-tests (297 s). `rapide` avant : vert.
