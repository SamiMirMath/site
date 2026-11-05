# Tests rapides : décisions

À placer dans `docs/chantiers/tests-rapides/decisions.md`.
Ordre de priorité : **CLAUDE.md > ce fichier > audit.md**. Méthode : `docs/methode-chantiers.md`.
Validé par l'enseignant le 04.11.2026.

---

## 0. Principe absolu

Ce chantier touche à ce qui vérifie tous les autres. Une erreur ici rendrait la suite **verte à tort**. D'où trois règles :

1. **Le même ensemble de tests, nom par nom.** Après chaque partie, la liste des identifiants collectés, passés, xfail et sautés est **identique** à la référence de P0. Les nombres de sous-tests aussi (voir §2 pour les pages).
2. **Aucun test retiré, sauté, affaibli ni raccourci.** Pas d'oracle allégé, pas de corpus réduit dans `complet`, pas de tolérance élargie, pas de délai d'attente allongé pour faire passer un test.
3. **Un cache ne remplace jamais le moteur.** Il est explicite, il rend une **copie profonde**, et un interrupteur `MEMO=0` le coupe. En fin de session, une suite complète est lancée **avec `MEMO=0`** et doit donner les mêmes listes.

---

## 1. Décisions

| n° | Mesure de l'audit | Décision |
|---|---|---|
| T1 | M1, contrôle allégé du chef d'orchestre | **Oui.** `lancer.py complet --rapport <dossier>` et `lancer.py verifier <dossier>`, comme dans l'audit §M1 (empreintes, fichiers non suivis, codes, listes). **Un test qui disparaît** par rapport à la partie précédente fait refuser `verifier`. Le chef d'orchestre n'accepte qu'un renommage justifié dans `suivi.md` (ancien nom → nouveau nom, raison). Une suite complète est relancée par le chef d'orchestre en fin de session. |
| T2 | M2, test du clavier | **Oui**, dans le harnais seulement (`navigateur.py`), comme dans l'audit §2.3. Le recentrage est borné à 3 essais, et une erreur explicite est levée si l'élément n'est pas sous le doigt. La page n'est pas modifiée. |
| T3 | M3, boucle quadratique de `TestStructure` | **Oui.** Calcul une fois par classe, copie profonde par test. |
| T4 | M4, cache de l'outil Limites | **Oui, par fichier entier** : seuls les fichiers **sans aucun `mock`** importent `memo`. Pas de cache classe par classe dans un fichier qui contient des `mock`. Un test de garde le vérifie. Interrupteur `MEMO=0`. |
| T5 | M5, cache de `racines` | **Oui.** La clé doit être injective (à démontrer dans `suivi.md`), le résultat est rendu en copie, et la comparaison avec et sans cache est faite une fois. **Interdit** de modifier `racines` elle-même. |
| T6 | P6 de l'audit (`xdist_group`) | **Non pour l'instant** : risque de chemin critique sur un worker, pour un gain incertain. À rediscuter avec des mesures. |
| T7 | M6, `rapide` et pages des moteurs | **Oui.** `complet` ne change pas. |
| T8 | M7, navigateur partagé | **Non** (gain inférieur à 20 s). |
| T9 | M8, étude du chargement de Pyodide | **Oui, en étude seule** : mesures et rapport `docs/chantiers/tests-rapides/etude-pyodide.md`, **aucun code modifié**. On décidera ensuite. |
| T10 | Documentation | Claude Code **ne modifie pas `CLAUDE.md`**. Il écrit dans `suivi.md` le texte proposé pour `CLAUDE.md` (nouvelles mesures de temps, `--rapport`, `verifier`, `MEMO=0`) ; l'enseignant le reporte lui-même. Il **peut** mettre à jour `docs/methode-chantiers.md` (section « Organisation de nuit » : le contrôle allégé), dans un commit séparé. |

---

## 2. Référence (P0)

- Deux lancements de `complet` sur le commit de départ, avec `--junitxml` et `--collect-only -q`. Les listes sont gardées dans `docs/chantiers/tests-rapides/reference/` (commitées : elles servent de preuve).
- **Si les sous-tests de pages varient** entre les deux lancements (tirages au hasard), trouver la source et la noter dans `suivi.md`. La comparaison porte alors sur les **noms** des tests et sur les sous-tests des fichiers stables. On ne change rien aux tirages.
- Le premier commit verse aussi `audit.md` et ce fichier.

---

## 3. Découpage

| Partie | Contenu | Vérification propre |
|---|---|---|
| P0 | `suivi.md` (court) et `journal.md` ; deux lancements de référence ; option `--rapport` de `lancer.py` | Le rapport du 2ᵉ lancement reproduit les listes du 1ᵉʳ |
| P1 | T2 : harnais du toucher | Le test du clavier lancé 20 fois seul, puis 20 fois sous charge (2 processus) : 40 sur 40 ; listes identiques |
| P2 | T1 : `lancer.py verifier` ; texte proposé pour `CLAUDE.md` (dans `suivi.md`) ; mise à jour de `docs/methode-chantiers.md` (commit séparé) | Essais de l'audit §M1 : commit modifié refusé, fichier non suivi signalé, test disparu refusé |
| P3 | T3 : `TestStructure` | Listes et sous-tests identiques ; mur Python mesuré |
| P4 | T4 : `memo.py`, test de garde, `MEMO=0` | Listes identiques avec et sans `MEMO=0` |
| P5 | T5 : cache de `racines` | Racines identiques avec et sans cache, pour toutes les clés ; listes identiques |
| P6 | T7 : `rapide` et pages des moteurs | `lancer.py liste` sur des modifications simulées ; `complet` inchangé |
| P7 | T9 : étude du chargement de Pyodide (rapport seul) | Aucun fichier de code modifié (`git diff --stat` le montre) |

Ordre : P0 d'abord ; P1 tôt, car un test qui échoue au hasard gêne toutes les parties suivantes. Les autres parties sont indépendantes entre elles.

**Fin de session** :
1. le chef d'orchestre lance une suite complète normale sur le dernier commit ;
2. il lance une suite complète avec `MEMO=0` ;
3. il compare les deux aux listes de référence ;
4. il note les murs avant / après dans le résumé.

**Bilan attendu** (audit) : suite Python d'environ 718 s → 520 à 560 s ; suite de pages sans échec au hasard ; environ 25 à 28 min par partie de chantier au lieu d'environ 60.
