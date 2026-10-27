"""T33 — Corrections après la chasse aux trous du 27.10.2026 : chaque forme trouvée par l'audit (batterie BATTERIE_AUDIT de cas_el.py) est résolue
juste dans les deux méthodes (oracle mpmath), avec la rédaction décidée ; aucune saisie d'une grille de formes du chapitre ne lève d'exception."""
import random
import re
import unittest

import moteurs  # noqa: F401  (chemins des moteurs)
import exp_log as el
import resoudre_el as rel
import sortie as so
from cas_el import BATTERIE_AUDIT, HORS_PROGRAMME, PAS_ENCORE
from exp_log import Eq, Log, Nb, Neg, Op, E
from test_exp_log import MP, corriger, evaluer, rendu, vrai


def lignes(saisie, methode=el.METHODE_LOGARITHMES):
    return [el.tex_chaine(l) for c in corriger(saisie, methode)["etapes"] for l in c["lignes"] if not isinstance(l, el.Message)]


def resultats(saisie):
    """Le résultat de chaque méthode : les deux variantes d'une équation exponentielle, sinon l'unique corrigé."""
    s = el.analyser_saisie(saisie)
    v = el.variantes_equation(s.g, s.d, s.inconnue)
    return v if v is not None else {"-": el.corriger_equation(s.g, s.d, s.inconnue)}


# Grille de formes du chapitre : aucune ne doit lever d'exception (F5), chaque sortie respecte le format commun
BASES = ["2", "3", "10", "e", "(1/2)", "0,5", "4"]
EXPOSANTS = ["x", "-x", "x+1", "2x-3", "x/2", "x^2", "x^2-1", "x^2+x", "x^2-3x+2"]
SECONDS = ["1", "8", "5", "1/2", "0", "-4", "0,3"]


def puissance(a, p):
    return f"{a}^{p}" if p == "x" else f"{a}^({p})"


def grille():
    rng = random.Random(27102026)
    saisies = []
    for a in BASES:
        for p in EXPOSANTS:
            for c in SECONDS:
                saisies += [f"{puissance(a, p)}={c}", f"3*{puissance(a, p)}-2={c}"]
    for _ in range(300):
        a, b, p, q, c = rng.choice(BASES), rng.choice(BASES), rng.choice(EXPOSANTS), rng.choice(EXPOSANTS), rng.choice(SECONDS)
        A, B = puissance(a, p), puissance(b, q)
        saisies += [f"{A}={B}", f"2*{A}=5*{B}", f"{A}*{B}={c}", f"{A}/{B}={c}", f"{A}-{B}=0", f"{A}+{B}=0", f"({A}-{c})({B}-2)=0",
                    f"{A}+{B}={c}", f"x*{A}=0", f"{c}/{A}=2"]
    for p in ["x", "x+1", "2x-3", "5-x", "-x", "x/2", "x^2", "x^2-1", "x^2+x"]:
        for c in ["-2", "0", "1", "1/2", "1,5"]:
            saisies += [f"log({p})={c}", f"ln({p})={c}", f"log_2({p})={c}", f"2*log({p})+1={c}", f"log(log({p}))={c}"]
    for n in ["2", "8", "1", "1/8", "100"]:
        for k in ["1", "2", "-1", "-2", "0", "1/2"]:
            saisies.append(f"log_x({n})={k}")
    saisies += ["log(x)+log(2)=1", "log(x)-log(2)=1", "2^x+ln(2)=3", "log(x)=ln(5)", "2^x=ln(5)", "x²=4", "2^(x²)=5", "log(x)=x-1"]
    return list(dict.fromkeys(saisies))


class TestBatterieAudit(unittest.TestCase):
    def test_solutions_attendues_dans_chaque_methode(self):
        for saisie, attendu in BATTERIE_AUDIT:
            for methode, r in resultats(saisie).items():
                with self.subTest(saisie=saisie, methode=methode):
                    self.assertIsNotNone(r)
                    if r.get("message"):                   # la méthode A ne s'applique pas : elle le dit, sans solution
                        self.assertEqual(r["solutions"], [])
                        continue
                    self.assertEqual([round(el.valeur(n), 3) + 0.0 for n in r["solutions"]], [round(v, 3) for v in attendu])

    def test_oracle_les_solutions_verifient_l_equation_de_l_enonce(self):
        for saisie, _ in BATTERIE_AUDIT:
            s = el.analyser_saisie(saisie)
            for methode, r in resultats(saisie).items():
                with self.subTest(saisie=saisie, methode=methode):
                    for n in r["solutions"] or []:
                        self.assertTrue(vrai(Eq(s.g, s.d), evaluer(n)), f"{saisie} : {el.tex(n)}")

    def test_proprietes_de_la_liste(self):
        for saisie, _ in BATTERIE_AUDIT:
            for methode, r in resultats(saisie).items():
                with self.subTest(saisie=saisie, methode=methode):
                    for c in r["etapes"]:
                        for l in c["lignes"]:
                            if isinstance(l, el.Message):
                                continue
                            for p in l.props + [l.note]:
                                self.assertTrue(p is None or p in el.PROPRIETES or isinstance(p, el.Car), (saisie, p))


class TestRacineDouble(unittest.TestCase):
    """F1 à F3 : Δ = 0 donne la ligne « Δ = 0 : une seule solution », puis x = −b/(2a), et S n'a qu'un élément ; x² · log(a) = 0 donne x² = 0, puis x = 0."""

    def test_delta_nul_methode_a(self):
        l = lignes("0,5^(x^2)*0,5^(2x-3)=16", el.METHODE_MEME_BASE)
        self.assertEqual(l[-3:], [r"Δ = (-2)^{2} - 4(-1) \cdot (-1) = 0", r"Δ = 0 \text{ : une seule solution}",
                                  r"x = \frac{-b}{2a} = \frac{2}{2(-1)} = -1"])
        self.assertEqual(el.tex_solution(corriger("0,5^(x^2)*0,5^(2x-3)=16", el.METHODE_MEME_BASE)), r"S = \left\{-1\right\}")
        self.assertEqual(lignes("4^(x^2)=2^(4x-2)", el.METHODE_MEME_BASE)[-1], r"x = \frac{-b}{2a} = \frac{4}{2 \cdot 2} = 1")

    def test_delta_nul_methode_b(self):
        l = lignes("2^(x^2)=2^(2x-1)")
        self.assertEqual(l[1:], [r"Δ = (-2\log(2))^{2} - 4\log(2) \cdot \log(2) = 0 \quad \text{(formule du discriminant)}",
                                 r"Δ = 0 \text{ : une seule solution}", r"x = \frac{-b}{2a} = \frac{2\log(2)}{2\log(2)}"])
        r = corriger("2^(x^2)=2^(2x-1)")
        self.assertEqual(len(r["solutions"]), 1)
        self.assertEqual(el.controle_calculatrice(r), r"Contrôlez à la calculatrice : \(x = \frac{2\log(2)}{2\log(2)} = 1\).")

    def test_x_carre_fois_log_nul(self):
        self.assertTrue(lignes("2^(x^2)=1")[0].endswith(
            r"\iff x^{2} \cdot \log(2) = 0 \quad \text{(log(a^A) = A · log(a))} \iff x^{2} = 0 \quad \text{(car } \log(2) \neq 0\text{)} \iff x = 0"))
        for saisie in ["2^(x^2)=1", "1=5^(x^2)", "(1/2)^(x^2)=1"]:
            for methode in el.METHODES:
                with self.subTest(saisie=saisie, methode=methode):
                    r = corriger(saisie, methode)
                    self.assertEqual(el.tex_solution(r), r"S = \left\{0\right\}")
                    self.assertIsNone(el.controle_calculatrice(r))

    def test_aucune_racine_de_zero_ni_solution_en_double(self):
        for saisie in grille():
            s = rel.resoudre(saisie)
            if not s["ok"]:
                continue
            for v in s.get("variantes") or [{"cartes": s["cartes"]}]:
                with self.subTest(saisie):
                    texte = " ".join(b.get("html") or b.get("tex") for c in v["cartes"] for b in c["blocs"])
                    self.assertNotIn(r"\sqrt{0}", texte)
                    self.assertNotIn(" + -", texte)
            sa = el.analyser_saisie(saisie)
            for methode, r in resultats(saisie).items():
                valeurs = [round(el.valeur(n), 9) for n in r["solutions"] or []]
                self.assertEqual(len(valeurs), len(set(valeurs)), (saisie, methode))


class TestSignes(unittest.TestCase):
    def test_jamais_plus_moins(self):
        """F4 : a + (−b) s'écrit a − b."""
        self.assertEqual(el.tex(Op("+", Nb(1), Neg(Log(Nb(7), E())))), r"1 - \ln(7)")
        self.assertEqual(el.tex(Op("+", Nb(1), Nb(-3))), "1 - 3")
        self.assertEqual(el.tex(Op("+", Nb(1), Neg(Op("+", Nb(2), Nb(3))))), "1 - (2 + 3)")
        self.assertEqual(el.tex_solution(corriger("3x-1=-ln(7)")), r"S = \left\{\frac{1 - \ln(7)}{3}\right\} \text{, soit } x \approx -0{,}315")


class TestRobustesse(unittest.TestCase):
    def test_aucune_exception_et_format_commun(self):
        """F5 : aucune saisie de la grille ne lève d'exception ; log(x) + log(2) = 1 a le message « pas encore »."""
        for saisie in grille():
            with self.subTest(saisie):
                s = rel.resoudre(saisie)
                self.assertEqual(so.valider(s), [])
        for saisie in ["log(x)+log(2)=1", "log(x)-log(2)=1"]:
            self.assertEqual(rel.resoudre(saisie), {"ok": False, "erreur": el.MESSAGE_PAS_ENCORE})

    def test_les_listes_de_messages_restent_sans_solution(self):
        for saisie in HORS_PROGRAMME + PAS_ENCORE:
            with self.subTest(saisie):
                self.assertFalse(rel.resoudre(saisie)["ok"])


if __name__ == "__main__":
    unittest.main()
