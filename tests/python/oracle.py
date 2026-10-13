"""Oracle numérique indépendant des moteurs : évalue l'arbre d'une fonction en haute
précision (mpmath, 50 chiffres) avec ses propres règles de définition. Ni `evaluer`
(arrondi des compensations) ni SymPy ne sont utilisés.

Conventions (celles du cours, cf. docs/specifications/ensemble-definition.md) :
ln(u) : u > 0 ; √u : u ≥ 0 ; quotient : dénominateur ≠ 0 ;
u^(p/q) constant, q impair : défini sur ℝ (racine réelle) ; q pair : u ≥ 0 ;
exposant négatif : u ≠ 0 ; exposant non constant : u > 0 ; u^0 = 1 (y compris 0^0)."""
from fractions import Fraction as F

import mpmath

from moteurs import ensemble_def as ed

mp = mpmath.mp
mp.dps = 50


def _constante(n):
    v = ed.valeur_constante(n)
    if v is None:
        return None
    return F(v) if not isinstance(v, float) else F(0)


def valeur(n, x):
    """Valeur de l'arbre n en x (mpf) ; None si non définie."""
    x = mp.mpf(x)
    return _val(n, x)


def _val(n, x):
    if isinstance(n, ed.Nb):
        return mp.mpf(n.v.numerator) / n.v.denominator
    if isinstance(n, ed.X):
        return x
    if isinstance(n, ed.E):
        return mp.e
    if isinstance(n, ed.Neg):
        a = _val(n.a, x)
        return None if a is None else -a
    if isinstance(n, ed.Fn):
        a = _val(n.a, x)
        if a is None:
            return None
        if n.nom == "ln":
            return mp.log(a) if a > 0 else None
        if n.nom == "sqrt":
            return mp.sqrt(a) if a >= 0 else None
        return mp.exp(a)
    a = _val(n.a, x)
    if a is None:
        return None
    if n.op == "^":
        e = _constante(n.b)
        if e is None:
            b = _val(n.b, x)
            if b is None or a <= 0:
                return None
            return mp.exp(b * mp.log(a))
        if e == 0:
            return mp.mpf(1)
        if a == 0:
            return mp.mpf(0) if e > 0 else None
        if e.denominator == 1:
            return a ** int(e)
        if a < 0:
            if e.denominator % 2 == 0:
                return None
            r = (-a) ** (mp.mpf(e.numerator) / e.denominator)
            return -r if e.numerator % 2 else r
        return a ** (mp.mpf(e.numerator) / e.denominator)
    b = _val(n.b, x)
    if b is None:
        return None
    if n.op == "+":
        return a + b
    if n.op == "-":
        return a - b
    if n.op == "*":
        return a * b
    if b == 0:
        return None
    return a / b


def definie(n, x):
    return valeur(n, x) is not None


def derivee(n, x, h=mp.mpf("1e-20")):
    """f'(x) par différence centrée en haute précision (erreur ~ h², négligeable)."""
    a, b = valeur(n, mp.mpf(x) + h), valeur(n, mp.mpf(x) - h)
    if a is None or b is None:
        return None
    return (a - b) / (2 * h)
