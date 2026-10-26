# Documentation interne — samimir.ch

Ce dossier n'est **pas publié** sur le site (`_config.yml` l'exclut de GitHub Pages).

## Sommaire

| Fichier | Contenu |
|---|---|
| [analyse-2026-10-13.md](analyse-2026-10-13.md) | État des lieux du dépôt (architecture, problèmes classés, mesures de chargement) |
| [choix-techniques.md](choix-techniques.md) | Architecture cible, décisions validées, options écartées, coût d'un Pyodide auto-hébergé |
| [specifications/socle-commun.md](specifications/socle-commun.md) | Ce que toute page outil doit faire (saisie, hasard, étapes, impression, mobile, accessibilité, notation suisse) |
| [specifications/accueil.md](specifications/accueil.md) | Page d'accueil et registre des outils |
| [specifications/ensemble-definition.md](specifications/ensemble-definition.md) | Outil « Ensemble de définition » (3e Ms/Mr) |
| [specifications/derivee-variations.md](specifications/derivee-variations.md) | Outil « Dérivée, signe et variations » (3e Ms/Mr) |
| [specifications/limites-asymptotes.md](specifications/limites-asymptotes.md) | Outil « Limites et asymptotes » (3e Ms/Mr) |
| [specifications/etude-complete.md](specifications/etude-complete.md) | Outil « Étude complète de fonction » (3e Ms/Mr) |
| [specifications/factorisation.md](specifications/factorisation.md) | Outil « Factorisation » (1re C/Ms/Mr) |
| [specifications/exponentielles-logarithmes.md](specifications/exponentielles-logarithmes.md) | Outil « Exponentielles et logarithmes » (3C ; 2M plus tard) |
| [specifications/simplexe.md](specifications/simplexe.md) | Outil « Programmation linéaire » (2e) |
| [a-valider.md](a-valider.md) | Questions ouvertes : rien n'est changé sur ces points tant qu'elles ne sont pas tranchées |
| [guide-redaction.md](guide-redaction.md) | Format de rédaction des corrigés (minimum de lignes) : règles R1–R11 et 7 exemples de référence |
| [taches.md](taches.md) | Découpage en tâches indépendantes, chacune avec sa vérification |
| [futur_outils.md](futur_outils.md) | Outils proposés d'après le plan d'études (brochure officielle) (non spécifiés, à choisir) |

## Lancer les tests en local

Une seule commande, depuis la racine du dépôt (utilise `uv` et `python3.12`, déjà présents ;
SymPy est pris dans le cache de `uv`, rien n'est installé dans le système) :

```sh
uv run -q --no-project --python 3.12 --with sympy==1.13.3 python -m unittest discover -s tests/python
```

Versions de référence : **Python 3.12 et SymPy 1.13.3**, identiques à celles de Pyodide 0.27.7
utilisé par le site. Le code des moteurs exige Python ≥ 3.12 (syntaxe des f-strings).

## Tests de pages (navigateur, local et CI)

Chrome sans interface piloté depuis Python (Google Chrome installé ; Node inutile). Pyodide, SymPy et mpmath
viennent d'une copie locale non versionnée (`tests/pages/pyodide-local/`, ≈ 18 Mo) ; KaTeX vient encore de jsDelivr
(réseau requis). Hors de `tests/python` : la commande ci-dessus ne les lance pas.

```sh
# une fois (et à chaque changement de version de Pyodide dans moteur/manifeste.json) : télécharger la copie
python3 tests/pages/pyodide_local.py
# le rendu de chaque page est égal à la référence (tests/pages/references/*.json), ~ 3 min
uv run -q --no-project --python 3.12 --with sympy==1.13.3 --with websockets \
    python -m unittest discover -s tests/pages          # OUTILS=etude-complete pour une seule page
# après un changement VOULU du rendu : régénérer puis relire le diff git
uv run -q --no-project --python 3.12 --with sympy==1.13.3 --with websockets python tests/pages/capturer_references.py [outil …]
# captures d'écran avant/après un changement de CSS (non versionnées)
… --with pillow python tests/pages/captures.py enregistrer DOSSIER   puis   comparer AVANT APRES
```

## Conventions de ces documents

- Chaque critère d'acceptation a un identifiant (`ED-03`, `SOC-12`…) et un mode de vérification :
  - **[auto-py]** test Python dans `tests/python/` (local + CI) ;
  - **[auto-js]** test Node dans la CI uniquement (`node --test`) ;
  - **[auto-page]** test de page dans la CI (navigateur sans interface) ;
  - **[manuel]** vérification à la main (téléphone, impression).
- **À valider** : point non tranché par l'enseignant. Le comportement actuel est conservé tant
  que la question reste ouverte (voir [a-valider.md](a-valider.md)).
- Les URL publiques des outils (`/ensemble-definition/`, `/factorisation/`…) et le paramètre
  `?f=` ne changent pas : des liens circulent chez les élèves.

## Corrections déjà faites (13.10.2026)

| Commit | Correction | Test |
|---|---|---|
| `14e0ee8` | Dérivée de x^(p/q) fausse (fraction mal transmise à SymPy) | `tests/python/test_derivee_puissances.py` |
| `70e6b1e` | Asymptote verticale annoncée alors que les deux limites sont finies ; genre « saut » (remplacé par la formulation Q7, tâche T08b) | `tests/python/test_limites_deux_cotes.py` |
| `a9b2a6e` | Étapes de la dérivée annonçant « f'(x) = … » pour un morceau de f | `tests/python/test_derivee_narration.py` |
