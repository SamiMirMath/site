# Suivi — refonte de la rédaction des limites (3M)

Branche `refonte-redaction-3m` (créée le 30.10.2026 depuis `main`, au commit de secours `40b3d8d`). **Rien n'est poussé, rien n'est fusionné.**
Cible : `docs/reference/limites/ch8-corrige-limites.pdf` (local, ignoré par git : documents de cours, jamais publiés ; les tests s'appuient sur les
transcriptions de la spécification). Contrat des tests : `docs/specifications/redaction-limites-3m.md`.
Décisions à valider : `docs/a-valider.md` (section « refonte de la rédaction »). Revue : `revue-matin.html` (même dossier ; la regénérer avec
`generer_revue_matin.py`).

## Jalons

| Jalon | État | Commit |
|---|---|---|
| 0. Version de secours sur `main` (8.12e retiré de la page) | fait, suite complète verte | 40b3d8d |
| A. Spécification + brouillons + `.gitignore` | fait | f2cd628 |
| B. Rendu (blocs `bh`, `encadre`, `resultat_lim`, `valeurs`, `sous_calcul`, cartes « Étape n ») | fait | 7c1be3d |
| C. Descente, BH détaillé, simplification à part, dérivées confirmées | fait (24 exercices du corrigé en descente) | 7c1be3d |
| D. Formes déterminées + « Attention », 0·∞, constante, `ln(x³)` | fait | 7c1be3d |
| E. Podium (t = x, −x, 1/x), tableau de valeurs, ✓ | fait | 7c1be3d |
| F. Exposant / ln (R16), « BH tourne en rond » (8.12 h), sous-limite « on calcule à part » (8.12 g), bord (R19) | fait ; 0⁻ de 8.12 f non couvert (voir plus bas) | 7c1be3d |
| G. Études 3.10 / 3.11 et Étude complète | fait : mêmes cartes (`cartes_etude`), `limites_bornes` signées (0⁺/0⁻), bilan inchangé sur le fond | 7c1be3d |
| H. Page : 8.12e remis, +5 exemples (8.11b, 8.12b, 8.12h, Ex6, 8.13c) | fait | 7c1be3d |

## Principe du moteur

- Nouveau module `limites-asymptotes/redaction_bh.py`, branché dans `_narrer_limite` (et dans `_narrer_cotes` pour les deux côtés) ; `Abandon` ⇒
  l'ancienne rédaction, sauf si elle viole R14 (forme indéterminée suivie de « = valeur ») : alors le message de repli.
- Chaque égalité écrite et chaque dérivée sont vérifiées numériquement avant affichage ; la valeur finale est comparée à la référence SymPy
  (garde-fou inchangé : `_rejete` + sonde mpmath) ; le signe est recoupé par une sonde mpmath (80 chiffres) ; la prédiction du podium est comparée au
  résultat (sinon elle est retirée et une entrée `alertes` est levée : le test correspondant échoue).
- Fractions rationnelles seules (sans exp ni ln) : méthodes anciennes inchangées (R18).

## Écarts mineurs avec le corrigé (tolérés par les tests)

- 8.11 a : « on remplace » au lieu de « on remplace à nouveau ».
- 8.11 c et d : la forme revérifiée entre deux BH est écrite sous la chaîne (« Forme −∞/−∞ : encore indéterminée ») ; le corrigé la met dans une étape à part ou à droite de la ligne ; en 8.11 d, l'outil ajoute l'étape « on vérifie la forme » et finit par « on remplace ».
- Ex5 a : deux étapes BH détaillées au lieu de « BH deux fois » condensé.
- 8.12 d et 8.14 : « BH » puis « on simplifie » en deux étapes au lieu de « BH et simplification » ; en 8.12 d la forme finale est −1/(x e^(−x)).
- Simplifications : l'étape « on simplifie » écrit « fraction ÷ fraction = fraction × inverse = forme réduite » ; les intermédiaires du corrigé
  (−x⁴/(3x) = −x³/3) ne sont pas reproduits.
- 8.12 g : « On calcule à part… » avec sous-calcul complet au lieu de la citation de l'exemple 5 b) ; pas d'encadré « Autre méthode ».
- 8.13 f : pas de ligne « Autre façon : ln(1/x) = −ln(x) ». 8.11 b : pas de remarque sur le graphe de ln en 0⁺.
- Dans la prédiction, le signe n'est justifié par « pour x > 1 » etc. que sous la forme « > 0 / < 0 » (pas de condition sur x).

## Limites connues (repli ou ancienne rédaction, jamais d'étape fausse)

- Bornes encore en ancienne rédaction ou repli : voir le tableau du « reste du corpus » en bas de `revue-matin.html` (13 replis au plus : test).
  Cas typiques : exposant `a^x` (3.8 g′), signe de pôles irrationnels, `x·eˣ/(1 − eˣ)` (forme indéterminée imbriquée), sommes d'exponentielles
  `e^x − x²` (mise en évidence, ancienne rédaction).
- 8.12 f en 0⁻ (`e^(1/x)/x²`) : BH tourne en rond puis sous-limite non couverte → ancienne rédaction ou repli (le corrigé ne traite que 0⁺).
- Fonctions rationnelles : inchangées (R18).

## Tests

- Nouveau : `tests/python/test_redaction_bh_3m.py` (contrat des 24 exercices, structure R9/R11/R14, cartes, transverses).
- Adaptés : `test_redaction_limites.py` (les tests de l'ancienne rédaction passent par `@ancienne_redaction`, qui désactive la nouvelle ; les
  phrases exactes de cas sans forme indéterminée sont réécrites pour la descente), `test_doctrine_bh.py` (le mot « podium » n'est permis que dans
  les encadrés de prédiction et la ligne de confirmation), `test_resoudre_la.py` / `test_resoudre_ec.py` (cartes « Étape n » : `titres_etude`),
  `test_resoudre_import.py`, `test_limites_deux_cotes.py` (bord vs trou), `test_corpus_limites_3m.py` (le xfail du signe 0⁺/0⁻ passe : retiré).
- Instantanés (Python et pages) régénérés : les diffs ne touchent que Limites et Étude complète.

## Mesures de temps (Pyodide, Chrome sans interface sur le Mac de développement) — plafond 6 s par fonction

Mesure du 30.10.2026 sur les 14 exemples de la page et les 26 autres saisies du corpus (40 fonctions, page déjà chargée) : **maximum 4,5 s**
(`x*e^x/(1-e^x)`, ancienne rédaction en repli de la descendante), moyenne 0,6 s. Page : `ln(x^2-3)/(2-x)` 2,1 s ; tous les autres exemples ≤ 1,1 s.
Le premier calcul d'une session est plus lent (chargement de SymPy). Le test `test_limites_exemples_et_rappel_a_360_px` impose désormais < 6 s.
Avant correction, `e^(-2x/(x^2-5))` demandait 7,6 s (5,9 s de `sympy.limit` en 4 points irrationnels) : la limite de `e^u` / `ln u` est maintenant
cherchée par composition d'abord (`_limite_brute`), 0,6 s ; la sonde mpmath contrôle toujours le résultat.

## État des tests

Suite complète du 30.10.2026 (commit des jalons B-H) : 904 passed (Python) + 62 passed (pages, 360 px compris), code de retour 0.
Test de fumée du jalon A : 20 passed.

## Fusion (si validé)

    git switch main && git merge --no-ff refonte-redaction-3m
