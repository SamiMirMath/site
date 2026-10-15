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
            r"Quand \(x \to -\infty\), \(2x \to -\infty\).",
            r"Or \(e^{t} \to 0^{+}\) quand \(t \to -\infty\), donc \(\displaystyle\lim_{x\to -\infty} f(x) = 0\).",
            r"Asymptote horizontale d'équation \(y = 0\).",
        ])

    def test_exponentielle_en_plus_l_infini(self):
        self.assertEqual(textes("e^(2x)", r"x \to +\infty")[-2:], [
            r"Or \(e^{t} \to +\infty\) quand \(t \to +\infty\), donc \(\displaystyle\lim_{x\to +\infty} f(x) = +\infty\).",
            "La limite est infinie : pas d'asymptote horizontale.",
        ])

    def test_logarithme_en_une_valeur_interdite(self):
        self.assertEqual(textes("ln(x-1)", r"x \to 1^+"), [
            r"\(x = 1\) est une valeur interdite : on étudie la limite de \(f\) quand \(x \to 1^{+}\).",
            r"À droite de \(1\), l'argument \(x - 1\) est positif (cf. tableau de signes de \(x - 1\)) : il tend vers \(0^{+}\).",
            r"Or \(\ln t \to -\infty\) quand \(t \to 0^{+}\), donc \(\displaystyle\lim_{x\to 1^{+}} f(x) = -\infty\).",
            r"Asymptote verticale d'équation \(x = 1\).",
        ])

    def test_produit_sans_forme_indeterminee_ne_cite_pas_la_croissance_comparee(self):
        t = textes("x*e^x", r"x \to +\infty")
        self.assertIn(r"\(x \to +\infty\) et \(e^{x} \to +\infty\), donc \(\displaystyle\lim_{x\to +\infty} f(x) = +\infty\).", t)
        for phrase in t:
            self.assertNotIn("croissance comparée", phrase)
            self.assertNotIn("indéterminée", phrase)

    def test_inverse_d_un_zero_de_signe_connu(self):
        self.assertEqual(textes("e^(1/x)", r"x \to 0"), [
            r"\(x = 0\) est une valeur interdite.",
            r"Le numérateur vaut \(1\) et le dénominateur \(x\) tend vers \(0\).",
            r"À gauche de \(0\), le dénominateur est négatif (cf. tableau de signes de \(x\)) : il tend vers \(0^{-}\), "
            r"donc \(\frac{1}{x} \to \dfrac{1}{0^{-}} = -\infty\).",
            r"Or \(e^{t} \to 0^{+}\) quand \(t \to -\infty\), donc \(f(x) \to 0\).",
            r"À droite de \(0\), le dénominateur est positif (cf. tableau de signes de \(x\)) : il tend vers \(0^{+}\), "
            r"donc \(\frac{1}{x} \to \dfrac{1}{0^{+}} = +\infty\).",
            r"Or \(e^{t} \to +\infty\) quand \(t \to +\infty\), donc \(f(x) \to +\infty\).",
            r"Asymptote verticale d'équation \(x = 0\) (du côté droit) ; à gauche, \(f(x) \to 0\).",
        ])

    def test_quotient_dont_le_denominateur_tend_vers_zero(self):
        self.assertEqual(textes("ln(x^2-4x)/(x-5)", r"x \to 5"), [
            r"\(x = 5\) est une valeur interdite.",
            r"Le numérateur \(\ln\left(x^{2} - 4x\right)\) vaut "
            r"\(\ln\left(5^{2} - 4 \cdot 5\right) = \ln{\left(5 \right)}\) et le dénominateur \(x - 5\) "
            r"tend vers \(0\).",
            r"À gauche de \(5\), le dénominateur est négatif (cf. tableau de signes de \(x - 5\)) : il tend vers \(0^{-}\), "
            r"donc \(f(x) \to \dfrac{\ln{\left(5 \right)}}{0^{-}} = -\infty\).",
            r"À droite de \(5\), le dénominateur est positif (cf. tableau de signes de \(x - 5\)) : il tend vers \(0^{+}\), "
            r"donc \(f(x) \to \dfrac{\ln{\left(5 \right)}}{0^{+}} = +\infty\).",
            r"Asymptote verticale d'équation \(x = 5\).",
        ])

    def test_une_sous_expression_n_est_commentee_qu_une_fois(self):
        t = textes("(e^x+1)/(e^x-1)", r"x \to -\infty")
        self.assertEqual(sum(1 for p in t if p.startswith(r"Or \(e^{t}")), 1)
        self.assertIn(r"\(e^{x} + 1 \to 1\) et \(e^{x} - 1 \to -1\), donc \(\displaystyle\lim_{x\to -\infty} f(x) = -1\).", t)


def sans_tableau():
    """Le moteur de signe ne construit aucun tableau : la justification reste en texte."""
    return mock.patch.object(la, "_construire_tableau", return_value=None)


class TestConclusionDesValeursInterdites(unittest.TestCase):
    """Chaque valeur interdite se termine par sa conclusion : asymptote (avec le côté si un seul côté est infini),
    trou, ou absence de limite (LA-27)."""

    def conclusion(self, entree, ou):
        return textes(entree, ou)[-1]

    def test_un_seul_cote_infini(self):
        self.assertEqual(self.conclusion("e^(1/x)", r"x \to 0"),
                         r"Asymptote verticale d'équation \(x = 0\) (du côté droit) ; à gauche, \(f(x) \to 0\).")
        self.assertEqual(self.conclusion("e^(-1/x)", r"x \to 0"),
                         r"Asymptote verticale d'équation \(x = 0\) (du côté gauche) ; à droite, \(f(x) \to 0\).")

    def test_deux_cotes_infinis(self):
        self.assertEqual(self.conclusion("(e^x+1)/(e^x-1)", r"x \to 0"), r"Asymptote verticale d'équation \(x = 0\).")

    def test_trou_et_absence_de_limite(self):
        self.assertTrue(self.conclusion("(e^x-1)/x", r"x \to 0").startswith("Les deux limites sont finies et égales à"))
        self.assertTrue(self.conclusion("x/sqrt(x^2)", r"x \to 0").startswith("Limites à gauche et à droite différentes"))

    def test_chaque_valeur_interdite_a_une_conclusion(self):
        concluantes = ("Asymptote verticale", "Les deux limites sont finies", "Limites à gauche et à droite différentes",
                       "f n'est pas définie en", "Ces limites n'ont pas pu", "La limite n'a pas pu")
        for entree in ["1/(x-2)", "(x^2-1)/(x-1)", "1/(x^2-2)", "(x^2-3)/(x^3-3x)", "e^(1/x)", "ln(x)", "ln(x-1)",
                       "(e^x-1)/x", "x/sqrt(x^2)", "x*ln(x^2)", "ln(x^2-4x)/(x-5)", "1/ln(x)", "e^x/x", "x*e^(1/x)"]:
            for etude in la.etudier(entree)["etudes"]:
                if "infty" in etude["ou"]:
                    continue
                with self.subTest(f=entree, ou=etude["ou"]):
                    self.assertTrue(etude["etapes"][-1]["html"].startswith(concluantes), etude["etapes"][-1]["html"])


class TestValeursInterdites(unittest.TestCase):
    """Valeur interdite sans forme indéterminée : le signe du dénominateur se lit dans le tableau de signes
    (un seul, en tête), puis une ligne par côté (LA-14, LA-18, LA-25)."""

    def test_modele_de_l_enseignant(self):
        self.assertEqual(textes("1/(x^2-2)", r"x \to \sqrt{2}"), [
            r"\(x = \sqrt{2}\) est une valeur interdite.",
            r"Le numérateur vaut \(1\) et le dénominateur \(x^{2} - 2\) tend vers \(0\).",
            r"À gauche de \(\sqrt{2}\), le dénominateur est négatif (cf. tableau de signes de \(x^{2} - 2\)) : il tend vers \(0^{-}\), "
            r"donc \(f(x) \to \dfrac{1}{0^{-}} = -\infty\).",
            r"À droite de \(\sqrt{2}\), le dénominateur est positif (cf. tableau de signes de \(x^{2} - 2\)) : il tend vers \(0^{+}\), "
            r"donc \(f(x) \to \dfrac{1}{0^{+}} = +\infty\).",
            r"Asymptote verticale d'équation \(x = \sqrt{2}\).",
        ])

    def test_fraction_rationnelle(self):
        self.assertEqual(textes("(x^2-1)/(x-3)", r"x \to 3"), [
            r"\(x = 3\) est une valeur interdite.",
            r"Le numérateur \(x^{2} - 1\) vaut \(3^{2} - 1 = 8\) et le dénominateur \(x - 3\) tend vers \(0\).",
            r"À gauche de \(3\), le dénominateur est négatif (cf. tableau de signes de \(x - 3\)) : il tend vers \(0^{-}\), "
            r"donc \(f(x) \to \dfrac{8}{0^{-}} = -\infty\).",
            r"À droite de \(3\), le dénominateur est positif (cf. tableau de signes de \(x - 3\)) : il tend vers \(0^{+}\), "
            r"donc \(f(x) \to \dfrac{8}{0^{+}} = +\infty\).",
            r"Asymptote verticale d'équation \(x = 3\).",
        ])

    def test_denominateur_oppose(self):
        t = textes("5/(3-x)", r"x \to 3")
        self.assertEqual(t[2], r"À gauche de \(3\), le dénominateur est positif (cf. tableau de signes de \(3 - x\)) : il tend vers \(0^{+}\), "
                               r"donc \(f(x) \to \dfrac{5}{0^{+}} = +\infty\).")

    def test_meme_limite_des_deux_cotes_une_seule_conclusion(self):
        self.assertEqual(textes("1/(x-1)^2", r"x \to 1"), [
            r"\(x = 1\) est une valeur interdite.",
            r"Le numérateur vaut \(1\) et le dénominateur \(\left(x - 1\right)^{2}\) tend vers \(0\).",
            r"De part et d'autre de \(1\), le dénominateur est positif (cf. tableau de signes de \(\left(x - 1\right)^{2}\)) : il tend vers \(0^{+}\), "
            r"donc \(f(x) \to \dfrac{1}{0^{+}} = +\infty\).",
            r"Donc \(\displaystyle\lim_{x\to 1} f(x) = +\infty\).",
            r"Asymptote verticale d'équation \(x = 1\).",
        ])

    def test_denominateur_factorise(self):
        t = textes("(x^2-3)/(x^3-3x)", r"x \to 0")
        self.assertEqual(t[2], r"À gauche de \(0\), le dénominateur est positif (cf. tableau de signes de \(x^{3} - 3x\)) : il tend vers \(0^{+}\), "
                               r"donc \(f(x) \to \dfrac{-3}{0^{+}} = -\infty\).")

    def test_signe_par_la_monotonie(self):
        t = textes("(e^x+1)/(e^x-1)", r"x \to 0")
        self.assertEqual(t[1], r"Le numérateur \(e^{x} + 1\) vaut \(e^{0} + 1 = 2\) et le dénominateur "
                               r"\(e^{x} - 1\) tend vers \(0\).")
        self.assertEqual(t[2], r"À gauche de \(0\), le dénominateur est négatif (cf. tableau de signes de \(e^{x} - 1\)) : il tend vers \(0^{-}\), "
                               r"donc \(f(x) \to \dfrac{2}{0^{-}} = -\infty\).")

    def test_argument_d_un_logarithme_lu_dans_son_tableau(self):
        t = textes("ln(x^2-4x)/(x-5)", r"x \to 4^+")
        self.assertEqual(t[1], r"À droite de \(4\), l'argument \(x^{2} - 4x\) est positif (cf. tableau de signes de \(x^{2} - 4x\)) : il tend vers \(0^{+}\).")
        self.assertEqual(t[2], r"Or \(\ln t \to -\infty\) quand \(t \to 0^{+}\), donc \(\ln\left(x^{2} - 4x\right) \to -\infty\).")
        self.assertEqual(t[-1], r"Asymptote verticale d'équation \(x = 4\).")

    def test_zero_de_signe_connu_en_un_point_irrationnel(self):
        t = textes("ln(x^2-3)", r"x \to \sqrt{3}^+")
        self.assertEqual(t[1], r"À droite de \(\sqrt{3}\), l'argument \(x^{2} - 3\) est positif (cf. tableau de signes de \(x^{2} - 3\)) : il tend vers \(0^{+}\).")

    def test_zero_de_signe_inconnu_donne_le_repli(self):
        """Pas de tableau ni de factorisation au point irrationnel d'un polynôme de degré 3 : le signe n'est pas inventé."""
        with sans_tableau():
            etape = etapes("ln(x^3-3x)", r"x \to \sqrt{3}^+")[1]
        self.assertEqual(etape["html"], REPLI + r"\(\displaystyle\lim_{x\to {\sqrt{3}}^{+}} f(x) = -\infty\).")
        self.assertIn("signe inconnu", etape["detail"])

    def test_chaque_pole_sans_facteur_commun_est_redige(self):
        for entree in ["1/(x-2)", "(2x+1)/(x-1)", "x^2/(x-1)", "1/x^2", "(x^3+1)/(x-2)", "(2x^2+1)/(x^2-1)", "1/(x^2-2)"]:
            r = la.etudier(entree)
            for etude in r["etudes"]:
                if "infty" in etude["ou"]:
                    continue
                with self.subTest(f=entree, ou=etude["ou"]):
                    t = [e["html"] for e in etude["etapes"]]
                    self.assertFalse(any(p.startswith(REPLI) for p in t), t)
                    self.assertEqual(sum(1 for p in t if p.startswith("Le numérateur")), 1)
                    self.assertTrue(any(p.startswith(("À gauche de", "De part et d'autre de")) for p in t), t)
                    self.assertTrue(t[-1].startswith("Asymptote verticale d'équation"), t[-1])

    def test_garde_fou_sur_un_pole_rationnel(self):
        with mock.patch.object(la, "_noeud", side_effect=la.Abandon("essai")):
            avec = la.etudier("1/(x-2)")
        normal = la.etudier("1/(x-2)")
        self.assertEqual(avec["asymptotes"], normal["asymptotes"])
        t = [e["html"] for e in next(e for e in avec["etudes"] if e["ou"] == r"x \to 2")["etapes"]]
        self.assertEqual(sum(1 for p in t if REPLI[1:] in p), 2)       # un repli par côté (limites différentes)
        self.assertTrue(t[1].startswith("À gauche : ") and t[2].startswith("À droite : "), t)


class TestLogarithmeSurAffine(unittest.TestCase):
    """ln(x²−4x)/(x−5) : seules les bornes ±∞ (forme ∞/∞, méthodes L6/L7) donnent la phrase de repli ;
    en 0⁻, 4⁺, 5⁻ et 5⁺ tout est rédigé."""

    def test_repli_seulement_en_l_infini(self):
        r = la.etudier("ln(x^2-4x)/(x-5)")
        avec_repli = {e["ou"] for e in r["etudes"] if any(REPLI[1:] in st["html"] for st in e["etapes"])}
        self.assertEqual(avec_repli, {r"x \to -\infty", r"x \to +\infty"})

    def test_chaque_ligne_qui_lit_un_tableau_y_renvoie(self):
        t0 = textes("ln(x^2-4x)/(x-5)", r"x \to 0^-")
        self.assertIn(r"À gauche de \(0\), l'argument \(x^{2} - 4x\) est positif "
                      r"(cf. tableau de signes de \(x^{2} - 4x\)) : il tend vers \(0^{+}\).", t0)
        t4 = textes("ln(x^2-4x)/(x-5)", r"x \to 4^+")
        self.assertIn(r"À droite de \(4\), l'argument \(x^{2} - 4x\) est positif "
                      r"(cf. tableau de signes de \(x^{2} - 4x\)) : il tend vers \(0^{+}\).", t4)
        t5 = textes("ln(x^2-4x)/(x-5)", r"x \to 5")
        self.assertIn(r"À gauche de \(5\), le dénominateur est négatif (cf. tableau de signes de \(x - 5\)) : "
                      r"il tend vers \(0^{-}\), donc \(f(x) \to \dfrac{\ln{\left(5 \right)}}{0^{-}} = -\infty\).", t5)
        self.assertIn(r"À droite de \(5\), le dénominateur est positif (cf. tableau de signes de \(x - 5\)) : "
                      r"il tend vers \(0^{+}\), donc \(f(x) \to \dfrac{\ln{\left(5 \right)}}{0^{+}} = +\infty\).", t5)

    def test_titres_des_tableaux(self):
        titres = [i["html"] for i in la.etudier("ln(x^2-4x)/(x-5)")["tableaux_signe"] if i["type"] == "texte"]
        self.assertEqual(titres, [r"Signe de \(x^{2} - 4x\) :", r"Signe de \(x - 5\) :"])


class TestTableauxDeSignes(unittest.TestCase):
    """Le signe d'un dénominateur (ou de l'argument d'un ln qui tend vers 0) vient du tableau de signes de
    l'outil « Ensemble de définition » : un tableau en tête, valeurs interdites en double barre (LA-25)."""

    def tableaux(self, entree):
        return [i for i in la.etudier(entree)["tableaux_signe"] if i.get("type") == "tableau"]

    def test_1_sur_x2_moins_2(self):
        (t,) = self.tableaux("1/(x^2-2)")
        self.assertEqual(t["crit"], [r"-\sqrt{2}", r"\sqrt{2}"])
        self.assertEqual([(r["label"], r["cells"]) for r in t["rows"]], [("x^{2} - 2", ["+", "||", "-", "||", "+"])])

    def test_x_plus_1_sur_x2_moins_4(self):
        (t,) = self.tableaux("(x+1)/(x^2-4)")
        self.assertEqual(t["crit"], ["-2", "2"])
        self.assertEqual([r["cells"] for r in t["rows"]],
                         [["-", "||", "-", "||", "+"], ["-", "||", "+", "||", "+"], ["+", "||", "-", "||", "+"]])
        self.assertTrue(t["rows"][-1]["final"])

    def test_exponentielle(self):
        (t,) = self.tableaux("(e^x+1)/(e^x-1)")
        self.assertEqual((t["crit"], t["rows"][-1]["cells"]), (["0"], ["-", "||", "+"]))

    def test_logarithme_puis_denominateur(self):
        ln, den = self.tableaux("ln(x^2-4x)/(x-5)")
        self.assertEqual(ln["crit"], ["0", "4"])
        self.assertEqual(ln["rows"][-1]["cells"], ["+", "0", "-", "0", "+"])
        self.assertEqual((den["crit"], den["rows"][-1]["cells"]), (["5"], ["-", "||", "+"]))
        titres = [i["html"] for i in la.etudier("ln(x^2-4x)/(x-5)")["tableaux_signe"] if i["type"] == "texte"]
        self.assertEqual(titres, [r"Signe de \(x^{2} - 4x\) :", r"Signe de \(x - 5\) :"])

    def test_x2_moins_1_sur_x_moins_3(self):
        (t,) = self.tableaux("(x^2-1)/(x-3)")
        self.assertEqual((t["crit"], t["rows"][-1]["cells"]), (["3"], ["-", "||", "+"]))

    def test_aucun_tableau_sans_valeur_interdite_a_signe(self):
        for entree in ["e^(2x)", "x^2/2", "x^3-3x", "(2x+1)/(x^2+1)"]:
            self.assertEqual(la.etudier(entree)["tableaux_signe"], [], entree)

    def test_le_tableau_est_lu_et_les_deux_cotes_concordent(self):
        """La lecture du tableau et le signe calculé par les règles sur les limites doivent coïncider."""
        for entree in ["1/(x^2-2)", "(x+1)/(x^2-4)", "(e^x+1)/(e^x-1)", "1/(x^2-4x+4)", "(x^2+1)/(x^3-x)"]:
            r = la.etudier(entree)
            textes_ = " ".join(e["html"] for et in r["etudes"] for e in et["etapes"])
            self.assertIn("cf. tableau de signes de", textes_, entree)
            self.assertNotIn("Signe de", textes_, entree)

    def test_sans_tableau_on_garde_la_justification_en_texte(self):
        with sans_tableau():
            r = la.etudier("1/(x^2-2)")
        self.assertEqual(r["tableaux_signe"], [])
        t = [e["html"] for e in next(e for e in r["etudes"] if e["ou"] == r"x \to \sqrt{2}")["etapes"]]
        self.assertEqual(t[2], r"Signe de \(x^{2} - 2\) (trinôme, racines \(- \sqrt{2}\) et \(\sqrt{2}\)) : "
                               r"négatif entre \(- \sqrt{2}\) et \(\sqrt{2}\), positif pour \(x > \sqrt{2}\).")
        self.assertEqual(t[3], r"À gauche : \(x^{2} - 2 \to 0^{-}\), donc \(f(x) \to \dfrac{1}{0^{-}} = -\infty\).")

    def test_un_tableau_qui_contredit_le_calcul_donne_le_repli(self):
        class Faux(la.TableauSigne):
            def lire(self, pt):
                return -super().lire(pt)
        vrai = la._construire_tableau("den", la.lire("x-3"))
        faux = Faux(vrai.genre, vrai.A, vrai.c, vrai.infos, [])
        with mock.patch.object(la.TABLEAUX, "chercher", return_value=faux):
            t = etapes("(x^2-1)/(x-3)", r"x \to 3")
        self.assertTrue(any(REPLI[1:] in e["html"] for e in t))
        self.assertTrue(any("contredit" in e.get("detail", "") for e in t))


class TestMiseEnEvidence(unittest.TestCase):
    """L3 : polynômes et fractions rationnelles en ±∞ — forme indéterminée nommée, terme dominant mis en
    évidence, chaque terme écrit (LA-13, LA-18, LA-19)."""

    def test_polynome_infini_moins_infini(self):
        self.assertEqual(textes("x^3-3x", r"x \to -\infty"), [
            r"\(x^{3} \to -\infty\) et \(-3x \to +\infty\) : forme indéterminée « \(\infty - \infty\) ».",
            r"On met en évidence le terme de plus haut degré : "
            r"\(x^{3} - 3x = x^{3}\left(1 - \dfrac{3}{x^{2}}\right)\).",
            r"Quand \(x \to -\infty\), \(\dfrac{3}{x^{2}} \to 0\), donc \(1 - \dfrac{3}{x^{2}} \to 1\).",
            r"Comme \(x^{3} \to -\infty\) et que le facteur entre parenthèses tend vers 1, "
            r"\(x^{3} - 3x \to -\infty\).",
            r"Donc \(\displaystyle\lim_{x\to -\infty} f(x) = -\infty\).",
            "La limite est infinie : pas d'asymptote horizontale.",
            r"Le polynôme est de degré 3 \(\geq 2\) : pas d'asymptote oblique (branche parabolique).",
        ])

    def test_polynome_sans_forme_indeterminee(self):
        t = textes("x^3+x", r"x \to -\infty")
        self.assertEqual(t[0], r"\(x^{3} \to -\infty\) et \(x \to -\infty\), donc \(x^{3} + x \to -\infty\).")
        self.assertFalse(any("indéterminée" in p or "mise en évidence" in p for p in t))

    def test_fraction_rationnelle_infini_sur_infini(self):
        self.assertEqual(textes("(2x^2+3x)/(x^2+1)", r"x \to +\infty"), [
            r"Le numérateur tend vers \(+\infty\) et le dénominateur tend vers \(+\infty\) "
            r"(limite de leur terme de plus haut degré) : forme indéterminée « \(\infty/\infty\) ».",
            r"On met en évidence le terme de plus haut degré : "
            r"\(2x^{2} + 3x = 2\,x^{2}\left(1 + \dfrac{3}{2x}\right)\) et "
            r"\(x^{2} + 1 = x^{2}\left(1 + \dfrac{1}{x^{2}}\right)\).",
            r"Donc \(\frac{2x^{2} + 3x}{x^{2} + 1} = \dfrac{2\,x^{2}\left(1 + \dfrac{3}{2x}\right)}"
            r"{x^{2}\left(1 + \dfrac{1}{x^{2}}\right)} = 2 \cdot \dfrac{1 + \dfrac{3}{2x}}{1 + \dfrac{1}{x^{2}}}\).",
            r"Quand \(x \to +\infty\), \(\dfrac{3}{2x} \to 0\) et \(\dfrac{1}{x^{2}} \to 0\) : "
            r"le quotient \(\dfrac{1 + \dfrac{3}{2x}}{1 + \dfrac{1}{x^{2}}}\) tend vers 1.",
            r"Le quotient tend vers 1 : la limite est \(2\) (rapport des coefficients dominants).",
            r"Donc \(\displaystyle\lim_{x\to +\infty} f(x) = 2\).",
            r"Asymptote horizontale d'équation \(y = 2\).",
        ])

    def test_numerateur_constant_pas_de_mise_en_evidence(self):
        self.assertEqual(textes("1/(x-2)", r"x \to -\infty"), [
            r"Le numérateur vaut \(1\) et le dénominateur \(x - 2\) tend vers \(-\infty\) "
            r"(limite de son terme de plus haut degré), donc \(\frac{1}{x - 2} \to 0\).",
            r"Donc \(\displaystyle\lim_{x\to -\infty} f(x) = 0\).",
            r"Asymptote horizontale d'équation \(y = 0\).",
        ])

    def test_degre_du_numerateur_superieur(self):
        t = textes("x^2/(x-1)", r"x \to +\infty")
        self.assertIn(r"Le quotient tend vers 1 et \(x \to +\infty\) : la limite est \(+\infty\).", t)
        self.assertIn("La limite est infinie : pas d'asymptote horizontale.", t)
        self.assertTrue(any(p.startswith("Le degré du numérateur dépasse celui du dénominateur de 1") for p in t))

    def test_racine_d_un_trinome_avec_et_sans_forme_indeterminee(self):
        moins = textes("sqrt(x^2-4x+5)", r"x \to -\infty")
        plus = textes("sqrt(x^2-4x+5)", r"x \to +\infty")
        self.assertEqual(moins[:2], [
            r"\(x^{2} \to +\infty\) et \(-4x \to +\infty\), donc \(x^{2} - 4x + 5 \to +\infty\).",
            r"Or \(\sqrt{t} \to +\infty\) quand \(t \to +\infty\), donc \(\displaystyle\lim_{x\to -\infty} f(x) = +\infty\).",
        ])
        self.assertEqual(plus[0], r"\(x^{2} \to +\infty\) et \(-4x \to -\infty\) : forme indéterminée « \(\infty - \infty\) ».")
        self.assertIn(r"On met en évidence le terme de plus haut degré : "
                      r"\(x^{2} - 4x + 5 = x^{2}\left(1 - \dfrac{4}{x} + \dfrac{5}{x^{2}}\right)\).", plus)
        self.assertIn(r"Or \(\sqrt{t} \to +\infty\) quand \(t \to +\infty\), "
                      r"donc \(\displaystyle\lim_{x\to +\infty} f(x) = +\infty\).", plus)

    def test_ecriture_des_coefficients(self):          # LA-19
        for entree in ["2x^2-x+1", "(2x^2+3x)/(x^2+1)", "(3x+1)/(2x-4)", "x^3-3x", "(x^2+1)/(3x^2-6)"]:
            r = la.etudier(entree)
            for etude in r["etudes"]:
                for e in etude["etapes"]:
                    with self.subTest(f=entree, ou=etude["ou"]):
                        self.assertNotIn(r"\dfrac{\frac", e["html"])
                        self.assertNotIn(r"\frac{\frac", e["html"])
                        self.assertNotIn("}{1}", e["html"].replace(r"\dfrac{1}{1}", ""))
                        self.assertNotIn("\\right)}{1}", e["html"])
        t = " ".join(textes("(3x+1)/(2x-4)", r"x \to +\infty"))
        self.assertIn(r"3\,x\left(1 + \dfrac{1}{3x}\right)", t)
        self.assertIn(r"2\,x\left(1 - \dfrac{2}{x}\right)", t)

    def test_somme_de_fractions_ramenee_a_une_fraction(self):
        t = textes("x^2/(x-1)-x", r"x \to +\infty")
        self.assertEqual(t[0], r"On écrit \(f\) sous la forme d'une seule fraction : \(f(x) = \frac{x}{x - 1}\).")
        self.assertEqual(t[-2:], [r"Donc \(\displaystyle\lim_{x\to +\infty} f(x) = 1\).",
                                  r"Asymptote horizontale d'équation \(y = 1\)."])

    def test_garde_fou_polynome_et_fraction(self):
        for entree, ou in [("x^3-3x", r"x \to +\infty"), ("(2x^2+3x)/(x^2+1)", r"x \to +\infty")]:
            with self.subTest(f=entree):
                normal = la.etudier(entree)
                with mock.patch.object(la, "_phrases_polynome_infini", return_value=(["faux"], la.Lim.infini(-1))), \
                        mock.patch.object(la, "_phrases_fraction_infini", return_value=(["faux"], la.Lim.infini(-1))):
                    faux = la.etudier(entree)
                self.assertEqual(faux["asymptotes"], normal["asymptotes"])
                t = [e["html"] for e in next(e for e in faux["etudes"] if e["ou"] == ou)["etapes"]]
                self.assertTrue(t[0].startswith(REPLI), t)
                self.assertNotIn("faux", " ".join(t))


class TestZeroSurZero(unittest.TestCase):
    """L3 : forme 0/0 en une valeur — nommée, on factorise, on simplifie, puis on passe à la limite."""

    def test_trou(self):
        self.assertEqual(textes("(x^2-1)/(x-1)", r"x \to 1"), [
            r"\(x = 1\) est une valeur interdite.",
            r"Le numérateur et le dénominateur tendent vers \(0\) quand \(x \to 1\) : "
            r"forme indéterminée « \(0/0\) ».",
            r"On factorise le numérateur et le dénominateur par \(\left(x-1\right)\) et l'on simplifie "
            r"(pour \(x \neq 1\)) : \(f(x) = \dfrac{\left(x + 1\right)\,\cancel{\left(x-1\right)}}"
            r"{\cancel{\left(x-1\right)}} = x + 1\).",
            r"Donc \(\displaystyle\lim_{x\to 1} f(x) = \lim_{x\to 1} \left(x + 1\right) = 1 + 1 = 2\).",
            r"f n'est pas définie en \(x=1\), mais sa limite y est finie (\(=2\)) : pas d'asymptote verticale, "
            r"trou dans le graphique en \((1\,;\,2)\).",
        ])

    def test_pole_restant_apres_simplification(self):
        t = textes("(x^2-4)/(x^2-4x+4)", r"x \to 2")
        self.assertIn("forme indéterminée « \\(0/0\\) ».", " ".join(t))
        self.assertIn(r"Le numérateur \(x + 2\) vaut \(2 + 2 = 4\) et le dénominateur \(x - 2\) tend vers \(0\).", t)
        self.assertIn(r"À gauche de \(2\), le dénominateur est négatif (cf. tableau de signes de \(x - 2\)) : il tend vers \(0^{-}\), "
                      r"donc \(f(x) \to \dfrac{4}{0^{-}} = -\infty\).", t)
        self.assertEqual(t[-1], r"Asymptote verticale d'équation \(x = 2\).")

    def test_aucune_forme_zero_sur_zero_sans_facteur_commun(self):
        for entree in ["1/(x-2)", "(x^2-1)/(x-3)", "1/x^2"]:
            for etude in la.etudier(entree)["etudes"]:
                self.assertFalse(any("0/0" in e["html"] for e in etude["etapes"]), (entree, etude["ou"]))


class TestTermesDominants(unittest.TestCase):
    """L5 : en ±∞, quotient dont un membre est une racine — chaque membre est remplacé par son terme dominant,
    le remplacement est justifié (rapport → 1) et « x < 0 donc √(x²) = |x| = −x » est écrit en −∞ (LA-20)."""

    def test_racine_sur_affine_en_plus_l_infini(self):
        t = textes("sqrt(4x^2+1)/(x+2)", r"x \to +\infty")
        self.assertEqual(t[3:], [
            r"Le numérateur \(\sqrt{4x^{2} + 1}\) tend vers \(+\infty\) et le dénominateur \(x + 2\) tend vers "
            r"\(+\infty\) : forme indéterminée « \(\infty/\infty\) ».",
            r"Au voisinage de \(+\infty\), on remplace chaque membre par son terme dominant.",
            r"\(\sqrt{4x^{2} + 1} \sim \sqrt{4\,x^{2}} = 2|x| = 2\,x\) (car \(x > 0\)).",
            r"\(x + 2 \sim x\).",
            r"En effet, le rapport de chaque membre à son terme dominant tend vers 1 : "
            r"\(\dfrac{\sqrt{4x^{2} + 1}}{\sqrt{4\,x^{2}}} = \sqrt{1 + \dfrac{1}{4x^{2}}} \to 1\).",
            r"Donc \(\frac{\sqrt{4x^{2} + 1}}{x + 2} \sim \dfrac{2\,x}{x} = 2\), "
            r"d'où \(\displaystyle\lim_{x\to +\infty} f(x) = 2\).",
            r"Asymptote horizontale d'équation \(y = 2\).",
        ])

    def test_racine_sur_affine_en_moins_l_infini(self):
        t = textes("sqrt(4x^2+1)/(x+2)", r"x \to -\infty")
        self.assertIn(r"Comme \(x < 0\), \(\sqrt{x^{2}} = |x| = -x\).", t)
        self.assertIn(r"\(\sqrt{4x^{2} + 1} \sim \sqrt{4\,x^{2}} = 2|x| = -2\,x\).", t)
        self.assertIn(r"Donc \(\frac{\sqrt{4x^{2} + 1}}{x + 2} \sim \dfrac{-2\,x}{x} = -2\), "
                      r"d'où \(\displaystyle\lim_{x\to -\infty} f(x) = -2\).", t)

    def test_pente_d_une_racine_de_trinome(self):             # a = lim f(x)/x pour √(x²−4x+5)
        self.assertIn(r"d'où \(\displaystyle\lim_{x\to +\infty} f(x) = 1\).", " ".join(textes("sqrt(x^2-4x+5)/x", r"x \to +\infty")))
        t = textes("sqrt(x^2-4x+5)/x", r"x \to -\infty")
        self.assertIn(r"Comme \(x < 0\), \(\sqrt{x^{2}} = |x| = -x\).", t)
        self.assertIn(r"d'où \(\displaystyle\lim_{x\to -\infty} f(x) = -1\).", " ".join(t))

    def test_racine_d_un_carre(self):
        t = textes("x/sqrt(x^2)", r"x \to -\infty")
        self.assertIn(r"\(\sqrt{x^{2}} = |x| = -x\).", t)
        self.assertIn(r"Donc \(\frac{x}{\sqrt{x^{2}}} \sim \dfrac{x}{-x} = -1\), d'où "
                      r"\(\displaystyle\lim_{x\to -\infty} f(x) = -1\).", t)

    def test_somme_de_racines_au_denominateur(self):
        t = textes("sqrt(x^2+1)/(sqrt(x^2+4)+1)", r"x \to +\infty")
        self.assertIn(r"\(\sqrt{x^{2} + 4} + 1 \sim x\).", t)

    def test_jamais_pour_une_fraction_rationnelle_ni_quand_les_termes_se_compensent(self):
        for entree in ["(2x^2+3x)/(x^2+1)", "x^3-3x", "x^2/(x-1)", "1/(x-2)"]:
            for etude in la.etudier(entree)["etudes"]:
                self.assertFalse(any("terme dominant" in e["html"] for e in etude["etapes"]), (entree, etude["ou"]))
        # √(x²+x) − x en +∞ : les termes dominants se compensent (∞ − ∞) : pas de remplacement par les dominants
        t = textes("sqrt(x^2+x)-x", r"x \to +\infty")
        premiere = next(i for i, p in enumerate(t) if "terme dominant" in p)
        self.assertTrue(any("conjuguée" in p for p in t[:premiere]), t)

    def test_garde_fou(self):
        with mock.patch.object(la, "_dominant", side_effect=lambda n, s: (la._sympy().Integer(3), 1)):
            t = etapes("sqrt(4x^2+1)/(x+2)", r"x \to +\infty")
        self.assertTrue(any(REPLI[1:] in e["html"] for e in t))
        self.assertFalse(any("terme dominant" in e["html"] for e in t))


class TestConjuguee(unittest.TestCase):
    """L4 : expression conjuguée — ∞ − ∞ avec une racine en ±∞, 0/0 avec une racine en une valeur (LA-20)."""

    def test_racine_moins_x_en_plus_l_infini(self):
        t = textes("sqrt(x^2+x)-x", r"x \to +\infty")
        i = t.index(r"\(\sqrt{x^{2} + x} \to +\infty\) et \(x \to +\infty\) : forme indéterminée « \(\infty - \infty\) ».")
        self.assertEqual(t[i + 1:i + 3], [
            r"On multiplie et on divise par l'expression conjuguée \(\sqrt{x^{2} + x} + x\) :",
            r"\(\sqrt{x^{2} + x} - x = \dfrac{\left(\sqrt{x^{2} + x} - x\right)\left(\sqrt{x^{2} + x} + x\right)}"
            r"{\sqrt{x^{2} + x} + x} = \dfrac{\left(x^{2} + x\right) - x^{2}}{\sqrt{x^{2} + x} + x} = "
            r"\dfrac{x}{\sqrt{x^{2} + x} + x}\).",
        ])
        self.assertIn(r"Donc \(\displaystyle\lim_{x\to +\infty} f(x) = \frac{1}{2}\).", t)
        self.assertIn(r"\(\sqrt{x^{2} + x} + x \sim 2\,x\).", t)

    def test_racine_moins_x_en_moins_l_infini_pas_de_forme_indeterminee(self):
        t = textes("sqrt(x^2+x)-x", r"x \to -\infty")
        self.assertFalse(any("conjuguée" in p for p in t), t)
        self.assertIn(r"\(\sqrt{x^{2} + x} \to +\infty\) et \(x \to -\infty\), donc "
                      r"\(\displaystyle\lim_{x\to -\infty} f(x) = +\infty\).", t)

    def test_ordonnee_a_l_origine_d_une_asymptote_oblique(self):   # b = lim (f(x) − ax)
        plus = " ".join(textes("sqrt(x^2-4x+5)-x", r"x \to +\infty"))
        self.assertIn(r"d'où \(\displaystyle\frac{-4x + 5}{\sqrt{x^{2} - 4x + 5} + x} \to -2\)".replace(r"\displaystyle", ""), plus)
        self.assertIn(r"\lim_{x\to +\infty} f(x) = -2", plus)
        moins = " ".join(textes("sqrt(x^2-4x+5)+x", r"x \to -\infty"))
        self.assertIn("expression conjuguée", moins)
        self.assertIn(r"Comme \(x < 0\), \(\sqrt{x^{2}} = |x| = -x\).", moins)
        self.assertIn(r"\lim_{x\to -\infty} f(x) = 2", moins)

    def test_zero_sur_zero_conjuguee_du_numerateur(self):
        t = textes("(sqrt(x+3)-2)/(x-1)", r"x \to 1")
        self.assertEqual(t[:7], [
            r"\(x = 1\) est une valeur interdite.",
            r"Le numérateur \(\sqrt{x + 3} - 2\) tend vers \(0\) et le dénominateur \(x - 1\) tend vers \(0\) : "
            r"forme indéterminée « \(0/0\) ».",
            r"On multiplie le numérateur et le dénominateur par l'expression conjuguée \(\sqrt{x + 3} + 2\) du numérateur :",
            r"\(\frac{\sqrt{x + 3} - 2}{x - 1} = \dfrac{\left(\sqrt{x + 3} - 2\right)\left(\sqrt{x + 3} + 2\right)}"
            r"{\left(x - 1\right)\,\left(\sqrt{x + 3} + 2\right)} = \dfrac{\left(x + 3\right) - 2^{2}}"
            r"{\left(x - 1\right)\,\left(\sqrt{x + 3} + 2\right)} = \dfrac{x - 1}"
            r"{\left(x - 1\right)\,\left(\sqrt{x + 3} + 2\right)}\).",
            r"On factorise et on simplifie par \(\left(x-1\right)\) (pour \(x \neq 1\)) : "
            r"\(f(x) = \dfrac{\cancel{\left(x-1\right)}}{\cancel{\left(x-1\right)}\,\left(\sqrt{x + 3} + 2\right)} = "
            r"\frac{1}{\sqrt{x + 3} + 2}\).",
            r"Quand \(x \to 1\), \(\frac{1}{\sqrt{x + 3} + 2} \to \frac{1}{\sqrt{1 + 3} + 2} = \frac{1}{4}\).",
            r"Donc \(\displaystyle\lim_{x\to 1} f(x) = \frac{1}{4}\).",
        ])

    def test_zero_sur_zero_conjuguee_du_denominateur(self):
        t = " ".join(textes("(x-1)/(sqrt(x+3)-2)", r"x \to 1"))
        self.assertIn("conjuguée \\(\\sqrt{x + 3} + 2\\) du dénominateur", t)
        self.assertIn(r"\lim_{x\to 1} f(x) = 4", t)

    def test_jamais_sans_racine(self):
        for entree in ["x^3-3x", "(x^2-1)/(x-1)", "x^2-4x", "e^x-1"]:
            for etude in la.etudier(entree)["etudes"]:
                self.assertFalse(any("conjuguée" in e["html"] for e in etude["etapes"]), (entree, etude["ou"]))

    def test_garde_fou(self):
        with mock.patch.object(la, "_carre_poly", side_effect=lambda n: [la.F(1), la.F(1)]):
            t = etapes("sqrt(x^2+x)-x", r"x \to +\infty")
        self.assertTrue(any(REPLI[1:] in e["html"] for e in t))
        self.assertFalse(any("conjuguée" in e["html"] for e in t))


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
        with mock.patch.object(la, "_noeud", return_value=(la.Lim.infini(1), [])):
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
                    if any(REPLI[1:] in p for p in t):
                        continue
                    conclusions = [p for p in t if r"\lim_{x\to" in p or r"f(x) \to" in p or "Limites à gauche" in p]
                    self.assertTrue(conclusions, t)
                    self.assertTrue(any("donc" in p or "Or " in p for p in t), t)


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


class TestStyle(unittest.TestCase):
    """Règles de style (LA-21 à LA-24) : élève moyen de gymnase, une idée par ligne, rien de mécanique."""

    INTERDITES = [r"par continuité", r"est une constante", r"la différence tend vers", r"la somme tend vers",
                  r"le produit tend vers", r"le quotient tend vers \\\(", r"Par substitution", r"il vaut"]
    CORPUS = (TestToutEstEcritOuReplie.ENTREES + CAS + ["(x^2-1)/(x-1)", "(x^2-4)/(x^2-4x+4)", "1/(x-1)^2",
              "5/(3-x)", "(x^2-3)/(x^3-3x)", "1/(x^2-2)", "ln(x^2-3)", "ln(x^3-3x)", "x^2/(x-1)-x", "(x+1)/(x-1)/2"])

    def tous_les_textes(self):
        import json, os
        vus = set()
        for entree in self.CORPUS:
            if entree in vus:
                continue
            vus.add(entree)
            r = la.etudier(entree)
            for etude in r.get("etudes", []):
                yield entree, etude["ou"], [e["html"] for e in etude["etapes"]]
        dossier = os.path.join(os.path.dirname(__file__), "instantanes")
        with open(os.path.join(dossier, "limites-asymptotes.json"), encoding="utf-8") as fh:
            for entree, r in json.load(fh).items():
                for etude in r.get("etudes", []) if isinstance(r, dict) else []:
                    yield "instantané " + entree, etude["ou"], [e["html"] for e in etude["etapes"]]

    def test_phrases_interdites(self):                                   # LA-21
        import re
        for entree, ou, t in self.tous_les_textes():
            for phrase in t:
                for interdite in self.INTERDITES:
                    with self.subTest(f=entree, ou=ou, interdite=interdite):
                        self.assertIsNone(re.search(interdite, phrase, re.I), phrase)

    def test_signe_d_un_denominateur_toujours_justifie(self):            # LA-22
        for entree, ou, t in self.tous_les_textes():
            if any(REPLI[1:] in p for p in t):
                continue
            for i, p in enumerate(t):
                if p.startswith("Le numérateur") and "tend vers \\(0\\)" in p:
                    with self.subTest(f=entree, ou=ou):
                        suite = t[i + 1]
                        self.assertTrue(suite.startswith(("Signe de", "À gauche de", "À droite de", "De part et d'autre de")), suite)
                if r"quand \(t \to 0^{+}\) et" in p:
                    with self.subTest(f=entree, ou=ou):
                        self.assertTrue(any(q.startswith("Signe de") for q in t[:i]), t)
                if "l'argument" in p and p.startswith(("À gauche de", "À droite de")):
                    with self.subTest(f=entree, ou=ou):
                        self.assertIn("(cf. tableau de signes de", p)

    def test_chaque_renvoi_a_son_tableau(self):                           # LA-28
        """« (cf. tableau de signes de X) » renvoie à un tableau titré « Signe de X : » présent dans la même étude."""
        import re
        for entree in ["1/(x^2-2)", "(x+1)/(x^2-4)", "(e^x+1)/(e^x-1)", "ln(x^2-4x)/(x-5)", "(x^2-1)/(x-3)",
                       "(x^2-4)/(x^2-4x+4)", "ln(x^2-3)", "e^(1/x)", "1/(x-1)^2", "ln(x)/x"]:
            r = la.etudier(entree)
            titres = {i["html"] for i in r["tableaux_signe"] if i["type"] == "texte"}
            renvois = [m for et in r["etudes"] for e in et["etapes"]
                       for m in re.findall(r"\(cf\. tableau de signes de (\\\(.*?\\\))\)", e["html"])]
            with self.subTest(f=entree):
                for expr in renvois:
                    self.assertIn(f"Signe de {expr} :", titres)
                self.assertEqual(len(titres), len({r_ for r_ in renvois}) if renvois else 0)

    def test_valeur_interdite_partie_commune_une_seule_fois(self):       # LA-23
        for entree in ["1/(x-2)", "(x^2-1)/(x-3)", "1/(x^2-2)", "(e^x+1)/(e^x-1)", "e^(1/x)", "ln(x^2-4x)/(x-5)",
                       "(x^2-3)/(x^3-3x)", "1/(x-1)^2"]:
            r = la.etudier(entree)
            for etude in r["etudes"]:
                t = [e["html"] for e in etude["etapes"]]
                if not any(p.endswith("est une valeur interdite.") for p in t):
                    continue
                with self.subTest(f=entree, ou=etude["ou"]):
                    self.assertEqual(sum(1 for p in t if p.endswith("est une valeur interdite.")), 1)
                    self.assertLessEqual(sum(1 for p in t if p.startswith("Le numérateur")), 1)
                    self.assertLessEqual(sum(1 for p in t if p.startswith("Signe de")), 1)
                    self.assertLessEqual(sum(1 for p in t if p.startswith("À gauche")), 1)
                    self.assertLessEqual(sum(1 for p in t if p.startswith("À droite")), 1)

    def test_une_variable_ne_vaut_jamais_sa_limite(self):               # LA-26
        """Même sans tableau de signes (justification en texte), on n'écrit pas « x est positif (il vaut 4) »."""
        import re
        entrees = ["(x^2-1)/(x-3)", "1/(x^2-2)", "(x+1)/(x^2-4)", "(x^2-3)/(x^3-3x)", "1/(x-1)^2", "5/(3-x)",
                   "(e^x+1)/(e^x-1)", "ln(x^2-4x)/(x-5)", "ln(x^2-3)", "e^(1/x)", "1/x^2", "(2x^2+1)/(x^2-1)"]
        with sans_tableau():
            for entree in entrees:
                for etude in la.etudier(entree)["etudes"]:
                    for e in etude["etapes"]:
                        with self.subTest(f=entree, ou=etude["ou"]):
                            self.assertIsNone(re.search(r"il vaut", e["html"]), e["html"])

    def test_une_phrase_ne_cite_que_le_vocabulaire_du_cours(self):       # LA-24
        for entree, ou, t in self.tous_les_textes():
            for phrase in t:
                for mot in ("SymPy", "sympy", "Abandon", "exception", "noeud", "arbre"):
                    self.assertNotIn(mot, phrase)


if __name__ == "__main__":
    unittest.main()
