"""T02 — Ensemble de définition : propriétés vérifiées par l'oracle haute précision
(critère ED-02 de docs/specifications/ensemble-definition.md)."""
import unittest

from moteurs import ensemble_def as ed
import oracle
from generateurs import fonctions

N_FONCTIONS = 1000
GRILLE = [-12 + 0.137 * i for i in range(176)] + [-1e3, -250.5, 250.5, 1e3]

# Fonctions dont un zéro double est une valeur interdite : cas où le contrôle numérique
# de la page signale à tort un désaccord (voir test_controle_numerique_sans_fausse_alerte).
ZEROS_DOUBLES = ["ln(x^2-10x+25)", "1/(x^2-6x+9)", "(x*ln(2x+3))/((x^2-8x+16))", "ln(x^2-8x+16)",
                 "sqrt(x^2-4x+4)", "1/(4x^2+4x+1)"]


def points_de_test(ED):
    pts = list(GRILLE)
    for iv in ED:
        for p in (iv.lo, iv.hi):
            if p is not None:
                for d in (1e-7, 1e-4, 1e-2):
                    pts += [p.val - d * (1 + abs(p.val)), p.val + d * (1 + abs(p.val))]
    # trop près d'une borne, l'arrondi de la borne elle-même rend le test non significatif
    return [x for x in pts if not any(ed.iv_proche(iv, x) for iv in ED)]


class TestProprietesEnsembleDefinition(unittest.TestCase):
    def test_ed_conforme_oracle(self):
        """Pour chaque fonction générée : f est définie en x (oracle) ⟺ x ∈ ED trouvé."""
        for f in fonctions(N_FONCTIONS):
            res, arbre, ED = ed._analyser(f)
            with self.subTest(f=f):
                self.assertTrue(res["ok"], res.get("erreur"))
                self.assertTrue(res["complet"], "condition non résolue")
                for x in points_de_test(ED):
                    self.assertEqual(oracle.definie(arbre, x), ed.contient(ED, x),
                                     f"x = {x!r}, ED = {res['ED_tex']}")

    def test_zeros_doubles_ed_juste(self):
        for f in ZEROS_DOUBLES:
            res, arbre, ED = ed._analyser(f)
            with self.subTest(f=f):
                for x in points_de_test(ED):
                    self.assertEqual(oracle.definie(arbre, x), ed.contient(ED, x), f"x = {x!r}")

    @unittest.expectedFailure
    def test_controle_numerique_sans_fausse_alerte(self):
        """BUG CONNU (non corrigé) : près d'un zéro double, `evaluer` arrondit à 0 une valeur
        de l'ordre de 1e-12 (seuil anti-compensation de ensemble_def.py), et le contrôle
        numérique affiché à l'élève signale un « désaccord » alors que l'ED est juste.
        Quand ce test passera, retirer @expectedFailure."""
        for f in ZEROS_DOUBLES + fonctions(100, graine=7):
            with self.subTest(f=f):
                self.assertTrue(ed.verifier(f)["accord"])


if __name__ == "__main__":
    unittest.main()
