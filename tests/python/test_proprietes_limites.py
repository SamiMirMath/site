"""T02 — Limites et asymptotes : chaque limite annoncée est confirmée par une sonde
numérique haute précision, indépendante de SymPy (critères LA-04, LA-05)."""
import unittest

import mpmath

from moteurs import ensemble_def as ed
import limites_asymptotes as la
import oracle

mp = mpmath.mp

CAS = [
    # rationnelles
    "1/(x-2)", "(x^2-1)/(x-3)", "1/x^2", "x^2/(x-1)", "(2x+1)/(x-1)", "(2x^2+1)/(x^2-1)", "(x^3+1)/(x-2)",
    "(x^2-1)/(x-1)", "1/(x^2-2)", "x/(x^2+1)", "(x^2+x-2)/(x^2-1)", "(x^3-1)/(x^2+1)", "(3x^2-x)/(x^2+4)",
    "(x+3)/((x-1)^2)", "(x^4-1)/(x^2-4)", "-x^2/(2x+4)", "(x^2-4x+3)/(x-1)^2", "5/(3-x)",
    # transcendantes
    "e^(2x)", "ln(x)", "ln(x-1)", "x^2*e^(-x)", "ln(x)/x", "x*e^x", "e^x/x", "(e^x-1)/x", "x*ln(x^2)",
    "x/sqrt(x^2)", "e^(1/x)", "x+ln(x)", "sqrt(x^2+1)", "sqrt(x^2-4x+5)", "ln(x^2-4x)/(x-5)",
    "x*ln(x)", "ln(x)^2/x", "e^(-x)*(x+1)", "x-ln(x)", "sqrt(x)", "1/ln(x)", "x+1/x", "x*e^(1/x)",
    "ln(1+1/x)", "sqrt(x^2+x)-x",
]

# Sondes très lointaines / très proches (possibles grâce aux 50 chiffres de l'oracle) :
# les limites logarithmiques convergent lentement (1/ln(x) ≈ 0,05 en 10^8, ≈ 0,014 en 10^30).
GRANDS = [mp.mpf(10) ** k for k in (2, 4, 8, 16, 30)]
PETITS = [mp.mpf(10) ** -k for k in (3, 6, 12, 30)]


def petits(p):
    """Écarts de sonde autour du point p. Le point n'est connu qu'en flottant (16 chiffres) :
    sauf en 0 (exact), on ne s'en approche pas plus près que 1e-12 relatif, sinon une
    valeur irrationnelle comme √2 serait sondée du mauvais côté."""
    return PETITS if p == 0 else [h for h in PETITS if h >= mp.mpf("1e-12") * (1 + abs(p))]


def sens_infini(ou):
    return 1 if r"+\infty" in ou else -1


def suite(arbre, xs):
    vals = [oracle.valeur(arbre, x) for x in xs]
    return [v for v in vals if v is not None]


class TestProprietesLimites(unittest.TestCase):
    def assert_tend_vers(self, vals, cible_tex, cible_val, msg):
        self.assertGreaterEqual(len(vals), 2, msg + " : pas assez de points évaluables")
        if cible_tex in (r"+\infty", r"-\infty"):
            s = 1 if cible_tex == r"+\infty" else -1
            self.assertTrue(all(s * v > 0 for v in vals[1:]), msg + f" : signe {vals}")
            self.assertTrue(all(s * b > s * a for a, b in zip(vals, vals[1:])), msg + f" : non croissant {vals}")
            self.assertGreater(abs(vals[-1]), 10, msg + f" : {vals}")
        else:
            self.assertIsNotNone(cible_val, msg + " : valeur numérique absente")
            ecarts = [abs(v - cible_val) for v in vals]
            self.assertLessEqual(ecarts[-1], 0.02 * (1 + abs(cible_val)), msg + f" : {vals}")
            self.assertLessEqual(ecarts[-1], ecarts[0] + mp.mpf("1e-30"), msg + f" : ne se rapproche pas {vals}")

    def test_limites_confirmees(self):
        for f in CAS:
            r = la.etudier(f)
            arbre = ed.lire(f)
            with self.subTest(f=f):
                self.assertTrue(r["ok"], r.get("erreur"))
            for a in r["asymptotes"]:
                msg = f"{f} : {a['genre']} ({a['ou']})"
                with self.subTest(f=f, asymptote=a["ou"], genre=a["genre"]):
                    g = a["genre"]
                    if g in ("horizontale", "aucune"):
                        s = sens_infini(a["ou"])
                        self.assert_tend_vers(suite(arbre, [s * X for X in GRANDS]),
                                              a["valeur_tex"], a.get("valeur_val"), msg)
                    elif g == "oblique":
                        s = sens_infini(a["ou"])
                        ecarts = [abs(oracle.valeur(arbre, s * X) - (a["a_val"] * s * X + a["b_val"]))
                                  for X in GRANDS]
                        self.assertLess(ecarts[-1], 0.01, msg + f" : {ecarts}")
                        self.assertLessEqual(ecarts[-1], ecarts[0], msg + f" : {ecarts}")
                    else:
                        p = mp.mpf(a["point_val"])
                        cotes = []
                        if g in ("verticale", "saut"):
                            if a.get("gauche_tex"):
                                cotes.append((-1, a["gauche_tex"], a.get("gauche_val")))
                            if a.get("droite_tex"):
                                cotes.append((1, a["droite_tex"], a.get("droite_val")))
                            if g == "verticale":
                                self.assertTrue(any(r"\infty" in t for _, t, _ in cotes), msg)
                        elif g == "trou":
                            cotes = [(s, a["valeur_tex"], a.get("valeur_val")) for s in (-1, 1)
                                     if oracle.definie(arbre, p + s * petits(p)[0])]
                        else:
                            self.fail(f"genre inconnu : {g}")
                        for s, t, v in cotes:
                            self.assert_tend_vers(suite(arbre, [p + s * h for h in petits(p)]), t, v,
                                                  msg + (" à gauche" if s < 0 else " à droite"))


if __name__ == "__main__":
    unittest.main()
