"""Commandes de test du dépôt (Python seulement, sans dépendance : les tests sont lancés par `uv`).

    python3 tests/lancer.py rapide    # les tests des fichiers modifiés (git) + tests de fumée ; quelques minutes au plus
    python3 tests/lancer.py complet   # toute la suite Python puis toute la suite de pages (parallèles) ; code de retour propagé
    python3 tests/lancer.py python    # toute la suite Python seule
    python3 tests/lancer.py pages     # toute la suite de pages seule (CORPUS=reduit pour le corpus de la CI)
    python3 tests/lancer.py liste     # affiche ce que « rapide » lancerait, sans rien lancer

Le code de retour est celui de pytest (0 = tout est vert) : pas de pipe, donc rien n'est masqué (CLAUDE.md). Ce fichier ne s'appelle pas
`test_*.py` : ni pytest ni unittest ne le collectent."""
import os
import re
import subprocess
import sys

RACINE = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DOSSIERS_MOTEURS = ("ensemble-definition", "moteur", "derivee-variations", "limites-asymptotes", "etude-complete", "factorisation",
                    "exponentielles-logarithmes")
# modules lancés quoi qu'on touche : la liste des outils, l'accueil et le manifeste des fichiers chargés par Pyodide
FUMEE_PYTHON = ("test_manifeste.py", "test_accueil.py", "test_source_unique.py")
# dossier d'outil -> nom donné à OUTILS dans les tests de pages
OUTILS_PAGES = {"factorisation": "factorisation", "simplexe": "simplexe", "ensemble-definition": "ensemble-definition",
                "derivee-variations": "derivee-variations", "limites-asymptotes": "limites-asymptotes", "etude-complete": "etude-complete",
                "exponentielles-logarithmes": "exponentielles-logarithmes"}
UV = ["uv", "run", "-q", "--no-project", "--python", "3.12", "--with", "sympy==1.13.3", "--with", "mpmath==1.3.0",
      "--with", "websockets", "--with", "pytest", "--with", "pytest-xdist", "python", "-m", "pytest"]


def sh(*args):
    return subprocess.run(args, cwd=RACINE, capture_output=True, text=True, check=True).stdout


def fichiers_modifies():
    """Fichiers modifiés (indexés ou non) et non suivis, chemins relatifs à la racine."""
    noms = set(sh("git", "diff", "--name-only", "HEAD").split())
    noms |= set(sh("git", "ls-files", "--others", "--exclude-standard").split())
    return sorted(n for n in noms if os.path.exists(os.path.join(RACINE, n)))


def modules_du_depot():
    """{nom de module: chemin relatif} pour les .py des moteurs et des tests Python (les noms sont uniques dans le dépôt)."""
    modules = {}
    for dossier in DOSSIERS_MOTEURS + ("tests/python",):
        for nom in sorted(os.listdir(os.path.join(RACINE, dossier))):
            if nom.endswith(".py"):
                modules.setdefault(nom[:-3], f"{dossier}/{nom}")
    return modules


def imports(chemin):
    """Modules importés (lecture du texte, pas de l'arbre : le script se lance avec n'importe quel Python 3)."""
    with open(os.path.join(RACINE, chemin), encoding="utf-8") as f:
        return set(re.findall(r"^\s*(?:import|from)\s+(\w+)", f.read(), re.MULTILINE))


def tests_python_concernes(modifies):
    """Les test_*.py modifiés, et ceux qui importent (même de loin) un module modifié."""
    modules = modules_du_depot()
    dependances = {nom: imports(chemin) & set(modules) for nom, chemin in modules.items()}
    touches = {nom for nom, chemin in modules.items() if chemin in modifies}
    atteints = set(touches)
    change = True
    while change:
        change = False
        for nom, deps in dependances.items():
            if nom not in atteints and deps & atteints:
                atteints.add(nom)
                change = True
    tests = {modules[n] for n in atteints if modules[n].startswith("tests/python/test_")}
    tests |= {f"tests/python/{n}" for n in FUMEE_PYTHON}
    # un test qui lit un fichier du dépôt (page, JSON) sans l'importer : toute page ou tout JSON modifié relance la fumée seule
    return sorted(tests)


def outils_de_pages(modifies):
    """Outils dont une page (HTML, JS, CSS) est modifiée ; 'tous' si un fichier commun l'est."""
    outils = set()
    for n in modifies:
        haut = n.split("/")[0]
        if haut in OUTILS_PAGES and not n.endswith(".py"):
            outils.add(OUTILS_PAGES[haut])
        elif haut in ("commun", "index.html", "moteur") and not n.endswith(".py"):
            outils.add("tous")
        elif n.startswith("tests/pages/") and n.endswith(".py"):
            outils.add("tous")
    return outils


def lancer(arguments, env=None):
    commande = UV + arguments
    print("$", " ".join(commande), flush=True)
    return subprocess.run(commande, cwd=RACINE, env={**os.environ, **(env or {})}).returncode


def python(fichiers=None):
    return lancer((fichiers or ["tests/python"]) + ["-n", "auto", "-q", "-p", "no:cacheprovider", "-W", "ignore"])


def pages(outils=None, reduit=False):
    env = {}
    if reduit:
        env["CORPUS"] = "reduit"
    if outils and "tous" not in outils:
        env["OUTILS"] = ",".join(sorted(outils))
    return lancer(["tests/pages", "-n", "2", "--dist", "load", "-q", "-p", "no:cacheprovider", "-W", "ignore"], env)


def rapide(seulement_lister=False):
    modifies = fichiers_modifies()
    tests = tests_python_concernes(modifies)
    outils = outils_de_pages(modifies)
    print("fichiers modifiés :", ", ".join(modifies) or "aucun")
    print("tests Python :", ", ".join(os.path.basename(t) for t in tests))
    print("pages (corpus réduit) :", ", ".join(sorted(outils)) or "aucune")
    if seulement_lister:
        return 0
    code = python(tests)
    if code == 0 and outils:
        code = pages(outils, reduit=True)
    return code


def main(argv):
    commande = argv[1] if len(argv) > 1 else ""
    if commande == "rapide":
        return rapide()
    if commande == "liste":
        return rapide(seulement_lister=True)
    if commande == "python":
        return python()
    if commande == "pages":
        return pages(reduit=os.environ.get("CORPUS") == "reduit")
    if commande == "complet":
        code = python()
        return code if code else pages()
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
