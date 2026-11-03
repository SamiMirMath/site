"""Bug : les étapes de la dérivée annonçaient « f'(x) = … » pour un morceau de f
(produit sous un facteur constant, terme d'une somme, signe moins devant) ;
la ligne contredisait alors le résultat final."""
import json
import unittest

import mpmath

from moteurs import ensemble_def as ed, derivee_numerique, proches, texte_etape
import derivee_variations as dv

DEBUT = r"\(f'(x) = "
FIN = r"\)."

CAS = ["3(x*ln(x))", "-(x*ln(x))", "(x+1)/(x-1)/2", "(x*ln(x))*3", "x*ln(x)+x",
       "2(x^2+ln(x))", "-x^2", "3x^2-4x", "x*ln(x)", "(x^2-1)/(x-3)", "x^2-4x+3",
       "x^2*e^(-x)-x/(x^2+1)", "-(x^2-1)/(x-3)", "1/2*sqrt(x)*ln(x)"]


class TestNarrationDerivee(unittest.TestCase):
    def test_lignes_f_prime_egales_au_resultat(self):
        for entree in CAS:
            r = dv.etudier(entree)
            self.assertTrue(r["ok"] and r["deriv_resolu"], entree)
            for it in r["deriv_etapes"]:
                h = texte_etape(it)
                if h.startswith(DEBUT):
                    with self.subTest(f=entree, ligne=h):
                        self.assertTrue(h.endswith(FIN))
                        self.assertEqual(h[:-len(FIN)].rsplit(" = ", 1)[1], r["deriv_tex"])

    def test_resultat_juste(self):
        for entree in CAS:
            f = ed.lire(entree)
            fp = dv._simplifier(dv.derivee_narree(f, [], top=True))
            for t in (0.7, 1.9, 4.3):
                attendu = derivee_numerique(f, t)
                if attendu is None:
                    continue
                with self.subTest(f=entree, x=t):
                    self.assertTrue(proches(ed.evaluer(fp, t), attendu))


class TestSansOperationNeutre(unittest.TestCase):
    """Guide R11 : jamais de « + 0 », « - 0 », « · 1 », « / 1 » dans les étapes (u'(x) = 8x, pas 8x + 0)."""
    ENTREES = CAS + ["sqrt(4x^2+1)/(x+2)", "ln(x^2+1)/x", "(x^3+2x)^4*e^x", "sqrt(x^2-3x+2)", "(2x+1)/(x^2+1)",
                     "e^(x^2+1)", "ln(x^2+1)", "(x^2+1)^3", "x/(x^2+4)", "sqrt(x^2+1)*e^x", "x^(1/3)*(x^2+1)"]

    def test_aucune_operation_neutre(self):
        import re
        motif = re.compile(r"(?:[+-] 0(?![\d.,{])|\\cdot 1(?![\d.,{])|\\frac\{[^{}]*\}\{1\}|\\dfrac\{[^{}]*\}\{1\})")
        for entree in self.ENTREES:
            r = dv.etudier(entree)
            for it in r["deriv_etapes"]:
                with self.subTest(f=entree, ligne=texte_etape(it)):
                    self.assertIsNone(motif.search(texte_etape(it)), texte_etape(it))

    def test_derivee_interne_sans_zero(self):
        h = " ".join(texte_etape(it) for it in dv.etudier("sqrt(4x^2+1)/(x+2)")["deriv_etapes"])
        self.assertIn(r"u'(x) = 8x\)", h)
        self.assertNotIn("8x + 0", h)

    def test_justification_d_une_derivee_de_reference_presente(self):
        """Guide R11 : les justifications restent TOUJOURS (les élèves les oublient)."""
        def etapes(entree):
            return " ".join(texte_etape(it) for it in dv.etudier(entree)["deriv_etapes"])
        self.assertIn(r"\(\left(x^{2}\right)' = 2x\) (règle de la puissance)", etapes("x^2*ln(x)"))
        self.assertIn(r"\(\left(x^{3}\right)' = 3x^{2}\) (règle de la puissance)", etapes("(x^3+2x)^4*e^x"))
        self.assertIn(r"\(\left(\ln(x)\right)' = \frac{1}{x}\) (règle de base)", etapes("x^2*ln(x)"))
        self.assertIn(r"\(\left(e^{x}\right)' = e^{x}\) (règle de base)", etapes("(x^3+2x)^4*e^x"))
        self.assertIn("règle du quotient", etapes("sqrt(4x^2+1)/(x+2)"))
        self.assertIn("règle du produit", etapes("x^2*ln(x)"))
        self.assertIn(r"est de la forme \(\sqrt{u}\)", etapes("sqrt(4x^2+1)/(x+2)"))

    def test_pas_de_den_dans_les_libelles_du_tableau(self):
        for entree in ("sqrt(4x^2+1)/(x+2)", "(2x+1)/(x^2+1)", "ln(x^2+1)/x"):
            for ligne in dv.etudier(entree)["table_signe"]["rows"]:
                with self.subTest(f=entree, ligne=ligne["label"]):
                    self.assertNotIn("dén", ligne["label"])


class TestFormesDuCorrige(unittest.TestCase):
    """Chantier étude complète, P1 (decisions.md D6, D7, D17) : e^(somme) gardé entier, une exponentielle par exposant
    distinct ; facteur négatif entre parenthèses ; une phrase écrite une seule fois ; 3e^{−6} ; signe dans le facteur eˣ − 3."""
    FAMILLE = ["e^((x^2+x-2)/(6x-12))", "e^(2x)-4e^x", "e^x(6-e^x)", "e^(-x)-e^x", "(x+1)e^(x^2+x)", "e^x*e^(x+1)",
               "x*e^(1/x)", "ln(x)/x", "(x^2-6)e^(-2x)", "(1-e^x)/(1+e^x)"]

    def test_resultat_juste(self):
        for entree in self.FAMILLE:
            f = ed.lire(entree)
            r = dv.etudier(entree)
            fp = dv._simplifier(dv.derivee_narree(f, [], top=True))
            self.assertEqual(ed.tex(fp), r["deriv_tex"], entree)
            for t in (-1.3, 0.7, 1.9, 2.6):
                attendu = derivee_numerique(f, t)
                if attendu is None:
                    continue
                with self.subTest(f=entree, x=t):
                    self.assertTrue(proches(ed.evaluer(fp, t), attendu))

    def test_une_exponentielle_par_exposant(self):
        attendus = {"e^((x^2+x-2)/(6x-12))": [r"e^{\frac{x^{2} + x - 2}{6x - 12}}"], "e^(2x)-4e^x": ["e^{x}"],
                    "(x+1)e^(x^2+x)": ["e^{x^{2} + x}"], "x*e^(1/x)": [r"e^{\frac{1}{x}}"]}
        for entree, exps in attendus.items():
            t = dv.etudier(entree)["deriv_tex"]
            with self.subTest(f=entree):
                for e in exps:
                    self.assertIn(e, t)
                self.assertEqual(t.count("e^{"), sum(t.count(e) for e in exps), t)     # aucune autre exponentielle

    def test_facteur_negatif_entre_parentheses(self):
        r = dv.etudier("(x^2-6)e^(-2x)")
        ligne = next(texte_etape(it) for it in r["deriv_etapes"] if "u'(x)v(x) + u(x)v'(x)" in texte_etape(it))
        self.assertIn(r"\left(x^{2} - 6\right) \cdot \left(-2e^{-2x}\right)", ligne)        # parenthèses ET point (D7, P7a)
        self.assertNotIn(r"\cdot -", ligne)

    def test_phrase_ecrite_une_fois(self):
        etapes = [texte_etape(it) for it in dv.etudier("e^x(6-e^x)")["deriv_etapes"]]
        self.assertEqual(len(etapes), len(set(etapes)), etapes)
        self.assertEqual(sum(r"\left(e^{x}\right)' = e^{x}" in h for h in etapes), 1, etapes)

    def test_formes_exactes(self):
        self.assertEqual(dv.etudier("e^x(6-e^x)")["deriv_tex"], r"2e^{x}\,\left(3 - e^{x}\right)")
        self.assertEqual(dv.etudier("ln(x)/x")["deriv_tex"], r"\frac{1 - \ln(x)}{x^{2}}")
        self.assertEqual(dv.etudier("(x^2-6)e^(-2x)")["deriv_tex"], r"-2\left(x - 3\right)\,\left(x + 2\right)\,e^{-2x}")
        valeurs = {e["x_tex"]: e["f_tex"] for e in dv.etudier("(x^2-6)e^(-2x)")["extrema"]}
        self.assertEqual(valeurs, {"-2": "- 2 e^{4}", "3": "3 e^{-6}"})
        self.assertEqual(dv.etudier("x*e^x")["extrema"][0]["f_tex"], "- e^{-1}")
        self.assertEqual(dv.etudier("x*e^(2x)")["extrema"][0]["f_tex"], r"- \frac{1}{2 e}")        # coefficient non entier : inchangé
        # somme sans terme négatif : le signe reste devant (jamais −e^{2x} − 1)
        self.assertEqual(dv.etudier("e^(-x)-e^x")["deriv_tex"], r"-\left(e^{2x} + 1\right)\,e^{-x}")


def lire_tex(t):
    r"""Relit une formule affichée (LaTeX de l'outil : \frac, \left( \right), \, et \cdot, exposants entre accolades) en saisie de l'outil."""
    t = t.replace(r"\left(", "(").replace(r"\right)", ")").replace(r"\,", "*").replace(r"\cdot", "*").replace(r"\dfrac", r"\frac")
    t = t.replace(" ", "")

    def groupe(i):                        # t[i] == "{" : contenu jusqu'à l'accolade fermante, et la position qui suit
        prof = 0
        for j in range(i, len(t)):
            prof += {"{": 1, "}": -1}.get(t[j], 0)
            if prof == 0:
                return t[i + 1:j], j + 1
        raise ValueError(t)
    while r"\frac{" in t:
        i = t.index(r"\frac{")
        a, j = groupe(i + 5)
        b, k = groupe(j)
        t = t[:i] + "((" + a + ")/(" + b + "))" + t[k:]
    return ed.lire(t.replace("{", "(").replace("}", ")"))


def formule(html):
    r"""La formule d'une ligne « \(…\) (propriété) » et la propriété."""
    f, reste = html[2:].split(r"\)", 1)
    return f, reste.strip().strip("()")


def sous_carte(r):
    return next((it for it in r["deriv_etapes"] if it["type"] == "sous_calcul"), None)


def polynome_au_hasard(rnd, degre, facteur=1):
    """Polynôme écrit développé, coefficients entiers (tous multipliés par `facteur`)."""
    termes = []
    for k in range(degre, -1, -1):
        c = facteur * (rnd.randint(-6, 6) if k < degre else rnd.choice([-3, -2, -1, 1, 2, 3, 4, 6]))
        if c == 0:
            continue
        corps = "" if k == 0 else "x" if k == 1 else f"x^{k}"
        nombre = str(abs(c)) if (abs(c) != 1 or k == 0) else ""
        termes.append(("-" if c < 0 else "+") + nombre + corps)
    s = "".join(termes)
    return s[1:] if s.startswith("+") else s


class TestDeriveeExposantEtTableauUV(unittest.TestCase):
    """Chantier étude complète, P7a (decisions.md D7, D7b, D8) : tableau u, v / u′, v′ ; facteur négatif entre parenthèses avec le
    point ; dérivée de l'exposant détaillée une étape par ligne, chaque ligne vérifiée ; développement d'abord pour un polynôme en eˣ."""
    EX7 = "e^((x^2+x-2)/(6x-12))"

    def test_ex7_lignes_exactes(self):
        r = dv.etudier(self.EX7)
        e = r["deriv_etapes"]
        self.assertEqual([it["type"] for it in e], ["texte", "sous_calcul", "texte"])
        self.assertEqual(e[0]["html"], r"\(f(x) = e^{g(x)}\) avec \(g(x) = \frac{x^{2} + x - 2}{6x - 12}\), donc \(f'(x) = g'(x) \cdot e^{g(x)}\) "
                                       r"(dérivée d'une composée). On calcule d'abord \(g'(x)\).")
        self.assertEqual(e[2]["html"], r"On remplace \(g'(x)\) dans \(f'(x) = g'(x) \cdot e^{g(x)}\) :")
        sc = e[1]
        self.assertEqual(sc["titre"], "Dérivée de l'exposant")
        self.assertEqual([et["titre"] for et in sc["etapes"]], ["règle du quotient", "calcul du numérateur, puis simplification"])
        self.assertEqual(sc["etapes"][0]["blocs"], [
            {"type": "texte", "html": dv.REGLE_QUOTIENT},
            {"type": "uv", "u": "u = x^{2} + x - 2", "du": "u' = 2x + 1", "v": "v = 6x - 12", "dv": "v' = 6"},
            {"type": "texte", "html": r"\(g'(x) = \frac{\left(2x + 1\right)\,\left(6x - 12\right) - \left(x^{2} + x - 2\right) \cdot 6}"
                                      r"{\left(6x - 12\right)^{2}}\) (règle du quotient)"}])
        self.assertEqual([b["html"] for b in sc["etapes"][1]["blocs"]], [
            r"\(g'(x) = \frac{12x^{2} - 24x + 6x - 12 - 6x^{2} - 6x + 12}{36\left(x - 2\right)^{2}}\) (développement)",
            r"\(= \frac{6x^{2} - 24x}{36\left(x - 2\right)^{2}}\) (réduction)",
            r"\(= \frac{6x\,\left(x - 4\right)}{36\left(x - 2\right)^{2}}\) (mise en évidence)",
            r"\(= \frac{x\,\left(x - 4\right)}{6\left(x - 2\right)^{2}}\) (simplification par 6)"])
        self.assertNotIn(r"\left(x^{2}\right)' = 2x", json.dumps(e))                  # plus de « (x²)′ = 2x » parasite
        self.assertEqual(r["deriv_tex"], dv.tex(dv._simplifier(dv.derivee_narree(ed.lire(self.EX7), [], top=True))))   # f′ inchangée

    def test_d_et_e_puissance_un_sur_x(self):
        sc = sous_carte(dv.etudier("e^(2/(x^2-4))"))
        self.assertEqual(sc["etapes"][0]["blocs"][1], {"type": "uv", "u": "u = 2", "du": "u' = 0", "v": "v = x^{2} - 4", "dv": "v' = 2x"})
        self.assertEqual(sc["etapes"][0]["blocs"][2]["html"], r"\(g'(x) = \frac{-2 \cdot 2x}{\left(x^{2} - 4\right)^{2}}\) (règle du quotient)")
        self.assertEqual([b["html"] for b in sc["etapes"][1]["blocs"]], [r"\(g'(x) = \frac{-4x}{\left(x^{2} - 4\right)^{2}}\) (calcul)"])
        sc = sous_carte(dv.etudier("e^(1/x)"))                 # rien à développer : la ligne de la règle du quotient suffit
        self.assertEqual(len(sc["etapes"]), 1)
        self.assertEqual(sc["etapes"][0]["blocs"][2]["html"], r"\(g'(x) = \frac{-1}{x^{2}}\) (règle du quotient)")

    def test_chaque_ligne_egale_g_prime_oracle(self):
        """40 exposants u/v tirés au hasard : chaque ligne affichée, relue et évaluée en mpmath (oracle), vaut g′ (dérivée numérique
        de l'oracle) ; u′ et v′ du tableau aussi ; les propriétés viennent dans l'ordre du corrigé."""
        import random
        import oracle
        rnd = random.Random(20261103)
        ordre = ["règle du quotient", "développement", "calcul", "réduction", "mise en évidence", "simplification"]
        avec = 0
        for _ in range(40):
            haut = polynome_au_hasard(rnd, rnd.randint(0, 2))
            # coefficient commun au dénominateur une fois sur deux : (6x − 12)² = 36(x − 2)²
            bas = polynome_au_hasard(rnd, rnd.randint(1, 2), rnd.choice([1, 1, 1, 2, 3, 6]))
            g, u, v = ed.lire(f"({haut})/({bas})"), ed.lire(haut), ed.lire(bas)
            r = dv.etudier(f"e^(({haut})/({bas}))")
            sc = sous_carte(r)
            if sc is None:
                continue
            avec += 1
            uv = sc["etapes"][0]["blocs"][1]
            lignes = [sc["etapes"][0]["blocs"][2]["html"]] + [b["html"] for et in sc["etapes"][1:] for b in et["blocs"]]
            proprietes = [formule(h)[1] for h in lignes]
            rangs = [next(i for i, p in enumerate(ordre) if p2.startswith(p)) for p2 in proprietes]
            with self.subTest(g=f"({haut})/({bas})"):
                self.assertEqual(rangs, sorted(rangs), proprietes)
                self.assertEqual(len(set(lignes)), len(lignes))
                for x in (-2.3, -0.6, 0.7, 1.9, 3.4):
                    attendu = oracle.derivee(g, x) if oracle.definie(g, x) else None
                    if attendu is None:
                        continue
                    for h in lignes:
                        f = formule(h)[0].split("=")[-1]
                        self.assertLess(abs(oracle.valeur(lire_tex(f), x) - attendu), mpmath.mpf("1e-25") * (1 + abs(attendu)), h)
                    for cle, n in (("du", u), ("dv", v)):
                        d = oracle.derivee(n, x)
                        self.assertLess(abs(oracle.valeur(lire_tex(uv[cle].split("=")[1]), x) - d), mpmath.mpf("1e-25") * (1 + abs(d)))
        self.assertGreaterEqual(avec, 35, "la sous-carte manque pour trop d'exposants")

    def test_cas_laisses_a_la_redaction_habituelle(self):
        for entree in ("e^(x^2)", "e^(-x^2)", "e^((x+1)^2/(x-1))", "e^(-1/x)", "e^((x/2+1)/(x-1))", "e^(ln(x)/x)", "x*e^(1/x)",
                       "e^(sqrt(x)/(x+1))"):
            with self.subTest(f=entree):
                r = dv.etudier(entree)
                self.assertIsNone(sous_carte(r))
                self.assertNotIn("On calcule d'abord", json.dumps(r["deriv_etapes"]))

    def test_garde_fous_forces(self):
        from unittest import mock
        for nom in ("_egaux", "_derivee_juste"):
            with self.subTest(garde_fou=nom), mock.patch.object(dv, nom, return_value=False):
                r = dv.etudier(self.EX7)
                self.assertIsNone(sous_carte(r))
                self.assertIn(r"est de la forme \(e^{u}\)", " ".join(texte_etape(it) for it in r["deriv_etapes"]))
                self.assertEqual(r["deriv_tex"], dv.etudier(self.EX7)["deriv_tex"])
        with mock.patch.object(dv, "_egaux", return_value=False):
            self.assertNotIn("On développe d'abord", " ".join(texte_etape(it) for it in dv.etudier("e^x(6-e^x)")["deriv_etapes"]))
        with mock.patch.object(dv, "charger_sympy", return_value=None):
            self.assertIsNone(dv._derivee_exposant(ed.lire(self.EX7), ed.lire("x")))
            self.assertIsNone(dv._developpe_d_abord(ed.lire("e^x(6-e^x)"), ed.lire("x")))
        # f′ fausse (forcée) : la sous-carte n'est pas écrite, puisque g′·e^{g} ≠ f′
        self.assertIsNone(dv._derivee_exposant(ed.lire(self.EX7), ed.lire("x")))
        self.assertIsNone(dv._developpe_d_abord(ed.lire("e^x(6-e^x)"), ed.lire("x")))

    def test_tableau_uv_produit_et_quotient(self):
        r = dv.etudier("(x^2-6)e^(-2x)")
        e = r["deriv_etapes"]
        self.assertEqual(e[0], {"type": "texte", "html": dv.REGLE_PRODUIT})
        self.assertEqual(e[1], {"type": "uv", "u": "u = x^{2} - 6", "du": "u' = 2x", "v": "v = e^{-2x}", "dv": "v' = -2e^{-2x}"})
        textes = " ".join(texte_etape(it) for it in e)
        self.assertNotIn("On pose", textes)
        self.assertIn(r"(règle de la puissance)", textes)                                     # justifications gardées (R11)
        for entree in CAS + TestSansOperationNeutre.ENTREES:
            r = dv.etudier(entree)
            for i, it in enumerate(r.get("deriv_etapes", [])):
                if it["type"] == "uv":
                    with self.subTest(f=entree):
                        self.assertIn(r["deriv_etapes"][i - 1]["html"], (dv.REGLE_PRODUIT, dv.REGLE_QUOTIENT))
                        self.assertEqual([it[k][:4] for k in ("u", "du", "v", "dv")], ["u = ", "u' =", "v = ", "v' ="])
            self.assertNotIn("On pose", json.dumps(r.get("deriv_etapes", [])), entree)

    def test_developpe_d_abord(self):
        etapes = dv.etudier("e^x(6-e^x)")["deriv_etapes"]
        self.assertEqual([it["html"] for it in etapes[:3]], [
            "On développe d'abord (c'est plus simple à dériver) :",
            r"\(f(x) = e^{x}\,\left(6 - e^{x}\right) = 6e^{x} - e^{x} \cdot e^{x}\) (développement)",
            r"\(= 6e^{x} - e^{2x}\) (réduction)"])
        import oracle
        for entree in ("e^x(6-e^x)", "(e^x-1)(e^x+2)", "(2e^x+1)(e^(2x)-3)", "e^(2x)(1-e^x)", "(3-e^x)e^x"):
            r = dv.etudier(entree)
            textes = [it["html"] for it in r["deriv_etapes"] if it["type"] == "texte"]
            with self.subTest(f=entree):
                self.assertEqual(textes[0], "On développe d'abord (c'est plus simple à dériver) :")
                f = ed.lire(entree)
                self.assertEqual(r["deriv_tex"], dv.tex(dv._simplifier(dv.derivee_narree(f, [], top=True))))     # f′ inchangée
                for h in textes[1:3]:
                    if "(développement)" in h or "(réduction)" in h:
                        membre = formule(h)[0].split("=")[-1]
                        for x in (-1.2, 0.3, 1.1):
                            self.assertLess(abs(oracle.valeur(lire_tex(membre), x) - oracle.valeur(f, x)), mpmath.mpf("1e-30"), h)
        for entree in ("x*e^x", "e^x*e^x", "e^(-x)*(e^x+1)", "(e^x+1)^2", "e^x(6-x)", "2(e^x+1)", "e^x(e^x+x)"):
            with self.subTest(f=entree):
                self.assertNotIn("On développe d'abord", json.dumps(dv.etudier(entree).get("deriv_etapes", [])))


if __name__ == "__main__":
    unittest.main()
