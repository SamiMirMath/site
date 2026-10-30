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
| 3 | Simplexe | à faire |
| 4 | Autres outils, un commit par outil | à faire |
| 5 | Fin : suivi complet, commande de fusion, résumé | à faire |

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
