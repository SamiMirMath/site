

# ---------------------------------------------------------------------------------------------------------------------
# Suite de la classe Desc (méthodes ajoutées à la fin du module)
# ---------------------------------------------------------------------------------------------------------------------
def _m_resoudre(self):
    f = self.f
    if isinstance(f, Fn) and f.nom in ("exp", "ln"):
        return self.composee(f)
    if isinstance(f, Op) and f.op in "*/":
        return self.produit_quotient(f)
    raise Abandon("forme non prise en charge par la rédaction descendante")


def _m_produit_quotient(self, f):
    pt = self.pt
    A, B, op = None, None, None
    texte = self.texte_haut_bas(f)
    if isinstance(f, Op) and f.op == "/":
        nom, A, B = forme(f, pt)
        op = "/"
    else:
        fs = cotes(f)
        if len(fs) != 2:
            raise Abandon("produit de plus de deux facteurs non constants")
        A, B = lim(fs[0], pt), lim(fs[1], pt)
        nom = "0·∞" if ((A.inf and B.nul()) or (B.inf and A.nul())) else None
        op = "*"
    if nom is None:                                          # forme déterminée
        L = lim(f, pt)
        self.etape("on remplace", [self.txt(texte + self.forme_phrase(None, A, B, op))])
        return self.conclure_direct(f, A, B, op, L)
    # ---- étape 1 : on remplace, prédiction ----
    blocs1 = [self.txt(texte + self.forme_phrase(nom, A, B, op))]
    try:
        bloc, self.attendu = self.prediction(f)
        blocs1.append(bloc)
    except Sans_podium:
        bs, self.devine = self.bloc_calculatrice(f)
        blocs1 += bs
    self.etape("on remplace", blocs1)
    cur = f
    if op == "*":
        cur = self.preparer_produit(cur)
    else:
        cur = Op("/", f.a, f.b)
    L = self.boucle(cur.a, cur.b)
    if self.constante is not None:
        c, Lc = self.constante
        L2 = LA._produit(Lc, L)
        self.etape("on n'oublie pas la constante", [self.txt(M(f"{T(c)} \\cdot {LT(L)} = {LT(L2)}")
                                                              + (" (une constante positive fois un nombre minuscule négatif)." if False else "."))])
        L = L2
    return L


def _m_conclure_direct(self, f, A, B, op, L):
    if op == "/":
        if A.nul() and B.inf:
            phrase = "Un nombre minuscule divisé par un nombre énorme reste minuscule :"
        elif A.inf and B.nul():
            phrase = "Un nombre énorme (positif ou négatif) divisé par un nombre minuscule devient encore plus énorme :"
        elif A.inf:
            phrase = "Un nombre énorme divisé par un nombre ordinaire reste énorme :"
        else:
            phrase = "On conclut avec les règles de calcul :"
        chaine = f"\\dfrac{{{LT(A)}}}{{{LT(B)}}} = {LT(L)}"
    else:
        if A.inf and B.inf:
            phrase = f"(règle des signes : {'+' if A.inf > 0 else '−'} · {'+' if B.inf > 0 else '−'} = {'+' if L.inf > 0 else '−'}) :"
        else:
            phrase = "On conclut avec les règles de calcul :"
        chaine = f"{LP(A)} \\cdot {LP(B)} = {LT(L)}"
    blocs = [self.txt(phrase), so.resultat_lim(f"{self.lim_tex(f)} = {chaine}")]
    if op == "/" and ((A.nul() and B.inf) or (A.inf and B.nul())):
        fm = "\\dfrac{0}{\\infty}" if A.nul() else "\\dfrac{\\infty}{0}"
        blocs.append(so.encadre("attention", "Attention", [
            f"Ici, il <b>ne faut pas</b> utiliser BH : la forme {M(fm)} n'est pas indéterminée. "
            "C'est exactement pour cela qu'on vérifie <b>toujours</b> la forme en premier."]))
    elif op == "*" and A.inf and B.inf:
        blocs.append(so.encadre("attention", "Attention", ["Pas de BH ici : un produit de deux « énormes » n'est jamais indéterminé."]))
    self.etape("on conclut directement", blocs)
    self.final_deja = True
    return L


def _m_preparer_produit(self, cur):
    """Produit 0·∞ : simplification du logarithme, constante sortie, mise en quotient ; renvoie le quotient (Op '/')."""
    pt = self.pt
    x_positif = pt.s > 0 or (pt.a is not None and pt.a == 0 and pt.d > 0)
    # (a) ln(x^k) = k ln(x)
    fs = []
    _facteurs_produit(cur, fs)
    nouveaux, change = [], []
    for g in fs:
        if isinstance(g, Fn) and g.nom == "ln" and x_positif:
            m = mono(g.a)
            if m is not None and m.coef == 1 and len(m.fact) == 1 and isinstance(m.fact[0][0], X) and m.fact[0][1] not in (1,):
                k = m.fact[0][1]
                nouveaux.append(Op("*", Nb(F(k)), Fn("ln", X())))
                change.append((g, k))
                continue
        nouveaux.append(g)
    if change:
        g2 = _produit(nouveaux)
        nv = mono_arbre(mono(g2))
        if not egaux(cur, nv):
            raise Abandon("simplification du logarithme non confirmée")
        g, k = change[0]
        self.etape("on simplifie le logarithme", [self.txt(
            f"Propriété des logarithmes : {M(T(g) + ' = ' + str(k) + chr(92) + 'ln(x)')}. Donc"),
            self.disp(f"{T(cur)} = {T(nv)}")])
        cur = nv
    # (b) constante : e^(ax+b) = e^(ax)·e^b
    fs = []
    _facteurs_produit(cur, fs)
    cstes, reste = [], []
    for g in fs:
        if isinstance(g, Fn) and g.nom == "exp":
            P = _poly(g.a)
            if P is not None and len(P) == 2 and P[0] != 0:
                cstes.append(Fn("exp", Nb(P[0])))
                reste.append(Fn("exp", LA._arbre_poly([F(0), P[1]])))
                continue
        reste.append(g)
    if cstes:
        c = _produit(cstes)
        g2 = Op("*", c, _produit(reste))
        if not egaux(cur, g2):
            raise Abandon("constante non confirmée")
        Lc = lim(c, pt)
        v = float(charger_sympy().N(Lc.val))
        sign = "positive" if v > 0 else "négative"
        P0 = next(_poly(g.a)[0] for g in fs if isinstance(g, Fn) and g.nom == "exp" and _poly(g.a) and len(_poly(g.a)) == 2 and _poly(g.a)[0] != 0)
        self.etape("on sort la constante", [
            self.txt(f"Propriété des puissances : {M(T(fs[[isinstance(g, Fn) and g.nom == 'exp' and _poly(g.a) and len(_poly(g.a)) == 2 and _poly(g.a)[0] != 0 for g in fs].index(True)]) + ' = ' + T(reste[[isinstance(g, Fn) and g.nom == 'exp' for g in reste].index(True)]) + chr(92) + 'cdot ' + T(c))}. "
                     f"Le nombre {M(T(c) + ' ' + chr(92) + 'approx ' + fmt_approx(v))} est une <b>constante {sign}</b> : elle ne change "
                     + ("ni le signe ni " if v > 0 else "pas ") + "le résultat « 0 ou ∞ ». On la garde de côté :"),
            self.disp(f"{T(cur)} = {T(c)} \\cdot {T(_produit(reste))}")])
        self.constante = (c, Lc)
        cur = _produit(reste)
    # (c) produit → quotient
    fs = []
    _facteurs_produit(cur, fs)
    pt_zero = [g for g in fs if not sans_x(g) and lim(g, pt).nul()]
    if len(pt_zero) != 1:
        raise Abandon("facteur tendant vers 0 non unique")
    z = pt_zero[0]
    autres = [g for g in fs if g is not z]
    haut = _produit(autres) if len(autres) > 1 else autres[0]
    if isinstance(haut, Op) and haut.op == "*" and isinstance(haut.a, Nb):
        pass
    bas = LA._inverse_en_bas(z)
    q = Op("/", haut, bas)
    if not egaux(cur, q):
        raise Abandon("quotient non confirmé")
    # le haut est mis sous forme normale (3 e^{-x} ln x)
    haut_n = mono_arbre(mono(haut))
    q = Op("/", haut_n, bas)
    blocs = [self.txt(f"BH ne marche pas sur un produit. On écrit {M(T(z) + ' = ' + T(Op('/', Nb(F(1)), bas)))} :"),
             self.disp(f"{T(cur)} = {T(q)}")]
    if any(isinstance(g, Fn) and g.nom == "ln" for g in autres):
        ln_g = next(g for g in autres if isinstance(g, Fn) and g.nom == "ln")
        blocs.append(self.txt(f"<i>Pourquoi garder {M(T(ln_g))} en haut ? Parce que sa dérivée {M(T(_embellir(LA._derivee_nat(ln_g))))} est simple. "
                              f"Si on mettait {M(chr(92) + 'dfrac{1}{' + T(ln_g) + '}')} en bas, sa dérivée serait compliquée.</i>"))
    self.etape("on transforme le produit en quotient", blocs)
    # (d) on vérifie la forme
    an = self.analyse(q)
    if an[0] != "ind":
        raise Abandon("le quotient n'est pas indéterminé")
    _, nom, A, B, _ = an
    self.etape("on vérifie la forme", [self.txt(self.texte_haut_bas(q) + self.forme_phrase(nom, A, B, "/"))])
    self.forme_deja = True
    return q


def _m_boucle(self, N, Dn):
    """Boucle BH sur N/Dn (forme indéterminée) ; renvoie la limite finale. Les étapes sont ajoutées à self.etapes."""
    pt = self.pt
    encore = False
    while True:
        self.n_bh += 1
        if self.n_bh > MAX_BH:
            raise Abandon("plus de quatre BH")
        dN, dD = derive(N), derive(Dn)
        intro = intro_derivee(N) + intro_derivee(Dn)
        q = Op("/", dN, dD)
        C = mono_arbre(mono(q)) if mono(q) is not None else q
        if not egaux(q, C):
            raise Abandon("simplification non confirmée")
        identique = T(C) == T(q)
        simple = not _a_fraction(dN) and not _a_fraction(dD)
        commun = _commun(dN, dD)
        blocs = []
        if intro:
            blocs.append(self.txt(" ".join(intro)))
        blocs.append(so.bh(T(N), tex_derivee(dN), T(Dn), tex_derivee(dD)))
        chaine = f"{self.lim_tex(Op('/', N, Dn))} \\overset{{\\text{{BH}}}}{{=}} \\lim_{{x\\to {pt.tex()}}} {T(q)}"
        note = None
        sep_etape = False
        if not identique:
            if simple or commun is not None:
                chaine += f" = \\lim_{{x\\to {pt.tex()}}} {T(C)}"
                if commun is not None and not simple:
                    note = f"(Les deux {M(T(commun))} se simplifient.)"
            else:
                sep_etape = True
        blocs.append(self.disp(chaine))
        if note:
            blocs.append(self.txt(note))
        cur = C if (not identique) else q
        cur = desigmer(cur)
        an = self.analyse(cur)
        titre = "BH"
        etape_bh = {"titre": titre, "blocs": None}
        if not sep_etape:
            if an[0] == "ind":
                blocs.append(self.txt(self.forme_phrase(an[1], an[2], an[3], an[4], encore=True)))
            self.etapes.append({"titre": "BH", "blocs": [b for b in blocs if b], "bh": True})
        else:
            self.etapes.append({"titre": "BH", "blocs": [b for b in blocs if b], "bh": True})
            dd = Op("/", Nb(F(1)), dD) if not (isinstance(dD, Op) and dD.op == "/") else Op("/", dD.b, dD.a)
            inter = Op("*", dN, mono_arbre(mono(dd)) if mono(dd) is not None else dd)
            expl = "Diviser par une fraction, c'est multiplier par son inverse :"
            if isinstance(dD, Op) and dD.op == "/" and isinstance(dD.a, Nb) and dD.a.v == 1:
                expl = f"Diviser par {M(T(dD))}, c'est multiplier par {M(T(dD.b))} :"
            egal = f"{T(q)} = {T(inter)}" if T(inter) != T(C) else f"{T(q)}"
            ch2 = f"{T(q)} = {T(inter)} = {T(C)}" if T(inter) != T(C) else f"{T(q)} = {T(C)}"
            if not egaux(inter, q):
                raise Abandon("simplification intermédiaire non confirmée")
            b2 = [self.txt(expl), self.disp(ch2)]
            if an[0] == "ind":
                b2.append(self.txt(self.forme_phrase(an[1], an[2], an[3], an[4], encore=True)))
            self.etape("on simplifie", b2)
        if an[0] == "ind":
            N, Dn = cur.a, cur.b
            encore = True
            continue
        # forme déterminée : on remplace
        L = an[1]
        self.etape("on remplace", [self.txt(phrase_remplace_final(cur, pt))])
        return L


def _m_composee(self, f):
    pt = self.pt
    u = f.a
    ext = "l'exposant" if f.nom == "exp" else "l'intérieur du ln"
    try:
        Lu = lim(u, pt)
        direct = True
    except LA.FormeIndeterminee:
        direct = False
    mot = "Exposant" if f.nom == "exp" else "Intérieur"
    if direct:
        L = LA._exp_lim(Lu) if f.nom == "exp" else LA._ln_lim(Lu)
        d = detail(u, pt)
        phrase = f"{mot} : " + M(d if d else plain(u, pt)) + "."
        phrase += " Donc " + M(f"{T(f)} \\to " + (f"e^{{{LT(Lu)}}}" if f.nom == "exp" else f"\\ln({LT(Lu)})") + f" = {LT(L)}") + "."
        self.etape("on remplace", [self.txt(phrase), so.resultat_lim(f"{self.lim_tex(f)} = {LT(L)}")])
        self.final_deja = True
        return L
    if not (isinstance(u, Op) and u.op == "/"):
        raise Abandon("exposant indéterminé qui n'est pas un quotient")
    nom, A, B = forme(u, pt)
    if nom not in ("0/0", "∞/∞"):
        raise Abandon("forme de l'exposant")
    blocs = [self.txt(self.texte_haut_bas(u) + self.forme_phrase(nom, A, B, "/"))]
    attendu = None
    try:
        bp, attendu = self.prediction_exposant(u, f)
        blocs.append(bp)
    except Sans_podium:
        pass
    chaine, Lu = self.bh_compact(u.a, u.b)
    blocs.append(self.txt("Calcul avec BH :"))
    blocs.append(self.disp(chaine))
    titre = "limite de l'exposant, à part" if f.nom == "exp" else "limite de l'intérieur du ln"
    self.etape(titre, blocs)
    L = LA._exp_lim(Lu) if f.nom == "exp" else LA._ln_lim(Lu)
    ap = ""
    if not L.inf and not L.nul():
        v = float(charger_sympy().N(L.val))
        ap = f" \\approx {fmt_approx(v)}" if not L.val.is_Rational else ""
    ent = f"e^{{{LT(Lu)}}}" if f.nom == "exp" else f"\\ln({LT(Lu)})"
    egal = f"{ent} = {LT(L)}" if ent != LT(L) else ent
    self.etape("on applique l'exponentielle" if f.nom == "exp" else "on applique le logarithme",
               [so.resultat_lim(f"{self.lim_tex(f)} = {egal}{ap}")])
    self.final_deja = True
    self.attendu_exposant = attendu
    self.Lu = Lu
    return L


def _m_bh_compact(self, N, Dn):
    pt = self.pt
    s = f"\\lim_{{x\\to {pt.tex()}}} {T(Op('/', N, Dn))}"
    for _ in range(MAX_BH):
        dN, dD = derive(N), derive(Dn)
        q = Op("/", dN, dD)
        s += " \\overset{\\text{BH}}{=} \\lim_{x\\to " + pt.tex() + "} " + T(q)
        m = mono(q)
        C = mono_arbre(m) if m is not None else q
        if not egaux(q, C):
            raise Abandon("simplification non confirmée")
        an = self.analyse(desigmer(C) if T(C) != T(q) else q)
        if an[0] == "ind":
            if T(C) != T(q):
                s += " = \\lim_{x\\to " + pt.tex() + "} " + T(C)
                C = desigmer(C)
            else:
                C = q
            s += f" \\quad \\left(\\text{{forme }} {forme_tex(an[1], an[2], an[3], an[4])}\\right)"
            N, Dn = C.a, C.b
            continue
        L = an[1]
        if T(C) != T(q) and not (isinstance(C, Nb)):
            s += " = \\lim_{x\\to " + pt.tex() + "} " + T(C)
        s += f" = {LT(L)}"
        return s, L
    raise Abandon("trop de BH")


def _m_prediction_exposant(self, u, f):
    """Podium sur l'exposant (quotient de polynômes en ±∞) : quotient des coefficients, ou plus grande puissance."""
    pt = self.pt
    if not pt.s:
        raise Sans_podium()
    P, Q = _poly(u.a), _poly(u.b)
    if P is None or Q is None:
        raise Sans_podium()
    dp, dq = len(P) - 1, len(Q) - 1
    nom = lambda d: T(Op("^", X(), Nb(F(d))) if d > 1 else X())
    cible = "exposant" if f.nom == "exp" else "intérieur"
    sA, sB = signe_lim(lim(u.a, pt)), signe_lim(lim(u.b, pt))
    if dp == dq:
        c = F(P[-1]) / F(Q[-1])
        fr = f"\\dfrac{{{qtex_(P[-1])}}}{{{qtex_(Q[-1])}}}"
        valeur = qtex_(c)
        l1 = (f"Même puissance {M(nom(dp))} en haut et en bas : égalité ! On s'attend au quotient des coefficients : "
              f"{M(fr + (' = ' + valeur if fr != valeur else ''))}.")
        lignes = [l1]
        ap = f" \\to {valeur}"
        ent = f"e^{{{valeur}}}" if f.nom == "exp" else f"\\ln({valeur})"
        fin = f"{cible} {M('\\to ' + valeur)}, donc {M((f'e^{{\\cdots}}' if f.nom == 'exp' else '\\ln(\\cdots)') + ' \\to ' + ent)}"
        genre = ("const", c)
    else:
        hg = dp > dq
        pos = "haut" if hg else "bas"
        sg = sA * sB
        gr = f"En haut {M(nom(dp))}, en bas {M(nom(dq))} : la plus grande puissance est au <b>{pos}</b>, donc {'l' + chr(39) + 'exposant part vers l' + chr(39) + 'infini' if hg else 'l' + chr(39) + 'exposant tend vers 0'}."
        if f.nom == "ln" and hg:
            gr = gr.replace("l'exposant", "l'intérieur")
        elif f.nom == "ln":
            gr = gr.replace("l'exposant", "l'intérieur")
        lignes = [gr, f"Signe : haut {signe_mot(sA)} 0, bas {signe_mot(sB)} 0, donc {'0' if not hg else ''}{'^{+}' if False else ''}"]
        # écriture du signe : 0⁺ / 0⁻ ou ±∞
        if hg:
            vu = "+\\infty" if sg > 0 else "-\\infty"
        else:
            vu = "0^{+}" if sg > 0 else "0^{-}"
        lignes[1] = f"Signe : haut {signe_mot(sA)} 0, bas {signe_mot(sB)} 0, donc {M(vu)}."
        if f.nom == "exp":
            sortie = {"+\\infty": "+\\infty", "-\\infty": "0^{+}", "0^{+}": "1", "0^{-}": "1"}[vu]
            ent = f"e^{{{vu}}}" if hg else "e^{0} = 1"
            fin = f"{cible} {M('\\to ' + vu)}, donc {M('e^{\\cdots} \\to ' + (ent if hg else 'e^{0} = 1'))}"
            if hg and vu == "-\\infty":
                fin = f"{cible} {M('\\to -\\infty')}, donc {M('e^{\\cdots} \\to 0^{+}')}"
            elif hg:
                fin = f"{cible} {M('\\to +\\infty')}, donc {M('e^{\\cdots} \\to +\\infty')}"
        else:
            fin = f"{cible} {M('\\to ' + vu)}, donc {M('\\ln(\\cdots)')} à calculer ensuite"
        genre = ("inf" if hg else "zero", sg)
        if not hg and f.nom == "exp":
            fin = f"{cible} {M('\\to ' + vu)}, donc {M('e^{\\cdots} \\to e^{0} = 1')}"
    lignes.append(f"<b>On s'attend à :</b> {fin}")
    return so.encadre("prediction", "Prédiction avec la règle du podium", lignes), genre


def qtex_(c):
    c = F(c)
    return str(c.numerator) if c.denominator == 1 else (("-" if c < 0 else "") + f"\\frac{{{abs(c.numerator)}}}{{{c.denominator}}}")


Desc.resoudre = _m_resoudre
Desc.produit_quotient = _m_produit_quotient
Desc.conclure_direct = _m_conclure_direct
Desc.preparer_produit = _m_preparer_produit
Desc.boucle = _m_boucle
Desc.composee = _m_composee
Desc.bh_compact = _m_bh_compact
Desc.prediction_exposant = _m_prediction_exposant


# ---------------------------------------------------------------------------------------------------------------------
# Point d'entrée
# ---------------------------------------------------------------------------------------------------------------------
def _signe_numerique(f, pt, L):
    """Signe de f près du point par mpmath (haute précision) ; Abandon s'il contredit la limite annoncée."""
    import mpmath
    mp = mpmath.MPContext()
    mp.dps = 80
    pts = []
    for k in (3, 5, 8):
        if pt.s:
            pts.append(pt.s * mp.mpf(10) ** k)
        else:
            a = mp.mpf(str(charger_sympy().N(pt.a, 60)))
            pts.append(a + pt.d * mp.mpf(10) ** (-k))
    sg = set()
    for x in pts:
        try:
            v = LA._val_mp(mp, f, x)
        except Exception:
            v = None
        if v is not None and v != 0:
            sg.add(1 if v > 0 else -1)
    if not sg:
        return
    attendu = signe_lim(L) if (L.inf or L.nul()) else None
    if attendu and (len(sg) != 1 or attendu not in sg):
        raise Abandon("signe contredit par la sonde")


def descente(f, pt, ref):
    """Rédaction descendante de lim f en pt (référence SymPy `ref`) : {"etapes", "alertes", "valeur"} ou Abandon."""
    if not _contient_transcendant(f):
        raise Abandon("fonction rationnelle : méthodes actuelles (R18)")
    R = LA._lim_depuis_sympy(ref)
    d = Desc(f, pt)
    d.final_deja = False
    try:
        L = d.resoudre()
    except LA.FormeIndeterminee as e:
        raise Abandon("forme indéterminée imbriquée : " + str(e))
    if not LA._meme_valeur(L, R):
        raise Abandon(f"valeur rédigée {LT(L)} ≠ référence {R.tex()}")
    _signe_numerique(f, pt, L)
    # prédiction : comparée au résultat final
    att = d.attendu
    confirme = None
    if att is not None:
        genre, sg = att
        ok = (genre == "inf" and L.inf == sg) or (genre == "zero" and L.nul() and L.ap == sg)
        if ok:
            confirme = "✓ Le calcul confirme la prédiction du podium."
        else:
            d.alertes.append(f"prédiction {att} ≠ résultat {LT(L)}")
            d.etapes = [dict(e, blocs=[b for b in e["blocs"] if not (b.get("type") == "encadre" and b.get("genre") == "prediction")])
                        for e in d.etapes]
    elif getattr(d, "attendu_exposant", None) is not None:
        genre, v = d.attendu_exposant
        Lu = d.Lu
        if genre == "const":
            ok = (not Lu.inf) and (not Lu.nul() or v == 0) and abs(float(charger_sympy().N(Lu.val)) - float(v)) < 1e-12
        else:
            ok = (genre == "inf" and Lu.inf == v) or (genre == "zero" and Lu.nul() and Lu.ap == v)
        if ok:
            confirme = "✓ Le calcul confirme la prédiction du podium."
        else:
            d.alertes.append(f"prédiction de l'exposant {d.attendu_exposant} ≠ {LT(Lu)}")
    elif d.devine is not None:
        xs, vs = d.devine
        v = vs[-1]
        try:
            ok = (not L.inf) and abs(float(v.replace("{,}", ".").replace("\\approx ", "")) - float(charger_sympy().N(L.val))) < 1e-3
        except Exception:
            ok = False
        if ok:
            confirme = "La calculatrice avait bien « deviné » : le calcul le confirme."
        else:
            d.alertes.append("valeurs de la calculatrice non cohérentes avec le résultat")
    if not d.final_deja:
        dernier = d.etapes[-1]
        dernier["blocs"].append(so.resultat_lim(f"{d.lim_tex(f)} = {LT(L)}"))
    if confirme:
        d.etapes[-1]["blocs"].append(so.texte(confirme, style="confirme"))
    return {"etapes": d.etapes, "alertes": d.alertes, "valeur": L}
