"""Outil « Équations du 2e degré » : lecture et analyse de la saisie (equations-2e-degre/equations.py ; chantier equations-2e-degre,
P3 ; decisions.md, D23, § 4 et § 13.5).

- Chaque message du § 13.5, et l'ordre de priorité sur des saisies qui en mêlent plusieurs.
- Notation suisse (apostrophe, virgule décimale), décimaux de l'énoncé (E14 : paramètre `decimaux_enonce`).
- (x + 1)(x + 3) = 15, Az 4.1 g, e^x = 2 (« une seule inconnue ») ; la saisie lue se résout par second_degre.resoudre_equation.
- R12 (vouvoiement) et vocabulaire de tous les littéraux du fichier.

Le dossier de l'outil n'entre au manifeste qu'en P5 : le module est chargé ici par son chemin (dossier ajouté à la fin de sys.path)."""
import os
import sys
import unittest
from fractions import Fraction as F

import moteurs  # noqa: F401  (chemins des moteurs)

import exp_log
import expr
import second_degre as sd
from aides_sortie import TUTOIEMENT, chaines_litterales
from corpus_second_degre import RESOLUES
from noyau import ErreurSaisie
from test_vocabulaire import INTERDITS

DOSSIER = os.path.join(moteurs.RACINE, "equations-2e-degre")
if DOSSIER not in sys.path:
    sys.path.append(DOSSIER)

import equations  # noqa: E402

M = equations.MESSAGES_SAISIE
VIDE = "Écrivez une équation."


class Saisie(unittest.TestCase):

    def message(self, saisie):
        with self.assertRaises(ErreurSaisie) as e:
            equations.analyser(saisie)
        return str(e.exception)

    def assertMessage(self, saisie, attendu):
        with self.subTest(saisie=saisie):
            self.assertEqual(self.message(saisie), attendu)


class TestMessages(Saisie):

    def test_le_fichier_est_dans_le_dossier_de_l_outil(self):
        self.assertEqual(os.path.dirname(os.path.abspath(equations.__file__)), DOSSIER)

    def test_lexique(self):
        """Le lexique commun avec les messages de l'outil ; sqrt et √ restent lus (l'analyse les refuse avec son message)."""
        L = equations.LEXIQUE_EQ
        self.assertEqual(L.fonctions, ("sqrt",))
        self.assertEqual(L.message_vide, VIDE)
        self.assertIn("x^2", L.message_exposant)
        self.assertEqual((L.lettres_reservees, L.lire_pi, L.message_pourcentage), ("", False, None))

    def test_saisie_vide(self):
        for s in ("", "   ", "\t"):
            self.assertMessage(s, VIDE)

    def test_syntaxe(self):
        """Les messages de la lecture commune, avec l'exemple de l'outil pour l'exposant."""
        self.assertMessage("x^-2=1", equations.MESSAGE_EXPOSANT)
        self.assertMessage("x^2x=1", equations.MESSAGE_EXPOSANT)
        self.assertMessage("x^2(x+1)=1", equations.MESSAGE_EXPOSANT)
        self.assertMessage("x^2 < 4", expr.MESSAGE_INEQUATION)
        self.assertMessage("sin(x)=0", "La fonction sin n'est pas traitée par cet outil.")
        self.assertMessage("ln(x)=1", "La fonction ln n'est pas traitée par cet outil.")
        self.assertMessage("x^2+*3=0", "Il manque un terme avant « * ».")
        self.assertMessage("x^2=", "Il manque un membre de l'équation (avant ou après le signe =).")
        self.assertMessage("x=1=2", "Un seul signe = dans une équation.")
        self.assertMessage("(x+1=0", "Il manque une parenthèse fermante.")
        self.assertMessage("√x=2", "Après √, écrivez une parenthèse : √(x).")
        self.assertMessage("3%x=1", "Caractère non reconnu : « % ».")
        self.assertMessage("x^2=1 000", "Pas d'espace dans un nombre : écrivez 1000 ou 1’000.")

    def test_pas_de_signe_egal(self):
        for s in ("x^2-4", "x+y", "2+2", "(x+1)(x+3)"):
            self.assertMessage(s, M["sans_egal"])
        self.assertEqual(M["sans_egal"], "Écrivez une équation, avec le signe « = ».")

    def test_aucune_lettre(self):
        for s in ("2=2", "3^2=9", "sqrt(4)=2", "1/0=1"):
            self.assertMessage(s, M["sans_lettre"])

    def test_plusieurs_lettres(self):
        """D23 : une seule lettre. e est une lettre comme une autre (l'outil ne connaît pas le nombre e) : e^x = 2 en a deux."""
        for s in ("x^2+y=0", "ax^2=1", "e^x=2", "y^x=2", "pi x=1", "x^2=X"):
            self.assertMessage(s, M["plusieurs_lettres"])

    def test_inconnue_en_exposant(self):
        for s in ("2^x=8", "x^x=1", "3^(x+1)=x^2", "x^2=2^(2x)"):
            self.assertMessage(s, M["exposant"])
        self.assertIn("« Exponentielles et logarithmes »", M["exposant"])

    def test_prochaine_version(self):
        """L'inconnue sous une racine ou au dénominateur, un exposant non entier ou négatif sur l'inconnue."""
        for s in ("sqrt(x)=2", "√(x+1)=3", "1/x=2", "(x+1)/(x-1)=0", "x^2=3/(2x)", "x^(1/2)=3", "x^(-1)=2", "x^0,5=2",
                  "(x+1)^(-2)=1", "x^2+sqrt(x^2+1)=0"):
            self.assertMessage(s, M["prochaine_version"])

    def test_racine_sans_l_inconnue(self):
        """Une racine dans un coefficient, même rationnelle, et une puissance d'exposant non entier d'un nombre."""
        for s in ("sqrt(2)x^2=1", "x^2=√(4)", "2^(1/2)x=1", "x^2=9^(1/2)", "x^(sqrt(4))=1"):
            self.assertMessage(s, M["racine"])

    def test_division_par_zero(self):
        for s in ("x^2=1/0", "x/(2-2)=1", "0^(-1)x=1", "x^2=(1/0)^2"):
            self.assertMessage(s, M["division_par_0"])

    def test_bornes(self):
        """§ 13.5 : degré > 8 après développement, coefficient de plus de 9 chiffres (numérateur ou dénominateur)."""
        for s in ("x^9=1", "(x+1)^10=0", "(x^3+1)^3=x", "x^(2^100)=1", "1234567890x^2=1", "x^2=1/1234567890",
                  "x^5*x^5=x", "x^8=x^9-x^9+1"):                                 # chaque membre est borné (x^9 ici)
            self.assertMessage(s, M["bornes"])
        self.assertEqual(equations.analyser("123456789x^2=-123456789x+1/123456789")[2], "x")       # 9 chiffres : accepté
        self.assertEqual(equations.analyser("x^8=1")[2], "x")
        self.assertEqual(M["bornes"], sd.MESSAGES["hors_bornes"])

    def test_ordre_de_priorite(self):
        """§ 13.5 : vide, syntaxe, pas de « = », aucune lettre, plusieurs lettres, exposant, prochaine version, racine, division
        par 0, bornes : sur une saisie qui en mêle plusieurs, le premier dans cet ordre."""
        for saisie, cle in (("x^2 + y +* 1", None),                      # syntaxe avant « = » et plusieurs lettres
                            ("x + y", "sans_egal"),                        # pas de « = » avant plusieurs lettres
                            ("1/0 + 2", "sans_egal"),
                            ("sqrt(2) = 1/0", "sans_lettre"),             # aucune lettre avant racine et division par 0
                            ("y^x = sqrt(x)", "plusieurs_lettres"),       # plusieurs lettres avant exposant
                            ("2^x = sqrt(x)", "exposant"),                # exposant avant prochaine version
                            ("1/x = 2^x", "exposant"),
                            ("sqrt(x) = sqrt(2)", "prochaine_version"),   # prochaine version avant racine
                            ("1/x = 1/0", "prochaine_version"),           # … et avant division par 0
                            ("sqrt(2)x = 1/0", "racine"),                 # racine avant division par 0
                            ("x^9 = 1/0", "division_par_0"),              # division par 0 avant bornes
                            ("x^9 = sqrt(2)", "racine"),
                            ("x^(1/2) = x^9", "prochaine_version")):
            attendu = "Il manque un terme avant « * »." if cle is None else M[cle]
            self.assertMessage(saisie, attendu)
        self.assertEqual(list(M), ["sans_egal", "sans_lettre", "plusieurs_lettres", "exposant", "prochaine_version", "racine",
                                   "division_par_0", "bornes"])
        self.assertEqual(equations.ORDRE, ("exposant", "prochaine_version", "racine", "division_par_0"))

    def test_messages_du_paragraphe_4(self):
        """Les messages du § 4 et du § 13.5, mot pour mot."""
        self.assertEqual(M["plusieurs_lettres"], "Écrivez une équation avec une seule inconnue.")
        self.assertEqual(M["sans_lettre"], "Écrivez une équation avec une inconnue.")
        self.assertEqual(M["prochaine_version"], "Les équations avec une fraction ou une racine contenant l'inconnue seront "
                                                 "traitées dans une prochaine version.")
        self.assertEqual(M["racine"], "Écrivez une équation dont les coefficients n'ont pas de racine.")
        self.assertEqual(M["division_par_0"], "Division par 0 : vérifiez la saisie.")
        self.assertEqual(M["exposant"], "L'inconnue est en exposant : utilisez l'outil « Exponentielles et logarithmes ».")
        self.assertEqual(M["bornes"], "Cette équation dépasse ce que l'outil sait traiter.")

    def test_vouvoiement_et_vocabulaire(self):
        """R12 et C6 sur tous les littéraux du fichier (test_vocabulaire ne lit pas encore ce dossier : il entre au manifeste en P5)."""
        litteraux = chaines_litterales(equations.__file__)
        self.assertGreater(len(litteraux), 10)
        for ligne, texte in litteraux:
            with self.subTest(ligne=ligne):
                self.assertIsNone(TUTOIEMENT.search(texte), texte)
                self.assertIsNone(INTERDITS.search(texte), texte)


class TestLecture(Saisie):

    def test_inconnue_saisie(self):
        """D23 : l'inconnue est la lettre saisie (x, t, y, z, u, s dans le corrigé), majuscule comprise."""
        for saisie, x in (("t^2+20t+100=0", "t"), ("45u+12=12u^2", "u"), ("48z^2-216z+243=0", "z"), ("-y^2+10y-9=0", "y"),
                          ("(5/4)s^2+3s+1=0", "s"), ("X^2=4", "X"), ("e^2=4", "e")):
            with self.subTest(saisie=saisie):
                g, d, inconnue, dec = equations.analyser(saisie)
                self.assertEqual(inconnue, x)
                self.assertFalse(dec)

    def test_notation_suisse(self):
        """Apostrophe des milliers, virgule (ou point) décimale, x² du clavier de téléphone."""
        g, d, x, dec = equations.analyser("1’000x^2 = 4’000")
        self.assertEqual((sd.vers_polynome(g, x), sd.vers_polynome(d, x), dec), (sd.Polynome([0, 0, 1000]), sd.Polynome([4000]), False))
        g, d, x, dec = equations.analyser("1'000x^2 = 4'000")
        self.assertEqual(sd.vers_polynome(g, x)[2], 1000)
        g, d, x, dec = equations.analyser("2,5x² = 10")
        self.assertEqual((sd.vers_polynome(g, x)[2], expr.tex(g), dec), (F(5, 2), "2{,}5x^{2}", True))
        g, d, x, dec = equations.analyser("2.5x^2 = 10")
        self.assertEqual((sd.vers_polynome(g, x)[2], dec), (F(5, 2), True))
        self.assertMessage("1’00x^2=1", "Une apostrophe dans un nombre est suivie d'exactement 3 chiffres : 1’000.")

    def test_decimaux_de_l_enonce(self):
        """E14 : `decimaux_enonce` vrai dès qu'un nombre est écrit en décimal, dans l'un ou l'autre membre ; une fraction n'en est
        pas un. Les résultats décimaux finis restent décimaux, les autres sont des fractions."""
        for saisie, dec in (("0,5x^2=2", True), ("x^2=0,25", True), ("(1/2)x^2=2", False), ("x^2-0,2x=0", True),
                            ("x^2=1,0", True), ("4x^2=9", False)):
            with self.subTest(saisie=saisie):
                self.assertEqual(equations.analyser(saisie)[3], dec)
        self.assertIs(exp_log._a_des_decimaux, expr.a_des_decimaux)               # déplacé d'Exp-log (§ 13.2, Q2)
        res = sd.resoudre_equation(*equations.analyser("0,2x^2-0,5x=0,3"))
        self.assertEqual(res["S"], r"S = \{-0{,}5\,;\,3\}")
        res = sd.resoudre_equation(*equations.analyser("(1/5)x^2-(1/2)x=3/10"))
        self.assertEqual(res["S"], r"S = \{-\frac{1}{2}\,;\,3\}")

    def test_x_plus_1_x_plus_3_egal_15(self):
        """§ 7 : la saisie est lue telle quelle (produit non développé), puis développée par la résolution (double distribution)."""
        g, d, x, dec = equations.analyser("(x + 1)(x + 3) = 15")
        self.assertEqual((expr.tex(g), expr.tex(d), x, dec), ("(x + 1)(x + 3)", "15", "x", False))
        res = sd.resoudre_equation(g, d, x, dec)
        self.assertEqual(res["statut"], "resolu")
        self.assertEqual(res["S"], r"S = \{-6\,;\,2\}")
        self.assertEqual(res["etapes"][0]["lignes"][2], (r"\iff", "x^{2} + 3x + x + 3 = 15", "double distribution"))

    def test_az_4_1_g(self):
        """Az 4.1 g : la saisie est acceptée (une inconnue, aucun dénominateur) ; le développement donne 1 = 1, l'identité est
        rédigée en P4b."""
        g, d, x, dec = equations.analyser("(2x-1)^2-4x(x-1)=1")
        self.assertEqual((x, dec), ("x", False))
        self.assertTrue(sd.ramener(g, d, x)["P"].nul())

    def test_e_puissance_x(self):
        self.assertMessage("e^x=2", "Écrivez une équation avec une seule inconnue.")
        self.assertMessage("e^x = 2x", "Écrivez une équation avec une seule inconnue.")

    def test_meme_lecture_que_le_corpus(self):
        """Toutes les saisies du corpus (P2B, P3) : mêmes arbres que la lecture commune, l'inconnue et les décimaux ; la résolution
        de la saisie analysée est celle du corpus."""
        from test_redaction_second_degre import lire, resoudre
        for nom, saisie in RESOLUES.items():
            with self.subTest(nom=nom):
                lu = equations.analyser(saisie)
                self.assertEqual(lu, lire(saisie))
                self.assertEqual(sd.resoudre_equation(*lu)["S"], resoudre(saisie)["S"])


if __name__ == "__main__":
    unittest.main()
