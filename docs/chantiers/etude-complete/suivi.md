# Chantier « Étude complète » — suivi

Refonte de l'outil Étude complète pour suivre le corrigé `docs/reference/etude-complete/3MSt_Ch8_EtudesFonctions_Corrige.tex` (exemple 7, exercice 8.15 a–d).
Branche `etude-complete`, créée le 02.11.2026 depuis `main` à jour (9716912, fusion de `correctif-explog-3c`). Rien n'est poussé ni fusionné.
Ordre de priorité : `CLAUDE.md` > `decisions.md` (validé par l'enseignant le 02.11.2026) > `audit-etape0.md`.
Un commit « EC P{N} : … » par partie ; suite complète verte (`python3 tests/lancer.py complet`, code de retour lu sans pipe) avant chaque commit.

**Reprise après compactage** : relire ce fichier, `decisions.md`, puis `git log --oneline main..HEAD` ; reprendre à la première partie « à faire ».
Les tests du chantier sont dans `tests/python/test_corpus_etude_complete.py` (corpus : `tests/python/donnees/corpus_etude_complete.py`) ; chaque
vérification pas encore faite y est marquée `xfail` **strict** avec le numéro de sa partie : la partie qui la traite retire la marque (un xfail qui
passe fait échouer la suite). Temps natif : `docs/chantiers/etude-complete/mesurer_temps.py`.

## Parties

| Partie | Contenu (decisions.md §6) | Touche | État | Commit |
|---|---|---|---|---|
| P0 | `suivi.md`, corpus + oracle mpmath, xfail marqués avec leur partie | tests | **fait** | 5eadf34 |
| P1 | D6, D7 (parenthèses, doublons), D17 | Dérivée | **fait** | voir `git log` (« EC P1 ») |
| P2 | Squelette des 6 parties titrées (D1), spécification (D2, D19) | EC | à faire | |
| P3 | Partie 1 : mise en forme + ED détaillé (D3) | EC | à faire | |
| P4 | Partie 2 : parité (D4) | EC | à faire | |
| P5 | Partie 3 : zéros, signe, f(0) (D5) | EC | à faire | |
| P6 | Partie 4 : D12, D13, D16 | Limites | reportée (hors de la nuit du 02.11) | |
| P7a | Dérivée de l'exposant détaillée, tableau u/v (D7, D8, D7b si simple) | Dérivée | à faire | |
| P7b | Valeurs dans le tableau de variations (D10), extremums (D11) | EC + Dérivée | à faire | |
| P8 | Graphe (D15, §3) | EC | à faire | |
| P9 | Exemples (D18), Bilan (D20), instantanés, largeurs 320–390 px, mesure Pyodide | EC | reportée (hors de la nuit du 02.11) | |
| P10 | *(facultatif)* Pente au point exclu (D14) | EC | reportée (hors de la nuit du 02.11) | |

## Résumé de la nuit

- **P0 faite** : branche `etude-complete` ; `audit-etape0.md` (copie inchangée du rapport d'audit) et `decisions.md` versés au dépôt ; corpus
  Ex7, a–d avec les résultats de decisions.md §4–5 ; oracle mpmath (fonctions écrites à la main) : tout le corpus est confirmé ; les valeurs de
  l'outil (ED, extremums, signe de f′, limites du tableau, asymptotes, fenêtre) sont justes ; 66 vérifications de rédaction marquées xfail (P1 à P10).
  Aucun changement du moteur.
- **P1 faite** : outil Dérivée (`derivee_variations.py`) : e^(somme) gardé entier (une exponentielle par exposant, D6) ; facteur négatif entre
  parenthèses et phrase de dérivée écrite une seule fois (D7) ; 3e^{−6} et 2eˣ(3 − eˣ) (D17). 5 xfail P1 retirés ; 5 instantanés de
  l'outil Dérivée / EC modifiés (liste sous « À relire ») ; questions 5 et 6 ; temps inchangé.

## Plans

### P0 (02.11.2026)

1. Branche `etude-complete` depuis `main` à jour ; copie telle quelle du rapport d'audit vers `audit-etape0.md`.
2. `tests/python/donnees/corpus_etude_complete.py` : une entrée par fonction (Ex7 exemple, a–d exercices, D18) avec f et f′ écrites à la main
   en mpmath, valeurs interdites, parité et sa justification (ED non symétrique ou f(0) et contre-exemple), zéros, signe de f, f(0), limites
   avec signe d'approche, regroupement ±∞, extremums (≈, global ou non, raison), AH et position, AV et côtés, ronds vides, pentes (P10).
3. `tests/python/test_corpus_etude_complete.py`, en trois sections :
   - **oracle** (mpmath seul, ni parseur ni SymPy) : f′ = dérivée numérique ; ED ; parité ; zéros et signe sur une grille fine ; f(0) ;
     limites et signe d'approche par sondes (±10ᵏ, a ± 10⁻ᵏ) ; extremums (f′ = 0, changement de signe, global recalculé d'après D11,
     raison) ; asymptotes et ronds vides déduits des limites ; pentes ; arrondis de decisions.md §2 ;
   - **valeurs de l'outil** (vertes aujourd'hui) : ED lu dans `ed_tex`, extremums (`x_tex`, `f_tex`, valeurs), points critiques et signe de
     f′, limites du tableau de variations (T06c) et 0⁺, asymptotes et côtés des AV, fenêtre contenant extremums, zéros et (0 ; f(0)) ;
     les écritures LaTeX de l'outil sont lues par une petite lecture écrite à la main (liste fermée de motifs) ;
   - **rédaction cible** : une vérification par décision, `xfail(strict=True)` avec la partie (P1 … P10), posée paramètre par paramètre
     seulement là où le test échoue aujourd'hui (vérifié avec `--runxfail` : toutes échouent par une assertion, aucune par une erreur du test).
4. `docs/chantiers/etude-complete/mesurer_temps.py` : temps natif de `etudier()` (processus neuf par mesure, médiane de 3).
5. Suite complète, puis commit « EC P0 : … » (audit, décisions, suivi, corpus, test, script de mesure).

### P1 (02.11.2026)

Tout se passe dans `derivee-variations/derivee_variations.py` (portée EC + Dérivée) ; le noyau (`ensemble_def.tex`, `num_sympy`) n'est pas
touché, pour ne pas changer les autres outils.
1. **D6** : `_simplifier` passe par `powsimp(combine='exp')`, puis chaque `exp(a)` devient `T^k` (T symbole muet par famille d'exposants
   proportionnels, k entier : `e^{2x} = T²` si `T = eˣ`), `factor`, puis on remet les exponentielles. Repli sur l'ancien calcul en cas
   d'erreur. Le remplacement est exact (a = k·w), donc aucun risque de valeur fausse.
2. **D7 parenthèses** : dans la ligne « u′v + uv′ » (ou « u′v − uv′ »), un facteur de droite négatif est écrit `Neg(…)`, que `tex`
   met entre parenthèses : `(x² − 6)(−2e^{−2x})`.
3. **D7 doublons** : une phrase de narration déjà écrite n'est pas répétée (« (eˣ)′ = eˣ » une seule fois pour c). Le « (x²)′ = 2x » parasite
   de Ex7 reste (P7a).
4. **D17** : (a) valeur exacte d'un extremum de la forme *entier × e^{−k}* (k constant > 0) : l'exponentielle reste au numérateur
   (`3e^{−6}`, pas `3/e⁶`) ; un coefficient non entier (−1/(2e)) garde l'écriture de SymPy ;
   (b) f′ = c·… avec c < 0 et un seul facteur somme non polynomial de puissance impaire ayant un terme négatif (eˣ − 3) : le signe y entre
   (`2(3 − eˣ)`) ; un facteur `e^{u}` seul passe devant le facteur somme qui le contient (`2eˣ(3 − eˣ)`). Les facteurs polynomiaux (x − 3)
   restent unitaires (R7), donc b garde −2 (comme le corrigé) ; −(e^{2x} + 1)e^{−x} reste tel quel (jamais −e^{2x} − 1).
5. Tests : retrait des xfail « P1 » du corpus ; `TestFormesDuCorrige` dans `test_derivee_narration.py` (justesse numérique de f′ sur une
   famille à exponentielles, une exponentielle par exposant, parenthèses, phrase unique, formes exactes et cas laissés tels quels) ;
   `test_isoler_atome.py` suit la nouvelle forme de ln(x)/x. Instantanés moteurs, `resoudre` et références de pages régénérés, listés sous
   « À relire » ; suite complète ; temps natif ; commit « EC P1 : … ».

## Temps natif de etudier() (s, médiane de 3 processus neufs)

| Partie | Ex7 | a | b | c | d |
|---|---|---|---|---|---|
| P0 | 0,59 | 0,02 | 0,42 | 0,18 | 0,30 |
| P1 | 0,63 | 0,02 | 0,42 | 0,19 | 0,30 |

## Suite complète

| Partie | Suite Python | Suite de pages | Date |
|---|---|---|---|
| P0 | 1052 passés, 66 xfail (659 s) | 116 passés (885 s) ; code de retour 0 | 02.11.2026 |
| P1 | 1062 passés, 61 xfail (641 s) | 116 passés (871 s) ; code de retour 0 (3ᵉ lancement, voir Écarts) | 03.11.2026 |

## Écarts acceptés

- P0 : le test du corpus est écrit en fonctions pytest (et non en `unittest.TestCase` comme les autres) : `parametrize` permet une marque xfail
  par fonction du corpus, donc de ne marquer que les cas qui échouent vraiment.
- P1 (D17) : b s'écrit `−2(x − 3)(x + 2)e^{−2x}` et non `−2e^{−2x}(x − 3)(x + 2)` comme le corrigé : déplacer l'exponentielle devant des
  facteurs polynomiaux changerait toutes les dérivées de la forme `P(x)·e^{u}` de l'outil Dérivée (x(x + 2)eˣ deviendrait xeˣ(x + 2)).
  L'exponentielle ne passe devant que le facteur somme qui la contient (c : `2eˣ(3 − eˣ)`).
- P1 (D7) : le facteur négatif est entre parenthèses, mais sans « · » : `(x² − 6)(−2e^{−2x})` (convention de `tex` pour un produit de
  parenthèses, déjà utilisée par l'outil : `(2x + 1)(6x − 12)`), et non `(x² − 6)·(−2e^{−2x})` comme decisions.md D7.
- P1 : **test instable hors chantier** `tests/pages/test_clavier.py::test_a_deux_formules…` (page Limites, qui ne charge pas l'outil Dérivée) :
  le premier appui sur « effacer » laisse parfois `(x^2-1)/(x-3)` dans le champ. Il a fait échouer les 2 premières suites complètes ; lancé seul,
  il échoue 2 fois sur 4 avec P1 et **2 fois sur 6 sur `HEAD` (P0, sans P1)** : défaut préexistant, non corrigé ici (aucun test affaibli).
  Le 3ᵉ lancement de la suite complète est vert (code de retour 0). À traiter dans un chantier « clavier » (cause non trouvée : sur 5 essais
  instrumentés, le toucher arrive bien au bouton).

## Questions pour l'enseignant

1. **Notation scientifique des valeurs approchées (P5, P7b)** : decisions.md §2 écrit `4,5·10⁻⁴` (2 chiffres significatifs, point médian) ; R13
   écrit `3,162 × 10⁻⁵` (×, 4 chiffres) et passe aussi en notation scientifique dès 10⁶ (decisions.md n'en dit rien). decisions.md dit « R13
   l'emporte » : c'est ce qui sera appliqué. Aucune valeur du corpus n'est concernée (le test d'arrondi refuse ce cas tant qu'il n'est pas tranché).
2. **Valeur approchée d'un entier exact** : (ln 3 ; 9) ≈ (1,10 ; 9) dans decisions.md §5 c ; j'en déduis qu'une valeur exacte entière s'écrit telle
   quelle (9, pas 9,00), y compris f(0) = 1, −6, 5. À confirmer.
3. **Critère §3 « AH visible »** : un x visible où |f(x) − L| < 5 % de la hauteur. Pris tel quel, il est satisfait par Ex7 grâce à la branche qui
   file vers 0 en 2⁻ (ce n'est pas l'AH). Le test cherche donc ce x **du côté de l'asymptote, au-delà de tous les points à montrer et des valeurs
   interdites**. Avec cette lecture, Ex7 échoue (P8) mais c passe, bien que l'audit dise que l'AH gauche de c ne se voit pas : la fenêtre de c va
   de −51 à 21 en y, et 5 % de la hauteur font 3,6. Faut-il un critère plus serré (par exemple 5 % de la valeur max |f| des points à montrer) ?
4. **« (x²)′ = 2x » parasite (D7)** : retiré pour Ex7 (la ligne n'a rien à voir avec u′, qui est un quotient). Dans a, b et d, la même ligne
   justifie u′ : elle n'est pas testée et reste. Le test est rattaché à P7a (réécriture de la dérivée de l'exposant) plutôt qu'à P1.

5. **P1, écriture −e^{−1} (D17)** : la règle « 3e^{−6} et non 3/e⁶ » est appliquée à tout extremum de la forme *entier × e^{−k}* :
   −1/e devient −e^{−1}, −3/e devient −3e^{−1}, 4/e² devient 4e^{−2} (outils Dérivée et EC). Un coefficient non entier garde l'écriture de
   SymPy (−1/(2e)). Faut-il garder 1/e et −1/e (coefficient ±1) en fraction ?
6. **P1, ln(x)/x (D17)** : la règle « signe dans le facteur non polynomial » donne aussi f′(x) = (1 − ln x)/x² au lieu de −(ln x − 1)/x²
   (une ligne « −1 » de moins dans le tableau de signes). La justification du zéro devient « 1 − ln(x) = 0 ⇔ ln(x) = 1 (on isole ln(x) du côté
   où son coefficient est positif) », phrase existante du moteur, au lieu de « (on ajoute 1) ». À relire.

## À relire par l'enseignant

- P0 : rien (aucun changement du moteur, aucun instantané modifié).
- **P1** (outil Dérivée, donc aussi EC). Instantanés modifiés : `tests/python/instantanes/{derivee-variations,etude-complete}.json`,
  `tests/python/instantanes/resoudre/{derivee-variations,etude-complete}.json`, `tests/pages/references/{derivee-variations,etude-complete}.json`.
  Aucun autre outil ne change (ED, Limites, Factorisation, Exp/Log : instantanés identiques).

  | Entrée | Avant | Après |
  |---|---|---|
  | `ln(x)/x` (Dérivée, EC) | f′(x) = −(ln(x) − 1)/x² ; tableau : lignes −1, (ln(x) − 1), x² ; « ln(x) − 1 = 0 ⇔ ln(x) = 1 (on ajoute 1) » | f′(x) = (1 − ln(x))/x² ; tableau : lignes (1 − ln(x)), x² ; « 1 − ln(x) = 0 ⇔ ln(x) = 1 (on isole ln(x) du côté où son coefficient est positif) » |
  | `x*ln(x)` (Dérivée, EC) | minimum : f(e^{−1}) = −1/e | f(e^{−1}) = −e^{−1} |
  | `3(x*ln(x))` (Dérivée, EC) | minimum : f(e^{−1}) = −3/e | f(e^{−1}) = −3e^{−1} |
  | `x*ln(x)+x` (Dérivée) | minimum : f(e^{−2}) = −1/e² | f(e^{−2}) = −e^{−2} |
  | `x^2*e^(-x)` (Dérivée, EC) | maximum : f(2) = 4/e² | f(2) = 4e^{−2} |

  Hors instantanés, sur le corpus (tests du chantier) : Ex7 f′ = x(x − 4)e^{(x² + x − 2)/(6x − 12)}/(6(x − 2)²) (avant : trois
  exponentielles e^{−2/(6x−12)}e^{x/(6x−12)}e^{x²/(6x−12)}, et trois lignes d'exponentielles dans le tableau) ; b : ligne
  « 2xe^{−2x} + (x² − 6)(−2e^{−2x}) » (avant « (x² − 6) · −2e^{−2x} ») et maximum 3e^{−6} (avant 3/e⁶) ; c : « (eˣ)′ = eˣ » écrit une fois
  (avant deux), f′ = 2eˣ(3 − eˣ) (avant −2(eˣ − 3)eˣ), tableau : lignes 2, eˣ, (3 − eˣ).
