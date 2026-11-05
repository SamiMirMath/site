# Chantier « Fondations » — suivi

Branche `fondations` (depuis `main` 96f183c), PC (WSL2), `PROCESSUS_PAGES=4`. Principe : aucun changement visible pour les élèves.
Consigne complète, plan et détails : `journal.md`. La consigne du chantier tient lieu de `decisions.md`.

## État des parties

| Partie | Contenu | État | Commit |
|---|---|---|---|
| F0 | Fiches, référence rafraîchie, `tests/outils/dump_sorties.py`, dump de départ | faite (suite verte) | voir `git log` |
| F1 | `verifier` : docs/ ignoré, baisse de sous-tests justifiée ici ; `test_lancer.py` | à faire | — |
| F2 | `lancer.py rapide` (reste de R4) | à faire | — |
| F3 | R1 : une seule liste des outils | à faire | — |
| F4 | R6 : `test_noyau` étendu, graphe d'imports figé, noms à plat uniques | à faire | — |
| F5 | R3 : ménage | à faire | — |
| F6 | Copie locale de KaTeX pour les tests de pages | à faire | — |

## Vérification après chaque partie

Dump brut comparé au dump de départ (commande exacte dans `journal.md`, section F0), instantanés et références inchangés, listes de
tests égales à la référence (sauf ajouts annoncés).

## Questions pour l'enseignant

(aucune)

## À relire par l'enseignant

(rien : aucun instantané ni texte affiché modifié)

## Variations de sous-tests

Format : test, avant → après, raison. Une baisse non justifiée ici fait refuser `verifier` (à partir de F1).

(aucune)

## Reprise après compactage

- Lire `CLAUDE.md`, ce fichier, puis `journal.md` (consigne du chantier, plan, section de la dernière partie).
- `git log --oneline main..fondations` : un commit par partie faite.
- Dump de départ : `/tmp/claude-1000/-home-sami-ubuntu-site/b574d683-7da7-4c53-a00c-237ca55256c7/scratchpad/dumps/depart`
  (hors du dépôt ; s'il a disparu, le refaire sur le commit F0 avec `tests/outils/dump_sorties.py`).
