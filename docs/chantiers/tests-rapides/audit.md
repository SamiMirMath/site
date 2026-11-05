# Tests rapides, étape 0 : rapport d'audit (aucun fichier du dépôt modifié)

Audit fait le 04.11.2026 sur la branche `etude-complete` (commit 4b98d12), sans modifier ni le code ni les tests, sans commit ni branche.
Seul ce fichier est écrit. Les scripts de mesure (sonde, comptages) sont restés dans le dossier temporaire de la session.

## Résumé

1. **Mesures** (Mac de l'enseignant, 2 cœurs physiques, 4 logiques) : suite Python **718 s** (1290 passés, 1 xfail, 101 641 sous-tests, 4 workers) ; suite de pages **944 s** (121 passés, 2 382 sous-tests, 2 workers). Les deux sont vertes (code de retour 0).
2. **Les deux suites sont déjà saturées** : ajouter des workers ne gagne rien (pages : `-n 3` = 283 s contre 279 s à `-n 2` sur le même lot ; chaque test y est 36 % plus lent).
3. **Le coût vient de calculs refaits**, pas de la collecte (1 s), ni de Chrome (2 s), ni de l'installation. Un seul test Python fait 162 s : `test_les_deux_signes_zero_sont_ecrits` relance l'outil Limites sur tout le corpus pour chaque cas (boucle quadratique).
4. Dans les 12 fichiers de l'outil Limites, `la.etudier` est appelé **3 556 fois pour 354 entrées distinctes**. Dans deux fichiers de l'outil Exponentielles et logarithmes, l'oracle `racines` est appelé **472 fois pour 162 équations**.
5. Côté pages, chaque test rouvre sa page et recharge Pyodide et SymPy : environ 6 s par page seule, soit environ 120 chargements dans la suite.
6. **Test instable du clavier, cause probable** : après « Calculer ▶ », la page lance un défilement doux (`commun/outil.js:329`) qui l'emporte sur le défilement instantané du test. Sous charge, la touche « C » finit au bord haut de l'écran (centre à 5 px) ; un peu plus haut, l'appui tombe hors de l'écran et « effacer » laisse la formule.
7. **Plus gros gain : le double contrôle du chef d'orchestre**. Il relance aujourd'hui les 28 minutes de suite complète pour chaque partie. Un rapport signé par `lancer.py` (empreinte des fichiers testés, liste des tests passés) le remplacerait par une vérification d'une minute, plus `rapide`. Gain : **environ 26 min par partie**.
8. **Ensuite** : stabiliser le test du clavier (environ 6 min par lancement de la suite de pages, en moyenne) ; puis mettre en cache, dans les tests, ce qui est recalculé (`la.etudier`, `racines`, la boucle quadratique) : 3 à 4 min par suite Python.
9. **Contrainte respectée par construction** : aucune mesure ne retire, ne saute ni n'affaiblit un test. Chaque partie se vérifie en comparant à la référence la liste des identifiants collectés et passés, et les nombres de sous-tests.
10. **Découpage proposé** : 8 parties (un commit chacune), décrit en fin de rapport. Gain attendu : environ 60 min → environ 27 min par partie de chantier.

## 1. Mesures

### 1.1 Commandes

Les commandes sont celles de `python3 tests/lancer.py complet` (même `uv`, mêmes options), plus `--durations=40` et un rapport JUnit
(liste des tests passés et temps de chacun). Les deux suites sont lancées séparément, la machine ne faisant rien d'autre :

```
uv run -q --no-project --python 3.12 --with sympy==1.13.3 --with mpmath==1.3.0 --with websockets --with pytest --with pytest-xdist \
  python -m pytest tests/python -n auto -q -p no:cacheprovider -W ignore --durations=40 --junitxml=python.xml
uv run … python -m pytest tests/pages -n 2 --dist load -q -p no:cacheprovider -W ignore --durations=40 --junitxml=pages.xml
```

`-n auto` donne **4 workers** : pytest-xdist 3.8.0 sans `psutil` prend `os.cpu_count()` = 4 cœurs logiques. Les mesures du 29.10.2026
écrites dans `CLAUDE.md` (322 s et 589 s) ne valent plus : la suite a grandi depuis.

### 1.2 Résultats

| Suite | Mur | Résultat | Somme des temps des tests | CPU (user + sys) | Collecte |
|---|---|---|---|---|---|
| Python (`-n auto` = 4) | 718 s (12 min) | 1290 passés, 1 xfail (P10), 101 641 sous-tests ; code 0 | 2 745 s | 2 622 s | 0,97 s pour 1 291 tests (2 s avec le démarrage) |
| Pages (`-n 2`) | 944 s (15 min 44 s) | 121 passés, 2 382 sous-tests ; code 0 | 1 879 s | 1 382 s | négligeable |

**Python.** La somme des temps divisée par 4 donne 686 s, pour 718 s de mur : la répartition est bonne (96 %). Mais les 4 workers se
partagent 2 cœurs physiques. Le test le plus long prend **162 s** dans la suite et **87 s** seul : chaque test y est donc 1,86 fois plus lent.
Plus de workers ne gagnerait rien. Le mur ne baisse que si le **travail** baisse. Règle de calcul utilisée plus bas :
**mur ≈ somme des temps × 0,262** (718 / 2 745).

Coût fixe négligeable : la collecte prend 1 s par worker et l'import des moteurs avec SymPy 0,5 s. Aucun `conftest.py`, aucune fixture.
Les tests sont des `unittest.TestCase` (seul `test_corpus_etude_complete.py` est en fonctions pytest).

Fichiers les plus lourds (somme des temps dans la suite, sur 2 745 s) :

| Fichier | Somme | Plus long test |
|---|---|---|
| `test_explog_3c.py` | 517 s | 99 s (`TestImplicationsAutresFamilles`) |
| `test_redaction_bh_3m.py` | 269 s | **162 s** (`TestStructure::test_les_deux_signes_zero_sont_ecrits`) |
| `test_exp_log_m_t36.py` | 247 s | 69 s |
| `test_exp_log_m.py` | 234 s | 45 s |
| `test_exercices_el_m.py` | 220 s | 43 s |
| `test_parties_ec.py` | 118 s | 18 s |
| `test_redaction_limites.py` | 117 s | 16 s |
| `test_doctrine_bh.py` | 109 s | 18 s |

Les quatre fichiers de l'outil Exponentielles et logarithmes (3C et M) font à eux seuls 1 218 s, soit 44 % du total.

**Pages.** La somme des temps divisée par 2 donne exactement le mur : la répartition est parfaite. Répartition par fichier :
`test_comportement` 701 s, `test_simplexe` 249 s, `test_clavier` 236 s, `test_rendu` 227 s, `test_graphique` 208 s, `test_largeurs` 192 s,
`test_pyodide_local` 44 s, `test_accueil` 22 s. Plus longs tests :
- `test_graphique::test_traces_egales_aux_references` : 118 s ;
- `test_clavier::test_c_abc_et_123…` : 83 s ;
- `test_clavier::test_c_abc_rouvre…` : 77 s ;
- `test_comportement::test_t35_el_filiere_de_depart…` : 76 s ;
- `test_rendu::test_exponentielles_logarithmes` : 75 s.

### 1.3 Installation, chargement, parallélisme (mesures ciblées, chacune sous `timeout 300`)

- **Démarrage de Chrome et du serveur** (`Navigateur.__enter__`) : **2,2 s**. Avec 8 classes et 2 workers, cela fait au plus 16 démarrages,
  soit environ 35 s de somme. C'est négligeable.
- **Ouverture d'une page outil jusqu'à « Prêt. »**, page seule : 8,3 s à froid, puis **5,3 à 6,6 s**. Le HTML seul se charge en 1 s ;
  le reste est Pyodide, puis SymPy.
- **Nombre de chargements** : chaque `nav.ouvrir` ferme l'onglet précédent, donc chaque ouverture recharge Pyodide. Le code compte environ
  120 ouvertures de pages outils, boucles comprises (`test_comportement` à lui seul : environ 73). Le simplexe n'utilise pas Pyodide.
  Le chargement de Pyodide pèse donc environ 12 à 18 min de somme, soit 40 à 60 % de la suite de pages.
- **Processeur pendant les pages** (`test_rendu.py`, `-n 2`, `top` toutes les 2 s) : 47 % d'inactivité en moyenne sur les 4 cœurs logiques.
  Ce chiffre trompe : le même lot (`test_largeurs.py` + `test_graphique.py`, 19 tests) prend **279 s à `-n 2`** et **283 s à `-n 3`**.
  À `-n 3`, la somme des temps passe de 444 s à 602 s : chaque test est plus lent et les délais d'attente sont plus près d'être atteints.
- **xdist et classes** : avec `--dist load`, chaque worker reçoit les tests dans l'ordre de la collecte (xdist 3.8.0, `scheduler/load.py`).
  Une classe est donc d'un seul tenant dans chaque worker : au plus deux `setUpClass` (deux Chrome) par classe.

### 1.4 Calculs refaits (comptages, tests lancés en entier avec un simple compteur)

Les deux comptages ont été faits avec une extension pytest placée hors du dépôt, qui enveloppe la fonction sans changer son résultat.
Les deux lancements sont verts (250 passés et 37 456 sous-tests pour le premier).

| Fonction | Fichiers | Appels | Entrées distinctes | Temps cumulé | Avec un cache par processus | Une fois par entrée |
|---|---|---|---|---|---|---|
| `limites_asymptotes.etudier` (appels de premier niveau) | 12 fichiers de l'outil Limites (`test_redaction_bh_3m`, `test_redaction_limites`, `test_doctrine_bh`, `test_tableau_limites`, `test_corpus_limites_3m`, `test_limites_d12_d16`, `test_resoudre_la`, `test_instantanes`, `test_instantanes_resoudre`, `test_garde_fou_limites`, `test_limites_deux_cotes`, `test_vocabulaire`) | 3 556 | 354 | 650 s | 191 s | 78 s |
| `racines` (oracle de `test_exp_log_m.py`, importé ailleurs) | `test_explog_3c`, `test_exp_log_m_t36` | 472 | 162 | 734 s | 501 s | 241 s |

Les temps sont mesurés dans un lancement à 4 workers : ils sont gonflés comme ceux de la suite et se comparent aux sommes du § 1.2.

D'où viennent ces répétitions :
- **`test_redaction_bh_3m.py::TestStructure`** : chaque test parcourt `toutes()`, qui relance `la.etudier` sur toutes les entrées (environ 11 s
  dans la suite). `test_les_deux_signes_zero_sont_ecrits` rappelle `toutes()` **pour chaque cas** de valeur 0 : 162 s.
  Les 9 tests de la classe font 248 s, pour un calcul qui en vaut un seul.
- **`test_doctrine_bh.py`** : `test_outil_limites` et `test_pas_bh_sans_hypotheses_affichees` relancent chacun `la.etudier` sur le même
  corpus `ENTREES`. Les autres fichiers de l'outil Limites relancent les mêmes entrées (exemples de la page, corpus 3M).
- **`racines(s)`** : un balayage d'environ 5 230 points en mpmath à 30 chiffres, puis des bissections, soit environ 1 à 3 s par équation.
  Il est appelé **dans la boucle des variantes** (une fois par méthode du corrigé), dans `test_explog_3c.py` (`_oracle_famille`,
  `TestImplicationsAutresFamilles`) et dans `test_exp_log_m_t36.py`. Les mêmes équations y sont reprises en 3C et en M.
  Profil de `test_explog_3c.py::TestToutesLesFamilles::test_oracle_0` : 97 s, dont 96,6 s dans `racines` (36 appels pour 19 équations).

## 2. Test instable du clavier

Test : `tests/pages/test_clavier.py::TestClavierIntegre::test_a_deux_formules_aux_touches_donnent_le_corrige_de_la_saisie_directe`
(page Limites). Symptôme : « effacer » laisse `(x^2-1)/(x-3)`, c'est-à-dire le premier appui de la deuxième formule, qui suit un calcul.

### 2.1 Ce que fait le test à cet endroit

1. `page.toucher("#clavier button.lancer")` lance le calcul.
2. `corrige(page)` attend la première carte, puis clique « Tout afficher ».
3. `toucher_valeur(page, '#clavier button[data-k="clear"]', "")` : `Page._centre_immobile` fait un `scrollIntoView` **instantané** (centre),
   attend 6 mesures identiques à 50 ms d'intervalle (0,3 s d'immobilité), puis envoie l'appui au centre mesuré.

Côté page, `afficher` → `poserCartes(1, true)` → `montrer(1, defiler=true)` lance un défilement **doux** vers la première carte
(`der.scrollIntoView({behavior: "smooth", block: "nearest"})`, `commun/outil.js:329`). À l'étape 3, ce défilement peut être en cours.

### 2.2 Sonde (hors du dépôt : `Page._centre_immobile` et `Page.toucher` remplacés en mémoire par des copies qui journalisent)

| Essais | Position de « C » avant le calcul | Position de « C » après le calcul (scrollY final ; centre de « C » dans l'écran de 800 px) | Élément sous le doigt | Résultat |
|---|---|---|---|---|
| 6 essais seuls | scrollY 163 ; y = 400 (centré) à chaque fois | 165 ; 273 ; 315 ; 273 ; 315 ; 292 (y = 398 à 248) | « C » | 6 réussites |
| 5 essais sous charge (2 processus qui occupent le processeur, comme à `-n 2`) | 163 ; y = 400 | 268 ; 165 ; 398 ; **541 (y = 22)** ; **558 (y = 5)** | « C » | 5 réussites |

Constats :
- **Le centrage du test ne tient pas après un calcul** : la page étant la même, la position finale de « C » varie d'un essai à l'autre.
  Le défilement doux de la page et le défilement instantané du test se concurrencent.
- **Sous charge, « C » remonte jusqu'au bord haut de l'écran** (centre à 5 px, touche de 44 px à moitié cachée).
- Dès que le défilement va environ 20 px plus loin, le centre mesuré est hors de l'écran. L'appui ne touche alors aucun élément, aucun clic
  n'est produit, et `attendre_valeur` échoue au bout de 10 s avec la formule précédente : c'est exactement le symptôme.
- L'attente d'immobilité ajoutée au chantier « Clavier intégré » (`docs/chantiers/clavier-integre/suivi.md`, partie 2, « Écart rencontré ») vérifie que la page **ne bouge plus**. Elle ne
  vérifie pas que la touche est **dans l'écran**.
- La sensibilité à la charge explique les observations : échecs surtout dans la suite complète, de 1 sur 3 à 1 sur 6 lancé seul.

**Cause probable** (non reproduite en 11 essais instrumentés, mais la dérive mesurée y mène directement) : un appui envoyé à une
position hors de l'écran, parce que le test ne vérifie pas où est la touche après la fin du défilement de la page. **La page n'est pas
en défaut** : un élève ne touche pas une touche qu'il ne voit pas.

### 2.3 Correction proposée (dans le harnais, aucun test affaibli)

Dans `Page._centre_immobile` (`tests/pages/navigateur.py`) :
1. attendre l'immobilité **avant** le `scrollIntoView` aussi ;
2. après l'immobilité, vérifier que le rectangle de l'élément est **entièrement dans l'écran**, sinon recentrer et attendre de nouveau
   (3 essais au plus) ;
3. dans `toucher`, vérifier que `document.elementFromPoint(x, y)` est l'élément visé ou l'un de ses descendants. Sinon, lever une erreur
   claire (« la touche n'est pas sous le doigt ») au lieu d'un appui perdu.

L'appui reste un vrai toucher sur la vraie touche, et toutes les assertions restent. Le contrôle (3) rend même le harnais plus strict.
Tous les tests tactiles en profitent (`test_clavier`, simplexe partie F, graphique).

## 3. Mesures proposées

Pour chaque mesure : le gain (avec sa base de calcul), les risques, ce qui pourrait changer l'ensemble des tests passés, et la vérification.

**Vérification commune à toutes les parties : la référence.** Lancer deux fois `complet` sur le commit de départ avec `--junitxml`, puis
garder hors de git (dossier temporaire) :
- la sortie de `--collect-only -q` des deux suites ;
- la liste des identifiants **passés**, **xfail** et **sautés** (JUnit) ;
- les nombres de sous-tests (101 641 et 2 382 aujourd'hui).

Les deux lancements disent si ces nombres sont stables. Les tirages au hasard de certaines pages pourraient faire varier les sous-tests
de pages ; ce point est à établir. Après chaque partie, ces listes doivent être **identiques**.

### M1. Double contrôle du chef d'orchestre allégé (rapport signé par `lancer.py`)

**Aujourd'hui** : pour chaque partie, le sous-agent lance au moins une fois `complet` (28 min), puis le chef d'orchestre relance tout
(28 min), soit au moins 56 min. Le second lancement ne vérifie qu'une chose : que le premier a bien eu lieu, sur les bons fichiers, et qu'il était vert.

**Proposition** :
- `python3 tests/lancer.py complet --rapport <dossier>` écrit, en plus de la sortie habituelle, les deux fichiers JUnit et un
  `rapport.json`. Ce fichier contient le commit `HEAD`, l'empreinte (`git hash-object`) de chaque fichier modifié ou non suivi au début
  du lancement, les codes de retour, les durées, la liste des tests passés, xfail et sautés, et les nombres de sous-tests.
- `python3 tests/lancer.py verifier <dossier>`, lancé par le chef d'orchestre **après le commit**, contrôle trois points :
  (a) chaque fichier du commit a, dans `HEAD`, l'empreinte notée pendant le lancement ;
  (b) aucun autre fichier n'était modifié pendant le lancement, hors d'une liste permise (`CLAUDE.md` en cours de modification par vous) ;
  (c) les deux codes valent 0, aucun test n'a disparu par rapport à la référence de la partie précédente et aucun test n'est sauté en plus.
  Puis le chef d'orchestre lance `rapide`, un contrôle indépendant de quelques minutes.
- **Une** suite complète relancée par le chef d'orchestre en fin de session, sur le dernier commit, et non plus une par partie.

**Gain** : 28 min de suite remplacées par environ 1 min de vérification, plus `rapide` (souvent moins de 5 min sur les fichiers de la
partie) : **environ 22 à 26 min par partie**.

**Risques** :
- Le lancement n'est plus refait de façon indépendante : un état local (fichier non suivi, cache) qui fait passer la suite chez le
  sous-agent ne serait vu qu'en fin de session. Le point (b), `rapide` et la suite de fin de session limitent ce risque.
- Ce dispositif établit la confiance par le contrôle et non par la répétition. C'est à vous de décider s'il vous suffit.

**Ensemble des tests passés** : inchangé (aucun test touché).

**Vérification** :
- sur une partie test, lancer `complet --rapport`, commiter, puis `verifier` : la vérification doit être verte ;
- modifier ensuite un fichier commité sans relancer : `verifier` doit refuser ;
- ajouter un fichier non suivi pendant le lancement : `verifier` doit le signaler.

La règle de `CLAUDE.md` (« lancer la suite complète avant chaque commit ») ne change pas. Seul le contrôle du chef d'orchestre change ;
le texte qui le décrit est à valider par vous.

### M2. Stabiliser le test du clavier (§ 2.3)

**Gain** : en session 2, `test_clavier` a fait échouer 3 lancements de la suite de pages sur 10 (contrôles de R1 et de P9, 2ᵉ lancement de P6).
Chaque échec a coûté au moins 6 relances du test seul (6 × 35 s ≈ 3,5 min), souvent une suite de pages entière (16 min), et un temps de
diagnostic. Espérance : 0,3 × (16 + 3,5) ≈ **6 min par lancement de la suite de pages**, soit environ 12 min par partie avec le contrôle
d'aujourd'hui, et environ 6 min avec M1. Une suite qui n'échoue plus au hasard rend aussi M1 plus sûr.

**Risques** : faibles. Il ne faut pas masquer un vrai défaut de la page : le recentrage est borné à 3 essais, et l'erreur de l'étape 3
est explicite.

**Ensemble des tests passés** : inchangé. Le test doit passer à chaque fois au lieu de 4 à 5 fois sur 6.

**Vérification** :
- la sonde du § 2.2 (le test lancé 20 fois de suite, seul puis sous charge de 2 processus) : 20 réussites sur 20 ;
- deux suites de pages vertes ;
- `--collect-only` identique.

### M3. Boucle quadratique de `test_redaction_bh_3m.py::TestStructure`

Calculer une seule fois, au niveau de la classe, la liste des rédactions descendantes `(saisie, ou, descente)` (par exemple dans
`setUpClass`), puis faire parcourir cette liste à chaque test, au lieu de relancer `la.etudier` à chaque appel de `toutes()`.

**Gain** : les 9 tests de la classe font 248 s dans la suite. Le calcul vaut environ 11 s. Avec la répartition sur 4 workers, il est
fait au plus 4 fois (environ 45 s). Gain : environ 200 s de somme → **environ 50 s de mur**. Le test le plus long de la suite (162 s)
disparaît aussi.

**Risques** : un test qui modifierait une rédaction (une liste ou un dictionnaire partagés) gênerait les suivants. Lecture faite : les
tests de la classe ne modifient rien, mais une copie profonde par test (`copy.deepcopy`, quelques millisecondes) supprime ce risque.
Aucun `mock` dans ce fichier.

**Ensemble des tests passés** : inchangé ; même nombre de sous-tests (chaque `subTest` reste dans sa boucle).

**Vérification** : listes de référence identiques ; nombre de sous-tests de `test_redaction_bh_3m.py` identique avant et après
(lancement du fichier seul).

### M4. Cache des sorties de l'outil Limites, réservé aux tests sans `mock`

Un petit module de test (par exemple `tests/python/memo.py`) expose `etudier_la(entree)` : un `functools.lru_cache` qui rend une
**copie profonde** du résultat. Il est utilisé à la place de `la.etudier` dans les fichiers qui relisent les mêmes entrées sans rien
remplacer dans le moteur : `test_doctrine_bh`, `test_redaction_bh_3m`, `test_tableau_limites`, `test_corpus_limites_3m`, et les classes sans
`mock` des autres fichiers.

Le module est un simple module Python, et non une fixture pytest : les tests restent des `unittest.TestCase`, lançables avec
`python -m unittest` comme l'indiquent leurs en-têtes.

**Gain** : dans les 12 fichiers de l'outil Limites, 650 s de somme → 191 s avec un cache par processus, soit au plus environ 460 s de
somme, ou **2 min de mur** (× 0,262). M3 en prend déjà une partie, et les fichiers avec `mock` restent hors du cache : compter
**1 à 1,5 min** de plus que M3.

**Risques** :
- **`mock`** : `test_garde_fou_limites.py` remplace `sp.limit` puis appelle le moteur ; `test_redaction_limites.py`, `test_limites_d12_d16.py`
  et `test_vocabulaire.py` contiennent aussi des `mock.patch`. Un cache global (qui remplacerait `la.etudier` lui-même) y rendrait un
  résultat calculé **sans** le remplacement : le garde-fou serait faussé. D'où un cache **explicite**, jamais un remplacement du moteur,
  et un test de garde : aucun fichier qui importe `memo` ne contient `mock`.
- **État partagé** : copie profonde à chaque lecture. Un état global du moteur (précision de mpmath, caches de SymPy) rendrait déjà
  aujourd'hui les résultats dépendants de l'ordre des tests, ordre qui varie avec xdist : le cache n'ajoute pas ce risque.
- **Tests qui écrivent dans les mêmes fichiers** : aucun. Les instantanés ne s'écrivent qu'avec `REGENERER=1`, et le cache est en mémoire,
  propre à chaque processus, jamais sur disque.

**Ensemble des tests passés** : inchangé.

**Vérification** :
- listes de référence identiques ;
- un interrupteur `MEMO=0` (cache coupé) pour comparer une fois les deux lancements ;
- un test qui vérifie, sur quelques entrées, que `etudier_la` rend une copie égale à `la.etudier` et qu'en modifier une ne change pas la suivante.

### M5. Cache de l'oracle `racines`

`racines(s)` (`tests/python/test_exp_log_m.py`) ne dépend que de `s.g` et `s.d` (lus par `ecart`) et du contexte `MP`, fixé à 30 chiffres.
Le mettre en cache par processus, avec pour clé une représentation fidèle des deux arbres. Il faut vérifier qu'elle est injective (les
arbres eux-mêmes s'ils sont hachables).

**Gain** : sur `test_explog_3c` et `test_exp_log_m_t36`, 734 s de somme → 501 s, soit **environ 1 min de mur**. Une variante regroupe sur un
même worker les quatre fichiers qui appellent `racines` (`--dist loadgroup` et `xdist_group`) : on descendrait vers 241 s, soit environ
2 min de mur. Mais ce groupe pourrait devenir le chemin critique d'un worker. Ce n'est à garder que si la mesure le montre (partie à part).

**Risques** : l'oracle reste exactement le même (même balayage, même précision) ; seul son résultat est réutilisé. **Il ne faut pas**
accélérer `racines` lui-même (grille en flottants, moins de points) : cela changerait ce que l'oracle détecte, donc l'affaiblirait.
Rendre une copie de la liste (des `mpf`, non modifiés par les tests).

**Ensemble des tests passés** : inchangé.

**Vérification** : listes de référence identiques ; nombres de sous-tests des 4 fichiers identiques ; une comparaison unique, avec et
sans cache, des racines trouvées pour toutes les clés.

### M6. `rapide` : relancer aussi les pages de l'outil dont un moteur change

Aujourd'hui, modifier un moteur `.py` (par exemple `limites-asymptotes/limites_asymptotes.py`) ne relance **aucun** test de pages
(`outils_de_pages` ignore les `.py`), alors que les pages chargent ces moteurs dans Pyodide (références de `test_rendu`). Ajouter la page
de l'outil, à corpus réduit.

**Gain** : aucun en temps sur `complet`. Le gain est de trouver plus tôt, pendant le travail, un échec de page, au lieu d'attendre la
suite complète : en session 2, P6 a d'abord eu 16 échecs de `test_graphique`. Chaque échec trouvé par `rapide` évite une suite complète
rouge (28 min).

Ordres de grandeur de `rapide`, calculés depuis les temps mesurés :

| Fichier modifié | Fichiers Python relancés | Part de la suite Python | Mur estimé |
|---|---|---|---|
| `limites_asymptotes.py` | 25 | 37 % | ≈ 4,4 min |
| `exp_log_m.py` | 15 | 59 % | ≈ 7 min |
| `moteur/noyau.py` | 46 | 98 % | presque toute la suite |
| fichier commun (`commun/…`) | — | — | presque toute la suite de pages (le corpus réduit n'économise qu'environ 1 min sur `test_rendu`) |

**Risques** : `rapide` un peu plus long quand un moteur change. Il ne remplace jamais `complet`.

**Vérification** : `python3 tests/lancer.py liste` sur des modifications simulées ; `complet` inchangé (même commande).

### M7. Navigateur partagé entre les classes de tests de pages

Un seul Chrome par worker pour toute la session, au lieu d'un par classe.

**Gain** : au plus 16 démarrages × 2,2 s ≈ 35 s de somme → **moins de 20 s de mur**. **Rapport gain / risque faible : non recommandé
pour l'instant.**

**Risques** : un Chrome planté ferait échouer toutes les classes suivantes du worker. Il faut aussi vérifier que l'état propre à chaque
page est remis à zéro (aujourd'hui `Storage.clearDataForOrigin` à chaque ouverture).

### M8. Pyodide partagé entre les tests de pages

C'est le plus gros gisement des pages (environ 120 chargements de 6 à 9 s), mais **non recommandé tel quel**. Garder Pyodide demande de
garder la page, donc son état d'un test à l'autre :
- `localStorage` : filière, variante mémorisée ;
- DOM modifié par le test ;
- scripts injectés avant le chargement (`script_initial`) ;
- émulation tactile et agent utilisateur fixés à l'ouverture.

Plusieurs tests vérifient d'ailleurs le chargement lui-même (`test_t31_libelle_pendant_le_chargement_de_sympy`,
`test_t40_l_apercu_ne_attend_pas_sympy`, `test_pyodide_local`). Regrouper des vérifications sur une même page changerait ce que chaque
test vérifie (un état neuf).

Piste sans ce risque, à **mesurer d'abord** (une partie d'étude, sans commit de code) : où vont les 5 s entre le HTML et « Prêt. » ?
- compilation de `pyodide.asm.wasm` : le type `application/wasm` et le cache de code de Chrome sont-ils utilisés par le serveur de test ?
- décompression de la roue SymPy ;
- `import sympy`.

Un gain sur le chargement lui-même ne touche à aucun test.

### Mesures écartées

- **Plus de workers** (Python ou pages) : mesuré sans gain (§ 1.2 et § 1.3), avec plus de risques de délais dépassés.
- **Raccourcir l'oracle ou le corpus**, sauter les tests lents dans `complet` : interdit par la contrainte (affaiblissement).

## 4. Classement et découpage en parties (branche dédiée, un commit par partie)

Classement par rapport gain / risque :

| Rang | Mesure | Gain par partie de chantier | Risque |
|---|---|---|---|
| 1 | M1, contrôle allégé | ≈ 22–26 min | confiance dans le rapport (vérifiée par empreintes) |
| 2 | M2, clavier stable | ≈ 6 min en moyenne, et plus de relances au hasard | faible |
| 3 | M3, boucle quadratique | ≈ 1 min par suite Python | très faible |
| 4 | M4, cache de l'outil Limites | ≈ 1–1,5 min par suite Python | `mock` (cache explicite et test de garde) |
| 5 | M5, cache de `racines` | ≈ 1 min (2 min avec le regroupement) | faible ; regroupement à mesurer |
| 6 | M6, `rapide` et pages des moteurs | échecs trouvés plus tôt | nul pour `complet` |
| 7 | M8, étude du chargement de Pyodide | à mesurer | nul (étude) |
| 8 | M7, navigateur partagé | < 20 s | moyen : non recommandé |

**Découpage proposé** :

| Partie | Contenu | Vérification |
|---|---|---|
| P0 | `docs/chantiers/tests-rapides/suivi.md` ; deux lancements de référence sur le commit de départ (listes du § 3, hors git) ; option `--rapport` de `lancer.py` | le rapport du 2ᵉ lancement reproduit les listes du 1ᵉʳ |
| P1 | M2 : harnais du toucher (`navigateur.py`) | 20 sur 20 sous charge ; listes identiques |
| P2 | M1 : `lancer.py verifier`, et la procédure du chef d'orchestre (texte de `CLAUDE.md` à valider par vous, commit séparé si vous le souhaitez) | essais du § M1 (commit modifié, fichier non suivi) |
| P3 | M3 : `TestStructure` calculé une fois | listes et sous-tests identiques ; mur Python mesuré |
| P4 | M4 : `memo.py`, son test de garde (pas de `mock`) et son interrupteur `MEMO=0` | listes identiques ; comparaison avec `MEMO=0` |
| P5 | M5 : cache de `racines` | listes identiques ; racines identiques avec et sans cache |
| P6 | (facultative) regroupement `xdist_group` des fichiers à `racines`, gardé seulement si le mur baisse sur 2 lancements | mur mesuré ; listes identiques |
| P7 | M6 : `rapide` relance la page de l'outil dont un moteur change | `lancer.py liste` sur des cas simulés |

Chaque partie lance `complet` avant son commit (règle de `CLAUDE.md`). Elle compare `--collect-only -q` et les listes JUnit à la référence
de P0, et note dans `suivi.md` le mur de chaque suite.

**Bilan attendu** :
- suite Python : environ 718 s → 520 à 560 s ;
- suite de pages : inchangée en moyenne (944 s), mais sans échec au hasard ;
- par partie de chantier, contrôle compris : au moins 56 min plus environ 6 min d'échecs au hasard aujourd'hui, environ 25 à 28 min
  après (une suite complète, `verifier`, `rapide`), plus une suite complète par session.
