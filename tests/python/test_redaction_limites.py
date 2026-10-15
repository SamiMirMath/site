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
            r"Signe de \(x - 1\) : positif pour \(x > 1\).",
            r"Or \(\ln t \to -\infty\) quand \(t \to 0^{+}\) et \(x - 1 \to 0^{+}\), "
            r"donc \(\displaystyle\lim_{x\to 1^{+}} f(x) = -\infty\).",
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
            r"Signe de \(x\) : négatif pour \(x < 0\), positif pour \(x > 0\).",
            r"À gauche : \(x \to 0^{-}\), donc \(\frac{1}{x} \to \dfrac{1}{0^{-}} = -\infty\).",
            r"Or \(e^{t} \to 0^{+}\) quand \(t \to -\infty\), donc \(f(x) \to 0\).",
            r"À droite : \(x \to 0^{+}\), donc \(\frac{1}{x} \to \dfrac{1}{0^{+}} = +\infty\).",
            r"Or \(e^{t} \to +\infty\) quand \(t \to +\infty\), donc \(f(x) \to +\infty\).",
            r"Au moins une des deux limites est infinie : asymptote verticale d'équation \(x = 0\).",
        ])

    def test_quotient_dont_le_denominateur_tend_vers_zero(self):
        self.assertEqual(textes("ln(x^2-4x)/(x-5)", r"x \to 5"), [
            r"\(x = 5\) est une valeur interdite.",
            r"Le numérateur \(\ln\left(x^{2} - 4x\right)\) vaut "
            r"\(\ln\left(5^{2} - 4 \cdot 5\right) = \ln{\left(5 \right)}\) et le dénominateur \(x - 5\) tend vers \(0\).",
            r"Signe de \(x - 5\) : négatif pour \(x < 5\), positif pour \(x > 5\).",
            r"À gauche : \(x - 5 \to 0^{-}\), donc \(f(x) \to \dfrac{\ln{\left(5 \right)}}{0^{-}} = -\infty\).",
            r"À droite : \(x - 5 \to 0^{+}\), donc \(f(x) \to \dfrac{\ln{\left(5 \right)}}{0^{+}} = +\infty\).",
            r"Au moins une des deux limites est infinie : asymptote verticale d'équation \(x = 5\).",
        ])

    def test_une_sous_expression_n_est_commentee_qu_une_fois(self):
        t = textes("(e^x+1)/(e^x-1)", r"x \to -\infty")
        self.assertEqual(sum(1 for p in t if p.startswith(r"Or \(e^{t}")), 1)
        self.assertIn(r"\(e^{x} + 1 \to 1\) et \(e^{x} - 1 \to -1\), donc \(\displaystyle\lim_{x\to -\infty} f(x) = -1\).", t)


class TestValeursInterdites(unittest.TestCase):
    """Valeur interdite sans forme indéterminée : la partie commune une seule fois (valeur interdite,
    numérateur, signe du dénominateur), puis une ligne par côté (LA-14, LA-18, règles de style 2 et 3)."""

    def test_modele_de_l_enseignant(self):
        self.assertEqual(textes("1/(x^2-2)", r"x \to \sqrt{2}"), [
            r"\(x = \sqrt{2}\) est une valeur interdite.",
            r"Le numérateur vaut \(1\) et le dénominateur \(x^{2} - 2\) tend vers \(0\).",
            r"Signe de \(x^{2} - 2\) (trinôme, racines \(- \sqrt{2}\) et \(\sqrt{2}\)) : "
            r"négatif entre \(- \sqrt{2}\) et \(\sqrt{2}\), positif pour \(x > \sqrt{2}\).",
            r"À gauche : \(x^{2} - 2 \to 0^{-}\), donc \(f(x) \to \dfrac{1}{0^{-}} = -\infty\).",
            r"À droite : \(x^{2} - 2 \to 0^{+}\), donc \(f(x) \to \dfrac{1}{0^{+}} = +\infty\).",
            r"Asymptote verticale d'équation \(x = \sqrt{2}\).",
        ])
        t = textes("1/(x^2-2)", r"x \to -\sqrt{2}")
        self.assertEqual(t[2], r"Signe de \(x^{2} - 2\) (trinôme, racines \(- \sqrt{2}\) et \(\sqrt{2}\)) : "
                               r"positif pour \(x < - \sqrt{2}\), négatif entre \(- \sqrt{2}\) et \(\sqrt{2}\).")
        self.assertEqual(t[3], r"À gauche : \(x^{2} - 2 \to 0^{+}\), donc \(f(x) \to \dfrac{1}{0^{+}} = +\infty\).")
        self.assertEqual(t[4], r"À droite : \(x^{2} - 2 \to 0^{-}\), donc \(f(x) \to \dfrac{1}{0^{-}} = -\infty\).")

    def test_fraction_rationnelle(self):
        self.assertEqual(textes("(x^2-1)/(x-3)", r"x \to 3"), [
            r"\(x = 3\) est une valeur interdite.",
            r"Le numérateur \(x^{2} - 1\) vaut \(3^{2} - 1 = 8\) et le dénominateur \(x - 3\) tend vers \(0\).",
            r"Signe de \(x - 3\) : négatif pour \(x < 3\), positif pour \(x > 3\).",
            r"À gauche : \(x - 3 \to 0^{-}\), donc \(f(x) \to \dfrac{8}{0^{-}} = -\infty\).",
            r"À droite : \(x - 3 \to 0^{+}\), donc \(f(x) \to \dfrac{8}{0^{+}} = +\infty\).",
            r"Asymptote verticale d'équation \(x = 3\).",
        ])

    def test_denominateur_oppose(self):
        t = textes("5/(3-x)", r"x \to 3")
        self.assertEqual(t[1], r"Le numérateur vaut \(5\) et le dénominateur \(3 - x\) tend vers \(0\).")
        self.assertEqual(t[2], r"Signe de \(3 - x = -\left(x - 3\right)\) : positif pour \(x < 3\), négatif pour \(x > 3\).")
        self.assertEqual(t[3], r"À gauche : \(3 - x \to 0^{+}\), donc \(f(x) \to \dfrac{5}{0^{+}} = +\infty\).")

    def test_meme_limite_des_deux_cotes_une_seule_conclusion(self):
        self.assertEqual(textes("1/(x-1)^2", r"x \to 1"), [
            r"\(x = 1\) est une valeur interdite.",
            r"Le numérateur vaut \(1\) et le dénominateur \(\left(x - 1\right)^{2}\) tend vers \(0\).",
            r"Signe de \(\left(x - 1\right)^{2}\) : positif pour \(x \neq 1\), car une puissance paire est positive.",
            r"\(\left(x - 1\right)^{2} \to 0^{+}\), donc \(f(x) \to \dfrac{1}{0^{+}} = +\infty\).",
            r"Asymptote verticale d'équation \(x = 1\).",
        ])

    def test_denominateur_factorise_pour_connaitre_son_signe(self):
        t = textes("(x^2-3)/(x^3-3x)", r"x \to 0")
        self.assertEqual(t[1], r"Le numérateur \(x^{2} - 3\) vaut \(0^{2} - 3 = -3\) et le dénominateur "
                               r"\(x^{3} - 3x\) tend vers \(0\).")
        self.assertEqual(t[2], r"Signe de \(x^{3} - 3x = x\,\left(x^{2} - 3\right)\) : près de \(0\), "
                               r"\(x^{2} - 3\) est négatif (il vaut \(-3\)), donc \(x^{3} - 3x\) est positif pour "
                               r"\(x < 0\), négatif pour \(x > 0\).")
        self.assertEqual(t[3], r"À gauche : \(x^{3} - 3x \to 0^{+}\), donc \(f(x) \to \dfrac{-3}{0^{+}} = -\infty\).")

    def test_signe_par_la_monotonie(self):
        t = textes("(e^x+1)/(e^x-1)", r"x \to 0")
        self.assertEqual(t[1], r"Le numérateur \(e^{x} + 1\) vaut \(e^{0} + 1 = 2\) et le dénominateur "
                               r"\(e^{x} - 1\) tend vers \(0\).")
        self.assertEqual(t[2], r"Signe de \(e^{x} - 1\) : \(e^{x}\) est croissante et vaut \(1\) en \(x = 0\), "
                               r"donc \(e^{x} - 1\) est négatif pour \(x < 0\), positif pour \(x > 0\).")

    def test_zero_de_signe_connu_en_un_point_irrationnel(self):
        t = textes("ln(x^2-3)", r"x \to \sqrt{3}^+")
        self.assertEqual(t[1], r"Signe de \(x^{2} - 3\) (trinôme, racines \(- \sqrt{3}\) et \(\sqrt{3}\)) : "
                               r"positif pour \(x > \sqrt{3}\).")

    def test_zero_de_signe_inconnu_donne_le_repli(self):
        """Pas de factorisation possible au point irrationnel d'un polynôme de degré 3 : le signe n'est pas inventé."""
        etape = etapes("ln(x^3-3x)", r"x \to \sqrt{3}^+")[1]
        self.assertEqual(etape["html"], REPLI + r"\(\displaystyle\lim_{x\to {\sqrt{3}}^{+}} f(x) = -\infty\).")
        self.assertIn("signe inconnu", etape["detail"])

    def test_factorisation_dans_un_logarithme(self):
        t = textes("ln(x^2-4x)/(x-5)", r"x \to 4^+")
        self.assertEqual(t[1], r"Signe de \(x^{2} - 4x = x\,\left(x - 4\right)\) : près de \(4\), \(x\) est positif "
                               r"(il vaut \(4\)), donc \(x^{2} - 4x\) est positif pour \(x > 4\).")
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
                    self.assertEqual(sum(1 for p in t if p.startswith("Le numérateur")), 1)
                    self.assertEqual(sum(1 for p in t if p.startswith("Signe de")), 1)
                    self.assertTrue(t[-1].startswith("Asymptote verticale d'équation"), t[-1])

    def test_garde_fou_sur_un_pole_rationnel(self):
        with mock.patch.object(la, "_noeud", side_effect=la.Abandon("essai")):
            avec = la.etudier("1/(x-2)")
        normal = la.etudier("1/(x-2)")
        self.assertEqual(avec["asymptotes"], normal["asymptotes"])
        t = [e["html"] for e in next(e for e in avec["etudes"] if e["ou"] == r"x \to 2")["etapes"]]
        self.assertEqual(sum(1 for p in t if REPLI[1:] in p), 2)       # un repli par côté (limites différentes)
        self.assertTrue(t[1].startswith("À gauche : ") and t[2].startswith("À droite : "), t)


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
        self.assertIn(r"Signe de \(x - 2\) : négatif pour \(x < 2\), positif pour \(x > 2\).", t)
        self.assertIn(r"À gauche : \(x - 2 \to 0^{-}\), donc \(f(x) \to \dfrac{4}{0^{-}} = -\infty\).", t)
        self.assertEqual(t[-1], r"Asymptote verticale d'équation \(x = 2\).")

    def test_aucune_forme_zero_sur_zero_sans_facteur_commun(self):
        for entree in ["1/(x-2)", "(x^2-1)/(x-3)", "1/x^2"]:
            for etude in la.etudier(entree)["etudes"]:
                self.assertFalse(any("0/0" in e["html"] for e in etude["etapes"]), (entree, etude["ou"]))


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
                  r"le produit tend vers", r"le quotient tend vers \\\(", r"Par substitution"]
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
                if "tend vers \\(0\\)." in p and p.startswith("Le numérateur"):
                    with self.subTest(f=entree, ou=ou):
                        self.assertTrue(t[i + 1].startswith("Signe de"), (t[i], t[i + 1]))
                if r"quand \(t \to 0^{+}\) et" in p:
                    with self.subTest(f=entree, ou=ou):
                        self.assertTrue(any(q.startswith("Signe de") for q in t[:i]), t)

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

    def test_une_phrase_ne_cite_que_le_vocabulaire_du_cours(self):       # LA-24
        for entree, ou, t in self.tous_les_textes():
            for phrase in t:
                for mot in ("SymPy", "sympy", "Abandon", "exception", "noeud", "arbre"):
                    self.assertNotIn(mot, phrase)


if __name__ == "__main__":
    unittest.main()
