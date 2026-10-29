# Suivi — refonte de la rédaction des limites (3M)

Branche `refonte-redaction-3m` (créée le 30.10.2026 depuis `main`, au commit de secours `40b3d8d`). **Rien n'est poussé, rien n'est fusionné.**
Cible : `docs/reference/limites/ch8-corrige-limites.pdf` (local, ignoré par git). Contrat des tests : `docs/specifications/redaction-limites-3m.md`.
Décisions à valider : `docs/a-valider.md` (section « refonte de la rédaction »).

## Jalons

| Jalon | État | Commit |
|---|---|---|
| 0. Version de secours sur `main` (8.12e retiré de la page) | fait, suite complète verte | 40b3d8d |
| A. Spécification + brouillons | en cours | |
| B. Rendu (blocs, cartes « Étape n ») | à faire | |
| C. Descente, BH détaillé, simplification à part | brouillon fonctionnel (8.11 a, 8.12 a–e, 8.14 vus à l'écran) | |
| D. Formes déterminées, 0·∞, constante | brouillon | |
| E. Podium, tableau de valeurs, ✓ | brouillon | |
| F. Exposant / ln, « tourne en rond », bords | à faire | |
| G. Études 3.10 / 3.11, Étude complète | à faire | |
| H. Page (exemples, rappel) | à faire | |

## Décisions

- Le moteur est un nouveau module `limites-asymptotes/redaction_bh.py` branché dans `_narrer_limite` ; toute exception `Abandon` retombe sur
  l'ancienne rédaction (ou sur le repli, voir `a-valider.md`). Les brouillons sont dans `brouillons/` (sauvegarde : /private/tmp peut être vidé).
- Chaque égalité écrite et chaque dérivée sont vérifiées numériquement avant affichage ; la valeur finale doit coïncider avec la référence
  SymPy (garde-fou inchangé) et le signe avec une sonde mpmath ; la prédiction du podium est comparée au résultat (sinon retirée, entrée `alertes`).

## Écarts mineurs avec le corrigé

(à compléter au fil des jalons)

## Mesures de temps (Pyodide)

(à compléter : plafond 6 s par fonction)

## État des tests

Suite complète sur `main` au commit de secours : 877 passed + 62 passed (pages), rc=0.

## Fusion (si validé)

    git switch main && git merge --no-ff refonte-redaction-3m
