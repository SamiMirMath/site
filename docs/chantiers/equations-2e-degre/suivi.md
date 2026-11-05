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
| P1 | Correction d'`oracle.racines` ; `moteur/polynomes.py` (déplacements Q2) ; `moteur/second_degre.py`, calcul sans texte | faite (suite verte, dump identique) | voir `git log` |
| P2a | Affichage commun : `tableau_essais`, encadré D29, options de `chaine.py` | faite (suite verte, dump identique) | voir `git log` |
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

9. **P1, radicande** : un Δ non carré dont numérateur × dénominateur dépasse 10¹² (`second_degre.BORNE_RADICANDE`) donne le
   message des bornes (`HorsBornes`) : `noyau.squarefree` (division d'essai, seule simplification permise, § 13.2) prend 0,1 s à 10¹²
   et ne finirait pas à 10¹⁸ (coefficients de 9 chiffres). N'arrive qu'avec des coefficients d'environ 6 chiffres ou plus.
10. **P1, ME non entière en degré ≥ 3** : § 13.4 (« ME avec des coefficients non entiers : aucune ») est appliqué aussi à xʲ ;
    0,5x³ − 2x = 0 n'a donc aucun chemin (« hors_cours ») au lieu de « ME x, puis la formule ». Option qui affiche le moins ; P4b peut
    l'ouvrir si vous le voulez.
11. **P1, `s_applique` hors du chemin** : S-P et tâtonnement demandent c ≠ 0 (sinon la ME vient avant) ; le tâtonnement demande a ≥ 2
    (D21 : −pgcd d'abord) ; aucune méthode ne s'applique en degré < 2 (on isole x, E13). Pour le futur quiz.

12. **P2a, fond de l'encadré D29** : dans le HTML de KaTeX, le cadre de `\fbox` est dessiné après la valeur et la cachait avec son
    fond. Le fond `--ok-soft` n'est donc posé que si le navigateur connaît `:has` (Safari ≥ 15.4, Chrome ≥ 105, Firefox ≥ 121), qui
    fait passer la valeur au-dessus ; sinon, cadre vert sans fond (valeur toujours visible). Option qui affiche le moins.
13. **P2a, A et B** : D29 écrit « avec ⟦A = 4z, B = 9⟧ » (un seul cadre pour les deux) ; le test de pages suit cette écriture. P2b
    choisit (un cadre, ou un par valeur) ; l'affichage commun convient aux deux.

## À relire par l'enseignant

- **P2a, captures à 390 px** (cartes du test `tests/pages/test_tableau_essais.py`, écrites à la main : affichage commun seulement,
  pas la rédaction de P2b) : `/home/sami-ubuntu/nuits/equations-2e-degre/captures/P2a/cartes-390-clair.png`, `cartes-390-sombre.png`
  (et `cartes-320-clair.png`). À juger : tableau S-P (filets, ligne ✓ encadrée), cadres D29, coupure après « ou ».
- **P2a, règle CSS générale** `.katex .fbox` (bordure `--good`, fond `--ok-soft`) dans `commun/composants.css` : aucune page ni aucun
  moteur n'écrit `\fbox` ou `\boxed` aujourd'hui (vérifié), donc aucun rendu existant ne change.
- P2a ne change aucun instantané, aucune référence de page ni aucune sortie (dump identique à l'octet).

- **P1, oracle renforcé** (Q11) : `tests/python/oracle.py::racines` retire d'abord les termes constants nuls (racine 0 de multiplicité
  exacte) ; `[7, -19, 0]` faisait refuser l'oracle. Test `test_oracle.TestCasDemandes.test_racine_nulle_retiree_d_abord`.
- **P1, dette nommée** : `docs/architecture.md` § 5, « 4 copies de k√m/d » (chantier « nombres partout ») ; § 1 nomme `polynomes`.
- P1 ne change aucun instantané ni aucune sortie (dump identique à l'octet).

## Exceptions

Aucune pour l'instant (exceptions d'import, `architecture.md` § 5).

## Variations de sous-tests

Lue par `verifier`. Format, une ligne par test : `` - `<identifiant pytest complet>` : <avant> → <après> : <raison> ``.

- `tests/python/test_exp_log.py::TestVouvoiement::test_aucun_texte_du_fichier_ne_tutoie` : 960 → 957 : P1, les docstrings de `_Hors`, `_racine_carree`, `_racine_entiere_exacte`, `_puissance_rationnelle_exacte` et `_const` partent avec leurs fonctions dans `moteur/polynomes.py` (déplacement Q2), dont les littéraux sont contrôlés par `test_vocabulaire.TestVouvoiement.test_litteraux_des_moteurs` (8812 → 9012).

## Reprise après compactage

- Lire `CLAUDE.md`, ce fichier, puis `journal.md` (plan en tête, section P0 pour les commandes, section de la dernière partie).
- `git log --oneline main..equations-2e-degre` : un commit par partie faite.
- Dossier de travail hors du dépôt : `/home/sami-ubuntu/nuits/equations-2e-degre` (`rapports/<partie>`, `dumps/depart`, `dumps/<partie>`,
  `captures/`, `tmp/`). Si le dump de départ a disparu, le refaire sur le commit de P0 (commande dans `journal.md`, P0).
