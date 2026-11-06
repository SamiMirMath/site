# Chantier « Équations du 2e degré » — suivi

Branche `equations-2e-degre` (depuis `main` b72fe2e), PC (WSL2), `PROCESSUS_PAGES=4`, exécution de nuit (chef d'orchestre et un
sous-agent par partie). Font foi : `CLAUDE.md` > `decisions.md` (§ 13 en tête) > ce fichier > `audit-etape0.md`. Plan approuvé,
consignes de nuit et détail : `journal.md`.

**Invariant de la nuit (§ 13.1)** : après chaque partie, `tests/outils/dump_sorties.py` des outils existants est identique à l'octet
au dump de départ (`/home/sami-ubuntu/nuits/equations-2e-degre/dumps/depart`) ; P5 n'y ajoute que le nouvel outil.

## Résumé (06.11.2026, PC)

Huit parties, huit commits, toutes acceptées par le contrôle allégé (`verifier` ACCEPTÉ, `rapide --depuis HEAD~1` vert) ; dump des
outils existants identique à l'octet au départ après chaque partie (4 148 sorties) ; aucun instantané ni aucune référence de page
d'un outil existant modifiés (détail : `journal.md`, « Contrôles du chef d'orchestre » et « Suite d'avant commit » de chaque partie).

| Partie | Contenu | Commit | Suite d'avant commit | Tests ajoutés |
|---|---|---|---|---|
| P0 | fiches, référence rafraîchie, dump de départ | `0fd0060` | 6 min 40 | — |
| P1 | `oracle.racines` (racine nulle), brique `polynomes`, `second_degre` (calcul sans texte) | `5f21ac0` | 6 min 44 | 40 Python |
| P2a | affichage commun : `tableau_essais`, encadré D29, `bloc_rangees`, coupure après « ou » | `5b9254c` | 7 min 02 | 14 Python, 6 de pages |
| P2b | rédaction dans `second_degre` (`resoudre_equation`, étapes du § 5) | `a52b58a` | 7 min 05 | 59 Python (dont 22 xfail stricts P3/P4a/P4b) |
| P3 | saisie (`equations.analyser`), E1 et E2 (ramener, développer), `expr.a_des_decimaux` | `8e838be` | 7 min 00 | 34 Python (10 xfail « P3 » passent) |
| P4a | formes structurées sur l'arbre (produit déjà nul, facteur commun, Id. rem. structurée, E1.3) | `06f3daf` | 7 min 12 | 12 Python, 1 renommé (5 xfail « P4a » passent) |
| P4b | degrés ≠ 2 (ME de xᵏ, E9, x⁴ − 16), degré 1, identité, messages définitifs | `88ea64e` | 7 min 21 | 13 Python, 1 renommé (7 xfail « P4b » passent) |
| P5 | l'outil (page, `resoudre_eq`, manifeste, registre sans filière) ; message « forme non traitée » (question 29) | `f65131b` | 7 min 10 | 6 Python (3 retirés), 3 de pages |
| R1 | une carte par étape (question 36) | `ee52a47` | 7 min (Python 100 s, pages 335 s) | 3 Python, 1 de pages |
| R2 | développer d'abord, fractions supprimées d'abord (question 29) | `88f44ee` | 7 min (Python 95 s, pages 334 s) | 8 Python (1 renommé), 1 de pages |
| R3 | les deux boutons pour comparer (questions 37 et 25) | commit « R3 » de la branche | voir `journal.md`, R3 | 6 Python (1 renommé), 1 de pages |
| P6 | filières 1C, 1Ms, 1Mr, 2C au registre ; 4 cartes à l'accueil (16 → 20 liens) ; `test_acc03` d'origine (question 39) | commit « P6 » de la branche | voir `journal.md`, P6 | aucun (2 tests de pages mis à jour) |

Suite finale (chef d'orchestre, sur `f65131b`, `PROCESSUS_PAGES=4`, `…/rapports/FIN`) : code 0 ; Python 1 666 passés + 1 xfail
(celui d'avant le chantier), 128 686 sous-tests (113 s) ; pages 154 passés, 2 520 sous-tests (332 s) ; 7 min 28 de mur ; `verifier`
ACCEPTÉ ; `comparer_listes tests/reference FIN` : seulement des ajouts (173 tests Python, 9 de pages), des hausses de sous-tests et
la baisse justifiée de `test_exp_log::…::test_aucun_texte_du_fichier_ne_tutoie` (960 → 955). Même suite avec `MEMO=0`
(`…/rapports/FIN-memo0`) : code 0, `verifier` ACCEPTÉ, listes identiques nom par nom (7 min 54). Dump final identique à celui de P5 ;
par rapport au départ, seuls `apercu/equations-2e-degre.txt`, `resoudre/equations-2e-degre.txt` et leurs deux lignes d'`index.txt`
s'ajoutent. Aucun xfail du chantier ne reste.

**Texte rendu de l'exemple cible 2.11 h** (`resoudre_eq.resoudre("4x^2+2x=56")`, sur `f65131b`, carte « Résolution », chemin du
cours ; `gauche` : membre de gauche de la 1re rangée), puis S :

    gauche 4x^{2} + 2x = 56   \iff  4x^{2} + 2x - 56 = 0
                              \iff  2(2x^{2} + x - 28) = 0                                          ME
    texte  Le trinôme \(2x^{2} + x - 28\) n'est pas unitaire : tâtonnement.
    texte  \(\fbox{$x = -4$}\) est solution de \(2x^{2} + x - 28 = 0\), car \(2 \cdot (-4)^{2} - 4 - 28 = 32 - 4 - 28 = 0\).
    texte  Donc \(2x^{2} + x - 28 = (x + 4)(2x + \triangle)\) avec \(4 \cdot \triangle = -28\), donc \(\fbox{$\triangle = -7$}\).
                              \iff  2(x + 4)(2x - 7) = 0
                              \iff  {\underbrace{2 = 0}_{\text{impossible}}} \text{ ou } \allowbreak {x + 4 = 0} \text{ ou } \allowbreak {2x - 7 = 0}
                                                                                                    produit nul
                              \iff  {x = -4} \text{ ou } \allowbreak {x = \frac{7}{2}}
    resultat_lim  S = \{-4\,;\,\frac{7}{2}\}

Variante « Par la formule » proposée (Δ = 4 + 896 = ⟦900⟧, √Δ = 30, x₁ = −4, x₂ = 7/2). Comparaison au § 7 : mêmes lignes, même
ordre et mêmes étapes (ramener · factoriser (ME) · factoriser (TATONNEMENT, r = −4, △ = −7) · produit_nul) ; écarts voulus :
étiquette « produit nul » (D5), x = −4 et △ = −7 encadrés (D29), parenthèses de la ME ordinaires (rendu seulement). Texte identique
à celui de P3 (`journal.md`, P3, « Texte rendu de 2.11 h »).

**À relire par l'enseignant** (détail : section « À relire » ci-dessous et `journal.md`) :
- **P6** : l'accueil (4 cartes « Équations du 2e degré » : I C, Ms, Mr après Factorisation ; II C après Programmation linéaire),
  description épelée « Mise en évidence, … » ; capture `/home/sami-ubuntu/nuits/equations-2e-degre/captures/P6/` ; questions 43, 44.
- **R3** : 37 entrées gagnent la variante « Par la formule » (formes structurées, c = 0), 8 la perdent (degré ≥ 3) ; chemin du cours
  inchangé pour les 225 entrées ; captures `/home/sami-ubuntu/nuits/equations-2e-degre/captures/R3/` ; question 42.
- **R2** : textes de 2(x + 1)² = 8, x²/2 = 1 + x, Az 4.1 b et h (`journal.md`, R2) ; les 16 instantanés changés (tous « forme non
  traitée » avant) et les 21 nouveaux ; captures `/home/sami-ubuntu/nuits/equations-2e-degre/captures/R2/` ; question 41.
- **R1** : captures `/home/sami-ubuntu/nuits/equations-2e-degre/captures/R1/` ; tous les instantanés du nouvel outil, découpage en
  cartes ; question 40 (étape sans ligne de chaîne).
- Captures à 390 px : `/home/sami-ubuntu/nuits/equations-2e-degre/captures/P5/` (`2.11-h-390-clair.png`, `2.11-h-390-sombre.png`,
  `2.10-a-390-clair.png`, `javet-2.17-c-390-clair.png`, `2.12-e-390-clair.png`, `x+1-x+3-egal-15-390-clair.png`) et
  `/home/sami-ubuntu/nuits/equations-2e-degre/captures/P2a/` (`cartes-390-clair.png`, `cartes-390-sombre.png`, `cartes-320-clair.png`)
  (`journal.md`, P5, « Captures à 390 px » ; P2a).
- Instantanés nouveaux : `tests/python/instantanes/equations-2e-degre.json` (rédaction, 204 entrées) et
  `tests/python/instantanes/resoudre/equations-2e-degre.json` (sorties de la page) ; aucun instantané d'un outil existant modifié ;
  les 11 entrées changées en P5 par la question 29 (`hors_cours` → `forme_non_traitee`), liste dans « À relire », P5.
- ⏸ ligne du tâtonnement en échec (decisions.md § 10, E7 : « On teste les diviseurs de 3 (±1, ±3) : aucun n'est solution. On utilise
  la formule. », 2.12 b, Javet 2.17 d) : à juger à l'écran. Coupure de la ligne de Δ de Javet 2.17 c dans « 4 · 1 · (−2) » à 390 px
  (rien ne déborde ; `journal.md`, P5).
- Renforcements et adaptations : oracle (`racines`, racine nulle retirée d'abord, P1) ; dette « 4 copies de k√m/d » (chantier
  « nombres partout ») dans `docs/architecture.md` § 5 ; `test_acc03` adapté (un outil sans filière n'a pas de carte, option A) et
  butée de `test_accueil` à 16 liens / 8 outils (P5), puis 20 / 8 et `test_acc03` revenu au test d'origine (P6) ; 19 arêtes d'import nouvelles dans `test_imports` (`polynomes`, `second_degre`,
  `equations`, `resoudre_eq`, `exp_log(_m) -> polynomes`), aucune exception (aucun import entre outils).
- Les 7 points « Ce qui reste contradictoire » du plan, pris avec leur option par défaut et validés (questions 1 à 7 ci-dessous).

**Questions pour l'enseignant** (texte complet : section « Questions pour l'enseignant » ci-dessous), triées :
- **29** « hors du cours » faux pour des formes du cours que l'outil n'écrit pas : décision du chef d'orchestre en P5 (rien de faux),
  « Cette forme d'équation n'est pas traitée par l'outil. », statut `forme_non_traitee` ; autres possibilités : étendre E2, écrire
  les structures non écrites, un autre texte.
- **8** instabilité de chargement de `test_soc04_parametre_f` en P0, acceptée par le chef comme celle de `test_clavier`.
- **40** (R1) étape sans ligne de chaîne (tentative en échec, phrase de choix seule, « Δ < 0 ») : une carte de textes à elle ; badges.
- **41** (R2) choix de rédaction du développement pas à pas et de la suppression des fractions ; formes encore non écrites.
- **42** (R3) choix de la variante : pas pour un monôme ax² = 0 ; solutions différentes → « ne conclut pas » ; une forme structurée
  développée comme en R2 ; plus de ME de xʲ (aucune variante en degré ≥ 3).
- 36 **tranché : une carte par étape** (R1, fait) ; 29 **tranché : développer d'abord, fractions supprimées d'abord** (R2, fait) ; 37 et 25
  **tranchés : les deux boutons pour comparer** (R3, fait) ; autres questions : options par défaut gardées (proposé le 06.11.2026, sans objection de l'enseignant) ; 30 « bicarrée » aussi après une ME ; 31 ordre d'écriture de x⁴ − 16.
- 9 radicande > 10¹² : message des bornes ; 10 ME non entière en degré ≥ 3 (0,5x³ − 2x) ; 11 `s_applique` hors du chemin (quiz).
- 12 fond de l'encadré D29 seulement avec `:has` ; 13 et 17 un seul cadre « A = 4z, B = 9 ».
- 15 « unitaire » deux fois (S-P de plus de 12 lignes) ; 16 petites options de rédaction de P2b ; 32 petites phrases de P4b.
- 18 ce que E2 développe ; 20 phrase d'E1 devant un simple développement ; 21 saisie (2^(1/2), lettre e, bornes par membre).
- 22 A et B de 2.12 h en marge ; 23 ligne des parenthèses enlevées ; 24 structures non écrites ; 25 pas de variante sur une forme
  structurée ; 26 E1.3 « on soustrait le second membre » ; 27 facteur commun ; 28 produit déjà nul (constante en tête).
- 33 identité et égalité fausse ; 34 degré 1 toujours ramené ; 35 facteur de degré 2 dans un produit déjà nul.
- 37 libellés de la variante E12 ; 38 aperçu (syntaxe seulement) ; 39 `test_acc03` et outil sans filière (**réglée par P6**).
- **43** (P6) place de la carte en 2C (après Programmation linéaire) ; **44** (P6) liens des cartes de l'accueil hauts de 19 px
  (toutes les cartes, avant P6 aussi).
- Pour mémoire (réglées pendant la nuit) : 14 (statut `non_traite`, disparu en P4b), 19 (réglée par P4a).

Exceptions (`architecture.md`) : aucune. Variations de sous-tests : quatre lignes, section « Variations de sous-tests » (lue par
`verifier`). Tests renommés ou retirés : cinq (P4a, P4b, P5, R2, R3), section « Tests renommés ».

Fusion, par l'enseignant, une commande à la fois : `git checkout main && git merge --no-ff --no-edit equations-2e-degre`, puis
`git push`, puis `git branch -d equations-2e-degre`.

## État des parties

| Partie | Contenu | État | Commit |
|---|---|---|---|
| P0 | Prérequis présents ; fiches ; référence rafraîchie (1 494 tests Python dont 1 xfail, 106 768 sous-tests ; 145 tests de pages, 2 421 sous-tests) ; dump de départ (4 148 sorties, déterministe) | faite (suite verte) | `0fd0060` |
| P1 | Correction d'`oracle.racines` ; `moteur/polynomes.py` (déplacements Q2) ; `moteur/second_degre.py`, calcul sans texte | faite (suite verte, dump identique) | `5f21ac0` |
| P2a | Affichage commun : `tableau_essais`, encadré D29, options de `chaine.py` | faite (suite verte, dump identique) | `5b9254c` |
| P2b | Rédaction dans `second_degre` (§ 5), instantanés hors d'`instantanes/` | faite (suite verte, dump identique) | `a52b58a` |
| P3 | Saisie : E1, E2 (`second_degre.ramener`), `equations-2e-degre/equations.py` (`analyser`), `expr.a_des_decimaux` | faite (suite verte, dump identique) | `8e838be` |
| P4a | Formes structurées, sur l'arbre (produit déjà nul, facteur commun, Id. rem. structurée ; E1.3) | faite (suite verte, dump identique) | `06f3daf` |
| P4b | Degrés ≠ 2 (ME de xᵏ, Id. rem. de A = x², E9), degré 1, identité, messages définitifs (bicarrée, hors du cours) ; plus de `non_traite` | faite (suite verte, dump identique) | `88ea64e` |
| P5 | L'outil (page, adaptateur, manifeste, registre sans filière, tests) ; message vrai « forme non traitée » (question 29) | faite (suite verte, dump : seuls ajouts du nouvel outil) | `f65131b` |
| R1 | Une carte par étape (question 36) ; invariant du § 5 adapté | faite (suite verte, dump : outils existants identiques au départ) | `ee52a47` |
| R2 | Développer d'abord, fractions supprimées d'abord (question 29) | faite (suite verte, dump : outils existants identiques au départ) | `88f44ee` |
| R3 | Les deux boutons pour comparer (questions 37 et 25) | faite (suite verte, dump : outils existants identiques au départ) | commit « R3 » |
| P6 | Filières 1C, 1Ms, 1Mr, 2C au registre, cartes de l'accueil, butée de `test_accueil` (20, 8), `test_acc03` d'origine | faite (suite verte, dump identique à R3) | commit « P6 » |

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
    formule (3x² − 12x ; revu en R3 : proposée, la formule directe).
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
    **Revue en R3** (question 37, tranchée) : la variante développe la forme structurée, puis la formule ; le chemin du cours, lui,
    ne développe toujours pas.
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

29. **P4b, « hors du cours » par défaut** (consigne de la nuit) : ce que l'outil n'écrit pas reçoit « Cette équation ne se résout pas
    avec les méthodes du cours. » : E2 hors de ce qu'il développe (2(x + 1)(x + 3) = 5, x²/2 = 1 + x, (x + 1)³ = 8 + x, **Az 4.1 b et
    h**, à fractions) et `STRUCTURES_NON_ECRITES` (2(x + 1)² = 8, (x² − 1)² = 0…). **Inexact pour elles** (elles sont du cours) :
    à trancher avant P6 (message propre, p. ex. « Cette forme d'équation n'est pas traitée par l'outil. », ou E2 étendu).
    **Décision du chef d'orchestre, faite en P5** (CLAUDE.md, rien de faux, prime) : statut `forme_non_traitee`, « Cette forme
    d'équation n'est pas traitée par l'outil. », pour ces formes et pour tout degré ≥ 3 douteux ; « hors du cours » seulement s'il est
    vrai (`second_degre.hors_du_cours` : degré ≥ 3, coefficients entiers, pas bicarrée, au plus une ME de constante sur le chemin, reste
    pas bicarré : x³ = x + 1, Az 4.1 d développé). Devenus « forme non traitée » parce que douteux : 2x⁴ − 10x² + 8 (ME puis bicarrée),
    x⁶ − 64 (Id. rem. puis x³ ± 8), 0,5x³ − 2x (question 10). **Reste ouvert** : étendre E2 (2(x + 1)(x + 3), x²/2, fractions d'Az 4.1
    b et h), écrire les structures non écrites, un autre texte, ou « bicarrée » après une ME (question 30).
    **Tranché par l'enseignant (06.11.2026) : développer d'abord** toute forme polynomiale qui n'est pas une forme que l'outil
    factorise directement (A² − B², produit déjà nul, facteur commun) : 2(x + 1)² = 8, 2(x + 1)(x + 3) = 5, (x + 1)³ = 8 + x…, puis le
    chemin habituel ; E2 étendu. Pas de deuxième bouton. **Dénominateur numérique (tranché le 06.11.2026)** : multiplier d'abord
    par le dénominateur (x²/2 = 1 + x ⇔ x² = 2 + 2x) : « on supprime les fractions de préférence ». **Fait en R2** (question 41).
30. **P4b, bicarrée à la lettre** (§ 13.4) : x⁴ − 5x² + 4, x⁴ + 4, x⁴ − 5 → « bicarrée » ; 2x⁴ − 10x² + 8 et x⁵ − 5x³ + 4x (une ME
    s'applique) → « hors du cours ». Autre possibilité : « bicarrée » aussi après une ME.
31. **P4b, ordre d'écriture** (x⁴ − 16) : l'Id. rem. de x² − 4 d'abord, puis le tableau S-P de x² + 4 en échec, juste avant le
    produit nul et Δ (E9, comme Javet 2.17 c). Autre possibilité : l'ordre du calcul (le S-P en échec juste après la 1re Id. rem.).
32. **P4b, petites phrases** : ME de a < 0 en degré ≠ 2, « Le coefficient de x³ est négatif : on met d'abord −x en évidence. » (sans
    « trinôme » ni « a = ») ; formule d'emblée sur un facteur non entier, « Les coefficients du trinôme x² + 1/2 ne sont pas entiers :
    on utilise la formule. » ; deux trinômes par la formule (4x⁴ − 9) : leurs lignes de Δ dans l'ordre du produit, sans en-tête.
33. **P4b, identité et égalité fausse** : la ligne des constantes de chaque membre (« 1 = 1 », « 1 = 2 », « −4 = −4 », comme
    Exp-log), pas « 0 = 0 » ramené ; la phrase termine la dernière étape (pas d'étape à elle) ; forme structurée : « g − d = 0 », puis
    « 0 = 0 ».
34. **P4b, degré 1** : toujours ramené (§ 13.4 à la lettre : x = 3 ⇔ x − 3 = 0 ⇔ x = 3) ; la ligne ramenée « x = 0 » suffit (Az 4.1 a) ;
    « x = 0 » saisi seul : une seule ligne. Une fois factorisée : le facteur constant en tête, « 4(2x − 2) = 0 », « −3(x − 1) = 0 ».
35. **P4b, facteur de degré 2 dans un produit déjà nul** : factorisé par le cours sur le produit écrit ((x² − 1)(x + 2) = 0 ⇔
    (x + 1)(x − 1)(x + 2) = 0) ; avec un carré dans le même produit, ou (x² − 1)² = 0 : « hors du cours ». Une autre lettre que
    l'inconnue (refusée par la saisie avant) : `ValueError` dans `resoudre_equation`.

36. **P5, une seule carte** : la page montre une carte « Résolution » (la chaîne entière : la concaténation des lignes de toutes les
    étapes est la chaîne affichée, § 5), donc « Étape 1 / 1 » et « Étape suivante » grisé. Autre possibilité : une carte par étape
    (la chaîne coupée en morceaux, ⇔ alignés carte par carte), à décider avec l'onglet « S'entraîner ».
    **Tranché par l'enseignant (06.11.2026) : une carte par étape** (« ça rend plus clair la résolution »), dévoilées une à une par
    « Étape suivante » comme dans les autres outils ; la suite des cartes redonne la chaîne entière (invariant du § 5 adapté).
    **Fait en R1** (question 40).
37. **P5, libellés de la variante E12** : « Méthodes du cours » (défaut) et « Par la formule » (D2) ; le choix est gardé d'une saisie
    à l'autre (comportement commun d'`outil.js`, comme Exp-log). Pas de variante sur une forme structurée (question 25).
    **Tranché par l'enseignant (06.11.2026)** : libellés gardés ; **les deux boutons pour comparer** (« ainsi ils peuvent comparer ») :
    la variante « Par la formule » est proposée pour toute équation qui se ramène à un trinôme du 2e degré, formes structurées
    comprises (question 25) et 3x² − 12x = 0 (formule directe, c = 0) ; un seul bouton seulement quand le chemin du cours passe déjà
    par la formule ; aucun en degré 1 ou ≥ 3. Remplace la règle E12 de decisions.md (« seulement si le chemin du cours n'utilise pas
    la formule », ME de la puissance de x indispensable) pour ces cas ; decisions.md non modifié. **Fait en R3** (question 42).
38. **P5, aperçu** : seulement la lecture (syntaxe) ; « x+1 » s'affiche sans erreur (le message « pas de = » vient au calcul) ; une
    équation que l'analyse accepte est écrite comme l'énoncé (`ecrire_enonce`). Erreurs de l'analyse (plusieurs lettres, 2^x…) :
    seulement au calcul, comme Exp-log.
39. **P5, accueil** : `test_acc03` (page) compare les liens de l'accueil aux chemins des outils **qui ont une filière** (option A :
    l'outil est au registre sans carte) ; en P6, avec ses filières, il y revient de lui-même. **Réglée par P6** : `test_acc03`
    revenu au test d'origine (les liens de l'accueil = tous les chemins du registre).

40. **R1, une carte par étape** (question 36) : « Étape k » avec un badge court, comme Exp-log et Factorisation (noms du rappel de la
    page) : Ramener à 0, Développer, Isoler x, Mise en évidence, Identité remarquable, Somme-Produit, Tâtonnement, Formule,
    Discriminant, Valeurs de x, Produit nul ; puis « Solution » (carte normale, § 13.3). Une carte commence par l'équation d'arrivée
    de la précédente en membre de gauche, sauf si elle commence par une ligne de Δ (pas de répétition, § 13.3). **Étape sans ligne de
    chaîne** (tentative en échec du S-P ou du tâtonnement, phrase de choix seule de la formule, « Δ < 0 : … ») : une carte à elle,
    faite de blocs texte et tableau (une chaîne sans ligne ⇔ est refusée par `sortie.valider`, A4 interdit le HTML) ; ses textes
    sont un peu plus grands que ceux d'une chaîne (capture de Javet 2.17 c, Étape 2). Autre possibilité : la joindre à la carte
    suivante. La seule étape vide (formule choisie d'emblée, variante) rejoint la carte du discriminant. E9 : la ligne finale
    « ⇔ x = … » de « Valeurs de x » suit les lignes de Δ, sans membre de gauche, comme dans la chaîne entière.

41. **R2, développer d'abord et fractions supprimées d'abord** (question 29) ; choix pris (options qui affichent le moins, ou les plus
    proches d'E2) :
    - **étiquette des fractions** : « on multiplie par 12 » (celle d'`ensemble_def`, proche d'Exp-log « on multiplie les deux membres
      par le dénominateur » ; la référence n'a pas d'exemple rédigé). Chaque terme est multiplié et simplifié sur la même ligne
      (Az 4.1 b : 2(3x − 2) = 3(x + 1) + 60), puis E2. Seule une division qui a l'inconnue au numérateur déclenche la multiplication ;
      une constante fractionnaire seule ((1/2)x², x² = 1/4) garde D22 (instantanés inchangés). Après la suppression des fractions,
      aucune forme structurée : (x + 1)²/4 = 1 ⇔ (x + 1)² = 4 est développée.
    - **ordre du développement** : les produits de parenthèses d'abord, le coefficient distribué en dernier
      (2(x + 1)(x + 3) ⇔ 2(x² + 3x + x + 3) ⇔ 2(x² + 4x + 3) ⇔ 2x² + 8x + 6) ; la réduction dans la parenthèse a sa ligne, sans
      étiquette (comme E2). Plus de deux parenthèses : la double distribution des deux premières, puis de même.
    - **cube et puissances** : (x + 1)³ ⇔ (x + 1)²(x + 1) (ligne sans étiquette, comme D24), puis l'Id. rem., puis la double
      distribution ; carré d'une somme qui n'est pas un binôme d'E2 ((x² + x + 1)²) : (B)(B), puis la double distribution. Un produit
      de monômes écrit (x · 3) se lit comme le monôme : « x · 3 + x² = 1 ⇔ x² + 3x − 1 = 0 ».
    - **produit déjà nul** : un cube y est réécrit (B)(B)(B) comme un carré (D24, (x + 1)³ = 0) ; un carré à côté d'un trinôme
      ((x + 1)²(x² − 4) = 0) reste écrit jusqu'au produit nul, où il est réécrit (B)(B) (question 35 revue).
    - **messages** : une forme structurée non écrite qui, développée, finit en « hors du cours » ou « bicarrée » garde « Cette forme
      d'équation n'est pas traitée par l'outil. » (un produit nul direct pourrait la résoudre). Un degré ≥ 3 développé sans ME ni
      Id. rem. reçoit « hors du cours » ((x + 1)³ = 8 + x, (x² + x + 1)² = x), comme Az 4.1 d développé. **Encore non écrites**
      (message vrai) : fraction dans une parenthèse ou une puissance (2(x + 1/2) = x²/2, (x/2 + 1)² = 1), parenthèses imbriquées,
      (x² − 3)² = 1, (x − 1)(x + 2)(x + 3) = 5(x − 1), et les degrés ≥ 3 douteux des questions 10 et 30 (0,5x³ − 2x, 2x⁴ − 10x² + 8,
      x⁶ − 64).

42. **R3, les deux boutons pour comparer** (questions 37 et 25) ; choix pris :
    - **règle** : variante « Par la formule » si et seulement si l'équation résolue se ramène à un trinôme de degré 2 (P = gauche −
      droite) et qu'aucune étape du cours n'utilise la formule ; **pas pour un monôme** ax² = 0 (3x² = 0 ⇔ x = 0 : rien à comparer,
      Δ = 0 − 0 ; option qui affiche le moins) ; aucune en degré 1, en degré ≥ 3 (les 8 variantes « ME de x, puis la formule » de
      degré ≥ 3 disparaissent, dont 2.12 c) ni pour un message.
    - **rédaction** : on ramène et développe jusqu'à ax² + bx + c = 0 avec les lignes de E1, E2 et R2 (celles d'une forme développée),
      puis Δ et les valeurs de x ; plus de mise en évidence de la puissance de x (c = 0 : la formule directe, « Δ = (−12)² − 4 · 3 · 0
      = ⟦144⟧ ») ; a < 0 comme avant (pas de −1 en évidence, x₁ avec −√Δ, S croissant). Une forme structurée est développée comme en
      R2 (2.12 e : double distribution des deux membres, puis E1 ramène du côté où x² reste positif, 2x² − x − 1 = 0, alors que le
      cours ramène à gauche). Autre possibilité : ramener d'abord tout à gauche, puis développer.
    - **garde-fou** : la variante n'est proposée que si elle conclut et a exactement les solutions du cours ; des solutions
      différentes donnent « Le calcul ne permet pas de conclure… » pour toute l'équation (jamais rencontré).

43. **P6, ordre des cartes** : l'ordre d'une cellule est celui du registre (ACC-01) ; l'entrée reste la dernière du registre. Année I :
    après Factorisation (les méthodes de résolution s'appuient sur la factorisation) ; année II, C : après Programmation linéaire
    (la carte existante garde sa place ; l'ordre du programme de 2C n'est pas écrit dans le dépôt). Autre possibilité : placer
    l'entrée avant le simplexe dans le registre (Équations en tête de la 2C, Factorisation restant avant en année I).

44. **P6, cibles tactiles de l'accueil** : le lien d'une carte est le titre seul (`.tool a`, en ligne : 19 px de haut à 390 px), la
    carte fait 104 px (106 px pour Équations du 2e degré, à cause du « e » en exposant) ; c'est le cas de toutes les cartes depuis
    T22, P6 n'y change rien (option qui affiche le moins). Autre possibilité : rendre toute la carte cliquable (composant commun),
    dans un chantier de l'accueil.

## À relire par l'enseignant

- **P6, accueil** : `commun/registre.json` (`"filieres": {"1": ["C", "Ms", "Mr"], "2": ["C"]}`, aucun `parametres` ; description
  « ME, … » devenue « Mise en évidence, identités remarquables, Somme-Produit, tâtonnement et formule, étape par étape. », comme
  la carte Factorisation, ME n'étant pas défini à l'accueil) ; `index.html` : 4 cartes (titre « Équations du 2<sup>e</sup> degré »).
  Tests changés : `tests/pages/test_accueil.py` (butée (16, 8) → (20, 8), nom gardé ; `test_acc03` d'origine ; `test_acc04` : Ms
  1 + 1 + 4 → 2 + 1 + 4, C 1 + 1 + 1 → 2 + 2 + 1). Aucun instantané, aucune référence de page, aucun `test_largeurs` ne porte
  sur l'accueil (vérifié) : rien d'autre à mettre à jour. Captures à 390 px (clair) :
  `/home/sami-ubuntu/nuits/equations-2e-degre/captures/P6/accueil-tous-390-clair.png`, `accueil-C-390-clair.png`,
  `accueil-Ms-390-clair.png` ; rien ne déborde à 320, 360 et 390 px ; questions 43 et 44.

- **R3, les deux boutons pour comparer** (question 42) : instantanés du nouvel outil (`tests/python/instantanes/equations-2e-degre.json`,
  `tests/python/instantanes/resoudre/equations-2e-degre.json`) : 225 entrées, **chemin du cours identique pour toutes** (vérifié entrée
  par entrée) ; **37 gagnent la variante** « Par la formule » (33 formes structurées, dont 2.9 k, 2.9 l, 2.12 e, 2.12 h ; 4 formes
  développées avec c = 0, dont 3x² − 12x = 0) ; **8 la perdent** (degré ≥ 3 : x³ − x = 0 (2.12 c), x³ = 4x, 2x³ − 4x² + 2x = 0…) ;
  73 gardent la même ; 107 sans variante, identiques. Références de pages : 5 changées (boutons et variante seulement : 2.9 k, 2.9 l,
  2.12 e, 2.12 h gagnent le sélecteur, 2.12 c le perd). Liste et textes rendus dans `journal.md`, R3. Captures à 390 px :
  `/home/sami-ubuntu/nuits/equations-2e-degre/captures/R3/` (`2.12-e-par-la-formule-tout-390-clair.png`,
  `3x2-moins-12x-par-la-formule-tout-390-clair.png`).

- **R2, développer d'abord, fractions supprimées d'abord** (question 41) : instantanés du nouvel outil
  (`tests/python/instantanes/equations-2e-degre.json`, `tests/python/instantanes/resoudre/equations-2e-degre.json`) : **188 entrées
  identiques**, **16 changées** (toutes « forme non traitée » avant : 14 résolues, dont Az 4.1 b et h, x²/2 = 1 + x, 2(x + 1)² = 8,
  2(x + 1)(x + 3) = 5, les 8 structures non écrites ; 2 « hors du cours », (x + 1)³ = 8 + x et (x² + x + 1)² = x), **21 nouvelles** ;
  liste et textes rendus dans `journal.md`, R2. Références de pages : 57 identiques. Captures à 390 px :
  `/home/sami-ubuntu/nuits/equations-2e-degre/captures/R2/` (x²/2 = 1 + x, 2(x + 1)² = 8, Az 4.1 h).

- **R1, une carte par étape** : captures à 390 px (clair) dans `/home/sami-ubuntu/nuits/equations-2e-degre/captures/R1/` :
  `2.11-h-tout-390-clair.png`, `2.11-h-apres-un-clic-390-clair.png`, `2.10-a-tout-390-clair.png`, `javet-2.17-c-tout-390-clair.png`.
  Instantanés : **tous les instantanés du nouvel outil, découpage en cartes** (`tests/python/instantanes/equations-2e-degre.json`,
  `tests/python/instantanes/resoudre/equations-2e-degre.json`, `tests/pages/references/equations-2e-degre.json`) : mêmes lignes,
  coupées aux étapes (recoupé entrée par entrée, 241 résolutions) ; exemples avant / après dans `journal.md`, R1. Question 40.

- **P5, l'outil** : page `equations-2e-degre/index.html` (accroche, aide de saisie, rappel E15), captures à 390 px dans
  `/home/sami-ubuntu/nuits/equations-2e-degre/captures/P5/` : `2.11-h-390-clair.png`, `2.11-h-390-sombre.png`, `2.10-a-390-clair.png`,
  `javet-2.17-c-390-clair.png`, `2.12-e-390-clair.png`, `x+1-x+3-egal-15-390-clair.png`. À juger : ligne de Δ de Javet 2.17 c coupée
  dans « 4 · 1 · (−2) » à 390 px (rien ne déborde) ; une seule carte (question 36).
- **P5, instantanés** : le JSON provisoire devient `tests/python/instantanes/equations-2e-degre.json` (clé = la saisie, lue par
  `equations.analyser` comme la page) ; **11 entrées modifiées** (statut et message seulement), avant `hors_cours` « Cette équation ne
  se résout pas avec les méthodes du cours. » → après `forme_non_traitee` « Cette forme d'équation n'est pas traitée par l'outil. » :
  Az 4.1 b, Az 4.1 h, (x² + x + 1)² = x, (x + 1)³ = 8 + x, x²/2 = 1 + x, 0,5(x + 2)² = x + 3, x·3 + x² = 1, 2(x + 1)(x + 3) = 5,
  x⁶ − 64 = 0, 0,5x³ − 2x = 0, 2x⁴ − 10x² + 8 = 0 ; les 172 autres identiques ; 21 nouvelles (8 structures non écrites, 13 saisies
  invalides). Nouveaux : `instantanes/resoudre/equations-2e-degre.json` (204 sorties de la page) et
  `tests/pages/references/equations-2e-degre.json` (57 rendus). Aucun instantané d'un autre outil ne change (dump identique).

- **P4b, instantanés de la rédaction** : 52 entrées **nouvelles** dans `tests/python/donnees/equations-2e-degre/instantanes.json`
  (36 de `P4B` : 2.12 c, Az 4.1 a, f, g, x⁴ − 16, degré 1, identités, formes structurées de P4b… ; 16 de `NON_RESOLUES` : statut et
  message) ; **aucune** des 131 entrées de P2b à P4a modifiée. Textes rendus de 2.12 c, Az 4.1 f, Az 4.1 g et x⁴ − 16 comparés au
  corrigé dans `journal.md`, P4b. Messages « hors du cours » : question 29.

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
- `tests/python/test_redaction_second_degre.py::TestDegres::test_messages_definitifs` : 21 → 16 : R2 (par rapport à R1 ; test absent de `tests/reference`), six entrées sortent de `NON_RESOLUES` (2(x + 1)(x + 3) = 5, 0,5(x + 2)² = x + 3, x · 3 + x² = 1, x²/2 = 1 + x, Az 4.1 b, Az 4.1 h : maintenant résolues et contrôlées dans `R2` : oracle, invariants, instantanés, `TestR2`) et une y entre ((x − 1)(x + 2)(x + 3) = 1, hors du cours) : 16 → 11 entrées.
- `tests/python/test_redaction_second_degre.py::TestNonResolu::test_hors_du_cours_seulement_si_vrai` : 27 → 22 : R2 (par rapport à R1 ; test absent de `tests/reference`), même raison : `NON_RESOLUES` passe de 16 à 11 entrées (six résolues dans `R2`, une ajoutée).
- `tests/python/test_redaction_second_degre.py::TestNonResolu::test_formes_pas_encore_traitees` : 21 → 6 : P3 puis P4a (par rapport à P2b ; test absent de `tests/reference`), les 10 formes « P3 » puis les 5 formes « P4a » d'`A_VENIR` sont maintenant résolues et contrôlées par `test_a_venir[P3-…]` et `test_a_venir[P4a-…]` (xfail retiré), par l'oracle et par les instantanés.

## Tests renommés

- R3 : `tests/python/test_redaction_second_degre.py::TestStructures::test_aucune_variante_ni_developpement` →
  `::TestStructures::test_aucun_developpement` (test de P4a, absent de `tests/reference`) : le chemin du cours d'une forme structurée
  ne développe toujours rien (même contrôle) ; la variante, qui n'était jamais proposée, suit maintenant la règle de R3 (question 37)
  et y est contrôlée (proposée ⇔ trinôme de degré 2 et cours sans formule ; elle finit par la formule), plus `TestR3`.

- R2 : `tests/python/test_redaction_second_degre.py::TestNonResolu::test_hors_de_ce_que_e2_developpe` →
  `::TestNonResolu::test_developper_d_abord` (test de P3, absent de `tests/reference`) : ce qu'E2 n'écrivait pas est maintenant
  développé ou débarrassé de ses fractions (question 29) ; mêmes saisies, contrôlées résolues (première étape attendue), ou « hors du
  cours » vrai pour les degrés ≥ 3, plus tout `R2`.

- P5 : `tests/python/test_instantanes_second_degre.py::TestInstantanesSecondDegre::test_instantanes`, `::test_json_strict` et
  `::test_vocabulaire` retirés (tests de P2b, absents de `tests/reference`) : le JSON a quitté `tests/python/donnees/` pour
  `tests/python/instantanes/equations-2e-degre.json`, que figent et contrôlent les tests communs `test_instantanes.py::TestInstantanes::test_equations_2e_degre`,
  `test_json_strict.py::TestJsonStrict::test_fichiers_d_instantanes_en_json_strict` et `test_vocabulaire.py::TestVocabulaireEleve::test_instantanes` ;
  `test_section_8_complete` et `test_sorties_conformes` restent (sur le nouveau fichier), `test_corpus_fige_avec_son_statut` s'ajoute.

- P4b : `tests/python/test_redaction_second_degre.py::TestNonResolu::test_formes_pas_encore_traitees` →
  `::TestNonResolu::test_aucun_statut_temporaire` (test de P2b, absent de `tests/reference`) : le test d'attente est devenu vide
  (toutes les parties d'`A_VENIR` sont faites) ; il contrôle maintenant qu'aucune entrée (`RESOLUES`, `NON_RESOLUES`,
  `STRUCTURES_NON_ECRITES`) n'a de statut temporaire, chacune avec son statut et son message définitifs.
- P4a : `tests/python/test_redaction_second_degre.py::TestNonResolu::test_structures_laissees_a_p4a` →
  `::TestNonResolu::test_structures_sans_developper` (test de P3, absent de `tests/reference`) : les structures ne sont plus
  « laissées à P4a » ; mêmes formes, qui sont maintenant résolues sans développer, plus `STRUCTURES_NON_ECRITES` (« non_traite »).

## Reprise après compactage

- **P6 faite** (06.11.2026, filières au registre et cartes de l'accueil) : détail dans `journal.md`, P6. **Chantier terminé** :
  reste la fusion par l'enseignant (commande dans « Résumé »).
- **R3 faite** (06.11.2026, les deux boutons pour comparer, questions 37 et 25) : détail dans `journal.md`, R3. Suivante : P6.
- **R2 faite** (06.11.2026, développer d'abord, fractions supprimées d'abord, question 29) : détail dans `journal.md`, R2.
  Suivantes : R3 (questions 37 et 25), P6.
- **R1 faite** (06.11.2026, une carte par étape, question 36) : détail dans `journal.md`, R1.
- **Chantier de nuit terminé** (06.11.2026) : P0 à P5 faites et commitées, suite finale verte, résumé en tête de ce fichier (commit
  du résumé : le dernier de la branche). Prochaine étape : relecture par l'enseignant (« Résumé », questions), puis P6 et les
  corrections de relecture (parties R1, R2…) dans une nouvelle session ; rien à reprendre de la nuit.
- Lire `CLAUDE.md`, ce fichier, puis `journal.md` (plan en tête, section P0 pour les commandes, section de la dernière partie).
- `git log --oneline main..equations-2e-degre` : un commit par partie faite, puis celui du résumé.
- Dossier de travail hors du dépôt : `/home/sami-ubuntu/nuits/equations-2e-degre` (`rapports/<partie>`, `dumps/depart`, `dumps/<partie>`,
  `captures/`, `tmp/`). Si le dump de départ a disparu, le refaire sur le commit de P0 (commande dans `journal.md`, P0).
