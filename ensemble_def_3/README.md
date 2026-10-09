# Ensemble de définition — calcul détaillé

Site statique : la page `index.html` charge Python dans le navigateur (Pyodide) puis exécute
`ensemble_def.py`, qui fait tout le calcul. Aucun serveur Python n'est nécessaire.

## Fichiers
- `ensemble_def.py` — moteur de calcul, Python pur (aucune dépendance).
- `index.html` — interface (mobile), rendu des formules avec KaTeX.

Les deux fichiers doivent être **dans le même dossier**.

## Mise en ligne sur GitHub Pages
1. Déposer `index.html` et `ensemble_def.py` dans un dépôt (ou un sous-dossier, ex. `ensemble-definition/`).
2. Settings → Pages → Source : branche `main`, dossier `/ (root)`.
3. Le site est à `https://<utilisateur>.github.io/<depot>/` (ajouter le sous-dossier le cas échéant).

Lien direct vers un calcul : `…/index.html?f=ln(x^2-4)/(x-5)`.

## Test en local
Ouvrir le fichier par double-clic ne marche pas (le navigateur bloque la lecture du `.py`).
Dans le dossier :

```
python3 -m http.server
```
puis ouvrir http://localhost:8000.

Le moteur s'utilise aussi seul :
```
python3 ensemble_def.py "ln(x)/(ln(x)+2)" "sqrt(x^2+2x-3)"
```

## Ce que le moteur sait faire
- Conditions : argument de `ln` > 0, dénominateur ≠ 0, contenu de `sqrt` ≥ 0 (aussi `x^(1/2)`, `x^(-2)`…).
- Résolution exacte : polynômes et fractions rationnelles (racines évidentes, discriminant, racines en √),
  tableau de signes complet avec valeurs interdites ‖.
- Substitution `t = ln(B)`, `t = e^B`, `t = √B` puis retour à x (ex. `e^(2x)-5e^x+6`, `(ln x)^2-1`, `ln(ln x)`).
- Non pris en charge (message clair) : conditions transcendantes mixtes comme `x - ln(x) ≠ 0`.
