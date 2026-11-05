"""moteur/chaine.py : la brique commune des chaînes du corrigé (chantier briques-communes, B2 ; revue de structure, R5).

La brique seule (éléments, TeX d'une ligne, rangées alignées), son branchement par des éléments et des justifications d'outil, les trois
options de présentation des corrigés du 2e degré (étiquette grise, « impossible » sous le facteur constant, texte au milieu de la
chaîne), activées (sortie attendue écrite d'après les corrigés de l'enseignant, Id_rem.pdf 2.9 a et c) et désactivées (la sortie
d'Exp-log d'avant la brique, écrite telle quelle), l'absence d'état (A7) ; puis le réexport par exp_log : chaque nom déplacé est le
même objet dans les deux modules (`exp_log.X is chaine.X`)."""
import ast
import os
import unittest
from fractions import Fraction as F

import moteurs  # noqa: F401  (chemins des moteurs)
from moteurs import RACINE

import chaine
import exp_log as el
import exp_log_m as elm
from chaine import (Chaine, Element, Eq, Justification, LigneTexte, Message, Ou, Rel, Texte, est_impossible, rangees_chaine,
                    tex_chaine, tex_element, tex_message)
from expr import LEXIQUE_COMMUN, Nb, Neg, Op, Var, lire_membres

# Noms déplacés d'exp_log vers la brique, gardés dans exp_log sous le même nom (même objet).
DEPLACES = ("Eq", "Rel", "Ou", "Texte", "Chaine", "Message", "tex_element", "LIENS_TEX", "tex_chaine", "rangees_chaine",
            "PROP_AUTRE_COTE", "PROP_PRODUIT_NUL", "PROP_MISE_EN_EVIDENCE")
# Propres à Exp-log, restés dans exp_log : jamais dans la brique.
PROPRES_A_EXP_LOG = ("Positif", "Car", "Divise", "PROP_BIEN_DEFINI", "PROPRIETES", "PROP_EXPO_POSITIVE", "PROP_LOG_DEUX_MEMBRES",
                     "PROP_ISOLER", "PROP_DISCRIMINANT", "_carte")
# Étiquettes du corrigé du 2e degré (decisions.md, D5) : des textes que l'outil passera, la brique ne les connaît pas.
ME, ID_REM, PRODUIT_NUL = "ME", "Id. rem. A = x, B = 1", "produit nul"


def eq(texte):
    g, d = lire_membres(texte, LEXIQUE_COMMUN)
    return Eq(g, d)


def corriger(saisie):
    s = el.analyser_saisie(saisie)
    return el.corriger_equation(s.g, s.d, s.inconnue, el.METHODE_LOGARITHMES)


def exercice_2_9_a():
    """Id_rem.pdf, 2.9 a : 6x² − 6 = 0 ⇔ 6(x² − 1) = 0 (ME) ⇔ 6(x + 1)(x − 1) = 0 (Id. rem.) ⇔ 6 = 0 ou x + 1 = 0 ou x − 1 = 0
    ⇔ x = −1 ou x = 1."""
    c = Chaine([eq("6x^2 - 6 = 0"), eq("6(x^2 - 1) = 0")], ["⇔"], [ME])
    x = Var("x")
    c.ajouter(Eq(Op("*", Nb(6), Op("*", Op("+", x, Nb(1)), Op("-", x, Nb(1)))), Nb(0)), "⇔", ID_REM)
    c.ajouter(Ou([Eq(Nb(6), Nb(0)), eq("x + 1 = 0"), eq("x - 1 = 0")]), "⇔", PRODUIT_NUL)
    c.ajouter(Ou([Eq(Var("x"), Nb(-1)), Eq(Var("x"), Nb(1))]), "⇔")
    return c


VERIFICATION = Message("Id. rem. ", Texte("A^{2} - 2AB + B^{2}"), " avec ", Texte("A = 4z"), ", ", Texte("B = 9"),
                       ". Vérification : ", Texte(r"2AB = 2 \cdot 4z \cdot 9 = 72z"), " ✓")


def exercice_2_9_c(texte=True):
    """Id_rem.pdf, 2.9 c : la ligne « Id. rem. … Vérification … ✓ » au milieu de la chaîne, entre la ME et 3(4z − 9)² = 0."""
    c = Chaine([eq("48z^2 - 216z + 243 = 0"), eq("3(16z^2 - 72z + 81) = 0")], ["⇔"], [ME])
    c.ajouter(eq("3(4z - 9)^2 = 0"), "⇔", texte_avant=VERIFICATION if texte else None)
    c.ajouter(Ou([Eq(Nb(3), Nb(0)), eq("4z - 9 = 0")]), "⇔", PRODUIT_NUL)
    c.ajouter(Eq(Var("z"), Nb(F(9, 4))), "⇔")
    return c


class TestElements(unittest.TestCase):
    def test_eq(self):
        self.assertEqual(eq("x = 2"), Eq(Var("x"), Nb(2)))
        self.assertEqual(Eq(Var("x"), Nb(2), [Nb(3)]), Eq(Var("x"), Nb(2)))           # milieu hors égalité
        self.assertEqual(len({Eq(Var("x"), Nb(2)), Eq(Var("x"), Nb(2)), Eq(Var("x"), Nb(3))}), 2)
        self.assertEqual(repr(Eq(Var("x"), Nb(2))), "Eq(Var('x'), Nb(Fraction(2, 1), None, None))")

    def test_tex_element(self):
        x = Var("x")
        self.assertEqual(tex_element(Eq(x, Nb(1000), [Nb(10)])), "x = 10 = 1\\text{’}000")
        self.assertEqual(tex_element(Ou([Eq(x, Nb(-1)), Eq(x, Nb(1))])), r"x = -1 \text{ ou } x = 1")
        self.assertEqual(tex_element(Rel(x, "≤", Nb(0))), r"x \le 0")
        self.assertEqual(tex_element(Texte(r"x > 0", r"2^{5} < 50")), r"x > 0 \quad (2^{5} < 50)")
        self.assertEqual(tex_element(eq("x^2 + 7x = 18").g), "x^{2} + 7x")
        with self.assertRaises(TypeError):
            tex_element(Element())

    def test_message(self):
        m = Message("Donc ", Texte("x < 1"), " et ", Nb(F(1, 2)), " < x.")
        self.assertEqual(m.texte(), r"Donc x < 1 et \frac{1}{2} < x.")
        self.assertEqual(m.html(), r"Donc \(x &lt; 1\) et \(\frac{1}{2}\) &lt; x.")
        self.assertEqual(tex_message(m), r"\text{Donc }x < 1\text{ et }\frac{1}{2}\text{ < x.}")
        self.assertEqual(tex_message("On ramène tout à gauche."), r"\text{On ramène tout à gauche.}")
        with self.assertRaises(TypeError):
            tex_message({"type": "tableau"})


class TestChaine(unittest.TestCase):
    """Sans option : l'écriture d'Exp-log d'avant la brique."""

    def test_liens_et_proprietes(self):
        c = Chaine([eq("2x + 1 = 5"), eq("2x = 4")], ["⇔"], [chaine.PROP_AUTRE_COTE])
        c.ajouter(eq("x = 2"), "⇒").ajouter(Nb(2), "≈")
        self.assertEqual(tex_chaine(c), r"2x + 1 = 5 \iff 2x = 4 \quad \text{(on passe un terme de l'autre côté)} \Rightarrow x = 2"
                                        r" \approx 2")
        self.assertEqual(rangees_chaine(c), [("", "2x + 1 = 5", None), (r"\iff", "2x = 4", "(on passe un terme de l'autre côté)"),
                                             (r"\Rightarrow", r"x = 2 \approx 2", None)])

    def test_egalites_alignees(self):
        """Les « = » prolongent la ligne jusqu'à une propriété ; la suite est alignée sous le « = » précédent."""
        x = Var("x")
        c = Chaine([Eq(x, Nb(F(1, 2)))], [], []).ajouter(Nb(F(2, 4)), "=", "réduite").ajouter(Nb(F(1, 2)), "=")
        self.assertEqual(rangees_chaine(c), [("", r"x = \frac{1}{2} = \frac{1}{2}", "(réduite)"),
                                             ("", r"\phantom{x} = \frac{1}{2}", None)])

    def test_note(self):
        c = Chaine([Rel(Var("x"), ">", Nb(0))], note="aucune solution")
        self.assertEqual(tex_chaine(c), r"x > 0 \quad \text{(aucune solution)}")
        self.assertEqual(rangees_chaine(c), [("", "x > 0", "(aucune solution)")])
        c = Chaine([Rel(Var("x"), ">", Nb(0))], note="retenue", coche=True)
        self.assertEqual(tex_chaine(c), r"x > 0 \quad \text{(retenue)} \; \checkmark")
        self.assertEqual(rangees_chaine(c), [("", "x > 0", r"(retenue) \(\checkmark\)")])
        c = Chaine([eq("x = 1"), eq("x = 1")], ["⇔"], ["a"], note="b")
        self.assertEqual(rangees_chaine(c)[-1][2], "(a) (b)")

    def test_exp_log_inchange(self):
        """Des chaînes d'Exp-log, écrites telles que l'outil les écrivait avant la brique (dump identique au départ du chantier)."""
        verification = corriger("log(5-x)=8")["etapes"][-1]["lignes"][0]
        self.assertTrue(verification.coche)
        self.assertEqual(tex_chaine(verification), r"5 - x = 10^{8} > 0 \quad \text{(le logarithme est bien défini)} \; \checkmark")
        self.assertEqual(rangees_chaine(verification),
                         [("", "5 - x = 10^{8} > 0", r"(le logarithme est bien défini) \(\checkmark\)")])
        c = corriger("2^x = 3^(x-1)")["etapes"][-1]["lignes"][-1]
        self.assertEqual(rangees_chaine(c), [
            ("", "2^{x} = 3^{x - 1}", None),
            (r"\iff", r"\log(2^{x}) = \log(3^{x - 1})", "(log des deux membres)"),
            (r"\iff", r"x \cdot \log(2) = (x - 1) \cdot \log(3)", "(log(a^A) = A · log(a))"),
            (r"\iff", r"x \cdot \log(2) = x \cdot \log(3) - \log(3)", None),
            (r"\iff", r"\log(3) = x(\log(3) - \log(2))", None),
            (r"\iff", r"x = \frac{\log(3)}{\log(3) - \log(2)}", r"(car \(\log(3) - \log(2) \neq 0\))"),
            ("", r"\phantom{x} = \frac{\log(3)}{\log\left(\frac{3}{2}\right)}", "(log a − log b = log(a/b))")])
        self.assertEqual(tex_chaine(c).split(r" \iff ")[-1],
                         r"x = \frac{\log(3)}{\log(3) - \log(2)} \quad \text{(car } \log(3) - \log(2) \neq 0\text{)} = "
                         r"\frac{\log(3)}{\log\left(\frac{3}{2}\right)} \quad \text{(log a − log b = log(a/b))}")

    def test_options_desactivees_par_defaut(self):
        for c in (exercice_2_9_a(), exercice_2_9_c(texte=False), corriger("2^x = 3^(x-1)")["etapes"][-1]["lignes"][-1]):
            with self.subTest(tex_chaine(c)[:30]):
                self.assertEqual(tex_chaine(c), tex_chaine(c, etiquette_grise=False, impossible=False))
                self.assertEqual(rangees_chaine(c), rangees_chaine(c, etiquette_grise=False, impossible=False))
                self.assertFalse(any(isinstance(r, LigneTexte) for r in rangees_chaine(c)))
                self.assertNotIn("impossible", tex_chaine(c))
                self.assertNotIn("textcolor", tex_chaine(c))


class TestBranchements(unittest.TestCase):
    """Un élément ou une justification propres à un outil s'écrivent eux-mêmes ; la brique ne les connaît pas."""

    def test_element_d_un_outil(self):
        class Borne(Element):
            __slots__ = ("x",)

            def __init__(self, x):
                self.x = x

            def ecrire_tex(self):
                return self.x + r" \in \mathbb{R}"
        c = Chaine([Borne("x")]).ajouter(eq("x = 1"), "=").ajouter(eq("x = 1"), "=", "p").ajouter(Nb(1), "=")
        self.assertEqual(rangees_chaine(c), [("", r"x \in \mathbb{R} = x = 1 = x = 1", "(p)"), ("", " = 1", None)])  # pas d'ancre

    def test_justification_d_un_outil(self):
        class Parce(Justification):
            __slots__ = ()

            def ecrire_tex(self):
                return r"\text{(parce que)}"

            def ecrire_rangee(self):
                return "(parce que)"
        c = Chaine([eq("x = 1"), eq("x = 1")], ["⇔"], [Parce()])
        for grise in (False, True):
            self.assertEqual(tex_chaine(c, etiquette_grise=grise), r"x = 1 \iff x = 1 \quad \text{(parce que)}")
            self.assertEqual(rangees_chaine(c, etiquette_grise=grise)[-1], (r"\iff", "x = 1", "(parce que)"))
        with self.assertRaises(TypeError):
            tex_chaine(Chaine([eq("x = 1"), eq("x = 1")], ["⇔"], [Justification()]))

    def test_exp_log(self):
        self.assertTrue(issubclass(el.Positif, Element))
        self.assertTrue(issubclass(el.Car, Justification) and issubclass(el.Divise, Justification))
        x = Var("x")
        self.assertEqual(tex_element(el.Positif(Var("u"), Nb(3))), "u = 3 > 0")
        c = Chaine([eq("2x = 1"), Eq(x, Nb(F(1, 2)))], ["⇔"], [el.Car(Nb(2))])
        self.assertEqual(tex_chaine(c), r"2x = 1 \iff x = \frac{1}{2} \quad \text{(car } 2 \neq 0\text{)}")
        self.assertEqual(rangees_chaine(c)[-1][2], r"(car \(2 \neq 0\))")
        c = Chaine([eq("3Q = 2Q"), eq("3 = 2")], ["⇔"], [el.Divise("Q")])
        self.assertEqual(tex_chaine(c), r"3Q = 2Q \iff 3 = 2 \quad \text{(on divise les deux membres par } Q \text{ ; } Q > 0 "
                                        r"\text{ : une quantité de départ est positive)}")
        self.assertEqual(rangees_chaine(c)[-1][2], r"(on divise les deux membres par \(Q\) (\(Q > 0\) : une quantité de départ est "
                                                   r"positive))")


class TestEtiquetteGrise(unittest.TestCase):
    """Id_rem.pdf : « ME », « Id. rem. A = x, B = 1 » en gris à droite, sans parenthèses (decisions.md, D5)."""

    def test_activee(self):
        c = exercice_2_9_a()
        self.assertEqual(rangees_chaine(c, etiquette_grise=True)[:3], [
            ("", "6x^{2} - 6 = 0", None), (r"\iff", "6(x^{2} - 1) = 0", "ME"), (r"\iff", "6(x + 1)(x - 1) = 0", ID_REM)])
        self.assertEqual(tex_chaine(c, etiquette_grise=True).split(r" \iff ")[1], r"6(x^{2} - 1) = 0 \quad \textcolor{gray}{\text{ME}}")

    def test_desactivee(self):
        c = exercice_2_9_a()
        self.assertEqual(rangees_chaine(c)[1], (r"\iff", "6(x^{2} - 1) = 0", "(ME)"))
        self.assertEqual(tex_chaine(c).split(r" \iff ")[1], r"6(x^{2} - 1) = 0 \quad \text{(ME)}")

    def test_note(self):
        c = Chaine([eq("x = 1"), eq("x = 1")], ["⇔"], ["a"], note="b", coche=True)
        self.assertEqual(rangees_chaine(c, etiquette_grise=True)[-1][2], r"a ; b \(\checkmark\)")
        self.assertEqual(tex_chaine(c, etiquette_grise=True),
                         r"x = 1 \iff x = 1 \quad \textcolor{gray}{\text{a}} \quad \textcolor{gray}{\text{b}} \; \checkmark")
        self.assertEqual(rangees_chaine(Chaine([eq("x = 1")], note="b"), etiquette_grise=True), [("", "x = 1", "b")])


class TestImpossible(unittest.TestCase):
    """Id_rem.pdf, 2.9 a, c, e, f : le facteur constant du produit nul, « 6 = 0 » avec « impossible » dessous (D7, E8)."""

    def test_activee(self):
        c = exercice_2_9_a()
        self.assertEqual(rangees_chaine(c, impossible=True)[3],
                         (r"\iff", r"\underbrace{6 = 0}_{\text{impossible}} \text{ ou } x + 1 = 0 \text{ ou } x - 1 = 0", f"({PRODUIT_NUL})"))
        self.assertIn(r"\iff \underbrace{6 = 0}_{\text{impossible}} \text{ ou } x + 1 = 0", tex_chaine(c, impossible=True))
        self.assertEqual(tex_element(Ou([Eq(Neg(Nb(1)), Nb(0)), Eq(Nb(-6), Nb(0)), eq("x = 0")]), impossible=True),
                         r"\underbrace{-1 = 0}_{\text{impossible}} \text{ ou } \underbrace{-6 = 0}_{\text{impossible}} \text{ ou } x = 0")

    def test_desactivee(self):
        c = exercice_2_9_a()
        self.assertEqual(rangees_chaine(c)[3][1], r"6 = 0 \text{ ou } x + 1 = 0 \text{ ou } x - 1 = 0")
        self.assertNotIn("impossible", tex_chaine(c))

    def test_seulement_une_egalite_fausse_entre_deux_nombres(self):
        """Rien de faux : la mention ne va que sur une égalité fausse entre deux nombres écrits, et seulement dans un « ou »."""
        for e, attendu in [(Eq(Nb(6), Nb(0)), True), (Eq(Neg(Nb(1)), Nb(0)), True), (Eq(Nb(F(1, 2)), Nb(0)), True),
                           (Eq(Nb(0), Nb(0)), False), (Eq(Nb(2), Neg(Neg(Nb(2)))), False), (eq("x = 0"), False),
                           (eq("2 - 2 = 1"), False), (Eq(Nb(1), Nb(0), [Nb(2)]), False), (Rel(Nb(1), "<", Nb(0)), False)]:
            with self.subTest(tex_element(e)):
                self.assertIs(est_impossible(e), attendu)
        self.assertEqual(tex_element(Eq(Nb(6), Nb(0)), impossible=True), "6 = 0")                  # hors d'un « ou » : rien
        self.assertEqual(tex_element(Ou([Eq(Nb(0), Nb(0)), eq("x = 0")]), impossible=True), r"0 = 0 \text{ ou } x = 0")


class TestTexteAuMilieu(unittest.TestCase):
    """Id_rem.pdf, 2.9 c : « Id. rem. A² − 2AB + B² avec A = 4z, B = 9. Vérification : 2AB = 2 · 4z · 9 = 72z ✓ » sur toute la largeur,
    entre la ME et 3(4z − 9)² = 0, dont le ⇔ reste aligné sous les autres (decisions.md, E5)."""

    def test_activee(self):
        c = exercice_2_9_c()
        self.assertEqual(c.textes, {2: [VERIFICATION]})
        self.assertEqual(rangees_chaine(c, etiquette_grise=True, impossible=True), [
            ("", "48z^{2} - 216z + 243 = 0", None),
            (r"\iff", "3(16z^{2} - 72z + 81) = 0", "ME"),
            LigneTexte(VERIFICATION),
            (r"\iff", "3(4z - 9)^{2} = 0", None),
            (r"\iff", r"\underbrace{3 = 0}_{\text{impossible}} \text{ ou } 4z - 9 = 0", PRODUIT_NUL),
            (r"\iff", r"z = \frac{9}{4}", None)])
        self.assertEqual(tex_chaine(c, etiquette_grise=True, impossible=True),
                         r"48z^{2} - 216z + 243 = 0 \iff 3(16z^{2} - 72z + 81) = 0 \quad \textcolor{gray}{\text{ME}} \quad "
                         r"\text{Id. rem. }A^{2} - 2AB + B^{2}\text{ avec }A = 4z\text{, }B = 9\text{. Vérification : }"
                         r"2AB = 2 \cdot 4z \cdot 9 = 72z\text{ ✓} \quad \iff 3(4z - 9)^{2} = 0 \iff "
                         r"\underbrace{3 = 0}_{\text{impossible}} \text{ ou } 4z - 9 = 0 \quad \textcolor{gray}{\text{produit nul}} "
                         r"\iff z = \frac{9}{4}")
        with self.assertRaises(ValueError):
            [lien for lien, _, _ in rangees_chaine(c)]                        # une page qui l'ignorerait échoue, sans rien cacher

    def test_desactivee(self):
        avec, sans = exercice_2_9_c(), exercice_2_9_c(texte=False)
        self.assertEqual(sans.textes, {})
        self.assertEqual([r for r in rangees_chaine(avec) if not isinstance(r, LigneTexte)], rangees_chaine(sans))
        self.assertEqual(tex_chaine(sans), r"48z^{2} - 216z + 243 = 0 \iff 3(16z^{2} - 72z + 81) = 0 \quad \text{(ME)} \iff "
                                           r"3(4z - 9)^{2} = 0 \iff 3 = 0 \text{ ou } 4z - 9 = 0 \quad \text{(produit nul)} \iff "
                                           r"z = \frac{9}{4}")

    def test_plusieurs_lignes_et_un_bloc(self):
        """Phrase de choix, puis tableau S-P (un bloc, passé tel quel), puis ⇔ (x + 6)(x − 7) = 0 (decisions.md, § 7, S-P)."""
        tableau = {"type": "tableau_essais"}
        c = Chaine([eq("x^2 = x + 42"), eq("x^2 - x - 42 = 0")], ["⇔"], [None])
        c.ajouter(eq("(x + 6)(x - 7) = 0"), "⇔", texte_avant=["Pas de ME, pas d'Id. rem. : S-P.", tableau])
        self.assertEqual(rangees_chaine(c)[2:], [LigneTexte("Pas de ME, pas d'Id. rem. : S-P."), LigneTexte(tableau),
                                                 (r"\iff", "(x + 6)(x - 7) = 0", None)])
        with self.assertRaises(TypeError):
            tex_chaine(c)                                                     # un bloc ne s'écrit pas en TeX : erreur, pas de faux

    def test_egalite_apres_le_texte(self):
        """Un lien « = » après la ligne de texte commence une nouvelle ligne, alignée sous le « = » précédent."""
        x = Var("x")
        c = Chaine([Eq(x, Nb(F(4, 8)))]).ajouter(Nb(F(1, 2)), "=", texte_avant="On réduit.")
        self.assertEqual(rangees_chaine(c), [("", r"x = \frac{1}{2}", None), LigneTexte("On réduit."),
                                             ("", r"\phantom{x} = \frac{1}{2}", None)])

    def test_position(self):
        for textes in ({0: ["a"]}, {2: ["a"]}, {1: []}):
            with self.subTest(textes), self.assertRaises(AssertionError):
                Chaine([eq("x = 1"), eq("x = 1")], ["⇔"], [None], textes=textes)
        self.assertEqual(Chaine([eq("x = 1"), eq("x = 1")], ["⇔"], [None], textes={1: ("a",)}).textes, {1: ["a"]})


class TestSansEtat(unittest.TestCase):
    """A7 : aucune variable de module modifiée, aucun conteneur modifiable au niveau du module ; la brique n'importe que expr."""

    def source(self):
        with open(os.path.join(RACINE, "moteur", "chaine.py"), encoding="utf-8") as f:
            return ast.parse(f.read())

    def test_aucune_instruction_global(self):
        self.assertEqual([n.lineno for n in ast.walk(self.source()) if isinstance(n, (ast.Global, ast.Nonlocal))], [])

    def test_aucun_conteneur_modifiable(self):
        modifiables = {nom: type(v).__name__ for nom, v in vars(chaine).items()
                       if not nom.startswith("__") and isinstance(v, (list, dict, set, bytearray))}
        self.assertEqual(modifiables, {})
        with self.assertRaises(TypeError):
            chaine.LIENS_TEX["⇔"] = "="
        with self.assertRaises(TypeError):
            Rel.SIGNES["<"] = ">"

    def test_imports(self):
        internes = {(n.module if isinstance(n, ast.ImportFrom) else a.name) for n in ast.walk(self.source())
                    if isinstance(n, (ast.Import, ast.ImportFrom)) for a in n.names}
        self.assertEqual(internes, {"collections", "html", "types", "expr"})


class TestReexportParExpLog(unittest.TestCase):
    def test_memes_objets(self):
        for nom in DEPLACES:
            with self.subTest(nom):
                self.assertIs(getattr(el, nom), getattr(chaine, nom))

    def test_exp_log_m_lit_les_memes_objets(self):
        for nom in ("Chaine", "Eq", "Ou", "Rel", "Texte", "Message", "tex_element", "tex_chaine", "PROP_AUTRE_COTE",
                    "PROP_MISE_EN_EVIDENCE", "PROP_PRODUIT_NUL"):
            with self.subTest(nom):
                self.assertIs(getattr(elm, nom), getattr(chaine, nom))

    def test_propres_a_exp_log_hors_de_la_brique(self):
        for nom in PROPRES_A_EXP_LOG:
            with self.subTest(nom):
                self.assertTrue(hasattr(el, nom))
                self.assertFalse(hasattr(chaine, nom))
        self.assertEqual(sorted(n for n in vars(chaine) if n.startswith("PROP_")),
                         ["PROP_AUTRE_COTE", "PROP_MISE_EN_EVIDENCE", "PROP_PRODUIT_NUL"])
        self.assertTrue({chaine.PROP_AUTRE_COTE, chaine.PROP_MISE_EN_EVIDENCE, chaine.PROP_PRODUIT_NUL} <= el.PROPRIETES)

    def test_la_coche_suit_la_note_bien_defini(self):
        """La coche d'Exp-log était lue sur la note PROP_BIEN_DEFINI ; elle est maintenant posée par l'outil sur ces chaînes-là."""
        for saisie in ["log(5-x)=8", "log(2x+1)=3", "ln(2-x)=1", "2^(x+1)=8", "log_x(256)=4", "log(x^2-3x)=1"]:
            for carte in corriger(saisie)["etapes"]:
                for ligne in carte["lignes"]:
                    if isinstance(ligne, Chaine):
                        with self.subTest(saisie=saisie, note=ligne.note):
                            self.assertIs(ligne.coche, ligne.note == el.PROP_BIEN_DEFINI)

    def test_aucun_nom_prive_importe_de_la_brique(self):
        """Comme pour noyau (test_noyau) : un moteur d'outil ne prend dans la brique que des noms publics."""
        import test_noyau
        for chemin in test_noyau.MOTEURS:
            for module, nom, _ in test_noyau.imports_de(chemin):
                if module == "chaine":
                    with self.subTest(moteur=chemin, nom=nom):
                        self.assertFalse(nom.startswith("_"), f"{nom} est privé")


if __name__ == "__main__":
    unittest.main()
