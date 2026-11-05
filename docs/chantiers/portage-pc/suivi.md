# Chantier « Portage PC » — suivi

## Cadre

Branche `portage-pc`, créée le 05.11.2026 depuis `main` à jour (c9b257f, fusion de `tests-rapides` présente). Une seule session sur le
PC (WSL2 Ubuntu, Ryzen 5 5600X, 12 cœurs logiques), sans sous-agent. Méthode : `docs/methode-chantiers.md`. Diagnostic de départ :
[`diagnostic.md`](diagnostic.md). Détail (commandes, durées, comparaisons) : [`journal.md`](journal.md).

Avant chaque commit : `PROCESSUS_PAGES=4 python3 tests/lancer.py complet --rapport <dossier>` (dossier dans le scratchpad), puis
`python3 tests/comparer_listes.py <référence> <dossier>` : mêmes tests nom par nom, hors ajouts annoncés.

## État des points

| Point | Contenu | État |
|---|---|---|
| 1 | `PROCESSUS_PAGES` dans `tests/lancer.py` | **fait** : suite verte avec 4 (pages 299 s) et sans la variable (548 s), listes identiques entre elles et à la référence |
| 2 | Référence propre au dépôt (`tests/reference/`), `lancer.py reference <dossier>`, défaut de `verifier` | **fait** : référence = lancement sur `main` (c9b257f) ; suite verte (`PROCESSUS_PAGES=4`), identique à la référence |
| 3 | `rapide --depuis <commit>` ; procédure allégée dans la méthode | **fait** (suite verte, identique à la référence) |
| 4 | `CLAUDE.md` (autorisé pour ce point) | à faire |
| 5 | `diagnostic.md` versé | à faire |

## Questions ouvertes

(aucune pour l'instant)

## À relire par l'enseignant

- Point 1 : `tests/lancer.py` seul (`processus_pages()`, contrôle en tête de `main` pour rapide, pages, complet). Sans la variable, les
  commandes lancées sont identiques à celles d'avant. Aucun test ajouté (pas de test de `lancer.py`, question ouverte de
  `tests-rapides`, e.6) : vérifications à la main, dans `journal.md`.
- Point 2 : `tests/lancer.py` (commande `reference`), `tests/verifier.py` (référence par défaut : `tests/reference`),
  `tests/comparer_listes.py` (exemple du docstring), `docs/methode-chantiers.md` (puce « Référence au P0 »). Nouveau : `tests/reference/`
  (4 listes + `origine.txt`). Règle d'acceptation de `reference` : voir `journal.md`, « Point 2 ». `docs/chantiers/tests-rapides/reference`
  n'est pas touchée (archive).
- Point 3 : `tests/lancer.py` (`fichiers_modifies(depuis)`, `rapide(…, depuis)`, options de `rapide` / `liste`),
  `docs/methode-chantiers.md` (étape 3 du contrôle allégé). Répond à la question e.2 de `tests-rapides`. Changement de comportement :
  `rapide` et `liste` refusent désormais une option inconnue (code 2, aide) au lieu de l'ignorer, pour qu'une faute de frappe
  (`--depui`) ne lance pas en silence le contrôle sur HEAD.
- `verifier` refuse les rapports de ce chantier pour un seul motif (b) : vos 4 fichiers non suivis (`docs/architecture.md`,
  `docs/chantiers/equations-2e-degre/quiz.md`, `docs/chantiers/revue-structure/rapport.md`, et `diagnostic.md` jusqu'au point 5), que je
  n'ai ni commités ni déplacés. Contrôle retenu, comme demandé : `comparer_listes`.

## Reprise après compactage

Lire ce fichier, puis `git log --oneline main..HEAD` et `journal.md`. Les dossiers de rapport sont dans le scratchpad de la session.
