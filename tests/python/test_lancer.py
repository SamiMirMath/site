"""Chantier fondations, F1, F2 et F3 : `python3 tests/lancer.py verifier` et `liste` (ce que `rapide` lancerait), essayés dans un dépôt
git temporaire.

Chaque test travaille dans un dépôt jetable (tempfile) : jamais dans le vrai dépôt (chaque commande git ou Python y est lancée avec ce
dossier pour `cwd`, sous GIT_CEILING_DIRECTORIES, et le dépôt jetable vérifie qu'il est bien sa propre racine). On y copie les scripts
de commande (`tests/lancer.py`, `tests/verifier.py`, `tests/comparer_listes.py`) et la liste des outils que lancer.py charge
(`tests/python/outils_du_site.py`, F3), qui prennent alors ce dépôt pour racine.

Les dossiers de rapport sont écrits par le vrai `complet_avec_rapport` du lancer.py copié ; seuls les deux lancements de pytest
(`lancer.python`, `lancer.pages`) sont remplacés par un faux qui écrit ce que pytest aurait écrit : le JSON de l'extension
`tests/rapport_pytest.py` (collectes, issues, sous-tests, code) et le JUnit (`--junitxml`, même forme que celui de pytest). La référence
est posée par la vraie commande `lancer.py reference`, puis commitée, comme au P0 d'un chantier.

Aides communes : `Depot` (git, écrire, commiter, lancer une commande de lancer.py), `Depot.rapport` (faux lancement complet),
`ModeleDepot` (dépôt de départ construit une fois par processus, copié pour chaque test).

F2 (`TestRapide`) : un second dépôt modèle, `ModeleRapide`, imite la forme du vrai (moteur/manifeste.json, commun/registre.json depuis
F3, dossiers d'outils et leurs pages, tests/python avec cas.py, donnees/ et instantanes/, tests/pages avec ses références), avec des
noms à espaces et non ASCII ; chaque test y modifie, supprime ou déplace des fichiers et compare ce que `liste` (et `liste --depuis`)
annonce à ce qui est attendu. Rien n'y est lancé : `liste` ne lance aucun test. F3 : un manifeste ou un registre modifié relance les
dépendants de outils_du_site.py ; une liste des outils illisible fait tout relancer."""
import atexit
import copy
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

RACINE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
SCRIPTS = ("tests/lancer.py", "tests/verifier.py", "tests/comparer_listes.py", "tests/python/outils_du_site.py")
DELAI = 60                                   # secondes, pour chaque sous-processus (git ou Python)
BRANCHE = "essai"
SUIVI = f"docs/chantiers/{BRANCHE}/suivi.md"

TEXTE_SUIVI = """# Chantier « essai » — suivi

## Variations de sous-tests

Format, une ligne par test : - `identifiant pytest complet` : avant → après : raison.

{lignes}

## Reprise après compactage

- Rien.
"""

# suite -> {identifiant: [issue, {issue des sous-tests: nombre}]} : ce que pytest et l'extension noteraient
SUITES_DEPART = {
    "python": {"code": 0, "tests": {
        "tests/python/test_a.py::test_un": ["passé", {"passé": 5}],
        "tests/python/test_a.py::TestB::test_deux": ["passé", {}],
        "tests/python/test_a.py::test_trois": ["xfail", {}],
        "tests/python/test_c.py::test_param[x-1]": ["passé", {"passé": 3}],
    }},
    "pages": {"code": 0, "tests": {
        "tests/pages/test_p.py::TestP::test_page": ["passé", {"passé": 4}],
        "tests/pages/test_p.py::TestP::test_autre": ["passé", {}],
    }},
}

# Lancé dans le dépôt temporaire : le vrai `complet_avec_rapport`, avec un faux pytest qui écrit le JSON de l'extension et le JUnit.
FAUX_COMPLET = r'''
import json, os, sys
from xml.sax.saxutils import quoteattr
sys.path.insert(0, "tests")
import comparer_listes, lancer

dossier, chemin_spec = sys.argv[1:3]
with open(chemin_spec, encoding="utf-8") as f:
    spec = json.load(f)
JUNIT = {"passé": "", "xpass": "", "échoué": '<failure message="assert False">assert False</failure>',
         "erreur": '<error message="erreur au montage">erreur</error>',
         "sauté": '<skipped type="pytest.skip" message="sauté">test.py:1: sauté</skipped>',
         "xfail": '<skipped type="pytest.xfail" message="pas encore" />'}


def faux_pytest(suite):
    def lancement(*_args, en_plus=(), **_kwargs):
        options = dict(a.split("=", 1) for a in en_plus if a.startswith("--") and "=" in a)
        for chemin, texte in spec.get("pendant", {}).get(suite, {}).items():     # fichier changé pendant le lancement
            os.makedirs(os.path.dirname(chemin) or ".", exist_ok=True)
            with open(chemin, "w", encoding="utf-8") as f:
                f.write(texte)
        s = spec[suite]
        tests = s["tests"]
        donnees = {"collectes": sorted(s.get("collectes", tests)), "issues": {i: t[0] for i, t in sorted(tests.items())},
                   "sous_tests": {i: t[1] for i, t in sorted(tests.items()) if t[1]}, "code": s["code"]}
        with open(options["--rapport-json"], "w", encoding="utf-8") as f:
            json.dump(donnees, f, ensure_ascii=False, indent=1)
        cas = []
        for i, (issue, _) in sorted(tests.items()):
            classe, nom = comparer_listes.adresse_junit(i)
            corps = JUNIT[issue]
            cas.append(f'<testcase classname={quoteattr(classe)} name={quoteattr(nom)} time="0.001"' +
                       (f">{corps}</testcase>" if corps else " />"))
        compte = lambda *issues: sum(1 for t in tests.values() if t[0] in issues)
        with open(options["--junitxml"], "w", encoding="utf-8") as f:
            f.write('<?xml version="1.0" encoding="utf-8"?><testsuites name="pytest tests"><testsuite name="pytest" '
                    f'errors="{compte("erreur")}" failures="{compte("échoué")}" skipped="{compte("sauté", "xfail")}" '
                    f'tests="{len(tests)}" time="0.1" timestamp="2026-11-05T12:00:00+01:00" hostname="essai">'
                    + "".join(cas) + "</testsuite></testsuites>")
        return s["code"]
    return lancement


lancer.python = faux_pytest("python")
lancer.pages = faux_pytest("pages")
sys.exit(lancer.complet_avec_rapport(dossier))
'''


def environnement(plafond):
    """Variables des sous-processus : git sans configuration de l'utilisateur ni du système, identité fixe, aucune recherche de dépôt
    au-dessus du dossier temporaire ; ni CORPUS ni OUTILS (sinon le faux lancement serait noté comme une suite non complète)."""
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_") and k not in ("CORPUS", "OUTILS")}
    env.update({"GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_NOSYSTEM": "1", "GIT_CEILING_DIRECTORIES": plafond,
                "GIT_AUTHOR_NAME": "Essai", "GIT_AUTHOR_EMAIL": "essai@example.invalid",
                "GIT_COMMITTER_NAME": "Essai", "GIT_COMMITTER_EMAIL": "essai@example.invalid", "LC_ALL": "C.UTF-8",
                "PYTHONDONTWRITEBYTECODE": "1"})
    return env


class Depot:
    """Un dépôt git jetable dans `<base>/depot` ; les dossiers de rapport vont dans `<base>/rapports` (hors du dépôt)."""

    def __init__(self, base):
        self.base = os.path.realpath(base)
        self.racine = os.path.join(self.base, "depot")
        self.env = environnement(self.base)

    def executer(self, *commande):
        r = subprocess.run(commande, cwd=self.racine, env=self.env, capture_output=True, text=True, timeout=DELAI)
        return r.returncode, r.stdout + r.stderr

    def git(self, *args):
        code, sortie = self.executer("git", *args)
        if code:
            raise AssertionError(f"git {' '.join(args)} : code {code}\n{sortie}")
        return sortie

    def verifier_isole(self):
        assert os.path.commonpath([self.racine, RACINE]) != RACINE, "le dépôt temporaire est dans le vrai dépôt"
        assert os.path.realpath(self.git("rev-parse", "--show-toplevel").strip()) == self.racine, "pas la racine du dépôt temporaire"

    def ecrire(self, chemin, texte):
        complet = os.path.join(self.racine, chemin)
        os.makedirs(os.path.dirname(complet), exist_ok=True)
        with open(complet, "w", encoding="utf-8") as f:
            f.write(texte)

    def lire(self, chemin):
        with open(os.path.join(self.racine, chemin), encoding="utf-8") as f:
            return f.read()

    def commiter(self, message, *chemins):
        self.git("add", "--", *chemins)
        self.git("commit", "-q", "-m", message)

    def lancer(self, *args):
        """`python3 tests/lancer.py <args>` dans le dépôt temporaire -> (code, sortie)."""
        return self.executer(sys.executable, "tests/lancer.py", *args)

    def rapport(self, nom, suites, pendant=None):
        """Faux `complet --rapport <base>/rapports/<nom>` -> (code, dossier). `pendant` : {suite: {chemin: texte}} écrits pendant
        le lancement de cette suite."""
        dossier = os.path.join(self.base, "rapports", nom)
        spec = dict(copy.deepcopy(suites), pendant=pendant or {})
        chemin_spec = os.path.join(self.base, f"spec-{nom}.json")
        with open(chemin_spec, "w", encoding="utf-8") as f:
            json.dump(spec, f, ensure_ascii=False)
        code, sortie = self.executer(sys.executable, "-c", FAUX_COMPLET, dossier, chemin_spec)
        if not os.path.exists(os.path.join(dossier, "rapport.json")):
            raise AssertionError(f"faux lancement sans rapport.json (code {code})\n{sortie}")
        return code, dossier


class ModeleDepot:
    """Dépôt de départ, construit une fois par processus puis copié pour chaque test : les scripts copiés, un fichier de code, un
    CLAUDE.md, le suivi.md du chantier `essai` (section « Variations de sous-tests » vide), puis la référence posée par
    `lancer.py reference` et commitée (P0)."""
    _modele = None

    @classmethod
    def copie(cls, base):
        if cls._modele is None:
            modele = tempfile.mkdtemp(prefix="modele-lancer-")
            atexit.register(shutil.rmtree, modele, True)
            cls._construire(Depot(modele))
            cls._modele = modele
        shutil.copytree(os.path.join(cls._modele, "depot"), os.path.join(base, "depot"), symlinks=True)
        depot = Depot(base)
        depot.verifier_isole()
        return depot

    @staticmethod
    def _construire(depot):
        os.makedirs(depot.racine)
        depot.git("init", "-q", "-b", BRANCHE)
        depot.verifier_isole()
        for chemin in SCRIPTS:
            with open(os.path.join(RACINE, chemin), encoding="utf-8") as f:
                depot.ecrire(chemin, f.read())
        depot.ecrire(".gitignore", "__pycache__/\n")             # comme le vrai .gitignore
        depot.ecrire("src/calcul.py", "VALEUR = 1\n")
        depot.ecrire("CLAUDE.md", "# Instructions\n")
        depot.ecrire(SUIVI, TEXTE_SUIVI.format(lignes="(aucune)"))
        depot.commiter("départ", ".gitignore", *SCRIPTS, "src/calcul.py", "CLAUDE.md", SUIVI)
        code, dossier = depot.rapport("P0", SUITES_DEPART)
        assert code == 0, code
        code, sortie = depot.lancer("reference", dossier)
        assert code == 0, sortie
        depot.commiter("P0 : référence", "tests/reference")
        shutil.rmtree(os.path.join(depot.base, "rapports"))


def suites_avec(**changements):
    """Les suites de départ, modifiées : changements {suite: {identifiant: [issue, sous-tests] ou None (retiré)}}, ou
    `code_<suite>` pour un code de retour."""
    suites = copy.deepcopy(SUITES_DEPART)
    for cle, valeur in changements.items():
        if cle.startswith("code_"):
            suites[cle[5:]]["code"] = valeur
            continue
        for identifiant, resultat in valeur.items():
            if resultat is None:
                del suites[cle]["tests"][identifiant]
            else:
                suites[cle]["tests"][identifiant] = resultat
    return suites


class TestVerifier(unittest.TestCase):
    """Verdicts de `lancer.py verifier` sur une partie : changement de code, lancement, commit, vérification."""

    def setUp(self):
        self.base = tempfile.mkdtemp(prefix="test-lancer-")
        self.addCleanup(shutil.rmtree, self.base, True)
        self.depot = ModeleDepot.copie(self.base)

    def partie(self, suites=SUITES_DEPART, avant=None, pendant=None, apres=None, commit=("src/calcul.py",), options=()):
        """Une partie : `avant` (dict chemin -> texte, écrit avant le lancement), le lancement, `apres` (écrit après), le commit des
        fichiers `commit`, puis `verifier` -> (code, sortie)."""
        self.depot.ecrire("src/calcul.py", "VALEUR = 2\n")
        for chemin, texte in (avant or {}).items():
            self.depot.ecrire(chemin, texte)
        _, dossier = self.depot.rapport("partie", suites, pendant)
        for chemin, texte in (apres or {}).items():
            self.depot.ecrire(chemin, texte)
        self.depot.commiter("partie", *commit)
        self.dossier = dossier
        return self.depot.lancer("verifier", dossier, *options)

    def accepte(self, code, sortie):
        self.assertEqual(code, 0, sortie)
        self.assertIn("VERDICT : ACCEPTÉ (code 0)", sortie)

    def refuse(self, code, sortie, *motifs):
        self.assertEqual(code, 1, sortie)
        self.assertIn("VERDICT : REFUSÉ (code 1)", sortie)
        for motif in motifs:
            self.assertIn(motif, sortie)

    def justifier(self, *lignes):
        return {SUIVI: TEXTE_SUIVI.format(lignes="\n".join(lignes))}

    # --- (a), (b) : commit et fichiers

    def test_accepte_nominal(self):
        code, sortie = self.partie()
        self.accepte(code, sortie)
        self.assertIn("fichiers ignorés (docs/ ; CLAUDE.md hors du commit) : aucun", sortie)
        self.assertIn("empreintes conformes pour les 1 fichier(s) testé(s)", sortie)
        self.assertIn(f"(d) suivi : {SUIVI} : 0 justification(s)", sortie)

    def test_test_ajoute_et_sous_tests_en_hausse_acceptes_et_listes(self):
        code, sortie = self.partie(suites_avec(python={"tests/python/test_a.py::test_nouveau": ["passé", {}],
                                                       "tests/python/test_a.py::test_un": ["passé", {"passé": 7}]}))
        self.accepte(code, sortie)
        self.assertIn("tests/python/test_a.py::test_nouveau (nouveau, passé)", sortie)
        self.assertIn("tests/python/test_a.py::test_un : 5 -> 7", sortie)

    def test_docs_modifie_ou_non_suivi_ignore_et_liste(self):
        code, sortie = self.partie(
            avant={SUIVI: TEXTE_SUIVI.format(lignes="(aucune, modifié)"), "docs/notes.md": "non suivi\n", "CLAUDE.md": "# Changé\n"},
            pendant={"python": {"docs/apparu.md": "pendant\n", "docs/notes.md": "changé pendant\n"}},
            apres={f"docs/chantiers/{BRANCHE}/journal.md": "écrit après\n"},
            commit=("src/calcul.py", f"docs/chantiers/{BRANCHE}/journal.md"))
        self.accepte(code, sortie)
        self.assertIn("fichiers ignorés (docs/ ; CLAUDE.md hors du commit) : 5", sortie)
        for chemin in (SUIVI, "docs/notes.md", "docs/apparu.md", f"docs/chantiers/{BRANCHE}/journal.md", "CLAUDE.md"):
            self.assertIn(f"      {chemin} : ", sortie)

    def test_claude_md_dans_le_commit_change_apres_le_lancement_refuse(self):
        code, sortie = self.partie(apres={"CLAUDE.md": "# Changé après\n"}, commit=("src/calcul.py", "CLAUDE.md"))
        self.refuse(code, sortie, "(a) fichier(s) du commit différent(s)", "CLAUDE.md : dans le commit, mais ni modifié")

    def test_autre_fichier_non_suivi_refuse(self):
        code, sortie = self.partie(avant={"src/brouillon.py": "X = 0\n"})
        self.refuse(code, sortie, "(b) fichier(s) modifié(s) ou non suivi(s)", "src/brouillon.py : modifié ou non suivi")

    def test_fichier_apparu_pendant_le_lancement_refuse(self):
        code, sortie = self.partie(pendant={"pages": {"src/apparu.py": "X = 0\n"}})
        self.refuse(code, sortie, "src/apparu.py : apparu pendant le lancement")

    def test_commit_different_des_empreintes_refuse(self):
        code, sortie = self.partie(apres={"src/calcul.py": "VALEUR = 3\n"})
        self.refuse(code, sortie, "(a) fichier(s) du commit différent(s) de ce que le lancement a testé", "src/calcul.py : empreinte")

    def test_commit_qui_n_est_pas_l_enfant_du_depart_refuse(self):
        _, sortie = self.partie()
        self.depot.ecrire("src/calcul.py", "VALEUR = 4\n")
        self.depot.commiter("commit de trop", "src/calcul.py")
        code, sortie = self.depot.lancer("verifier", self.dossier)
        self.refuse(code, sortie, "n'est ni le commit de départ du lancement")

    # --- (c) : codes et listes ; (d) : justifications

    def test_test_disparu_refuse_meme_justifie(self):
        identifiant = "tests/python/test_c.py::test_param[x-1]"
        code, sortie = self.partie(suites_avec(python={identifiant: None}),
                                   avant=self.justifier(f"- `{identifiant}` : 3 → 0 : retiré"), commit=("src/calcul.py", SUIVI))
        self.refuse(code, sortie, "(c) python : test(s) disparu(s) par rapport à la référence", identifiant)

    def test_echec_refuse(self):
        with self.subTest("pages : un test échoué"):
            code, sortie = self.partie(suites_avec(pages={"tests/pages/test_p.py::TestP::test_autre": ["échoué", {}]}, code_pages=1))
            self.refuse(code, sortie, "(c) pages : issue(s) dégradée(s) ou changée(s)",
                        "tests/pages/test_p.py::TestP::test_autre : passé -> échoué", "(c) codes de retour")
        with self.subTest("python : un sous-test échoué, justification sans effet"):
            identifiant = "tests/python/test_a.py::test_un"
            self.depot.git("reset", "-q", "--hard", "HEAD~1")
            code, sortie = self.partie(suites_avec(python={identifiant: ["échoué", {"passé": 4, "échoué": 1}]}, code_python=1),
                                       avant=self.justifier(f"- `{identifiant}` : 5 → 4 : un sous-test en moins"),
                                       commit=("src/calcul.py", SUIVI))
            self.assertEqual(code, 2, sortie)          # pages non lancées : leurs listes manquent
            self.assertIn("VERDICT : REFUSÉ (code 2)", sortie)

    def test_saute_en_plus_refuse_meme_justifie(self):
        code, sortie = self.partie(
            suites_avec(python={"tests/python/test_a.py::TestB::test_deux": ["sauté", {}]},
                        pages={"tests/pages/test_p.py::TestP::test_page": ["sauté", {}]}),
            avant=self.justifier("- `tests/pages/test_p.py::TestP::test_page` : 4 → 0 : sauté"), commit=("src/calcul.py", SUIVI))
        self.refuse(code, sortie, "(c) python : test(s) sauté(s) en plus", "test_deux : passé -> sauté",
                    "(c) pages : test(s) sauté(s) en plus", "test_page : passé -> sauté")

    def test_nouveau_test_saute_refuse(self):
        code, sortie = self.partie(suites_avec(python={"tests/python/test_a.py::test_neuf": ["sauté", {}]}))
        self.refuse(code, sortie, "(c) python : test(s) sauté(s) en plus", "test_neuf (nouveau, sauté)")

    def test_baisse_de_sous_tests_sans_justification_refuse(self):
        code, sortie = self.partie(suites_avec(python={"tests/python/test_a.py::test_un": ["passé", {"passé": 4}]}))
        self.refuse(code, sortie, "(c) python : nombre de sous-tests passés en baisse, sans justification exacte",
                    "tests/python/test_a.py::test_un : 5 -> 4 (aucune ligne pour ce test dans suivi.md)")

    def test_baisse_de_sous_tests_justifiee_acceptee(self):
        for fleche in ("→", "->"):
            with self.subTest(fleche=fleche):
                if fleche == "->":
                    self.depot.git("reset", "-q", "--hard", "HEAD~1")
                code, sortie = self.partie(
                    suites_avec(python={"tests/python/test_a.py::test_un": ["passé", {"passé": 4}]},
                                pages={"tests/pages/test_p.py::TestP::test_page": ["passé", {"passé": 1}]}),
                    avant=self.justifier(f"- `tests/python/test_a.py::test_un` : 5 {fleche} 4 : doublon retiré (F9)",
                                         f"- `tests/pages/test_p.py::TestP::test_page` : 4 {fleche} 1 : corpus réduit (F9)",
                                         f"- `tests/python/test_a.py::test_trois` : 2 {fleche} 1 : ligne sans baisse"),
                    commit=("src/calcul.py", SUIVI))
                self.accepte(code, sortie)
                self.assertIn("tests/python/test_a.py::test_un : 5 -> 4 : doublon retiré (F9)", sortie)
                self.assertIn("tests/pages/test_p.py::TestP::test_page : 4 -> 1 : corpus réduit (F9)", sortie)
                self.assertIn("(d) justification(s) sans baisse correspondante (sans effet) : 1", sortie)
                self.assertIn(f"(d) suivi : {SUIVI} : 3 justification(s)", sortie)

    def test_justification_aux_mauvais_nombres_refuse(self):
        identifiant = "tests/python/test_a.py::test_un"
        for n, (avant, apres) in enumerate(((5, 3), (6, 4))):
            with self.subTest(justification=f"{avant} → {apres}"):
                if n:
                    self.depot.git("reset", "-q", "--hard", "HEAD~1")
                code, sortie = self.partie(suites_avec(python={identifiant: ["passé", {"passé": 4}]}),
                                           avant=self.justifier(f"- `{identifiant}` : {avant} → {apres} : raison"),
                                           commit=("src/calcul.py", SUIVI))
                self.refuse(code, sortie, f"{identifiant} : 5 -> 4 (suivi.md donne {avant} → {apres} : nombres différents)")

    def test_justification_hors_format_sans_effet(self):
        identifiant = "tests/python/test_a.py::test_un"
        code, sortie = self.partie(suites_avec(python={identifiant: ["passé", {"passé": 4}]}),
                                   avant=self.justifier(f"- `{identifiant}` : 5 → 4"), commit=("src/calcul.py", SUIVI))
        self.refuse(code, sortie, "(d) ligne(s) de la section « Variations de sous-tests » hors format (sans effet) : 1",
                    "(aucune ligne pour ce test dans suivi.md)")

    def test_suivi_introuvable_puis_option_suivi(self):
        identifiant = "tests/python/test_a.py::test_un"
        self.depot.git("checkout", "-q", "-b", "autre")
        ailleurs = os.path.join(self.base, "suivi-ailleurs.md")
        with open(ailleurs, "w", encoding="utf-8") as f:
            f.write(TEXTE_SUIVI.format(lignes=f"- `{identifiant}` : 5 → 4 : raison donnée ailleurs"))
        code, sortie = self.partie(suites_avec(python={identifiant: ["passé", {"passé": 4}]}))
        self.refuse(code, sortie, "(d) suivi : docs/chantiers/autre/suivi.md : fichier introuvable",
                    f"{identifiant} : 5 -> 4 (suivi.md : fichier introuvable)")
        code, sortie = self.depot.lancer("verifier", self.dossier, "--suivi", ailleurs)
        self.accepte(code, sortie)
        self.assertIn("raison donnée ailleurs", sortie)

    def test_suivi_sans_section_refuse(self):
        identifiant = "tests/python/test_a.py::test_un"
        code, sortie = self.partie(suites_avec(python={identifiant: ["passé", {"passé": 4}]}),
                                   avant={SUIVI: f"# Suivi\n\n- `{identifiant}` : 5 → 4 : hors section\n"}, commit=("src/calcul.py", SUIVI))
        self.refuse(code, sortie, "section « Variations de sous-tests » absente")

    def test_code_de_retour_non_nul_refuse(self):
        code, sortie = self.partie(suites_avec(code_pages=1))
        self.refuse(code, sortie, "(c) codes de retour : global 1, Python 0, pages 1 (0 exigé partout)")

    # --- F2 : noms lus avec -z (à espaces, non ASCII) et --no-renames, dans le rapport comme dans verifier

    def test_noms_a_espaces_et_non_ascii_dans_le_commit(self):
        code, sortie = self.partie(avant={"src/é b.py": "X = 1\n"}, commit=("src/calcul.py", "src/é b.py"))
        self.accepte(code, sortie)
        self.assertIn("empreintes conformes pour les 2 fichier(s) testé(s)", sortie)
        with open(os.path.join(self.dossier, "rapport.json"), encoding="utf-8") as f:
            self.assertIn("src/é b.py", json.load(f)["fichiers_modifies"])

    def test_nom_non_ascii_change_apres_le_lancement_refuse(self):
        code, sortie = self.partie(avant={"src/é.py": "X = 1\n"}, apres={"src/é.py": "X = 2\n"}, commit=("src/calcul.py", "src/é.py"))
        self.refuse(code, sortie, "(a) fichier(s) du commit différent(s) de ce que le lancement a testé", "src/é.py : empreinte")

    def test_fichier_deplace_accepte(self):
        self.depot.git("mv", "src/calcul.py", "src/calcul_deplace.py")
        _, dossier = self.depot.rapport("partie", SUITES_DEPART)
        with open(os.path.join(dossier, "rapport.json"), encoding="utf-8") as f:
            self.assertEqual(sorted(json.load(f)["fichiers_modifies"].items()),
                             [("src/calcul.py", None), ("src/calcul_deplace.py", self.depot.git("hash-object", "--", "src/calcul_deplace.py").strip())])
        self.depot.git("commit", "-q", "-m", "déplacement")
        code, sortie = self.depot.lancer("verifier", dossier)
        self.accepte(code, sortie)
        self.assertIn("2 fichier(s) changé(s)", sortie)

    def test_fichier_manquant_code_2(self):
        _, sortie = self.partie()
        os.remove(os.path.join(self.dossier, "resultats-pages.txt"))
        code, sortie = self.depot.lancer("verifier", self.dossier)
        self.assertEqual(code, 2, sortie)
        self.assertIn("VERDICT : REFUSÉ (code 2)", sortie)
        self.assertIn("resultats-pages.txt", sortie)


# --- F2 : rapide (ce que `liste` annonce) -----------------------------------------------------------------------------------------

MANIFESTE_ESSAI = {"outils": {
    "factorisation": {"fichiers": ["factorisation/a b.py", "moteur/noyau.py"]},
    "exponentielles-logarithmes": {"fichiers": ["exponentielles-logarithmes/moteur ê.py", "moteur/noyau.py"]},
    "limites-asymptotes": {"fichiers": ["limites-asymptotes/la.py"]},
}}
# F3 : les pages d'outil (OUTILS_PAGES de lancer.py) et la variante de filière M (références et instantané resoudre à part) en viennent
REGISTRE_ESSAI = {"outils": [
    {"id": "factorisation", "chemin": "factorisation/"},
    {"id": "exponentielles-logarithmes", "chemin": "exponentielles-logarithmes/", "parametres": {"Ms": "?filiere=M", "Mr": "?filiere=M"}},
    {"id": "limites-asymptotes", "chemin": "limites-asymptotes/"},
]}

# Dépôt de forme réelle, petit : chaque module dit ce qu'il importe ou lit, pour que chaque règle de `rapide` se voie seule.
FICHIERS_RAPIDE = {
    ".gitignore": "__pycache__/\n",
    "moteur/manifeste.json": json.dumps(MANIFESTE_ESSAI, ensure_ascii=False, indent=1) + "\n",
    "commun/registre.json": json.dumps(REGISTRE_ESSAI, ensure_ascii=False, indent=1) + "\n",
    "moteur/noyau.py": "X = 1\n",
    "commun/rendu.js": "export const X = 1;\n",
    "index.html": "<!doctype html>\n",
    "factorisation/a b.py": "import noyau\n",
    "factorisation/index.html": "<script>const EXEMPLES=[\"x+1\"];\n</script>\n",
    "exponentielles-logarithmes/moteur ê.py": "import noyau\n",
    "exponentielles-logarithmes/index.html": "<script>const EXEMPLES=[\"e^x\"];\n</script>\n",
    "limites-asymptotes/la.py": "X = 1\n",
    "limites-asymptotes/index.html": "<!doctype html>\n",
    "tests/python/cas.py": 'import os\nPAGE = os.path.join("factorisation", "index.html")\n',
    "tests/python/cas_el.py": "from cas import PAGE\n",
    "tests/python/é.py": "X = 1\n",
    "tests/python/outil_commun.py": "X = 1\n",
    "tests/python/test_accent.py": "import é\n",
    "tests/python/test_a b.py": "X = 1\n",
    "tests/python/test_chaine.py": "import outil_commun\n",
    "tests/python/test_isole.py": "X = 1\n",
    "tests/python/test_donnees.py": 'import os, sys\nsys.path.insert(0, os.path.join(os.path.dirname(__file__), "donnees"))\nimport corpus\n',
    "tests/python/test_par_donnees.py": "import test_donnees\n",
    "tests/python/test_instantanes.py": 'import os\nfrom cas import PAGE\nDOSSIER = os.path.join(os.path.dirname(__file__), "instantanes")\n',
    "tests/python/test_instantanes_resoudre.py": 'import os\nimport cas_el\nDOSSIER = os.path.join("instantanes", "resoudre")\n',
    "tests/python/test_json_strict.py": 'import os\nimport noyau\nDOSSIER = os.path.join(os.path.dirname(__file__), "instantanes")\n',
    "tests/python/test_vocabulaire.py": 'import os\nDOSSIER = os.path.join(os.path.dirname(__file__), "instantanes")\n',
    "tests/python/test_refs.py": 'import os\nDOSSIER = os.path.join("..", "pages", "references")\n',
    "tests/python/test_lancer.py": "X = 1\n",
    "tests/python/test_manifeste.py": "X = 1\n",
    "tests/python/test_accueil.py": "X = 1\n",
    "tests/python/test_source_unique.py": "X = 1\n",
    "tests/python/donnees/corpus.py": "CORPUS = []\n",
    "tests/python/donnees/table.json": "{}\n",
    "tests/python/instantanes/factorisation.json": "{}\n",
    "tests/python/instantanes/resoudre/factorisation.json": "{}\n",
    "tests/python/instantanes/resoudre/exponentielles-logarithmes-M.json": "{}\n",
    "tests/pages/rendu.py": "import os\n",
    "tests/pages/test_rendu.py": "import rendu\n",
    "tests/pages/references/factorisation.json": "{}\n",
    "tests/pages/references/exponentielles-logarithmes-M.json": "{}\n",
    "tests/pages/references/graphique-traces.json": "{}\n",
}
FUMEE = {"test_accueil.py", "test_manifeste.py", "test_source_unique.py"}
INSTANTANES_ET_JSON = {"test_instantanes.py", "test_instantanes_resoudre.py", "test_json_strict.py"}
TOUTES_LES_PAGES = {"tous"}
EXP_LOG = {"exponentielles-logarithmes", "exponentielles-logarithmes-M"}


class ModeleRapide(ModeleDepot):
    """Dépôt de départ des essais de `rapide` : les scripts de commande (rapport_pytest.py compris) et FICHIERS_RAPIDE, commités."""
    _modele = None

    @staticmethod
    def _construire(depot):
        os.makedirs(depot.racine)
        depot.git("init", "-q", "-b", BRANCHE)
        depot.verifier_isole()
        for chemin in SCRIPTS + ("tests/rapport_pytest.py",):
            with open(os.path.join(RACINE, chemin), encoding="utf-8") as f:
                depot.ecrire(chemin, f.read())
        for chemin, contenu in FICHIERS_RAPIDE.items():
            depot.ecrire(chemin, contenu)
        depot.git("add", "-A")                                   # dépôt jetable : tout ce qui vient d'être écrit
        depot.git("commit", "-q", "-m", "départ")


class TestRapide(unittest.TestCase):
    """`lancer.py liste` (ce que `rapide` lancerait) sur des modifications construites : règles du chantier fondations, F2."""

    def setUp(self):
        self.base = tempfile.mkdtemp(prefix="test-rapide-")
        self.addCleanup(shutil.rmtree, self.base, True)
        self.depot = ModeleRapide.copie(self.base)

    def liste(self, *options):
        """`liste [options]` -> (fichiers annoncés, tests Python annoncés, pages annoncées), chacun en ensemble."""
        code, sortie = self.depot.lancer("liste", *options)
        self.assertEqual(code, 0, sortie)
        lignes = sortie.splitlines()
        self.assertEqual(len(lignes), 3, sortie)
        valeurs = []
        for ligne, debut in zip(lignes, ("fichiers modifiés", "tests Python :", "pages (corpus réduit) :")):
            self.assertTrue(ligne.startswith(debut), sortie)
            reste = ligne.split(" : ", 1)[1]
            valeurs.append(set() if reste in ("aucun", "aucune") else set(reste.split(", ")))
        return valeurs

    def modifier(self, *chemins):
        for chemin in chemins:
            self.depot.ecrire(chemin, self.depot.lire(chemin) + "# modifié\n")

    def annonce(self, fichiers, tests, pages, *options):
        """Vérifie l'annonce de `liste` : `tests` sans les tests de fumée, toujours attendus."""
        annonces = self.liste(*options)
        self.assertEqual(annonces, [set(fichiers), set(tests) | FUMEE, set(pages)])

    def test_rien_de_modifie(self):
        self.annonce((), (), ())

    def test_noms_a_espaces_et_non_ascii(self):
        self.modifier("factorisation/a b.py", "tests/python/é.py", "tests/python/test_a b.py")
        self.depot.ecrire("tests/python/test_nouveau é.py", "import é\n")          # non suivi
        attendus = (["factorisation/a b.py", "tests/python/é.py", "tests/python/test_a b.py", "tests/python/test_nouveau é.py"],
                    ["test_accent.py", "test_a b.py", "test_nouveau é.py"], ["factorisation"])
        self.annonce(*attendus)
        self.depot.git("add", "--", *attendus[0])
        self.annonce(*attendus)                                                    # indexés
        self.depot.git("commit", "-q", "-m", "noms")
        self.annonce((), (), ())                                                   # arbre propre : la fumée seule
        self.annonce(*attendus, "--depuis", "HEAD~1")

    def test_fichier_supprime_relance_ses_dependants(self):
        os.remove(os.path.join(self.depot.racine, "tests/python/outil_commun.py"))
        attendus = (["tests/python/outil_commun.py (supprimé)"], ["test_chaine.py"], ())
        self.annonce(*attendus)
        self.depot.git("rm", "-q", "--cached", "--", "tests/python/outil_commun.py")
        self.depot.git("commit", "-q", "-m", "suppression")
        self.annonce((), (), ())
        self.annonce(*attendus, "--depuis", "HEAD~1")

    def test_test_supprime_et_module_de_moteur_supprime(self):
        with self.subTest("un test supprimé n'est pas lancé"):
            self.depot.git("rm", "-q", "--", "tests/python/test_chaine.py")
            self.annonce(["tests/python/test_chaine.py (supprimé)"], (), ())
        with self.subTest("module de moteur supprimé : ses dépendants et les pages qui le chargent"):
            self.depot.git("reset", "-q", "--hard")
            self.depot.git("rm", "-q", "--", "moteur/noyau.py")
            self.annonce(["moteur/noyau.py (supprimé)"], ["test_json_strict.py"], {"factorisation"} | EXP_LOG)

    def test_fichier_deplace(self):
        self.depot.git("mv", "tests/python/outil_commun.py", "tests/python/outil_deplace.py")
        attendus = (["tests/python/outil_commun.py (supprimé)", "tests/python/outil_deplace.py"], ["test_chaine.py"], ())
        self.annonce(*attendus)
        self.depot.git("commit", "-q", "-m", "déplacement")
        self.annonce(*attendus, "--depuis", "HEAD~1")

    def test_donnees(self):
        with self.subTest("module de donnees/ : ses importeurs et ceux qui nomment le dossier, puis leurs dépendants"):
            self.modifier("tests/python/donnees/corpus.py")
            self.annonce(["tests/python/donnees/corpus.py"], ["test_donnees.py", "test_par_donnees.py"], ())
        with self.subTest("fichier non Python de donnees/ (modifié, supprimé, nouveau)"):
            self.depot.git("reset", "-q", "--hard")
            os.remove(os.path.join(self.depot.racine, "tests/python/donnees/table.json"))
            self.depot.ecrire("tests/python/donnees/nouveau é.json", "{}\n")
            self.annonce(["tests/python/donnees/table.json (supprimé)", "tests/python/donnees/nouveau é.json"],
                         ["test_donnees.py", "test_par_donnees.py"], ())
        with self.subTest("aucun module ne nomme donnees/ : tous les tests Python"):
            self.depot.git("reset", "-q", "--hard")
            self.depot.git("clean", "-q", "-f")
            self.depot.ecrire("tests/python/test_donnees.py", "import corpus\n")
            self.depot.git("commit", "-q", "-am", "sans le nom du dossier")
            self.modifier("tests/python/donnees/table.json")
            fichiers, tests, pages = self.liste()
            self.assertEqual((fichiers, tests, pages),
                             ({"tests/python/donnees/table.json"}, {"tous (tests/python : on ne sait pas borner)"}, set()))

    def test_page(self):
        for page, outils in (("factorisation/index.html", {"factorisation"}), ("exponentielles-logarithmes/index.html", EXP_LOG),
                             ("limites-asymptotes/index.html", {"limites-asymptotes"})):
            with self.subTest(page=page):
                self.depot.git("reset", "-q", "--hard")
                self.modifier(page)
                self.annonce([page], INSTANTANES_ET_JSON, outils)

    def test_page_commitee_depuis(self):
        self.modifier("factorisation/index.html")
        self.depot.commiter("page", "factorisation/index.html")
        self.annonce(["factorisation/index.html"], INSTANTANES_ET_JSON, ["factorisation"], "--depuis", "HEAD~1")

    def test_cas(self):
        with self.subTest("cas_el.py : ses importeurs, et test_instantanes*, test_json_strict"):
            self.modifier("tests/python/cas_el.py")
            self.annonce(["tests/python/cas_el.py"], INSTANTANES_ET_JSON, ())
        with self.subTest("cas.py supprimé"):
            self.depot.git("reset", "-q", "--hard")
            self.depot.git("rm", "-q", "--", "tests/python/cas.py")
            self.annonce(["tests/python/cas.py (supprimé)"], INSTANTANES_ET_JSON, ())

    def test_instantane(self):
        with self.subTest("instantané : test_instantanes*, test_json_strict et les modules qui nomment instantanes/"):
            self.modifier("tests/python/instantanes/factorisation.json")
            self.annonce(["tests/python/instantanes/factorisation.json"], INSTANTANES_ET_JSON | {"test_vocabulaire.py"}, ())
        for nom, outils in (("factorisation", {"factorisation"}), ("exponentielles-logarithmes-M", EXP_LOG)):
            with self.subTest(f"instantané resoudre {nom} : en plus, la page de l'outil (test_comportement le lit)"):
                self.depot.git("reset", "-q", "--hard")
                chemin = f"tests/python/instantanes/resoudre/{nom}.json"
                self.modifier(chemin)
                self.annonce([chemin], INSTANTANES_ET_JSON | {"test_vocabulaire.py"}, outils)
        with self.subTest("instantané supprimé"):
            self.depot.git("reset", "-q", "--hard")
            self.depot.git("rm", "-q", "--", "tests/python/instantanes/factorisation.json")
            self.annonce(["tests/python/instantanes/factorisation.json (supprimé)"], INSTANTANES_ET_JSON | {"test_vocabulaire.py"}, ())

    def test_reference_de_page(self):
        for nom, outils in (("factorisation", {"factorisation"}), ("exponentielles-logarithmes-M", EXP_LOG),
                            ("graphique-traces", TOUTES_LES_PAGES)):
            with self.subTest(reference=nom):
                self.depot.git("reset", "-q", "--hard")
                chemin = f"tests/pages/references/{nom}.json"
                self.modifier(chemin)
                self.annonce([chemin], ["test_refs.py"], outils)

    def test_moteur_relance_la_page_de_l_outil(self):
        for chemin, tests, outils in (("exponentielles-logarithmes/moteur ê.py", (), EXP_LOG),
                                      ("moteur/noyau.py", ["test_json_strict.py"], {"factorisation"} | EXP_LOG),
                                      ("limites-asymptotes/la.py", (), {"limites-asymptotes"})):
            with self.subTest(moteur=chemin):
                self.depot.git("reset", "-q", "--hard")
                self.modifier(chemin)
                self.annonce([chemin], tests, outils)

    def test_moteur_relance_les_lecteurs_des_moteurs(self):
        """F4 : test_imports.py et test_noyau.py lisent les .py des moteurs par leur chemin (ast) ; un .py des dossiers des moteurs
        (modifié, nouveau ou supprimé) les relance, une page ou un module de tests non."""
        lecteurs = {"test_imports.py", "test_noyau.py"}
        for nom in lecteurs:
            self.depot.ecrire(f"tests/python/{nom}", "X = 1\n")
        self.depot.commiter("lecteurs", *(f"tests/python/{nom}" for nom in lecteurs))
        for chemin, tests, outils in (("factorisation/a b.py", lecteurs, {"factorisation"}),
                                      ("moteur/noyau.py", lecteurs | {"test_json_strict.py"}, {"factorisation"} | EXP_LOG),
                                      ("factorisation/index.html", INSTANTANES_ET_JSON, {"factorisation"}),
                                      ("tests/python/é.py", {"test_accent.py"}, ())):
            with self.subTest(modifie=chemin):
                self.depot.git("reset", "-q", "--hard")
                self.modifier(chemin)
                self.annonce([chemin], tests, outils)
        with self.subTest("module nouveau (non suivi) d'un dossier de moteur"):
            self.depot.git("reset", "-q", "--hard")
            self.depot.ecrire("limites-asymptotes/nouveau.py", "import noyau\n")
            self.annonce(["limites-asymptotes/nouveau.py"], lecteurs, TOUTES_LES_PAGES)
            os.remove(os.path.join(self.depot.racine, "limites-asymptotes/nouveau.py"))
        with self.subTest("module de moteur supprimé, puis commité (--depuis)"):
            self.depot.git("reset", "-q", "--hard")
            self.depot.git("rm", "-q", "--", "exponentielles-logarithmes/moteur ê.py")
            attendus = (["exponentielles-logarithmes/moteur ê.py (supprimé)"], lecteurs, EXP_LOG)
            self.annonce(*attendus)
            self.depot.git("commit", "-q", "-m", "suppression")
            self.annonce(*attendus, "--depuis", "HEAD~1")

    def test_scripts_de_commande_relancent_test_lancer(self):
        for chemin in SCRIPTS + ("tests/rapport_pytest.py",):
            with self.subTest(script=chemin):
                self.depot.git("reset", "-q", "--hard")
                self.modifier(chemin)
                self.annonce([chemin], ["test_lancer.py"], ())

    def test_manifeste_et_registre_relancent_les_listes_derivees(self):
        """F3 : les listes d'outils des tests dérivent de outils_du_site.py, qui lit le manifeste et le registre."""
        self.depot.ecrire("tests/python/test_listes.py", "import outils_du_site\n")
        self.depot.commiter("listes", "tests/python/test_listes.py")
        for chemin in ("moteur/manifeste.json", "commun/registre.json"):
            with self.subTest(source=chemin):
                self.depot.git("reset", "-q", "--hard")
                self.depot.ecrire(chemin, self.depot.lire(chemin) + "\n")            # encore du JSON valide
                self.annonce([chemin], ["test_listes.py"], TOUTES_LES_PAGES)

    def test_liste_des_outils_illisible_relance_tout(self):
        """F3 : registre (ou manifeste) illisible : on ne sait pas borner, tous les tests Python et toutes les pages."""
        for chemin in ("commun/registre.json", "moteur/manifeste.json"):
            with self.subTest(source=chemin):
                self.depot.git("reset", "-q", "--hard")
                self.depot.ecrire(chemin, "{")
                fichiers, tests, pages = self.liste()
                self.assertEqual((fichiers, pages), ({chemin}, TOUTES_LES_PAGES))
                self.assertTrue(any(t.startswith("tous (tests/python : on ne sait pas borner : liste des outils illisible") for t in tests),
                                tests)

    def test_sans_effet_sur_les_autres_tests(self):
        self.modifier("tests/python/test_isole.py", "commun/rendu.js")
        self.annonce(["tests/python/test_isole.py", "commun/rendu.js"], ["test_isole.py"], TOUTES_LES_PAGES)


if __name__ == "__main__":
    unittest.main()
