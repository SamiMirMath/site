# Onglet « S'entraîner » de l'outil Équations du 2e degré : spécification

**Statut (mis à jour le 06.11.2026) : accepté sur le principe** ; l'onglet sera un chantier séparé (§ 6). Le chantier `equations-2e-degre`,
fusionné sur `main` avec ses corrections R1 à R4 et P6, fournit déjà les étapes structurées du § 4.
Dates : proposé le 04.11.2026 ; accepté sur le principe le 05.11.2026 ; mis à jour le 06.11.2026 (décisions du jour, alignement sur
`decisions.md` et sur le code de `main`).

Décisions de l'enseignant :
- 04.11.2026 : un onglet dans l'outil du 2e degré ; un quiz « évolutif » qui fait construire la résolution étape par étape ; QZ-05 (méthode
  juste mais pas dans l'ordre), QZ-06 (deux essais) et « niveau 2 plus tard » (QZ-14) acceptées.
- 06.11.2026 : une tentative en échec du chemin du cours est une bonne réponse (QZ-05, option a) ; familles F15 et F16 (§ 3).

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
   tentative en échec, « Aucun couple ne convient. Et maintenant ? » ou « Aucun diviseur de c n'est solution. Et maintenant ? » (QZ-05).
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
- « Développer » en phase `ramener` : bonne réponse de F15 et d'Az 4.1 g (E2, D27), acceptée pour F16 ; « Produit nul » y est le piège
  de F15 et de F16.
- Quand il reste un facteur du 2e degré non factorisé (après « ME » sur x³ − 5x² + 6x, par exemple), la question suivante porte sur ce
  facteur seul (« Et pour x² − 5x + 6 ? ») avec les boutons de la phase `factoriser`.
- Sans question : une ligne seulement réordonnée (E1, réponse 1 du § 7). Sans bouton prévu : l'étape « on multiplie par 12 » (méthode
  `FRACTIONS`, R2) et la phase `isoler` (degré 1) ; aucune famille ne les tire (§ 7, question ouverte f).
- « Diviser par la constante » n'est **jamais** proposé : ce n'est pas la rédaction des 1M, 1C et 2C (le facteur constant passe par le
  produit nul, D7).

**QZ-05. Attendue, juste pas dans l'ordre, erreur** (décision du 06.11.2026 pour les tentatives en échec).
- **Attendue** : la méthode que le chemin du cours (`chemin`, D28) écrit à cet endroit, **tentative en échec comprise**. Quand le S-P
  (D3) ou le tâtonnement (D1, E7) échoue, il est la bonne réponse : ses lignes s'ajoutent (phrase de choix ; tableau S-P sans ✓, puis
  « Aucun couple ne convient : on utilise la formule. », ou « On teste les diviseurs de 1 (±1) : aucun n'est solution. On utilise la
  formule. »), puis la question « Aucun couple ne convient. Et maintenant ? » (ou « Aucun diviseur de c n'est solution. Et maintenant ? »)
  attend « Formule (Δ) ».
- **Acceptée** (« juste, pas dans l'ordre ») : tout autre bouton dont la méthode aboutit, `s_applique(methode, P)` sur la cible (§ 13.4 :
  « la méthode aboutit ») ; `s_applique` ne sert qu'à ce classement, jamais à choisir l'attendue. Remarque : « Cela marche, mais le S-P
  vient avant dans l'ordre du cours. » (de même « … l'identité remarquable vient avant … »). La partie continue **par le chemin du
  cours**, lignes de l'échec comprises ; l'étape est comptée « juste, pas dans l'ordre » (QZ-08). Exemples : la formule d'emblée là où
  le S-P échoue (F4, F5, F10) ; le S-P pour t² + 20t + 100 (F7).
- **Refusée** : tout autre bouton (QZ-06, QZ-07).
- Ce que `s_applique` décide sur `main` (question 11 de `suivi.md`) : rien en degré < 2 ;
  - ME : coefficients entiers et facteur k·xʲ différent de 1 (−pgcd quand a < 0, −1 compris, D21) ; aucune ME avec des coefficients
    non entiers (§ 13.4) ;
  - Id. rem. : sur le polynôme développé (E5, D8) ; A = k·xʲ avec k² = a, B rationnel ou √|c| simplifié quand le terme en x manque ;
    48z² − 216z + 243 n'en est **pas** une avant la ME (48 n'est pas un carré), x² + 6x + 4 non plus (2AB = 4x) ;
  - S-P : a = 1, coefficients entiers, c ≠ 0, un couple existe (même si le tableau aurait plus de 12 lignes) ;
  - tâtonnement : coefficients entiers, a ≥ 2, c ≠ 0, une racine entière existe (§ 9 de `decisions.md`) ; jamais de fraction (D1) ;
  - formule : tout trinôme du 2e degré ; jamais en degré ≥ 3 (x³ − x, F11).
- Phase `ramener` : les méthodes de factorisation et le produit nul sont refusés (QZ-07) ; « Développer » est acceptée si elle aboutit
  (F16). `s_applique` ne couvre ni « Développer » ni « Tout ramener à gauche » (§ 7, question ouverte d).

**QZ-06. Erreur.** Un choix refusé donne une explication **propre à l'équation et au choix** (QZ-07), en rouge, et l'élève réessaie (le bouton
choisi est grisé). Après **deux** erreurs sur la même question, la bonne réponse est donnée avec son explication, la carte s'ajoute, et l'étape
est comptée « erreur ».

**QZ-07. Les explications.** Vouvoiement (R12), une ou deux phrases, avec les nombres de l'équation, jamais le nom d'une méthode interne (SOC, 7c).
Elles sont produites par le moteur avec l'étape, pas écrites dans la page. Une tentative en échec du chemin du cours n'est jamais une erreur
(QZ-05). Modèles :

| Situation | Explication |
|---|---|
| Id. rem. ou S-P choisi alors qu'un facteur commun existe | « Avant tout, cherchez un facteur commun : 6x² et 6 sont tous les deux divisibles par 6. » |
| Fausse Id. rem. (les carrés sont aux bouts, mais pas 2AB) | « x² et 4 sont des carrés (A = x, B = 2), mais 2AB = 2 · x · 2 = 4x ≠ 6x : ce n'est pas une identité remarquable. » |
| Mauvaise des trois Id. rem. | « Le terme du milieu est négatif : c'est A² − 2AB + B². » ; « Il n'y a pas de terme en x : c'est A² − B². » |
| Somme de deux carrés prise pour A² − B² | « x² + 4 est une somme : A² − B² demande une différence. » |
| S-P choisi alors que a ≠ 1 | « Le S-P ne s'utilise que si le trinôme est unitaire (a = 1) ; ici a = 2. » |
| Tâtonnement choisi alors que a = 1 (refusé : a ≥ 2, question 11) | « Le trinôme est unitaire (a = 1) : le S-P est plus rapide. » |
| Tâtonnement choisi hors du chemin du cours, aucune racine entière | « Aucun diviseur de −1 n'annule le trinôme : il faut la formule. » (§ 9 de `decisions.md` ; § 7, question ouverte c) |
| Méthode de factorisation ou produit nul choisi avant de ramener à « … = 0 » (F12, F16) | « Le second membre n'est pas nul : ramenez d'abord tout à gauche. » |
| Produit nul choisi, produit égal à un nombre non nul (F15) | « Le produit vaut 15, pas 0 : le produit nul ne s'applique pas. Développez d'abord. » |
| Développer choisi devant un produit nul | « L'équation est déjà un produit égal à 0 : utilisez le produit nul. » |
| Valeur de Δ fausse | l'erreur typique nommée : « Attention au signe : Δ = b² − 4ac = (−5)² − 4 · 1 · 6. » |
| Nombre de solutions faux | « Δ = −3 < 0 : l'équation n'a aucune solution réelle. » |

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

Liste fixe : les 40 exercices de 2.9 à 2.12 (§ 8 de `decisions.md`) sont tous résolus par l'outil sur `main`. Le chemin de **2.12 b**
(6x² + 5x + 1 = 0) a changé : tâtonnement en échec (diviseurs ±1), puis la formule (Δ = 1), écart voulu au corrigé (D1).

| # | Famille | Exemple | Chemin du cours | Choix piège (refusé, ou accepté avec QZ-05) |
|---|---|---|---|---|
| F1 | ME cachée devant une Id. rem. | 48z² − 216z + 243 = 0 | ME (3) → A² − 2AB + B² → produit nul | Id. rem. d'emblée (refusée : 48 n'est pas un carré) |
| F2 | ME qui rend le trinôme unitaire | 2z² + 24z + 64 = 0 | ME (2) → S-P → produit nul | tâtonnement (accepté : r = −4 existe) |
| F3 | a = −1 | −x² + 5x − 6 = 0 | ME (−1) → S-P → produit nul | S-P d'emblée (refusé : a = −1) |
| F4 | Fausse Id. rem. | x² + 6x + 4 = 0 | S-P en échec → formule (Δ = 20) | A² + 2AB + B² (refusée) ; formule d'emblée (acceptée) |
| F5 | Somme de deux carrés | x² + 4 = 0 | S-P en échec → formule (Δ = −16 < 0, S = ∅) | A² − B² (refusée) ; formule d'emblée (acceptée) |
| F6 | Id. rem. avec B = √k ou B fractionnaire | x² − 5 = 0 ; 9x² − 1/9 = 0 | A² − B² → produit nul | formule (acceptée) |
| F7 | Id. rem. qui marche aussi en S-P | t² + 20t + 100 = 0 | A² + 2AB + B² (la vérification 2AB écrite) | S-P (accepté) |
| F8 | Non unitaire, sans ME | 2x² + 13x + 15 = 0 | tâtonnement (r = −5, □ = 2, △ = 3) → produit nul | S-P (refusé : a ≠ 1) |
| F9 | Racine fractionnaire (D1 : aucune fraction cherchée) | 6x² + 5x + 1 = 0 (2.12 b) | tâtonnement en échec (±1) → formule (Δ = 1) | S-P (refusé : a ≠ 1) ; formule d'emblée (acceptée) |
| F10 | Pas de racine rationnelle | x² + x − 1 = 0 | S-P en échec → formule (Δ = 5, racines avec √5) | tâtonnement (refusé : a = 1) ; formule d'emblée (acceptée) |
| F11 | Degré 3 | x³ − x = 0 | ME (x) → A² − B² → produit nul | formule (refusée : degré 3) |
| F12 | Pas sous la forme « … = 0 » | 4(x − 2)² = 1 ; x² = 3x + 10 | tout ramener à gauche, sans développer → Id. rem. avec A = 2(x − 2), B = 1 (« car ») ; ramener → S-P | Id. rem. d'emblée (refusée) |
| F13 | Unitaire « simple » (témoin) | x² − 5x − 36 = 0 | S-P → produit nul | tâtonnement (refusé : a = 1) |
| F14 | Δ = 0 sans Id. rem. visible | 4x² + 12x + 9 = 0 (Id. rem.) ; 2x² + 4x + 2 = 0 (ME puis Id. rem.) | selon le cas | formule (acceptée) |
| F15 | Produit égal à un nombre non nul | (x + 1)(x + 3) = 15 | Développer (double distribution, E2) → ramener (x² + 4x − 12 = 0) → S-P → produit nul | Produit nul (refusé, QZ-07) |
| F16 | Facteur commun aux deux membres (2.12 e) | (x − 1)(2 − x) = (x − 1)(x + 3) | ramener sans développer, avec l'avertissement « Attention : on ne divise pas par (x − 1) … » (E3) → ME de (x − 1) → produit nul | Produit nul (refusé : second membre non nul) ; Développer (accepté s'il aboutit) |

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
  "question":   texte (« Et pour x² − 1 ? »)
  "boutons":    [cle]                       # QZ-04, ordre fixe de la phase
  "attendue":   cle                         # QZ-05 : la méthode du chemin du cours, tentative en échec comprise
  "acceptees":  {cle: remarque}             # QZ-05 : s_applique vrai, pas l'attendue
  "refusees":   {cle: explication}          # QZ-06, QZ-07 : une explication par bouton refusé
  "sous_questions": []                      # QZ-14, vide en première version
```

- `attendue` se lit dans `methode` : RAMENER → « Tout ramener à gauche », DEVELOPPER → « Développer », ME, les trois Id. rem., SP, TATONNEMENT,
  FORMULE → « Formule (Δ) », PRODUIT_NUL → « Produit nul ». Les étapes `delta_valeur` et `delta_nombre` ont leurs propres boutons (QZ-04).
- Après une tentative en échec, le moteur passe directement à `delta_valeur` (une étape `factoriser` / `FORMULE` n'existe que pour la formule
  choisie d'emblée, coefficients non entiers, D22) : `quiz_json` insère la question « … Et maintenant ? » (attendue FORMULE, sans ligne).
- Chaque bouton de `boutons` est dans exactement un des trois ensembles (`attendue`, `acceptees`, `refusees`) : vérifié par le validateur de sortie.
- `s_applique(methode, P)` et `appliquer(methode, P)` (une méthode seule, rédigée, ou None) portent sur un `Polynome` développé ; ils existent et
  sont testés depuis P1 et P2b.
- La concaténation des `lignes` de toutes les étapes **est** la chaîne de `second_degre.blocs` (invariant du § 5, testé) ; les cartes du quiz
  sont celles de `second_degre.cartes` (R1), badges de `resoudre_eq.TITRES`.
- L'onglet « Résoudre » et le quiz partagent donc `resoudre_equation` ; le quiz y ajoute seulement les questions, le classement des boutons et
  les explications.

## 5. Tests

- **Python (oracle)** : pour chaque famille, 200 graines : solutions = racines de l'oracle mpmath (`oracle.racines`), et aucune autre ; propriété
  et chemin de la famille vérifiés ; chaque bouton classé dans exactement un ensemble ; `attendue` = la méthode du chemin du cours (tentatives en
  échec comprises) ; chaque méthode de `acceptees` aboutit réellement (`appliquer` rend une factorisation qui se redéveloppe) ; aucune méthode de
  `refusees` n'aboutit ; la concaténation des `lignes` égale la chaîne de « Résoudre » pour la même équation, et les cartes celles de `cartes`.
- **Rédaction** : instantanés `quiz_json` sur les exercices 2.9 à 2.12 et une graine par famille (F1 à F16) ; textes au vouvoiement (R12),
  vocabulaire (SOC, 7c), notation suisse et ≈ (D13).
- **Pages** : un parcours complet au clic (2.9 a) ; une tentative en échec puis « Formule (Δ) » (2.12 b) ; deux erreurs puis réponse donnée ;
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

Questions ouvertes (06.11.2026, à trancher au chantier « S'entraîner ») :

- a. **Formule sur un facteur (E9)** : après une ME, le chemin écrit le produit nul **avant** Δ (Javet 2.17 c, 4x² + 2x + 2 = 0) ; la
  question « Et maintenant ? » d'après l'échec n'a alors pas « Formule (Δ) » pour étape suivante. Aucune famille ne tire ce cas.
- b. **Réponse écrite avant la question** : les lignes de l'échec finissent par « on utilise la formule » (D3, E7), puis le quiz demande
  « Et maintenant ? ».
- c. **« … : il faut la formule. »** (QZ-07, § 9 de `decisions.md`) est faux quand une Id. rem. ou une ME vient avant (4x² − 9).
- d. **Ce qui « aboutit » en phase `ramener`** : aucune fonction du moteur ne le dit pour « Développer » (F12, F16) ni pour « Tout ramener à
  gauche » (F15) ; `s_applique` ne lit pas les formes structurées (pour F16, `s_applique("ME", −2x² + x + 1)` met −1 en évidence, pas x − 1).
- e. **Explications sans modèle** : S-P refusé sans couple hors du chemin (x² − 5, F6), formule refusée en degré 3 (F11), produit nul refusé
  en F16 (modèle « ramenez d'abord » repris ci-dessus).
- f. **Étapes sans bouton** : `FRACTIONS` (R2) et `isoler` (degré 1).
