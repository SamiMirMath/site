"""L9 : l'encadré « Rappel de la méthode » de la page Limites suit l'ordre des méthodes du cours (Q9, LA-15), cite la
chaîne d'égalités, les asymptotes (division euclidienne, a puis b, position relative) et n'emploie aucun équivalent."""
import os
import re
import unittest

from moteurs import RACINE
import limites_asymptotes as la


def encadre():
    with open(os.path.join(RACINE, "limites-asymptotes", "index.html"), encoding="utf-8") as f:
        s = f.read()
    m = re.search(r'<details class="card rappel"[^>]*>(.*?)</details>', s, re.S)
    assert m, "encadré « Rappel de la méthode » introuvable"
    return re.sub(r"<[^>]+>", " ", m.group(1))


class TestRappelDeLaMethode(unittest.TestCase):
    def test_titre_et_ordre_des_methodes(self):
        t = encadre()
        self.assertIn("Rappel de la méthode", t)
        ordre = ["Opérations sur les limites", "Mise en évidence", "Expression conjuguée", "Croissance comparée", "Bernoulli-L'Hôpital"]
        places = [t.index(mot) for mot in ordre]
        self.assertEqual(places, sorted(places), ordre)
        # même ordre que dans le moteur : mise en évidence, conjuguée, croissance comparée, L'Hôpital
        noms = [m.__name__ for m in la.METHODES]
        self.assertLess(noms.index("_conjuguee"), noms.index("_comparee_pure"))
        self.assertLess(noms.index("_comparee_pure"), noms.index("_lhopital"))

    def test_chaine_d_egalites_et_asymptotes(self):
        t = encadre()
        for mot in ["chaîne d'égalités", "division euclidienne", "position relative", "asymptote", "trou", "|x|"]:
            self.assertIn(mot.lower(), t.lower(), mot)
        self.assertRegex(t, r"a=\\lim\\frac\{f\(x\)\}\{x\}")

    def test_aucun_equivalent(self):
        t = encadre()
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
