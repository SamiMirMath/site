# Chantier « R2 : bloc inconnu visible » — journal

## 04.11.2026 — partie 1

**Départ.** `git pull` sur `main` : déjà à jour. Dernier commit d'`origin/main` : `ca6c243` « Équations du 2e degré : audit (étape 0) »
(04.11.2026, 16:09). Le seul correctif Exp-log présent est `9716912` « Fusion de correctif-explog-3c dans main » (02.11.2026) ; le correctif
en cours sur le Mac n'y est pas, et aucune autre branche n'est poussée (`git ls-remote --heads origin` : `main` seulement).

**Origine.** Revue de structure, R2 : `commun/rendu.js` (`rendreCarte`, l. 155-158 avant le correctif) sautait un bloc de type inconnu avec un seul
`console.error`. Avec la fenêtre de cache de GitHub Pages (environ 10 minutes pour les JS et CSS, sans `?v=`), un ancien `rendu.js` peut recevoir la
sortie d'un moteur plus récent : un bloc nouveau (le tableau Somme-Produit du 2e degré, par exemple) disparaîtrait sans que l'élève le sache.

**Correctif.**
- `rendreBloc(b, c)` : un seul point de rendu d'un bloc, utilisé par `rendreCarte` et par `sous_calcul` (qui sautait aussi les blocs inconnus, avec `""`).
  Type inconnu : `console.error` (gardé) et, à la place du bloc, le bloc commun `encadre` genre « attention » (`.enc.enc-attention`), titre
  « Affichage incomplet », texte `BLOC_INCONNU` (exporté). Aucun CSS ajouté.
- `STYLE_TEXTE` : un style inconnu levait `TypeError: STYLE_TEXTE[(b.style || "etape")] is not a function` et toute la carte était perdue ;
  il est rendu comme « etape », avec un `console.error`.

**Test.** `tests/pages/test_comportement.py::test_soc22_bloc_inconnu_visible` : les cartes sont ajoutées à `#cartes` (section `#resultat` affichée,
comme après un calcul) ; carte ordinaire (texte avant, bloc inconnu, texte après : l'encadré est entre les deux), carte finale, sous-calcul : un encadré
chacune, titre et texte attendus, **visible** (taille non nulle, ni `display: none` ni `visibility: hidden`) ; style inconnu rendu ; aucun « undefined »
ni « [object » ; aucune exception JS (`page.evaluer` en lèverait une).
Sans le correctif (`git stash` de `rendu.js`), le test échoue : `ErreurPage: TypeError: STYLE_TEXTE[(b.style || "etape")] is not a function`.
Premier essai du test : encadré mesuré invisible, parce que `#resultat` est `hidden` tant qu'aucun calcul n'a eu lieu (corrigé dans le test).

**Suite complète** (`python3 tests/lancer.py complet`, PC, 21:52:23 → 22:04:19), code de retour **0** :

| Suite | Résultat | Durée |
|---|---|---|
| Python | 1 296 réussis, 1 xfail (attendu), 101 738 sous-tests | 164,8 s |
| Pages (corpus complet, `-n 2`) | 123 réussis (122 + le nouveau), 2 386 sous-tests | 547,9 s |

Références de pages et instantanés inchangés (`git status` : seuls les fichiers du chantier).

**Fusion.** Conditionnée par la demande à la présence du correctif Exp-log du Mac dans `origin/main` : absent, donc branche poussée seule, non fusionnée.
