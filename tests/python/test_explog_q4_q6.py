"""Chantier explog-q4-q6 (questions Q4 et Q6 de docs/chantiers/explog-suite/suivi.md).

Q6 — Méthode « Même base / définition » : jamais « Il faut les logarithmes. » quand les deux membres ont la même base.
Avant : 2^(x² − 5x) = 2^(−1/2) (et tout exposant fractionnaire ou décimal donnant un trinôme à coefficients non entiers) affichait
« Il faut les logarithmes. », sans carte « Solution ». Deux causes, toutes deux dans exp_log.py :
- `_isoler` refuse un membre constant irrationnel (2^(−1/2)), alors qu'avec a^A = b^B il n'y a rien à isoler ;
- `_resoudre_polynome` refuse un trinôme à coefficients non entiers (x² − 5x + 1/2 = 0), que la méthode B résout (`_suite_polynome`).
Après : x² − 5x = −1/2 ⇔ x² − 5x + 1/2 = 0, Δ = 23, x₁, x₂ — la suite de la méthode B, dans les filières C et M.

Les solutions sont confirmées par l'oracle (tests/python/oracle.py, mpmath 50 chiffres, arbre de l'outil ED, indépendant d'Exp-log)."""
import re
import unittest

import mpmath

import moteurs  # noqa: F401  (chemins des moteurs)
from moteurs import ensemble_def as ed
import oracle
import exp_log as el
import resoudre_el

mp = mpmath.mp
FILIERES = ("C", "M")
LIGNE = re.compile(r'<span class="expr">\\\((.*?)\\\)</span>')
MESSAGE = re.compile(r"il faut les logarithmes", re.IGNORECASE)


def lignes(entree, filiere, cle):
    """Les expressions TeX de la variante `cle` (sans \\( \\)), cartes finales comprises, et les phrases ; dans l'ordre."""
    s = resoudre_el.resoudre(entree, filiere)
    assert s["ok"], s
    variante = next(v for v in s["variantes"] if v["cle"] == cle)
    out = []
    for carte in variante["cartes"]:
        for b in carte["blocs"]:
            if b["type"] == "texte":
                out += LIGNE.findall(b["html"]) or [b["html"]]
            elif "tex" in b:
                out.append(b["tex"])
    return out


def solutions(entree, filiere, cle):
    s = el.analyser_saisie(entree, filiere)
    r = el.variantes_equation(s.g, s.d, s.inconnue, s.parametres)[cle]
    return sorted(el.valeur(n) for n in r["solutions"])


def membres_ed(entree):
    """(g, d) lus par l'outil ED (la virgule décimale devient un point)."""
    g, d = entree.replace(",", ".").split("=")
    return ed.lire(g), ed.lire(d)


def _racines(expressions):
    """Racines attendues en mpf : chaque entier de l'écriture devient un mpf (2/9 n'est jamais un flottant)."""
    return sorted(eval(re.sub(r"\d+", lambda m: f"mpf({m.group()})", e), {"sqrt": mp.sqrt, "mpf": mp.mpf}) for e in expressions)


# entrée, racines exactes, lignes attendues de la méthode « Même base / définition »
CAS_Q6 = [
    ("2^(x^2-5x)=2^(-1/2)", ["(5-sqrt(23))/2", "(5+sqrt(23))/2"],
     [r"x^{2} - 5x = -\frac{1}{2}", r"x^{2} - 5x + \frac{1}{2} = 0", r"Δ = (-5)^{2} - 4 \cdot 1 \cdot \frac{1}{2} = 23",
      r"x_{1} = \frac{5 - \sqrt{23}}{2}", r"x_{2} = \frac{5 + \sqrt{23}}{2}"]),
    ("2^(x^2-x)=2^(-1/4)", ["1/2"], [r"x^{2} - x + \frac{1}{4} = 0", r"S = \left\{\frac{1}{2}\right\}"]),
    ("2^(x^2-x)=2^(0,5)", ["(1-sqrt(3))/2", "(1+sqrt(3))/2"],
     [r"x^{2} - x = 0{,}5", r"x^{2} - x - 0{,}5 = 0", r"Δ = (-1)^{2} - 4 \cdot 1 \cdot (-0{,}5) = 3"]),
    ("2^(x^2-x)=2^(-2/9)", ["1/3", "2/3"], [r"S = \left\{\frac{1}{3} \,;\, \frac{2}{3}\right\}"]),
    ("2^(x^2-5x)=2^(-6,5)", [], [r"x^{2} - 5x + 6{,}5 = 0", r"S = \varnothing"]),
    ("2^(x^2-1)=2^(1/2)", ["-sqrt(3/2)", "sqrt(3/2)"], [r"x^{2} = \frac{3}{2}", r"x_{2} = \sqrt{\frac{3}{2}}"]),
    ("2^(x^2)=2^(-1/2)", [], [r"x^{2} = -\frac{1}{2}", r"S = \varnothing"]),
    ("3^(2x^2-5x)=3^(3/2)", ["(5-sqrt(37))/4", "(5+sqrt(37))/4"], [r"2x^{2} - 5x - \frac{3}{2} = 0"]),
    ("e^(x^2-5x)=e^(-1/2)", ["(5-sqrt(23))/2", "(5+sqrt(23))/2"], [r"x^{2} - 5x + \frac{1}{2} = 0"]),
    ("10^(x^2-5x)=10^(-1/2)", ["(5-sqrt(23))/2", "(5+sqrt(23))/2"], [r"x^{2} - 5x + \frac{1}{2} = 0"]),
    ("2^(x^2)=2^(x+1/2)", ["(1-sqrt(3))/2", "(1+sqrt(3))/2"], [r"x^{2} = x + \frac{1}{2}", r"x^{2} - x = \frac{1}{2}", r"x^{2} - x - \frac{1}{2} = 0"]),
    ("2^(x^2-5x)*2^(1/2)=1", ["(5-sqrt(23))/2", "(5+sqrt(23))/2"], [r"2^{x^{2} - 5x + \frac{1}{2}} = 2^{0}", r"x^{2} - 5x + \frac{1}{2} = 0"]),
    ("4^(x^2-x)=8^(-1/2)", [], [r"2x^{2} - 2x + \frac{3}{2} = 0", r"S = \varnothing"]),
    ("9^(x^2)=3^(x+1/2)", ["(1-sqrt(5))/4", "(1+sqrt(5))/4"], [r"2x^{2} - x - \frac{1}{2} = 0"]),
    ("0,5^(x^2-x)=0,5^(-1/4)", ["1/2"], [r"S = \left\{0{,}5\right\}"]),
]

# balayage : mêmes bases des deux côtés, exposants fractionnaires, décimaux ou négatifs, sept bases
VOISINES_Q6 = [f"{b}^({p})={b}^({k})" for b in ("2", "3", "10", "e", "0,5", "(1/2)", "4")
               for k in ("-1/2", "1/2", "-1/4", "-2/9", "0,5", "-6,5", "-6", "3/2", "-3")
               for p in ("x^2-5x", "x^2-x", "2x^2-5x", "x^2", "-x^2+5x", "x^2-1")]
VOISINES_Q6 += [f"{b}^(x^2)={b}^(x+1/2)" for b in ("2", "3", "e")] + ["4^(x^2-5x)=2^(-1)", "8^(x^2)=2^(x+1)", "4^(x^2-x)=8^(-1/2)",
                                                                      "9^(x^2)=3^(x+1/2)", "2^(x^2-x/2)=2^(1)", "2^(x^2/2-x)=2^(-1/2)"]


class TestQ6MemeBase(unittest.TestCase):
    def test_redaction(self):
        for entree, _, attendues in CAS_Q6:
            for filiere in FILIERES:
                with self.subTest(entree=entree, filiere=filiere):
                    texte = lignes(entree, filiere, el.METHODE_MEME_BASE)
                    self.assertFalse([t for t in texte if MESSAGE.search(t)], texte)
                    for ligne in attendues:
                        self.assertIn(ligne, texte)

    def test_oracle(self):
        for entree, attendues, _ in CAS_Q6:
            G, D = membres_ed(entree)
            h = lambda x: oracle.valeur(G, x) - oracle.valeur(D, x)
            racines = _racines(attendues)
            with self.subTest(entree=entree, controle="racines exactes"):
                for r in racines:
                    self.assertLess(abs(h(r)), mp.mpf("1e-40"), f"h({r}) ≠ 0")
            with self.subTest(entree=entree, controle="aucune autre racine"):
                grille = [mp.mpf(k) / 64 for k in range(-20 * 64, 20 * 64 + 1)]
                changements = [a for a, b in zip(grille, grille[1:]) if h(a) * h(b) < 0]
                for a in changements:
                    self.assertTrue(any(a - mp.mpf(1) / 64 <= r <= a + mp.mpf(1) / 64 for r in racines), f"racine près de {a}")
                simples = [r for r in racines if not any(abs(r - s) < mp.mpf("1e-30") for s in racines if s is not r)]
                self.assertLessEqual(len(changements), len(simples))
            for filiere in FILIERES:
                with self.subTest(entree=entree, filiere=filiere, controle="solutions de l'outil"):
                    outil = solutions(entree, filiere, el.METHODE_MEME_BASE)
                    self.assertEqual(len(outil), len(racines))
                    for v, r in zip(outil, racines):
                        self.assertAlmostEqual(v, float(r), places=12)

    def test_balayage(self):
        """Même base des deux côtés : la méthode A ne renvoie jamais aux logarithmes ; ses solutions sont celles de la méthode B et
        annulent g − d (oracle)."""
        for entree in VOISINES_Q6:
            G, D = membres_ed(entree)
            for filiere in FILIERES:
                with self.subTest(entree=entree, filiere=filiere):
                    texte = lignes(entree, filiere, el.METHODE_MEME_BASE)
                    self.assertFalse([t for t in texte if MESSAGE.search(t)], texte)
                    a = solutions(entree, filiere, el.METHODE_MEME_BASE)
                    b = solutions(entree, filiere, el.METHODE_LOGARITHMES)
                    self.assertEqual(len(a), len(b))
                    for u, v in zip(a, b):
                        self.assertAlmostEqual(u, v, places=12)
                    for u in a:
                        x = mp.mpf(u)
                        self.assertLess(abs(oracle.valeur(G, x) - oracle.valeur(D, x)), mp.mpf("1e-9") * (1 + abs(oracle.valeur(D, x))))


if __name__ == "__main__":
    unittest.main()
