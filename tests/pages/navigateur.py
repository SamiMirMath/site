"""Chrome sans interface piloté par le protocole DevTools (CDP), pour les tests de pages (T15).

Python seulement : `uv run -q --no-project --python 3.12 --with websockets python …`. Le site est servi
par un petit serveur HTTP local (le dépôt tel quel). Aucun réseau pendant les tests : Pyodide, SymPy et mpmath viennent de la copie locale
de Pyodide (pyodide_local.py, T30), KaTeX et ses polices de la copie locale de KaTeX (katex_local.py, fondations F6). Les requêtes que
les pages adressent à jsDelivr sont interceptées (domaine Fetch du protocole DevTools, y compris dans le worker) et servies depuis ces
copies ; seul ce serveur de test redirige, les URL des pages ne changent pas. Les autres ressources extérieures des pages sont servies
vides (balise GoatCounter, feuille Google Fonts de l'accueil : police de repli).

Garde-fou réseau (F6) : toute autre requête HTTPS est refusée et notée (`intercepteur.fuites`) ; Chrome passe par un mandataire local
(`_Puits`) qui refuse et note tout ce qui sortirait encore (HTTP hors du serveur local, connexions) et ne résout aucun nom
(--host-resolver-rules). Rien ne quitte la machine ; une requête non servie fait échouer la sortie du Navigateur (tearDownClass).

    with Navigateur() as nav:
        page = nav.ouvrir("ensemble-definition/?f=ln(x-1)")
        page.attendre("document.querySelector('#etat').textContent === 'Prêt.'", 120)
"""
import functools
import http.server
import itertools
import json
import os
import shutil
import subprocess
import tempfile
import threading
import time
import queue
import urllib.parse
import urllib.request

from websockets.sync.client import connect as _connect

import katex_local
import pyodide_local

RACINE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
CHEMINS_CHROME = (
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "google-chrome", "google-chrome-stable", "chromium", "chromium-browser",
)


def trouver_chrome():
    for c in CHEMINS_CHROME:
        if os.path.isabs(c) and os.path.exists(c):
            return c
        if not os.path.isabs(c) and shutil.which(c):
            return shutil.which(c)
    raise RuntimeError("Chrome introuvable (Google Chrome ou chromium requis)")


_copie_verifiee = False


def _verifier_la_copie_locale():
    """Les copies locales de Pyodide et de KaTeX ne changent pas pendant un processus : les vérifier une fois (elles relisent tout le dépôt
    de fichiers) suffit. Une copie absente, incomplète ou d'une autre version que les pages fait échouer ici, avec la commande à lancer."""
    global _copie_verifiee
    if not _copie_verifiee:
        pyodide_local.verifier()
        _copie_verifiee = katex_local.verifier()
    return _copie_verifiee


# services de Chrome lui-même (mises à jour de composants, synchronisation, traduction, saisie automatique…) : sans ces options, Chrome
# contacte des serveurs de Google dès son lancement, sans rapport avec les pages. Le puits refuserait de toute façon ce trafic (rien ne
# sort) ; ces options en retirent l'essentiel (moins de bruit et de travail inutile). Ce qui en reste est noté par le puits (`connexions`,
# `navigateur`), sans faire échouer : ce n'est pas une requête des pages.
SANS_SERVICES_DU_NAVIGATEUR = (
    "--disable-background-networking", "--disable-component-update", "--disable-sync", "--disable-default-apps",
    "--disable-client-side-phishing-detection", "--disable-domain-reliability", "--no-pings",
    "--disable-features=Translate,OptimizationHints,AutofillServerCommunication,MediaRouter,CertificateTransparencyComponentUpdater",
)


def connect(url, **options):
    """Connexion WebSocket synchrone. Les versions récentes de `websockets` renvoient un objet à utiliser comme gestionnaire de contexte
    (DeprecationWarning si on l'utilise directement) : on l'ouvre ici, et `close()` du résultat ferme la connexion."""
    contexte = _connect(url, **options)
    connexion = contexte.__enter__()
    connexion._contexte = contexte                 # garder le gestionnaire en vie : le ramasse-miettes fermerait la connexion
    return connexion


class _Silencieux(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def end_headers(self):
        # les requêtes de Pyodide réécrites vers la copie locale gardent leur nature « cross-origin » pour Chrome
        self.send_header("Access-Control-Allow-Origin", "*")
        super().end_headers()


class _Serveur(http.server.ThreadingHTTPServer):
    """Un fil par requête (ThreadingHTTPServer) et une file de connexions assez grande. Une page télécharge en parallèle tous
    les fichiers Python de son outil (9 pour l'Étude complète) alors que Chrome ouvre jusqu'à 6 connexions par hôte : avec la file
    de 5 par défaut, un serveur qui n'accepte plus pendant un instant (machine chargée) fait réinitialiser des connexions
    (ConnectionResetError, vu sur macOS avec 12 connexions simultanées), donc « Failed to fetch » dans moteur-python.js."""
    request_queue_size = 128


class _Puits(http.server.ThreadingHTTPServer):
    """Mandataire (proxy) de Chrome pendant les tests : tout ce qui n'est ni intercepté ni adressé au serveur local (127.0.0.1, que Chrome
    ne fait jamais passer par un mandataire) arrive ici, est noté puis refusé (403) ; rien ne part sur le réseau. Trois listes :
    - `fuites` : requêtes d'une page (en-tête Referer ou Origin du serveur local), URL complète : HTTP hors du serveur local ;
    - `connexions` : demandes de connexion (CONNECT hôte:port), jamais une requête d'une page, puisque l'intercepteur prend toutes leurs
      requêtes HTTPS avant toute connexion : connexions d'avance (<link rel="preconnect"> de l'accueil) ou services de Chrome ;
    - `navigateur` : autres requêtes HTTP, sans page d'origine : services de Chrome lui-même (horloge réseau…)."""
    daemon_threads = True

    def __init__(self):
        self.fuites, self.connexions, self.navigateur = [], [], []
        puits = self

        class _Refus(http.server.BaseHTTPRequestHandler):
            def handle_one_request(self):
                self.raw_requestline = self.rfile.readline(65537)
                if not self.raw_requestline or not self.parse_request():
                    self.close_connection = True
                    return
                cible = f"{self.command} {self.path}"
                origine = " ".join(self.headers.get(n, "") for n in ("Referer", "Origin"))
                if self.command == "CONNECT":
                    puits.connexions.append(cible)
                elif "http://127.0.0.1:" in origine:
                    puits.fuites.append(cible)
                else:
                    puits.navigateur.append(cible)
                self.send_response(403, "Hors des copies locales des tests")
                self.send_header("Content-Length", "0")
                self.send_header("Connection", "close")
                self.end_headers()
                self.close_connection = True

            def log_message(self, *a):
                pass

        super().__init__(("127.0.0.1", 0), _Refus)
        threading.Thread(target=self.serve_forever, daemon=True).start()

    def fermer(self):
        self.shutdown()
        self.server_close()


class _Intercepteur(threading.Thread):
    """Intercepte toutes les requêtes HTTPS de chaque onglet suivi, y compris celles de son worker (le worker de Pyodide charge
    pyodide.asm.wasm et les paquets lui-même : le domaine Fetch de la page les voit, sans qu'il faille s'attacher au worker, qui ne le prend
    pas en charge), et la balise GoatCounter (gc.zgo.at, en HTTP). Connexion DevTools à part : la page et ses commandes ne sont jamais
    bloquées par ce fil. Pyodide (https://cdn.jsdelivr.net/pyodide/) et KaTeX (https://cdn.jsdelivr.net/npm/katex@…) sont servis depuis
    leur copie locale (`servies`) ; un fichier absent de la copie reçoit un 404 (`refusees`, jamais le réseau). Toute autre requête HTTPS
    est refusée et notée (`fuites`), sauf GoatCounter (`comptage`) et la feuille Google Fonts de l'accueil (`polices`), servies vides."""
    def __init__(self, url_ws, port_http, dossier, version, katex):
        super().__init__(daemon=True)
        self.ws = connect(url_ws, max_size=None)
        self.port_http, self.dossier, self.version = port_http, dossier, version
        self.katex = katex                    # contenu d'empreintes.json de la copie de KaTeX (version, fichiers)
        self.a_suivre = queue.Queue()
        self.arret = threading.Event()
        self.servies, self.refusees = [], []
        self.comptage, self.fuites = [], []   # GoatCounter : requêtes de la balise (gc.zgo.at) servies par un script vide ; requêtes extérieures refusées (goatcounter.com, hôte sans copie locale : jamais attendues)
        self.polices = []                     # feuille Google Fonts de l'accueil, servie vide (police de repli)
        self._recus = queue.Queue()  # événements arrivés pendant l'attente d'une réponse : traités par run(), jamais en cascade
        self._n = 0
        self.start()

    def surveiller(self, cible):
        """Attend que l'onglet `cible` soit intercepté : à appeler avant d'y naviguer."""
        resultat = {"fait": threading.Event()}
        self.a_suivre.put((cible, resultat))
        if not resultat["fait"].wait(30):
            raise RuntimeError("interception des requêtes extérieures impossible (délai)")
        if "erreur" in resultat:
            raise RuntimeError(f"interception des requêtes extérieures impossible : {resultat['erreur']}")

    def _envoyer(self, methode, session=None, **params):
        self._n += 1
        msg = {"id": self._n, "method": methode, "params": params}
        if session:
            msg["sessionId"] = session
        self.ws.send(json.dumps(msg))
        return self._n

    def _appel(self, methode, session=None, **params):
        i = self._envoyer(methode, session, **params)
        while True:
            m = json.loads(self.ws.recv(timeout=30))
            if m.get("id") == i:
                if "error" in m:
                    raise ErreurPage(m["error"])
                return m["result"]
            self._recus.put(m)

    def _intercepter(self, session):
        self._appel("Fetch.enable", session, patterns=[{"urlPattern": "https://*"}, {"urlPattern": "*gc.zgo.at*"},
                                                       {"urlPattern": "*goatcounter.com*"}])

    def _evenement(self, m):
        methode, p = m.get("method"), m.get("params", {})
        if methode == "Fetch.requestPaused":
            self._repondre(m["sessionId"], p["requestId"], p["request"]["url"])

    def _compteur(self, session, requete, url):
        """La balise GoatCounter (gc.zgo.at/count.js) reçoit un script vide : aucune requête sortante pendant les tests, et la visite n'est jamais comptée.
        Une requête vers goatcounter.com (le script vide n'en envoie pas) est enregistrée, puis refusée."""
        if "gc.zgo.at" in url:
            self.comptage.append(url)
            self._appel("Fetch.fulfillRequest", session, requestId=requete, responseCode=200, responsePhrase="Script vide",
                        responseHeaders=[{"name": "Content-Type", "value": "application/javascript"}])
        else:
            self.fuites.append(url)
            self._appel("Fetch.failRequest", session, requestId=requete, errorReason="BlockedByClient")

    def _repondre(self, session, requete, url):
        try:
            self._servir(session, requete, url)
        except ErreurPage:
            pass  # l'onglet a été fermé ou a navigué pendant l'attente : la requête n'existe plus

    def _servir(self, session, requete, url):
        if "gc.zgo.at" in url or "goatcounter.com" in url:
            return self._compteur(session, requete, url)
        if url.startswith(katex_local.PREFIXE_CDN):
            return self._katex(session, requete, url)
        if urllib.parse.urlparse(url).hostname == "fonts.googleapis.com":
            self.polices.append(url)
            return self._appel("Fetch.fulfillRequest", session, requestId=requete, responseCode=200, responsePhrase="Feuille vide",
                               responseHeaders=[{"name": "Content-Type", "value": "text/css"}])
        if not url.startswith(pyodide_local.PREFIXE_CDN):
            self.fuites.append(url)
            return self._appel("Fetch.failRequest", session, requestId=requete, errorReason="BlockedByClient")
        chemin = urllib.parse.urlparse(url).path
        prefixe = f"/pyodide/v{self.version}/full/"
        nom = chemin[len(prefixe):] if chemin.startswith(prefixe) else None
        if not nom or "/" in nom or not os.path.isfile(os.path.join(self.dossier, nom)):
            self.refusees.append(url)
            self._appel("Fetch.fulfillRequest", session, requestId=requete, responseCode=404, responsePhrase="Absent de la copie locale")
            return
        # réécriture vers le serveur de test (même origine que la page) plutôt qu'un corps envoyé par DevTools : 18 Mo en base64
        # à chaque page ralentissaient la suite, alors que le cache HTTP de Chrome garde ces fichiers d'une page à la suivante
        self.servies.append(nom)
        self._appel("Fetch.continueRequest", session, requestId=requete,
                    url=f"http://127.0.0.1:{self.port_http}/{os.path.relpath(self.dossier, RACINE)}/{nom}")

    def _katex(self, session, requete, url):
        """KaTeX : https://cdn.jsdelivr.net/npm/katex@<version>/<chemin> réécrit vers la copie locale (même version, fichier de la copie),
        sinon 404. Les polices, demandées par la feuille de style relativement à son URL d'origine (la réécriture ne se voit pas de la page),
        passent aussi par ici."""
        version, _, chemin = url[len(katex_local.PREFIXE_CDN):].split("?")[0].split("#")[0].partition("/")
        if version != self.katex["version"] or chemin not in self.katex["fichiers"]:
            self.refusees.append(url)
            self._appel("Fetch.fulfillRequest", session, requestId=requete, responseCode=404, responsePhrase="Absent de la copie locale")
            return
        self.servies.append(f"katex/{chemin}")
        self._appel("Fetch.continueRequest", session, requestId=requete,
                    url=f"http://127.0.0.1:{self.port_http}/{os.path.relpath(katex_local.DOSSIER, RACINE)}/{chemin}")

    def run(self):
        try:
            while not self.arret.is_set():
                try:
                    cible, resultat = self.a_suivre.get_nowait()
                except queue.Empty:
                    pass
                else:
                    try:
                        session = self._appel("Target.attachToTarget", targetId=cible, flatten=True)["sessionId"]
                        self._intercepter(session)
                    except ErreurPage as e:
                        resultat["erreur"] = e
                    resultat["fait"].set()
                try:
                    m = self._recus.get_nowait()
                except queue.Empty:
                    try:
                        m = json.loads(self.ws.recv(timeout=0.05))
                    except TimeoutError:
                        continue
                self._evenement(m)
        except Exception:
            if not self.arret.is_set():
                raise

    def fermer(self):
        self.arret.set()
        self.join(5)
        self.ws.close()


class ErreurPage(Exception):
    pass


class ErreurReseau(AssertionError):
    """Garde-fou réseau : une page a demandé une ressource extérieure qu'aucune copie locale ne sert."""


class Page:
    def __init__(self, ws, session):
        self.ws, self.session, self._id = ws, session, itertools.count(1)
        self.console = []
        self.erreurs = []             # exceptions non attrapées, erreurs du journal du navigateur (ressource introuvable, module refusé…) et console.error

    def appel(self, methode, **params):
        i = next(self._id)
        self.ws.send(json.dumps({"id": i, "sessionId": self.session, "method": methode, "params": params}))
        while True:
            m = json.loads(self.ws.recv(timeout=180))
            if m.get("method") == "Runtime.consoleAPICalled":
                self.console.append((m["params"]["type"], " ".join(str(a.get("value", a.get("description", ""))) for a in m["params"]["args"])))
                if m["params"]["type"] == "error":
                    self.erreurs.append("console.error : " + self.console[-1][1])
            elif m.get("method") == "Runtime.exceptionThrown":
                d = m["params"]["exceptionDetails"]
                self.erreurs.append("exception : " + (d.get("exception", {}).get("description") or d.get("text", "")))
            elif m.get("method") == "Log.entryAdded" and m["params"]["entry"].get("level") == "error":
                e = m["params"]["entry"]
                self.erreurs.append(f"journal : {e.get('text', '')} ({e.get('url', '')})")
            if m.get("id") == i:
                if "error" in m:
                    raise ErreurPage(m["error"])
                return m.get("result", {})

    def evaluer(self, js):
        r = self.appel("Runtime.evaluate", expression=js, returnByValue=True, awaitPromise=True)
        if "exceptionDetails" in r:
            raise ErreurPage(r["exceptionDetails"].get("exception", {}).get("description", str(r["exceptionDetails"])))
        return r["result"].get("value")

    def attendre(self, condition_js, delai=60, pas=0.05):
        fin = time.time() + delai
        while time.time() < fin:
            if self.evaluer(f"Boolean({condition_js})"):
                return
            time.sleep(pas)
        raise TimeoutError(f"condition non atteinte en {delai} s : {condition_js}")

    def taper(self, selecteur, texte, pause=0.03):
        """Tape `texte` caractère par caractère dans le champ `selecteur` (un événement `input` par touche)."""
        self.evaluer(f"document.querySelector({selecteur!r}).focus()")
        for c in texte:
            self.appel("Input.insertText", text=c)
            time.sleep(pause)

    def _immobile(self, position):
        """Évalue `position` toutes les 50 ms jusqu'à 6 mesures identiques de suite (0,3 s sans bouger), 10 s au plus ; renvoie la dernière mesure."""
        derniere, calme, fin = None, 0, time.time() + 10
        while calme < 6 and time.time() < fin:
            time.sleep(0.05)
            mesure = self.evaluer(position)
            calme = calme + 1 if mesure == derniere else 0
            derniere = mesure
        return derniere

    def _centre_immobile(self, selecteur):
        """Amène l'élément au milieu de l'écran et renvoie son centre (x, y) une fois la page immobile : un défilement doux en cours (vers la carte qui vient
        d'apparaître) fait avaler le geste par le navigateur, ce que l'élève ne fait jamais (il ne touche pas pendant que la page défile).
        On laisse d'abord finir un défilement de la page en cours (sinon il se bat avec le centrage), puis on centre ; si, une fois la page immobile,
        l'élément n'est pas entièrement dans l'écran (un défilement de la page l'a emporté), on recentre : 3 essais au plus (chantier « Tests rapides », P1)."""
        position = (f"(() => {{ const r = document.querySelector({selecteur!r}).getBoundingClientRect(), h = document.documentElement; "
                    "return [scrollX, scrollY, r.x + r.width / 2, r.y + r.height / 2, h.scrollHeight, "
                    "r.left >= 0 && r.top >= 0 && r.right <= h.clientWidth && r.bottom <= h.clientHeight]; })()")
        self._immobile(position)
        for _ in range(3):
            self.evaluer(f"document.querySelector({selecteur!r}).scrollIntoView({{block: 'center', behavior: 'instant'}})")
            mesure = self._immobile(position)
            if mesure[5]:
                break
        return mesure[2], mesure[3]

    def toucher(self, selecteur):
        """Appui d'un doigt (touchStart puis touchEnd) au centre de l'élément, après l'avoir amené à l'écran ; le navigateur en tire le clic
        (page ouverte avec `tactile=True`). Si le point d'appui n'est pas sur l'élément (ou l'un de ses descendants), erreur explicite plutôt qu'un appui
        perdu (chantier « Tests rapides », P1)."""
        x, y = self._centre_immobile(selecteur)
        dessous = self.evaluer(f"(() => {{ const e = document.querySelector({selecteur!r}), d = document.elementFromPoint({x}, {y}); "
                               "return d && (d === e || e.contains(d)) ? '' : (d ? d.outerHTML.slice(0, 160) : 'aucun élément (point hors de l’écran)'); })()")
        if dessous:
            raise ErreurPage(f"la touche n'est pas sous le doigt : {selecteur} visé en ({x:.0f}, {y:.0f}), sous le doigt : {dessous}")
        self.appel("Input.dispatchTouchEvent", type="touchStart", touchPoints=[{"x": x, "y": y}])
        self.appel("Input.dispatchTouchEvent", type="touchEnd", touchPoints=[])

    def glisser(self, selecteur, dx=0, dy=0, etapes=12, pause=0.016):
        """Glissement d'un doigt de (dx, dy) pixels à partir du centre de l'élément (touchStart, touchMove en `etapes` pas, touchEnd) ; la page décide
        si le geste fait défiler (touch-action) ou le manipule. Page ouverte avec `tactile=True`."""
        x, y = self._centre_immobile(selecteur)
        self.appel("Input.dispatchTouchEvent", type="touchStart", touchPoints=[{"x": x, "y": y}])
        for k in range(1, etapes + 1):
            self.appel("Input.dispatchTouchEvent", type="touchMove", touchPoints=[{"x": x + dx * k / etapes, "y": y + dy * k / etapes}])
            time.sleep(pause)
        self.appel("Input.dispatchTouchEvent", type="touchEnd", touchPoints=[])

    def capture(self, chemin):
        import base64
        d = self.appel("Page.captureScreenshot", format="png", captureBeyondViewport=True)["data"]
        with open(chemin, "wb") as f:
            f.write(base64.b64decode(d))

    def taille(self, largeur, hauteur=900, sombre=False, imprimante=False, dpr=1):
        self.appel("Emulation.setDeviceMetricsOverride", width=largeur, height=hauteur, deviceScaleFactor=dpr, mobile=False)
        feats = [{"name": "prefers-color-scheme", "value": "dark" if sombre else "light"}]
        self.appel("Emulation.setEmulatedMedia", media="print" if imprimante else "screen", features=feats)


class Navigateur:
    def __init__(self, port_http=0):
        self.port_http = port_http

    def __enter__(self):
        katex = _verifier_la_copie_locale()  # copies présentes, complètes, de la version des pages : sinon le test échoue ici, avec la marche à suivre
        self.puits = _Puits()
        gestionnaire = functools.partial(_Silencieux, directory=RACINE)
        self.serveur = _Serveur(("127.0.0.1", self.port_http), gestionnaire)
        self.port_http = self.serveur.server_address[1]
        threading.Thread(target=self.serveur.serve_forever, daemon=True).start()
        self.profil = tempfile.mkdtemp(prefix="chrome-tests-")
        self.proc = subprocess.Popen(
            [trouver_chrome(), "--headless=new", "--remote-debugging-port=0", f"--user-data-dir={self.profil}",
             "--no-first-run", "--no-default-browser-check", "--disable-gpu", "--no-sandbox", "--hide-scrollbars",
             # garde-fou réseau (F6) : tout ce qui ne va pas au serveur local passe par le puits, et aucun nom n'est résolu
             f"--proxy-server=http://127.0.0.1:{self.puits.server_address[1]}", "--host-resolver-rules=MAP * ~NOTFOUND , EXCLUDE 127.0.0.1",
             *SANS_SERVICES_DU_NAVIGATEUR, "about:blank"],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        # port DevTools choisi par Chrome (port 0) et écrit dans le profil : plusieurs Chrome peuvent tourner en même temps (pytest-xdist)
        url = None
        for _ in range(200):
            try:
                with open(os.path.join(self.profil, "DevToolsActivePort")) as f:
                    port_cdp = int(f.readline())
                with urllib.request.urlopen(f"http://127.0.0.1:{port_cdp}/json/version", timeout=2) as reponse:
                    url = json.load(reponse)["webSocketDebuggerUrl"]
                break
            except Exception:
                time.sleep(0.1)
        if not url:
            raise RuntimeError("Chrome ne répond pas")
        self.ws = connect(url, max_size=None)
        self.intercepteur = _Intercepteur(url, self.port_http, pyodide_local.DOSSIER, pyodide_local.version_attendue(), katex)
        return self

    def fuites(self):
        """Requêtes extérieures non servies localement depuis l'ouverture : refusées par l'intercepteur (HTTPS) ou par le puits (le reste)."""
        return self.intercepteur.fuites + self.puits.fuites

    def _appel(self, methode, session=None, **params):
        i = getattr(self, "_n", 0) + 1
        self._n = i
        msg = {"id": i, "method": methode, "params": params}
        if session:
            msg["sessionId"] = session
        self.ws.send(json.dumps(msg))
        while True:
            m = json.loads(self.ws.recv(timeout=60))
            if m.get("id") == i:
                if "error" in m:
                    raise ErreurPage(m["error"])
                return m["result"]

    def ouvrir(self, chemin, script_initial=None, conserver_stockage=False, tactile=False, agent=None):
        """Ouvre `chemin` (relatif à la racine du site) dans un nouvel onglet ; renvoie la Page.
        `script_initial` : JavaScript exécuté dans la page avant tout autre script (banc du graphique).
        `conserver_stockage` : ne pas vider le localStorage (test qui rouvre une page pour vérifier qu'un choix est gardé).
        `tactile` : écran tactile émulé dès le chargement (`(pointer: coarse)` vrai, 5 points de contact) : les pages lisent ce média au démarrage.
        `agent` : (agent utilisateur, plateforme) imposés, p. ex. un iPhone ou un téléphone Android : sur un Mac, le navigateur tactile émulé se déclare « MacIntel »
        avec des points de contact, comme un iPad."""
        # un seul onglet à la fois : chaque page lance un worker Pyodide (plusieurs dizaines de Mo), les laisser
        # s'accumuler fait dépasser les délais de chargement
        for ancien in getattr(self, "_cibles", []):
            try:
                self._appel("Target.closeTarget", targetId=ancien)
            except ErreurPage:
                pass
        cible = self._appel("Target.createTarget", url="about:blank")["targetId"]
        self._cibles = [cible]
        self.intercepteur.surveiller(cible)
        session = self._appel("Target.attachToTarget", targetId=cible, flatten=True)["sessionId"]
        page = Page(self.ws, session)
        page.appel("Page.enable")
        page.appel("Runtime.enable")
        page.appel("Log.enable")
        if tactile:
            page.appel("Emulation.setTouchEmulationEnabled", enabled=True, maxTouchPoints=5)
        if agent:
            page.appel("Emulation.setUserAgentOverride", userAgent=agent[0], platform=agent[1])
        # chaque page part d'un état propre : le navigateur et le serveur sont les mêmes pour tous les tests, donc le localStorage aussi
        # (test_acc04 mémorise une filière sur l'accueil, que la page « Exponentielles et logarithmes » reprend ensuite)
        if not conserver_stockage:
            page.appel("Storage.clearDataForOrigin", origin=f"http://127.0.0.1:{self.port_http}", storageTypes="local_storage,session_storage")
        if script_initial:
            page.appel("Page.addScriptToEvaluateOnNewDocument", source=script_initial)
        page.appel("Page.navigate", url=f"http://127.0.0.1:{self.port_http}/{chemin}")
        return page

    def __exit__(self, *exc):
        try:
            self.intercepteur.fermer()
            self.ws.close()
        finally:
            self.proc.terminate()
            try:
                self.proc.wait(10)
            except subprocess.TimeoutExpired:
                self.proc.kill()
            self.serveur.shutdown()
            self.serveur.server_close()
            self.puits.fermer()
            shutil.rmtree(self.profil, ignore_errors=True)
        # garde-fou réseau (F6) : une requête extérieure non servie localement fait échouer (tearDownClass, fin du `with`) ; une exception
        # déjà en cours garde la priorité
        if exc[0] is None and self.fuites():
            raise ErreurReseau("requêtes extérieures non servies par les copies locales (refusées, rien n'est sorti) : " + " ; ".join(self.fuites()))
