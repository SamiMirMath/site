"""Listes de tests (collectés, issues, sous-tests) écrites en texte trié, et comparaison nom par nom (chantier tests-rapides, P0).

    python3 tests/comparer_listes.py <référence> <dossier>
        compare, suite par suite, les fichiers texte de deux dossiers (par exemple tests/reference et le dossier
        écrit par `python3 tests/lancer.py complet --rapport <dossier>`) ; code 0 si tout est identique, 1 sinon, 2 si un fichier manque.

Fichiers d'un dossier, pour chaque suite (python, pages) :
    collecte-<suite>.txt   un identifiant collecté par ligne (trié) ;
    resultats-<suite>.txt  « identifiant <tab> issue <tab> sous-tests » (trié) ; issue : passé, échoué, erreur, sauté, xfail, xpass ;
                           sous-tests : le nombre de sous-tests passés, ou « passé:n,échoué:m » s'il y a d'autres issues, ou 0.
Dans le dossier de référence seulement, `soustests-variables.txt` (facultatif) liste les identifiants dont le nombre de sous-tests varie
d'un lancement à l'autre (tirages au hasard) : pour eux, seuls le nom et l'issue sont comparés.

Sans dépendance (lancé par le Python du système, comme lancer.py). Ce fichier ne s'appelle pas `test_*.py` : pytest ne le collecte pas."""
import os
import re
import sys
import xml.etree.ElementTree as ET

SUITES = ("python", "pages")
VARIABLES = "soustests-variables.txt"


# --- écriture --------------------------------------------------------------------------------------------------------------------

def texte_sous_tests(compte):
    """{issue: nombre} -> « 12 » (seulement des passés) ou « passé:10,échoué:2 » ; « 0 » sans sous-test."""
    compte = {k: v for k, v in (compte or {}).items() if v}
    if not compte:
        return "0"
    if set(compte) == {"passé"}:
        return str(compte["passé"])
    return ",".join(f"{k}:{compte[k]}" for k in sorted(compte))


def ecrire_listes(dossier, suite, donnees):
    """Écrit collecte-<suite>.txt et resultats-<suite>.txt à partir du JSON de l'extension `tests/rapport_pytest.py`."""
    with open(os.path.join(dossier, f"collecte-{suite}.txt"), "w", encoding="utf-8") as f:
        f.writelines(i + "\n" for i in sorted(donnees["collectes"]))
    with open(os.path.join(dossier, f"resultats-{suite}.txt"), "w", encoding="utf-8") as f:
        for i in sorted(donnees["issues"]):
            f.write(f"{i}\t{donnees['issues'][i]}\t{texte_sous_tests(donnees['sous_tests'].get(i))}\n")


def junit_issues(chemin):
    """{(classname, name): issue} d'après un fichier JUnit de pytest (pour vérifier l'extension par un second témoin)."""
    issues = {}
    for cas in ET.parse(chemin).getroot().iter("testcase"):
        enfants = {e.tag: e for e in cas}
        if "error" in enfants:
            issue = "erreur"
        elif "failure" in enfants:
            issue = "échoué"
        elif "skipped" in enfants:
            issue = "xfail" if enfants["skipped"].get("type") == "pytest.xfail" else "sauté"
        else:
            issue = "passé"
        issues[(cas.get("classname"), cas.get("name"))] = issue
    return issues


def adresse_junit(nodeid):
    """Identifiant pytest -> (classname, name) du JUnit (même règle que `mangle_test_address` de pytest)."""
    chemin, crochet, parametres = nodeid.partition("[")
    noms = chemin.split("::")
    noms[0] = re.sub(r"\.py$", "", noms[0].replace("/", "."))
    noms[-1] += crochet + parametres
    return ".".join(noms[:-1]), noms[-1]


def ecarts_junit(chemin_junit, issues):
    """Différences entre le JUnit et les issues de l'extension ; liste vide si les deux témoins concordent."""
    junit = junit_issues(chemin_junit)
    attendu = {}
    for i, issue in issues.items():
        # xpass : JUnit le note « passé » (non strict) ; un sous-test échoué peut laisser le parent « passé » dans le JUnit
        attendu[adresse_junit(i)] = "passé" if issue == "xpass" else issue
    ecarts = [f"absent du JUnit : {k}" for k in sorted(set(attendu) - set(junit))]
    ecarts += [f"absent de l'extension : {k}" for k in sorted(set(junit) - set(attendu))]
    ecarts += [f"{k} : JUnit {junit[k]}, extension {attendu[k]}" for k in sorted(set(junit) & set(attendu))
               if junit[k] != attendu[k] and not (attendu[k] == "échoué" and junit[k] == "passé")]
    return ecarts


# --- lecture et comparaison ------------------------------------------------------------------------------------------------------

def lire_collecte(dossier, suite):
    with open(os.path.join(dossier, f"collecte-{suite}.txt"), encoding="utf-8") as f:
        return [l.rstrip("\n") for l in f if l.strip()]


def lire_resultats(dossier, suite):
    resultats = {}
    with open(os.path.join(dossier, f"resultats-{suite}.txt"), encoding="utf-8") as f:
        for ligne in f:
            if ligne.strip():
                i, issue, sous = ligne.rstrip("\n").split("\t")
                resultats[i] = (issue, sous)
    return resultats


def lire_variables(dossier):
    chemin = os.path.join(dossier, VARIABLES)
    if not os.path.exists(chemin):
        return set()
    with open(chemin, encoding="utf-8") as f:
        return {l.strip() for l in f if l.strip() and not l.startswith("#")}


def comparer_suite(reference, dossier, suite, variables):
    """Lignes de différences d'une suite (vide si identique)."""
    ecarts = []
    ref_c, aut_c = set(lire_collecte(reference, suite)), set(lire_collecte(dossier, suite))
    ecarts += [f"collecte : disparu {i}" for i in sorted(ref_c - aut_c)]
    ecarts += [f"collecte : nouveau {i}" for i in sorted(aut_c - ref_c)]
    ref_r, aut_r = lire_resultats(reference, suite), lire_resultats(dossier, suite)
    ecarts += [f"résultats : disparu {i} ({ref_r[i][0]})" for i in sorted(set(ref_r) - set(aut_r))]
    ecarts += [f"résultats : nouveau {i} ({aut_r[i][0]})" for i in sorted(set(aut_r) - set(ref_r))]
    for i in sorted(set(ref_r) & set(aut_r)):
        if ref_r[i][0] != aut_r[i][0]:
            ecarts.append(f"issue : {i} : {ref_r[i][0]} -> {aut_r[i][0]}")
        if ref_r[i][1] != aut_r[i][1] and i not in variables:
            ecarts.append(f"sous-tests : {i} : {ref_r[i][1]} -> {aut_r[i][1]}")
    return ecarts


def resume(dossier, suite):
    r = lire_resultats(dossier, suite)
    issues = {}
    for issue, _ in r.values():
        issues[issue] = issues.get(issue, 0) + 1
    sous = 0
    for _, s in r.values():
        sous += sum(int(p.split(":")[-1]) for p in s.split(","))
    return f"{len(lire_collecte(dossier, suite))} collectés ; " + ", ".join(f"{issues[k]} {k}" for k in sorted(issues)) + f" ; {sous} sous-tests"


def main(argv):
    if len(argv) != 3:
        print(__doc__)
        return 2
    reference, dossier = argv[1], argv[2]
    variables = lire_variables(reference)
    code = 0
    for suite in SUITES:
        manquants = [n for n in (f"collecte-{suite}.txt", f"resultats-{suite}.txt") for d in (reference, dossier)
                     if not os.path.exists(os.path.join(d, n))]
        if manquants:
            print(f"{suite} : fichier absent ({', '.join(sorted(set(manquants)))}) dans {reference} ou {dossier}")
            code = 2
            continue
        ecarts = comparer_suite(reference, dossier, suite, variables)
        print(f"{suite} : référence {resume(reference, suite)}")
        print(f"{suite} : comparé   {resume(dossier, suite)}")
        if ecarts:
            code = max(code, 1)
            print(f"{suite} : {len(ecarts)} différence(s)")
            for e in ecarts:
                print("   ", e)
        else:
            exclus = len([v for v in variables if v in lire_resultats(reference, suite)])
            print(f"{suite} : identique, nom par nom" + (f" (sous-tests non comparés pour {exclus} test(s) variable(s))" if exclus else ""))
    return code


if __name__ == "__main__":
    sys.exit(main(sys.argv))
