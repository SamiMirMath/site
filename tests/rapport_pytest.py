"""Extension pytest passive de `lancer.py complet --rapport` : elle note, sans rien changer aux tests, l'issue de chaque test et ses sous-tests.

Chargée par `-p tests.rapport_pytest --rapport-json=<fichier>`. Elle n'agit que dans le processus principal (le contrôleur de xdist,
qui reçoit tous les comptes rendus des workers) et écrit à la fin un JSON :
    {"collectes": [identifiants], "issues": {identifiant: issue}, "sous_tests": {identifiant: {issue: nombre}}, "code": code de pytest}
Issues : passé, échoué, erreur, sauté, xfail, xpass. Ce fichier ne s'appelle pas `test_*.py` : pytest ne le collecte pas."""
import json

import pytest


def pytest_addoption(parser):
    parser.addoption("--rapport-json", default=None, help="fichier JSON des issues et des sous-tests (lancer.py --rapport)")


def _issue(report):
    if report.passed:
        return "xpass" if hasattr(report, "wasxfail") else "passé"
    if report.skipped:
        return "xfail" if hasattr(report, "wasxfail") else "sauté"
    return "échoué" if report.when == "call" else "erreur"


class Compteur:
    def __init__(self, chemin):
        self.chemin = chemin
        self.collectes = set()
        self.issues = {}
        self.sous_tests = {}

    @pytest.hookimpl(optionalhook=True)
    def pytest_xdist_node_collection_finished(self, node, ids):
        self.collectes.update(ids)

    def pytest_collection_modifyitems(self, items):
        # sans xdist, la collecte a lieu dans ce processus
        self.collectes.update(item.nodeid for item in items)

    def pytest_runtest_logreport(self, report):
        if type(report).__name__ == "SubtestReport":
            if report.when == "call":
                compte = self.sous_tests.setdefault(report.nodeid, {})
                issue = _issue(report)
                compte[issue] = compte.get(issue, 0) + 1
            return
        issue = _issue(report)
        if report.when == "setup" and issue != "passé":
            self.issues[report.nodeid] = issue
        elif report.when == "call":
            self.issues.setdefault(report.nodeid, issue)
        elif report.when == "teardown" and report.failed:
            self.issues[report.nodeid] = "erreur"

    def pytest_sessionfinish(self, session, exitstatus):
        for nodeid, compte in self.sous_tests.items():
            # un sous-test en échec ne change pas l'issue du test parent dans pytest 9 : on la corrige ici
            if (compte.get("échoué") or compte.get("erreur")) and self.issues.get(nodeid) == "passé":
                self.issues[nodeid] = "échoué"
        donnees = {"collectes": sorted(self.collectes), "issues": dict(sorted(self.issues.items())),
                   "sous_tests": dict(sorted(self.sous_tests.items())), "code": int(exitstatus)}
        with open(self.chemin, "w", encoding="utf-8") as f:
            json.dump(donnees, f, ensure_ascii=False, indent=1)


def pytest_configure(config):
    chemin = config.getoption("--rapport-json")
    if chemin and not hasattr(config, "workerinput"):
        config.pluginmanager.register(Compteur(chemin), "rapport_pytest_compteur")
