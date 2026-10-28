# Accueil et registre des outils

## Fonctionnel

- Présentation (titre, phrase d'accueil, ruban de Möbius décoratif).
- Choix de la filière (C, Ms, Mr ou « tous ») mémorisé dans le navigateur ; « changer » pour revenir
  au choix. Une année sans outil pour la filière choisie est masquée.
- Pour chaque année (I, II, III) et chaque filière : liste des outils (titre + description + lien).
- **Sans JavaScript** : tous les outils de toutes les filières sont visibles et les liens
  fonctionnent (le choix de filière est une amélioration apportée par le JS). Mécanisme (T22) : le CSS de base montre tout (trois colonnes par
  année) et cache la porte ; un petit script dans `<head>` pose `data-js` sur `<html>` puis `data-track` (filière enregistrée) avant le premier
  affichage ; les règles qui cachent le contenu ou filtrent par filière sont toutes sous `html[data-js]`. Le canvas du ruban est caché sans JS.
- Pied de page « © 2026 Sami Mir · samimir.ch ».

## Registre `commun/registre.json`

Source unique de la liste des outils, lue par les tests (l'accueil reste du HTML écrit à la main). Fait en T22 : 6 outils, 13 cartes
(année I : 3, année II : 2, année III : 8). `parametres` (requête ajoutée au lien) et `descriptions` (texte propre à une filière) sont facultatifs, par filière : T35 les utilise pour
Exponentielles et logarithmes en 2Ms et 2Mr (`?filiere=M`, description « Équations exponentielles et logarithmiques avec ensemble de définition, étape par étape. ») ; le simplexe les aura avec T27.
Avec T35 : 7 outils, 16 cartes (année I : 3, année II : 4, année III : 9). Les tests lisent `parametres` et `descriptions` (ACC-01).

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
| ACC-03 | Sans JavaScript, tous les liens d'outils sont visibles (aucune règle CSS ne masque `#content` hors de `html[data-js]`) ; les 16 cartes du registre | [auto-py] (analyse CSS) + [auto-page] JS désactivé |
| ACC-04 | Avec JS, choisir « Ms » masque les années sans outil Ms et affiche le choix courant | [auto-page] |
| ACC-05 | Le texte doré (`--gold`) a un contraste ≥ 4,5:1 sur `--paper` et `--paper-raised` (ex. `#84672c` : 4,9:1) ; le mode sombre reste ≥ 4,5:1 | [auto-py] |
| ACC-06 | L'animation ne consomme aucune image (`requestAnimationFrame`) quand le canvas est hors écran | [auto-page] |
| ACC-07 | Le commentaire périmé « fourmi » est supprimé | revue |
| ACC-08 | En 2e année : 2C pointe vers `simplexe/?methode=geometrique`, 2Mr vers `simplexe/?methode=algebrique`, aucun lien vers le simplexe en 2Ms | [auto-py] (T27 : la page du simplexe doit d'abord comprendre le paramètre ; jusque-là 2C et 2Mr gardent `simplexe/`) |
