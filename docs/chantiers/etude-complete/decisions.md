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
- Format : « Maximum local en x = 0 : (0 ; e^{1/6}) ≈ (0 ; 1,18) (f′ passe de + à −) ».
- La valeur est **calculée en chaîne** quand l'exposant n'est pas immédiat : `g(4) = 18/12 = 3/2, donc f(4) = e^{3/2} ≈ 4,48`.
- **Global.** Un maximum en x₀ est global si f(x₀) est strictement plus grand que :
  - les autres maximums locaux ;
  - **toutes** les limites aux bornes de l'ED (±∞ et chaque côté de chaque valeur interdite).

  On l'écrit avec sa justification : « global : les autres valeurs de f sont plus petites (limites 0⁺ en ±∞) ». Règle symétrique pour un minimum.
- **Pas global** si une limite ou un autre extremum dépasse f(x₀). On l'écrit avec la raison : « pas global : f(x) → +∞ quand x → 2⁺ ».
- Si une limite vaut « ? » ou si le cas est limite (une limite égale à f(x₀)) : « local » seul, sans commentaire.
- Valeurs approchées (à aligner sur R13 ; si R13 dit autre chose, **R13 l'emporte** et on le signale) :

  | Valeur v | Écriture | Exemple |
  |---|---|---|
  | \|v\| ≥ 0,01 | 2 décimales | 1,18 |
  | 10⁻³ ≤ \|v\| < 0,01 | 2 chiffres significatifs | 0,0074 |
  | \|v\| < 10⁻³ | notation scientifique | 4,5·10⁻⁴ |

### Justification de 0⁺ / 0⁻ (D12) — validé
Règle, calquée sur le .tex : la **valeur d'essai** pour un dénominateur qui s'annule en a (zéro simple ou double).

> bas : 6x − 12 → 0 ; avec x = 1,99 : 6·1,99 − 12 = −0,06 < 0, donc 0⁻

Garde-fou : le point d'essai (a ± 0,01, ou plus près si nécessaire) est choisi de façon qu'**aucun autre zéro ni aucune valeur interdite** ne se trouve entre lui et a. Le signe est confirmé par la factorisation.
Le tableau R8 reste utilisé quand l'expression a plusieurs facteurs qui changent de signe près de a. Une seule règle pour l'EC et l'outil Limites.

### Asymptotes, position, points exclus (D13)
- AH : « Asymptote horizontale y = 0 (à gauche). f(x) → 0⁺ : le graphe est au-dessus. » La position n'est écrite que si le signe d'approche est démontré.
- Exposant → 0⁺ : « e^{0⁺} = 1⁺ (e^t > 1 pour t > 0) : le graphe est au-dessus de y = 1 ».
- AV d'un seul côté : « Asymptote verticale x = 2, seulement du côté droit. À gauche, f(x) → 0⁺ : le graphe s'approche du point (2 ; 0), qui n'appartient pas au graphe (rond vide). »

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
- Extremum : max (0 ; e^{−1/2}) ≈ (0 ; 0,61), pas global : f(x) → +∞ quand x → 2⁺.

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
| P6 | Partie 4 : D12, D13, D16 | **Limites** |
| P7a | Dérivée de l'exposant détaillée, tableau u/v (D7, D8, D7b si simple) | **Dérivée** |
| P7b | Valeurs dans le tableau de variations (D10), extremums (D11) | EC + **Dérivée** |
| P8 | Graphe (D15, §3) | EC |
| P9 | Exemples (D18), Bilan (D20), instantanés, largeurs 320–390 px, **mesure Pyodide** | EC |
| P10 | *(facultatif)* Pente au point exclu (D14) | EC |
