# Socle commun des pages outils

S'applique à toutes les pages outils, sauf mention contraire pour le simplexe
(voir [simplexe.md](simplexe.md)).

## Fonctionnel

1. **En-tête** : lien « ← samimir.ch » vers l'accueil, titre de l'outil, une phrase d'accroche.
2. **Exercice au hasard** : bouton « Nouvel exercice » ; l'énoncé s'affiche (aperçu KaTeX) sans
   le corrigé ; bouton « Afficher le corrigé ». Pas d'étiquette de difficulté visible. L'énoncé
   tiré a une URL partageable `?exo=<niveau>-<graine>`.
3. **Saisie** : champ texte + clavier virtuel propre à l'outil ; aperçu en direct ; exemples
   cliquables ; touche Entrée = calculer ; `?f=<expression>` pré-remplit et calcule.
4. **Corrigé par étapes** : cartes affichées une à une (« Étape k / n », « Étape suivante »,
   « Tout afficher ») ; la dernière carte donne le résultat encadré.
5. **Impression / PDF** : bouton « Télécharger le corrigé (PDF) » ; toutes les cartes imprimées,
   sans boutons ni clavier ; titre de fichier explicite.
6. **Chargement** : état lisible (« Chargement du moteur de calcul… », « Prêt ») ; le bouton de
   calcul reste désactivé jusqu'à ce que le moteur soit prêt.
7. **Erreurs** : message en français, jamais de trace Python ; calcul de plus de 30 s interrompu
   avec un message et relance du moteur. Erreur de connexion : « Vérifiez votre connexion
   internet, puis rechargez la page ». Le détail technique n'est écrit que dans la console
   (`console.error`), jamais dans la page.
7b. **Aperçu de la saisie** (décidé le 14.10.2026) : aucun message d'erreur rouge pendant la frappe ;
   une erreur n'apparaît qu'après une pause d'environ 0,5 s, et disparaît dès que la saisie
   redevient valide ; une réponse tardive ou perdue ne laisse jamais un ancien message.
7c. **Vocabulaire** (décidé le 14.10.2026) : aucun texte visible ne cite une méthode interne
   (« calcul formel », SymPy, dichotomie…) ; le mot « transcendante » est interdit partout. Si une
   équation ne se résout pas avec les méthodes du cours : « solution obtenue numériquement : x ≈ … ».
   **Facteurs de signe évident** (décidé le 15.10.2026) : dans tout tableau de signes (ED, Dérivée,
   Étude complète, Limites), un facteur dont le signe est évident n'a PAS de ligne ; il est justifié en une phrase
   (« √(4x²+1) > 0 » ; « (x+2)² > 0 pour x ≠ −2 » ; « e^u > 0 » ; constante : son signe), puis « donc f'(x) est du
   signe de … ». Le tableau ne contient que les facteurs qui changent de signe ; la valeur interdite ou le zéro d'un
   facteur retiré garde sa colonne (double barre pour une valeur interdite). Si tous les facteurs sont évidents :
   pas de tableau, une phrase. Sont évidents : exponentielle, constante, puissance paire, racine d'une expression
   strictement positive, polynôme sans zéro réel et positif ; ne le sont pas : une racine dont l'argument s'annule
   (√(x−2), √(x²)), une racine impaire.
   **Les équivalents sont interdits partout** (décidé le 15.10.2026) : ni le symbole ∼ (`\sim`), ni le mot
   « équivalent », ni « se comporte comme », dans toutes les sorties de tous les outils. On met en évidence,
   avec des égalités exactes (√(4x²+1) = √(x²(4 + 1/x²)) = |x|·√(4 + 1/x²)).
8. **Pied de page** : « © 2026 Sami Mir · samimir.ch », identique à l'accueil.

## Notation suisse

- Virgule décimale partout (`2{,}5` en TeX, « 2,5 » en texte).
- Séparateur de milliers : apostrophe typographique ’ (U+2019) **dès 4 chiffres** (1’000) ;
  en TeX `\text{’}` (tranché le 14.10.2026, Q5).
- Saisie : « 2,5 » et « 2.5 » acceptés ; « 1'000 », « 1’000 » acceptés (apostrophe suivie
  d'exactement 3 chiffres) ; « 1 000 » (espace entre chiffres) refusé avec un message clair
  plutôt que lu 1·000.
- Valeurs approchées toujours précédées de ≈.

## Visuel et mobile

- Variables CSS partagées (`commun/style.css`), identité de l'accueil (serif, papier, bordeaux),
  modes clair, sombre et impression.
- Aucun défilement horizontal de la page à 360 px de large ; les tableaux et formules longues
  défilent dans leur propre conteneur.
- Cibles tactiles ≥ 44 × 44 px pour les boutons du clavier et de navigation.
- Champ de saisie ≥ 16 px (pas de zoom automatique sur iOS).
- Un glissement vertical à un doigt sur un graphique fait défiler la page.

## Accessibilité

- `lang="fr"`, titres hiérarchisés, un seul `<h1>`.
- Boutons à symbole (⌫, C, −, +, ÷) avec `aria-label` en toutes lettres.
- Zones `#etat` et `#apercu` en `aria-live="polite"`.
- Tableaux de signes et de variations avec cellules d'en-tête (`<th scope>`).
- Contraste texte ≥ 4,5:1 (≥ 3:1 pour les grands textes) dans les modes clair et sombre.
- Animations désactivées si `prefers-reduced-motion: reduce`.

## Critères d'acceptation

| Id | Critère | Vérif. |
|---|---|---|
| SOC-01 | Chaque page outil contient le lien d'en-tête vers `/` et le pied de page commun, identiques à un modèle | [auto-py] |
| SOC-02 | Chaque page outil charge `commun/style.css` et ne redéfinit aucune variable de couleur du socle | [auto-py] |
| SOC-03 | Pour chaque couple texte/fond déclaré dans `commun/style.css` (clair et sombre), contraste ≥ 4,5:1 | [auto-py] |
| SOC-04 | `?f=<exemple>` affiche le corrigé sans autre action | [auto-page] |
| SOC-05 | `?exo=<niveau>-<graine>` affiche toujours le même énoncé | [auto-py] (moteur) + [auto-page] |
| SOC-06 | Une saisie invalide affiche un message en français ; aucune réponse de moteur ne contient « Traceback » | [auto-py] (balayage d'entrées invalides) |
| SOC-07 | « Étape suivante » révèle exactement une carte ; « Tout afficher » les révèle toutes ; le compteur est juste | [auto-page] |
| SOC-08 | En impression, toutes les cartes sont visibles et aucun bouton n'apparaît | [manuel] |
| SOC-09 | À 360 px de large, `document.documentElement.scrollWidth` ≤ largeur de la fenêtre après un calcul | [auto-page] |
| SOC-10 | Les boutons à symbole ont un `aria-label` ; `#etat` et `#apercu` ont `aria-live` | [auto-py] (analyse HTML) |
| SOC-11 | « 1'000 » et « 1’000 » sont lus 1000 ; « 1 000 » est refusé avec un message | [auto-py] |
| SOC-12 | Aucune valeur décimale affichée avec un point (moteurs et graduations) | [auto-py] (balayage des sorties) + [manuel] |
| SOC-13 | Après 30 s de calcul, message « trop long » et moteur relancé ; un nouveau calcul fonctionne ensuite | [auto-page] |
| SOC-15 | Aucune sortie de moteur ni aucune page ne contient « calcul formel », SymPy, « dichotomie », « transcend… », « exacte simple », « Erreur du moteur », ni équivalent (« ∼ », « équivalent », « se comporte comme ») ; le détail technique est dans des champs `detail` / `*_detail` à part | [auto-py] (`test_vocabulaire.py`) |
| SOC-16 | En tapant `ln(x)/x` (clavier ou bouton ln), aucun message rouge n'apparaît pendant la frappe ni à la fin ; une saisie incomplète (`ln(`) n'affiche son erreur qu'après ≈ 0,5 s | [auto-page] (Chrome, CI, T15) |
| SOC-14 | Chargement sur un vrai téléphone : délai jusqu'à « Prêt » relevé et noté dans `docs/` | [manuel] (enseignant) |
