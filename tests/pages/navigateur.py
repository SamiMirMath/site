"""Chrome sans interface piloté par le protocole DevTools (CDP), pour les tests de pages (T15).

Python seulement : `uv run -q --no-project --python 3.12 --with websockets python …`. Le site est servi
par un petit serveur HTTP local (le dépôt tel quel) ; Pyodide et KaTeX viennent de jsDelivr (réseau requis).

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
import urllib.request

from websockets.sync.client import connect

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


class _Silencieux(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a):
        pass


class _Serveur(http.server.ThreadingHTTPServer):
    """Un fil par requête (ThreadingHTTPServer) et une file de connexions assez grande. Une page télécharge en parallèle tous
    les fichiers Python de son outil (9 pour l'Étude complète) alors que Chrome ouvre jusqu'à 6 connexions par hôte : avec la file
    de 5 par défaut, un serveur qui n'accepte plus pendant un instant (machine chargée) fait réinitialiser des connexions
    (ConnectionResetError, vu sur macOS avec 12 connexions simultanées), donc « Failed to fetch » dans moteur-python.js."""
    request_queue_size = 128


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

    def attendre(self, condition_js, delai=60, pas=0.2):
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
    def __init__(self, port_http=0, port_cdp=9333):
        self.port_cdp = port_cdp
        self.port_http = port_http

    def __enter__(self):
        gestionnaire = functools.partial(_Silencieux, directory=RACINE)
        self.serveur = _Serveur(("127.0.0.1", self.port_http), gestionnaire)
        self.port_http = self.serveur.server_address[1]
        threading.Thread(target=self.serveur.serve_forever, daemon=True).start()
        self.profil = tempfile.mkdtemp(prefix="chrome-tests-")
        self.proc = subprocess.Popen(
            [trouver_chrome(), "--headless=new", f"--remote-debugging-port={self.port_cdp}", f"--user-data-dir={self.profil}",
             "--no-first-run", "--no-default-browser-check", "--disable-gpu", "--no-sandbox", "--hide-scrollbars", "about:blank"],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        url = None
        for _ in range(100):
            try:
                url = json.load(urllib.request.urlopen(f"http://127.0.0.1:{self.port_cdp}/json/version", timeout=2))["webSocketDebuggerUrl"]
                break
            except Exception:
                time.sleep(0.2)
        if not url:
            raise RuntimeError("Chrome ne répond pas")
        self.ws = connect(url, max_size=None)
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

    def ouvrir(self, chemin, script_initial=None):
        """Ouvre `chemin` (relatif à la racine du site) dans un nouvel onglet ; renvoie la Page.
        `script_initial` : JavaScript exécuté dans la page avant tout autre script (banc du graphique)."""
        # un seul onglet à la fois : chaque page lance un worker Pyodide (plusieurs dizaines de Mo), les laisser
        # s'accumuler fait dépasser les délais de chargement
        for ancien in getattr(self, "_cibles", []):
            try:
                self._appel("Target.closeTarget", targetId=ancien)
            except ErreurPage:
                pass
        cible = self._appel("Target.createTarget", url="about:blank")["targetId"]
        self._cibles = [cible]
        session = self._appel("Target.attachToTarget", targetId=cible, flatten=True)["sessionId"]
        page = Page(self.ws, session)
        page.appel("Page.enable")
        page.appel("Runtime.enable")
        if script_initial:
            page.appel("Page.addScriptToEvaluateOnNewDocument", source=script_initial)
        page.appel("Page.navigate", url=f"http://127.0.0.1:{self.port_http}/{chemin}")
        return page

    def __exit__(self, *exc):
        try:
            self.ws.close()
        finally:
            self.proc.terminate()
            try:
                self.proc.wait(10)
            except subprocess.TimeoutExpired:
                self.proc.kill()
            self.serveur.shutdown()
            shutil.rmtree(self.profil, ignore_errors=True)
