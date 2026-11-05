# Chantier « Portage PC » — journal

## Lancement de départ (référence)

`python3 tests/lancer.py complet --rapport <scratchpad>/ref-main` sur `main` (c9b257f), sans `PROCESSUS_PAGES` (donc `-n 2`), avant toute
modification : code 0. Python 1317 passés + 1 xfail, 101 952 sous-tests, 96 s ; pages 123 passés, 2 386 sous-tests, 545 s.
Fichiers non suivis pendant le lancement (non lus par les tests) : `docs/architecture.md`, `docs/chantiers/equations-2e-degre/quiz.md`,
`docs/chantiers/portage-pc/diagnostic.md`, `docs/chantiers/revue-structure/rapport.md`.

Comparé à l'ancienne référence `docs/chantiers/tests-rapides/reference` (commit 7268412) : 89 différences Python, 6 de pages, celles déjà
décrites dans le résumé de `tests-rapides` (§0 : réconciliation avec `origin/main`). Ce lancement sert de nouvelle référence (point 2).

## Point 1 — PROCESSUS_PAGES

- Valeurs refusées avec le code 2 et un message, avant tout lancement (rapide, pages, complet) : `''`, `0`, `-1`, `abc`, `4.0`, `' 4'`,
  `04`. Acceptées : absente → 2, `1`, `4`, `12`. `liste` et `verifier` ne lisent pas la variable.
- Commande des pages (fonction `lancer` remplacée par un relevé) : sans la variable, `-n 2` et le reste identique à `main` (complet et
  rapide à corpus réduit) ; avec 4, seul `-n 4` change.
- Suites complètes (`--rapport`, scratchpad) sur l'arbre du point 1 :

| Lancement | Code | Python | Pages | Listes |
|---|---|---|---|---|
| `p1-n4` (`PROCESSUS_PAGES=4`) | 0 | 92 s | **299 s** | identiques à la référence, nom par nom |
| `p1-n2` (absente) | 1 | 94 s | 548 s | test instable du clavier échoué (KaTeX non chargé depuis jsDelivr : `net::ERR_CERT_VERIFIER_CHANGED`, cause réseau) ; relancé seul : passé, 2 sous-tests |
| `p1-n2b` (absente, relancé) | 0 | 87 s | 548 s | identiques à `p1-n4`, nom par nom |
