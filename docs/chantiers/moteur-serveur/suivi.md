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

## Questions ouvertes

Questions pour l'enseignant (P1, 07.11.2026 ; l'option prise est en service, rien n'est affiché aux élèves) :
1. **CLAUDE.md dit « A1–A9 »** (§ Architecture). Proposition : « A1–A10 ». Non modifié (accord nécessaire).
2. **`rapide` ne connaît pas `serveur/`** : après le commit, une modification de `serveur/app.py` seule ne relance ni
   `test_serveur.py` ni `test_imports.py` (seulement les tests de fumée) ; de même pour `tests/outils/dump_sorties.py`, que
   `test_serveur.py` charge par son chemin. Proposition : dans `tests/lancer.py`, relancer ces deux tests pour `serveur/*.py` et
   `test_serveur.py` pour `tests/outils/dump_sorties.py`. `lancer.py` non modifié.
3. **A10 et `/api/sante`** : T1 fait faire au serveur un vrai calcul, `resoudre` du 2e degré : c'est la seule mention d'un outil
   dans `serveur/app.py` (`CALCUL_DE_SANTE`). Il passe par la liste blanche du manifeste, et `TestA10` ne la tolère que là. À
   confirmer (ligne A10 de `architecture.md`).
4. **Fichier d'état de `/api/sante`** (format choisi en P1, écrit par le minuteur de P2) : JSON
   `{"certificat_expire": "<ISO 8601>", "disque_pourcent": …}`, refusé s'il date de plus de **3 h** (une écriture horaire manquée
   tolérée, pas deux). La réponse 503 dit sa raison (`{"ok": false, "raison": "disque"}`…), utile depuis le téléphone (§ 5.2) ; elle
   ne contient aucune donnée d'élève. À confirmer.
5. **Versions au démarrage** (ajout de P1, au-delà de T3) : l'application refuse de démarrer si Python, SymPy ou mpmath n'ont pas
   la version du manifeste. La clé `pyodide` est sautée, nommée dans `app.py` ; à retirer avec elle en P5.

## À relire par l'enseignant

- P1 : `docs/architecture.md`, ligne **A10** (texte de T2, plus la phrase sur `/api/sante` de la question 3).
- Instantanés : **aucun** modifié (P1 ne touche aucun moteur ni aucun outil partagé).

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
