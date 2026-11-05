"""moteur/expr.py : la brique commune des expressions (chantier briques-communes, B1 ; revue de structure, R5).

La brique seule (arbre, TeX, lecture avec le lexique commun, « membre = membre », erreurs), son branchement par un lexique et par des
nœuds d'outil, l'absence d'état (A7) ; puis le réexport par exp_log : chaque nom déplacé est le même objet dans les deux modules
(`exp_log.X is expr.X`), et la lecture d'Exp-log est celle de la brique avec le lexique d'Exp-log."""
import ast
import os
import unittest
from fractions import Fraction as F

import moteurs  # noqa: F401  (chemins des moteurs)
from moteurs import RACINE

import expr
import exp_log as el
import exp_log_m as elm
from expr import Defini, Fn, Lexique, LEXIQUE_COMMUN, Nb, Neg, Noeud, Op, Pi, Pow, Var, lire_membres, tex, variables
from noyau import ErreurSaisie

# Noms déplacés d'exp_log vers la brique, gardés dans exp_log sous leur nom : (nom dans exp_log, nom dans expr).
DEPLACES = [(n, n) for n in ("Noeud", "Nb", "Var", "Pi", "Neg", "Op", "Pow", "Fn", "Defini", "variables", "tex", "tex_saisie", "Tok")] + [
    ("_nb_tex", "nb_tex"), ("_comme_somme", "comme_somme"), ("_entre_parentheses", "entre_parentheses"), ("_nom_tex", "nom_tex"),
    ("_DEBUT_COLLABLE", "DEBUT_COLLABLE"), ("_MINUSCULES", "MINUSCULES"), ("_NOM_INDEXE", "NOM_INDEXE"), ("_SYMBOLES", "SYMBOLES"),
    ("_OPERATEURS", "OPERATEURS"), ("_INEGALITES", "INEGALITES"), ("_nombre", "lire_nombre"), ("_pourcentage", "lire_pourcentage")]
# Gardés dans exp_log, branchés sur la brique (même nom, même signature) : la lecture avec le lexique d'Exp-log.
ENVELOPPES = ("tokeniser", "lire_membres", "_Parseur")
# Propres à Exp-log, restés dans exp_log : jamais dans la brique.
PROPRES_A_EXP_LOG = ("E", "Log", "contient_e", "LEXIQUE", "_fonction", "_base", "_base_entre_parentheses", "_BASE_SOULIGNEE",
                     "_BASE_COLLEE", "_DECIMAUX", "_avec_decimaux", "_nb_exact")


def lire(texte):
    return lire_membres(texte, LEXIQUE_COMMUN)


def x():
    return Var("x")


class TestArbre(unittest.TestCase):
    def test_egalite_et_hachage(self):
        self.assertEqual(Nb(F(1, 2)), Nb("1/2"))
        self.assertEqual(Nb(F(1, 2), "0,5"), Nb(F(1, 2)))                 # l'écriture décimale est hors égalité
        self.assertEqual(hash(Nb(F(1, 2), "0,5")), hash(Nb(F(1, 2))))
        self.assertNotEqual(Op("+", x(), Nb(1)), Op("-", x(), Nb(1)))
        self.assertEqual(len({Op("*", Nb(2), x()), Op("*", Nb(2), x()), Pow(x(), Nb(2))}), 2)
        self.assertNotEqual(Var("x"), "x")

    def test_repr(self):
        self.assertEqual(repr(Op("+", Var("x"), Nb(1))), "Op('+', Var('x'), Nb(Fraction(1, 1), None, None))")

    def test_sans_dict(self):
        """Des nœuds à __slots__ seulement (le cache des tests, memo_racines, en dépend)."""
        for n in (Nb(1), Var("x"), Pi(), Neg(x()), Op("+", x(), x()), Pow(x(), x()), Fn("sqrt", x()), Defini("a", x())):
            with self.subTest(type(n).__name__):
                self.assertFalse(hasattr(n, "__dict__"))

    def test_variables(self):
        g, d = lire("C0 * (1 + t)^n = sqrt(y) - pi")
        self.assertEqual(variables(g), {"C0", "t", "n"})
        self.assertEqual(variables(d), {"y", "p", "i"})                    # le lexique commun ne lit pas π
        self.assertEqual(variables(Defini(r"\Delta", Op("-", Pow(Var("b"), Nb(2)), Var("c")))), {"b", "c"})
        self.assertEqual(variables(Pi()), set())
        with self.assertRaises(TypeError):
            variables("x")


class TestTex(unittest.TestCase):
    CAS = [
        ("x^2 + 7x - 18", "x^{2} + 7x - 18"),
        ("4x + 32", "4x + 32"),
        ("2 * 3", r"2 \cdot 3"),
        ("x(x + 1)", "x(x + 1)"),
        ("(x - 2)(x + 1)", "(x - 2)(x + 1)"),
        ("3(x - 2)^2", "3(x - 2)^{2}"),
        ("-(x + 1)", "-(x + 1)"),
        ("(-x)^2", "(-x)^{2}"),
        ("(2^x)^3", "(2^{x})^{3}"),
        ("x - (2 - x)", "x - (2 - x)"),
        ("(1/2)x", r"\frac{1}{2} \cdot x"),
        ("(1/2)^x", r"\left(\frac{1}{2}\right)^{x}"),
        ("0,5^x", "0{,}5^{x}"),
        ("1234,5 + 1000000", r"1\text{’}234{,}5 + 1\text{’}000\text{’}000"),
        ("2sqrt(x + 1)", r"2\sqrt{x + 1}"),
        ("√(2)", r"\sqrt{2}"),
        ("C_0 * V0", r"C_{0} \cdot V_{0}"),
        ("x² − 3·x", "x^{2} - 3x"),
        ("2 × x ÷ 3", r"\frac{2x}{3}"),
    ]

    def test_saisies(self):
        for saisie, attendu in self.CAS:
            with self.subTest(saisie):
                g, d = lire(saisie)
                self.assertIsNone(d)
                self.assertEqual(tex(g), attendu)

    def test_arbres(self):
        self.assertEqual(tex(Op("+", x(), Neg(Nb(3)))), "x - 3")                      # jamais « + − »
        self.assertEqual(tex(Op("+", x(), Nb(-3))), "x - 3")
        self.assertEqual(tex(Op("+", x(), Op("+", Neg(x()), Nb(1)))), "x + (-x + 1)")
        self.assertEqual(tex(Op("*", Nb(-2), x())), r"(-2) \cdot x")
        self.assertEqual(tex(Neg(Nb(-100))), "-(-100)")
        self.assertEqual(tex(Nb(F(-3, 4))), r"-\frac{3}{4}")
        self.assertEqual(tex(Nb(F(3, 100), "0,03", "3")), r"3\,\%")
        self.assertEqual(tex(Defini(r"\Delta", Nb(5))), r"\Delta")
        self.assertEqual(tex(Op("*", Nb(2), Pi())), r"2\pi")
        self.assertEqual(expr.tex_saisie(x(), Nb(2)), "x = 2")
        self.assertEqual(expr.tex_saisie(x()), "x")

    def test_noeud_inconnu(self):
        class Sans(Noeud):
            __slots__ = ()
        with self.assertRaises(TypeError):
            tex(Sans())
        with self.assertRaises(TypeError):
            tex(3)

    def test_noeud_d_un_outil(self):
        """Un nœud propre à un outil s'écrit lui-même, et ses deux attributs de classe règlent le TeX commun."""
        class K(Noeud):
            __slots__ = ("a",)
            LETTRE = True
            BASE_ENTRE_PARENTHESES = True

            def __init__(self, a):
                self.a = a

            def ecrire_tex(self):
                return r"\kappa_{" + tex(self.a) + "}"
        k = K(x())
        self.assertEqual(tex(Op("*", k, Op("+", x(), Nb(1)))), r"\kappa_{x}(x + 1)")      # LETTRE : collé au groupe qui suit
        self.assertEqual(tex(Pow(k, Nb(2))), r"(\kappa_{x})^{2}")                          # BASE_ENTRE_PARENTHESES
        self.assertEqual(variables(Op("+", k, Var("y"))), {"x", "y"})                      # les lettres de ses champs
        self.assertEqual(tex(Op("*", el.E(), Op("+", x(), Nb(1)))), "e(x + 1)")             # Exp-log : e, logarithmes
        self.assertEqual(tex(Pow(el.Log(x()), Nb(2))), r"(\log(x))^{2}")
        self.assertEqual(tex(Op("*", Nb(2), el.Log(x(), el.E()))), r"2\ln(x)")


class TestLecture(unittest.TestCase):
    def test_membre_egal_membre(self):
        """« membre = membre » (P3 du 2e degré) : les deux arbres ; sans « = », (expression, None)."""
        g, d = lire("x^2 + 7x = 18")
        self.assertEqual(g, Op("+", Pow(x(), Nb(2)), Op("*", Nb(7), x())))
        self.assertEqual(d, Nb(18))
        g, d = lire("4x + 32 = x²")
        self.assertEqual((tex(g), tex(d)), ("4x + 32", "x^{2}"))
        g, d = lire("(x + 1)(x + 3) = 15")
        self.assertEqual(expr.tex_saisie(g, d), "(x + 1)(x + 3) = 15")
        g, d = lire("45u + 12 = 12u^2")
        self.assertEqual(variables(g) | variables(d), {"u"})
        self.assertEqual(lire("x^2 - 1"), (Op("-", Pow(x(), Nb(2)), Nb(1)), None))

    def test_nombres(self):
        self.assertEqual(lire("0,5x = 1’000")[1], Nb(1000))
        self.assertEqual(lire("0,5x")[0].a.dec, "0,5")
        self.assertEqual(lire("1.25")[0], Nb(F(5, 4)))
        self.assertEqual(lire("-x")[0], Neg(x()))

    def test_erreurs(self):
        for saisie, message in [
            ("", expr.MESSAGE_VIDE_COMMUN),
            ("   ", expr.MESSAGE_VIDE_COMMUN),
            ("x = 1 = 2", "Un seul signe = dans une équation."),
            ("= 3", "Il manque un membre de l'équation (avant ou après le signe =)."),
            ("x^2 =", "Il manque un membre de l'équation (avant ou après le signe =)."),
            ("x < 2", expr.MESSAGE_INEQUATION),
            ("x ≥ 2", expr.MESSAGE_INEQUATION),
            ("(x + 1", "Il manque une parenthèse fermante."),
            ("x + 1)", "Parenthèse fermante en trop."),
            ("x + ", "Il manque quelque chose à la fin de l'expression."),
            ("x + + 1", "Deux signes à la suite : utilisez des parenthèses, par exemple 3 + (-2)."),
            ("x 2", "Un nombre ne peut pas suivre directement une lettre, une parenthèse ou un autre nombre : "
                    "écrivez 2x (nombre devant), ou 2*3 avec le signe *."),
            ("1/2x", "Ajoutez des parenthèses après la division : 1/(2x) ou (1/2)x."),
            ("x^-2", expr.MESSAGE_EXPOSANT_COMMUN),
            ("2^3x", expr.MESSAGE_EXPOSANT_COMMUN),
            ("x^", "Il manque l'exposant après le signe ^."),
            ("2^3^2", "Mettez les exposants entre parenthèses : 2^(3^2) ou (2^3)^2."),
            ("1 000x", "Pas d'espace dans un nombre : écrivez 1000 ou 1’000."),
            ("1'00", "Une apostrophe dans un nombre est suivie d'exactement 3 chiffres : 1’000."),
            ("x # 2", "Caractère non reconnu : « # »."),
            ("sqrt x", "Après sqrt, ouvrez une parenthèse : sqrt(x)."),
            ("√x", "Après √, écrivez une parenthèse : √(x)."),
            ("sin(x) = 1", "La fonction sin n'est pas traitée par cet outil."),
        ]:
            with self.subTest(saisie):
                with self.assertRaises(ErreurSaisie) as e:
                    lire(saisie)
                self.assertEqual(str(e.exception), message)

    def test_le_lexique_commun_ne_connait_pas_exp_log(self):
        """Ni logarithme, ni exp, ni e, ni π, ni % : ils ne sont lus que par le lexique d'Exp-log."""
        for saisie, message in [("log(x) = 2", "La fonction log n'est pas traitée par cet outil."),
                                ("ln(x) = 2", "La fonction ln n'est pas traitée par cet outil."),
                                ("exp(x) = 2", "La fonction exp n'est pas traitée par cet outil."),
                                ("3 % = x", "Caractère non reconnu : « % »."),
                                ("π = x", "Caractère non reconnu : « π ».")]:
            with self.subTest(saisie):
                with self.assertRaises(ErreurSaisie) as e:
                    lire(saisie)
                self.assertEqual(str(e.exception), message)
        self.assertEqual(lire("e^x = 2")[0], Pow(Var("e"), x()))                     # e : une lettre comme une autre
        self.assertEqual(lire("E")[0], Var("E"))
        self.assertEqual(lire("e_1")[0], Var("e1"))

    def test_lexique_d_un_outil(self):
        """Le lexique est un paramètre explicite : fonctions, construction de leurs nœuds, lettres réservées, π, %, messages."""
        class Abs(Noeud):
            __slots__ = ("a",)

            def __init__(self, a):
                self.a = a

            def ecrire_tex(self):
                return r"\left|" + tex(self.a) + r"\right|"
        lexique = Lexique(fonctions=("sqrt", "abs"), noeud_fonction=lambda p, arg: Abs(arg), lettres_reservees="k",
                          noeud_lettre=lambda nom: Nb(7) if nom == "k" else Var(nom), lire_pi=True,
                          message_pourcentage="Le signe % suit un nombre.", message_exposant="Exposant entre parenthèses.",
                          message_vide="Vide.")
        g, d = lire_membres("abs(x - K) = 2pi + 5 %", lexique)
        self.assertEqual(g, Abs(Op("-", x(), Nb(7))))
        self.assertEqual(d, Op("+", Op("*", Nb(2), Pi()), Nb(F(1, 20))))
        self.assertEqual(tex(g) + " = " + tex(d), r"\left|x - 7\right| = 2\pi + 5\,\%")
        for saisie, message in [("", "Vide."), ("% 3", "Le signe % suit un nombre."), ("x^-1", "Exposant entre parenthèses."),
                                ("abs x", "Après abs, ouvrez une parenthèse : abs(x)."), ("xabs(x)", None)]:
            with self.subTest(saisie):
                if message is None:
                    self.assertEqual(lire_membres(saisie, lexique)[0], Op("*", x(), Abs(x())))
                    continue
                with self.assertRaises(ErreurSaisie) as e:
                    lire_membres(saisie, lexique)
                self.assertEqual(str(e.exception), message)
        self.assertEqual(LEXIQUE_COMMUN, Lexique())
        with self.assertRaises(AttributeError):
            LEXIQUE_COMMUN.fonctions = ()                                            # immuable


class TestSansEtat(unittest.TestCase):
    """A7 : aucune variable de module modifiée, aucun conteneur modifiable au niveau du module."""

    def test_aucune_instruction_global(self):
        with open(os.path.join(RACINE, "moteur", "expr.py"), encoding="utf-8") as f:
            arbre = ast.parse(f.read())
        self.assertEqual([n.lineno for n in ast.walk(arbre) if isinstance(n, (ast.Global, ast.Nonlocal))], [])

    def test_aucun_conteneur_modifiable(self):
        modifiables = {nom: type(v).__name__ for nom, v in vars(expr).items()
                       if not nom.startswith("__") and isinstance(v, (list, dict, set, bytearray))}
        self.assertEqual(modifiables, {})


class TestReexportParExpLog(unittest.TestCase):
    def test_memes_objets(self):
        for nom_el, nom_expr in DEPLACES:
            with self.subTest(nom_el):
                self.assertIs(getattr(el, nom_el), getattr(expr, nom_expr))

    def test_exp_log_m_lit_les_memes_objets(self):
        for nom in ("Nb", "Var", "Op", "Pow", "Neg", "Fn", "Pi", "Defini", "tex", "variables", "_nom_tex", "E", "Log"):
            with self.subTest(nom):
                self.assertIs(getattr(elm, nom), getattr(el, nom))

    def test_noeuds_d_exp_log(self):
        for nom in ("E", "Log"):
            with self.subTest(nom):
                classe = getattr(el, nom)
                self.assertTrue(issubclass(classe, expr.Noeud))
                self.assertFalse(hasattr(expr, nom))
                self.assertIn("ecrire_tex", vars(classe))

    def test_propres_a_exp_log_hors_de_la_brique(self):
        for nom in PROPRES_A_EXP_LOG:
            with self.subTest(nom):
                self.assertTrue(hasattr(el, nom))
                self.assertFalse(hasattr(expr, nom))

    def test_enveloppes(self):
        """tokeniser, lire_membres, _Parseur : la lecture de la brique avec le lexique d'Exp-log."""
        for saisie in ("log_(2x)(1296) = 3", "3Q = Q(1 + 3,75 %)^x", "e^(2x) - 3e^x + 2 = 0", "ln(x) + log_2(x) = π", "√(x) = 2"):
            with self.subTest(saisie):
                self.assertEqual(el.tokeniser(saisie), expr.tokeniser(saisie, el.LEXIQUE))
                self.assertEqual(el.lire_membres(saisie), lire_membres(saisie, el.LEXIQUE))
                toks = el.tokeniser(saisie.split("=")[0])
                self.assertEqual(el._Parseur(toks).tout(), expr.Parseur(toks, el.LEXIQUE).tout())
        self.assertEqual(el.lire_membres("2e^x = 5"), (Op("*", Nb(2), Pow(el.E(), x())), Nb(5)))

    def test_aucun_nom_prive_importe_de_la_brique(self):
        """Comme pour noyau (test_noyau) : un moteur d'outil ne prend dans la brique que des noms publics."""
        import test_noyau
        for chemin in test_noyau.MOTEURS:
            for module, nom, _ in test_noyau.imports_de(chemin):
                if module == "expr":
                    with self.subTest(moteur=chemin, nom=nom):
                        self.assertFalse(nom.startswith("_"), f"{nom} est privé")


if __name__ == "__main__":
    unittest.main()
