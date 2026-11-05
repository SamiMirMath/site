# Chantier « Tests rapides » — suivi

## Résumé de session

Session du 04 au 05.11.2026, sans vous. **Rien n'a été poussé de toute la session** (`origin/main` est resté à ca6c243).
Pas d'exemple cible à rendre : P0 à P7 ne changent aucun texte affiché (aucun instantané modifié) ; le rendu de l'étape B est
dans `docs/chantiers/correctif-explog-delta.md`.

**a. Étape A — méthode de chantier (commit 351fb77 sur `main`).** Un seul fichier trouvé, `~/Downloads/methode-chantiers.md`
(4 nov., 6 258 octets), versé dans `docs/methode-chantiers.md`. Ligne ajoutée à la section « Suivi » de `CLAUDE.md` :
« - Méthode de travail par chantier : docs/methode-chantiers.md. ». Suite verte avant le commit. **Le push de `main` a été refusé
par le système de permissions de Claude Code** (`git push origin main`), sans nouvel essai.

**b. Étape B — correctif Exp-log (123ba43, branche `correctif-explog-delta`).**
- Cause : en méthode « Logarithmes », le second membre est l'exposant tel qu'il est écrit (`2^(-6)` → arbre `Neg(6)`, non reconnu
  comme nombre) ; il partait dans la branche « coefficients logarithmiques », qui ne calcule rien : « x² − 5x − (−6) = 0 »,
  « 4·1·(−−6) », S = {x₁ ; x₂}. Même défaut avec `1/64` (Δ jamais calculé), au 1ᵉʳ degré (S = {5 − 6}) et quand a < 0 (« + (−4)· »).
- Correction (`exp_log.py` seul) : un second membre rationnel est calculé, puis résolu comme en méthode « même base » ; une constante
  égale à a^k s'écrit log(1/64) = log(2⁻⁶) = −6·log(2) (exactitude décidée par facteurs premiers) ; sinon Δ s'écrit avec les
  logarithmes, sans double signe, et un Δ rationnel est calculé.
- Entrées ajoutées : 42 (`BATTERIE_DELTA`, `tests/python/cas_el.py`) ; nouveau `tests/python/test_explog_delta.py` (15 tests).
- Écart : log₂(1/64) = −6 n'est pas écrit, car EL-20 interdit log_a(a^k) = k en méthode « Logarithmes » ; l'outil passe par
  log(2⁻⁶) = −6·log(2).
- **Fusionné dans `main` en local (7268412)**, parce que les deux suites étaient vertes (contrôle du chef d'orchestre sur 123ba43 :
  Python 1311 + 1 xfail, pages 122, code 0) et que les instantanés modifiés ne concernent que l'outil Exp-log : 3 modifiés et 42 ajoutés
  par fichier non M, 42 ajoutés par fichier M, aucun retiré. **Non poussé** (permission refusée).
- **8 questions** à trancher : `docs/chantiers/correctif-explog-delta.md`, « Questions pour l'enseignant » (dont : Δ ou factorisation
  pour `2^(x^2-5x)=2^(-6)` ; doubles signes `log(--100)` de la carte « Contrôle » 3C, autre défaut, ticket à ouvrir).

**c. Parties P0 à P7 (branche `tests-rapides`).** Aucun échec de partie.

| Partie | Commit | Contenu | État | Contrôle du chef d'orchestre |
|---|---|---|---|---|
| P0 | 1feb6cf | Référence (deux lancements), `complet --rapport`, `comparer_listes.py` | faite | suite complète relancée : code 0, identique nom par nom |
| P1 | a8d6ab6 | Harnais du toucher (test du clavier 40/40) | faite | suite complète relancée : code 0, identique nom par nom |
| P2 | 55daa1f, 1f34e3c | `lancer.py verifier` ; méthode : contrôle allégé | faite | `verifier` ACCEPTÉ ×2 ; son essai « test disparu » REFUSÉ, comme attendu |
| P3 | f140f1c | `TestStructure` calculé une fois par classe (fichier 121 s → 44 s) | faite | `verifier` ACCEPTÉ ; tests du commit verts ; diff relu |
| P4 | 7186b6d | Cache de l'outil Limites (`memo.py`), garde, `MEMO=0` ; 6 tests ajoutés | faite | `verifier` ACCEPTÉ ×2 (avec et sans `MEMO=0`) ; tests du commit verts dans les deux cas |
| P5 | 46fd547 | Cache de l'oracle `racines` (`memo_racines.py`) ; 563 clés identiques avec et sans cache ; 11 tests ajoutés | faite | `verifier` ACCEPTÉ ; tests du commit verts (avec `MEMO=0` : limite de 5 min dépassée, voir d) |
| P6 | d116aa1 | `rapide` relance les pages des outils dont un moteur change (manifeste), filière M | faite | `verifier` ACCEPTÉ ; diff relu, `complet` intact |
| P7 | 8d08a67 | Étude du chargement de Pyodide (`etude-pyodide.md`, aucun code) | faite | `git diff --stat` : 3 fichiers de docs ; `verifier` ACCEPTÉ |

`rapide` (code 0) a aussi été lancé après chaque partie de P2 à P7. Détail : `journal.md`, « Contrôles du chef d'orchestre ».

**d. Échecs rencontrés** (aucun n'est un échec de partie).
- Test instable du clavier : un échec au 2ᵉ lancement de référence de P0 (avant P1), vert relancé seul (une fois aussi pendant
  l'étape B). Aucun échec ensuite, de P1 à la fin, dans aucune suite.
- P5 : le contrôle du chef d'orchestre avec `MEMO=0` sur les 10 fichiers du commit a dépassé la limite de 5 minutes. Ce n'est pas
  un échec de test ; la suite complète `MEMO=0` de fin de session le couvre (verte).

**e. Questions pour vous** (texte complet : `journal.md`, « Questions détaillées » ; en attendant, l'option qui affiche le moins).
1. P2 : confirmer la liste permise de `verifier` (`suivi.md` et `journal.md` du chantier ; `CLAUDE.md` hors du commit).
2. P2, P6 : après le commit, `rapide` ne relance que les tests de fumée (arbre propre). Ajouter `rapide --depuis HEAD~1`, plus utile
   depuis P6 ? Non fait.
3. P4 : `test_doctrine_bh.py` (sans mock, passe par `memo`) importe `TestStyle` d'un fichier à mock. Lecture retenue : T4 porte sur le
   texte du fichier. À confirmer.
4. P4 : le cache de l'outil Limites ne fait gagner que 12 à 20 s (les gros appelants ont des mock). Le garder ?
5. P5 : cache de `racines` dans un module à part (`memo_racines.py`), avec une garde qui admet `setattr(TestX, "test_…", …)`. À confirmer.
6. P6 : confirmer la filière M ajoutée avec la page des exponentielles, et « toutes les pages » quand on ne sait pas borner. Faut-il
   un test de `lancer.py` (`test_lancer.py`) dans un chantier suivant ?
7. P7 (`etude-pyodide.md` §5) : faire l'onglet de réserve (≈ 35 s) ? Le cache de Chrome d'une classe à la suivante (≈ 45 à 60 s), ou
   rouvrir T8 ? Confirmer l'abandon de M8 (Pyodide partagé). Hors chantier : la pause de 0,7 s avant SymPy et `invalidate_caches`
   (0,3 s), qui coûtent aussi à l'élève.

**f. Murs avant / après.**

| | Avant (P0 : deux lancements + contrôle) | Après (fin de session, 8d08a67) | Après, `MEMO=0` |
|---|---|---|---|
| Python | 737 / 755 / 737 s | **556 s** | 660 s |
| Pages | 967 / 938 / 950 s | **966 s** | 973 s |

Bilan attendu (`decisions.md` §3) : Python d'environ 718 s → 520 à 560 s. **Atteint, dans le haut de la fourchette** : 556 s en fin
de session, mais 570 à 588 s pour les suites de P5 à P7 (bruit d'environ ± 40 s). Le gain vient surtout de P3 et de P5 ; le cache de
P4 pèse 12 à 20 s. Pages : aucun échec au hasard depuis P1 (attendu) ; leur mur ne change pas (aucune partie ne le visait, P7 l'a
étudié). Par partie, le contrôle allégé ne demande plus qu'une suite complète (environ 25 à 27 min) au lieu de deux.

**g. Fin de session** (suites relancées par le chef d'orchestre sur 8d08a67). Suite normale et suite `MEMO=0` vertes (code 0) :
Python 1328 passés + 1 xfail, 103 161 sous-tests ; pages 122 passés, 2 554 sous-tests. Les deux sont identiques entre elles, nom par
nom (issues et sous-tests). Seuls écarts avec la référence P0 : les 17 tests ajoutés (6 de P4, 11 de P5, listés dans `journal.md`,
« P4 » et « P5 ») ; aucun test de la référence ne manque. `verifier` : ACCEPTÉ sur les deux rapports.

**h. À reporter dans `CLAUDE.md`** : section « À reporter par l'enseignant dans CLAUDE.md » plus bas (`--rapport`, `verifier`,
`MEMO=0` pour les deux caches, `rapide` et pages des moteurs, mesures de temps du 05.11.2026).

**i. Commandes pour vous** (une à la fois) :

```
git push origin main
git push -u origin tests-rapides
```

Plus tard, après relecture, la fusion :

```
git checkout main
git merge --no-ff --no-edit tests-rapides
git push
```

Et la branche déjà fusionnée dans `main` :

```
git branch -d correctif-explog-delta
```

## Cadre

Branche `tests-rapides`, créée depuis `main` à jour (7268412). Rien n'est poussé ni fusionné.
Ordre de priorité : `CLAUDE.md` > [`decisions.md`](decisions.md) (validé le 04.11.2026) > [`audit.md`](audit.md). Méthode : `docs/methode-chantiers.md`.
Un commit « Tests rapides P{N} : … » par partie, suite complète verte avant chaque commit. Tout le détail (plans, tableaux, temps,
rapports) : [`journal.md`](journal.md).

## État des parties

| Partie | Contenu | État |
|---|---|---|
| P0 | `suivi.md`, `journal.md`, deux lancements de référence, `lancer.py complet --rapport` | **faite** (commit « Tests rapides P0 : … ») |
| P1 | T2 : harnais du toucher (test du clavier) | **faite** (commit « Tests rapides P1 : … ») : test du clavier 20/20 seul et 20/20 sous charge ; listes identiques |
| P2 | T1 : `lancer.py verifier`, texte proposé pour `CLAUDE.md`, méthode (commit séparé) | **faite** (commit « Tests rapides P2 : lancer.py verifier … », `verifier` ACCEPTÉ ; méthode : commit séparé « Tests rapides P2 (méthode) : … ») : commit modifié refusé, fichier non suivi signalé et refusé, test disparu refusé ; listes identiques |
| P3 | T3 : `TestStructure` (calcul une fois par classe) | **faite** (commit « Tests rapides P3 : … ») : copie profonde par test ; fichier seul 121 s → 44 s ; mur Python 670 s ; listes et sous-tests identiques |
| P4 | T4 : `memo.py`, test de garde, `MEMO=0` | **faite** (commit « Tests rapides P4 : … ») : 9 fichiers sans mock passent par `memo` ; 6 tests ajoutés (`test_memo.py`, `test_memo_garde.py`) ; listes identiques avec et sans `MEMO=0` (seuls écarts à la référence : les 6 ajoutés) ; Python 660 s (cache) / 672 s (`MEMO=0`) |
| P5 | T5 : cache de `racines` | **faite** (commit « Tests rapides P5 : … ») : `memo_racines.py` ; 9 appels de 4 fichiers passent par le cache ; `racines` inchangée (empreinte gardée) ; avec et sans cache : 563 clés, 695 racines, 0 écart ; 11 tests ajoutés ; listes identiques (seuls écarts : les ajouts de P4 et P5) ; Python 570 s (P4 : 660 s) |
| P6 | T7 : `rapide` et pages des moteurs | **faite** (commit « Tests rapides P6 : … ») : un `.py` modifié d'un dossier d'outil ou de `moteur/` relance les pages (corpus réduit) des outils qui le chargent d'après `moteur/manifeste.json`, « tous » si on ne sait pas borner ; filière M avec la page des exponentielles ; `complet` inchangé (commandes identiques octet pour octet) ; suite complète code 0, listes identiques à P5 nom par nom (seuls écarts à la référence : les 17 de P4 et P5) ; Python 588 s, pages 974 s |
| P7 | T9 : étude du chargement de Pyodide (rapport seul) | **faite** (commit « Tests rapides P7 : … ») : rapport [`etude-pyodide.md`](etude-pyodide.md), aucun code modifié ; 122 chargements par suite, 6,9 s à chaud, 18,2 s pour la 1ʳᵉ page de chaque Chrome ; environ 47 % du temps des tests de pages. **Recommandation** : ne pas partager Pyodide entre les tests ; si l'on veut gagner, onglet de réserve puis cache de Chrome gardé d'une classe à la suivante (environ 1,5 min sur la suite de pages) |

## Référence (P0)

- Listes du 1ᵉʳ lancement (commit 7268412, code inchangé) : [`reference/`](reference/) — `collecte-{python,pages}.txt`,
  `resultats-{python,pages}.txt` (identifiant, issue, nombre de sous-tests).
- Python : **1312 collectés, 1311 passés, 1 xfail** (`test_P10_pente_au_point_exclu`), 0 sauté, **103 033 sous-tests**.
- Pages : **122 collectés, 122 passés**, 0 xfail, 0 sauté, **2 554 sous-tests**.
- **Sous-tests stables** : identiques test par test entre les deux lancements (Python et pages), sauf le test instable connu du
  clavier, qui a échoué au 2ᵉ lancement (2 → 0 sous-tests) et passe relancé seul (2 sous-tests). Les seuls tirages au hasard des pages
  (`Math.random`, `commun/outil.js:343` et `:363`, « exercice au hasard ») sont dans des tests sans `subTest` : ils ne changent pas les
  nombres. Aucun fichier `reference/soustests-variables.txt` n'est donc nécessaire.
- Comparer un lancement à la référence (code 0 si identique nom par nom) :
  `python3 tests/lancer.py complet --rapport <dossier hors du dépôt>` puis
  `python3 tests/comparer_listes.py docs/chantiers/tests-rapides/reference <dossier>`.
- Murs : Python 737 s puis 755 s ; pages 967 s puis 938 s (détail : `journal.md`, « P0 »).

## Injectivité de la clé (P5, décision T5)

Clé de `memo_racines.racines(s)` = (contexte de l'oracle, instantané de `s`). L'instantané est un tuple immuable qui commence par le
**type exact** de chaque objet et contient **tous** ses champs (nœuds d'`exp_log` d'une liste fermée, sans sous-classe ni `__dict__` ;
`Saisie` entière ; `Fraction` par numérateur et dénominateur ; `str` ; `None` ; `tuple`) ; tout autre type (flottant, entier, booléen,
SymPy…) n'a pas de clé et l'oracle est appelé directement. Le contexte contient les fonctions `racines`, `ecart`, `evaluer`, l'objet `MP`
avec sa précision et son arrondi, et les classes que lit `evaluer`. Deux clés égales désignent donc des arguments indiscernables, le même
code et le même contexte ; `racines` (un seul paramètre, sans défaut) étant déterministe, le résultat est le même. Démonstration
détaillée et pièges écartés (1 == 1.0 == True, assomptions SymPy, arbre modifié après l'appel) : `journal.md`, « P5 », « Clé ».

## À relire par l'enseignant

- P0 : aucun instantané modifié. Outil de test modifié : `tests/lancer.py` (option `complet --rapport` ; sans l'option, mêmes
  commandes et même code de retour) ; nouveaux : `tests/rapport_pytest.py` (extension pytest passive, chargée seulement avec
  `--rapport`) et `tests/comparer_listes.py`.
- P1 : aucun instantané ni aucun test modifié. Harnais modifié : `tests/pages/navigateur.py` (`toucher` : attente d'immobilité avant le
  centrage, recentrage borné à 3 essais, erreur « la touche n'est pas sous le doigt » si `elementFromPoint` n'est pas l'élément visé).
  Coût : `test_clavier.py` 218 s → 241 s ; mur des pages 994 s (P0 : 938 à 967 s). Détail : `journal.md`, « P1 ».
- P2 : aucun instantané ni aucun test modifié. Outil de test modifié : `tests/lancer.py` (commande `verifier` ; `rapport.json` note
  `CORPUS`, `OUTILS`, `MEMO`) ; nouveau : `tests/verifier.py`. Les règles exactes de (a), (b), (c) et la liste permise sont dans
  `journal.md`, « P2 ». Méthode (`docs/methode-chantiers.md`, « Organisation de nuit ») : commit séparé, à relire.
- P3 : aucun instantané ni aucun moteur modifié. Test modifié : `tests/python/test_redaction_bh_3m.py`, classe `TestStructure`
  (`toutes()` : calcul commun gardé par classe, copie profonde par test ; corps des tests inchangés). Détail : `journal.md`, « P3 ».

- P4 : aucun instantané ni aucun moteur modifié. Nouveaux : `tests/python/memo.py`, `tests/python/test_memo.py`,
  `tests/python/test_memo_garde.py`. Tests modifiés (seulement `la.etudier(…)` → `memo.etudier_la(…)`, et l'import) : `test_corpus_limites_3m`,
  `test_doctrine_bh`, `test_instantanes`, `test_limites_deux_cotes`, `test_racines_reelles`, `test_rappel_methode`, `test_redaction_bh_3m`,
  `test_resoudre_la`, `test_tableau_limites`. Détail : `journal.md`, « P4 ».

- P5 : aucun instantané ni aucun moteur modifié ; `racines`, `ecart`, `evaluer` inchangées. Nouveaux : `tests/python/memo_racines.py`,
  `tests/python/test_memo_racines.py`, `tests/python/test_memo_racines_garde.py`. Tests modifiés (seulement `racines(s)` →
  `memo_racines.racines(s)` et les imports) : `test_exp_log_m`, `test_exp_log_m_t36`, `test_exercices_el_m`, `test_explog_3c`.
  Détail : `journal.md`, « P5 ».

- P6 : aucun instantané, aucun test ni aucun moteur modifié. Outil de test modifié : `tests/lancer.py` (chemin de `rapide` / `liste`
  seulement : `outils_des_moteurs`, `corpus_des_pages`, `outils_de_pages`). Simulations avant / après et preuve de `complet` inchangé :
  `journal.md`, « P6 ».

- P7 : aucun instantané, aucun test, aucun code modifié. Nouveau : [`etude-pyodide.md`](etude-pyodide.md) (mesures, options classées,
  recommandation, décisions). Mesures et scripts : `journal.md`, « P7 ».

## À reporter par l'enseignant dans CLAUDE.md

Texte proposé (décision T10 : Claude Code ne modifie pas `CLAUDE.md`), pour la section « Commandes de test », à la place de la ligne
« Mesures du 29.10.2026 … » :

```
- `rapide` (à la place de la ligne actuelle) : les tests Python des fichiers modifiés (`git diff HEAD` + fichiers non suivis, dépendances
  d'import comprises) plus les tests de fumée (manifeste, accueil, source unique) ; les tests de pages à corpus réduit si une page, un
  fichier commun ou un test de page est touché, et aussi pour chaque outil dont un moteur Python chargé par la page change (d'après
  `moteur/manifeste.json` : un module partagé relance tous les outils qui le chargent ; toutes les pages si on ne sait pas borner, ou
  si un module du corpus des pages, `cas.py`, `cas_el.py`, `moteurs.py`, change). La page des exponentielles vient avec sa filière M.
  `liste` affiche ce que `rapide` lancerait, sans rien lancer. Pour travailler : ne remplace pas la suite complète avant un commit.
- `complet --rapport <dossier>` : comme `complet` (mêmes commandes, même code de retour), et écrit en plus dans <dossier> (hors du
  dépôt, par exemple le scratchpad) les JUnit, les listes de tests (collectés, issues, sous-tests) et rapport.json (commit de départ,
  empreintes des fichiers modifiés ou non suivis au début et à la fin, codes, durées, CORPUS/OUTILS/MEMO). C'est la forme à utiliser
  pour la suite complète d'avant commit dans un chantier.
- `verifier <dossier> [--reference <dossier>]` : après le commit, contrôle sans rien relancer que le rapport porte exactement sur ce
  commit (empreintes), qu'aucun autre fichier n'était modifié ou non suivi pendant le lancement (hors suivi.md / journal.md de chantier
  et CLAUDE.md), que les codes valent 0 et qu'aucun test n'a disparu, n'est sauté en plus, ne se dégrade ni ne perd de sous-tests par
  rapport à la référence (par défaut docs/chantiers/tests-rapides/reference). Verdict final ACCEPTÉ (code 0) ou REFUSÉ (1, ou 2 si un
  fichier manque). `python3 tests/comparer_listes.py <référence> <dossier>` compare deux dossiers nom par nom.
- `MEMO=0` (variable d'environnement) : coupe les caches de test `tests/python/memo.py` (sorties de l'outil Limites) et
  `tests/python/memo_racines.py` (oracle `racines` des exponentielles et logarithmes), gardés par processus, copie profonde à chaque
  appel : chaque appel devient un appel direct du moteur ou de l'oracle. Ces caches ne servent qu'aux fichiers sans aucun mock
  (`test_memo_garde.py`, `test_memo_racines_garde.py` le vérifient). Une fois par session de chantier, lancer aussi `MEMO=0 python3 tests/lancer.py complet --rapport
  <dossier>` : les listes doivent être les mêmes qu'avec le cache.
- Mesures du 05.11.2026 sur le Mac de l'enseignant (2 cœurs physiques ; 1329 tests Python et 103 161 sous-tests, 122 tests de pages et
  2 554 sous-tests) : suite Python 556 à 588 s (660 s avec `MEMO=0`) ; suite de pages 966 à 999 s ; `complet` environ 25 à 27 min
  (avant le chantier tests-rapides, le 04.11.2026 : Python 737 à 755 s, pages 938 à 967 s).
```

Procédure allégée du chef d'orchestre (décision T1 ; écrite aussi dans `docs/methode-chantiers.md`, « Organisation de nuit ») :
1. le sous-agent lance `python3 tests/lancer.py complet --rapport <dossier>` avant son commit et donne `<dossier>` dans son rapport ;
2. le chef d'orchestre : `git log --oneline -3`, puis `python3 tests/lancer.py verifier <dossier>` (`VERDICT : ACCEPTÉ` exigé), puis
   `python3 tests/lancer.py rapide` (sur l'arbre propre d'après le commit : tests de fumée seulement) ; une ligne dans `journal.md`, « Contrôles du chef d'orchestre » ;
3. un test disparu fait refuser `verifier` ; seul un renommage justifié dans `suivi.md` (ancien nom → nouveau nom, raison) est accepté,
   et les parties suivantes se comparent alors au dossier de cette partie (`--reference`) ;
4. une seule suite complète relancée par le chef d'orchestre, en fin de session (et une avec `MEMO=0`, decisions §3).

## Reprise après compactage

Chantier terminé : P0 à P7 (P2 en deux commits) commitées sur `tests-rapides`, fin de session faite (suites normale et `MEMO=0`
vertes, identiques), résumé en tête de ce fichier (commit « Tests rapides : résumé de session »). **Rien n'est poussé** : `main` a 3
commits locaux (351fb77, 123ba43, 7268412), push refusé par les permissions ; `tests-rapides` n'est ni poussée ni fusionnée.
Reste à l'enseignant : relire le résumé (questions e, section « À reporter … dans CLAUDE.md »), lancer les commandes de i, trancher
les 8 questions de `docs/chantiers/correctif-explog-delta.md`. Contrôle d'un commit : `python3 tests/lancer.py verifier <dossier de
complet --rapport>`. Pour reprendre : lire ce fichier, `decisions.md`, puis `git log --oneline main..HEAD` ; le détail est dans
`journal.md`.
