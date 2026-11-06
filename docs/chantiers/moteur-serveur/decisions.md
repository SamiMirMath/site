# Moteur sur serveur : décisions

**Statut : validé par l'enseignant le 06.11.2026** (brouillon relu par un sous-agent indépendant puis corrigé ; questions du § 9
toutes réglées le même soir). Ce fichier fait foi : `CLAUDE.md` > `decisions.md` > `suivi.md` > `audit-etape0.md`.

**Références.**
- Audit : `docs/chantiers/moteur-serveur/audit-etape0.md`. Il contient les mesures, les offres, le prototype et le découpage ; ce
  fichier le précise et le tranche.
- Règles générales : `docs/architecture.md` (A1 à A9), `docs/methode-chantiers.md`, `docs/specifications/socle-commun.md` (SOC-07,
  SOC-13, SOC-15, SOC-21, SOC-22), `docs/guide-redaction.md` (R12 : vouvoiement).
- Règle des examens : `docs/chantiers/equations-2e-degre/quiz.md` § 8.
- Arbre des tâches : `arbre.md`, un document de travail jamais commité.

**Numérotation.** Les décisions de l'enseignant gardent leurs numéros **M1 à M11** (ceux de `arbre.md`) et les décisions techniques
sont notées **T1 à T17**. Cela évite toute confusion avec les D1, D10, D13… de `docs/choix-techniques.md`.

**But.** Les moteurs Python tournent sur un VPS Infomaniak au lieu de Pyodide, et la page n'en reçoit que la sortie JSON. Le site
entier, pages et moteur, est servi par le VPS. Ensuite, le dépôt GitHub passe en privé et ne sert plus que de dépôt. Le chantier
« S'entraîner » vient après et ne fait pas partie de celui-ci.

---

## 1. Principes

1. **Rien de faux à l'écran.**
   - Une réponse du serveur n'est affichée que si elle répond à la **dernière** demande de l'élève (T7).
   - Une panne donne un message clair (§ 5), jamais un corrigé partiel, périmé ou d'une autre saisie.
   - Un message ne dit rien d'inexact sur ce qui se passe (par exemple « relancé » alors que rien ne l'est).
   - Le détail technique ne va que dans la console.
2. **Sorties identiques à l'octet.**
   - Le serveur renvoie **la chaîne brute** de `<fn>_json`, jamais re-sérialisée : `json.loads` puis `json.dumps` changerait des
     espaces ou l'échappement.
   - Aucun moteur ne change dans ce chantier (T9).
   - Le dump direct et le dump par HTTP sont identiques (`diff -r --exclude=temps`, code 0), et les références de pages restent
     identiques.
3. **Le manifeste reste la liste blanche.** Le serveur n'appelle que les couples outil–fonction de `moteur/manifeste.json`, et
   rien d'autre.
4. **Aucun garde-fou affaibli** : `CONNUS` vide, aucun test affaibli, aucun `xfail` sur un test qui passait. Un test qui disparaît
   (Pyodide, en P5) est justifié dans `suivi.md`.
5. **Le moteur n'est plus public.**
   - En production, aucun fichier `.py` ni `moteur/` n'est servi (T4).
   - Aucun repli Pyodide (M11).
   - Ce qui a déjà été publié reste dans l'historique public jusqu'au passage en privé (audit § 0).
6. **Aucune donnée d'examen sur le serveur ni dans le dépôt** (M9).
7. **Ce que le site dit des données est exact** (T14) : rien n'est promis qui ne soit fait, et les services tiers sont nommés.
8. **Simple à entretenir pour une personne seule** : une seule machine, une seule application et un seul script de reconstruction.
   Aucune étape qu'il faudrait refaire à la main de mémoire.

---

## 2. Décisions de l'enseignant (06.11.2026)

| # | Décision | Portée |
|---|---|---|
| M1 | **VPS Lite 1 vCPU / 2 Go** chez Infomaniak : 2.70 CHF HT par mois, payé à l'année. On monte si les mesures de P2 dépassent les seuils du § 6 ; on ne peut jamais redescendre. Avant la commande, il faut vérifier que l'offre comprend bien une IPv4 (non écrit sur le site, audit § 10). | P2 |
| M2 | **Montage A** : le site et le moteur sont sur le VPS, à la même origine (`https://samimir.ch/api/…`, pas de CORS). GitHub privé ne sert que de dépôt. | P3 à P6 |
| M3 | **Mise en ligne par une GitHub Action (SSH) au push sur `main`** (T12), avec : un utilisateur de déploiement restreint (commande forcée, sans `sudo` général) ; un environnement « production » limité à `main` ; des actions figées par empreinte (SHA). Elle n'attend pas les tests GitHub. Le même script reste lançable depuis l'ordinateur de l'enseignant, en secours. Une clé volée vaut autant qu'un push sur `main` (T12) : la double authentification de GitHub est la première protection. | P6 et ensuite |
| M4 | **Tests GitHub en privé** : le job Python seul au push sur `main`, sauf si seul `docs/` change ; le job Pages à la demande (`workflow_dispatch`) ; une limite de dépense à 0 USD. La suite complète locale avant chaque commit reste la vraie protection (CLAUDE.md). | P6 |
| M5 | **En deux temps.** samimir.ch reste sur GitHub Pages jusqu'à ce que le site sur le VPS soit opérationnel. Ensuite seulement, on désactive Pages et le dépôt passe en privé. Jamais dans l'autre ordre : le site tomberait. | P6 |
| M6 | **Messages à l'élève au vouvoiement** (R12), avec le texte exact du § 5.1, relus à l'écran. Le § 5.1 liste ses écarts avec les textes de l'audit § 6. | P3 |
| M7 | **Aperçu à chaque frappe après 150 ms**, comme aujourd'hui. | P3 |
| M8 | **Aucun compte.** Le journal d'accès ne contient ni le corps des requêtes ni les saisies ; les adresses IP sont gardées 7 jours (T14). | tout le chantier |
| M9 | **La règle des examens est hors de ce chantier** (tranchée au chantier S'entraîner). Seule contrainte ici : aucune donnée d'examen ni liste d'exclusion ne va sur le serveur ni dans le dépôt. | tout le chantier |
| M10 | **Le simplexe reste en JS**, donc public : à l'examen, ce sont des problèmes, pas des exercices tirés. | — |
| M11 | **Pyodide est supprimé à la fin, sans repli** : un repli republierait le moteur. | P5 |

---

## 3. Décisions techniques

### T1. Contrat de l'API

- `POST /api/<outil>/<fn>`. Le corps est l'argument JSON que la page passe aujourd'hui à `appelPy` : une chaîne, ou un tableau pour
  `[entrée, filière]` et `[niveau, filière]`. `Content-Type: application/json`.
- **La réponse 200** est la chaîne brute de `<module>.<fn>_json(arg)`, avec `Content-Type: application/json; charset=utf-8` et
  `Cache-Control: no-store`. Le serveur appelle `fn(*arg)` si l'argument est un tableau, et `fn(arg)` sinon, comme
  `worker-pyodide.js`.
- `GET` (et `HEAD`) `/api/sante` renvoie `{"ok": true, "version": "<commit>"}` si tout va bien, et un code **503** sinon. Il vérifie :
  - un vrai calcul : `resoudre_json` du 2e degré sur `x^2-1=0`, avec une sortie `ok` ;
  - l'état de la machine, lu dans un petit fichier écrit chaque heure par un minuteur root : le certificat expire dans plus de
    14 jours, et le disque est plein à moins de 90 %.

  La version permet à la mise en ligne de vérifier que la nouvelle version est bien en service (T12).
- **Les fonctions « anciennes »** du manifeste sont encore acceptées, pour les pages restées en cache, comme aujourd'hui.
- **La page ne lit jamais le corps d'une réponse d'erreur.** nginx renvoie du HTML pour certains codes ; la page ne regarde que le
  code HTTP et le traduit ainsi (messages exacts au § 5.1) :

  | Réponse | Cause probable | Code côté page (T6) | Message |
  |---|---|---|---|
  | 200, JSON lisible | — | — | Le corrigé ou l'aperçu, comme aujourd'hui |
  | 200, JSON illisible | Portail Wi-Fi ou proxy de l'école | `reseau` | Serveur injoignable |
  | Pas de réponse (`fetch` rejeté) | Réseau coupé, VPS arrêté | `reseau` | Serveur injoignable |
  | 400, 404, 405 | Page plus ancienne ou plus récente que le serveur | `page` | Page à recharger |
  | 413 | Saisie de plus de 4 Ko | `trop_long` | Saisie trop longue |
  | 429 | Limite de requêtes (T5 : `limit_req_status 429` et `limit_conn_status 429`) | `trop` | Trop de calculs |
  | 500 | Exception du moteur | `serveur` | Erreur du serveur |
  | 502, 503, 504 | Application en redémarrage ou arrêtée, processus tué au-delà du délai | `serveur` | Erreur du serveur |
  | Délai de la page dépassé (`AbortController`) | Calcul long | `delai` | Trop long, comme aujourd'hui |

### T2. Règle d'architecture A10 (ajoutée à `docs/architecture.md` en P1)

> **A10. Le serveur ne connaît aucun outil par son nom.** `serveur/app.py` n'appelle que des fonctions `<fn>_json` listées dans
> `moteur/manifeste.json`, sur le module que le manifeste nomme ; il n'importe aucun moteur d'outil directement et ne transforme pas
> la chaîne renvoyée.
> Garde-fou : `test_imports` (le serveur n'a d'arête que vers la bibliothèque standard), `test_serveur` (liste blanche, chaîne brute).

Tous les outils tournent dans un même processus, servi à tous les élèves. Cela marche grâce à A8 (aucun nom de module en double,
`test_noms_de_modules_uniques`). Pour que ni un outil ni un élève ne change la sortie d'un autre, `test_serveur` rejoue le corpus
dans deux ordres mélangés entre outils et compare à l'octet (T8).

### T3. Serveur d'application

- **Système : Ubuntu 24.04 LTS**, s'il est proposé par Infomaniak, ce que leur liste d'OS indique. Son Python 3.12 système reçoit
  les correctifs de sécurité par `unattended-upgrades`. Debian n'a pas de Python 3.12 (Debian 12 : 3.11 ; Debian 13 : 3.13), et un
  Python installé par `uv` échapperait aux mises à jour automatiques.
- **Environnement virtuel aux versions figées** : SymPy 1.13.3, mpmath 1.3.0, gunicorn à une version écrite. Il est créé par le
  script de reconstruction (T11) ; jamais d'installation pendant une mise en ligne.
- **gunicorn, en processus synchrones** : une requête à la fois par processus (audit § 3).
  - Un calcul SymPy ne s'interrompt pas depuis un fil.
  - Il existe un état de module, toléré par A7 (`exp_log._DECIMAUX`).
  - `random` sert aux exercices.
- **3 processus de travail** sur 1 vCPU (environ 85 Mo chacun) : un calcul long n'empêche pas les aperçus des autres élèves. Le
  nombre est à ajuster en P2 d'après la mesure.
- **Délais.** Le serveur attend toujours plus longtemps que la page, pour que l'élève lise « trop long » et non « erreur ».
  - Le plus grand délai d'une page est de **45 s** (Étude complète, `delaiCalcul: 45000`) ; les autres pages attendent 30 s.
  - gunicorn tue un processus au-delà de **50 s** (`--timeout 50`) et le remplace ; nginx attend **55 s** (`proxy_read_timeout`).
  - Un test vérifie que le délai de gunicorn dépasse le plus grand `delaiCalcul` des pages, lu dans les pages.
  - Quand la page a abandonné, le calcul continue côté serveur jusqu'à 50 s au plus.
- **Recyclage** : un processus est remplacé après N requêtes (`max_requests`, avec une variation de 10 %), car le cache de SymPy
  grossit. N est fixé en P2 d'après la croissance de la mémoire mesurée : au moins 5 000, pour ne pas recycler toutes les 30 s
  avec un cache froid.
- **Mémoire bornée** : systemd `MemoryMax=1200M` pour l'application entière, et `Restart=always`.
- **Chargement au démarrage** (`--preload`) de tous les modules du manifeste et de SymPy, **modules importés paresseusement compris**
  (`exp_log_m`). Le premier appel n'est donc pas froid, et un module qui ne s'importe pas empêche le démarrage au lieu de tomber sur
  un élève.
- **Avec `--preload`, un simple rechargement (HUP) ne recharge pas le code** : les nouveaux processus partent de l'ancien import. Une
  mise en ligne fait donc un **`systemctl restart moteur`** (T12). La coupure, d'environ 1 à 2 s, est à mesurer en P2. Un élève qui
  calcule à cet instant lit « Erreur du serveur » (§ 5.1), jamais un faux résultat. La procédure sans coupure de gunicorn (USR2)
  n'est essayée en P2 que si la coupure dépasse 3 s.
- **Application sans framework** : la bibliothèque standard et le protocole WSGI, environ 80 lignes avec les codes d'erreur et
  `/api/sante`.

### T4. nginx et fichiers servis

- Il fait le HTTPS (Let's Encrypt, T16), avec une redirection HTTP → HTTPS. `www.samimir.ch` redirige vers `samimir.ch`.
- Il compresse en gzip les réponses JSON, HTML, JS et CSS.
- **En-têtes** :
  - `X-Content-Type-Options: nosniff`, `Referrer-Policy: no-referrer` et `server_tokens off` ;
  - HSTS après la bascule seulement, d'abord sur une courte durée (1 jour), puis 6 mois une fois stable, sans « preload ».
- **Aucun moteur n'est servi en production** (à partir de P6). Le dossier web est construit par le script de mise en ligne à partir
  de **`git ls-files`** du commit, et non du disque : ainsi, ni `__pycache__` ni un fichier non suivi ne partent. Il ne garde que les
  extensions `.html`, `.css` et `.js`, dans `index.html`, les dossiers des pages du registre et `commun/`.
  - Les fichiers Python vont dans le dossier de l'application, hors du dossier web.
  - Un test vérifie que la liste publique ne contient aucun `.py`, `.pyc`, `.md`, `.json` ni `__pycache__`, et rien de `moteur/`,
    `docs/`, `tests/`, `serveur/` ni `.github/`.
  - nginx refuse quand même `*.py` et `*.pyc` (code 404), comme deuxième barrière.
- **Site d'essai** (P3 à P5, T10) : tant qu'il reste des outils sur Pyodide, `essai.samimir.ch` sert aussi `moteur/`, les `.py` et
  les roues, comme GitHub Pages aujourd'hui. Le moteur y est donc aussi public qu'aujourd'hui, ni plus ni moins. La liste blanche
  stricte vaut pour la production.
- **Cache du navigateur** : `Cache-Control: no-cache` (revalidation par ETag) pour le HTML, le JS et le CSS. Le site public fait
  287 Ko, donc revalider coûte peu. Les réponses de l'API ont `no-store`.
- **Versions décalées** (une page encore en cache face à un serveur plus récent) : SOC-22 (« Affichage incomplet »), les fonctions
  « anciennes » (T1) et le message « page à recharger » pour un 404 (T1) restent les garde-fous.

### T5. Limite de requêtes

- **Pas de compte : la seule clé est l'IP**, et une classe derrière le NAT de l'école partage souvent **une seule IP**. Mesure de
  l'audit : 30 élèves font environ 47 requêtes par seconde, dont 40 d'aperçus.
- nginx, sur `/api/` : `limit_req` par IP, **60 requêtes par seconde avec une rafale de 200** (`nodelay`), au-delà réponse **429**
  (`limit_req_status 429`).
- **Calculs simultanés par IP** (`limit_conn`, `limit_conn_status 429`), sur `resoudre`, `exercice` et `controle` (pas sur `fenetre`,
  qui ne dure que 1 à 2 ms) : **au moins 40**, pour qu'une classe entière qui clique en même temps ne reçoive aucune réponse 429. La
  valeur est fixée en P2 par la rafale de 30 « Calculer » mesurée **depuis une seule IP**.
- Les refus sont notés au niveau `info` (`limit_req_log_level`, `limit_conn_log_level`), en dessous du niveau du journal d'erreurs
  (T14) : ils ne remplissent pas le journal.
- **Risque accepté tant qu'il n'y a pas de comptes** : quelqu'un qui enverrait sans arrêt des saisies très lentes peut occuper les
  3 processus, 50 s au plus par requête. Les délais, le recyclage et la mémoire bornée (T3) empêchent que cela dure ou fasse tomber
  la machine ; un accès réservé plus tard le réglera.

### T6. Client `MoteurServeur` (`commun/`)

- **La même interface que `MoteurPython`**, pour que `outil.js`, `graphique.js` et les greffons changent le moins possible :
  - `demarrer()` : `GET /api/sante` (10 s au plus) ; un échec rejette, et `outil.js` affiche le message d'ouverture existant ;
  - `appelPy(fn, arg, délai, options)` : `fetch` en `POST`, `AbortController` pour le délai (rejet `Error("delai")`, comme
    aujourd'hui). Un **4e paramètre facultatif `{ signal }`** permet à l'appelant d'annuler **sa** demande (T7). Il n'y a jamais
    d'annulation par nom de fonction : la frappe ne doit pas annuler l'aperçu de l'exercice tiré ;
  - `relancer()` : vide les demandes en cours, sans rien d'autre à relancer ;
  - `sympyOK = true` et `sympyPret` résolu dès le départ ; `noterActivite()` et `hater()` ne font rien ;
  - `worker` vaut une valeur vraie une fois démarré, puisque `outil.js` teste `moteur.worker`. On le renomme en P5.
- **Erreurs** : `appelPy` rejette avec une `Error` dont le message est un des codes de T1 (`delai`, `reseau`, `page`, `trop_long`,
  `trop`, `serveur`). `outil.js` fait correspondre chaque code à un message du § 5.1. Une annulation demandée par l'appelant rejette
  avec `annule`, qui n'affiche rien.
- Annuler une requête évite seulement l'attente et l'affichage côté page. Le processus du serveur, synchrone, finit quand même le
  calcul (un aperçu dure moins de 1 ms).
- **Pendant la migration (P3, P4)** : une clé `"execution": "serveur"` par outil dans le manifeste choisit le client.
  `test_manifeste` la vérifie (seule valeur admise : `"serveur"` ; absente, c'est Pyodide). Elle disparaît en P5.
- **Plus de manifeste côté page après P5** : le serveur est la liste blanche (T1). Le manifeste n'est plus publié, mais il reste dans
  le dépôt comme liste des modules et des fichiers à déployer (T12) ; `test_manifeste` garde ses contrôles « complet et minimal ».

### T7. Réponses dans le désordre

Avec le Worker, les réponses arrivaient dans l'ordre des demandes (une seule file). Avec le réseau, **une réponse plus ancienne peut
arriver après une plus récente**. Règle : seule la réponse à la dernière demande de chaque sorte est affichée ; les autres sont
annulées ou ignorées.

| Appel | Aujourd'hui | À faire |
|---|---|---|
| `apercu` de la frappe (`outil.js:109`) | Garde par numéro (`seqAp`) | Garder le numéro ; **annuler** la requête précédente par son propre `signal` (T6) dès une nouvelle frappe. Une requête annulée n'affiche rien. |
| `resoudre` (`outil.js:160`) | Garde par numéro (`numCalcul`) | Garder. Côté page, le second appel après `besoin_sympy` disparaît en P5 (T9). |
| `controle`, greffon `apres` (ED) | Garde `actuel()` | Garder. |
| `exercice` puis son `apercu` (`outil.js:349`) | **Aucune garde.** Deux clics rapides peuvent afficher l'énoncé du premier tirage alors que `exoCourant` vaut le second. Pendant « Chargement… », « Afficher le corrigé » est visible alors que `exoCourant` vaut encore l'**exercice précédent** : l'élève obtiendrait le corrigé d'un autre exercice que celui qui s'affiche ensuite. | **Garde par numéro de tirage** : seul le dernier tirage écrit l'énoncé et `exoCourant`, tous deux du même tirage. **Dès le début d'un tirage**, `exoCourant = null` et « Afficher le corrigé » est désactivé ; on le réactive avec l'énoncé. Un changement de filière (`changerFiliere`) incrémente aussi le numéro. |
| `fenetre`, zoom du graphique (`graphique.js:190`) | Un délai de 150 ms, pas de garde | **Garde par numéro** : ni les segments ni le message d'échec d'une fenêtre périmée ne sont pris en compte (`message.hidden` compris), pour ne pas afficher l'échec sur un tracé à jour. |

**Message « trop long »** (`outil.js:180`) : aujourd'hui, `majEtat()` l'écrase aussitôt (`outil.js:184`), et il dit « relancé »,
ce qui serait faux avec le serveur. Il est remplacé par le texte du § 5.1 et reste affiché jusqu'à la saisie ou au calcul suivant.
Un test lit `#etat`.

**Test dédié** (P3, puis chaque outil concerné en P4) : le serveur de test des pages retarde certaines réponses (paramètre de test,
absent de l'application de production) pour forcer l'inversion.
- **Aperçu** : taper `ln(x` puis `ln(x)`, la réponse de `ln(x` arrivant en dernier. L'aperçu final est celui de `ln(x)`, sans
  message rouge.
- **Calcul** : deux calculs, le premier arrivant en dernier. Les cartes sont celles du second.
- **Exercice** : deux clics, le premier arrivant en dernier. L'énoncé affiché et le corrigé ouvert sont du même exercice. Le bouton
  « Afficher le corrigé » est désactivé pendant le tirage.
- **Changement de filière pendant un tirage** (EL) : aucun énoncé de l'ancienne filière n'est affiché.
- **Zoom** : deux zooms, le premier arrivant en dernier. Les segments dessinés sont ceux du second, et un échec périmé n'affiche pas
  de message.

Le garde-fou réseau de `navigateur.py` (F6) reste.

### T8. Exercices tirés (Factorisation, EL) et dump par HTTP

- `exercice_json` tire au hasard (`random`). Le dump par HTTP ne peut pas fixer la graine dans un autre processus, et on n'ajoute
  **aucune porte de test dans l'application de production**.
- Donc :
  - `dump_sorties.py --serveur <URL>` compare par HTTP `resoudre`, `apercu` et `controle` (tout le corpus) ;
  - `test_serveur.py` appelle l'application WSGI **dans le même processus**, avec `random.seed` fixé, et compare `exercice` à
    l'octet avec l'appel direct.

  C'est le même code de transport que pour les autres fonctions.
- `fenetre` est vérifiée de même dans `test_serveur.py`, sur quelques fenêtres.
- `test_serveur.py` rejoue le corpus réduit **dans deux ordres mélangés entre outils**, dans un seul processus, et compare (T2).

### T9. Rien ne change dans les moteurs

- Aucun fichier de moteur ni d'adaptateur n'est modifié dans ce chantier. Les instantanés (`test_instantanes*.py`) restent
  identiques sans être régénérés.
- **`besoin_sympy` reste dans les sorties** (`ensemble_def.py`, `resoudre_ed.py`, `sortie.py`). Seul le code de la page qui le
  traite est retiré en P5 : sur le serveur, SymPy est toujours chargé, donc ce champ n'y vaut jamais vrai.

### T10. Ordre de mise en ligne

- **La branche `moteur-serveur` n'est fusionnée dans `main` qu'en P6.** Une page passée au serveur, publiée par GitHub Pages,
  appellerait un `/api/` qui n'existe pas.
- **Pendant P3 à P5** :
  - on développe et on teste contre le serveur de test local ;
  - on met en ligne **à la main** (secours de T12) sur un site d'essai du VPS, **`essai.samimir.ch`** : sous-domaine, certificat à
    lui, service `moteur-essai` à lui. Il sert à l'essai sur iPhone ;
  - samimir.ch reste sur GitHub Pages (M5) ; le VPS n'a pas encore de production.
- **Juste avant la fusion de P6**, GitHub Pages est **gelé** : sa source passe de `main` à une branche `pages-gelee`, une copie de
  `main` d'avant la fusion, avec Pyodide. La fusion ne republie donc rien sur Pages. Tant que Pages n'est pas désactivé, un retour
  du DNS vers GitHub ramène ce site gelé, qui marche.
- `main` peut recevoir d'autres commits pendant le chantier, par exemple dans `docs/` : la fusion de P6 les reprend.

### T11. Sécurité de base du VPS (dans le script de reconstruction)

`serveur/reconstruire.sh` doit pouvoir être relancé sans dégât. On le lance en root sur un VPS neuf (Ubuntu 24.04 LTS, T3), puis
sans risque à chaque changement de configuration. Il fait :

1. **Utilisateurs.**
   - `admin` : l'enseignant ; `sudo` **avec mot de passe** ; clé SSH seulement pour se connecter.
   - `deploiement` : la mise en ligne. Son shell reste `/bin/sh`, car sshd lance la commande forcée par le shell de l'utilisateur ;
     la restriction vient de la clé (point 2).
   - `moteur` : il fait tourner l'application ; aucune connexion, et il ne peut pas écrire dans le code.
2. **SSH par clé uniquement.**
   - `PasswordAuthentication no`, `KbdInteractiveAuthentication no`, **`PermitRootLogin no`**, `AllowUsers admin deploiement`.
   - **Les clés autorisées appartiennent à root** (`AuthorizedKeysFile /etc/ssh/cles/%u`) : ni `deploiement` ni le code qu'il dépose
     ne peuvent les réécrire pour lever la commande forcée.
   - La clé de `deploiement` porte `command="/usr/local/bin/recevoir-version",restrict` (ni terminal, ni redirection de port).
     Le script **ignore `SSH_ORIGINAL_COMMAND`** et ne lit que l'archive sur l'entrée standard.
   - **Pour ne pas s'enfermer dehors** : le script ne ferme la connexion root par SSH et par mot de passe **qu'après avoir vérifié**
     qu'une connexion `admin` par clé a réussi (deux lancements, guidés par `INSTALLATION.md`).
3. **Pare-feu** (`ufw`) : tout est refusé en entrée **sauf 22, 80 et 443** (IPv4 et IPv6) ; tout est permis en sortie pour le
   système (mises à jour). L'application, elle, n'a aucune sortie réseau (point 6).
4. **Mises à jour de sécurité automatiques** (`unattended-upgrades`, sécurité Ubuntu, Python système compris), avec un redémarrage
   automatique si un noyau l'exige, **à 3 h**, hors des heures de cours.
5. **Paquets** : Python 3.12 système, environnement virtuel aux versions figées (T3), nginx, certbot (renouvellement par minuteur
   systemd), logrotate et journald bornés (T14), et le minuteur root de l'état de la machine (T1).
6. **Service systemd `moteur`** : `User=moteur`, `NoNewPrivileges=yes`, `ProtectSystem=strict`, `ProtectHome=yes`, `PrivateTmp=yes`,
   `MemoryMax=1200M` et `Restart=always`. **`IPAddressDeny=any` et `IPAddressAllow=localhost`** : même un code malveillant déposé par
   une mise en ligne ne peut rien envoyer au-dehors. Il écoute sur `127.0.0.1` seulement ; seul nginx est exposé.
7. **Vérification finale.** Le script affiche :
   - l'état du pare-feu ;
   - les ports ouverts (`ss -tlnp` : seuls nginx sur 80 et 443 et SSH sur 22 sont joignables de l'extérieur) ;
   - la configuration SSH effective (`sshd -T`) ;
   - `/api/sante`.

Le VPS Lite n'a pas de snapshot : **ce script et le dépôt suffisent à refaire la machine** en moins d'une heure (à mesurer en P2). Il
n'y a aucune donnée à sauvegarder, puisqu'il n'y a ni compte ni stockage. Après une reconstruction, la **clé d'hôte change** : il
faut mettre à jour le secret `known_hosts` de l'Action et les ordinateurs de l'enseignant (procédure dans `INSTALLATION.md`). Le pas
à pas pour l'enseignant est dans `serveur/INSTALLATION.md` : commande du VPS, première connexion, lancement du script, DNS,
certificats, surveillance, dépannage depuis le téléphone (§ 5.2).

### T12. Mise en ligne, mise en ligne ratée, retour en arrière

- **Sur le VPS**, `/srv/samimir/versions/<date>-<commit>/` contient le dossier web et le dossier de l'application. `courante` est un
  lien vers la version en service. On garde **les 5 dernières** versions.
- **La GitHub Action** (`.github/workflows/mise-en-ligne.yml`) se déclenche au push sur `main`, sauf si seul `docs/**` change. Elle
  tourne dans l'environnement « production » (secrets accessibles depuis `main` seulement), avec des actions figées par SHA et
  **`concurrency`** : une seule mise en ligne à la fois, et la plus récente gagne.
  1. Elle construit l'archive (liste blanche de T4, plus les fichiers du manifeste et `serveur/app.py` pour l'application).
  2. Elle y joint `verif.json` : les sorties de 20 entrées du corpus réduit, calculées par le commit lui-même. Elle installe donc
     les versions figées, environ 1 minute.
  3. Elle l'envoie par SSH à l'utilisateur `deploiement`. L'empreinte du serveur est vérifiée : `known_hosts` est fixé dans les
     secrets.
- **La réception** (`recevoir-version`, avec une seule règle `sudo` sans mot de passe, pour lancer la bascule) :
  1. elle prend un verrou (`flock`) : deux réceptions ne se croisent jamais ;
  2. elle décompresse avec `tarfile` et `filter="data"`, ce qui refuse les chemins `../`, les liens et les fichiers spéciaux. Elle
     écrit dans un nouveau dossier seulement ;
  3. elle lance la bascule **détachée de la connexion SSH** (`systemd-run`) : une connexion coupée ne laisse jamais une bascule à
     moitié faite.
- **La bascule** (service ponctuel) :
  1. elle vérifie **dans le même bac à sable que le service** (`User=moteur`, sans réseau) que tous les modules du manifeste
     s'importent, et que les 20 entrées donnent exactement `verif.json` ;
  2. elle bascule `courante` **atomiquement** (nouveau lien puis `mv -T`) et redémarre le service (T3, pas de HUP) ;
  3. elle vérifie `/api/sante`, version comprise.
- **Mise en ligne ratée.** Si une vérification échoue avant la bascule, rien ne change. Si elle échoue après, **retour automatique**
  à la version précédente, suivi de la même vérification. L'Action échoue alors visiblement, et GitHub envoie un courriel. Le site ne
  reste jamais sur une version qui ne répond pas.
- **Retour en arrière à la main, sans GitHub** :
  - depuis l'ordinateur de l'enseignant, `serveur/retour.sh` (SSH en `admin`, avec sa propre clé) ;
  - ou, sur le VPS, `sudo samimir-retour` ;
  - au choix : rétablir la version précédente, ou une version nommée parmi les 5 gardées.

  Il bascule le lien, redémarre le service et vérifie `/api/sante`. Il marche même si GitHub est en panne, ou si le quota est épuisé.
- **Secours** : `serveur/mettre-en-ligne.sh` fait depuis l'ordinateur de l'enseignant ce que fait l'Action (même archive tirée de
  `git ls-files`, même `verif.json`). Il passe par la clé `admin` et refuse si l'arbre n'est pas propre. C'est aussi lui qui met en
  ligne `essai.samimir.ch` pendant le chantier (T10).
- **Ce que permet la clé de déploiement si elle est volée** : autant qu'**un push sur `main`**. Elle peut mettre en ligne n'importe
  quel code, qui tourne alors comme `moteur`, et des pages modifiées.

  Elle ne donne ni shell, ni `sudo`, ni accès aux clés SSH, et le code déposé n'a **aucune sortie réseau** (T11, point 6). Il ne peut
  donc pas envoyer au-dehors des saisies ou des IP. Une page modifiée pourrait en revanche le faire depuis le navigateur des élèves,
  comme avec un push sur `main` aujourd'hui.

  Les protections sont donc celles du compte GitHub : double authentification, environnement limité à `main`, actions figées par
  SHA. Si le compte est compromis, on remplace la clé (`reconstruire.sh` sait le faire) et on fait un retour à une version sûre.

### T13. Surveillance

- **Une alerte externe** : un service de surveillance gratuit (proposé : UptimeRobot, compte à créer par l'enseignant) interroge
  `https://samimir.ch/api/sante` **toutes les 5 minutes**. `/api/sante` fait un vrai calcul et vérifie le certificat et le disque
  (T1) : l'alerte couvre donc le moteur, le certificat (14 jours avant l'expiration) et le disque, pas seulement la machine. La page
  d'accueil est aussi surveillée.
- **Alerte par courriel et par notification sur le téléphone** (application du service) après **2 échecs de suite**, environ
  10 minutes. Un courriel au retour.
- Let's Encrypt n'envoie plus de courriels d'expiration depuis 2025 : on ne compte que sur `/api/sante` pour le certificat.
- But : que l'enseignant sache qu'il y a une panne **avant ses cours**. La procédure en cas d'alerte est au § 5.2.

### T14. Données des élèves et journaux

**Sur le VPS.**
- **Journal d'accès nginx** : un format à nous (`log_format`), avec la date, l'IP, la méthode, **`$uri`** (le chemin **sans** la
  requête : pas de `?f=<saisie>`), le code et la durée. **Ni le corps** (la saisie), ni `Referer`, ni l'agent utilisateur.
- **Journal d'erreurs nginx** au niveau `crit` : les lignes ordinaires, qui citent la requête et le `Referer`, n'y sont pas écrites.
  Les refus de T5 sont au niveau `info`, donc pas écrits non plus.
- **Journal de l'application** : le type d'exception, l'outil, la fonction et les cadres de la pile (fichier, ligne, fonction),
  **jamais le message de l'exception**, qui peut contenir la saisie (par exemple `SympifyError`), **ni la saisie**. Une erreur
  reproductible se retrouve par le corpus et les tests. gunicorn n'écrit pas de journal d'accès.
- **Durée : 7 jours au plus partout.** logrotate quotidien avec `rotate 6` (le jour courant plus 6), pour nginx et l'application, au
  lieu des 14 jours de la configuration par défaut d'Ubuntu ; journald avec `MaxRetentionSec=7day`.
- Les journaux ne quittent pas le VPS, et la surveillance (T13) ne voit que `/api/sante`.

**Dans les pages** (vérifié le 06.11.2026) :
- **GoatCounter** est sur les 9 pages, pas seulement l'accueil. Son script envoie le chemin **avec la requête** : un lien
  `?f=<saisie>` part donc chez GoatCounter. Décidé (§ 9, question 1) : en P5, ne lui envoyer que le chemin, avec le réglage `path` de
  GoatCounter. Le test de la « balise GoatCounter exacte » est mis à jour exprès.
- **KaTeX** (jsDelivr, sur chaque page) et **Google Fonts** (accueil) font partir l'IP de l'élève chez ces services. Décidé (§ 9,
  question 1) : en P5, héberger KaTeX et ses polices sur le VPS (la copie `tests/pages/katex_local.py` existe déjà), et la police de
  l'accueil aussi.
- **`localStorage`** garde deux préférences dans le navigateur : la variante de résolution choisie et la filière de l'accueil
  (`samimir-track`). Rien n'est envoyé.
- **Pas de ligne « Données » pour l'instant** (enseignant, 06.11.2026 ; § 9, question 4). Un texte possible est gardé de côté au
  § 5.1, sans être affiché. Les protections de T14 s'appliquent quand même.

### T15. Tests GitHub (M4)

- `tests.yml` : `on: push` limité à `main` avec `paths-ignore: ["docs/**"]`, plus `workflow_dispatch`. Le job Python tourne au push ;
  le job Pages ne tourne qu'à la demande (`if: github.event_name == 'workflow_dispatch'`).
- Limite de dépense à 0 USD (réglage du compte, par l'enseignant).
- L'Action de mise en ligne (T12) est indépendante : elle ne dépend pas des tests GitHub.
- Ce changement est fait **en P6**, avec le passage en privé. Avant, le dépôt est public et les minutes sont gratuites.

### T16. DNS, certificats et bascule (M5)

Dans la zone samimir.ch, chez Infomaniak :
1. **P2** : `essai.samimir.ch` reçoit A et AAAA vers le VPS. Son certificat s'obtient tout de suite par le défi HTTP de certbot.
2. **Avant la bascule, le certificat de `samimir.ch` et `www`.** Le défi HTTP échouerait tant que le DNS pointe vers GitHub. Le
   **premier** certificat s'obtient donc par le défi DNS **à la main** : certbot donne un enregistrement TXT, que l'enseignant ajoute
   dans le Manager d'Infomaniak, guidé par `INSTALLATION.md`. Aucun jeton d'accès au DNS ne reste sur le VPS. Juste après la bascule,
   on le remplace par un certificat obtenu par le défi HTTP, qui se renouvelle seul.
3. **La veille** : le TTL des enregistrements de `samimir.ch` et `www` passe à 300 s.
4. **Le jour de la bascule** :
   1. on gèle GitHub Pages (T10) ;
   2. on fusionne dans `main`, et l'Action met la production en ligne sur le VPS ;
   3. on vérifie à l'adresse du VPS (`curl --resolve samimir.ch:443:<IP>`) ;
   4. on remplace les 4 A de GitHub par l'A et l'AAAA du VPS ; `www` reçoit un CNAME vers `samimir.ch` (redirection par nginx) ;
   5. on remplace le certificat (point 2).
5. On vérifie sur iPhone, après un rechargement sans cache.
6. **Seulement ensuite** : GitHub Pages est désactivé, `CNAME`, `_config.yml` et la branche `pages-gelee` sont retirés, et le dépôt
   passe en privé (M5).

On revient en arrière (DNS vers GitHub, site gelé avec Pyodide) tant que Pages n'est pas désactivé.

### T17. Ce qui reste inconnu (vérifié en P2 avant de s'y fier)

- L'IPv4 du VPS Lite, à vérifier avant la commande (M1).
- Ubuntu 24.04 au catalogue du VPS Lite.
- La vitesse d'un vCPU, la coupure au redémarrage (T3), la croissance de la mémoire (recyclage), la rafale depuis une seule IP (T5).
- L'aller-retour réseau depuis l'école.

---

## 4. Tests (ce que chaque nouveauté ajoute)

- **`tests/python/test_serveur.py`** (P1), l'application WSGI appelée en processus, sans réseau :
  - **à l'octet** avec l'appel direct, sur le corpus réduit de chaque outil, toutes fonctions et filières, `exercice` avec une graine
    (T8) et `fenetre` sur quelques fenêtres ;
  - **deux ordres mélangés entre outils** (T2, T8) ;
  - codes 400, 404, 405, 413 et 500 ; la réponse 500 ne contient pas la saisie ;
  - `/api/sante` en `GET` et en `HEAD`, avec le 503 quand l'état de la machine est mauvais ;
  - en-têtes (`Content-Type`, `no-store`) ;
  - fonctions « anciennes » acceptées ;
  - **A10** ;
  - le délai de gunicorn dépasse le plus grand `delaiCalcul` des pages (T3) ;
  - le journal de l'application ne contient ni la saisie ni le message de l'exception (T14).
- **`dump_sorties.py --serveur <URL>`** (P1), lancé à chaque partie contre le serveur local, puis en P2 contre le VPS :
  `diff -r --exclude=temps` code 0.
- **`test_imports`** : le serveur n'a d'arête que vers la bibliothèque standard (A10). **`test_manifeste`** : la clé `execution`
  (P3, P4), puis son absence (P5).
- **Liste blanche publique** (P1, T4) : l'archive est construite dans le test depuis `git ls-files` ; aucun `.py`, `.pyc`, `.md`,
  `.json`, `__pycache__` ni fichier des dossiers interdits.
- **`recevoir-version` et la bascule** (P2) : un test Python les lance sur un dossier temporaire. Il vérifie :
  - archive piégée (`../`, lien) refusée ;
  - `verif.json` différent : la bascule est refusée ;
  - santé en échec après la bascule : retour automatique ;
  - deux réceptions simultanées : le verrou en sérialise une.
- **Tests de pages** (P3, P4) : `navigateur.py` sert `/api/` avec la même application, dans un processus à part, et un paramètre de
  retard réservé aux tests (T7). Tests nouveaux :
  - serveur injoignable à l'ouverture ;
  - panne pendant un calcul ;
  - 404 (page à recharger), 429, 500 ;
  - 200 illisible (portail Wi-Fi) ;
  - délai (`window.__delaiCalcul`, comme SOC-13), avec `#etat` lu ;
  - **réponses dans le désordre** (T7 : aperçu, calcul, exercice, filière, zoom).

  Pour chaque outil passé au serveur : références de pages identiques, `test_largeurs` de 320 à 1100 px.
- **Tests remplacés en P5** (justifiés dans `suivi.md`, section des tests disparus) :
  - `test_pyodide_local.py` et `test_roues.py` disparaissent ;
  - `test_t31_libelle_pendant_le_chargement_de_sympy` et `test_t40_l_apercu_ne_attend_pas_sympy` (SOC-21) sont remplacés par les
    tests d'ouverture et de panne ;
  - `test_soc13_*` restent, réécrits pour le serveur de test.
- **Scripts du VPS** (P2) : `reconstruire.sh` est relu et essayé sur le VPS réel, avec sa vérification finale (T11, point 7).

---

## 5. Exemple rédigé : ce que voient l'élève et l'enseignant

### 5.1 L'élève (texte exact, au vouvoiement)

| Situation | `#etat` | Résultat ou aperçu |
|---|---|---|
| Ouverture, serveur joignable | « Chargement du moteur de calcul… » (texte inchangé, moins d'une seconde), puis « Prêt. » | Bouton « Calculer » actif. |
| Ouverture, serveur injoignable | « **Impossible de charger l'outil de calcul.** Vérifiez votre connexion internet, puis rechargez la page. » (texte inchangé, `outil.js:98`) | Bouton désactivé. |
| `reseau` : panne pendant un calcul (réseau coupé, VPS arrêté, portail Wi-Fi) | « Prêt. » | Carte d'erreur : « Le serveur de calcul ne répond pas. Vérifiez votre connexion internet, puis réessayez. » |
| `serveur` : erreur du serveur (500, 502, 503, 504) | « Prêt. » | Carte d'erreur : « Une erreur s'est produite sur le serveur de calcul : réessayez dans un instant. » |
| `page` : page plus ancienne ou plus récente que le serveur (400, 404, 405) | « Prêt. » | Carte d'erreur : « Cette page n'est plus à jour : rechargez-la. » |
| `delai` : calcul trop long (30 s ; 45 s pour l'Étude complète) | « Calcul interrompu : il a pris trop de temps. », gardé jusqu'à la saisie ou au calcul suivant (T7) | « Le calcul a pris trop de temps (plus de 30 s). Essayez une écriture plus simple. » (inchangé ; le nombre suit le délai de la page) |
| `trop` : trop de requêtes (429) | « Prêt. » | Carte d'erreur : « Trop de calculs en même temps : réessayez dans quelques secondes. » |
| `trop_long` : saisie de plus de 4 Ko (413) | « Prêt. » | Carte d'erreur : « Votre saisie est trop longue : écrivez-la plus simplement. » |
| Aperçu en échec (panne, 429, délai de 5 s) | inchangé | Rien de nouveau : le dernier aperçu valide reste estompé, sans message rouge (comportement actuel). |
| Exercice au hasard en échec | inchangé | « Erreur de chargement. » (inchangé) ; « Afficher le corrigé » reste désactivé (T7). |
| Zoom du graphique en échec | inchangé | Message existant : « La courbe n'a pas pu être recalculée pour cette fenêtre : le tracé affiché correspond à la dernière fenêtre réussie. » |

**Écarts avec les textes de l'audit § 6** (M6 portait sur eux) :
- le message de panne était « Le serveur de calcul ne répond pas : réessayez dans un instant. » ; il devient deux messages,
  `reseau` et `serveur`, parce que la cause et le conseil diffèrent ;
- trois messages sont nouveaux : `page`, `trop_long` et l'état « Calcul interrompu… » ;
- l'état « Calcul trop long : le calcul a été relancé. » disparaît, parce qu'il serait faux avec le serveur (T7).

**Texte gardé de côté, non affiché** (§ 9, question 4 : pas de ligne « Données » pour l'instant). S'il sert un jour, il suppose KaTeX
et les polices sur le VPS et GoatCounter sans la requête (§ 9, question 1), et il doit être revérifié contre T14 :

> Les calculs sont faits sur un serveur situé en Suisse. Vos saisies ne sont pas conservées : seule l'adresse IP de votre appareil
> est enregistrée dans les journaux du serveur, pour la sécurité du site, et elle est effacée après 7 jours. Le nombre de visites
> est compté par GoatCounter, sans cookie. Vos préférences (filière, méthode affichée) restent dans votre navigateur.

Aucun de ces textes ne contient « SymPy », « Pyodide », « Python » ni un code HTTP (SOC-15). Le détail va dans `console.error`.

### 5.2 L'enseignant

- **Mettre en ligne** : fusionner dans `main`, puis `git push`. L'Action met en ligne en environ 2 à 3 minutes, et l'onglet Actions
  montre le résultat. En cas d'échec, GitHub envoie un courriel et le site reste sur la version précédente.
- **Revenir en arrière** : `serveur/retour.sh` depuis le Mac ou le PC. Le script affiche la version rétablie et `/api/sante`.
  Environ 10 secondes, sans GitHub.
- **Alerte reçue (T13)**, par exemple avant un cours, depuis le téléphone :
  1. ouvrir `https://samimir.ch/api/sante` ;
  2. si cela ne répond pas, **redémarrer le VPS depuis l'application ou le Manager d'Infomaniak** : c'est faisable sur téléphone,
     sans SSH, et le service repart seul (`Restart=always`) ;
  3. depuis un ordinateur : `ssh admin@<vps>` puis `sudo systemctl restart moteur`, ou `serveur/retour.sh` si la panne suit une
     mise en ligne ;
  4. en dernier recours : `serveur/INSTALLATION.md`, section « Refaire le serveur ».

  Ces étapes sont écrites dans `INSTALLATION.md`.

---

## 6. Résultats attendus et seuils

| Mesure | Valeur connue au 06.11.2026 | Seuil proposé | Partie |
|---|---|---|---|
| Dump par HTTP identique au dump direct | 4 178 appels identiques sur 4 178 (prototype, audit) | 100 %, nombre remesuré au P0 | P1, P2 |
| Aperçu, aller-retour depuis l'école ou un téléphone en 4G (p95) | à mesurer | < 150 ms | P2 |
| `resoudre`, 30 élèves simulés sur le VPS (p95, hors réseau) | 9 ms (PC, 4 processus, audit) | < 300 ms | P2 |
| Rafale de 30 « Calculer » simultanés sur `x*e^x/(1-e^x)`, depuis une seule IP, le dernier | 3,1 s (PC à 6 cœurs, 4 processus, audit). Sur 1 vCPU, estimé à 16–21 s (30 × 0,35 s × 1,5 à 2), à mesurer | **< 20 s**, nettement sous les 30 s de la page : au-delà, un élève lirait « trop long » pour une saisie simple. Sinon, passer à 2 vCPU (M1). | P2 |
| Mémoire de l'application après la charge | environ 410 Mo (PC, 4 processus, audit) | < 800 Mo | P2 |
| Coupure au redémarrage d'une mise en ligne (T3) | à mesurer | < 3 s | P2 |
| Ouverture d'une page jusqu'à « Prêt. » | environ 5,5 s sur ordinateur avec Pyodide, davantage sur téléphone (`choix-techniques.md`, D13) | < 1 s sur iPhone | P3, P6 |
| Durée de la suite de pages | 342 s le 06.11.2026 avec Pyodide (PC, `PROCESSUS_PAGES=4`, suite d'avant le commit de l'audit) | à mesurer sans Pyodide, noté | P4, P5 |
| Reconstruction complète du VPS | à mesurer | < 1 h | P2 |

---

## 7. Découpage

| Partie | Contenu | Qui | Dépend de | À relire par l'enseignant |
|---|---|---|---|---|
| **P0** | Branche `moteur-serveur` depuis `main` à jour ; `suivi.md` et `journal.md` ; référence des tests ; dump de départ (`--processus 6` et `1`). | Claude Code (de nuit possible) | decisions.md validé | — |
| **P1** | `serveur/app.py` (T1, T3 sans gunicorn), `test_serveur.py`, `dump_sorties.py --serveur`, liste blanche publique, A10 dans `architecture.md` et `test_imports`. Rien ne change pour les pages. | Claude Code (de nuit) | P0 | `architecture.md` (A10) |
| **P2** | Claude Code écrit `serveur/reconstruire.sh`, `recevoir-version`, la bascule, `retour.sh`, `mettre-en-ligne.sh` et `INSTALLATION.md`, avec leurs tests. Puis l'enseignant, guidé pas à pas : vérification de l'IPv4 et d'Ubuntu 24.04, commande du VPS (M1), lancement du script en deux temps (T11), DNS et certificat de `essai.samimir.ch`, compte de surveillance (T13). Mesures du § 6 et de T17 sur le VPS. | Claude Code, puis l'enseignant | P1 | Rapport de mesures ; vérification finale du script (T11, point 7) |
| **P3** | `MoteurServeur` (T6), clé `execution`, codes et messages du § 5.1, gardes de T7, message « trop long » (T7), serveur de test dans `navigateur.py`, tests de panne et de désordre. **L'outil du 2e degré passe au serveur.** Mise en ligne sur `essai.samimir.ch`. | Claude Code (de nuit), puis l'enseignant sur iPhone | P1 ; P2 pour l'essai sur iPhone | Captures à 390 px des messages ; essai sur iPhone |
| **P4** | Les autres outils, un commit chacun : ED (`controle`), DV, LA, EC (`fenetre`, délai de 45 s), FA (`exercice`), EL (`exercice`, filières C et M). | Claude Code (de nuit) | P3 | Essai sur iPhone d'EC (zoom) et d'EL |
| **P5** | Retrait de Pyodide (M11) : `worker-pyodide.js`, `moteur-python.js`, `moteur/roues/`, `construire_roues.py`, `pyodide_local.py` et leurs tests, cache de la CI, `sympyAvant`, traitement de `besoin_sympy` côté page (T9), clé `execution`. KaTeX et polices sur le VPS, GoatCounter sans la requête (T14, § 9 question 1). Docs : `choix-techniques.md` (D1, D10, D13), `architecture.md`, `socle-commun.md` (SOC-13, SOC-14, SOC-21) ; CLAUDE.md seulement avec l'accord de l'enseignant. | Claude Code (de nuit) | P4 | Liste des tests disparus ; CLAUDE.md |
| **P6** | Bascule (T16) : Action de mise en ligne (T12) et secrets ; `tests.yml` (T15) ; premier certificat par le défi DNS ; gel de Pages ; fusion dans `main` ; DNS ; iPhone ; puis Pages désactivé, `CNAME`, `_config.yml` et `pages-gelee` retirés, dépôt privé, limite de dépense à 0. | L'enseignant guidé, Claude Code pour les fichiers | P2, P5 | Tout le jour de la bascule |

P1 et l'écriture des scripts de P2 peuvent se faire la même nuit. La commande du VPS bloque seulement la seconde moitié de P2 et
l'essai sur iPhone de P3.

---

## 8. Hors chantier

- Le chantier S'entraîner et la règle des examens (M9) : `entrainement-2e-degre/decisions.md` sera revu après P6 (identifiants
  opaques, réserve construite en local, appel au serveur ; audit § 8).
- Les comptes, l'accès réservé ou payant (question à l'école, LPD).
- Le simplexe (M10).
- Une montée de version de SymPy ou de Python : un chantier à part, avec un dump identique ou des changements listés.
- Un service worker, un usage hors ligne.

---

## 9. Questions pour l'enseignant (toutes réglées le 06.11.2026)

1. ✓ **Services tiers des pages** (T14) : **oui** (enseignant, 06.11.2026). En P5, KaTeX et les polices sont hébergés sur le VPS, et
   GoatCounter ne reçoit que le chemin, sans `?f=<saisie>`.
2. ✓ **Site d'essai `essai.samimir.ch`** (T10) pendant P3 à P5 : **oui** (06.11.2026). Il ne coûte rien de plus : le sous-domaine est
   dans la zone DNS de samimir.ch, déjà chez Infomaniak ; le certificat Let's Encrypt est gratuit ; il tourne sur le même VPS.
3. ✓ **Service de surveillance** (T13) : **UptimeRobot** (gratuit, courriel et application sur le téléphone), compte au nom de
   l'enseignant, créé en P2 (06.11.2026). Il ne voit que `/api/sante`, aucune donnée d'élève.
4. ✓ **Ligne « Données »** de l'accueil : **pas de phrase pour l'instant** (06.11.2026). Le texte du § 5.1 est gardé de côté.
5. ✓ **Ubuntu 24.04 LTS** plutôt que Debian (T3) : retenu sur recommandation (06.11.2026). C'est le seul système courant qui a
   Python 3.12, la version des tests, avec des mises à jour de sécurité automatiques.
6. ✓ **Redémarrage automatique à 3 h** après une mise à jour du noyau (T11, point 4) : **oui** (06.11.2026).
7. ✓ **1 vCPU et la rafale** (§ 6) : **on commence avec 1 vCPU, et on augmente après si la mesure de P2 dépasse le seuil**
   (06.11.2026). Infomaniak permet d'augmenter les ressources d'un VPS Lite (2 vCPU : 5.40 CHF HT par mois). Qu'il faille ou non
   réinstaller est à vérifier avant la commande.
