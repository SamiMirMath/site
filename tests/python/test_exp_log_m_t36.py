"""T36 (29.10.2026) — Trous de la filière M relevés dans le polycopié Javet et la brochure Amaudruz : exposants non polynomiaux (1/x, √x, ± ln x), bases
polynomiales, bicarrés, log_x(c) = p/q, constantes irrationnelles dans un regroupement, cas isolés. Pour chaque batterie : les solutions attendues (les deux
méthodes quand l'équation en a deux), l'oracle mpmath indépendant du moteur (chaque solution est une racine dans l'ensemble de définition, aucune racine n'est
perdue), les propriétés de la liste fermée, une sortie valide, et la 3C qui ne change pas (aucune carte d'ensemble de définition)."""
import json
import unittest

import moteurs  # noqa: F401  (chemins des moteurs)
import exp_log as el
import exp_log_m as elm
import resoudre_el as rel
import sortie as so
from cas_el import BATTERIE_M_BASE_POLYNOMIALE, BATTERIE_M_EXPOSANTS
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
                    self.assertEqual(r["etapes"][0]["titre"], "Ensemble de définition")
                    for carte in r["etapes"]:
                        for ligne in carte.get("lignes", []):
                            if isinstance(ligne, el.Chaine):
                                for p in ligne.props:
                                    self.assertTrue(p is None or p in el.PROPRIETES or p in elm.PROPRIETES_M or isinstance(p, el.Car), (entree, p))
                                if ligne.note:
                                    self.assertTrue(ligne.note in el.PROPRIETES or ligne.note.startswith(("dans l'ensemble", "rejetée")), (entree, ligne.note))

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


if __name__ == "__main__":
    unittest.main()
