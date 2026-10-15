# Découpage en tâches

Chaque tâche fait **un commit (ou une petite série)**, laisse le site en ligne fonctionnel, et
se termine par sa vérification. Commande de référence pour les tests Python :

```sh
uv run -q --no-project --python 3.12 --with sympy==1.13.3 python -m unittest discover -s tests/python
```

Légende : **Dépend** = tâches à terminer avant ; **Bloquée** = question ouverte de
[a-valider.md](a-valider.md).

## Déjà fait (13.10.2026)

| Commit | Contenu |
|---|---|
| `88b7b0f` | `_config.yml` (docs/ et tests/ non publiés), `__pycache__/` ignoré |
| `14e0ee8` | Bug 1 : dérivée de x^(p/q) + premier test |
| `70e6b1e` | Bug 2 : fausse asymptote verticale, genre « saut » + test |
| `a9b2a6e` | Bug 3 : étapes de la dérivée cohérentes avec le résultat + test |
| `43685f1` | T01 : instantanés des moteurs Python |
| `8689cac` | T02 : tests de propriétés (oracle haute précision) |
| `155afba` | T03 : intégration continue GitHub Actions |
| `43f760b` | T04 : manifeste des fichiers Python par outil |

## Phase B — réalisé (14.10.2026)

| Tâche | Commit(s) | Contenu |
|---|---|---|
| T05 | `1b55deb`, `8d23921` | plantage sur constante nulle ; pas de seuil 1e-12 sur les fractions exactes |
| T07 | `80fb69c` | graphique figé au dézoom (EC-03) ; message discret si une fenêtre échoue |
| T08 | `44d30cf`, `4977248` | limite non déterminée jamais prise pour une asymptote ; « limite non déterminée automatiquement » |
| T08b | `21830d7` | formulations Q7 (trou, pas de limite) ; genre `sans_limite` |
| T06 | `1519e12` | tableau Q3 : ED de f', valeur de f sans barre, extrema (i) et (ii) |
| T06b | `ad7552c` | fonction constante : « 0 » et flèche → ; zéro isolé (x³) inchangé |
| T07b | `f98f63e` | plus de faux « désaccord » près d'une racine double (seuil 1e-14) |
| — | `3793909` | JSON strict (`allow_nan=False`) ; plus de `Infinity` (x^(2/3)) |
| — | `b548253`, `a53bb49` | racine réelle pour x^(p/q), q impair : pont SymPy, atomes racine q-ième exacts |
| T10 | `6a1be82`, `aff5872` | f' en un quotient, coefficients entiers, racines ; narration de f' = 0 cohérente |
| — | `e5dc17a`, `d347c5e` | énoncé « x^{3/2} = √(x³) » ; étape « on multiplie par k > 0 » |
| — | `ef9497f`, `16e992f`, `f73e5d7`, `4dd62f1` | tableau : zones hors ED hachurées, double barre de valeur interdite centrée, sur toutes les lignes |
| — | `b45265a` | aperçu de la saisie : pas d'erreur rouge pendant la frappe, plus de message obsolète |
| — | `c2a6e53` | dérivée de u^α, α constant irrationnel : α·u^(α−1)·u' ; tableau de signes de l'ED aligné (`2bb4da8`) |
| — | atome au degré 1 | ln, exp ou racine isolés étape par étape (sans « On pose t ») ; substitution réservée au degré ≥ 2 ; réciproques « (exp est croissante) », « (ln est croissante) » |
| — | C5 (`19d9a3e`) | ED de x^α (α constant, simplifié exactement), [0 ; +∞[ pour α irrationnel > 0 |
| — | C6 | vocabulaire élève (aucune méthode interne, « transcend… » interdit), détails techniques en console |

## Reste à faire dans la phase B

- **T09 — croissance comparée** (débloquée, Q1) : incluse dans T29 (commit L6).
- **T29 — Limites et asymptotes rédigées étape par étape** (décidé le 14.10.2026, Q9) : la méthode du
  cours à la place du résultat seul, dans l'outil Limites et dans l'Étude complète. Moteur
  `limites-asymptotes/limites_asymptotes.py` ; la valeur de chaque limite et les asymptotes ne changent
  pas (garde-fou : repli honnête si la rédaction n'aboutit pas). Un commit par étape, chacun avec sa suite verte :
  L0 documents ; L1 opérations et composition, forme indéterminée nommée, garde-fou, conclusion de chaque
  borne ; L2 valeur interdite (numérateur, signe du dénominateur, ℓ/0^±) ; L3 mise en évidence (polynômes,
  fractions rationnelles, 0/0) ; *relecture de l'enseignant* ; L4 expression conjuguée ; L5 mise
  en évidence sous une racine (les « termes dominants » sont supprimés : ni ∼, ni « équivalent », ni
  « se comporte comme », décidé le 15.10.2026) ; L6 croissance comparée (T09) ; L7 Bernoulli-L'Hôpital ; L8 asymptote oblique ; L9 encadré
  « Rappel de la méthode ». Critères : LA-10 à LA-20.
- **T06c — limites contre les doubles barres, dans l'Étude complète seulement** (décidé le 14.10.2026) :
  sur la ligne f(x), écrire la limite contre la barre, du côté de l'ED (−∞ à gauche de la colonne −2
  pour ln(x²−4)) ; « limite non déterminée automatiquement » si SymPy ne conclut pas ; la Dérivée
  garde les flèches seules. À spécifier dans `etude-complete.md` avant de commencer (limites en ±∞ aux
  extrémités de l'ED : non, seulement contre les barres).
- Tableau de signes de l'Ensemble de définition : la valeur interdite n'est marquée que sur la ligne du
  quotient (les lignes de facteurs montrent « 0 ») ; à aligner sur la Dérivée si l'on veut la barre sur
  toute la colonne (à décider).
- Dérivée d'une puissance d'exposant constant irrationnel : faite (α·u^(α−1)·u'). Deux restes
  d'écriture, à traiter plus tard : (1) un coefficient s'écrit « −1 + ln 3 » (ordre de SymPy) au lieu de
  « ln 3 − 1 » ; (2) f' de x^√2·ln x reste un quotient non simplifié, (x·√2·x^(√2−1)·ln x + x^√2)/x, au lieu de
  x^(√2−1)(√2·ln x + 1).

## Phase A — Filet de sécurité

### T01 — Instantanés des moteurs Python
- **But** : figer la sortie actuelle de tous les moteurs, pour détecter toute régression.
- **Fichiers** : `tests/python/test_instantanes.py`, `tests/python/instantanes/*.json`.
- **Contenu** : pour chaque outil Python, les exemples et listes d'exercices des pages, plus les
  cas limites des spécifications ; régénération explicite seulement (`REGENERER=1`).
- **Vérification** : la suite passe ; modifier une phrase d'un moteur fait échouer le test qui
  la concerne (essai manuel puis retour en arrière).
- **Critères** : ED-01, DV-06, LA-06, EC-01 (partie instantanés).

### T02 — Tests de propriétés mathématiques
- **But** : vérifier les résultats indépendamment des moteurs.
- **Fichiers** : `tests/python/test_proprietes_*.py`, `tests/python/generateurs.py` (fonctions
  aléatoires avec graine).
- **Contenu** : ED comparé au contrôle numérique (≥ 1 000 fonctions) ; f' comparée à la dérivée
  numérique ; limites confirmées par sonde numérique ; factorisation redéveloppée = entrée et
  facteurs irréductibles.
- **Vérification** : la suite passe ; annuler localement `14e0ee8` la fait échouer.
- **Critères** : ED-02, DV-01, DV-05 (partie existante), LA-04, LA-05, FA-01, FA-02.

### T03 — Intégration continue
- **But** : lancer les tests à chaque push et pull request.
- **Fichiers** : `.github/workflows/tests.yml` (Python 3.12 + `sympy==1.13.3`, `unittest`) ;
  emplacement réservé pour Node (`node --test tests/js`) et les tests de pages.
- **Dépend** : T01.
- **Vérification** : exécution verte sur `main` ; sur une branche de test avec un test cassé
  volontairement, l'exécution est rouge.

### T04 — Manifeste des fichiers Python par outil
- **But** : une seule liste des fichiers que chaque page charge dans Pyodide.
- **Fichiers** : `moteur/manifeste.json`, `tests/python/test_manifeste.py`.
- **Vérification** : le test copie, pour chaque outil, uniquement les fichiers du manifeste dans un
  dossier temporaire et importe le module de l'outil avec succès ; il échoue si un fichier manque.

## Phase B — Bugs restants (après les tests, validés au point 1)

### T05 — Bug 5 : plantage sur constante nulle (`0.0`)
- **Fichiers** : `ensemble-definition/ensemble_def.py` (`valeur_constante`), test dédié.
- **Dépend** : T01.
- **Vérification** : ED-03, ED-08 (u⁰ = 1, ED de la base exigé : comportement actuel déjà conforme,
  à figer par un test) ; instantanés inchangés sauf `x^(2-2)`, `x^(1/2-1/2)`.

### T06 — Bug 4 : ED de f', extrema (i) et (ii), notation du tableau — **débloquée (Q3, 14.10.2026)**
- **Contenu** : étape « ED de f' » quand ED(f') ≠ ED(f) ; extremum (i) en un point intérieur de
  l'ED où f' change de signe même si f' n'y est pas définie ; extremum (ii) en toute borne fermée
  de l'ED, nature donnée par le sens de variation adjacent ; tableau : double barre sur la ligne
  f'(x), valeur f(a) sans barre sur la ligne f(x).
- **Fichiers** : `derivee-variations/derivee_variations.py`, `derivee-variations/index.html` et
  `etude-complete/index.html` (affichage d'une valeur dans la ligne f(x)), tests.
- **Dépend** : T01, T02.
- **Vérification** : DV-03, DV-04, DV-05, DV-09, DV-10 ; `test_aucun_extremum_manque` et
  `test_extrema_bornes_fermees` passent (retirer `@expectedFailure`) ; instantanés modifiés
  uniquement pour les fonctions concernées (relus un par un).

### T06b — Fonction constante dans le tableau (décidée le 14.10.2026, avec T06)
- **Contenu** : sur chaque intervalle où f' est identiquement nulle, « 0 » sur la ligne f'(x) et
  flèche horizontale → sur la ligne f(x), avec la valeur constante aux bornes appartenant à l'ED ;
  aucun extremum sur cet intervalle ; un zéro isolé de f' (x³) reste « 0 » avec ↗ ↗.
- **Fichiers** : `derivee-variations/derivee_variations.py`, `derivee-variations/index.html` et
  `etude-complete/index.html` (flèche →, message), `tests/python/test_tableau_variations.py`.
- **Dépend** : T06.
- **Vérification** : DV-11, DV-12, DV-13 ; instantanés modifiés uniquement pour x^(2-2) et x/√(x²).

### T07 — Bug 6 : graphique figé au dézoom
- **Fichiers** : `etude-complete/etude_complete.py` (`_echantillonner`), `etude-complete/index.html`
  (message en cas d'échec), test dédié.
- **Vérification** : EC-03 ; EC-04 (test de page, après T15).

### T07b — Faux « ⚠ désaccord » du contrôle numérique près d'une racine double — **priorité haute**
- **Constat** (trouvé par T02) : pour ln(x²−10x+25), 1/(x²−6x+9)…, l'ED est juste mais la page
  affiche « ⚠ Le contrôle numérique signale un désaccord près de x ≈ 5 ». Près d'un zéro double,
  `evaluer` arrondit à 0 une valeur ≈ 1e-12 (seuil anti-compensation de `ensemble_def.py`), et
  `verifier` conclut à tort que f n'est pas définie. L'élève voit un avertissement injustifié.
- **Fichiers** : `ensemble-definition/ensemble_def.py` (`verifier`, ou le seuil de compensation
  de `evaluer` utilisé par le contrôle), `tests/python/test_proprietes_ed.py`.
- **Dépend** : T01, T02.
- **Vérification** : `test_controle_numerique_sans_fausse_alerte` passe (retirer
  `@expectedFailure`) ; ED-07 ; `test_ed_conforme_oracle` et instantanés inchangés, sauf le
  contrôle affiché pour les fonctions à racine double.

### T08 — Limite non déterminée jamais prise pour une asymptote
- **Fichiers** : `limites-asymptotes/limites_asymptotes.py`, test dédié (SymPy simulé en échec).
- **Vérification** : LA-03.

### T08b — Vocabulaire des limites finies en une valeur interdite — **débloquée (Q7, 14.10.2026)**
- **Contenu** : remplacer « point de discontinuité » par « f n'est pas définie en a, mais sa limite
  y est finie (= ℓ) : pas d'asymptote verticale, trou dans le graphique en (a ; ℓ) » ; remplacer le
  genre « saut » par « limites à gauche et à droite différentes : f n'a pas de limite en a ; pas
  d'asymptote verticale » (nouveau nom de genre, ex. `sans_limite`).
- **Fichiers** : `limites-asymptotes/limites_asymptotes.py` (pôle rationnel, cas transcendant un
  côté, `_bilan_deux_cotes`), `limites-asymptotes/index.html` et `etude-complete/index.html`
  (`ligneAsymptote`), `tests/python/test_limites_deux_cotes.py`.
- **Dépend** : T01.
- **Vérification** : LA-02 (adapté), LA-08 ; instantanés régénérés, diff limité au vocabulaire et
  au nom du genre.

### T09 — Croissance comparée — **débloquée (Q1, 14.10.2026)**
- **Contenu** : ne citer la croissance comparée qu'en cas de forme indéterminée (∞/∞, 0·∞,
  ∞ − ∞ levée par factorisation) entre x^n (n > 0 réel) et e^(ax) (a > 0) ou ln, en ±∞ ou en 0⁺
  pour ln ; nommer la limite de référence utilisée.
- **Fichiers** : `limites-asymptotes/limites_asymptotes.py` (`_croissance_comparee`), test dédié.
- **Dépend** : T01, T08b.
- **Vérification** : LA-07 ; instantanés : seules les phrases de croissance comparée changent.

### T10 — Allègement des coefficients fractionnaires de f' — **faite** (`6a1be82`, `aff5872`)
- **Fichiers** : `derivee-variations/derivee_variations.py` (`_nettoyer`).
- **Vérification** : DV-07 ; DV-01 inchangé (valeurs).

## Phase C — Interface Python publique (ensemble_def.py intact)

### T11 — `moteur/noyau.py`
- **But** : réexporter sous des noms publics ce que les autres moteurs prennent au noyau.
- **Fichiers** : `moteur/noyau.py` ; imports de `derivee_variations.py`, `limites_asymptotes.py`,
  `etude_complete.py`, `factorisation.py` ; `moteur/manifeste.json` ; pages (fichier en plus à charger).
- **Dépend** : T01, T04.
- **Vérification** : test d'analyse syntaxique : aucun module hors `noyau.py` n'importe de nom
  commençant par « _ » depuis `ensemble_def` ; `git diff` vide sur `ensemble_def.py` ;
  instantanés inchangés.

### T12 — Format de sortie commun
- **Fichiers** : `moteur/sortie.py`, une fonction `resoudre()` par outil (adaptateur), test de schéma.
- **Dépend** : T11.
- **Vérification** : ED-06 et équivalents ; anciennes fonctions `*_json` inchangées (instantanés).

### T13 — Exercices avec graine
- **Fichiers** : `moteur/exercices.py` (gabarits validés), `exercice(niveau, graine)` par outil, tests.
- **Dépend** : T12. Gabarits acceptés (Q4, 14.10.2026) : pondérations conservées, racines
  distinctes et exactes (sauf réponse contraire à Q8 pour le carré parfait de la factorisation).
- **Vérification** : FA-03, SOC-05 (moteur) ; ED-05, DV-08 ; 200 graines × 4 niveaux × outil
  résolues exactement.

## Phase D — Pages communes

### T14 — `commun/style.css` (identité de l'accueil, contraste AA)
- **Fichiers** : `commun/style.css`, `tests/python/test_contrastes.py`.
- **Vérification** : SOC-03, ACC-05.

### T15 — Client Pyodide commun + tests de pages en CI
- **Fichiers** : `commun/moteur-python.js`, `commun/worker-pyodide.js`, `tests/pages/` (navigateur
  sans interface, CI seulement), migration pilote de `ensemble-definition/index.html`.
- **Dépend** : T04, T14.
- **Vérification** : SOC-04, SOC-06, SOC-13 sur l'outil pilote ; essai manuel sur téléphone.
- **Tests de pages à y intégrer** (CI seulement, Chrome sans interface via le protocole DevTools, décidé le
  14.10.2026) : aperçu de la saisie (SOC-16 : `ln(x)/x` au clavier et avec le bouton ln, pas de message
  rouge pendant la frappe, erreur après ≈ 0,5 s) sur les cinq pages ; rendu du tableau (DV-16 : double
  barre centrée, continue, à 380 px et sur ordinateur) ; message de repli du graphique (EC-04).

### T16 — `commun/outil.js` + `commun/rendu.js`, outil pilote
- **But** : page outil générique (saisie, aperçu, clavier, hasard, étapes, impression) pilotée
  par une config.
- **Dépend** : T12, T15.
- **Vérification** : SOC-01, SOC-02, SOC-07, SOC-09, SOC-10 sur l'Ensemble de définition ;
  [manuel] SOC-08.

### T17 à T20 — Migration des autres pages (une tâche par outil)
- T17 Dérivée, T18 Limites, T19 Étude complète (+ EC-04, EC-05, EC-06), T20 Factorisation.
- **Dépend** : T16. **Vérification** : mêmes critères SOC + critères de page de l'outil ;
  instantanés des moteurs inchangés.

### T21 — Factorisation : une carte par méthode
- **Dépend** : T12, T20. **Vérification** : FA-04, FA-05.

### T22 — Accueil : registre, sans-JS, contraste, animation sobre
- **Fichiers** : `commun/registre.json`, `index.html`, `tests/python/test_accueil.py`.
- **Vérification** : ACC-01 à ACC-08. Les liens `?methode=` de la 2e année ne sont posés qu'une
  fois T27 en ligne (la page doit d'abord comprendre le paramètre) ; d'ici là, 2C et 2Mr gardent
  le lien actuel `simplexe/`.

### T23 — Notation suisse
- **Fichiers** : tokeniseurs (`ensemble_def.py`, `factorisation.py`), `dec()`, `commun/nombres.js`,
  graduations du graphique.
- **Dépend** : T01. Milliers : ’ dès 4 chiffres, saisie de ' et ’ (Q5, 14.10.2026).
- **Vérification** : SOC-11, SOC-12.

## Phase E — Simplexe (en dernier, priorité faible)

### T24 — Extraire `simplexe/lp.js` et le tester (Node, CI)
- **Vérification** : PL-01, PL-05.
### T25 — Méthode géométrique exacte et notation suisse
- **Dépend** : T24. **Vérification** : PL-02, PL-03, PL-04.
### T26 — Suppression du code mort
- **Vérification** : PL-07 ; PL-05 inchangé.
### T27 — Style commun, en-tête, `?methode=` par filière
- **Dépend** : T14, T24. **Vérification** : PL-06, PL-08, PL-10, PL-11, PL-12, SOC-01, SOC-02 ; puis liens
  `?methode=` de l'accueil (ACC-08).
### T28 — Exercices au hasard du simplexe
- **Dépend** : T24, T25. Gabarits acceptés (Q4, 14.10.2026). **Vérification** : PL-09, PL-13, SOC-05.

## Plus tard (hors plan, si les tests tiennent)

- Découpage de `ensemble_def.py` en modules (`moteur/expr.py`, `poly.py`, `ensembles.py`…),
  vérifié par les instantanés et les propriétés.
- Auto-hébergement de Pyodide (coût dans [choix-techniques.md](choix-techniques.md)).

## Ordre conseillé

T01 → T02 → T03 → T04 (faites) → T05, T07, T08 (indépendantes) → T08b → T06 → T07b (priorité haute)
→ T09 → T11 → T12 → T13 → T14 → T15 → T16 → T17…T20 → T21, T22, T23 → T10 → T24…T27 → T28.

**Plus aucune tâche n'est bloquée** (Q1 à Q7 tranchées le 14.10.2026). Q8 (racine double du
carré parfait en factorisation) reste ouverte ; elle ne concerne qu'un gabarit de T13.
