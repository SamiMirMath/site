# Questions à valider

Tant qu'une question est ouverte, **le comportement actuel est conservé** et les tâches qui en
dépendent sont bloquées (voir [taches.md](taches.md)).

**État au 14.10.2026 : Q1 à Q7 et Q9 sont tranchées.** Seule Q8 (apparue en reportant Q4) reste ouverte ;
elle ne bloque aucune tâche, seulement un gabarit de factorisation. **Q10 à Q12 (outil Exponentielles et logarithmes)
sont tranchées le 26.10.2026.**

## ~~Q1 — « Croissance comparée » dans l'outil Limites~~ (tranchée le 14.10.2026)

**Rappel.** Les croissances comparées sont les limites de référence qui lèvent les formes
indéterminées entre puissances, exponentielle et logarithme.

**Décision.** Proposition acceptée, logarithme compris, avec les ajouts de l'enseignant :

- La croissance comparée n'est citée que face à une **forme indéterminée** entre une puissance
  de x et une exponentielle ou un logarithme : ∞/∞, 0·∞, et aussi **∞ − ∞ levée par
  factorisation** (e^x − x² = e^x(1 − x²/e^x) ; x − ln x = x(1 − ln(x)/x)).
- Lieux : en ±∞, et en 0⁺ pour le logarithme.
- Puissances x^n avec **n > 0 réel** (pas seulement entier) ; exponentielles **e^(ax) avec a > 0**
  (et e^(−ax) = 1/e^(ax)).
- Limites de référence couvertes (n > 0, a > 0) :
  - en +∞ : e^(ax)/x^n → +∞ ; x^n·e^(−ax) → 0 ; ln(x)/x^n → 0 ; x^n/ln(x) → +∞ ;
  - en −∞ : x^n·e^(ax) → 0 (x^n défini pour x < 0, n entier) ;
  - en 0⁺ : x^n·ln(x) → 0.
- La phrase **nomme toujours la limite de référence utilisée**, par exemple
  « x²·e^(−x) → 0 en +∞ par croissance comparée (lim x^n e^(−x) = 0) ».
- Hors de ces cas (x·e^x en +∞, e^x/x en 0…), aucune mention de croissance comparée.

Voir [specifications/limites-asymptotes.md](specifications/limites-asymptotes.md) ; débloque **T09**.

## ~~Q2 — Simplexe~~ (tranchée le 13.10.2026)

- **2C : méthode graphique ; 2Mr (OS) : méthode algébrique ; 2Ms : pas d'outil de programmation linéaire.**
- `?methode=` présélectionne la méthode de la filière ; l'autre reste accessible.
- **Exercices au hasard : oui** (gabarits : Q4).

Voir [specifications/simplexe.md](specifications/simplexe.md).

## ~~Q3 — Tableau quand f est définie mais pas f'~~ (tranchée le 14.10.2026)

**Décision.**
- Ligne f'(x) : **double barre** (f' non définie).
- Ligne f(x) : **la valeur f(a), sans barre**.
- Extremum local annoncé :
  - **(i)** en un point **intérieur** de l'ED où f' change de signe, même si f' n'y est pas
    définie (√(x²) en 0, x^(2/3) en 0) ;
  - **(ii)** en toute **borne fermée** de l'ED (±2 pour √(x²−4), 0 pour √x) : extremum local
    dont la nature est donnée par le sens de variation sur l'intervalle adjacent (f décroissante
    à gauche de la borne droite ou croissante à droite de la borne gauche ⇒ minimum ; sinon maximum).

Voir [specifications/derivee-variations.md](specifications/derivee-variations.md) (DV-04, DV-09,
DV-10) ; débloque entièrement **T06**.

## ~~Q4 — Gabarits et niveaux des exercices au hasard~~ (tranchée le 14.10.2026)

**Décision.** Gabarits ci-dessous acceptés, pondérations conservées (35 % / 35 % / 20 % / 10 %),
avec les règles suivantes :

- **Paramètres** (a, b, c, k, s, p) entiers petits ; **racines distinctes, toutes exactes**.
- **Simplexe algébrique, minimisation** : f a au moins un coefficient négatif (sinon l'optimum
  est trivialement à l'origine).
- **Simplexe, niveaux facile et moyen** : aucune égalité dans le test du rapport (pas de
  dégénérescence).
- **Simplexe graphique, très difficile** : deux gabarits séparés, « région non bornée, optimum
  fini » et « problème non borné ».

| Outil | facile | moyen | difficile | très difficile |
|---|---|---|---|---|
| Ensemble de définition | ln(ax+b) ; ln(x²−k²) ; 1/(e^x−k) ; ln(x−a)+ln(x−b) | 1/ln(x+a) ; ln(x)/(ln(x)+k) ; ln((x−a)/(x−b)) ; √(trinôme à racines entières) ; e^(1/trinôme) | k·ln(x)/((ln x)²−1) ; ln(trinôme)/(x−c) ; 1/(e^(2x)−s·e^x+p) | √(x·ln(x+a)+x) ; 1/(ln(x−a)+ln(x−b)) |
| Dérivée | trinôme ; x³−3k²x ; e^(ax) | x⁴−2k²x² ; x·ln(x) ; ln(x)/x ; √(trinôme à Δ<0) | (x²−a²)/(x−c) ; x/(x²+k) ; ln(x²−k²) | x²·e^(−x) |
| Limites | 1/(x−a) ; e^(ax) ; ln(x) | (x²−a²)/(x−c) ; ln(x−a) ; 1/x² | x²/(x−a) ; √(trinôme) ; x²·e^(−x) | ln(x²−ax)/(x−c) |
| Étude complète | comme Dérivée, facile | x⁴−2k²x² ; x·ln(x) ; ln(x)/x | (x²−a²)/(x−c) ; x/(x²+k) | x²·e^(−x) |
| Factorisation | voir [specifications/factorisation.md](specifications/factorisation.md) | | | |
| Simplexe — graphique (2C) | 2 contraintes ≤, maximiser, sommets entiers | 3 contraintes dont une ≥, sommets entiers ou demi-entiers | minimiser avec contraintes ≥ ; coefficient de y négatif dans f | (a) région non bornée, optimum fini ; (b) problème non borné ; (c) infinité de solutions (côté parallèle aux droites f = c) |
| Simplexe — algébrique (2Mr/OS) | 2 variables, 2 contraintes ≤ (b ≥ 0), 1 à 2 pivots | 2 variables, 3 contraintes, 2 pivots | 3 variables, 3 contraintes ≤ | 3 variables, 4 contraintes, 3 pivots ou plus ; minimisation (f avec un coefficient négatif) |

Débloque **T13** et **T28**.

## ~~Q5 — Séparateur de milliers~~ (tranchée le 14.10.2026)

**Décision.** Apostrophe typographique ’ **dès 4 chiffres** (1’000) ; à la saisie, ' et ’ sont
acceptés. Voir [specifications/socle-commun.md](specifications/socle-commun.md) ; débloque
entièrement **T23**.

## ~~Q6 — x⁰~~ (tranchée le 14.10.2026)

**Décision.** u⁰ = 1 sur ℝ (0⁰ compris), **mais l'ED de la base reste exigé** :
(ln x)⁰ n'est défini que pour x > 0, (1/x)⁰ pour x ≠ 0.
Le comportement actuel est déjà conforme (vérifié le 14.10.2026) ; critère ED-08 ajouté.

## ~~Q7 — Vocabulaire quand la limite en une valeur interdite est finie~~ (tranchée le 14.10.2026)

**Décision.** Ne plus écrire « point de discontinuité » quand a ∉ ED.
- Limites latérales finies et égales à ℓ : « f n'est pas définie en a, mais sa limite y est
  finie (= ℓ) : pas d'asymptote verticale, trou dans le graphique en (a ; ℓ) ».
- Limites latérales finies et différentes : « limites à gauche et à droite différentes : f n'a
  pas de limite en a ; pas d'asymptote verticale ». Cette formulation **remplace le genre
  « saut »** introduit par `70e6b1e`.

Voir [specifications/limites-asymptotes.md](specifications/limites-asymptotes.md) ; nouvelle
tâche **T08b**.

## ~~Q9 — Rédaction détaillée des limites et des asymptotes~~ (tranchée le 14.10.2026)

**Décision.** Chaque limite est rédigée avec la méthode du cours, la première qui s'applique :
(0) opérations et composition de limites, s'il n'y a pas de forme indéterminée ; (1) mise en
évidence ; (2) expression conjuguée ; (3) limites de référence et croissance comparée (Q1
seulement) ; (4) Bernoulli-L'Hôpital en dernier recours.
- **Pas d'équivalent** (précisé le 15.10.2026) : ni le symbole ∼, ni le mot « équivalent », ni « se
  comporte comme », dans toutes les sorties de tous les outils. La méthode « termes dominants »
  est supprimée : tout passe par la **mise en évidence**, écrite en égalités exactes. Racine de polynôme :
  √(4x²+1) = √(x²(4 + 1/x²)) = |x|·√(4 + 1/x²), puis |x| = x (x > 0) ou −x (x < 0) et simplification
  (en −∞ : f(x) = −x·√(4 + 1/x²)/(x(1 + 2/x)) = −√(4 + 1/x²)/(1 + 2/x) → −2). Après une conjuguée :
  x/(√(x²+x) + x) = 1/(√(1 + 1/x) + 1) → 1/2. ln d'un polynôme : ln(x²+1) = ln(x²(1 + 1/x²)) =
  2 ln|x| + ln(1 + 1/x²), puis croissance comparée (ln x / x^n → 0) **avant** Bernoulli-L'Hôpital.
- **√(x²) = |x|** (et √(u²) = |u|) est reconnu : x/√(x²) en 0 donne x/|x|, −1 à gauche et 1 à droite.
- **Expression conjuguée** : ajoutée (∞ − ∞ et 0/0 avec une racine), juste après la mise en évidence.
- **Limites de référence** : celles de Q1 seulement. (e^x − 1)/x en 0 ou ln(x)/(x − 1) en 1 passent
  par Bernoulli-L'Hôpital.
- **Bernoulli-L'Hôpital** : forme 0/0 ou ∞/∞ (0·∞ et ∞ − ∞ d'abord mis en quotient), f et g
  dérivables au voisinage de a (sauf peut-être en a), g' ≠ 0 au voisinage de a (sauf peut-être en a),
  lim f'/g' existe ; les quatre hypothèses sont écrites ; au plus deux applications de suite ; si une
  hypothèse n'est pas vérifiée ou si lim f'/g' n'existe pas, la règle n'est pas appliquée et ne conclut rien.
- **Racines en −∞** : écrire « x < 0 donc √(x²) = |x| = −x » chaque fois que x² sort d'une racine.
- **Asymptote oblique** : division euclidienne pour une fraction rationnelle ; sinon
  a = lim f(x)/x puis b = lim (f(x) − ax), chaque limite rédigée ; position relative au voisinage de ±∞
  seulement, quand le signe de f(x) − (ax + b) se lit directement.
- **Garde-fou** : la valeur de chaque limite reste celle du calcul actuel. Si la rédaction n'aboutit pas
  ou donne une autre valeur, toutes ses étapes sont abandonnées et la page écrit « Le calcul détaillé de
  cette limite n'est pas rédigé ici ; résultat : lim f(x) = … » (jamais une étape fausse).

Voir [specifications/limites-asymptotes.md](specifications/limites-asymptotes.md) ; tâche **T29**
(T09 y est incluse).

## Q8 — Racine double dans les gabarits de factorisation (ouverte)

La règle de Q4 « racines distinctes » s'applique-t-elle aussi au gabarit factorisation
« difficile : carré parfait (px + q)² », dont la racine double est le but même de l'exercice
(identité remarquable) ? Proposition : la règle vise les coïncidences accidentelles entre
paramètres ; un gabarit conçu pour une racine double (carré parfait, cube d'un binôme) la garde.
D'ici la décision, le gabarit est conservé tel quel.

## ~~Q10 — Exercices au hasard de « Exponentielles et logarithmes » : gabarits et pondérations~~ (tranchée le 26.10.2026)

**Décision.** Le niveau « difficile » est validé : tous les types (bases différentes, a^(x²)·b^x = c, log_x(n) = k, log(log(x)) = c) sont dans le chapitre 3C.
Pondérations **30 % / 30 % / 30 % / 10 %** (facile / moyen / logarithme / difficile) au lieu de 35 / 35 / 20 / 10. Contraintes du générateur :
- x² en exposant : trinôme à racines entières ou rationnelles simples, **jamais de discriminant non carré** ;
- environ **1 exercice sur 10 du niveau « logarithme »** a un second membre ≤ 0 (S = ∅, par exemple 5^(8x) = −25).
Voir [specifications/exponentielles-logarithmes.md](specifications/exponentielles-logarithmes.md) ; pool C seulement, le pool M viendra avec les 2M.

## ~~Q11 — Forme du résultat exact~~ (tranchée le 26.10.2026)

**Décision.** log(10^k) = k et ln(e^k) = k sont évalués ; log a − log b est regroupé en log(a/b) seulement dans les équations de bases différentes (E3), comme
le corrigé (2.24). Ailleurs la valeur exacte reste **celle que donne la chaîne** : `ln(25/37)/(−0,02)` n'est **pas** simplifié en `−50 · ln(25/37)`.

## ~~Q12 — Séparateur des milliers dans les résultats~~ (tranchée le 26.10.2026)

**Décision.** La règle Q5 est appliquée dès maintenant dans cet outil : apostrophe typographique ’ **dès 4 chiffres, sur la partie entière seulement**
(−99’999’995, 1’234,567, 0,0001), jamais de séparateur dans les décimales ; saisie de ' et ’ lue 1000 ; « 1 000 » refusé avec un message. Fait en `657806d` ;
les fonctions de formatage sont dans `moteur/nombres.py` (`grouper`, `formater_entier`, `formater_decimal`, `nettoyer_saisie`), à réutiliser par **T23**.
