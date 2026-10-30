# Outil « Programmation linéaire » (2e) — priorité faible, traité en dernier

URL : `/simplexe/` · page autonome en JS (pas de Pyodide, pas de KaTeX).

## Fonctionnel (actuel, conservé)

- Formulaire : méthode, nombre de variables (2 ou 3), objectif max/min, fonction économique,
  jusqu'à 8 contraintes ≤/≥ (x ≥ 0 sous-entendu) ; nombres entiers, décimaux (0,5) ou fractions (1/2).
- **Méthode géométrique (2C)** : 2 variables ; chaque contrainte : isoler y, deux
  points de la droite, côté admissible et vérification par un point test ; zone admissible et
  ses sommets ; famille de parallèles f = c ; sens de déplacement ; premier contact ; tableau
  des valeurs de f aux sommets ; cas non borné et infinité de solutions.
- **Méthode algébrique (2Mr/OS)** : dictionnaire du simplexe en fractions exactes
  (BigInt), variable entrante au choix (Dantzig par défaut), rapports, pivot animé, polygone ou
  polyèdre 3D, mode exploration ; phase 1 non traitée (message clair).
- **Onglets** (mise en page fluide, 30.10.2026) : « Solution » | « Visualisation graphique » (l'ancien « Pas à pas ») | « Explorer » (algébrique seulement), en
  `role="tablist"` avec les flèches du clavier ; après « Lancer », « Solution » est la vue par défaut.
  - **Méthode algébrique** : « Solution » est du texte seul (une carte par étape, **aucune figure**). Elle part toujours du programme initial et suit Dantzig,
    **quels que soient les pivots choisis** dans « Visualisation graphique ». Chaque carte a un lien « Voir sur le graphique » qui ouvre la visualisation
    graphique sur ce pivot et cette sous-étape (le chemin de Dantzig est rejoué depuis le départ). *(Avant le 30.10.2026, la vue reprenait le chemin choisi.)*
  - **Méthode géométrique** : « Solution » garde ses figures (une par étape, rendu paresseux), puisque la méthode est graphique ; axes nommés x et y
    (la méthode algébrique garde x₁, x₂, x₃).
- **Formulaire fluide** : chaque coefficient et chaque second membre est un bloc `.champ-signe` (bouton de signe + champ collés ; le champ montre la valeur absolue,
  l'état garde la valeur signée ; champ vide = 0). Blocs insécables : `[signe + champ + variable]`, `[≤ + second membre + ✕]` en entier, « (1) » et « f = »
  collés au premier terme. Dès 390 px, une contrainte tient sur deux lignes au plus (3 variables : exactement deux à 390 px).
- **Figures** : le cadre des données a 8 % de marge, la hauteur du canvas suit la figure (2D : entre 0,5 et 1,1 fois la largeur ; 3D en 4:3). Les étiquettes
  (« f = … », numéros et coordonnées des sommets, noms d'axes, graduations, « p = … ») sont posées par ordre de priorité en évitant les points et les textes déjà
  posés. La conversion écran → coordonnées (Explorer) tient compte de la bordure du canvas ; un appui à peine hors de la région place le point à l'endroit le plus proche.
- Impression : rapport dédié avec images.

## Répartition par filière (validé, Q2)

| Filière | Méthode | Lien depuis l'accueil |
|---|---|---|
| 2C | graphique | `simplexe/?methode=geometrique` |
| 2Mr (OS) | algébrique | `simplexe/?methode=algebrique` |
| 2Ms | — (pas d'outil de programmation linéaire) | — |

### Paramètre `?methode=` (validé)

La filière est un **guide, pas un verrou** : la comparaison des deux méthodes sert en cours.

- `?methode=geometrique` ou `?methode=algebrique` **présélectionne** la méthode de la filière
  (et un exemple de cette méthode).
- L'autre méthode reste **toujours accessible** par un sélecteur discret, par exemple
  « Autre méthode : méthode algébrique (2Mr/OS) ».
- Le lien ne change **que la présélection, jamais ce qui est possible** : avec ou sans paramètre,
  les mêmes méthodes, options et exemples sont disponibles.
- Valeur de `?methode` **absente ou inconnue** : comportement actuel (méthode algébrique et
  « Exemple 2D » présélectionnés), sans message d'erreur.
- **3D uniquement avec la méthode algébrique**, comme aujourd'hui (le bouton « 3 variables » est
  désactivé avec la méthode géométrique ; passer en géométrique ramène à 2 variables).
- Libellés de la page inchangés : « 2C · Méthode géométrique » et « 2Mr/OS · Méthode algébrique ».
- **Exercices au hasard : oui**, générés avec graine pour chaque méthode, problèmes à données
  entières et solution exacte ; gabarits et niveaux acceptés le 14.10.2026 (Q4 de
  [../a-valider.md](../a-valider.md)), avec ces règles :
  - pondérations 35 % / 35 % / 20 % / 10 % ;
  - méthode algébrique, minimisation : f a au moins un coefficient négatif (sinon optimum
    trivial à l'origine) ;
  - niveaux facile et moyen : aucune égalité dans le test du rapport (pas de dégénérescence) ;
  - méthode graphique, très difficile : gabarits séparés « région non bornée, optimum fini »,
    « problème non borné » et « infinité de solutions ».

## Évolutions prévues

- Fonctions mathématiques pures dans `simplexe/lp.js` (fractions, pivot, sommets, région),
  testées par Node dans la CI ; interface dans `simplexe.js`.
- Méthode géométrique en **fractions exactes** pour les sommets et les valeurs de f (la classe
  `Fr` existe déjà) ; affichage en notation suisse.
- Contrainte de second membre 0 : point test choisi hors de la droite ; deuxième point de la
  droite distinct de l'origine.
- Suppression du mode « gradient » inactif (`AFFICHER_GRADIENT=false`) et de l'initialisation
  inutile de `ordonnerPlan`.
- Style, en-tête, pied de page communs ; paramètre `?methode=geometrique|algebrique`.
- Exercices au hasard (générateur JS avec graine dans `lp.js`, lien `?methode=…&exo=<niveau>-<graine>`).

## Critères d'acceptation

| Id | Critère | Vérif. |
|---|---|---|
| PL-01 | Pour 200 problèmes aléatoires à 2 et 3 variables (graine fixe), l'optimum du simplexe exact = le meilleur sommet obtenu par énumération exacte | [auto-js] |
| PL-02 | Méthode géométrique : sommets et valeur optimale exacts (fractions), égaux à PL-01 | [auto-js] |
| PL-03 | Contrainte `x − y ≤ 0` : le point test n'est pas sur la droite et la conclusion est juste ; aucun texte « (0 ; 0) et par (0 ; 0) » | [auto-js] |
| PL-04 | Aucun nombre affiché avec un point décimal ; milliers avec ’ | [auto-js] |
| PL-05 | Les 6 exemples actuels donnent les mêmes étapes et le même optimum qu'avant (instantanés) | [auto-js] |
| PL-06 | `?methode=geometrique` présélectionne la méthode géométrique ; `?methode=algebrique` la méthode algébrique | [auto-page] |
| PL-07 | Plus aucune référence à `AFFICHER_GRADIENT`, `rendreGrad`, `ctrlGrad` | [auto-py] (recherche texte) |
| PL-08 | Avec `?methode=geometrique` comme avec `?methode=algebrique`, l'autre méthode reste accessible en un clic et l'ensemble des méthodes, options et exemples disponibles est identique à celui de la page sans paramètre | [auto-page] |
| PL-11 | `?methode=` absent, vide ou inconnu (`?methode=xyz`) : même état initial qu'aujourd'hui (algébrique, « Exemple 2D »), aucune erreur dans la console | [auto-page] |
| PL-12 | Avec la méthode géométrique, « 3 variables » est désactivé ; passer de l'algébrique 3D à la géométrique ramène à 2 variables | [auto-page] |
| PL-09 | Exercices générés : déterministes pour une graine ; 200 graines × niveaux × méthode ont une solution exacte (ou un cas « non borné » / « infinité » voulu par le gabarit), vérifiée par énumération des sommets | [auto-js] |
| PL-13 | Exercices générés : minimisation algébrique ⇒ f a un coefficient négatif ; niveaux facile et moyen ⇒ aucun ex æquo dans aucun test du rapport ; les gabarits graphiques « région non bornée, optimum fini » et « problème non borné » produisent bien chacun leur cas (vérifié par énumération) | [auto-js] |
| PL-10 | Les libellés de la page et de l'accueil indiquent 2C → graphique et 2Mr/OS → algébrique ; aucune mention de 2Ms | [auto-py] |
