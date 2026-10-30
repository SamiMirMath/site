# Spécification : rédaction des limites (3M), d'après le corrigé du chapitre 8

Source de vérité : `docs/reference/limites/ch8-corrige-limites.pdf` (« Corrigé détaillé, exercices 8.8 à 8.14, exemples 5 et 6 », Sami Mir).
Ce document est le **contrat des tests** du chantier « refonte de la rédaction » (branche `refonte-redaction-3m`, 29.10.2026).
Il complète `docs/specifications/limites-asymptotes.md` (doctrine, périmètre) et `docs/guide-redaction.md` (ton, notations).

## 1. Vocabulaire des blocs

| Bloc | Contenu | Rendu |
|---|---|---|
| **Carte « Étape n : titre »** | une étape de la descente | une carte, titre en gras, navigable (« Étape suivante », « Tout afficher ») |
| **Prédiction** | encadré « Prédiction avec la règle du podium » : phrases + « On s'attend à : … » | encadré violet |
| **Attention** | encadré rouge « Attention » (piège évité) | encadré rouge |
| **Piège** | encadré rouge « Le piège » (BH qui empire) | encadré rouge |
| **Autre méthode** | encadré orange « Autre méthode : … » | encadré orange |
| **Tableau BH** | deux lignes : « haut : f ⟶ dérivée : f′ » / « bas : g ⟶ dérivée : g′ » | tableau centré |
| **Chaîne** | `lim f/g =^BH lim f′/g′ = …` (+ « forme … : encore indéterminée ») | formule centrée |
| **Résultat** | `lim … = …` encadré vert | encadré vert |
| **Confirmation** | « ✓ Le calcul confirme la prédiction du podium. » (vert italique) | ligne |

Mots de forme : « **indéterminée** » (rouge) ; « **pas indéterminée** » (vert).

## 2. Règles R1 à R20

R1  Déroulement **descendant** : on part de la limite demandée et on descend en une seule suite d'étapes. Plus de blocs imbriqués calculés « avant ». Une sous-limite nécessaire est annoncée et calculée là où on en a besoin (« On calcule à part … »), puis citée quand on la réutilise.
R2  « Étape 1 : on remplace. » Haut : … → … / Bas : … → … (ou chaque facteur d'un produit), avec les intermédiaires du corrigé (« −x → +∞, donc e^(−x) → +∞ »). Puis « Forme … : indéterminée. » ou « Forme … : pas indéterminée ! ».
R3  Forme déterminée : « Étape 2 : on conclut directement. » + la phrase du corrigé (règle des signes ; « un nombre minuscule divisé par un nombre énorme reste minuscule »…) + la chaîne (= « 0⁺/+∞ » = 0⁺). Si la forme ressemble à un piège (0/∞, ∞/0, ∞·∞) : encadré « Attention » comme Ex5 d) et 8.12 c).
R4  Forme indéterminée : encadré « Prédiction avec la règle du podium » : au haut / au bas (ou le produit), qui gagne (eˣ bat xⁿ qui bat ln x ; entre puissances, la plus grande gagne ; à égalité, quotient des coefficients), signe à part, « On s'attend à : … ». En x → −∞ ou 0⁺ : « On pense à t = −x » ou « t = 1/x ». Si le podium ne s'applique pas (8.14) : « Ici, le podium ne peut pas aider… », tableau de valeurs calculé en haute précision (format du corrigé : 0,8515 ; 0,99998 ; ≈ 1), puis « La calculatrice ne prouve rien… ». La prédiction est calculée par des règles puis comparée au résultat final. Si elles divergent, la prédiction n'est pas affichée et un test échoue (c'est un bug).
R5  Le podium ne justifie jamais une égalité.
R6  0·(±∞) : « Étape : on transforme le produit en quotient. BH ne marche pas sur un produit. On écrit x³ = 1/x⁻³ : … ». ln reste en haut, avec la remarque « Pourquoi garder ln(x) en haut ? Parce que sa dérivée 1/x est simple. Si on mettait 1/ln(x) en bas, sa dérivée serait compliquée. » ; eᵘ = 1/e^(−u). Puis « Étape : on vérifie la forme. » avec Haut / Bas.
R7  Constante : « Étape : on sort la constante. Propriété des puissances : e^(3x−5) = e^(3x)·e⁻⁵. Le nombre e⁻⁵ ≈ 0,0067 est une constante positive : elle ne change ni le signe ni le résultat « 0 ou ∞ ». On la garde de côté. » À la fin : « Étape : on n'oublie pas la constante. e⁻⁵·0⁻ = 0⁻ ».
R8  Simplification préalable : « Étape : on simplifie le logarithme. Propriété des logarithmes : ln(x³) = 3 ln(x) » (8.12 b), et toute simplification évidente avant BH.
R9  BH : « Étape k : BH (1re fois). », puis le tableau sur deux lignes, AVANT la chaîne : « haut : … ⟶ dérivée : … » / « bas : … ⟶ dérivée : … », puis la chaîne « lim … =^BH lim f′/g′ ». Les dérivées composées sont expliquées comme dans le corrigé (« on utilise (eᵘ)′ = u′eᵘ avec u = 1/x, u′ = −1/x² » ; « on pose u = −x… »).
R10 Après BH, on garde la forme quotient. La simplification est une étape à part : « Étape : on simplifie. Diviser par 1/x, c'est multiplier par x : … », « (Les deux −1/x² se simplifient.) ». Jamais de retour au produit suivi d'une nouvelle mise en quotient. Les simplifications triviales (facteur constant, signes) restent dans la chaîne, après un « = ».
R11 Avant chaque nouveau BH, la forme est revérifiée et écrite avec ses signes : « forme −∞/+∞ : encore indéterminée. » (à droite de la chaîne, ou « Étape : on vérifie la forme »). Au moins trois BH de suite.
R12 « BH tourne en rond » (8.12 h) : encadré « Le piège » qui montre le BH qui empire, puis « Étape : on réécrit » et le bon quotient.
R13 Étape finale « on remplace » : « x eˣ → (+∞)·(+∞) = +∞ : pas indéterminée. »
R14 Une forme indéterminée n'est **jamais** suivie de « = valeur ». Test sur tout le corpus.
R15 Résultat encadré « lim … = … », puis « ✓ Le calcul confirme la prédiction du podium. » (pour 8.14 : « La calculatrice avait bien « deviné » : le calcul le confirme. »).
R16 e^(…) et ln(…) : « Étape 1 : limite de l'exposant, à part. » (ou de l'intérieur), prédiction (« exposant → 3, donc e^… → e³ »), « Calcul avec BH : », puis « Étape 2 : on applique l'exponentielle. » (ou « le logarithme »). Les fractions rationnelles DANS un exposant ou dans un ln se traitent par BH, comme Ex6 et 8.13.
R17 Notation : 0⁺ / 0⁻ dès que le signe est connu, y compris dans le résultat ; un infini négatif entre parenthèses dans un produit ((−∞)·0⁺) ; valeur exacte puis approchée (e³ ≈ 20,09 ; √e ≈ 1,65 ; ln 3 ≈ 1,10), virgule décimale.
R18 Fonctions purement rationnelles (sans exp, ln, aˣ) : méthodes actuelles inchangées (mise en évidence, factorisation, division euclidienne). Voir `docs/a-valider.md`.
R19 « Trou » est réservé à un point intérieur de l'ensemble de définition. Au bord : « Le graphe s'arrête au point (0 ; 1), qui n'en fait pas partie. » (à valider).
R20 Vouvoiement ; vocabulaire du corrigé (« haut », « bas », « on remplace », « podium »).

### Titres d'étapes (vocabulaire fermé)

`on remplace` · `on conclut directement` · `on transforme le produit en quotient` · `on sort la constante` · `on simplifie le logarithme` · `on vérifie la forme` · `BH` / `BH (1re fois)` / `BH (2e fois)` / `BH (3e fois)` · `on simplifie` · `on réécrit` · `on n'oublie pas la constante` · `limite de l'exposant, à part` · `limite de l'intérieur du ln` · `on applique l'exponentielle` · `on applique le logarithme` · `les dérivées` (8.14, composées).
Numérotation : « Étape 1 », « Étape 2 », … sans trou. « BH » seul s'il n'y a qu'un seul BH dans la descente, sinon « BH (1re fois) », « (2e fois) », …

## 3. Transcriptions du corrigé (contrat des tests)

Notation : `E n [titre]` = carte « Étape n : titre » ; `P` = prédiction ; `T` = tableau BH (haut → dérivée / bas → dérivée) ; `C` = chaîne ; `R` = résultat encadré ; `✓` = confirmation. Les formules sont en LaTeX allégé (`->` pour →, `^` exposant).

### Exercice 8.11

**a) lim_{x→+∞} e^x / ln(x)**
- E1 [on remplace] Haut : e^x → +∞. Bas : ln(x) → +∞. Forme +∞/+∞ : indéterminée.
- P : Au haut : e^x. Au bas : ln(x). Sur le podium, e^x bat ln(x) : c'est le **haut** qui gagne, donc le quotient part vers l'infini. Signe : haut > 0, bas > 0, donc quotient > 0. On s'attend à : +∞
- E2 [BH] « On dérive le haut et le bas séparément : » T : haut : e^x → dérivée : e^x ; bas : ln(x) → dérivée : 1/x. C : lim e^x/ln x =BH lim e^x/(1/x).
- E3 [on simplifie] « Diviser par 1/x, c'est multiplier par x : » e^x/(1/x) = e^x·x.
- E4 [on remplace à nouveau] e^x → +∞ et x → +∞, donc x e^x → (+∞)·(+∞) = +∞ : pas indéterminée.
- R : lim e^x/ln(x) = +∞ ; ✓.
- (Outil : « on remplace » au lieu de « on remplace à nouveau » : écart mineur.)

**b) lim_{x→0⁺} x³ ln(x)**
- E1 [on remplace] x³ → (0⁺)³ = 0⁺. ln(x) → −∞ (quand x → 0⁺, le graphe de ln plonge vers le bas). Forme 0·(−∞) : indéterminée.
- P : Produit : x³ → 0 et ln(x) → −∞. La puissance x³ est plus forte que ln(x) (le podium reste vrai en 0⁺) : c'est x³ qui impose sa limite, donc 0. Signe : pour 0 < x < 1, x³ > 0 et ln(x) < 0, donc produit < 0. On s'attend à : 0⁻
- E2 [on transforme le produit en quotient] BH ne marche pas sur un produit. On écrit x³ = 1/x⁻³ : x³ ln(x) = ln(x)/x⁻³. Remarque : « Pourquoi garder ln(x) en haut ? Parce que sa dérivée 1/x est simple. Si on mettait 1/ln(x) en bas, sa dérivée serait compliquée. »
- E3 [on vérifie la forme] Haut : ln(x) → −∞. Bas : x⁻³ = 1/x³ → 1/0⁺ = +∞. Forme −∞/+∞ : indéterminée, on peut utiliser BH.
- E4 [BH] T : haut : ln(x) → dérivée : 1/x ; bas : x⁻³ → dérivée : −3x⁻⁴ = −3/x⁴. C : lim ln(x)/x⁻³ =BH lim (1/x)/(−3/x⁴).
- E5 [on simplifie] (diviser par une fraction = multiplier par son inverse) : (1/x)/(−3/x⁴) = (1/x)·(−x⁴/3) = −x⁴/(3x) = −x³/3.
- E6 [on remplace] x³ → 0⁺, donc −x³/3 → 0⁻ : pas indéterminée.
- R : lim x³ ln(x) = 0⁻ ; ✓.

**c) lim_{x→−∞} x² e^x**
- E1 [on remplace] x² → (−∞)² = +∞. e^x → e^(−∞) = 0⁺. Forme (+∞)·0 : indéterminée.
- P : Produit : x² → +∞ et e^x → 0. L'exponentielle bat la puissance : c'est e^x qui impose sa limite, donc 0. Signe : x² > 0 et e^x > 0, donc produit > 0. On s'attend à : 0⁺
- E2 [on transforme en quotient] On écrit e^x = 1/e^(−x) : x² e^x = x²/e^(−x).
- E3 [on vérifie la forme] Haut : x² → +∞. Bas : −x → +∞, donc e^(−x) → +∞. Forme +∞/+∞ : indéterminée.
- E4 [BH (1re fois)] T : haut : x² → dérivée : 2x ; bas : e^(−x) → dérivée : −e^(−x). C : lim x²/e^(−x) =BH lim 2x/(−e^(−x)).
- E5 [on vérifie la forme] Haut : 2x → −∞. Bas : −e^(−x) → −∞. Forme −∞/−∞ : encore indéterminée.
- E6 [BH (2e fois)] T : haut : 2x → dérivée : 2 ; bas : −e^(−x) → dérivée : −(−e^(−x)) = e^(−x). C : lim 2x/(−e^(−x)) =BH lim 2/e^(−x).
- E7 [on remplace] e^(−x) → +∞, donc 2/e^(−x) → 2/(+∞) = 0⁺ : pas indéterminée.
- R : lim x² e^x = 0⁺ ; ✓.

**d) lim_{x→+∞} x² e^(−5x)**
- E1 [on remplace] x² → +∞. −5x → −∞, donc e^(−5x) → 0⁺. Forme (+∞)·0 : indéterminée.
- P : Produit : x² → +∞ et e^(−5x) → 0. L'exponentielle bat la puissance : c'est e^(−5x) qui impose sa limite, donc 0. Signe : x² > 0 et e^(−5x) > 0, donc produit > 0. On s'attend à : 0⁺
- E2 [on transforme en quotient] e^(−5x) = 1/e^(5x), donc x² e^(−5x) = x²/e^(5x). Haut → +∞, bas → +∞ : forme +∞/+∞, indéterminée.
- E3 [BH (1re fois)] T : haut : x² → dérivée : 2x ; bas : e^(5x) → dérivée : 5e^(5x). C : lim x²/e^(5x) =BH lim 2x/(5e^(5x))  forme +∞/+∞ : encore indéterminée.
- E4 [BH (2e fois)] T : haut : 2x → dérivée : 2 ; bas : 5e^(5x) → dérivée : 25e^(5x). C : lim 2x/(5e^(5x)) =BH lim 2/(25e^(5x)) = 2/(+∞) = 0⁺.
- R : lim x² e^(−5x) = 0⁺ ; ✓.

### Exemple 5

**a) lim_{x→+∞} x² e^(−x)**
- E1 [on remplace] x² → +∞ et e^(−x) → e^(−∞) = 0⁺. Forme (+∞)·0 : indéterminée.
- P : Produit : x² → +∞ et e^(−x) → 0. L'exponentielle bat la puissance : e^(−x) impose sa limite, donc 0. Signe : tout est positif. On s'attend à : 0⁺
- E2 [quotient] x² e^(−x) = x²/e^x. Forme +∞/+∞ : indéterminée.
- E3 [BH deux fois] lim x²/e^x =BH lim 2x/e^x (forme +∞/+∞) =BH lim 2/e^x = 2/(+∞) = 0⁺.
- R : lim x² e^(−x) = 0⁺ ; ✓.
- (Outil : deux étapes BH détaillées comme 8.11 c ; la version condensée du corrigé n'est pas reproduite : écart signalé.)

**b) lim_{x→0⁺} x·e^(1/x)**
- E1 [on remplace] x → 0⁺. 1/x → 1/0⁺ = +∞, donc e^(1/x) → +∞. Forme 0·(+∞) : indéterminée.
- P : On pense à t = 1/x : quand x → 0⁺, t → +∞, et x e^(1/x) = e^t/t. L'exponentielle (au haut) bat la puissance (au bas) : le quotient part vers l'infini. Signe : tout est positif. On s'attend à : +∞
- E2 [quotient] On écrit x = 1/(1/x) : x e^(1/x) = e^(1/x)/(1/x). Forme +∞/+∞ : indéterminée.
- E3 [BH] « Pour dériver e^(1/x), on utilise (e^u)′ = u′e^u avec u = 1/x, u′ = −1/x² : » T : haut : e^(1/x) → dérivée : −(1/x²)e^(1/x) ; bas : 1/x → dérivée : −1/x². C : lim e^(1/x)/(1/x) =BH lim (−(1/x²)e^(1/x))/(−1/x²) = lim e^(1/x) = +∞. « (Les deux −1/x² se simplifient.) »
- R : lim x e^(1/x) = +∞ ; ✓.

**c) lim_{x→−∞} e^(−x)/x²**
- E1 [on remplace] Haut : −x → +∞, donc e^(−x) → +∞. Bas : x² → +∞. Forme +∞/+∞ : indéterminée.
- P : Au haut : e^(−x) → +∞. Au bas : x² → +∞. L'exponentielle bat la puissance : c'est le **haut** qui gagne. Signe : haut > 0, bas > 0. On s'attend à : +∞
- E2 [BH (1re fois)] T : haut : e^(−x) → dérivée : −e^(−x) ; bas : x² → dérivée : 2x. C : lim e^(−x)/x² =BH lim (−e^(−x))/(2x)  forme −∞/−∞ : indéterminée.
- E3 [BH (2e fois)] T : haut : −e^(−x) → dérivée : e^(−x) ; bas : 2x → dérivée : 2. C : lim (−e^(−x))/(2x) =BH lim e^(−x)/2 = +∞/2 = +∞.
- R : lim e^(−x)/x² = +∞ ; ✓.

**d) lim_{x→+∞} e^(−x)/(4x)**
- E1 [on remplace] Haut : e^(−x) → 0⁺. Bas : 4x → +∞. Forme 0⁺/(+∞) : **pas indéterminée** !
- E2 [on conclut directement] « Un nombre minuscule divisé par un nombre énorme reste minuscule : » R : lim e^(−x)/(4x) = 0⁺/(+∞) = 0⁺.
- Attention : « Ici, il **ne faut pas** utiliser BH : la forme 0/∞ n'est pas indéterminée. C'est exactement pour cela qu'on vérifie **toujours** la forme en premier. »
- Pas de prédiction, pas de ✓.

### Exercice 8.12

**a) lim_{x→+∞} ln(x)/e^(2x)**
- E1 [on remplace] Haut : ln(x) → +∞. Bas : 2x → +∞, donc e^(2x) → +∞. Forme +∞/+∞ : indéterminée.
- P : Au haut : ln(x). Au bas : e^(2x). Sur le podium, l'exponentielle bat ln(x) : c'est le **bas** qui gagne, donc le quotient tend vers 0. Signe : haut > 0 et bas > 0 (pour x > 1). On s'attend à : 0⁺
- E2 [BH] T : haut : ln(x) → dérivée : 1/x ; bas : e^(2x) → dérivée : 2e^(2x). C : lim ln x/e^(2x) =BH lim (1/x)/(2e^(2x)).
- E3 [on simplifie] (1/x)/(2e^(2x)) = (1/x)·(1/(2e^(2x))) = 1/(2x e^(2x)).
- E4 [on remplace] 2x → +∞ et e^(2x) → +∞, donc 2x e^(2x) → +∞ et 1/(2x e^(2x)) → 1/(+∞) = 0⁺.
- R : lim ln(x)/e^(2x) = 0⁺ ; ✓.

**b) lim_{x→+∞} e^(−x) ln(x³)**
- E1 [on remplace] e^(−x) → 0⁺. x³ → +∞, donc ln(x³) → +∞. Forme 0·(+∞) : indéterminée.
- P : Produit : e^(−x) → 0 et ln(x³) = 3 ln(x) → +∞. L'exponentielle bat le logarithme : e^(−x) impose sa limite, donc 0. Signe : e^(−x) > 0 et ln(x³) > 0 (pour x > 1). On s'attend à : 0⁺
- E2 [on simplifie le logarithme] Propriété des logarithmes : ln(x³) = 3 ln(x). Donc e^(−x) ln(x³) = 3 e^(−x) ln(x).
- E3 [quotient] e^(−x) = 1/e^x, donc 3e^(−x) ln(x) = 3 ln(x)/e^x. Forme +∞/+∞ : indéterminée.
- E4 [BH] T : haut : 3 ln(x) → dérivée : 3/x ; bas : e^x → dérivée : e^x. C : lim 3 ln x/e^x =BH lim (3/x)/e^x = lim 3/(x e^x).
- E5 [on remplace] x e^x → (+∞)·(+∞) = +∞, donc 3/(x e^x) → 3/(+∞) = 0⁺.
- R : lim e^(−x) ln(x³) = 0⁺ ; ✓.

**c) lim_{x→−∞} e^(−x)·x**
- E1 [on remplace] −x → +∞, donc e^(−x) → +∞. x → −∞. Forme (+∞)·(−∞) : **pas indéterminée** !
- E2 [on conclut directement] (règle des signes : + · − = −) : R : lim e^(−x) x = (+∞)·(−∞) = −∞.
- Attention : « Pas de BH ici : un produit de deux « énormes » n'est jamais indéterminé. »

**d) lim_{x→−∞} e^x ln(−x)**
- E1 [on remplace] e^x → e^(−∞) = 0⁺. −x → +∞, donc ln(−x) → +∞. Forme 0·(+∞) : indéterminée. Remarque : ln(−x) existe bien, car quand x est négatif, −x est positif.
- P : Produit : e^x → 0 et ln(−x) → +∞. L'exponentielle bat le logarithme : e^x impose sa limite, donc 0. Signe : e^x > 0 et ln(−x) > 0 (pour x < −1). On s'attend à : 0⁺
- E2 [quotient] e^x = 1/e^(−x), donc e^x ln(−x) = ln(−x)/e^(−x). Forme +∞/+∞ : indéterminée.
- E3 [les dérivées (attention aux composées)] • (ln(−x))′ : on pose u = −x, u′ = −1. Alors (ln u)′ = u′/u = −1/(−x) = 1/x. • (e^(−x))′ = −e^(−x). T : haut : ln(−x) → dérivée : 1/x ; bas : e^(−x) → dérivée : −e^(−x).
- E4 [BH et simplification] lim ln(−x)/e^(−x) =BH lim (1/x)/(−e^(−x)) = lim 1/(x·(−e^(−x))) = lim 1/((−x)e^(−x)).
- E5 [on remplace] −x → +∞ et e^(−x) → +∞, donc (−x)e^(−x) → +∞ et 1/((−x)e^(−x)) → 1/(+∞) = 0⁺.
- R : lim e^x ln(−x) = 0⁺ ; ✓.
- (Outil : « BH » puis « on simplifie » en deux étapes au lieu de « BH et simplification » : écart mineur.)

**e) lim_{x→−∞} x³ e^(3x−5)**
- E1 [on remplace] x³ → (−∞)³ = −∞. 3x−5 → −∞, donc e^(3x−5) → 0⁺. Forme (−∞)·0 : indéterminée.
- P : Produit : x³ → −∞ et e^(3x−5) → 0. L'exponentielle bat la puissance : e^(3x−5) impose sa limite, donc 0. Signe : x³ < 0 (car x < 0) et e^(3x−5) > 0, donc produit < 0. On s'attend à : 0⁻
- E2 [on sort la constante] Propriété des puissances : e^(3x−5) = e^(3x)·e⁻⁵. Le nombre e⁻⁵ ≈ 0,0067 est une **constante positive** : elle ne change ni le signe ni le résultat « 0 ou ∞ ». On la garde de côté : x³ e^(3x−5) = e⁻⁵·x³ e^(3x).
- E3 [quotient] e^(3x) = 1/e^(−3x), donc x³ e^(3x) = x³/e^(−3x). Haut → −∞, bas → +∞ : forme −∞/+∞ : indéterminée.
- E4 [BH (1re fois)] T : haut : x³ → dérivée : 3x² ; bas : e^(−3x) → dérivée : −3e^(−3x). C : lim x³/e^(−3x) =BH lim 3x²/(−3e^(−3x)) = lim −x²/e^(−3x)  forme −∞/+∞ : indéterminée.
- E5 [BH (2e fois)] T : haut : −x² → dérivée : −2x ; bas : e^(−3x) → dérivée : −3e^(−3x). C : lim −x²/e^(−3x) =BH lim −2x/(−3e^(−3x)) = lim 2x/(3e^(−3x))  forme −∞/+∞ : indéterminée.
- E6 [BH (3e fois)] T : haut : 2x → dérivée : 2 ; bas : 3e^(−3x) → dérivée : −9e^(−3x). C : lim 2x/(3e^(−3x)) =BH lim 2/(−9e^(−3x)) = 2/(−∞) = 0⁻.
- E7 [on n'oublie pas la constante] e⁻⁵·0⁻ = 0⁻ (une constante positive fois un nombre minuscule négatif).
- R : lim x³ e^(3x−5) = 0⁻ ; ✓.

**f) lim_{x→0⁺} e^(1/x)/x²**
- E1 [on remplace] Haut : 1/x → +∞, donc e^(1/x) → +∞. Bas : x² → 0⁺. Forme (+∞)/0⁺ : **pas indéterminée** !
- E2 [on conclut directement] « Un nombre énorme (positif) divisé par un nombre minuscule positif devient encore plus énorme : » R : lim e^(1/x)/x² = (+∞)/0⁺ = +∞.

**g) lim_{x→0⁺} e^(1/x) x²**
- E1 [on remplace] e^(1/x) → +∞ (comme en f)). x² → 0⁺. Forme (+∞)·0 : indéterminée.
- P : On pense à t = 1/x → +∞ : alors x² = 1/t² et e^(1/x) x² = e^t/t². L'exponentielle (au haut) bat la puissance (au bas) : le quotient part vers l'infini. Signe : tout est positif. On s'attend à : +∞
- E2 [quotient] x² = 1/x⁻², donc e^(1/x) x² = e^(1/x)/x⁻². Bas : x⁻² = 1/x² → 1/0⁺ = +∞. Forme +∞/+∞ : indéterminée.
- E3 [BH (1re fois)] T : haut : e^(1/x) → dérivée : −(1/x²)e^(1/x) ; bas : x⁻² → dérivée : −2x⁻³ = −2/x³. C : lim e^(1/x)/x⁻² =BH lim (−(1/x²)e^(1/x))/(−2/x³).
- E4 [on simplifie] (−(1/x²)e^(1/x))/(−2/x³) = (e^(1/x)/x²)·(x³/2) = x e^(1/x)/2.
- E5 [on remplace] x → 0⁺ et e^(1/x) → +∞ : forme 0·(+∞), encore indéterminée. Mais c'est exactement l'exemple 5 b), où l'on a trouvé lim x e^(1/x) = +∞. Donc lim x e^(1/x)/2 = (+∞)/2 = +∞.
- R : lim e^(1/x) x² = +∞ ; ✓.
- Autre méthode : le changement de variable. On pose t = 1/x. Quand x → 0⁺, t → +∞, et x² = 1/t². Alors e^(1/x) x² = e^t/t² → +∞ (podium : e^t bat t²).
- (Outil : la citation de l'exemple 5 b) devient « On calcule à part … » (R1) ; l'encadré « Autre méthode » est facultatif.)

**h) lim_{x→0⁺} e^(−1/x)/x**
- E1 [on remplace] Haut : −1/x → −∞, donc e^(−1/x) → 0⁺. Bas : x → 0⁺. Forme 0⁺/0⁺ : indéterminée.
- P : On pense à t = 1/x → +∞ : alors e^(−1/x)/x = t e^(−t) = t/e^t. L'exponentielle (au bas) bat la puissance (au haut) : le quotient tend vers 0. Signe : tout est positif. On s'attend à : 0⁺
- Piège : « Si on applique BH directement : lim e^(−1/x)/x =BH lim ((1/x²)e^(−1/x))/1 = e^(−1/x)/x² on retombe sur une forme 0/0… **encore pire** qu'au départ (x² au lieu de x) ! BH tourne en rond. Il faut d'abord **réécrire** l'expression autrement. »
- E2 [on réécrit] e^(−1/x) = 1/e^(1/x) et 1/x reste en haut : e^(−1/x)/x = (1/x)·e^(−1/x) = (1/x)/e^(1/x). Haut → +∞, bas → +∞ : forme +∞/+∞ : indéterminée.
- E3 [BH] T : haut : 1/x → dérivée : −1/x² ; bas : e^(1/x) → dérivée : −(1/x²)e^(1/x). C : lim (1/x)/e^(1/x) =BH lim (−1/x²)/(−(1/x²)e^(1/x)) = lim 1/e^(1/x). « (Les deux −1/x² se simplifient.) »
- E4 [on remplace] e^(1/x) → +∞, donc 1/e^(1/x) → 1/(+∞) = 0⁺.
- R : lim e^(−1/x)/x = 0⁺ ; ✓.

### Exemple 6 (exponentielle d'une fraction)

**lim_{x→+∞} e^((3x+4)/(x−2))**
- E1 [limite de l'exposant, à part] 3x+4 → +∞ et x−2 → +∞ : forme +∞/+∞, indéterminée.
- P : Même puissance x en haut et en bas : égalité ! On s'attend au quotient des coefficients : 3/1 = 3. On s'attend à : exposant → 3, donc e^… → e³
- « Calcul avec BH : » lim (3x+4)/(x−2) =BH lim 3/1 = 3.
- E2 [on applique l'exponentielle] R : lim e^((3x+4)/(x−2)) = e³ ≈ 20,09 ; ✓.

### Exercice 8.13

**a) lim_{x→+∞} e^(−x)** — Exposant : −x → −∞. Donc e^(−x) → e^(−∞). R : lim e^(−x) = 0⁺. (pas de carte « Étape », pas de prédiction)
**b) lim_{x→+∞} e^((x²−3x+2)/(2x²))**
- E1 [limite de l'exposant] Haut et bas → +∞ : forme +∞/+∞, indéterminée.
- P : Même puissance x² en haut et en bas : égalité ! On s'attend au quotient des coefficients : 1/2. On s'attend à : exposant → 1/2, donc e^… → e^(1/2)
- « Calcul avec BH : » lim (x²−3x+2)/(2x²) =BH lim (2x−3)/(4x) (forme +∞/+∞) =BH lim 2/4 = 1/2.
- E2 [exponentielle] R : lim = e^(1/2) = √e ≈ 1,65 ; ✓.
**c) lim_{x→+∞} e^(−2x/(x²−5))**
- E1 [limite de l'exposant] Haut : −2x → −∞. Bas : x²−5 → +∞. Forme −∞/+∞, indéterminée.
- P : En haut x, en bas x² : la plus grande puissance est **au bas**, donc l'exposant tend vers 0. Signe : haut < 0, bas > 0, donc 0⁻. On s'attend à : exposant → 0⁻, donc e^… → e⁰ = 1
- « Calcul avec BH : » lim −2x/(x²−5) =BH lim −2/(2x) = lim (−1/x) = 0⁻.
- E2 [exponentielle] e⁰ = 1 : R : lim e^(−2x/(x²−5)) = e⁰ = 1 ; ✓.
**d) lim_{x→−∞} e^((3x²+2)/(2x))**
- E1 [limite de l'exposant] Haut : 3x²+2 → +∞. Bas : 2x → −∞. Forme +∞/−∞, indéterminée.
- P : En haut x², en bas x : la plus grande puissance est **au haut**, donc l'exposant part vers l'infini. Signe : haut > 0, bas < 0, donc −∞. On s'attend à : exposant → −∞, donc e^… → 0⁺
- « Calcul avec BH : » lim (3x²+2)/(2x) =BH lim 6x/2 = lim 3x = −∞.
- E2 [exponentielle] R : lim = e^(−∞) = 0⁺ ; ✓.
**e) lim_{x→+∞} ln((3x²−3x+2)/(x²−5x+2))**
- E1 [limite de l'intérieur du ln] Haut et bas → +∞ : forme +∞/+∞, indéterminée.
- P : Même puissance x² en haut et en bas : égalité ! On s'attend au quotient des coefficients : 3/1 = 3. On s'attend à : intérieur → 3, donc ln(…) → ln(3)
- « Calcul avec BH : » lim (3x²−3x+2)/(x²−5x+2) =BH lim (6x−3)/(2x−5) (forme +∞/+∞) =BH lim 6/2 = 3.
- E2 [logarithme] R : lim ln(…) = ln(3) ≈ 1,10 ; ✓.
**f) lim_{x→+∞} ln(1/x)** — Intérieur : 1/x → 1/(+∞) = 0⁺. Et ln(0⁺) = −∞. R : lim ln(1/x) = −∞. « Autre façon : ln(1/x) = −ln(x) → −∞. »

### Exercice 8.14

**lim_{x→−∞} ln(1+e^x)/e^x**
- (a) « En remplaçant naïvement. » e^x → e^(−∞) = 0⁺. Donc le haut tend vers ln(1+0) = ln(1) = 0 et le bas vers 0⁺. Forme 0/0 : indéterminée. On ne peut rien conclure ainsi.
- P (podium inapplicable) : « Ici, le podium **ne peut pas aider** : il n'y a pas de « course » entre une exponentielle, une puissance et un logarithme qui partent vers l'infini. Le haut et le bas tendent tous les deux vers 0. Pour prédire, on utilise la calculatrice (point b). »
- (b) « À la calculatrice. » tableau : x = −1, −10, −20, −25, −30 ; ln(1+e^x)/e^x = 0,8515 ; 0,99998 ; ≈ 1 ; ≈ 1 ; ≈ 1. « On devine que la limite vaut 1. Remarque : pour x = −25 ou x = −30, certaines calculatrices affichent des valeurs bizarres (par exemple 0,998 ou 1,000004) à cause des arrondis sur des nombres minuscules. La calculatrice ne prouve rien : c'est le calcul qui suit qui donne la réponse sûre. »
- E1 [la forme] D'après a), forme 0/0 : indéterminée.
- E2 [les dérivées] Pour le haut, on utilise (ln u)′ = u′/u avec u = 1+e^x et u′ = e^x. T : haut : ln(1+e^x) → dérivée : e^x/(1+e^x) ; bas : e^x → dérivée : e^x.
- E3 [BH et simplification] lim ln(1+e^x)/e^x =BH lim (e^x/(1+e^x))/e^x = lim e^x/(1+e^x)·1/e^x = lim 1/(1+e^x).
- E4 [on remplace] e^x → 0⁺, donc 1+e^x → 1 et 1/(1+e^x) → 1/1 = 1.
- R : lim ln(1+e^x)/e^x = 1. « La calculatrice avait bien « deviné » : le calcul le confirme. »
- (Outil : la partie (a) devient l'étape 1 « on remplace » ; le tableau de valeurs précède le calcul ; « BH et simplification » devient « BH » + « on simplifie » : écart mineur.)

## 4. Fiche réflexe (rappel de la méthode)

| Forme obtenue | Ce que je fais |
|---|---|
| Pas indéterminée | Je conclus directement (règles des signes, « nbre sur 0^± »…). |
| 0/0 ou ±∞/±∞ | Je prédis avec le podium, puis BH : je dérive le haut, je dérive le bas, je revérifie la forme. À la fin, je compare avec la prédiction. |
| 0·(±∞) | Je transforme en quotient (e^x = 1/e^(−x), x^k = 1/x^(−k)), en gardant ln en haut. |
| e^… ou ln(…) | Je calcule d'abord la limite de l'exposant (ou de l'intérieur), à part. |
| BH « tourne en rond » | Je réécris autrement l'expression (voir 8.12 h). |

## 5. Tests dérivés

1. **Structure** : pour chaque exercice ci-dessus, la suite des titres d'étapes, le nombre de BH, les dérivées haut/bas, la forme revérifiée avec ses signes, la présence de la prédiction, le résultat avec signe et le ✓ — contre cette transcription. Les écarts de formulation mineurs sont listés dans `suivi-refonte.md`.
2. **Transverses** (tout le corpus de `tests/python/donnees/corpus_limites_3m.py`) : R14 ; aucun « croissance comparée » ; valeurs contre l'oracle mpmath ; signe 0⁺/0⁻ ; au plus 13 replis ; prédiction cohérente avec le résultat.
3. **Page** : 360 px, aucun défilement horizontal.
