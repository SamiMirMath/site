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


# ---------------------------------------------------------------------------------------------------------------------
# Dérivées (table maison, confirmées numériquement) et leur présentation
# ---------------------------------------------------------------------------------------------------------------------
def _a_expo_neg(n):
    if isinstance(n, Op) and n.op == "^":
        k = valeur_constante(n.b)
        if k is not None and k < 0:
            return True
    if isinstance(n, (Neg, Fn)):
        return _a_expo_neg(n.a)
    return isinstance(n, Op) and (_a_expo_neg(n.a) or _a_expo_neg(n.b))


def _embellir(n):
    """3·(1/x) s'écrit 3/x."""
    if isinstance(n, Neg):
        return Neg(_embellir(n.a))
    if isinstance(n, Fn):
        return Fn(n.nom, _embellir(n.a))
    if isinstance(n, Op):
        a, b = _embellir(n.a), _embellir(n.b)
        if n.op == "*" and isinstance(a, Nb) and isinstance(b, Op) and b.op == "/" and isinstance(b.a, Nb) and b.a.v == 1:
            return Op("/", a, b.b)
        return Op(n.op, a, b)
    return n


def derive(h):
    d = _embellir(LA._derivee_nat(h))
    if not derivee_ok(h, d):
        raise Abandon("dérivée non confirmée : " + T(h))
    return d


def tex_derivee(d):
    """Écriture de la dérivée dans le tableau BH : −3x^{−4} = −\\frac{3}{x^{4}} quand elle contient une puissance négative."""
    t = T(d)
    if _a_expo_neg(d):
        m = mono(d)
        if m is not None:
            alt = mono_arbre(m)
            if T(alt) != t and egaux(alt, d):
                return t + " = " + T(alt)
    return t


def _fns(n, out):
    if isinstance(n, Fn):
        out.append(n)
        _fns(n.a, out)
    elif isinstance(n, Neg):
        _fns(n.a, out)
    elif isinstance(n, Op):
        _fns(n.a, out)
        _fns(n.b, out)


def intro_derivee(h):
    """Phrases du corrigé pour les dérivées composées : (e^u)' = u'e^u, (ln u)' = u'/u."""
    fs, vus, out = [], set(), []
    _fns(h, fs)
    for g in fs:
        u = g.a
        if g.nom == "exp":
            P = _poly(u)
            if P is not None and len(P) == 2:
                continue                                  # e^{kx+b} : la dérivée k·e^{kx+b} se lit dans le tableau
            cle = "e" + T(u)
            if cle in vus:
                continue
            vus.add(cle)
            du = derive(u)
            out.append(f"Pour dériver {M(T(g))}, on utilise {M(chr(92) + 'left(e^{u}' + chr(92) + 'right)' + chr(39) + ' = u' + chr(39) + 'e^{u}')} "
                       f"avec {M('u = ' + T(u))}, {M('u' + chr(39) + ' = ' + T(du))}.")
        elif g.nom == "ln" and not isinstance(u, X):
            cle = "l" + T(u)
            if cle in vus:
                continue
            vus.add(cle)
            du = derive(u)
            alt = mono(Op("/", du, u))
            fin = ""
            if alt is not None:
                a = mono_arbre(alt)
                brut = f"\\dfrac{{{T(du)}}}{{{T(u)}}}"
                if T(a) != brut and egaux(a, Op("/", du, u)):
                    fin = f" = {T(a)}"
            out.append(f"Pour dériver {M(T(g))}, on utilise {M(chr(92) + 'left(' + chr(92) + 'ln u' + chr(92) + 'right)' + chr(39) + ' = ' + chr(92) + 'dfrac{u' + chr(39) + '}{u}')} "
                       f"avec {M('u = ' + T(u))} et {M('u' + chr(39) + ' = ' + T(du))}"
                       + (f" : {M(chr(92) + 'dfrac{' + T(du) + '}{' + T(u) + '}' + fin)}" if fin else "") + ".")
    return out




# ---------------------------------------------------------------------------------------------------------------------
# Podium : classement exponentielle > puissance > logarithme, en t → +∞ (t = x, −x, ou 1/x en 0⁺)
# ---------------------------------------------------------------------------------------------------------------------
class Sans_podium(Exception):
    pass


def _poly(u):
    try:
        return LA._polynome_de(u)
    except Exception:
        return None


def _norm(n):
    """Écriture normalisée d'un arbre (arguments d'exp, ln et sommes compris) : 1/(1/t) → t."""
    if isinstance(n, Fn):
        return Fn(n.nom, _norm(n.a))
    if isinstance(n, Neg):
        return mono_arbre(_mono_norm(n))
    if isinstance(n, Op) and n.op in "+-":
        return Op(n.op, _norm(n.a), _norm(n.b))
    m = _mono_norm(n)
    return mono_arbre(m) if m is not None else n


def _mono_norm(n):
    m = mono(n)
    if m is None:
        return None
    fact = []
    for a, k in m.fact:
        if isinstance(a, Fn):
            a = Fn(a.nom, _norm(a.a))
        elif isinstance(a, Op) and a.op in "+-":
            a = Op(a.op, _norm(a.a), _norm(a.b))
        fact.append((a, k))
    out = Mono(m.coef)
    for t, k in fact:
        out = _fusion(out, Mono(1, [(t, k)]))
    return out


def en_t_arbre(f, pt):
    """f écrite en t (t → +∞) : (arbre, nom de t, borne +∞) ; en ±∞ l'arbre est f elle-même et s = ±1."""
    if pt.s:
        return f, None, pt.s
    if pt.a is not None and pt.a == 0 and pt.d > 0:
        return _norm(LA._substituer(f, Op("/", Nb(F(1)), X()))), "t = \\dfrac{1}{x}", 1
    raise Sans_podium()


def classer_atome(a, k, s):
    """(rang, valeur signée, coefficient dominant) de a^k quand x → s·∞ (t = s·x) ; Sans_podium sinon.
    rang 1 logarithme (valeur : multiple de ln t), 2 puissance (degré), 3 exponentielle (coefficient de t dans l'exposant)."""
    if isinstance(a, X):
        return 2, k, F(1)
    if isinstance(a, Fn) and a.nom == "exp":
        P = _poly(a.a)
        if P is None or len(P) != 2 or P[1] == 0:
            raise Sans_podium()
        return 3, k * P[1] * s, F(1)
    if isinstance(a, Fn) and a.nom == "ln":
        m = mono(a.a)
        if m is not None and len(m.fact) == 1 and isinstance(m.fact[0][0], X):
            j = m.fact[0][1]
            if m.coef > 0 and s > 0 or (m.coef < 0 and s < 0 and j % 2 == 1) or (m.coef > 0 and s < 0 and j % 2 == 0):
                return 1, k * j, F(1)
        P = _poly(a.a)
        if P is not None and len(P) >= 2 and P[-1] * (s ** (len(P) - 1)) > 0:
            return 1, k * (len(P) - 1), F(1)
        raise Sans_podium()
    P = _poly(a)
    if P is not None and len(P) >= 2 and P[-1] != 0:
        return 2, k * (len(P) - 1), P[-1] ** k
    raise Sans_podium()


NOM = {3: "l'exponentielle", 2: "la puissance", 1: "le logarithme"}


def nom_maj(r):
    return NOM[r][0].upper() + NOM[r][1:]


def classer(m, s):
    """(genre, rang, éléments) : genre 'inf' | 'zero' | 'const' ; éléments [(atome, k, rang, valeur)]."""
    cumul = {1: F(0), 2: F(0), 3: F(0)}
    coef = m.coef
    elems = []
    for a, k in m.fact:
        if sans_x(a):
            raise Sans_podium()
        r, v, c = classer_atome(a, k, s)
        cumul[r] += v
        if r == 2:
            coef *= c
        elems.append((a, k, r, v))
    for r in (3, 2, 1):
        if cumul[r] != 0:
            return ("inf" if cumul[r] > 0 else "zero"), elems, coef
    return "const", elems, coef


def signe_mot(s):
    return ">" if s > 0 else "<"


# ---------------------------------------------------------------------------------------------------------------------
# Tableau de valeurs (8.14) : valeurs en haute précision
# ---------------------------------------------------------------------------------------------------------------------
def fmt_val(v):
    import math
    if v is None:
        return None
    a = abs(v)
    if a >= 1e5 or (0 < a < 1e-4):
        e = int(math.floor(math.log10(a)))
        mant = v / 10 ** e
        return f"{mant:.2f}".replace(".", "{,}") + f" \\cdot 10^{{{e}}}"
    r = round(v)
    for d in range(4, 9):
        s = f"{v:.{d}f}"
        if float(s) != r:
            return s.replace(".", "{,}")
    return "\\approx " + str(int(r))


def tableau_valeurs(f, pt):
    """([x tex], [valeur tex]) ; None si trop peu de points évaluables."""
    import mpmath
    mp = mpmath.MPContext()
    mp.dps = 80
    if pt.s < 0:
        xs = [-1, -10, -20, -25, -30]
    elif pt.s > 0:
        xs = [1, 10, 20, 50, 100]
    else:
        a = float(charger_sympy().N(pt.a))
        xs = [a + pt.d * h for h in (0.1, 0.01, 0.001, 0.0001, 0.00001)]
    out_x, out_v = [], []
    for x in xs:
        try:
            v = LA._val_mp(mp, f, mp.mpf(x))
        except Exception:
            v = None
        if v is None:
            continue
        out_x.append(str(x).replace(".", "{,}") if not isinstance(x, int) else str(x))
        out_v.append(fmt_val(float(v)))
    return (out_x, out_v) if len(out_x) >= 3 else None


# ---------------------------------------------------------------------------------------------------------------------
# La descente
# ---------------------------------------------------------------------------------------------------------------------
def _contient_transcendant(n):
    if isinstance(n, Fn):
        return n.nom in ("exp", "ln") or _contient_transcendant(n.a)
    if isinstance(n, Neg):
        return _contient_transcendant(n.a)
    return isinstance(n, Op) and (_contient_transcendant(n.a) or _contient_transcendant(n.b) or (n.op == "^" and not sans_x(n.b)))


def _facteurs_produit(n, out):
    if isinstance(n, Op) and n.op == "*":
        _facteurs_produit(n.a, out)
        _facteurs_produit(n.b, out)
    else:
        out.append(n)


def _a_fraction(n):
    if isinstance(n, Op):
        return n.op == "/" or _a_fraction(n.a) or _a_fraction(n.b)
    if isinstance(n, (Neg, Fn)):
        return _a_fraction(n.a)
    return False


def _commun(a, b):
    fa, fb = [], []
    _facteurs_produit(a.a if isinstance(a, Neg) else a, fa)
    _facteurs_produit(b.a if isinstance(b, Neg) else b, fb)
    for x in fa:
        if isinstance(x, Nb) or sans_x(x):
            continue
        if any(T(x) == T(y) for y in fb):
            return x
    return None


def desigmer(c):
    """−A/B devient (−A)/B : le signe passe dans le haut, comme le corrigé (−x²/e^(−3x))."""
    if isinstance(c, Neg) and isinstance(c.a, Op) and c.a.op == "/":
        return Op("/", LA._oppose_arbre(c.a.a), c.a.b)
    return c


def fmt_approx(v):
    s = f"{v:.2f}" if abs(v) >= 1 else f"{v:.2g}"
    return s.replace(".", "{,}")


class Desc:
    def __init__(self, f, pt):
        self.f, self.pt = f, pt
        self.etapes = []
        self.alertes = []
        self.n_bh = 0
        self.attendu = None            # (genre, signe) annoncé par le podium
        self.devine = None             # valeur devinée à la calculatrice (8.14)
        self.constante = None

    # ---- blocs ----
    def etape(self, titre, blocs):
        self.etapes.append({"titre": titre, "blocs": [b for b in blocs if b]})

    def lim_tex(self, e):
        return f"\\lim_{{x\\to {self.pt.tex()}}} {T(e)}"

    def txt(self, html):
        return so.texte(html, style="etape")

    def disp(self, t):
        return so.texte(D(t), style="etape")

    def forme_phrase(self, nom, A, B, op, encore=False):
        ft = forme_tex(nom, A, B, op)
        if nom:
            return f"Forme {M(ft)} : {'encore ' if encore else ''}{IND()}."
        return f"Forme {M(ft)} : {DET()}!"

    # ---- analyse d'une expression ----
    def analyse(self, c):
        """('ind', nom, A, B, op) | ('det', L, A, B, op) | ('cst', L) pour c = A/B, produit ou autre."""
        pt = self.pt
        try:
            if isinstance(c, Op) and c.op == "/":
                nom, A, B = forme(c, pt)
                return ("ind", nom, A, B, "/") if nom else ("det", lim(c, pt), A, B, "/")
            fs = cotes(c)
            if isinstance(c, (Op, Neg)) and len(fs) == 2 and not (isinstance(c, Op) and c.op in "+-"):
                if not (isinstance(c, Neg)):
                    A, B = lim(fs[0], pt), lim(fs[1], pt)
                    nom = "0·∞" if ((A.inf and B.nul()) or (B.inf and A.nul())) else None
                    return ("ind", nom, A, B, "*") if nom else ("det", lim(c, pt), A, B, "*")
            return ("cst" if sans_x(c) else "det", lim(c, pt), None, None, None)
        except LA.FormeIndeterminee:
            raise Abandon("forme indéterminée imbriquée")

    # ---- étape « on remplace » ----
    def texte_haut_bas(self, f):
        pt = self.pt
        if isinstance(f, Op) and f.op == "/":
            h = fragment(f.a, pt) or M(plain(f.a, pt))
            b = fragment(f.b, pt) or M(plain(f.b, pt))
            return f"Haut : {h}. Bas : {b}. "
        fs = cotes(f)
        return ". ".join(fragment(x, pt) or M(plain(x, pt)) for x in fs) + ". "

    # ---- prédiction ----
    def signe_global(self, f):
        m = mono(f)
        if m is None:
            raise Abandon("signe inconnu")
        s = 1 if m.coef > 0 else -1
        for a, k in m.fact:
            sa = signe_lim(lim(a, self.pt))
            if sa == 0:
                raise Abandon("signe d'un facteur inconnu")
            if k % 2:
                s *= sa
        return s

    def prediction(self, f):
        """(bloc, (genre, signe)) ; Sans_podium si le podium ne peut pas aider."""
        pt = self.pt
        ft, nom_t, s = en_t_arbre(f, pt)
        m = _mono_norm(ft)
        if m is None:
            raise Sans_podium()
        genre, elems, coef = classer(m, s)
        if genre == "const":
            raise Sans_podium()
        sg = self.signe_global(f)
        tr = (lambda t: t.replace("x", "t")) if nom_t else (lambda t: t)
        lignes = []
        quotient = bool(nom_t) or (isinstance(f, Op) and f.op == "/")
        if nom_t:
            lignes.append("On pense à " + M(nom_t) + " : quand " + M("x \\to " + pt.tex()) + ", " + M("t \\to +\\infty")
                          + ", et " + M(tr(T(self._canon(f, m, elems)))) + ".")
        if quotient:
            haut = [e for e in elems if e[3] > 0]
            bas = [e for e in elems if e[3] < 0]
            if not haut or not bas:
                raise Sans_podium()
            dh = max(haut, key=lambda e: (e[2], abs(e[3])))
            db = max(bas, key=lambda e: (e[2], abs(e[3])))
            nm = lambda e: tr(T(self._affiche(e, nom_t)))
            l1 = f"Au haut : {M(nm(dh))}. Au bas : {M(nm(db))}. "
            if dh[2] != db[2]:
                hg = dh[2] > db[2]
                g, p = (dh, db) if hg else (db, dh)
                l1 += (f"Sur le podium, {NOM[g[2]]} bat {NOM[p[2]]} : c'est le <b>{'haut' if hg else 'bas'}</b> qui gagne, "
                       f"donc le quotient {'part vers l' + chr(39) + 'infini' if hg else 'tend vers 0'}.")
            elif dh[2] == 2:
                hg = abs(dh[3]) > abs(db[3])
                l1 += (f"La plus grande puissance est au <b>{'haut' if hg else 'bas'}</b>, donc le quotient "
                       f"{'part vers l' + chr(39) + 'infini' if hg else 'tend vers 0'}.")
            else:
                raise Sans_podium()
            lignes.append(l1)
            lignes.append(self.ligne_signe(f, True))
        else:
            fs = cotes(f)
            rangs = {}
            for a, k, r, v in elems:
                rangs.setdefault(r, []).append(a)
            if len(fs) < 2 or len(rangs) < 2:
                raise Sans_podium()
            hi, lo = max(rangs), min(rangs)
            gagnant = rangs[hi][0]
            l1 = "Produit : " + " et ".join(M(plain(a, pt)) for a in fs) + ". "
            verbe = "bat" if hi == 3 else "est plus forte que"
            l1 += (f"{nom_maj(hi)} {verbe} {NOM[lo]} : c'est {M(T(gagnant))} qui impose sa limite, "
                   f"donc {'0' if genre == 'zero' else '∞'}.")
            lignes.append(l1)
            lignes.append(self.ligne_signe(f, False))
        val = ("+\\infty" if sg > 0 else "-\\infty") if genre == "inf" else ("0^{+}" if sg > 0 else "0^{-}")
        lignes.append(f"<b>On s'attend à :</b> {M(val)}")
        return so.encadre("prediction", "Prédiction avec la règle du podium", lignes), (genre, sg)

    def _affiche(self, e, nom_t):
        a, k, r, v = e
        if isinstance(a, X) or (r == 2 and not isinstance(a, Fn)):
            P = _poly(a)
            d = abs(k) * (len(P) - 1) if P else abs(k)
            return Op("^", X(), Nb(F(d))) if d > 1 else X()
        return a

    def _canon(self, f, m, elems):
        out = Mono(m.coef)
        for a, k, r, v in elems:
            if isinstance(a, Fn) and a.nom == "exp" and v < 0:
                a, k = Fn("exp", _norm(LA._oppose_arbre(a.a))), -k
            out = _fusion(out, Mono(1, [(a, k)]))
        return mono_arbre(out)

    def ligne_signe(self, f, quotient):
        pt = self.pt
        sg = self.signe_global(f)
        if quotient and isinstance(f, Op) and f.op == "/":
            sa, sb = signe_lim(lim(f.a, pt)), signe_lim(lim(f.b, pt))
            return f"Signe : haut {signe_mot(sa)} 0, bas {signe_mot(sb)} 0, donc quotient {signe_mot(sg)} 0."
        fs = cotes(f)
        parts = [f"{M(T(a))} {signe_mot(signe_lim(lim(a, pt)))} 0" for a in fs]
        return "Signe : " + " et ".join(parts) + f", donc {'produit' if len(fs) > 1 else 'quotient'} {signe_mot(sg)} 0."

    def bloc_calculatrice(self, f):
        """Podium inapplicable (8.14) : encadré + tableau de valeurs ; renvoie (blocs, valeur devinée ou None)."""
        pt = self.pt
        tv = tableau_valeurs(f, pt)
        lignes = ["Ici, le podium <b>ne peut pas aider</b> : il n'y a pas de « course » entre une exponentielle, une puissance et un logarithme "
                  "qui partent vers l'infini."]
        if tv is not None:
            lignes.append("Pour prédire, on utilise la calculatrice (tableau ci-dessous).")
        blocs = [so.encadre("prediction", "Prédiction avec la règle du podium", lignes)]
        if tv is not None:
            blocs.append(so.valeurs(T(f), tv[0], tv[1]))
            blocs.append(so.texte("<i>La calculatrice ne prouve rien : c'est le calcul qui suit qui donne la réponse sûre.</i>", style="etape"))
        return blocs, tv


# ---------------------------------------------------------------------------------------------------------------------
# Suite de la classe Desc (méthodes ajoutées à la fin du module)
# ---------------------------------------------------------------------------------------------------------------------
def _m_resoudre(self):
    f = self.f
    if isinstance(f, Fn) and f.nom in ("exp", "ln"):
        return self.composee(f)
    if isinstance(f, Op) and f.op in "*/":
        return self.produit_quotient(f)
    raise Abandon("forme non prise en charge par la rédaction descendante")


def _m_produit_quotient(self, f):
    pt = self.pt
    A, B, op = None, None, None
    texte = self.texte_haut_bas(f)
    if isinstance(f, Op) and f.op == "/":
        nom, A, B = forme(f, pt)
        op = "/"
    else:
        fs = cotes(f)
        if len(fs) != 2:
            raise Abandon("produit de plus de deux facteurs non constants")
        A, B = lim(fs[0], pt), lim(fs[1], pt)
        nom = "0·∞" if ((A.inf and B.nul()) or (B.inf and A.nul())) else None
        op = "*"
    if nom is None:                                          # forme déterminée
        L = lim(f, pt)
        self.etape("on remplace", [self.txt(texte + self.forme_phrase(None, A, B, op))])
        return self.conclure_direct(f, A, B, op, L)
    # ---- étape 1 : on remplace, prédiction ----
    blocs1 = [self.txt(texte + self.forme_phrase(nom, A, B, op))]
    try:
        bloc, self.attendu = self.prediction(f)
        blocs1.append(bloc)
    except Sans_podium:
        bs, self.devine = self.bloc_calculatrice(f)
        blocs1 += bs
    self.etape("on remplace", blocs1)
    cur = f
    if op == "*":
        cur = self.preparer_produit(cur)
    else:
        cur = Op("/", f.a, f.b)
    L = self.boucle(cur.a, cur.b)
    if self.constante is not None:
        c, Lc = self.constante
        L2 = LA._produit(Lc, L)
        self.etape("on n'oublie pas la constante", [self.txt(M(f"{T(c)} \\cdot {LT(L)} = {LT(L2)}")
                                                              + (" (une constante positive fois un nombre minuscule négatif)." if False else "."))])
        L = L2
    return L


def _m_conclure_direct(self, f, A, B, op, L):
    if op == "/":
        if A.nul() and B.inf:
            phrase = "Un nombre minuscule divisé par un nombre énorme reste minuscule :"
        elif A.inf and B.nul():
            phrase = "Un nombre énorme (positif ou négatif) divisé par un nombre minuscule devient encore plus énorme :"
        elif A.inf:
            phrase = "Un nombre énorme divisé par un nombre ordinaire reste énorme :"
        else:
            phrase = "On conclut avec les règles de calcul :"
        chaine = f"\\dfrac{{{LT(A)}}}{{{LT(B)}}} = {LT(L)}"
    else:
        if A.inf and B.inf:
            phrase = f"(règle des signes : {'+' if A.inf > 0 else '−'} · {'+' if B.inf > 0 else '−'} = {'+' if L.inf > 0 else '−'}) :"
        else:
            phrase = "On conclut avec les règles de calcul :"
        chaine = f"{LP(A)} \\cdot {LP(B)} = {LT(L)}"
    blocs = [self.txt(phrase), so.resultat_lim(f"{self.lim_tex(f)} = {chaine}")]
    if op == "/" and ((A.nul() and B.inf) or (A.inf and B.nul())):
        fm = "\\dfrac{0}{\\infty}" if A.nul() else "\\dfrac{\\infty}{0}"
        blocs.append(so.encadre("attention", "Attention", [
            f"Ici, il <b>ne faut pas</b> utiliser BH : la forme {M(fm)} n'est pas indéterminée. "
            "C'est exactement pour cela qu'on vérifie <b>toujours</b> la forme en premier."]))
    elif op == "*" and A.inf and B.inf:
        blocs.append(so.encadre("attention", "Attention", ["Pas de BH ici : un produit de deux « énormes » n'est jamais indéterminé."]))
    self.etape("on conclut directement", blocs)
    self.final_deja = True
    return L


def _m_preparer_produit(self, cur):
    """Produit 0·∞ : simplification du logarithme, constante sortie, mise en quotient ; renvoie le quotient (Op '/')."""
    pt = self.pt
    x_positif = pt.s > 0 or (pt.a is not None and pt.a == 0 and pt.d > 0)
    # (a) ln(x^k) = k ln(x)
    fs = []
    _facteurs_produit(cur, fs)
    nouveaux, change = [], []
    for g in fs:
        if isinstance(g, Fn) and g.nom == "ln" and x_positif:
            m = mono(g.a)
            if m is not None and m.coef == 1 and len(m.fact) == 1 and isinstance(m.fact[0][0], X) and m.fact[0][1] not in (1,):
                k = m.fact[0][1]
                nouveaux.append(Op("*", Nb(F(k)), Fn("ln", X())))
                change.append((g, k))
                continue
        nouveaux.append(g)
    if change:
        g2 = _produit(nouveaux)
        nv = mono_arbre(mono(g2))
        if not egaux(cur, nv):
            raise Abandon("simplification du logarithme non confirmée")
        g, k = change[0]
        self.etape("on simplifie le logarithme", [self.txt(
            f"Propriété des logarithmes : {M(T(g) + ' = ' + str(k) + chr(92) + 'ln(x)')}. Donc"),
            self.disp(f"{T(cur)} = {T(nv)}")])
        cur = nv
    # (b) constante : e^(ax+b) = e^(ax)·e^b
    fs = []
    _facteurs_produit(cur, fs)
    cstes, reste = [], []
    for g in fs:
        if isinstance(g, Fn) and g.nom == "exp":
            P = _poly(g.a)
            if P is not None and len(P) == 2 and P[0] != 0:
                cstes.append(Fn("exp", Nb(P[0])))
                reste.append(Fn("exp", LA._arbre_poly([F(0), P[1]])))
                continue
        reste.append(g)
    if cstes:
        c = _produit(cstes)
        g2 = Op("*", c, _produit(reste))
        if not egaux(cur, g2):
            raise Abandon("constante non confirmée")
        Lc = lim(c, pt)
        v = float(charger_sympy().N(Lc.val))
        sign = "positive" if v > 0 else "négative"
        g_old = next(g for g in fs if isinstance(g, Fn) and g.nom == "exp" and _poly(g.a) and len(_poly(g.a)) == 2 and _poly(g.a)[0] != 0)
        g_new = next(g for g in reste if isinstance(g, Fn) and g.nom == "exp")
        self.etape("on sort la constante", [
            self.txt(f"Propriété des puissances : {M(T(g_old) + ' = ' + T(g_new) + chr(92) + 'cdot ' + T(c))}. "
                     f"Le nombre {M(T(c) + ' ' + chr(92) + 'approx ' + fmt_approx(v))} est une <b>constante {sign}</b> : elle ne change "
                     + ("ni le signe ni " if v > 0 else "pas ") + "le résultat « 0 ou ∞ ». On la garde de côté :"),
            self.disp(f"{T(cur)} = {T(c)} \\cdot {T(_produit(reste))}")])
        self.constante = (c, Lc)
        cur = _produit(reste)
    # (c) produit → quotient
    fs = []
    _facteurs_produit(cur, fs)
    pt_zero = [g for g in fs if not sans_x(g) and lim(g, pt).nul()]
    if len(pt_zero) != 1:
        raise Abandon("facteur tendant vers 0 non unique")
    z = pt_zero[0]
    autres = [g for g in fs if g is not z]
    haut = _produit(autres) if len(autres) > 1 else autres[0]
    if isinstance(haut, Op) and haut.op == "*" and isinstance(haut.a, Nb):
        pass
    bas = LA._inverse_en_bas(z)
    q = Op("/", haut, bas)
    if not egaux(cur, q):
        raise Abandon("quotient non confirmé")
    # le haut est mis sous forme normale (3 e^{-x} ln x)
    haut_n = mono_arbre(mono(haut))
    q = Op("/", haut_n, bas)
    blocs = [self.txt(f"BH ne marche pas sur un produit. On écrit {M(T(z) + ' = ' + T(Op('/', Nb(F(1)), bas)))} :"),
             self.disp(f"{T(cur)} = {T(q)}")]
    if any(isinstance(g, Fn) and g.nom == "ln" for g in autres):
        ln_g = next(g for g in autres if isinstance(g, Fn) and g.nom == "ln")
        blocs.append(self.txt(f"<i>Pourquoi garder {M(T(ln_g))} en haut ? Parce que sa dérivée {M(T(_embellir(LA._derivee_nat(ln_g))))} est simple. "
                              f"Si on mettait {M(chr(92) + 'dfrac{1}{' + T(ln_g) + '}')} en bas, sa dérivée serait compliquée.</i>"))
    self.etape("on transforme le produit en quotient", blocs)
    # (d) on vérifie la forme
    an = self.analyse(q)
    if an[0] != "ind":
        raise Abandon("le quotient n'est pas indéterminé")
    _, nom, A, B, _ = an
    self.etape("on vérifie la forme", [self.txt(self.texte_haut_bas(q) + self.forme_phrase(nom, A, B, "/"))])
    self.forme_deja = True
    return q


def _m_boucle(self, N, Dn):
    """Boucle BH sur N/Dn (forme indéterminée) ; renvoie la limite finale. Les étapes sont ajoutées à self.etapes."""
    pt = self.pt
    encore = False
    while True:
        self.n_bh += 1
        if self.n_bh > MAX_BH:
            raise Abandon("plus de quatre BH")
        dN, dD = derive(N), derive(Dn)
        intro = intro_derivee(N) + intro_derivee(Dn)
        q = Op("/", dN, dD)
        C = mono_arbre(mono(q)) if mono(q) is not None else q
        if not egaux(q, C):
            raise Abandon("simplification non confirmée")
        identique = T(C) == T(q)
        simple = not _a_fraction(dN) and not _a_fraction(dD)
        commun = _commun(dN, dD)
        blocs = []
        if intro:
            blocs.append(self.txt(" ".join(intro)))
        blocs.append(so.bh(T(N), tex_derivee(dN), T(Dn), tex_derivee(dD)))
        chaine = f"{self.lim_tex(Op('/', N, Dn))} \\overset{{\\text{{BH}}}}{{=}} \\lim_{{x\\to {pt.tex()}}} {T(q)}"
        note = None
        sep_etape = False
        if not identique:
            if simple or commun is not None:
                chaine += f" = \\lim_{{x\\to {pt.tex()}}} {T(C)}"
                if commun is not None and not simple:
                    note = f"(Les deux {M(T(commun))} se simplifient.)"
            else:
                sep_etape = True
        blocs.append(self.disp(chaine))
        if note:
            blocs.append(self.txt(note))
        cur = C if (not identique) else q
        cur = desigmer(cur)
        an = self.analyse(cur)
        titre = "BH"
        etape_bh = {"titre": titre, "blocs": None}
        if not sep_etape:
            if an[0] == "ind":
                blocs.append(self.txt(self.forme_phrase(an[1], an[2], an[3], an[4], encore=True)))
            self.etapes.append({"titre": "BH", "blocs": [b for b in blocs if b], "bh": True})
        else:
            self.etapes.append({"titre": "BH", "blocs": [b for b in blocs if b], "bh": True})
            dd = Op("/", Nb(F(1)), dD) if not (isinstance(dD, Op) and dD.op == "/") else Op("/", dD.b, dD.a)
            inter = Op("*", dN, mono_arbre(mono(dd)) if mono(dd) is not None else dd)
            expl = "Diviser par une fraction, c'est multiplier par son inverse :"
            if isinstance(dD, Op) and dD.op == "/" and isinstance(dD.a, Nb) and dD.a.v == 1:
                expl = f"Diviser par {M(T(dD))}, c'est multiplier par {M(T(dD.b))} :"
            egal = f"{T(q)} = {T(inter)}" if T(inter) != T(C) else f"{T(q)}"
            ch2 = f"{T(q)} = {T(inter)} = {T(C)}" if T(inter) != T(C) else f"{T(q)} = {T(C)}"
            if not egaux(inter, q):
                raise Abandon("simplification intermédiaire non confirmée")
            b2 = [self.txt(expl), self.disp(ch2)]
            if an[0] == "ind":
                b2.append(self.txt(self.forme_phrase(an[1], an[2], an[3], an[4], encore=True)))
            self.etape("on simplifie", b2)
        if an[0] == "ind":
            N, Dn = cur.a, cur.b
            encore = True
            continue
        # forme déterminée : on remplace
        L = an[1]
        self.etape("on remplace", [self.txt(phrase_remplace_final(cur, pt))])
        return L


def _m_composee(self, f):
    pt = self.pt
    u = f.a
    ext = "l'exposant" if f.nom == "exp" else "l'intérieur du ln"
    try:
        Lu = lim(u, pt)
        direct = True
    except LA.FormeIndeterminee:
        direct = False
    mot = "Exposant" if f.nom == "exp" else "Intérieur"
    if direct:
        L = LA._exp_lim(Lu) if f.nom == "exp" else LA._ln_lim(Lu)
        d = detail(u, pt)
        phrase = f"{mot} : " + M(d if d else plain(u, pt)) + "."
        phrase += " Donc " + M(f"{T(f)} \\to " + (f"e^{{{LT(Lu)}}}" if f.nom == "exp" else f"\\ln({LT(Lu)})") + f" = {LT(L)}") + "."
        self.etape("on remplace", [self.txt(phrase), so.resultat_lim(f"{self.lim_tex(f)} = {LT(L)}")])
        self.final_deja = True
        return L
    if not (isinstance(u, Op) and u.op == "/"):
        raise Abandon("exposant indéterminé qui n'est pas un quotient")
    nom, A, B = forme(u, pt)
    if nom not in ("0/0", "∞/∞"):
        raise Abandon("forme de l'exposant")
    blocs = [self.txt(self.texte_haut_bas(u) + self.forme_phrase(nom, A, B, "/"))]
    attendu = None
    try:
        bp, attendu = self.prediction_exposant(u, f)
        blocs.append(bp)
    except Sans_podium:
        pass
    chaine, Lu = self.bh_compact(u.a, u.b)
    blocs.append(self.txt("Calcul avec BH :"))
    blocs.append(self.disp(chaine))
    titre = "limite de l'exposant, à part" if f.nom == "exp" else "limite de l'intérieur du ln"
    self.etape(titre, blocs)
    L = LA._exp_lim(Lu) if f.nom == "exp" else LA._ln_lim(Lu)
    ap = ""
    if not L.inf and not L.nul():
        v = float(charger_sympy().N(L.val))
        ap = f" \\approx {fmt_approx(v)}" if not L.val.is_Rational else ""
    ent = f"e^{{{LT(Lu)}}}" if f.nom == "exp" else f"\\ln({LT(Lu)})"
    egal = f"{ent} = {LT(L)}" if ent != LT(L) else ent
    self.etape("on applique l'exponentielle" if f.nom == "exp" else "on applique le logarithme",
               [so.resultat_lim(f"{self.lim_tex(f)} = {egal}{ap}")])
    self.final_deja = True
    self.attendu_exposant = attendu
    self.Lu = Lu
    return L


def _m_bh_compact(self, N, Dn):
    pt = self.pt
    s = f"\\lim_{{x\\to {pt.tex()}}} {T(Op('/', N, Dn))}"
    for _ in range(MAX_BH):
        dN, dD = derive(N), derive(Dn)
        q = Op("/", dN, dD)
        s += " \\overset{\\text{BH}}{=} \\lim_{x\\to " + pt.tex() + "} " + T(q)
        m = mono(q)
        C = mono_arbre(m) if m is not None else q
        if not egaux(q, C):
            raise Abandon("simplification non confirmée")
        an = self.analyse(desigmer(C) if T(C) != T(q) else q)
        if an[0] == "ind":
            if T(C) != T(q):
                s += " = \\lim_{x\\to " + pt.tex() + "} " + T(C)
                C = desigmer(C)
            else:
                C = q
            s += f" \\quad \\left(\\text{{forme }} {forme_tex(an[1], an[2], an[3], an[4])}\\right)"
            N, Dn = C.a, C.b
            continue
        L = an[1]
        if T(C) != T(q) and not (isinstance(C, Nb)):
            s += " = \\lim_{x\\to " + pt.tex() + "} " + T(C)
        s += f" = {LT(L)}"
        return s, L
    raise Abandon("trop de BH")


def _m_prediction_exposant(self, u, f):
    """Podium sur l'exposant (quotient de polynômes en ±∞) : quotient des coefficients, ou plus grande puissance."""
    pt = self.pt
    if not pt.s:
        raise Sans_podium()
    P, Q = _poly(u.a), _poly(u.b)
    if P is None or Q is None:
        raise Sans_podium()
    dp, dq = len(P) - 1, len(Q) - 1
    nom = lambda d: T(Op("^", X(), Nb(F(d))) if d > 1 else X())
    cible = "exposant" if f.nom == "exp" else "intérieur"
    sA, sB = signe_lim(lim(u.a, pt)), signe_lim(lim(u.b, pt))
    if dp == dq:
        c = F(P[-1]) / F(Q[-1])
        fr = f"\\dfrac{{{qtex_(P[-1])}}}{{{qtex_(Q[-1])}}}"
        valeur = qtex_(c)
        l1 = (f"Même puissance {M(nom(dp))} en haut et en bas : égalité ! On s'attend au quotient des coefficients : "
              f"{M(fr + (' = ' + valeur if fr != valeur else ''))}.")
        lignes = [l1]
        ap = f" \\to {valeur}"
        ent = f"e^{{{valeur}}}" if f.nom == "exp" else f"\\ln({valeur})"
        fin = f"{cible} {M('\\to ' + valeur)}, donc {M((f'e^{{\\cdots}}' if f.nom == 'exp' else '\\ln(\\cdots)') + ' \\to ' + ent)}"
        genre = ("const", c)
    else:
        hg = dp > dq
        pos = "haut" if hg else "bas"
        sg = sA * sB
        gr = f"En haut {M(nom(dp))}, en bas {M(nom(dq))} : la plus grande puissance est au <b>{pos}</b>, donc {'l' + chr(39) + 'exposant part vers l' + chr(39) + 'infini' if hg else 'l' + chr(39) + 'exposant tend vers 0'}."
        if f.nom == "ln" and hg:
            gr = gr.replace("l'exposant", "l'intérieur")
        elif f.nom == "ln":
            gr = gr.replace("l'exposant", "l'intérieur")
        lignes = [gr, f"Signe : haut {signe_mot(sA)} 0, bas {signe_mot(sB)} 0, donc {'0' if not hg else ''}{'^{+}' if False else ''}"]
        # écriture du signe : 0⁺ / 0⁻ ou ±∞
        if hg:
            vu = "+\\infty" if sg > 0 else "-\\infty"
        else:
            vu = "0^{+}" if sg > 0 else "0^{-}"
        lignes[1] = f"Signe : haut {signe_mot(sA)} 0, bas {signe_mot(sB)} 0, donc {M(vu)}."
        if f.nom == "exp":
            sortie = {"+\\infty": "+\\infty", "-\\infty": "0^{+}", "0^{+}": "1", "0^{-}": "1"}[vu]
            ent = f"e^{{{vu}}}" if hg else "e^{0} = 1"
            fin = f"{cible} {M('\\to ' + vu)}, donc {M('e^{\\cdots} \\to ' + (ent if hg else 'e^{0} = 1'))}"
            if hg and vu == "-\\infty":
                fin = f"{cible} {M('\\to -\\infty')}, donc {M('e^{\\cdots} \\to 0^{+}')}"
            elif hg:
                fin = f"{cible} {M('\\to +\\infty')}, donc {M('e^{\\cdots} \\to +\\infty')}"
        else:
            fin = f"{cible} {M('\\to ' + vu)}, donc {M('\\ln(\\cdots)')} à calculer ensuite"
        genre = ("inf" if hg else "zero", sg)
        if not hg and f.nom == "exp":
            fin = f"{cible} {M('\\to ' + vu)}, donc {M('e^{\\cdots} \\to e^{0} = 1')}"
    lignes.append(f"<b>On s'attend à :</b> {fin}")
    return so.encadre("prediction", "Prédiction avec la règle du podium", lignes), genre


def qtex_(c):
    c = F(c)
    return str(c.numerator) if c.denominator == 1 else (("-" if c < 0 else "") + f"\\frac{{{abs(c.numerator)}}}{{{c.denominator}}}")


Desc.resoudre = _m_resoudre
Desc.produit_quotient = _m_produit_quotient
Desc.conclure_direct = _m_conclure_direct
Desc.preparer_produit = _m_preparer_produit
Desc.boucle = _m_boucle
Desc.composee = _m_composee
Desc.bh_compact = _m_bh_compact
Desc.prediction_exposant = _m_prediction_exposant


# ---------------------------------------------------------------------------------------------------------------------
# Point d'entrée
# ---------------------------------------------------------------------------------------------------------------------
def _signe_numerique(f, pt, L):
    """Signe de f près du point par mpmath (haute précision) ; Abandon s'il contredit la limite annoncée."""
    import mpmath
    mp = mpmath.MPContext()
    mp.dps = 80
    pts = []
    for k in (3, 5, 8):
        if pt.s:
            pts.append(pt.s * mp.mpf(10) ** k)
        else:
            a = mp.mpf(str(charger_sympy().N(pt.a, 60)))
            pts.append(a + pt.d * mp.mpf(10) ** (-k))
    sg = set()
    for x in pts:
        try:
            v = LA._val_mp(mp, f, x)
        except Exception:
            v = None
        if v is not None and v != 0:
            sg.add(1 if v > 0 else -1)
    if not sg:
        return
    attendu = signe_lim(L) if (L.inf or L.nul()) else None
    if attendu and (len(sg) != 1 or attendu not in sg):
        raise Abandon("signe contredit par la sonde")


def descente(f, pt, ref):
    """Rédaction descendante de lim f en pt (référence SymPy `ref`) : {"etapes", "alertes", "valeur"} ou Abandon."""
    if not _contient_transcendant(f):
        raise Abandon("fonction rationnelle : méthodes actuelles (R18)")
    R = LA._lim_depuis_sympy(ref)
    d = Desc(f, pt)
    d.final_deja = False
    try:
        L = d.resoudre()
    except LA.FormeIndeterminee as e:
        raise Abandon("forme indéterminée imbriquée : " + str(e))
    if not LA._meme_valeur(L, R):
        raise Abandon(f"valeur rédigée {LT(L)} ≠ référence {R.tex()}")
    _signe_numerique(f, pt, L)
    # prédiction : comparée au résultat final
    att = d.attendu
    confirme = None
    if att is not None:
        genre, sg = att
        ok = (genre == "inf" and L.inf == sg) or (genre == "zero" and L.nul() and L.ap == sg)
        if ok:
            confirme = "✓ Le calcul confirme la prédiction du podium."
        else:
            d.alertes.append(f"prédiction {att} ≠ résultat {LT(L)}")
            d.etapes = [dict(e, blocs=[b for b in e["blocs"] if not (b.get("type") == "encadre" and b.get("genre") == "prediction")])
                        for e in d.etapes]
    elif getattr(d, "attendu_exposant", None) is not None:
        genre, v = d.attendu_exposant
        Lu = d.Lu
        if genre == "const":
            ok = (not Lu.inf) and (not Lu.nul() or v == 0) and abs(float(charger_sympy().N(Lu.val)) - float(v)) < 1e-12
        else:
            ok = (genre == "inf" and Lu.inf == v) or (genre == "zero" and Lu.nul() and Lu.ap == v)
        if ok:
            confirme = "✓ Le calcul confirme la prédiction du podium."
        else:
            d.alertes.append(f"prédiction de l'exposant {d.attendu_exposant} ≠ {LT(Lu)}")
    elif d.devine is not None:
        xs, vs = d.devine
        v = vs[-1]
        try:
            ok = (not L.inf) and abs(float(v.replace("{,}", ".").replace("\\approx ", "")) - float(charger_sympy().N(L.val))) < 1e-3
        except Exception:
            ok = False
        if ok:
            confirme = "La calculatrice avait bien « deviné » : le calcul le confirme."
        else:
            d.alertes.append("valeurs de la calculatrice non cohérentes avec le résultat")
    bhs = [e for e in d.etapes if e.get("bh")]
    ordres = ["1re", "2e", "3e", "4e"]
    for i, e in enumerate(bhs):
        e["titre"] = "BH" if len(bhs) == 1 else f"BH ({ordres[i]} fois)"
    if not d.final_deja:
        dernier = d.etapes[-1]
        dernier["blocs"].append(so.resultat_lim(f"{d.lim_tex(f)} = {LT(L)}"))
    if confirme:
        d.etapes[-1]["blocs"].append(so.texte(confirme, style="confirme"))
    return {"etapes": d.etapes, "alertes": d.alertes, "valeur": L}
