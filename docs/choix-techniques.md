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

Schéma de `resoudre` :

```json
{
  "ok": true,
  "erreur": null,
  "enonce_tex": "f(x) = \\ln(x-1)",
  "cartes": [
    {
      "titre": "Condition 1",
      "badge": "logarithme",
      "blocs": [
        {"type": "texte", "html": "…"},
        {"type": "formule", "tex": "…"},
        {"type": "tableau_signes", "var": "x", "crit": ["…"], "rows": [{"label": "…", "cells": ["+", "0", "-"], "final": false}]},
        {"type": "tableau_variations", "…": "…"},
        {"type": "liste", "items": ["…"]},
        {"type": "graphique", "xmin": 0, "xmax": 1, "ymin": 0, "ymax": 1, "segments": [], "asymptotes": [], "points": []}
      ],
      "resultat_tex": "E_1 = \\left]1;+\\infty\\right["
    }
  ],
  "resultat_tex": "ED = \\left]1;+\\infty\\right[",
  "controle": {"ok": true, "texte": "…"}
}
```

- `ok: false` ⇒ `erreur` est un message en français destiné à l'élève, **jamais une trace Python**.
- Les anciennes fonctions (`analyser_json`, `etudier_json`, `factoriser_json`) restent
  disponibles tant que toutes les pages ne sont pas migrées.

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
