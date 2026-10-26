"""Construit les roues précompilées de SymPy et mpmath (T32) : mêmes fichiers que les roues officielles de Pyodide, mais avec le bytecode
(.pyc) à la place du source (.py) pour les modules que `import sympy` charge. Python n'a alors plus à les compiler à chaque ouverture de page :
`import sympy` passe d'environ 5 s à moins de 1 s sur un ordinateur, d'environ 20 s à 3 s sur un téléphone (voir docs/choix-techniques.md D13).

    uv run -q --no-project --python 3.12 --with sympy==1.13.3 python moteur/construire_roues.py

À relancer seulement quand la version de SymPy ou de mpmath change dans moteur/manifeste.json, ou quand Pyodide change de version de Python
(le « numéro magique » du bytecode est alors différent : la page retombe sur les roues du CDN tant que la bande n'est pas reconstruite).
Écrit moteur/roues/*.zip (nom = version + 8 premiers caractères du SHA-256, jamais deux contenus sous un même nom) et la clé « roues » du manifeste.
tests/python/test_roues.py vérifie que les roues viennent bien de ce SymPy-là."""
import hashlib
import importlib.util
import io
import json
import os
import py_compile
import re
import sys
import tempfile
import urllib.request
import zipfile

RACINE = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DOSSIER = os.path.join(RACINE, "moteur", "roues")
COPIE_LOCALE = os.path.join(RACINE, "tests", "pages", "pyodide-local")
DATE = (1980, 1, 1, 0, 0, 0)


def lire_manifeste():
    with open(os.path.join(RACINE, "moteur", "manifeste.json"), encoding="utf-8") as f:
        return json.load(f)


def roue_officielle(paquet, version_pyodide):
    """Octets de la roue officielle (copie de test si elle est là, sinon jsDelivr ; SHA-256 du pyodide-lock.json dans les deux cas)."""
    base = f"https://cdn.jsdelivr.net/pyodide/v{version_pyodide}/full/"
    chemin_lock = os.path.join(COPIE_LOCALE, "pyodide-lock.json")
    if os.path.isfile(chemin_lock):
        with open(chemin_lock, encoding="utf-8") as f:
            lock = json.load(f)
    else:
        with urllib.request.urlopen(base + "pyodide-lock.json", timeout=60) as r:
            lock = json.load(r)
    info = lock["packages"][paquet]
    local = os.path.join(COPIE_LOCALE, info["file_name"])
    if os.path.isfile(local):
        with open(local, "rb") as f:
            octets = f.read()
    else:
        with urllib.request.urlopen(base + info["file_name"], timeout=300) as r:
            octets = r.read()
    if hashlib.sha256(octets).hexdigest() != info["sha256"]:
        raise RuntimeError(f"{info['file_name']} : SHA-256 différent de celui de pyodide-lock.json")
    return octets, info["version"]


def modules_charges_par_import_sympy():
    import sympy  # noqa: F401
    return {m for m in sys.modules if m == "sympy" or m.startswith("sympy.")}


def nom_du_module(chemin):
    m = chemin[:-3].replace("/", ".")
    return m[: -len(".__init__")] if m.endswith(".__init__") else m


def precompiler(octets_roue, a_compiler):
    """Roue réécrite : les .py dont `a_compiler(module)` est vrai deviennent des .pyc sans contrôle de date (UNCHECKED_HASH) ; le reste est copié."""
    sortie = io.BytesIO()
    with zipfile.ZipFile(io.BytesIO(octets_roue)) as zin, zipfile.ZipFile(sortie, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as zout, \
            tempfile.TemporaryDirectory() as tmp:
        for info in zin.infolist():
            donnees = zin.read(info.filename)
            if info.filename.endswith(".py") and a_compiler(nom_du_module(info.filename)):
                src, cible = os.path.join(tmp, "m.py"), os.path.join(tmp, "m.pyc")
                with open(src, "wb") as f:
                    f.write(donnees)
                py_compile.compile(src, cfile=cible, dfile=info.filename, doraise=True,
                                   invalidation_mode=py_compile.PycInvalidationMode.UNCHECKED_HASH)
                with open(cible, "rb") as f:
                    donnees = f.read()
                nom = info.filename[:-3] + ".pyc"
            else:
                nom = info.filename
            zi = zipfile.ZipInfo(nom, DATE)
            zi.compress_type = zipfile.ZIP_DEFLATED
            zi.external_attr = 0o644 << 16
            zout.writestr(zi, donnees)
    return sortie.getvalue()


def main():
    if sys.version_info[:2] != (3, 12):
        sys.exit(f"Python 3.12 requis (le bytecode doit être celui de Pyodide), pas {sys.version}")
    manifeste = lire_manifeste()
    v = manifeste["versions"]
    import sympy
    if sympy.__version__ != v["sympy"]:
        sys.exit(f"SymPy installé {sympy.__version__} ≠ manifeste {v['sympy']} : relancer avec --with sympy=={v['sympy']}")
    charges = modules_charges_par_import_sympy()
    os.makedirs(DOSSIER, exist_ok=True)
    fichiers = []
    for paquet, regle in (("mpmath", lambda m: True), ("sympy", lambda m: m in charges)):
        octets, version = roue_officielle(paquet, v["pyodide"])
        if version != v[paquet]:
            sys.exit(f"{paquet} {version} dans pyodide-lock.json ≠ manifeste {v[paquet]}")
        roue = precompiler(octets, regle)
        nom = f"{paquet}-{version}-pyc312-{hashlib.sha256(roue).hexdigest()[:8]}.zip"
        with open(os.path.join(DOSSIER, nom), "wb") as f:
            f.write(roue)
        fichiers.append("moteur/roues/" + nom)
        with zipfile.ZipFile(io.BytesIO(roue)) as z:       # les licences accompagnent les roues (BSD : à redistribuer avec le code)
            for fichier in z.namelist():
                base = fichier.rsplit("/", 1)[-1]
                if ".dist-info/" in fichier and base in ("LICENSE", "AUTHORS"):
                    with open(os.path.join(DOSSIER, f"{base}-{paquet}.txt"), "wb") as f:
                        f.write(z.read(fichier))
        print(f"{nom} : {round(len(octets) / 1e6, 2)} Mo -> {round(len(roue) / 1e6, 2)} Mo")
    for ancien in os.listdir(DOSSIER):
        if ancien.endswith(".zip") and "moteur/roues/" + ancien not in fichiers:
            os.remove(os.path.join(DOSSIER, ancien))
    ligne = '  "roues": ' + json.dumps({"pyc": importlib.util.MAGIC_NUMBER.hex(), "fichiers": fichiers}, ensure_ascii=False) + ","
    chemin = os.path.join(RACINE, "moteur", "manifeste.json")
    with open(chemin, encoding="utf-8") as f:
        texte = f.read()
    if re.search(r'^  "roues": .*$', texte, re.M):
        texte = re.sub(r'^  "roues": .*$', lambda _: ligne, texte, flags=re.M)
    else:
        texte = texte.replace('  "outils": {', ligne + '\n  "outils": {', 1)       # une ligne : le reste du manifeste garde sa mise en forme
    with open(chemin, "w", encoding="utf-8") as f:
        f.write(texte)

if __name__ == "__main__":
    main()
