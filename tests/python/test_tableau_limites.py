"""T06c : limites contre les doubles barres et en ±∞ sur la ligne f(x) du tableau de variations de
l'Étude complète (EC-08 à EC-12). Les valeurs viennent du calcul de la partie Limites (une seule source)."""
import unittest

from cas import CAS_LIMITES, entrees_page
import derivee_variations as dv
import etude_complete as ec
import limites_asymptotes as la

INF_M, INF_P = r"-\infty", r"+\infty"


def colonnes(entree):
    r = ec.etudier(entree)
    assert r["ok"], r
    return r, {c["j"]: (c["gauche"], c["droite"]) for c in r["variations_limites"]["colonnes"]}


def ligne_fprime(r):
    return next(l["cells"] for l in r["derivee"]["table_signe"]["rows"] if l["label"] == "f'(x)")


class TestExemples(unittest.TestCase):
    def test_pole_simple(self):  # EC-08, A
        r, col = colonnes("1/(x-2)")
        v = r["variations_limites"]
        self.assertEqual(col, {1: (INF_M, INF_P)})
        self.assertEqual((v["moins_inf"], v["plus_inf"]), ("0", "0"))
        self.assertEqual(ligne_fprime(r), ["-", "||", "-"])

    def test_pole_meme_signe(self):  # EC-08, B
        r, col = colonnes("1/(x-2)^2")
        v = r["variations_limites"]
        self.assertEqual(col, {1: (INF_P, INF_P)})
        self.assertEqual((v["moins_inf"], v["plus_inf"]), ("0", "0"))
        self.assertEqual(ligne_fprime(r), ["+", "||", "-"])

    def test_trou(self):  # EC-08 et EC-11, C : f' = 1 n'a aucune ligne de facteur
        r, col = colonnes("(x^2-1)/(x-1)")
        v = r["variations_limites"]
        self.assertEqual(col, {1: ("2", "2")})
        self.assertEqual((v["moins_inf"], v["plus_inf"]), (INF_M, INF_P))
        self.assertEqual(ligne_fprime(r), ["+", "||", "+"])
        self.assertEqual(dv.etudier("(x^2-1)/(x-1)")["table_signe"]["rows"][-2]["cells"], ["+", "||", "+"])

    def test_zone_hachuree(self):  # EC-09
        r, col = colonnes("ln(x^2-4)")
        v = r["variations_limites"]
        self.assertEqual(col, {1: (INF_M, None), 3: (None, INF_M)})
        self.assertEqual((v["moins_inf"], v["plus_inf"]), (INF_P, INF_P))

    def test_bornes(self):  # EC-09
        r, col = colonnes("ln(x)")
        v = r["variations_limites"]
        self.assertEqual(col, {1: (None, INF_M)})
        self.assertEqual((v["moins_inf"], v["plus_inf"]), (None, INF_P))
        r, col = colonnes("sqrt(x)")          # borne fermée : f(0) = 0 (T06), pas de limite
        self.assertEqual(col, {})
        self.assertEqual(r["variations_limites"]["moins_inf"], None)

    def test_valeur_interdite_toutes_lignes(self):  # EC-11
        for entree in ["1/(x-2)", "(x^2-1)/(x-1)", "ln(x^2-4)", "ln(x)", "1/x"]:
            with self.subTest(f=entree):
                t = dv.etudier(entree)["table_signe"]
                for j in range(1, len(t["rows"][0]["cells"]), 2):
                    for l in t["rows"]:
                        if l.get("variation"):
                            continue
                        self.assertIn(l["cells"][j], ("||", "x"), (l["label"], l["cells"]))


class TestIndeterminee(unittest.TestCase):
    def test_phrase_et_marqueur(self):  # « ? » à la place de la valeur, phrase sous le tableau
        t = {"crit": ["2"], "rows": [{"label": "f(x)", "cells": ["a", "asym", "b"], "variation": True}]}
        v = ec.limites_du_tableau(t, [{"type": "fini", "point_tex": "2", "point_val": 2.0,
                                       "gauche": "?", "droite": INF_P},
                                      {"type": "inf", "signe": 1, "tex": "?"}])
        self.assertEqual(v["colonnes"], [{"j": 1, "gauche": "?", "droite": INF_P}])
        self.assertEqual(v["plus_inf"], "?")
        self.assertEqual(v["non_determinees"], ["2^{-}", INF_P])


class TestMemeSourceQueLimites(unittest.TestCase):
    def test_sortie_de_l_outil_limites_inchangee(self):  # EC-12 (partie Limites)
        self.assertNotIn("limites_bornes", la.etudier("1/(x-2)"))
        self.assertNotIn("limites_bornes", ec.etudier("1/(x-2)")["limites"])

    def test_corpus_egal_a_la_partie_limites(self):  # EC-10
        corpus = set(CAS_LIMITES["etude-complete"] + CAS_LIMITES["limites-asymptotes"] + CAS_LIMITES["derivee-variations"])
        for page in ("etude-complete", "limites-asymptotes", "derivee-variations"):
            corpus |= set(entrees_page(page))
        verifiees = 0
        for entree in sorted(corpus):
            r = ec.etudier(entree)
            if not r.get("ok") or "variations_limites" not in r:
                continue
            v = r["variations_limites"]
            crit = r["derivee"]["table_signe"]["crit"]
            col = {c["j"]: c for c in v["colonnes"]}
            for a in r["limites"]["asymptotes"]:
                with self.subTest(f=entree, asymptote=a.get("ou")):
                    if "point_tex" in a:
                        c = col[2 * crit.index(a["point_tex"]) + 1]
                        for cote in ("gauche", "droite"):
                            attendu = a.get(cote + "_tex", a.get("valeur_tex"))
                            if attendu is not None and c[cote] is not None:
                                attendu = "?" if "non déterminée" in attendu else attendu
                                self.assertEqual(c[cote], attendu)
                                verifiees += 1
                    elif "valeur_tex" in a:
                        self.assertEqual(v["moins_inf" if "-" in a["ou"] else "plus_inf"], a["valeur_tex"])
                        verifiees += 1
        self.assertGreater(verifiees, 40)


if __name__ == "__main__":
    unittest.main()
