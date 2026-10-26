# Choix techniques

## Contraintes (rappel)

- Site **statique** sur GitHub Pages, **sans étape de build ni framework** : un push sur `main`
  est une mise en ligne.
- **Exactitude mathématique avant tout** ; **aucune régression** sur les outils en ligne.
- Public : élèves, souvent sur téléphone ; navigateurs de **moins de 4 ans environ**
  (ES2020, modules ES, `BigInt`, `IntersectionObserver` disponibles partout).
- Interface en français, notation suisse.

## Architecture cible

```
_config.yml              exclut docs/ et tests/ de la publication
index.html               accueil statique (fonctionne sans JS), vérifié contre le registre
commun/
  registre.json          outils × années × filières (source unique ; lue par les tests)
  style.css              variables partagées (identité de l'accueil) + composants + impression
  outil.js               monte une page outil à partir de sa config (module ES)
  moteur-python.js       client du worker : chargement, progression, délais, relance, erreurs
  worker-pyodide.js      worker (vrai fichier, plus de Blob) ; version de Pyodide définie ici seulement
  rendu.js               KaTeX + rendu générique des cartes et des blocs
  nombres.js             format suisse côté JS (graphique, simplexe)
moteur/
  noyau.py               interface publique du noyau (réexporte ensemble_def.py, noms sans « _ »)
  sortie.py              constructeurs du format de sortie commun (cartes, blocs)
  exercices.py           tirage avec graine à partir de gabarits validés
  manifeste.json         fichiers Python à charger dans Pyodide, par outil
<outil>/index.html       page outil réduite à sa config + son « Rappel de la méthode »
<outil>/*.py             moteurs actuels, à leur place (ensemble_def.py intact)
simplexe/
  index.html, simplexe.js (interface), lp.js (fonctions pures exactes, testables)
tests/
  python/                unittest — local en une commande + CI
  js/                    node --test — CI uniquement
  pages/                 tests de pages dans un navigateur sans interface — CI uniquement
.github/workflows/tests.yml
```

## Décisions validées

| # | Décision | Raison |
|---|---|---|
| D1 | **Garder Python/Pyodide** pour les moteurs d'analyse et la factorisation | ≈ 5 000 lignes éprouvées ; SymPy garantit l'exactitude. Une réécriture JS n'aurait pas de calcul formel de même qualité et ferait courir un gros risque de régression. |
| D2 | **Format de sortie commun** à tous les moteurs Python (voir plus bas) | Un seul code de rendu en JS ; ajouter un outil = un module Python + une config de page + une ligne du registre. |
| D3 | **Modules ES natifs**, pas de bundler | Fonctionne tel quel sur GitHub Pages. |
| D4 | **En-tête et pied de page écrits en HTML** dans chaque page, contrôlés par un test | Marchent sans JS, pas de clignotement ; la duplication (≈ 6 lignes) est vérifiée automatiquement. |
| D5 | **Accueil en HTML statique**, vérifié contre `commun/registre.json` | Doit fonctionner sans JavaScript (décision enseignant). Le registre est la source ; le test échoue si l'accueil diverge. |
| D6 | **Interface Python publique d'abord** (`moteur/noyau.py`), `ensemble_def.py` intact | Supprime les imports de noms privés sans toucher au noyau. Le découpage en modules viendra plus tard, si les tests tiennent. « Intact » = pas de restructuration ; les corrections de bugs y restent permises. |
| D7 | **Tests en CI (GitHub Actions)**, pas de build | Python 3.12 + SymPy 1.13.3 (= Pyodide 0.27.7). Python lançable en une commande locale ; Node seulement dans la CI. |
| D8 | **Exercices générés en Python avec une graine**, à partir de gabarits validés par l'enseignant ; niveaux conservés | Reproductibles, partageables (`?exo=`), testables : chaque exercice généré doit être résolu exactement. |
| D9 | **Identité visuelle de l'accueil** (serif, papier, bordeaux) étendue aux outils, variables CSS partagées, contraste WCAG AA | Une seule identité ; corrige le doré de l'accueil (3,7:1). |
| D10 | **Pyodide reste sur jsDelivr** ; pas de service worker pour l'instant | Décision enseignant ; coût de l'auto-hébergement chiffré plus bas. |
| D11 | **Simplexe reste en JS** (pas de Pyodide) | Instantané sur téléphone, déjà exact (BigInt). Priorité faible, traité en dernier. |
| D12 | `docs/` et `tests/` **exclus de la publication** (`_config.yml`) | Fait (`88b7b0f`). Attention : Jekyll ignore aussi les dossiers commençant par « _ » ; ne jamais nommer ainsi un dossier à publier. |
| D13 | **SymPy et mpmath précompilés, hébergés avec le site** (`moteur/roues/`) ; Pyodide, lui, reste sur jsDelivr (D10) | Mesuré le 26.10.2026 : `import sympy` compile ≈ 470 modules à chaque ouverture de page (≈ 5 s sur ordinateur, ≈ 20 s sur téléphone) parce que les roues officielles ne contiennent que du source. Avec le bytecode : < 1 s. Voir « Roues précompilées » plus bas. |

### Précautions pour `moteur/noyau.py` (D6, fait en T11, `0e019bf`)

- **Tout passe par le noyau** : un moteur n'importe jamais `ensemble_def` directement. Une fonction
  du noyau devenue utile ailleurs s'ajoute à la liste d'import de `noyau.py`, sous un nom public si
  elle est privée (comme `_sympy` → `charger_sympy`). `tests/python/test_noyau.py` le vérifie.
- **Réexporter, rien de plus** : aucune logique dans `noyau.py`. `SYMPY` est le même dict que `_SP`
  (pas une copie) : on le lit, on ne le réaffecte jamais.
- **Fichiers à plat dans Pyodide** : `ensemble_def.py` et `noyau.py` sont écrits côte à côte, sans
  dossier. `moteur/` n'est pas un paquet Python : pas de `from moteur.noyau import …`, qui
  casserait l'import dans le navigateur (le test d'import isolé du manifeste le détecte).
- **Déclaration par outil** : chaque outil qui utilise le noyau liste `moteur/noyau.py` dans
  `moteur/manifeste.json` et le charge dans sa page (`fetch` + `writeFile`) ; `test_manifeste.py`
  vérifie les deux. Vaut aussi pour les outils de la phase F.
- **Simulations de test** : simuler un nom là où il est utilisé. Simuler `noyau.charger_sympy`
  n'atteint ni `ensemble_def` ni les moteurs, qui ont déjà leur copie du nom.
- **Mise en ligne** : GitHub Pages garde le HTML en cache une dizaine de minutes. Après un push qui
  change les fichiers chargés par une page, un élève dont l'ancienne page est en cache peut voir
  une erreur d'import jusqu'au rechargement : éviter de pousser juste avant un cours ou un devoir,
  et essayer chaque page touchée dans un navigateur avant de pousser.

## Format de sortie commun (D2)

Chaque outil Python expose trois fonctions publiques (via un adaptateur, sans modifier
`ensemble_def.py`) :

```python
resoudre(entree: str) -> dict        # corrigé complet
apercu(entree: str) -> dict          # {"ok": True, "tex": ...} ou {"ok": False, "erreur": ...}
exercice(niveau: str, graine: int) -> dict   # {"ok": True, "entree": "...", "niveau": ..., "graine": ...}
```

Schéma de `resoudre` (T12, `moteur/sortie.py` : constructeurs et `valider()`, fait le 17.10.2026) :

```json
{
  "ok": true,
  "erreur": null,
  "enonce_tex": "f(x) = \\ln(x-1)",
  "entete": {"titre": "Fonction", "style": "normal", "blocs": ["…"]},
  "cartes": [
    {
      "titre": "Condition 1",
      "badge": "logarithme",
      "style": "normal",
      "blocs": [
        {"type": "texte", "html": "…", "style": "etape"},
        {"type": "formule", "tex": "…"},
        {"type": "tableau", "var": "x", "crit": ["…"], "rows": [{"label": "…", "cells": ["+", "0", "-"], "final": false}]},
        {"type": "liste", "items": ["…"], "style": "extrema"},
        {"type": "graphique", "xmin": 0, "xmax": 1, "ymin": 0, "ymax": 1, "segments": [], "extrema": [], "asymptotes": [], "recalculable": true},
        {"type": "resultat", "tex": "E_1 = \\left]1;+\\infty\\right["}
      ]
    }
  ],
  "besoin_sympy": false
}
```

- `ok: false` ⇒ `erreur` est un message en français destiné à l'élève, **jamais une trace Python** ;
  le détail technique va dans `detail` (console), à côté de `erreur`, sur une carte ou sur un bloc `texte`.
- Styles : carte `normal | etape | final | erreur` ; `texte` `etape | discret | indice` ; `liste` `extrema | bilan`.
- Un seul type `tableau` : le format déjà produit par les moteurs d'analyse (cases `+ - 0 | || x asym
  extremum \nearrow \searrow \rightarrow val:<tex>`, une ligne de `2·len(crit)+1` cases). L'Étude complète
  y ajoute `limites` (T06c).
- `resultat` est un bloc (et non un champ de carte) : l'ordre d'affichage est explicite.
- `entete` : carte toujours visible, hors compteur d'étapes (l'Ensemble de définition seulement ; les
  autres outils comptent leur carte « Fonction » comme première étape). Décidé en T16 : on ne change pas
  l'aspect, la différence reste.
- `titre_masque: true` (clé facultative de carte, T16) : la carte a un `titre` dans les données, mais la page
  ne l'affiche pas (cartes « Fonction » et carte finale de l'ED).
- Pas de `controle` dans `resoudre` : le contrôle numérique de l'ED est un appel séparé, `controle` (T16 :
  `{ok, accord, texte}`, la phrase est écrite en Python), lancé par la page après l'affichage ;
  `fenetre_json` (recalcul du graphique au zoom) reste aussi séparée.
- Les textes que les pages composaient en JS (nombre de conditions, phrases des extrema et des
  asymptotes, « Condition non résolue », valeurs ≈) sont écrits par les adaptateurs.
- Adaptateurs : un `resoudre_<outil>.py` par outil (`resoudre`, `resoudre_json`, `apercu_json`), à côté du
  moteur, qui ne change pas. Les pages continuent d'appeler les anciennes fonctions (`analyser_json`,
  `etudier_json`, `factoriser_json`) jusqu'à leur migration (T17 à T20), qui chargera `sortie.py` et
  `resoudre_<outil>.py` et mettra le manifeste à jour.

### Rendu commun et page générique (T16, `commun/rendu.js` et `commun/outil.js`)

`rendu.js` transforme une carte en HTML ; les règles y sont écrites une seule fois :

| Élément du format | Rendu |
|---|---|
| carte | `card` ; `+ cond` si elle a un badge ; `+ final` si style `final` ; style `erreur` : `card err` avec le seul message |
| titre | `<h3>titre<span class="badge">badge</span></h3>` (`titre_tex` en formule) ; sans badge, `<h3>` simple ; `titre_masque` : rien |
| `texte` | `etape` (défaut) → `.etape` ; `discret` → `.muted` ; `indice` → `.hint` |
| `formule` | carte à titre masqué → `.enonce` ; sinon `.c` |
| `resultat` / `erreur` | `.res` / `.res.err` (dans une carte `final` : `.err`) |
| `liste` | `<ul class="extrema|bilan">` |
| `tableau` | tableau de signes ; `limites` (Étude complète) : valeurs en ±∞ dans les cases du bord de la ligne de variation et de part et d'autre d'une colonne interdite |
| `graphique` | greffon (`ajouterGreffon`), voir « Graphique réutilisable » ci-dessous |

`outil.js` : `monterOutil({outil, titrePdf, exemples, exos, poids, prefixe?, sympyAvant?, delaiCalcul?, greffons?, apres?})` monte le
comportement commun (client Python, aperçu, clavier, exemples, calcul, cartes cachées puis révélées,
PDF, exercice) sur le **HTML statique** de la page, qui garde ses `id`. `apres({entree, appelPy,
derniereCarte, actuel})` est le crochet propre à l'outil (ED : badge du contrôle numérique). Le test
`test_source_unique.py` interdit les phrases de corrigé dans les pages migrées, `rendu.js` et `outil.js`.
Le manifeste a une clé `anciennes` : fonctions que seules des pages en cache appellent encore.
`delaiCalcul` (ms, 30 000 par défaut ; 45 000 pour l'Étude complète, comme avant) fixe le délai au-delà duquel le calcul est
abandonné et le moteur relancé. `greffons` : blocs à comportement, voir ci-dessous.

### Graphique réutilisable (T19, `commun/graphique.js`)

Livré comme module (et non comme code de page) pour les outils de la phase F (N01, N05, N11, N22, N25, N26).

- **`rendu.js`** : `ajouterGreffon({type, rendu, barre?, activer?})`. `rendu(bloc, carte)` donne le HTML du bloc ; `barre(bloc, carte)`
  place des boutons à droite du **titre de la carte** (le titre reste tiré des données : la barre de titre est un `.barre` avec
  le `<h3>`) ; `activer(carte, bloc, contexte)` est appelé une fois la carte construite. `rendreCarte(carte, contexte)` et
  `monterOutil` transmettent `contexte = { appelPy, entree }` (`entree` : la saisie dont la carte est le corrigé).
- **`graphique.js`** : `dessinerGraphique(canvas, g, extrema, asymptotes, vista, forcerClair)` (dessin, échelle égale en x et en y),
  `monterGraphique(éléments, {g, extrema, asymptotes, fenetre})` (interaction), `greffonGraphique` (bloc `graphique` de
  `moteur/sortie.py`). La page l'active par `monterOutil({greffons: [greffonGraphique]})` et ne contient plus aucun code de graphique.
- **Recalcul de la courbe** : si le bloc est `recalculable`, un zoom ou un déplacement appelle
  `appelPy("fenetre", JSON {f: saisie, xmin, xmax, n})` → `{ok, segments}` (`resoudre_ec.fenetre_json`). Si le calcul échoue (`ok:false`
  ou erreur), la courbe reste celle de la dernière fenêtre réussie et un message discret l'indique (EC-04).
- **Redessin** : le canvas se redessine seul quand sa taille change (`ResizeObserver` et `resize` : une carte cachée a une largeur nulle)
  et autour de l'impression (`beforeprint` : couleurs du thème clair, `afterprint` : thème de l'écran), donc aussi avec Ctrl+P. Les écouteurs
  de la fenêtre disparaissent quand le canvas quitte la page.
- **Gestes** : souris et stylet, molette zoome autour du pointeur, glisser déplace. Écran tactile : `touch-action: pan-x pan-y` (un doigt =
  la page défile, la courbe ne bouge pas) et écouteurs `touchstart`/`touchmove` non passifs qui font `preventDefault()` dès que deux doigts
  touchent le canvas (un pointer event ne peut pas annuler un geste déjà pris en charge par le navigateur). Le geste à deux doigts est
  calculé **depuis l'état au début du geste** (fenêtre affichée, écart et milieu des doigts) : le point de la courbe sous le milieu des doigts y
  reste, quel que soit le nombre de `pointermove` livrés (Chrome en fusionne ; l'ancien calcul, qui divisait par l'échelle courante, laissait glisser
  le point). Limite connue : si le défilement à un doigt est déjà lancé quand le deuxième doigt arrive, il continue ; il faut lever les doigts.
- **Nombres** : tout nombre écrit sur le graphique passe par `etiquette()` (au plus deux décimales, virgule) ; T23 la remplacera par `commun/nombres.js`.
- **Limite actuelle** : un seul graphique par page (les `id` `graphique`, `zoomPlus`, `zoomMoins`, `zoomReset`, `msgFenetre` sont fixes, les tests
  les utilisent) ; le module n'interroge aucun `id` global. Un préfixe d'`id` sera ajouté au premier outil qui en a besoin.
- **Crochets de test** : `window.__echecFenetre` (`"refus"` : le moteur répond `ok:false` ; `"exception"` : erreur), `window.__delaiCalcul` (ms).

### Preuve que le graphique ne change pas (banc `tests/pages/graphique.py`)

- **Trace des appels canvas** : chaque appel du contexte 2D avec ses arguments arrondis à 1e-4. Le dessin n'utilise pas `measureText` : la trace
  ne dépend d'aucune police, ses empreintes sont versionnées (`tests/pages/references/graphique-traces.json`) et rejouées en CI
  (3 fonctions × 2 vues × 8 états, ≈ 2,3 min). Matrice complète, en local : 6 fonctions × 4 vues (clair, sombre, 360 px, dpr 2) × 8 états
  (tracé initial, +, −, réinitialiser, molette, glisser, pincer, impression) ≈ 8 min. Molette, glisser et pincer passent par de vrais
  événements DevTools (un événement synthétique ferait échouer `setPointerCapture`).
- **Pixels du canvas** et **captures de page** (`tests/pages/captures.py`) : comparés sur la même machine, jamais versionnés.
- **Bruit mesuré** (18.10.2026, même code rechargé) : 0 trace et 0 pixel d'écart sur 10 × 48 scénarios ; 0 pixel sur 10 × 10 captures de
  `etude-complete`, d'où un plancher de 20 px pour cette page (`BRUIT_PAGE`), 400 px pour les autres.
- **Un changement voulu** se prouve par ce qui change : EC-06 ne change que des `fillText` fractionnaires (`.` → `,`) ; EC-05 ne change que les
  scénarios `pincer`.
- **Serveur de test** : un fil par requête et une file de 128 connexions (la file de 5 par défaut réinitialise des connexions quand le
  serveur n'accepte plus un instant : `Failed to fetch` au chargement des fichiers Python). À l'expiration de « Prêt. », `attendre_pret`
  donne le texte de `#etat` et la console.

- Fichiers à plat dans Pyodide comme `noyau.py` (`test_resoudre_import.py`) ; la fonction `exercice(niveau, graine)`
  est l'objet de T13.

## Options écartées

| Option | Pourquoi |
|---|---|
| Réécrire les moteurs en JS | Pas de calcul formel équivalent à SymPy ; risque de régression majeur. |
| Serveur de calcul | Contraire à la contrainte « statique ». |
| Corrigés précalculés uniquement | Supprime la saisie libre d'un exercice. |
| Une seule page pour tous les outils | Change les URL partagées ; charge tout d'un coup. |
| En-tête chargé par `fetch` ou iframe | Clignotement, ne marche pas sans JS. |
| Accueil généré en JS depuis le registre | L'accueil doit fonctionner sans JS (D5). |
| Découper `ensemble_def.py` maintenant | Repoussé (D6) : d'abord les tests. |
| MathJax | KaTeX est plus léger et plus rapide, déjà en place. |
| Git LFS pour auto-héberger Pyodide | GitHub Pages ne sert pas les fichiers LFS. |

## Coût d'un Pyodide auto-hébergé (pour décision ultérieure)

Mesuré le 13.10.2026 sur la version utilisée (0.27.7), en ne gardant que le nécessaire :

| Fichier | Taille dans le dépôt | Transfert gzip (GitHub Pages) |
|---|---|---|
| pyodide.asm.wasm | 10,1 Mo | 3,1 Mo |
| python_stdlib.zip | 2,4 Mo | 2,3 Mo |
| sympy-1.13.3 (wheel) | 4,1 Mo | 4,0 Mo |
| pyodide.asm.js | 1,3 Mo | 0,24 Mo |
| mpmath-1.3.0 (wheel) | 0,4 Mo | 0,4 Mo |
| pyodide-lock.json, pyodide.js | 0,13 Mo | 0,03 Mo |
| **Total** | **≈ 18,4 Mo** | **≈ 10,1 Mo** (≈ 10,0 Mo en brotli chez jsDelivr) |

- **Poids** : + 18 Mo par version, **définitivement** dans l'historique git (chaque mise à jour
  en ajoute autant). Après 5 versions ≈ 90 Mo : sous les limites de GitHub (dépôt et site
  < 1 Go recommandés, fichier < 100 Mo), mais un clone plus lent. KaTeX (+ ≈ 1 Mo avec ses
  polices) peut suivre la même voie.
- **Mises à jour** : manuelles — télécharger les fichiers de la nouvelle version, remplacer le
  dossier, changer la constante de version dans `commun/worker-pyodide.js`, relancer les tests
  avec les **nouvelles** versions de Python et SymPy (elles changent avec Pyodide). Estimation :
  1 à 2 h par mise à jour. Avec jsDelivr, la mise à jour coûte la même chose côté tests ; seul
  le téléchargement des fichiers disparaît.
- **Bénéfices** : plus de dépendance au CDN (filtrage possible à l'école), même origine que le site.
- **Transfert pour l'élève** : identique (≈ 10 Mo à la première visite).
- **À noter** : la numérotation de Pyodide a changé (versions `314.0.x` sur npm, qui suivent
  Python 3.14). Une montée de version sera un vrai chantier, à faire avec la suite de tests.

## Roues précompilées de SymPy et mpmath (D13, T32)

**Pourquoi.** Plainte de l'enseignant (26.10.2026) : le chargement du moteur est « extrêmement lent » sur téléphone. Décomposition mesurée
(Mac, Pyodide servi en local donc CPU seulement, charge machine élevée donc chiffres à ± 30 %) :

| Étape (Étude complète) | Avant | Après |
|---|---|---|
| Pyodide (wasm, bibliothèque standard) | 5-9 s | inchangé |
| Import du module de l'outil | 0,4-1,2 s | inchangé |
| Téléchargement et dézippage de SymPy | 1,1-2,1 s | 0,8 s |
| **`import sympy`** | **5-8 s** (24 s avec un processeur 4 fois plus lent) | **0,8-1,3 s** |
| **Jusqu'à « Prêt. »** (médiane de 3 ouvertures) | **≈ 11-13 s** | **≈ 5,5 s** |

La cause est la compilation : les roues officielles (et la bibliothèque standard de Pyodide) ne contiennent que du source `.py`, Python compile
donc chaque module importé à chaque ouverture de page (le cache `__pycache__` vit en mémoire et disparaît avec l'onglet). Sur CPython 3.12 natif,
`import sympy` prend 3,0 s sans cache et 0,7 s avec : les trois quarts du temps sont de la compilation.

**Ce qui est fait.** `moteur/construire_roues.py` réécrit les roues officielles de Pyodide (SHA-256 vérifié contre `pyodide-lock.json`) en
remplaçant par leur `.pyc` les modules que `import sympy` charge (420 modules ; les 427 autres restent en source) et tous ceux de mpmath.
Les roues sont dans `moteur/roues/` (nom = version + 8 premiers caractères du SHA-256 : un nom ne désigne jamais deux contenus), le manifeste
les annonce (clé `roues`, avec le numéro magique du bytecode). Le worker les télécharge **dès le début, pendant le chargement de Pyodide**
(avant, SymPy ne commençait à se télécharger qu'une fois Python prêt), les décompresse dans `site-packages` et importe.

**Sécurités.** (1) Si le numéro magique du bytecode de Pyodide n'est pas celui du manifeste (Pyodide passé à une autre version de Python), ou si
une roue manque ou ne se télécharge pas, le worker charge SymPy depuis le CDN comme avant : plus lent, jamais cassé (deux tests de page). (2) Retirer
la clé `roues` du manifeste suffit à revenir au comportement d'avant. (3) `tests/python/test_roues.py` vérifie, module par module, que chaque
`.pyc` est exactement le bytecode du source du SymPy installé (une roue périmée fait échouer la suite), le numéro magique, l'absence de source en double
et qu'un Python 3.12 importe SymPy depuis la roue seule.

**Coût.** + 7,3 Mo dans le dépôt par reconstruction (6,6 Mo SymPy + 0,7 Mo mpmath ; 2,7 Mo de plus à télécharger que les roues officielles,
puisque le bytecode se compresse moins bien que le source) ; la reconstruction n'a lieu que si SymPy, mpmath ou la version de Python de Pyodide
changent (≈ 10 minutes avec la commande de `construire_roues.py`, puis `tests/python` et `tests/pages`). GitHub Pages sert ces fichiers avec un cache de
10 minutes et une revalidation : un élève qui revient le jour même ne les retélécharge pas.

**Pas fait (à décider selon les mesures sur téléphone, T31) :** préchargement de Pyodide dès l'accueil ; précompilation de nos propres modules
Python (≈ 0,3 s sur ordinateur, ≈ 1,5 s sur téléphone) ; service worker (hors ligne et rechargement instantané, écarté par D10) ; instantané mémoire de
Pyodide (trop gros). Ce qui reste incompressible : le démarrage de Pyodide lui-même (≈ 5 s sur ordinateur).
