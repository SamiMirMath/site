"""Commandes de test du dépôt (Python seulement, sans dépendance : les tests sont lancés par `uv`).

    python3 tests/lancer.py rapide    # les tests des fichiers modifiés (git) + tests de fumée ; pages à corpus réduit des outils dont
                                      # une page ou un moteur Python chargé par la page (moteur/manifeste.json) est modifié
    python3 tests/lancer.py complet   # toute la suite Python puis toute la suite de pages (parallèles) ; code de retour propagé
    python3 tests/lancer.py python    # toute la suite Python seule
    python3 tests/lancer.py pages     # toute la suite de pages seule (CORPUS=reduit pour le corpus de la CI)
    python3 tests/lancer.py liste     # affiche ce que « rapide » lancerait, sans rien lancer
    python3 tests/lancer.py complet --rapport <dossier>
                                      # comme complet, et écrit en plus dans <dossier> (hors du dépôt, ou ignoré par git) : les deux JUnit
                                      # (python.xml, pages.xml), rapport.json (commit, empreintes des fichiers modifiés ou non suivis,
                                      # codes, durées, tests passés / xfail / sautés, sous-tests, variables CORPUS, OUTILS et MEMO) et les
                                      # listes texte de comparer_listes.py
    python3 tests/lancer.py verifier <dossier> [--reference <dossier>] [--commit <rév>]
                                      # après le commit : contrôle le rapport de `complet --rapport` (empreintes du commit, autres
                                      # fichiers modifiés, codes, tests disparus ou dégradés par rapport à la référence) ; voir verifier.py

Variable PROCESSUS_PAGES (entier ≥ 1) : nombre de processus (Chrome) de la suite de pages, pour rapide, pages et complet ; absente : 2
(Mac de l'enseignant, CI) ; 4 sur le PC. Une valeur invalide arrête la commande avant tout lancement (code 2).

Le code de retour est celui de pytest (0 = tout est vert) : pas de pipe, donc rien n'est masqué (CLAUDE.md). Ce fichier ne s'appelle pas
`test_*.py` : ni pytest ni unittest ne le collectent."""
import datetime
import json
import os
import re
import subprocess
import sys
import time

import comparer_listes
import verifier

RACINE = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DOSSIERS_MOTEURS = ("ensemble-definition", "moteur", "derivee-variations", "limites-asymptotes", "etude-complete", "factorisation",
                    "exponentielles-logarithmes")
# modules lancés quoi qu'on touche : la liste des outils, l'accueil et le manifeste des fichiers chargés par Pyodide
FUMEE_PYTHON = ("test_manifeste.py", "test_accueil.py", "test_source_unique.py")
# dossier d'outil -> nom donné à OUTILS dans les tests de pages
OUTILS_PAGES = {"factorisation": "factorisation", "simplexe": "simplexe", "ensemble-definition": "ensemble-definition",
                "derivee-variations": "derivee-variations", "limites-asymptotes": "limites-asymptotes", "etude-complete": "etude-complete",
                "exponentielles-logarithmes": "exponentielles-logarithmes"}
OUTIL_M = "exponentielles-logarithmes-M"     # filière M de la page des exponentielles (tests/pages/rendu.py) : ses références sont à part
MANIFESTE = "moteur/manifeste.json"          # fichiers Python que chaque page charge dans Pyodide
PROCESSUS_PAGES_DEFAUT = 2                   # suite de pages sans la variable PROCESSUS_PAGES (Mac de l'enseignant, CI)
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


def outils_des_moteurs(modifies):
    """Outils dont la page charge (dans Pyodide) un .py modifié d'un dossier d'outil ou de moteur/, d'après moteur/manifeste.json
    (liste complète et minimale, vérifiée par test_manifeste.py) ; un module partagé donne tous les outils qui le chargent. 'tous' si on
    ne sait pas borner : fichier cité par aucun outil, outil du manifeste inconnu ici, manifeste illisible."""
    moteurs = [n for n in modifies if n.endswith(".py") and n.split("/")[0] in set(DOSSIERS_MOTEURS) | set(OUTILS_PAGES)]
    if not moteurs:
        return set()
    try:
        with open(os.path.join(RACINE, MANIFESTE), encoding="utf-8") as f:
            charges = {outil: set(o["fichiers"]) for outil, o in json.load(f)["outils"].items()}
    except (OSError, ValueError, KeyError, TypeError, AttributeError):
        return {"tous"}
    outils = set()
    for n in moteurs:
        concernes = {outil for outil, fichiers in charges.items() if n in fichiers}
        if not concernes or not concernes <= set(OUTILS_PAGES):
            return {"tous"}
        outils |= {OUTILS_PAGES[o] for o in concernes}
    return outils


def corpus_des_pages():
    """Modules de tests/python que les tests de pages importent, même de loin (corpus des pages : cas.py, cas_el.py…)."""
    modules = {nom: chemin for nom, chemin in modules_du_depot().items() if chemin.startswith("tests/python/")}
    atteints = set()
    for nom in sorted(os.listdir(os.path.join(RACINE, "tests/pages"))):
        if nom.endswith(".py"):
            atteints |= imports(f"tests/pages/{nom}") & set(modules)
    a_lire = list(atteints)
    while a_lire:
        for dep in imports(modules[a_lire.pop()]) & set(modules):
            if dep not in atteints:
                atteints.add(dep)
                a_lire.append(dep)
    return {modules[n] for n in atteints}


def outils_de_pages(modifies):
    """Outils dont une page (HTML, JS, CSS) ou un moteur Python chargé par la page est modifié ; 'tous' si un fichier commun, un test de
    pages ou un module de leur corpus l'est. La page des exponentielles et logarithmes vient avec sa filière M (références à part)."""
    outils = outils_des_moteurs(modifies)
    corpus = corpus_des_pages()
    for n in modifies:
        haut = n.split("/")[0]
        if haut in OUTILS_PAGES and not n.endswith(".py"):
            outils.add(OUTILS_PAGES[haut])
        elif haut in ("commun", "index.html", "moteur") and not n.endswith(".py"):
            outils.add("tous")
        elif n.startswith("tests/pages/") and n.endswith(".py"):
            outils.add("tous")
        elif n in corpus:
            outils.add("tous")
    if "tous" in outils:
        return {"tous"}
    if "exponentielles-logarithmes" in outils:
        outils.add(OUTIL_M)
    return outils


def processus_pages():
    """Nombre de processus de la suite de pages : PROCESSUS_PAGES (entier ≥ 1), 2 si la variable est absente ; ValueError sinon."""
    valeur = os.environ.get("PROCESSUS_PAGES")
    if valeur is None:
        return PROCESSUS_PAGES_DEFAUT
    if not re.fullmatch(r"[1-9][0-9]*", valeur):
        raise ValueError(f"PROCESSUS_PAGES={valeur!r} : un entier ≥ 1 est attendu (par exemple PROCESSUS_PAGES=4), "
                         f"ou la variable absente ({PROCESSUS_PAGES_DEFAUT} processus)")
    return int(valeur)


def lancer(arguments, env=None):
    commande = UV + arguments
    print("$", " ".join(commande), flush=True)
    return subprocess.run(commande, cwd=RACINE, env={**os.environ, **(env or {})}).returncode


def python(fichiers=None, en_plus=()):
    return lancer((fichiers or ["tests/python"]) + ["-n", "auto", "-q", "-p", "no:cacheprovider", "-W", "ignore"] + list(en_plus))


def pages(outils=None, reduit=False, en_plus=()):
    env = {}
    if reduit:
        env["CORPUS"] = "reduit"
    if outils and "tous" not in outils:
        env["OUTILS"] = ",".join(sorted(outils))
    return lancer(["tests/pages", "-n", str(processus_pages()), "--dist", "load", "-q", "-p", "no:cacheprovider", "-W", "ignore"] + list(en_plus), env)


# --- complet --rapport : preuve du lancement (chantier tests-rapides, P0) -------------------------------------------------------

FICHIERS_RAPPORT = ("rapport.json", "python.xml", "pages.xml", "python.json", "pages.json", "collecte-python.txt", "collecte-pages.txt",
                    "resultats-python.txt", "resultats-pages.txt")


def etat_fichiers():
    """{chemin: empreinte `git hash-object`, ou None si supprimé} des fichiers modifiés (indexés ou non) ou non suivis."""
    noms = set(sh("git", "diff", "--name-only", "HEAD").splitlines())
    noms |= set(sh("git", "ls-files", "--others", "--exclude-standard").splitlines())
    presents = sorted(n for n in noms if os.path.isfile(os.path.join(RACINE, n)))
    empreintes = sh("git", "hash-object", "--", *presents).split() if presents else []
    etat = dict(zip(presents, empreintes))
    etat.update({n: None for n in noms if n not in etat})
    return dict(sorted(etat.items()))


def dossier_rapport(chemin):
    """Chemin absolu du dossier du rapport, ou None (message affiché) s'il est dans le dépôt sans être ignoré par git."""
    dossier = os.path.abspath(chemin)
    dans_depot = os.path.commonpath([dossier, RACINE]) == RACINE
    if dans_depot and subprocess.run(["git", "check-ignore", "-q", os.path.join(dossier, "rapport.json")], cwd=RACINE).returncode != 0:
        print(f"--rapport : {dossier} est dans le dépôt sans être ignoré par git ; choisissez un dossier hors du dépôt (ou ignoré)")
        return None
    return dossier


def bilan_suite(dossier, suite, code, duree):
    """Résumé d'une suite pour rapport.json, d'après l'extension `rapport_pytest.py`, recoupé avec le JUnit."""
    chemin_json = os.path.join(dossier, f"{suite}.json")
    if not os.path.exists(chemin_json):
        return {"code": code, "duree_s": round(duree, 1), "lancee": True, "extension": "absente (pytest arrêté avant la fin ?)"}
    with open(chemin_json, encoding="utf-8") as f:
        donnees = json.load(f)
    comparer_listes.ecrire_listes(dossier, suite, donnees)
    par_issue = {}
    for i, issue in donnees["issues"].items():
        par_issue.setdefault(issue, []).append(i)
    sous_tests = {i: sum(c.values()) for i, c in donnees["sous_tests"].items()}
    junit = os.path.join(dossier, f"{suite}.xml")
    return {"code": code, "duree_s": round(duree, 1), "lancee": True, "junit": f"{suite}.xml",
            "ecarts_junit": comparer_listes.ecarts_junit(junit, donnees["issues"]) if os.path.exists(junit) else ["JUnit absent"],
            "collectes": len(donnees["collectes"]), "nombres": {k: len(v) for k, v in sorted(par_issue.items())},
            "sous_tests_total": sum(sous_tests.values()),
            "passes": sorted(par_issue.get("passé", [])), "xfail": sorted(par_issue.get("xfail", [])),
            "sautes": sorted(par_issue.get("sauté", [])),
            "autres": {k: sorted(v) for k, v in sorted(par_issue.items()) if k not in ("passé", "xfail", "sauté")},
            "sous_tests": dict(sorted(sous_tests.items()))}


def complet_avec_rapport(chemin):
    """`complet`, avec les mêmes commandes et le même code de retour, plus le rapport écrit dans le dossier donné."""
    dossier = dossier_rapport(chemin)
    if dossier is None:
        return 2
    os.makedirs(dossier, exist_ok=True)
    for nom in FICHIERS_RAPPORT:                                     # pas de reste d'un lancement précédent
        if os.path.exists(os.path.join(dossier, nom)):
            os.remove(os.path.join(dossier, nom))
    rapport = {"commande": "python3 tests/lancer.py complet --rapport", "head": sh("git", "rev-parse", "HEAD").strip(),
               "branche": sh("git", "rev-parse", "--abbrev-ref", "HEAD").strip(),
               "debut": datetime.datetime.now().astimezone().isoformat(timespec="seconds"), "fichiers_modifies": etat_fichiers(),
               "environnement": {k: os.environ.get(k) for k in ("CORPUS", "OUTILS", "MEMO")}}

    def en_plus(suite):
        return ["-p", "tests.rapport_pytest", f"--rapport-json={os.path.join(dossier, suite + '.json')}",
                f"--junitxml={os.path.join(dossier, suite + '.xml')}"]

    t = time.time()
    code = python(en_plus=en_plus("python"))
    rapport["python"] = bilan_suite(dossier, "python", code, time.time() - t)
    if code:
        rapport["pages"] = {"lancee": False}
    else:
        t = time.time()
        code = pages(en_plus=en_plus("pages"))
        rapport["pages"] = bilan_suite(dossier, "pages", code, time.time() - t)
    rapport["code"] = code
    rapport["fin"] = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
    rapport["fichiers_modifies_fin"] = etat_fichiers()               # pour voir un fichier changé pendant le lancement
    with open(os.path.join(dossier, "rapport.json"), "w", encoding="utf-8") as f:
        json.dump(rapport, f, ensure_ascii=False, indent=1)
    print(f"rapport : {os.path.join(dossier, 'rapport.json')} (code {code})")
    return code


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
    if commande in ("rapide", "pages", "complet"):              # avant tout lancement : pas de suite Python perdue pour rien
        try:
            processus_pages()
        except ValueError as erreur:
            print(f"erreur : {erreur}")
            return 2
    if commande == "rapide":
        return rapide()
    if commande == "liste":
        return rapide(seulement_lister=True)
    if commande == "python":
        return python()
    if commande == "pages":
        return pages(reduit=os.environ.get("CORPUS") == "reduit")
    if commande == "complet":
        if "--rapport" in argv[2:]:
            i = argv.index("--rapport", 2)
            if i + 1 >= len(argv):
                print(__doc__)
                return 2
            return complet_avec_rapport(argv[i + 1])
        code = python()
        return code if code else pages()
    if commande == "verifier":
        return verifier.main(argv[2:])
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
