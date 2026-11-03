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
| P3 | Partie 1 : mise en forme + ED détaillé (D3) | EC | **fait** | f108f7f |
| P4 | Partie 2 : parité (D4) | EC | **fait** | 62781a8 |
| P5 | Partie 3 : zéros, signe, f(0) (D5) | EC | **fait** | 8fc2fa2 |
| P6 | Partie 4 : D12, D13, D16 | Limites | reportée (hors de la nuit du 02.11) | |
| P7a | Dérivée de l'exposant détaillée, tableau u/v (D7, D8, D7b si simple) | Dérivée | **fait** | |
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
- **P4 faite** : partie 2 (parité, D4) dans `parties.py` (`cartes_parite`, appelée par `resoudre` sur l'analyse en cache) : ED non
  symétrique (« −2 ∈ ED, mais 2 ∉ ED »), chaîne f(−x) une étape par ligne avec la propriété nommée (paire / impaire), sinon « Pas
  impaire » (f(0) ≠ 0 ou contre-exemple) et « Pas paire » (contre-exemple, valeurs exactes puis arrondies, arrondis différents).
  Chaque affirmation confirmée par SymPy et par une sonde mpmath (30 chiffres) ; sinon un message clair, sans conclusion. 5 xfail P4
  retirés ; instantanés de l'EC : partie 2 seule (liste sous « À relire ») ; questions 15 à 21 ; `etudier()` inchangé, parité 0,2 à 9 ms.
- **P5 faite** : partie 3 (D5) dans `parties.py` (`cartes_zeros_signe`) : « e^{…} > 0 pour tout x (une exponentielle est strictement
  positive) », f(x) = 0 en chaîne une étape par ligne avec la propriété nommée (« car e^{−2x} > 0 », « produit nul », Somme-Produit…),
  chaque zéro exact puis ≈, zéro hors de l'ED rejeté ; sans zéro et de signe constant « Donc f n'a pas de zéro et f(x) > 0 sur ED » ;
  sinon tableau de signes de f par la machinerie R7 du tableau de f′ (extraite en `derivee_variations.tableau_signes`, outil Dérivée
  inchangé) ; f(0) exact puis ≈ et le point, ou « 0 ∉ ED » ; zéros non exacts ou doute : message clair. Garde-fous SymPy (f(z) = 0,
  `solveset`, signe exact par intervalle) et sonde mpmath. 5 xfail P5 retirés ; instantanés de l'EC : partie 3 seule (liste sous « À
  relire ») ; largeurs 320/360/390 sans faute ; questions 22 à 30 ; `etudier()` inchangé, partie 3 de 5 à 61 ms.
- **P7a faite** (outil Dérivée, donc aussi EC) : tableau u | v / u′ | v′ (D8, nouveau bloc `uv`, composant commun `.uv` qui empile
  u, u′, v, v′ quand les colonnes ne tiennent pas) à la place de « On pose … » et des lignes u′, v′ ; facteur négatif entre
  parenthèses **avec** le point, (x² − 6)·(−2e^{−2x}) (écart de P1 résorbé) ; f = e^{u/v} (Ex7, d, e^(1/x)) : sous-carte « Dérivée de
  l'exposant » (règle du quotient, tableau, puis développement, réduction, mise en évidence, simplification par 6, une étape par
  ligne), sans « (x²)′ = 2x » parasite ; D7b fait (critère simple : produit de deux sommes de c·e^{kx}) : « On développe d'abord »
  eˣ(6 − eˣ) = 6eˣ − eˣ · eˣ = 6eˣ − e^{2x}. f′ inchangée ; chaque ligne vérifiée (SymPy et sonde), sinon rédaction habituelle.
  4 xfail P7a retirés (3 tests) ; 9 entrées de la Dérivée et 11 de l'EC modifiées (carte « Dérivée » seule, liste sous « À relire ») ;
  questions 31 à 39 ; temps : Ex7 0,64 s (+ 8 %), autres inchangés.

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

### P4 (03.11.2026)

Partie 2 de l'EC (D4), tout dans `etude-complete/parties.py` (`cartes_parite`, appelée par `resoudre_ec` sur l'analyse en cache : aucun
nouveau calcul de l'ED, D19) ; les autres outils ne changent pas. Toute affirmation est confirmée deux fois (principe 0.2) : SymPy exact
et une sonde mpmath (évaluation de l'arbre à 30 chiffres, écrite dans `parties.py` : `evaluer` est en flottants) ; au moindre doute, un
message clair et aucune conclusion.
1. **ED non symétrique (règle 1)** : comparaison exacte des intervalles de l'ED et de leurs symétriques (bornes rationnelles, sinon SymPy ;
   une borne approchée = doute). Point a : d'abord le symétrique d'une borne rationnelle (Ex7 : « −2 ∈ ED, mais 2 ∉ ED »), sinon 1, 2, 1/2,
   3… ; appartenance exacte, puis sonde (f(a) définie, f(−a) non définie). Une carte « Symétrie de l'ED », conclusion « ni paire ni impaire ».
2. **ED symétrique** : carte « Symétrie de l'ED » (« ED est symétrique par rapport à 0. »), puis la sonde classe f (paire, impaire, ni
   l'une ni l'autre, doute) sur des points de l'ED.
   - Paire ou impaire : confirmée par SymPy (f(−x) ∓ f(x) se simplifie en 0) ; carte « Calcul de f(−x) », une étape par ligne :
     substitution « (on remplace x par −x) », puis la forme simplifiée avec la propriété (« car (−x)² = x² », « règle des signes » pour
     les signes), pour une fonction impaire somme « −(…) (mise en évidence de −1) », enfin « = f(x) » ou « = −f(x) » ; chaque ligne est
     vérifiée (SymPy et sonde). La chaîne n'est écrite que si la parité se lit sur l'arbre (puissances de x, sommes, produits, quotients,
     exp/ln/√ d'une expression paire) ; sinon message clair.
   - Ni l'une ni l'autre (règle 3) : carte « Pas impaire » (f(0) ≠ 0 en valeur exacte si 0 ∈ ED et f(0) ≠ 0, sinon contre-exemple
     f(−a) ≠ −f(a)), carte « Pas paire » (contre-exemple f(−a) ≠ f(a)), a dans 1, 2, 1/2, 3, 4, 1/3, 5 avec ±a ∈ ED ; valeurs exactes
     (f(a) écrit par substitution et calcul des constantes rationnelles, vérifié égal à la valeur SymPy et à la sonde), puis approchées
     (decisions.md §2 ; entier exact sans « ≈ ») ; les deux valeurs arrondies affichées doivent différer, sinon a suivant, sinon message.
3. `resoudre_ec` : cartes de la partie 2 sous l'intertitre « 2. Parité ».
4. Tests : xfail P4 retirés ; `test_parties_ec.py` (cartes exactes du corpus et des entrées de la page, oracle mpmath de `tests/python/
   oracle.py` pour les valeurs et la parité, garde-fous forcés : sonde ou SymPy en désaccord, arrondis égaux, SymPy absent) ;
   `test_resoudre_ec.py` suit les nouvelles cartes. Instantanés `resoudre` et références de pages de l'EC régénérés (liste sous « À
   relire ») ; largeurs ; suite complète ; temps natif (et coût de la parité, calculée hors d'`etudier()`) ; commit « EC P4 : … ».

### P5 (03.11.2026)

Partie 3 de l'EC (D5), dans `etude-complete/parties.py` (`cartes_zeros_signe`, appelée par `resoudre_ec` sur l'analyse en cache, D19).
Le tableau de signes de f réutilise la machinerie R7 du tableau de f′ : le bloc de `derivee_variations.etudier` qui construit les points
critiques, les lignes de facteurs et la ligne combinée devient la fonction publique `tableau_signes(expr, Z, D, ED, étiquette, c, facteurs)`,
appelée par `etudier` (sortie de l'outil Dérivée inchangée : instantanés identiques) et par la partie 3 (étiquette « f(x) »).
1. **Exponentielle** : chaque facteur e^{…} de f (`aplatir`) donne « e^{…} > 0 pour tout x (une exponentielle est strictement
   positive) ; il ne s'annule jamais. » (« x ∈ ED » si ED ≠ ℝ ; f = e^{…} seule : phrase de decisions.md §4, « e^{g(x)} » si g est nommé).
2. **Zéros** : chaque autre facteur du numérateur résolu par le moteur de l'outil ED (`preimage`) ; chaîne une étape par ligne, la
   propriété nommée (« car e^{−2x} > 0 », « numérateur nul », « produit nul » avec les facteurs menés ensemble ; polynômes : chaîne courte
   de la partie 1, mise en évidence et Somme-Produit ; autres facteurs : lignes « A ⇔ B (propriété) » de l'outil ED enchaînées) ; dernière
   étape : chaque zéro exact puis ≈ ; zéro hors de l'ED rejeté ; forme non couverte : lignes de l'outil ED ; zéro approché ou non calculé :
   message clair, pas de tableau.
3. **Signe** : sans zéro et de signe constant, « Donc f n'a pas de zéro et f(x) > 0 sur ED. » ; sinon carte « Signe de f » (tableau).
   Garde-fous (principe 0.2) : SymPy (f(z) = 0 ; `solveset` ne donne aucun autre zéro dans l'ED ; signe exact en un point rationnel de
   chaque intervalle ; appartenance à l'ED exacte) et sonde mpmath (f(z) ≈ 0 ; signe en 9 points de chaque intervalle) ; sinon message.
4. **Ordonnée à l'origine** : f(0) exact (substitution calculée, comme P4) puis ≈, « g(0) = −2/(−12) = 1/6, donc f(0) = e^{1/6} » quand
   g est nommé, puis le point ; « 0 ∉ ED : le graphe ne coupe pas l'axe des y » ; ≈ : decisions.md §2 et R13 (questions 1 et 2).
5. Tests : xfail P5 retirés ; `test_parties_ec.py` (cartes exactes du corpus et des entrées de la page, oracle mpmath de `oracle.py` pour
   les zéros, le signe et f(0), famille au hasard, garde-fous forcés) ; `test_resoudre_ec.py` suit les nouvelles cartes ; spécification.
   Instantanés `resoudre` et références de pages de l'EC régénérés (liste sous « À relire ») ; largeurs 320/360/390 ; suite complète ;
   temps natif (et coût de la partie 3) ; commit « EC P5 : … ».

### P7a (03.11.2026)

Outil Dérivée (`derivee-variations/derivee_variations.py`, `resoudre_dv.carte_derivee`), donc aussi l'EC (portée EC + Dérivée) ; f′ ne
change pas (même calcul, même écriture de `deriv_tex`), seules les étapes de la carte « Dérivée » changent.
1. **D8, tableau u, v / u′, v′** : nouveau bloc `uv` du format de sortie (`sortie.uv`, `valider`), rendu par `commun/rendu.js` en deux
   colonnes (u, u′) | (v, v′) ; composant commun `.uv` dans `commun/composants.css` : si les deux colonnes ne tiennent pas côte à côte, la
   colonne v passe sous la colonne u (u, u′, v, v′ empilés, par retour à la ligne, aucune largeur en pixels). Règle du produit et du
   quotient (premier niveau) : « On applique la règle du produit, (uv)′ = u′v + uv′, avec : », le tableau, les justifications des
   dérivées (R11), puis la ligne f′ ; les phrases « On pose u(x) = … et v(x) = … » et « u′(x) = … », « v′(x) = … » disparaissent.
2. **D7, parenthèses avec le point** : dans la ligne u′v ± uv′, un facteur négatif à droite d'un produit s'écrit `(x² − 6)·(−2e^{−2x})`
   (`_tex_brut`, partout ailleurs l'écriture de `tex`) : l'écart de P1 est résorbé.
3. **D7, dérivée de l'exposant** : f = e^{g(x)}, g = u/v avec u et v polynômes écrits développés à coefficients entiers, v non constant
   (Ex7, d, e^(1/x)). Une phrase « f(x) = e^{g(x)} avec g(x) = …, donc f′(x) = g′(x)·e^{g(x)} (dérivée d'une composée) », puis la
   sous-carte « Dérivée de l'exposant » (bloc `sous_calcul` existant) : étape « règle du quotient » (formule, tableau u/v, ligne
   g′(x) = …), étape « calcul du numérateur, puis simplification » (développement terme à terme, réduction, mise en évidence de c·xᵏ,
   simplification par le pgcd avec le coefficient du dénominateur (6x − 12)² = 36(x − 2)²), une étape par ligne ; puis « On remplace
   g′(x) dans f′(x) = g′(x)·e^{g(x)} : » et f′ encadré. Plus de « (x²)′ = 2x » parasite. Garde-fous : chaque ligne égale à la précédente
   (SymPy et sonde en 7 points), la dernière égale à g′ (SymPy `diff` et différence centrée), g′·e^{g} égale à f′ ; sinon la rédaction
   actuelle. Exposant polynôme (a : −x²) : rédaction actuelle (le .tex n'a pas de sous-carte).
4. **D7b, développer d'abord** (critère simple et sûr, donc fait) : f = A·B, A et B sommes de c·e^{kx} (k entier ≥ 1) et de constantes
   entières, une exponentielle dans chacun, une somme dans l'un : « On développe d'abord (c'est plus simple à dériver) : », f(x) = eˣ(6 − eˣ)
   = 6eˣ − eˣ · eˣ (développement) = 6eˣ − e^{2x} (réduction), puis la dérivée de la somme. Garde-fous : SymPy et sonde, et la dérivée
   de la forme développée doit s'écrire exactement comme f′ ; sinon la rédaction actuelle.
5. Tests : xfail P7a retirés ; `test_derivee_narration.py` (lignes exactes Ex7, d, c, b ; famille d'exposants u/v tirés au hasard dont
   chaque ligne affichée, relue et évaluée en mpmath, égale g′ ; cas laissés à la rédaction actuelle ; garde-fous forcés) ; les tests
   qui lisaient `it["html"]` lisent tout le texte de l'étape (`moteurs.texte_etape`, tableau et sous-carte compris) ; `test_sortie.py`
   (bloc `uv`), `test_composants.py` (`.uv`), `test_largeurs.py` (tableau u/v et sous-carte à 320–1100 px : rien ne déborde, colonnes
   alignées côte à côte, empilées dans l'ordre u, u′, v, v′ quand elles ne tiennent pas). Instantanés Dérivée et EC régénérés (moteur,
   `resoudre`, références de pages), listés sous « À relire » ; spécification de l'outil Dérivée ; suite complète ; temps natif ; commit.

## Temps natif de etudier() (s, médiane de 3 processus neufs)

| Partie | Ex7 | a | b | c | d |
|---|---|---|---|---|---|
| P0 | 0,59 | 0,02 | 0,42 | 0,18 | 0,30 |
| P1 | 0,63 | 0,02 | 0,42 | 0,19 | 0,30 |
| P2 | 0,60 | 0,02 | 0,43 | 0,18 | 0,32 |
| P3 | 0,59 | 0,02 | 0,42 | 0,19 | 0,30 |
| P4 | 0,60 | 0,02 | 0,43 | 0,18 | 0,29 |
| P5 | 0,59 | 0,02 | 0,43 | 0,19 | 0,29 |
| P7a | 0,64 | 0,02 | 0,42 | 0,20 | 0,31 |

P3 ne touche pas `etudier()` ; la partie 1 (`parties.cartes_domaine`, appelée par `resoudre`) coûte en plus 0,5 ms (Ex7), 0,2 ms (d),
moins de 0,01 ms (a, b, c).
P4 ne touche pas `etudier()` ; la partie 2 (`parties.cartes_parite`, appelée par `resoudre`, SymPy déjà chargé, médiane de 3 processus
neufs) coûte en plus 0,2 ms (Ex7 : ED non symétrique, sans SymPy), 4,8 ms (a), 7,2 ms (b), 8,6 ms (c), 6,2 ms (d).
P5 ne change pas la sortie d'`etudier()` (le tableau de f′ passe par `tableau_signes`, même calcul) ; la partie 3
(`parties.cartes_zeros_signe`, appelée par `resoudre`, SymPy déjà chargé, médiane de 3 processus neufs) coûte en plus 43 ms (Ex7),
5 ms (a), 61 ms (b), 44 ms (c), 27 ms (d) : surtout `solveset` et `simplify` (garde-fous du principe 0.2). Coût sous Pyodide à
mesurer en P9.
P7a : la rédaction D7 / D7b est calculée dans `etudier()` (outil Dérivée) : + 58 ms (Ex7, sous-carte) et + 16 ms (c, développement),
surtout les preuves SymPy de chaque ligne. Une première version (preuve par `simplify`) donnait Ex7 0,77 s et c 0,37 s (+ 95 %) ; la
preuve passe maintenant d'abord par `cancel(expand(…))` (exacte, rapide), `simplify` seulement si elle ne conclut pas.

## Suite complète

| Partie | Suite Python | Suite de pages | Date |
|---|---|---|---|
| P0 | 1052 passés, 66 xfail (659 s) | 116 passés (885 s) ; code de retour 0 | 02.11.2026 |
| P1 | 1062 passés, 61 xfail (641 s) | 116 passés (871 s) ; code de retour 0 (3ᵉ lancement, voir Écarts) | 03.11.2026 |
| P1 (contrôle du chef d'orchestre) | 1062 passés, 61 xfail (643 s) | 115 passés, 1 échec : `test_clavier.py::test_a_deux_formules…` (le test instable, voir Écarts) ; ce test seul sur P0 (5eadf34, sans P1) dans un arbre séparé : 1 échec sur 6 → défaut préexistant, P1 acceptée | 03.11.2026 |
| P2 | 1071 passés, 55 xfail (655 s) | 116 passés (880 s) ; code de retour 0 (2ᵉ lancement : le 1ᵉʳ a échoué sur `test_soc07_etapes`, adapté aux intertitres, voir Écarts) | 03.11.2026 |
| P2 (contrôle du chef d'orchestre) | 1071 passés, 55 xfail (649 s) | 116 passés (865 s) ; code de retour 0 | 03.11.2026 |
| P3 | 1091 passés, 48 xfail (637 s) | 116 passés (870 s) ; code de retour 0 (2ᵉ lancement : le 1ᵉʳ a échoué sur `test_resoudre_import`, liste de fichiers mise à jour, voir Écarts) | 03.11.2026 |
| P3 (contrôle du chef d'orchestre) | 1091 passés, 48 xfail (634 s) | 116 passés (886 s) ; code de retour 0 | 03.11.2026 |
| P4 | 1113 passés, 43 xfail (631 s) | 116 passés (873 s) ; code de retour 0 (1ᵉʳ lancement) | 03.11.2026 |
| P4 (contrôle du chef d'orchestre) | 1113 passés, 43 xfail (629 s) | 116 passés (875 s) ; code de retour 0 | 03.11.2026 |
| P5 | 1136 passés, 38 xfail (662 s) | 116 passés (870 s) ; code de retour 0 (1ᵉʳ lancement) | 03.11.2026 |
| P5 (contrôle du chef d'orchestre) | 1136 passés, 38 xfail (657 s) | 116 passés (885 s) ; code de retour 0 | 03.11.2026 |
| P7a | 1149 passés, 34 xfail (643 s) | 117 passés (914 s, dont le nouveau test de largeurs du tableau u/v) ; code de retour 0 (1ᵉʳ lancement) | 03.11.2026 |

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
- P4 : `tests/python/test_resoudre_ec.py::test_ordre_des_cartes_comme_la_page` place sous « 2. Parité » les titres des cartes de
  `parties.cartes_parite` (comme « Mise en forme » à P3) : le reste de l'ordre est vérifié comme avant ; le contenu de la partie 2 est
  vérifié à part (`test_parties_ec.py` : cartes exactes, oracle mpmath, garde-fous ; `test_resoudre_place_la_parite_sous_son_intertitre`).
  La spécification `docs/specifications/etude-complete.md` décrit la partie 2 (sinon elle serait fausse : « 2 vide »).

- P5 : `derivee-variations/derivee_variations.py` : le bloc d'`etudier` qui construit les points critiques et le tableau de signes
  (R7) devient la fonction publique `tableau_signes` (et deux petites fonctions `_point_test`, `_zone_hors`), appelée par `etudier` et
  par la partie 3 de l'EC ; même calcul : instantanés de l'outil Dérivée et sortie d'`etudier()` de l'EC identiques.
- P5 : `parties.py` : `factorisation` (partie 1) s'appuie sur `_factoriser` (facteurs exposés pour la chaîne de la partie 3),
  `resolution_denominateur` sur `resolution_polynome`, `valeur_en` (partie 2) sur `valeur_verifiee` (partagée avec f(0)) : sorties
  inchangées (parties 1 et 2 des instantanés identiques). `plier` calcule aussi 1^p = 1 et 0^p = 0 (p > 0) : f(0) de x^(2/3) s'écrit
  « 0 » et non « ∛(0²) » ; aucune carte de parité des instantanés ne change.
- P5 : `tests/python/test_resoudre_ec.py::test_ordre_des_cartes_comme_la_page` place sous « 3. Zéros, signe, ordonnée à l'origine » les
  titres des cartes de `parties.cartes_zeros_signe` (comme la partie 2 à P4) : le reste de l'ordre est vérifié comme avant ; le
  contenu est vérifié à part (`test_parties_ec.py` : cartes exactes, oracle mpmath, garde-fous ; `test_resoudre_place_la_partie_3…`).
  La spécification décrit la partie 3 (sinon elle serait fausse : « 3 vide »).

- P7a : les tests qui lisaient le texte des étapes de la dérivée par `it["html"]` (`test_derivee_narration.py`,
  `test_proprietes_derivee.py`, `test_racines_reelles.py`, `test_derivee_exposant_irrationnel.py`) lisent maintenant tout le texte de
  l'étape (`moteurs.texte_etape` : html d'un texte, toutes les chaînes d'un tableau `uv` ou d'une sous-carte) : mêmes vérifications,
  étendues aux cases du tableau et aux lignes de la sous-carte (`test_racines_reelles` garde `get("html", "")` pour les étapes du signe,
  comme avant). `test_facteur_negatif_entre_parentheses` attend `(x² − 6) \cdot (−2e^{−2x})` (parenthèses et point, D7) au lieu de
  `(x² − 6)\,(−2e^{−2x})` : même force (le refus de `\cdot -` reste).
- P7a : `docs/specifications/derivee-variations.md` (point 2, « Dérivée ») décrit le tableau u/v, la sous-carte et le développement
  d'abord (sinon elle serait fausse). Le guide de rédaction (R11 : « u, u', v, v' sur une ligne ») n'est pas modifié : D8 (tableau) le
  remplace pour ces deux règles (question 32).
- P7a : l'écart de P1 « parenthèses sans point » est résorbé : `(x² − 6)·(−2e^{−2x})` (outil Dérivée et EC), par `_tex_brut`, qui
  n'écrit autrement que `tex` ; les autres produits gardent l'écriture de `tex` (`(2x + 1)(6x − 12)`, `(x² + x − 2)·6`).

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

15. **P4, « ≈ » hors de la formule** : « \(f(1) = −5e^{−2}\) ≈ −0,68 » ; la valeur approchée est écrite en texte (virgule, signe
    « − »), après la formule, et non dans la formule (« 0{,}68 ») comme les autres outils : le test du corpus (P0) la cherche telle
    quelle dans le texte. À l'écran, la police du « ≈ −0,68 » est celle du texte. Faut-il la passer dans la formule ?
16. **P4, cartes de la partie 2** : toujours une carte « Symétrie de l'ED » d'abord (« ED est symétrique par rapport à 0. », même pour
    ED = ℝ, que le .tex ne dit pas : même suite d'étapes pour toutes les fonctions, principe 6), puis « Calcul de f(−x) » ou « Pas
    impaire » et « Pas paire » ; la conclusion en gras (« Donc f est paire. ») à la fin de la dernière carte. La phrase « une fonction
    impaire vérifie f(0) = 0 » vient du .tex (c).
17. **P4, propriétés de la chaîne** : la 1ʳᵉ ligne porte « (on remplace x par −x) » (absent du .tex) ; les signes sont justifiés par
    « règle des signes » (x³ − 3x : « car (−x)³ = −x³ ; règle des signes »), une somme impaire passe par « −(x³ − 3x) (mise en
    évidence de −1) » avant « = −f(x) ». Les mots vous conviennent-ils ?
18. **P4, chaîne non rédigée** : quand la parité est confirmée (SymPy et sonde) mais ne se lit pas sur l'arbre (e^x + e^(−x),
    x^(1/3), (x³ − x)²), l'outil écrit « Le calcul de f(−x) n'a pas pu être rédigé par l'outil : la parité n'est pas traitée. » (option
    qui affiche le moins). Aucune entrée de la page ni du corpus n'est concernée.
19. **P4, valeurs des contre-exemples** : a est pris dans 1, 2, 1/2, 3, 4, 1/3, 5 ; une valeur hors de [10⁻³ ; 1000[ fait passer au a
    suivant (notation scientifique : question 1 ; séparateur des milliers ’ : pas encore dans l'EC) ; un entier exact s'écrit sans
    « ≈ » (question 2 : f(1) = 0, f(−1) = 8) ; un f(0) non entier s'écrit « f(0) = … ≠ 0 (≈ 0,61) ». L'écriture exacte est la
    substitution, constantes rationnelles calculées, sans autre simplification : (e^x − 1)/x donne f(−1) = −(e^{−1} − 1) (et non
    1 − e^{−1}).
20. **P4, point a d'un ED non symétrique** : d'abord le symétrique d'une borne rationnelle exclue (Ex7 : −2 ; (x² − 1)/(x − 3) : −3),
    sinon le premier de 1, −1, 2, −2, 1/2… (ln(x)/x : « 1 ∈ ED, mais −1 ∉ ED » ; √(x + 1) : « 2 ∈ ED, mais −2 ∉ ED »).
21. **P4, b : −36,95** : le .tex écrit f(−1) ≈ −36,9 ; decisions.md §5 écrit −36,95 (2 décimales, §2) : c'est −36,95 qui est affiché.

22. **P5, chaîne une étape par ligne** : decisions.md §2 écrit la résolution sur une ligne ; elle est écrite une étape par ligne
    (principe 5, comme la chaîne f(−x) de P4) : « (x² − 6)e^{−2x} = 0 », « ⇔ x² − 6 = 0 (car e^{−2x} > 0) », « ⇔ x² = 6 »,
    « ⇔ x = −√6 ≈ −2,45 ou x = √6 ≈ 2,45 ». La valeur approchée suit chaque zéro (et non « ≈ ±2,45 » en bout de chaîne) : une seule
    écriture pour un ou plusieurs zéros, symétriques ou non. À confirmer.
23. **P5, tableau de f avec les facteurs écrits** : le tableau prend les facteurs de f tels que saisis (machinerie R7) : x² − 4x + 3 a
    une seule ligne « x² − 4x + 3 » puis f(x), bien que la chaîne l'ait factorisé en (x − 1)(x − 3) (Somme-Produit). Faut-il une ligne
    par facteur de la factorisation de la chaîne ?
24. **P5, phrase de l'exponentielle** : écrite comme decisions.md §2 (« … strictement positive) ; il ne s'annule jamais. ») ; « pour
    tout x ∈ ED » quand ED ≠ ℝ (Ex7, d, e^(1/x)), « pour tout x » sinon ; f = e^{…} seule : phrase de §4 sans « il ne s'annule
    jamais », puis « Donc f n'a pas de zéro et f(x) > 0 sur ED. ».
25. **P5, propriétés ajoutées** (absentes de decisions.md) : « numérateur nul » (quotient : (x² − 1)/(x − 3) = 0 ⇔ x² − 1 = 0),
    « on divise par 3 » (3x ln x), « produit nul », « mise en évidence », « Somme-Produit », et celles de l'outil ED (« on ajoute 1 »,
    « on isole e^x du côté où son coefficient est positif »). Un zéro hors de l'ED : « x = 0 est rejeté, car 0 ∉ ED. ». Les mots
    vous conviennent-ils ?
26. **P5, formes que la chaîne ne couvre pas** (√(x² − 4), x² + 1, x³ − 12x² + 44x − 48, trinôme à Δ non carré) : les lignes de
    l'outil ED telles quelles (« On résout … », Δ, « Solutions : … »), puis « Donc x = −2 ou x = 2. ». Faut-il une autre rédaction ?
27. **P5, le point (0 ; f(0))** : « Le graphe coupe l'axe des y au point (0 ; e^{1/6}). » (le .tex écrit « Point (0 ; e^{1/6}) ») :
    phrase symétrique de « 0 ∉ ED : le graphe ne coupe pas l'axe des y » (decisions.md §2).
28. **P5, valeurs approchées** : R13 appliqué (question 1) : notation scientifique sous 10⁻³ et dès 10⁶ (« ≈ 4,540 × 10⁻⁵ ») ; entre
    1000 et 10⁶, aucune valeur approchée (la valeur exacte seule, option qui affiche le moins) tant que le séparateur des milliers
    n'est pas tranché pour l'EC (question 19). Aucune valeur du corpus n'est concernée.
29. **P5, après le tableau** : aucune phrase de conclusion (« f(x) > 0 sur … ; f(x) < 0 sur … ») : le tableau la porte (option qui
    affiche le moins). En voulez-vous une ?
30. **P5, sans zéro mais avec changement de signe** (e^x/x, 1/x, x/√(x²)) : « Donc f n'a pas de zéro. » puis le tableau (decisions.md
    ne prévoit la phrase « f(x) > 0 sur ED » sans tableau que pour un signe constant).

31. **P7a, quand la sous-carte « Dérivée de l'exposant »** : seulement si f = e^{u/v}, u et v polynômes écrits développés à
    coefficients entiers, v non constant (Ex7, d, e^(1/x)). Un exposant polynôme (a : −x², e^(x²)) garde la phrase « de la forme e^u »
    (le .tex de a n'a pas de sous-carte) ; e^(−1/x) aussi (la règle du quotient donnerait « −(−1) »), de même un exposant non développé
    ((x + 1)²/(x − 1)), à coefficient non entier, ou f = P(x)·e^{u/v} (option qui affiche le moins). Faut-il l'étendre ?
32. **P7a, place du tableau u/v** : « On applique la règle du produit, (uv)′ = u′v + uv′, avec : », le tableau, puis les justifications
    des dérivées (R11 : « (x²)′ = 2x (règle de la puissance) », « e^{−2x} est de la forme e^u avec u(x) = −2x … »), puis la ligne f′.
    Le nom u de la phrase « de la forme e^u » n'est pas le u du tableau (comme avant P7a, où « On pose u(x) = x² − 6 » précédait la
    même phrase). Le guide (R11) dit encore « u, u', v, v' sur une ligne » : à mettre à jour si le tableau vous convient.
33. **P7a, forme finale de g′** : la chaîne s'arrête après la simplification par le pgcd (mise en évidence de c·xᵏ seulement, pas de
    Somme-Produit) : d donne g′(x) = −4x/(x² − 4)² (comme le .tex), mais f′ encadré garde l'écriture factorisée de l'outil,
    −4x·e^{…}/((x − 2)²(x + 2)²). De même, x² − 6x + 1 ou 2x² − 8x + 5 restent tels quels.
34. **P7a, résultat encadré** : la ligne « On remplace g′(x) dans f′(x) = g′(x)·e^{g(x)} : » précède le résultat encadré habituel
    f′(x) = x(x − 4)e^{g}/(6(x − 2)²) (écriture de l'outil, une seule exponentielle, avec l'exposant écrit en entier), et non
    « f′(x) = x(x − 4)/(6(x − 2)²) · e^{g(x)} » du .tex : changer l'écriture de f′ changerait la ligne des zéros et le tableau de signes.
35. **P7a, mots de la sous-carte** : étapes « Étape 1 : règle du quotient. » et « Étape 2 : calcul du numérateur, puis
    simplification. » (rendu du bloc `sous_calcul` des limites) ; propriétés « (règle du quotient) », « (développement) » — « (calcul) »
    quand aucun produit de sommes n'est développé (d : −2·2x = −4x) —, « (réduction) », « (mise en évidence) », « (simplification par
    6) » ; dénominateur (6x − 12)² écrit 36(x − 2)² dès la ligne du développement (decisions.md §4 ; (−6x − 18)² = 36(x + 3)²). La
    phrase d'entrée nomme g(x) = (x² + x − 2)/(6x − 12) (écrit développé), alors que la carte « Mise en forme » de l'EC le nomme sous
    forme factorisée.
36. **P7a, D7b** : après le développement, la dérivée de la somme suit la rédaction habituelle (« (6eˣ)′ = 6·(eˣ)′ = 6eˣ », phrase de
    e^{2x}, puis « f′(x) = 2eˣ(3 − eˣ) ») ; la ligne du .tex « f′(x) = 6eˣ − 2e^{2x} = 2eˣ(3 − eˣ) (on a mis 2eˣ en évidence) »
    n'est pas écrite (changement de la rédaction de toutes les sommes de l'outil). Critère : f = produit de deux sommes de c·e^{kx}
    (k ≥ 1 entier) et de constantes entières, une exponentielle dans chacune ; e^{−x}(eˣ + 1), (eˣ + 1)², eˣ(eˣ + x) gardent la
    rédaction habituelle.
37. **P7a, écart à D6 vu en passant (non corrigé, hors corpus)** : l'exposant de f′ n'est pas toujours celui de l'énoncé :
    e^((x² + 1)/(2x)) donne f′ avec e^{(½x² + ½)/x}, et e^((−2x² + 3x − 1)/(3x − 6)) réordonne le haut (3x − 2x² − 1). Cela vient du
    `_simplifier` de P1 (SymPy) ; à corriger avec P7b ou à part ?
38. **P7a, « · » seulement devant un facteur négatif** : (x² − 6)·(−2e^{−2x}), x²·(−e^{−x}), (3x² + x − 3)·(−6) ; deux parenthèses
    positives restent côte à côte, (2x + 1)(6x − 12), comme dans l'outil.
39. **P7a, temps** : aucune hausse de plus de 50 % (Ex7 + 8 %, c + 5 %, d + 7 %).

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

- **P4** (EC seule ; aucun autre outil ne change : instantanés identiques, `etudier()` identique). Instantanés modifiés :
  `tests/python/instantanes/resoudre/etude-complete.json` (17 entrées modifiées) et `tests/pages/references/etude-complete.json`
  (17 modifiées ; l'entrée d'erreur `ln(` est identique). Vérifié par programme : dans chaque entrée, tout ce qui précède « 2. Parité »
  et tout ce qui suit « 3. Zéros, signe, ordonnée à l'origine » est identique ; seules les cartes de la partie 2 s'ajoutent (le compteur
  d'étapes augmente de 1 à 3).

  | Entrée | Avant (partie 2) | Après (partie 2) |
  |---|---|---|
  | toutes | intertitre seul | Symétrie de l'ED · [Calcul de f(−x)] ou [Pas impaire · Pas paire] |
  | `e^((x^2+x-2)/(6x-12))` (Ex7) | — | −2 ∈ ED, mais 2 ∉ ED : ED n'est pas symétrique par rapport à 0. Donc **f n'est ni paire ni impaire**. |
  | `(x^2-1)/(x-3)` | — | −3 ∈ ED, mais 3 ∉ ED : … ni paire ni impaire |
  | `ln(x)/x`, `x*ln(x)`, `3(x*ln(x))` | — | 1 ∈ ED, mais −1 ∉ ED : … ni paire ni impaire |
  | `e^(2/(x^2-4))` (d), `sqrt(x^2-4)`, `x^4-2x^2`, `x^(2/3)` | — | ED symétrique ; f(−x) = e^{2/((−x)² − 4)} (on remplace x par −x) = e^{2/(x² − 4)} (car (−x)² = x²) = f(x) ; **f est paire** (de même √((−x)² − 4), (−x)⁴ − 2(−x)², ∛((−x)²)) |
  | `x^3-3x` | — | f(−x) = (−x)³ − 3(−x) = −x³ + 3x (car (−x)³ = −x³ ; règle des signes) = −(x³ − 3x) (mise en évidence de −1) = −f(x) ; **f est impaire** |
  | `x/(x^2+1)`, `x/sqrt(x^2)` | — | f(−x) = (−x)/((−x)² + 1) = −x/(x² + 1) (car (−x)² = x² ; règle des signes) = −f(x) ; **f est impaire** |
  | `e^(2x)` | — | f(0) = 1 ≠ 0 : pas impaire ; f(1) = e² ≈ 7,39, f(−1) = e^{−2} ≈ 0,14 : pas paire |
  | `x^2-4x+3` | — | f(0) = 3 ≠ 0 ; f(1) = 0, f(−1) = 8 (entiers, sans ≈) |
  | `e^(1/x)` | — | 0 ∉ ED : f(1) = e ≈ 2,72, donc −f(1) ≈ −2,72 ; f(−1) = e^{−1} ≈ 0,37 : pas impaire ; même a pour « pas paire » |
  | `x^2*e^(-x)` | — | f(0) = 0 : contre-exemple f(1) = e^{−1} ≈ 0,37, −f(1) ≈ −0,37, f(−1) = e ≈ 2,72 ; pas paire avec le même a |
  | `(e^x-1)/x` | — | f(1) = e − 1 ≈ 1,72 ; f(−1) = −(e^{−1} − 1) ≈ 0,63 (question 19) |

  Hors instantanés (corpus) : b « f(0) = −6 ≠ 0 », « f(1) = −5e^{−2} ≈ −0,68 », « f(−1) = −5e^{2} ≈ −36,95 » ; c « f(0) = 5 ≠ 0 »,
  « f(1) = e(6 − e) ≈ 8,92 », « f(−1) = e^{−1}(6 − e^{−1}) ≈ 2,07 » ; a « f(−x) = e^{−(−x)²} = e^{−x²} (car (−x)² = x²) = f(x) ».
  Largeurs 320 / 360 / 390 px vérifiées à part (script de mesure de `test_largeurs.py`) pour 12 entrées dont Ex7, b, c, d, ln(x² + 1)/x
  et x² + x/1000 : aucune faute.

- **P5** (EC seule ; outil Dérivée : `tableau_signes` extrait d'`etudier`, instantanés identiques ; ED, Limites, Exp-log : identiques ;
  `tests/python/instantanes/etude-complete.json` (sortie d'`etudier()`) identique). Instantanés modifiés :
  `tests/python/instantanes/resoudre/etude-complete.json` (17 entrées modifiées) et `tests/pages/references/etude-complete.json`
  (17 modifiées ; l'entrée d'erreur `ln(` est identique). Vérifié par programme : dans chaque entrée, tout ce qui précède et suit la
  partie 3 est identique ; seules les cartes de la partie 3 s'ajoutent (2 ou 3 ; le compteur d'étapes augmente d'autant).

  | Entrée | Avant (partie 3) | Après (partie 3) |
  |---|---|---|
  | toutes | intertitre seul | [Zéros de f · Signe de f (tableau)] ou [Zéros et signe de f] · Ordonnée à l'origine |
  | `e^((x^2+x-2)/(6x-12))` (Ex7) | — | e^{g(x)} > 0 pour tout x ∈ ED (une exponentielle est strictement positive). Donc f n'a pas de zéro et f(x) > 0 sur ED. · g(0) = −2/(−12) = 1/6, donc f(0) = e^{1/6} ≈ 1,18. Le graphe coupe l'axe des y au point (0 ; e^{1/6}). |
  | `e^(2/(x^2-4))` (d), `e^(2x)`, `e^(1/x)` | — | même phrase (« pour tout x » si ED = ℝ) et « f(x) > 0 sur ED » ; f(0) = e^{−1/2} ≈ 0,61 (d), f(0) = 1 ; e^(1/x) : 0 ∉ ED : le graphe ne coupe pas l'axe des y |
  | `x^2*e^(-x)` | — | e^{−x} > 0 … ; il ne s'annule jamais. x²e^{−x} = 0 ⇔ x² = 0 (car e^{−x} > 0) ⇔ x = 0 · tableau x², e^{−x}, f(x) : + 0 + · f(0) = 0 |
  | `x^2-4x+3` | — | x² − 4x + 3 = 0 ⇔ (x − 1)(x − 3) = 0 (Somme-Produit) ⇔ x − 1 = 0 ou x − 3 = 0 (produit nul) ⇔ x = 1 ou x = 3 · tableau (une ligne x² − 4x + 3, question 23) · f(0) = 3 |
  | `x^3-3x`, `x^4-2x^2` | — | mise en évidence, produit nul, x² = 3 ⇔ x = −√3 ≈ −1,73 ou x = 0 ou x = √3 ≈ 1,73 (de même ±√2 ≈ ±1,41) · tableau · f(0) = 0 |
  | `(x^2-1)/(x-3)`, `x/(x^2+1)`, `ln(x)/x` | — | « ⇔ x² − 1 = 0 (numérateur nul) ⇔ x² = 1 ⇔ x = −1 ou x = 1 » (de même x = 0 ; ln(x) = 0 ⇔ x = 1) · tableau avec la valeur interdite (‖) et la zone hors de l'ED (hachurée) · f(0) = 1/3 ≈ 0,33 ; 0 ; 0 ∉ ED |
  | `x*ln(x)`, `3(x*ln(x))` | — | « ⇔ x = 0 ou ln(x) = 0 (produit nul) ⇔ x = 0 ou x = 1 », « x = 0 est rejeté, car 0 ∉ ED. » (3x ln x : « (on divise par 3) ») · tableau · 0 ∉ ED |
  | `(e^x-1)/x` | — | « ⇔ eˣ − 1 = 0 (numérateur nul) ⇔ eˣ = 1 (on ajoute 1) ⇔ x = 0 », x = 0 rejeté, « Donc f n'a pas de zéro et f(x) > 0 sur ED. » (pas de tableau) · 0 ∉ ED |
  | `x/sqrt(x^2)` | — | « ⇔ x = 0 (numérateur nul) », rejeté, « Donc f n'a pas de zéro. » · tableau − ‖ + (question 30) · 0 ∉ ED |
  | `sqrt(x^2-4)` | — | lignes de l'outil ED (« √(x² − 4) = 0 ⇔ x² − 4 = 0 », « On résout … », « Solutions : … »), « Donc x = −2 ou x = 2. » (question 26) · tableau + 0 (hachuré) 0 + · 0 ∉ ED |
  | `x^(2/3)` | — | « ∛(x²) = 0 ⇔ (∛x)² = 0 ⇔ ∛x = 0 ⇔ x = 0 » · tableau + 0 + · f(0) = 0 |

  Hors instantanés (corpus) : b « (x² − 6)e^{−2x} = 0 ⇔ x² − 6 = 0 (car e^{−2x} > 0) ⇔ x² = 6 ⇔ x = −√6 ≈ −2,45 ou x = √6 ≈ 2,45 »,
  tableau x² − 6, e^{−2x}, f(x) : + 0 − 0 +, f(0) = −6 ; c « eˣ(6 − eˣ) = 0 ⇔ 6 − eˣ = 0 (car eˣ > 0) ⇔ eˣ = 6 (on isole eˣ …) ⇔
  x = ln(6) ≈ 1,79 », tableau + 0 −, f(0) = 5 ; a « e^{−x²} > 0 pour tout x … Donc f n'a pas de zéro et f(x) > 0 sur ED », f(0) = 1.
  Largeurs 320 / 360 / 390 px vérifiées à part (mesure de `test_largeurs.py`, corrigé complet affiché) pour 18 entrées dont Ex7, a–d,
  x⁴ − 2x², ln(x)/x, √(x² − 4), (x² − 5)(x² − 7)e^{−x} (tableau à 4 zéros) : aucune faute.

- **P7a** (outil Dérivée, donc aussi EC). Instantanés modifiés : `tests/python/instantanes/{derivee-variations,etude-complete}.json`,
  `tests/python/instantanes/resoudre/{derivee-variations,etude-complete}.json`, `tests/pages/references/{derivee-variations,etude-complete}.json` :
  9 entrées de la Dérivée et 11 de l'EC, aucune nouvelle ni retirée. Vérifié par programme : dans chaque entrée, seule la carte
  « Dérivée » change (étapes de la dérivée ; f′, tableaux, extremums identiques). Aucun autre outil ne change.

  | Entrée | Avant | Après |
  |---|---|---|
  | produit et quotient (Dérivée : `(x+1)/(x-1)/2`, `(x^2-1)/(x-3)`, `-(x*ln(x))`, `3(x*ln(x))`, `ln(x)/x`, `x*ln(x)`, `x*ln(x)+x`, `x/(x^2+1)`, `x^2*e^(-x)` ; EC : `(e^x-1)/x`, `(x^2-1)/(x-3)`, `3(x*ln(x))`, `ln(x)/x`, `x*ln(x)`, `x/(x^2+1)`, `x/sqrt(x^2)`, `x^2*e^(-x)`) | « On pose u(x) = … et v(x) = … : règle du produit, (uv)′ = u′v + uv′. » · justifications · « u′(x) = … . » · « v′(x) = … . » · ligne f′ | « On applique la règle du produit, (uv)′ = u′v + uv′, avec : » · **tableau** u = … \| v = … / u′ = … \| v′ = … · justifications · ligne f′ (inchangée) |
  | `x^2*e^(-x)` (Dérivée, EC) | … = 2xe^{−x} + x²(−e^{−x}) = … | … = 2xe^{−x} + x²·(−e^{−x}) = … |
  | `e^((x^2+x-2)/(6x-12))` (Ex7, EC) | « (x²)′ = 2x (règle de la puissance). » · « e^{…} est de la forme e^u avec u(x) = (x² + x − 2)/(6x − 12) (dérivée interne u′(x) = ((2x + 1)(6x − 12) − (x² + x − 2)·6)/(6x − 12)²) ⇒ (e^{…})′ = u′e^u = x(x − 4)e^{…}/(6(x − 2)²). » | « f(x) = e^{g(x)} avec g(x) = (x² + x − 2)/(6x − 12), donc f′(x) = g′(x)·e^{g(x)} (dérivée d'une composée). On calcule d'abord g′(x). » · sous-carte **Dérivée de l'exposant** : Étape 1 règle du quotient (formule, tableau u = x² + x − 2 \| v = 6x − 12 / u′ = 2x + 1 \| v′ = 6, g′(x) = ((2x + 1)(6x − 12) − (x² + x − 2)·6)/(6x − 12)²) ; Étape 2 = (12x² − 24x + 6x − 12 − 6x² − 6x + 12)/(36(x − 2)²) (développement) = (6x² − 24x)/(36(x − 2)²) (réduction) = 6x(x − 4)/(36(x − 2)²) (mise en évidence) = x(x − 4)/(6(x − 2)²) (simplification par 6) · « On remplace g′(x) dans f′(x) = g′(x)·e^{g(x)} : » · f′ encadré (inchangé) |
  | `e^(2/(x^2-4))` (d, EC) | « (x²)′ = 2x » · phrase « de la forme e^u … u′(x) = −2·2x/(x² − 4)² » | même structure : tableau u = 2 \| v = x² − 4 / u′ = 0 \| v′ = 2x ; g′(x) = −2·2x/(x² − 4)² (règle du quotient) ; = −4x/(x² − 4)² (calcul) |
  | `e^(1/x)` (EC) | phrase « de la forme e^u … u′(x) = −1/x² … » | même structure : tableau u = 1 \| v = x / u′ = 0 \| v′ = 1 ; g′(x) = −1/x² (règle du quotient), pas d'étape 2 |

  Hors instantanés (corpus) : b « On applique la règle du produit … » · tableau u = x² − 6 \| v = e^{−2x} / u′ = 2x \| v′ = −2e^{−2x} ·
  « f′(x) = … = 2xe^{−2x} + (x² − 6)·(−2e^{−2x}) = −2(x − 3)(x + 2)e^{−2x} » ; c « On développe d'abord (c'est plus simple à
  dériver) : » · « f(x) = eˣ(6 − eˣ) = 6eˣ − eˣ · eˣ (développement) » · « = 6eˣ − e^{2x} (réduction) » · dérivée de la somme
  (« (eˣ)′ = eˣ », « (6eˣ)′ = 6·(eˣ)′ = 6eˣ », « e^{2x} est de la forme e^u … = 2e^{2x} », « f′(x) = 2eˣ(3 − eˣ) ») au lieu de la
  règle du produit ; a inchangé. Largeurs : `test_largeurs.py::test_tableau_uv_et_derivee_de_l_exposant` (Dérivée
  `(x^3+2x)^4*e^x`, EC Ex7, 320 à 1100 px) : aucune faute, tableaux dans leur carte, côte à côte à 1100 px, empilés u, u′, v, v′ à
  320 px ; captures relues à 320 et 1100 px.
