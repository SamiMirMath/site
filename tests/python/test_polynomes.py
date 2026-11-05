"""Brique moteur/polynomes.py (chantier equations-2e-degre, P1 ; decisions.md § 13.2, Q2) : coefficients exacts d'un polynôme écrit
avec l'arbre de moteur/expr.py, déplacés d'Exp-log sans réécriture.

- Réexports : Exp-log garde ses anciens noms privés, qui sont les mêmes objets que ceux de la brique (`assertIs`, modèle
  `test_expr.TestReexportParExpLog`) ; les définitions ne restent pas dans Exp-log (déplacées, pas copiées) ; Exp-log ne prend dans
  la brique que des noms publics.
- Identité de `pq` sur le corpus d'Exp-log : sur chaque sous-arbre des saisies du corpus (3C et M), `exp_log_m._pq` est la fonction
  de la brique, et les coefficients qu'elle rend valent, en 10 points rationnels, la valeur exacte de l'arbre calculée par un
  évaluateur écrit ici (indépendant de la brique).
Le dump de toutes les sorties d'Exp-log, identique à l'octet avant et après le déplacement, est contrôlé en fin de partie
(tests/outils/dump_sorties.py, journal.md du chantier)."""
import os
import unittest
from fractions import Fraction as F
from math import isqrt

import moteurs  # noqa: F401  (chemins des moteurs)
from moteurs import RACINE

import cas_el
import exp_log as el
import exp_log_m as elm
import expr
import polynomes
import test_noyau
from noyau import ErreurSaisie

# (module, ancien nom, nom dans la brique)
DEPLACES = [
    (el, "_Hors", "Hors"), (el, "_racine_carree", "racine_carree"), (el, "_racine_entiere_exacte", "racine_entiere_exacte"),
    (el, "_puissance_rationnelle_exacte", "puissance_rationnelle_exacte"), (el, "_const", "const"), (el, "_pnet", "pnet"),
    (el, "_padd", "padd"),
    (elm, "DEGRE_MAX", "DEGRE_MAX"), (elm, "_pmul_n", "pmul_n"), (elm, "_pq", "pq"),
    # exp_log_m les prend d'exp_log (inchangé) : mêmes objets
    (elm, "_Hors", "Hors"), (elm, "_const", "const"), (elm, "_padd", "padd"), (elm, "_pnet", "pnet"),
    (elm, "_puissance_rationnelle_exacte", "puissance_rationnelle_exacte"), (elm, "_racine_carree", "racine_carree"),
]
FICHIERS_EL = ["exponentielles-logarithmes/exp_log.py", "exponentielles-logarithmes/exp_log_m.py"]


class TestReexports(unittest.TestCase):
    def test_memes_objets(self):
        for module, ancien, nouveau in DEPLACES:
            with self.subTest(f"{module.__name__}.{ancien}"):
                self.assertIs(getattr(module, ancien), getattr(polynomes, nouveau))

    def test_hors_reste_le_meme_objet(self):
        self.assertIs(el._Hors, elm._Hors)
        with self.assertRaises(el._Hors):
            polynomes.pq(expr.Pow(expr.Var("x"), expr.Nb(9)))
        with self.assertRaises(polynomes.Hors):
            elm._pq(expr.Fn("sqrt", expr.Nb(2)))

    def test_definitions_deplacees_pas_copiees(self):
        for chemin in FICHIERS_EL:
            with open(os.path.join(RACINE, chemin), encoding="utf-8") as f:
                source = f.read()
            for _, ancien, _ in DEPLACES:
                with self.subTest(chemin=chemin, nom=ancien):
                    self.assertNotIn(f"def {ancien}(", source)
                    self.assertNotIn(f"class {ancien}(", source)
                    self.assertNotIn(f"\n{ancien} = ", source)

    def test_exp_log_ne_prend_que_des_noms_publics(self):
        for chemin in FICHIERS_EL:
            for module, nom, _ in test_noyau.imports_de(chemin):
                if module == "polynomes":
                    with self.subTest(moteur=chemin, nom=nom):
                        self.assertFalse(nom.startswith("_"), f"{nom} est privé")
                        self.assertIn(nom, polynomes.__all__)

    def test_tout_est_exporte(self):
        for nom in polynomes.__all__:
            with self.subTest(nom):
                self.assertTrue(hasattr(polynomes, nom))


def evaluer(n, x):
    """Valeur exacte (Fraction) de l'arbre en x, écrite ici sans la brique ; None si elle n'est pas rationnelle ou pas définie."""
    if isinstance(n, expr.Nb):
        return n.val
    if isinstance(n, expr.Var):
        return x
    if isinstance(n, expr.Neg):
        a = evaluer(n.a, x)
        return None if a is None else -a
    if isinstance(n, expr.Op):
        a, b = evaluer(n.a, x), evaluer(n.b, x)
        if a is None or b is None or (n.op == "/" and b == 0):
            return None
        return {"+": lambda: a + b, "-": lambda: a - b, "*": lambda: a * b, "/": lambda: a / b}[n.op]()
    if isinstance(n, expr.Pow):
        a, b = evaluer(n.a, x), evaluer(n.b, x)
        if a is None or b is None or b.denominator != 1 or abs(b) > 64 or (a == 0 and b < 0):
            return None
        return a ** int(b)
    if isinstance(n, expr.Fn) and n.nom == "sqrt":
        a = evaluer(n.a, x)
        if a is None or a < 0:
            return None
        r, s = isqrt(a.numerator), isqrt(a.denominator)
        return F(r, s) if r * r == a.numerator and s * s == a.denominator else None
    return None


def sous_arbres(n):
    yield n
    if isinstance(n, expr.Defini):
        yield from sous_arbres(n.arbre)
        return
    for nom in getattr(type(n), "__slots__", ()):
        e = getattr(n, nom, None)
        if isinstance(e, expr.Noeud):
            yield from sous_arbres(e)


POINTS = [F(0), F(1), F(2), F(3), F(-1), F(-2), F(1, 2), F(-1, 3), F(5), F(7)]


class TestPqSurLeCorpusEl(unittest.TestCase):
    def test_pq_identique_sur_le_corpus(self):
        vus, polynomiaux = set(), 0
        for saisie in cas_el.entrees_el() + cas_el.entrees_el_m():
            try:
                membres = el.lire_membres(saisie)
            except ErreurSaisie:
                continue
            for membre in membres:
                if membre is None:
                    continue
                for n in sous_arbres(membre):
                    if n in vus or len(expr.variables(n)) > 1:
                        continue
                    vus.add(n)
                    try:
                        p = elm._pq(n)
                    except polynomes.Hors:
                        continue
                    polynomiaux += 1
                    self.assertLessEqual(len(p), polynomes.DEGRE_MAX + 1)
                    comparees = 0
                    for x in POINTS:
                        v = evaluer(n, x)
                        if v is None:
                            continue
                        comparees += 1
                        valeur = sum(c * x ** k for k, c in enumerate(p))
                        if valeur != v:
                            self.fail(f"{saisie} : pq({expr.tex(n)}) = {p} vaut {valeur} en {x}, l'arbre {v}")
                    if expr.variables(n):
                        self.assertGreaterEqual(comparees, len(p), f"{saisie} : {expr.tex(n)}")
        self.assertGreater(polynomiaux, 200)                 # 251 sous-arbres distincts au 05.11.2026


if __name__ == "__main__":
    unittest.main()
