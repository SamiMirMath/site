# Étude complète, étape 0 : rapport d'audit (aucun fichier du dépôt modifié)

Référence lue en entier : `docs/reference/etude-complete/3MSt_Ch8_EtudesFonctions_Corrige.tex` (810 l. : plan en 6 points, exemple 7, exercice 8.15 a–d).
Moteur lancé avec `uv` (Python 3.12, SymPy 1.13.3), `PYTHONDONTWRITEBYTECODE=1`, sans rien écrire dans le dépôt. L'oracle est mpmath à 40 chiffres, avec les fonctions écrites à la main : il n'utilise ni le parseur ni SymPy.

Seule action prévue après la sortie du mode plan : écrire ce rapport dans `docs/chantiers/etude-complete/audit-etape0.md`, puis s'arrêter (aucun commit, aucune branche).

## Synthèse

1. **Les valeurs sont toutes justes** sur les 5 fonctions du corrigé (contrôle par l'oracle) : ED, f', zéros de f', extremums (valeurs exactes et numériques), limites aux bornes, limites placées dans le tableau, asymptotes.
2. **Le plan du corrigé n'est pas suivi.**
   - La parité est absente : aucun code dans tout le dépôt.
   - Les zéros de f, le signe de f et l'ordonnée à l'origine sont absents.
   - L'ordre est différent : l'outil fait ED, dérivée, variations, limites, graphe ; le corrigé fait ED, parité, zéros et signe, limites, dérivée et variations, graphe.
   - La pente au point exclu (lim f' en 2⁻) est absente.
3. **Un défaut de rédaction partagé avec l'outil Dérivée.** `_simplifier` (`sp.factor`) éclate e^(somme) en un produit d'exponentielles. Exemples :
   - exemple 7 : f' contient e^(−2/(6x−12))·e^(x/(6x−12))·e^(x²/(6x−12)), et le tableau de signes a 3 lignes d'exponentielles ;
   - e^(x²+x) devient eˣ·e^(x²) ;
   - e^((x+1)/x) devient e·e^(1/x).

   Le résultat est juste mais illisible, et il ne correspond pas à l'énoncé.
4. **Le tableau de variations n'écrit pas les extremums.** La cellule affiche « • » (`commun/rendu.js:59`) ; le corrigé écrit e^(1/6), e^(3/2), −2e⁴…
5. **Les parties Limites suivent déjà la refonte 3M.** On y trouve le podium, BH, « pas indéterminée » et « Attention ». Restent des écarts de détail :
   - 0⁻ / 0⁺ du bas non justifié en x → 2 (ni tableau R8, ni valeur d'essai 1,99) ;
   - « f(x) → 0 » au lieu de 0⁺ dans le bilan ;
   - pas de position par rapport à l'AH ;
   - pas de rond vide (2 ; 0) sur le graphe.

## 1. Fichiers de l'outil et dépendances

**Propres à l'outil**

| Fichier | Rôle |
|---|---|
| `etude-complete/index.html` (≈100 l.) | `monterOutil({outil:"etude-complete", sympyAvant, delaiCalcul:45000, greffons:[greffonGraphique]})`, 8 exemples, 4 niveaux d'exercices. Aucun exemple du .tex. |
| `etude-complete/etude_complete.py` (≈200 l.) | `etudier()` : ED (`analyser_complet`), puis `dv.etudier`, `la.etudier(avec_bornes=True)`, `limites_du_tableau` (T06c) et le cadrage et l'échantillonnage du graphe ; `fenetre()` pour le zoom. Aucun calcul mathématique propre (EC-01). |
| `etude-complete/resoudre_ec.py` (≈60 l.) | Assemble les cartes : `rdv.carte_rappel`, `carte_derivee`, `carte_signe(ec=True)`, `rla.carte_tableaux`, `cartes_etude`, `carte_bilan`, puis la carte graphique. Réexporte `etudier_json` (ancienne page). |
| `docs/specifications/etude-complete.md` | EC-01 à EC-14 ; « Les résultats des trois étapes sont exactement ceux des outils séparés ». |

**Dépendances, et ce qu'un changement casserait ailleurs**

| Dépendance | Utilisée aussi par | Ce qu'un changement casse |
|---|---|---|
| `derivee-variations/derivee_variations.py` (`derivee_narree`, `_simplifier`, `etudier` : signe, tableau, extremums) | Outil Dérivée | Toute retouche de la forme de f' ou du tableau change la sortie de l'outil Dérivée : instantanés `instantanes/derivee-variations.json`, `resoudre/derivee-variations.json`, `pages/references/derivee-variations.json`, et les tests `test_proprietes_derivee`, `test_tableau_variations`, `test_facteurs_evidents`, `test_derivee_*`. Le correctif e^(somme) est voulu des deux côtés : instantanés à relire un par un. |
| `derivee-variations/resoudre_dv.py` (`carte_rappel`, `carte_derivee`, `carte_signe(ec=…)`) | Outil Dérivée | EC-01 (`test_resoudre_ec` : la carte Dérivée de l'EC = celle de l'outil Dérivée). Toute rédaction propre à l'EC doit passer par un paramètre (`ec=True`, comme aujourd'hui) ou rompre EC-01 explicitement. |
| `limites-asymptotes/limites_asymptotes.py` (3 783 l.) et `redaction_bh.py` (1 535 l., refonte 3M) | Outil Limites | Doctrine BH, podium, replis, garde-fou SymPy et sonde mpmath. Une retouche casse `test_redaction_bh_3m`, `test_corpus_limites_3m` (corpus de l'enseignant), `test_doctrine_bh`, `test_redaction_limites`, `test_garde_fou_limites`, et les instantanés Limites et EC. `avec_bornes=True` ne sert qu'à l'EC. |
| `limites-asymptotes/resoudre_la.py` (`carte_tableaux`, `cartes_etude`, `ligne_asymptote`, `carte_bilan`) | Outil Limites | Même règle EC-01. La phrase « à gauche, f(x) → 0 » et le bilan sans signe sont écrits ici : les corriger touche les deux outils. |
| `moteur/noyau.py`, puis `ensemble-definition/ensemble_def.py` (parseur, ED, `preimage`, `tableau_facteurs`, `evaluer`, pont SymPy) | Les 6 outils | Ajouter une fonction (parité, f(0)) est sans risque. Modifier le parseur, l'ED ou `preimage` touche tous les outils et tous les instantanés. `test_noyau` impose de n'importer que depuis `noyau`. |
| `moteur/sortie.py` (blocs `texte`, `formule`, `bh`, `encadre`, `resultat_lim`, `valeurs`, `sous_calcul`, `liste`, `tableau` ; `valider`) | Tous les outils | Un nouveau type de bloc demande `valider`, `rendu.js`, `test_sortie` et `aides_sortie` ; les tableaux passent par `_valider_tableau`. |
| `commun/rendu.js` (cellules du tableau : `extremum` → « • », `val:`, `asym` + limites) | Tous les outils à cartes | Écrire la valeur de l'extremum à la place de « • » changerait aussi l'outil Dérivée, sauf si c'est fait par un drapeau du tableau, comme `limites` en T06c. |
| `commun/graphique.js` (courbe, AH, AV, AO, trous, extremums, zoom tactile) | EC seule aujourd'hui | Tests de pages `test_graphique` (EC-04/05/06) et `references/graphique-traces.json`. Le rond vide d'une AV d'un seul côté et les points des zéros ou de f(0) seraient des ajouts. |
| `commun/outil.js`, `composants.css/js`, `style.css`, `tableaux.css` | Toutes les pages | `test_largeurs` (320 à 1100 px, `CONNUS` vide), `test_comportement`, `test_style_commun`, `test_tableaux_css`. |
| `moteur/manifeste.json` | Chargement Pyodide | Un nouveau fichier Python de l'EC doit y figurer (`test_manifeste`). Les 10 fichiers sont déjà chargés en parallèle (piège T19 de la file de connexions). |
| `tests/python/cas.py` → `entrees_page()` (lit `EXEMPLES` et `EXOS` du HTML) | Instantanés, `test_doctrine_bh`, `test_resoudre_ec` | Changer les exemples de la page change l'ensemble des instantanés obligatoires (ajouts à relire). |

**Fait annexe** : EC-02 (« ED calculé une seule fois, `fenetre()` ne recalcule pas l'ED ») n'est ni testé ni respecté. `analyser_complet` est appelé par `etudier`, `dv.etudier` et `la.etudier`, soit 3 fois, puis à chaque `fenetre()`, sans aucun cache.

## 2. Déroulement du corrigé, étape par étape, et état de l'outil

| # | Étape du .tex | Outil aujourd'hui | État |
|---|---|---|---|
| 0 | Mise en forme préalable : on factorise haut et bas (Ex7 : (x+2)(x−1), 6(x−2)) ; on nomme l'exposant g(x) | Rien | **Absent** |
| 1 | **ED** avec le calcul (6x − 12 = 0 ⇔ x = 2 ; x² − 4 = 0 ⇔ x = ±2), résultat encadré | Une ligne discrète « ED = ℝ∖{2} » dans la carte « Fonction », sans calcul. L'outil ED a les cartes de condition (`resoudre_ed`, réutilisées par l'outil Exp-log M). | **Différent** (pas de calcul) |
| 2 | **Parité** : ED non symétrique (Ex7 : −2 ∈ D, 2 ∉ D) ; f(−x) = f(x) en chaîne (a, d) ; contre-exemple f(1), f(−1) en valeurs approchées (b) ; f(0) ≠ 0, donc pas impaire (c) | Rien (aucun code de parité dans le dépôt) | **Absent** |
| 3 | **Zéros, signe, ordonnée à l'origine** : « eᵘ > 0, jamais nul » ; résolution de f = 0 (x² − 6 = 0 ⇔ x = ±√6 ; eˣ = 6 ⇔ x = ln 6) ; tableau de signes de f ; f(0) exacte et ≈ | Rien pour f (seulement pour f') | **Absent** |
| 4a | **Limites en ±∞** : « on remplace » haut / bas, forme, podium, BH avec dérivées haut / bas, « on applique l'exponentielle », ✓ ; ±∞ regroupés quand c'est identique (d) | Cartes « Étape n » de la refonte 3M : podium, BH, ✓, « pas indéterminée », « Attention » conformes. Écarts : Ex7 sans tableau haut → dérivée / bas → dérivée (présent en b), pas de « = +∞/6 » ; ±∞ jamais regroupés | **Conforme** pour l'essentiel, écarts mineurs |
| 4b | **Limites en une valeur interdite** : haut (4, pas 0, donc pas indéterminée), bas avec valeur d'essai (1,99 → −0,06 → 0⁻), exposant, puis exponentielle | Une seule étape « Exposant → 4/0⁻ = −∞. Donc e^… → 0⁺ ». **0⁻ non justifié** : ni tableau de signes (R8), ni valeur d'essai | **Différent** |
| 4c | **Conclusions** : AH y = 0 « à gauche », **graphe au-dessus (0⁺)** ; AH y = 1, exposant → 0⁺, donc au-dessus ; AV x = 2 **seulement à droite**, point exclu (2 ; 0) « rond vide » | « Asymptote horizontale : y = 0. » sans position ; « Asymptote verticale : x = 2 (du côté droit) ; à gauche, f(x) → 0 » (0 sans signe) ; bilan « lim_{x→2⁻} f(x) = 0 » | **Différent** |
| 5a | **Dérivée** : formule (eᵍ)' = g'·eᵍ ; g' par règle du quotient avec tableau u, u', v, v' ; numérateur développé morceau par morceau ; simplification 36(x−2)² ; résultat encadré **x(x−4)/(6(x−2)²)·e^{g(x)}** | Phrase parasite « (x²)' = 2x » puis une seule phrase « de la forme eᵘ… u'(x) = [(2x+1)(6x−12) − (x²+x−2)·6]/(6x−12)² » sans développement ni simplification ; résultat **e^(g) éclaté en trois exponentielles** | **Différent** (et défaut) |
| 5b | Produit (b) : tableau u, u', v, v' ; e^(−2x) mis en évidence ; trinôme factorisé (Somme-Produit) | u, v en phrase, u', v' sur deux lignes ; « (x²−6) · −2e^(−2x) » **sans parenthèses** ; factorisation directe par SymPy, sans étape | **Différent** |
| 5c | (c) : « on développe d'abord » 6eˣ − e^(2x), puis 2eˣ(3 − eˣ) | Règle du produit, « (eˣ)' = eˣ » écrit **deux fois** ; résultat −2(eˣ − 3)eˣ | **Différent** (juste) |
| 5d | **Signe de f'** : une ligne par facteur, dont des facteurs groupés (6(x−2)², −2e^(−2x)) | Une ligne par facteur et une par constante (R7) : « 1/6 », « −2 », « −4 » à part ; ligne précédée de la résolution de f' = 0 | **Conforme à R7**, différent du .tex |
| 5e | **Valeurs des extremums** calculées (g(4) = 18/12 = 3/2, donc f(4) = e^{3/2} ≈ 4,48) | Valeur exacte seule, sans calcul ni ≈ | **Différent** |
| 5f | **Tableau de variations** avec les limites et les **valeurs des extremums** dans la ligne f(x) | Limites aux bords et aux doubles barres (T06c) ✓ ; extremums **« • »** | **Différent** |
| 5g | **Extremums** : point (x ; y) ≈ (…), raison « f' passe de + à − », **global / local** (b min global, c max global, d « pas global ») | « maximum local en x = 0 : f(0) = e^{1/6} » ; toujours « local » ; ni point, ni ≈, ni raison | **Différent** |
| 6 | **Pente au point exclu** lim_{x→2⁻} f'(x) : changement de variable t = 1/(x−2), produit vers quotient, 2 BH, tangente horizontale (Ex7, d) | Absent. L'outil Limites lancé sur f' donne la bonne valeur, mais **en repli** (« pas rédigé ici ; résultat : 0 »), en 14 s natif | **Absent** |
| 7 | **Graphe** : courbe, AV et AH en pointillé, extremums, **zéros et f(0) marqués** (b, c), **rond vide aux points exclus**, fenêtre qui montre l'AH ; b : vue d'ensemble puis zoom | Courbe, asymptotes, extremums, trous (genre « trou » seulement) ; pas de zéros ni de f(0) ; pas de rond vide pour une AV d'un seul côté ; c : fenêtre x ∈ [−0,9 ; 3,1], donc l'AH à gauche n'est pas visible ; zoom interactif à la place de la 2e figure | **Différent** |

## 3. Les 5 fonctions du corrigé : résultats et écarts

Valeurs : toutes justes. f' de l'outil contre la dérivée numérique : écart relatif ≤ 3·10⁻⁴¹. f aux extremums identique à 8 chiffres. f'(x_extr) = 0. Sondes en ±10³ et en a ± 10⁻⁶ conformes. Temps natif : 0,0 à 0,8 s par fonction.

| Fonction | Valeurs (oracle) | Écarts de rédaction (en plus des absences de §2 : parité, zéros, signe, f(0), ordre, ≈, global, pente) |
|---|---|---|
| **Ex7** e^((x²+x−2)/(6x−12)) | ED ℝ∖{2} ✓ ; max (0 ; e^{1/6} ≈ 1,1814) ✓ ; min (4 ; e^{3/2} ≈ 4,4817) ✓ ; −∞ : 0⁺ ✓ ; +∞ : +∞ ✓ ; 2⁻ : 0⁺, 2⁺ : +∞ ✓ ; lim f' en 2⁻ = 0⁻ (oracle ≈ −4,5·10⁻²⁸⁴), absente de l'outil | **f' éclatée en 3 exponentielles**, d'où 3 lignes d'exponentielles et une ligne « 1/6 » dans le tableau ; « (x²)' = 2x » parasite ; g' non développée ni simplifiée ; BH de l'exposant sans tableau haut / bas ; 0⁻ en 2 non justifié ; « à gauche, f(x) → 0 » et bilan « = 0 » sans signe ; pas de rond vide (2 ; 0) ; fenêtre x ∈ [−2 ; 6] |
| **a** e^(−x²) | ED ℝ ✓ ; max (0 ; 1) ✓ (global) ; ±∞ : 0⁺ ✓ ; AH y = 0 des deux côtés ✓ | Très proche. Écrit « maximum local » (le .tex : maximum global) ; deux lignes « −2 » et « x » au lieu de « −2x » (R7) ; pas « graphe au-dessus » |
| **b** (x²−6)e^(−2x) | Zéros ±√6 ✓ (oracle), f(0) = −6 ; min (−2 ; −2e⁴ ≈ −109,196) ✓ (global) ; max (3 ; 3e⁻⁶ ≈ 0,00744) ✓ ; −∞ : +∞ ✓ ; +∞ : 0⁺ (2 BH) ✓ | Limites **très proches du .tex** (Étapes 1 à 6, BH 1re et 2e fois, ✓) ; « (x²−6) · −2e^(−2x) » sans parenthèses ; mise en évidence de e^(−2x) et Somme-Produit absents ; f(3) écrit 3/e⁶ (le .tex : 3e⁻⁶) ; « minimum local » au lieu de global ; graphe y ∈ [−145 ; 70], max local illisible sans zoom |
| **c** eˣ(6 − eˣ) | Zéro ln 6 ✓ (oracle), f(0) = 5 ; max (ln 3 ; 9) ✓ (global) ; −∞ : 0⁺ ✓ ; +∞ : −∞ ✓ | « (eˣ)' = eˣ » écrit deux fois ; produit au lieu de « on développe d'abord » ; −2(eˣ − 3)eˣ au lieu de 2eˣ(3 − eˣ) ; les limites « 0⁺·6 = 0⁺ » et « (+∞)·(−∞) » sont conformes ; fenêtre sans l'AH gauche |
| **d** e^(2/(x²−4)) | ED ℝ∖{−2 ; 2} ✓ ; paire ; max (0 ; e^{−1/2} ≈ 0,6065) ✓ (non global) ; ±∞ : 1 ✓ (f − 1 > 0, donc au-dessus) ; −2⁻ : +∞, −2⁺ : 0⁺, 2⁻ : 0⁺, 2⁺ : +∞ ✓ ; lim f' en 2⁻ = 0⁻ | f' avec (x−2)²(x+2)² au lieu de (x²−4)² ; u' = −2·2x/(x²−4)² non simplifié en −4x ; ±∞ non regroupés ; « e^{0⁺} = 1 » sans « au-dessus » ; points exclus (±2 ; 0) non dessinés ; pente absente (l'outil Limites sur f' : repli en 2⁻ et −2⁺) |

La portée du défaut e^(somme) a été vérifiée dans l'outil Dérivée : e^(x²+x) donne (2x+1)eˣe^(x²) ; e^((x+1)/x) donne −e·e^(1/x)/x² ; x·e^((x−1)/(x+1)) donne deux exponentielles.

## 4. Tests existants de l'Étude complète

**Couvert**
- `test_resoudre_ec.py` (EC-01, EC-14) : schéma, rien de perdu, ordre des cartes, cartes identiques aux outils séparés, phrases propres, graphique, limites dans le tableau, erreurs, JSON.
- `test_tableau_limites.py` (EC-08 à EC-12) : 1/(x−2), 1/(x−2)², trou, ln(x²−4), ln x, √x, « ? », mêmes valeurs que la partie Limites.
- `test_fenetre_zoom.py` (EC-03), `test_doctrine_bh.py` (exemples de la page, 3.10e, 3.11e : pas de croissance comparée), `test_instantanes.py` et `test_instantanes_resoudre.py` (15 entrées : 8 exemples, EXOS et 6 cas limites).
- Transversaux : `test_json_strict`, `test_vocabulaire`, `test_facteurs_evidents`, `test_racines_reelles`, `test_tableaux_css` (EC-13), `test_noyau`.
- Pages : `test_graphique.py` (EC-04/05/06), `test_comportement.py` (rendu commun = ancienne page, `x^2*e^(-x)`), `test_rendu.py`, `test_largeurs.py`.

**Manque**
- Aucune des 5 fonctions du .tex dans un test, ni dans les exemples de la page. Aucune fonction e^(fraction) dans les instantanés de l'EC.
- Aucun oracle sur la sortie de l'EC elle-même (extremums, limites du tableau) : EC-10 compare à la partie Limites, pas à mpmath. `test_proprietes_derivee` couvre l'outil Dérivée, pas les valeurs affichées par l'EC.
- Rien ne détecte la forme de f' (e^(g) gardé entier), ni les parenthèses autour d'un facteur négatif.
- EC-02 n'est pas testé (et pas respecté) ; EC-07 est manuel.
- Le cadrage du graphe n'est pas testé : AH visible, extremums dans la fenêtre.
- Rien sur l'AV d'un seul côté avec point exclu.
- Sans objet aujourd'hui : parité, zéros, signe de f, f(0), global ou local, ≈, ordre des parties du .tex.

## 5. Décisions à prendre avant la refonte (avec recommandation)

1. **Ordre et titres des parties.** Recommandation : suivre le .tex exactement, avec les titres numérotés « 1. Domaine de définition », « 2. Parité », « 3. Zéros, signe, ordonnée à l'origine », « 4. Limites et asymptotes », « 5. Dérivée, tableau de variation, extremums », « 6. Graphe ».
2. **EC-01 (« aucun calcul nouveau, cartes identiques aux outils séparés »).** La parité, les zéros, le signe de f, f(0), global ou local et les ≈ sont des calculs nouveaux. Recommandation : remplacer EC-01 par « les parties communes ED, dérivée et limites gardent les mêmes valeurs que les outils séparés ». Les parties nouvelles vont dans un module propre (`etude-complete/parties.py`), avec garde-fou numérique ; la rédaction propre à l'EC passe par des paramètres (`ec=True`).
3. **ED détaillé.** Recommandation : réutiliser les cartes de condition de l'outil ED (`resoudre_ed`, comme l'outil Exp-log M), en version courte « 6x − 12 = 0 ⇔ x = 2 », résultat encadré.
4. **Méthode de parité.** Recommandation, dans cet ordre :
   - (i) ED non symétrique : un point a ∈ D avec −a ∉ D ;
   - (ii) f(−x) écrite et simplifiée, = f(x) ou = −f(x), confirmée par SymPy et par sonde ;
   - (iii) sinon f(0) ≠ 0 pour « pas impaire » quand 0 ∈ D, et un contre-exemple f(1), f(−1) en ≈ pour « pas paire ».

   Un contre-exemple n'est écrit que si l'écart numérique est net ; sinon un message clair.
5. **Zéros et signe de f.** Recommandation :
   - réutiliser `preimage` et la machinerie du tableau de f' ;
   - phrase « eᵘ > 0, jamais nul » quand un facteur exponentiel est présent ;
   - tableau de signes de f seulement si f a des zéros ou des valeurs interdites qui changent le signe ;
   - sinon une ligne (« f(x) > 0 partout »).
6. **Correction de `_simplifier` (e^(somme)).** C'est un défaut partagé. Recommandation : le corriger dans `derivee_variations.py` (traiter chaque eᵘ comme un atome avant `sp.factor`), avec relecture des instantanés de l'outil Dérivée, dans une partie à elle seule, avant tout le reste.
7. **Dérivée d'un exposant composé (Ex7).** Recommandation : sous-étape « dérivée de l'exposant » avec la règle du quotient au premier niveau, puis numérateur développé et simplifié (étapes 3 et 4 du .tex), puis f' = g'·e^{g(x)} avec g nommé. Écrire aussi les parenthèses autour d'un facteur négatif (défaut b).
8. **u, u', v, v' : tableau 2 × 2 (.tex) ou ligne (R11).** Recommandation : tableau 2 × 2 comme le .tex, sur le modèle du bloc `bh` existant, dans les deux outils. Sinon garder R11 et accepter l'écart.
9. **Lignes du tableau de signes de f' : R7 (une par facteur, constantes à part) ou facteurs groupés (6(x−2)², −2e^(−2x)) comme le .tex.** Recommandation : garder R7 (règle validée, partagée, testée).
10. **Valeurs des extremums dans le tableau de variations.** Recommandation : oui, en EC par un drapeau du tableau (comme `limites` en T06c). L'outil Dérivée garde « • » sauf si vous le voulez aussi.
11. **Extremums : point, raison, global ou local, ≈.** Recommandation :
    - « Maximum local en x = 0 : (0 ; e^{1/6}) ≈ (0 ; 1,18) (f' passe de + à −) » ;
    - « global » seulement si la comparaison avec toutes les limites aux bornes et les autres extremums est sûre ; s'il y a un « ? », « local » seul ;
    - ≈ avec 2 décimales, notation scientifique sous 10⁻³ (R13), soit ≈ 0,0074 pour 3e⁻⁶.
12. **Justification de 0⁺ / 0⁻ en une valeur interdite.** Il faut trancher entre le tableau de signes (R8, outil Limites) et la valeur d'essai x = 1,99 (.tex). Aujourd'hui aucun des deux n'apparaît pour un exposant. Recommandation : une seule règle pour les deux outils. Je propose la valeur d'essai du .tex (plus proche du cours 3M), en gardant le tableau R8 pour ln et les fractions déjà traitées ; ou R8 partout si vous préférez la cohérence.
13. **Position par rapport à l'AH et AV d'un seul côté.** Recommandation :
    - « le graphe est au-dessus (0⁺) » quand le signe d'approche est connu ;
    - « Asymptote verticale x = 2, seulement du côté droit ; à gauche le graphe s'approche du point (2 ; 0), qui n'appartient pas au graphe » ;
    - 0⁺ partout (bilan compris) ;
    - rond vide sur le graphe.

    Ces changements touchent aussi l'outil Limites.
14. **Pente au point exclu (lim f' en a⁻).** Le moteur actuel le fait en repli seulement : il faut un changement de variable t = 1/(x−a) et 2 BH. Recommandation : le reporter à une étape tardive et facultative (« Pour aller plus loin »), affichée seulement si la rédaction complète réussit ; jamais de phrase de repli dans l'EC.
15. **Graphe.** Recommandation :
    - marquer zéros et f(0) ;
    - rond vide aux points exclus ;
    - cadrage élargi pour montrer chaque AH (c, Ex7) ;
    - pas de seconde figure (le zoom interactif remplace « Zoom » de b).
16. **Regrouper ±∞ quand les deux calculs sont identiques (d) ; ordre des bornes.** Recommandation : regrouper seulement si le texte est identique ; garder l'ordre −∞, valeurs interdites, +∞ (le .tex n'est pas constant).
17. **Forme des valeurs exactes** (3/e⁶ contre 3e⁻⁶, −2(eˣ − 3) contre 2(3 − eˣ)). Recommandation : écriture du .tex quand elle est sans risque (e⁻ᵏ gardé, coefficient positif devant), sinon accepter l'écart.
18. **Exemples de la page.** Recommandation : ajouter les 5 fonctions du .tex aux exemples et aux exercices (niveaux difficile et très difficile), ce qui les fait entrer dans les instantanés et les tests de pages.
19. **EC-02 (ED calculé 3 fois, sans cache).** Recommandation : cache par entrée dans `etude_complete.py` et un test compteur, ou retirer le critère.

## Risques

- **Effet de bord sur l'outil Dérivée et l'outil Limites** : décisions 6, 7, 8, 12 et 13. Chaque partie partagée doit relire les instantanés des deux outils et passer `test_corpus_limites_3m` et `test_redaction_bh_3m` sans affaiblir les garde-fous.
- **« Rien de faux à l'écran »** : la parité, le global ou local et les contre-exemples sont de nouvelles affirmations. Chacune doit être confirmée par SymPy et par sonde mpmath, avec un message clair si l'un des deux doute.
- **Temps Pyodide** : l'EC appelle déjà ED, Dérivée et Limites (délai 45 s). Ajouter parité, zéros et global, et surtout la pente (14 s natif en repli pour Ex7), peut dépasser le plafond. Il faut mesurer dans Pyodide à chaque partie.
- **Longueur de la page** : Ex7 compte déjà environ 20 cartes ; avec 6 parties et des sous-étapes, il faudra regrouper par partie pour garder « Étape suivante » utilisable à 390 px.
- **Tableau de variations plus large** avec des valeurs (e^{3/2}, 0⁺ ‖ +∞) : à vérifier à 320–360 px (EC-13, `test_largeurs`).
- **Manifeste** : un nouveau fichier Python s'ajoute au chargement parallèle (piège T19).

## Découpage proposé (une branche `etude-complete`, un commit par partie, suite complète verte avant chaque commit)

0. Fiche `docs/chantiers/etude-complete/suivi.md`, puis corpus du .tex (`tests/python/donnees/corpus_etude_complete.py`) avec oracle mpmath sur valeurs, extremums, limites, zéros, parité et f(0). Échecs attendus marqués.
1. Correctif partagé `_simplifier` (e^(somme) gardé entier) et parenthèses du facteur négatif ; doublon « (eˣ)' » et ligne parasite retirés. Instantanés de l'outil Dérivée relus.
2. Squelette de l'EC dans l'ordre du .tex, avec des titres de parties numérotés (sans contenu nouveau) ; EC-01 et EC-14 réécrits dans la spécification.
3. Partie 1, ED détaillé (cartes de l'outil ED).
4. Partie 2, parité (module nouveau, garde-fous).
5. Partie 3, zéros, signe de f, f(0) (≈ selon R13).
6. Partie 4, retouches Limites : 0⁺ partout, position par rapport à l'AH, AV d'un seul côté, justification de 0± (décision 12), regroupement ±∞. Touche l'outil Limites.
7. Partie 5 : dérivée de l'exposant détaillée, tableau u, u', v, v', valeurs dans le tableau de variations, extremums (point, raison, global, ≈).
8. Partie 6, graphe : zéros, f(0), ronds vides, cadrage des AH. Tests de pages et largeurs.
9. Exemples de la page, instantanés, `test_largeurs`, mesure Pyodide ; relecture à l'écran par l'enseignant.
10. (Facultatif, plus tard) Pente au point exclu, avec changement de variable.
