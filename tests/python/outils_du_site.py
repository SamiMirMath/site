"""La liste des outils du site, seule source des listes d'outils des tests (chantier fondations, F3 ; revue de structure, R1 ;
docs/architecture.md, règle A3).

Deux sources, déjà vérifiées par leurs propres tests :
- commun/registre.json : toutes les pages d'outil, dans l'ordre de l'accueil (test_accueil.py : l'accueil, les dossiers à index.html) ;
- moteur/manifeste.json : les outils à moteur Python chargé par Pyodide, dans l'ordre du manifeste (test_manifeste.py : complet et
  minimal ; le simplexe n'y est pas, il n'a pas de moteur Python).

Sans dépendance (json, os, urllib.parse) : tests/lancer.py le charge par son chemin avec n'importe quel Python 3 ; les tests Python et
les tests de pages l'importent (tests/python est sur leur chemin). Chaque fonction relit les fichiers (`racine` : la racine du dépôt,
celle de ce fichier par défaut ; lancer.py passe la sienne).

Une donnée propre à un outil (exemple, entrée invalide, corpus réduit…) reste écrite à la main dans son test, dans un dictionnaire
dont les clés sont vérifiées par tests/python/test_outils_du_site.py et tests/pages/test_donnees_des_pages.py : un outil oublié ou en
trop fait échouer un test."""
import json
import os
from urllib.parse import parse_qs

RACINE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
REGISTRE = "commun/registre.json"
MANIFESTE = "moteur/manifeste.json"


def lire(chemin, racine=RACINE):
    with open(os.path.join(racine, chemin), encoding="utf-8") as f:
        return json.load(f)


def registre(racine=RACINE):
    """Les entrées du registre (liste de dictionnaires : id, chemin, titre, filieres…), dans l'ordre de l'accueil."""
    return lire(REGISTRE, racine)["outils"]


def manifeste(racine=RACINE):
    """{outil: entrée du manifeste (module, fichiers, fonctions…)}, dans l'ordre du manifeste."""
    return lire(MANIFESTE, racine)["outils"]


def outils(racine=RACINE):
    """Ids de toutes les pages d'outil (registre), dans l'ordre du registre."""
    return [o["id"] for o in registre(racine)]


def outils_pyodide(racine=RACINE):
    """Ids des outils à moteur Python (manifeste), dans l'ordre du manifeste : les pages construites par monterOutil
    (commun/outil.js)."""
    return list(manifeste(racine))


def pages(racine=RACINE):
    """{dossier de la page: id de l'outil} pour chaque outil du registre (le dossier est le chemin sans « / »)."""
    return {o["chemin"].rstrip("/"): o["id"] for o in registre(racine)}


def dossiers_moteurs(racine=RACINE):
    """Dossiers des fichiers Python que les pages chargent (manifeste), dans l'ordre de leur première apparition (outils dans l'ordre
    du manifeste, fichiers dans l'ordre de chaque outil). tests/python/moteurs.py les insère un à un en tête de sys.path, dans cet
    ordre (le dernier se retrouve donc en premier) : le changer change l'ordre de sys.path (test_outils_du_site.py le vérifie)."""
    dossiers = []
    for o in manifeste(racine).values():
        for chemin in o["fichiers"]:
            d = os.path.dirname(chemin)
            if d not in dossiers:
                dossiers.append(d)
    return dossiers


def filieres(outil, racine=RACINE):
    """Filières à part d'un outil : les valeurs de `filiere` des « parametres » du registre (?filiere=M), triées ; [] sans
    paramètre."""
    entree = next(o for o in registre(racine) if o["id"] == outil)
    valeurs = set()
    for requete in entree.get("parametres", {}).values():
        valeurs |= set(parse_qs(requete.lstrip("?")).get("filiere", []))
    return sorted(valeurs)


def variantes(racine=RACINE):
    """{nom de variante: outil} des pages ouvertes avec une filière à part (`<outil>-<filière>`, par exemple
    exponentielles-logarithmes-M) : leurs instantanés resoudre et leurs références de pages sont dans des fichiers à part."""
    return {f"{o}-{f}": o for o in outils(racine) for f in filieres(o, racine)}


def nom_de_test(nom):
    """Nom de la méthode de test d'un outil ou d'une variante, là où il y en a une par outil (test_instantanes*.py, test_rendu.py) :
    test_<outil> ; test_<outil>_filiere_<f> pour la variante <outil>-<F>."""
    for variante, outil in variantes().items():
        if nom == variante:
            return "test_" + outil.replace("-", "_") + "_filiere_" + nom[len(outil) + 1:].lower()
    return "test_" + nom.replace("-", "_")
