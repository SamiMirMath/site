# Étude complète : décisions de rédaction

À placer dans `docs/chantiers/etude-complete/decisions.md`.
Ordre de priorité : **CLAUDE.md > ce fichier > audit-etape0.md**.
Source de la manière de résoudre : `docs/reference/etude-complete/3MSt_Ch8_EtudesFonctions_Corrige.tex`.
Si une décision est impossible à tenir ou ambiguë, Claude Code **pose la question**. Il ne choisit pas seul. En exécution sans l'enseignant, il note la question dans `suivi.md`, prend l'option qui affiche le moins et continue.
Toutes les décisions ci-dessous sont **validées par l'enseignant** (2 nov. 2026).

---

## 0. Principes

1. **Le corrigé .tex est la cible.** Un écart n'est permis que s'il figure dans ce fichier.
2. **Rien de faux.** Les nouvelles affirmations sont : parité, « global », signe de f, contre-exemple, position par rapport à une asymptote, rond vide. Chacune est confirmée **deux fois** :
   - par un calcul exact (SymPy) ;
   - par une sonde mpmath.

   Si l'un des deux doute, l'outil affiche un message clair ou se tait, mais n'affirme jamais.
3. **« Local » est toujours vrai** pour un extremum. « Global » demande une preuve affichée (D11).
4. **Portée explicite.** Chaque décision indique si elle vaut pour l'EC seule, pour EC + Dérivée ou pour EC + Limites.
   - Une rédaction propre à l'EC passe par un paramètre (`ec=True`) ou par un drapeau du tableau.
   - Un changement partagé fait relire les instantanés de l'autre outil (liste avant / après dans `suivi.md`).
5. **Mise en forme.** Une étape par ligne, la propriété nommée entre parenthèses. Valeur exacte, puis valeur approchée. Vouvoiement dans les phrases adressées à l'élève.
6. **Public : les élèves de M aiment les algorithmes et les nombres, pas les concepts.** Entre deux justifications correctes, on prend la plus **calculatoire et concrète** :
   - un nombre qu'on calcule plutôt qu'une phrase de concept : valeur d'essai (D12), contre-exemple chiffré (D4), valeur approchée à côté de chaque valeur exacte ;
   - une suite d'étapes toujours dans le même ordre, que l'élève peut refaire seul : mêmes sous-titres, même ordre des lignes d'une fonction à l'autre ;
   - des phrases de conclusion courtes, avec les mots du .tex, sans vocabulaire théorique ajouté (pas de « voisinage », « continuité », « monotonie stricte », etc.).

---

## 1. Décisions

| n° | Décision | Portée |
|---|---|---|
| D1 | Ordre et titres du .tex : **1. Domaine de définition · 2. Parité · 3. Zéros, signe, ordonnée à l'origine · 4. Limites et asymptotes · 5. Dérivée, tableau de variation, extremums · 6. Graphe**. La partie 1 commence par une carte « Mise en forme » (haut et bas factorisés, exposant nommé g(x)). | EC |
| D2 | **EC-01 réécrit** : « Les valeurs communes (ED, f′, zéros de f′, limites) sont identiques à celles des outils séparés. La rédaction peut différer, par paramètre. » **Nouveau EC-15** : « Toute partie propre à l'EC a un garde-fou numérique et un message clair en cas de doute. » Les parties nouvelles vont dans `etude-complete/parties.py`. | EC |
| D3 | ED détaillé. On réutilise les cartes de condition de l'outil ED, en version courte (`6x − 12 = 0 ⇔ 6x = 12 ⇔ x = 2`). Le résultat est encadré. | EC |
| D4 | Parité : voir §2. | EC |
| D5 | Zéros, signe, f(0) : voir §2. | EC |
| D6 | **Correctif `_simplifier`** (e^(somme) gardé entier) **en premier**. Technique : `powsimp(combine='exp')`, puis chaque `exp(u)` est remplacé par un symbole muet ; ensuite `factor`, puis on remet les exponentielles. Critères : **une seule exponentielle par exposant distinct**, et l'exposant affiché est celui de l'énoncé (à la mise en forme près). | EC + Dérivée |
| D7 | **Dérivée de l'exposant** quand il n'est pas affine. Sous-carte « Dérivée de l'exposant » : règle du quotient ou du produit, puis numérateur développé une étape par ligne (développement, réduction, mise en évidence, simplification), puis `f′(x) = g′(x)·e^{g(x)}` encadré. **Parenthèses** autour d'un facteur négatif : `(x² − 6)·(−2e^{−2x})`. On supprime « (x²)′ = 2x » parasite et « (eˣ)′ = eˣ » écrit deux fois. | EC + Dérivée |
| D7b | *(validé ; reportable si le critère n'est pas simple et sûr)* Si f est un polynôme en eˣ (aucun x hors des exponentielles), on développe d'abord (.tex c) : `eˣ(6 − eˣ) = 6eˣ − e^{2x}`. | EC + Dérivée |
| D8 | **u, u′, v, v′ en tableau 2 × 2** comme le .tex (colonnes u \| v ; lignes fonction \| dérivée). Repli en lignes empilées si le tableau ne tient pas à 320 px (composant commun). | EC + Dérivée |
| D9 | Tableau de signes de f′ : on **garde R7** (une ligne par facteur, constantes à part). Écart au .tex accepté. | — |
| D10 | **Valeurs des extremums dans la ligne f(x)** du tableau de variations (exactes : e^{1/6}, −2e⁴…), par un drapeau du tableau. **Oui dans les deux outils** (EC et Dérivée) : un tableau de variations sans valeurs est incomplet pour l'élève. Vérifier la largeur à 320–390 px dans les deux outils. | EC + Dérivée |
| D11 | Extremums : voir §2. | EC |
| D12 | Justification de 0⁺ / 0⁻ en une valeur interdite **par une valeur d'essai** : voir §2. | EC + Limites |
| D13 | **Signe d'approche partout** (0⁺, 1⁺, bilan compris). Position par rapport à l'AH, AV d'un seul côté, point exclu : voir §2. | EC + Limites |
| D14 | Pente au point exclu (lim f′ en a⁻) : **reportée** en partie P10 facultative, sous le titre « Pour aller plus loin ». Elle n'est affichée que si la rédaction complète réussit. **Jamais de phrase de repli dans l'EC.** | EC |
| D15 | Graphe : zéros et point (0 ; f(0)) marqués ; **rond vide** à chaque point exclu dont la limite est finie (d'un côté ou des deux) ; cadrage selon §3 ; pas de seconde figure (le zoom tactile la remplace). | EC |
| D16 | Regrouper `x → ±∞` **seulement si les deux chaînes sont identiques au symbole près** (.tex a, d). Ordre : −∞, puis valeurs interdites croissantes (gauche puis droite), puis +∞. | EC + Limites |
| D17 | Formes exactes du .tex quand c'est sans risque : `3e^{−6}` (pas `3/e⁶`) ; coefficient constant positif en tête (`2eˣ(3 − eˣ)` plutôt que `−2(eˣ − 3)eˣ`). Sinon l'écart est accepté et noté dans `suivi.md`. | EC + Dérivée |
| D18 | Ex7 devient un **exemple** de la page ; a–d deviennent des **exercices** (difficile / très difficile). Ils entrent donc dans les instantanés et les tests de pages. | EC |
| D19 | **Cache** de l'analyse par entrée normalisée (`functools.lru_cache`), avec un test compteur : `analyser_complet` est appelé une seule fois par `etudier()`, et `fenetre()` ne le rappelle pas. EC-02 devient testé. | EC |
| D20 | **Carte « Bilan de l'étude »** à la fin, avant le graphe : ED, parité, zéros, signe, f(0), asymptotes avec position, extremums (nature et ≈). Chaque ligne renvoie au résultat de sa partie. L'élève y vérifie vite ses réponses. | EC |

---

## 2. Règles détaillées

### Parité (D4)
On applique, dans l'ordre :
1. **ED non symétrique.** Écrire un point `a ∈ ED` avec `−a ∉ ED` (Ex7 : « −2 ∈ ED, mais 2 ∉ ED »), puis la phrase « ED n'est pas symétrique par rapport à 0, donc f n'est ni paire ni impaire. »
2. **ED symétrique.** Calculer `f(−x)` en chaîne, une étape par ligne, la propriété nommée (« car (−x)² = x² »).
   - Si on aboutit à `f(x)` : « f est paire ».
   - Si on aboutit à `−f(x)` : « f est impaire ».

   Le résultat est confirmé par SymPy et par la sonde.
3. **Sinon, deux justifications séparées :**
   - **Pas impaire.** Si `0 ∈ ED` et `f(0) ≠ 0` : `f(0) = … ≠ 0` (valeur exacte). Sinon, contre-exemple `f(−a) ≠ −f(a)`.
   - **Pas paire.** Contre-exemple `f(−a) ≠ f(a)`. On choisit `a` dans 1, 2, 1/2, 3… avec `±a ∈ ED`. On écrit les valeurs exactes puis approchées. **Les deux valeurs arrondies affichées doivent être différentes** ; sinon on essaie le `a` suivant, et à défaut un message clair.

### Zéros, signe, ordonnée à l'origine (D5)
- Un facteur exponentiel donne la phrase « e^{…} > 0 pour tout x (une exponentielle est strictement positive) ; il ne s'annule jamais ». On résout ensuite l'équation sur les autres facteurs, en chaîne :
  `(x² − 6)e^{−2x} = 0 ⇔ x² − 6 = 0 (car e^{−2x} > 0) ⇔ x² = 6 ⇔ x = −√6 ou x = √6`, puis `≈ ±2,45`.
- Si aucun zéro : « f n'a pas de zéro et f(x) > 0 (ou < 0) sur ED ». Pas de tableau.
- Sinon : **tableau de signes de f** (machinerie R7 du tableau de f′), avec les zéros et les valeurs interdites.
- Si les zéros ne se calculent pas exactement : message clair, pas de tableau.
- Ordonnée à l'origine :
  - si `0 ∈ ED` : `f(0) = …` en exact puis ≈, et le point `(0 ; f(0))` ;
  - si `0 ∉ ED` : « 0 ∉ ED : le graphe ne coupe pas l'axe des y ».

### Extremums (D11)
- Format (révisé le 03.11, Q43) : le mot en gras donne la **conclusion** :
  - prouvé global : « **Maximum global** en x = 0 : (0 ; 1) (f′ passe de + à −). Les autres valeurs de f sont plus petites (limites 0⁺ en ±∞). »
  - prouvé non global : « **Maximum local** en x = 0 : (0 ; e^{1/6}) ≈ (0 ; 1,18) (f′ passe de + à −). Pas global : f(x) → +∞ quand x → 2⁺. »
  - sinon : « **Maximum local** en x = … : … » seul.
- Raison de « pas global » (Q40) : la limite ou l'extremum le plus extrême, puis le premier dans l'ordre du tableau (−∞, valeurs interdites de gauche à droite, +∞).
- La valeur est **calculée en chaîne** quand l'exposant n'est pas immédiat : `g(4) = 18/12 = 3/2, donc f(4) = e^{3/2} ≈ 4,48`.
- **Global.** Un maximum en x₀ est global si f(x₀) est strictement plus grand que :
  - les autres maximums locaux ;
  - **toutes** les limites aux bornes de l'ED (±∞ et chaque côté de chaque valeur interdite).

  On l'écrit avec sa justification : « global : les autres valeurs de f sont plus petites (limites 0⁺ en ±∞) ». Règle symétrique pour un minimum.
- **Pas global** si une limite ou un autre extremum dépasse f(x₀). On l'écrit avec la raison : « pas global : f(x) → +∞ quand x → 2⁺ ».
- Si une limite vaut « ? » ou si le cas est limite (une limite égale à f(x₀)) : « local » seul, sans commentaire.
- Valeurs approchées : **R13 s'applique** (Q1) : 2 décimales, 2 chiffres significatifs entre 10⁻³ et 0,01 (0,0074), notation scientifique de R13 sous 10⁻³ et dès 10⁶ ; séparateur des milliers ’ (convention du site, Q28 : ≈ 1’234,57) ; un entier exact s'écrit sans « ≈ » (Q2).

### Justification de 0⁺ / 0⁻ (D12) — validé
Règle, calquée sur le .tex : la **valeur d'essai** pour un dénominateur qui s'annule en a (zéro simple ou double).

> bas : 6x − 12 → 0 ; avec x = 1,99 : 6·1,99 − 12 = −0,06 < 0, donc 0⁻

Garde-fou : le point d'essai (a ± 0,01, ou plus près si nécessaire) est choisi de façon qu'**aucun autre zéro ni aucune valeur interdite** ne se trouve entre lui et a. Le signe est confirmé par la factorisation.
Le tableau R8 reste utilisé quand l'expression a plusieurs facteurs qui changent de signe près de a. Une seule règle pour l'EC et l'outil Limites.

### Asymptotes, position, points exclus (D13)
- AH : « Asymptote horizontale y = 0 (à gauche). f(x) → 0⁺ : le graphe est au-dessus. » La position n'est écrite que si le signe d'approche est démontré.
- Exposant → 0⁺ : « e^{0⁺} = 1⁺ (e^t > 1 pour t > 0) : le graphe est au-dessus de y = 1 ».
- AV d'un seul côté : « Asymptote verticale x = 2, seulement du côté droit. À gauche, f(x) → 0⁺ : le graphe s'approche du point (2 ; 0), qui n'appartient pas au graphe (rond vide). »
- Limite infinie en ±∞ sans asymptote : **pas de phrase** (la règle R6 du guide l'emporte, Q67), sauf décision contraire de l'enseignant notée en §8.

---

## 3. Critères testables du graphe (D15)
- La fenêtre contient tous les extremums, les zéros et (0 ; f(0)).
- Pour chaque AH y = L en ±∞, il existe un x **visible** où |f(x) − L| < 5 % de la hauteur de la fenêtre.
- Chaque point exclu à limite finie a un rond vide ; aucun rond vide ailleurs.
- Les asymptotes sont en pointillé (existant, EC-04 à EC-06).

---

## 4. Rédaction cible : Exemple 7 (texte de référence)

`f(x) = e^{(x² + x − 2)/(6x − 12)}`

**1. Domaine de définition**
- Mise en forme :
  - x² + x − 2 = (x + 2)(x − 1) (Somme-Produit) ;
  - 6x − 12 = 6(x − 2) (mise en évidence).
- On note g(x) = (x + 2)(x − 1) / (6(x − 2)), donc f(x) = e^{g(x)}.
- Condition : 6x − 12 ≠ 0. On résout 6x − 12 = 0 ⇔ 6x = 12 ⇔ x = 2.
- **ED = ℝ ∖ {2}**

**2. Parité**
- −2 ∈ ED, mais 2 ∉ ED : ED n'est pas symétrique par rapport à 0.
- Donc f n'est ni paire ni impaire.

**3. Zéros, signe, ordonnée à l'origine**
- e^{g(x)} > 0 pour tout x ∈ ED (une exponentielle est strictement positive).
- Donc f n'a pas de zéro et f(x) > 0 sur ED.
- g(0) = (−2)/(−12) = 1/6, donc f(0) = e^{1/6} ≈ 1,18. Point (0 ; e^{1/6}).

**4. Limites et asymptotes** (cartes de la refonte 3M, plus les ajouts D12, D13, D16)
- x → −∞ : g(x) → −∞ (podium en prédiction, BH avec les dérivées du haut et du bas). Donc f(x) → e^{−∞} = 0⁺.
  → AH y = 0 à gauche ; le graphe est au-dessus.
- x → 2⁻ :
  - haut : 4 + 2 − 2 = 4 (pas 0, donc pas indéterminée) ;
  - bas : avec x = 1,99 : 6·1,99 − 12 = −0,06, donc 0⁻ ;
  - g(x) → 4/0⁻ = −∞, donc f(x) → 0⁺.

  → Pas d'AV à gauche. Le graphe s'approche de (2 ; 0), qui n'appartient pas au graphe (rond vide).
- x → 2⁺ : bas → 0⁺ (x = 2,01 : 0,06) ; g(x) → +∞, donc f(x) → +∞.
  → AV x = 2, seulement du côté droit.
- x → +∞ : g(x) → +∞, donc f(x) → +∞ (pas d'AH à droite).

**5. Dérivée, tableau de variation, extremums**
- (e^{g})′ = g′·e^{g} (dérivée d'une composée).
- g′ par la règle du quotient :

  | u = x² + x − 2 | v = 6x − 12 |
  |---|---|
  | u′ = 2x + 1 | v′ = 6 |

- Calcul de g′(x), une étape par ligne :
  - g′(x) = [(2x + 1)(6x − 12) − (x² + x − 2)·6] / (6x − 12)² (règle du quotient)
  - = [12x² − 24x + 6x − 12 − 6x² − 6x + 12] / (36(x − 2)²) (développement)
  - = (6x² − 24x) / (36(x − 2)²) (réduction)
  - = 6x(x − 4) / (36(x − 2)²) (mise en évidence)
  - = x(x − 4) / (6(x − 2)²) (simplification par 6)
- **f′(x) = x(x − 4) / (6(x − 2)²) · e^{g(x)}** (une seule exponentielle)
- f′(x) = 0 ⇔ x(x − 4) = 0 ⇔ x = 0 ou x = 4 (produit nul).
- Tableau de signes (R7) : lignes 1/6, x, x − 4, (x − 2)², e^{g(x)}.
- Tableau de variations : 0⁺ ↗ **e^{1/6}** ↘ 0⁺ ‖ +∞ ↘ **e^{3/2}** ↗ +∞
- g(4) = 18/12 = 3/2, donc f(4) = e^{3/2} ≈ 4,48.
- Maximum local en x = 0 : (0 ; e^{1/6}) ≈ (0 ; 1,18) (f′ passe de + à −). Pas global : f(x) → +∞ quand x → 2⁺.
- Minimum local en x = 4 : (4 ; e^{3/2}) ≈ (4 ; 4,48) (f′ passe de − à +). Pas global : f(x) → 0⁺ quand x → −∞.

**6. Graphe**
- Courbe ; AV x = 2 (côté droit) et AH y = 0 (à gauche), en pointillé.
- Points marqués : max (0 ; 1,18), qui est aussi (0 ; f(0)) ; min (4 ; 4,48) ; rond vide en (2 ; 0).
- La fenêtre montre l'approche de y = 0 à gauche.

---

## 5. Résultats attendus pour a–d (pour le corpus et les instantanés)

**a. f(x) = e^{−x²}**
- ED : ℝ.
- Parité : f(−x) = e^{−(−x)²} = e^{−x²} (car (−x)² = x²) = f(x), donc **paire**.
- Zéros et signe : aucun zéro, f > 0.
- f(0) = 1.
- Limites : `x → ±∞` regroupés ; f(x) → 0⁺. AH y = 0 des deux côtés, graphe au-dessus.
- Extremum : max (0 ; 1), **global** (limites 0⁺ < 1).

**b. f(x) = (x² − 6)e^{−2x}**
- ED : ℝ.
- Pas impaire : f(0) = −6 ≠ 0.
- Pas paire : f(1) = −5e^{−2} ≈ −0,68 et f(−1) = −5e² ≈ −36,95.
- Zéros : ±√6 ≈ ±2,45. Signe : + puis − puis +.
- Limites : en −∞, +∞ ; en +∞, 0⁺ (2 BH).
- Dérivée : f′(x) = −2e^{−2x}(x − 3)(x + 2).
- Extremums :
  - min (−2 ; −2e⁴) ≈ (−2 ; −109,20), **global** ;
  - max (3 ; 3e^{−6}) ≈ (3 ; 0,0074), pas global : f(x) → +∞ quand x → −∞.

**c. f(x) = eˣ(6 − eˣ)**
- ED : ℝ.
- Pas impaire : f(0) = 5 ≠ 0.
- Pas paire : f(1) = e(6 − e) ≈ 8,92 et f(−1) = e^{−1}(6 − e^{−1}) ≈ 2,07.
- Zéro : ln 6 ≈ 1,79. Signe : + puis −.
- Limites : en −∞, 0⁺ (AH y = 0 à gauche, au-dessus) ; en +∞, −∞.
- Dérivée : f′(x) = 2eˣ(3 − eˣ).
- Extremum : max (ln 3 ; 9) ≈ (1,10 ; 9), **global**.

**d. f(x) = e^{2/(x² − 4)}**
- ED : ℝ ∖ {−2 ; 2}.
- Parité : **paire** (car (−x)² = x²).
- Zéros et signe : aucun zéro, f > 0.
- f(0) = e^{−1/2} ≈ 0,61.
- Limites :
  - `x → ±∞` regroupés : f(x) → 1⁺, AH y = 1, graphe au-dessus ;
  - −2⁻ : +∞ ; −2⁺ : 0⁺ ; 2⁻ : 0⁺ ; 2⁺ : +∞.
- Asymptotes verticales : x = −2 côté gauche ; x = 2 côté droit. Ronds vides en (−2 ; 0) et (2 ; 0).
- Extremum : max (0 ; e^{−1/2}) ≈ (0 ; 0,61), pas global : f(x) → +∞ quand x → −2⁻ (règle Q40).

---

## 6. Découpage (une branche `etude-complete`, un commit par partie)

| Partie | Contenu | Touche |
|---|---|---|
| P0 | `suivi.md`, corpus + oracle mpmath, xfail marqués avec leur partie | tests |
| P1 | D6, D7 (parenthèses, doublons), D17 | **Dérivée** |
| P2 | Squelette des 6 parties titrées (D1), spécification (D2, D19) | EC |
| P3 | Partie 1 : mise en forme + ED détaillé (D3) | EC |
| P4 | Partie 2 : parité (D4) | EC |
| P5 | Partie 3 : zéros, signe, f(0) (D5) | EC |
| R1 | Corrections après relecture qui touchent l'outil Dérivée : Q37, Q56, Q32 (§7) | **Dérivée** |
| R2 | Corrections après relecture propres à l'EC : Q7, Q11, Q15, Q23, Q28, Q41, Q43 (§7) | EC |
| P6 | Partie 4 : D12, D13, D16 | **Limites** |
| R3 | Corrections après la session 2 : Q57, ln(x² − 4), D7b (Dérivée) ; Q66, Q50 (EC) (§8) | **Dérivée** + EC |
| P7a | Dérivée de l'exposant détaillée, tableau u/v (D7, D8, D7b si simple) | **Dérivée** |
| P7b | Valeurs dans le tableau de variations (D10), extremums (D11) | EC + **Dérivée** |
| P8 | Graphe (D15, §3) | EC |
| P9 | Exemples (D18), Bilan (D20), instantanés, largeurs 320–390 px, **mesure Pyodide** | EC |
| P10 | *(facultatif)* Pente au point exclu (D14) | EC |

Ordre d'exécution après la nuit du 02.11 : **R1, R2, P6, P9** (P10 plus tard).

---

## 7. Réponses aux questions de la nuit (03.11.2026)

Les numéros sont ceux de `suivi.md`.
✓ = choix de la nuit confirmé · ✎ = à changer (partie R1, R2 ou P9) · ⏸ = jugé à l'écran par l'enseignant en P9 · ⇥ = hors chantier.

| Q | Réponse |
|---|---|
| 1, 2 | ✓ R13 s'applique ; entier exact sans « ≈ » (voir §2, Extremums). |
| 3, 49 | ✓ Lecture retenue : le x cherché est du côté de l'AH, au-delà de tous les points à montrer et des valeurs interdites. |
| 4 | ✓ « (x²)′ = 2x » reste quand il justifie u′ (a, b, d). |
| 5 | ✓ −e^{−1}, −3e^{−1}, 4e^{−2} : une seule écriture, comme 3e^{−6}. |
| 6 | ✓ (1 − ln x)/x². |
| 7 | ✎ **R2** : jamais d'intertitre seul. Sous « 5. … », si la dérivée sort du cadre, la phrase de l'outil Dérivée (« Cette fonction sort du cadre de l'outil : la dérivée n'a pas été calculée. »). |
| 8, 9, 10 | ✓ (9 : sans objet). |
| 11 | ✎ **R2** : Somme-Produit pour **tout trinôme unitaire à racines entières** (x² − 3x + 2 = 0 ⇔ (x − 1)(x − 2) = 0 (Somme-Produit) ⇔ x = 1 ou x = 2), dans les parties 1 et 3. Sinon, les lignes de l'outil ED. |
| 12 | ✓ « On résout … » : le .tex fait foi dans l'EC. |
| 13 | ⇥ « ED = ]0 ; +∞[ = ]0 ; +∞[ » : correctif de l'outil ED, chantier séparé. |
| 14 | ✓ Somme-Produit aussi pour a² − b² (une seule méthode). |
| 15 | ✎ **R2** : la valeur approchée dans la formule, comme dans les autres outils. |
| 16–22 | ✓ |
| 23 | ✎ **R2** : tableau de signes de f avec **une ligne par facteur de la factorisation écrite dans la chaîne** (x − 1 et x − 3, pas x² − 4x + 3). Garde-fou : le produit des lignes est égal à f. |
| 24–27, 29–31 | ✓ |
| 28 | ✎ **R2** : séparateur des milliers ’ (convention du site) ; la valeur approchée est écrite aussi entre 1000 et 10⁶. |
| 32 | ✎ **R1** : mettre la règle R11 du guide à jour (tableau u/v de D8). |
| 33–36 | ✓ Écart accepté : f′ encadré dans l'écriture de l'outil (exposant en entier) ; g écrit développé dans la carte « Dérivée ». |
| 37 | ✎ **R1** (outil Dérivée) : l'exposant de f′ s'écrit **exactement comme dans l'énoncé** (mêmes termes, même ordre). Ajouter au corpus e^((x²+1)/(2x)) et e^((−2x²+3x−1)/(3x−6)), plus une famille tirée au hasard. |
| 38, 39 | ✓ |
| 40 | ✓ Règle de la nuit (voir §2) ; §5 d corrigé (x → −2⁻). |
| 41 | ✎ **R2** : une ligne de calcul pour **chaque** extremum dès que la substitution se vérifie (SymPy et sonde), avec la machinerie de la partie 2 (`valeur_verifiee`), pas seulement pour f = e^{u/v}. Exemples : b « f(−2) = ((−2)² − 6)e^{−2·(−2)} = (4 − 6)e⁴ = −2e⁴ » ; c « f(ln 3) = e^{ln 3}(6 − e^{ln 3}) = 3(6 − 3) = 9 ». La répétition de g(0) (déjà en partie 3) est acceptée, par régularité. |
| 42, 44, 45, 47, 48 | ✓ |
| 43 | ✎ **R2** : format révisé (voir §2, Extremums) : « **Maximum global** … » quand c'est prouvé, comme le .tex. |
| 46, 50, 51, 54 | ⏸ **P9** : captures à 390 px (Ex7, a–d, e^(1/x), x/(x²+1)) versées dans `suivi.md`. L'enseignant juge le défilement du tableau de d, l'échelle égale, les branches coupées et les étiquettes des zéros. |
| 52 | ✓ Deux ronds vides pour x/√(x²) ; mettre la spécification à jour. |
| 53, 55 | ✓ |
| 56 | ✎ **R1** (outil Dérivée, une seule rédaction) : on retire les facteurs qui ne s'annulent jamais, avec leur raison, puis produit nul : « f′(x) = 0 ⇔ x(x − 4) = 0 (car e^{…} > 0) ⇔ x = 0 ou x = 4 (produit nul) ; valeur interdite : x = 2 ». |

**Hors chantier, à noter pour plus tard** : le test instable `test_clavier.py::test_a_deux_formules…` ; Q13 (outil ED).

---

## 8. Réponses aux questions de la session 2 (04.11.2026)

Même légende qu'en §7. Les captures à 390 px ont été relues : **aucune affirmation fausse** n'y figure.

| Q | Réponse |
|---|---|
| 46 | ✓ Le tableau de d défile à 390 px : accepté (valeurs exactes gardées). |
| 50 | ✎ **R3** *(confirmé par l'enseignant le 04.11.2026)* : **abandon de l'échelle égale** dans le graphe de l'EC. Les axes x et y suivent chacun leur cadrage (§3), comme le .tex. Raison : à échelle égale, le graphe de b s'étend sur x ∈ [−80 ; 80] et la courbe n'est qu'un trait, celui de x/(x² + 1) est plat (y ∈ [−10 ; 10] pour des extremums à ±0,5). Cadrage (§3, Q49, Q51) inchangé. |
| 51, 54 | ✓ Branches coupées en y et coordonnées à côté des points gardées ; les chevauchements de b devraient disparaître avec Q50. |
| 57 | ✎ **R1 bis, dans R3** (outil Dérivée) : ligne des zéros de f′ avec les propriétés de la partie 3, réunies dans une parenthèse : « f′(x) = 0 ⇔ x(x − 4) = 0 (numérateur nul ; e^{…} > 0) ⇔ x = 0 ou x = 4 (produit nul) » ; « (on divise par −2 ; e^{−2x} > 0) » pour b ; « (numérateur nul ; on divise par −1) » pour x/(x² + 1). |
| 58 | ✓ |
| 59 | ✓ « (produit nul) » en fin de chaîne Somme-Produit : gardé (même règle que la ligne des zéros de f′). |
| 60–65 | ✓ (62 : « −2(−2) » accepté). |
| 66 | ✎ **R3** : une ligne par facteur du dénominateur factorisé en partie 1 dans le tableau de f (même garde-fou que Q23 : produit des lignes = f). |
| 67 | ✓ *(par défaut)* R6 du guide l'emporte : pas de « pas d'asymptote horizontale ». Si le .tex écrit une phrase en +∞ pour Ex7, l'enseignant le note ici et R6 est adapté pour l'EC. |
| 68–74 | ✓ (68, 71 : les fractions rationnelles gardent la rédaction R18 du guide des limites). |
| 75–82 | ✓ |
| 83 | ⇥ Chantier « robustesse », après la fusion : piste **(b)**, refus immédiat des tours d'exponentielles (e^x^x, e^(e^x), x^(x^x)) avec « pas encore prise en charge », comme sin(x). Dans le même chantier : le message trompeur de abs(x) (« Symbole inconnu « a » »). |

**Ajouts vus en relisant les captures et les tableaux « À relire »** :

| Point | Réponse |
|---|---|
| ln(x² − 4) dans l'outil Dérivée | ✎ **R3** (à vérifier, puis corriger si besoin) : la ligne « f′(x) = 0 ⇔ x = 0 » alors que 0 ∉ ED. Si aucune ligne ne rejette x = 0, ajouter « x = 0 est rejeté, car 0 ∉ ED » (phrase de la partie 3) et conclure « f′ ne s'annule pas sur ED ». |
| D7b, ligne manquante (c) | ✎ **R3** (outil Dérivée, seulement dans le cas « on développe d'abord ») : après les dérivées des termes, écrire « f′(x) = 6eˣ − 2e^{2x} = 2eˣ(3 − eˣ) (mise en évidence de 2eˣ) », une étape par ligne. Aujourd'hui, la page passe directement des dérivées des termes à 2eˣ(3 − eˣ). |
| Dérivée de x/(x² + 1) | ⇥ Plus tard (chantier Dérivée) : la ligne saute de (x² + 1 − x·2x)/(x² + 1)² à −(x + 1)(x − 1)/(x² + 1)² sans « = (1 − x²)/(x² + 1)² (réduction) ». Défaut antérieur, général à la règle du quotient. |
| Lignes coupées à 390 px | R3, **constat seulement** : dans la carte limite de x/(x² + 1), la ligne « = « −∞/+∞ » : forme indéterminée … » paraît coupée sur la capture. Vérifier si elle défile ou si elle est tronquée, et le noter sans corriger. |
