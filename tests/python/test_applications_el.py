"""T33 (applications, étape 1) — Outil « Exponentielles et logarithmes » : lecture d'un problème d'application (EL-22) :
casse des lettres, noms indexés (C0, V_0), signe %, paramètre à simplifier et message à deux inconnues."""
import unittest
from fractions import Fraction as F

import moteurs  # noqa : met les moteurs dans sys.path
import exp_log as el
from exp_log import Nb, Var, Op, Pow, Neg, Eq
from noyau import ErreurSaisie

import resoudre_el as rel
import sortie as so
from cas_el import BATTERIE_APPLICATIONS
from test_exp_log import evaluer, vrai


def lire(s):
    g, d = el.lire_membres(s)
    return g if d is None else (g, d)


class TestCasseEtNoms(unittest.TestCase):
    def test_la_casse_des_lettres_est_gardee(self):
        self.assertEqual(lire("Q"), Var("Q"))
        self.assertNotEqual(lire("Q"), lire("q"))
        self.assertEqual(lire("3Q"), Op("*", Nb(3), Var("Q")))

    def test_les_noms_de_fonction_ignorent_la_casse(self):
        for s in ["LOG(x)", "Log(x)", "LN(x)", "SQRT(x)", "EXP(x)", "Log_2(x)", "LOG2(x)"]:
            with self.subTest(s):
                self.assertEqual(el.variables(lire(s)), {"x"})

    def test_la_base_d_un_logarithme_garde_sa_casse(self):
        self.assertEqual(el.variables(lire("log_Q(8)")), {"Q"})

    def test_un_nom_indexe_est_une_seule_lettre(self):
        for s, nom in [("C0", "C0"), ("V0", "V0"), ("C_0", "C0"), ("V_0", "V0"), ("c_0", "c0"), ("C_12", "C12"), ("x_1", "x1")]:
            with self.subTest(s):
                self.assertEqual(lire(s), Var(nom))
        self.assertEqual(lire("2C0"), Op("*", Nb(2), Var("C0")))
        self.assertEqual(lire("V0(1-t)"), Op("*", Var("V0"), Op("-", Nb(1), Var("t"))))

    def test_tex_d_un_nom_indexe(self):
        self.assertEqual(el.tex(Var("C0")), "C_{0}")
        self.assertEqual(el.tex(Var("C12")), "C_{12}")
        self.assertEqual(el.tex(Var("Q")), "Q")

    def test_un_nombre_apres_une_minuscule_reste_refuse(self):
        for s in ["x2=3", "2^x3=8"]:
            with self.subTest(s):
                with self.assertRaises(ErreurSaisie) as c:
                    el.lire_membres(s)
                self.assertIn("Un nombre ne peut pas suivre", str(c.exception))

    def test_e_reste_le_nombre_e_quelle_que_soit_la_casse(self):
        self.assertEqual(lire("E^x=2"), lire("e^x=2"))
        with self.assertRaises(ErreurSaisie) as c:
            el.analyser_saisie("E0=3")
        self.assertIn("Un nombre ne peut pas suivre", str(c.exception))


class TestPourcentage(unittest.TestCase):
    def test_un_pourcentage_est_un_nombre_sur_cent(self):
        for s, v in [("3,75%", F(375, 10000)), ("3,75 %", F(375, 10000)), ("3.75%", F(375, 10000)), ("5%", F(1, 20)), ("100 %", F(1)), ("0,5%", F(1, 200))]:
            with self.subTest(s):
                n = lire(s)
                self.assertIsInstance(n, Nb)
                self.assertEqual(n.val, v)

    def test_ecriture_decimale_et_tex(self):
        n = lire("3,75%")
        self.assertEqual((n.dec, n.pct), ("0,0375", "3,75"))
        self.assertEqual(el.tex(n), r"3{,}75\,\%")
        self.assertEqual(lire("100%").dec, "1")
        self.assertEqual(el.tex(lire("5 %")), r"5\,\%")
        self.assertEqual(el.tex(lire("1+3,75%")), r"1 + 3{,}75\,\%")

    def test_un_pourcentage_dans_une_base(self):
        g, d = lire("3=(1+3,75%)^x")
        self.assertEqual(g, Nb(3))
        self.assertIsInstance(d, Pow)
        self.assertEqual(d.a.b.val, F(3, 80))

    def test_le_pourcentage_se_place_apres_un_nombre(self):
        for s in ["%", "x%", "(1+2)%=3", "3%%", "2^x=%", "+%"]:
            with self.subTest(s):
                with self.assertRaises(ErreurSaisie) as c:
                    el.lire_membres(s)
                self.assertEqual(str(c.exception), el.MESSAGE_POURCENT)

    def test_l_apercu_accepte_le_pourcentage(self):
        r = el.apercu("3=(1+3,75%)^x")
        self.assertTrue(r["ok"])
        self.assertIn(r"3{,}75\,\%", r["tex"])


class TestParametre(unittest.TestCase):
    def test_l_inconnue_est_la_lettre_de_l_exposant(self):
        for s, inconnue, params in [
            ("3Q = Q(1+3,75/100)^x", "x", ("Q",)),
            ("2C = C(1+0,04)^n", "n", ("C",)),
            ("C0*1,05^n = 2*C0", "n", ("C0",)),
            ("C_0*1,05^n = 2C_0", "n", ("C0",)),
            ("V0/2 = V0(1-20/100)^n", "n", ("V0",)),
            ("V_0/2 = V_0(1-20/100)^n", "n", ("V0",)),
            ("Q = Q*0,8^n", "n", ("Q",)),
            ("2Q = 1,04^n*Q", "n", ("Q",)),
            ("Q*2^x = 3Q", "x", ("Q",)),
            ("-Q = -Q*2^x", "x", ("Q",)),
            ("5Q/2 = Q*(1+0,035)^t", "t", ("Q",)),
        ]:
            with self.subTest(s):
                r = el.analyser_saisie(s)
                self.assertEqual((r.genre, r.inconnue, r.parametres), ("equation", inconnue, params))

    def test_sans_parametre(self):
        for s in ["2000*1,045^n = 3805", "37e^(-0,02t) = 25", "3^(x+1)=27", "log_x(256)=4"]:
            with self.subTest(s):
                self.assertEqual(el.analyser_saisie(s).parametres, ())

    def test_un_parametre_qui_ne_se_simplifie_pas_donne_deux_inconnues(self):
        for s, message in [
            ("3Q = 1,04^x", "Cette équation contient deux inconnues : Q et x."),
            ("Q + 1 = Q*2^x", "Cette équation contient deux inconnues : Q et x."),
            ("Q*2^x = 3", "Cette équation contient deux inconnues : Q et x."),
            ("Q*(1+Q)^x = 2Q", "Cette équation contient deux inconnues : Q et x."),
            ("Q = r*1,04^n", "Cette équation contient trois inconnues : Q, r et n."),
            ("C0 = 1,05^n*Q", "Cette équation contient trois inconnues : C0, Q et n."),
        ]:
            with self.subTest(s):
                with self.assertRaises(ErreurSaisie) as c:
                    el.analyser_saisie(s)
                self.assertEqual(str(c.exception), message)

    def test_sans_lettre_en_exposant_le_message_d_avant_reste(self):
        for s in ["x+y=3", "2^(x+y)=8", "Q+q=3"]:
            with self.subTest(s):
                with self.assertRaises(ErreurSaisie) as c:
                    el.analyser_saisie(s)
                self.assertIn("Une seule inconnue : vous avez écrit", str(c.exception))

    def test_sans_facteur(self):
        Q = Var("Q")
        self.assertEqual(el.sans_facteur(Q, "Q"), Nb(1))
        self.assertEqual(el.sans_facteur(Op("*", Nb(3), Q), "Q"), Op("*", Nb(3), Nb(1)))
        self.assertEqual(el.sans_facteur(Op("/", Q, Nb(2)), "Q"), Op("/", Nb(1), Nb(2)))
        self.assertEqual(el.sans_facteur(Neg(Q), "Q"), Neg(Nb(1)))
        self.assertIsNone(el.sans_facteur(Op("+", Q, Nb(1)), "Q"))
        self.assertIsNone(el.sans_facteur(Op("/", Nb(2), Q), "Q"))
        self.assertIsNone(el.sans_facteur(Op("*", Q, Q), "Q"))
        self.assertIsNone(el.sans_facteur(Nb(3), "Q"))

    def test_pas_de_faux_corrige_tant_que_le_parametre_n_est_pas_simplifie(self):
        # étape 1 : la saisie est lue, la résolution vient à l'étape 3 ; jamais un corrigé qui traite Q comme une constante
        r = rel.resoudre("3Q = Q(1+3,75/100)^x")
        self.assertFalse(r["ok"])
        self.assertEqual(r["erreur"], el.MESSAGE_PAS_ENCORE)

    def test_l_apercu_d_un_probleme_d_application(self):
        r = el.apercu("3Q = Q(1+3,75/100)^x")
        self.assertTrue(r["ok"])
        self.assertEqual(r["tex"], r"3Q = Q \cdot \left(1 + \frac{3{,}75}{100}\right)^{x}")
        self.assertEqual(el.apercu("V0/2 = V0(1-20/100)^n")["tex"].count("V_{0}"), 2)


def titres(r):
    return [c["titre"] for c in r["etapes"]]


class TestBaseCalculee(unittest.TestCase):
    """EL-22 : une base écrite avec un taux devient un nombre, sur une ligne à part, dans les deux méthodes."""

    def prepare(self, saisie):
        s = el.analyser_saisie(saisie)
        return s, el.preparer_application(s.g, s.d, s.inconnue)

    def test_la_ligne_de_la_base(self):
        for saisie, ligne in [
            ("3=(1+3,75/100)^x", r"1 + \frac{3{,}75}{100} = 1{,}0375"),
            ("3=(1+3,75%)^x", r"1 + 3{,}75\,\% = 1{,}0375"),
            ("2=(1+0,04)^n", r"1 + 0{,}04 = 1{,}04"),
            ("0,5=(1-20/100)^n", r"1 - \frac{20}{100} = 0{,}8"),
            ("(1+0,035)^n=2", r"1 + 0{,}035 = 1{,}035"),
            ("2000*(1+4,5%)^n=3805", r"1 + 4{,}5\,\% = 1{,}045"),
        ]:
            with self.subTest(saisie):
                _, (g, d, cartes) = self.prepare(saisie)
                self.assertEqual([c["titre"] for c in cartes], ["Calculer la base"])
                self.assertEqual([el.tex_chaine(l) for l in cartes[0]["lignes"]], [ligne])

    def test_la_base_devient_un_decimal_ou_une_fraction(self):
        _, (g, d, _) = self.prepare("3=(1+3,75/100)^x")
        self.assertEqual((d.a.val, d.a.dec), (F(10375, 10000), "1,0375"))
        _, (g, d, _) = self.prepare("3=(1+0,1/3)^x")        # 31/30 ne s'arrête pas : une fraction
        self.assertEqual((d.a.val, d.a.dec), (F(31, 30), None))
        _, (g, d, _) = self.prepare("3=(1-20/100)^x")
        self.assertEqual((d.a.val, d.a.dec), (F(4, 5), "0,8"))

    def test_rien_a_calculer(self):
        for saisie in ["3^(x+1)=27", "(1/2)^x=8", "1,5^x=2,25", "2000*1,045^n=3805", "(1+1/3)^x=2", "(2+1)^x=9", "e^x=7", "log(5-x)=8",
                       "3=1^x", "(0,5+0,5)^x=2", "(1+0,04)=x+1", "2^(1+0,5)=x"]:
            with self.subTest(saisie):
                try:
                    s = el.analyser_saisie(saisie)
                except ErreurSaisie:
                    continue
                g, d, cartes = el.preparer_application(s.g, s.d, s.inconnue)
                self.assertEqual(cartes, [])
                self.assertEqual((g, d), (s.g, s.d))

    def test_une_seule_ligne_par_base(self):
        s = el.analyser_saisie("(1+0,04)^x=2*(1+0,04)^(2x)")
        _, _, cartes = el.preparer_application(s.g, s.d, s.inconnue)
        self.assertEqual(len(cartes[0]["lignes"]), 1)
        s = el.analyser_saisie("(1+0,04)^x=(1+5%)^x")
        _, _, cartes = el.preparer_application(s.g, s.d, s.inconnue)
        self.assertEqual(len(cartes[0]["lignes"]), 2)

    def test_les_deux_methodes_commencent_par_la_carte(self):
        for saisie in ["3=(1+3,75/100)^x", "2000*(1+0,045)^n=3805", "0,5=(1-20/100)^n", "3=(1+3,75%)^x"]:
            with self.subTest(saisie):
                s = el.analyser_saisie(saisie)
                variantes = el.variantes_equation(s.g, s.d, s.inconnue)
                self.assertEqual(set(variantes), set(el.METHODES))
                for m, r in variantes.items():
                    self.assertEqual(titres(r)[0], "Calculer la base", m)
                    self.assertEqual(titres(r).count("Calculer la base"), 1)
                    self.assertEqual(r["enonce"], Eq(s.g, s.d))

    def test_batterie_oracle_mpmath(self):
        """La solution, substituée dans l'équation de l'énoncé (écrite avec le taux), la vérifie ; le nombre de solutions est celui attendu."""
        for saisie, attendu in BATTERIE_APPLICATIONS:
            with self.subTest(saisie):
                s = el.analyser_saisie(saisie)
                for m in el.METHODES:
                    r = el.variantes_equation(s.g, s.d, s.inconnue)[m]
                    if r.get("message"):
                        continue
                    self.assertEqual(len(r["solutions"]), len(attendu), m)
                    for n, v in zip(r["solutions"], attendu):
                        self.assertAlmostEqual(float(evaluer(n)), v, places=3)
                        self.assertTrue(vrai(Eq(s.g, s.d), evaluer(n)), f"{saisie} : {m}")

    def test_sorties_valides_et_carte_numerotee(self):
        for saisie, _ in BATTERIE_APPLICATIONS:
            with self.subTest(saisie):
                sortie = rel.resoudre(saisie)
                self.assertEqual(so.valider(sortie), [])
                if saisie == "2=1,0375^x":                  # la base est déjà un nombre : pas de carte (entrée témoin)
                    self.assertNotIn("Calculer la base", [c.get("badge") for v in sortie["variantes"] for c in v["cartes"]])
                    continue
                for v in sortie["variantes"]:
                    premiere = v["cartes"][0]
                    self.assertEqual((premiere["titre"], premiere["badge"]), ("Étape 1", "Calculer la base"))

    def test_message_d_erreur_sur_l_equation_preparee(self):
        sortie = rel.resoudre("x*(1+0,04)^x=8")
        self.assertFalse(sortie["ok"])
        self.assertEqual(sortie["erreur"], el.MESSAGE_HORS_PROGRAMME)


if __name__ == "__main__":
    unittest.main()
