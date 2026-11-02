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
| P0 | `suivi.md`, corpus + oracle mpmath, xfail marqués avec leur partie | tests | **fait** | voir `git log` (« EC P0 ») |
| P1 | D6, D7 (parenthèses, doublons), D17 | Dérivée | à faire | |
| P2 | Squelette des 6 parties titrées (D1), spécification (D2, D19) | EC | à faire | |
| P3 | Partie 1 : mise en forme + ED détaillé (D3) | EC | à faire | |
| P4 | Partie 2 : parité (D4) | EC | à faire | |
| P5 | Partie 3 : zéros, signe, f(0) (D5) | EC | à faire | |
| P6 | Partie 4 : D12, D13, D16 | Limites | à faire | |
| P7a | Dérivée de l'exposant détaillée, tableau u/v (D7, D8, D7b si simple) | Dérivée | à faire | |
| P7b | Valeurs dans le tableau de variations (D10), extremums (D11) | EC + Dérivée | à faire | |
| P8 | Graphe (D15, §3) | EC | à faire | |
| P9 | Exemples (D18), Bilan (D20), instantanés, largeurs 320–390 px, mesure Pyodide | EC | à faire | |
| P10 | *(facultatif)* Pente au point exclu (D14) | EC | à faire | |

## Résumé de la nuit

- **P0 faite** : branche `etude-complete` ; `audit-etape0.md` (copie inchangée du rapport d'audit) et `decisions.md` versés au dépôt ; corpus
  Ex7, a–d avec les résultats de decisions.md §4–5 ; oracle mpmath (fonctions écrites à la main) : tout le corpus est confirmé ; les valeurs de
  l'outil (ED, extremums, signe de f′, limites du tableau, asymptotes, fenêtre) sont justes ; 66 vérifications de rédaction marquées xfail (P1 à P10).
  Aucun changement du moteur.

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

## Temps natif de etudier() (s, médiane de 3 processus neufs)

| Partie | Ex7 | a | b | c | d |
|---|---|---|---|---|---|
| P0 | 0,59 | 0,02 | 0,42 | 0,18 | 0,30 |

## Suite complète

| Partie | Suite Python | Suite de pages | Date |
|---|---|---|---|
| P0 | 1052 passés, 66 xfail (659 s) | 116 passés (885 s) ; code de retour 0 | 02.11.2026 |

## Écarts acceptés

- P0 : le test du corpus est écrit en fonctions pytest (et non en `unittest.TestCase` comme les autres) : `parametrize` permet une marque xfail
  par fonction du corpus, donc de ne marquer que les cas qui échouent vraiment.

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

## À relire par l'enseignant

- P0 : rien (aucun changement du moteur, aucun instantané modifié).
