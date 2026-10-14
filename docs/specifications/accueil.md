# Accueil et registre des outils

## Fonctionnel

- Présentation (titre, phrase d'accueil, ruban de Möbius décoratif).
- Choix de la filière (C, Ms, Mr ou « tous ») mémorisé dans le navigateur ; « changer » pour revenir
  au choix. Une année sans outil pour la filière choisie est masquée.
- Pour chaque année (I, II, III) et chaque filière : liste des outils (titre + description + lien).
- **Sans JavaScript** : tous les outils de toutes les filières sont visibles et les liens
  fonctionnent (le choix de filière est une amélioration apportée par le JS).
- Pied de page « © 2026 Sami Mir · samimir.ch ».

## Registre `commun/registre.json`

Source unique de la liste des outils, lue par les tests (l'accueil reste du HTML écrit à la main).

```json
{
  "outils": [
    {
      "id": "factorisation",
      "chemin": "factorisation/",
      "titre": "Factorisation",
      "description": "Mise en évidence, identités remarquables, Somme-Produit, groupements… étape par étape.",
      "filieres": {"1": ["C", "Ms", "Mr"]}
    },
    {
      "id": "simplexe",
      "chemin": "simplexe/",
      "titre": "Programmation linéaire",
      "description": "…",
      "filieres": {"2": ["C", "Mr"]},
      "parametres": {"C": "?methode=geometrique", "Mr": "?methode=algebrique"},
      "descriptions": {"C": "Méthode géométrique, pas à pas.", "Mr": "Méthode algébrique (simplexe), pas à pas."}
    }
  ]
}
```

Répartition du simplexe (validée, Q2) : 2C → méthode géométrique, 2Mr (OS) → méthode algébrique,
rien en 2Ms (l'accueil reste « Outils en préparation » en 2Ms). Chaque filière reçoit sa
description et son lien direct. `descriptions` remplace `description` quand elle
diffère selon la filière.

## Ruban de Möbius

- L'animation s'arrête quand le canvas sort de l'écran ou que l'onglet est caché, et reprend ensuite.
- Image fixe si `prefers-reduced-motion: reduce` (comportement actuel conservé).
- Les couleurs suivent un changement de thème clair/sombre sans recharger la page.

## Critères d'acceptation

| Id | Critère | Vérif. |
|---|---|---|
| ACC-01 | L'ensemble des couples (année, filière, chemin, titre, description) présents dans `index.html` est exactement celui du registre | [auto-py] |
| ACC-02 | Chaque `chemin` du registre existe et contient un `index.html` | [auto-py] |
| ACC-03 | Sans JavaScript, tous les liens d'outils sont visibles (aucune règle CSS ne masque `#content` en l'absence de `data-track`) | [auto-py] (analyse CSS) + [auto-page] JS désactivé |
| ACC-04 | Avec JS, choisir « Ms » masque les années sans outil Ms et affiche le choix courant | [auto-page] |
| ACC-05 | Le texte doré (`--gold`) a un contraste ≥ 4,5:1 sur `--paper` et `--paper-raised` (ex. `#84672c` : 4,9:1) ; le mode sombre reste ≥ 4,5:1 | [auto-py] |
| ACC-06 | L'animation ne consomme aucune image (`requestAnimationFrame`) quand le canvas est hors écran | [auto-page] |
| ACC-07 | Le commentaire périmé « fourmi » est supprimé | revue |
| ACC-08 | En 2e année : 2C pointe vers `simplexe/?methode=geometrique`, 2Mr vers `simplexe/?methode=algebrique`, aucun lien vers le simplexe en 2Ms | [auto-py] |
