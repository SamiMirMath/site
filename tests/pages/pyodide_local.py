"""Copie locale de Pyodide pour les tests de pages (T30) : plus de dépendance au CDN pendant les tests.

La copie (Pyodide, SymPy et mpmath, ≈ 18 Mo) est téléchargée une fois dans tests/pages/pyodide-local/ (ignoré par git) :

    python tests/pages/pyodide_local.py            # télécharge si la copie manque (rien à faire sinon)

Le serveur de test redirige alors vers elle les requêtes que les pages adressent à jsDelivr (voir navigateur.py) ; les URL
des pages ne changent pas. La version de la copie doit être celle des pages (moteur/manifeste.json et factorisation/index.html)."""
import json
import os
import re
import sys
import urllib.request

RACINE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DOSSIER = os.path.join(os.path.dirname(__file__), "pyodide-local")
PREFIXE_CDN = "https://cdn.jsdelivr.net/pyodide/"
FICHIERS_BASE = ("pyodide.js", "pyodide.asm.js", "pyodide.asm.wasm", "python_stdlib.zip", "pyodide-lock.json")
PAQUETS = ("sympy",)  # + leurs dépendances (mpmath), lues dans pyodide-lock.json


def versions_des_pages():
    """{version: [fichiers]} pour chaque version de Pyodide écrite dans le manifeste ou dans une page."""
    trouvees = {}
    with open(os.path.join(RACINE, "moteur", "manifeste.json"), encoding="utf-8") as f:
        trouvees.setdefault(json.load(f)["versions"]["pyodide"], []).append("moteur/manifeste.json")
    for dossier, _, noms in os.walk(RACINE):
        if any(p in dossier for p in (".git", "node_modules", "pyodide-local")):
            continue
        for nom in noms:
            if nom.endswith((".html", ".js")):
                chemin = os.path.join(dossier, nom)
                with open(chemin, encoding="utf-8") as f:
                    for v in re.findall(r"cdn\.jsdelivr\.net/pyodide/v([0-9][0-9.]*)/", f.read()):
                        trouvees.setdefault(v, []).append(os.path.relpath(chemin, RACINE))
    return trouvees


def version_attendue():
    v = versions_des_pages()
    if len(v) != 1:
        raise RuntimeError(f"les pages n'utilisent pas une seule version de Pyodide : {v}")
    return next(iter(v))


def _lock(dossier=DOSSIER):
    with open(os.path.join(dossier, "pyodide-lock.json"), encoding="utf-8") as f:
        return json.load(f)


def fichiers_requis(lock):
    paquets, pile = set(), list(PAQUETS)
    while pile:
        n = pile.pop()
        if n not in paquets:
            paquets.add(n)
            pile += lock["packages"][n]["depends"]
    return list(FICHIERS_BASE) + sorted(lock["packages"][n]["file_name"] for n in paquets)


def verifier(dossier=DOSSIER):
    """Lève RuntimeError si la copie manque, est incomplète ou n'a pas la version des pages."""
    attendue = version_attendue()
    if not os.path.exists(os.path.join(dossier, "pyodide-lock.json")):
        raise RuntimeError(f"copie locale de Pyodide absente : lancer  python {os.path.relpath(__file__, RACINE)}")
    version = _lock(dossier)["info"]["version"]
    if version != attendue:
        raise RuntimeError(f"la copie locale est en Pyodide {version}, les pages utilisent {attendue} : "
                           f"supprimer {os.path.relpath(dossier, RACINE)} puis relancer  python {os.path.relpath(__file__, RACINE)}")
    manquants = [n for n in fichiers_requis(_lock(dossier)) if not os.path.exists(os.path.join(dossier, n))]
    if manquants:
        raise RuntimeError(f"copie locale de Pyodide incomplète ({', '.join(manquants)}) : supprimer "
                           f"{os.path.relpath(dossier, RACINE)} puis relancer  python {os.path.relpath(__file__, RACINE)}")


def telecharger(dossier=DOSSIER):
    try:
        verifier(dossier)
        return False
    except RuntimeError as e:
        if "absente" not in str(e) and "incomplète" not in str(e):
            raise
    base = f"{PREFIXE_CDN}v{version_attendue()}/full/"
    os.makedirs(dossier, exist_ok=True)
    # pyodide-lock.json est écrit en dernier : sa présence prouve que la copie est complète
    print("téléchargement", base + "pyodide-lock.json", flush=True)
    octets_lock = _lire(base + "pyodide-lock.json")
    for nom in fichiers_requis(json.loads(octets_lock)):
        if nom != "pyodide-lock.json":
            print("téléchargement", base + nom, flush=True)
            _ecrire(os.path.join(dossier, nom), _lire(base + nom))
    _ecrire(os.path.join(dossier, "pyodide-lock.json"), octets_lock)
    verifier(dossier)
    return True


def _lire(url):
    with urllib.request.urlopen(url, timeout=120) as r:
        return r.read()


def _ecrire(chemin, octets):
    with open(chemin + ".part", "wb") as f:
        f.write(octets)
    os.replace(chemin + ".part", chemin)


if __name__ == "__main__":
    try:
        print("copie téléchargée" if telecharger() else "copie déjà présente et à jour", "→", DOSSIER)
    except RuntimeError as e:
        sys.exit(str(e))
