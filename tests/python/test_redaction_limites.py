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
            r"De part et d'autre de \(1\), le dénominateur est positif (\(\left(x - 1\right)^{2} > 0\) pour \(x \neq 1\)) : il tend vers \(0^{+}\), "
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
    """ln(x²−4x)/(x−5) : toutes les bornes sont rédigées (±∞ par Bernoulli-L'Hôpital depuis L7, 0⁻, 4⁺, 5⁻ et 5⁺
    par les règles sur les limites) ; aucune phrase de repli."""

    def test_repli_seulement_en_l_infini(self):
        r = la.etudier("ln(x^2-4x)/(x-5)")
        avec_repli = {e["ou"] for e in r["etudes"] if any(REPLI[1:] in st["html"] for st in e["etapes"])}
        self.assertEqual(avec_repli, set())          # ±∞ : ∞/∞ levée par Bernoulli-L'Hôpital (L7)

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
        for entree in ["1/(x^2-2)", "(x+1)/(x^2-4)", "(e^x+1)/(e^x-1)", "(x^2+1)/(x^3-x)"]:
            r = la.etudier(entree)
            textes_ = " ".join(e["html"] for et in r["etudes"] for e in et["etapes"])
            self.assertIn("cf. tableau de signes de", textes_, entree)
            self.assertNotIn("Signe de", textes_, entree)

    def test_facteurs_evidents_sans_ligne_ni_tableau(self):
        """Un facteur de signe évident (carré, exponentielle, racine d'une expression positive) n'a pas de ligne ;
        si tous le sont, pas de tableau : la lecture cite la phrase."""
        r = la.etudier("1/(x^2-4x+4)")
        self.assertEqual(r["tableaux_signe"], [])
        textes_ = " ".join(e["html"] for et in r["etudes"] for e in et["etapes"])
        self.assertIn(r"le dénominateur est positif (\(\left(x - 2\right)^{2} > 0\) pour \(x \neq 2\))", textes_)
        self.assertNotIn("cf. tableau", textes_)
        # un carré parmi d'autres facteurs : pas de ligne pour (x + 2)², mais sa valeur interdite garde sa colonne
        r = la.etudier("1/((x-1)*(x+2)^2)")
        tab = next(i for i in r["tableaux_signe"] if i.get("type") == "tableau")
        self.assertEqual(tab["crit"], ["-2", "1"])
        self.assertEqual(len(tab["rows"]), 1)
        self.assertEqual(tab["rows"][0]["cells"], ["-", "||", "-", "||", "+"])
        textes_ = " ".join(i.get("html", "") for i in r["tableaux_signe"])
        self.assertIn(r"\(\left(x + 2\right)^{2} > 0\) pour \(x \neq -2\)", textes_)
        self.assertIn("est du signe de", textes_)

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
        t = textes("x^3-3x", r"x \to -\infty")
        self.assertEqual(t[0], r"\(x^{3} \to -\infty\) et \(-3x \to +\infty\) : forme indéterminée « \(\infty - \infty\) ».")
        self.assertEqual(t[1], r"\[\begin{aligned}\lim_{x\to -\infty} f(x) &= \lim_{x\to -\infty} x^{3}\,\left(1 - \frac{3}{x^{2}}\right) = "
                               r"\left(-\infty\right) \cdot 1 = -\infty \qquad \left(\text{on met } x^{3} \text{ en évidence} \; ;\; "
                               r"\frac{3}{x^{2}} \to 0\right)\end{aligned}\]")
        self.assertEqual(t[2:], [
            "La limite est infinie : pas d'asymptote horizontale.",
            r"Le polynôme est de degré 3 \(\geq 2\) : pas d'asymptote oblique (branche parabolique).",
        ])

    def test_polynome_sans_forme_indeterminee(self):
        t = textes("x^3+x", r"x \to -\infty")
        self.assertEqual(t[0], r"\(x^{3} \to -\infty\) et \(x \to -\infty\), donc \(x^{3} + x \to -\infty\).")
        self.assertFalse(any("indéterminée" in p or "mise en évidence" in p for p in t))

    def test_fraction_rationnelle_infini_sur_infini(self):
        t = textes("(2x^2+3x)/(x^2+1)", r"x \to +\infty")
        self.assertEqual(t[0], r"Le numérateur \(2x^{2} + 3x\) tend vers \(+\infty\) et le dénominateur \(x^{2} + 1\) tend vers \(+\infty\) : "
                               r"forme indéterminée « \(\infty/\infty\) ».")
        self.assertEqual(t[1],
                         r"\[\begin{aligned}\lim_{x\to +\infty} f(x) &= \lim_{x\to +\infty} \dfrac{2x^{2}\,\left(1 + \frac{3}{2x}\right)}"
                         r"{x^{2}\,\left(1 + \frac{1}{x^{2}}\right)} \qquad \left(2x^{2} + 3x = 2x^{2}\,\left(1 + \frac{3}{2x}\right) ,\; "
                         r"x^{2} + 1 = x^{2}\,\left(1 + \frac{1}{x^{2}}\right)\right) \\ "
                         r"&= \lim_{x\to +\infty} \frac{2\left(1 + \frac{3}{2x}\right)}{1 + \frac{1}{x^{2}}} = \dfrac{2 \cdot 1}{1} = 2 "
                         r"\qquad \left(\text{on simplifie par } x^{2} \; ;\; \frac{3}{2x} \to 0 \; ;\; \frac{1}{x^{2}} \to 0\right)\end{aligned}\]")
        self.assertEqual(t[2:], [r"Asymptote horizontale d'équation \(y = 2\)."])

    def test_numerateur_constant_pas_de_mise_en_evidence(self):
        self.assertEqual(textes("1/(x-2)", r"x \to -\infty"), [
            r"Le numérateur vaut \(1\) et le dénominateur \(x - 2\) tend vers \(-\infty\) "
            r"(limite de son terme de plus haut degré), donc \(\frac{1}{x - 2} \to 0\).",
            r"Donc \(\displaystyle\lim_{x\to -\infty} f(x) = 0\).",
            r"Asymptote horizontale d'équation \(y = 0\).",
        ])

    def test_degre_du_numerateur_superieur(self):
        t = textes("x^2/(x-1)", r"x \to +\infty")
        ch = chaine("x^2/(x-1)", r"x \to +\infty")
        self.assertIn(r"\dfrac{+\infty}{1} = +\infty", ch)
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
        self.assertIn(r"\lim_{x\to +\infty} \left(x^{2} - 4x + 5\right) &= \lim_{x\to +\infty} x^{2}\,\left(1 - \frac{4}{x} + \frac{5}{x^{2}}\right)", " ".join(plus))
        self.assertIn(r"= \left(+\infty\right) \cdot 1 = +\infty", " ".join(plus))

    def test_ecriture_des_coefficients(self):          # LA-19
        for entree in ["2x^2-x+1", "(2x^2+3x)/(x^2+1)", "(3x+1)/(2x-4)", "x^3-3x", "(x^2+1)/(3x^2-6)"]:
            r = la.etudier(entree)
            for etude in r["etudes"]:
                for e in etude["etapes"]:
                    with self.subTest(f=entree, ou=etude["ou"]):
                        self.assertNotIn(r"\dfrac{\frac", e["html"])
                        self.assertNotIn(r"\frac{\frac", e["html"])
                        self.assertNotIn("\\right)}{1}", e["html"])
        t = chaine("(3x+1)/(2x-4)", r"x \to +\infty")
        self.assertIn(r"3x\,\left(1 + \frac{1}{3x}\right)", t)
        self.assertIn(r"2x\,\left(1 - \frac{2}{x}\right)", t)

    def test_somme_de_fractions_ramenee_a_une_fraction(self):
        t = textes("x^2/(x-1)-x", r"x \to +\infty")
        self.assertEqual(t[0], r"On écrit \(f\) sous la forme d'une seule fraction : \(f(x) = \frac{x}{x - 1}\).")
        self.assertIn(r"= \dfrac{1}{1} = 1", t[-2])
        self.assertEqual(t[-1], r"Asymptote horizontale d'équation \(y = 1\).")

    def test_garde_fou_polynome_et_fraction(self):
        for entree, ou in [("x^3-3x", r"x \to +\infty"), ("(2x^2+3x)/(x^2+1)", r"x \to +\infty")]:
            with self.subTest(f=entree):
                normal = la.etudier(entree)
                with mock.patch.object(la, "_phrases_polynome_infini", return_value=(["faux"], la.Lim.infini(-1))), \
                        mock.patch.object(la, "_evidence_quotient", return_value=(la.Lim.infini(-1), ["faux"])):
                    faux = la.etudier(entree)
                self.assertEqual(faux["asymptotes"], normal["asymptotes"])
                t = [e["html"] for e in next(e for e in faux["etudes"] if e["ou"] == ou)["etapes"]]
                self.assertTrue(t[0].startswith(REPLI), t)
                self.assertNotIn("faux", " ".join(t))


class TestZeroSurZero(unittest.TestCase):
    """L3 : forme 0/0 en une valeur — nommée, on factorise, on simplifie, puis on passe à la limite."""

    def test_trou(self):
        t = textes("(x^2-1)/(x-1)", r"x \to 1")
        self.assertEqual(t[:2], [
            r"\(x = 1\) est une valeur interdite.",
            r"Le numérateur et le dénominateur tendent vers \(0\) quand \(x \to 1\) : forme indéterminée « \(0/0\) ».",
        ])
        self.assertEqual(t[2],
                         r"\[\begin{aligned}\lim_{x\to 1} f(x) &= \lim_{x\to 1} \dfrac{\left(x + 1\right)\,\cancel{\left(x-1\right)}}"
                         r"{\cancel{\left(x-1\right)}} \qquad \left(\text{on factorise par } \left(x-1\right)\right) \\ "
                         r"&= \lim_{x\to 1} \left(x + 1\right) = 1 + 1 = 2 \qquad \left(\text{on simplifie} \; (x \neq 1)\right)\end{aligned}\]")
        self.assertEqual(t[3], r"f n'est pas définie en \(x=1\), mais sa limite y est finie (\(=2\)) : pas d'asymptote verticale, "
                               r"trou dans le graphique en \((1\,;\,2)\).")

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


def chaine(entree, ou):
    """La chaîne d'égalités (formule affichée) de l'étude, ou ''. Chaque ligne est séparée par ' \\\\ '."""
    return " ".join(p for p in textes(entree, ou) if p.startswith(r"\["))


class TestEvidenceRacine(unittest.TestCase):
    """L5 (chaîne d'égalités, règle du 15.10) : en ±∞, quotient dont un membre est une racine — on met x^k en évidence
    dans chaque membre, en égalités exactes (√(4x²+1) = √(x²(4 + 1/x²)) = |x|√(4 + 1/x²), puis |x| = ±x), sans
    équivalent ; « x < 0 donc |x| = −x » est écrit en −∞ (LA-20, LA-29)."""

    def test_racine_sur_affine_en_moins_l_infini(self):            # l'exemple de l'enseignant
        t = textes("sqrt(4x^2+1)/(x+2)", r"x \to -\infty")
        ch = chaine("sqrt(4x^2+1)/(x+2)", r"x \to -\infty")
        self.assertEqual(sum(1 for p in t if p.startswith(r"\[")), 1)
        for morceau in [
            r"\lim_{x\to -\infty} f(x) &= \lim_{x\to -\infty} \dfrac{\sqrt{x^{2}\left(4 + \frac{1}{x^{2}}\right)}}{x\,\left(1 + \frac{2}{x}\right)}",
            r"&= \lim_{x\to -\infty} \dfrac{|x|\sqrt{4 + \frac{1}{x^{2}}}}{x\,\left(1 + \frac{2}{x}\right)}",
            r"&= \lim_{x\to -\infty} \dfrac{-x\,\sqrt{4 + \frac{1}{x^{2}}}}{x\,\left(1 + \frac{2}{x}\right)}",
            r"\left(x < 0 \text{ donc } |x| = -x\right)",
            r"&= \lim_{x\to -\infty} -\frac{\sqrt{4 + \frac{1}{x^{2}}}}{1 + \frac{2}{x}} = -\dfrac{\sqrt{4}}{1} = -2",
        ]:
            self.assertIn(morceau, ch)
        # le texte se limite à la forme indéterminée avant la chaîne et à la conclusion (asymptote) après
        i = next(i for i, p in enumerate(t) if p.startswith(r"\["))
        self.assertIn("forme indéterminée « \\(\\infty/\\infty\\) »", t[i - 1])
        self.assertEqual(t[i + 1:], [r"Asymptote horizontale d'équation \(y = -2\)."])

    def test_racine_sur_affine_en_plus_l_infini(self):
        ch = chaine("sqrt(4x^2+1)/(x+2)", r"x \to +\infty")
        self.assertIn(r"\left(x > 0 \text{ donc } |x| = x\right)", ch)
        self.assertIn(r"&= \lim_{x\to +\infty} \dfrac{x\,\sqrt{4 + \frac{1}{x^{2}}}}{x\,\left(1 + \frac{2}{x}\right)}", ch)
        self.assertIn(r"= \dfrac{\sqrt{4}}{1} = 2", ch)

    def test_pente_d_une_racine_de_trinome(self):             # a = lim f(x)/x pour √(x²−4x+5)
        self.assertIn(r"= \sqrt{1} = 1", chaine("sqrt(x^2-4x+5)/x", r"x \to +\infty"))
        ch = chaine("sqrt(x^2-4x+5)/x", r"x \to -\infty")
        self.assertIn(r"\left(x < 0 \text{ donc } |x| = -x\right)", ch)
        self.assertIn(r"= -\sqrt{1} = -1", ch)

    def test_racine_d_un_carre(self):
        ch = chaine("x/sqrt(x^2)", r"x \to -\infty")
        self.assertIn(r"\dfrac{x}{-x}", ch)
        self.assertIn(r"x < 0 \text{ donc } |x| = -x", ch)
        self.assertIn(r"= -1", ch)

    def test_somme_de_racines_au_denominateur(self):
        ch = chaine("sqrt(x^2+1)/(sqrt(x^2+4)+1)", r"x \to +\infty")
        self.assertIn(r"\sqrt{x^{2} + 4} + 1 = x\,\left(\sqrt{1 + \frac{4}{x^{2}}} + \frac{1}{x}\right)", ch)
        self.assertIn(r"\text{on met } x \text{ en évidence}", ch)
        self.assertIn(r"= 1", ch)

    def test_jamais_pour_une_fraction_rationnelle_ni_quand_les_termes_se_compensent(self):
        for entree in ["(2x^2+3x)/(x^2+1)", "x^3-3x", "x^2/(x-1)", "1/(x-2)"]:
            for etude in la.etudier(entree)["etudes"]:
                self.assertFalse(any("|x|" in e["html"] for e in etude["etapes"]), (entree, etude["ou"]))
        # √(x²+x) − x en +∞ : les termes de plus haut degré se compensent (∞ − ∞) : l'expression conjuguée passe d'abord
        ch = chaine("sqrt(x^2+x)-x", r"x \to +\infty")
        self.assertIn("conjuguée", ch)
        self.assertLess(ch.index("conjuguée"), ch.index("|x|"))

    def test_garde_fou(self):
        with mock.patch.object(la, "_meme_fonction", side_effect=la.Abandon("réécriture fausse")):
            t = etapes("sqrt(4x^2+1)/(x+2)", r"x \to +\infty")
        self.assertTrue(any(REPLI[1:] in e["html"] for e in t))
        self.assertFalse(any("|x|" in e["html"] for e in t))

    def test_aucun_equivalent(self):                 # ni « ∼ », ni « équivalent », ni « se comporte comme »
        for entree in ["sqrt(4x^2+1)/(x+2)", "sqrt(x^2+x)-x", "x/sqrt(x^2)", "ln(x^2+1)/x", "sqrt(x^2+1)/(sqrt(x^2+4)+1)"]:
            r = la.etudier(entree)
            for etude in r["etudes"]:
                for e in etude["etapes"]:
                    for mot in (r"\sim", "∼", "équivalent", "se comporte comme", "terme dominant"):
                        self.assertNotIn(mot, e["html"], (entree, etude["ou"]))


class TestChaineEtReferences(unittest.TestCase):
    def test_chaque_limite_de_reference_cite_son_point(self):
        for nom, (lim, cond) in la.REFERENCES.items():
            self.assertRegex(lim, r"\\lim_\{x\\to [^}]+\}", nom)

    def test_une_chaine_commence_par_lim_f_et_se_termine_par_la_valeur(self):
        for entree, ou, valeur in [("sqrt(4x^2+1)/(x+2)", r"x \to -\infty", "-2"), ("(x^2-1)/(x-3)", r"x \to +\infty", r"+\infty"),
                                   ("e^x-x^2", r"x \to +\infty", r"+\infty"),
                                   ("(sqrt(x+3)-2)/(x-1)", r"x \to 1", r"\frac{1}{4}")]:
            ch = chaine(entree, ou)
            with self.subTest(f=entree, ou=ou):
                self.assertTrue(ch.startswith(r"\[\begin{aligned}\lim_{x\to"), ch[:60])
                self.assertIn("f(x)", ch.split("&=")[0] if "&=" in ch else ch)
                self.assertTrue(ch.endswith(r"\end{aligned}\]"))


class TestEvidenceLn(unittest.TestCase):
    """Retouche 2 : ln(u)/v en ±∞ avec u polynôme : ln(u) = k ln|x| + ln(c + …), puis croissance comparée
    (ln x / x^n → 0), avant Bernoulli-L'Hôpital — en chaîne d'égalités."""

    def test_ln_de_x_carre_plus_1_sur_x(self):
        ch = chaine("ln(x^2+1)/x", r"x \to +\infty")
        self.assertIn(r"\ln\left(x^{2}\left(1 + \frac{1}{x^{2}}\right)\right)", ch)
        self.assertIn(r"2\ln|x| + \ln\left(1 + \frac{1}{x^{2}}\right)", ch)
        self.assertIn(r"2\,\dfrac{\ln|x|}{x} + \dfrac{\ln\left(1 + \frac{1}{x^{2}}\right)}{x} = 2 \cdot 0 + 0 = 0", ch)
        self.assertIn(r"\text{ : croissance comparée, } \lim_{x\to +\infty} \dfrac{\ln x}{x^{n}} = 0", ch)
        self.assertFalse(any("Bernoulli" in p for p in textes("ln(x^2+1)/x", r"x \to +\infty")))

    def test_en_moins_l_infini_on_pose_t_egal_moins_x(self):
        ch = chaine("ln(x^2+1)/x", r"x \to -\infty")
        self.assertIn(r"t = -x \to +\infty", ch)
        self.assertIn(r"\lim_{t\to +\infty} \dfrac{\ln t}{t^{n}} = 0", ch)
        self.assertFalse(any("Bernoulli" in p for p in textes("ln(x^2+1)/x", r"x \to -\infty")))

    def test_denominateur_mis_en_evidence(self):
        ch = chaine("ln(x^2-4x)/(x-5)", r"x \to +\infty")
        self.assertIn(r"x - 5 = x\,\left(1 - \frac{5}{x}\right)", ch)
        self.assertFalse(any("Bernoulli" in p for p in textes("ln(x^2-4x)/(x-5)", r"x \to +\infty")))

    def test_avant_l_hopital_seulement_pour_ln_de_polynome(self):
        for entree, ou in [("ln(x)/(x-1)", r"x \to 1"), ("x*ln(x^2)", r"x \to 0")]:
            self.assertTrue(any("Bernoulli" in p for p in textes(entree, ou)), entree)


class TestRacineCarreeParfaite(unittest.TestCase):
    """√(x²) = |x| (et √(u²) = |u|) en une valeur : on lit le signe de u de chaque côté, sans repli, sans « 0/0 » répété."""

    def test_x_sur_racine_de_x_carre_en_zero(self):
        t = textes("x/sqrt(x^2)", r"x \to 0")
        self.assertFalse(any(REPLI[1:] in p for p in t), t)
        self.assertEqual(sum(1 for p in t if "forme indéterminée" in p), 1)       # pas de « 0/0 » après √(x²) = −x
        gauche = t[t.index("À gauche :") + 1]
        droite = t[t.index("À droite :") + 1]
        self.assertIn(r"\lim_{x\to 0^{-}} f(x) &= \lim_{x\to 0^{-}} \frac{x}{|x|}", gauche)
        self.assertIn(r"\lim_{x\to 0^{-}} \frac{x}{-x}", gauche)
        self.assertIn(r"x < 0 \text{ à gauche de } 0 \text{, donc } |x| = -x", gauche)
        self.assertIn(r"\lim_{x\to 0^{-}} -1 = -1", gauche)
        self.assertIn(r"x > 0 \text{ à droite de } 0 \text{, donc } |x| = x", droite)
        self.assertIn(r"\lim_{x\to 0^{+}} 1 = 1", droite)
        self.assertIn("f n'a pas de limite en", " ".join(t))

    def test_racine_d_un_carre_decale(self):         # √((x − 1)²) = |x − 1|
        t = " ".join(textes("(x-1)/sqrt(x^2-2x+1)", r"x \to 1"))
        self.assertIn(r"x - 1 < 0 \text{ à gauche de } 1 \text{, donc } |x - 1| = -\left(x - 1\right)", t)
        self.assertIn(r"x - 1 > 0 \text{ à droite de } 1 \text{, donc } |x - 1| = x - 1", t)


class TestConjuguee(unittest.TestCase):
    """L4 : expression conjuguée — ∞ − ∞ avec une racine en ±∞, 0/0 avec une racine en une valeur (LA-20)."""

    def test_racine_moins_x_en_plus_l_infini(self):
        t = textes("sqrt(x^2+x)-x", r"x \to +\infty")
        ch = chaine("sqrt(x^2+x)-x", r"x \to +\infty")
        self.assertEqual(sum(1 for p in t if p.startswith(r"\[")), 1)         # une seule chaîne : la conjuguée puis la mise en évidence
        for morceau in [
            r"\text{on multiplie et on divise par la conjuguée } \sqrt{x^{2} + x} + x",
            r"(a - b)(a + b) = a^{2} - b^{2}",
            r"\dfrac{\left(x^{2} + x\right) - x^{2}}{\sqrt{x^{2} + x} + x}",
            r"\lim_{x\to +\infty} \frac{x}{\sqrt{x^{2} + x} + x}",
            r"\left(x > 0 \text{ donc } |x| = x\right)",
            r"= \lim_{x\to +\infty} \frac{1}{\sqrt{1 + \frac{1}{x}} + 1} = \dfrac{1}{\sqrt{1} + 1} = \frac{1}{2}",
        ]:
            self.assertIn(morceau, ch)
        self.assertTrue(any("forme indéterminée « \\(\\infty - \\infty\\) »" in p for p in t))
        self.assertTrue(any("forme indéterminée « \\(\\infty/\\infty\\) »" in p for p in t))
        self.assertEqual(t[-1], r"Asymptote horizontale d'équation \(y = \frac{1}{2}\).")

    def test_racine_moins_x_en_moins_l_infini_pas_de_forme_indeterminee(self):
        t = textes("sqrt(x^2+x)-x", r"x \to -\infty")
        t = t[:next(i for i, p in enumerate(t) if p.startswith("On cherche une asymptote oblique"))]   # la limite de f seule
        self.assertFalse(any("conjuguée" in p for p in t), t)
        self.assertIn(r"\(\sqrt{x^{2} + x} \to +\infty\) et \(x \to -\infty\), donc "
                      r"\(\displaystyle\lim_{x\to -\infty} f(x) = +\infty\).", t)

    def test_ordonnee_a_l_origine_d_une_asymptote_oblique(self):   # b = lim (f(x) − ax)
        plus = chaine("sqrt(x^2-4x+5)-x", r"x \to +\infty")
        self.assertIn(r"-\frac{4\left(1 - \frac{5}{4x}\right)}{\sqrt{1 - \frac{4}{x} + \frac{5}{x^{2}}} + 1} = -\left(\dfrac{4 \cdot 1}{\sqrt{1} + 1}\right) = -2", plus)
        moins = chaine("sqrt(x^2-4x+5)+x", r"x \to -\infty")
        self.assertIn("conjuguée", moins)
        self.assertIn(r"x < 0 \text{ donc } |x| = -x", moins)
        self.assertIn("= 2", moins)

    def test_zero_sur_zero_conjuguee_du_numerateur(self):
        t = textes("(sqrt(x+3)-2)/(x-1)", r"x \to 1")
        self.assertEqual(t[:2], [
            r"\(x = 1\) est une valeur interdite.",
            r"Le numérateur \(\sqrt{x + 3} - 2\) tend vers \(0\) et le dénominateur \(x - 1\) tend vers \(0\) : "
            r"forme indéterminée « \(0/0\) ».",
        ])
        ch = t[2]
        for morceau in [
            r"\lim_{x\to 1} f(x) &= \lim_{x\to 1} \dfrac{\left(\sqrt{x + 3} - 2\right)\left(\sqrt{x + 3} + 2\right)}"
            r"{\left(x - 1\right)\,\left(\sqrt{x + 3} + 2\right)}",
            r"\text{on multiplie par la conjuguée } \sqrt{x + 3} + 2 \text{ du numérateur}",
            r"\dfrac{\left(x + 3\right) - 2^{2}}{\left(x - 1\right)\,\left(\sqrt{x + 3} + 2\right)}",
            r"\dfrac{x - 1}{\left(x - 1\right)\,\left(\sqrt{x + 3} + 2\right)}",
            r"\text{on factorise par } \left(x-1\right)",
            r"= \lim_{x\to 1} \frac{1}{\sqrt{x + 3} + 2} = \frac{1}{\sqrt{1 + 3} + 2} = \frac{1}{4}",
        ]:
            self.assertIn(morceau, ch)
        self.assertEqual(sum(1 for p in t if p.startswith(r"\[")), 1)         # les deux côtés donnent la même chaîne : une seule

    def test_zero_sur_zero_conjuguee_du_denominateur(self):
        ch = chaine("(x-1)/(sqrt(x+3)-2)", r"x \to 1")
        self.assertIn(r"\text{on multiplie par la conjuguée } \sqrt{x + 3} + 2 \text{ du dénominateur}", ch)
        self.assertIn("= 4", ch)

    def test_jamais_sans_racine(self):
        for entree in ["x^3-3x", "(x^2-1)/(x-1)", "x^2-4x", "e^x-1"]:
            for etude in la.etudier(entree)["etudes"]:
                self.assertFalse(any("conjuguée" in e["html"] for e in etude["etapes"]), (entree, etude["ou"]))

    def test_garde_fou(self):
        with mock.patch.object(la, "_carre_poly", side_effect=lambda n: [la.F(1), la.F(1)]):
            t = etapes("sqrt(x^2+x)-x", r"x \to +\infty")
        self.assertTrue(any(REPLI[1:] in e["html"] for e in t))
        self.assertFalse(any("conjuguée" in e["html"] for e in t))


class TestCroissanceComparee(unittest.TestCase):
    """L6 / T09 (Q1) : la croissance comparée n'est citée que devant une forme indéterminée, avec la limite de
    référence nommée ; mise en évidence de l'exponentielle (LA-07)."""

    def test_x2_exp_moins_x(self):
        t = textes("x^2*e^(-x)", r"x \to +\infty")
        i = next(i for i, p in enumerate(t) if "forme indéterminée" in p)
        self.assertEqual(t[i], r"\(x^{2} \to +\infty\) et \(e^{-x} \to 0^{+}\) : forme indéterminée « \(0 \cdot \infty\) ».")
        self.assertEqual(t[i + 1], r"\[\begin{aligned}\lim_{x\to +\infty} f(x) = 0 \qquad \left(x^{2}\,e^{-x} \to 0 "
                                   r"\text{ : croissance comparée, } \lim_{x\to +\infty} x^{n}e^{-ax} = 0 \text{ pour } "
                                   r"a > 0 \text{ et } n > 0\right)\end{aligned}\]")
        self.assertEqual(t[i + 2], r"Asymptote horizontale d'équation \(y = 0\).")

    def test_liste_de_la_specification(self):
        cas = [("x^2*e^(-x)", r"x \to +\infty", "x^{n}e^{-ax} = 0"), ("x^(1/2)*e^(-x)", r"x \to +\infty", "x^{n}e^{-ax} = 0"),
               ("ln(x)/x", r"x \to +\infty", r"\dfrac{\ln x}{x^{n}} = 0"), ("x*ln(x)", r"x \to 0^+", r"x^{n}\ln x = 0"),
               ("e^x-x^2", r"x \to +\infty", "x^{n}e^{-ax} = 0"), ("x-ln(x)", r"x \to +\infty", r"\dfrac{\ln x}{x^{n}} = 0"),
               ("x*e^x", r"x \to -\infty", "x^{n}e^{ax} = 0"), ("e^x/x", r"x \to +\infty", r"\dfrac{e^{ax}}{x^{n}} = +\infty"),
               ("e^(2x)/x^3", r"x \to +\infty", r"\dfrac{e^{ax}}{x^{n}} = +\infty")]
        for entree, ou, reference in cas:
            with self.subTest(f=entree):
                t = " ".join(textes(entree, ou))
                self.assertIn("croissance comparée", t)
                self.assertIn(reference, t)
                self.assertIn("forme indéterminée", t)

    def test_jamais_hors_forme_indeterminee(self):
        for entree, ou in [("x*e^x", r"x \to +\infty"), ("e^x/x", r"x \to 0"), ("e^(2x)", r"x \to +\infty"),
                           ("e^(2x)", r"x \to -\infty"), ("x^2*e^(-x)", r"x \to -\infty"), ("ln(x)/x", r"x \to 0^+")]:
            with self.subTest(f=entree, ou=ou):
                self.assertFalse(any("croissance comparée" in p for p in textes(entree, ou)))

    def test_toute_mention_suit_une_forme_indeterminee(self):
        for entree, ou, t in TestStyle().tous_les_textes():
            for i, p in enumerate(t):
                if "croissance comparée" in p:
                    with self.subTest(f=entree, ou=ou):
                        self.assertTrue(any("forme indéterminée" in q for q in t[:i + 1]), t)

    def test_mise_en_evidence_de_l_exponentielle(self):
        ch = chaine("e^x-x^2", r"x \to +\infty")
        self.assertIn(r"\lim_{x\to +\infty} f(x) &= \lim_{x\to +\infty} e^{x}\,\left(1 - x^{2}\,e^{-x}\right) = "
                      r"\left(+\infty\right) \cdot 1 = +\infty", ch)
        self.assertIn(r"\text{on met } e^{x} \text{ en évidence}", ch)
        self.assertIn(r"x^{2}\,e^{-x} \to 0", ch)
        ch = chaine("(e^x+1)/(e^x-1)", r"x \to +\infty")
        self.assertIn(r"e^{x} + 1 = e^{x}\,\left(1 + e^{-x}\right) ,\; e^{x} - 1 = e^{x}\,\left(1 - e^{-x}\right)", ch)
        self.assertIn(r"\frac{1 + e^{-x}}{1 - e^{-x}} = \dfrac{1}{1} = 1", ch)

    def test_polynome_devant_l_exponentielle(self):
        ch = chaine("e^(-x)*(x+1)", r"x \to +\infty")
        self.assertIn(r"x + 1 = x\left(1 + \dfrac{1}{x}\right)", ch)
        self.assertIn(r"\lim_{x\to +\infty} x\,e^{-x}\,\left(1 + \frac{1}{x}\right) = 0 \cdot 1 = 0", ch)

    def test_garde_fou(self):
        with mock.patch.object(la, "_reference", return_value=("puissance_exp_neg", la.Lim.infini(1))):
            t = etapes("x^2*e^(-x)", r"x \to +\infty")
        self.assertTrue(any(REPLI[1:] in e["html"] for e in t))


class TestLHopital(unittest.TestCase):
    """L7 : règle de Bernoulli-L'Hôpital en dernier recours, quatre hypothèses vérifiées ET écrites (LA-15, LA-16)."""

    def test_exponentielle_moins_1_sur_x_en_0(self):
        t = textes("(e^x-1)/x", r"x \to 0")
        i = next(i for i, p in enumerate(t) if p.startswith("On applique la règle"))
        self.assertEqual(t[i:i + 9], [
            r"On applique la règle de Bernoulli-L'Hôpital avec \(f(x) = e^{x} - 1\) et \(g(x) = x\). Vérifions les hypothèses :",
            r"(a) forme indéterminée « \(0/0\) » : vérifiée ;",
            r"(b) \(f\) et \(g\) sont dérivables sur \(\mathbb{R}\), donc au voisinage de \(0\) (sauf peut-être en \(0\)) : vérifiée ;",
            r"On calcule \(f'(x) = e^{x}\) et \(g'(x) = 1\).",
            r"(c) \(g'(x) = 1 \neq 0\) au voisinage de \(0\) (sauf peut-être en \(0\)) : vérifiée ;",
            r"(d) Calculons la limite de \(\dfrac{f'(x)}{g'(x)}\) :",
            r"\[\begin{aligned}\lim_{x\to 0} \dfrac{f'(x)}{g'(x)} &= \lim_{x\to 0} e^{x} = e^{0} = 1\end{aligned}\]",
            r"La limite de \(\dfrac{f'(x)}{g'(x)}\) existe et vaut \(1\) : (d) est vérifiée, donc la règle s'applique :",
            r"\[\begin{aligned}\lim_{x\to 0} f(x) &= \lim_{x\to 0} \dfrac{f'(x)}{g'(x)} = 1 \qquad "
            r"\left(\text{règle de Bernoulli-L'Hôpital}\right)\end{aligned}\]",
        ])
        self.assertIn("trou dans le graphique en \\((0\\,;\\,1)\\)", t[i + 9])

    def test_logarithme_sur_x_moins_1_en_1(self):
        t = " ".join(textes("ln(x)/(x-1)", r"x \to 1"))
        self.assertIn(r"(b) \(f\) et \(g\) sont dérivables sur \(\left]0 \,;\, +\infty\right[\)", t)
        self.assertIn(r"On calcule \(f'(x) = \frac{1}{x}\) et \(g'(x) = 1\).", t)
        self.assertIn(r"\lim_{x\to 1} \dfrac{f'(x)}{g'(x)} &= \lim_{x\to 1} \frac{1}{x} = \frac{1}{1} = 1", t)

    def test_ln_de_trinome_sur_affine_ne_passe_plus_par_la_regle(self):     # retouche 2 : mise en évidence de ln, avant L'Hôpital
        for ou in (r"x \to +\infty", r"x \to -\infty"):
            self.assertFalse(any("Bernoulli" in p for p in textes("ln(x^2-4x)/(x-5)", ou)), ou)

    def test_produit_mis_en_quotient(self):
        t = " ".join(textes("x*ln(x^2)", r"x \to 0"))
        self.assertIn(r"On écrit \(x\,\ln\left(x^{2}\right) = \dfrac{\ln\left(x^{2}\right)}{\frac{1}{x}}\) pour obtenir un quotient.", t)
        self.assertIn(r"(b) \(f\) et \(g\) sont dérivables sur", t)
        self.assertIn(r"\lim_{x\to 0} -2x = -2 \cdot 0 = 0", t)

    def test_une_seconde_forme_se_traite_par_croissance_comparee(self):
        t = textes("ln(x)^2/x", r"x \to +\infty")
        self.assertIn(r"\lim_{x\to +\infty} \dfrac{f'(x)}{g'(x)} &= \lim_{x\to +\infty} \frac{2\ln(x)}{x}", " ".join(t))
        self.assertTrue(any("croissance comparée" in p for p in t))
        self.assertEqual(sum(1 for p in t if "croissance comparée" in p), 1)

    def test_jamais_hors_forme_indeterminee(self):
        for entree, ou in [("(x+1)/x", r"x \to 0"), ("1/(x-2)", r"x \to 2"), ("e^x/x", r"x \to 0"), ("x*e^x", r"x \to +\infty"),
                           ("ln(x)/(x-1)", r"x \to 0^+")]:
            with self.subTest(f=entree, ou=ou):
                self.assertFalse(any("Bernoulli" in p for p in textes(entree, ou)))

    def test_jamais_pour_une_fraction_rationnelle_ni_une_limite_de_reference(self):    # LA-15
        for entree in ["(x^2-1)/(x-1)", "(x^2-4)/(x^2-4x+4)", "(2x^2+3x)/(x^2+1)", "x^2/(x-1)", "e^((x^2-1)/(x-1))"]:
            for etude in la.etudier(entree)["etudes"]:
                self.assertFalse(any("Bernoulli" in e["html"] for e in etude["etapes"]), (entree, etude["ou"]))
        for entree, ou in [("x^2*e^(-x)", r"x \to +\infty"), ("ln(x)/x", r"x \to +\infty"), ("x*ln(x)", r"x \to 0^+"),
                           ("e^x-x^2", r"x \to +\infty"), ("x*e^x", r"x \to -\infty"), ("x-ln(x)", r"x \to +\infty")]:
            self.assertFalse(any("Bernoulli" in p for p in textes(entree, ou)), entree)

    def test_non_appliquee_si_g_prime_n_est_pas_non_nul(self):
        with mock.patch.object(la, "_g_prime_non_nul", return_value=None):
            t = textes("(e^x-1)/x", r"x \to 0")
        self.assertFalse(any("Bernoulli" in p for p in t))
        self.assertTrue(any(REPLI[1:] in p for p in t))

    def test_non_appliquee_si_la_limite_du_quotient_des_derivees_n_est_pas_obtenue(self):
        reel = la._noeud

        def sans_derivees(n, ctx):
            if ctx.nb_lhopital:
                raise la.Abandon("limite de f'/g' non obtenue")
            return reel(n, ctx)

        with mock.patch.object(la, "_noeud", side_effect=sans_derivees):
            t = textes("(e^x-1)/x", r"x \to 0")
        self.assertFalse(any("Bernoulli" in p for p in t))
        self.assertTrue(any(REPLI[1:] in p for p in t))

    def test_boucle_sur_une_forme_indeterminee_donne_le_repli(self):
        """x/√(x²) en 0, sans la lecture de √(x²) = |x| : f'/g' retombe sur une forme 0/0 ; après deux applications
        on ne conclut pas par la règle."""
        sans_abs = [m for m in la.METHODES if m is not la._racine_carre_parfait]
        with mock.patch.object(la, "METHODES", sans_abs):
            t = textes("x/sqrt(x^2)", r"x \to 0")
        self.assertFalse(any("Bernoulli" in p for p in t), t)
        self.assertTrue(any(REPLI[1:] in p for p in t))

    def test_au_plus_deux_applications_de_suite(self):
        for entree in ["(e^x-1)/x", "ln(x)/(x-1)", "x*ln(x^2)", "ln(x)^2/x", "x*e^(1/x)"]:
            for etude in la.etudier(entree)["etudes"]:
                with self.subTest(f=entree, ou=etude["ou"]):
                    self.assertLessEqual(sum(1 for e in etude["etapes"] if e["html"].startswith("On applique la règle")), 2)

    def test_garde_fou(self):
        with mock.patch.object(la, "_arbre_propre", side_effect=lambda t: la.Nb(la.F(7))):
            t = textes("(e^x-1)/x", r"x \to 0")
        self.assertTrue(any(REPLI[1:] in p for p in t))
        self.assertFalse(any("Bernoulli" in p for p in t))


class TestOblique(unittest.TestCase):
    """L8 : asymptote oblique — division euclidienne (sans « + 0 » ni « + - ») pour une fraction rationnelle ;
    a = lim f(x)/x puis b = lim (f(x) − ax), chaque limite en chaîne d'égalités, sinon ; position relative (LA-17)."""

    def apres(self, entree, ou):
        t = textes(entree, ou)
        return t[next(i for i, p in enumerate(t) if p.startswith("On cherche une asymptote oblique")):]

    def test_division_euclidienne_x2_moins_1_sur_x_moins_3(self):
        t = textes("(x^2-1)/(x-3)", r"x \to +\infty")
        self.assertIn(r"\[x^{2} - 1 = \left(x - 3\right)\,\left(x + 3\right) + 8\]", t)
        self.assertIn(r"Donc \(f(x) = x + 3 + \dfrac{8}{x - 3}\), d'où :", t)
        reste = next(p for p in t if p.startswith(r"\[\begin{aligned}\lim_{x\to +\infty} \left(f(x) - "))
        self.assertIn(r"&= \lim_{x\to +\infty} \dfrac{8}{x - 3} = 0", reste)
        self.assertIn(r"Asymptote oblique d'équation \(y = x + 3\).", t)
        self.assertIn("la courbe est au-dessus de la droite", t[-1])
        self.assertIn("la courbe est au-dessous de la droite", textes("(x^2-1)/(x-3)", r"x \to -\infty")[-1])

    def test_jamais_plus_zero_ni_plus_moins(self):
        for entree in ["(x^2-1)/(x-3)", "(x^3+1)/(x^2+1)", "(x^2-4x+3)/(x-1)", "(x^2+1)/(1-x)", "(2x^2+1)/(x-1)"]:
            for etude in la.etudier(entree)["etudes"]:
                for e in etude["etapes"]:
                    for mauvais in ("+ 0", "+ -", "+ −", " + \\dfrac{-", " + \\left(-"):
                        self.assertNotIn(mauvais, e["html"], (entree, etude["ou"]))

    def test_reste_negatif_et_division_exacte(self):
        t = textes("(x^3+1)/(x^2+1)", r"x \to +\infty")
        self.assertIn(r"\[x^{3} + 1 = \left(x^{2} + 1\right)\,x - x + 1\]", t)
        self.assertIn(r"Donc \(f(x) = x - \dfrac{x - 1}{x^{2} + 1}\), d'où :", t)
        t = textes("(x^2-4x+3)/(x-1)", r"x \to +\infty")
        self.assertIn(r"\[x^{2} - 4x + 3 = \left(x - 1\right)\,\left(x - 3\right)\]", t)
        self.assertTrue(any("la courbe est contenue dans la droite" in p for p in t))

    def test_racine_a_puis_b_en_plus_et_moins_l_infini(self):        # LA-20
        for ou, a, b in [(r"x \to +\infty", "1", "-2"), (r"x \to -\infty", "-1", "2")]:
            suite = self.apres("sqrt(x^2-4x+5)", ou)
            chaine_a = next(p for p in suite if p.startswith(r"\[") and r"\dfrac{f(x)}{x}" in p)
            chaine_b = next(p for p in suite if p.startswith(r"\[") and r"\left(f(x) " in p)
            self.assertIn(f"= {a} \\qquad", chaine_a)
            self.assertIn(f"= {b} \\qquad", chaine_b)
            if ou.endswith(r"-\infty"):
                self.assertIn(r"x < 0 \text{ donc } |x| = -x", chaine_a)
            self.assertTrue(any("sont finis (et \\(a \\neq 0\\)) : asymptote oblique" in p for p in suite))
            self.assertIn("la courbe est au-dessus de la droite", suite[-1])

    def test_racine_moins_x_en_moins_l_infini(self):
        suite = " ".join(self.apres("sqrt(x^2+x)-x", r"x \to -\infty"))
        self.assertIn("= - \\frac{1}{2}", suite)
        self.assertIn(r"y = -2x - \frac{1}{2}", suite)
        self.assertIn("la courbe est au-dessous de la droite", suite)
        self.assertNotIn(REPLI[1:], suite)

    def test_pas_de_position_quand_le_signe_ne_se_lit_pas(self):
        for etude in la.etudier("e^x-x^2")["etudes"]:
            self.assertFalse(any("Position relative" in e["html"] for e in etude["etapes"]))


class TestFormeIndeterminee(unittest.TestCase):
    """Sans méthode pour la lever (L1), la rédaction est abandonnée : phrase de repli, jamais d'étape fausse."""

    def test_repli_mot_pour_mot_et_detail_en_console(self):
        with mock.patch.object(la, "METHODES", []):          # aucune méthode du cours : la forme n'est pas levée
            etape = etapes("x*e^x", r"x \to -\infty")[0]
        self.assertEqual(etape["html"], REPLI + r"\(\displaystyle\lim_{x\to -\infty} f(x) = 0\).")
        self.assertIn("0 · ∞", etape["detail"])

    def test_repli_garde_la_conclusion(self):
        with mock.patch.object(la, "METHODES", []):
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
                if p.startswith("Le numérateur") and "tend vers \\(0\\)" in p and "forme indéterminée" not in p:
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
