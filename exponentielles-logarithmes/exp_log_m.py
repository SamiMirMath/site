"""
exp_log_m.py — Outil « Exponentielles et logarithmes », filière M (2Ms, 2Mr) : l'ensemble de définition d'abord, puis la résolution, puis la
vérification de chaque solution contre l'ensemble de définition (T35, spécification « Filière M »).

Ce fichier ajoute à exp_log.py (la 3C, inchangée) :
  - `ensemble_de_definition(g, d, x)` : l'ED d'une équation logarithmique, calculé par le moteur de l'outil Ensemble de définition (le noyau,
    `analyser_complet`) sur l'équation de départ ; l'arbre de l'outil est traduit en saisie de ce moteur (tout logarithme devient ln : la
    condition « argument > 0 » ne dépend pas de la base) ;
  - `verification(ed, solutions, x)` : chaque solution est confrontée aux conditions de l'ED (exactement, jamais par un arrondi d'affichage) ;
    celles qui n'y sont pas sont rejetées avec la raison ;
  - `corriger_equation(g, d, x)` : le corrigé d'une équation logarithmique en filière M.
Tout le TeX est écrit par l'arbre de exp_log.py ou par le moteur de l'outil ED ; ce fichier n'importe ni `sortie` ni SymPy.
"""
import decimal
from fractions import Fraction as F

from noyau import analyser_complet
from exp_log import (Chaine, Defini, E, Fn, Log, Message, Neg, Nb, Op, Pow, Texte, Var, _Hors, _const, _nom_tex, _precis, _valeur_rationnelle,
                     _carte, tex, tex_approx, valeur, variables, logarithmique_m)

__all__ = ["EnsembleDef", "ensemble_de_definition", "verification", "corriger_equation"]


class EnsembleDef:
    """L'ensemble de définition d'une équation : `res` (le résultat de `analyser` de l'outil ED : `conditions`, `ED_tex`, `inter_tex`, `complet`) ou,
    pour une base inconnue, `base` (la chaîne « x > 0 et x ≠ 1 ») ; `ed_tex` : l'ensemble en TeX ; `vide` ; `conditions` : les conditions à vérifier."""
    __slots__ = ("inconnue", "res", "base", "ed_tex", "vide", "conditions", "besoin_sympy")

    def __init__(self, inconnue, res, base, ed_tex, vide, conditions, besoin_sympy=False):
        self.inconnue, self.res, self.base, self.ed_tex, self.vide, self.conditions, self.besoin_sympy = inconnue, res, base, ed_tex, vide, conditions, besoin_sympy


# =====================================================================
# 1. ÉCRITURE EN TEXTE SIMPLE (les raisons d'un rejet sont du texte, pas du TeX : elles passent à la ligne à 360 px)
# =====================================================================
_PRIORITE = {"+": 1, "-": 1, "*": 2, "/": 2}


def _txt(n, mini=0):
    """Écriture en texte simple d'un arbre (x − 1, 2x + 3, ln(x²)), pour les raisons d'un rejet."""
    if isinstance(n, Defini):
        return n.nom
    if isinstance(n, Nb):
        if n.dec:
            return n.dec.replace("-", "−")
        v = n.val
        s = str(abs(v.numerator)) + ("/" + str(v.denominator) if v.denominator != 1 else "")
        return ("−" if v < 0 else "") + s
    if isinstance(n, Var):
        return n.nom
    if isinstance(n, E):
        return "e"
    if isinstance(n, Neg):
        return "−" + _txt(n.a, 3)
    if isinstance(n, Op):
        p = _PRIORITE[n.op]
        signe = {"+": " + ", "-": " − ", "*": "·", "/": "/"}[n.op]
        s = _txt(n.a, p) + signe + _txt(n.b, p + 1)
        return "(" + s + ")" if p < mini else s
    if isinstance(n, Pow):
        return _txt(n.a, 4) + "^" + _txt(n.b, 4)
    if isinstance(n, Fn):
        return "√(" + _txt(n.a) + ")"
    if isinstance(n, Log):
        nom = "log" if n.base is None else "ln" if isinstance(n.base, E) else "log_" + _txt(n.base, 4)
        return nom + "(" + _txt(n.a) + ")"
    raise TypeError(n)


# =====================================================================
# 2. CONDITIONS D'EXISTENCE (parcours de l'arbre) ET APPARTENANCE EXACTE
# =====================================================================
def _logs_en_x(n):
    """Les logarithmes de l'arbre dont l'argument ou la base contient l'inconnue."""
    if isinstance(n, Defini):
        return []
    if isinstance(n, Log):
        return ([n] if variables(n.a) or (n.base is not None and variables(n.base)) else []) + _logs_en_x(n.a)
    if isinstance(n, (Neg, Fn)):
        return _logs_en_x(n.a)
    if isinstance(n, (Op, Pow)):
        return _logs_en_x(n.a) + _logs_en_x(n.b)
    return []


def contient_log_en_x(g, d):
    return bool(_logs_en_x(g) or _logs_en_x(d))


def _liste_conditions(n, x, sortie):
    """Les conditions d'existence de l'arbre, dans l'ordre où l'outil ED les trouve : ("arg", A, log) pour log(A) (A > 0), ("den", B, None) pour un
    dénominateur (B ≠ 0), ("base", None, log) pour une base inconnue (x > 0 et x ≠ 1). Une forme que ce parcours ne connaît pas lève _Hors."""
    if isinstance(n, Defini) or not variables(n):
        if isinstance(n, Log) and variables(n.a):
            raise _Hors
        return
    if isinstance(n, Neg):
        _liste_conditions(n.a, x, sortie)
    elif isinstance(n, Fn):
        raise _Hors                                    # racine carrée dans une équation logarithmique : l'ED la traite, la vérification pas encore
    elif isinstance(n, Log):
        _liste_conditions(n.a, x, sortie)
        if n.base is not None and not isinstance(n.base, E) and variables(n.base):
            if n.base != Var(x):
                raise _Hors                            # base polynomiale (log_(x+1)) : hors du chantier
            sortie.append(("base", None, n))
        if variables(n.a):
            sortie.append(("arg", n.a, n))
    elif isinstance(n, Op):
        _liste_conditions(n.a, x, sortie)
        _liste_conditions(n.b, x, sortie)
        if n.op == "/" and variables(n.b):
            sortie.append(("den", n.b, None))
    elif isinstance(n, Pow):
        k = _const(n.b)
        if variables(n.b) or k is None or k.denominator != 1:
            raise _Hors
        _liste_conditions(n.a, x, sortie)
        if k < 0 and variables(n.a):
            sortie.append(("den", n.a, None))


def _substituer(n, x, s):
    """L'arbre n où l'inconnue x est remplacée par l'arbre s."""
    if isinstance(n, Var):
        return s if n.nom == x else n
    if isinstance(n, Neg):
        return Neg(_substituer(n.a, x, s))
    if isinstance(n, Op):
        return Op(n.op, _substituer(n.a, x, s), _substituer(n.b, x, s))
    if isinstance(n, Pow):
        return Pow(_substituer(n.a, x, s), _substituer(n.b, x, s))
    if isinstance(n, Fn):
        return Fn(n.nom, _substituer(n.a, x, s))
    if isinstance(n, Log):
        return Log(_substituer(n.a, x, s), None if n.base is None else _substituer(n.base, x, s))
    return n


_ZERO = decimal.Decimal("1e-50")


def _signe_exact(n):
    """Signe (−1, 0 ou 1) d'un arbre sans inconnue : exact pour un rationnel (même écrit avec des logarithmes), sinon celui de sa valeur à 80 chiffres
    (zéro sous 10⁻⁵⁰ : une différence de deux écritures d'un même nombre irrationnel)."""
    q = _valeur_rationnelle(n)
    if q is not None:
        return (q > 0) - (q < 0)
    with decimal.localcontext() as c:
        c.prec = 80
        v = _precis(n)
    return 0 if abs(v) < _ZERO else (v > 0) - (v < 0)


def _violation(condition, x, s):
    """None si la solution s (un arbre) vérifie la condition, sinon le signe de la quantité qui la viole (−1 ou 0)."""
    genre, expr, _ = condition
    try:
        if genre == "base":
            signe_x, signe_un = _signe_exact(s), _signe_exact(Op("-", s, Nb(1)))
            return None if signe_x > 0 and signe_un != 0 else (-1 if signe_x < 0 else 0)
        signe = _signe_exact(_substituer(expr, x, s))
    except (ArithmeticError, ValueError, decimal.DecimalException):
        return -1                                      # un logarithme intérieur n'est pas défini : la condition extérieure ne l'est pas non plus
    if genre == "arg":
        return None if signe > 0 else signe
    return None if signe != 0 else 0


def _raison(condition, x, signe):
    """La raison du rejet, en texte simple : « log(x − 1) n'est pas défini : x − 1 < 0 »."""
    genre, expr, log = condition
    if genre == "base":
        return f"{x} est la base d'un logarithme : {x} doit être strictement positif et différent de 1"
    if genre == "den":
        return f"{_txt(expr)} = 0 : division par 0"
    nom = "log" if log.base is None else "ln" if isinstance(log.base, E) else "log_" + _txt(log.base, 4)
    return f"{nom}({_txt(expr)}) n'est pas défini : {_txt(expr)} {'<' if signe < 0 else '='} 0"


# =====================================================================
# 3. ENSEMBLE DE DÉFINITION : traduction vers l'outil ED
# =====================================================================
def _vers_ed(n, x):
    """La saisie du moteur de l'outil ED pour l'arbre n (les logarithmes deviennent ln ; l'inconnue devient x)."""
    if isinstance(n, Defini):
        return _vers_ed(n.arbre, x)
    if isinstance(n, Nb):
        if n.dec:
            return "(" + n.dec.replace(",", ".") + ")" if n.val < 0 else n.dec.replace(",", ".")
        v = n.val
        return f"({v.numerator})" if v.denominator == 1 and v < 0 else str(v.numerator) if v.denominator == 1 else f"({v.numerator}/{v.denominator})"
    if isinstance(n, Var):
        if n.nom != x:
            raise _Hors
        return "x"
    if isinstance(n, E):
        return "e"
    if isinstance(n, Neg):
        return "(-" + _vers_ed(n.a, x) + ")"
    if isinstance(n, Op):
        return "(" + _vers_ed(n.a, x) + n.op + _vers_ed(n.b, x) + ")"
    if isinstance(n, Pow):
        return "((" + _vers_ed(n.a, x) + ")^(" + _vers_ed(n.b, x) + "))"
    if isinstance(n, Fn):
        return "sqrt(" + _vers_ed(n.a, x) + ")"
    if isinstance(n, Log):
        return "ln(" + _vers_ed(n.a, x) + ")"
    raise TypeError(n)


def _logs_imbriques_ok(n):
    """Un logarithme dans un logarithme n'est traité qu'en base e : l'outil ED écrit « ln(x) > 0 ⇔ x > 1 (exp est croissante) », juste seulement pour ln."""
    if isinstance(n, Log):
        interieurs = _logs_en_x(n.a)
        if interieurs and (n.base is not None and not isinstance(n.base, E) or any(l.base is None or not isinstance(l.base, E) for l in interieurs)):
            return False
        return _logs_imbriques_ok(n.a)
    if isinstance(n, (Neg, Fn)):
        return _logs_imbriques_ok(n.a)
    if isinstance(n, (Op, Pow)):
        return _logs_imbriques_ok(n.a) and _logs_imbriques_ok(n.b)
    return True


def ensemble_de_definition(g, d, x):
    """L'EnsembleDef de l'équation g = d (arbres) : par l'outil ED, ou pour une base inconnue (log_x(256) = 4) la condition x > 0 et x ≠ 1.
    Lève _Hors quand l'équation sort de ce que la filière M traite (base polynomiale, logarithme imbriqué en base 10, condition non résolue)."""
    conditions = []
    _liste_conditions(g, x, conditions)
    _liste_conditions(d, x, conditions)
    if not conditions:
        raise _Hors
    if not (_logs_imbriques_ok(g) and _logs_imbriques_ok(d)):
        raise _Hors
    if any(genre == "base" for genre, _, _ in conditions):
        if len(conditions) > 1:
            raise _Hors                                # base inconnue et autre condition : plus tard
        condition = Chaine([Texte(f"{x} > 0 \\text{{ et }} {x} \\neq 1")], note="une base de logarithme est strictement positive et différente de 1")
        return EnsembleDef(x, None, condition, r"\left]0 \,;\, 1\right[ \cup \left]1 \,;\, +\infty\right[", False, conditions)
    res, _, _ = analyser_complet("(" + _vers_ed(g, x) + ")+(" + _vers_ed(d, x) + ")")
    if not res["ok"] or not res["complet"]:
        if res.get("besoin_sympy"):
            return EnsembleDef(x, res, None, "", False, conditions, besoin_sympy=True)
        raise _Hors
    return EnsembleDef(x, res, None, res["ED_tex"], res["ED_tex"] == r"\varnothing", conditions, res["besoin_sympy"])


# =====================================================================
# 4. VÉRIFICATION DES SOLUTIONS CONTRE L'ENSEMBLE DE DÉFINITION
# =====================================================================
NOTE_DANS_ED = "dans l'ensemble de définition ✓"


def _ligne_solution(s, x):
    """L'expression d'une solution pour la vérification : `x = 35/11` (rationnelle), `x_{1} ≈ −2,702` (nommée) ou `(1 + √41)/2 ≈ 3,702`."""
    if isinstance(s, Defini):
        return tex(s) + r" \approx " + tex_approx(valeur(s))
    if _const(s) is not None:
        return _nom_tex(x) + " = " + tex(s)
    return tex(s) + r" \approx " + tex_approx(valeur(s))


def verification(ed, solutions, x):
    """(retenues, lignes) : la solution s est retenue si elle vérifie toutes les conditions de l'ED ; chaque solution a sa ligne (« dans l'ensemble
    de définition ✓ » ou « rejetée : … » avec la première condition violée). Une phrase de plus quand aucune n'est retenue."""
    retenues, lignes = [], []
    for s in solutions:
        raison = None
        for condition in ed.conditions:
            signe = _violation(condition, x, s)
            if signe is not None:
                raison = _raison(condition, x, signe)
                break
        if raison is None:
            retenues.append(s)
            lignes.append(Chaine([Texte(_ligne_solution(s, x))], note=NOTE_DANS_ED))
        else:
            lignes.append(Chaine([Texte(_ligne_solution(s, x) + r" \notin ED")], note="rejetée : " + raison))
    if not retenues:
        lignes.append(Message("Aucune solution de l'équation n'est dans l'ensemble de définition."))
    return retenues, lignes


# =====================================================================
# 5. CORRIGÉ D'UNE ÉQUATION LOGARITHMIQUE EN FILIÈRE M
# =====================================================================
def _carte_ed(ed, apres=()):
    """La carte « Ensemble de définition » ; `apres` : des phrases (Message) qui suivent l'ensemble."""
    return {"titre": "Ensemble de définition", "ed": ed, "apres": list(apres)}


def corriger_equation(g, d, x):
    """Le corrigé de l'équation logarithmique g = d en filière M : la carte « Ensemble de définition », la résolution de la 3C, la carte
    « Vérification » ; une équation dont l'ED est vide n'a pas d'autre carte. None quand ce n'est pas une équation logarithmique en x, ou
    quand la filière M ne la traite pas (le corrigé de la 3C ou le message s'appliquent alors)."""
    if not contient_log_en_x(g, d):
        return None
    try:
        ed = ensemble_de_definition(g, d, x)
    except _Hors:
        return None
    if ed.vide:
        etapes = [_carte_ed(ed, [Message("L'ensemble de définition est vide : l'équation n'a aucune solution.")])]
        return {"genre": "logarithmique", "inconnue": x, "enonce": None, "base": None, "etapes": etapes, "solutions": [], "remarque": None,
                "ed": ed, "besoin_sympy": ed.besoin_sympy}
    r = logarithmique_m(g, d, x)
    if r is None or r["solutions"] is None:
        return None
    etapes = [_carte_ed(ed)] + [dict(c) for c in r["etapes"]]
    if r["remarque"] and etapes[-1].get("lignes") is not None:
        etapes[-1]["lignes"] = list(etapes[-1]["lignes"]) + [Message(r["remarque"])]
    retenues = r["solutions"]
    if r["solutions"]:
        retenues, lignes = verification(ed, r["solutions"], x)
        etapes.append(_carte("Vérification", lignes))
    return {**r, "etapes": etapes, "solutions": retenues, "remarque": None, "ed": ed, "besoin_sympy": ed.besoin_sympy}
