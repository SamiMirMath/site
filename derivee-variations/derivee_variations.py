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
    lire, tex, par, prec, valeur_constante, Num, Iv, REELS, inter, ens_tex, points, contient, proche,
    preimage, resoudre_general, json_strict, ajouter_saisie, domaine, fusion, evaluer, aplatir, qtex,
    indice_racine, _sympy, en_sympy, en_sympy_reel, arbre_depuis_sympy, num_sympy, _SP,
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


def _produit(facteurs):
    out = facteurs[0]
    for f in facteurs[1:]:
        out = Op("*", out, f)
    return out


def _en_quotient(n):
    """Écrit f' en un seul quotient numérateur / dénominateur : coefficient rationnel réparti
    (2/3 · 1/∛x → 2/(3∛x)), exposants négatifs au dénominateur, signe au numérateur. Les facteurs
    gardent leur ordre. Une expression déjà sans fraction (coefficient entier, exposants positifs)
    est laissée telle quelle."""
    try:
        c, facs = aplatir(n)
    except Exception:
        return n
    if c == 0 or (c.denominator == 1 and all(k > 0 for _, k in facs)):
        return n

    def puiss(h, k):
        q = indice_racine(h)
        if q is not None:           # (racine q-ième de u)^k s'écrit u^(k/q) (tex : racine q-ième de u^k)
            e = F(k, q)
            return h.a if e == 1 else Op("^", h.a, Nb(e))
        return h if k == 1 else Op("^", h, Nb(F(k)))
    haut = [puiss(h, k) for h, k in facs if k > 0]
    bas = [puiss(h, -k) for h, k in facs if k < 0]
    if abs(c.numerator) != 1 or not haut:
        haut.insert(0, Nb(F(abs(c.numerator))))
    if c.denominator != 1:
        bas.insert(0, Nb(F(c.denominator)))
    N = _produit(haut)
    if c < 0:
        N = Neg(N)
    return Op("/", N, _produit(bas)) if bas else N


def _simplifier(n):
    """Met f' en forme factorisée (jamais développée) : plus facile à lire, et les
    zéros s'y lisent directement — c'est la convention demandée pour la suite. Le résultat
    est écrit en un quotient numérateur / dénominateur (_en_quotient)."""
    sp = _sympy()
    if sp is None:
        return _en_quotient(_nettoyer(n))
    try:
        return _en_quotient(_nettoyer(arbre_depuis_sympy(sp.factor(en_sympy(n)))))
    except Exception:
        return _en_quotient(_nettoyer(n))


# =====================================================================
# Dérivation narrée
# =====================================================================
F_PRIME = "f'(x)"


def _etiquette(n):
    """Nom de la dérivée d'un morceau de f dans la narration : (morceau)'."""
    return r"\left(" + tex(n) + r"\right)'"


def _facteur_constant(c, g, forme, items, top, etiq):
    """c·g, g·c ou g/c (c constant) : on dérive g (narration sous le nom (g)'),
    puis, si cette narration a produit des lignes, on conclut pour ce niveau."""
    avant = len(items)
    dg = derivee_narree(g, items, top=top, etiq=_etiquette(g))
    if forme == "c*g":
        resultat, ecrit = _simplifier(_mul(c, dg)), rf"{par(c, 2)} \cdot {_etiquette(g)}"
    elif forme == "g*c":
        resultat, ecrit = _simplifier(_mul(dg, c)), rf"{_etiquette(g)} \cdot {par(c, 2)}"
    else:
        resultat, ecrit = _simplifier(_div(dg, c)), rf"\dfrac{{{_etiquette(g)}}}{{{tex(c)}}}"
    if top and len(items) > avant:
        items.append(txt(rf"\({etiq} = {ecrit} = {tex(resultat)}\)."))
    return resultat


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


def _derivee_somme(n, items, top, etiq=F_PRIME):
    termes = _termes(n)
    if top and len(termes) > 1:
        items.append(txt("La dérivée d'une somme (ou différence) est la somme (ou différence) des "
                         "dérivées : on dérive terme à terme."))
    parties = [(signe, derivee_narree(t, items, top=top, etiq=_etiquette(t) if len(termes) > 1 else etiq))
               for signe, t in termes]
    resultat = parties[0][1] if parties[0][0] > 0 else Neg(parties[0][1])
    for signe, dt in parties[1:]:
        resultat = _add(resultat, dt) if signe > 0 else _sub(resultat, dt)
    if not top:
        return resultat
    resultat = _simplifier(resultat)
    if len(termes) > 1:
        items.append(txt(rf"\({etiq} = {tex(resultat)}\)."))
    return resultat


def _derivee_produit(n, items, top, etiq=F_PRIME):
    a, b = n.a, n.b
    ca, cb = valeur_constante(a), valeur_constante(b)
    if ca is not None and cb is not None:
        return Nb(0)
    if ca is not None:
        return _facteur_constant(a, b, "c*g", items, top, etiq)
    if cb is not None:
        return _facteur_constant(b, a, "g*c", items, top, etiq)
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
    items.append(txt(rf"\({etiq} = u'(x)v(x) + u(x)v'(x) = {tex(brut)} = {tex(simplifie)}\)."))
    return simplifie


def _derivee_quotient(n, items, top, etiq=F_PRIME):
    a, b = n.a, n.b
    cb = valeur_constante(b)
    if cb is not None:
        return _facteur_constant(b, a, "g/c", items, top, etiq)
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
    items.append(txt(rf"\({etiq} = \dfrac{{u'(x)v(x) - u(x)v'(x)}}{{v(x)^2}} = {tex(brut)} = {tex(simplifie)}\)."))
    return simplifie


def derivee_narree(n, items, top=True, etiq=F_PRIME):
    """Dérivée de n, avec narration dans items. `etiq` est le nom (tex) sous lequel
    la narration de ce niveau annonce son résultat : f'(x) pour f elle-même,
    (morceau)' pour un terme de somme ou ce qui suit un facteur constant."""
    if isinstance(n, (Nb, E)):
        return Nb(0)
    if isinstance(n, X):
        return Nb(1)
    if isinstance(n, Neg):
        if not top:
            return Neg(derivee_narree(n.a, items, top))
        avant = len(items)
        resultat = Neg(derivee_narree(n.a, items, top, etiq=_etiquette(n.a)))
        if len(items) > avant:
            items.append(txt(rf"\({etiq} = -{_etiquette(n.a)} = {tex(_simplifier(resultat))}\)."))
        return resultat
    if isinstance(n, Fn):
        return _derivee_fn(n, items)
    if isinstance(n, Op):
        if n.op in ("+", "-"):
            return _derivee_somme(n, items, top, etiq)
        if n.op == "*":
            return _derivee_produit(n, items, top, etiq)
        if n.op == "/":
            return _derivee_quotient(n, items, top, etiq)
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
        fe = en_sympy_reel(f_tree)
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


def _aligner_sur(D, ED):
    """Les bornes de D obtenues numériquement (valeurs approchées) qui coïncident, à 1e-6 près,
    avec une borne exacte de l'ED sont remplacées par celle-ci : sinon un même point apparaît deux
    fois dans le tableau (≈ 0,2929 et (2 − √2)/2) et l'on prend l'un pour un point de l'ED."""
    exactes = [p for iv in ED for p in (iv.lo, iv.hi) if p is not None and not p.approx]

    def snap(p):
        if p is None or not p.approx:
            return p
        for e in exactes:
            if abs(e.val - p.val) <= 1e-6 * (1 + abs(e.val)):
                return e
        return p
    return fusion([Iv(snap(iv.lo), iv.lf, snap(iv.hi), iv.hf) for iv in D])


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

    res = ajouter_saisie({"ok": True, "f_tex": tex(f), "ed_tex": res_ed["ED_tex"]}, f)

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
    D = _aligner_sur(inter(ED, D_fprime), ED)
    res["domaine_etude_tex"] = ens_tex(D)

    # 1) On cherche d'abord les zéros de f' (candidats extrema) : narration explicite,
    # avant de dresser le tableau — c'est la méthode demandée.
    items_signe = []
    if ens_tex(D) != ens_tex(ED):
        res["ed_deriv_tex"] = ens_tex(D)
        items_signe.append(txt(
            rf"ED de f' : \(D_{{f'}} = {ens_tex(D)}\), différent de l'ED de f, \(D_f = {ens_tex(ED)}\). "
            "On étudie le signe de f' sur cet ensemble ; là où f est définie mais pas f', "
            "on regarde directement le signe de part et d'autre."))
    items_signe.append(txt("On cherche d'abord les zéros de f'(x) : on résout f'(x) = 0."))
    n_intro = len(items_signe)
    numerateur = fprime.a if isinstance(fprime, Op) and fprime.op == "/" else fprime
    cn = valeur_constante(numerateur)
    try:
        if cn is not None and cn != 0 and numerateur is not fprime:
            # f' = c / D avec c constante non nulle : aucun zéro, rien à résoudre
            items_signe.append(txt(rf"Le numérateur de f' vaut \({qtex(cn)}\) : il ne s'annule jamais, "
                                   r"f' n'a aucun zéro (les valeurs interdites viennent du dénominateur)."))
            Z = []
        else:
            Z = preimage(fprime, points([Num.rat(0)]), items_signe)
    except NonPrisEnCharge:
        items_signe = items_signe[:n_intro]
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
    # Une colonne n'existe que pour un point de l'ED ou une borne de l'ED : un point critique situé
    # au milieu d'une zone hors de l'ED (0 pour ln(x²−4)) n'est pas un point d'étude.
    ed_ivs = fusion(ED)

    def _borne_de_ed(pt):
        return any(b is not None and proche(b.val, pt.val) for iv in ed_ivs for b in (iv.lo, iv.hi))
    crit = [pt for pt in crit if contient(ED, pt.val) or _borne_de_ed(pt)]
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

    # Intervalles hors de l'ED de f : ni signe ni flèche, case barrée (« x ») sur toutes les lignes.
    # Chaque intervalle entre deux points critiques est entièrement dans l'ED ou entièrement dehors
    # (les bornes de l'ED sont des points critiques).
    hors = [not contient(ED, _test(i)) for i in range(k + 1)]

    def _dans_zone_hors(j):
        """Case j du tableau (intervalle si j pair, point critique si j impair) entièrement hors de l'ED :
        un point critique ne l'est que si l'intervalle de chaque côté l'est."""
        return hors[j // 2] if j % 2 == 0 else (hors[(j - 1) // 2] and hors[(j + 1) // 2])

    def _barrer(cells):
        """Zone hors de l'ED : hachurée (« x »). Valeur interdite de f (borne hors de l'ED) : double barre
        « || » sur toute la colonne, quelle que soit la ligne (facteurs, f', f)."""
        out = []
        for j, c in enumerate(cells):
            if _dans_zone_hors(j):
                out.append("x")
            elif j % 2 == 1 and not contient(ED, crit[j // 2].val):
                out.append("||")
            else:
                out.append(c)
        return out

    lignes = []
    if c_const < 0:
        lignes.append({"label": qtex(c_const), "cells": _barrer(["-"] * (2 * k + 1))})
    for h, expo in facs:
        label = tex(h) if prec(h) >= 3 else r"\left(" + tex(h) + r"\right)"
        if abs(expo) > 1:
            if indice_racine(h) is not None:
                label = r"\left(" + label + r"\right)"
            label += "^{" + str(abs(expo)) + "}"
        if expo < 0:
            label += r"\ (\text{dén.})"
        cells = []
        for i in range(k + 1):
            cells.append(_cellule(evaluer(h, _test(i)), expo))
            if i < k:
                cells.append(_cellule(evaluer(h, crit[i].val), expo))
        lignes.append({"label": label, "cells": _barrer(cells)})

    combinee = []
    for i in range(k + 1):
        colonne = [l["cells"][2 * i] for l in lignes]
        combinee.append("x" if "x" in colonne else "||" if "||" in colonne else "0" if "0" in colonne else
                         ("-" if colonne.count("-") % 2 else "+"))
        if i < k:
            colonne = [l["cells"][2 * i + 1] for l in lignes]
            combinee.append("x" if "x" in colonne else "||" if "||" in colonne else "0" if "0" in colonne else
                             ("-" if colonne.count("-") % 2 else "+"))
    # f' identiquement nulle (f constante sur chaque morceau de son ED) : « 0 » sur chaque
    # intervalle de l'ED, « || » aux valeurs interdites, hors de l'ED la case est barrée.
    f_constante = valeur_constante(fprime) == 0
    if f_constante:
        for i in range(2 * k + 1):
            if i % 2 == 0:
                combinee[i] = "x" if hors[i // 2] else "0" if contient(D, _test(i // 2)) else "x"
            else:
                combinee[i] = "x" if _dans_zone_hors(i) else "0" if contient(D, crit[i // 2].val) else "||"
    lignes.append({"label": "f'(x)", "cells": combinee, "final": True})

    res["signe_resolu"] = True
    res["signe_etapes"] = items_signe
    res["table_signe"] = {"var": "x", "crit": [p.tex for p in crit], "rows": lignes}

    # 4) Variations : une flèche par intervalle ; en chaque point critique de l'ED de f :
    #  - extremum (i) : point intérieur de l'ED où f' change de signe (même si f' n'y est pas définie) ;
    #  - extremum (ii) : borne fermée de l'ED, nature donnée par le sens de variation de
    #    l'intervalle adjacent (Q3, 14.10.2026) ;
    #  - jamais sur un intervalle où f est constante ; jamais hors de l'ED.
    # Là où f est définie mais pas f' (ou f constante), la ligne f(x) porte la valeur f(a), sans barre.
    def _bornes_fermees(pt):
        gauche = any(iv.lo is not None and iv.lf and proche(iv.lo.val, pt.val) for iv in ed_ivs)
        droite = any(iv.hi is not None and iv.hf and proche(iv.hi.val, pt.val) for iv in ed_ivs)
        return gauche, droite

    memo = {}

    def _valeur_en(pt):
        if pt.val not in memo:
            valeur = None if pt.approx else _valeur_exacte(f, pt)
            if valeur is None:
                v = _valeur_num(f, pt.val)
                memo[pt.val] = (v, Num.approche(v).tex if v is not None else "?")
            else:
                memo[pt.val] = (valeur.val, valeur.tex)
        return memo[pt.val]

    fleche_cells, extrema = [], []
    for i in range(k + 1):
        s = combinee[2 * i]
        fleche_cells.append({"+": r"\nearrow", "-": r"\searrow", "0": r"\rightarrow", "x": "x"}.get(s, ""))
        if i >= k:
            continue
        p = crit[i]
        if not contient(ED, p.val):
            fleche_cells.append("x" if _dans_zone_hors(2 * i + 1) else "asym")
            continue
        s_droite = combinee[2 * i + 2]
        gauche, droite = _bornes_fermees(p)
        genre = None
        if gauche != droite:   # borne fermée de l'ED : intervalle adjacent à l'intérieur de l'ED
            if gauche:
                genre = {"+": "minimum local", "-": "maximum local"}.get(s_droite)
            else:
                genre = {"+": "maximum local", "-": "minimum local"}.get(s)
        elif not gauche and s in ("+", "-") and s_droite in ("+", "-") and s != s_droite:
            # "local" : un changement de signe de f' donne un extremum local
            genre = "maximum local" if s == "+" else "minimum local"
        if genre is not None:
            v, valeur_tex = _valeur_en(p)
            extrema.append({"genre": genre, "x_tex": p.tex, "f_tex": valeur_tex,
                            "x_val": p.val, "f_val": v})
        if not contient(D, p.val) or f_constante:
            v, valeur_tex = _valeur_en(p)
            fleche_cells.append("val:" + valeur_tex)
        else:
            fleche_cells.append("extremum" if genre is not None else "")

    if f_constante:
        res["f_constante"] = True
    lignes.append({"label": "f(x)", "cells": fleche_cells, "variation": True})
    res["extrema"] = extrema

    return res


def etudier_json(entree):
    return json_strict(etudier(entree))


if __name__ == "__main__":
    import sys
    for arg in sys.argv[1:] or ["(x^2-1)/(x-3)"]:
        r = etudier(arg)
        print(json.dumps(r, ensure_ascii=False, indent=2))
        print("=" * 60)
