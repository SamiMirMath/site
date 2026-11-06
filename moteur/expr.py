"""
expr.py — Brique commune « expressions » : l'arbre d'expressions, son TeX et sa lecture (tokeniseur et analyseur syntaxique).

Tirée de l'outil Exponentielles et logarithmes (chantier briques-communes, B1 ; revue de structure, R5), qui la réexporte sous les mêmes
noms (`exp_log.Nb is expr.Nb`, etc.) : la sortie de l'outil est identique à l'octet. Python pur, sans SymPy.

Arbre : `Nb` (rationnel exact, écriture décimale et % de la saisie gardées pour l'affichage), `Var`, `Pi`, `Neg`, `Op` (+ - * /),
`Pow`, `Fn` (seulement « sqrt »), `Defini` (un nombre nommé : Δ, x₁). Un outil ajoute ses propres nœuds (Exp-log : le nombre e, les
logarithmes) en sous-classes de `Noeud` : ils s'écrivent eux-mêmes (`ecrire_tex`) et disent par deux attributs de classe comment le
TeX commun les traite (`LETTRE`, `BASE_ENTRE_PARENTHESES`). La brique ne connaît aucun nœud d'un outil.

TeX : écrit par l'arbre (`tex`), jamais par SymPy ; nombres en notation suisse (moteur/nombres.py).

Lecture : `tokeniser(texte, lexique)`, `Parseur(jetons, lexique)`, `lire_membres(texte, lexique)` (« membre = membre », ou une
expression seule). Ce que la lecture sait de plus que les opérations, la racine carrée et les nombres est un paramètre explicite, le
`Lexique` passé par l'outil : ses fonctions et la construction de leurs nœuds, les lettres réservées (e d'Exp-log), π, le signe %, les
messages qui citent un exemple. `LEXIQUE_COMMUN` ne lit que sqrt (et √). Les erreurs sont des `ErreurSaisie` (moteur/noyau.py) au
message français.

Aucun état : aucune variable de module n'est modifiée (règle A7 de docs/architecture.md) ; l'état décimal d'Exp-log (`_DECIMAUX`)
reste dans exp_log, qui seul le lit.
"""
import decimal
import re
from collections import namedtuple
from fractions import Fraction as F
from types import MappingProxyType

from noyau import ErreurSaisie
from nombres import MOTIF_ESPACE_DANS_UN_NOMBRE, MOTIF_SAISIE, formater_decimal, formater_entier, nettoyer_saisie

__all__ = ["Noeud", "Nb", "Var", "Pi", "Neg", "Op", "Pow", "Fn", "Defini", "variables", "a_des_decimaux",
           "tex", "tex_saisie", "nb_tex", "comme_somme", "entre_parentheses", "nom_tex", "DEBUT_COLLABLE",
           "Tok", "Lexique", "LEXIQUE_COMMUN", "lire_fonction", "fonction_inconnue", "lire_nom", "tokeniser", "lire_nombre",
           "lire_pourcentage", "Parseur", "lire_membres", "MINUSCULES", "NOM_INDEXE", "SYMBOLES", "OPERATEURS", "INEGALITES",
           "MESSAGE_EXPOSANT_COMMUN", "MESSAGE_VIDE_COMMUN", "MESSAGE_INEQUATION"]


# =====================================================================
# 1. ARBRE SYNTAXIQUE
# =====================================================================
class Noeud:
    """Nœud de l'arbre. Égalité et hachage par la classe et les champs (`__slots__`). Un nœud propre à un outil (sous-classe) définit
    `ecrire_tex` et, s'il le faut, les deux attributs de classe ci-dessous."""
    __slots__ = ()
    LETTRE = False                   # s'écrit comme une lettre : collé au groupe qui le suit (x(x + 1), e(x + 1))
    BASE_ENTRE_PARENTHESES = False   # mis entre parenthèses comme base d'une puissance ((x + 1)², (−x)², (2ˣ)³)

    def _cle(self):
        return (type(self).__name__,) + tuple(getattr(self, s) for s in self.__slots__)

    def __eq__(self, autre):
        return isinstance(autre, Noeud) and self._cle() == autre._cle()

    def __hash__(self):
        return hash(self._cle())

    def __repr__(self):
        return type(self).__name__ + "(" + ", ".join(repr(getattr(self, s)) for s in self.__slots__) + ")"

    def ecrire_tex(self):
        """TeX d'un nœud propre à un outil (appelé par `tex` pour toute classe qu'il ne connaît pas)."""
        raise TypeError(self)


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
    LETTRE = True

    def __init__(self, nom):
        self.nom = nom


class Pi(Noeud):
    """Le nombre π (lu quand le lexique le demande : `Lexique.lire_pi`)."""
    __slots__ = ()


class Neg(Noeud):
    __slots__ = ("a",)
    BASE_ENTRE_PARENTHESES = True

    def __init__(self, a):
        self.a = a


class Op(Noeud):
    """Opération binaire : « + », « - », « * », « / »."""
    __slots__ = ("op", "a", "b")
    BASE_ENTRE_PARENTHESES = True

    def __init__(self, op, a, b):
        self.op, self.a, self.b = op, a, b


class Pow(Noeud):
    __slots__ = ("a", "b")
    BASE_ENTRE_PARENTHESES = True

    def __init__(self, a, b):
        self.a, self.b = a, b


class Fn(Noeud):
    """Fonction à un argument : seulement « sqrt » (une autre fonction est un nœud de l'outil qui la lit : Exp-log construit exp et
    les logarithmes avec ses propres nœuds)."""
    __slots__ = ("nom", "a")

    def __init__(self, nom, a):
        self.nom, self.a = nom, a


class Defini(Noeud):
    """Un nombre qui porte un nom dans le corrigé (Δ, x₁ = (−b − √Δ)/(2a)) : écrit par son nom, évalué par sa définition. Il raccourcit les
    lignes d'un trinôme à coefficients logarithmiques, qui ne tiendraient pas à 360 px."""
    __slots__ = ("nom", "arbre")

    def __init__(self, nom, arbre):
        self.nom, self.arbre = nom, arbre


def variables(n):
    """Ensemble des lettres inconnues (les `Var`) qui apparaissent dans l'arbre ; d'un nœud propre à un outil, celles de ses champs qui
    sont des nœuds (Exp-log : l'argument et la base d'un logarithme ; jamais e)."""
    if isinstance(n, Defini):
        return variables(n.arbre)
    if isinstance(n, Var):
        return {n.nom}
    if isinstance(n, (Nb, Pi)):
        return set()
    if isinstance(n, Neg) or isinstance(n, Fn):
        return variables(n.a)
    if isinstance(n, (Op, Pow)):
        return variables(n.a) | variables(n.b)
    if isinstance(n, Noeud):
        return set().union(*(variables(e) for e in (getattr(n, s) for s in n.__slots__) if isinstance(e, Noeud)))
    raise TypeError(n)


def a_des_decimaux(n):
    """Vrai si l'arbre contient un nombre écrit en décimal (0,7 ; 1,045)."""
    if isinstance(n, Nb):
        return n.dec is not None
    enfants = [getattr(n, nom, None) for nom in getattr(n, "__slots__", ()) if nom != "nom"]
    return any(a_des_decimaux(e) for e in enfants if isinstance(e, Noeud))


# =====================================================================
# 2. TEX (écrit par l'arbre, jamais par SymPy)
# =====================================================================
def nb_tex(n):
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


def comme_somme(n):
    """Vrai si le nœud doit être mis entre parenthèses comme opérande d'une multiplication, d'une puissance ou d'une soustraction."""
    return isinstance(n, Neg) or (isinstance(n, Op) and n.op in "+-") or (isinstance(n, Nb) and n.val < 0)


def entre_parentheses(s):
    return r"\left(" + s + r"\right)" if r"\frac" in s else "(" + s + ")"


# TeX qui se colle après un nombre positif (2x, 3(x + 1), 2\ln(x), 3\sqrt{x}) : une lettre, une parenthèse, une commande de fonction
DEBUT_COLLABLE = re.compile(r"^([A-Za-z(]|\\left\(|\\ln|\\log|\\sqrt|\\pi)")


def nom_tex(nom):
    """C0 s'écrit C_{0} (nom indexé : une lettre suivie de chiffres), une lettre seule telle quelle."""
    return nom[0] + "_{" + nom[1:] + "}" if len(nom) > 1 else nom


def tex(n):
    if isinstance(n, Defini):
        return n.nom
    if isinstance(n, Nb):
        return nb_tex(n)
    if isinstance(n, Var):
        return nom_tex(n.nom)
    if isinstance(n, Pi):
        return r"\pi"
    if isinstance(n, Neg):
        s = tex(n.a)                                      # −(x + 1), et −(−100) quand x = −100 remplace x dans −x : jamais « −−100 »
        return "-" + (entre_parentheses(s) if comme_somme(n.a) else s)
    if isinstance(n, Op):
        if n.op == "/":
            return r"\frac{" + tex(n.a) + "}{" + tex(n.b) + "}"
        g, d = tex(n.a), tex(n.b)
        if n.op == "+":                                   # a + (−b) s'écrit a − b : jamais « + − »
            if isinstance(n.b, Neg):
                return tex(Op("-", n.a, n.b.a))
            if isinstance(n.b, Nb) and n.b.val < 0:
                return tex(Op("-", n.a, Nb(-n.b.val, n.b.dec)))
            return g + " + " + (entre_parentheses(d) if d.startswith("-") else d)       # −x + (−x + 1) : jamais « + − »
        if n.op == "-":
            return g + " - " + (entre_parentheses(d) if comme_somme(n.b) or d.startswith("-") else d)
        deux_groupes = comme_somme(n.a) and comme_somme(n.b)
        if comme_somme(n.a):
            g = entre_parentheses(g)
        if comme_somme(n.b):
            d = entre_parentheses(d)
        lettre_puis_groupe = n.a.LETTRE and comme_somme(n.b)
        if deux_groupes or lettre_puis_groupe or (isinstance(n.a, Nb) and n.a.val >= 0 and DEBUT_COLLABLE.match(d)):
            return g + d
        return g + r" \cdot " + d
    if isinstance(n, Pow):
        base = tex(n.a)
        if n.a.BASE_ENTRE_PARENTHESES or (isinstance(n.a, Nb) and (n.a.val < 0 or n.a.pct is not None or (n.a.val.denominator != 1 and n.a.dec is None))):
            base = entre_parentheses(base)
        return base + "^{" + tex(n.b) + "}"
    if isinstance(n, Fn):
        return r"\sqrt{" + tex(n.a) + "}"
    if isinstance(n, Noeud):
        return n.ecrire_tex()                             # nœud propre à un outil (Exp-log : e, logarithmes)
    raise TypeError(n)


def tex_saisie(g, d=None):
    return tex(g) if d is None else tex(g) + " = " + tex(d)


# =====================================================================
# 3. LEXIQUE ET TOKENISEUR (les noms de fonction passent avant les lettres isolées)
# =====================================================================
# Tables de lecture en lecture seule (MappingProxyType) : la brique n'a aucun conteneur modifiable (A7).
Tok = namedtuple("Tok", "type val base")      # type : num, var, fn, op, const, pct ; base : propre à une fonction de l'outil (log_a)

MINUSCULES = MappingProxyType(str.maketrans("ABCDEFGHIJKLMNOPQRSTUVWXYZ", "abcdefghijklmnopqrstuvwxyz"))      # str.lower() peut changer la longueur : seulement l'ASCII
NOM_INDEXE = re.compile(r"[A-Za-z](?:_([0-9]+)|(?<=[A-Z])([0-9]+))")      # C0, V0, C_0, c_0 (x2 reste x · 2 : message de lecture)
SYMBOLES = MappingProxyType(str.maketrans({"−": "-", "–": "-", "×": "*", "·": "*", "⋅": "*", "÷": "/", "²": "^2", "³": "^3"}))   # x² se lit x^2 (clavier de téléphone)
OPERATEURS = "+-*/^()="
INEGALITES = "<>≤≥≠"

MESSAGE_EXPOSANT_COMMUN = "Mettez l'exposant entre parenthèses : 2^(x+1)."
MESSAGE_VIDE_COMMUN = "Écrivez une expression ou une équation."
MESSAGE_INEQUATION = "Les inéquations ne sont pas traitées par cet outil : écrivez une équation avec =."


def lire_fonction(s, i, brut, lexique):
    """Lecture d'un nom de fonction (celle du `LEXIQUE_COMMUN`) : (jeton, fin) si s[i:] commence par une fonction du lexique, dans
    l'ordre du lexique, suivie d'une parenthèse ; sinon None. `brut` : le texte avant la mise en minuscules (inutile ici ; un outil
    s'en sert pour garder la casse d'une base, log_Q)."""
    for nom in lexique.fonctions:
        if s.startswith(nom, i):
            j = i + len(nom)
            k = j
            while k < len(s) and s[k].isspace():
                k += 1
            if s[k:k + 1] != "(":
                raise ErreurSaisie(f"Après {nom}, ouvrez une parenthèse : {nom}(x).")
            return Tok("fn", nom, None), j
    return None


class Lexique(namedtuple("Lexique", "fonctions lire_fonction noeud_fonction lettres_reservees noeud_lettre lire_pi "
                                    "message_pourcentage message_exposant message_vide",
                         defaults=(("sqrt",), lire_fonction, None, "", Var, False, None, MESSAGE_EXPOSANT_COMMUN, MESSAGE_VIDE_COMMUN))):
    """Ce qu'un outil ajoute à la lecture commune ; paramètre explicite de `tokeniser`, `Parseur` et `lire_membres` (immuable).

    - `fonctions` : les noms de fonction lus (minuscules, dans l'ordre où on les essaie) ; un autre nom suivi d'une parenthèse est
      refusé (« La fonction sin n'est pas traitée par cet outil. ») ;
    - `lire_fonction(s, i, brut, lexique)` : (jeton « fn », fin) ou None ; par défaut `lire_fonction` (le nom, puis une parenthèse) ;
    - `noeud_fonction(jeton, argument)` : le nœud d'une fonction autre que sqrt (None : le lexique n'en lit pas d'autre) ;
    - `lettres_reservees` : lettres qui désignent un nombre (Exp-log : « e ») : lues seules, jamais comme nom indexé, sans tenir compte
      de la casse (E se lit e) ; `noeud_lettre(nom)` : le nœud d'une lettre (par défaut `Var`) ;
    - `lire_pi` : lire « pi » et « π » comme le nombre π ;
    - `message_pourcentage` : None si le signe % n'est pas lu ; sinon le message quand il ne suit pas un nombre ;
    - `message_exposant`, `message_vide` : les messages qui citent un exemple propre à l'outil (exposant à mettre entre parenthèses,
      saisie vide)."""
    __slots__ = ()


LEXIQUE_COMMUN = Lexique()          # opérations, nombres, lettres, sqrt et √ ; ni e, ni π, ni %, ni logarithme


def fonction_inconnue(s, i, fonctions):
    """Le nom (sin, cos, tan, lg…) si les lettres qui commencent en s[i] forment au moins deux lettres suivies d'une parenthèse sans se
    terminer par un nom de fonction connu (xlog(x) reste x · log(x)) ; sinon None."""
    j = i
    while j < len(s) and s[j].isalpha() and s[j].isascii():
        j += 1
    k = j
    while k < len(s) and s[k].isspace():
        k += 1
    if j - i < 2 or s[k:k + 1] != "(" or s[i:j].endswith(tuple(fonctions)):
        return None
    return s[i:j]


def lire_nom(texte, i, lettres_reservees=""):
    """(nom, fin) de la lettre en texte[i] : un nom indexé (C0, V_0, c_0) est une seule inconnue, écrite sans tiret bas (C0) ; une
    lettre réservée (e d'Exp-log) est lue seule, en minuscule."""
    if texte[i].translate(MINUSCULES) in lettres_reservees:
        return texte[i].translate(MINUSCULES), i + 1
    m = NOM_INDEXE.match(texte, i)
    return (texte[i] + (m.group(1) or m.group(2)), m.end()) if m else (texte[i], i + 1)


def tokeniser(texte, lexique=LEXIQUE_COMMUN):
    brut = texte.strip().translate(SYMBOLES)
    s = brut.translate(MINUSCULES)                      # les noms de fonction ne tiennent pas compte de la casse, les lettres oui
    toks, i = [], 0
    while i < len(s):
        c = s[i]
        if c.isspace():
            i += 1
        elif lexique.lire_pi and (c == "π" or (s.startswith("pi", i) and not s[i + 2:i + 3].isalpha() and (i == 0 or not s[i - 1].isalpha()))):
            toks.append(Tok("const", "pi", None))                  # le nombre π (« pi » seul, ou le signe π)
            i += 1 if c == "π" else 2
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
        elif c == "%" and lexique.message_pourcentage is not None:
            if not toks or toks[-1].type != "num":
                raise ErreurSaisie(lexique.message_pourcentage)
            toks.append(Tok("pct", "%", None))
            i += 1
        elif c.isalpha() and c.isascii():
            lu = lexique.lire_fonction(s, i, brut, lexique)
            if lu:
                toks.append(lu[0])
                i = lu[1]
            else:
                inconnue = fonction_inconnue(s, i, lexique.fonctions)
                if inconnue:
                    raise ErreurSaisie(f"La fonction {inconnue} n'est pas traitée par cet outil.")
                nom, i = lire_nom(brut, i, lexique.lettres_reservees)
                toks.append(Tok("var", nom, None))
        elif c in OPERATEURS or c in INEGALITES:
            toks.append(Tok("op", c, None))
            i += 1
        else:
            raise ErreurSaisie(f"Caractère non reconnu : « {c} ».")
    return toks


# =====================================================================
# 4. ANALYSEUR SYNTAXIQUE
# =====================================================================
def lire_nombre(brut):
    t = nettoyer_saisie(brut)
    return Nb(F(t), t.replace(".", ",") if "." in t else None)


def lire_pourcentage(brut):
    """« 3,75 » suivi de % : le nombre 3,75/100 (décimal 0,0375), écrit 3,75 % pour l'aperçu."""
    t = nettoyer_saisie(brut)
    dec = format(decimal.Decimal(t).scaleb(-2), "f")
    if "." in dec:
        dec = dec.rstrip("0").rstrip(".")
    return Nb(F(t) / 100, dec.replace(".", ","), t.replace(".", ","))


class Parseur:
    def __init__(self, toks, lexique=LEXIQUE_COMMUN):
        self.t, self.i, self.lexique = toks, 0, lexique

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
            elif p is not None and (p.type in ("num", "var", "fn", "const") or (p.type == "op" and p.val == "(")):
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
            raise ErreurSaisie(self.lexique.message_exposant)
        n = self.atome()
        if self.est_op("^"):
            raise ErreurSaisie("Mettez les exposants entre parenthèses : 2^(3^2) ou (2^3)^2.")
        s = self.pic()
        if s is not None and p.type in ("num", "var"):
            colle = s.type == "var" or (p.type == "num" and (s.type == "fn" or (s.type == "op" and s.val == "(")))
            if colle:
                raise ErreurSaisie(self.lexique.message_exposant)
        return n

    def atome(self):
        p = self.prendre()
        if p is None:
            raise ErreurSaisie("Il manque quelque chose à la fin de l'expression.")
        if p.type == "num":
            suivant = self.pic()
            if suivant is not None and suivant.type == "pct":
                self.i += 1
                return lire_pourcentage(p.val)
            return lire_nombre(p.val)
        if p.type == "const":
            return Pi()
        if p.type == "var":
            return self.lexique.noeud_lettre(p.val)
        if p.type == "fn":
            self.attendre("(")
            arg = self.somme()
            self.attendre(")")
            if p.val == "sqrt":
                return Fn("sqrt", arg)
            return self.lexique.noeud_fonction(p, arg)
        if p.val == "(":
            n = self.somme()
            self.attendre(")")
            return n
        if p.val == ")":
            raise ErreurSaisie("Parenthèse fermante en trop.")
        if p.val in INEGALITES:
            raise ErreurSaisie(MESSAGE_INEQUATION)
        raise ErreurSaisie(f"Il manque un terme avant « {p.val} ».")


def lire_membres(texte, lexique=LEXIQUE_COMMUN):
    """(gauche, droite) d'une équation « membre = membre », ou (expression, None) sans signe =. Syntaxe seulement : le nombre
    d'inconnues et le sens des lettres se contrôlent chez l'outil (Exp-log : `analyser_saisie`)."""
    toks = tokeniser(texte, lexique)
    if not toks:
        raise ErreurSaisie(lexique.message_vide)
    if any(t.type == "op" and t.val in INEGALITES for t in toks):
        raise ErreurSaisie(MESSAGE_INEQUATION)
    egaux = [i for i, t in enumerate(toks) if t.type == "op" and t.val == "="]
    if len(egaux) > 1:
        raise ErreurSaisie("Un seul signe = dans une équation.")
    if not egaux:
        return Parseur(toks, lexique).tout(), None
    cote = [toks[:egaux[0]], toks[egaux[0] + 1:]]
    if not cote[0] or not cote[1]:
        raise ErreurSaisie("Il manque un membre de l'équation (avant ou après le signe =).")
    return Parseur(cote[0], lexique).tout(), Parseur(cote[1], lexique).tout()
