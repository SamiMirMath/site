# Onglet « S'entraîner » de l'outil Équations du 2e degré : spécification

**Statut (mis à jour le 06.11.2026) : accepté sur le principe** ; l'onglet sera un chantier séparé (§ 6). Le chantier `equations-2e-degre`,
fusionné sur `main` avec ses corrections R1 à R4 et P6, fournit déjà les étapes structurées du § 4.
Dates : proposé le 04.11.2026 ; accepté sur le principe le 05.11.2026 ; mis à jour le 06.11.2026 (décisions du jour, alignement sur
`decisions.md` et sur le code de `main`) ; points a à h réglés le 06.11.2026 (après-midi) ; spécification complète le 06.11.2026
(fin d'après-midi) ; § 8 (tirage et examens, moteur sur serveur) ajouté le 06.11.2026 (soir).

Décisions de l'enseignant :
- 04.11.2026 : un onglet dans l'outil du 2e degré ; un quiz « évolutif » qui fait construire la résolution étape par étape ; QZ-05 (méthode
  juste mais pas dans l'ordre), QZ-06 (deux essais) et « niveau 2 plus tard » (QZ-14) acceptées.
- 06.11.2026 : une tentative en échec du chemin du cours est une bonne réponse (QZ-05, option a) ; familles F15 et F16 (§ 3). L'après-midi :
  « attendue » est toujours ce que le chemin du cours écrit ensuite ; points a à h du § 7 réglés ; trois choix validés (« Produit nul » dans
  la phase `ramener`, remarque sans « aussi », « ramenez d'abord tout à gauche » pour F16). En fin d'après-midi : point i (étapes sans
  question), règle d généralisée en algorithme du moteur, « Développer » devant un produit nul accepté, phrase du tâtonnement à
  coefficients non entiers, « Aucun couple ne convient. » et « On utilise la formule. » en deux phrases (D3, E6, E7, § 13.5 de
  `decisions.md` mis à jour), E3 corrigé (le code fait foi), Javet 2.17 c dans la liste fixe et famille F17 (§ 7, tout réglé).

Références. `decisions.md` fait foi (§§ 1 à 13, le § 13 prime) : ses décisions (Dn) et règles de rédaction (En) sont citées ici, pas
recopiées. `suivi.md` : questions 11 (`s_applique`), 36 (une carte par étape, R1), 37 (les deux boutons, R3), 45 (tâtonnement avec
□ et △, R4). Corrigés de l'enseignant `Id_rem.pdf` (2.9, 2.10) et `tatonement.pdf` (2.11, 2.12), polycopié Javet 1MRenf (chap. 2), dans
`docs/reference/equations-2e-degre/` : ils font foi pour la rédaction, sauf les écarts voulus (D1 : aucune fraction au tâtonnement ;
question 45).

## 1. Objectif et public

- **Objectif** : l'élève apprend à **choisir la méthode**, dans l'ordre du cours (D28) : ME → Id. rem. → S-P → tâtonnement → formule (Δ),
  puis le produit nul. Le quiz ne montre pas une résolution : l'élève la construit, une décision à la fois, et voit s'ajouter à chaque
  bonne réponse la carte de l'étape, celle de l'onglet « Résoudre ».
- **Public** : 1M (1Ms, 1Mr), 1C et 2C, les seuls niveaux de l'outil. Une seule rédaction pour les trois : produit nul avec le facteur
  constant écrit « 6 = 0 » et marqué « impossible » (D7). Pas de bouton de filière.

## 2. Règles

**QZ-01. Place.** Deux onglets en tête de l'outil : « Résoudre » (par défaut) et « S'entraîner » (composant commun `monterOnglets`, `commun/composants.js`).
Changer d'onglet ne perd ni la saisie de « Résoudre » ni la partie en cours de « S'entraîner ». `?onglet=entrainement` ouvre directement le quiz.

**QZ-02. Source unique.** Le quiz ne contient **aucune réponse écrite à la main**. Le moteur (`moteur/second_degre.py`, `resoudre_equation`)
produit la résolution en **étapes structurées** (§ 4) ; l'onglet « Résoudre » les montre en une carte par étape (`second_degre.cartes`, R1),
l'onglet « S'entraîner » les dévoile une à une en posant une question à chacune.
Conséquence : le quiz ne peut pas contredire la résolution, et les mêmes tests (oracle) valident les deux.

**QZ-03. Déroulé d'une partie.**
1. Une équation est tirée (§ 3) et affichée seule, avec la question « Par quoi commencez-vous ? ».
2. L'élève choisit un bouton (QZ-04).
3. **Bonne réponse** (la méthode que le chemin du cours écrit à cet endroit, QZ-05) : « ✓ » et une phrase courte ; la carte de l'étape
   s'ajoute (« Étape k » et son badge, comme dans « Résoudre ») : ses lignes de chaîne avec leur étiquette (« ME », « Id. rem. A² − B²
   avec ⟦A = x, B = 1⟧ », « produit nul » ; D5, D29) et les lignes pleine largeur qui les précèdent : phrase de choix (D19),
   « Vérification : 2AB = … ✓ » (D6), tableau S-P, lignes du tâtonnement (« ⟦x = −5⟧ est solution, car … », puis « Donc … = (x + 5)(□x + △),
   avec ⟦□ = 2⟧ et 15 = 5 · △, donc ⟦△ = 3⟧. », question 45).
4. La question suivante porte sur ce qui reste à faire : « Et pour x² − 1 ? », « Le produit est factorisé. Et maintenant ? » ; après une
   tentative en échec, « Aucun couple ne convient. Et maintenant ? » ou « Aucun diviseur de c n'est solution. Et maintenant ? » (QZ-05) ;
   après un tableau S-P de plus de 12 lignes (§ 13.5 de `decisions.md`), « Il y a trop de couples à tester. Et maintenant ? » ; après
   un échec sur un facteur (E9), « Et pour <trinôme> = 0 ? » une fois le produit nul écrit (QZ-05, point a du § 7 ; exemple : F17, § 3).
   Les étapes sans question (réordonnancement, « supprimer les fractions », « isoler » ; QZ-04, point i du § 7) s'ajoutent d'office,
   sans bouton, et la partie passe à la question suivante.
5. La partie se termine sur la carte « Solution » (S encadré, ligne ≈ d'E14), avec le bilan (QZ-08) et les boutons « Nouvelle équation »
   et « Voir dans Résoudre ».

Exemple de référence (2.9 a ; chaque carte commence par l'équation d'arrivée de la précédente, R1) :

| Question | Bonne réponse | Carte ajoutée |
|---|---|---|
| Par quoi commencez-vous ? | ME | Mise en évidence : `6x² − 6 = 0 ⇔ 6(x² − 1) = 0` · ME |
| Et pour x² − 1 ? | A² − B² | Identité remarquable : `6(x² − 1) = 0 ⇔ 6(x + 1)(x − 1) = 0` · Id. rem. A² − B² avec ⟦A = x, B = 1⟧ |
| Le produit est factorisé. Et maintenant ? | Produit nul | Produit nul : `6(x + 1)(x − 1) = 0 ⇔ 6 = 0 (impossible) ou x + 1 = 0 ou x − 1 = 0` · produit nul, `⇔ x = −1 ou x = 1` ; puis la carte « Solution », `S = {−1 ; 1}` |

**QZ-04. Les boutons proposés**, selon la phase (toujours les mêmes à une phase donnée, pour ne pas souffler la réponse) :

| Phase | Boutons |
|---|---|
| `ramener` : équation qui n'est pas sous la forme « … = 0 » | Tout ramener à gauche (… = 0) · Développer · Produit nul · ME · A² − B² · A² + 2AB + B² · A² − 2AB + B² · S-P · Tâtonnement · Formule (Δ) |
| `factoriser` : polynôme ou facteur à factoriser, aussi après une tentative en échec | ME · A² − B² · A² + 2AB + B² · A² − 2AB + B² · S-P · Tâtonnement · Formule (Δ) |
| `produit_nul` : produit de facteurs du 1er degré (et constantes) = 0 | Produit nul · Développer · Formule (Δ) |
| `delta_valeur` : après « Formule (Δ) », valeur de Δ | 3 ou 4 valeurs : la bonne et des erreurs typiques calculées (b² + 4ac, −b² − 4ac, b − 4ac), toutes distinctes |
| `delta_nombre` : après Δ, nombre de solutions | 2 · 1 · 0 |

- Les identités remarquables sont écrites en formules (KaTeX) sur les boutons.
- « Développer » en phase `ramener` : bonne réponse de F15 et d'Az 4.1 g (E2, D27) ; ailleurs, acceptée (QZ-05) si `resoudre_equation`
  résout la forme développée (F12, F16 ; point f du § 7), y compris devant un produit nul (phase `produit_nul`, QZ-05, QZ-07).
  « Tout ramener à gauche » : bonne réponse de F12 et F16, acceptée en F15
  (point h). « Produit nul » est un bouton de la phase `ramener` (choix validé le 06.11.2026) : c'est le piège de F15 et de F16.
- Quand il reste un facteur du 2e degré non factorisé (après « ME » sur x³ − 5x² + 6x, par exemple), la question suivante porte sur ce
  facteur seul (« Et pour x² − 5x + 6 ? ») avec les boutons de la phase `factoriser`.
- **Étapes sans question** (point i du § 7, décision du 06.11.2026) : « « supprimer les fractions » et « isoler » sont des étapes sans
  question, affichées d'office (comme la ligne de réordonnancement, réponse 1 du § 7). Aucune famille ne les vise. » Ce sont la ligne
  seulement réordonnée (E1), l'étape « on multiplie par 12 » (méthode `FRACTIONS`, R2) et la phase `isoler` (degré 1) ; elles n'ont ni
  question ni bouton, et ne comptent pas dans le bilan (QZ-08).
- « Diviser par la constante » n'est **jamais** proposé : ce n'est pas la rédaction des 1M, 1C et 2C (le facteur constant passe par le
  produit nul, D7).

**QZ-05. Attendue, juste pas dans l'ordre, erreur** (décisions du 06.11.2026 : tentatives en échec, puis points a à h du § 7).
- **Attendue** : toujours ce que le chemin du cours (`chemin`, D28) écrit ensuite, **tentative en échec comprise**. Quand le S-P (D3) ou
  le tâtonnement (D1, E7) échoue, il est la bonne réponse : ses lignes s'ajoutent (phrase de choix ; tableau S-P sans ✓, puis « Aucun
  couple ne convient. », ou « On teste les diviseurs de 1 (±1) : aucun n'est solution. » ; tableau de plus de 12 lignes : « Le trinôme
  est unitaire, mais il y a trop de couples à tester. », § 13.5), puis la question « Aucun couple ne convient. Et maintenant ? » (ou
  « Aucun diviseur de c n'est solution. Et maintenant ? », « Il y a trop de couples à tester. Et maintenant ? ») attend « Formule (Δ) »,
  dont l'étape `FORMULE` commence par « On utilise la formule. » (§ 4, points b et c ; décision du 06.11.2026, fin d'après-midi : deux
  phrases partout).
- **Échec sur un facteur (E9, point a)** : le chemin écrit le produit nul avant Δ. « Et maintenant ? » attend donc « Produit nul » ; puis
  « Et pour <trinôme> = 0 ? » attend « Formule (Δ) », dont l'étape commence par « On utilise la formule. », écrite après la ligne du
  produit nul (décision du 06.11.2026). « Formule (Δ) » choisie tout de suite (à « Et maintenant ? ») est acceptée. Exemple : Javet
  2.17 c et F17 (§ 3).
- **Acceptée** (« juste, pas dans l'ordre ») : tout autre bouton dont la méthode aboutit, c'est-à-dire dont le moteur résout la forme
  obtenue (point f). Le chantier « S'entraîner » ajoute une fonction de classement des boutons qui fait réellement le calcul, formes
  structurées comprises ; sur un polynôme développé, `s_applique(methode, P)` le fait déjà (§ 13.4 : « la méthode aboutit »). Ce
  classement ne sert jamais à choisir l'attendue. Remarque : « Cela marche, mais le S-P vient avant dans l'ordre du cours. » (de même
  « … l'identité remarquable vient avant … » ; choix validé : sans « aussi ») ; « Tout ramener à gauche » en F15 : « Cela marche, mais ici
  on développe d'abord le produit. » (point h). La partie continue **par le chemin du cours**, lignes de l'échec comprises ; l'étape est
  comptée « juste, pas dans l'ordre » (QZ-08). Exemples : la formule d'emblée là où le S-P échoue (F4, F5, F10) ; le S-P pour
  t² + 20t + 100 (F7) ; « Développer » quand `resoudre_equation` résout la forme développée (F12, F16) ; « Développer » devant un
  produit nul (point f ; décision du 06.11.2026), avec la remarque « Cela marche, mais l'équation est déjà un produit égal à 0 : le
  produit nul est plus rapide. ».
- **Refusée** : tout autre bouton (QZ-06, QZ-07).
- Ce que `s_applique` décide sur `main` (question 11 de `suivi.md`) : rien en degré < 2 ;
  - ME : coefficients entiers et facteur k·xʲ différent de 1 (−pgcd quand a < 0, −1 compris, D21) ; aucune ME avec des coefficients
    non entiers (§ 13.4) ;
  - Id. rem. : sur le polynôme développé (E5, D8) ; A = k·xʲ avec k² = a, B rationnel ou √|c| simplifié quand le terme en x manque ;
    48z² − 216z + 243 n'en est **pas** une avant la ME (48 n'est pas un carré), x² + 6x + 4 non plus (2AB = 4x) ;
  - S-P : a = 1, coefficients entiers, c ≠ 0, un couple existe (même si le tableau aurait plus de 12 lignes) ;
  - tâtonnement : coefficients entiers, a ≥ 2, c ≠ 0, une racine entière existe (§ 9 de `decisions.md`) ; jamais de fraction (D1) ;
    on suit le code : a = 1 est refusé (QZ-07, point e) ;
  - formule : tout trinôme du 2e degré ; jamais en degré ≥ 3 (x³ − x, F11).
- Phase `ramener` : les méthodes de factorisation et le produit nul sont refusés (QZ-07) ; « Développer » est acceptée si
  `resoudre_equation` résout la forme développée (F12, F16), « Tout ramener à gauche » en F15 (point h). `s_applique` ne lit pas les
  formes structurées (pour F16, `s_applique("ME", −2x² + x + 1)` met −1 en évidence, pas x − 1) : la fonction de classement en décide
  (point f).

**QZ-06. Erreur.** Un choix refusé donne une explication **propre à l'équation et au choix** (QZ-07), en rouge, et l'élève réessaie (le bouton
choisi est grisé). Après **deux** erreurs sur la même question, la bonne réponse est donnée avec son explication, la carte s'ajoute, et l'étape
est comptée « erreur ».

**QZ-07. Les explications.** Vouvoiement (R12), une ou deux phrases, avec les nombres de l'équation, jamais le nom d'une méthode interne (SOC, 7c).
Elles sont produites par le moteur avec l'étape, pas écrites dans la page. Une tentative en échec du chemin du cours n'est jamais une erreur
(QZ-05).

**Règle d** (point d du § 7, généralisée le 06.11.2026 en fin d'après-midi en algorithme du moteur, § 4) : « une explication de refus
nomme d'abord, avec les nombres de l'équation, la première méthode du cours qui s'applique avant le choix (ME de −1 en F3, ME ou Id. rem.
pour x² − 5x et x² + 6x + 9) ; sinon, elle dit pourquoi le choix n'aboutit pas. » Les méthodes « avant le choix » sont celles de l'ordre
du cours (D28) : en phase `ramener`, ramener tout à gauche (ou développer, F15) ; puis ME, Id. rem. ; en phase `produit_nul`, le
produit nul. Chaque ligne ci-dessous est un exemple de cette règle (colonne « Branche ») ; une explication commence par la méthode
d'avant quand il y en a une.

| Situation | Branche | Explication |
|---|---|---|
| Id. rem., S-P ou tâtonnement choisi alors qu'un facteur commun existe (2.9 a, F1) | ME d'avant | « Avant tout, cherchez un facteur commun : 6x² et 6 sont tous les deux divisibles par 6. » |
| Tâtonnement choisi pour x² − 5x (a = 1, une ME vient avant) | ME d'avant | « Avant tout, cherchez un facteur commun : x² et 5x contiennent tous les deux x. » |
| S-P ou tâtonnement choisi alors que a = −1 (F3, −x² + 5x − 6) | ME de −1 d'avant | « Avant le S-P, mettez −1 en évidence : ici a = −1, et le S-P demande un trinôme unitaire (a = 1). » (tâtonnement : « Avant le tâtonnement, mettez −1 en évidence : ici a = −1. ») |
| Formule choisie en degré 3 (F11, x³ − x ; point h) | ME d'avant | « Avant tout, cherchez un facteur commun : x³ et x contiennent tous les deux x. La formule ne s'applique qu'à un trinôme (degré 2), et ici le degré est 3. » |
| S-P choisi alors qu'une Id. rem. s'applique (F6, x² − 5 ; point h) | Id. rem. d'avant | « Avant le S-P, regardez les identités remarquables : x² − 5 est une différence (A = x, B = √5). » |
| Tâtonnement choisi alors qu'une Id. rem. s'applique (4x² − 9) | Id. rem. d'avant | « Avant le tâtonnement, regardez les identités remarquables : 4x² et 9 sont des carrés. » |
| Tâtonnement choisi pour x² + 6x + 9 (a = 1, une Id. rem. vient avant) | Id. rem. d'avant | « Avant le tâtonnement, regardez les identités remarquables : x² et 9 sont des carrés, et 2 · x · 3 = 6x. » |
| Méthode de factorisation ou produit nul choisi avant de ramener à « … = 0 » (F12, F16 ; choix validé pour F16) | ramener d'avant | F16 : « Ramenez d'abord tout à gauche : le second membre, (x − 1)(x + 3), n'est pas nul. » ; F12 (4(x − 2)² = 1) : « Ramenez d'abord tout à gauche : le second membre, 1, n'est pas nul. » |
| Produit nul choisi, produit égal à un nombre non nul (F15) | développer d'avant | « Avant le produit nul, développez (x + 1)(x + 3) : le produit vaut 15, pas 0. » |
| Méthode de factorisation ou formule choisie en F15 | développer d'avant | « Avant tout, développez (x + 1)(x + 3) : le second membre vaut 15, pas 0. » |
| Développer choisi devant un produit nul que `resoudre_equation` ne résout pas une fois développé (Az 4.1 d : la forme développée 3x³ − 14x² + 21x − 10 = 0 est `hors_cours` sur `main`) | produit nul d'avant | « Utilisez d'abord le produit nul : l'équation est déjà un produit égal à 0. » |
| Fausse Id. rem. (F4 ; les carrés sont aux bouts, mais pas 2AB) | pourquoi | « x² et 4 sont des carrés (A = x, B = 2), mais 2AB = 2 · x · 2 = 4x ≠ 6x : ce n'est pas une identité remarquable. » |
| Mauvaise des trois Id. rem. | pourquoi | « Le terme du milieu est négatif : c'est A² − 2AB + B². » ; « Il n'y a pas de terme en x : c'est A² − B². » |
| Somme de deux carrés prise pour A² − B² (F5) | pourquoi | « x² + 4 est une somme : A² − B² demande une différence. » |
| Id. rem. choisie, un terme des bouts n'est pas un carré (F8, 2x² + 13x + 15 ; nouveau modèle, à relire) | pourquoi | « 2x² n'est pas un carré : ce n'est pas une identité remarquable. » |
| ME choisie sans facteur commun (F4, x² + 6x + 4 ; nouveau modèle, à relire) | pourquoi | « x², 6x et 4 n'ont pas de facteur commun. » |
| S-P choisi alors que a ≠ 1, sans ME ni Id. rem. d'avant (F8, F9) | pourquoi | « Le S-P ne s'utilise que si le trinôme est unitaire (a = 1) ; ici a = 2. » |
| Tâtonnement choisi alors que a = 1, sans ME ni Id. rem. d'avant (F10, F13 ; refusé : on suit le code, a ≥ 2 ; point e) | pourquoi | « Le trinôme est unitaire (a = 1) : le S-P est plus rapide. » |
| Tâtonnement choisi, coefficients non entiers, sans méthode d'avant (Javet 2.17 e ; D22 ; décision du 06.11.2026) | pourquoi | « Le tâtonnement demande des coefficients entiers : il faut la formule. » |
| Valeur de Δ fausse | pourquoi | l'erreur typique nommée : « Attention au signe : Δ = b² − 4ac = (−5)² − 4 · 1 · 6. » |
| Nombre de solutions faux | pourquoi | « Δ = −3 < 0 : l'équation n'a aucune solution réelle. » |

Remarques des choix acceptés (QZ-05 ; pas des refus) :
- choix qui aboutit mais vient après l'attendue dans l'ordre du cours (la formule d'emblée en F4, le S-P en F7) : « Cela marche, mais le
  S-P vient avant dans l'ordre du cours. » (de même « … l'identité remarquable vient avant … ») ;
- « Tout ramener à gauche » en F15 (point h) : « Cela marche, mais ici on développe d'abord le produit. » ;
- « Développer » devant un produit nul, quand `resoudre_equation` résout la forme développée (point f ; décision du 06.11.2026) : « Cela
  marche, mais l'équation est déjà un produit égal à 0 : le produit nul est plus rapide. »

Un refus pour lequel l'algorithme du § 4 ne trouve aucun modèle ne s'affiche jamais : l'équation n'est pas proposée (QZ-10), et le test
de la famille échoue (§ 5).

**QZ-08. Score et bilan.** Rien n'est enregistré (ni compte, ni `localStorage`). La page tient un compteur pour la session : « Étapes réussies du premier coup : 7 / 9 ».
À la fin d'une partie, le bilan donne trois nombres : étapes réussies du premier coup (✓), étapes « justes, pas dans l'ordre » (QZ-05), erreurs (QZ-06).
Recharger la page remet le compteur à zéro.

**QZ-09. Fin de partie.** « Nouvelle équation » tire une autre famille (§ 3) que la précédente. « Voir dans Résoudre » passe à l'onglet « Résoudre » avec l'équation
saisie et calculée (même mécanisme que `?f=`).

**QZ-10. Rien de faux à l'écran.** Une équation n'est proposée que si `resoudre_equation` rend le statut `resolu` (garde-fou exact : chaque
factorisation redéveloppée et comparée, chaque solution substituée exactement ; principe 1 de `decisions.md`). Tout autre statut (`pas_encore`,
`hors_cours`, `forme_non_traitee`, `ne_conclut_pas`, `hors_bornes`) la rejette **avant** l'affichage, et une autre est tirée (nombre d'essais borné ;
au-delà, une équation de la liste fixe). Aucun message « ne conclut pas » ne peut apparaître dans le quiz.

**QZ-11. Mise en page.** Fluide, cible 390 px, filet de sécurité 320 px (SOC-19) : les boutons en grille de deux colonnes (une colonne sous
360 px si un libellé déborde), cibles ≥ 44 px ; les cartes sont celles de « Résoudre » : bloc commun « chaine » (rangées de
`chaine.bloc_rangees`, comme `second_degre.cartes` ; `chaine.bloc_chaine` pour une chaîne entière) et CSS `.chaine` ; le tableau S-P est le bloc
commun `tableau_essais` (`sortie.tableau_essais`, D4) ; encadrés de D29. Après chaque réponse, le focus va à l'explication (`aria-live="polite"`)
puis à la question suivante ; tout se fait au clavier.

**QZ-12. Impression.** L'onglet « S'entraîner » ne s'imprime pas (`no-print`) ; le bouton PDF reste propre à « Résoudre ».

**QZ-13. Partage.** Une partie a une URL `?onglet=entrainement&exo=<famille>-<graine>` (même principe que SOC, 2) : la même équation revient, ce qui sert aux tests et
permet à l'enseignant de projeter un cas précis.

**QZ-14. Niveau 2 (plus tard, hors de la première version).** Sous-questions après une bonne réponse : « Que mettez-vous en évidence ? » (6 · 3 · 6x · x),
« A = ? B = ? », « Quel nombre r annule le trinôme ? ». Le format des étapes (§ 4) les prévoit déjà, pour ne rien refaire.

## 3. Les équations : familles de pièges

Chaque famille est un générateur à coefficients au hasard (bornés : entiers de −12 à 12, au plus une fraction simple), plus les exercices 2.9
à 2.12 des corrigés comme liste fixe (réponse 3 du § 7). Le générateur **vérifie** que l'équation tirée a bien la propriété et le chemin de sa
famille (sinon il retire, QZ-10). Tirage : familles équiprobables, jamais deux fois la même de suite.

Liste fixe : les 40 exercices de 2.9 à 2.12 (§ 8 de `decisions.md`), plus **Javet 2.17 c** (2x² − 4x − 4 = 0 ; décision du 06.11.2026,
point a du § 7), soit 41 équations, toutes résolues par l'outil sur `main`. Le chemin de **2.12 b** (6x² + 5x + 1 = 0) a changé :
tâtonnement en échec (diviseurs ±1), puis la formule (Δ = 1), écart voulu au corrigé (D1).

| # | Famille | Exemple | Chemin du cours | Choix piège (refusé, ou accepté avec QZ-05) |
|---|---|---|---|---|
| F1 | ME cachée devant une Id. rem. | 48z² − 216z + 243 = 0 | ME (3) → A² − 2AB + B² → produit nul | Id. rem. d'emblée (refusée : 48 n'est pas un carré) |
| F2 | ME qui rend le trinôme unitaire | 2z² + 24z + 64 = 0 | ME (2) → S-P → produit nul | tâtonnement (accepté : r = −4 existe) |
| F3 | a = −1 | −x² + 5x − 6 = 0 | ME (−1) → S-P → produit nul | S-P d'emblée (refusé : la ME de −1 vient avant, QZ-07) |
| F4 | Fausse Id. rem. | x² + 6x + 4 = 0 | S-P en échec → formule (Δ = 20) | A² + 2AB + B² (refusée) ; formule d'emblée (acceptée) |
| F5 | Somme de deux carrés | x² + 4 = 0 | S-P en échec → formule (Δ = −16 < 0, S = ∅) | A² − B² (refusée) ; formule d'emblée (acceptée) |
| F6 | Id. rem. avec B = √k ou B fractionnaire | x² − 5 = 0 ; 9x² − 1/9 = 0 | A² − B² → produit nul | formule (acceptée) ; S-P pour x² − 5 (refusé, QZ-07, point h) |
| F7 | Id. rem. qui marche aussi en S-P | t² + 20t + 100 = 0 | A² + 2AB + B² (la vérification 2AB écrite) | S-P (accepté) |
| F8 | Non unitaire, sans ME | 2x² + 13x + 15 = 0 | tâtonnement (r = −5, □ = 2, △ = 3) → produit nul | S-P (refusé : a ≠ 1) |
| F9 | Racine fractionnaire (D1 : aucune fraction cherchée) | 6x² + 5x + 1 = 0 (2.12 b) | tâtonnement en échec (±1) → formule (Δ = 1) | S-P (refusé : a ≠ 1) ; formule d'emblée (acceptée) |
| F10 | Pas de racine rationnelle | x² + x − 1 = 0 | S-P en échec → formule (Δ = 5, racines avec √5) | tâtonnement (refusé : a = 1) ; formule d'emblée (acceptée) |
| F11 | Degré 3 | x³ − x = 0 | ME (x) → A² − B² → produit nul | formule (refusée : degré 3, QZ-07, point h) |
| F12 | Pas sous la forme « … = 0 » | 4(x − 2)² = 1 ; x² = 3x + 10 | tout ramener à gauche, sans développer → Id. rem. avec A = 2(x − 2), B = 1 (« car ») ; ramener → S-P | Id. rem. d'emblée (refusée) ; Développer (accepté si `resoudre_equation` résout la forme développée, point f) |
| F13 | Unitaire « simple » (témoin) | x² − 5x − 36 = 0 | S-P → produit nul | tâtonnement (refusé : a = 1) |
| F14 | Δ = 0 sans Id. rem. visible | 4x² + 12x + 9 = 0 (Id. rem.) ; 2x² + 4x + 2 = 0 (ME puis Id. rem.) | selon le cas | formule (acceptée) |
| F15 | Produit égal à un nombre non nul | (x + 1)(x + 3) = 15 | Développer (double distribution, E2) → ramener (x² + 4x − 12 = 0) → S-P → produit nul | Produit nul (refusé, QZ-07) ; « Tout ramener à gauche » (accepté, QZ-05, point h) |
| F16 | Facteur commun aux deux membres (2.12 e) | (x − 1)(2 − x) = (x − 1)(x + 3) | ramener sans développer, avec l'avertissement « Attention : on ne divise pas par (x − 1) … » (E3) dans l'étape « ramener » (le code fait foi, point g) → ME de (x − 1) → produit nul | Produit nul (refusé : « ramenez d'abord tout à gauche », QZ-07) ; Développer (accepté si `resoudre_equation` résout la forme développée, point f) |
| F17 | Échec sur un facteur après une ME (E9 ; décision du 06.11.2026, point a) | 2x² − 4x − 4 = 0 (Javet 2.17 c) ; 3x² + 6x − 3 = 0 ; 5x² + 5x + 5 = 0 ; −2x² + 4x + 2 = 0 | ME (constante) → S-P en échec → produit nul → formule sur le facteur (« Et pour x² − 2x − 2 = 0 ? ») | Formule (Δ) à « Aucun couple ne convient. Et maintenant ? » (acceptée, QZ-05) ; tâtonnement sur le facteur (refusé : a = 1) |

**F17, générateur** : une constante k (2 ≤ |k|, k < 0 donnant la ME de −pgcd avec sa phrase, D21, E3), puis un trinôme unitaire
x² + bx + c à coefficients entiers, c ≠ 0, **sans couple d'entiers** (b² − 4c n'est pas un carré parfait, Δ < 0 compris), qui n'est pas
une Id. rem. (b ≠ 0 quand c < 0 : sinon A² − B² avec B = √|c|, D8) ; l'équation tirée est k(x² + bx + c) développée, coefficients
bornés comme les autres familles (donc |c| ≤ 6 et le tableau S-P a au plus 2 lignes : jamais le cas « trop de couples »). Le générateur
vérifie le chemin (ME, S-P avec `aboutit` faux, produit nul, formule) et le statut `resolu` (QZ-10).

**F17, chemin vérifié sur `main`** (`resoudre_equation`, 06.11.2026) : sur 2x² − 4x − 4 = 0, 3x² + 6x − 3 = 0, 5x² + 5x + 5 = 0 et
−2x² + 4x + 2 = 0, les étapes sont `factoriser`/ME, `factoriser`/SP (`aboutit` faux), `produit_nul`, `delta_valeur`, `delta_nombre` (statut
`resolu` ; S = {1 − √3 ; 1 + √3}, {−1 − √2 ; −1 + √2}, ∅, {1 − √2 ; 1 + √2}). Sur `main`, l'étape S-P se termine par « Aucun couple ne
convient : on utilise la formule. », avant la ligne du produit nul ; avec −2, la ME est précédée de « Le coefficient de x² est négatif
(a = −2) : on met d'abord −2 en évidence. » ; avec Δ < 0, la dernière ligne est « Δ < 0 : x² + x + 1 = 0 n'a aucune solution réelle. ».
Chemin du quiz (après les points b et c, § 4), sur Javet 2.17 c :

| Question | Bonne réponse | Carte ajoutée |
|---|---|---|
| Par quoi commencez-vous ? | ME | `2x² − 4x − 4 = 0 ⇔ 2(x² − 2x − 2) = 0` · ME |
| Et pour x² − 2x − 2 ? | S-P (tentative en échec, QZ-05) | « Le trinôme x² − 2x − 2 est unitaire : S-P. », « On cherche deux nombres dont le produit vaut −2 et la somme vaut −2 : », tableau d'une ligne (1 et −2, somme −1) sans ✓, « Aucun couple ne convient. » |
| Aucun couple ne convient. Et maintenant ? | Produit nul (« Formule (Δ) » acceptée) | `⇔ 2 = 0 (impossible) ou x² − 2x − 2 = 0` · produit nul |
| Et pour x² − 2x − 2 = 0 ? | Formule (Δ) | « On utilise la formule. » (première ligne de l'étape `FORMULE`, après la ligne du produit nul) |
| valeur de Δ (`delta_valeur`) | 12 | `Δ = b² − 4ac = (−2)² − 4 · 1 · (−2) = 4 + 8 = 12` |
| nombre de solutions (`delta_nombre`) | 2 | `Δ > 0 : deux solutions. √Δ = √12 = 2√3`, x₁, x₂, `⇔ x = 1 − √3 ou x = 1 + √3` ; puis la carte « Solution », `S = {1 − √3 ; 1 + √3}` |

## 4. Interface du moteur

Sur `main` (§ 5 de `decisions.md`), `second_degre.resoudre_equation(gauche, droite, inconnue, decimaux_enonce=False, methodes=ORDRE_DU_COURS)`
rend `{statut, etapes, solutions, S, approx, variantes, message}` ; `statut` ∈ `resolu`, `pas_encore`, `hors_cours`, `forme_non_traitee`,
`ne_conclut_pas`, `hors_bornes`. Une `Etape` du moteur a les champs :

```
phase:      "ramener" | "factoriser" | "produit_nul" | "delta_valeur" | "delta_nombre" | "isoler"
methode:    "FRACTIONS" | "DEVELOPPER" | "RAMENER" (phase ramener) | "ISOLER" | "ME" | "IDREM_DIFF" | "IDREM_PLUS" | "IDREM_MOINS"
            | "SP" | "TATONNEMENT" | "FORMULE" | "PRODUIT_NUL"
cible:      TeX du polynôme, du facteur ou de l'équation traités (« Et pour x² − 1 ? »)
parametres: calcul exact de la méthode ; S-P et tâtonnement : "aboutit" (False : tentative en échec)
lignes:     rangées (lien, expr, étiquette) et lignes pleine largeur (texte ou bloc tableau_essais), en JSON par chaine.bloc_rangees
segment:    la Chaine de l'étape (usage interne)
```

Le quiz ajoute une fonction au manifeste, appelée **une seule fois par partie** (la page gère ensuite le dévoilement sans rappeler Python) :

```
quiz_json(exo)  ->  {"equation": tex, "etapes": [EtapeQuiz], "solutions": [tex], "S": tex}
EtapeQuiz = champs de l'Etape (sauf segment), plus :
  "question":   texte (« Et pour x² − 1 ? ») | null    # null : étape sans question (FRACTIONS, ISOLER ; point i)
  "boutons":    [cle]                       # QZ-04, ordre fixe de la phase ; [] pour une étape sans question
  "attendue":   cle | null                  # QZ-05 : ce que le chemin du cours écrit ensuite, tentative en échec comprise
  "acceptees":  {cle: remarque}             # QZ-05 : la méthode aboutit (fonction de classement), pas l'attendue
  "refusees":   {cle: explication}          # QZ-06, QZ-07 : une explication par bouton refusé
  "sous_questions": []                      # QZ-14, vide en première version
```

- `attendue` se lit dans `methode` : RAMENER → « Tout ramener à gauche », DEVELOPPER → « Développer », ME, les trois Id. rem., SP, TATONNEMENT,
  FORMULE → « Formule (Δ) », PRODUIT_NUL → « Produit nul ». Les étapes `delta_valeur` et `delta_nombre` ont leurs propres boutons (QZ-04).
- **Étapes sans question** (point i, décision du 06.11.2026) : la ligne seulement réordonnée (E1 ; elle appartient à l'étape qui suit,
  § 5 de `decisions.md`, et s'affiche d'office avant la question de cette étape), l'étape `ramener`/`FRACTIONS` (« on multiplie par
  12 », R2) et l'étape `isoler`/`ISOLER` (degré 1) : `question` et `attendue` valent null, `boutons`, `acceptees` et `refusees` sont
  vides ; la page ajoute la carte d'office et passe à l'étape suivante. Aucune famille ne les vise (§ 3).
- **Étape `FORMULE` et ses premières lignes** (points b et c ; décisions du 06.11.2026, fin d'après-midi). Sur `main`, après une
  tentative en échec, le moteur passe directement à `delta_valeur` (une étape `factoriser`/`FORMULE` n'existe que pour la formule
  choisie d'emblée, coefficients non entiers, D22), et la phrase « … : on utilise la formule. » termine l'étape de l'échec
  (`PHRASE_SP_ECHEC`, `PHRASE_SP_TROP`, ligne des diviseurs de `_ecrire_tatonnement`, `moteur/second_degre.py`). Au chantier
  « S'entraîner », première partie, côté moteur, l'étape `FORMULE` existe à part, selon le cas :
  - formule choisie d'emblée (coefficients non entiers, D22) : inchangée, la phrase de choix « Pas de ME, pas d'Id. rem. ; les
    coefficients ne sont pas entiers : on utilise la formule. » (E4) ;
  - après un S-P en échec : l'étape S-P se termine sur « Aucun couple ne convient. », l'étape `FORMULE` commence par « On utilise la
    formule. » (D3, E6) ;
  - après un tâtonnement en échec : l'étape se termine sur « On teste les diviseurs de 1 (±1) : aucun n'est solution. », l'étape
    `FORMULE` commence par « On utilise la formule. » (E7) ;
  - tableau S-P de plus de 12 lignes : l'étape S-P se termine sur « Le trinôme est unitaire, mais il y a trop de couples à tester. »,
    puis l'étape `FORMULE` (§ 13.5) ;
  - échec sur un facteur (E9, point a) : l'étape de l'échec se termine de même ; vient l'étape `produit_nul` (« Et maintenant ? »,
    `acceptees` contient « Formule (Δ) »), puis l'étape `FORMULE` du trinôme (« Et pour <trinôme> = 0 ? »), dont « On utilise la
    formule. » est la première ligne, **après** la ligne du produit nul (à faire dans `_ecrire_sp`, `_ecrire_tatonnement` et dans l'écriture
    de la formule d'un facteur, qui suit `_ecrire_produit_nul`).
  « Résoudre » écrit les mêmes lignes (invariant de concaténation) : même texte coupé en deux phrases, et, dans les cas E9, « On utilise
  la formule. » après la ligne du produit nul ; les instantanés modifiés sont listés pour l'enseignant. C'est une règle à venir : `main`
  écrit encore l'ancien texte.
- Chaque bouton de `boutons` est dans exactement un des trois ensembles (`attendue`, `acceptees`, `refusees`) : vérifié par le validateur de sortie.
- `s_applique(methode, P)` et `appliquer(methode, P)` (une méthode seule, rédigée, ou None) portent sur un `Polynome` développé ; ils existent et
  sont testés depuis P1 et P2b. Le chantier « S'entraîner » ajoute la fonction de classement des boutons (point f) : elle fait réellement le
  calcul, formes structurées comprises (« Développer » est acceptée si `resoudre_equation` résout la forme développée).
- **Algorithme de la règle d** (QZ-07 ; fonction à écrire au chantier « S'entraîner », dans `moteur/second_degre.py`, appelée par
  `quiz_json` pour chaque bouton refusé) : `explication_refus(etape, bouton, inconnue, decimaux_enonce) -> texte | None`.
  - Prend : l'étape du chemin du cours où la question est posée (sa `phase`, sa `cible` : `Polynome` développé, ou équation structurée
    en phase `ramener` et `produit_nul`), le bouton refusé (clé de QZ-04), l'inconnue et `decimaux_enonce` (pour écrire les nombres de
    l'équation comme « Résoudre », E14).
  - 1) Méthodes d'avant, dans l'ordre du cours (D28), seulement celles qui précèdent le bouton : en phase `ramener`, développer (produit
    égal à un nombre non nul, F15) puis ramener tout à gauche ; en phase `factoriser`, la ME (`s_applique("ME", cible)`, −1 et −pgcd
    compris, D21), puis l'Id. rem. (`s_applique` d'une des trois) ; en phase `produit_nul`, le produit nul. La première qui s'applique
    donne l'explication, avec les nombres de l'équation (modèles « … d'avant » de QZ-07).
  - 2) Sinon, la raison pour laquelle le bouton n'aboutit pas, lue sur la cible (modèles « pourquoi » de QZ-07) : a ≠ 1 (S-P), a = 1
    (tâtonnement, on suit le code), coefficients non entiers (tâtonnement), degré 3 (formule), fausse Id. rem., mauvaise des trois, somme
    de deux carrés, terme des bouts non carré, pas de facteur commun (ME) ; pour `delta_valeur` et `delta_nombre`, l'erreur typique.
  - Rend : le texte (TeX en ligne, vouvoiement R12, sans nom de méthode interne), ou None si aucun modèle ne s'applique : `quiz_json`
    rejette alors l'équation (QZ-10) ; le test de la famille le relève (§ 5). Le texte est recalculé à partir de la cible, jamais
    écrit à la main (QZ-02) ; chaque nombre cité est relu sur le polynôme (garde-fou, « rien de faux à l'écran »).
- La concaténation des `lignes` de toutes les étapes **est** la chaîne de `second_degre.blocs` (invariant du § 5, testé) ; les cartes du quiz
  sont celles de `second_degre.cartes` (R1), badges de `resoudre_eq.TITRES`.
- L'onglet « Résoudre » et le quiz partagent donc `resoudre_equation` ; le quiz y ajoute seulement les questions, le classement des boutons et
  les explications.

## 5. Tests

- **Python (oracle)** : pour chaque famille, 200 graines : solutions = racines de l'oracle mpmath (`oracle.racines`), et aucune autre ; propriété
  et chemin de la famille vérifiés ; chaque bouton classé dans exactement un ensemble ; `attendue` = la méthode du chemin du cours (tentatives en
  échec comprises) ; chaque méthode de `acceptees` aboutit réellement (le moteur résout la forme obtenue ; sur un polynôme développé, `appliquer`
  rend une factorisation qui se redéveloppe) ; aucune méthode de `refusees` n'aboutit ; la concaténation des `lignes` égale la chaîne de « Résoudre » pour la même équation, et les cartes celles de `cartes`.
- **Rédaction** : instantanés `quiz_json` sur la liste fixe (2.9 à 2.12, Javet 2.17 c) et une graine par famille (F1 à F17) ; une
  équation avec une étape sans question (`FRACTIONS`, `isoler` ; point i) ; une explication de refus par branche de la règle d (QZ-07) ; textes au vouvoiement (R12),
  vocabulaire (SOC, 7c), notation suisse et ≈ (D13).
- **Python (règle d)** : pour chaque famille et chaque bouton refusé, `explication_refus` rend un texte (jamais None sur les familles) ;
  quand une ME ou une Id. rem. s'applique avant le bouton, le texte la nomme.
- **Pages** : un parcours complet au clic (2.9 a) ; une tentative en échec puis « Formule (Δ) » (2.12 b) ; un échec sur un facteur
  (Javet 2.17 c : « Produit nul », puis « Formule (Δ) ») ; deux erreurs puis réponse donnée ;
  « juste, pas dans l'ordre » ; compteur ; « Voir dans Résoudre » ; `?onglet=entrainement&exo=…` ; navigation au clavier ; `test_largeurs`
  de 320 à 1100 px à chaque phase (`CONNUS` vide).

## 6. Place dans le chantier

L'onglet « S'entraîner » fera l'objet d'un **chantier séparé**. Le chantier `equations-2e-degre` (fusionné sur `main`) n'a pas d'onglet
« S'entraîner » ; il a produit tout ce que le quiz demande au moteur : `resoudre_equation`, les étapes du § 4, `s_applique`, `appliquer`,
`cartes`. Les anciens noms de ce fichier (`resoudre_polynome`, « P3 », § 13.6 (a) 7 de `decisions.md`) sont corrigés.

## 7. Questions

Réponses de l'enseignant du 05.11.2026 :

1. **Termes dans le désordre** (5 + x² − 6x = 0) : la chaîne écrit-elle une ligne « ⇔ x² − 6x + 5 = 0 » sans question, ou est-ce une étape « Ordonner » à choisir ?
   Les corrigés ne montrent pas ce cas. **Réponse : une ligne sans question** (sans étiquette).
2. **Après la formule** : faut-il aussi faire choisir les solutions (x₁, x₂ parmi des valeurs proposées), ou les afficher directement après « 2 · 1 · 0 » ?
   **Réponse : les solutions sont affichées directement en première version.**
3. **Liste fixe** : quels exercices des corrigés et du polycopié Javet faut-il garder tels quels dans le tirage (en plus des générateurs) ?
   **Réponse : les exercices 2.9 à 2.12 des corrigés de l'enseignant.**

Décisions du 06.11.2026 : 4. tentative en échec = bonne réponse, option a (QZ-05, QZ-07, F4, F5, F9, F10) ; 5. famille F15 ; 6. famille F16.

Points a à h (posés le 06.11.2026 au matin), **réglés (06.11.2026, après-midi)** ; règle générale : « attendue » est toujours ce que le
chemin du cours écrit ensuite (QZ-05). Les trois choix du matin sont validés (QZ-04, QZ-05, QZ-07).

- a. **Formule sur un facteur (E9 ; Javet 2.17 c, 2x² − 4x − 4 = 0 ; 4x² + 2x + 2 = 0)** : réglé, « Produit nul » puis la formule, formule
  tout de suite acceptée (QZ-03, QZ-05, § 4) ; le 06.11.2026 en fin d'après-midi, Javet 2.17 c entre dans la liste fixe et la famille
  F17 tire ce cas (§ 3).
- b. **Réponse écrite avant la question** : réglé avec c, « On utilise la formule. » ouvre une étape `FORMULE` à part (§ 4, QZ-05).
- c. **Pas d'étape « formule » à part après un échec** : réglé avec b, au chantier « S'entraîner », première partie, côté moteur (§ 4).
- d. **« … : il faut la formule. » faux quand une méthode vient avant (4x² − 9)** : réglé par la règle d (QZ-07 ; exemple du § 9 de
  `decisions.md` corrigé).
- e. **Tâtonnement avec a = 1** : réglé, on suit le code (a ≥ 2), refus avec sa phrase (QZ-05, QZ-07).
- f. **Ce qui « aboutit » (formes structurées, phase `ramener`)** : réglé, le moteur résout la forme obtenue ; fonction de classement des
  boutons au chantier « S'entraîner » (QZ-04, QZ-05, § 3, § 4, § 5).
- g. **Avertissement de F16** : réglé, il reste dans l'étape « ramener » (§ 3, F16).
- h. **Explications sans modèle (F6, F11, F15)** : réglé, trois phrases ajoutées (QZ-07 ; QZ-05 pour F15 ; § 3).

Décisions de l'enseignant du 06.11.2026 (fin d'après-midi) : **toutes les questions sont réglées** ; la spécification est complète.

- i. **Étapes sans bouton** (`FRACTIONS`, R2, et `isoler`, degré 1 ; ancien point f du fichier du 06.11.2026 au matin) : réglé,
  « « supprimer les fractions » et « isoler » sont des étapes sans question, affichées d'office (comme la ligne de réordonnancement,
  réponse 1 du § 7). Aucune famille ne les vise. » (QZ-03, QZ-04, § 4, § 5).
- b/c contre a : réglé, « Dans les cas E9, « On utilise la formule. » passe après la ligne du produit nul (première ligne de l'étape
  FORMULE) ; ailleurs, même texte, coupé en deux phrases. » (QZ-05, § 3 F17, § 4).
- b/c contre D3/E6 : réglé, « deux phrases partout, « Aucun couple ne convient. » puis « On utilise la formule. » ; tableau S-P de plus
  de 12 lignes : « Le trinôme est unitaire, mais il y a trop de couples à tester. » puis l'étape FORMULE. » ; D3, E6, E7 et § 13.5 de
  `decisions.md` mis à jour (QZ-03, QZ-05, § 4).
- g contre E3 : réglé, « le code fait foi » ; E3 de `decisions.md` corrigé (l'avertissement de 2.12 e est dans l'étape « ramener » ;
  § 3, F16).
- Règle d généralisée : réglé, algorithme du moteur (QZ-07, § 4 ; fonction `explication_refus` au chantier « S'entraîner »).
- QZ-07, « S-P choisi alors que a ≠ 1 » quand une ME vient avant : réglé, F3 nomme la ME de −1 avec les nombres (QZ-07, § 3).
- QZ-07, « Tâtonnement choisi alors que a = 1 » quand une ME ou une Id. rem. vient avant (x² − 5x, x² + 6x + 9) : réglé, l'explication
  nomme la ME ou l'Id. rem. ; la phrase du point e reste quand aucune ne s'applique (QZ-07).
- QZ-07, F15 (« Produit nul » et méthodes de factorisation) : réglé, l'explication nomme d'abord « développez (x + 1)(x + 3) » (QZ-07).
- QZ-07, F11 (formule en degré 3) : réglé, l'explication nomme d'abord le facteur commun (QZ-07).
- QZ-07, « Développer » devant un produit nul : réglé, « accepté (f), « Cela marche, mais l'équation est déjà un produit égal à 0 : le
  produit nul est plus rapide. » » (QZ-04, QZ-05, QZ-07) ; refusé seulement si `resoudre_equation` ne résout pas la forme développée.
- QZ-07, tâtonnement avec des coefficients non entiers : réglé, « « Le tâtonnement demande des coefficients entiers : il faut la
  formule. » (sauf si la règle d s'applique d'abord) » (QZ-07).
- Point a, liste fixe et famille : réglé, « Javet 2.17 c (2x² − 4x − 4 = 0) entre dans la liste fixe ; nouvelle famille F17 « échec sur
  un facteur après une ME » (générateur : ME d'une constante, puis un trinôme unitaire sans couple d'entiers) » (§ 3, § 5).

## 8. Tirage et examens ; moteur sur serveur (06.11.2026, soir)

**Règle (enseignant, 06.11.2026)** : un exercice tiré au sort ne doit jamais pouvoir tomber à l'examen (règle légale : on ne donne pas
aux élèves un exercice de l'examen). Elle prime sur le § 3 (liste fixe, générateurs F1 à F17).

**Ce qui ne marche pas, et pourquoi.**
- Retirer l'exercice d'examen du tirage dans le code : le code est lu par les élèves, le retrait révèle l'exercice.
- Rendre seulement le dépôt privé : la page télécharge le moteur dans le navigateur (Pyodide, `moteur/`, servi par samimir.ch) ; une
  liste d'exclusion envoyée au navigateur reste lisible, même chiffrée ou hachée, et un générateur lancé mille fois montre ce qui manque.
- Des bornes publiques du tirage, avec l'examen hors des bornes : refusé par l'enseignant (« un élève est sûr que telle ou telle
  solution n'est jamais à l'examen »).

**Décision de l'enseignant (06.11.2026, soir) : d'abord le chantier « moteur-serveur », puis « S'entraîner »** (`docs/chantiers/entrainement-2e-degre/decisions.md`, en attente, sera revu pour un tirage côté serveur). Orientation, dont les détails (hébergeur, découpage) sont à trancher au chantier « moteur-serveur » (audit à faire) :
- tout le moteur devient privé (aussi pour un accès réservé ou payant plus tard, à vérifier auprès de l'école) : les moteurs Python
  tournent sur un serveur (Infomaniak envisagé), la page n'en reçoit que la sortie JSON ; le dépôt passe en privé une fois le moteur
  retiré du site public (sans GitHub Pages, un dépôt privé est gratuit ; avec GitHub Pages, GitHub Pro est nécessaire, sinon le site
  tombe) ;
- l'onglet « S'entraîner » est construit **directement côté serveur**, après cette migration, et non dans le navigateur.

**Principe du tirage côté serveur** (proposé, à valider avec le chantier « moteur-serveur ») :
- le générateur et la liste des exercices d'examen ne quittent jamais le serveur ni le dépôt privé ; aucune donnée d'examen dans un
  fichier servi par le site ;
- une réserve d'exercices est tirée au hasard dans un très grand ensemble, avec une graine secrète, et les exercices d'examen en sont
  retirés à la construction ; la réserve est renouvelée (par exemple chaque semestre) ;
- les sujets d'examen restent hors de tout fichier public (`docs/reference/`, jamais commité, ou le dépôt privé).

**Points à relire par l'enseignant** (mise à jour du 06.11.2026, fin d'après-midi) :
- phrases de refus écrites pour la règle d, à relire : F3, x² − 5x, x² + 6x + 9, F11, F15, Az 4.1 d, et les deux nouveaux modèles
  marqués « à relire » en QZ-07 (F8 « 2x² n'est pas un carré… », F4 « x², 6x et 4 n'ont pas de facteur commun. ») ;
- phrase de F16 réordonnée pour la règle d : « Ramenez d'abord tout à gauche : le second membre, (x − 1)(x + 3), n'est pas nul. »
  (forme validée : « Le second membre n'est pas nul : ramenez d'abord tout à gauche. ») ;
- F10 : la phrase « … le S-P est plus rapide » est gardée, alors que le S-P y échoue aussi ;
- cas sans modèle (aucune famille ne les tire ; `explication_refus` rendrait None) : « Formule (Δ) » à l'étape du produit nul hors E9 ;
  S-P avec a = 1 et des coefficients non entiers, sans Id. rem. ;
- `decisions.md` § 7 (exemples rédigés, dont Javet 2.17 c), § 10 et E9 gardent l'ancien texte « … : on utilise la formule. » (une
  phrase, avant la ligne du produit nul) : à aligner sur D3, E6, E7 et § 13.5 (06.11.2026).
