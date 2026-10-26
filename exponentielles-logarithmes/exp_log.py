"""
exp_log.py — Outil « Exponentielles et logarithmes » (3C) : lecture de la saisie, arbre syntaxique, TeX.

Lecture propre à l'outil, parce que le tokeniseur de l'Ensemble de définition lit `log` comme `ln` et ne connaît ni log_a ni aˣ :
    log(x)  logarithme en base 10        ln(x)  logarithme en base e        log2(x), log_2(x), log_x(x)  base 2, base 2, base x
    exp(x), e^x, sqrt(x), + - * / ^ ( ), multiplication implicite (2x, 3ln(x), (x+1)(x-2)), virgule ou point décimal, un seul « = ».

Le tokeniseur reconnaît les noms de fonction (sqrt, exp, log…, ln) AVANT les lettres isolées : « exp » n'est jamais e·x·p.
La lettre e est toujours le nombre e ; elle ne peut pas être l'inconnue.

Tout le TeX est écrit par notre arbre (`tex`) : ln → \\ln, log → \\log, log_a → \\log_{a}. Aucune conversion depuis SymPy,
qui écrirait « log » pour ln. Ce fichier n'importe pas SymPy.

Interface : `lire_membres(texte)` (syntaxe seule, sert à l'aperçu), `analyser_saisie(texte)` (équation ou calcul, une seule inconnue),
`apercu_json(texte)`. Les erreurs sont des `ErreurSaisie` au message français.
"""
from fractions import Fraction as F
import math
import re
from collections import namedtuple
from functools import reduce
from math import gcd, isqrt

from noyau import ErreurSaisie, json_strict

__all__ = ["Nb", "Var", "E", "Neg", "Op", "Pow", "Fn", "Log", "tex", "variables", "lire_membres", "analyser_saisie", "tex_saisie",
           "apercu", "apercu_json", "Saisie"]

MESSAGE_E = "La lettre e désigne le nombre e ≈ 2,718 : choisissez une autre lettre pour l'inconnue."
MESSAGE_EXPOSANT = "Mettez l'exposant entre parenthèses : e^(-0,02t)."


# =====================================================================
# 1. ARBRE SYNTAXIQUE
# =====================================================================
class Noeud:
    __slots__ = ()

    def _cle(self):
        return (type(self).__name__,) + tuple(getattr(self, s) for s in self.__slots__)

    def __eq__(self, autre):
        return isinstance(autre, Noeud) and self._cle() == autre._cle()

    def __hash__(self):
        return hash(self._cle())

    def __repr__(self):
        return type(self).__name__ + "(" + ", ".join(repr(getattr(self, s)) for s in self.__slots__) + ")"


class Nb(Noeud):
    """Nombre rationnel exact. `dec` : écriture décimale de la saisie (« 0,02 »), gardée pour l'affichage ; hors égalité."""
    __slots__ = ("val", "dec")

    def __init__(self, val, dec=None):
        self.val, self.dec = F(val), dec

    def _cle(self):
        return ("Nb", self.val)


class Var(Noeud):
    __slots__ = ("nom",)

    def __init__(self, nom):
        self.nom = nom


class E(Noeud):
    """Le nombre e."""
    __slots__ = ()


class Neg(Noeud):
    __slots__ = ("a",)

    def __init__(self, a):
        self.a = a


class Op(Noeud):
    """Opération binaire : « + », « - », « * », « / »."""
    __slots__ = ("op", "a", "b")

    def __init__(self, op, a, b):
        self.op, self.a, self.b = op, a, b


class Pow(Noeud):
    __slots__ = ("a", "b")

    def __init__(self, a, b):
        self.a, self.b = a, b


class Fn(Noeud):
    """Fonction à un argument : seulement « sqrt » (exp devient Pow(E, …), ln et log deviennent Log)."""
    __slots__ = ("nom", "a")

    def __init__(self, nom, a):
        self.nom, self.a = nom, a


class Log(Noeud):
    """Logarithme de `a` en base `base` : None = base 10 (log), E() = base e (ln), sinon un nombre ou une inconnue (log_a)."""
    __slots__ = ("a", "base")

    def __init__(self, a, base=None):
        self.a, self.base = a, base


def variables(n):
    """Ensemble des lettres inconnues (jamais e) qui apparaissent dans l'arbre, base des logarithmes comprise."""
    if isinstance(n, Var):
        return {n.nom}
    if isinstance(n, (Nb, E)):
        return set()
    if isinstance(n, Neg) or isinstance(n, Fn):
        return variables(n.a)
    if isinstance(n, (Op, Pow)):
        return variables(n.a) | variables(n.b)
    if isinstance(n, Log):
        return variables(n.a) | (variables(n.base) if n.base is not None else set())
    raise TypeError(n)


def contient_e(n):
    if isinstance(n, E):
        return True
    if isinstance(n, (Var, Nb)):
        return False
    if isinstance(n, (Neg, Fn)):
        return contient_e(n.a)
    if isinstance(n, (Op, Pow)):
        return contient_e(n.a) or contient_e(n.b)
    if isinstance(n, Log):
        return contient_e(n.a) or (n.base is not None and contient_e(n.base))
    raise TypeError(n)


# =====================================================================
# 2. TEX (écrit par l'arbre, jamais par SymPy)
# =====================================================================
def _nb_tex(n):
    v = n.val
    if n.dec is not None:
        s = n.dec.replace(",", "{,}")
    elif v.denominator == 1:
        s = str(abs(v.numerator))
    else:
        s = r"\frac{" + str(abs(v.numerator)) + "}{" + str(v.denominator) + "}"
    return "-" + s if v < 0 else s


def _comme_somme(n):
    """Vrai si le nœud doit être mis entre parenthèses comme opérande d'une multiplication, d'une puissance ou d'une soustraction."""
    return isinstance(n, Neg) or (isinstance(n, Op) and n.op in "+-") or (isinstance(n, Nb) and n.val < 0)


def _entre_parentheses(s):
    return r"\left(" + s + r"\right)" if r"\frac" in s else "(" + s + ")"


_DEBUT_COLLABLE = re.compile(r"^([A-Za-z(]|\\left\(|\\ln|\\log|\\sqrt)")


def tex(n):
    if isinstance(n, Nb):
        return _nb_tex(n)
    if isinstance(n, Var):
        return n.nom
    if isinstance(n, E):
        return "e"
    if isinstance(n, Neg):
        s = tex(n.a)
        return "-" + (_entre_parentheses(s) if isinstance(n.a, Op) and n.a.op in "+-" else s)
    if isinstance(n, Op):
        if n.op == "/":
            return r"\frac{" + tex(n.a) + "}{" + tex(n.b) + "}"
        g, d = tex(n.a), tex(n.b)
        if n.op == "+":
            return g + " + " + d
        if n.op == "-":
            return g + " - " + (_entre_parentheses(d) if _comme_somme(n.b) else d)
        deux_groupes = _comme_somme(n.a) and _comme_somme(n.b)
        if _comme_somme(n.a):
            g = _entre_parentheses(g)
        if _comme_somme(n.b):
            d = _entre_parentheses(d)
        lettre_puis_groupe = isinstance(n.a, (Var, E)) and _comme_somme(n.b)
        if deux_groupes or lettre_puis_groupe or (isinstance(n.a, Nb) and n.a.val >= 0 and _DEBUT_COLLABLE.match(d)):
            return g + d
        return g + r" \cdot " + d
    if isinstance(n, Pow):
        base = tex(n.a)
        if isinstance(n.a, (Op, Neg, Log, Pow)) or (isinstance(n.a, Nb) and (n.a.val < 0 or (n.a.val.denominator != 1 and n.a.dec is None))):
            base = _entre_parentheses(base)
        return base + "^{" + tex(n.b) + "}"
    if isinstance(n, Fn):
        return r"\sqrt{" + tex(n.a) + "}"
    if isinstance(n, Log):
        if n.base is None:
            nom = r"\log"
        elif isinstance(n.base, E):
            nom = r"\ln"
        else:
            nom = r"\log_{" + tex(n.base) + "}"
        return nom + _entre_parentheses(tex(n.a))
    raise TypeError(n)


def tex_saisie(g, d=None):
    return tex(g) if d is None else tex(g) + " = " + tex(d)


# =====================================================================
# 3. TOKENISEUR (les noms de fonction passent avant les lettres isolées)
# =====================================================================
Tok = namedtuple("Tok", "type val base")      # type : num, var, fn, op ; base : seulement pour log

_NOMBRE = re.compile(r"\d+(?:[.,]\d+)?|[.,]\d+")
_BASE_SOULIGNEE = re.compile(r"_(\d+(?:[.,]\d+)?|[a-z])")
_BASE_COLLEE = re.compile(r"\d+")
_SYMBOLES = str.maketrans({"−": "-", "–": "-", "×": "*", "·": "*", "⋅": "*", "÷": "/"})
_OPERATEURS = "+-*/^()="
_INEGALITES = "<>≤≥≠"


def _fonction(s, i):
    """(nom, base, fin) si s[i:] commence par un nom de fonction, sinon None. Du plus long au plus court ; log accepte
    une base collée (log2, log10) ou soulignée (log_2, log_x)."""
    for nom in ("sqrt", "exp", "log", "ln"):
        if s.startswith(nom, i):
            j, base = i + len(nom), None
            if nom == "log":
                m = _BASE_SOULIGNEE.match(s, j)
                if m:
                    base, j = m.group(1), m.end()
                else:
                    m = _BASE_COLLEE.match(s, j)
                    if m:
                        base, j = m.group(0), m.end()
            return nom, base, j
    return None


def tokeniser(texte):
    s = texte.strip().lower().translate(_SYMBOLES)
    toks, i = [], 0
    while i < len(s):
        c = s[i]
        if c.isspace():
            i += 1
        elif c == "√":
            if s[i + 1:i + 2] != "(":
                raise ErreurSaisie("Après √, écrivez une parenthèse : √(x).")
            toks.append(Tok("fn", "sqrt", None))
            i += 1
        elif c in "0123456789.,":
            m = _NOMBRE.match(s, i)
            if not m:
                raise ErreurSaisie(f"Caractère non reconnu : « {c} ».")
            toks.append(Tok("num", m.group(0), None))
            i = m.end()
        elif c.isalpha() and c.isascii():
            f = _fonction(s, i)
            if f:
                nom, base, j = f
                k = j
                while k < len(s) and s[k].isspace():
                    k += 1
                if s[k:k + 1] != "(":
                    if nom == "log" and s[j:j + 1] == "_":
                        raise ErreurSaisie("Pour une autre base, écrivez log_2(x) ou log_a(x) : un nombre ou une lettre après le tiret bas.")
                    suite = nom + ("_" + base if base else "")
                    raise ErreurSaisie(f"Après {suite}, ouvrez une parenthèse : {suite}(x).")
                toks.append(Tok("fn", nom, base))
                i = j
            else:
                toks.append(Tok("var", c, None))
                i += 1
        elif c in _OPERATEURS or c in _INEGALITES:
            toks.append(Tok("op", c, None))
            i += 1
        else:
            raise ErreurSaisie(f"Caractère non reconnu : « {c} ».")
    return toks


# =====================================================================
# 4. ANALYSEUR SYNTAXIQUE
# =====================================================================
def _nombre(brut):
    t = brut.replace(",", ".")
    return Nb(F(t), brut.replace(".", ",") if "." in t else None)


def _base(nom_base):
    """Nœud de base d'un log_a : None pour 10, E() pour e, sinon un nombre (> 0, ≠ 1) ou une inconnue."""
    if nom_base is None:
        return None
    if nom_base[0].isdigit() or nom_base[0] in ".,":
        b = _nombre(nom_base)
        if b.val <= 0 or b.val == 1:
            raise ErreurSaisie("La base d'un logarithme est strictement positive et différente de 1.")
        return None if b.val == 10 else b
    return E() if nom_base == "e" else Var(nom_base)


class _Parseur:
    def __init__(self, toks):
        self.t, self.i = toks, 0

    def pic(self):
        return self.t[self.i] if self.i < len(self.t) else None

    def est_op(self, *ops):
        p = self.pic()
        return p is not None and p.type == "op" and p.val in ops

    def prendre(self):
        p = self.pic()
        self.i += 1
        return p

    def attendre(self, op):
        if not self.est_op(op):
            raise ErreurSaisie("Il manque une parenthèse fermante." if op == ")" else "Il manque une parenthèse ouvrante.")
        self.i += 1

    def tout(self):
        n = self.somme()
        p = self.pic()
        if p is not None:
            raise ErreurSaisie("Parenthèse fermante en trop." if p.val == ")" else f"Je ne comprends pas « {p.val} » ici.")
        return n

    def somme(self):
        signe = self.prendre().val if self.est_op("+", "-") else None
        n = self.produit()
        if signe == "-":
            n = Neg(n)
        while self.est_op("+", "-"):
            op = self.prendre().val
            if self.est_op("+", "-"):
                raise ErreurSaisie("Deux signes à la suite : utilisez des parenthèses, par exemple 3 + (-2).")
            n = Op(op, n, self.produit())
        return n

    def produit(self):
        n = self.puissance()
        dernier = None
        while True:
            p = self.pic()
            if self.est_op("*", "/"):
                dernier = self.prendre().val
                n = Op(dernier, n, self.puissance())
            elif p is not None and (p.type in ("num", "var", "fn") or (p.type == "op" and p.val == "(")):
                if p.type == "num":
                    raise ErreurSaisie("Un nombre ne peut pas suivre directement une lettre, une parenthèse ou un autre nombre : "
                                       "écrivez 2x (nombre devant), ou 2*3 avec le signe *.")
                if dernier == "/":
                    raise ErreurSaisie("Ajoutez des parenthèses après la division : 1/(2x) ou (1/2)x.")
                n = Op("*", n, self.puissance())
                dernier = "*"
            else:
                return n

    def puissance(self):
        base = self.atome()
        if self.est_op("^"):
            self.prendre()
            return Pow(base, self.exposant())
        return base

    def exposant(self):
        """Exposant : un seul nombre, une seule lettre, ou une parenthèse. Tout le reste (signe, fonction, nombre ou lettre suivi
        d'une autre lettre, d'une fonction ou d'une parenthèse, autre puissance) demande des parenthèses."""
        p = self.pic()
        if p is None:
            raise ErreurSaisie("Il manque l'exposant après le signe ^.")
        if (p.type == "op" and p.val in "+-") or p.type == "fn":
            raise ErreurSaisie(MESSAGE_EXPOSANT)
        n = self.atome()
        if self.est_op("^"):
            raise ErreurSaisie("Mettez les exposants entre parenthèses : 2^(3^2) ou (2^3)^2.")
        s = self.pic()
        if s is not None and p.type in ("num", "var"):
            colle = s.type == "var" or (p.type == "num" and (s.type == "fn" or (s.type == "op" and s.val == "(")))
            if colle:
                raise ErreurSaisie(MESSAGE_EXPOSANT)
        return n

    def atome(self):
        p = self.prendre()
        if p is None:
            raise ErreurSaisie("Il manque quelque chose à la fin de l'expression.")
        if p.type == "num":
            return _nombre(p.val)
        if p.type == "var":
            return E() if p.val == "e" else Var(p.val)
        if p.type == "fn":
            self.attendre("(")
            arg = self.somme()
            self.attendre(")")
            if p.val == "sqrt":
                return Fn("sqrt", arg)
            if p.val == "exp":
                return Pow(E(), arg)
            if p.val == "ln":
                return Log(arg, E())
            return Log(arg, _base(p.base))
        if p.val == "(":
            n = self.somme()
            self.attendre(")")
            return n
        if p.val == ")":
            raise ErreurSaisie("Parenthèse fermante en trop.")
        if p.val in _INEGALITES:
            raise ErreurSaisie("Les inéquations ne sont pas traitées par cet outil : écrivez une équation avec =.")
        raise ErreurSaisie(f"Il manque un terme avant « {p.val} ».")


def lire_membres(texte):
    """(gauche, droite) d'une équation, ou (expression, None). Syntaxe seulement : une inconnue ou une lettre e déplacée
    se détecte dans `analyser_saisie`."""
    toks = tokeniser(texte)
    if not toks:
        raise ErreurSaisie("Écrivez une équation, par exemple 3^(x+1) = 27.")
    if any(t.type == "op" and t.val in _INEGALITES for t in toks):
        raise ErreurSaisie("Les inéquations ne sont pas traitées par cet outil : écrivez une équation avec =.")
    egaux = [i for i, t in enumerate(toks) if t.type == "op" and t.val == "="]
    if len(egaux) > 1:
        raise ErreurSaisie("Un seul signe = dans une équation.")
    if not egaux:
        return _Parseur(toks).tout(), None
    cote = [toks[:egaux[0]], toks[egaux[0] + 1:]]
    if not cote[0] or not cote[1]:
        raise ErreurSaisie("Il manque un membre de l'équation (avant ou après le signe =).")
    return _Parseur(cote[0]).tout(), _Parseur(cote[1]).tout()


# =====================================================================
# 5. SAISIE VALIDE : ÉQUATION À UNE INCONNUE, OU LOGARITHME À CALCULER
# =====================================================================
Saisie = namedtuple("Saisie", "genre g d inconnue")      # genre : « equation » ou « calcul » (d et inconnue : None)


def analyser_saisie(texte):
    g, d = lire_membres(texte)
    if d is None:
        if variables(g):
            raise ErreurSaisie("Écrivez une équation (avec =), ou une expression sans lettre pour calculer un logarithme.")
        return Saisie("calcul", g, None, None)
    inconnues = sorted(variables(g) | variables(d))
    if not inconnues:
        raise ErreurSaisie(MESSAGE_E if contient_e(g) or contient_e(d) else "Il faut une inconnue : une lettre, par exemple x.")
    if len(inconnues) > 1:
        raise ErreurSaisie("Une seule inconnue : vous avez écrit " + " et ".join(inconnues) + ".")
    return Saisie("equation", g, d, inconnues[0])


# =====================================================================
# 6. APERÇU
# =====================================================================
def apercu(texte):
    try:
        g, d = lire_membres(texte)
        return {"ok": True, "tex": tex_saisie(g, d)}
    except ErreurSaisie as e:
        return {"ok": False, "erreur": str(e)}


def apercu_json(texte):
    return json_strict(apercu(texte))


# =====================================================================
# 7. ARITHMÉTIQUE EXACTE ET VALEUR NUMÉRIQUE
# =====================================================================
class _Hors(Exception):
    """La forme sort de ce que la méthode sait traiter : la méthode ne s'applique pas (ce n'est pas une erreur de saisie)."""


def _premiers(n):
    """Décomposition en facteurs premiers {p: exposant} d'un entier n ≥ 1 (division d'essai)."""
    if n > 10 ** 12:
        raise _Hors
    f, p = {}, 2
    while p * p <= n:
        while n % p == 0:
            f[p] = f.get(p, 0) + 1
            n //= p
        p += 1 if p == 2 else 2
    if n > 1:
        f[n] = f.get(n, 0) + 1
    return f


def _racine_primitive(q):
    """Le rationnel r > 1 tel que q = r^k ou q = r^(-k) avec k entier maximal : 8 → 2, 1/16 → 2, 9/4 → 3/2, 10 → 10."""
    num, den = _premiers(q.numerator), _premiers(q.denominator)
    ex = {p: num.get(p, 0) - den.get(p, 0) for p in set(num) | set(den)}
    g = 0
    for e in ex.values():
        g = gcd(g, abs(e))
    r = F(1)
    for p, e in ex.items():
        r *= F(p) ** (e // g)
    return r if r > 1 else 1 / r


def _exposant_entier(q, b):
    """L'entier k tel que b^k = q (b > 1), ou None."""
    if q == 1:
        return 0
    if q < 1:
        k = _exposant_entier(1 / q, b)
        return None if k is None else -k
    k, v = 0, F(1)
    while v < q:
        v *= b
        k += 1
    return k if v == q else None


def _racine_carree(q):
    """Racine carrée exacte d'un rationnel ≥ 0, ou None."""
    a, b = isqrt(q.numerator), isqrt(q.denominator)
    return F(a, b) if a * a == q.numerator and b * b == q.denominator else None


def _const(n):
    """Valeur exacte (Fraction) d'un arbre sans inconnue, ou None si elle n'est pas rationnelle."""
    if isinstance(n, Nb):
        return n.val
    if isinstance(n, Neg):
        v = _const(n.a)
        return None if v is None else -v
    if isinstance(n, Op):
        a, b = _const(n.a), _const(n.b)
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
        a, b = _const(n.a), _const(n.b)
        if a is None or b is None or b.denominator != 1 or abs(b) > 64 or (a == 0 and b < 0):
            return None
        return a ** int(b)
    if isinstance(n, Fn):
        a = _const(n.a)
        return None if a is None or a < 0 else _racine_carree(a)
    return None


def valeur(n, x=None):
    """Valeur numérique (float) d'un arbre ; x : valeur de l'inconnue. Sert aux valeurs « ≈ » et aux contrôles."""
    if isinstance(n, Nb):
        return float(n.val)
    if isinstance(n, Var):
        return float(x)
    if isinstance(n, E):
        return math.e
    if isinstance(n, Neg):
        return -valeur(n.a, x)
    if isinstance(n, Op):
        a, b = valeur(n.a, x), valeur(n.b, x)
        return a + b if n.op == "+" else a - b if n.op == "-" else a * b if n.op == "*" else a / b
    if isinstance(n, Pow):
        return valeur(n.a, x) ** valeur(n.b, x)
    if isinstance(n, Fn):
        return math.sqrt(valeur(n.a, x))
    if isinstance(n, Log):
        v = math.log(valeur(n.a, x))
        return v / (math.log(10) if n.base is None else math.log(valeur(n.base, x)))
    raise TypeError(n)


# polynômes en l'inconnue, degré ≤ 2 : liste [c0, c1, c2] de Fractions
def _pnet(p):
    p = list(p)
    while len(p) > 1 and p[-1] == 0:
        p.pop()
    return p


def _padd(a, b, signe=1):
    n = max(len(a), len(b))
    return _pnet([(a[i] if i < len(a) else 0) + signe * (b[i] if i < len(b) else 0) for i in range(n)])


def _pmul(a, b):
    r = [F(0)] * (len(a) + len(b) - 1)
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            r[i + j] += x * y
    r = _pnet(r)
    if len(r) > 3:
        raise _Hors
    return r


def _poly(n, x):
    """Coefficients de n (polynôme de degré ≤ 2 en x à coefficients rationnels), sinon _Hors."""
    if not variables(n):
        v = _const(n)
        if v is None:
            raise _Hors
        return [v]
    if isinstance(n, Var):
        return [F(0), F(1)]
    if isinstance(n, Neg):
        return [-c for c in _poly(n.a, x)]
    if isinstance(n, Op):
        if n.op in "+-":
            return _padd(_poly(n.a, x), _poly(n.b, x), 1 if n.op == "+" else -1)
        if n.op == "*":
            return _pmul(_poly(n.a, x), _poly(n.b, x))
        d = _const(n.b)
        if d is None or d == 0:
            raise _Hors
        return [c / d for c in _poly(n.a, x)]
    if isinstance(n, Pow) and isinstance(n.a, Var):
        k = _const(n.b)
        if k in (0, 1, 2):
            r = [F(1)]
            for _ in range(int(k)):
                r = _pmul(r, [F(0), F(1)])
            return r
    raise _Hors


def _arbre_poly(p, x="x"):
    """Arbre d'un polynôme, écrit comme on l'écrit à la main : x² + 2x − 3, −2x + 1, ½x."""
    termes = [(c, k) for k, c in reversed(list(enumerate(p))) if c != 0]
    if not termes:
        return Nb(0)

    def monome(c, k):
        if k == 0:
            return Nb(c)
        xk = Var(x) if k == 1 else Pow(Var(x), Nb(k))
        return xk if c == 1 else Op("*", Nb(c), xk)

    c0, k0 = termes[0]
    n = monome(abs(c0), k0)
    if c0 < 0:
        n = Neg(n)
    for c, k in termes[1:]:
        n = Op("-" if c < 0 else "+", n, monome(abs(c), k))
    return n


# =====================================================================
# 8. CORRIGÉ : ÉQUATIONS, CHAÎNES, CARTES
# =====================================================================
class Eq:
    """Une équation g = d (arbres)."""
    __slots__ = ("g", "d")

    def __init__(self, g, d):
        self.g, self.d = g, d

    def __eq__(self, o):
        return isinstance(o, Eq) and (self.g, self.d) == (o.g, o.d)

    def __hash__(self):
        return hash((self.g, self.d))

    def __repr__(self):
        return f"Eq({self.g!r}, {self.d!r})"


class Ou:
    """x = a ou x = b : plusieurs équations dont une au moins est vraie."""
    __slots__ = ("eqs",)

    def __init__(self, eqs):
        self.eqs = list(eqs)


class Chaine:
    """Une ligne du corrigé : éléments (arbres, Eq ou Ou) reliés par « = » (expressions) ou « ⇔ » (équations), chaque lien avec
    sa propriété (texte) ou None quand le calcul est évident."""

    def __init__(self, elements, liens=(), props=()):
        self.elements, self.liens, self.props = list(elements), list(liens), list(props)
        assert len(self.liens) == len(self.props) == len(self.elements) - 1

    def ajouter(self, element, lien, prop=None):
        self.elements.append(element)
        self.liens.append(lien)
        self.props.append(prop)
        return self


def tex_element(e):
    if isinstance(e, Eq):
        return tex(e.g) + " = " + tex(e.d)
    if isinstance(e, Ou):
        return r" \text{ ou } ".join(tex_element(q) for q in e.eqs)
    return tex(e)


def tex_chaine(c):
    """TeX d'une ligne : la propriété de chaque lien suit l'élément qu'elle justifie, entre parenthèses."""
    s = tex_element(c.elements[0])
    for e, lien, prop in zip(c.elements[1:], c.liens, c.props):
        s += (r" \iff " if lien == "⇔" else " = ") + tex_element(e)
        if prop:
            s += r" \quad \text{(" + prop + ")}"
    return s


PROP_PUISSANCE = "(aᵐ)ⁿ = aᵐⁿ"
PROP_PRODUIT = "aᵐ · aⁿ = aᵐ⁺ⁿ"
PROP_UN = "1 = a⁰"
PROP_MEME_BASE = "même base : a^A = a^B ⇔ A = B"
PROP_ISOLER = "on isole le terme exponentiel"
PROP_PRODUIT_NUL = "un produit est nul si l'un des facteurs est nul"
PROP_DISCRIMINANT = "formule du discriminant"
PROPRIETES = frozenset({PROP_PUISSANCE, PROP_PRODUIT, PROP_UN, PROP_MEME_BASE, PROP_ISOLER, PROP_PRODUIT_NUL, PROP_DISCRIMINANT})


def _carte(titre, lignes):
    return {"titre": titre, "lignes": lignes}


def _produit(arbres):
    n = arbres[0]
    for a in arbres[1:]:
        n = Op("*", n, a)
    return n


# =====================================================================
# 9. MÉTHODE « MÊME BASE » : a^A = a^B ⇔ A = B
# =====================================================================
class _Fac:
    """Un facteur d'un membre : « pow » = base^exposant (base rationnelle > 0, différente de 1, exposant polynôme),
    « cte » = constante rationnelle > 0. `arbre` : le facteur tel qu'écrit ; `imbrique` : (aᵐ)ⁿ écrit comme tel ;
    `base_ecrite` : la base telle qu'écrite (nœud) ; `expo_ecrit` : l'exposant tel qu'écrit (nœud) quand il n'est pas recomposé."""
    __slots__ = ("genre", "base", "exp", "arbre", "imbrique", "base_ecrite", "expo_ecrit")

    def __init__(self, genre, base, exp, arbre, imbrique=False, base_ecrite=None, expo_ecrit=None):
        self.genre, self.base, self.exp, self.arbre = genre, base, exp, arbre
        self.imbrique, self.base_ecrite, self.expo_ecrit = imbrique, base_ecrite, expo_ecrit


def _aplatir(n):
    return _aplatir(n.a) + _aplatir(n.b) if isinstance(n, Op) and n.op == "*" else [n]


def _base_valide(a):
    return isinstance(a, Nb) and a.val > 0 and a.val != 1


def _facteur(f, x):
    if not variables(f):
        if isinstance(f, Pow) and _base_valide(f.a):
            k = _const(f.b)
            if k is not None:
                return _Fac("pow", f.a.val, [k], f, False, f.a, f.b)
        v = _const(f)
        if v is None or v <= 0:
            raise _Hors
        return _Fac("cte", v, None, f)
    if not isinstance(f, Pow):
        raise _Hors
    if variables(f.b) and not variables(f.a):
        g = _poly(f.b, x)
        a = f.a
        if _base_valide(a):
            return _Fac("pow", a.val, g, f, False, a, f.b)
        if isinstance(a, Pow) and _base_valide(a.a) and _const(a.b) is not None:         # (10²)^x
            return _Fac("pow", a.a.val, _pmul([_const(a.b)], g), f, True, a.a)
        v = _const(a)
        if v is None or v <= 0 or v == 1:
            raise _Hors
        return _Fac("pow", v, g, f, False, a, f.b)
    if not variables(f.b):
        k = _const(f.b)
        interne = _facteur(f.a, x)
        if k is None or interne.genre != "pow" or interne.imbrique:           # (25^x)²
            raise _Hors
        return _Fac("pow", interne.base, _pmul(interne.exp, [k]), f, True, interne.base_ecrite)
    raise _Hors


def _facteurs(n, x):
    return [_facteur(f, x) for f in _aplatir(n)]


def _isoler(g, d, x):
    """Isole le terme qui contient l'inconnue quand l'autre membre est une constante : T + c, T − c, c − T, c·T, T/c, −T.
    Renvoie (g', d', chaîne ou None)."""
    if variables(g) and not variables(d):
        a, b, inverse = g, d, False
    elif variables(d) and not variables(g):
        a, b, inverse = d, g, True
    else:
        return g, d, None
    o = _const(b)
    if o is None:
        raise _Hors
    equation = lambda s, t: Eq(t, s) if inverse else Eq(s, t)
    chaine = Chaine([equation(a, b)])
    while True:
        if isinstance(a, Op) and a.op in "+-" and not variables(a.b):
            c = _const(a.b)
            a, o = a.a, (o - c if a.op == "+" else o + c)
        elif isinstance(a, Op) and a.op in "+-" and not variables(a.a):
            c = _const(a.a)
            a, o = (a.b, o - c) if a.op == "+" else (a.b, c - o)
        elif isinstance(a, Op) and a.op == "*" and not variables(a.a) and _const(a.a):
            a, o = a.b, o / _const(a.a)
        elif isinstance(a, Op) and a.op == "*" and not variables(a.b) and _const(a.b):
            a, o = a.a, o / _const(a.b)
        elif isinstance(a, Op) and a.op == "/" and not variables(a.b) and _const(a.b):
            a, o = a.a, o * _const(a.b)
        elif isinstance(a, Neg):
            a, o = a.a, -o
        else:
            break
        if o is None:
            raise _Hors
        chaine.ajouter(equation(a, Nb(o)), "⇔", PROP_ISOLER)
    if not chaine.liens:
        return g, d, None
    return (Nb(o), a, chaine) if inverse else (a, Nb(o), chaine)


def _choisir_base(facs):
    """La base commune : une base déjà écrite (> 1) dont tout le reste est une puissance entière, sinon la racine primitive."""
    valeurs = [f.base for f in facs if not (f.genre == "cte" and f.base == 1)]
    if not valeurs:
        raise _Hors
    racines = {_racine_primitive(v) for v in valeurs}
    if len(racines) != 1:
        raise _Hors
    for b in sorted({f.base for f in facs if f.genre == "pow" and f.base > 1}):
        if all(_exposant_entier(v, b) is not None for v in valeurs):
            return b
    return racines.pop()


def _expo_arbre(f):
    return f.expo_ecrit if f.expo_ecrit is not None else _arbre_poly(f.exp)


def _etapes_membre(n, x, base0, b0):
    """(arbre final, chaîne ou None) du membre `n` récrit en base `base0` : (aᵐ)ⁿ, changement de base, aᵐ · aⁿ."""
    facs = _facteurs(n, x)
    changes = [f.genre == "cte" or f.base != base0 for f in facs]
    k_de = [_exposant_entier(f.base, base0) for f in facs]
    # T1 : (aᵐ)ⁿ écrit dans l'énoncé
    t1 = [Pow(f.base_ecrite, _arbre_poly(f.exp)) if f.imbrique else f.arbre for f in facs]
    # T2 : la base écrite comme puissance de base0
    t2 = []
    for f, ch, k, t in zip(facs, changes, k_de, t1):
        if f.genre == "cte":
            t2.append(Pow(b0, Nb(k)))
        elif ch:
            t2.append(Pow(Pow(b0, Nb(k)), f.expo_ecrit if f.expo_ecrit is not None and not f.imbrique else _arbre_poly(f.exp)))
        else:
            t2.append(t)
    # T3 : (aᵐ)ⁿ = aᵐⁿ, l'exposant k·f laissé factorisé quand f est une somme
    t3 = []
    for f, ch, k, t in zip(facs, changes, k_de, t2):
        if f.genre == "pow" and ch:
            somme = sum(1 for c in f.exp if c != 0) >= 2
            e = Op("*", Nb(k), _expo_arbre(f)) if somme else _arbre_poly([k * c for c in f.exp])
            t3.append(Pow(b0, e))
        else:
            t3.append(t)
    # T4 : exposants développés
    t4 = []
    for f, ch, k, t in zip(facs, changes, k_de, t3):
        t4.append(Pow(b0, _arbre_poly([k * c for c in f.exp])) if f.genre == "pow" and ch else t)
    # T5 : aᵐ · aⁿ = aᵐ⁺ⁿ
    total = [F(0)]
    for f, k in zip(facs, k_de):
        total = _padd(total, [F(k)] if f.genre == "cte" else [k * c for c in f.exp])
    t5 = [Pow(b0, _arbre_poly(total))] if len(facs) > 1 else t4
    un = any(f.genre == "cte" and f.base == 1 for f in facs)
    etapes = [(n, None), (_produit(t1), PROP_PUISSANCE), (_produit(t2), PROP_UN if un else None),
              (_produit(t3), PROP_PUISSANCE), (_produit(t4), None), (_produit(t5), PROP_PRODUIT)]
    chaine = Chaine([n])
    for arbre, prop in etapes[1:]:
        if tex(arbre) != tex(chaine.elements[-1]):
            chaine.ajouter(arbre, "=", prop)
    fin = chaine.elements[-1]
    return fin, (chaine if chaine.liens else None)


def _exposant_final(n):
    """L'exposant A d'un membre écrit a^A."""
    if isinstance(n, Pow):
        return n.b
    raise _Hors


def _resoudre_polynome(A, B, At, Bt, x):
    """Lignes du corrigé pour A = B (polynômes de degré ≤ 2) : (lignes, solutions, remarque). `solutions` : liste de nœuds, ou
    None quand tout réel convient."""
    P = _padd(A, B, -1)
    X = Var(x)
    c = Chaine([Eq(At, Bt)])
    lignes = [c]
    if not any(P):
        return lignes, None, "Cette égalité est vraie pour tout nombre réel."
    if len(P) == 1:
        c.ajouter(Eq(Nb(A[0]), Nb(B[0])), "⇔")
        return lignes, [], "Cette égalité est fausse : l'équation n'a aucune solution."
    if len(P) == 2:
        p, q = (A[1] if len(A) > 1 else F(0)), A[0]
        r, s = (B[1] if len(B) > 1 else F(0)), B[0]
        cx, second = (r, q - s) if p == 0 else (p - r, s - q)
        e1 = Eq(_arbre_poly([F(0), cx]), Nb(second))
        if tex_element(e1) != tex_element(c.elements[-1]):
            c.ajouter(e1, "⇔")
        if cx != 1:
            c.ajouter(Eq(X, Nb(second / cx)), "⇔")
        return lignes, [Nb(second / cx)], None
    if any(v.denominator != 1 for v in P):
        raise _Hors
    c0, b, a = (int(v) for v in P)
    standard = Eq(_arbre_poly(P), Nb(0))
    if tex_element(standard) != tex_element(c.elements[-1]):
        c.ajouter(standard, "⇔")
    delta = b * b - 4 * a * c0
    if delta >= 0:
        k = isqrt(delta)
        if k * k == delta and a == 1 and (-b + k) % 2 == 0:
            r1, r2 = sorted([F(-b - k, 2), F(-b + k, 2)])
            facteur = lambda r: X if r == 0 else Op("-", X, Nb(r)) if r > 0 else Op("+", X, Nb(-r))
            c.ajouter(Eq(Op("*", facteur(r1), facteur(r2)), Nb(0)), "⇔")
            racines = [r1] if r1 == r2 else [r1, r2]
            c.ajouter(Ou(Eq(X, Nb(r)) for r in racines), "⇔", PROP_PRODUIT_NUL)
            return lignes, [Nb(r) for r in racines], None
    d_ligne = Chaine([Var("Δ"), Op("-", Pow(Nb(b), Nb(2)), Op("*", Op("*", Nb(4), Nb(a)), Nb(c0))), Nb(delta)], ["=", "="],
                     [None, None])
    lignes.append(d_ligne)
    if delta < 0:
        return lignes, [], "Δ < 0 : l'équation n'a aucune solution réelle."
    racines = _racines_du_second_degre(a, b, delta)
    fin = Chaine([Ou(Eq(X, r) for r in racines)])
    lignes.append(fin)
    return lignes, racines, None


def _racines_du_second_degre(a, b, delta):
    k, m = 1, delta
    for p, e in _premiers(delta).items() if delta else []:
        k *= p ** (e // 2)
        m = m // p ** (2 * (e // 2))
    if m == 1:
        r = sorted({F(-b - k, 2 * a), F(-b + k, 2 * a)})
        return [Nb(v) for v in r]
    g = gcd(gcd(abs(b), k), abs(2 * a))
    bb, kk, dd = -b // g, k // g, 2 * a // g
    if dd < 0:
        bb, kk, dd = -bb, kk, -dd
    racine = Fn("sqrt", Nb(m))
    terme = racine if kk == 1 else Op("*", Nb(kk), racine)

    def racine_signe(signe):
        if bb == 0:
            haut = terme if signe > 0 else Neg(terme)
        else:
            haut = Op("+" if signe > 0 else "-", Nb(bb), terme)
        return haut if dd == 1 else Op("/", haut, Nb(dd))

    return [racine_signe(-1), racine_signe(1)]


def meme_base(g, d, x):
    """Corrigé de g = d par la méthode « même base », ou None si elle ne s'applique pas (la constante n'est pas une puissance de la
    base, second membre ≤ 0, exposant non polynomial…). Renvoie {genre, inconnue, enonce, base, etapes, solutions, remarque}."""
    try:
        return _meme_base(g, d, x)
    except _Hors:
        return None


def _meme_base(g, d, x):
    enonce = Eq(g, d)
    etapes = []
    g, d, iso = _isoler(g, d, x)
    if iso is not None:
        etapes.append(_carte("Isoler l'exponentielle", [iso]))
    fg, fd = _facteurs(g, x), _facteurs(d, x)
    if not any(f.genre == "pow" and variables(f.arbre) for f in fg + fd):
        raise _Hors
    base0 = _choisir_base(fg + fd)
    b0 = next((f.base_ecrite for f in fg + fd if f.genre == "pow" and f.base == base0 and isinstance(f.base_ecrite, Nb)), Nb(base0))
    g2, chaine_g = _etapes_membre(g, x, base0, b0) if _a_changer(fg, base0) else (g, None)
    d2, chaine_d = _etapes_membre(d, x, base0, b0) if _a_changer(fd, base0) else (d, None)
    lignes = [c for c in (chaine_g, chaine_d) if c is not None]
    if lignes:
        etapes.append(_carte("Même base", lignes))
    A_tree, B_tree = _exposant_final(g2), _exposant_final(d2)
    A, B = _poly(A_tree, x), _poly(B_tree, x)
    l_exp, solutions, remarque = _resoudre_polynome(A, B, A_tree, B_tree, x)
    debut = Eq(g2, d2)
    premiere = l_exp[0]
    ligne = Chaine([debut], [], [])
    ligne.ajouter(premiere.elements[0], "⇔", PROP_MEME_BASE)
    for e, lien, prop in zip(premiere.elements[1:], premiere.liens, premiere.props):
        ligne.ajouter(e, lien, prop)
    etapes.append(_carte("Égalité des exposants", [ligne] + l_exp[1:]))
    return {"genre": "meme_base", "inconnue": x, "enonce": enonce, "base": base0, "etapes": etapes,
            "solutions": solutions, "remarque": remarque}


def _a_changer(facs, base0):
    return len(facs) > 1 or any(f.genre == "cte" or f.base != base0 or f.imbrique for f in facs)
