# Chantier « Mise en page fluide et modulaire » — suivi

Demande du 30.10.2026 (simplexe + tout le site), d'après les retours d'élèves sur iPhone : formulaires trop larges, coupures de lignes au hasard,
figures trop chargées, bouton « Étape suivante » trop loin.
Branche `mise-en-page-fluide` (créée depuis `main` après vérification : `refonte-redaction-3m` d3cce68 et les commits du simplexe 53d09a6, cf896a1,
e1f25ef, c9fd212 sont dans `main`). Rien n'est poussé ni fusionné. Un commit par phase, un commit par outil en phase 4 ; suite complète verte
(`python3 tests/lancer.py complet`, code de retour lu sans pipe) avant chaque commit.
Plan détaillé : `/Users/samimir/.claude/plans/pasted-content-id-3a8a-chantier-sparkling-tulip.md`.

**Reprise après compactage** : relire ce fichier, `git log --oneline main..HEAD`, puis reprendre à la première phase qui n'est pas « faite ».

## Décisions

- Contrainte du simplexe : au plus deux lignes dès 390 px (2D et 3D) ; une contrainte 3D fait exactement deux lignes à 390 px.
- L'accueil (`index.html`) est hors chantier : seuls les 7 outils du registre sont balayés et migrés.
- Les « xfail » du balayage sont un tableau `CONNUS` strict dans `tests/pages/test_largeurs.py` (la CI lance `unittest discover`, qui ne connaît pas xfail par outil).
- Noms d'axes : dans les figures de la **méthode géométrique** seulement, « x₁ / x₂ » devient « x / y » (comme le reste de cette méthode) ; la méthode
  algébrique garde x₁ / x₂. Autorisé par l'enseignant le 30.10.2026.
- Hauteur variable du canvas (3d) : la conversion écran → coordonnées doit rester exacte ; test d'appui sur un sommet (Explorer, 390 et 1100 px).
- Passage en module ES : test qui ouvre chaque page modifiée, lance un exemple et échoue sur toute erreur de console ou exception non attrapée.

| Phase | Sujet | État |
|---|---|---|
| 0 | Branche, conditions, suivi | **faite** (inclus dans le commit de la phase 1) |
| 1 | Règle et composants communs (`composants.css`, `composants.js`) | **faite** (suite complète verte : 911 + 80) |
| 2 | Test de balayage des largeurs (`test_largeurs.py`), rapport initial | **faite** (suite complète verte : 911 + 89) |
| 3 | Simplexe | **faite** (suite complète verte : 911 + 99) |
| 4 | Autres outils, un commit par outil | **faite** (6 outils, voir le tableau de la phase 4) |
| 5 | Fin : suivi complet, commande de fusion, résumé | **faite** |

## Phase 1 — règle et composants communs

- Règle : `docs/specifications/socle-commun.md`, section « Mise en page fluide » (sous « Visuel et mobile ») ; renvoi depuis R14 de `docs/guide-redaction.md`.
- `commun/composants.css` : `.champ-signe` (+ `.membre`), `.onglets`, `.carte-etape`, `.bouton-flottant`, `.insecable`, `.flux`, `.conteneur-fluide`, `.cadre-fluide`.
  Aucune largeur d'écran en pixels. Le bouton flottant de `style.css` (`button.flottant`) n'est pas encore remplacé : c'est fait en phase 4 (premier outil).
- `commun/composants.js` (module ES) : `monterOnglets`, `champSigne`.
- Test statique : `tests/python/test_composants.py`.

## Phase 2 — test de balayage des largeurs

- `tests/pages/test_largeurs.py` : une méthode par outil (6 outils à cartes, la filière M de Exponentielles et logarithmes, le simplexe) + un auto-test du
  script de mesure. Chaque outil : ouvrir, lancer un exemple, mesurer à 320, 360, 375, 390, 430, 768 et 1100 px. Outils à cartes : deux états (première carte,
  avec le bouton flottant visible ; corrigé complet). Simplexe : formulaire 2D, 3D, solution 3D, solution / pas à pas / explorer en 2D, méthode géométrique
  (formulaire, solution, pas à pas). Durée : environ 50 s pour les 8 méthodes en local.
- Critères : `debordement` (la page défile horizontalement), `hors-ecran`, `cible-44` (≤ 430 px), `insecable-coupe`. Sont des « cibles » : `button`, `input`
  (hors `hidden`), `select`, `textarea`, `summary`, `[role=tab]` ; les liens ne sont pas comptés (liens dans le texte). Une case à cocher est mesurée par son étiquette.
- **xfail** : tableau `CONNUS` strict (voir l'en-tête du test). `BALAYAGE_RAPPORT=<fichier>` écrit le rapport complet sans rien affirmer.
- **Console** (ajout du 30.10.2026) : le pilote (`tests/pages/navigateur.py`) enregistre maintenant `page.erreurs` (exceptions non attrapées, erreurs du journal du navigateur
  — ressource ou module introuvable —, `console.error`). Le même parcours échoue si cette liste n'est pas vide (hors icône de l'onglet et ressources extérieures).
  Aucune erreur sur les 8 pages avant migration.

### Rapport initial (30.10.2026, avant toute migration)

Aucun débordement de page, aucun élément hors de l'écran, aucun `.insecable` (il n'en existe pas encore) ; à 768 et 1100 px, tout passe sauf Étude complète.
Les échecs sont :

| Outil | Critère | Largeurs | Éléments |
|---|---|---|---|
| Ensemble de définition | cible-44 | 320–430 | 20 boutons d'exemple (33,8 px), `#tout` et `#pdf` (40,8 px), résumé « Rappel » (24,8 px) |
| Dérivée et variations | cible-44 | 320–430 | 12 boutons d'exemple, `#tout`, `#pdf`, résumé « Rappel » |
| Limites et asymptotes | cible-44 | 320–430 | 14 boutons d'exemple, `#tout`, `#pdf`, 2 résumés (« Rappel de la méthode », « Rappel : les asymptotes ») |
| Étude complète | cible-44 | 320–430 | 8 boutons d'exemple, `#tout`, `#pdf`, `#zoomMoins`, `#zoomPlus`, `#zoomReset` (40,8 px) |
| Étude complète | **debordement** | 320, 360, 375, 390, 768 | la page mesure 417 px de large (768 px : 783 px), uniquement en « corrigé complet » ; élément à identifier en phase 4 |
| Exponentielles et logarithmes (3C) | cible-44 | 320–430 | 12 boutons (exemples et sélecteur 3C / 2M, 33,8 à 40,8 px), `#tout`, `#pdf`, une case à cocher (20,8 px), résumé |
| Exponentielles et logarithmes (filière M) | cible-44 | 320–430 | idem sans la case à cocher |
| Factorisation | cible-44 | 320–430 | 8 boutons d'exemple, `#tout`, `#pdf`, résumé |
| Simplexe | cible-44 | 320–430 | 42 éléments : choix de méthode, 2 / 3 variables, maximiser / minimiser, exemples, onglets, boutons de commande |

Lecture : les corrections de cible tactile sont communes aux 6 outils à cartes (une règle dans `commun/style.css`, faite avec le premier outil de la phase 4) ;
le simplexe est traité en phase 3 ; seul Étude complète demande un diagnostic de débordement.

## Phase 3 — simplexe (`simplexe/index.html`)

**Chargement.** La page charge `commun/composants.css`, et un petit `<script type="module">` importe `commun/composants.js`, expose `window.Composants` et appelle
`demarrer()`. Le script principal reste **classique** : ses variables globales (`S`, `ST`, `PS`…) sont lues et écrites par les tests de page (17 appels), qu'un module
aurait silencieusement cassés. Le test de console (phase 2) vérifie qu'aucune erreur ne vient de ce chargement.

**Formulaire.** Chaque coefficient et chaque second membre est un `.champ-signe` (`champNombre` s'appuie sur `Composants.champSigne`) ; plus aucun « + » écrit en dur.
Blocs `.insecable` : `[signe + champ + variable]`, `(i)` et `f =` collés au premier terme, `[≤ + second membre + ✕]` en un bloc. Rangées `.flux`. Aucune largeur d'écran codée :
`@media 920px`, `.lab` 190 px, `.num` 30 px, champs en px et `.sol` 780 px remplacés (`min(100%, 12rem)`, `auto-fit`, `ch`, `rem`). À 390 px : 2D sur 2 lignes, 3D sur exactement 2 lignes
(marge de 16 px avec la police de ce Mac ; 3 lignes à 360 px, ce que le filet de sécurité autorise). Toutes les cibles font au moins 44 px de haut (`button{min-height:44px}`, curseurs).

**Onglets** : « Solution » | « Visualisation graphique » | « Explorer » (algébrique), « Solution » | « Visualisation graphique » (géométrique), `role="tablist"`, flèches, Début, Fin.
« Gradient » reste masqué (`AFFICHER_GRADIENT = false`) et n'est pas dans l'ordre des flèches. **Texte modifié** (nécessaire, l'onglet change de nom) : « Faites tourner le polyèdre dans l'onglet
Visualisation graphique. » ; le titre « Solution complète » des cartes est inchangé.

**Solution algébrique** : texte seul (une `.carte-etape` par étape, aucun canvas), toujours depuis le programme initial avec Dantzig (`enregistrements(true, true)`), indépendante des
pivots choisis dans la visualisation graphique. Lien « Voir sur le graphique » dans chaque carte : rejoue le chemin de Dantzig jusqu'à ce pivot et fixe la sous-étape. **Changement de
comportement** : jusqu'ici la vue reprenait le chemin choisi par l'élève (le suivi du chantier « Programmation linéaire » le disait voulu) ; `docs/specifications/simplexe.md` est mis à jour.
L'impression « toutes les étapes » reste sur le chemin de l'élève.

**Solution géométrique** : garde ses figures. Noms d'axes **x / y** dans ses figures (autorisé le 30.10.2026) ; la méthode algébrique garde x₁, x₂, x₃.

**Figures.** Marge des données 8 % (au lieu de 16 %), marges en pixels réduites aux graduations ; hauteur du canvas = hauteur de la figure (2D : de 0,5 à 1,1 largeur, 3D en 4:3).
Étiquettes posées par ordre de priorité (`Scene.placerPx`) : 1 + 8 directions à 3 distances, en évitant points, textes et noms d'axes ; rendu en deux passes pour connaître tous les points
(sommets et point mobile) avant de poser les étiquettes. « f = … » ne chevauche plus ni un sommet ni un nom d'axe ; vérifié par `test_simplexe.py` sur tous les exemples du site, pas à pas complet,
Explorer, 3D en rotation, 390 et 1100 px.

**Deux défauts trouvés en écrivant le test d'appui (votre ajout 2)** :
1. La bordure de 1 px du canvas décalait la conversion écran → coordonnées, et, en `border-box`, la hauteur affichée était 2 px plus courte que le dessin (léger écrasement vertical). Corrigé :
   `ptSouris` retire la bordure et la hauteur CSS ajoute la bordure.
2. `clampPoint` laissait le point sur place quand l'appui tombait à peine hors de la région (d'un arrondi) et que le point était déjà sur un bord : un appui sur un coin ne déplaçait pas le point depuis
   le sommet voisin. Il projette maintenant sur les contraintes violées (repli : l'ancienne recherche le long du segment). Comportement un peu différent hors zone : le point glisse le long du bord.
Le choix d'un sommet par appui existe dans le mode « Gradient », masqué : même fonction `ptSouris`, couverte par l'appui d'Explorer (le test vérifie que l'onglet est masqué).

**Test fiabilisé** : `test_a_lancer_a_vide…` rechargeait la page puis cliquait sans attendre le nouveau document (course latente révélée par le chargement en module) ; il ouvre maintenant une page neuve.

**Tests ajoutés** (`test_simplexe.py`, partie E) : lignes de contrainte (≤ 2 dès 390 px, 3D = 2 à 390), « Modifier le problème » restitue tout (deux méthodes, signes, ≤/≥, valeurs), « Solution » identique après des
choix non-Dantzig, « Voir sur le graphique » ouvre le bon pivot et la bonne sous-étape, appui sur chaque sommet et au centre (Explorer, 390 et 1100 px), figure qui remplit son cadre et canvas à la
bonne hauteur, étiquettes sans chevauchement (deux méthodes), axes x₁/x₂ ou x/y, flèches du clavier sur les onglets. L'entrée `simplexe` de `CONNUS` est retirée : le balayage ne trouve plus aucune faute.

**Reste, hors périmètre** : en 3D, les trois étiquettes de flèches (« x₃↑ : +8 »…) se touchent encore (elles ne sont pas dans les étiquettes écartées) ; le polyèdre 3D reste petit quand il est mince ;
`touch-action:none` sur les canvas empêche le défilement de la page au doigt sur la figure (socle : « un glissement vertical sur un graphique fait défiler la page »).

## Phase 4 — outils à cartes (un commit par outil)

Outils, dans l'ordre : Limites et asymptotes, Étude complète, Ensemble de définition, Dérivée et variations, Exponentielles et logarithmes, Factorisation.

| Outil | État | Commit |
|---|---|---|
| Limites et asymptotes (+ socle commun des outils à cartes) | **faite** (911 + 99) | 11120fd |
| Étude complète | **faite** (911 + 99) | 216f9cd |
| Ensemble de définition | **faite** (rien à migrer) | e26359d |
| Dérivée et variations | **faite** (rien à migrer) | 6c27392 |
| Exponentielles et logarithmes | **faite** (912 + 99) | eac8a5b |
| Factorisation | **faite** (rien à migrer) | 28bac75 |

### Limites et asymptotes, et socle commun (premier commit de la phase 4)

`commun/outil.js`, `commun/rendu.js` et `commun/style.css` sont partagés : le premier outil migré porte donc les changements communs aux 6 outils, ce qui retire d'un coup toutes les entrées `cible-44`
de `CONNUS`.
- Les 6 pages chargent `commun/composants.css` (après `style.css`, avant leur `<style>`) ; `test_style_commun.py` l'exige.
- **Cibles tactiles** : `button{min-height:44px}` dans `style.css` (boutons d'exemple, `#tout`, `#pdf`, sélecteur de méthode, zoom du graphique), résumés « Rappel » (`padding:10px 0`), case à cocher de l'option (`.option{min-height:44px}`).
- **Bouton flottant** : `#suivantFlottant` prend la classe `.bouton-flottant` (les règles `button.flottant` et `--flottant-*` sont retirées de `style.css`, elles vivent dans `composants.css`). Même comportement :
  visible seulement s'il reste des cartes, même action que `#suivant` (qui reste en place), défilement doux jusqu'à la nouvelle carte, place réservée sous les cartes (`#cartes{padding-bottom}`).
- **Cartes** : `rendreCarte` et `rendreErreur` ajoutent `.carte-etape` (marges intérieures `clamp(10px, 3vw, 18px)` au lieu de 22 / 26 px fixes : un peu plus serré sur ordinateur). `.final` devient `.card.final`
  pour garder sa bordure verte. Les instantanés ignorent désormais la classe `carte-etape` (classe de mise en page, comme `cache`) : **les références ne changent pas d'un octet** (aucun texte mathématique touché).
- Limites : aucun style local à remplacer (`details ol/li`, `.rappel` sont propres à la page) ; ses formules et tableaux longs défilaient déjà dans leur propre bloc.

### Étude complète

Débordement de page diagnostiqué (417 px à 320–390 px, 783 px à 768 px, uniquement en « corrigé complet ») : KaTeX ajoute à chaque formule une copie MathML invisible en `position:absolute`. Comme les blocs
qui défilent (`.etape`, `.res`, `.cond .c`, `.enonce`, `.tsigne`, `.apercu`) n'étaient pas positionnés, ce MathML n'était **pas rogné** par eux : il étendait la zone défilable *de la page*. Le correctif
(`position:relative` sur ces blocs) existait déjà pour les blocs de Limites (`.bh`, `.vals`, `.enc-c p`…) ; il est étendu aux blocs communs dans `commun/style.css`. Même cause, même cure pour tous les outils : le test de
balayage n'ouvre qu'un exemple par outil, d'autres formules larges pouvaient donc déborder ailleurs. L'entrée `etude-complete` de `CONNUS` est retirée : **`CONNUS` est vide**.
Aucun autre changement de l'outil (pas de style local, pas de largeur codée).

### Contrôle de tous les exemples (une fois, hors CI)

Le test de balayage n'ouvre qu'un exemple par outil. Un script jetable a mesuré **tous** les exemples de chaque page (82 au total : ED 20, Dérivée 12, Factorisation 8, Limites 14, Étude complète 8, Exponentielles 10 + 10 en filière M),
corrigé complet affiché, aux 7 largeurs, avec les mêmes quatre critères : **aucune faute et aucune erreur de console** sur l'arbre de 216f9cd. À refaire après tout changement des feuilles communes.

### Ensemble de définition

Aucune largeur d'écran codée ; ses seules règles locales (`.verif`, pastille du contrôle numérique) sont propres à son contenu et sans équivalent commun. Les cibles tactiles viennent du socle commun (20 boutons d'exemple à 44 px).
Balayage et 20 exemples : aucune faute. Rien à modifier dans la page.

### Dérivée et variations

Aucun `<style>` local ni largeur codée : l'outil n'utilise que la feuille commune (tableaux de signe et de variations défilants dans leur bloc, `position:relative` ajouté en Étude complète). Balayage et 12 exemples : aucune faute.

### Factorisation

Styles locaux (`details ol`, `.final .res`, `.final .c`) : mises en forme du contenu, sans largeur d'écran. Balayage et 8 exemples : aucune faute. Rien à modifier dans la page.

### Exponentielles et logarithmes

Seule page qui avait une largeur d'écran codée : `@media (max-width:820px)` sur les chaînes de ⇔ (`.chaine`). Remplacée par `@container (max-width: 47rem)` : le bloc `.etape` qui contient une chaîne est un conteneur
(`.etape:has(>.chaine){container-type:inline-size}`, sélecteur propre à la page ; un `container-type` sur tous les `.etape` aurait écrasé ceux qui sont dans des boîtes à largeur ajustée). La disposition suit donc la place de
la carte, pas l'écran : trois colonnes (⇔, expression, propriété) quand le bloc fait au moins 752 px, deux colonnes (propriété sous l'expression) sinon, comme avant (même seuil pour l'ancienne mise en page :
750 px de bloc à 820 px d'écran). Vérifié à 1100 (3 colonnes, 1030 px), 900 (3 colonnes, 830 px), 800 (2 colonnes, 730 px) et 390 (2 colonnes, 333 px). `.prop` : `max-width:min(22em,100%)`.
Navigateurs sans `:has()` (avant iOS 15.4) : la requête ne s'applique pas, la disposition à trois colonnes reste et défile dans son bloc.
Garde ajoutée : `test_style_commun.py` interdit toute requête `@media` ou `@container` en pixels dans le `<style>` local d'un outil (simplexe compris).

## Phase 5 — fin

**État.** Phases 0 à 5 faites sur la branche `mise-en-page-fluide` (10 commits depuis `main`, du 30.10.2026 : fade6af … eac8a5b). Suite complète verte avant chaque commit de code (dernier passage : 912 tests Python, 99 tests de pages,
code de retour 0, sans pipe). `main` n'a pas été touché, rien n'est poussé ni fusionné. Les commits « Ensemble de définition », « Dérivée et variations », « Factorisation » et celui du contrôle des exemples ne contiennent que de la
documentation : le code testé est celui de 216f9cd.

**`xfail` restants (`CONNUS` dans `tests/pages/test_largeurs.py`) : aucun.** Le tableau est vide ; il reste strict (un nouvel échec fait échouer la suite, et une entrée corrigée y ferait échouer aussi).

**Ce qui reste, et qui n'est pas dans ce chantier.**
- Simplexe 3D : les trois étiquettes de flèches (« x₃↑ : +8 »…) se touchent encore au départ ; le polyèdre est petit quand il est mince.
- Simplexe : `touch-action:none` sur les canvas empêche de faire défiler la page en glissant sur la figure (le socle demande l'inverse hors Explorer).
- Le mode « Gradient » (choix d'un sommet par appui) est masqué : sa conversion est la même que celle d'Explorer, testée ; il n'a pas de test propre tant qu'il est masqué.
- « Exactement deux lignes » pour une contrainte 3D à 390 px dépend des chasses de police : 16 px de marge avec la police de ce Mac. Si la CI (Linux) a des chiffres plus larges, ce test peut demander un ajustement (largeur du champ ou marges).
- Le balayage de la CI n'ouvre qu'un exemple par outil ; le contrôle de tous les exemples (82) est un script jetable, à refaire après un changement des feuilles communes.
- Le débordement par le MathML caché de KaTeX est corrigé pour tous les blocs qui défilent ; tout **nouveau** bloc `overflow-x:auto` doit porter `position:relative` (à retenir dans `docs/specifications/socle-commun.md`).
- Non vérifié sur un vrai iPhone ni dans la CI GitHub (les tests ont tourné en local, Chrome sur Mac). `:has()` (Exponentielles) demande iOS 15.4 ou plus.

**Fusion, si vous validez** :
```
git switch main && git merge --no-ff mise-en-page-fluide
```

### Ce qui change pour l'élève, outil par outil

- **Tous les outils à cartes** : les boutons d'exemple, « Tout afficher », « Télécharger le corrigé », le sélecteur de méthode, le zoom du graphique, les « Rappel » et la case d'option font au moins 44 px de haut
  (touchables au pouce) ; « Étape suivante ▶ » flotte en bas à droite, toujours sous le pouce, et la page défile en douceur jusqu'à la nouvelle carte ; les cartes ont des marges qui s'adaptent à l'écran.
- **Programmation linéaire (simplexe)** : un bouton « + / − » collé à chaque champ, pas de coupure au milieu d'un terme (« (1) + 3 x₁ + 4 x₂ » puis « ≤ 4200 ✕ » à la ligne, en entier) ; deux lignes par contrainte sur iPhone ;
  onglets « Solution », « Visualisation graphique », « Explorer » ; « Solution » est un texte à suivre, sans figure, toujours depuis le départ avec Dantzig, avec un lien « Voir sur le graphique » dans chaque étape ; figures plus
  grandes, hauteur adaptée, « f = … » et les numéros de sommets ne se recouvrent plus ; dans la méthode géométrique, les axes s'appellent x et y ; un appui sur un coin de la figure (Explorer) place le point sur ce coin.
- **Limites et asymptotes** : cibles tactiles et bouton flottant (socle commun) ; rien d'autre.
- **Étude complète** : la page ne dépasse plus de l'écran en « corrigé complet » (elle mesurait 417 px sur un écran de 390 px).
- **Ensemble de définition, Dérivée et variations, Factorisation** : cibles tactiles et bouton flottant (socle commun) ; aucune autre modification.
- **Exponentielles et logarithmes** : les chaînes de ⇔ se mettent sur deux colonnes selon la place de la carte et non selon la largeur de l'écran (sur tablette en largeur réduite ou fenêtre étroite aussi).
