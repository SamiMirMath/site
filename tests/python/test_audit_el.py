"""T33 — Corrections après la chasse aux trous du 27.10.2026 : chaque forme trouvée par l'audit (batterie BATTERIE_AUDIT de cas_el.py) est résolue
juste dans les deux méthodes (oracle mpmath), avec la rédaction décidée ; aucune saisie d'une grille de formes du chapitre ne lève d'exception."""
import random
import re
import unittest

import moteurs  # noqa: F401  (chemins des moteurs)
import exp_log as el
import resoudre_el as rel
import sortie as so
from cas_el import BATTERIE_AUDIT, HORS_PROGRAMME, PAS_ENCORE, entrees_el
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
                    if attendu is None:                    # tout réel
                        self.assertIsNone(r["solutions"])
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
            r"\iff x^{2} \cdot \log(2) = 0 \quad \text{(log(1) = 0)} \iff x^{2} = 0 \quad \text{(car } \log(2) \neq 0\text{)} \iff x = 0"))
        self.assertTrue(lignes("2^(x^2)*3^(x^2)=1")[0].endswith(                    # plusieurs facteurs : le développement, puis x² = 0
            r"\iff x^{2} = 0 \quad \text{(car } \log(2) + \log(3) \neq 0\text{)} \iff x = 0"))
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


class TestIsolerLesExponentielles(unittest.TestCase):
    """Groupe 3 (T1, T5) : la carte « Isoler les exponentielles » vient d'abord, dans les deux méthodes ; une somme d'exponentielles nulle n'a aucune solution."""

    def cartes(self, saisie, methode=el.METHODE_LOGARITHMES):
        return [c["titre"] for c in corriger(saisie, methode)["etapes"]]

    def test_un_terme_de_l_autre_cote(self):
        self.assertEqual(lignes("2^x-3^(x+1)=0")[0], r"2^{x} - 3^{x + 1} = 0 \iff 2^{x} = 3^{x + 1} \quad \text{(on passe un terme de l'autre côté)}")
        self.assertEqual(lignes("0=2*3^x-5*2^x")[0],
                         r"0 = 2 \cdot 3^{x} - 5 \cdot 2^{x} \iff 2 \cdot 3^{x} = 5 \cdot 2^{x} \quad \text{(on passe un terme de l'autre côté)}")
        for methode in el.METHODES:
            self.assertEqual(self.cartes("2^x-3^(x+1)=0", methode)[0], "Isoler les exponentielles")
        self.assertEqual(self.cartes("4^x-2^(x+1)=0", el.METHODE_MEME_BASE), ["Isoler les exponentielles", "Même base"])

    def test_somme_nulle_aucune_solution(self):
        for saisie in ["2^x+3^(x+1)=0", "e^x+2^x=0", "-2^x-5^x=0"]:
            with self.subTest(saisie):
                v = resultats(saisie)
                self.assertEqual(rendu(v[el.METHODE_MEME_BASE]), rendu(v[el.METHODE_LOGARITHMES]))
                self.assertEqual(self.cartes(saisie), ["Isoler les exponentielles", "Aucune solution"])
                self.assertEqual(el.tex_solution(corriger(saisie)), r"S = \varnothing")
        self.assertEqual(lignes("2^x+3^(x+1)=0"), [
            r"2^{x} + 3^{x + 1} = 0 \iff 2^{x} = -3^{x + 1} \quad \text{(on passe un terme de l'autre côté)}",
            r"2^{x} > 0 \quad \text{(une exponentielle est strictement positive)}", r"-3^{x + 1} < 0 \quad \text{(aucune solution)}"])

    def test_deux_membres_negatifs_et_denominateur(self):
        self.assertEqual(lignes("-2^x=-3^(x+1)")[0], r"-2^{x} = -3^{x + 1} \iff 2^{x} = 3^{x + 1} \quad \text{(on multiplie les deux membres par −1)}")
        self.assertEqual(lignes("3^(x+1)/2^x=1", el.METHODE_MEME_BASE)[0],          # méthode B : log(u/v) = log u − log v (groupe 4)
                         r"\frac{3^{x + 1}}{2^{x}} = 1 \iff 3^{x + 1} = 2^{x} \quad \text{(on multiplie les deux membres par le dénominateur)}")

    def test_produit_nul_d_une_difference(self):
        self.assertEqual(self.cartes("(2^x-3^x)(5^x-25)=0"), ["Produit nul", "Facteur 1", "Facteur 2"])


class TestQuotients(unittest.TestCase):
    """Groupe 4 (T2) : méthode A, aᵐ/aⁿ = aᵐ⁻ⁿ (même base) ou multiplier les deux membres ; méthode B, log(u/v) = log u − log v."""

    def test_meme_base_puissance_d_un_quotient(self):
        self.assertEqual(lignes("8/2^x=2", el.METHODE_MEME_BASE)[0], r"\frac{8}{2^{x}} = \frac{2^{3}}{2^{x}} = 2^{-x + 3} \quad \text{(aᵐ / aⁿ = aᵐ⁻ⁿ)}")
        self.assertEqual(el.tex_solution(corriger("8/2^x=2", el.METHODE_MEME_BASE)), r"S = \left\{2\right\}")
        self.assertEqual(el.tex_solution(corriger("2^(x+1)/2^x=2", el.METHODE_MEME_BASE)), r"S = \mathbb{R}")

    def test_methode_a_multiplie_les_deux_membres(self):
        self.assertEqual(lignes("3/e^x=6", el.METHODE_MEME_BASE), [
            r"\frac{3}{e^{x}} = 6 \iff 3 = 6e^{x} \quad \text{(on multiplie les deux membres par le dénominateur)} "
            r"\iff \frac{1}{2} = e^{x} \quad \text{(on isole le terme exponentiel)}",
            r"\frac{1}{2} = e^{x} \iff e^{x} = \frac{1}{2} \iff x = \ln\left(\frac{1}{2}\right) \quad \text{(définition du logarithme)}"])

    def test_methode_b_logarithme_d_un_quotient(self):
        self.assertIn(r"\iff \log(8) - \log(2^{x}) = \log(2) \quad \text{(log(a/b) = log a − log b)}", lignes("8/2^x=2")[0])
        self.assertIn(r"\iff \ln(3) - \ln(e^{x}) = \ln(6) \quad \text{(ln(a/b) = ln a − ln b)}", lignes("3/e^x=6")[0])
        self.assertTrue(lignes("3/e^x=6")[0].endswith(r"\iff x = \ln(3) - \ln(6)"))                  # jamais x · (−1)
        self.assertIn(r"\iff \log(3) + \log(2^{x}) - \log(4^{x}) = \log(5) \quad \text{(propriétés des logarithmes)}", lignes("3*2^x/4^x=5")[0])
        for saisie in ["8/2^x=2", "3/e^x=6", "2^x/3^x=1"]:
            self.assertEqual([c["titre"] for c in corriger(saisie)["etapes"]], ["Logarithme des deux membres"])

    def test_methode_a_seule_quand_b_diviserait_par_zero(self):
        for saisie, fin in [("4^x=2^(2x)", r"S = \mathbb{R}"), ("2^(2x)/4^(x-1)=8", r"S = \varnothing")]:
            with self.subTest(saisie):
                s = rel.resoudre(saisie)
                self.assertTrue(s["ok"])
                self.assertNotIn("variantes", s)
                self.assertEqual(s["cartes"][-1]["blocs"][0]["tex"], fin)
                self.assertEqual(corriger(saisie)["genre"], "meme_base")


class TestExposantDuSecondDegre(unittest.TestCase):
    """Groupe 5 (T3) : a^(P(x)) = c ⇔ P(x) · log(a) = log(c) ⇔ P(x) = log(c)/log(a) ; x² = k donne x = ±√k, k < 0 aucune solution (un carré est
    positif ou nul) ; la forme générale par le discriminant, Δ, x₁ et x₂ nommés."""

    def test_x_carre_egal_k(self):
        self.assertEqual(lignes("2^(x^2)=5"), [
            r"2^{x^{2}} = 5 \iff \log(2^{x^{2}}) = \log(5) \quad \text{(log des deux membres)} \iff x^{2} \cdot \log(2) = \log(5) "
            r"\quad \text{(log(a^A) = A · log(a))} \iff x^{2} = \frac{\log(5)}{\log(2)} \quad \text{(car } \log(2) \neq 0\text{)}",
            r"x_{1} = -\sqrt{\frac{\log(5)}{\log(2)}}", r"x_{2} = \sqrt{\frac{\log(5)}{\log(2)}}"])          # nommés : la ligne finale tient à 360 px
        self.assertEqual(el.tex_solution(corriger("2^(x^2)=5")), r"S = \left\{x_{1} \,;\, x_{2}\right\} \text{, soit } x \approx -1{,}524 \text{ ou } x \approx 1{,}524")
        self.assertTrue(lignes("2^(x^2-1)=5")[0].endswith(r"\iff x^{2} = 1 + \frac{\log(5)}{\log(2)}"))
        self.assertEqual(lignes("2^(x^2-1)=5")[-1], r"x_{2} = \sqrt{1 + \frac{\log(5)}{\log(2)}}")
        self.assertTrue(lignes("e^(x^2)=2")[0].endswith(r"\iff x^{2} = \ln(2) \quad \text{(car ln(e) = 1)}"))
        self.assertEqual(lignes("e^(x^2)=2", el.METHODE_MEME_BASE), [
            r"e^{x^{2}} = 2 \iff x^{2} = \ln(2) \quad \text{(définition du logarithme)}", r"x_{1} = -\sqrt{\ln(2)}", r"x_{2} = \sqrt{\ln(2)}"])
        self.assertTrue(lignes("10^(x^2)=10000")[-1].endswith(r"\iff x^{2} = 4 \quad \text{(car log(10) = 1)} \iff x = -2 \text{ ou } x = 2"))   # racine exacte : en ligne

    def test_k_negatif_aucune_solution(self):
        self.assertEqual(lignes("2^(x^2)=1/2")[1:], [r"x^{2} \ge 0 \quad \text{(un carré est positif ou nul)}",
                                                     r"\frac{\log\left(\frac{1}{2}\right)}{\log(2)} < 0 \quad \text{(aucune solution)}"])
        self.assertEqual(el.tex_solution(corriger("2^(x^2)=1/2")), r"S = \varnothing")

    def test_forme_generale_par_le_discriminant(self):
        self.assertEqual(lignes("2^(x^2+x)=5")[1:], [
            r"Δ = 1^{2} - 4 \cdot 1 \cdot \left(-\frac{\log(5)}{\log(2)}\right) = 1 + 4 \cdot \frac{\log(5)}{\log(2)} \quad \text{(formule du discriminant)}",
            r"x_{1} = \frac{-1 - \sqrt{Δ}}{2}", r"x_{2} = \frac{-1 + \sqrt{Δ}}{2}"])
        self.assertTrue(lignes("2^(x^2+x)=5")[0].endswith(r"\iff x^{2} + x - \frac{\log(5)}{\log(2)} = 0"))
        self.assertEqual(el.tex_solution(corriger("2^(x^2+x)=5")), r"S = \left\{x_{1} \,;\, x_{2}\right\} \text{, soit } x \approx -2{,}104 \text{ ou } x \approx 1{,}104")

    def test_bases_differentes(self):
        self.assertIn(r"\iff x(x \cdot \log(2) - \log(3)) = 0", lignes("2^(x^2)=3^x")[0])
        self.assertEqual(corriger("2^(x^2)*3^x=6")["genre"], "logarithmes")


class TestBaseInconnue(unittest.TestCase):
    """Groupe 6 (T7) : log_x(n) = k avec k ≤ 0 ou n = 1."""

    def test_exposant_negatif(self):
        self.assertEqual(lignes("log_x(8)=-1")[1], r"\log_{x}(8) = -1 \iff x^{\log_{x}(8)} = x^{-1} \quad \text{(exponentielle des deux membres)} "
                                                   r"\iff 8 = x^{-1} \quad \text{(a^(log_a(A)) = A, A > 0)} \iff 8 = \frac{1}{x} \quad \text{(a⁻ᵐ = 1/aᵐ)} "
                                                   r"\iff x = \frac{1}{8}")
        self.assertEqual(el.tex_solution(corriger("log_x(4)=-2")), r"S = \left\{\frac{1}{2}\right\}")
        self.assertIn(r"x = \frac{1}{2} \quad \text{(seule la solution positive convient)}", lignes("log_x(4)=-2"))

    def test_exposant_nul(self):
        r = corriger("log_x(5)=0")
        self.assertTrue(lignes("log_x(5)=0")[1].endswith(r"\iff 5 = 1 \quad \text{(a⁰ = 1)}"))
        self.assertEqual(r["remarque"], "Cette égalité est fausse : l'équation n'a aucune solution.")
        self.assertEqual(el.tex_solution(r), r"S = \varnothing")
        r = corriger("log_x(1)=0")
        self.assertEqual(r["remarque"], "Cette égalité est vraie pour toute base x > 0 et différente de 1.")
        self.assertEqual(el.tex_solution(r), r"S = \left]0 \,;\, 1\right[ \cup \left]1 \,;\, +\infty\right[")

    def test_argument_un(self):
        self.assertEqual(lignes("log_x(1)=2")[-1], r"x = 1 \text{ et } x = -1 \text{ ne conviennent pas} "
                                                   r"\quad \text{(une base de logarithme est strictement positive et différente de 1)}")
        self.assertEqual(lignes("log_x(1)=3")[-1], r"x = 1 \text{ ne convient pas} \quad \text{(une base de logarithme est strictement positive et différente de 1)}")
        for saisie in ["log_x(1)=2", "log_x(1)=3", "log_x(1)=-1"]:
            self.assertEqual(el.tex_solution(corriger(saisie)), r"S = \varnothing", saisie)


class TestProduitNulPolynomeExponentielle(unittest.TestCase):
    """Groupe 7 (T8) : x · 2^x = 0 ⇔ x = 0 ou 2^x = 0, et 2^x = 0 n'a aucune solution."""

    def test_redaction(self):
        r = corriger("x*2^x=0")
        self.assertEqual([c["titre"] for c in r["etapes"]], ["Produit nul", "Facteur 1", "Facteur 2"])
        self.assertEqual(lignes("x*2^x=0"), [
            r"x \cdot 2^{x} = 0 \iff x = 0 \text{ ou } 2^{x} = 0 \quad \text{(un produit est nul si l'un des facteurs est nul)}", "x = 0",
            r"2^{x} > 0 \quad \text{(une exponentielle est strictement positive)}", r"2^{x} = 0 \quad \text{(aucune solution)}"])
        self.assertEqual(lignes("10^x*(x-4)=0")[-1], r"x - 4 = 0 \iff x = 4")
        v = resultats("x*2^x=0")
        self.assertEqual(rendu(v[el.METHODE_MEME_BASE]), rendu(v[el.METHODE_LOGARITHMES]))

    def test_facteur_constant_et_trinome_sans_solution(self):
        self.assertEqual(lignes("3x*2^x=0")[0],
                         r"3x \cdot 2^{x} = 0 \iff x = 0 \text{ ou } 2^{x} = 0 \quad \text{(un produit est nul si l'un des facteurs est nul)}")
        self.assertEqual(el.tex_solution(corriger("(x^2+1)*2^x=0")), r"S = \varnothing")
        self.assertIsNone(el.corriger_equation(*el.lire_membres("(x-1)(x+2)=0"), "x"))        # sans exponentielle : pas une équation du chapitre


class TestLogarithmeDeXCarre(unittest.TestCase):
    """Groupe 8 (T4 limité) : log(x²) = c, ln(x²) = c, log_a(x²) = c par l'exponentielle des deux membres, x² = 10^c ⇔ x = ±√(10^c), jamais 2 log(x)."""

    def test_redaction(self):
        self.assertEqual(lignes("log(x^2)=-1")[:3], [
            r"\log(x^{2}) = -1 \iff 10^{\log(x^{2})} = 10^{-1} \quad \text{(exponentielle des deux membres)} "
            r"\iff x^{2} = 10^{-1} = \frac{1}{10} \quad \text{(10^(log(A)) = A, A > 0)}", r"x_{1} = -\sqrt{\frac{1}{10}}", r"x_{2} = \sqrt{\frac{1}{10}}"])
        self.assertTrue(lignes("ln(x^2)=1")[0].endswith(r"\iff x^{2} = e \quad \text{(e^(ln(A)) = A, A > 0)}"))
        self.assertEqual(lignes("ln(x^2)=1")[1:3], [r"x_{1} = -\sqrt{e}", r"x_{2} = \sqrt{e}"])
        self.assertEqual([c["titre"] for c in corriger("log_2(x^2)=-1")["etapes"]], ["Exponentielle des deux membres", "Vérification"])

    def test_jamais_deux_log_de_x_et_trinome_general_plus_tard(self):
        for saisie in ["log(x^2)=-1", "ln(x^2)=1", "log(x^2)=1,5", "2ln(x^2)-5=0"]:
            texte = " ".join(lignes(saisie))
            self.assertNotIn(r"2\log(x)", texte)
            self.assertNotIn(r"2\ln(x)", texte)
            self.assertNotIn(r"\left|", texte)
        self.assertEqual(rel.resoudre("log(x^2-1)=1/2"), {"ok": False, "erreur": el.MESSAGE_PAS_ENCORE})


class TestExposantsEnChiffresSuperieurs(unittest.TestCase):
    """Groupe 9 (D3) : ² et ³ se lisent ^2 et ^3."""

    def test_meme_arbre_et_meme_corrige(self):
        for saisie, ecrite in [("x²=4", "x^2=4"), ("2^(x²)*4^x=8", "2^(x^2)*4^x=8"), ("log(x²)=2", "log(x^2)=2"), ("(x+1)³=8", "(x+1)^3=8"),
                               ("2^(x³)=8", "2^(x^3)=8"), ("10²", "10^2")]:
            with self.subTest(saisie):
                self.assertEqual(el.lire_membres(saisie), el.lire_membres(ecrite))
                self.assertEqual(rel.resoudre(saisie), rel.resoudre(ecrite))
        self.assertEqual(el.apercu("2^(x²)=5"), el.apercu("2^(x^2)=5"))

    def test_l_exposant_compose_demande_toujours_des_parentheses(self):
        self.assertEqual(rel.resoudre("2^x²=5")["erreur"], "Mettez les exposants entre parenthèses : 2^(3^2) ou (2^3)^2.")


class TestFusionDesPuissances(unittest.TestCase):
    """Méthode A : un produit ou un quotient de puissances de 10 ou de e se fusionne, puis la définition du logarithme conclut (plus de « il faut les logarithmes »)."""

    def test_quotient_de_puissances_de_e(self):
        r = corriger("e^(2x)/e^x=5", el.METHODE_MEME_BASE)
        self.assertNotIn("message", r)
        self.assertEqual([c["titre"] for c in r["etapes"]], ["Définition du logarithme"])
        self.assertEqual(lignes("e^(2x)/e^x=5", el.METHODE_MEME_BASE),
                         [r"\frac{e^{2x}}{e^{x}} = 5 \iff e^{x} = 5 \quad \text{(aᵐ / aⁿ = aᵐ⁻ⁿ)} \iff x = \ln(5) \quad \text{(définition du logarithme)}"])
        self.assertEqual([el.tex(n) for n in r["solutions"]], [r"\ln(5)"])

    def test_produit_et_base_10(self):
        self.assertIn(r"e^{2x + 1} = 5 \quad \text{(aᵐ · aⁿ = aᵐ⁺ⁿ)}", lignes("e^x*e^(x+1)=5", el.METHODE_MEME_BASE)[0])
        self.assertIn(r"10^{x} = 3 \quad \text{(aᵐ / aⁿ = aᵐ⁻ⁿ)}", lignes("10^(2x)/10^x=3", el.METHODE_MEME_BASE)[0])

    def test_autre_base_garde_le_message(self):
        self.assertIsNotNone(corriger("2^(2x)/2^x=5", el.METHODE_MEME_BASE).get("message"))


class TestBaseInconnueArgumentNegatif(unittest.TestCase):
    """log_x(n) = k avec n ≤ 0 : S = ∅, une base admissible est strictement positive donc xᵏ > 0."""

    def test_redaction(self):
        r = corriger("log_x(-8)=3")
        self.assertEqual([c["titre"] for c in r["etapes"]], ["Condition", "Définition du logarithme", "Aucune solution"])
        self.assertEqual(lignes("log_x(-8)=3")[1:],
                         [r"\log_{x}(-8) = 3 \iff x^{3} = -8 \quad \text{(définition du logarithme)}",
                          r"x^{3} > 0 \quad \text{(une base admissible est strictement positive, donc xᵏ > 0)}",
                          r"-8 < 0 \quad \text{(aucune solution)}"])
        self.assertEqual(r["solutions"], [])
        self.assertEqual(el.tex_solution(r), r"S = \varnothing")

    def test_argument_nul(self):
        self.assertEqual(lignes("log_x(0)=2")[-1], r"x^{2} = 0 \quad \text{(aucune solution)}")

    def test_argument_positif_inchange(self):
        self.assertEqual([round(el.valeur(n), 3) for n in corriger("log_x(8)=3")["solutions"]], [2.0])


class TestOrdreDesSolutions(unittest.TestCase):
    """Les solutions sont toujours en ordre croissant (S, lignes « x = … ou x = … », x₁ < x₂), et les deux méthodes donnent S dans le même ordre."""

    @staticmethod
    def ou(r):
        return [e for c in r["etapes"] for l in c["lignes"] if isinstance(l, el.Chaine) for e in l.elements if isinstance(e, el.Ou)]

    def test_croissant_et_meme_ordre_dans_les_deux_methodes(self):
        n = 0
        for saisie in list(dict.fromkeys(entrees_el() + grille())):
            try:
                s = el.analyser_saisie(saisie)
            except Exception:
                continue
            if s.genre != "equation":
                continue
            res = resultats(saisie)
            valeurs = {}
            for methode, r in res.items():
                if r is None or r.get("message"):
                    continue
                with self.subTest(saisie=saisie, methode=methode):
                    v = [el.valeur(x) for x in r["solutions"] or []]
                    self.assertEqual(v, sorted(v))
                    for o in self.ou(r):
                        w = [el.valeur(e.d) for e in o.eqs]
                        self.assertEqual(w, sorted(w), el.tex_chaine(el.Chaine([o])))
                valeurs[methode] = [round(el.valeur(x), 6) for x in r["solutions"] or []]
                n += 1
            if len(valeurs) == 2:
                with self.subTest(saisie=saisie):
                    self.assertEqual(valeurs[el.METHODE_MEME_BASE], valeurs[el.METHODE_LOGARITHMES])
        self.assertGreater(n, 1000)


class TestMiseEnEvidence(unittest.TestCase):
    """Correction 4 (D1) : somme de termes de même base dont les exposants diffèrent d'un entier ; carte « Mise en évidence » commune aux deux méthodes."""
    A, B = el.METHODE_MEME_BASE, el.METHODE_LOGARITHMES

    def carte(self, saisie, methode):
        return corriger(saisie, methode)["etapes"][0]

    def test_la_carte_est_la_meme_dans_les_deux_methodes(self):
        for saisie in ["2^x+2^(x+1)=12", "2^x+2^x=8", "2^(x+2)-2^x=12", "2^x+2^(x+1)+3=15", "2^x-2^x=3", "2^x-2^(x+1)=4", "12=2^x+2^(x+1)+3"]:
            with self.subTest(saisie):
                a, b = self.carte(saisie, self.A), self.carte(saisie, self.B)
                self.assertEqual(a["titre"], "Mise en évidence")
                self.assertEqual([el.tex_chaine(l) for l in a["lignes"]], [el.tex_chaine(l) for l in b["lignes"]])

    def test_exposant_decale_puis_mise_en_evidence_puis_isolement(self):
        self.assertEqual(lignes("2^x+2^(x+1)=12", self.A)[:2], [
            r"2^{x + 1} = 2^{x} \cdot 2 \quad \text{(aᵐ⁺ⁿ = aᵐ · aⁿ)}",
            r"2^{x} + 2^{x + 1} = 12 \iff 2^{x} \cdot (1 + 2) = 12 \quad \text{(mise en évidence)} \iff 3 \cdot 2^{x} = 12 "
            r"\iff 2^{x} = 4 \quad \text{(on isole le terme exponentiel)}"])
        self.assertEqual(lignes("2^(x+2)-2^x=12", self.B)[0], r"2^{x + 2} = 2^{x} \cdot 2^{2} \quad \text{(aᵐ⁺ⁿ = aᵐ · aⁿ)}")
        self.assertIn(r"2^{x} \cdot (2^{2} - 1) = 12", lignes("2^(x+2)-2^x=12", self.B)[1])

    def test_coefficient_puissance_de_la_base_fondu(self):
        for methode in (self.A, self.B):
            self.assertEqual(lignes("2^x+2^x=8", methode)[0], r"2^{x} + 2^{x} = 8 \iff 2^{x} \cdot (1 + 1) = 8 \quad \text{(mise en évidence)} "
                             r"\iff 2^{x} \cdot 2 = 8 \iff 2^{x + 1} = 8 \quad \text{(aᵐ · aⁿ = aᵐ⁺ⁿ)}")
        self.assertIn(r"\iff 2^{x} \cdot 4 = 16 \iff 2^{x} \cdot 2^{2} = 16 \iff 2^{x + 2} = 16", lignes("2*2^x+2^(x+1)=16", self.A)[1])

    def test_constante_isolee_d_abord(self):
        self.assertIn(r"2^{x} + 2^{x + 1} + 3 = 15 \iff 2^{x} + 2^{x + 1} = 12 \quad \text{(on isole le terme exponentiel)} \iff 2^{x} \cdot (1 + 2) = 12",
                      lignes("2^x+2^(x+1)+3=15", self.A)[1])

    def test_coefficient_nul_ou_negatif(self):
        self.assertIsNone(corriger("2^x-2^x=0", self.A)["solutions"])
        self.assertEqual(el.tex_solution(corriger("2^x-2^x=0", self.B)), r"S = \mathbb{R}")
        self.assertEqual(corriger("2^x-2^x=3", self.A)["solutions"], [])
        self.assertEqual(lignes("2^x-2^x=3", self.B)[0], r"2^{x} - 2^{x} = 3 \iff 2^{x} \cdot (1 - 1) = 3 \quad \text{(mise en évidence)} \iff 2^{x} \cdot 0 = 3 \iff 0 = 3")
        for saisie in ["2^x-2^(x+1)=4", "-2^x-2^(x+1)=12"]:
            for methode in (self.A, self.B):
                with self.subTest(saisie=saisie, methode=methode):
                    r = corriger(saisie, methode)
                    self.assertEqual([c["titre"] for c in r["etapes"]], ["Mise en évidence", "Aucune solution"])
                    self.assertEqual(r["solutions"], [])

    def test_coefficient_irrationnel_en_base_e(self):
        """e^x + e^(x+1) = 5 ⇔ e^x (1 + e) = 5 ⇔ e^x = 5/(1 + e) ⇔ x = ln(5/(1 + e)) ≈ 0,296 ; coefficient négatif ou quotient négatif : « Aucune solution »."""
        for methode in (self.A, self.B):
            with self.subTest(methode=methode):
                self.assertEqual(lignes("e^x+e^(x+1)=5", methode)[1], r"e^{x} + e^{x + 1} = 5 \iff e^{x} \cdot (1 + e) = 5 \quad \text{(mise en évidence)} "
                                 r"\iff e^{x} = \frac{5}{1 + e} \quad \text{(on isole le terme exponentiel)}")
                self.assertEqual(el.tex_solution(corriger("e^x+e^(x+1)=5", methode)), r"S = \left\{\ln\left(\frac{5}{1 + e}\right)\right\} \text{, soit } x \approx 0{,}296")
                r = corriger("e^x-e^(x+1)=5", methode)
                self.assertEqual([c["titre"] for c in r["etapes"]], ["Mise en évidence", "Aucune solution"])
                self.assertEqual(r["solutions"], [])
        self.assertEqual(lignes("e^x+e^(x+1)=5", self.A)[2], r"e^{x} = \frac{5}{1 + e} \iff x = \ln\left(\frac{5}{1 + e}\right) \quad \text{(définition du logarithme)}")
        self.assertTrue(lignes("e^x+e^(x+1)=5", self.B)[2].endswith(r"\iff x = \ln\left(\frac{5}{1 + e}\right) \quad \text{(car ln(e) = 1)}"))

    def test_tout_coefficient_positif_suffit(self):
        """Coefficient rationnel quelconque (7 + 8, 1/3 + 2/3, 1 + 10) ou irrationnel : la mise en évidence aboutit dans les deux méthodes."""
        for saisie, attendu in [("7*2^x+2^(x+3)=60", 2.0), ("2^x/3+2^(x+1)/3=2", 1.0), ("3^x+3^(x+2)=30", 1.0), ("e^(x+1)-e^x=3", 0.557)]:
            for methode in (self.A, self.B):
                with self.subTest(saisie=saisie, methode=methode):
                    self.assertEqual([round(el.valeur(n), 3) for n in corriger(saisie, methode)["solutions"]], [attendu])

    def test_formes_qui_restent_hors_de_la_methode(self):
        for saisie in ["4^x-2^x-6=0", "e^x+e^(-x)=3", "2^x+1=3^x", "2^x+2^(x+1)=3^x"]:
            self.assertEqual(rel.resoudre(saisie), {"ok": False, "erreur": el.MESSAGE_HORS_PROGRAMME})


class TestMessages(unittest.TestCase):
    def test_sans_exponentielle_ni_logarithme(self):
        """Correction 3 : x² = 4, 2x + 1 = 9 ne sont pas « pas encore » : l'outil dit ce qu'il traite."""
        for saisie in ["x^2=4", "x²=4", "2x+1=9", "sqrt(x)=3", "(x+1)^3=8", "3x=6"]:
            with self.subTest(saisie):
                self.assertEqual(rel.resoudre(saisie), {"ok": False, "erreur": el.MESSAGE_SANS_EXP_LOG})
        self.assertEqual(el.MESSAGE_SANS_EXP_LOG, "Cet outil traite les équations exponentielles et logarithmiques.")
        for saisie in ["x^x=4", "2^(x^3)=8", "log(x)+log(2)=1", "log(2)*x=3"]:      # une exponentielle ou un logarithme : un autre message
            with self.subTest(saisie):
                self.assertNotEqual(rel.resoudre(saisie)["erreur"], el.MESSAGE_SANS_EXP_LOG)

    def test_logarithme_et_terme_en_x_ou_exponentielle_hors_programme(self):
        """Groupe 2 : un logarithme avec un terme en x ou une exponentielle (de part et d'autre, ou en facteur) n'est pas une équation du cours."""
        for saisie in ["log(x)=x-1", "ln(x)=x", "x*log(x)=1", "e^x=ln(x)", "log(x)=2^x", "log(x)/x=1", "ln(x)+x=2", "2^x*log(x)=1"]:
            with self.subTest(saisie):
                self.assertEqual(rel.resoudre(saisie), {"ok": False, "erreur": el.MESSAGE_HORS_PROGRAMME})
        for saisie in ["log(x)=log(5)", "log(x)+log(x-1)=1", "2^(x^3)=8"]:            # formes du programme pas encore gérées
            with self.subTest(saisie):
                self.assertEqual(rel.resoudre(saisie), {"ok": False, "erreur": el.MESSAGE_PAS_ENCORE})

    def test_second_degre_en_a_puissance_x_hors_programme_quelle_que_soit_la_base(self):
        """Groupe 10 (D2) : le même message pour 4^x − 2^x − 6 = 0 et e^(2x) − 3e^x + 2 = 0 (avant : « hors programme » ou « pas encore » selon la base) ;
        la mise en évidence (D1) est au programme : voir TestMiseEnEvidence."""
        for saisie in ["4^x-2^x-6=0", "9^x-3^x=6",
                       "4^x+2^x=6", "e^(2x)-3e^x+2=0", "e^x+e^(-x)=3", "2^(2x)-5*2^x+4=0", "3^(2x)-4*3^x+3=0", "2^x+2^(-x)=2", "2*4^x-3*2^x+1=0"]:
            with self.subTest(saisie):
                self.assertEqual(rel.resoudre(saisie), {"ok": False, "erreur": el.MESSAGE_HORS_PROGRAMME})

    def test_aucune_forme_resolue_n_est_classee_hors_programme(self):
        for saisie, _ in BATTERIE_AUDIT:
            with self.subTest(saisie):
                s = el.analyser_saisie(saisie)
                self.assertFalse(el.hors_programme(s.g, s.d, s.inconnue))


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
