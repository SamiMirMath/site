# Équations du 2e degré : décisions

**Statut : validé par l'enseignant le 05.11.2026, complété le même soir après le plan d'exécution (§ 13, qui prime sur les sections précédentes en cas de contradiction).** Ce fichier fait foi :
`CLAUDE.md` > `decisions.md` > `suivi.md` > `audit-etape0.md`.

**Références.**
- Corrigés de l'enseignant `Id_rem.pdf` (2.9, 2.10) et `tatonement.pdf` (2.11, 2.12). Ils font foi pour la rédaction (A9).
- Polycopié Javet 1MRenf (chap. 2, § 2.2 à 2.4 : la formule en 5e méthode, ex. 2.17).
- Tous dans `docs/reference/equations-2e-degre/`, jamais commités.
- Règles générales : `docs/architecture.md` (A1 à A9), `docs/guide-redaction.md` (R1 à R20), `docs/chantiers/equations-2e-degre/quiz.md`.

**Prérequis.** Les chantiers `fondations` et `briques-communes` sont fusionnés. Ils apportent :
- `moteur/expr.py`, avec **le parseur** (lecture de « membre = membre ») ;
- `moteur/chaine.py`, avec les options du corrigé : étiquette grise, « impossible » sous le facteur constant, texte au milieu de la chaîne ;
- le type de bloc « chaine », avec une **ligne pleine largeur** au milieu de la chaîne qui peut contenir un autre bloc (le tableau S-P, D4) sans casser l'alignement des ⇔ ;
- le CSS `.chaine` commun ;
- `nombres.approx` (D13) et `nombres.exact(x, decimaux_enonce=False)` (E14) ;
- `oracle.racines`.

Les parties P1 et P2 de l'audit (extraction de la chaîne et du CSS) ne font donc **pas** partie de ce chantier.

---

## 1. Principes

1. **Rien de faux à l'écran.**
   - Chaque factorisation est redéveloppée exactement (`Fraction`, et nombres de la forme p + q√m) et comparée au polynôme.
   - Chaque solution est substituée exactement dans l'équation de départ.
   - En cas d'échec : le message « ne conclut pas » (§ 4), jamais un résultat douteux.
   - L'oracle mpmath (`oracle.racines`) contrôle tout dans les tests.
2. **Python pur, sans SymPy.** Le calcul est exact, et il n'y a aucun délai de chargement.
3. **Portée explicite.** Chaque décision dit à quoi elle s'applique. Aucun outil existant n'est rebranché dans ce chantier.
4. **Principe 6.** Les élèves (1M, 1C, 2C) aiment les algorithmes et les nombres, pas les concepts : on montre les essais (tableau S-P, diviseurs testés) plutôt qu'un argument.
5. **Une résolution, plusieurs vues (A6, A9).** Le moteur produit des **étapes structurées** (§ 5). L'onglet « Résoudre » les affiche toutes, et le futur onglet « S'entraîner » les dévoilera une à une.

---

## 2. Décisions

| # | Décision | Portée |
|---|---|---|
| D0 | Les PDF de référence vont dans `docs/reference/equations-2e-degre/`, contrôlés par `git check-ignore` avant le premier commit. Ils ne sont jamais commités. | P0 |
| D1 | **Tâtonnement** (a ≠ 1, coefficients entiers) : on teste les **diviseurs entiers** de c. S'il y a une racine entière r, on l'affiche seule (2.11). Sinon, **une seule ligne** nomme les diviseurs testés, sans les calculs (décision du 05.11.2026), puis on passe **directement à la formule**, qui confirme le résultat (solutions non entières ou S = ∅). **Écart voulu au corrigé 2.12 b** (décision du 05.11.2026) : on ne cherche **pas** de solution fractionnaire. FA-09 reste valable pour l'outil Factorisation. | outil 2e degré |
| D2 | La formule (Δ) est la 5e méthode, après ME, Id. rem., S-P et tâtonnement. Une **variante « Par la formule »** est proposée quand le chemin du cours ne passe pas déjà par la formule (E12). | outil |
| D3 | **Échec du S-P** (a = 1, coefficients entiers, aucun couple) : le tableau **complet**, sans ✓, puis **deux phrases** (06.11.2026) : « Aucun couple ne convient. », qui termine l'étape du S-P, puis « On utilise la formule. », première ligne de l'étape FORMULE ; dans les cas E9, « On utilise la formule. » vient après la ligne du produit nul (06.11.2026). Règle à venir : le code de `main` écrit encore l'ancien texte (« Aucun couple ne convient : on utilise la formule. », `PHRASE_SP_ECHEC`) ; le changement est fait au chantier « S'entraîner », première partie, avec la liste des instantanés modifiés pour l'enseignant. | outil |
| D4 | Tableau S-P : un **type de bloc commun** (A4), avec constructeur dans `sortie.py`, schéma, rendu, CSS et test. | P2, P5 |
| D5 | **Étiquettes** grises, sans parenthèses, comme le corrigé : « ME », « Id. rem. A² − B² avec A = …, B = … », « produit nul ». Le S-P, le tâtonnement et la formule n'ont pas d'étiquette : une phrase les annonce. **Écart voulu à R3** (mots entiers entre parenthèses), limité à cet outil. | outil |
| D6 | « Vérification : 2AB = … ✓ » pour A² ± 2AB + B². | outil |
| D7 | **Facteur constant** : « 6 = 0 » marqué « impossible », −1 compris. **Facteur monôme kxⁿ** : il reste un seul facteur, « 3x = 0 ou x − 4 = 0 », puis « x = 0 » à la ligne suivante. Exemple : `3(x − 2)(x + 1) = 0 ⇔ 3 = 0 (impossible) ou x − 2 = 0 ou x + 1 = 0`. Le paramètre `facteur_constant=` n'a qu'une valeur (A6 : pas de profil avant un 2e utilisateur). | outil |
| D8 | x² − k, avec k non carré : Id. rem. avec B = √k (2.9 j). x² = 16 passe par x² − 16 = 0 (2.12 g). x² + k, avec k > 0 : chemin normal jusqu'à Δ < 0. | outil |
| D9 | **Δ** : rédaction d'Exp-log, conforme au polycopié. Δ est écrit une fois (R5), sur une ligne (R14). Substitution avec parenthèses : `(−5)² − 4 · 1 · (−36)`. x₁ et x₂ toujours nommés. √Δ simplifié sur sa propre ligne. Fraction réduite dans la même ligne (E11). | outil |
| D10 | Dossier `equations-2e-degre`, pour 1Ms, 1Mr, 1C et 2C. **Pas de bouton de filière.** Registre et accueil en dernière partie, après relecture à l'écran. | outil |
| D11 | **Périmètre** : équations polynomiales seulement (§ 3, E13). Bicarrées, rationnelles et racines : **chantier suivant**, après un corrigé de l'enseignant. Inéquations et formules littérales : hors chantier. | chantier |
| D12 | Pas de vérification des solutions quand la chaîne n'est faite que d'équivalences (R1, comme le corrigé). Le garde-fou exact reste interne (principe 1). | outil |
| D13 | **Nombres : R13**, appliquée par la fonction unique `nombres.approx` (briques-communes), avec la sortie d'Exp-log identique à l'octet. Détail en E14. | tous (via R13) |
| D14 | **Ordres.** Facteurs (A + B)(A − B). Au tâtonnement, (x − r) en premier. Au S-P, les facteurs dans l'ordre de la ligne ✓. Solutions dans l'ordre des facteurs dans la chaîne. S en ordre croissant. | outil |
| D15 | La brique `moteur/second_degre.py` est réutilisable. Aucun outil existant n'est rebranché dans ce chantier. | chantier |
| D16 | Ce chantier est la première pièce de N02 (brique « équations »), sans attendre N01. `docs/taches.md` est mis à jour. | doc |
| D17 | Tickets hors chantier : voir § 11. | — |
| D18 | **Ramener à « … = 0 »** : E1. | outil |
| D19 | **Phrase de choix de la méthode**, toujours écrite avant un S-P, un tâtonnement ou la formule (E4). | outil |
| D20 | **Étape intermédiaire `kx = …`** : seulement si le coefficient de x est différent de ±1 **et** si la constante n'est pas entière (2.9 h contre 2.9 d et k, 2.12 e). | outil |
| D21 | **a < 0** : on met **toujours** d'abord −1 (ou −pgcd) en évidence (2.10 e). Le S-P, le tâtonnement et la formule portent donc toujours sur a > 0 (sauf dans la variante E12). | outil |
| D22 | **Coefficients non entiers** (fractions, décimaux) : pas de multiplication par le dénominateur. L'Id. rem. reste possible (B = 1/2, 2.9 g ; B = 1/3, 2.9 h). Le S-P et le tâtonnement demandent des coefficients entiers ; sinon, la formule (Javet 2.17 e, f). | outil |
| D23 | **Inconnue** : la lettre saisie (x, t, y, z, u dans le corrigé). Une seule lettre. | outil |
| D24 | **Carré d'un binôme** : on réécrit toujours `(t + 10)² = 0 ⇔ (t + 10)(t + 10) = 0`, puis le facteur n'apparaît **qu'une fois** au produit nul (2.9 b). Un monôme (x²) n'est pas réécrit. | outil |
| D25 | **Milliers** : apostrophe dès 4 chiffres (`4’913`). Une valeur **exacte** entière la garde toujours (`1’234’567`, décision du 05.11.2026) ; une valeur **approchée** passe en notation scientifique dès 10⁶ (R13). Déjà en place dans `nombres.py` (vérifié par `briques-communes`). Pas encore appliquée par Factorisation, Limites, l'Étude complète, Exp-log (interprétation) ni le contrôle de l'ED : ce sera le chantier « nombres partout », hors de celui-ci. | tous |
| D26 | **Rappel de la méthode** : un bloc repliable, fermé au départ, en tête de chaque résolution (texte en E15). | outil |
| D27 | **Développer** seulement quand aucune structure ne s'applique, en montrant les produits, avec l'étiquette « double distribution » ou « distribution » (E2). | outil |
| D29 | **Mise en relief des valeurs trouvées** (demande de l'enseignant du 05.11.2026, pour faire ressortir les résultats) : ce que l'élève doit trouver est encadré, dans la couleur et le cadre déjà utilisés pour le résultat d'une limite dans l'outil Limites (même composant, déplacé dans `commun/` s'il est propre à cette page, A2 ; clair et sombre). Concerné : **A et B** de l'Id. rem. (« avec ⟦A = 4z, B = 9⟧ ») ; la **ligne ✓** du tableau S-P ; **r et △** du tâtonnement (« ⟦x = −4⟧ est solution », « donc ⟦△ = −7⟧ ») ; la **valeur de Δ** ; **S** (déjà encadré). Chaque encadré est insécable (jamais coupé à 390 px). La « Vérification », les calculs et les étiquettes ne sont pas encadrés. | outil |
| D28 | **Ordre des méthodes fixe**, même si a = 1 : ME, Id. rem., S-P, tâtonnement, formule (encadré de 2.12, Javet). Le S-P choisi à la place d'une Id. rem. est « juste, pas dans l'ordre » dans le quiz (QZ-05, F7). | outil, quiz |

---

## 3. Règles de rédaction (E1 à E15)

La forme impersonnelle est de règle (« on », R12). Les ⇔ sont alignés, une étape par ligne, avec l'étiquette à droite (R14 ; repli à deux colonnes sur écran étroit).

**E1. Ramener à « … = 0 ».**
1. Si le second membre est 0 : rien.
2. Si les deux membres sont développés (sommes de monômes) : on regroupe tout **du côté où le coefficient du terme de plus haut degré devient positif** (à gauche si les deux côtés conviennent ou si tout s'annule), en ordre décroissant des puissances.
   - `x² + 7x = 18 ⇔ x² + 7x − 18 = 0`
   - `4x + 32 = x² ⇔ x² − 4x − 32 = 0` (2.10 j)
   - `45u + 12 = 12u² ⇔ 12u² − 45u − 12 = 0` (2.11 j)
3. Sinon (un produit ou une puissance non développés) :
   - si une structure s'applique (Id. rem. sur une forme structurée E5, facteur commun aux deux membres E3, produit déjà nul E13), on soustrait le second membre **sans développer** : `4(x − 2)² = 1 ⇔ 4(x − 2)² − 1 = 0` (2.9 k, l ; 2.12 e) ;
   - sinon, on développe (E2).

**Mise en forme.**
- La ligne n'a pas d'étiquette.
- La phrase « On ramène d'abord l'équation à la forme … = 0 : » n'est écrite que si une phrase de choix (E4) suit directement (2.10 h, 2.11 f). Sinon (une ME ou une Id. rem. suit), la ligne ouvre la chaîne (2.9 d, 2.11 h).
- Des termes seulement dans le désordre (`5 + x² − 6x = 0`) : une ligne `⇔ x² − 6x + 5 = 0`, sans étiquette (quiz.md, réponse 1).

**E2. Développer (D27).** Quand aucune structure ne s'applique, on développe chaque membre **en montrant les produits**, car les élèves ont de la peine à développer. On applique ensuite E1.2.
- **Produit de deux parenthèses** : une ligne avec tous les produits partiels, étiquette « double distribution » ; la réduction se fait à la ligne suivante, sans étiquette.
  `(x + 1)(x + 3) = 15 ⇔ x² + 3x + x + 3 = 15` (double distribution) `⇔ x² + 4x + 3 = 15 ⇔ x² + 4x − 12 = 0`.
- **Nombre ou monôme × parenthèse** : étiquette « distribution ».
- **Carré d'un binôme** : par l'Id. rem., avec l'étiquette « Id. rem. (A − B)² avec A = 2x, B = 1 ».
- **Signe « − » devant un produit** : le produit développé s'écrit d'abord entre parenthèses, `− (4x² − 4x)`, et on enlève les parenthèses à la ligne suivante.
- Plusieurs développements sur une même ligne : les étiquettes sont séparées par « ; ».
- Dans le moteur : phase « ramener », méthode « DEVELOPPER ».

**E3. ME.**
- Facteur commun : pgcd entier des coefficients × la plus grande puissance commune de x (`3x(x − 4)`, `x(x² − 1)`). Si a < 0 : −pgcd (D21), précédé de « Le trinôme n'est pas unitaire (a = −1) : on met d'abord −1 en évidence. » (2.10 e), ou, avec un pgcd, « Le coefficient de x² est négatif (a = −6) : on met d'abord −6 en évidence. ». Exemple : `−6x² + 12x − 6 = 0 ⇔ −6(x² − 2x + 1) = 0` (ME), puis la méthode suivante sur x² − 2x + 1, jusqu'à `−6 = 0 (impossible) ou x − 1 = 0`.
- Facteur commun binôme aux deux membres (2.12 e) : phrase « Attention : on ne divise pas par (x − 1), car ce facteur peut être nul ! On ramène tout dans le membre de gauche, puis on met (x − 1) en évidence. » Elle est écrite dans l'étape « ramener » (phase `ramener`, avant la ligne `(x − 1)(2 − x) − (x − 1)(x + 3) = 0`), pas dans l'étape de la ME : le code de `main` fait foi (`_phrase_attention`, appelée par l'étape « ramener » ; quiz.md § 7, point g) (06.11.2026).
- Étiquette « ME ».
- Le facteur restant est réduit sur ses propres lignes : `(x − 1)(2 − x − x − 3) = 0 ⇔ (x − 1)(−2x − 1) = 0`.

**E4. Phrase de choix (D19).** Écrite avant le S-P, le tâtonnement ou la formule :
- sans ME : « Pas de ME, pas d'Id. rem. ; le trinôme est unitaire (a = 1) : S-P. » / « Pas de ME, pas d'Id. rem. ; a = 2 ≠ 1 : tâtonnement. » / « Pas de ME, pas d'Id. rem. ; les coefficients ne sont pas entiers : on utilise la formule. » ;
- après une ME, sur le trinôme réduit : « Le trinôme z² + 12z + 32 est unitaire : S-P. » / « Le trinôme 3x² + 8x − 3 n'est pas unitaire : tâtonnement. » (2.12 d).

Rien avant une Id. rem., ni avant une ME (sauf quand a < 0, E3).

**E5. Id. rem.**
- **Détection sur un polynôme développé** : A = kx, avec k rationnel positif et k² = a ; B rationnel avec B² = |c|, ou B = √k quand le terme en x est absent et c < 0 (D8).
  - 48z² − 216z + 243 n'est **pas** une Id. rem. avant la ME (48 n'est pas un carré).
  - x² + 6x + 4 n'en est pas une (2AB = 4x ≠ 6x).
- **Détection sur une forme structurée** : (binôme)² − m, k(binôme)² − m, m − (binôme)² (2.9 k, l ; 2.12 h).
- **A² ± 2AB + B²** : une ligne de texte avant la ligne de chaîne, « Id. rem. A² + 2AB + B² avec A = t, B = 10. Vérification : 2AB = 2 · t · 10 = 20t ✓ », puis `⇔ (t + 10)² = 0` et la réécriture D24.
- **A² − B²** : étiquette en marge, « Id. rem. A² − B² avec A = 2x, B = 3 ». Si A doit être justifié, on écrit à la place une ligne de texte avant la chaîne : « Id. rem. A² − B² avec A = 2(x − 2) et B = 1 (car A² = 4(x − 2)²). » (2.9 k).
- **Facteurs d'une forme structurée** : on les développe sur des lignes successives, `(2(x − 2) + 1)(2(x − 2) − 1) ⇔ (2x − 4 + 1)(2x − 4 − 1) ⇔ (2x − 3)(2x − 5)`. Un facteur réduit commence par le terme en x, sauf si son coefficient est négatif alors que la constante est positive : `2 − 3x` (2.12 h), mais `−2x − 1` (2.12 e).
- Pas de ME faite après coup : `(3x + 6)(2 − 3x)`, et non 3(x + 2)(2 − 3x).

**E6. S-P** (a = 1, coefficients entiers).
- « On cherche deux nombres dont le produit vaut c et la somme vaut b : », puis le tableau `produit = c | somme`.
- **Lignes** : d = 1, 2, … ≤ √|c|, seulement les diviseurs de c.
- **Signes** :
  - si c > 0, les deux nombres ont le signe de b (positifs si b = 0) ;
  - si c < 0, le plus grand en valeur absolue a le signe de b (à égalité, le négatif en premier).
- On s'arrête à la ligne ✓. Les facteurs suivent l'ordre de cette ligne : (4, −9) donne (x + 4)(x − 9).
- **Échec (D3)** : toutes les lignes, sans ✓, puis « Aucun couple ne convient. » ; « On utilise la formule. » est la première ligne de l'étape FORMULE qui suit, et, dans les cas E9, vient après la ligne du produit nul (06.11.2026 ; règle à venir : le code de `main` écrit encore l'ancien texte (`PHRASE_SP_ECHEC`) ; le changement est fait au chantier « S'entraîner », première partie, avec la liste des instantanés modifiés pour l'enseignant).

**E7. Tâtonnement** (a > 1, coefficients entiers, après ME).
- **Si une racine entière existe** : elle est unique, parce qu'après la ME le trinôme est primitif et a ≠ ±1. On écrit :
  - « x = −5 est solution, car 2 · (−5)² + 13 · (−5) + 15 = 50 − 65 + 15 = 0. » Après une ME : « x = −4 est solution de 2x² + x − 28 = 0, car … » ;
  - un terme b · r avec b = ±1 s'écrit directement (« 2 · (−4)² − 4 − 28 ») ;
  - « Donc 2x² + 13x + 15 = (x + 5)(2x + △) avec 5 · △ = 15, donc △ = 3. » (−r)·△ = c, où (−r) est écrit comme un nombre : `−12 · △ = −72`.
- **Sinon (D1)** : une seule ligne, « On teste les diviseurs de 12 (±1, ±2, ±3, ±4, ±6, ±12) : aucun n'est solution. », qui termine l'étape du tâtonnement, puis « On utilise la formule. », première ligne de l'étape FORMULE ; dans les cas E9, « On utilise la formule. » vient après la ligne du produit nul (06.11.2026 ; règle à venir : le code de `main` écrit encore l'ancien texte (les deux phrases sur une ligne, `_ecrire_tatonnement`) ; le changement est fait au chantier « S'entraîner », première partie, avec la liste des instantanés modifiés pour l'enseignant). Les diviseurs sont rangés par |d| croissant. Aucun calcul d'essai n'est écrit. L'affirmation est confirmée juste après : la formule donne des solutions non entières ou S = ∅, donc rien de non démontré ne reste à l'écran.
- On ne cherche jamais de fraction : pas de « Remarque. Pour éviter les fractions… ».

**E8. Produit nul.**
- Étiquette « produit nul » sur la ligne qui sépare les facteurs.
- Facteur constant : `6 = 0` avec « impossible » dessous (D7).
- Monôme : `3x = 0`, puis `x = 0` à la ligne suivante.
- Binôme `x − r` : il s'écrit `x − r = 0`, puis `x = r`.
- Étape intermédiaire selon D20 : `3x + 1/3 = 0` donne `3x = −1/3`, puis `x = −1/9`.
- Les solutions suivent l'ordre des facteurs (D14).

**E9. Formule sur un facteur.** Quand la formule s'applique à un trinôme facteur (après une ME de constante ou de xᵏ), le produit nul vient d'abord, `⇔ 2 = 0 (impossible) ou x² − 2x − 2 = 0`, puis les lignes de Δ, puis `⇔ x = 1 − √3 ou x = 1 + √3`.

**E10. Formule.**
```
Δ = b² − 4ac = 4² − 4 · 1 · (−1) = 16 + 4 = 20
Δ > 0 : deux solutions.    √Δ = √20 = 2√5
x₁ = (−b − √Δ)/(2a) = (−4 − 2√5)/2 = −2 − √5
x₂ = (−b + √Δ)/(2a) = (−4 + 2√5)/2 = −2 + √5
```
- Δ = 0 : « Δ = 0 : une seule solution. » puis `x = −b/(2a) = 12/8 = 3/2`.
- Δ < 0 : « Δ < 0 : l'équation n'a aucune solution réelle. » Sur un facteur : « Δ < 0 : x² + x + 1 = 0 n'a aucune solution réelle. »
- √Δ entier : « √Δ = 1 ».

**E11. Valeurs exactes.**
- Fractions réduites, signe devant.
- Radicaux simplifiés, regroupés en une seule fraction réduite : `(−5 − √17)/2`, `(4 − √22)/3`, `−2 − √5` quand le dénominateur vaut 1.
- Dans S, chaque solution est écrite séparément, en ordre croissant : `S = {−2 − √5 ; −2 + √5}`. Jamais de ±.

**E12. Variante « Par la formule »** (D2).
- On met en évidence seulement la puissance de x indispensable (pas la constante), puis la formule sur le trinôme.
- Elle n'est proposée que si le chemin du cours n'utilise pas la formule.
- C'est la seule voie où Δ = 0 apparaît avec des coefficients entiers. En effet, Δ = 0 avec un trinôme primitif force a et c à être des carrés : l'Id. rem. aboutit avant.

**E13. Ce que l'outil résout.**
- Degré 2 (et degré 1, quand x² s'annule : on isole x).
- Degré ≥ 3 quand une ME de xᵏ laisse un facteur de degré ≤ 2, ou quand une Id. rem. s'applique (2.12 c, Az 4.1 f).
- Produit déjà factorisé (Az 4.1 d) : produit nul direct, sans développer.
- Facteur commun aux deux membres (2.12 e).
- Identité ou égalité fausse : S = ℝ ou S = ∅, avec la rédaction d'Exp-log (Az 4.1 g).

**E14. Nombres (D13 = R13).**
- Valeurs exactes calculées à partir d'entiers : en fractions.
- Décimaux de l'énoncé : ils gardent leur écriture. Un résultat qui en découle et qui est un décimal fini reste décimal ; sinon, une fraction (paramètre explicite `decimaux_enonce=`, réglé par la lecture de la saisie, A7).
- **≈ seulement pour les solutions irrationnelles**, une fois, après S. Toutes les solutions sont reprises dans l'ordre : les rationnelles avec « = », les irrationnelles avec « ≈ ». On écrit x₁ et x₂ quand la formule les a nommés, sinon x. Exemples :
  - `S = {−√5 ; √5}, soit x ≈ −2,236 ou x ≈ 2,236` ;
  - `S = {−2 − √5 ; −2 + √5}, soit x₁ ≈ −4,236 et x₂ ≈ 0,236` ;
  - `S = {−√2 ; 0 ; √2}, soit x ≈ −1,414 ou x = 0 ou x ≈ 1,414`.
- 3 décimales, virgule décimale, arrondi au plus proche, la moitié vers le haut en valeur absolue, comme la calculatrice (0,0625 ≈ 0,063).
- Notation scientifique sous 10⁻³ et dès 10⁶, décidée sur la valeur **arrondie** : au plus 4 chiffres significatifs, **zéros finaux de la mantisse retirés** comme dans R13 (`3,162 × 10⁻⁵`, `1 × 10¹⁰`). Une mantisse arrondie à 10 devient `1 × 10ⁿ⁺¹`. Jamais `−0,000`. Apostrophe dès 4 chiffres (D25).

**E15. Rappel de la méthode** (bloc repliable, D26) :

> Pour factoriser, on procède dans l'ordre : ① mise en évidence (ME) ; ② identité remarquable (Id. rem.) ; ③ Somme-Produit (S-P), si le
> trinôme est unitaire (a = 1) ; ④ tâtonnement, si a ≠ 1 ; ⑤ la formule. Puis : un produit est nul si et seulement si l'un des facteurs est nul.
> A² − B² = (A + B)(A − B) · A² + 2AB + B² = (A + B)² · A² − 2AB + B² = (A − B)².
> S-P : si a = 1, x² + bx + c = (x + p)(x + q), où p · q = c et p + q = b.
> Tâtonnement : on cherche une solution entière r parmi les diviseurs de c ; alors ax² + bx + c = (x − r)(ax + △), avec (−r) · △ = c.
> Formule : Δ = b² − 4ac ; si Δ > 0, x₁,₂ = (−b ± √Δ)/(2a) ; si Δ = 0, x = −b/(2a) ; si Δ < 0, S = ∅.

---

## 4. Messages (vouvoiement, R12 ; EL-11)

| Cas | Message |
|---|---|
| Pas de « = » | « Écrivez une équation, avec le signe « = ». » |
| Plusieurs lettres | « Écrivez une équation avec une seule inconnue. » |
| Fraction avec l'inconnue au dénominateur, racine, exposant non entier | « Les équations avec une fraction ou une racine contenant l'inconnue seront traitées dans une prochaine version. » |
| Degré ≥ 3 hors E13 (bicarrée, etc.) | « Cette équation se ramène au 2e degré par un changement de variable : ce sera traité dans une prochaine version. » si c'est une bicarrée ; sinon « Cette équation ne se résout pas avec les méthodes du cours. » |
| Garde-fou en échec | « Le calcul ne permet pas de conclure avec certitude : cette équation n'est pas résolue ici. » |

---

## 5. Étapes structurées (exigence de quiz.md § 4, dès ce chantier)

`moteur/second_degre.py` expose, en Python pur :

```
resoudre_equation(gauche, droite, inconnue, decimaux_enonce=False, methodes=ORDRE_DU_COURS) -> Resolution
Resolution = {
  "statut":    "resolu" | "pas_encore" | "hors_cours" | "ne_conclut_pas",
  "etapes":    [Etape],
  "solutions": [nombre exact],          # croissant
  "S":         tex,
  "approx":    tex | None,              # ligne « soit x ≈ … » (E14)
  "variantes": ["formule"] | []         # E12
}
Etape = {
  "phase":      "ramener" | "factoriser" | "produit_nul" | "delta_valeur" | "delta_nombre" | "isoler",   # isoler : degré 1 (E13)
  "methode":    "RAMENER" | "DEVELOPPER" | "ISOLER" | "ME" | "IDREM_DIFF" | "IDREM_PLUS" | "IDREM_MOINS" | "SP" | "TATONNEMENT" | "FORMULE" | "PRODUIT_NUL",
  "cible":      tex du polynôme ou du facteur traité (pour « Et pour x² − 1 ? »),
  "parametres": dict propre à la méthode (ME : facteur ; IDREM : A, B ; SP : essais, p, q ; TATONNEMENT : essais, r, triangle ;
                FORMULE : a, b, c, delta, racine_delta, x1, x2),
  "lignes":     [objets de moteur/chaine.py et blocs tableau_essais]   # phrase de choix et textes intermédiaires compris
}
s_applique(methode, polynome) -> bool      # mêmes règles de détection que le chemin du cours (E5, E6, E7, D21, D22)
appliquer(methode, polynome) -> Etape | None
```

**Règles.**
- L'adaptateur `resoudre_eq.py` construit la page **uniquement** à partir des `etapes`. **La concaténation des `lignes` de toutes les étapes est la chaîne affichée** (testé).
- Une ligne seulement réordonnée (E1) appartient à l'étape qui suit.
- Les champs `question`, `boutons`, `acceptees`, `refusees` et les explications appartiennent au chantier « S'entraîner ». Ils ne sont pas écrits ici, mais `s_applique` et `appliquer` existent déjà pour eux, et ils sont testés.

---

## 6. Tests

- **Oracle.** Pour chaque équation du corpus (§ 8) et des propriétés sur des polynômes générés : solutions = `oracle.racines`, et aucune autre. `oracle.racines` prend les coefficients du plus haut degré au terme constant (int, Fraction, Decimal, str ; float refusé) et refuse le polynôme nul : l'identité et l'égalité fausse (S = ℝ, S = ∅) se testent à part.
- **Garde-fou.** Chaque factorisation affichée est redéveloppée exactement ; chaque solution est substituée exactement.
- **Méthodes.** Pour chaque méthode et chaque polynôme du corpus : `s_applique` vrai ⇒ `appliquer` rend une factorisation qui se redéveloppe exactement ; `s_applique` faux ⇒ `None`.
- **Invariant des étapes.** La concaténation des `lignes` donne le rendu de « Résoudre » (identique à l'octet).
- **Rédaction.** Instantanés du corpus ; R12 (vouvoiement) ; vocabulaire ; E14 (R13, ≈, apostrophe).
- **Cas limites.**
  - `x² + 1000x − 1 = 0` (mantisse 10,000 dans E14) ;
  - `3t² + 5t + 12 = 0` (12 diviseurs, une seule ligne) ;
  - `−6x² + 12x − 6 = 0` (ME de −6, Id. rem., D24, « −6 = 0 impossible ») ;
  - décimaux de l'énoncé (`0,5x² − 2 = 0`) ;
  - `x² + 4 = 0` (S-P avec b = 0 : tableau puis Δ < 0).
- **Pages.** `test_largeurs` de 320 à 1100 px (`CONNUS` vide), y compris le tableau S-P et une étiquette longue d'Id. rem.

---

## 7. Exemples rédigés

À l'écran, S est encadré. Les étiquettes sont en gris à droite.

**ME seule**
```
3x² − 12x = 0  ⇔  3x(x − 4) = 0                         ME
               ⇔  3x = 0  ou  x − 4 = 0                 produit nul
               ⇔  x = 0  ou  x = 4
S = {0 ; 4}
```

**Id. rem. (carré), après une ME**
```
12x² − 12x + 3 = 0  ⇔  3(4x² − 4x + 1) = 0              ME
Id. rem. A² − 2AB + B² avec A = 2x, B = 1.    Vérification : 2AB = 2 · 2x · 1 = 4x ✓
                    ⇔  3(2x − 1)² = 0
                    ⇔  3(2x − 1)(2x − 1) = 0
                    ⇔  3 = 0 (impossible)  ou  2x − 1 = 0      produit nul
                    ⇔  x = 1/2
S = {1/2}
```

**Id. rem. A² − B² (B = √k, étape intermédiaire, ≈)**
```
25x² = 3  ⇔  25x² − 3 = 0
          ⇔  (5x + √3)(5x − √3) = 0                     Id. rem. A² − B² avec A = 5x, B = √3
          ⇔  5x + √3 = 0  ou  5x − √3 = 0               produit nul
          ⇔  5x = −√3  ou  5x = √3
          ⇔  x = −√3/5  ou  x = √3/5
S = {−√3/5 ; √3/5},  soit x ≈ −0,346 ou x ≈ 0,346
```

**S-P**
```
On ramène d'abord l'équation à la forme … = 0 :
x² = x + 42  ⇔  x² − x − 42 = 0
Pas de ME, pas d'Id. rem. ; le trinôme est unitaire (a = 1) : S-P.
On cherche deux nombres dont le produit vaut −42 et la somme vaut −1 :
      produit = −42 | somme
       1     −42    |  −41
       2     −21    |  −19
       3     −14    |  −11
       6      −7    |   −1 ✓
             ⇔  (x + 6)(x − 7) = 0
             ⇔  x + 6 = 0  ou  x − 7 = 0                produit nul
             ⇔  x = −6  ou  x = 7
S = {−6 ; 7}
```

**Tâtonnement, racine entière**
```
On ramène d'abord l'équation à la forme … = 0 :
3x² + 10x = 8  ⇔  3x² + 10x − 8 = 0
Pas de ME, pas d'Id. rem. ; a = 3 ≠ 1 : tâtonnement.
x = −4 est solution, car 3 · (−4)² + 10 · (−4) − 8 = 48 − 40 − 8 = 0.
Donc 3x² + 10x − 8 = (x + 4)(3x + △)   avec 4 · △ = −8, donc △ = −2.
               ⇔  (x + 4)(3x − 2) = 0
               ⇔  x + 4 = 0  ou  3x − 2 = 0             produit nul
               ⇔  x = −4  ou  x = 2/3
S = {−4 ; 2/3}
```

**Tâtonnement en échec, puis formule (Δ > 0, carré parfait) : 2.12 b, écart voulu (D1)**
```
Pas de ME, pas d'Id. rem. ; a = 6 ≠ 1 : tâtonnement.
On teste les diviseurs de 1 (±1) : aucun n'est solution. On utilise la formule.
Δ = b² − 4ac = 5² − 4 · 6 · 1 = 25 − 24 = 1
Δ > 0 : deux solutions.    √Δ = 1
x₁ = (−b − √Δ)/(2a) = (−5 − 1)/12 = −1/2
x₂ = (−b + √Δ)/(2a) = (−5 + 1)/12 = −1/3
S = {−1/2 ; −1/3}
```

**S-P en échec, puis formule (Δ > 0, irrationnel)**
```
Pas de ME, pas d'Id. rem. ; le trinôme est unitaire (a = 1) : S-P.
On cherche deux nombres dont le produit vaut −1 et la somme vaut 4 :
      produit = −1 | somme
      −1     1     |   0
Aucun couple ne convient : on utilise la formule.
Δ = b² − 4ac = 4² − 4 · 1 · (−1) = 16 + 4 = 20
Δ > 0 : deux solutions.    √Δ = √20 = 2√5
x₁ = (−b − √Δ)/(2a) = (−4 − 2√5)/2 = −2 − √5
x₂ = (−b + √Δ)/(2a) = (−4 + 2√5)/2 = −2 + √5
S = {−2 − √5 ; −2 + √5},  soit x₁ ≈ −4,236 et x₂ ≈ 0,236
```

**Formule sur un facteur, après une ME (Javet 2.17 c)**
```
2x² − 4x − 4 = 0  ⇔  2(x² − 2x − 2) = 0                ME
Le trinôme x² − 2x − 2 est unitaire : S-P.
On cherche deux nombres dont le produit vaut −2 et la somme vaut −2 :
      produit = −2 | somme
       1     −2    |  −1
Aucun couple ne convient : on utilise la formule.
                  ⇔  2 = 0 (impossible)  ou  x² − 2x − 2 = 0      produit nul
Δ = b² − 4ac = (−2)² − 4 · 1 · (−2) = 4 + 8 = 12
Δ > 0 : deux solutions.    √Δ = √12 = 2√3
x₁ = (−b − √Δ)/(2a) = (2 − 2√3)/2 = 1 − √3
x₂ = (−b + √Δ)/(2a) = (2 + 2√3)/2 = 1 + √3
                  ⇔  x = 1 − √3  ou  x = 1 + √3
S = {1 − √3 ; 1 + √3},  soit x₁ ≈ −0,732 et x₂ ≈ 2,732
```

**Δ = 0 (variante « Par la formule » de 4x² − 12x + 9 = 0)**
```
Δ = b² − 4ac = (−12)² − 4 · 4 · 9 = 144 − 144 = 0
Δ = 0 : une seule solution.
x = −b/(2a) = 12/8 = 3/2
S = {3/2}
```

**Développer (double distribution), puis S-P**
```
On ramène d'abord l'équation à la forme … = 0 :
(x + 1)(x + 3) = 15  ⇔  x² + 3x + x + 3 = 15             double distribution
                     ⇔  x² + 4x + 3 = 15
                     ⇔  x² + 4x − 12 = 0
Pas de ME, pas d'Id. rem. ; le trinôme est unitaire (a = 1) : S-P.
On cherche deux nombres dont le produit vaut −12 et la somme vaut 4 :
      produit = −12 | somme
      −1     12     |  11
      −2      6     |   4 ✓
                     ⇔  (x − 2)(x + 6) = 0
                     ⇔  x − 2 = 0  ou  x + 6 = 0          produit nul
                     ⇔  x = 2  ou  x = −6
S = {−6 ; 2}
```

**Développer, puis identité (Az 4.1 g)**
```
(2x − 1)² − 4x(x − 1) = 1  ⇔  4x² − 4x + 1 − (4x² − 4x) = 1      Id. rem. (A − B)² avec A = 2x, B = 1 ; distribution
                           ⇔  4x² − 4x + 1 − 4x² + 4x = 1
                           ⇔  1 = 1
L'égalité est vraie pour tout réel x.
S = ℝ
```

**Tâtonnement en échec, puis Δ < 0**
```
Pas de ME, pas d'Id. rem. ; a = 2 ≠ 1 : tâtonnement.
On teste les diviseurs de 3 (±1, ±3) : aucun n'est solution. On utilise la formule.
Δ = b² − 4ac = 1² − 4 · 2 · 3 = 1 − 24 = −23
Δ < 0 : l'équation n'a aucune solution réelle.
S = ∅
```

### Exemple cible : 2.11 h (texte rendu à fournir en fin de session)
```
4x² + 2x = 56  ⇔  4x² + 2x − 56 = 0
               ⇔  2(2x² + x − 28) = 0                    ME
Le trinôme 2x² + x − 28 n'est pas unitaire : tâtonnement.
x = −4 est solution de 2x² + x − 28 = 0, car 2 · (−4)² − 4 − 28 = 32 − 4 − 28 = 0.
Donc 2x² + x − 28 = (x + 4)(2x + △)   avec 4 · △ = −28, donc △ = −7.
               ⇔  2(x + 4)(2x − 7) = 0
               ⇔  2 = 0 (impossible)  ou  x + 4 = 0  ou  2x − 7 = 0    produit nul
               ⇔  x = −4  ou  x = 7/2
S = {−4 ; 7/2}
```
Étapes : ramener · factoriser (ME, cible 4x² + 2x − 56) · factoriser (TATONNEMENT, cible 2x² + x − 28, r = −4, △ = −7) · produit_nul.

---

## 8. Résultats attendus (corpus ; valeurs contrôlées par l'oracle de l'audit)

| Exercice | Chemin | S |
|---|---|---|
| 2.9 a 6x² − 6 = 0 | ME 6 · A² − B² (A = x, B = 1) | {−1 ; 1} |
| 2.9 b t² + 20t + 100 = 0 | A² + 2AB + B² (A = t, B = 10) · D24 | {−10} |
| 2.9 c 48z² − 216z + 243 = 0 | ME 3 · A² − 2AB + B² (A = 4z, B = 9) | {9/4} |
| 2.9 d 4x² = 9 | ramener · A² − B² (2x, 3) | {−3/2 ; 3/2} |
| 2.9 e 8x² − 112x + 392 = 0 | ME 8 · A² − 2AB + B² (x, 7) | {7} |
| 2.9 f 196z² + 280z = −100 | ramener · ME 4 · A² + 2AB + B² (7z, 5) | {−5/7} |
| 2.9 g t² + t + 1/4 = 0 | A² + 2AB + B² (t, 1/2) | {−1/2} |
| 2.9 h 9x² − 1/9 = 0 | A² − B² (3x, 1/3) · D20 | {−1/9 ; 1/9} |
| 2.9 i 18z² + 72z + 72 = 0 | ME 18 · A² + 2AB + B² (z, 2) | {−2} |
| 2.9 j x² − 5 = 0 | A² − B² (x, √5) | {−√5 ; √5}, ≈ −2,236 et 2,236 |
| 2.9 k 4(x − 2)² = 1 | ramener sans développer · A² − B² (2(x − 2), 1, « car ») | {3/2 ; 5/2} |
| 2.9 l (x + 1)² = 16 | ramener sans développer · A² − B² (x + 1, 4) | {−5 ; 3} |
| 2.10 a x² − 5x − 36 = 0 | S-P (4 lignes) | {−4 ; 9} |
| 2.10 b x² + 3x − 18 = 0 | S-P (3 lignes) | {−6 ; 3} |
| 2.10 c 2z² + 24z + 64 = 0 | ME 2 · S-P | {−8 ; −4} |
| 2.10 d x² + 7x + 6 = 0 | S-P (1 ligne) | {−6 ; −1} |
| 2.10 e −y² + 10y − 9 = 0 | ME −1 · S-P | {1 ; 9} |
| 2.10 f t² + 11t + 30 = 0 | S-P | {−6 ; −5} |
| 2.10 g x² − 11x + 10 = 0 | S-P | {1 ; 10} |
| 2.10 h x² + 7x = 18 | ramener (phrase) · S-P | {−9 ; 2} |
| 2.10 i x² + 18x + 45 = 0 | S-P | {−15 ; −3} |
| 2.10 j 4x + 32 = x² | ramener (à droite) · S-P | {−4 ; 8} |
| 2.11 a 2x² + 13x + 15 = 0 | tâtonnement r = −5, △ = 3 | {−5 ; −3/2} |
| 2.11 b 9x² + 8x − 1 = 0 | r = −1, △ = −1 | {−1 ; 1/9} |
| 2.11 c 5y² − 54y − 72 = 0 | r = 12, △ = 6 | {−6/5 ; 12} |
| 2.11 d 2x² − x − 28 = 0 | r = 4, △ = 7 | {−7/2 ; 4} |
| 2.11 e 3x² + 2x − 1 = 0 | r = −1, △ = −1 | {−1 ; 1/3} |
| 2.11 f 4t² + 7t = 2 | ramener (phrase) · r = −2, △ = −1 | {−2 ; 1/4} |
| 2.11 g 17x² + 288x − 17 = 0 | r = −17, △ = −1 | {−17 ; 1/17} |
| 2.11 h 4x² + 2x = 56 | ramener · ME 2 · r = −4, △ = −7 | {−4 ; 7/2} |
| 2.11 i 3x² − 8x − 35 = 0 | r = 5, △ = 7 | {−7/3 ; 5} |
| 2.11 j 45u + 12 = 12u² | ramener (à droite) · ME 3 · r = 4, △ = 1 | {−1/4 ; 4} |
| 2.12 a x² − 8x + 12 = 0 | S-P | {2 ; 6} |
| 2.12 b 6x² + 5x + 1 = 0 | tâtonnement en échec (±1) · formule, Δ = 1 (**écart D1**) | {−1/2 ; −1/3} |
| 2.12 c x³ − x = 0 | ME x · A² − B² | {−1 ; 0 ; 1} |
| 2.12 d 6x² + 16x − 6 = 0 | ME 2 · r = −3, △ = −1 | {−3 ; 1/3} |
| 2.12 e (x − 1)(2 − x) = (x − 1)(x + 3) | avertissement · ramener sans développer · ME (x − 1) | {−1/2 ; 1} |
| 2.12 f t² + 8t − 48 = 0 | S-P | {−12 ; 4} |
| 2.12 g x² = 16 | ramener · A² − B² (x, 4) | {−4 ; 4} |
| 2.12 h 16 − (3x + 2)² = 0 | A² − B² (4, 3x + 2), facteurs (3x + 6)(2 − 3x) | {−2 ; 2/3} |
| Javet 2.17 a x² + 5x + 2 = 0 | S-P en échec · Δ = 17 | {(−5 − √17)/2 ; (−5 + √17)/2}, ≈ −4,562 et −0,438 |
| Javet 2.17 b x² + 4x + 2 = 0 | S-P en échec · Δ = 8 | {−2 − √2 ; −2 + √2}, ≈ −3,414 et −0,586 |
| Javet 2.17 c 2x² − 4x − 4 = 0 | ME 2 · S-P en échec · E9 · Δ = 12 | {1 − √3 ; 1 + √3} |
| Javet 2.17 d 3t² + 5t + 12 = 0 | tâtonnement en échec (12 diviseurs) · Δ = −119 | ∅ |
| Javet 2.17 e (3/2)x² − 4x − 1 = 0 | coefficients non entiers · Δ = 22 | {(4 − √22)/3 ; (4 + √22)/3}, ≈ −0,230 et 2,897 |
| Javet 2.17 f (5/4)s² + 3s + 1 = 0 | coefficients non entiers · Δ = 4 | {−2 ; −2/5} |
| Az 4.1 c x² + 7x + 12 = 0 | S-P | {−4 ; −3} |
| Az 4.1 d (x − 1)(2 − x)(5 − 3x) = 0 | produit nul direct | {1 ; 5/3 ; 2} |
| Az 4.1 e 3x² + 4 = 0 | tâtonnement en échec · Δ < 0 | ∅ |
| Az 4.1 f x³ + 8x² = 0 | ME x² | {−8 ; 0} |
| Az 4.1 g (2x − 1)² − 4x(x − 1) = 1 | développer (Id. rem. ; distribution) · identité | ℝ |
| (x + 1)(x + 3) = 15 | développer (double distribution) · ramener · S-P | {−6 ; 2} |

Les exemples de la page (`index.html`) sont les exercices 2.9 à 2.12 (quiz.md, réponse 3). Ils sont fixés dès P5, car ce sont des entrées d'instantanés.

---

## 9. Conséquences pour quiz.md (à reporter au chantier « S'entraîner »)

- **F9** (6x² + 5x + 1) : le chemin devient tâtonnement en échec, puis formule (D1). Le piège reste « S-P » (a ≠ 1).
- **QZ-07** : « Aucun diviseur de −1 (ni fraction ±p/q) n'annule le trinôme » devient, pour 4x² − 9, « Avant le tâtonnement, regardez les identités remarquables : 4x² et 9 sont des carrés. » (règle d de quiz.md, QZ-07 ; en F9, 6x² + 5x + 1, le tâtonnement en échec est la bonne réponse, QZ-05 : aucun refus).
- **QZ-03, exemple 2.9 a** : la ligne du produit nul porte l'étiquette « produit nul » (D5).
- **QZ-05** : « le tâtonnement s'applique » signifie « une racine entière existe ».

## 10. Découpage

Une branche `equations-2e-degre` partant de `main` à jour. Un sous-agent et un commit par partie, et la suite complète verte avant chaque
commit. Les parties s'enchaînent dans l'ordre : chacune dépend de la précédente. Les parties P1 et P2 de l'audit sont faites par
`briques-communes`. La numérotation ci-dessous est celle de ce chantier.

| Partie | Contenu | Tests | Dépend de |
|---|---|---|---|
| P0 | Contrôle des prérequis (`main` contient `fondations` et `briques-communes` : `moteur/chaine.py`, `moteur/expr.py` avec le parseur, le type de bloc « chaine » avec ligne pleine largeur, `nombres.approx`, `nombres.exact`, `oracle.racines`, `.chaine` dans `commun/composants.css` ; sinon **arrêt de toute la session**). PDF déplacés et `git check-ignore` (D0). `suivi.md` (court, avec « Reprise après compactage ») et `journal.md`. Référence des tests (`complet --rapport` puis `reference`), commitée. | — | — |
| P1 | **Calcul** (`moteur/second_degre.py`, sans texte) : polynômes exacts (`Fraction`) ; nombres (p + q√m)/d exacts ; ME (pgcd, xᵏ, −pgcd), Id. rem. (E5, polynôme développé), S-P (E6, essais et signes), tâtonnement (E7, racine entière unique), formule (Δ, √Δ simplifié), produit nul ; `s_applique` et `appliquer` ; garde-fou exact. | Oracle sur le corpus § 8 (degré 2 développé) et sur des polynômes générés ; `s_applique` ⇒ `appliquer` se redéveloppe ; garde-fou ; temps natif | P0 |
| P2 | **Rédaction** : étapes structurées (§ 5) et `lignes` en objets de `chaine.py`, rendues par `chaine.bloc_chaine(c, etiquette_grise=True, impossible=True, membre_gauche=True)` (4 colonnes, comme le corrigé) ; E3 à E12, E14 (R13 par `nombres.approx` et `nombres.exact`, ≈, apostrophe), D20, D24, D29 (mise en relief) ; type de bloc commun `tableau_essais` (A4 : `sortie.py`, `valider`, `rendu.js`, CSS, test), ajouté à `BLOCS_DANS_CHAINE`, placé dans une ligne pleine largeur de la chaîne. | Instantanés du texte (2.9 à 2.12 développés, Javet 2.17) ; invariant « concaténation des lignes » ; R12, vocabulaire ; cas limites § 6 | P1 |
| P3 | **Saisie** : « membre = membre » lu par `expr.lire_membres` avec un `Lexique` propre à l'outil (aucune fonction : ni e, ni log, ni ln ; une seule lettre), inconnue (D23), `decimaux_enonce` (R13), E1 (cas 1 et 2 ; cas 3 par développement seulement, les structures venant en P4), E2 (développer, D27), messages § 4. | Erreurs de saisie, notation suisse, décimaux de l'énoncé, (x + 1)(x + 3) = 15, Az 4.1 g | P2 |
| P4 | **Formes structurées et degrés ≠ 2** : Id. rem. structurée (2.9 k, l ; 2.12 h), facteur commun aux deux membres avec l'avertissement (2.12 e), produit déjà factorisé (Az 4.1 d), ME de xᵏ en degré ≥ 3 (2.12 c, Az 4.1 f), E9, degré 1, identité et égalité fausse. | Oracle et instantanés sur ces cas ; le reste du corpus § 8 | P3 |
| P5 | **Outil** `equations-2e-degre/` : `equations.py`, `resoudre_eq.py`, `index.html` (`monterOutil`, exemples = 2.9 à 2.12, clavier commun, variante « Par la formule » E12, rappel repliable D26, avec un type de bloc s'il n'en existe pas, A4) ; manifeste ; nouvelles arêtes d'import déclarées (A1) ; données de test de l'outil (A3). **Pas de registre.** | Instantanés `resoudre`, références de pages, `test_largeurs` de 320 à 1100 px (`CONNUS` vide), `json_strict`, source unique | P4 |
| P6 | **Après la relecture de l'enseignant** (pas de nuit) : corrections, puis registre et carte de l'accueil, compteur de `tests/pages/test_accueil.py`. | `test_accueil` | P5 et relecture |

**À relire par l'enseignant après la nuit** :
- le texte rendu de 2.11 h (exemple cible) ;
- des captures à 390 px de 2.11 h, 2.10 a (tableau S-P), Javet 2.17 c (formule sur un facteur), 2.12 e (avertissement) et (x + 1)(x + 3) = 15 (double distribution) ;
- les instantanés du corpus ;
- **à juger à l'écran (⏸)** : la ligne du tâtonnement en échec (E7, « On teste les diviseurs de 3 (±1, ±3) : aucun n'est solution. On utilise la formule. », sur 2.12 b et Javet 2.17 d) : l'élève comprend-il pourquoi on passe à la formule sans avoir vu les essais ? Sinon, revenir aux lignes d'essai de 2.12 b.

## 11. Tickets hors chantier (D17)

- (a) Δ « (−−6) » d'Exp-log : à vérifier, peut-être corrigé par les correctifs « doubles signes ».
- (b) `lancer.py::fichiers_modifies` ignore les noms avec espaces ou accents.
- (c) `docs/methode-chantiers.md` : réglé s'il est commité.
- (d) « R1–R12 » (README) et « R1–R19 » (CLAUDE.md) contre R20.
- (e) Apostrophe dès 4 chiffres dans `nombres.py` (D25, probablement déjà faite pour l'Étude complète, Q28) : `briques-communes` la vérifie et liste les instantanés d'autres outils qui changeraient.

## 12. Questions pour l'enseignant

- ~~Q-A~~ Réglée le 05.11.2026 : une seule ME de −pgcd (E3).
- ~~Q-B~~ Réglée le 05.11.2026 : développer en montrant les produits, avec l'étiquette « double distribution » (E2, D27).
- ~~Q-C~~ Réglée le 05.11.2026 : une seule ligne avec les diviseurs (D1, E7).

---

## 13. Compléments du 05.11.2026 au soir (après le plan d'exécution) — priment sur les sections précédentes

Numérotation : les réponses Q1 à Q13 et les écarts (a) 1 à 19 renvoient au plan d'exécution recopié en tête de `journal.md`.

### 13.1 Découpage (remplace le § 10 pour la numérotation)

P0 · P1 · **P2a** (affichage commun : `tableau_essais`, encadré D29, options de `chaine.py`) · **P2b** (rédaction dans `second_degre`)
· P3 · **P4a** (formes structurées, sur l'arbre) · **P4b** (degré ≥ 3, E9, degré 1, identité, bicarrée, reste du corpus) · P5 · P6 (après relecture).
**Invariant de toute la nuit : `dump_sorties.py` des outils existants identique à l'octet après chaque partie** (P5 n'ajoute que le nouvel outil).

### 13.2 Architecture et réutilisation

- **Q1, registre** : option A. En P5, entrée du registre avec `"filieres": {}` (aucune carte à l'accueil), butée de `test_accueil` (16, 7) → (16, 8).
  Les filières et la carte viennent en P6. Le « pas de registre » du § 10 est remplacé par ceci.
- **Q2, A2** : **déplacer**, pas réécrire.
  - `exp_log_m._pq` (avec `_const`, `_padd`, `_pnet`, `_Hors`) → `moteur/polynomes.py`, réexporté sous les mêmes noms (même objet `_Hors`) ; manifeste d'EL + 1 fichier.
  - `exp_log._a_des_decimaux` → `moteur/expr.py`, réexporté.
  - `squarefree` et `racine_q` ajoutés à la façade `noyau`. `Nombre` (p + q√m) s'appuie dessus : pas de 5e simplification de k√m/d.
  - Garantie : dump d'Exp-log identique à l'octet. Les 4 copies existantes de la simplification deviennent une dette nommée au § 5 d'`architecture.md` (chantier « nombres partout »).
  - Les fonctions de Factorisation à borne silencieuse (`somme_produit`, `racine_entiere`, BORNE = 3000) ne sont **pas** réutilisées. Ticket au § 11 (f).
- **Q7, SymPy** : rien à changer dans ce chantier. Ticket au § 11 (g).
- **Q11, oracle** : oui, corriger `oracle.racines` en tête de P1 (retirer d'abord les racines nulles, test `[7, -19, 0]`).
- **Q12** :
  - le découpage du § 13.1 ;
  - P3 : E1 et E2 dans `second_degre` ; `Lexique`, messages et analyse de la saisie dans `equations-2e-degre/equations.py` dès P3 ;
  - des instantanés **dès P2b** : le chef d'orchestre choisit la façon la plus simple (JSON rangé hors d'`instantanes/` jusqu'en P5, ou adaptation minimale de `dump_sorties.py`), sans changer le dump des outils existants ;
  - `rapide` au-delà de 5 min, en arrière-plan : accepté.

### 13.3 Affichage

- **Q3, D29** :
  - forme : `\fbox{$…$}` dans le TeX, plus une règle dans `commun/composants.css` (bordure `--good`, fond `--ok-soft`), clair et sombre par les variables, insécable, sans HTML (A4) ;
  - A et B sont encadrés aussi dans l'étiquette grise ; pour Δ, on encadre « Δ = 20 » en entier ;
  - **S** : dans `sortie.resultat` (`.rbox`, le cadre vert de Limites que l'enseignant a montré), dans une carte **normale**, pour éviter un double cadre.
- **Q4, chaîne** :
  - les lignes de Δ, x₁, x₂, « Δ < 0 : … » et la phrase de l'identité sont des **rangées** (`bloc_rangees`) : l'invariant du § 5 porte sur les rangées, en JSON ;
  - comme dans le corrigé (2.10 a), la phrase de choix et le tableau viennent d'abord, puis la chaîne, qui commence par l'équation en membre de gauche ;
  - quand aucun ⇔ ne suit (2.12 b, Javet 2.17 d, Δ = 0), l'équation n'est pas répétée, puisque l'énoncé est affiché en tête.
- **(a) 11** : 2 colonnes à 390 px, avec le membre de gauche seul au-dessus (forme de B3) : accepté, à juger à la relecture.
- **Q5, rappel D26** : `<details class="card">` statique dans la page, comme sur les autres outils. Pas de type de bloc.
- **Q6, exemples** : 10 boutons. Le corpus complet va dans les tests.
  - 2.9 a, 2.9 b, 2.9 j ;
  - 2.10 a, 2.10 e ;
  - 2.11 h ;
  - 2.12 b, 2.12 c, 2.12 e ;
  - Javet 2.17 c.
- **Q13, clavier** : le clavier commun, dont la dernière rangée devient `0 , x =` (`^` et `√` gardés ailleurs).
- **Produit nul à 3 facteurs à 390 px** : nouvelle option de `tex_element`, désactivée par défaut, qui permet une coupure après « ou » (Exp-log inchangé).

### 13.4 Rédaction

- **D9 et E10** : la rédaction de Δ est celle du § 7 (nouvelle, comme Javet), pas celle d'Exp-log. Le § 7 fait foi.
- **Identité (E13)** : la phrase d'Exp-log, « Cette égalité est vraie pour tout nombre réel. » (réutilisée, et non celle du § 7).
- **B irrationnel ou fractionnaire** : B est écrit sous sa forme simplifiée : x² − 8 → B = 2√2 ; x² − 1/2 → B = √2/2.
- **ME avec des coefficients non entiers** : aucune. Id. rem. si elle se lit, sinon la formule (D22).
- **3x² = 0** : `3x² = 0 ⇔ x = 0` (un seul facteur monôme, D7).
- **x⁴ − 16** : Id. rem. avec A = x², B = 4 (E13), puis le facteur x² + 4 par la formule sur un facteur (E9 : « Δ < 0 : x² + 4 = 0 n'a aucune solution réelle ») et x² − 4 par l'Id. rem.
  Le message « bicarrée » ne s'affiche que si ni ME ni Id. rem. ne s'applique (x⁴ − 5x² + 4).
- **Variante E12 avec a < 0** : x₁ et x₂ sont nommés selon la formule (x₁ avec −√Δ), et S reste croissant.
- **Degré 1** : on ramène à « … = 0 » (E1), puis on isole x en une ou deux lignes (D20).
- **`s_applique`** = « la méthode aboutit » :
  - S-P : un couple existe ;
  - tâtonnement : une racine entière existe ;
  - Id. rem. et ME : la factorisation existe ;
  - formule : elle s'applique toujours. Le test « se redéveloppe » vaut pour Δ ≥ 0 ; pour Δ < 0, on contrôle S = ∅ avec l'oracle.

### 13.5 Bornes et messages (complète le § 4)

**Bornes.**
- Degré maximal après développement : 8, comme EL-M.
- Coefficients de plus de 9 chiffres (numérateur ou dénominateur) : message « Cette équation dépasse ce que l'outil sait traiter. »
- Tableau S-P de plus de 12 lignes : pas de tableau. On écrit « Le trinôme est unitaire, mais il y a trop de couples à tester. » puis l'étape FORMULE (06.11.2026 ; règle à venir : le code de `main` écrit encore l'ancien texte (« … : on utilise la formule. », `PHRASE_SP_TROP`) ; le changement est fait au chantier « S'entraîner », première partie, avec la liste des instantanés modifiés pour l'enseignant).
- La ligne des diviseurs du tâtonnement n'a pas de borne : elle passe à la ligne.

**Messages, dans cet ordre de priorité :**

| Cas | Message |
|---|---|
| Saisie vide | « Écrivez une équation. » |
| Erreur de syntaxe | Message du lexique ; `message_exposant` propre à l'outil, avec l'exemple `x^2` |
| Pas de « = » | Message du § 4 |
| Aucune lettre (2 = 2) | « Écrivez une équation avec une inconnue. » |
| Plusieurs lettres | « Écrivez une équation avec une seule inconnue. » |
| Inconnue en exposant (2^x) | « L'inconnue est en exposant : utilisez l'outil « Exponentielles et logarithmes ». » |
| Inconnue sous une racine ou au dénominateur, exposant non entier ou négatif | Message « prochaine version » du § 4 |
| Racine sans l'inconnue | « Écrivez une équation dont les coefficients n'ont pas de racine. » |
| Division par 0 | « Division par 0 : vérifiez la saisie. » |
| Bornes dépassées | Message des bornes ci-dessus |
| Degré ≥ 3 hors E13 | Message « bicarrée » ou « hors du cours » du § 4 |
| Garde-fou en échec | Message « ne conclut pas » du § 4 |

### 13.6 Écarts du plan, réglés

- (a) 2 et 18 : les PDF sont déjà rangés ; le ticket § 11 (b) est déjà réglé.
- (a) 4 : P5 écrit aussi tout ce que la liste de P5 du plan relève, et complète `architecture.md` § 4 avec les oublis.
- (a) 7 : `appliquer` relève de P2b (calcul de P1 + rédaction). Les noms de quiz.md (`resoudre_polynome`, « P3 ») sont à corriger dans le chantier du quiz (§ 9).
- (a) 13 : l'état « Chargement… » tant que SymPy n'est pas prêt est accepté pour ce chantier (Q7).
- (a) 19 : P0 refait la référence des tests, comme le plan le prévoit.

### 13.7 Tickets ajoutés au § 11

- (f) **Factorisation, borne silencieuse** : `somme_produit(-1, -4032)` rend None alors que x² − x − 4032 = (x − 64)(x + 63). Vérifier ce que l'outil Factorisation **affiche** dans ce cas : s'il affirme « ne se factorise pas », c'est un résultat faux à l'écran, donc prioritaire.
- (g) SymPy chargé pour un outil en Python pur : option de `monterOutil` (valeur par défaut inchangée), dans un chantier à part.
