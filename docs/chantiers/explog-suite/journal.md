# Journal — explog-suite (PC, 05.11.2026)

## Point 1 : doubles signes de la carte « Contrôle »

### Reproduction (avant, `main` 78e09d6, filière C)

- `log(-x)=2` : `\log(--100) = \log(100) = \log(10^{2}) = 2`
- `log_(-x)(4)=2` : `\log_{--2}(4) = \log_{2}(4) = \log_{2}(2^{2}) = 2`
- `-log(x)=2` : `-\log\left(\frac{1}{100}\right) = --2`, puis `= 2`
- Filière M : pas de carte « Contrôle » (ensemble de définition, puis « dans l'ensemble de définition ✓ ») ; les mêmes entrées n'y ont pas de double signe.

### Cause

`exp_log.py`, `tex()`, nœud `Neg` : `"-" + s`, avec parenthèses seulement si l'argument est une somme (`Op` + ou −).
`exp_log_m._substituer` remplace x par l'arbre de la solution : −x devient `Neg(Nb(−100))`. `_logs_de_puissances` donne `Neg(Nb(−2))` pour
−log(1/100). Une saisie `-(-x)` donne `Neg(Neg(Var x))`. Dans les trois cas, le TeX collait les deux signes.

### Correction

`Neg` : parenthèses dès que l'argument est `_comme_somme` (somme, opposé ou nombre négatif), la règle déjà utilisée pour le second
terme d'une soustraction. Aucun calcul ne change, seule l'écriture.

### Balayage (scratchpad, `balayage.py`) : corpus C (`entrees_el`) et M (`entrees_el_m`), plus chaque entrée où x devient (−x)

Motif `[+\-−]\s*[+\-−]` dans chaque formule \( \) et chaque champ tex, et dans le texte hors formules (tableaux exclus).

| | Entrées avec un double signe |
|---|---|
| Avant | 133 (118 en C, 15 en M) |
| Après | 1 : `e^(-x)*e^((-x)+1)=5` (C), `-x + -x + 1 = \ln(5)` : autre cause (somme dont le second terme commence par −), traitée au point 2 |

Exemples d'avant, hors corpus : `\log_{2}(--16)`, `\ln(--e^{3})`, `(--x) \cdot \log(4) = 6\log(2)` (C) ; `3^{--x} = 3^{x}`,
`\log_{--x}(4) = 2`, `e^{--x} = \pi` (M).

Durée du balayage : 1,7 s (corpus et variantes, deux filières) : il entre tel quel dans le test.

### Test

`tests/python/test_explog_doubles_signes.py` : 4 tests, 1 645 sous-tests, 1,8 s. Sur le moteur d'avant : 137 échecs (sous-tests).

### Suite complète d'avant commit

`PROCESSUS_PAGES=4 python3 tests/lancer.py complet --rapport /tmp/claude-1000/-home-sami-ubuntu-site/3d463e14-8256-47e9-b8e9-912fa4c5bc5c/scratchpad/p1` : code 0.
- Python : 1 321 passed, 1 xfailed, 103 595 sous-tests, 98 s.
- Pages : 123 passed, 2 386 sous-tests, 295 s.
