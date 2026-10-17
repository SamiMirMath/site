"""T12 — limites-asymptotes/resoudre_la.py : sortie du format commun, sans rien perdre de l'ancienne,
et phrases des asymptotes que la page composait en JS (`ligneAsymptote`)."""
import json
import unittest

import moteurs  # noqa: F401  (chemins des moteurs)
import limites_asymptotes as la
import resoudre_la as rla
from aides_sortie import manquantes, valide, blocs_de_type
from cas import entrees_page, CAS_LIMITES

ENTREES = list(dict.fromkeys(entrees_page("limites-asymptotes") + CAS_LIMITES["limites-asymptotes"]))
TECHNIQUE = ("detail", "ok", "genre", "a", "b")


def bilan(entree):
    return blocs_de_type(rla.resoudre(entree), "liste")[0]["items"]


class TestResoudreLA(unittest.TestCase):
    def test_schema_et_rien_de_perdu(self):
        for entree in ENTREES:
            with self.subTest(entree=entree):
                s = rla.resoudre(entree)
                valide(self, s)
                self.assertEqual(manquantes(la.etudier(entree), s, TECHNIQUE), [])

    def test_ordre_et_nombre_de_cartes(self):
        for entree in ENTREES:
            ancien = la.etudier(entree)
            if not ancien["ok"]:
                continue
            with self.subTest(entree=entree):
                s = rla.resoudre(entree)
                n = 1 + (1 if ancien.get("tableaux_signe") else 0) + len(ancien["etudes"]) + 1
                self.assertEqual(len(s["cartes"]), n)
                self.assertEqual(s["cartes"][0]["titre"], "Fonction")
                self.assertEqual(s["cartes"][-1]["titre"], "Bilan des asymptotes")
                self.assertEqual([c["titre_tex"] for c in s["cartes"] if c["titre"] == "Limite"],
                                 [e["ou"] for e in ancien["etudes"]])

    def test_phrases_des_asymptotes(self):
        self.assertEqual(bilan("(x^2-1)/(x-3)"), [
            "Asymptote oblique (\\(x \\to -\\infty\\)) : \\(y = x + 3\\)",
            "Asymptote oblique (\\(x \\to +\\infty\\)) : \\(y = x + 3\\)",
            "Asymptote verticale : \\(x = 3\\) (\\(\\lim_{x\\to 3^-} f(x) = -\\infty\\) ; \\(\\lim_{x\\to 3^+} f(x) = +\\infty\\))",
        ])
        self.assertTrue(bilan("(2x^2+1)/(x^2-1)")[0].startswith("Asymptote horizontale (\\(x \\to -\\infty\\)) : \\(y = 2\\)"))
        self.assertEqual(bilan("(x^2-1)/(x-1)")[2],
                         "Trou en \\((1\\,;\\,2)\\) : f n'est pas définie en \\(x = 1\\), mais \\(f(x) \\to 2\\) (pas une asymptote verticale)")
        self.assertTrue(any(l.startswith("Pas de limite en \\(x = 0\\) (pas d'asymptote verticale) : ") for l in bilan("x/sqrt(x^2)")))
        self.assertEqual(bilan("(x^3+1)/(x-2)")[:2], [
            "Pas d'asymptote (\\(x \\to -\\infty\\)) — branche parabolique.",
            "Pas d'asymptote (\\(x \\to +\\infty\\)) — branche parabolique."])

    def test_aucune_asymptote(self):
        s = rla.resoudre("x^(1/2)")
        self.assertEqual(blocs_de_type(s, "liste"), [])
        self.assertEqual(s["cartes"][-1]["blocs"], [{"type": "texte", "html": "Aucune asymptote détectée.", "style": "discret"}])

    def test_toutes_les_asymptotes_ont_une_phrase(self):
        for entree in ENTREES:
            ancien = la.etudier(entree)
            if ancien["ok"] and ancien["asymptotes"]:
                with self.subTest(entree=entree):
                    self.assertEqual(len(bilan(entree)), len(ancien["asymptotes"]))

    def test_erreurs_en_francais(self):
        for entree in ("", "ln(", "x+*2"):
            with self.subTest(entree=entree):
                s = rla.resoudre(entree)
                valide(self, s)
                self.assertFalse(s["ok"])
                self.assertNotIn("Traceback", json.dumps(s))

    def test_json(self):
        self.assertEqual(json.loads(rla.resoudre_json("1/x")), rla.resoudre("1/x"))


if __name__ == "__main__":
    unittest.main()
