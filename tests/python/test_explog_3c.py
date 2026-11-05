"""Correctif du 02.11.2026 — « Exponentielles et logarithmes », filière 3C : tout ce que la 2M résout, la 3C le résout aussi (log(x + 3) = 2 log(3)),
sans ensemble de définition : on résout directement, puis la carte « Contrôle » remplace x par chaque solution dans l'équation de DÉPART.

EL-42  la 3C résout tout ce que la 2M résout (regroupement, constante irrationnelle, log_x(n) = p/q, second membre calculé, carré dans l'exposant, x − x·ln x = 0,
       2e degré en aˣ, bicarré, exposants 1/x √x ln x, base polynomiale, π), avec exactement le même S et les mêmes messages quand rien ne s'applique ;
EL-43  la carte « Contrôle » : chaque solution est remplacée, chaque membre calculé (propriété nommée, valeur exacte puis approchée), conclusion ;
       un logarithme d'un nombre négatif ou nul « n'existe pas » : la solution est rejetée ; rien de faux n'est jamais affiché ;
EL-44  chaque ligne de la 3C est une implication vraie sur tout le domaine de l'équation de départ (aucune racine perdue), propriétés de la liste fermée,
       aucune mention de l'ensemble de définition ; log = base 10, ln = base e."""
import re
import unittest
from fractions import Fraction as F

import moteurs  # noqa: F401  (chemins des moteurs)
import exp_log as el
import exp_log_m as elm
import resoudre_el as rel
import sortie as so
from cas_el import (BATTERIE_3C_REGROUPEMENT, BATTERIE_3C_REJETS, BATTERIE_M, BATTERIE_M_BASE_POLYNOMIALE, BATTERIE_M_BASE_RATIONNELLE, BATTERIE_M_BICARRE,
                    BATTERIE_M_CARRE_DANS_L_EXPOSANT, BATTERIE_M_EXPOSANTS, BATTERIE_M_IRRATIONNEL, BATTERIE_M_PI, BATTERIE_M_PRODUIT_X_LOG,
                    BATTERIE_M_SECOND_MEMBRE_CALCULE, BATTERIE_M_VAR, M_TOUT_L_ED, entrees_el, entrees_el_m)
import memo_racines
from test_exp_log_m import MP, ecart, evaluer

SANS_PERTE = [("log(x^2)=2", [-10, 10]), ("log(x(x-3))=1", [-2, 5]), ("log(x)+log(x-3)=1", [5]), ("ln(x^2)=2ln(3)", [-3, 3])]


def lire(entree):
    s = el.analyser_saisie(entree, "C")
    return s, elm.corriger_equation_c(s.g, s.d, s.inconnue)


def solutions(r):
    return sorted(MP.mpf(el.valeur(n)) for n in r["solutions"])


def textes(sortie):
    """Tout le texte (TeX et phrases) des blocs d'une sortie ok."""
    cartes = sortie["cartes"] if "cartes" in sortie else [c for v in sortie["variantes"] for c in v["cartes"]]
    return [b.get("html") or b.get("tex") or "" for c in cartes for b in c["blocs"]]


def solution_finale(sortie):
    cartes = sortie["cartes"] if "cartes" in sortie else sortie["variantes"][-1]["cartes"]
    return next(b["tex"] for c in cartes for b in c["blocs"] if nom(c) in ("Solution", "Résultat") and b["type"] == "resultat")


def nom(carte):
    """Le nom d'une carte de la sortie : le badge d'une « Étape k », sinon le titre (« Solution »)."""
    return carte.get("badge") or carte["titre"]


def carte_controle(sortie):
    return next(c for c in sortie["cartes"] if nom(c) == "Contrôle")


def cartes_c(entree, filiere="C"):
    return [nom(c) for c in rel.resoudre(entree, filiere)["cartes"]]


class TestBatterie3C(unittest.TestCase):
    def test_les_equations_de_la_batterie_sont_resolues_en_3c_comme_en_2m(self):
        """Chaque équation : une solution par valeur attendue, exacte (écart nul à 10⁻⁹ près dans l'équation de départ, oracle mpmath), aucune racine perdue
        (balayage numérique indépendant du moteur) ; la filière M donne les mêmes solutions."""
        for entree, attendu in BATTERIE_3C_REGROUPEMENT:
            with self.subTest(entree=entree):
                s, r = lire(entree)
                self.assertIsNotNone(r, "la 3C ne résout pas cette équation")
                trouvees = solutions(r)
                self.assertEqual(len(trouvees), len(attendu))
                for v, a in zip(trouvees, sorted(attendu)):
                    self.assertAlmostEqual(float(v), float(a), delta=1e-9 * (1 + abs(float(a))))
                    e = ecart(s, v)
                    self.assertIsNotNone(e, "solution où un logarithme n'existe pas")
                    self.assertLess(abs(e), MP.mpf("1e-9") * (1 + abs(v)))
                for rac in memo_racines.racines(s):
                    self.assertTrue(any(abs(rac - v) < MP.mpf("1e-9") * (1 + abs(rac)) for v in trouvees), ("racine perdue", rac))
                m = elm.corriger_equation(s.g, s.d, s.inconnue)
                self.assertEqual([float(v) for v in trouvees], [float(v) for v in solutions(m)])

    def test_les_cinq_equations_de_l_enonce(self):
        for entree, S in [("log(x+3) = 2log(3)", "6"), ("log(2x-1) = log(3) + log(5)", "8"), ("log(x) + log(x-3) = 1", "5"),
                          ("2log(x) = log(4x)", "4"), ("ln(x+1) = 3ln(2)", "7")]:
            with self.subTest(entree=entree):
                for filiere in ("C", "M"):
                    sortie = rel.resoudre(entree, filiere)
                    self.assertTrue(sortie["ok"], (filiere, sortie))
                    self.assertEqual(solution_finale(sortie), r"S = \left\{" + S + r"\right\}")


class TestSansPerte(unittest.TestCase):
    """Chaque ligne doit rester vraie pour toutes les solutions de l'équation de départ : log(x²) = 2 garde −10 (jamais 2 log(x)), log(x(x − 3)) = 1 garde −2."""

    def test_meme_s_en_3c_et_en_2m_avec_l_oracle(self):
        for entree, attendu in SANS_PERTE:
            with self.subTest(entree=entree):
                s = el.analyser_saisie(entree, "C")
                c = rel.resoudre(entree, "C")
                m = rel.resoudre(entree, "M")
                self.assertTrue(c["ok"] and m["ok"])
                self.assertEqual(solution_finale(c), solution_finale(m))
                _, r = lire(entree)
                self.assertEqual([float(v) for v in solutions(r)], [float(a) for a in attendu])
                for v in solutions(r):
                    self.assertLess(abs(ecart(s, v)), MP.mpf("1e-9") * (1 + abs(v)))
                self.assertEqual(sorted({round(float(x), 6) for x in memo_racines.racines(s)}), [float(a) for a in attendu])

    def test_le_rejet_de_moins_deux(self):
        """log(x) + log(x − 3) = 1 : x(x − 3) = 10 donne −2 et 5 ; −2 est rejetée au contrôle, S = {5}."""
        sortie = rel.resoudre("log(x) + log(x - 3) = 1", "C")
        controle = carte_controle(sortie)
        texte = " ".join(b["html"] for b in controle["blocs"])
        self.assertIn(r"\(x = -2\)", texte)
        self.assertIn(r"\(\log(-2)\)", texte)
        self.assertIn("n'existe pas", texte)
        self.assertIn("est rejetée", texte)
        self.assertIn(r"\(x = 5\)", texte)
        self.assertIn("est solution", texte)
        self.assertEqual(solution_finale(sortie), r"S = \left\{5\right\}")

    def test_aucune_ligne_ne_developpe(self):
        """Un résultat de la 2M qui contiendrait un développement (log(u²) = 2 log(u)) perdrait des solutions : la conversion le refuse (« pas encore »)."""
        r = elm.regrouper(*(lambda s: (s.g, s.d, s.inconnue))(el.analyser_saisie("log(x)+log(x-3)=1", "C")))
        self.assertIsNotNone(r)
        faux = el.Chaine([el.Eq(el.Log(el.Pow(el.Var("x"), el.Nb(2))), el.Nb(2)), el.Eq(el.Op("*", el.Nb(2), el.Log(el.Var("x"))), el.Nb(2))],
                         ["⇔"], ["log(u^k) = k · log u"])
        r["etapes"] = [el._carte("Développement", [faux])]
        with self.assertRaises(el._Hors):
            elm.en_3c(r)
        autre = el.Chaine([el.Eq(el.Var("x"), el.Nb(1)), el.Eq(el.Var("x"), el.Nb(1))], ["⇔"], ["x > 0 : sur l'ED"])
        r["etapes"] = [el._carte("Autre", [autre])]
        with self.assertRaises(el._Hors):
            elm.en_3c(r)


class TestControle(unittest.TestCase):
    def test_les_rejets(self):
        for entree, rejetees in BATTERIE_3C_REJETS:
            with self.subTest(entree=entree):
                sortie = rel.resoudre(entree, "C")
                self.assertTrue(sortie["ok"], sortie)
                controle = carte_controle(sortie)
                texte = " ".join(b["html"] for b in controle["blocs"])
                for v in rejetees:
                    self.assertIn(r"x = " + (str(v) if v >= 0 else "-" + str(-v)), texte)
                self.assertEqual(texte.count("est rejetée"), len(rejetees))
                self.assertIn("n'existe pas", texte)
                s, r = lire(entree)
                for v in solutions(r):                            # S ne contient que des solutions contrôlées
                    self.assertIsNotNone(ecart(s, v))
                    self.assertNotIn(F(float(v)).limit_denominator(1000), rejetees)

    def test_ensemble_vide_apres_controle(self):
        sortie = rel.resoudre("log(x-3)+log(1-x)=0", "C")
        texte = " ".join(textes(sortie))
        self.assertIn("Aucune solution trouvée ne convient", texte)
        self.assertEqual(solution_finale(sortie), r"S = \varnothing")

    def test_la_carte_est_la_derniere_avant_la_solution(self):
        for entree, _ in BATTERIE_3C_REGROUPEMENT + [("log(5-x)=8", None), ("log_x(256)=4", None), ("log(log(x-1))=0", None)]:
            with self.subTest(entree=entree):
                titres = cartes_c(entree)
                if titres[-1] == "Solution" and "Contrôle" in titres:
                    self.assertEqual(titres[-2], "Contrôle")
                self.assertEqual(titres.count("Contrôle") + titres.count("Vérification"), 1 if "Contrôle" in titres else 0)
                self.assertNotIn("Vérification", titres)
                self.assertNotIn("Ensemble de définition", titres)

    def test_chaque_membre_est_calcule_avec_sa_propriete(self):
        """x = 6 dans log(x + 3) = 2 log(3) : log(6 + 3) = log(9) et 2 log(3) = log(3²) = log(9) (k · log u = log(u^k)), les deux membres sont égaux."""
        sortie = rel.resoudre("log(x+3) = 2log(3)", "C")
        controle = carte_controle(sortie)
        texte = " ".join(b["html"] for b in controle["blocs"])
        for morceau in (r"\(x = 6\)", r"\log(6 + 3) = \log(9)", r"2\log(3) = \log(3^{2})", "(k · log u = log(u^k))", r"\log(9) \approx 0{,}954",
                        "Les deux membres sont égaux", "est solution ✓"):
            self.assertIn(morceau, texte)

    def test_valeur_exacte_quand_l_argument_est_une_puissance_de_la_base(self):
        texte = " ".join(textes(rel.resoudre("log(x) + log(x-3) = 1", "C")))
        self.assertIn(r"\log(5 \cdot 2)", texte)
        self.assertIn(r"\log(10) = 1", texte)
        self.assertIn("(car log(10) = 1)", texte)
        texte = " ".join(textes(rel.resoudre("log(5-x)=8", "C")))
        self.assertIn(r"\log(10^{8}) = 8", texte)

    def test_la_valeur_approchee_d_une_solution_irrationnelle_reste_approchee(self):
        """x₂ = (1 + √41)/2 : le calcul numérique n'est jamais présenté comme un calcul exact (« ≈ », pas « = »)."""
        texte = " ".join(textes(rel.resoudre("log(x)+log(x-1)=1", "C")))
        self.assertIn(r"\log(x_{2}) + \log(x_{2} - 1) \approx 1{,}000", texte)
        self.assertIn(r"\log(x_{1})\) n'existe pas", texte)

    def test_un_decimal_dans_l_enonce_reste_decimal(self):
        texte = " ".join(textes(rel.resoudre("log(x)=1,5", "C")))
        self.assertIn(r"= 1{,}5", texte)
        self.assertNotIn(r"\frac{3}{2}\)", texte.split("Contrôle")[-1] if "Contrôle" in texte else texte)

    def test_l_identite_donne_l_ensemble_ou_les_logarithmes_existent(self):
        for entree in M_TOUT_L_ED:
            with self.subTest(entree=entree):
                c, m = rel.resoudre(entree, "C"), rel.resoudre(entree, "M")
                self.assertTrue(c["ok"], c)
                self.assertEqual(solution_finale(c), solution_finale(m))


class TestBase10(unittest.TestCase):
    def test_log_est_en_base_10_et_ln_en_base_e(self):
        """En Suisse log = base 10, ln = base e : log(x) = 2 donne 100, ln(x) = 1 donne e ; l'affichage est \\log et \\ln, jamais \\log_{10}."""
        self.assertEqual(solution_finale(rel.resoudre("log(x)=2", "C")), r"S = \left\{100\right\}")
        self.assertEqual(solution_finale(rel.resoudre("ln(x)=1", "C")), r"S = \left\{e\right\} \text{, soit } x \approx 2{,}718")
        for entree in ("log(x)=2", "ln(x)=1", "log(x)+log(x-3)=1", "ln(x+1)=3ln(2)", "log(x+3) = 2log(3)"):
            texte = " ".join(textes(rel.resoudre(entree, "C")))
            self.assertNotIn(r"\log_{10}", texte)
            self.assertNotIn(r"\log_{e}", texte)
            self.assertIn(r"\ln" if entree.startswith("ln") else r"\log", texte)


class TestAucuneMentionDeLED(unittest.TestCase):
    def test_pas_d_ensemble_de_definition_en_3c(self):
        """La 3C n'a pas d'ensemble de définition : aucune carte, aucune mention « ED » ni « sur l'ED » dans les sorties du correctif ; propriétés de la liste fermée."""
        permises = el.PROPRIETES | elm.PROPRIETES_C_AJOUTEES
        for entree, _ in BATTERIE_3C_REGROUPEMENT + BATTERIE_3C_REJETS:
            with self.subTest(entree=entree):
                s = rel.resoudre(entree, "C")
                self.assertTrue(s["ok"], s)
                texte = " ".join(textes(s))
                self.assertNotRegex(texte, r"\bED\b|ensemble de définition|sur l'ED")
                _, r = lire(entree)
                for carte in r["etapes"]:
                    for ligne in carte["lignes"]:
                        if isinstance(ligne, el.Chaine):
                            for prop in ligne.props:
                                if isinstance(prop, str):
                                    self.assertIn(prop, permises)
                            for lien in ligne.liens:
                                self.assertIn(lien, ("⇔", "⇒", "=", "≈"))


class TestImplicationsVraies(unittest.TestCase):
    """Chaque équation « g = d » d'une chaîne de la 3C est vraie pour toute racine de l'équation de départ (trouvée sans le moteur, par balayage) :
    une ligne qui perdrait une racine échoue ici. Les cartes « Contrôle » (calculs de membres) ne sont pas des équations d'étape."""

    def test_toute_ligne_est_vraie_en_chaque_racine(self):
        verifiees = 0
        for entree, _ in BATTERIE_3C_REGROUPEMENT + BATTERIE_M[:25]:
            s, r = lire(entree)
            if r is None or elm.regrouper(s.g, s.d, s.inconnue) is None:
                continue
            for rac in memo_racines.racines(s):
                for carte in r["etapes"]:
                    if carte["titre"] == "Contrôle":
                        continue
                    for ligne in carte["lignes"]:
                        for e in (ligne.elements if isinstance(ligne, el.Chaine) else []):
                            if not isinstance(e, el.Eq) or el.variables(e.g) | el.variables(e.d) != {s.inconnue}:
                                continue
                            a, b = evaluer(e.g, rac), evaluer(e.d, rac)
                            if a is None or b is None:
                                self.fail(f"{entree} : ligne sans valeur en la racine {rac} : {el.tex_element(e)}")
                            verifiees += 1
                            self.assertLess(abs(a - b), MP.mpf("1e-9") * (1 + abs(a) + abs(b)), (entree, el.tex_element(e), rac))
        self.assertGreater(verifiees, 150)


class TestSDeCEgalSDeM(unittest.TestCase):
    """EL-42 : pour tout le corpus, la 3C résout exactement ce que la 2M résout, avec le même S (jamais une solution de moins ni de plus) ; quand la 2M ne
    résout pas, la 3C donne le même message."""

    def test_meme_s_sur_tout_le_corpus(self):
        compares = refus = 0
        for entree in dict.fromkeys(entrees_el() + entrees_el_m()):
            c, m = rel.resoudre(entree, "C"), rel.resoudre(entree, "M")
            if m["ok"]:
                self.assertTrue(c["ok"], (entree, c))
                self.assertEqual(solution_finale(c), solution_finale(m), entree)
                compares += 1
            elif c["ok"]:
                self.fail(f"{entree} : résolue en 3C seulement")
            else:
                refus += 1
        self.assertGreater(compares, 500)
        self.assertGreater(refus, 30)

    def test_les_messages_de_refus_ne_different_que_par_la_lecture(self):
        """Quand la 2M refuse une équation sans logarithme de l'inconnue (hors programme, pas encore), la 3C donne le même message."""
        for entree in dict.fromkeys(entrees_el() + entrees_el_m()):
            c, m = rel.resoudre(entree, "C"), rel.resoudre(entree, "M")
            if not c["ok"] and not m["ok"]:
                with self.subTest(entree=entree):
                    self.assertEqual(c["erreur"], m["erreur"])

    def test_le_format_est_valide_et_le_json_strict(self):
        for entree, _ in BATTERIE_3C_REGROUPEMENT + BATTERIE_3C_REJETS:
            with self.subTest(entree=entree):
                self.assertEqual(so.valider(rel.resoudre(entree, "C")), [])
                self.assertEqual(rel.resoudre_json(entree), rel.resoudre_json(entree, "C"))


def resultats_c(entree):
    """Les résultats du moteur pour la 3C : chacune des deux méthodes d'une équation exponentielle, sinon l'unique corrigé."""
    s = el.analyser_saisie(entree, "C")
    v = el.variantes_equation(s.g, s.d, s.inconnue, s.parametres) if elm.lecture_3c(s.g, s.d) else None
    v = v or elm.variantes_changement(s.g, s.d, s.inconnue, "C") or elm.variantes_exposant(s.g, s.d, s.inconnue, "C")
    return s, (list(v.values()) if v else [elm.corriger_equation_c(s.g, s.d, s.inconnue)])


FAMILLES = {"2e degré en a^x": BATTERIE_M_VAR, "exposants 1/x √x ln x": BATTERIE_M_EXPOSANTS, "base polynomiale": BATTERIE_M_BASE_POLYNOMIALE,
            "bicarré": BATTERIE_M_BICARRE, "log_x(n) = p/q": BATTERIE_M_BASE_RATIONNELLE, "constante irrationnelle": BATTERIE_M_IRRATIONNEL,
            "carré dans l'exposant": BATTERIE_M_CARRE_DANS_L_EXPOSANT, "second membre calculé": BATTERIE_M_SECOND_MEMBRE_CALCULE,
            "x − x·ln x = 0": BATTERIE_M_PRODUIT_X_LOG, "π": BATTERIE_M_PI}


def _oracle_famille(nom):
    def test(self):
        """Chaque entrée de la famille est résolue en 3C, chaque solution annule g − d (oracle mpmath), aucune racine n'est perdue (balayage numérique), le
        Contrôle rejette ce qui n'existe pas ; mêmes solutions qu'en 2M."""
        for entree, _ in FAMILLES[nom]:
            with self.subTest(entree=entree):
                s, rs = resultats_c(entree)
                self.assertTrue(all(r is not None for r in rs), "la 3C ne résout pas cette équation")
                m = elm.corriger_equation(s.g, s.d, s.inconnue)
                for r in rs:
                    if r.get("message"):                        # méthode « même base » qui ne s'applique pas : pas de solution à comparer
                        continue
                    trouvees = solutions(r)
                    for v in trouvees:
                        e = ecart(s, v)
                        self.assertIsNotNone(e, "solution où une expression n'existe pas")
                        self.assertLess(abs(e), MP.mpf("1e-9") * (1 + abs(v)))
                    for rac in memo_racines.racines(s):
                        self.assertTrue(any(abs(rac - v) < MP.mpf("1e-9") * (1 + abs(rac)) for v in trouvees), ("racine perdue", rac))
                    if m is not None and m["solutions"] is not None:
                        self.assertEqual([float(v) for v in trouvees], [float(v) for v in solutions(m)])
    test.__doc__ = f"Oracle mpmath sur la famille « {nom} » en 3C."
    return test


class TestToutesLesFamilles(unittest.TestCase):
    pass


for _i, _nom in enumerate(FAMILLES):
    setattr(TestToutesLesFamilles, f"test_oracle_{_i}", _oracle_famille(_nom))


class TestImplicationsAutresFamilles(unittest.TestCase):
    """Les familles sans embranchement (exposants, x − x·ln x = 0) : chaque équation d'une chaîne est vraie en toute racine, comme pour le regroupement."""

    def test_toute_ligne_est_vraie_en_chaque_racine(self):
        verifiees = 0
        for entree, _ in BATTERIE_M_EXPOSANTS + BATTERIE_M_PRODUIT_X_LOG + BATTERIE_M_BASE_RATIONNELLE:
            s, rs = resultats_c(entree)
            for r in rs:
                for rac in memo_racines.racines(s):
                    for carte in r["etapes"]:
                        if carte["titre"] == "Contrôle":
                            continue
                        for ligne in carte["lignes"]:
                            for e in (ligne.elements if isinstance(ligne, el.Chaine) else []):
                                if not isinstance(e, el.Eq) or el.variables(e.g) | el.variables(e.d) != {s.inconnue}:
                                    continue
                                a, b = evaluer(e.g, rac), evaluer(e.d, rac)
                                if a is None or b is None:
                                    continue
                                verifiees += 1
                                self.assertLess(abs(a - b), MP.mpf("1e-9") * (1 + abs(a) + abs(b)), (entree, el.tex_element(e), rac))
        self.assertGreater(verifiees, 40)


class TestM(unittest.TestCase):
    def test_la_2m_n_a_pas_de_controle(self):
        """La 2M garde l'ensemble de définition d'abord et la carte « Vérification » ; le correctif ne touche pas ses sorties."""
        for entree, _ in BATTERIE_3C_REGROUPEMENT[:5]:
            titres = cartes_c(entree, "M")
            self.assertEqual(titres[0], "Ensemble de définition")
            self.assertEqual(titres[-2], "Vérification")
            self.assertNotIn("Contrôle", titres)


if __name__ == "__main__":
    unittest.main()
