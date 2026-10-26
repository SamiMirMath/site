"""T33 (étape 1) — Outil « Exponentielles et logarithmes » : lecture de la saisie, arbre, TeX, aperçu (EL-03, EL-04, EL-05 pour la lecture).

Les étapes suivantes ajouteront ici la résolution (EL-01, EL-02, EL-06 à EL-11)."""
import json
import os
import re
import unittest
from fractions import Fraction as F

import mpmath as mp

from moteurs import RACINE
import cas_el
from cas_el import (BATTERIE_C1, BATTERIE_E1, BATTERIE_E2, BATTERIE_E3, BATTERIE_E4, SANS_E1, SANS_E2, SANS_E3)
from aides_sortie import TUTOIEMENT, chaines_litterales
import exp_log as el
from exp_log import Nb, Var, E, Neg, Op, Pow, Fn, Log, Eq
from noyau import ErreurSaisie

X = Var("x")


def lire(s):
    g, d = el.lire_membres(s)
    return g if d is None else (g, d)


class TestTokeniseur(unittest.TestCase):
    """EL-03 : les noms de fonction passent avant les lettres ; e est toujours le nombre e."""

    def test_fonctions_lues_comme_fonctions(self):
        self.assertEqual(lire("ln(x)"), Log(X, E()))
        self.assertEqual(lire("exp(x)"), Pow(E(), X))
        self.assertEqual(lire("log2(x)"), Log(X, Nb(2)))
        self.assertEqual(lire("log_3(x)"), Log(X, Nb(3)))
        self.assertEqual(lire("log10(x)"), Log(X, None))
        self.assertEqual(lire("log_10(x)"), Log(X, None))
        self.assertEqual(lire("log(x)"), Log(X, None))
        self.assertEqual(lire("log_x(256)"), Log(Nb(256), X))
        self.assertEqual(lire("log_2,5(x)"), Log(X, Nb(F(5, 2))))
        self.assertEqual(lire("sqrt(x)"), Fn("sqrt", X))
        self.assertEqual(lire("√(x)"), Fn("sqrt", X))

    def test_les_lettres_d_un_nom_de_fonction_ne_sont_jamais_des_inconnues(self):
        for s, attendu in [("ln(x)=3", {"x"}), ("exp(x)=7", {"x"}), ("log2(x)=4", {"x"}), ("log_3(x)=2", {"x"}),
                           ("log10(x)=1", {"x"}), ("sqrt(x)=3", {"x"}), ("log_x(256)=4", {"x"}), ("2*exp(t)=5", {"t"}),
                           ("ln(p)+log(p)=1", {"p"}), ("EXP(x)=7", {"x"}), ("LN(X)=3", {"x"})]:
            with self.subTest(s):
                g, d = el.lire_membres(s)
                self.assertEqual(el.variables(g) | el.variables(d), attendu)
                self.assertEqual(el.analyser_saisie(s).inconnue, next(iter(attendu)))

    def test_multiplication_implicite(self):
        self.assertEqual(lire("2x"), Op("*", Nb(2), X))
        self.assertEqual(lire("3ln(x)"), Op("*", Nb(3), Log(X, E())))
        self.assertEqual(lire("xlog(x)"), Op("*", X, Log(X, None)))
        self.assertEqual(lire("(x+1)(x-2)"), Op("*", Op("+", X, Nb(1)), Op("-", X, Nb(2))))
        self.assertEqual(lire("2exp(x)"), Op("*", Nb(2), Pow(E(), X)))
        self.assertEqual(lire("37*e^(-0,02t)"), Op("*", Nb(37), Pow(E(), Neg(Op("*", Nb(F(1, 50)), Var("t"))))))

    def test_e_est_toujours_la_constante(self):
        self.assertEqual(lire("e^x=7"), (Pow(E(), X), Nb(7)))
        s = el.analyser_saisie("e^x=7")
        self.assertEqual((s.genre, s.inconnue), ("equation", "x"))
        s = el.analyser_saisie("x+e=3")
        self.assertEqual(s.inconnue, "x")
        self.assertEqual(s.g, Op("+", X, E()))
        self.assertEqual(lire("ex"), Op("*", E(), X))
        self.assertEqual(lire("log_e(x)"), Log(X, E()))

    def test_e_ne_peut_pas_etre_l_inconnue(self):
        for s in ["2e=5", "e^2=e", "e=3", "e+1=4", "ln(e)=1"]:
            with self.subTest(s):
                with self.assertRaises(ErreurSaisie) as c:
                    el.analyser_saisie(s)
                self.assertEqual(str(c.exception), el.MESSAGE_E)

    def test_priorites_et_associativite(self):
        self.assertEqual(lire("-x^2"), Neg(Pow(X, Nb(2))))
        self.assertEqual(lire("2^x+1"), Op("+", Pow(Nb(2), X), Nb(1)))
        self.assertEqual(lire("2^(-x)"), Pow(Nb(2), Neg(X)))
        self.assertEqual(lire("x-1-2"), Op("-", Op("-", X, Nb(1)), Nb(2)))
        self.assertEqual(lire("8/2/2"), Op("/", Op("/", Nb(8), Nb(2)), Nb(2)))
        self.assertEqual(lire("2x^2"), Op("*", Nb(2), Pow(X, Nb(2))))
        self.assertEqual(lire("4^(3x+1)"), Pow(Nb(4), Op("+", Op("*", Nb(3), X), Nb(1))))

    def test_decimaux(self):
        self.assertEqual(lire("0,01"), Nb(F(1, 100)))
        self.assertEqual(lire("0.01"), Nb(F(1, 100)))
        self.assertEqual(lire(",5"), Nb(F(1, 2)))
        self.assertEqual(lire("1,0325"), Nb(F(10325, 10000)))


class TestErreurs(unittest.TestCase):
    """Messages en français, jamais de trace Python."""

    def refuse(self, s, fragment, analyser=False):
        with self.assertRaises(ErreurSaisie) as c:
            (el.analyser_saisie if analyser else el.lire_membres)(s)
        m = str(c.exception)
        self.assertIn(fragment, m, s)
        self.assertNotIn("Traceback", m)

    def test_syntaxe(self):
        self.refuse("", "Écrivez une équation")
        self.refuse("   ", "Écrivez une équation")
        self.refuse("3^(x+1", "parenthèse fermante")
        self.refuse("3^x+1)", "Parenthèse fermante en trop")
        self.refuse("(x+1)=)", "Parenthèse fermante en trop")
        self.refuse("x==3", "Un seul signe")
        self.refuse("x=3=4", "Un seul signe")
        self.refuse("=3", "membre")
        self.refuse("x=", "membre")
        self.refuse("x+*3=1", "Il manque un terme avant")
        self.refuse("3 + = 4", "Il manque")
        self.refuse("x+#", "Caractère non reconnu")
        self.refuse("2+-3=x", "Deux signes")

    def test_fonctions_sans_parentheses(self):
        self.refuse("ln x = 3", "Après ln, ouvrez une parenthèse")
        self.refuse("exp x", "Après exp, ouvrez une parenthèse")
        self.refuse("log2 x = 4", "Après log_2, ouvrez une parenthèse")
        self.refuse("sqrt x", "Après sqrt")
        self.refuse("√x", "Après √")
        self.refuse("log_(x)", "Pour une autre base")

    def test_ambiguites_refusees(self):
        self.refuse("2 3x = 5", "Un nombre ne peut pas suivre")
        self.refuse("x2 = 5", "Un nombre ne peut pas suivre")
        self.refuse("(x+1)2 = 5", "Un nombre ne peut pas suivre")
        self.refuse("1/2x = 3", "parenthèses après la division")
        self.refuse("a/bc = 3", "parenthèses après la division")

    def test_inequations(self):
        for s in ["x<3", "2^x>=3", "2^x≤8", "x>1", "x≠2"]:
            with self.subTest(s):
                self.refuse(s, "inéquations")

    def test_bases_interdites(self):
        for s in ["log_1(x)=2", "log_0(x)=2", "log1(x)=2", "log0(x)=2", "log_0,0(x)=1"]:
            with self.subTest(s):
                self.refuse(s, "strictement positive et différente de 1")

    def test_fonctions_inconnues(self):
        for s, nom in [("sin(x)=0", "sin"), ("cos(x)=1", "cos"), ("tan(x)=2", "tan"), ("TAN(x)=2", "tan"), ("lg(x)=2", "lg"), ("2lg(x)=4", "lg"),
                       ("sin(", "sin"), ("sin (x)=0", "sin")]:
            with self.subTest(s):
                self.refuse(s, f"La fonction {nom} n'est pas traitée par cet outil.")
        for s in ["xlog(x)=2", "3ln(x)=1", "2exp(t)=5", "(x+1)(x-2)=0", "2x(x+1)=0", "Log(x)=2"]:      # produits implicites et noms connus : acceptés
            with self.subTest(s):
                el.lire_membres(s)

    def test_equation_ou_calcul(self):
        self.refuse("3^x", "Écrivez une équation", analyser=True)
        self.refuse("2x+1", "Écrivez une équation", analyser=True)
        self.refuse("3=4", "Il faut une inconnue", analyser=True)
        self.refuse("x+y=3", "Une seule inconnue : vous avez écrit x et y", analyser=True)
        self.refuse("2^(x+y)=8", "Une seule inconnue", analyser=True)
        s = el.analyser_saisie("log_4(sqrt(2))")
        self.assertEqual((s.genre, s.d, s.inconnue), ("calcul", None, None))
        self.assertEqual(el.analyser_saisie("log(50)").genre, "calcul")
        self.assertEqual(el.analyser_saisie("log_x(256)=4").inconnue, "x")


# (saisie, TeX attendu)
TEX = [
    ("3^(x+1)=27", "3^{x + 1} = 27"),
    ("2^x=100", "2^{x} = 100"),
    ("4^(3x+1)=8", "4^{3x + 1} = 8"),
    ("3*2^(x^2+1)=96", "3 \\cdot 2^{x^{2} + 1} = 96"),
    ("2^x=2*4^(x-1)", "2^{x} = 2 \\cdot 4^{x - 1}"),
    ("10^(2x)=0,01", "10^{2x} = 0{,}01"),
    ("1,0325^n=3", "1{,}0325^{n} = 3"),
    ("log(5-x)=8", "\\log(5 - x) = 8"),
    ("ln(x)=3", "\\ln(x) = 3"),
    ("log2(x)=4", "\\log_{2}(x) = 4"),
    ("log_2(x)=4", "\\log_{2}(x) = 4"),
    ("log10(x)=1", "\\log(x) = 1"),
    ("log_x(256)=4", "\\log_{x}(256) = 4"),
    ("2*log_3(x)=10", "2\\log_{3}(x) = 10"),
    ("37*e^(-0,02t)=25", "37e^{-0{,}02t} = 25"),
    ("exp(x)=7", "e^{x} = 7"),
    ("e^(-0,01x)=0,7", "e^{-0{,}01x} = 0{,}7"),
    ("sqrt(x)=3", "\\sqrt{x} = 3"),
    ("x/2=3", "\\frac{x}{2} = 3"),
    ("ln(25/37)", "\\ln\\left(\\frac{25}{37}\\right)"),
    ("log_4(sqrt(2))", "\\log_{4}(\\sqrt{2})"),
    ("(x+3)(x-1)=0", "(x + 3)(x - 1) = 0"),
    ("10^x*(10^x-4)=0", "10^{x} \\cdot (10^{x} - 4) = 0"),
    ("2^(x-1)=3^x", "2^{x - 1} = 3^{x}"),
    ("-x^2+1", "-x^{2} + 1"),
    ("2-(x+1)", "2 - (x + 1)"),
    ("(1/2)^x", "\\left(\\frac{1}{2}\\right)^{x}"),
    ("x(x-2)=0", "x(x - 2) = 0"),
    ("(2^2)^x", "(2^{2})^{x}"),
    ("log(log(log(x)))=0", "\\log(\\log(\\log(x))) = 0"),
]


class TestTex(unittest.TestCase):
    def test_tex_attendu(self):
        for saisie, attendu in TEX:
            with self.subTest(saisie):
                g, d = el.lire_membres(saisie)
                self.assertEqual(el.tex_saisie(g, d), attendu)

    def test_ln_et_log_ne_se_melangent_jamais(self):
        """EL-04/EL-05 : ln s'écrit \\ln (base e), log s'écrit \\log (base 10), log_a s'écrit \\log_{a} ; jamais l'un pour l'autre."""
        for s in ["ln(x)=3", "e^x=7", "log(x)=3", "log10(x)=3", "log_10(x)=3"]:
            g, d = el.lire_membres(s)
            t = el.tex_saisie(g, d)
            if s.startswith("ln"):
                self.assertIn("\\ln", t)
                self.assertNotIn("\\log", t)
            elif s.startswith("log"):
                self.assertIn("\\log", t)
                self.assertNotIn("\\ln", t)
                self.assertNotIn("_{10}", t)
            else:
                self.assertNotIn("\\log", t)
        self.assertEqual(el.tex(Log(X, None)), "\\log(x)")
        self.assertEqual(el.tex(Log(X, E())), "\\ln(x)")
        self.assertEqual(el.tex(Log(X, Nb(5))), "\\log_{5}(x)")
        self.assertEqual(el.tex(Log(X, Var("a"))), "\\log_{a}(x)")

    def test_pas_de_point_decimal(self):
        """SOC-12 : la virgule décimale est la seule écriture (« 0{,}01 »), jamais « 0.01 »."""
        for s in ["10^(2x)=0.01", "10^(2x)=0,01", "1.0325^n=3"]:
            g, d = el.lire_membres(s)
            self.assertNotRegex(el.tex_saisie(g, d), r"\d\.\d")

    def test_tex_des_noeuds_calcules(self):
        """Les valeurs exactes que les étapes suivantes construiront (fractions, négatifs) s'écrivent aussi par l'arbre."""
        self.assertEqual(el.tex(Nb(F(3, 2))), "\\frac{3}{2}")
        self.assertEqual(el.tex(Nb(F(-3, 2))), "-\\frac{3}{2}")
        self.assertEqual(el.tex(Op("-", X, Nb(-3))), "x - (-3)")
        self.assertEqual(el.tex(Op("*", Nb(-2), X)), "(-2) \\cdot x")
        self.assertEqual(el.tex(Neg(Op("+", X, Nb(1)))), "-(x + 1)")
        self.assertEqual(el.tex(Op("/", Log(Nb(20), None), Log(Nb(2), None))), "\\frac{\\log(20)}{\\log(2)}")
        self.assertEqual(el.tex(Pow(Nb(F(3, 2)), X)), "\\left(\\frac{3}{2}\\right)^{x}")


class TestApercu(unittest.TestCase):
    def test_apercu_ok_et_erreur(self):
        r = json.loads(el.apercu_json("log_2(x)=4"))
        self.assertEqual(r, {"ok": True, "tex": "\\log_{2}(x) = 4"})
        r = json.loads(el.apercu_json("3^(x+1"))
        self.assertFalse(r["ok"])
        self.assertIn("parenthèse", r["erreur"])
        self.assertNotIn("Traceback", r["erreur"])

    def test_apercu_ne_valide_que_la_syntaxe(self):
        """Le contrôle manifeste (test_manifeste) appelle apercu_json('x+1') ; une saisie à deux lettres ou sans « = » s'affiche aussi."""
        for s in ["x+1", "x+y=3", "3^x", "2e=5"]:
            self.assertTrue(json.loads(el.apercu_json(s))["ok"], s)

    def test_aucune_saisie_ne_leve_autre_chose_qu_une_erreur_de_saisie(self):
        for s in ["((", "))", "^", "x^", "^2", "log_", "log_(", "log(", "ln()", "2^^3", "x=y=z", "1..2", "1,,2", "ln(x)ln", "=", "==",
                  "x+", "*2", "2*", "/", "2/", "e^", "sqrt()", "exp(", "√", "x y", "ln(x)(", "((x)", ",", ".", "x,y"]:
            with self.subTest(s):
                try:
                    el.apercu(s)
                    try:
                        el.analyser_saisie(s)
                    except ErreurSaisie:
                        pass
                except ErreurSaisie:
                    self.fail("apercu doit renvoyer un dict d'erreur, pas lever")
                r = el.apercu(s)
                if not r["ok"]:
                    self.assertTrue(r["erreur"])
                    self.assertNotIn("Traceback", r["erreur"])


class TestExposants(unittest.TestCase):
    """L'exposant est un seul nombre, une seule lettre, ou une parenthèse : sinon l'élève doit mettre des parenthèses."""

    def test_l_exposant_s_arrete_au_premier_terme(self):
        g = lire("2^x+1")
        self.assertEqual(g, Op("+", Pow(Nb(2), X), Nb(1)))
        self.assertEqual(el.tex(g), "2^{x} + 1")
        self.assertEqual(lire("x^2+1"), Op("+", Pow(X, Nb(2)), Nb(1)))
        self.assertEqual(lire("2^x*3"), Op("*", Pow(Nb(2), X), Nb(3)))

    def test_exposants_composes_exigent_des_parentheses(self):
        for s in ["e^-0,02t", "2^-x", "2^+x", "e^-1", "e^0,02t", "2^3x", "2^xy", "2^sqrt(x)", "2^ln(x)", "e^2(x+1)", "e^2ln(x)",
                  "2^x^2*3", "x^2y"]:
            with self.subTest(s):
                with self.assertRaises(ErreurSaisie) as c:
                    el.lire_membres(s)
                self.assertIn("exposant", str(c.exception).lower(), s)
        for s in ["e^-0,02t", "2^-x", "e^0,02t", "2^3x", "2^sqrt(x)", "e^2(x+1)"]:
            with self.assertRaises(ErreurSaisie) as c:
                el.lire_membres(s)
            self.assertEqual(str(c.exception), "Mettez l'exposant entre parenthèses : e^(-0,02t).", s)
        self.assertEqual(el.MESSAGE_EXPOSANT, "Mettez l'exposant entre parenthèses : e^(-0,02t).")

    def test_puissance_de_puissance(self):
        with self.assertRaises(ErreurSaisie) as c:
            el.lire_membres("2^3^2")
        self.assertIn("Mettez les exposants entre parenthèses", str(c.exception))
        self.assertEqual(lire("2^(3^2)"), Pow(Nb(2), Pow(Nb(3), Nb(2))))
        self.assertEqual(lire("(2^3)^2"), Pow(Pow(Nb(2), Nb(3)), Nb(2)))

    def test_exposants_acceptes(self):
        self.assertEqual(lire("e^(-0,02t)"), Pow(E(), Neg(Op("*", Nb(F(1, 50)), Var("t")))))
        self.assertEqual(lire("2^(-x)"), Pow(Nb(2), Neg(X)))
        self.assertEqual(lire("x^2"), Pow(X, Nb(2)))
        self.assertEqual(lire("2^x"), Pow(Nb(2), X))
        self.assertEqual(lire("1,03^n"), Pow(Nb(F(103, 100)), Var("n")))
        self.assertEqual(lire("e^x"), Pow(E(), X))
        self.assertEqual(lire("2^e"), Pow(Nb(2), E()))
        self.assertEqual(lire("x^(1/2)"), Pow(X, Op("/", Nb(1), Nb(2))))
        # une lettre en exposant, puis une parenthèse ou une fonction : le produit est sans ambiguïté
        self.assertEqual(lire("10^x(10^x-4)=0")[0], Op("*", Pow(Nb(10), X), Op("-", Pow(Nb(10), X), Nb(4))))
        self.assertEqual(lire("2^x ln(x)"), Op("*", Pow(Nb(2), X), Log(X, E())))

    def test_equations_du_cours(self):
        self.assertEqual(lire("4^(3x+1)=8"), (Pow(Nb(4), Op("+", Op("*", Nb(3), X), Nb(1))), Nb(8)))
        self.assertEqual(lire("37e^(-0,02t)=25"),
                         (Op("*", Nb(37), Pow(E(), Neg(Op("*", Nb(F(1, 50)), Var("t"))))), Nb(25)))
        self.assertEqual(el.tex_saisie(*el.lire_membres("4^(3x+1)=8")), "4^{3x + 1} = 8")
        self.assertEqual(el.tex_saisie(*el.lire_membres("37e^(-0,02t)=25")), "37e^{-0{,}02t} = 25")
        self.assertEqual(el.analyser_saisie("37e^(-0,02t)=25").inconnue, "t")
        self.assertEqual(el.analyser_saisie("4^(3x+1)=8").inconnue, "x")


class TestVouvoiement(unittest.TestCase):
    """Les messages destinés à l'élève vouvoient : « Choisissez une autre lettre », « Ouvrez une parenthèse : ln(x). »."""

    MAUVAISES_SAISIES = ["", "   ", "3^(x+1", "3^x+1)", "x==3", "=3", "x+*3=1", "x+#", "2+-3=x", "ln x = 3", "exp x", "log2 x = 4", "sqrt x",
                         "√x", "log_(x)", "2 3x = 5", "x2 = 5", "1/2x = 3", "x<3", "log_1(x)=2", "3^x", "2x+1", "3=4", "x+y=3", "2e=5",
                         "e^2=e", "e=3", "e^-0,02t", "2^3^2", "x^", "e^0,02t"]

    def messages(self):
        for s in self.MAUVAISES_SAISIES:
            try:
                el.analyser_saisie(s)
            except ErreurSaisie as e:
                yield s, str(e)

    def test_messages_d_erreur(self):
        vus = list(self.messages())
        self.assertEqual(len(vus), len(self.MAUVAISES_SAISIES))
        for s, m in vus:
            with self.subTest(s):
                self.assertIsNone(TUTOIEMENT.search(m), m)

    def test_vouvoiement_dans_les_messages_connus(self):
        self.assertEqual(el.MESSAGE_E, "La lettre e désigne le nombre e ≈ 2,718 : choisissez une autre lettre pour l'inconnue.")
        r = el.apercu("ln x = 3")
        self.assertEqual(r["erreur"], "Après ln, ouvrez une parenthèse : ln(x).")
        with self.assertRaises(ErreurSaisie) as c:
            el.analyser_saisie("x+y=3")
        self.assertEqual(str(c.exception), "Une seule inconnue : vous avez écrit x et y.")

    def test_aucun_texte_du_fichier_ne_tutoie(self):
        """Tout littéral texte de exp_log.py (hors docstrings), pas seulement ceux que les entrées ci-dessus font apparaître."""
        chemin = os.path.join(RACINE, "exponentielles-logarithmes", "exp_log.py")
        for ligne, texte in chaines_litterales(chemin):
            with self.subTest(ligne=ligne):
                self.assertIsNone(TUTOIEMENT.search(texte), texte)


# ---------------------------------------------------------------------
# Étape 2 : méthode « même base » (E1)
# ---------------------------------------------------------------------
MP = mp.MPContext()          # contexte isolé : ne change pas la précision globale de mpmath (les autres tests l'utilisent)
MP.dps = 30


def evaluer(n, x=None):
    """Oracle indépendant du moteur : valeur d'un arbre avec mpmath."""
    if isinstance(n, Nb):
        return MP.mpf(n.val.numerator) / n.val.denominator
    if isinstance(n, Var):
        return MP.mpf(x)
    if isinstance(n, E):
        return MP.e
    if isinstance(n, Neg):
        return -evaluer(n.a, x)
    if isinstance(n, Op):
        a, b = evaluer(n.a, x), evaluer(n.b, x)
        return a + b if n.op == "+" else a - b if n.op == "*" and False else (a - b if n.op == "-" else (a * b if n.op == "*" else a / b))
    if isinstance(n, Pow):
        return MP.power(evaluer(n.a, x), evaluer(n.b, x))
    if isinstance(n, Fn):
        return MP.sqrt(evaluer(n.a, x))
    if isinstance(n, Log):
        return MP.log(evaluer(n.a, x)) / (MP.log(10) if n.base is None else MP.log(evaluer(n.base, x)))
    raise TypeError(n)


def vrai(eq, x):
    """L'équation est vérifiée en x (écart relatif < 1e-15)."""
    g, d = evaluer(eq.g, x), evaluer(eq.d, x)
    return abs(g - d) <= MP.mpf("1e-15") * (1 + abs(g) + abs(d))


def element_vrai(e, x):
    return any(vrai(q, x) for q in e.eqs) if isinstance(e, el.Ou) else vrai(e, x)


def corrige(saisie):
    s = el.analyser_saisie(saisie)
    return el.meme_base(s.g, s.d, s.inconnue)


def val(x):
    return MP.mpf(x.numerator) / x.denominator




class TestMemeBase(unittest.TestCase):
    def test_batterie(self):
        for saisie, attendu in BATTERIE_E1:
            with self.subTest(saisie):
                r = corrige(saisie)
                self.assertIsNotNone(r)
                if attendu is None:
                    self.assertIsNone(r["solutions"])
                    continue
                self.assertEqual(len(r["solutions"]), len(attendu))
                for n, v in zip(r["solutions"], attendu):
                    self.assertEqual(n, Nb(v))
                    self.assertAlmostEqual(el.valeur(n), float(v), places=12)

    def test_solution_irrationnelle(self):
        r = corrige("2^(x^2)=2^(2x+1)")
        self.assertEqual([el.tex(n) for n in r["solutions"]], ["1 - \\sqrt{2}", "1 + \\sqrt{2}"])
        for n in r["solutions"]:
            self.assertTrue(vrai(Eq(*el.lire_membres("2^(x^2)=2^(2x+1)")), evaluer(n)))
        r = corrige("3^(x^2)=3^(2x+3)")        # x² − 2x − 3 = 0 : racines entières
        self.assertEqual(r["solutions"], [Nb(-1), Nb(3)])
        r = corrige("2^(x^2)=2^(3x+1)")        # Δ = 13
        self.assertEqual([round(el.valeur(n), 9) for n in r["solutions"]], [round((3 - 13 ** 0.5) / 2, 9), round((3 + 13 ** 0.5) / 2, 9)])
        r = corrige("2^(x^2)=2^(4x+2)")        # x = 2 ± √6, 6 sans facteur carré
        self.assertEqual([el.tex(n) for n in r["solutions"]], ["2 - \\sqrt{6}", "2 + \\sqrt{6}"])
        r = corrige("2^(x^2)=2^(6x+2)")        # Δ = 44 = 4·11 : x = 3 ± √11
        self.assertEqual([el.tex(n) for n in r["solutions"]], ["3 - \\sqrt{11}", "3 + \\sqrt{11}"])
        r = corrige("2^(2x^2)=2^(x+3)")        # 2x² − x − 3 = 0 : x = −1 ou 3/2, a ≠ 1 : par le discriminant
        self.assertEqual(r["solutions"], [Nb(F(-1)), Nb(F(3, 2))])

    def test_oracle_les_solutions_verifient_l_equation_de_l_enonce(self):
        for saisie, attendu in BATTERIE_E1:
            if not attendu:
                continue
            with self.subTest(saisie):
                s = el.analyser_saisie(saisie)
                for v in attendu:
                    self.assertTrue(vrai(Eq(s.g, s.d), val(v)), f"{saisie} : x = {v}")

    def test_aucune_autre_solution_dans_l_intervalle(self):
        """Le nombre de racines de g − d sur [−8 ; 8] (changements de signe) est celui des solutions annoncées."""
        for saisie, attendu in BATTERIE_E1:
            if attendu is None or len(attendu) == 0:
                continue
            with self.subTest(saisie):
                s = el.analyser_saisie(saisie)
                pas, signes, k = 0.01, [], 0
                for i in range(-800, 801):
                    x = MP.mpf(i) * MP.mpf("0.01") + MP.mpf("0.000123")
                    g = evaluer(s.g, x) - evaluer(s.d, x)
                    signes.append(1 if g > 0 else -1)
                racines = sum(1 for a, b in zip(signes, signes[1:]) if a != b)
                self.assertEqual(racines, len([v for v in attendu if -8 < v < 8]), saisie)

    def test_chaines_les_egalites_sont_justes_pour_tout_x(self):
        """Une chaîne « a = b = c » d'expressions : tous les éléments ont la même valeur, pour des x quelconques."""
        for saisie, attendu in BATTERIE_E1:
            with self.subTest(saisie):
                for carte in corrige(saisie)["etapes"]:
                    for ligne in carte["lignes"]:
                        if "=" not in ligne.liens:
                            continue
                        elements = ligne.elements
                        if isinstance(elements[0], Var) and elements[0].nom == "Δ":      # Δ = b² − 4ac = valeur : Δ n'est pas l'inconnue
                            elements = elements[1:]
                        for x in ["0.37", "-1.4", "2.3", "0.9", "-0.2"]:
                            v = [evaluer(e, MP.mpf(x)) for e in elements]
                            for w in v[1:]:
                                self.assertLessEqual(abs(w - v[0]), MP.mpf("1e-20") * (1 + abs(v[0])), (saisie, el.tex_chaine(ligne)))

    def test_chaines_les_equivalences_gardent_les_solutions(self):
        """Une chaîne « E₀ ⇔ E₁ ⇔ … » : chaque équation est vérifiée aux solutions et pas aux autres points d'une grille."""
        for saisie, attendu in BATTERIE_E1:
            if attendu is None:
                continue
            with self.subTest(saisie):
                sols = [val(v) for v in attendu]
                grille = [MP.mpf(i) / 4 + MP.mpf("0.0371") for i in range(-40, 41)]
                for carte in corrige(saisie)["etapes"]:
                    for ligne in carte["lignes"]:
                        if "⇔" not in ligne.liens:
                            continue
                        for e in ligne.elements:
                            if not isinstance(e, (Eq, el.Ou)):
                                continue
                            for x in sols:
                                if isinstance(e, Eq) and "Δ" in el.tex(e.g):
                                    continue
                                self.assertTrue(element_vrai(e, x), (saisie, el.tex_element(e), x))
                            for x in grille:
                                self.assertFalse(element_vrai(e, x), (saisie, el.tex_element(e), x))

    def test_proprietes_nommees(self):
        """Toute propriété affichée est dans la liste fermée, et le passage de a^A = a^B à A = B porte « même base »."""
        for saisie, attendu in BATTERIE_E1:
            with self.subTest(saisie):
                r = corrige(saisie)
                for carte in r["etapes"]:
                    for ligne in carte["lignes"]:
                        for p in ligne.props:
                            self.assertTrue(p is None or p in el.PROPRIETES, (saisie, p))
                derniere = r["etapes"][-1]
                self.assertEqual(derniere["titre"], "Même base")
                avec_equivalences = [l for l in derniere["lignes"] if "⇔" in l.liens]
                self.assertEqual(len(avec_equivalences), 1, "une seule chaîne de ⇔ dans la carte « Même base »")
                self.assertEqual(avec_equivalences[0].props[0], el.PROP_MEME_BASE)

    def test_cartes(self):
        titres = lambda s: [c["titre"] for c in corrige(s)["etapes"]]
        self.assertEqual(titres("7^(2x+1)=7^9"), ["Même base"])
        self.assertEqual(titres("3^x=27"), ["Même base"])
        self.assertEqual(titres("3^(x+1)-27=0"), ["Isoler l'exponentielle", "Même base"])
        self.assertEqual(titres("2*3^(x-1)=18"), ["Isoler l'exponentielle", "Même base"])
        self.assertEqual(titres("5^(3x+2)=(5^x)^2"), ["Même base"])
        self.assertEqual(titres("2^(x^2)*4^x=8"), ["Même base"])

    def test_carte_meme_base_reecriture_puis_une_chaine_d_equivalences(self):
        """La carte « Même base » (comme l'encadré « se ramener à la même base » du corrigé) : les lignes de réécriture (liens « = »)
        d'abord, puis la chaîne de ⇔ qui part de a^A = a^B ; « Isoler l'exponentielle » reste une carte à part."""
        for saisie, _ in BATTERIE_E1:
            with self.subTest(saisie):
                r = corrige(saisie)
                self.assertEqual(sum(1 for c in r["etapes"] if c["titre"] == "Même base"), 1)
                self.assertLessEqual(len(r["etapes"]), 2)
                lignes = r["etapes"][-1]["lignes"]
                rang = [i for i, l in enumerate(lignes) if "⇔" in l.liens][0]
                self.assertTrue(all("=" in l.liens for l in lignes[:rang]), saisie)
                if r["etapes"][0]["titre"] != "Même base":
                    self.assertEqual(r["etapes"][0]["titre"], "Isoler l'exponentielle")
                    self.assertTrue(all(l == "⇔" for l in r["etapes"][0]["lignes"][0].liens))

    def test_base_choisie(self):
        for saisie, base in [("4^(-x)=2^6", 2), ("4^x=8", 2), ("3^x=9^(2x+3)", 3), ("8^(3x+2)=1/16", 2), ("(25^x)^2=5^0*5^(x+3)", 5),
                             ("4^x=16", 4), ("(1/2)^x=8", 2), ("9^x=1/3", 3), ("2^x=2*4^(x-1)", 2), ("1,5^x=2,25", F(3, 2)),
                             ("11^(2x+1)=1", 11), ("10^(2x)=0,01", 10), ("2^(x+7)=4^(5x+2)", 2)]:
            with self.subTest(saisie):
                self.assertEqual(corrige(saisie)["base"], F(base))

    def test_rien_a_dire_ou_methode_non_applicable(self):
        for saisie in SANS_E1:
            with self.subTest(saisie):
                s = el.analyser_saisie(saisie)
                self.assertIsNone(el.meme_base(s.g, s.d, s.inconnue))

    def test_ecriture_du_corrige(self):
        lignes = lambda s: [el.tex_chaine(l) for c in corrige(s)["etapes"] for l in c["lignes"]]
        self.assertEqual(lignes("3^(x+1)-27=0"), [
            r"3^{x + 1} - 27 = 0 \iff 3^{x + 1} = 27 \quad \text{(on isole le terme exponentiel)}",
            r"27 = 3^{3}",
            r"3^{x + 1} = 3^{3} \iff x + 1 = 3 \quad \text{(même base : a^A = a^B ⇔ A = B)} \iff x = 2"])
        self.assertEqual(lignes("2*3^(x-1)=18")[0], r"2 \cdot 3^{x - 1} = 18 \iff 3^{x - 1} = 9 \quad \text{(on isole le terme exponentiel)}")
        self.assertEqual(lignes("18=2*3^(x-1)")[0], r"18 = 2 \cdot 3^{x - 1} \iff 9 = 3^{x - 1} \quad \text{(on isole le terme exponentiel)}")
        self.assertEqual(lignes("2^(x+7)=4^(5x+2)")[0],
                         r"4^{5x + 2} = (2^{2})^{5x + 2} = 2^{2(5x + 2)} \quad \text{((aᵐ)ⁿ = aᵐⁿ)} = 2^{10x + 4}")
        self.assertEqual(lignes("(25^x)^2=5^0*5^(x+3)")[0],
                         r"(25^{x})^{2} = 25^{2x} \quad \text{((aᵐ)ⁿ = aᵐⁿ)} = (5^{2})^{2x} = 5^{4x} \quad \text{((aᵐ)ⁿ = aᵐⁿ)}")
        self.assertEqual(lignes("11^(2x+1)=1")[0], r"1 = 11^{0} \quad \text{(1 = a⁰)}")
        self.assertEqual(lignes("2^(x^2)*4^x=8")[-1],
                         r"2^{x^{2} + 2x} = 2^{3} \iff x^{2} + 2x = 3 \quad \text{(même base : a^A = a^B ⇔ A = B)} \iff x^{2} + 2x - 3 = 0 "
                         r"\iff (x + 3)(x - 1) = 0 \iff x = -3 \text{ ou } x = 1 \quad \text{(un produit est nul si l'un des facteurs est nul)}")

    def test_le_tex_du_corrige_vient_de_l_arbre(self):
        """Aucun \\ln ni \\log dans une équation à même base ; virgule décimale (SOC-12) ; aucun mot interdit ni tutoiement."""
        for saisie, _ in BATTERIE_E1:
            with self.subTest(saisie):
                for carte in corrige(saisie)["etapes"]:
                    self.assertIsNone(TUTOIEMENT.search(carte["titre"]))
                    for ligne in carte["lignes"]:
                        t = el.tex_chaine(ligne)
                        self.assertNotIn("\\ln", t)
                        self.assertNotIn("\\log", t)
                        self.assertIsNone(re.search(r"\d\.\d", t), t)
                        self.assertIsNone(TUTOIEMENT.search(re.sub(r"\\[a-z]+", " ", t)), t)

    def test_decimaux_gardes_tels_qu_ecrits(self):
        r = corrige("1,5^x=2,25")
        texte = " ".join(el.tex_chaine(l) for c in r["etapes"] for l in c["lignes"])
        self.assertIn("1{,}5", texte)
        self.assertIn("2{,}25 = 1{,}5^{2}", texte)


# ---------------------------------------------------------------------
# Étape 3 : méthode « logarithme » (E2), produit nul, premier degré à constantes logarithmiques
# ---------------------------------------------------------------------
def corriger(saisie):
    s = el.analyser_saisie(saisie)
    return el.corriger_equation(s.g, s.d, s.inconnue)




class TestLogarithme(unittest.TestCase):
    def test_batterie(self):
        for saisie, attendu in BATTERIE_E2:
            with self.subTest(saisie):
                r = corriger(saisie)
                self.assertIsNotNone(r)
                self.assertEqual([round(el.valeur(n), 3) + 0.0 for n in r["solutions"]], attendu)

    def test_oracle_les_solutions_verifient_l_equation_de_l_enonce(self):
        for saisie, attendu in BATTERIE_E2:
            with self.subTest(saisie):
                s = el.analyser_saisie(saisie)
                r = corriger(saisie)
                for n in r["solutions"]:
                    self.assertTrue(vrai(Eq(s.g, s.d), evaluer(n)), f"{saisie} : {el.tex(n)}")

    def test_aucune_autre_solution(self):
        """g − d change de signe exactement aux solutions annoncées sur [−12 ; 12] (équations à une exponentielle)."""
        for saisie, attendu in BATTERIE_E2:
            if len(attendu) == 0 or saisie in ("x=ln(3)", "2x=ln(0,1)"):
                continue
            with self.subTest(saisie):
                s = el.analyser_saisie(saisie)
                signes = []
                for i in range(-1200, 1201):
                    x = MP.mpf(i) / 100 + MP.mpf("0.000123")
                    signes.append(1 if evaluer(s.g, x) - evaluer(s.d, x) > 0 else -1)
                racines = sum(1 for a, b in zip(signes, signes[1:]) if a != b)
                self.assertEqual(racines, len([v for v in attendu if -12 < v < 12]))

    def test_formes_exactes(self):
        """La forme que donne la chaîne (Q11) : ni simplification de ln(25/37)/(−0,02), ni regroupement hors E3."""
        for saisie, exact in [
            ("2^x=100", r"\frac{2}{\log(2)}"), ("10^x=8", r"\log(8)"), ("e^x=7", r"\ln(7)"), ("3e^x=0,65", r"\ln\left(\frac{13}{60}\right)"),
            ("e^(-0,01x)=0,7", r"\frac{\ln(0{,}7)}{-0{,}01}"), ("37*e^(-0,02t)=25", r"\frac{\ln\left(\frac{25}{37}\right)}{-0{,}02}"),
            ("3^(x-1)=10", r"1 + \frac{1}{\log(3)}"), ("5^(2x+3)=7", r"\frac{\frac{\log(7)}{\log(5)} - 3}{2}"),
            ("10^(2x)=0,7", r"\frac{\log(0{,}7)}{2}"), ("10^(3x)=25", r"\frac{\log(25)}{3}"), ("12^x=49", r"\frac{\log(49)}{\log(12)}"),
            ("1,04^x=100", r"\frac{2}{\log(1{,}04)}"), ("4^(x-4)=20", r"4 + \frac{\log(20)}{\log(4)}"),
            ("2000*1,045^n=3805", r"\frac{\log(1{,}9025)}{\log(1{,}045)}"), ("0,8^n=0,5", r"\frac{\log(0{,}5)}{\log(0{,}8)}"),
            ("(1/2)^x=3", r"\frac{\log(3)}{\log\left(\frac{1}{2}\right)}"), ("2x=ln(0,1)", r"\frac{\ln(0{,}1)}{2}"),
            ("x=ln(3)", r"\ln(3)"), ("10^(-x)=8", r"-\log(8)"), ("e^x=1", "0"), ("4^(2x+1)=60", r"\frac{\frac{\log(60)}{\log(4)} - 1}{2}"),
            ("(10^(-x)-1)*(10^(-x)-8)=0", None)]:
            with self.subTest(saisie):
                r = corriger(saisie)
                if exact is None:
                    self.assertEqual([el.tex(n) for n in r["solutions"]], [r"-\log(8)", "0"])
                else:
                    self.assertEqual([el.tex(n) for n in r["solutions"]], [exact])

    def test_cartes(self):
        titres = lambda s: [c["titre"] for c in corriger(s)["etapes"]]
        self.assertEqual(titres("2^x=100"), ["Logarithme des deux membres"])
        self.assertEqual(titres("10^x=8"), ["Définition du logarithme"])
        self.assertEqual(titres("e^x=7"), ["Définition du logarithme"])
        self.assertEqual(titres("37*e^(-0,02t)=25"), ["Isoler l'exponentielle", "Définition du logarithme"])
        self.assertEqual(titres("2000*1,045^n=3805"), ["Isoler l'exponentielle", "Logarithme des deux membres"])
        self.assertEqual(titres("5^(8x)=-25"), ["Aucune solution"])
        self.assertEqual(titres("2*3^x=-6"), ["Isoler l'exponentielle", "Aucune solution"])
        self.assertEqual(titres("10^x*(10^x-4)=0"), ["Produit nul", "Facteur 1", "Facteur 2"])
        self.assertEqual(titres("2x=ln(0,1)"), ["Équation du premier degré"])
        self.assertEqual(titres("x=ln(3)"), [])
        self.assertEqual(corriger("x=ln(3)")["genre"], "lineaire")
        self.assertEqual(corriger("10^x*(10^x-4)=0")["genre"], "produit_nul")
        self.assertEqual(corriger("2^x=100")["genre"], "logarithme")

    def test_la_meme_base_garde_la_priorite(self):
        for saisie in ["3^x=27", "4^(2x)=8", "10^x=1/100", "2*3^(x-1)=18", "11^(2x+1)=1", "5^(3x+2)=(5^x)^2", "2^x=2*4^(x-1)"]:
            with self.subTest(saisie):
                self.assertEqual(corriger(saisie)["genre"], "meme_base")
        self.assertEqual(corriger("4^(2x)=8")["solutions"], [Nb(F(3, 4))])      # 2.23 c : base commune 2, pas de logarithme

    def test_ecriture_du_corrige(self):
        lignes = lambda s: [el.tex_chaine(l) for c in corriger(s)["etapes"] for l in c["lignes"]]
        self.assertEqual(lignes("2^x=100"), [
            r"2^{x} = 100 \iff \log(2^{x}) = \log(100) \quad \text{(log des deux membres)} \iff x \cdot \log(2) = \log(100) "
            r"\quad \text{(log(a^A) = A · log(a))} \iff x \cdot \log(2) = 2 \quad \text{(log(10ᵏ) = k)} \iff x = \frac{2}{\log(2)}"])
        self.assertEqual(lignes("5^(8x)=-25"), [r"5^{8x} > 0 \quad \text{(une exponentielle est strictement positive)}",
                                                r"-25 < 0 \quad \text{(aucune solution)}"])
        self.assertEqual(lignes("10^x=0"), [r"10^{x} > 0 \quad \text{(une exponentielle est strictement positive)}",
                                            r"10^{x} = 0 \quad \text{(aucune solution)}"])
        self.assertEqual(lignes("10^x*(10^x-4)=0")[0], r"10^{x} \cdot (10^{x} - 4) = 0 \iff 10^{x} = 0 \text{ ou } 10^{x} - 4 = 0 "
                                                       r"\quad \text{(un produit est nul si l'un des facteurs est nul)}")
        self.assertEqual(lignes("e^x=1"), [r"e^{x} = 1 \iff x = 0 \quad \text{(ln(1) = 0)}"])
        self.assertEqual(lignes("18=2*10^x+1")[0],
                         r"18 = 2 \cdot 10^{x} + 1 \iff 17 = 2 \cdot 10^{x} \quad \text{(on isole le terme exponentiel)} "
                         r"\iff \frac{17}{2} = 10^{x} \quad \text{(on isole le terme exponentiel)}")

    def test_propriete_a_chaque_etape_du_logarithme(self):
        for saisie, _ in BATTERIE_E2:
            with self.subTest(saisie):
                r = corriger(saisie)
                for carte in r["etapes"]:
                    for ligne in carte["lignes"]:
                        for p in ligne.props + [ligne.note]:
                            self.assertTrue(p is None or p in el.PROPRIETES, (saisie, p))
                        if carte["titre"] in ("Définition du logarithme", "Logarithme des deux membres"):
                            props = [p for p in ligne.props if p is not None]      # le simple échange des membres (100 = 2^x) n'a pas de propriété
                            if carte["titre"] == "Logarithme des deux membres":
                                self.assertEqual(props[:2], [el.PROP_LOG_DEUX_MEMBRES, el.PROP_LOG_PUISSANCE])
                            else:
                                self.assertIn(props[0], (el.PROP_DEFINITION_LOG, el.PROP_LN_UN))

    def test_chaines_les_equivalences_gardent_les_solutions(self):
        for saisie, attendu in BATTERIE_E2:
            with self.subTest(saisie):
                r = corriger(saisie)
                sols = [evaluer(n) for n in r["solutions"]]
                grille = [MP.mpf(i) / 4 + MP.mpf("0.0371") for i in range(-40, 41)]
                for carte in r["etapes"]:
                    for ligne in carte["lignes"]:
                        if "⇔" not in ligne.liens:
                            continue
                        for e in ligne.elements:
                            if not isinstance(e, (Eq, el.Ou)):
                                continue
                            facteur = r["genre"] == "produit_nul" and carte["titre"].startswith("Facteur")
                            for x in sols:
                                # une carte « Facteur k » n'est vraie qu'aux solutions de son facteur : elles se reconnaissent à la première équation
                                if facteur and not element_vrai(ligne.elements[0], x):
                                    self.assertFalse(element_vrai(e, x), (saisie, el.tex_element(e), x))
                                else:
                                    self.assertTrue(element_vrai(e, x), (saisie, el.tex_element(e), x))
                            for x in grille:
                                self.assertFalse(element_vrai(e, x), (saisie, el.tex_element(e), x))

    def test_chaines_les_egalites_sont_justes_pour_tout_x(self):
        for saisie, _ in BATTERIE_E2:
            with self.subTest(saisie):
                for carte in corriger(saisie)["etapes"]:
                    for ligne in carte["lignes"]:
                        if "=" in ligne.liens:
                            for x in ["0.37", "-1.4", "2.3"]:
                                v = [evaluer(e, MP.mpf(x)) for e in ligne.elements]
                                for w in v[1:]:
                                    self.assertLessEqual(abs(w - v[0]), MP.mpf("1e-20") * (1 + abs(v[0])), (saisie, el.tex_chaine(ligne)))

    def test_ln_pour_e_log_pour_le_reste(self):
        """EL-04/EL-05 : une équation en e^… n'écrit que \\ln ; les autres n'écrivent que \\log (base 10) ; log_a n'apparaît jamais ici."""
        for saisie, _ in BATTERIE_E2:
            with self.subTest(saisie):
                texte = " ".join(el.tex_chaine(l) for c in corriger(saisie)["etapes"] for l in c["lignes"])
                texte += " ".join(el.tex(n) for n in corriger(saisie)["solutions"])
                en_e = ("e^" in saisie or "exp(" in saisie or "ln(" in saisie) and "10" not in saisie
                if "log" in texte or "ln" in texte:
                    if en_e:
                        self.assertNotIn("\\log", texte)
                    else:
                        self.assertNotIn("\\ln", texte)
                self.assertNotIn("\\log_", texte)
                self.assertIsNone(re.search(r"\d\.\d", texte), texte)
                self.assertIsNone(TUTOIEMENT.search(re.sub(r"\\[a-z]+", " ", texte)), texte)

    def test_x_moins_a_donne_a_plus_le_second_membre(self):
        """x − a = c donne x = a + c (corrigé 2.23 d : x = 1 + 1/log(3)), jamais c + a ; x + a = c donne c − a."""
        ligne = lambda s: el.tex_chaine(corriger(s)["etapes"][-1]["lignes"][0])
        self.assertTrue(ligne("3^(x-1)=10").endswith(r"x - 1 = \frac{1}{\log(3)} \iff x = 1 + \frac{1}{\log(3)}"))
        self.assertTrue(ligne("4^(x-4)=20").endswith(r"x - 4 = \frac{\log(20)}{\log(4)} \iff x = 4 + \frac{\log(20)}{\log(4)}"))
        self.assertTrue(ligne("5^(2x-3)=7").endswith(
            r"2x - 3 = \frac{\log(7)}{\log(5)} \iff 2x = 3 + \frac{\log(7)}{\log(5)} \iff x = \frac{3 + \frac{\log(7)}{\log(5)}}{2}"))
        self.assertTrue(ligne("5^(2x+3)=7").endswith(
            r"2x + 3 = \frac{\log(7)}{\log(5)} \iff 2x = \frac{\log(7)}{\log(5)} - 3 \iff x = \frac{\frac{\log(7)}{\log(5)} - 3}{2}"))
        self.assertEqual([el.tex(n) for n in corriger("10^(x-3)=7")["solutions"]], [r"3 + \log(7)"])
        self.assertEqual([el.tex(n) for n in corriger("e^(x+3)=7")["solutions"]], [r"\ln(7) - 3"])

    def test_x_deja_isole_a_quand_meme_une_ligne_finale(self):
        """x = ln(3) : aucune carte de méthode, mais l'élève voit « S = {ln(3)}, soit x ≈ 1,099 » (l'adaptateur de l'étape 7 en fait la carte finale)."""
        r = corriger("x=ln(3)")
        self.assertEqual(r["etapes"], [])
        self.assertEqual([el.tex(n) for n in r["solutions"]], [r"\ln(3)"])
        self.assertEqual(el.tex_solution(r), r"S = \left\{\ln(3)\right\} \text{, soit } x \approx 1{,}099")
        self.assertEqual(el.tex_solution(corriger("ln(3)=x")), r"S = \left\{\ln(3)\right\} \text{, soit } x \approx 1{,}099")
        self.assertEqual(el.tex_solution(corriger("t=ln(0,5)")), r"S = \left\{\ln(0{,}5)\right\} \text{, soit } t \approx -0{,}693")

    def test_ligne_finale(self):
        for saisie, attendu in [
            ("2^x=100", r"S = \left\{\frac{2}{\log(2)}\right\} \text{, soit } x \approx 6{,}644"),
            ("3^x=27", r"S = \left\{3\right\}"), ("4^x=8", r"S = \left\{\frac{3}{2}\right\}"), ("5^(8x)=-25", r"S = \varnothing"),
            ("2^(x+1)=2*2^x", r"S = \mathbb{R}"), ("2^(x+1)=2^(x+3)", r"S = \varnothing"),
            ("2x=ln(0,1)", r"S = \left\{\frac{\ln(0{,}1)}{2}\right\} \text{, soit } x \approx -1{,}151"),
            ("(10^(-x)-1)*(10^(-x)-8)=0", r"S = \left\{-\log(8) \,;\, 0\right\} \text{, soit } x \approx -0{,}903 \text{ ou } x = 0"),
            ("2^(x^2)=2^(2x+1)", r"S = \left\{1 - \sqrt{2} \,;\, 1 + \sqrt{2}\right\} \text{, soit } x \approx -0{,}414 \text{ ou } x \approx 2{,}414"),
            ("2^(x^2)*4^x=8", r"S = \left\{-3 \,;\, 1\right\}"),
            ("2000*1,045^n=3805", r"S = \left\{\frac{\log(1{,}9025)}{\log(1{,}045)}\right\} \text{, soit } n \approx 14{,}612"),
            ("1,04^x=100", r"S = \left\{\frac{2}{\log(1{,}04)}\right\} \text{, soit } x \approx 117{,}417"),
            ("10^(x+3)=117000", r"S = \left\{\log(117\text{’}000) - 3\right\} \text{, soit } x \approx 2{,}068")]:
            with self.subTest(saisie):
                self.assertEqual(el.tex_solution(corriger(saisie)), attendu)

    def test_ligne_finale_partout_et_conforme(self):
        """Toute équation de la batterie a sa ligne finale : « S = … » ; un « ≈ » vient toujours après la valeur exacte, 3 décimales, virgule ;
        « soit » seulement s'il y a une valeur non rationnelle ; pas de point décimal ni de tutoiement."""
        for saisie, _ in BATTERIE_E1 + BATTERIE_E2 + BATTERIE_E4:
            with self.subTest(saisie):
                r = el.corriger_equation(*(lambda s: (s.g, s.d, s.inconnue))(el.analyser_saisie(saisie)))
                t = el.tex_solution(r)
                self.assertTrue(t.startswith("S = "), t)
                irrationnelle = bool(r["solutions"]) and any(el._const(n) is None for n in r["solutions"])
                self.assertEqual(r"\approx" in t, irrationnelle, t)
                self.assertEqual(r"\text{, soit }" in t, irrationnelle, t)
                if irrationnelle:
                    self.assertLess(t.index(r"\right\}"), t.index(r"\approx"))
                    for approx in re.findall(r"\\approx (-?[\d\\text{’}]+\{,\}\d+)", t):
                        self.assertEqual(len(approx.split("{,}")[1]), 3, approx)
                self.assertIsNone(re.search(r"\d\.\d", t), t)
                self.assertIsNone(TUTOIEMENT.search(re.sub(r"\\[a-z]+", " ", t)), t)

    def test_hors_programme_ou_autre_methode(self):
        for saisie in SANS_E2:
            with self.subTest(saisie):
                s = el.analyser_saisie(saisie)
                self.assertIsNone(el.corriger_equation(s.g, s.d, s.inconnue))

    def test_fractions_exactes(self):
        """Toute valeur exacte calculée s'écrit en fraction (jamais 1,9025 ni 2,5) ; les décimaux de l'énoncé gardent leur écriture."""
        for v, tex in [(F(761, 400), r"\frac{761}{400}"), (F(-1, 50), r"-\frac{1}{50}"), (F(13, 60), r"\frac{13}{60}"), (F(7), "7"),
                       (F(1, 3), r"\frac{1}{3}"), (F(5, 2), r"\frac{5}{2}"), (F(1, 8), r"\frac{1}{8}")]:
            with self.subTest(v):
                n = el._nb_exact(v)
                self.assertIsNone(n.dec)
                self.assertEqual(n.val, v)
                self.assertEqual(el.tex(n), tex)
        for saisie, ligne in [("e^(-0,01x)=0,7", r"\frac{\ln(0{,}7)}{-0{,}01}"), ("37*e^(-0,02t)=25", r"\frac{\ln\left(\frac{25}{37}\right)}{-0{,}02}")]:
            self.assertEqual(el.tex(corriger(saisie)["solutions"][0]), ligne)

    def test_decimaux_de_l_enonce_gardes_et_fractions_pour_les_entiers(self):
        """R13 : un énoncé qui contient un décimal garde le décimal (exposant compris) quand la valeur calculée est un décimal fini ;
        un calcul qui part d'entiers ou de puissances donne une fraction."""
        exact = lambda s, k=0: el.tex(corriger(s)["solutions"][k])
        self.assertEqual(exact("log(x)=-0,27"), r"10^{-0{,}27}")                    # pas 10^(−27/100)
        self.assertEqual(exact("log(x)=1,5"), r"10\sqrt{10}")
        self.assertEqual(el.tex_chaine(corriger("log(x)=2,5")["etapes"][0]["lignes"][0]),
                         r"\log(x) = 2{,}5 \iff x = 10^{2{,}5} = 100\sqrt{10} \quad \text{(définition du logarithme)}")
        self.assertEqual(exact("2000*1,045^n=3805"), r"\frac{\log(1{,}9025)}{\log(1{,}045)}")           # pas 761/400
        self.assertEqual(exact("1,5^x=2^(x+1)"), r"\frac{\log(2)}{\log(0{,}75)}")
        self.assertEqual(exact("3e^x=0,65"), r"\ln\left(\frac{13}{60}\right)")                          # pas un décimal fini : fraction
        lignes = lambda s: " ".join(el.tex_chaine(l) for c in corriger(s)["etapes"] for l in c["lignes"])
        self.assertIn(r"\log(x) = \frac{5}{2} \iff x = 10^{\frac{5}{2}} = 100\sqrt{10}", lignes("2log(x)-5=0"))     # entiers : fraction
        self.assertIn(r"x = 10^{-1} = \frac{1}{10}", lignes("log(x)=-1"))
        self.assertIn(r"\frac{17}{2} = 10^{x}", lignes("18=2*10^x+1"))
        self.assertEqual(el.tex(calculer("log_4(0,5)")["valeur"]), "-0{,}5")
        self.assertEqual(el.tex(calculer("log_4(1/2)")["valeur"]), r"-\frac{1}{2}")
        self.assertEqual(el.tex(calculer("log_9(27)")["valeur"]), r"\frac{3}{2}")
        self.assertFalse(el._DECIMAUX)                                                # le réglage est remis après chaque calcul

    def test_approximation_en_notation_scientifique(self):
        """3 décimales ; sous 10⁻³ et dès 10⁶ : notation scientifique (3,162 × 10⁻⁵) ; un rationnel n'a pas de « soit x ≈ »."""
        for v, attendu in [(6.644, "6{,}644"), (-0.693, "-0{,}693"), (0.0, "0{,}000"), (1e10, r"1 \times 10^{10}"), (1e-4, r"1 \times 10^{-4}"),
                           (3.1623e-5, r"3{,}162 \times 10^{-5}"), (-2.5e7, r"-2{,}500 \times 10^{7}"), (0.00099999, r"1 \times 10^{-3}"),
                           (123456.789, r"123\text{’}456{,}789"), (4.5e6, r"4{,}500 \times 10^{6}")]:
            with self.subTest(v):
                self.assertEqual(el.tex_approx(v), attendu)

    def test_base_inferieure_a_1_ne_boucle_pas(self):
        for saisie, v in [("(1/2)^x=3", -1.585), ("0,8^n=0,5", 3.106), ("0,5^x=8", -3.0), ("(1/3)^x=9", -2.0), ("0,5^x=3", -1.585)]:
            with self.subTest(saisie):
                r = corriger(saisie)
                self.assertEqual(round(el.valeur(r["solutions"][0]), 3) + 0.0, v)


# ---------------------------------------------------------------------
# Étape 4 : méthode « bases différentes » (E3)
# ---------------------------------------------------------------------


class TestBasesDifferentes(unittest.TestCase):
    def test_batterie(self):
        for saisie, attendu in BATTERIE_E3:
            with self.subTest(saisie):
                r = corriger(saisie)
                self.assertIsNotNone(r)
                self.assertEqual(r["genre"], "bases_differentes")
                self.assertEqual([round(el.valeur(n), 3) + 0.0 for n in r["solutions"]], [attendu])

    def test_oracle_la_solution_verifie_l_equation_de_l_enonce(self):
        for saisie, _ in BATTERIE_E3:
            with self.subTest(saisie):
                s = el.analyser_saisie(saisie)
                for n in corriger(saisie)["solutions"]:
                    self.assertTrue(vrai(Eq(s.g, s.d), evaluer(n)), f"{saisie} : {el.tex(n)}")

    def test_une_seule_solution(self):
        """g − d change de signe une seule fois sur [−12 ; 12] quand la solution y est, jamais sinon."""
        for saisie, attendu in BATTERIE_E3:
            with self.subTest(saisie):
                s = el.analyser_saisie(saisie)
                signes = [1 if evaluer(s.g, MP.mpf(i) / 100 + MP.mpf("0.000123")) - evaluer(s.d, MP.mpf(i) / 100 + MP.mpf("0.000123")) > 0 else -1
                          for i in range(-1200, 1201)]
                self.assertEqual(sum(1 for a, b in zip(signes, signes[1:]) if a != b), 1 if -12 < attendu < 12 else 0)

    def test_ecriture_du_corrige(self):
        """Le corrigé 2.24 a, b, c, ligne pour ligne."""
        lignes = lambda s: [el.tex_chaine(l) for c in corriger(s)["etapes"] for l in c["lignes"]]
        debut = lambda g, d, f, h: (rf"{g} = {d} \iff \log({g}) = \log({d}) \quad \text{{(log des deux membres)}} \iff {f} = {h} "
                                    r"\quad \text{(log(a^A) = A · log(a))}")
        self.assertEqual(lignes("2^(x-1)=3^x"), [
            debut("2^{x - 1}", "3^{x}", r"(x - 1) \cdot \log(2)", r"x \cdot \log(3)").replace(r"\log(2^{x - 1})", r"\log(2^{x - 1})")
            + r" \iff x \cdot \log(2) - \log(2) = x \cdot \log(3) \iff x(\log(2) - \log(3)) = \log(2) "
              r"\iff x = \frac{\log(2)}{\log(2) - \log(3)} \quad \text{(car } \log(2) - \log(3) \neq 0\text{)} "
              r"= \frac{\log(2)}{\log\left(\frac{2}{3}\right)} \quad \text{(log a − log b = log(a/b))}"])
        self.assertEqual(lignes("4^(x+1)=6^(3x)"), [
            debut("4^{x + 1}", "6^{3x}", r"(x + 1) \cdot \log(4)", r"3x \cdot \log(6)")
            + r" \iff x \cdot \log(4) + \log(4) = 3x \cdot \log(6) \iff \log(4) = x(3\log(6) - \log(4)) "
              r"\iff x = \frac{\log(4)}{3\log(6) - \log(4)} \quad \text{(car } 3\log(6) - \log(4) \neq 0\text{)} "
              r"= \frac{\log(4)}{\log(54)} \quad \text{(propriétés des logarithmes)}",
            r"3\log(6) - \log(4) = \log\left(\frac{6^{3}}{4}\right) \quad \text{(propriétés des logarithmes)} = \log(54)"])
        self.assertEqual(lignes("2^(x+4)=3^(x-1)"), [
            debut("2^{x + 4}", "3^{x - 1}", r"(x + 4) \cdot \log(2)", r"(x - 1) \cdot \log(3)")
            + r" \iff x \cdot \log(2) + 4\log(2) = x \cdot \log(3) - \log(3) \iff \log(3) + 4\log(2) = x(\log(3) - \log(2)) "
              r"\iff x = \frac{\log(3) + 4\log(2)}{\log(3) - \log(2)} \quad \text{(car } \log(3) - \log(2) \neq 0\text{)} "
              r"= \frac{\log(48)}{\log\left(\frac{3}{2}\right)} \quad \text{(propriétés des logarithmes)}",
            r"\log(3) + 4\log(2) = \log(3 \cdot 2^{4}) \quad \text{(propriétés des logarithmes)} = \log(48)",
            r"\log(3) - \log(2) = \log\left(\frac{3}{2}\right) \quad \text{(propriétés des logarithmes)}"])

    def test_formes_exactes_et_ligne_finale(self):
        for saisie, exact, finale in [
            ("2^(x-1)=3^x", r"\frac{\log(2)}{\log\left(\frac{2}{3}\right)}", r"x \approx -1{,}710"),
            ("4^(x+1)=6^(3x)", r"\frac{\log(4)}{\log(54)}", r"x \approx 0{,}348"),
            ("2^(x+4)=3^(x-1)", r"\frac{\log(48)}{\log\left(\frac{3}{2}\right)}", r"x \approx 9{,}548"),
            ("2^x=3^(x+1)", r"\frac{\log(3)}{\log\left(\frac{2}{3}\right)}", r"x \approx -2{,}710"),
            ("2^(x-1)=5^(x+1)", r"\frac{1}{\log\left(\frac{2}{5}\right)}", r"x \approx -2{,}513"),
            ("10^x=3^(x+1)", r"\frac{\log(3)}{1 - \log(3)}", r"x \approx 0{,}912")]:
            with self.subTest(saisie):
                r = corriger(saisie)
                self.assertEqual([el.tex(n) for n in r["solutions"]], [exact])
                self.assertEqual(el.tex_solution(r), r"S = \left\{" + exact + r"\right\} \text{, soit } " + finale)
        self.assertEqual(el.tex_solution(corriger("3^x=2^x")), r"S = \left\{0\right\}")

    def test_les_x_vont_du_cote_qui_laisse_la_constante_positive(self):
        """2.24 a : à gauche (x(log 2 − log 3) = log 2) ; b et c : à droite (log 4 = x(3 log 6 − log 4))."""
        lignes = lambda s: el.tex_chaine(corriger(s)["etapes"][0]["lignes"][0])
        self.assertIn(r"\iff x(\log(2) - \log(3)) = \log(2) \iff", lignes("2^(x-1)=3^x"))
        self.assertIn(r"\iff \log(4) = x(3\log(6) - \log(4)) \iff", lignes("4^(x+1)=6^(3x)"))
        self.assertIn(r"\iff \log(3) + 4\log(2) = x(\log(3) - \log(2)) \iff", lignes("2^(x+4)=3^(x-1)"))
        self.assertIn(r"\iff x(\log(3) - \log(2)) = 0 \iff x = 0 \quad \text{(car } \log(3) - \log(2) \neq 0\text{)}", lignes("3^x=2^x"))
        self.assertIn(r"\iff x(\log(3) - \log(2)) = \log(3) \iff", lignes("2^(-x)=3^(1-x)"))      # les termes positifs d'abord : jamais −log(2) + log(3)

    def test_regroupement_seulement_ici(self):
        """log a − log b = log(a/b) : prop de la dernière égalité quand il n'y a que des différences ; sinon « propriétés des logarithmes »."""
        derniere = lambda s: [p for p in corriger(s)["etapes"][0]["lignes"][0].props if p][-1]
        self.assertEqual(derniere("2^(x-1)=3^x"), el.PROP_LOG_QUOTIENT)
        self.assertEqual(derniere("2^x=3^(x+1)"), el.PROP_LOG_QUOTIENT)
        self.assertEqual(derniere("1,5^x=2^(x+1)"), el.PROP_LOG_QUOTIENT)
        self.assertEqual(derniere("2^(x+4)=3^(x-1)"), el.PROP_LOG_REGROUPER)
        self.assertEqual(derniere("4^(x+1)=6^(3x)"), el.PROP_LOG_REGROUPER)
        self.assertEqual(derniere("2^(x-1)=5^(x+1)"), el.PROP_LOG_REGROUPER)

    def test_log_d_une_puissance_de_10_est_un_nombre(self):
        """Q11 : log(10) = 1 et log(2 · 5) = log(10) = 1 ; plus aucun log(10) après la ligne (log(10ᵏ) = k)."""
        for saisie in ["10^x=3^(x+1)", "10^(x-1)=3^x", "0,1^x=2^(x+1)", "2^(x-1)=5^(x+1)"]:
            with self.subTest(saisie):
                r = corriger(saisie)
                texte = " ".join(el.tex_chaine(l) for c in r["etapes"] for l in c["lignes"]) + el.tex_solution(r)
                self.assertIn(el.PROP_LOG_10K, texte)
                apres = texte.split(el.PROP_LOG_10K, 1)[1]          # log(10) est écrit une fois (log(a^A) = A · log(a)), puis remplacé par 1
                self.assertNotIn(r"\log(10)", apres)
                self.assertNotIn(r"\log(0{,}1)", apres)

    def test_base_ecrite_conservee(self):
        texte = " ".join(el.tex_chaine(l) for c in corriger("(1/2)^x=3^(x+1)")["etapes"] for l in c["lignes"])
        self.assertIn(r"x \cdot \log\left(\frac{1}{2}\right) = x \cdot \log(3) + \log(3)", texte)
        self.assertNotIn("0{,}5", texte)

    def test_une_carte_et_des_proprietes_de_la_liste(self):
        for saisie, _ in BATTERIE_E3:
            with self.subTest(saisie):
                r = corriger(saisie)
                self.assertEqual([c["titre"] for c in r["etapes"]], ["Bases différentes"])
                lignes = r["etapes"][0]["lignes"]
                self.assertEqual(r["genre"], "bases_differentes")
                for ligne in lignes:
                    for p in ligne.props + [ligne.note]:
                        self.assertTrue(p is None or p in el.PROPRIETES or isinstance(p, el.Car), (saisie, p))
                props = [p for p in lignes[0].props if p is not None and not isinstance(p, el.Car)]
                if "e^" in saisie:
                    self.assertEqual(props[0], el.PROP_LN_DEUX_MEMBRES)
                    self.assertIn(el.PROP_LN_E, props)
                else:
                    self.assertEqual(props[0], el.PROP_LOG_DEUX_MEMBRES)
                    self.assertIn(el.PROP_LOG_PUISSANCE, props)
                for ligne in lignes[1:]:                       # lignes « car … » : des « = » seulement
                    self.assertEqual(set(ligne.liens), {"="})

    def test_equivalences_gardent_la_solution_et_rien_d_autre(self):
        for saisie, _ in BATTERIE_E3:
            with self.subTest(saisie):
                r = corriger(saisie)
                sols = [evaluer(n) for n in r["solutions"]]
                grille = [MP.mpf(i) / 4 + MP.mpf("0.0371") for i in range(-40, 41)]
                for ligne in r["etapes"][0]["lignes"]:
                    for e in ligne.elements:
                        if isinstance(e, (Eq, el.Ou)):
                            for x in sols:
                                self.assertTrue(element_vrai(e, x), (saisie, el.tex_element(e)))
                            for x in grille:
                                self.assertFalse(element_vrai(e, x), (saisie, el.tex_element(e), x))

    def test_les_egalites_sont_justes(self):
        """Chaque lien « = » : le membre de droite de l'élément précédent vaut l'élément suivant."""
        droite = lambda e: e.d if isinstance(e, Eq) else e
        for saisie, _ in BATTERIE_E3:
            with self.subTest(saisie):
                for ligne in corriger(saisie)["etapes"][0]["lignes"]:
                    for e, lien, suivant in zip(ligne.elements, ligne.liens, ligne.elements[1:]):
                        if lien == "=":
                            a, b = evaluer(droite(e), MP.mpf("0.37")), evaluer(suivant, MP.mpf("0.37"))
                            self.assertLessEqual(abs(a - b), MP.mpf("1e-20") * (1 + abs(a)), (saisie, el.tex_chaine(ligne)))

    def test_ln_avec_une_base_e_log_sinon_jamais_de_point_decimal(self):
        for saisie, _ in BATTERIE_E3:
            with self.subTest(saisie):
                r = corriger(saisie)
                texte = " ".join(el.tex_chaine(l) for c in r["etapes"] for l in c["lignes"]) + el.tex_solution(r)
                self.assertNotIn("\\log" if "e^" in saisie else "\\ln", texte)          # ln dès qu'une base est e, log sinon
                self.assertNotIn("\\log_", texte)
                self.assertIsNone(re.search(r"\d\.\d", texte), texte)
                self.assertIsNone(TUTOIEMENT.search(re.sub(r"\\[a-z]+", " ", texte)), texte)

    def test_redaction_avec_la_base_e(self):
        """ln aux deux membres dès qu'une base est e (ln(e^A) = A), les termes en x réunis, puis « car … ≠ 0 »."""
        lignes = lambda s: [el.tex_chaine(l) for c in corriger(s)["etapes"] for l in c["lignes"]]
        self.assertEqual(lignes("e^x=2^x"), [
            r"e^{x} = 2^{x} \iff \ln(e^{x}) = \ln(2^{x}) \quad \text{(ln des deux membres)} \iff x = x \cdot \ln(2) \quad \text{(ln(e^A) = A)} "
            r"\iff x - x \cdot \ln(2) = 0 \iff x(1 - \ln(2)) = 0 \iff x = 0 \quad \text{(car } 1 - \ln(2) \neq 0\text{)}"])
        self.assertEqual(lignes("e^x=2^(x+1)"), [
            r"e^{x} = 2^{x + 1} \iff \ln(e^{x}) = \ln(2^{x + 1}) \quad \text{(ln des deux membres)} \iff x = (x + 1) \cdot \ln(2) "
            r"\quad \text{(ln(e^A) = A)} \iff x = x \cdot \ln(2) + \ln(2) \iff x - x \cdot \ln(2) = \ln(2) \iff x(1 - \ln(2)) = \ln(2) "
            r"\iff x = \frac{\ln(2)}{1 - \ln(2)} \quad \text{(car } 1 - \ln(2) \neq 0\text{)}"])
        self.assertEqual(el.tex_solution(corriger("e^x=2^(x+1)")), r"S = \left\{\frac{\ln(2)}{1 - \ln(2)}\right\} \text{, soit } x \approx 2{,}259")
        self.assertEqual(el.tex_solution(corriger("e^x=2^x")), r"S = \left\{0\right\}")
        self.assertEqual(el.tex_solution(corriger("2*e^x=3^x")), r"S = \left\{\frac{\ln(2)}{\ln(3) - 1}\right\} \text{, soit } x \approx 7{,}029")

    def test_facteurs_constants(self):
        """k·a^f = m·b^h : log(k) + log(a^f) (log(ab) = log a + log b), puis le même regroupement ; log(10) = 1 ; les constantes de même base se réunissent."""
        lignes = lambda s: [el.tex_chaine(l) for c in corriger(s)["etapes"] for l in c["lignes"]]
        self.assertEqual(lignes("2*2^x=3^x")[0],
                         r"2 \cdot 2^{x} = 3^{x} \iff \log(2 \cdot 2^{x}) = \log(3^{x}) \quad \text{(log des deux membres)} "
                         r"\iff \log(2) + \log(2^{x}) = \log(3^{x}) \quad \text{(log(ab) = log a + log b)} "
                         r"\iff \log(2) + x \cdot \log(2) = x \cdot \log(3) \quad \text{(log(a^A) = A · log(a))} "
                         r"\iff x \cdot \log(2) + \log(2) = x \cdot \log(3) \iff \log(2) = x(\log(3) - \log(2)) "
                         r"\iff x = \frac{\log(2)}{\log(3) - \log(2)} \quad \text{(car } \log(3) - \log(2) \neq 0\text{)} "
                         r"= \frac{\log(2)}{\log\left(\frac{3}{2}\right)} \quad \text{(log a − log b = log(a/b))}")
        self.assertIn(r"\iff x \cdot \log(2) + 1 = x \cdot \log(3) \quad \text{(log(10ᵏ) = k)} \iff 1 = x(\log(3) - \log(2))", lignes("10*2^x=3^x")[0])
        self.assertIn(r"\iff x \cdot \log(2) = x \cdot \log(3)", lignes("2*2^(x-1)=3^x")[0])      # 2 · 2^(x−1) = 2^x : les constantes se compensent
        self.assertEqual(el.tex_solution(corriger("2*2^(x-1)=3^x")), r"S = \left\{0\right\}")
        un = corriger("1*2^x=3^(x+1)")                                             # un facteur 1 n'écrit ni log(1) ni la ligne log(ab)
        texte = " ".join(el.tex_chaine(l) for c in un["etapes"] for l in c["lignes"])
        self.assertNotIn(r"\log(1)", texte)
        self.assertNotIn(el.PROP_LOG_SOMME, texte)
        self.assertEqual([el.tex(n) for n in un["solutions"]], [el.tex(n) for n in corriger("2^x=3^(x+1)")["solutions"]])

    def test_signes_des_facteurs(self):
        for saisie in ["2*3^x=-5*2^x", "-2^x=3^(x+1)", "3^x=-2*2^(x+1)", "-3^x=2*5^x"]:
            with self.subTest(saisie):
                r = corriger(saisie)
                self.assertEqual([c["titre"] for c in r["etapes"]], ["Aucune solution"])
                self.assertEqual(r["solutions"], [])
                self.assertEqual(el.tex_solution(r), r"S = \varnothing")
                self.assertIn(el.PROP_EXPO_POSITIVE, [l.note for l in r["etapes"][0]["lignes"]])
        self.assertEqual([el.tex_chaine(l) for l in corriger("2*3^x=-5*2^x")["etapes"][0]["lignes"]], [
            r"2 \cdot 3^{x} > 0 \quad \text{(une exponentielle est strictement positive)}",
            r"-5 \cdot 2^{x} < 0 \quad \text{(aucune solution)}"])

    def test_chaque_division_est_justifiee(self):
        """Toute chaîne qui divise par un coefficient logarithmique le dit : « car D ≠ 0 », avec D qui n'est pas nul."""
        for saisie, _ in BATTERIE_E3:
            with self.subTest(saisie):
                ligne = corriger(saisie)["etapes"][0]["lignes"][0]
                cars = [(e, p) for e, p in zip(ligne.elements[1:], ligne.props) if isinstance(p, el.Car)]
                self.assertEqual(len(cars), 1)
                element, car = cars[0]
                self.assertIsInstance(element, Eq)
                self.assertEqual(element.g, X)
                self.assertGreater(abs(evaluer(car.expr)), MP.mpf("1e-6"))
                if isinstance(element.d, Op):
                    self.assertEqual(el.tex(element.d.b), el.tex(car.expr))          # le diviseur de la ligne est bien celui du « car »

    def test_les_autres_methodes_gardent_la_priorite(self):
        for saisie, genre in [("4^(x+1)=8^(2x)", "meme_base"), ("2^x=100", "logarithme"), ("2^x=8", "meme_base"), ("3^x=2", "logarithme"),
                              ("10^x*(10^x-4)=0", "produit_nul"), ("x=ln(3)", "lineaire")]:
            with self.subTest(saisie):
                self.assertEqual(corriger(saisie)["genre"], genre)
                s = el.analyser_saisie(saisie)
                self.assertIsNone(el.bases_differentes(s.g, s.d, s.inconnue))

    def test_hors_programme(self):
        for saisie in SANS_E3:
            with self.subTest(saisie):
                s = el.analyser_saisie(saisie)
                self.assertIsNone(el.bases_differentes(s.g, s.d, s.inconnue))
                self.assertIsNone(el.corriger_equation(s.g, s.d, s.inconnue))

    def test_ligne_finale_partout(self):
        for saisie, _ in BATTERIE_E3:
            with self.subTest(saisie):
                t = el.tex_solution(corriger(saisie))
                irrationnelle = el._const(corriger(saisie)["solutions"][0]) is None
                self.assertTrue(t.startswith("S = "), t)
                self.assertEqual(r"\approx" in t, irrationnelle, t)


# ---------------------------------------------------------------------
# Étape 5 : équations logarithmiques (E4)
# ---------------------------------------------------------------------


class TestLogarithmique(unittest.TestCase):
    def test_batterie(self):
        for saisie, attendu in BATTERIE_E4:
            with self.subTest(saisie):
                r = corriger(saisie)
                self.assertIsNotNone(r)
                self.assertEqual(r["genre"], "logarithmique")
                self.assertEqual([round(el.valeur(n), 3) + 0.0 for n in r["solutions"]], [round(v, 3) for v in attendu])

    def test_oracle_les_solutions_verifient_l_equation_de_l_enonce(self):
        for saisie, _ in BATTERIE_E4:
            with self.subTest(saisie):
                s = el.analyser_saisie(saisie)
                for n in corriger(saisie)["solutions"]:
                    self.assertTrue(vrai(Eq(s.g, s.d), evaluer(n)), f"{saisie} : {el.tex(n)}")

    def test_aucune_autre_solution(self):
        """g − d change de signe aux solutions annoncées seulement (là où le logarithme est défini, hors pôle de la base x)."""
        def difference(s, x):
            try:
                v = evaluer(s.g, x) - evaluer(s.d, x)
            except (ValueError, ZeroDivisionError):
                return None
            return None if isinstance(v, MP.mpc) or abs(v) > 50 else v
        for saisie, attendu in BATTERIE_E4:
            if any(0 < v <= 0.02 for v in attendu):
                continue                                    # une racine plus près de 0 que le pas de la grille (0,01) n'est pas encadrée
            with self.subTest(saisie):
                s = el.analyser_saisie(saisie)
                valeurs = [difference(s, MP.mpf(i) / 100 + MP.mpf("0.000123")) for i in range(-2000, 2001)]
                racines = sum(1 for a, b in zip(valeurs, valeurs[1:]) if a is not None and b is not None and (a > 0) != (b > 0))
                self.assertEqual(racines, len([v for v in attendu if -20 < v < 20]), saisie)

    def test_ecriture_du_corrige(self):
        lignes = lambda s: [el.tex_chaine(l) for c in corriger(s)["etapes"] for l in c["lignes"]]
        self.assertEqual(lignes("log(5-x)=8"), [
            r"\log(5 - x) = 8 \iff 5 - x = 10^{8} \quad \text{(définition du logarithme)} \iff x = 5 - 10^{8} = -99\text{’}999\text{’}995",
            r"5 - x = 10^{8} > 0 \quad \text{(le logarithme est bien défini)} \; \checkmark"])
        self.assertEqual(lignes("log(log(log(x)))=0"), [
            r"\log(\log(\log(x))) = 0 \iff \log(\log(x)) = 10^{0} = 1 \quad \text{(définition du logarithme)} "
            r"\iff \log(x) = 10^{1} = 10 \quad \text{(définition du logarithme)} "
            r"\iff x = 10^{10} \quad \text{(définition du logarithme)}"])
        self.assertEqual(lignes("log(x)=3"), [r"\log(x) = 3 \iff x = 10^{3} = 1\text{’}000 \quad \text{(définition du logarithme)}"])
        self.assertEqual(lignes("log(x)=-4"), [r"\log(x) = -4 \iff x = 10^{-4} \quad \text{(définition du logarithme)}"])      # notation scientifique, pas 0,0001
        self.assertEqual(lignes("log(x)=-1"), [r"\log(x) = -1 \iff x = 10^{-1} = \frac{1}{10} \quad \text{(définition du logarithme)}"])
        self.assertEqual(lignes("log(x)=-2"), [r"\log(x) = -2 \iff x = 10^{-2} = \frac{1}{100} \quad \text{(définition du logarithme)}"])
        self.assertEqual(lignes("log(x)=1,5"), [r"\log(x) = 1{,}5 \iff x = 10^{1{,}5} = 10\sqrt{10} \quad \text{(définition du logarithme)}"])
        self.assertEqual(lignes("log(x)=-0,27"), [r"\log(x) = -0{,}27 \iff x = 10^{-0{,}27} \quad \text{(définition du logarithme)}"])
        self.assertEqual(lignes("2log(x)-5=0"), [
            r"2\log(x) - 5 = 0 \iff 2\log(x) = 5 \quad \text{(on isole le logarithme)} \iff \log(x) = \frac{5}{2} \quad \text{(on isole le logarithme)}",
            r"\log(x) = \frac{5}{2} \iff x = 10^{\frac{5}{2}} = 100\sqrt{10} \quad \text{(définition du logarithme)}"])
        self.assertEqual(lignes("ln(x)=3"), [r"\ln(x) = 3 \iff x = e^{3} \quad \text{(définition du logarithme)}"])
        self.assertEqual(lignes("log2(x)=4"), [r"\log_{2}(x) = 4 \iff x = 2^{4} = 16 \quad \text{(définition du logarithme)}"])
        self.assertEqual(lignes("2log_3(x)=10")[1], r"\log_{3}(x) = 5 \iff x = 3^{5} = 243 \quad \text{(définition du logarithme)}")
        self.assertEqual(lignes("log_x(256)=4"), [
            r"x > 0 \text{ et } x \neq 1 \quad \text{(une base de logarithme est strictement positive et différente de 1)}",
            r"\log_{x}(256) = 4 \iff x^{4} = 256 \quad \text{(définition du logarithme)} \iff x = 4 \text{ ou } x = -4",
            r"x = 4 \quad \text{(seule la solution positive convient)}"])
        self.assertEqual(lignes("log(x^2)=2"), [
            r"\log(x^{2}) = 2 \iff x^{2} = 10^{2} = 100 \quad \text{(définition du logarithme)} \iff x^{2} - 100 = 0 \iff (x + 10)(x - 10) = 0 "
            r"\iff x = -10 \text{ ou } x = 10 \quad \text{(un produit est nul si l'un des facteurs est nul)}",
            r"x^{2} = 10^{2} > 0 \quad \text{(le logarithme est bien défini)} \; \checkmark"])

    def test_formes_exactes_et_ligne_finale(self):
        for saisie, attendu in [
            ("log(x)=3", r"S = \left\{1\text{’}000\right\}"), ("log(x)=1,5", r"S = \left\{10\sqrt{10}\right\} \text{, soit } x \approx 31{,}623"),
            ("log(x)=-0,27", r"S = \left\{10^{-0{,}27}\right\} \text{, soit } x \approx 0{,}537"),
            ("log(x)=-4", r"S = \left\{10^{-4}\right\}"), ("log(log(x))=1", r"S = \left\{10^{10}\right\}"), ("log(x)=-1", r"S = \left\{\frac{1}{10}\right\}"),
            ("ln(x)=3", r"S = \left\{e^{3}\right\} \text{, soit } x \approx 20{,}086"), ("ln(x)=1", r"S = \left\{e\right\} \text{, soit } x \approx 2{,}718"),
            ("ln(x)=0", r"S = \left\{1\right\}"), ("ln(2-x)=1", r"S = \left\{2 - e\right\} \text{, soit } x \approx -0{,}718"),
            ("log(x^2)=2", r"S = \left\{-10 \,;\, 10\right\}"), ("log(x^2+x+3)=0", r"S = \varnothing"),
            ("log(5-x)=8", r"S = \left\{-99\text{’}999\text{’}995\right\}"), ("log_x(256)=4", r"S = \left\{4\right\}"),
            ("2log(x)-5=0", r"S = \left\{100\sqrt{10}\right\} \text{, soit } x \approx 316{,}228")]:
            with self.subTest(saisie):
                self.assertEqual(el.tex_solution(corriger(saisie)), attendu)

    def test_cartes(self):
        titres = lambda s: [c["titre"] for c in corriger(s)["etapes"]]
        self.assertEqual(titres("log(x)=3"), ["Définition du logarithme"])
        self.assertEqual(titres("2log(x)-5=0"), ["Isoler le logarithme", "Définition du logarithme"])
        self.assertEqual(titres("log(5-x)=8"), ["Définition du logarithme", "Vérification"])
        self.assertEqual(titres("log(log(log(x)))=0"), ["Définition du logarithme"])               # pas de vérification pour les logarithmes imbriqués
        self.assertEqual(titres("log(log(x-1))=0"), ["Définition du logarithme"])
        self.assertEqual(titres("log_x(256)=4"), ["Condition", "Définition du logarithme"])
        self.assertEqual(titres("log(x^2+x+3)=0"), ["Définition du logarithme"])                    # S = ∅ : rien à vérifier
        self.assertEqual(corriger("log(x^2+x+3)=0")["remarque"], "Δ < 0 : l'équation n'a aucune solution réelle.")

    def test_verification_pour_chaque_argument_avec_inconnue(self):
        """EL-09 : un logarithme dont l'argument n'est pas x seul a sa vérification « > 0 » ; elle porte sur l'argument de l'énoncé."""
        for saisie in ["log(5-x)=8", "log(2x+1)=3", "log(x^2)=2", "log(x^2-3x)=1", "ln(2-x)=1", "log(-x)=2"]:
            with self.subTest(saisie):
                r = corriger(saisie)
                self.assertEqual(r["etapes"][-1]["titre"], "Vérification")
                verification = r["etapes"][-1]["lignes"][0]
                self.assertEqual(verification.note, el.PROP_BIEN_DEFINI)
                positif = verification.elements[0]
                self.assertIsInstance(positif, el.Positif)
                for x in r["solutions"]:
                    self.assertGreater(evaluer(positif.expr, evaluer(x)), 0)            # l'argument, calculé en la solution, est > 0

    def test_base_inconnue_rejette_la_solution_negative(self):
        r = corriger("log_x(256)=4")
        self.assertEqual([el.tex(n) for n in r["solutions"]], ["4"])
        self.assertIn("x = -4", " ".join(el.tex_chaine(l) for l in r["etapes"][1]["lignes"]))
        self.assertEqual(r["etapes"][1]["lignes"][1].note, el.PROP_SEULE_POSITIVE)
        self.assertEqual(r["etapes"][0]["lignes"][0].note, el.PROP_BASE_LOG)
        for saisie in ["log_x(8)=3", "log_x(1/8)=3"]:                                        # exposant impair : pas de solution négative à écarter
            self.assertEqual(len(corriger(saisie)["etapes"][1]["lignes"]), 1)

    def test_log_de_x_carre_se_resout_par_la_definition(self):
        """EL-10 : log(x²) = 2 donne ±10 ; jamais 2 log|x|."""
        r = corriger("log(x^2)=2")
        texte = " ".join(el.tex_chaine(l) for c in r["etapes"] for l in c["lignes"])
        self.assertEqual([el.tex(n) for n in r["solutions"]], ["-10", "10"])
        self.assertNotIn("|", texte)
        self.assertNotIn(r"\left|", texte)

    def test_proprietes_et_tex(self):
        for saisie, _ in BATTERIE_E4:
            with self.subTest(saisie):
                r = corriger(saisie)
                texte = " ".join(el.tex_chaine(l) for c in r["etapes"] for l in c["lignes"]) + el.tex_solution(r)
                for carte in r["etapes"]:
                    for ligne in carte["lignes"]:
                        for p in ligne.props + [ligne.note]:
                            self.assertTrue(p is None or p in el.PROPRIETES, (saisie, p))
                self.assertIsNone(re.search(r"\d\.\d", texte), texte)
                self.assertIsNone(TUTOIEMENT.search(re.sub(r"\\[a-z]+", " ", texte)), texte)
                self.assertNotIn("\\log" if "ln" in saisie and "log" not in saisie else "\\ln", texte)

    def test_equivalences_gardent_les_solutions_et_rien_d_autre(self):
        grille = [MP.mpf(i) / 4 + MP.mpf("0.0371") for i in range(-40, 41)]
        for saisie, _ in BATTERIE_E4:
            with self.subTest(saisie):
                r = corriger(saisie)
                sols = [evaluer(n) for n in r["solutions"]]
                for carte in r["etapes"]:
                    for ligne in carte["lignes"]:
                        for e in ligne.elements:
                            if isinstance(e, (Eq, el.Ou)):
                                if carte["titre"] == "Définition du logarithme" and isinstance(e, Eq) and e.g == X and ligne.note == el.PROP_SEULE_POSITIVE:
                                    continue
                                for x in sols:
                                    self.assertTrue(element_vrai(e, x), (saisie, el.tex_element(e), x))

    def test_ecritures_intermediaires_egales(self):
        """Eq(g, d, milieu) : 10^3 = 1000 ; chaque écriture intermédiaire vaut d."""
        for saisie, _ in BATTERIE_E4:
            with self.subTest(saisie):
                for carte in corriger(saisie)["etapes"]:
                    for ligne in carte["lignes"]:
                        for e in ligne.elements:
                            if isinstance(e, Eq):
                                for m in e.milieu:
                                    a, b = evaluer(m), evaluer(e.d)
                                    self.assertLessEqual(abs(a - b), MP.mpf("1e-20") * (1 + abs(b)), (saisie, el.tex_element(e)))

    def test_les_autres_methodes_gardent_la_priorite(self):
        for saisie, genre in [("x=ln(3)", "lineaire"), ("2x=ln(0,1)", "lineaire"), ("10^x=8", "logarithme"), ("4^(x+1)=6^(3x)", "bases_differentes")]:
            with self.subTest(saisie):
                self.assertEqual(corriger(saisie)["genre"], genre)
                s = el.analyser_saisie(saisie)
                self.assertIsNone(el.logarithmique(s.g, s.d, s.inconnue))

    def test_pas_encore(self):
        """Hors de la méthode : plusieurs logarithmes, second membre avec un logarithme, base inconnue non entière, trinôme à coefficients non entiers."""
        for saisie in ["log(x)=log(5)", "log(x)+log(x-1)=1", "log_x(2)=3", "log_x(256)=0,5", "log_x(1)=2", "log(x^2)=-1", "log(x^3)=2", "x*log(x)=1",
                       "log(x)=x", "log(2x+1)=ln(3)"]:
            with self.subTest(saisie):
                s = el.analyser_saisie(saisie)
                self.assertIsNone(el.logarithmique(s.g, s.d, s.inconnue))


# ---------------------------------------------------------------------
# Étape 6 : calcul de log_a(y) (C1)
# ---------------------------------------------------------------------
def calculer(saisie):
    return el.calculer_logarithme(el.analyser_saisie(saisie).g)




class TestCalculLogarithme(unittest.TestCase):
    def test_batterie(self):
        for saisie, attendu in BATTERIE_C1:
            with self.subTest(saisie):
                r = calculer(saisie)
                self.assertIsNotNone(r)
                self.assertEqual(r["genre"], "calcul")
                if isinstance(attendu, F):
                    self.assertEqual(el._const(r["valeur"]), attendu)
                else:
                    self.assertIsNone(el._const(r["valeur"]))
                    self.assertEqual(round(el.valeur(r["valeur"]), 3), attendu)

    def test_oracle_la_valeur_est_celle_du_logarithme_de_l_enonce(self):
        for saisie, _ in BATTERIE_C1:
            with self.subTest(saisie):
                r = calculer(saisie)
                a, b = evaluer(el.analyser_saisie(saisie).g), evaluer(r["valeur"])
                self.assertLessEqual(abs(a - b), MP.mpf("1e-25") * (1 + abs(a)), (saisie, a, b))

    def test_chaque_egalite_est_juste(self):
        for saisie, _ in BATTERIE_C1:
            with self.subTest(saisie):
                for carte in calculer(saisie)["etapes"]:
                    for ligne in carte["lignes"]:
                        for e, lien, suivant in zip(ligne.elements, ligne.liens, ligne.elements[1:]):
                            a, b = evaluer(e), evaluer(suivant)
                            self.assertLessEqual(abs(a - b), MP.mpf("1e-25") * (1 + abs(a)), (saisie, el.tex_chaine(ligne)))

    def test_ecriture_du_corrige(self):
        lignes = lambda s: [el.tex_chaine(l) for c in calculer(s)["etapes"] for l in c["lignes"]]
        self.assertEqual(lignes("log(1000000)"), [r"1\text{’}000\text{’}000 = 10^{6}",
                                                  r"\log(1\text{’}000\text{’}000) = \log(10^{6}) = 6 \quad \text{(log(10ᵏ) = k)}"])
        self.assertEqual(lignes("log_8(64)"), [r"64 = 8^{2}", r"\log_{8}(64) = \log_{8}(8^{2}) = 2 \quad \text{(log_a(a^k) = k)}"])
        self.assertEqual(lignes("log_5(0,2)"), [r"0{,}2 = 5^{-1}", r"\log_{5}(0{,}2) = \log_{5}(5^{-1}) = -1 \quad \text{(log_a(a^k) = k)}"])
        self.assertEqual(lignes("log_4(sqrt(2))"), [
            r"\sqrt{2} = 2^{\frac{1}{2}} = \left(4^{\frac{1}{2}}\right)^{\frac{1}{2}} = 4^{\frac{1}{4}}",
            r"\log_{4}(\sqrt{2}) = \log_{4}\left(4^{\frac{1}{4}}\right) = \frac{1}{4} \quad \text{(log_a(a^k) = k)}"])
        self.assertEqual(lignes("log(sqrt(10))")[0], r"\sqrt{10} = 10^{\frac{1}{2}}")
        self.assertEqual(lignes("log_8(2)")[0], r"2 = 8^{\frac{1}{3}}")                                  # exposant 1 : pas de (8^(1/3))^1
        self.assertEqual(lignes("log_9(27)")[0], r"27 = 3^{3} = \left(9^{\frac{1}{2}}\right)^{3} = 9^{\frac{3}{2}}")
        self.assertEqual(lignes("log_2(sqrt(8))")[0], r"\sqrt{8} = 2^{\frac{3}{2}}")                      # la base est déjà la racine primitive
        self.assertEqual(lignes("log_2(50)"), [
            r"50 \text{ n'est pas une puissance de } 2 \quad (2^{5} = 32 < 50 < 64 = 2^{6})",
            r"\log_{2}(50) = \frac{\log(50)}{\log(2)} \quad \text{(changement de base)}"])
        self.assertEqual(lignes("ln(e^3)"), [r"\ln(e^{3}) = 3 \quad \text{(ln(e^k) = k)}"])

    def test_ligne_finale(self):
        for saisie, attendu in [("log_8(64)", r"\log_{8}(64) = 2"), ("log_4(sqrt(2))", r"\log_{4}(\sqrt{2}) = \frac{1}{4}"),
                                ("log_2(50)", r"\log_{2}(50) = \frac{\log(50)}{\log(2)} \approx 5{,}644"), ("log(50)", r"\log(50) \approx 1{,}699"),
                                ("ln(7)", r"\ln(7) \approx 1{,}946"), ("log_5(0,3)", r"\log_{5}(0{,}3) = \frac{\log(0{,}3)}{\log(5)} \approx -0{,}748"),
                                ("log_2(1/8)", r"\log_{2}\left(\frac{1}{8}\right) = -3")]:
            with self.subTest(saisie):
                self.assertEqual(el.tex_resultat(calculer(saisie)), attendu)

    def test_encadrement_entre_deux_puissances_consecutives(self):
        for y, a in [(F(50), F(2)), (F(10), F(3)), (F(3, 10), F(5)), (F(1, 3), F(2)), (F(7), F(10)), (F(1, 1000) + F(1, 7), F(10)), (F(5, 2), F(3, 2))]:
            with self.subTest((y, a)):
                j, bas, haut = el._encadrement(y, a)
                self.assertTrue(bas < y < haut and haut == bas * a and bas == a ** j)

    def test_changement_de_base_seulement_hors_base_10_et_e(self):
        for saisie, avec in [("log_2(50)", True), ("log_3(10)", True), ("log(50)", False), ("ln(7)", False)]:
            with self.subTest(saisie):
                props = [p for c in calculer(saisie)["etapes"] for l in c["lignes"] for p in l.props]
                self.assertEqual(el.PROP_CHANGEMENT_DE_BASE in props, avec)

    def test_proprietes_de_la_liste_pas_de_point_decimal_pas_de_tutoiement(self):
        for saisie, _ in BATTERIE_C1:
            with self.subTest(saisie):
                r = calculer(saisie)
                texte = " ".join(el.tex_chaine(l) for c in r["etapes"] for l in c["lignes"]) + el.tex_resultat(r)
                for c in r["etapes"]:
                    for l in c["lignes"]:
                        for p in l.props + [l.note]:
                            self.assertTrue(p is None or p in el.PROPRIETES, (saisie, p))
                self.assertIsNone(re.search(r"\d\.\d", texte), texte)
                self.assertIsNone(TUTOIEMENT.search(re.sub(r"\\[a-z]+", " ", texte)), texte)

    def test_pas_encore(self):
        """Hors de la méthode : plus d'un logarithme, argument non rationnel, nul ou négatif, base e dans un argument autre que e^k."""
        for saisie in ["2log(5)", "log(2)+log(3)", "log(e^2)", "log(0)", "log(-3)", "log_2(0)", "ln(2e)", "ln(sqrt(e))", "log(2)/log(3)", "log(5)^2",
                       "sqrt(log(2))"]:
            with self.subTest(saisie):
                try:
                    g = el.analyser_saisie(saisie).g
                except ErreurSaisie:
                    continue
                self.assertIsNone(el.calculer_logarithme(g))


class TestMessagesNonResolu(unittest.TestCase):
    """EL-11 : deux messages. « ne se résout pas avec les méthodes du cours » seulement pour un vrai hors-programme ;
    « ne traite pas encore » pour une forme du programme que l'outil ne gère pas encore."""
    HORS_PROGRAMME = cas_el.HORS_PROGRAMME
    PAS_ENCORE = cas_el.PAS_ENCORE

    def message(self, saisie):
        s = el.analyser_saisie(saisie)
        self.assertIsNone(el.corriger_equation(s.g, s.d, s.inconnue), saisie)
        return el.message_non_resolu(s.g, s.d, s.inconnue)

    def test_textes_exacts(self):
        self.assertEqual(el.MESSAGE_HORS_PROGRAMME, "Cette équation ne se résout pas avec les méthodes du cours.")
        self.assertEqual(el.MESSAGE_PAS_ENCORE, "Cet outil ne traite pas encore ce type d'équation.")

    def test_vrais_hors_programme(self):
        for saisie in self.HORS_PROGRAMME:
            with self.subTest(saisie):
                self.assertEqual(self.message(saisie), el.MESSAGE_HORS_PROGRAMME)

    def test_formes_du_programme_pas_encore_gerees(self):
        for saisie in self.PAS_ENCORE:
            with self.subTest(saisie):
                self.assertEqual(self.message(saisie), el.MESSAGE_PAS_ENCORE)

    def test_aucun_hors_programme_ne_donne_de_solution(self):
        for saisie, _ in BATTERIE_E1 + BATTERIE_E2 + BATTERIE_E3 + BATTERIE_E4:
            with self.subTest(saisie):
                s = el.analyser_saisie(saisie)
                self.assertFalse(el.hors_programme(s.g, s.d, s.inconnue), saisie)


class TestNotationSuisse(unittest.TestCase):
    """Q5 (14.10.2026), Q12 (26.10.2026) : ’ dès 4 chiffres sur la partie entière seulement (1’234,567), virgule décimale ;
    saisie de ' et ’ ; « 1 000 » refusé. Fonctions de moteur/nombres.py."""

    def test_affichage(self):
        for n, attendu in [(Nb(1000), "1\\text{’}000"), (Nb(999), "999"), (Nb(F(-99999995)), "-99\\text{’}999\\text{’}995"),
                           (Nb(1234567), "1\\text{’}234\\text{’}567"), (Nb(F(3, 2)), "\\frac{3}{2}"),
                           (Nb(F(1000, 3)), "\\frac{1\\text{’}000}{3}"), (Nb(F(-1, 16)), "-\\frac{1}{16}"), (Nb(0), "0"),
                           (Nb(F(1234567, 1000), "1234,567"), "1\\text{’}234{,}567"), (Nb(F(1, 10000), "0,0001"), "0{,}0001"),
                           (Nb(F(12345678901, 100000), "123456,78901"), "123\\text{’}456{,}78901")]:
            with self.subTest(attendu):
                self.assertEqual(el.tex(n), attendu)

    def test_equations_avec_grands_nombres(self):
        for saisie, attendu in [("2000*1,045^n=3805", "2\\text{’}000 \\cdot 1{,}045^{n} = 3\\text{’}805"),
                                ("log(5-x)=10^8", "\\log(5 - x) = 10^{8}"), ("x=5-100000000", "x = 5 - 100\\text{’}000\\text{’}000"),
                                ("7200000*1,03^n=746000000", "7\\text{’}200\\text{’}000 \\cdot 1{,}03^{n} = 746\\text{’}000\\text{’}000"),
                                ("10^x=0,0001", "10^{x} = 0{,}0001"), ("x=12345,6789", "x = 12\\text{’}345{,}6789")]:
            with self.subTest(saisie):
                self.assertEqual(el.tex_saisie(*el.lire_membres(saisie)), attendu)

    def test_saisie_avec_apostrophes(self):
        for s, v in [("1'000", F(1000)), ("1’000", F(1000)), ("1'234'567", F(1234567)), ("12’345", F(12345)), ("1’234,567", F(1234567, 1000)),
                     ("1'234.5", F(12345, 10)), ("999", F(999)), ("1234567", F(1234567)), ("0,0001", F(1, 10000))]:
            with self.subTest(s):
                self.assertEqual(lire(s), Nb(v))
        self.assertEqual(el.tex(lire("1’234,567")), "1\\text{’}234{,}567")      # la saisie est réécrite en notation suisse

    def test_espace_dans_un_nombre_refuse(self):
        for s in ["1 000", "10 000", "7 200 000x=1", "x=1 000", "2 100", "1\u00a0000"]:
            with self.subTest(s):
                with self.assertRaises(ErreurSaisie) as c:
                    el.lire_membres(s)
                self.assertEqual(str(c.exception), "Pas d'espace dans un nombre : écrivez 1000 ou 1’000.")
        # deux nombres qui ne ressemblent pas à des milliers : l'ancien message
        with self.assertRaises(ErreurSaisie) as c:
            el.lire_membres("2 3x = 5")
        self.assertIn("Un nombre ne peut pas suivre", str(c.exception))

    def test_apostrophes_mal_placees(self):
        for s in ["1'00", "1'0000", "12'34", "1'", "1’00x=1", "x=1'2"]:
            with self.subTest(s):
                with self.assertRaises(ErreurSaisie) as c:
                    el.lire_membres(s)
                self.assertEqual(str(c.exception), "Une apostrophe dans un nombre est suivie d'exactement 3 chiffres : 1’000.")

    def test_jamais_d_apostrophe_droite_ni_de_point_decimal_dans_le_tex(self):
        for s in ["1'000x=1'234,5", "x=1’234.5678", "10^x=0.0001", "2000*1.045^n=3805"]:
            t = el.tex_saisie(*el.lire_membres(s))
            self.assertNotIn("'", t)
            self.assertIsNone(re.search(r"\d\.\d", t), t)

    def test_les_corriges_n_ecrivent_pas_de_separateur_dans_les_decimales_ni_sous_4_chiffres(self):
        for saisie, _ in BATTERIE_E1:
            for carte in corrige(saisie)["etapes"]:
                for ligne in carte["lignes"]:
                    t = el.tex_chaine(ligne)
                    self.assertIsNone(re.search(r"\{,\}\d*\\text\{’\}", t), t)             # pas de ’ après la virgule
                    self.assertIsNone(re.search(r"(?<![\d])\d{1,3}\\text\{’\}\d{1,2}(?!\d)", t), t)      # groupes de 3 chiffres exactement


class TestSource(unittest.TestCase):
    def source(self, nom):
        with open(os.path.join(RACINE, "exponentielles-logarithmes", nom), encoding="utf-8") as f:
            return f.read()

    def test_le_tex_ne_vient_jamais_de_sympy(self):
        """EL-04 : aucun appel à un écrivain TeX de SymPy ni à la conversion SymPy → arbre, et pas d'import de SymPy pour écrire."""
        for nom in ["exp_log.py", "resoudre_el.py"]:
            s = self.source(nom)
            self.assertIsNone(re.search(r"\blatex\s*\(", s), nom)
            self.assertNotIn("arbre_depuis_sympy", s, nom)
            self.assertNotIn("sp.latex", s, nom)
            self.assertNotIn("print_latex", s, nom)
            self.assertNotIn("charger_sympy", s, nom)
            self.assertNotIn("import sympy", s, nom)


if __name__ == "__main__":
    unittest.main()
