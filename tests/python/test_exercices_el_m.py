"""T35 (étape 5) — Exercices au hasard de la filière M (EL-32) : `exercice(niveau, graine, "M")` est déterministe, produit un gabarit du niveau,
et le moteur le résout (oracle mpmath indépendant : chaque solution annule g − d et est dans l'ensemble de définition, aucune racine perdue)."""
import json
import re
import unittest
from fractions import Fraction as F

import moteurs  # noqa: F401  (chemins des moteurs)
import exp_log as el
import exp_log_m as elm
import resoudre_el as rel
import sortie as so
from test_exp_log_m import MP, ecart, racines

GRAINES = range(500)
GRAINES_BALAYAGE = range(0, 500, 25)         # le balayage numérique des racines est lent : une graine sur vingt-cinq
ARG = r"-?(?:\d*x|x)(?:[+-]\d+)?"
NOMBRE = r"-?\d+"
GABARITS = {
    "exponentielle": [r"[^l]*", ],
    "definition": [rf"log(?:_\d)?\({ARG}\)={NOMBRE}", rf"ln\({ARG}\)={NOMBRE}", r"log\(x\^2(?:[+-]x|[+-]\d*x)?(?:[+-]\d+)?\)=\d", r"log_x\(\d+\)=\d"],
    "sommes": [rf"(?:log|ln|log_\d)\({ARG}\)\+(?:log|ln|log_\d)\({ARG}\)=(?:\d|ln\(\d+\))",
               rf"log\({ARG}\)-log\({ARG}\)=1"],
    "egalite": [rf"2log\({ARG}\)=log\({ARG}\)", r"log\(x\)=2log\(\d\)\+log\(\d\)-log\(\d\)", rf"log\({ARG}\)-log\(\d\)=log\({ARG}\)", rf"log\({ARG}\)=log\({ARG}\)\+1"],
    "variable": [r"(?:\d+\*)?(?:\d+\^x|\d+\^\(2x\))(?:[+-](?:\d+\*)?\d+\^x)?[+-]\d+=0", r"e\^\(2x\)(?:[+-](?:\d+\*)?e\^x)?[+-]\d+=0", r"\d+\^\(x\+\d\)\+\d+\^\(-x\)=\d+"],
    "difficile": [rf"log\({ARG}\)\+log\(-?\d+-x\)=\d", rf"log\({ARG}\)\+log\({ARG}\)=log\({ARG}\)\+log\(\d\)", r"log\(x\^2(?:[+-]\d+)?\)=2log\(x(?:[+-]\d)?\)"],
}


class TestPoolM(unittest.TestCase):
    def test_deterministe_et_varie(self):
        for niveau in elm.NIVEAUX_M:
            for graine in range(50):
                self.assertEqual(el.exercice(niveau, graine, "M"), el.exercice(niveau, graine, "M"))
            self.assertGreater(len({el.exercice(niveau, g, "M")["expr"] for g in range(100)}), 25, niveau)

    def test_gabarit_du_niveau(self):
        for niveau, motifs in GABARITS.items():
            for graine in GRAINES:
                e = el.exercice(niveau, graine, "M")
                self.assertTrue(e["ok"] and e["niveau"] == niveau)
                with self.subTest(niveau=niveau, expr=e["expr"]):
                    self.assertTrue(any(re.fullmatch(m, e["expr"]) for m in motifs), e["expr"])

    def test_l_exercice_par_defaut_n_a_pas_change_et_le_pool_m_a_ses_niveaux(self):
        self.assertEqual(el.exercice("facile", 3), el.exercice("facile", 3, "C"))
        self.assertEqual(el.exercice("facile", 3, "M"), {"ok": False, "erreur": "Niveau d'exercice inconnu."})
        self.assertEqual(el.exercice("exponentielle", 3, "C"), {"ok": False, "erreur": "Niveau d'exercice inconnu."})
        self.assertTrue(json.loads(el.exercice_json("sommes", "M"))["ok"])

    def test_le_moteur_resout_chaque_exercice_dans_les_deux_filieres_de_la_page(self):
        for niveau in elm.NIVEAUX_M:
            for graine in GRAINES:
                expr = el.exercice(niveau, graine, "M")["expr"]
                with self.subTest(niveau=niveau, expr=expr):
                    s = rel.resoudre(expr, "M")
                    self.assertTrue(s["ok"], (expr, s))
                    self.assertEqual(so.valider(s), [])

    def _oracle(self, niveau):
        """Chaque solution annule g − d et est dans l'ED (500 graines) ; aucune racine n'est perdue (balayage, une graine sur vingt-cinq)."""
        for graine in GRAINES:
            expr = el.exercice(niveau, graine, "M")["expr"]
            s = el.analyser_saisie(expr)
            v = elm.variantes_changement(s.g, s.d, s.inconnue)
            r = v[el.METHODE_LOGARITHMES] if v is not None else (elm.corriger_equation(s.g, s.d, s.inconnue) or el.corriger_equation(s.g, s.d, s.inconnue, parametres=s.parametres))
            with self.subTest(niveau=niveau, expr=expr):
                self.assertIsNotNone(r)
                retenues = [MP.mpf(el.valeur(n)) for n in r["solutions"]]
                for x in retenues:
                    e = ecart(s, x)
                    self.assertIsNotNone(e, "solution hors de l'ensemble de définition")
                    self.assertLess(abs(e), MP.mpf("1e-9") * (1 + abs(x)))
                if graine in GRAINES_BALAYAGE and niveau != "exponentielle":
                    for rac in racines(s):
                        self.assertTrue(any(abs(rac - x) < MP.mpf("1e-9") * (1 + abs(rac)) for x in retenues), ("racine perdue", rac))

    def test_les_deux_methodes_des_exercices_exponentiels_ont_le_meme_s(self):
        for niveau in ("exponentielle", "variable"):
            for graine in range(0, 500, 5):
                expr = el.exercice(niveau, graine, "M")["expr"]
                s = el.analyser_saisie(expr)
                v = elm.variantes_changement(s.g, s.d, s.inconnue) or el.variantes_equation(s.g, s.d, s.inconnue, s.parametres)
                if v is None:
                    continue
                a, b = v[el.METHODE_MEME_BASE], v[el.METHODE_LOGARITHMES]
                if a.get("message"):
                    continue
                with self.subTest(niveau=niveau, expr=expr):
                    self.assertEqual([round(el.valeur(n), 9) for n in a["solutions"]], [round(el.valeur(n), 9) for n in b["solutions"]])

    def test_le_niveau_sommes_a_souvent_une_solution_rejetee(self):
        rejets = total = 0
        for graine in GRAINES:
            expr = el.exercice("sommes", graine, "M")["expr"]
            s = el.analyser_saisie(expr)
            r = elm.corriger_equation(s.g, s.d, s.inconnue)
            if r is not None and r.get("candidats"):
                total += 1
                rejets += len(r["candidats"]) > len(r["solutions"])
        self.assertGreater(total, 450)
        self.assertGreater(rejets / total, 0.5)

    def test_le_niveau_variable_a_deux_solutions_ou_une_racine_rejetee(self):
        deux = rejetee = 0
        for graine in GRAINES:
            expr = el.exercice("variable", graine, "M")["expr"]
            s = el.analyser_saisie(expr)
            r = elm.variantes_changement(s.g, s.d, s.inconnue)[el.METHODE_LOGARITHMES]
            deux += len(r["solutions"]) == 2
            rejetee += any("rejetée" in (l.note or "") for c in r["etapes"] for l in c["lignes"] if isinstance(l, el.Chaine))
        self.assertGreater(deux, 100)
        self.assertGreater(rejetee, 60)

    def test_le_niveau_difficile_contient_des_ed_vides(self):
        vides = 0
        for graine in GRAINES:
            s = el.analyser_saisie(el.exercice("difficile", graine, "M")["expr"])
            vides += elm.corriger_equation(s.g, s.d, s.inconnue)["etapes"][0]["ed"].vide
        self.assertGreater(vides, 40)


def _methode_oracle(niveau):
    def test(self):
        self._oracle(niveau)
    test.__doc__ = f"Oracle mpmath sur le niveau « {niveau} » (une méthode par niveau : les niveaux se répartissent entre les processus de pytest-xdist)."
    return test


for _niveau in elm.NIVEAUX_M:
    setattr(TestPoolM, f"test_oracle_les_solutions_sont_les_racines_dans_l_ensemble_de_definition_{_niveau}", _methode_oracle(_niveau))


if __name__ == "__main__":
    unittest.main()
