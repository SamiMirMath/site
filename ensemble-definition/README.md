# Ensemble de définition — calcul détaillé

Site statique : la page `index.html` charge Python dans le navigateur (Pyodide) puis le moteur de cet outil, qui fait tout
le calcul. Aucun serveur Python n'est nécessaire.

## Fichiers
- `ensemble_def.py` — moteur de calcul, Python pur (SymPy facultatif, voir plus bas) ; c'est aussi la base du noyau commun
  des autres outils (`moteur/noyau.py`).
- `resoudre_ed.py` — adaptateur : met le résultat au format de sortie commun (`moteur/sortie.py`) que la page affiche, et
  compose la phrase du contrôle numérique.
- `index.html` — page de l'outil, montée par `commun/outil.js` ; les fichiers Python chargés sont listés dans
  `moteur/manifeste.json`.

## Mise en ligne
Le site entier (branche `main`) est publié par GitHub Pages ; voir `docs/README.md`.
Lien direct vers un calcul : `…/ensemble-definition/?f=ln(x^2-4)/(x-5)`.

## Test en local
Ouvrir le fichier par double-clic ne marche pas (le navigateur bloque la lecture du `.py`).
À la racine du dépôt (la page lit `../commun/` et `../moteur/`) :

```
python3 -m http.server
```
puis ouvrir http://localhost:8000/ensemble-definition/.

Le moteur s'utilise aussi seul :
```
python3 ensemble_def.py "ln(x)/(ln(x)+2)" "sqrt(x^2+2x-3)"
```

## Comment le moteur résout chaque condition (du plus exact au plus robuste)
1. **Méthode exacte détaillée** (Python pur) : polynômes, fractions rationnelles, Δ, racines évidentes,
   tableau de signes ; substitution `t = ln(B)`, `t = e^B`, `t = √B` puis retour à x.
   Sommes de logarithmes : sur le domaine D des ln, `ln(a)+ln(b) = ln(ab)`, `ln(a)−ln(b) = ln(a/b)`, `n ln(a) = ln(aⁿ)`,
   puis résolution et tri des solutions selon D. Trinômes de second membre irrationnel (`x²+1 = e²`) par la forme canonique.
2. **Produit / quotient de facteurs** : si la condition mélange x et ln/exp/√ (ex. `x·ln(x+2) ≥ 0`),
   signe de chaque facteur puis tableau de signes global (zones hors domaine hachurées ×).
   Si l'expression n'est pas écrite en produit, **SymPy** la factorise (`x ln(x+2) + x = x(ln(x+2)+1)`).
3. **SymPy** (`solveset`) pour un facteur que la méthode exacte ne sait pas traiter.
4. **Dichotomie numérique** en dernier recours (ex. `ln(x) - x + 2 = 0`) : valeurs approchées notées ≈.

Après chaque calcul, un **contrôle numérique indépendant** évalue f en ~5000 points et vérifie
qu'elle est définie exactement dans l'ED trouvé.

Python tourne dans un Web Worker (Pyodide 0.27.7, SymPy 1.13.3 inclus) : la page ne se fige jamais ;
un calcul de plus de 30 s est interrompu et le moteur relancé.

Moteur testé sur les exercices A.1–A.3 de la fiche et sur ~1000 fonctions générées au hasard
(avec et sans SymPy), comparées au contrôle numérique.

Test en ligne de commande avec SymPy : `pip install sympy`, puis `python3 ensemble_def.py "sqrt(x ln(x+2))"`.
