# Chantier « Mise en page fluide et modulaire » — suivi

Demande du 30.10.2026 (simplexe + tout le site), d'après les retours d'élèves sur iPhone : formulaires trop larges, coupures de lignes au hasard,
figures trop chargées, bouton « Étape suivante » trop loin.
Branche `mise-en-page-fluide` (créée depuis `main` après vérification : `refonte-redaction-3m` d3cce68 et les commits du simplexe 53d09a6, cf896a1,
e1f25ef, c9fd212 sont dans `main`). Rien n'est poussé ni fusionné. Un commit par phase, un commit par outil en phase 4 ; suite complète verte
(`python3 tests/lancer.py complet`, code de retour lu sans pipe) avant chaque commit.
Plan détaillé : `/Users/samimir/.claude/plans/pasted-content-id-3a8a-chantier-sparkling-tulip.md`.

**Reprise après compactage** : relire ce fichier, `git log --oneline main..HEAD`, puis reprendre à la première phase qui n'est pas « faite ».

## Décisions

- Contrainte du simplexe : au plus deux lignes dès 390 px (2D et 3D) ; une contrainte 3D fait exactement deux lignes à 390 px.
- L'accueil (`index.html`) est hors chantier : seuls les 7 outils du registre sont balayés et migrés.
- Les « xfail » du balayage sont un tableau `CONNUS` strict dans `tests/pages/test_largeurs.py` (la CI lance `unittest discover`, qui ne connaît pas xfail par outil).
- Noms d'axes : dans les figures de la **méthode géométrique** seulement, « x₁ / x₂ » devient « x / y » (comme le reste de cette méthode) ; la méthode
  algébrique garde x₁ / x₂. Autorisé par l'enseignant le 30.10.2026.
- Hauteur variable du canvas (3d) : la conversion écran → coordonnées doit rester exacte ; test d'appui sur un sommet (Explorer, 390 et 1100 px).
- Passage en module ES : test qui ouvre chaque page modifiée, lance un exemple et échoue sur toute erreur de console ou exception non attrapée.

| Phase | Sujet | État |
|---|---|---|
| 0 | Branche, conditions, suivi | **faite** (inclus dans le commit de la phase 1) |
| 1 | Règle et composants communs (`composants.css`, `composants.js`) | **faite** (suite complète verte : 911 + 80) |
| 2 | Test de balayage des largeurs (`test_largeurs.py`), rapport initial | à faire |
| 3 | Simplexe | à faire |
| 4 | Autres outils, un commit par outil | à faire |
| 5 | Fin : suivi complet, commande de fusion, résumé | à faire |

## Phase 1 — règle et composants communs

- Règle : `docs/specifications/socle-commun.md`, section « Mise en page fluide » (sous « Visuel et mobile ») ; renvoi depuis R14 de `docs/guide-redaction.md`.
- `commun/composants.css` : `.champ-signe` (+ `.membre`), `.onglets`, `.carte-etape`, `.bouton-flottant`, `.insecable`, `.flux`, `.conteneur-fluide`, `.cadre-fluide`.
  Aucune largeur d'écran en pixels. Le bouton flottant de `style.css` (`button.flottant`) n'est pas encore remplacé : c'est fait en phase 4 (premier outil).
- `commun/composants.js` (module ES) : `monterOnglets`, `champSigne`.
- Test statique : `tests/python/test_composants.py`.
