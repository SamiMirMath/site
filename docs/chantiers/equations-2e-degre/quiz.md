# Onglet « S'entraîner » de l'outil Équations du 2e degré : spécification

**Statut (05.11.2026) : accepté sur le principe** ; dépend des décisions du chantier (D1–D14 encore à valider). Seule exigence pour le
1er chantier : les étapes structurées du § 4. L'onglet sera un chantier séparé.

Proposition du 04.11.2026.
Décisions de l'enseignant du 04.11.2026 : un onglet dans l'outil du 2e degré ; un quiz « évolutif » qui fait construire la résolution étape par étape ; les
recommandations QZ-05 (méthode juste mais pas dans l'ordre), QZ-06 (deux essais) et « niveau 2 plus tard » (QZ-14) sont acceptées.

Références, qui font foi pour la rédaction : corrigés de l'enseignant `Id_rem.pdf` (exercices 2.9 et 2.10) et `tatonement.pdf` (2.11 et 2.12), polycopié
Javet 1MRenf (chap. 2, § 2.2 à 2.4, la formule en 5e méthode), tous dans `docs/reference/equations-2e-degre/`. Décisions de l'audit
(`audit-etape0.md`, § 5) reprises telles quelles : D1 (tâtonnement), D2 (formule en 5e méthode), D4 (tableau S-P), D5 (étiquettes), D6 (vérification 2AB),
D7 (« 6 = 0 impossible »), D8 (x² − k par Id. rem. avec B = √k), D9 (rédaction de Δ), D13 (≈ à 3 décimales, notation suisse), D14 (ordres).

## 1. Objectif et public

- **Objectif** : l'élève apprend à **choisir la méthode**, dans l'ordre du cours : ME → Id. rem. → S-P → tâtonnement → formule (Δ), puis le produit nul.
  Le quiz ne montre pas une résolution : l'élève la construit, une décision à la fois, et voit la chaîne du corrigé s'allonger à chaque bonne réponse.
- **Public** : 1M (1Ms, 1Mr), 1C et 2C, les seuls niveaux de l'outil. Une seule rédaction pour les trois : produit nul avec le facteur constant écrit
  « 6 = 0 » et marqué « impossible » (D7). Pas de bouton de filière.

## 2. Règles

**QZ-01. Place.** Deux onglets en tête de l'outil : « Résoudre » (par défaut) et « S'entraîner » (composant commun `monterOnglets`, `commun/composants.js`).
Changer d'onglet ne perd ni la saisie de « Résoudre » ni la partie en cours de « S'entraîner ». `?onglet=entrainement` ouvre directement le quiz.

**QZ-02. Source unique.** Le quiz ne contient **aucune réponse écrite à la main**. Le moteur du 2e degré (`moteur/second_degre.py`, partie P3) produit la résolution
sous forme d'**étapes structurées** (§ 4) ; l'onglet « Résoudre » les affiche toutes, l'onglet « S'entraîner » les dévoile une à une en posant une question à chacune.
Conséquence : le quiz ne peut pas contredire la résolution, et les mêmes tests (oracle) valident les deux.

**QZ-03. Déroulé d'une partie.**
1. Une équation est tirée (§ 3) et affichée seule, avec la question « Par quoi commencez-vous ? ».
2. L'élève choisit un bouton (§ 2, QZ-04).
3. **Bonne réponse** (la méthode du cours) : « ✓ » et une phrase courte ; la ou les lignes correspondantes s'ajoutent à la chaîne, avec leur étiquette
   (« ME », « Id. rem. A = x, B = 1 »), et, s'il y en a, le texte qui les précède dans le corrigé (choix de la méthode, « Vérification : 2AB = … ✓ », tableau S-P,
   lignes du tâtonnement).
4. La question suivante porte sur ce qui reste à faire : « Et pour x² − 1 ? », « Le produit est factorisé. Et maintenant ? ».
5. La partie se termine sur `S = {…}` encadré, avec le bilan de la partie (QZ-08) et les boutons « Nouvelle équation » et « Voir dans Résoudre ».

Exemple de référence (2.9 a) :

| Question | Bonne réponse | Ajouté à la chaîne |
|---|---|---|
| Par quoi commencez-vous ? | ME | `6x² − 6 = 0 ⇔ 6(x² − 1) = 0` · ME |
| Et pour x² − 1 ? | A² − B² | `⇔ 6(x + 1)(x − 1) = 0` · Id. rem. A = x, B = 1 |
| Le produit est factorisé. Et maintenant ? | Produit nul | `⇔ 6 = 0 (impossible) ou x + 1 = 0 ou x − 1 = 0 ⇔ x = −1 ou x = 1`, puis `S = {−1 ; 1}` |

**QZ-04. Les boutons proposés**, selon ce qui est à l'écran (toujours les mêmes à une phase donnée, pour ne pas souffler la réponse) :

| Phase | Boutons |
|---|---|
| Équation qui n'est pas sous la forme « … = 0 » | Tout ramener à gauche (… = 0) · ME · A² − B² · A² + 2AB + B² · A² − 2AB + B² · S-P · Tâtonnement · Formule (Δ) |
| Polynôme (ou facteur) à factoriser | ME · A² − B² · A² + 2AB + B² · A² − 2AB + B² · S-P · Tâtonnement · Formule (Δ) |
| Produit de facteurs du 1er degré (et constantes) = 0 | Produit nul · Développer · Formule (Δ) |
| Après « Formule (Δ) » : valeur de Δ | 3 ou 4 valeurs : la bonne et des erreurs typiques calculées (b² + 4ac, −b² − 4ac, b − 4ac), toutes distinctes |
| Après Δ : nombre de solutions | 2 · 1 · 0 |

- Les identités remarquables sont écrites en formules (KaTeX) sur les boutons.
- Quand il reste un facteur du 2e degré non factorisé (après « ME » sur x³ − 5x² + 6x, par exemple), la question suivante porte sur ce facteur seul
  (« Et pour x² − 5x + 6 ? ») avec les boutons de la phase « à factoriser ».
- « Diviser par la constante » n'est **jamais** proposé : ce n'est pas la rédaction des 1M, 1C et 2C (le facteur constant passe par le produit nul, D7).

**QZ-05. Méthode juste mais pas la première.** Si le choix de l'élève **s'applique** mais n'est pas la méthode du cours à ce moment (le S-P pour x² − 1, la formule
pour x² − 5x + 6), il est **accepté avec une remarque** : « Cela marche aussi, mais l'identité remarquable vient avant dans l'ordre du cours. » La partie continue
**par le chemin du cours** (la chaîne affichée reste celle du corrigé). L'étape est comptée « juste, pas dans l'ordre » (QZ-08).
- « S'applique » est décidé par **les mêmes fonctions de détection** que l'onglet « Résoudre », avec les restrictions du cours : une Id. rem. demande A et B
  lisibles comme dans le corrigé (A = kx avec k rationnel, B rationnel ou √k quand le terme en x est absent, D8) ; 48z² − 216z + 243 n'est donc **pas** une Id. rem.
  avant la ME (48 n'est pas un carré), et ce choix est une erreur.
- La formule s'applique à tout trinôme : la choisir alors qu'une autre méthode vient avant est toujours « juste, pas dans l'ordre », jamais une erreur.
- « ME » ne s'applique que s'il existe un facteur commun différent de 1 (ou −1 quand a < 0, comme le corrigé de 2.10).

**QZ-06. Erreur.** Un choix qui ne s'applique pas donne une explication **propre à l'équation et au choix** (QZ-07), en rouge, et l'élève réessaie (le bouton
choisi est grisé). Après **deux** erreurs sur la même question, la bonne réponse est donnée avec son explication, la chaîne avance, et l'étape est comptée « erreur ».

**QZ-07. Les explications.** Vouvoiement (R12), une ou deux phrases, avec les nombres de l'équation, jamais le nom d'une méthode interne (SOC, 7c). Elles sont
produites par le moteur avec l'étape, pas écrites dans la page. Modèles :

| Situation | Explication |
|---|---|
| Id. rem. ou S-P choisi alors qu'un facteur commun existe | « Avant tout, cherchez un facteur commun : 6x² et 6 sont tous les deux divisibles par 6. » |
| Fausse Id. rem. (les carrés sont aux bouts, mais pas 2AB) | « x² et 4 sont des carrés (A = x, B = 2), mais 2AB = 2 · x · 2 = 4x ≠ 6x : ce n'est pas une identité remarquable. » |
| Mauvaise des trois Id. rem. | « Le terme du milieu est négatif : c'est A² − 2AB + B². » ; « Il n'y a pas de terme en x : c'est A² − B². » |
| Somme de deux carrés prise pour A² − B² | « x² + 4 est une somme : A² − B² demande une différence. » |
| S-P choisi alors que a ≠ 1 | « Le S-P ne s'utilise que si le trinôme est unitaire (a = 1) ; ici a = 2. » |
| S-P choisi, a = 1, mais aucun couple d'entiers | « Aucun couple d'entiers n'a pour produit −1 et pour somme 1. » |
| Tâtonnement choisi alors que a = 1 | « Le trinôme est unitaire (a = 1) : le S-P est plus rapide. » (accepté avec QZ-05 s'il aboutit) |
| Tâtonnement choisi, aucune solution entière ni fractionnaire | « Aucun diviseur de −1 (ni fraction ±p/q) n'annule le trinôme : il faut la formule. » |
| Méthode de factorisation choisie avant de ramener à « … = 0 » | « Le second membre n'est pas nul : ramenez d'abord tout à gauche. » |
| Développer choisi devant un produit nul | « L'équation est déjà un produit égal à 0 : utilisez le produit nul. » |
| Valeur de Δ fausse | l'erreur typique nommée : « Attention au signe : Δ = b² − 4ac = (−5)² − 4 · 1 · 6. » |
| Nombre de solutions faux | « Δ = −3 < 0 : l'équation n'a aucune solution réelle. » |

**QZ-08. Score et bilan.** Rien n'est enregistré (ni compte, ni `localStorage`). La page tient un compteur pour la session : « Étapes réussies du premier coup : 7 / 9 ».
À la fin d'une partie, le bilan donne trois nombres : étapes réussies du premier coup (✓), étapes « justes, pas dans l'ordre » (QZ-05), erreurs (QZ-06).
Recharger la page remet le compteur à zéro.

**QZ-09. Fin de partie.** « Nouvelle équation » tire une autre famille (§ 3) que la précédente. « Voir dans Résoudre » passe à l'onglet « Résoudre » avec l'équation
saisie et calculée (même mécanisme que `?f=`).

**QZ-10. Rien de faux à l'écran.** Une équation n'est proposée que si le moteur la résout entièrement avec le garde-fou exact (produit redéveloppé en `Fraction` et
comparé aux coefficients, chaque solution substituée exactement). Sinon elle est rejetée **avant** l'affichage, et une autre est tirée (nombre d'essais borné ; au-delà,
une équation de la liste fixe des corrigés). Aucun message « ne conclut pas » ne peut apparaître dans le quiz.

**QZ-11. Mise en page.** Fluide, cible 390 px, filet de sécurité 320 px (SOC-19) : les boutons en grille de deux colonnes (une colonne sous 360 px si un libellé
déborde), cibles ≥ 44 px ; la chaîne reprend le CSS commun `.chaine` (grille lien | expression | étiquette, repli à deux colonnes) ; le tableau S-P est le type de
bloc commun prévu en P3. Après chaque réponse, le focus va à l'explication (`aria-live="polite"`) puis à la question suivante ; tout se fait au clavier.

**QZ-12. Impression.** L'onglet « S'entraîner » ne s'imprime pas (`no-print`) ; le bouton PDF reste propre à « Résoudre ».

**QZ-13. Partage.** Une partie a une URL `?onglet=entrainement&exo=<famille>-<graine>` (même principe que SOC, 2) : la même équation revient, ce qui sert aux tests et
permet à l'enseignant de projeter un cas précis.

**QZ-14. Niveau 2 (plus tard, hors de la première version).** Sous-questions après une bonne réponse : « Que mettez-vous en évidence ? » (6 · 3 · 6x · x),
« A = ? B = ? », « Quel nombre r annule le trinôme ? ». Le format des étapes (§ 4) les prévoit déjà, pour ne rien refaire.

## 3. Les équations : familles de pièges

Chaque famille est un générateur à coefficients au hasard (bornés : entiers de −12 à 12, au plus une fraction simple), plus les exercices des corrigés comme liste fixe.
Le générateur **vérifie** que l'équation tirée a bien la propriété de sa famille (sinon il retire, QZ-10). Tirage : familles équiprobables, jamais deux fois la même de suite.

| # | Famille | Exemple | Chemin du cours | Choix piège (refusé, ou accepté avec QZ-05) |
|---|---|---|---|---|
| F1 | ME cachée devant une Id. rem. | 48z² − 216z + 243 = 0 | ME (3) → A² − 2AB + B² → produit nul | Id. rem. d'emblée |
| F2 | ME qui rend le trinôme unitaire | 2z² + 24z + 64 = 0 | ME (2) → S-P → produit nul | tâtonnement |
| F3 | a = −1 | −x² + 5x − 6 = 0 | ME (−1) → S-P → produit nul | S-P d'emblée |
| F4 | Fausse Id. rem. | x² + 6x + 4 = 0 | Formule (Δ = 20) | A² + 2AB + B² |
| F5 | Somme de deux carrés | x² + 4 = 0 | Formule (Δ < 0, S = ∅) | A² − B² |
| F6 | Id. rem. avec B = √k ou B fractionnaire | x² − 5 = 0 ; 9x² − 1/9 = 0 | A² − B² → produit nul | formule |
| F7 | Id. rem. qui marche aussi en S-P | t² + 20t + 100 = 0 | A² + 2AB + B² (la vérification 2AB écrite) | S-P (accepté, QZ-05) |
| F8 | Non unitaire, sans ME | 2x² + 13x + 15 = 0 | tâtonnement (r = −5, △ = 3) → produit nul | S-P |
| F9 | Racine fractionnaire | 6x² + 5x + 1 = 0 | tâtonnement (x = −1/2, facteur 2x + 1) → produit nul | formule (acceptée, QZ-05) |
| F10 | Pas de racine rationnelle | x² + x − 1 = 0 | formule (Δ = 5, racines avec √5) | S-P |
| F11 | Degré 3 | x³ − x = 0 | ME (x) → A² − B² → produit nul | formule |
| F12 | Pas sous la forme « … = 0 » | 4(x − 2)² = 1 ; x² = 3x + 10 | tout ramener à gauche → (Id. rem. avec A = 2(x − 2) ; S-P) | Id. rem. d'emblée |
| F13 | Unitaire « simple » (témoin) | x² − 5x − 36 = 0 | S-P → produit nul | tâtonnement |
| F14 | Δ = 0 sans Id. rem. visible | 4x² + 12x + 9 = 0 (Id. rem.) ; 2x² + 4x + 2 = 0 (ME puis Id. rem.) | selon le cas | formule |

## 4. Interface du moteur (pour P3)

Le moteur expose une fonction de plus dans le manifeste, appelée **une seule fois par partie** (la page gère ensuite le dévoilement sans rappeler Python) :

```
quiz_json(exo)  ->  {"equation": tex, "etapes": [Etape], "solutions": [tex], "S": tex}
Etape = {
  "phase":      "ramener" | "factoriser" | "produit_nul" | "delta_valeur" | "delta_nombre",
  "question":   texte (« Et pour x² − 1 ? »),
  "boutons":    [cle]                       # QZ-04, ordre fixe de la phase
  "attendue":   cle                         # la méthode du cours
  "acceptees":  {cle: remarque}             # QZ-05 : s'applique, pas dans l'ordre
  "refusees":   {cle: explication}          # QZ-06 et QZ-07 : une explication par bouton refusé
  "lignes":     [lignes de chaîne + textes intermédiaires + bloc tableau S-P éventuel]   # ce qui s'ajoute après la bonne réponse
  "sous_questions": []                      # QZ-14, vide en première version
}
```

- Chaque bouton de `boutons` est dans exactement un des trois ensembles (`attendue`, `acceptees`, `refusees`) : vérifié par le validateur de sortie.
- `lignes` utilise les mêmes objets que l'onglet « Résoudre » (`moteur/chaine.py`) : la concaténation des `lignes` de toutes les étapes **est** la chaîne de « Résoudre ».
- L'onglet « Résoudre » et le quiz partagent donc `resoudre_polynome` ; le quiz y ajoute seulement le calcul de `acceptees` et `refusees`.

## 5. Tests

- **Python (oracle)** : pour chaque famille, 200 graines : solutions = racines de l'oracle mpmath (`oracle.racines`), et aucune autre ; propriété de la famille
  vérifiée ; chaque bouton classé dans exactement un ensemble ; chaque méthode de `acceptees` aboutit réellement (on l'applique et on compare au produit) ;
  aucune méthode de `refusees` n'aboutit ; la concaténation des `lignes` égale la chaîne de « Résoudre » pour la même équation.
- **Rédaction** : instantanés `quiz_json` sur les exercices des corrigés (2.9 à 2.12) et une graine par famille ; textes au vouvoiement (R12), vocabulaire (SOC, 7c),
  notation suisse et ≈ (D13).
- **Pages** : un parcours complet au clic (2.9 a) ; deux erreurs puis réponse donnée ; « juste, pas dans l'ordre » ; compteur ; « Voir dans Résoudre » ;
  `?onglet=entrainement&exo=…` ; navigation au clavier ; `test_largeurs` de 320 à 1100 px à chaque phase (`CONNUS` vide).

## 6. Place dans le chantier

Nouvelle partie **P5b « Onglet S'entraîner »**, après P5 (l'outil existe) et avant P10 (registre). P3 doit déjà produire les étapes structurées du § 4 : c'est la seule
contrainte que le quiz impose aux parties précédentes.

## 7. Questions (réponses de l'enseignant du 05.11.2026)

1. **Termes dans le désordre** (5 + x² − 6x = 0) : la chaîne écrit-elle une ligne « ⇔ x² − 6x + 5 = 0 » sans question, ou est-ce une étape « Ordonner » à choisir ?
   Les corrigés ne montrent pas ce cas. **Réponse : une ligne sans question** (sans étiquette).
2. **Après la formule** : faut-il aussi faire choisir les solutions (x₁, x₂ parmi des valeurs proposées), ou les afficher directement après « 2 · 1 · 0 » ?
   **Réponse : les solutions sont affichées directement en première version.**
3. **Liste fixe** : quels exercices des corrigés et du polycopié Javet faut-il garder tels quels dans le tirage (en plus des générateurs) ?
   **Réponse : les exercices 2.9 à 2.12 des corrigés de l'enseignant.**
