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
import random
import re
from collections import namedtuple
from functools import reduce
from math import gcd, isqrt

from noyau import ErreurSaisie, json_strict
from nombres import (MOTIF_ESPACE_DANS_UN_NOMBRE, MOTIF_SAISIE, formater_decimal, formater_entier, nettoyer_saisie)

__all__ = ["Nb", "Var", "E", "Neg", "Op", "Pow", "Fn", "Log", "tex", "variables", "lire_membres", "analyser_saisie", "tex_saisie",
           "apercu", "apercu_json", "Saisie"]

MESSAGE_E = "La lettre e désigne le nombre e ≈ 2,718 : choisissez une autre lettre pour l'inconnue."
MESSAGE_EXPOSANT = "Mettez l'exposant entre parenthèses : e^(-0,02t)."
MESSAGE_HORS_PROGRAMME = "Cette équation ne se résout pas avec les méthodes du cours."
MESSAGE_PAS_ENCORE = "Cet outil ne traite pas encore ce type d'équation."
MESSAGE_PAS_UN_LOGARITHME = "Écrivez une équation (avec =) ou un logarithme à calculer, par exemple log_2(50)."
MESSAGE_CALCUL_PAS_ENCORE = "Cet outil ne traite pas encore ce type de calcul."
MESSAGE_ARGUMENT_NON_POSITIF = "Le logarithme d'un nombre négatif ou nul n'est pas défini."


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
    """Notation suisse (Q5) : ’ dès 4 chiffres sur la partie entière, virgule décimale (moteur/nombres.py)."""
    v = n.val
    if n.dec is not None:
        s = formater_decimal(n.dec, tex=True)
    elif v.denominator == 1:
        s = formater_entier(abs(v.numerator), tex=True)
    else:
        s = r"\frac{" + formater_entier(abs(v.numerator), tex=True) + "}{" + formater_entier(v.denominator, tex=True) + "}"
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


def _fonction_inconnue(s, i):
    """Le nom (sin, cos, tan, lg…) si les lettres qui commencent en s[i] forment au moins deux lettres suivies d'une parenthèse sans se
    terminer par un nom de fonction connu (xlog(x) reste x · log(x)) ; sinon None."""
    j = i
    while j < len(s) and s[j].isalpha() and s[j].isascii():
        j += 1
    k = j
    while k < len(s) and s[k].isspace():
        k += 1
    if j - i < 2 or s[k:k + 1] != "(" or s[i:j].endswith(("sqrt", "exp", "log", "ln")):
        return None
    return s[i:j]


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
            m = MOTIF_SAISIE.match(s, i)
            if not m:
                raise ErreurSaisie(f"Caractère non reconnu : « {c} ».")
            suivant = s[m.end():m.end() + 1]
            if suivant in ("'", "’") or (suivant.isdigit() and ("'" in m.group(0) or "’" in m.group(0))):
                raise ErreurSaisie("Une apostrophe dans un nombre est suivie d'exactement 3 chiffres : 1’000.")
            if m.group(0).isdigit() and MOTIF_ESPACE_DANS_UN_NOMBRE.match(s, m.end()):
                raise ErreurSaisie("Pas d'espace dans un nombre : écrivez 1000 ou 1’000.")
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
                inconnue = _fonction_inconnue(s, i)
                if inconnue:
                    raise ErreurSaisie(f"La fonction {inconnue} n'est pas traitée par cet outil.")
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
    t = nettoyer_saisie(brut)
    return Nb(F(t), t.replace(".", ",") if "." in t else None)


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
    """L'entier k tel que b^k = q (b > 0, b ≠ 1), ou None."""
    if q == 1:
        return 0
    if b < 1:
        k = _exposant_entier(q, 1 / b)
        return None if k is None else -k
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


def _nb_ecrit(v, arbre=None):
    """Nb(v) écrit comme dans l'énoncé quand v y figure en décimal (−0,02 ; 1,045), en fraction sinon."""
    def cherche(n):
        if isinstance(n, Nb):
            return n if n.dec is not None and abs(n.val) == abs(v) else None
        enfants = [getattr(n, nom, None) for nom in getattr(n, "__slots__", ()) if nom != "nom"]
        return next((r for r in (cherche(e) for e in enfants if isinstance(e, Noeud)) if r is not None), None)
    v, trouve = F(v), (cherche(arbre) if arbre is not None else None)
    return Nb(v, trouve.dec) if trouve is not None else Nb(v)


def _arbre_poly(p, x="x", ecrit=None):
    """Arbre d'un polynôme, écrit comme on l'écrit à la main : x² + 2x − 3, −2x + 1, ½x. `ecrit` : l'arbre de l'énoncé, qui garde ses décimaux."""
    termes = [(c, k) for k, c in reversed(list(enumerate(p))) if c != 0]
    if not termes:
        return Nb(0)

    def monome(c, k):
        if k == 0:
            return _nb_ecrit(c, ecrit)
        xk = Var(x) if k == 1 else Pow(Var(x), Nb(k))
        return xk if c == 1 else Op("*", _nb_ecrit(c, ecrit), xk)

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
    __slots__ = ("g", "d", "milieu")

    def __init__(self, g, d, milieu=()):
        """`milieu` : écritures intermédiaires de d, affichées entre g et d (x = 10³ = 1000) ; d est la dernière."""
        self.g, self.d, self.milieu = g, d, list(milieu)

    def __eq__(self, o):
        return isinstance(o, Eq) and (self.g, self.d) == (o.g, o.d)

    def __hash__(self):
        return hash((self.g, self.d))

    def __repr__(self):
        return f"Eq({self.g!r}, {self.d!r})"


class Rel:
    """Une relation d'ordre g < d, g ≤ d, g > d (arbres), par exemple 5^(8x) > 0."""
    SIGNES = {"<": " < ", ">": " > ", "≤": r" \le ", "≥": r" \ge "}
    __slots__ = ("g", "signe", "d")

    def __init__(self, g, signe, d):
        self.g, self.signe, self.d = g, signe, d


class Positif:
    """« u = valeur > 0 » : vérification que l'argument d'un logarithme est strictement positif."""
    __slots__ = ("expr", "valeur")

    def __init__(self, expr, valeur):
        self.expr, self.valeur = expr, valeur


class Texte:
    """Une condition déjà écrite en TeX (x > 0 et x ≠ 1) ; `detail` : un complément en TeX qui s'affiche entre parenthèses, à droite de la
    ligne dans la page (l'encadrement 2⁵ = 32 < 50 < 64 = 2⁶)."""
    __slots__ = ("tex", "detail")

    def __init__(self, tex, detail=None):
        self.tex, self.detail = tex, detail


class Ou:
    """x = a ou x = b : plusieurs équations dont une au moins est vraie."""
    __slots__ = ("eqs",)

    def __init__(self, eqs):
        self.eqs = list(eqs)


class Chaine:
    """Une ligne du corrigé : éléments (arbres, Eq ou Ou) reliés par « = » (expressions) ou « ⇔ » (équations), chaque lien avec
    sa propriété (texte) ou None quand le calcul est évident."""

    def __init__(self, elements, liens=(), props=(), note=None):
        self.elements, self.liens, self.props, self.note = list(elements), list(liens), list(props), note
        assert len(self.liens) == len(self.props) == len(self.elements) - 1

    def ajouter(self, element, lien, prop=None):
        self.elements.append(element)
        self.liens.append(lien)
        self.props.append(prop)
        return self


def tex_element(e):
    if isinstance(e, Eq):
        return tex(e.g) + "".join(" = " + tex(m) for m in e.milieu) + " = " + tex(e.d)
    if isinstance(e, Positif):
        return tex(e.expr) + " = " + tex(e.valeur) + " > 0"
    if isinstance(e, Texte):
        return e.tex + (r" \quad (" + e.detail + ")" if e.detail else "")
    if isinstance(e, Ou):
        return r" \text{ ou } ".join(tex_element(q) for q in e.eqs)
    if isinstance(e, Rel):
        return tex(e.g) + Rel.SIGNES[e.signe] + tex(e.d)
    return tex(e)


def tex_chaine(c):
    """TeX d'une ligne : la propriété de chaque lien suit l'élément qu'elle justifie, entre parenthèses."""
    s = tex_element(c.elements[0])
    for e, lien, prop in zip(c.elements[1:], c.liens, c.props):
        s += (r" \iff " if lien == "⇔" else " = ") + tex_element(e)
        if isinstance(prop, Car):
            s += r" \quad \text{(car } " + tex(prop.expr) + r" \neq 0\text{)}"
        elif prop:
            s += r" \quad \text{(" + prop + ")}"
    if c.note:
        s += r" \quad \text{(" + c.note + ")}" + (r" \; \checkmark" if c.note == PROP_BIEN_DEFINI else "")
    return s


def _gauche(e):
    """TeX du membre de gauche auquel un lien « = » se rattache : x dans `x = N/D`, l'expression elle-même dans une chaîne de « = »."""
    if isinstance(e, Eq):
        return tex(e.g)
    if isinstance(e, (Positif, Texte, Ou, Rel)):
        return None
    return tex(e)


def rangees_chaine(c):
    """La chaîne en lignes alignées, une étape par ligne comme le corrigé : [(lien, expression, propriété)], les trois en TeX/texte.
    `lien` : « \\iff » ou vide ; `expression` : un élément après un « ⇔ » ; les liens « = » prolongent la ligne (`√2 = 2^(1/2) = 4^(1/4)`)
    jusqu'à une propriété, après laquelle la suite commence une nouvelle ligne `{} = suite`, alignée sous le « = » précédent ;
    `propriété` : le texte entre parenthèses (le TeX y est entre `\\(` et `\\)`), ou None. La page met le lien dans une première colonne,
    l'expression dans la deuxième et la propriété à droite (sous l'expression sur un écran étroit)."""
    premier = c.elements[0]
    rangees = [["", premier.tex if isinstance(premier, Texte) else tex_element(premier),
                r"(\(" + premier.detail + r"\))" if isinstance(premier, Texte) and premier.detail else None]]
    ancre = _gauche(premier)
    for e, lien, prop in zip(c.elements[1:], c.liens, c.props):
        if lien == "⇔":
            rangees.append([r"\iff", tex_element(e), None])
            ancre = _gauche(e)
        elif rangees[-1][2] is None:                                  # pas de propriété sur la ligne : la suite d'égalités continue
            rangees[-1][1] += " = " + tex_element(e)
        else:                                                         # nouvelle ligne, son « = » sous celui de la ligne d'au-dessus
            cale = r"\phantom{" + ancre + "}" if ancre and len(ancre) <= 30 else ""
            rangees.append(["", cale + " = " + tex_element(e), None])
        if isinstance(prop, Car):
            rangees[-1][2] = r"(car \(" + tex(prop.expr) + r" \neq 0\))"
        elif prop:
            rangees[-1][2] = "(" + prop + ")"
    if c.note:
        note = "(" + c.note + ")" + (r" \(\checkmark\)" if c.note == PROP_BIEN_DEFINI else "")
        rangees[-1][2] = note if rangees[-1][2] is None else rangees[-1][2] + " " + note
    return [tuple(r) for r in rangees]


PROP_PUISSANCE = "(aᵐ)ⁿ = aᵐⁿ"
PROP_PRODUIT = "aᵐ · aⁿ = aᵐ⁺ⁿ"
PROP_UN = "1 = a⁰"
PROP_MEME_BASE = "même base : a^A = a^B ⇔ A = B"
PROP_ISOLER = "on isole le terme exponentiel"
PROP_PRODUIT_NUL = "un produit est nul si l'un des facteurs est nul"
PROP_DISCRIMINANT = "formule du discriminant"
PROP_DEFINITION_LOG = "définition du logarithme"
PROP_LOG_DEUX_MEMBRES = "log des deux membres"
PROP_LOG_PUISSANCE = "log(a^A) = A · log(a)"
PROP_LOG_10K = "log(10ᵏ) = k"
PROP_LN_UN = "ln(1) = 0"
PROP_EXPO_POSITIVE = "une exponentielle est strictement positive"
PROP_AUCUNE_SOLUTION = "aucune solution"
PROP_LOG_QUOTIENT = "log a − log b = log(a/b)"
PROP_LOG_PRODUIT = "log a + log b = log(ab)"
PROP_LOG_REGROUPER = "propriétés des logarithmes"
PROP_LOG_BASE_PUISSANCE = "log_a(a^k) = k"
PROP_LN_E_PUISSANCE = "ln(e^k) = k"
PROP_CHANGEMENT_DE_BASE = "changement de base"
PROP_ISOLER_LOG = "on isole le logarithme"
PROP_BIEN_DEFINI = "le logarithme est bien défini"
PROP_BASE_LOG = "une base de logarithme est strictement positive et différente de 1"
PROP_SEULE_POSITIVE = "seule la solution positive convient"
PROP_LOG_SOMME = "log(ab) = log a + log b"
PROP_LN_DEUX_MEMBRES = "ln des deux membres"
PROP_LN_E = "ln(e^A) = A"
PROPRIETES = frozenset({PROP_PUISSANCE, PROP_PRODUIT, PROP_UN, PROP_MEME_BASE, PROP_ISOLER, PROP_PRODUIT_NUL, PROP_DISCRIMINANT,
                        PROP_DEFINITION_LOG, PROP_LOG_DEUX_MEMBRES, PROP_LOG_PUISSANCE, PROP_LOG_10K, PROP_LN_UN, PROP_EXPO_POSITIVE,
                        PROP_AUCUNE_SOLUTION, PROP_LOG_QUOTIENT, PROP_LOG_PRODUIT, PROP_LOG_REGROUPER, PROP_LOG_SOMME, PROP_LN_DEUX_MEMBRES, PROP_LN_E,
                        PROP_ISOLER_LOG, PROP_BIEN_DEFINI, PROP_BASE_LOG, PROP_SEULE_POSITIVE, PROP_LOG_BASE_PUISSANCE, PROP_LN_E_PUISSANCE,
                        PROP_CHANGEMENT_DE_BASE})


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


_DECIMAUX = False        # vrai pendant la résolution d'un énoncé qui contient un décimal (voir _avec_decimaux)


def _a_des_decimaux(n):
    """Vrai si l'arbre contient un nombre écrit en décimal (0,7 ; 1,045)."""
    if isinstance(n, Nb):
        return n.dec is not None
    enfants = [getattr(n, nom, None) for nom in getattr(n, "__slots__", ()) if nom != "nom"]
    return any(_a_des_decimaux(e) for e in enfants if isinstance(e, Noeud))


def _avec_decimaux(methode):
    """Pendant l'appel, `_nb_exact` écrit en décimal fini (1,9025 ; 0,27) les valeurs calculées à partir d'un énoncé qui contient un décimal."""
    def appel(*args):
        global _DECIMAUX
        avant, _DECIMAUX = _DECIMAUX, _DECIMAUX or any(_a_des_decimaux(a) for a in args if isinstance(a, Noeud))
        try:
            return methode(*args)
        finally:
            _DECIMAUX = avant
    appel.__name__, appel.__doc__ = methode.__name__, methode.__doc__
    return appel


def _nb_exact(v):
    """Nb(v) pour une valeur exacte calculée (règle R13) : en fraction (5/2, 1/10, 3/2) quand le calcul part d'entiers ou de puissances ;
    en décimal fini (1,9025 ; −0,27) quand l'énoncé contient un décimal et que la valeur est un décimal fini."""
    v = F(v)
    if not _DECIMAUX:
        return Nb(v)
    d, k2, k5 = v.denominator, 0, 0
    while d % 2 == 0:
        d, k2 = d // 2, k2 + 1
    while d % 5 == 0:
        d, k5 = d // 5, k5 + 1
    k = max(k2, k5)
    if v.denominator == 1 or d != 1 or k > 8:
        return Nb(v)
    chiffres = str(int(abs(v) * 10 ** k)).rjust(k + 1, "0")
    return Nb(v, chiffres[:-k] + "," + chiffres[-k:])


def _isoler(g, d, x, prop=None):
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
        chaine.ajouter(equation(a, _nb_exact(o)), "⇔", prop or PROP_ISOLER)
    if not chaine.liens:
        return g, d, None
    return (_nb_exact(o), a, chaine) if inverse else (a, _nb_exact(o), chaine)


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
    # T4 : exposants developpes
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


@_avec_decimaux
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
    A_tree, B_tree = _exposant_final(g2), _exposant_final(d2)
    A, B = _poly(A_tree, x), _poly(B_tree, x)
    l_exp, solutions, remarque = _resoudre_polynome(A, B, A_tree, B_tree, x)
    debut = Eq(g2, d2)
    premiere = l_exp[0]
    ligne = Chaine([debut], [], [])
    ligne.ajouter(premiere.elements[0], "⇔", PROP_MEME_BASE)
    for e, lien, prop in zip(premiere.elements[1:], premiere.liens, premiere.props):
        ligne.ajouter(e, lien, prop)
    # une seule carte « Même base » : la réécriture des membres, puis UNE chaîne de ⇔ (a^A = a^B ⇔ A = B ⇔ … ⇔ solutions)
    etapes.append(_carte("Même base", lignes + [ligne] + l_exp[1:]))
    return {"genre": "meme_base", "inconnue": x, "enonce": enonce, "base": base0, "etapes": etapes,
            "solutions": solutions, "remarque": remarque}


def _a_changer(facs, base0):
    return len(facs) > 1 or any(f.genre == "cte" or f.base != base0 or f.imbrique for f in facs)


# =====================================================================
# 10. MÉTHODE « LOGARITHME » : a^f = b, avec b qui n'est pas une puissance de a
# =====================================================================
def _exponentielle(n, x):
    """(base écrite, valeur de la base ou None pour e, exposant) pour n = a^f : a constante > 0 différente de 1, ou e, f contient l'inconnue."""
    if not (isinstance(n, Pow) and variables(n.b) and not variables(n.a)):
        raise _Hors
    a = n.a
    if isinstance(a, E):
        return a, None, n.b
    if _base_valide(a):
        return a, a.val, n.b
    v = _const(a)
    if v is None or v <= 0 or v == 1:
        raise _Hors
    return a, v, n.b


def _suite_lineaire(chaine, p, q0, c, x, ecrit=None):
    """Ajoute à `chaine` (qui se termine par « p·x + q0 = c ») les lignes qui isolent x ; renvoie la solution (arbre).
    La forme est celle que donne la chaîne : on ne simplifie pas c/p (ln(25/37)/(−0,02), jamais −50·ln(25/37))."""
    haut = c
    if q0 != 0:
        # x + a = c donne c − a ; x − a = c donne a + c (corrigé 2.23 d : x = 1 + 1/log(3), jamais 1/log(3) + 1)
        haut = Op("-", c, _nb_ecrit(q0, ecrit)) if q0 > 0 else Op("+", _nb_ecrit(-q0, ecrit), c)
        chaine.ajouter(Eq(_arbre_poly([F(0), p], x, ecrit), haut), "⇔")
    if p == 1:
        return haut
    solution = Neg(haut) if p == -1 else Op("/", haut, _nb_ecrit(p, ecrit))
    chaine.ajouter(Eq(Var(x), solution), "⇔")
    return solution


@_avec_decimaux
def logarithme(g, d, x):
    """Corrigé de a^f = b par les logarithmes (a constante > 0, ≠ 1, ou e ; f du 1er degré), après avoir isolé l'exponentielle ;
    S = ∅ si le second membre est ≤ 0. None si la méthode ne s'applique pas."""
    try:
        return _logarithme(g, d, x)
    except _Hors:
        return None


def _logarithme(g, d, x):
    enonce = Eq(g, d)
    g, d, iso = _isoler(g, d, x)
    etapes = [_carte("Isoler l'exponentielle", [iso])] if iso is not None else []
    if variables(g) and not variables(d):
        s, o, inverse = g, d, False
    elif variables(d) and not variables(g):
        s, o, inverse = d, g, True
    else:
        raise _Hors
    q = _const(o)
    if q is None:
        raise _Hors
    base, valeur_base, f_tree = _exponentielle(s, x)
    f = _poly(f_tree, x)
    if len(f) != 2:
        raise _Hors
    if q <= 0:
        etapes.append(_carte("Aucune solution", [
            Chaine([Rel(s, ">", Nb(0))], note=PROP_EXPO_POSITIVE),
            Chaine([Rel(o, "<", Nb(0)) if q < 0 else Eq(s, o)], note=PROP_AUCUNE_SOLUTION)]))
        return {"genre": "logarithme", "inconnue": x, "enonce": enonce, "base": valeur_base, "etapes": etapes, "solutions": [],
                "remarque": None}
    if valeur_base is not None and _exposant_entier(q, valeur_base) is not None:
        raise _Hors                                    # b est une puissance de a : méthode « même base »
    chaine = Chaine([Eq(g, d)])
    if inverse:
        chaine.ajouter(Eq(s, o), "⇔")
    if valeur_base == 10 or base_est_e(base):
        if base_est_e(base) and q == 1:
            chaine.ajouter(Eq(f_tree, Nb(0)), "⇔", PROP_LN_UN)
            c = Nb(0)
        else:
            c = Log(o, E() if base_est_e(base) else None)
            chaine.ajouter(Eq(f_tree, c), "⇔", PROP_DEFINITION_LOG)
        titre = "Définition du logarithme"
    else:
        chaine.ajouter(Eq(Log(s, None), Log(o, None)), "⇔", PROP_LOG_DEUX_MEMBRES)
        gauche = Op("*", f_tree, Log(base, None))
        chaine.ajouter(Eq(gauche, Log(o, None)), "⇔", PROP_LOG_PUISSANCE)
        k = _exposant_entier(q, F(10))
        haut = Log(o, None)
        if k is not None:
            haut = Nb(k)
            chaine.ajouter(Eq(gauche, haut), "⇔", PROP_LOG_10K)
        c = Op("/", haut, Log(base, None))
        chaine.ajouter(Eq(f_tree, c), "⇔")
        titre = "Logarithme des deux membres"
    solution = _suite_lineaire(chaine, f[1], f[0], c, x, f_tree)
    etapes.append(_carte(titre, [chaine]))
    return {"genre": "logarithme", "inconnue": x, "enonce": enonce, "base": valeur_base, "etapes": etapes, "solutions": [solution],
            "remarque": None}


def base_est_e(base):
    return isinstance(base, E)


# =====================================================================
# 10 bis. MÉTHODE « BASES DIFFÉRENTES » : k·a^f = m·b^h
# =====================================================================
class Car:
    """Justification « car D ≠ 0 » : on divise par le coefficient logarithmique D (1 − ln 2, log 2 − log 3)."""
    __slots__ = ("expr",)

    def __init__(self, expr):
        self.expr = expr


def _terme(c, avec_x, a, ln):
    """Le terme c · [x] · log(a) sous la forme (c, avec_x, a). a = None : la base e, ln(e) = 1. En base 10, log(10ᵏ) = k : le logarithme
    d'une puissance de 10 devient un nombre (a = None) ; ln(10) n'est pas un nombre."""
    if a is None:
        return (c, avec_x, None)
    k = None if ln else _exposant_entier(a, F(10))
    return (c, avec_x, a) if k is None else (c * k, avec_x, None)


def _oppose(t):
    return (-t[0],) + t[1:]


def _noeud_terme(c, avec_x, a, x, ecrit, ln):
    """|c| · [x] · log(a), le coefficient 1 étant omis ; a = None : le logarithme est déjà un nombre. `ecrit` : la base telle qu'écrite
    dans l'énoncé ((1/2)^x garde log(1/2), pas log(0,5))."""
    c = abs(c)
    coef = _arbre_poly([F(0), c], x) if avec_x else (_nb_exact(c) if c != 1 or a is None else None)
    if a is None:
        return coef
    lg = Log(ecrit.get(a, _nb_exact(a)), E() if ln else None)
    return lg if coef is None else Op("*", coef, lg)


def _fusionner(termes):
    """Les termes de même logarithme (et de même présence de x) additionnés : 2 log 2 + log 2 = 3 log 2 ; les termes nuls disparaissent."""
    vus = {}
    for c, avec_x, a in termes:
        vus[(avec_x, a)] = vus.get((avec_x, a), 0) + c
    return [(c, avec_x, a) for (avec_x, a), c in vus.items() if c != 0]


def _trier(termes):
    """Les termes positifs d'abord (log 3 + 4 log 2, jamais − log 2 + log 3), l'ordre d'écriture sinon."""
    termes = _fusionner(termes)
    return [t for t in termes if t[0] > 0] + [t for t in termes if t[0] < 0]


def _somme(termes, x, ecrit, ln, trier=True):
    """Somme écrite comme à la main : x log 2 − log 2, 3 log 6 − log 4 ; 0 si elle est vide."""
    termes = _trier(termes) if trier else _fusionner(termes)
    n = None
    for c, avec_x, a in termes:
        t = _noeud_terme(c, avec_x, a, x, ecrit, ln)
        n = (Neg(t) if c < 0 else t) if n is None else Op("-" if c < 0 else "+", n, t)
    return Nb(0) if n is None else n


def _regrouper(termes, ecrit):
    """La somme Σ cᵢ · log(aᵢ) (cᵢ entiers, base 10) écrite comme un seul logarithme : (nœud, genre, ligne) ou None si elle n'est pas regroupable.
    genre : « seul » (rien à regrouper), « quotient » (log a − log b), « produit » (log a + log b) ou « general » ;
    ligne : le calcul « car … » (chaîne de « = »), sauf pour « seul »."""
    termes = _trier(termes)
    if any(a is None or c.denominator != 1 for c, _, a in termes):
        return None
    R = F(1)
    for c, _, a in termes:
        R *= a ** int(c)
    if max(R.numerator, R.denominator) > 10 ** 12:
        return None
    k = _exposant_entier(R, F(10))
    final = Nb(k) if k is not None else Log(_nb_exact(R))
    formes = [c for c, _, _ in termes]
    if formes == [1] and k is None:
        return final, "seul", None
    genre = "general" if k is not None else "quotient" if formes == [1, -1] else "produit" if formes == [1, 1] else "general"
    base = lambda a: ecrit.get(a, _nb_exact(a))
    puissance = lambda a, c: base(a) if c == 1 else Pow(base(a), Nb(c))
    haut = [puissance(a, c) for c, _, a in termes if c > 0]
    bas = [puissance(a, -c) for c, _, a in termes if c < 0]
    produit = _produit(haut) if haut else Nb(1)
    if bas:
        produit = Op("/", produit, _produit(bas))
    ligne = Chaine([_somme([(c, False, a) for c, _, a in termes], None, ecrit, False, False)])
    ligne.ajouter(Log(produit), "=", PROP_LOG_REGROUPER)
    if tex(ligne.elements[-1]) != tex(final):
        ligne.ajouter(final, "=", PROP_LOG_10K if k is not None else None)
    return final, genre, ligne


def _cote(n, x):
    """(k, nœud de k, puissance) pour n = a^f ou k·a^f (k constante rationnelle non nulle) ; k = 1 et nœud None sans facteur.
    Un signe moins devant la puissance rend k négatif (le nœud de k ne sert alors pas)."""
    if isinstance(n, Neg):
        k, _, p = _cote(n.a, x)
        return -k, None, p
    if isinstance(n, Op) and n.op == "*":
        for c, p in ((n.a, n.b), (n.b, n.a)):
            if not variables(c) and variables(p):
                k = _const(c)
                if k is None or k == 0:
                    raise _Hors
                return k, (None if k == 1 else c), p
    return F(1), None, n


@_avec_decimaux
def bases_differentes(g, d, x):
    """Corrigé de k·a^f = m·b^h (bases différentes ou base e, f et h du 1er degré, k et m des constantes) : log (ln si une base est e) des deux
    membres, puis les termes en x regroupés comme dans une équation du premier degré (corrigé 2.24). None si la méthode ne s'applique pas."""
    try:
        return _bases_differentes(g, d, x)
    except _Hors:
        return None


def _bases_differentes(g, d, x):
    k, kn, pg = _cote(g, x)
    m, mn, pd = _cote(d, x)
    base_g, va, f_tree = _exponentielle(pg, x)
    base_d, vb, h_tree = _exponentielle(pd, x)
    if k * m < 0:                                          # un membre > 0 et l'autre < 0 : aucune solution
        positif, negatif = (g, d) if k > 0 else (d, g)
        return {"genre": "bases_differentes", "inconnue": x, "enonce": Eq(g, d), "base": None, "remarque": None, "solutions": [],
                "etapes": [_carte("Aucune solution", [Chaine([Rel(positif, ">", Nb(0))], note=PROP_EXPO_POSITIVE),
                                                      Chaine([Rel(negatif, "<", Nb(0))], note=PROP_AUCUNE_SOLUTION)])]}
    if k < 0:
        raise _Hors                                        # deux membres négatifs : pas encore traité
    ln = va is None or vb is None
    if va is None and vb is None:
        raise _Hors                                        # e^f = e^h : même base
    f, h = _poly(f_tree, x), _poly(h_tree, x)
    if len(f) != 2 or len(h) != 2 or (not ln and _racine_primitive(va) == _racine_primitive(vb)):
        raise _Hors                                        # exposants du 1er degré ; une même base est possible : méthode « même base »
    (q, p), (s, r) = f, h
    X, bl = Var(x), (E() if ln else None)
    ecrit = {v: n for v, n in ((va, base_g), (vb, base_d), (k, kn), (m, mn)) if v is not None and n is not None}
    ligne = Chaine([Eq(g, d)])
    ligne.ajouter(Eq(Log(g, bl), Log(d, bl)), "⇔", PROP_LN_DEUX_MEMBRES if ln else PROP_LOG_DEUX_MEMBRES)
    if kn is not None or mn is not None:                   # log(k · a^f) = log(k) + log(a^f)
        separe = lambda c, puissance: Op("+", Log(c, bl), Log(puissance, bl)) if c is not None else Log(puissance, bl)
        ligne.ajouter(Eq(separe(kn, pg), separe(mn, pd)), "⇔", PROP_LOG_SOMME)

    def avec_puissance(c, base, exposant):                   # [log k +] f · log(a) ; ln(e^f) = f (base None)
        t = exposant if base is None else Op("*", exposant, Log(base, bl))
        return t if c is None else Op("+", Log(c, bl), t)
    ligne.ajouter(Eq(avec_puissance(kn, None if va is None else base_g, f_tree),
                     avec_puissance(mn, None if vb is None else base_d, h_tree)), "⇔", PROP_LN_E if ln else PROP_LOG_PUISSANCE)
    gauche = [_terme(p, True, va, ln), _terme(q, False, va, ln)] + ([_terme(F(1), False, k, ln)] if kn is not None else [])
    droite = [_terme(r, True, vb, ln), _terme(s, False, vb, ln)] + ([_terme(F(1), False, m, ln)] if mn is not None else [])
    developpe = Eq(_somme(gauche, x, ecrit, ln, False), _somme(droite, x, ecrit, ln, False))
    if tex_element(developpe) != tex_element(ligne.elements[-1]):       # (x − 1) log 2 devient x log 2 − log 2 ; log(10) devient 1
        valeurs = [va, vb] + ([k] if kn is not None else []) + ([m] if mn is not None else [])
        convertit = not ln and any(_exposant_entier(v, F(10)) is not None for v in valeurs)
        ligne.ajouter(developpe, "⇔", PROP_LOG_10K if convertit else None)
    # les termes en x du côté qui laisse la constante positive (2.24 a : à gauche ; b et c : à droite)
    valeur_terme = lambda t: t[0] if t[2] is None else float(t[0]) * math.log(t[2])
    c_gauche, c_droite = [t for t in gauche if not t[1]], [t for t in droite if not t[1]]
    a_gauche = sum(valeur_terme(t) for t in c_droite) - sum(valeur_terme(t) for t in c_gauche) > -1e-12
    if a_gauche:
        coeff, cte = [gauche[0], _oppose(droite[0])], [_oppose(t) for t in c_gauche] + c_droite
    else:
        coeff, cte = [droite[0], _oppose(gauche[0])], [_oppose(t) for t in c_droite] + c_gauche
    D, C = _somme([(c, False, a) for c, _, a in coeff], x, ecrit, ln), _somme(cte, x, ecrit, ln)
    if abs(valeur(D)) < 1e-12:
        raise _Hors                                        # p·log a = r·log b : une même base
    if ln:                                                 # x − x ln 2 = 0 : les termes en x réunis, comme dans l'équation du premier degré
        reunis = _somme(coeff, x, ecrit, ln)
        ligne.ajouter(Eq(reunis, C) if a_gauche else Eq(C, reunis), "⇔")
    facteur = Op("*", X, D)
    ligne.ajouter(Eq(facteur, C) if a_gauche else Eq(C, facteur), "⇔")
    lignes = [ligne]
    if not _fusionner(cte):                                # x(log 3 − log 2) = 0
        ligne.ajouter(Eq(X, Nb(0)), "⇔", Car(D))
        solution = Nb(0)
    else:
        ligne.ajouter(Eq(X, Op("/", C, D)), "⇔", Car(D))
        solution = Op("/", C, D)
        haut, bas = (None, None) if ln else (_regrouper(cte, ecrit), _regrouper([(c, False, a) for c, _, a in coeff], ecrit))
        if haut is not None and bas is not None:
            genres = {haut[1], bas[1]} - {"seul"}
            prop = {"quotient": PROP_LOG_QUOTIENT, "produit": PROP_LOG_PRODUIT}.get(next(iter(genres)) if len(genres) == 1 else None,
                                                                                    PROP_LOG_REGROUPER)
            solution = Op("/", haut[0], bas[0])
            ligne.ajouter(solution, "=", prop)
            if prop == PROP_LOG_REGROUPER:
                lignes += [p[2] for p in (haut, bas) if p[2] is not None]
    return {"genre": "bases_differentes", "inconnue": x, "enonce": Eq(g, d), "base": None,
            "etapes": [_carte("Bases différentes", lignes)], "solutions": [solution], "remarque": None}


# =====================================================================
# 10 ter. MÉTHODE « DÉFINITION DU LOGARITHME » : log_a(u) = c ⇔ u = a^c (équations logarithmiques en une étape)
# =====================================================================
def _racine_entiere(n, k):
    """Le rationnel r > 0 tel que r^k = n (n > 0 rationnel, k entier ≥ 1), ou None."""
    def racine(m):
        r = round(m ** (1 / k))
        return next((v for v in (r - 1, r, r + 1) if v >= 0 and v ** k == m), None)
    a, b = racine(n.numerator), racine(n.denominator)
    return None if a is None or b is None else F(a, b)


def _valeur_exacte(p):
    """Écriture exacte d'une puissance a^c quand le cours la donne : un nombre (10³ = 1000, 10⁻¹ = 1/10, 2⁴ = 16), sauf les très grands et très petits
    (10¹⁰, 10⁻⁴ : notation scientifique) ou a^(n+½) = aⁿ√a (10^1,5 = 10√10) ; None sinon."""
    if not isinstance(p, Pow):
        return None
    if _const(p.b) == 0:
        return Nb(1)                                   # a⁰ = 1, même pour e
    v = _const(p)
    if v is not None:
        return _nb_exact(v) if v == 0 or F(1, 1000) <= abs(v) < 10 ** 6 else None     # 10⁻⁴ et 10¹⁰ restent en notation scientifique
    c = _const(p.b)
    if isinstance(p.a, Nb) and p.a.val.denominator == 1 and c is not None and c.denominator == 2 and c >= F(1, 2):
        n = int(c - F(1, 2))
        racine = Fn("sqrt", p.a)
        return racine if n == 0 else Op("*", Nb(p.a.val ** n), racine)
    return None


def _base_du_logarithme(base):
    """(nœud, valeur ou None pour e) de la base d'un logarithme sans inconnue."""
    if base is None:
        return Nb(10), F(10)
    if isinstance(base, E):
        return base, None
    v = _const(base)
    if variables(base) or v is None or v <= 0 or v == 1:
        raise _Hors
    return base, v


@_avec_decimaux
def logarithmique(g, d, x):
    """Corrigé de log_a(u) = c par la définition du logarithme (u polynôme de degré ≤ 2 en x, ou logarithmes imbriqués, ou base inconnue
    log_x(n) = k), après avoir isolé le logarithme. None si la méthode ne s'applique pas."""
    try:
        return _logarithmique(g, d, x)
    except _Hors:
        return None


def _logarithmique(g, d, x):
    enonce = Eq(g, d)
    g, d, iso = _isoler(g, d, x, PROP_ISOLER_LOG)
    etapes = [_carte("Isoler le logarithme", [iso])] if iso is not None else []
    if variables(g) and not variables(d):
        s, o, inverse = g, d, False
    elif variables(d) and not variables(g):
        s, o, inverse = d, g, True
    else:
        raise _Hors
    c = _const(o)
    if not isinstance(s, Log) or c is None:
        raise _Hors
    chaine = Chaine([Eq(g, d)])
    if inverse:
        chaine.ajouter(Eq(s, o), "⇔")
    if isinstance(s.base, Var):
        return _base_inconnue(enonce, etapes, chaine, s, c, x)
    rhs, courant, profondeur = _nb_exact(c), s, 0
    while True:                                   # on épluche les logarithmes de l'extérieur vers l'intérieur
        base, _ = _base_du_logarithme(courant.base)
        puissance = base if isinstance(base, E) and rhs == Nb(1) else Pow(base, rhs)          # e^1 s'écrit e
        profondeur += 1
        if not isinstance(courant.a, Log):
            break
        exact = _valeur_exacte(puissance)
        chaine.ajouter(Eq(courant.a, exact or puissance, [puissance] if exact is not None else ()), "⇔", PROP_DEFINITION_LOG)
        rhs, courant = exact or puissance, courant.a
    u = courant.a
    if not variables(u) or not _est_polynome(u):
        raise _Hors
    lignes, remarque = [chaine], None
    if isinstance(u, Var):
        exact = _valeur_exacte(puissance)
        chaine.ajouter(Eq(u, exact or puissance, [puissance] if exact is not None else ()), "⇔", PROP_DEFINITION_LOG)
        solutions = [exact or puissance]
    else:
        f = _poly(u, x)
        if len(f) == 2:
            chaine.ajouter(Eq(u, puissance), "⇔", PROP_DEFINITION_LOG)
            if f[1] == -1 and f[0] != 0:                      # q − x = c donne x = q − c (corrigé 2.15 l : x = 5 − 10⁸)
                sol = Op("-", _nb_exact(f[0]), puissance)
                chaine.ajouter(Eq(Var(x), sol), "⇔")
            else:
                sol = _suite_lineaire(chaine, f[1], f[0], puissance, x, u)
            v = _const(sol)
            dernier = chaine.elements[-1]
            if v is not None and (v == 0 or F(1, 10 ** 8) <= abs(v) < 10 ** 15) and isinstance(dernier, Eq) and tex(dernier.d) == tex(sol):
                chaine.elements[-1] = Eq(dernier.g, _nb_exact(v), [sol])
                sol = _nb_exact(v)
            solutions = [sol]
        else:
            v = _const(puissance)
            if v is None:
                raise _Hors
            chaine.ajouter(Eq(u, _nb_exact(v), [puissance]), "⇔", PROP_DEFINITION_LOG)
            l_poly, solutions, remarque = _resoudre_polynome(f, [v], u, _nb_exact(v), x)
            if solutions is None:
                raise _Hors
            premiere = l_poly[0]
            for e, lien, prop in zip(premiere.elements[1:], premiere.liens, premiere.props):
                chaine.ajouter(e, lien, prop)
            lignes += l_poly[1:]
    etapes.append(_carte("Définition du logarithme", lignes))
    if profondeur == 1 and not isinstance(u, Var) and solutions:
        etapes.append(_carte("Vérification", [Chaine([Positif(u, puissance)], note=PROP_BIEN_DEFINI)]))
    return {"genre": "logarithmique", "inconnue": x, "enonce": enonce, "base": None, "etapes": etapes, "solutions": solutions,
            "remarque": remarque}


def _base_inconnue(enonce, etapes, chaine, s, c, x):
    """log_x(n) = k avec k entier ≥ 1 : x > 0 et x ≠ 1, xᵏ = n, puis la solution positive : r si n = rᵏ (256 = 4⁴), sinon la racine k-ième
    de n écrite comme telle (√255, 255^(1/3))."""
    n = _const(s.a)
    if variables(s.a) or n is None or n <= 0 or n == 1 or c.denominator != 1 or c < 1 or c > 12:
        raise _Hors
    k = int(c)
    r = _racine_entiere(n, k)
    if r is not None:
        racine = _nb_exact(r)
    else:
        racine = Fn("sqrt", _nb_exact(n)) if k == 2 else Pow(_nb_exact(n), Nb(F(1, k)))
    X = Var(s.base.nom)
    condition = Chaine([Texte(f"{X.nom} > 0 \\text{{ et }} {X.nom} \\neq 1")], note=PROP_BASE_LOG)
    equation = Eq(Pow(X, Nb(k)) if k > 1 else X, _nb_exact(n))
    chaine.ajouter(equation, "⇔", PROP_DEFINITION_LOG)
    lignes = [chaine]
    if k % 2 == 0:
        chaine.ajouter(Ou([Eq(X, racine), Eq(X, Neg(racine) if r is None else _nb_exact(-r))]), "⇔")
        lignes.append(Chaine([Eq(X, racine)], note=PROP_SEULE_POSITIVE))
    elif k > 1:
        chaine.ajouter(Eq(X, racine), "⇔")
    etapes += [_carte("Condition", [condition]), _carte("Définition du logarithme", lignes)]
    return {"genre": "logarithmique", "inconnue": x, "enonce": enonce, "base": None, "etapes": etapes, "solutions": [racine],
            "remarque": None}


# =====================================================================
# 10 quater. CALCUL DE log_a(y) (saisie sans « = »)
# =====================================================================
def _vecteur(n):
    """Exposants des facteurs premiers de n : un rationnel > 0, la racine carrée d'un tel nombre, une puissance a^c (c rationnel) ;
    {premier: exposant rationnel}, ou None si n n'est pas de cette forme."""
    if isinstance(n, Fn):
        v = _vecteur(n.a)
        return None if v is None else {p: e / 2 for p, e in v.items()}
    if isinstance(n, Pow) and not variables(n):
        c, v = _const(n.b), _vecteur(n.a)
        return None if c is None or v is None else {p: e * c for p, e in v.items()}
    q = _const(n)
    if q is None or q <= 0:
        return None
    haut, bas = _premiers(q.numerator), _premiers(q.denominator)
    return {p: F(haut.get(p, 0) - bas.get(p, 0)) for p in set(haut) | set(bas)}


def _exposant_de_la_base(arg, base):
    """Le rationnel k tel que arg = base^k, ou None."""
    va, vb = _vecteur(arg), _vecteur(base)
    if va is None or vb is None:
        return None
    p0 = next((p for p, e in vb.items() if e != 0), None)
    if p0 is None:
        return None
    k = va.get(p0, F(0)) / vb[p0]
    return k if all(va.get(p, F(0)) == k * vb.get(p, F(0)) for p in set(va) | set(vb)) else None


def _encadrement(y, a):
    """(j, a^j, a^(j+1)) tels que a^j < y < a^(j+1), pour a > 1 et y > 0 rationnels qui ne sont pas des puissances entières de a."""
    j = 0
    while a ** (j + 1) <= y:
        j += 1
    while a ** j > y:
        j -= 1
    return j, a ** j, a ** (j + 1)


@_avec_decimaux
def calculer_logarithme(g):
    """Corrigé du calcul de log_a(y) (a et y sans inconnue) : y = aᵏ donne k (64 = 8², log₈(64) = 2 ; √2 = 4^(1/4), log₄(√2) = 1/4),
    sinon changement de base et valeur approchée (log₂(50) = log(50)/log(2) ≈ 5,644). None si le calcul sort de ces formes."""
    try:
        return _calculer_logarithme(g)
    except _Hors:
        return None


def _calculer_logarithme(g):
    if not isinstance(g, Log) or variables(g):
        raise _Hors
    arg, base = g.a, g.base
    resultat = lambda etapes, valeur: {"genre": "calcul", "inconnue": None, "enonce": g, "etapes": etapes, "valeur": valeur, "solutions": None,
                                       "remarque": None}
    if isinstance(base, E):                                     # ln : ln(1) = 0, ln(e) = 1, ln(e^k) = k, sinon la valeur de la calculatrice
        q = _const(arg)
        if q == 1:
            return resultat([_carte("Calcul", [Chaine([g, Nb(0)], ["="], [PROP_LN_UN])])], Nb(0))
        if isinstance(arg, E) or (isinstance(arg, Pow) and isinstance(arg.a, E) and _const(arg.b) is not None):
            k = F(1) if isinstance(arg, E) else _const(arg.b)
            return resultat([_carte("Calcul", [Chaine([g, _nb_exact(k)], ["="], [PROP_LN_E_PUISSANCE])])], _nb_exact(k))
        if contient_e(arg) or _vecteur(arg) is None:
            raise _Hors
        return resultat([], g)
    if contient_e(arg):
        raise _Hors
    base_noeud, b = (Nb(10), F(10)) if base is None else (base, _const(base))
    if b is None or b <= 0 or b == 1:
        raise _Hors
    k = _exposant_de_la_base(arg, base_noeud)
    prop = PROP_LOG_10K if b == 10 else PROP_LOG_BASE_PUISSANCE
    if k is not None:
        lignes = []
        if k.denominator == 1:
            lignes.append(Chaine([arg, Pow(base_noeud, Nb(k))], ["="], [None]))            # 64 = 8²
        else:                                                   # √2 = 2^(1/2) = (4^(1/2))^(1/2) = 4^(1/4)
            rho = _racine_primitive(b)
            m = _exposant_entier(b, rho)
            rho_noeud = _nb_exact(rho)
            s = _exposant_de_la_base(arg, rho_noeud)
            chaine = Chaine([arg])
            if s != 1 or m == 1:
                chaine.ajouter(Pow(rho_noeud, _nb_exact(s)), "=")
            if m != 1 and s != 1:
                chaine.ajouter(Pow(Pow(base_noeud, _nb_exact(F(1, m))), _nb_exact(s)), "=")
            if tex(chaine.elements[-1]) != tex(Pow(base_noeud, _nb_exact(k))):
                chaine.ajouter(Pow(base_noeud, _nb_exact(k)), "=")
            lignes.append(chaine)
        lignes.append(Chaine([g, Log(Pow(base_noeud, _nb_exact(k)), base), _nb_exact(k)], ["=", "="], [None, prop]))   # log₈(64) = log₈(8²) = 2
        return resultat([_carte("Calcul", lignes)], _nb_exact(k))
    if _vecteur(arg) is None:
        raise _Hors                                             # argument négatif, nul ou hors de ces formes
    lignes, valeur = [], (g if base is None else Op("/", Log(arg), Log(base_noeud)))
    q = _const(arg)
    texte_base = tex(base_noeud)
    if q is not None and b > 1:
        j, bas, haut = _encadrement(q, b)
        lignes.append(Chaine([Texte(tex(arg) + r" \text{ n'est pas une puissance de } " + texte_base,
                                    detail=tex(Pow(base_noeud, Nb(j))) + " = " + tex(_nb_exact(bas)) + " < " + tex(arg) + " < "
                                    + tex(_nb_exact(haut)) + " = " + tex(Pow(base_noeud, Nb(j + 1))))]))
    else:
        lignes.append(Chaine([Texte(tex(arg) + r" \text{ n'est pas une puissance de } " + texte_base)]))
    if base is not None:
        lignes.append(Chaine([g, valeur], ["="], [PROP_CHANGEMENT_DE_BASE]))
    return resultat([_carte("Calcul", lignes)], valeur)


def tex_resultat(r):
    """Ligne finale du calcul : `log_8(64) = 2` ; `log_2(50) = log(50)/log(2) ≈ 5,644` ; `log(50) ≈ 1,699`."""
    v = r["valeur"]
    if _const(v) is not None:
        return tex(r["enonce"]) + " = " + tex(v)
    return (tex(v) if v == r["enonce"] else tex(r["enonce"]) + " = " + tex(v)) + r" \approx " + tex_approx(valeur(v))


# =====================================================================
# 11. PRODUIT NUL ET PREMIER DEGRÉ À CONSTANTES LOGARITHMIQUES
# =====================================================================
@_avec_decimaux
def produit_nul(g, d, x):
    """Corrigé de P1 · P2 · … = 0 quand chaque facteur = 0 se résout par « même base » ou « logarithme » (10^x(10^x − 4) = 0)."""
    try:
        return _produit_nul(g, d, x)
    except _Hors:
        return None


NOMS_FACTEURS = ("Facteur 1", "Facteur 2", "Facteur 3", "Facteur 4")


def _produit_nul(g, d, x):
    if isinstance(d, Nb) and d.val == 0 and isinstance(g, Op) and g.op == "*":
        produit = g
    elif isinstance(g, Nb) and g.val == 0 and isinstance(d, Op) and d.op == "*":
        produit = d
    else:
        raise _Hors
    facteurs = _aplatir(produit)
    if len(facteurs) > len(NOMS_FACTEURS) or any(not variables(f) for f in facteurs):
        raise _Hors
    etapes = [_carte("Produit nul", [Chaine([Eq(g, d), Ou(Eq(f, Nb(0)) for f in facteurs)], ["⇔"], [PROP_PRODUIT_NUL])])]
    solutions = []
    for nom, f in zip(NOMS_FACTEURS, facteurs):
        r = meme_base(f, Nb(0), x) or logarithme(f, Nb(0), x)
        if r is None:
            raise _Hors
        etapes.append(_carte(nom, [l for c in r["etapes"] for l in c["lignes"]]))
        if r["solutions"] is None:
            raise _Hors
        for n in r["solutions"]:
            if all(abs(valeur(n) - valeur(m)) > 1e-12 for m in solutions):
                solutions.append(n)
    solutions.sort(key=valeur)
    return {"genre": "produit_nul", "inconnue": x, "enonce": Eq(g, d), "base": None, "etapes": etapes, "solutions": solutions,
            "remarque": None}


def _contient_log(n):
    if isinstance(n, Log):
        return True
    if isinstance(n, (Neg, Fn)):
        return _contient_log(n.a)
    if isinstance(n, (Op, Pow)):
        return _contient_log(n.a) or _contient_log(n.b)
    return False


@_avec_decimaux
def lineaire_logarithmes(g, d, x):
    """Corrigé de p·x + q = c où c est une constante qui contient un logarithme (x = ln(3) ; 2x = ln(0,1))."""
    try:
        return _lineaire_logarithmes(g, d, x)
    except _Hors:
        return None


def _lineaire_logarithmes(g, d, x):
    if variables(g) and not variables(d):
        s, c, inverse = g, d, False
    elif variables(d) and not variables(g):
        s, c, inverse = d, g, True
    else:
        raise _Hors
    f = _poly(s, x)
    if len(f) != 2 or not _contient_log(c):
        raise _Hors
    chaine = Chaine([Eq(g, d)])
    if inverse:
        chaine.ajouter(Eq(s, c), "⇔")
    solution = _suite_lineaire(chaine, f[1], f[0], c, x, s)
    etapes = [_carte("Équation du premier degré", [chaine])] if chaine.liens else []
    return {"genre": "lineaire", "inconnue": x, "enonce": Eq(g, d), "base": None, "etapes": etapes, "solutions": [solution],
            "remarque": None}


def tex_approx(v):
    """Valeur approchée à 3 décimales, virgule décimale ; en notation scientifique (3,162 × 10⁻⁵, 1 × 10¹⁰) sous 10⁻³ et dès 10⁶."""
    a = abs(v)
    if a == 0 or 1e-3 <= a < 1e6:
        return formater_decimal(f"{v:.3f}", tex=True)
    e = math.floor(math.log10(a))
    if abs(float(f"{v / 10 ** e:.3f}")) >= 10:
        e += 1
    m = f"{v / 10 ** e:.3f}"
    m = m[:-4] if m.endswith(".000") else m
    return formater_decimal(m, tex=True) + r" \times 10^{" + str(e) + "}"


def tex_solution(r):
    """Ligne finale du corrigé : l'ensemble solution (valeur exacte), puis « soit x ≈ … » (3 décimales) quand une solution n'est pas un
    rationnel. Elle existe même quand aucune carte de méthode ne précède (x = ln 3 : S = {ln(3)}, soit x ≈ 1,099)."""
    sols = r["solutions"]
    if sols is None:
        return r"S = \mathbb{R}"
    if not sols:
        return r"S = \varnothing"
    s = r"S = \left\{" + r" \,;\, ".join(tex(n) for n in sols) + r"\right\}"
    rationnel = lambda n: _const(n) is not None
    if all(rationnel(n) for n in sols):
        return s
    x = r["inconnue"]
    parts = [x + (" = " + tex(n) if rationnel(n) else r" \approx " + tex_approx(valeur(n))) for n in sols]
    return s + r" \text{, soit } " + r" \text{ ou } ".join(parts)


def corriger_equation(g, d, x):
    """Corrigé de g = d par la première méthode du cours qui s'applique (même base, logarithme, produit nul, bases différentes, premier degré),
    ou None si l'équation ne se résout pas avec ces méthodes."""
    for methode in (meme_base, logarithme, produit_nul, bases_differentes, logarithmique, lineaire_logarithmes):
        r = methode(g, d, x)
        if r is not None:
            return r
    return None


# =====================================================================
# 12. QUAND AUCUNE MÉTHODE NE S'APPLIQUE : HORS PROGRAMME OU PAS ENCORE TRAITÉ
# =====================================================================
def _termes_additifs(n):
    if isinstance(n, Op) and n.op in "+-":
        return _termes_additifs(n.a) + _termes_additifs(n.b)
    return _termes_additifs(n.a) if isinstance(n, Neg) else [n]


def _puissances_en_x(n):
    """Les puissances de l'arbre dont l'exposant contient l'inconnue."""
    if isinstance(n, Pow):
        return ([n] if variables(n.b) else []) + _puissances_en_x(n.a) + _puissances_en_x(n.b)
    if isinstance(n, (Neg, Fn)):
        return _puissances_en_x(n.a)
    if isinstance(n, Op):
        return _puissances_en_x(n.a) + _puissances_en_x(n.b)
    if isinstance(n, Log):
        return _puissances_en_x(n.a)
    return []


def _classe(n):
    """« cte », « exp » (une puissance dont l'exposant contient l'inconnue), « log » ou « poly » (l'inconnue hors d'un exposant et d'un logarithme)."""
    if not variables(n):
        return "cte"
    if _puissances_en_x(n):
        return "exp"
    return "log" if _contient_log(n) else "poly"


def _est_polynome(n):
    """Vrai si n est un polynôme en l'inconnue, de degré quelconque : x³ + 1, 2x − 5."""
    if isinstance(n, (Nb, Var)):
        return True
    if isinstance(n, Neg):
        return _est_polynome(n.a)
    if isinstance(n, Op):
        if n.op == "/":
            return _est_polynome(n.a) and not variables(n.b)
        return _est_polynome(n.a) and _est_polynome(n.b)
    if isinstance(n, Pow):
        k = _const(n.b)
        return _est_polynome(n.a) and k is not None and k.denominator == 1 and 0 <= k <= 64
    return False


def _hors_arbre(n, nul=False):
    """Vrai si l'arbre contient une forme sans méthode dans le cours : l'inconnue dans une base et dans un exposant (x^x), un exposant qui n'est
    pas un polynôme (2^√x), une exponentielle multipliée ou divisée par un facteur en x (x · 2^x, sauf produit égal à 0), une somme de deux
    exponentielles de bases différentes (2^x + 3^x). Un exposant polynomial de degré 3 (2^(x³) = 8) n'est pas hors programme : le logarithme
    donne une équation du 3ᵉ degré, que l'outil ne traite pas encore."""
    if isinstance(n, Pow) and variables(n.b):
        if variables(n.a) or not _est_polynome(n.b):
            return True
    if isinstance(n, Op) and n.op in "*/":
        facteurs = _aplatir(n) if n.op == "*" else [n.a, n.b]
        classes = {_classe(f) for f in facteurs}
        if "exp" in classes and "poly" in classes and not nul:
            return True
    if isinstance(n, Op) and n.op in "+-":
        avec_exp = [t for t in _termes_additifs(n) if _classe(t) == "exp"]
        bases = {"e" if isinstance(p.a, E) else _const(p.a) for t in avec_exp for p in _puissances_en_x(t)}
        if len(bases) > 1:
            return True
    enfants = {Neg: lambda n: [n.a], Fn: lambda n: [n.a], Op: lambda n: [n.a, n.b], Pow: lambda n: [n.a, n.b],
               Log: lambda n: [n.a] + ([n.base] if n.base is not None else [])}
    return any(_hors_arbre(e) for e in enfants.get(type(n), lambda n: [])(n))


def hors_programme(g, d, x):
    """Vrai pour une équation dont le type n'est pas dans le cours : x · 2^x = 8, 2^x + 3^x = 5, x^x = 4, 2^(x³) = 8, 2^x = x + 1."""
    egal_zero = lambda a, b: isinstance(b, Nb) and b.val == 0 and isinstance(a, Op) and a.op == "*"
    if _hors_arbre(g, egal_zero(g, d)) or _hors_arbre(d, egal_zero(d, g)):
        return True
    classes = {_classe(t) for t in _termes_additifs(g) + _termes_additifs(d)}
    return "exp" in classes and "poly" in classes


def message_non_resolu(g, d, x):
    """Le message à afficher quand `corriger_equation` ne trouve aucune méthode : « ne se résout pas avec les méthodes du cours » pour un
    vrai hors-programme, « ne traite pas encore » pour une forme du programme que l'outil ne gère pas encore."""
    return MESSAGE_HORS_PROGRAMME if hors_programme(g, d, x) else MESSAGE_PAS_ENCORE


def message_calcul_non_resolu(g):
    """Le message à afficher quand `calculer_logarithme` renvoie None : pas un logarithme, argument négatif ou nul (une base invalide est
    refusée à la lecture), ou calcul pas encore traité (2 log 5, log 2 + log 3, argument avec e)."""
    if not _contient_log(g):
        return MESSAGE_PAS_UN_LOGARITHME
    if isinstance(g, Log):
        a = _const(g.a)
        if a is not None and a <= 0:
            return MESSAGE_ARGUMENT_NON_POSITIF
    return MESSAGE_CALCUL_PAS_ENCORE


# =====================================================================
# 13. EXERCICES AU HASARD (pool C)
# =====================================================================
NIVEAUX = ("facile", "moyen", "logarithme", "difficile")


def _lineaire_texte(p, q, x="x"):
    """px + q écrit comme un élève : x, 2x, x+1, 3x-2."""
    t = x if p == 1 else f"{p}{x}"
    return t if q == 0 else f"{t}+{q}" if q > 0 else f"{t}{q}"


def _expo_texte(base, p, q):
    """base^(px+q), sans parenthèses quand l'exposant est x seul."""
    return f"{base}^x" if (p, q) == (1, 0) else f"{base}^({_lineaire_texte(p, q)})"


def _puissance_de_la_racine(b, a):
    """Vrai si b est une puissance entière de la racine de a (a = 4 : 2, 4, 8, 16… ; a = 7 : 7, 49…) : l'équation relèverait de la même base."""
    r = next(r for r in range(2, a + 1) if _exposant_entier(F(a), F(r)) is not None)
    while b % r == 0:
        b //= r
    return b == 1


def _gabarit_facile(rng):
    if rng.random() < 0.6:                                       # a^(px+q) = a^k, solution entière
        a = rng.choice([2, 3, 5, 10])
        kmax = {2: 6, 3: 4, 5: 3, 10: 3}[a]
        while True:
            p, x0, q = rng.randint(1, 3), rng.randint(-3, 4), rng.randint(-3, 3)
            if 1 <= p * x0 + q <= kmax:
                return f"{_expo_texte(a, p, q)}={a ** (p * x0 + q)}"
    forme = rng.choice(["log", "ln", "log_a"])                    # définition du logarithme
    if forme == "log":
        return f"log(x)={rng.choice([-2, -1, 1, 2, 3, 4])}"
    if forme == "ln":
        return f"ln(x)={rng.choice([-1, 1, 2, 3])}"
    a = rng.choice([2, 3, 5])
    return f"log_{a}(x)={rng.choice([-2, -1, 1, 2, 3] + ([4, 5] if a == 2 else [4] if a == 3 else []))}"


def _gabarit_moyen(rng):
    famille = rng.choice(["facteur", "meme_racine", "argument"])
    if famille == "facteur":                                      # k * a^(px+q) = k * a^m
        a, k = rng.choice([2, 3, 5]), rng.choice([2, 3, 4, 5])
        while True:
            p, x0, q = rng.randint(1, 2), rng.randint(-2, 4), rng.randint(-3, 3)
            m = p * x0 + q
            if 1 <= m <= (4 if a == 2 else 3):
                return f"{k}*{_expo_texte(a, p, q)}={k * a ** m}"
    if famille == "meme_racine":                                  # 4^(3x+1) = 8 : bases puissances d'une même base
        r = rng.choice([2, 3, 5])
        s, t = rng.choice([(2, 3), (2, 1), (3, 2), (3, 1), (1, 2), (1, 3)]) if r != 5 else rng.choice([(2, 1), (1, 2)])
        while True:
            p, q = rng.randint(1, 3), rng.randint(-2, 2)
            x0 = (F(t, s) - q) / p
            if x0.denominator <= 6:
                return f"{_expo_texte(r ** s, p, q)}={r ** t}"
    c = rng.randint(1, 3)                                         # log(q - x) = c, log(px + q) = c
    if rng.random() < 0.5:
        return f"log({rng.randint(1, 9)}-x)={c}"
    return f"log({rng.randint(2, 4)}x+{rng.randint(1, 5)})={c}"


def _gabarit_logarithme(rng):
    tirage = rng.random()
    if tirage < 0.10:                                             # second membre négatif : S = ∅
        return f"{rng.choice([2, 3, 5, 7])}^({_lineaire_texte(rng.randint(1, 8), 0)})=-{rng.randint(3, 60)}"
    if tirage < 0.40:                                             # k * e^(cx) = b
        k = rng.choice([2, 3, 5, 10, 20, 37, 50])
        c = rng.choice(["0,02", "0,05", "0,1", "0,5", "-0,02", "-0,05", "-0,1", "-0,5"])
        b = rng.choice([v for v in range(3, 100) if v != k])
        return f"{k}*e^({c}x)={b}"
    a = rng.choice([2, 3, 4, 5, 6, 7])
    b = rng.choice([v for v in range(5, 100) if not _puissance_de_la_racine(v, a)])
    p, q = rng.randint(1, 3), rng.randint(-3, 3)
    if tirage < 0.70:                                             # a^(px+q) = b
        return f"{_expo_texte(a, p, q)}={b}"
    if tirage < 0.90:                                             # k * a^(px+q) = b, avec b/k qui n'est pas une puissance de a
        k = rng.choice([2, 3, 4, 5])
        b = rng.choice([v for v in range(5, 100) if v % k or not _puissance_de_la_racine(v // k, a)])
        return f"{k}*{_expo_texte(a, p, q)}={b}"
    return f"e^({_lineaire_texte(p, q)})={b}"


def _gabarit_difficile(rng):
    tirage = rng.random()
    if tirage < 0.40:                                             # bases différentes : a^(x+p) = b^(qx)
        a, b = rng.sample([2, 3, 5, 6, 7, 10], 2)
        p, q = rng.choice([-3, -2, -1, 1, 2, 3]), rng.randint(1, 3)
        return f"{a}^({_lineaire_texte(1, p)})={b}^({_lineaire_texte(q, 0)})" if q > 1 else f"{a}^({_lineaire_texte(1, p)})={b}^x"
    if tirage < 0.65:                                             # a^(x²) · b^x = c, b et c puissances de a : racines entières
        a = rng.choice([2, 3, 5])
        s, t = rng.choice([(2, 3), (3, 4)])
        return f"{a}^(x^2)*{a ** s}^x={a ** t}"
    if tirage < 0.85:                                             # base inconnue : log_x(m^k) = k
        k = rng.choice([2, 3, 4])
        m = rng.choice([2, 3, 4, 5] if k < 4 else [2, 3, 4])
        return f"log_x({m ** k})={k}"
    return f"log(log(x))={rng.choice([0, 1])}"                     # log(log(x)) = c


_GABARITS = {"facile": _gabarit_facile, "moyen": _gabarit_moyen, "logarithme": _gabarit_logarithme, "difficile": _gabarit_difficile}


def exercice(niveau, graine):
    """Exercice du niveau (facile, moyen, logarithme, difficile), déterministe : la même graine donne le même énoncé. Aucun exposant de
    degré 3 ou plus ; quand x² est en exposant, les racines sont entières. Renvoie {ok, expr, niveau}."""
    if niveau not in _GABARITS:
        return {"ok": False, "erreur": "Niveau d'exercice inconnu."}
    return {"ok": True, "expr": _GABARITS[niveau](random.Random(f"{niveau}:{graine}")), "niveau": niveau}


def exercice_json(niveau):
    """Appelé par la page : un exercice du niveau demandé, graine tirée au hasard."""
    return json_strict(exercice(niveau, random.randrange(2 ** 31)))
