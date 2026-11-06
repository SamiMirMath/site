# Chantier « moteur-serveur » — suivi

Branche `moteur-serveur` (depuis `main` e59fb05), PC (WSL2), `PROCESSUS_PAGES=4`. Font foi : `CLAUDE.md` > `decisions.md` > ce
fichier > `audit-etape0.md`. Le détail (plans, commandes, temps, rapports) est dans `journal.md`. L'arbre des tâches, `arbre.md`, est
un document de travail **jamais commité** (`.gitignore`).

**Invariants** (`decisions.md` § 1) :
- `tests/outils/dump_sorties.py` est identique à l'octet au dump de départ après chaque partie. Le dump de départ est dans
  `/home/sami-ubuntu/nuits/moteur-serveur/dumps/depart` : 19 fichiers, 4 598 sorties.
- À partir de P1, le dump par HTTP est identique au dump direct.
- Les références de pages restent identiques, `CONNUS` reste vide, et aucun moteur ne change (T9).

## État des parties

| Partie | Contenu | État | Commit |
|---|---|---|---|
| P0 | fiches, `decisions.md` validé, référence des tests, dump de départ, `.gitignore` (`arbre.md`) | fait | commit « P0 » de la branche |
| P1 | `serveur/app.py`, `test_serveur.py`, `dump_sorties.py --serveur`, liste blanche publique, A10 | à faire | — |
| P2 | scripts du VPS et `INSTALLATION.md`, puis commande et installation du VPS (enseignant) | à faire | — |
| P3 | `MoteurServeur`, messages, gardes T7, outil du 2e degré par le serveur, `essai.samimir.ch` | à faire | — |
| P4 | les autres outils, un commit chacun | à faire | — |
| P5 | retrait de Pyodide, KaTeX et polices sur le VPS, GoatCounter sans la requête | à faire | — |
| P6 | bascule : Action, DNS, certificats, gel de Pages, dépôt privé | à faire | — |

## Suite verte

- P0 : référence prise sur e59fb05 (`complet --rapport`, code 0). Par rapport à l'ancienne référence : 193 tests Python et 13 de
  pages nouveaux, 50 tests qui changent de nombre de sous-tests, dont une baisse déjà justifiée (`journal.md`, P0).
- P0, suite d'avant commit (`rapports/P0`) : code 0 ; Python 1 686 passés + 1 xfail, 132 568 sous-tests ; pages 158 passés,
  2 529 sous-tests.
- P0, après la 1re version du commit (d1a9ec1) : `verifier` ACCEPTÉ ; `rapide --depuis HEAD~1` vert ; `MEMO=0` identique nom par
  nom. Commit refait le 06.11.2026 (corrections de `journal.md` et `suivi.md`, message) : suite `rapports/P0b`, contrôles notés au
  début de P1.

## Questions ouvertes

Aucune : les questions du § 9 de `decisions.md` sont toutes réglées (06.11.2026).

## À relire par l'enseignant

Rien pour P0.

## Écarts

Aucun.

## Variations de sous-tests

Aucune.

## Tests disparus ou renommés

Aucun.

## Reprise après compactage

1. Lire `CLAUDE.md`, `decisions.md` (il fait foi), ce fichier, puis `journal.md` (la dernière partie seulement) et `arbre.md`.
2. `git log --oneline -5` sur la branche `moteur-serveur` : la dernière partie commitée est la dernière ligne « fait » ci-dessus.
3. Dossier de travail hors du dépôt : `/home/sami-ubuntu/nuits/moteur-serveur`, avec `rapports/<partie>` (`complet --rapport`) et
   `dumps/depart` (19 fichiers, 4 598 sorties), `dumps/depart-p1` (`--processus 1`, temps natifs), puis `dumps/<partie>`.
4. Avant chaque commit : `PROCESSUS_PAGES=4 python3 tests/lancer.py complet --rapport /home/sami-ubuntu/nuits/moteur-serveur/rapports/<partie>`
   (code 0), dump identique (`diff -r --exclude=temps`), puis commit, puis `python3 tests/lancer.py verifier <dossier>` (ACCEPTÉ).
5. Ne jamais commiter `arbre.md`, `docs/reference/`, ni rien hors des fichiers de la partie ; ne jamais pousser ni fusionner.
