"""Copie locale de KaTeX pour les tests de pages (chantier fondations, F6) : plus aucune requête vers jsDelivr pendant les tests.

La copie (les fichiers de KaTeX que les pages demandent, et les polices que nomme sa feuille de style, ≈ 1,5 Mo) est téléchargée une fois
dans tests/pages/katex-local/ (ignoré par git), sur le modèle de pyodide_local.py :

    python3 tests/pages/katex_local.py            # télécharge si la copie manque (rien à faire sinon)

Le serveur de test redirige alors vers elle les requêtes que les pages adressent à https://cdn.jsdelivr.net/npm/katex@<version>/
(voir navigateur.py) ; les URL des pages ne changent pas. La version et les fichiers sont lus dans les pages elles-mêmes.

Intégrité : le paquet npm de cette version (registry.npmjs.org) est vérifié par l'empreinte SHA-512 que publie le registre ; chaque fichier
qui en est extrait doit avoir l'empreinte SHA-256 que jsDelivr donne pour ce fichier (data.jsdelivr.com), donc les octets servis aux tests
sont exactement ceux que jsDelivr sert aux élèves. Les empreintes sont gardées dans la copie (empreintes.json, écrit en dernier : sa
présence prouve que la copie est complète) et revérifiées par verifier() à chaque processus de test."""
import base64
import gzip
import hashlib
import io
import json
import os
import re
import sys
import tarfile

from pyodide_local import _ecrire, _lire

RACINE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DOSSIER = os.path.join(os.path.dirname(__file__), "katex-local")
PREFIXE_CDN = "https://cdn.jsdelivr.net/npm/katex@"
EMPREINTES = "empreintes.json"
EXCLUS = (".git", "node_modules", "docs", "tests")        # archives de chantier (docs/) et tests : pas des pages servies aux élèves
COMMANDE = f"python3 {os.path.relpath(__file__, RACINE)}"


def references_des_pages(racine=RACINE):
    """{version: {chemin dans le paquet: [fichiers qui le demandent]}} pour chaque URL jsDelivr de KaTeX écrite dans une page (.html, .js, .css)."""
    trouvees = {}
    for dossier, sous, noms in os.walk(racine):
        if os.path.relpath(dossier, racine) == ".":
            sous[:] = [s for s in sous if s not in EXCLUS]
        for nom in noms:
            if nom.endswith((".html", ".js", ".css")):
                chemin = os.path.join(dossier, nom)
                with open(chemin, encoding="utf-8") as f:
                    for v, fichier in re.findall(r"cdn\.jsdelivr\.net/npm/katex@([0-9][0-9.]*)/([^\"'\s)?#>]+)", f.read()):
                        trouvees.setdefault(v, {}).setdefault(fichier, []).append(os.path.relpath(chemin, racine))
    return trouvees


def version_attendue(racine=RACINE):
    v = references_des_pages(racine)
    if len(v) != 1:
        raise RuntimeError(f"les pages n'utilisent pas une seule version de KaTeX : {sorted(v)}")
    return next(iter(v))


def polices_de_la_feuille(chemin_css, contenu):
    """Chemins (dans le paquet) des fichiers que la feuille de style nomme par url(…) relatif : les polices de KaTeX."""
    base = os.path.dirname(chemin_css)
    chemins = set()
    for url in re.findall(r"url\(\s*['\"]?([^'\")]+)['\"]?\s*\)", contenu):
        if re.match(r"^[a-z]+:|^/|^#", url):
            raise RuntimeError(f"{chemin_css} : url({url}) n'est pas relative au paquet")
        chemin = os.path.normpath(os.path.join(base, url.split("?")[0].split("#")[0])).replace(os.sep, "/")
        if chemin.startswith(".."):
            raise RuntimeError(f"{chemin_css} : url({url}) sort du paquet")
        chemins.add(chemin)
    return chemins


def lire_empreintes(dossier=DOSSIER):
    with open(os.path.join(dossier, EMPREINTES), encoding="utf-8") as f:
        return json.load(f)


def sha256(octets):
    return hashlib.sha256(octets).hexdigest()


def verifier(dossier=DOSSIER, racine=RACINE):
    """Lève RuntimeError si la copie manque, n'a pas la version des pages, n'a pas un fichier que les pages demandent, ou si un fichier
    n'a plus l'empreinte enregistrée au téléchargement. Rend le contenu d'empreintes.json."""
    attendue = version_attendue(racine)
    relancer = f"supprimer {os.path.relpath(dossier, RACINE)} puis relancer  {COMMANDE}"
    if not os.path.exists(os.path.join(dossier, EMPREINTES)):
        raise RuntimeError(f"copie locale de KaTeX absente : lancer  {COMMANDE}")
    e = lire_empreintes(dossier)
    if e["version"] != attendue:
        raise RuntimeError(f"la copie locale est en KaTeX {e['version']}, les pages utilisent {attendue} : {relancer}")
    manquants = sorted(set(references_des_pages(racine)[attendue]) - set(e["fichiers"]))
    for chemin, empreinte in sorted(e["fichiers"].items()):
        complet = os.path.join(dossier, chemin)
        if not os.path.isfile(complet):
            manquants.append(chemin)
        else:
            with open(complet, "rb") as f:
                if sha256(f.read()) != empreinte:
                    manquants.append(f"{chemin} (empreinte différente)")
    if manquants:
        raise RuntimeError(f"copie locale de KaTeX incomplète ({', '.join(manquants)}) : {relancer}")
    return e


def _sha512_npm(integrite):
    """Vérification d'un paquet par son champ `integrity` du registre npm (« sha512-<base64> »)."""
    if not integrite.startswith("sha512-"):
        raise RuntimeError(f"empreinte npm inattendue : {integrite}")
    attendue = base64.b64decode(integrite[len("sha512-"):])

    def verification(octets):
        if hashlib.sha512(octets).digest() != attendue:
            raise OSError("empreinte SHA-512 différente de celle du registre npm")
        gzip.decompress(octets)                       # archive lisible jusqu'au bout
    return verification


def telecharger(dossier=DOSSIER, racine=RACINE):
    try:
        verifier(dossier, racine)
        return False
    except RuntimeError as e:
        if "absente" not in str(e) and "incomplète" not in str(e):
            raise
    version = version_attendue(racine)
    demandes = set(references_des_pages(racine)[version])
    meta_url = f"https://registry.npmjs.org/katex/{version}"
    print("téléchargement", meta_url, flush=True)
    meta = json.loads(_lire(meta_url, verification=json.loads))
    if meta.get("version") != version:
        raise RuntimeError(f"le registre npm répond {meta.get('version')} pour KaTeX {version}")
    print("téléchargement", meta["dist"]["tarball"], flush=True)
    paquet = _lire(meta["dist"]["tarball"], verification=_sha512_npm(meta["dist"]["integrity"]))
    api = f"https://data.jsdelivr.com/v1/packages/npm/katex@{version}?structure=flat"
    print("téléchargement", api, flush=True)
    jsdelivr = {f["name"].lstrip("/"): f["hash"] for f in json.loads(_lire(api, verification=json.loads))["files"]}

    contenus = {}
    with tarfile.open(fileobj=io.BytesIO(paquet), mode="r:gz") as archive:
        def extraire(chemin):
            membre = archive.getmember("package/" + chemin)      # KeyError si le paquet ne l'a pas
            if not membre.isfile():
                raise RuntimeError(f"{chemin} n'est pas un fichier du paquet")
            octets = archive.extractfile(membre).read()
            if chemin not in jsdelivr:
                raise RuntimeError(f"{chemin} : jsDelivr ne donne pas d'empreinte pour ce fichier")
            if base64.b64encode(hashlib.sha256(octets).digest()).decode() != jsdelivr[chemin]:
                raise RuntimeError(f"{chemin} : les octets du paquet npm diffèrent de ceux que sert jsDelivr")
            contenus[chemin] = octets
        try:
            for chemin in sorted(demandes):
                extraire(chemin)
                if chemin.endswith(".css"):
                    for police in sorted(polices_de_la_feuille(chemin, contenus[chemin].decode("utf-8"))):
                        extraire(police)
        except KeyError as e:
            raise RuntimeError(f"fichier absent du paquet KaTeX {version} : {e}")

    for chemin, octets in sorted(contenus.items()):
        complet = os.path.join(dossier, *chemin.split("/"))
        os.makedirs(os.path.dirname(complet), exist_ok=True)
        _ecrire(complet, octets)
    # empreintes.json en dernier : sa présence prouve que la copie est complète
    _ecrire(os.path.join(dossier, EMPREINTES), json.dumps(
        {"version": version, "paquet": meta["dist"]["tarball"], "integrite_npm": meta["dist"]["integrity"],
         "fichiers": {c: sha256(o) for c, o in sorted(contenus.items())}}, indent=1, ensure_ascii=False).encode("utf-8"))
    verifier(dossier, racine)
    return True


if __name__ == "__main__":
    try:
        print("copie téléchargée" if telecharger() else "copie déjà présente et à jour", "→", DOSSIER)
    except RuntimeError as e:
        sys.exit(str(e))
