"""Application du moteur sur serveur (chantier moteur-serveur, P1 ; docs/chantiers/moteur-serveur/decisions.md, T1, T3, T14 ;
docs/architecture.md, règle A10).

WSGI, bibliothèque standard seule, sans framework, synchrone : une requête à la fois par processus (gunicorn en processus synchrones,
P2). Le serveur ne connaît aucun outil par son nom (A10) : il n'appelle que les fonctions `<fn>_json` listées dans
moteur/manifeste.json, sur le module que le manifeste nomme, et renvoie leur chaîne telle quelle, jamais re-sérialisée.

Routes :
- `POST /api/<outil>/<fn>` : le corps est l'argument JSON que la page passe à `appelPy`, une chaîne ou un tableau de chaînes
  (`[entrée, filière]`, `[niveau, filière]`), avec `Content-Type: application/json`. Un tableau est une liste d'arguments
  (`fn(*arg)`), toute chaîne est passée telle quelle (`fn(arg)`), comme commun/worker-pyodide.js. Réponse 200 : la chaîne brute de
  `<module>.<fn>_json`, en UTF-8. Les fonctions « anciennes » du manifeste sont dans « fonctions » : elles restent acceptées.
- `GET` et `HEAD /api/sante` : `{"ok": true, "version": "<commit>"}` si tout va bien, sinon 503 avec `{"ok": false, "raison": …}`.
  Contrôles (T1) : la version (variable MOTEUR_VERSION, 7 à 40 chiffres hexadécimaux) ; l'état de la machine, lu dans le fichier
  nommé par MOTEUR_ETAT (écrit chaque heure par un minuteur root, P2), un objet JSON
      {"certificat_expire": "<date et heure ISO 8601 avec fuseau>", "disque_pourcent": <nombre de 0 à 100>}
  (le certificat expire dans plus de CERTIFICAT_JOURS_MIN jours, le disque est plein à moins de DISQUE_POURCENT_MAX %, le fichier
  date de moins de AGE_MAX_ETAT_S secondes) ; un vrai calcul, CALCUL_DE_SANTE, dont la sortie a `"ok": true`. Variable absente, fichier
  absent, illisible, périmé ou mauvais : 503.

Codes (la page ne lit jamais le corps d'une erreur, seulement le code : T1) : 400 (corps illisible, type de contenu, argument qui
n'est ni une chaîne ni un tableau de chaînes, nombre d'arguments refusé par la fonction), 404 (chemin, outil ou fonction hors du
manifeste), 405 (méthode, avec `Allow`), 413 (corps de plus de TAILLE_MAX octets, non lu), 500 (exception du moteur, ou sortie qui
n'est pas une chaîne), 503 (santé). Toute réponse : `Content-Type: application/json; charset=utf-8`, `Cache-Control: no-store`. Le
corps d'une erreur est fixe : il ne contient jamais la saisie.

Journal (T14) : une ligne par exception, sur le journal « serveur » (module logging), au niveau ERROR : l'outil, la fonction, le type
de l'exception et les cadres de la pile (fichier, ligne, fonction). Jamais le message de l'exception, qui peut contenir la saisie
(SympifyError), ni la saisie. Aucun journal d'accès.

Démarrage (T3, `--preload` de gunicorn) : la création de l'application vérifie les versions du manifeste (Python ; SymPy et mpmath
importés, version installée = version du manifeste), met les dossiers des moteurs en tête de sys.path dans l'ordre de
tests/python/moteurs.py, importe chaque .py du manifeste (modules importés paresseusement compris, comme exp_log_m) et vérifie que
chaque fonction du manifeste existe. Un module qui ne s'importe pas empêche le démarrage au lieu de tomber sur un élève. La racine
est le dossier parent de serveur/.

gunicorn : `application` de ce module ; délai DELAI_GUNICORN_S (plus grand que le plus grand délai des pages : test_serveur.py).
Serveur local, sans gunicorn : `python3 tests/outils/serveur_local.py`."""
import datetime
import importlib
import importlib.metadata
import inspect
import json
import logging
import math
import os
import re
import sys
import time
import traceback

RACINE = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
MANIFESTE = "moteur/manifeste.json"
TAILLE_MAX = 4096                     # octets du corps d'une requête (T1 : saisie de plus de 4 Ko -> 413)
DELAI_GUNICORN_S = 50                 # gunicorn --timeout (T3) : plus que le plus grand delaiCalcul des pages (45 s)
CHEMIN_API = re.compile(r"/api/([a-z0-9]+(?:-[a-z0-9]+)*)/([a-z]+(?:_[a-z]+)*)")
CHEMIN_SANTE = "/api/sante"
CALCUL_DE_SANTE = ("equations-2e-degre", "resoudre", "x^2-1=0")      # T1 : un vrai calcul, par la liste blanche du manifeste
CERTIFICAT_JOURS_MIN = 14
DISQUE_POURCENT_MAX = 90
AGE_MAX_ETAT_S = 3 * 3600             # écrit chaque heure : une écriture manquée est tolérée, pas deux
VERSION = re.compile(r"[0-9a-f]{7,40}")
VARIABLE_VERSION = "MOTEUR_VERSION"
VARIABLE_ETAT = "MOTEUR_ETAT"
VERSIONS_HORS_SERVEUR = {"pyodide"}    # clé de « versions » qui n'est pas un paquet du serveur (le moteur de la page)
CADRES_MAX = 40                       # au-delà (récursion), le journal garde les premiers et les derniers cadres
JOURNAL = logging.getLogger("serveur")
STATUTS = {200: "200 OK", 400: "400 Bad Request", 404: "404 Not Found", 405: "405 Method Not Allowed",
           413: "413 Payload Too Large", 500: "500 Internal Server Error", 503: "503 Service Unavailable"}
ERREURS = {400: "requete", 404: "introuvable", 405: "methode", 413: "trop_long", 500: "serveur"}


def dossiers_moteurs(manifeste):
    """Dossiers des fichiers du manifeste, dans l'ordre de leur première apparition (tests/python/outils_du_site.py,
    dossiers_moteurs : test_serveur.py vérifie que c'est la même liste)."""
    dossiers = []
    for entree in manifeste["outils"].values():
        for chemin in entree["fichiers"]:
            d = os.path.dirname(chemin)
            if d not in dossiers:
                dossiers.append(d)
    return dossiers


def verifier_versions(versions):
    """Python et paquets du manifeste (« versions ») : exactement ceux des tests, sinon RuntimeError. Importe les paquets (SymPy)."""
    for nom, attendue in versions.items():
        if nom in VERSIONS_HORS_SERVEUR:
            continue
        if nom == "python":
            trouvee = "%d.%d" % sys.version_info[:2]
        else:
            importlib.import_module(nom)
            trouvee = importlib.metadata.version(nom)
        if trouvee != attendue:
            raise RuntimeError(f"{nom} {trouvee} au lieu de {attendue} (moteur/manifeste.json)")


def arguments(arg):
    """Tuple des arguments de `<fn>_json` (une chaîne, ou un tableau non vide de chaînes), None sinon."""
    if isinstance(arg, str):
        return (arg,)
    if isinstance(arg, list) and arg and all(isinstance(a, str) for a in arg):
        return tuple(arg)
    return None


def cadres(tb):
    """« fichier:ligne:fonction » de chaque cadre de la pile, du plus extérieur au plus intérieur (aucune ligne de code, aucune
    valeur) ; chemins relatifs à la racine pour les fichiers du dépôt."""
    liste = []
    for cadre, ligne in traceback.walk_tb(tb):
        fichier = cadre.f_code.co_filename
        if fichier.startswith(RACINE + os.sep):
            fichier = os.path.relpath(fichier, RACINE)
        liste.append(f"{fichier}:{ligne}:{cadre.f_code.co_name}")
    if len(liste) > CADRES_MAX:
        liste = liste[:10] + [f"… {len(liste) - CADRES_MAX} cadres …"] + liste[-(CADRES_MAX - 10):]
    return liste


def noter_erreur(outil, fn, exception):
    """Journal de l'application (T14) : ni le message de l'exception, ni la saisie."""
    genre = type(exception)
    JOURNAL.error("erreur outil=%s fonction=%s type=%s.%s pile=%s", outil, fn, genre.__module__, genre.__qualname__,
                  " > ".join(cadres(exception.__traceback__)))


def etat_de_la_machine(chemin, maintenant=None):
    """None si l'état est bon ; sinon la raison du 503 (etat_absent, etat_illisible, etat_perime, certificat, disque)."""
    if not chemin:
        return "etat_absent"
    maintenant = time.time() if maintenant is None else maintenant
    try:
        age = maintenant - os.stat(chemin).st_mtime
        with open(chemin, encoding="utf-8") as f:
            etat = json.load(f)
    except FileNotFoundError:
        return "etat_absent"
    except (OSError, ValueError):
        return "etat_illisible"
    if age > AGE_MAX_ETAT_S:
        return "etat_perime"
    if not isinstance(etat, dict):
        return "etat_illisible"
    disque = etat.get("disque_pourcent")
    try:
        expire = datetime.datetime.fromisoformat(etat.get("certificat_expire"))
    except (TypeError, ValueError):
        return "etat_illisible"
    if expire.tzinfo is None or type(disque) not in (int, float) or not math.isfinite(disque) or not 0 <= disque <= 100:
        return "etat_illisible"
    if expire - datetime.datetime.fromtimestamp(maintenant, datetime.timezone.utc) <= datetime.timedelta(days=CERTIFICAT_JOURS_MIN):
        return "certificat"
    if disque >= DISQUE_POURCENT_MAX:
        return "disque"
    return None


class Application:
    """L'application WSGI. `manifeste` : le contenu de moteur/manifeste.json (lu dans `racine` par défaut)."""

    def __init__(self, racine=RACINE, manifeste=None):
        if manifeste is None:
            with open(os.path.join(racine, MANIFESTE), encoding="utf-8") as f:
                manifeste = json.load(f)
        verifier_versions(manifeste.get("versions", {}))
        for dossier in dossiers_moteurs(manifeste):
            chemin = os.path.join(racine, dossier)
            if chemin not in sys.path:
                sys.path.insert(0, chemin)
        self.outils = {}
        for outil, entree in manifeste["outils"].items():
            for fichier in entree["fichiers"]:
                importlib.import_module(os.path.splitext(os.path.basename(fichier))[0])
            module = importlib.import_module(entree["module"])
            for fn in entree["fonctions"]:
                if not callable(getattr(module, fn + "_json", None)):
                    raise RuntimeError(f"{outil} : {entree['module']}.{fn}_json absente (moteur/manifeste.json)")
            self.outils[outil] = (module, frozenset(entree["fonctions"]))
        outil, fn, _ = CALCUL_DE_SANTE
        if fn not in self.outils.get(outil, (None, ()))[1]:
            raise RuntimeError(f"calcul de /api/sante hors du manifeste : {outil}/{fn}")

    def fonction(self, outil, fn):
        """`<fn>_json` du module de l'outil, lue à chaque appel (jamais gardée)."""
        return getattr(self.outils[outil][0], fn + "_json")

    def __call__(self, environ, start_response):
        chemin = environ.get("PATH_INFO", "")
        methode = environ.get("REQUEST_METHOD", "")
        entetes = []
        if chemin == CHEMIN_SANTE:
            if methode in ("GET", "HEAD"):
                code, corps = self.sante()
            else:
                code, corps, entetes = 405, None, [("Allow", "GET, HEAD")]
        else:
            m = CHEMIN_API.fullmatch(chemin)
            if not m or m.group(1) not in self.outils or m.group(2) not in self.outils[m.group(1)][1]:
                code, corps = 404, None
            elif methode != "POST":
                code, corps, entetes = 405, None, [("Allow", "POST")]
            else:
                code, corps = self.calcul(m.group(1), m.group(2), environ)
        if corps is None:
            corps = json.dumps({"erreur": ERREURS[code]}).encode("utf-8")
        start_response(STATUTS[code], [("Content-Type", "application/json; charset=utf-8"), ("Cache-Control", "no-store"),
                                       ("Content-Length", str(len(corps)))] + entetes)
        return [] if methode == "HEAD" else [corps]

    def calcul(self, outil, fn, environ):
        """(code, corps en octets ou None) d'un POST sur un couple outil-fonction du manifeste."""
        if environ.get("CONTENT_TYPE", "").split(";")[0].strip().lower() != "application/json":
            return 400, None
        try:
            longueur = int(environ.get("CONTENT_LENGTH") or "")
        except ValueError:
            return 400, None
        if longueur < 0:
            return 400, None
        if longueur > TAILLE_MAX:
            return 413, None
        brut = environ["wsgi.input"].read(longueur)
        if len(brut) != longueur:
            return 400, None
        try:
            args = arguments(json.loads(brut.decode("utf-8")))
        except ValueError:                            # UnicodeDecodeError et JSONDecodeError compris
            return 400, None
        if args is None:
            return 400, None
        fonction = self.fonction(outil, fn)
        try:
            inspect.signature(fonction).bind(*args)
        except TypeError:
            return 400, None
        except ValueError:                            # pas de signature lisible : l'appel tranchera
            pass
        try:
            resultat = fonction(*args)
            if not isinstance(resultat, str):
                raise TypeError("le résultat n'est pas une chaîne")
            return 200, resultat.encode("utf-8")
        except Exception as e:                       # noqa: BLE001 (toute exception du moteur : 500, notée sans message)
            noter_erreur(outil, fn, e)
            return 500, None

    def sante(self):
        """(code, corps) de /api/sante."""
        version = os.environ.get(VARIABLE_VERSION, "")
        raison = None if VERSION.fullmatch(version) else "version"
        raison = raison or etat_de_la_machine(os.environ.get(VARIABLE_ETAT))
        if raison is None:
            outil, fn, entree = CALCUL_DE_SANTE
            try:
                if json.loads(self.fonction(outil, fn)(entree)).get("ok") is not True:
                    raison = "calcul"
            except Exception as e:                   # noqa: BLE001
                noter_erreur(outil, fn, e)
                raison = "calcul"
        if raison:
            return 503, json.dumps({"ok": False, "raison": raison}).encode("utf-8")
        return 200, json.dumps({"ok": True, "version": version}).encode("utf-8")


application = Application()
