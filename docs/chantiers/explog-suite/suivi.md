# Chantier explog-suite (PC, 05.11.2026)

Branche `explog-suite`, depuis `main` à jour (78e09d6). Une seule session, sans sous-agent. Méthode : `docs/methode-chantiers.md`.
Origine : fiche du correctif du Mac, `origin/mac-correctif-explog:docs/chantiers/correctif-explog-delta.md` (ses 8 questions).
Détail (balayages, rapports, temps) : `journal.md`.

## État

| Point | Objet | État |
|---|---|---|
| 1 | Doubles signes de la carte « Contrôle » (3C) et de « −(−x) » (C et M) | ✓ commité (6fb5ec1), suite verte ; `verifier` REFUSÉ (voir Écarts) |
| 2 | Garde générale « deux signes consécutifs », tous les outils | ✓ commité, suite verte |
| 3 | Cas 1/64 : **non modifié** (spécification, exemples 10 et 11 : log(32) reste log(32)) | ✓ rien à faire |
| 4 | Les 7 autres questions du Mac : recommandations ci-dessous, rien d'appliqué | ✓ |

## Point 1

- **Cause** : `tex()` (`exponentielles-logarithmes/exp_log.py`, nœud `Neg`) ne mettait entre parenthèses que la somme sous un signe moins.
  Quand la carte « Contrôle » remplace x par −100 dans −x, l'arbre est `Neg(Nb(−100))`, écrit « --100 » ; de même `Neg(Neg(x))`
  (saisie « −(−x) ») écrit « --x », et `Neg(Nb(−2))` (−log(1/100)) écrit « --2 ».
- **Correction** : sous un signe moins, un opposé ou un nombre négatif est aussi mis entre parenthèses (`_comme_somme`, déjà utilisé
  pour la soustraction) : « log(−(−100)) = log(100) », « log_{−(−2)}(4) », « −log(1/100) = −(−2) = 2 ».
  Un seul imprimeur pour les deux filières : la 3C et la 2M sont corrigées ensemble.
- **Entrées touchées** (balayage du corpus C et M et de ses variantes où x devient (−x), voir `journal.md`) : avant, 118 en C et 15 en M ;
  après, aucune avec deux signes moins. Dans le corpus lui-même : les 3 entrées de la fiche du Mac (3C seulement).
- **Test** : `tests/python/test_explog_doubles_signes.py` (textes exacts des 3 contrôles, oracle sur les solutions contrôlées, « −(−x) »
  en C et M, balayage). Sans la correction : 137 échecs ; avec : vert.

## À relire par l'enseignant (instantanés modifiés)

| Fichier | Entrée | Avant | Après |
|---|---|---|---|
| `tests/python/instantanes/resoudre/exponentielles-logarithmes.json` et `tests/pages/references/exponentielles-logarithmes.json` | `log(-x)=2` | `\log(--100) = \log(100) = …` | `\log(-(-100)) = \log(100) = …` |
| (les mêmes) | `log_(-x)(4)=2` | `\log_{--2}(4) = \log_{2}(4) = …` | `\log_{-(-2)}(4) = \log_{2}(4) = …` |
| (les mêmes) | `-log(x)=2` | `-\log\left(\frac{1}{100}\right) = --2` | `-\log\left(\frac{1}{100}\right) = -(-2)` |

Aucune autre ligne ne change (filière M : instantané et référence identiques). Le point 2 ne change aucun instantané.

## Point 2

- **Garde** : `tests/python/test_doubles_signes.py`. Motif : deux signes parmi + - − séparés au plus par des espaces, une accolade ouvrante
  ou une petite espace TeX (`\,`, `\;`…) ; couvre « -- », « −− », « +- », « -+ », « + - », « - - » (et « ++ », « + {-1} »).
  - Instantanés `resoudre` (7 outils) : chaque chaîne ; dans le HTML, chaque morceau entre deux balises, ses formules \( \) et \[ \] et son texte.
  - Références de pages (8 fichiers) : chaque formule ⟦…⟧ et chaque case de tableau. Le texte en clair d'une carte y colle les cases d'un
    tableau de signes (« −−0+ ») et les boutons du graphique (« − + ») : il est contrôlé dans l'instantané `resoudre`, auquel la page est égale.
  - Sur `main`, la garde trouve exactement les 3 fautes du point 1 (instantané et référence 3C) ; **aucune dans les autres outils** : rien à lister.
- **Autre cas trouvé dans Exp-log (hors corpus, par le balayage en (−x))** : `e^(-x)*e^((-x)+1)=5` écrivait « −x + −x + 1 = ln(5) »
  (somme dont le second terme commence par un signe moins). Corrigé dans `tex()` : « −x + (−x + 1) = ln(5) » ; même règle pour une
  différence. Aucun instantané ne change.
- `test_explog_doubles_signes.py` : le balayage du corpus et des variantes en (−x) cherche désormais tous les doubles signes (motif de la
  garde) ; test du cas ci-dessus en C et M. Sans la correction du point 2 : 3 échecs.
- **Hors des motifs demandés, non corrigé** (signes doublés séparés par une parenthèse, famille Δ, questions 5 et 7) :
  `10^(x^2-5x)=1000^(-2)` « x² − 5x − (−2)·log(1’000) = 0 », « 25 + 4(−2)·log(1’000) » ; `2^(-x^2+5x)=3` « 25 + (−4)·… » ;
  dans le corpus, 3 entrées « + (−4) \cdot » (fiche du Mac, tableau des instantanés).

## Point 4 : les 7 autres questions du Mac (rien d'appliqué)

Le correctif du Mac (`origin/mac-correctif-explog`) n'est pas dans `main` ; `main` a son propre correctif (b6aacef). Constat refait sur
`main` (variante « Logarithmes », filière C, identique en M), puis recommandation.

| Q | Entrée | Sur `main` aujourd'hui | Recommandation |
|---|---|---|---|
| 1 | `2^(x^2-5x)=2^(-6)` | x² − 5x + 6 = 0 ⇔ (x − 2)(x − 3) = 0 (pas de Δ), comme la méthode « même base » | **Garder la factorisation** quand a = 1 et Δ carré parfait (corrigés de référence : factoriser puis produit nul) ; Δ seulement sinon. |
| 2 | `2^(x^2-4)=1/8` | x² = 4 + log(1/8)/log(2), x₁ = −√(…), S = {x₁ ; x₂}, contrôle à la calculatrice | **Ne rien changer** : même règle que 1/64 (spécification, exemples 10 et 11 : le logarithme reste écrit). |
| 3 | `3^(x^2)=3^(x+6)` | x²·log(3) − x·log(3) − 6log(3) = 0, Δ = (−log(3))² − 4log(3)·(−6log(3)) non calculé, S = {x₁ ; x₂} | **Diviser par log(3)** (« car log(3) ≠ 0 », pas un calcul de logarithme) quand tous les coefficients en sont des multiples rationnels : x² − x − 6 = 0, puis factorisation. À confirmer par l'enseignant (change des instantanés). |
| 4 | `2^(x^2-5x)=2^0` | S = {0 ; 5log(2)/log(2)} et contrôle « on retrouve x = 0 ou x = 5 » | **Simplifier** 5log(2)/log(2) = 5 (simplification d'une fraction, sans calcul de logarithme) : S = {0 ; 5}, sans contrôle. Prioritaire : visible et maladroit. |
| 5 | `10^(x^2-5x)=1000^(-2)` | x² − 5x = (−2)·log(1’000), puis « x² − 5x − (−2)·log(1’000) = 0 » et « Δ = … = 25 + 4(−2)·log(1’000) » (signes doublés séparés par une parenthèse, hors des motifs du point 2) | **Écrire log(1’000) = log(10³) = 3·log(10)** (règle de la méthode B pour les puissances de 10, log(100) = log(10²) = 2·log(10), sans log(10ᵏ) = k interdit par EL-20), d'où x² − 5x = −6, puis la factorisation. |
| 6 | `2^(x^2-5x)=2^(-1/2)` | Méthode « Même base / définition » : « Il faut les logarithmes. » alors que les bases sont les mêmes | **Corriger** (le message est faux) : la méthode A doit résoudre x² − 5x = −1/2 comme la méthode B (x² − 5x + 1/2 = 0, Δ = 23). Prioritaire (règle « rien de faux »). |
| 7 | `2^(-x^2+5x)=3` | Δ = 25 + (−4)·log(3)/log(2), puis x₁ = (−5 + √Δ)/(−2) | **Multiplier par −1 avant Δ** (x² − 5x + log(3)/log(2) = 0, Δ = 25 − 4·log(3)/log(2), x₁ = (5 − √Δ)/2) ; « + (−4)· » disparaît du même coup. |

Q8 (doubles signes de la carte « Contrôle ») : point 1 de ce chantier.

## Écarts

- **`verifier` du point 1 : REFUSÉ, deux motifs.**
  1. Fichiers non suivis de l'enseignant sous `docs/` (`docs/architecture.md`, `docs/chantiers/equations-2e-degre/quiz.md`,
     `docs/chantiers/revue-structure/rapport.md`) : vaut accepté (consigne du 05.11).
  2. **Sous-tests en baisse** : `test_exp_log.py::TestVouvoiement::test_aucun_texte_du_fichier_ne_tutoie` 1 208 → 1 207 et
     `test_vocabulaire.py::TestVouvoiement::test_litteraux_des_moteurs` 8 698 → 8 697. Un sous-test par littéral de chaîne du moteur :
     la correction a retiré le littéral `"+-"` (`n.a.op in "+-"` devenu `_comme_somme(n.a)`). Aucun test n'est modifié ni affaibli,
     mais c'est un motif de refus autre que les fichiers non suivis : **pas de fusion** (consigne), branche poussée seule.
     Pour fusionner, l'enseignant peut accepter ce motif, puis rafraîchir `tests/reference/` (`lancer.py reference`) sur la branche.
- **`verifier` du point 2** : seul motif, les fichiers non suivis de l'enseignant (vaut accepté) ; listes identiques à la référence, 9 tests
  ajoutés, les deux sous-tests de vouvoiement remontent à 1 209 et 8 699 (deux littéraux `"-"` ajoutés). Le refus du point 1 empêche
  quand même la fusion (consigne : tout autre motif de refus, pas de fusion) ; branche poussée seule.
- Commande de fusion, si l'enseignant accepte le motif du point 1 : `git switch main && git merge --no-ff --no-edit explog-suite`,
  puis `git push`, puis `git branch -d explog-suite`.

- Pas de nouvelle référence au P0 (`lancer.py reference`) : `tests/reference/` date d'aujourd'hui (PC, c9b257f), les commits suivants ne
  touchent que l'outillage de test ; le prompt demande un commit par point.

## Reprise après compactage

- Branche `explog-suite` ; un commit par point (1, puis 2) ; suite d'avant commit :
  `PROCESSUS_PAGES=4 python3 tests/lancer.py complet --rapport <scratchpad>/p<N>` puis `verifier`.
- Fichiers non suivis de l'enseignant (`docs/architecture.md`, `docs/chantiers/equations-2e-degre/quiz.md`,
  `docs/chantiers/revue-structure/`) : ne pas y toucher ; un refus de `verifier` pour ce seul motif vaut accepté (consigne du 05.11).
- Fusion et push seulement si tout est vert et si les instantanés modifiés ne concernent que les doubles signes corrigés ; sinon push de la branche seule.
