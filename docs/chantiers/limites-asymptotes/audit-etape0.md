# Limites et asymptotes (3M), étape 0 : rapport d'audit (aucun fichier du dépôt modifié)

Références lues en entier : `ch8-corrige-limites.pdf` (21 p.), `limite_J.pdf` (5 p., cours 8.3), les 5 images (3.8 a–h, 3.8 g–h, 3.10, 3.11, feuille eˣ a–h).
Scripts d'essai : `docs/chantiers/limites-asymptotes/scripts/corpus.py` et `repli.py` (moteur lancé via `uv`, SymPy 1.13.3).

## Synthèse

1. **Les valeurs sont presque toutes justes** : 44 limites ou bornes sur 47 du corpus. Les trois cas non lus sont `ln(cos x)`, `sin x` et `log_5` (voir §2). Une valeur est fausse : le pôle gauche de 8.13e (§7).
2. **La rédaction s'écarte du corrigé sur presque tous les points du mode d'emploi** :
   - Aucune prédiction « podium » et aucun « ✓ comparaison ».
   - Pas d'étapes numérotées : une limite = une carte = un seul bloc `aligned`.
   - Les dérivées du haut et du bas ne sont pas montrées séparément, et la simplification de BH est fondue dans la même égalité.
   - Pas de détection de « BH tourne en rond », pas de « on sort la constante », pas de ln gardé en haut systématique.
3. **Conflit de doctrine à trancher** : le moteur évite BH quand une « limite de référence » s'applique (croissance comparée, spec LA-15/LA-32/LA-34) et pour les fractions rationnelles (mise en évidence). Le corrigé fait BH partout, même pour x²e⁻ˣ et pour l'exposant de e^((3x+4)/(x−2)).
4. **Six cas du corpus ne sont pas rédigés** (phrase de repli) : 8.12e (−∞), 8.12f (0⁻), 8.12h (0⁺), 3.8g, Ex5c (−∞) et 3.8g′.

## 1. Fichiers et appel du moteur

| Fichier | Rôle |
|---|---|
| `limites-asymptotes/index.html` (100 l.) | Page : 11 exemples, 4 niveaux d'exercices, encadré « Rappel de la méthode ». Appelle `monterOutil({outil:"limites-asymptotes", sympyAvant:true, …})`. |
| `commun/outil.js` (409 l.) | Socle commun : `appelPy("resoudre", entrée)`. Attend SymPy (`sympyAvant`), gère l'étape suivante, « tout afficher » et le PDF. |
| `commun/moteur-python.js`, `worker-pyodide.js`, `rendu.js` | Worker Pyodide, appels Python, rendu des cartes (KaTeX). |
| `limites-asymptotes/resoudre_la.py` (84 l.) | Adaptateur au format de sortie commun. `resoudre()` appelle `etudier()` puis fabrique les cartes. Réutilisé par l'Étude complète (`resoudre_ec.py`). |
| `limites-asymptotes/limites_asymptotes.py` (3 351 l.) | Tout le moteur : étude rationnelle exacte, rédaction par arbre (`_noeud`, `Lim`, méthodes), asymptotes. |
| `moteur/noyau.py` | Réexporte `ensemble-definition/ensemble_def.py` (2 674 l. : parseur, arbre, ED, polynômes exacts, tableaux de signes, pont SymPy). |
| `moteur/sortie.py` (286 l.) | `so.carte`, `so.texte(html, style, detail)`, `so.formule`, `so.liste`, `so.sortie_ok`. |

**Format renvoyé.**
- `etudier(entrée)` renvoie `{ok, f_tex, ed_tex, etudes:[{ou, etapes:[…]}], asymptotes:[{genre, ou, …}], tableaux_signe}`.
- Chaque élément de `etapes` est `{type:"texte", html, detail?}` ou `{type:"tableau", rows…}`.
- `resoudre()` donne `sortie_ok(énoncé, cartes)` avec les cartes : « Fonction » (ED), « Tableaux de signes », une carte « Limite » par borne (`titre_tex = ou`), puis « Bilan des asymptotes ».
- **Point clé pour « étapes pas assez détaillées »** : une limite rédigée est un objet `Chaine` (l. 1620) rendu en **une seule formule** `\begin{aligned}`. Les justifications (BH, hypothèses) sont des parenthèses à droite de la ligne. Il n'y a ni titre « Étape n », ni encadré de prédiction, ni découpage du pas BH.

## 2. Méthode de calcul

- **Valeur de référence** : `sympy.limit` (`_limite_sympy`, l. 70) sur `en_sympy_reel(f)`.
- **Rationnelles** : chemin exact sans SymPy (`_etude_rationnelle_infini` / `_pole`, l. 312-548) : mise en évidence, division euclidienne, AH/AO/branche parabolique, factorisation par (x−a), trou.
- **Non rationnelles** : `_etude_transcendante` (l. 3176) puis la rédaction par arbre.
  - `Lim` (l. 589) : limites exactes avec signe d'approche de 0 (`ap`). Règles `_somme`, `_produit`, `_quotient`, `_puissance_*`, `_exp_lim`, `_ln_lim`. Elles lèvent `FormeIndeterminee` (∞−∞, 0·∞, ∞/∞, 0/0).
  - `_lever` (l. 1589) essaie `METHODES` dans cet ordre : `_racine_carre_parfait`, `_simplifier_zero_sur_zero`, `_evidence_exp`, `_conjuguee`, `_evidence_racine`, `_comparee_pure`, `_evidence_ln`, `_lhopital` (l. 2870).
  - **Garde-fou** : chaque limite écrite est comparée à SymPy ; au moindre doute, `Abandon` puis phrase de repli (`PHRASE_REPLI`, l. 563).
- **Fonctions reconnues** (`NOMS`, `ensemble_def.py:104`) : `sqrt/racine`, `exp`/`e^`, `log`=`ln`, `ln`, puissances rationnelles, `a^x` (base numérique), multiplication implicite.
  - **Non reconnues** : `sin`, `cos`, `tan` (erreur « Symbole inconnu « s » »), `log_a` (« Caractère non reconnu « _ » »).
  - `a^x` avec base ≠ e passe le parseur, mais la rédaction s'arrête (« exposant non rationnel », cas 3.8g′).
- **Saisie des limites** : aucune. L'utilisateur n'entre que f(x). Les bornes viennent de l'ED (`_bornes`, l. 104) : ±∞ si l'ED y va, chaque valeur interdite (côté gauche, droit ou deux), chaque borne ouverte. On ne peut pas demander « lim_{x→2} » en un point de l'ED, ni une limite latérale choisie, ni lim_{x→0} f(x)/x isolé. Les feuilles 3.8 à 3.11 passent tant que le point est une valeur interdite ou une borne de l'ED.
- **Situations traitées** : substitution ; k/0^± avec tableau de signes ; 0/0 (factorisation pour les polynômes, sinon BH) ; ∞/∞ ; 0·∞ ; ∞−∞ (mise en évidence, conjuguée) ; e^(…) et ln(…) (limite de l'intérieur écrite dans une chaîne séparée) ; AH, AV (un ou deux côtés), AO (division euclidienne ou a puis b), trou, « sans limite », branche parabolique (rationnelles seulement).
- **Ne dit rien** : pour une fonction non rationnelle dont f(x)/x → ∞ (3.10c, 3.11a, 3.11b en +∞), `_oblique_generale` renvoie `None` sans phrase. Il n'y a aucun « pas d'asymptote oblique ».

## 3. Chaque application de BH

Un seul endroit : `_lhopital` (l. 2760) et `_lhopital_avec` (l. 2777), appelés par `_lever` (l. 1599). Candidats : `_candidats_lhopital` (l. 2747). Deux appels indirects : l'asymptote oblique, `a = lim f/x` (l. 3042) et `b = lim (f − ax)` (l. 3045), passent par `_rediger` donc `_lever`.

| Question | Constat |
|---|---|
| Forme vérifiée avant ? | Oui. BH n'est tenté que sur un nœud qui a levé `FormeIndeterminee`, et la forme 0/0 ou ∞/∞ est recalculée (l. 2781-2791). BH n'est jamais appliqué sur une forme déterminée. Les fractions de polynômes en sont exclues (l. 2763). |
| 0·∞ ? | Transformé en quotient `u/(1/v)` de façon mécanique (l. 2753). **Pas** la règle du corrigé : ln gardé en haut, eˣ → 1/e⁻ˣ, x² → 1/x⁻², constante sortie. L'ordre des candidats suit la saisie, pas la règle. |
| Existence de la nouvelle limite ? | Implicite : `_noeud(q_arbre)` la calcule, sinon `Abandon` puis repli. L'hypothèse (d) n'est pas écrite. La parenthèse n'affiche que la dérivabilité (b) et g′ ≠ 0 (c). |
| Dérivées haut et bas séparées ? | **Non.** Seule (g)′ apparaît dans la parenthèse d'hypothèse. Aucune ligne « haut : … → dérivée : … » / « bas : … → dérivée : … ». |
| Schéma haut → dérivée / bas → dérivée ? | Absent. La ligne passe directement à `sp.simplify(f′/g′)` (l. 2800) : **BH et simplification sont fusionnés**. |
| Table de dérivées ? | Aucune table maison. `sp.diff` puis `arbre_depuis_sympy`. Les formes écrites sont celles de SymPy, pas celles du corrigé. |
| Reverification avant chaque BH ? | Implicite : une nouvelle forme levée à l'intérieur de `q_arbre` relance `_lever`. Plafond `nb_lhopital ≥ 2` et profondeur ≥ 4. Le corrigé a besoin de 3 BH en 8.12e. |
| Boucle détectée ? | **Non** (aucun code). Seuls les plafonds ci-dessus, d'où un repli (8.12h). |
| Ordre des méthodes | BH est le **dernier recours** : mise en évidence et croissance comparée passent avant. |

**Exemples constatés.**
- 8.12a : `ln(x)/e^(2x)` donne `\frac{\frac{1}{2}e^{-2x}}{x}` en une étape. Le corrigé : (1/x)/(2e²ˣ) = 1/(2x e²ˣ), en deux temps.
- Ex5b en −∞ : BH sur `a = lim x·e^(1/x)/x` donne `(e^(1/x) + (−e^(1/x))/x)/1`, alors que x/x se simplifie directement. `b = lim (f − x)` tombe en repli (∞−∞ non levée).
- 8.12g en 0⁺ : deux BH enchaînés avec une réécriture ½·x·e^(1/x), et trois fois la même parenthèse « x > 0 : cf. tableau de signes ».

## 4. Mode d'emploi du corrigé, point par point

| # | Étape du corrigé | État |
|---|---|---|
| 1 | Remplacer (haut, bas, ou chaque facteur) | **Existe** : `lim f = « … » = « … »`, niveaux de substitution (`_niveaux`). Une seule ligne, pas « Haut : … Bas : … Forme : … ». |
| 2 | Nommer la forme, conclure si déterminée | **Existe** (« : forme indéterminée »). Manque « : pas indéterminée ! » en vert et le « Attention : pas de BH ici » (Ex5d, 8.12c). |
| 3 | Prédiction podium (ou tableau de valeurs, 8.14) | **Absente** : aucune prédiction, aucun « On s'attend à », ni tableau de valeurs. |
| 4 | 0·(±∞) en quotient, ln en haut, constantes sorties | **Écart** : transformation mécanique, constante non sortie (8.12e en repli), pas de « ln en haut, pourquoi ». |
| 5 | Simplification préalable (8.12b : ln(x³) = 3 ln x) | **Absente** devant BH. Existe seulement dans la chaîne ln/x (« propriétés de ln »). |
| 6 | BH : haut → dérivée / bas → dérivée | **Absent** (§3). |
| 7 | Simplification explicite après BH | **Fondue** dans le pas BH (`sp.simplify`). |
| 8 | Revérifier la forme avant chaque BH | **Implicite**, jamais écrit : « BH (1re fois), forme encore indéterminée… » n'apparaît pas. |
| 9 | « BH tourne en rond » (8.12h) | **Absent** : repli (« 0/0 non levée »). |
| 10 | Limite de l'exposant / de l'intérieur à part | **Existe** (Ex6, 8.13 b–e). Mais le calcul de l'intérieur passe par la mise en évidence, pas par BH, et sans prédiction. Résultat final de l'exposant donné sans signe (0⁻ en 8.13c non écrit). |
| 11 | Résultat encadré et « ✓ comparaison » | **Absents**. De plus la valeur finale 0 est écrite sans signe (`L.tex(False)`) alors que le corrigé écrit 0⁺ / 0⁻. |
| 12 | Cartes « Prédiction », « Attention », « Autre méthode : changement de variable » | **Absentes** (styles de blocs à inventorier dans `sortie.py` et `rendu.js`). |

## 5. Réutilisable depuis l'outil « Ensemble de définition »

Déjà importé par le moteur des limites :
- `domaine`, `fusion`, `inter`, `complement`, `signe_facteur`, `tableau_facteurs` (`ensemble_def.py` l. 2069, 2151, 2254, 816).
- `TableauSigne` et le registre `TABLEAUX` (l. 820-927 de `limites_asymptotes.py`) : ED de ln, tableaux de signes, rendu identique à l'outil ED.
- `blocs_condition` (`resoudre_ed.py`), déjà réutilisé par l'outil Exponentielles et logarithmes (filière M).

À examiner :
- `exponentielles-logarithmes/exp_log_m.py` gère déjà `log_a` (l. 309, 491 : `_base_log`, `_FAMILLES`). Je n'ai pas vérifié comment la saisie `log_5(…)` y est lue.
- L'ED de `log_a(u)` revient à celle de `ln(u)`, plus les conditions constantes a > 0 et a ≠ 1.
- Le parseur de l'ED ne lit ni `log_a`, ni `sin`, ni `cos` (jeu de fonctions ln, exp, sqrt seulement) : à étendre côté noyau (`NOMS`) avec un effet sur tous les outils, ou à traiter par réécriture log_a(u) = ln(u)/ln(a) dans l'outil.

## 6. Tests existants

**Couvert :**
- `test_redaction_limites.py` (1 128 l.) : phrases exactes, tableaux de signes, mise en évidence, conjuguée, croissance comparée, L'Hôpital, garde-fou, vocabulaire.
- `test_proprietes_limites.py` : oracle mpmath 50 chiffres, sondes à ±10²…10³⁰ et a ± 10⁻³…10⁻³⁰ sur environ 60 fonctions (LA-04, LA-05, LA-12).
- `test_limite_indeterminee.py` (LA-03), `test_limites_deux_cotes.py` (LA-01, LA-08).
- `test_tableau_limites.py` (Étude complète), `test_resoudre_la.py`, `test_rappel_methode.py`, `test_vocabulaire.py`, `test_json_strict.py`, `test_racines_reelles.py`.
- Instantanés : `tests/python/instantanes/limites-asymptotes.json` (24 entrées) et `instantanes/resoudre/limites-asymptotes.json`.
- Pages : `tests/pages/references/limites-asymptotes.json` (25 entrées), `test_rendu.py`, `test_comportement.py` (page à 360 px sur une fonction, `captures.py` pour les vues 360 px).

**Manque :**
- Aucun test sur le **corpus de l'enseignant** (ni 8.11 à 8.14, ni 3.8, 3.10, 3.11, ni la feuille eˣ).
- Aucune vérification de la structure « étapes numérotées ».
- Aucun test pour les produits 0·∞ (ln en haut, constante sortie), la boucle, la prédiction, `sin`, `cos`, `log_a`.
- Rien qui détecte une valeur SymPy non réelle (cas 8.13e).
- Les tests **encodent la doctrine actuelle** : LA-15, LA-32 et LA-34 (« jamais L'Hôpital quand une référence s'applique », « au plus deux applications de suite », ln(x²+1)/x sans BH). Ils devront être réécrits avec le nouveau mode d'emploi.

## 7. Moteur actuel sur le corpus

Légende : « Valeur » = limite renvoyée ; « Rédaction » = écarts avec le corrigé (BH = Bernoulli-L'Hôpital, CC = croissance comparée, MEE = mise en évidence). Sauf mention, les écarts communs de §4 s'appliquent (pas de prédiction, pas de ✓, valeur finale sans signe 0⁺/0⁻, pas d'étapes numérotées).

| Limite | Valeur attendue (SymPy indépendant) | Outil | OK | Écarts de rédaction |
|---|---|---|---|---|
| 8.11a eˣ/ln x, +∞ | +∞ | +∞ | oui | BH tenté, mais haut→dérivée absent, simplification fondue (e^x/(1/x) → x·eˣ). |
| 8.11b x³ ln x, 0⁺ | 0⁻ | 0 | oui (signe perdu) | CC au lieu de BH ; pas de ln en haut, pas de x³ = 1/x⁻³. |
| 8.11c x²eˣ, −∞ | 0⁺ | 0 | oui (signe perdu) | CC au lieu de BH. |
| 8.11d x²e⁻⁵ˣ, +∞ | 0⁺ | 0 | oui (signe perdu) | CC au lieu de 2 BH. |
| Ex5a x²e⁻ˣ, +∞ | 0⁺ | 0 | oui (signe perdu) | CC. |
| Ex5b x·e^(1/x), 0⁺ | +∞ | +∞ | oui | Chaîne x = 1/(1/x) puis BH : proche du corrigé. En 0⁻ : 0. En ±∞ : −∞ / +∞ ✓, mais l'AO y = x + 1 passe par BH inutile et b en repli. |
| Ex5c e⁻ˣ/x², −∞ | +∞ | +∞ | oui | **Repli** (`∞/∞ non levée`) alors que le corrigé fait 2 BH. |
| Ex5d e⁻ˣ/(4x), +∞ | 0⁺ | 0 | oui | Direct, bien. Manque « Attention : pas de BH ». |
| 8.12a ln x/e²ˣ, +∞ | 0⁺ | 0 | oui | BH ✓ mais pas de haut/bas séparés, simplification fondue, ½e⁻²ˣ/x au lieu de 1/(2x e²ˣ). |
| 8.12b e⁻ˣ ln(x³), +∞ | 0⁺ | 0 | oui | Pas de ln(x³) = 3 ln x préalable ; quotient ln(x³)/(1/e⁻ˣ) au lieu de 3 ln x/eˣ. |
| 8.12c e⁻ˣ·x, −∞ | −∞ | −∞ | oui | Direct. |
| 8.12d eˣ ln(−x), −∞ | 0⁺ | 0 | oui | BH sur ln(−x)/(1/eˣ) : proche du corrigé, mais dérivée composée non expliquée. |
| 8.12e x³e^(3x−5), −∞ | 0⁻ | 0 | oui | **Repli** (`0·∞ non levée`) : 3 BH requis, plafond 2 ; constante e⁻⁵ non sortie. |
| 8.12f e^(1/x)/x², 0⁺ | +∞ | +∞ | oui | Direct, comme le corrigé. En 0⁻ : 0 en **repli**. |
| 8.12g e^(1/x)x², 0⁺ | +∞ | +∞ | oui | 2 BH enchaînés, parenthèse de signe répétée 3 fois ; le corrigé renvoie à Ex5b. |
| 8.12h e^(−1/x)/x, 0⁺ | 0⁺ | 0 | oui | **Repli** (`0/0 non levée`) : piège « BH tourne en rond » non géré. |
| Ex6 e^((3x+4)/(x−2)), +∞ | e³ | e³ | oui | Exposant par MEE (pas BH), pas de prédiction 3/1 = 3. |
| Ex6 cours e^(−(3x+4)/(x−2)), +∞ | e⁻³ | e⁻³ | oui | Idem. |
| 8.13a e⁻ˣ, +∞ | 0⁺ | 0 | oui | Écrit « e^{−∞} = 0 » sans le +. |
| 8.13b e^((x²−3x+2)/(2x²)), +∞ | e^(1/2) | e^(1/2) | oui | MEE au lieu de BH sur l'exposant. |
| 8.13c e^(−2x/(x²−5)), +∞ | 1 | 1 | oui | Exposant → 0⁻ non écrit. |
| 8.13d e^((3x²+2)/(2x)), −∞ | 0⁺ | 0 | oui | MEE. |
| 8.13e ln(…), +∞ | ln 3 | ln 3 | oui | MEE. Aux **pôles** : voir « Valeurs fausses » ci-dessous. |
| 8.13f ln(1/x), +∞ | −∞ | −∞ | oui | Pas détaillé (intérieur 0⁺). |
| 8.14 ln(1+eˣ)/eˣ, −∞ | 1 | 1 | oui | BH ✓ ; pas de tableau de valeurs ni de « le podium ne peut pas aider ». |
| 3.8a ln(x+1)/x, 0 | 1 | 1 | oui | BH + trou (0 ; 1) ✓. |
| 3.8b ln(cos x)/x², 0 | −1/2 | — | **non pris en charge** | « Symbole inconnu « c » ». |
| 3.8c (ln x − 1)/(x − e), e | e⁻¹ | e⁻¹ | oui | BH ✓. |
| 3.8d ln(x²−3)/(2−x), 2 | −4 | −4 | oui | BH ✓ ; ±∞ par CC et MEE. |
| 3.8e ln(x²+1)/x, −∞ | 0 | 0 | oui | CC/MEE, pas BH. |
| 3.8f (ln x + 1)/(1 − ln x), +∞ | −1 | −1 | oui | BH ✓, simplification fondue. |
| 3.8g ln(x²)/ln²(x), +∞ | 0 | 0 | oui | **Repli** (`∞/∞ non levée`). |
| 3.8h ln x/eˣ, +∞ | 0⁺ | 0 | oui | BH ✓. |
| 3.8 g′ (8ˣ − 2ˣ)/(4x), 0 | ln 2 / 2 | ln 2 / 2 | oui | **Repli** (aˣ non géré). |
| 3.8 h′ log₅(x+2)/(x+1), −1 | 1/ln 5 | — | **non pris en charge** | `log_5` non lu. |
| Feuille a (eˣ − e²)/(x − 2), 2 | e² | e² | oui | BH ✓. |
| Feuille b (eˣ − 1)/sin x, 0 | 1 | — | **non pris en charge** | `sin`. |
| Feuille c x eˣ/(1 − eˣ), 0 | −1 | −1 | oui | BH ✓ ; +∞ : « −1x » mal écrit, oblique en repli. |
| Feuille d x e^(1/x), 0⁺ | +∞ | +∞ | oui | Voir Ex5b. |
| Feuille e (eˣ + e⁻ˣ)/(2x), −∞ | −∞ | −∞ | oui | BH partiel + MEE. |
| Feuille f (2eˣ − 1)/(eˣ + 2), +∞ | 2 | 2 | oui | MEE (corrigé : BH). |
| Feuille g (x²+x)eˣ, −∞ | 0⁺ | 0 | oui | CC/MEE. |
| Feuille h eˣ/(x²−2x+3), +∞ | +∞ | +∞ | oui | CC. |
| 3.10 a à e (e^(−x²), e^(1/x), (x²−4x+4)eˣ, x/eˣ, (eˣ+2)/(1−3eˣ)) | AH y = 0 et 0 ; y = 1 ; AV x = 0 ; AH y = 0 (−∞) ; AH y = 0 (+∞) ; AH y = 2 et −1/3, AV x = −ln 3 | identique | oui | Pas de phrase « pas d'asymptote oblique » aux bords où f(x)/x → ∞. |
| 3.11 a à e (x² ln x, ln(x²+1), ln x/x, ln(2x/(x+1)), (ln x − 2)/(ln x − 1)) | trou (0 ; 0) ; pas d'asymptote ; AV x = 0, AH y = 0 ; AH y = ln 2, AV x = −1 et x = 0 ; AH y = 1, AV x = e, trou (0 ; 1) | identique | oui | Idem. |

**Valeurs fausses (une) : 8.13e au pôle gauche.** En x → ((5 − √17)/2)⁻, le dénominateur est positif, donc ln(…) → +∞ et la droite x = (5 − √17)/2 est une asymptote. L'outil affiche une limite « finie » absurde (`− log(x) + log(…) + iπ`) et conclut « trou dans le graphique ». Le pôle droit est correct (+∞). Cause : `_limite_sympy` (l. 70-82) ne rejette pas un résultat SymPy contenant le symbole x ou i. `_valeur_tex` (l. 94-98) retombe alors sur `sp.latex(res)`. Le garde-fou ne joue pas parce que ce cas passe par le chemin « repli ».

## 8. Risques, non pris en charge, questions ouvertes

**Non pris en charge :**
- `sin`, `cos`, `tan`, `log_a`.
- `aˣ` en rédaction (le calcul SymPy marche, la rédaction tombe en repli).
- Produit 0·∞ avec constantes, sortie de constante, ordre ln en haut.
- Boucle de BH.
- Troisième BH.
- Prédiction podium (incluant x → −∞, 0⁺ par t = −x ou 1/x), tableau de valeurs.
- Limite en un point choisi par l'utilisateur (hors valeur interdite).

**Risques :**
- **Refonte du pas BH** : il faut une vraie table de dérivées sur l'arbre (eᵘ, ln u, composées, 1/x, puissances) à la place de `sp.diff` et `sp.simplify`, sinon les formes ne coïncideront jamais avec le corrigé. La simplification devient une étape à part, avec des règles explicites.
- **Doctrine** : l'ordre des méthodes, LA-15, LA-32 et LA-34 sont contredits par le nouveau mode d'emploi. Les tests et les instantanés actuels cassent en masse.
- **Format de sortie** : étapes numérotées et nouveaux styles (prédiction, attention, résultat) dans `sortie.py` et `rendu.js` : touche tous les outils qui partagent ces cartes (Étude complète en premier, via `resoudre_ec.py`).
- Le garde-fou protège de l'erreur, mais pas d'une rédaction qui ne suit pas le corrigé ; chaque nouveau chemin doit être confronté à la sonde mpmath.
- Temps de calcul dans Pyodide : SymPy sert encore de référence ; les tests complets durent déjà plusieurs centaines de secondes.

**Questions ouvertes pour l'enseignant :**
1. BH partout (comme le corrigé) ou conserver MEE et CC avant BH pour les fractions rationnelles et les références (x²e⁻ˣ en CC) ? Mon avis : BH comme le corrigé quand la forme est 0/0 ou ∞/∞ ; MEE et CC restent proposées en « Autre méthode », jamais en méthode principale.
2. Une limite en un point quelconque et une saisie « lim » (limites latérales) : faut-il un second champ (point et côté) ? Aujourd'hui l'outil ne traite que les bornes de l'ED.
3. `sin`, `cos` : requis pour 3.8b et la feuille b, ou hors programme 3M ? `log_a` pour 3.8 h′ ?
4. Préférez-vous une carte par « Étape n » (avec bouton « étape suivante ») ou une seule carte par limite avec sections ?
5. Faut-il garder l'étude complète des deux bords (ED) en même temps, ou une limite à la fois comme dans le corrigé ?
6. Le « tableau de valeurs » de 8.14 : généré par l'outil (valeurs à 5 chiffres) ou texte fixe ?

## Proposition pour l'étape 1 (à valider)

1. Corriger d'abord le défaut de 8.13e (rejeter dans `_limite_sympy` tout résultat avec symbole libre ou imaginaire) : bug indépendant du reste.
2. Ajouter un test sur tout le corpus de `docs/reference/limites/` avec oracle numérique, avant toute refonte.
3. Rédiger la spécification « filière 3M, mode d'emploi BH » (nouvelles règles du guide de rédaction, remplacement de LA-15/LA-32/LA-34).
4. Construire la table de dérivées et la nouvelle structure d'étapes, cas par cas, en commençant par le corrigé 8.11 à 8.12.

Aucun fichier du dépôt n'a été modifié.
