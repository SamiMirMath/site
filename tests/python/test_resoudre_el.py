"""T33 (étape 7) — Adaptateur resoudre_el.py de l'outil « Exponentielles et logarithmes » : format de sortie commun (moteur/sortie.py),
cartes « Étape k » + carte finale (EL-18), messages quand aucune méthode ne s'applique (EL-11), JSON strict."""
import json
import re
import unittest

import moteurs  # noqa: F401  (chemins des moteurs)
import exp_log as el
import resoudre_el as rel
import sortie as so
from cas_el import (BATTERIE_C1, BATTERIE_E1, BATTERIE_E2, BATTERIE_E3, BATTERIE_E4, CALCULS_NON_RESOLUS, ERREURS_DE_LECTURE, HORS_PROGRAMME,
                    PAS_ENCORE, entrees_el)

EQUATIONS = [s for batterie in (BATTERIE_E1, BATTERIE_E2, BATTERIE_E3, BATTERIE_E4) for s, _ in batterie]
CALCULS = [s for s, _ in BATTERIE_C1]


def textes(sortie):
    return [b for c in sortie["cartes"] for b in c["blocs"] if b["type"] == "texte"]


class TestFormat(unittest.TestCase):
    def test_toute_sortie_respecte_le_schema(self):
        for entree in entrees_el():
            with self.subTest(entree=entree):
                s = rel.resoudre(entree)
                self.assertEqual(so.valider(s), [])
                self.assertEqual(json.loads(rel.resoudre_json(entree)), s)

    def test_aucun_chevron_brut_dans_le_html(self):
        """Le TeX des lignes passe dans du HTML : « < » (5^(8x) > 0, −25 < 0, Δ < 0) est échappé."""
        vus = 0
        for entree in entrees_el():
            s = rel.resoudre(entree)
            for b in textes(s) if s["ok"] else []:
                vus += 1
                self.assertNotIn("<", re.sub(r"</?(div|span)[^>]*>", "", b["html"]), entree)
        self.assertGreater(vus, 300)
        s = rel.resoudre("5^(8x)=-25")
        self.assertTrue(any("&lt;" in b["html"] for b in textes(s)))

    def test_enonce(self):
        self.assertEqual(rel.resoudre("3^(x+1) = 27")["enonce_tex"], "3^{x + 1} = 27")
        self.assertEqual(rel.resoudre("log_2(50)")["enonce_tex"], r"\log_{2}(50)")

    def test_aperçu_est_celui_du_moteur(self):
        self.assertEqual(rel.apercu_json("3^(x+1)=27"), el.apercu_json("3^(x+1)=27"))


def chaines_du_moteur(entree):
    s = el.analyser_saisie(entree)
    r = el.calculer_logarithme(s.g) if s.genre == "calcul" else el.corriger_equation(s.g, s.d, s.inconnue)
    return [ligne for c in r["etapes"] for ligne in c["lignes"]] if r else []


class TestLignesAlignees(unittest.TestCase):
    """Une chaîne s'affiche une étape par ligne : lien à gauche, expression, propriété à droite (EL, demande du 26.10.2026)."""

    def test_les_liens_les_elements_et_les_proprietes_du_moteur(self):
        """Un ⇔ ouvre une ligne ; un « = » prolonge la ligne tant qu'elle n'a pas de propriété ; chaque propriété est écrite une seule fois, dans
        l'ordre ; chaque élément est écrit dans l'ordre."""
        vues = 0
        for entree in EQUATIONS + CALCULS:
            for chaine in chaines_du_moteur(entree):
                rangees = el.rangees_chaine(chaine)
                with self.subTest(entree=entree):
                    self.assertEqual(rangees[0][0], "")
                    self.assertEqual(sum(1 for r in rangees if r[0]), chaine.liens.count("⇔"))
                    self.assertLessEqual(len(rangees), len(chaine.elements))
                    self.assertGreaterEqual(len(rangees), 1 + chaine.liens.count("⇔"))
                    toutes = " ".join(r[1] for r in rangees).replace(r"\phantom", "")
                    position = 0
                    for e in chaine.elements:
                        texte = e.tex if isinstance(e, el.Texte) else el.tex_element(e)
                        position = toutes.index(texte, position) + len(texte)
                    vues += 1
        self.assertGreater(vues, 300)

    def test_rien_ne_se_perd_par_rapport_a_la_ligne_unique(self):
        """Les mêmes éléments et les mêmes propriétés que `tex_chaine`, répartis en lignes."""
        for entree in EQUATIONS + CALCULS:
            for chaine in chaines_du_moteur(entree):
                with self.subTest(entree=entree):
                    rangees = el.rangees_chaine(chaine)
                    ligne = el.tex_chaine(chaine)
                    for e in chaine.elements:
                        self.assertIn(el.tex_element(e), ligne)
                    if not chaine.note and not isinstance(chaine.elements[0], el.Texte):
                        voulues = ["(" + p + ")" if isinstance(p, str) else r"(car \(" + el.tex(p.expr) + r" \neq 0\))" for p in chaine.props if p]
                        self.assertEqual([r[2] for r in rangees if r[2]], voulues)

    def test_suite_d_egalites_alignee_sous_le_premier_signe_egal(self):
        rangees = el.rangees_chaine(chaines_du_moteur("2^(x-1)=3^x")[0])
        self.assertEqual(rangees[-1][0], "")
        self.assertTrue(rangees[-1][1].startswith(r"\phantom{x} = "), rangees[-1])
        self.assertEqual(rangees[-2][2], r"(car \(\log(2) - \log(3) \neq 0\))")
        self.assertEqual(rangees[-1][2], "(log a − log b = log(a/b))")
        # sans propriété sur la ligne, les égalités se suivent sur la même ligne
        calcul = el.rangees_chaine(chaines_du_moteur("log_4(sqrt(2))")[0])
        self.assertEqual(calcul, [("", r"\sqrt{2} = 2^{\frac{1}{2}} = \left(4^{\frac{1}{2}}\right)^{\frac{1}{2}} = 4^{\frac{1}{4}}", None)])
        calcul = el.rangees_chaine(chaines_du_moteur("log_4(sqrt(2))")[1])
        self.assertEqual(len(calcul), 1)
        self.assertEqual(calcul[0][2], "(log_a(a^k) = k)")
        delta = el.rangees_chaine(chaines_du_moteur("log(x^2+x+3)=0")[1])
        self.assertEqual(delta, [("", "Δ = 1^{2} - 4 \cdot 1 \cdot 2 = -7", None)])

    def test_la_note_de_verification_porte_la_coche(self):
        rangees = el.rangees_chaine(chaines_du_moteur("log(5-x)=8")[-1])
        self.assertEqual(rangees, [("", r"5 - x = 10^{8} > 0", r"(le logarithme est bien défini) \(\checkmark\)")])

    def test_le_html_de_la_page(self):
        s = rel.resoudre("2^(x-1)=3^x")
        html = s["cartes"][0]["blocs"][0]["html"]
        self.assertTrue(html.startswith('<div class="chaine"><div class="ligne"><span class="lien"></span><span class="expr">'))
        self.assertEqual(html.count('<div class="ligne">'), 7)
        self.assertEqual(html.count(r'<span class="lien">\(\iff\)</span>'), 5)
        self.assertIn('<span class="prop">(log des deux membres)</span>', html)
        self.assertIn(r'<span class="prop">(car \(\log(2) - \log(3) \neq 0\))</span>', html)


class TestCartes(unittest.TestCase):
    def test_equations_etapes_numerotees_puis_solution(self):
        for entree in EQUATIONS:
            s = rel.resoudre(entree)
            if not s["ok"]:
                continue
            with self.subTest(entree=entree):
                cartes = s["cartes"]
                self.assertEqual([c["titre"] for c in cartes[:-1]], [f"Étape {k}" for k in range(1, len(cartes))])
                for c in cartes[:-1]:
                    self.assertTrue(c["badge"])                 # la méthode
                    self.assertEqual(c["style"], "normal")
                    self.assertTrue(all(b["type"] == "texte" for b in c["blocs"]))
                final = cartes[-1]
                self.assertEqual((final["titre"], final["style"]), ("Solution", "final"))
                self.assertEqual([b["type"] for b in final["blocs"]], ["resultat"])

    def test_la_carte_finale_est_celle_du_moteur(self):
        """EL-18 sur la sortie élève : S = {valeur exacte}, puis « soit x ≈ … » quand une solution n'est pas un rationnel."""
        for entree in EQUATIONS:
            s = rel.resoudre(entree)
            if not s["ok"]:
                continue
            sa = el.analyser_saisie(entree)
            with self.subTest(entree=entree):
                self.assertEqual(s["cartes"][-1]["blocs"][0]["tex"], el.tex_solution(el.corriger_equation(sa.g, sa.d, sa.inconnue)))

    def test_x_deja_isole_a_quand_meme_sa_ligne_finale(self):
        s = rel.resoudre("x=ln(3)")
        self.assertEqual([c["titre"] for c in s["cartes"]], ["Solution"])
        self.assertEqual(s["cartes"][0]["blocs"][0]["tex"], r"S = \left\{\ln(3)\right\} \text{, soit } x \approx 1{,}099")

    def test_lignes_finales_de_reference(self):
        attendu = {
            "3^(x+1)-27=0": r"S = \left\{2\right\}",
            "2^x=100": r"S = \left\{\frac{2}{\log(2)}\right\} \text{, soit } x \approx 6{,}644",
            "5^(8x)=-25": r"S = \varnothing",
            "2^(x+1)=2*2^x": r"S = \mathbb{R}",
            "log(5-x)=8": r"S = \left\{-99\text{’}999\text{’}995\right\}",
            "log_x(256)=4": r"S = \left\{4\right\}",
        }
        for entree, tex in attendu.items():
            with self.subTest(entree=entree):
                self.assertEqual(rel.resoudre(entree)["cartes"][-1]["blocs"][0]["tex"], tex)

    def test_les_methodes_en_badge_dans_l_ordre(self):
        titres = lambda e: [(c["titre"], c.get("badge")) for c in rel.resoudre(e)["cartes"]]
        self.assertEqual(titres("3^(x+1)-27=0"), [("Étape 1", "Isoler l'exponentielle"), ("Étape 2", "Même base"), ("Solution", None)])
        self.assertEqual(titres("log_x(256)=4"), [("Étape 1", "Condition"), ("Étape 2", "Définition du logarithme"), ("Solution", None)])
        self.assertEqual([t for t, _ in titres("10^x*(10^x-4)=0")], ["Étape 1", "Étape 2", "Étape 3", "Solution"])
        self.assertEqual([b for _, b in titres("10^x*(10^x-4)=0")][:3], ["Produit nul", "Facteur 1", "Facteur 2"])

    def test_la_remarque_du_moteur_est_dans_la_derniere_carte_d_etapes(self):
        s = rel.resoudre("log(x^2+x+3)=0")
        derniere = s["cartes"][-2]
        self.assertEqual(derniere["blocs"][-1]["html"], "Δ &lt; 0 : l'équation n'a aucune solution réelle.")
        self.assertEqual(s["cartes"][-1]["blocs"][0]["tex"], r"S = \varnothing")
        s = rel.resoudre("log(x^2+x+3)+1=1")            # deux cartes d'étapes : la remarque est dans la seconde, pas dans la première
        self.assertEqual(len(s["cartes"]), 3)
        self.assertNotIn("Δ &lt; 0", " ".join(b["html"] for b in s["cartes"][0]["blocs"]))
        self.assertEqual(s["cartes"][1]["blocs"][-1]["html"], "Δ &lt; 0 : l'équation n'a aucune solution réelle.")
        s = rel.resoudre("2^(x+1)=2*2^x")
        self.assertEqual(s["cartes"][-2]["blocs"][-1]["html"], "Cette égalité est vraie pour tout nombre réel.")

    def test_calculs_carte_calcul_puis_resultat(self):
        for entree in CALCULS:
            s = rel.resoudre(entree)
            with self.subTest(entree=entree):
                self.assertTrue(s["ok"])
                final = s["cartes"][-1]
                self.assertEqual((final["titre"], final["style"]), ("Résultat", "final"))
                sa = el.analyser_saisie(entree)
                self.assertEqual(final["blocs"][0]["tex"], el.tex_resultat(el.calculer_logarithme(sa.g)))
                self.assertEqual([c["titre"] for c in s["cartes"][:-1]], [f"Étape {k}" for k in range(1, len(s["cartes"]))])
                self.assertTrue(all(c["badge"] == "Calcul" for c in s["cartes"][:-1]))
        self.assertEqual([c["titre"] for c in rel.resoudre("log_8(64)")["cartes"]], ["Étape 1", "Résultat"])
        self.assertEqual([c["titre"] for c in rel.resoudre("ln(7)")["cartes"]], ["Résultat"])      # rien à expliquer : la valeur seule
        self.assertEqual(rel.resoudre("log_8(64)")["cartes"][-1]["blocs"][0]["tex"], r"\log_{8}(64) = 2")

    def test_aucun_etat_d_une_resolution_a_l_autre(self):
        """Un énoncé à décimaux (1,9025) ne change pas l'écriture de l'énoncé suivant (1/10), dans les deux sens."""
        seul = {e: rel.resoudre(e) for e in ("log(x)=-1", "2000*1,045^n=3805", "log(x)=-0,27")}
        for e in ("2000*1,045^n=3805", "log(x)=-0,27", "log(x)=-1", "x*2^x=8", "log(x)=-1", "2000*1,045^n=3805"):
            self.assertEqual(rel.resoudre(e), rel.resoudre(e))
            if e in seul:
                self.assertEqual(rel.resoudre(e), seul[e], e)


class TestMessages(unittest.TestCase):
    def erreur(self, entree):
        s = rel.resoudre(entree)
        self.assertFalse(s["ok"], entree)
        self.assertEqual(so.valider(s), [], entree)
        self.assertNotIn("Traceback", s["erreur"])
        return s["erreur"]

    def test_vrai_hors_programme(self):
        for entree in HORS_PROGRAMME:
            with self.subTest(entree=entree):
                self.assertEqual(self.erreur(entree), "Cette équation ne se résout pas avec les méthodes du cours.")

    def test_pas_encore_traite(self):
        for entree in PAS_ENCORE:
            with self.subTest(entree=entree):
                self.assertEqual(self.erreur(entree), "Cet outil ne traite pas encore ce type d'équation.")

    def test_jamais_non_applicable(self):
        for entree in HORS_PROGRAMME + PAS_ENCORE + CALCULS_NON_RESOLUS + ERREURS_DE_LECTURE:
            with self.subTest(entree=entree):
                self.assertNotIn("applicable", self.erreur(entree))

    def test_calculs_non_resolus(self):
        attendu = {
            "2log(5)": "Cet outil ne traite pas encore ce type de calcul.",
            "log(2)+log(3)": "Cet outil ne traite pas encore ce type de calcul.",
            "log_2(e)": "Cet outil ne traite pas encore ce type de calcul.",
            "log(0)": "Le logarithme d'un nombre négatif ou nul n'est pas défini.",
            "log(-5)": "Le logarithme d'un nombre négatif ou nul n'est pas défini.",
            "ln(0)": "Le logarithme d'un nombre négatif ou nul n'est pas défini.",
            "2+3": "Écrivez une équation (avec =) ou un logarithme à calculer, par exemple log_2(50).",
            "sqrt(2)": "Écrivez une équation (avec =) ou un logarithme à calculer, par exemple log_2(50).",
        }
        for entree, message in attendu.items():
            with self.subTest(entree=entree):
                self.assertEqual(self.erreur(entree), message)
        for entree in CALCULS_NON_RESOLUS:
            self.erreur(entree)

    def test_erreurs_de_lecture_ont_le_message_du_moteur(self):
        for entree in ERREURS_DE_LECTURE:
            with self.subTest(entree=entree):
                with self.assertRaises(el.ErreurSaisie) as c:
                    el.analyser_saisie(entree)
                self.assertEqual(self.erreur(entree), str(c.exception))
        self.assertIn("inéquations", self.erreur("x<3"))

    def test_une_equation_resolue_n_est_jamais_une_erreur(self):
        for entree in EQUATIONS + CALCULS:
            with self.subTest(entree=entree):
                self.assertTrue(rel.resoudre(entree)["ok"])


if __name__ == "__main__":
    unittest.main()
