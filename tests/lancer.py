"""Commandes de test du dépôt (Python seulement, sans dépendance : les tests sont lancés par `uv`).

    python3 tests/lancer.py rapide    # les tests des fichiers modifiés (git) + tests de fumée ; pages à corpus réduit des outils dont
                                      # une page ou un moteur Python chargé par la page (moteur/manifeste.json) est modifié ; règles
                                      # détaillées ci-dessous
    python3 tests/lancer.py complet   # toute la suite Python puis toute la suite de pages (parallèles) ; code de retour propagé
    python3 tests/lancer.py python    # toute la suite Python seule
    python3 tests/lancer.py pages     # toute la suite de pages seule (CORPUS=reduit pour le corpus de la CI)
    python3 tests/lancer.py liste     # affiche ce que « rapide » lancerait, sans rien lancer
    python3 tests/lancer.py rapide --depuis <commit>
                                      # (ou liste --depuis) les fichiers modifiés depuis <commit> (par exemple HEAD~1) au lieu de HEAD :
                                      # changements commités depuis ce commit, plus ceux de l'arbre et les non suivis ; pour le contrôle
                                      # du chef d'orchestre après un commit
    python3 tests/lancer.py complet --rapport <dossier>
                                      # comme complet, et écrit en plus dans <dossier> (hors du dépôt, ou ignoré par git) : les deux JUnit
                                      # (python.xml, pages.xml), rapport.json (commit, empreintes des fichiers modifiés ou non suivis,
                                      # codes, durées, tests passés / xfail / sautés, sous-tests, variables CORPUS, OUTILS et MEMO) et les
                                      # listes texte de comparer_listes.py
    python3 tests/lancer.py verifier <dossier> [--reference <dossier>] [--commit <rév>] [--suivi <fichier>]
                                      # après le commit : contrôle le rapport de `complet --rapport` (empreintes du commit, autres
                                      # fichiers modifiés hors docs/ et CLAUDE.md, codes, tests disparus, échoués ou sautés en plus par
                                      # rapport à la référence, sous-tests en baisse non justifiés dans le suivi.md du chantier, section
                                      # « Variations de sous-tests ») ; voir verifier.py
    python3 tests/lancer.py reference <dossier>
                                      # remplace la référence du dépôt (tests/reference, celle de verifier) par les listes de <dossier>,
                                      # écrit par `complet --rapport` sur un commit de la branche, vert, complet, sans autre fichier modifié
                                      # que dans docs/ ou CLAUDE.md ; jamais automatique : à lancer au P0 de chaque chantier, puis à commiter

Ce que `rapide` relance (et que `liste` affiche). Fichiers : `git diff --name-only --no-renames -z <commit>` (HEAD, ou --depuis) et
`git ls-files --others --exclude-standard -z`, découpés sur \\0 (noms à espaces ou non ASCII tels quels), fichiers supprimés compris
(marqués « supprimé » ; un fichier déplacé donne son ancien et son nouveau chemin). Tests Python (tests_python_concernes) : les test_*.py
modifiés, ceux qui importent même de loin un module modifié ou supprimé des moteurs, de tests/python ou de tests/python/donnees ; ceux
qui lisent par son chemin un fichier modifié ou supprimé de tests/python/donnees, tests/python/instantanes ou tests/pages/references
(modules dont une chaîne nomme ce dossier, puis leurs dépendants ; tous les tests Python si aucun ne le nomme) ; test_instantanes*.py et
test_json_strict.py quand une page d'outil, un cas*.py ou un instantané change ; test_lancer.py quand un script de commande change
(lancer.py, verifier.py, comparer_listes.py, rapport_pytest.py, outils_du_site.py) ; test_imports.py et test_noyau.py quand un .py des
dossiers des moteurs change (ils le lisent par son chemin) ; les dépendants de tests/python/outils_du_site.py
quand moteur/manifeste.json ou commun/registre.json change (les listes d'outils des tests et de ce script en dérivent) ; toujours les
tests de fumée. Pages, corpus réduit (outils_de_pages) : l'outil dont la page, un moteur Python chargé par la page
(moteur/manifeste.json), la référence de page (tests/pages/references/<outil>.json) ou l'instantané resoudre (lu par
test_comportement.py) change, avec ses variantes de filière (registre : la filière M pour les exponentielles) ; toutes les pages pour un
fichier commun, un autre fichier de tests/pages ou un module du corpus des pages (cas.py, cas_el.py…), ou si on ne sait pas borner (liste
des outils illisible comprise). Dans le doute, on élargit, jamais on ne réduit ; `rapide` ne remplace pas `complet` avant
un commit.

Variable PROCESSUS_PAGES (entier ≥ 1) : nombre de processus (Chrome) de la suite de pages, pour rapide, pages et complet ; absente : 2
(Mac de l'enseignant, CI) ; 4 sur le PC. Une valeur invalide arrête la commande avant tout lancement (code 2).

Le code de retour est celui de pytest (0 = tout est vert) : pas de pipe, donc rien n'est masqué (CLAUDE.md). Ce fichier ne s'appelle pas
`test_*.py` : ni pytest ni unittest ne le collectent."""
import datetime
import glob
import importlib.util
import json
import os
import re
import subprocess
import sys
import time

import comparer_listes
import verifier

RACINE = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
# la liste des outils (chantier fondations, F3) : tests/python/outils_du_site.py, chargé par son chemin (sys.path inchangé), lit
# moteur/manifeste.json et commun/registre.json ; une modification de l'un d'eux relance les dépendants de ce module
MODULE_DES_OUTILS = "outils_du_site"
SOURCES_DES_OUTILS = ("moteur/manifeste.json", "commun/registre.json")


def charger_outils_du_site():
    chemin = os.path.join(RACINE, "tests", "python", MODULE_DES_OUTILS + ".py")
    spec = importlib.util.spec_from_file_location(MODULE_DES_OUTILS, chemin)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


# DOSSIERS_MOTEURS : dossiers des fichiers Python chargés par les pages (manifeste), dans l'ordre du manifeste ; OUTILS_PAGES : dossier
# d'outil -> nom donné à OUTILS dans les tests de pages (registre) ; VARIANTES : page ouverte avec une filière à part (références et
# instantané resoudre à part, par exemple exponentielles-logarithmes-M) -> outil. Liste illisible (manifeste ou registre absent ou
# invalide) : listes vides et LISTES_ILLISIBLES ; `rapide` relance alors tout (seuls verifier, reference et complet s'en passent).
try:
    outils_du_site = charger_outils_du_site()
    DOSSIERS_MOTEURS = tuple(outils_du_site.dossiers_moteurs(RACINE))
    OUTILS_PAGES = outils_du_site.pages(RACINE)
    VARIANTES = outils_du_site.variantes(RACINE)
    LISTES_ILLISIBLES = None
except (OSError, ValueError, KeyError, TypeError, AttributeError, StopIteration) as erreur_des_listes:
    outils_du_site, DOSSIERS_MOTEURS, OUTILS_PAGES, VARIANTES = None, (), {}, {}
    LISTES_ILLISIBLES = f"liste des outils illisible ({type(erreur_des_listes).__name__} : {erreur_des_listes})"
# modules lancés quoi qu'on touche : la liste des outils, l'accueil et le manifeste des fichiers chargés par Pyodide
FUMEE_PYTHON = ("test_manifeste.py", "test_accueil.py", "test_source_unique.py")
DOSSIERS_TESTS_PYTHON = ("tests/python", "tests/python/donnees")   # modules des tests Python (donnees/ : corpus de l'enseignant)
TOUS_LES_TESTS_PYTHON = "tests/python"
# fichiers lus par leur chemin, sans import : dossier -> élément de chemin cherché dans les chaînes des modules qui les lisent
LUS_PAR_CHEMIN = {"tests/python/donnees/": "donnees", "tests/python/instantanes/": "instantanes", "tests/pages/references/": "references"}
# relancés quand une page (dont cas.py lit les exemples), un cas*.py ou un instantané change (revue de structure, R4)
INSTANTANES_ET_JSON = ("tests/python/test_instantanes*.py", "tests/python/test_json_strict.py")
# scripts de commande que test_lancer.py copie dans un dépôt temporaire (sans les importer) : leur modification relance ce test
SCRIPTS_DE_COMMANDE = ("tests/lancer.py", "tests/verifier.py", "tests/comparer_listes.py", "tests/rapport_pytest.py",
                       "tests/python/outils_du_site.py")
TEST_DES_SCRIPTS = "tests/python/test_lancer.py"
# tests qui lisent les .py des moteurs par leur chemin (ast), sans les importer : relancés quand un .py des dossiers des moteurs change
# (chantier fondations, F4 : graphe des imports figé, frontière du noyau)
LECTEURS_DES_MOTEURS = ("tests/python/test_imports.py", "tests/python/test_noyau.py")
PROCESSUS_PAGES_DEFAUT = 2                   # suite de pages sans la variable PROCESSUS_PAGES (Mac de l'enseignant, CI)
UV = ["uv", "run", "-q", "--no-project", "--python", "3.12", "--with", "sympy==1.13.3", "--with", "mpmath==1.3.0",
      "--with", "websockets", "--with", "pytest", "--with", "pytest-xdist", "python", "-m", "pytest"]


def sh(*args):
    return subprocess.run(args, cwd=RACINE, capture_output=True, text=True, check=True).stdout


def fichiers_modifies(depuis="HEAD"):
    """Fichiers modifiés depuis le commit `depuis` (commités ensuite, indexés ou non), supprimés compris, et non suivis : chemins
    relatifs à la racine, lus avec `-z` (noms à espaces ou non ASCII tels quels) ; `--no-renames` : un fichier déplacé donne son
    ancien chemin (supprimé) et le nouveau."""
    noms = set(verifier.noms_git("diff", "--name-only", "--no-renames", "-z", depuis, "--"))
    noms |= set(verifier.noms_git("ls-files", "--others", "--exclude-standard", "-z"))
    return sorted(noms)


def existe(chemin):
    return os.path.exists(os.path.join(RACINE, chemin))


def module_de(chemin):
    """Nom de module d'un .py des moteurs ou des tests Python (présent ou supprimé), None pour un autre fichier."""
    dossier, nom = os.path.split(chemin)
    return nom[:-3] if nom.endswith(".py") and dossier in DOSSIERS_MOTEURS + DOSSIERS_TESTS_PYTHON else None


def modules_du_depot():
    """{nom de module: chemin relatif} pour les .py présents des moteurs, des tests Python et de leurs données (les noms sont uniques
    dans le dépôt)."""
    modules = {}
    for dossier in DOSSIERS_MOTEURS + DOSSIERS_TESTS_PYTHON:
        if os.path.isdir(os.path.join(RACINE, dossier)):
            for nom in sorted(os.listdir(os.path.join(RACINE, dossier))):
                if nom.endswith(".py"):
                    modules.setdefault(nom[:-3], f"{dossier}/{nom}")
    return modules


def texte(chemin):
    with open(os.path.join(RACINE, chemin), encoding="utf-8") as f:
        return f.read()


IMPORT = re.compile(r"^\s*(?:import|from)\s+(\w+)", re.MULTILINE)


def imports(chemin):
    """Modules importés (lecture du texte, pas de l'arbre : le script se lance avec n'importe quel Python 3)."""
    return set(IMPORT.findall(texte(chemin)))


def nomme_le_dossier(contenu, element):
    """Vrai si une chaîne du texte (entre guillemets, sur une ligne) a `element` pour élément de chemin : "donnees",
    "tests/python/donnees/x.json"…"""
    return re.search(rf"""["'](?:[^"'\n]*/)?{re.escape(element)}(?:/[^"'\n]*)?["']""", contenu) is not None


def tests_python_concernes(modifies):
    """Tests Python à relancer (chemins), ou [TOUS_LES_TESTS_PYTHON] si on ne sait pas borner :
    - les test_*.py modifiés (encore présents) ;
    - ceux qui importent, même de loin, un module modifié ou supprimé. Le graphe est lu sur l'état présent, où le nom d'un module
      supprimé reste un nœud : un module qui l'importe encore est atteint, et un module qui ne l'importe plus a été modifié, donc est
      atteint lui aussi ; rien n'est perdu par rapport au graphe d'avant la suppression ;
    - ceux qui lisent par son chemin un fichier modifié ou supprimé d'un dossier de LUS_PAR_CHEMIN (donnees/, instantanes/, références
      des pages) : les modules dont une chaîne nomme ce dossier, puis leurs dépendants ; tous les tests si aucun module ne le nomme ;
    - test_instantanes*.py et test_json_strict.py si une page (fichier non .py d'un dossier d'outil, que cas.py lit), un cas*.py ou un
      instantané change ;
    - test_lancer.py si un script de commande change (il les copie au lieu de les importer) ;
    - test_imports.py et test_noyau.py si un .py des dossiers des moteurs change, supprimé ou nouveau compris (ils le lisent par
      son chemin) ;
    - les dépendants de outils_du_site.py si le manifeste ou le registre change (les listes d'outils des tests en dérivent) ;
    - et toujours les tests de fumée. Tous les tests si la liste des outils est illisible."""
    if LISTES_ILLISIBLES:
        return [TOUS_LES_TESTS_PYTHON]
    modules = modules_du_depot()
    textes = {nom: texte(chemin) for nom, chemin in modules.items()}
    touches = {m for m in map(module_de, modifies) if m}
    if any(n in SOURCES_DES_OUTILS for n in modifies):
        touches.add(MODULE_DES_OUTILS)
    noms = set(modules) | touches
    dependances = {nom: set(IMPORT.findall(t)) & noms for nom, t in textes.items()}
    for prefixe, element in sorted(LUS_PAR_CHEMIN.items()):
        if any(n.startswith(prefixe) for n in modifies):
            lecteurs = {nom for nom, t in textes.items() if nomme_le_dossier(t, element)}
            if not lecteurs:
                return [TOUS_LES_TESTS_PYTHON]
            touches |= lecteurs
    atteints = set(touches)
    change = True
    while change:
        change = False
        for nom, deps in dependances.items():
            if nom not in atteints and deps & atteints:
                atteints.add(nom)
                change = True
    tests = {modules[n] for n in atteints if n in modules and modules[n].startswith("tests/python/test_")}
    if any(est_page(n) or re.fullmatch(r"tests/python/cas[^/]*\.py", n) or n.startswith("tests/python/instantanes/")
           for n in modifies):
        for motif in INSTANTANES_ET_JSON:
            tests |= {os.path.relpath(c, RACINE).replace(os.sep, "/") for c in glob.glob(os.path.join(RACINE, motif))}
    if any(n in SCRIPTS_DE_COMMANDE for n in modifies) and existe(TEST_DES_SCRIPTS):
        tests.add(TEST_DES_SCRIPTS)
    if any(n.endswith(".py") and os.path.dirname(n) in DOSSIERS_MOTEURS for n in modifies):
        tests |= set(LECTEURS_DES_MOTEURS)
    tests = {t for t in tests if existe(t)}
    tests |= {f"tests/python/{n}" for n in FUMEE_PYTHON}
    return sorted(tests)


def est_page(chemin):
    """Fichier d'une page d'outil (index.html et ce qui l'accompagne) : tout fichier non .py d'un dossier d'outil."""
    return chemin.split("/")[0] in OUTILS_PAGES and not chemin.endswith(".py")


def outils_des_moteurs(modifies):
    """Outils dont la page charge (dans Pyodide) un .py modifié ou supprimé d'un dossier d'outil ou de moteur/, d'après
    moteur/manifeste.json (liste complète et minimale, vérifiée par test_manifeste.py) ; un module partagé donne tous les outils qui le
    chargent. 'tous' si on ne sait pas borner : fichier cité par aucun outil, outil du manifeste inconnu ici, manifeste illisible."""
    moteurs = [n for n in modifies if n.endswith(".py") and n.split("/")[0] in set(DOSSIERS_MOTEURS) | set(OUTILS_PAGES)]
    if not moteurs:
        return set()
    try:
        charges = {outil: set(o["fichiers"]) for outil, o in outils_du_site.manifeste(RACINE).items()}
    except (OSError, ValueError, KeyError, TypeError, AttributeError):
        return {"tous"}
    outils = set()
    for n in moteurs:
        concernes = {outil for outil, fichiers in charges.items() if n in fichiers}
        if not concernes or not concernes <= set(OUTILS_PAGES):
            return {"tous"}
        outils |= {OUTILS_PAGES[o] for o in concernes}
    return outils


def corpus_des_pages(modifies=()):
    """Noms des modules de tests/python (donnees/ comprise) que les tests de pages importent, même de loin (corpus des pages : cas.py,
    cas_el.py…) ; un module supprimé que l'un d'eux importe encore en fait partie."""
    modules = {nom: chemin for nom, chemin in modules_du_depot().items() if chemin.startswith("tests/python/")}
    noms = set(modules) | {module_de(n) for n in modifies if n.startswith("tests/python/") and module_de(n)}
    atteints = set()
    for nom in sorted(os.listdir(os.path.join(RACINE, "tests/pages"))):
        if nom.endswith(".py"):
            atteints |= imports(f"tests/pages/{nom}") & noms
    a_lire = list(atteints)
    while a_lire:
        nom = a_lire.pop()
        for dep in (imports(modules[nom]) if nom in modules else set()) & noms:
            if dep not in atteints:
                atteints.add(dep)
                a_lire.append(dep)
    return atteints


def outil_du_json(chemin):
    """Outil d'une référence de page ou d'un instantané resoudre (`<outil>.json`, une variante de filière avec sa page) ; 'tous'
    sinon."""
    nom = os.path.basename(chemin)[:-len(".json")]
    if nom in VARIANTES:
        return VARIANTES[nom]
    return nom if nom in OUTILS_PAGES.values() else "tous"


def outils_de_pages(modifies):
    """Outils dont une page (HTML, JS, CSS), un moteur Python chargé par la page, la référence de page (tests/pages/references) ou
    l'instantané resoudre (lu par test_comportement.py) est modifié ou supprimé ; 'tous' si un fichier commun, un autre fichier des
    tests de pages ou un module de leur corpus l'est ; 'tous' aussi si la liste des outils est illisible. Une page vient avec ses
    variantes de filière (la page des exponentielles et logarithmes avec sa filière M : références à part)."""
    if LISTES_ILLISIBLES:
        return {"tous"}
    outils = outils_des_moteurs(modifies)
    corpus = corpus_des_pages(modifies)
    for n in modifies:
        haut = n.split("/")[0]
        if est_page(n):
            outils.add(OUTILS_PAGES[haut])
        elif haut in ("commun", "index.html", "moteur") and not n.endswith(".py"):
            outils.add("tous")
        elif re.fullmatch(r"tests/(pages/references|python/instantanes/resoudre)/[^/]+\.json", n):
            outils.add(outil_du_json(n))
        elif n.startswith("tests/pages/"):
            outils.add("tous")
        elif n.startswith("tests/python/") and module_de(n) in corpus:
            outils.add("tous")
    if "tous" in outils:
        return {"tous"}
    outils |= {variante for variante, outil in VARIANTES.items() if outil in outils}
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
    """{chemin: empreinte `git hash-object`, ou None si supprimé} des fichiers modifiés (indexés ou non) ou non suivis ; noms lus
    comme dans fichiers_modifies (-z, --no-renames), et comme verifier.py lit ceux du commit."""
    noms = set(fichiers_modifies("HEAD"))
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


# --- reference : rafraîchir la référence du dépôt (chantier portage-pc) ---------------------------------------------------------

LISTES_REFERENCE = tuple(f"{n}-{s}.txt" for s in comparer_listes.SUITES for n in ("collecte", "resultats"))
ORIGINE_REFERENCE = "origine.txt"
HORS_TESTS = re.compile(r"^(docs/|CLAUDE\.md$)")    # aucun test ne lit ces fichiers : ils peuvent être modifiés pendant le lancement


def motifs_refus_reference(dossier, rapport):
    """Raisons de ne pas prendre ce rapport pour référence (liste vide : accepté)."""
    motifs = []
    head = rapport.get("head") or ""
    if subprocess.run(["git", "cat-file", "-e", f"{head}^{{commit}}"], cwd=RACINE, capture_output=True).returncode:
        motifs.append(f"commit de départ introuvable : {head or '(non noté)'}")
    elif subprocess.run(["git", "merge-base", "--is-ancestor", head, "HEAD"], cwd=RACINE).returncode:
        motifs.append(f"le commit du lancement ({head[:7]}) n'est pas dans l'historique de HEAD")
    py, pa = rapport.get("python") or {}, rapport.get("pages") or {}
    if rapport.get("code") != 0 or py.get("code") != 0 or pa.get("code") != 0 or not pa.get("lancee"):
        motifs.append(f"codes de retour : global {rapport.get('code')}, Python {py.get('code')}, "
                      f"pages {pa.get('code') if pa.get('lancee') else 'non lancées'} (0 exigé partout)")
    env = rapport.get("environnement") or {}
    motifs += [f"suite non complète : {k}={env[k]} au lancement" for k in verifier.ENV_INTERDITS if env.get(k) not in (None, "")]
    for suite, b in (("python", py), ("pages", pa)):
        if b.get("ecarts_junit") or b.get("ecarts_junit") is None:
            motifs.append(f"{suite} : JUnit et extension discordants ou non comparés (rapport.json)")
    fichiers = set(rapport.get("fichiers_modifies") or {}) | set(rapport.get("fichiers_modifies_fin") or {})
    if rapport.get("fichiers_modifies") is None or rapport.get("fichiers_modifies_fin") is None:
        motifs.append("rapport.json incomplet : fichiers modifiés au début ou à la fin non notés")
    motifs += [f"{f} : modifié ou non suivi pendant le lancement (le lancement ne porte pas sur le commit seul)"
               for f in sorted(fichiers) if not HORS_TESTS.match(f)]
    return motifs


def rafraichir_reference(chemin):
    """Copie les listes d'un dossier de `complet --rapport` dans tests/reference, après contrôle ; code 0, 1 (refus) ou 2 (fichier manquant)."""
    dossier = os.path.abspath(chemin)
    cible = os.path.join(RACINE, verifier.REFERENCE)
    manquants = [n for n in ("rapport.json",) + LISTES_REFERENCE if not os.path.exists(os.path.join(dossier, n))]
    if manquants:
        print(f"reference : fichier(s) absent(s) de {dossier} : {', '.join(manquants)} ; rien n'est changé")
        return 2
    with open(os.path.join(dossier, "rapport.json"), encoding="utf-8") as f:
        rapport = json.load(f)
    motifs = motifs_refus_reference(dossier, rapport)
    if motifs:
        print(f"reference : REFUSÉ, {verifier.REFERENCE} n'est pas changée :")
        print("\n".join(f"  - {m}" for m in motifs))
        return 1
    if os.path.isdir(cible) and all(os.path.exists(os.path.join(cible, n)) for n in LISTES_REFERENCE):
        variables = comparer_listes.lire_variables(cible)
        for suite in comparer_listes.SUITES:
            ecarts = comparer_listes.comparer_suite(cible, dossier, suite, variables)
            print(f"{suite} : {len(ecarts)} différence(s) avec l'ancienne référence" + (" :" if ecarts else ""))
            print("\n".join(verifier.coupe(ecarts)) if ecarts else "", end="\n" if ecarts else "")
    os.makedirs(cible, exist_ok=True)
    for nom in LISTES_REFERENCE:                    # soustests-variables.txt, s'il existe, est gardé tel quel
        with open(os.path.join(dossier, nom), encoding="utf-8") as source, \
                open(os.path.join(cible, nom), "w", encoding="utf-8") as copie:
            copie.write(source.read())
    lignes = [f"Référence de `python3 tests/lancer.py verifier` (et de comparer_listes.py), écrite par `python3 tests/lancer.py reference`.",
              f"commit du lancement : {rapport['head']} (branche {rapport.get('branche')})",
              f"lancement : {rapport.get('debut')} -> {rapport.get('fin')} ; Python {rapport['python'].get('duree_s')} s, "
              f"pages {rapport['pages'].get('duree_s')} s",
              f"environnement : " + ", ".join(f"{k}={v if v is not None else '(non défini)'}"
                                              for k, v in sorted((rapport.get("environnement") or {}).items()))]
    lignes += [f"{suite} : {comparer_listes.resume(cible, suite)}" for suite in comparer_listes.SUITES]
    with open(os.path.join(cible, ORIGINE_REFERENCE), "w", encoding="utf-8") as f:
        f.write("\n".join(lignes) + "\n")
    print("\n".join(lignes[1:]))
    print(f"reference : {verifier.REFERENCE} remplacée ; à commiter (git add {verifier.REFERENCE})")
    return 0


def rapide(seulement_lister=False, depuis="HEAD"):
    modifies = fichiers_modifies(depuis)
    tests = tests_python_concernes(modifies)
    outils = outils_de_pages(modifies)
    print("fichiers modifiés" + (f" depuis {depuis}" if depuis != "HEAD" else "") + " :",
          ", ".join(n + ("" if existe(n) else " (supprimé)") for n in modifies) or "aucun")
    print("tests Python :", f"tous (tests/python : on ne sait pas borner{' : ' + LISTES_ILLISIBLES if LISTES_ILLISIBLES else ''})"
          if tests == [TOUS_LES_TESTS_PYTHON]
          else ", ".join(os.path.basename(t) for t in tests))
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
    if commande in ("rapide", "liste"):
        options = argv[2:]
        if options and (len(options) != 2 or options[0] != "--depuis" or options[1].startswith("-")):
            print(__doc__)
            return 2
        depuis = options[1] if options else "HEAD"
        if subprocess.run(["git", "rev-parse", "--verify", "-q", f"{depuis}^{{commit}}"], cwd=RACINE, capture_output=True).returncode:
            print(f"erreur : --depuis {depuis} : commit introuvable")
            return 2
        return rapide(seulement_lister=commande == "liste", depuis=depuis)
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
    if commande == "reference":
        if len(argv) != 3 or argv[2].startswith("--"):
            print(__doc__)
            return 2
        return rafraichir_reference(argv[2])
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
