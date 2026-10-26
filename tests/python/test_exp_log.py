"""T33 (étape 1) — Outil « Exponentielles et logarithmes » : lecture de la saisie, arbre, TeX, aperçu (EL-03, EL-04, EL-05 pour la lecture).

Les étapes suivantes ajouteront ici la résolution (EL-01, EL-02, EL-06 à EL-11)."""
import json
import os
import re
import unittest
from fractions import Fraction as F

from moteurs import RACINE
from aides_sortie import TUTOIEMENT, chaines_litterales
import exp_log as el
from exp_log import Nb, Var, E, Neg, Op, Pow, Fn, Log
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
