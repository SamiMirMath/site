# Revue de la structure du projet : rapport (lecture seule)

Date : 04.11.2026.

Ce rapport est le seul fichier écrit, et il n'est pas commité. Il n'y a ni branche ni commit, et aucun autre fichier du dépôt n'a été modifié. `git status` ne montre que `docs/chantiers/portage-pc/`, qui était déjà là, et ce dossier.

**Méthode**
- Trois sous-agents, en lecture seule et en parallèle :
  - A : le moteur Python ;
  - B : les pages et le front ;
  - C : les tests et la documentation.
- Analyse statique : `ast`, grep, imports réels à plat avec `uv`. Collecte pytest seulement : la suite n'a pas été lancée. Chaque commande a duré moins de 5 minutes.
- J'ai ensuite revérifié les affirmations les plus lourdes : tout ce qui sert aux recommandations a été recontrôlé par grep ou par lecture.
- Légende : **[V]** vérifié ; **[S]** supposé, non exécuté.

---

## Synthèse

1. **L'architecture tient.** Elle repose sur quatre choses :
   - une page générique pilotée par une configuration (`monterOutil`) ;
   - un adaptateur `resoudre_*` par outil, avec la même interface ;
   - un format de sortie validé (`sortie.valider`) ;
   - un manifeste contrôlé : `test_manifeste` prouve qu'il est complet et minimal par un import à plat isolé.

   Les garde-fous de vérité (oracle mpmath sans SymPy, `parties.valeur_verifiee`, `CONNUS = {}`, copie locale obligatoire de Pyodide) sont solides. Ils sont listés au § 3, à ne pas casser.
2. **Le problème principal, ce sont les listes d'outils écrites à la main.**
   - On en compte environ 20, dans 14 fichiers de tests, plus 3 côté site.
   - Pour ajouter un outil, il faut toucher environ 18 fichiers.
   - Surtout, la plupart de ces listes **se taisent quand on les oublie**. Un outil absent de `rendu.OUTILS` échappe au balayage des largeurs, alors que CLAUDE.md exige que « toute nouveauté [soit] couverte ».
   - C'est à régler avant equations-2e-degre, qui ajoute précisément un outil.
3. **Les doublons métier sont nombreux** :
   - 5 conventions pour « ≈ » ;
   - au moins 8 rédactions du second degré ;
   - 3 parseurs ;
   - 2 arbres d'expressions aux classes homonymes ;
   - 2 classes `Chaine`.

   C'est la conséquence attendue de la construction par outils successifs. Il ne faut pas tout unifier d'un coup : chaque unification fait bouger des centaines d'entrées d'instantanés.
4. **La proposition § 4 de l'audit equations-2e-degre est saine, mais sa partie 1 n'est pas une « extraction pure » telle qu'écrite.**
   - Le modèle de chaîne d'EL dépend de l'arbre d'EL et de son `tex` (`exp_log.py:212`).
   - `_resoudre_polynome` lit l'état global `_DECIMAUX` (`exp_log.py:1219`).
   - Il faut d'abord sortir l'arbre et le rendu, puis la chaîne, et décider du format ≈ (D13) avant d'écrire la brique. Voir le § 4.2.
5. **La documentation dérive** : règles « R1–R19 » / « R1–R12 » alors que R20 existe, fichiers cités absents, commandes caduques, CI différente de `complet`. Rien de grave, mais un nouveau sous-agent qui lit ces documents part sur des bases fausses.
6. **Un risque de « faux à l'écran » côté front** :
   - un bloc de type inconnu est sauté sans rien afficher (`commun/rendu.js:158`, console seulement) ;
   - or un ancien `rendu.js` en cache peut recevoir une sortie Python récente.

   C'est un petit correctif, à faire tôt.

---

## 1. Carte

### 1.1 Arborescence commentée

```
/                         site statique GitHub Pages (Jekyll : _config.yml exclut docs/, tests/, CLAUDE.md)
├─ index.html             accueil écrit à la main (557 l., 144 l. de <style> propre, 16 liens) ; ne lit PAS registre.json
├─ CNAME, _config.yml
├─ commun/                front partagé (modules ES, aucun global)
│  ├─ outil.js            monterOutil → demarrerOutil (l. 60-442) : saisie, aperçu, clavier, exemples, cartes, variantes, filières, PDF
│  ├─ rendu.js            rendreCarte, table BLOCS (rendu d'un bloc par type), ajouterGreffon ; KaTeX via window.katex
│  ├─ graphique.js        greffon canvas (monterGraphique, dessinerGraphique) ; appelle fenetre_json
│  ├─ composants.js       onglets, champSigne, clavier tactile, pavé
│  ├─ style.css           socle + tableaux de signes + encadrés
│  ├─ composants.css      « ajouts seulement » (SOC-19)
│  ├─ moteur-python.js    classe MoteurPython : manifeste, liste blanche des fonctions, Worker, délai 30 s
│  ├─ worker-pyodide.js   Worker : Pyodide (CDN), roues, fichiers à plat, import du module
│  └─ registre.json       7 outils (source de l'accueil, contrôlée par test)
├─ moteur/                briques communes Python
│  ├─ noyau.py            façade (33 l.) : réexporte 59 noms d'ensemble_def (dont _sympy→charger_sympy, _SP→SYMPY, _analyser→analyser_complet)
│  ├─ sortie.py           constructeurs de blocs/cartes, sortie_ok/sortie_erreur/variante/option, validateur valider (schéma BLOCS l. 28)
│  ├─ nombres.py          notation suisse (’ des milliers, virgule), pure (55 l.)
│  ├─ manifeste.json      par outil : module, fichiers (chargés à plat), fonctions appelables, « anciennes » ; versions
│  ├─ construire_roues.py fabrique les roues .pyc de SymPy/mpmath
│  └─ roues/              roues hachées (sympy-1.13.3-pyc312-…zip, mpmath-…)
├─ ensemble-definition/   ensemble_def.py (2690 l. : arbre Nb/X/E/Neg/Op/Fn, parseur lire, tex/qtex, intervalles,
│                         polynômes, trinome, pont SymPy paresseux, json_strict, ErreurSaisie ET l'analyse ED) ; resoudre_ed.py
├─ derivee-variations/    derivee_variations.py (1463 l.) ; resoudre_dv.py
├─ limites-asymptotes/    limites_asymptotes.py (3846 l.) ; redaction_bh.py (1659 l., filière 3M) ; resoudre_la.py
├─ etude-complete/        etude_complete.py (313 l., orchestration) ; parties.py (2150 l., rédaction) ; resoudre_ec.py
├─ exponentielles-logarithmes/  exp_log.py (3643 l. : 2e arbre, 2e parseur, Chaine, rédaction) ; exp_log_m.py (2675 l., filière M) ; resoudre_el.py
├─ factorisation/         factorisation.py (1885 l. : 3e parseur en tuples, trinome_methodes) ; resoudre_fa.py
├─ simplexe/              index.html autonome (1067 l., 872 l. de JS classique) : pas de Pyodide, ni d'outil.js, ni de KaTeX
├─ tests/                 lancer.py ; python/ (≈ 60 fichiers, 1 297 tests) ; pages/ (122 tests, Chrome sans interface) ; outils/audit_m.py
├─ docs/                  guide-redaction, specifications/, chantiers/<chantier>/, taches, choix-techniques… (docs/reference ignoré)
└─ .github/workflows/tests.yml   CI : job python (pip + pytest) et job pages (unittest, corpus réduit)
```

### 1.2 Qui importe qui (moteur) [V]

Arêtes internes au dépôt. « ~> » marque un import paresseux, fait dans une fonction.

- **Base**
  - `ensemble_def` : bibliothèque standard seulement ; SymPy ~> par `_sympy` (l. 1825), mis en cache dans `_SP`.
  - `noyau` → `ensemble_def`.
  - `nombres` et `sortie` : aucun import interne.
- **Moteurs d'outils**
  - `derivee_variations` → `noyau` (43 noms).
  - `factorisation` → `noyau` (5 noms : `json_strict`, `ErreurSaisie`, `trinome`, `qtex`, `charger_sympy`).
  - `limites_asymptotes` → `noyau` (50) **⇄** `redaction_bh`. Ce **cycle** est réglé par un `import redaction_bh` en fin de fichier (l. 3839). `redaction_bh` lit 21 noms privés de LA (37 accès `LA._x`) et greffe 6 méthodes sur `Desc` (l. 1526 et suivantes).
  - `exp_log` → `noyau` (`ErreurSaisie`, `json_strict`), `nombres`, et ~> `exp_log_m` (l. 3634).
  - `exp_log_m` → `noyau` (`analyser_complet`) et `exp_log` : 80 noms, dont 31 privés (l. 22). C'est un **cycle**, plus un `~> _GABARITS` redondant (l. 2545).
  - `parties` → `nombres`, `noyau` (31), `sortie`, **`resoudre_ed`** (un adaptateur), ~> `derivee_variations` (l. 1225).
  - `etude_complete` → `noyau`, `derivee_variations`, `limites_asymptotes`, `parties`.
- **Adaptateurs**
  - `resoudre_ed` → `ensemble_def` (direct, légitime) et `sortie`.
  - `resoudre_dv` → `noyau`, `sortie`, `derivee_variations`.
  - `resoudre_la` → `noyau`, `sortie`, `limites_asymptotes`.
  - `resoudre_fa` → `noyau`, `sortie`, `factorisation` (dont le privé `_factoriser`).
  - `resoudre_el` → `noyau`, `sortie`, `exp_log`, `exp_log_m`, **`resoudre_ed`**.
  - `resoudre_ec` → `noyau`, `sortie`, `resoudre_dv`, `resoudre_la`, `parties`, `etude_complete`.

Les deux cycles fonctionnent dans les deux ordres d'import (essai de A). Pour les 6 outils, les modules chargés à l'exécution sont exactement les fichiers du manifeste.

### 1.3 La frontière `moteur/noyau.py`

- **Ce qu'elle exporte.** `noyau.py` est une façade : il réexporte 59 noms d'`ensemble_def`, y compris 3 privés renommés. C'est par lui que les outils accèdent à l'arbre, au parseur, aux polynômes et au pont SymPy.
- **Qui la respecte.** Tous les moteurs passent par `noyau`, sauf `resoudre_ed`, l'adaptateur de l'outil ED lui-même. Aucun nom privé ne fuit par la façade.
- **Ce qu'elle ne protège pas.** `tests/python/test_noyau.py:16-22` (`MOTEURS`) ne surveille que 5 fichiers : `exp_log`, `exp_log_m` et `redaction_bh` ne sont pas contrôlés, même s'ils respectent la règle aujourd'hui.
- **Une contradiction de documentation** : le `__all__` d'`ensemble_def` (l. 28) liste 4 noms alors que `noyau` en réexporte 59.
- **Deux adaptateurs importés par des moteurs.** `resoudre_ed` est importé par `parties` et par `resoudre_el`. Un moteur dépend donc d'un adaptateur de sortie : la flèche va dans le mauvais sens.

### 1.4 Comment une page charge son moteur dans Pyodide [V]

1. **La page.** `<head>` charge KaTeX 0.16.11 (jsDelivr, sans SRI), `style.css`, `composants.css`, un `<style>` local éventuel et GoatCounter. Un seul `<script type="module">` importe `monterOutil` depuis `commun/outil.js`, avec la configuration de l'outil (`outil:"<dossier>"`, `EXEMPLES`, `EXOS`…).
2. **Le chemin d'un clic.** Tous les chemins partent de `RACINE = new URL("../", import.meta.url)`.
   - `#calculer` → `calculer()` (`outil.js:150`).
   - `MoteurPython.appelPy("resoudre", …)` (`moteur-python.js:121`) refuse toute fonction absente de `fonctions` dans le manifeste (l. 122).
3. **Le chargement du moteur.**
   - `moteur-python.js` lit `moteur/manifeste.json` (`cache:"no-cache"`), puis télécharge les `.py` de l'outil (`no-cache`).
   - Chaque fichier est désigné par son seul nom (`split("/").pop()`, l. 57). C'est ce qui rend le chargement **à plat**.
   - Le Worker charge Pyodide par `importScripts` (`cdn.jsdelivr.net/pyodide/v0.27.7/full/`, version lue dans `manifeste.versions`).
   - Les roues du site sont installées si le magic number vaut `cb0d0d0a` ; sinon, repli sur `loadPackage("sympy")` (l. 158, 173-185).
   - Chaque `.py` est écrit dans le système de fichiers par `FS.writeFile(basename)` (l. 151), puis le Worker fait `import <module>`.
4. **L'appel et le rendu.**
   - `runPython("<module>.resoudre_json(*args)")` (l. 165) → `JSON.parse`.
   - `afficher` → `rendreCarte` (`rendu.js`) : KaTeX `renderToString`, un rendu par type de bloc (`BLOCS`).
   - SymPy est préchargé après une pause de frappe (SOC-21) ; un délai de 30 s relance le Worker.
5. **Le cache.**
   - Le manifeste et les `.py` sont revalidés (`no-cache`), et les roues ont des noms hachés.
   - Les JS et CSS n'ont ni `?v=` ni service worker. [S] GitHub Pages sert avec `max-age=600` : pendant environ 10 minutes, un ancien `rendu.js` ou `outil.js` peut donc tourner avec le nouveau Python. C'est la raison d'être des « anciennes » du manifeste.

### 1.5 Les tests en une vue [V]

- **`tests/lancer.py`**
  - `rapide` : fichiers modifiés → tests qui les importent (regex) + fumée ; les pages en corpus réduit seulement si une page, `commun/` ou `moteur/` change.
  - `complet` : python (`-n auto`), puis pages (`-n 2`).
  - `liste` : affiche ce que `rapide` lancerait.
- **Import du moteur.** `tests/python/moteurs.py:9-10` ajoute 7 dossiers à `sys.path` (plus 8 `sys.path.insert` locaux).
- **Oracle.** `tests/python/oracle.py` : mpmath à 50 chiffres sur l'arbre ED, sans SymPy, utilisé par 11 fichiers. Il n'a pas de recherche de racines.
- **Instantanés.**
  - Format : JSON trié, `allow_nan=False`.
  - Les flottants sont **arrondis à 9 chiffres significatifs** (`test_instantanes.py:36-41`), et les segments du graphique sont résumés par empreinte sha256.
  - Deux jeux :
    - `instantanes/` (moteur) : ED 42, DV 32, LA 37, EC 21, FA 194 ;
    - `instantanes/resoudre/` : les mêmes, plus EL 583 et EL-M 276.
  - Les entrées sont lues dans les `EXEMPLES` et `EXOS` des pages (`cas.py:17`).
- **Pages.**
  - Chrome sans interface, piloté par CDP (`tests/pages/navigateur.py`), avec la copie locale de Pyodide obligatoire (`_verifier_la_copie_locale`, l. 49).
  - `references/` contient 8 JSON ; il n'y en a **aucun pour le simplexe**.
  - `test_largeurs` balaie 7 largeurs de 320 à 1100 px, avec `CONNUS = {}`.

---

## 2. Problèmes (avec preuves)

### 2.1 Listes d'outils écrites à la main : le plus coûteux [V]

**Côté site, 3 listes :**
- `commun/registre.json` (7 outils) ;
- les 16 liens de `index.html` ;
- `moteur/manifeste.json` (6 outils : le simplexe n'a pas de moteur, à juste titre).

**Côté tests, environ 20 listes :**
- `tests/lancer.py` : `DOSSIERS_MOTEURS` (l. 17) et `OUTILS_PAGES` (l. 22) ;
- `tests/python/moteurs.py:9` ;
- `test_vocabulaire.py` : l. 90 et l. 143 ;
- `test_style_commun.py:9` ;
- `test_source_unique.py` : `MIGREES` (l. 11) et `PAGES` (l. 59) ;
- `test_resoudre_import.py:12-29`, qui **recopie les listes de fichiers du manifeste** ;
- `test_json_strict.py:19-23` ;
- `test_instantanes.py:26` et `test_instantanes_resoudre.py:25`, chacun avec une méthode `test_` par outil ;
- `tests/pages/rendu.py` : `OUTILS` (l. 16), `REDUIT` (l. 30) et `entrees()` ;
- `test_comportement.py` : `CALCUL`, `EXEMPLE`, `INVALIDE` (l. 20-27) ;
- `test_rendu.py` : une méthode par outil ;
- `captures.py` ;
- `test_tableaux_css.py:10` ;
- `tests/pages/test_accueil.py:57-60` : « 16 liens / 7 outils » en dur.

**Bilan.** Pour ajouter un outil, il faut toucher environ 18 fichiers : 4 côté site et environ 14 côté tests.

**Le vrai défaut : les oublis se taisent.** Seuls `test_manifeste` et `tests/python/test_accueil.py::test_aucun_outil_oublie` (l. 121) se recalent sur les dossiers ou sur le registre. Ailleurs, un oubli ne fait rien échouer :
- un outil absent de `rendu.OUTILS` échappe à `test_largeurs`, dont la docstring promet pourtant « tous les outils du registre » ;
- un outil absent de `test_vocabulaire` échappe au contrôle du vouvoiement (R12).

**Un trou existe déjà.** EL est absent de `test_instantanes.py` (jeu moteur : il n'y a pas d'`instantanes/exponentielles-logarithmes.json`), de `test_json_strict` et de `test_source_unique.MIGREES`. [S] C'est peut-être voulu, puisque le jeu resoudre couvre EL, mais rien ne le dit.

### 2.2 Doublons métier

**Formats de « ≈ » : 5 conventions** [V]

| Fonction | Fichier (ligne) | Convention |
|---|---|---|
| `dec` | ensemble_def (740) | 4 décimales, sans apostrophe |
| `arrondi`, `decimal_tex`, `approchee` | parties (744, 755, 1088) | 2 décimales ou 2 chiffres significatifs, notation suisse, × 10ⁿ |
| `tex_approx` | exp_log (3104) | 3 décimales, notation suisse |
| `fmt_approx` | redaction_bh (800) | 2 décimales ou 2 chiffres significatifs, sans apostrophe |
| `fmt_val` | redaction_bh (703) | `\cdot 10^` au lieu de `\times 10^` |

`decimal_tex` existe deux fois avec deux sens différents : Fraction exacte dans redaction_bh (l. 364), Decimal en notation suisse dans parties (l. 755).

**Notation des nombres exacts.** `qtex` (ensemble_def l. 518) n'applique pas la notation suisse, alors que l'arbre EL l'applique. On obtient « 1000 » ou « 1’000 » selon l'outil. Autour de `qtex` :
- `redaction_bh.qtex_` (l. 1520) en est une copie ;
- `factorisation.qtx` (l. 296) l'enveloppe ;
- la virgule `replace(".", "{,}")` est écrite à la main dans 5 fichiers.

**Côté JS** [V] :
- `nb` du simplexe est conforme.
- `plain` (simplexe l. 604) fait un `toFixed(2)` **avec un point et sans « ≈ »**. Il est affiché dans le verdict « Maximum de f = » (l. 888, 1044) : c'est un écart à R13 visible à l'écran.
- `nomGrad` (l. 483) met un point décimal sur les graduations.
- `etiquette` (graphique.js:25) met une virgule, mais pas de ’. Son commentaire annonce un `commun/nombres.js` qui n'existe pas.

**Second degré : au moins 8 rédactions** [V]
- ED : `trinome` (l. 1053, avec la ligne Δ) et `racines_quad_r` (l. 1550) ;
- FA : `trinome_methodes` (l. 1154), qui rappelle `trinome` ;
- EC : `parties._factoriser` et sa factorisation (l. 109-144 : Δ et Somme-Produit) ;
- EL : `_resoudre_polynome` (l. 1375), `_suite_polynome` (l. 1885), `_second_degre` (l. 2161) et `_racines_du_second_degre` (l. 1448).

**Parseurs et arbres** [V]
- 3 parseurs : ED (`tokeniser` + `Parseur`), EL (`tokeniser` + `_Parseur`, l. 339 et 449), FA (`_tokeniser` + `_Parseur`, arbre en tuples).
- 2 arbres aux classes homonymes (Nb, E, Neg, Op, Fn) et 2 fonctions `tex`.
- 2 classes `Chaine` (exp_log l. 981, limites_asymptotes l. 1822).
- Au total, 53 noms sont définis dans plusieurs modules.

**Rédaction en double.** La phrase « Ni logarithme… » est écrite deux fois : `parties.AUCUNE_CONDITION` (l. 67) et `resoudre_ed` (l. 25). [V]

**Front** [V]
- 48 lignes non vides sont identiques dans les 6 pages Pyodide (head, carte « Exercice au hasard », barre `#resultat`, clavier). C'est la moitié de chaque page.
- `details ol{…}` est recopié dans 3 pages (LA, EL, FA, l. 13).
- `.final .res` / `.final .c` sont recopiés dans EL et FA (l. 14-15).
- La palette existe en 4 copies : style.css:53-59, simplexe:9-16, `couleurs()` du simplexe, `forcerClair` de graphique.js.
- KaTeX 0.16.11 est écrit en dur 18 fois.
- Le simplexe recopie 6 règles du socle et en fait diverger 8.

**Tests** [V]
- `verifier_outil` et `sortie` sont copiés entre `test_instantanes.py` et `test_instantanes_resoudre.py`.
- Deux oracles EL privés presque identiques : `test_exp_log.py:369-412` et `test_exp_log_m.py:72-122`. Le second est réimporté comme module par `test_explog_3c.py:22` et `test_exp_log_m_t36.py:15`.

### 2.3 Fichiers et fonctions trop gros [V]

**Les fichiers.**
- 4 fichiers dépassent 2 600 lignes :
  - limites_asymptotes : 3 846 lignes, 182 fonctions de premier niveau ;
  - exp_log : 3 643 lignes, 178 fonctions ;
  - ensemble_def : 2 690 lignes, 122 fonctions ;
  - exp_log_m : 2 675 lignes, 128 fonctions.
- parties (2 150) et factorisation (1 885) suivent.

**Les fonctions restent raisonnables** (toutes ≤ 169 lignes). Les plus longues : `derivee_variations.etudier` (169), `ensemble_def.resoudre_rat` (141), `exp_log_m._regrouper` (117), `derivee_variations.tableau_signes` (111).

**Le vrai coût, c'est le couplage** des gros fichiers, pas leur longueur. Pour Pyodide, la taille ne coûte qu'en téléchargement, qui est en cache après le premier.

**Le cas d'`ensemble_def.py`.** Il est à la fois le noyau commun et l'outil ED. Tous les outils chargent l'analyse ED complète pour n'en utiliser que la base.

**Front et tests.**
- `outil.js::demarrerOutil` : environ 380 lignes, en une seule closure d'environ 35 fonctions.
- `simplexe/index.html` : 119 fonctions, 64 lignes de plus de 200 caractères, deux vues dupliquées avec un suffixe P (`summaryP`, `bNextP`…).
- Tests géants : `test_parties_ec.py` (2 137 l.), `test_exp_log.py` (1 837 l.).

### 2.4 Code mort [V : grep par mot sur .py, .js, .html, tests compris]

- **Python jamais référencé :**
  - ensemble_def : `INFO` (l. 1404), `POURQUOI` (l. 2409) ;
  - exp_log : `MESSAGE_PI_EN_3C` (l. 641) ;
  - exp_log_m : `_arbre_produit_poly` (l. 1331), `POIDS_M` (l. 2520, présent seulement dans `__all__`) ;
  - limites_asymptotes : `_enumerer` (368), `_terme_signe_tex` (373), `_mot_signe` (433), `_egalites` (437), `_ligne_reference` (2686) ;
  - redaction_bh : `est_zero_mono` (152) ;
  - `noyau.racine_rationnelle` : réexporté, importé par personne.
- **Les « anciennes » du manifeste**, toujours là :
  - `analyser_json` / `verifier_json` (ensemble_def l. 2601, 2653, depuis le 17.10) ;
  - `etudier_json` (etude_complete l. 273, depuis le 20.10).

  Elles devaient être retirées « après quelques jours » ; elles ont 15 à 18 jours de retard. Il y a aussi des `etudier_json` dans DV (l. 1454) et LA (l. 3835) que seuls les tests appellent.
- **JS :**
  - `ajouterBloc` est exporté (rendu.js:120) mais jamais importé ;
  - `relancer()` ne fait qu'appeler `lancer()` ;
  - `…&&false` (simplexe l. 489) ;
  - onglet Gradient sous `AFFICHER_GRADIENT=false` (l. 194).
- **CSS :**
  - `.enc-autre` (style.css:153) : jamais produit ;
  - `.exo`, `.asymptotes`, `ol.mode` : sans style ni test ;
  - exemption `#graphique` périmée dans `test_style_commun.py:42`.
- **Tests :** les branches « CLIENT » et « fetch inline » de `test_manifeste.py:81-93` ne servent plus.
- **Docs :**
  - `docs/chantiers/limites-asymptotes/brouillons/*.py`, dont deux copies de redaction_bh de plus de 1 270 lignes ;
  - `revue-matin.html` (99 Ko).

### 2.5 Dépendances qui se croisent [V]

- **Cycles :**
  - LA ⇄ redaction_bh (21 privés lus, 6 méthodes greffées sur `Desc`) ;
  - exp_log ⇄ exp_log_m (31 privés importés).
- **Un moteur qui dépend d'un adaptateur :** `parties` → `resoudre_ed` ; `resoudre_el` → `resoudre_ed`.
- **Des outils qui en chargent d'autres :** EC charge DV, LA et ED (13 fichiers). Tout outil charge `ensemble-definition/ensemble_def.py`.
- **État global mutable : `exp_log._DECIMAUX`** (l. 1219).
  - Il est basculé par le décorateur `_avec_decimaux` (10 fonctions, dont 7 dans exp_log_m) et par `_valeur_de_la_base` (l. 2613).
  - `_nb_exact` le lit, et `_resoudre_polynome` appelle `_nb_exact`. Toute brique extraite d'EL hérite de cet état caché.
- **Collisions de noms de fichiers.** L'écriture à plat par nom de fichier n'est protégée contre aucune collision : deux `.py` de même nom dans deux dossiers s'écraseraient en silence. [S] Il n'y en a aucune aujourd'hui.
- **Couplages par regex entre tests et pages** :
  - `const (EXEMPLES|EXOS)=` (`cas.py:17`) ;
  - `outil:"<dossier>"` sans espace (`test_manifeste.py:70`) ;
  - HTML du clavier (`test_source_unique.py:44, 69`).

  Un simple reformatage d'une page casse les tests.
- **HTML écrit en Python.** `resoudre_el.py:33-37` produit le HTML de la grille `.chaine` dans un bloc `texte`, que `sortie.valider` ne contrôle pas. Son CSS vit dans la page EL (l. 16-27) : un écart à SOC-19.

### 2.6 Noms incohérents [V]

- **Tests nommés d'après un ticket :** `test_exp_log_m_t36`, `test_limites_d12_d16`, `test_audit_el`.
- **Graphie flottante :** `test_explog_3c` à côté de `test_exp_log*`.
- **Tests nommés d'après autre chose que l'outil testé :** `test_tableau_limites` et `test_fenetre_zoom` testent l'EC ; `test_rappel_methode` teste la page Limites.
- **Adaptateurs :** `enonce` est public dans DV et LA, `_enonce` privé dans ED, pour le même code. `resoudre_fa` importe le privé `_factoriser`.
- **Front, mélange français/anglais :**
  - simplexe : ids `summary`, `launch`, `editBtn`, `printBtn`… ; classes `.row`, `.grid`, `.on`, `.ok` ;
  - accueil : `.tools`, `.track`, `data-track` ;
  - socle : `.card`, `.wrap`, `.hint`, `.badge`.
- **Mêmes noms, sens différents :** `.ind` (rouge gras dans style.css:143, indicateur dans le simplexe), `.bar`, `.err`, `.hint`. Ils entreraient en collision si le simplexe chargeait style.css.
- **Accessibilité :** le simplexe marque ses bascules par `.on`, sans `aria-pressed`, alors qu'outil.js utilise `aria-pressed`.
- **Identifiants de règles :** `redaction-limites-3m.md:23` a son propre jeu « R1 à R20 ». Les mêmes identifiants désignent donc deux règles différentes selon le document.

### 2.7 Documentation contradictoire ou périmée [V]

**Numérotation des règles.** `CLAUDE.md:16` annonce « R1–R19 », `docs/README.md:21` « R1–R12 », alors que le guide va jusqu'à R20 (`guide-redaction.md:142`, décision du 02.11).

**Fichiers cités mais absents :**
- `docs/methode-chantiers.md` et `docs/chantiers/tests-rapides/*` (cités par l'audit, l. 28-29, et par `portage-pc/diagnostic.md:18`) ;
- `moteur/exercices.py` et `moteur/expr.py` (`taches.md:203`, `:550`) ;
- `tests/python/test_contrastes.py` (`taches.md:213`) ;
- `commun/nombres.js` (`choix-techniques.md:190`, `graphique.js:23`).

**Commandes caduques.**
- `docs/README.md:31` et `taches.md:7` donnent `python -m unittest discover -s tests/python`. Or `test_corpus_etude_complete.py:22` importe pytest, et la commande officielle est `tests/lancer.py`.
- Le README annonce une catégorie « [auto-js] node --test » (l. 59) : il n'existe pas de tests/js. Les 13 points de `simplexe.md` qui portent cette étiquette ne sont cités par aucun test.

**La CI ne fait pas la même chose que `complet`** (`.github/workflows/tests.yml`) :
- elle installe avec pip et non avec uv ;
- elle lance les pages par `unittest discover` (l. 97), sans xdist, en `CORPUS=reduit` ;
- son commentaire « ≈ 300 entrées » (l. 91) est périmé : le corpus complet en compte environ 1 190.

**Chiffres et commentaires périmés :**
- « cinq outils » dans `test_style_commun.py:1`, `test_comportement.py:1` et `captures.py:1` ;
- « Échecs connus au 30.10.2026 » au-dessus d'un `CONNUS` vide (`test_largeurs.py:26`) ;
- durées mesurées sur le Mac dans `CLAUDE.md:43`, contre celles du PC dans le diagnostic de portage-pc (non suivi) ;
- docstrings d'`ensemble_def` :
  - l. 4 : « aucune dépendance », alors qu'il y a un pont SymPy ;
  - l. 9 : `analyser_json` « utilisée par le site », alors que c'est une « ancienne » ;
- les adaptateurs disent encore « reproduit les cartes que la page affiche aujourd'hui », un vocabulaire de migration.

**Documents historiques et suivis.**
- `analyse-2026-10-13.md` décrit le Worker Blob et 5 pages : c'est une archive, plus un état des lieux.
- `taches.md` fait 567 lignes, en majorité des sections closes.
- `a-valider.md` : seule Q8 est ouverte.

**Fiches de chantier hors format :**
- `etude-complete/suivi.md` fait 703 lignes, contre la règle « court » ;
- `limites-asymptotes` n'a pas de `suivi.md` ;
- seul `etude-complete` a un `journal.md` ;
- explog-3c, simplexe et limites n'ont pas de « Reprise après compactage ».

**CLAUDE.md lui-même.** Le paragraphe « Fiche de chantier » est rangé sous « Commandes de test ».

**Traçabilité.** 78 des 179 identifiants des spécifications ne sont cités par aucun test (FA-09 par exemple ; SOC-19 est couvert par `test_largeurs`, mais sans citation). Cela ne prouve pas qu'ils sont non couverts.

### 2.8 Pièges de l'outillage de test [V]

**`lancer.py::fichiers_modifies` (l. 33-37)** découpe la sortie de git avec `.split()` :
- un nom à espaces est coupé en deux ;
- git met un nom non ASCII entre guillemets octaux (essai fait dans un dépôt jetable : `"\303\251.py"`) ;
- `os.path.exists` (l. 37) écarte ensuite ces noms en silence ;
- un fichier supprimé est écarté de la même façon, et ses dépendants ne sont pas relancés.

**Ce que `rapide` ne relance pas :**
- rien quand on modifie `tests/python/donnees/` (l. 43) ;
- pas les tests d'instantanés quand on modifie les `EXEMPLES` d'une page (l. 71, qui l'admet en commentaire), un JSON d'instantané ou une référence de page ;
- pas `test_rendu` quand on modifie un `.py` de moteur, alors que les références de pages en dépendent ;
- et `-W ignore` (l. 96, 105) masque les avertissements.

**Aucun test ne couvre `lancer.py`.**

**Collecte jointe impossible.** Les deux `test_accueil.py` font échouer une collecte commune de `tests/python` et `tests/pages` (« import file mismatch »). C'est connu et documenté dans CLAUDE.md, mais cela reste un piège.

**« À l'octet » n'est pas garanti.** Les instantanés arrondissent les flottants à 9 chiffres et résument les segments du graphique par empreinte. Des instantanés identiques ne prouvent donc pas, à eux seuls, une sortie identique à l'octet.

### 2.9 Fichiers suivis ou ignorés

- `.gitignore` ignore bien `__pycache__/`, `pyodide-local`, `docs/reference/` et `tests/outils/resultats_m.json`. [V]
- **Aucun motif n'ignore `*.pdf` sous `docs/chantiers/`.** Le risque relevé par l'audit (D0) demeure. [V]
- **Les PDF de l'audit equations-2e-degre ne sont plus dans ce clone** : `docs/chantiers/equations-2e-degre/` ne contient que `audit-etape0.md`, et `docs/reference/` n'existe pas. [V] [S] Ils sont probablement sur le Mac. À confirmer avant P0 (D0).
- `docs/chantiers/portage-pc/diagnostic.md` n'est pas suivi : ses chiffres (PC : 120 s et 540 s) ne sont donc nulle part dans l'historique.

---

## 3. Ce qui est BIEN fait, à ne pas casser

1. **Le contrat page ↔ moteur.**
   - `monterOutil` est une page générique pilotée par une configuration, et aucun texte de corrigé n'est écrit en JS (`test_source_unique`).
   - Interface commune `resoudre` / `resoudre_json` / `apercu_json` sur les 6 adaptateurs, avec `sortie_erreur`.
   - Schéma de sortie validé par `sortie.valider`.
   - Liste blanche des fonctions appelables (`moteur-python.js:122`).
2. **Le manifeste, source unique du chargement.**
   - `test_manifeste` prouve qu'il est complet et minimal par un import à plat isolé (`-I`).
   - La version de Pyodide n'est écrite qu'une fois.
   - Les roues sont hachées, avec contrôle du magic number et repli sur le CDN ; le manifeste et les `.py` sont revalidés (`no-cache`).
   - Aucun manquant, aucun inutile pour les 6 outils.
3. **La façade `noyau.py`.** `test_noyau` vérifie l'identité des objets réexportés (`assertIs`) et l'absence d'import direct d'`ensemble_def`.
4. **Les garde-fous de vérité.**
   - L'oracle mpmath est indépendant de SymPy et du parseur d'évaluation.
   - `parties.valeur_verifiee` exige la concordance de l'écriture exacte, de SymPy et d'une sonde mpmath.
   - Chaque égalité de redaction_bh est vérifiée, et `parties._factoriser` redéveloppe sa factorisation.
   - `json_strict` refuse NaN et infini (`allow_nan=False`).
5. **La discipline des tests.**
   - `CONNUS = {}`, strict dans les deux sens ; xfail strict, et un « unexpected success » compte comme un échec.
   - Les entrées des instantanés sont lues dans les pages.
   - La copie locale de Pyodide est obligatoire, sans repli silencieux sur le CDN, et `intercepteur.fuites` doit être vide.
   - `REDUIT` est vérifié comme sous-ensemble du corpus complet ; la variable `OUTILS` permet de cibler une page.
6. **La mise en page testée.** Pas de requête media en px, pas de redéfinition du socle, variables du socle seulement, 7 largeurs balayées. La CI met Pyodide en cache sous le hash du manifeste.
7. **`nombres.py`** : pur, testé, déjà le bon endroit pour toute convention de nombre.
8. **Aucune dépendance croisée côté front.** Tous les chemins partent de `RACINE`, et aucune page ne lit un fichier d'un autre outil.

---

## 4. Recommandations (chacune pensée comme un futur chantier)

**Principe de vérification commun.** Avant et après chaque chantier, un script **hors dépôt**, dans le bloc-notes de la session, vide la sortie **brute** de `resoudre_json` sur tout le corpus : entrées des instantanés et exemples des pages, toutes filières et variantes. On compare ensuite les deux fichiers avec `cmp`.

Pourquoi ce script : les instantanés seuls ne suffisent pas à prouver l'identité à l'octet (arrondi à 9 chiffres, § 2.8). Il complète les contrôles habituels :
- `REGENERER=1`, puis `git diff --exit-code tests/python/instantanes tests/pages/references` ;
- même nombre de tests collectés (`pytest --collect-only -q` : 1 297 et 122 aujourd'hui) ;
- `python3 tests/lancer.py complet`.

### 4.1 Classement

| # | Chantier | Gain | Risque | Coût | Quand |
|---|---|---|---|---|---|
| R1 | Source unique des outils pour les tests, et oublis qui échouent | fort | faible | 1 à 2 séances | **avant 2e degré** |
| R2 | Bloc inconnu visible à l'écran (rendu.js) | fort (rien de faux) | très faible | < 1 h | **avant 2e degré** |
| R3 | Ménage : « anciennes », code mort, docstrings, documentation (D17 c et d), `.gitignore` des PDF | moyen | faible | 1 séance | **avant 2e degré** |
| R4 | `lancer.py` fiable (D17 b), et test de `lancer.py` | moyen | faible | 1 séance | **avant 2e degré** |
| R5 | Préparer les briques du 2e degré : `moteur/expr.py`, puis `moteur/chaine.py`, `.chaine` dans composants.css, fonction ≈ dans `nombres.py`, `racines` dans l'oracle | fort | moyen (EL) | 2 à 3 séances | **avant 2e degré** (remplace P1–P2 de l'audit) |
| R6 | Garde-fous d'architecture : `test_noyau` étendu, graphe d'imports figé, collision des noms à plat | moyen | très faible | < 1 séance | avant 2e degré (avec R1 ou R5) |
| R7 | Nombres côté JS (`commun/nombres.js`) et virgule du simplexe | moyen (R13 à l'écran) | moyen | 1 séance | après |
| R8 | Ranger les tests : `git mv` par sujet, oracles EL dans oracle.py, aides factorisées, CI alignée sur `complet` | moyen | faible | 1 à 2 séances | après |
| R9 | Unifier les formats ≈ et la notation suisse de `qtex` | moyen | **élevé** (des centaines d'entrées) | 1 chantier par outil | après 2e degré, outil par outil |
| R10 | Sortir la base d'`ensemble_def` (arbre, polynômes, pont SymPy) dans `moteur/` | moyen | moyen | 2 séances | après |
| R11 | Rendre publics les privés croisés (LA ↔ BH, EL ↔ EL-M) et lever les cycles | faible à moyen | moyen | 2 séances | plus tard |
| R12 | Simplexe : JS et CSS hors du HTML, `aria-pressed`, références de pages d'abord | moyen | moyen | 1 à 2 séances | plus tard |
| R13 | Découper `demarrerOutil` (outil.js) en modules ES | faible | moyen | 1 séance | plus tard |
| R14 | Archiver : analyse-2026-10-13, sections closes de taches.md, brouillons, fiches au format | faible | nul | < 1 séance | quand on veut |

**Écartés volontairement, parce qu'ils ne collent pas au cadre :**
- générer le squelette HTML commun des pages par Jekyll ou par JS : les tests servent les fichiers bruts, `cas.py` lit les pages, et SOC-10 serait cassé. Un test « blocs communs identiques » suffit, en basse priorité ;
- un `?v=` sur chaque import ES : fragile sans build. On garde « anciennes », plus R2 ;
- unifier les 3 parseurs : coût énorme, gain faible tant que chaque outil reste juste.

### 4.2 Avant equations-2e-degre (ordre conseillé : R1 → R2/R3/R4 → R6 → R5)

L'audit (§ 4) prévoit `moteur/chaine.py` (P1), le CSS `.chaine` commun (P2), `moteur/second_degre.py` (P3), puis un nouvel outil (P5). Les quatre chantiers ci-dessous mettent ses briques au bon endroit et suppriment les pièges qu'il rencontrerait.

**R1 : source unique des outils pour les tests** (branche `tests-outils`)
- **À faire :**
  - un module sans dépendance, `tests/outils_du_site.py` (nom à fixer), lisible par `lancer.py` avec n'importe quel Python 3. Il lit `moteur/manifeste.json` et `commun/registre.json`.
  - En dériver `moteurs.py`, `lancer.py` (`DOSSIERS_MOTEURS`, `OUTILS_PAGES`), `test_vocabulaire`, `test_style_commun`, `rendu.OUTILS` et `test_resoudre_import`. Pour ce dernier : supprimer la copie des fichiers et ne garder que l'exemple par outil.
  - Pour les données qui restent écrites à la main (`REDUIT`, `CALCUL`, `EXEMPLE`, `INVALIDE`, les instantanés, `test_json_strict`) : un test « clés = outils Pyodide du registre », pour qu'un oubli **échoue**.
  - Remplacer les méthodes `test_<outil>` par des `subTest` sur la liste.
  - Garder « 16 liens / 7 outils » de `tests/pages/test_accueil.py` comme butée explicite : le nouvel outil le mettra à jour en P10.
  - Statuer sur l'absence d'EL dans le jeu moteur, `test_json_strict` et `MIGREES` : l'écrire en exception nommée, ou l'ajouter.
- **Ce que ça casserait :** l'ordre de `sys.path`, si la dérivation change l'ordre des dossiers ; des noms de tests dans les rapports, si l'on passe aux `subTest`.
- **Vérification :**
  - même nombre de tests collectés (1 297 et 122), à l'exception des cas nouveaux annoncés ;
  - instantanés et références inchangés (`git diff --exit-code`) ;
  - `lancer.py liste` identique sur un même jeu de fichiers modifiés.
- **Gain pour le 2e degré :** P5 passe d'environ 14 fichiers de tests à toucher à environ 4 (données propres à l'outil), et rien ne peut plus être oublié en silence.

**R2 : bloc inconnu visible** (peut aller dans la même branche que R3)
- **À faire :** dans `rendreCarte` (`commun/rendu.js:155-158`), remplacer le `console.error` par un encadré visible, du genre « Affichage incomplet : rechargez la page ». Ajouter un test de page qui injecte un bloc de type inconnu.
- **Ce que ça casserait :** rien (cas absent du corpus).
- **Vérification :** références de pages inchangées, plus le nouveau test.
- **Pourquoi avant :** le 2e degré ajoutera au moins un type de bloc (tableau Somme-Produit) pendant la fenêtre de cache de GitHub Pages.

**R3 : ménage** (branche `menage-structure`, une partie par point, sorties identiques à l'octet)
1. **Les « anciennes ».** Retirer `analyser`, `verifier` et `etudier` du manifeste, avec leurs fonctions `*_json` (ensemble_def l. 2601, 2653 ; etude_complete l. 273) et l'import de compatibilité `resoudre_ed.py:10`. Basculer les tests qui les appellent (`test_json_strict`, `test_racines_reelles`…) sur `resoudre_json`.
2. **Le code mort du § 2.4.** Tout supprimer, sauf ce qu'un test exerce volontairement : `etudier_json` de DV et LA, s'ils servent d'interface de test, à confirmer.
3. **Les copies.** `qtex_` → `qtex` (redaction_bh) ; une seule source pour « Ni logarithme… ».
4. **Docstrings et `__all__`.** Corriger ceux d'`ensemble_def` ; « cinq outils » dans les tests ; le commentaire de `test_largeurs.py:26` ; le commentaire de `tests.yml:91`.
5. **Documentation (D17 c et d) :**
   - « R1–R20 » dans le README (et dans CLAUDE.md si l'enseignant le valide : c'est son fichier d'instructions) ;
   - créer `docs/methode-chantiers.md` ou retirer les références (je recommande de les retirer : CLAUDE.md, le gabarit de taches.md et les audits en tiennent lieu) ;
   - README : commandes par `lancer.py`, sommaire complet, `[auto-js]` marqué « prévu » ;
   - renommer les règles de `redaction-limites-3m.md` (RL1–RL20) ;
   - retirer les fichiers fantômes de taches.md et choix-techniques.md.
6. **`.gitignore`.** Ajouter `docs/chantiers/**/*.pdf`, et confirmer où sont les PDF (D0).

- **Ce que ça casserait :** une page restée en cache plus de 15 jours appellerait une fonction disparue. [S] C'est négligeable : `max-age` vaut environ 10 minutes, et la liste blanche de `moteur-python.js` refuse proprement.
- **Vérification :** dump brut identique (`cmp`), instantanés et références inchangés, `test_manifeste` vert (manifeste minimal).

**R4 : `lancer.py` fiable** (D17 b)
- **À faire :**
  - `git diff -z` et `ls-files -z`, avec un découpage sur `\0` ;
  - les fichiers supprimés relancent leurs dépendants ;
  - parcourir `tests/python/donnees/` ;
  - quand une page, `cas*.py` ou un JSON d'instantané change : relancer `test_instantanes*` et `test_json_strict` ;
  - quand un `.py` de moteur ou une référence change : relancer `test_rendu` pour l'outil concerné ;
  - ajouter `tests/python/test_lancer.py`, qui crée un dépôt git temporaire avec des noms comme « a b.py » et « é.py ».
- **Ce que ça casserait :** `rapide` lancera un peu plus de tests, ce qui est voulu.
- **Vérification :** `lancer.py liste` sur des cas construits ; `complet` inchangé.

**R6 : garde-fous d'architecture** (petit, avec R1 ou en tête de R5)
- **À faire :**
  - étendre `test_noyau.MOTEURS` à `exp_log`, `exp_log_m` et `redaction_bh` ;
  - ajouter un test qui fige le graphe d'imports internes : la liste blanche des arêtes, paresseuses comprises, extraite par `ast`. Toute arête nouvelle, comme `chaine` → `exp_log`, échoue et doit être ajoutée exprès ;
  - ajouter un test « aucun nom de fichier en double parmi les fichiers d'un manifeste », puisque l'écriture se fait à plat par nom de fichier.
- **Ce que ça casserait :** rien.
- **Vérification :** les nouveaux tests sont verts sur `main`.
- **Gain :** l'extraction de R5 devient vérifiable mécaniquement.

**R5 : préparer les briques du 2e degré** (branche `briques-communes`, ou parties P1–P2 de l'audit révisées)

C'est le point où la proposition de l'audit doit être corrigée [V] : `tex_element` et `tex_chaine` (exp_log l. 996, 1013) appellent `exp_log.tex` (l. 212), qui dépend de tout l'arbre EL (Nb, Defini, Var, Log, Pi… et `_nb_tex`, l. 53-310). Une `chaine.py` « pure » posée seule importerait donc `exp_log`, ou le dupliquerait.

1. **`moteur/expr.py`.** Y déplacer l'arbre EL et son `tex`, sans le parseur EL, qui reste à EL. `exp_log` réexporte tout sous les mêmes noms : les tests utilisent `el.Chaine` 14 fois et `el.tex_chaine` 47 fois, et `exp_log_m` reprend 80 noms par `exp_log`.
   - Garder un seul propriétaire pour l'état décimal, et ne pas le changer dans ce chantier.
   - Ajouter `moteur/expr.py` au manifeste de l'outil EL.
2. **`moteur/chaine.py`.** Y mettre `Eq`, `Rel`, `Ou`, `Texte`, `Chaine`, `Message`, `tex_element`, `tex_chaine` et `rangees_chaine` par-dessus `expr`, avec **seulement** les propriétés génériques : autre côté, produit nul, mise en évidence.
   - Les 47 `PROP_*` d'exp/log (l. 1070-1116) restent dans `exp_log`.
   - Le `_ligne` HTML de `resoudre_el.py` (l. 33-37) va dans `sortie.py`, comme constructeur de bloc à sortie identique, puisque c'est du rendu d'adaptateur.
   - Plus tard, et hors de ce chantier, on en fera un vrai type de bloc validé.
3. **CSS.** Déplacer `.chaine` (page EL, l. 16-27, 11 règles, `@container 47rem`) tel quel dans `commun/composants.css`. Mettre `details ol` en commun dans style.css, à côté de `details ul`, pour que le nouvel outil n'en fasse pas une 4e copie.
4. **Nombres.** Décider D13, puis écrire **une** fonction ≈ dans `moteur/nombres.py`, sans y brancher les 5 formats existants (c'est R9). Décider aussi si les nombres exacts du nouvel outil suivent la notation suisse, qui manque à `qtex` de l'ED. Sinon, un corrigé mêlerait « 1000 » (saisie lue par l'ED) et « 1’000 » (chaîne EL).
5. **Oracle.** Ajouter `racines(coeffs)` à `tests/python/oracle.py` (`polyroots` de mpmath) avant P3, au lieu d'un 3e oracle privé.
6. **Pour P3**, ce n'est pas du travail préalable mais une consigne :
   - `second_degre.py` prend un paramètre explicite `decimaux=` et ne lit jamais `exp_log._DECIMAUX` ;
   - il travaille sur des `Fraction`, et la saisie est rendue par `Texte` à partir du `tex` de l'ED, pour ne pas manipuler deux arbres ;
   - le tableau Somme-Produit est un **type de bloc** (`sortie.essais` validé dans `_valider_bloc`, `BLOCS.essais` dans rendu.js, CSS dans composants.css, sur le modèle de `.vals`/`.uv` : `overflow-x:auto`, aucune largeur fixe), et non du HTML dans un bloc `texte` comme `.chaine`.

- **Ce que ça casserait :**
  - l'ordre de définition d'`exp_log` (les décorateurs `_avec_decimaux` sur des fonctions de l'arbre) ;
  - le cycle `exp_log` ⇄ `exp_log_m` ;
  - les tests qui inspectent `el.<nom>` par identité.
- **Vérification :**
  - dump brut EL et EL-M identique (`cmp`) ;
  - instantanés `resoudre/exponentielles-logarithmes*.json` et références `exponentielles-logarithmes*.json` identiques ;
  - aucune ligne de test modifiée, hors manifeste ;
  - `test_manifeste` (complet et minimal) et R6 (nouvelles arêtes `exp_log` → `expr` et `chaine` déclarées, aucune arête `chaine` → `exp_log`) ;
  - `test_largeurs` avec `CONNUS = {}`.

### 4.3 Après equations-2e-degre (résumé)

- **R7 : `commun/nombres.js`**, miroir de `moteur/nombres.py`.
  - Y brancher `etiquette` (graphique.js), `plain` et `nomGrad` (simplexe), avec « ≈ » quand la valeur est arrondie.
  - Casse : `graphique-traces.json` et les tests du simplexe, à régénérer et relire.
  - Vérification : les cas de `test_nombres.py` rejoués dans Chrome (node est absent de la machine).
- **R8 : ranger les tests.**
  - `git mv` par sujet avec un préfixe d'outil, sans changer le contenu ; fusionner les 2 oracles EL dans `oracle.py` ; sortir `verifier_outil` et les aides EL-M dans des modules `aides_*`.
  - CI : passer par `tests/lancer.py` (uv et pytest pour les pages), corpus réduit, plus un corpus complet en `workflow_dispatch`.
  - Vérification : même collecte, aux noms de fichiers près.
- **R9 : unifier les formats ≈.** Un chantier par outil, dans l'ordre de l'audit (EC et DV d'abord, EL en dernier), chacun avec la régénération **relue** de ses trois jeux. C'est le seul chantier qui change volontairement l'affichage.
- **R10 : sortir la base d'`ensemble_def`.**
  - Créer `moteur/arbre.py`, `moteur/polynomes.py`, `moteur/pont_sympy.py` (seul propriétaire de `_SP`) et `moteur/base.py` (`json_strict`, `ErreurSaisie`), avec un réexport complet dans `ensemble_def`. Ainsi `noyau`, `resoudre_ed`, les tests et l'`assertIs` de `test_noyau` restent inchangés.
  - Casse : les 6 entrées du manifeste (requêtes en plus, sans coût notable une fois en cache).
- **R11 : lever les cycles.** Rendre publics, dans un module dédié, les 21 privés de LA lus par redaction_bh et les 31 privés d'exp_log lus par exp_log_m. Rendre `resoudre_ed` indépendant de `parties` et de `resoudre_el`, en mettant ses textes partagés dans un module de moteur.
- **R12 : simplexe.**
  - Capturer d'abord des références de pages, puisqu'il n'en a aucune.
  - Ensuite : `simplexe/simplexe.js` en script classique (les globals S, ST, PS restent), puis `simplexe.css`, puis `aria-pressed`. Charger `style.css` seulement après avoir renommé `.ind`, `.bar`, `.err` et `.hint`.
- **R13 : `outil.js`.** Découper `demarrerOutil` en modules ES (filières, variantes et option, exercice) sans changer le DOM. Vérification : `test_comportement`, `test_clavier`, références des 7 pages.
- **R14 : archives.**
  - Déplacer `analyse-2026-10-13.md`, les sections closes de `taches.md` et les brouillons de limites dans `docs/archives/`.
  - Remettre `etude-complete/suivi.md` au format (le détail va dans `journal.md`), et créer le `suivi.md` de limites.

---

## 5. Questions pour l'enseignant

1. Les PDF d'equations-2e-degre sont-ils sur le Mac, dans `docs/reference/` ? Ce clone (PC) ne les a pas (D0).
2. R5 : faire un chantier séparé `briques-communes`, ou réviser P1–P2 de l'audit dans la branche `equations-2e-degre` ? Je recommande un chantier séparé : il est fusionnable et vérifiable à l'octet indépendamment.
3. D13 et la notation suisse des nombres exacts, à trancher avant R5.4.
4. L'absence d'EL dans le jeu d'instantanés moteur, dans `test_json_strict` et dans `MIGREES` : est-elle voulue ?
5. CLAUDE.md : les corrections de forme (R1–R20, place du paragraphe « Fiche de chantier », durées Mac/PC, commande `pyodide_local.py` du portage PC) sont à faire par vous, ou sur votre demande explicite.
