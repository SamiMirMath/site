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

- **T09 — croissance comparée** : **faite** (`f953e40`, L6 de T29).
- **T29 — Limites et asymptotes rédigées étape par étape** : **faite, L0 à L9** (16.10.2026) —
  L0 `b526701` ; L1 `fcb5bfb` ; L2 `350c891` ; L3 `a1f8e92` ; L4 `79040f4` ; L5 `fbc44c7` ; L6 `f953e40` ;
  L7 `0b4b14c` ; L8 `59f95f7` ; L9 `1bf807a`. Suites : rédaction minimale selon
  [guide-redaction.md](guide-redaction.md) (`c4604ce`, `de086aa`, `8c1fbc2`, `1957da2`), tableaux de signes
  R7 (`459feef`, `6034f68`), Ensemble de définition R10 (`5190d98`, `2c58766`), Dérivée R11 (`bb1640e`).
  Les « termes dominants » sont supprimés (décidé le 15.10.2026). Critères LA-10 à LA-20.
  *Relecture de l'enseignant* : faite (exemples Limites, Dérivée et Ensemble de définition relus pendant la rédaction allégée).
- **T06c — faite (`55a4730`, 16.10.2026) — limites contre les doubles barres et en ±∞ quand l'ED y va, dans
  l'Étude complète seulement** (décidé le 14.10.2026, ±∞ ajouté le 16.10.2026, spec dans `etude-complete.md`) :
  sur la ligne f(x), limite contre chaque double barre, du côté de l'ED (−∞ à gauche de la colonne −2 pour
  ln(x²−4)), et limite en −∞ / +∞ sous l'en-tête ; « ? » et une phrase si SymPy ne conclut pas ; une seule
  source de calcul (celle de la partie Limites), test sur le corpus (EC-10) ; la Dérivée garde les flèches
  seules, mais la double barre figure maintenant sur f'(x) à toute valeur interdite (trou compris).
- Tableau de signes de l'Ensemble de définition : **fait** (`2bb4da8`, `459feef`, `2c58766` : une ligne par
  facteur, barre simple pour un facteur non nul sur une colonne critique, double barre réservée aux valeurs interdites).
- Dérivée d'une puissance d'exposant constant irrationnel : **faite** (α·u^(α−1)·u' ; ordre « ln 3 − 1 » `dbb6d93` ;
  f' de x^√2·ln x en x^(√2−1)(√2 ln x + 1) `8cd50c3`).

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

### T11 — `moteur/noyau.py` — **faite** (`0e019bf`, 17.10.2026)
- **But** : réexporter sous des noms publics ce que les autres moteurs prennent au noyau.
- **Fichiers** : `moteur/noyau.py` ; imports de `derivee_variations.py`, `limites_asymptotes.py`,
  `etude_complete.py`, `factorisation.py` ; `moteur/manifeste.json` ; pages (fichier en plus à charger).
- **Dépend** : T01, T04.
- **Vérification** : test d'analyse syntaxique : aucun module hors `noyau.py` n'importe de nom
  commençant par « _ » depuis `ensemble_def` ; `git diff` vide sur `ensemble_def.py` ;
  instantanés inchangés.
- **Réalisé** : 58 noms réexportés ; `_sympy` → `charger_sympy`, `_SP` → `SYMPY`, `_analyser` →
  `analyser_complet` ; les quatre moteurs et leurs pages (sauf l'Ensemble de définition, qui n'importe
  pas le noyau) chargent `noyau.py` ; test `tests/python/test_noyau.py`. Les tests qui appellent
  `ensemble_def._…` directement sont inchangés (ils testent le noyau lui-même).

### T12 — Format de sortie commun — **faite** (`2a9353f` à `043dd73` + docs, 17.10.2026)
- **Fichiers** : `moteur/sortie.py`, une fonction `resoudre()` par outil (adaptateur), test de schéma.
- **Dépend** : T11.
- **Vérification** : ED-06 et équivalents ; anciennes fonctions `*_json` inchangées (instantanés).
- **Réalisé** : `moteur/sortie.py` (constructeurs + `valider()`), un adaptateur `resoudre_<outil>.py` par outil
  (`resoudre`, `resoudre_json`, `apercu_json`), instantanés `tests/python/instantanes/resoudre/`, critères DV-14, LA-40,
  EC-14, FA-08, ED-06 ; schéma réel dans [choix-techniques.md](choix-techniques.md). Pages et moteurs inchangés ;
  les pages passeront à `resoudre()` en T17 à T20.

### T13 — Exercices avec graine
- **Fichiers** : `moteur/exercices.py` (gabarits validés), `exercice(niveau, graine)` par outil, tests.
- **Dépend** : T12. Gabarits acceptés (Q4, 14.10.2026) : pondérations conservées, racines
  distinctes et exactes (sauf réponse contraire à Q8 pour le carré parfait de la factorisation).
- **Vérification** : FA-03, SOC-05 (moteur) ; ED-05, DV-08 ; 200 graines × 4 niveaux × outil
  résolues exactement.

## Phase D — Pages communes

### T14 — `commun/style.css` — **faite, aspect inchangé** (`7656eef`, 17.10.2026)
- La nouvelle identité de l'accueil (contraste AA, SOC-03) reste à faire, en tâche séparée après les migrations T16 à T20.
- **Fichiers** : `commun/style.css`, `tests/python/test_contrastes.py`.
- **Vérification** : SOC-03, ACC-05.

### T15 — Client Pyodide commun + tests de pages en CI — **faite** (17.10.2026 : étape 0 `0797de9`, client commun et pilote ED)
- **Fichiers** : `commun/moteur-python.js`, `commun/worker-pyodide.js`, `tests/pages/` (navigateur
  sans interface, CI seulement), migration pilote de `ensemble-definition/index.html`.
- **Dépend** : T04, T14.
- **Vérification** : SOC-04, SOC-06, SOC-13 sur l'outil pilote ; essai manuel sur téléphone.
- **Réalisé** : `commun/moteur-python.js` (client : lit `moteur/manifeste.json`, télécharge les fichiers, worker, délais, relance),
  `commun/worker-pyodide.js` (vrai fichier ; la version de Pyodide vient du manifeste seulement), page Ensemble de définition migrée
  (chargement uniquement), `test_manifeste.py` adapté aux deux modes ; `tests/pages/` (Chrome sans interface piloté depuis Python, local et
  CI) : rendu égal aux références (`test_rendu.py`, 5 pages, ≈ 300 entrées), comportement commun (`test_comportement.py` : SOC-04, SOC-06,
  SOC-16 ; SOC-13 au niveau du client commun, la phrase « Calcul trop long » restant dans la page jusqu'à T16) ; job CI `pages` (corpus réduit : 3 entrées par outil dont une erreur, ≈ 3 min en local, estimé 6 à 10 min sur GitHub ; le
  corpus complet reste en local, `CORPUS=reduit` pour l'autre).
  Reste à la main : essai sur téléphone (Safari, worker en fichier), blocage de jsDelivr, délai jusqu'à « Prêt » (SOC-14).
- **Tests de pages à y intégrer** (CI seulement, Chrome sans interface via le protocole DevTools, décidé le
  14.10.2026) : aperçu de la saisie (SOC-16 : `ln(x)/x` au clavier et avec le bouton ln, pas de message
  rouge pendant la frappe, erreur après ≈ 0,5 s) sur les cinq pages ; rendu du tableau (DV-16 : double
  barre centrée, continue, à 380 px et sur ordinateur) ; message de repli du graphique (EC-04).

### T16 — `commun/outil.js` + `commun/rendu.js`, outil pilote — **faite** (17.10.2026 : Python `c2c7c82`, rendu et page ED `6458dd2`)
- **Réalisé** : `titre_masque` et `resoudre_ed.controle` (phrase du contrôle numérique en Python) ; `commun/rendu.js` (règles de
  rendu des cartes et blocs, voir choix-techniques.md) ; `commun/outil.js` (`monterOutil`, config de page, crochet `apres`) ;
  page de l'ED réduite à ses exemples, ses exercices et sa config (aucun texte de corrigé en JS) ; manifeste (`resoudre_ed`, clé
  `anciennes`) ; rendu égal aux 41 références, 50 captures identiques au pixel ; tests `test_source_unique.py` (source unique, SOC-10),
  SOC-07, SOC-09, SOC-13 (page), banc de rendu des instantanés des 5 outils (`test_comportement.py`). Job CI `pages` : 30 min
  (corpus réduit ≈ 6 min en local).
- **Report** : SOC-01 (lien « ← samimir.ch » et pied de page) avec la nouvelle identité visuelle, pour les 5 pages d'un coup.
- **But** : page outil générique (saisie, aperçu, clavier, hasard, étapes, impression) pilotée
  par une config.
- **Dépend** : T12, T15.
- **Vérification** : SOC-01, SOC-02, SOC-07, SOC-09, SOC-10 sur l'Ensemble de définition ;
  [manuel] SOC-08.

### T17 à T20 — Migration des autres pages (une tâche par outil)
- T17 Dérivée — **faite** (17.10.2026) : page réduite à ses exemples, ses exercices et sa config (`sympyAvant: true`) ;
  manifeste (`resoudre_dv`, fonctions `resoudre` et `apercu`) ; SOC-10 et source unique étendus à la page ; 31 références
  inchangées au caractère près (seul l'espace entre la formule et la ligne « ED = … » disparaît, invisible : références
  regénérées) ; 50 captures identiques. Aucun changement de Python.
- T18 Limites — **faite** (17.10.2026) : page réduite à ses exemples, ses exercices et sa config (`sympyAvant: true`) ;
  manifeste (`resoudre_la`, fonctions `resoudre` et `apercu`) ; SOC-10 et source unique étendus à la page ; 24 références sur 25
  changent d'une seule chose, l'espace entre la formule et la ligne « ED = … » (invisible : 50 captures sans écart au-delà du bruit de
  rendu) ; aucun changement de Python.
- T19 Étude complète — **faite** (21.10.2026, 10 commits : `13c7a5a`, `97fc5cb`, `a47ae1c`, `68b5dbb`, `0fbdc18`, `b6c29c9`, `618be7f`,
  `42f568f`, `b5b7eb9`, `7d5acf4`) : page réduite à ses exemples, ses exercices et sa config (`sympyAvant`, `delaiCalcul: 45000`, greffon
  graphique) ; `commun/graphique.js` réutilisable (dessin, `monterGraphique`, `greffonGraphique`) ; `rendu.js` rend `tableau.limites` et les
  greffons ; manifeste `resoudre_ec` (`etudier` gardée comme ancienne). Preuve (banc `tests/pages/graphique.py`, voir
  [choix-techniques.md](choix-techniques.md)) : bruit mesuré nul ; commits 2 à 4 : 192 scénarios identiques en trace et en pixels, 10 captures
  identiques à l'octet ; EC-06 : seuls des `fillText` fractionnaires changent (628 étiquettes) ; EC-05 : seuls les 24 pincements changent.
  EC-04, EC-05, EC-06 testés (`test_graphique.py`) ; EC-05 et EC-07 vérifiés au doigt sur téléphone (14 vérifications, 21.10.2026). Défaut
  de l'ancien code corrigé : la translation du pincement dépendait du nombre de `pointermove`. Critère `resoudre()` renuméroté EC-14 (EC-13
  désigne le rendu à 360 px).
- T20 Factorisation — **faite** (22.10.2026) : page réduite à ses exemples et sa config (`sympyAvant`, `prefixe:""`, `prefixeExo:"Factoriser : "`,
  `exercicePython:"exercice"`) ; manifeste `resoudre_fa` (fonctions `resoudre`, `apercu`, `exercice`), l'ancien `factoriser` n'est plus appelé ;
  `outil.js` gagne `exercicePython` (tirage de l'exercice par niveau en Python) et `prefixeExo`, et lit le texte d'attente de l'aperçu dans la
  page (« Aperçu du polynôme ») ; SOC-10 : `aria-live` et `aria-label` ajoutés à la page ; SOC-10 et source unique étendus. Rendu : les
  références de la page (corpus complet) passent sans régénération ; aucun changement de Python hors l'export de `exercice_json`.
- **Dépend** : T16. **Vérification** : mêmes critères SOC + critères de page de l'outil ;
  instantanés des moteurs inchangés.

### T21 — Factorisation : une carte par méthode — **faite** (25.10.2026)
- **Dépend** : T12, T20. **Vérification** : FA-04, FA-05, FA-09.
- **Réalisé** : `Ctx.groupes` (méthode de chaque étape) et `_factoriser()` dans `factorisation.py` ; `resoudre_fa.py` regroupe les
  étapes consécutives de même méthode (« Étape k », badge = méthode) puis la carte « Factorisation » (bilan). `factoriser_expr` et
  `factoriser_json` gardent leur format (pages en cache). FA-05 : `(x+1)^2-(x-1)^2` = différence de carrés, `4x`.
- **Décision de l'enseignant (25.10.2026)** : plus de « zéro évident » p/q. Un trinôme a ≠ 1 passe par le discriminant
  (`a(x − x₁)(x − x₂)`, ex. 6x² − 7x − 3 = 6(x + 1/3)(x − 3/2)) ; la « racine évidente » (degré ≥ 3) ne teste que les diviseurs
  entiers du terme constant (FA-09). Instantanés régénérés : 12 entrées changées, toutes relues (méthode annoncée, résultat vérifié).

### T22 — Accueil : registre, sans-JS, contraste, animation sobre — **faite** (26.10.2026)
- **Fait** : `commun/registre.json` (6 outils, 13 cartes) vérifié contre `index.html` (`tests/python/test_accueil.py` : ACC-01, 02, 03, 05, 07 ; `tests/pages/test_accueil.py` : ACC-03 sans JS,
  ACC-04, ACC-06, thème). Sans JavaScript tout est visible (`data-js`) ; `--gold` clair `#84672c` (4,9:1) ; le ruban s'arrête hors écran, onglet caché, et suit le thème
  sans recharger ; commentaires « fourmi » supprimés. **ACC-08 reporté à T27** (la page du simplexe ne comprend pas encore `?methode=`).
- **Fichiers** : `commun/registre.json`, `index.html`, `tests/python/test_accueil.py`.
- **Vérification** : ACC-01 à ACC-08. Les liens `?methode=` de la 2e année ne sont posés qu'une
  fois T27 en ligne (la page doit d'abord comprendre le paramètre) ; d'ici là, 2C et 2Mr gardent
  le lien actuel `simplexe/`.

### T23 — Notation suisse
- **Fichiers** : tokeniseurs (`ensemble_def.py`, `factorisation.py`), `dec()`, `commun/nombres.js`,
  graduations du graphique.
- **Dépend** : T01. Milliers : ’ dès 4 chiffres, saisie de ' et ’ (Q5, 14.10.2026).
- **Déjà fait par T33 (Q12, `657806d`)** : la partie Python du formatage, dans `moteur/nombres.py` (`grouper`, `formater_entier`, `formater_decimal`,
  `nettoyer_saisie`, motifs de saisie), appliquée à l'outil Exponentielles et logarithmes ; règle précisée : séparateur sur la partie entière seulement
  (1’234,567, jamais dans les décimales). **Reste pour T23** : réutiliser ces fonctions dans les tokeniseurs de `ensemble_def.py` et `factorisation.py` et dans
  `dec()`, écrire `commun/nombres.js` (même règle), les graduations du graphique, et régénérer les instantanés.
- **Vérification** : SOC-11, SOC-12.

## Phase F — Nouveaux outils (avant la phase E)

Les outils viennent de [futur_outils.md](futur_outils.md) (numéros « # » ci-dessous). Ils se placent
**avant le simplexe** : ils comblent des années sans outil (1re n'a que la factorisation) alors que
le simplexe existe déjà et fonctionne. Tâches **N01 à N26**, une par outil.

### Prérequis communs

- **T11, T12, T13** (noyau public, format `resoudre()`, exercices avec graine) : sans eux, chaque
  moteur importerait des noms privés de `ensemble_def.py` et écrirait un adaptateur jeté ensuite.
- **T16 puis T17 à T20** (page générique prouvée sur les quatre pages existantes), **T22**
  (registre : un outil = une entrée + ACC-01 à ACC-08), **T23** (notation suisse : décimaux des
  statistiques et probabilités, tokeniseurs modifiés une seule fois).
- **Graphique réutilisable** : T19 doit livrer le graphique de l'Étude complète comme module
  (`commun/graphique.js`) et non comme code de page ; il sert à N01, N05, N11, N22, N25, N26.
  Si T19 ne le fait pas, une tâche d'extraction précède N01.
- **Une seule tâche d'outil à la fois**, et jamais en parallèle d'une migration T17 à T20.

### Gabarit d'une tâche d'outil (étapes = commits)

1. **Spécification** `docs/specifications/<outil>.md` : critères d'acceptation numérotés (préfixe
   propre à l'outil), questions pour l'enseignant dans [a-valider.md](a-valider.md). Comportement
   à trancher avant le code, comme pour les outils actuels.
2. **Moteur Python** (`resoudre()` + gabarits d'exercices T13) avec : tests de propriétés contre un
   oracle indépendant (comme T02), instantanés (comme T01), entrée dans `moteur/manifeste.json`.
3. **Page** (configuration de la page générique, pas de page copiée), exemples de rédaction ajoutés
   à [guide-redaction.md](guide-redaction.md), test de page en CI.
4. **Registre** : entrée dans `commun/registre.json` (année, filières) ; le lien sur l'accueil n'est
   posé qu'après relecture des exemples par l'enseignant.

### Briques communes (créées par le premier outil qui en a besoin)

| Brique | Créée par | Réutilisée par |
|---|---|---|
| Graphique de fonction réutilisable | T19 | N01, N05, N11, N22, N25, N26 |
| Analyse d'équations, inéquations et systèmes (`=`, `≤`, plusieurs lignes) et affichage de l'ensemble solution | N02 | N03, N04, N05, N06, N11, N08, N18, N21 |
| Figure plane SVG (repère, points, vecteurs, droites, cercles, angles) | N08 (cercle trigonométrique) | N09, N16, N17, N18, N21 |
| Champs de saisie typés (nombres, listes, vecteurs, points, matrices, tableaux de données) | N12 | N13, N14, N15, N16, N17, N23 |
| Calcul exact sur matrices (Gauss) | N06 | N23, N24 |

### Ordre et dépendances

**Vague 1 — Pilote et résolution** (analyse de la 2e et algèbre de la 1re)

| Tâche | Outil (#) | Niveau | Dépend | Remarque |
|---|---|---|---|---|
| N01 | Tangente en un point (6) | 2e Ms/Mr | prérequis, graphique | **Pilote** : petit, réutilise la dérivée ; premier outil entièrement natif, il valide T16 à T22 avant les gros chantiers |
| N02 | Équations et inéquations (1) | 1re Ms/Mr | N01 | Crée l'analyse d'équations ; réutilise le tableau de signes et l'ensemble de définition |
| N03 | Équations exponentielles et logarithmiques (5) | 2e Ms/Mr | N02 | ED d'abord, puis changement de variable comme en factorisation. **Version 3C faite avant, sous T33** (sans ED ; la version 2M reprendra le moteur de T33 et ajoutera l'ED) |
| N04 | Tangente depuis un point extérieur (6, suite) | 2e Ms/Mr | N01, N02 | Étend N01 (équation en t) |
| N05 | Optimisation (7) | 2e Ms/Mr | N01, N02 | **À valider** : forme de l'énoncé (fonction donnée sur un intervalle, ou contrainte à éliminer) |
| N06 | Systèmes d'équations (3) | 1re Ms/Mr | N02 | Crée le calcul exact sur matrices |
| N07 | Division euclidienne et Horner (2) | 1re Ms/Mr | T21 | Se recoupe avec la factorisation |

**Vague 2 — Trigonométrie** (1re/2e)

| Tâche | Outil (#) | Niveau | Dépend | Remarque |
|---|---|---|---|---|
| N08 | Équations trigonométriques (4) | 1re Mr, 2e Ms/Mr | N02 | Crée la figure plane (cercle trigonométrique) ; familles de solutions périodiques |
| N09 | Triangle quelconque (16) | 1re Ms/Mr | N08 | Sinus, cosinus, aire |

**Vague 3 — Intégrale** (3e)

| Tâche | Outil (#) | Niveau | Dépend | Remarque |
|---|---|---|---|---|
| N10 | Primitives et intégrale définie (8) | 3e Ms/Mr | T17 (dérivée migrée) | Règles de dérivation lues à l'envers ; mêmes étapes minimales que la dérivée |
| N11 | Aire entre courbes et volume de révolution (9) | 3e Ms/Mr | N10, N02 | Les bornes sont les intersections de f et g (équation de N02) |

**Vague 4 — Dénombrement, probabilités, statistique** (indépendante des vagues 1 à 3 : peut passer plus tôt si l'enseignant en a besoin)

| Tâche | Outil (#) | Niveau | Dépend | Remarque |
|---|---|---|---|---|
| N12 | Champs de saisie typés | — | prérequis | Brique seule, vérifiée sur une page de test |
| N13 | Dénombrement (13) | 3e Ms/Mr | N12 | Formule justifiée, pas seulement le résultat |
| N14 | Probabilités (14) | 3e Ms/Mr | N13 | Arbre pondéré (composant propre) |
| N15 | Statistique descriptive (15) | 1re Ms/Mr | N12, T23 | Décimaux suisses ; variance/écart type exacts |

**Vague 5 — Géométrie analytique**

| Tâche | Outil (#) | Niveau | Dépend | Remarque |
|---|---|---|---|---|
| N16 | Vecteurs (11) | 1re Ms/Mr (+ appui 3C→2M) | N08 (figure), N12 | Produit vectoriel et mixte : Mr seulement |
| N17 | Droites du plan (10) | 2e Ms/Mr | N16 | |
| N18 | Cercle et tangentes (12) | 3e Ms/Mr | N17, N02 | Tangentes issues d'un point : équation du 2e degré |

**Vague 6 — Niveau renforcé (Mr)**

| Tâche | Outil (#) | Dépend | Remarque |
|---|---|---|---|
| N19 | Convexité et points d'inflexion (19) | T19 | Prolonge l'Étude complète ; **peut se faire dès T19 terminée**, avant le reste de la phase F |
| N20 | Intégration avancée (22) | N10, N07 | Parties, changement de variable, éléments simples |
| N21 | Nombres complexes (17) | N02, N08 (figure) | Plan d'Argand ; équations dans ℂ |
| N22 | Suites et limites (18) | graphique, Limites | Réutilise le moteur de limites (n → ∞) |
| N23 | Algèbre linéaire (20) | N06, N12 | Le plus gros chantier : à découper en sous-tâches (matrices et déterminants, espaces vectoriels, valeurs propres) dans sa spécification |
| N24 | Géométrie dans l'espace (21) | N16, N17, N23 | **À valider** : rendu 3D (schéma statique ou projection) |

**Vague 7 — Option applications des mathématiques**

| Tâche | Outil (#) | Dépend | Remarque |
|---|---|---|---|
| N25 | Résolution approchée d'équations (23) | N01, graphique | Newton = tangente de N01 qui coupe l'axe ; erreur affichée |
| N26 | Simulateur de modèles (24) | N22, graphique | |
| — | Projections, axonométrie, perspective (25) | — | Hors plan : tracé interactif lourd, à rediscuter |

### Vérification de la phase

Pour chaque outil : sa spécification relue par l'enseignant avant le code ; la suite complète
verte (CLAUDE.md) ; instantanés de **tous** les autres moteurs inchangés ; ACC-01 à ACC-08 verts
avec la nouvelle entrée du registre ; un exemple par niveau (Ms, Mr) relu avant de lier l'outil
sur l'accueil.

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

## Après T19 — chargement et temps d'attente (tickets du 21.10.2026)

Origine : sur la suite de tests, des « Prêt. » non atteints (un `fetch` local réinitialisé ; une page restée figée sur « Chargement du moteur
de calcul… » pendant 150 s, cause non établie) ; sur
l'élève, un « Calcul en cours… » qui dure parce que SymPy se charge encore. Trois tickets indépendants de T20 à T23.

### T29 — Message quand le chargement est trop long
- Si le chargement de Python ou du moteur (SymPy) dépasse un délai, la page affiche « Le chargement prend plus de temps que prévu, recharge la
  page ». Aujourd'hui, un chargement qui reste bloqué n'a ni délai ni nouvel essai (observé une fois sur 16 ouvertures de page).
- **Fichiers** : `commun/outil.js`, `commun/moteur-python.js` (texte d'interface, écrit une fois dans `outil.js`). Délai à fixer d'après les
  mesures de T31.
- **Vérification** : test de page avec un téléchargement ralenti ou coupé (même principe que SOC-13), le message apparaît puis disparaît
  si le chargement aboutit.

### T30 — Tests de pages sans réseau (Pyodide en copie locale) — FAITE le 2026-10-21
- Les tests de pages chargent Pyodide 0.27.7, SymPy, mpmath et KaTeX depuis une copie locale servie par le serveur de test, plus depuis
  jsDelivr. Les pages gardent leurs URL de production ; le test redirige les requêtes (interception DevTools) vers la copie.
- La copie (≈ 18 Mo, voir « Coût d'un Pyodide auto-hébergé » dans [choix-techniques.md](choix-techniques.md)) n'est **pas** versionnée :
  téléchargée une fois dans un dossier ignoré par git, mise en cache dans la CI.
- **Vérification** : suite de pages verte avec le réseau coupé ; plus aucun « Prêt. » non atteint dû au CDN.
- **Fait** : Pyodide 0.27.7, SymPy et mpmath seulement (`tests/pages/pyodide_local.py`, copie dans `tests/pages/pyodide-local/`) ;
  **KaTeX reste sur jsDelivr** (la page l'a en `defer`, les tests passent sans, mais le réseau reste nécessaire pour le rendu des formules).
  Les requêtes vers `cdn.jsdelivr.net/pyodide/` sont interceptées (Fetch DevTools sur l'onglet, qui voit aussi celles du worker) et réécrites
  vers le serveur de test ; envoyer les corps par DevTools (base64) rendait la suite plus lente que le CDN (899 s contre 682 s).
  Durée de la suite de pages : 682 s avant, 587 s après (4 tests de plus). Version de la copie ≠ pages : le test échoue.

### T32 — Chargement du moteur : SymPy précompilé — FAITE le 2026-10-26
- Plainte de l'enseignant : « extrêmement lent sur téléphone » (≈ 20 s de compilation de SymPy sur téléphone, à chaque ouverture de page).
- **Fait** : `moteur/construire_roues.py` et `moteur/roues/` (roues SymPy et mpmath en bytecode, D13 dans [choix-techniques.md](choix-techniques.md)),
  téléchargement en parallèle de Pyodide, repli sur le CDN si une roue manque ou si le bytecode n'est pas celui de Pyodide. Jusqu'à « Prêt. » :
  ≈ 11-13 s -> ≈ 5,5 s sur un Mac chargé (`import sympy` : 5-8 s -> 0,8-1,3 s). Tests : `tests/python/test_roues.py`, 3 tests de page.
- **Reste (T31 b/c)** : mesurer sur téléphone en Suisse ; décider du préchargement dès l'accueil et de la précompilation de nos propres modules.

### T31 — Temps d'attente : libellé et mesure en Suisse — (a) FAITE le 2026-10-22 ; (b) et (c) restent à faire
- (a) **Libellé** (faite) : pendant l'attente de SymPy (`sympyAvant`, pages Dérivée, Limites, Étude complète), l'état affiche « Calcul en cours… »
  alors que le calcul n'a pas commencé. Afficher « Chargement du moteur de calcul pour cette fonction… » (texte déjà dans `outil.js`), et
  décider si « Calculer » doit rester actif avant « Prêt. ».
  **Fait** (`commun/outil.js`) : un calcul lancé avant l'arrivée de SymPy affiche « Chargement du moteur de calcul pour cette fonction… »,
  puis « Calcul en cours… » une fois SymPy chargé, puis « Prêt. » ; test de page `test_t31_libelle_pendant_le_chargement_de_sympy`
  (échoue avec l'ancien code). **Décision : « Calculer » reste actif** avant « Prêt. » : le clic met le calcul en attente, le libellé
  dit pourquoi, et `?f=` lance déjà le calcul à l'ouverture ; le désactiver obligerait à revenir cliquer.
- (b) **Mesure en Suisse** (téléphone, Wi-Fi et 4G/5G ; Safari iOS et Chrome Android) : durée jusqu'à « Prêt. » à froid et avec cache, durée du
  premier calcul, pour les pages à `sympyAvant`. Référence prise le 21.10.2026 sur Mac, Wi-Fi, charge faible : ≈ 17 s à froid jusqu'à « Prêt. »
  (Python prêt vers 9 s, SymPy vers 17 s) ; une fois prêt, les 8 exemples de l'Étude complète prennent de 0,2 à 1,2 s ; ≈ 10 Mo transférés.
- (c) **Décision d'après les chiffres** : rien, préchargement du moteur dès l'accueil, ou auto-hébergement de Pyodide
  (coût et conséquences dans [choix-techniques.md](choix-techniques.md)).
- **Vérification** : tableau des mesures (appareil, navigateur, réseau, durées) ajouté à cette fiche ; libellé vérifié par un test de page (fait).
- **Reste** : (b) mesures sur téléphone, à faire par l'enseignant ; (c) décision d'après ces chiffres.

### T33 — Outil « Exponentielles et logarithmes » (3C) — priorité du 26.10.2026, **avant T23**
- Demande de l'enseignant : un outil pour le prochain test des 3C (polycopié 3C (chapitre 2), pp. 17-40). C'est l'outil N03 de la
  phase F, **sans attendre N02** : il porte sa propre lecture de la saisie (`log` = base 10, `log_a`, `e` constante) et n'utilise pas l'outil
  Ensemble de définition (le polycopié n'en parle pas ; les 2M l'auront, plus tard).
- **Spécification** : [specifications/exponentielles-logarithmes.md](specifications/exponentielles-logarithmes.md) (EL-01 à EL-18), questions Q10 à Q12 (tranchées le 26.10.2026).
- **Étapes (un commit chacune, aucun push)** : 0 spécification (**arrêt : l'enseignant valide les formulations**) ; 1 lecture, arbre, TeX, aperçu ;
  2 même base (E1) ; 3 isoler puis logarithme (E2) ; 4 bases différentes (E3) ; 5 équations logarithmiques (E4) ; 6 calcul de log_a(y) (C1) ;
  7 adaptateur `resoudre_el.py`, manifeste, instantanés, vocabulaire, propriétés ; 8 page + pool C + test de page + exemples dans le guide
  (**arrêt : relecture à l'écran**) ; 9 registre et accueil ; 10 si le temps le permet : C2, C3, E5.
- **Fichiers** : `exponentielles-logarithmes/` (nouveau), `moteur/manifeste.json`, `tests/python/moteurs.py`, `cas_el.py`, `test_exp_log.py`,
  `commun/registre.json`, `index.html`.
- **Vérification** : EL-01 à EL-18 ; suite complète verte ; instantanés des autres moteurs inchangés.

- **Suite du 27.10.2026 (sélecteur de méthode, avant l'étape 9)** : chaque équation exponentielle a deux résolutions, « Même base / définition » (A) et « Logarithmes » (B, défaut), choisies par deux boutons
  sans nouveau calcul ; les équations logarithmiques se résolvent par l'exponentielle des deux membres (10^(log(A)) = A) ; contrôle à la calculatrice (R15) ; e^x = e^3 et e^x = e^(x+1) traitées.
  Spécification : « Sélecteur de méthode », EL-19 à EL-21 ; socle commun : `variantes` (SOC-17). **Commits** : 1 docs · 2 `sortie.py` · 3 moteur · 4 adaptateur · 5 page et socle JS · 6 équations logarithmiques.
  **Arrêt : relecture à l'écran** (les deux méthodes), puis étape 9.

- **Suite du 28.10.2026 (problèmes d'application)** : paramètre (Q, C0, V0…) simplifié par une carte, base calculée (`1 + 3,75/100 = 1,0375`, signe %), carte « Interprétation » en années, mois et jours (case à cocher, R16), formes d'application dans le pool.
  Spécification : « Problèmes d'application », EL-22 à EL-25 ; socle commun : `option` (SOC-18). **Commits** : 0 docs · 1 lecture (casse, noms indexés, %, paramètre) · 2 base calculée · 3 simplifier par le paramètre + batterie · 4 interprétation (moteur) · 5 format de sortie `option` · 6 page · 7 pool · 8 audit avant/après.
  **Audit du 28.10.2026 (commit 8)** : corpus de 13 126 saisies (9 660 d'avant + 3 466 d'applications : capitalisation et dépréciation × paramètres × écritures de la base × taux, sans paramètre, %, négatif, ∅, refus), oracle mpmath et durée recalculée en jours ; applications : OK 602 → 3 443, erreurs de lecture 2 864 → 20 (tous des refus voulus : deux inconnues, % mal placé, c0 en minuscule), pas encore 0 → 3 (base 1, 0 ou négative) ; corpus d'avant : inchangé (4 « faux » de l'oracle sur des racines doubles ou très petites, solutions du moteur vérifiées), 0 exception. Suite de pages : 47 tests verts (un délai dépassé dans le pincement des graphiques, relancé seul : vert).
  **Arrêt : relecture à l'écran**.

### T34 — Relire les autres outils avec la règle R13 (fractions et notation scientifique) — **après le test des 3C**
- Demande de l'enseignant (26.10.2026) : la règle R13 du [guide de rédaction](guide-redaction.md) vaut pour **tous** les outils, pas seulement « Exponentielles et logarithmes » :
  valeurs exactes calculées à partir d'entiers ou de puissances en **fractions** ; **décimaux de l'énoncé gardés** (exposant compris) et décimal fini conservé quand le calcul part de décimaux ;
  très grands et très petits nombres en **notation scientifique**. Seul l'outil de T33 l'applique aujourd'hui.
- **Étapes** : 1 relever, outil par outil (factorisation, étude complète, dérivée, limites, ensemble de définition, simplexe, accueil), les endroits où un décimal ou un grand nombre est écrit
  (corrigés, instantanés, exemples du guide) ; 2 présenter la liste à l'enseignant (**arrêt : validation**, certains décimaux sont voulus : arrondis, virgule du simplexe) ; 3 appliquer, un commit par outil,
  instantanés mis à jour un outil à la fois ; 4 `moteur/nombres.py` (T23) : y reprendre `tex_approx` (notation scientifique) si l'enseignant le valide.
- **Vérification** : suite complète verte ; instantanés des outils non touchés inchangés ; relecture par l'enseignant.

### T35 — Outil « Exponentielles et logarithmes » : filière M (2Ms, 2Mr) — demande du 28.10.2026 (suite de N03)
- Demande de l'enseignant : étendre l'outil de T33 aux 2M. Paramètre `filiere` (`"C"` par défaut) ; en M : carte « Ensemble de définition » (cartes de l'outil ED) avant toute équation logarithmique,
  regroupement des logarithmes (jamais de développement, log(x²) intact), carte « Vérification » qui rejette les solutions hors de l'ED avec la raison, changement de variable t = aˣ, pool M, page
  (`?filiere=M`, filière de l'accueil, interrupteur 3C / 2M), registre et accueil pour 2Ms et 2Mr. **Les sorties C restent identiques** (instantanés).
- **Spécification** : [specifications/exponentielles-logarithmes.md](specifications/exponentielles-logarithmes.md), section « Filière M » (EL-26 à EL-34) ; règle R17 du guide de rédaction ; supports de cours : polycopié Javet 2M et brochure Amaudruz 2M.
- **Étapes (un commit chacune, aucun push)** : 0 docs · 1 paramètre `filiere` + refactor `resoudre_ed.py` · 2 carte ED + Vérification (un seul logarithme) · 3 regroupement (plusieurs logarithmes) · 4 changement de variable ·
  5 pool M · 6 page (worker à plusieurs arguments, interrupteur) · 7 registre et accueil · 8 audit avant/après (**arrêt : relecture à l'écran**).
- **Fichiers** : `exponentielles-logarithmes/exp_log_m.py` (nouveau), `resoudre_el.py`, `index.html`, `ensemble-definition/resoudre_ed.py`, `moteur/manifeste.json`, `commun/worker-pyodide.js`, `commun/outil.js`, `commun/registre.json`, `index.html`, tests.
- **Vérification** : EL-26 à EL-34 ; suite Python et suite de pages vertes ; instantanés C et ED inchangés.
- **État (28.10.2026)** : étapes 0 à 8 commitées, rien poussé (eb4084c … dernier commit « étape 8 »). **Arrêt : relecture à l'écran par l'enseignant** (`?filiere=M`, exemples M1 à M8, pool M, accueil 2Ms et 2Mr), puis éventuelles retouches.

### T36 — Filière M : les trous relevés dans le polycopié et la brochure de 2M — demande du 29.10.2026 (suite de T35)
- Demande de l'enseignant (plan en 5 chantiers du 29.10.2026, partie 3) : combler les formes du polycopié 2M et de la brochure 2M que la filière M ne traitait pas, **sans changer la 3C ni l'outil ED**.
- **Spécification** : [specifications/exponentielles-logarithmes.md](specifications/exponentielles-logarithmes.md), section « Filière M », paragraphe 6 (EL-35 à EL-42) ; règle R18 du guide de rédaction.
- **Étapes (un commit chacune, aucun push)** : 1c logarithmes imbriqués de toute base · B exposants 1/x, √x, ±ln x · C base polynomiale `log_(2x)` · D bicarré · E `log_x(n) = p/q` · F constante irrationnelle dans un regroupement ·
  G1 carré d'une somme dans un exposant · G2 second membre calculé · G3 `xᵏ(a + b log x) = 0` · G4 π en M · docs.
- **Fichiers** : `exponentielles-logarithmes/exp_log_m.py` (sections 4 quater à 4 octies), `exp_log.py` (nœud `Pi`, lecture de `log_(expr)(arg)`, `_fin_beta`, `analyser_saisie(texte, filiere)`), `resoudre_el.py`, `tests/python/cas_el.py`, `test_exp_log_m_t36.py`, instantanés et références de rendu M, `tests/outils/audit_m.py`.
- **Vérification** : suite Python et suite de pages vertes ; instantanés C et ED inchangés ; audit avant/après (6 803 saisies) : exception 0.
- **État (29.10.2026)** : toutes les étapes commitées, rien poussé. **Reste** : relecture à l'écran (les 10 saisies M du rapport), puis éventuelles retouches. Limites assumées (« pas encore ») : voir le paragraphe 6 de la spécification.

## Plus tard (hors plan, si les tests tiennent)

- Découpage de `ensemble_def.py` en modules (`moteur/expr.py`, `poly.py`, `ensembles.py`…),
  vérifié par les instantanés et les propriétés.
- Auto-hébergement de Pyodide (coût dans [choix-techniques.md](choix-techniques.md)).
- **Déplacer `docs/` dans un dépôt privé** quand le moteur passera sur un serveur (décision du 26.10.2026). D'ici là, `docs/` reste ici, hors du
  site (`_config.yml`) ; on n'y retire ni les décisions de l'enseignant ni les références, qui sont le journal du plan. À ce moment : copier
  `docs/` dans le dépôt privé, le retirer de celui-ci, et adapter les chemins qui le citent (`tests/python/`, commentaires `docs/choix-techniques.md`).

## Ordre conseillé

T01 → T02 → T03 → T04 (faites) → T05, T07, T08 (indépendantes) → T08b → T06 → T07b (priorité haute)
→ T09 → T11 → T12 → T13 → T14 → T15 → T16 → T17…T20 → T21, T22, T23 → T10
→ **phase F (N01 → N26, vagues 1 à 7)** → T24…T27 → T28 ; T29, T30, T31 (chargement) : après T19, indépendantes.
**T35** (filière M de l'outil exponentielles-logarithmes) : après le test des 3C et T34 si l'enseignant ne dit pas autrement. **T33** (outil des 3C) passe avant T23 ; **T34** (règle R13 dans les autres outils) vient juste après le test des 3C, avant T23.
Les spécifications des outils de la phase F (étape 1 du gabarit) peuvent être rédigées dès maintenant :
ce sont des documents, ils ne touchent pas au code.

**Plus aucune tâche n'est bloquée** (Q1 à Q7 tranchées le 14.10.2026). Q8 (racine double du
carré parfait en factorisation) reste ouverte ; elle ne concerne qu'un gabarit de T13.
