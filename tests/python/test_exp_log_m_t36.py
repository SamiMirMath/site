"""T36 (29.10.2026) — Trous de la filière M relevés dans le polycopié Javet et la brochure Amaudruz : exposants non polynomiaux (1/x, √x, ± ln x), bases
polynomiales, bicarrés, log_x(c) = p/q, constantes irrationnelles dans un regroupement, cas isolés. Pour chaque batterie : les solutions attendues (les deux
méthodes quand l'équation en a deux), l'oracle mpmath indépendant du moteur (chaque solution est une racine dans l'ensemble de définition, aucune racine n'est
perdue), les propriétés de la liste fermée, une sortie valide, et la 3C qui ne change pas (aucune carte d'ensemble de définition)."""
import json
import unittest
from fractions import Fraction as F

import moteurs  # noqa: F401  (chemins des moteurs)
import exp_log as el
import exp_log_m as elm
import resoudre_el as rel
import sortie as so
from cas_el import BATTERIE_M_BASE_POLYNOMIALE, BATTERIE_M_BASE_RATIONNELLE, BATTERIE_M_BICARRE, BATTERIE_M_EXPOSANTS, BATTERIE_M_IRRATIONNEL
from test_exp_log_m import MP, ecart, racines


def corrige_m(entree):
    """{méthode: résultat} de la filière M pour l'entrée (une seule méthode « logarithmes » quand l'équation n'en a pas deux), None si elle n'est pas traitée."""
    s = el.analyser_saisie(entree, "M")
    v = elm.variantes_exposant(s.g, s.d, s.inconnue) or elm.variantes_changement(s.g, s.d, s.inconnue)
    if v is not None:
        return v
    r = elm.corriger_equation(s.g, s.d, s.inconnue)
    return None if r is None else {el.METHODE_LOGARITHMES: r}


class _Batterie:
    """Les vérifications communes à toutes les batteries ; chaque sous-classe donne BATTERIE (saisie, solutions arrondies à 10⁻³) et DEUX_METHODES."""
    BATTERIE = []
    DEUX_METHODES = True
    ED_EN_PREMIER = True                      # une équation exponentielle sans logarithme ni dénominateur n'a pas de carte d'ensemble de définition

    def test_les_solutions_attendues_dans_chaque_methode(self):
        for entree, attendu in self.BATTERIE:
            with self.subTest(entree=entree):
                v = corrige_m(entree)
                self.assertIsNotNone(v)
                if self.DEUX_METHODES:
                    self.assertEqual(set(v), set(el.METHODES))
                for methode, r in v.items():
                    if r.get("message"):
                        self.assertEqual(methode, el.METHODE_MEME_BASE, entree)       # « 20 n'est pas une puissance de 3 : il faut les logarithmes. »
                        continue
                    sol = sorted(el.valeur(n) for n in r["solutions"])
                    self.assertEqual(len(sol), len(attendu), (entree, methode, sol))
                    for a, b in zip(sol, sorted(attendu)):
                        self.assertAlmostEqual(a, b, delta=1e-3 * (1 + abs(b)))

    def test_oracle_les_solutions_sont_exactement_les_racines_dans_l_ensemble_de_definition(self):
        for entree, _ in self.BATTERIE:
            with self.subTest(entree=entree):
                s = el.analyser_saisie(entree, "M")
                for methode, r in corrige_m(entree).items():
                    if r.get("message"):
                        continue
                    retenues = [MP.mpf(el.valeur(n)) for n in r["solutions"]]
                    for x in retenues:
                        e = ecart(s, x)
                        self.assertIsNotNone(e, "solution hors de l'ensemble de définition")
                        self.assertLess(abs(e), MP.mpf("1e-9") * (1 + abs(x)))
                    for rac in racines(s):
                        self.assertTrue(any(abs(rac - x) < MP.mpf("1e-9") * (1 + abs(rac)) for x in retenues), ("racine perdue", methode, rac))

    def test_proprietes_de_la_liste_fermee_et_ed_en_premier(self):
        for entree, _ in self.BATTERIE:
            with self.subTest(entree=entree):
                for r in corrige_m(entree).values():
                    if self.ED_EN_PREMIER:
                        self.assertEqual(r["etapes"][0]["titre"], "Ensemble de définition")
                    for carte in r["etapes"]:
                        for ligne in carte.get("lignes", []):
                            if isinstance(ligne, el.Chaine):
                                for p in ligne.props:
                                    self.assertTrue(p is None or p in el.PROPRIETES or p in elm.PROPRIETES_M or isinstance(p, el.Car), (entree, p))
                                if ligne.note:
                                    self.assertTrue(ligne.note in el.PROPRIETES or ligne.note.startswith(("dans l'ensemble", "rejetée", "retenue")), (entree, ligne.note))

    def test_sortie_valide_vouvoiement_et_3c_inchangee(self):
        for entree, _ in self.BATTERIE:
            with self.subTest(entree=entree):
                m = rel.resoudre(entree, "M")
                self.assertTrue(m["ok"], m)
                self.assertEqual(so.valider(m), [])
                self.assertNotRegex(json.dumps(m, ensure_ascii=False), r"\b(tu|ton|ta|tes|toi)\b")
                c = rel.resoudre(entree, "C")
                self.assertNotIn("Ensemble de définition", json.dumps(c, ensure_ascii=False))


class TestExposants(_Batterie, unittest.TestCase):
    BATTERIE = BATTERIE_M_EXPOSANTS


class TestBasePolynomiale(_Batterie, unittest.TestCase):
    BATTERIE = BATTERIE_M_BASE_POLYNOMIALE
    DEUX_METHODES = False

    def test_la_3c_garde_son_message_de_lecture(self):
        for entree, _ in self.BATTERIE:
            with self.subTest(entree=entree):
                self.assertEqual(rel.resoudre(entree, "C"), {"ok": False, "erreur": el.MESSAGE_AUTRE_BASE})
                self.assertEqual(el.apercu(entree)["ok"], True)             # l'aperçu lit la base : le message ne vient qu'à la résolution

    def test_les_formes_refusees_restent_en_pas_encore(self):
        for entree in ["log_(x+1)(x+2)=1", "log_(x^2)(4)=1", "log_(2x)(5)=1/2", "log_(2x)(1296)=0", "log_(2x)(-4)=2", "log_(2x)(1296)=x"]:
            with self.subTest(entree=entree):
                r = rel.resoudre(entree, "M")
                self.assertFalse(r["ok"])
                self.assertIn(r["erreur"], (el.MESSAGE_PAS_ENCORE, el.MESSAGE_HORS_PROGRAMME))

    def test_lecture_de_la_base(self):
        self.assertEqual(el.tex_saisie(*el.lire_membres("log_(2x)(1296)=4")), r"\log_{2x}(1\text{’}296) = 4")
        self.assertEqual(el.tex_saisie(*el.lire_membres("log_( 2 )(8)=3")), el.tex_saisie(*el.lire_membres("log_2(8)=3")))
        self.assertEqual(el.tex_saisie(*el.lire_membres("log_(10)(x)=3")), el.tex_saisie(*el.lire_membres("log(x)=3")))
        for faux, message in [("log_()(8)=3", "vide"), ("log_(2x(8)=3", "parenthèse"), ("log_(1)(8)=3", "différente de 1"), ("log_(2x)=3", "Pour une autre base")]:
            with self.subTest(faux=faux):
                with self.assertRaises(el.ErreurSaisie) as e:
                    el.analyser_saisie(faux, "M")
                self.assertIn(message, str(e.exception))


class TestBicarre(_Batterie, unittest.TestCase):
    BATTERIE = BATTERIE_M_BICARRE
    ED_EN_PREMIER = False

    def test_la_carte_bicarree_pose_u_et_garde_les_u_positifs(self):
        v = corrige_m("3^x-3*3^(-x)-4*3^(-3x)=0")[el.METHODE_LOGARITHMES]
        titres = [c["titre"] for c in v["etapes"]]
        self.assertEqual(titres[:3], ["Changement de variable", "Équation bicarrée", "Valeurs de t"])
        notes = [l.note for c in v["etapes"] for l in c.get("lignes", []) if isinstance(l, el.Chaine) and l.note]
        self.assertTrue(any(n.startswith("rejetée : u = t²") for n in notes), notes)       # u = −1 rejeté
        self.assertTrue(any(n.startswith("rejetée") and "exponentielle" in n for n in notes), notes)       # t = −2 rejeté

    def test_une_racine_irrationnelle_de_t_reste_pas_encore(self):
        self.assertEqual(rel.resoudre("3^x+3^(-x)-6*3^(-3x)=0", "M"), {"ok": False, "erreur": el.MESSAGE_PAS_ENCORE})
        self.assertFalse(rel.resoudre("3^x+3^(-x)-6*3^(-3x)=0", "C")["ok"])


class TestBaseRationnelle(_Batterie, unittest.TestCase):
    BATTERIE = BATTERIE_M_BASE_RATIONNELLE
    DEUX_METHODES = False

    def test_les_cas_entiers_de_la_3c_ne_changent_pas(self):
        for entree in ["log_x(9)=-2", "log_x(4)=2", "log_x(27)=3", "log_x(1/8)=3"]:
            with self.subTest(entree=entree):
                self.assertTrue(rel.resoudre(entree, "M")["ok"])
                self.assertIsNone(elm.base_inconnue_rationnelle(*(lambda s: (s.g, s.d, s.inconnue))(el.analyser_saisie(entree, "M"))))

    def test_les_formes_refusees_restent_en_pas_encore(self):
        for entree in ["log_x(5)=13/2", "log_x(5)=1/13", "log_x(x+1)=3/2"]:
            with self.subTest(entree=entree):
                r = rel.resoudre(entree, "M")
                self.assertFalse(r["ok"])


class TestIrrationnel(_Batterie, unittest.TestCase):
    BATTERIE = BATTERIE_M_IRRATIONNEL
    DEUX_METHODES = False

    def test_le_signe_et_l_appartenance_sont_exacts_pres_de_zero(self):
        """Δ et l'appartenance à l'ED sont décidés par `_signe_exact` (80 chiffres, zéro sous 10⁻⁵⁰), jamais par un arrondi d'affichage : deux écritures d'un
        même irrationnel donnent exactement 0, un écart de 10⁻⁴⁰ garde son signe."""
        s = el.analyser_saisie("ln(x)+ln(x+1)=3", "M")
        r = elm.corriger_equation(s.g, s.d, s.inconnue)
        self.assertEqual(len(r["candidats"]), 2)
        self.assertEqual(len(r["solutions"]), 1)
        racine_basse, racine_haute = sorted(r["candidats"], key=el.valeur)
        self.assertEqual(elm._signe_exact(el.Op("+", racine_basse, el.Nb(0))), -1)
        self.assertEqual(elm._signe_exact(el.Op("-", racine_haute, racine_haute)), 0)           # deux écritures d'un même irrationnel : zéro exact
        self.assertEqual(elm._signe_exact(el.Op("-", racine_haute, el.Op("+", racine_haute, el.Nb(F(1, 10 ** 40))))), -1)

    def test_les_limites_assumees_restent_en_pas_encore(self):
        for entree in ["ln(x)-ln(x+1)=1", "ln(x^3)+ln(2)=1", "ln(x)=ln(x+1)+1/2", "ln(x)*ln(x+1)=3"]:
            with self.subTest(entree=entree):
                r = rel.resoudre(entree, "M")
                self.assertFalse(r["ok"])


if __name__ == "__main__":
    unittest.main()
