"""Graphe des imports internes du moteur, figé (chantier fondations, F4 ; revue de structure, R6 ; docs/architecture.md, règle A1).

Modules : tous les .py de moteur/ et des dossiers d'outil du manifeste (outils_du_site.dossiers_moteurs()), désignés par leur nom de
module (Pyodide les écrit à plat : test_noms_de_modules_uniques). Arêtes extraites par `ast`, sans rien importer : `import x`,
`import x.y`, `from x import y`, relatifs (`from . import x`, `from .x import y`), `importlib.import_module("x")` et
`__import__("x")` ; une arête est notée « a -> b » si l'import s'exécute au chargement de `a` (tête du fichier, corps de classe,
bloc if/try de tête, décorateurs et valeurs par défaut), « a ~> b » s'il est paresseux (dans le corps d'une fonction). Les imports
vers des modules extérieurs (bibliothèque standard, SymPy, mpmath) ne sont pas des arêtes.

La liste blanche est exacte : ARETES (arêtes permises par les couches, chacune avec sa raison) plus les arêtes des EXCEPTIONS
nommées (docs/architecture.md, § 1 pour l'assemblage voulu de l'Étude complète, § 5 pour la dette ; chacune avec sa règle et le
chantier qui la résorbe). Une arête nouvelle ou disparue fait échouer `test_aretes_figees`. Les couches de § 1 sont vérifiées
mécaniquement (`couche`, `violation`) : aucune arête de ARETES ne les viole, aucune n'est sur un cycle, et chaque exception sert.

Ajouter une arête : exprès, dans ARETES avec sa raison si elle respecte les couches ; sinon elle se discute avant d'être écrite
(CLAUDE.md, Architecture) et n'entre que comme exception nommée, avec la règle qu'elle enfreint et le chantier qui la résorbe, après
accord de l'enseignant (et dans docs/architecture.md, § 5)."""
import ast
import os
import unittest

from moteurs import RACINE
import outils_du_site

# Couche 1, rangée hors de moteur/ : la base (arbre, parseur, polynômes, pont SymPy), dans le dossier de l'outil ED ; les autres
# outils la prennent par sa façade moteur/noyau.py (test_noyau.py), seuls noyau et l'outil ED (resoudre_ed) l'importent directement.
BASE = "ensemble_def"
FACADE_DE_LA_BASE = "noyau"
BRIQUES = "moteur"                        # couche 1 : les briques communes

# Arêtes permises par les couches (docs/architecture.md, § 1), avec leur raison. Arête paresseuse : « ~> ».
ARETES = {
    # couche 1 : briques
    "noyau -> ensemble_def": "façade de la base (noyau réexporte ensemble_def)",
    "expr -> noyau": "brique : ErreurSaisie, l'erreur de saisie commune (briques-communes, B1)",
    "expr -> nombres": "brique : notation suisse des nombres, lus et écrits par l'arbre (briques-communes, B1)",
    "chaine -> expr": "brique : les chaînes du corrigé s'écrivent avec le TeX de l'arbre (briques-communes, B2)",
    "chaine -> sortie": "brique : une chaîne donne son bloc « chaine » (bloc_chaine, constructeurs de sortie.py ; briques-communes, B3)",
    "polynomes -> expr": "brique : les coefficients exacts se lisent sur l'arbre (pq, const ; equations-2e-degre, P1)",
    "second_degre -> polynomes": "brique : un polynôme saisi devient ses coefficients exacts (vers_polynome sur pq ; equations-2e-degre, P1)",
    "second_degre -> noyau": "brique : la base par sa façade (squarefree, racine_q pour p + q√m, pn, deg ; equations-2e-degre, P1)",
    "second_degre -> expr": "brique : vers_polynome vérifie qu'il n'y a qu'une lettre dans l'arbre (variables ; equations-2e-degre, P1)",
    "second_degre -> nombres": "brique : valeurs approchées garanties par nombres.approx (approx_garantie, E14 ; equations-2e-degre, P1)",
    "second_degre -> chaine": "brique : la rédaction écrit chaque étape comme un segment de chaîne du corrigé (Chaine, rangees_chaine, "
                              "bloc_rangees ; equations-2e-degre, P2b)",
    "second_degre -> sortie": "brique : tableau S-P (tableau_essais), S encadré (resultat_lim) et ligne ≈ de la résolution (equations-2e-degre, "
                              "P2b)",
    # outil ED : la base est son moteur
    "resoudre_ed -> ensemble_def": "adaptateur de l'outil ED, sur la base directement (légitime : rapport de la revue, § 1.2)",
    "resoudre_ed -> sortie": "adaptateur : brique de sortie",
    # Dérivée et variations
    "derivee_variations -> noyau": "moteur : la base par sa façade",
    "resoudre_dv -> noyau": "adaptateur : la base par sa façade",
    "resoudre_dv -> sortie": "adaptateur : brique de sortie",
    "resoudre_dv -> derivee_variations": "adaptateur : le moteur de son outil",
    # Limites et asymptotes
    "limites_asymptotes -> noyau": "moteur : la base par sa façade",
    "redaction_bh -> noyau": "moteur : la base par sa façade",
    "redaction_bh -> sortie": "moteur : brique de sortie (blocs de la rédaction BH)",
    "resoudre_la -> noyau": "adaptateur : la base par sa façade",
    "resoudre_la -> sortie": "adaptateur : brique de sortie",
    "resoudre_la -> limites_asymptotes": "adaptateur : le moteur de son outil",
    # Étude complète (hors assemblage : voir EXCEPTIONS)
    "etude_complete -> noyau": "moteur : la base par sa façade",
    "etude_complete -> parties": "moteur : un moteur de son outil",
    "parties -> nombres": "moteur : brique des nombres",
    "parties -> noyau": "moteur : la base par sa façade",
    "parties -> sortie": "moteur : brique de sortie (blocs des parties)",
    "resoudre_ec -> noyau": "adaptateur : la base par sa façade",
    "resoudre_ec -> sortie": "adaptateur : brique de sortie",
    "resoudre_ec -> parties": "adaptateur : un moteur de son outil",
    "resoudre_ec -> etude_complete": "adaptateur : le moteur de son outil",
    # Factorisation
    "factorisation -> noyau": "moteur : la base par sa façade",
    "resoudre_fa -> noyau": "adaptateur : la base par sa façade",
    "resoudre_fa -> sortie": "adaptateur : brique de sortie",
    "resoudre_fa -> factorisation": "adaptateur : le moteur de son outil",
    # Exponentielles et logarithmes
    "exp_log -> noyau": "moteur : la base par sa façade",
    "exp_log -> nombres": "moteur : brique des nombres",
    "exp_log -> expr": "moteur : brique des expressions (arbre, TeX, lecture), réexportée sous les mêmes noms (briques-communes, B1)",
    "exp_log -> chaine": "moteur : brique des chaînes du corrigé, réexportée sous les mêmes noms (briques-communes, B2)",
    "exp_log -> polynomes": "moteur : brique des polynômes exacts (_Hors, _const, _padd…), réexportée sous les mêmes noms (equations-2e-degre, P1)",
    "exp_log_m -> noyau": "moteur : la base par sa façade",
    "exp_log_m -> polynomes": "moteur : brique des polynômes exacts (_pq, _pmul_n, DEGRE_MAX), réexportée sous les mêmes noms (equations-2e-degre, P1)",
    "resoudre_el -> noyau": "adaptateur : la base par sa façade",
    "resoudre_el -> sortie": "adaptateur : brique de sortie",
    "resoudre_el -> exp_log": "adaptateur : un moteur de son outil",
    "resoudre_el -> exp_log_m": "adaptateur : un moteur de son outil (filière M)",
    # Équations du 2e degré (equations-2e-degre, P3 pour equations.py, déclarées en P5 quand l'outil entre au manifeste)
    "equations -> expr": "moteur : la saisie « membre = membre » est lue par la brique des expressions (Lexique, lire_membres, "
                         "variables, a_des_decimaux)",
    "equations -> noyau": "moteur : la base par sa façade (ErreurSaisie, l'erreur de saisie commune)",
    "equations -> polynomes": "moteur : constantes exactes de l'arbre (const : exposant, dénominateur nul ; P3, écart au plan noté)",
    "equations -> second_degre": "moteur : la brique du 2e degré borne la saisie (vers_polynome, HorsBornes, § 13.5)",
    "resoudre_eq -> equations": "adaptateur : le moteur de son outil (lecture et analyse de la saisie)",
    "resoudre_eq -> second_degre": "adaptateur : la brique du 2e degré (resoudre_equation, blocs, ecrire_enonce)",
    "resoudre_eq -> sortie": "adaptateur : brique de sortie",
    "resoudre_eq -> chaine": "adaptateur : le TeX de l'énoncé (tex_element de l'équation écrite par ecrire_enonce)",
    "resoudre_eq -> expr": "adaptateur : l'aperçu syntaxique pendant la frappe (lire_membres avec le lexique de l'outil, tex)",
    "resoudre_eq -> noyau": "adaptateur : la base par sa façade (ErreurSaisie, json_strict)",
}

# Exceptions nommées : arêtes qui violent les couches (motif « couches ») ou qui sont sur un cycle (motif « cycle ») ; chaque motif
# listé doit valoir pour chaque arête de l'exception (test_exceptions_utiles).
EXCEPTIONS = {
    "assemblage de l'Étude complète": {
        "aretes": ["etude_complete -> derivee_variations", "etude_complete -> limites_asymptotes",
                   "parties ~> derivee_variations", "resoudre_ec -> resoudre_dv", "resoudre_ec -> resoudre_la"],
        "motifs": ("couches",),
        "regle": "A1 (§ 1 : seule exception voulue, l'EC assemble DV, LA et ED ; parties ~> derivee_variations en fait partie)",
        "chantier": "aucun : voulue",
    },
    "cycle limites_asymptotes ⇄ redaction_bh": {
        "aretes": ["limites_asymptotes -> redaction_bh", "redaction_bh -> limites_asymptotes"],
        "motifs": ("cycle",),
        "regle": "A1, A6 (21 noms privés de LA lus par redaction_bh ; import de fin de fichier)",
        "chantier": "R11",
    },
    "cycle exp_log ⇄ exp_log_m": {
        "aretes": ["exp_log ~> exp_log_m", "exp_log_m -> exp_log", "exp_log_m ~> exp_log"],
        "motifs": ("cycle",),
        "regle": "A1, A6 (31 noms privés ; exp_log_m ~> exp_log : _GABARITS, redondant)",
        "chantier": "R11",
    },
    "parties importe l'adaptateur resoudre_ed": {
        "aretes": ["parties -> resoudre_ed"],
        "motifs": ("couches",),
        "regle": "A1 (un moteur importe un adaptateur, d'un autre outil)",
        "chantier": "R11",
    },
    "resoudre_el importe l'adaptateur resoudre_ed": {
        "aretes": ["resoudre_el -> resoudre_ed"],
        "motifs": ("couches",),
        "regle": "A1 (un adaptateur importe l'adaptateur d'un autre outil)",
        "chantier": "R11",
    },
}

COMMENT_AJOUTER = (
    "Une arête nouvelle s'ajoute exprès, avec sa raison : dans ARETES de tests/python/test_imports.py si elle respecte les couches "
    "(docs/architecture.md, § 1 et règle A1) ; sinon elle se discute avant d'être écrite (CLAUDE.md, Architecture) et n'entre que "
    "comme exception nommée dans EXCEPTIONS (règle enfreinte, chantier qui la résorbe), après accord de l'enseignant, et dans "
    "docs/architecture.md § 5. Une arête disparue se retire de ARETES ou EXCEPTIONS (la liste reste exacte).")


def modules_du_moteur(racine=RACINE):
    """{nom de module: [chemins]} des .py de moteur/ et des dossiers d'outil du manifeste (une liste : un nom en double se voit)."""
    dossiers = list(outils_du_site.dossiers_moteurs(racine))
    if BRIQUES not in dossiers:
        dossiers.append(BRIQUES)
    modules = {}
    for dossier in dossiers:
        for nom in sorted(os.listdir(os.path.join(racine, dossier))):
            if nom.endswith(".py"):
                modules.setdefault(nom[:-len(".py")], []).append(f"{dossier}/{nom}")
    return modules


def cibles(noeud):
    """Noms de premier niveau des modules qu'importe `noeud` ([] s'il n'importe rien)."""
    if isinstance(noeud, ast.Import):
        return [a.name.split(".")[0] for a in noeud.names]
    if isinstance(noeud, ast.ImportFrom):
        if noeud.level and not noeud.module:                         # from . import x, y
            return [a.name for a in noeud.names]
        return [noeud.module.split(".")[0]]
    if isinstance(noeud, ast.Call) and noeud.args and isinstance(noeud.args[0], ast.Constant) \
            and isinstance(noeud.args[0].value, str):
        f = noeud.func
        nom = f.id if isinstance(f, ast.Name) else f.attr if isinstance(f, ast.Attribute) else None
        if nom in ("import_module", "__import__"):
            return [noeud.args[0].value.lstrip(".").split(".")[0]]
    return []


def imports_du_source(source, nom_du_fichier="<source>"):
    """[(module importé, paresseux, ligne)] de tous les imports du source, dans l'ordre du parcours."""
    trouves = []

    def parcourir(noeud, paresseux):
        trouves.extend((c, paresseux, noeud.lineno) for c in cibles(noeud))
        if isinstance(noeud, (ast.FunctionDef, ast.AsyncFunctionDef)):
            for n in [*noeud.decorator_list, noeud.args] + ([noeud.returns] if noeud.returns else []):
                parcourir(n, paresseux)                              # évalués à la définition
            for n in noeud.body:
                parcourir(n, True)
        elif isinstance(noeud, ast.Lambda):
            parcourir(noeud.args, paresseux)
            parcourir(noeud.body, True)
        else:
            for n in ast.iter_child_nodes(noeud):
                parcourir(n, paresseux)

    parcourir(ast.parse(source, filename=nom_du_fichier), False)
    return trouves


def graphe(racine=RACINE):
    """{arête « a -> b » ou « a ~> b »: [« chemin l. N »]} des imports internes (vers un module de modules_du_moteur)."""
    modules = modules_du_moteur(racine)
    aretes = {}
    for nom, chemins in sorted(modules.items()):
        for chemin in chemins:
            with open(os.path.join(racine, chemin), encoding="utf-8") as f:
                source = f.read()
            for cible, paresseux, ligne in imports_du_source(source, chemin):
                if cible in modules:
                    aretes.setdefault(f"{nom} {'~>' if paresseux else '->'} {cible}", []).append(f"{chemin} l. {ligne}")
    return aretes


def extremites(arete):
    a, _, b = arete.split()
    return a, b


def couche(nom, racine=RACINE):
    """(couche de docs/architecture.md § 1, outil) d'un module : 1 pour les briques (moteur/) et la base (outil ED) ; 3 pour
    l'adaptateur d'un outil (son `module` au manifeste) ; 2 pour les autres .py d'un dossier d'outil (moteurs d'outil)."""
    manifeste = outils_du_site.manifeste(racine)
    chemin = modules_du_moteur(racine)[nom][0]
    dossier = os.path.dirname(chemin)
    if dossier == BRIQUES:
        return 1, None
    if nom == BASE:
        return 1, dossier
    if dossier in manifeste and manifeste[dossier]["module"] == nom:
        return 3, dossier
    return 2, dossier


def violation(arete, racine=RACINE):
    """Règle des couches (§ 1) que viole l'arête, ou None."""
    a, b = extremites(arete)
    (ca, oa), (cb, ob) = couche(a, racine), couche(b, racine)
    noms = {1: "une brique", 2: "un moteur d'outil", 3: "un adaptateur"}
    if cb > ca:
        return f"{noms[ca]} importe {noms[cb]} (couche {cb} au-dessus de {ca})"
    if ca >= 2 and cb >= 2 and oa != ob:
        return f"{noms[ca]} importe {noms[cb]} d'un autre outil ({ob})"
    if b == BASE and a != FACADE_DE_LA_BASE and ca >= 2 and oa != ob:
        return f"la base ({BASE}) importée sans sa façade ({FACADE_DE_LA_BASE}) par un autre outil"
    return None


def sur_un_cycle(aretes):
    """Arêtes (parmi `aretes`) qui sont sur un cycle du graphe (sans tenir compte de « -> » ou « ~> »)."""
    suivants = {}
    for arete in aretes:
        a, b = extremites(arete)
        suivants.setdefault(a, set()).add(b)

    def atteint(depart, but):
        vus, a_voir = set(), [depart]
        while a_voir:
            n = a_voir.pop()
            if n == but:
                return True
            if n not in vus:
                vus.add(n)
                a_voir.extend(suivants.get(n, ()))
        return False
    return {arete for arete in aretes if atteint(extremites(arete)[1], extremites(arete)[0])}


def aretes_des_exceptions():
    return {arete: nom for nom, e in EXCEPTIONS.items() for arete in e["aretes"]}


class TestGrapheDesImports(unittest.TestCase):
    """Règle A1 : les imports internes suivent les couches ; la liste des arêtes est figée."""

    @classmethod
    def setUpClass(cls):
        cls.graphe = graphe()

    def test_noms_de_modules_uniques(self):
        """Pyodide écrit les fichiers à plat : un nom de module ne désigne qu'un fichier (sinon le graphe serait ambigu)."""
        doubles = {nom: chemins for nom, chemins in modules_du_moteur().items() if len(chemins) > 1}
        self.assertEqual(doubles, {})

    def test_aretes_figees(self):
        permises = set(ARETES) | set(aretes_des_exceptions())
        nouvelles = sorted(set(self.graphe) - permises)
        disparues = sorted(permises - set(self.graphe))
        self.assertEqual(nouvelles, [], "arête(s) nouvelle(s) : "
                         + "; ".join(f"{a} ({', '.join(self.graphe[a])})" for a in nouvelles) + ". " + COMMENT_AJOUTER)
        self.assertEqual(disparues, [], "arête(s) disparue(s) : " + "; ".join(disparues) + ". " + COMMENT_AJOUTER)

    def test_liste_bien_formee(self):
        exceptions = aretes_des_exceptions()
        self.assertEqual(set(ARETES) & set(exceptions), set(), "une arête est soit dans ARETES, soit dans une exception")
        toutes = [a for e in EXCEPTIONS.values() for a in e["aretes"]]
        self.assertEqual(len(toutes), len(set(toutes)), "une arête dans deux exceptions")
        modules = modules_du_moteur()
        for arete in list(ARETES) + toutes:
            with self.subTest(arete=arete):
                morceaux = arete.split()
                self.assertEqual(len(morceaux), 3)
                self.assertIn(morceaux[1], ("->", "~>"))
                self.assertIn(morceaux[0], modules)
                self.assertIn(morceaux[2], modules)
        for arete, raison in ARETES.items():
            with self.subTest(raison=arete):
                self.assertTrue(raison.strip(), "raison manquante")
        for nom, e in EXCEPTIONS.items():
            with self.subTest(exception=nom):
                self.assertEqual(set(e), {"aretes", "motifs", "regle", "chantier"})
                self.assertTrue(e["motifs"] and set(e["motifs"]) <= {"couches", "cycle"})
                self.assertTrue(e["aretes"] and e["regle"].strip() and e["chantier"].strip())

    def test_couches(self):
        """Aucune arête hors exception « couches » ne viole les couches de docs/architecture.md § 1."""
        exceptions = aretes_des_exceptions()
        for arete in sorted(self.graphe):
            raison = violation(arete)
            if raison and "couches" not in EXCEPTIONS.get(exceptions.get(arete), {}).get("motifs", ()):
                with self.subTest(arete=arete):
                    self.fail(f"{arete} ({', '.join(self.graphe[arete])}) : {raison}. " + COMMENT_AJOUTER)

    def test_aucun_cycle_hors_exceptions(self):
        exceptions = aretes_des_exceptions()
        for arete in sorted(sur_un_cycle(self.graphe)):
            if "cycle" not in EXCEPTIONS.get(exceptions.get(arete), {}).get("motifs", ()):
                with self.subTest(arete=arete):
                    self.fail(f"{arete} ({', '.join(self.graphe[arete])}) est sur un cycle. " + COMMENT_AJOUTER)

    def test_exceptions_utiles(self):
        """Chaque arête d'une exception enfreint vraiment ce que dit son motif ; sinon elle va dans ARETES (ou disparaît)."""
        cycles = sur_un_cycle(self.graphe)
        for nom, e in EXCEPTIONS.items():
            for arete in e["aretes"]:
                with self.subTest(exception=nom, arete=arete):
                    if "couches" in e["motifs"]:
                        self.assertIsNotNone(violation(arete), "respecte les couches : motif « couches » à retirer (ou ARETES)")
                    if "cycle" in e["motifs"]:
                        self.assertIn(arete, cycles, "n'est sur aucun cycle : motif « cycle » à retirer (ou ARETES)")


class TestExtraction(unittest.TestCase):
    """L'extraction voit chaque forme d'import, de tête ou paresseuse."""

    SOURCE = (
        "import a\n"
        "import b.sous as bb\n"
        "from c import x\n"
        "from . import d, e\n"
        "from .f import y\n"
        "import json, sympy\n"
        "if True:\n"
        "    import g\n"
        "try:\n"
        "    from h import z\n"
        "except ImportError:\n"
        "    pass\n"
        "class K:\n"
        "    import i\n"
        "    def m(self):\n"
        "        import j\n"
        "def f(p=__import__('k')):\n"
        "    from l import w\n"
        "    def g():\n"
        "        import importlib\n"
        "        importlib.import_module('m')\n"
        "@decorer(__import__('n'))\n"
        "async def h():\n"
        "    import o\n"
        "q = lambda: __import__('p')\n"
    )

    def test_formes(self):
        trouves = {(c, p) for c, p, _ in imports_du_source(self.SOURCE)}
        attendus = {("a", False), ("b", False), ("c", False), ("d", False), ("e", False), ("f", False), ("json", False),
                    ("sympy", False), ("g", False), ("h", False), ("i", False), ("j", True), ("k", False), ("l", True),
                    ("importlib", True), ("m", True), ("n", False), ("o", True), ("p", True)}
        self.assertEqual(trouves, attendus)


if __name__ == "__main__":
    unittest.main()
