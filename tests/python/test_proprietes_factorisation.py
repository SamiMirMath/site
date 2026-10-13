"""T02 — Factorisation : le LaTeX AFFICHÉ (résultat et égalités des étapes) est relu,
reconverti en expression SymPy et comparé à l'entrée ; chaque facteur doit être
irréductible (critères FA-01, FA-02 de docs/specifications/factorisation.md)."""
import random
import re
import unittest

import sympy as sp

from moteurs import ensemble_def  # noqa: F401  (chemins + SymPy)
import factorisation as fa
from cas import FACTORISATION, entrees_page

LETTRES = {c: sp.Symbol(c) for c in "abcdefghijklmnopqrstuvwxyz"}
N_GENERES = 500
# Étapes qui contiennent une chaîne d'égalités vérifiable (les autres sont du texte).
MOTS = ("en évidence", "On reconnaît", "Méthode Somme-Produit", "on complète", "en divisant",
        "On groupe", "On revient", "D'où", "factorisation complète", "sans fraction", "on factorise")
NON_POLYNOMES = {"sqrt(x)", "x/y", "x^2-1'000"}   # refusés avec un message (FA-06)


def tex_vers_expr(t):
    """LaTeX produit par le moteur -> expression SymPy (indépendant du moteur)."""
    s = t.replace(r"\left[", "(").replace(r"\right]", ")").replace(r"\left(", "(").replace(r"\right)", ")")
    s = s.replace(r"\cdot", "*").replace(r"\times", "*").replace("{,}", ".")
    while r"\frac{" in s:
        i = s.index(r"\frac{")
        j = k = i + 6
        prof = 1
        while prof:
            prof += {"{": 1, "}": -1}.get(s[k], 0)
            k += 1
        num = s[j:k - 1]
        m, prof = k + 1, 1
        while prof:
            prof += {"{": 1, "}": -1}.get(s[m], 0)
            m += 1
        s = s[:i] + "((" + num + ")/(" + s[k + 1:m - 1] + "))" + s[m:]
    s = re.sub(r"\\sqrt\{(\d+)\}", r"Q(\1)", s)
    s = re.sub(r"\^\{(\d+)\}", r"**(\1)", s).replace(" ", "")
    out = ""
    for i, c in enumerate(s):
        if i and (c.isalpha() or c == "(") and (s[i - 1].isalnum() or s[i - 1] == ")"):
            if not (c == "(" and s[i - 1] == "Q"):
                out += "*"
        if i and c.isdigit() and s[i - 1] == ")":
            out += "*"
        out += c
    return sp.sympify(out, locals=dict(LETTRES, Q=sp.sqrt))


def polynome_entree(entree):
    return sp.expand(fa.vers_sympy(fa.Ctx(sp, []), LETTRES, fa.analyser(entree)))


def exercices_generes():
    niveaux = ["facile", "moyen", "difficile", "tresDifficile"]
    out = []
    for k in range(N_GENERES):
        random.seed(k)
        out.append(fa.genere_exercice(niveaux[k % 4]))
    return out


def battery():
    vues, out = set(), []
    for e in entrees_page("factorisation") + [e for l in FACTORISATION.values() for e in l] + exercices_generes():
        if e not in vues and e not in NON_POLYNOMES:
            vues.add(e)
            out.append(e)
    return out


class TestProprietesFactorisation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.resultats = {e: fa.factoriser_expr(e) for e in battery()}

    def test_resultat_affiche_egal_entree(self):
        """FA-01 : le résultat affiché, redéveloppé, redonne l'entrée ; aucun repli de secours."""
        for e, r in self.resultats.items():
            with self.subTest(entree=e):
                self.assertTrue(r["ok"], r.get("erreur"))
                self.assertFalse(r["secours"], "une méthode a produit un résultat faux (repli SymPy)")
                self.assertEqual(sp.expand(tex_vers_expr(r["resultat_tex"]) - polynome_entree(e)), 0,
                                 r["resultat_tex"])

    def test_egalites_des_etapes(self):
        """FA-01 : chaque chaîne d'égalités affichée dans les étapes est juste."""
        for e, r in self.resultats.items():
            for et in r["etapes"]:
                h = et["html"]
                if not any(m in h for m in MOTS) or "On pose" in h:
                    continue
                morceaux = re.findall(r"\\\((.*?)\\\)", h)
                if not morceaux:
                    continue
                with self.subTest(entree=e, etape=morceaux[-1]):
                    vals = [sp.expand(tex_vers_expr(c)) for c in morceaux[-1].split("=")]
                    for a, b in zip(vals, vals[1:]):
                        self.assertEqual(sp.expand(a - b), 0)

    def test_facteurs_irreductibles(self):
        """FA-02 : chaque facteur à coefficients rationnels est irréductible sur ℚ ; un facteur
        contenant une racine carrée est de degré 1 (trinôme seul à Δ > 0 non carré)."""
        for e, r in self.resultats.items():
            produit = tex_vers_expr(r["resultat_tex"])
            for facteur in sp.Mul.make_args(produit):
                base = facteur.as_base_exp()[0]
                if base.is_number:
                    continue
                with self.subTest(entree=e, facteur=str(base)):
                    if any(a.is_Pow and a.exp == sp.S.Half for a in sp.preorder_traversal(base)):
                        self.assertEqual(sp.Poly(base, *sorted(base.free_symbols, key=str)).total_degree(), 1)
                    else:
                        _, morceaux = sp.factor_list(base)
                        self.assertEqual([m for _, m in morceaux], [1], f"{base} se factorise encore")

    def test_non_polynomes_refuses(self):
        """FA-06 : message en français, pas d'exception."""
        for e in sorted(NON_POLYNOMES):
            with self.subTest(entree=e):
                r = fa.factoriser_expr(e)
                self.assertFalse(r["ok"])
                self.assertNotIn("Erreur interne", r["erreur"])


if __name__ == "__main__":
    unittest.main()
