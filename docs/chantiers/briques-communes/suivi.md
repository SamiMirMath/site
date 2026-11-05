# Chantier « Briques communes » — suivi

Branche `briques-communes` (depuis `main` 5ce3f8c), PC (WSL2), `PROCESSUS_PAGES=4`. R5 de la revue de structure
(`docs/chantiers/revue-structure/rapport.md` § 4.2), prérequis de `docs/chantiers/equations-2e-degre/decisions.md`.
Principe : **aucune sortie existante ne change** (dump brut identique à l'octet au dump de départ, instantanés et références de pages
inchangés). Consigne complète, plans et détails : `journal.md`. La consigne du chantier et `decisions.md` du 2e degré (Prérequis, D13,
D25, E14, § 5, P3) tiennent lieu de décisions.

## État des parties

| Partie | Contenu | État | Commit |
|---|---|---|---|
| B0 | Fiches, référence rafraîchie (1 392 tests Python dont 1 xfail, 106 244 sous-tests ; 138 tests de pages, 2 407 sous-tests), dump de départ (4 148 sorties, déterministe) | faite (suite verte) | voir `git log` |
| B1 | `moteur/expr.py` : arbre d'Exp-log, `tex`, parseur (« membre = membre ») ; réexport par `exp_log` ; manifeste | à faire | — |
| B2 | `moteur/chaine.py` : Eq, Rel, Ou, Texte, Chaine, Message, `tex_element`, `tex_chaine`, `rangees_chaine`, propriétés génériques ; trois options désactivées par défaut | à faire | — |
| B3 | Type de bloc « chaine » (A4 : `sortie.py`, `valider`, `rendu.js`, test), ligne pleine largeur au milieu ; Exp-log inchangé (exception nommée) | à faire | — |
| B4 | CSS : `.chaine` dans `commun/composants.css`, `details ol` dans `commun/style.css` | à faire | — |
| B5 | `nombres.approx(x, decimales=3)` et `nombres.exact(x, decimaux_enonce=False)`, fonctions pures, aucun outil rebranché ; tests croisés | à faire | — |
| B6 | `oracle.racines(coeffs)` (mpmath 50 chiffres) et ses tests | à faire | — |

## Vérification après chaque partie

Dump brut comparé au dump de départ (commandes exactes dans `journal.md`, section B0), instantanés et références inchangés, listes de
tests égales à la référence (sauf ajouts annoncés), `test_imports` à jour (aucune arête `chaine` → `exp_log`, aucune arête `moteur/` → un
outil), `test_manifeste` vert, `test_largeurs` avec `CONNUS` vide.

## Questions pour l'enseignant

(aucune pour l'instant)

## À relire par l'enseignant

(rien pour l'instant ; B0 ne modifie ni instantané, ni référence de page, ni sortie)

## Variations de sous-tests

Lue par `verifier` (voir sa docstring, point (d)). Format, une ligne par test, commençant en début de ligne par un tiret :
`` - `<identifiant pytest complet>` : <avant> → <après> : <raison> `` (« -> » vaut « → »). <avant> et <après> sont les nombres de
sous-tests passés de la référence et du lancement, exactement ceux que `verifier` affiche ; sinon refus.

## Reprise après compactage

- Lire `CLAUDE.md`, ce fichier, puis `journal.md` (consigne du chantier, section B0 pour les commandes, section de la dernière partie).
- `git log --oneline main..briques-communes` : un commit par partie faite.
- Dump de départ : `/tmp/claude-1000/-home-sami-ubuntu-site/4164342b-a2d3-4999-80ff-850ac94e5e5e/scratchpad/briques/dumps/depart`
  (hors du dépôt ; s'il a disparu, le refaire sur le commit B0 avec `tests/outils/dump_sorties.py`, commande dans `journal.md`).
- Rapports `complet --rapport` : `/tmp/claude-1000/-home-sami-ubuntu-site/4164342b-a2d3-4999-80ff-850ac94e5e5e/scratchpad/briques/rapports/<partie>`.
