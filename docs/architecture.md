# Architecture du site : couches et règles

**Validé par l'enseignant le 05.11.2026, sauf D13** (format « ≈ », à trancher dans les décisions du 2e degré, voir A5). Tiré de la revue de
structure (`docs/chantiers/revue-structure/rapport.md`) et des décisions orales du 04.11.2026. CLAUDE.md y renvoie (§ 7).

**But** : qu'un nouvel outil (le prochain : équations du 2e degré) se construise avec les briques existantes, sans copier de code ni oublier
de test, et que ces règles soient **vérifiées par des tests** plutôt que seulement écrites : une règle seulement écrite finit par ne plus être
respectée.

## 1. Les quatre couches

Chaque couche ne dépend que de celles du dessous.

```
4. Pages            <outil>/index.html : une configuration passée à monterOutil ; tout le reste dans commun/ (JS, CSS)
3. Adaptateurs      <outil>/resoudre_xx.py : assemblent la sortie affichée de l'outil (blocs de moteur/sortie.py)
2. Moteurs d'outil  <outil>/*.py : résolution et rédaction propres à l'outil ; n'importent que moteur/ (dont sortie.py
                    pour ceux qui rédigent : parties, redaction_bh, demain second_degre)
1. Briques communes moteur/ : nombres, sortie (blocs affichés, pour les moteurs qui rédigent comme pour les adaptateurs),
                    noyau (façade de la base), expr (arbre d'expressions, TeX, lecture avec le lexique de l'outil),
                    et demain chaine, second_degre
```

| Couche | Peut importer | Ne doit jamais importer |
|---|---|---|
| 1. Briques (`moteur/`) | d'autres briques | un moteur d'outil, un adaptateur |
| 2. Moteurs d'outil | les briques (par `moteur/noyau.py` pour la base) | un autre outil, un adaptateur |
| 3. Adaptateurs | les briques, **le moteur de leur outil** | un autre adaptateur, le moteur d'un autre outil |
| 4. Pages | `commun/` | un fichier d'un autre outil |

L'Étude complète est la seule exception voulue : c'est un outil qui **assemble** DV, LA et ED. Son moteur importe ceux de DV et LA
(`etude_complete` → `derivee_variations`, `limites_asymptotes`), et son adaptateur ceux de DV et LA (`resoudre_ec` → `resoudre_dv`, `resoudre_la`).
La liste des arêtes autorisées (A1) le dit explicitement (`tests/python/test_imports.py`, exception nommée « assemblage de l'Étude
complète », où entre aussi l'import paresseux `parties` ~> `derivee_variations`) ; aucun autre outil ne fait de même.

## 2. Ce qui marche déjà et qu'on garde

- **Le contrat page ↔ moteur** : `monterOutil`, `resoudre` / `resoudre_json` / `apercu_json`, sortie validée par `sortie.valider`, liste blanche
  des fonctions dans le manifeste, aucun texte de corrigé en JS.
- **Le manifeste**, seule source du chargement (`test_manifeste` : complet et minimal).
- **Les garde-fous de vérité** : oracle mpmath indépendant, `valeur_verifiee`, factorisations redéveloppées, `json_strict`, `CONNUS = {}`,
  copie locale de Pyodide obligatoire.

## 3. Règles

Chaque règle a son garde-fou. « À créer » renvoie au chantier de la revue qui l'apporte.

| # | Règle | Garde-fou |
|---|---|---|
| A1 | **Les imports suivent les couches** (§ 1). La liste des arêtes internes autorisées est figée ; une arête nouvelle s'ajoute exprès, avec sa raison. | `test_noyau` (étendu à `redaction_bh`, `exp_log`, `exp_log_m` ; tout nouveau moteur d'outil réclamé) ; graphe d'imports figé par `ast` : `tests/python/test_imports.py` (liste blanche `ARETES` avec leur raison, `EXCEPTIONS` nommées, couches de § 1 vérifiées, aucun cycle hors exception) : R6, fondations F4 |
| A2 | **Règle du 2e utilisateur.** Une fonction propre à un outil y reste. Dès qu'un **deuxième** outil en a besoin, on la déplace dans `moteur/` (avec réexport sous l'ancien nom, sortie identique à l'octet), on ne la copie pas et on ne l'importe pas depuis l'autre outil. | A1 l'empêche mécaniquement (importer un autre outil échoue) ; relecture de l'audit d'étape 0 |
| A3 | **Une seule liste des outils** : `commun/registre.json` (pages) et `moteur/manifeste.json` (moteurs). Les tests en dérivent leurs listes ; une donnée propre à un outil (exemple, entrée invalide…) est dans un dictionnaire dont les clés sont vérifiées. **Un oubli fait échouer un test.** | `test_manifeste`, `test_aucun_outil_oublie` (existent) ; dérivation (`tests/python/outils_du_site.py`) et clés vérifiées (`test_outils_du_site`, `tests/pages/test_donnees_des_pages`) : R1, fondations F3 |
| A4 | **Un nouvel affichage = un type de bloc** : constructeur dans `moteur/sortie.py`, schéma dans `valider`, rendu dans `commun/rendu.js` (`BLOCS`), CSS dans `commun/composants.css`, test. Jamais de HTML écrit dans un bloc `texte`. Une page qui ne connaît pas un bloc l'annonce au lieu de le sauter. | `sortie.valider`, `test_style_commun` (existent) ; SOC-22 (bloc inconnu annoncé, dans `main` : R2, branche `r2-bloc-inconnu` fusionnée) |
| A5 | **Les nombres passent par `moteur/nombres.py`** (virgule, apostrophe, « ≈ ») ; côté JS, par `commun/nombres.js` quand il existera (R7). Une brique nouvelle n'écrit jamais `replace(".", "{,}")` elle-même. | à créer : test qui cherche ces écritures hors de `nombres.py`, avec la liste nommée des anciennes (R9 les résorbe). Format « ≈ » (D13) à trancher dans les décisions du 2e degré |
| A6 | **Une résolution, plusieurs rédactions.** Quand la rédaction dépend du niveau (année et filière), le moteur résout **une** fois et la différence est un **paramètre explicite** de la rédaction (exemple : facteur constant par produit nul « 6 = 0 impossible » en 1M, 1C et 2C, division en 3e). Jamais une copie du moteur par filière (ce qu'ont fait `exp_log_m.py` et `redaction_bh.py`). Une table de « profils de rédaction » n'est créée qu'au deuxième outil qui en a besoin (A2). | instantanés par niveau ; les solutions sont identiques d'un niveau à l'autre (oracle) |
| A7 | **Pas d'état global caché dans une brique** : tout réglage est un paramètre (`decimaux=`, `facteur_constant=`), jamais une variable de module basculée par un décorateur (comme `exp_log._DECIMAUX`). | relecture ; A1 empêche une brique de lire l'état d'EL |
| A8 | **Pas deux fichiers de même nom dans un manifeste** : le Worker les écrit à plat, par nom de fichier, et le second écraserait le premier sans rien dire. | `test_manifeste.py` (`test_aucun_nom_de_fichier_en_double`, par outil) ; `test_imports.py` (`test_noms_de_modules_uniques`, tous les modules du moteur) : R6, fondations F4 |
| A9 | **La rédaction suit les corrigés de l'enseignant** (`docs/reference/<chantier>/`, jamais commités) : on les lit avant de proposer une rédaction ; une décision qui s'en écarte est écrite dans les décisions du chantier. Une étape structurée (méthode, paramètres, résultat) plutôt que du texte seul, pour qu'une même résolution serve au corrigé et aux exercices guidés (onglet « S'entraîner »). | instantanés ; oracle sur chaque valeur affichée |

## 4. Ajouter un outil

Avant R1, environ **18 fichiers** (4 côté site, environ 14 côté tests), et la plupart des oublis passaient sans rien faire échouer.
Depuis R1 (chantier fondations, F3), les listes d'outils des tests et de `tests/lancer.py` dérivent de `tests/python/outils_du_site.py`,
qui lit le registre et le manifeste ; les données propres à un outil restent écrites à la main, mais leurs clés sont vérifiées par
`tests/python/test_outils_du_site.py` et `tests/pages/test_donnees_des_pages.py` (un outil oublié ou en trop échoue, sauf exception
nommée avec sa raison). Pour un outil à moteur Python, la liste devient :

1. `<outil>/` : le moteur, l'adaptateur `resoudre_xx.py`, `index.html` (configuration de `monterOutil`) ;
2. `moteur/manifeste.json` : module, fichiers, fonctions ;
3. les données propres à l'outil dans les tests, que les tests réclament d'eux-mêmes (environ 10 fichiers, au lieu d'environ 14 dont
   la moitié pouvait être oubliée en silence) :
   - `tests/python` : le corpus (`cas.py` ou un module à lui), `test_instantanes.py` (fonction et corpus, ou exception nommée) et
     `test_instantanes_resoudre.py` (de même, et une méthode `test_<outil>` chacun ; instantanés écrits avec `REGENERER=1`),
     `test_json_strict.OUTILS_ENTREES`, `test_resoudre_import.EXEMPLE`, `test_source_unique.TestDispositionDuClavier.PAGES`,
     `test_vocabulaire` (`ANALYSES`, ou une méthode nommée dans `METHODES`) ;
   - `tests/pages` : `rendu.py` (`REDUIT`, et `entrees` pour le corpus), `test_comportement.py` (`CALCUL`, `EXEMPLE`, `INVALIDE`),
     `test_rendu.py` (une méthode `test_<outil>`), la référence de page (`capturer_references.py`) ;
4. à la fin, après relecture à l'écran : `commun/registre.json`, la carte de l'accueil, et la butée « 16 liens / 7 outils » de
   `tests/pages/test_accueil.py`, mise à jour exprès.

Rien à écrire, ces listes dérivent du registre ou du manifeste : `tests/lancer.py` (`DOSSIERS_MOTEURS`, `OUTILS_PAGES`, variantes de
filière), `moteurs.py` (sys.path), `test_style_commun`, `test_tableaux_css`, `test_source_unique.MIGREES`, `test_vocabulaire` (dossiers
des moteurs, pages), `test_memo_garde`, `test_resoudre_import` (fichiers et module), `rendu.OUTILS`, `test_largeurs`, `captures.py`.

Et les nouvelles arêtes d'import (A1), s'il y en a, dans `ARETES` de `tests/python/test_imports.py`, chacune avec sa raison (le test
réclame toute arête nouvelle) ; un nouveau moteur d'outil entre aussi dans `test_noyau.MOTEURS` (réclamé de même).

## 5. Exceptions connues (dette à ne pas aggraver)

Elles sont tolérées ; celles qui sont des arêtes d'import (A1) sont **listées nommément** dans `tests/python/test_imports.py`
(`EXCEPTIONS`, avec leur règle et le chantier qui les résorbe ; R6, fondations F4), pour qu'aucune nouvelle ne s'y ajoute en silence :

| Exception | Règle | Chantier qui la résorbe |
|---|---|---|
| Cycles `limites_asymptotes` ⇄ `redaction_bh` (21 noms privés), `exp_log` ⇄ `exp_log_m` (31) | A1, A6 | R11 |
| `parties` et `resoudre_el` importent l'adaptateur `resoudre_ed` | A1 | R11 |
| `exp_log._DECIMAUX` | A7 | R5 : `moteur/expr.py` ne le lit pas (B1 : il reste dans `exp_log`, seul `_nb_exact` le lit, aucun état dans la brique) ; puis R10 |
| 3 parseurs (ED, `moteur/expr.py` repris d'EL avec le lexique d'EL, FA), 2 arbres d'expressions (ED, `expr`), 2 classes `Chaine` | A2 | R5 (une chaîne commune), le reste seulement si un outil en a besoin |
| 5 formats de « ≈ », `qtex` sans notation suisse | A5 | R9, outil par outil |
| HTML de la grille `.chaine` écrit dans un bloc `texte` (`resoudre_el.py`), CSS dans la page EL | A4 | R5 (CSS commun), puis un vrai type de bloc |

## 6. Ordre des chantiers

Déjà fait : **R2** (bloc inconnu visible, SOC-22), branche `r2-bloc-inconnu` fusionnée ; les branches du Mac (tests rapides, correctif
exp-log) sont fusionnées.

1. **`fondations`** : **R1, R6, R3** (A1, A3, A8 deviennent des tests ; R3 : ménage).
2. **R5** (`briques-communes`) : `moteur/expr.py`, `moteur/chaine.py` avec les options de présentation du corrigé du 2e degré (étiquette grise,
   « impossible » sous le facteur constant, texte au milieu de la chaîne), CSS `.chaine` commun, fonction « ≈ » unique, `oracle.racines`.
3. **`equations-2e-degre`** : le premier outil construit selon ces règles, avec son onglet « S'entraîner »
   (`docs/chantiers/equations-2e-degre/quiz.md`).
4. Ensuite, sans urgence : R7 à R14 de la revue.

## 7. Ligne de CLAUDE.md (ajoutée le 05.11.2026)

> Architecture : couches et règles A1–A9 dans `docs/architecture.md` ; un import entre outils, une copie d'une fonction d'un autre outil ou un
> moteur dupliqué par filière se discutent avant d'être écrits.
