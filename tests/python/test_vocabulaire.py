"""C6 : aucun texte visible par l'élève ne cite une méthode interne (calcul formel, SymPy, dichotomie…) ni
ne qualifie une racine ou une puissance de « transcendante » (le mot est interdit partout).
Les équivalents sont interdits partout, dans toutes les sorties de tous les outils : ni le symbole ∼ (\\sim),
ni le mot « équivalent », ni « se comporte comme » (on met en évidence, avec des égalités exactes)."""
import json
import os
import re
import unittest

from moteurs import RACINE, ensemble_def as ed
import derivee_variations as dv
import etude_complete as ec
import factorisation as fa
import limites_asymptotes as la
from cas import CAS_LIMITES, entrees_page, entrees_factorisation
from aides_sortie import TUTOIEMENT, chaines_litterales

INTERDITS = re.compile(r"calcul formel|sympy|transcend|dichotom|exacte simple|valeurs? approchée|moteur python|erreur du moteur"
                       r"|erreur interne|formel|∼|~|\\sim|équivalent|se comporte comme", re.I)
DOSSIER_INSTANTANES = os.path.join(os.path.dirname(__file__), "instantanes")
EXEMPLES_RACINES = ["x^(1/3)", "x^(2/3)", "x^(4/3)", "x^(1/3)+x", "sqrt(x)+x", "ln(x)-x+3", "sqrt(ln(x)-x+2)", "x^3-x+1",
                    "ln(x)/(x^3-2x+5)", "x^(ln(2))", "x^(ln(4)-2ln(2))", "ln(x)+x^2-3", "e^x-x^2", "x*e^x-2", "(ln x)^2-x"]


def chaines(o):
    if isinstance(o, str):
        yield o
    elif isinstance(o, dict):
        for k, v in o.items():
            if k != "detail" and not k.endswith("_detail"):       # détail technique : console seulement
                yield from chaines(v)
    elif isinstance(o, (list, tuple)):
        for v in o:
            yield from chaines(v)


class TestVocabulaireEleve(unittest.TestCase):
    def verifie(self, o, ou):
        for t in chaines(o):
            m = INTERDITS.search(t)
            self.assertIsNone(m, f"{ou} : « {m.group(0) if m else ''} » dans : {t[:160]}")
            m = TUTOIEMENT.search(t)
            self.assertIsNone(m, f"{ou} : tutoiement « {m.group(0).strip() if m else ''} » dans : {t[:160]}")

    def test_instantanes(self):
        for nom in sorted(os.path.relpath(os.path.join(d, n), DOSSIER_INSTANTANES)
                          for d, _, noms in os.walk(DOSSIER_INSTANTANES) for n in noms if n.endswith(".json")):
            with open(os.path.join(DOSSIER_INSTANTANES, nom), encoding="utf-8") as f:
                data = json.load(f)
            for entree, sortie in data.items():
                with self.subTest(fichier=nom, entree=entree):
                    self.verifie(sortie, f"{nom} {entree}")

    def test_cas_limites_et_exemples_de_racines(self):
        outils = {"ensemble-definition": ed.analyser, "derivee-variations": dv.etudier,
                  "limites-asymptotes": la.etudier, "etude-complete": ec.etudier}
        for outil, fn in outils.items():
            for entree in dict.fromkeys(entrees_page(outil) + CAS_LIMITES[outil] + EXEMPLES_RACINES):
                with self.subTest(outil=outil, entree=entree):
                    self.verifie(fn(entree), f"{outil} {entree}")

    def test_factorisation(self):
        for entree in entrees_factorisation():
            with self.subTest(entree=entree):
                self.verifie(fa.factoriser_expr(entree), f"factorisation {entree}")

    def test_erreurs_generiques_et_detail_a_part(self):
        # une erreur de condition : message générique, détail technique dans un champ à part (console)
        from unittest import mock
        with mock.patch.object(ed, "resoudre_condition", side_effect=RuntimeError("boom interne")):
            res = ed.analyser("ln(x)")
        c = res["conditions"][0]
        self.assertEqual(c["etapes"][0]["html"], "Cette condition n'a pas pu être résolue automatiquement.")
        self.assertIn("boom interne", c["detail"])


class TestVouvoiement(unittest.TestCase):
    """L'enseignant vouvoie ses élèves : aucun texte destiné à l'élève (messages d'erreur, corrigés, pages, rappels de méthode) ne tutoie.
    Détecteur : aides_sortie.TUTOIEMENT (tu/ton/ta/tes/toi, impératifs « choisis », « ouvre », « mets »…, impératifs en début de phrase)."""

    DOSSIERS_MOTEURS = ["ensemble-definition", "derivee-variations", "limites-asymptotes", "etude-complete", "factorisation",
                        "exponentielles-logarithmes", "moteur"]
    PAS_UN_TEXTE_ELEVE = {"construire_roues.py"}          # script de construction des roues : aucun texte pour l'élève

    def fichiers_python(self):
        for dossier in self.DOSSIERS_MOTEURS:
            for nom in sorted(os.listdir(os.path.join(RACINE, dossier))):
                if nom.endswith(".py") and nom not in self.PAS_UN_TEXTE_ELEVE:
                    yield os.path.join(RACINE, dossier, nom)

    def test_litteraux_des_moteurs(self):
        """Tout littéral texte des moteurs (hors docstrings) : messages d'erreur, phrases du corrigé, y compris celles qu'aucune entrée de
        test ne fait apparaître."""
        vus = 0
        for chemin in self.fichiers_python():
            for ligne, texte in chaines_litterales(chemin):
                vus += 1
                with self.subTest(fichier=os.path.relpath(chemin, RACINE), ligne=ligne):
                    m = TUTOIEMENT.search(texte)
                    self.assertIsNone(m, f"« {m.group(0).strip() if m else ''} » dans : {texte[:160]}")
        self.assertGreater(vus, 1000)

    def test_pages_et_textes_communs(self):
        fichiers = ["index.html"] + [os.path.join(d, "index.html") for d in sorted(os.listdir(RACINE))
                                      if os.path.isfile(os.path.join(RACINE, d, "index.html"))]
        fichiers += [os.path.join("commun", n) for n in sorted(os.listdir(os.path.join(RACINE, "commun"))) if n.endswith(".js")]
        for f in fichiers:
            with self.subTest(fichier=f):
                texte = texte_visible(os.path.join(RACINE, f))
                attributs = " ".join(re.findall(r'(?:placeholder|aria-label|title|alt)="([^"]*)"', texte))
                texte = re.sub(r"<[^>]*>", " ", texte) + "\n" + attributs
                for ligne in texte.splitlines():
                    m = TUTOIEMENT.search(ligne)
                    self.assertIsNone(m, f"« {m.group(0).strip() if m else ''} » dans : {ligne.strip()[:200]}")

    def test_registre(self):
        with open(os.path.join(RACINE, "commun", "registre.json"), encoding="utf-8") as f:
            registre = json.load(f)
        for o in registre["outils"]:
            for champ in ("titre", "description"):
                self.assertIsNone(TUTOIEMENT.search(o[champ]), o[champ])


def texte_visible(chemin):
    with open(chemin, encoding="utf-8") as f:
        s = f.read()
    s = re.sub(r"<!--.*?-->", " ", s, flags=re.S)
    s = re.sub(r"/\*.*?\*/", " ", s, flags=re.S)
    s = re.sub(r"(?m)(^|\s)//[^\n]*", " ", s)
    return s


class TestVocabulairePages(unittest.TestCase):
    PAGES = ["ensemble-definition", "derivee-variations", "limites-asymptotes", "etude-complete", "factorisation", ""]

    def test_pages(self):
        motifs = re.compile(r"SymPy|calcul formel|transcend|dichotom|exacte simple|valeurs approchées|moteur Python|Erreur du moteur"
                            r"|via un serveur|python3 -m http|∼|\\sim|équivalent|se comporte comme", re.I if False else 0)
        for page in self.PAGES:
            chemin = os.path.join(RACINE, page, "index.html")
            with self.subTest(page=page or "accueil"):
                for ligne in texte_visible(chemin).splitlines():
                    self.assertIsNone(motifs.search(ligne), ligne.strip()[:200])


if __name__ == "__main__":
    unittest.main()
