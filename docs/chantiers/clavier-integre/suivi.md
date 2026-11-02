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
| 3 | Défilement sur les figures du simplexe | **faite** (suite complète : 914 + 112 verts, **un seul échec de chronométrage, hors chantier** : voir ci-dessous) |
| 4 | Retours iPhone du 02.11.2026 : « ABC » et lenteur de l'aperçu | **faite** (suite complète verte : 914 + 115, y compris le chronométrage de Limites) |

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

## Partie 3 — défilement sur les figures (simplexe)

**Constat** : les figures de la « Solution » géométrique (`canvas.fig`) étaient déjà en `touch-action: pan-y` ; c'étaient `#cv` (algébrique : Visualisation graphique et Explorer) et `#cvp` (géométrique : Visualisation graphique)
qui étaient en `touch-action: none` partout, alors que `#cvp` n'a aucun geste et que `#cv` n'en a que dans deux cas.

**Changement** (`simplexe/index.html`) : `#cv` et `#cvp` passent en `pan-y` ; `#cv.manipulable` reste en `none`. La classe est posée par `majManipulable()` (appelée par `setMode`) : en 3D (rotation du polyèdre, en « Visualisation
graphique » comme en « Explorer ») et en « Explorer » 2D (glisser le point). Au passage : `Scene.attach()` retire les gestes d'une scène 3D précédente (ils restaient sur `#cv` après un lancement en 2D), et `pointercancel` arrête le glissement du point.

**Tests** (`test_simplexe.py`, partie G, doigt émulé à 390 × 500 px, glissement de 150 px) : sur une figure de la Solution géométrique, sur `#cv` en 2D « Visualisation graphique » et sur `#cvp`, la page défile ;
dans Explorer 2D le point bouge et la page ne défile pas, et la figure redevient défilable en quittant Explorer ; en 3D (Visualisation graphique et Explorer) le polyèdre tourne (`yaw`, `pitch`) et la page ne défile pas ;
une scène 2D n'a plus les gestes d'une scène 3D précédente. Sensibilité vérifiée : avec l'ancienne règle `none`, le même glissement laisse la page à 282 px au lieu de 471 px.
`tests/pages/navigateur.py` : `Page.glisser(sélecteur, dx, dy)` (glissement d'un doigt), qui partage avec `toucher` l'attente d'une page immobile.

**Entorse à la règle « jamais de commit si un test échoue », accordée par l'enseignant le 02.11.2026 pour ce seul commit** : `test_comportement.py::test_limites_exemples_et_rappel_a_360_px`
(plafond de 6 s par fonction, Pyodide) échoue sur ce Mac, toujours sur `ln(x^2-3)/(2-x)` : 7,8 s, 8,1 s et 7,6 s dans trois suites complètes de la branche (3 échecs sur 6), 4,3 à 6,2 s seul.
**Indépendant du chantier** : une copie de `main` sans aucun de ces changements l'échoue aussi (5,2 s ; 6,9 s ; 7,3 s, mesures du même jour) ; la CI (Linux) le passe en 0,7 s ; le clavier et les figures n'interviennent pas dans ce calcul.
Les 5 nouveaux tests de la partie 3 et tout le reste de la suite (914 Python, 112 pages) sont verts. Le plafond n'a pas été modifié ; à reprendre séparément (mesure plus stable, ou machine moins chargée).

## Ce qui change pour l'élève

Sur téléphone et tablette (écran tactile), partout où il saisit une formule ou un nombre :
- **Outils à saisie de fonction** (Ensemble de définition, Dérivée et variations, Limites et asymptotes, Étude complète, Factorisation, Exponentielles et logarithmes) : le clavier du téléphone ne s'ouvre plus. Les touches de la page, disposées
  comme une calculatrice (chiffres, virgule, × ÷ + − ^, parenthèses, ⌫ et C, puis les fonctions de l'outil), écrivent dans le champ, au curseur. Une rangée « Calculer ▶ » (ou « Factoriser ▶ », « Résoudre ▶ ») est juste en dessous ;
  « ABC » rouvre le clavier du téléphone pour une saisie inhabituelle, « 123 » revient aux touches. La touche × écrit `*`, la virgule est comprise comme virgule décimale.
- **Programmation linéaire** : un pavé numérique (7 8 9 ⌫ / 4 5 6 , / 1 2 3 / / 0 « Suivant ▶ ») apparaît en bas de l'écran dès qu'on touche un champ ; « Suivant ▶ » passe au champ suivant, dans l'ordre de lecture, et ferme le pavé après le dernier.
  Le signe reste sur le bouton « + / − » du champ. Le champ actif reste visible au-dessus du pavé.
- **Figures du simplexe** : on fait défiler la page en glissant le doigt sur une figure ; seuls « Explorer » (glisser le point) et la 3D (faire tourner le polyèdre) gardent le geste pour la figure.
- **Ordinateur** : rien ne change (saisie au clavier, pas de pavé, pas de rangée « ABC »).

## Fin du chantier

Trois commits locaux sur `clavier-integre` (parties 1 à 3), rien n'est poussé ni fusionné. Fusion (à lancer par l'enseignant) :

```
git switch main && git merge --no-ff clavier-integre
```

À savoir avant de fusionner : (1) le test de chronométrage de la page Limites (plafond de 6 s) échoue sur ce Mac, sur `main` aussi (voir « Entorse » ci-dessus) ; (2) le clavier n'a pas pu être essayé sur un vrai iPhone : `readonly` sur iOS est une précaution
(Safari ouvre parfois son clavier malgré `inputmode="none"`) à vérifier sur un téléphone ; (3) à 320 px, les touches font 40 px de large (44 px de haut), le filet de sécurité.

## Partie 4 — retours de l'enseignant sur iPhone (02.11.2026)

Constat de l'enseignant, testé en local sur iPhone : « ABC » n'ouvre pas le clavier ; l'aperçu prend du temps.

**1. « ABC »** (`commun/composants.js`). Cause probable : après toute touche de la page, le champ garde le focus (en lecture seule) ; `focus()` sur un champ déjà focalisé ne fait rien et iOS n'ouvre son clavier que pour un focus
donné dans le geste de l'élève. Correctif : `blur()` puis `focus()` dans le même geste, `readonly` et `inputmode` retirés avant le focus ; « 123 » fait `blur()` (le clavier se ferme) puis remet le champ muet. Le `mousedown` n'est plus annulé
sur « ABC » (le navigateur fait son travail). Test : le geste produit bien `blur` puis `focus`, champ ni muet ni en lecture seule au moment du focus. **iOS lui-même n'est pas testable ici : à confirmer sur l'iPhone.**
Si le clavier ne s'ouvre toujours pas : prochaine piste = ouvrir le clavier avec un champ de saisie réel (un second `input` visible pour la saisie inhabituelle) plutôt que de basculer les attributs du même champ.

**2. Aperçu.** Mesures sur ce Mac (processeur ralenti ×1, ×4, ×6 : aucune différence sur le worker) :
- **En régime établi, l'aperçu est instantané** : 150 ms de pause volontaire (anti-rebond), 5 à 7 ms de calcul Python, 10 ms d'affichage.
- **Le retard est au chargement.** Aucun aperçu ne part tant que Python n'est pas prêt (`appelPy` attend `pret`) ; tout ce qui a été tapé avant arrive d'un coup. Décomposition du démarrage (copie locale de Pyodide) :
  `loadPyodide` 5,1 à 6,4 s (le gros du temps : réseau, compilation WebAssembly) ; import des modules du site 0,25 à 0,7 s ; **installation des roues SymPy 0,8 à 1,0 s puis `import sympy` 0,6 à 0,9 s, qui bloquent le worker**.
  Le worker ne fait qu'une chose à la fois, et la demande « SymPy » partait juste après l'initialisation, **avant** le premier aperçu : celui-ci attendait 1,5 à 2 s de plus (plus sur un téléphone).
- **Correctif** (`commun/moteur-python.js`, `commun/outil.js`) : SymPy ne se charge qu'après une pause de frappe (700 ms sans activité), au plus tard 8 s après le démarrage de Python, ou tout de suite si un calcul en a besoin
  (`hater()`, déjà prévu par `sympyAvant` et `besoin_sympy`). Mesure avant/après, mêmes touches tapées pendant le chargement : **premier aperçu à 9,1 s → 5,3 s** (−3,8 s, soit −40 %).
- Test : `test_t40_l_apercu_ne_attend_pas_sympy` (sur les 4 outils à SymPy) ; il échoue sur l'ancien code (vérifié sur une copie).

**Pistes mesurées, non faites (à décider)** :
- *Aperçu en JavaScript, sans Python* : instantané dès l'ouverture de la page, mais il faut réécrire en JavaScript l'analyse de trois grammaires (ensemble_def, factorisation, exp_log) et les garder identiques au Python (risque d'aperçu faux : à protéger par un test de parité sur tout le corpus).
- *`loadPyodide` (5 à 6 s)* : cache du navigateur, hébergement de Pyodide avec le site (voir `docs/choix-techniques.md`), ou chargement progressif.
- *Précompiler les modules Python du site* (0,25 à 0,7 s de compilation à chaque ouverture) comme les roues SymPy.

**Suite complète de la partie 4 : entièrement verte** (914 Python, 115 pages), y compris `test_limites_exemples_et_rappel_a_360_px` qui échouait dans les suites précédentes de la branche.
Ce test n'a pas été modifié ; il passe ici parce que SymPy ne se charge plus pendant que la page Limites est utilisée (la mesure reste une mesure de machine : à surveiller).
