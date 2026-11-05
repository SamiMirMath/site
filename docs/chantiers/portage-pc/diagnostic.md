# Portage sur PC (WSL2 Ubuntu) — étape 0 : diagnostic

Date : 04.11.2026. Diagnostic seul : aucun fichier suivi du dépôt modifié, aucune correction appliquée au code ni aux tests,
aucune référence régénérée. Seule action hors diagnostic, à la demande de l'enseignant : le téléchargement de la copie locale
de Pyodide (`tests/pages/pyodide-local/`, ignorée par git). Ce fichier n'est pas commité.

## Conclusion

**La suite complète est verte sur le PC** dès que la copie locale de Pyodide est présente : `python3 tests/lancer.py complet`
renvoie 0, avec le corpus complet. Il n'y a eu aucun échec lié au chemin de Chrome, aux polices et largeurs ni aux références de pages.

| Suite | Résultat | Durée PC | Mac (audit.md, chiffres de la demande) | Mac (CLAUDE.md, 29.10.2026) |
|---|---|---|---|---|
| Python (`-n auto` = 12 processus) | verte : 1 296 réussis, 1 xfail (attendu), 101 738 sous-tests | **120 s** (135 s au 1er lancement) | 718 s (÷ 6,0) | 322 s (÷ 2,7) |
| Pages (`-n 2`, corpus complet) | verte : 122 réussis, 2 386 sous-tests, aucun ignoré | **540 s** | 944 s (÷ 1,75) | 589 s (÷ 1,09) |
| Total `complet` | code de retour **0** | **663 s** (11 min 03 s) | 1 662 s | 911 s |

`docs/chantiers/tests-rapides/audit.md` n'existe pas dans ce dépôt (ni le dossier, ni dans l'historique git d'aucune branche) :
les chiffres 718 s et 944 s viennent de la demande ; ceux du 29.10.2026 (322 s et 589 s, après parallélisation) viennent de CLAUDE.md.

## Machine

| | PC (ce diagnostic) | Mac de l'enseignant |
|---|---|---|
| Système | WSL2, noyau 6.18.54.1-microsoft-standard-WSL2, Ubuntu | macOS |
| Processeur | AMD Ryzen 5 5600X : 6 cœurs physiques, 12 logiques | 2 cœurs physiques (4 logiques) |
| Mémoire | 15 Go (+ 4 Go d'échange) | — |
| Chrome | Google Chrome 157.0.8103.38, `/usr/bin/google-chrome` | `/Applications/Google Chrome.app/…` |
| uv | 0.13.7 (fournit Python 3.12, SymPy 1.13.3, mpmath 1.3.0) | — |
| Polices | 119 faces : DejaVu, Liberation, Ubuntu ; ni Roboto, ni Helvetica, ni Segoe UI | polices système Apple |
| Réseau | jsDelivr joignable (KaTeX : HTTP 200 en 0,16 s) | — |

État du dépôt : `main` à `ca6c243` ; après les deux lancements, `git status` ne montre que ce dossier (`docs/chantiers/portage-pc/`) :
aucune référence ni aucun fichier suivi n'a été réécrit par les tests. La CI (ubuntu-latest, corpus réduit) est verte sur ce même
commit (exécution 41854811345, 15 min 11 s).

## Lancement 1 — sans la copie locale de Pyodide

`python3 tests/lancer.py complet`, code de retour **1** ; durée totale 144 s.

- Python : verte, 135,5 s (748 % de processeur en moyenne).
- Pages : 6 échecs, 111 erreurs, 5 réussis, en 1,5 s. **Une seule cause, classée « autre » : la copie locale de Pyodide était absente.**
  - 115 tests : `RuntimeError: copie locale de Pyodide absente : lancer  python tests/pages/pyodide_local.py`, levée par
    `_verifier_la_copie_locale()` dans `Navigateur.__enter__` (`tests/pages/navigateur.py:301`), avant même le lancement de Chrome :
    dans `setUpClass` de `test_rendu`, `test_graphique`, `test_largeurs`, `test_simplexe`, `test_clavier`, `test_comportement`,
    `test_accueil` (d'où des ERROR), et dans 4 tests de `test_pyodide_local.py`.
  - 2 tests de `test_pyodide_local.py` : `FileNotFoundError` sur `shutil.copytree(pyodide_local.DOSSIER, …)`
    (`tests/pages/test_pyodide_local.py:86` et `:99`), même cause.
  - C'est le comportement voulu du garde-fou (T30) : le test échoue avec la marche à suivre au lieu de passer en silence par le CDN.

## Téléchargement de la copie

`python3 tests/pages/pyodide_local.py` (Python 3.14.4 du système ; le script n'utilise que la bibliothèque standard) :
Pyodide 0.27.7 (`pyodide.js`, `pyodide.asm.js`, `pyodide.asm.wasm`, `python_stdlib.zip`, `pyodide-lock.json`) et les roues
SymPy 1.13.3 et mpmath 1.3.0, téléchargés depuis jsDelivr et vérifiés ; 18 Mo, 3 s, code de retour 0.

## Lancement 2 — avec la copie

`python3 tests/lancer.py complet` (corpus complet : ni `CORPUS` ni `OUTILS` définis), code de retour **0** ; durée totale 663 s,
174 % de processeur en moyenne, 359 Mo de mémoire au plus.

- Python : 1 296 réussis, 1 xfail (attendu), 101 738 sous-tests, **120,2 s**.
- Pages : 122 réussis, 2 386 sous-tests, aucun ignoré, aucun échec attendu, **540,3 s**.

### Classement des échecs

| Catégorie | Nombre | Constat |
|---|---|---|
| Chemin de Chrome | 0 | `trouver_chrome()` trouve `google-chrome` dans le PATH (`tests/pages/navigateur.py:31`) ; Chrome 157 sans interface tourne sous WSL2 sans serveur graphique, deux instances en parallèle. |
| Polices et largeurs | 0 | `test_largeurs.py` vert de 320 à 1100 px pour tous les outils, `CONNUS` vide, alors que `system-ui` donne ici DejaVu Sans (plus large que la police du Mac). |
| Références de pages | 0 | `test_rendu.py` (corpus complet, 7 références) et `test_graphique.py` (`graphique-traces.json`) verts : premier passage connu du corpus complet sous Linux. |
| Autre | 0 | (la cause du lancement 1 est levée) |

## Remarques

- **Polices différentes, résultat identique.** Le PC teste la mise en page avec DejaVu Sans, le Mac avec sa police système : les deux
  sont verts, ce qui renforce le filet de sécurité (une police plus large passe aussi). Ce n'est pas la police des iPhone des élèves :
  le balayage du PC ne remplace pas une relecture à 390 px sur le Mac ou sur un téléphone.
- **La suite de pages profite peu du PC** (÷ 1,09 par rapport aux 589 s du Mac) : elle est limitée à deux Chrome (`-n 2` dans
  `tests/lancer.py`), et le processeur est occupé à 174 % en moyenne sur 12 cœurs logiques. Voir l'essai `-n 4` ci-dessous.
- **Variation entre lancements** : 135 s puis 120 s pour la suite Python (premier lancement : création de l'environnement `uv` et caches
  froids probables).

## Essai : suite de pages avec `-n 4`

Demandé par l'enseignant, sans commit ni modification de `tests/lancer.py`. J'ai lancé à la main la commande de `lancer.py pages`,
en remplaçant seulement `-n 2` par `-n 4` (corpus complet, `--dist load` ; `--durations` ajouté pour la mesure, sans effet sur les tests) :

| Lancement | Résultat | Durée |
|---|---|---|
| `-n 2` (lancement 2 ci-dessus) | 122 réussis, 2 386 sous-tests | 540 s |
| `-n 4`, essai 1 | 122 réussis, 2 386 sous-tests | **286 s** |
| `-n 4`, essai 2 | 122 réussis, 2 386 sous-tests | **297 s** |

- **Gain : ÷ 1,85 environ** (540 s → 286–297 s), stable et vert sur les deux essais. Aucun délai n'a été dépassé : les attentes des
  tests sont larges (60 à 240 s, `tests/pages/navigateur.py:238`, `tests/pages/rendu.py:109`).
- **Plancher** : le test le plus long, `test_graphique.py::test_traces_egales_aux_references`, dure 115 s à lui seul (puis
  `test_clavier.py` 74 s et 69 s, `test_rendu.py::test_exponentielles_logarithmes` 49 s). Avec plus de processus, la suite ne peut
  pas descendre sous ce test (et le démarrage de son Chrome) ; `-n 6` n'a pas été essayé.
- **Le Mac garde `-n 2`** : il n'a que 2 cœurs physiques, et les mesures du 29.10.2026 y ont été faites avec `-n 2`.
- **Correction minimale possible, non appliquée** : nombre de processus de pages réglable dans `tests/lancer.py`, par une variable
  d'environnement (par exemple `PROCESSUS_PAGES`, 2 par défaut, donc rien ne change sur le Mac ni dans la CI) ; sur le PC,
  `PROCESSUS_PAGES=4 python3 tests/lancer.py complet` donnerait environ 120 + 290 ≈ 410 s au lieu de 663 s. Cela ne touche à
  aucun test ni à aucun garde-fou. À faire, si l'enseignant le souhaite, sur une branche dédiée avec la fiche de suivi.

## Corrections minimales proposées (aucune appliquée)

1. **Copie locale de Pyodide : seule action nécessaire, déjà faite** (à la demande de l'enseignant) ; à refaire une fois par version de
   Pyodide, comme le fait la CI. Aucun fichier suivi ne change, aucun test n'est affaibli.
2. **Documentation (facultatif, une ligne).** Ajouter à la section « Commandes de test » de CLAUDE.md : « Première installation sur une
   machine : `python3 tests/pages/pyodide_local.py` (copie locale de Pyodide, une fois par version) ». Je déconseille de faire
   télécharger la copie automatiquement par `lancer.py` : le message d'échec actuel est clair, et un téléchargement implicite
   masquerait une dépendance au réseau.
3. **Chemin de Chrome : rien à faire.** Une variable d'environnement `CHROME` (consultée en tête de `trouver_chrome()`, avec un échec
   clair si elle ne désigne pas un exécutable) ne servirait que pour imposer la même version de Chrome sur les deux machines ; inutile
   tant que les deux suites sont vertes.
4. **Polices : rien à faire.** Aucun échec de largeur.

## Suite proposée

Si le portage continue (par exemple la note dans CLAUDE.md, ou le nombre de processus de pages réglable), créer une branche dédiée
depuis `main` et la fiche `docs/chantiers/portage-pc/suivi.md` (avec `journal.md`), selon CLAUDE.md. Sinon, le PC peut déjà servir
tel quel pour lancer la suite complète avant un commit.

Journaux bruts (hors dépôt), dans `/tmp/claude-1000/-home-sami-ubuntu-site/a5d52da8-e01b-4cf9-9bbb-113a4ea04796/scratchpad/` :
`complet.log` et `complet.time` (lancement 1), `complet2.log` (lignes horodatées) et `complet2.time` (lancement 2),
`n4.log`, `n4.time`, `n4b.log` et `n4b.time` (essais `-n 4`).
