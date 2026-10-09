"""
ensemble_def.py — Calcul détaillé de l'ensemble de définition (ED) d'une fonction.

Python pur (aucune dépendance) : fonctionne en local et dans le navigateur via Pyodide.

Utilisation :
    python3 ensemble_def.py "ln(x^2-4)/(x-5)"
    >>> from ensemble_def import analyser
    >>> analyser("ln(x)/(ln(x)+2)")          # dictionnaire
    >>> analyser_json("1/(e^x-1)")           # chaîne JSON (utilisée par le site)

Fonctions reconnues : ln (ou log), exp (ou e^...), sqrt (ou racine, √), puissances entières,
puissance 1/2. Multiplication implicite : 2x, 3ln(x), (x+1)(x-2).

Principe :
  1. On repère chaque logarithme (argument > 0), chaque dénominateur (≠ 0),
     chaque racine carrée (contenu ≥ 0) : conditions C1, C2, ...
  2. Chaque condition est résolue exactement : factorisation, discriminant,
     tableau de signes ; si la condition porte sur ln(B), e^B ou √B,
     on pose t = ln(B) (etc.), on résout en t puis on revient à x.
  3. ED = E1 ∩ E2 ∩ ...
"""
from fractions import Fraction as F
import math
import json

__all__ = ["analyser", "analyser_json", "apercu_json"]


class ErreurSaisie(Exception):
    pass


class NonPrisEnCharge(Exception):
    pass


# =====================================================================
# 1. ARBRE SYNTAXIQUE
# =====================================================================
class Noeud:
    pass


class Nb(Noeud):
    def __init__(self, v, txt=None):
        self.v = F(v)
        self.txt = txt if txt is not None else ftxt(self.v)

    def key(self):
        return str(self.v)


class X(Noeud):
    def key(self):
        return "x"


class E(Noeud):
    def key(self):
        return "e"


class Neg(Noeud):
    def __init__(self, a):
        self.a = a

    def key(self):
        return "(neg " + self.a.key() + ")"


class Op(Noeud):
    def __init__(self, op, a, b):
        self.op, self.a, self.b = op, a, b

    def key(self):
        if self.op == "^" and valeur_constante(self.b) == F(1, 2):
            return "(sqrt " + self.a.key() + ")"
        return "(" + self.op + " " + self.a.key() + " " + self.b.key() + ")"


class Fn(Noeud):
    def __init__(self, nom, a):
        self.nom, self.a = nom, a

    def key(self):
        return "(" + self.nom + " " + self.a.key() + ")"


def ftxt(q):
    q = F(q)
    return str(q.numerator) if q.denominator == 1 else f"{q.numerator}/{q.denominator}"


# =====================================================================
# 2. ANALYSE DE LA SAISIE
# =====================================================================
NOMS = ["sqrt", "racine", "exp", "log", "ln", "x", "e"]


def tokeniser(s):
    rempl = [("−", "-"), ("–", "-"), ("·", "*"), ("×", "*"), ("**", "^"), ("²", "^2"), ("³", "^3"),
             ("√", "sqrt"), ("{", "("), ("}", ")"), ("[", "("), ("]", ")"), (":", "/"), ("÷", "/")]
    for a, b in rempl:
        s = s.replace(a, b)
    toks, i = [], 0
    while i < len(s):
        c = s[i]
        if c.isspace():
            i += 1
            continue
        if c.isdigit() or (c in ".," and i + 1 < len(s) and s[i + 1].isdigit()):
            j = i
            while j < len(s) and s[j].isdigit():
                j += 1
            if j < len(s) and s[j] in ".," and j + 1 < len(s) and s[j + 1].isdigit():
                j += 1
                while j < len(s) and s[j].isdigit():
                    j += 1
            toks.append(("nb", s[i:j]))
            i = j
            continue
        if c.isalpha():
            for nm in NOMS:
                if s[i:i + len(nm)].lower() == nm:
                    toks.append(("nom", nm))
                    i += len(nm)
                    break
            else:
                raise ErreurSaisie(f"Symbole inconnu « {c} ». La variable s'appelle x ; "
                                   "fonctions permises : ln, exp, sqrt (ou e^…, √).")
            continue
        if c in "+-*/^()":
            toks.append(("op", c))
            i += 1
            continue
        raise ErreurSaisie(f"Caractère non reconnu : « {c} ».")
    return toks


class Parseur:
    def __init__(self, toks):
        self.t, self.i = toks, 0

    def voir(self):
        return self.t[self.i] if self.i < len(self.t) else (None, None)

    def manger(self, op):
        if self.voir() == ("op", op):
            self.i += 1
            return True
        return False

    def tout(self):
        if not self.t:
            raise ErreurSaisie("Entrez une expression, par exemple ln(x-1)/(x-3).")
        a = self.expr()
        if self.i < len(self.t):
            raise ErreurSaisie(f"Expression mal formée près de « {self.t[self.i][1]} ».")
        return a

    def expr(self):
        a = self.terme()
        while True:
            if self.manger("+"):
                a = Op("+", a, self.terme())
            elif self.manger("-"):
                a = Op("-", a, self.terme())
            else:
                return a

    def debut_primaire(self):
        k, v = self.voir()
        return k in ("nb", "nom") or (k, v) == ("op", "(")

    def terme(self):
        a = self.unaire()
        while True:
            if self.manger("*"):
                a = Op("*", a, self.unaire())
            elif self.manger("/"):
                a = Op("/", a, self.unaire())
            elif self.debut_primaire():
                a = Op("*", a, self.puissance())
            else:
                return a

    def unaire(self):
        if self.manger("-"):
            return Neg(self.unaire())
        if self.manger("+"):
            return self.unaire()
        return self.puissance()

    def puissance(self):
        b = self.primaire()
        if self.manger("^"):
            ex = self.unaire()
            if isinstance(b, E):
                return Fn("exp", ex)
            return Op("^", b, ex)
        return b

    def primaire(self):
        k, v = self.voir()
        if k == "nb":
            self.i += 1
            return Nb(F(v.replace(",", ".")), v)
        if k == "nom":
            self.i += 1
            if v == "x":
                return X()
            if v == "e":
                return E()
            nom = {"ln": "ln", "log": "ln", "exp": "exp", "sqrt": "sqrt", "racine": "sqrt"}[v]
            if self.manger("("):
                a = self.expr()
                if not self.manger(")"):
                    raise ErreurSaisie("Parenthèse fermante manquante.")
            else:
                if not self.debut_primaire():
                    raise ErreurSaisie(f"Il manque l'argument de {v}.")
                a = self.puissance()
            return Fn(nom, a)
        if self.manger("("):
            a = self.expr()
            if not self.manger(")"):
                raise ErreurSaisie("Parenthèse fermante manquante.")
            return a
        if k is None:
            raise ErreurSaisie("Expression incomplète.")
        raise ErreurSaisie(f"Symbole inattendu « {v} ».")


def lire(s):
    s = str(s).strip()
    if "=" in s:
        s = s.split("=")[-1]
    return Parseur(tokeniser(s)).tout()


def valeur_constante(n):
    """Valeur rationnelle d'un sous-arbre sans x ni e ; None sinon."""
    if isinstance(n, Nb):
        return n.v
    if isinstance(n, Neg):
        v = valeur_constante(n.a)
        return None if v is None else -v
    if isinstance(n, Op):
        a, b = valeur_constante(n.a), valeur_constante(n.b)
        if a is None or b is None:
            return None
        if n.op == "+":
            return a + b
        if n.op == "-":
            return a - b
        if n.op == "*":
            return a * b
        if n.op == "/":
            return None if b == 0 else a / b
        if n.op == "^":
            if b.denominator == 1 and not (a == 0 and b < 0) and abs(b) <= 64:
                return a ** int(b)
            return None
    return None


# =====================================================================
# 3. ÉCRITURE LaTeX
# =====================================================================
def prec(n):
    if isinstance(n, Op):
        return {"+": 1, "-": 1, "*": 2, "/": 2, "^": 3}[n.op]
    if isinstance(n, Neg):
        return 1.5
    if isinstance(n, Fn) and n.nom == "exp":
        return 3
    return 4


def par(n, mini):
    t = tex(n)
    return r"\left(" + t + r"\right)" if prec(n) < mini else t


def tex(n):
    if isinstance(n, Nb):
        return n.txt.replace(",", "{,}").replace(".", "{,}")
    if isinstance(n, X):
        return "x"
    if isinstance(n, E):
        return "e"
    if isinstance(n, Neg):
        return "-" + par(n.a, 2)
    if isinstance(n, Fn):
        if n.nom == "ln":
            a = tex(n.a)
            return r"\ln(" + a + ")" if isinstance(n.a, (X, Nb)) else r"\ln\left(" + a + r"\right)"
        if n.nom == "exp":
            return "e^{" + tex(n.a) + "}"
        return r"\sqrt{" + tex(n.a) + "}"
    if n.op == "+":
        if isinstance(n.b, Neg):
            return tex(n.a) + " - " + par(n.b.a, 2)
        return tex(n.a) + " + " + tex(n.b)
    if n.op == "-":
        return tex(n.a) + " - " + par(n.b, 2)
    if n.op == "/":
        return r"\frac{" + tex(n.a) + "}{" + tex(n.b) + "}"
    if n.op == "*":
        g, d = par(n.a, 1.5), par(n.b, 2)
        if d[:1].isdigit() or d[:1] == "-":
            sep = r" \cdot "
        elif isinstance(n.a, Nb) or (isinstance(n.a, Neg) and isinstance(n.a.a, Nb)):
            sep = ""
        else:
            sep = r"\,"
        return g + sep + d
    # puissance
    if valeur_constante(n.b) == F(1, 2):
        return r"\sqrt{" + tex(n.a) + "}"
    base = n.a
    atome = isinstance(base, (X, E)) or (isinstance(base, Nb) and base.v.denominator == 1 and base.v >= 0)
    bt = tex(base) if atome else r"\left(" + tex(base) + r"\right)"
    return bt + "^{" + tex(n.b) + "}"


# =====================================================================
# 4. POLYNÔMES ET FRACTIONS RATIONNELLES (coefficients rationnels exacts)
# =====================================================================
def pn(p):
    p = list(p)
    while len(p) > 1 and p[-1] == 0:
        p.pop()
    return p or [F(0)]


def deg(p):
    p = pn(p)
    return 0 if (len(p) == 1) else len(p) - 1


def nul(p):
    p = pn(p)
    return len(p) == 1 and p[0] == 0


def padd(p, q):
    n = max(len(p), len(q))
    return pn([(p[i] if i < len(p) else 0) + (q[i] if i < len(q) else 0) for i in range(n)])


def pscal(p, c):
    return pn([F(a) * c for a in p])


def pmul(p, q):
    r = [F(0)] * (len(p) + len(q) - 1)
    for i, a in enumerate(p):
        for j, b in enumerate(q):
            r[i + j] += a * b
    return pn(r)


def peval(p, x):
    s = 0
    for a in reversed(p):
        s = s * x + a
    return s


def pdivlin(p, r):
    """Division de p par (v - r) : (quotient, reste)."""
    n = len(p) - 1
    q = [F(0)] * n
    acc = F(0)
    for i in range(n, 0, -1):
        acc = acc * r + p[i]
        q[i - 1] = acc
    reste = acc * r + p[0]
    return pn(q), reste


def ptex(p, v):
    p = pn(p)
    termes = []
    for k in range(len(p) - 1, -1, -1):
        c = p[k]
        if c == 0:
            continue
        mono = "" if k == 0 else (v if k == 1 else f"{v}^{{{k}}}")
        a = abs(c)
        if mono and a == 1:
            coef = ""
        else:
            coef = qtex(a)
        termes.append(("-" if c < 0 else "+", coef + mono))
    if not termes:
        return "0"
    s = ("-" if termes[0][0] == "-" else "") + termes[0][1]
    for sg, t in termes[1:]:
        s += f" {sg} {t}"
    return s


def qtex(q):
    q = F(q)
    if q.denominator == 1:
        return str(q.numerator)
    s = r"\frac{" + str(abs(q.numerator)) + "}{" + str(q.denominator) + "}"
    return "-" + s if q < 0 else s


# fraction rationnelle = (num, den)
def r_const(c):
    return ([F(c)], [F(1)])


def r_add(a, b):
    return (padd(pmul(a[0], b[1]), pmul(b[0], a[1])), pmul(a[1], b[1]))


def r_neg(a):
    return (pscal(a[0], -1), a[1])


def r_mul(a, b):
    return (pmul(a[0], b[0]), pmul(a[1], b[1]))


def r_div(a, b):
    if nul(b[0]):
        raise ErreurSaisie("Division par zéro dans l'expression.")
    return (pmul(a[0], b[1]), pmul(a[1], b[0]))


def r_pow(a, k):
    r = r_const(1)
    for _ in range(abs(k)):
        r = r_mul(r, a)
    return r if k >= 0 else r_div(r_const(1), r)


def r_norm(R):
    n, d = pn(R[0]), pn(R[1])
    c = d[-1]
    n, d = pscal(n, 1 / c), pscal(d, 1 / c)
    # simplification par les puissances de v communes (toujours nulles au même endroit : sans effet
    # sur le signe ni sur les valeurs interdites, on les garde donc) ; on ne simplifie que les constantes
    return (n, d)


def rtex(R, v):
    n, d = r_norm(R)
    if deg(d) == 0:
        return ptex(n, v)
    return r"\frac{" + ptex(n, v) + "}{" + ptex(d, v) + "}"


def est_identite(R):
    n, d = r_norm(R)
    return deg(d) == 0 and pn(n) == [0, 1]


def est_affine(R):
    n, d = r_norm(R)
    return deg(d) == 0 and deg(n) == 1


# =====================================================================
# 5. NOMBRES RÉELS EXACTS (affichage exact, comparaison numérique)
# =====================================================================
class Num:
    def __init__(self, val, tex, q=None, genre="gen", data=None, approx=False):
        self.val, self.tex, self.q, self.genre, self.data, self.approx = val, tex, q, genre, data, approx

    @staticmethod
    def rat(q):
        q = F(q)
        return Num(float(q), qtex(q), q=q, genre="rat")

    @staticmethod
    def quad(a, b, m):
        """a + b·√m (m sans facteur carré, > 1)."""
        a, b = F(a), F(b)
        d = a.denominator * b.denominator // math.gcd(a.denominator, b.denominator)
        A, B = int(a * d), int(b * d)
        rac = ("" if abs(B) == 1 else str(abs(B))) + r"\sqrt{" + str(m) + "}"
        if A == 0:
            s = ("-" if B < 0 else "") + rac
        else:
            s = str(A) + (" - " if B < 0 else " + ") + rac
        if d != 1:
            s = r"\frac{" + s + "}{" + str(d) + "}"
        return Num(float(a) + float(b) * math.sqrt(m), s, genre="quad", data=(a, b, m))


def proche(a, b):
    return abs(a - b) <= 1e-9 * (1 + abs(a) + abs(b))


def exp_de(n):
    if n.q is not None:
        if n.q == 0:
            return Num.rat(1)
        t = "e" if n.q == 1 else "e^{" + n.tex + "}"
        return Num(math.exp(n.val), t, genre="exp", data=n)
    if n.genre == "ln":
        return n.data
    return Num(math.exp(n.val), "e^{" + n.tex + "}", genre="exp", data=n)


def ln_de(n):
    if n.genre == "exp":
        return n.data
    if n.q is not None:
        q = n.q
        if q == 1:
            return Num.rat(0)
        if q.numerator == 1:
            return Num(math.log(n.val), r"-\ln(" + str(q.denominator) + ")", genre="ln", data=Num.rat(1 / q))
        t = r"\ln(" + str(q.numerator) + ")" if q.denominator == 1 else r"\ln\left(" + n.tex + r"\right)"
        return Num(math.log(n.val), t, genre="ln", data=n)
    return Num(math.log(n.val), r"\ln\left(" + n.tex + r"\right)", genre="ln", data=n)


def carre(n):
    if n.q is not None:
        return Num.rat(n.q * n.q)
    if n.genre == "quad":
        a, b, m = n.data
        if a == 0:
            return Num.rat(b * b * m)
        return Num.quad(a * a + b * b * m, 2 * a * b, m)
    if n.genre == "exp" and n.data.q is not None:
        return exp_de(Num.rat(2 * n.data.q))
    return Num(n.val ** 2, r"\left(" + n.tex + r"\right)^{2}", approx=n.approx)


def affine_inv(n, m, b):
    """x tel que m·x + b = n."""
    m, b = F(m), F(b)
    if n.q is not None:
        return Num.rat((n.q - b) / m)
    if n.genre == "quad":
        a, c, r = n.data
        return Num.quad((a - b) / m, c / m, r)
    val = (n.val - float(b)) / float(m)
    if n.approx:
        return Num(val, dec(val), approx=True)
    if m < 0:
        m, b, signe = -m, -b, "-"
    else:
        signe = ""
    t = n.tex
    if b > 0:
        t = t + " - " + qtex(b)
    elif b < 0:
        t = t + " + " + qtex(-b)
    if m == 1:
        if signe:
            t = "-" + (r"\left(" + t + r"\right)" if b != 0 else t)
    else:
        if signe:
            t = (r"\frac{" + qtex(-b) + " - " + n.tex + "}{" + qtex(m) + "}") if b != 0 else \
                (r"-\frac{" + n.tex + "}{" + qtex(m) + "}")
        else:
            t = r"\frac{" + t + "}{" + qtex(m) + "}"
    return Num(val, t)


def dec(v):
    return (f"{v:.4f}".rstrip("0").rstrip(".")).replace(".", "{,}")


def squarefree(n):
    """n = k²·m avec m sans facteur carré ; renvoie (k, m)."""
    k, m, f = 1, n, 2
    while f * f <= m:
        while m % (f * f) == 0:
            m //= f * f
            k *= f
        f += 1
    return k, m


def racine_q(q):
    """√q exacte si q est un carré rationnel, sinon (k, m) avec √q = k·√m."""
    q = F(q)
    p, d = q.numerator * q.denominator, q.denominator
    k, m = squarefree(p)
    return F(k, d), m   # √q = (k/d)·√m


# =====================================================================
# 6. ENSEMBLES (réunions d'intervalles)
# =====================================================================
class Iv:
    def __init__(self, lo, lf, hi, hf):
        self.lo, self.lf, self.hi, self.hf = lo, lf, hi, hf   # lo/hi : Num ou None (= ∓∞)


def vlo(iv):
    return -math.inf if iv.lo is None else iv.lo.val


def vhi(iv):
    return math.inf if iv.hi is None else iv.hi.val


def vide(iv):
    a, b = vlo(iv), vhi(iv)
    if iv.lo is not None and iv.hi is not None and proche(a, b):
        return not (iv.lf and iv.hf)
    return a > b


def fusion(L):
    L = [iv for iv in L if not vide(iv)]
    L.sort(key=lambda iv: (vlo(iv), 0 if iv.lf else 1))
    out = []
    for iv in L:
        if out:
            c = out[-1]
            touche = c.hi is not None and iv.lo is not None and proche(vhi(c), vlo(iv))
            if (vlo(iv) < vhi(c) and not touche) or (touche and (c.hf or iv.lf)) or c.hi is None:
                if iv.hi is None or (c.hi is not None and (vhi(iv) > vhi(c) and not proche(vhi(iv), vhi(c)))):
                    c.hi, c.hf = iv.hi, iv.hf
                elif c.hi is not None and iv.hi is not None and proche(vhi(iv), vhi(c)):
                    c.hf = c.hf or iv.hf
                continue
        out.append(Iv(iv.lo, iv.lf, iv.hi, iv.hf))
    return out


def inter(A, B):
    out = []
    for a in A:
        for b in B:
            if a.lo is None:
                lo, lf = b.lo, b.lf
            elif b.lo is None:
                lo, lf = a.lo, a.lf
            elif proche(a.lo.val, b.lo.val):
                lo, lf = a.lo, a.lf and b.lf
            else:
                lo, lf = (a.lo, a.lf) if a.lo.val > b.lo.val else (b.lo, b.lf)
            if a.hi is None:
                hi, hf = b.hi, b.hf
            elif b.hi is None:
                hi, hf = a.hi, a.hf
            elif proche(a.hi.val, b.hi.val):
                hi, hf = a.hi, a.hf and b.hf
            else:
                hi, hf = (a.hi, a.hf) if a.hi.val < b.hi.val else (b.hi, b.hf)
            out.append(Iv(lo, lf, hi, hf))
    return fusion(out)


def union(A, B):
    return fusion(list(A) + list(B))


def complement(A):
    A = fusion(A)
    out, lo, lf = [], None, False
    for iv in A:
        if iv.lo is not None:
            out.append(Iv(lo, lf, iv.lo, not iv.lf))
        if iv.hi is None:
            return fusion(out)
        lo, lf = iv.hi, not iv.hf
    out.append(Iv(lo, lf, None, False))
    return fusion(out)


REELS = [Iv(None, False, None, False)]
GE, LE, SEP = r"\geq", r"\leq", r" \,;\, "


def points(L):
    return fusion([Iv(p, True, p, True) for p in L])


def ens_tex(S):
    S = fusion(S)
    if not S:
        return r"\varnothing"
    if S[0].lo is None and S[-1].hi is None and all(
            S[i].hi is not None and S[i + 1].lo is not None and proche(S[i].hi.val, S[i + 1].lo.val)
            and not S[i].hf and not S[i + 1].lf for i in range(len(S) - 1)):
        if len(S) == 1:
            return r"\mathbb{R}"
        return r"\mathbb{R} \setminus \left\{" + r" \,;\, ".join(S[i].hi.tex for i in range(len(S) - 1)) + r"\right\}"
    morceaux = []
    for iv in S:
        if iv.lo is not None and iv.hi is not None and proche(iv.lo.val, iv.hi.val):
            morceaux.append(r"\left\{" + iv.lo.tex + r"\right\}")
            continue
        g = r"\left]-\infty" if iv.lo is None else ((r"\left[" if iv.lf else r"\left]") + iv.lo.tex)
        d = r"+\infty\right[" if iv.hi is None else (iv.hi.tex + (r"\right]" if iv.hf else r"\right["))
        morceaux.append(g + r" \,;\, " + d)
    return r" \cup ".join(morceaux)


def contrainte_tex(expr, S):
    """Écrit « expr ∈ S » sous la forme la plus lisible (> a, ≥ a, = a, ≠ a…)."""
    S = fusion(S)
    if len(S) == 1:
        iv = S[0]
        if iv.lo is not None and iv.hi is None:
            return f"{expr} {GE if iv.lf else '>'} {iv.lo.tex}"
        if iv.lo is None and iv.hi is not None:
            return f"{expr} {LE if iv.hf else '<'} {iv.hi.tex}"
        if iv.lo is not None and iv.hi is not None and proche(iv.lo.val, iv.hi.val):
            return f"{expr} = {iv.lo.tex}"
        if iv.lo is not None and iv.hi is not None:
            return f"{iv.lo.tex} {LE if iv.lf else '<'} {expr} {LE if iv.hf else '<'} {iv.hi.tex}"
        return f"{expr} \\in \\mathbb{{R}}"
    if not S:
        return f"{expr} \\in \\varnothing"
    if all(iv.lo is not None and iv.hi is not None and proche(iv.lo.val, iv.hi.val) for iv in S):
        return f"{expr} \\in \\left\\{{{' \\,;\\, '.join(iv.lo.tex for iv in S)}\\right\\}}"
    return f"{expr} \\in {ens_tex(S)}"


# =====================================================================
# 7. FACTORISATION AVEC EXPLICATIONS
# =====================================================================
def racine_rationnelle(Q):
    den = 1
    for a in Q:
        den = den * a.denominator // math.gcd(den, a.denominator)
    P = [int(a * den) for a in Q]
    if P[0] == 0:
        return F(0)
    a0, an = abs(P[0]), abs(P[-1])
    if a0 > 10 ** 6 or an > 10 ** 6:
        return None
    divs = lambda n: [d for d in range(1, n + 1) if n % d == 0]
    for p in divs(a0):
        for q in divs(an):
            for s in (1, -1):
                r = F(s * p, q)
                if peval(Q, r) == 0:
                    return r
    return None


def racines_numeriques(Q):
    """Racines réelles approchées d'un polynôme (Durand–Kerner puis Newton)."""
    n = deg(Q)
    c = [complex(float(a)) for a in Q]
    c = [a / c[-1] for a in c]
    z = [(0.4 + 0.9j) ** k for k in range(n)]
    f = lambda x: sum(c[i] * x ** i for i in range(n + 1))
    for _ in range(800):
        nz = []
        for i in range(n):
            den = 1
            for j in range(n):
                if j != i:
                    den *= (z[i] - z[j])
            nz.append(z[i] - f(z[i]) / den if den != 0 else z[i])
        z = nz
    res = []
    for w in z:
        if abs(w.imag) < 1e-6 * (1 + abs(w)):
            x = w.real
            for _ in range(50):
                fx = sum(float(Q[i]) * x ** i for i in range(n + 1))
                dfx = sum(i * float(Q[i]) * x ** (i - 1) for i in range(1, n + 1))
                if dfx == 0:
                    break
                x -= fx / dfx
            if not any(proche(x, y) for y in res):
                res.append(x)
    return sorted(res)


def facteur(poly, v, racines, mult=1):
    t = ptex(poly, v)
    if mult > 1:
        t = r"\left(" + t + r"\right)^{" + str(mult) + "}"
    return {"poly": pscal(pn(poly), 1), "mult": mult, "tex": t, "racines": racines}


def factoriser(P, v):
    """Renvoie (constante c, facteurs, lignes d'explication) avec P = c·∏ facteurs."""
    P = pn(P)
    n = deg(P)
    lignes = []
    if n == 0:
        return P[0], [], lignes
    if n == 1:
        r = -P[0] / P[1]
        lignes.append(rf"\({ptex(P, v)} = 0 \iff {v} = {qtex(r)}\)")
        return F(1), [facteur(P, v, [Num.rat(r)])], lignes
    if n == 2 and P[0] != 0:
        return trinome(P, v, lignes, entier=True)
    c = P[-1]
    Q = pscal(P, 1 / c)
    facteurs = []
    k = 0
    while Q[0] == 0:
        Q = pn(Q[1:])
        k += 1
    if k:
        facteurs.append(facteur([F(0), F(1)], v, [Num.rat(0)], k))
        lignes.append(rf"On met \({v}^{{{k}}}\) en évidence : \({ptex(P, v)} = "
                      rf"{v}^{{{k}}}\left({ptex(pscal(Q, c), v)}\right)\)" if k > 1 else
                      rf"On met \({v}\) en évidence : \({ptex(P, v)} = {v}\left({ptex(pscal(Q, c), v)}\right)\)")
    while deg(Q) >= 3:
        r = racine_rationnelle(Q)
        if r is None:
            break
        m = 0
        while deg(Q) >= 1 and peval(Q, r) == 0:
            Q, _ = pdivlin(Q, r)
            m += 1
        facteurs.append(facteur([-r, F(1)], v, [Num.rat(r)], m))
        lignes.append(rf"Racine évidente \({v} = {qtex(r)}\)" + (f" (d'ordre {m})" if m > 1 else "") +
                      rf" ; on divise par \({ptex([-r, F(1)], v)}\) : il reste \({ptex(pscal(Q, c), v)}\).")
    d = deg(Q)
    if d == 1:
        r = -Q[0]
        facteurs.append(facteur(Q, v, [Num.rat(r)]))
        lignes.append(rf"\({ptex(Q, v)} = 0 \iff {v} = {qtex(r)}\)")
    elif d == 2:
        cc, ff, ll = trinome(Q, v, [], entier=False)
        facteurs += ff
        lignes += ll
    elif d >= 3:
        rs = racines_numeriques(Q)
        nums = [Num(x, dec(x), approx=True) for x in rs]
        facteurs.append(facteur(Q, v, nums))
        lignes.append(rf"\({ptex(Q, v)}\) n'a pas de racine rationnelle : zéros approchés "
                      + (", ".join(rf"\({v} \approx {x.tex}\)" for x in nums) if nums else "aucun zéro réel") + ".")
    return c, facteurs, lignes


def trinome(P, v, lignes, entier):
    c0, b, a = P[0], P[1], P[2]
    D = b * b - 4 * a * c0
    T = ptex(P, v)
    lignes.append(rf"Trinôme \({T}\) : \(\Delta = b^2 - 4ac = {par_q(b)}^2 - 4 \cdot {par_q(a)} \cdot {par_q(c0)} = {qtex(D)}\)")
    if D < 0:
        signe = "positif" if a > 0 else "négatif"
        lignes.append(rf"\(\Delta < 0\) : aucun zéro ; le trinôme garde le signe de \(a = {qtex(a)}\), il est toujours {signe}.")
        return F(1), [facteur(P, v, [])], lignes
    if D == 0:
        r = -b / (2 * a)
        lignes.append(rf"\(\Delta = 0\) : zéro double \({v} = \frac{{-b}}{{2a}} = {qtex(r)}\), et \({T} = {mono_c(a)}\left({ptex([-r, F(1)], v)}\right)^{{2}}\).")
        return a, [facteur([-r, F(1)], v, [Num.rat(r)], 2)], lignes
    k, m = racine_q(D)
    if m == 1:
        r1, r2 = sorted([(-b - k) / (2 * a), (-b + k) / (2 * a)])
        lignes.append(rf"\(\Delta > 0\), \(\sqrt{{\Delta}} = {qtex(k)}\) : deux zéros \({v}_1 = \frac{{-b - \sqrt{{\Delta}}}}{{2a}} = {qtex(r1)}\) "
                      rf"et \({v}_2 = \frac{{-b + \sqrt{{\Delta}}}}{{2a}} = {qtex(r2)}\).")
        return a, [facteur([-r1, F(1)], v, [Num.rat(r1)]), facteur([-r2, F(1)], v, [Num.rat(r2)])], lignes
    x1 = Num.quad(-b / (2 * a), -k / (2 * a), m)
    x2 = Num.quad(-b / (2 * a), k / (2 * a), m)
    x1, x2 = sorted([x1, x2], key=lambda z: z.val)
    lignes.append(rf"\(\Delta > 0\) : deux zéros \({v}_1 = \frac{{-b - \sqrt{{\Delta}}}}{{2a}} = {x1.tex}\) "
                  rf"et \({v}_2 = {x2.tex}\) \((\approx {dec(x1.val)}\) et \(\approx {dec(x2.val)})\).")
    return F(1), [facteur(P, v, [x1, x2])], lignes


def par_q(q):
    t = qtex(q)
    return "(" + t + ")" if q < 0 or q.denominator != 1 else t


def mono_c(a):
    return "" if a == 1 else ("-" if a == -1 else qtex(a))


# =====================================================================
# 8. TABLEAU DE SIGNES ET RÉSOLUTION D'UNE CONDITION RATIONNELLE
# =====================================================================
def sg(x):
    return "+" if x > 0 else "-"


def resoudre_rat(R, rel, v, items, nom_expr=None):
    """Ensemble des v tels que R(v) rel 0, rel ∈ {'>', '>=', '='}. Ajoute les explications à items."""
    N, D = r_norm(R)
    N, D = pn(N), pn(D)
    expr = nom_expr or rtex((N, D), v)
    if nul(N):
        z = []
        if deg(D) > 0:
            _, fD, _ = factoriser(D, v)
            z = [r for f in fD for r in f["racines"]]
        if rel == ">":
            items.append(txt(rf"\({expr}\) est nulle : la condition \(> 0\) n'est jamais vraie."))
            return []
        items.append(txt(rf"\({expr}\) est nulle partout où elle est définie."))
        return complement(points(z))
    cN, fN, lN = factoriser(N, v)
    if deg(D) > 0:
        cD, fD, lD = factoriser(D, v)
    else:
        cD, fD, lD = D[0], [], []
    const = cN / cD
    zN = [r for f in fN for r in f["racines"]]
    zD = [r for f in fD for r in f["racines"]]

    if rel == "=":
        if deg(N) == 0:
            items.append(txt(rf"Le numérateur vaut \({qtex(N[0])} \neq 0\) : aucune solution."))
            return []
        if fD:
            items.append(txt(rf"Une fraction est nulle lorsque son numérateur est nul (et son dénominateur non nul) : "
                             rf"on résout \({ptex(N, v)} = 0\)."))
        else:
            items.append(txt(rf"On résout \({ptex(N, v)} = 0\)."))
        for l in lN:
            items.append(txt(l))
        sols = []
        for z in zN:
            if any(proche(z.val, w.val) for w in zD):
                items.append(txt(rf"\({v} = {z.tex}\) annule aussi le dénominateur : elle est exclue."))
            elif not any(proche(z.val, s.val) for s in sols):
                sols.append(z)
        sols.sort(key=lambda z: z.val)
        if sols:
            items.append(txt(("Solution : " if len(sols) == 1 else "Solutions : ") +
                             ", ".join(rf"\({v} = {z.tex}\)" for z in sols) + "."))
        else:
            items.append(txt("Aucune solution réelle."))
        return points(sols)

    # inéquation : tableau de signes
    if deg(N) == 0 and deg(D) == 0:
        ok = const > 0 or (rel == ">=" and const == 0)
        items.append(txt(rf"\({expr}\) est constante, égale à \({qtex(const)}\) : la condition est "
                         + ("toujours vraie." if ok else "toujours fausse.")))
        return REELS if ok else []
    if lN:
        items.append(txt("Zéros du numérateur :" if fD else "Zéros :"))
        for l in lN:
            items.append(txt(l))
    if lD:
        items.append(txt("Zéros du dénominateur (valeurs interdites, marquées ‖) :"))
        for l in lD:
            items.append(txt(l))
    crit = []
    for z in zN + zD:
        if not any(proche(z.val, c.val) for c in crit):
            crit.append(z)
    crit.sort(key=lambda z: z.val)
    k = len(crit)

    def test(i):
        if k == 0:
            return 0.0
        if i == 0:
            return crit[0].val - 1
        if i == k:
            return crit[-1].val + 1
        return (crit[i - 1].val + crit[i].val) / 2

    lignes = []
    tous = [(f, False) for f in fN] + [(f, True) for f in fD]
    if const < 0:
        lignes.append({"label": qtex(const), "cells": cellules(lambda x: float(const), [], k, test, crit)})
    for f, est_den in tous:
        poly = f["poly"]
        mult = f["mult"]
        fn = (lambda p, m: (lambda x: float(peval(p, x)) ** m))(poly, mult)
        lignes.append({"label": f["tex"], "cells": cellules(fn, f["racines"], k, test, crit)})
    # ligne finale
    fin = []
    for i in range(k + 1):
        x = test(i)
        val = float(const)
        for f, est_den in tous:
            y = float(peval(f["poly"], x)) ** f["mult"]
            val = val / y if est_den else val * y
        fin.append(sg(val))
        if i < k:
            c = crit[i]
            if any(proche(c.val, z.val) for z in zD):
                fin.append("||")
            elif any(proche(c.val, z.val) for z in zN):
                fin.append("0")
            else:
                fin.append("?")
    if len(tous) + (1 if const < 0 else 0) > 1 or fD:
        lignes.append({"label": expr, "cells": fin, "final": True})
    else:
        lignes[-1]["final"] = True
        lignes[-1]["label"] = expr if (deg(D) == 0 and const > 0 and len(tous) == 1) else lignes[-1]["label"]
    items.append({"type": "tableau", "var": v, "crit": [c.tex for c in crit], "rows": lignes})

    S = []
    for i in range(k + 1):
        if fin[2 * i] == "+":
            lo = crit[i - 1] if i > 0 else None
            hi = crit[i] if i < k else None
            S.append(Iv(lo, False, hi, False))
        if i < k and rel == ">=" and fin[2 * i + 1] == "0":
            S.append(Iv(crit[i], True, crit[i], True))
    S = fusion(S)
    symb = ">" if rel == ">" else r"\geq"
    items.append(txt(rf"On lit les intervalles où \({expr} {symb} 0\)" +
                     (" (les zéros sont inclus, les valeurs interdites exclues)" if rel == ">=" and zD else
                      " (zéros inclus)" if rel == ">=" else "") +
                     rf" : \({v} \in {ens_tex(S)}\)."))
    return S


def cellules(fn, racines, k, test, crit):
    out = []
    for i in range(k + 1):
        out.append(sg(fn(test(i))))
        if i < k:
            c = crit[i]
            out.append("0" if any(proche(c.val, r.val) for r in racines) else sg(fn(c.val)))
    return out


def txt(s):
    return {"type": "texte", "html": s}


# =====================================================================
# 9. SUBSTITUTION t = ln(B), e^B, √B ET RETOUR À x
# =====================================================================
def cle_atome(n):
    if isinstance(n, Op):     # puissance 1/2
        return "sqrt", n.a
    return n.nom, n.a


def est_atome(n):
    return isinstance(n, Fn) or (isinstance(n, Op) and n.op == "^" and valeur_constante(n.b) == F(1, 2))


def collecter(n, acc):
    if isinstance(n, X):
        acc["x"] = True
    elif isinstance(n, E):
        raise NonPrisEnCharge("la constante e apparaît seule dans la condition (coefficient irrationnel).")
    elif est_atome(n):
        acc["at"].append(n)
    elif isinstance(n, Neg):
        collecter(n.a, acc)
    elif isinstance(n, Op):
        if n.op == "^":
            e = valeur_constante(n.b)
            if e is None or e.denominator != 1:
                raise NonPrisEnCharge("puissance non entière (autre que 1/2) dans la condition.")
            collecter(n.a, acc)
        else:
            collecter(n.a, acc)
            collecter(n.b, acc)


def en_rationnelle(n, atomf):
    if isinstance(n, Nb):
        return r_const(n.v)
    if isinstance(n, X) or est_atome(n):
        return atomf(n)
    if isinstance(n, Neg):
        return r_neg(en_rationnelle(n.a, atomf))
    a = en_rationnelle(n.a, atomf)
    if n.op == "^":
        return r_pow(a, int(valeur_constante(n.b)))
    b = en_rationnelle(n.b, atomf)
    return {"+": r_add, "-": lambda p, q: r_add(p, r_neg(q)), "*": r_mul, "/": r_div}[n.op](a, b)


def decomposer(n):
    """('x', R) si n est rationnelle en x ; ('t', genre, B, R, t_tex) si n = R(t) avec t = ln(B), e^B ou √B."""
    acc = {"x": False, "at": []}
    collecter(n, acc)
    X_R = ([F(0), F(1)], [F(1)])
    if not acc["at"]:
        return ("x", en_rationnelle(n, lambda a: X_R))
    if acc["x"]:
        raise NonPrisEnCharge("la condition mélange x et une fonction ln, exp ou racine de x "
                              "(équation transcendante : pas de résolution exacte).")
    genres = {cle_atome(a)[0] for a in acc["at"]}
    if len(genres) > 1:
        raise NonPrisEnCharge("la condition mélange plusieurs fonctions (ln, exp, racine).")
    genre = genres.pop()
    cles = {cle_atome(a)[1].key() for a in acc["at"]}
    if len(cles) == 1:
        B = cle_atome(acc["at"][0])[1]
        t_tex = {"ln": r"\ln\left(" + tex(B) + r"\right)" if not isinstance(B, (X, Nb)) else r"\ln(" + tex(B) + ")",
                 "exp": "e^{" + tex(B) + "}", "sqrt": r"\sqrt{" + tex(B) + "}"}[genre]
        R = en_rationnelle(n, lambda a: ([F(0), F(1)], [F(1)]))
        return ("t", genre, B, R, t_tex)
    if genre == "exp":
        coefs = {}
        for a in acc["at"]:
            B = a.a
            try:
                RB = r_norm(decomposer(B)[1]) if decomposer(B)[0] == "x" else None
            except NonPrisEnCharge:
                RB = None
            if RB is None or deg(RB[1]) != 0 or deg(RB[0]) != 1 or RB[0][0] != 0:
                raise NonPrisEnCharge("exponentielles d'arguments différents non proportionnels.")
            coefs[B.key()] = RB[0][1] / RB[1][0]
        num = 0
        den = 1
        for c in coefs.values():
            num = math.gcd(num, c.numerator)
            den = den * c.denominator // math.gcd(den, c.denominator)
        g = F(num, den)
        Bg = X() if g == 1 else Op("*", Nb(g), X())
        if g == -1:
            Bg = Neg(X())

        def atomf(a):
            p = coefs[a.a.key()] / g
            return r_pow(([F(0), F(1)], [F(1)]), int(p))
        R = en_rationnelle(n, atomf)
        return ("t", "exp", Bg, R, "e^{" + tex(Bg) + "}")
    raise NonPrisEnCharge("plusieurs logarithmes ou racines d'arguments différents dans la même condition.")


INFO = {
    "ln": ("t = {t}", r"\ln", "exponentielle"),
    "exp": ("t = {t}", "e", "logarithme"),
    "sqrt": ("t = {t}", r"\sqrt{}", "carré"),
}


def retour_atome(genre, S, t_tex, B_tex, items):
    """{B : φ(B) ∈ S} où φ = ln, exp ou √ (fonctions strictement croissantes)."""
    S = fusion(S)
    if genre == "ln":
        out = []
        for iv in S:
            lo = Num.rat(0) if iv.lo is None else exp_de(iv.lo)
            lf = False if iv.lo is None else iv.lf
            hi = None if iv.hi is None else exp_de(iv.hi)
            out.append(Iv(lo, lf, hi, iv.hf))
        out = fusion(out)
        if all(iv.lo is not None and iv.hi is not None and proche(iv.lo.val, iv.hi.val) for iv in S) and S:
            for iv in S:
                items.append(txt(rf"\({t_tex} = {iv.lo.tex} \iff {B_tex} = {exp_de(iv.lo).tex}\)"))
        else:
            items.append(txt(rf"L'exponentielle est strictement croissante et \(\ln\) n'est définie que sur "
                             rf"\(\left]0 \,;\, +\infty\right[\) : \({contrainte_tex(t_tex, S)} \iff {contrainte_tex(B_tex, out)}\)."))
        return out
    if genre == "exp":
        pos = [Iv(Num.rat(0), False, None, False)]
        ok = inter(S, pos)
        pts = all(iv.lo is not None and iv.hi is not None and proche(iv.lo.val, iv.hi.val) for iv in S) and S
        if pts:
            for iv in S:
                if iv.lo.val <= 0:
                    items.append(txt(rf"\({t_tex} = {iv.lo.tex}\) est impossible, car \({t_tex} > 0\) pour tout réel : solution rejetée."))
        elif len(ok) != len(S) or any(vlo(a) != vlo(b) for a, b in zip(ok, S)):
            items.append(txt(rf"Comme \({t_tex} > 0\) pour tout réel, on ne garde que \({t_tex} \in {ens_tex(ok)}\)."))
        out = []
        for iv in ok:
            lo = None if proche(iv.lo.val, 0) else ln_de(iv.lo)
            lf = False if lo is None else iv.lf
            hi = None if iv.hi is None else ln_de(iv.hi)
            out.append(Iv(lo, lf, hi, iv.hf))
        out = fusion(out)
        if pts:
            for iv in ok:
                items.append(txt(rf"\({t_tex} = {iv.lo.tex} \iff {B_tex} = {ln_de(iv.lo).tex}\)"))
        elif ok:
            items.append(txt(rf"Le logarithme est strictement croissant : \({contrainte_tex(t_tex, ok)} \iff {contrainte_tex(B_tex, out)}\)."))
        return out
    # racine carrée
    pos = [Iv(Num.rat(0), True, None, False)]
    ok = inter(S, pos)
    pts = all(iv.lo is not None and iv.hi is not None and proche(iv.lo.val, iv.hi.val) for iv in S) and S
    if pts:
        for iv in S:
            if iv.lo.val < 0:
                items.append(txt(rf"\({t_tex} = {iv.lo.tex}\) est impossible, car une racine carrée est positive ou nulle : solution rejetée."))
    out = fusion([Iv(iv.lo and carre(iv.lo), iv.lf, None if iv.hi is None else carre(iv.hi), iv.hf) for iv in ok])
    if ok:
        if pts:
            for iv in ok:
                items.append(txt(rf"\({t_tex} = {iv.lo.tex} \iff {B_tex} = {carre(iv.lo).tex}\)"))
        else:
            items.append(txt(rf"Une racine carrée est positive et la fonction carré est croissante sur \(\left[0 \,;\, +\infty\right[\) : "
                             rf"\({contrainte_tex(t_tex, ok)} \iff {contrainte_tex(B_tex, out)}\)."))
    return out


def resoudre_dans(R, S, v, expr_tex, items):
    """{v : R(v) ∈ S}."""
    S = fusion(S)
    if est_identite(R):
        return S
    n, d = r_norm(R)
    if est_affine(R):
        m, b = n[1] / d[0], n[0] / d[0]
        out = []
        for iv in S:
            lo = None if iv.lo is None else affine_inv(iv.lo, m, b)
            hi = None if iv.hi is None else affine_inv(iv.hi, m, b)
            if m > 0:
                out.append(Iv(lo, iv.lf, hi, iv.hf))
            else:
                out.append(Iv(hi, iv.hf, lo, iv.lf))
        out = fusion(out)
        rem = " (on divise par un nombre négatif : le sens s'inverse)" if m < 0 and not all(
            iv.lo is not None and iv.hi is not None and proche(iv.lo.val, iv.hi.val) for iv in S) else ""
        items.append(txt(rf"\({contrainte_tex(expr_tex, S)} \iff {contrainte_tex(v, out)}\){rem}."))
        return out
    if any((iv.lo is not None and iv.lo.q is None) or (iv.hi is not None and iv.hi.q is None) for iv in S):
        raise NonPrisEnCharge("il faudrait résoudre une équation polynomiale de second membre irrationnel.")
    res = []
    for iv in S:
        if iv.lo is not None and iv.hi is not None and proche(iv.lo.val, iv.hi.val):
            Rz = r_add(R, r_const(-iv.lo.q))
            if iv.lo.q != 0:
                items.append(txt(rf"\({expr_tex} = {iv.lo.tex}\)"))
            res = union(res, resoudre_rat(Rz, "=", v, items))
            continue
        cur = REELS
        if iv.lo is not None:
            Rl = r_add(R, r_const(-iv.lo.q))
            if iv.lo.q != 0:
                items.append(txt(rf"\({expr_tex} {GE if iv.lf else '>'} {iv.lo.tex} \iff {rtex(r_norm(Rl), v)} {GE if iv.lf else '>'} 0\)"))
            cur = inter(cur, resoudre_rat(Rl, ">=" if iv.lf else ">", v, items))
        if iv.hi is not None:
            Rh = r_add(r_const(iv.hi.q), r_neg(R))
            items.append(txt(rf"\({expr_tex} {LE if iv.hf else '<'} {iv.hi.tex} \iff {rtex(r_norm(Rh), v)} {GE if iv.hf else '>'} 0\)"))
            cur = inter(cur, resoudre_rat(Rh, ">=" if iv.hf else ">", v, items))
        res = union(res, cur)
    return res


def preimage(B, S, items):
    """{x : B(x) ∈ S}, en détaillant."""
    if isinstance(B, X):
        return fusion(S)
    dec_ = decomposer(B)
    if dec_[0] == "x":
        return resoudre_dans(dec_[1], S, "x", tex(B), items)
    _, genre, B2, R2, t_tex = dec_
    if est_identite(R2):
        S_t = fusion(S)
    else:
        items.append(txt(rf"On pose \(t = {t_tex}\) : \({tex(B)} = {rtex(R2, 't')}\)."))
        S_t = resoudre_dans(R2, S, "t", rtex(R2, "t"), items)
    S_B = retour_atome(genre, S_t, t_tex, tex(B2), items)
    return preimage(B2, S_B, items)


# =====================================================================
# 10. CONDITIONS D'EXISTENCE ET ANALYSE COMPLÈTE
# =====================================================================
POURQUOI = {
    "ln": "L'argument d'un logarithme doit être strictement positif.",
    "den": "Un dénominateur doit être non nul.",
    "sqrt": "Le contenu d'une racine carrée doit être positif ou nul.",
    "pos": "Une puissance d'exposant fractionnaire négatif exige une base strictement positive.",
}
TITRE = {"ln": "logarithme", "den": "dénominateur", "sqrt": "racine carrée", "pos": "puissance"}


def conditions(n, out):
    def ajouter(genre, a):
        c = valeur_constante(a)
        if genre == "den" and c is not None:
            if c == 0:
                raise ErreurSaisie("Division par zéro dans l'expression.")
            return
        k = (genre, a.key())
        if not any((g, x.key()) == k for g, x in out):
            out.append((genre, a))

    if isinstance(n, Neg):
        conditions(n.a, out)
    elif isinstance(n, Fn):
        conditions(n.a, out)
        if n.nom == "ln":
            ajouter("ln", n.a)
        elif n.nom == "sqrt":
            ajouter("sqrt", n.a)
    elif isinstance(n, Op):
        conditions(n.a, out)
        conditions(n.b, out)
        if n.op == "/":
            ajouter("den", n.b)
        elif n.op == "^":
            e = valeur_constante(n.b)
            if e is None:
                raise ErreurSaisie("Exposant variable non pris en charge : écrivez plutôt e^(…) avec exp.")
            if e.denominator % 2 == 0:
                ajouter("sqrt" if e > 0 else "pos", n.a)
            elif e < 0:
                ajouter("den", n.a)


def resoudre_condition(genre, A):
    items = [txt(POURQUOI[genre])]
    At = tex(A)
    if genre == "den":
        cond = rf"{At} \neq 0"
        items.append(txt(rf"On cherche les valeurs interdites : on résout \({At} = 0\)."))
        Z = preimage(A, points([Num.rat(0)]), items)
        E_ = complement(Z)
        if Z:
            items.append(txt(rf"On exclut ces valeurs."))
        else:
            items.append(txt(rf"\({At}\) ne s'annule jamais : aucune valeur interdite."))
        return cond, items, E_
    if genre in ("ln", "pos"):
        cond, S0 = rf"{At} > 0", [Iv(Num.rat(0), False, None, False)]
    else:
        cond, S0 = rf"{At} \geq 0", [Iv(Num.rat(0), True, None, False)]
    if isinstance(A, X):
        items.append(txt(rf"La condition s'écrit directement \({cond}\)."))
    E_ = preimage(A, S0, items)
    return cond, items, E_


def analyser(entree):
    try:
        f = lire(entree)
        conds = []
        conditions(f, conds)
    except ErreurSaisie as e:
        return {"ok": False, "erreur": str(e)}
    res = {"ok": True, "f_tex": tex(f), "conditions": []}
    ED = REELS
    complet = True
    for i, (genre, A) in enumerate(conds, 1):
        c = {"num": i, "genre": genre, "titre": TITRE[genre], "source_tex": tex(A)}
        try:
            cond, items, E_ = resoudre_condition(genre, A)
            c.update({"cond_tex": cond, "etapes": items, "E_tex": ens_tex(E_), "resolu": True})
            ED = inter(ED, E_)
        except NonPrisEnCharge as e:
            c.update({"cond_tex": {"den": rf"{tex(A)} \neq 0", "ln": rf"{tex(A)} > 0", "pos": rf"{tex(A)} > 0"}
                      .get(genre, rf"{tex(A)} \geq 0"),
                      "etapes": [txt("Résolution exacte non prise en charge : " + str(e))],
                      "E_tex": None, "resolu": False})
            complet = False
        except (ErreurSaisie, ZeroDivisionError, OverflowError, ValueError) as e:
            c.update({"cond_tex": tex(A), "etapes": [txt("Erreur : " + str(e))], "E_tex": None, "resolu": False})
            complet = False
        res["conditions"].append(c)
    res["complet"] = complet
    if complet:
        res["ED_tex"] = ens_tex(ED)
        if conds:
            res["inter_tex"] = r" \cap ".join(f"E_{{{c['num']}}}" for c in res["conditions"])
    return res


def analyser_json(entree):
    return json.dumps(analyser(entree), ensure_ascii=False)


def apercu_json(entree):
    try:
        return json.dumps({"ok": True, "tex": tex(lire(entree))}, ensure_ascii=False)
    except ErreurSaisie as e:
        return json.dumps({"ok": False, "erreur": str(e)}, ensure_ascii=False)


# =====================================================================
# 11. LIGNE DE COMMANDE
# =====================================================================
def _texte(res):
    import re
    if not res["ok"]:
        return "Erreur : " + res["erreur"]
    out = [f"f(x) = {res['f_tex']}"]
    for c in res["conditions"]:
        out.append(f"\nCondition {c['num']} ({c['titre']}) : {c['cond_tex']}")
        for it in c["etapes"]:
            if it["type"] == "texte":
                out.append("   " + re.sub(r"\\\(|\\\)", "", it["html"]))
            else:
                out.append("   Tableau de signes (" + it["var"] + ") : " + " | ".join(it["crit"]))
                for r in it["rows"]:
                    out.append(f"      {r['label']:<28} " + " ".join(f"{x:>2}" for x in r["cells"]))
        out.append(f"   E_{c['num']} = {c['E_tex']}")
    if res["complet"]:
        out.append(f"\nED = {res.get('inter_tex', '')} = {res['ED_tex']}")
    return "\n".join(out)


if __name__ == "__main__":
    import sys
    for arg in sys.argv[1:] or ["ln(x)-2/(ln(x)-1)"]:
        print(_texte(analyser(arg)))
        print("=" * 60)
