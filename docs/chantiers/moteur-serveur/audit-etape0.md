# Chantier « moteur-serveur » : audit (étape 0)

06.11.2026, Claude Code, sur `main` (f92112e), PC (WSL2, Ryzen 5 5600X). Aucun fichier du dépôt modifié hors de celui-ci ; aucun commit.
Les mesures et le prototype sont dans le dossier temporaire de la session (hors du dépôt), décrits en annexe pour pouvoir les refaire.

**But.** Faire tourner les moteurs Python sur un serveur (Infomaniak) au lieu de Pyodide dans le navigateur. La page ne reçoit plus que la
sortie JSON, le moteur n'est plus public, et plus tard un accès réservé devient possible. Ensuite, l'onglet « S'entraîner » sera construit
directement côté serveur (`quiz.md` § 8).

---

## 0. En bref

- **Le passage est petit côté code.** Toutes les pages passent par un seul point d'entrée, `MoteurPython.appelPy(fn, arg, délai)`
  (`commun/moteur-python.js`). La fonction appelée est `<module>.<fn>_json(arg)`, et la liste blanche des fonctions est dans
  `moteur/manifeste.json`. Il suffit de remplacer le Worker par un `fetch` vers `POST /api/<outil>/<fn>`, avec la même interface JS ;
  aucun moteur Python ne change.
- **L'invariant « sorties identiques à l'octet » tient par HTTP, mesuré.** Un prototype jetable (WSGI, gunicorn) a rejoué tout le dump
  par HTTP : 4 178 appels `resoudre`, `apercu` et `controle`, **4 178 identiques à l'octet**. Les sorties ne dépendent pas non plus de
  `PYTHONHASHSEED` : les dumps faits avec 0, 12345 et `random` sont identiques (`diff -r` code 0).
- **Le serveur demandé est minuscule.** En Python natif, un `resoudre` prend de 1 à 60 ms en médiane selon l'outil, 1 s au pire du
  corpus (Limites). Un processus de travail occupe environ 85 Mo de mémoire. Pour 30 élèves simulés (4 processus), les temps de réponse
  sont de 2 ms en médiane et de 154 ms au 99e centile. Un VPS de 1 à 2 vCPU et 2 Go suffit largement.
- **Offre la plus adaptée : VPS Lite d'Infomaniak**, de 2.70 à 5.40 CHF HT par mois, payé à l'année. Il n'est pas géré : les mises à jour
  sont à votre charge, et il n'a ni snapshot ni disponibilité garantie. L'hébergement Web mutualisé **ne fait pas tourner Python**
  (FAQ Infomaniak 1307 et 516).
- **Le domaine samimir.ch est déjà chez Infomaniak** : registraire « Infomaniak Network SA » et DNS `ns11/ns12.infomaniak.ch`. Il pointe
  aujourd'hui vers GitHub Pages (4 A en 185.199.108–111.153, `www` en CNAME vers `samimirmath.github.io`).
- **Deux pièges** (détails en § 5) :
  1. Un dépôt privé perd GitHub Pages sur le plan gratuit : il faut donc déplacer le site avant de rendre le dépôt privé.
  2. Les tests GitHub Actions dépasseraient le quota gratuit d'un dépôt privé. On a mesuré 1 121 minutes facturables du 1er au
     06.11.2026, alors que le plan Free inclut 12 USD par mois, soit environ 2 000 minutes Linux.
- **Ce qui a déjà été publié reste public.** Le code des moteurs est dans l'historique public depuis le 09.10.2026 (381 commits, aucune
  bifurcation, nombre de clones inconnu). Rendre le dépôt privé ne protège que **ce qui sera écrit ensuite** : générateurs du quiz,
  réserve d'exercices, futures versions. Il faut donc que le dépôt soit privé **avant** d'écrire les générateurs de « S'entraîner ».

---

## 1. Ce que charge chaque outil aujourd'hui

### 1.1 Point d'entrée commun

- `commun/outil.js` (`monterOutil`) crée un `MoteurPython(outil)` et n'appelle le moteur que par `appelPy`. Il fait 6 appels, aux
  lignes 121, 172 à 177, 188, 223, 362 et 366 : `apercu` à chaque frappe (après 150 ms sans frappe, délai de 5 s), `resoudre` (délai de
  30 s, `window.__delaiCalcul` dans les tests), `exercice`, ainsi que `controle` et `fenetre` par les greffons. Deux appels ne passent
  pas par `outil.js` :
  - `commun/graphique.js:357` appelle `fenetre` (zoom du graphique de l'Étude complète, délai de 10 s) ;
  - `ensemble-definition/index.html:95` appelle `controle` (greffon `apres`, délai de 20 s).
- `commun/moteur-python.js` (126 lignes) :
  1. il lit le manifeste, puis télécharge les fichiers `.py` de l'outil ;
  2. il lance `commun/worker-pyodide.js` (59 lignes), qui charge Pyodide 0.27.7 depuis jsDelivr, écrit les fichiers **à plat** (règle A8)
     et importe le module ;
  3. SymPy et mpmath arrivent ensuite, par les roues précompilées du site (`moteur/roues/`, 7,1 Mo) ou, à défaut, par le CDN. Ils sont
     chargés après une pause de frappe (700 ms) ou tout de suite si un calcul renvoie `besoin_sympy` (`hater`) ;
  4. `appelPy` vérifie la liste blanche, attend `pret`, puis analyse la chaîne JSON reçue. Au-delà du délai, il rejette avec
     `Error("delai")` et `relancer()` recrée le Worker (SOC-13).
- Le contrat ne change pas : la page n'écrit aucun texte de corrigé, et `rendu.js` affiche les blocs validés par `sortie.valider`.

### 1.2 Par outil (manifeste au 06.11.2026)

| Outil | Module | Fichiers | Taille téléchargée | Lignes | Fonctions de la page |
|---|---|---|---|---|---|
| ensemble-definition | `resoudre_ed` | 3 | 130 Ko | 3 280 | resoudre, apercu, controle |
| derivee-variations | `resoudre_dv` | 5 | 195 Ko | 4 758 | resoudre, apercu |
| limites-asymptotes | `resoudre_la` | 6 | 356 Ko | 8 857 | resoudre, apercu |
| etude-complete | `resoudre_ec` | 13 | 560 Ko | 13 219 | resoudre, apercu, fenetre |
| factorisation | `resoudre_fa` | 5 | 200 Ko | 5 149 | resoudre, apercu, exercice |
| exponentielles-logarithmes | `resoudre_el` | 11 | 486 Ko | 10 510 | resoudre (filière C/M), apercu, exercice (niveau, filière) |
| equations-2e-degre | `resoudre_eq` | 10 | 332 Ko | 7 434 | resoudre, apercu |
| simplexe | — (JS, D11) | — | — | 1 067 (page) | — |

Tous les outils chargent aussi SymPy 1.13.3 et mpmath 1.3.0 (6,6 Mo et 0,7 Mo de roues), avec Pyodide d'environ 5 à 9 s de
démarrage. Jusqu'à « Prêt. », il faut environ 5,5 s sur ordinateur et nettement plus sur téléphone (`docs/choix-techniques.md`, D13).
Le moteur du 2e degré est en Python pur (`decisions.md` du 2e degré : sans SymPy), mais il passe par `ensemble_def`, qui demande SymPy
paresseusement.

### 1.3 Ce qui reste public après le chantier

- **Le simplexe** : son moteur est en JS dans la page (D11). Il reste lisible tant qu'il n'est pas porté en Python. À décider (M10).
- **Les listes d'exercices écrites dans les pages** (`EXOS` de ED, DV, LA, EC) et les poids des niveaux. Une liste publique n'enfreint
  pas la règle des examens : vous choisissez l'examen hors de la liste. En revanche, les générateurs `exercice` de Factorisation et d'EL
  passent côté serveur avec le reste.
- `commun/*.js` et `*.css` : ce sont l'affichage et la saisie, sans aucun corrigé. Rien de secret.
- L'historique git public jusqu'au passage en privé (voir § 0).

---

## 2. Mesures (Python natif, corpus des tests)

Sources des corpus :
- **mesure 1** : le corpus fixe de `tests/outils/dump_sorties.py`, avec les clés des instantanés, les exemples et `EXOS` des pages, les
  entrées de `tests/pages/rendu.py` et les corpus de l'enseignant (`tests/python/donnees/`) ;
- **dump** : en plus, les énoncés des exercices tirés.

Chaque outil tourne dans un processus neuf, sur le PC (le processeur d'un VPS sera sans doute 1,5 à 2 fois plus lent : à mesurer en P2).

| Outil | Corpus | `resoudre` médiane | p90 | max | entrée la plus lente | `apercu` max | Sortie moyenne / max | Mémoire au pic |
|---|---|---|---|---|---|---|---|---|
| ensemble-definition | 42 | 0,2 ms | 0,6 ms | 118 ms (1er appel) | `sqrt(ln(x)-x+2)` | 0,1 ms | 1,0 / 2,6 Ko | 65 Mo |
| derivee-variations | 33 | 4,9 ms | 24 ms | 108 ms | `(x^2-1)/(x-3)` | < 0,1 ms | 1,7 / 3,4 Ko | 65 Mo |
| limites-asymptotes | 66 | 49 ms | 205 ms | **1,01 s** | `x*e^x/(1-e^x)` | 0,1 ms | 4,8 / 13,9 Ko | 69 Mo |
| etude-complete | 22 | 61 ms | 249 ms | 276 ms | `sqrt(x^2-4)` | 0,1 ms | **51,7 / 62,3 Ko** | 65 Mo |
| factorisation | 194 | 3,8 ms | 13 ms | 63 ms | `x^3 - 9x^2 + 23x - 15` | 0,1 ms | 1,0 / 3,9 Ko | 65 Mo |
| exponentielles-logarithmes C / M | 667 | 0,9 / 0,7 ms | 1,8 / 1,7 ms | 11 / 3,5 ms | `-x*ln(x)-x=0` | 0,1 ms | 3,7 / 21,6 Ko | 65 Mo |
| equations-2e-degre | 225 | 2,1 ms | 3,6 ms | 17 ms | `x^2+1-(10-x^2)/8=(6x-3)/4` | 0,3 ms | 2,1 / 5,1 Ko | 65 Mo |

D'autres temps, mesurés à part :
- démarrage d'un processus (`import sympy`, Python 3.12, bytecode en cache) : 0,2 s, pour 49 Mo ;
- `fenetre` (zoom de l'Étude complète, 500 points) : 1 à 2 ms, pour environ 21 Ko de réponse ;
- la plus grosse réponse est celle de l'Étude complète : 61 Ko pour `(x^2-1)/(x-3)`, 26 Ko après gzip.

**Charge de 30 élèves.** Le prototype (gunicorn, 4 processus synchrones, un seul processus pour tous les outils grâce à A8) a tourné
60 s sur le PC. Chaque élève simulé :
1. tire une entrée au hasard dans le dump, tous outils confondus ;
2. tape 6 aperçus, un toutes les 200 ms ;
3. demande `resoudre` ;
4. pense en moyenne 3 s, puis recommence.

Cette charge est bien plus forte qu'en classe.

| Appel | Requêtes | Débit | Médiane | p95 | p99 | max |
|---|---|---|---|---|---|---|
| apercu | 2 658 | 40 req/s | 1 ms | 1 ms | 5 ms | 27 ms |
| resoudre | 443 | 6,7 req/s | 2 ms | 9 ms | 154 ms | 379 ms |

- **Rafale** : 30 « Calculer » simultanés sur l'entrée la plus lente (`x*e^x/(1-e^x)`) donnent 0,35 s pour le premier, 2,2 s en
  médiane et 3,1 s pour le dernier.
- **Mémoire** : environ 85 Mo par processus de travail après la charge, et environ 410 Mo en tout avec 4 processus et le maître.
- **Ces chiffres ne comptent pas le réseau.** Il faudra ajouter l'aller-retour vers le centre de données suisse, sans doute 10 à 40 ms
  depuis l'école : à mesurer en P2.

**Conséquences.**
- 1 vCPU suffit pour une classe ; 2 vCPU donnent de la marge pour deux classes en même temps ou pour la rafale.
- 2 Go de mémoire suffisent : 4 processus × environ 100 Mo, plus nginx et le système.
- Le premier appel d'un processus neuf est plus lent, car le cache de SymPy est froid (118 ms en ED) : on charge tout au démarrage
  (`--preload`).

---

## 3. Ce qu'il faut sur le serveur

- **Python 3.12, SymPy 1.13.3, mpmath 1.3.0**, aux versions figées, les mêmes que les tests. Pyodide ne contraint plus les versions,
  mais changer SymPy peut changer des sorties : toute montée de version passe par le dump identique (§ 7).
- **Un serveur d'application à processus synchrones** (gunicorn ou équivalent) : une requête à la fois par processus. Trois raisons :
  - un calcul SymPy ne s'interrompt pas depuis un fil ; seul le processus peut être tué ;
  - il existe un état de module, toléré par A7, que des fils partageraient (`exp_log._DECIMAUX`) ;
  - `random` sert à `exercice`.

  Le serveur doit aussi :
  - tuer un processus au-delà d'un délai (par exemple 35 s, au-dessus des 30 s de la page) ;
  - recycler un processus après N requêtes (`max_requests`), car le cache de SymPy grossit ;
  - limiter la mémoire (systemd `MemoryMax`, ou `RLIMIT_AS` par processus) ;
  - fixer une taille maximale des entrées (le prototype refuse plus de 4 Ko).
- **Une application minimale**, sans framework : environ 30 lignes, déjà écrites pour le prototype. `POST /api/<outil>/<fn>`, avec
  comme corps l'argument JSON (une chaîne, ou un tableau pour `[entrée, filière]`), et comme réponse **la chaîne brute** de
  `<fn>_json`. L'outil et la fonction sont vérifiés contre le manifeste : il garde son rôle de liste blanche, mais ne sert plus à
  télécharger des fichiers.
- **nginx** en façade : HTTPS (certbot / Let's Encrypt, à installer soi-même sur un VPS), gzip des réponses JSON (la plus grosse passe
  de 61 Ko à 26 Ko), limite de requêtes (§ 6), fichiers statiques du site si tout est hébergé au même endroit (§ 5).
- **L'entretien demandé** (VPS non géré) :
  - mises à jour de sécurité automatiques (`unattended-upgrades`) ;
  - pare-feu (ports 22, 80 et 443), SSH par clé seulement ;
  - certbot en renouvellement automatique ;
  - une page de santé surveillée par un service gratuit (par exemple UptimeRobot) ;
  - un redémarrage de l'application automatique (systemd) ;
  - une mise à niveau de l'OS tous les 2 à 4 ans (Debian ou Ubuntu LTS).

  Comptez environ 1 h par trimestre une fois l'installation faite, plus une demi-journée pour l'installation. Tout est décrit pas à pas
  dans un fichier du dépôt (P2), et la machine se reconstruit par un script : le VPS Lite n'a pas de snapshot.

---

## 4. Offres Infomaniak (lues sur infomaniak.com le 06.11.2026, prix HT, TVA 8,1 % en plus)

| Offre | Plus petite configuration | CHF / mois HT | Entretien | Python persistant |
|---|---|---|---|---|
| **VPS Lite** | 1 vCPU, 2 Go, 20 Go NVMe ; aussi 2 vCPU / 2 Go / 40 Go à 5.40 et 2 vCPU / 4 Go / 60 Go à 7.20 | **2.70**, avec engagement annuel payé d'avance | À votre charge (OS, mises à jour) ; pas de snapshot, pas de disponibilité garantie | Oui (root, SSH) |
| VPS Cloud | 4 vCPU, 12 Go, 250 Go ; 99,99 % garantis, 1 snapshot | dès 38.41 | À votre charge | Oui |
| Serveur Cloud managé | 4 vCPU, 12 Go | dès 38.41 | Géré par Infomaniak | Douteux (la FAQ 516 l'exclut pour Django) : à confirmer au support |
| Hébergement Web (mutualisé) | 250 Go, 20 sites | dès 10.91 | Géré | **Non** (FAQ 1307 : Python non supporté) ; un seul site Node.js |
| Jelastic Cloud (PaaS) | 1 cloudlet = 128 Mo, 400 MHz ; il en faudrait 3 à 5 | environ 6.31 par cloudlet, à l'heure | Plateforme gérée ; le contenu du conteneur n'a pas été vérifié | Oui |
| Hébergement Starter | 10 Mo, 1 Go de trafic par mois | gratuit avec un domaine | Géré | Non (fichiers statiques) |

Le site statique sans les moteurs ni les roues pèse **287 Ko** : il tiendrait dans le Starter, mais il faut vérifier que les fichiers
`.js` y sont servis. Le prix de la plus petite instance du Public Cloud (OpenStack) n'a pas pu être lu : la page est chargée par
JavaScript. Les données sont en Suisse (TIER III+, ISO 27001), et la conformité « RGPD et LPD » est affichée.

**Recommandation : VPS Lite, 2 vCPU / 2 Go**, environ 65 CHF HT par an. Le modèle 1 vCPU / 2 Go (environ 32 CHF HT par an) suffit
d'après les mesures, mais on ne peut ensuite qu'augmenter les ressources : on peut commencer petit, puisque monter reste possible.

---

## 5. Où héberger, DNS, dépôt privé, minutes des tests

**Trois montages possibles :**

| | A. Tout sur le VPS (recommandé) | B. Site statique ailleurs, moteur sur le VPS | C. GitHub Pro + Pages, moteur sur le VPS |
|---|---|---|---|
| Site | nginx du VPS | Starter Infomaniak, ou un hébergeur statique gratuit relié au dépôt privé | GitHub Pages (dépôt privé) |
| Adresse du moteur | `samimir.ch/api/…` (même origine, **pas de CORS**) | `api.samimir.ch` (CORS limité à `https://samimir.ch`) | `api.samimir.ch` (CORS) |
| Coût en plus | 0 | 0 | GitHub Pro (environ 4 USD par mois, non vérifié dans ce chantier) |
| Mise en ligne | script de déploiement (ci-dessous) | deux mises en ligne à synchroniser | push sur `main` plus déploiement du moteur |
| Version de la page et du moteur | une seule mise en ligne, donc toujours accordées | elles peuvent différer quelques minutes | idem |

- **DNS.** La zone de samimir.ch est déjà gérée chez Infomaniak.
  - Montage A : on remplace les 4 A de GitHub par l'IPv4 du VPS (et un AAAA), et `www` par un CNAME vers `samimir.ch` (ou une
    redirection).
  - Montage B ou C : on ajoute seulement `api` en A/AAAA.
  - Pour passer sans coupure : baisser le TTL la veille, garder GitHub Pages en ligne jusqu'à la propagation, puis retirer le CNAME
    du dépôt.
- **La mise en ligne remplace le « push = en ligne » de GitHub Pages.** Proposé : `tests/deployer.py` (ou un script shell).
  1. Il refuse si l'arbre n'est pas propre, si `main` n'est pas à jour, ou si la suite de référence n'est pas verte.
  2. Il envoie par `rsync` une **copie datée** (dossier `versions/<commit>/`), puis bascule un lien symbolique et recharge gunicorn,
     qui recharge les moteurs en douceur.
  3. Il vérifie `/api/sante` et rejoue quelques entrées du dump.

  On revient en arrière en rebasculant le lien. C'est l'enseignant qui lance ce script, comme aujourd'hui pour `git push`.

  On peut aussi faire déployer par une GitHub Action par SSH : c'est quelques minutes par déploiement, mais une clé SSH est alors
  stockée chez GitHub.
- **Le dépôt privé ensuite.** Sans GitHub Pages, un dépôt privé est gratuit. L'ordre est imposé : (1) le site est servi par le VPS ;
  (2) ensuite, Pages est désactivé et le dépôt passe en privé. Dans l'autre ordre, le site tombe. Ce qui a déjà été publié reste dans
  les copies existantes (§ 0).
- **Minutes des tests en privé.** Mesuré sur les exécutions de « Tests » du 14.10 au 06.11.2026 :
  - 87 exécutions, 1 391 minutes facturables (arrondi à la minute par job) : le job Python dure 4,6 min en moyenne, le job Pages 15 min
    (22 min au maximum) ;
  - **novembre : 1 121 minutes en 6 jours**, à un rythme d'environ 20 pushs par jour.

  En privé, le plan Free inclut 12 USD par mois, soit environ 2 000 minutes Linux 2 cœurs à 0,006 USD. Ce quota serait épuisé en une
  dizaine de jours. Options :
  1. lancer les tests GitHub seulement sur `main` et à la demande (`workflow_dispatch`), puisque la suite complète tourne déjà en local
     avant chaque commit (CLAUDE.md) ;
  2. **un runner auto-hébergé sur le PC** (gratuit, illimité ; le PC doit être allumé) ;
  3. garder seulement le job Python (5 min) ;
  4. accepter un dépassement payant, avec une limite de dépense à 0 USD pour ne rien payer par surprise.

  Après le chantier, les tests de pages n'auront plus à démarrer Pyodide dans chaque page, ce qui devrait les raccourcir nettement :
  non mesuré, à mesurer en P4.

---

## 6. Si le serveur ne répond pas ; limite de requêtes ; données

**Ce que voit l'élève.** Le socle a déjà les textes (SOC-07 et `outil.js`). Il faut les rebrancher sur le réseau, sans rien afficher de
faux :

| Situation | Aujourd'hui (Pyodide) | Proposé (serveur) |
|---|---|---|
| Ouverture de la page | « Chargement du moteur de calcul… » pendant 5 à 20 s, puis « Prêt. » | Un appel `/api/sante` (moins de 50 ms), puis « Prêt. ». Plus de chargement de SymPy : `sympyAvant`, `besoin_sympy`, `hater` et SOC-21 deviennent sans objet. |
| Serveur injoignable à l'ouverture | — | Le message existant, « Impossible de charger l'outil de calcul. Vérifiez votre connexion internet, puis rechargez la page. » ; bouton « Calculer » désactivé. |
| Panne pendant un calcul | — | La carte d'erreur : « Le serveur de calcul ne répond pas : réessayez dans un instant. » (texte nouveau, à valider, R12). Aucun corrigé partiel. |
| Calcul trop long | Délai de 30 s, le Worker est relancé (SOC-13) | Même délai côté page (`AbortController`). Le serveur tue son processus à 35 s ; `relancer()` ne fait plus rien d'autre que vider l'état. Même message. |
| Trop de requêtes (429) | — | « Trop de calculs en même temps : réessayez dans quelques secondes. » (texte nouveau, à valider). |
| Aperçu qui échoue | L'erreur est ignorée, l'aperçu estompé | Inchangé : une réponse perdue n'affiche rien d'obsolète. |

Sans connexion internet, l'outil ne fonctionne plus du tout. Aujourd'hui non plus, puisque Pyodide vient de jsDelivr. En revanche, une
page déjà « Prête » continue de calculer hors ligne aujourd'hui, et ce ne sera plus le cas.

**Limite de requêtes.** Il n'y a aucun compte, donc la seule clé possible est l'adresse IP. Or **une classe derrière le NAT de l'école
partage souvent une seule IP**. Une limite par IP doit donc laisser passer 30 élèves. D'après la mesure du § 2 : 47 req/s en tout,
dont 40 d'aperçus.

Proposé :
- nginx `limit_req` par IP à environ 60 req/s, avec une rafale de 200 ;
- au plus 8 calculs `resoudre` en cours par IP (`limit_conn`), au-delà réponse 429 ;
- la vraie protection est ailleurs : délai par calcul, recyclage et mémoire bornée (§ 3), et file d'attente bornée de gunicorn.

Un élève qui enverrait des milliers d'entrées très lentes saturerait les 4 processus pour tous, au pire 35 s par requête. On accepte ce
risque tant qu'il n'y a pas de comptes ; un accès réservé (jeton par classe, plus tard) le règle.

On peut aussi espacer les aperçus de 150 ms à 250 ms pour diviser leur nombre par environ 1,5 : cela changerait la sensation de
frappe, donc c'est à décider (M7).

**Protection des données (sans comptes).** Le serveur ne reçoit que des saisies mathématiques et l'adresse IP. Proposé :
- journal d'accès sans le corps des requêtes, IP gardées 7 jours puis effacées (nécessaire pour la limite et les abus) ;
- aucun cookie, aucun stockage ;
- serveur en Suisse, chez Infomaniak.

Une ligne « Données » dans le pied de l'accueil dirait « les calculs sont faits sur un serveur en Suisse ; aucune donnée personnelle
n'est enregistrée, sauf l'adresse IP, 7 jours, pour la sécurité ». À faire vérifier par l'école, comme l'accès payant : la LPD
(nLPD) s'applique, et la décision n'est pas technique. La balise GoatCounter de l'accueil ne change pas. Plus tard, avec des comptes
ou un jeton par classe : nouvelle analyse.

---

## 7. Garder l'invariant « sorties identiques à l'octet »

Les moteurs ne changent pas. Seul le transport change : il faut prouver que le serveur renvoie **la chaîne brute** de `<fn>_json`,
sans re-sérialisation (`json.loads` puis `json.dumps` changerait des espaces ou l'échappement d'`ensure_ascii`).

1. **Le dump par HTTP** : on ajoute à `tests/outils/dump_sorties.py` une option `--serveur <URL>`, qui fait les mêmes appels par
   `POST`. `diff -r --exclude=temps <dump direct> <dump HTTP>` doit donner un code 0. Le prototype l'a fait : 4 178 appels identiques.
   Pour `exercice`, le serveur doit recevoir une graine, sinon `random.seed` côté test ne l'atteint pas : soit un paramètre de test
   réservé au serveur local, soit `exercice(niveau, graine)`, qui existe déjà dans EL (`exp_log.exercice`).
2. **Un test Python `test_serveur.py`** : l'application WSGI est appelée **en processus**, sans réseau, sur le corpus réduit, à
   l'octet. Il vérifie aussi :
   - la liste blanche (outil ou fonction hors du manifeste : 404) ;
   - la taille maximale (413) ;
   - la méthode (seul `POST`) ;
   - l'en-tête `Content-Type` ;
   - l'en-tête CORS, en montage B ou C.
3. **Les instantanés** (`test_instantanes*.py`) appellent déjà les moteurs directement : ils ne changent pas.
4. **Les tests de pages** (`tests/pages/navigateur.py`) servent déjà le dépôt par un serveur HTTP local et interceptent jsDelivr. Le
   serveur local de test sert aussi `/api/…` **avec la même application WSGI**, dans un processus à part. Il n'y a ni Pyodide ni réseau,
   et le garde-fou F6 (aucune requête ne sort) reste. Ce qui change :
   - `pyodide_local.py`, `test_pyodide_local.py`, le cache Pyodide de la CI et `test_roues.py` disparaissent à la fin (P5), avec une
     justification dans `suivi.md` (tests disparus) ;
   - `test_t31_libelle_pendant_le_chargement_de_sympy` et `test_t40_l_apercu_ne_attend_pas_sympy` (SOC-21) deviennent sans objet ;
     ils sont remplacés par « serveur injoignable » et « 429 » ;
   - `test_soc13_*` : le délai est simulé par une entrée de test qui dort, servie par le serveur de test seulement.

   Les références de pages (`capturer_references.py`, `test_rendu.py`) doivent rester identiques.
5. **En production, après chaque déploiement** : rejouer une vingtaine d'entrées du dump contre le vrai serveur (`deployer.py`, § 5).
   On contrôle ainsi aussi les versions de Python et de SymPy du VPS.

Pendant la migration, outil par outil, les deux chemins coexistent. Une clé `"execution": "serveur"` par outil dans le manifeste choisit
le client (`MoteurServeur` ou `MoteurPython`) ; `test_manifeste` la vérifie. À la fin, on retire Pyodide et la clé.

---

## 8. « S'entraîner » côté serveur, avec la règle des examens

La règle (`quiz.md` § 8, mémoire « tirage et examens ») : un exercice tiré ne doit jamais pouvoir tomber à l'examen, et aucune liste
d'exclusion n'est lisible. Le § 8 a écarté l'ancienne piste des « bornes publiques ».

**Proposé :**
- **La réserve est construite sur votre machine, pas sur le serveur.** Le générateur (familles F1 à F17, dans le dépôt privé) produit
  une **réserve** d'exercices, avec une graine secrète. Les exercices d'examen en sont retirés **en local**, à partir de
  `docs/reference/` (jamais commité). On n'envoie au serveur que la réserve déjà filtrée, par exemple `reserve.json` : quelques milliers
  d'exercices, renouvelée chaque semestre.
- **Ainsi la liste d'examen ne quitte jamais votre machine**, même si le serveur était compromis, et l'absence d'un exercice dans une
  réserve tirée au hasard ne se voit pas.
- **Des identifiants opaques** au lieu de `<famille>-<graine>` (QZ-13 à revoir). `?exo=` porte un numéro de la réserve (ou un jeton
  court) ; le serveur refuse tout numéro hors de la réserve. Ainsi, un élève qui essaie des graines ne peut pas faire tourner le
  générateur lui-même ni explorer l'espace des tirages.
- **Le quiz entier est envoyé à la page** (`quiz_json(exo)` : étapes, boutons, explications). Les bonnes réponses se lisent alors dans
  les outils du navigateur : c'est sans importance pour un entraînement non noté, et cela garde la page fluide, sans un aller-retour par
  clic. Si un jour le quiz est noté, il faudra vérifier chaque réponse côté serveur (à décider : M9).
- **« Voir dans Résoudre »** résout n'importe quelle équation, celles de l'examen comprises. La règle porte sur le tirage, pas sur
  Résoudre : c'est à confirmer (M9).
- **Les générateurs `exercice` existants** (Factorisation, EL) et les listes `EXOS` publiques des pages : la règle s'applique-t-elle à
  eux aussi ? À trancher (M9). Si oui, la même réserve filtrée peut les remplacer.

**Dépendances.** `entrainement-2e-degre/decisions.md` est à revoir avant son exécution : QZ-13, E4 (réserve, construction locale,
identifiants opaques), et E5 (la page appelle `quiz` par le serveur). Ce chantier ne démarre qu'après P6 ci-dessous (dépôt privé),
pour que les générateurs ne soient jamais publiés.

---

## 9. Décisions à prendre par l'enseignant

| # | Décision | Proposition |
|---|---|---|
| M1 | Offre | VPS Lite 2 vCPU / 2 Go (5.40 CHF HT par mois, payé à l'année), ou 1 vCPU / 2 Go (2.70) pour commencer. Pas le mutualisé : il ne fait pas tourner Python. |
| M2 | Tout chez Infomaniak, ou seulement le moteur | **Montage A, tout sur le VPS** : même origine, une seule mise en ligne, page et moteur toujours accordés, pas de GitHub Pro. |
| M3 | Mise en ligne | Script `deployer.py` lancé par l'enseignant (copie datée et retour en arrière), plutôt qu'une Action GitHub qui garde une clé SSH. |
| M4 | Tests GitHub en privé | Python seulement, ou bien sur `main` et à la demande ; ou un runner sur le PC. Limite de dépense à 0 USD. |
| M5 | Moment du passage en privé | Après P5 (site et tous les moteurs servis par le VPS), et **avant** le chantier S'entraîner. |
| M6 | Textes nouveaux pour l'élève | « Le serveur de calcul ne répond pas : réessayez dans un instant. » ; « Trop de calculs en même temps : réessayez dans quelques secondes. » ; ligne « Données » de l'accueil. |
| M7 | Aperçu à chaque frappe | Garder 150 ms (les mesures le permettent), ou passer à 250 ms. |
| M8 | Données et accès réservé | Journal sans saisies, IP 7 jours. Demander à l'école (LPD, accès payant) avant tout compte. |
| M9 | Règle des examens : portée | Le quiz est envoyé entier ; « Voir dans Résoudre » reste libre ; les générateurs FA et EL et les `EXOS` des pages : la règle s'y applique-t-elle ? |
| M10 | Simplexe (JS, public) | Le laisser en JS (D11) tant qu'il n'y a pas d'exercice d'examen tiré ; sinon, un chantier à part. |
| M11 | Repli Pyodide | Le supprimer à la fin (P5), plutôt que de le garder en secours : un repli rendrait le moteur de nouveau public. |

---

## 10. Découpage proposé (une partie = un commit ; le 2e degré en premier)

| Partie | Contenu | Dépend de | Tests |
|---|---|---|---|
| **P0** | Branche `moteur-serveur`, `suivi.md` et `journal.md`, référence des tests (`complet --rapport` puis `reference`), dump de départ. | — | Suite complète. |
| **P1** | **L'application serveur dans le dépôt** (`serveur/app.py`, WSGI sans framework, liste blanche lue dans le manifeste, taille maximale, `/api/sante`), `test_serveur.py` en processus, option `--serveur` de `dump_sorties.py`. Règle d'architecture nouvelle (A10 : le serveur n'appelle que des `<fn>_json` du manifeste, n'importe aucun outil par son nom) dans `test_imports`. Rien ne change pour les pages. | P0 | Dump direct = dump par HTTP local, à l'octet ; `test_serveur`. |
| **P2** | **Le VPS** (enseignant, guidé pas à pas par `serveur/INSTALLATION.md`) : Debian, utilisateur, SSH, pare-feu, `unattended-upgrades`, Python 3.12, paquets aux versions figées, gunicorn sous systemd (délai, recyclage, mémoire), nginx, certbot, limite de requêtes. Mesure du temps réel depuis l'école ou un téléphone. | P1, M1 | Dump par HTTP contre le VPS identique ; mesure de charge (§ 2) refaite sur le VPS. |
| **P3** | **Client `MoteurServeur`** dans `commun/` : même interface que `MoteurPython` (`demarrer`, `appelPy`, `relancer`, `sympyOK` toujours vrai). Clé `execution` du manifeste. Messages M6. Serveur de test dans `navigateur.py`. **L'outil du 2e degré passe au serveur** ; les autres restent sur Pyodide. Adresse du serveur dans une seule constante (montage A : chemin relatif `/api`). | P1, M2, M6 | Références de pages du 2e degré inchangées ; `test_largeurs` ; nouveaux tests « serveur injoignable », « 429 » et « délai ». |
| **P4** | Les autres outils, l'un après l'autre (ED, DV, LA, EC avec `fenetre`, FA et EL avec `exercice` et sa graine), avec une mesure du temps des tests de pages. | P3 | Références de pages identiques, outil par outil. |
| **P5** | **Retrait de Pyodide** : `worker-pyodide.js`, `moteur-python.js`, `moteur/roues/`, `construire_roues.py`, `pyodide_local.py` et ses tests, cache de la CI, `sympyAvant` et `besoin_sympy`. Mise à jour de `choix-techniques.md` (D1, D10, D13), `architecture.md`, `socle-commun.md` (SOC-13, SOC-14, SOC-21) et CLAUDE.md (avec votre accord). Les moteurs ne sont plus servis comme fichiers (nginx refuse `*.py`). | P4, M11 | Suite complète ; tests disparus justifiés dans `suivi.md`. |
| **P6** | **Bascule** (enseignant, guidé) : `deployer.py` (M3), DNS (TTL, A et AAAA, `www`), contrôle sur iPhone, Pages désactivé, dépôt en privé, workflow des tests adapté (M4). | P5, M2 à M5 | `deployer.py` rejoue le dump ; vérification sur iPhone. |
| **ensuite** | Chantier `entrainement-2e-degre`, revu pour le serveur (§ 8). | P6 | — |

P3 peut être mis en ligne avant P4 (le 2e degré par le serveur, le reste par Pyodide), mais seulement en montage B ou C ou après P6 en
montage A. En montage A, le plus simple est de développer P3 et P4 en local, contre le serveur de test et le VPS, puis de tout basculer
en P6. **Ce qui n'a pas été vérifié** : la vitesse d'un vCPU du VPS Lite ; l'IPv4 du VPS Lite, qui n'est pas écrite noir sur blanc ;
les fichiers `.js` sur le Starter ; le prix exact de GitHub Pro ; l'aller-retour réseau depuis l'école.

---

## Annexe : refaire les mesures

- Temps et mémoire par outil : un script lit le corpus fixe de `dump_sorties.corpus_fixe` et lance un processus neuf par outil, sous
  `uv run --python 3.12 --with sympy==1.13.3 --with mpmath==1.3.0` avec `PYTHONHASHSEED=0`. Il mesure `perf_counter` par appel,
  `VmRSS` et `ru_maxrss`.
- Indépendance de la graine de hachage : `dump_sorties.py` avec `DUMP_SORTIES_UV=1` et `PYTHONHASHSEED` à 0, 12345 et `random`, puis
  `diff -r --exclude=temps`.
- Prototype : environ 30 lignes WSGI (`POST /api/<outil>/<fn>`, chaîne brute), `gunicorn -w 4 --timeout 35`. Le rejeu du dump
  (8 fils) donne 4 178 appels identiques, et la charge simule 30 élèves sur 60 s.
- Minutes de CI : `gh api repos/SamiMirMath/site/actions/runs/<id>/jobs` sur les 87 exécutions de « Tests » depuis le 14.10.2026, avec
  un arrondi à la minute par job.
