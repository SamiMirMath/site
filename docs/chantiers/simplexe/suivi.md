# Chantier « Programmation linéaire » (simplexe et méthode géométrique) — suivi

Demande du 30.10.2026, d'après trois retours d'élèves. Un commit par partie, suite complète verte avant chaque commit, rien n'est poussé.
Page : `simplexe/index.html` (autonome, sans Pyodide). Tests de page : `tests/pages/test_simplexe.py` (créé en A).

| Partie | Sujet | État |
|---|---|---|
| A | Aucun champ prérempli à l'ouverture | **faite** (commit A) |
| B | Clavier du téléphone : négatifs et fractions | **faite** (commit B) |
| C | Solution complète en défilement (au lieu d'« Étape suivante ») | **faite** (commit C) |

## A — Aucun champ prérempli

- `S = formulaireVide()` : fonction économique vide, 3 contraintes vides (≤), 2 variables, « Maximiser », méthode algébrique (inchangée).
- Les boutons « Remplir avec un exemple » remplissent seulement au clic (comportement inchangé).
- Messages d'erreur (vouvoiement) : « Fonction économique vide : entrez au moins un coefficient non nul. » ;
  « Il faut au moins une contrainte : remplissez au moins une ligne (coefficients et second membre). » (précisé).
- « Modifier le problème » garde la saisie (le formulaire est seulement masqué) ; un redessin du formulaire aussi (testé).
- Tests (360 px et 1100 px) : formulaire vide, exemple au clic, messages à vide dans les deux méthodes, saisie gardée.

## B — Négatifs et fractions au clavier du téléphone

- Les champs numériques (fonction économique, coefficients et seconds membres, deux méthodes, 2D et 3D) passent de `inputmode="decimal"` à
  `inputmode="text"` avec `autocomplete="off" autocorrect="off" autocapitalize="off" spellcheck="false"`.
- `lireNombre` : tout tiret de clavier vaut le signe moins (U+002D, U+2212, U+2013, U+2014, U+2010, U+2011) ; virgule et point restent des séparateurs décimaux.
- Aide sous le formulaire : « Nombres : 3, −2, 0,5 ou 1/2 ; case vide = 0. » suivie de la phrase propre à chaque méthode.
- Recherche de `inputmode` dans tout le dépôt (`.html`, `.js`, `.py`, `.md`) : seuls les deux champs du simplexe (l. 400 et 406 avant la modification)
  avaient `inputmode`. **Aucun autre outil n'a de champ `decimal` ou `numeric`** : les autres outils utilisent un champ texte (`#entree`), rien à corriger.
- Tests : `lireNombre` (−3, –3, —3, ‐3, ‑3, -1/2, -0,5…), refus des écritures ambiguës, attributs de tous les champs dans les trois configurations,
  saisie par insertion de texte (comme un clavier de téléphone) puis lancement, à 360 px et 1100 px.

## C — Solution complète en défilement

- **Onglets** : méthode algébrique « Solution complète » (par défaut, première position) · « Pas à pas » · « Explorer » ; méthode géométrique : « Solution complète » (par défaut) · « Pas à pas ».
  Le pas à pas (animation, choix de la variable entrante, lecture auto, curseur des parallèles) est inchangé. Les onglets portent `aria-pressed` ;
  Entrée ou Espace sur un onglet l'active (le raccourci « étape suivante » du clavier ne le détourne plus).
- **Méthode algébrique** : `construireSolution()` prend `enregistrements(true)` (la source du rapport imprimable) et, pour chaque enregistrement, les blocs de
  `blocsPivot(…)` : une carte par bloc (étapes 0 à 6), la dernière est la carte finale (optimum ou non borné). Au lancement c'est le chemin de Dantzig ;
  si l'élève a déjà avancé dans le pas à pas, la vue reprend son chemin puis Dantzig (comme le rapport, c'est voulu : « toujours identiques »).
- **Méthode géométrique** : `construireSolutionPara()` : une carte par élément de `etapesPara()`. `etatPara(k, c, contact, manuel)` est l'état de dessin pur
  d'un pas (`etatDessinPara()` l'appelle avec l'état courant : pas à pas inchangé). `drawPara` accepte `fantomes` (positions intermédiaires du glissement).
- **Figures** : une par changement de dessin, pas deux identiques de suite. Algébrique : étape 0 (sommet et arêtes), 1 (arête entrante), 2 (pointillé vers le sommet
  suivant ; omise si non borné car identique à la 1), 3 (déplacement) ; les étapes 4 à 6 gardent la figure de la 3. Géométrique : une par carte.
  Chaque figure a son `<canvas class="fig">` (`Scene(…, fixe=true)` : pas de rotation à la souris), à la largeur de la carte et au `devicePixelRatio`,
  dessiné quand il approche de l'écran (`IntersectionObserver`, marge 300 px ; `data-dessine`), redessiné au redimensionnement et au changement de thème.
  3D : orientation courante figée, phrase « Faites tourner le polyèdre dans l'onglet Pas à pas. » dans l'en-tête de la vue.
- **Mise en page** : en-tête (problème et nombre d'étapes), cartes, résultat dans un encadré (`.verdict`), lien « ↑ Haut de la page ». Colonne de 780 px au plus ;
  les équations longues défilent dans leur propre bloc (`.eq`), jamais la page.
- `enregistrements(true)` est désormais plafonné à 500 pivots (comme `resoudre`) : la vue s'ouvre au lancement, une boucle sans fin figerait la page.
- **Impression** : le bouton « Imprimer / PDF de toutes les étapes » est inchangé (rapport à images). Le réutiliser pour la vue défilante n'est pas simple
  (le rapport est paginé, une image par pivot) : non fait, comme prévu par la demande.
- Tests (`tests/pages/test_simplexe.py`, 360 px et 1100 px) : Exemple 2D, Exemple 3D, les trois exemples de la méthode géométrique, un cas non borné
  de chaque méthode et un cas à infinité de solutions ; valeur optimale recalculée par énumération exacte des sommets (fractions) ; nombre de cartes =
  nombre de `.bloc` du rapport imprimable ; rendu paresseux, figures non vides et deux à deux différentes ; thème sombre et largeur ; « Pas à pas » jusqu'au résultat.

## À traiter ailleurs (hors chantier)

- Ticket 8 de `docs/taches.md` : échappement des attributs `value="${…}"` du formulaire (toujours ouvert).
