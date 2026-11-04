# Chantier « Étude complète » — suivi

Refonte de l'outil Étude complète pour suivre le corrigé `docs/reference/etude-complete/3MSt_Ch8_EtudesFonctions_Corrige.tex` (exemple 7, exercice 8.15 a–d).
Branche `etude-complete`, créée le 02.11.2026 depuis `main` à jour (9716912, fusion de `correctif-explog-3c`). Rien n'est poussé ni fusionné.
Ordre de priorité : `CLAUDE.md` > `decisions.md` (validé par l'enseignant le 02.11.2026) > `audit-etape0.md`.
Un commit « EC P{N} : … » par partie ; suite complète verte (`python3 tests/lancer.py complet`, code de retour lu sans pipe) avant chaque commit.

**Détail déplacé dans [`journal.md`](journal.md) (04.11.2026)** : le « Résumé de la nuit (02–03.11.2026) », les « Plans »,
« Temps natif de etudier() », « Temps sous Pyodide (P9) », « Suite complète », « Écarts acceptés », les questions 1 à 56 (tranchées
par `decisions.md` §7, sauf 46, 50, 51 et 54, ⏸ à juger à l'écran sur les captures de P9, gardées ici) et les tableaux « À relire »
de P0 à P8 sont dans `journal.md` : les renvois de ce fichier vers ces sections (« plus bas », « voir Écarts », « voir Plans »,
« À relire, P0 »…) y mènent.

**Reprise après compactage (04.11.2026)** : chantier **à relire par l'enseignant** : P0 à P9, R1 et R2 commitées ; P10 non faite
(facultative) ; 1 xfail reste (P10) ; questions ouvertes : 46, 50, 51, 54 (⏸) et 57 à 83 ; rien n'est poussé ni fusionné. Ce
fichier est allégé : tout le détail (plans, temps, suites, écarts, questions tranchées, tableaux « À relire » de la nuit) est dans
`journal.md`, à lire seulement en cas de besoin. Reste hors parties : l'audit tests-rapides (non commité). Pour reprendre : lire le
« Résumé de la session 2 », `decisions.md`, puis `git log --oneline main..HEAD`.

**Reprise après compactage (nuit du 02–03.11)** : la nuit du 02–03.11.2026 est **terminée** (P0 à P5, P7a, P7b, P8 commitées ; résumé ci-dessous ;
rien n'est poussé ni fusionné). Prochaine étape : **relecture de l'enseignant** (questions « à trancher avant la fusion », instantanés
« À relire », texte rendu de l'Ex7), puis **P6** (partie 4, Limites : D12, D13, D16), puis **P9** (D18, D20, mesure Pyodide), P10
facultative. Pour reprendre : relire ce fichier, `decisions.md`, puis `git log --oneline main..HEAD` ; reprendre à la première partie
« reportée », après les réponses de l'enseignant.
Les tests du chantier sont dans `tests/python/test_corpus_etude_complete.py` (corpus : `tests/python/donnees/corpus_etude_complete.py`) ; chaque
vérification pas encore faite y est marquée `xfail` **strict** avec le numéro de sa partie (21 restent : P6, P9, P10) : la partie qui la
traite retire la marque (un xfail qui passe fait échouer la suite). Temps natif : `docs/chantiers/etude-complete/mesurer_temps.py`.

## Résumé de la session 2 (03–04.11.2026)

### Parties faites

Vérifié par `git log --oneline 67a3ca1..HEAD` (4 commits de parties, plus ce résumé ; rien n'est poussé ni fusionné). Au début de la
session, 21 xfail stricts restaient (P6 : 14, P9 : 6, P10 : 1).

| Partie | Commit | Contenu | D / Q traités | xfail retirés (restent) |
|---|---|---|---|---|
| R1 | e38278c | **Outil Dérivée** et EC : exposant de f′ écrit comme dans l'énoncé ; ligne des zéros « f′(x) = 0 ⇔ x(x − 4) = 0 (car e^{…} > 0) ⇔ x = 0 ou x = 4 (produit nul) » ; guide R11 et R7 (tableau u/v, ligne des zéros) ; verse la nouvelle version de `decisions.md` | Q37, Q56, Q32 | 0 (21) |
| R2 | 0acc931 | EC : partie 5 jamais vide (phrase « sort du cadre », carte d'erreur du signe) ; Somme-Produit en parties 1 et 3 ; ≈ dans la formule, séparateur ’ entre 1000 et 10⁶ ; tableau de f avec une ligne par facteur écrit ; ligne de calcul de chaque extremum ; « **Maximum global** » | Q7, Q11, Q15, Q23, Q28, Q41, Q43 | 0 (21) |
| P6 | 94168f8 | **Outil Limites** et EC (partie 4) : ordre −∞, valeurs interdites, +∞ ; x → ±∞ regroupés si les chaînes sont identiques ; valeur d'essai pour 0⁺ / 0⁻ ; 1⁺ / 1⁻ confirmé par une sonde ; côté et position de l'AH ; AV d'un seul côté avec le point exclu ; 0⁺ dans le bilan ; guide R6 | D12, D13 (sauf « pas d'AH à droite », question 67), D16 | 14 (7) |
| P9 | 72ff3bb | EC : Ex7 en exemple, a, c « difficile », b, d « très difficile » ; carte « Bilan de l'étude » avant le graphique, une ligne par résultat avec « (partie k) », sans calcul nouveau ; largeurs 320–1100 px ; mesure sous Pyodide ; 7 captures à 390 px | D18, D20 | 6 (1 : P10) |
| Entrée bloquante | (ce commit) | Diagnostic de e^x^x (et e^(e^x)), qui bloque l'étude plus de 120 s dans la sonde mpmath de l'outil Limites (défaut antérieur à la session) ; deux pistes proposées ; **aucune correction** | question 83 | — |

P10 (pente au point exclu, D14) n'est pas faite : exclue de la session (facultative).

### Commits

- e38278c — EC R1 : outil Dérivée, exposant de l'énoncé dans f′ (Q37), ligne des zéros (Q56), guide R11 (Q32)
- 0acc931 — EC R2 : partie 5 jamais vide (Q7), Somme-Produit (Q11), ≈ dans la formule et ’ (Q15, Q28), lignes du tableau de f (Q23),
  calcul de chaque extremum (Q41), « Maximum global » (Q43)
- 94168f8 — EC P6 : partie 4 (outil Limites et EC) : ordre et regroupement (D16), valeur d'essai (D12), signe d'approche, position, AV
  d'un seul côté, bilan (D13)
- 72ff3bb — EC P9 : Ex7 en exemple, a–d en exercices (D18), carte « Bilan de l'étude » (D20), largeurs, mesure sous Pyodide, captures
- (ce commit) — EC : résumé de la session 2 (suivi) ; contient aussi le hash de P9 dans le tableau « Parties », la ligne « P9 (contrôle
  du chef d'orchestre) » et la question 83

### Échecs

- **Aucun échec de partie** : les quatre parties sont faites et commitées.
- Premiers lancements rouges (corrigés avant le commit, voir « Écarts acceptés ») :
  - P6, 1ᵉʳ lancement de la suite de pages : 16 échecs de `test_graphique.py::test_traces_egales_aux_references`, tous e^(1/x) (ordre
    des asymptotes, D16) : `graphique-traces.json` régénéré (liste sous « À relire », P6) ;
  - P9, 1ᵉʳ lancement de la suite Python : 4 échecs (`test_P7b_extremums` pour a, b, c : le bilan doublait le compte de « global » ;
    `test_bilan_avec_la_liste_de_l_outil_derivee` : attente corrigée, « minimum local en … ») ; la suite de pages n'avait pas été lancée.
- Test instable **préexistant** `tests/pages/test_clavier.py::test_a_deux_formules…` (page Limites ; même symptôme chaque fois :
  « effacer » laisse `(x^2-1)/(x-3)`) : échec au contrôle du chef d'orchestre de R1 (ce test seul : 3 réussites sur 6), au 2ᵉ lancement
  de P6 par le sous-agent (5 sur 6 ; au 1ᵉʳ lancement de P6, il a passé), au contrôle de P9 (5 sur 6). Hors chantier (decisions.md §7).

Suites complètes de la session (détail : tableau « Suite complète » plus bas) :

| Partie | Suite Python | Suite de pages | Date |
|---|---|---|---|
| R1 | 1224 passés, 21 xfail (679 s) | 119 passés (908 s) ; code de retour 0 | 03.11.2026 |
| R1 (contrôle) | 1224 passés, 21 xfail (666 s) | 118 passés, 1 échec : `test_clavier` (seul : 3 sur 6) → R1 acceptée | 03.11.2026 |
| R2 | 1240 passés, 21 xfail (930 s) | 120 passés (1202 s) ; code de retour 0 | 03.11.2026 |
| R2 (contrôle) | 1240 passés, 21 xfail (917 s) | 120 passés (1199 s) ; code de retour 0 | 03.11.2026 |
| P6 | 1273 passés, 7 xfail (713 s) | 1ᵉʳ lancement : 16 échecs `test_graphique` ; 2ᵉ : 119 passés, 1 échec : `test_clavier` (seul : 5 sur 6) → P6 acceptée | 03.11.2026 |
| P6 (contrôle) | 1273 passés, 7 xfail (696 s) | 120 passés (929 s) ; code de retour 0 | 04.11.2026 |
| P9 | 1290 passés, 1 xfail (700 s ; 1ᵉʳ lancement : 4 échecs) | 121 passés (930 s) ; code de retour 0 | 04.11.2026 |
| P9 (contrôle) | 1290 passés, 1 xfail (708 s) | 120 passés, 1 échec : `test_clavier` (seul : 5 sur 6) → P9 acceptée | 04.11.2026 |
| Résumé (ce commit) | 1290 passés, 1 xfail (720 s) | 121 passés (940 s) ; code de retour 0 (1ᵉʳ lancement) | 04.11.2026 |

### Temps

Temps natif d'`etudier()` (s, médiane de 3 processus neufs ; tableau complet « Temps natif de etudier() » plus bas) :

| Partie | Ex7 | a | b | c | d |
|---|---|---|---|---|---|
| P8 (fin de la nuit) | 0,58 | 0,03 | 0,36 | 0,26 | 0,21 |
| R1 | 0,58 | 0,03 | 0,35 | 0,25 | 0,21 |
| R2 | 0,67 | 0,03 | 0,42 | 0,30 | 0,24 |
| P6 | 0,76 | 0,03 | 0,41 | 0,27 | 0,27 |
| P9 | 0,73 | 0,03 | 0,35 | 0,26 | 0,23 |

**Aucune hausse de plus de 50 % au-dessus de 0,1 s** (vérifié dans le tableau) : d'une partie à la suivante, la plus forte est + 20 %
(R2 : b 0,35 → 0,42 s, c 0,25 → 0,30 s ; bruit de la machine selon le rapport de R2, qui mesure R1 à 0,70 s pour Ex7 le même jour) ;
sur toute la session, Ex7 0,58 → 0,76 s au plus (+ 31 %, P6 : valeurs d'essai en 2⁻ et 2⁺), puis 0,73 s. a reste à 0,03 s (sous 0,1 s).

Temps sous Pyodide (P9, page réelle, Chrome sans interface, du clic sur « Calculer ▶ » à la dernière carte ; section « Temps sous
Pyodide (P9) » plus bas) :

| Fonction | Mesure 1 (s) | Mesure 2 (s) | Mesure 3 (s) | Médiane (s) |
|---|---|---|---|---|
| Ex7 | 1,89 | 1,87 | 1,88 | 1,88 |
| a | 0,51 | 0,51 | 0,55 | 0,51 |
| b | 1,53 | 1,54 | 1,53 | 1,53 |
| c | 1,34 | 1,34 | 1,28 | 1,34 |
| d | 1,22 | 1,23 | 1,30 | 1,23 |

Première mesure sous Pyodide (aucune hausse à comparer) ; le plus long, Ex7, 1,9 s, loin du délai de la page (45 s).

### Nouvelles questions (57 à 83) : index

Texte complet dans « Questions pour l'enseignant » plus bas.

**À lire en premier** :
- Q83 — entrée bloquante e^x^x : l'élève attend 45 s pour « Le calcul a pris trop de temps » ; piste (a) ou (b) ?
- Q67 — « Pas d'asymptote horizontale à droite (f(x) → +∞) » (D13) non écrit : R6 du guide et les tests de style l'interdisent
  (**écart avec decisions.md**, D13).
- Q59 — « (produit nul) » ajouté en fin de chaîne Somme-Produit (**écart avec l'exemple de §7**, Q11).
- Q64 — carte d'erreur « Signe de f′ et variations » ajoutée quand le signe n'est pas étudié (au-delà de Q7).
- Q60 — Somme-Produit limitée aux trinômes x² + bx + c (b ≠ 0, c ≠ 0, deux racines entières distinctes) (**écart avec §7**, Q11 :
  « tout trinôme unitaire à racines entières »).
- Q62 — chaîne de valeur d'un extremum : « −2(−2) » (**§7** : « −2·(−2) ») ; x₀ irrationnel : pas de ligne.
- Q68, Q69 — valeur d'essai (D12) non écrite pour les fractions rationnelles, pour un bas = x, un point irrationnel ou 1/3, un bas non
  polynomial (**écart avec D12**, « une seule règle pour l'EC et l'outil Limites »).
- Q70 — « Exposant : … Donc e^{…} → … » au lieu de « g(x) → 4/0⁻ = −∞, donc f(x) → 0⁺ » (**écart avec §4**).

**Toutes** :
- Q57 (R1) — ligne des zéros de f′ : constante et dénominateur retirés sans propriété ; ajouter « (numérateur nul) » ?
- Q58 (R1) — x^x non reconnu comme exponentielle (pas de « car x^x > 0 ») ; lignes de l'outil ED avant la ligne des zéros.
- Q59 (R2) — « (produit nul) » en fin de chaîne Somme-Produit.
- Q60 (R2) — portée de Somme-Produit (racine double, sans terme constant, non unitaire : outil ED).
- Q61 (R2) — ’ entre 1000 et 10⁶ dans les parties 3 et 5 ; contre-exemples de la partie 2 gardés dans [10⁻³ ; 1000[.
- Q62 (R2) — forme de la chaîne de valeur d'un extremum.
- Q63 (R2) — ligne « g(x₀) = … » gardée pour Ex7 et d ; g(0) répété.
- Q64 (R2) — carte d'erreur du signe de f′ non étudié.
- Q65 (R2) — « f(0) = e^{−1/2} ≈ 0,61 ≠ 0 » dans « Pas impaire ».
- Q66 (R2) — dénominateur factorisé en partie 1 : une seule ligne dans le tableau de f.
- Q67 (P6) — « pas d'AH à droite » non écrit (R6 du guide).
- Q68 (P6) — pas de valeur d'essai pour les fractions rationnelles (tableau de signes, R18).
- Q69 (P6) — autres cas sans valeur d'essai (bas = x, point irrationnel, bas non polynomial, 0/0).
- Q70 (P6) — mots de la valeur d'essai et de la descente.
- Q71 (P6) — position de l'AH seulement si le signe d'approche est démontré (pas pour e³, −1, fractions rationnelles).
- Q72 (P6) — « (rond vide) » aussi dans la page Limites, sans graphique.
- Q73 (P6) — bilan des asymptotes : position, 0⁺ / 0⁻, une ligne par côté ; autre côté « ? » : phrase d'avant.
- Q74 (P6) — ordre et regroupement D16 aussi pour les fractions rationnelles et tous les outils.
- Q75 (P9) — place du bilan (première carte de « 6. Graphe », style final).
- Q76 (P9) — forme des lignes du bilan (« (partie k) », mots d'entrée).
- Q77 (P9) — signe au bilan : ensembles écrits (écriture nouvelle) ou « voir le tableau de signes » ?
- Q78 (P9) — partie qui ne conclut pas : pas de ligne au bilan.
- Q79 (P9) — asymptotes reprises telles quelles (affichées deux fois) ; ronds vides absents du bilan.
- Q80 (P9) — extremums sans rédaction D11 : ligne de l'outil Dérivée.
- Q81 (P9) — niveaux des exercices (D18) ; Ex7 à la fin des exemples.
- Q82 (P9) — ce que mesure le temps sous Pyodide ; pas de mesure sur téléphone.
- Q83 (après P9) — entrée bloquante e^x^x, e^(e^x) (sonde mpmath ; défaut antérieur à la session) ; abs(x) : message trompeur, à voir
  à part.

### À relire par l'enseignant

Détail (tableaux avant / après) dans la section « À relire par l'enseignant » plus bas, sous R1, R2, P6, P9. **D'abord les outils
partagés** :
- **R1 (outil Dérivée, donc aussi EC)** : `tests/python/instantanes/{derivee-variations,etude-complete}.json`,
  `tests/python/instantanes/resoudre/{derivee-variations,etude-complete}.json`, `tests/pages/references/{derivee-variations,etude-complete}.json`
  (21 entrées de la Dérivée modifiées et 2 nouvelles, 11 de l'EC ; seule la ligne des zéros de f′ change) ; `docs/guide-redaction.md`
  (R7, R11, exemple 4).
- **P6 (outil Limites, donc aussi EC)** : `tests/python/instantanes/limites-asymptotes.json` (31 entrées sur 37),
  `tests/python/instantanes/resoudre/limites-asymptotes.json` (30 sur 37), `tests/pages/references/limites-asymptotes.json` (30 sur 38),
  `tests/pages/references/graphique-traces.json` (16 empreintes sur 48, e^(1/x)), `tests/python/instantanes/etude-complete.json` (12 sur
  18), `tests/python/instantanes/resoudre/etude-complete.json` (13 sur 18), `tests/pages/references/etude-complete.json` (11 sur 19) ;
  `docs/guide-redaction.md` (R6).
- R2 (EC seule) : `tests/python/instantanes/resoudre/etude-complete.json` et `tests/pages/references/etude-complete.json` (16 entrées
  modifiées, 1 nouvelle : 1/(x² − 3x + 2)) ; `tests/python/instantanes/etude-complete.json` (1 nouvelle, aucune modifiée).
- P9 (EC seule) : `tests/python/instantanes/resoudre/etude-complete.json` et `tests/pages/references/etude-complete.json` (18 entrées
  modifiées : la carte « Bilan de l'étude » seule ; 3 nouvelles : a, b, c) ; `tests/python/instantanes/etude-complete.json` (3
  nouvelles, aucune modifiée).

### Exemple 7 : texte rendu complet (sortie de resoudre_ec)

Sortie de `resoudre_ec.resoudre("e^((x^2+x-2)/(6x-12))")` générée sur 72ff3bb (HEAD, Python 3.12, SymPy 1.13.3), transcrite à la main
de la sortie JSON (LaTeX → écriture lisible) ; le contenu mathématique n'est pas changé. Mêmes conventions que la transcription de la
nuit : « [encadré] » : bloc résultat encadré ; les cartes « Étape k : … » de la partie 4 sont les étapes de la carte « Limite » qui les
précède.

Énoncé (en tête de la page) : f(x) = e^((x² + x − 2)/(6x − 12))

#### 1. Domaine de définition

- Carte « Fonction » [titre masqué] :
  - f(x) = e^((x² + x − 2)/(6x − 12))
- Carte « Mise en forme » :
  - x² + x − 2 = (x + 2)(x − 1) (Somme-Produit)
  - 6x − 12 = 6(x − 2) (mise en évidence)
  - On note g(x) = ((x + 2)(x − 1))/(6(x − 2)), donc f(x) = e^(g(x)).
- Carte « Condition 1 » [badge « dénominateur »] :
  - 6x − 12 ≠ 0
  - On résout 6x − 12 = 0 ⇔ 6x = 12 ⇔ x = 2.
- Carte « Ensemble de définition » :
  - **[encadré]** ED = ℝ ∖ {2}

#### 2. Parité

- Carte « Symétrie de l'ED » :
  - −2 ∈ ED, mais 2 ∉ ED : ED n'est pas symétrique par rapport à 0.
  - Donc **f n'est ni paire ni impaire**.

#### 3. Zéros, signe, ordonnée à l'origine

- Carte « Zéros et signe de f » :
  - e^(g(x)) > 0 pour tout x ∈ ED (une exponentielle est strictement positive).
  - Donc f n'a pas de zéro et f(x) > 0 sur ED.
- Carte « Ordonnée à l'origine » :
  - g(0) = (−2)/(−12) = 1/6, donc f(0) = e^(1/6) ≈ 1,18.
  - Le graphe coupe l'axe des y au point (0 ; e^(1/6)).

#### 4. Limites et asymptotes

- Carte « Limite (x → −∞) » [badge « limite »] :
  - lim_(x → −∞) e^((x² + x − 2)/(6x − 12))
- Carte « Étape 1 : limite de l'exposant, à part. » :
  - Haut : x² + x − 2 → +∞. Bas : 6x − 12 → −∞. Forme +∞/−∞ : indéterminée.
  - Encadré « Prédiction avec la règle du podium » :
    - En haut x², en bas x : la plus grande puissance est au **haut**, donc l'exposant part vers l'infini.
    - Signe : haut > 0, bas < 0, donc −∞.
    - **On s'attend à :** exposant → −∞, donc e^(⋯) → 0⁺
  - Calcul avec BH :
  - lim_(x → −∞) (x² + x − 2)/(6x − 12) =(BH) lim_(x → −∞) (2x + 1)/6 = −∞
- Carte « Étape 2 : on applique l'exponentielle. » :
  - **[encadré]** lim_(x → −∞) e^((x² + x − 2)/(6x − 12)) = e^(−∞) = 0⁺
  - ✓ Le calcul confirme la prédiction du podium.
  - Asymptote horizontale : y = 0 (à gauche). f(x) → 0⁺ : le graphe est au-dessus.
- Carte « Limite (x → 2) » [badge « limite »] :
  - lim_(x → 2⁻) e^((x² + x − 2)/(6x − 12))
- Carte « Étape 1 : on remplace. » :
  - Haut de l'exposant : x² + x − 2 → 2² + 2 − 2 = 4 (pas 0, donc pas indéterminée).
  - Bas de l'exposant : 6x − 12 → 0 ; avec x = 1,99 : 6 · 1,99 − 12 = −0,06 < 0, donc 0⁻.
  - Exposant : (x² + x − 2)/(6x − 12) → 4/0⁻ = −∞. Donc e^((x² + x − 2)/(6x − 12)) → e^(−∞) = 0⁺.
  - **[encadré]** lim_(x → 2⁻) e^((x² + x − 2)/(6x − 12)) = 0⁺
- Carte « Limite (x → 2) » [badge « limite »] :
  - lim_(x → 2⁺) e^((x² + x − 2)/(6x − 12))
- Carte « Étape 1 : on remplace. » :
  - Haut de l'exposant : x² + x − 2 → 2² + 2 − 2 = 4 (pas 0, donc pas indéterminée).
  - Bas de l'exposant : 6x − 12 → 0 ; avec x = 2,01 : 6 · 2,01 − 12 = 0,06 > 0, donc 0⁺.
  - Exposant : (x² + x − 2)/(6x − 12) → 4/0⁺ = +∞. Donc e^((x² + x − 2)/(6x − 12)) → e^(+∞) = +∞.
  - **[encadré]** lim_(x → 2⁺) e^((x² + x − 2)/(6x − 12)) = +∞
  - Asymptote verticale : x = 2, seulement du côté droit. À gauche, f(x) → 0⁺ : le graphe s'approche du point (2 ; 0), qui
    n'appartient pas au graphe (rond vide).
- Carte « Limite (x → +∞) » [badge « limite »] :
  - lim_(x → +∞) e^((x² + x − 2)/(6x − 12))
- Carte « Étape 1 : limite de l'exposant, à part. » :
  - Haut : x² + x − 2 → +∞. Bas : 6x − 12 → +∞. Forme +∞/+∞ : indéterminée.
  - Encadré « Prédiction avec la règle du podium » :
    - En haut x², en bas x : la plus grande puissance est au **haut**, donc l'exposant part vers l'infini.
    - Signe : haut > 0, bas > 0, donc +∞.
    - **On s'attend à :** exposant → +∞, donc e^(⋯) → +∞
  - Calcul avec BH :
  - lim_(x → +∞) (x² + x − 2)/(6x − 12) =(BH) lim_(x → +∞) (2x + 1)/6 = +∞
- Carte « Étape 2 : on applique l'exponentielle. » :
  - **[encadré]** lim_(x → +∞) e^((x² + x − 2)/(6x − 12)) = e^(+∞) = +∞
  - ✓ Le calcul confirme la prédiction du podium.
- Carte « Bilan des asymptotes » :
  - Liste :
    - Asymptote horizontale (x → −∞) : y = 0, graphe au-dessus
    - Asymptote verticale : x = 2 (lim_(x → 2⁻) f(x) = 0⁺ ; lim_(x → 2⁺) f(x) = +∞)

#### 5. Dérivée, tableau de variation, extremums

- Carte « Dérivée » [badge « calcul »] :
  - f(x) = e^(g(x)) avec g(x) = (x² + x − 2)/(6x − 12), donc f′(x) = g′(x) · e^(g(x)) (dérivée d'une composée). On calcule d'abord g′(x).
  - Sous-carte « Dérivée de l'exposant » :
    - Étape 1 : règle du quotient.
      - On applique la règle du quotient, (u/v)′ = (u′v − uv′)/v², avec :
      - Tableau u / v :

        | u = x² + x − 2 | v = 6x − 12 |
        |---|---|
        | u′ = 2x + 1 | v′ = 6 |

      - g′(x) = ((2x + 1)(6x − 12) − (x² + x − 2) · 6)/(6x − 12)² (règle du quotient)
    - Étape 2 : calcul du numérateur, puis simplification.
      - g′(x) = (12x² − 24x + 6x − 12 − 6x² − 6x + 12)/(36(x − 2)²) (développement)
      - = (6x² − 24x)/(36(x − 2)²) (réduction)
      - = (6x(x − 4))/(36(x − 2)²) (mise en évidence)
      - = (x(x − 4))/(6(x − 2)²) (simplification par 6)
  - On remplace g′(x) dans f′(x) = g′(x) · e^(g(x)) :
  - **[encadré]** f′(x) = (x(x − 4)e^((x² + x − 2)/(6x − 12)))/(6(x − 2)²)
- Carte « Signe de f' et variations » [badge « tableau »] :
  - f′(x) = 0 ⇔ x(x − 4) = 0 (car e^((x² + x − 2)/(6x − 12)) > 0) ⇔ x = 0 ou x = 4 (produit nul) ; valeur interdite : x = 2.
  - Tableau de signes et de variations :

    | x | −∞ |  | 0 |  | 2 |  | 4 |  | +∞ |
    |---|---|---|---|---|---|---|---|---|---|
    | 1/6 |  | + | + | + | ‖ | + | + | + |  |
    | x |  | − | 0 | + | ‖ | + | + | + |  |
    | (x − 4) |  | − | − | − | ‖ | − | 0 | + |  |
    | e^((x² + x − 2)/(6x − 12)) |  | + | + | + | ‖ | + | + | + |  |
    | (x − 2)² |  | + | + | + | ‖ | + | + | + |  |
    | **f′(x)** |  | + | 0 | − | ‖ | − | 0 | + |  |
    | **f(x)** | 0⁺ | ↗ | e^(1/6) | ↘ | 0⁺ ‖ +∞ | ↘ | e^(3/2) | ↗ | +∞ |

  - g(0) = (−2)/(−12) = 1/6, donc f(0) = e^(1/6) ≈ 1,18.
  - g(4) = 18/12 = 3/2, donc f(4) = e^(3/2) ≈ 4,48.
  - Liste des extremums :
    - **Maximum local** en x = 0 : (0 ; e^(1/6)) ≈ (0 ; 1,18) (f′ passe de + à −). Pas global : f(x) → +∞ quand x → 2⁺.
    - **Minimum local** en x = 4 : (4 ; e^(3/2)) ≈ (4 ; 4,48) (f′ passe de − à +). Pas global : f(x) → 0⁺ quand x → −∞.

#### 6. Graphe

- Carte « Bilan de l'étude » [style final, cadre vert] :
  - Liste :
    - ED = ℝ ∖ {2} (partie 1)
    - Parité : f n'est ni paire ni impaire (partie 2)
    - Zéros : aucun (partie 3)
    - Signe : f(x) > 0 sur ED (partie 3)
    - Ordonnée à l'origine : f(0) = e^(1/6) ≈ 1,18 (partie 3)
    - Asymptote horizontale (x → −∞) : y = 0, graphe au-dessus (partie 4)
    - Asymptote verticale : x = 2 (lim_(x → 2⁻) f(x) = 0⁺ ; lim_(x → 2⁺) f(x) = +∞) (partie 4)
    - **Maximum local** en x = 0 : (0 ; e^(1/6)) ≈ (0 ; 1,18) (partie 5)
    - **Minimum local** en x = 4 : (4 ; e^(3/2)) ≈ (4 ; 4,48) (partie 5)
- Carte « Graphique » :
  - Graphique : fenêtre x de −9,625 à 6, y de −1,40 à 7,00 ; courbe en deux morceaux (de part et d'autre de x = 2, tracés de −25,1 à
    1,89 et de 2,08 à 21,5) ; en pointillé, AH y = 0 (x → −∞, graphe au-dessus) et AV x = 2 (à gauche → 0⁺, à droite → +∞) ; points
    pleins : maximum (0 ; 1,18), qui est aussi (0 ; f(0)), et minimum (4 ; 4,48) ; aucun zéro ; rond vide en (2 ; 0).
  - Texte d'aide : Courbe (trait plein), asymptotes (pointillé), extremums, zéros et point (0 ; f(0)) (points pleins), points exclus du
    graphe (ronds vides). Molette ou boutons pour zoomer, cliquer-glisser pour déplacer.

#### Écarts restants avec la cible (decisions.md §4)

Résorbés depuis la nuit : ligne des zéros de f′ (Q56, R1) ; ordre −∞, 2⁻, 2⁺, +∞ (D16) ; valeur d'essai en 2⁻ et 2⁺ (D12) ; AH « (à
gauche) … le graphe est au-dessus », AV « seulement du côté droit » et point (2 ; 0) exclu, 0⁺ au bilan (D13) ; carte « Bilan de l'étude »
(D20) ; Ex7 dans les exemples de la page (D18).

Ouverts (à trancher) :
- Partie 4, x → 2⁻ et 2⁺ : « Exposant : … → 4/0⁻ = −∞. Donc e^(…) → e^(−∞) = 0⁺. » au lieu de « g(x) → 4/0⁻ = −∞, donc f(x) → 0⁺ »
  (l'outil Limites ne nomme pas g) → question 70 ; ligne du haut « 2² + 2 − 2 = 4 » (§4 : « 4 + 2 − 2 = 4 »).
- Partie 4, x → 2⁻ : pas de « Pas d'AV à gauche » après 2⁻ ; la conclusion de l'AV d'un seul côté (point (2 ; 0), rond vide) est écrite
  une fois, après x → 2⁺ (noté sous « À relire », P6 ; pas de question numérotée).
- Partie 4, x → +∞ : pas de « (pas d'AH à droite) » → question 67.
- Pente au point exclu (D14) → P10, non faite.

Acceptés par decisions.md §7 (rappel) : partie 3 « Le graphe coupe l'axe des y au point (0 ; e^(1/6)) » au lieu de « Point (0 ;
e^(1/6)) » (Q27) ; partie 5 f′ encadré avec l'exposant écrit en entier, et non « x(x − 4)/(6(x − 2)²) · e^(g(x)) » (Q34), g(x) écrit
développé dans la carte « Dérivée » (Q35), ligne g(0) répétée (Q41), ordre des lignes du tableau (e^(…) avant (x − 2)²) et libellé
e^((x² + x − 2)/(6x − 12)) plutôt que e^(g(x)) (D9) ; partie 6 carte « Graphique » sous l'intertitre « 6. Graphe » (Q8), fenêtre x de
−9,625 à 6 (.tex : −8 à 10 ; Q49). La forme des lignes du bilan (absent du .tex) : questions 75 à 79.

### Captures de P9

PNG à 390 px de large, page entière, corrigé complet (« Tout afficher ») ; détail sous « Temps sous Pyodide (P9) ». À juger à l'écran
(points ⏸ de decisions.md §7 : Q46, Q50, Q51, Q54) :

| Fichier | Fonction | Point ⏸ à juger |
|---|---|---|
| `docs/chantiers/etude-complete/captures/Ex7-390.png` | e^((x² + x − 2)/(6x − 12)) | Q50 (échelle égale), Q51 (branche infinie en 2⁺ coupée en y), Q54 (étiquettes des points) ; carte « Bilan de l'étude » |
| `docs/chantiers/etude-complete/captures/a-390.png` | e^(−x²) | Q50 (fenêtre large et plate) |
| `docs/chantiers/etude-complete/captures/b-390.png` | (x² − 6)e^(−2x) | Q51 (branche vers +∞ en −∞ coupée), Q54 (étiquettes des zéros ±√6) |
| `docs/chantiers/etude-complete/captures/c-390.png` | eˣ(6 − eˣ) | Q50, Q51 (branche vers −∞ en +∞), Q54 (étiquette du zéro ln 6) |
| `docs/chantiers/etude-complete/captures/d-390.png` | e^(2/(x² − 4)) | Q46 (le tableau de variations défile à 390 px), Q51 (deux AV) |
| `docs/chantiers/etude-complete/captures/e1x-390.png` | e^(1/x) | Q50, Q51 (branche en 0⁺), AH y = 1 des deux côtés (position) |
| `docs/chantiers/etude-complete/captures/x1-390.png` | x/(x² + 1) | Q50 (fenêtre plate : max et min à ±0,5), Q54 (zéro et (0 ; f(0)) confondus) |

### Fusion

À lancer par l'enseignant **seulement après relecture** (rien n'est poussé ni fusionné) :

```
git switch main && git merge --no-ff etude-complete
```

Fichier modifié non commité qui ne fait pas partie du chantier : `CLAUDE.md` (modifié par l'enseignant : paragraphe « Fiche de chantier :
suivi.md reste court … journal.md »), laissé tel quel dans l'arbre. Avant la fusion, restent aussi l'audit tests-rapides (non commité)
et l'allègement de ce fichier vers `journal.md` (commit séparé).

## Parties

| Partie | Contenu (decisions.md §6) | Touche | État | Commit |
|---|---|---|---|---|
| P0 | `suivi.md`, corpus + oracle mpmath, xfail marqués avec leur partie | tests | **fait** | 5eadf34 |
| P1 | D6, D7 (parenthèses, doublons), D17 | Dérivée | **fait** | edf17c3 |
| P2 | Squelette des 6 parties titrées (D1), spécification (D2, D19) | EC | **fait** | 4cf3e9e |
| P3 | Partie 1 : mise en forme + ED détaillé (D3) | EC | **fait** | f108f7f |
| P4 | Partie 2 : parité (D4) | EC | **fait** | 62781a8 |
| P5 | Partie 3 : zéros, signe, f(0) (D5) | EC | **fait** | 8fc2fa2 |
| R1 | Corrections après relecture, outil Dérivée : Q37, Q56, Q32 (§7) | Dérivée | **fait** | e38278c |
| R2 | Corrections après relecture, EC : Q7, Q11, Q15, Q23, Q28, Q41, Q43 (§7) | EC | **fait** | 0acc931 |
| P6 | Partie 4 : D12, D13, D16 | Limites | **fait** | 94168f8 |
| P7a | Dérivée de l'exposant détaillée, tableau u/v (D7, D8, D7b si simple) | Dérivée | **fait** | 1799fff |
| P7b | Valeurs dans le tableau de variations (D10), extremums (D11) | EC + Dérivée | **fait** | cfe88de |
| P8 | Graphe (D15, §3) | EC | **fait** | 3ece3c9 |
| P9 | Exemples (D18), Bilan (D20), instantanés, largeurs 320–390 px, mesure Pyodide | EC | **fait** | 72ff3bb |
| P10 | *(facultatif)* Pente au point exclu (D14) | EC | reportée (hors de la nuit du 02.11) | |

## Questions pour l'enseignant

46. **P7b, largeur** : à 390 px, le tableau de d défile maintenant (voir Écarts) ; les valeurs exactes sont gardées (repli du composant
    commun plutôt qu'une écriture ≈ dans le tableau). Vous convient-il ?

50. **P8, échelle égale en x et en y** (graphique de T19) : pour une AH approchée lentement (en 1/x), l'élargissement rend la fenêtre
    large et plate : e^(1/x) x de −11 à 10, x/(x² + 1) de −10 à 10, (e^x − 1)/x de −7,8 à 2. Le .tex n'est pas à échelle égale.
    Gardez-vous l'échelle égale (le zoom compense) ?
51. **P8, ordonnées : branches coupées** : la hauteur de la fenêtre suit les points à montrer (extremums, zéros, f(0), ronds, AH) ; une
    branche qui file vers ±∞ sort du cadre (comme « restrict y to domain » du .tex). e^(2x) : y de −0,5 à 2,5 (avant −2,75 à 13,73) ;
    x⁴ − 2x² : −1,5 à 1,5 (avant −2,24 à 5,22) ; √(x² − 4) : −0,5 à 1,5. À relire à l'écran.
54. **P8, coordonnées écrites à côté des zéros et de (0 ; f(0))** : comme pour les extremums (« (−2,45 ; 0) », « (0 ; −6) ») ; la
    figure du .tex ne les écrit pas. Dans la vue d'ensemble de b (y de −143 à 61), les étiquettes se chevauchent près de l'origine
    (le zoom les sépare). Les garder ?

57. **R1, ligne des zéros de f′ (Q56)** : écrite comme l'exemple de §7, « f′(x) = 0 ⇔ x(x − 4) = 0 (car e^{…} > 0) ⇔ … » : f′ n'est
    pas réécrite (elle est encadrée juste au-dessus, dans la carte « Dérivée ») ; la constante (1/6, −2) et le dénominateur
    (6(x − 2)²) sont retirés **sans** propriété, alors que la partie 3 de l'EC écrit « (numérateur nul ; on divise par …) » ; un
    facteur du numérateur qui ne s'annule pas et qui n'est pas une exponentielle (x² + 1, x^x) reste dans le produit, sans raison
    (option qui affiche le moins). Faut-il ajouter « (numérateur nul) » et « on divise par … » comme en partie 3 ?
58. **R1, x^x** : x^x n'est pas reconnu comme une exponentielle (il s'écrit e^{x ln x}) : « f′(x) = 0 ⇔ x^x(ln(x) + 1) = 0 ⇔ ln(x)
    + 1 = 0 ⇔ x = e^{−1} », sans « (car x^x > 0) ». Les lignes d'explication de l'outil ED (« ln(x) + 1 = 0 ⇔ ln(x) = −1 (on
    soustrait 1) ») restent **avant** la ligne des zéros, comme avant R1 (x ln x, ln(x)/x, c). À garder ?

59. **R2, Q11, « (produit nul) » en fin de chaîne** : §7 écrit « x² − 3x + 2 = 0 ⇔ (x − 1)(x − 2) = 0 (Somme-Produit) ⇔ x = 1 ou
    x = 2 », sans propriété à la dernière étape ; la ligne des zéros de f′ (Q56, même page) écrit « ⇔ x = 0 ou x = 4 (produit nul) ».
    Une seule règle a été prise pour les parties 1, 3 et 5 : « … (Somme-Produit) ⇔ x = 1 ou x = 2 (produit nul) ». À retirer ?
60. **R2, Q11, portée** : Somme-Produit pour un dénominateur x² + bx + c (unitaire, b ≠ 0, c ≠ 0, deux racines entières distinctes).
    Restent à l'outil ED : racine double (x² − 2x + 1), sans terme constant (x² − 4x, qui se ferait par mise en évidence), non
    unitaire (2x² − 6x + 4) ; ax² + c garde « x² − 4 = 0 ⇔ x² = 4 ⇔ … » (§2 b, d). La partie 3 garde la mise en évidence avant
    Somme-Produit (2x² − 6x + 4 = 2(x² − 3x + 2) = 2(x − 1)(x − 2)). Faut-il étendre la partie 1 (racine double, mise en évidence) ?
61. **R2, Q28 et Q19** : les valeurs approchées entre 1000 et 10⁶ s'écrivent maintenant avec ’ (≈ 1’234,57) dans les parties 3 et 5 ;
    la partie 2 garde ses contre-exemples dans [10⁻³ ; 1000[ (Q19 confirmé : une valeur au-delà fait passer au a suivant). Faut-il
    accepter aussi les contre-exemples entre 1000 et 10⁶ ?
62. **R2, Q41, forme de la chaîne** : une ligne, comme l'exemple de §7 : substitution (x₀ entre parenthèses s'il est négatif ou
    fractionnaire), puis puissances, produits et quotients de nombres calculés (avec e^{ln q} = q, ln(e^{q}) = q, e⁰ = 1, 1·a = a,
    0·a = 0), puis les sommes, puis l'écriture de l'extremum (celle du tableau) : b « f(−2) = ((−2)² − 6)e^{−2(−2)} = (4 − 6)e⁴ = −2e⁴
    ≈ −109,20 » (l'outil écrit −2(−2), §7 −2·(−2)) ; a « f(0) = e^{−0²} = 1 » ; ln(x)/x « f(e) = ln(e)/e = 1/e = e^{−1} ≈ 0,37 ».
    Pas de propriété entre parenthèses (comme §7). x₀ irrationnel (3 ± 2√2, (3 ± √3)/3) : pas de ligne (option qui affiche le moins).
    Les lignes de calcul sont toutes avant la liste des extremums (comme P7b). À relire à l'écran (P9).
63. **R2, Q41, Ex7 et d** : la ligne « g(x₀) = …, donc f(x₀) = … » (P7b) est gardée quand g est nommé et x₀ entier ; sinon la
    substitution. g(0) reste répété (accepté par Q41).
64. **R2, Q7, signe de f′ non étudié** : en plus de la phrase « sort du cadre » (Q7), la carte d'erreur « Signe de f′ et variations »
    de l'outil Dérivée est maintenant affichée quand la dérivée est calculée mais pas son signe (CLAUDE.md : un résultat non traité
    donne un message clair ; avant R2, l'EC n'affichait rien). Aucune entrée de la page ni du corpus n'est concernée.
65. **R2, Q15, f(0) non entier dans « Pas impaire »** : « f(0) = e^{−1/2} ≈ 0,61 ≠ 0 » (une formule) au lieu de « f(0) = e^{−1/2} ≠ 0
    (≈ 0,61) ». Aucune entrée de la page ni du corpus n'est concernée.
66. **R2, Q23, dénominateur** : les lignes du tableau de f suivent la factorisation écrite dans la **chaîne de la partie 3** (le
    numérateur) ; un dénominateur factorisé en partie 1 (1/(x² − 3x + 2) : (x − 1)(x − 2), Somme-Produit) garde une ligne
    x² − 3x + 2 (option qui affiche le moins). Faut-il aussi une ligne par facteur du dénominateur ?

67. **P6, D13 « Pas d'asymptote horizontale à droite (f(x) → +∞) »** : **non écrit**. Le guide de rédaction (R6) supprime « La
    limite est infinie : pas d'asymptote horizontale » et CLAUDE.md impose le guide (CLAUDE.md > decisions.md) ; les tests de style
    (`test_redaction_limites.py`, `test_doctrine_bh.py`, `test_phrases_interdites`) interdisent « pas d'asymptote horizontale »
    partout. Option qui affiche le moins, sans affaiblir ces tests. Faut-il modifier R6 et la liste des phrases interdites pour écrire
    cette ligne en chaque borne infinie (D13) ?
68. **P6, D12 et fractions rationnelles** : la valeur d'essai est écrite dans la rédaction descendante (fonctions transcendantes,
    les deux outils) ; les fractions rationnelles gardent leur justification par le tableau de signes (« x − 3 < 0 : cf. tableau de
    signes », R18 du guide des limites 3M ; (x² − 1)/(x − 3), 1/(x² − 3x + 2) dans l'EC). Faut-il la valeur d'essai aussi pour elles ?
69. **P6, D12, cas sans valeur d'essai** (écriture d'avant, « x² − 5 → 0⁻ ») : bas = x (« x → 0⁻ » se lit directement : e^(1/x)),
    point irrationnel (±√5 de e^(−2x/(x² − 5))) ou sans écriture décimale finie (1/3), bas non polynomial (eˣ − 1, ln x), forme
    0/0 (BH ensuite : le signe du 0 ne décide rien). À confirmer.
70. **P6, D12, mots** : « Haut de l'exposant : x² + x − 2 → 2² + 2 − 2 = 4 (pas 0, donc pas indéterminée). » · « Bas de l'exposant :
    6x − 12 → 0 ; avec x = 1,99 : 6 · 1,99 − 12 = −0,06 < 0, donc 0⁻. » · « Exposant : (x² + x − 2)/(6x − 12) → 4/0⁻ = −∞. Donc
    e^{…} → e^{−∞} = 0⁺. » (§4 écrit « g(x) → 4/0⁻ = −∞, donc f(x) → 0⁺ » : l'outil Limites ne nomme pas g). Hors d'un exposant
    (ln(x² − 4x)/(x − 5)) : seule la ligne « Bas : … » reçoit la valeur d'essai. Point d'essai : a ± 0,01, plus près si un autre zéro
    du bas ou une borne de l'ED est entre les deux (jusqu'à 10⁻⁶), sinon l'écriture d'avant.
71. **P6, D13, position et côté de l'AH** : la position n'est écrite que si le signe d'approche est démontré par la rédaction
    descendante : 0⁺ / 0⁻ (règles, puis sonde du signe de f) et 1⁺ / 1⁻ (e^{0±}, sonde du signe de f − 1). Pas de position pour
    e³ (e^((3x + 4)/(x − 2))), −1 ((eˣ + 1)/(eˣ − 1)), x²e^(−x) en +∞ (ancienne rédaction, « = 0 » sans signe), ni pour les
    fractions rationnelles (« Asymptote horizontale : y = 0. », sans « (à gauche) », R18). Faut-il étendre (ℓ⁺ / ℓ⁻ quelconque,
    fractions rationnelles) ?
72. **P6, D13, « (rond vide) » dans l'outil Limites** : la phrase de l'AV d'un seul côté est la même dans les deux outils (portée
    EC + Limites), « rond vide » compris, alors que la page Limites n'a pas de graphique. À garder ?
73. **P6, D13, bilan** : « Asymptote horizontale (x → −∞) : y = 0, graphe au-dessus » (position démontrée seulement) ; limites
    latérales des AV avec 0⁺ / 0⁻ ; une ligne par côté (pas de « ±∞ » dans le bilan). L'autre côté d'une AV non déterminé (« ? ») :
    phrase d'avant « (du côté droit) ; à gauche, … » (sans « seulement » : une limite inconnue pourrait être infinie).
74. **P6, D16, regroupement des fractions rationnelles** : la règle « chaînes identiques au symbole près » regroupe aussi 1/x²,
    1/(x² − 2), (2x² + 1)/(x² − 1) (outil Limites) et x⁴ − 2x² (EC). L'ordre −∞, valeurs interdites, +∞ vaut pour tous les
    outils et pour le bilan ((x² − 1)/(x − 3) : oblique en −∞, AV x = 3, oblique en +∞). À confirmer.

75. **P9, D20, place du bilan** : « à la fin, avant le graphe » ; D1 garde six intertitres, donc la carte « Bilan de l'étude » est la
    première carte de « 6. Graphe », juste avant « Graphique » (et non un 7ᵉ intertitre, ni la fin de la partie 5). Style `final`
    (cadre vert, celui du résultat final des autres outils ; l'EC n'en avait pas). À garder ?
76. **P9, D20, « chaque ligne renvoie au résultat de sa partie »** : lu comme « (partie k) » à la fin de chaque ligne, avec un mot
    d'entrée régulier : « ED = … », « Parité : f n'est ni paire ni impaire », « Zéros : aucun » ou « Zéros : x = −√6 ≈ −2,45 ; x = √6
    ≈ 2,45 », « Signe : … », « Ordonnée à l'origine : f(0) = e^{1/6} ≈ 1,18 » (« aucune, car 0 ∉ ED »), les lignes du bilan des
    asymptotes telles quelles, « **Maximum local** en x = 0 : (0 ; e^{1/6}) ≈ (0 ; 1,18) » (sans « (f′ passe de + à −) » ni la raison
    de « global » / « pas global ») ; aucun extremum : « Aucun extremum local » (phrase de la partie 5). À relire à l'écran (captures).
77. **P9, D20, signe** : sans tableau, « Signe : f(x) > 0 sur ED » (phrase de la partie 3) ; avec tableau, les ensembles lus dans la
    ligne f(x) confirmée, écrits comme l'ED, le positif d'abord : b « f(x) > 0 sur ]−∞ ; −√6[ ∪ ]√6 ; +∞[ ; f(x) < 0 sur ]−√6 ; √6[ » ;
    x²e^(−x) « f(x) > 0 sur ℝ ∖ {0} » ; une borne fermée de l'ED où f ne s'annule pas est incluse ([a ; …[). Écriture nouvelle pour
    l'élève (la partie 3 n'a que le tableau) : la garder, ou écrire « voir le tableau de signes » ?
78. **P9, D20, partie qui ne conclut pas** (doute, message, SymPy absent, repli) : sa ligne n'est pas écrite (option qui affiche le
    moins) ; aucune entrée de la page ni du corpus n'est concernée. Faut-il plutôt une ligne « Parité : non établie (partie 2) » ?
79. **P9, D20, asymptotes** : les lignes de la carte « Bilan des asymptotes » de la partie 4 sont reprises telles quelles (la page les
    montre donc deux fois) : AH une ligne par côté (d : deux lignes y = 1, règle de Q73), « Trou », « Bord du graphe », « Pas de
    limite », « branche parabolique » compris ; sans asymptote : « Aucune asymptote détectée » (phrase de l'outil Limites, sans le
    point). Les ronds vides (partie 6) ne sont pas au bilan (D20 ne les cite pas). À garder ?
80. **P9, D20, extremums sans rédaction D11** (repli, aucune entrée concernée) : la ligne de la liste de l'outil Dérivée (« minimum
    en x=2 : f(2)=−1 »), telle que la carte l'affiche. À garder ?
81. **P9, D18, niveaux** : a (e^(−x²)) et c (eˣ(6 − eˣ)) en « difficile » (une exponentielle, un extremum) ; b ((x² − 6)e^(−2x)) et d
    (e^(2/(x² − 4))) en « très difficile » (deux extremums, ou deux AV et quatre limites latérales) ; Ex7 ajouté **à la fin** des
    exemples (le premier exemple, (x² − 1)/(x − 3), reste : c'est celui du balayage des largeurs de toutes les pages). Les poids des
    niveaux ne changent pas (difficile 0,2, très difficile 0,1). À confirmer.
82. **P9, mesure Pyodide** : temps compté du clic à la dernière carte (toutes les cartes sont écrites d'un coup, puis montrées une à une
    par « Étape suivante ») ; le chargement de Pyodide n'est pas compté, et la fin du dessin du graphique (canvas) n'est pas
    attendue. Ex7 1,9 s, a 0,5 s, b 1,5 s,
    c 1,3 s, d 1,2 s : rien près de 30 s. Mesure du temps sur un téléphone : non faite (navigateur des tests seulement).
83. **Entrée bloquante (après P9, rien corrigé) : e^x^x**, lu e^(x^x). Le script d'essai de l'enseignant (arrêté après 1 h 44) a été
    relancé une entrée par processus, limite 120 s (même Python que les tests) : abs(x) 1,7 s (erreur « Symbole inconnu « a ». La
    variable s'appelle x ; … » : message trompeur pour abs, à voir à part), x^(x^2) 1,1 s, ln(ln(x)) 0,9 s, sqrt(x)^x 1,0 s,
    **e^x^x > 120 s, arrêtée**, (x^2+1)^x 1,4 s, log(x) 0,9 s, x^sqrt(2) 1,1 s, 2^x 0,8 s, sin(x) 0,6 s (« pas encore prise en
    charge ») ; hors abs(x), sin(x) et e^x^x, toutes ok (dérivée et signe résolus) ; les 1 h 44 sont donc e^x^x (5ᵉ entrée du
    script). e^(e^x) bloque de la même façon (> 120 s, même pile).
    **Où** (pile `faulthandler` à 55 s et 110 s, identique) : `etude_complete.py:247` (`la.etudier`) → `limites_asymptotes.py:3779`
    (`_etudier_bornes`, borne x → +∞) → `:3649` (`_etude_transcendante`) → `:269` (`_limite_sympy`) → `:240` (`_contradit_par_sonde`,
    sonde haute précision) → `:166` (`_val_mp`, `mp.exp(a)`) → mpmath `mpf_exp` → `ln2_fixed` (`machin`, `bsp_acot`). Le temps
    n'est **pas** dans SymPy : la limite SymPy (`_limite_brute`) donne +∞ en 0,08 s. Il est dans mpmath : la sonde évalue f en
    x = 10², 10⁴, 10⁸, 10¹⁶, 10³⁰ (l. 222) ; en 10⁸, x^x ≈ 10^(8·10⁸) et exp de ce nombre demande ln 2 à environ 2,7·10⁹ bits
    (mesuré : x = 10⁴ 0,19 s, 10⁵ 11 s, 10⁶ > 60 s ; 10⁸ ne finit pas, 10¹⁶ et 10³⁰ encore moins). Les sondes lointaines (10¹⁰⁰,
    10¹⁰⁰⁰) sont déjà évitées pour les exponentielles (`_sonde_lointaine`, l. 133-144), pas les points ordinaires, trop grands
    pour une exponentielle d'exponentielle. Le blocage existe **avant la session 2** (67a3ca1, arbre séparé : > 120 s, même pile
    aux numéros de ligne d'avant P6 près) et dans l'**outil Limites** seul (`la.etudier("e^x^x")` > 120 s, même pile).
    **Dans la page** (code lu, sans navigateur) : le calcul tourne dans un Web Worker, la page ne gèle pas ; l'EC a une limite de 45 s
    (`etude-complete/index.html:71`, `delaiCalcul`), la page Limites 30 s (`commun/outil.js:53`) ; au-delà : « Calcul trop long : le
    calcul a été relancé. » et la carte « Le calcul a pris trop de temps (plus de 45 s). Essayez une écriture plus simple. »
    (`commun/outil.js:180-181`), puis le worker est arrêté et relancé (`commun/moteur-python.js:68`, SymPy rechargé). Rien de faux
    n'est affiché, mais l'élève attend 45 s pour un message qui ne dit pas que la fonction n'est pas traitée.
    **Pistes** (aucune appliquée) : (a) dans `_val_mp` (l. 166, et l. 174 pour un exposant variable), lever `OverflowError` (déjà
    intercepté par la sonde, l. 241 : point non évaluable) quand l'argument de exp dépasse une taille en bits (par exemple 10⁵ à 10⁶
    bits) : e^x^x garde 10² et 10⁴, la sonde juge encore sur deux points ; à vérifier : moins de deux points évaluables donne
    aujourd'hui « pas de contradiction » (la limite SymPy est gardée) ; pour ne pas affaiblir le garde-fou, ce cas devrait plutôt
    donner « limite non déterminée ». Une limite de temps dans la sonde ne suffit pas : un seul appel `mp.exp` ne s'interrompt pas.
    (b) Refuser en amont les tours d'exponentielles (exp ou exposant variable dont l'argument contient lui-même exp ou un exposant
    variable : e^x^x, e^(e^x), x^(x^x)) avec un message clair « pas encore prise en charge », comme sin(x). Laquelle ?

## À relire par l'enseignant

- **R1** (outil Dérivée, donc aussi EC ; Q37, Q56). Instantanés modifiés : `tests/python/instantanes/{derivee-variations,etude-complete}.json`,
  `tests/python/instantanes/resoudre/{derivee-variations,etude-complete}.json`, `tests/pages/references/{derivee-variations,etude-complete}.json` :
  21 entrées de la Dérivée modifiées et 2 nouvelles (Q37), 11 entrées de l'EC modifiées. Vérifié par programme : dans chaque entrée
  modifiée, **seule la ligne des zéros de f′** change (carte « Signe de f′ et variations ») ; aucun exposant ne change dans les entrées
  existantes. ED, Limites, Factorisation, Exp-log : instantanés identiques.

  | Entrée | Avant | Après |
  |---|---|---|
  | `e^((x^2+x-2)/(6x-12))` (Ex7, EC) | f′(x) = x(x − 4)e^{…}/(6(x − 2)²) = 0 ⇔ x = 0 ou x − 4 = 0 ⇔ x = 0 ou x = 4 ; valeur interdite : x = 2. | f′(x) = 0 ⇔ x(x − 4) = 0 (car e^{(x² + x − 2)/(6x − 12)} > 0) ⇔ x = 0 ou x = 4 (produit nul) ; valeur interdite : x = 2. |
  | `e^(2/(x^2-4))` (d, EC) | f′(x) = −4x e^{…}/((x − 2)²(x + 2)²) = 0 ⇔ x = 0 ; valeurs interdites : x = −2 ; x = 2. | f′(x) = 0 ⇔ x = 0 (car e^{2/(x² − 4)} > 0) ; valeurs interdites : x = −2 ; x = 2. |
  | `x^2*e^(-x)` (Dérivée, EC) | f′(x) = −x(x − 2)e^{−x} = 0 ⇔ x = 0 ou x − 2 = 0 ⇔ x = 0 ou x = 2. | f′(x) = 0 ⇔ x(x − 2) = 0 (car e^{−x} > 0) ⇔ x = 0 ou x = 2 (produit nul). |
  | `e^(x^2)` (Dérivée) | f′(x) = 2xe^{x²} = 0 ⇔ x = 0. | f′(x) = 0 ⇔ x = 0 (car e^{x²} > 0). |
  | `x^3-3x` (Dérivée, EC) ; de même `x/(x^2+1)` (Dérivée, EC) | f′(x) = 3(x + 1)(x − 1) = 0 ⇔ x + 1 = 0 ou x − 1 = 0 ⇔ x = −1 ou x = 1. | f′(x) = 0 ⇔ (x + 1)(x − 1) = 0 ⇔ x = −1 ou x = 1 (produit nul). |
  | `x^4-2x^2` (Dérivée, EC) | f′(x) = 4x(x + 1)(x − 1) = 0 ⇔ x = 0 ou x + 1 = 0 ou x − 1 = 0 ⇔ x = −1 ou x = 0 ou x = 1. | f′(x) = 0 ⇔ x(x + 1)(x − 1) = 0 ⇔ x = −1 ou x = 0 ou x = 1 (produit nul). |
  | `(x^2-1)/(x-3)` (Dérivée, EC) | f′(x) = (x² − 6x + 1)/(x − 3)² = 0 ⇔ x² − 6x + 1 = 0 ⇔ x = 3 − 2√2 ou x = 3 + 2√2 ; valeur interdite : x = 3. | f′(x) = 0 ⇔ x² − 6x + 1 = 0 ⇔ x = 3 − 2√2 ou x = 3 + 2√2 ; valeur interdite : x = 3. |
  | `3x^2-4x`, `x^2-4x+3`, `sqrt(x^2-4x+5)` (Dérivée ; x² − 4x + 3 aussi EC) | f′(x) = 2(3x − 2) = 0 ⇔ 3x − 2 = 0 ⇔ x = 2/3 (de même 2(x − 2), (x − 2)/√(x² − 4x + 5)) | f′(x) = 0 ⇔ 3x − 2 = 0 ⇔ x = 2/3 (de même x − 2 = 0 ⇔ x = 2) |
  | `-x^2`, `ln(x^2-4)`, `(x^2+1)^(1/2)` (Dérivée) | f′(x) = −2x = 0 ⇔ x = 0 (de même 2x/((x − 2)(x + 2)), x/√(x² + 1)) | f′(x) = 0 ⇔ x = 0 |
  | `x^3` (Dérivée) | f′(x) = 3x² = 0 ⇔ x = 0. | f′(x) = 0 ⇔ x² = 0 ⇔ x = 0. |
  | `(x-1)^3` (Dérivée) | f′(x) = 3(x − 1)² = 0 ⇔ x − 1 = 0 ⇔ x = 1. | f′(x) = 0 ⇔ (x − 1)² = 0 ⇔ x = 1. |
  | `x^(3/2)` (Dérivée) | f′(x) = 3√x/2 = 0 ⇔ √x = 0 ⇔ x = 0. | f′(x) = 0 ⇔ √x = 0 ⇔ x = 0. |
  | `x*ln(x)`, `x*ln(x)+x`, `3(x*ln(x))`, `-(x*ln(x))`, `ln(x)/x` (Dérivée ; x ln x, 3x ln x, ln(x)/x aussi EC) | f′(x) = ln(x) + 1 = 0 ⇔ x = e^{−1} (3(ln(x) + 1) = 0 ⇔ ln(x) + 1 = 0 ⇔ … ; (1 − ln(x))/x² = 0 ⇔ 1 − ln(x) = 0 ⇔ x = e) | f′(x) = 0 ⇔ ln(x) + 1 = 0 ⇔ x = e^{−1} (de même ln(x) + 2, −ln(x) − 1, 1 − ln(x)) ; les lignes d'explication de l'outil ED qui précèdent sont inchangées |
  | `x^x` (Dérivée) | f′(x) = x^x(ln(x) + 1) = 0 ⇔ ln(x) + 1 = 0 ⇔ x = e^{−1}. | f′(x) = 0 ⇔ x^x(ln(x) + 1) = 0 ⇔ ln(x) + 1 = 0 ⇔ x = e^{−1}. (question 58) |
  | `e^((x^2+1)/(2x))` (nouvelle, Dérivée, Q37) | (HEAD, hors instantanés) f′ avec e^{(½x² + ½)/x}, dans f′ encadré, la ligne des zéros et le tableau | f′(x) = (x + 1)(x − 1)e^{(x² + 1)/(2x)}/(2x²) ; « f′(x) = 0 ⇔ (x + 1)(x − 1) = 0 (car e^{(x² + 1)/(2x)} > 0) ⇔ x = −1 ou x = 1 (produit nul) ; valeur interdite : x = 0. » |
  | `e^((-2x^2+3x-1)/(3x-6))` (nouvelle, Dérivée, Q37) | (HEAD, hors instantanés) f′ avec e^{(3x − 2x² − 1)/(3x − 6)} | f′(x) = −(2x² − 8x + 5)e^{(−2x² + 3x − 1)/(3x − 6)}/(3(x − 2)²) ; « f′(x) = 0 ⇔ 2x² − 8x + 5 = 0 (car e^{…} > 0) ⇔ x = (4 − √6)/2 ou x = (4 + √6)/2 ; valeur interdite : x = 2. » |

  Hors instantanés (corpus) : b « f′(x) = 0 ⇔ (x − 3)(x + 2) = 0 (car e^{−2x} > 0) ⇔ x = −2 ou x = 3 (produit nul) » (avant « f′(x) =
  −2(x − 3)(x + 2)e^{−2x} = 0 ⇔ x − 3 = 0 ou x + 2 = 0 ⇔ x = −2 ou x = 3 ») ; a « f′(x) = 0 ⇔ x = 0 (car e^{−x²} > 0) » ; c
  « f′(x) = 0 ⇔ 3 − eˣ = 0 (car eˣ > 0) ⇔ x = ln(3) » ; x·e^(−x/3 + 1) : exposant de f′ e^{−x/3 + 1} (avant e^{1 − x/3}), e^(x/2) :
  e^{x/2} (avant e^{½x}). Guide : R7 (ligne des zéros), R11 (tableau u/v, Q32), exemple 4.

- **R2** (EC seule ; ED, Dérivée, Limites, Factorisation, Exp-log : instantanés identiques). Instantanés modifiés :
  `tests/python/instantanes/resoudre/etude-complete.json` (16 entrées modifiées, 1 nouvelle : `1/(x^2-3x+2)`),
  `tests/pages/references/etude-complete.json` (16 modifiées, 1 nouvelle), `tests/python/instantanes/etude-complete.json` (sortie
  d'`etudier()` : 1 nouvelle entrée, aucune modifiée). Vérifié par programme : seules changent les lignes des parties 2, 3 et 5
  ci-dessous (et la nouvelle entrée) ; `x/sqrt(x^2)` et l'entrée d'erreur `ln(` sont identiques.

  | Entrée | Avant | Après |
  |---|---|---|
  | toutes les valeurs approchées (Q15) : `(e^x-1)/x`, `e^(1/x)`, `e^(2x)`, `x^2*e^(-x)` (partie 2) ; `(x^2-1)/(x-3)`, Ex7, d (f(0)) ; `x^3-3x`, `x^4-2x^2` (zéros) ; tous les points des extremums | `\(f(1) = e - 1\)` ≈ 1,72 ; `\(x = -\sqrt{3}\)` ≈ −1,73 ; `\(\left(0\,;\,e^{1/6}\right)\)` ≈ (0 ; 1,18) (≈ en texte) | `\(f(1) = e - 1 \approx 1{,}72\)` ; `\(x = -\sqrt{3} \approx -1{,}73\)` ; `\(\left(0\,;\,e^{1/6}\right) \approx \left(0\,;\,1{,}18\right)\)` (≈ dans la formule) ; « −f(1) ≈ −1,72 » de même |
  | `x^2-4x+3` (Q11, Q23) | « ⇔ (x − 1)(x − 3) = 0 (Somme-Produit) » · « ⇔ x − 1 = 0 ou x − 3 = 0 (produit nul) » · « ⇔ x = 1 ou x = 3 » ; tableau : ligne x² − 4x + 3 | « ⇔ (x − 1)(x − 3) = 0 (Somme-Produit) » · « ⇔ x = 1 ou x = 3 (produit nul) » ; tableau : lignes (x − 1), (x − 3) |
  | `x^3-3x`, `x^4-2x^2` (Q23) | tableau : une ligne x³ − 3x (x⁴ − 2x²) | lignes x, (x² − 3) ; x², (x² − 2) |
  | `x^2-4x+3`, `x^3-3x`, `x^4-2x^2`, `x/(x^2+1)`, `x^2*e^(-x)`, `sqrt(x^2-4)`, `x^(2/3)`, `ln(x)/x`, `x*ln(x)`, `3(x*ln(x))` (Q41, nouvelles lignes avant la liste) | — | « f(2) = 2² − 4·2 + 3 = 4 − 8 + 3 = −1. » ; « f(−1) = (−1)³ − 3(−1) = −1 − (−3) = 2. » ; « f(−1) = (−1)/((−1)² + 1) = −1/(1 + 1) = −1/2 ≈ −0,50. » ; « f(0) = 0²e^{−0} = 0. », « f(2) = 2²e^{−2} = 4e^{−2} ≈ 0,54. » ; « f(−2) = √((−2)² − 4) = √(4 − 4) = 0. » ; « f(0) = ∛(0²) = 0. » ; « f(e) = ln(e)/e = 1/e = e^{−1} ≈ 0,37. » ; « f(e^{−1}) = e^{−1}ln(e^{−1}) = e^{−1}(−1) = −e^{−1} ≈ −0,37. » ; « f(e^{−1}) = 3e^{−1}ln(e^{−1}) = 3e^{−1}(−1) = −3e^{−1} ≈ −1,10. » |
  | extremums globaux (Q43) : `x^2-4x+3`, `x/(x^2+1)` (2), `x^(2/3)`, `ln(x)/x`, `x*ln(x)`, `3(x*ln(x))` | « **Minimum local** en x = 2 : (2 ; −1) (f′ passe de − à +). Global : les autres valeurs de f sont plus grandes (limites +∞ en ±∞). » | « **Minimum global** en x = 2 : (2 ; −1) (f′ passe de − à +). Les autres valeurs de f sont plus grandes (limites +∞ en ±∞). » |
  | `1/(x^2-3x+2)` (nouvelle) | — | Condition 1 : « On résout x² − 3x + 2 = 0 ⇔ (x − 1)(x − 2) = 0 (Somme-Produit) ⇔ x = 1 ou x = 2 (produit nul). » ; « f(3/2) = 1/((3/2)² − 3(3/2) + 2) = 1/(9/4 − 9/2 + 2) = −4. » ; « **Maximum local** en x = 3/2 : (3/2 ; −4) ≈ (1,50 ; −4) (f′ passe de + à −). Pas global : f(x) → +∞ quand x → 1⁻. » |

  Inchangés : les « Pas global : … » (mêmes raisons), les lignes « g(x₀) = … » d'Ex7 et de d (≈ dans la formule seulement), les
  extremums de (x² − 1)/(x − 3) (x₀ = 3 ± 2√2 : pas de ligne de calcul, ≈ dans la formule seulement).
  Hors instantanés (corpus) : b « f(1) = −5e^{−2} ≈ −0,68 », « f(−1) = −5e^{2} ≈ −36,95 » (formule) ; zéros « x = −√6 ≈ −2,45 ou
  x = √6 ≈ 2,45 » ; « f(−2) = ((−2)² − 6)e^{−2(−2)} = (4 − 6)e⁴ = −2e⁴ ≈ −109,20. », « f(3) = (3² − 6)e^{−2·3} = (9 − 6)e^{−6} = 3e^{−6}
  ≈ 0,0074. », « **Minimum global** en x = −2 … Les autres valeurs de f sont plus grandes (limites +∞ en −∞ et 0⁺ en +∞). » ; c
  « f(ln(3)) = e^{ln(3)}(6 − e^{ln(3)}) = 3(6 − 3) = 9. », « **Maximum global** en x = ln(3) : (ln(3) ; 9) ≈ (1,10 ; 9) … Les autres
  valeurs de f sont plus petites (…). » ; a « f(0) = e^{−0²} = 1. », « **Maximum global** en x = 0 : (0 ; 1) (f′ passe de + à −). Les
  autres valeurs de f sont plus petites (limites 0⁺ en ±∞). » ; Ex7 et d : ≈ dans la formule seulement.
  Largeurs : b, c, a, Ex7, d, 1/(x² − 3x + 2), x⁴ − 2x², x² − 4x + 3, 3x ln x, x ln x + x, 2x² − 6x + 4, (x² + x − 6)e^{−x},
  x²e^{−x²}, (x² − 1)/(x − 3), corrigé complet à 320 – 1100 px : aucune faute du balayage, aucune formule hors de sa carte.

- **P6** (outil **Limites**, donc aussi EC ; D12, D13, D16). Instantanés modifiés : `tests/python/instantanes/limites-asymptotes.json`
  (31 entrées sur 37), `tests/python/instantanes/resoudre/limites-asymptotes.json` (30 sur 37), `tests/pages/references/limites-asymptotes.json`
  (30 sur 38), `tests/pages/references/graphique-traces.json` (16 empreintes sur 48, toutes de e^(1/x) : même nombre d'appels de
  dessin, ordre des asymptotes AH (−∞), AV x = 0, AH (+∞) au lieu de AH, AH, AV), `tests/python/instantanes/etude-complete.json` (12 sur 18 : ordre des études, `gauche_tex` / `droite_tex` signés, 1⁺ du
  tableau de d, `position` des AH), `tests/python/instantanes/resoudre/etude-complete.json` (13 sur 18 : partie 4 seule, plus le bloc
  du graphique (données des asymptotes, non affichées) et la ligne f(x) du tableau de variations de d (1⁺ en ±∞)),
  `tests/pages/references/etude-complete.json` (11 sur 19). ED, Dérivée, Factorisation, Exp-log : instantanés identiques. Vérifié par
  programme : seules changent les lignes ci-dessous et l'ordre des cartes de limites.

  | Changement | Entrées | Avant | Après |
  |---|---|---|---|
  | Ordre des bornes (D16) | Limites : (eˣ − 1)/x, (eˣ − e²)/(x − 2), (ln(x) − 1)/(x − e), (ln(x) − 2)/(ln(x) − 1), (x² − 1)/(x − 1), (x² − 1)/(x − 3), (x³ + 1)/(x − 2), 1/(x − 2), e^((3x + 4)/(x − 2)), e^(−1/x)/x, e^(−2x/(x² − 5)), e^(1/x), eˣ/ln(x), eˣ/x, ln(x + 1)/x, ln(x² − 3)/(2 − x), ln(x² − 4x)/(x − 5), x ln(x²), x/√(x²), x²/(x − 1) ; EC : Ex7, (eˣ − 1)/x, (x² − 1)/(x − 3), 1/(x² − 3x + 2), e^(1/x), x/√(x²) | −∞, +∞, puis les valeurs interdites ; bilan dans le même ordre | −∞, valeurs interdites de gauche à droite, +∞ ; bilan : (x² − 1)/(x − 3) « oblique (−∞) · AV x = 3 · oblique (+∞) » |
  | x → ±∞ regroupés (D16) | Limites : 1/x², 1/(x² − 2), (2x² + 1)/(x² − 1) ; EC : d, x⁴ − 2x² ; corpus : a | deux cartes « Limite x → −∞ » et « x → +∞ », mêmes lignes | une carte « Limite x → ±∞ », `\lim_{x\to \pm\infty}` ; d : « Asymptote horizontale : y = 1 (des deux côtés). f(x) → 1⁺ : le graphe est au-dessus. » |
  | Valeur d'essai (D12) | Limites : e^((3x + 4)/(x − 2)) (2⁻, 2⁺), ln(x² − 4x)/(x − 5) (5⁻, 5⁺) ; EC : Ex7 (2⁻, 2⁺), d (±2⁻, ±2⁺) | « Exposant : (x² + x − 2)/(6x − 12) → 4/0⁻ = −∞. Donc … » ; « Bas : x − 5 → 0⁻. » | en plus, avant : « Haut de l'exposant : x² + x − 2 → 2² + 2 − 2 = 4 (pas 0, donc pas indéterminée). » · « Bas de l'exposant : 6x − 12 → 0 ; avec x = 1,99 : 6 · 1,99 − 12 = −0,06 < 0, donc 0⁻. » ; d : « avec x = −2,01 : (−2,01)² − 4 = 0,0401 > 0, donc 0⁺ » ; « Bas : x − 5 → 0 ; avec x = 4,99 : 4,99 − 5 = −0,01 < 0, donc 0⁻. » |
  | 1⁺ / 1⁻ (D13) | Limites et EC : e^(1/x) (±∞) ; EC : d (±∞) | « e^{0⁺} = 1 », résultat « = 1 », tableau de variations de d : 1 en ±∞ | « e^{0⁺} = 1⁺ (e^t > 1 pour t > 0) », résultat « = 1⁺ » ; tableau de d : 1⁺ ; e^(1/x) en −∞ : « e^{0⁻} = 1⁻ (e^t < 1 pour t < 0) » |
  | AH : côté et position (D13) | Limites : 20 entrées transcendantes (eˣ/x, x·eˣ, e^(2x), ln(x)/e^(2x)…) ; EC : Ex7, (eˣ − 1)/x, e^(1/x), d, e^(2x), ln(x)/x, x/√(x²), x²e^(−x) | « Asymptote horizontale : y = 0. » ; bilan « Asymptote horizontale (x → −∞) : y = 0 » | « Asymptote horizontale : y = 0 (à gauche). f(x) → 0⁺ : le graphe est au-dessus. » (position seulement si démontrée : sans elle pour e³, −1, ±1 de x/√(x²), 1 de ln(1 + eˣ)/eˣ…) ; bilan « … : y = 0, graphe au-dessus » |
  | AV d'un seul côté (D13) | Limites : e^((3x + 4)/(x − 2)), e^(−1/x)/x, e^(−2x/(x² − 5)) (±√5), e^(1/x) ; EC : Ex7, e^(1/x), d (±2) | « Asymptote verticale : x = 2 (du côté droit) ; à gauche, f(x) → 0. » ; bilan « lim_{x→2⁻} f(x) = 0 » | « Asymptote verticale : x = 2, seulement du côté droit. À gauche, f(x) → 0⁺ : le graphe s'approche du point (2 ; 0), qui n'appartient pas au graphe (rond vide). » ; bilan « lim_{x→2⁻} f(x) = 0⁺ » |

  Hors instantanés (corpus) : a « Limite x → ±∞ » : « Exposant : −x² → −∞. Donc e^{−x²} → e^{−∞} = 0⁺. », « Asymptote horizontale :
  y = 0 (des deux côtés). f(x) → 0⁺ : le graphe est au-dessus. » ; b « Asymptote horizontale : y = 0 (à droite). f(x) → 0⁺ : le graphe
  est au-dessus. » ; c « … y = 0 (à gauche). f(x) → 0⁺ : le graphe est au-dessus. ».
  Partie 4 de l'Ex7 après P6, écarts restants avec decisions.md §4 : « Exposant : … → 4/0⁻ = −∞. Donc e^{…} → e^{−∞} = 0⁺. » au lieu de
  « g(x) → 4/0⁻ = −∞, donc f(x) → 0⁺ » (question 70) ; la conclusion de l'AV d'un seul côté est écrite une fois, après x → 2⁺ (§4 :
  « Pas d'AV à gauche » après 2⁻, puis « AV x = 2, seulement du côté droit » après 2⁺) ; pas de « pas d'AH à droite (f(x) → +∞) » en
  +∞ (question 67). Les cartes de 2⁻ et 2⁺ sont maintenant entre −∞ et +∞ (D16).

- **P9** (EC seule ; ED, Dérivée, Limites, Factorisation, Exp-log : instantanés identiques, vérifié par `git status` après
  régénération : seuls les fichiers de l'EC changent). Instantanés modifiés : `tests/python/instantanes/resoudre/etude-complete.json`
  (18 entrées modifiées, 3 nouvelles : e^(−x²), (x² − 6)e^(−2x), eˣ(6 − eˣ)), `tests/pages/references/etude-complete.json` (18
  modifiées, l'entrée d'erreur `ln(` identique, 3 nouvelles), `tests/python/instantanes/etude-complete.json` (sortie d'`etudier()` :
  3 nouvelles entrées, **aucune modifiée**). Vérifié par programme : dans chaque entrée existante, la seule différence est la carte
  « Bilan de l'étude » ajoutée entre « 6. Graphe » et « Graphique » (et, dans les références de pages, le compteur « Étape n / N »
  qui gagne 1) ; toutes les autres cartes sont identiques.

  | Entrée | Avant | Après (lignes de la carte « Bilan de l'étude », style final) |
  |---|---|---|
  | Ex7 | — | « ED = ℝ ∖ {2} (partie 1) » · « Parité : f n'est ni paire ni impaire (partie 2) » · « Zéros : aucun (partie 3) » · « Signe : f(x) > 0 sur ED (partie 3) » · « Ordonnée à l'origine : f(0) = e^{1/6} ≈ 1,18 (partie 3) » · « Asymptote horizontale (x → −∞) : y = 0, graphe au-dessus (partie 4) » · « Asymptote verticale : x = 2 (lim_{x→2⁻} f(x) = 0⁺ ; lim_{x→2⁺} f(x) = +∞) (partie 4) » · « **Maximum local** en x = 0 : (0 ; e^{1/6}) ≈ (0 ; 1,18) (partie 5) » · « **Minimum local** en x = 4 : (4 ; e^{3/2}) ≈ (4 ; 4,48) (partie 5) » |
  | d | — | « ED = ℝ ∖ {−2 ; 2} » · « Parité : f est paire » · « Zéros : aucun » · « Signe : f(x) > 0 sur ED » · « Ordonnée à l'origine : f(0) = e^{−1/2} ≈ 0,61 » · AH y = 1 (−∞), graphe au-dessus · AV x = −2 (+∞ ; 0⁺) · AV x = 2 (0⁺ ; +∞) · AH y = 1 (+∞), graphe au-dessus · « **Maximum local** en x = 0 : (0 ; e^{−1/2}) ≈ (0 ; 0,61) » |
  | a, b, c (nouvelles) | — | a : ℝ · paire · aucun zéro · f(x) > 0 sur ED · f(0) = 1 · AH y = 0 (−∞) et (+∞), au-dessus · « **Maximum global** en x = 0 : (0 ; 1) » ; b : ℝ · ni paire ni impaire · « x = −√6 ≈ −2,45 ; x = √6 ≈ 2,45 » · « f(x) > 0 sur ]−∞ ; −√6[ ∪ ]√6 ; +∞[ ; f(x) < 0 sur ]−√6 ; √6[ » · f(0) = −6 · AH y = 0 (+∞), au-dessus · « **Minimum global** en x = −2 : (−2 ; −2e⁴) ≈ (−2 ; −109,20) » · « **Maximum local** en x = 3 : (3 ; 3e^{−6}) ≈ (3 ; 0,0074) » ; c : ℝ · ni paire ni impaire · « x = ln(6) ≈ 1,79 » · « f(x) > 0 sur ]−∞ ; ln(6)[ ; f(x) < 0 sur ]ln(6) ; +∞[ » · f(0) = 5 · AH y = 0 (−∞), au-dessus · « **Maximum global** en x = ln(3) : (ln(3) ; 9) ≈ (1,10 ; 9) » ; et toutes leurs autres cartes (nouvelles entrées : corrigé complet tel que le montrent les captures) |
  | 16 autres entrées de la page et cas limites | — | même forme ; à noter : e^(1/x) « AH (x → −∞) : y = 1, graphe au-dessous », « Ordonnée à l'origine : aucune, car 0 ∉ ED », « Aucun extremum local » ; x/√(x²) « Pas de limite en x = 0 … », « Aucun extremum » ; x^(2/3) « Aucune asymptote détectée », « f(x) > 0 sur ℝ ∖ {0} » ; √(x² − 4) « f(x) > 0 sur ]−∞ ; −2[ ∪ ]2 ; +∞[ », zéros −2 et 2 ; x³ − 3x « … — branche parabolique (partie 4) » (sans le point de la phrase de l'outil Limites) ; x ln x « Bord du graphe : … » |

  Page : Ex7 est le dernier exemple ; a, c en exercices « difficile », b, d en « très difficile » (question 81). Largeurs : Ex7, a–d,
  corrigé complet de 320 à 1100 px : aucune faute du balayage, aucune formule hors de sa carte, bilan visible avant le graphique
  (`test_largeurs.py::test_corrige_et_bilan_de_l_etude`). Captures : section « Temps sous Pyodide (P9) ».

## Journal

Tout le détail du chantier (résumé de la nuit, plans, temps, suites, écarts acceptés, questions 1 à 56 sauf 46, 50, 51 et 54,
tableaux « À relire » de P0 à P8) : [`journal.md`](journal.md).
