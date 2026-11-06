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
| P2b | Rédaction dans `second_degre` (§ 5), instantanés hors d'`instantanes/` | faite (suite verte, dump identique) | voir `git log` |
| P3 | Saisie : E1, E2 (`second_degre.ramener`), `equations-2e-degre/equations.py` (`analyser`), `expr.a_des_decimaux` | faite (suite verte, dump identique) | voir `git log` |
| P4a | Formes structurées, sur l'arbre (produit déjà nul, facteur commun, Id. rem. structurée ; E1.3) | faite (suite verte, dump identique) | voir `git log` |
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
14. **P2b, § 5 précisé** : statuts `non_traite` (temporaire : P2b ne prend que « P = 0 » développée de degré 2 ; les autres formes
    attendent P3, P4a, P4b, en xfail stricts) et `hors_bornes` (§ 13.5) ; champ `message` ; `Etape.segment` (sa chaîne).
15. **P2b, S-P de plus de 12 lignes** : la phrase de choix (D19, « toujours ») puis celle du § 13.5 (« Le trinôme est unitaire, mais
    il y a trop de couples… ») : « unitaire » deux fois. Autre possibilité : la phrase du § 13.5 seule.
16. **P2b, petites options de rédaction** (à juger sur les instantanés) : a < 0 avec a ≠ −1 et pgcd 1 → « Le coefficient de x² est
    négatif (a = −3) : on met d'abord −1 en évidence. » ; ME de −x → « … on met d'abord −x en évidence. » ; Δ avec b = 0 sans le calcul
    « 0 − 16 » ; 2a = 1 écrit (« \frac{-2}{1} = −2 », 0,5x² − 2 = 0) ; variante « formule » non proposée quand elle n'aurait pas de
    formule (3x² − 12x).
17. **P2b, A et B** (question 13) : un seul cadre « ⟦A = 4z, B = 9⟧ », comme D29 l'écrit. **Identité** : la phrase d'Exp-log est
    prête, branchée en P4b (aucune identité ne peut se produire en P2b).

18. **P3, ce que E2 développe** : nombre ou monôme × une parenthèse (« distribution »), deux parenthèses sans autre facteur (« double
    distribution »), carré d'un binôme A ± B écrit avec A sans signe (« Id. rem. (A ± B)² avec A = …, B = … », **sans cadre** : A et B
    se lisent, ils ne se trouvent pas, D29). Tout le reste (2(x + 1)(x + 3), k(x + 2)², (x + 1)³, x²/2, x·3) : « non_traite ». Une
    réduction sans étiquette suit le développement quand des termes de même degré apparaissent (§ 7), aussi sans développement
    (x² + x² = 8 ⇔ 2x² = 8).
19. **P3, structures laissées à P4a** (`second_degre.forme_structuree`, E1.3) : produit ou puissance = 0 ; facteur non monôme commun
    aux deux membres (aussi (x − 1)(x + 2) = x − 1) ; un carré de binôme et des constantes de signe opposé ou nulles, ou deux carrés
    de signes opposés ((x + 1)² = (2x − 3)²). (x + 1)² = −16 se développe. P4a peut revoir la liste.
20. **P3, phrase d'E1** « On ramène d'abord l'équation à la forme … = 0 : » : écrite aussi devant un simple développement dont le
    second membre est déjà 0 (x² − (2x + 3) = 0), si une phrase de choix suit.
21. **P3, saisie** : une puissance d'un nombre à exposant non entier (2^(1/2), 9^(1/2)) reçoit le message « racine », comme √4 ; la
    lettre e est une inconnue comme une autre (e² = 4 se résout en e) ; chaque membre est borné (x⁸ = x⁹ − x⁹ + 1 : message des
    bornes). Arête de plus que le plan, à déclarer en P5 : `equations -> polynomes` (`const`).

22. **P4a, 2.12 h** : A et B en **étiquette en marge** (« Id. rem. A² − B² avec ⟦A = 4, B = 3x + 2⟧ »), comme 2.9 l : E5 n'écrit
    une ligne de texte avant la chaîne que si A doit être justifié (2.9 k, « (car A² = 4(x − 2)²) ») ; le corrigé de 2.12 h écrit une
    ligne de texte sans « car ». Autre possibilité : une ligne de texte dès que A ou B est une somme.
23. **P4a, ligne des parenthèses enlevées** (E5) : écrite seulement si un « − » précède une parenthèse ou si √k ≠ 1, comme le corrigé
    (2.9 l passe de ((x + 1) + 4)((x + 1) − 4) à (x + 5)(x − 3) ; 2.9 k et 2.12 h ont la ligne).
24. **P4a, structures non écrites** : une structure s'applique (E1.3 : on ne développe pas) mais P4a ne l'écrit pas → « non_traite »
    (message clair) : facteurs seulement proportionnels (2(x − 1) = 3(1 − x)(x + 2)) ou écrit développé ((x − 1)(x + 2) = 2x − 2) ;
    √k irrationnel (2(x + 1)² = 8) ; A constant irrationnel (−(x + 1)² + 5 = 0) ; cube ; facteur de degré 2 dans un produit
    ((x² − 1)(x + 2) = 0, 3(x² − 4) = 0 : P4b) ; degré 1 une fois factorisée ((x + 1)² = (x − 3)² : P4b) ; facteur non réduit. Liste :
    `corpus_second_degre.STRUCTURES_NON_ECRITES`. Question 18 revue : 3(x + 1)² = 0 et 4(x − 2)² = 1 sont maintenant résolues
    (structures) ; 2(x + 1)(x + 3) = 5, k(B)² avec des termes en x, (x + 1)³ = 8 + x et 4(x − 2)² = −1 restent « non_traite » (hors
    d'E2, pas une structure). Question 19 réglée par P4a.
25. **P4a, pas de variante « formule »** sur une forme structurée : elle demanderait de développer, ce qu'E1.3 exclut.
26. **P4a, E1.3 « on soustrait le second membre »** : tout reste à gauche, même si le coefficient de tête devient négatif
    ((x + 1)² = (2x − 3)² ⇔ (x + 1)² − (2x − 3)² = 0) ; « 0 = produit » : la ligne « produit = 0 ». L'**énoncé** d'une forme structurée
    a ses produits côte à côte (`second_degre.ecrire_enonce` : « (x − 1)(2 − x)(5 − 3x) », là où expr.tex écrit « (x − 1)(2 − x) ·
    (5 − 3x) ») ; P5 : l'en-tête de la page devrait l'utiliser aussi. Les énoncés de P2b et P3 ne changent pas (« rac{3}{2} · x² »).
27. **P4a, facteur commun** : seulement un facteur **égal** dans les deux membres, restes de degré ≤ 1 ; une droite « −(…) » s'ajoute
    (« g + d = 0 », crochet « [(x + 2) + (x + 3)] ») ; une solution répétée (facteurs proportionnels) n'est écrite qu'une fois
    (« ⇔ x = −1 ») : la ligne finale du produit nul sans doublon (aucune sortie de P2b/P3 ne change).
28. **P4a, produit déjà nul** : la constante et le monôme passent en tête du produit nul (« 3 = 0 » impossible d'abord), même écrits
    après ((x − 1) · 3 = 0) ; un facteur réduit monôme s'écrit en tête (x(x + 2), jamais « (x + 1)(x) ») ; un carré d'une somme est
    réécrit (B)(B) (D24, « toujours »), un cube n'est pas écrit (question 24).

## À relire par l'enseignant

- **P4a, instantanés de la rédaction** : 33 entrées **nouvelles** dans `tests/python/donnees/equations-2e-degre/instantanes.json`
  (formes structurées : 2.9 k, 2.9 l, 2.12 e, 2.12 h, Az 4.1 d et 28 formes « E13 … », « E5 … », « E3 … ») ; **aucune** des 98 entrées
  de P2b et P3 modifiée. Textes rendus des cinq exercices et comparaison au corrigé dans `journal.md`, P4a.

- **P3, instantanés de la rédaction** : 26 entrées **nouvelles** dans `tests/python/donnees/equations-2e-degre/instantanes.json`
  (énoncés à ramener ou à développer : 2.9 d, 2.9 f, 2.10 h, 2.10 j, 2.11 f, 2.11 h, 2.11 j, 2.12 g, (x + 1)(x + 3) = 15 et 17 formes
  « E1 … », « E2 … ») ; **aucune** des 72 entrées de P2b modifiée. Texte rendu de 2.11 h complet (depuis « 4x² + 2x = 56 ») et
  comparaison au § 7 dans `journal.md`, P3.

- **P2b, instantanés de la rédaction** (nouveaux, aucun existant modifié) : `tests/python/donnees/equations-2e-degre/instantanes.json`
  (72 équations, variante « formule » comprise) ; texte rendu de 2.11 h et comparaison au § 7 dans `journal.md`, P2b.

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

- `tests/python/test_exp_log.py::TestVouvoiement::test_aucun_texte_du_fichier_ne_tutoie` : 960 → 955 : P3, les deux littéraux (« __slots__ », « nom ») de `_a_des_decimaux` partent dans `moteur/expr.py` (`a_des_decimaux`, déplacement Q2, réexporté), contrôlés par `test_vocabulaire.TestVouvoiement.test_litteraux_des_moteurs` ; avant, P1 (960 → 957) : les docstrings de `_Hors`, `_racine_carree`, `_racine_entiere_exacte`, `_puissance_rationnelle_exacte` et `_const` partent avec leurs fonctions dans `moteur/polynomes.py` (déplacement Q2), dont les littéraux sont contrôlés par `test_vocabulaire.TestVouvoiement.test_litteraux_des_moteurs` (8812 → 9012).
- `tests/python/test_redaction_second_degre.py::TestNonResolu::test_formes_pas_encore_traitees` : 21 → 6 : P3 puis P4a (par rapport à P2b ; test absent de `tests/reference`), les 10 formes « P3 » puis les 5 formes « P4a » d'`A_VENIR` sont maintenant résolues et contrôlées par `test_a_venir[P3-…]` et `test_a_venir[P4a-…]` (xfail retiré), par l'oracle et par les instantanés.

## Tests renommés

- P4a : `tests/python/test_redaction_second_degre.py::TestNonResolu::test_structures_laissees_a_p4a` →
  `::TestNonResolu::test_structures_sans_developper` (test de P3, absent de `tests/reference`) : les structures ne sont plus
  « laissées à P4a » ; mêmes formes, qui sont maintenant résolues sans développer, plus `STRUCTURES_NON_ECRITES` (« non_traite »).

## Reprise après compactage

- Lire `CLAUDE.md`, ce fichier, puis `journal.md` (plan en tête, section P0 pour les commandes, section de la dernière partie).
- `git log --oneline main..equations-2e-degre` : un commit par partie faite.
- Dossier de travail hors du dépôt : `/home/sami-ubuntu/nuits/equations-2e-degre` (`rapports/<partie>`, `dumps/depart`, `dumps/<partie>`,
  `captures/`, `tmp/`). Si le dump de départ a disparu, le refaire sur le commit de P0 (commande dans `journal.md`, P0).
