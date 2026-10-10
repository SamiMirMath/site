"""
derivee_variations.py — Dérivée, signe de f' et tableau de variations.

Réutilise ensemble_def.py (parseur, arbre syntaxique, moteur de tableaux de signes,
système de valeurs exactes, pont SymPy) : ce fichier ne refait pas cette
infrastructure, il la complète avec la dérivation.

Convention pédagogique (décidée avec l'enseignant) :
  - Somme/différence : on dérive terme à terme (règle de linéarité), sans tableau.
  - Produit u·v ou quotient u/v (facteurs non constants) : on nomme u et v dans un
    petit tableau (u, u', v, v'), puis on applique la formule — UNIQUEMENT au premier
    niveau (f lui-même, ou chaque terme d'une somme). Les dérivées internes de u et v
    sont calculées directement, sans sous-tableau imbriqué.
  - Composée (ln(u), e^u, √u, u^n) : PAS de tableau — la fonction interne u et sa
    dérivée interne u' sont nommées dans la même phrase que le résultat, de façon
    implicite, comme à l'examen. C'est volontaire : ne pas « spoiler » l'étape de la
    dérivée interne derrière un tableau séparé, qui est justement le point sur lequel
    les élèves bloquent (ex. f(x) = e^{2x} ⟹ f'(x) = 2 e^{2x}).
  - Le calcul brut n'est jamais refait par SymPy : la RÈGLE appliquée et sa narration
    sont écrites à la main. SymPy n'intervient qu'en appoint, pour mettre le résultat
    final au même dénominateur / le simplifier (comme ailleurs dans ensemble_def.py),
    jamais pour décider quelle règle utiliser.
"""
import json

from fractions import Fraction as F

from ensemble_def import (
    Nb, X, E, Neg, Op, Fn,
    lire, tex, prec, valeur_constante, Num, Iv, REELS, inter, ens_tex, points, contient, proche,
    preimage, resoudre_general, domaine, evaluer, aplatir, qtex,
    _sympy, en_sympy, arbre_depuis_sympy, num_sympy, _SP,
    txt, NonPrisEnCharge, ErreurSaisie, _analyser, apercu_json,
)

__all__ = ["etudier", "etudier_json", "apercu_json"]


# =====================================================================
# Petits constructeurs d'arbre
# =====================================================================
def _c(v):
    return Nb(v)


def _add(a, b):
    return Op("+", a, b)


def _sub(a, b):
    return Op("-", a, b)


def _mul(a, b):
    return Op("*", a, b)


def _div(a, b):
    return Op("/", a, b)


def _pow(a, b):
    return Op("^", a, b)


def _puiss_sure(u, k):
    """u^k en évitant les exposants 0 ou 1 inutiles à l'affichage."""
    if k == 0:
        return Nb(1)
    if k == 1:
        return u
    return _pow(u, Nb(k))


# =====================================================================
# Simplification d'appoint (SymPy) — jamais pour choisir la règle, seulement
# pour mettre en forme le résultat déjà obtenu à la main.
# =====================================================================
def _pos_et_signe(n):
    """Si n équivaut à -(reste) (Neg, nombre négatif, ou produit commençant par un
    facteur négatif), renvoie (reste positif, True). Sinon (n, False)."""
    if isinstance(n, Neg):
        return n.a, True
    if isinstance(n, Nb) and n.v < 0:
        return Nb(-n.v), True
    if isinstance(n, Op) and n.op == "*":
        g, ng = _pos_et_signe(n.a)
        if ng:
            if isinstance(g, Nb) and g.v == 1:
                return n.b, True
            return Op("*", g, n.b), True
    return n, False


def _nettoyer(n):
    """Après un aller-retour par SymPy, remet en forme « a + (-b) » en « a - b » et
    supprime les coefficients 1 superflus (SymPy ne fait pas toujours ce choix
    d'écriture, tex() ne le corrige pas tout seul)."""
    if isinstance(n, (Nb, X, E)):
        return n
    if isinstance(n, Neg):
        return Neg(_nettoyer(n.a))
    if isinstance(n, Fn):
        return Fn(n.nom, _nettoyer(n.a))
    if isinstance(n, Op):
        a, b = _nettoyer(n.a), _nettoyer(n.b)
        if n.op == "*":
            if isinstance(a, Nb) and a.v == 1:
                return b
            if isinstance(b, Nb) and b.v == 1:
                return a
            if isinstance(a, Neg) and isinstance(a.a, Nb) and a.a.v == 1:
                return Neg(b)
            if isinstance(b, Neg) and isinstance(b.a, Nb) and b.a.v == 1:
                return Neg(a)
            return Op("*", a, b)
        if n.op == "+":
            bp, neg = _pos_et_signe(b)
            return Op("-", a, bp) if neg else Op("+", a, b)
        return Op(n.op, a, b)
    return n


def _simplifier(n):
    """Met f' en forme factorisée (jamais développée) : plus facile à lire, et les
    zéros s'y lisent directement — c'est la convention demandée pour la suite."""
    sp = _sympy()
    if sp is None:
        return _nettoyer(n)
    try:
        return _nettoyer(arbre_depuis_sympy(sp.factor(en_sympy(n))))
    except Exception:
        return _nettoyer(n)


# =====================================================================
# Dérivation narrée
# =====================================================================
REGLE_FN_FORME = {"ln": r"\ln(u)", "exp": r"e^{u}", "sqrt": r"\sqrt{u}"}
REGLE_FN_TEX = {"ln": r"\frac{u'}{u}", "exp": r"u' e^{u}", "sqrt": r"\frac{u'}{2\sqrt{u}}"}


def _derivee_fn(n, items):
    u = n.a
    du = derivee_narree(u, items, top=False)
    if n.nom == "ln":
        resultat = _div(du, u)
    elif n.nom == "exp":
        resultat = _mul(du, Fn("exp", u))
    else:  # sqrt
        resultat = _div(du, _mul(Nb(2), Fn("sqrt", u)))
    resultat = _simplifier(resultat)
    if isinstance(u, X):
        items.append(txt(rf"\(\left({tex(n)}\right)' = {tex(resultat)}\) (règle de base)."))
    else:
        items.append(txt(
            rf"\({tex(n)}\) est de la forme \({REGLE_FN_FORME[n.nom]}\) avec "
            rf"\(u(x) = {tex(u)}\) (dérivée interne \(u'(x) = {tex(du)}\)) \(\Rightarrow\) "
            rf"\(\left({tex(n)}\right)' = {REGLE_FN_TEX[n.nom]} = {tex(resultat)}\)."
        ))
    return resultat


def _derivee_puissance(n, items):
    e = valeur_constante(n.b)
    if e is None:
        # cas général a^b, b non constant : a^b = e^{b ln a}
        da = derivee_narree(n.a, items, top=False)
        db = derivee_narree(n.b, items, top=False)
        resultat = _simplifier(_mul(n, _add(_mul(db, Fn("ln", n.a)), _mul(n.b, _div(da, n.a)))))
        items.append(txt(
            rf"\({tex(n)}\) s'écrit \(e^{{{tex(n.b)}\ln\left({tex(n.a)}\right)}}\) : on dérive cette forme "
            rf"composée \(\Rightarrow\) \(\left({tex(n)}\right)' = {tex(resultat)}\)."
        ))
        return resultat
    if valeur_constante(n.a) is not None:
        return Nb(0)
    u = n.a
    du = derivee_narree(u, items, top=False)
    reste = _puiss_sure(u, e - 1)
    resultat = _simplifier(_mul(_mul(Nb(e), reste), du)) if e != 1 else du
    if isinstance(u, X):
        items.append(txt(rf"\(\left({tex(n)}\right)' = {tex(resultat)}\) (règle de la puissance)."))
    else:
        items.append(txt(
            rf"\({tex(n)}\) est de la forme \(u^{{{tex(Nb(e))}}}\) avec \(u(x) = {tex(u)}\) "
            rf"(dérivée interne \(u'(x) = {tex(du)}\)) \(\Rightarrow\) "
            rf"\(\left({tex(n)}\right)' = {tex(Nb(e))}\,u^{{{tex(Nb(e - 1))}}}u' = {tex(resultat)}\)."
        ))
    return resultat


def _termes(n, signe=1, out=None):
    out = [] if out is None else out
    if isinstance(n, Op) and n.op in ("+", "-"):
        _termes(n.a, signe, out)
        _termes(n.b, signe if n.op == "+" else -signe, out)
    elif isinstance(n, Neg):
        _termes(n.a, -signe, out)
    else:
        out.append((signe, n))
    return out


def _derivee_somme(n, items, top):
    termes = _termes(n)
    if top and len(termes) > 1:
        items.append(txt("La dérivée d'une somme (ou différence) est la somme (ou différence) des "
                         "dérivées : on dérive terme à terme."))
    parties = [(signe, derivee_narree(t, items, top=top)) for signe, t in termes]
    resultat = parties[0][1] if parties[0][0] > 0 else Neg(parties[0][1])
    for signe, dt in parties[1:]:
        resultat = _add(resultat, dt) if signe > 0 else _sub(resultat, dt)
    if not top:
        return resultat
    resultat = _simplifier(resultat)
    if len(termes) > 1:
        items.append(txt(rf"\(f'(x) = {tex(resultat)}\)."))
    return resultat


def _derivee_produit(n, items, top):
    a, b = n.a, n.b
    ca, cb = valeur_constante(a), valeur_constante(b)
    if ca is not None and cb is not None:
        return Nb(0)
    if ca is not None:
        return _simplifier(_mul(a, derivee_narree(b, items, top=top)))
    if cb is not None:
        return _simplifier(_mul(derivee_narree(a, items, top=top), b))
    if top:
        items.append(txt(rf"On pose \(u(x) = {tex(a)}\) et \(v(x) = {tex(b)}\) : règle du produit, "
                         rf"\((uv)' = u'v + uv'\)."))
    ua = derivee_narree(a, items, top=False)
    ub = derivee_narree(b, items, top=False)
    if top:
        ua, ub = _simplifier(ua), _simplifier(ub)
        items.append(txt(rf"\(u'(x) = {tex(ua)}\)."))
        items.append(txt(rf"\(v'(x) = {tex(ub)}\)."))
    brut = _add(_mul(ua, b), _mul(a, ub))
    if not top:
        return brut
    simplifie = _simplifier(brut)
    items.append(txt(rf"\(f'(x) = u'(x)v(x) + u(x)v'(x) = {tex(brut)} = {tex(simplifie)}\)."))
    return simplifie


def _derivee_quotient(n, items, top):
    a, b = n.a, n.b
    cb = valeur_constante(b)
    if cb is not None:
        return _simplifier(_div(derivee_narree(a, items, top=top), b))
    if top:
        items.append(txt(rf"On pose \(u(x) = {tex(a)}\) et \(v(x) = {tex(b)}\) : règle du quotient, "
                         rf"\(\left(\frac{{u}}{{v}}\right)' = \frac{{u'v - uv'}}{{v^2}}\)."))
    ua = derivee_narree(a, items, top=False)
    ub = derivee_narree(b, items, top=False)
    if top:
        ua, ub = _simplifier(ua), _simplifier(ub)
        items.append(txt(rf"\(u'(x) = {tex(ua)}\)."))
        items.append(txt(rf"\(v'(x) = {tex(ub)}\)."))
    brut = _div(_sub(_mul(ua, b), _mul(a, ub)), _pow(b, Nb(2)))
    if not top:
        return brut
    simplifie = _simplifier(brut)
    items.append(txt(rf"\(f'(x) = \dfrac{{u'(x)v(x) - u(x)v'(x)}}{{v(x)^2}} = {tex(brut)} = {tex(simplifie)}\)."))
    return simplifie


def derivee_narree(n, items, top=True):
    if isinstance(n, (Nb, E)):
        return Nb(0)
    if isinstance(n, X):
        return Nb(1)
    if isinstance(n, Neg):
        return Neg(derivee_narree(n.a, items, top))
    if isinstance(n, Fn):
        return _derivee_fn(n, items)
    if isinstance(n, Op):
        if n.op in ("+", "-"):
            return _derivee_somme(n, items, top)
        if n.op == "*":
            return _derivee_produit(n, items, top)
        if n.op == "/":
            return _derivee_quotient(n, items, top)
        if n.op == "^":
            return _derivee_puissance(n, items)
    raise NonPrisEnCharge("dérivée non prise en charge pour ce nœud.")


# =====================================================================
# Signe de f', variations, extrema
# =====================================================================
def _valeur_exacte(f_tree, point):
    """f(point) en forme exacte (objet Num) si possible via SymPy, sinon None."""
    sp = _sympy()
    if sp is None or point.py is None:
        return None
    try:
        val = sp.sympify(point.py, locals={"sqrt": sp.sqrt, "exp": sp.exp, "log": sp.log, "pi": sp.pi})
        fe = en_sympy(f_tree)
        r = sp.simplify(fe.subs(_SP["x"], val))
        if r.is_real is False:
            return None
        return num_sympy(r)
    except Exception:
        return None


def _valeur_num(f_tree, x):
    try:
        return evaluer(f_tree, x)
    except Exception:
        return None


def etudier(entree):
    try:
        f = lire(entree)
    except ErreurSaisie as e:
        return {"ok": False, "erreur": str(e)}

    res_ed, _, ED = _analyser(entree)
    if not res_ed.get("ok"):
        return {"ok": False, "erreur": res_ed["erreur"]}
    if not res_ed.get("complet"):
        return {"ok": False, "erreur": "L'ensemble de définition n'a pas pu être calculé pour cette fonction."}

    res = {"ok": True, "f_tex": tex(f), "ed_tex": res_ed["ED_tex"]}

    items_deriv = []
    try:
        fprime = derivee_narree(f, items_deriv, top=True)
    except NonPrisEnCharge as e:
        res["deriv_resolu"] = False
        res["deriv_erreur"] = str(e)
        return res
    fprime = _simplifier(fprime)
    res["deriv_tex"] = tex(fprime)
    res["deriv_etapes"] = items_deriv
    res["deriv_resolu"] = True

    try:
        D_fprime = domaine(fprime)
    except Exception:
        D_fprime = REELS
    D = inter(ED, D_fprime)
    res["domaine_etude_tex"] = ens_tex(D)

    # 1) On cherche d'abord les zéros de f' (candidats extrema) : narration explicite,
    # avant de dresser le tableau — c'est la méthode demandée.
    items_signe = [txt("On cherche d'abord les zéros de f'(x) : on résout f'(x) = 0.")]
    try:
        Z = preimage(fprime, points([Num.rat(0)]), items_signe)
    except NonPrisEnCharge:
        items_signe = items_signe[:1]
        try:
            Z = resoudre_general(fprime, "=", items_signe)
        except Exception as e:
            res["signe_resolu"] = False
            res["signe_erreur"] = "Le signe de f'(x) n'a pas pu être étudié automatiquement : " + str(e)
            return res
    except Exception as e:
        res["signe_resolu"] = False
        res["signe_erreur"] = "Le signe de f'(x) n'a pas pu être étudié automatiquement : " + str(e)
        return res

    # 2) Points critiques = zéros de f' (ci-dessus) ∪ bornes finies du domaine d'étude
    # (valeurs interdites, asymptotes) — une seule liste, servant à la fois aux tests
    # de signe et aux valeurs exactes des extrema.
    crit = []

    def _ajouter(p):
        if p is not None and not any(proche(p.val, q.val) for q in crit):
            crit.append(p)

    for iv in Z:
        _ajouter(iv.lo)
        _ajouter(iv.hi)
    for iv in D:
        _ajouter(iv.lo)
        _ajouter(iv.hi)
    crit.sort(key=lambda p: p.val)
    k = len(crit)

    def _test(i):
        if k == 0:
            return 0.0
        if i == 0:
            return crit[0].val - 1
        if i == k:
            return crit[-1].val + 1
        return (crit[i - 1].val + crit[i].val) / 2

    # 3) Une ligne par facteur de f' (f' étant gardée factorisée, cf. plus haut), puis
    # la ligne combinée — même présentation qu'un tableau de signes « papier ».
    try:
        c_const, facs = aplatir(fprime)
    except Exception:
        c_const, facs = F(1), [(fprime, 1)]

    def _cellule(v, expo):
        if v is None:
            return "x"
        if abs(v) <= 1e-9:
            return "||" if expo < 0 else "0"
        s = "+" if v > 0 else "-"
        return "+" if (s == "-" and expo % 2 == 0) else s

    lignes = []
    if c_const < 0:
        lignes.append({"label": qtex(c_const), "cells": ["-"] * (2 * k + 1)})
    for h, expo in facs:
        label = tex(h) if prec(h) >= 3 else r"\left(" + tex(h) + r"\right)"
        if abs(expo) > 1:
            label += "^{" + str(abs(expo)) + "}"
        if expo < 0:
            label += r"\ (\text{dén.})"
        cells = []
        for i in range(k + 1):
            cells.append(_cellule(evaluer(h, _test(i)), expo))
            if i < k:
                cells.append(_cellule(evaluer(h, crit[i].val), expo))
        lignes.append({"label": label, "cells": cells})

    combinee = []
    for i in range(k + 1):
        colonne = [l["cells"][2 * i] for l in lignes]
        combinee.append("x" if "x" in colonne else "||" if "||" in colonne else "0" if "0" in colonne else
                         ("-" if colonne.count("-") % 2 else "+"))
        if i < k:
            colonne = [l["cells"][2 * i + 1] for l in lignes]
            combinee.append("x" if "x" in colonne else "||" if "||" in colonne else "0" if "0" in colonne else
                             ("-" if colonne.count("-") % 2 else "+"))
    lignes.append({"label": "f'(x)", "cells": combinee, "final": True})

    res["signe_resolu"] = True
    res["signe_etapes"] = items_signe
    res["table_signe"] = {"var": "x", "crit": [p.tex for p in crit], "rows": lignes}

    # 4) Variations : une flèche par intervalle, un extremum à chaque point critique où
    # le signe de f' change effectivement (sinon, asymptote/valeur interdite, ou zéro
    # sans changement de signe — pas d'extremum).
    fleche_cells, extrema = [], []
    for i in range(k + 1):
        s = combinee[2 * i]
        fleche_cells.append({"+": r"\nearrow", "-": r"\searrow"}.get(s, ""))
        if i >= k:
            continue
        p = crit[i]
        if not contient(D, p.val):
            fleche_cells.append("asym")
            continue
        s_droite = combinee[2 * i + 2]
        if s in ("+", "-") and s_droite in ("+", "-") and s != s_droite:
            # "local" : un changement de signe de f' donne un extremum local — les
            # bords du domaine (s'ils sont dans l'ED) sont à comparer séparément pour
            # un extremum global sur un compact.
            genre = "maximum local" if s == "+" else "minimum local"
            valeur = None if p.approx else _valeur_exacte(f, p)
            if valeur is None:
                v = _valeur_num(f, p.val)
                valeur_tex = Num.approche(v).tex if v is not None else "?"
            else:
                valeur_tex = valeur.tex
            extrema.append({"genre": genre, "x_tex": p.tex, "f_tex": valeur_tex})
            fleche_cells.append("extremum")
        else:
            fleche_cells.append("")

    lignes.append({"label": "f(x)", "cells": fleche_cells, "variation": True})
    res["extrema"] = extrema

    return res


def etudier_json(entree):
    return json.dumps(etudier(entree), ensure_ascii=False)


if __name__ == "__main__":
    import sys
    for arg in sys.argv[1:] or ["(x^2-1)/(x-3)"]:
        r = etudier(arg)
        print(json.dumps(r, ensure_ascii=False, indent=2))
        print("=" * 60)
