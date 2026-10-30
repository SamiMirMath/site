# Chantier « Programmation linéaire » (simplexe et méthode géométrique) — suivi

Demande du 30.10.2026, d'après trois retours d'élèves. Un commit par partie, suite complète verte avant chaque commit, rien n'est poussé.
Page : `simplexe/index.html` (autonome, sans Pyodide). Tests de page : `tests/pages/test_simplexe.py` (créé en A).

| Partie | Sujet | État |
|---|---|---|
| A | Aucun champ prérempli à l'ouverture | **faite** (commit A) |
| B | Clavier du téléphone : négatifs et fractions | **faite** (commit B) |
| C | Solution complète en défilement (au lieu d'« Étape suivante ») | à faire |

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

## À traiter ailleurs (hors chantier)

- Ticket 8 de `docs/taches.md` : échappement des attributs `value="${…}"` du formulaire (toujours ouvert).
