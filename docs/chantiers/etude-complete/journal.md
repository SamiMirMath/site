# Chantier « Étude complète » — journal

Détail du chantier, déplacé de suivi.md le 04.11.2026 ; état et questions ouvertes : suivi.md.
Fiche de suivi : [`suivi.md`](suivi.md). Questions 46, 50, 51, 54 (⏸, à juger à l'écran) et 57 à 83 : restées dans `suivi.md`.

Note de reprise de la session 2, remplacée dans `suivi.md` le 04.11.2026 (texte d'origine) :

**Reprise après compactage (session 2, 03–04.11.2026)** : la session 2 est **terminée pour les parties** : R1, R2, P6, P9 commitées
(résumé ci-dessous, « Résumé de la session 2 ») ; P10 non faite (facultative, exclue de la session) ; 1 xfail reste (P10) ; questions
57 à 83 ; rien n'est poussé ni fusionné. `decisions.md` (§7 : réponses aux questions 1 à 56 ; §2 Extremums révisé) a été versé avec
R1. Restent, hors parties : l'**audit tests-rapides** (non commité) et l'**allègement de ce fichier** vers `journal.md` (nouveau
paragraphe de `CLAUDE.md`, commit séparé). Pour reprendre : lire le « Résumé de la session 2 », `decisions.md`, puis
`git log --oneline main..HEAD`.

## Résumé de la nuit (02–03.11.2026)

### Parties faites

Vérifié par `git log --oneline main..HEAD` (9 commits, rien n'est poussé ni fusionné).

| Partie | Commit | Ce que l'élève voit de nouveau |
|---|---|---|
| P0 | 5eadf34 | Rien (tests seulement) : corpus Ex7, a–d, oracle mpmath, 66 vérifications de rédaction marquées xfail. |
| P1 | edf17c3 | **Outil Dérivée** et EC : f′ avec une seule exponentielle par exposant (Ex7 : une au lieu de trois), facteur négatif entre parenthèses, « (eˣ)′ = eˣ » écrit une fois, formes du corrigé 3e^{−6} et 2eˣ(3 − eˣ). |
| P2 | 4cf3e9e | L'étude suit les six parties titrées du corrigé (limites avant la dérivée) ; un seul calcul par étude (cache). |
| P3 | f108f7f | Partie 1 : carte « Mise en forme » (factorisations, g(x) nommé), une carte par condition avec la résolution courte « 6x − 12 = 0 ⇔ 6x = 12 ⇔ x = 2 », ED encadré. |
| P4 | 62781a8 | Partie 2 : parité justifiée (ED non symétrique, chaîne f(−x) une étape par ligne, ou contre-exemples chiffrés). |
| P5 | 8fc2fa2 | Partie 3 : zéros en chaîne avec la propriété nommée, signe de f (phrase ou tableau), f(0) exact puis approché. |
| P7a | 1799fff | **Outil Dérivée** et EC : tableau u / v ; sous-carte « Dérivée de l'exposant » une étape par ligne (Ex7, d) ; « On développe d'abord » pour c. |
| P7b | cfe88de | **Outil Dérivée** et EC : valeur exacte de chaque extremum dans le tableau de variations ; dans l'EC, extremums avec valeur approchée et « global » / « pas global » justifié. |
| P8 | 3ece3c9 | Partie 6 : zéros et (0 ; f(0)) marqués, rond vide à chaque point exclu à limite finie, fenêtre qui montre l'approche des AH. |

### Échecs, parties reportées, xfail

- Échecs : **aucun**.
- Reportées (non faites cette nuit, sur consigne) : **P6** (partie 4, Limites : D12, D13, D16), **P9** (exemples D18, Bilan D20,
  instantanés, largeurs, mesure Pyodide), **P10** (facultative, pente au point exclu D14).
- 21 xfail stricts restent dans `tests/python/test_corpus_etude_complete.py`, tous rattachés à une partie reportée :
  - P6 (14) : signe d'approche 1⁺ de d dans le tableau (1) ; position du graphe par rapport à l'AH (5 : Ex7, a–d) ; valeur d'essai
    0⁺ / 0⁻ (2 : Ex7, d) ; x → ±∞ regroupés (2 : a, d) ; 0⁺ dans la phrase de l'AV et le bilan (2 : Ex7, d) ; AV d'un seul côté et
    point exclu (2 : Ex7, d) ;
  - P9 (6) : fonctions du corrigé dans la page (1) ; carte « Bilan de l'étude » (5) ;
  - P10 (1) : pente au point exclu.

### Suite complète

Dernière vérification du chef d'orchestre sur 3ece3c9 (P8) : suite Python **1220 passés, 21 xfail** ; suite de pages **119 passés** ;
code de retour 0 (tableau « Suite complète » plus bas). Test instable **préexistant** `tests/pages/test_clavier.py::test_a_deux_formules…`
(page Limites ; échoue aussi sur P0, environ 1 fois sur 6 lancé seul) : non modifié, à traiter hors chantier (voir Écarts, P1).

### Temps natif

Voir le tableau « Temps natif de etudier() » plus bas : aucune hausse notable, sauf celle signalée à la **question 55** (a : 0,02 →
0,03 s, quelques millisecondes ; c : + 30 % ; la partie 3 est maintenant comptée dans `etudier()` et non plus dans `resoudre`).
La mesure sous Pyodide est prévue en P9.

### Questions pour l'enseignant : index

La liste complète, numérotée, est dans la section « Questions pour l'enseignant » plus bas.

**À trancher avant la fusion** :
- Q9 — fusionner sans P6 ni P9 ? (P4 et P5, demandées par Q9, sont faites)
- Q37 — exposant de f′ parfois différent de l'énoncé (**outil Dérivée**, D6)
- Q40 — raison « pas global » de d : −2⁻ au lieu de 2⁺
- Q5 — −1/e écrit −e^{−1} (**outil Dérivée**)
- Q6 — ln(x)/x : f′ = (1 − ln x)/x² (**outil Dérivée**)
- Q32 — tableau u/v à la place de R11 (**outil Dérivée**, guide)
- Q46 — tableau de variations de d défile à 390 px
- Q52 — deux ronds vides pour x/√(x²) (affirmation nouvelle du graphe)

**Toutes, par partie** :
- P0 : Q1 notation scientifique, R13 contre decisions.md §2 · Q2 entier exact sans « ≈ » (9, pas 9,00) ·
  Q3 lecture du critère « AH visible » (§3) · Q4 « (x²)′ = 2x » gardé pour a, b, d.
- P1 : Q5 −1/e devient −e^{−1} · Q6 ln(x)/x : (1 − ln x)/x².
- P2 : Q7 partie 5 vide si la dérivée sort du cadre · Q8 titre « Graphique » répète l'intertitre · Q9 ne pas fusionner sans P4, P5.
- P3 : Q10 quand afficher « Mise en forme » · Q11 chaîne courte pour d'autres trinômes · Q12 « On résout … » contre R10 ·
  Q13 « ED = ]0 ; +∞[ = ]0 ; +∞[ » repris de l'outil ED · Q14 Somme-Produit aussi pour a² − b².
- P4 : Q15 « ≈ » écrit hors de la formule · Q16 carte « Symétrie de l'ED » toujours affichée · Q17 mots de la chaîne f(−x) ·
  Q18 parité confirmée mais chaîne non rédigée · Q19 choix de a, écritures exactes · Q20 point a d'un ED non symétrique ·
  Q21 b : −36,95 (.tex : −36,9).
- P5 : Q22 chaîne une étape par ligne, ≈ par zéro · Q23 tableau de f avec les facteurs saisis · Q24 phrase de l'exponentielle ·
  Q25 propriétés ajoutées (numérateur nul, produit nul…) · Q26 formes non couvertes : lignes de l'outil ED · Q27 « Le graphe coupe
  l'axe des y au point … » · Q28 pas de ≈ entre 1000 et 10⁶ · Q29 pas de phrase après le tableau · Q30 sans zéro mais signe changeant.
- P7a : Q31 quand la sous-carte « Dérivée de l'exposant » · Q32 place du tableau u/v, R11 · Q33 forme finale de g′ · Q34 f′ encadré
  avec l'exposant en entier · Q35 mots de la sous-carte, g écrit développé · Q36 D7b : critère et dernière ligne · Q37 exposant de f′
  différent de l'énoncé · Q38 « · » seulement devant un facteur négatif · Q39 temps : aucune hausse de plus de 50 %.
- P7b : Q40 raison de « pas global » (d) · Q41 ligne g(x₀) pour chaque extremum · Q42 extremum à une borne fermée ·
  Q43 mots de « global » · Q44 limite « ? » : « local » seul · Q45 égalité avec une limite : « local » seul · Q46 tableau de d défile
  à 390 px · Q47 notation scientifique dans un point · Q48 « pas global » par un autre extremum.
- P8 : Q49 élargissement de la fenêtre pour l'AH · Q50 échelle égale : fenêtres larges et plates · Q51 branches infinies coupées en y ·
  Q52 deux ronds vides pour x/√(x²) · Q53 limite finie hors liste : pas de rond · Q54 coordonnées écrites à côté des zéros ·
  Q55 temps : a + 50 % (quelques ms).
- Résumé (vue en transcrivant l'Ex7) : Q56 ligne des zéros de f′ sans « produit nul » (**outil Dérivée**).

### À relire par l'enseignant

Détail (tableaux avant / après) dans la section « À relire par l'enseignant » plus bas. **D'abord l'outil Dérivée** :
- **P1, P7a, P7b** : `tests/python/instantanes/{derivee-variations,etude-complete}.json`,
  `tests/python/instantanes/resoudre/{derivee-variations,etude-complete}.json`, `tests/pages/references/{derivee-variations,etude-complete}.json`
  (P1 : 5 entrées ; P7a : 9 entrées de la Dérivée, 11 de l'EC ; P7b : 18 de la Dérivée, 13 de l'EC).
- P2, P4, P5 (EC seule) : `tests/python/instantanes/resoudre/etude-complete.json`, `tests/pages/references/etude-complete.json`.
- P3 (EC seule) : les deux mêmes, plus `tests/python/instantanes/etude-complete.json` (2 entrées nouvelles : Ex7, d).
- P8 (EC seule) : `tests/python/instantanes/etude-complete.json`, `tests/python/instantanes/resoudre/etude-complete.json`,
  `tests/pages/references/etude-complete.json`, `tests/pages/references/graphique-traces.json`.
- P0 : aucun instantané.

### Fusion

À lancer par l'enseignant **seulement après relecture** (rien n'est poussé ni fusionné) :

```
git switch main && git merge --no-ff etude-complete
```

P6 (Limites : D12, D13, D16) et P9 (exemples de la page D18, Bilan D20, mesure Pyodide) ne sont pas faites : l'outil est cohérent
(chaque partie affichée est vérifiée), mais la partie 4 garde la rédaction de l'outil Limites et l'Ex7 n'est pas encore un exemple de
la page (il n'est visible qu'en le saisissant).

### Exemple 7 : texte rendu (sortie de resoudre_ec)

Sortie de `resoudre_ec.resoudre("e^((x^2+x-2)/(6x-12))")` sur 3ece3c9 (Python 3.12, SymPy 1.13.3), transcrite par un script de
conversion (LaTeX → écriture lisible), relue à la main ; le contenu mathématique n'est pas changé. « [encadré] » : bloc résultat
encadré ; les cartes « Étape k : … » de la partie 4 sont les étapes de la carte « Limite » qui les précède.

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
  - Asymptote horizontale : y = 0.
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
- Carte « Limite (x → 2) » [badge « limite »] :
  - lim_(x → 2⁻) e^((x² + x − 2)/(6x − 12))
- Carte « Étape 1 : on remplace. » :
  - Exposant : (x² + x − 2)/(6x − 12) → 4/0⁻ = −∞. Donc e^((x² + x − 2)/(6x − 12)) → e^(−∞) = 0⁺.
  - **[encadré]** lim_(x → 2⁻) e^((x² + x − 2)/(6x − 12)) = 0⁺
- Carte « Limite (x → 2) » [badge « limite »] :
  - lim_(x → 2⁺) e^((x² + x − 2)/(6x − 12))
- Carte « Étape 1 : on remplace. » :
  - Exposant : (x² + x − 2)/(6x − 12) → 4/0⁺ = +∞. Donc e^((x² + x − 2)/(6x − 12)) → e^(+∞) = +∞.
  - **[encadré]** lim_(x → 2⁺) e^((x² + x − 2)/(6x − 12)) = +∞
  - Asymptote verticale : x = 2 (du côté droit) ; à gauche, f(x) → 0.
- Carte « Bilan des asymptotes » :
  - Liste :
    - Asymptote horizontale (x → −∞) : y = 0
    - Asymptote verticale : x = 2 (lim_(x → 2⁻) f(x) = 0 ; lim_(x → 2⁺) f(x) = +∞)

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
  - f′(x) = (x(x − 4)e^((x² + x − 2)/(6x − 12)))/(6(x − 2)²) = 0 ⇔ x = 0 ou x − 4 = 0 ⇔ x = 0 ou x = 4 ; valeur interdite : x = 2.
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

- Carte « Graphique » :
  - Graphique : fenêtre x de −9,62 à 6, y de −1,40 à 7,00 ; courbe en deux morceaux (de part et d'autre de x = 2) ; en pointillé, AH y = 0 (x → −∞) et AV x = 2 (à gauche → 0, à droite → +∞) ; points pleins : maximum (0 ; 1,18), qui est aussi (0 ; f(0)), et minimum (4 ; 4,48) ; aucun zéro ; rond vide en (2 ; 0).
  - Texte d'aide : Courbe (trait plein), asymptotes (pointillé), extremums, zéros et point (0 ; f(0)) (points pleins), points exclus du graphe (ronds vides). Molette ou boutons pour zoomer, cliquer-glisser pour déplacer.

#### Écarts restants avec la cible (decisions.md §4)

- Partie 4, x → 2⁻ et 2⁺ : « Exposant : … → 4/0⁻ » sans les lignes haut / bas ni la valeur d'essai (x = 1,99 : 6·1,99 − 12 = −0,06,
  donc 0⁻) → **P6** (D12).
- Partie 4, asymptotes : « Asymptote horizontale : y = 0 » sans « à gauche » ni « le graphe est au-dessus » ; AV « (du côté droit) ;
  à gauche, f(x) → 0 » au lieu de 0⁺, « seulement du côté droit » et du point (2 ; 0) exclu (rond vide) ; bilan « = 0 » sans 0⁺ → **P6** (D13).
- Partie 4, ordre : −∞, +∞, 2⁻, 2⁺ au lieu de −∞, 2⁻, 2⁺, +∞ ; « pas d'AH à droite » non écrit en +∞ → **P6** (D16 ; la phrase en +∞ :
  à confirmer).
- Partie 3 : « Le graphe coupe l'axe des y au point (0 ; e^{1/6}) » au lieu de « Point (0 ; e^{1/6}) » → question 27.
- Partie 5 : f′ encadré avec l'exposant écrit en entier, et non « x(x − 4)/(6(x − 2)²) · e^{g(x)} » → question 34 ; g(x) nommé sous forme
  développée dans la carte « Dérivée » (factorisée dans « Mise en forme ») → question 35 ; ligne g(0) répétée (déjà en partie 3) → question 41.
- Partie 5 : « f′(x) = … = 0 ⇔ x = 0 ou x − 4 = 0 ⇔ x = 0 ou x = 4 » au lieu de « ⇔ x(x − 4) = 0 ⇔ x = 0 ou x = 4 (produit nul) » →
  question 56. Ordre des lignes du tableau (e^{…} avant (x − 2)², §4 : l'inverse) et libellé e^{(x² + x − 2)/(6x − 12)} plutôt que
  e^{g(x)} : machinerie R7 de l'outil Dérivée (D9, écart accepté).
- Partie 6 : carte « Graphique » sous l'intertitre « 6. Graphe » (question 8) ; fenêtre x de −9,62 à 6 (.tex : −8 à 10, question 49).
- Pas de carte « Bilan de l'étude » ni d'Ex7 dans les exemples de la page → **P9** (D20, D18) ; pente au point exclu → **P10** (D14).

### Détail par partie (rapports de la nuit)

- **P0 faite** : branche `etude-complete` ; `audit-etape0.md` (copie inchangée du rapport d'audit) et `decisions.md` versés au dépôt ; corpus
  Ex7, a–d avec les résultats de decisions.md §4–5 ; oracle mpmath (fonctions écrites à la main) : tout le corpus est confirmé ; les valeurs de
  l'outil (ED, extremums, signe de f′, limites du tableau, asymptotes, fenêtre) sont justes ; 66 vérifications de rédaction marquées xfail (P1 à P10).
  Aucun changement du moteur.
- **P1 faite** : outil Dérivée (`derivee_variations.py`) : e^(somme) gardé entier (une exponentielle par exposant, D6) ; facteur négatif entre
  parenthèses et phrase de dérivée écrite une seule fois (D7) ; 3e^{−6} et 2eˣ(3 − eˣ) (D17). 5 xfail P1 retirés ; 5 instantanés de
  l'outil Dérivée / EC modifiés (liste sous « À relire ») ; questions 5 et 6 ; temps inchangé.
- **P2 faite** : six parties titrées dans l'ordre du .tex (D1) par un nouveau style de carte `partie` (intertitre sans cadre, commun à tous
  les outils, affiché avec la carte qui le suit et hors du compteur d'étapes) ; limites avant la dérivée ; parties 2 et 3 vides ;
  cache de l'analyse (D19) : un seul calcul par `etudier()`, aucun par `fenetre()` ; spécification réécrite (EC-01, EC-02 testé, EC-15).
  2 xfail P2 retirés ; seuls les instantanés de l'EC changent (ordre des cartes et intertitres) ; questions 7 à 9.
- **P3 faite** : partie 1 rédigée par le nouveau module `etude-complete/parties.py` (D2) : carte « Fonction » (f seule), carte « Mise en
  forme » (Ex7 : Somme-Produit, mise en évidence, g(x) nommé), une carte par condition (cartes de l'outil ED ; dénominateur affine ou
  ax² + c en chaîne courte « On résout 6x − 12 = 0 ⇔ 6x = 12 ⇔ x = 2. »), carte « Ensemble de définition » (ED encadré). Garde-fous exact
  et numérique ; les outils ED, Dérivée, Limites, Exp-log ne changent pas. 7 xfail P3 retirés ; instantanés de l'EC : partie 1 seule
  (liste sous « À relire ») ; questions 10 à 14 ; temps inchangé.
- **P4 faite** : partie 2 (parité, D4) dans `parties.py` (`cartes_parite`, appelée par `resoudre` sur l'analyse en cache) : ED non
  symétrique (« −2 ∈ ED, mais 2 ∉ ED »), chaîne f(−x) une étape par ligne avec la propriété nommée (paire / impaire), sinon « Pas
  impaire » (f(0) ≠ 0 ou contre-exemple) et « Pas paire » (contre-exemple, valeurs exactes puis arrondies, arrondis différents).
  Chaque affirmation confirmée par SymPy et par une sonde mpmath (30 chiffres) ; sinon un message clair, sans conclusion. 5 xfail P4
  retirés ; instantanés de l'EC : partie 2 seule (liste sous « À relire ») ; questions 15 à 21 ; `etudier()` inchangé, parité 0,2 à 9 ms.
- **P5 faite** : partie 3 (D5) dans `parties.py` (`cartes_zeros_signe`) : « e^{…} > 0 pour tout x (une exponentielle est strictement
  positive) », f(x) = 0 en chaîne une étape par ligne avec la propriété nommée (« car e^{−2x} > 0 », « produit nul », Somme-Produit…),
  chaque zéro exact puis ≈, zéro hors de l'ED rejeté ; sans zéro et de signe constant « Donc f n'a pas de zéro et f(x) > 0 sur ED » ;
  sinon tableau de signes de f par la machinerie R7 du tableau de f′ (extraite en `derivee_variations.tableau_signes`, outil Dérivée
  inchangé) ; f(0) exact puis ≈ et le point, ou « 0 ∉ ED » ; zéros non exacts ou doute : message clair. Garde-fous SymPy (f(z) = 0,
  `solveset`, signe exact par intervalle) et sonde mpmath. 5 xfail P5 retirés ; instantanés de l'EC : partie 3 seule (liste sous « À
  relire ») ; largeurs 320/360/390 sans faute ; questions 22 à 30 ; `etudier()` inchangé, partie 3 de 5 à 61 ms.
- **P7a faite** (outil Dérivée, donc aussi EC) : tableau u | v / u′ | v′ (D8, nouveau bloc `uv`, composant commun `.uv` qui empile
  u, u′, v, v′ quand les colonnes ne tiennent pas) à la place de « On pose … » et des lignes u′, v′ ; facteur négatif entre
  parenthèses **avec** le point, (x² − 6)·(−2e^{−2x}) (écart de P1 résorbé) ; f = e^{u/v} (Ex7, d, e^(1/x)) : sous-carte « Dérivée de
  l'exposant » (règle du quotient, tableau, puis développement, réduction, mise en évidence, simplification par 6, une étape par
  ligne), sans « (x²)′ = 2x » parasite ; D7b fait (critère simple : produit de deux sommes de c·e^{kx}) : « On développe d'abord »
  eˣ(6 − eˣ) = 6eˣ − eˣ · eˣ = 6eˣ − e^{2x}. f′ inchangée ; chaque ligne vérifiée (SymPy et sonde), sinon rédaction habituelle.
  4 xfail P7a retirés (3 tests) ; 9 entrées de la Dérivée et 11 de l'EC modifiées (carte « Dérivée » seule, liste sous « À relire ») ;
  questions 31 à 39 ; temps : Ex7 0,64 s (+ 8 %), autres inchangés.
- **P7b faite** (D10 : outil Dérivée, donc aussi EC ; D11 : EC seule) : la case de chaque extremum de la ligne f(x) porte sa valeur
  exacte (e^{1/6}, −2e⁴, 4√2 + 6…) au lieu de « • » (case `val:` déjà rendue par `commun/rendu.js` ; « • » reste si la valeur est
  inconnue). Dans l'EC, `parties.blocs_extremums` remplace la liste : « g(4) = 18/12 = 3/2, donc f(4) = e^{3/2} ≈ 4,48. » quand g est
  nommé, puis « **Maximum local** en x = 0 : (0 ; e^{1/6}) ≈ (0 ; 1,18) (f′ passe de + à −). Pas global : f(x) → +∞ quand x → 2⁺. »,
  « Global : les autres valeurs de f sont plus petites (limites 0⁺ en ±∞). » ou rien (« local » seul : « ? », égalité, doute).
  Comparaisons par SymPy et mpmath, « global » confirmé par une sonde de f sur l'ED, « pas global » par une valeur de f au-delà de
  f(x₀). 10 xfail P7b retirés (2 tests) ; 18 entrées de la Dérivée et 13 de l'EC modifiées (liste sous « À relire ») ; questions 40 à
  48 ; temps d'`etudier()` inchangé, D11 coûte 16 à 30 ms dans `resoudre`.
- **P8 faite** (EC seule, D15, §3) : partie 6 « Graphe » : zéros et (0 ; f(0)) marqués (données de la partie 3, calculée une fois
  par étude, `etude_et_partie3`) ; rond vide à chaque point exclu à limite finie d'un côté (Ex7 (2 ; 0), d (±2 ; 0)) ou à deux
  limites finies différentes (x/√(x²)), confirmé par SymPy (limite latérale par les règles) et par une sonde mpmath, sinon rien ;
  cadrage : fenêtre des points à montrer, branches infinies coupées en y, côté de chaque AH élargi jusqu'à l'approche à 5 % (Ex7,
  c, d) ; courbe tracée une largeur au-delà ; `commun/graphique.js` : un dessin de rond vide, un dessin de point plein. 3 xfail P8
  retirés ; instantanés et traces de l'EC régénérés (liste sous « À relire ») ; questions 49 à 55.

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

### P2 (03.11.2026)

Squelette sans contenu mathématique nouveau (D1), spécification (D2), cache (D19). L'outil Dérivée et l'outil Limites seuls ne changent pas.
1. **Intertitres (D1)** : nouveau style de carte `partie` dans `moteur/sortie.py` (constructeur `so.partie(titre)`, carte sans bloc), rendu
   par `commun/rendu.js` en `<h2>` sans cadre (`.carte-etape.partie` dans `commun/composants.css`, composant commun). `commun/outil.js` :
   un intertitre n'est pas une étape (il apparaît avec la carte qui le suit et n'entre pas dans « Étape k / n »). Les autres outils
   n'ont pas d'intertitre : rien ne change pour eux.
2. `resoudre_ec.py` : six intertitres dans l'ordre du .tex ; cartes réordonnées : 1 « Fonction » ; 2 et 3 vides (l'option qui affiche
   le moins) ; 4 tableaux de signes, limites, bilan des asymptotes ; 5 dérivée, signe de f′ et variations ; 6 graphique.
3. **D19** : `etude_complete.py`, cache `functools.lru_cache` de `analyser_complet` par entrée normalisée (espaces réduits) et état de
   SymPy (un résultat obtenu sans SymPy n'est jamais resservi avec) ; `dv.etudier` et `la.etudier` reçoivent un paramètre facultatif
   `analyse` (résultat déjà calculé) : sans lui, comportement inchangé. Test compteur : vide le cache, puis 1 calcul par `etudier()`,
   0 de plus par `fenetre()`.
4. Spécification `docs/specifications/etude-complete.md` : EC-01 réécrit, EC-02 testé, EC-15 nouveau, les 6 parties, module
   `parties.py` annoncé (créé à P4, quand une partie a un contenu : rien d'utile à y mettre à P2) ; `docs/choix-techniques.md` : style
   `partie` du format de sortie.
5. Tests : retrait des xfail P2 ; `test_resoudre_ec.py` suit le nouvel ordre ; `test_sortie.py` (style `partie`) ; instantanés `resoudre`
   et références de pages de l'EC régénérés ; suite complète ; temps natif ; commit « EC P2 : … ».

### P3 (03.11.2026)

Partie 1 de l'EC (D1, D3), tout dans un nouveau module `etude-complete/parties.py` (D2) ; les outils ED, Dérivée, Limites et Exp-log ne
changent pas (leurs instantanés restent identiques). Comme la filière M de l'outil Exp-log (`resoudre_el._blocs_ed`), on reprend les
fonctions publiques de `resoudre_ed` (`blocs_condition`, `blocs_ensemble`), sans les modifier.
1. `parties.mise_en_forme(f)` : seulement si f = e^{haut/bas}, haut et bas polynômes de degré ≥ 1 écrits développés à coefficients
   entiers. Chaque membre : mise en évidence de c·xᵏ (c = pgcd), puis Somme-Produit (trinôme unitaire, deux racines entières distinctes,
   facteurs par racine croissante : (x + 2)(x − 1)) ; une ligne par méthode, « (méthode) » à droite ; puis « On note g(x) = haut/bas
   factorisés, donc f(x) = e^{g(x)}. ». Garde-fous : produit développé = polynôme (exact), sonde `evaluer` de l'arbre en 5 points ;
   sinon la ligne n'est pas écrite. Aucune ligne : pas de carte (d n'en a pas, comme le .tex : haut constant).
2. `parties.blocs_condition(c, A)` : un dénominateur affine ou ax² + c (c/a < 0, racines rationnelles ou k√m), écrit développé, donne la
   chaîne courte du .tex (« On résout … ⇔ … ») sous l'inégalité de l'outil ED ; garde-fous : l'ensemble ℝ ∖ {racines} écrit comme l'outil
   ED est exactement son `E_tex`, et `evaluer(A, racine) ≈ 0` ; dénominateur x : « x ≠ 0 » seul (l'outil ED écrit « x ≠ 0 ⇔ x ≠ 0 ») ;
   tout le reste (ln, racine, Δ, écriture factorisée…) : les blocs de l'outil ED tels quels. Les arbres des conditions viennent de
   `conditions` (réexporté par `noyau`, sans changement de `ensemble_def`), sur l'analyse en cache (aucun nouveau calcul, D19).
3. `parties.cartes_domaine` : Fonction (formule seule : l'ED est établi juste après), Mise en forme, Condition k (titre, badge et
   détail de l'outil ED), « Ensemble de définition » (style normal, `blocs_ensemble` : ED encadré ; sans condition, précédé de la phrase
   de l'outil ED « Ni logarithme, ni dénominateur, ni racine : aucune condition. »). `resoudre_ec` l'appelle à la place de
   `rdv.carte_rappel`. Manifeste : `resoudre_ed.py` et `parties.py` ajoutés à l'EC.
4. Tests : xfail P3 retirés ; `test_parties_ec.py` (lignes exactes, oracle mpmath sur 150 polynômes tirés au hasard et sur les racines,
   formes laissées à l'outil ED, garde-fous forcés en échec) ; `test_resoudre_ec.py` (ordre des cartes calculé depuis l'analyse de
   l'outil ED, ED et conditions identiques à l'outil ED) ; `test_noyau.py` (parties.py n'importe que du noyau) ; Ex7 et d ajoutés aux cas
   limites de l'EC (`cas.py`, cités dans la spécification) pour les instantanés et le rendu de page. Instantanés `resoudre` et
   références de pages de l'EC régénérés ; largeurs 320/360/390 vérifiées à part pour Ex7, d, 1/(4x²−1) et une mise en forme à
   deux lignes (aucune faute) ; suite complète ; temps natif ; commit « EC P3 : … ».

### P4 (03.11.2026)

Partie 2 de l'EC (D4), tout dans `etude-complete/parties.py` (`cartes_parite`, appelée par `resoudre_ec` sur l'analyse en cache : aucun
nouveau calcul de l'ED, D19) ; les autres outils ne changent pas. Toute affirmation est confirmée deux fois (principe 0.2) : SymPy exact
et une sonde mpmath (évaluation de l'arbre à 30 chiffres, écrite dans `parties.py` : `evaluer` est en flottants) ; au moindre doute, un
message clair et aucune conclusion.
1. **ED non symétrique (règle 1)** : comparaison exacte des intervalles de l'ED et de leurs symétriques (bornes rationnelles, sinon SymPy ;
   une borne approchée = doute). Point a : d'abord le symétrique d'une borne rationnelle (Ex7 : « −2 ∈ ED, mais 2 ∉ ED »), sinon 1, 2, 1/2,
   3… ; appartenance exacte, puis sonde (f(a) définie, f(−a) non définie). Une carte « Symétrie de l'ED », conclusion « ni paire ni impaire ».
2. **ED symétrique** : carte « Symétrie de l'ED » (« ED est symétrique par rapport à 0. »), puis la sonde classe f (paire, impaire, ni
   l'une ni l'autre, doute) sur des points de l'ED.
   - Paire ou impaire : confirmée par SymPy (f(−x) ∓ f(x) se simplifie en 0) ; carte « Calcul de f(−x) », une étape par ligne :
     substitution « (on remplace x par −x) », puis la forme simplifiée avec la propriété (« car (−x)² = x² », « règle des signes » pour
     les signes), pour une fonction impaire somme « −(…) (mise en évidence de −1) », enfin « = f(x) » ou « = −f(x) » ; chaque ligne est
     vérifiée (SymPy et sonde). La chaîne n'est écrite que si la parité se lit sur l'arbre (puissances de x, sommes, produits, quotients,
     exp/ln/√ d'une expression paire) ; sinon message clair.
   - Ni l'une ni l'autre (règle 3) : carte « Pas impaire » (f(0) ≠ 0 en valeur exacte si 0 ∈ ED et f(0) ≠ 0, sinon contre-exemple
     f(−a) ≠ −f(a)), carte « Pas paire » (contre-exemple f(−a) ≠ f(a)), a dans 1, 2, 1/2, 3, 4, 1/3, 5 avec ±a ∈ ED ; valeurs exactes
     (f(a) écrit par substitution et calcul des constantes rationnelles, vérifié égal à la valeur SymPy et à la sonde), puis approchées
     (decisions.md §2 ; entier exact sans « ≈ ») ; les deux valeurs arrondies affichées doivent différer, sinon a suivant, sinon message.
3. `resoudre_ec` : cartes de la partie 2 sous l'intertitre « 2. Parité ».
4. Tests : xfail P4 retirés ; `test_parties_ec.py` (cartes exactes du corpus et des entrées de la page, oracle mpmath de `tests/python/
   oracle.py` pour les valeurs et la parité, garde-fous forcés : sonde ou SymPy en désaccord, arrondis égaux, SymPy absent) ;
   `test_resoudre_ec.py` suit les nouvelles cartes. Instantanés `resoudre` et références de pages de l'EC régénérés (liste sous « À
   relire ») ; largeurs ; suite complète ; temps natif (et coût de la parité, calculée hors d'`etudier()`) ; commit « EC P4 : … ».

### P5 (03.11.2026)

Partie 3 de l'EC (D5), dans `etude-complete/parties.py` (`cartes_zeros_signe`, appelée par `resoudre_ec` sur l'analyse en cache, D19).
Le tableau de signes de f réutilise la machinerie R7 du tableau de f′ : le bloc de `derivee_variations.etudier` qui construit les points
critiques, les lignes de facteurs et la ligne combinée devient la fonction publique `tableau_signes(expr, Z, D, ED, étiquette, c, facteurs)`,
appelée par `etudier` (sortie de l'outil Dérivée inchangée : instantanés identiques) et par la partie 3 (étiquette « f(x) »).
1. **Exponentielle** : chaque facteur e^{…} de f (`aplatir`) donne « e^{…} > 0 pour tout x (une exponentielle est strictement
   positive) ; il ne s'annule jamais. » (« x ∈ ED » si ED ≠ ℝ ; f = e^{…} seule : phrase de decisions.md §4, « e^{g(x)} » si g est nommé).
2. **Zéros** : chaque autre facteur du numérateur résolu par le moteur de l'outil ED (`preimage`) ; chaîne une étape par ligne, la
   propriété nommée (« car e^{−2x} > 0 », « numérateur nul », « produit nul » avec les facteurs menés ensemble ; polynômes : chaîne courte
   de la partie 1, mise en évidence et Somme-Produit ; autres facteurs : lignes « A ⇔ B (propriété) » de l'outil ED enchaînées) ; dernière
   étape : chaque zéro exact puis ≈ ; zéro hors de l'ED rejeté ; forme non couverte : lignes de l'outil ED ; zéro approché ou non calculé :
   message clair, pas de tableau.
3. **Signe** : sans zéro et de signe constant, « Donc f n'a pas de zéro et f(x) > 0 sur ED. » ; sinon carte « Signe de f » (tableau).
   Garde-fous (principe 0.2) : SymPy (f(z) = 0 ; `solveset` ne donne aucun autre zéro dans l'ED ; signe exact en un point rationnel de
   chaque intervalle ; appartenance à l'ED exacte) et sonde mpmath (f(z) ≈ 0 ; signe en 9 points de chaque intervalle) ; sinon message.
4. **Ordonnée à l'origine** : f(0) exact (substitution calculée, comme P4) puis ≈, « g(0) = −2/(−12) = 1/6, donc f(0) = e^{1/6} » quand
   g est nommé, puis le point ; « 0 ∉ ED : le graphe ne coupe pas l'axe des y » ; ≈ : decisions.md §2 et R13 (questions 1 et 2).
5. Tests : xfail P5 retirés ; `test_parties_ec.py` (cartes exactes du corpus et des entrées de la page, oracle mpmath de `oracle.py` pour
   les zéros, le signe et f(0), famille au hasard, garde-fous forcés) ; `test_resoudre_ec.py` suit les nouvelles cartes ; spécification.
   Instantanés `resoudre` et références de pages de l'EC régénérés (liste sous « À relire ») ; largeurs 320/360/390 ; suite complète ;
   temps natif (et coût de la partie 3) ; commit « EC P5 : … ».

### P7a (03.11.2026)

Outil Dérivée (`derivee-variations/derivee_variations.py`, `resoudre_dv.carte_derivee`), donc aussi l'EC (portée EC + Dérivée) ; f′ ne
change pas (même calcul, même écriture de `deriv_tex`), seules les étapes de la carte « Dérivée » changent.
1. **D8, tableau u, v / u′, v′** : nouveau bloc `uv` du format de sortie (`sortie.uv`, `valider`), rendu par `commun/rendu.js` en deux
   colonnes (u, u′) | (v, v′) ; composant commun `.uv` dans `commun/composants.css` : si les deux colonnes ne tiennent pas côte à côte, la
   colonne v passe sous la colonne u (u, u′, v, v′ empilés, par retour à la ligne, aucune largeur en pixels). Règle du produit et du
   quotient (premier niveau) : « On applique la règle du produit, (uv)′ = u′v + uv′, avec : », le tableau, les justifications des
   dérivées (R11), puis la ligne f′ ; les phrases « On pose u(x) = … et v(x) = … » et « u′(x) = … », « v′(x) = … » disparaissent.
2. **D7, parenthèses avec le point** : dans la ligne u′v ± uv′, un facteur négatif à droite d'un produit s'écrit `(x² − 6)·(−2e^{−2x})`
   (`_tex_brut`, partout ailleurs l'écriture de `tex`) : l'écart de P1 est résorbé.
3. **D7, dérivée de l'exposant** : f = e^{g(x)}, g = u/v avec u et v polynômes écrits développés à coefficients entiers, v non constant
   (Ex7, d, e^(1/x)). Une phrase « f(x) = e^{g(x)} avec g(x) = …, donc f′(x) = g′(x)·e^{g(x)} (dérivée d'une composée) », puis la
   sous-carte « Dérivée de l'exposant » (bloc `sous_calcul` existant) : étape « règle du quotient » (formule, tableau u/v, ligne
   g′(x) = …), étape « calcul du numérateur, puis simplification » (développement terme à terme, réduction, mise en évidence de c·xᵏ,
   simplification par le pgcd avec le coefficient du dénominateur (6x − 12)² = 36(x − 2)²), une étape par ligne ; puis « On remplace
   g′(x) dans f′(x) = g′(x)·e^{g(x)} : » et f′ encadré. Plus de « (x²)′ = 2x » parasite. Garde-fous : chaque ligne égale à la précédente
   (SymPy et sonde en 7 points), la dernière égale à g′ (SymPy `diff` et différence centrée), g′·e^{g} égale à f′ ; sinon la rédaction
   actuelle. Exposant polynôme (a : −x²) : rédaction actuelle (le .tex n'a pas de sous-carte).
4. **D7b, développer d'abord** (critère simple et sûr, donc fait) : f = A·B, A et B sommes de c·e^{kx} (k entier ≥ 1) et de constantes
   entières, une exponentielle dans chacun, une somme dans l'un : « On développe d'abord (c'est plus simple à dériver) : », f(x) = eˣ(6 − eˣ)
   = 6eˣ − eˣ · eˣ (développement) = 6eˣ − e^{2x} (réduction), puis la dérivée de la somme. Garde-fous : SymPy et sonde, et la dérivée
   de la forme développée doit s'écrire exactement comme f′ ; sinon la rédaction actuelle.
5. Tests : xfail P7a retirés ; `test_derivee_narration.py` (lignes exactes Ex7, d, c, b ; famille d'exposants u/v tirés au hasard dont
   chaque ligne affichée, relue et évaluée en mpmath, égale g′ ; cas laissés à la rédaction actuelle ; garde-fous forcés) ; les tests
   qui lisaient `it["html"]` lisent tout le texte de l'étape (`moteurs.texte_etape`, tableau et sous-carte compris) ; `test_sortie.py`
   (bloc `uv`), `test_composants.py` (`.uv`), `test_largeurs.py` (tableau u/v et sous-carte à 320–1100 px : rien ne déborde, colonnes
   alignées côte à côte, empilées dans l'ordre u, u′, v, v′ quand elles ne tiennent pas). Instantanés Dérivée et EC régénérés (moteur,
   `resoudre`, références de pages), listés sous « À relire » ; spécification de l'outil Dérivée ; suite complète ; temps natif ; commit.

### P7b (03.11.2026)

D10 dans l'outil Dérivée (donc aussi l'EC) ; D11 dans l'EC seule (`parties.py`, appelé par `resoudre_ec`, sur l'analyse en cache).
1. **D10** (`derivee_variations.etudier`) : la case d'un extremum de la ligne f(x) porte sa valeur exacte (case `val:…` déjà rendue par
   `commun/rendu.js`, comme f(a) là où f′ n'est pas définie) au lieu de « • » ; « • » reste seulement si la valeur n'est pas connue
   (« ? »). Chaque extremum garde aussi ses écritures SymPy (`x_py`, `f_py`) pour l'EC. La liste des extremums de l'outil Dérivée ne
   change pas.
2. **D11** (`parties.blocs_extremums`, à la place de la liste dans la carte « Signe de f′ et variations » de l'EC, `carte_signe(…,
   extremums=…)`) :
   - quand la carte « Dérivée » a nommé g (f = e^{u/v}, sous-carte « Dérivée de l'exposant ») et x₀ rationnel : « g(4) = 18/12 = 3/2,
     donc f(4) = e^{3/2} ≈ 4,48. » (u(x₀)/v(x₀) calculé, réduit ; vérifié : e^{g(x₀)} = f(x₀) par SymPy et par la sonde) ;
   - une ligne par extremum : « **Maximum local** en x = 0 : (0 ; e^{1/6}) ≈ (0 ; 1,18) (f′ passe de + à −). » (≈ : `approchee` de P5,
     decisions.md §2 et R13 ; entier exact sans ≈ ; « (f′ passe … ) » seulement si f′ change de signe) ;
   - puis, selon D11 : « Global : les autres valeurs de f sont plus petites (limites 0⁺ en ±∞). » si f(x₀) dépasse strictement les
     autres extremums du même genre et **toutes** les limites aux bornes de l'ED (±∞, chaque côté ouvert de chaque borne, lues dans le
     tableau T06c) ; « Pas global : f(x) → +∞ quand x → 2⁺. » si une limite ou un autre extremum dépasse strictement (raison : la valeur
     la plus extrême, puis l'ordre du tableau) ; rien sinon (une limite « ? » ou absente, une égalité, une borne fermée qui n'est pas un
     extremum, une valeur non exacte, un doute).
   - Garde-fous (principe 0.2) : chaque comparaison est faite par SymPy (signe exact de la différence) et par mpmath ; « global » est
     confirmé par une sonde de f sur l'ED (grille et points près de chaque borne : aucune valeur au-delà de f(x₀)) ; « pas global » par
     une sonde qui trouve un x de l'ED où f dépasse f(x₀) ; sinon « local » seul. Limites lues sur une liste fermée d'écritures (±∞,
     0^{±}, entiers, fractions, avec signe d'approche) : toute autre écriture = doute.
3. Tests : xfail P7b retirés ; `test_tableau_variations.py` attend la valeur à la place de « extremum » ; `test_parties_ec.py` (lignes
   exactes du corpus et des entrées de la page, oracle mpmath : valeurs, arrondis, global ou non recalculé sur une grille dense de l'ED,
   raison vérifiée ; famille au hasard ; garde-fous forcés) ; `test_largeurs.py` (tableau de variations avec valeurs dans les deux
   outils, 320 à 1100 px). Instantanés Dérivée et EC régénérés (moteur, `resoudre`, références de pages), listés sous « À relire » ;
   spécifications ; suite complète ; temps natif ; commit « EC P7b : … ».

### P8 (03.11.2026)

Partie 6 de l'EC (D15, decisions.md §3), EC seule. Lecture de « AH visible » retenue (question 3) : le x cherché est du côté de
l'asymptote, au-delà de tous les points à montrer et des valeurs interdites.
1. **Données de la partie 3 réutilisées** : `parties.partie3(analyse)` rend les cartes de la partie 3 (inchangées) **et** les zéros
   confirmés et f(0) confirmé (les mêmes garde-fous : rien si doute) ; `etude_complete.etude_et_partie3` la calcule une fois par
   étude : `etudier()` s'en sert pour le graphique, `resoudre` pour les cartes (le coût de la partie 3 passe de `resoudre` à
   `etudier()`). Pas de cache entre deux appels (un test qui fausse un garde-fou ne doit pas laisser un résultat faussé en cache).
   `cartes_zeros_signe` reste (mêmes cartes).
2. **Ronds vides** (`parties.ronds_vides`, nouvelle section « Partie 6 ») : pour chaque borne finie de l'ED, chaque côté dont la
   limite (valeurs T06c de la partie Limites, une seule source) est finie, hors des points déjà dessinés comme « trou » par l'outil
   Limites : (a ; L) seulement si L se lit sur la liste fermée de `lire_limite`, si SymPy donne exactement L (limite latérale ; pour
   f = e^{u}, e^{lim u}, beaucoup plus rapide que la limite de f) **et** si la sonde mpmath (f(a ± 10⁻ᵏ), 30 chiffres) s'approche de
   L du bon côté (signe d'approche compris) ; sinon pas de rond (principe 0.2). Ex7 : (2 ; 0) ; d : (−2 ; 0), (2 ; 0) ;
   x/√(x²) : (0 ; −1), (0 ; 1).
3. **Points marqués** : zéros et (0 ; f(0)) dans le bloc du graphique (`points`), sans doublon avec un extremum (déjà marqué).
4. **Cadrage** (`_cadrage_et_courbe`) : x d'intérêt = bornes finies de l'ED, extremums, zéros, 0 (si f(0) existe), ronds ; y d'intérêt
   = leurs ordonnées et les AH ; les échantillons (bande centrale, comme avant) sont ramenés dans [min − e ; max + e] des y d'intérêt
   (e = max(étendue/4 ; 1)) : une branche qui file vers ±∞ n'écrase plus l'échelle (c : y de −51 à 21 avant). Puis, pour chaque AH
   y = L en ±∞, tant qu'aucun échantillon au-delà de tous les points à montrer n'est à moins de 5 % de la hauteur de L, le côté de
   l'AH est élargi de 25 % de la largeur (6 fois au plus, fenêtre au plus 3,8 fois plus large ; sinon le cadrage sans élargissement). `fenetre()` ne change pas.
5. **Dessin** (`commun/graphique.js`) : un seul dessin de rond vide pour les trous de l'outil Limites et les `ronds_vides`, un seul
   dessin de point plein (avec ses coordonnées) pour les extremums et les `points` ; bloc `graphique` : clés facultatives `points`,
   `ronds_vides` (`moteur/sortie.py`) ; texte d'aide de la carte mis à jour.
6. Tests : xfail P8 retirés ; corpus (ronds vides = oracle, zéros et f(0) marqués, fenêtre §3, AH visible) ; `test_parties_ec.py`
   (ronds vides et cadrage sur d'autres fonctions, oracle mpmath ; garde-fous forcés : SymPy ou sonde en désaccord, SymPy absent) ;
   `test_resoudre_ec.py` (bloc du graphique) ; page : `test_graphique.py` (ronds vides et points dessinés à leur place),
   `graphique-traces.json` régénéré ; largeurs. Instantanés de l'EC régénérés (liste sous « À relire ») ; spécification ; suite
   complète ; temps natif ; commit « EC P8 : … ».

### R1 (03.11.2026, session 2)

Corrections après relecture qui touchent l'**outil Dérivée** (donc aussi l'EC) : Q37, Q56, Q32 (decisions.md §7). Tout dans
`derivee-variations/derivee_variations.py` ; les autres outils ne changent pas (leurs instantanés doivent rester identiques).
1. **Q37, exposant de l'énoncé** : à la fin de `_simplifier`, chaque `e^{a}` de f′ dont l'exposant a est égal à un exposant écrit
   dans l'arbre dérivé (donc dans l'énoncé) reprend cet exposant tel qu'il est écrit (mêmes termes, même ordre). Égalité prouvée
   deux fois : `cancel(together(a − b)) = 0` (SymPy, exact) **et** sonde (évaluation en 5 points, au moins un point défini) ;
   sinon l'écriture de SymPy reste (elle est juste). f′ ne change pas de valeur ; seules les écritures changent.
   Tests : e^((x²+1)/(2x)) et e^((−2x²+3x−1)/(3x−6)) entrent dans les cas limites de l'outil Dérivée (`tests/python/cas.py`,
   cités dans la spécification : instantanés et références de pages) ; `TestExposantDeLEnonce` (ces deux cas, Ex7, e^(x/2),
   x·e^(−x/3+1) ; famille de 60 fonctions tirées au hasard, e^{u/v}, P·e^{Q}, e^{Q}/v : tout exposant de f′ est un exposant de
   l'énoncé et f′ = dérivée de l'oracle mpmath).
2. **Q56, ligne des zéros de f′** (une seule rédaction, `_ligne_zeros`) : « f′(x) = 0 ⇔ P = 0 (car e^{…} > 0) ⇔ … (produit nul) »,
   P = produit des facteurs du numérateur qui ne sont pas des exponentielles (constante et dénominateur retirés, sans phrase, comme
   l'exemple de §7) ; un facteur x − a s'écrit directement x = a ; « (produit nul) » dès que deux facteurs s'annulent ; une seule
   équation : l'équation, puis ses solutions ; aucun zéro : la ligne « ne s'annule jamais » ne change pas. Tests : lignes exactes
   (Ex7, b, a, c, d, x³ − 3x, x³, (x² − 1)/(x − 3), x ln x, e^{2x}) ; propriété sur ≥ 25 fonctions avec l'oracle mpmath (le produit
   écrit s'annule là où f′ s'annule, chaque zéro final annule f′, exponentielles citées = lignes du tableau) ;
   `test_facteurs_evidents.py` suit la nouvelle ligne (même égalité exacte).
3. **Q32, guide R11** : « u, u′, v, v′ dans un tableau 2 × 2 » (D8) ; exemple 4 du guide (tableau u/v, nouvelle ligne des zéros) ;
   R7 décrit la ligne des zéros. Spécification de l'outil Dérivée (points 2 et 4, DV-17, DV-18).
4. Instantanés de l'outil Dérivée et de l'EC (moteur, `resoudre`, références de pages) régénérés et listés sous « À relire » (avant /
   après) ; suite complète ; temps natif ; commit « EC R1 : … » avec la nouvelle version de `decisions.md`.

### R2 (03.11.2026, session 2)

Corrections après relecture **propres à l'EC** : Q7, Q11, Q15, Q23, Q28, Q41, Q43 (decisions.md §7, §2 Extremums révisé). Tout dans
`etude-complete/parties.py` et `etude-complete/resoudre_ec.py` ; les outils ED, Dérivée, Limites, Exp-log ne changent pas (leurs
instantanés doivent rester identiques).
1. **Q7** (`resoudre_ec`) : si la dérivée sort du cadre, la carte « Dérivée » de l'outil Dérivée (`rdv.carte_derivee` : « Cette
   fonction sort du cadre de l'outil : la dérivée n'a pas été calculée. ») sous « 5. … » ; si la dérivée est calculée mais pas son
   signe, la carte d'erreur « Signe de f′ et variations » de l'outil Dérivée (CLAUDE.md : un résultat non traité donne un message
   clair). Jamais d'intertitre seul. Test : dérivée forcée hors du cadre, signe forcé non étudié.
2. **Q11** : partie 1, un dénominateur **trinôme unitaire** (x² + bx + c, b ≠ 0, c ≠ 0) à deux racines entières distinctes : « On
   résout x² − 3x + 2 = 0 ⇔ (x − 1)(x − 2) = 0 (Somme-Produit) ⇔ x = 1 ou x = 2 (produit nul). » (garde-fous de P3 : produit développé
   = polynôme, même ensemble que l'outil ED, valeur nulle aux racines) ; partie 3, même chaîne : un facteur x − r d'un produit s'écrit
   directement x = r (règle de Q56 dans l'outil Dérivée), « (x − 1)(x − 3) = 0 (Somme-Produit) ⇔ x = 1 ou x = 3 (produit nul) » au
   lieu de l'étape « x − 1 = 0 ou x − 3 = 0 ». Affine et ax² + c gardent la chaîne courte de P3 (x² − 4 = 0 ⇔ x² = 4, comme §2 b).
3. **Q15, Q28** : une seule écriture des valeurs approchées (`approchee`, TeX) **dans la formule**, après `\approx`, dans les parties
   2, 3 et 5 : `f(1) = −5e^{−2} ≈ −0,68`, `x = √6 ≈ 2,45`, `(0 ; e^{1/6}) ≈ (0 ; 1,18)`, `g(4) = … = 3/2, donc f(4) = e^{3/2} ≈ 4,48` ;
   entre 1000 et 10⁶, 2 décimales avec le séparateur des milliers ’ (`moteur/nombres.py`, convention du site, ajouté au manifeste de
   l'EC) ; R13 sous 10⁻³ et dès 10⁶ (inchangé).
4. **Q23** : tableau de signes de f (partie 3) avec une ligne par facteur de la factorisation **écrite dans la chaîne** (mise en
   évidence, Somme-Produit) : x² − 4x + 3 → x − 1, x − 3 ; x³ − 3x → x, x² − 3 ; x⁴ − 2x² → x², x² − 2. Garde-fou : le produit des
   lignes (constante comprise) est égal à f (SymPy exact et sonde mpmath), sinon les lignes d'avant ; la ligne f(x) reste confirmée par
   `confirmer_signe`.
5. **Q41** : une ligne de calcul pour **chaque** extremum : f = e^{u/v} avec g nommé et x₀ entier, la ligne « g(x₀) = …, donc f(x₀) =
   … » (P7b) ; sinon la substitution en chaîne « f(−2) = ((−2)² − 6)e^{−2·(−2)} = (4 − 6)e⁴ = −2e⁴ ≈ −109,20 » (substitution, puis
   puissances et produits de nombres calculés avec e^{ln q} = q et ln(e^q) = q, puis le reste, puis l'écriture de l'extremum), pour x₀
   rationnel, ln(q) ou e^{q}. Chaque membre est vérifié égal à f(x₀) (SymPy exact et sonde mpmath, machinerie `valeur_verifiee` de la
   partie 2) ; sinon pas de ligne.
6. **Q43** (§2 révisé) : « **Maximum global** en x = 0 : (0 ; 1) (f′ passe de + à −). Les autres valeurs de f sont plus petites
   (limites 0⁺ en ±∞). » quand c'est prouvé ; « **Maximum local** … Pas global : … » ; sinon « **Maximum local** … » seul. Mêmes
   garde-fous qu'en P7b.
7. Tests : `test_parties_ec.py` (lignes exactes mises à jour ; nouveaux tests : chaîne Somme-Produit d'une condition, lignes du
   tableau = facteurs écrits avec produit = f et garde-fou forcé, chaîne de valeur de chaque extremum relue et évaluée par l'oracle
   mpmath, garde-fous forcés, séparateur des milliers, format « Maximum global ») ; `test_corpus_etude_complete.py` (P4 cherche les
   valeurs dans la formule ; P7b attend « Maximum global » pour un extremum global) ; `test_resoudre_ec.py` (Q7) ;
   `test_resoudre_import.py` (nombres.py). Instantanés `resoudre` et références de pages de l'EC régénérés, listés sous « À relire » ;
   largeurs ; spécification ; suite complète ; temps natif ; commit « EC R2 : … ».

### P6 (03.11.2026, session 2)

Partie 4 de l'EC (D12, D13, D16), portée **EC + Limites** : une seule rédaction, dans l'outil Limites (`limites_asymptotes.py`,
`redaction_bh.py`, `resoudre_la.py`), reprise telle quelle par l'EC. Fractions rationnelles : méthodes anciennes inchangées (R18 du
guide des limites ; seul l'ordre des bornes change pour elles).
1. **D16, ordre** : `_bornes` rend −∞ (ou la borne finie de gauche), puis les valeurs interdites croissantes (gauche puis droite),
   puis +∞ (ou la borne finie de droite) ; études, asymptotes et bilan suivent cet ordre (les deux outils).
2. **D16, regroupement** (rendu, `resoudre_la.cartes_limites`, partagé) : les cartes de −∞ et de +∞ ne font qu'une, « x → ±∞ »,
   seulement si leurs étapes sont identiques une fois le symbole du point (−∞ / +∞ dans « x → … ») remplacé ; la conclusion devient
   celle « des deux côtés ». Les données d'`etudier()` ne changent pas (une étude par borne).
3. **D12, valeur d'essai** (`redaction_bh`, rédaction descendante, les deux outils) : forme k/0 en un point fini (bas → 0, haut ↛ 0),
   bas polynôme à coefficients rationnels autre que x, point a décimal : « bas : 6x − 12 → 0 ; avec x = 1,99 : 6 · 1,99 − 12 = −0,06 < 0,
   donc 0⁻ » (haut : substitution « 2² + 2 − 2 = 4 »). Garde-fous : x = a ± 0,01 (sinon 0,001…, jusqu'à 10⁻⁶), aucun autre zéro du bas
   dans [a ; x] (isolation exacte des racines par SymPy, après division exacte par (x − a)^m), aucune autre valeur interdite de f
   entre les deux, valeur exacte (fractions) du signe annoncé par les règles de calcul (0⁻) ; sinon l'écriture actuelle.
4. **D13, signe d'approche partout** : e^{0⁺} = 1⁺ « (e^t > 1 pour t > 0) » dans la descente, le résultat, le tableau de variations de
   l'EC (T06c) et le bilan ; le signe ℓ⁺ / ℓ⁻ d'une limite finie non nulle n'est écrit que s'il est donné par les règles **et**
   confirmé par une sonde mpmath (80 chiffres) du signe de f − ℓ ; bilan : les limites latérales des AV avec 0⁺ / 0⁻.
5. **D13, conclusions** (transcendantes) : AH « Asymptote horizontale : y = 0 (à gauche). f(x) → 0⁺ : le graphe est au-dessus. »
   (position seulement si le signe d'approche est démontré, comme ci-dessus) ; limite infinie en ±∞ sans asymptote oblique : « Pas
   d'asymptote horizontale à droite (f(x) → +∞). » — **retiré en cours de partie** : R6 du guide (imposé par CLAUDE.md) supprime
   cette phrase et les tests de style l'interdisent (question 67) ; AV d'un seul côté : « Asymptote verticale : x = 2, seulement du côté droit. À
   gauche, f(x) → 0⁺ : le graphe s'approche du point (2 ; 0), qui n'appartient pas au graphe (rond vide). » (l'autre côté « ? » :
   phrase actuelle) ; asymptote oblique, AV des deux côtés, trou, bord : phrases actuelles. Bilan : la position après l'AH.
6. Tests : retrait des 14 xfail P6 du corpus de l'EC ; tests de l'outil Limites sur l'ordre, le regroupement (et non-regroupement),
   la valeur d'essai (garde-fous forcés : autre zéro proche, point irrationnel, bas non polynomial), 1⁺ et la sonde forcée en
   désaccord, les phrases des conclusions ; tests existants dont la phrase exacte change : nouvelle phrase exacte (même force).
   Instantanés de l'outil Limites et de l'EC régénérés et listés sous « À relire » (avant / après) ; largeurs ; spécifications
   (Limites, EC) ; suite complète ; temps natif ; commit « EC P6 : … ».

### P9 (04.11.2026, session 2)

EC seule (D18, D20) : `etude-complete/index.html`, `etude-complete/parties.py`, `etude-complete/resoudre_ec.py` ; les outils ED,
Dérivée, Limites, Factorisation, Exp-log ne changent pas (leurs instantanés doivent rester identiques).
1. **D18** : Ex7 ajouté à la fin des exemples de la page (le premier exemple, celui du balayage des largeurs, ne change pas) ; a et c
   en exercices « difficile », b et d en « très difficile » (a, c : une exponentielle, un extremum ; b, d : deux extremums ou deux
   AV et quatre limites latérales). Les entrées de la page entrent d'elles-mêmes dans les instantanés et les tests de pages
   (`cas.entrees_page`) : a, b, c sont nouvelles (Ex7 et d y étaient déjà, cas limites de P3).
2. **D20, carte « Bilan de l'étude »** : sous « 6. Graphe », avant la carte « Graphique » (« à la fin, avant le graphe » ; D1 garde
   six intertitres), style `final` (cadre vert, comme le résultat final des autres outils). Une liste, une ligne par résultat, dans
   l'ordre de D20, chacune terminée par « (partie k) » : ED ; parité ; zéros ; signe ; f(0) ; chaque asymptote (avec la position) ;
   chaque extremum (nature et ≈). **Aucun calcul nouveau** : chaque ligne reprend un résultat déjà écrit et confirmé par sa partie
   (une seule source) :
   - ED : `ed_tex` de l'étude (celui de l'encadré de la partie 1) ;
   - parité : la conclusion de la partie 2 (`parties.partie2`, nouvelle : cartes + conclusion « paire », « impaire », « ni », ou
     rien si la partie ne conclut pas) ;
   - zéros, signe, f(0) : `parties.partie3` rend en plus les écritures de ses cartes (« x = √6 ≈ 2,45 », « f(0) = e^{1/6} ≈ 1,18 ») et
     les ensembles où f > 0 et f < 0, lus dans la ligne f(x) du tableau de signes **déjà confirmée** (`confirmer_signe` : SymPy et
     sonde, cases des intervalles et des points critiques), écrits comme l'ED (`ens_tex`) ; f de signe constant : « f(x) > 0 sur ED » ;
   - asymptotes : les lignes de la carte « Bilan des asymptotes » de la partie 4 (`resoudre_la.ligne_asymptote`), telles quelles ;
   - extremums : la ligne de la partie 5 sans sa justification (« **Maximum local** en x = 0 : (0 ; e^{1/6}) ≈ (0 ; 1,18) ») ;
     sans rédaction D11 (repli), la ligne de l'outil Dérivée ; aucun extremum : la phrase de la partie 5.
   Une partie qui ne conclut pas (doute, message) : sa ligne n'est pas écrite (option qui affiche le moins).
3. Tests : xfail P9 retirés (6) ; corpus (lignes du bilan contre l'oracle mpmath : parité, zéros, f(0), positions, extremums et ≈) ;
   `test_parties_ec.py` (lignes exactes d'Ex7, a–d ; pour toutes les entrées de la page et les cas limites : chaque ligne renvoie au
   résultat de sa partie (ses formules sont dans les cartes de la partie), ensembles du signe recoupés par l'oracle de `oracle.py` ;
   garde-fous forcés : partie 2 ou 3 en doute, ligne absente) ; `test_resoudre_ec.py` (ordre des cartes) ; `test_largeurs.py`
   (Ex7, a–d, corrigé complet de 320 à 1100 px : aucune faute du balayage, aucune formule hors de sa carte, bilan visible).
   Instantanés `resoudre`, moteur et références de pages de l'EC régénérés, listés sous « À relire » ; spécification.
4. **Mesure Pyodide** (`docs/chantiers/etude-complete/mesurer_pyodide.py`, navigateur et serveur des tests de pages, copie locale de
   Pyodide) : pour Ex7, a–d, une page neuve par mesure (le cache D19 fausserait une deuxième mesure dans la même page), du clic sur
   « Calculer ▶ » à la dernière carte affichée (bouton rendu, carte « Graphique » présente), 3 mesures, médiane ; une commande par
   fonction, limite de 5 minutes. **Captures** PNG à 390 px, page entière, corrigé complet (« Tout afficher ») : Ex7, a–d,
   e^(1/x), x/(x²+1), dans `docs/chantiers/etude-complete/captures/` ; vérifier que ce dossier n'est ni publié ni collecté.
5. Suite complète ; temps natif ; commit « EC P9 : … ».

## Temps natif de etudier() (s, médiane de 3 processus neufs)

| Partie | Ex7 | a | b | c | d |
|---|---|---|---|---|---|
| P0 | 0,59 | 0,02 | 0,42 | 0,18 | 0,30 |
| P1 | 0,63 | 0,02 | 0,42 | 0,19 | 0,30 |
| P2 | 0,60 | 0,02 | 0,43 | 0,18 | 0,32 |
| P3 | 0,59 | 0,02 | 0,42 | 0,19 | 0,30 |
| P4 | 0,60 | 0,02 | 0,43 | 0,18 | 0,29 |
| P5 | 0,59 | 0,02 | 0,43 | 0,19 | 0,29 |
| P7a | 0,64 | 0,02 | 0,42 | 0,20 | 0,31 |
| P7b | 0,64 | 0,02 | 0,43 | 0,20 | 0,30 |
| P8 | 0,58 | 0,03 | 0,36 | 0,26 | 0,21 |
| R1 | 0,58 | 0,03 | 0,35 | 0,25 | 0,21 |
| R2 | 0,67 | 0,03 | 0,42 | 0,30 | 0,24 |
| P6 | 0,76 | 0,03 | 0,41 | 0,27 | 0,27 |
| P9 | 0,73 | 0,03 | 0,35 | 0,26 | 0,23 |

P3 ne touche pas `etudier()` ; la partie 1 (`parties.cartes_domaine`, appelée par `resoudre`) coûte en plus 0,5 ms (Ex7), 0,2 ms (d),
moins de 0,01 ms (a, b, c).
P4 ne touche pas `etudier()` ; la partie 2 (`parties.cartes_parite`, appelée par `resoudre`, SymPy déjà chargé, médiane de 3 processus
neufs) coûte en plus 0,2 ms (Ex7 : ED non symétrique, sans SymPy), 4,8 ms (a), 7,2 ms (b), 8,6 ms (c), 6,2 ms (d).
P5 ne change pas la sortie d'`etudier()` (le tableau de f′ passe par `tableau_signes`, même calcul) ; la partie 3
(`parties.cartes_zeros_signe`, appelée par `resoudre`, SymPy déjà chargé, médiane de 3 processus neufs) coûte en plus 43 ms (Ex7),
5 ms (a), 61 ms (b), 44 ms (c), 27 ms (d) : surtout `solveset` et `simplify` (garde-fous du principe 0.2). Coût sous Pyodide à
mesurer en P9.
P7a : la rédaction D7 / D7b est calculée dans `etudier()` (outil Dérivée) : + 58 ms (Ex7, sous-carte) et + 16 ms (c, développement),
surtout les preuves SymPy de chaque ligne. Une première version (preuve par `simplify`) donnait Ex7 0,77 s et c 0,37 s (+ 95 %) ; la
preuve passe maintenant d'abord par `cancel(expand(…))` (exacte, rapide), `simplify` seulement si elle ne conclut pas.
P7b : `etudier()` ne fait aucun calcul de plus (D10 place une valeur déjà calculée ; l'écriture SymPy de la valeur est gardée) ; un
premier lancement a donné Ex7 0,77 s et b 0,48 s, le second (retenu, ci-dessus) 0,64 s et 0,43 s : bruit de la machine. Les extremums
D11 (`parties.blocs_extremums`, appelé par `resoudre`, SymPy chargé, médiane de 3) coûtent en plus 18 ms (Ex7), 16 ms (a), 30 ms (b),
23 ms (c), 22 ms (d) : surtout la sonde « global » (400 points par intervalle à 30 chiffres) et les comparaisons SymPy.
P8 : `etudier()` calcule maintenant la partie 3 (zéros et f(0) du graphique ; ses cartes sont reprises par `resoudre`, qui ne la
recalcule plus : le coût passe de `resoudre` à `etudier()`, 5 à 61 ms selon P5), les ronds vides (3 à 8 ms : limite par les règles,
e^{lim u}, au lieu de la limite de e^{u}, 200 à 290 ms) et le cadrage (élargissement pour les AH, courbe tracée une largeur au-delà de
chaque côté). a : 0,02 → 0,03 s (+ 5 à 10 ms, + 50 % à l'arrondi près : partie 3 et cadrage) ; c : 0,20 → 0,26 s (+ 30 %, surtout
la partie 3, 44 ms) ; Ex7, b, d : en dessous de P7b (bruit de la machine, mesures du même jour 0,56 à 0,58 s pour Ex7). Le temps de
`resoudre` (page) ne monte que des ronds vides et du cadrage. Question 55.
R1 : aucune hausse (la restitution de l'exposant de l'énoncé ajoute un `cancel` par exponentielle réécrite par SymPy ; la ligne des
zéros ne fait aucun calcul de plus).
R2 : aucune hausse due à R2 : le même script, lancé le même jour sur R1 (e38278c, code de R2 mis de côté), donne Ex7 0,70 s, a 0,03 s,
b 0,42 s, c 0,29 s, d 0,24 s (la machine est plus lente qu'au moment de la mesure R1). Dans `etudier()`, R2 n'ajoute que les lignes du
tableau de f (Q23), et seulement quand la chaîne de la partie 3 écrit une factorisation (aucune fonction du corpus) ; les lignes de
calcul des extremums (Q41) sont dans `resoudre` (`blocs_extremums`).
P6 : Ex7 + 12 à 19 % (valeurs d'essai en 2⁻ et 2⁺ : isolation exacte des racines du bas par SymPy, calculées deux fois par côté
comme toute la descente en un point interdit, `_narrer_cotes`) ; les autres dans le bruit. Même jour, même machine, HEAD (R2, 0acc931,
arbre séparé) : Ex7 0,64 s, a 0,03 s, b 0,51 s, c 0,35 s, d 0,30 s ; un premier lancement sur P6 avait donné Ex7 0,73 s, a 0,05 s,
b 0,63 s, c 0,34 s, d 0,28 s (bruit : b ne fait aucun calcul nouveau). Aucune hausse de plus de 50 % au-dessus de 0,1 s.
P9 : aucune hausse (le bilan ne fait aucun calcul : dans `etudier()`, la partie 3 garde en plus ses écritures des zéros et de f(0) et
les ensembles du signe, lus dans la ligne f(x) déjà confirmée ; la carte du bilan est écrite par `resoudre`).

## Temps sous Pyodide (P9)

Page réelle (`etude-complete/index.html`), navigateur et serveur des tests de pages (Chrome sans interface, copie locale de Pyodide
0.27.7, SymPy chargé avant « Prêt. »), script `docs/chantiers/etude-complete/mesurer_pyodide.py` : une page neuve par mesure (le
cache D19 ne sert pas), temps lu dans la page (`performance.now()`) du clic sur « Calculer ▶ » à la dernière carte affichée (bouton
rendu, dernière carte « Graphique »), largeur 390 px. Une commande par fonction, chacune sous `timeout 300` (31 s par fonction environ,
chargement des 3 pages compris) : aucune n'a dépassé sa limite. Mac de l'enseignant, 04.11.2026, sur le code de P9.

| Fonction | Mesure 1 (s) | Mesure 2 (s) | Mesure 3 (s) | Médiane (s) |
|---|---|---|---|---|
| Ex7 | 1,89 | 1,87 | 1,88 | 1,88 |
| a | 0,51 | 0,51 | 0,55 | 0,51 |
| b | 1,53 | 1,54 | 1,53 | 1,53 |
| c | 1,34 | 1,34 | 1,28 | 1,34 |
| d | 1,22 | 1,23 | 1,30 | 1,23 |

Aucun temps au-dessus de 30 s (le plus long, Ex7, 1,9 s ; délai de la page : 45 s). Le chargement de Pyodide et de SymPy (avant
« Prêt. ») n'est pas compté.

**Captures** (PNG, 390 px de large, page entière, corrigé complet après « Tout afficher », 1 px CSS = 1 px ; prises par le même script,
option `--capture`, première mesure de chaque fonction ; e^(1/x) et x/(x² + 1) avec `--n 0`) :

| Fichier | Fonction | Point ⏸ de decisions.md §7 à juger |
|---|---|---|
| `docs/chantiers/etude-complete/captures/Ex7-390.png` | e^((x² + x − 2)/(6x − 12)) | Q50 (échelle égale), Q51 (branche infinie en 2⁺ coupée en y), Q54 (étiquettes des points) ; carte « Bilan de l'étude » |
| `docs/chantiers/etude-complete/captures/a-390.png` | e^(−x²) | Q50 (fenêtre large et plate) |
| `docs/chantiers/etude-complete/captures/b-390.png` | (x² − 6)e^(−2x) | Q51 (branche vers +∞ en −∞ coupée), Q54 (étiquettes des zéros ±√6) |
| `docs/chantiers/etude-complete/captures/c-390.png` | eˣ(6 − eˣ) | Q50, Q51 (branche vers −∞ en +∞), Q54 (étiquette du zéro ln 6) |
| `docs/chantiers/etude-complete/captures/d-390.png` | e^(2/(x² − 4)) | Q46 (le tableau de variations défile à 390 px : il est capturé dans sa position de départ, à gauche), Q51 (deux AV) |
| `docs/chantiers/etude-complete/captures/e1x-390.png` | e^(1/x) | Q50, Q51 (branche en 0⁺), AH y = 1 des deux côtés (position) |
| `docs/chantiers/etude-complete/captures/x1-390.png` | x/(x² + 1) | Q50 (fenêtre plate : max et min à ±0,5), Q54 (zéro et (0 ; f(0)) confondus) |

Les captures sont dans `docs/` : **non publiées** et **non collectées**. Vérifié :
- `_config.yml` (GitHub Pages, Jekyll) exclut `docs` ; `tests/python/test_accueil.py::test_les_fichiers_internes_ne_sont_pas_publies`
  vérifie que `docs` reste dans cette liste ;
- aucune page publiée (`index.html`, pages des outils, `commun/`) ni `moteur/manifeste.json` (fichiers chargés par Pyodide) ne
  référence `docs/` (`grep -rln "docs/"` sur les .html, .js, .json hors de `docs/` et `tests/` : aucun fichier) ;
- les tests ne les lisent pas : pytest ne collecte que `tests/python` et `tests/pages` (`tests/lancer.py`, aucun fichier de
  configuration pytest dans le dépôt), et seulement des `test_*.py` ; aucun test ne nomme `captures/` (le seul « captures » des tests,
  `tests/pages/captures.py`, écrit dans un dossier passé en argument) ; les parcours de fichiers (`test_accueil.py` : `index.html` et
  `.md`, hors `docs` et `tests` ; `test_json_strict.py` : `.json` de `tests/python/instantanes`) ignorent les .png ;
- le serveur HTTP des tests de pages sert tout le dépôt sur 127.0.0.1 pendant les tests (comme avant), mais aucune page ni aucun test
  n'y demande `docs/` ;
- aucune règle ne les exclut du dépôt (`git check-ignore` : non ignorés ; `.gitignore` n'exclut que `docs/reference/` dans `docs`) :
  les 7 PNG (3,6 Mo en tout) sont commités avec P9.

## Suite complète

| Partie | Suite Python | Suite de pages | Date |
|---|---|---|---|
| P0 | 1052 passés, 66 xfail (659 s) | 116 passés (885 s) ; code de retour 0 | 02.11.2026 |
| P1 | 1062 passés, 61 xfail (641 s) | 116 passés (871 s) ; code de retour 0 (3ᵉ lancement, voir Écarts) | 03.11.2026 |
| P1 (contrôle du chef d'orchestre) | 1062 passés, 61 xfail (643 s) | 115 passés, 1 échec : `test_clavier.py::test_a_deux_formules…` (le test instable, voir Écarts) ; ce test seul sur P0 (5eadf34, sans P1) dans un arbre séparé : 1 échec sur 6 → défaut préexistant, P1 acceptée | 03.11.2026 |
| P2 | 1071 passés, 55 xfail (655 s) | 116 passés (880 s) ; code de retour 0 (2ᵉ lancement : le 1ᵉʳ a échoué sur `test_soc07_etapes`, adapté aux intertitres, voir Écarts) | 03.11.2026 |
| P2 (contrôle du chef d'orchestre) | 1071 passés, 55 xfail (649 s) | 116 passés (865 s) ; code de retour 0 | 03.11.2026 |
| P3 | 1091 passés, 48 xfail (637 s) | 116 passés (870 s) ; code de retour 0 (2ᵉ lancement : le 1ᵉʳ a échoué sur `test_resoudre_import`, liste de fichiers mise à jour, voir Écarts) | 03.11.2026 |
| P3 (contrôle du chef d'orchestre) | 1091 passés, 48 xfail (634 s) | 116 passés (886 s) ; code de retour 0 | 03.11.2026 |
| P4 | 1113 passés, 43 xfail (631 s) | 116 passés (873 s) ; code de retour 0 (1ᵉʳ lancement) | 03.11.2026 |
| P4 (contrôle du chef d'orchestre) | 1113 passés, 43 xfail (629 s) | 116 passés (875 s) ; code de retour 0 | 03.11.2026 |
| P5 | 1136 passés, 38 xfail (662 s) | 116 passés (870 s) ; code de retour 0 (1ᵉʳ lancement) | 03.11.2026 |
| P5 (contrôle du chef d'orchestre) | 1136 passés, 38 xfail (657 s) | 116 passés (885 s) ; code de retour 0 | 03.11.2026 |
| P7a | 1149 passés, 34 xfail (643 s) | 117 passés (914 s, dont le nouveau test de largeurs du tableau u/v) ; code de retour 0 (1ᵉʳ lancement) | 03.11.2026 |
| P7a (contrôle du chef d'orchestre) | 1149 passés, 34 xfail (657 s) | 116 passés, 1 échec : `test_clavier.py::test_a_deux_formules…` (le test instable, même symptôme : « effacer » laisse `(x^2-1)/(x-3)`) ; ce test seul sur P7a : 6 réussites sur 6 → P7a acceptée | 03.11.2026 |
| P7b | 1181 passés, 24 xfail (650 s) | 118 passés (939 s, dont le nouveau test de largeurs du tableau de variations) ; code de retour 0 (2ᵉ lancement : le 1ᵉʳ, arrêté avant la fin, pour corriger « Global … () » d'un ED fermé, √(4 − x²), vu en relisant des cas hors corpus) | 03.11.2026 |
| P7b (contrôle du chef d'orchestre) | 1181 passés, 24 xfail (667 s) | 118 passés (936 s) ; code de retour 0 | 03.11.2026 |
| P8 | 1220 passés, 21 xfail (689 s) | 119 passés (954 s, dont le nouveau test `test_graphique.py::test_d15_ronds_vides_et_points_marques`) ; code de retour 0 (1ᵉʳ lancement) | 03.11.2026 |
| P8 (contrôle du chef d'orchestre) | 1220 passés, 21 xfail (647 s) | 119 passés (923 s) ; code de retour 0 | 03.11.2026 |
| R1 | 1224 passés, 21 xfail (679 s) | 119 passés (908 s) ; code de retour 0 (1ᵉʳ lancement) | 03.11.2026 |
| R1 (contrôle du chef d'orchestre) | 1224 passés, 21 xfail (666 s) | 118 passés, 1 échec : `test_clavier.py::test_a_deux_formules…` (le test instable, même symptôme : « effacer » laisse `(x^2-1)/(x-3)`, page Limites, que R1 ne touche pas) ; ce test seul sur R1 : 3 réussites sur 6 → R1 acceptée | 03.11.2026 |
| R2 | 1240 passés, 21 xfail (930 s) | 120 passés (1202 s, dont le nouveau test `test_largeurs.py::test_lignes_de_calcul_et_valeurs_approchees`) ; code de retour 0 (1ᵉʳ lancement) | 03.11.2026 |
| R2 (contrôle du chef d'orchestre) | 1240 passés, 21 xfail (917 s) | 120 passés (1199 s) ; code de retour 0 | 03.11.2026 |
| P6 | 1273 passés, 7 xfail (713 s ; 1ᵉʳ lancement : 836 s, mêmes résultats) | 2ᵉ lancement : 119 passés, 1 échec : `test_clavier.py::test_a_deux_formules…` (le test instable, même symptôme : « effacer » laisse `(x^2-1)/(x-3)`) ; ce test seul : 5 réussites sur 6 ; 1ᵉʳ lancement : 16 échecs de `test_graphique.py::test_traces_egales_aux_references`, tous e^(1/x) (ordre des asymptotes, D16 : `graphique-traces.json` régénéré, voir « À relire »), `test_clavier` passé → P6 acceptée comme R1 | 03.11.2026 |
| P6 (contrôle du chef d'orchestre) | 1273 passés, 7 xfail (696 s) | 120 passés (929 s) ; code de retour 0 | 04.11.2026 |
| P9 | 1290 passés, 1 xfail (P10) (700 s) | 121 passés (930 s, dont le nouveau test `test_largeurs.py::test_corrige_et_bilan_de_l_etude`) ; code de retour 0 (2ᵉ lancement : le 1ᵉʳ a échoué dans la suite Python, 4 tests, voir Écarts, P9 ; la suite de pages n'avait pas été lancée) | 04.11.2026 |
| P9 (contrôle du chef d'orchestre) | 1290 passés, 1 xfail (708 s) | 120 passés, 1 échec : `test_clavier.py::test_a_deux_formules…` (le test instable, même symptôme : « effacer » laisse `(x^2-1)/(x-3)`) ; ce test seul sur P9 : 5 réussites sur 6 → P9 acceptée | 04.11.2026 |
| Résumé de la session 2 (sur 72ff3bb, suivi.md seul modifié) | 1290 passés, 1 xfail (720 s) | 121 passés (940 s) ; code de retour 0 (1ᵉʳ lancement) | 04.11.2026 |

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

- P2 : `docs/choix-techniques.md` (description du format de sortie et du rendu commun) reçoit une ligne pour le nouveau style de carte
  `partie` : sans elle, la documentation du format serait fausse. `parties.py` n'est pas créé à P2 (aucune partie n'a encore de contenu
  propre à l'EC) : la spécification l'annonce pour P4, avec sa déclaration dans `moteur/manifeste.json`.
- P2 : `tests/pages/test_comportement.py::test_soc07_etapes` (« Étape suivante révèle exactement une carte ») comptait toutes les cartes
  cachées, intertitres compris : il échouait sur l'EC (19 cachées pour 14 étapes). Il compte maintenant les cartes cachées hors intertitres
  et vérifie **en plus** qu'un intertitre n'est jamais la dernière carte visible ; pour les autres outils, rien ne change.
- P3 : `tests/python/test_resoudre_ec.py` suit la nouvelle partie 1 : l'ordre attendu des cartes est maintenant calculé depuis
  l'analyse de l'outil ED (une carte « Condition k » par condition, « Mise en forme » quand `parties.mise_en_forme` en donne une,
  « Ensemble de définition ») au lieu de la seule carte « Fonction » : vérification plus forte. La ligne « ED = ]0 ; +∞[ » de la carte
  « Fonction » de ln(x)/x est vérifiée dans la carte « Ensemble de définition » (encadrée) ; nouveau test : ED et conditions identiques
  à l'outil ED (EC-01).
- P3 : `moteur/noyau.py` réexporte `conditions` (liste (genre, arbre) des conditions d'existence, celle qu'utilise l'analyse), pour que
  `parties.py` n'importe que du noyau (`test_noyau.py`) ; `ensemble_def.py` ne change pas. Ex7 et d entrent dans `CAS_LIMITES` de l'EC
  (`tests/python/cas.py`, cités dans la spécification) : aucune entrée des pages n'a de carte « Mise en forme », et sans eux elle
  n'aurait ni instantané ni rendu de page testé (P9 les mettra dans les exemples, D18).
- P3 : `tests/python/test_resoudre_import.py` (import à plat de l'EC avec les fichiers d'une page) reçoit les deux fichiers ajoutés au
  manifeste (`resoudre_ed.py`, `parties.py`) : même vérification, liste à jour (1ᵉʳ lancement de la suite complète en échec sur ce point).
- P4 : `tests/python/test_resoudre_ec.py::test_ordre_des_cartes_comme_la_page` place sous « 2. Parité » les titres des cartes de
  `parties.cartes_parite` (comme « Mise en forme » à P3) : le reste de l'ordre est vérifié comme avant ; le contenu de la partie 2 est
  vérifié à part (`test_parties_ec.py` : cartes exactes, oracle mpmath, garde-fous ; `test_resoudre_place_la_parite_sous_son_intertitre`).
  La spécification `docs/specifications/etude-complete.md` décrit la partie 2 (sinon elle serait fausse : « 2 vide »).

- P5 : `derivee-variations/derivee_variations.py` : le bloc d'`etudier` qui construit les points critiques et le tableau de signes
  (R7) devient la fonction publique `tableau_signes` (et deux petites fonctions `_point_test`, `_zone_hors`), appelée par `etudier` et
  par la partie 3 de l'EC ; même calcul : instantanés de l'outil Dérivée et sortie d'`etudier()` de l'EC identiques.
- P5 : `parties.py` : `factorisation` (partie 1) s'appuie sur `_factoriser` (facteurs exposés pour la chaîne de la partie 3),
  `resolution_denominateur` sur `resolution_polynome`, `valeur_en` (partie 2) sur `valeur_verifiee` (partagée avec f(0)) : sorties
  inchangées (parties 1 et 2 des instantanés identiques). `plier` calcule aussi 1^p = 1 et 0^p = 0 (p > 0) : f(0) de x^(2/3) s'écrit
  « 0 » et non « ∛(0²) » ; aucune carte de parité des instantanés ne change.
- P5 : `tests/python/test_resoudre_ec.py::test_ordre_des_cartes_comme_la_page` place sous « 3. Zéros, signe, ordonnée à l'origine » les
  titres des cartes de `parties.cartes_zeros_signe` (comme la partie 2 à P4) : le reste de l'ordre est vérifié comme avant ; le
  contenu est vérifié à part (`test_parties_ec.py` : cartes exactes, oracle mpmath, garde-fous ; `test_resoudre_place_la_partie_3…`).
  La spécification décrit la partie 3 (sinon elle serait fausse : « 3 vide »).

- P7a : les tests qui lisaient le texte des étapes de la dérivée par `it["html"]` (`test_derivee_narration.py`,
  `test_proprietes_derivee.py`, `test_racines_reelles.py`, `test_derivee_exposant_irrationnel.py`) lisent maintenant tout le texte de
  l'étape (`moteurs.texte_etape` : html d'un texte, toutes les chaînes d'un tableau `uv` ou d'une sous-carte) : mêmes vérifications,
  étendues aux cases du tableau et aux lignes de la sous-carte (`test_racines_reelles` garde `get("html", "")` pour les étapes du signe,
  comme avant). `test_facteur_negatif_entre_parentheses` attend `(x² − 6) \cdot (−2e^{−2x})` (parenthèses et point, D7) au lieu de
  `(x² − 6)\,(−2e^{−2x})` : même force (le refus de `\cdot -` reste).
- P7a : `docs/specifications/derivee-variations.md` (point 2, « Dérivée ») décrit le tableau u/v, la sous-carte et le développement
  d'abord (sinon elle serait fausse). Le guide de rédaction (R11 : « u, u', v, v' sur une ligne ») n'est pas modifié : D8 (tableau) le
  remplace pour ces deux règles (question 32).
- P7a : l'écart de P1 « parenthèses sans point » est résorbé : `(x² − 6)·(−2e^{−2x})` (outil Dérivée et EC), par `_tex_brut`, qui
  n'écrit autrement que `tex` ; les autres produits gardent l'écriture de `tex` (`(2x + 1)(6x − 12)`, `(x² + x − 2)·6`).

- P7b (D10) : pas de « drapeau du tableau » à part : D10 vaut pour les deux outils, la case d'un extremum prend le type `val:` qui existe
  déjà (valeur de f là où f′ n'est pas définie, même rendu `.pt` dans `commun/rendu.js`, inchangé) ; « extremum » (•) reste pour une
  valeur inconnue. Chaque extremum de `etudier()` (outil Dérivée) reçoit deux champs techniques, `x_py` et `f_py` (écritures SymPy, pour
  les garde-fous de l'EC), jamais affichés ; `tests/python/test_resoudre_dv.py` les ajoute à `TECHNIQUE` (champs non affichés, comme
  `domaine_etude_tex`) : même vérification pour tout le reste. Ils figurent aussi dans le bloc du graphique de l'EC (liste des extremums
  passée telle quelle, `test_resoudre_ec.py::test_graphique`).
- P7b : `tests/python/test_tableau_variations.py` attend la valeur à la place de « extremum » (ln(x)/x : `val:e^{-1}`, √(4 − x²) :
  `val:2`, 1/(2x² − 4x + 1) : `val:-1`) : vérification plus forte ; nouveau test `TestValeursDesExtremums` (chaque extremum, valeur
  recoupée par l'évaluateur, cas « ? » et ≈ forcés).
- P7b : `tests/python/test_corpus_etude_complete.py::test_P6_regroupement_infini` (xfail P6 inchangé) cherchait « ±∞ » dans toutes les
  cartes ; la partie 5 écrit maintenant « (limites 0⁺ en ±∞) » (D11, mots de decisions.md) pour a, ce qui faisait passer le test xfail
  (XPASS) sans que D16 soit fait. Il cherche « ±∞ » dans la partie 4 seule (la partie que vise D16), et vérifie que cette partie
  n'est pas vide : même force pour D16.
- P7b (largeurs) : avec les valeurs, le tableau de variations défile horizontalement (repli du composant commun `.tsigne` : libellés
  fixes, aucune faute du balayage) à 320 px pour Ex7 (comme avant), de 320 à 390 px pour d (avant : 320 à 375 px) et pour
  (x² − 1)/(x − 3) dans l'outil Dérivée (comme avant). Nouveau test `test_largeurs.py::test_tableau_de_variations_avec_valeurs`.

- P8 : `etude_complete.etudier()` appelle maintenant la partie 3 (`parties.partie3`) et `parties.ronds_vides` (données du graphique,
  D15) : `etude_complete` importe `parties` (le module restait un assemblage sans calcul propre ; les garde-fous sont dans `parties.py`).
  La partie 3 est calculée une fois par étude (`etude_et_partie3`, `resoudre` en reprend les cartes) ; pas de cache entre deux appels
  (un test qui fausse un garde-fou laisserait sinon un résultat faussé en cache). `cartes_zeros_signe` garde sa sortie.
- P8 : les « trous » de l'outil Limites (limites finies égales, ou bord de l'ED) gardent leur dessin (d'après la partie Limites, qui
  les écrit déjà « trou dans le graphique ») ; seuls les nouveaux ronds vides (`ronds_vides`) passent par la double confirmation.
  `tests/python/test_corpus_etude_complete.py::ronds_vides_de_l_outil` (P0) les additionne déjà : inchangé.
- P8 : `tests/python/test_resoudre_ec.py::test_graphique` vérifie en plus `points` et `ronds_vides` du bloc ; `docs/choix-techniques.md`
  (exemple du bloc `graphique`, clés facultatives) et la spécification (partie 6, EC-16) sont mis à jour (sinon ils seraient faux).
- P8 : la courbe est échantillonnée une largeur de fenêtre au-delà de chaque côté (l'écran, à échelle égale, montre souvent plus large
  que la fenêtre) : environ 3 fois plus de points dans le bloc du graphique (fenêtre et cadrage inchangés par ce tracé).

- R1 : `tests/python/test_facteurs_evidents.py::test_racine_positive_et_carre_au_denominateur` attend la nouvelle ligne des zéros
  (« f′(x) = 0 ⇔ 8x − 1 = 0 ⇔ x = 1/8 ; valeur interdite : x = −2 », Q56) au lieu de « f′(x) = (8x − 1)/(…) = 0 ⇔ … » : même égalité
  exacte, même force. Exemple 4 du guide mis à jour de même (et le tableau u/v, Q32) ; sa ligne f(x) garde « min » (D10, P7b, hors R1).
- R1 : e^((x²+1)/(2x)) et e^((−2x²+3x−1)/(3x−6)) entrent dans les cas limites de l'outil Dérivée (`tests/python/cas.py`), cités dans
  la spécification (point 2, DV-17) : 2 entrées nouvelles dans les instantanés et les références de pages de la Dérivée (Q37,
  « ajouter au corpus »). La famille tirée au hasard est dans `test_derivee_narration.py` (`TestExposantDeLEnonce`).

- R2 : `1/(x^2-3x+2)` entre dans les cas limites de l'EC (`tests/python/cas.py`, cité dans la spécification) : aucune entrée de la page
  n'a de dénominateur résolu par Somme-Produit (Q11) ni d'extremum en un x₀ fractionnaire (Q41) ; 1 entrée nouvelle dans les
  instantanés (`etudier()` et `resoudre`) et les références de pages de l'EC.
- R2 : `moteur/nombres.py` (notation suisse, séparateur des milliers ’, déjà chargé par l'outil Exp-log) entre dans le manifeste de
  l'EC (Q28) ; `tests/python/test_resoudre_import.py` reçoit ce fichier (même vérification, liste à jour).
- R2 : `tests/python/test_corpus_etude_complete.py` : P4 cherche les valeurs approchées dans la formule (`maths`, « f(1) = −5e^{−2} ≈
  −0,68 » en entier, au lieu de « −0,68 » seul dans le texte : vérification plus forte) ; P7b attend « Maximum global » pour un
  extremum global et « Maximum local » sinon (§2 révisé), et compte les « global</b> » (au lieu de tous les mots « global ») : même
  force. `test_resoudre_ec.py::test_ordre_des_cartes_comme_la_page` : la carte « Dérivée » est toujours attendue (Q7).
- R2 : `tests/python/test_parties_ec.py` : lignes exactes mises à jour (≈ dans la formule, Somme-Produit, lignes du tableau, chaînes de
  valeur, « Maximum global ») ; l'oracle des zéros relit maintenant aussi les zéros écrits avec ln (x = ln(6) de c n'était pas relu :
  vérification plus forte) ; la lecture des formules (`nombre_affiche`) comprend les puissances, `\cdot` et `\sqrt[3]` pour relire
  chaque membre des chaînes de valeur ; « 1/(x^2-3x+2) » passe de la liste « laissées à l'outil ED » à la liste des chaînes
  (Somme-Produit), remplacé dans la première par quatre formes qui y restent (Δ non carré, racine double, sans terme constant, non
  unitaire). Nouveau test de largeurs `test_largeurs.py::test_lignes_de_calcul_et_valeurs_approchees` (b et 1/(x² − 3x + 2), 320 à
  1100 px : aucune faute, aucune formule hors de sa carte).

- P6 : `tests/python/test_redaction_limites.py` : les phrases exactes des conclusions transcendantes suivent D13 (« Asymptote
  horizontale : y = 0 (à gauche). f(x) → 0⁺ : le graphe est au-dessus. », « Asymptote verticale : x = 0, seulement du côté droit. … (rond
  vide). », « (à droite) » pour √…) : même égalité exacte, même force. `test_resoudre_la.py::test_phrases_des_asymptotes` : bilans dans
  l'ordre de D16 ((x³ + 1)/(x − 2) : les deux lignes « branche parabolique » sont les lignes 1 et 3), plus le bilan de l'Ex7 (position,
  0⁺). `test_limites_deux_cotes.py` : e^(1/x) a pour limite à gauche « 0^{+} » (au lieu de « 0 ») : plus précis.
- P6 : `test_resoudre_la.py` et `test_resoudre_ec.py` (« rien de perdu », ordre et nombre des cartes) comparent la sortie de `resoudre`
  aux études **affichées** (`rla.etudes_affichees` : x → ±∞ regroupés, D16) ; la clé `conclusion` (données du regroupement, jamais
  affichées) rejoint `TECHNIQUE`. Le regroupement lui-même est vérifié à part (`test_limites_d12_d16.py` : étapes identiques au symbole
  près, même limite par l'oracle mpmath, une étude de moins exactement).
- P6 : `test_tableau_limites.py::test_corpus_egal_a_la_partie_limites` (EC-10) : les limites latérales (asymptote verticale) sont
  comparées **avec** leur signe (les deux sont signées par la même fonction : plus fort qu'avant) ; en ±∞, la valeur sans le signe
  (la phrase écrit y = 1) **et** le signe comparé à la position de l'AH (« au-dessus » ⇔ ⁺) : plus fort qu'avant.
- P6 : `limites_asymptotes.etudier` : la boucle des bornes passe dans `_etudier_bornes` (même code), pour vider dans un `finally` la
  liste des bornes de l'ED que lit le garde-fou de la valeur d'essai (jamais de bornes périmées hors d'une étude).

- P9 : `test_resoudre_ec.py::test_ordre_des_cartes_comme_la_page` attend la carte « Bilan de l'étude » entre « 6. Graphe » et
  « Graphique » ; `test_partie_5_jamais_vide` vérifie en plus qu'aucune ligne « (partie 5) » n'est au bilan quand la partie 5 ne
  conclut pas (même force, une vérification de plus).
- P9 : `test_P9_bilan_de_l_etude` (corpus) vérifiait seulement la présence de la carte ; il vérifie maintenant ses lignes contre
  l'oracle (plus fort).
- P9 : `test_P7b_extremums` (corpus) comptait « global</b> » et « pas global » dans **tout** le texte de la sortie ; le bilan reprend
  la nature des extremums (« **Maximum global** … »), donc le compte doublait (1ᵉʳ lancement de la suite complète : 3 échecs, a, b,
  c). Le test lit maintenant les cartes de la partie 5 seules (mêmes vérifications, même force) ; les lignes du bilan sont vérifiées
  par `test_P9_bilan_de_l_etude`. Même lancement : `test_bilan_avec_la_liste_de_l_outil_derivee` (nouveau) attendait « minimum en … »
  au lieu de « minimum local en … » (écriture de la liste de l'outil Dérivée) : attente corrigée.

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
7. **P2, partie 5 sans dérivée** : quand la dérivée sort du cadre de l'outil, l'Étude complète n'affichait aucune carte de dérivée (l'outil
   Dérivée affiche « Cette fonction sort du cadre de l'outil : la dérivée n'a pas été calculée. »). L'intertitre « 5. Dérivée, tableau de
   variation, extremums » reste alors seul (option qui affiche le moins). Faut-il y mettre la phrase de l'outil Dérivée ? Aucune fonction du
   corpus ni des exemples n'est concernée.
8. **P2, « 6. Graphe » puis la carte « Graphique »** : le titre de la carte répète l'intertitre. Gardé tel quel (titre de la carte du
   graphique, attendu par les tests de pages) ; à revoir en P8 si vous préférez une carte sans titre.
9. **P2, parties 2 et 3 vides** : jusqu'à P4 et P5, l'élève voit les intertitres « 2. Parité » et « 3. Zéros, signe, ordonnée à
   l'origine » sans rien dessous (un clic sur « Étape suivante » montre d'un coup 2, 3, 4 et la première carte des limites). Ne pas
   fusionner la branche dans cet état sans P4 et P5.

10. **P3, quand afficher la carte « Mise en forme »** : seulement si f(x) = e^{haut/bas}, haut et bas de degré ≥ 1 écrits développés, et
    si l'un des deux se factorise (mise en évidence de c·xᵏ, Somme-Produit à racines entières). d n'en a pas (haut constant, comme le
    .tex) ; f = P(x)·e^{…}, un exposant non rationnel, un coefficient dominant négatif ou un trinôme à racines non entières non plus
    (option qui affiche le moins). Faut-il l'étendre (par exemple nommer g(x) même sans factorisation) ?
11. **P3, chaîne courte limitée** aux dénominateurs affines et ax² + c : un autre trinôme garde la rédaction de l'outil ED (Δ et zéros),
    par exemple x² − 3x + 2. Voulez-vous aussi « x² − 3x + 2 = 0 ⇔ (x − 1)(x − 2) = 0 (Somme-Produit) ⇔ x = 1 ou x = 2 » ?
12. **P3, « On résout … »** : écrit comme decisions.md §4 et le .tex, alors que R10 (outil ED) a retiré « On résout » (« condition ⇔
    solution »). L'inégalité de l'outil ED reste au-dessus (« 6x − 12 ≠ 0 »). À confirmer.
13. **P3, conclusion de l'outil ED reprise telle quelle** : pour ln(x)/x, « ED = ]0 ; +∞[ = ]0 ; +∞[ » (l'intersection des deux
    conditions est déjà ]0 ; +∞[ ; même écriture dans l'outil ED). Gardée pour que l'ED soit celui de l'outil ED (EC-01) ; à corriger
    dans l'outil ED si vous le souhaitez.
14. **P3, Somme-Produit aussi pour a² − b²** : x² − 9 = (x + 3)(x − 3) (Somme-Produit), facteurs par racine croissante, alors que R10
    (outil ED) factorise a² − b² directement. Une seule méthode pour tous les trinômes unitaires (principe 6) ; à confirmer.

15. **P4, « ≈ » hors de la formule** : « \(f(1) = −5e^{−2}\) ≈ −0,68 » ; la valeur approchée est écrite en texte (virgule, signe
    « − »), après la formule, et non dans la formule (« 0{,}68 ») comme les autres outils : le test du corpus (P0) la cherche telle
    quelle dans le texte. À l'écran, la police du « ≈ −0,68 » est celle du texte. Faut-il la passer dans la formule ?
16. **P4, cartes de la partie 2** : toujours une carte « Symétrie de l'ED » d'abord (« ED est symétrique par rapport à 0. », même pour
    ED = ℝ, que le .tex ne dit pas : même suite d'étapes pour toutes les fonctions, principe 6), puis « Calcul de f(−x) » ou « Pas
    impaire » et « Pas paire » ; la conclusion en gras (« Donc f est paire. ») à la fin de la dernière carte. La phrase « une fonction
    impaire vérifie f(0) = 0 » vient du .tex (c).
17. **P4, propriétés de la chaîne** : la 1ʳᵉ ligne porte « (on remplace x par −x) » (absent du .tex) ; les signes sont justifiés par
    « règle des signes » (x³ − 3x : « car (−x)³ = −x³ ; règle des signes »), une somme impaire passe par « −(x³ − 3x) (mise en
    évidence de −1) » avant « = −f(x) ». Les mots vous conviennent-ils ?
18. **P4, chaîne non rédigée** : quand la parité est confirmée (SymPy et sonde) mais ne se lit pas sur l'arbre (e^x + e^(−x),
    x^(1/3), (x³ − x)²), l'outil écrit « Le calcul de f(−x) n'a pas pu être rédigé par l'outil : la parité n'est pas traitée. » (option
    qui affiche le moins). Aucune entrée de la page ni du corpus n'est concernée.
19. **P4, valeurs des contre-exemples** : a est pris dans 1, 2, 1/2, 3, 4, 1/3, 5 ; une valeur hors de [10⁻³ ; 1000[ fait passer au a
    suivant (notation scientifique : question 1 ; séparateur des milliers ’ : pas encore dans l'EC) ; un entier exact s'écrit sans
    « ≈ » (question 2 : f(1) = 0, f(−1) = 8) ; un f(0) non entier s'écrit « f(0) = … ≠ 0 (≈ 0,61) ». L'écriture exacte est la
    substitution, constantes rationnelles calculées, sans autre simplification : (e^x − 1)/x donne f(−1) = −(e^{−1} − 1) (et non
    1 − e^{−1}).
20. **P4, point a d'un ED non symétrique** : d'abord le symétrique d'une borne rationnelle exclue (Ex7 : −2 ; (x² − 1)/(x − 3) : −3),
    sinon le premier de 1, −1, 2, −2, 1/2… (ln(x)/x : « 1 ∈ ED, mais −1 ∉ ED » ; √(x + 1) : « 2 ∈ ED, mais −2 ∉ ED »).
21. **P4, b : −36,95** : le .tex écrit f(−1) ≈ −36,9 ; decisions.md §5 écrit −36,95 (2 décimales, §2) : c'est −36,95 qui est affiché.

22. **P5, chaîne une étape par ligne** : decisions.md §2 écrit la résolution sur une ligne ; elle est écrite une étape par ligne
    (principe 5, comme la chaîne f(−x) de P4) : « (x² − 6)e^{−2x} = 0 », « ⇔ x² − 6 = 0 (car e^{−2x} > 0) », « ⇔ x² = 6 »,
    « ⇔ x = −√6 ≈ −2,45 ou x = √6 ≈ 2,45 ». La valeur approchée suit chaque zéro (et non « ≈ ±2,45 » en bout de chaîne) : une seule
    écriture pour un ou plusieurs zéros, symétriques ou non. À confirmer.
23. **P5, tableau de f avec les facteurs écrits** : le tableau prend les facteurs de f tels que saisis (machinerie R7) : x² − 4x + 3 a
    une seule ligne « x² − 4x + 3 » puis f(x), bien que la chaîne l'ait factorisé en (x − 1)(x − 3) (Somme-Produit). Faut-il une ligne
    par facteur de la factorisation de la chaîne ?
24. **P5, phrase de l'exponentielle** : écrite comme decisions.md §2 (« … strictement positive) ; il ne s'annule jamais. ») ; « pour
    tout x ∈ ED » quand ED ≠ ℝ (Ex7, d, e^(1/x)), « pour tout x » sinon ; f = e^{…} seule : phrase de §4 sans « il ne s'annule
    jamais », puis « Donc f n'a pas de zéro et f(x) > 0 sur ED. ».
25. **P5, propriétés ajoutées** (absentes de decisions.md) : « numérateur nul » (quotient : (x² − 1)/(x − 3) = 0 ⇔ x² − 1 = 0),
    « on divise par 3 » (3x ln x), « produit nul », « mise en évidence », « Somme-Produit », et celles de l'outil ED (« on ajoute 1 »,
    « on isole e^x du côté où son coefficient est positif »). Un zéro hors de l'ED : « x = 0 est rejeté, car 0 ∉ ED. ». Les mots
    vous conviennent-ils ?
26. **P5, formes que la chaîne ne couvre pas** (√(x² − 4), x² + 1, x³ − 12x² + 44x − 48, trinôme à Δ non carré) : les lignes de
    l'outil ED telles quelles (« On résout … », Δ, « Solutions : … »), puis « Donc x = −2 ou x = 2. ». Faut-il une autre rédaction ?
27. **P5, le point (0 ; f(0))** : « Le graphe coupe l'axe des y au point (0 ; e^{1/6}). » (le .tex écrit « Point (0 ; e^{1/6}) ») :
    phrase symétrique de « 0 ∉ ED : le graphe ne coupe pas l'axe des y » (decisions.md §2).
28. **P5, valeurs approchées** : R13 appliqué (question 1) : notation scientifique sous 10⁻³ et dès 10⁶ (« ≈ 4,540 × 10⁻⁵ ») ; entre
    1000 et 10⁶, aucune valeur approchée (la valeur exacte seule, option qui affiche le moins) tant que le séparateur des milliers
    n'est pas tranché pour l'EC (question 19). Aucune valeur du corpus n'est concernée.
29. **P5, après le tableau** : aucune phrase de conclusion (« f(x) > 0 sur … ; f(x) < 0 sur … ») : le tableau la porte (option qui
    affiche le moins). En voulez-vous une ?
30. **P5, sans zéro mais avec changement de signe** (e^x/x, 1/x, x/√(x²)) : « Donc f n'a pas de zéro. » puis le tableau (decisions.md
    ne prévoit la phrase « f(x) > 0 sur ED » sans tableau que pour un signe constant).

31. **P7a, quand la sous-carte « Dérivée de l'exposant »** : seulement si f = e^{u/v}, u et v polynômes écrits développés à
    coefficients entiers, v non constant (Ex7, d, e^(1/x)). Un exposant polynôme (a : −x², e^(x²)) garde la phrase « de la forme e^u »
    (le .tex de a n'a pas de sous-carte) ; e^(−1/x) aussi (la règle du quotient donnerait « −(−1) »), de même un exposant non développé
    ((x + 1)²/(x − 1)), à coefficient non entier, ou f = P(x)·e^{u/v} (option qui affiche le moins). Faut-il l'étendre ?
32. **P7a, place du tableau u/v** : « On applique la règle du produit, (uv)′ = u′v + uv′, avec : », le tableau, puis les justifications
    des dérivées (R11 : « (x²)′ = 2x (règle de la puissance) », « e^{−2x} est de la forme e^u avec u(x) = −2x … »), puis la ligne f′.
    Le nom u de la phrase « de la forme e^u » n'est pas le u du tableau (comme avant P7a, où « On pose u(x) = x² − 6 » précédait la
    même phrase). Le guide (R11) dit encore « u, u', v, v' sur une ligne » : à mettre à jour si le tableau vous convient.
33. **P7a, forme finale de g′** : la chaîne s'arrête après la simplification par le pgcd (mise en évidence de c·xᵏ seulement, pas de
    Somme-Produit) : d donne g′(x) = −4x/(x² − 4)² (comme le .tex), mais f′ encadré garde l'écriture factorisée de l'outil,
    −4x·e^{…}/((x − 2)²(x + 2)²). De même, x² − 6x + 1 ou 2x² − 8x + 5 restent tels quels.
34. **P7a, résultat encadré** : la ligne « On remplace g′(x) dans f′(x) = g′(x)·e^{g(x)} : » précède le résultat encadré habituel
    f′(x) = x(x − 4)e^{g}/(6(x − 2)²) (écriture de l'outil, une seule exponentielle, avec l'exposant écrit en entier), et non
    « f′(x) = x(x − 4)/(6(x − 2)²) · e^{g(x)} » du .tex : changer l'écriture de f′ changerait la ligne des zéros et le tableau de signes.
35. **P7a, mots de la sous-carte** : étapes « Étape 1 : règle du quotient. » et « Étape 2 : calcul du numérateur, puis
    simplification. » (rendu du bloc `sous_calcul` des limites) ; propriétés « (règle du quotient) », « (développement) » — « (calcul) »
    quand aucun produit de sommes n'est développé (d : −2·2x = −4x) —, « (réduction) », « (mise en évidence) », « (simplification par
    6) » ; dénominateur (6x − 12)² écrit 36(x − 2)² dès la ligne du développement (decisions.md §4 ; (−6x − 18)² = 36(x + 3)²). La
    phrase d'entrée nomme g(x) = (x² + x − 2)/(6x − 12) (écrit développé), alors que la carte « Mise en forme » de l'EC le nomme sous
    forme factorisée.
36. **P7a, D7b** : après le développement, la dérivée de la somme suit la rédaction habituelle (« (6eˣ)′ = 6·(eˣ)′ = 6eˣ », phrase de
    e^{2x}, puis « f′(x) = 2eˣ(3 − eˣ) ») ; la ligne du .tex « f′(x) = 6eˣ − 2e^{2x} = 2eˣ(3 − eˣ) (on a mis 2eˣ en évidence) »
    n'est pas écrite (changement de la rédaction de toutes les sommes de l'outil). Critère : f = produit de deux sommes de c·e^{kx}
    (k ≥ 1 entier) et de constantes entières, une exponentielle dans chacune ; e^{−x}(eˣ + 1), (eˣ + 1)², eˣ(eˣ + x) gardent la
    rédaction habituelle.
37. **P7a, écart à D6 vu en passant (non corrigé, hors corpus)** : l'exposant de f′ n'est pas toujours celui de l'énoncé :
    e^((x² + 1)/(2x)) donne f′ avec e^{(½x² + ½)/x}, et e^((−2x² + 3x − 1)/(3x − 6)) réordonne le haut (3x − 2x² − 1). Cela vient du
    `_simplifier` de P1 (SymPy) ; à corriger avec P7b ou à part ?
38. **P7a, « · » seulement devant un facteur négatif** : (x² − 6)·(−2e^{−2x}), x²·(−e^{−x}), (3x² + x − 3)·(−6) ; deux parenthèses
    positives restent côte à côte, (2x + 1)(6x − 12), comme dans l'outil.
39. **P7a, temps** : aucune hausse de plus de 50 % (Ex7 + 8 %, c + 5 %, d + 7 %).

40. **P7b, raison de « pas global »** : la limite (ou l'extremum) la plus extrême, puis la première dans l'ordre du tableau (−∞, valeurs
    interdites de gauche à droite, +∞). Ex7, b et le minimum d'Ex7 donnent la raison de decisions.md ; **d donne « f(x) → +∞ quand
    x → −2⁻ »** et non « x → 2⁺ » (§5 d) : aucune règle simple ne redonne les quatre raisons du corrigé (Ex7 max : 2⁺ plutôt que +∞ ;
    Ex7 min : −∞ plutôt que 2⁻ ; d : 2⁺ plutôt que −2⁻). Laquelle préférez-vous ?
41. **P7b, valeur en chaîne** : écrite pour **chaque** extremum quand la carte « Dérivée » a nommé g (f = e^{u/v}) et que x₀ est entier :
    Ex7 a donc aussi « g(0) = −2/(−12) = 1/6, donc f(0) = e^{1/6} ≈ 1,18. » (déjà en partie 3 ; decisions.md §4 ne montre que g(4),
    le .tex écrit les deux à l'étape 6) et d « g(0) = 2/(−4) = −1/2, donc f(0) = e^{−1/2} ≈ 0,61. ». x₀ non entier (fractions de
    fractions) ou f qui n'est pas e^{u/v} : pas de ligne (b : pas de « f(−2) = (4 − 6)e⁴ = −2e⁴ » du .tex). À confirmer.
42. **P7b, extremum à une borne fermée de l'ED** (√(x² − 4) en ±2) : f′ n'y change pas de signe, la parenthèse « (f′ passe de … à …) »
    n'est pas écrite (rien plutôt qu'une phrase inventée). Voulez-vous une autre justification (« borne de l'ED ») ?
43. **P7b, mots de « global »** : « Global : les autres valeurs de f sont plus petites (limites 0⁺ en ±∞). » ; les limites égales en
    −∞ et en +∞ s'écrivent « en ±∞ », sinon « limites 0⁺ en −∞ et −∞ en +∞ » ; avec un autre extremum du même genre, « (autre maximum
    local : f(…) = … ; limites …) ». Sans limite à citer (ED fermé, √(4 − x²)) : « Global : les autres valeurs de f sont plus
    petites. », sans parenthèse. La ligne commence toujours par « Maximum local » (decisions.md §2), même quand il est global (le
    .tex de a et c écrit « Maximum (global) »). Les limites sans signe d'approche (x/(x² + 1) : « limites 0 en ±∞ ») attendent P6.
44. **P7b, « ? » pris à la lettre** : une limite « ? » (ou absente) donne « local » seul, même si une autre borne prouverait « pas
    global » (decisions.md §2). Aucune entrée de la page ni du corpus n'est concernée.
45. **P7b, cas limite x²e^{−x}** : le minimum (0 ; 0) égale la limite 0⁺ en +∞ : « local » seul (decisions.md §2), bien que f ≥ 0
    partout. De même x⁴ − 2x² (deux minimums égaux à −1) et √(x² − 4) (deux minimums égaux à 0).
47. **P7b, notation scientifique dans un point** : e^(7/(x² − 1)) donne « (0 ; e^{−7}) ≈ (0 ; 9,119 × 10⁻⁴) » (R13, question 1).
48. **P7b, « pas global » par un autre extremum** : « Pas global : le maximum local en x = … est plus grand. » (aucune entrée de la page
    ni du corpus n'est concernée : une limite infinie l'emporte toujours). Les mots vous conviennent-ils ?

49. **P8, « AH visible » (question 3)** : appliquée telle que lue par le test du corpus (x au-delà de tous les points à montrer et des
    valeurs interdites, |f(x) − L| < 5 % de la hauteur de la fenêtre). Le côté de l'AH est élargi de 25 % de la largeur à la fois,
    6 fois au plus (fenêtre au plus 3,8 fois plus large) ; au-delà, la fenêtre des points reste (ln(x)/x : l'approche de y = 0
    demanderait x ≈ 60 et écraserait le maximum). Ex7 : x de −9,6 à 6 (.tex : −8 à 10) ; d : −6 à 6 (comme le .tex) ; c : la fenêtre
    en y passe de [−51 ; 21] à [−5,1 ; 11,8] et la courbe va jusqu'à x ≈ −7,8 : l'approche de y = 0 se voit. À confirmer.
52. **P8, deux limites finies différentes** (x/√(x²) en 0 : −1 et 1) : deux ronds vides, (0 ; −1) et (0 ; 1) (D15 « d'un côté ou des
    deux »), alors que la spécification disait « rien n'est dessiné ». À confirmer.
53. **P8, limite finie hors de la liste fermée** (e, √2, ln 2… : e^(1/(x − 1)) + e en 1⁻) : pas de rond vide (la valeur ne se compare
    pas exactement : option qui affiche le moins). Aucune entrée de la page ni du corpus n'est concernée.
55. **P8, temps** : a passe de 0,02 à 0,03 s (+ 50 % à l'arrondi près, quelques millisecondes : la partie 3, déjà payée par
    `resoudre`, est maintenant comptée dans `etudier()`) ; aucune autre hausse de plus de 50 % (c + 30 %). Signalé selon la règle ;
    sans effet pour l'élève (le temps de la page ne change que de quelques millisecondes).

56. **Résumé, ligne des zéros de f′ (outil Dérivée)** : vue en transcrivant l'Ex7 : « f′(x) = … = 0 ⇔ x = 0 ou x − 4 = 0 ⇔ x = 0
    ou x = 4 ; valeur interdite : x = 2 » ; decisions.md §4 écrit « f′(x) = 0 ⇔ x(x − 4) = 0 ⇔ x = 0 ou x = 4 (produit nul) ». La ligne
    est celle de l'outil Dérivée (aucune décision ne la vise) : la changer toucherait ses instantanés. Faut-il l'aligner sur §4 ?

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

- **P2** (EC seule ; l'outil Dérivée et l'outil Limites seuls ne changent pas : leur `etudier` reçoit un paramètre facultatif `analyse`,
  sans effet quand il est absent, et leurs instantanés sont identiques). Instantanés modifiés : `tests/python/instantanes/resoudre/etude-complete.json`
  (15 entrées) et `tests/pages/references/etude-complete.json` (16 entrées) ; `tests/python/instantanes/etude-complete.json` (sortie
  d'`etudier()`) est identique. Vérifié par programme : dans chaque entrée, mêmes cartes qu'avant (aucune n'est modifiée), dans un autre
  ordre, plus les six intertitres.

  | Entrée | Avant | Après |
  |---|---|---|
  | toutes (15) | Fonction · Dérivée · Signe de f′ et variations · [Tableaux de signes] · Limite… · Bilan des asymptotes · Graphique | **1. Domaine de définition** · Fonction · **2. Parité** · **3. Zéros, signe, ordonnée à l'origine** · **4. Limites et asymptotes** · [Tableaux de signes] · Limite… · Bilan des asymptotes · **5. Dérivée, tableau de variation, extremums** · Dérivée · Signe de f′ et variations · **6. Graphe** · Graphique |
  | page, au départ | 1 carte visible, « Étape 1 / n » | l'intertitre 1 et la carte « Fonction » visibles, « Étape 1 / n » (n inchangé : les intertitres ne comptent pas) |

- **P3** (EC seule ; outils ED, Dérivée, Limites, Exp-log : instantanés identiques). Instantanés modifiés :
  `tests/python/instantanes/resoudre/etude-complete.json` (15 entrées modifiées, 2 nouvelles : Ex7 et d) ;
  `tests/pages/references/etude-complete.json` (15 modifiées, 2 nouvelles) ; `tests/python/instantanes/etude-complete.json` (sortie
  d'`etudier()`) : 2 nouvelles entrées, aucune modifiée. Vérifié par programme : dans chaque entrée modifiée, tout ce qui suit
  « 2. Parité » est identique ; seule la partie 1 change (et le compteur d'étapes : + 1 à + 3).

  | Entrée | Avant (partie 1) | Après (partie 1) |
  |---|---|---|
  | toutes | Fonction : f(x) = … et « ED = … » (discret) | Fonction : f(x) = … seule · [Mise en forme] · Condition k (une carte par condition, badge) · Ensemble de définition : **ED = …** encadré |
  | `(x^2-1)/(x-3)` | ED = ℝ ∖ {3} | Condition 1 (dénominateur) : x − 3 ≠ 0 ; « On résout x − 3 = 0 ⇔ x = 3. » · ED = ℝ ∖ {3} |
  | `e^(1/x)`, `(e^x-1)/x` | ED = ℝ ∖ {0} | Condition 1 (dénominateur) : x ≠ 0 · ED = ℝ ∖ {0} |
  | `x/(x^2+1)` | ED = ℝ | Condition 1 : x² + 1 ≠ 0, lignes de l'outil ED (Δ = −4, ne s'annule jamais) · ED = ℝ |
  | `ln(x)/x` | ED = ]0 ; +∞[ | Condition 1 (logarithme) : x > 0 · Condition 2 (dénominateur) : x ≠ 0 · ED = ]0 ; +∞[ = ]0 ; +∞[ (question 13) |
  | `x*ln(x)`, `3(x*ln(x))`, `sqrt(x^2-4)`, `x/sqrt(x^2)` | ED = … | une carte de condition de l'outil ED (lignes et tableau tels quels) · ED encadré |
  | `e^(2x)`, `x^(2/3)`, `x^2*e^(-x)`, `x^2-4x+3`, `x^3-3x`, `x^4-2x^2` | ED = ℝ | « Ni logarithme, ni dénominateur, ni racine : aucune condition. » · ED = ℝ encadré |
  | `e^((x^2+x-2)/(6x-12))` (nouvelle, Ex7) | — | Mise en forme : x² + x − 2 = (x + 2)(x − 1) (Somme-Produit) ; 6x − 12 = 6(x − 2) (mise en évidence) ; On note g(x) = (x + 2)(x − 1)/(6(x − 2)), donc f(x) = e^{g(x)}. · Condition 1 : 6x − 12 ≠ 0 ; On résout 6x − 12 = 0 ⇔ 6x = 12 ⇔ x = 2. · ED = ℝ ∖ {2} |
  | `e^(2/(x^2-4))` (nouvelle, d) | — | Condition 1 : x² − 4 ≠ 0 ; On résout x² − 4 = 0 ⇔ x² = 4 ⇔ x = −2 ou x = 2. · ED = ℝ ∖ {−2 ; 2} |

- **P4** (EC seule ; aucun autre outil ne change : instantanés identiques, `etudier()` identique). Instantanés modifiés :
  `tests/python/instantanes/resoudre/etude-complete.json` (17 entrées modifiées) et `tests/pages/references/etude-complete.json`
  (17 modifiées ; l'entrée d'erreur `ln(` est identique). Vérifié par programme : dans chaque entrée, tout ce qui précède « 2. Parité »
  et tout ce qui suit « 3. Zéros, signe, ordonnée à l'origine » est identique ; seules les cartes de la partie 2 s'ajoutent (le compteur
  d'étapes augmente de 1 à 3).

  | Entrée | Avant (partie 2) | Après (partie 2) |
  |---|---|---|
  | toutes | intertitre seul | Symétrie de l'ED · [Calcul de f(−x)] ou [Pas impaire · Pas paire] |
  | `e^((x^2+x-2)/(6x-12))` (Ex7) | — | −2 ∈ ED, mais 2 ∉ ED : ED n'est pas symétrique par rapport à 0. Donc **f n'est ni paire ni impaire**. |
  | `(x^2-1)/(x-3)` | — | −3 ∈ ED, mais 3 ∉ ED : … ni paire ni impaire |
  | `ln(x)/x`, `x*ln(x)`, `3(x*ln(x))` | — | 1 ∈ ED, mais −1 ∉ ED : … ni paire ni impaire |
  | `e^(2/(x^2-4))` (d), `sqrt(x^2-4)`, `x^4-2x^2`, `x^(2/3)` | — | ED symétrique ; f(−x) = e^{2/((−x)² − 4)} (on remplace x par −x) = e^{2/(x² − 4)} (car (−x)² = x²) = f(x) ; **f est paire** (de même √((−x)² − 4), (−x)⁴ − 2(−x)², ∛((−x)²)) |
  | `x^3-3x` | — | f(−x) = (−x)³ − 3(−x) = −x³ + 3x (car (−x)³ = −x³ ; règle des signes) = −(x³ − 3x) (mise en évidence de −1) = −f(x) ; **f est impaire** |
  | `x/(x^2+1)`, `x/sqrt(x^2)` | — | f(−x) = (−x)/((−x)² + 1) = −x/(x² + 1) (car (−x)² = x² ; règle des signes) = −f(x) ; **f est impaire** |
  | `e^(2x)` | — | f(0) = 1 ≠ 0 : pas impaire ; f(1) = e² ≈ 7,39, f(−1) = e^{−2} ≈ 0,14 : pas paire |
  | `x^2-4x+3` | — | f(0) = 3 ≠ 0 ; f(1) = 0, f(−1) = 8 (entiers, sans ≈) |
  | `e^(1/x)` | — | 0 ∉ ED : f(1) = e ≈ 2,72, donc −f(1) ≈ −2,72 ; f(−1) = e^{−1} ≈ 0,37 : pas impaire ; même a pour « pas paire » |
  | `x^2*e^(-x)` | — | f(0) = 0 : contre-exemple f(1) = e^{−1} ≈ 0,37, −f(1) ≈ −0,37, f(−1) = e ≈ 2,72 ; pas paire avec le même a |
  | `(e^x-1)/x` | — | f(1) = e − 1 ≈ 1,72 ; f(−1) = −(e^{−1} − 1) ≈ 0,63 (question 19) |

  Hors instantanés (corpus) : b « f(0) = −6 ≠ 0 », « f(1) = −5e^{−2} ≈ −0,68 », « f(−1) = −5e^{2} ≈ −36,95 » ; c « f(0) = 5 ≠ 0 »,
  « f(1) = e(6 − e) ≈ 8,92 », « f(−1) = e^{−1}(6 − e^{−1}) ≈ 2,07 » ; a « f(−x) = e^{−(−x)²} = e^{−x²} (car (−x)² = x²) = f(x) ».
  Largeurs 320 / 360 / 390 px vérifiées à part (script de mesure de `test_largeurs.py`) pour 12 entrées dont Ex7, b, c, d, ln(x² + 1)/x
  et x² + x/1000 : aucune faute.

- **P5** (EC seule ; outil Dérivée : `tableau_signes` extrait d'`etudier`, instantanés identiques ; ED, Limites, Exp-log : identiques ;
  `tests/python/instantanes/etude-complete.json` (sortie d'`etudier()`) identique). Instantanés modifiés :
  `tests/python/instantanes/resoudre/etude-complete.json` (17 entrées modifiées) et `tests/pages/references/etude-complete.json`
  (17 modifiées ; l'entrée d'erreur `ln(` est identique). Vérifié par programme : dans chaque entrée, tout ce qui précède et suit la
  partie 3 est identique ; seules les cartes de la partie 3 s'ajoutent (2 ou 3 ; le compteur d'étapes augmente d'autant).

  | Entrée | Avant (partie 3) | Après (partie 3) |
  |---|---|---|
  | toutes | intertitre seul | [Zéros de f · Signe de f (tableau)] ou [Zéros et signe de f] · Ordonnée à l'origine |
  | `e^((x^2+x-2)/(6x-12))` (Ex7) | — | e^{g(x)} > 0 pour tout x ∈ ED (une exponentielle est strictement positive). Donc f n'a pas de zéro et f(x) > 0 sur ED. · g(0) = −2/(−12) = 1/6, donc f(0) = e^{1/6} ≈ 1,18. Le graphe coupe l'axe des y au point (0 ; e^{1/6}). |
  | `e^(2/(x^2-4))` (d), `e^(2x)`, `e^(1/x)` | — | même phrase (« pour tout x » si ED = ℝ) et « f(x) > 0 sur ED » ; f(0) = e^{−1/2} ≈ 0,61 (d), f(0) = 1 ; e^(1/x) : 0 ∉ ED : le graphe ne coupe pas l'axe des y |
  | `x^2*e^(-x)` | — | e^{−x} > 0 … ; il ne s'annule jamais. x²e^{−x} = 0 ⇔ x² = 0 (car e^{−x} > 0) ⇔ x = 0 · tableau x², e^{−x}, f(x) : + 0 + · f(0) = 0 |
  | `x^2-4x+3` | — | x² − 4x + 3 = 0 ⇔ (x − 1)(x − 3) = 0 (Somme-Produit) ⇔ x − 1 = 0 ou x − 3 = 0 (produit nul) ⇔ x = 1 ou x = 3 · tableau (une ligne x² − 4x + 3, question 23) · f(0) = 3 |
  | `x^3-3x`, `x^4-2x^2` | — | mise en évidence, produit nul, x² = 3 ⇔ x = −√3 ≈ −1,73 ou x = 0 ou x = √3 ≈ 1,73 (de même ±√2 ≈ ±1,41) · tableau · f(0) = 0 |
  | `(x^2-1)/(x-3)`, `x/(x^2+1)`, `ln(x)/x` | — | « ⇔ x² − 1 = 0 (numérateur nul) ⇔ x² = 1 ⇔ x = −1 ou x = 1 » (de même x = 0 ; ln(x) = 0 ⇔ x = 1) · tableau avec la valeur interdite (‖) et la zone hors de l'ED (hachurée) · f(0) = 1/3 ≈ 0,33 ; 0 ; 0 ∉ ED |
  | `x*ln(x)`, `3(x*ln(x))` | — | « ⇔ x = 0 ou ln(x) = 0 (produit nul) ⇔ x = 0 ou x = 1 », « x = 0 est rejeté, car 0 ∉ ED. » (3x ln x : « (on divise par 3) ») · tableau · 0 ∉ ED |
  | `(e^x-1)/x` | — | « ⇔ eˣ − 1 = 0 (numérateur nul) ⇔ eˣ = 1 (on ajoute 1) ⇔ x = 0 », x = 0 rejeté, « Donc f n'a pas de zéro et f(x) > 0 sur ED. » (pas de tableau) · 0 ∉ ED |
  | `x/sqrt(x^2)` | — | « ⇔ x = 0 (numérateur nul) », rejeté, « Donc f n'a pas de zéro. » · tableau − ‖ + (question 30) · 0 ∉ ED |
  | `sqrt(x^2-4)` | — | lignes de l'outil ED (« √(x² − 4) = 0 ⇔ x² − 4 = 0 », « On résout … », « Solutions : … »), « Donc x = −2 ou x = 2. » (question 26) · tableau + 0 (hachuré) 0 + · 0 ∉ ED |
  | `x^(2/3)` | — | « ∛(x²) = 0 ⇔ (∛x)² = 0 ⇔ ∛x = 0 ⇔ x = 0 » · tableau + 0 + · f(0) = 0 |

  Hors instantanés (corpus) : b « (x² − 6)e^{−2x} = 0 ⇔ x² − 6 = 0 (car e^{−2x} > 0) ⇔ x² = 6 ⇔ x = −√6 ≈ −2,45 ou x = √6 ≈ 2,45 »,
  tableau x² − 6, e^{−2x}, f(x) : + 0 − 0 +, f(0) = −6 ; c « eˣ(6 − eˣ) = 0 ⇔ 6 − eˣ = 0 (car eˣ > 0) ⇔ eˣ = 6 (on isole eˣ …) ⇔
  x = ln(6) ≈ 1,79 », tableau + 0 −, f(0) = 5 ; a « e^{−x²} > 0 pour tout x … Donc f n'a pas de zéro et f(x) > 0 sur ED », f(0) = 1.
  Largeurs 320 / 360 / 390 px vérifiées à part (mesure de `test_largeurs.py`, corrigé complet affiché) pour 18 entrées dont Ex7, a–d,
  x⁴ − 2x², ln(x)/x, √(x² − 4), (x² − 5)(x² − 7)e^{−x} (tableau à 4 zéros) : aucune faute.

- **P7a** (outil Dérivée, donc aussi EC). Instantanés modifiés : `tests/python/instantanes/{derivee-variations,etude-complete}.json`,
  `tests/python/instantanes/resoudre/{derivee-variations,etude-complete}.json`, `tests/pages/references/{derivee-variations,etude-complete}.json` :
  9 entrées de la Dérivée et 11 de l'EC, aucune nouvelle ni retirée. Vérifié par programme : dans chaque entrée, seule la carte
  « Dérivée » change (étapes de la dérivée ; f′, tableaux, extremums identiques). Aucun autre outil ne change.

  | Entrée | Avant | Après |
  |---|---|---|
  | produit et quotient (Dérivée : `(x+1)/(x-1)/2`, `(x^2-1)/(x-3)`, `-(x*ln(x))`, `3(x*ln(x))`, `ln(x)/x`, `x*ln(x)`, `x*ln(x)+x`, `x/(x^2+1)`, `x^2*e^(-x)` ; EC : `(e^x-1)/x`, `(x^2-1)/(x-3)`, `3(x*ln(x))`, `ln(x)/x`, `x*ln(x)`, `x/(x^2+1)`, `x/sqrt(x^2)`, `x^2*e^(-x)`) | « On pose u(x) = … et v(x) = … : règle du produit, (uv)′ = u′v + uv′. » · justifications · « u′(x) = … . » · « v′(x) = … . » · ligne f′ | « On applique la règle du produit, (uv)′ = u′v + uv′, avec : » · **tableau** u = … \| v = … / u′ = … \| v′ = … · justifications · ligne f′ (inchangée) |
  | `x^2*e^(-x)` (Dérivée, EC) | … = 2xe^{−x} + x²(−e^{−x}) = … | … = 2xe^{−x} + x²·(−e^{−x}) = … |
  | `e^((x^2+x-2)/(6x-12))` (Ex7, EC) | « (x²)′ = 2x (règle de la puissance). » · « e^{…} est de la forme e^u avec u(x) = (x² + x − 2)/(6x − 12) (dérivée interne u′(x) = ((2x + 1)(6x − 12) − (x² + x − 2)·6)/(6x − 12)²) ⇒ (e^{…})′ = u′e^u = x(x − 4)e^{…}/(6(x − 2)²). » | « f(x) = e^{g(x)} avec g(x) = (x² + x − 2)/(6x − 12), donc f′(x) = g′(x)·e^{g(x)} (dérivée d'une composée). On calcule d'abord g′(x). » · sous-carte **Dérivée de l'exposant** : Étape 1 règle du quotient (formule, tableau u = x² + x − 2 \| v = 6x − 12 / u′ = 2x + 1 \| v′ = 6, g′(x) = ((2x + 1)(6x − 12) − (x² + x − 2)·6)/(6x − 12)²) ; Étape 2 = (12x² − 24x + 6x − 12 − 6x² − 6x + 12)/(36(x − 2)²) (développement) = (6x² − 24x)/(36(x − 2)²) (réduction) = 6x(x − 4)/(36(x − 2)²) (mise en évidence) = x(x − 4)/(6(x − 2)²) (simplification par 6) · « On remplace g′(x) dans f′(x) = g′(x)·e^{g(x)} : » · f′ encadré (inchangé) |
  | `e^(2/(x^2-4))` (d, EC) | « (x²)′ = 2x » · phrase « de la forme e^u … u′(x) = −2·2x/(x² − 4)² » | même structure : tableau u = 2 \| v = x² − 4 / u′ = 0 \| v′ = 2x ; g′(x) = −2·2x/(x² − 4)² (règle du quotient) ; = −4x/(x² − 4)² (calcul) |
  | `e^(1/x)` (EC) | phrase « de la forme e^u … u′(x) = −1/x² … » | même structure : tableau u = 1 \| v = x / u′ = 0 \| v′ = 1 ; g′(x) = −1/x² (règle du quotient), pas d'étape 2 |

  Hors instantanés (corpus) : b « On applique la règle du produit … » · tableau u = x² − 6 \| v = e^{−2x} / u′ = 2x \| v′ = −2e^{−2x} ·
  « f′(x) = … = 2xe^{−2x} + (x² − 6)·(−2e^{−2x}) = −2(x − 3)(x + 2)e^{−2x} » ; c « On développe d'abord (c'est plus simple à
  dériver) : » · « f(x) = eˣ(6 − eˣ) = 6eˣ − eˣ · eˣ (développement) » · « = 6eˣ − e^{2x} (réduction) » · dérivée de la somme
  (« (eˣ)′ = eˣ », « (6eˣ)′ = 6·(eˣ)′ = 6eˣ », « e^{2x} est de la forme e^u … = 2e^{2x} », « f′(x) = 2eˣ(3 − eˣ) ») au lieu de la
  règle du produit ; a inchangé. Largeurs : `test_largeurs.py::test_tableau_uv_et_derivee_de_l_exposant` (Dérivée
  `(x^3+2x)^4*e^x`, EC Ex7, 320 à 1100 px) : aucune faute, tableaux dans leur carte, côte à côte à 1100 px, empilés u, u′, v, v′ à
  320 px ; captures relues à 320 et 1100 px.

- **P7b** (D10 : outil Dérivée, donc aussi EC ; D11 : EC seule). Instantanés modifiés :
  `tests/python/instantanes/{derivee-variations,etude-complete}.json` (sortie d'`etudier()`),
  `tests/python/instantanes/resoudre/{derivee-variations,etude-complete}.json`, `tests/pages/references/{derivee-variations,etude-complete}.json` :
  18 entrées de la Dérivée (22 pour `etudier()` : les 4 dont l'extremum portait déjà sa valeur, √(x²), √(x² − 4), x^(1/2), x^(2/3),
  ne gagnent que les champs techniques `x_py`, `f_py`) et 13 de l'EC, aucune nouvelle ni retirée. Vérifié par programme : dans la
  sortie d'`etudier()`, seules changent la case de l'extremum (ligne f(x)) et les champs `x_py`, `f_py` ; dans la Dérivée, seule la
  case ; dans l'EC, la case, la liste des extremums (remplacée par les lignes D11) et les champs techniques du bloc du graphique.
  Aucun autre outil ne change.

  **Outil Dérivée (et EC) : ligne f(x) du tableau de variations, « • » → valeur**

  | Entrée | Avant | Après |
  |---|---|---|
  | `(x^2-1)/(x-3)` | ↗ • ↘ ‖ ↘ • ↗ | ↗ 6 − 4√2 ↘ ‖ ↘ 4√2 + 6 ↗ |
  | `ln(x)/x`, `-(x*ln(x))` | … • … | … e^{−1} … |
  | `x*ln(x)`, `3(x*ln(x))`, `x*ln(x)+x` | … • … | … −e^{−1} … ; −3e^{−1} ; −e^{−2} |
  | `x/(x^2+1)` | ↘ • ↗ • ↘ | ↘ −1/2 ↗ 1/2 ↘ |
  | `x^2*e^(-x)` | ↘ • ↗ • ↘ | ↘ 0 ↗ 4e^{−2} ↘ |
  | `x^2-4x+3`, `3x^2-4x`, `-x^2` | ↘ • ↗ (↗ • ↘) | −1 ; −4/3 ; 0 |
  | `x^3-3x` | ↗ • ↘ • ↗ | ↗ 2 ↘ −2 ↗ |
  | `x^4-2x^2` | ↘ • ↗ • ↘ • ↗ | ↘ −1 ↗ 0 ↘ −1 ↗ |
  | `(x^2+1)^(1/2)`, `e^(x^2)`, `sqrt(x^2-4x+5)` | ↘ • ↗ | ↘ 1 ↗ |
  | `x^(3/2)` | • ↗ | 0 ↗ |
  | `x^x` | ↘ • ↗ | ↘ e^{−1/e} ↗ |
  | `e^((x^2+x-2)/(6x-12))` (Ex7, EC) | 0⁺ ↗ • ↘ 0⁺ ‖ +∞ ↘ • ↗ +∞ | 0⁺ ↗ e^{1/6} ↘ 0⁺ ‖ +∞ ↘ e^{3/2} ↗ +∞ (comme le .tex) |
  | `e^(2/(x^2-4))` (d, EC) | 1 ↗ +∞ ‖ 0⁺ ↗ • ↘ 0⁺ ‖ +∞ ↘ 1 | 1 ↗ +∞ ‖ 0⁺ ↗ e^{−1/2} ↘ 0⁺ ‖ +∞ ↘ 1 |

  La liste des extremums de l'outil Dérivée (« maximum local en x = 0 : f(0) = … ») ne change pas.

  **Étude complète : extremums (D11), à la place de la liste « maximum local en x = … : f(…) = … »**

  | Entrée | Après |
  |---|---|
  | `e^((x^2+x-2)/(6x-12))` (Ex7) | g(0) = −2/(−12) = 1/6, donc f(0) = e^{1/6} ≈ 1,18. · g(4) = 18/12 = 3/2, donc f(4) = e^{3/2} ≈ 4,48. · **Maximum local** en x = 0 : (0 ; e^{1/6}) ≈ (0 ; 1,18) (f′ passe de + à −). Pas global : f(x) → +∞ quand x → 2⁺. · **Minimum local** en x = 4 : (4 ; e^{3/2}) ≈ (4 ; 4,48) (f′ passe de − à +). Pas global : f(x) → 0⁺ quand x → −∞. |
  | `e^(2/(x^2-4))` (d) | g(0) = 2/(−4) = −1/2, donc f(0) = e^{−1/2} ≈ 0,61. · **Maximum local** en x = 0 : (0 ; e^{−1/2}) ≈ (0 ; 0,61) (f′ passe de + à −). Pas global : f(x) → +∞ quand x → −2⁻ (question 40). |
  | `(x^2-1)/(x-3)` | **Maximum local** en x = 3 − 2√2 : (3 − 2√2 ; 6 − 4√2) ≈ (0,17 ; 0,34) (+ à −). Pas global : f(x) → +∞ quand x → 3⁺. · **Minimum local** en x = 3 + 2√2 : (…) ≈ (5,83 ; 11,66) (− à +). Pas global : f(x) → −∞ quand x → −∞. |
  | `ln(x)/x` | **Maximum local** en x = e : (e ; e^{−1}) ≈ (2,72 ; 0,37) (+ à −). Global : les autres valeurs de f sont plus petites (limites −∞ en 0⁺ et 0⁺ en +∞). |
  | `x*ln(x)`, `3(x*ln(x))` | **Minimum local** en x = e^{−1} : (e^{−1} ; −e^{−1}) ≈ (0,37 ; −0,37) (− à +). Global : les autres valeurs de f sont plus grandes (limites 0⁻ en 0⁺ et +∞ en +∞). (de même −3e^{−1} ≈ −1,10) |
  | `x/(x^2+1)` | **Minimum local** en x = −1 : (−1 ; −1/2) ≈ (−1 ; −0,50) (− à +). Global : … plus grandes (limites 0 en ±∞). · **Maximum local** en x = 1 : (1 ; 1/2) ≈ (1 ; 0,50) (+ à −). Global : … plus petites (limites 0 en ±∞). |
  | `x^2*e^(-x)` | **Minimum local** en x = 0 : (0 ; 0) (− à +). (rien : égal à la limite 0⁺, question 45) · **Maximum local** en x = 2 : (2 ; 4e^{−2}) ≈ (2 ; 0,54) (+ à −). Pas global : f(x) → +∞ quand x → −∞. |
  | `x^2-4x+3` | **Minimum local** en x = 2 : (2 ; −1) (− à +). Global : … plus grandes (limites +∞ en ±∞). |
  | `x^3-3x` | **Maximum local** en x = −1 : (−1 ; 2) (+ à −). Pas global : f(x) → +∞ quand x → +∞. · **Minimum local** en x = 1 : (1 ; −2) (− à +). Pas global : f(x) → −∞ quand x → −∞. |
  | `x^4-2x^2` | **Minimum local** en x = −1 : (−1 ; −1) (− à +). · **Maximum local** en x = 0 : (0 ; 0) (+ à −). Pas global : f(x) → +∞ quand x → −∞. · **Minimum local** en x = 1 : (1 ; −1) (− à +). (minimums égaux : rien) |
  | `sqrt(x^2-4)` | **Minimum local** en x = −2 : (−2 ; 0). · **Minimum local** en x = 2 : (2 ; 0). (bornes fermées, minimums égaux : rien, question 42) |
  | `x^(2/3)` | **Minimum local** en x = 0 : (0 ; 0) (− à +). Global : … plus grandes (limites +∞ en ±∞). |

  Avant P7b, ces entrées de l'EC avaient la liste de l'outil Dérivée (« maximum local en x = 0 : f(0) = e^{1/6} », etc.).
  Hors instantanés (corpus) : a « **Maximum local** en x = 0 : (0 ; 1) (f′ passe de + à −). Global : les autres valeurs de f sont plus
  petites (limites 0⁺ en ±∞). » ; b « **Minimum local** en x = −2 : (−2 ; −2e⁴) ≈ (−2 ; −109,20) (− à +). Global : … plus grandes
  (limites +∞ en −∞ et 0⁺ en +∞). » et « **Maximum local** en x = 3 : (3 ; 3e^{−6}) ≈ (3 ; 0,0074) (+ à −). Pas global : f(x) → +∞
  quand x → −∞. » ; c « **Maximum local** en x = ln(3) : (ln(3) ; 9) ≈ (1,10 ; 9) (+ à −). Global : … plus petites (limites 0⁺ en −∞
  et −∞ en +∞). » ; tableaux b : +∞ ↘ −2e⁴ ↗ 3e^{−6} ↘ 0⁺, c : 0⁺ ↗ 9 ↘ −∞ (comme le .tex).
  Largeurs : `test_largeurs.py::test_tableau_de_variations_avec_valeurs` (Dérivée `(x^2-1)/(x-3)`, EC Ex7 et d, 320 à 1100 px) :
  aucune faute, chaque tableau dans sa carte, chaque valeur en formule dans sa case ; défilement du tableau : voir Écarts.

- **P8** (EC seule ; aucun autre outil ne change : instantanés des outils ED, Dérivée, Limites, Factorisation, Exp-log identiques).
  Instantanés modifiés : `tests/python/instantanes/etude-complete.json` (sortie d'`etudier()` : seul le bloc `graphique` change, 17
  entrées), `tests/python/instantanes/resoudre/etude-complete.json` (17 entrées : seule la carte « Graphique » change, bloc et texte
  d'aide), `tests/pages/references/etude-complete.json` (17 entrées : texte d'aide seul), `tests/pages/references/graphique-traces.json`
  (48 empreintes : les 3 fonctions du banc, x²e^{−x}, e^(1/x), (x² − 1)/(x − 1), changent de cadrage ou de points). Vérifié par
  programme : aucune autre carte ne change.

  Texte d'aide de la carte : avant « Courbe (trait plein), asymptotes (pointillé), extrema (points pleins), trou (rond vide). … » ;
  après « Courbe (trait plein), asymptotes (pointillé), extremums, zéros et point (0 ; f(0)) (points pleins), points exclus du graphe
  (ronds vides). … ».

  | Entrée | Fenêtre avant (x ; y) | Fenêtre après (x ; y) | Points marqués ajoutés | Ronds vides ajoutés |
  |---|---|---|---|---|
  | `e^((x^2+x-2)/(6x-12))` (Ex7) | [−2 ; 6] ; [−1,49 ; 7,47] | [−9,62 ; 6] ; [−1,40 ; 7,00] (AH à gauche) | — ((0 ; f(0)) = maximum) | (2 ; 0) |
  | `e^(2/(x^2-4))` (d) | [−4 ; 4] ; [−0,18 ; 3,68] | [−6 ; 6] ; [−0,50 ; 2,15] | — | (−2 ; 0), (2 ; 0) |
  | `e^(1/x)` | [−2 ; 2] ; [−2,81 ; 14,58] | [−10,97 ; 10,12] ; [−0,50 ; 2,13] (AH y = 1) | — | (0 ; 0) |
  | `x/sqrt(x^2)` | [−2 ; 2] ; [−1,5 ; 1,5] | inchangée | — | (0 ; −1), (0 ; 1) |
  | `(e^x-1)/x` | [−2 ; 2] ; [−0,62 ; 3,08] | [−7,77 ; 2] ; [−0,50 ; 2,50] (AH à gauche) | — | — (trou (0 ; 1) déjà dessiné) |
  | `(x^2-1)/(x-3)` | [−2,66 ; 8,66] ; [−6,11 ; 18,11] | [−4,41 ; 9,24] ; [−5,00 ; 17,35] | (−1 ; 0), (1 ; 0), (0 ; 0,33) | — |
  | `x^2-4x+3` | [0 ; 4] ; [−1,50 ; 0,94] | [−2 ; 5] ; [−2,25 ; 5,25] ((0 ; 3) était hors de la fenêtre) | (1 ; 0), (3 ; 0), (0 ; 3) | — |
  | `x^3-3x` | [−3 ; 3] ; [−3 ; 3] | [−3,73 ; 3,73] ; [−4,5 ; 4,5] | (−1,73 ; 0), (0 ; 0), (1,73 ; 0) | — |
  | `x^4-2x^2` | [−3 ; 3] ; [−2,24 ; 5,22] | [−3,41 ; 3,41] ; [−1,5 ; 1,5] | (−1,41 ; 0), (1,41 ; 0) | — |
  | `x/(x^2+1)` | [−3 ; 3] ; [−1 ; 1] | [−10,12 ; 10,12] ; [−1 ; 1] (AH y = 0) | (0 ; 0) | — |
  | `x^2*e^(-x)` | [−2 ; 4] ; [−0,50 ; 1,91] | [−2 ; 7,38] ; [−0,50 ; 1,04] (AH à droite) | — ((0 ; 0) = minimum) | — |
  | `e^(2x)` | [−2 ; 2] ; [−2,75 ; 13,73] | [−2 ; 2] ; [−0,5 ; 2,5] | (0 ; 1) | — |
  | `x*ln(x)`, `3(x*ln(x))` | [−0,6 ; 2,37] ; [−0,87 ; 1,71] (3x ln x : [−2,29 ; 4,81]) | [−0,6 ; 3] ; [−0,87 ; 1,50] ([−1,63 ; 1,53]) | (1 ; 0) | — (bord 0 : trou déjà dessiné) |
  | `ln(x)/x` | [−0,6 ; 4,72] ; [−0,56 ; 0,87] | inchangée (approche de l'AH trop lente, question 49) | (1 ; 0) | — |
  | `sqrt(x^2-4)` | [−4 ; 4] ; [−0,75 ; 3,73] | [−4 ; 4] ; [−0,5 ; 1,5] | — | — |
  | `x^(2/3)` | [−2 ; 2] ; [−0,5 ; 1,63] | [−2 ; 2] ; [−0,5 ; 1,5] | — | — |

  Toutes les entrées : la courbe est tracée une largeur de fenêtre au-delà de chaque côté (segments environ 3 fois plus longs).
  Hors instantanés (corpus) : b fenêtre [−5,17 ; 5,72] ; [−143,3 ; 61,4] (avant [−4,5 ; 5,5] ; [−144,9 ; 69,5]), points (±√6 ; 0) et
  (0 ; −6) ; c [−2 ; 3,79] ; [−5,06 ; 11,81] (avant [−0,9 ; 3,1] ; [−51,3 ; 21,1]), points (ln 6 ; 0) et (0 ; 5) ; a inchangée.
  Captures relues (360 et 700 px) : Ex7, b, c, d, x/√(x²), e^(1/x), (x² − 1)/(x − 1).
