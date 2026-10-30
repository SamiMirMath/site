# Chantier « Programmation linéaire » (simplexe et méthode géométrique) — suivi

Demande du 30.10.2026, d'après trois retours d'élèves. Un commit par partie, suite complète verte avant chaque commit, rien n'est poussé.
Page : `simplexe/index.html` (autonome, sans Pyodide). Tests de page : `tests/pages/test_simplexe.py` (créé en A).

| Partie | Sujet | État |
|---|---|---|
| A | Aucun champ prérempli à l'ouverture | **faite** (commit A) |
| B | Clavier du téléphone : négatifs et fractions | à faire |
| C | Solution complète en défilement (au lieu d'« Étape suivante ») | à faire |

## A — Aucun champ prérempli

- `S = formulaireVide()` : fonction économique vide, 3 contraintes vides (≤), 2 variables, « Maximiser », méthode algébrique (inchangée).
- Les boutons « Remplir avec un exemple » remplissent seulement au clic (comportement inchangé).
- Messages d'erreur (vouvoiement) : « Fonction économique vide : entrez au moins un coefficient non nul. » ;
  « Il faut au moins une contrainte : remplissez au moins une ligne (coefficients et second membre). » (précisé).
- « Modifier le problème » garde la saisie (le formulaire est seulement masqué) ; un redessin du formulaire aussi (testé).
- Tests (360 px et 1100 px) : formulaire vide, exemple au clic, messages à vide dans les deux méthodes, saisie gardée.

## À traiter ailleurs (hors chantier)

- Ticket 8 de `docs/taches.md` : échappement des attributs `value="${…}"` du formulaire (toujours ouvert).
