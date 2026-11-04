"""Correctif Exp-log Δ (04.11.2026) — a^P(x) = constante, P du 2e degré, méthode « Logarithmes » (variante par défaut), filières C et M.

Avant : `2^(x^2-5x)=2^(-6)` écrivait « x² − 5x − (−6) = 0 » puis « Δ = (−5)² − 4·1·(−−6) = 25 + 4(−6) », et `2^(x^2-5x)=1/64` gardait Δ avec des
logarithmes (log(1/64)/log(2) = −6 n'était pas calculé). Le second membre écrit −6 (Neg(6)) n'était pas reconnu comme un nombre.

Après :
- un second membre rationnel est calculé avant la suite : x² − 5x + 6 = 0, Δ = (−5)² − 4·1·6 = 1 (ou la factorisation), x − 5 = −6 ⇔ x = −1 ;
- au 2e degré, quand b = a^k exactement, la puissance est écrite dans le logarithme : log(1/64) = log(2⁻⁶) = −6 · log(2) (log(a^A) = A · log(a)), puis
  on divise par log(2) ; jamais log_a(a^k) = k ni le changement de base en méthode B (EL-20) ;
- sinon Δ s'écrit avec les logarithmes, sans double signe (« 25 − 4 · log(3)/log(2) », jamais « 25 + (−4) · … » ni « − (−3/log 2) »).

Valeurs : l'oracle mpmath indépendant (tests/python/oracle.py, arbre lu par l'outil ED), jamais le moteur. Rédaction : textes exacts de la sortie."""
import re
import unittest
from fractions import Fraction as F

import mpmath

import moteurs  # noqa: F401  (chemins des moteurs)
from moteurs import ensemble_def as ed
import oracle
import exp_log as el
import resoudre_el as rel
from cas_el import BATTERIE_DELTA, DELTA_PAS_ENCORE
from test_exp_log_m import evaluer

MP = mpmath.mp
DOUBLE_SIGNE = re.compile(r"--|\(--|\+ \(-|- \(-|\+ -")


_MEMBRES = {}


def membres(saisie):
    """Les deux membres lus par l'outil ED (arbres de l'oracle), jamais par le parseur d'Exp-log."""
    if saisie not in _MEMBRES:
        g, d = saisie.split("=")
        _MEMBRES[saisie] = (ed.lire(g), ed.lire(d))
    return _MEMBRES[saisie]


def ecart(saisie, x):
    """g(x) − d(x) par l'oracle (mpmath, 50 chiffres) ; None hors du domaine."""
    g, d = membres(saisie)
    a, b = oracle.valeur(g, x), oracle.valeur(d, x)
    return None if a is None or b is None else a - b


def racines_oracle(saisie):
    """Les racines simples de g = d sur [−20 ; 20] : changements de signe de g − d (oracle), puis bissection."""
    pas, depart = MP.mpf(1) / 50, MP.mpf(-20) + MP.mpf("0.000713")
    trouvees = []
    a, fa = depart, ecart(saisie, depart)
    for i in range(1, 2001):
        b = depart + i * pas
        fb = ecart(saisie, b)
        if fa is not None and fb is not None and fa * fb < 0:
            lo, hi, flo = a, b, fa
            for _ in range(160):
                mid = (lo + hi) / 2
                fm = ecart(saisie, mid)
                if flo * fm <= 0:
                    hi = mid
                else:
                    lo, flo = mid, fm
            trouvees.append((lo + hi) / 2)
        a, fa = b, fb
    return trouvees


def variantes(saisie):
    s = el.analyser_saisie(saisie)
    return s, el.variantes_equation(s.g, s.d, s.inconnue, s.parametres)


def textes(sortie):
    return [b.get("html") or b.get("tex") or "" for v in sortie["variantes"] for c in v["cartes"] for b in c["blocs"]]


def textes_variante(sortie, cle):
    v = next(v for v in sortie["variantes"] if v["cle"] == cle)
    return [b.get("html") or b.get("tex") or "" for c in v["cartes"] for b in c["blocs"]]


def lignes_tex(saisie, methode=el.METHODE_LOGARITHMES):
    """Les lignes TeX (rangées « lien expression (propriété) ») de la méthode, carte par carte."""
    _, r = variantes(saisie)
    return [(lien, expr, prop) for carte in r[methode]["etapes"] for ligne in carte["lignes"] if isinstance(ligne, el.Chaine)
            for lien, expr, prop in el.rangees_chaine(ligne)]


def proche(a, b, tol=MP.mpf("1e-25")):
    return abs(a - b) <= tol * (1 + abs(a) + abs(b))


class TestOracle(unittest.TestCase):
    """Chaque solution annoncée (deux méthodes) annule g − d (oracle), vaut la solution attendue, et aucune racine simple n'est perdue."""

    def test_les_solutions_sont_celles_de_l_oracle(self):
        for saisie, attendu in BATTERIE_DELTA:
            with self.subTest(saisie):
                _, r = variantes(saisie)
                self.assertIsNotNone(r, saisie)
                trouvees = racines_oracle(saisie)
                for m in el.METHODES:
                    if r[m].get("message"):                    # « même base » qui ne s'applique pas (2^(−1/2)) : pas de solution affichée
                        self.assertEqual(m, el.METHODE_MEME_BASE, saisie)
                        continue
                    sols = sorted(evaluer(n, 0) for n in r[m]["solutions"])       # valeur exacte du TeX (x₁ = (5 − √Δ)/2), 30 chiffres
                    self.assertEqual(len(sols), len(attendu), (saisie, m))
                    for v, a in zip(sols, attendu):
                        e = ecart(saisie, v)
                        self.assertIsNotNone(e, (saisie, m, v))
                        self.assertLess(abs(e), MP.mpf("1e-20"), (saisie, m, v))
                        if isinstance(a, F):
                            self.assertTrue(proche(v, MP.mpf(a.numerator) / a.denominator), (saisie, m, v, a))
                        else:
                            self.assertAlmostEqual(float(v), a, places=3, msg=(saisie, m))
                    for t in trouvees:                         # aucune racine simple perdue
                        self.assertTrue(any(abs(t - v) < MP.mpf("1e-20") for v in sols), (saisie, m, t))

    def test_toute_ligne_est_vraie_en_chaque_racine(self):
        """Chaque égalité des chaînes de la méthode « Logarithmes » (équations, écritures intermédiaires, Δ = formule = valeur) est vraie en chaque
        solution attendue : log₂(1/64) = log₂(2⁻⁶) = −6, Δ = (−5)² − 4·1·6 = 1 (évaluateur mpmath des tests, pas le moteur)."""
        verifiees = 0
        for saisie, attendu in BATTERIE_DELTA:
            _, r = variantes(saisie)
            for a in attendu:
                x = MP.mpf(a.numerator) / a.denominator if isinstance(a, F) else None
                if x is None:
                    continue
                for carte in r[el.METHODE_LOGARITHMES]["etapes"]:
                    for ligne in carte["lignes"]:
                        if not isinstance(ligne, el.Chaine):
                            continue
                        premier = ligne.elements[0]
                        if isinstance(premier, el.Eq) and not proche(evaluer(premier.g, x) or 0, evaluer(premier.d, x) or 1, MP.mpf("1e-12")):
                            continue                           # une branche d'un produit nul (x·log 2 − 5 log 2 = 0) : elle concerne une autre racine
                        precedent = None
                        for e, lien in zip(ligne.elements, [None] + ligne.liens):
                            if isinstance(e, el.Eq):
                                valeurs = [evaluer(t, x) for t in [e.g] + e.milieu + [e.d]]
                            elif isinstance(e, (el.Ou, el.Texte, el.Rel, el.Positif)) or (isinstance(e, el.Var) and e.nom != "x"):
                                precedent = None               # « Δ » écrit Var("Δ") dans la ligne du discriminant entier : son nom, pas sa valeur
                                continue
                            else:
                                valeurs = [evaluer(e, x)]
                                if lien == "=" and precedent is not None:
                                    valeurs = [precedent] + valeurs
                            with self.subTest(saisie=saisie, x=a, ligne=el.tex_element(e)):
                                self.assertNotIn(None, valeurs)
                                for v in valeurs[1:]:
                                    self.assertTrue(proche(valeurs[0], v, MP.mpf("1e-12")))
                                    verifiees += 1
                            precedent = valeurs[-1]
        self.assertGreater(verifiees, 300)


class TestFilieres(unittest.TestCase):
    def test_la_meme_sortie_en_c_et_en_m(self):
        """Les équations exponentielles de la famille ont la même sortie en 3C et en 2Ms/2Mr (même moteur, `variantes_equation`), méthode
        « Logarithmes » par défaut."""
        for saisie, _ in BATTERIE_DELTA:
            with self.subTest(saisie):
                c, m = rel.resoudre(saisie, "C"), rel.resoudre(saisie, "M")
                self.assertTrue(c["ok"], c)
                self.assertEqual(c, m)
                self.assertEqual(c["variante_defaut"], el.METHODE_LOGARITHMES)

    def test_pas_encore_reste_un_message(self):
        for saisie in DELTA_PAS_ENCORE:
            for f in ("C", "M"):
                with self.subTest(saisie=saisie, filiere=f):
                    self.assertEqual(rel.resoudre(saisie, f), {"ok": False, "erreur": el.MESSAGE_PAS_ENCORE})


class TestRedaction(unittest.TestCase):
    def test_aucun_double_signe(self):
        for saisie, _ in BATTERIE_DELTA:
            for f in ("C", "M"):
                with self.subTest(saisie=saisie, filiere=f):
                    for t in textes(rel.resoudre(saisie, f)):
                        self.assertIsNone(DOUBLE_SIGNE.search(t), (saisie, t))

    def test_le_constat_de_l_audit(self):
        """`2^(x^2-5x)=2^(-6)` : x² − 5x + 6 = 0, puis la factorisation (comme la méthode « même base ») ; S = {2 ; 3} sans x₁ ni contrôle."""
        lignes = lignes_tex("2^(x^2-5x)=2^(-6)")
        self.assertIn((r"\iff", "x^{2} - 5x = -6", r"(car \(\log(2) \neq 0\))"), lignes)
        self.assertIn((r"\iff", "x^{2} - 5x + 6 = 0", None), lignes)
        self.assertIn((r"\iff", "(x - 2)(x - 3) = 0", None), lignes)
        sortie = rel.resoudre("2^(x^2-5x)=2^(-6)")
        logs = " ".join(textes_variante(sortie, el.METHODE_LOGARITHMES))
        self.assertIn(r"S = \left\{2 \,;\, 3\right\}", logs)
        self.assertNotIn("x_{1}", logs)
        self.assertNotIn("Contrôlez", logs)

    def test_un_soixante_quatrieme_le_logarithme_est_calcule(self):
        """1/64 = 2⁻⁶ est écrit dans le logarithme pour que log(a^A) = A · log(a) s'applique (comme log(100) = log(10²) = 2 · log(10)) : la méthode B
        n'utilise ni log_a(a^k) = k, ni le changement de base (EL-20)."""
        lignes = lignes_tex("2^(x^2-5x)=1/64")
        self.assertIn((r"\iff", r"(x^{2} - 5x) \cdot \log(2) = \log\left(\frac{1}{64}\right)", "(log(a^A) = A · log(a))"), lignes)
        self.assertIn((r"\iff", r"(x^{2} - 5x) \cdot \log(2) = \log(2^{-6}) = -6\log(2)", "(log(a^A) = A · log(a))"), lignes)
        self.assertIn((r"\iff", "x^{2} - 5x = -6", r"(car \(\log(2) \neq 0\))"), lignes)
        self.assertIn((r"\iff", "x^{2} - 5x + 6 = 0", None), lignes)
        self.assertNotIn("Δ", " ".join(e for _, e, _ in lignes))
        self.assertNotIn(r"\frac{\log\left(\frac{1}{64}\right)}{\log(2)}", " ".join(e for _, e, _ in lignes))

    def test_methode_b_sans_propriete_de_la_methode_a(self):
        """EL-20 sur toute la famille : ni « définition du logarithme », ni log(10ᵏ) = k, ni log_a(a^k) = k, ni ln(e^k) = k, ni changement de base."""
        interdites = {el.PROP_DEFINITION_LOG, el.PROP_LOG_10K, el.PROP_LN_E_PUISSANCE, el.PROP_LOG_BASE_PUISSANCE, el.PROP_CHANGEMENT_DE_BASE}
        for saisie, _ in BATTERIE_DELTA:
            with self.subTest(saisie):
                _, r = variantes(saisie)
                for carte in r[el.METHODE_LOGARITHMES]["etapes"]:
                    for ligne in carte["lignes"]:
                        if isinstance(ligne, el.Chaine):
                            self.assertFalse(interdites & {p for p in ligne.props if isinstance(p, str)}, (saisie, ligne.props))

    def test_delta_ecrit_comme_d_habitude(self):
        """a ≠ 1 : le discriminant entier, calculé (même ligne que la méthode « même base »)."""
        for saisie in ("2^(2x^2-5x)=2^(-3)", "2^(2x^2-5x)=1/8"):
            with self.subTest(saisie):
                exprs = [e for _, e, _ in lignes_tex(saisie)]
                self.assertIn("2x^{2} - 5x + 3 = 0", exprs)
                self.assertIn(r"Δ = (-5)^{2} - 4 \cdot 2 \cdot 3 = 1", exprs)

    def test_delta_rationnel_non_entier_calcule(self):
        attendus = {
            "2^(x^2-5x)=2^(3/2)": [r"x^{2} - 5x - \frac{3}{2} = 0", r"Δ = (-5)^{2} - 4 \cdot 1 \cdot \left(-\frac{3}{2}\right) = 31"],
            "2^(x^2-5x)=2^(-1/2)": [r"x^{2} - 5x + \frac{1}{2} = 0", r"Δ = (-5)^{2} - 4 \cdot 1 \cdot \frac{1}{2} = 23"],
            "2^(x^2-5x)=2^(-25/4)": [r"Δ = (-5)^{2} - 4 \cdot 1 \cdot \frac{25}{4} = 0", r"Δ = 0 \text{ : une seule solution}"],
            "2^(x^2-5x)=2^(-6,5)": [r"x^{2} - 5x + 6{,}5 = 0", r"Δ = (-5)^{2} - 4 \cdot 1 \cdot 6{,}5 = -1"],
            "2^(x^2-5x+1)=2^(-6,5)": [r"x^{2} - 5x + 7{,}5 = 0", r"Δ = (-5)^{2} - 4 \cdot 1 \cdot 7{,}5 = -5"],
        }
        for saisie, lignes in attendus.items():
            with self.subTest(saisie):
                exprs = [e for _, e, _ in lignes_tex(saisie)]
                for ligne in lignes:
                    self.assertIn(ligne, exprs)

    def test_delta_avec_logarithmes_sans_double_signe(self):
        attendus = {
            "2^(x^2-5x)=3": r"Δ = (-5)^{2} - 4 \cdot 1 \cdot \left(-\frac{\log(3)}{\log(2)}\right) = 25 + 4 \cdot \frac{\log(3)}{\log(2)}",
            "2^(-x^2+5x)=3": r"Δ = 5^{2} - 4(-1) \cdot \left(-\frac{\log(3)}{\log(2)}\right) = 25 - 4 \cdot \frac{\log(3)}{\log(2)}",
            "2^(x^2-5x)=0,001": r"Δ = (-5)^{2} - 4 \cdot 1 \cdot \frac{3}{\log(2)} = 25 - 4 \cdot \frac{3}{\log(2)}",
        }
        for saisie, ligne in attendus.items():
            with self.subTest(saisie):
                exprs = [e for _, e, _ in lignes_tex(saisie)]
                self.assertIn(ligne, exprs)
        self.assertIn(r"x^{2} - 5x + \frac{3}{\log(2)} = 0", [e for _, e, _ in lignes_tex("2^(x^2-5x)=0,001")])

    def test_autres_bases_et_puissances(self):
        attendus = {
            "2^(x^2-5x)=4^3": [r"(x^{2} - 5x) \cdot \log(2) = \log(4^{3}) = \log(2^{6}) = 6\log(2)", "x^{2} - 5x = 6"],
            "4^(x^2-5x)=2^(-12)": [r"(x^{2} - 5x) \cdot \log(4) = \log(2^{-12}) = \log(4^{-6}) = -6\log(4)", "x^{2} - 5x = -6"],
            "(1/2)^(x^2-5x)=64": [r"(x^{2} - 5x) \cdot \log\left(\frac{1}{2}\right) = \log\left(\left(\frac{1}{2}\right)^{-6}\right) = -6\log\left(\frac{1}{2}\right)",
                                   "x^{2} - 5x = -6"],
            "2^(x^2-5x)=8^(1/3)": [r"(x^{2} - 5x) \cdot \log(2) = \log\left(8^{\frac{1}{3}}\right) = \log(2)", "x^{2} - 5x - 1 = 0"],
            "2^(x^2+x)=1/2": [r"(x^{2} + x) \cdot \log(2) = \log(2^{-1}) = -\log(2)", "x^{2} + x + 1 = 0"],
        }
        for saisie, lignes in attendus.items():
            with self.subTest(saisie):
                exprs = [e for _, e, _ in lignes_tex(saisie)]
                for ligne in lignes:
                    self.assertIn(ligne, exprs)

    def test_base_10_et_autre_base_delta_avec_logarithmes(self):
        """10^(x² − 5x) = 1000⁻² : la méthode B ne calcule pas log(1000) (ce serait log(10ᵏ) = k) ; Δ reste écrit avec le logarithme, proprement."""
        exprs = [e for _, e, _ in lignes_tex("10^(x^2-5x)=1000^(-2)")]
        self.assertIn(r"x^{2} - 5x + 2\log(1\text{’}000) = 0", exprs)
        self.assertIn(r"Δ = (-5)^{2} - 4 \cdot 1 \cdot 2\log(1\text{’}000) = 25 - 4 \cdot 2\log(1\text{’}000)", exprs)

    def test_premier_degre_le_calcul_se_fait(self):
        """Même cause au 1er degré : x − 5 = −6 ⇔ x = −1 (avant : x = 5 − 6, S = {5 − 6})."""
        self.assertIn((r"\iff", "x = -1", None), lignes_tex("2^(x-5)=2^(-6)"))
        self.assertIn((r"\iff", "x = -2", None), lignes_tex("2^(2x+1)=2^(-3)"))
        logs = " ".join(textes_variante(rel.resoudre("2^(x-5)=2^(-6)"), el.METHODE_LOGARITHMES))
        self.assertIn(r"S = \left\{-1\right\}", logs)

    def test_le_premier_degre_ecrit_avec_log_garde_son_controle(self):
        """Hors du 2e degré, le corrigé 2.23 ne change pas : x = 5 + log(1/64)/log(2), puis le contrôle à la calculatrice."""
        logs = " ".join(textes_variante(rel.resoudre("2^(x-5)=1/64"), el.METHODE_LOGARITHMES))
        self.assertIn(r"S = \left\{5 + \frac{\log\left(\frac{1}{64}\right)}{\log(2)}\right\}", logs)
        self.assertIn("Contrôlez à la calculatrice", logs)


if __name__ == "__main__":
    unittest.main()
