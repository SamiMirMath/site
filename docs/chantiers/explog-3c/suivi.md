# Chantier « Exponentielles et logarithmes 3C : résoudre ce que la 2M résout, puis contrôler » — suivi

Demande du 02.11.2026, branche `correctif-explog-3c` (depuis `main`). Deux commits, suite complète verte avant chacun, **rien n'est poussé**.

| Commit | Contenu | État |
|---|---|---|
| (a) | adaptateur 3C → 2M, carte « Contrôle », famille « regroupement » (les 5 équations de l'énoncé) | **faite** (suite complète verte : 931 tests Python, 100 tests de pages) |
| (b) | les autres familles de la 2M (voir le tableau) | à faire |

## Symptôme et cause exacte

`log(x+3) = 2log(3)` : 3C « Cet outil ne traite pas encore ce type d'équation. », 2M `S = {6}`. Les cinq équations de l'énoncé échouent en 3C et passent en 2M.

- La 2M (`exponentielles-logarithmes/resoudre_el.py:145-162` avant le correctif) essaie `elm.variantes_changement`, `elm.variantes_exposant`, puis `elm.corriger_equation` (`exp_log_m.py:1978`) qui enchaîne
  `_calcul_du_second_membre`, `logarithmique_m`, **`regrouper`** (`exp_log_m.py:711`), `base_polynomiale`, `base_inconnue_rationnelle`, `produit_x_log`.
- La 3C n'appelait que `el.corriger_equation` (`resoudre_el.py:171`) : `logarithmique` et `lineaire_logarithmes` (`exp_log.py:3329`). `_logarithmique` exige un seul logarithme égal à une **constante** (`exp_log.py:2768-2770` : `c = _const(o)` vaut
  `None` pour `2log(3)`, donc `_Hors`), d'où « pas encore » (`resoudre_el.py:172-174`).
- Deux verrous propres à la 3C dans `analyser_saisie` (`exp_log.py:670-673`) : `log_(2x)(…)` et π.

## Écarts mesurés avant le correctif (664 saisies : batteries, exemples C et M, pools ; 1 155 avec 60 graines par niveau)

186 saisies résolues en 2M et pas en 3C (160 avec les graines, autres entrées) :

| Famille | Entrées | Commit |
|---|---|---|
| Regroupement de logarithmes (k·log u, log u ± log v, log au second membre, constante) | ~50 (dont les 5 de l'énoncé) | (a) |
| Constante irrationnelle (`ln(x) + ln(2) = 3`, `ln(x³) = 2`) | ~18 | (b) |
| `log_x(32) = 5/3` | 12 | (b) |
| Second membre calculé (`log(x) = (log 20 + log 100 − log 2)/(…)`) | 6 | (b) |
| Carré d'une somme dans l'exposant | 6 | (b) |
| `x − x·ln(x) = 0` | 10 | (b) |
| Changement de variable et bicarré (« hors programme 3C » depuis le 27.10) | ~25 | (b) |
| Exposants 1/x, √x, ±ln x | ~27 | (b) |
| Base polynomiale `log_(2x)(1296) = 4` | 15 | (b) |
| π (`e^x = π`) | 7 | (b) |

## Décisions

1. **Tout aligner sur la 2M** : les 186 cas, y compris les anciens « hors programme 3C » (décisions des 27 et 29.10.2026, amendées dans la spécification).
2. En 3C, **⇒** sur les lignes de regroupement, ⇔ ailleurs, propriétés sans « sur l'ED ». **Chaque ligne est une implication vraie sur tout le domaine de l'équation de départ** : aucun développement
   (`log(u²) → 2 log u`, `log(uv) → log u + log v`) qui perdrait des solutions qu'aucun contrôle ne rattrape ; la conversion lève `_Hors` plutôt que de perdre une solution.
3. **Une seule carte « Contrôle »** pour toute équation logarithmique ; elle remplace l'ancienne « Vérification » de la 3C (exemple 6 `log(5 − x) = 8` compris).
4. **log = base 10, ln = base e** (usage suisse) : déjà le cas (`_base_du_logarithme(None)` → 10 ; spécification ligne 35). Test d'affichage (`\log`, `\ln`, jamais `\log_{10}`).
5. Deux commits : (a) adaptateur + Contrôle + regroupement ; (b) les autres familles.

## Réalisation (commit a)

- `exp_log.py` : liens de chaîne « ⇒ » et « ≈ » (`LIENS_TEX`, `tex_chaine`, `rangees_chaine`). Rien d'autre. Le moteur 3C d'un logarithme (`_logarithmique`) produit encore sa carte « Vérification » en interne ; `controler_3c` la retire
  et ajoute le Contrôle (nettoyage possible plus tard : il faudrait adapter `test_exp_log.py` qui appelle `el.corriger_equation` directement).
- `exp_log_m.py`, section 6 : `PROPRIETES_C` (propriété M → propriété 3C, lien), `en_3c`, `_chaine_membre` / `_regrouper_membre` (calcul d'un membre avec sa propriété nommée), `_message_rejet`, `_controler`, `controler_3c`,
  `corriger_equation_3c` (regroupement), `corriger_equation_c` (point d'entrée de l'adaptateur). La filière M n'est pas modifiée : ses 1 150 sorties sont identiques avant/après (comparaison des sorties complètes de `resoudre`).
- `resoudre_el.py` : la branche C appelle `elm.corriger_equation_c` ; `besoin_sympy` transmis (identité : l'ensemble où les logarithmes existent vient de l'outil ED).

## Mesures

- Avant/après sur 2 300 sorties (1 150 saisies × 2 filières, graines 0 à 59 des pools C et M) : M identique 1 150/1 150 ; C identique 761 ; C « nouveau corrigé » 224 ; C « corrigé changé » 165 (le Contrôle remplace la Vérification) ; **0 régression**
  (aucune équation résolue avant ne l'est plus).
- Après (a) : 160 saisies encore résolues en M et pas en C = les familles du commit (b).
- Aucune différence de S entre C et M sur toutes les saisies que les deux résolvent (917 sur 1 155).
- Instantané 3C régénéré (M intact) : 61 corrigés changés (Contrôle à la place de Vérification), 13 entrées ajoutées, 3 erreurs devenues des corrigés, 0 exponentielle modifiée. Références de la page 3C : 64 rendus changés, 13 ajoutés, 2 retirés, aucun sans log/ln.
- Suite complète : 931 tests Python (924 s), 100 tests de pages (1 084 s), code de retour 0. Test de page à 390 px et 1100 px : `test_explog_3c_controle_a_390_px`.
- Les `regrouper` de la 2M traitent aussi une constante irrationnelle seule (`log(x²−1) = 1/2`, `ln(x) = …`) : elles passent en 3C dès le commit (a), plus tôt que prévu ; le commit (b) garde le reste du tableau.

## Pièges notés

- zsh ne découpe pas une variable : écrire la commande `uv run …` en entier.
- Les cartes de la sortie portent « Étape k » en titre et le nom de la méthode en **badge** : les tests cherchent « Contrôle » dans le badge.
- `racines()` (oracle de balayage) renvoie parfois deux fois la même racine : dédoublonner avant de comparer.
- `_valeur_rationnelle` reconnaît un rationnel numériquement (60 chiffres) : « = » n'est écrit que pour un calcul exact (`_const`), sinon « ≈ ».
