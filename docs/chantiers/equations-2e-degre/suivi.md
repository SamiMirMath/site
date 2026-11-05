# Chantier « Équations du 2e degré » — suivi

Branche `equations-2e-degre` (depuis `main` b72fe2e), PC (WSL2), `PROCESSUS_PAGES=4`, exécution de nuit (chef d'orchestre et un
sous-agent par partie). Font foi : `CLAUDE.md` > `decisions.md` (§ 13 en tête) > ce fichier > `audit-etape0.md`. Plan approuvé,
consignes de nuit et détail : `journal.md`.

**Invariant de la nuit (§ 13.1)** : après chaque partie, `tests/outils/dump_sorties.py` des outils existants est identique à l'octet
au dump de départ (`/home/sami-ubuntu/nuits/equations-2e-degre/dumps/depart`) ; P5 n'y ajoute que le nouvel outil.

## État des parties

| Partie | Contenu | État | Commit |
|---|---|---|---|
| P0 | Prérequis présents ; fiches ; référence rafraîchie (1 494 tests Python dont 1 xfail, 106 768 sous-tests ; 145 tests de pages, 2 421 sous-tests) ; dump de départ (4 148 sorties, déterministe) | faite (suite verte) | voir `git log` |
| P1 | Correction d'`oracle.racines` ; `moteur/polynomes.py` (déplacements Q2) ; `moteur/second_degre.py`, calcul sans texte | à faire | — |
| P2a | Affichage commun : `tableau_essais`, encadré D29, options de `chaine.py` | à faire | — |
| P2b | Rédaction dans `second_degre` (§ 5), instantanés hors d'`instantanes/` | à faire | — |
| P3 | Saisie : E1, E2, `equations-2e-degre/equations.py` | à faire | — |
| P4a | Formes structurées, sur l'arbre | à faire | — |
| P4b | Degrés ≠ 2 et reste du corpus | à faire | — |
| P5 | L'outil (page, adaptateur, manifeste, registre sans filière, tests) | à faire | — |
| P6 | Filières, carte de l'accueil (après relecture) | hors nuit | — |

## Questions pour l'enseignant

Les 7 points « Ce qui reste contradictoire » du plan (`journal.md`, en tête), chacun validé par l'enseignant le 05.11.2026 (option
par défaut) :

1. S « dans `sortie.resultat` (`.rbox`) » : **`sortie.resultat_lim`** (rendu `.rbox`), dans une carte normale, docstring élargie.
2. « Δ = 20 encadré en entier » : **`\fbox` sur la seule valeur finale** de Δ (« = ⟦20⟧ »).
3. Chaîne sans aucun ⇔ : lignes de Δ, √Δ, x₁, x₂ en **rangées sans lien** (`{lien: "", expr}`) ; validateur inchangé.
4. x⁴ − 16, facteur x² + 4 : **D28** (tableau S-P en échec, puis E9 « Δ < 0 : … »).
5. Tableau S-P de plus de 12 lignes : on compte les **lignes affichées** ; au-delà, la phrase du § 13.5 puis la formule.
6. Déplacement de `_pq` : la **liste de `polynomes.py`** du plan (avec `_const`, ses dépendances, `_pmul_n`, `DEGRE_MAX`).
7. Clavier : **pas de touche √** (dernière rangée `0 , x =`).

Questions nouvelles de la nuit :

8. **P0, test de pages instable** : `tests/pages/test_comportement.py::TestComportement::test_soc04_parametre_f`
   (`outil='ensemble-definition'`) a échoué une fois dans la suite de référence (`#cartes` encore absent : page pas chargée), puis passé
   seul et dans la suite relancée. Traité comme `test_clavier` (relancé seul, suite relancée), sans rien modifier. À surveiller ; détail
   dans `journal.md`, P0.

## À relire par l'enseignant

Rien pour l'instant.

## Exceptions

Aucune pour l'instant (exceptions d'import, `architecture.md` § 5).

## Variations de sous-tests

Lue par `verifier`. Format, une ligne par test : `` - `<identifiant pytest complet>` : <avant> → <après> : <raison> ``.

## Reprise après compactage

- Lire `CLAUDE.md`, ce fichier, puis `journal.md` (plan en tête, section P0 pour les commandes, section de la dernière partie).
- `git log --oneline main..equations-2e-degre` : un commit par partie faite.
- Dossier de travail hors du dépôt : `/home/sami-ubuntu/nuits/equations-2e-degre` (`rapports/<partie>`, `dumps/depart`, `dumps/<partie>`,
  `captures/`, `tmp/`). Si le dump de départ a disparu, le refaire sur le commit de P0 (commande dans `journal.md`, P0).
