"""
polynomes.py — Brique commune : coefficients exacts (Fraction) d'un polynôme écrit avec l'arbre de moteur/expr.py.

Déplacée sans réécriture d'Exp-log (chantier equations-2e-degre, P1 ; decisions.md § 13.2, Q2 ; règle A2 du 2e utilisateur : le
nouvel outil « Équations du 2e degré » lit ses polynômes comme la filière M d'Exp-log) :
    d'exponentielles-logarithmes/exp_log.py    : Hors, racine_carree, racine_entiere_exacte, puissance_rationnelle_exacte, const,
                                                 pnet, padd ;
    d'exponentielles-logarithmes/exp_log_m.py  : DEGRE_MAX, pmul_n, pq.
Exp-log les réexporte sous leurs anciens noms privés (`exp_log._Hors is polynomes.Hors`, `exp_log_m._pq is polynomes.pq`…) : ce sont
les mêmes objets, la sortie d'Exp-log est identique à l'octet (tests/python/test_polynomes.py).

Ordre des coefficients : croissant (p[k] est le coefficient de xᵏ). `pq` traite toute lettre (`Var`) comme l'inconnue : l'appelant
vérifie d'abord qu'il n'y en a qu'une.
"""
from fractions import Fraction as F
from math import isqrt

from expr import Nb, Var, Neg, Op, Pow, Fn, variables

__all__ = ["Hors", "racine_carree", "racine_entiere_exacte", "puissance_rationnelle_exacte", "const", "pnet", "padd", "DEGRE_MAX",
           "pmul_n", "pq"]


class Hors(Exception):
    """La forme sort de ce que la méthode sait traiter : la méthode ne s'applique pas (ce n'est pas une erreur de saisie)."""


def racine_carree(q):
    """Racine carrée exacte d'un rationnel ≥ 0, ou None."""
    a, b = isqrt(q.numerator), isqrt(q.denominator)
    return F(a, b) if a * a == q.numerator and b * b == q.denominator else None


def racine_entiere_exacte(n, q):
    """La racine q-ième entière exacte de l'entier n ≥ 0, ou None."""
    r = round(n ** (1 / q))
    return next((c for c in (r - 1, r, r + 1) if c >= 0 and c ** q == n), None)


def puissance_rationnelle_exacte(a, b):
    """a^b (a > 0 rationnel, b rationnel non entier) quand c'est un rationnel (8^(2/3) = 4, 9^(3/2) = 27, (1/4)^(1/2) = 1/2) ; None sinon."""
    if a <= 0 or b.denominator > 12:
        return None
    num, den = (racine_entiere_exacte(a.numerator, b.denominator), racine_entiere_exacte(a.denominator, b.denominator))
    if num is None or den is None or num == 0:
        return None
    return (F(num, den)) ** b.numerator


def const(n):
    """Valeur exacte (Fraction) d'un arbre sans inconnue, ou None si elle n'est pas rationnelle."""
    if isinstance(n, Nb):
        return n.val
    if isinstance(n, Neg):
        v = const(n.a)
        return None if v is None else -v
    if isinstance(n, Op):
        a, b = const(n.a), const(n.b)
        if a is None or b is None:
            return None
        if n.op == "+":
            return a + b
        if n.op == "-":
            return a - b
        if n.op == "*":
            return a * b
        return None if b == 0 else a / b
    if isinstance(n, Pow):
        a, b = const(n.a), const(n.b)
        if a is None or b is None or abs(b) > 64 or (a == 0 and b < 0):
            return None
        if b.denominator != 1:
            return puissance_rationnelle_exacte(a, b)
        return a ** int(b)
    if isinstance(n, Fn):
        a = const(n.a)
        return None if a is None or a < 0 else racine_carree(a)
    return None


# polynômes en l'inconnue : liste [c0, c1, c2, …] de Fractions
def pnet(p):
    p = list(p)
    while len(p) > 1 and p[-1] == 0:
        p.pop()
    return p


def padd(a, b, signe=1):
    n = max(len(a), len(b))
    return pnet([(a[i] if i < len(a) else 0) + signe * (b[i] if i < len(b) else 0) for i in range(n)])


DEGRE_MAX = 8


def pmul_n(a, b):
    r = [F(0)] * (len(a) + len(b) - 1)
    for i, u in enumerate(a):
        for j, v in enumerate(b):
            r[i + j] += u * v
    while len(r) > 1 and r[-1] == 0:
        r.pop()
    if len(r) > DEGRE_MAX + 1:
        raise Hors
    return r


def pq(n):
    """Coefficients de n, un polynôme en l'inconnue de degré quelconque (jusqu'à DEGRE_MAX) à coefficients rationnels ; sinon Hors."""
    if not variables(n):
        v = const(n)
        if v is None:
            raise Hors
        return [v]
    if isinstance(n, Var):
        return [F(0), F(1)]
    if isinstance(n, Neg):
        return [-c for c in pq(n.a)]
    if isinstance(n, Op):
        if n.op in "+-":
            return padd(pq(n.a), pq(n.b), 1 if n.op == "+" else -1)
        if n.op == "*":
            return pmul_n(pq(n.a), pq(n.b))
        d = const(n.b)
        if d is None or d == 0 or variables(n.b):
            raise Hors
        return [c / d for c in pq(n.a)]
    if isinstance(n, Pow):
        k = const(n.b)
        if k is None or k.denominator != 1 or not 0 <= k <= DEGRE_MAX:
            raise Hors
        r = [F(1)]
        for _ in range(int(k)):
            r = pmul_n(r, pq(n.a))
        return r
    raise Hors
