# Chantier « Étude complète » — suivi

Refonte de l'outil Étude complète pour suivre le corrigé `docs/reference/etude-complete/3MSt_Ch8_EtudesFonctions_Corrige.tex` (exemple 7, exercice 8.15 a–d).
Branche `etude-complete`, créée le 02.11.2026 depuis `main` à jour (9716912, fusion de `correctif-explog-3c`). Rien n'est poussé ni fusionné.
Ordre de priorité : `CLAUDE.md` > `decisions.md` (validé par l'enseignant le 02.11.2026) > `audit-etape0.md`.
Un commit « EC P{N} : … » par partie ; suite complète verte (`python3 tests/lancer.py complet`, code de retour lu sans pipe) avant chaque commit.

**Reprise après compactage** : relire ce fichier, `decisions.md`, puis `git log --oneline main..HEAD` ; reprendre à la première partie « à faire ».
Les tests du chantier sont dans `tests/python/test_corpus_etude_complete.py` (corpus : `tests/python/donnees/corpus_etude_complete.py`) ; chaque
vérification pas encore faite y est marquée `xfail` **strict** avec le numéro de sa partie : la partie qui la traite retire la marque (un xfail qui
passe fait échouer la suite). Temps natif : `docs/chantiers/etude-complete/mesurer_temps.py`.

## Parties

| Partie | Contenu (decisions.md §6) | Touche | État | Commit |
|---|---|---|---|---|
| P0 | `suivi.md`, corpus + oracle mpmath, xfail marqués avec leur partie | tests | **fait** | 5eadf34 |
| P1 | D6, D7 (parenthèses, doublons), D17 | Dérivée | **fait** | edf17c3 |
| P2 | Squelette des 6 parties titrées (D1), spécification (D2, D19) | EC | **fait** | 4cf3e9e |
| P3 | Partie 1 : mise en forme + ED détaillé (D3) | EC | **fait** | voir `git log` (« EC P3 ») |
| P4 | Partie 2 : parité (D4) | EC | à faire | |
| P5 | Partie 3 : zéros, signe, f(0) (D5) | EC | à faire | |
| P6 | Partie 4 : D12, D13, D16 | Limites | reportée (hors de la nuit du 02.11) | |
| P7a | Dérivée de l'exposant détaillée, tableau u/v (D7, D8, D7b si simple) | Dérivée | à faire | |
| P7b | Valeurs dans le tableau de variations (D10), extremums (D11) | EC + Dérivée | à faire | |
| P8 | Graphe (D15, §3) | EC | à faire | |
| P9 | Exemples (D18), Bilan (D20), instantanés, largeurs 320–390 px, mesure Pyodide | EC | reportée (hors de la nuit du 02.11) | |
| P10 | *(facultatif)* Pente au point exclu (D14) | EC | reportée (hors de la nuit du 02.11) | |

## Résumé de la nuit

- **P0 faite** : branche `etude-complete` ; `audit-etape0.md` (copie inchangée du rapport d'audit) et `decisions.md` versés au dépôt ; corpus
  Ex7, a–d avec les résultats de decisions.md §4–5 ; oracle mpmath (fonctions écrites à la main) : tout le corpus est confirmé ; les valeurs de
  l'outil (ED, extremums, signe de f′, limites du tableau, asymptotes, fenêtre) sont justes ; 66 vérifications de rédaction marquées xfail (P1 à P10).
  Aucun changement du moteur.
- **P1 faite** : outil Dérivée (`derivee_variations.py`) : e^(somme) gardé entier (une exponentielle par exposant, D6) ; facteur négatif entre
  parenthèses et phrase de dérivée écrite une seule fois (D7) ; 3e^{−6} et 2eˣ(3 − eˣ) (D17). 5 xfail P1 retirés ; 5 instantanés de
  l'outil Dérivée / EC modifiés (liste sous « À relire ») ; questions 5 et 6 ; temps inchangé.
- **P2 faite** : six parties titrées dans l'ordre du .tex (D1) par un nouveau style de carte `partie` (intertitre sans cadre, commun à tous
  les outils, affiché avec la carte qui le suit et hors du compteur d'étapes) ; limites avant la dérivée ; parties 2 et 3 vides ;
  cache de l'analyse (D19) : un seul calcul par `etudier()`, aucun par `fenetre()` ; spécification réécrite (EC-01, EC-02 testé, EC-15).
  2 xfail P2 retirés ; seuls les instantanés de l'EC changent (ordre des cartes et intertitres) ; questions 7 à 9.
- **P3 faite** : partie 1 rédigée par le nouveau module `etude-complete/parties.py` (D2) : carte « Fonction » (f seule), carte « Mise en
  forme » (Ex7 : Somme-Produit, mise en évidence, g(x) nommé), une carte par condition (cartes de l'outil ED ; dénominateur affine ou
  ax² + c en chaîne courte « On résout 6x − 12 = 0 ⇔ 6x = 12 ⇔ x = 2. »), carte « Ensemble de définition » (ED encadré). Garde-fous exact
  et numérique ; les outils ED, Dérivée, Limites, Exp-log ne changent pas. 7 xfail P3 retirés ; instantanés de l'EC : partie 1 seule
  (liste sous « À relire ») ; questions 10 à 14 ; temps inchangé.

## Plans

### P0 (02.11.2026)

1. Branche `etude-complete` depuis `main` à jour ; copie telle quelle du rapport d'audit vers `audit-etape0.md`.
2. `tests/python/donnees/corpus_etude_complete.py` : une entrée par fonction (Ex7 exemple, a–d exercices, D18) avec f et f′ écrites à la main
   en mpmath, valeurs interdites, parité et sa justification (ED non symétrique ou f(0) et contre-exemple), zéros, signe de f, f(0), limites
   avec signe d'approche, regroupement ±∞, extremums (≈, global ou non, raison), AH et position, AV et côtés, ronds vides, pentes (P10).
3. `tests/python/test_corpus_etude_complete.py`, en trois sections :
   - **oracle** (mpmath seul, ni parseur ni SymPy) : f′ = dérivée numérique ; ED ; parité ; zéros et signe sur une grille fine ; f(0) ;
     limites et signe d'approche par sondes (±10ᵏ, a ± 10⁻ᵏ) ; extremums (f′ = 0, changement de signe, global recalculé d'après D11,
     raison) ; asymptotes et ronds vides déduits des limites ; pentes ; arrondis de decisions.md §2 ;
   - **valeurs de l'outil** (vertes aujourd'hui) : ED lu dans `ed_tex`, extremums (`x_tex`, `f_tex`, valeurs), points critiques et signe de
     f′, limites du tableau de variations (T06c) et 0⁺, asymptotes et côtés des AV, fenêtre contenant extremums, zéros et (0 ; f(0)) ;
     les écritures LaTeX de l'outil sont lues par une petite lecture écrite à la main (liste fermée de motifs) ;
   - **rédaction cible** : une vérification par décision, `xfail(strict=True)` avec la partie (P1 … P10), posée paramètre par paramètre
     seulement là où le test échoue aujourd'hui (vérifié avec `--runxfail` : toutes échouent par une assertion, aucune par une erreur du test).
4. `docs/chantiers/etude-complete/mesurer_temps.py` : temps natif de `etudier()` (processus neuf par mesure, médiane de 3).
5. Suite complète, puis commit « EC P0 : … » (audit, décisions, suivi, corpus, test, script de mesure).

### P1 (02.11.2026)

Tout se passe dans `derivee-variations/derivee_variations.py` (portée EC + Dérivée) ; le noyau (`ensemble_def.tex`, `num_sympy`) n'est pas
touché, pour ne pas changer les autres outils.
1. **D6** : `_simplifier` passe par `powsimp(combine='exp')`, puis chaque `exp(a)` devient `T^k` (T symbole muet par famille d'exposants
   proportionnels, k entier : `e^{2x} = T²` si `T = eˣ`), `factor`, puis on remet les exponentielles. Repli sur l'ancien calcul en cas
   d'erreur. Le remplacement est exact (a = k·w), donc aucun risque de valeur fausse.
2. **D7 parenthèses** : dans la ligne « u′v + uv′ » (ou « u′v − uv′ »), un facteur de droite négatif est écrit `Neg(…)`, que `tex`
   met entre parenthèses : `(x² − 6)(−2e^{−2x})`.
3. **D7 doublons** : une phrase de narration déjà écrite n'est pas répétée (« (eˣ)′ = eˣ » une seule fois pour c). Le « (x²)′ = 2x » parasite
   de Ex7 reste (P7a).
4. **D17** : (a) valeur exacte d'un extremum de la forme *entier × e^{−k}* (k constant > 0) : l'exponentielle reste au numérateur
   (`3e^{−6}`, pas `3/e⁶`) ; un coefficient non entier (−1/(2e)) garde l'écriture de SymPy ;
   (b) f′ = c·… avec c < 0 et un seul facteur somme non polynomial de puissance impaire ayant un terme négatif (eˣ − 3) : le signe y entre
   (`2(3 − eˣ)`) ; un facteur `e^{u}` seul passe devant le facteur somme qui le contient (`2eˣ(3 − eˣ)`). Les facteurs polynomiaux (x − 3)
   restent unitaires (R7), donc b garde −2 (comme le corrigé) ; −(e^{2x} + 1)e^{−x} reste tel quel (jamais −e^{2x} − 1).
5. Tests : retrait des xfail « P1 » du corpus ; `TestFormesDuCorrige` dans `test_derivee_narration.py` (justesse numérique de f′ sur une
   famille à exponentielles, une exponentielle par exposant, parenthèses, phrase unique, formes exactes et cas laissés tels quels) ;
   `test_isoler_atome.py` suit la nouvelle forme de ln(x)/x. Instantanés moteurs, `resoudre` et références de pages régénérés, listés sous
   « À relire » ; suite complète ; temps natif ; commit « EC P1 : … ».

### P2 (03.11.2026)

Squelette sans contenu mathématique nouveau (D1), spécification (D2), cache (D19). L'outil Dérivée et l'outil Limites seuls ne changent pas.
1. **Intertitres (D1)** : nouveau style de carte `partie` dans `moteur/sortie.py` (constructeur `so.partie(titre)`, carte sans bloc), rendu
   par `commun/rendu.js` en `<h2>` sans cadre (`.carte-etape.partie` dans `commun/composants.css`, composant commun). `commun/outil.js` :
   un intertitre n'est pas une étape (il apparaît avec la carte qui le suit et n'entre pas dans « Étape k / n »). Les autres outils
   n'ont pas d'intertitre : rien ne change pour eux.
2. `resoudre_ec.py` : six intertitres dans l'ordre du .tex ; cartes réordonnées : 1 « Fonction » ; 2 et 3 vides (l'option qui affiche
   le moins) ; 4 tableaux de signes, limites, bilan des asymptotes ; 5 dérivée, signe de f′ et variations ; 6 graphique.
3. **D19** : `etude_complete.py`, cache `functools.lru_cache` de `analyser_complet` par entrée normalisée (espaces réduits) et état de
   SymPy (un résultat obtenu sans SymPy n'est jamais resservi avec) ; `dv.etudier` et `la.etudier` reçoivent un paramètre facultatif
   `analyse` (résultat déjà calculé) : sans lui, comportement inchangé. Test compteur : vide le cache, puis 1 calcul par `etudier()`,
   0 de plus par `fenetre()`.
4. Spécification `docs/specifications/etude-complete.md` : EC-01 réécrit, EC-02 testé, EC-15 nouveau, les 6 parties, module
   `parties.py` annoncé (créé à P4, quand une partie a un contenu : rien d'utile à y mettre à P2) ; `docs/choix-techniques.md` : style
   `partie` du format de sortie.
5. Tests : retrait des xfail P2 ; `test_resoudre_ec.py` suit le nouvel ordre ; `test_sortie.py` (style `partie`) ; instantanés `resoudre`
   et références de pages de l'EC régénérés ; suite complète ; temps natif ; commit « EC P2 : … ».

### P3 (03.11.2026)

Partie 1 de l'EC (D1, D3), tout dans un nouveau module `etude-complete/parties.py` (D2) ; les outils ED, Dérivée, Limites et Exp-log ne
changent pas (leurs instantanés restent identiques). Comme la filière M de l'outil Exp-log (`resoudre_el._blocs_ed`), on reprend les
fonctions publiques de `resoudre_ed` (`blocs_condition`, `blocs_ensemble`), sans les modifier.
1. `parties.mise_en_forme(f)` : seulement si f = e^{haut/bas}, haut et bas polynômes de degré ≥ 1 écrits développés à coefficients
   entiers. Chaque membre : mise en évidence de c·xᵏ (c = pgcd), puis Somme-Produit (trinôme unitaire, deux racines entières distinctes,
   facteurs par racine croissante : (x + 2)(x − 1)) ; une ligne par méthode, « (méthode) » à droite ; puis « On note g(x) = haut/bas
   factorisés, donc f(x) = e^{g(x)}. ». Garde-fous : produit développé = polynôme (exact), sonde `evaluer` de l'arbre en 5 points ;
   sinon la ligne n'est pas écrite. Aucune ligne : pas de carte (d n'en a pas, comme le .tex : haut constant).
2. `parties.blocs_condition(c, A)` : un dénominateur affine ou ax² + c (c/a < 0, racines rationnelles ou k√m), écrit développé, donne la
   chaîne courte du .tex (« On résout … ⇔ … ») sous l'inégalité de l'outil ED ; garde-fous : l'ensemble ℝ ∖ {racines} écrit comme l'outil
   ED est exactement son `E_tex`, et `evaluer(A, racine) ≈ 0` ; dénominateur x : « x ≠ 0 » seul (l'outil ED écrit « x ≠ 0 ⇔ x ≠ 0 ») ;
   tout le reste (ln, racine, Δ, écriture factorisée…) : les blocs de l'outil ED tels quels. Les arbres des conditions viennent de
   `conditions` (réexporté par `noyau`, sans changement de `ensemble_def`), sur l'analyse en cache (aucun nouveau calcul, D19).
3. `parties.cartes_domaine` : Fonction (formule seule : l'ED est établi juste après), Mise en forme, Condition k (titre, badge et
   détail de l'outil ED), « Ensemble de définition » (style normal, `blocs_ensemble` : ED encadré ; sans condition, précédé de la phrase
   de l'outil ED « Ni logarithme, ni dénominateur, ni racine : aucune condition. »). `resoudre_ec` l'appelle à la place de
   `rdv.carte_rappel`. Manifeste : `resoudre_ed.py` et `parties.py` ajoutés à l'EC.
4. Tests : xfail P3 retirés ; `test_parties_ec.py` (lignes exactes, oracle mpmath sur 150 polynômes tirés au hasard et sur les racines,
   formes laissées à l'outil ED, garde-fous forcés en échec) ; `test_resoudre_ec.py` (ordre des cartes calculé depuis l'analyse de
   l'outil ED, ED et conditions identiques à l'outil ED) ; `test_noyau.py` (parties.py n'importe que du noyau) ; Ex7 et d ajoutés aux cas
   limites de l'EC (`cas.py`, cités dans la spécification) pour les instantanés et le rendu de page. Instantanés `resoudre` et
   références de pages de l'EC régénérés ; largeurs 320/360/390 vérifiées à part pour Ex7, d, 1/(4x²−1) et une mise en forme à
   deux lignes (aucune faute) ; suite complète ; temps natif ; commit « EC P3 : … ».

## Temps natif de etudier() (s, médiane de 3 processus neufs)

| Partie | Ex7 | a | b | c | d |
|---|---|---|---|---|---|
| P0 | 0,59 | 0,02 | 0,42 | 0,18 | 0,30 |
| P1 | 0,63 | 0,02 | 0,42 | 0,19 | 0,30 |
| P2 | 0,60 | 0,02 | 0,43 | 0,18 | 0,32 |
| P3 | 0,59 | 0,02 | 0,42 | 0,19 | 0,30 |

P3 ne touche pas `etudier()` ; la partie 1 (`parties.cartes_domaine`, appelée par `resoudre`) coûte en plus 0,5 ms (Ex7), 0,2 ms (d),
moins de 0,01 ms (a, b, c).

## Suite complète

| Partie | Suite Python | Suite de pages | Date |
|---|---|---|---|
| P0 | 1052 passés, 66 xfail (659 s) | 116 passés (885 s) ; code de retour 0 | 02.11.2026 |
| P1 | 1062 passés, 61 xfail (641 s) | 116 passés (871 s) ; code de retour 0 (3ᵉ lancement, voir Écarts) | 03.11.2026 |
| P1 (contrôle du chef d'orchestre) | 1062 passés, 61 xfail (643 s) | 115 passés, 1 échec : `test_clavier.py::test_a_deux_formules…` (le test instable, voir Écarts) ; ce test seul sur P0 (5eadf34, sans P1) dans un arbre séparé : 1 échec sur 6 → défaut préexistant, P1 acceptée | 03.11.2026 |
| P2 | 1071 passés, 55 xfail (655 s) | 116 passés (880 s) ; code de retour 0 (2ᵉ lancement : le 1ᵉʳ a échoué sur `test_soc07_etapes`, adapté aux intertitres, voir Écarts) | 03.11.2026 |
| P2 (contrôle du chef d'orchestre) | 1071 passés, 55 xfail (649 s) | 116 passés (865 s) ; code de retour 0 | 03.11.2026 |
| P3 | 1091 passés, 48 xfail (637 s) | 116 passés (870 s) ; code de retour 0 (2ᵉ lancement : le 1ᵉʳ a échoué sur `test_resoudre_import`, liste de fichiers mise à jour, voir Écarts) | 03.11.2026 |

## Écarts acceptés

- P0 : le test du corpus est écrit en fonctions pytest (et non en `unittest.TestCase` comme les autres) : `parametrize` permet une marque xfail
  par fonction du corpus, donc de ne marquer que les cas qui échouent vraiment.
- P1 (D17) : b s'écrit `−2(x − 3)(x + 2)e^{−2x}` et non `−2e^{−2x}(x − 3)(x + 2)` comme le corrigé : déplacer l'exponentielle devant des
  facteurs polynomiaux changerait toutes les dérivées de la forme `P(x)·e^{u}` de l'outil Dérivée (x(x + 2)eˣ deviendrait xeˣ(x + 2)).
  L'exponentielle ne passe devant que le facteur somme qui la contient (c : `2eˣ(3 − eˣ)`).
- P1 (D7) : le facteur négatif est entre parenthèses, mais sans « · » : `(x² − 6)(−2e^{−2x})` (convention de `tex` pour un produit de
  parenthèses, déjà utilisée par l'outil : `(2x + 1)(6x − 12)`), et non `(x² − 6)·(−2e^{−2x})` comme decisions.md D7.
- P1 : **test instable hors chantier** `tests/pages/test_clavier.py::test_a_deux_formules…` (page Limites, qui ne charge pas l'outil Dérivée) :
  le premier appui sur « effacer » laisse parfois `(x^2-1)/(x-3)` dans le champ. Il a fait échouer les 2 premières suites complètes ; lancé seul,
  il échoue 2 fois sur 4 avec P1 et **2 fois sur 6 sur `HEAD` (P0, sans P1)** : défaut préexistant, non corrigé ici (aucun test affaibli).
  Le 3ᵉ lancement de la suite complète est vert (code de retour 0). À traiter dans un chantier « clavier » (cause non trouvée : sur 5 essais
  instrumentés, le toucher arrive bien au bouton).

- P2 : `docs/choix-techniques.md` (description du format de sortie et du rendu commun) reçoit une ligne pour le nouveau style de carte
  `partie` : sans elle, la documentation du format serait fausse. `parties.py` n'est pas créé à P2 (aucune partie n'a encore de contenu
  propre à l'EC) : la spécification l'annonce pour P4, avec sa déclaration dans `moteur/manifeste.json`.
- P2 : `tests/pages/test_comportement.py::test_soc07_etapes` (« Étape suivante révèle exactement une carte ») comptait toutes les cartes
  cachées, intertitres compris : il échouait sur l'EC (19 cachées pour 14 étapes). Il compte maintenant les cartes cachées hors intertitres
  et vérifie **en plus** qu'un intertitre n'est jamais la dernière carte visible ; pour les autres outils, rien ne change.
- P3 : `tests/python/test_resoudre_ec.py` suit la nouvelle partie 1 : l'ordre attendu des cartes est maintenant calculé depuis
  l'analyse de l'outil ED (une carte « Condition k » par condition, « Mise en forme » quand `parties.mise_en_forme` en donne une,
  « Ensemble de définition ») au lieu de la seule carte « Fonction » : vérification plus forte. La ligne « ED = ]0 ; +∞[ » de la carte
  « Fonction » de ln(x)/x est vérifiée dans la carte « Ensemble de définition » (encadrée) ; nouveau test : ED et conditions identiques
  à l'outil ED (EC-01).
- P3 : `moteur/noyau.py` réexporte `conditions` (liste (genre, arbre) des conditions d'existence, celle qu'utilise l'analyse), pour que
  `parties.py` n'importe que du noyau (`test_noyau.py`) ; `ensemble_def.py` ne change pas. Ex7 et d entrent dans `CAS_LIMITES` de l'EC
  (`tests/python/cas.py`, cités dans la spécification) : aucune entrée des pages n'a de carte « Mise en forme », et sans eux elle
  n'aurait ni instantané ni rendu de page testé (P9 les mettra dans les exemples, D18).
- P3 : `tests/python/test_resoudre_import.py` (import à plat de l'EC avec les fichiers d'une page) reçoit les deux fichiers ajoutés au
  manifeste (`resoudre_ed.py`, `parties.py`) : même vérification, liste à jour (1ᵉʳ lancement de la suite complète en échec sur ce point).

## Questions pour l'enseignant

1. **Notation scientifique des valeurs approchées (P5, P7b)** : decisions.md §2 écrit `4,5·10⁻⁴` (2 chiffres significatifs, point médian) ; R13
   écrit `3,162 × 10⁻⁵` (×, 4 chiffres) et passe aussi en notation scientifique dès 10⁶ (decisions.md n'en dit rien). decisions.md dit « R13
   l'emporte » : c'est ce qui sera appliqué. Aucune valeur du corpus n'est concernée (le test d'arrondi refuse ce cas tant qu'il n'est pas tranché).
2. **Valeur approchée d'un entier exact** : (ln 3 ; 9) ≈ (1,10 ; 9) dans decisions.md §5 c ; j'en déduis qu'une valeur exacte entière s'écrit telle
   quelle (9, pas 9,00), y compris f(0) = 1, −6, 5. À confirmer.
3. **Critère §3 « AH visible »** : un x visible où |f(x) − L| < 5 % de la hauteur. Pris tel quel, il est satisfait par Ex7 grâce à la branche qui
   file vers 0 en 2⁻ (ce n'est pas l'AH). Le test cherche donc ce x **du côté de l'asymptote, au-delà de tous les points à montrer et des valeurs
   interdites**. Avec cette lecture, Ex7 échoue (P8) mais c passe, bien que l'audit dise que l'AH gauche de c ne se voit pas : la fenêtre de c va
   de −51 à 21 en y, et 5 % de la hauteur font 3,6. Faut-il un critère plus serré (par exemple 5 % de la valeur max |f| des points à montrer) ?
4. **« (x²)′ = 2x » parasite (D7)** : retiré pour Ex7 (la ligne n'a rien à voir avec u′, qui est un quotient). Dans a, b et d, la même ligne
   justifie u′ : elle n'est pas testée et reste. Le test est rattaché à P7a (réécriture de la dérivée de l'exposant) plutôt qu'à P1.

5. **P1, écriture −e^{−1} (D17)** : la règle « 3e^{−6} et non 3/e⁶ » est appliquée à tout extremum de la forme *entier × e^{−k}* :
   −1/e devient −e^{−1}, −3/e devient −3e^{−1}, 4/e² devient 4e^{−2} (outils Dérivée et EC). Un coefficient non entier garde l'écriture de
   SymPy (−1/(2e)). Faut-il garder 1/e et −1/e (coefficient ±1) en fraction ?
6. **P1, ln(x)/x (D17)** : la règle « signe dans le facteur non polynomial » donne aussi f′(x) = (1 − ln x)/x² au lieu de −(ln x − 1)/x²
   (une ligne « −1 » de moins dans le tableau de signes). La justification du zéro devient « 1 − ln(x) = 0 ⇔ ln(x) = 1 (on isole ln(x) du côté
   où son coefficient est positif) », phrase existante du moteur, au lieu de « (on ajoute 1) ». À relire.
7. **P2, partie 5 sans dérivée** : quand la dérivée sort du cadre de l'outil, l'Étude complète n'affichait aucune carte de dérivée (l'outil
   Dérivée affiche « Cette fonction sort du cadre de l'outil : la dérivée n'a pas été calculée. »). L'intertitre « 5. Dérivée, tableau de
   variation, extremums » reste alors seul (option qui affiche le moins). Faut-il y mettre la phrase de l'outil Dérivée ? Aucune fonction du
   corpus ni des exemples n'est concernée.
8. **P2, « 6. Graphe » puis la carte « Graphique »** : le titre de la carte répète l'intertitre. Gardé tel quel (titre de la carte du
   graphique, attendu par les tests de pages) ; à revoir en P8 si vous préférez une carte sans titre.
9. **P2, parties 2 et 3 vides** : jusqu'à P4 et P5, l'élève voit les intertitres « 2. Parité » et « 3. Zéros, signe, ordonnée à
   l'origine » sans rien dessous (un clic sur « Étape suivante » montre d'un coup 2, 3, 4 et la première carte des limites). Ne pas
   fusionner la branche dans cet état sans P4 et P5.

10. **P3, quand afficher la carte « Mise en forme »** : seulement si f(x) = e^{haut/bas}, haut et bas de degré ≥ 1 écrits développés, et
    si l'un des deux se factorise (mise en évidence de c·xᵏ, Somme-Produit à racines entières). d n'en a pas (haut constant, comme le
    .tex) ; f = P(x)·e^{…}, un exposant non rationnel, un coefficient dominant négatif ou un trinôme à racines non entières non plus
    (option qui affiche le moins). Faut-il l'étendre (par exemple nommer g(x) même sans factorisation) ?
11. **P3, chaîne courte limitée** aux dénominateurs affines et ax² + c : un autre trinôme garde la rédaction de l'outil ED (Δ et zéros),
    par exemple x² − 3x + 2. Voulez-vous aussi « x² − 3x + 2 = 0 ⇔ (x − 1)(x − 2) = 0 (Somme-Produit) ⇔ x = 1 ou x = 2 » ?
12. **P3, « On résout … »** : écrit comme decisions.md §4 et le .tex, alors que R10 (outil ED) a retiré « On résout » (« condition ⇔
    solution »). L'inégalité de l'outil ED reste au-dessus (« 6x − 12 ≠ 0 »). À confirmer.
13. **P3, conclusion de l'outil ED reprise telle quelle** : pour ln(x)/x, « ED = ]0 ; +∞[ = ]0 ; +∞[ » (l'intersection des deux
    conditions est déjà ]0 ; +∞[ ; même écriture dans l'outil ED). Gardée pour que l'ED soit celui de l'outil ED (EC-01) ; à corriger
    dans l'outil ED si vous le souhaitez.
14. **P3, Somme-Produit aussi pour a² − b²** : x² − 9 = (x + 3)(x − 3) (Somme-Produit), facteurs par racine croissante, alors que R10
    (outil ED) factorise a² − b² directement. Une seule méthode pour tous les trinômes unitaires (principe 6) ; à confirmer.

## À relire par l'enseignant

- P0 : rien (aucun changement du moteur, aucun instantané modifié).
- **P1** (outil Dérivée, donc aussi EC). Instantanés modifiés : `tests/python/instantanes/{derivee-variations,etude-complete}.json`,
  `tests/python/instantanes/resoudre/{derivee-variations,etude-complete}.json`, `tests/pages/references/{derivee-variations,etude-complete}.json`.
  Aucun autre outil ne change (ED, Limites, Factorisation, Exp/Log : instantanés identiques).

  | Entrée | Avant | Après |
  |---|---|---|
  | `ln(x)/x` (Dérivée, EC) | f′(x) = −(ln(x) − 1)/x² ; tableau : lignes −1, (ln(x) − 1), x² ; « ln(x) − 1 = 0 ⇔ ln(x) = 1 (on ajoute 1) » | f′(x) = (1 − ln(x))/x² ; tableau : lignes (1 − ln(x)), x² ; « 1 − ln(x) = 0 ⇔ ln(x) = 1 (on isole ln(x) du côté où son coefficient est positif) » |
  | `x*ln(x)` (Dérivée, EC) | minimum : f(e^{−1}) = −1/e | f(e^{−1}) = −e^{−1} |
  | `3(x*ln(x))` (Dérivée, EC) | minimum : f(e^{−1}) = −3/e | f(e^{−1}) = −3e^{−1} |
  | `x*ln(x)+x` (Dérivée) | minimum : f(e^{−2}) = −1/e² | f(e^{−2}) = −e^{−2} |
  | `x^2*e^(-x)` (Dérivée, EC) | maximum : f(2) = 4/e² | f(2) = 4e^{−2} |

  Hors instantanés, sur le corpus (tests du chantier) : Ex7 f′ = x(x − 4)e^{(x² + x − 2)/(6x − 12)}/(6(x − 2)²) (avant : trois
  exponentielles e^{−2/(6x−12)}e^{x/(6x−12)}e^{x²/(6x−12)}, et trois lignes d'exponentielles dans le tableau) ; b : ligne
  « 2xe^{−2x} + (x² − 6)(−2e^{−2x}) » (avant « (x² − 6) · −2e^{−2x} ») et maximum 3e^{−6} (avant 3/e⁶) ; c : « (eˣ)′ = eˣ » écrit une fois
  (avant deux), f′ = 2eˣ(3 − eˣ) (avant −2(eˣ − 3)eˣ), tableau : lignes 2, eˣ, (3 − eˣ).

- **P2** (EC seule ; l'outil Dérivée et l'outil Limites seuls ne changent pas : leur `etudier` reçoit un paramètre facultatif `analyse`,
  sans effet quand il est absent, et leurs instantanés sont identiques). Instantanés modifiés : `tests/python/instantanes/resoudre/etude-complete.json`
  (15 entrées) et `tests/pages/references/etude-complete.json` (16 entrées) ; `tests/python/instantanes/etude-complete.json` (sortie
  d'`etudier()`) est identique. Vérifié par programme : dans chaque entrée, mêmes cartes qu'avant (aucune n'est modifiée), dans un autre
  ordre, plus les six intertitres.

  | Entrée | Avant | Après |
  |---|---|---|
  | toutes (15) | Fonction · Dérivée · Signe de f′ et variations · [Tableaux de signes] · Limite… · Bilan des asymptotes · Graphique | **1. Domaine de définition** · Fonction · **2. Parité** · **3. Zéros, signe, ordonnée à l'origine** · **4. Limites et asymptotes** · [Tableaux de signes] · Limite… · Bilan des asymptotes · **5. Dérivée, tableau de variation, extremums** · Dérivée · Signe de f′ et variations · **6. Graphe** · Graphique |
  | page, au départ | 1 carte visible, « Étape 1 / n » | l'intertitre 1 et la carte « Fonction » visibles, « Étape 1 / n » (n inchangé : les intertitres ne comptent pas) |

- **P3** (EC seule ; outils ED, Dérivée, Limites, Exp-log : instantanés identiques). Instantanés modifiés :
  `tests/python/instantanes/resoudre/etude-complete.json` (15 entrées modifiées, 2 nouvelles : Ex7 et d) ;
  `tests/pages/references/etude-complete.json` (15 modifiées, 2 nouvelles) ; `tests/python/instantanes/etude-complete.json` (sortie
  d'`etudier()`) : 2 nouvelles entrées, aucune modifiée. Vérifié par programme : dans chaque entrée modifiée, tout ce qui suit
  « 2. Parité » est identique ; seule la partie 1 change (et le compteur d'étapes : + 1 à + 3).

  | Entrée | Avant (partie 1) | Après (partie 1) |
  |---|---|---|
  | toutes | Fonction : f(x) = … et « ED = … » (discret) | Fonction : f(x) = … seule · [Mise en forme] · Condition k (une carte par condition, badge) · Ensemble de définition : **ED = …** encadré |
  | `(x^2-1)/(x-3)` | ED = ℝ ∖ {3} | Condition 1 (dénominateur) : x − 3 ≠ 0 ; « On résout x − 3 = 0 ⇔ x = 3. » · ED = ℝ ∖ {3} |
  | `e^(1/x)`, `(e^x-1)/x` | ED = ℝ ∖ {0} | Condition 1 (dénominateur) : x ≠ 0 · ED = ℝ ∖ {0} |
  | `x/(x^2+1)` | ED = ℝ | Condition 1 : x² + 1 ≠ 0, lignes de l'outil ED (Δ = −4, ne s'annule jamais) · ED = ℝ |
  | `ln(x)/x` | ED = ]0 ; +∞[ | Condition 1 (logarithme) : x > 0 · Condition 2 (dénominateur) : x ≠ 0 · ED = ]0 ; +∞[ = ]0 ; +∞[ (question 13) |
  | `x*ln(x)`, `3(x*ln(x))`, `sqrt(x^2-4)`, `x/sqrt(x^2)` | ED = … | une carte de condition de l'outil ED (lignes et tableau tels quels) · ED encadré |
  | `e^(2x)`, `x^(2/3)`, `x^2*e^(-x)`, `x^2-4x+3`, `x^3-3x`, `x^4-2x^2` | ED = ℝ | « Ni logarithme, ni dénominateur, ni racine : aucune condition. » · ED = ℝ encadré |
  | `e^((x^2+x-2)/(6x-12))` (nouvelle, Ex7) | — | Mise en forme : x² + x − 2 = (x + 2)(x − 1) (Somme-Produit) ; 6x − 12 = 6(x − 2) (mise en évidence) ; On note g(x) = (x + 2)(x − 1)/(6(x − 2)), donc f(x) = e^{g(x)}. · Condition 1 : 6x − 12 ≠ 0 ; On résout 6x − 12 = 0 ⇔ 6x = 12 ⇔ x = 2. · ED = ℝ ∖ {2} |
  | `e^(2/(x^2-4))` (nouvelle, d) | — | Condition 1 : x² − 4 ≠ 0 ; On résout x² − 4 = 0 ⇔ x² = 4 ⇔ x = −2 ou x = 2. · ED = ℝ ∖ {−2 ; 2} |
