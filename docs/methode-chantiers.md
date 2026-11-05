# Méthode de chantier — samimir.ch

Tirée du chantier « Étude complète » (02–04.11.2026). Elle complète `CLAUDE.md` et ne le remplace pas.

## Rôles

| Qui | Fait | Ne fait pas |
|---|---|---|
| **Enseignant** | Fournit le corrigé de référence, tranche les décisions, relit (instantanés, captures, texte rendu), fusionne et pousse | — |
| **Claude (claude.ai, projet)** | Rédaction attendue, `decisions.md`, prompts, tri des questions, relecture pédagogique | Ne touche pas au dépôt |
| **Claude Code** | Audit, code, tests, `suivi.md` et `journal.md`, commits sur la branche du chantier | Ne pousse et ne fusionne que si le prompt l'autorise ; ne modifie ni `CLAUDE.md` ni `decisions.md` sans accord explicite |

## Étapes d'un chantier

0. **Référence** : le corrigé de l'enseignant (`.tex`, PDF) va dans `docs/reference/<outil>/`, ignoré par git, jamais publié.
1. **Audit (étape 0, Claude Code)** : lire la référence, lancer le moteur sur ses exemples avec un oracle mpmath, comparer étape par étape (référence / outil / état), lister les dépendances et ce qu'un changement casserait, proposer les décisions à prendre et un découpage. Aucun fichier modifié sauf `docs/chantiers/<outil>/audit-etape0.md`.
2. **`decisions.md` (claude.ai)** : principes (rien de faux, double confirmation SymPy et sonde, portée explicite, principe 6 : les M aiment les algorithmes et les nombres, pas les concepts), décisions Dn avec leur portée, règles détaillées, un exemple entièrement rédigé (texte cible), résultats attendus pour le corpus, découpage avec dépendances. Validé par l'enseignant, il fait foi : `CLAUDE.md` > `decisions.md` > `suivi.md` > audit.
3. **Exécution (Claude Code, de préférence de nuit)** : une partie = un sous-agent = un commit, suite complète verte avant le commit. Pour une seule partie, pas de chef d'orchestre : la session principale fait le travail, après `/clear`.
4. **Relecture** : résumé en tête de `suivi.md`, questions triées dans `decisions.md` (§7, §8… : ✓ confirmé · ✎ à changer · ⏸ à juger à l'écran · ⇥ hors chantier), instantanés des outils partagés (avant / après), captures à 390 px, texte rendu de l'exemple cible.
5. **Corrections** (parties R1, R2…), puis fusion et vérification sur iPhone.

## Règles d'exécution (à recopier dans chaque prompt de nuit)

- `decisions.md` fait foi. Une question non réglée est notée sous « Questions pour l'enseignant » ; on prend l'option qui affiche le moins et on continue.
- Interdit d'affaiblir un test, un garde-fou ou une tolérance, ou de marquer `xfail` un test qui passait. Les vérifications pas encore faites sont des `xfail` **stricts**, chacun avec le numéro de sa partie.
- Une partie qui touche un outil partagé liste chaque instantané modifié, avant / après, sous « À relire par l'enseignant ».
- Toute commande d'essai ou de mesure est limitée à **5 minutes** (avec `subprocess` et un `timeout`). Seule la suite complète n'a pas de limite.
- Après chaque partie : temps natif d'`etudier()` (ou équivalent) sur le corpus ; signaler toute hausse de plus de 50 % au-dessus de 0,1 s.
- `suivi.md` reste **court** (état, questions ouvertes, à relire) ; tout le détail (plans, tableaux, temps, rapports) va dans `journal.md`.
- En cas d'échec : remettre l'arbre au dernier commit, décrire le blocage, marquer « échec » ; passer à la partie suivante si elle n'en dépend pas.
- Le test instable connu (`test_clavier.py::test_a_deux_formules…`) est relancé seul, jamais modifié.

## Organisation de nuit (plusieurs parties)

- La session principale est le **chef d'orchestre** : elle ne code pas.
- **Un sous-agent par partie**, l'un après l'autre, jamais en parallèle (même dossier, mêmes instantanés, même suite).
- Sous-agents de type **general-purpose**, avec **`model: "opus"`** ; jamais Explore.
- Consigne de chaque sous-agent : lire `CLAUDE.md`, `decisions.md` et `suivi.md`, écrire son plan, exécuter, committer, rendre un rapport de 10 lignes au plus, avec le dossier de `complet --rapport`.
- Le chef d'orchestre vérifie chaque partie par le **contrôle allégé** (chantier tests-rapides, décision T1) ; il ne relance plus la suite
  complète après chaque partie :
  1. le sous-agent lance sa suite complète d'avant commit avec `python3 tests/lancer.py complet --rapport <dossier>` (dossier hors du
     dépôt, par exemple dans le scratchpad), commite, puis donne ce dossier dans son rapport ;
  2. le chef d'orchestre lance `git log --oneline -3` (un seul commit de plus, sur la branche du chantier), puis
     `python3 tests/lancer.py verifier <dossier>` : il exige `VERDICT : ACCEPTÉ`. `verifier` refuse si le commit n'est pas exactement
     ce que la suite a testé (empreintes), si un autre fichier était modifié ou non suivi pendant le lancement, si un code de retour
     n'est pas 0, si un test disparaît ou est sauté en plus, si une issue se dégrade ou si des sous-tests manquent ;
  3. il lance ensuite `python3 tests/lancer.py rapide`, un contrôle indépendant de quelques minutes (sur l'arbre propre d'après le
     commit, il ne relance aujourd'hui que les tests de fumée : question ouverte du chantier tests-rapides) ;
  4. il note une ligne dans `journal.md`, section « Contrôles du chef d'orchestre » (commit, verdict, nombres, murs).
- **Un test disparu fait refuser `verifier`.** Le chef d'orchestre n'accepte qu'un **renommage justifié dans `suivi.md`** (ancien nom →
  nouveau nom, raison) ; pour les parties suivantes, il compare alors au dossier de cette partie
  (`verifier <dossier> --reference <dossier de la partie acceptée>`). Tout autre refus : la partie est en échec (règles d'exécution).
- **Une suite complète en fin de session** : le chef d'orchestre la relance lui-même sur le dernier commit
  (`complet --rapport <dossier>`, puis `verifier <dossier>` et `python3 tests/comparer_listes.py <référence> <dossier>`).
- Un dernier sous-agent écrit le résumé en tête de `suivi.md`, avec le texte rendu de l'exemple cible.
- En lecture seule (audits, revues), plusieurs sous-agents peuvent travailler en parallèle.

## Machines

- **Une machine par chantier** ; `git pull` avant de commencer, branche poussée en fin de session.
- Mac : `caffeinate -i claude`, branché, couvercle ouvert. PC (WSL2 Ubuntu) : alimentation « jamais de mise en veille ». Première installation : `python3 tests/pages/pyodide_local.py`.
- `/model` Opus, mode auto (shift+tab), `/clear` avant chaque session.
- Une commande en arrière-plan peut survivre à son agent : l'arrêter depuis le panneau « Shell details » (touche `x`).
- Quelques centimes de Haiku dans le relevé de consommation sont normaux (tâches internes), pas des sous-agents.

## Fusion

Une commande à la fois. `git merge --no-ff --no-edit <branche>` n'ouvre pas d'éditeur. Puis `git push`, `git branch -d <branche>`, et vérification sur iPhone après rechargement sans cache.

## Modèle de prompt de nuit

```
Chantier <nom> — exécution de nuit, sans moi.
decisions.md (docs/chantiers/<nom>/) fait foi (CLAUDE.md > decisions.md >
suivi.md > audit). Méthode : docs/methode-chantiers.md.
PARTIES : <liste dans l'ordre>. NE PAS faire : <liste>.
Dépendances : <…>.
ORGANISATION : section « Organisation de nuit » de la méthode.
PRÉCISIONS : <propres au chantier>.
RÈGLES : section « Règles d'exécution » de la méthode, recopiée mot pour
mot dans la consigne de chaque sous-agent.
Fin : résumé en tête de suivi.md, avec le texte rendu de <exemple cible>.
```
