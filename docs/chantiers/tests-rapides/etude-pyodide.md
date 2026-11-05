# Tests rapides P7 : étude du chargement de Pyodide dans les tests de pages

Décision T9 (`decisions.md`) : **étude seule, aucun code modifié**. Mesures du 05.11.2026 sur le Mac de l'enseignant (2 cœurs physiques,
4 logiques ; Chrome 150, Pyodide 0.27.7, SymPy 1.13.3), branche `tests-rapides` (d116aa1). Scripts de mesure hors du dépôt
(`scratchpad/P7/`) ; chaque commande sous une limite de 5 min. Détail des lancements : `journal.md`, « P7 ».

## Résumé

1. **Combien.** La suite de pages charge Pyodide **122 fois** (119 vus par la sonde + 3 dans `test_pyodide_local.py`), soit
   environ **61 par processus** (`-n 2`). Par classe : `TestComportement` 78, `TestLargeurs` 15, `TestClavierIntegre` 11,
   `TestGraphique` 8, `TestRendu` 7, `TestPyodideLocal` 3 (un Chrome neuf à chaque test). Par test : 1 à 11 (record :
   `test_t35_el_filiere_de_depart_url_accueil_puis_defaut`) ; 70 tests sur 122 chargent Pyodide au moins une fois. Le simplexe et
   l'accueil ne le chargent pas.
2. **Durée d'un chargement** (de `nav.ouvrir` à « Prêt. » vu par le test, dans la suite à `-n 2`) : **6,9 s** à chaud (médiane 6,8 s),
   **18,2 s** pour la première page de chaque Chrome (cache vide, les deux processus démarrant en même temps). Page seule, sans
   charge : 5,2 à 5,5 s à chaud, 7,7 à 8,3 s à froid.
3. **Part du mur.** Les chargements font environ **960 s sur environ 2 030 s** de temps de tests de pages, soit **47 %**, environ
   **7,5 min** des 16 min de la suite de pages (974 s au rapport P6).
4. **Où va le temps** (chargement à chaud, dans la suite) : ouverture de l'onglet 0,74 s (dont **0,58 s** : démarrage du processus de
   rendu du nouvel onglet) ; HTML, KaTeX, manifeste et fichiers Python 0,4 s ; `loadPyodide` environ 2 à 2,5 s (instanciation du wasm,
   bibliothèque standard, démarrage de Python) ; import du module de l'outil 0,2 à 0,7 s ; **pause de 0,7 s voulue par la page**
   (`CALME_MS`, SymPy attend une pause de frappe) ; SymPy 1,85 s (décompression des roues 0,5 s, `invalidate_caches` 0,3 s,
   `import sympy` 0,6 s, en page seule).
5. **Cache.** Le cache HTTP sert déjà tout à chaud (0 octet transféré, sauf la revalidation des fichiers `.py`, 1,8 ko) ; le `.wasm` est
   servi en `application/wasm` et compilé en flux ; le **cache de code** de Chrome joue dès la 3ᵉ page d'un même Chrome
   (`compileStreaming` 70 ms). **SymPy précompilé** (roues `pyc`) est déjà utilisé partout, sauf dans les deux tests de repli exprès.
   Rien à gagner de ce côté.
6. **Le vrai surcoût** est la page **à froid** : chaque classe ouvre un Chrome neuf avec un profil neuf, donc un cache vide. Il y a
   10 premières pages par suite (5 classes × 2 processus) + 3 Chrome de `test_pyodide_local`, à environ **11 s de plus** chacune. L'audit
   (M7) ne comptait que les 2,2 s de démarrage de Chrome.
7. **Recommandation** : ne pas partager Pyodide entre les tests (M8 tel quel : risque d'isolement élevé, et certains tests vérifient le
   chargement lui-même). Si l'on veut gagner : (a) **onglet de réserve** (environ 35 s de mur, risque très faible), puis (b) **cache de
   Chrome gardé d'une classe à la suivante** dans un même processus (environ 45 à 60 s de mur, risque faible). Ensemble : environ
   **1,5 min** sur la suite de pages (environ 10 %). Rien n'est fait dans ce chantier (T9) : décisions à prendre en fin de rapport.

## 1. Méthode

- **Sonde de suite** (extension pytest chargée par `-p` dans les seuls lancements de mesure) : elle remplace en mémoire
  `Navigateur.__enter__`, `Navigateur.ouvrir`, `Page.appel` et `Page.attendre` par des copies qui notent chaque ouverture (test,
  processus, Chrome, page, options) et ajoutent à la page un petit script d'observation (horodatage des changements de `#etat` et des
  messages `init` / `sympy` échangés avec le worker). Rien n'est changé dans le dépôt.
- **Lots** : la suite de pages en 6 lots de moins de 5 min, chacun lancé comme `complet` (`-n 2 --dist load`) : `test_rendu` (139 s),
  `test_comportement` en deux moitiés (197 s et 201 s), `test_clavier` (185 s), `test_graphique` + `test_accueil` +
  `test_pyodide_local` (192 s), `test_largeurs` (114 s). Tous verts. `test_simplexe` n'a pas été relancé : sa page ne charge ni
  `outil.js` ni `moteur-python.js` (0 chargement, vérifié dans le code), et ses temps viennent du rapport P6.
- **Banc** (script seul, Chrome du dépôt importé tel quel) : le worker de la page est remplacé, dans la page du banc seulement, par un
  worker qui charge le vrai `commun/worker-pyodide.js` en horodatant `importScripts`, `loadPyodide`, `runPython`, `unpackArchive` ;
  ressources du worker lues par le protocole DevTools ; essais à froid et à chaud, deux Chrome successifs, rechargement du même
  onglet, profil gardé d'un Chrome au suivant, détail de `Navigateur.ouvrir`. Contrôle : sans aucun script ajouté, mêmes temps
  (7,5 s à froid puis 5,2 à 5,3 s, contre 8,1 s puis 5,2 à 5,4 s avec le banc).
- **Écart de la sonde** : la somme des temps des tests mesurés (1 773 s) dépasse d'environ 6 % celle des mêmes tests au rapport P6
  (1 672 s), dont environ 22 s viennent du découpage de `test_comportement` en deux lots (deux premières pages à froid de plus).

## 2. Mesures

### 2.1 Nombre de chargements

| Classe | Chargements | Chrome (premières pages à froid) dans la suite | Remarques |
|---|---|---|---|
| `TestComportement` | 78 | 2 | boucles sur les outils ; 13 ouvertures avec `script_initial`, 1 avec `conserver_stockage`, 2 relances du worker (délai dépassé, SOC-13) |
| `TestLargeurs` | 15 | 2 | + 2 pages du simplexe sans Pyodide |
| `TestClavierIntegre` | 11 | 2 | 9 ouvertures tactiles, 8 avec agent utilisateur imposé |
| `TestGraphique` | 8 | 2 | `script_initial` (banc du graphique) à chaque ouverture |
| `TestRendu` | 7 | 2 | une page par outil, puis tout le corpus dans la même page |
| `TestPyodideLocal` | 3 | 3 | un Chrome neuf par test ; deux tests de repli vers le paquet SymPy du CDN |
| `TestAccueil` | 0 (2 interrompus) | — | `test_goatcounter…` ouvre deux pages outils sans attendre Pyodide |
| `TestSimplexe` | 0 | — | page sans Pyodide |
| **Total** | **122** | **13** | 61 environ par processus |

### 2.2 Durée d'un chargement (dans la suite, `-n 2`)

| Phase (moyennes) | À chaud (107 pages) | Première page d'un Chrome (12 pages) |
|---|---|---|
| `nav.ouvrir` jusqu'à la navigation (fermer l'onglet, en créer un, l'intercepter, l'attacher) | 0,74 s | 0,74 s |
| navigation → worker lancé (HTML, KaTeX, manifeste, fichiers `.py`) | 0,41 s | 0,85 s |
| `init` : `loadPyodide` + import du module de l'outil | 3,13 s | 10,17 s |
| pause avant SymPy (`CALME_MS` de la page) | 0,68 s | 0,71 s |
| `sympy` : roues précompilées + `import sympy` | 1,85 s | 5,48 s |
| navigation → « Prêt. » (page) | 6,08 s (médiane 5,94) | 17,20 s |
| `nav.ouvrir` → « Prêt. » vu par le test | **6,91 s** | **18,17 s** |

Par rang dans un même Chrome (navigation → « Prêt. ») : 1ʳᵉ page 17,2 s ; 2ᵉ 6,4 s ; 3ᵉ 5,7 s ; suivantes 6,1 s.

**Page seule, sans charge** (banc, factorisation) : 1ʳᵉ page 7,7 à 8,3 s, 2ᵉ 6,6 à 6,9 s, puis 5,2 à 5,5 s. Détail d'une page à chaud
(ms depuis la navigation) : worker à 280 ; `loadPyodide` de 290 à 2 220 ; `import resoudre_fa` 2 230 → 2 440 ; pause jusqu'à 3 160 ;
roues décompressées 3 160 → 3 640 ; `invalidate_caches` 3 640 → 3 920 ; `import sympy` 3 920 → 4 500 (« Prêt. »). À froid,
`loadPyodide` prend 4,4 s au lieu de 1,9 s : les fichiers arrivent pourtant en moins de 0,4 s ; le surcoût est la compilation (wasm
et JavaScript) sans cache de code. Dans la suite, les deux processus font leur première page en même temps : 17 s au lieu de 8 s.
Étude complète (13 fichiers Python) : mêmes ordres de grandeur (5,5 s à chaud ; import du module 0,45 s).

### 2.3 Part du mur des pages

| | Somme | Part |
|---|---|---|
| Temps des tests de pages (rapport P6) | 1 932 s (mur 974 s à `-n 2`) | 100 % |
| `nav.ouvrir` → « Prêt. », 122 chargements | environ 960 s | **47 %** (environ 460 s de mur) |
| dont surcoût des premières pages (13 × 11 s environ) | environ 140 s | 7 % |
| dont démarrage du rendu des nouveaux onglets (122 × 0,58 s) | environ 70 s | 4 % |
| dont pause `CALME_MS` de la page (122 × 0,7 s) | environ 85 s | 4 % |
| dont reste du chargement à chaud (Pyodide, module, SymPy) | environ 660 s | 34 % |
| Démarrage de Chrome (16 classes × processus + 3) | environ 50 s | 2,5 % |

Les tests les plus marqués : `test_t35_el_filiere_de_depart_url_accueil_puis_defaut` (11 chargements, 84 s : le test entier),
`test_t33_selecteur_absent_des_autres_outils` (5, 34 s sur 37 s), `test_t40_l_apercu_ne_attend_pas_sympy` (4, 31 s sur 31 s). À
l'inverse, `test_traces_egales_aux_references` (1 chargement, 9 s sur 123 s) et les tests du clavier `test_c_…` (2 chargements, 11 à
24 s sur 78 à 101 s) coûtent ailleurs.

### 2.4 Cache du navigateur, paquets, SymPy précompilé

- **Cache HTTP** : à partir de la 2ᵉ page d'un Chrome, aucune ressource n'est retéléchargée (taille transférée 0), y compris les
  fichiers de Pyodide réécrits vers le serveur de test par l'intercepteur ; seuls les fichiers `.py` sont revalidés (`cache:
  "no-cache"` dans `moteur-python.js`, 1,8 ko en tout). KaTeX vient du réseau (jsDelivr) à la 1ʳᵉ page seulement.
- **Type MIME** : le serveur de test sert le `.wasm` en `application/wasm` (Python 3.12) : Pyodide compile en flux
  (`instantiateStreaming`).
- **Cache de code** : dans un worker chargé, `compileStreaming` du wasm prend 70 ms (cache de code utilisé), `WebAssembly.compile`
  d'un tampon 30 à 40 ms (compilation paresseuse). Chrome crée ce cache à la 2ᵉ page et s'en sert à la 3ᵉ : d'où la 2ᵉ page un peu
  plus lente.
- **SymPy précompilé** : le manifeste donne les roues `pyc` du site (SymPy 6,6 Mo, mpmath 0,7 Mo), téléchargées pendant `loadPyodide`
  (terminées avant d'en avoir besoin) ; le repli vers le paquet du CDN ne sert que dans les deux tests faits pour lui.
- **Profil** : chaque `Navigateur` crée un profil neuf (`tempfile.mkdtemp`) et un port HTTP au hasard : rien ne passe d'une classe à la
  suivante. Banc « profil gardé » (même profil, même port, trois Chrome successifs, page seule) : 1ʳᵉ page de chaque Chrome 8,3 s,
  puis 6,6 s, puis 5,5 s ; avec un port différent à chaque Chrome, 8,2 s, 7,0 s, 6,7 s (le cache des fichiers réécrits est lié au port).
- **Onglet** : la 1ʳᵉ attache à un onglet neuf attend 0,58 s (démarrage de son processus de rendu), quelle que soit la connexion qui
  s'attache en premier. Banc « rechargement du même onglet » : 4,4 à 4,5 s, contre 5,2 à 5,5 s pour un onglet neuf.

## 3. Ce qui serait partageable, et à quel risque

| Option | Gain estimé (mur des pages) | Risque d'isolement entre tests | Remarques |
|---|---|---|---|
| **A. Onglet de réserve** : `ouvrir` crée et intercepte d'avance l'onglet suivant (`about:blank`), pendant le test en cours | environ **35 s** (122 × 0,58 s / 2) | **très faible** : chaque page reste dans un onglet neuf, jamais utilisé ; seul change le moment où il est créé | `navigateur.py` seul ; un onglet vide de plus par Chrome |
| **B. Cache de Chrome gardé d'une classe à la suivante** dans un même processus (profil par processus et port fixe par processus, Chrome toujours neuf par classe) | environ **45 à 60 s** (premières pages : 8 à 11 sur 13 deviennent chaudes) | **faible** : seuls le cache HTTP et le cache de code passent ; même origine d'une classe à l'autre, mais les pages n'utilisent que `localStorage` et `sessionStorage`, vidés à chaque ouverture (sauf `conserver_stockage`, voulu, dans un même test) ; aucun `indexedDB`, `serviceWorker`, `caches` ni cookie dans les pages | profil propre à la session (jamais réutilisé d'un lancement à l'autre) ; `test_pyodide_local` en profiterait aussi, ce qui change son point de départ (cache chaud) sans changer ce qu'il vérifie (requêtes interceptées, repli) |
| **C. Chrome partagé par processus** (M7, refusé par T8) | environ **60 s** (B + 14 démarrages de Chrome évités) | faible à moyen : un Chrome planté fait échouer toutes les classes suivantes du processus | T8 reposait sur « gain inférieur à 20 s » : le surcoût des premières pages (environ 11 s chacune) n'y était pas compté |
| **D. Recharger le même onglet** au lieu d'en ouvrir un neuf | environ 50 s (122 × 0,8 s / 2) | **moyen** : même cible, donc émulation tactile, agent utilisateur et scripts `addScriptToEvaluateOnNewDocument` à défaire à chaque fois ; journaux de la page à remettre à zéro | A donne la plus grande part du gain sans ce risque |
| **E. Pyodide gardé entre les tests** (même page pour plusieurs tests, M8) | jusqu'à environ 5 à 6 min | **élevé** : DOM, `localStorage`, état du worker et du moteur Python, options d'ouverture (`script_initial` ×21, tactile ×9, agent ×8 dans les lots) partagés ; `test_t31…`, `test_t40…`, `test_t35…filiere_de_depart…`, `test_pyodide_local` vérifient le chargement lui-même | change ce que chaque test vérifie (un état neuf) : contraire à `decisions.md` §0 ; **non recommandé** |
| **F. Relancer seulement le worker** dans une page gardée | ≤ D | moyen (DOM gardé) | impossible sans modifier les pages ; Pyodide se charge dans le worker, donc presque aucun gain sur D |
| **G. Changer le chargement lui-même** (pause `CALME_MS`, `invalidate_caches`, instantané Pyodide) | jusqu'à environ 40 s pour la pause seule | aucun pour les tests, mais **c'est le site** qui change | hors chantier : comportement voulu pour l'élève (`test_t40` le vérifie) ; à décider pour le site, pas pour les tests |
| **H. Cache HTTP, type MIME, SymPy précompilé** | 0 | — | déjà en place et efficaces (§ 2.4) |

Classement par gain / risque : **A** (meilleur rapport), puis **B** (ou **C**, si l'on accepte de rediscuter T8), loin devant **D** ; **E**
et **F** écartés ; **G** relève du site ; **H** sans objet.

## 4. Recommandation

- Ne pas partager Pyodide entre les tests (E, F) : le gain est réel, mais il retire à chaque test son état neuf, et plusieurs tests
  vérifient justement le chargement.
- Si l'enseignant veut gagner sur la suite de pages, une partie de code dans un chantier suivant, limitée à `tests/pages/navigateur.py` :
  **A puis B**, environ 1,5 min de mur (974 s → environ 890 s), vérifiée comme les autres parties (mêmes listes, mêmes sous-tests,
  test du clavier 20 fois seul et 20 fois sous charge, car A et B changent le minutage des ouvertures).
- Gain modeste au regard de la suite complète (environ 28 min) : on peut aussi ne rien faire.

## 5. À décider

1. **Faire A (onglet de réserve)** dans une partie suivante ? (environ 35 s, risque très faible, `navigateur.py` seul)
2. **Faire B (cache gardé d'une classe à la suivante)**, ou **rouvrir T8** pour C (Chrome partagé) au vu de ces mesures ? (environ 45 à
   60 s)
3. **Confirmer l'abandon de E** (Pyodide gardé entre les tests, M8).
4. **G (hors chantier)** : la pause de 0,7 s avant SymPy et `invalidate_caches` (0,3 s) coûtent à chaque élève aussi ; faut-il les
   étudier pour le site ?
