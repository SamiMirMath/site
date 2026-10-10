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

__all__ = ["analyser", "analyser_json", "apercu_json", "verifier_json"]


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
        if n.op in "+-":
            r = a + b if n.op == "+" else a - b
            # compensation catastrophique (ex. ln(x²) − 2 ln x) : on arrondit à 0
            return 0.0 if abs(r) <= 1e-12 * (abs(a) + abs(b)) else r
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
        # un "/" dans n.txt ne peut venir que du repli ftxt() d'un Nb construit
        # programmatiquement (jamais de la saisie utilisateur, dont le tokeniseur
        # n'émet jamais "/" à l'intérieur d'un nombre) : on l'écrit en \frac{}{}.
        if "/" in n.txt:
            num, den = n.txt.split("/")
            return r"\frac{" + num + "}{" + den + "}"
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
    """Réel avec écriture exacte (tex), valeur approchée (val) et forme SymPy (py)."""
    def __init__(self, val, tex, q=None, genre="gen", data=None, approx=False, py=None):
        self.val, self.tex, self.q, self.genre, self.data, self.approx = val, tex, q, genre, data, approx
        self.py = py if py is not None else repr(float(val))

    @staticmethod
    def rat(q):
        q = F(q)
        return Num(float(q), qtex(q), q=q, genre="rat", py=f"({q.numerator})/({q.denominator})")

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
        return Num(float(a) + float(b) * math.sqrt(m), s, genre="quad", data=(a, b, m),
                   py=f"(({a})+({b})*sqrt({m}))")

    @staticmethod
    def approche(v):
        return Num(v, r"{\approx}\," + dec(v), approx=True)


def proche(a, b):
    if not (math.isfinite(a) and math.isfinite(b)):
        return a == b
    return abs(a - b) <= 1e-9 * (1 + abs(a) + abs(b))


def parenthese(t):
    return r"\left(" + t + r"\right)" if (" + " in t or " - " in t) else t


def exp_de(n):
    if n.q is not None:
        if n.q == 0:
            return Num.rat(1)
        t = "e" if n.q == 1 else "e^{" + n.tex + "}"
        return Num(math.exp(n.val), t, genre="exp", data=n, py=f"exp({n.py})")
    if n.genre == "ln":
        return n.data
    return Num(math.exp(n.val), "e^{" + n.tex + "}", genre="exp", data=n, approx=n.approx, py=f"exp({n.py})")


def ln_de(n):
    if n.genre == "exp":
        return n.data
    if n.q is not None:
        q = n.q
        if q == 1:
            return Num.rat(0)
        if q.numerator == 1:
            return Num(math.log(n.val), r"-\ln(" + str(q.denominator) + ")", genre="ln", data=n,
                       py=f"-log({q.denominator})")
        t = r"\ln(" + str(q.numerator) + ")" if q.denominator == 1 else r"\ln\left(" + n.tex + r"\right)"
        return Num(math.log(n.val), t, genre="ln", data=n, py=f"log({n.py})")
    return Num(math.log(n.val), r"\ln\left(" + n.tex + r"\right)", genre="ln", data=n, approx=n.approx,
               py=f"log({n.py})")


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
    if n.approx:
        return Num.approche(n.val ** 2)
    return Num(n.val ** 2, r"\left(" + n.tex + r"\right)^{2}", py=f"({n.py})**2")


def affine_inv(n, m, b):
    """x tel que m·x + b = n, c.-à-d. x = n/m − b/m."""
    m, b = F(m), F(b)
    if n.q is not None:
        return Num.rat((n.q - b) / m)
    if n.genre == "quad":
        a, c, r = n.data
        return Num.quad((a - b) / m, c / m, r)
    val = (n.val - float(b)) / float(m)
    if n.approx:
        return Num.approche(val)
    al, be = 1 / m, -b / m
    if al == 1:
        t = n.tex
    elif al == -1:
        t = "-" + parenthese(n.tex)
    elif al.numerator in (1, -1):
        t = ("-" if al < 0 else "") + r"\frac{" + n.tex + "}{" + str(al.denominator) + "}"
    else:
        t = qtex(al) + parenthese(n.tex)
    if be > 0:
        t += " + " + qtex(be)
    elif be < 0:
        t += " - " + qtex(-be)
    return Num(val, t, py=f"(({n.py})-({b}))/({m})")


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


def points_exclus(S):
    """Si l'ensemble S équivaut à R privé d'un nombre fini de points, renvoie la liste
    (valeur, tex) de ces points (éventuellement vide si S = R). Sinon renvoie None.
    Sert à préférer, dans l'affichage final, « E \\ {valeurs interdites} » à une
    intersection quand c'est mathématiquement la même chose (A ∩ (R \\ P) = A \\ P)."""
    S = fusion(S)
    if not S or S[0].lo is not None or S[-1].hi is not None:
        return None
    if not all(S[i].hi is not None and S[i + 1].lo is not None and proche(S[i].hi.val, S[i + 1].lo.val)
               and not S[i].hf and not S[i + 1].lf for i in range(len(S) - 1)):
        return None
    return [(S[i].hi.val, S[i].hi.tex) for i in range(len(S) - 1)]


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
        nums = [Num.approche(x) for x in rs]
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
        if deg(d) == 0 and deg(n) == 2:
            return quad_irrationnel(pscal(n, 1 / d[0]), S, v, expr_tex, items)
        raise NonPrisEnCharge("il faudrait résoudre une équation polynomiale de second membre irrationnel.")
    res = []
    for iv in S:
        if iv.lo is not None and iv.hi is not None and proche(iv.lo.val, iv.hi.val):
            Rz = r_add(R, r_const(-iv.lo.q))
            ligne = rf"\({expr_tex} = {iv.lo.tex}\)"
            if iv.lo.q != 0 and not (items and items[-1].get("html", "").endswith(ligne[2:])):
                items.append(txt(ligne))
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


def racines_quad_r(P, r, v, items):
    """Zéros de a v² + b v + c = r (r réel écrit exactement) par la forme canonique a(v − h)² + k = r."""
    c, b, a = P[0], P[1], P[2]
    h = -b / (2 * a)
    k = c - b * b / (4 * a)
    carre_tex = v if h == 0 else r"\left(" + ptex([-h, F(1)], v) + r"\right)"
    carre_tex += "^{2}"
    gauche = (mono_c(a) + carre_tex) + ("" if k == 0 else (" + " + qtex(k) if k > 0 else " - " + qtex(-k)))
    # K = (r − k)/a
    if r.q is not None:
        Kq = (r.q - k) / a
        Kv, Ktex = float(Kq), qtex(Kq)
    else:
        Kv = (r.val - float(k)) / float(a)
        if a > 0:
            num = r.tex if k == 0 else r.tex + (" - " + qtex(k) if k > 0 else " + " + qtex(-k))
            Ktex = num if a == 1 else r"\frac{" + num + "}{" + qtex(a) + "}"
        else:
            num = ("-" + parenthese(r.tex)) if k == 0 else qtex(k) + " - " + parenthese(r.tex)
            Ktex = num if a == -1 else r"\frac{" + num + "}{" + qtex(-a) + "}"
    etapes = rf"\({ptex(P, v)} = {r.tex}\)"
    if b != 0:
        etapes += rf" \(\iff {gauche} = {r.tex}\) (forme canonique)"
    etapes += rf" \(\iff {carre_tex} = {Ktex}\)"
    items.append(txt(etapes + "."))
    if Kv < -1e-12:
        ap = "" if r.q is not None else rf" \approx {dec(Kv)}"
        items.append(txt(rf"Or \({Ktex}{ap} < 0\) et un carré est positif : aucune solution."))
        return []
    if abs(Kv) <= 1e-12:
        x0 = Num.rat(h)
        items.append(txt(rf"\({Ktex} = 0\) : une seule solution \({v} = {x0.tex}\)."))
        return [x0]
    if r.q is not None:
        kk, m = racine_q(Kq)
        if m == 1:
            x1, x2 = Num.rat(h - kk), Num.rat(h + kk)
        else:
            x1, x2 = Num.quad(h, -kk, m), Num.quad(h, kk, m)
    else:
        rac = r"\sqrt{" + Ktex + "}"
        ht = "" if h == 0 else qtex(h) + " "
        x1 = Num(float(h) - math.sqrt(Kv), (ht + "- " + rac) if h != 0 else "-" + rac)
        x2 = Num(float(h) + math.sqrt(Kv), (ht + "+ " + rac) if h != 0 else rac)
    ap = (lambda z: "" if z.q is not None else rf" \approx {dec(z.val)}")
    apK = "" if r.q is not None else rf" \approx {dec(Kv)}"
    items.append(txt(rf"Comme \({Ktex}{apK} > 0\) : \({v} = {x1.tex}{ap(x1)}\) "
                     rf"ou \({v} = {x2.tex}{ap(x2)}\)."))
    return [x1, x2]


def quad_irrationnel(P, S, v, expr_tex, items):
    """{v : P(v) ∈ S}, P trinôme, bornes de S quelconques : P(v) − r a le signe de a hors des racines."""
    a = P[2]
    res = []
    for iv in fusion(S):
        if iv.lo is not None and iv.hi is not None and proche(iv.lo.val, iv.hi.val):
            res = union(res, points(racines_quad_r(P, iv.lo, v, items)))
            continue
        cur = REELS
        for borne, ferme, haut in ((iv.lo, iv.lf, False), (iv.hi, iv.hf, True)):
            if borne is None:
                continue
            rs = racines_quad_r(P, borne, v, items)
            # ensemble où P(v) > borne (ou ≥)
            if not rs:
                sup = REELS if a > 0 else []
            elif len(rs) == 1:
                sup = complement(points(rs)) if a > 0 else []
                if ferme:
                    sup = union(sup, points(rs))
            else:
                x1, x2 = rs
                if a > 0:
                    sup = [Iv(None, False, x1, ferme), Iv(x2, ferme, None, False)]
                else:
                    sup = [Iv(x1, ferme, x2, ferme)]
            sup = fusion(sup)
            if haut:     # P(v) < borne (ou ≤) : complément de P(v) > borne (ou ≥) avec bords inversés
                ens = complement(sup)
                if ferme:
                    ens = union(ens, points(rs))
                else:
                    ens = inter(ens, complement(points(rs)))
            else:
                ens = sup
            symb = (GE if ferme else ">") if not haut else (LE if ferme else "<")
            items.append(txt(rf"Le trinôme a le signe de \(a = {qtex(a)}\) à l'extérieur de ses racines : "
                             rf"\({expr_tex} {symb} {borne.tex} \iff {v} \in {ens_tex(ens)}\)."))
            cur = inter(cur, ens)
        res = union(res, cur)
    return res


def preimage(B, S, items):
    """{x : B(x) ∈ S}, en détaillant."""
    if isinstance(B, X):
        return fusion(S)
    try:
        dec_ = decomposer(B)
    except NonPrisEnCharge:
        r = via_somme_logs(B, S, items)
        if r is None:
            raise
        return r
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


def termes_logs(n, c, logs, k):
    """Décompose n en Σ c_i·ln(B_i) + k (c_i entiers, k rationnel). Renvoie False si impossible."""
    v = valeur_constante(n)
    if v is not None:
        k[0] += c * v
        return True
    if isinstance(n, Neg):
        return termes_logs(n.a, -c, logs, k)
    if isinstance(n, Fn) and n.nom == "ln":
        for L in logs:
            if L[1].key() == n.a.key():
                L[0] += c
                return True
        logs.append([c, n.a])
        return True
    if isinstance(n, Op) and n.op in "+-":
        return termes_logs(n.a, c, logs, k) and termes_logs(n.b, c if n.op == "+" else -c, logs, k)
    if isinstance(n, Op) and n.op in "*/":
        va, vb = valeur_constante(n.a), valeur_constante(n.b)
        if n.op == "*" and va is not None:
            return termes_logs(n.b, c * va, logs, k)
        if vb is not None and vb != 0:
            return termes_logs(n.a, c * vb if n.op == "*" else c / vb, logs, k)
    return False


def via_somme_logs(A, S, items):
    """A = Σ c_i ln(B_i) + k : sur le domaine D des logarithmes, A = ln(∏ B_i^{c_i}) + k.
    On résout alors la condition sur le produit, puis on ne garde que les solutions dans D."""
    logs, k = [], [F(0)]
    if not termes_logs(A, F(1), logs, k):
        return None
    logs = [(c, B) for c, B in logs if c != 0]
    if len(logs) < 2 or any(c.denominator != 1 for c, _ in logs):
        return None

    def puiss(B, c):
        return B if c == 1 else Op("^", B, Nb(c))

    def prod(L):
        out = L[0]
        for b in L[1:]:
            out = Op("*", out, b)
        return out
    num = [puiss(B, int(c)) for c, B in logs if c > 0]
    den = [puiss(B, int(-c)) for c, B in logs if c < 0]
    P = prod(num) if num else Nb(1)
    if den:
        P = Op("/", P, prod(den))
    lnP = Fn("ln", P)
    A2 = lnP if k[0] == 0 else Op("+", lnP, Nb(k[0]) if k[0] > 0 else Neg(Nb(-k[0])))
    D = domaine(A)
    regles = []
    if any(c > 0 for c, _ in logs) and sum(1 for c, _ in logs if c > 0) > 1:
        regles.append(r"\ln(a) + \ln(b) = \ln(ab)")
    if den:
        regles.append(r"\ln(a) - \ln(b) = \ln\left(\frac{a}{b}\right)")
    if any(abs(c) > 1 for c, _ in logs):
        regles.append(r"n\ln(a) = \ln(a^{n})")
    items.append(txt(rf"Les logarithmes sont tous définis pour \(x \in D = {ens_tex(D)}\). "
                     rf"Sur \(D\), on regroupe avec " + ", ".join(rf"\({r}\)" for r in regles)
                     + rf" (valable car \(a, b > 0\)) : \({tex(A)} = {tex(A2)}\)."))
    it = []
    R = preimage(A2, S, it)
    items.extend(it)
    R2 = inter(R, D)
    perdus = [iv for iv in R if not inter([iv], D)]
    approx = lambda p: "" if p.q is not None else rf" \approx {dec(p.val)}"
    if all(iv.lo is not None and iv.hi is not None and proche(iv.lo.val, iv.hi.val) for iv in R) and R:
        for iv in R:
            if not contient(D, iv.lo.val):
                items.append(txt(rf"\(x = {iv.lo.tex}{approx(iv.lo)}\) n'est pas dans \(D\) : solution rejetée."))
            else:
                items.append(txt(rf"\(x = {iv.lo.tex}{approx(iv.lo)}\) est dans \(D\) : solution retenue."))
    elif R != R2 or perdus:
        RT = ens_tex(R) if len(fusion(R)) <= 1 else r"\left(" + ens_tex(R) + r"\right)"
        items.append(txt(rf"On ne garde que ce qui est dans \(D\) : \(x \in {RT} \cap {ens_tex(D)} = {ens_tex(R2)}\)."))
    return R2


# =====================================================================
# 9 bis. CAS GÉNÉRAL : SIGNE FACTEUR PAR FACTEUR, CALCUL FORMEL (SymPy), NUMÉRIQUE
# =====================================================================
#   Quand la condition mélange x et ln/exp/√ (ex. x·ln(x+2) ≥ 0), on l'écrit comme un
#   produit/quotient de facteurs, on étudie le signe de chaque facteur (méthode exacte,
#   sinon SymPy, sinon dichotomie numérique) et on dresse le tableau de signes.

ETAT = {"sympy_manquant": False}
_SP = {}


def _sympy():
    """Module sympy s'il est disponible (Pyodide : pyodide.loadPackage('sympy')), sinon None."""
    if "sp" in _SP:
        return _SP["sp"]
    try:
        import sympy
        _SP["sp"] = sympy
        _SP["x"] = sympy.Symbol("x", real=True)
        return sympy
    except Exception:
        return None


def en_py(n):
    """Arbre → chaîne lisible par SymPy."""
    if isinstance(n, Nb):
        return f"({n.v.numerator})/({n.v.denominator})" if n.v.denominator != 1 else f"({n.v.numerator})"
    if isinstance(n, X):
        return "x"
    if isinstance(n, E):
        return "E"
    if isinstance(n, Neg):
        return "(-" + en_py(n.a) + ")"
    if isinstance(n, Fn):
        return {"ln": "log", "exp": "exp", "sqrt": "sqrt"}[n.nom] + "(" + en_py(n.a) + ")"
    op = {"^": "**"}.get(n.op, n.op)
    return "(" + en_py(n.a) + op + en_py(n.b) + ")"


def en_sympy(n):
    sp = _sympy()
    return sp.sympify(en_py(n), locals={"x": _SP["x"], "E": sp.E})


def num_sympy(e):
    sp = _sympy()
    e = sp.nsimplify(e) if e.is_Float else e
    v = float(sp.N(e, 30))
    t = sp.latex(e, ln_notation=True)
    if len(t) > 60 or e.has(sp.LambertW) or not e.is_real:
        return Num.approche(v)
    return Num(v, t, q=F(int(e.p), int(e.q)) if e.is_Rational else None, py=str(e))


def depuis_sympy(S):
    """Ensemble SymPy → liste d'intervalles. Lève NonPrisEnCharge si SymPy n'a pas conclu."""
    sp = _sympy()
    if S == sp.S.EmptySet:
        return []
    if S == sp.S.Reals:
        return REELS
    if isinstance(S, sp.Interval):
        lo = None if S.start == -sp.oo else num_sympy(S.start)
        hi = None if S.end == sp.oo else num_sympy(S.end)
        return fusion([Iv(lo, lo is not None and not S.left_open, hi, hi is not None and not S.right_open)])
    if isinstance(S, sp.FiniteSet):
        pts = []
        for p in S.args:
            if p.is_real is False:
                continue
            if p.is_real is None and abs(sp.im(sp.N(p))) > 1e-12:
                continue
            pts.append(num_sympy(p))
        return points(pts)
    if isinstance(S, sp.Union):
        out = []
        for a in S.args:
            out = union(out, depuis_sympy(a))
        return out
    if isinstance(S, sp.Intersection):
        out = REELS
        for a in S.args:
            out = inter(out, depuis_sympy(a))
        return out
    if isinstance(S, sp.Complement):
        return inter(depuis_sympy(S.args[0]), complement(depuis_sympy(S.args[1])))
    raise NonPrisEnCharge("SymPy n'a pas trouvé de forme exacte.")


def arbre_depuis_sympy(e):
    """Expression SymPy → arbre (pour réutiliser une factorisation SymPy)."""
    sp = _sympy()
    if e == _SP["x"]:
        return X()
    if e == sp.E:
        return E()
    if e.is_Rational:
        q = F(int(e.p), int(e.q))
        return Neg(Nb(-q)) if q < 0 else Nb(q)
    if isinstance(e, sp.Add):
        args = [arbre_depuis_sympy(a) for a in e.as_ordered_terms()]
        out = args[0]
        for a in args[1:]:
            out = Op("+", out, a)
        return out
    if isinstance(e, sp.Mul):
        num, den = [], []
        for a in e.args:
            b, ex = a.as_base_exp()
            if ex.is_number and ex < 0:
                den.append(arbre_depuis_sympy(b ** (-ex)))
            else:
                num.append(arbre_depuis_sympy(a))
        prod = lambda L: L[0] if len(L) == 1 else Op("*", prod(L[:-1]), L[-1])
        top = prod(num) if num else Nb(1)
        return Op("/", top, prod(den)) if den else top
    if isinstance(e, sp.Pow):
        b, ex = e.args
        if b == sp.E:
            return Fn("exp", arbre_depuis_sympy(ex))
        if ex == sp.Rational(1, 2):
            return Fn("sqrt", arbre_depuis_sympy(b))
        if ex == -1:
            return Op("/", Nb(1), arbre_depuis_sympy(b))
        if ex.is_Rational:
            return Op("^", arbre_depuis_sympy(b), arbre_depuis_sympy(ex))
    if isinstance(e, sp.exp):
        return Fn("exp", arbre_depuis_sympy(e.args[0]))
    if isinstance(e, sp.log):
        return Fn("ln", arbre_depuis_sympy(e.args[0]))
    raise NonPrisEnCharge("expression SymPy non convertible.")


class Incertain(Exception):
    """Valeur hors de portée des flottants (e^(±700)…) : point inutilisable pour un test numérique."""


def evaluer(n, x):
    """Valeur numérique de l'arbre en x (None si non définie)."""
    try:
        if isinstance(n, Nb):
            return float(n.v)
        if isinstance(n, X):
            return x
        if isinstance(n, E):
            return math.e
        if isinstance(n, Neg):
            a = evaluer(n.a, x)
            return None if a is None else -a
        if isinstance(n, Fn):
            a = evaluer(n.a, x)
            if a is None:
                return None
            if n.nom == "ln":
                return math.log(a) if a > 0 else None
            if n.nom == "sqrt":
                return math.sqrt(a) if a >= 0 else None
            if abs(a) > 700:
                raise Incertain()
            return math.exp(a)
        a, b = evaluer(n.a, x), evaluer(n.b, x)
        if a is None or b is None:
            return None
        if n.op in "+-":
            r = a + b if n.op == "+" else a - b
            # compensation catastrophique (ex. ln(x²) − 2 ln x) : on arrondit à 0
            return 0.0 if abs(r) <= 1e-12 * (abs(a) + abs(b)) else r
        if n.op == "*":
            return a * b
        if n.op == "/":
            return None if b == 0 else a / b
        e = valeur_constante(n.b)
        if e is not None and e.denominator == 1:
            if a == 0 and e < 0:
                return None
            return a ** int(e)
        if e is not None and e.denominator % 2 == 1:
            if a == 0 and e < 0:
                return None
            r = abs(a) ** float(e)
            return -r if (a < 0 and e.numerator % 2) else r
        if a < 0 or (a == 0 and b <= 0):
            return None
        return a ** b
    except OverflowError:
        raise Incertain()
    except (ValueError, ZeroDivisionError):
        return None


def aplatir(n):
    """n = c · ∏ h_i^{k_i} (c rationnel, k_i entiers non nuls)."""
    c = [F(1)]
    facs = []

    def ajout(h, k):
        for f in facs:
            if f[0].key() == h.key():
                f[1] += k
                return
        facs.append([h, k])

    def rec(m, k):
        v = valeur_constante(m)
        if v is not None:
            if v == 0 and k < 0:
                raise ErreurSaisie("Division par zéro dans l'expression.")
            c[0] *= v ** k
        elif isinstance(m, Neg):
            c[0] *= (-1) ** abs(k)
            rec(m.a, k)
        elif isinstance(m, Op) and m.op == "*":
            rec(m.a, k)
            rec(m.b, k)
        elif isinstance(m, Op) and m.op == "/":
            rec(m.a, k)
            rec(m.b, -k)
        elif isinstance(m, Op) and m.op == "^" and valeur_constante(m.b) is not None \
                and valeur_constante(m.b).denominator == 1:
            rec(m.a, k * int(valeur_constante(m.b)))
        else:
            ajout(m, k)
    rec(n, 1)
    return c[0], [(h, k) for h, k in facs if k != 0]


def contient(S, v):
    for iv in S:
        if iv.lo is not None:
            if proche(v, iv.lo.val):
                if not iv.lf:
                    continue
            elif v < iv.lo.val:
                continue
        if iv.hi is not None:
            if proche(v, iv.hi.val):
                if not iv.hf:
                    continue
            elif v > iv.hi.val:
                continue
        return True
    return False


def domaine(h):
    """Ensemble de définition de h (même méthode, sans le détail)."""
    conds = []
    conditions(h, conds)
    D = REELS
    for genre, A in conds:
        D = inter(D, resoudre_condition(genre, A)[2])
    return D


ECHANT = sorted(set([i / 40 for i in range(-2400, 2401)] +
                    [s * 10 ** (k / 25) for s in (-1, 1) for k in range(40, 226)]))


def signe_numerique(h, D):
    """P = {h > 0}, Z = {h = 0} sur D, zéros approchés par dichotomie."""
    def f(t):
        try:
            return evaluer(h, t)
        except Incertain:
            return None
    P, Z = [], []
    for iv in D:
        a, b = vlo(iv), vhi(iv)
        xs = [t for t in ECHANT if a < t < b]
        for bord, sens in ((a, 1), (b, -1)):
            if math.isfinite(bord):
                xs += [bord + sens * 10 ** (-k) * (1 + abs(bord)) for k in range(1, 10)]
        xs = sorted(t for t in set(xs) if a < t < b)
        if not xs:
            continue
        vals = [f(t) for t in xs]
        racines = []
        for i, t in enumerate(xs):
            if vals[i] == 0:
                racines.append(t)
            elif i and vals[i - 1] not in (None, 0) and vals[i] is not None and (vals[i - 1] > 0) != (vals[i] > 0):
                lo, hi, flo = xs[i - 1], t, vals[i - 1]
                for _ in range(200):
                    mid = (lo + hi) / 2
                    fm = f(mid)
                    if fm is None or fm == 0 or hi - lo < 1e-15 * (1 + abs(mid)):
                        break
                    if (fm > 0) == (flo > 0):
                        lo, flo = mid, fm
                    else:
                        hi = mid
                racines.append((lo + hi) / 2)
        nums = []
        for r in sorted(racines):
            if not any(proche(r, m.val) for m in nums):
                nums.append(Num.approche(r))
        Z = union(Z, points(nums))
        # bords fermés où h s'annule
        for bord, ferme in ((iv.lo, iv.lf), (iv.hi, iv.hf)):
            if bord is not None and ferme and f(bord.val) is not None and abs(f(bord.val)) < 1e-12:
                Z = union(Z, points([bord]))
        coupes = [iv.lo] + nums + [iv.hi]
        for j in range(len(coupes) - 1):
            lo, hi = coupes[j], coupes[j + 1]
            l, r = (-math.inf if lo is None else lo.val), (math.inf if hi is None else hi.val)
            ts = [t for t in xs if l < t < r and not proche(t, l) and not proche(t, r)]
            t = ts[len(ts) // 2] if ts else ((l + r) / 2 if math.isfinite(l) and math.isfinite(r) else
                                             (r - 1 if math.isfinite(r) else (l + 1 if math.isfinite(l) else 0.0)))
            v = f(t)
            if v is not None and v > 0:
                P = union(P, [Iv(lo, False, hi, False)])
    P = inter(P, D)
    return fusion(P), inter(fusion(Z), D)


def signe_facteur(h, nom):
    """Étudie le signe d'un facteur : (D, P, Z, étapes)."""
    ht = tex(h)
    D = domaine(h)
    items = []
    if not (len(D) == 1 and D[0].lo is None and D[0].hi is None):
        items.append(txt(rf"\({ht}\) est défini pour \({nom} \in {ens_tex(D)}\)."))
    # 1) méthode exacte
    try:
        it = []
        P = inter(preimage(h, [Iv(Num.rat(0), False, None, False)], it), D)
        Z = inter(preimage(h, points([Num.rat(0)]), []), D)
        items += it
        items.append(txt(rf"Bilan : \({ht} > 0 \iff {nom} \in {ens_tex(P)}\) ; "
                         + (rf"\({ht} = 0 \iff {nom} \in {ens_tex(Z)}\)." if Z else rf"\({ht}\) ne s'annule pas.")))
        return D, P, Z, items, "exact"
    except NonPrisEnCharge:
        pass
    # 2) calcul formel
    sp = _sympy()
    if sp is not None:
        try:
            e, xs = en_sympy(h), _SP["x"]
            P = inter(depuis_sympy(sp.solveset(e > 0, xs, sp.S.Reals)), D)
            Z = inter(depuis_sympy(sp.solveset(sp.Eq(e, 0), xs, sp.S.Reals)), D)
            items.append(txt(rf"Ce facteur mélange \(x\) et une fonction transcendante : on résout avec le calcul formel : "
                             rf"\({ht} > 0 \iff {nom} \in {ens_tex(P)}\) et "
                             + (rf"\({ht} = 0 \iff {nom} \in {ens_tex(Z)}\)." if Z else rf"\({ht}\) ne s'annule pas.")))
            return D, P, Z, items, "sympy"
        except Exception:
            pass
    else:
        ETAT["sympy_manquant"] = True
    # 3) numérique
    P, Z = signe_numerique(h, D)
    items.append(txt(rf"L'équation \({ht} = 0\) n'a pas de solution exacte simple : on localise ses zéros "
                     rf"par dichotomie (valeurs approchées). "
                     + (rf"Zéros : \({SEP.join(z.lo.tex for z in Z)}\) ; " if Z else "Aucun zéro ; ")
                     + rf"\({ht} > 0\) sur \({ens_tex(P)}\)."))
    return D, P, Z, items, "numerique"


def tableau_facteurs(c, infos, rel, expr_tex, items):
    """Tableau de signes de c·∏ h_i^{k_i} ; renvoie {expr rel 0} (rel : '>' ou '>=')."""
    crit = []
    for (h, k), (D, P, Z) in infos:
        for S in (D, P, Z):
            for iv in S:
                for p in (iv.lo, iv.hi):
                    if p is not None and not any(proche(p.val, q.val) for q in crit):
                        crit.append(p)
    crit.sort(key=lambda p: p.val)
    n = len(crit)

    def test(i):
        if n == 0:
            return 0.0
        if i == 0:
            return crit[0].val - 1
        if i == n:
            return crit[-1].val + 1
        return (crit[i - 1].val + crit[i].val) / 2

    def etat(D, P, Z, k, v):
        if not contient(D, v):
            return "x"
        if contient(Z, v):
            return "||" if k < 0 else "0"
        s = "+" if contient(P, v) else "-"
        return "+" if (s == "-" and k % 2 == 0) else s

    vals = []
    for i in range(n + 1):
        vals.append(test(i))
        if i < n:
            vals.append(crit[i].val)
    lignes = []
    if c < 0:
        lignes.append({"label": qtex(c), "cells": ["-"] * len(vals)})
    for (h, k), (D, P, Z) in infos:
        lab = tex(h) if prec(h) >= 3 else r"\left(" + tex(h) + r"\right)"
        if abs(k) > 1:
            lab = (lab if prec(h) >= 3 and not isinstance(h, Fn) else r"\left(" + tex(h) + r"\right)") + "^{" + str(abs(k)) + "}"
        elif prec(h) < 3:
            lab = tex(h)
        if k < 0:
            lab += r" \ (\text{dén.})"
        lignes.append({"label": lab, "cells": [etat(D, P, Z, k, v) for v in vals]})
    fin = []
    for j in range(len(vals)):
        col = [l["cells"][j] for l in lignes]
        if "x" in col:
            fin.append("x")
        elif "||" in col:
            fin.append("||")
        elif "0" in col:
            fin.append("0")
        else:
            fin.append("-" if col.count("-") % 2 else "+")
    lignes.append({"label": expr_tex, "cells": fin, "final": True})
    items.append({"type": "tableau", "var": "x", "crit": [p.tex for p in crit], "rows": lignes})
    S = []
    for i in range(n + 1):
        if fin[2 * i] == "+":
            S.append(Iv(crit[i - 1] if i else None, False, crit[i] if i < n else None, False))
        if i < n and rel == ">=" and fin[2 * i + 1] == "0":
            S.append(Iv(crit[i], True, crit[i], True))
    S = fusion(S)
    if any(ch == "x" for ch in fin):
        items.append(txt("Les zones hachurées (×) sont hors du domaine de définition de l'expression."))
    symb = ">" if rel == ">" else r"\geq"
    items.append(txt(rf"On lit le tableau : \({expr_tex} {symb} 0 \iff x \in {ens_tex(S)}\)."))
    return S


def resoudre_general(A, rel, items):
    """Condition A rel 0 (rel ∈ '>', '>=', '=') par étude du signe de chaque facteur."""
    c, facs = aplatir(A)
    nonconst = [(h, k) for h, k in facs]
    if len(nonconst) == 1 and nonconst[0][1] == 1:
        sp = _sympy()
        if sp is not None:
            try:
                fe = sp.factor(en_sympy(A))
                c2, facs2 = aplatir(arbre_depuis_sympy(fe))
                if len(facs2) > 1 or any(abs(k) > 1 for _, k in facs2):
                    A2 = arbre_depuis_sympy(fe)
                    items.append(txt(rf"On factorise : \({tex(A)} = {tex(A2)}\)."))
                    c, facs = c2, facs2
            except Exception:
                pass
    if len(facs) > 1 or any(abs(k) > 1 for _, k in facs):
        items.append(txt("On étudie le signe de chaque facteur, puis on dresse le tableau de signes."))
    infos = []
    for h, k in facs:
        D, P, Z, it, _ = signe_facteur(h, "x")
        if len(facs) > 1:
            items.append(txt(rf"<b>Signe de \({tex(h)}\)</b>"))
        items.extend(it)
        infos.append(((h, k), (D, P, Z)))
    if rel == "=":
        Dtot = REELS
        for (h, k), (D, P, Z) in infos:
            Dtot = inter(Dtot, D)
            if k < 0:
                Dtot = inter(Dtot, complement(Z))
        Zs = []
        for (h, k), (D, P, Z) in infos:
            if k > 0:
                Zs = union(Zs, Z)
        Zs = inter(Zs, Dtot)
        if len(facs) > 1:
            items.append(txt("Un produit est nul si et seulement si l'un de ses facteurs (du numérateur) est nul, "
                             "les autres étant définis."))
        return Zs
    return tableau_facteurs(c, infos, rel, tex(A), items)


# =====================================================================
# 10. CONDITIONS D'EXISTENCE ET ANALYSE COMPLÈTE
# =====================================================================
POURQUOI = {
    "ln": "L'argument d'un logarithme doit être strictement positif.",
    "den": "Un dénominateur doit être non nul.",
    "sqrt": "Le contenu d'une racine carrée doit être positif ou nul.",
    "pos": "Une puissance a^b d'exposant non entier (a^b = e^{b ln a}) exige une base strictement positive.",
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
                ajouter("pos", n.a)        # a^b = e^(b·ln a) : base > 0
            elif e.denominator % 2 == 0:
                ajouter("sqrt" if e > 0 else "pos", n.a)
            elif e < 0:
                ajouter("den", n.a)


def resoudre_condition(genre, A):
    items = [txt(POURQUOI[genre])]
    At = tex(A)
    if genre == "den":
        cond = rf"{At} \neq 0"
        items.append(txt(rf"On cherche les valeurs interdites : on résout \({At} = 0\)."))
        try:
            it = []
            Z = preimage(A, points([Num.rat(0)]), it)
        except NonPrisEnCharge:
            it = []
            Z = resoudre_general(A, "=", it)
        items += it
        E_ = complement(Z)
        if Z:
            items.append(txt(rf"Valeurs interdites : \(x \in {ens_tex(Z)}\). On les exclut."))
        else:
            items.append(txt(rf"\({At}\) ne s'annule jamais : aucune valeur interdite."))
        return cond, items, E_
    if genre in ("ln", "pos"):
        cond, rel, S0 = rf"{At} > 0", ">", [Iv(Num.rat(0), False, None, False)]
    else:
        cond, rel, S0 = rf"{At} \geq 0", ">=", [Iv(Num.rat(0), True, None, False)]
    if isinstance(A, X):
        items.append(txt(rf"La condition s'écrit directement \({cond}\)."))
    try:
        it = []
        E_ = preimage(A, S0, it)
    except NonPrisEnCharge:
        it = []
        E_ = resoudre_general(A, rel, it)
    items += it
    return cond, items, E_


def _analyser(entree):
    ETAT["sympy_manquant"] = False
    try:
        f = lire(entree)
        conds = []
        conditions(f, conds)
    except ErreurSaisie as e:
        return {"ok": False, "erreur": str(e)}, None, None
    res = {"ok": True, "f_tex": tex(f), "conditions": []}
    ED = REELS
    complet = True
    E_par_cond = {}
    for i, (genre, A) in enumerate(conds, 1):
        c = {"num": i, "genre": genre, "titre": TITRE[genre], "source_tex": tex(A)}
        try:
            cond, items, E_ = resoudre_condition(genre, A)
            c.update({"cond_tex": cond, "etapes": items, "E_tex": ens_tex(E_), "resolu": True})
            ED = inter(ED, E_)
            E_par_cond[i] = E_
        except Exception as e:      # filet de sécurité : jamais de plantage de la page
            c.update({"cond_tex": {"den": rf"{tex(A)} \neq 0", "ln": rf"{tex(A)} > 0", "pos": rf"{tex(A)} > 0"}
                      .get(genre, rf"{tex(A)} \geq 0"),
                      "etapes": [txt("Cette condition n'a pas pu être résolue : " + str(e))],
                      "E_tex": None, "resolu": False})
            complet = False
        res["conditions"].append(c)
    res["complet"] = complet
    res["besoin_sympy"] = ETAT["sympy_manquant"]
    if complet:
        res["ED_tex"] = ens_tex(ED)
        if len(conds) == 1:
            res["inter_tex"] = "E_{1}"
        elif conds:
            res["inter_tex"] = combinaison_tex(res["conditions"], E_par_cond)
    return res, f, (ED if complet else None)


def _appartient(val, S):
    for iv in S:
        bas = iv.lo is None or val > iv.lo.val or (iv.lf and proche(val, iv.lo.val))
        haut = iv.hi is None or val < iv.hi.val or (iv.hf and proche(val, iv.hi.val))
        if bas and haut:
            return True
    return False


def combinaison_tex(conditions_, E_par_cond):
    """Construit « E_i ∩ E_j ... \\ {valeurs interdites} » : les conditions dont
    l'ensemble équivaut à R privé de points (dénominateur ≠ 0, ln(...) ≠ valeur, etc.)
    sont soustraites plutôt qu'intersectées — c'est la même chose mathématiquement
    (A ∩ (R \\ P) = A \\ P), mais ça correspond à la façon dont les élèves raisonnent :
    on part du domaine puis on retire les valeurs interdites, plutôt que d'intersecter."""
    domaine_nums, points_tous = [], []
    for c in conditions_:
        E_ = E_par_cond.get(c["num"])
        if E_ is None:
            continue
        pts = points_exclus(E_)
        if pts is None:
            domaine_nums.append(c["num"])
        elif pts:
            points_tous.extend(pts)

    domaine = REELS
    for n in domaine_nums:
        domaine = inter(domaine, E_par_cond[n])
    points_finaux = []
    for val, t in points_tous:
        if _appartient(val, domaine) and not any(proche(val, v2) for v2, _ in points_finaux):
            points_finaux.append((val, t))
    points_finaux.sort(key=lambda vt: vt[0])

    base = r" \cap ".join(f"E_{{{n}}}" for n in domaine_nums) if domaine_nums else r"\mathbb{R}"
    if len(domaine_nums) > 1:
        base = r"\left(" + base + r"\right)"
    if points_finaux:
        pts_tex = r" \,;\, ".join(t for _, t in points_finaux)
        return base + r" \setminus \left\{" + pts_tex + r"\right\}"
    return base


def analyser(entree):
    return _analyser(entree)[0]


def analyser_json(entree):
    return json.dumps(analyser(entree), ensure_ascii=False)


def egaux(A, B):
    A, B = fusion(A), fusion(B)
    if len(A) != len(B):
        return False
    for a, b in zip(A, B):
        for p, q in ((a.lo, b.lo), (a.hi, b.hi)):
            if (p is None) != (q is None) or (p is not None and not proche(p.val, q.val)):
                return False
        if (a.lo is not None and a.lf != b.lf) or (a.hi is not None and a.hf != b.hf):
            return False
    return True


def verifier(entree):
    """Contrôle indépendant : on évalue f numériquement en de nombreux points et on vérifie
    que f est définie exactement aux points de l'ED trouvé (et seulement là)."""
    res, f, ED = _analyser(entree)
    if not res["ok"] or ED is None:
        return {"ok": False, "msg": "Pas d'ensemble à vérifier."}
    pts = list(ECHANT)
    for iv in ED:
        for p in (iv.lo, iv.hi):
            if p is not None:
                d = 1e-6 * (1 + abs(p.val))
                pts += [p.val - d, p.val + d, p.val - 1e3 * d, p.val + 1e3 * d]
    n_in = n_out = 0
    erreurs = []
    for t in pts:
        if any(iv_proche(iv, t) for iv in ED):
            continue            # trop près d'une borne : test non fiable en virgule flottante
        try:
            defini = evaluer(f, t) is not None
        except Incertain:
            continue
        dedans = contient(ED, t)
        if defini == dedans:
            n_in += dedans
            n_out += not dedans
        else:
            erreurs.append(t)
    return {"ok": True, "accord": not erreurs, "n_in": n_in, "n_out": n_out,
            "erreurs": [dec(t) for t in erreurs[:5]]}


def iv_proche(iv, t):
    return any(p is not None and abs(t - p.val) < 1e-9 * (1 + abs(p.val)) for p in (iv.lo, iv.hi))


def verifier_json(entree):
    return json.dumps(verifier(entree), ensure_ascii=False)


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
