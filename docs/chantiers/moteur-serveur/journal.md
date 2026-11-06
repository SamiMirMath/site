# Chantier « moteur-serveur » — journal

Détail des parties : plan, commandes, temps et rapports. `suivi.md` reste court. Dossier de travail hors du dépôt :
`W=/home/sami-ubuntu/nuits/moteur-serveur`.

## P0 — départ (06.11.2026, soir, PC)

**Plan.**
1. Branche `moteur-serveur` depuis `main` à jour (e59fb05 = `origin/main`). L'ancienne branche locale du même nom, déjà fusionnée
   (d9a89c5, audit), a été supprimée puis recréée.
2. Référence des tests (méthode, « Référence au P0 »). Elle exige qu'aucun fichier hors de `docs/` ne soit modifié : la modification
   de `.gitignore` (ligne `arbre.md`, demandée par l'enseignant le 06.11.2026) a été mise de côté (`git stash push -- .gitignore`)
   pendant le lancement, puis rétablie.
3. Dump de départ, avec 6 processus puis 1 processus.
4. Fiches `suivi.md` et `journal.md` ; statut « validé » de `decisions.md`.
5. Suite complète d'avant commit, commit, `verifier`.

**Référence des tests.**

    PROCESSUS_PAGES=4 python3 tests/lancer.py complet --rapport $W/rapports/P0-reference     # 23 h 24 → 23 h 32, code 0
    python3 tests/lancer.py reference $W/rapports/P0-reference                               # code 0

- Python : 1 687 collectés, 1 686 passés + 1 xfail, 132 568 sous-tests (111,8 s).
- Pages : 158 collectés, 158 passés, 2 529 sous-tests (348,1 s).
- Par rapport à l'ancienne référence (chantier fondations, b72fe2e), venues des chantiers briques-communes et equations-2e-degre :
  - **193 tests Python et 13 de pages nouveaux**, aucun test disparu (`git diff -U0` des collectes : 0 ligne `-`) ;
  - 43 tests Python et 7 de pages existants **changent de nombre de sous-tests** ;
  - **une baisse** : `tests/python/test_exp_log.py::TestVouvoiement::test_aucun_texte_du_fichier_ne_tutoie` passe de 960 à 955,
    déjà justifiée dans `docs/chantiers/equations-2e-degre/suivi.md` (P1 et P3 de ce chantier).

  Correction du 06.11.2026 : la première version de ce journal disait « toutes des tests nouveaux », et le message du commit P0
  « seulement des ajouts ». C'est inexact, relevé par la vérification indépendante (ci-dessous).

**Dump de départ.**

    python3 tests/outils/dump_sorties.py $W/dumps/depart --processus 6        # 19 fichiers, 4 598 sorties, 5 s
    python3 tests/outils/dump_sorties.py $W/dumps/depart-p1 --processus 1     # 19 fichiers, 4 598 sorties, 14 s
    diff -r --exclude=temps $W/dumps/depart $W/dumps/depart-p1                # code 0

- Le dump est aussi identique à celui de l'audit (même commit des moteurs) : `diff` code 0.
- 4 598 sorties = 4 178 appels rejoués par HTTP dans l'audit (`resoudre`, `apercu`, `controle`) + 420 exercices tirés
  (`exercice`, graine fixée en processus, T8).

**Temps natifs** (`depart-p1/temps/temps.json`, `resoudre_json`, 1 processus) :

| Outil | Entrées | Total | Plus long appel |
|---|---|---|---|
| derivee-variations | 33 | 0,27 s | 0,083 s (`e^((-2x^2+3x-1)/(3x-6))`) |
| ensemble-definition | 42 | 0,03 s | 0,023 s (`sqrt(ln(x)-x+2)`) |
| equations-2e-degre | 225 | 0,48 s | 0,008 s (`x^3-(x-1)^3=1`) |
| etude-complete | 22 | 2,10 s | 0,298 s (`sqrt(x^2-4)`) |
| exponentielles-logarithmes C / M | 914 / 914 | 0,96 / 0,80 s | 0,005 / 0,004 s |
| factorisation | 309 | 1,92 s | 0,065 s (`x^3+6x^2-7x-60`) |
| limites-asymptotes | 66 | 6,16 s | 1,268 s (`x*e^x/(1-e^x)`) |

Le dump compte toute la durée de 1 processus : 13,9 s.

**Suite d'avant commit.**

    PROCESSUS_PAGES=4 python3 tests/lancer.py complet --rapport $W/rapports/P0        # 23 h 33 → 23 h 41, code 0

- Python : 1 686 passés + 1 xfail, 132 568 sous-tests (103,8 s).
- Pages : 158 passés, 2 529 sous-tests (343,0 s).

**Commit**, première version d1a9ec1 (9 fichiers : `.gitignore`, `decisions.md`, `suivi.md`, `journal.md`, 5 fichiers de
`tests/reference/`). Il a été **refait** le 06.11.2026 à la demande de l'enseignant (`git commit --amend`, branche non poussée), pour
inclure les corrections de `journal.md` et `suivi.md` et corriger son message. Hors de `docs/`, les deux versions ont les mêmes
fichiers. La suite d'avant le commit refait est dans `$W/rapports/P0b`. Ses nombres et son `verifier` sont notés au début de P1, avec
les contrôles de ce commit.

Ces nombres n'avaient pas été écrits ici avant le commit, avec une justification fausse : on croyait qu'un fichier de `docs/`
modifié après le lancement ferait refuser `verifier`. Or `verifier` ne contrôle pas `docs/` par empreinte (`IGNORES = ^docs/`,
`tests/verifier.py:47`) : il le liste seulement comme ignoré. Ils sont ajoutés après coup.

## Contrôles du chef d'orchestre

| Partie | Commit | `verifier` | `rapide --depuis HEAD~1` | `MEMO=0` | Remarque |
|---|---|---|---|---|---|
| P0 (1re version) | d1a9ec1 | ACCEPTÉ (listes identiques à la référence nom par nom) | code 0 : 23 tests Python, 278 sous-tests, 3,6 s ; aucune page (aucun fichier de page touché) | `complet --rapport $W/rapports/P0-memo0` sur d1a9ec1, arbre propre : code 0, `comparer_listes P0 P0-memo0` identique nom par nom (Python 120,7 s, pages 345,1 s) | — |

## Vérification indépendante du P0 (sous-agent, lecture seule, 06.11.2026)

Demandée par l'enseignant sur le compte rendu du P0. Sur les 9 affirmations, 6 vraies, 2 inexactes et 1 fausse :
- **Vraies** : les points 1, 3, 4, 5, 7 et 9 du compte rendu. Le dump relancé par le vérificateur sur d1a9ec1 est identique à
  `dumps/depart`.
- **Inexacte** : « seulement des ajouts » (corrigé ci-dessus).
- **Inexacte** : la procédure de référence. Elle est conforme, mais `decisions.md` a changé après la prise de référence (statut
  « validé » écrit après l'accord explicite de l'enseignant, « decisions.md validé, lance le P0 », 06.11.2026). C'est permis sous
  `docs/`.
- **Fausse** : la raison de ne pas noter la suite dans le journal (corrigé ci-dessus).
- **Manques relevés** :
  - la suite d'avant commit absente de `journal.md` et de `suivi.md` : corrigé ;
  - le contrôle `rapide --depuis HEAD~1` et la section des contrôles : faits et ajoutés ;
  - l'identité avec le dump de l'audit n'a pas été revérifiée par le vérificateur (le dump de l'audit est dans un dossier temporaire
    de la session).
- **Ambiguïté** : la méthode (« Machines ») dit « branche poussée en fin de session », mais CLAUDE.md dit de ne jamais pousser.
  CLAUDE.md fait foi : c'est l'enseignant qui pousse.
