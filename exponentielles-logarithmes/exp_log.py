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
import re
from collections import namedtuple

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
        if deux_groupes or (isinstance(n.a, Nb) and n.a.val >= 0 and _DEBUT_COLLABLE.match(d)):
            return g + d
        return g + r" \cdot " + d
    if isinstance(n, Pow):
        base = tex(n.a)
        if isinstance(n.a, (Op, Neg, Log)) or (isinstance(n.a, Nb) and (n.a.val < 0 or (n.a.val.denominator != 1 and n.a.dec is None))):
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
