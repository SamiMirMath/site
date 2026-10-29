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
import random
from fractions import Fraction as F
from math import gcd

from noyau import analyser_complet
from exp_log import (Car, Chaine, Defini, E, Eq, Fn, Log, Message, Neg, Nb, Op, Ou, Pow, Rel, Texte, Var, _Hors, _arbre_poly, _avec_decimaux,
                     _base_du_logarithme, _carte, _const, _contient_log, _nb_exact, _nom_tex, _padd, _par_exponentielle, _pnet, _precis, _produit,
                     _racine_entiere, _resoudre_polynome, _somme_arbres, _suite_polynome, _milieu_exact, _valeur_exacte, _valeur_rationnelle, _exposant_entier, _racine_carree, _racine_primitive, tex_element, logarithmique_m, _fin_beta,
                     resolution_exponentielle, tex, tex_approx, valeur, variables, METHODE_LOGARITHMES, METHODE_MEME_BASE, METHODES, PROP_EXPONENTIELLE, PROP_ISOLER_LOG, PROP_PUISSANCE_NEGATIVE, PROP_EXP_LOG_BASE,
                     PROP_AUCUNE_SOLUTION, PROP_CAR_LN_E, PROP_CAR_LOG_10, PROP_DEFINITION_LOG, PROP_FOIS_MOINS_UN, PROP_LN_DEUX_MEMBRES,
                     PROP_LN_E_PUISSANCE, PROP_LN_PUISSANCE, PROP_LOG_BASE_PUISSANCE, PROP_LOG_DEUX_MEMBRES, PROP_LOG_PUISSANCE, PROP_MEME_BASE)

__all__ = ["EnsembleDef", "ensemble_de_definition", "verification", "regrouper", "variantes_changement", "variantes_exposant", "reconnu_exposant", "reconnu_changement", "corriger_equation",
           "exercice_m", "NIVEAUX_M", "POIDS_M", "PROPRIETES_M"]


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


def _txt_lineaire(n, x):
    """Un polynôme du 1er degré en texte simple, comme on l'écrit à la main : 2x, x + 1, −x + 3 (la base d'un logarithme)."""
    b0, b1 = _pq(n)
    coef = "" if abs(b1) == 1 else _txt(Nb(abs(b1)))
    terme = ("−" if b1 < 0 else "") + coef + x
    if b0 == 0:
        return terme
    return terme + (" − " if b0 < 0 else " + ") + _txt(Nb(abs(b0)))


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


def _liste_conditions(n, x, sortie, general=False):
    """Les conditions d'existence de l'arbre, dans l'ordre où l'outil ED les trouve : ("arg", A, log) pour log(A) (A > 0), ("den", B, None) pour un
    dénominateur (B ≠ 0), ("base", None, log) pour une base inconnue (x > 0 et x ≠ 1) et, si `general`, ("rac", A, None) pour √A (A ≥ 0) ; avec `general`
    aussi, l'exposant d'une puissance de base constante peut contenir l'inconnue (e^(6/x)). Une forme que ce parcours ne connaît pas lève _Hors."""
    if isinstance(n, Defini) or not variables(n):
        if isinstance(n, Log) and variables(n.a):
            raise _Hors
        return
    if isinstance(n, Neg):
        _liste_conditions(n.a, x, sortie, general)
    elif isinstance(n, Fn):
        if not general:
            raise _Hors                                # racine carrée dans une équation logarithmique : l'ED la traite, la vérification pas encore
        _liste_conditions(n.a, x, sortie, general)
        sortie.append(("rac", n.a, None))
    elif isinstance(n, Log):
        _liste_conditions(n.a, x, sortie, general)
        if n.base is not None and not isinstance(n.base, E) and variables(n.base):
            if n.base == Var(x):
                sortie.append(("base", None, n))
            elif variables(n.a) or len(_pq(n.base)) != 2:
                raise _Hors                            # log_(x+1)(x+2), base de degré ≥ 2 : pas encore
            else:
                sortie.append(("basep", n.base, n))    # log_(2x)(1296) : base du 1er degré, argument constant
        if variables(n.a):
            sortie.append(("arg", n.a, n))
    elif isinstance(n, Op):
        _liste_conditions(n.a, x, sortie, general)
        _liste_conditions(n.b, x, sortie, general)
        if n.op == "/" and variables(n.b):
            sortie.append(("den", n.b, None))
    elif isinstance(n, Pow):
        if general and variables(n.b) and not variables(n.a):
            _liste_conditions(n.b, x, sortie, general)       # b^A, b constante : seule A peut manquer de sens
            return
        k = _const(n.b)
        if variables(n.b) or k is None or k.denominator != 1:
            raise _Hors
        _liste_conditions(n.a, x, sortie, general)
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
        if genre == "basep":
            base = _substituer(expr, x, s)
            signe_b, signe_un = _signe_exact(base), _signe_exact(Op("-", base, Nb(1)))
            return None if signe_b > 0 and signe_un != 0 else (-1 if signe_b < 0 else 0 if signe_b == 0 else 1)
        signe = _signe_exact(_substituer(expr, x, s))
    except (ArithmeticError, ValueError, decimal.DecimalException):
        return -1                                      # un logarithme intérieur n'est pas défini : la condition extérieure ne l'est pas non plus
    if genre == "arg":
        return None if signe > 0 else signe
    if genre == "rac":
        return None if signe >= 0 else signe
    return None if signe != 0 else 0


def _raison(condition, x, signe):
    """La raison du rejet, en texte simple : « log(x − 1) n'est pas défini : x − 1 < 0 »."""
    genre, expr, log = condition
    if genre == "base":
        return f"{x} est la base d'un logarithme : {x} doit être strictement positif et différent de 1"
    if genre == "basep":
        base = _txt_lineaire(expr, x)
        return f"log_({base})({_txt(log.a)}) n'est pas défini : la base {base} {'< 0' if signe < 0 else '= 0' if signe == 0 else '= 1'}"
    if genre == "den":
        return f"{_txt(expr)} = 0 : division par 0"
    if genre == "rac":
        return f"√({_txt(expr)}) n'est pas défini : {_txt(expr)} < 0"
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
    """Vrai quand les logarithmes imbriqués sont tous en base e : l'outil ED sait les traiter (« ln(x) > 0 ⇔ x > 1 (exp est croissante) », juste seulement
    pour ln). Sinon l'ensemble de définition est calculé ici (_ed_imbrique)."""
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


_PUISSANCE_MAX = 400                                   # |exposant| maximal d'une borne b^c (10^10 passe, 10^(10^10) non)


def _borne(b, c):
    """b^c, une borne exacte : b rationnel > 0 (None pour la base e : seul e^0 = 1 est rationnel) et c entier ; sinon _Hors."""
    if b is None:
        if c != 0:
            raise _Hors
        return F(1)
    if c.denominator != 1 or abs(c) > _PUISSANCE_MAX:
        raise _Hors
    return b ** int(c)


def _image_reciproque(b, lo, hi):
    """{w : log_b(w) ∈ ]lo ; hi[}, b > 0 et ≠ 1 (lo à None : −∞, hi à None : +∞) : ]b^lo ; b^hi[ si b > 1 (log_b croissante), ]b^hi ; b^lo[ si b < 1."""
    croissante = b is None or b > 1
    if croissante:
        return (F(0) if lo is None else _borne(b, lo)), (None if hi is None else _borne(b, hi))
    return (F(0) if hi is None else _borne(b, hi)), (None if lo is None else _borne(b, lo))


def _tex_ens(lo, hi):
    """L'intervalle ouvert ]lo ; hi[ en TeX (lo à None : −∞, hi à None : +∞)."""
    bas = r"-\infty" if lo is None else tex(Nb(lo))
    haut = r"+\infty" if hi is None else tex(Nb(hi))
    return r"\left]" + bas + r" \,;\, " + haut + r"\right["


def _tex_ineg(t, lo, hi):
    """L'inégalité qui écrit t ∈ ]lo ; hi[ (« < » est écrit &lt; : la ligne est du HTML)."""
    if hi is None:
        return f"{t} > {tex(Nb(lo))}"
    if lo is None:
        return f"{t} &lt; {tex(Nb(hi))}"
    return f"{tex(Nb(lo))} &lt; {t} &lt; {tex(Nb(hi))}"


def _base_log(l):
    """La base rationnelle du logarithme l (10 pour log, None pour ln)."""
    return None if isinstance(l.base, E) else F(10) if l.base is None else _const(l.base)


def _contient(n, cible):
    if n is cible:
        return True
    if isinstance(n, (Neg, Fn, Log)):
        return _contient(n.a, cible)
    if isinstance(n, (Op, Pow)):
        return _contient(n.a, cible) or _contient(n.b, cible)
    return False


def _chaine_de_logarithmes(g, d, conditions):
    """La chaîne log_b1(log_b2(… log_bn(u))) de l'équation, du plus extérieur au plus intérieur, avec u du 1er degré : tous les logarithmes en x de
    l'équation la forment, d'un seul côté du signe =, et leurs bases sont des constantes ; sinon _Hors."""
    logs = _logs_en_x(g) + _logs_en_x(d)
    if not logs or (_logs_en_x(g) and _logs_en_x(d)) or any(genre != "arg" for genre, _, _ in conditions) or len(logs) != len(conditions):
        raise _Hors
    for l in logs:
        if l.base is not None and not isinstance(l.base, E) and (variables(l.base) or _const(l.base) is None or _const(l.base) <= 0 or _const(l.base) == 1):
            raise _Hors
    hauts = [l for l in logs if not any(_contient(m.a, l) for m in logs if m is not l)]
    if len(hauts) != 1:
        raise _Hors
    chaine = [hauts[0]]
    while isinstance(chaine[-1].a, Log) and variables(chaine[-1].a):
        chaine.append(chaine[-1].a)
    if len(chaine) != len(logs):
        raise _Hors
    u = chaine[-1].a
    c = _pq(u)
    if len(c) != 2 or c[1] == 0:
        raise _Hors                                    # l'argument le plus intérieur doit être du 1er degré
    return chaine, u, c[0], c[1]


def _ed_imbrique(g, d, x, conditions):
    """L'ensemble de définition d'une équation dont les logarithmes forment une chaîne imbriquée dont une base n'est pas e (log(log(x)) = 1,
    log_2(log_2(x)) = 1, log(log(log(x - 1))) = 0) : l'outil ED ne connaît que ln, ses bornes seraient fausses (e au lieu de 10). Une condition par
    logarithme, dans l'ordre de l'outil ED (du plus intérieur au plus extérieur) : log_b(A) > 0 se ramène, couche par couche, à une inégalité sur
    l'argument de A (log_b est croissante si b > 1, décroissante si 0 < b < 1), puis au 1er degré. Les bornes sont exactes (b^c, c entier) ; sinon _Hors."""
    chaine, u, q0, p1 = _chaine_de_logarithmes(g, d, conditions)
    if any(_base_log(l) is None and l.base is not None and not isinstance(l.base, E) for l in chaine):
        raise _Hors
    n = len(chaine)
    cartes, ensembles, besoin = [], [], False
    for rang in range(1, n + 1):                       # la condition de rang `rang` : l'argument du logarithme chaine[n - rang] est > 0
        l = chaine[n - rang]
        couches = chaine[n - rang + 1:]               # les logarithmes que contient cet argument, du plus extérieur au plus intérieur
        lo, hi = F(0), None
        if not couches:                                # l'argument est u : la condition de l'outil ED (u > 0)
            r, _, _ = analyser_complet("ln(" + _vers_ed(u, x) + ")")
            if not r["ok"] or not r["complet"]:
                raise _Hors
            c = dict(r["conditions"][0])
            besoin = besoin or bool(r.get("besoin_sympy"))
        else:
            lignes, phrases, courant = [], [], l.a                  # `courant` : l'expression dont on écrit le signe (le 1er logarithme de `couches`)
            for m in couches:
                lo2, hi2 = _image_reciproque(_base_log(m), lo, hi)
                phrase = f"({'ln' if isinstance(m.base, E) else 'log' if m.base is None else 'log_' + _txt(m.base, 4)} est {'croissante' if _base_log(m) is None or _base_log(m) > 1 else 'décroissante'})."
                lignes.append(f"{_tex_ineg(tex(courant), lo, hi)} \\iff {_tex_ineg(tex(m.a), lo2, hi2)}")
                phrases.append(phrase)
                lo, hi, courant = lo2, hi2, m.a
            c = {"genre": "ln", "titre": "logarithme", "source_tex": tex(l.a), "cond_tex": tex(l.a) + " > 0", "resolu": True}
        # u ∈ ]lo ; hi[ ⇔ x ∈ ]bas ; haut[ (p1·x + q0 = u)
        bas = None if lo is None else (lo - q0) / p1
        haut = None if hi is None else (hi - q0) / p1
        if p1 < 0:
            bas, haut = haut, bas
        if couches:
            if not (p1 == 1 and q0 == 0):
                lignes[-1] += " \\iff " + _tex_ineg("x", bas, haut)
            c["etapes"] = [{"type": "texte", "html": "\\(" + ligne + "\\) " + phrase} for ligne, phrase in zip(lignes, phrases)]
        c["num"], c["E_tex"] = rang, _tex_ens(bas, haut)
        cartes.append(c)
        ensembles.append((bas, haut))
    bas = max((b for b, _ in ensembles if b is not None), default=None)
    haut = min((h for _, h in ensembles if h is not None), default=None)
    vide = bas is not None and haut is not None and bas >= haut
    ed_tex = r"\varnothing" if vide else _tex_ens(bas, haut)
    res = {"ok": True, "conditions": cartes, "complet": True, "besoin_sympy": besoin, "ED_tex": ed_tex,
           "inter_tex": r" \cap ".join(c["E_tex"] for c in cartes) if len(cartes) > 1 else ""}
    return EnsembleDef(x, res, None, ed_tex, vide, conditions, besoin)


def _ed_base_polynomiale(x, conditions):
    """L'ensemble de définition de log_B(n) = k avec B du 1er degré : B > 0 et B ≠ 1 (les cartes de l'outil ED pour 1/ln(B), la seconde renommée)."""
    if len(conditions) != 1:
        raise _Hors                                    # une base polynomiale et une autre condition : pas encore
    base = conditions[0][1]
    res, _, _ = analyser_complet("1/ln(" + _vers_ed(base, x) + ")")
    if not res["ok"] or not res["complet"] or len(res["conditions"]) != 2:
        raise _Hors
    positive, differente = (dict(c) for c in res["conditions"])
    ln_b = r"\ln\left(" + tex(base) + r"\right)"
    positive["titre"], differente["titre"] = "base strictement positive", "base différente de 1"
    differente["cond_tex"] = tex(base) + r" \neq 1"
    etapes = [dict(e) for e in differente["etapes"][1:]]                       # « ln(2x) = 0 ⇔ 2x = 1 » n'est plus utile : on écrit 2x ≠ 1 directement
    etapes = [{**e, "html": e["html"].replace(ln_b + r" \neq 0", tex(base) + r" \neq 1")} if e.get("type") == "texte" else e for e in etapes]
    differente["etapes"] = etapes
    res = {**res, "conditions": [positive, differente]}
    return EnsembleDef(x, res, None, res["ED_tex"], res["ED_tex"] == r"\varnothing", conditions, res["besoin_sympy"])


def ensemble_de_definition(g, d, x, general=False):
    """L'EnsembleDef de l'équation g = d (arbres) : par l'outil ED, ou pour une base inconnue (log_x(256) = 4) la condition x > 0 et x ≠ 1.
    Lève _Hors quand l'équation sort de ce que la filière M traite (base polynomiale, condition non résolue). `general` : équation exponentielle dont
    l'exposant contient 1/x, √x ou un logarithme (variantes_exposant) ; les conditions « 7 > 0 » des bases constantes n'y sont pas écrites."""
    conditions = []
    _liste_conditions(g, x, conditions, general)
    _liste_conditions(d, x, conditions, general)
    if not conditions:
        raise _Hors
    if general:
        res, _, _ = analyser_complet("(" + _vers_ed(g, x) + ")+(" + _vers_ed(d, x) + ")")
        if not res["ok"] or not res["complet"]:
            raise _Hors
        utiles = [c for c in res["conditions"] if not (c["genre"] == "pos" and c["E_tex"] == r"\mathbb{R}")]
        for k, c in enumerate(utiles, 1):
            c["num"] = k
        res = {**res, "conditions": utiles, "inter_tex": r" \cap ".join(c["E_tex"] for c in utiles) if len(utiles) > 1 else ""}
        return EnsembleDef(x, res, None, res["ED_tex"], res["ED_tex"] == r"\varnothing", conditions, res["besoin_sympy"])
    if any(genre == "basep" for genre, _, _ in conditions):
        return _ed_base_polynomiale(x, conditions)
    if not (_logs_imbriques_ok(g) and _logs_imbriques_ok(d)):
        return _ed_imbrique(g, d, x, conditions)
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
        "oppose": f"−{n} a = {n}(1/a)",
    }[genre]


PROP_FOIS_DENOMINATEURS = "on multiplie les deux membres par les dénominateurs, non nuls sur l'ED"
PROP_RACINE_IMPAIRE = "xⁿ = c ⇔ x = c^(1/n) (n impair)"
PROP_RACINE_PAIRE = "xⁿ = c ⇔ x = ±c^(1/n) (n pair, c > 0)"
PROP_PUISSANCE_PAIRE = "une puissance paire est positive ou nulle"
PROP_PUISSANCES = "propriétés des puissances"
PROP_CARRE_DES_DEUX_MEMBRES = "les deux membres sont positifs : on élève au carré"
PROP_ISOLER_RACINE = "on isole la racine"


def _prop_fois(nom, decalage):
    """« on multiplie les deux membres par t, t > 0 » (t² pour un décalage de 2 ; « divise » quand le décalage est négatif : 8ˣ − 2·4ˣ − 8·2ˣ = 0)."""
    return f"on {'multiplie' if decalage > 0 else 'divise'} les deux membres par {nom}{'' if abs(decalage) == 1 else '²³⁴'[abs(decalage) - 2]}, {nom} > 0"


def _prop_pose(t, u):
    """« on pose u = t² » : l'équation bicarrée t⁴ − 10t² + 9 = 0 devient u² − 10u + 9 = 0."""
    return f"on pose {u} = {t}²"


PROPRIETES_M = frozenset({_propriete(f, g) for f in _FAMILLES for g in ("puissance", "produit", "quotient", "mixte", "constante", "egaux", "oppose")} |
                         {PROP_CARRE_DES_DEUX_MEMBRES, PROP_ISOLER_RACINE, PROP_FOIS_DENOMINATEURS, PROP_RACINE_IMPAIRE, PROP_RACINE_PAIRE, PROP_PUISSANCE_PAIRE, PROP_PUISSANCES} |
                         {_prop_fois(nom, k) for nom in ("t", "u") for k in (-4, -3, -2, -1, 1, 2, 3, 4)} | {_prop_pose("t", "u"), _prop_pose("u", "v")})
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
        carre_pur = len(P) == 3 and P[1] == 0 and len(A) == 3 and A[1] == 0 and len(B) == 1 and not variables(Bt)         # a·x² + q = c
        try:
            l_poly, solutions, remarque = _resoudre_polynome(A, B, At, Bt, x)
        except _Hors:
            if not carre_pur:
                raise
            return _suite_polynome(chaine, A, At, Bt, x)                                    # coefficients non entiers (5x² = 1/10) : x² = k
        if solutions and any(_const(s) is None for s in solutions) and carre_pur:         # x² = k, x = ±√k (x₁ et x₂ nommés)
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
        _par_exponentielle(carte2, logarithme, base, puissance, exact or puissance, _milieu_exact(puissance, exact))
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
    if len(pentes) + (1 if constantes["g"] != 0 or constantes["d"] != 0 else 0) < 3:
        raise _Hors                                      # moins de trois termes : pas un trinôme en t, la méthode de la 3C (même base, logarithmes)
    pas = _pgcd_rationnels(pentes)
    if any((sg / pas).denominator != 1 for sg in pentes):
        raise _Hors
    mus = {int(sg / pas) for sg in pentes} | ({0} if constantes["g"] != 0 or constantes["d"] != 0 else set())
    decalage = -min(mus)
    bicarre = len(mus) == 3 and max(mus) - min(mus) == 4 and sorted(mus)[1] == min(mus) + 2      # t⁻³, t⁻¹, t : t⁴ − 10t² + 9 après multiplication par t³
    if not bicarre and (max(mus) - min(mus) != 2 or max(mus) > 4 or abs(decalage) > 2):
        raise _Hors
    if bicarre and (max(mus) > 5 or abs(decalage) > 4):
        raise _Hors
    return termes, b0, base_noeud, lignes, constantes, pas, mus, decalage


def reconnu_changement(g, d, x):
    """Vrai pour une équation du 2ᵉ degré en aˣ (au programme M), que l'outil la résolve ou non."""
    try:
        _analyse(g, d, x)
        return True
    except _Hors:
        return False


def _bicarre(chaine, At, Bt, t):
    """L'équation bicarrée at⁴ + bt² + c = 0 (t > 0) : on pose u = t², u > 0, on résout le trinôme en u (les valeurs de u retenues sont celles qui sont
    strictement positives), puis les candidats t = ±√u (la racine négative est rejetée par la carte « Valeurs de t »). (cartes, candidats t, remarque)."""
    A, B = _pq(At), _pq(Bt)
    P = _padd(A, B, -1)
    if len(P) != 5 or P[1] != 0 or P[3] != 0:
        raise _Hors
    u = "v" if t == "u" else "u"
    standard = Eq(_arbre_poly(P, t), Nb(0))
    if tex_element(standard) != tex_element(chaine.elements[-1]):
        chaine.ajouter(standard, "⇔")
    quadratique = P[0::2]
    ligne = Chaine([standard, Eq(_arbre_poly(quadratique, u), Nb(0))], ["⇔"], [_prop_pose(t, u)])
    suite, valeurs_u, remarque = _resoudre_egalite(ligne, _arbre_poly(quadratique, u), Nb(0), u)
    lignes = [Message("Équation bicarrée : on pose ", Texte(f"{u} = {t}^{{2}}"), ". Comme ", Texte(f"{t} > 0"), ", ", Texte(f"{u} > 0"), ".")]
    lignes += [ligne] + suite
    if valeurs_u is None or any(_const(v) is None for v in valeurs_u):
        raise _Hors
    candidats, retenues = [], []
    for v in sorted(valeurs_u, key=_const):
        q = _const(v)
        if q > 0:
            retenues.append(q)
            lignes.append(Chaine([Texte(f"{u} = {tex(v)} > 0")], note="retenue ✓"))
        else:
            lignes.append(Chaine([Texte(f"{u} = {tex(v)} \\le 0")], note=f"rejetée : {u} = {t}² est strictement positif"))
    if valeurs_u and not retenues:
        lignes.append(Message("Aucune valeur de ", Texte(u), " ne convient : l'équation n'a aucune solution."))
    for q in retenues:
        r = _racine_carree(q)
        if r is None:
            raise _Hors                                  # t = √2 : pas encore (2ˣ = √2 n'est pas traité)
        lignes.append(Chaine([Eq(Pow(Var(t), Nb(2)), _nb_exact(q)), Ou([Eq(Var(t), _nb_exact(-r)), Eq(Var(t), _nb_exact(r))])], ["⇔"], [PROP_RACINE_PAIRE]))
        candidats += [_nb_exact(-r), _nb_exact(r)]
    return [_carte("Équation bicarrée", lignes)], sorted(candidats, key=_const), remarque


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
    if max(mus) - min(mus) == 4:
        cartes_bicarre, solutions, remarque = _bicarre(chaine, At, Bt, t)
        cartes = [_carte("Changement de variable", carte + [chaine])] + cartes_bicarre
    else:
        suite, solutions, remarque = _resoudre_egalite(chaine, At, Bt, t)
        cartes = [_carte("Changement de variable", carte + [chaine] + suite)]
    if solutions is None or any(_const(s) is None for s in solutions):
        raise _Hors                                      # identité en t ou racines irrationnelles : pas encore
    plan.remarque = remarque
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
# 4 quater. EXPONENTIELLE À EXPOSANT NON POLYNOMIAL : e^(6/x) = e^(x − 1), 3^(−1/x) = 20, 7^√x = 3, e^(−ln x) = 3 (T36, partie B)
# =====================================================================
REMARQUE_RACINE_NEGATIVE = "Une racine carrée est positive ou nulle : l'équation n'a aucune solution."


def _contient_fn(n):
    if isinstance(n, Fn):
        return True
    if isinstance(n, (Neg, Log)):
        return _contient_fn(n.a)
    if isinstance(n, (Op, Pow)):
        return _contient_fn(n.a) or _contient_fn(n.b)
    return False


def _frac(n):
    """(N, D) : n = N/D, deux polynômes en l'inconnue à coefficients rationnels (listes [c0, c1, …]) ; sinon _Hors."""
    if not variables(n):
        v = _const(n)
        if v is None:
            raise _Hors
        return [v], [F(1)]
    if isinstance(n, Var):
        return [F(0), F(1)], [F(1)]
    if isinstance(n, Neg):
        N, D = _frac(n.a)
        return [-c for c in N], D
    if isinstance(n, Op):
        N1, D1 = _frac(n.a)
        N2, D2 = _frac(n.b)
        if n.op in "+-":
            return _padd(_pmul_n(N1, D2), _pmul_n(N2, D1), 1 if n.op == "+" else -1), _pmul_n(D1, D2)
        if n.op == "*":
            return _pmul_n(N1, N2), _pmul_n(D1, D2)
        if not any(N2):
            raise _Hors
        return _pmul_n(N1, D2), _pmul_n(D1, N2)
    if isinstance(n, Pow):
        k = _const(n.b)
        if variables(n.b) or k is None or k.denominator != 1 or not -4 <= k <= 4:
            raise _Hors
        N, D = _frac(n.a)
        if k < 0:
            if not any(N):
                raise _Hors
            N, D, k = D, N, -k
        rn, rd = [F(1)], [F(1)]
        for _ in range(int(k)):
            rn, rd = _pmul_n(rn, N), _pmul_n(rd, D)
        return rn, rd
    raise _Hors


def _cote_exponentiel(n):
    """(nœud de la base, valeur de la base — 'e' ou un rationnel > 0 différent de 1 —, exposant) pour b^A avec l'inconnue dans A ; sinon None."""
    if isinstance(n, Pow) and not variables(n.a) and variables(n.b):
        if isinstance(n.a, E):
            return n.a, "e", n.b
        v = _const(n.a)
        if v is not None and v > 0 and v != 1:
            return n.a, v, n.b
    return None


def _genre_exposant(a):
    """« racine » (l'exposant contient √), « log » (il contient un logarithme), « frac » (fraction rationnelle dont le dénominateur est du 1er degré)
    ou « poly » (aucun dénominateur : la 3C et le changement de variable le traitent) ; _Hors si l'exposant sort de ces formes."""
    if _contient_fn(a):
        return "racine"
    if _logs_en_x(a):
        return "log"
    N, D = _frac(a)
    if len(D) == 1:
        return "poly"
    if len(D) > 2 or len(N) > 3:
        raise _Hors
    return "frac"


def _sans_racine(n, x):
    """n où √x est remplacé par la lettre « r » (qui devient la seule variable) ; _Hors si une racine porte sur autre chose que x, ou si x reste."""
    if isinstance(n, Fn):
        if n.a != Var(x):
            raise _Hors
        return Var("r")
    if isinstance(n, Neg):
        return Neg(_sans_racine(n.a, x))
    if isinstance(n, Op):
        return Op(n.op, _sans_racine(n.a, x), _sans_racine(n.b, x))
    if isinstance(n, Pow):
        return Pow(_sans_racine(n.a, x), _sans_racine(n.b, x))
    if isinstance(n, Var):
        raise _Hors                                    # x et √x ensemble : pas encore
    return n


def _affine_en_racine(a, x):
    """(p, q) tels que a = p + q·√x (p rationnel, q rationnel non nul) ; sinon _Hors."""
    c = _pq(_sans_racine(a, x))
    if len(c) != 2 or c[1] == 0:
        raise _Hors
    return c[0], c[1]


def _exposant_logarithme(a, valeur_base):
    """(signe, logarithme) pour a = ±log_b(u), u du 1er degré et b la base de l'exponentielle ; sinon _Hors."""
    signe = 1
    if isinstance(a, Neg):
        signe, a = -1, a.a
    if not isinstance(a, Log) or (a.base is not None and variables(a.base)):
        raise _Hors
    cle = F(10) if a.base is None else "e" if isinstance(a.base, E) else _const(a.base)
    c = _pq(a.a)
    if cle != valeur_base or len(c) != 2 or c[1] == 0:
        raise _Hors
    return signe, a


class _Situation:
    """L'équation b^A = c ou b^A = b^B décrite pour les deux méthodes."""
    __slots__ = ("x", "g", "d", "echange", "noeud", "base", "exposant", "genre", "second", "autre", "constante", "m")


def _situation(g, d, x):
    """Reconnaît b^A = c (c rationnel) et b^A = b^B (même base) où A contient 1/x, √x ou log(x) ; _Hors sinon (la 3C et le changement de variable
    traitent les exposants polynomiaux)."""
    gauche, droite = _cote_exponentiel(g), _cote_exponentiel(d)
    s = _Situation()
    s.x, s.g, s.d, s.echange, s.second, s.autre, s.constante, s.m = x, g, d, False, None, None, None, None
    if gauche is None and droite is None:
        raise _Hors
    if gauche is not None and droite is not None:
        if gauche[1] != droite[1]:
            raise _Hors
        s.noeud, s.base, s.exposant = gauche
        s.autre = droite[2]
        genres = {_genre_exposant(s.exposant), _genre_exposant(s.autre)}
        if genres != {"frac"} and genres != {"frac", "poly"}:
            raise _Hors
        s.genre = "meme_base"
        return s
    s.echange = gauche is None
    s.noeud, s.base, s.exposant = droite if s.echange else gauche
    s.second = g if s.echange else d
    if variables(s.second):
        raise _Hors
    s.constante = _const(s.second)
    if isinstance(s.second, Pow) and not variables(s.second.b) and _const(s.second.b) is not None and (
            (s.base == "e" and isinstance(s.second.a, E)) or (s.base != "e" and _const(s.second.a) == s.base)):
        s.m = _const(s.second.b)                       # le second membre est écrit b^m (e^2, 2^3) : même base tout de suite
    elif s.constante is None:
        raise _Hors
    s.genre = _genre_exposant(s.exposant)
    if s.genre == "poly":
        raise _Hors
    if s.genre == "racine":
        _affine_en_racine(s.exposant, x)
    if s.genre == "log" and s.m is not None:
        raise _Hors
    if s.genre == "log" and s.constante > 0:
        _exposant_logarithme(s.exposant, s.base)
        if s.constante == 1:
            raise _Hors
    return s


def _puissance_de_la_base(s, c):
    """L'entier m tel que c = b^m, ou None."""
    if c == 1:
        return F(0)
    return None if s.base == "e" else _exposant_entier(c, s.base)


def _arbre_produit_poly(facteur, poly, x):
    """facteur · poly(x) écrit proprement : m·D, avec m = 1 (D seul) et m = 0 (0) traités à part."""
    return _arbre_poly([facteur * c for c in poly], x)


def _fin_egalite_des_exposants(chaine, s, resultat, titre):
    """b^A = b^B ⇒ A = B (chaîne déjà écrite jusque-là) ; fractions : on multiplie par le dénominateur, puis l'équation polynomiale."""
    x = s.x
    A, B = s.exposant, s.autre
    (NA, DA), (NB, DB) = _frac(A), _frac(B)
    if len(DA) > 1 and len(DB) > 1 and DA != DB:
        raise _Hors
    Dm = DA if len(DA) > 1 else DB
    Dtree = _arbre_poly(Dm, x)
    gauche = _arbre_poly(NA, x) if DA == Dm else Op("*", Dtree, A)
    droite = _arbre_poly(NB, x) if DB == Dm else Op("*", Dtree, B)
    if len(_pq(gauche)) < len(_pq(droite)):             # x(x − 1) = 6 plutôt que 6 = x(x − 1) : le côté de plus haut degré à gauche
        gauche, droite = droite, gauche
    chaine.ajouter(Eq(gauche, droite), "⇔", PROP_FOIS_DENOMINATEURS)
    suite, solutions, remarque = _resoudre_egalite(chaine, gauche, droite, x)
    return resultat([_carte(titre, [chaine] + suite)], solutions, remarque)


def _fin_fraction(chaine, s, A, K_rat, K_log, resultat, titre):
    """A = K avec A = N/D : N = K·D, puis la résolution. K_rat : K rationnel, K_log : K un logarithme L(c) (ou L(c)/L(b), traité par l'appelant)."""
    x = s.x
    N, D = _frac(A)
    if K_rat is not None:
        gauche = _arbre_poly(N, x)
        droite = _arbre_poly([K_rat * c for c in D], x)
        if len(N) < len(D):
            gauche, droite = droite, gauche
        chaine.ajouter(Eq(gauche, droite), "⇔", PROP_FOIS_DENOMINATEURS)
        suite, solutions, remarque = _resoudre_egalite(chaine, gauche, droite, x)
        return resultat([_carte(titre, [chaine] + suite)], solutions, remarque)
    raise _Hors


def _quotient_de_logarithmes(n, haut, bas):
    """n · haut / bas écrit comme à la main : −log(3)/log(20), 2 log(3)/log(5). `haut` None : n seul au numérateur."""
    num = _nb_exact(abs(n)) if haut is None else haut if abs(n) == 1 else Op("*", _nb_exact(abs(n)), haut)
    q = Op("/", num, bas)
    return Neg(q) if n < 0 else q


def _x_egal_quotient(chaine, s, N, lb, lc, resultat, titre):
    """n·L(b) = x·L(c) (D = x, N = n constant) : x = n·L(b)/L(c), car L(c) ≠ 0. `lb` None : L(b) = 1 (log(10), ln(e))."""
    x = s.x
    haut_gauche = _nb_exact(N[0]) if lb is None else (Neg(lb) if N[0] == -1 else lb if N[0] == 1 else Op("*", _nb_exact(N[0]), lb))
    chaine.ajouter(Eq(haut_gauche, Op("*", Var(x), lc)), "⇔", PROP_FOIS_DENOMINATEURS)
    solution = _quotient_de_logarithmes(N[0], lb, lc)
    chaine.ajouter(Eq(Var(x), solution), "⇔", Car(lc))
    return resultat([_carte(titre, [chaine])], [solution])


def _fin_fraction_logarithmes(chaine, s, resultat, titre, c):
    """b^(N/D) = c, c non puissance de b : N·log(b) = D·log(c) ; monômes c·xᵏ·log(a), puis la fin de la méthode B de la 3C (degré 1 ou 2)."""
    x = s.x
    N, D = _frac(s.exposant)
    ln = s.base == "e"
    cle = "e" if ln else F(10)
    lb, lc = Log(s.noeud, E() if ln else None), Log(s.second, E() if ln else None)
    if len(N) == 1 and D == [0, 1]:
        return _x_egal_quotient(chaine, s, N, lb, lc, resultat, titre)
    chaine.ajouter(Eq(Op("*", _arbre_poly(N, x), lb), Op("*", _arbre_poly(D, x), lc)), "⇔", PROP_FOIS_DENOMINATEURS)
    a_b = None if s.base == cle else s.base
    a_c = None if c == cle else c
    monos_g = [(n, k, a_b) for k, n in enumerate(N) if n != 0]
    monos_d = [(dk, k, a_c) for k, dk in enumerate(D) if dk != 0]
    ecrit = {}
    if a_b is not None:
        ecrit[a_b] = s.noeud
    if a_c is not None:
        ecrit[a_c] = s.second
    suite, solutions, remarque = _fin_beta(chaine, monos_g, monos_d, x, ecrit, ln)
    return resultat([_carte(titre, suite)], solutions, remarque)


def _fin_racine(chaine, s, K_rat, K_tree, resultat, titre):
    """p + q√x = K : √x = (K − p)/q, puis x = (…)² quand (K − p)/q est positif ; négatif : aucune solution. K_rat : K rationnel (sinon K_tree, une
    constante écrite avec des logarithmes, dont la valeur peut être rationnelle : log(8)/log(2) = 3)."""
    x, X = s.x, Var(s.x)
    p, q = _affine_en_racine(s.exposant, x)
    if K_rat is not None:
        S = Nb((K_rat - p) / q)
    else:
        S = K_tree if p == 0 else Op("-", K_tree, _nb_exact(p)) if p > 0 else Op("+", K_tree, _nb_exact(-p))
        if q != 1:
            S = Op("/", S, _nb_exact(q))
    valeur_s = _valeur_rationnelle(S)
    signe = _signe_exact(S)
    racine = Fn("sqrt", X)
    if not (p == 0 and q == 1):
        chaine.ajouter(Eq(racine, S), "⇔", PROP_ISOLER_RACINE)
    if signe < 0:
        return resultat([_carte(titre, [chaine])], [], REMARQUE_RACINE_NEGATIVE)
    if signe == 0:
        chaine.ajouter(Eq(X, Nb(0)), "⇔")
        return resultat([_carte(titre, [chaine])], [Nb(0)])
    if valeur_s is None and p != 0:
        raise _Hors                                    # x = ((log 3/log 2 + 1))² : pas encore (la ligne « S = … » ne tient pas à 360 px)
    carre = Pow(S, Nb(2))
    if valeur_s is not None:
        solution = Nb(valeur_s ** 2)
        chaine.ajouter(Eq(X, solution, [carre]), "⇔", PROP_CARRE_DES_DEUX_MEMBRES)
    else:
        solution = carre
        chaine.ajouter(Eq(X, carre), "⇔", PROP_CARRE_DES_DEUX_MEMBRES)
    return resultat([_carte(titre, [chaine])], [solution])


def _exposant_log(chaine, s, methode, resultat):
    """b^(±log_b(u)) = c : même chaîne pour les deux méthodes après la première ligne (définition du logarithme, ou logarithme des deux membres)."""
    x = s.x
    signe, lg = _exposant_logarithme(s.exposant, s.base)
    u, c = lg.a, s.constante
    famille = "e" if s.base == "e" else "10" if lg.base is None else "a"
    ln = s.base == "e"
    lc = Log(s.second, lg.base)
    gauche = Neg(lg) if signe < 0 else lg
    if methode == METHODE_MEME_BASE:
        titre = "Même base / définition"
        chaine.ajouter(Eq(gauche, lc), "⇔", PROP_DEFINITION_LOG)
    else:
        titre = "Logarithme des deux membres"
        chaine.ajouter(Eq(Log(_exponentielle(s), lg.base), lc), "⇔", PROP_LN_DEUX_MEMBRES if ln else PROP_LOG_DEUX_MEMBRES)
        chaine.ajouter(Eq(gauche, lc), "⇔", PROP_LN_E_PUISSANCE if ln else PROP_LOG_BASE_PUISSANCE)
    if signe < 0:
        chaine.ajouter(Eq(lg, Neg(lc)), "⇔", PROP_FOIS_MOINS_UN)
        inverse = _nb_exact(1 / c)
        chaine.ajouter(Eq(lg, Log(inverse, lg.base)), "⇔", _propriete(famille, "oppose"))
        cible = inverse
    else:
        cible = s.second
    chaine.ajouter(Eq(u, cible), "⇔", _propriete(famille, "egaux"))
    suite, solutions, remarque = _resoudre_egalite(chaine, u, cible, x)
    return resultat([_carte(titre, [chaine] + suite)], solutions, remarque)


def _exponentielle(s):
    return Pow(s.noeud, s.exposant)


def _methode_exposant(s, methode):
    """Le résultat (sans ensemble de définition) de la méthode A (même base / définition) ou B (logarithmes) d'une équation de _situation."""
    x = s.x
    enonce = Eq(s.g, s.d)
    chaine = Chaine([enonce])
    if s.echange:
        chaine.ajouter(Eq(s.d, s.g), "⇔")
    ln = s.base == "e"

    def resultat(cartes, solutions, remarque=None, **autres):
        return {"genre": "exposant", "inconnue": x, "enonce": enonce, "base": None, "etapes": cartes, "solutions": solutions, "remarque": remarque, **autres}

    if s.genre == "meme_base":
        if methode == METHODE_MEME_BASE:
            titre = "Même base"
            chaine.ajouter(Eq(s.exposant, s.autre), "⇔", PROP_MEME_BASE)
        else:
            titre = "Logarithme des deux membres"
            chaine.ajouter(Eq(Log(_exponentielle(s), E() if ln else None), Log(Pow(s.noeud, s.autre), E() if ln else None)), "⇔",
                           PROP_LN_DEUX_MEMBRES if ln else PROP_LOG_DEUX_MEMBRES)
            if s.base in ("e", F(10)):
                chaine.ajouter(Eq(s.exposant, s.autre), "⇔", PROP_LN_E_PUISSANCE if ln else PROP_LOG_BASE_PUISSANCE)
            else:
                lb = Log(s.noeud)
                chaine.ajouter(Eq(Op("*", s.exposant, lb), Op("*", s.autre, lb)), "⇔", PROP_LOG_PUISSANCE)
                chaine.ajouter(Eq(s.exposant, s.autre), "⇔", Car(lb))
        return _fin_egalite_des_exposants(chaine, s, resultat, titre)

    if s.m is not None:                                  # b^A = b^m
        A = s.exposant
        if methode == METHODE_MEME_BASE:
            titre = "Même base"
            chaine.ajouter(Eq(A, _nb_exact(s.m)), "⇔", PROP_MEME_BASE)
        else:
            titre = "Logarithme des deux membres"
            bl = E() if ln else None
            chaine.ajouter(Eq(Log(_exponentielle(s), bl), Log(s.second, bl)), "⇔", PROP_LN_DEUX_MEMBRES if ln else PROP_LOG_DEUX_MEMBRES)
            if s.base in ("e", F(10)):
                chaine.ajouter(Eq(A, _nb_exact(s.m)), "⇔", PROP_LN_E_PUISSANCE if ln else PROP_LOG_BASE_PUISSANCE)
            else:
                lb = Log(s.noeud)
                chaine.ajouter(Eq(Op("*", A, lb), Op("*", _nb_exact(s.m), lb)), "⇔", PROP_LOG_PUISSANCE)
                chaine.ajouter(Eq(A, _nb_exact(s.m)), "⇔", Car(lb))
        if s.genre == "racine":
            return _fin_racine(chaine, s, s.m, _nb_exact(s.m), resultat, titre)
        return _fin_fraction(chaine, s, A, s.m, None, resultat, titre)

    c = s.constante
    if c <= 0:                                           # une exponentielle est strictement positive
        positif, autre = _exponentielle(s), s.second
        lignes = [Chaine([Rel(positif, ">", Nb(0))], note=PROP_EXPO_POSITIVE),
                  Chaine([Eq(positif, autre) if c == 0 else Rel(autre, "<", Nb(0))], note=PROP_AUCUNE_SOLUTION)]
        return resultat([_carte("Aucune solution", lignes)], [])
    if s.genre == "log":
        return _exposant_log(chaine, s, methode, resultat)

    A = s.exposant
    m = _puissance_de_la_base(s, c)
    if methode == METHODE_MEME_BASE:
        titre = "Même base / définition"
        if m is not None:                                # c = b^m
            chaine.ajouter(Eq(_exponentielle(s), Pow(s.noeud, _nb_exact(m))), "⇔")
            chaine.ajouter(Eq(A, _nb_exact(m)), "⇔", PROP_MEME_BASE)
            K_rat, K_tree = m, _nb_exact(m)
        elif s.base in ("e", F(10)):                     # définition du logarithme
            K_rat, K_tree = None, Log(s.second, E() if ln else None)
            chaine.ajouter(Eq(A, K_tree), "⇔", PROP_DEFINITION_LOG)
        else:
            message = Message(s.second, " n'est pas une puissance de ", s.noeud, " : il faut les logarithmes.")
            return resultat([_carte(titre, [message])], [], None, message=message)
        if s.genre == "racine":
            return _fin_racine(chaine, s, K_rat, K_tree, resultat, titre)
        if K_rat is not None:
            return _fin_fraction(chaine, s, A, K_rat, None, resultat, titre)
        return _fin_fraction_logarithmes_definition(chaine, s, c, resultat, titre)

    titre = "Logarithme des deux membres"
    lb, lc = Log(s.noeud, E() if ln else None), Log(s.second, E() if ln else None)
    chaine.ajouter(Eq(Log(_exponentielle(s), E() if ln else None), lc), "⇔", PROP_LN_DEUX_MEMBRES if ln else PROP_LOG_DEUX_MEMBRES)
    chaine.ajouter(Eq(Op("*", A, lb), lc), "⇔", PROP_LN_PUISSANCE if ln else PROP_LOG_PUISSANCE)
    if s.genre == "racine":
        if s.base in ("e", F(10)):
            K_tree = lc
            chaine.ajouter(Eq(A, lc), "⇔", PROP_CAR_LN_E if ln else PROP_CAR_LOG_10)
        else:
            K_tree = Op("/", lc, lb)
            chaine.ajouter(Eq(A, K_tree), "⇔", Car(lb))
        return _fin_racine(chaine, s, None, K_tree, resultat, titre)
    if s.base in ("e", F(10)):
        chaine.ajouter(Eq(A, lc), "⇔", PROP_CAR_LN_E if ln else PROP_CAR_LOG_10)
        return _fin_fraction_logarithmes_definition(chaine, s, c, resultat, titre)
    return _fin_fraction_logarithmes(chaine, s, resultat, titre, c)


def _fin_fraction_logarithmes_definition(chaine, s, c, resultat, titre):
    """b^(N/D) = c avec b = 10 ou e (définition du logarithme) : N/D = log(c) ⇒ N = D·log(c), puis la fin de la méthode B de la 3C."""
    x = s.x
    N, D = _frac(s.exposant)
    ln = s.base == "e"
    cle = "e" if ln else F(10)
    lc = Log(s.second, E() if ln else None)
    if len(N) == 1 and D == [0, 1]:
        return _x_egal_quotient(chaine, s, N, None, lc, resultat, titre)
    chaine.ajouter(Eq(_arbre_poly(N, x), Op("*", _arbre_poly(D, x), lc)), "⇔", PROP_FOIS_DENOMINATEURS)
    a_c = None if c == cle else c
    monos_g = [(n, k, None) for k, n in enumerate(N) if n != 0]
    monos_d = [(dk, k, a_c) for k, dk in enumerate(D) if dk != 0]
    ecrit = {} if a_c is None else {a_c: s.second}
    suite, solutions, remarque = _fin_beta(chaine, monos_g, monos_d, x, ecrit, ln)
    return resultat([_carte(titre, suite)], solutions, remarque)


def reconnu_exposant(g, d, x):
    """Vrai pour une équation exponentielle à exposant 1/x, √x ou ± ln x que l'outil sait lire, qu'il la résolve ou non."""
    try:
        _situation(g, d, x)
        return True
    except _Hors:
        return False


@_avec_decimaux
def variantes_exposant(g, d, x):
    """{méthode: résultat} d'une équation exponentielle dont l'exposant n'est pas un polynôme (6/x, √x, ln x), avec la carte « Ensemble de définition »
    en tête et la « Vérification » ; None si l'équation n'est pas de cette forme."""
    try:
        s = _situation(g, d, x)
        ed = ensemble_de_definition(g, d, x, general=True)
        return {m: _avec_ed_et_verification(ed, _methode_exposant(s, m), x) for m in METHODES}
    except _Hors:
        return None


# =====================================================================
# 4 quinquies. BASE POLYNOMIALE : log_(2x)(1296) = 4, log_(5x)(1000) = 3, log_(x+1)(5) = 16 (T36, partie C)
# =====================================================================
def _puissance(base, m):
    return base if m == 1 else Pow(base, Nb(m))


def _x_selon_la_base(b, valeur_base, valeur_exacte):
    """x tel que b0 + b1·x = valeur_base (un arbre sans inconnue ; `valeur_exacte` : sa valeur rationnelle ou None) ; b = [b0, b1]."""
    b0, b1 = b
    if valeur_exacte is not None:
        return _nb_exact((valeur_exacte - b0) / b1)
    haut = valeur_base if b0 == 0 else Op("-", valeur_base, _nb_exact(b0)) if b0 > 0 else Op("+", valeur_base, _nb_exact(-b0))
    return haut if b1 == 1 else Op("/", haut, _nb_exact(b1))


@_avec_decimaux
def base_polynomiale(g, d, x):
    """Le corrigé de log_B(n) = k où B est du 1er degré en x (2x, 5x, x + 1), n un rationnel > 0 et k un entier non nul : l'exponentielle des deux membres
    B^(log_B(n)) = B^k, n = B^k, puis B = ±n^(1/k) et x. None quand la forme n'est pas celle-là (pas encore)."""
    try:
        return _base_polynomiale(g, d, x)
    except _Hors:
        return None


def _base_polynomiale(g, d, x):
    enonce = Eq(g, d)
    if variables(g) and not variables(d):
        s, o, inverse = g, d, False
    elif variables(d) and not variables(g):
        s, o, inverse = d, g, True
    else:
        raise _Hors
    k = _const(o)
    if not isinstance(s, Log) or k is None or s.base is None or isinstance(s.base, (E, Var)) or not variables(s.base):
        raise _Hors
    n = _const(s.a)
    if variables(s.a) or n is None or n <= 0:
        raise _Hors
    b = _pq(s.base)
    if len(b) != 2 or k.denominator != 1 or k == 0 or abs(k) > 16:
        raise _Hors
    B, X, k = s.base, Var(x), int(k)
    m = abs(k)
    chaine = Chaine([enonce])
    if inverse:
        chaine.ajouter(Eq(s, o), "⇔")
    chaine.ajouter(Eq(Pow(B, s), _puissance(B, k) if k > 0 else Pow(B, Nb(k))), "⇔", PROP_EXPONENTIELLE)          # B^(log_B(n)) = B^k
    chaine.ajouter(Eq(_nb_exact(n), Pow(B, Nb(k)) if k != 1 else B), "⇔", PROP_EXP_LOG_BASE)
    if k < 0:                                                         # n = B^(−m) = 1/B^m ⇔ B^m = 1/n
        chaine.ajouter(Eq(_nb_exact(n), Op("/", Nb(1), _puissance(B, m))), "⇔", PROP_PUISSANCE_NEGATIVE)
        chaine.ajouter(Eq(_puissance(B, m), _nb_exact(1 / n)), "⇔")
        n = 1 / n
    racine = _racine_entiere(n, m)
    if racine is not None:
        rho = _nb_exact(racine)
        if m > 1 and not (k < 0):
            chaine.ajouter(Eq(Pow(rho, Nb(m)), _puissance(B, m)), "⇔")      # 1296 = 6^4 : le premier membre réécrit en puissance
    else:
        rho = Fn("sqrt", _nb_exact(n)) if m == 2 else Pow(_nb_exact(n), Nb(F(1, m)))
    valeur_rho = racine
    if m % 2 == 0:
        negatif = Neg(rho) if racine is None else _nb_exact(-racine)
        chaine.ajouter(Ou([Eq(B, negatif), Eq(B, rho)]), "⇔", PROP_RACINE_PAIRE)
        candidats = [(negatif, None if racine is None else -racine), (rho, valeur_rho)]
    else:
        if m > 1 or k < 0:
            chaine.ajouter(Eq(B, rho), "⇔", PROP_RACINE_IMPAIRE)
        candidats = [(rho, valeur_rho)]
    solutions = [_x_selon_la_base(b, v, e) for v, e in candidats]
    solutions.sort(key=valeur)
    lignes = [chaine]
    if all(_const(t) is not None for t in solutions):
        if len(solutions) == 1:
            chaine.ajouter(Eq(X, solutions[0]), "⇔")
        else:
            chaine.ajouter(Ou([Eq(X, t) for t in solutions]), "⇔")
    else:
        lignes.append(Chaine([Ou([Eq(X, t) for t in solutions])]) if len(solutions) > 1 else Chaine([Eq(X, solutions[0])]))
    return {"genre": "logarithmique", "inconnue": x, "enonce": enonce, "base": None, "etapes": [_carte("Exponentielle des deux membres", lignes)],
            "solutions": solutions, "remarque": None}


# =====================================================================
# 5. CORRIGÉ D'UNE ÉQUATION LOGARITHMIQUE EN FILIÈRE M
# =====================================================================
def _nommer_racines(r):
    """Deux racines irrationnelles (x = (1 − √41)/2 ou x = (1 + √41)/2) : x₁ et x₂ portent un nom, comme pour le discriminant en 3C, pour que la ligne
    « S = {x₁ ; x₂}, soit x ≈ … » tienne à 360 px. Sans effet si la ligne « x = … ou x = … » n'est pas dans les cartes."""
    sols = r["solutions"]
    if not sols or len(sols) != 2 or any(_const(s) is not None or isinstance(s, Defini) for s in sols):
        return r
    noms = [Defini("x_{1}", sols[0]), Defini("x_{2}", sols[1])]
    etapes, trouve = [], False
    for c in r["etapes"]:
        if c.get("lignes"):
            nouvelles = []
            for ligne in c["lignes"]:
                if (isinstance(ligne, Chaine) and len(ligne.elements) == 1 and isinstance(ligne.elements[0], Ou)
                        and [tex(e.d) for e in ligne.elements[0].eqs] == [tex(s) for s in sols]):
                    nouvelles += [Chaine([Eq(n, n.arbre)]) for n in noms]
                    trouve = True
                else:
                    nouvelles.append(ligne)
            c = {**c, "lignes": nouvelles}
        etapes.append(c)
    return {**r, "etapes": etapes, "solutions": noms} if trouve else r


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
    r = logarithmique_m(g, d, x) or regrouper(g, d, x) or base_polynomiale(g, d, x)
    if r is None:
        return None
    return _avec_ed_et_verification(ed, r, x)


def _avec_ed_et_verification(ed, r, x):
    """Le corrigé complet : la carte « Ensemble de définition », les cartes de la résolution `r`, puis la carte « Vérification » des solutions
    contre l'ensemble de définition (rien à vérifier quand la méthode ne s'applique pas ou qu'il n'y a aucune solution)."""
    if ed.vide:
        etapes = [_carte_ed(ed, [Message("L'ensemble de définition est vide : l'équation n'a aucune solution.")])]
        return {"genre": "logarithmique", "inconnue": x, "enonce": None, "base": None, "etapes": etapes, "solutions": [], "remarque": None,
                "ed": ed, "besoin_sympy": ed.besoin_sympy}
    r = _nommer_racines(r)
    etapes = [_carte_ed(ed)] + [dict(c) for c in r["etapes"]]
    if r["remarque"] and etapes[-1].get("lignes") is not None:
        etapes[-1]["lignes"] = list(etapes[-1]["lignes"]) + [Message(r["remarque"])]
    retenues, autres = r["solutions"], {"candidats": r["solutions"]}
    if r["solutions"] is None:                         # l'égalité est vraie sur tout l'ensemble de définition : S = ED
        autres["ensemble"] = r.get("ensemble", ed.ed_tex)
    elif r["solutions"]:
        retenues, lignes = verification(ed, r["solutions"], x)
        etapes.append(_carte("Vérification", lignes))
        if len(retenues) == 1 and isinstance(retenues[0], Defini):         # une seule solution gardée : sa valeur exacte, pas son nom (S = {(1 + √41)/2})
            retenues = [retenues[0].arbre]
    return {**r, **autres, "etapes": etapes, "solutions": retenues, "remarque": None, "ed": ed, "besoin_sympy": ed.besoin_sympy}


# =====================================================================
# 7. EXERCICES AU HASARD (pool M) : construits à l'envers, solutions entières ou rationnelles simples, souvent une solution rejetée
# =====================================================================
NIVEAUX_M = ("exponentielle", "definition", "sommes", "egalite", "variable", "difficile")
POIDS_M = (("exponentielle", .25), ("definition", .15), ("sommes", .20), ("egalite", .15), ("variable", .15), ("difficile", .10))


def _lin(p, q, x="x"):
    """px + q comme on l'écrit : x, -x, 2x+1, x-3, -x+11, 5 (p = 0)."""
    t = "" if p == 0 else x if p == 1 else "-" + x if p == -1 else f"{p}{x}"
    if q == 0 and t:
        return t
    return f"{t}{q:+d}" if t else str(q)


def _poly2(c0, c1, c2=1):
    """c2·x² + c1·x + c0 : x^2-x+4, x^2+5x-6, 2x^2-3."""
    t = "x^2" if c2 == 1 else "-x^2" if c2 == -1 else f"{c2}x^2"
    if c1:
        t += "+x" if c1 == 1 else "-x" if c1 == -1 else f"{c1:+d}x"
    return t + (f"{c0:+d}" if c0 else "")


def _log(base, arg):
    return f"log({arg})" if base == 10 else f"ln({arg})" if base == "e" else f"log_{base}({arg})"


def _g_exponentielle(rng):
    """Les tirages exponentiels du pool C (facile, moyen, logarithme : sans logarithme de l'inconnue)."""
    from exp_log import _GABARITS
    for _ in range(100):
        e = _GABARITS[rng.choice(["facile", "moyen", "logarithme", "logarithme"])](rng)
        if "log" not in e and "ln" not in e:
            return e
    return "2^x=8"


def _g_definition(rng):
    forme = rng.choice(["lineaire", "lineaire", "ln", "trinome", "base"])
    if forme == "lineaire":                              # log_a(px + q) = c, solution entière
        a, c = rng.choice([(2, 3), (2, 4), (2, 5), (3, 2), (3, 3), (5, 2), (10, 1), (10, 2)])
        p, x0 = rng.randint(1, 4), rng.randint(-3, 8)
        return f"{_log(a, _lin(p, a ** c - p * x0))}={c}"
    if forme == "ln":                                    # ln(px + q) = c : x = (e^c − q)/p
        return f"ln({_lin(rng.randint(1, 3), rng.randint(-5, 5))})={rng.randint(1, 3)}"
    if forme == "trinome":                               # log(x² + bx + c0) = k, deux racines entières, toutes deux dans l'ED
        r1, r2 = sorted(rng.sample(range(-6, 7), 2))
        k = rng.choice([1, 2])
        return f"log({_poly2(r1 * r2 + 10 ** k, -(r1 + r2))})={k}"
    k = rng.choice([2, 3, 4])                            # base inconnue : log_x(m^k) = k
    m = rng.choice([2, 3, 4, 5] if k < 4 else [2, 3, 4])
    return f"log_x({m ** k})={k}"


def _g_sommes(rng):
    forme = rng.choice(["produit", "produit", "produit_ln", "difference", "log_a"])
    if forme == "difference":                            # log(x + m) − log(x − n) = 1, x = (10n + m)/9 entier
        n, x0 = rng.randint(1, 5), 0
        x0 = rng.randint(n + 1, n + 6)
        return f"log({_lin(1, 9 * x0 - 10 * n)})-log({_lin(1, -n)})=1"
    if forme == "produit_ln":                            # ln(x + a) + ln(x + b) = ln(k), k = (r + a)(r + b)
        a, b, r = rng.randint(-3, 3), rng.randint(-3, 3), rng.randint(1, 6)
        while r + a <= 0 or r + b <= 0 or a == b:
            a, b, r = rng.randint(-3, 3), rng.randint(-3, 3), rng.randint(1, 6)
        return f"ln({_lin(1, a)})+ln({_lin(1, b)})=ln({(r + a) * (r + b)})"
    base, c = (10, rng.choice([1, 2])) if forme == "produit" else rng.choice([(2, 3), (2, 4), (3, 2), (3, 3)])
    produit = base ** c
    m, n = rng.choice([(m, produit // m) for m in range(1, int(produit ** 0.5) + 1) if produit % m == 0])
    a = rng.randint(-3, 3)                               # (r + a)(r + b) = base^c avec r + a = m, r + b = n : l'autre racine est rejetée
    while m == n:                                        # deux arguments identiques : log(x + a) + log(x + a)
        m, n = rng.choice([(m, produit // m) for m in range(1, int(produit ** 0.5) + 1) if produit % m == 0])
    r = m - a
    return f"{_log(base, _lin(1, a))}+{_log(base, _lin(1, n - r))}={c}"


def _g_egalite(rng):
    forme = rng.choice(["carre", "carre", "constantes", "difference", "plus_un"])
    if forme == "carre":                                 # 2 log(x + a) = log(px + q), racines r1 et r2, la seconde souvent rejetée
        while True:
            a, r1, r2 = rng.randint(-4, 3), rng.randint(-3, 6), rng.randint(-6, 6)
            p, q = 2 * a + r1 + r2, a * a - r1 * r2
            if r1 + a > 0 and r1 != r2 and p != 0:
                return f"2log({_lin(1, a)})=log({_lin(p, q)})"
    if forme == "constantes":                            # log(x) = 2 log(m) + log(n) − log(r)
        m, n, r = rng.randint(2, 5), rng.randint(2, 7), rng.randint(2, 6)
        return f"log(x)=2log({m})+log({n})-log({r})"
    if forme == "difference":                            # log(x + a) − log(m) = log(px + q), x0 entier
        while True:
            m, p, x0, s = rng.randint(2, 5), rng.randint(-2, 3), rng.randint(-2, 6), rng.randint(1, 6)
            a, q = m * s - x0, s - p * x0
            if 1 - m * p != 0 and p != 0 and x0 + a > 0:
                return f"log({_lin(1, a)})-log({m})=log({_lin(p, q)})"
    while True:                                          # log(x + a) = log(px + q) + 1 : x + a = 10 (px + q)
        p, x0, s = rng.randint(2, 4), rng.randint(-3, 6), rng.randint(1, 5)
        a, q = 10 * s - x0, s - p * x0
        if 1 - 10 * p != 0:
            return f"log({_lin(1, a)})=log({_lin(p, q)})+1"


def _terme_puissance(coef, base_texte):
    """+3*2^x, -2^x, +5*4^x pour le terme coef·base^x (coef ≠ 0)."""
    signe = "+" if coef > 0 else "-"
    return signe + (base_texte if abs(coef) == 1 else f"{abs(coef)}*{base_texte}")


def _g_variable(rng):
    forme = rng.choice(["deux", "deux", "rejetee", "e", "decalage"])
    if forme == "decalage":                              # a^(x+k) + a^(−x) = a^k + 1 : t = 1 ou t = a^(−k), x = 0 ou x = −k
        a, k = rng.choice([(2, 1), (2, 2), (2, 3), (3, 1), (3, 2), (5, 1)])
        return f"{a}^(x+{k})+{a}^(-x)={a ** k + 1}"
    if forme == "e":                                     # e^(2x) − s·e^x + p = 0, t1 et t2 entiers positifs
        t1, t2 = sorted(rng.sample(range(1, 7), 2))
        return f"e^(2x){_terme_puissance(-(t1 + t2), 'e^x')}{t1 * t2:+d}=0"
    a = rng.choice([2, 3, 5])
    if forme == "deux":                                  # (a^x)² − (a^i + a^j)·a^x + a^(i+j) = 0
        i, j = sorted(rng.sample(range(0, 4 if a == 2 else 3), 2))
        t1, t2 = a ** i, a ** j
    else:                                                # une racine t = −m négative, rejetée : (a^x)² − (a^j − m)·a^x − m·a^j = 0
        j, m = rng.randint(1, 3 if a == 2 else 2), rng.randint(1, 4)
        while m == a ** j:                               # t² − p = 0 se réduirait à une exponentielle simple
            m = rng.randint(1, 4)
        t1, t2 = -m, a ** j
    s, p = t1 + t2, t1 * t2
    k = rng.choice([1, 1, 2, 3])                          # k·(t² − s·t + p) = 0
    carre = rng.choice([f"{a * a}^x", f"{a}^(2x)"])
    haut = (carre if k == 1 else f"{k}*{carre}") + (_terme_puissance(-k * s, f"{a}^x") if s else "") + f"{k * p:+d}"
    return haut + "=0"


def _g_difficile(rng):
    forme = rng.choice(["vide", "trois", "trois", "carre_m", "carre_m"])
    if forme == "vide":                                  # ED vide : x > −a et x < b avec b ≤ −a
        a = rng.randint(-6, -1)
        b = rng.randint(-5, -a)
        return f"log({_lin(1, a)})+log({b}-x)={rng.choice([0, 1])}"
    if forme == "trois":                                 # log(x + a) + log(x + b) = log(x + c) + log(k), (x + a)(x + b) = k (x + c)
        for _ in range(500):
            a, b, k, r1 = rng.randint(-3, 3), rng.randint(-3, 3), rng.randint(2, 5), rng.randint(1, 8)
            produit = (r1 + a) * (r1 + b)
            if produit % k == 0 and produit > 0 and r1 + a > 0 and r1 + b > 0:
                c = produit // k - r1
                if r1 + c > 0 and a + b - k != 0 and len({a, b, c}) == 3:
                    return f"log({_lin(1, a)})+log({_lin(1, b)})=log({_lin(1, c)})+log({k})"
    for _ in range(1000):                                # log(x² − m) = 2 log(x + n), x = −(m + n²)/(2n)
        n, m = rng.randint(1, 4), rng.randint(-3, 9)
        x0 = F(-(m + n * n), 2 * n)
        if x0 + n > 0 and x0 * x0 > m and m > -10:
            return f"log({_poly2(-m, 0)})=2log({_lin(1, n)})"
    return "log(x^2-7)=2log(x+3)"


_GABARITS_M = {"exponentielle": _g_exponentielle, "definition": _g_definition, "sommes": _g_sommes, "egalite": _g_egalite,
               "variable": _g_variable, "difficile": _g_difficile}


def exercice_m(niveau, graine):
    """Exercice de la filière M (NIVEAUX_M), déterministe : la même graine donne le même énoncé. Renvoie {ok, expr, niveau}."""
    if niveau not in _GABARITS_M:
        return {"ok": False, "erreur": "Niveau d'exercice inconnu."}
    return {"ok": True, "expr": _GABARITS_M[niveau](random.Random(f"M:{niveau}:{graine}")), "niveau": niveau}
