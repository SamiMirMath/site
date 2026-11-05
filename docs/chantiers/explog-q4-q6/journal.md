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

## Q4

### Balayage structurel (scratchpad `q4scan.py`)

Avant : 13 entrées en C et 4 en M avec un quotient p·L/(q·L) dans une solution (corpus et entrées ciblées) ; puis, au 1er degré,
`2^x=2*4^(x-1)`, `2^x-2^(2x-3)=0`, `5^(3x+2)=(5^x)^2`, `2^x+3^x=2^(x+1)+3^(x-1)`, `2^(x+6)=2^(3x+4)`, `3^x=3*9^(x-1)` (regroupement ou
numérateur = dénominateur). Après : aucune.

### Instantanés : lignes avant / après (méthode « Logarithmes », C puis M)

```
===== tests/python/instantanes/resoudre/exponentielles-logarithmes.json
## 25^x-6*5^x+5=0
   -S = \left\{0 \,;\, \frac{\log(5)}{\log(5)}\right\}
   -Contrôlez à la calculatrice : on retrouve \(x = 0\) ou \(x = 1\).
   +\phantom{x} = 1
   +S = \left\{0 \,;\, 1\right\}
   -S = \left\{0 \,;\, \frac{\log(5)}{\log(5)}\right\}
   -Contrôlez à la calculatrice : on retrouve \(x = 0\) ou \(x = 1\).
   +\phantom{x} = 1
   +S = \left\{0 \,;\, 1\right\}
## 2^(2t)-3*2^t=-2
   -S = \left\{0 \,;\, \frac{\log(2)}{\log(2)}\right\}
   -Contrôlez à la calculatrice : on retrouve \(t = 0\) ou \(t = 1\).
   +\phantom{t} = 1
   +S = \left\{0 \,;\, 1\right\}
   -S = \left\{0 \,;\, \frac{\log(2)}{\log(2)}\right\}
   -Contrôlez à la calculatrice : on retrouve \(t = 0\) ou \(t = 1\).
   +\phantom{t} = 1
   +S = \left\{0 \,;\, 1\right\}
## 2^(x+1)+2^(x-1)=10
   -x = 1 + \frac{\log(2)}{\log(2)}
   -S = \left\{1 + \frac{\log(2)}{\log(2)}\right\}
   -Contrôlez à la calculatrice : \(\frac{\log(2)}{\log(2)} = 1\), on retrouve \(x = 2\).
   +\phantom{x - 1} = 1
   +x = 2
   +S = \left\{2\right\}
   -x = 1 + \frac{\log(2)}{\log(2)}
   -S = \left\{1 + \frac{\log(2)}{\log(2)}\right\}
   -Contrôlez à la calculatrice : \(\frac{\log(2)}{\log(2)} = 1\), on retrouve \(x = 2\).
   +\phantom{x - 1} = 1
   +x = 2
   +S = \left\{2\right\}
## 2^(x^2)=2^(2x-1)
   -x = \frac{-b}{2a} = \frac{2\log(2)}{2\log(2)}
   -S = \left\{\frac{2\log(2)}{2\log(2)}\right\}
   -Contrôlez à la calculatrice : \(x = \frac{2\log(2)}{2\log(2)} = 1\).
   +x = \frac{-b}{2a} = \frac{2\log(2)}{2\log(2)} = 1
   +S = \left\{1\right\}
   -x = \frac{-b}{2a} = \frac{2\log(2)}{2\log(2)}
   -S = \left\{\frac{2\log(2)}{2\log(2)}\right\}
   -Contrôlez à la calculatrice : \(x = \frac{2\log(2)}{2\log(2)} = 1\).
   +x = \frac{-b}{2a} = \frac{2\log(2)}{2\log(2)} = 1
   +S = \left\{1\right\}
## 2^x+2^(x-1)=6
   -x = 1 + \frac{\log(2)}{\log(2)}
   -S = \left\{1 + \frac{\log(2)}{\log(2)}\right\}
   -Contrôlez à la calculatrice : \(\frac{\log(2)}{\log(2)} = 1\), on retrouve \(x = 2\).
   +\phantom{x - 1} = 1
   +x = 2
   +S = \left\{2\right\}
   -x = 1 + \frac{\log(2)}{\log(2)}
   -S = \left\{1 + \frac{\log(2)}{\log(2)}\right\}
   -Contrôlez à la calculatrice : \(\frac{\log(2)}{\log(2)} = 1\), on retrouve \(x = 2\).
   +\phantom{x - 1} = 1
   +x = 2
   +S = \left\{2\right\}
## 2^x+3^x=2^(x+1)+3^(x-1)
   -\phantom{x} = \frac{\log\left(\frac{3}{2}\right)}{\log\left(\frac{3}{2}\right)}
   -\phantom{x} = \frac{\log\left(\frac{3}{2}\right)}{\log\left(\frac{3}{2}\right)}
## 2^x-2^(2x-3)=0
   -\phantom{x} = \frac{\log(8)}{\log(2)}
   -3\log(2) = \log(2^{3})
   -\phantom{3\log(2)} = \log(8)
   -S = \left\{\frac{\log(8)}{\log(2)}\right\}
   -Contrôlez à la calculatrice : \(x = \frac{\log(8)}{\log(2)} = 3\).
   +\phantom{x} = 3
   +S = \left\{3\right\}
   -\phantom{x} = \frac{\log(8)}{\log(2)}
   -3\log(2) = \log(2^{3})
   -\phantom{3\log(2)} = \log(8)
   -S = \left\{\frac{\log(8)}{\log(2)}\right\}
   -Contrôlez à la calculatrice : \(x = \frac{\log(8)}{\log(2)} = 3\).
   +\phantom{x} = 3
   +S = \left\{3\right\}
## 2^x/3+2^(x+1)/3=2
   -S = \left\{\frac{\log(2)}{\log(2)}\right\}
   -Contrôlez à la calculatrice : \(x = \frac{\log(2)}{\log(2)} = 1\).
   +\phantom{x} = 1
   +S = \left\{1\right\}
   -S = \left\{\frac{\log(2)}{\log(2)}\right\}
   -Contrôlez à la calculatrice : \(x = \frac{\log(2)}{\log(2)} = 1\).
   +\phantom{x} = 1
   +S = \left\{1\right\}
## 2^x=2*4^(x-1)
   -\phantom{x} = \frac{\log(2)}{\log(2)}
   -\phantom{x} = \frac{\log(2)}{\log(2)}
## 3(2^x+1)=9
   -S = \left\{\frac{\log(2)}{\log(2)}\right\}
   -Contrôlez à la calculatrice : \(x = \frac{\log(2)}{\log(2)} = 1\).
   +\phantom{x} = 1
   +S = \left\{1\right\}
   -S = \left\{\frac{\log(2)}{\log(2)}\right\}
   -Contrôlez à la calculatrice : \(x = \frac{\log(2)}{\log(2)} = 1\).
   +\phantom{x} = 1
   +S = \left\{1\right\}
## 3^x+3^(x+2)=30
   -S = \left\{\frac{\log(3)}{\log(3)}\right\}
   -Contrôlez à la calculatrice : \(x = \frac{\log(3)}{\log(3)} = 1\).
   +\phantom{x} = 1
   +S = \left\{1\right\}
   -S = \left\{\frac{\log(3)}{\log(3)}\right\}
   -Contrôlez à la calculatrice : \(x = \frac{\log(3)}{\log(3)} = 1\).
   +\phantom{x} = 1
   +S = \left\{1\right\}
## 4*2^(-3x)-5*2^(-x)+2^x=0
   -S = \left\{0 \,;\, \frac{\log(2)}{\log(2)}\right\}
   -Contrôlez à la calculatrice : on retrouve \(x = 0\) ou \(x = 1\).
   +\phantom{x} = 1
   +S = \left\{0 \,;\, 1\right\}
   -S = \left\{0 \,;\, \frac{\log(2)}{\log(2)}\right\}
   -Contrôlez à la calculatrice : on retrouve \(x = 0\) ou \(x = 1\).
   +\phantom{x} = 1
   +S = \left\{0 \,;\, 1\right\}
## 4^x+4^(x+1)=20
   -S = \left\{\frac{\log(4)}{\log(4)}\right\}
   -Contrôlez à la calculatrice : \(x = \frac{\log(4)}{\log(4)} = 1\).
   +\phantom{x} = 1
   +S = \left\{1\right\}
   -S = \left\{\frac{\log(4)}{\log(4)}\right\}
   -Contrôlez à la calculatrice : \(x = \frac{\log(4)}{\log(4)} = 1\).
   +\phantom{x} = 1
   +S = \left\{1\right\}
## 5*2^(x^2)-3=7
   -x_{1} = -\sqrt{\frac{\log(2)}{\log(2)}}
   -x_{2} = \sqrt{\frac{\log(2)}{\log(2)}}
   -S = \left\{x_{1} \,;\, x_{2}\right\}
   -Contrôlez à la calculatrice : on retrouve \(x = -1\) ou \(x = 1\).
   +\phantom{x^{2}} = 1
   +x = -1 \text{ ou } x = 1
   +S = \left\{-1 \,;\, 1\right\}
   -x_{1} = -\sqrt{\frac{\log(2)}{\log(2)}}
   -x_{2} = \sqrt{\frac{\log(2)}{\log(2)}}
   -S = \left\{x_{1} \,;\, x_{2}\right\}
   -Contrôlez à la calculatrice : on retrouve \(x = -1\) ou \(x = 1\).
   +\phantom{x^{2}} = 1
   +x = -1 \text{ ou } x = 1
   +S = \left\{-1 \,;\, 1\right\}
## 5^(3x)-26*5^x+25*5^(-x)=0
   -S = \left\{0 \,;\, \frac{\log(5)}{\log(5)}\right\}
   -Contrôlez à la calculatrice : on retrouve \(x = 0\) ou \(x = 1\).
   +\phantom{x} = 1
   +S = \left\{0 \,;\, 1\right\}
   -S = \left\{0 \,;\, \frac{\log(5)}{\log(5)}\right\}
   -Contrôlez à la calculatrice : on retrouve \(x = 0\) ou \(x = 1\).
   +\phantom{x} = 1
   +S = \left\{0 \,;\, 1\right\}
## 5^(3x+2)=(5^x)^2
   -\phantom{x} = \frac{\log(25)}{\log\left(\frac{1}{5}\right)}
   -2\log(5) = \log(5^{2})
   -\phantom{2\log(5)} = \log(25)
   --\log(5) = \log\left(\frac{1}{5}\right)
   -S = \left\{\frac{\log(25)}{\log\left(\frac{1}{5}\right)}\right\}
   -Contrôlez à la calculatrice : \(x = \frac{\log(25)}{\log\left(\frac{1}{5}\right)} = -2\).
   +\phantom{x} = -2
   +S = \left\{-2\right\}
   -\phantom{x} = \frac{\log(25)}{\log\left(\frac{1}{5}\right)}
   -2\log(5) = \log(5^{2})
   -\phantom{2\log(5)} = \log(25)
   --\log(5) = \log\left(\frac{1}{5}\right)
   -S = \left\{\frac{\log(25)}{\log\left(\frac{1}{5}\right)}\right\}
   -Contrôlez à la calculatrice : \(x = \frac{\log(25)}{\log\left(\frac{1}{5}\right)} = -2\).
   +\phantom{x} = -2
   +S = \left\{-2\right\}
## 5^x+5^(x+1)+5^(x+2)=155
   -S = \left\{\frac{\log(5)}{\log(5)}\right\}
   -Contrôlez à la calculatrice : \(x = \frac{\log(5)}{\log(5)} = 1\).
   +\phantom{x} = 1
   +S = \left\{1\right\}
   -S = \left\{\frac{\log(5)}{\log(5)}\right\}
   -Contrôlez à la calculatrice : \(x = \frac{\log(5)}{\log(5)} = 1\).
   +\phantom{x} = 1
   +S = \left\{1\right\}
## 9*3^(-3x)-10*3^(-x)+3^x=0
   -S = \left\{0 \,;\, \frac{\log(3)}{\log(3)}\right\}
   -Contrôlez à la calculatrice : on retrouve \(x = 0\) ou \(x = 1\).
   +\phantom{x} = 1
   +S = \left\{0 \,;\, 1\right\}
   -S = \left\{0 \,;\, \frac{\log(3)}{\log(3)}\right\}
   -Contrôlez à la calculatrice : on retrouve \(x = 0\) ou \(x = 1\).
   +\phantom{x} = 1
   +S = \left\{0 \,;\, 1\right\}
## 9^x-3^x=6
   -S = \left\{\frac{\log(3)}{\log(3)}\right\}
   -Contrôlez à la calculatrice : \(x = \frac{\log(3)}{\log(3)} = 1\).
   +\phantom{x} = 1
   +S = \left\{1\right\}
   -S = \left\{\frac{\log(3)}{\log(3)}\right\}
   -Contrôlez à la calculatrice : \(x = \frac{\log(3)}{\log(3)} = 1\).
   +\phantom{x} = 1
   +S = \left\{1\right\}
## 9^x-4*3^(x+1)+27=0
   +\phantom{x} = 1
   -S = \left\{\frac{\log(3)}{\log(3)} \,;\, \frac{\log(9)}{\log(3)}\right\}
   +S = \left\{1 \,;\, \frac{\log(9)}{\log(3)}\right\}
   +\phantom{x} = 1
   -S = \left\{\frac{\log(3)}{\log(3)} \,;\, \frac{\log(9)}{\log(3)}\right\}
   +S = \left\{1 \,;\, \frac{\log(9)}{\log(3)}\right\}
===== tests/python/instantanes/resoudre/exponentielles-logarithmes-M.json
## 25^x-6*5^x+5=0
   -S = \left\{0 \,;\, \frac{\log(5)}{\log(5)}\right\}
   -Contrôlez à la calculatrice : on retrouve \(x = 0\) ou \(x = 1\).
   +\phantom{x} = 1
   +S = \left\{0 \,;\, 1\right\}
   -S = \left\{0 \,;\, \frac{\log(5)}{\log(5)}\right\}
   -Contrôlez à la calculatrice : on retrouve \(x = 0\) ou \(x = 1\).
   +\phantom{x} = 1
   +S = \left\{0 \,;\, 1\right\}
## 2^(2t)-3*2^t=-2
   -S = \left\{0 \,;\, \frac{\log(2)}{\log(2)}\right\}
   -Contrôlez à la calculatrice : on retrouve \(t = 0\) ou \(t = 1\).
   +\phantom{t} = 1
   +S = \left\{0 \,;\, 1\right\}
   -S = \left\{0 \,;\, \frac{\log(2)}{\log(2)}\right\}
   -Contrôlez à la calculatrice : on retrouve \(t = 0\) ou \(t = 1\).
   +\phantom{t} = 1
   +S = \left\{0 \,;\, 1\right\}
## 2^(x+6)=2^(3x+4)
   -\phantom{x} = \frac{\log(4)}{\log(4)}
   -2\log(2) = \log(2^{2})
   -\phantom{2\log(2)} = \log(4)
   -2\log(2) = \log(2^{2})
   -\phantom{2\log(2)} = \log(4)
   -\phantom{x} = \frac{\log(4)}{\log(4)}
   -2\log(2) = \log(2^{2})
   -\phantom{2\log(2)} = \log(4)
   -2\log(2) = \log(2^{2})
   -\phantom{2\log(2)} = \log(4)
## 3^x=3*9^(x-1)
   -\phantom{x} = \frac{\log(3)}{\log(3)}
   -\phantom{x} = \frac{\log(3)}{\log(3)}
## 4*2^(-3x)-5*2^(-x)+2^x=0
   -S = \left\{0 \,;\, \frac{\log(2)}{\log(2)}\right\}
   -Contrôlez à la calculatrice : on retrouve \(x = 0\) ou \(x = 1\).
   +\phantom{x} = 1
   +S = \left\{0 \,;\, 1\right\}
   -S = \left\{0 \,;\, \frac{\log(2)}{\log(2)}\right\}
   -Contrôlez à la calculatrice : on retrouve \(x = 0\) ou \(x = 1\).
   +\phantom{x} = 1
   +S = \left\{0 \,;\, 1\right\}
## 5^(3x)-26*5^x+25*5^(-x)=0
   -S = \left\{0 \,;\, \frac{\log(5)}{\log(5)}\right\}
   -Contrôlez à la calculatrice : on retrouve \(x = 0\) ou \(x = 1\).
   +\phantom{x} = 1
   +S = \left\{0 \,;\, 1\right\}
   -S = \left\{0 \,;\, \frac{\log(5)}{\log(5)}\right\}
   -Contrôlez à la calculatrice : on retrouve \(x = 0\) ou \(x = 1\).
   +\phantom{x} = 1
   +S = \left\{0 \,;\, 1\right\}
## 9*3^(-3x)-10*3^(-x)+3^x=0
   -S = \left\{0 \,;\, \frac{\log(3)}{\log(3)}\right\}
   -Contrôlez à la calculatrice : on retrouve \(x = 0\) ou \(x = 1\).
   +\phantom{x} = 1
   +S = \left\{0 \,;\, 1\right\}
   -S = \left\{0 \,;\, \frac{\log(3)}{\log(3)}\right\}
   -Contrôlez à la calculatrice : on retrouve \(x = 0\) ou \(x = 1\).
   +\phantom{x} = 1
   +S = \left\{0 \,;\, 1\right\}
## 9^x-4*3^(x+1)+27=0
   +\phantom{x} = 1
   -S = \left\{\frac{\log(3)}{\log(3)} \,;\, \frac{\log(9)}{\log(3)}\right\}
   +S = \left\{1 \,;\, \frac{\log(9)}{\log(3)}\right\}
   +\phantom{x} = 1
   -S = \left\{\frac{\log(3)}{\log(3)} \,;\, \frac{\log(9)}{\log(3)}\right\}
   +S = \left\{1 \,;\, \frac{\log(9)}{\log(3)}\right\}
```

### Suite complète d'avant commit (Q4)

`PROCESSUS_PAGES=4 python3 tests/lancer.py complet --rapport /tmp/claude-1000/-home-sami-ubuntu-site/3d463e14-8256-47e9-b8e9-912fa4c5bc5c/scratchpad/q4` : code 0 ; Python 1 334 passed, 1 xfailed, 105 807 sous-tests (92 s) ; pages 123 passed, 2 386 sous-tests (292 s).
