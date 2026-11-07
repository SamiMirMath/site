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
| P1 | `serveur/app.py`, `test_serveur.py`, `dump_sorties.py --serveur`, liste blanche publique, A10 | fait | commit « P1 » de la branche |
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
  nom. Commit refait le 06.11.2026 (corrections de `journal.md` et `suivi.md`, message), 976bc7b. Contrôles au début de P1
  (07.11.2026) : `verifier rapports/P0c` ACCEPTÉ ; `rapports/P0b` REFUSÉ par construction (lancé sur d1a9ec1), ACCEPTÉ avec
  `--commit d1a9ec1`, et d1a9ec1 → 976bc7b ne change que `docs/` ; `rapide --depuis HEAD~1` vert.
- P1, suite d'avant commit (`rapports/P1`) : code 0 ; Python 1 720 passés + 1 xfail, 133 634 sous-tests (+34 tests, tous
  nouveaux) ; pages 158 passés, 2 529 sous-tests. Dump direct = dump de départ, dump par HTTP = dump direct (`diff` code 0) ; temps
  natifs sans hausse.
- P1, après le commit : `verifier rapports/P1` ACCEPTÉ ; `rapide --depuis HEAD~1` vert (64 tests) ; `MEMO=0` identique nom par
  nom (`rapports/P1-memo0`).
- P1, corrections de la relecture (second commit, `rapports/P1-relecture`) : code 0 ; Python 1 722 passés + 1 xfail,
  133 641 sous-tests ; pages 158 passés, 2 529 sous-tests.
- P1, cas de 404 rétabli (troisième commit, `rapports/P1-relecture2`) : code 0 ; Python 1 722 passés + 1 xfail, 133 642
  sous-tests ; pages 158 passés, 2 529 sous-tests.

## Questions ouvertes

Aucune. Les questions de P1 sont réglées (enseignant, 07.11.2026 ; chaque fois l'option recommandée) :
1. ✓ **CLAUDE.md « A1–A10 »** : oui, au premier commit de P2 (avec la citation de `docs/architecture.md` § 7).
2. ✓ **`rapide` et `serveur/`** : oui, pour tout `serveur/` (scripts de P2 compris), plus `tests/outils/dump_sorties.py` et
   `tests/pages/rendu.py` : ils relancent `test_serveur.py` et `test_imports.py`. Au début de P2 : `tests/lancer.py` (règle et
   docstring), un test dans `test_lancer.py`, la description de `rapide` dans CLAUDE.md.
3. ✓ **A10 et `/api/sante`** : l'exception reste telle quelle (`CALCUL_DE_SANTE`, bornée par `TestA10`).
4. ✓ **Fichier d'état** : tel quel (JSON `certificat_expire`, `disque_pourcent` ; périmé après 3 h ; raison dans le 503). Le
   minuteur de P2 écrit ce format.
5. ✓ **`MOTEUR_VERSION` absente ou mal formée → 503** : oui. P2 fournit la variable au service.
6. ✓ **Versions au démarrage** : refuser de démarrer si Python, SymPy ou mpmath diffèrent du manifeste.
7. ✓ **Ouverture des pages** (question nouvelle, relevée en préparant les questions) : selon T6, la page interroge `/api/sante` à
   l'ouverture ; un 503 pour le disque, le certificat ou la version bloquerait les élèves avec « Impossible de charger l'outil de
   calcul. Vérifiez votre connexion internet… », un message inexact. Réponse : **contrôle séparé**. La page interroge une adresse qui
   vérifie seulement qu'un calcul répond, et `/api/sante` (disque, certificat, version) ne sert qu'à la surveillance (T13). À faire
   en P2 ou P3 : l'adresse dans `serveur/app.py`, ses tests, et T6 retouché dans `decisions.md` (accord de l'enseignant sur le
   principe, 07.11.2026 ; texte à lui faire relire).
8. ✓ **Commits limités à `docs/`** (question nouvelle, 07.11.2026) : la suite complète n'y protège rien, car aucun test ne lit
   `docs/` (`tests/verifier.py`, `IGNORES`). Décision : pour un commit qui ne touche que `docs/`, `rapide` suffit. Texte proposé pour
   CLAUDE.md (§ Git), au premier commit de P2 : « Exception : un commit qui ne touche que `docs/` (jamais `docs/reference/`) se
   contente de `python3 tests/lancer.py rapide` (code 0) ; pas de suite complète ni de `verifier` pour lui. » Le commit des réponses
   ci-dessus a encore suivi l'ancienne règle (suite `rapports/P1-reponses`).
9. ✓ **Offre du VPS** (07.11.2026, à la commande) : **2 vCPU, 2 Go, 40 Go** au lieu de 1 vCPU (M1). Commandé : Ubuntu 24.04.4,
   IPv4 179.237.105.75 (détail : `journal.md`, « Commande du VPS »). À reporter dans `decisions.md` (M1, § 6, § 9 question 7)
   avec l'accord de l'enseignant.

## À relire par l'enseignant

- P1 : `docs/architecture.md`, ligne **A10** : exception de `/api/sante` confirmée (question 3) ; le reste de la ligne (phrase sur
  A8, garde-fous) reste à relire.
- Instantanés : **aucun** modifié (P1 ne touche aucun moteur ni aucun outil partagé).

## Écarts

- P1 a trois commits (b41c190 ; « corrections de la relecture » ; puis un cas de 404 retiré à tort, rétabli), au lieu d'un par
  partie (méthode) : le prompt de P1 demandait un nouveau commit pour toute correction de code ou de tests issue de la relecture,
  sans amend (le rapport de la suite, lancé sur le commit précédent, ne vaut que pour un commit enfant ; un amend hors de `docs/`
  demanderait de relancer la suite sur son parent). CLAUDE.md permet « un commit par partie (ou par phase) ».

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
