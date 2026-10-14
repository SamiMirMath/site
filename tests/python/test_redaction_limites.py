"""T29 (Q9) — Limites rédigées étape par étape : opérations et composition de limites (L1).

Critères LA-10 (partiel : fonctions non rationnelles), LA-11 (garde-fou), LA-12 (limites
intermédiaires confirmées par l'oracle), LA-13 (forme indéterminée), LA-18 (conclusion).
"""
import unittest
from unittest import mock

import mpmath

from moteurs import ensemble_def as ed
import limites_asymptotes as la
import oracle
from test_proprietes_limites import CAS, GRANDS, petits

mp = mpmath.mp
REPLI = "Le calcul détaillé de cette limite n'est pas rédigé ici ; résultat : "


def etapes(entree, ou):
    r = la.etudier(entree)
    assert r["ok"], r
    return next(e["etapes"] for e in r["etudes"] if e["ou"] == ou)


def textes(entree, ou):
    return [e["html"] for e in etapes(entree, ou)]


class TestPhrasesExactes(unittest.TestCase):
    def test_exponentielle_en_moins_l_infini(self):
        self.assertEqual(textes("e^(2x)", r"x \to -\infty"), [
            r"Comme \(x \to -\infty\) et \(2 > 0\), on a \(2x \to -\infty\).",
            r"Or \(e^{t} \to 0^{+}\) quand \(t \to -\infty\) : \(e^{2x} \to 0^{+}\).",
            r"Donc \(\displaystyle\lim_{x\to -\infty} f(x) = 0\).",
            r"Asymptote horizontale d'équation \(y = 0\).",
        ])

    def test_exponentielle_en_plus_l_infini(self):
        self.assertEqual(textes("e^(2x)", r"x \to +\infty")[-2:], [
            r"Donc \(\displaystyle\lim_{x\to +\infty} f(x) = +\infty\).",
            "La limite est infinie : pas d'asymptote horizontale.",
        ])

    def test_logarithme_en_une_valeur_interdite(self):
        self.assertEqual(textes("ln(x-1)", r"x \to 1^+")[1:], [
            r"Pour \(x > 1\), \(x - 1 > 0\) : \(x - 1 \to 0^{+}\).",
            r"Or \(\ln t \to -\infty\) quand \(t \to 0^{+}\) : \(\ln\left(x - 1\right) \to -\infty\).",
            r"Donc \(\displaystyle\lim_{x\to 1^{+}} f(x) = -\infty\).",
            r"Asymptote verticale d'équation \(x = 1\).",
        ])

    def test_produit_sans_forme_indeterminee_ne_cite_pas_la_croissance_comparee(self):
        t = textes("x*e^x", r"x \to +\infty")
        self.assertIn(r"\(x \to +\infty\) et \(e^{x} \to +\infty\) : le produit tend vers \(+\infty\).", t)
        for phrase in t:
            self.assertNotIn("croissance comparée", phrase)
            self.assertNotIn("indéterminée", phrase)

    def test_inverse_d_un_zero_de_signe_connu(self):
        self.assertEqual(textes("e^(1/x)", r"x \to 0")[1:6], [
            r"Limite à gauche (\(x \to 0^{-}\)) :",
            r"\(1\) est une constante et \(x \to 0^{-}\) : \(\dfrac{1}{0^{-}} = -\infty\).",
            r"Or \(e^{t} \to 0^{+}\) quand \(t \to -\infty\) : \(e^{\frac{1}{x}} \to 0^{+}\).",
            r"Donc \(\displaystyle\lim_{x\to 0^{-}} f(x) = 0\).",
            r"Limite à droite (\(x \to 0^{+}\)) :",
        ])

    def test_quotient_dont_le_denominateur_tend_vers_zero(self):
        t = textes("ln(x^2-4x)/(x-5)", r"x \to 5")
        self.assertIn(r"\(\ln\left(x^{2} - 4x\right) \to \ln{\left(5 \right)}\) et \(x - 5 \to 0^{-}\) : "
                      r"\(\dfrac{\ln{\left(5 \right)}}{0^{-}} = -\infty\).", t)
        self.assertIn(r"Au moins une des deux limites est infinie : asymptote verticale d'équation \(x = 5\).", t)

    def test_une_sous_expression_n_est_commentee_qu_une_fois(self):
        t = textes("(e^x+1)/(e^x-1)", r"x \to -\infty")
        self.assertEqual(sum(1 for p in t if p.startswith(r"Or \(e^{t}")), 1)


class TestValeursInterdites(unittest.TestCase):
    """L2 : valeur interdite sans forme indéterminée — limite du numérateur, signe du dénominateur de chaque
    côté, ℓ/0^±, asymptote verticale (LA-14, LA-18)."""

    def test_fraction_rationnelle(self):
        self.assertEqual(textes("(x^2-1)/(x-3)", r"x \to 3"), [
            r"\(x=3\) est une valeur interdite : on étudie la limite de \(f\) quand \(x \to 3\).",
            r"Limite à gauche (\(x \to 3^{-}\)) :",
            r"Par substitution, \(x^{2} - 1 \to 3^{2} - 1 = 8\).",
            r"Pour \(x < 3\), \(x - 3 < 0\) : \(x - 3 \to 0^{-}\).",
            r"\(x^{2} - 1 \to 8\) et \(x - 3 \to 0^{-}\) : \(\dfrac{8}{0^{-}} = -\infty\).",
            r"Donc \(\displaystyle\lim_{x\to 3^{-}} f(x) = -\infty\).",
            r"Limite à droite (\(x \to 3^{+}\)) :",
            r"Par substitution, \(x^{2} - 1 \to 3^{2} - 1 = 8\).",
            r"Pour \(x > 3\), \(x - 3 > 0\) : \(x - 3 \to 0^{+}\).",
            r"\(x^{2} - 1 \to 8\) et \(x - 3 \to 0^{+}\) : \(\dfrac{8}{0^{+}} = +\infty\).",
            r"Donc \(\displaystyle\lim_{x\to 3^{+}} f(x) = +\infty\).",
            r"Asymptote verticale d'équation \(x = 3\).",
        ])

    def test_denominateur_oppose(self):
        t = textes("5/(3-x)", r"x \to 3")
        self.assertIn(r"Pour \(x < 3\), \(3 - x = -\left(x - 3\right)\), \(3 - x > 0\) : \(3 - x \to 0^{+}\).", t)
        self.assertIn(r"\(5\) est une constante et \(3 - x \to 0^{+}\) : \(\dfrac{5}{0^{+}} = +\infty\).", t)

    def test_carre_et_signe_du_quotient(self):
        t = textes("1/(x-1)^2", r"x \to 1")
        self.assertEqual(t.count(r"Quand \(x \to 1^{-}\), \(\left(x - 1\right)^{2} \to 0^{+}\) (carré)."), 1)
        self.assertEqual(t.count(r"\(1\) est une constante et \(\left(x - 1\right)^{2} \to 0^{+}\) : "
                                 r"\(\dfrac{1}{0^{+}} = +\infty\)."), 2)

    def test_denominateur_factorise_pour_connaitre_son_signe(self):
        t = textes("(x^2-3)/(x^3-3x)", r"x \to 0")
        self.assertIn(r"\(x^{3} - 3x = x\,\left(x^{2} - 3\right)\) ; quand \(x \to 0^{-}\), "
                      r"\(x^{2} - 3 \to -3\) et \(x \to 0^{-}\) : \(x^{3} - 3x \to 0^{+}\).", t)
        self.assertIn(r"\(x^{2} - 3 \to -3\) et \(x^{3} - 3x \to 0^{+}\) : \(\dfrac{-3}{0^{+}} = -\infty\).", t)

    def test_pole_irrationnel(self):
        t = textes("1/(x^2-2)", r"x \to \sqrt{2}")
        self.assertIn(r"Limite à gauche (\(x \to {\sqrt{2}}^{-}\)) :", t)
        self.assertIn(r"\(1\) est une constante et \(x^{2} - 2 \to 0^{-}\) : \(\dfrac{1}{0^{-}} = -\infty\).", t)
        self.assertEqual(t[-1], r"Asymptote verticale d'équation \(x = \sqrt{2}\).")

    def test_zero_de_signe_connu_en_un_point_irrationnel(self):
        t = textes("ln(x^2-3)", r"x \to \sqrt{3}^+")
        self.assertIn(r"\(x^{2} \to 3\) et \(3\) est une constante : la différence tend vers \(0^{+}\).", t)

    def test_zero_de_signe_inconnu_donne_le_repli(self):
        """Pas de factorisation possible au point irrationnel d'un polynôme de degré 3 : le signe n'est pas inventé."""
        etape = etapes("ln(x^3-3x)", r"x \to \sqrt{3}^+")[1]
        self.assertEqual(etape["html"], REPLI + r"\(\displaystyle\lim_{x\to {\sqrt{3}}^{+}} f(x) = -\infty\).")
        self.assertIn("signe inconnu", etape["detail"])

    def test_factorisation_dans_un_logarithme(self):
        t = textes("ln(x^2-4x)/(x-5)", r"x \to 4^+")
        self.assertIn(r"\(x^{2} - 4x = x\,\left(x - 4\right)\) ; quand \(x \to 4^{+}\), \(x \to 4\) et "
                      r"\(x - 4 \to 0^{+}\) : \(x^{2} - 4x \to 0^{+}\).", t)
        self.assertEqual(t[-1], r"Asymptote verticale d'équation \(x = 4\).")

    def test_chaque_pole_sans_facteur_commun_est_redige(self):
        for entree in ["1/(x-2)", "(2x+1)/(x-1)", "x^2/(x-1)", "1/x^2", "(x^3+1)/(x-2)", "(2x^2+1)/(x^2-1)", "1/(x^2-2)"]:
            r = la.etudier(entree)
            for etude in r["etudes"]:
                if "infty" in etude["ou"]:
                    continue
                with self.subTest(f=entree, ou=etude["ou"]):
                    t = [e["html"] for e in etude["etapes"]]
                    self.assertFalse(any(p.startswith(REPLI) for p in t), t)
                    self.assertEqual(sum(1 for p in t if p.startswith("Donc ")), 2)
                    self.assertTrue(t[-1].startswith("Asymptote verticale d'équation"), t[-1])

    def test_garde_fou_sur_un_pole_rationnel(self):
        with mock.patch.object(la, "_noeud", side_effect=la.Abandon("essai")):
            avec = la.etudier("1/(x-2)")
        normal = la.etudier("1/(x-2)")
        self.assertEqual(avec["asymptotes"], normal["asymptotes"])
        t = [e["html"] for e in next(e for e in avec["etudes"] if e["ou"] == r"x \to 2")["etapes"]]
        self.assertEqual(sum(1 for p in t if p.startswith(REPLI)), 2)


class TestFormeIndeterminee(unittest.TestCase):
    """Sans méthode pour la lever (L1), la rédaction est abandonnée : phrase de repli, jamais d'étape fausse."""

    def test_repli_mot_pour_mot_et_detail_en_console(self):
        etape = etapes("x*e^x", r"x \to -\infty")[0]
        self.assertEqual(etape["html"], REPLI + r"\(\displaystyle\lim_{x\to -\infty} f(x) = 0\).")
        self.assertIn("0 · ∞", etape["detail"])

    def test_repli_garde_la_conclusion(self):
        t = textes("x*e^x", r"x \to -\infty")
        self.assertEqual(len(t), 2)
        self.assertEqual(t[1], r"Asymptote horizontale d'équation \(y = 0\).")

    def test_aucune_forme_annoncee_quand_il_n_y_en_a_pas(self):
        for entree, ou in [("e^(2x)", r"x \to +\infty"), ("sqrt(x)", r"x \to +\infty"),
                           ("ln(x-1)", r"x \to 1^+"), ("x*e^x", r"x \to +\infty")]:
            with self.subTest(f=entree):
                self.assertFalse(any("indéterminée" in p or "detail" in e
                                     for e, p in zip(etapes(entree, ou), textes(entree, ou))))


class TestGardeFou(unittest.TestCase):
    def test_sous_expression_fausse_donne_le_repli(self):
        with mock.patch.object(la, "_exp_lim", return_value=la.Lim.infini(1)):
            t = etapes("e^(2x)", r"x \to -\infty")
        self.assertEqual(t[0]["html"], REPLI + r"\(\displaystyle\lim_{x\to -\infty} f(x) = 0\).")
        self.assertIn("≠", t[0]["detail"])
        self.assertFalse(any(r"Or \(e^{t}" in e["html"] or "Comme" in e["html"] for e in t))

    def test_valeur_finale_fausse_donne_le_repli(self):
        with mock.patch.object(la, "_noeud", return_value=la.Lim.infini(1)):
            t = etapes("ln(x)", r"x \to 0^+")
        self.assertEqual(t[1]["html"], REPLI + r"\(\displaystyle\lim_{x\to 0^{+}} f(x) = -\infty\).")
        self.assertIn("valeur rédigée", t[1]["detail"])

    def test_exception_inattendue_donne_le_repli(self):
        with mock.patch.object(la, "_produit", side_effect=RuntimeError("boum")):
            t = etapes("x*e^x", r"x \to +\infty")
        self.assertEqual(t[0]["html"], REPLI + r"\(\displaystyle\lim_{x\to +\infty} f(x) = +\infty\).")
        self.assertIn("RuntimeError", t[0]["detail"])

    def test_la_valeur_de_reference_ne_change_pas(self):
        for entree in ["e^(2x)", "ln(x-1)", "x*e^x", "e^(1/x)"]:
            with mock.patch.object(la, "_noeud", side_effect=la.Abandon("essai")):
                sans = la.etudier(entree)["asymptotes"]
            self.assertEqual(la.etudier(entree)["asymptotes"], sans, entree)


class TestToutEstEcritOuReplie(unittest.TestCase):
    """LA-10 (fonctions non rationnelles) : jamais « lim f(x) = v » seul."""

    ENTREES = ["e^(2x)", "ln(x)", "ln(x-1)", "x*e^x", "x^2*e^(-x)", "sqrt(x)", "e^(1/x)", "x*ln(x)", "ln(x)/x",
               "ln(x^2-4x)/(x-5)", "(e^x+1)/(e^x-1)", "(e^x-1)/x", "x/sqrt(x^2)", "sqrt(x^2-4x+5)", "x^(1/3)",
               "x-ln(x)", "e^x-x^2", "x+ln(x)", "sqrt(x^2+1)", "1/ln(x)"]

    def test_chaque_borne_est_redigee_ou_replie(self):
        for entree in self.ENTREES:
            r = la.etudier(entree)
            for etude in r["etudes"]:
                with self.subTest(f=entree, ou=etude["ou"]):
                    t = [e["html"] for e in etude["etapes"]]
                    lims = [i for i, p in enumerate(t) if r"\lim_{x\to" in p]
                    self.assertTrue(lims, t)
                    for i in lims:
                        if t[i].startswith(REPLI):
                            continue
                        self.assertTrue(t[i].startswith("Donc "), t[i])
                        self.assertGreaterEqual(i, 1)
                        self.assertNotIn(r"\lim_{x\to", t[i - 1])


class TestLimitesIntermediairesConfirmeesParOracle(unittest.TestCase):
    """LA-12 : chaque limite écrite pour une sous-expression est confirmée par l'oracle haute précision."""

    def sonde(self, arbre, pt):
        if pt.s:
            return [pt.s * X for X in GRANDS]
        p = mp.mpf(str(pt.a.evalf(30)))
        return [p + pt.d * h for h in petits(float(p))]

    def verifier_une(self, arbre, L, pt, msg):
        vals = [v for v in (oracle.valeur(arbre, x) for x in self.sonde(arbre, pt)) if v is not None]
        self.assertGreaterEqual(len(vals), 2, msg + " : pas assez de points évaluables")
        if L.inf:
            self.assertTrue(all(L.inf * v > 0 for v in vals[1:]), msg + f" : {vals}")
            self.assertGreater(abs(vals[-1]), abs(vals[0]), msg + f" : {vals}")
            self.assertGreater(abs(vals[-1]), 10, msg + f" : {vals}")
        else:
            cible = mp.mpf(str(L.val.evalf(40)))
            self.assertLessEqual(abs(vals[-1] - cible), mp.mpf("0.02") * (1 + abs(cible)), msg + f" : {vals}")
            if L.nul() and L.ap:
                self.assertTrue(all(L.ap * v > 0 for v in vals), msg + f" : signe d'approche {vals}")

    def test_corpus(self):
        original = la._Contexte.verifier
        ecrites = []

        def espion(self, n, L):
            original(self, n, L)
            ecrites.append((n, L, self.pt))

        with mock.patch.object(la._Contexte, "verifier", autospec=True, side_effect=espion):
            for f in CAS:
                la.etudier(f)
        self.assertGreater(len(ecrites), 100)
        vus = set()
        for n, L, pt in ecrites:
            cle = (n.key(), pt.tex())
            if cle in vus:
                continue
            vus.add(cle)
            with self.subTest(sous_expression=ed.tex(n), limite=L.tex(), point=pt.tex()):
                self.verifier_une(n, L, pt, f"{ed.tex(n)} en {pt.tex()}")


if __name__ == "__main__":
    unittest.main()
