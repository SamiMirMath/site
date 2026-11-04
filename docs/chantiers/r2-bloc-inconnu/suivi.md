# Chantier « R2 : bloc inconnu visible » — suivi

Demande du 04.11.2026 (recommandation R2 de la revue de structure, `docs/chantiers/revue-structure/rapport.md`, non suivi). Branche `r2-bloc-inconnu`
depuis `main` à jour (`ca6c243`, égal à `origin/main`). Une partie, un commit. Le détail est dans [journal.md](journal.md).

## État

| Partie | Contenu | État |
|---|---|---|
| 1 | `commun/rendu.js` : bloc de type inconnu remplacé par l'encadré commun « attention » (SOC-22), aussi dans un sous-calcul et dans la carte finale ; style de texte inconnu rendu comme « etape » ; test de page ; spécification | **faite**, suite complète verte (1 296 Python, 123 pages) |

## Décisions

1. **Encadré** : le bloc `encadre` existant, genre « attention » (`.enc.enc-attention`, `commun/style.css`), titre « Affichage incomplet », texte
   « Une partie du corrigé n'a pas pu s'afficher. Rechargez la page (le navigateur garde peut-être une ancienne version du site). » (vouvoiement, R12).
   Aucun CSS nouveau : ni couleur, ni largeur en px.
2. Le `console.error` du type inconnu est gardé (détail technique, SOC 7).
3. **Style de texte inconnu** : trouvé par le test, l'ancien code levait une exception (`STYLE_TEXTE[…] is not a function`) et toute la carte était
   perdue. Il est rendu comme une étape ordinaire (le contenu est juste, seul le style manque), avec un `console.error`.

## Écarts

- `docs/methode-chantiers.md`, cité par la demande, n'existe pas dans le dépôt (constat de la revue, D17 c) : j'ai suivi CLAUDE.md.
- Fusion : la demande la conditionne à la présence du « Correctif Exp-log » dans `origin/main`. Seul `9716912` (« Fusion de correctif-explog-3c »,
  02.11.2026) y figure ; le correctif en cours sur le Mac n'est pas poussé. Branche poussée, **non fusionnée**.

## Questions ouvertes

Aucune.

## Reprise après compactage

Branche `r2-bloc-inconnu`. Fichiers : `commun/rendu.js` (`rendreBloc`, constante exportée `BLOC_INCONNU`), `tests/pages/test_comportement.py`
(`test_soc22_bloc_inconnu_visible`), `docs/specifications/socle-commun.md` (règle 7 et ligne SOC-22), ce dossier. Le test échoue sans le correctif
(vérifié). La branche locale `bloc-inconnu` (première version, message rouge) est remplacée par celle-ci.
