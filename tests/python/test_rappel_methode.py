"""L9 : l'encadré « Rappel de la méthode » de la page Limites reprend le mode d'emploi en 7 points du corrigé du chapitre 8 (étape 1 du chantier
3M, 29.10.2026), au vouvoiement, suivi de la phrase sur le podium ; un second encadré rappelle les asymptotes (division euclidienne, a puis b,
position relative). Aucun équivalent, aucune croissance comparée."""
import os
import re
import unittest

from moteurs import RACINE
import limites_asymptotes as la

PHRASE_PODIUM = "La règle du podium vous sert à prédire le résultat ; la justification se fait avec la règle de BH."


def page():
    with open(os.path.join(RACINE, "limites-asymptotes", "index.html"), encoding="utf-8") as f:
        return f.read()


def encadre_brut():
    m = re.search(r'<details class="card rappel"[^>]*>(.*?)</details>', page(), re.S)
    assert m, "encadré « Rappel de la méthode » introuvable"
    return m.group(1)


def encadre():
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", encadre_brut()))


def asymptotes():
    m = re.search(r'<details class="card asymptotes"[^>]*>(.*?)</details>', page(), re.S)
    assert m, "encadré « Rappel : les asymptotes » introuvable"
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", m.group(1)))


class TestRappelDeLaMethode(unittest.TestCase):
    def test_titre_et_sept_points(self):
        self.assertIn("Rappel de la méthode", encadre())
        brut = encadre_brut()
        m = re.search(r'<ol class="mode">(.*?)</ol>', brut, re.S)
        self.assertTrue(m, "liste numérotée du mode d'emploi introuvable")
        points = re.findall(r"<li>(.*?)</li>", m.group(1), re.S)
        self.assertEqual(len(points), 7, points)
        mots = ["remplacez", "forme", "podium", "quotient", "BH", "recommencez", "prédiction"]
        for point, mot in zip(points, mots):
            self.assertIn(mot.lower(), re.sub(r"<[^>]+>", " ", point).lower(), (mot, point))

    def test_phrase_sur_le_podium_apres_les_sept_points(self):
        t = encadre()
        self.assertIn(PHRASE_PODIUM, t)
        self.assertGreater(t.index(PHRASE_PODIUM), t.index("prédiction"))

    def test_pieges_de_bh_et_vouvoiement(self):
        t = encadre()
        for mot in ["dérivée d'un quotient", "0\\cdot\\infty", "forme déterminée", "avant chaque"]:
            self.assertIn(mot.lower().replace(" ", ""), t.lower().replace(" ", ""), mot)
        self.assertIn("vous", t.lower())
        for tutoiement in [" tu ", " ton ", " ta ", " tes ", " toi "]:
            self.assertNotIn(tutoiement, t.lower())

    def test_moteur_sans_croissance_comparee(self):
        noms = [m.__name__ for m in la.METHODES]
        self.assertLess(noms.index("_conjuguee"), noms.index("_lhopital"))
        self.assertNotIn("_comparee_pure", noms)
        self.assertNotIn("_evidence_ln", noms)
        self.assertNotIn("croissance comparée", encadre().lower())

    def test_asymptotes_dans_leur_encadre(self):
        t = asymptotes()
        for mot in ["division euclidienne", "position relative", "asymptote", "trou"]:
            self.assertIn(mot.lower(), t.lower(), mot)
        self.assertRegex(t, r"a=\\lim\\frac\{f\(x\)\}\{x\}")

    def test_aucun_equivalent(self):
        for t in (encadre(), asymptotes()):
            for mot in ["équivalent", "∼", "\\sim", "se comporte comme", "terme dominant"]:
                self.assertNotIn(mot, t)


class TestFormulesBienFormees(unittest.TestCase):
    """Chaque formule (en ligne ou affichée) des sorties Limites est syntaxiquement équilibrée pour KaTeX :
    accolades, \\left/\\right, \\begin/\\end."""

    @staticmethod
    def equilibree(f):
        prof = 0
        for i, c in enumerate(f):
            if c == "\\" and i + 1 < len(f) and f[i + 1] in "{}":
                continue
            if c == "{" and not (i and f[i - 1] == "\\"):
                prof += 1
            elif c == "}" and not (i and f[i - 1] == "\\"):
                prof -= 1
                if prof < 0:
                    return False
        return prof == 0 and f.count("\\left") == f.count("\\right") and f.count("\\begin{aligned}") == f.count("\\end{aligned}")

    def test_toutes_les_formules(self):
        from cas import CAS_LIMITES, entrees_page
        entrees = dict.fromkeys(entrees_page("limites-asymptotes") + CAS_LIMITES["limites-asymptotes"] +
                                ["sqrt(4x^2+1)/(x+2)", "sqrt(x^2+x)-x", "ln(x^2+1)/x", "x/sqrt(x^2)", "(x^3+1)/(x^2+1)",
                                 "sqrt(x^2-4x+5)", "(x^2-1)/(x-3)", "ln(x^2-4x)/(x-5)", "e^x-x^2", "(e^x-1)/x"])
        for entree in entrees:
            for etude in la.etudier(entree)["etudes"]:
                for e in etude["etapes"]:
                    h = e.get("html", "")
                    for f in re.findall(r"\\\((.*?)\\\)", h, re.S) + re.findall(r"\\\[(.*?)\\\]", h, re.S):
                        with self.subTest(f=entree, ou=etude["ou"]):
                            self.assertTrue(self.equilibree(f), f[:200])


if __name__ == "__main__":
    unittest.main()
