# Chantier « S'entraîner » (onglet de l'outil Équations du 2e degré) : décisions

**Statut : validé par l'enseignant le 06.11.2026 (soir).** Font foi, dans cet ordre : `CLAUDE.md` > ce fichier >
`docs/chantiers/equations-2e-degre/quiz.md` (spécification complète, commit a602f49) > `docs/chantiers/equations-2e-degre/decisions.md`
(§§ 1 à 13) > `suivi.md` de ce chantier. Ce fichier ne recopie pas la spécification : il la complète (§ 2), la découpe (§ 3) et dit ce
qui sera relu (§ 4).

Dossier du chantier : `docs/chantiers/entrainement-2e-degre/` (ce fichier, `suivi.md`, `journal.md`).

---

## 1. Principes

1. **Source unique (QZ-02).** Le quiz n'écrit aucune réponse à la main : questions, boutons, classement et explications viennent du
   moteur (`moteur/second_degre.py`), calculés sur la même résolution que « Résoudre » (`resoudre_equation`).
2. **Rien de faux à l'écran (QZ-10).** Une équation n'est proposée que si `resoudre_equation` rend `resolu`, et si chaque bouton
   refusé a une explication (sinon elle est écartée du tirage). Chaque nombre cité dans une explication est relu sur le polynôme.
3. **Invariants de toute la session.**
   - Les sorties des **autres outils** sont identiques à l'octet après chaque partie (`dump_sorties.py`).
   - Les sorties de **« Résoudre »** (outil `equations-2e-degre`) ne changent **qu'en E1** (étape FORMULE à part), et chaque
     changement est listé, avant / après, pour l'enseignant. À partir d'E2, elles sont identiques à celles d'E1 ; seules les sorties
     du quiz s'ajoutent.
4. **Python pur** dans le moteur, sans SymPy ; vouvoiement (R12) ; notation suisse et ≈ par `nombres` (R13, E14).
5. **Principe 6** : le quiz fait choisir des méthodes, jamais un concept ; les explications citent les nombres de l'équation.

---

## 2. Compléments à la spécification (décisions du 06.11.2026, soir)

**S1. Phrases de QZ-07 corrigées** (elles remplacent celles de quiz.md) :
- Mauvaise des trois Id. rem. : la phrase ne donne pas la réponse. « Le terme du milieu, −4x, est négatif. » ; « Il n'y a pas de
  terme en x. » ; « Le terme du milieu, 6x, est positif. » (sans nommer l'identité).
- Terme des bouts qui n'est pas un carré (F8) : « 2 n'est pas un carré parfait : ce n'est pas une identité remarquable. »
  (« 2x² n'est pas un carré » est faux au sens strict : 2x² = (√2·x)²).
- ME sans facteur commun (F4) : « x², 6x et 4 n'ont pas de facteur commun (autre que 1). »
- Tâtonnement avec a = 1, sans méthode d'avant (F10, F13) : « Le trinôme est unitaire (a = 1) : on commence par le S-P. »
  (vrai aussi quand le S-P échoue, F10).

**S2. Les deux cas qui n'avaient pas de modèle :**
- « Formule (Δ) » devant un produit déjà factorisé (phase `produit_nul`, hors du cas E9) : **acceptée** (elle aboutit : forme
  développée, puis la formule), remarque « Cela marche, mais le produit est déjà factorisé : le produit nul est plus rapide. ».
- S-P avec a = 1 et des coefficients non entiers : **refusé**, « Le S-P demande des coefficients entiers : il faut la formule. »
  (sauf si la règle d nomme d'abord une méthode d'avant).

**S3. Remarque des choix acceptés (QZ-05), forme générale** : « Cela marche, mais <la méthode attendue> vient avant dans l'ordre du
cours. », la méthode étant écrite en mots (« la mise en évidence », « l'identité remarquable », « le S-P », « le tâtonnement »,
« le produit nul »). Les remarques particulières de quiz.md (F15, « Développer » devant un produit nul) et de S2 priment.

**S4. Temps.**
- `quiz_json` : moins de 0,3 s en Python natif par partie, le classement des boutons compris (il résout réellement les formes
  obtenues) ; mesuré et noté dans `journal.md` après chaque partie.
- Tests « 200 graines par famille » (§ 5 de quiz.md) : dans la suite complète si l'ensemble reste sous 10 s par tranche ; sinon, une
  partie dans la suite (par exemple 20 graines par famille) et les 200 graines dans un test marqué, lancé en fin de session et noté.
  La suite complète ne doit pas s'allonger de plus d'une minute.

**S5. Page.** Les onglets réutilisent `monterOnglets` (`commun/composants.js`) ; « Résoudre » garde exactement son comportement
(références de pages inchangées après E1, hors cartes changées par E1). Les cartes du quiz sont celles de `second_degre.cartes`
(R1). Rien n'est enregistré (QZ-08 : pas de `localStorage`).

**S6. Aucune question pendant la nuit** : à chaque doute, l'option qui affiche le moins ou ne touche à rien d'existant, notée sous
« Questions pour l'enseignant », et on continue.

---

## 3. Découpage

Branche `entrainement-2e-degre` depuis `main` à jour. Un sous-agent general-purpose (Opus) par partie, l'un après l'autre ; une partie
par commit ; suite complète verte avant chaque commit ; contrôle du chef : `verifier`, puis `rapide --depuis HEAD~1`, puis une ligne
dans `journal.md`. Chaque partie dépend de la précédente.

| Partie | Contenu | Tests | Sorties |
|---|---|---|---|
| E0 | Prérequis (`resoudre_equation`, `cartes`, `s_applique`, `appliquer`, `monterOnglets`, quiz.md à jour) ; fiches `suivi.md` et `journal.md` (plan approuvé en tête) ; référence des tests ; dump de départ. Si un prérequis manque ou si la suite est rouge : arrêt. | — | aucune |
| E1 | **Étape FORMULE à part** (quiz.md § 4, points b et c ; D3, E6, E7, E9, § 13.5 de decisions.md) : l'étape de l'échec se termine sur « Aucun couple ne convient. » (ou la ligne des diviseurs, ou « … trop de couples à tester. ») ; l'étape `FORMULE` commence par « On utilise la formule. », après la ligne du produit nul dans les cas E9. Exemples de decisions.md (§ 7, § 10, E9) mis à jour au nouveau texte. | Instantanés de l'outil régénérés ; **liste avant / après de chaque sortie changée** dans `suivi.md` ; invariant de concaténation ; autres outils : dump identique | « Résoudre » change (listé) |
| E2 | **Classement des boutons** (point f) : fonction qui rend, pour une étape et sa phase, `attendue` (ce que le chemin écrit ensuite, tentative en échec comprise), `acceptees` (le moteur résout réellement la forme obtenue ; formes structurées comprises) et `refusees`. Remarques QZ-05 et S3. | Chaque bouton dans exactement un ensemble ; chaque acceptée aboutit, aucune refusée n'aboutit ; attendue = chemin ; corpus et liste fixe | aucune |
| E3 | **Explications** : `explication_refus` (règle d, QZ-07, S1, S2) ; questions (« Et pour x² − 1 ? », « Aucun couple ne convient. Et maintenant ? »…) ; valeurs de Δ proposées (erreurs typiques distinctes) et phase `delta_nombre`. | Une explication par branche ; jamais None sur les familles ; quand une ME ou une Id. rem. vient avant, le texte la nomme ; R12, vocabulaire | aucune |
| E4 | **`quiz_json(exo)`** et les équations : familles F1 à F17 (générateurs à graine, propriété et chemin vérifiés, retirage borné), liste fixe (41), QZ-10, QZ-13 (`exo` = `<famille>-<graine>`) ; manifeste (nouvelle fonction). | Oracle sur les familles (S4) ; instantanés de `quiz_json` (liste fixe et une graine par famille) ; invariant : concaténation des lignes du quiz = chaîne de « Résoudre » ; temps (S4) | seules s'ajoutent les sorties du quiz |
| E5 | **Page** : onglets « Résoudre » / « S'entraîner » (`?onglet=entrainement`), déroulé QZ-03 à QZ-09, boutons en grille (QZ-11), explication en `aria-live`, deux essais (QZ-06), bilan et compteur (QZ-08), « Nouvelle équation », « Voir dans Résoudre », `?exo=`, `no-print`, clavier. | Pages : parcours 2.9 a, tentative en échec (2.12 b), échec sur un facteur (Javet 2.17 c), deux erreurs, « juste, pas dans l'ordre », compteur, « Voir dans Résoudre », `?onglet=…&exo=…`, clavier ; `test_largeurs` de 320 à 1100 px à chaque phase (`CONNUS` vide) ; captures à 390 px | seules s'ajoutent les sorties du quiz |
| E6 | Après la relecture de l'enseignant (pas de nuit) : corrections. | — | — |

---

## 4. À relire par l'enseignant après la nuit

- **E1** : la liste avant / après des sorties de « Résoudre » changées (deux phrases au lieu d'une ; place de « On utilise la
  formule. » dans les cas E9).
- **E3** : un tableau des explications produites, une par branche de la règle d, sur des équations des familles.
- **E5** : captures à 390 px (clair et sombre) d'une partie complète sur 2.9 a, d'une tentative en échec (2.12 b), d'un échec sur
  un facteur (Javet 2.17 c), d'une erreur avec son explication et du bilan.
- Les questions notées pendant la nuit (S6).
