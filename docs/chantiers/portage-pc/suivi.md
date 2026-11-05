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
| 2 | Référence propre au dépôt (`tests/reference/`), `lancer.py reference <dossier>`, défaut de `verifier` | à faire |
| 3 | `rapide --depuis <commit>` ; procédure allégée dans la méthode | à faire |
| 4 | `CLAUDE.md` (autorisé pour ce point) | à faire |
| 5 | `diagnostic.md` versé | à faire |

## Questions ouvertes

(aucune pour l'instant)

## À relire par l'enseignant

- Point 1 : `tests/lancer.py` seul (`processus_pages()`, contrôle en tête de `main` pour rapide, pages, complet). Sans la variable, les
  commandes lancées sont identiques à celles d'avant. Aucun test ajouté (pas de test de `lancer.py`, question ouverte de
  `tests-rapides`, e.6) : vérifications à la main, dans `journal.md`.

## Reprise après compactage

Lire ce fichier, puis `git log --oneline main..HEAD` et `journal.md`. Les dossiers de rapport sont dans le scratchpad de la session.
