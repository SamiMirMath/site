"""Chrome sans interface piloté par le protocole DevTools (CDP), pour les tests de pages (T15).

Python seulement : `uv run -q --no-project --python 3.12 --with websockets python …`. Le site est servi
par un petit serveur HTTP local (le dépôt tel quel) ; KaTeX vient de jsDelivr (réseau requis). Pyodide, SymPy et mpmath viennent
de la copie locale (pyodide_local.py, T30) : les requêtes que les pages adressent à jsDelivr sont interceptées (domaine Fetch du
protocole DevTools, y compris dans le worker) et servies depuis la copie ; seul ce serveur de test redirige, les URL des pages ne changent pas.

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
    """La copie locale de Pyodide ne change pas pendant un processus : la vérifier une fois (elle relit tout le dépôt de fichiers) suffit."""
    global _copie_verifiee
    if not _copie_verifiee:
        pyodide_local.verifier()
        _copie_verifiee = True


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


class _Intercepteur(threading.Thread):
    """Sert depuis la copie locale les requêtes vers https://cdn.jsdelivr.net/pyodide/ de chaque onglet suivi, y compris celles
    de son worker (le worker de Pyodide charge pyodide.asm.wasm et les paquets lui-même : le domaine Fetch de la page les voit, sans
    qu'il faille s'attacher au worker, qui ne le prend pas en charge). Connexion DevTools à part : la page et ses
    commandes ne sont jamais bloquées par ce fil. Une requête hors de la copie reçoit un 404 (jamais le réseau)."""
    def __init__(self, url_ws, port_http, dossier, version):
        super().__init__(daemon=True)
        self.ws = connect(url_ws, max_size=None)
        self.port_http, self.dossier, self.version = port_http, dossier, version
        self.a_suivre = queue.Queue()
        self.arret = threading.Event()
        self.servies, self.refusees = [], []
        self._recus = queue.Queue()  # événements arrivés pendant l'attente d'une réponse : traités par run(), jamais en cascade
        self._n = 0
        self.start()

    def surveiller(self, cible):
        """Attend que l'onglet `cible` soit intercepté : à appeler avant d'y naviguer."""
        resultat = {"fait": threading.Event()}
        self.a_suivre.put((cible, resultat))
        if not resultat["fait"].wait(30):
            raise RuntimeError("interception de Pyodide impossible (délai)")
        if "erreur" in resultat:
            raise RuntimeError(f"interception de Pyodide impossible : {resultat['erreur']}")

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
        self._appel("Fetch.enable", session, patterns=[{"urlPattern": pyodide_local.PREFIXE_CDN + "*"}])

    def _evenement(self, m):
        methode, p = m.get("method"), m.get("params", {})
        if methode == "Fetch.requestPaused":
            self._repondre(m["sessionId"], p["requestId"], p["request"]["url"])

    def _repondre(self, session, requete, url):
        try:
            self._servir(session, requete, url)
        except ErreurPage:
            pass  # l'onglet a été fermé ou a navigué pendant l'attente : la requête n'existe plus

    def _servir(self, session, requete, url):
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


class Page:
    def __init__(self, ws, session):
        self.ws, self.session, self._id = ws, session, itertools.count(1)
        self.console = []

    def appel(self, methode, **params):
        i = next(self._id)
        self.ws.send(json.dumps({"id": i, "sessionId": self.session, "method": methode, "params": params}))
        while True:
            m = json.loads(self.ws.recv(timeout=180))
            if m.get("method") == "Runtime.consoleAPICalled":
                self.console.append((m["params"]["type"], " ".join(str(a.get("value", a.get("description", ""))) for a in m["params"]["args"])))
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
        _verifier_la_copie_locale()  # copie présente, complète, de la version des pages : sinon le test échoue ici, avec la marche à suivre
        gestionnaire = functools.partial(_Silencieux, directory=RACINE)
        self.serveur = _Serveur(("127.0.0.1", self.port_http), gestionnaire)
        self.port_http = self.serveur.server_address[1]
        threading.Thread(target=self.serveur.serve_forever, daemon=True).start()
        self.profil = tempfile.mkdtemp(prefix="chrome-tests-")
        self.proc = subprocess.Popen(
            [trouver_chrome(), "--headless=new", "--remote-debugging-port=0", f"--user-data-dir={self.profil}",
             "--no-first-run", "--no-default-browser-check", "--disable-gpu", "--no-sandbox", "--hide-scrollbars", "about:blank"],
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
        self.intercepteur = _Intercepteur(url, self.port_http, pyodide_local.DOSSIER, pyodide_local.version_attendue())
        return self

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

    def ouvrir(self, chemin, script_initial=None, conserver_stockage=False):
        """Ouvre `chemin` (relatif à la racine du site) dans un nouvel onglet ; renvoie la Page.
        `script_initial` : JavaScript exécuté dans la page avant tout autre script (banc du graphique).
        `conserver_stockage` : ne pas vider le localStorage (test qui rouvre une page pour vérifier qu'un choix est gardé)."""
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
            shutil.rmtree(self.profil, ignore_errors=True)
