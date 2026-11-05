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

### verifier (point 1, commit 6fb5ec1)

REFUSÉ, 2 motifs : (b) les 3 fichiers non suivis de l'enseignant sous `docs/` (vaut accepté, consigne) ; (c) sous-tests en baisse,
`test_exp_log.py::TestVouvoiement::test_aucun_texte_du_fichier_ne_tutoie` 1 208 → 1 207 et
`test_vocabulaire.py::TestVouvoiement::test_litteraux_des_moteurs` 8 698 → 8 697 (un sous-test par littéral de exp_log.py ; le littéral
`"+-"` de l'ancienne condition a disparu). Listes de tests sinon identiques à la référence, 4 tests ajoutés.

## Point 2 : garde générale

### Balayage des fichiers enregistrés (brouillon, scratchpad `scan.py`, motif `[+\-−]\s*[+\-−]` sur chaque chaîne entière)

- Instantanés `resoudre` : seulement les 3 fautes du point 1.
- Références de pages : nombreuses occurrences dans le texte en clair des cartes, toutes des cases de tableaux de signes collées
  (« ⟦x - 1⟧−−0+⟦x + 3⟧−++ ») ou les boutons du graphique (« Graphique − + Réinitialiser ») : d'où le choix de ne contrôler dans les
  références que les formules ⟦…⟧ et chaque case de tableau.
- Garde définitive (`test_doubles_signes.py`) sur les fichiers de `main` (`git show`) : exactement les 3 fautes du point 1, dans
  l'instantané et la référence 3C ; sur la branche après le point 1 : aucune.

### Cas trouvé hors corpus (balayage en (−x) du point 1)

`e^(-x)*e^((-x)+1)=5` (C et M), variante « Logarithmes » : `-x + -x + 1 = \ln(5)`. Arbre `Op("+", Neg(x), Op("+", Neg(x), 1))` : le
second terme n'est ni un `Neg` ni un nombre négatif, mais son TeX commence par « - ». Correction : parenthèses dans ce cas (« + » et « − »).
Après : `-x + (-x + 1) = \ln(5)`. Balayage complet (corpus et variantes, tous les doubles signes) : 0 entrée. Aucun instantané changé.

### Tests

`test_doubles_signes.py` (4 tests, 0,5 s) ; `test_explog_doubles_signes.py` : 5 tests. Sans la correction du point 2 : 3 échecs.

### Suite complète d'avant commit (point 2)

`PROCESSUS_PAGES=4 python3 tests/lancer.py complet --rapport /tmp/claude-1000/-home-sami-ubuntu-site/3d463e14-8256-47e9-b8e9-912fa4c5bc5c/scratchpad/p2` : code 0.
- Python : 1 326 passed, 1 xfailed, 103 616 sous-tests, 103 s.
- Pages : 123 passed, 2 386 sous-tests, 296 s.
