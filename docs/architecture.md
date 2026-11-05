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
3. Adaptateurs      <outil>/resoudre_xx.py : seule couche qui fabrique la sortie affichée (moteur/sortie.py)
2. Moteurs d'outil  <outil>/*.py : résolution et rédaction propres à l'outil ; n'importent que moteur/
1. Briques communes moteur/ : nombres, sortie, noyau (façade de la base), et demain expr, chaine, second_degre
```

| Couche | Peut importer | Ne doit jamais importer |
|---|---|---|
| 1. Briques (`moteur/`) | d'autres briques | un moteur d'outil, un adaptateur |
| 2. Moteurs d'outil | les briques (par `moteur/noyau.py` pour la base) | un autre outil, un adaptateur |
| 3. Adaptateurs | les briques, **le moteur de leur outil** | un autre adaptateur, le moteur d'un autre outil |
| 4. Pages | `commun/` | un fichier d'un autre outil |

L'Étude complète est la seule exception voulue : c'est un outil qui **assemble** DV, LA et ED. Son moteur importe ceux de DV et LA
(`etude_complete` → `derivee_variations`, `limites_asymptotes`), et son adaptateur ceux de DV et LA (`resoudre_ec` → `resoudre_dv`, `resoudre_la`).
La liste des arêtes autorisées (A1) le dit explicitement ; aucun autre outil ne fait de même.

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
| A1 | **Les imports suivent les couches** (§ 1). La liste des arêtes internes autorisées est figée ; une arête nouvelle s'ajoute exprès, avec sa raison. | `test_noyau` (existe, à étendre à `exp_log`, `exp_log_m`, `redaction_bh`) ; graphe d'imports figé par `ast` (à créer, R6) |
| A2 | **Règle du 2e utilisateur.** Une fonction propre à un outil y reste. Dès qu'un **deuxième** outil en a besoin, on la déplace dans `moteur/` (avec réexport sous l'ancien nom, sortie identique à l'octet), on ne la copie pas et on ne l'importe pas depuis l'autre outil. | A1 l'empêche mécaniquement (importer un autre outil échoue) ; relecture de l'audit d'étape 0 |
| A3 | **Une seule liste des outils** : `commun/registre.json` (pages) et `moteur/manifeste.json` (moteurs). Les tests en dérivent leurs listes ; une donnée propre à un outil (exemple, entrée invalide…) est dans un dictionnaire dont les clés sont vérifiées. **Un oubli fait échouer un test.** | `test_manifeste`, `test_aucun_outil_oublie` (existent) ; dérivation et clés vérifiées (à créer, R1) |
| A4 | **Un nouvel affichage = un type de bloc** : constructeur dans `moteur/sortie.py`, schéma dans `valider`, rendu dans `commun/rendu.js` (`BLOCS`), CSS dans `commun/composants.css`, test. Jamais de HTML écrit dans un bloc `texte`. Une page qui ne connaît pas un bloc l'annonce au lieu de le sauter. | `sortie.valider`, `test_style_commun` (existent) ; SOC-22 (bloc inconnu annoncé, dans `main` : R2, branche `r2-bloc-inconnu` fusionnée) |
| A5 | **Les nombres passent par `moteur/nombres.py`** (virgule, apostrophe, « ≈ ») ; côté JS, par `commun/nombres.js` quand il existera (R7). Une brique nouvelle n'écrit jamais `replace(".", "{,}")` elle-même. | à créer : test qui cherche ces écritures hors de `nombres.py`, avec la liste nommée des anciennes (R9 les résorbe). Format « ≈ » (D13) à trancher dans les décisions du 2e degré |
| A6 | **Une résolution, plusieurs rédactions.** Quand la rédaction dépend du niveau (année et filière), le moteur résout **une** fois et la différence est un **paramètre explicite** de la rédaction (exemple : facteur constant par produit nul « 6 = 0 impossible » en 1M, 1C et 2C, division en 3e). Jamais une copie du moteur par filière (ce qu'ont fait `exp_log_m.py` et `redaction_bh.py`). Une table de « profils de rédaction » n'est créée qu'au deuxième outil qui en a besoin (A2). | instantanés par niveau ; les solutions sont identiques d'un niveau à l'autre (oracle) |
| A7 | **Pas d'état global caché dans une brique** : tout réglage est un paramètre (`decimaux=`, `facteur_constant=`), jamais une variable de module basculée par un décorateur (comme `exp_log._DECIMAUX`). | relecture ; A1 empêche une brique de lire l'état d'EL |
| A8 | **Pas deux fichiers de même nom dans un manifeste** : le Worker les écrit à plat, par nom de fichier, et le second écraserait le premier sans rien dire. | à créer (R6) |
| A9 | **La rédaction suit les corrigés de l'enseignant** (`docs/reference/<chantier>/`, jamais commités) : on les lit avant de proposer une rédaction ; une décision qui s'en écarte est écrite dans les décisions du chantier. Une étape structurée (méthode, paramètres, résultat) plutôt que du texte seul, pour qu'une même résolution serve au corrigé et aux exercices guidés (onglet « S'entraîner »). | instantanés ; oracle sur chaque valeur affichée |

## 4. Ajouter un outil

Aujourd'hui, environ **18 fichiers** (4 côté site, environ 14 côté tests), et la plupart des oublis passent sans rien faire échouer.
Après R1 et R6, la liste devient :

1. `<outil>/` : le moteur, l'adaptateur `resoudre_xx.py`, `index.html` (configuration de `monterOutil`) ;
2. `moteur/manifeste.json` : module, fichiers, fonctions ;
3. les données propres à l'outil dans les tests (exemple, entrée invalide, corpus réduit), que les tests réclament d'eux-mêmes ;
4. à la fin, après relecture à l'écran : `commun/registre.json` et la carte de l'accueil.

Et les nouvelles arêtes d'import (A1), s'il y en a.

## 5. Exceptions connues (dette à ne pas aggraver)

Elles sont tolérées et **listées nommément** dans le test d'imports (R6), pour qu'aucune nouvelle ne s'y ajoute en silence :

| Exception | Règle | Chantier qui la résorbe |
|---|---|---|
| Cycles `limites_asymptotes` ⇄ `redaction_bh` (21 noms privés), `exp_log` ⇄ `exp_log_m` (31) | A1, A6 | R11 |
| `parties` et `resoudre_el` importent l'adaptateur `resoudre_ed` | A1 | R11 |
| `exp_log._DECIMAUX` | A7 | R5 (la brique ne le lit pas), puis R10 |
| 3 parseurs, 2 arbres d'expressions, 2 classes `Chaine` | A2 | R5 (une chaîne commune), le reste seulement si un outil en a besoin |
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
