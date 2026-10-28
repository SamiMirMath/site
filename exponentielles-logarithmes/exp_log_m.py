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
from math import gcd

from noyau import analyser_complet
from exp_log import (Chaine, Defini, E, Eq, Fn, Log, Message, Neg, Nb, Op, Ou, Pow, Texte, Var, _Hors, _arbre_poly, _avec_decimaux,
                     _base_du_logarithme, _carte, _const, _contient_log, _nb_exact, _nom_tex, _padd, _par_exponentielle, _pnet, _precis, _produit,
                     _racine_entiere, _resoudre_polynome, _somme_arbres, _suite_polynome, _valeur_exacte, _valeur_rationnelle, _exposant_entier, _racine_primitive, logarithmique_m,
                     resolution_exponentielle, tex, tex_approx, valeur, variables, METHODE_LOGARITHMES, METHODE_MEME_BASE, METHODES, PROP_EXPONENTIELLE, PROP_ISOLER_LOG)

__all__ = ["EnsembleDef", "ensemble_de_definition", "verification", "regrouper", "variantes_changement", "reconnu_changement", "corriger_equation",
           "PROPRIETES_M"]


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
        return "ln(" + _vers_ed(n.a, x) + ")" if variables(n.a) else "1"       # log(3) : aucune condition sur x
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
# 4 bis. REGROUPEMENT DES LOGARITHMES : plusieurs logarithmes, des constantes, deux membres (méthode du cours : on regroupe, on ne développe jamais)
# =====================================================================
_FAMILLES = {"10": "log", "e": "ln", "a": "log_a"}


def _propriete(famille, genre):
    """La propriété (texte) d'une ligne de regroupement, pour la famille de logarithmes « 10 » (log), « e » (ln) ou « a » (log_a)."""
    n = _FAMILLES[famille]
    return {
        "puissance": f"k · {n} u = {n}(u^k), sur l'ED",
        "produit": f"{n} u + {n} v = {n}(uv), sur l'ED",
        "quotient": f"{n} u − {n} v = {n}(u/v), sur l'ED",
        "mixte": "propriétés des logarithmes, sur l'ED",
        "constante": {"10": "c = log(10^c)", "e": "c = ln(e^c)", "a": "c = log_a(a^c)"}[famille],
        "egaux": f"{n} u = {n} v ⇔ u = v, sur l'ED",
    }[genre]


PROP_FOIS_DENOMINATEURS = "on multiplie les deux membres par les dénominateurs, non nuls sur l'ED"
PROP_RACINE_IMPAIRE = "xⁿ = c ⇔ x = c^(1/n) (n impair)"
PROP_RACINE_PAIRE = "xⁿ = c ⇔ x = ±c^(1/n) (n pair, c > 0)"
PROP_PUISSANCE_PAIRE = "une puissance paire est positive ou nulle"
PROP_PUISSANCES = "propriétés des puissances"


def _prop_fois(nom, decalage):
    """« on multiplie les deux membres par t, t > 0 » (t² pour un décalage de 2 ; « divise » quand le décalage est négatif : 8ˣ − 2·4ˣ − 8·2ˣ = 0)."""
    return f"on {'multiplie' if decalage > 0 else 'divise'} les deux membres par {nom}{'²' if abs(decalage) == 2 else ''}, {nom} > 0"


PROPRIETES_M = frozenset({_propriete(f, g) for f in _FAMILLES for g in ("puissance", "produit", "quotient", "mixte", "constante", "egaux")} |
                         {PROP_FOIS_DENOMINATEURS, PROP_RACINE_IMPAIRE, PROP_RACINE_PAIRE, PROP_PUISSANCE_PAIRE, PROP_PUISSANCES} |
                         {_prop_fois(nom, k) for nom in ("t", "u") for k in (-2, -1, 1, 2)})
DEGRE_MAX = 8


def _pmul_n(a, b):
    r = [F(0)] * (len(a) + len(b) - 1)
    for i, u in enumerate(a):
        for j, v in enumerate(b):
            r[i + j] += u * v
    while len(r) > 1 and r[-1] == 0:
        r.pop()
    if len(r) > DEGRE_MAX + 1:
        raise _Hors
    return r


def _pq(n):
    """Coefficients de n, un polynôme en l'inconnue de degré quelconque (jusqu'à DEGRE_MAX) à coefficients rationnels ; sinon _Hors."""
    if not variables(n):
        v = _const(n)
        if v is None:
            raise _Hors
        return [v]
    if isinstance(n, Var):
        return [F(0), F(1)]
    if isinstance(n, Neg):
        return [-c for c in _pq(n.a)]
    if isinstance(n, Op):
        if n.op in "+-":
            return _padd(_pq(n.a), _pq(n.b), 1 if n.op == "+" else -1)
        if n.op == "*":
            return _pmul_n(_pq(n.a), _pq(n.b))
        d = _const(n.b)
        if d is None or d == 0 or variables(n.b):
            raise _Hors
        return [c / d for c in _pq(n.a)]
    if isinstance(n, Pow):
        k = _const(n.b)
        if k is None or k.denominator != 1 or not 0 <= k <= DEGRE_MAX:
            raise _Hors
        r = [F(1)]
        for _ in range(int(k)):
            r = _pmul_n(r, _pq(n.a))
        return r
    raise _Hors


def _decouper(n, signe=F(1)):
    """Les termes d'un membre : [(coefficient, Log)] pour c·log(u), [(coefficient, None)] pour une constante ; _Hors pour tout autre terme."""
    if isinstance(n, Neg):
        return _decouper(n.a, -signe)
    if isinstance(n, Op) and n.op in "+-":
        return _decouper(n.a, signe) + _decouper(n.b, signe if n.op == "+" else -signe)
    if isinstance(n, Log):
        return [(signe, n)]
    if isinstance(n, Op) and n.op == "*":
        for k, l in ((n.a, n.b), (n.b, n.a)):
            c = None if variables(k) or _contient_log(k) else _const(k)
            if c is not None and isinstance(l, Log):
                return [(signe * c, l)]
    if isinstance(n, Op) and n.op == "/" and isinstance(n.a, Log):
        c = None if variables(n.b) or _contient_log(n.b) else _const(n.b)
        if c:
            return [(signe / c, n.a)]
    if not variables(n) and not _contient_log(n):
        c = _const(n)
        if c is not None:
            return [(signe * c, None)]
    raise _Hors


def _cle_base(log):
    noeud, valeur_ = _base_du_logarithme(log.base)
    return "e" if valeur_ is None else valeur_


def _puissance_constante(u, c):
    """u^c (u > 0 rationnel, c rationnel) quand c'est un rationnel exact, sinon _Hors."""
    if c.denominator == 1:
        return u ** int(c)
    r = _racine_entiere(u, c.denominator)
    if r is None:
        raise _Hors
    return r ** c.numerator


def _log_puissance(u, c, base):
    """k · log(u) = log(u^k) avec k = |c| : Log de l'arbre u^k (un nombre si u est constant)."""
    if c == 1:
        return Log(u, base)
    if not variables(u):
        return Log(_nb_exact(_puissance_constante(_const(u), c)), base)
    if c.denominator != 1:
        raise _Hors
    return Log(Pow(u, Nb(c)), base)


def _fusion_constantes(args):
    """Les facteurs d'un produit, la constante en tête et réduite à un seul nombre : [3, x, x + 1]."""
    cte, autres = F(1), []
    for a in args:
        if variables(a):
            autres.append(a)
        else:
            cte *= _const(a)
    return ([_nb_exact(cte)] if cte != 1 or not autres else []) + autres


class _Rap:
    """Le rapport N/D de deux listes de facteurs (D vide : pas de dénominateur) ; `arbre` : N/D écrit."""
    def __init__(self, num, den):
        self.num, self.den = _fusion_constantes(num), (_fusion_constantes(den) if den else [])
        if self.den and not any(variables(a) for a in self.num + self.den):         # deux constantes : un seul nombre
            self.num, self.den = [_nb_exact(_const(_produit(self.num)) / _const(_produit(self.den)))], []
        n = _produit(self.num)
        self.arbre = n if not self.den else Op("/", n, _produit(self.den))


def _arbre_terme(c, log):
    """c·log(u) comme on l'écrit : log(u), −log(u), 2 log(u), −½ log(u)."""
    t = log if abs(c) == 1 else Op("*", _nb_exact(abs(c)), log)
    return Neg(t) if c < 0 else t


def _arbre_unitaire(termes, base):
    """La somme de ±log(u) : termes = [(signe, u)]."""
    return _somme_arbres([Neg(Log(u, base)) if s < 0 else Log(u, base) for s, u in termes])


def _quotient(termes):
    """Le _Rap des termes ±log(u) regroupés en un seul logarithme : produit des arguments positifs sur produit des arguments négatifs."""
    return _Rap([u for s, u in termes if s > 0], [u for s, u in termes if s < 0])


def _resoudre_egalite(chaine, At, Bt, x):
    """Ajoute à `chaine` (qui se termine par At = Bt, deux polynômes) la résolution : (lignes qui suivent, solutions, remarque). `solutions` est None
    quand l'égalité est vraie pour tout x."""
    A, B = _pq(At), _pq(Bt)
    P = _padd(A, B, -1)
    if len(P) <= 3:
        l_poly, solutions, remarque = _resoudre_polynome(A, B, At, Bt, x)
        if (solutions and any(_const(s) is None for s in solutions) and len(P) == 3 and P[1] == 0
                and len(A) == 3 and A[1] == 0 and len(B) == 1 and not variables(Bt)):       # a·x² + q = c : x² = k, x = ±√k (x₁ et x₂ nommés)
            return _suite_polynome(chaine, A, At, Bt, x)
        premiere = l_poly[0]
        for e, lien, prop in zip(premiere.elements[1:], premiere.liens, premiere.props):
            chaine.ajouter(e, lien, prop)
        return l_poly[1:], solutions, remarque
    n = len(P) - 1                                     # degré ≥ 3 : seule la forme a·xⁿ = c se résout
    if any(P[1:n]):
        raise _Hors
    k = -P[0] / P[n]
    X = Var(x)
    puissance = Pow(X, Nb(n))
    if tex(Eq(At, Bt).g) != tex(puissance) or _const(Bt) != k:
        chaine.ajouter(Eq(puissance, _nb_exact(k)), "⇔")
    if n % 2 == 1:
        racine = _racine_entiere(abs(k), n)
        sol = Nb(-racine if k < 0 else racine) if racine is not None else (Pow(_nb_exact(k), Nb(F(1, n))) if k > 0 else Neg(Pow(_nb_exact(-k), Nb(F(1, n)))))
        chaine.ajouter(Eq(X, sol), "⇔", PROP_RACINE_IMPAIRE)
        return [], [sol], None
    if k < 0:
        chaine.ajouter(Eq(puissance, _nb_exact(k)), "⇔") if False else None
        return [], [], "Une puissance paire est positive ou nulle : l'équation n'a aucune solution."
    if k == 0:
        chaine.ajouter(Eq(X, Nb(0)), "⇔", PROP_RACINE_PAIRE)
        return [], [Nb(0)], None
    racine = _racine_entiere(k, n)
    pos = Nb(racine) if racine is not None else Pow(_nb_exact(k), Nb(F(1, n)))
    neg = Nb(-racine) if racine is not None else Neg(pos)
    chaine.ajouter(Ou([Eq(X, neg), Eq(X, pos)]), "⇔", PROP_RACINE_PAIRE)
    return [], [neg, pos], None


@_avec_decimaux
def regrouper(g, d, x):
    """Le corrigé de l'équation logarithmique g = d par regroupement des logarithmes (log u + log v = log(uv), log u − log v = log(u/v), k log u = log(u^k),
    c = log(10^c)), puis log A = log B ⇔ A = B ou l'exponentielle des deux membres, puis une équation polynomiale de degré ≤ 2 (ou a·xⁿ = c).
    Les logarithmes sont tous de la même base constante et leurs arguments des polynômes. None quand la forme n'est pas traitée."""
    try:
        return _regrouper(g, d, x)
    except _Hors:
        return None


def _regrouper(g, d, x):
    enonce = Eq(g, d)
    tg, td = _decouper(g), _decouper(d)
    lg, ld = [(c, l) for c, l in tg if l is not None], [(c, l) for c, l in td if l is not None]
    kg, kd = sum((c for c, l in tg if l is None), F(0)), sum((c for c, l in td if l is None), F(0))
    tous = [l for _, l in lg + ld]
    if not tous or len({_cle_base(l) for l in tous}) != 1:
        raise _Hors
    base, valeur_base = _base_du_logarithme(tous[0].base)
    ecrite = tous[0].base                              # la base telle qu'elle est écrite (None pour log)
    for l in tous:
        _pq(l.a)
        if not variables(l.a) and _const(l.a) <= 0:
            raise _Hors                                # log(−3) : le calcul de la 3C répond
    if not any(variables(l.a) for l in tous):
        raise _Hors
    famille = "e" if valeur_base is None else "10" if valeur_base == 10 else "a"
    un_cote = not (lg and ld)                           # un membre sans logarithme : l'exponentielle des deux membres
    logs, k_logs, k_autre, a_gauche = (lg, kg, kd, True) if lg or not ld else (ld, kd, kg, False)
    # ---- carte 1 : regrouper ----
    lignes_regroupement = []
    chaine = Chaine([enonce])
    courant = {"g": g, "d": d}
    termes_g = [(c, l) for c, l in lg]
    termes_d = [(c, l) for c, l in ld]
    c0 = None
    if un_cote:
        c0 = k_autre - k_logs
        termes = [(c, l) for c, l in logs]
        if k_logs != 0:                                 # Σ logs + K = c ⇔ Σ logs = c − K
            somme, cte = _somme_arbres([_arbre_terme(c, l) for c, l in termes]), Nb(c0)
            chaine.ajouter(Eq(somme, cte) if a_gauche else Eq(cte, somme), "⇔", PROP_ISOLER_LOG)
        membres = {"logs": termes}
    else:
        membres = {"g": termes_g, "d": termes_d}

    def arbres(unitaires):
        """Les deux membres (ou le seul membre de logarithmes) écrits à partir de termes [(signe, u)] ; la constante c0 reste à sa place."""
        if un_cote:
            somme = _arbre_unitaire(unitaires["logs"], ecrite)
            return (somme, Nb(c0)) if a_gauche else (Nb(c0), somme)
        return _arbre_unitaire(unitaires["g"], ecrite), _arbre_unitaire(unitaires["d"], ecrite)

    # étape 1 : k · log(u) = log(u^k)
    unitaires = {}
    changement = False
    for cle, termes in membres.items():
        unitaires[cle] = []
        for c, l in termes:
            if abs(c) != 1:
                changement = True
            unitaires[cle].append((1 if c > 0 else -1, _log_puissance(l.a, abs(c), ecrite).a))
    if changement:
        a, b = arbres(unitaires)
        chaine.ajouter(Eq(a, b), "⇔", _propriete(famille, "puissance"))
    # étape 2 : c = log(10^c), seulement quand les deux membres ont des logarithmes
    if not un_cote:
        for cle, k in (("g", kg), ("d", kd)):
            if k != 0:
                if k.denominator != 1 or valeur_base is None:
                    raise _Hors
                unitaires[cle].append((1 if k > 0 else -1, _nb_exact(valeur_base ** int(abs(k)))))
        if kg != 0 or kd != 0:
            a, b = arbres(unitaires)
            chaine.ajouter(Eq(a, b), "⇔", _propriete(famille, "constante"))
    # étape 3 : un seul logarithme par membre
    a_regrouper = any(len(t) > 1 or t[0][0] < 0 for t in unitaires.values())
    rapports = {cle: _quotient(t) for cle, t in unitaires.items()}
    if a_regrouper:
        positifs_multiples = any(sum(1 for s, _ in t if s > 0) > 1 for t in unitaires.values())
        negatifs = any(any(s < 0 for s, _ in t) for t in unitaires.values())
        genre = "mixte" if positifs_multiples and negatifs else "produit" if positifs_multiples else "quotient"
        logs_regroupes = {cle: Log(r.arbre, ecrite) for cle, r in rapports.items()}
        if un_cote:
            a, b = (logs_regroupes["logs"], Nb(c0)) if a_gauche else (Nb(c0), logs_regroupes["logs"])
        else:
            a, b = logs_regroupes["g"], logs_regroupes["d"]
        chaine.ajouter(Eq(a, b), "⇔", _propriete(famille, genre))
    cartes = []
    if len(chaine.elements) > 1:
        cartes.append(_carte("Regroupement des logarithmes", [chaine]))
    # ---- carte 2 : exponentielle des deux membres, ou log A = log B ⇔ A = B ----
    if un_cote:
        r = rapports["logs"]
        logarithme = Log(r.arbre, ecrite)
        carte2 = Chaine([Eq(logarithme, Nb(c0)) if a_gauche else Eq(Nb(c0), logarithme)])
        if not a_gauche:
            carte2.ajouter(Eq(logarithme, Nb(c0)), "⇔")
        rhs = _nb_exact(c0)
        puissance = base if isinstance(base, E) and rhs == Nb(1) else Pow(base, rhs)
        v = F(1) if c0 == 0 else _const(puissance)          # e⁰ = 1
        if v is None or v <= 0:
            raise _Hors
        exact = _valeur_exacte(puissance)
        _par_exponentielle(carte2, logarithme, base, puissance, exact or puissance, [puissance] if exact is not None else ())
        egal = (r, _Rap([_nb_exact(v)], []))
        titre = "Exponentielle des deux membres"
    else:
        ra, rb = rapports["g"], rapports["d"]
        carte2 = Chaine([Eq(Log(ra.arbre, ecrite), Log(rb.arbre, ecrite))])
        carte2.ajouter(Eq(ra.arbre, rb.arbre), "⇔", _propriete(famille, "egaux"))
        egal = (ra, rb)
        titre = "Égalité des logarithmes"
    ra, rb = egal
    if ra.den or rb.den:                                # N_A / D_A = N_B / D_B ⇔ N_A · D_B = N_B · D_A (les dénominateurs ne s'annulent pas sur l'ED)
        gauche = _produit(_fusion_constantes(ra.num + rb.den))
        droite = _produit(_fusion_constantes(rb.num + ra.den))
        carte2.ajouter(Eq(gauche, droite), "⇔", PROP_FOIS_DENOMINATEURS)
    else:
        gauche, droite = ra.arbre, rb.arbre
    suite, solutions, remarque = _resoudre_egalite(carte2, gauche, droite, x)
    if solutions is None:
        remarque = "Cette égalité est vraie pour tout x de l'ensemble de définition."
    cartes.append(_carte(titre, [carte2] + suite))
    return {"genre": "logarithmique", "inconnue": x, "enonce": enonce, "base": None, "etapes": cartes, "solutions": solutions, "remarque": remarque}


# =====================================================================
# 4 ter. CHANGEMENT DE VARIABLE : 2ᵉ degré en aˣ (4ˣ − 2ˣ − 6 = 0, e^(2x) − 3eˣ + 2 = 0, 3^(x+1) + 3^(−x) = 4)
# =====================================================================
def _additifs(n, signe=F(1)):
    if isinstance(n, Neg):
        return _additifs(n.a, -signe)
    if isinstance(n, Op) and n.op in "+-":
        return _additifs(n.a, signe) + _additifs(n.b, signe if n.op == "+" else -signe)
    return [(signe, n)]


def _terme_exp(n, x):
    """(k, base, (q, p)) pour n = k · base^(q + p·x) : base est un rationnel > 0 (≠ 1), "e", ou None quand n est une constante (k)."""
    if not variables(n):
        v = _const(n)
        if v is None:
            raise _Hors
        return v, None, None
    if isinstance(n, Neg):
        k, b, e = _terme_exp(n.a, x)
        return -k, b, e
    if isinstance(n, Op) and n.op in "*/":
        k1, b1, e1 = _terme_exp(n.a, x)
        k2, b2, e2 = _terme_exp(n.b, x)
        if n.op == "/":
            if k2 == 0:
                raise _Hors
            k2, e2 = 1 / k2, (None if e2 is None else (-e2[0], -e2[1]))
        if b1 is not None and b2 is not None and b1 != b2:
            raise _Hors
        base = b1 if b1 is not None else b2
        if b1 is not None and b2 is not None:
            e = (e1[0] + e2[0], e1[1] + e2[1])
        else:
            e = e1 if b1 is not None else e2
        return k1 * k2, base, e
    if isinstance(n, Pow):
        if variables(n.b):
            if variables(n.a):
                raise _Hors
            p = _pq(n.b)
            if len(p) > 2:
                raise _Hors
            base = "e" if isinstance(n.a, E) else _const(n.a)
            if base is None or (base != "e" and (base <= 0 or base == 1)):
                raise _Hors
            return F(1), base, (p[0], p[1] if len(p) > 1 else F(0))
        k = _const(n.b)
        k0, b0, e0 = _terme_exp(n.a, x)
        if k is None or k.denominator != 1 or b0 is None or not 0 < k <= 4:
            raise _Hors
        return k0 ** int(k), b0, (e0[0] * k, e0[1] * k)
    raise _Hors


def _pgcd_rationnels(valeurs):
    den = 1
    for v in valeurs:
        den = den * v.denominator // gcd(den, v.denominator)
    g = 0
    for v in valeurs:
        g = gcd(g, int(abs(v) * den))
    return F(g, den)


def _arbre_t(c, mu, T):
    """c · tᵘ comme on l'écrit : 3t, t², −t, 1/t, 2/t²."""
    if mu == 0:
        return _nb_exact(c)
    puissance = T if abs(mu) == 1 else Pow(T, Nb(abs(mu)))
    if mu > 0:
        corps = puissance if abs(c) == 1 else Op("*", _nb_exact(abs(c)), puissance)
    else:
        corps = Op("/", _nb_exact(abs(c)), puissance)
    return Neg(corps) if c < 0 else corps


class _Plan:
    """Tout ce que les deux méthodes ont en commun dans un changement de variable : la variable t, les cartes d'avant le retour à x, les valeurs de t."""
    __slots__ = ("t", "cartes", "retenues", "base_noeud", "pas", "lignes_t", "x", "enonce", "remarque", "variable")


def _plan(g, d, x):
    return _plan_apres(g, d, x, *_analyse(g, d, x))


def _analyse(g, d, x):
    """Reconnaît une équation du 2ᵉ degré en aˣ : (termes, b0, base_noeud, lignes, constantes, pas, mus, decalage). _Hors sinon."""
    termes = {"g": [(s, n, _terme_exp(n, x)) for s, n in _additifs(g)], "d": [(s, n, _terme_exp(n, x)) for s, n in _additifs(d)]}
    bases = {b for lt in termes.values() for _, _, (_, b, _) in lt if b is not None}
    if not bases:
        raise _Hors
    if "e" in bases:
        if bases != {"e"}:
            raise _Hors
        b0 = "e"
    else:
        racines = {_racine_primitive(b) for b in bases}
        if len(racines) != 1:
            raise _Hors
        candidats = sorted(b for b in bases if b > 1)
        b0 = next((c for c in candidats if all(_exposant_entier(b, c) is not None for b in bases)), racines.pop())
    base_noeud = E() if b0 == "e" else _nb_exact(b0)
    lignes = {"g": [], "d": []}                          # (signe, terme écrit, coefficient sans le signe, pente de l'exposant en base b0)
    constantes = {"g": F(0), "d": F(0)}
    for cote, lt in termes.items():
        for s, n, (k, b, e) in lt:
            if b is None:
                constantes[cote] += s * k
                continue
            m = 1 if b0 == "e" else _exposant_entier(b, b0)
            q, p = e
            if b0 == "e" and q != 0:
                raise _Hors                              # e^(x+1) : coefficient irrationnel
            sigma = m * p
            cn = k * (F(1) if b0 == "e" else _puissance_constante(b0, m * q))
            if sigma == 0:
                constantes[cote] += s * cn
            else:
                lignes[cote].append((s, n, cn, sigma))
    pentes = [sg for lt in lignes.values() for _, _, _, sg in lt]
    if not pentes:
        raise _Hors
    pas = _pgcd_rationnels(pentes)
    if any((sg / pas).denominator != 1 for sg in pentes):
        raise _Hors
    mus = {int(sg / pas) for sg in pentes} | ({0} if constantes["g"] != 0 or constantes["d"] != 0 else set())
    decalage = -min(mus)
    if max(mus) - min(mus) != 2 or max(mus) > 4 or abs(decalage) > 2:
        raise _Hors
    return termes, b0, base_noeud, lignes, constantes, pas, mus, decalage


def reconnu_changement(g, d, x):
    """Vrai pour une équation du 2ᵉ degré en aˣ (au programme M), que l'outil la résolve ou non."""
    try:
        _analyse(g, d, x)
        return True
    except _Hors:
        return False


def _plan_apres(g, d, x, termes, b0, base_noeud, lignes, constantes, pas, mus, decalage):
    t = "u" if x == "t" else "t"
    T = Var(t)
    t_tex = Pow(base_noeud, _arbre_poly([F(0), pas], x))
    carte = [Message("On pose ", Texte(f"{t} = " + tex(t_tex)), ". Une exponentielle est strictement positive : ", Texte(f"{t} > 0"), ".")]
    arbres_t, polys = {}, {}
    for cote in ("g", "d"):
        morceaux, poly = [], [F(0)] * (max(mus) + decalage + 1)
        for s, n, cn, sigma in lignes[cote]:
            mu = int(sigma / pas)
            milieu, forme = _arbre_t(cn, mu, t_tex), _arbre_t(cn, mu, T)
            if tex(n) != tex(milieu):                    # le terme n'est pas déjà c · aˣ : une ligne qui le réécrit avec t
                carte.append(Chaine([n, milieu, forme], ["=", "="], [PROP_PUISSANCES, None]))
            morceaux.append(_arbre_t(s * cn, mu, T))
            poly[mu + decalage] += s * cn
        if constantes[cote] != 0:
            morceaux.append(_nb_exact(constantes[cote]))
            poly[decalage] += constantes[cote]
        arbres_t[cote] = _somme_arbres(morceaux) if morceaux else Nb(0)
        polys[cote] = _pnet(poly)
    plan = _Plan()
    plan.t, plan.x, plan.base_noeud, plan.pas, plan.enonce, plan.variable = t, x, base_noeud, pas, Eq(g, d), (t, t_tex)
    chaine = Chaine([Eq(g, d), Eq(arbres_t["g"], arbres_t["d"])], ["⇔"], [None])
    At, Bt = _arbre_poly(polys["g"], t), _arbre_poly(polys["d"], t)
    if decalage:
        chaine.ajouter(Eq(At, Bt), "⇔", _prop_fois(t, decalage))
    suite, solutions, remarque = _resoudre_egalite(chaine, At, Bt, t)
    if solutions is None or any(_const(s) is None for s in solutions):
        raise _Hors                                      # identité en t ou racines irrationnelles : pas encore
    plan.remarque = remarque
    cartes = [_carte("Changement de variable", carte + [chaine] + suite)]
    solutions = sorted(solutions, key=_const)
    lignes_t, retenues = [], []
    for s in solutions:
        v = _const(s)
        if v > 0:
            retenues.append(v)
            lignes_t.append(Chaine([Texte(f"{t} = {tex(s)} > 0")], note="retenue ✓"))
        else:
            lignes_t.append(Chaine([Texte(f"{t} = {tex(s)} \\le 0")], note="rejetée : " + PROP_EXPO_POSITIVE))
    if solutions:
        if not retenues:
            lignes_t.append(Message("Aucune valeur de ", Texte(t), " ne convient : l'équation n'a aucune solution."))
        cartes.append(_carte(f"Valeurs de {t}", lignes_t))
    plan.cartes, plan.retenues = cartes, retenues
    return plan


PROP_EXPO_POSITIVE = "une exponentielle est strictement positive"


def _resultat_methode(plan, methode):
    cartes = list(plan.cartes)
    solutions, message = [], None
    for v in plan.retenues:
        r = resolution_exponentielle(Pow(plan.base_noeud, _arbre_poly([F(0), plan.pas], plan.x)), _nb_exact(v), plan.x, methode)
        if r is None:
            raise _Hors
        suffixe = f" ({plan.t} = {_txt(Nb(v))})" if len(plan.retenues) > 1 else ""
        cartes += [{**c, "titre": c["titre"] + suffixe} for c in r["etapes"]]
        if r.get("message"):
            message = message or r["message"]
        solutions += r["solutions"] or []
    solutions.sort(key=valeur)
    resultat = {"genre": "changement", "inconnue": plan.x, "enonce": plan.enonce, "base": None, "etapes": cartes, "solutions": [] if message else solutions,
                "remarque": plan.remarque, "variable": plan.variable}
    if message:
        resultat["message"] = message
    return resultat


@_avec_decimaux
def variantes_changement(g, d, x):
    """{méthode: résultat} d'une équation du 2ᵉ degré en aˣ (t = aˣ, t > 0), les deux méthodes du retour à x ; None si ce n'est pas une telle équation."""
    try:
        plan = _plan(g, d, x)
        return {m: _resultat_methode(plan, m) for m in METHODES}
    except _Hors:
        return None


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
    r = logarithmique_m(g, d, x) or regrouper(g, d, x)
    if r is None:
        return None
    etapes = [_carte_ed(ed)] + [dict(c) for c in r["etapes"]]
    if r["remarque"] and etapes[-1].get("lignes") is not None:
        etapes[-1]["lignes"] = list(etapes[-1]["lignes"]) + [Message(r["remarque"])]
    retenues, autres = r["solutions"], {"candidats": r["solutions"]}
    if r["solutions"] is None:                         # l'égalité est vraie sur tout l'ensemble de définition : S = ED
        autres["ensemble"] = r.get("ensemble", ed.ed_tex)
    elif r["solutions"]:
        retenues, lignes = verification(ed, r["solutions"], x)
        etapes.append(_carte("Vérification", lignes))
    return {**r, **autres, "etapes": etapes, "solutions": retenues, "remarque": None, "ed": ed, "besoin_sympy": ed.besoin_sympy}
