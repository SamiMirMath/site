"""
redaction_bh.py — Rédaction « descendante » des limites transcendantes (chantier 3M, refonte du 29.10.2026).

On part de la limite demandée et on descend en une seule suite d'étapes, comme dans le corrigé du chapitre 8
(docs/specifications/redaction-limites-3m.md) : on remplace, prédiction du podium, produit → quotient, BH
(tableau haut / bas avant la chaîne), simplification à part, on remplace, résultat.

`descente(f, pt, ref)` renvoie {"etapes": [...], "alertes": [...], "valeur": Lim} ou lève Abandon : l'appelant
(limites_asymptotes._narrer_limite) garde alors l'ancienne rédaction. Rien n'est affiché sans contrôle : chaque
égalité écrite est vérifiée numériquement, chaque dérivée aussi, la valeur finale est comparée à la valeur de
référence (SymPy + sonde mpmath), la prédiction du podium au résultat.
"""
from fractions import Fraction as F

import limites_asymptotes as LA
from noyau import Nb, X, E, Neg, Op, Fn, tex, valeur_constante, sans_x, evaluer, charger_sympy
import sortie as so

Abandon = LA.Abandon
Lim = LA.Lim

MAX_BH = 4
POINTS = [-9.3, -4.2, -2.6, -1.7, -0.8, -0.45, -0.2, 0.15, 0.35, 0.6, 0.85, 1.4, 2.3, 3.1, 5.7, 8.2]


# ---------------------------------------------------------------------------------------------------------------------
# Contrôles numériques (rien d'affiché sans contrôle)
# ---------------------------------------------------------------------------------------------------------------------
def _ev(n, x):
    try:
        return evaluer(n, x)
    except Exception:
        return None


def egaux(a, b):
    """Identité numérique de deux arbres sur les points d'échantillon où les deux sont définis (au moins deux)."""
    vus = 0
    for x in POINTS:
        va, vb = _ev(a, x), _ev(b, x)
        if va is None or vb is None:
            continue
        if abs(va - vb) > 1e-8 * max(1.0, abs(va), abs(vb)):
            return False
        vus += 1
    return vus >= 2


def derivee_ok(h, d):
    vus = 0
    for x in POINTS:
        v1, v0, dv = _ev(h, x + 1e-6), _ev(h, x - 1e-6), _ev(d, x)
        if v1 is None or v0 is None or dv is None:
            continue
        if abs((v1 - v0) / 2e-6 - dv) > 1e-4 * max(1.0, abs(dv)):
            return False
        vus += 1
    return vus >= 2


# ---------------------------------------------------------------------------------------------------------------------
# Monômes généralisés : coefficient · Π atome^k (atomes : x, e^u, ln u, sommes, racines…)
# ---------------------------------------------------------------------------------------------------------------------
class Mono:
    def __init__(self, coef=F(1), fact=None):
        self.coef = F(coef)
        self.fact = list(fact or [])          # [(arbre, exposant entier)]


def _fusion(a, b):
    fact = [(t, k) for t, k in a.fact]
    for t, k in b.fact:
        for i, (t2, k2) in enumerate(fact):
            if t2.key() == t.key():
                fact[i] = (t2, k2 + k)
                break
        else:
            fact.append((t, k))
    return Mono(a.coef * b.coef, [(t, k) for t, k in fact if k != 0])


def _inverse(m):
    if m.coef == 0:
        return None
    return Mono(1 / m.coef, [(t, -k) for t, k in m.fact])


def _puiss(m, k):
    return Mono(m.coef ** k, [(t, e * k) for t, e in m.fact])


def mono(n):
    v = valeur_constante(n)
    if v is not None:
        return Mono(v)
    if isinstance(n, Neg):
        m = mono(n.a)
        return None if m is None else Mono(-m.coef, m.fact)
    if isinstance(n, Op) and n.op in "*/":
        a, b = mono(n.a), mono(n.b)
        if a is None or b is None:
            return None
        if n.op == "/":
            b = _inverse(b)
            if b is None:
                return None
        return _fusion(a, b)
    if isinstance(n, Op) and n.op == "^":
        k = valeur_constante(n.b)
        if k is not None and k.denominator == 1 and abs(k) <= 64 and not sans_x(n.a):
            m = mono(n.a)
            return None if m is None else _puiss(m, int(k))
    return Mono(1, [(n, 1)])


def _rang(t):
    if sans_x(t):
        return 0
    if isinstance(t, X):
        return 1
    if isinstance(t, Fn) and t.nom == "exp":
        return 3
    if isinstance(t, Fn) and t.nom == "ln":
        return 4
    return 2


def _produit(liste):
    out = liste[0]
    for t in liste[1:]:
        out = Op("*", out, t)
    return out


def mono_arbre(m):
    """Arbre de m, écrit comme le corrigé : signe devant, puissances de x, exponentielles, puis le reste ; fraction si besoin."""
    haut, bas = [], []
    for t, k in sorted(m.fact, key=lambda f: _rang(f[0])):
        (haut if k > 0 else bas).append(t if abs(k) == 1 else Op("^", t, Nb(F(abs(k)))))
    p, q = abs(m.coef.numerator), m.coef.denominator
    if p != 1 or not haut:
        haut.insert(0, Nb(F(p)))
    if q != 1:
        bas.insert(0, Nb(F(q)))
    r = _produit(haut)
    if bas:
        r = Op("/", r, _produit(bas))
    return Neg(r) if m.coef < 0 else r


def est_zero_mono(m):
    return m.coef == 0


# ---------------------------------------------------------------------------------------------------------------------
# Limites par remplacement (sans lever les formes indéterminées)
# ---------------------------------------------------------------------------------------------------------------------
def lim(n, pt):
    """Lim de n en pt par simple remplacement ; FormeIndeterminee ou Abandon sinon."""
    if sans_x(n):
        return Lim.fin(LA._const_sympy(n), None)
    if isinstance(n, X):
        return pt.lim_x()
    if isinstance(n, Neg):
        return LA._oppose(lim(n.a, pt))
    if isinstance(n, Fn):
        U = lim(n.a, pt)
        if n.nom == "exp":
            return LA._exp_lim(U)
        if n.nom == "ln":
            return LA._ln_lim(U)
        return LA._puissance_reelle(U, F(1, 2))
    if isinstance(n, Op):
        if n.op == "^":
            k = valeur_constante(n.b)
            if k is None:
                raise Abandon("exposant non constant")
            U = lim(n.a, pt)
            if k.denominator == 1:
                if k in (0, 1) or abs(k) > 64:
                    raise Abandon("exposant 0, 1 ou trop grand")
                return LA._puissance_entiere(U, int(k))
            return LA._puissance_reelle(U, k)
        A, B = lim(n.a, pt), lim(n.b, pt)
        if n.op == "+":
            return LA._somme(A, B)
        if n.op == "-":
            return LA._somme(A, LA._oppose(B))
        if n.op == "*":
            return LA._produit(A, B)
        return LA._quotient(A, B)
    raise Abandon("sous-expression non prise en charge")


def forme(n, pt):
    """(nom, LA, LB) si n = A·B ou A/B est une forme indéterminée ; (None, LA, LB) sinon."""
    A, B = lim(n.a, pt), lim(n.b, pt)
    if n.op == "*":
        if (A.inf and B.nul()) or (B.inf and A.nul()):
            return "0·∞", A, B
    elif n.op == "/":
        if A.nul() and B.nul():
            return "0/0", A, B
        if A.inf and B.inf:
            return "∞/∞", A, B
    return None, A, B


def signe_lim(L):
    if L.inf:
        return L.inf
    if L.nul():
        return L.ap or 0
    return LA._signe(L.val)


# ---------------------------------------------------------------------------------------------------------------------
# Écriture
# ---------------------------------------------------------------------------------------------------------------------
def M(t):
    return "\\(" + t + "\\)"


def D(t):
    return "\\[" + t + "\\]"


def T(n):
    return tex(n)


def LT(L):
    return L.tex()


def LP(L):
    """Limite entre parenthèses dans un produit : (−∞)·0⁺."""
    t = L.tex()
    return "\\left(" + t + "\\right)" if t[:1] in "+-" else t


def IND(texte="indéterminée"):
    return f'<span class="ind">{texte}</span>'


def DET():
    return '<span class="det">pas indéterminée</span>'


def forme_tex(nom, A, B, op):
    """Écriture de la forme, comme le corrigé : (+∞)·0 ; 0·(−∞) ; \\frac{+∞}{+∞} ; \\frac{0^+}{0^+}."""
    if op == "*":
        if nom:                                    # indéterminée : le 0 s'écrit sans signe
            a = "0" if A.nul() else LP(A)
            b = "0" if B.nul() else LP(B)
            return f"{a} \\cdot {b}"
        return f"{LP(A)} \\cdot {LP(B)}"
    return f"\\dfrac{{{LT(A)}}}{{{LT(B)}}}"


def plain(n, pt):
    """« e^{2x} → +∞ » (une écriture simple, sans détail)."""
    return f"{T(n)} \\to {LT(lim(n, pt))}"


def detail(n, pt):
    """Fragment de remplacement d'une expression, avec les intermédiaires du corrigé ; "" si rien à dire (x, nombre)."""
    if isinstance(n, (X, Nb)) or sans_x(n):
        return ""
    L = lim(n, pt)
    if isinstance(n, Fn) and n.nom == "exp":
        u = n.a
        Lu = lim(u, pt)
        if isinstance(u, X):
            return f"{T(n)} \\to {LT(L)}" if Lu.inf > 0 else f"{T(n)} \\to e^{{{LT(Lu)}}} = {LT(L)}"
        return f"{T(u)} \\to {LT(Lu)}\\text{{, donc }}{T(n)} \\to {LT(L)}"
    if isinstance(n, Fn) and n.nom == "ln":
        u = n.a
        if isinstance(u, X):
            return f"{T(n)} \\to {LT(L)}"
        return f"{T(u)} \\to {LT(lim(u, pt))}\\text{{, donc }}{T(n)} \\to {LT(L)}"
    if isinstance(n, Op) and n.op == "^" and isinstance(n.a, X):
        return f"{T(n)} \\to \\left({LT(lim(n.a, pt))}\\right)^{{{T(n.b)}}} = {LT(L)}"
    if isinstance(n, Op) and n.op == "/" and not sans_x(n.a) is False and False:
        return ""
    if isinstance(n, Op) and n.op in "*/" and not sans_x(n.a) and not sans_x(n.b):
        A, B = lim(n.a, pt), lim(n.b, pt)
        if n.op == "/":
            return f"{T(n)} \\to \\dfrac{{{LT(A)}}}{{{LT(B)}}} = {LT(L)}"
        return f"{T(n)} \\to {LP(A)} \\cdot {LP(B)} = {LT(L)}"
    if isinstance(n, Op) and n.op == "/" and isinstance(n.a, Nb) and not sans_x(n.b):
        B = lim(n.b, pt)
        return f"{T(n)} \\to \\dfrac{{{LT(lim(n.a, pt))}}}{{{LT(B)}}} = {LT(L)}"
    return plain(n, pt)


def fragment(n, pt, premier_majuscule=False):
    d = detail(n, pt)
    return M(d) if d else ""


def cotes(n):
    """Facteurs « utiles » (non constants) d'un produit écrit."""
    if isinstance(n, Op) and n.op == "*":
        return cotes(n.a) + cotes(n.b)
    if isinstance(n, Neg):
        return cotes(n.a)
    return [] if sans_x(n) else [n]


def phrase_remplace_final(n, pt):
    """Phrase « on remplace » d'une expression déterminée (fin de descente) : les morceaux, puis le tout."""
    L = lim(n, pt)
    morceaux = []
    if isinstance(n, Op) and n.op == "/":
        A, B = lim(n.a, pt), lim(n.b, pt)
        pn_, pd_ = [x for x in cotes(n.a)], [x for x in cotes(n.b)]
        atomes = pn_ + pd_
        s = " et ".join(M(plain(a, pt)) for a in atomes)
        if len(pd_) > 1 or (pd_ and not isinstance(n.b, type(pd_[0]))) or (len(pd_) == 1 and n.b is not pd_[0]):
            s += f", donc {M(plain(n.b, pt))}"
        return (s + " et " if s else "") + M(f"{T(n)} \\to \\dfrac{{{LT(A)}}}{{{LT(B)}}} = {LT(L)}") + "."
    if isinstance(n, Op) and n.op == "*" and len(cotes(n)) >= 2:
        fs = cotes(n)
        s = " et ".join(M(plain(a, pt)) for a in fs)
        prod = " \\cdot ".join(LP(lim(a, pt)) for a in fs)
        return s + f", donc {M(f'{T(n)} \\to {prod} = {LT(L)}')}."
    return M(plain(n, pt)) + "."


