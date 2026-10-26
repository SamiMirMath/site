"""T33 (étape 1) — Outil « Exponentielles et logarithmes » : lecture de la saisie, arbre, TeX, aperçu (EL-03, EL-04, EL-05 pour la lecture).

Les étapes suivantes ajouteront ici la résolution (EL-01, EL-02, EL-06 à EL-11)."""
import json
import os
import re
import unittest
from fractions import Fraction as F

import mpmath as mp

from moteurs import RACINE
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


# (saisie, solutions exactes) : exercices 2.13 a-o du polycopié et exemples p. 22-23
BATTERIE_E1 = [
    ("7^(2x+1)=7^9", [F(4)]), ("3^x=27", [F(3)]), ("10^x=1/100", [F(-2)]), ("2*3^(x-1)=18", [F(3)]),
    ("4^(-x)=2^6", [F(-3)]), ("4^x=8", [F(3, 2)]), ("3^x=9^(2x+3)", [F(-2)]), ("10^(x+2)=(10^2)^x", [F(2)]),
    ("5^(3x+2)=(5^x)^2", [F(-2)]), ("11^(2x+1)=1", [F(-1, 2)]), ("2^(x+7)=4^(5x+2)", [F(1, 3)]),
    ("8^(3x+2)=1/16", [F(-10, 9)]), ("(25^x)^2=5^0*5^(x+3)", [F(1)]), ("2^x=2*4^(x-1)", [F(1)]),
    ("2^(x^2)*4^x=8", [F(-3), F(1)]),
    ("3^(x+1)-27=0", [F(2)]), ("10^(2x)=0,01", [F(-1)]), ("3*2^(x^2+1)=96", [F(-2), F(2)]), ("4^(3x+1)=8", [F(1, 6)]),
    # autres formes de la même méthode
    ("18=2*3^(x-1)", [F(3)]), ("3(2^x+1)=9", [F(1)]), ("-2^x=-8", [F(3)]), ("5-2^x=1", [F(2)]), ("2^x/4=2", [F(3)]),
    ("(1/2)^x=8", [F(-3)]), ("9^x=1/3", [F(-1, 2)]), ("2^(x/2)=8", [F(6)]), ("2^(-x)=8", [F(-3)]), ("4^x=16", [F(2)]),
    ("1,5^x=2,25", [F(2)]), ("2^(x^2)=8^x", [F(0), F(3)]), ("2^(x+1)=2*2^x", None), ("2^(x+1)=2^(x+3)", []),
    ("2^(x^2)=2^(x-5)", []), ("9^(x^2)=3^(x+1)", [F(-1, 2), F(1)]),
]
SANS_E1 = ["3^x=20", "2^x=0", "2^x=-4", "5^(8x)=-25", "e^x=7", "2^x+3^x=5", "x^2=4", "log(x)=2", "3^x=2^x", "2^x=3^(x+1)",
           "2^(x^3)=8", "2^(x^2)*3^x=6", "x*2^x=8", "x^x=4", "sqrt(2)^x=4", "3^x=2"]


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
                self.assertEqual(derniere["titre"], "Égalité des exposants")
                self.assertEqual(derniere["lignes"][0].props[0], el.PROP_MEME_BASE)

    def test_cartes(self):
        titres = lambda s: [c["titre"] for c in corrige(s)["etapes"]]
        self.assertEqual(titres("7^(2x+1)=7^9"), ["Égalité des exposants"])
        self.assertEqual(titres("3^x=27"), ["Même base", "Égalité des exposants"])
        self.assertEqual(titres("3^(x+1)-27=0"), ["Isoler l'exponentielle", "Même base", "Égalité des exposants"])
        self.assertEqual(titres("2*3^(x-1)=18"), ["Isoler l'exponentielle", "Même base", "Égalité des exposants"])
        self.assertEqual(titres("5^(3x+2)=(5^x)^2"), ["Même base", "Égalité des exposants"])

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


class TestSource(unittest.TestCase):
    def source(self, nom):
        with open(os.path.join(RACINE, "exponentielles-logarithmes", nom), encoding="utf-8") as f:
            return f.read()

    def test_le_tex_ne_vient_jamais_de_sympy(self):
        """EL-04 : aucun appel à un écrivain TeX de SymPy ni à la conversion SymPy → arbre, et pas d'import de SymPy pour écrire."""
        for nom in ["exp_log.py"]:
            s = self.source(nom)
            self.assertIsNone(re.search(r"\blatex\s*\(", s), nom)
            self.assertNotIn("arbre_depuis_sympy", s, nom)
            self.assertNotIn("sp.latex", s, nom)
            self.assertNotIn("print_latex", s, nom)
            self.assertNotIn("charger_sympy", s, nom)
            self.assertNotIn("import sympy", s, nom)


if __name__ == "__main__":
    unittest.main()
