"""T33 (applications, étape 1) — Outil « Exponentielles et logarithmes » : lecture d'un problème d'application (EL-22) :
casse des lettres, noms indexés (C0, V_0), signe %, paramètre à simplifier et message à deux inconnues."""
import re
import unittest
from fractions import Fraction as F

import mpmath as mp

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
        self.assertEqual(el.sans_facteur(Op("*", Nb(3), Q), "Q"), Nb(3))
        self.assertEqual(el.sans_facteur(Op("*", Q, Pow(Nb(2), Var("x"))), "Q"), Pow(Nb(2), Var("x")))
        self.assertEqual(el.sans_facteur(Op("*", Op("+", Nb(1), Nb(2)), Q), "Q"), Op("+", Nb(1), Nb(2)))
        self.assertEqual(el.sans_facteur(Op("/", Q, Nb(2)), "Q"), Op("/", Nb(1), Nb(2)))
        self.assertEqual(el.sans_facteur(Neg(Q), "Q"), Neg(Nb(1)))
        self.assertIsNone(el.sans_facteur(Op("+", Q, Nb(1)), "Q"))
        self.assertIsNone(el.sans_facteur(Op("/", Nb(2), Q), "Q"))
        self.assertIsNone(el.sans_facteur(Op("*", Q, Q), "Q"))
        self.assertIsNone(el.sans_facteur(Nb(3), "Q"))

    def test_l_apercu_d_un_probleme_d_application(self):
        r = el.apercu("3Q = Q(1+3,75/100)^x")
        self.assertTrue(r["ok"])
        self.assertEqual(r["tex"], r"3Q = Q \cdot \left(1 + \frac{3{,}75}{100}\right)^{x}")
        self.assertEqual(el.apercu("V0/2 = V0(1-20/100)^n")["tex"].count("V_{0}"), 2)


def substituer(n, nom, valeur):
    """L'arbre n où la lettre `nom` vaut le nombre `valeur` (oracle : l'énoncé tel qu'il est écrit, paramètre compris)."""
    if isinstance(n, Var):
        return Nb(valeur) if n.nom == nom else n
    if isinstance(n, Neg):
        return Neg(substituer(n.a, nom, valeur))
    if isinstance(n, Op):
        return Op(n.op, substituer(n.a, nom, valeur), substituer(n.b, nom, valeur))
    if isinstance(n, Pow):
        return Pow(substituer(n.a, nom, valeur), substituer(n.b, nom, valeur))
    return n


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
        """La solution, substituée dans l'équation de l'énoncé (écrite avec le taux et les paramètres, valant 1, 7 ou 1234,5), la vérifie ;
        le nombre de solutions est celui attendu (EL-22)."""
        for saisie, attendu in BATTERIE_APPLICATIONS:
            with self.subTest(saisie):
                s = el.analyser_saisie(saisie)
                for m in el.METHODES:
                    r = el.variantes_equation(s.g, s.d, s.inconnue, s.parametres)[m]
                    if r.get("message"):
                        continue
                    self.assertEqual(len(r["solutions"]), len(attendu), m)
                    for n, v in zip(r["solutions"], attendu):
                        self.assertAlmostEqual(float(evaluer(n)), v, places=3)
                        for valeur_du_parametre in (1, 7, F(24691, 20)):
                            g, d = s.g, s.d
                            for p in s.parametres:
                                g, d = substituer(g, p, valeur_du_parametre), substituer(d, p, valeur_du_parametre)
                            self.assertTrue(vrai(Eq(g, d), evaluer(n)), f"{saisie} : {m}, paramètre {valeur_du_parametre}")

    def test_sorties_valides_et_carte_numerotee(self):
        for saisie, _ in BATTERIE_APPLICATIONS:
            with self.subTest(saisie):
                sortie = rel.resoudre(saisie)
                self.assertEqual(so.valider(sortie), [])
                if saisie == "2=1,0375^x":                  # la base est déjà un nombre : pas de carte (entrée témoin)
                    self.assertNotIn("Calculer la base", [c.get("badge") for v in sortie["variantes"] for c in v["cartes"]])
                    continue
                s = el.analyser_saisie(saisie)
                attendu = "Calculer la base" if el.preparer_application(s.g, s.d, s.inconnue)[2] else "Simplifier par " + s.parametres[0]
                for v in sortie["variantes"]:
                    premiere = v["cartes"][0]
                    self.assertEqual((premiere["titre"], premiere["badge"]), ("Étape 1", attendu))

    def test_les_cartes_d_un_probleme_avec_parametre(self):
        s = el.analyser_saisie("3Q=Q(1+3,75/100)^x")
        for m, r in el.variantes_equation(s.g, s.d, s.inconnue, s.parametres).items():
            self.assertEqual(titres(r)[:2], ["Calculer la base", "Simplifier par Q"], m)
        s = el.analyser_saisie("C0*1,05^n=2*C0")                    # pas de base à calculer : la carte du paramètre seule
        r = el.corriger_equation(s.g, s.d, s.inconnue, parametres=s.parametres)
        self.assertEqual(titres(r)[0], "Simplifier par C0")
        chaine = r["etapes"][0]["lignes"][0]
        self.assertEqual(el.tex_chaine(chaine), r"C_{0} \cdot 1{,}05^{n} = 2C_{0} \iff 1{,}05^{n} = 2 \quad \text{(on divise les deux membres par } C_{0} \text{ ; } C_{0} > 0 \text{ : une quantité de départ est positive)}")

    def test_la_propriete_s_ecrit_avec_le_nom_du_parametre(self):
        for saisie, nom_tex in [("3Q=Q(1+3,75/100)^x", "Q"), ("C_0*1,05^n=2C_0", "C_{0}"), ("V0/2=V0(1-20/100)^n", "V_{0}")]:
            with self.subTest(saisie):
                sortie = rel.resoudre(saisie)
                texte = "".join(b.get("html", "") for v in sortie["variantes"] for c in v["cartes"] for b in c["blocs"])
                self.assertIn(rf"on divise les deux membres par \({nom_tex}\) (\({nom_tex} &gt; 0\) : une quantité de départ est positive)", texte)

    def test_dans_les_deux_methodes_la_carte_est_la_meme_et_les_solutions_aussi(self):
        for saisie, _ in BATTERIE_APPLICATIONS:
            s = el.analyser_saisie(saisie)
            a, b = (el.variantes_equation(s.g, s.d, s.inconnue, s.parametres)[m] for m in el.METHODES)
            self.assertEqual([c["titre"] for c in a["etapes"] if c["titre"].startswith(("Calculer", "Simplifier"))],
                             [c["titre"] for c in b["etapes"] if c["titre"].startswith(("Calculer", "Simplifier"))], saisie)
            if not a.get("message"):
                self.assertEqual(a["solutions"], b["solutions"], saisie)

    def test_chaque_justification_vient_de_la_liste_fermee(self):
        """EL-06 : propriétés nommées de la liste, justification « car D ≠ 0 » ou division par le paramètre ; aucune ligne ⇔ sans justification."""
        for saisie, _ in BATTERIE_APPLICATIONS:
            s = el.analyser_saisie(saisie)
            for m, r in el.variantes_equation(s.g, s.d, s.inconnue, s.parametres).items():
                for c in r["etapes"]:
                    for ligne in c["lignes"]:
                        if isinstance(ligne, el.Chaine):
                            for lien, p in zip(ligne.liens, ligne.props):
                                self.assertTrue(p is None or p in el.PROPRIETES or isinstance(p, (el.Car, el.Divise)), (saisie, m, p))
                                if c["titre"] == "Simplifier par " + (s.parametres[0] if s.parametres else ""):
                                    self.assertIsInstance(p, el.Divise)

    def test_message_d_erreur_sur_l_equation_preparee(self):
        sortie = rel.resoudre("x*(1+0,04)^x=8")
        self.assertFalse(sortie["ok"])
        self.assertEqual(sortie["erreur"], el.MESSAGE_HORS_PROGRAMME)


# ---------------------------------------------------------------------
# Étape 4 : interpretation en années, mois et jours (EL-23, règle R16)
# ---------------------------------------------------------------------
OR = mp.MPContext()          # contexte isolé : 50 chiffres, sans toucher à la précision globale de mpmath
OR.dps = 50


def duree_de_reference(x):
    """Oracle indépendant du moteur : la durée est arrondie au jour supérieur (T jours, 1 an = 360 jours, 1 mois = 30 jours), puis décomposée.
    x : Fraction (exact) ou mpf à 50 chiffres."""
    if isinstance(x, F):
        T = -((-x * 360).__floor__())
    else:
        T = int(OR.ceil(360 * x))
    return (T // 360, (T % 360) // 30, T % 30)


def duree_naive(x):
    """Ce que le moteur ne doit PAS faire : calculer les restes à partir des valeurs arrondies à 3 décimales."""
    r3 = lambda v: round(float(v) + 1e-12, 3)
    a = int(x)
    r = r3(x - a)
    m_ex = r * 12
    m = int(m_ex)
    r2 = r3(m_ex - m)
    j = -int(-(r2 * 30) // 1)
    if j >= 30:
        j, m = 0, m + 1
    if m >= 12:
        m, a = 0, a + 1
    return (a, m, j)


def duree_du_texte(conclusion):
    """(années, mois, jours) lus dans « Au bout de 29 ans, 10 mois et 4 jours. »."""
    m = re.fullmatch(r"Au bout de (\d+) ans?, (\d+) mois et (\d+) jours?\.", conclusion)
    assert m, conclusion
    return tuple(int(v) for v in m.groups())


def interpretation_de(saisie):
    s = el.analyser_saisie(saisie)
    return el.interpretation(el.corriger_equation(s.g, s.d, s.inconnue, parametres=s.parametres))


def resultat_fictif(*valeurs):
    return {"solutions": [Nb(v) for v in valeurs], "inconnue": "x", "ensemble": None}


class TestInterpretation(unittest.TestCase):
    def test_l_exemple_du_test(self):
        i = interpretation_de("3Q=Q(1+3,75/100)^x")
        self.assertEqual(i["duree"], (29, 10, 4))
        self.assertEqual(i["conclusion"], "Au bout de 29 ans, 10 mois et 4 jours.")
        self.assertEqual([l.texte() for l in i["carte"]["lignes"]], [
            "Conventions : 1 an = 12 mois et 1 mois = 30 jours.",
            r"x \approx 29{,}842 : 29 ans ; reste 0{,}842 an.",
            r"0{,}842 \cdot 12 \approx 10{,}107 mois → 10 mois ; reste 0{,}107 mois.",
            r"0{,}107 \cdot 30 \approx 3{,}215 jours → 4 jours.",
            "Au bout de 3 jours, la durée cherchée n'est pas encore écoulée : on arrondit au jour supérieur.",
        ])

    def test_les_exemples_de_la_demande(self):
        for saisie, duree in [("2C=C(1+0,04)^n", (17, 8, 3)), ("C0*1,05^n=2*C0", (14, 2, 15)), ("V0/2=V0(1-20/100)^n", (3, 1, 9)),
                              ("2000*1,045^n=3805", (14, 7, 11)), ("37e^(-0,02t)=25", (19, 7, 7))]:
            with self.subTest(saisie):
                i = interpretation_de(saisie)
                self.assertEqual(i["duree"], duree)
                self.assertEqual(duree_du_texte(i["conclusion"]), duree)

    def test_oracle_sur_les_taux_realistes(self):
        """Doubler, tripler (taux de 0,5 % à 8 %), diviser par 2 ou par 4 (dépréciation de 5 % à 25 %) : la durée du moteur est celle de l'oracle."""
        essais = 0
        for facteur, ecriture in [(2, "2C"), (3, "3C")]:
            for centiemes in range(50, 801, 25):
                taux = F(centiemes, 100)
                texte = f"{taux.numerator / taux.denominator:g}".replace(".", ",")
                saisie = f"{ecriture}=C*(1+{texte}/100)^n"
                x = OR.log(facteur) / OR.log(1 + OR.mpf(taux.numerator) / taux.denominator / 100)
                with self.subTest(saisie):
                    i = interpretation_de(saisie)
                    self.assertEqual(i["duree"], duree_de_reference(x))
                    self.assertEqual(duree_du_texte(i["conclusion"]), duree_de_reference(x))
                essais += 1
        for diviseur, ecriture in [(2, "C/2"), (4, "C/4")]:
            for centiemes in range(500, 2501, 25):
                taux = F(centiemes, 100)
                texte = f"{taux.numerator / taux.denominator:g}".replace(".", ",")
                saisie = f"{ecriture}=C*(1-{texte}/100)^n"
                x = OR.log(OR.mpf(1) / diviseur) / OR.log(1 - OR.mpf(taux.numerator) / taux.denominator / 100)
                with self.subTest(saisie):
                    i = interpretation_de(saisie)
                    self.assertEqual(i["duree"], duree_de_reference(x))
                essais += 1
        self.assertEqual(essais, 2 * 31 + 2 * 81)

    def test_les_restes_ne_viennent_pas_des_valeurs_arrondies(self):
        """Il existe des taux où calculer avec les valeurs affichées (3 décimales) donnerait une autre durée : le moteur suit l'oracle, pas la méthode naïve."""
        differents = []
        for centiemes in range(50, 801, 5):
            x = OR.log(2) / OR.log(1 + OR.mpf(centiemes) / 10000)
            if duree_naive(x) != duree_de_reference(x):
                differents.append(centiemes)
                taux = f"{centiemes / 100:g}".replace(".", ",")
                self.assertEqual(interpretation_de(f"2C=C*(1+{taux}/100)^n")["duree"], duree_de_reference(x), taux)
        self.assertGreater(len(differents), 3)

    def test_rationnels_exacts(self):
        for x, duree in [(F(5, 2), (2, 6, 0)), (F(3), (3, 0, 0)), (F(1, 360), (0, 0, 1)), (F(1, 720), (0, 0, 1)), (F(1, 12), (0, 1, 0)),
                         (F(1, 12) + F(1, 360), (0, 1, 1)), (F(7, 4), (1, 9, 0)), (F(1, 3), (0, 4, 0))]:
            with self.subTest(x=x):
                i = el.interpretation(resultat_fictif(x))
                self.assertEqual(i["duree"], duree)
                self.assertEqual(duree_de_reference(x), duree)

    def test_zero_mois_et_zero_jour_sont_ecrits(self):
        self.assertEqual(el.interpretation(resultat_fictif(F(3)))["conclusion"], "Au bout de 3 ans, 0 mois et 0 jour.")
        self.assertEqual(el.interpretation(resultat_fictif(F(1, 12)))["conclusion"], "Au bout de 0 an, 1 mois et 0 jour.")
        self.assertEqual(el.interpretation(resultat_fictif(F(1, 360)))["conclusion"], "Au bout de 0 an, 0 mois et 1 jour.")
        self.assertEqual(el.interpretation(resultat_fictif(F(2) + F(1, 12) + F(2, 360)))["conclusion"], "Au bout de 2 ans, 1 mois et 2 jours.")

    def test_une_valeur_exacte_s_ecrit_avec_egal(self):
        lignes = [l.texte() for l in el.interpretation(resultat_fictif(F(5, 2)))["carte"]["lignes"]]
        self.assertEqual(lignes[1], r"x = 2{,}5 : 2 ans ; reste 0{,}5 an.")
        self.assertEqual(lignes[2], r"0{,}5 \cdot 12 = 6 mois → 6 mois ; reste 0 mois.")
        self.assertEqual(lignes[3], r"0 \cdot 30 = 0 jour → 0 jour.")
        self.assertFalse(any("arrondit" in l for l in lignes))            # aucun arrondi : aucune phrase de justification

    def test_30_jours_se_reportent_sur_le_mois(self):
        i = interpretation_de("2C=C*(1+4,5%)^n")                  # n ≈ 15,747 : 29,029 jours, soit 30
        self.assertEqual(i["duree"], (15, 9, 0))
        self.assertEqual(i["conclusion"], "Au bout de 15 ans, 9 mois et 0 jour.")
        self.assertIn("30 jours font 1 mois : on ajoute 1 mois.", [l.texte() for l in i["carte"]["lignes"]])

    def test_12_mois_se_reportent_sur_l_annee(self):
        x = F(11) + F(11, 12) + F(59, 720)                        # 11 ans, 11 mois, 29,5 jours
        i = el.interpretation(resultat_fictif(x))
        self.assertEqual(i["duree"], (12, 0, 0))
        textes = [l.texte() for l in i["carte"]["lignes"]]
        self.assertIn("30 jours font 1 mois : on ajoute 1 mois.", textes)
        self.assertIn("12 mois font 1 an : on ajoute 1 an.", textes)
        self.assertEqual(i["conclusion"], "Au bout de 12 ans, 0 mois et 0 jour.")

    def test_pas_de_report_quand_rien_ne_depasse(self):
        textes = [l.texte() for l in interpretation_de("3Q=Q(1+3,75/100)^x")["carte"]["lignes"]]
        self.assertFalse(any("on ajoute" in t for t in textes))

    def test_phrases_sans_duree(self):
        for saisie, cas, phrase in [("Q/2=Q*1,04^n", "negative", "La solution est négative : la situation décrite n'arrive jamais."),
                                    ("-2Q=Q*1,04^n", "vide", "Aucune solution : la situation décrite n'arrive jamais."),
                                    ("Q*1,04^n=Q", "nulle", "La situation est atteinte dès le départ.")]:
            with self.subTest(saisie):
                i = interpretation_de(saisie)
                self.assertEqual((i["cas"], i["duree"], i["conclusion"], i["carte"]["lignes"]), (cas, None, phrase, []))

    def test_pas_d_interpretation_quand_elle_n_a_pas_de_sens(self):
        for saisie in ["2^(x^2)=8", "2^x-2^x=0", "x*2^x=8", "log(x)=2", "x=ln(3)", "log(5-x)=8", "2x=ln(0,1)", "log_x(256)=4", "(x-1)(2^x-8)=0"]:
            with self.subTest(saisie):
                s = el.analyser_saisie(saisie)
                r = el.corriger_equation(s.g, s.d, s.inconnue)
                self.assertIsNone(el.interpretation(r) if r else None)
        # la méthode A qui ne s'applique pas n'a pas de solution : pas d'interprétation
        s = el.analyser_saisie("3=(1+3,75/100)^x")
        a = el.variantes_equation(s.g, s.d, s.inconnue)[el.METHODE_MEME_BASE]
        self.assertIsNone(el.interpretation(a))

    def test_suggestion_de_la_case(self):
        for saisie, attendu in [("3Q=Q(1+3,75/100)^x", True), ("2000*1,045^n=3805", True), ("2C=C(1+0,04)^n", True), ("37e^(-0,02t)=25", False),
                                ("2^x=100", False), ("3^(x+1)=27", False), ("log(5-x)=8", False), ("2^n=100", True)]:
            with self.subTest(saisie):
                self.assertIs(el.suggere_interpretation(el.analyser_saisie(saisie)), attendu)
        self.assertFalse(el.suggere_interpretation(el.analyser_saisie("log_2(50)")))

    def test_croissance_et_depreciation_ont_la_meme_carte(self):
        a, b = interpretation_de("2C=C*(1+4%)^n"), interpretation_de("C/2=C*(1-4%)^n")
        self.assertEqual(a["cas"], "positive")
        self.assertEqual(b["cas"], "positive")
        self.assertEqual([l.texte().split(" ")[0] for l in a["carte"]["lignes"][:1]], [l.texte().split(" ")[0] for l in b["carte"]["lignes"][:1]])

    def test_vouvoiement_et_vocabulaire(self):
        from aides_sortie import TUTOIEMENT
        for saisie in ["3Q=Q(1+3,75/100)^x", "2C=C*(1+4,5%)^n", "Q/2=Q*1,04^n", "-2Q=Q*1,04^n"]:
            i = interpretation_de(saisie)
            for t in [l.texte() for l in i["carte"]["lignes"]] + [i["conclusion"]]:
                self.assertIsNone(TUTOIEMENT.search(t), t)
                self.assertNotIn("valeur approchée", t)


if __name__ == "__main__":
    unittest.main()
