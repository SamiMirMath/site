# Documentation interne — samimir.ch

Ce dossier n'est **pas publié** sur le site (`_config.yml` l'exclut de GitHub Pages).

## Sommaire

| Fichier | Contenu |
|---|---|
| [architecture.md](architecture.md) | Couches du site et règles A1–A9 (validé le 05.11.2026), exceptions nommées, ajout d'un outil |
| [choix-techniques.md](choix-techniques.md) | Architecture cible, décisions validées, options écartées, coût d'un Pyodide auto-hébergé |
| [methode-chantiers.md](methode-chantiers.md) | Méthode d'un chantier : rôles, étapes, règles d'exécution, organisation de nuit, contrôle allégé, fusion |
| [guide-redaction.md](guide-redaction.md) | Format de rédaction des corrigés (minimum de lignes) : règles R1–R20 et 8 exemples de référence |
| [specifications/socle-commun.md](specifications/socle-commun.md) | Ce que toute page outil doit faire (saisie, hasard, étapes, impression, mobile, accessibilité, notation suisse) |
| [specifications/accueil.md](specifications/accueil.md) | Page d'accueil et registre des outils |
| [specifications/ensemble-definition.md](specifications/ensemble-definition.md) | Outil « Ensemble de définition » (3e Ms/Mr) |
| [specifications/derivee-variations.md](specifications/derivee-variations.md) | Outil « Dérivée, signe et variations » (3e Ms/Mr) |
| [specifications/limites-asymptotes.md](specifications/limites-asymptotes.md) | Outil « Limites et asymptotes » (3e Ms/Mr) |
| [specifications/redaction-limites-3m.md](specifications/redaction-limites-3m.md) | Rédaction des limites (3M) d'après le corrigé du chapitre 8 : règles RL1–RL20, contrat des tests |
| [specifications/etude-complete.md](specifications/etude-complete.md) | Outil « Étude complète de fonction » (3e Ms/Mr) |
| [specifications/factorisation.md](specifications/factorisation.md) | Outil « Factorisation » (1re C/Ms/Mr) |
| [specifications/exponentielles-logarithmes.md](specifications/exponentielles-logarithmes.md) | Outil « Exponentielles et logarithmes » (3C ; filière M : 2Ms/Mr) |
| [specifications/simplexe.md](specifications/simplexe.md) | Outil « Programmation linéaire » (2e) |
| [a-valider.md](a-valider.md) | Questions ouvertes : rien n'est changé sur ces points tant qu'elles ne sont pas tranchées |
| [taches.md](taches.md) | Découpage en tâches indépendantes, chacune avec sa vérification |
| [futur_outils.md](futur_outils.md) | Outils proposés d'après le plan d'études (brochure officielle) (non spécifiés, à choisir) |
| [analyse-2026-10-13.md](analyse-2026-10-13.md) | Archive : état des lieux du dépôt au 13.10.2026 (architecture d'alors, problèmes classés, mesures de chargement) |
| `chantiers/<chantier>/` | Fiches de chantier : `suivi.md` (court), `journal.md` (détail), audits et décisions |
| `reference/` | Corrigés de l'enseignant (`.tex`, PDF) : non versionné (`.gitignore`), jamais publié |

## Lancer les tests en local

Depuis la racine du dépôt, toujours par `tests/lancer.py` (il appelle `uv`, qui fournit Python 3.12, SymPy 1.13.3, mpmath,
websockets, pytest et pytest-xdist ; rien n'est installé dans le projet). Détail de chaque commande : `CLAUDE.md` et la docstring
de `tests/lancer.py`.

```sh
python3 tests/lancer.py rapide      # pendant le travail : tests Python des fichiers modifiés, tests de fumée, pages touchées (corpus réduit)
python3 tests/lancer.py liste       # ce que rapide lancerait, sans rien lancer
python3 tests/lancer.py complet     # avant chaque commit : toute la suite Python, puis toute la suite de pages (corpus complet)
python3 tests/lancer.py python      # la suite Python seule ;  pages : la suite de pages seule
```

Versions de référence : **Python 3.12 et SymPy 1.13.3**, identiques à celles de Pyodide 0.27.7
utilisé par le site. Le code des moteurs exige Python ≥ 3.12 (syntaxe des f-strings).

## Tests de pages (navigateur, local et CI)

Chrome sans interface piloté depuis Python (Google Chrome installé ; Node inutile). Pyodide, SymPy et mpmath
viennent d'une copie locale non versionnée (`tests/pages/pyodide-local/`, ≈ 18 Mo) ; KaTeX vient encore de jsDelivr
(réseau requis). `python3 tests/lancer.py pages` (ou `complet`) les lance ; une seule page :
`OUTILS=etude-complete python3 tests/lancer.py pages`.

```sh
# une fois (et à chaque changement de version de Pyodide dans moteur/manifeste.json) : télécharger la copie
python3 tests/pages/pyodide_local.py
# après un changement VOULU du rendu : régénérer puis relire le diff git
uv run -q --no-project --python 3.12 --with sympy==1.13.3 --with websockets python tests/pages/capturer_references.py [outil …]
# captures d'écran avant/après un changement de CSS (non versionnées)
… --with pillow python tests/pages/captures.py enregistrer DOSSIER   puis   comparer AVANT APRES
```

## Conventions de ces documents

- Chaque critère d'acceptation a un identifiant (`ED-03`, `SOC-12`…) et un mode de vérification :
  - **[auto-py]** test Python dans `tests/python/` (local + CI) ;
  - **[auto-js]** test Node dans la CI (`node --test`) : **prévu**, pas encore en place (il n'y a ni `tests/js/` ni Node sur
    les machines) ; les critères ainsi marqués ne sont vérifiés par aucun test aujourd'hui ;
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
