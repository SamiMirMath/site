# Méthode de chantier — samimir.ch

À placer dans `docs/methode-chantiers.md`, et à citer dans `CLAUDE.md`.
Tirée du chantier « Étude complète » (02–04.11.2026). Elle complète `CLAUDE.md` et ne le remplace pas.

## Rôles

| Qui | Fait | Ne fait pas |
|---|---|---|
| **Enseignant** | Fournit le corrigé de référence, tranche les décisions, relit (instantanés, captures, texte rendu), fusionne et pousse | — |
| **Claude (claude.ai, projet)** | Rédaction attendue, `decisions.md`, prompts, tri des questions, relecture pédagogique | Ne touche pas au dépôt |
| **Claude Code** | Audit, code, tests, `suivi.md` et `journal.md`, commits sur la branche du chantier | Ne pousse jamais, ne fusionne jamais, ne modifie ni `CLAUDE.md` ni `decisions.md` |

## Étapes d'un chantier

0. **Référence.** Le corrigé de l'enseignant (`.tex`, PDF) va dans `docs/reference/<outil>/`, qui n'est jamais publié.
1. **Audit (étape 0, Claude Code, mode plan).**
   - Lire la référence et lancer le moteur sur ses exemples, avec un oracle mpmath.
   - Comparer, étape par étape : référence / outil / état.
   - Lister les dépendances et ce qu'un changement casserait ailleurs.
   - Rendre une liste de décisions à prendre, puis un découpage en parties.
   - Aucun fichier modifié, à part `docs/chantiers/<outil>/audit-etape0.md`.
2. **`decisions.md` (claude.ai).** Le fichier contient :
   - les **principes** : rien de faux, double confirmation SymPy et sonde, portée explicite, principe 6 (les M aiment les algorithmes et les nombres, pas les concepts) ;
   - les **décisions Dn**, chacune avec sa portée (outil seul ou outils partagés) ;
   - les **règles détaillées** ;
   - **un exemple entièrement rédigé** (texte cible) et les **résultats attendus** pour le corpus de tests ;
   - le **découpage** en parties, avec leurs dépendances.

   L'enseignant valide le fichier, et il fait foi : `CLAUDE.md` > `decisions.md` > `suivi.md` > audit.
3. **Exécution (Claude Code, de préférence de nuit).**
   - Une partie = un sous-agent = un commit, avec la suite complète verte avant le commit.
   - Pour une seule partie : pas de chef d'orchestre, la session principale fait le travail, avec `/clear` avant.
4. **Relecture.**
   - Le résumé en tête de `suivi.md`, puis les questions.
   - Tri dans `decisions.md` §7, §8… : ✓ confirmé · ✎ à changer (partie R1, R2…) · ⏸ à juger à l'écran · ⇥ hors chantier.
   - Les instantanés des **outils partagés** : avant / après.
   - Les captures à 390 px.
   - Le texte rendu de l'exemple cible.
5. **Corrections** (parties R1, R2…), puis **fusion** et **vérification sur iPhone**.

## Règles d'exécution (à recopier dans chaque prompt de nuit)

- `decisions.md` fait foi. Une question non réglée par ce fichier est notée sous « Questions pour l'enseignant » ; on prend alors l'option qui affiche le moins et on continue.
- Il est interdit d'affaiblir un test, un garde-fou ou une tolérance, et de marquer `xfail` un test qui passait. Les vérifications pas encore faites sont des `xfail` **stricts**, chacun avec le numéro de sa partie.
- Une partie qui touche un outil partagé liste chaque instantané modifié, avant / après, sous « À relire par l'enseignant ».
- Toute commande d'essai ou de mesure a une **limite de 5 minutes** (avec `subprocess` et un `timeout`, car la commande `timeout` n'existe pas sur macOS). Seule la suite complète n'a pas de limite.
- Après chaque partie, on note le temps natif d'`etudier()` (ou de son équivalent) sur le corpus, et on signale toute hausse de plus de 50 % au-dessus de 0,1 s.
- `suivi.md` reste **court** (état, questions ouvertes, à relire). Tout le détail (plans, tableaux, temps, rapports) va dans `journal.md`.
- En cas d'échec, on remet l'arbre au dernier commit, on décrit le blocage et on marque la partie « échec » ; le chef d'orchestre passe à la partie suivante si elle n'en dépend pas.
- Le test instable connu (`test_clavier.py::test_a_deux_formules…`) est relancé seul, jamais modifié.

## Organisation de nuit (plusieurs parties)

- La session principale est le **chef d'orchestre** : elle ne code pas.
- **Un sous-agent par partie**, l'un après l'autre, jamais en parallèle (même dossier, mêmes fichiers d'instantanés, même suite de tests).
- Chaque sous-agent est de type **general-purpose**, avec **`model: "opus"`** ; jamais Explore.
- Consigne de chaque sous-agent : lire `CLAUDE.md`, `decisions.md` et `suivi.md`, écrire son plan, exécuter, committer, puis rendre un rapport de 10 lignes au plus.
- Le chef d'orchestre vérifie `git log`, puis la suite. Selon les conclusions de l'audit tests-rapides, cette vérification pourra être allégée.
- Un dernier sous-agent écrit le résumé en tête de `suivi.md`, avec le texte rendu de l'exemple cible.

## Côté machine

- Lancer `caffeinate -i claude` (le Mac reste éveillé tant que Claude Code tourne). Mac branché, couvercle ouvert, sur une surface dure.
- Choisir Opus avec `/model`, le mode auto avec shift+tab, et faire `/clear` avant chaque nouvelle session.
- Une commande lancée en arrière-plan peut survivre à son agent. Si elle dure trop, l'arrêter depuis le panneau « Shell details » (touche `x`).
- Dans le relevé de consommation, quelques centimes de Haiku sont normaux : ce sont les tâches internes de Claude Code, pas les sous-agents.

## Fusion

- Coller **une commande à la fois**.
- `git merge --no-ff --no-edit <branche>` n'ouvre pas d'éditeur.
- Puis `git push`, `git branch -d <branche>`, et une vérification sur iPhone après un rechargement sans cache.

## Modèle de prompt de nuit

```
Chantier <nom> — exécution de nuit, sans moi.
decisions.md (docs/chantiers/<nom>/) fait foi (CLAUDE.md > decisions.md >
suivi.md > audit). Méthode : docs/methode-chantiers.md.
PARTIES : <liste dans l'ordre>. NE PAS faire : <liste>.
Dépendances : <…>.
ORGANISATION : section « Organisation de nuit » de la méthode.
PRÉCISIONS : <propres au chantier>.
RÈGLES : section « Règles d'exécution » de la méthode, mot pour mot,
recopiée dans la consigne de chaque sous-agent.
Fin : résumé en tête de suivi.md, avec le texte rendu de <exemple cible>.
```
