"""
exp_log.py — Outil « Exponentielles et logarithmes » (3C) : lecture de la saisie, arbre syntaxique, TeX.

Lecture propre à l'outil, parce que le tokeniseur de l'Ensemble de définition lit `log` comme `ln` et ne connaît ni log_a ni aˣ :
    log(x)  logarithme en base 10        ln(x)  logarithme en base e        log2(x), log_2(x), log_x(x)  base 2, base 2, base x
    exp(x), e^x, sqrt(x), + - * / ^ ( ), multiplication implicite (2x, 3ln(x), (x+1)(x-2)), virgule ou point décimal, un seul « = » ;
    les exposants ² et ³ se lisent ^2 et ^3 (x² = x^2).

Le tokeniseur reconnaît les noms de fonction (sqrt, exp, log…, ln) AVANT les lettres isolées : « exp » n'est jamais e·x·p.
La lettre e est toujours le nombre e ; elle ne peut pas être l'inconnue. Les noms de fonction sont insensibles à la casse, les lettres non
(Q n'est pas q) ; C0, V0, C_0 sont un seul nom (écrit C_{0}) ; « 3,75 % » vaut 3,75/100. Dans un problème d'application (3Q = Q(1+3,75/100)^x),
l'inconnue est la lettre de l'exposant et toute autre lettre, facteur de chaque membre, est un paramètre qui se simplifie.

Tout le TeX est écrit par notre arbre (`tex`) : ln → \\ln, log → \\log, log_a → \\log_{a}. Aucune conversion depuis SymPy,
qui écrirait « log » pour ln. Ce fichier n'importe pas SymPy.

Interface : `lire_membres(texte)` (syntaxe seule, sert à l'aperçu), `analyser_saisie(texte)` (équation ou calcul, une seule inconnue),
`apercu_json(texte)`. Les erreurs sont des `ErreurSaisie` au message français.
"""
from fractions import Fraction as F
import decimal
import math
import random
import re
from collections import namedtuple
from functools import reduce
from html import escape as _echapper
from math import gcd, isqrt

from noyau import ErreurSaisie, json_strict
from nombres import (MOTIF_ESPACE_DANS_UN_NOMBRE, MOTIF_SAISIE, formater_decimal, formater_entier, nettoyer_saisie)

__all__ = ["Nb", "Var", "E", "Neg", "Op", "Pow", "Fn", "Log", "tex", "variables", "lire_membres", "analyser_saisie", "tex_saisie",
           "apercu", "apercu_json", "Saisie", "sans_facteur"]

MESSAGE_E = "La lettre e désigne le nombre e ≈ 2,718 : choisissez une autre lettre pour l'inconnue."
MESSAGE_EXPOSANT = "Mettez l'exposant entre parenthèses : e^(-0,02t)."
MESSAGE_HORS_PROGRAMME = "Cette équation ne se résout pas avec les méthodes du cours."
MESSAGE_PAS_ENCORE = "Cet outil ne traite pas encore ce type d'équation."
MESSAGE_SANS_EXP_LOG = "Cet outil traite les équations exponentielles et logarithmiques."
MESSAGE_PAS_UN_LOGARITHME = "Écrivez une équation (avec =) ou un logarithme à calculer, par exemple log_2(50)."
MESSAGE_CALCUL_PAS_ENCORE = "Cet outil ne traite pas encore ce type de calcul."
MESSAGE_ARGUMENT_NON_POSITIF = "Le logarithme d'un nombre négatif ou nul n'est pas défini."
MESSAGE_POURCENT = "Le signe % se place juste après un nombre : 3,75 %."
MESSAGE_TROP_GRAND = "Une solution de cette équation est trop grande pour être écrite par cet outil."
MESSAGE_FILIERE = "La filière doit être C (3C) ou M (2M)."
FILIERES = ("C", "M")          # C : 3C (sans ensemble de définition) ; M : 2Ms et 2Mr (exp_log_m.py)


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
    """Nombre rationnel exact. `dec` : écriture décimale de la saisie (« 0,02 »), gardée pour l'affichage ; hors égalité.
    `pct` : le nombre écrit avec le signe % dans la saisie (« 3,75 » pour 3,75 % ; `val` vaut alors 3,75/100), affichage seulement."""
    __slots__ = ("val", "dec", "pct")

    def __init__(self, val, dec=None, pct=None):
        self.val, self.dec, self.pct = F(val), dec, pct

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


class Defini(Noeud):
    """Un nombre qui porte un nom dans le corrigé (Δ, x₁ = (−b − √Δ)/(2a)) : écrit par son nom, évalué par sa définition. Il raccourcit les
    lignes d'un trinôme à coefficients logarithmiques, qui ne tiendraient pas à 360 px."""
    __slots__ = ("nom", "arbre")

    def __init__(self, nom, arbre):
        self.nom, self.arbre = nom, arbre


def variables(n):
    """Ensemble des lettres inconnues (jamais e) qui apparaissent dans l'arbre, base des logarithmes comprise."""
    if isinstance(n, Defini):
        return variables(n.arbre)
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
    if isinstance(n, Defini):
        return contient_e(n.arbre)
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
    if n.pct is not None:
        return formater_decimal(n.pct, tex=True) + r"\,\%"
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


def _nom_tex(nom):
    """C0 s'écrit C_{0} (nom indexé : une lettre suivie de chiffres), une lettre seule telle quelle."""
    return nom[0] + "_{" + nom[1:] + "}" if len(nom) > 1 else nom


def tex(n):
    if isinstance(n, Defini):
        return n.nom
    if isinstance(n, Nb):
        return _nb_tex(n)
    if isinstance(n, Var):
        return _nom_tex(n.nom)
    if isinstance(n, E):
        return "e"
    if isinstance(n, Neg):
        s = tex(n.a)
        return "-" + (_entre_parentheses(s) if isinstance(n.a, Op) and n.a.op in "+-" else s)
    if isinstance(n, Op):
        if n.op == "/":
            return r"\frac{" + tex(n.a) + "}{" + tex(n.b) + "}"
        g, d = tex(n.a), tex(n.b)
        if n.op == "+":                                   # a + (−b) s'écrit a − b : jamais « + − »
            if isinstance(n.b, Neg):
                return tex(Op("-", n.a, n.b.a))
            if isinstance(n.b, Nb) and n.b.val < 0:
                return tex(Op("-", n.a, Nb(-n.b.val, n.b.dec)))
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
        if isinstance(n.a, (Op, Neg, Log, Pow)) or (isinstance(n.a, Nb) and (n.a.val < 0 or n.a.pct is not None or (n.a.val.denominator != 1 and n.a.dec is None))):
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
_MINUSCULES = str.maketrans("ABCDEFGHIJKLMNOPQRSTUVWXYZ", "abcdefghijklmnopqrstuvwxyz")      # str.lower() peut changer la longueur : seulement l'ASCII
_NOM_INDEXE = re.compile(r"[A-Za-z](?:_([0-9]+)|(?<=[A-Z])([0-9]+))")      # C0, V0, C_0, c_0 (x2 reste x · 2 : message de lecture)
_SYMBOLES = str.maketrans({"−": "-", "–": "-", "×": "*", "·": "*", "⋅": "*", "÷": "/", "²": "^2", "³": "^3"})   # x² se lit x^2 (clavier de téléphone)
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


def _lire_nom(texte, i):
    """(nom, fin) de la lettre en texte[i] : un nom indexé (C0, V_0, c_0) est une seule inconnue, écrite sans tiret bas (C0) ; e est le nombre e."""
    if texte[i] in "eE":
        return "e", i + 1
    m = _NOM_INDEXE.match(texte, i)
    return (texte[i] + (m.group(1) or m.group(2)), m.end()) if m else (texte[i], i + 1)


def _base_entre_parentheses(s, debut, brut):
    """(("expr", jetons), fin) pour la base écrite entre parenthèses en s[debut] == "(" (la parenthèse fermante qui lui correspond)."""
    profondeur = 0
    for k in range(debut, len(s)):
        if s[k] == "(":
            profondeur += 1
        elif s[k] == ")":
            profondeur -= 1
            if profondeur == 0:
                interieur = brut[debut + 1:k]
                if not interieur.strip():
                    raise ErreurSaisie("La base d'un logarithme est vide : log_(2x)(1296).")
                return ("expr", tokeniser(interieur)), k + 1
    raise ErreurSaisie("Il manque une parenthèse fermante.")


def tokeniser(texte):
    brut = texte.strip().translate(_SYMBOLES)
    s = brut.translate(_MINUSCULES)                     # les noms de fonction ne tiennent pas compte de la casse, les lettres oui
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
        elif c == "%":
            if not toks or toks[-1].type != "num":
                raise ErreurSaisie(MESSAGE_POURCENT)
            toks.append(Tok("pct", "%", None))
            i += 1
        elif c.isalpha() and c.isascii():
            f = _fonction(s, i)
            if f and f[0] == "log" and f[1] is None and s[f[2]:f[2] + 2] == "_(":
                base, j = _base_entre_parentheses(s, f[2] + 1, brut)           # log_(2x)(1296) : une base du 1er degré (acceptée par la filière M)
                k = j
                while k < len(s) and s[k].isspace():
                    k += 1
                if s[k:k + 1] != "(":
                    raise ErreurSaisie(MESSAGE_AUTRE_BASE)                         # log_(x) sans argument : le message de toujours
                toks.append(Tok("fn", "log", base))
                i = j
            elif f:
                nom, base, j = f
                if base is not None and base.isalpha() and base != "e":
                    base = brut[j - 1]                  # log_Q(x) : la base garde sa casse
                k = j
                while k < len(s) and s[k].isspace():
                    k += 1
                if s[k:k + 1] != "(":
                    if nom == "log" and s[j:j + 1] == "_":
                        raise ErreurSaisie(MESSAGE_AUTRE_BASE)
                    suite = nom + ("_" + base if base else "")
                    raise ErreurSaisie(f"Après {suite}, ouvrez une parenthèse : {suite}(x).")
                toks.append(Tok("fn", nom, base))
                i = j
            else:
                inconnue = _fonction_inconnue(s, i)
                if inconnue:
                    raise ErreurSaisie(f"La fonction {inconnue} n'est pas traitée par cet outil.")
                nom, i = _lire_nom(brut, i)
                toks.append(Tok("var", nom, None))
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


def _pourcentage(brut):
    """« 3,75 » suivi de % : le nombre 3,75/100 (décimal 0,0375), écrit 3,75 % pour l'aperçu."""
    t = nettoyer_saisie(brut)
    dec = format(decimal.Decimal(t).scaleb(-2), "f")
    if "." in dec:
        dec = dec.rstrip("0").rstrip(".")
    return Nb(F(t) / 100, dec.replace(".", ","), t.replace(".", ","))


def _base(nom_base):
    """Nœud de base d'un log_a : None pour 10, E() pour e, sinon un nombre (> 0, ≠ 1), une inconnue ou, écrite entre parenthèses, une expression."""
    if nom_base is None:
        return None
    if isinstance(nom_base, tuple):
        b = _Parseur(nom_base[1]).tout()
        if variables(b):
            return b
        v = _const(b)
        if v is None:
            raise ErreurSaisie("La base d'un logarithme est un nombre, une lettre ou une expression du 1er degré : log_2(x), log_a(x), log_(2x)(1296).")
        if v <= 0 or v == 1:
            raise ErreurSaisie("La base d'un logarithme est strictement positive et différente de 1.")
        return None if v == 10 else b if isinstance(b, Nb) else Nb(v)
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
            suivant = self.pic()
            if suivant is not None and suivant.type == "pct":
                self.i += 1
                return _pourcentage(p.val)
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
Saisie = namedtuple("Saisie", "genre g d inconnue parametres", defaults=((),))      # genre : « equation » ou « calcul » (d et inconnue : None) ; parametres : lettres à simplifier


def _lettres_en_exposant(n):
    """Les lettres qui figurent dans un exposant (la base d'un logarithme n'est pas un exposant)."""
    if isinstance(n, Defini):
        return _lettres_en_exposant(n.arbre)
    if isinstance(n, (Var, Nb, E)):
        return set()
    if isinstance(n, (Neg, Fn, Log)):
        return _lettres_en_exposant(n.a)
    if isinstance(n, Op):
        return _lettres_en_exposant(n.a) | _lettres_en_exposant(n.b)
    if isinstance(n, Pow):
        return variables(n.b) | _lettres_en_exposant(n.a) | _lettres_en_exposant(n.b)
    raise TypeError(n)


def _fois(a, b):
    """a · b sans le facteur 1 : 1 · b s'écrit b."""
    return b if a == Nb(1) else a if b == Nb(1) else Op("*", a, b)


def sans_facteur(n, p):
    """n divisé par la lettre p quand p en est un facteur simple (produit, quotient, opposé) et n'apparaît pas ailleurs ; sinon None.
    3Q donne 3, Q(1+t)^x donne (1+t)^x, V0/2 donne 1/2, Q donne 1."""
    if isinstance(n, Var):
        return Nb(1) if n.nom == p else None
    if isinstance(n, Neg):
        r = sans_facteur(n.a, p)
        return None if r is None else Neg(r)
    if isinstance(n, Op) and n.op == "*":
        if p not in variables(n.b) and (r := sans_facteur(n.a, p)) is not None:
            return _fois(r, n.b)
        if p not in variables(n.a) and (r := sans_facteur(n.b, p)) is not None:
            return _fois(n.a, r)
        return None
    if isinstance(n, Op) and n.op == "/" and p not in variables(n.b):
        r = sans_facteur(n.a, p)
        return None if r is None else Op("/", r, n.b)
    return None


def _liste_de_lettres(noms):
    return noms[0] if len(noms) == 1 else ", ".join(noms[:-1]) + " et " + noms[-1]


MESSAGE_AUTRE_BASE = "Pour une autre base, écrivez log_2(x) ou log_a(x) : un nombre ou une lettre après le tiret bas."


def _base_composee(n):
    """Vrai quand un logarithme de l'arbre a une base qui n'est ni un nombre, ni e, ni une seule lettre : log_(2x)(1296), log_(x+1)(5)."""
    if isinstance(n, Log):
        base = n.base
        return (base is not None and not isinstance(base, E) and variables(base) and not isinstance(base, Var)) or _base_composee(n.a)
    if isinstance(n, (Neg, Fn)):
        return _base_composee(n.a)
    if isinstance(n, (Op, Pow)):
        return _base_composee(n.a) or _base_composee(n.b)
    return False


def analyser_saisie(texte, filiere="C"):
    """La saisie analysée. `filiere` : "C" ou "M" ; une base de logarithme écrite comme une expression (log_(2x)(1296)) n'est lue qu'en filière M."""
    g, d = lire_membres(texte)
    if filiere != "M" and (_base_composee(g) or (d is not None and _base_composee(d))):
        raise ErreurSaisie(MESSAGE_AUTRE_BASE)
    if d is None:
        if variables(g):
            raise ErreurSaisie("Écrivez une équation (avec =), ou une expression sans lettre pour calculer un logarithme.")
        return Saisie("calcul", g, None, None)
    inconnues = sorted(variables(g) | variables(d))
    if not inconnues:
        raise ErreurSaisie(MESSAGE_E if contient_e(g) or contient_e(d) else "Il faut une inconnue : une lettre, par exemple x.")
    if len(inconnues) > 1:
        en_exposant = _lettres_en_exposant(g) | _lettres_en_exposant(d)
        if len(en_exposant) != 1:
            raise ErreurSaisie("Une seule inconnue : vous avez écrit " + " et ".join(inconnues) + ".")
        x = next(iter(en_exposant))
        autres = [v for v in inconnues if v != x]
        refuses = [p for p in autres if sans_facteur(g, p) is None or sans_facteur(d, p) is None]
        if refuses:                                 # un paramètre se simplifie : il est facteur de chaque membre (3Q = Q(1+t)^x)
            noms = refuses + [x]
            nombre = {2: "deux", 3: "trois"}.get(len(noms), "plusieurs")
            raise ErreurSaisie(f"Cette équation contient {nombre} inconnues : " + _liste_de_lettres(noms) + ".")
        return Saisie("equation", g, d, x, tuple(autres))
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


def _racine_entiere_exacte(n, q):
    """La racine q-ième entière exacte de l'entier n ≥ 0, ou None."""
    r = round(n ** (1 / q))
    return next((c for c in (r - 1, r, r + 1) if c >= 0 and c ** q == n), None)


def _puissance_rationnelle_exacte(a, b):
    """a^b (a > 0 rationnel, b rationnel non entier) quand c'est un rationnel (8^(2/3) = 4, 9^(3/2) = 27, (1/4)^(1/2) = 1/2) ; None sinon."""
    if a <= 0 or b.denominator > 12:
        return None
    num, den = (_racine_entiere_exacte(a.numerator, b.denominator), _racine_entiere_exacte(a.denominator, b.denominator))
    if num is None or den is None or num == 0:
        return None
    return (F(num, den)) ** b.numerator


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
        if a is None or b is None or abs(b) > 64 or (a == 0 and b < 0):
            return None
        if b.denominator != 1:
            return _puissance_rationnelle_exacte(a, b)
        return a ** int(b)
    if isinstance(n, Fn):
        a = _const(n.a)
        return None if a is None or a < 0 else _racine_carree(a)
    return None


def valeur(n, x=None):
    """Valeur numérique (float) d'un arbre ; x : valeur de l'inconnue. Sert aux valeurs « ≈ » et aux contrôles."""
    if isinstance(n, Defini):
        return valeur(n.arbre, x)
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
        if isinstance(prop, Divise):
            q = _nom_tex(prop.nom)
            s += r" \quad \text{(on divise les deux membres par } " + q + r" \text{ ; } " + q + r" > 0 \text{ : une quantité de départ est positive)}"
        elif isinstance(prop, Car):
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
        if isinstance(prop, Divise):
            rangees[-1][2] = "(" + prop.texte() + ")"
        elif isinstance(prop, Car):
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
PROP_SOMME_EXPOSANTS = "aᵐ⁺ⁿ = aᵐ · aⁿ"
PROP_MISE_EN_EVIDENCE = "mise en évidence"
PROP_REGROUPER = "on regroupe les termes de même base"
PROP_BASE_PUISSANCE_POSITIVE = "une base admissible est strictement positive, donc xᵏ > 0"
PROP_LOG_SOMME = "log(ab) = log a + log b"
PROP_LN_DEUX_MEMBRES = "ln des deux membres"
PROP_LN_PUISSANCE = "ln(a^A) = A · ln(a)"
PROP_CAR_LOG_10 = "car log(10) = 1"
PROP_CAR_LN_E = "car ln(e) = 1"
PROP_LOG_UN = "log(1) = 0"
PROP_EXPONENTIELLE = "exponentielle des deux membres"
PROP_EXP_LOG = "10^(log(A)) = A, A > 0"
PROP_EXP_LN = "e^(ln(A)) = A, A > 0"
PROP_EXP_LOG_BASE = "a^(log_a(A)) = A, A > 0"
PROP_QUOTIENT = "aᵐ / aⁿ = aᵐ⁻ⁿ"
PROP_LOG_DIFFERENCE = "log(a/b) = log a − log b"
PROP_LN_DIFFERENCE = "ln(a/b) = ln a − ln b"
PROP_CARRE = "un carré est positif ou nul"
PROP_PUISSANCE_ZERO = "a⁰ = 1"
PROP_PUISSANCE_NEGATIVE = "a⁻ᵐ = 1/aᵐ"
PROP_AUTRE_COTE = "on passe un terme de l'autre côté"
PROP_FOIS_MOINS_UN = "on multiplie les deux membres par −1"
PROP_FOIS_DENOMINATEUR = "on multiplie les deux membres par le dénominateur"
PROPRIETES = frozenset({PROP_CARRE, PROP_PUISSANCE_ZERO, PROP_PUISSANCE_NEGATIVE, PROP_AUTRE_COTE, PROP_FOIS_MOINS_UN, PROP_FOIS_DENOMINATEUR, PROP_QUOTIENT, PROP_LOG_DIFFERENCE, PROP_LN_DIFFERENCE,
                        PROP_PUISSANCE, PROP_PRODUIT, PROP_UN, PROP_MEME_BASE, PROP_ISOLER, PROP_PRODUIT_NUL, PROP_DISCRIMINANT,
                        PROP_DEFINITION_LOG, PROP_LOG_DEUX_MEMBRES, PROP_LOG_PUISSANCE, PROP_LOG_10K, PROP_LN_UN, PROP_EXPO_POSITIVE,
                        PROP_AUCUNE_SOLUTION, PROP_LOG_QUOTIENT, PROP_LOG_PRODUIT, PROP_LOG_REGROUPER, PROP_LOG_SOMME, PROP_LN_DEUX_MEMBRES, PROP_LN_PUISSANCE, PROP_CAR_LOG_10, PROP_CAR_LN_E, PROP_LOG_UN, PROP_EXPONENTIELLE, PROP_EXP_LOG, PROP_EXP_LN, PROP_EXP_LOG_BASE,
                        PROP_ISOLER_LOG, PROP_BIEN_DEFINI, PROP_BASE_LOG, PROP_SEULE_POSITIVE, PROP_BASE_PUISSANCE_POSITIVE, PROP_SOMME_EXPOSANTS, PROP_MISE_EN_EVIDENCE, PROP_REGROUPER, PROP_LOG_BASE_PUISSANCE, PROP_LN_E_PUISSANCE,
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
    `base_ecrite` : la base telle qu'écrite (nœud) ; `expo_ecrit` : l'exposant tel qu'écrit (nœud) quand il n'est pas recomposé ;
    `inverse` : le facteur est au dénominateur (8/2^x)."""
    __slots__ = ("genre", "base", "exp", "arbre", "imbrique", "base_ecrite", "expo_ecrit", "inverse")

    def __init__(self, genre, base, exp, arbre, imbrique=False, base_ecrite=None, expo_ecrit=None):
        self.genre, self.base, self.exp, self.arbre = genre, base, exp, arbre
        self.imbrique, self.base_ecrite, self.expo_ecrit = imbrique, base_ecrite, expo_ecrit
        self.inverse = False


def _aplatir(n):
    return _aplatir(n.a) + _aplatir(n.b) if isinstance(n, Op) and n.op == "*" else [n]


def _aplatir_quotient(n):
    """[(facteur, au dénominateur)] d'un produit ou d'un quotient qui contient l'inconnue : 8/2^x donne [(8, False), (2^x, True)] ;
    une constante (1/2) reste un seul facteur."""
    if isinstance(n, Op) and n.op == "*":
        return _aplatir_quotient(n.a) + _aplatir_quotient(n.b)
    if isinstance(n, Op) and n.op == "/" and variables(n):
        return _aplatir_quotient(n.a) + [(f, not inverse) for f, inverse in _aplatir_quotient(n.b)]
    return [(n, False)]


def _inverser(fac, inverse):
    fac.inverse = inverse
    return fac


def _assembler(arbres, facs):
    """Le membre écrit à partir des arbres de ses facteurs : les facteurs du dénominateur sous la barre de fraction."""
    haut = [a for a, f in zip(arbres, facs) if not f.inverse]
    bas = [a for a, f in zip(arbres, facs) if f.inverse]
    n = _produit(haut) if haut else Nb(1)
    return Op("/", n, _produit(bas)) if bas else n


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
    return [_inverser(_facteur(f, x), inverse) for f, inverse in _aplatir_quotient(n)]


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
            if c is None:                                  # log(x) + log(2) = 1 : la constante n'est pas un rationnel
                raise _Hors
            a, o = a.a, (o - c if a.op == "+" else o + c)
        elif isinstance(a, Op) and a.op in "+-" and not variables(a.a):
            c = _const(a.a)
            if c is None:
                raise _Hors
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
    # T5 : aᵐ · aⁿ = aᵐ⁺ⁿ, aᵐ / aⁿ = aᵐ⁻ⁿ
    total = [F(0)]
    for f, k in zip(facs, k_de):
        total = _padd(total, [F(k)] if f.genre == "cte" else [k * c for c in f.exp], -1 if f.inverse else 1)
    t5 = Pow(b0, _arbre_poly(total)) if len(facs) > 1 else _assembler(t4, facs)
    un = any(f.genre == "cte" and f.base == 1 for f in facs)
    etapes = [(n, None), (_assembler(t1, facs), PROP_PUISSANCE), (_assembler(t2, facs), PROP_UN if un else None),
              (_assembler(t3, facs), PROP_PUISSANCE), (_assembler(t4, facs), None),
              (t5, PROP_QUOTIENT if any(f.inverse for f in facs) else PROP_PRODUIT)]
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
        fausse = Eq(Nb(A[0]), Nb(B[0]))
        if tex_element(fausse) != tex_element(c.elements[-1]):
            c.ajouter(fausse, "⇔")
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
    standard = Eq(_arbre_poly(P, x), Nb(0))
    if tex_element(standard) != tex_element(c.elements[-1]):
        c.ajouter(standard, "⇔")
    if b == 0 and c0 == 0:                                # a·x² = 0 ⇔ x² = 0 ⇔ x = 0 (jamais Δ = 0 ni ±√0)
        if a != 1:
            c.ajouter(Eq(Pow(X, Nb(2)), Nb(0)), "⇔")
        c.ajouter(Eq(X, Nb(0)), "⇔")
        return lignes, [Nb(0)], None
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
    if delta == 0:
        racine = _nb_exact(F(-b, 2 * a))
        lignes += _une_seule_solution(X, Op("/", Nb(-b), Op("*", Nb(2), Nb(a))), racine)
        return lignes, [racine], None
    racines = _racines_du_second_degre(a, b, delta)
    fin = Chaine([Ou(Eq(X, r) for r in racines)])
    lignes.append(fin)
    return lignes, racines, None


FORMULE_RACINE_DOUBLE = r"\frac{-b}{2a}"


def _une_seule_solution(X, calcul, racine=None):
    """Les lignes qui suivent Δ = 0 : « Δ = 0 : une seule solution », puis x = −b/(2a) = calcul (= racine quand elle s'écrit plus simplement)."""
    formule = Defini(FORMULE_RACINE_DOUBLE, calcul)                    # écrit −b/(2a), vaut le calcul
    if racine is None or tex(racine) == tex(calcul):
        egalite = Eq(X, calcul, [formule])
    else:
        egalite = Eq(X, racine, [formule, calcul])
    return [Chaine([Texte(r"Δ = 0 \text{ : une seule solution}")]), Chaine([egalite])]


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
        return _essayer(lambda: _meme_base_e(g, d, x), lambda: _meme_base(g, d, x))
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
# 10. ÉQUATIONS EXPONENTIELLES : deux méthodes au choix (27.10.2026)
#     A « même base / définition » · B « logarithmes » (toujours disponible, méthode par défaut)
# =====================================================================
METHODE_MEME_BASE = "meme_base"
METHODE_LOGARITHMES = "logarithmes"
METHODES = (METHODE_MEME_BASE, METHODE_LOGARITHMES)


class Message:
    """Une phrase du corrigé qui n'est pas une chaîne d'équations (« 20 n'est pas une puissance de 3 : il faut les logarithmes. ») :
    du texte (str) et des arbres, écrits en TeX dans la page."""
    __slots__ = ("morceaux",)

    def __init__(self, *morceaux):
        self.morceaux = morceaux

    def texte(self):
        return "".join(m if isinstance(m, str) else m.tex if isinstance(m, Texte) else tex(m) for m in self.morceaux)

    def html(self):
        return "".join(_echapper(m, quote=False) if isinstance(m, str)
                       else r"\(" + _echapper(m.tex if isinstance(m, Texte) else tex(m), quote=False) + r"\)" for m in self.morceaux)


def _facteur_log(f, x):
    """Un facteur d'un membre pour la méthode « logarithmes » : comme `_facteur`, la base e en plus."""
    if isinstance(f, Pow) and isinstance(f.a, E):
        return _Fac("pow", "e", _poly(f.b, x), f, False, f.a, f.b)
    return _facteur(f, x)


def _cote_log(n, x):
    """(signe, facteurs) d'un membre : signe +1, −1 ou 0 (membre nul) ; facteurs = None quand le membre est une constante ≤ 0."""
    signe = 1
    while isinstance(n, Neg):
        signe, n = -signe, n.a
    if not variables(n):
        q = _const(n)                                      # None pour e^3 : une puissance de e est positive
        if q is None and signe < 0:
            raise _Hors
        if q is not None:
            total = signe * q
            if total <= 0:
                return (0 if total == 0 else -1), None
            if signe < 0:
                raise _Hors
    return signe, [_inverser(_facteur_log(f, x), inverse) for f, inverse in _aplatir_quotient(n)]


def _preparer(g, d, x):
    """(énoncé, g, d, cartes déjà écrites, (sg, fg, sd, fd)) : l'exponentielle isolée quand elle peut l'être, puis les facteurs de chaque membre."""
    enonce = Eq(g, d)
    try:
        g, d, iso = _isoler(g, d, x)
    except _Hors:                                          # l'autre membre n'est pas un rationnel (e^3) : rien à isoler
        iso = None
    etapes = [_carte("Isoler l'exponentielle", [iso])] if iso is not None else []
    if not (variables(g) or variables(d)):
        raise _Hors
    sg, fg = _cote_log(g, x)
    sd, fd = _cote_log(d, x)
    return enonce, g, d, etapes, (sg, fg, sd, fd)


def _resultat(genre, x, enonce, etapes, solutions, remarque=None, **autres):
    r = {"genre": genre, "inconnue": x, "enonce": enonce, "base": None, "etapes": etapes, "solutions": solutions, "remarque": remarque}
    r.update(autres)
    return r


def _vide(g, d, parse):
    """Les lignes de la carte « Aucune solution » quand un membre est ≤ 0 alors que l'autre est une exponentielle (strictement positive) ;
    None sinon."""
    sg, fg, sd, fd = parse
    if sg > 0 and sd > 0:
        return None
    if sg < 0 and sd < 0:
        raise _Hors                                            # deux membres négatifs : « Isoler les exponentielles » les multiplie par −1
    if sg > 0 and fd is None and variables(g):                 # exponentielle = nombre négatif ou nul
        positif, autre, nul = g, d, sd == 0
    elif sd > 0 and fg is None and variables(d):
        positif, autre, nul = d, g, sg == 0
    elif sg * sd < 0 and fg is not None and fd is not None:    # k·a^f = m·b^h de signes contraires
        positif, autre, nul = (g, d, False) if sg > 0 else (d, g, False)
    else:
        raise _Hors
    return [Chaine([Rel(positif, ">", Nb(0))], note=PROP_EXPO_POSITIVE),
            Chaine([Eq(positif, autre) if nul else Rel(autre, "<", Nb(0))], note=PROP_AUCUNE_SOLUTION)]


def _aucune_solution(g, d, x):
    """Résultat « S = ∅ » d'une exponentielle égale à un nombre négatif ou nul, ou de deux membres de signes contraires (même carte dans les deux
    méthodes) ; _Hors sinon."""
    enonce, g, d, etapes, parse = _preparer(g, d, x)
    lignes = _vide(g, d, parse)
    if lignes is None:
        raise _Hors
    return _resultat("aucune_solution", x, enonce, etapes + [_carte("Aucune solution", lignes)], [])


# ---------- méthode A : même base, puis définition du logarithme ----------
def _meme_base_e(g, d, x):
    """e^A = e^B ⇔ A = B (la base e : le cours l'écrit comme une autre base)."""
    if not (isinstance(g, Pow) and isinstance(g.a, E) and isinstance(d, Pow) and isinstance(d.a, E)):
        raise _Hors
    At, Bt = g.b, d.b
    l_exp, solutions, remarque = _resoudre_polynome(_poly(At, x), _poly(Bt, x), At, Bt, x)
    ligne = Chaine([Eq(g, d)])
    premiere = l_exp[0]
    ligne.ajouter(premiere.elements[0], "⇔", PROP_MEME_BASE)
    for e, lien, prop in zip(premiere.elements[1:], premiere.liens, premiere.props):
        ligne.ajouter(e, lien, prop)
    return _resultat("meme_base", x, Eq(g, d), [_carte("Même base", [ligne] + l_exp[1:])], solutions, remarque, base=None)


def _fusionner_puissances(n, x):
    """Un produit ou un quotient de puissances de 10 (ou de e) devient une seule puissance : e^(2x) / e^x donne e^x (aᵐ / aⁿ = aᵐ⁻ⁿ) ;
    n lui-même quand ce n'est pas un produit ni un quotient."""
    morceaux = _aplatir_quotient(n)
    if len(morceaux) < 2:
        return n
    facs = [_inverser(_facteur_log(f, x), inverse) for f, inverse in morceaux]
    base = facs[0].base
    if not all(f.genre == "pow" and f.base == base for f in facs) or base not in ("e", 10):
        raise _Hors
    total = [F(0)]
    for f in facs:
        total = _padd(total, f.exp, -1 if f.inverse else 1)
    if len(total) < 2 or not any(total[1:]):
        raise _Hors
    return Pow(facs[0].base_ecrite, _arbre_poly(total, x))


def _definition(g, d, x):
    """a^f = b avec a = 10 ou e et b > 0 qui n'est pas une puissance de a : 10^f = b ⇔ f = log(b), e^f = b ⇔ f = ln(b) (définition du logarithme)."""
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
    if q is None or q <= 0:
        raise _Hors
    avant = s
    s = _fusionner_puissances(s, x)
    base, valeur_base, f_tree = _exponentielle(s, x)
    f = _poly(f_tree, x)
    if len(f) not in (2, 3) or not (base_est_e(base) or valeur_base == 10):
        raise _Hors
    if valeur_base is not None and _exposant_entier(q, valeur_base) is not None:
        raise _Hors                                    # b est une puissance de a : méthode « même base »
    chaine = Chaine([Eq(g, d)])
    if inverse:
        chaine.ajouter(Eq(avant, o), "⇔")
    if avant is not s:
        chaine.ajouter(Eq(s, o), "⇔", PROP_QUOTIENT if any(i for _, i in _aplatir_quotient(avant)) else PROP_PRODUIT)
    if base_est_e(base) and q == 1:
        chaine.ajouter(Eq(f_tree, Nb(0)), "⇔", PROP_LN_UN)
        c = Nb(0)
    else:
        c = Log(o, E() if base_est_e(base) else None)
        chaine.ajouter(Eq(f_tree, c), "⇔", PROP_DEFINITION_LOG)
    suite, solutions, remarque = _suite_polynome(chaine, f, f_tree, c, x)
    etapes.append(_carte("Définition du logarithme", [chaine] + suite))
    return _resultat("definition", x, enonce, etapes, solutions, remarque, base=valeur_base)


def _message_meme_base(g, d, x):
    """La méthode A ne s'applique pas : « 20 n'est pas une puissance de 3 : il faut les logarithmes. » (la méthode B doit pouvoir lire l'équation)."""
    enonce, g, d, etapes, (sg, fg, sd, fd) = _preparer(g, d, x)
    if sg <= 0 or sd <= 0:
        raise _Hors
    facs = [f for f in fg + fd if not (f.genre == "cte" and f.base == 1)]
    noeud = lambda f: f.base_ecrite if f.genre == "pow" else f.arbre
    a = next((f for f in facs if f.genre == "pow"), None)
    b = None
    if a is not None:
        b = next((f for f in facs if (f.base == "e") != (a.base == "e")
                  or (f.base != "e" and _exposant_entier(F(f.base), F(a.base)) is None)), None)
    message = Message(noeud(b), " n'est pas une puissance de ", noeud(a), " : il faut les logarithmes.") if b is not None \
        else Message("Il faut les logarithmes.")
    carte = _carte("Même base / définition", [message])
    return _resultat("meme_base", x, enonce, etapes + [carte], [], None, message=message)


# ---------- méthode B : les logarithmes des deux membres ----------
def _terme_ecrit(f, bl, ln):
    """(arbre, monômes, milieu) du facteur f après log(a^A) = A · log(a) : exposant · log(base) pour une puissance, log(c) pour une constante
    (c = 10ᵏ s'écrit k · log(10), avec log(c) = log(10ᵏ) en écriture intermédiaire). Monômes : (coefficient, puissance de x, base du logarithme),
    la base étant une valeur (Fraction) ou « e ». Arbre None pour un facteur qui vaut 1 (a⁰, 1)."""
    if f.genre == "pow":
        if not any(f.exp):
            return None, [], []
        base = E() if f.base == "e" else f.base_ecrite
        monos = [(c, k, f.base) for k, c in reversed(list(enumerate(f.exp))) if c != 0]
        return Op("*", _expo_arbre(f), Log(base, bl)), monos, []
    c = f.base
    if c == 1:
        return None, [], []
    k = None if ln else _exposant_entier(c, F(10))
    if k is None:
        return Log(f.arbre, bl), [(F(1), 0, c)], []
    dix = Log(Nb(10))
    arbre = dix if k == 1 else Op("*", Nb(k), dix) if k > 0 else Neg(Op("*", Nb(-k), dix))
    return arbre, [(F(k), 0, F(10))], ([] if k == 1 else [Log(f.arbre), Log(Pow(Nb(10), Nb(k)))])


def _terme_converti(f, ln):
    """Le terme de f une fois log(10) = 1 (ln(e) = 1) : (x + 1) · log(10) donne x + 1 ; None quand le terme n'en contient pas."""
    if f.genre == "pow":
        return _expo_arbre(f) if f.base == ("e" if ln else F(10)) and any(f.exp) else None
    if not ln and f.base != 1:
        k = _exposant_entier(f.base, F(10))
        return None if k is None else Nb(k)
    return None


def _somme_arbres(arbres):
    n = None
    for t in arbres:
        if n is None:
            n = t
        elif isinstance(t, Neg):
            n = Op("-", n, t.a)
        elif isinstance(t, Nb) and t.val < 0:
            n = Op("-", n, Nb(-t.val))
        else:
            n = Op("+", n, t)
    return Nb(0) if n is None else n


class Car:
    """Justification « car D ≠ 0 » : on divise par le coefficient logarithmique D (1 − ln 2, log 2 − log 3)."""
    __slots__ = ("expr",)

    def __init__(self, expr):
        self.expr = expr


class Divise:
    """Justification de la carte « Simplifier par Q » : on divise les deux membres par le paramètre Q, positif parce que c'est une quantité de départ."""
    __slots__ = ("nom",)

    def __init__(self, nom):
        self.nom = nom

    def texte(self):
        q = _nom_tex(self.nom)
        return rf"on divise les deux membres par \({q}\) (\({q} > 0\) : une quantité de départ est positive)"


def _oppose(t):
    return (-t[0],) + t[1:]


def _noeud_terme(c, k, a, x, ecrit, ln):
    """|c| · xᵏ · log(a), le coefficient 1 étant omis ; a = None : le logarithme est déjà un nombre. `ecrit` : la base telle qu'écrite
    dans l'énoncé ((1/2)^x garde log(1/2), pas log(0,5))."""
    c = abs(c)
    coef = _arbre_poly([F(0)] * k + [c], x) if k else (_nb_exact(c) if c != 1 or a is None else None)
    if a is None:
        return coef
    lg = Log(ecrit.get(a, _nb_exact(a)), E() if ln else None)
    return lg if coef is None else Op("*", coef, lg)


def _fusionner(termes):
    """Les termes de même logarithme et de même puissance de x additionnés : 2 log 2 + log 2 = 3 log 2 ; les termes nuls disparaissent."""
    vus = {}
    for c, k, a in termes:
        vus[(k, a)] = vus.get((k, a), 0) + c
    return [(c, k, a) for (k, a), c in vus.items() if c != 0]


def _trier(termes):
    """Les termes positifs d'abord (log 3 + 4 log 2, jamais − log 2 + log 3), l'ordre d'écriture sinon."""
    termes = _fusionner(termes)
    return [t for t in termes if t[0] > 0] + [t for t in termes if t[0] < 0]


def _somme(termes, x, ecrit, ln, trier=True):
    """Somme écrite comme à la main : x log 2 − log 2, 3 log 6 − log 4 ; 0 si elle est vide."""
    termes = _trier(termes) if trier else _fusionner(termes)
    n = None
    for c, k, a in termes:
        t = _noeud_terme(c, k, a, x, ecrit, ln)
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
    final = Log(_nb_exact(R))
    formes = [c for c, _, _ in termes]
    if formes == [1]:
        return final, "seul", None
    genre = "quotient" if formes == [1, -1] else "produit" if formes == [1, 1] else "general"
    base = lambda a: ecrit.get(a, _nb_exact(a))
    puissance = lambda a, c: base(a) if c == 1 else Pow(base(a), Nb(c))
    haut = [puissance(a, c) for c, _, a in termes if c > 0]
    bas = [puissance(a, -c) for c, _, a in termes if c < 0]
    produit = _produit(haut) if haut else Nb(1)
    if bas:
        produit = Op("/", produit, _produit(bas))
    ligne = Chaine([_somme([(c, 0, a) for c, _, a in termes], None, ecrit, False, False)])
    ligne.ajouter(Log(produit), "=", PROP_LOG_REGROUPER)
    if tex(ligne.elements[-1]) != tex(final):
        ligne.ajouter(final, "=")
    return final, genre, ligne


def base_est_e(base):
    return isinstance(base, E)


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
        if isinstance(c, Nb):                                  # c est un nombre : le calcul se fait (x + 1 = 8 donne x = 7)
            haut = _nb_exact(c.val - q0)
        else:
            haut = Op("-", c, _nb_ecrit(q0, ecrit)) if q0 > 0 else Op("+", _nb_ecrit(-q0, ecrit), c)
        chaine.ajouter(Eq(_arbre_poly([F(0), p], x, ecrit), haut), "⇔")
    if p == 1:
        return haut
    if isinstance(haut, Nb):
        solution = _nb_exact(haut.val / p)
    else:
        solution = Neg(haut) if p == -1 else Op("/", haut, _nb_ecrit(p, ecrit))
    chaine.ajouter(Eq(Var(x), solution), "⇔")
    return solution


def _suite_polynome(chaine, f, f_tree, c, x):
    """Ajoute à `chaine` (qui se termine par « P(x) = c », P de degré 1 ou 2, c une constante écrite, avec ou sans logarithme) les lignes qui
    résolvent l'équation ; renvoie (lignes suivantes, solutions, remarque). Degré 2 : x² = k donne x = ±√k (k < 0 : aucune solution, un carré
    est positif ou nul) ; sinon le discriminant, Δ, x₁ et x₂ nommés quand c contient un logarithme."""
    if len(f) == 2:
        return [], [_suite_lineaire(chaine, f[1], f[0], c, x, f_tree)], None
    if len(f) != 3:
        raise _Hors
    X, X2 = Var(x), Pow(Var(x), Nb(2))
    q, b, a = f
    if b == 0:                                            # a·x² + q = c : x² = k
        haut = c
        if q != 0:
            haut = _nb_exact(c.val - q) if isinstance(c, Nb) else Op("-", c, _nb_ecrit(q, f_tree)) if q > 0 else Op("+", _nb_ecrit(-q, f_tree), c)
            chaine.ajouter(Eq(_arbre_poly([F(0), F(0), a], x, f_tree), haut), "⇔")
        k = haut if a == 1 else _nb_exact(haut.val / a) if isinstance(haut, Nb) else Neg(haut) if a == -1 else Op("/", haut, _nb_ecrit(a, f_tree))
        if a != 1:
            chaine.ajouter(Eq(X2, k), "⇔")
        signe = _signe(k)
        if signe < 0:
            return [Chaine([Rel(X2, "≥", Nb(0))], note=PROP_CARRE), Chaine([Rel(k, "<", Nb(0))], note=PROP_AUCUNE_SOLUTION)], [], None
        if signe == 0:
            if not isinstance(k, Nb):
                chaine.elements[-1] = Eq(X2, Nb(0), [k])
            chaine.ajouter(Eq(X, Nb(0)), "⇔")
            return [], [Nb(0)], None
        kv = _const(k)
        r = _racine_carree(kv) if kv is not None else None
        if r is not None:                                  # x² = 4 ⇔ x = −2 ou x = 2
            chaine.ajouter(Ou([Eq(X, _nb_exact(-r)), Eq(X, _nb_exact(r))]), "⇔")
            return [], [_nb_exact(-r), _nb_exact(r)], None
        # x₁ = −√k et x₂ = √k portent un nom, comme pour le discriminant : S = {x₁ ; x₂}, soit x ≈ … tient à 360 px
        racines = [Defini("x_{1}", Neg(Fn("sqrt", k))), Defini("x_{2}", Fn("sqrt", k))]
        return [Chaine([Eq(n, n.arbre)]) for n in racines], racines, None
    if isinstance(c, Nb):                                  # coefficients rationnels : la résolution de la méthode « même base »
        try:
            l_poly, solutions, remarque = _resoudre_polynome(f, [c.val], f_tree, c, x)
        except _Hors:
            l_poly = None
        if l_poly is not None:
            for e, lien, prop in zip(l_poly[0].elements[1:], l_poly[0].liens, l_poly[0].props):
                chaine.ajouter(e, lien, prop)
            return l_poly[1:], solutions, remarque
    # a·x² + b·x + q − c = 0, puis Δ = b² − 4a(q − c)
    constante = Neg(c) if q == 0 else Op("-", _nb_ecrit(q, f_tree), c)
    chaine.ajouter(Eq(Op("-", _arbre_poly(f, x, f_tree), c), Nb(0)), "⇔")
    r0 = b * b - 4 * a * q
    terme = c if 4 * a == 1 else Op("*", _nb_exact(4 * a), c)
    delta = terme if r0 == 0 else Op("+", _nb_exact(r0), terme)
    formule = Op("-", Pow(_nb_exact(b), Nb(2)), Op("*", Op("*", Nb(4), _nb_exact(a)), constante))
    D = Defini("Δ", delta)
    signe = _signe(delta)
    lignes = [Chaine([D, formule, delta] + ([Nb(0)] if signe == 0 else []), ["="] * (3 if signe == 0 else 2),
                     [None] * (2 if signe == 0 else 1) + [PROP_DISCRIMINANT])]
    if signe < 0:
        return lignes, [], "Δ < 0 : l'équation n'a aucune solution réelle."
    if signe == 0:
        lignes += _une_seule_solution(X, Op("/", _nb_exact(-b), Op("*", Nb(2), _nb_exact(a))), _nb_exact(-b / (2 * a)))
        return lignes, [_nb_exact(-b / (2 * a))], None
    moins_b = _nb_exact(-b)
    haut = lambda s: (Op("-" if s < 0 else "+", moins_b, Fn("sqrt", D)) if b != 0 else (Neg(Fn("sqrt", D)) if s < 0 else Fn("sqrt", D)))
    division = lambda h: h if 2 * a == 1 else Op("/", h, _nb_exact(2 * a))
    premier = -1 if a > 0 else 1                           # x₁ < x₂ : avec a < 0, c'est « + √Δ » qui donne la plus petite racine
    racines = [Defini("x_{1}", division(haut(premier))), Defini("x_{2}", division(haut(-premier)))]
    lignes += [Chaine([Eq(r, r.arbre)]) for r in racines]
    return lignes, racines, None


@_avec_decimaux
def logarithmes(g, d, x):
    """Corrigé de g = d par la méthode B « logarithmes » : le logarithme des deux membres (ln dès qu'une base e apparaît), log(a^A) = A · log(a)
    sur toute puissance écrite, puis log(10) = 1 (ln(e) = 1) ; jamais la définition du logarithme. Sans produit nul. None si elle ne s'applique pas."""
    try:
        return _logarithmes(g, d, x)
    except _Hors:
        return None


def _logarithmes(g, d, x):
    try:
        return _aucune_solution(g, d, x)
    except _Hors:
        pass
    enonce, g, d, etapes, (sg, fg, sd, fd) = _preparer(g, d, x)
    if sg <= 0 or sd <= 0:
        raise _Hors
    ln = any(f.genre == "pow" and f.base == "e" for f in fg + fd)
    seul = len(fg) == 1 and len(fd) == 1 and variables(g) != variables(d)
    if seul:
        s, o = (fg[0], fd[0]) if variables(g) else (fd[0], fg[0])
        seul = s.genre == "pow" and len(s.exp) in (2, 3) and (o.genre == "cte" or any(o.exp))
    if seul:
        lignes, solutions, remarque = _alpha(g, d, x, fg, fd, ln)
    else:
        lignes, solutions, remarque = _beta(g, d, x, fg, fd, ln)
    return _resultat("logarithmes", x, enonce, etapes + [_carte("Logarithme des deux membres", lignes)], solutions, remarque)


def _alpha(g, d, x, fg, fd, ln):
    """a^f = b (f du 1er ou du 2e degré, b une constante) : f · log(a) = log(b), on divise par log(a), puis on isole x (corrigé 2.23) ;
    au 2e degré, x² = k ou le discriminant (`_suite_polynome`)."""
    inverse = not variables(g)
    s, o, fs, fo = (d, g, fd[0], fg[0]) if inverse else (g, d, fg[0], fd[0])
    bl = E() if ln else None
    cle = "e" if ln else F(10)
    chaine = Chaine([Eq(g, d)])
    if inverse:
        chaine.ajouter(Eq(s, o), "⇔")
    chaine.ajouter(Eq(Log(s, bl), Log(o, bl)), "⇔", PROP_LN_DEUX_MEMBRES if ln else PROP_LOG_DEUX_MEMBRES)
    f_tree = _expo_arbre(fs)
    base_s = E() if fs.base == "e" else fs.base_ecrite
    gauche = Op("*", f_tree, Log(base_s, bl))
    droite, _, milieu = _terme_ecrit(fo, bl, ln)
    un = droite is None                                              # le second membre vaut 1 : log(1) = 0
    if un:
        droite = Log(fo.arbre, bl)
    chaine.ajouter(Eq(gauche, droite, milieu), "⇔", PROP_LN_PUISSANCE if ln else PROP_LOG_PUISSANCE)
    if un:
        chaine.ajouter(Eq(gauche, Nb(0)), "⇔", PROP_LN_UN if ln else PROP_LOG_UN)
        reste = Nb(0)
    else:
        reste = _terme_converti(fo, ln)                              # le second membre sans log(10) ou ln(e)
    prop_un = PROP_CAR_LN_E if ln else PROP_CAR_LOG_10
    a_node = Log(base_s, bl)
    if fs.base == cle:                                               # f · log(10) = … : log(10) = 1
        c = reste if reste is not None else droite
        chaine.ajouter(Eq(f_tree, c), "⇔", prop_un)
    else:
        if reste is not None and not un:
            chaine.ajouter(Eq(gauche, reste), "⇔", prop_un)
        if un:
            c = Nb(0)
        elif fo.genre == "pow" and fo.base == fs.base:               # f · log(a) = k · log(a) : on divise par log(a)
            c = _expo_arbre(fo)
        else:
            c = Op("/", reste if reste is not None else droite, a_node)
        chaine.ajouter(Eq(f_tree, c), "⇔", Car(a_node))
    suite, solutions, remarque = _suite_polynome(chaine, fs.exp, f_tree, c, x)
    return [chaine] + suite, solutions, remarque


def _beta(g, d, x, fg, fd, ln):
    """k·a^f = m·b^h et toutes les formes à plusieurs facteurs : logarithme des deux membres, développement, les termes en x d'un côté,
    x en facteur, division par le coefficient logarithmique (corrigé 2.24) ; du 2ᵉ degré par le discriminant."""
    bl = E() if ln else None
    cle = "e" if ln else F(10)
    ecrit = {}
    for f in fg + fd:
        if f.genre == "pow" and f.base != "e":
            ecrit.setdefault(f.base, f.base_ecrite)
        elif f.genre == "cte":
            ecrit.setdefault(f.base, f.arbre)
    chaine = Chaine([Eq(g, d)])
    chaine.ajouter(Eq(Log(g, bl), Log(d, bl)), "⇔", PROP_LN_DEUX_MEMBRES if ln else PROP_LOG_DEUX_MEMBRES)
    utiles = lambda facs: [f for f in facs if not (f.genre == "cte" and f.base == 1 and not f.inverse)] or facs[:1]   # un facteur 1 n'écrit pas log(1)
    signe = lambda f, a: Neg(a) if f.inverse and a is not None else a                                  # un facteur du dénominateur : − log(v)
    if len(utiles(fg)) > 1 or len(utiles(fd)) > 1:                   # log(ab) = log a + log b, log(a/b) = log a − log b
        separe = lambda facs: _somme_arbres([signe(f, Log(f.arbre, bl)) for f in utiles(facs)])
        inverses = [f.inverse for f in utiles(fg) + utiles(fd)]
        produits = sum(1 for f in utiles(fg) if not f.inverse) > 1 or sum(1 for f in utiles(fd) if not f.inverse) > 1
        prop = PROP_LOG_SOMME if not any(inverses) else PROP_LOG_REGROUPER if produits else PROP_LN_DIFFERENCE if ln else PROP_LOG_DIFFERENCE
        chaine.ajouter(Eq(separe(fg), separe(fd)), "⇔", prop)
    ecrits = lambda facs: [(signe(f, t[0]), [(-c, k, a) if f.inverse else (c, k, a) for c, k, a in t[1]], t[2])
                           for f, t in zip(facs, (_terme_ecrit(f, bl, ln) for f in facs))]
    tg, td = ecrits(fg), ecrits(fd)
    chaine.ajouter(Eq(_somme_arbres([t[0] for t in tg if t[0] is not None]), _somme_arbres([t[0] for t in td if t[0] is not None])),
                   "⇔", PROP_LN_PUISSANCE if ln else PROP_LOG_PUISSANCE)
    monos_g, monos_d = [m for t in tg for m in t[1]], [m for t in td for m in t[1]]
    conv = [signe(f, _terme_converti(f, ln)) for f in fg + fd]
    if any(c is not None for c in conv):                             # log(10) = 1, ln(e) = 1
        cg, cd = conv[:len(fg)], conv[len(fg):]
        arbre_g = _somme_arbres([c if c is not None else t[0] for c, t in zip(cg, tg) if c is not None or t[0] is not None])
        arbre_d = _somme_arbres([c if c is not None else t[0] for c, t in zip(cd, td) if c is not None or t[0] is not None])
        chaine.ajouter(Eq(arbre_g, arbre_d), "⇔", PROP_CAR_LN_E if ln else PROP_CAR_LOG_10)
        monos_g = [(c, k, None if a == cle else a) for c, k, a in monos_g]
        monos_d = [(c, k, None if a == cle else a) for c, k, a in monos_d]
    return _fin_beta(chaine, monos_g, monos_d, x, ecrit, ln)


def _fin_beta(chaine, monos_g, monos_d, x, ecrit, ln):
    """La fin de la méthode B (aussi utilisée par la filière M) : les monômes c·xᵏ·log(a) (a None : un nombre) des deux membres, les termes en x d'un côté,
    puis le degré 0, 1 ou 2 ; `ecrit` : base → nœud tel qu'il est écrit."""
    mg = sorted(_fusionner(monos_g), key=lambda t: -t[1])           # les termes en x d'abord : x log 2 + log 2
    md = sorted(_fusionner(monos_d), key=lambda t: -t[1])
    developpe = Eq(_somme(mg, x, ecrit, ln, False), _somme(md, x, ecrit, ln, False))
    if tex_element(developpe) != tex_element(chaine.elements[-1]):    # (x − 1) log 2 devient x log 2 − log 2
        chaine.ajouter(developpe, "⇔")
    P = _fusionner(mg + [_oppose(t) for t in md])
    degre = max([k for _, k, _ in P], default=0)
    if degre == 0:
        return _degre_zero(chaine, P, mg, md, x, ecrit, ln)
    if degre == 1:
        return _premier_degre(chaine, mg, md, x, ecrit, ln)
    if degre == 2:
        if all(a is None for _, _, a in P):                           # log(10) = 1 a tout rendu numérique : le trinôme ordinaire
            poly = lambda ms: [sum((c for c, k, _ in ms if k == i), F(0)) for i in range(3)]
            l_poly, solutions, remarque = _resoudre_polynome(_pnet(poly(mg)), _pnet(poly(md)), _somme(mg, x, ecrit, ln, False),
                                                              _somme(md, x, ecrit, ln, False), x)
            premiere = l_poly[0]
            for e, lien, prop in zip(premiere.elements[1:], premiere.liens, premiere.props):
                chaine.ajouter(e, lien, prop)
            return [chaine] + l_poly[1:], solutions, remarque
        return _second_degre(chaine, P, x, ecrit, ln)
    raise _Hors


def _valeur_terme(t):
    return float(t[0]) if t[2] is None else float(t[0]) * math.log(t[2])


def _degre_zero(chaine, P, mg, md, x, ecrit, ln):
    """Les termes en x disparaissent : 0 = 0 (tout réel) ou 0 = C (aucune solution)."""
    cte = _trier([_oppose(t) for t in mg] + md)
    if not cte:
        chaine.ajouter(Eq(Nb(0), Nb(0)), "⇔")
        return [chaine], None, "Cette égalité est vraie pour tout nombre réel."
    if any(a is not None for _, _, a in cte) and abs(sum(_valeur_terme(t) for t in cte)) < 1e-12:
        raise _Hors
    chaine.ajouter(Eq(Nb(0), _somme(cte, x, ecrit, ln)), "⇔")
    return [chaine], [], "Cette égalité est fausse : l'équation n'a aucune solution."


def _premier_degre(chaine, mg, md, x, ecrit, ln):
    X = Var(x)
    xg, xd = [t for t in mg if t[1] == 1], [t for t in md if t[1] == 1]
    cg, cd = [t for t in mg if t[1] == 0], [t for t in md if t[1] == 0]
    # les termes en x du côté qui laisse la constante positive (2.24 a : à gauche ; b et c : à droite)
    a_gauche = sum(_valeur_terme(t) for t in cd) - sum(_valeur_terme(t) for t in cg) > -1e-12
    cotes = lambda gauche: (xg + [_oppose(t) for t in xd], [_oppose(t) for t in cg] + cd) if gauche else \
        (xd + [_oppose(t) for t in xg], [_oppose(t) for t in cd] + cg)
    coeff, cte = cotes(a_gauche)
    if all(a is None for _, _, a in _fusionner(coeff)) and sum(c for c, _, _ in _fusionner(coeff)) < 0:
        a_gauche = not a_gauche                            # ln(3) − x = ln(6) : x à droite, jamais x · (−1)
        coeff, cte = cotes(a_gauche)
    coeff = [(c, 0, a) for c, _, a in _fusionner(coeff)]
    D, C = _somme(coeff, x, ecrit, ln), _somme(cte, x, ecrit, ln)
    if abs(valeur(D)) < 1e-12:
        raise _Hors                                        # p·log a = r·log b : une même base écrite autrement
    if ln and len(coeff) > 1:                               # x − x ln 2 = 0 : les termes en x réunis, comme dans l'équation du premier degré
        reunis = _somme([(c, 1, a) for c, _, a in coeff], x, ecrit, ln)
        chaine.ajouter(Eq(reunis, C) if a_gauche else Eq(C, reunis), "⇔")
    pur = isinstance(D, Nb)
    if pur and D.val == 1:
        if tex_element(Eq(X, C)) != tex_element(chaine.elements[-1]):
            chaine.ajouter(Eq(X, C), "⇔")
        solution = C
    else:
        facteur = Op("*", X, D)
        chaine.ajouter(Eq(facteur, C) if a_gauche else Eq(C, facteur), "⇔")
        if not _fusionner(cte):                            # x(log 3 − log 2) = 0
            chaine.ajouter(Eq(X, Nb(0)), "⇔", None if pur else Car(D))
            return [chaine], [Nb(0)], None
        if pur and isinstance(C, Nb):
            solution = Nb(C.val / D.val)
            chaine.ajouter(Eq(X, solution), "⇔")
        else:
            chaine.ajouter(Eq(X, Op("/", C, D)), "⇔", None if pur else Car(D))
            solution = Op("/", C, D)
    lignes = [chaine]
    if not pur and not ln and _fusionner(cte):
        haut, bas = _regrouper(cte, ecrit), _regrouper(coeff, ecrit)
        if haut is not None and bas is not None:
            genres = {haut[1], bas[1]} - {"seul"}
            prop = {"quotient": PROP_LOG_QUOTIENT, "produit": PROP_LOG_PRODUIT}.get(next(iter(genres)) if len(genres) == 1 else None,
                                                                                    PROP_LOG_REGROUPER)
            solution = Op("/", haut[0], bas[0])
            chaine.ajouter(solution, "=", prop)
            if prop == PROP_LOG_REGROUPER:
                lignes += [p[2] for p in (haut, bas) if p[2] is not None]
            un = Log(Nb(10))
            if haut[0] == bas[0]:                          # log(125)/log(125) : le numérateur et le dénominateur sont égaux
                solution = Nb(1)
                chaine.ajouter(solution, "=")
            elif un in (haut[0], bas[0]):                  # log(2 · 5) = log(10) : log(10) = 1
                solution = Op("/", Nb(1) if haut[0] == un else haut[0], Nb(1) if bas[0] == un else bas[0])
                chaine.ajouter(solution, "=", PROP_CAR_LOG_10)
    return lignes, [solution], None


def _second_degre(chaine, P, x, ecrit, ln):
    """a·x² + b·x + c = 0 à coefficients logarithmiques : mise en facteur de x quand c = 0, sinon le discriminant."""
    X = Var(x)
    if sum(_valeur_terme(t) for t in P if t[1] == 2) < 0:
        P = [_oppose(t) for t in P]
    P = sorted(P, key=lambda t: -t[1])
    zero = Eq(_somme(P, x, ecrit, ln, False), Nb(0))
    if tex_element(zero) != tex_element(chaine.elements[-1]):
        chaine.ajouter(zero, "⇔")
    A = [(c, 0, a) for c, k, a in P if k == 2]
    B = [(c, 0, a) for c, k, a in P if k == 1]
    C = [(c, 0, a) for c, k, a in P if k == 0]
    Anode = _somme(A, x, ecrit, ln)
    if _signe(Anode) == 0 or (B and _signe(_somme(B, x, ecrit, ln)) == 0):
        raise _Hors                                       # (log 0,5 + log 2) · x² : une même base écrite autrement, comme au premier degré
    if not C and not B:                                   # a·x² = 0 ⇔ x² = 0 ⇔ x = 0
        chaine.ajouter(Eq(Pow(X, Nb(2)), Nb(0)), "⇔", None if isinstance(Anode, Nb) else Car(Anode))
        chaine.ajouter(Eq(X, Nb(0)), "⇔")
        return [chaine], [Nb(0)], None
    if not C:                                             # x(a·x + b) = 0
        interieur = _somme([(c, k - 1, a) for c, k, a in P], x, ecrit, ln, False)
        chaine.ajouter(Eq(Op("*", X, interieur), Nb(0)), "⇔")
        chaine.ajouter(Ou([Eq(X, Nb(0)), Eq(interieur, Nb(0))]), "⇔", PROP_PRODUIT_NUL)
        racine = Op("/", _somme([_oppose(t) for t in B], x, ecrit, ln), Anode)
        suite = Chaine([Eq(interieur, Nb(0)), Eq(X, racine)], ["⇔"], [Car(Anode)])
        if _valeur_rationnelle(racine) is not None:          # log(8)/log(2) = 3 : le contrôle à la calculatrice l'écrit
            return [chaine, suite], sorted([Nb(0), racine], key=valeur), None
        nom = Defini("x_{1}" if valeur(racine) < 0 else "x_{2}", racine)   # S = {x₁ ; 0} tient à 360 px, pas S = {(log 2 − log 3)/log 2 ; 0}
        solutions = sorted([Nb(0), nom], key=valeur)
        return [chaine, suite, Chaine([Eq(nom, racine)])], solutions, None
    Bnode, Cnode = _somme(B, x, ecrit, ln), _somme(C, x, ecrit, ln)
    produit = Op("*", Op("*", Nb(4), Anode), Cnode)
    delta = Op("-", Pow(Bnode, Nb(2)), produit) if B else Neg(produit)
    signe = _signe(delta)
    D = Defini("Δ", delta)                                 # les lignes suivantes écrivent Δ, pas son expression : elles tiennent à 360 px
    lignes = [chaine, Chaine([D, delta, Nb(0)], ["=", "="], [None, PROP_DISCRIMINANT]) if signe == 0 else
              Chaine([D, delta], ["="], [PROP_DISCRIMINANT])]
    if signe < 0:
        return lignes, [], "Δ < 0 : l'équation n'a aucune solution réelle."
    moins_b = _somme([_oppose(t) for t in B], x, ecrit, ln) if B else None
    deux_a = Op("*", Nb(2), Anode)
    if signe == 0:
        racine = Op("/", moins_b, deux_a) if B else Nb(0)
        lignes += _une_seule_solution(X, racine)
        return lignes, [racine], None
    racine = Fn("sqrt", D)
    haut = (lambda signe: Op("-" if signe < 0 else "+", moins_b, racine)) if B else (lambda signe: Neg(racine) if signe < 0 else racine)
    premier = -1 if _signe(Anode) > 0 else 1                        # x₁ < x₂ : avec a < 0, c'est « + √Δ » qui donne la plus petite racine
    racines = [Defini("x_{1}", Op("/", haut(premier), deux_a)), Defini("x_{2}", Op("/", haut(-premier), deux_a))]
    lignes += [Chaine([Eq(r, r.arbre)]) for r in racines]          # x₁ = (−b − √Δ)/(2a) et x₂ = (−b + √Δ)/(2a), puis S = {x₁ ; x₂}
    return lignes, racines, None


# ---------- les deux méthodes, et leur choix ----------
def _essayer(*essais):
    for essai in essais:
        try:
            return essai()
        except _Hors:
            continue
    raise _Hors


def _un_facteur(g, d, x, methode):
    """Résolution sans produit nul : méthode B, ou méthode A (aucune solution, même base, définition, sinon le message)."""
    if methode == METHODE_LOGARITHMES:
        return _logarithmes(g, d, x)
    return _essayer(lambda: _aucune_solution(g, d, x), lambda: _essayer(lambda: _meme_base_e(g, d, x), lambda: _meme_base(g, d, x)),
                    lambda: _definition(g, d, x), lambda: _multiplier_le_denominateur(g, d, x, methode), lambda: _message_meme_base(g, d, x))


def _multiplier_le_denominateur(g, d, x, methode):
    """Méthode A, une exponentielle au dénominateur qui n'est pas de la même base : on multiplie les deux membres par le dénominateur
    (3/e^x = 6 ⇔ 3 = 6 · e^x), puis la méthode continue."""
    if not any(isinstance(n, Op) and n.op == "/" and variables(n.b) for n in (g, d)):
        raise _Hors
    return _apres_isolement(g, d, x, methode)


def _termes_signes(n):
    """Les termes d'une somme avec leur signe : 2^x − 3^(x+1) donne [(1, 2^x), (−1, 3^(x+1))]."""
    if isinstance(n, Op) and n.op in "+-":
        droite = _termes_signes(n.b)
        return _termes_signes(n.a) + (droite if n.op == "+" else [(-s, t) for s, t in droite])
    if isinstance(n, Neg):
        return [(-s, t) for s, t in _termes_signes(n.a)]
    return [(1, n)]


def _isoler_exponentielles(g, d, x):
    """(g', d', chaîne) : l'équation récrite avec une exponentielle (ou un produit d'exponentielles) dans chaque membre, comme à la main :
    a^P − b^Q = 0 ⇔ a^P = b^Q et a^P + b^Q = 0 ⇔ a^P = −b^Q (on passe un terme de l'autre côté) ; −a^P = −b^Q ⇔ a^P = b^Q (on multiplie
    les deux membres par −1) ; u/v = c ⇔ u = c · v (on multiplie les deux membres par le dénominateur). _Hors sinon."""
    for s, o, inverse in ((g, d, False), (d, g, True)):
        termes = _termes_signes(s)
        if _const(o) == 0 and len(termes) == 2 and all(_classe(t) == "exp" for _, t in termes):
            (s1, t1), (s2, t2) = termes
            if s1 < 0 < s2:
                (s1, t1), (s2, t2) = (s2, t2), (s1, t1)
            a, b = (t1, t2) if s1 * s2 < 0 else (t1, Neg(t2))
            return a, b, Chaine([Eq(g, d), Eq(a, b)], ["⇔"], [PROP_AUTRE_COTE])
        if isinstance(s, Op) and s.op == "/" and variables(s.b) and _classe(s.b) == "exp" and _classe(o) in ("cte", "exp"):
            produit = s.b if _const(o) == 1 else Nb(0) if _const(o) == 0 else Op("*", o, s.b)
            a, b = (produit, s.a) if inverse else (s.a, produit)
            return a, b, Chaine([Eq(g, d), Eq(a, b)], ["⇔"], [PROP_FOIS_DENOMINATEUR])
    if isinstance(g, Neg) and isinstance(d, Neg) and variables(g) and variables(d):
        return g.a, d.a, Chaine([Eq(g, d), Eq(g.a, d.a)], ["⇔"], [PROP_FOIS_MOINS_UN])
    raise _Hors


def _apres_isolement(g, d, x, methode):
    """La résolution de l'équation récrite par `_isoler_exponentielles`, précédée de la carte « Isoler les exponentielles » ; quand la résolution
    commence elle-même par isoler l'exponentielle (8 = 2 · 2^x ⇔ 2^x = 4), les deux chaînes n'en font qu'une."""
    g2, d2, chaine = _isoler_exponentielles(g, d, x)
    r = dict(_resolution(g2, d2, x, methode))
    etapes = list(r["etapes"])
    if etapes and etapes[0]["titre"] in ("Isoler l'exponentielle", "Isoler les exponentielles") and len(etapes[0]["lignes"]) == 1:
        suite = etapes.pop(0)["lignes"][0]
        for e, lien, prop in zip(suite.elements[1:], suite.liens, suite.props):
            chaine.ajouter(e, lien, prop)
    r["etapes"] = [_carte("Isoler les exponentielles", [chaine])] + etapes
    r["enonce"] = Eq(g, d)
    return r


class _Terme:
    """Un terme exponentiel c · a^f d'une somme : `coef` (rationnel, signe compris), `fac` (le facteur puissance), `n` (l'entier dont l'exposant dépasse le plus petit)."""
    __slots__ = ("coef", "fac", "terme", "n")

    def __init__(self, coef, fac, terme):
        self.coef, self.fac, self.terme, self.n = coef, fac, terme, 0


def _terme_exponentiel(signe, t, x):
    """c · a^f (ou a^f · c, a^f / c) : un facteur puissance et des constantes rationnelles positives ; _Hors sinon."""
    facs = [_inverser(_facteur_log(f, x), inverse) for f, inverse in _aplatir_quotient(t)]
    puissances = [f for f in facs if f.genre == "pow" and variables(f.arbre)]
    if len(puissances) != 1 or any(f.genre != "cte" and f is not puissances[0] for f in facs) or puissances[0].imbrique:
        raise _Hors
    coef = F(signe)
    for f in facs:
        if f.genre == "cte":
            coef = coef / f.base if f.inverse else coef * f.base
    return _Terme(coef, puissances[0], t)


def _terme_de_la_somme(t, base):
    """Le terme |c| · aⁿ de la parenthèse de la mise en évidence : 2^x (1 + 2), 2^x (3 + 2^2), 2^x (1 - 2) ; le signe est écrit par la somme."""
    coef = abs(t.coef)
    puissance = None if t.n == 0 else base if t.n == 1 else Pow(base, Nb(t.n))
    morceaux = ([_nb_exact(coef)] if coef != 1 or puissance is None else []) + ([puissance] if puissance is not None else [])
    arbre = _produit(morceaux)
    return Neg(arbre) if t.coef < 0 else arbre


def _somme_decalee(g, d, x):
    """(s, o, inverse, R, termes, constantes, a_des_constantes, plus_petit) d'une équation « somme de termes de même base dont les exposants diffèrent
    d'un entier = constante » : `termes` (des _Terme dont `n` est rempli), `constantes` la somme des termes sans inconnue ; _Hors sinon."""
    if variables(g) and not variables(d):
        s, o, inverse = g, d, False
    elif variables(d) and not variables(g):
        s, o, inverse = d, g, True
    else:
        raise _Hors
    R = _const(o)
    if R is None:
        raise _Hors
    termes, constantes = [], F(0)
    a_des_constantes = False
    for signe, t in _termes_signes(s):
        if variables(t):
            termes.append(_terme_exponentiel(signe, t, x))
        else:
            c = _const(t)
            if c is None:
                raise _Hors
            constantes, a_des_constantes = constantes + signe * c, True
    if len(termes) < 2:
        raise _Hors
    base = termes[0].fac.base
    pentes = [t.fac.exp[1:] for t in termes]
    if any(t.fac.base != base for t in termes) or any(p != pentes[0] for p in pentes):
        raise _Hors
    plus_petit = min(termes, key=lambda t: t.fac.exp[0])
    for t in termes:
        decalage = t.fac.exp[0] - plus_petit.fac.exp[0]
        if decalage.denominator != 1:
            raise _Hors
        t.n = int(decalage)
    return s, o, inverse, R, termes, constantes, a_des_constantes, plus_petit


def _mise_en_evidence_e(enonce, x, methode, equation, inverse, poly, termes_de_la_somme, parenthese, P, plus_petit, reste, chaine, carte):
    """Mise en évidence en base e avec un coefficient irrationnel : e^x + e^(x+1) = 5 ⇔ e^x (1 + e) = 5 ⇔ e^x = 5/(1 + e) ⇔ x = ln(5/(1 + e)).
    Le quotient est positif : la méthode A conclut par la définition du logarithme, la méthode B par le logarithme des deux membres. Sinon
    (quotient négatif ou nul) la carte « Aucune solution ». Exposant du 1er ou du 2e degré."""
    termes = [_Terme(c, None, None) for c in poly.values()]
    for t, n in zip(termes, poly):
        t.n = n
    C_tree = _somme_arbres([_terme_de_la_somme(t, E()) for t in termes])
    if len(poly) != len(termes_de_la_somme):               # 1 + e + e se réduit en 1 + 2e
        chaine.ajouter(equation(Op("*", P, C_tree), reste), "⇔")
    positif = sum(float(c) * math.e ** n for n, c in poly.items()) > 0
    quotient = Op("/", reste, C_tree) if reste.val != 0 else Nb(0)
    chaine.ajouter(equation(P, quotient), "⇔", PROP_ISOLER)
    signe_quotient = (1 if positif else -1) * (1 if reste.val > 0 else -1 if reste.val < 0 else 0)
    if signe_quotient <= 0:
        lignes = [Chaine([Rel(P, ">", Nb(0))], note=PROP_EXPO_POSITIVE),
                  Chaine([Eq(P, Nb(0)) if signe_quotient == 0 else Rel(quotient, "<", Nb(0))], note=PROP_AUCUNE_SOLUTION)]
        return _resultat("mise_en_evidence", x, enonce, [carte(), _carte("Aucune solution", lignes)], [])
    f, f_tree = plus_petit.fac.exp, _expo_arbre(plus_petit.fac)
    logarithme = Log(quotient, E())
    suite = Chaine([Eq(P, quotient)])
    if methode == METHODE_MEME_BASE:
        suite.ajouter(Eq(f_tree, logarithme), "⇔", PROP_DEFINITION_LOG)
        titre = "Définition du logarithme"
    else:
        suite.ajouter(Eq(Log(P, E()), logarithme), "⇔", PROP_LN_DEUX_MEMBRES)
        suite.ajouter(Eq(Op("*", f_tree, Log(E(), E())), logarithme), "⇔", PROP_LN_PUISSANCE)
        suite.ajouter(Eq(f_tree, logarithme), "⇔", PROP_CAR_LN_E)
        titre = "Logarithme des deux membres"
    fin, solutions, remarque = _suite_polynome(suite, f, f_tree, logarithme, x)
    r = _resultat("mise_en_evidence", x, enonce, [carte(), _carte(titre, [suite] + fin)], solutions, remarque)
    return r


def _mise_en_evidence(g, d, x, methode):
    """Somme de termes de même base dont les exposants diffèrent d'un entier (2^x + 2^(x+1) = 12, 2^(x+2) − 2^x = 12, 2^x + 2^x = 8), avec
    coefficients et constante éventuels : on met en évidence la plus petite puissance (2^(x+1) = 2^x · 2, puis 2^x (1 + 2)). Si le coefficient
    obtenu est une puissance de la base, on le fond (2^x · 2 = 2^(x+1)) ; sinon on isole l'exponentielle comme d'habitude ; un coefficient nul
    donne ℝ ou ∅. La carte « Mise en évidence » est la même dans les deux méthodes. _Hors sinon."""
    s, o, inverse, R, termes, constantes, a_des_constantes, plus_petit = _somme_decalee(g, d, x)
    enonce = Eq(g, d)
    equation = lambda gauche, droite: Eq(droite, gauche) if inverse else Eq(gauche, droite)
    base = termes[0].fac.base
    base_ecrite = plus_petit.fac.base_ecrite
    pas_isole = lambda t: Neg(t.terme) if t.coef < 0 and not isinstance(t.terme, Neg) else t.terme
    somme_seule = _somme_arbres([pas_isole(t) for t in termes])
    reste = _nb_exact(R - constantes)
    P = plus_petit.fac.arbre
    lignes = []
    for t in termes:                                       # 2^(x+1) = 2^x · 2
        if t.n and not any(tex(t.fac.arbre) == tex(l.elements[0]) for l in lignes):
            lignes.append(Chaine([t.fac.arbre, Op("*", P, base_ecrite if t.n == 1 else Pow(base_ecrite, Nb(t.n)))], ["="], [PROP_SOMME_EXPOSANTS]))
    chaine = Chaine([enonce])
    if a_des_constantes:
        chaine.ajouter(equation(somme_seule, reste), "⇔", PROP_ISOLER)
    parenthese = _somme_arbres([_terme_de_la_somme(t, base_ecrite) for t in termes])
    chaine.ajouter(equation(Op("*", P, parenthese), reste), "⇔", PROP_MISE_EN_EVIDENCE)
    carte = lambda: _carte("Mise en évidence", lignes + [chaine])
    if base == "e":                                        # le coefficient est un polynôme en e : 1 + e, 2 + e², e
        poly = {}
        for t in termes:
            poly[t.n] = poly.get(t.n, F(0)) + t.coef
        poly = {n: c for n, c in sorted(poly.items()) if c != 0}
        C = F(0) if not poly else poly[0] if set(poly) == {0} else None
        if C is None:
            return _mise_en_evidence_e(enonce, x, methode, equation, inverse, poly, termes, parenthese, P, plus_petit, reste, chaine, carte)
    else:
        C = sum((t.coef * base ** t.n for t in termes), F(0))
    if C == 0:                                             # 2^x (1 - 1) = 8 : 0 = 8
        chaine.ajouter(equation(Op("*", P, Nb(0)), reste), "⇔")
        chaine.ajouter(equation(Nb(0), reste), "⇔")
        vrai = R - constantes == 0
        return _resultat("mise_en_evidence", x, enonce, [carte()], None if vrai else [],
                         "Cette égalité est vraie pour tout nombre réel." if vrai else "Cette égalité est fausse : l'équation n'a aucune solution.")
    k = None if base == "e" or C <= 1 else _exposant_entier(C, F(base))
    if k is not None and k >= 1:                           # 2^x · 2 = 2^(x+1)
        chaine.ajouter(equation(Op("*", P, _nb_exact(C)), reste), "⇔")
        if k >= 2:                                         # 2^x · 4 = 2^x · 2^2
            chaine.ajouter(equation(Op("*", P, Pow(base_ecrite, Nb(k))), reste), "⇔")
        expo = list(plus_petit.fac.exp)
        expo[0] += k
        nouveau = Pow(base_ecrite, _arbre_poly(expo, x))
        chaine.ajouter(equation(nouveau, reste), "⇔", PROP_PRODUIT)
        g2, d2 = (reste, nouveau) if inverse else (nouveau, reste)
    else:
        nouveau = P if C == 1 else Neg(P) if C == -1 else Op("*", _nb_exact(C), P)
        chaine.ajouter(equation(nouveau, reste), "⇔")
        g2, d2 = (reste, nouveau) if inverse else (nouveau, reste)
    r = dict(_resolution(g2, d2, x, methode))
    etapes = list(r["etapes"])
    if etapes and etapes[0]["titre"] in ("Isoler l'exponentielle", "Isoler les exponentielles") and len(etapes[0]["lignes"]) == 1:
        suite = etapes.pop(0)["lignes"][0]
        for e, lien, prop in zip(suite.elements[1:], suite.liens, suite.props):
            chaine.ajouter(e, lien, prop)
    r["etapes"] = [carte()] + etapes
    r["enonce"] = enonce
    return r


def _analyser_regroupement(g, d, x):
    """([(signe, _Terme)] du membre de gauche, idem du membre de droite) d'une équation dont chaque terme est k · a^P, avec au plus deux bases
    distinctes et au moins trois termes (2^x − 3^(x+1) = 3^x, 2^x + 2^(x+1) = 2^(x+2)), un membre pouvant être 0 ; _Hors sinon (une constante
    additive, 2^x + 3^x = 5, reste hors programme). Dans un même groupe de base, les exposants ont la même partie variable et diffèrent d'un entier."""
    membres = []
    for n in (g, d):
        if not variables(n):
            if _const(n) != 0:
                raise _Hors
            membres.append([])
        else:
            membres.append([(signe, _terme_exponentiel(signe, t, x)) for signe, t in _termes_signes(n)])
    tous = [t for m in membres for _, t in m]
    bases = []
    for t in tous:
        if t.fac.base not in bases:
            bases.append(t.fac.base)
    if len(tous) < 3 or len(bases) > 2:
        raise _Hors
    for base in bases:
        groupe = [t for t in tous if t.fac.base == base]
        if any(t.fac.exp[1:] != groupe[0].fac.exp[1:] for t in groupe):
            raise _Hors
        if any((t.fac.exp[0] - groupe[0].fac.exp[0]).denominator != 1 for t in groupe):
            raise _Hors
        if base == "e" and any(t.fac.exp[0] != groupe[0].fac.exp[0] for t in groupe):
            raise _Hors                                    # le coefficient 1 + e n'est pas rationnel : e^x + e^(x+1) = 2^x
    return membres, bases


def _somme_signee(couples):
    """La somme des termes (signe, _Terme) écrite : 2^x − 3^(x+1) + 3^x."""
    return _somme_arbres([Neg(t.terme) if signe < 0 else t.terme for signe, t in couples])


def _cote_en_evidence(couples):
    """(lignes des exposants décalés, forme mise en évidence, forme réduite k · a^P, coefficient k) d'un membre fait de termes de même base :
    2^(x+1) = 2^x · 2 ; 3^x + 3^(x+1) devient 3^x (1 + 3), puis 4 · 3^x. Un seul terme : rien à faire (forme mise en évidence = forme réduite = lui-même)."""
    termes = []
    for signe, t in couples:
        copie = _Terme(signe * abs(t.coef), t.fac, t.terme)     # signe et coefficient du terme : −3 · 2^x
        termes.append(copie)
    if len(termes) == 1:
        t = termes[0]
        return [], None, None, t.coef
    plus_petit = min(termes, key=lambda t: t.fac.exp[0])
    for t in termes:
        t.n = int(t.fac.exp[0] - plus_petit.fac.exp[0])
    base = plus_petit.fac.base
    base_ecrite = plus_petit.fac.base_ecrite
    P = plus_petit.fac.arbre
    lignes = []
    for t in termes:
        if t.n and not any(tex(t.fac.arbre) == tex(l.elements[0]) for l in lignes):
            lignes.append(Chaine([t.fac.arbre, Op("*", P, base_ecrite if t.n == 1 else Pow(base_ecrite, Nb(t.n)))], ["="], [PROP_SOMME_EXPOSANTS]))
    parenthese = _somme_arbres([_terme_de_la_somme(t, base_ecrite) for t in termes])
    C = sum((t.coef * (base ** t.n if base != "e" else 1) for t in termes), F(0))
    reduit = Nb(0) if C == 0 else P if C == 1 else Neg(P) if C == -1 else Op("*", _nb_exact(C), P) if C > 0 else Neg(Op("*", _nb_exact(-C), P))
    return lignes, Op("*", P, parenthese), reduit, C


def _regrouper_les_bases(g, d, x, methode):
    """Équation dont chaque terme est k · a^P, avec au plus deux bases (2^x − 3^(x+1) = 3^x) : carte « Regrouper les termes de même base »
    (les termes d'une base d'un côté, ceux de l'autre base de l'autre côté), puis la mise en évidence de chaque côté, puis k · a^P = m · b^Q
    comme d'habitude (ou « Aucune solution » si un membre est ≤ 0). _Hors sinon."""
    (gauche, droite), bases = _analyser_regroupement(g, d, x)
    enonce = Eq(g, d)
    premier = (gauche or droite)[0][1].fac.base
    a = premier
    un_seul = len(bases) == 1
    L, R = [], []
    for membre, a_droite in ((gauche, False), (droite, True)):       # à gauche : les termes de gauche, puis ceux qui viennent de la droite
        for signe, t in membre:
            if un_seul or t.fac.base == a:
                L.append((-signe if a_droite else signe, t))
    for membre, a_droite in ((droite, True), (gauche, False)):       # à droite : les termes de droite, puis ceux qui viennent de la gauche
        for signe, t in membre:
            if not un_seul and t.fac.base != a:
                R.append((signe if a_droite else -signe, t))
    g1, d1 = _somme_signee(L), (_somme_signee(R) if R else Nb(0))
    etapes = []
    if tex_element(Eq(g1, d1)) != tex_element(enonce):
        etapes.append(_carte("Regrouper les termes de même base", [Chaine([enonce, Eq(g1, d1)], ["⇔"], [PROP_REGROUPER])]))
    if un_seul:
        r = dict(_resolution(g1, d1, x, methode))
        r["etapes"] = etapes + list(r["etapes"])
        r["enonce"] = enonce
        return r
    lignes_g, fact_g, red_g, Cg = _cote_en_evidence(L)
    lignes_d, fact_d, red_d, Cd = _cote_en_evidence(R)
    g2, d2 = red_g or g1, red_d or d1
    if fact_g is not None or fact_d is not None:
        chaine = Chaine([Eq(g1, d1), Eq(fact_g or g1, fact_d or d1)], ["⇔"], [PROP_MISE_EN_EVIDENCE])
        if tex_element(Eq(g2, d2)) != tex_element(chaine.elements[-1]):
            chaine.ajouter(Eq(g2, d2), "⇔")
        lignes = lignes_g + [l for l in lignes_d if not any(tex(l.elements[0]) == tex(m.elements[0]) for m in lignes_g)]
        etapes.append(_carte("Mise en évidence", lignes + [chaine]))
    if Cg == 0 and Cd == 0:                                          # 0 = 0
        return _resultat("regroupement", x, enonce, etapes, None, "Cette égalité est vraie pour tout nombre réel.")
    r = dict(_resolution(g2, d2, x, methode))
    r["etapes"] = etapes + list(r["etapes"])
    r["enonce"] = enonce
    return r


def _resolution(g, d, x, methode):
    return _essayer(lambda: _un_facteur(g, d, x, methode), lambda: _mise_en_evidence(g, d, x, methode), lambda: _produit_nul(g, d, x, methode),
                    lambda: _apres_isolement(g, d, x, methode), lambda: _regrouper_les_bases(g, d, x, methode))


@_avec_decimaux
def resolution_exponentielle(g, d, x, methode=METHODE_LOGARITHMES):
    """Corrigé de l'équation exponentielle g = d par la méthode demandée (METHODES), ou None si ce n'est pas une équation exponentielle du cours.
    Méthode A : même base, sinon définition du logarithme (10 ou e), sinon un résultat qui porte le « message » (« b n'est pas une puissance de a »)
    et aucune solution."""
    try:
        return _resolution(g, d, x, methode)
    except _Hors:
        return None


def _variantes_sans_preparation(g, d, x):
    rb = resolution_exponentielle(g, d, x, METHODE_LOGARITHMES)
    ra = resolution_exponentielle(g, d, x, METHODE_MEME_BASE) if rb is not None else None
    return None if rb is None or ra is None else {METHODE_MEME_BASE: ra, METHODE_LOGARITHMES: rb}


def variantes_equation(g, d, x, parametres=()):
    """{méthode: résultat} pour une équation exponentielle (les deux résolutions, calculées en une fois), None pour tout le reste.
    Les cartes de préparation d'un problème d'application (base calculée, paramètre simplifié) viennent en tête des deux résolutions."""
    g2, d2, cartes = preparer_application(g, d, x, parametres)
    variantes = _variantes_sans_preparation(g2, d2, x)
    return None if variantes is None else {m: _avec_preparation(r, g, d, cartes) for m, r in variantes.items()}


# =====================================================================
# 10 bis. PROBLÈMES D'APPLICATION : base calculée (1 + 3,75/100 = 1,0375)
# =====================================================================
def _a_un_taux(n):
    """Vrai si l'arbre écrit un taux : un décimal (0,035), un pourcentage (3,75 %) ou une division par 100, 1000… (20/100)."""
    if isinstance(n, Nb):
        return n.dec is not None or n.pct is not None
    if isinstance(n, Op) and n.op == "/" and isinstance(n.b, Nb) and n.b.val in (100, 1000, 10000):
        return True
    if isinstance(n, (Neg, Fn)):
        return _a_un_taux(n.a)
    if isinstance(n, (Op, Pow)):
        return _a_un_taux(n.a) or _a_un_taux(n.b)
    return False


def _base_a_calculer(b):
    """Vrai pour une base constante écrite avec un taux, qui n'est pas déjà un nombre : 1 + 3,75/100, 1 − 20/100, 1 + 0,035, 1 + 3,75 %."""
    if isinstance(b, (Nb, E)) or variables(b) or not _a_un_taux(b):
        return False
    v = _const(b)
    return v is not None and v > 0 and v != 1


def _valeur_de_la_base(v):
    """La valeur exacte d'une base calculée : un décimal quand elle s'arrête (1,0375 ; 0,8), une fraction sinon."""
    global _DECIMAUX
    avant, _DECIMAUX = _DECIMAUX, True
    try:
        return _nb_exact(v)
    finally:
        _DECIMAUX = avant


def _remplacer_les_bases(n, trouvees):
    """n dont chaque base à calculer (puissance d'exposant variable) est remplacée par sa valeur ; `trouvees` : [(base écrite, valeur)]."""
    if isinstance(n, Pow) and variables(n.b) and _base_a_calculer(n.a):
        nouvelle = _valeur_de_la_base(_const(n.a))
        if not any(tex(a) == tex(n.a) for a, _ in trouvees):
            trouvees.append((n.a, nouvelle))
        return Pow(nouvelle, _remplacer_les_bases(n.b, trouvees))
    if isinstance(n, Pow):
        return Pow(_remplacer_les_bases(n.a, trouvees), _remplacer_les_bases(n.b, trouvees))
    if isinstance(n, Op):
        return Op(n.op, _remplacer_les_bases(n.a, trouvees), _remplacer_les_bases(n.b, trouvees))
    if isinstance(n, Neg):
        return Neg(_remplacer_les_bases(n.a, trouvees))
    if isinstance(n, Fn):
        return Fn(n.nom, _remplacer_les_bases(n.a, trouvees))
    if isinstance(n, Log):
        return Log(_remplacer_les_bases(n.a, trouvees), n.base)
    return n


def preparer_application(g, d, x, parametres=()):
    """(g', d', cartes) : l'équation d'un problème d'application ramenée à une équation exponentielle ordinaire, avec les cartes qui le disent.
    Une base écrite avec un taux (1 + 3,75/100, 1 − 20/100, 1 + 0,035, 1 + 3,75 %) devient un nombre, sur une ligne à part (carte « Calculer la
    base », commune aux deux méthodes). Un paramètre (3Q = Q(1 + 3,75/100)^x : Q est facteur de chaque membre) se simplifie ensuite, une carte
    « Simplifier par Q » par paramètre. Sans rien à préparer : (g, d, [])."""
    trouvees = []
    g2, d2 = _remplacer_les_bases(g, trouvees), _remplacer_les_bases(d, trouvees)
    cartes = []
    if trouvees:
        cartes.append(_carte("Calculer la base", [Chaine([ancienne, nouvelle], ["="], [None]) for ancienne, nouvelle in trouvees]))
    for p in parametres:
        g3, d3 = sans_facteur(g2, p), sans_facteur(d2, p)
        if g3 is None or d3 is None:
            raise ValueError(f"{p} n'est pas un facteur de chaque membre")      # analyser_saisie l'a déjà refusé
        cartes.append(_carte(f"Simplifier par {p}", [Chaine([Eq(g2, d2), Eq(g3, d3)], ["⇔"], [Divise(p)])]))
        g2, d2 = g3, d3
    return g2, d2, cartes


def _avec_preparation(r, g, d, cartes):
    """Le résultat `r` (de l'équation préparée) précédé des cartes de préparation ; l'énoncé est celui de la saisie."""
    if r is None or not cartes:
        return r
    r = dict(r)
    r["etapes"] = list(cartes) + list(r["etapes"])
    r["enonce"] = Eq(g, d)
    return r


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


def _milieu_exact(puissance, exact):
    """Les écritures entre a^c et sa valeur : a^c seul, ou pour une puissance rationnelle d'un entier la justification
    8^(2/3) = (2³)^(2/3) = 2² = 4 (a = r^k avec r le plus petit entier possible)."""
    if exact is None:
        return ()
    milieu = [puissance]
    a, c = (_const(puissance.a), _const(puissance.b)) if isinstance(puissance, Pow) else (None, None)
    if a is not None and c is not None and c.denominator != 1 and a.denominator == 1 and a > 1:
        r = _racine_primitive(a)
        k = _exposant_entier(a, r)
        if r != a and k is not None:
            milieu.append(Pow(Pow(Nb(r), Nb(k)), puissance.b))
            if k * c != 1:
                milieu.append(Pow(Nb(r), Nb(k * c)))
    return milieu


def _par_exponentielle(chaine, courant, base, puissance, resultat, milieu=()):
    """log_a(u) = c ⇔ a^(log_a(u)) = a^c (exponentielle des deux membres) ⇔ u = a^c (a^(log_a(A)) = A, A > 0) : deux lignes par logarithme.
    `courant` : le logarithme, `base` : sa base (nœud), `puissance` : a^c, `resultat` : la valeur de u, `milieu` : les écritures intermédiaires."""
    prop = PROP_EXP_LN if isinstance(base, E) else PROP_EXP_LOG if base == Nb(10) else PROP_EXP_LOG_BASE
    chaine.ajouter(Eq(Pow(base, courant), puissance), "⇔", PROP_EXPONENTIELLE)
    chaine.ajouter(Eq(courant.a, resultat, milieu), "⇔", prop)


@_avec_decimaux
def logarithmique(g, d, x):
    """Corrigé de log_a(u) = c par la définition du logarithme (u polynôme de degré ≤ 2 en x, ou logarithmes imbriqués, ou base inconnue
    log_x(n) = k), après avoir isolé le logarithme. None si la méthode ne s'applique pas."""
    try:
        return _logarithmique(g, d, x)
    except _Hors:
        return None


@_avec_decimaux
def logarithmique_m(g, d, x):
    """`logarithmique` pour la filière M : l'ensemble de définition est une carte à part (exp_log_m.py), donc ni carte « Condition » ni carte
    « Vérification » ici, et la base inconnue garde ses deux candidats (x = −4 ou x = 4) que la vérification départage."""
    try:
        return _logarithmique(g, d, x, filiere_m=True)
    except _Hors:
        return None


def _logarithmique(g, d, x, filiere_m=False):
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
        return _base_inconnue(enonce, etapes, chaine, s, c, x, filiere_m)
    rhs, courant, profondeur = _nb_exact(c), s, 0
    while True:                                   # on épluche les logarithmes de l'extérieur vers l'intérieur
        base, _ = _base_du_logarithme(courant.base)
        puissance = base if isinstance(base, E) and rhs == Nb(1) else Pow(base, rhs)          # e^1 s'écrit e
        profondeur += 1
        if not isinstance(courant.a, Log):
            break
        exact = _valeur_exacte(puissance)
        _par_exponentielle(chaine, courant, base, puissance, exact or puissance, _milieu_exact(puissance, exact))
        rhs, courant = exact or puissance, courant.a
    u = courant.a
    if not variables(u) or not _est_polynome(u):
        raise _Hors
    lignes, remarque = [chaine], None
    if isinstance(u, Var):
        exact = _valeur_exacte(puissance)
        _par_exponentielle(chaine, courant, base, puissance, exact or puissance, _milieu_exact(puissance, exact))
        solutions = [exact or puissance]
    else:
        f = _poly(u, x)
        if len(f) == 2:
            _par_exponentielle(chaine, courant, base, puissance, puissance)
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
            try:
                if v is None:
                    raise _Hors
                l_poly, solutions, remarque = _resoudre_polynome(f, [v], u, _nb_exact(v), x)
            except _Hors:
                l_poly = None
            if l_poly is not None:                            # coefficients entiers : la résolution de la méthode « même base »
                _par_exponentielle(chaine, courant, base, puissance, _nb_exact(v), [puissance])
                if solutions is None:
                    raise _Hors
                premiere = l_poly[0]
                for e, lien, prop in zip(premiere.elements[1:], premiere.liens, premiere.props):
                    chaine.ajouter(e, lien, prop)
                lignes += l_poly[1:]
            elif f == [0, 0, 1]:                              # log(x²) = c : x² = 10^c ⇔ x = ±√(10^c), jamais 2 log(x)
                exact = _valeur_exacte(puissance)
                _par_exponentielle(chaine, courant, base, puissance, exact or puissance, _milieu_exact(puissance, exact))
                suite, solutions, remarque = _suite_polynome(chaine, f, u, exact or puissance, x)
                lignes += suite
            else:
                raise _Hors                                   # trinôme général à coefficients non entiers : plus tard
    etapes.append(_carte("Exponentielle des deux membres", lignes))
    if profondeur == 1 and not isinstance(u, Var) and solutions and not filiere_m:
        etapes.append(_carte("Vérification", [Chaine([Positif(u, puissance)], note=PROP_BIEN_DEFINI)]))
    return {"genre": "logarithmique", "inconnue": x, "enonce": enonce, "base": None, "etapes": etapes, "solutions": solutions,
            "remarque": remarque}


def _base_inconnue(enonce, etapes, chaine, s, c, x, filiere_m=False):
    """log_x(n) = k avec k entier de −12 à 12 : x > 0 et x ≠ 1, n = xᵏ, puis la solution positive : r si n = rᵏ (256 = 4⁴), sinon la racine
    k-ième de n écrite comme telle (√255, 255^(1/3)). k < 0 : n = x⁻ᵐ = 1/xᵐ, donc xᵐ = 1/n (log_x(8) = −1 donne x = 1/8) ; k = 0 : n = x⁰ = 1,
    vraie pour toute base si n = 1, aucune solution sinon ; n = 1 et k ≠ 0 : xᵏ = 1 ne donne que x = 1 ou x = −1, qui ne conviennent pas."""
    n = _const(s.a)
    if variables(s.a) or n is None:
        raise _Hors
    X = Var(s.base.nom)
    condition = Chaine([Texte(f"{X.nom} > 0 \\text{{ et }} {X.nom} \\neq 1")], note=PROP_BASE_LOG)
    if n <= 0:                                                         # une puissance d'une base admissible est > 0 : n = xᵏ est impossible
        puissance = Pow(X, Nb(c)) if c != 1 else X
        chaine.ajouter(Eq(puissance, _nb_exact(n)), "⇔", PROP_DEFINITION_LOG)
        impossible = Eq(puissance, Nb(0)) if n == 0 else Rel(_nb_exact(n), "<", Nb(0))
        return {"genre": "logarithmique", "inconnue": x, "enonce": enonce, "base": None, "solutions": [], "remarque": None,
                "etapes": etapes + ([] if filiere_m else [_carte("Condition", [condition])]) + [_carte("Définition du logarithme", [chaine]),
                                    _carte("Aucune solution", [Chaine([Rel(puissance, ">", Nb(0))], note=PROP_BASE_PUISSANCE_POSITIVE),
                                                               Chaine([impossible], note=PROP_AUCUNE_SOLUTION)])]}
    if c.denominator != 1 or abs(c) > 12:
        raise _Hors
    k = int(c)
    chaine.ajouter(Eq(Pow(X, s), Pow(X, Nb(k))), "⇔", PROP_EXPONENTIELLE)            # x^(log_x(n)) = x^k
    chaine.ajouter(Eq(_nb_exact(n), Pow(X, Nb(k)) if k != 1 else X), "⇔", PROP_EXP_LOG_BASE)
    lignes, autres = [chaine], {}
    resultat = lambda solutions, remarque=None: {"genre": "logarithmique", "inconnue": x, "enonce": enonce, "base": None,
                                                 "etapes": etapes + ([] if filiere_m else [_carte("Condition", [condition])]) + [_carte("Exponentielle des deux membres", lignes)],
                                                 "solutions": solutions, "remarque": remarque, **autres}
    if k == 0:                                                         # n = x⁰ = 1
        chaine.ajouter(Eq(_nb_exact(n), Nb(1)), "⇔", PROP_PUISSANCE_ZERO)
        if n != 1:
            return resultat([], "Cette égalité est fausse : l'équation n'a aucune solution.")
        autres["ensemble"] = r"\left]0 \,;\, 1\right[ \cup \left]1 \,;\, +\infty\right["
        return resultat(None, f"Cette égalité est vraie pour toute base {X.nom} > 0 et différente de 1.")
    m = abs(k)
    if k < 0:                                                          # n = x⁻ᵐ = 1/xᵐ ⇔ xᵐ = 1/n
        chaine.ajouter(Eq(_nb_exact(n), Op("/", Nb(1), Pow(X, Nb(m)) if m > 1 else X)), "⇔", PROP_PUISSANCE_NEGATIVE)
        chaine.ajouter(Eq(Pow(X, Nb(m)) if m > 1 else X, _nb_exact(1 / n)), "⇔")
        n = 1 / n
    if n == 1:                                                         # xᵐ = 1 : x = 1 (ou x = −1), exclus par la condition
        if m % 2 == 0:
            chaine.ajouter(Ou([Eq(X, Nb(-1)), Eq(X, Nb(1))]), "⇔")
            if not filiere_m:
                lignes.append(Chaine([Texte(f"{X.nom} = 1 \\text{{ et }} {X.nom} = -1 \\text{{ ne conviennent pas}}")], note=PROP_BASE_LOG))
        else:
            if m > 1:
                chaine.ajouter(Eq(X, Nb(1)), "⇔")
            if not filiere_m:
                lignes.append(Chaine([Texte(f"{X.nom} = 1 \\text{{ ne convient pas}}")], note=PROP_BASE_LOG))
        return resultat(([Nb(-1), Nb(1)] if m % 2 == 0 else [Nb(1)]) if filiere_m else [])
    r = _racine_entiere(n, m)
    if r is not None:
        racine = _nb_exact(r)
    else:
        racine = Fn("sqrt", _nb_exact(n)) if m == 2 else Pow(_nb_exact(n), Nb(F(1, m)))
    if m % 2 == 0:
        negatif = Neg(racine) if r is None else _nb_exact(-r)
        chaine.ajouter(Ou([Eq(X, negatif), Eq(X, racine)]), "⇔")
        if not filiere_m:
            lignes.append(Chaine([Eq(X, racine)], note=PROP_SEULE_POSITIVE))
        return resultat([negatif, racine] if filiere_m else [racine])
    elif m > 1 or k < 0:
        if tex_element(Eq(X, racine)) != tex_element(chaine.elements[-1]):
            chaine.ajouter(Eq(X, racine), "⇔")
    return resultat([racine])


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
NOMS_FACTEURS = ("Facteur 1", "Facteur 2", "Facteur 3", "Facteur 4")


def _produit_nul(g, d, x, methode):
    """P1 · P2 · … = 0 quand chaque facteur = 0 se résout par la méthode (10^x(10^x − 4) = 0). Avec la méthode A, le premier facteur qui demande
    les logarithmes porte le message et la résolution s'arrête là."""
    if isinstance(d, Nb) and d.val == 0 and isinstance(g, Op) and g.op == "*":
        produit = g
    elif isinstance(g, Nb) and g.val == 0 and isinstance(d, Op) and d.op == "*":
        produit = d
    else:
        raise _Hors
    facteurs = [f for f in _aplatir(produit) if variables(f)]
    if any(_signe(f) == 0 for f in _aplatir(produit) if not variables(f)):
        raise _Hors                                        # un facteur constant nul : l'égalité est vraie pour tout x
    if not 2 <= len(facteurs) <= len(NOMS_FACTEURS) or not any(_classe(f) == "exp" for f in facteurs):
        raise _Hors
    etapes = [_carte("Produit nul", [Chaine([Eq(g, d), Ou(Eq(f, Nb(0)) for f in facteurs)], ["⇔"], [PROP_PRODUIT_NUL])])]
    solutions = []
    for nom, f in zip(NOMS_FACTEURS, facteurs):
        if _classe(f) == "poly":                           # x · 2^x = 0 : le facteur x = 0 se résout comme une équation du 1er ou du 2e degré
            lignes, sols, remarque = _resoudre_polynome(_poly(f, x), [F(0)], f, Nb(0), x)
            if sols is None:
                raise _Hors
            etapes.append(_carte(nom, lignes + ([Message(remarque)] if remarque else [])))
            solutions += [n for n in sols if all(abs(valeur(n) - valeur(m)) > 1e-12 for m in solutions)]
            continue
        r = _essayer(lambda: _un_facteur(f, Nb(0), x, methode), lambda: _apres_isolement(f, Nb(0), x, methode))
        etapes.append(_carte(nom, [l for c in r["etapes"] for l in c["lignes"]]))
        if r.get("message"):
            return _resultat("produit_nul", x, Eq(g, d), etapes, [], None, message=r["message"])
        if r["solutions"] is None:
            raise _Hors
        for n in r["solutions"]:
            if all(abs(valeur(n) - valeur(m)) > 1e-12 for m in solutions):
                solutions.append(n)
    solutions.sort(key=valeur)
    return _resultat("produit_nul", x, Eq(g, d), etapes, solutions)


def _contient_log(n):
    if isinstance(n, Defini):
        return _contient_log(n.arbre)
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


def _precis(n):
    """Valeur d'un arbre sans inconnue avec 60 chiffres (module decimal) ; le contexte est celui de l'appelant."""
    D = decimal.Decimal
    if isinstance(n, Defini):
        return _precis(n.arbre)
    if isinstance(n, Nb):
        return D(n.val.numerator) / D(n.val.denominator)
    if isinstance(n, E):
        return D(1).exp()
    if isinstance(n, Neg):
        return -_precis(n.a)
    if isinstance(n, Op):
        a, b = _precis(n.a), _precis(n.b)
        return a + b if n.op == "+" else a - b if n.op == "-" else a * b if n.op == "*" else a / b
    if isinstance(n, Pow):
        return _precis(n.a) ** _precis(n.b)
    if isinstance(n, Fn):
        return _precis(n.a).sqrt()
    if isinstance(n, Log):
        v = _precis(n.a).ln()
        return v / (D(10).ln() if n.base is None else _precis(n.base).ln())
    raise TypeError(n)


def _valeur_rationnelle(n):
    """La valeur (Fraction) d'un arbre sans inconnue quand elle est rationnelle, sinon None. Une valeur écrite avec des logarithmes (log(8)/log(2))
    est reconnue avec 60 chiffres : un rationnel de dénominateur ≤ 10⁶ à 10⁻⁴⁰ près."""
    v = _const(n)
    if v is not None:
        return v
    try:
        with decimal.localcontext() as c:
            c.prec = 60
            p = _precis(n)
            f = F(p).limit_denominator(10 ** 6)
            ecart = abs(p - decimal.Decimal(f.numerator) / decimal.Decimal(f.denominator))
            return f if ecart < decimal.Decimal("1e-40") else None
    except (ArithmeticError, ValueError, decimal.DecimalException):
        return None


def _signe(n):
    """Signe (−1, 0 ou 1) d'un arbre sans inconnue : exact pour un rationnel, même écrit avec des logarithmes (Δ = (2 log 2)² − 4 log 2 · log 2 = 0),
    sinon celui de sa valeur à 60 chiffres."""
    q = _valeur_rationnelle(n)
    if q is not None:
        return (q > 0) - (q < 0)
    with decimal.localcontext() as c:
        c.prec = 60
        v = _precis(n)
    return (v > 0) - (v < 0)


def _morceaux_rationnels(n):
    """Les plus petits morceaux de l'arbre qui contiennent un logarithme et valent un rationnel (log(32)/log(2) dans 1 + log(32)/log(2))."""
    if not _contient_log(n):
        return []
    enfants = {Neg: lambda n: [n.a], Fn: lambda n: [n.a], Op: lambda n: [n.a, n.b], Pow: lambda n: [n.a, n.b]}.get(type(n), lambda n: [])(n)
    dessous = [m for e in enfants for m in _morceaux_rationnels(e)]
    if dessous:
        return dessous
    return [n] if _valeur_rationnelle(n) is not None else []


def controle_calculatrice(r):
    """La phrase « Contrôlez à la calculatrice : log(32)/log(2) = 5, on retrouve x = 6. » (HTML, TeX entre \\( et \\)) quand une solution est un rationnel
    écrit avec des logarithmes (règle R15) ; None sinon. La valeur est reconnue exactement (60 chiffres), jamais par un arrondi d'affichage."""
    sols = r["solutions"]
    if not sols or any(_valeur_rationnelle(n) is None for n in sols) or all(_const(n) is not None for n in sols):
        return None
    val = lambda n: tex(Nb(_valeur_rationnelle(n)))
    ecrire = lambda t: r"\(" + _echapper(t, quote=False) + r"\)"
    x = r["inconnue"]
    if len(sols) == 1:
        n = sols[0]
        morceaux = _morceaux_rationnels(n)
        if morceaux == [n]:
            return "Contrôlez à la calculatrice : " + ecrire(f"{x} = {tex(n)} = {val(n)}") + "."
        if not morceaux:
            return None                                    # jamais « Contrôlez à la calculatrice : , on retrouve… » sans rien à contrôler
        citations = " ; ".join(ecrire(f"{tex(m)} = {val(m)}") for m in morceaux)
        return f"Contrôlez à la calculatrice : {citations}, on retrouve " + ecrire(f"{x} = {val(n)}") + "."
    return "Contrôlez à la calculatrice : on retrouve " + " ou ".join(ecrire(f"{x} = {val(n)}") for n in sols) + "."


def tex_solution(r):
    """Ligne finale du corrigé : l'ensemble solution (valeur exacte), puis « soit x ≈ … » (3 décimales) quand une solution n'est pas un
    rationnel. Elle existe même quand aucune carte de méthode ne précède (x = ln 3 : S = {ln(3)}, soit x ≈ 1,099)."""
    sols = r["solutions"]
    if sols is None:
        return "S = " + r.get("ensemble", r"\mathbb{R}")
    if not sols:
        return r"S = \varnothing"
    s = r"S = \left\{" + r" \,;\, ".join(tex(n) for n in sols) + r"\right\}"
    rationnel = lambda n: _const(n) is not None
    certifie = {id(n): _valeur_rationnelle(n) for n in sols}              # rationnel écrit avec des logarithmes : voir controle_calculatrice
    if all(certifie[id(n)] is not None for n in sols):
        return s
    x = r["inconnue"]
    parts = [x + (" = " + tex(n) if rationnel(n) else r" \approx " + tex_approx(valeur(n))) for n in sols]
    return s + r" \text{, soit } " + r" \text{ ou } ".join(parts)


# =====================================================================
# 11 bis. INTERPRÉTATION D'UNE DURÉE : années, mois et jours (R16)
# =====================================================================
MOIS_PAR_AN, JOURS_PAR_MOIS = 12, 30
CONVENTIONS_DUREE = "Conventions : 1 an = 12 mois et 1 mois = 30 jours."
LIBELLE_INTERPRETATION = "Problème d'application (temps en années)"


def suggere_interpretation(saisie):
    """Vrai quand la case « Problème d'application » est cochée au départ : un paramètre (3Q = Q(1 + 3,75/100)^x) ou l'inconnue n (le temps de
    2000 · 1,045^n = 3805). Pas pour t : le temps peut être en minutes."""
    return saisie.genre == "equation" and (bool(saisie.parametres) or saisie.inconnue == "n")


def interpretation_possible(r):
    """Vrai si l'interprétation a un sens : une équation exponentielle résolue (pas une équation logarithmique, un premier degré ni un calcul),
    avec au plus une solution (S = ∅ compris)."""
    return (r is not None and r.get("genre") not in ("logarithmique", "lineaire", "calcul", "changement") and not r.get("message")
            and r["solutions"] is not None and len(r["solutions"]) <= 1 and r.get("ensemble") is None)


def _trois_decimales(q):
    """(texte TeX, exact) de q ≥ 0 à 3 décimales (arrondi au plus proche) ; exact quand la valeur s'écrit ainsi sans reste (sans zéros inutiles)."""
    n = (F(q) * 1000 + F(1, 2)).__floor__()
    exact = F(q) * 1000 == n
    if exact and F(q).denominator == 1:
        return formater_entier(int(q), tex=True), True
    chiffres = f"{n // 1000}.{n % 1000:03d}"
    return formater_decimal(chiffres.rstrip("0").rstrip(".") if exact else chiffres, tex=True), exact


def _unite(n, singulier, pluriel):
    """« 0 an », « 1 an », « 2 ans » : le pluriel dès 2."""
    return f"{n} {singulier if n < 2 else pluriel}"


def _egal(exact):
    return "=" if exact else r"\approx"


def interpretation(r):
    """L'interprétation de la solution en années, mois et jours (règle R16) : {cas, carte, conclusion, duree}, ou None si elle n'a pas de sens
    (interpretation_possible). 1 an = 12 mois, 1 mois = 30 jours ; les jours sont arrondis à l'entier supérieur (« au bout de ») ; les restes sont
    calculés à pleine précision (60 chiffres, ou exactement pour un rationnel), jamais à partir des valeurs arrondies affichées, et affichés à
    3 décimales ; 30 jours se reportent sur le mois, 12 mois sur l'année. `duree` : (années, mois, jours) ou None. `carte` : « Interprétation »,
    des Message ; `conclusion` : la phrase de la fin, écrite à part."""
    if not interpretation_possible(r):
        return None
    sols = r["solutions"]
    if not sols:
        return {"cas": "vide", "carte": _carte("Interprétation", []), "duree": None,
                "conclusion": "Aucune solution : la situation décrite n'arrive jamais."}
    n = sols[0]
    rationnel = _valeur_rationnelle(n)
    if rationnel is not None:
        x = rationnel
    else:
        with decimal.localcontext() as c:
            c.prec = 60
            x = F(_precis(n))
    if x < 0:
        return {"cas": "negative", "carte": _carte("Interprétation", []), "duree": None,
                "conclusion": "La solution est négative : la situation décrite n'arrive jamais."}
    if x == 0:
        return {"cas": "nulle", "carte": _carte("Interprétation", []), "duree": None,
                "conclusion": "La situation est atteinte dès le départ."}
    annees = x.__floor__()
    reste_an = x - annees
    mois_exacts = reste_an * MOIS_PAR_AN
    mois = mois_exacts.__floor__()
    reste_mois = mois_exacts - mois
    jours_exacts = reste_mois * JOURS_PAR_MOIS
    jours = -((-jours_exacts).__floor__())                                  # arrondi au jour supérieur
    nom = r["inconnue"]
    t = lambda q: _trois_decimales(q)
    (tx, ex), (tr1, e1), (tm, em), (tr2, e2), (tj, ej) = t(x), t(reste_an), t(mois_exacts), t(reste_mois), t(jours_exacts)
    lignes = [Message(CONVENTIONS_DUREE),
              Message(Texte(f"{_nom_tex(nom)} {_egal(ex)} {tx}"), f" : {_unite(annees, 'an', 'ans')} ; reste ", Texte(tr1), " an."),
              Message(Texte(rf"{tr1} \cdot {MOIS_PAR_AN} {_egal(em)} {tm}"), f" mois → {mois} mois ; reste ", Texte(tr2), " mois."),
              Message(Texte(rf"{tr2} \cdot {JOURS_PAR_MOIS} {_egal(ej)} {tj}"), f" {'jour' if jours_exacts < 2 else 'jours'} → {_unite(jours, 'jour', 'jours')}.")]
    if jours_exacts != jours_exacts.__floor__():
        lignes.append(Message(f"Au bout de {_unite(jours_exacts.__floor__(), 'jour', 'jours')}, la durée cherchée n'est pas encore écoulée : "
                              "on arrondit au jour supérieur."))
    if jours == JOURS_PAR_MOIS:
        jours, mois = 0, mois + 1
        lignes.append(Message(f"{JOURS_PAR_MOIS} jours font 1 mois : on ajoute 1 mois."))
    if mois == MOIS_PAR_AN:
        mois, annees = 0, annees + 1
        lignes.append(Message(f"{MOIS_PAR_AN} mois font 1 an : on ajoute 1 an."))
    conclusion = f"Au bout de {_unite(annees, 'an', 'ans')}, {_unite(mois, 'mois', 'mois')} et {_unite(jours, 'jour', 'jours')}."
    return {"cas": "positive", "carte": _carte("Interprétation", lignes), "duree": (annees, mois, jours), "conclusion": conclusion}


def corriger_equation(g, d, x, methode=METHODE_LOGARITHMES, parametres=()):
    """Corrigé de g = d : pour une équation exponentielle, la résolution de la méthode demandée (METHODES, B « logarithmes » par défaut) ;
    sinon la première méthode du cours qui s'applique (équation logarithmique, premier degré). None si l'équation ne se résout pas avec ces méthodes."""
    g2, d2, cartes = preparer_application(g, d, x, parametres)
    variantes = _variantes_sans_preparation(g2, d2, x)
    if variantes is not None:
        return _avec_preparation(variantes[methode], g, d, cartes)
    seule = resolution_exponentielle(g2, d2, x, METHODE_MEME_BASE)
    if seule is not None and not seule.get("message"):
        return _avec_preparation(seule, g, d, cartes)  # 4^x = 2^(2x) : la méthode B diviserait par log(4) − 2 log(2) = 0, la méthode A seule
    for essai in (logarithmique, lineaire_logarithmes):
        r = essai(g2, d2, x)
        if r is not None:
            return _avec_preparation(r, g, d, cartes)
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
        if "log" in classes and ("poly" in classes or "exp" in classes):        # x · log(x), log(x) · 2^x
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
    """Vrai pour une équation dont le type n'est pas dans le cours : x · 2^x = 8, 2^x + 3^x = 5, x^x = 4, 2^x = x + 1, log(x) = x − 1, x · log(x) = 1,
    e^x = ln(x), et pour les 3C deux exponentielles avec un troisième terme, quelle que soit la base (mise en facteur 2^x + 2^(x+1) = 12,
    2e degré en 2^x : 4^x − 2^x − 6 = 0, e^(2x) − 3e^x + 2 = 0)."""
    try:
        _somme_decalee(g, d, x)                            # 2^x + 2^(x+1) = 12 : dans le programme (mise en évidence)
        return False
    except _Hors:
        pass
    try:
        _analyser_regroupement(g, d, x)                    # 2^x − 3^(x+1) = 3^x : dans le programme (on regroupe les termes de même base)
        return False
    except _Hors:
        pass
    try:                                                   # 2^x − 3^(x+1) = 0 se ramène à 2^x = 3^(x+1)
        g2, d2, _ = _isoler_exponentielles(g, d, x)
        return hors_programme(g2, d2, x)
    except _Hors:
        pass
    for p, z in ((g, d), (d, g)):                          # produit nul : chaque facteur
        if _const(z) == 0 and isinstance(p, Op) and p.op == "*" and not variables(z):
            facteurs = [f for f in _aplatir(p) if variables(f)]
            if len(facteurs) > 1:
                return any(hors_programme(f, Nb(0), x) for f in facteurs)
    egal_zero = lambda a, b: isinstance(b, Nb) and b.val == 0 and isinstance(a, Op) and a.op == "*"
    if _hors_arbre(g, egal_zero(g, d)) or _hors_arbre(d, egal_zero(d, g)):
        return True
    termes = [t for t in _termes_additifs(g) + _termes_additifs(d) if _const(t) != 0]
    if len(termes) >= 3 and sum(1 for t in termes if _classe(t) == "exp") >= 2:
        return True                                        # 2^x + 2^(x+1) = 12 (mise en facteur), 4^x − 2^x − 6 = 0 (2e degré en 2^x) : pas en 3C
    classes = {_classe(t) for t in termes}
    # une exponentielle et un terme en x, ou un logarithme et un terme en x ou une exponentielle, de part et d'autre (2^x = x + 1, log(x) = x − 1, e^x = ln(x))
    return ("exp" in classes and "poly" in classes) or ("log" in classes and ("poly" in classes or "exp" in classes))


def _contient_exponentielle(n):
    """Vrai si l'arbre contient une puissance dont l'exposant contient l'inconnue (2^x, e^(x+1), x^x)."""
    if isinstance(n, Defini):
        return _contient_exponentielle(n.arbre)
    if isinstance(n, (Neg, Fn, Log)):
        return _contient_exponentielle(n.a)
    if isinstance(n, Pow):
        return bool(variables(n.b)) or _contient_exponentielle(n.a) or _contient_exponentielle(n.b)
    if isinstance(n, Op):
        return _contient_exponentielle(n.a) or _contient_exponentielle(n.b)
    return False


def message_non_resolu(g, d, x):
    """Le message à afficher quand `corriger_equation` ne trouve aucune méthode : « traite les équations exponentielles et logarithmiques »
    quand il n'y a ni exponentielle ni logarithme (x² = 4), « ne se résout pas avec les méthodes du cours » pour un vrai hors-programme,
    « ne traite pas encore » pour une forme du programme que l'outil ne gère pas encore."""
    if not any(_contient_exponentielle(n) or _contient_log(n) for n in (g, d)):
        return MESSAGE_SANS_EXP_LOG                        # x² = 4, 2x + 1 = 9 : ni exponentielle ni logarithme
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


TAUX_CAPITAL = [0.5, 1, 1.5, 2, 2.25, 2.5, 3, 3.5, 3.75, 4, 4.5, 5, 6, 7, 8]          # capitalisation : de 0,5 % à 8 %
TAUX_DEPRECIATION = [5, 6, 8, 10, 12, 12.5, 15, 18, 20, 25]                          # dépréciation : de 5 % à 25 %
PARAMETRES = ["C", "Q", "C0", "V0", "C_0", "V_0"]


def _virgule(v):
    """5 → « 5 », 3.75 → « 3,75 »."""
    return f"{v:g}".replace(".", ",")


def _base_application(rng, t, signe):
    """La base 1 ± t/100 écrite d'une des quatre façons de l'énoncé : (1+3,75/100), (1+3,75%), (1+0,0375), ou le décimal 1,0375 déjà calculé."""
    d = decimal.Decimal(str(t)) / 100
    produit = decimal.Decimal(1) + signe * d
    ecriture = rng.choice(["fraction", "pourcent", "decimal", "calculee"])
    if ecriture == "fraction":
        return f"(1{'+' if signe > 0 else '-'}{_virgule(t)}/100)"
    if ecriture == "pourcent":
        return f"(1{'+' if signe > 0 else '-'}{_virgule(t)}%)"
    if ecriture == "decimal":
        return f"(1{'+' if signe > 0 else '-'}{format(d.normalize(), 'f').replace('.', ',')})"
    return format(produit.normalize(), "f").replace(".", ",")


def _gabarit_application(rng):
    """Capitalisation et dépréciation, inconnue n : f·C = C·(1 + t/100)^n (f = 2 ou 3), C/2 ou C/4 = C·(1 − t/100)^n, ou sans paramètre
    A·(1 + t/100)^n = B (A = 1000 à 5000, B = 1,2 à 3 fois A)."""
    forme = rng.choice(["croissance", "croissance", "depreciation", "depreciation", "sans_parametre"])
    p = rng.choice(PARAMETRES)
    if forme == "sans_parametre":
        a = rng.choice([1000, 1500, 2000, 5000])
        b = round(a * rng.choice([1.2, 1.4, 1.5, 1.6, 1.8, 2, 2.5, 3]))
        return f"{a}*{_base_application(rng, rng.choice(TAUX_CAPITAL), 1)}^n={b}"
    if forme == "croissance":
        facteur = rng.choice([2, 3])
        membre = f"{p}*{_base_application(rng, rng.choice(TAUX_CAPITAL), 1)}^n"
        autre = f"{facteur}{p}"
    else:
        membre = f"{p}*{_base_application(rng, rng.choice(TAUX_DEPRECIATION), -1)}^n"
        autre = f"{p}/{rng.choice([2, 4])}"
    return f"{autre}={membre}" if rng.random() < 0.7 else f"{membre}={autre}"


def _gabarit_logarithme(rng):
    tirage = rng.random()
    if tirage < 0.10:                                             # second membre négatif : S = ∅
        return f"{rng.choice([2, 3, 5, 7])}^({_lineaire_texte(rng.randint(1, 8), 0)})=-{rng.randint(3, 60)}"
    if tirage < 0.40:                                             # problème d'application (30 %)
        return _gabarit_application(rng)
    if tirage < 0.55:                                             # k * e^(cx) = b
        k = rng.choice([2, 3, 5, 10, 20, 37, 50])
        c = rng.choice(["0,02", "0,05", "0,1", "0,5", "-0,02", "-0,05", "-0,1", "-0,5"])
        b = rng.choice([v for v in range(3, 100) if v != k])
        return f"{k}*e^({c}x)={b}"
    a = rng.choice([2, 3, 4, 5, 6, 7])
    b = rng.choice([v for v in range(5, 100) if not _puissance_de_la_racine(v, a)])
    p, q = rng.randint(1, 3), rng.randint(-3, 3)
    if tirage < 0.75:                                             # a^(px+q) = b
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


def exercice(niveau, graine, filiere="C"):
    """Exercice du niveau (facile, moyen, logarithme, difficile), déterministe : la même graine donne le même énoncé. Aucun exposant de
    degré 3 ou plus ; quand x² est en exposant, les racines sont entières. Renvoie {ok, expr, niveau}. `filiere` : "C" (ce pool) ou "M"
    (le pool M, niveaux NIVEAUX_M de exp_log_m.py)."""
    if filiere not in FILIERES:
        return {"ok": False, "erreur": MESSAGE_FILIERE}
    if filiere == "M":
        import exp_log_m                                  # chargé seulement pour la filière M (exp_log_m importe ce fichier)
        return exp_log_m.exercice_m(niveau, graine)
    if niveau not in _GABARITS:
        return {"ok": False, "erreur": "Niveau d'exercice inconnu."}
    return {"ok": True, "expr": _GABARITS[niveau](random.Random(f"{niveau}:{graine}")), "niveau": niveau}


def exercice_json(niveau, filiere="C"):
    """Appelé par la page : un exercice du niveau demandé, graine tirée au hasard."""
    return json_strict(exercice(niveau, random.randrange(2 ** 31), filiere))
