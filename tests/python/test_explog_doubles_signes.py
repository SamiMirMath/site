"""Chantier explog-suite, points 1 et 2 (question 8 de la fiche du Mac, correctif-explog-delta) : jamais deux signes de suite dans un corrigé
d'Exp-log.

Avant : la carte « Contrôle » de la 3C remplaçait x par une valeur négative dans −x et écrivait « log(--100) » (log(−x) = 2),
« log_{--2}(4) » (log_(−x)(4) = 2) et « −log(1/100) = --2 » (−log(x) = 2) ; une saisie « −(−x) » était récrite « --x » (filières C et M).
Cause : tex() (exp_log.py) ne mettait entre parenthèses que la somme sous un signe moins, jamais un opposé ni un nombre négatif.
Après : « log(−(−100)) = log(100) », « log_{−(−2)}(4) », « −log(1/100) = −(−2) = 2 », « −(−x) ».
Point 2 : une somme dont le second terme commence par un signe moins s'écrivait « −x + −x + 1 » (e^(−x)·e^((−x)+1) = 5) ; après,
« −x + (−x + 1) ». Le balayage du point 1 cherche depuis le point 2 tous les doubles signes (motif de test_doubles_signes.py).

Le balayage parcourt le corpus des deux filières (cas_el.py) et chacune de ses entrées où x est remplacé par (−x) : c'est là que les
opposés de négatifs apparaissent. La garde générale, pour tous les outils et tout le corpus enregistré, est test_doubles_signes.py."""
import re
import unittest

import mpmath

import moteurs  # noqa: F401  (chemins des moteurs)
from moteurs import ensemble_def as ed
import oracle
import resoudre_el
from cas_el import entrees_el, entrees_el_m
from test_doubles_signes import DOUBLE, morceaux_resoudre

mp = mpmath.mp
LIGNE = re.compile(r'<span class="expr">\\\((.*?)\\\)</span>')
X = re.compile(r"(?<![A-Za-z])x(?![A-Za-z])")

# entrée, solution contrôlée, ligne attendue dans la carte « Contrôle » (3C), g − d pour l'oracle (arbre de l'outil ED : log s'y écrit ln/ln(10))
CONTROLES = [
    ("log(-x)=2", "mpf(-100)", r"\log(-(-100)) = \log(100) = \log(10^{2}) = 2", "ln(-x)/ln(10) - 2"),
    ("log_(-x)(4)=2", "mpf(-2)", r"\log_{-(-2)}(4) = \log_{2}(4) = \log_{2}(2^{2}) = 2", "ln(4)/ln(-x) - 2"),
    ("-log(x)=2", "mpf(1) / 100", r"-\log\left(\frac{1}{100}\right) = -(-2)", "-ln(x)/ln(10) - 2"),
]


def _formules(o):
    """Les morceaux d'une sortie de resoudre, comme dans test_doubles_signes.py : chaque chaîne, et dans le HTML chaque formule et chaque texte
    entre deux balises."""
    if isinstance(o, str):
        yield from morceaux_resoudre(o)
    elif isinstance(o, dict):
        for v in o.values():
            yield from _formules(v)
    elif isinstance(o, list):
        for v in o:
            yield from _formules(v)


def _controle(entree):
    s = resoudre_el.resoudre(entree, "C")
    assert s["ok"], s
    carte = next(c for c in s["cartes"] if c.get("badge") == "Contrôle")
    return [e for b in carte["blocs"] if b["type"] == "texte" for e in LIGNE.findall(b["html"])]


class TestExplogDoublesSignes(unittest.TestCase):
    def test_controle_3c(self):
        for entree, _, attendue, _ in CONTROLES:
            with self.subTest(entree=entree):
                lignes = _controle(entree)
                self.assertIn(attendue, lignes)
                for ligne in lignes:
                    self.assertIsNone(DOUBLE.search(ligne), ligne)

    def test_controle_3c_oracle(self):
        """La solution contrôlée annule g − d (mpmath, 50 chiffres, arbre de l'outil ED)."""
        for entree, solution, _, h in CONTROLES:
            with self.subTest(entree=entree):
                self.assertLess(abs(oracle.valeur(ed.lire(h), eval(solution, {"mpf": mp.mpf}))), mp.mpf("1e-40"))

    def test_saisie_oppose_d_un_oppose(self):
        """−(−x) saisi reste −(−x) dans les deux filières (« --x » avant)."""
        for filiere, entree, attendue in (("M", "log(-(-x))=2", r"\log(-(-x)) = 2"), ("C", "2^(-(-x))=8", r"(-(-x)) \cdot \log(2) = \log(8)")):
            with self.subTest(filiere=filiere, entree=entree):
                self.assertIn(attendue, list(_formules(resoudre_el.resoudre(entree, filiere))))

    def test_somme_dont_le_second_terme_commence_par_moins(self):
        """Point 2 : « −x + (−x + 1) », jamais « −x + −x + 1 » (C et M)."""
        for filiere in ("C", "M"):
            with self.subTest(filiere=filiere):
                formules = list(_formules(resoudre_el.resoudre("e^(-x)*e^((-x)+1)=5", filiere)))
                self.assertIn(r"-x + (-x + 1) = \ln(5)", formules)

    def test_balayage_corpus_et_oppose(self):
        """Aucune formule ni aucun texte du corpus (C et M), ni de ses entrées où x devient (−x), n'a deux signes de suite."""
        for filiere, entrees in (("C", entrees_el()), ("M", entrees_el_m())):
            for entree in entrees + [X.sub("(-x)", e) for e in entrees if X.search(e)]:
                with self.subTest(filiere=filiere, entree=entree):
                    fautives = [f for f in _formules(resoudre_el.resoudre(entree, filiere)) if DOUBLE.search(f)]
                    self.assertEqual(fautives, [])


if __name__ == "__main__":
    unittest.main()
