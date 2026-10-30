

# ---------------------------------------------------------------------------------------------------------------------
# Podium : classement exponentielle > puissance > logarithme, en t → +∞ (t = x, −x, ou 1/x en 0⁺)
# ---------------------------------------------------------------------------------------------------------------------
class Sans_podium(Exception):
    pass


def _poly(u):
    try:
        return LA._polynome_de(u)
    except Exception:
        return None


def _norm(n):
    """Écriture normalisée d'un arbre (arguments d'exp, ln et sommes compris) : 1/(1/t) → t."""
    if isinstance(n, Fn):
        return Fn(n.nom, _norm(n.a))
    if isinstance(n, Neg):
        return mono_arbre(_mono_norm(n))
    if isinstance(n, Op) and n.op in "+-":
        return Op(n.op, _norm(n.a), _norm(n.b))
    m = _mono_norm(n)
    return mono_arbre(m) if m is not None else n


def _mono_norm(n):
    m = mono(n)
    if m is None:
        return None
    fact = []
    for a, k in m.fact:
        if isinstance(a, Fn):
            a = Fn(a.nom, _norm(a.a))
        elif isinstance(a, Op) and a.op in "+-":
            a = Op(a.op, _norm(a.a), _norm(a.b))
        fact.append((a, k))
    out = Mono(m.coef)
    for t, k in fact:
        out = _fusion(out, Mono(1, [(t, k)]))
    return out


def en_t_arbre(f, pt):
    """f écrite en t (t → +∞) : (arbre, nom de t, borne +∞) ; en ±∞ l'arbre est f elle-même et s = ±1."""
    if pt.s:
        return f, None, pt.s
    if pt.a is not None and pt.a == 0 and pt.d > 0:
        return _norm(LA._substituer(f, Op("/", Nb(F(1)), X()))), "t = \\dfrac{1}{x}", 1
    raise Sans_podium()


def classer_atome(a, k, s):
    """(rang, valeur signée, coefficient dominant) de a^k quand x → s·∞ (t = s·x) ; Sans_podium sinon.
    rang 1 logarithme (valeur : multiple de ln t), 2 puissance (degré), 3 exponentielle (coefficient de t dans l'exposant)."""
    if isinstance(a, X):
        return 2, k, F(1)
    if isinstance(a, Fn) and a.nom == "exp":
        P = _poly(a.a)
        if P is None or len(P) != 2 or P[1] == 0:
            raise Sans_podium()
        return 3, k * P[1] * s, F(1)
    if isinstance(a, Fn) and a.nom == "ln":
        m = mono(a.a)
        if m is not None and len(m.fact) == 1 and isinstance(m.fact[0][0], X):
            j = m.fact[0][1]
            if m.coef > 0 and s > 0 or (m.coef < 0 and s < 0 and j % 2 == 1) or (m.coef > 0 and s < 0 and j % 2 == 0):
                return 1, k * j, F(1)
        P = _poly(a.a)
        if P is not None and len(P) >= 2 and P[-1] * (s ** (len(P) - 1)) > 0:
            return 1, k * (len(P) - 1), F(1)
        raise Sans_podium()
    P = _poly(a)
    if P is not None and len(P) >= 2 and P[-1] != 0:
        return 2, k * (len(P) - 1), P[-1] ** k
    raise Sans_podium()


NOM = {3: "l'exponentielle", 2: "la puissance", 1: "le logarithme"}


def nom_maj(r):
    return NOM[r][0].upper() + NOM[r][1:]


def classer(m, s):
    """(genre, rang, éléments) : genre 'inf' | 'zero' | 'const' ; éléments [(atome, k, rang, valeur)]."""
    cumul = {1: F(0), 2: F(0), 3: F(0)}
    coef = m.coef
    elems = []
    for a, k in m.fact:
        if sans_x(a):
            raise Sans_podium()
        r, v, c = classer_atome(a, k, s)
        cumul[r] += v
        if r == 2:
            coef *= c
        elems.append((a, k, r, v))
    for r in (3, 2, 1):
        if cumul[r] != 0:
            return ("inf" if cumul[r] > 0 else "zero"), elems, coef
    return "const", elems, coef


def signe_mot(s):
    return ">" if s > 0 else "<"


# ---------------------------------------------------------------------------------------------------------------------
# Tableau de valeurs (8.14) : valeurs en haute précision
# ---------------------------------------------------------------------------------------------------------------------
def fmt_val(v):
    import math
    if v is None:
        return None
    a = abs(v)
    if a >= 1e5 or (0 < a < 1e-4):
        e = int(math.floor(math.log10(a)))
        mant = v / 10 ** e
        return f"{mant:.2f}".replace(".", "{,}") + f" \\cdot 10^{{{e}}}"
    r = round(v)
    for d in range(4, 9):
        s = f"{v:.{d}f}"
        if float(s) != r:
            return s.replace(".", "{,}")
    return "\\approx " + str(int(r))


def tableau_valeurs(f, pt):
    """([x tex], [valeur tex]) ; None si trop peu de points évaluables."""
    import mpmath
    mp = mpmath.MPContext()
    mp.dps = 80
    if pt.s < 0:
        xs = [-1, -10, -20, -25, -30]
    elif pt.s > 0:
        xs = [1, 10, 20, 50, 100]
    else:
        a = float(charger_sympy().N(pt.a))
        xs = [a + pt.d * h for h in (0.1, 0.01, 0.001, 0.0001, 0.00001)]
    out_x, out_v = [], []
    for x in xs:
        try:
            v = LA._val_mp(mp, f, mp.mpf(x))
        except Exception:
            v = None
        if v is None:
            continue
        out_x.append(str(x).replace(".", "{,}") if not isinstance(x, int) else str(x))
        out_v.append(fmt_val(float(v)))
    return (out_x, out_v) if len(out_x) >= 3 else None


# ---------------------------------------------------------------------------------------------------------------------
# La descente
# ---------------------------------------------------------------------------------------------------------------------
def _contient_transcendant(n):
    if isinstance(n, Fn):
        return n.nom in ("exp", "ln") or _contient_transcendant(n.a)
    if isinstance(n, Neg):
        return _contient_transcendant(n.a)
    return isinstance(n, Op) and (_contient_transcendant(n.a) or _contient_transcendant(n.b) or (n.op == "^" and not sans_x(n.b)))


def _facteurs_produit(n, out):
    if isinstance(n, Op) and n.op == "*":
        _facteurs_produit(n.a, out)
        _facteurs_produit(n.b, out)
    else:
        out.append(n)


def _a_fraction(n):
    if isinstance(n, Op):
        return n.op == "/" or _a_fraction(n.a) or _a_fraction(n.b)
    if isinstance(n, (Neg, Fn)):
        return _a_fraction(n.a)
    return False


def _commun(a, b):
    fa, fb = [], []
    _facteurs_produit(a.a if isinstance(a, Neg) else a, fa)
    _facteurs_produit(b.a if isinstance(b, Neg) else b, fb)
    for x in fa:
        if isinstance(x, Nb) or sans_x(x):
            continue
        if any(T(x) == T(y) for y in fb):
            return x
    return None


def desigmer(c):
    """−A/B devient (−A)/B : le signe passe dans le haut, comme le corrigé (−x²/e^(−3x))."""
    if isinstance(c, Neg) and isinstance(c.a, Op) and c.a.op == "/":
        return Op("/", LA._oppose_arbre(c.a.a), c.a.b)
    return c


def fmt_approx(v):
    s = f"{v:.2f}" if abs(v) >= 1 else f"{v:.2g}"
    return s.replace(".", "{,}")


class Desc:
    def __init__(self, f, pt):
        self.f, self.pt = f, pt
        self.etapes = []
        self.alertes = []
        self.n_bh = 0
        self.attendu = None            # (genre, signe) annoncé par le podium
        self.devine = None             # valeur devinée à la calculatrice (8.14)
        self.constante = None

    # ---- blocs ----
    def etape(self, titre, blocs):
        self.etapes.append({"titre": titre, "blocs": [b for b in blocs if b]})

    def lim_tex(self, e):
        return f"\\lim_{{x\\to {self.pt.tex()}}} {T(e)}"

    def txt(self, html):
        return so.texte(html, style="etape")

    def disp(self, t):
        return so.texte(D(t), style="etape")

    def forme_phrase(self, nom, A, B, op, encore=False):
        ft = forme_tex(nom, A, B, op)
        if nom:
            return f"Forme {M(ft)} : {'encore ' if encore else ''}{IND()}."
        return f"Forme {M(ft)} : {DET()}!"

    # ---- analyse d'une expression ----
    def analyse(self, c):
        """('ind', nom, A, B, op) | ('det', L, A, B, op) | ('cst', L) pour c = A/B, produit ou autre."""
        pt = self.pt
        try:
            if isinstance(c, Op) and c.op == "/":
                nom, A, B = forme(c, pt)
                return ("ind", nom, A, B, "/") if nom else ("det", lim(c, pt), A, B, "/")
            fs = cotes(c)
            if isinstance(c, (Op, Neg)) and len(fs) == 2 and not (isinstance(c, Op) and c.op in "+-"):
                if not (isinstance(c, Neg)):
                    A, B = lim(fs[0], pt), lim(fs[1], pt)
                    nom = "0·∞" if ((A.inf and B.nul()) or (B.inf and A.nul())) else None
                    return ("ind", nom, A, B, "*") if nom else ("det", lim(c, pt), A, B, "*")
            return ("cst" if sans_x(c) else "det", lim(c, pt), None, None, None)
        except LA.FormeIndeterminee:
            raise Abandon("forme indéterminée imbriquée")

    # ---- étape « on remplace » ----
    def texte_haut_bas(self, f):
        pt = self.pt
        if isinstance(f, Op) and f.op == "/":
            h = fragment(f.a, pt) or M(plain(f.a, pt))
            b = fragment(f.b, pt) or M(plain(f.b, pt))
            return f"Haut : {h}. Bas : {b}. "
        fs = cotes(f)
        return ". ".join(fragment(x, pt) or M(plain(x, pt)) for x in fs) + ". "

    # ---- prédiction ----
    def signe_global(self, f):
        m = mono(f)
        if m is None:
            raise Abandon("signe inconnu")
        s = 1 if m.coef > 0 else -1
        for a, k in m.fact:
            sa = signe_lim(lim(a, self.pt))
            if sa == 0:
                raise Abandon("signe d'un facteur inconnu")
            if k % 2:
                s *= sa
        return s

    def prediction(self, f):
        """(bloc, (genre, signe)) ; Sans_podium si le podium ne peut pas aider."""
        pt = self.pt
        ft, nom_t, s = en_t_arbre(f, pt)
        m = _mono_norm(ft)
        if m is None:
            raise Sans_podium()
        genre, elems, coef = classer(m, s)
        if genre == "const":
            raise Sans_podium()
        sg = self.signe_global(f)
        tr = (lambda t: t.replace("x", "t")) if nom_t else (lambda t: t)
        lignes = []
        quotient = bool(nom_t) or (isinstance(f, Op) and f.op == "/")
        if nom_t:
            canon = mono_arbre(Mono(m.coef, [(Fn("exp", LA._oppose_arbre(a.a)), -k) if (isinstance(a, Fn) and a.nom == "exp" and v * 1 < 0 and False) else (a, k)
                                            for a, k, r, v in elems]))
            lignes.append("On pense à " + M(nom_t) + " : quand " + M("x \\to " + pt.tex()) + ", " + M("t \\to +\\infty")
                          + ", et " + M(tr(T(self._canon(f, m, elems)))) + ".")
        if quotient:
            haut = [e for e in elems if e[3] > 0]
            bas = [e for e in elems if e[3] < 0]
            if not haut or not bas:
                raise Sans_podium()
            dh = max(haut, key=lambda e: (e[2], abs(e[3])))
            db = max(bas, key=lambda e: (e[2], abs(e[3])))
            nm = lambda e: tr(T(self._affiche(e, nom_t)))
            l1 = f"Au haut : {M(nm(dh))}. Au bas : {M(nm(db))}. "
            if dh[2] != db[2]:
                hg = dh[2] > db[2]
                g, p = (dh, db) if hg else (db, dh)
                l1 += (f"Sur le podium, {NOM[g[2]]} bat {NOM[p[2]]} : c'est le <b>{'haut' if hg else 'bas'}</b> qui gagne, "
                       f"donc le quotient {'part vers l' + chr(39) + 'infini' if hg else 'tend vers 0'}.")
            elif dh[2] == 2:
                hg = abs(dh[3]) > abs(db[3])
                l1 += (f"La plus grande puissance est au <b>{'haut' if hg else 'bas'}</b>, donc le quotient "
                       f"{'part vers l' + chr(39) + 'infini' if hg else 'tend vers 0'}.")
            else:
                raise Sans_podium()
            lignes.append(l1)
            lignes.append(self.ligne_signe(f, True))
        else:
            fs = cotes(f)
            rangs = {}
            for a, k, r, v in elems:
                rangs.setdefault(r, []).append(a)
            if len(fs) < 2 or len(rangs) < 2:
                raise Sans_podium()
            hi, lo = max(rangs), min(rangs)
            gagnant = rangs[hi][0]
            l1 = "Produit : " + " et ".join(M(plain(a, pt)) for a in fs) + ". "
            verbe = "bat" if hi == 3 else "est plus forte que"
            l1 += (f"{nom_maj(hi)} {verbe} {NOM[lo]} : c'est {M(T(gagnant))} qui impose sa limite, "
                   f"donc {'0' if genre == 'zero' else '∞'}.")
            lignes.append(l1)
            lignes.append(self.ligne_signe(f, False))
        val = ("+\\infty" if sg > 0 else "-\\infty") if genre == "inf" else ("0^{+}" if sg > 0 else "0^{-}")
        lignes.append(f"<b>On s'attend à :</b> {M(val)}")
        return so.encadre("prediction", "Prédiction avec la règle du podium", lignes), (genre, sg)

    def _affiche(self, e, nom_t):
        a, k, r, v = e
        if isinstance(a, X) or (r == 2 and not isinstance(a, Fn)):
            P = _poly(a)
            d = abs(k) * (len(P) - 1) if P else abs(k)
            return Op("^", X(), Nb(F(d))) if d > 1 else X()
        return a

    def _canon(self, f, m, elems):
        out = Mono(m.coef)
        for a, k, r, v in elems:
            if isinstance(a, Fn) and a.nom == "exp" and v < 0:
                a, k = Fn("exp", _norm(LA._oppose_arbre(a.a))), -k
            out = _fusion(out, Mono(1, [(a, k)]))
        return mono_arbre(out)

    def ligne_signe(self, f, quotient):
        pt = self.pt
        sg = self.signe_global(f)
        if quotient and isinstance(f, Op) and f.op == "/":
            sa, sb = signe_lim(lim(f.a, pt)), signe_lim(lim(f.b, pt))
            return f"Signe : haut {signe_mot(sa)} 0, bas {signe_mot(sb)} 0, donc quotient {signe_mot(sg)} 0."
        fs = cotes(f)
        parts = [f"{M(T(a))} {signe_mot(signe_lim(lim(a, pt)))} 0" for a in fs]
        return "Signe : " + " et ".join(parts) + f", donc {'produit' if len(fs) > 1 else 'quotient'} {signe_mot(sg)} 0."

    def bloc_calculatrice(self, f):
        """Podium inapplicable (8.14) : encadré + tableau de valeurs ; renvoie (blocs, valeur devinée ou None)."""
        pt = self.pt
        tv = tableau_valeurs(f, pt)
        lignes = ["Ici, le podium <b>ne peut pas aider</b> : il n'y a pas de « course » entre une exponentielle, une puissance et un logarithme "
                  "qui partent vers l'infini."]
        if tv is not None:
            lignes.append("Pour prédire, on utilise la calculatrice (tableau ci-dessous).")
        blocs = [so.encadre("prediction", "Prédiction avec la règle du podium", lignes)]
        if tv is not None:
            blocs.append(so.valeurs(T(f), tv[0], tv[1]))
            blocs.append(so.texte("<i>La calculatrice ne prouve rien : c'est le calcul qui suit qui donne la réponse sûre.</i>", style="etape"))
        return blocs, tv
