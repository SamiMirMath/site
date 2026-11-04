"""Correctif Exp-log (chantier correctif-explog-delta, audit equations-2e-degre § 0.4) : méthode « Logarithmes », a^P = a^k
avec le même a, P du 1er ou du 2e degré et k un nombre écrit en exposant (2^(x² − 5x) = 2^(−6)).

Avant : « x² − 5x − (−6) = 0 », « Δ = (−5)² − 4·1·(−−6) = 25 + 4(−6) », S = {x₁ ; x₂} ; « x = 5 − 6 » au 1er degré ;
« x² = 1 + 1/2 » ; Δ = 1 + 4 · 0,5 non calculé. Après : le second membre est le nombre k, la suite est celle d'un trinôme
à coefficients rationnels (x² − 5x + 6 = 0, puis la factorisation ou Δ = b² − 4ac = valeur), dans les filières C et M.

Les solutions sont confirmées par l'oracle (tests/python/oracle.py, mpmath 50 chiffres, arbre de l'outil ED, indépendant
d'Exp-log) : chaque racine attendue annule g − d, il n'y en a pas d'autre (changements de signe sur une grille), et les
solutions de l'outil sont ces racines.

Reste volontairement inchangé (spécification, exemples 10 et 11, décision du 27.10.2026) : 2^(x² − 5x) = 1/64 garde
log(1/64)/log(2) (« log(32) reste log(32) ») et le contrôle à la calculatrice ; la variante par défaut reste « Logarithmes »."""
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
LIGNE = re.compile(r'<span class="lien">(.*?)</span><span class="expr">\\\((.*?)\\\)</span>')


def lignes(entree, filiere, cle=el.METHODE_LOGARITHMES):
    """Les expressions TeX (sans \\( \\)) de la variante `cle`, cartes finales comprises, dans l'ordre."""
    s = resoudre_el.resoudre(entree, filiere)
    assert s["ok"], s
    variante = next(v for v in s["variantes"] if v["cle"] == cle)
    out = []
    for carte in variante["cartes"]:
        for b in carte["blocs"]:
            if b["type"] == "texte":
                out += [e for _, e in LIGNE.findall(b["html"])] or [b["html"]]
            elif b["type"] == "resultat":
                out.append(b["tex"])
    return out


def solutions_outil(entree, filiere):
    s = el.analyser_saisie(entree, filiere)
    r = el.variantes_equation(s.g, s.d, s.inconnue, s.parametres)[el.METHODE_LOGARITHMES]
    return sorted(el.valeur(n) for n in r["solutions"])


# entrée, (g, d) pour l'oracle (arbre de l'outil ED), racines exactes attendues, lignes attendues (variante « Logarithmes »)
CAS = [
    ("2^(x^2-5x)=2^(-6)", ("2^(x^2-5x)", "2^(-6)"), ["2", "3"],
     [r"x^{2} - 5x = -6", r"x^{2} - 5x + 6 = 0", r"(x - 2)(x - 3) = 0", r"x = 2 \text{ ou } x = 3", r"S = \left\{2 \,;\, 3\right\}"]),
    ("2^(-6)=2^(x^2-5x)", ("2^(-6)", "2^(x^2-5x)"), ["2", "3"],
     [r"x^{2} - 5x + 6 = 0", r"S = \left\{2 \,;\, 3\right\}"]),
    ("2^(x^2+5x)=2^(-6)", ("2^(x^2+5x)", "2^(-6)"), ["-3", "-2"],
     [r"x^{2} + 5x + 6 = 0", r"(x + 3)(x + 2) = 0", r"S = \left\{-3 \,;\, -2\right\}"]),
    ("10^(x^2-5x)=10^(-6)", ("10^(x^2-5x)", "10^(-6)"), ["2", "3"],
     [r"x^{2} - 5x + 6 = 0", r"S = \left\{2 \,;\, 3\right\}"]),
    ("e^(x^2-5x)=e^(-6)", ("e^(x^2-5x)", "e^(-6)"), ["2", "3"],
     [r"x^{2} - 5x + 6 = 0", r"S = \left\{2 \,;\, 3\right\}"]),
    ("0,5^(x^2-5x)=0,5^(-6)", ("0.5^(x^2-5x)", "0.5^(-6)"), ["2", "3"],
     [r"x^{2} - 5x + 6 = 0", r"S = \left\{2 \,;\, 3\right\}"]),
    ("2^(x-5)=2^(-6)", ("2^(x-5)", "2^(-6)"), ["-1"],
     [r"x - 5 = -6", r"x = -1", r"S = \left\{-1\right\}"]),
    ("2^(x^2-1)=2^(1/2)", ("2^(x^2-1)", "2^(1/2)"), ["-sqrt(3/2)", "sqrt(3/2)"],
     [r"x^{2} - 1 = \frac{1}{2}", r"x^{2} = \frac{3}{2}", r"x_{1} = -\sqrt{\frac{3}{2}}", r"x_{2} = \sqrt{\frac{3}{2}}"]),
    ("2^(x^2-x)=2^(-1/4)", ("2^(x^2-x)", "2^(-1/4)"), ["1/2"],
     [r"x^{2} - x + \frac{1}{4} = 0", r"Δ = (-1)^{2} - 4 \cdot 1 \cdot \frac{1}{4} = 0", r"S = \left\{\frac{1}{2}\right\}"]),
    ("2^(x^2-x)=2^(-2/9)", ("2^(x^2-x)", "2^(-2/9)"), ["1/3", "2/3"],
     [r"x^{2} - x + \frac{2}{9} = 0", r"Δ = (-1)^{2} - 4 \cdot 1 \cdot \frac{2}{9} = \frac{1}{9}",
      r"x = \frac{1}{3} \text{ ou } x = \frac{2}{3}", r"S = \left\{\frac{1}{3} \,;\, \frac{2}{3}\right\}"]),
    ("2^(x^2-x)=2^(0,5)", ("2^(x^2-x)", "2^(1/2)"), ["(1-sqrt(3))/2", "(1+sqrt(3))/2"],
     [r"x^{2} - x - 0{,}5 = 0", r"Δ = (-1)^{2} - 4 \cdot 1 \cdot (-0{,}5) = 3", r"x_{1} = \frac{1 - \sqrt{3}}{2}", r"x_{2} = \frac{1 + \sqrt{3}}{2}"]),
    ("2^(x^2)=2^(-6)", ("2^(x^2)", "2^(-6)"), [],
     [r"x^{2} = -6", r"S = \varnothing"]),
]

# double signe, opposé d'un négatif écrit tel quel, calcul laissé en suspens : jamais dans ces corrigés
INTERDITS = [re.compile(p) for p in (r"--", r"- \(-", r"- \\left\(-", r"\+ 4\(-", r"\+ 4 \\cdot \d", r"x = \d+ - \d+\b",
                                     r"x\^\{2\} = \d+ \+ ", r"\\sqrt\{Δ\}", r"x_\{1\} \\,;\\, x_\{2\}\\right\\\}$")]


def _racines(expressions):
    """Les racines attendues en mpf (50 chiffres) : chaque entier de l'écriture devient un mpf, 2/9 n'est jamais un flottant."""
    return sorted(eval(re.sub(r"\d+", lambda m: f"mpf({m.group()})", e), {"sqrt": mp.sqrt, "mpf": mp.mpf}) for e in expressions)


class TestCorrectifExplogDelta(unittest.TestCase):
    def test_redaction(self):
        for entree, _, _, attendues in CAS:
            for filiere in FILIERES:
                with self.subTest(entree=entree, filiere=filiere):
                    texte = lignes(entree, filiere)
                    for ligne in attendues:
                        self.assertIn(ligne, texte)
                    for ligne in texte:
                        for motif in INTERDITS:
                            self.assertIsNone(motif.search(ligne), f"{motif.pattern!r} dans {ligne!r}")

    def test_oracle(self):
        for entree, (g, d), attendues, _ in CAS:
            G, D = ed.lire(g), ed.lire(d)
            h = lambda x: oracle.valeur(G, x) - oracle.valeur(D, x)
            racines = _racines(attendues)
            with self.subTest(entree=entree, controle="racines exactes"):
                for r in racines:
                    self.assertLess(abs(h(r)), mp.mpf("1e-40"), f"h({r}) ≠ 0")
            with self.subTest(entree=entree, controle="aucune autre racine"):
                grille = [mp.mpf(k) / 64 for k in range(-20 * 64, 20 * 64 + 1)]
                changements = [a for a, b in zip(grille, grille[1:]) if h(a) * h(b) < 0]
                simples = [r for r in racines if not any(abs(r - s) < mp.mpf("1e-30") for s in racines if s is not r)]
                for a in changements:
                    self.assertTrue(any(a - mp.mpf(1) / 64 <= r <= a + mp.mpf(1) / 64 for r in racines), f"racine près de {a}")
                self.assertLessEqual(len(changements), len(simples))
            for filiere in FILIERES:
                with self.subTest(entree=entree, filiere=filiere, controle="solutions de l'outil"):
                    outil = solutions_outil(entree, filiere)
                    self.assertEqual(len(outil), len(racines))
                    for v, r in zip(outil, racines):
                        self.assertAlmostEqual(v, float(r), places=12)

    def test_un_soixante_quatrieme_inchange(self):
        """2^(x² − 5x) = 1/64 : log(1/64) reste écrit (spécification : « log(32) reste log(32) »), contrôle à la calculatrice."""
        for filiere in FILIERES:
            with self.subTest(filiere=filiere):
                texte = lignes("2^(x^2-5x)=1/64", filiere)
                self.assertIn(r"x^{2} - 5x = \frac{\log\left(\frac{1}{64}\right)}{\log(2)}", texte)
                self.assertTrue(any("on retrouve" in t and r"\(x = 2\) ou \(x = 3\)" in t for t in texte), texte)

    def test_variante_par_defaut_inchangee(self):
        """La variante par défaut d'une équation exponentielle reste « Logarithmes » (décision du 27.10.2026), même quand
        « Même base » s'applique (2^(x² − 5x) = 2^(−6), 3^(x²) = 3^(x + 6))."""
        for entree in ("2^(x^2-5x)=2^(-6)", "3^(x^2)=3^(x+6)", "2^(x^2-5x)=1/64"):
            for filiere in FILIERES:
                with self.subTest(entree=entree, filiere=filiere):
                    s = resoudre_el.resoudre(entree, filiere)
                    self.assertEqual(s["variante_defaut"], el.METHODE_LOGARITHMES)
                    self.assertIn(r"S = \left\{2 \,;\, 3\right\}" if "5x" in entree else r"S = \left\{-2 \,;\, 3\right\}",
                                  lignes(entree, filiere, el.METHODE_MEME_BASE))


if __name__ == "__main__":
    unittest.main()
