"""Liste blanche des fichiers publics du site (chantier moteur-serveur, P1 ; decisions.md, T4). Utilisée en P6 par le script de mise
en ligne, qui construit le dossier web ; vérifiée dès P1 par tests/python/test_serveur.py sur l'arbre du dépôt.

Source : `git ls-files` (les fichiers suivis, jamais le disque : ni __pycache__, ni fichier non suivi). Un fichier est public s'il a
l'extension .html, .css ou .js et s'il est `index.html` (l'accueil), ou dans commun/, ou dans le dossier d'une page du registre
(commun/registre.json, `chemin`). Aucun chemin qui passe par un dossier caché ou par __pycache__. Le registre ne peut pas désigner un
dossier interdit (moteur/, docs/, tests/, serveur/, .github/) ni un dossier à plusieurs niveaux : ValueError.

Bibliothèque standard seule (A10, test_imports.py)."""
import json
import os
import subprocess

EXTENSIONS = (".html", ".css", ".js")
ACCUEIL = "index.html"
COMMUN = "commun"
REGISTRE = "commun/registre.json"
INTERDITS = frozenset({"moteur", "docs", "tests", "serveur", ".github"})


def dossiers_des_pages(racine):
    """Dossiers des pages du registre (`chemin` sans « / »), vérifiés."""
    with open(os.path.join(racine, REGISTRE), encoding="utf-8") as f:
        chemins = [o["chemin"] for o in json.load(f)["outils"]]
    dossiers = []
    for chemin in chemins:
        d = chemin.rstrip("/")
        if not d or "/" in d or d.startswith(".") or d in INTERDITS or d == "__pycache__":
            raise ValueError(f"chemin du registre refusé pour la liste publique : {chemin!r}")
        dossiers.append(d)
    return dossiers


def est_public(chemin, dossiers):
    """Vrai si le fichier suivi `chemin` (relatif à la racine, séparateur « / ») est publié ; `dossiers` : commun et les pages."""
    parties = chemin.split("/")
    if any(p.startswith(".") or p == "__pycache__" for p in parties) or not chemin.endswith(EXTENSIONS):
        return False
    if chemin == ACCUEIL:
        return True
    return len(parties) > 1 and parties[0] in dossiers and parties[0] not in INTERDITS


def fichiers_publics(racine):
    """Fichiers publics, triés : `git ls-files -z` de `racine`, filtrés par est_public."""
    sortie = subprocess.run(["git", "ls-files", "-z"], cwd=racine, capture_output=True, check=True).stdout
    dossiers = {COMMUN} | set(dossiers_des_pages(racine))
    return sorted(n for n in (os.fsdecode(b) for b in sortie.split(b"\0") if b) if est_public(n, dossiers))
