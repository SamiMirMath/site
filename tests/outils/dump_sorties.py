"""Dump brut des sorties des moteurs (chantier fondations, F0 ; principe de vérification commun du rapport de revue-structure, § 4).

Quoi : pour chaque outil du site qui a un moteur Python (liste lue dans moteur/manifeste.json, recoupée avec commun/registre.json ; aucune
liste d'outils écrite ici), le script appelle les fonctions `<fn>_json` que la page appelle (manifeste, « fonctions » moins les
« anciennes ») sur tout le corpus de l'outil, et écrit la chaîne BRUTE renvoyée (ni re-sérialisée, ni arrondie, ni résumée), une entrée
par ligne, triées, dans un dossier HORS du dépôt. Les instantanés arrondissent les flottants et résument le graphique : ce dump prouve
l'identité à l'octet avant / après un chantier qui ne doit rien changer à l'écran.

Corpus d'un outil (union, sans doublon) :
- les clés de tous les instantanés tests/python/instantanes/**.json de l'outil (nom du fichier = id de l'outil, ou id-suffixe, par
  exemple exponentielles-logarithmes-M) : entrées de cas.py, cas_el.py, batteries de factorisation… ;
- les chaînes des constantes EXEMPLES*, EXOS* de la page (<outil>/index.html), filières comprises (EXEMPLES_M) ;
- le corpus des tests de pages (tests/pages/rendu.py, `entrees`, saisies d'erreur comprises) ;
- les saisies des corpus de l'enseignant (tests/python/donnees/) ;
- les exercices tirés par la page quand l'outil a une fonction « exercice » : N_EXERCICES par niveau (niveaux lus dans les `poids` de la
  page, par filière), graine fixe ; leur sortie brute va dans exercices/, leur énoncé entre dans le corpus.
Filières : celles des `parametres` du registre (?filiere=M) plus la valeur par défaut du paramètre `filiere` de `resoudre` ; chaque
filière résout tout le corpus de l'outil (les entrées 3C en 2M et inversement). `apercu`, `controle` ne prennent pas de filière (comme
dans la page). `fenetre` (arguments du graphique) n'est pas appelée : voir HORS_CORPUS.

Sorties dans <dossier> :
- index.txt : une ligne par fichier (fichier, outil, filière, fonction, nombre d'entrées), puis les outils du registre sans moteur ;
- <fonction>/<outil>.txt ou <fonction>/<outil>.<filière>.txt : en-tête « # … », puis « entrée JSON<TAB>sortie brute » par ligne ;
  une exception est écrite « !EXCEPTION Type: message » ;
- temps/temps.json : temps natif par outil et filière (somme des appels de resoudre_json, plus long appel, mur) ; HORS comparaison.
  Les temps dépendent du nombre de processus (cœurs partagés) et de l'ordre des appels (cache de SymPy) : ne comparer que des
  lancements faits avec le même --processus ; pour la règle « temps natif d'etudier() sur le corpus », --processus 1.
Le hasard est fixé avant chaque appel (random.seed sur la clé de l'appel) et PYTHONHASHSEED=0 : la sortie ne dépend ni de l'ordre des
appels ni de leur répartition entre processus. Aucun cache de test (memo.py) : les moteurs sont appelés directement.

Lancement, depuis n'importe où (le script se relance sous `uv` avec les dépendances de tests/lancer.py) :

    python3 tests/outils/dump_sorties.py <dossier hors du dépôt, absent ou vide> [--processus N]

Comparaison de deux dumps (code 0 et aucune sortie = identiques) :

    diff -r --exclude=temps <dump A> <dump B>

Ce fichier ne s'appelle pas test_*.py : ni pytest ni unittest ne le collectent."""
import importlib
import inspect
import json
import multiprocessing
import os
import random
import re
import subprocess
import sys
import time
import urllib.parse

ICI = os.path.dirname(os.path.abspath(__file__))
RACINE = os.path.abspath(os.path.join(ICI, "..", ".."))
TESTS_PYTHON = os.path.join(RACINE, "tests", "python")
TESTS_PAGES = os.path.join(RACINE, "tests", "pages")
INSTANTANES = os.path.join(TESTS_PYTHON, "instantanes")
N_EXERCICES = 30                       # exercices tirés par niveau et par filière
HORS_CORPUS = {"fenetre": "arguments JSON {f, xmin, xmax, n} du zoom du graphique, pas une saisie du corpus",
               "exercice": "tiré à part (dossier exercices/), son énoncé entre dans le corpus"}
# corpus de l'enseignant (tests/python/donnees/) : module -> (liste, outil) ; tout module du dossier doit y être
DONNEES = {"corpus_etude_complete": ("FONCTIONS", "etude-complete"), "corpus_limites_3m": ("CAS", "limites-asymptotes")}


def erreur(message):
    print(f"dump_sorties : {message}", file=sys.stderr)
    sys.exit(2)


def dossier_de_sortie(chemin):
    """Chemin absolu du dossier de sortie : hors du dépôt, absent ou vide."""
    d = os.path.realpath(os.path.abspath(chemin))
    if d == RACINE or d.startswith(RACINE + os.sep):
        erreur(f"le dossier doit être hors du dépôt : {d}")
    if os.path.exists(d) and (not os.path.isdir(d) or os.listdir(d)):
        erreur(f"le dossier existe et n'est pas vide : {d}")
    return d


def relancer_sous_uv(argv):
    """Relance ce script sous `uv run` (Python 3.12, SymPy 1.13.3, mpmath : les versions de tests/lancer.py), avec PYTHONHASHSEED=0."""
    sys.path.insert(0, os.path.join(RACINE, "tests"))
    import lancer
    uv = lancer.UV[:lancer.UV.index("python") + 1]
    env = dict(os.environ, DUMP_SORTIES_UV="1", PYTHONHASHSEED="0")
    return subprocess.run(uv + [os.path.abspath(__file__)] + argv, cwd=RACINE, env=env).returncode


# ---------------------------------------------------------------- outils, filières, corpus (processus principal)

def lire_json(chemin):
    with open(os.path.join(RACINE, chemin), encoding="utf-8") as f:
        return json.load(f)


def outils_du_site():
    """(outils du manifeste {id: entrée}, registre {id: entrée}, ids du registre sans moteur Python)."""
    manifeste = lire_json("moteur/manifeste.json")["outils"]
    registre = {o["id"]: o for o in lire_json("commun/registre.json")["outils"]}
    inconnus = sorted(set(manifeste) - set(registre))
    if inconnus:
        erreur(f"outils du manifeste absents du registre : {inconnus}")
    return manifeste, registre, sorted(set(registre) - set(manifeste))


def filieres(outil, module, registre):
    """Filières de `resoudre` : [None] si l'outil n'en a pas ; sinon la valeur par défaut et celles des paramètres du registre."""
    params = inspect.signature(module.resoudre).parameters
    du_registre = {v for q in registre[outil].get("parametres", {}).values()
                   for v in urllib.parse.parse_qs(urllib.parse.urlsplit(q).query).get("filiere", [])}
    if "filiere" not in params:
        if du_registre:
            erreur(f"{outil} : filières dans le registre, mais resoudre() n'a pas de paramètre filiere")
        return [None]
    return sorted(du_registre | {params["filiere"].default})


def html_page(outil):
    with open(os.path.join(RACINE, outil, "index.html"), encoding="utf-8") as f:
        return f.read()


def entrees_de_page(outil):
    """Chaînes des constantes EXEMPLES*, EXOS* de la page (les clés de niveau d'EXOS ne sont pas entre guillemets)."""
    out = set()
    for m in re.finditer(r"const (?:EXEMPLES|EXOS)\w*=(.*?);\n", html_page(outil), re.S):
        out |= set(re.findall(r'"([^"]*)"', m.group(1)))
    return out


def niveaux_de_page(outil):
    """{filière (None si la page n'en a pas): [niveaux]} lus dans les `poids` de monterOutil."""
    s = html_page(outil)
    par_filiere = {cle: re.findall(r'\["(\w+)",', poids)
                   for cle, poids in re.findall(r'\{cle:"(\w+)",[^{}]*?poids:(\[\[.*?\]\])\}', s)}
    if par_filiere:
        return par_filiere
    m = re.search(r"\bpoids:(\[\[.*?\]\])", s)
    if not m:
        erreur(f"{outil} : fonction exercice au manifeste, mais aucun `poids` dans la page")
    return {None: re.findall(r'\["(\w+)",', m.group(1))}


def outil_d_un_instantane(nom, ids):
    """Outil d'un fichier d'instantané : l'id le plus long tel que nom == id ou nom commence par id + '-'."""
    candidats = [i for i in ids if nom == i or nom.startswith(i + "-")]
    if not candidats:
        erreur(f"instantané sans outil du manifeste : {nom}.json")
    return max(candidats, key=len)


def corpus_fixe(ids):
    """{outil: set d'entrées} hors exercices tirés."""
    corpus = {i: set() for i in ids}
    for d, _, noms in os.walk(INSTANTANES):
        for n in sorted(noms):
            if n.endswith(".json"):
                with open(os.path.join(d, n), encoding="utf-8") as f:
                    corpus[outil_d_un_instantane(n[:-5], ids)] |= set(json.load(f))
    sys.path.insert(0, TESTS_PAGES)
    import rendu
    for outil in ids:
        corpus[outil] |= entrees_de_page(outil)
    for nom in list(rendu.OUTILS) + [rendu.OUTIL_M]:                  # OUTIL_M : la page ouverte en filière M
        corpus[outil_d_un_instantane(nom, ids)] |= set(rendu.entrees(nom))
    hors_rendu = sorted(set(ids) - set(rendu.OUTILS))
    if hors_rendu:
        erreur(f"outils absents du corpus des pages (tests/pages/rendu.py) : {hors_rendu}")
    modules = sorted(n[:-3] for n in os.listdir(os.path.join(TESTS_PYTHON, "donnees")) if n.endswith(".py") and n != "__init__.py")
    oublies = sorted(set(modules) - set(DONNEES))
    if oublies:
        erreur(f"corpus de tests/python/donnees/ non lus par ce script (DONNEES) : {oublies}")
    sys.path.insert(0, os.path.join(TESTS_PYTHON, "donnees"))          # comme les tests qui les lisent
    for nom, (liste, outil) in DONNEES.items():
        corpus[outil] |= {c.saisie for c in getattr(importlib.import_module(nom), liste)}
    return corpus


# ---------------------------------------------------------------- appels (processus de travail)

_MODULES = {}


def initialiser():
    sys.path.insert(0, TESTS_PYTHON)
    import moteurs  # noqa: F401  (chemins des moteurs, contrôle de SymPy)


def appeler(tache):
    """tache = (clé, module, fonction, arguments) -> (clé, sortie brute, durée en s)."""
    cle, module, fonction, args = tache
    if module not in _MODULES:
        _MODULES[module] = importlib.import_module(module)
    random.seed(repr(cle))
    debut = time.perf_counter()
    try:
        brut = getattr(_MODULES[module], fonction + "_json")(*args)
    except Exception as e:      # comportement figé, plantage compris
        brut = "!EXCEPTION " + type(e).__name__ + ": " + json.dumps(str(e), ensure_ascii=False)
    duree = time.perf_counter() - debut
    if not isinstance(brut, str):
        brut = "!PAS_UNE_CHAINE " + repr(brut)
    if "\n" in brut:
        brut = "!SAUT_DE_LIGNE " + json.dumps(brut, ensure_ascii=False)
    return cle, brut, duree


def lancer(pool, taches):
    """{clé: (brut, durée)} ; l'ordre des tâches (les plus longues d'abord) et leur répartition sont sans effet sur le résultat."""
    return {cle: (brut, duree) for cle, brut, duree in pool.imap_unordered(appeler, taches, chunksize=1)}


# ---------------------------------------------------------------- écriture

def nom_fichier(fonction, outil, filiere):
    return f"{fonction}/{outil}.txt" if filiere is None else f"{fonction}/{outil}.{filiere}.txt"


def ecrire(dossier, fichier, outil, filiere, fonction, lignes):
    """lignes : [(entrée, brut)] ; triées par entrée JSON."""
    chemin = os.path.join(dossier, fichier)
    os.makedirs(os.path.dirname(chemin), exist_ok=True)
    with open(chemin, "w", encoding="utf-8", newline="\n") as f:
        f.write(f"# outil={outil} filiere={filiere or '-'} fonction={fonction}_json entrees={len(lignes)}\n")
        for e, brut in sorted((json.dumps(e, ensure_ascii=False), b) for e, b in lignes):
            f.write(f"{e}\t{brut}\n")


def principal(argv):
    if not argv or argv[0].startswith("-"):
        erreur("usage : python3 tests/outils/dump_sorties.py <dossier hors du dépôt> [--processus N]")
    dossier = dossier_de_sortie(argv[0])
    processus = os.cpu_count() or 2
    if len(argv) == 3 and argv[1] == "--processus" and argv[2].isdigit() and int(argv[2]) >= 1:
        processus = int(argv[2])
    elif len(argv) != 1:
        erreur("arguments : <dossier> [--processus N]")
    if os.environ.get("DUMP_SORTIES_UV") != "1":
        return relancer_sous_uv([dossier] + argv[1:])

    debut = time.perf_counter()
    initialiser()
    manifeste, registre, sans_moteur = outils_du_site()
    ids = sorted(manifeste)
    modules = {o: importlib.import_module(manifeste[o]["module"]) for o in ids}
    corpus = corpus_fixe(ids)
    filieres_de = {o: filieres(o, modules[o], registre) for o in ids}
    fonctions = {}
    for o in ids:
        appelees = [f for f in manifeste[o]["fonctions"] if f not in manifeste[o].get("anciennes", [])]
        for f in appelees:
            if not hasattr(modules[o], f + "_json"):
                erreur(f"{o} : {manifeste[o]['module']}.{f}_json absente")
        fonctions[o] = [f for f in appelees if f not in HORS_CORPUS]
        if "resoudre" not in fonctions[o]:
            erreur(f"{o} : pas de fonction resoudre au manifeste")

    os.makedirs(dossier, exist_ok=True)
    ctx = multiprocessing.get_context("fork" if "fork" in multiprocessing.get_all_start_methods() else "spawn")
    with ctx.Pool(processus, initializer=initialiser) as pool:
        # 1. exercices tirés par la page (niveaux de ses `poids`), graine fixe par appel
        taches = []
        for o in ids:
            if "exercice" in manifeste[o]["fonctions"]:
                for filiere, niveaux in niveaux_de_page(o).items():
                    if (filiere is None) != (filieres_de[o] == [None]) or (filiere is not None and filiere not in filieres_de[o]):
                        erreur(f"{o} : filières de la page ({filiere}) et de resoudre ({filieres_de[o]}) différentes")
                    for niveau in niveaux:
                        for k in range(N_EXERCICES):
                            args = (niveau,) if filiere is None else (niveau, filiere)
                            taches.append((("exercice", o, filiere, niveau, k), manifeste[o]["module"], "exercice", args))
        exercices = lancer(pool, taches)
        par_fichier = {}
        for (fonction, o, filiere, niveau, k), (brut, _) in exercices.items():
            par_fichier.setdefault((o, filiere), []).append((f"{niveau}#{k}", brut))
            try:
                expr = json.loads(brut).get("expr")
            except ValueError:
                expr = None
            if isinstance(expr, str):
                corpus[o].add(expr)
        for (o, filiere), lignes in sorted(par_fichier.items(), key=lambda t: (t[0][0], t[0][1] or "")):
            ecrire(dossier, nom_fichier("exercices", o, filiere), o, filiere, "exercice", lignes)

        # 2. resoudre (par filière) et les autres fonctions de la page, sur tout le corpus de l'outil
        taches = []
        for o in sorted(ids, key=lambda o: o != "etude-complete"):        # le plus lent d'abord
            for f in fonctions[o]:
                for filiere in (filieres_de[o] if f == "resoudre" else [None]):
                    for e in sorted(corpus[o]):
                        args = (e,) if filiere is None else (e, filiere)
                        taches.append(((f, o, filiere, e), manifeste[o]["module"], f, args))
        sorties = lancer(pool, taches)

    index, temps = [], {}
    groupes = {}
    for (f, o, filiere, e), (brut, duree) in sorties.items():
        groupes.setdefault((f, o, filiere), []).append((e, brut, duree))
    for (f, o, filiere), lignes in sorted(groupes.items(), key=lambda t: (t[0][0], t[0][1], t[0][2] or "")):
        fichier = nom_fichier(f, o, filiere)
        ecrire(dossier, fichier, o, filiere, f, [(e, b) for e, b, _ in lignes])
        index.append((fichier, o, filiere or "-", f + "_json", len(lignes)))
        if f == "resoudre":
            plus_long = max(lignes, key=lambda t: t[2])
            temps.setdefault(o, {})[filiere or "-"] = {
                "entrees": len(lignes), "total_s": round(sum(t[2] for t in lignes), 3),
                "max_s": round(plus_long[2], 3), "entree_max": plus_long[0]}
    for (o, filiere), lignes in sorted(par_fichier.items(), key=lambda t: (t[0][0], t[0][1] or "")):
        index.append((nom_fichier("exercices", o, filiere), o, filiere or "-", "exercice_json", len(lignes)))
    with open(os.path.join(dossier, "index.txt"), "w", encoding="utf-8", newline="\n") as f:
        f.write("# fichier\toutil\tfiliere\tfonction\tentrees\n")
        for ligne in sorted(index):
            f.write("\t".join(str(c) for c in ligne) + "\n")
        for o in sans_moteur:
            f.write(f"# {o} : outil du registre sans moteur Python (absent de moteur/manifeste.json), rien à appeler\n")
        for fn, raison in sorted(HORS_CORPUS.items()):
            f.write(f"# {fn} : non appelée sur le corpus ({raison})\n")
    mur = time.perf_counter() - debut
    os.makedirs(os.path.join(dossier, "temps"), exist_ok=True)
    with open(os.path.join(dossier, "temps", "temps.json"), "w", encoding="utf-8") as f:
        json.dump({"mur_s": round(mur, 1), "processus": processus, "resoudre_json": temps}, f, ensure_ascii=False, indent=1, sort_keys=True)
        f.write("\n")
    total = sum(n for *_, n in index)
    print(f"dump_sorties : {len(index)} fichiers, {total} sorties, {mur:.0f} s de mur ({processus} processus) -> {dossier}")
    return 0


if __name__ == "__main__":
    sys.exit(principal(sys.argv[1:]))
