"""
derivee_variations.py — Dérivée, signe de f' et tableau de variations.

Réutilise ensemble_def.py (parseur, arbre syntaxique, moteur de tableaux de signes,
système de valeurs exactes, pont SymPy) : ce fichier ne refait pas cette
infrastructure, il la complète avec la dérivation.

Convention pédagogique :
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
from math import gcd

from noyau import (
    Nb, X, E, Neg, Op, Fn,
    lire, tex, par, prec, valeur_constante, Num, Iv, REELS, inter, ens_tex, points, contient, proche,
    preimage, resoudre_general, json_strict, ajouter_saisie, domaine, fusion, evaluer, aplatir, qtex,
    indice_racine, sans_x, charger_sympy, en_sympy, en_sympy_reel, arbre_depuis_sympy, num_sympy, SYMPY,
    txt, NonPrisEnCharge, ErreurSaisie, analyser_complet, apercu_json, signe_facteur, complement,
)

__all__ = ["etudier", "etudier_json", "apercu_json", "tableau_signes"]


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


def _epurer(n):
    """Supprime les opérations neutres d'une écriture non simplifiée (guide R11) : « + 0 », « - 0 », « · 1 »,
    « 1 · », « / 1 », « ^1 » ; un facteur 0 donne 0. Ne fait aucun autre calcul."""
    def est(m, v):
        return isinstance(m, Nb) and m.v == v
    if isinstance(n, Neg):
        return Neg(_epurer(n.a))
    if isinstance(n, Fn):
        return Fn(n.nom, _epurer(n.a))
    if not isinstance(n, Op):
        return n
    a, b = _epurer(n.a), _epurer(n.b)
    if n.op == "+":
        return a if est(b, 0) else b if est(a, 0) else Op("+", a, b)
    if n.op == "-":
        return a if est(b, 0) else Neg(b) if est(a, 0) else Op("-", a, b)
    if n.op == "*":
        if est(a, 0) or est(b, 0):
            return Nb(0)
        return b if est(a, 1) else a if est(b, 1) else Op("*", a, b)
    if n.op == "/":
        return Nb(0) if est(a, 0) else a if est(b, 1) else Op("/", a, b)
    if n.op == "^" and est(b, 1):
        return a
    return Op(n.op, a, b)


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


def _contient_x(n):
    if isinstance(n, X):
        return True
    if isinstance(n, Neg):
        return _contient_x(n.a)
    if isinstance(n, Fn):
        return _contient_x(n.a)
    if isinstance(n, Op):
        return _contient_x(n.a) or _contient_x(n.b)
    return False


def _ordre_naturel(n):
    """Ordre d'écriture des sommes : termes en x d'abord (ordre de SymPy), constantes ensuite, les
    constantes positives avant les négatives (« ln 3 − 1 », jamais « −1 + ln 3 ») ; si la somme
    commencerait par un moins, un terme positif passe devant (« 1 − ln 2·ln x »)."""
    if isinstance(n, Neg):
        return Neg(_ordre_naturel(n.a))
    if isinstance(n, Fn):
        return Fn(n.nom, _ordre_naturel(n.a))
    if not isinstance(n, Op):
        return n
    if n.op not in ("+", "-"):
        return Op(n.op, _ordre_naturel(n.a), _ordre_naturel(n.b))
    termes = [(sg, _ordre_naturel(t)) for sg, t in _termes(n)]
    termes = [(-sg, t2) if neg else (sg, t) for sg, t in termes for t2, neg in [_pos_et_signe(t)]]
    termes.sort(key=lambda st: (not _contient_x(st[1]) , (st[0] < 0) and not _contient_x(st[1])))
    if termes[0][0] < 0:                  # une somme ne commence pas par un moins : premier terme positif devant
        for i, st in enumerate(termes):
            if st[0] > 0:
                termes.insert(0, termes.pop(i))
                break
    out = termes[0][1] if termes[0][0] > 0 else Neg(termes[0][1])
    for sg, t in termes[1:]:
        out = Op("+" if sg > 0 else "-", out, t)
    return out


def _factoriser_avec_exp(sp, e):
    """factor(e) en gardant chaque exponentielle entière (décisions EC, D6) : factor développe e^(a + b) en e^a·e^b
    (e^{(x² + x − 2)/(6x − 12)} devenait trois exponentielles). On regroupe d'abord les produits d'exponentielles
    (powsimp), puis chaque e^a devient T^k, T symbole muet par famille d'exposants proportionnels (a = k·w, k entier :
    e^{2x} = T² si T = eˣ) ; on factorise, puis on remet e^w à la place de T. Le remplacement est exact."""
    e = sp.powsimp(e, combine="exp")
    familles = []                                    # [w0, [(exposant, rapport rationnel à w0)]]
    exposants = sorted((q.args[0] for q in e.atoms(sp.exp)), key=sp.default_sort_key)
    exposants.sort(key=lambda a: bool(a.could_extract_minus_sign()))      # base eˣ plutôt que e^{−x} (comme factor)
    for a in exposants:
        for fam in familles:
            r = sp.cancel(a / fam[0])
            if r.is_Rational and r != 0:
                fam[1].append((a, r))
                break
        else:
            familles.append([a, [(a, sp.Integer(1))]])
    if not familles:
        return sp.factor(e)
    remplacer, remettre = {}, {}
    for w0, membres in familles:
        g = sp.Rational(0)
        for _, r in membres:                         # pgcd des rapports rationnels : e^a = (e^w)^(r/g), r/g entier
            g = sp.Rational(sp.igcd(g.p * r.q, r.p * g.q), g.q * r.q) if g != 0 else abs(r)
        T = sp.Dummy("T")
        remettre[T] = sp.exp(w0 * g)
        for a, r in membres:
            remplacer[sp.exp(a)] = T ** int(r / g)
    c, facteurs = sp.factor(e.xreplace(remplacer)).as_coeff_mul()
    # facteur par facteur : un « −1 » reste devant le produit au lieu d'entrer dans la somme ((−e^{2x} − 1)·e^{−x})
    return c * sp.Mul(*[f.xreplace(remettre) for f in facteurs])


def _contient(n, cible):
    if n.key() == cible.key():
        return True
    if isinstance(n, (Neg, Fn)):
        return _contient(n.a, cible)
    if isinstance(n, Op):
        return _contient(n.a, cible) or _contient(n.b, cible)
    return False


def _oppose_somme(h):
    """−h pour une somme h, écrit comme une somme (−(eˣ − 3) = 3 − eˣ)."""
    termes = [(-sg, t) for sg, t in _termes(h)]
    out = termes[0][1] if termes[0][0] > 0 else Neg(termes[0][1])
    for sg, t in termes[1:]:
        out = Op("+" if sg > 0 else "-", out, t)
    return _ordre_naturel(out)


def _forme_du_corrige(n):
    """Formes du corrigé (décisions EC, D17), seulement là où l'écriture ne fait que changer de place un signe ou un facteur :
      - c·… avec c < 0 et un seul facteur somme non polynomial de puissance impaire, avec un terme négatif (eˣ − 3) : le signe
        entre dans ce facteur, −2(eˣ − 3)eˣ = 2(3 − eˣ)eˣ ; les facteurs polynomiaux (x − 3) restent tels quels (R7) ;
      - un facteur e^{u} seul passe devant le premier facteur somme qui le contient : 2eˣ(3 − eˣ) (« on met eˣ en évidence »).
    Dans un quotient, seul le numérateur est concerné. Sans changement, l'arbre est rendu tel quel."""
    if isinstance(n, Op) and n.op == "/":
        haut = _forme_du_corrige(n.a)
        return n if haut is n.a else Op("/", haut, n.b)
    try:
        c, facs = aplatir(n)
    except Exception:
        return n
    if c == 0 or c.denominator != 1 or not facs or any(k <= 0 for _, k in facs):
        return n
    facs = [list(f) for f in facs]
    change = False
    if c < 0:
        sommes = [f for f in facs if f[1] % 2 == 1 and isinstance(f[0], Op) and f[0].op in "+-" and not _est_polynome(f[0])]
        # seulement si l'opposé commence par un terme positif (3 − eˣ) ; jamais −e^{2x} − 1
        if len(sommes) == 1 and any(sg < 0 for sg, _ in _termes(sommes[0][0])):
            sommes[0][0] = _oppose_somme(sommes[0][0])
            c, change = -c, True
    for f in [f for f in facs if isinstance(f[0], Fn) and f[0].nom == "exp"]:
        i = next(i for i, g in enumerate(facs) if g is f)
        j = next((j for j, (s, _) in enumerate(facs) if isinstance(s, Op) and s.op in "+-" and _contient(s, f[0])), None)
        if j is not None and j < i:
            facs.insert(j, facs.pop(i))
            change = True
    if not change:
        return n
    out = _produit(([Nb(abs(c))] if abs(c) != 1 else []) + [_puiss_sure(h, k) for h, k in facs])
    return Neg(out) if c < 0 else out


def _simplifier(n):
    """Met f' en forme factorisée (jamais développée) : plus facile à lire, et les
    zéros s'y lisent directement. Le résultat
    est écrit en un quotient numérateur / dénominateur (_en_quotient)."""
    sp = charger_sympy()
    if sp is None:
        return _en_quotient(_ordre_naturel(_nettoyer(n)))
    try:
        e = en_sympy(n)
        irrationnel = any(not p.exp.is_Rational for p in e.atoms(sp.Pow))
        if irrationnel:
            # exposant constant irrationnel : x^α·ln x + x^α/x → x^(α−1)(α ln x + 1) (les puissances de x se combinent)
            e = sp.powsimp(sp.expand(e))
            e = sp.collect(e, [q for q in e.atoms(sp.Pow) if not q.exp.is_Rational])
        else:
            try:
                e = _factoriser_avec_exp(sp, e)
            except Exception:
                e = sp.factor(e)
        return _forme_du_corrige(_en_quotient(_ordre_naturel(_nettoyer(arbre_depuis_sympy(e)))))
    except Exception:
        return _en_quotient(_ordre_naturel(_nettoyer(n)))


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
            rf"\(u(x) = {tex(u)}\) (dérivée interne \(u'(x) = {tex(_epurer(du))}\)) \(\Rightarrow\) "
            rf"\(\left({tex(n)}\right)' = {REGLE_FN_TEX[n.nom]} = {tex(resultat)}\)."
        ))
    return resultat


def _derivee_puissance(n, items):
    e = valeur_constante(n.b)
    if e is None and sans_x(n.b):
        # exposant constant irrationnel (ln 2, √2, e…) : (u^α)' = α·u^(α−1)·u', comme pour un exposant rationnel
        if valeur_constante(n.a) is not None:
            return Nb(0)
        u, alpha = n.a, n.b
        du = derivee_narree(u, items, top=False)
        reste = Op("^", u, Op("-", alpha, Nb(F(1))))
        resultat = _simplifier(_mul(_mul(alpha, reste), du))
        if isinstance(u, X):
            items.append(txt(rf"\(\left({tex(n)}\right)' = {tex(resultat)}\) (règle de la puissance, \(\alpha = {tex(alpha)}\) constant)."))
        else:
            items.append(txt(
                rf"\({tex(n)}\) est de la forme \(u^{{\alpha}}\) avec \(u(x) = {tex(u)}\) et \(\alpha = {tex(alpha)}\) constant "
                rf"(dérivée interne \(u'(x) = {tex(_epurer(du))}\)) \(\Rightarrow\) "
                rf"\(\left({tex(n)}\right)' = \alpha\,u^{{\alpha - 1}}u' = {tex(resultat)}\)."
            ))
        return resultat
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
            rf"(dérivée interne \(u'(x) = {tex(_epurer(du))}\)) \(\Rightarrow\) "
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


def _signe_devant(n):
    """Facteur négatif (−2e^{−2x}, −1…) écrit −(…) : placé à droite d'un produit, il est écrit entre parenthèses, avec le point
    (_tex_brut) : (x² − 6)·(−2e^{−2x}) et non (x² − 6) · −2e^{−2x} (décisions EC, D7)."""
    reste, negatif = _pos_et_signe(n)
    return Neg(reste) if negatif and not isinstance(n, Neg) else n


def _tex_brut(n):
    """tex(n), sauf qu'un facteur négatif à droite d'un produit est précédé du point : (x² − 6)·(−2e^{−2x}) (décisions EC, D7 ;
    tex écrit deux parenthèses côte à côte sans point). Seuls les sommes, différences et quotients sont parcourus : partout
    ailleurs, l'écriture est exactement celle de tex."""
    if isinstance(n, Op):
        if n.op == "*" and isinstance(n.b, Neg):
            return par(n.a, 1.5) + r" \cdot " + par(n.b, 2)
        if n.op == "+" and not isinstance(n.b, Neg):
            return _tex_brut(n.a) + " + " + _tex_brut(n.b)
        if n.op == "-" and prec(n.b) >= 2:
            return _tex_brut(n.a) + " - " + _tex_brut(n.b)
        if n.op == "/" and not (isinstance(n.a, Neg) and isinstance(n.a.a, Nb) and isinstance(n.b, Nb)):
            return r"\frac{" + _tex_brut(n.a) + "}{" + tex(n.b) + "}"
    return tex(n)


def bloc_uv(u, du, v, dv):
    """Tableau u | v / u′ | v′ des règles du produit et du quotient (décisions EC, D8), bloc « uv » du format de sortie (tex)."""
    return {"type": "uv", "u": "u = " + tex(u), "du": "u' = " + tex(du), "v": "v = " + tex(v), "dv": "v' = " + tex(dv)}


REGLE_PRODUIT = r"On applique la règle du produit, \((uv)' = u'v + uv'\), avec :"
REGLE_QUOTIENT = r"On applique la règle du quotient, \(\left(\frac{u}{v}\right)' = \frac{u'v - uv'}{v^2}\), avec :"


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
        items.append(txt(REGLE_PRODUIT))
        place = len(items)                   # le tableau u, v / u′, v′ suit la règle ; les justifications des dérivées viennent après
    ua = derivee_narree(a, items, top=False)
    ub = derivee_narree(b, items, top=False)
    if top:
        ua, ub = _simplifier(ua), _simplifier(ub)
        items.insert(place, bloc_uv(a, ua, b, ub))
    brut = _epurer(_add(_mul(ua, b), _mul(a, _signe_devant(ub) if top else ub)))
    if not top:
        return brut
    simplifie = _simplifier(brut)
    items.append(txt(rf"\({etiq} = u'(x)v(x) + u(x)v'(x) = {_tex_brut(brut)} = {tex(simplifie)}\)."))
    return simplifie


def _derivee_quotient(n, items, top, etiq=F_PRIME):
    a, b = n.a, n.b
    cb = valeur_constante(b)
    if cb is not None:
        return _facteur_constant(b, a, "g/c", items, top, etiq)
    if top:
        items.append(txt(REGLE_QUOTIENT))
        place = len(items)
    ua = derivee_narree(a, items, top=False)
    ub = derivee_narree(b, items, top=False)
    if top:
        ua, ub = _simplifier(ua), _simplifier(ub)
        items.insert(place, bloc_uv(a, ua, b, ub))
    brut = _epurer(_div(_sub(_mul(ua, b), _mul(a, _signe_devant(ub) if top else ub)), _pow(b, Nb(2))))
    if not top:
        return brut
    simplifie = _simplifier(brut)
    items.append(txt(rf"\({etiq} = \dfrac{{u'(x)v(x) - u(x)v'(x)}}{{v(x)^2}} = {_tex_brut(brut)} = {tex(simplifie)}\)."))
    return simplifie


# =====================================================================
# Dérivée de l'exposant détaillée (D7) et développement d'abord (D7b)
# =====================================================================
POINTS_SONDE = (-3.7, -1.3, -0.45, 0.35, 1.6, 2.9, 5.1)


def _monome(t):
    """c·xᵏ écrit tel quel (c entier non nul, k ≥ 0) → (c, k) ; None sinon."""
    if isinstance(t, Nb):
        return (t.v, 0) if t.v.denominator == 1 and t.v != 0 else None
    if isinstance(t, X):
        return F(1), 1
    if isinstance(t, Op) and t.op == "^" and isinstance(t.a, X) and isinstance(t.b, Nb):
        return (F(1), int(t.b.v)) if t.b.v.denominator == 1 and t.b.v >= 2 else None
    if isinstance(t, Op) and t.op == "*" and isinstance(_coefficient(t.a), F):
        m = _monome(t.b)
        return (_coefficient(t.a) * m[0], m[1]) if m is not None and m[1] >= 1 else None
    return None


def _coefficient(n):
    """Coefficient entier non nul écrit devant : Nb (6) ou Neg(Nb) (le parseur lit −2x² comme (−2)·x²) ; None sinon."""
    if isinstance(n, Neg) and isinstance(n.a, Nb):
        c = _coefficient(n.a)
        return None if c is None else -c
    return n.v if isinstance(n, Nb) and n.v.denominator == 1 and n.v != 0 else None


def _monomes(n):
    """Termes (c, k) d'un polynôme écrit développé (somme de c·xᵏ, c entier), dans l'ordre d'écriture ; None sinon."""
    out = []
    for sg, t in _termes(n):
        m = _monome(t)
        if m is None:
            return None
        out.append((sg * m[0], m[1]))
    return out


def _reduire(termes):
    """Termes semblables regroupés, degrés décroissants, coefficients nuls retirés."""
    somme = {}
    for c, k in termes:
        somme[k] = somme.get(k, 0) + c
    return [(somme[k], k) for k in sorted(somme, reverse=True) if somme[k] != 0]


def _monome_arbre(c, k):
    """Arbre de c·xᵏ, c > 0."""
    if k == 0:
        return Nb(c)
    xk = X() if k == 1 else Op("^", X(), Nb(k))
    return xk if c == 1 else Op("*", Nb(c), xk)


def _somme_arbre(termes):
    """Arbre de la somme des c·xᵏ, dans l'ordre donné, sans rien regrouper (12x² − 24x + 6x − 12)."""
    out = None
    for c, k in termes:
        m = _monome_arbre(abs(c), k)
        out = (Neg(m) if c < 0 else m) if out is None else Op("-" if c < 0 else "+", out, m)
    return out


def _egaux(sp, arbres):
    """Toutes les écritures sont égales à la première : différence nulle pour SymPy ET sonde numérique en 7 points (au moins 4
    points où toutes sont définies). False au moindre doute."""
    try:
        ref = en_sympy(arbres[0])
        if any(not _nul(sp, en_sympy(t) - ref) for t in arbres[1:]):
            return False
        testes = 0
        for x in POINTS_SONDE:
            vals = [_valeur_num(t, x) for t in arbres]
            if all(v is None for v in vals):
                continue
            if any(v is None for v in vals) or any(abs(v - vals[0]) > 1e-9 * (1 + abs(vals[0])) for v in vals):
                return False
            testes += 1
        return testes >= 4
    except Exception:
        return False


def _nul(sp, e):
    """e est nulle pour SymPy : d'abord `cancel` après développement (fractions rationnelles, polynômes en exponentielles), rapide ;
    sinon `simplify`. Une réponse « non nul » vaut doute (jamais d'égalité affirmée sans preuve)."""
    if sp.cancel(sp.expand(sp.powsimp(e, combine="exp"))) == 0:
        return True
    return sp.simplify(e) == 0


def _derivee_juste(sp, g, gp):
    """gp est la dérivée de g : SymPy (diff) et sonde numérique (différence centrée)."""
    try:
        if not _nul(sp, sp.diff(en_sympy(g), SYMPY["x"]) - en_sympy(gp)):
            return False
        testes = 0
        for x in POINTS_SONDE:
            h = 1e-6 * (1 + abs(x))
            a, b, d = _valeur_num(g, x + h), _valeur_num(g, x - h), _valeur_num(gp, x)
            if None in (a, b, d):
                continue
            if abs((a - b) / (2 * h) - d) > 1e-4 * (1 + abs(d)):
                return False
            testes += 1
        return testes >= 4
    except Exception:
        return False


def _ligne(gauche, quotient, propriete):
    return txt(rf"\({gauche}{tex(quotient)}\) ({propriete})")


def _derivee_exposant(f, fprime):
    """Décisions EC, D7 : f = e^{g(x)} avec g = u/v, u et v polynômes écrits développés à coefficients entiers, v non constant
    (exposant qui n'est pas affine, comme Ex7 et d). Sous-carte « Dérivée de l'exposant » : tableau u, v / u′, v′ (D8), règle du
    quotient, puis le numérateur une étape par ligne (développement, réduction, mise en évidence, simplification). Chaque ligne
    est vérifiée égale à la précédente et la dernière égale à g′ (SymPy et sonde), et g′·e^{g} égale à f′ ; au moindre doute,
    None (rédaction habituelle). Renvoie les étapes de la carte « Dérivée » (avant le résultat encadré)."""
    if not (isinstance(f, Fn) and f.nom == "exp" and isinstance(f.a, Op) and f.a.op == "/"):
        return None
    sp = charger_sympy()
    if sp is None:
        return None
    g, A, B = f.a, f.a.a, f.a.b
    mA, mB = _monomes(A), _monomes(B)
    if mA is None or mB is None or all(k == 0 for _, k in mB):
        return None
    dA = _reduire([(c * k, k - 1) for c, k in mA if k >= 1])
    dB = _reduire([(c * k, k - 1) for c, k in mB if k >= 1])
    ua = _somme_arbre(dA) if dA else Nb(0)
    ub = _somme_arbre(dB)
    den1 = _pow(B, Nb(2))
    brut = _epurer(_div(_sub(_mul(ua, B), _mul(A, _signe_devant(ub))), den1))
    if r"-\left(-" in _tex_brut(brut):                 # « −(−1) » (e^{−1/x}) : écriture maladroite, rédaction habituelle
        return None
    # développement : chaque produit terme à terme, rien n'est regroupé ; dénominateur (c·w)² = c²·w² si c = pgcd > 1
    developpe = [(p * q, i + j) for p, i in dA for q, j in mB] + [(-p * q, i + j) for p, i in mA for q, j in dB]
    cB = 0
    for c, _ in mB:
        cB = gcd(cB, int(abs(c)))
    signe = -1 if mB[0][0] < 0 else 1                    # (−6x − 18)² = 36(x + 3)² : le carré ne dépend pas du signe
    W = _somme_arbre([(signe * c / cB, k) for c, k in mB]) if cB > 1 else B
    den = Op("*", Nb(cB * cB), _pow(W, Nb(2))) if cB > 1 else den1
    reduit = _reduire(developpe)
    if not reduit:
        return None
    distribue = len(dA) * len(mB) > 1 or len(mA) * len(dB) > 1          # un produit de sommes : développement ; sinon un calcul
    lignes = [(_div(_somme_arbre(developpe), den), "développement" if distribue else "calcul"),
              (_div(_somme_arbre(reduit), den), "réduction")]
    # mise en évidence de c·xᵏ (c = pgcd des coefficients, du signe du premier terme), puis simplification par le pgcd avec le
    # coefficient du dénominateur
    cN = 0
    for c, _ in reduit:
        cN = gcd(cN, int(abs(c)))
    cN = -cN if reduit[0][0] < 0 else cN
    kN = min(k for _, k in reduit)
    reste = [(c / cN, k - kN) for c, k in reduit]
    if len(reduit) >= 2 and (abs(cN) != 1 or kN >= 1):
        def facteur(c):
            corps = _monome_arbre(abs(c), kN) if (abs(c) != 1 or kN >= 1) else None
            produit = _somme_arbre(reste) if corps is None else Op("*", corps, _somme_arbre(reste))
            return Neg(produit) if c < 0 else produit
        lignes.append((_div(facteur(cN), den), "mise en évidence"))
    elif len(reduit) == 1:
        cN, kN, reste = reduit[0][0], reduit[0][1], []

        def facteur(c):
            return _somme_arbre([(c, kN)])
    else:
        cN = 1
    d = gcd(int(abs(cN)), cB * cB) if cB > 1 else 1
    if d > 1:
        haut = facteur(cN / d)
        bas = _pow(W, Nb(2)) if cB * cB == d else Op("*", Nb(cB * cB // d), _pow(W, Nb(2)))
        lignes.append((_div(haut, bas), f"simplification par {d}"))
    # une ligne identique à la précédente n'est pas écrite
    chaine, vu = [], tex(brut)
    for q, propriete in lignes:
        if tex(q) != vu:
            chaine.append((q, propriete))
            vu = tex(q)
    gp = chaine[-1][0] if chaine else brut
    if not (_egaux(sp, [brut] + [q for q, _ in chaine]) and _derivee_juste(sp, g, gp)
            and _egaux(sp, [fprime, Op("*", gp, Fn("exp", g))])):
        return None
    etape1 = [txt(REGLE_QUOTIENT), bloc_uv(A, ua, B, ub), txt(rf"\(g'(x) = {_tex_brut(brut)}\) (règle du quotient)")]
    etapes = [{"titre": "règle du quotient", "blocs": etape1}]
    if chaine:
        blocs = [_ligne("g'(x) = ", chaine[0][0], chaine[0][1])] + [_ligne("= ", q, p) for q, p in chaine[1:]]
        etapes.append({"titre": "calcul du numérateur, puis simplification", "blocs": blocs})
    return [
        txt(rf"\(f(x) = e^{{g(x)}}\) avec \(g(x) = {tex(g)}\), donc \(f'(x) = g'(x) \cdot e^{{g(x)}}\) (dérivée d'une composée). "
            r"On calcule d'abord \(g'(x)\)."),
        {"type": "sous_calcul", "titre": "Dérivée de l'exposant", "etapes": etapes},
        txt(r"On remplace \(g'(x)\) dans \(f'(x) = g'(x) \cdot e^{g(x)}\) :"),
    ]


def _terme_exp(t):
    """c·e^{kx} (c entier non nul, k entier ≥ 1) → (c, k) ; constante entière non nulle c → (c, 0) ; None sinon."""
    def k_de(a):
        if isinstance(a, X):
            return 1
        if isinstance(a, Op) and a.op == "*" and isinstance(a.a, Nb) and isinstance(a.b, X) and a.a.v.denominator == 1 and a.a.v >= 2:
            return int(a.a.v)
        return None
    if isinstance(t, Nb):
        return (t.v, 0) if t.v.denominator == 1 and t.v != 0 else None
    c = F(1)
    if isinstance(t, Op) and t.op == "*" and _coefficient(t.a) is not None:
        c, t = _coefficient(t.a), t.b
    if isinstance(t, Fn) and t.nom == "exp" and k_de(t.a) is not None:
        return c, k_de(t.a)
    return None


def _exp_kx(k):
    return Fn("exp", X() if k == 1 else Op("*", Nb(k), X()))


def _tex_termes(termes):
    """Somme écrite terme à terme ; un terme (c, [k₁, k₂…]) est c·e^{k₁x}·e^{k₂x}… (eˣ · eˣ, sans regrouper)."""
    out = ""
    for i, (c, ks) in enumerate(termes):
        corps = r" \cdot ".join(tex(_exp_kx(k)) for k in ks)
        corps = tex(Nb(abs(c))) if not ks else ("" if abs(c) == 1 else tex(Nb(abs(c)))) + corps
        out += ("-" if c < 0 else "") + corps if i == 0 else (" - " if c < 0 else " + ") + corps
    return out


def _developpe_d_abord(f, fprime):
    """Décisions EC, D7b (.tex c) : f produit de deux facteurs, chacun somme de termes c·e^{kx} (k entier ≥ 1) et de constantes
    entières, avec au moins une exponentielle dans chacun et une somme dans l'un d'eux (polynôme en eˣ, aucun x hors des
    exponentielles) : on développe d'abord, eˣ(6 − eˣ) = 6eˣ − eˣ · eˣ = 6eˣ − e^{2x}, puis on dérive la somme. Chaque ligne est
    vérifiée (SymPy et sonde), et la dérivée de la forme développée doit s'écrire exactement comme f′ ; sinon None."""
    if not (isinstance(f, Op) and f.op == "*"):
        return None
    facteurs = []
    for h in (f.a, f.b):
        termes = [(sg, _terme_exp(t)) for sg, t in _termes(h)]
        if any(m is None for _, m in termes) or not any(m[1] for _, m in termes):
            return None
        facteurs.append([(sg * m[0], m[1]) for sg, m in termes])
    if all(len(fa) == 1 for fa in facteurs):
        return None
    sp = charger_sympy()
    if sp is None:
        return None
    produits = [(c1 * c2, [k for k in (k1, k2) if k]) for c1, k1 in facteurs[0] for c2, k2 in facteurs[1]]
    ordre, somme = [], {}
    for c, ks in produits:
        if sum(ks) not in somme:
            ordre.append(sum(ks))
            somme[sum(ks)] = 0
        somme[sum(ks)] += c
    reduits = [(somme[k], k) for k in ordre if somme[k] != 0]
    if not reduits:
        return None
    dev = None
    for c, k in reduits:
        m = Nb(abs(c)) if k == 0 else _exp_kx(k) if abs(c) == 1 else Op("*", Nb(abs(c)), _exp_kx(k))
        dev = (Neg(m) if c < 0 else m) if dev is None else Op("-" if c < 0 else "+", dev, m)
    l1, l2 = _tex_termes(produits), _tex_termes([(c, [k] if k else []) for c, k in reduits])
    try:
        e1 = sp.Add(*[int(c) * sp.Mul(*[sp.exp(k * SYMPY["x"]) for k in ks]) for c, ks in produits], evaluate=False)
        if not _nul(sp, e1 - en_sympy(f)):
            return None
    except Exception:
        return None
    if not _egaux(sp, [f, dev]):
        return None
    items = []
    try:
        d = derivee_narree(dev, items, top=True)
    except Exception:
        return None
    if tex(_simplifier(d)) != tex(fprime):
        return None
    lignes = [txt("On développe d'abord (c'est plus simple à dériver) :")]
    if l1 != l2:
        lignes += [txt(rf"\(f(x) = {tex(f)} = {l1}\) (développement)"), txt(rf"\(= {l2}\) (réduction)")]
    else:
        lignes.append(txt(rf"\(f(x) = {tex(f)} = {l2}\) (développement)"))
    return lignes + items


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
    raise NonPrisEnCharge("cette fonction sort du cadre de l'outil : la dérivée n'a pas été calculée.")


# =====================================================================
# Signe de f', variations, extrema
# =====================================================================
def _exp_au_numerateur(sp, r, valeur):
    """Écriture du corrigé (décisions EC, D17) : 3e^{−6} et non 3/e⁶. Seulement pour un entier fois une exponentielle
    d'exposant constant négatif (3e^{−6}, −e^{−1}) ; seule l'écriture change (la valeur reste celle de num_sympy)."""
    if valeur.approx or not isinstance(r, sp.Mul) or len(r.args) != 2:
        return valeur
    c, q = sorted(r.args, key=lambda a: not a.is_Integer)
    if not (c.is_Integer and isinstance(q, sp.exp) and q.args[0].is_number and q.args[0].is_negative):
        return valeur
    t = ("- " if c < 0 else "") + ("" if abs(c) == 1 else f"{abs(c)} ") + sp.latex(q)      # « - 2 e^{4} » comme sp.latex
    return Num(valeur.val, t, q=valeur.q, genre=valeur.genre, data=valeur.data, py=valeur.py)


def _valeur_exacte(f_tree, point):
    """f(point) en forme exacte : (objet Num, écriture SymPy de la valeur) si possible via SymPy, sinon None."""
    sp = charger_sympy()
    if sp is None or point.py is None:
        return None
    try:
        val = sp.sympify(point.py, locals={"sqrt": sp.sqrt, "exp": sp.exp, "log": sp.log, "pi": sp.pi})
        fe = en_sympy_reel(f_tree)
        r = sp.simplify(fe.subs(SYMPY["x"], val))
        if r.is_real is False:
            return None
        return _exp_au_numerateur(sp, r, num_sympy(r)), str(r)
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


def _est_polynome(n):
    """Arbre formé de nombres, de x, de +, −, ×, et de puissances entières : le zéro se lit sans explication."""
    if isinstance(n, (Nb, X)):
        return True
    if isinstance(n, Neg):
        return _est_polynome(n.a)
    if isinstance(n, Op) and n.op in "+-*":
        return _est_polynome(n.a) and _est_polynome(n.b)
    if isinstance(n, Op) and n.op == "^":
        e = valeur_constante(n.b)
        return e is not None and e.denominator == 1 and e > 0 and _est_polynome(n.a)
    return False


def _point_isole(iv):
    return iv.lo is not None and iv.hi is not None and iv.lf and iv.hf and proche(iv.lo.val, iv.hi.val)


def _ligne_zeros(fprime, c_const, facs, Z, D, items):
    """La ligne qui précède le tableau (guide de rédaction, R7) : zéros de f' et valeurs interdites, sans phrase sur le signe
    d'un facteur ; None si les zéros ne sont pas des points isolés. Un facteur qui n'est pas un polynôme et qui s'annule garde
    l'explication de son zéro (ln(x) + 1 = 0 ⇔ ln(x) = −1 : on soustrait 1), ajoutée à items avant la ligne."""
    if not all(_point_isole(iv) for iv in Z):
        return None
    zeros = sorted((iv.lo for iv in Z), key=lambda p: p.val)
    interdites = sorted((iv.lo for iv in complement(D) if _point_isole(iv)), key=lambda p: p.val)
    equations = []
    for h, expo in facs:
        if expo < 0:
            continue
        zh = [z for z in zeros if (evaluer(h, z.val) is not None and abs(evaluer(h, z.val)) <= 1e-9)]
        if not zh:
            continue
        equations.append(f"{tex(h)} = 0")
        if not _est_polynome(h):
            explication = []
            try:
                preimage(h, points([Num.rat(0)]), explication)
            except Exception:
                explication = []
            items.extend(explication)
    finale = r" \text{ ou } ".join(f"x = {z.tex}" for z in zeros)
    if not zeros:
        ligne = rf"\(f'(x) = {tex(fprime)}\) ne s'annule jamais"
    else:
        etapes = [rf"f'(x) = {tex(fprime)} = 0"]
        if len(facs) > 1 or c_const != 1 or facs[0][1] != 1:
            moyen = r" \text{ ou } ".join(equations)
            if moyen != finale:
                etapes.append(moyen)
        etapes.append(finale)
        ligne = r"\(" + r" \iff ".join(etapes) + r"\)"
    if interdites:
        ligne += (" ; valeur interdite : " if len(interdites) == 1 else " ; valeurs interdites : ")
        ligne += " ; ".join(rf"\(x = {p.tex}\)" for p in interdites)
    return ligne + "."


def _point_test(crit, i):
    """Point de test de l'intervalle i (entre crit[i − 1] et crit[i])."""
    k = len(crit)
    if k == 0:
        return 0.0
    if i == 0:
        return crit[0].val - 1
    if i == k:
        return crit[-1].val + 1
    return (crit[i - 1].val + crit[i].val) / 2


def _zone_hors(hors, j):
    """Case j du tableau (intervalle si j pair, point critique si j impair) entièrement hors de l'ED :
    un point critique ne l'est que si l'intervalle de chaque côté l'est."""
    return hors[j // 2] if j % 2 == 0 else (hors[(j - 1) // 2] and hors[(j + 1) // 2])


def tableau_signes(expr, Z, D, ED, etiquette, c_const, facs):
    """Tableau de signes « papier » (guide de rédaction, R7) de expr = c_const · ∏ hᵏ (facs, issus d'`aplatir`) : une ligne par
    facteur (constante à part), puis la ligne combinée `etiquette` (« f'(x) », « f(x) »). Z : zéros de expr ; D : ensemble où expr est
    étudiée (dans l'ED de f) ; ED : ensemble de définition de f (zones hors de l'ED barrées, double barre aux valeurs interdites).
    Résultat : (points critiques [Num], lignes, hors) ; hors[i] : l'intervalle i est hors de l'ED. Partagé par l'outil Dérivée
    (tableau de f') et l'Étude complète (tableau de f, partie 3)."""
    # Points critiques = zéros de expr ∪ bornes finies du domaine d'étude (valeurs interdites,
    # asymptotes) — une seule liste, servant à la fois aux tests de signe et (outil Dérivée) aux
    # valeurs exactes des extrema.
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
        return _point_test(crit, i)

    # 3) Une ligne par facteur (expr étant gardée factorisée), puis la ligne combinée — même
    # présentation qu'un tableau de signes « papier ».

    def _cellule(v, expo, critique=False):
        if v is None:
            # facteur non défini : en un point critique de l'ED, expr n'y est pas définie (double barre) ;
            # sur un intervalle, on est hors du domaine (zone barrée en aval)
            return "||" if critique else "x"
        if abs(v) <= 1e-9:
            return "||" if expo < 0 else "0"
        s = "+" if v > 0 else "-"
        return "+" if (s == "-" and expo % 2 == 0) else s

    # Intervalles hors de l'ED de f : ni signe ni flèche, case barrée (« x ») sur toutes les lignes.
    # Chaque intervalle entre deux points critiques est entièrement dans l'ED ou entièrement dehors
    # (les bornes de l'ED sont des points critiques).
    hors = [not contient(ED, _test(i)) for i in range(k + 1)]

    def _dans_zone_hors(j):
        return _zone_hors(hors, j)

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
    elif c_const != 1:
        lignes.append({"label": qtex(c_const), "cells": _barrer(["+"] * (2 * k + 1))})
    for h, expo in facs:
        label = tex(h) if prec(h) >= 3 else r"\left(" + tex(h) + r"\right)"
        if abs(expo) > 1:
            if indice_racine(h) is not None:
                label = r"\left(" + label + r"\right)"
            label += "^{" + str(abs(expo)) + "}"
        cells = []
        for i in range(k + 1):
            cells.append(_cellule(evaluer(h, _test(i)), expo))
            if i < k:
                cells.append(_cellule(evaluer(h, crit[i].val), expo, critique=True))
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
    # Valeur interdite de f : double barre sur la ligne combinée aussi quand aucune ligne de facteur ne la porte
    # (trou de (x²−1)/(x−1), où f' = 1).
    for j in range(1, 2 * k + 1, 2):
        if combinee[j] not in ("x", "||") and not contient(ED, crit[j // 2].val):
            combinee[j] = "||"
    # expr identiquement nulle (f' nulle : f constante sur chaque morceau de son ED) : « 0 » sur chaque
    # intervalle de l'ED, « || » aux valeurs interdites, hors de l'ED la case est barrée.
    f_constante = valeur_constante(expr) == 0
    if f_constante:
        for i in range(2 * k + 1):
            if i % 2 == 0:
                combinee[i] = "x" if hors[i // 2] else "0" if contient(D, _test(i // 2)) else "x"
            else:
                combinee[i] = "x" if _dans_zone_hors(i) else "0" if contient(D, crit[i // 2].val) else "||"
    lignes.append({"label": etiquette, "cells": combinee, "final": True})
    return crit, lignes, hors


def etudier(entree, analyse=None):
    """`analyse` : le résultat de analyser_complet(entree) quand l'appelant l'a déjà (Étude complète, D19) ; sinon il est calculé ici."""
    try:
        f = lire(entree)
    except ErreurSaisie as e:
        return {"ok": False, "erreur": str(e)}

    res_ed, _, ED = analyse if analyse is not None else analyser_complet(entree)
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
        res["deriv_erreur"] = "Cette fonction sort du cadre de l'outil : la dérivée n'a pas été calculée."
        res["deriv_detail"] = str(e)
        return res
    fprime = _simplifier(fprime)
    # rédactions du corrigé (décisions EC) : dérivée de l'exposant détaillée (D7), développement d'abord (D7b) ; f' est la même
    # (calculée ci-dessus), seules les étapes changent, et seulement si chaque ligne est vérifiée
    items_deriv = _derivee_exposant(f, fprime) or _developpe_d_abord(f, fprime) or items_deriv
    res["deriv_tex"] = tex(fprime)
    etapes, vues = [], set()                             # une même phrase n'est écrite qu'une fois ((eˣ)′ = eˣ pour u et v : D7)
    for it in items_deriv:
        cle = json.dumps(it, sort_keys=True)
        if cle not in vues:
            vues.add(cle)
            etapes.append(it)
    res["deriv_etapes"] = etapes
    res["deriv_resolu"] = True

    try:
        D_fprime = domaine(fprime)
    except Exception:
        D_fprime = REELS
    D = _aligner_sur(inter(ED, D_fprime), ED)
    res["domaine_etude_tex"] = ens_tex(D)

    # 1) On cherche d'abord les zéros de f' (candidats extrema) : narration explicite,
    # avant de dresser le tableau.
    items_signe = []
    if ens_tex(D) != ens_tex(ED):
        res["ed_deriv_tex"] = ens_tex(D)
        items_signe.append(txt(
            rf"ED de f' : \(D_{{f'}} = {ens_tex(D)}\), différent de l'ED de f, \(D_f = {ens_tex(ED)}\)."))
    n_intro = len(items_signe)
    numerateur = fprime.a if isinstance(fprime, Op) and fprime.op == "/" else fprime
    cn = valeur_constante(numerateur)
    resolution = []                                      # la résolution détaillée de f' = 0 ne sert que de repli
    try:
        if cn is not None and cn != 0 and numerateur is not fprime:
            Z = []                                       # f' = c / D avec c constante non nulle : aucun zéro
        else:
            Z = preimage(fprime, points([Num.rat(0)]), resolution)
    except NonPrisEnCharge:
        resolution = []
        try:
            Z = resoudre_general(fprime, "=", resolution)
        except Exception as e:
            res["signe_resolu"] = False
            res["signe_erreur"] = "Le signe de f'(x) n'a pas pu être étudié automatiquement."
            res["signe_detail"] = f"{type(e).__name__} : {e}"
            return res
    except Exception as e:
        res["signe_resolu"] = False
        res["signe_erreur"] = "Le signe de f'(x) n'a pas pu être étudié automatiquement."
        res["signe_detail"] = f"{type(e).__name__} : {e}"
        return res
    # Guide de rédaction (R7) : une seule ligne avant le tableau — zéros et valeurs interdites ; aucune phrase sur le signe
    # d'un facteur.
    try:
        c_const, facs = aplatir(fprime)
    except Exception:
        c_const, facs = F(1), [(fprime, 1)]
    ligne = _ligne_zeros(fprime, c_const, facs, Z, D, items_signe)
    if ligne is None:                                    # zéros non isolés (f' nulle sur un intervalle…) : résolution détaillée
        items_signe.extend(resolution)
    else:
        items_signe.append(txt(ligne))

    # 2) et 3) Points critiques (zéros de f' ∪ bornes finies du domaine d'étude) et tableau de signes (R7), une ligne par
    # facteur de f' puis la ligne f'(x) : `tableau_signes`, partagé avec l'Étude complète (tableau de f).
    crit, lignes, hors = tableau_signes(fprime, Z, D, ED, "f'(x)", c_const, facs)
    k = len(crit)
    ed_ivs = fusion(ED)
    combinee = lignes[-1]["cells"]
    f_constante = valeur_constante(fprime) == 0

    def _dans_zone_hors(j):
        return _zone_hors(hors, j)

    res["signe_resolu"] = True
    res["signe_etapes"] = items_signe
    res["table_signe"] = {"var": "x", "crit": [p.tex for p in crit], "rows": lignes}

    # 4) Variations : une flèche par intervalle ; en chaque point critique de l'ED de f :
    #  - extremum (i) : point intérieur de l'ED où f' change de signe (même si f' n'y est pas définie) ;
    #  - extremum (ii) : borne fermée de l'ED, nature donnée par le sens de variation de
    #    l'intervalle adjacent ;
    #  - jamais sur un intervalle où f est constante ; jamais hors de l'ED.
    # Là où f est définie mais pas f' (ou f constante), la ligne f(x) porte la valeur f(a), sans barre.
    def _bornes_fermees(pt):
        gauche = any(iv.lo is not None and iv.lf and proche(iv.lo.val, pt.val) for iv in ed_ivs)
        droite = any(iv.hi is not None and iv.hf and proche(iv.hi.val, pt.val) for iv in ed_ivs)
        return gauche, droite

    memo = {}

    def _valeur_en(pt):
        """(valeur, écriture tex, écriture SymPy ou None si la valeur n'est pas exacte)."""
        if pt.val not in memo:
            exacte = None if pt.approx else _valeur_exacte(f, pt)
            if exacte is None:
                v = _valeur_num(f, pt.val)
                memo[pt.val] = (v, Num.approche(v).tex if v is not None else "?", None)
            else:
                valeur, py = exacte
                memo[pt.val] = (valeur.val, valeur.tex, py)
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
        valeur_tex = None
        if genre is not None:
            v, valeur_tex, valeur_py = _valeur_en(p)
            e = {"genre": genre, "x_tex": p.tex, "f_tex": valeur_tex, "x_val": p.val, "f_val": v}
            if valeur_py is not None and not p.approx and p.py is not None:
                e.update(x_py=p.py, f_py=valeur_py)        # écritures exactes (SymPy) : extremums de l'Étude complète (D11)
            extrema.append(e)
        if not contient(D, p.val) or f_constante:
            v, valeur_tex, _ = _valeur_en(p)
            fleche_cells.append("val:" + valeur_tex)
        elif genre is not None:
            # décisions EC, D10 (Dérivée et Étude complète) : la valeur de l'extremum dans la ligne f(x) ; « • » si elle est inconnue
            fleche_cells.append("extremum" if valeur_tex == "?" else "val:" + valeur_tex)
        else:
            fleche_cells.append("")

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
