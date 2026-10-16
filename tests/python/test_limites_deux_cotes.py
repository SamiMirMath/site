"""Bug : en une valeur interdite isolée (limites à gauche ET à droite) d'une
fonction non rationnelle, l'outil annonçait toujours une asymptote verticale,
même quand les deux limites sont finies."""
import unittest

from moteurs import ensemble_def  # noqa: F401  (chemins + SymPy)
import limites_asymptotes as la


def asymptote_en(entree, point_tex):
    r = la.etudier(entree)
    assert r["ok"], r
    trouvees = [a for a in r["asymptotes"] if a.get("point_tex") == point_tex]
    assert len(trouvees) == 1, trouvees
    return trouvees[0]


class TestLimitesDeuxCotes(unittest.TestCase):
    def test_limites_finies_egales_trou(self):
        for entree, valeur in [("(e^x-1)/x", "1"), ("x*ln(x^2)", "0")]:
            with self.subTest(f=entree):
                a = asymptote_en(entree, "0")
                self.assertEqual(a["genre"], "trou")
                self.assertEqual(a["valeur_tex"], valeur)

    def test_limites_finies_differentes_sans_limite(self):
        a = asymptote_en("x/sqrt(x^2)", "0")
        self.assertEqual(a["genre"], "sans_limite")
        self.assertEqual((a["gauche_tex"], a["droite_tex"]), ("-1", "1"))

    def test_limite_infinie_asymptote_verticale(self):
        for entree, g, d in [("e^x/x", r"-\infty", r"+\infty"), ("e^(1/x)", "0", r"+\infty")]:
            with self.subTest(f=entree):
                a = asymptote_en(entree, "0")
                self.assertEqual(a["genre"], "verticale")
                self.assertEqual((a["gauche_tex"], a["droite_tex"]), (g, d))

    def test_jamais_de_verticale_sans_limite_infinie(self):
        for entree in ["(e^x-1)/x", "x*ln(x^2)", "x/sqrt(x^2)", "e^x/x", "e^(1/x)", "ln(x)/x",
                       "(x^2-1)/(x-1)", "1/(x^2-2)", "x^2/(x-1)"]:
            r = la.etudier(entree)
            for a in r["asymptotes"]:
                if a["genre"] == "verticale":
                    with self.subTest(f=entree, point=a["point_tex"]):
                        cotes = [a.get("gauche_tex"), a.get("droite_tex")]
                        self.assertTrue(any(c and r"\infty" in c for c in cotes), a)

    def test_narration_conclut(self):
        r = la.etudier("(e^x-1)/x")
        etude = next(e for e in r["etudes"] if e["ou"] == r"x \to 0")
        self.assertIn("pas d'asymptote verticale", etude["etapes"][-1]["html"])


ENTREES_LA08 = ["(e^x-1)/x", "x*ln(x^2)", "x/sqrt(x^2)", "(x^2-1)/(x-1)", "ln(x)/x", "x*ln(x)",
                "1/(x^2-2)", "(x^2-2)/(x^4-4)", "e^x/x", "(x^2-3)/(x^3-3x)"]


def textes_et_genres(entree):
    r = la.etudier(entree)
    assert r["ok"], r
    textes = [e["html"] for et in r["etudes"] for e in et["etapes"]]
    return r, textes, [a["genre"] for a in r["asymptotes"]]


class TestVocabulaireQ7(unittest.TestCase):
    def test_aucun_ancien_vocabulaire(self):  # LA-08
        for entree in ENTREES_LA08:
            with self.subTest(f=entree):
                _, textes, genres = textes_et_genres(entree)
                for t in textes:
                    self.assertNotIn("discontinuité", t)
                self.assertNotIn("saut", genres)
                self.assertNotIn("saut", " ".join(textes).lower().split())

    def test_formulation_trou(self):
        for entree in ["(e^x-1)/x", "(x^2-1)/(x-1)", "x*ln(x)"]:
            with self.subTest(f=entree):
                _, textes, genres = textes_et_genres(entree)
                self.assertIn("trou", genres)
                dernier = next(t for t in textes if t.startswith("Limite finie"))
                self.assertIn("pas d'asymptote verticale, trou dans le graphique en", dernier)

    def test_formulation_sans_limite(self):
        _, textes, genres = textes_et_genres("x/sqrt(x^2)")
        self.assertIn("sans_limite", genres)
        self.assertTrue(any("Limites à gauche et à droite différentes : f n'a pas de limite en" in t
                            and "pas d'asymptote verticale" in t for t in textes))


if __name__ == "__main__":
    unittest.main()
