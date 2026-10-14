"""T06 / T06b : tableau de variations (Q3, 14.10.2026) — ED de f', double barre sur f',
valeur de f sans barre, extrema (i) et (ii), fonction constante."""
import unittest

from moteurs import ensemble_def as ed
import derivee_variations as dv


def lignes(entree):
    r = dv.etudier(entree)
    assert r["signe_resolu"], r
    t = r["table_signe"]
    return r, t, {l["label"]: l["cells"] for l in t["rows"]}


class TestEDdeFPrime(unittest.TestCase):
    def test_etape_ed_de_f_prime(self):  # DV-03
        for entree in ["sqrt(x^2-4)", "sqrt(x)", "sqrt(x^2)", "x^(2/3)", "sqrt(4-x^2)"]:
            with self.subTest(f=entree):
                r = dv.etudier(entree)
                f = ed.lire(entree)
                attendu = ed.ens_tex(ed.inter(ed._analyser(entree)[2], ed.domaine(
                    dv._simplifier(dv.derivee_narree(f, [], top=True)))))
                self.assertEqual(r["ed_deriv_tex"], attendu)
                etapes = [e["html"] for e in r["signe_etapes"] if "html" in e]
                self.assertTrue(any(h.startswith("ED de f'") and attendu in h for h in etapes), etapes)

    def test_pas_d_etape_si_meme_ed(self):
        for entree in ["x^3", "x^2-4x+3", "ln(x)"]:
            with self.subTest(f=entree):
                r = dv.etudier(entree)
                self.assertNotIn("ed_deriv_tex", r)
                self.assertFalse(any(h.get("html", "").startswith("ED de f'") for h in r["signe_etapes"]))


class TestTableauQ3(unittest.TestCase):
    def test_racine_x2_moins_4(self):  # DV-10
        r, t, L = lignes("sqrt(x^2-4)")
        self.assertEqual(t["crit"], ["-2", "2"])
        self.assertEqual(L["f'(x)"][1], "||")
        self.assertEqual(L["f'(x)"][3], "||")
        self.assertEqual(L["f(x)"][1], "val:0")     # valeur f(−2) = 0, sans barre
        self.assertEqual(L["f(x)"][3], "val:0")
        self.assertEqual([(e["genre"], e["x_tex"], e["f_tex"]) for e in r["extrema"]],
                         [("minimum local", "-2", "0"), ("minimum local", "2", "0")])

    def test_extremum_interieur_sans_derivee(self):  # DV-04
        for entree, genre in [("sqrt(x^2)", "minimum local"), ("x^(2/3)", "minimum local")]:
            with self.subTest(f=entree):
                r, _, L = lignes(entree)
                self.assertEqual(L["f'(x)"][1], "||")
                self.assertEqual(L["f(x)"][1], "val:0")
                self.assertEqual([(e["genre"], e["x_tex"]) for e in r["extrema"]], [(genre, "0")])

    def test_point_sans_derivee_sans_changement_de_signe(self):
        r, _, L = lignes("x^(1/3)")        # f' > 0 de part et d'autre de 0
        self.assertEqual(r["extrema"], [])
        self.assertEqual(L["f(x)"], [r"\nearrow", "val:0", r"\nearrow"])

    def test_borne_ouverte_sans_extremum_barre(self):
        r, _, L = lignes("ln(x)")
        self.assertEqual(r["extrema"], [])
        self.assertEqual(L["f(x)"][1], "asym")     # f non définie en 0 : double barre

    def test_zero_isole_de_f_prime(self):  # x³ : 0 dans la colonne de 0, ↗ ↗, aucun extremum
        r, _, L = lignes("x^3")
        self.assertEqual(L["f'(x)"], ["+", "0", "+"])
        self.assertEqual(L["f(x)"], [r"\nearrow", "", r"\nearrow"])
        self.assertEqual(r["extrema"], [])
        self.assertNotIn("f_constante", r)


class TestFonctionConstante(unittest.TestCase):
    def test_constante_sur_R(self):  # x^(2-2)
        r, t, L = lignes("x^(2-2)")
        self.assertEqual(L["f'(x)"], ["0"])
        self.assertEqual(L["f(x)"], [r"\rightarrow"])
        self.assertEqual(r["extrema"], [])
        self.assertTrue(r["f_constante"])

    def test_constante_par_morceaux(self):  # √(x²)/x : −1 pour x < 0, 1 pour x > 0
        r, _, L = lignes("sqrt(x^2)/x")
        self.assertEqual(L["f'(x)"], ["0", "||", "0"])
        self.assertEqual(L["f(x)"], [r"\rightarrow", "asym", r"\rightarrow"])
        self.assertEqual(r["extrema"], [])

    def test_constante_hors_ed_barree(self):  # ln(x²) − 2 ln(x), ED = ]0 ; +∞[
        r, _, L = lignes("ln(x^2)-2ln(x)")
        self.assertEqual(L["f'(x)"], ["x", "||", "0"])
        self.assertEqual(L["f(x)"], ["x", "asym", r"\rightarrow"])
        self.assertEqual(r["extrema"], [])

    def test_valeur_constante_a_la_borne_dans_l_ed(self):
        # f = (√x)⁰ : ED = [0 ; +∞[ (bord fermé), f ≡ 1.
        r, _, L = lignes("sqrt(x)^0")
        self.assertEqual(r["extrema"], [])
        self.assertTrue(r["f_constante"])
        self.assertEqual(L["f(x)"][1], "val:1")
        self.assertEqual(L["f(x)"][2], r"\rightarrow")


if __name__ == "__main__":
    unittest.main()


class TestZonesHorsED(unittest.TestCase):
    """C4 : jamais de signe ni de flèche hors de l'ED de f ; ces zones sont barrées (« x »)."""

    def test_ln(self):
        r, t, L = lignes("ln(x)")
        self.assertEqual(L["f'(x)"], ["x", "||", "+"])
        self.assertEqual(L["f(x)"], ["x", "asym", r"\nearrow"])

    def test_ln_sur_x(self):
        r, t, L = lignes("ln(x)/x")
        self.assertEqual(t["crit"], ["0", "e"])
        self.assertEqual(L["f'(x)"], ["x", "||", "+", "0", "-"])
        self.assertEqual(L["f(x)"], ["x", "asym", r"\nearrow", "extremum", r"\searrow"])

    def test_valeur_interdite_double_barre_sur_toute_la_colonne(self):
        """ln(x²−4), ED = ]−∞ ; −2[ ∪ ]2 ; +∞[ : colonnes −2 et 2 barrées sur TOUTES les lignes, zone ]−2 ; 2[ hachurée,
        colonne 0 supprimée (point hors de l'ED qui n'est pas une borne)."""
        r, t, L = lignes("ln(x^2-4)")
        self.assertEqual(t["crit"], ["-2", "2"])
        for ligne in t["rows"]:
            cases = ligne["cells"]
            self.assertEqual(len(cases), 5, ligne["label"])
            self.assertEqual((cases[1], cases[2], cases[3]), ("||" if not ligne.get("variation") else "asym", "x",
                                                              "||" if not ligne.get("variation") else "asym"), ligne["label"])
        self.assertEqual(L["f'(x)"], ["-", "||", "x", "||", "+"])
        self.assertEqual(L["f(x)"], [r"\searrow", "asym", "x", "asym", r"\nearrow"])

    def test_bornes_hors_ed(self):
        for entree in ("ln(x)", "1/x", "1/ln(x)", "ln(x)/x"):
            r, t, L = lignes(entree)
            for j in range(1, len(t["rows"][0]["cells"]), 2):
                col = [ligne["cells"][j] for ligne in t["rows"]]
                with self.subTest(f=entree, colonne=t["crit"][j // 2]):
                    if col[-1] == "asym":                    # valeur interdite de f : barre sur toutes les lignes
                        self.assertTrue(all(c in ("||", "asym") for c in col), col)

    def test_borne_dans_l_ed_sans_derivee_double_barre_seulement_sur_f_prime(self):    # Q3
        for entree in ("sqrt(x^2-4)", "sqrt(x)"):
            r, t, L = lignes(entree)
            j = 1
            col = {ligne["label"]: ligne["cells"][j] for ligne in t["rows"]}
            self.assertEqual(col["f'(x)"], "||")
            self.assertEqual(col["f(x)"], "val:0")

    def test_aucune_colonne_dans_une_zone_hors_ed(self):
        """Une colonne n'existe que pour un point de l'ED ou une borne de l'ED."""
        for entree in ("ln(x^2-4)", "sqrt(4-x^2)", "ln(x^2-4)/x", "ln(x)/x"):
            r, t, L = lignes(entree)
            cases = L["f'(x)"]
            for j in range(2, len(cases) - 2, 2):            # intervalle j entouré de colonnes
                with self.subTest(f=entree, intervalle=j):
                    self.assertFalse(cases[j - 2] == "x" and cases[j] == "x", cases)

    def test_bornes_fermees(self):
        r, t, L = lignes("sqrt(4-x^2)")
        self.assertEqual(L["f(x)"][0], "x")
        self.assertEqual(L["f(x)"][-1], "x")
        self.assertEqual(L["f(x)"][1:-1], ["val:0", r"\nearrow", "extremum", r"\searrow", "val:0"])

    def test_pas_de_doublon_de_points_critiques(self):
        r, t, L = lignes("1/(2x^2-4x+1)")        # pôles irrationnels : (2 ± √2)/2 ne doivent apparaître qu'une fois
        self.assertEqual(t["crit"], [r"\frac{2 - \sqrt{2}}{2}", "1", r"\frac{2 + \sqrt{2}}{2}"])
        self.assertEqual(L["f(x)"], [r"\nearrow", "asym", r"\nearrow", "extremum", r"\searrow", "asym", r"\searrow"])

    def test_x_exactement_hors_de_l_ed(self):
        """Pour des exemples et 150 fonctions générées : sur chaque intervalle, les lignes f'(x) et f(x) sont
        barrées si et seulement si f n'est pas définie (oracle haute précision)."""
        import oracle
        from generateurs import fonctions
        from cas import CAS_LIMITES, entrees_page
        with open(dv.__file__, encoding="utf-8") as f:
            src = f.read().replace('"rows": lignes}', '"rows": lignes, "crit_val": [p.val for p in crit]}')
        ns = {"__name__": "dv_instr"}
        exec(compile(src, "dv_instr", "exec"), ns)
        for entree in list(dict.fromkeys(entrees_page("derivee-variations") + CAS_LIMITES["derivee-variations"])) + fonctions(150, graine=3):
            r = ns["etudier"](entree)
            if not r.get("signe_resolu"):
                continue
            t, arbre = r["table_signe"], ed.lire(entree)
            cv, k = t["crit_val"], len(t["crit_val"])
            for i in range(k + 1):
                x = 0.0 if k == 0 else cv[0] - 1 if i == 0 else cv[-1] + 1 if i == k else (cv[i - 1] + cv[i]) / 2
                dedans = oracle.definie(arbre, x)
                for row in t["rows"]:
                    if row.get("final") or row.get("variation"):
                        with self.subTest(f=entree, ligne=row["label"], intervalle=i):
                            self.assertEqual(row["cells"][2 * i] == "x", not dedans, row["cells"])
                    elif not dedans:            # lignes de facteurs : la zone hors de l'ED est hachurée aussi
                        with self.subTest(f=entree, ligne=row["label"], intervalle=i):
                            self.assertEqual(row["cells"][2 * i], "x", row["cells"])
            for j in range(1, 2 * k, 2):         # colonne d'une valeur interdite : barre sur toutes les lignes
                f_row = next(w for w in t["rows"] if w.get("variation"))
                if f_row["cells"][j] == "asym":
                    for row in t["rows"]:
                        with self.subTest(f=entree, ligne=row["label"], colonne=j):
                            self.assertIn(row["cells"][j], ("||", "asym"), row["cells"])
            for j in range(2, 2 * k, 2):         # pas de colonne parasite entre deux zones hors de l'ED
                with self.subTest(f=entree, intervalle=j):
                    self.assertFalse(t["rows"][-1]["cells"][j - 2] == "x" and t["rows"][-1]["cells"][j] == "x")
