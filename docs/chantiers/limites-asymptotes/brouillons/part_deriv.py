# ---------------------------------------------------------------------------------------------------------------------
# Dérivées (table maison, confirmées numériquement) et leur présentation
# ---------------------------------------------------------------------------------------------------------------------
def _a_expo_neg(n):
    if isinstance(n, Op) and n.op == "^":
        k = valeur_constante(n.b)
        if k is not None and k < 0:
            return True
    if isinstance(n, (Neg, Fn)):
        return _a_expo_neg(n.a)
    return isinstance(n, Op) and (_a_expo_neg(n.a) or _a_expo_neg(n.b))


def _embellir(n):
    """3·(1/x) s'écrit 3/x."""
    if isinstance(n, Neg):
        return Neg(_embellir(n.a))
    if isinstance(n, Fn):
        return Fn(n.nom, _embellir(n.a))
    if isinstance(n, Op):
        a, b = _embellir(n.a), _embellir(n.b)
        if n.op == "*" and isinstance(a, Nb) and isinstance(b, Op) and b.op == "/" and isinstance(b.a, Nb) and b.a.v == 1:
            return Op("/", a, b.b)
        return Op(n.op, a, b)
    return n


def derive(h):
    d = _embellir(LA._derivee_nat(h))
    if not derivee_ok(h, d):
        raise Abandon("dérivée non confirmée : " + T(h))
    return d


def tex_derivee(d):
    """Écriture de la dérivée dans le tableau BH : −3x^{−4} = −\\frac{3}{x^{4}} quand elle contient une puissance négative."""
    t = T(d)
    if _a_expo_neg(d):
        m = mono(d)
        if m is not None:
            alt = mono_arbre(m)
            if T(alt) != t and egaux(alt, d):
                return t + " = " + T(alt)
    return t


def _fns(n, out):
    if isinstance(n, Fn):
        out.append(n)
        _fns(n.a, out)
    elif isinstance(n, Neg):
        _fns(n.a, out)
    elif isinstance(n, Op):
        _fns(n.a, out)
        _fns(n.b, out)


def intro_derivee(h):
    """Phrases du corrigé pour les dérivées composées : (e^u)' = u'e^u, (ln u)' = u'/u."""
    fs, vus, out = [], set(), []
    _fns(h, fs)
    for g in fs:
        u = g.a
        if g.nom == "exp":
            P = _poly(u)
            if P is not None and len(P) == 2:
                continue                                  # e^{kx+b} : la dérivée k·e^{kx+b} se lit dans le tableau
            cle = "e" + T(u)
            if cle in vus:
                continue
            vus.add(cle)
            du = derive(u)
            out.append(f"Pour dériver {M(T(g))}, on utilise {M(chr(92) + 'left(e^{u}' + chr(92) + 'right)' + chr(39) + ' = u' + chr(39) + 'e^{u}')} "
                       f"avec {M('u = ' + T(u))}, {M('u' + chr(39) + ' = ' + T(du))}.")
        elif g.nom == "ln" and not isinstance(u, X):
            cle = "l" + T(u)
            if cle in vus:
                continue
            vus.add(cle)
            du = derive(u)
            alt = mono(Op("/", du, u))
            fin = ""
            if alt is not None:
                a = mono_arbre(alt)
                brut = f"\\dfrac{{{T(du)}}}{{{T(u)}}}"
                if T(a) != brut and egaux(a, Op("/", du, u)):
                    fin = f" = {T(a)}"
            out.append(f"Pour dériver {M(T(g))}, on utilise {M(chr(92) + 'left(' + chr(92) + 'ln u' + chr(92) + 'right)' + chr(39) + ' = ' + chr(92) + 'dfrac{u' + chr(39) + '}{u}')} "
                       f"avec {M('u = ' + T(u))} et {M('u' + chr(39) + ' = ' + T(du))}"
                       + (f" : {M(chr(92) + 'dfrac{' + T(du) + '}{' + T(u) + '}' + fin)}" if fin else "") + ".")
    return out


