# Chantier « Clavier intégré » — suivi

Demande du 02.11.2026, d'après les retours d'élèves : sur téléphone, ils veulent taper les nombres avec des touches de la page, sans ouvrir le clavier du système.
Demande complétée le même jour : **partout où un élève saisit une formule ou un nombre, un clavier numérique apparaît**.
Branche `clavier-integre`, créée depuis `main` (b4dad03 : fusion de `mise-en-page-fluide` et du correctif d'étiquettes du simplexe). Rien n'est poussé ni fusionné.
Un commit par partie ; suite complète verte (`python3 tests/lancer.py complet`, code de retour lu sans pipe) avant chaque commit.
Plan : `/Users/samimir/.claude/plans/pasted-content-id-ec9d-chantier-polymorphic-zebra.md`.

**Reprise après compactage** : relire ce fichier, `git log --oneline main..HEAD`, `commun/composants.js` et `.css`, puis reprendre à la première partie qui n'est pas « faite ».

## Inventaire des saisies (02.11.2026)

Toutes les pages du site ont été parcourues : seuls 7 écrans demandent à l'élève de saisir une formule ou un nombre.

| Écran | Champ | Couvert par |
|---|---|---|
| Ensemble de définition, Dérivée et variations, Limites et asymptotes, Étude complète | `#entree` (f(x) =) | partie 1 |
| Factorisation | `#entree` (Factoriser :) | partie 1 |
| Exponentielles et logarithmes | `#entree` (Résoudre :) | partie 1 |
| Programmation linéaire (simplexe) | champs `.champ-signe` (coefficients, second membres) | partie 2 |

Les autres champs (curseurs `type="range"`, cases à cocher) ne demandent pas de saisie. Les six pages à `#entree` passent par `monterOutil` (`commun/outil.js`) : un futur outil
reçoit le clavier tactile sans rien écrire de plus.

## Décisions

- **Clavier à 6 colonnes, comme une calculatrice** (rangées 1 à 3 identiques sur les six outils, seule la dernière rangée change) :
  `7 8 9 ( ) ⌫` / `4 5 6 × ÷ C` / `1 2 3 + − ^` / `0 , x ln eˣ √`. « × » insère `*`, « ÷ » insère `/`, « , » insère la virgule (les deux analyseurs acceptent `,` et `.` entre deux chiffres ; la virgule n'a aucun autre rôle).
- Factorisation : dernière rangée `0 , x`. Exponentielles et logarithmes : `0 , x = e ln` / `log logₐ √ % n t` / `Q C V` ; la touche « 10 » disparaît (les chiffres suffisent).
- **Pavé du simplexe** (partie 2) : la grille dessinée par l'enseignant, virgule à droite du 6, « / » à droite du 3, « Suivant ▶ » sur trois colonnes.
- **iOS** : `inputmode="none"` ; sur iPhone et iPad **en plus** `readonly` d'office (pas de vérification possible sur un vrai iPhone ici). « ABC » enlève les deux, « 123 » les remet.
- Sur tactile, le bouton « Calculer ▶ » de la page est caché (doublon avec celui du clavier) mais reste dans la page : les autres scripts le déclenchent toujours.
- Touches de 44 px de haut au moins ; de large dès 360 px (45 à 47 px) ; **40 px à 320 px** (filet de sécurité : la rangée de six touches tient dans l'écran sans défilement horizontal).

| Partie | Sujet | État |
|---|---|---|
| 1 | Clavier des outils à saisie de fonction | **faite** (suite complète verte : 914 + 105) |
| 2 | Pavé numérique du simplexe | **faite** (suite complète verte : 914 + 108) |
| 3 | Défilement sur les figures du simplexe | à faire |

## Partie 1 — clavier des outils à saisie de fonction

**Fichiers** : les six `*/index.html` (bloc `.clavier`), `commun/composants.js` (`estTactile`, `sansClavierSysteme`, `avecClavierSysteme`, `monterClavierTactile`), `commun/composants.css`
(rangée « ABC » + « Calculer ▶ », survol non collé), `commun/style.css` (6 colonnes, écart `clamp(3px, 1vw, 6px)`), `commun/outil.js` (montage, garde sur les touches d'action).

**Comportement** :
- Les touches existantes gardent leur comportement : insertion au curseur (elle remplace la sélection), ⌫, C. Le gestionnaire ne réagit plus qu'aux boutons `data-t` / `data-k` (les boutons « ABC » et « Calculer ▶ » ont le leur).
- Tactile (`matchMedia("(pointer: coarse)")`) : `#entree` reçoit `inputmode="none"` ; une 5ᵉ rangée « ABC » (2 colonnes) + « Calculer ▶ » (4 colonnes, libellé et état du bouton de la page : « Factoriser ▶ », « Résoudre ▶ ») est ajoutée.
  Une touche ne prend pas le focus (`mousedown` annulé) : le curseur reste dans le champ.
- Ordinateur : rien ne change (ni rangée, ni `inputmode`, ni `readonly`).

**Tests** :
- `tests/pages/test_clavier.py` (nouveau) : en émulation tactile à 390 px, `(x^2-1)/(x-3)` puis `e^(-x)/(4x)` tapés uniquement avec les touches, « Calculer ▶ », mêmes cartes qu'en saisie directe sur ordinateur ;
  « × » insère `*`, insertion au curseur, ⌫, virgule décimale comprise ; « ABC » / « 123 » sur Android (`inputmode`) et sur iPhone (`readonly`) ; « Calculer ▶ » suit le bouton de la page ; ordinateur inchangé ;
  de 320 à 1100 px, pas de défilement horizontal, touches de 44 px (40 px de large à 320 px), aucune touche hors de l'écran (clavier de 5 et de 7 rangées).
- `tests/pages/navigateur.py` : `ouvrir(..., tactile=True, agent=...)` (écran tactile émulé avant le chargement, agent utilisateur imposé : un Mac tactile émulé se déclare « MacIntel » avec des points de contact, comme un iPad) et `Page.toucher(sélecteur)` (appui du doigt).
- `tests/python/test_source_unique.py` : mêmes trois premières rangées et mêmes noms (`aria-label` fois, divisé par, virgule) sur les six pages.
- `tests/pages/test_comportement.py` : le clavier d'Exponentielles et logarithmes écrit « 10 » avec les touches 1 et 0.

**Écart rencontré** : `test_limites_exemples_et_rappel_a_360_px` (plafond de 6 s par fonction, Pyodide) a échoué deux fois sur ce Mac (7,8 s dans la suite complète, 6,2 s seul) puis a passé (5,9 s, 4,3 s, et suite complète verte) :
la machine était chargée (charge ≈ 111 pour 2 cœurs) et le clavier n'intervient pas dans ce calcul. Le plafond n'a pas été relevé. Si l'échec revient, c'est à l'enseignant de décider.
Les appuis du doigt sont asynchrones (le clic est fabriqué par le navigateur après coup) : les tests attendent l'effet de chaque appui (`attendre_valeur`, `attendre_etat`) au lieu de le lire aussitôt.

## Partie 2 — pavé numérique du simplexe

**Fichiers** : `commun/composants.js` (`monterPave`, option `pave` de `champSigne`), `commun/composants.css` (`.pave`, `body.avec-pave`, `--pave-h`), `simplexe/index.html` (champs `pave:true`, montage dans `demarrer()`, `lancer()` ferme le pavé),
`tests/pages/test_simplexe.py` (partie F), `docs/specifications/simplexe.md`.

**Comportement** (écran tactile seulement ; sur ordinateur, aucun pavé) :
- Pavé fixé en bas (`safe-area-inset-bottom`), 4 colonnes : `7 8 9 ⌫ / 4 5 6 , / 1 2 3 / / 0 [Suivant ▶]` ; touches de 48 px. Mêmes places que le clavier de la partie 1 pour 0–9, la virgule et ⌫ (la virgule est à droite du 6, comme sur la grille demandée).
- Il apparaît au focus d'un champ `.champ-signe`. Chaque touche modifie la valeur au curseur puis envoie un événement `input` : le champ prévient la page, l'état `S` est à jour comme après une frappe.
- Le signe reste sur le bouton du champ (pas de touche « − ») ; toucher ce bouton garde le pavé ouvert, et la touche suivante écrit dans le même champ.
- « Suivant ▶ » : champ suivant dans l'ordre de lecture (fonction économique, puis chaque contrainte de gauche à droite, second membre compris) ; après le dernier, le pavé se ferme.
- Fermeture : toucher en dehors du pavé et des champs, lancement du calcul, après le dernier champ.
- Le champ actif reste visible : la page gagne en bas la hauteur du pavé (`--pave-h`) et le bloc du champ est amené à l'écran avec `scroll-margin-bottom`.

**Défaut trouvé par le test** : le défilement visait l'`input` alors que la marge `scroll-margin-bottom` est sur le bloc `.champ-signe` ; le champ restait sous le pavé. Corrigé (`amener()`).

**Tests** (`test_simplexe.py`, partie F) : écran de 390 × 420 px (le pavé couvre la moitié) : un problème 2D complet (f et trois contraintes, avec « 1,5 » et « 7/2 ») rempli uniquement avec le pavé et « Suivant ▶ » ; valeur du champ ET état `S`
vérifiés après chaque touche ; le champ actif est au-dessus du pavé ; le pavé se ferme après le dernier champ et rend la place ; lancement et solution exacte (`optimum_exact`) ; le bouton de signe garde le pavé ouvert ;
un toucher dehors et le lancement le ferment ; aucun pavé sur ordinateur (`inputmode="decimal"` conservé).

**Écart rencontré** : `test_clavier.py::test_a_…` a échoué deux fois dans la suite complète (jamais seul) : l'appui du doigt sur « C » juste après un calcul était perdu, la page faisant encore un défilement doux vers le corrigé
(Chrome avale un appui synthétique donné pendant un défilement). Ce n'est pas un défaut de la page : l'élève ne touche pas pendant que la page défile. `Page.toucher` (`tests/pages/navigateur.py`) attend maintenant que la page soit
immobile (6 mesures identiques de suite, à 50 ms) avant d'appuyer. Contrôle : les tests du clavier passent 4 fois sur 4 avec 3 processus qui saturent le processeur.
