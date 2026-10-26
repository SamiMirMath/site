"""
factorisation.py — Factorisation pas à pas, avec les méthodes du cours de 1M.

Principe
--------
* La JUSTESSE vient de SymPy : on sait toujours quelle est la factorisation
  complète (sur Q), et à la fin on vérifie que le résultat affiché, une fois
  développé, redonne exactement l'expression de départ. Un résultat faux ne
  peut donc pas être affiché.
* La PÉDAGOGIE vient d'une cascade de méthodes essayées dans l'ordre du cours,
  appliquée récursivement à chaque facteur obtenu, jusqu'à ce que plus rien ne
  se factorise :
      1. mise en évidence (facteur commun, y compris composé comme (a-b))
      2. identités remarquables : différence de carrés, carré parfait,
         somme/différence de cubes, cube d'un binôme
      3. trinôme du 2e degré : Somme-Produit, zéro évident, formule
      4. changement de variable (u = x^n)
      5. groupements
      6. racine évidente et division (degré >= 3)
  Un facteur qui ne se factorise plus est une fin normale, pas une erreur. Si
  une expression se factorise mais qu'aucune méthode du cours ne s'applique,
  on donne quand même la factorisation (calculée par SymPy), en le disant.

Références : manuel de 1re, « Notions élémentaires d'algèbre », §2.2 ; manuel de 1re,
« Algèbre 1M », §2.4 et exercices 2.11 à 2.16.
"""
from fractions import Fraction as F
import math
import json
import random
import re

from noyau import json_strict, ErreurSaisie, trinome, qtex, charger_sympy

__all__ = ["factoriser_json", "apercu_json", "exercice_json"]

BORNE = 3000          # recherche bornée des diviseurs (Somme-Produit, zéro évident)
PROF_MAX = 40         # garde-fou contre une récursion qui ne finirait pas
MAX_PARTITIONS = 120  # nombre maximal de façons de grouper les termes essayées


# =====================================================================
# 1. SAISIE : arbre syntaxique maison (sans SymPy, pour l'aperçu immédiat)
# =====================================================================
# Chaque lettre a..z est une variable ; "ab" signifie a·b. Nœuds :
#   ("num", Fraction, texte) ("var", "x") ("neg", n) ("add", [n...])
#   ("mul", [n...]) ("div", n, n) ("pow", n, entier) ("par", n)
_REMPLACEMENTS = [("−", "-"), ("–", "-"), ("·", "*"), ("×", "*"), ("**", "^"), ("²", "^2"),
                  ("³", "^3"), ("{", "("), ("}", ")"), ("[", "("), ("]", ")"), (":", "/"), ("÷", "/")]
_FONCTIONS = re.compile(r"sqrt|racine|ln|log|exp")


def _tokeniser(s):
    toks, i = [], 0
    while i < len(s):
        c = s[i]
        if c.isspace():
            i += 1
            continue
        if c.isdigit() or (c in ".," and i + 1 < len(s) and s[i + 1].isdigit()):
            j = i
            while j < len(s) and s[j].isdigit():
                j += 1
            if j < len(s) and s[j] in ".," and j + 1 < len(s) and s[j + 1].isdigit():
                j += 1
                while j < len(s) and s[j].isdigit():
                    j += 1
            toks.append(("nb", s[i:j]))
            i = j
            continue
        if "a" <= c <= "z":
            toks.append(("var", c))
            i += 1
            continue
        if c in "+-*/^()":
            toks.append(("op", c))
            i += 1
            continue
        raise ErreurSaisie(f"Caractère non reconnu : « {c} ».")
    return toks


def _valeur_constante(n):
    """Valeur (Fraction) d'un sous-arbre sans lettre, None s'il contient une lettre."""
    k = n[0]
    if k == "num":
        return n[1]
    if k == "var":
        return None
    if k in ("par", "neg"):
        v = _valeur_constante(n[1])
        return None if v is None else (v if k == "par" else -v)
    if k in ("add", "mul"):
        acc = F(0) if k == "add" else F(1)
        for c in n[1]:
            v = _valeur_constante(c)
            if v is None:
                return None
            acc = acc + v if k == "add" else acc * v
        return acc
    if k == "div":
        a, b = _valeur_constante(n[1]), _valeur_constante(n[2])
        if a is None or b is None:
            return None
        if b == 0:
            raise ErreurSaisie("Division par zéro.")
        return a / b
    if k == "pow":
        b = _valeur_constante(n[1])
        return None if b is None else b ** n[2]
    return None


class _Parseur:
    def __init__(self, toks):
        self.t, self.i = toks, 0

    def voir(self):
        return self.t[self.i] if self.i < len(self.t) else (None, None)

    def manger(self, op):
        if self.voir() == ("op", op):
            self.i += 1
            return True
        return False

    def tout(self):
        if not self.t:
            raise ErreurSaisie("Entrez une expression, par exemple x^2+5x-14.")
        a = self.expr()
        if self.i < len(self.t):
            raise ErreurSaisie(f"Expression mal formée près de « {self.t[self.i][1]} ».")
        return a

    def expr(self):
        enf = [self.terme()]
        while True:
            if self.manger("+"):
                enf.append(self.terme())
            elif self.manger("-"):
                enf.append(("neg", self.terme()))
            else:
                break
        return enf[0] if len(enf) == 1 else ("add", enf)

    def debut(self):
        k, v = self.voir()
        return k in ("nb", "var") or (k, v) == ("op", "(")

    def terme(self):
        enf = [self.unaire()]
        while True:
            if self.manger("*"):
                enf.append(self.unaire())
            elif self.manger("/"):
                gauche = enf[0] if len(enf) == 1 else ("mul", enf)
                enf = [("div", gauche, self.unaire())]
            elif self.debut():
                enf.append(self.puissance())
            else:
                break
        return enf[0] if len(enf) == 1 else ("mul", enf)

    def unaire(self):
        if self.manger("-"):
            return ("neg", self.unaire())
        if self.manger("+"):
            return self.unaire()
        return self.puissance()

    def puissance(self):
        b = self.primaire()
        if self.manger("^"):
            e = _valeur_constante(self.unaire())
            if e is None:
                raise ErreurSaisie("Un exposant doit être un nombre, pas une lettre.")
            if e.denominator != 1 or e < 0:
                raise ErreurSaisie("Seuls les exposants entiers positifs sont permis (c'est un polynôme).")
            if e > 60:
                raise ErreurSaisie("Exposant trop grand.")
            return ("pow", b, int(e))
        return b

    def primaire(self):
        k, v = self.voir()
        if k == "nb":
            self.i += 1
            return ("num", F(v.replace(",", ".")), v)
        if k == "var":
            self.i += 1
            return ("var", v)
        if self.manger("("):
            a = self.expr()
            if not self.manger(")"):
                raise ErreurSaisie("Parenthèse fermante manquante.")
            return ("par", a)
        if k is None:
            raise ErreurSaisie("Expression incomplète.")
        raise ErreurSaisie(f"Symbole inattendu « {v} ».")


def analyser(entree):
    s = str(entree).strip()
    for a, b in _REMPLACEMENTS:
        s = s.replace(a, b)
    s = s.lower()
    if "=" in s:
        gauche, _, droite = s.partition("=")
        if droite.strip() not in ("", "0"):
            raise ErreurSaisie("Écris seulement l'expression à factoriser (sans « = »).")
        s = gauche
    if _FONCTIONS.search(s):
        raise ErreurSaisie("Pas de fonction ici (ln, exp, racine…) : seulement des polynômes, "
                           "par exemple x^2-4 ou ax+bx.")
    return _Parseur(_tokeniser(s)).tout()


def _sans_parentheses(n):
    while n[0] == "par":
        n = n[1]
    return n


def lettres_arbre(n, acc=None):
    acc = [] if acc is None else acc
    if n[0] == "var":
        if n[1] not in acc:
            acc.append(n[1])
    elif n[0] in ("add", "mul"):
        for c in n[1]:
            lettres_arbre(c, acc)
    elif n[0] in ("neg", "par"):
        lettres_arbre(n[1], acc)
    elif n[0] == "div":
        lettres_arbre(n[1], acc)
        lettres_arbre(n[2], acc)
    elif n[0] == "pow":
        lettres_arbre(n[1], acc)
    return acc


# ---------- écriture LaTeX fidèle à la saisie ----------
def _prec(n):
    return {"add": 1, "neg": 1.5, "mul": 2, "div": 2, "pow": 3}.get(n[0], 4)


def tex_arbre(n):
    k = n[0]
    if k == "num":
        return n[2].replace(",", "{,}").replace(".", "{,}")
    if k == "var":
        return n[1]
    if k == "par":
        return r"\left(" + tex_arbre(n[1]) + r"\right)"
    if k == "neg":
        t = tex_arbre(n[1])
        return "-" + (r"\left(" + t + r"\right)" if _prec(n[1]) < 2 else t)
    if k == "add":
        s = tex_arbre(n[1][0])
        for c in n[1][1:]:
            if c[0] == "neg":
                t = tex_arbre(c[1])
                s += " - " + (r"\left(" + t + r"\right)" if _prec(c[1]) < 2 else t)
            else:
                s += " + " + tex_arbre(c)
        return s
    if k == "mul":
        out = ""
        for idx, c in enumerate(n[1]):
            t = tex_arbre(c)
            if _prec(c) < 2 and not (idx == 0 and c[0] == "neg"):
                t = r"\left(" + t + r"\right)"
            if idx and (t[:1].isdigit() or t[:1] == "-"):
                out += r" \cdot "
            out += t
        return out
    if k == "div":
        return r"\frac{" + tex_arbre(n[1]) + "}{" + tex_arbre(n[2]) + "}"
    # puissance
    b = n[1]
    tb = tex_arbre(b)
    atome = b[0] in ("var", "par") or (b[0] == "num" and b[1] >= 0 and b[1].denominator == 1)
    if not atome:
        tb = r"\left(" + tb + r"\right)"
    return tb + "^{" + str(n[2]) + "}"


# =====================================================================
# 2. POLYNÔMES (SymPy) : ordre des termes, écriture, contenu, pgcd
# =====================================================================
def _ratio(c):
    """Rationnel SymPy -> Fraction."""
    return F(int(c.p), int(c.q))


def qtx(c):
    return qtex(_ratio(c))


def _iroot(n, k):
    """Racine k-ième entière exacte de n >= 0, ou None."""
    if n < 0:
        return None
    if n < 2:
        return n
    if n.bit_length() < 900:
        r = int(round(n ** (1.0 / k)))
        for c in (r - 1, r, r + 1):
            if c >= 0 and c ** k == n:
                return c
        return None
    lo, hi = 0, 1 << (n.bit_length() // k + 1)
    while lo <= hi:
        mid = (lo + hi) // 2
        p = mid ** k
        if p == n:
            return mid
        if p < n:
            lo = mid + 1
        else:
            hi = mid - 1
    return None


def _gens(P):
    return sorted(P.free_symbols, key=str)


def _coef_mono(a, mono):
    """a > 0 rationnel devant un monôme : 3x, x, \\frac{x}{2}, \\frac{3x^{2}}{4}."""
    if not mono:
        return qtx(a)
    if a == 1:
        return mono
    if a.q == 1:
        return qtx(a) + mono
    return r"\frac{" + ("" if a.p == 1 else str(a.p)) + mono + "}{" + str(a.q) + "}"


class Ctx:
    """État d'un calcul : SymPy, lettres, étapes rédigées, méthodes utilisées."""

    def __init__(self, sp, lettres):
        self.sp = sp
        self.noms = set(lettres)
        self.etapes = []
        self.groupes = []     # méthode de chaque étape (parallèle à etapes) ; None = étape sans méthode propre
        self._marque = 0      # première étape pas encore rattachée à une méthode
        self.methodes = []
        self.reel = False   # True si l'expression est un trinôme à une variable (formule sur R)

    def dire(self, html):
        self.etapes.append({"type": "texte", "html": html})
        self.groupes.append(None)

    def inserer(self, i, html):
        self.etapes.insert(i, {"type": "texte", "html": html})
        self.groupes.insert(i, None)
        if i < self._marque:
            self._marque += 1

    def marquer(self, m=None):
        """Rattache à la méthode `m` les étapes dites depuis le dernier marquage (T21 : une carte par application)."""
        for i in range(self._marque, len(self.etapes)):
            self.groupes[i] = m
        self._marque = len(self.etapes)

    def methode(self, m):
        if m not in self.methodes:
            self.methodes.append(m)
        self.marquer(m)

    def paire_libre(self):
        for a, b in (("u", "v"), ("p", "q"), ("m", "n"), ("r", "s"), ("k", "l")):
            if a not in self.noms and b not in self.noms:
                return a, b
        return r"\alpha", r"\beta"

    def symbole_libre(self):
        for nom in ("u", "v", "w", "z", "t", "s", "k"):
            if nom not in self.noms:
                self.noms.add(nom)
                return self.sp.Symbol(nom)
        return self.sp.Symbol("U")

    # --- outils polynomiaux ---
    def termes_tries(self, P):
        """[(coef, exposants)] dans l'ordre d'écriture : degré total décroissant,
        puis ordre lexicographique (lettres par ordre alphabétique)."""
        sp = self.sp
        gens = _gens(P)
        tt = [(c, m) for m, c in sp.Poly(P, *gens).terms()]
        tt.sort(key=lambda cm: (-sum(cm[1]), tuple(-e for e in cm[1])))
        return gens, tt

    def coef_tete(self, P):
        P = self.sp.expand(P)
        if P.is_number:
            return P
        return self.termes_tries(P)[1][0][0]

    def tex_poly(self, P):
        sp = self.sp
        P = sp.expand(P)
        if P.is_number:
            return qtx(sp.Rational(P))
        gens, tt = self.termes_tries(P)
        # (−x + 1) s'écrit plus naturellement (1 − x)
        if len(tt) == 2 and tt[0][0] < 0 and tt[1][0] > 0:
            tt = [tt[1], tt[0]]
        out = ""
        for i, (c, m) in enumerate(tt):
            mono = "".join(str(g) + ("^{" + str(e) + "}" if e > 1 else "") for g, e in zip(gens, m) if e)
            corps = _coef_mono(abs(c), mono)
            if i == 0:
                out += ("-" if c < 0 else "") + corps
            else:
                out += (" - " if c < 0 else " + ") + corps
        return out

    def contenu(self, P):
        """Contenu positif : pgcd des numérateurs / ppcm des dénominateurs."""
        sp = self.sp
        P = sp.expand(P)
        if P.is_number:
            return abs(sp.Rational(P))
        num, den = 0, 1
        for c in sp.Poly(P, *_gens(P)).coeffs():
            fr = _ratio(c)
            num = math.gcd(num, abs(fr.numerator))
            den = den * fr.denominator // math.gcd(den, fr.denominator)
        return sp.Rational(num, den)

    def normaliser(self, P):
        """P = c · B, avec B à coefficients entiers premiers entre eux et premier
        terme (dans l'ordre d'écriture) positif."""
        sp = self.sp
        c = self.contenu(P)
        if self.coef_tete(P) < 0:
            c = -c
        return c, sp.expand(P / c)

    def pgcd(self, valeurs):
        """Plus grand facteur commun (numérique et polynomial), contenu positif."""
        sp = self.sp
        vals = [sp.expand(v) for v in valeurs]
        vals = [v for v in vals if v != 0]
        if len(vals) < 2:
            return sp.Integer(1)
        num, den = 0, 1
        prims = []
        for v in vals:
            c = self.contenu(v)
            fr = _ratio(c)
            num = math.gcd(num, fr.numerator)
            den = den * fr.denominator // math.gcd(den, fr.denominator)
            prims.append(sp.expand(v / c))
        g = sp.expand(sp.gcd_list(prims))
        if g.is_number:
            g = sp.Integer(1)
        else:
            g = self.normaliser(g)[1]
        return sp.expand(sp.Rational(num, den) * g)

    def decomposer(self, P):
        """P = c · ∏ base^e (bases : lettres ou polynômes normalisés), via SymPy."""
        sp = self.sp
        c, lst = sp.factor_list(sp.expand(P))
        c = sp.Rational(c)
        lettres, polys = [], []
        for f, m in lst:
            f = sp.expand(f)
            if f.is_Symbol:
                lettres.append([f, m])
                continue
            cf, bf = self.normaliser(f)
            c *= cf ** m
            polys.append([bf, m])
        lettres.sort(key=lambda bm: str(bm[0]))
        return c, lettres + polys

    def irreductible(self, P):
        _, lst = self.sp.factor_list(P)
        return len(lst) == 1 and lst[0][1] == 1


# =====================================================================
# 3. TERMES « ÉCRITS » : un terme = coefficient × produit de puissances
# =====================================================================
# On garde la structure de ce que l'élève a écrit (ex. le terme y(b−a)) : c'est
# ce qui permet de mettre (b−a) en évidence, ou de voir que (a+b)² est un carré.
class Terme:
    def __init__(self, coef, bases=None):
        self.coef = coef
        self.bases = [list(b) for b in (bases or [])]   # [base, exposant]

    def valeur(self):
        v = self.coef
        for b, e in self.bases:
            v = v * b ** e
        return v

    def monome(self):
        return all(b.is_Symbol for b, _ in self.bases)


def _egal(sp, a, b):
    return sp.expand(a - b) == 0


def _fusion(sp, bases):
    out = []
    for b, e in bases:
        for item in out:
            if _egal(sp, item[0], b):
                item[1] += e
                break
        else:
            out.append([b, e])
    return [it for it in out if it[1] > 0]


def produit_termes(ctx, t1, t2):
    return Terme(t1.coef * t2.coef, _fusion(ctx.sp, t1.bases + t2.bases))


def puissance_terme(t, k):
    return Terme(t.coef ** k, [[b, e * k] for b, e in t.bases])


def terme_depuis_expr(ctx, P):
    sp = ctx.sp
    P = sp.expand(P)
    if P == 0 or P.is_number:
        return Terme(sp.Rational(P))
    monos = termes_monomes(ctx, P)
    if len(monos) == 1:
        return monos[0]
    c, b = ctx.normaliser(P)
    return Terme(c, [[b, 1]])


def termes_monomes(ctx, P):
    sp = ctx.sp
    P = sp.expand(P)
    if P.is_number:
        return [Terme(sp.Rational(P))]
    gens, tt = ctx.termes_tries(P)
    return [Terme(c, [[g, e] for g, e in zip(gens, m) if e]) for c, m in tt]


def vers_sympy(ctx, syms, n):
    sp = ctx.sp
    k = n[0]
    if k == "num":
        return sp.Rational(n[1].numerator, n[1].denominator)
    if k == "var":
        return syms[n[1]]
    if k == "par":
        return vers_sympy(ctx, syms, n[1])
    if k == "neg":
        return -vers_sympy(ctx, syms, n[1])
    if k == "add":
        return sp.Add(*[vers_sympy(ctx, syms, c) for c in n[1]])
    if k == "mul":
        return sp.Mul(*[vers_sympy(ctx, syms, c) for c in n[1]])
    if k == "div":
        d = _valeur_constante(n[2])
        if d is None:
            raise ErreurSaisie("La division n'est permise que par un nombre "
                               "(sinon ce n'est pas un polynôme).")
        return vers_sympy(ctx, syms, n[1]) / sp.Rational(d.numerator, d.denominator)
    return vers_sympy(ctx, syms, n[1]) ** n[2]


def terme_arbre(ctx, syms, n):
    """Terme écrit correspondant au nœud n (un produit, pas une somme)."""
    sp = ctx.sp
    k = n[0]
    if k == "num":
        return Terme(sp.Rational(n[1].numerator, n[1].denominator))
    if k == "var":
        return Terme(sp.Integer(1), [[syms[n[1]], 1]])
    if k == "neg":
        t = terme_arbre(ctx, syms, n[1])
        t.coef = -t.coef
        return t
    if k == "mul":
        t = Terme(sp.Integer(1))
        for c in n[1]:
            t = produit_termes(ctx, t, terme_arbre(ctx, syms, c))
        return t
    if k == "div":
        t = terme_arbre(ctx, syms, n[1])
        d = _valeur_constante(n[2])
        if d is None:
            raise ErreurSaisie("La division n'est permise que par un nombre "
                               "(sinon ce n'est pas un polynôme).")
        t.coef = t.coef / sp.Rational(d.numerator, d.denominator)
        return t
    if k == "pow":
        return puissance_terme(terme_arbre(ctx, syms, n[1]), n[2])
    interieur = _sans_parentheses(n)
    if interieur[0] == "add":
        return terme_depuis_expr(ctx, vers_sympy(ctx, syms, interieur))
    return terme_arbre(ctx, syms, interieur)


def termes_ecrits(ctx, syms, n):
    n = _sans_parentheses(n)
    enfants = n[1] if n[0] == "add" else [n]
    return [terme_arbre(ctx, syms, c) for c in enfants]


# ---------- écriture LaTeX d'un terme, d'une somme, d'un produit ----------
def tex_terme(ctx, t, signe=True, absorber=False):
    """absorber=True : −(a−b) s'écrit (b−a) quand c'est possible (terme isolé)."""
    sp = ctx.sp
    coef = t.coef
    bases = [list(b) for b in t.bases]
    if absorber and coef < 0:
        for item in bases:
            if not item[0].is_Symbol and item[1] % 2 == 1:
                item[0] = sp.expand(-item[0])
                coef = -coef
                break
    lettres = sorted((b for b in bases if b[0].is_Symbol), key=lambda bm: str(bm[0]))
    polys = [b for b in bases if not b[0].is_Symbol]
    corps = ""
    for b, e in lettres + polys:
        s = str(b) if b.is_Symbol else r"\left(" + ctx.tex_poly(b) + r"\right)"
        corps += s + ("^{" + str(e) + "}" if e > 1 else "")
    a = abs(coef)
    if polys:
        txt = corps if a == 1 else qtx(a) + corps
    else:
        txt = _coef_mono(a, corps)
    return ("-" + txt) if (coef < 0 and signe) else txt


def tex_racine(ctx, t):
    """Écriture de A ou B dans « avec A = … et B = … » : a + b plutôt que (a + b)."""
    if len(t.bases) == 1 and not t.bases[0][0].is_Symbol and t.bases[0][1] == 1 and abs(t.coef) == 1:
        return ctx.tex_poly(t.valeur())
    return tex_terme(ctx, t, absorber=True)


def tex_somme(ctx, termes):
    out = ""
    for i, t in enumerate(termes):
        s = tex_terme(ctx, t, signe=False)
        if i == 0:
            out += ("-" if t.coef < 0 else "") + s
        else:
            out += (" - " if t.coef < 0 else " + ") + s
    return out


class Facteur:
    def __init__(self, expr, tex, mult=1):
        self.expr, self.tex, self.mult = expr, tex, mult

    @property
    def est_lettre(self):
        return self.expr.is_Symbol


def tex_produit(ctx, const, facteurs):
    lettres = sorted((f for f in facteurs if f.est_lettre), key=lambda f: str(f.expr))
    polys = [f for f in facteurs if not f.est_lettre]
    if not facteurs:
        return qtx(const)
    if const == 1 and not lettres and len(polys) == 1 and polys[0].mult == 1:
        return polys[0].tex
    corps = ""
    for f in lettres:
        corps += str(f.expr) + ("^{" + str(f.mult) + "}" if f.mult > 1 else "")
    for f in polys:
        corps += r"\left(" + f.tex + r"\right)" + ("^{" + str(f.mult) + "}" if f.mult > 1 else "")
    tete = "" if const == 1 else ("-" if const == -1 else qtx(const))
    return tete + corps


def combiner(ctx, const, facteurs):
    """Regroupe les facteurs égaux (ou opposés) en puissances."""
    sp = ctx.sp
    out = []
    for f in facteurs:
        for g in out:
            if _egal(sp, g.expr, f.expr):
                g.mult += f.mult
                break
            if _egal(sp, g.expr, -f.expr):
                g.mult += f.mult
                const = const * (-1) ** f.mult
                break
        else:
            out.append(Facteur(f.expr, f.tex, f.mult))
    return const, out


def facteurs_affichage(ctx, g):
    """Facteurs de g pour l'affichage ; un signe − est absorbé dans un facteur
    de degré impair : (b−a) plutôt que −(a−b)."""
    sp = ctx.sp
    c, bases = ctx.decomposer(g)
    facts = [Facteur(b, str(b) if b.is_Symbol else ctx.tex_poly(b), e) for b, e in bases]
    if c < 0:
        for f in facts:
            if not f.est_lettre and f.mult % 2 == 1:
                f.expr = sp.expand(-f.expr)
                f.tex = ctx.tex_poly(f.expr)
                c = -c
                break
    return c, facts


def _puissance_resultat(ctx, c, facteurs, m):
    return c ** m, [Facteur(f.expr, f.tex, f.mult * m) for f in facteurs]


# =====================================================================
# 4. MOTEUR RÉCURSIF
# =====================================================================
def fact(P, ctx, ecrits=None, tex_hint=None, prof=0, ident=False):
    """Factorisation complète de P (polynôme SymPy). Renvoie (constante, [Facteur])
    et rédige les étapes dans ctx. ident=True : P vient d'une identité remarquable
    (ex. a − 1/4) et on ne le réécrit pas si c'est déjà un facteur du 1er degré."""
    sp = ctx.sp
    P = sp.expand(P)
    if P.is_number:
        return sp.Rational(P), []
    T = tex_hint or ctx.tex_poly(P)
    if prof > PROF_MAX:
        return repli(P, ctx, T, prof)
    monos = termes_monomes(ctx, P)
    if ecrits and len(ecrits) >= 2 and (len(monos) == 1 or sp.Poly(P, *_gens(P)).total_degree() == 1):
        # une somme écrite qui se réduit à un monôme ou au 1er degré, (x+1)² − (x−1)² = 4x, (x+3)² − (x−1)² = 8x + 8 :
        # l'identité se lit sur les termes écrits (FA-05)
        m = reconnaitre_identite(ctx, ecrits)
        if m:
            return appliquer_identite(m, ctx, T, prof)
    if len(monos) == 1:
        t = monos[0]
        return t.coef, [Facteur(b, str(b), e) for b, e in t.bases]
    if not ecrits or len(ecrits) < 2:
        ecrits = monos

    r = mise_en_evidence(P, ctx, ecrits, T, prof)
    if r:
        return r
    gens = _gens(P)
    if sp.Poly(P, *gens).total_degree() == 1:
        if not ident and ctx.contenu(P).q != 1:   # 2x/3 + 4/3 = 2/3·(x + 2)
            return contenu_fractionnaire(P, ctx, T, prof)
        return sp.Integer(1), [Facteur(P, T, 1)]
    if len(gens) == 1:
        return fact_une_variable(P, gens[0], ctx, ecrits, monos, T, prof)
    return fact_plusieurs_variables(P, ctx, ecrits, monos, T, prof)


# ---------- 4.1 mise en évidence ----------
def diviser_terme(ctx, t, g):
    """t / g, en gardant la structure écrite si g y apparaît tel quel."""
    sp = ctx.sp
    cg, bg = ctx.decomposer(g)
    bases = [list(b) for b in t.bases]
    for b, e in bg:
        for item in bases:
            if item[1] >= e and _egal(sp, item[0], b):
                item[1] -= e
                break
        else:
            return terme_depuis_expr(ctx, sp.cancel(t.valeur() / g))
    return Terme(t.coef / cg, [it for it in bases if it[1] > 0])


def mise_en_evidence(P, ctx, ecrits, T, prof):
    sp = ctx.sp
    vals = [t.valeur() for t in ecrits]
    g = ctx.pgcd(vals)
    cg = ctx.contenu(g)
    if cg.q != 1:
        # un facteur numérique fractionnaire n'est mis en évidence qu'en dernier
        # recours (contenu_fractionnaire) : a² − 1/16 = (a − 1/4)(a + 1/4)
        # directement, comme l'élève, plutôt que 1/16·(4a − 1)(4a + 1).
        g = sp.expand(g / cg)
    if g == 1:
        if all(c < 0 for c in sp.Poly(P, *_gens(P)).coeffs()):
            g = sp.Integer(-1)   # −x − y = −(x + y)
        else:
            return None
    q1 = sp.expand(sp.cancel(vals[0] / g))
    if ctx.coef_tete(q1) < 0:
        g = -g
    quotients = [diviser_terme(ctx, t, g) for t in ecrits]
    quotients = [q for q in quotients if q.coef != 0]
    R = sp.expand(sum(q.valeur() for q in quotients))

    cG, fG = facteurs_affichage(ctx, g)
    G_tex = tex_produit(ctx, cG, fG)
    if cG == 1 and len(fG) == 1 and not fG[0].est_lettre and fG[0].mult == 1:
        G_tex = r"\left(" + G_tex + r"\right)"   # (a+b), pas a+b, devant un crochet
    structure = any(not q.monome() for q in quotients)
    if R.is_number:
        apres = tex_produit(ctx, cG * sp.Rational(R), fG)
        R_tex = None
    else:
        # dans la parenthèse, on garde l'ordre des termes de l'élève (s'il n'y a
        # pas de termes semblables à regrouper)
        cles = [tuple(sorted((str(b), e) for b, e in q.bases)) for q in quotients]
        if not structure and len(set(cles)) == len(cles):
            R_tex = tex_somme(ctx, quotients)
        else:
            R_tex = ctx.tex_poly(R)
        apres = tex_produit(ctx, cG, fG + [Facteur(R, R_tex, 1)])
    if structure:
        crochet = tex_somme(ctx, quotients)
        ctx.dire(rf"On met \({G_tex}\) en évidence (facteur commun à tous les termes) : "
                 rf"\({T} = {G_tex}\left[{crochet}\right] = {apres}\).")
    else:
        ctx.dire(rf"On met \({G_tex}\) en évidence (facteur commun à tous les termes) : "
                 rf"\({T} = {apres}\).")
    ctx.methode("Mise en évidence")

    const, facts = cG, []
    for f in fG:
        # un facteur commun du 2e degré en une lettre peut encore se scinder (formule)
        if not f.est_lettre and len(f.expr.free_symbols) == 1 and sp.degree(f.expr) == 2:
            c, ff = fact(f.expr, ctx, tex_hint=f.tex, prof=prof + 1)
            c, ff = _puissance_resultat(ctx, c, ff, f.mult)
            const *= c
            facts += ff
        else:
            facts.append(f)
    if R.is_number:
        return combiner(ctx, const * sp.Rational(R), facts)
    cR, fR = fact(R, ctx, ecrits=quotients if structure else None, tex_hint=R_tex, prof=prof + 1)
    return combiner(ctx, const * cR, facts + fR)


# ---------- 4.2 identités remarquables ----------
def _racine_rationnelle_n(sp, c, n):
    fr = _ratio(c)
    p, q = fr.numerator, fr.denominator
    signe = 1
    if p < 0:
        if n % 2 == 0:
            return None
        signe, p = -1, -p
    rp, rq = _iroot(p, n), _iroot(q, n)
    if rp is None or rq is None:
        return None
    return sp.Rational(signe * rp, rq)


def racine_terme(ctx, t, n):
    """(s, R) tels que t = s·R^n (s = ±1, R un Terme), ou None."""
    c, s = t.coef, 1
    if n % 2 == 0 and c < 0:
        s, c = -1, -c
    rc = _racine_rationnelle_n(ctx.sp, c, n)
    if rc is None:
        return None
    bases = []
    for b, e in t.bases:
        if e % n:
            return None
        bases.append([b, e // n])
    return s, Terme(rc, bases)


def _neg_terme(t):
    return Terme(-t.coef, t.bases)


def _abs_terme(t):
    return Terme(abs(t.coef), t.bases)


def reconnaitre_identite(ctx, termes):
    sp = ctx.sp
    n = len(termes)
    if n == 2:
        r1, r2 = racine_terme(ctx, termes[0], 2), racine_terme(ctx, termes[1], 2)
        if r1 and r2 and r1[0] != r2[0]:
            A, B = (r1[1], r2[1]) if r1[0] > 0 else (r2[1], r1[1])
            return {"genre": "diff_carres", "A": A, "B": B}
        c1, c2 = racine_terme(ctx, termes[0], 3), racine_terme(ctx, termes[1], 3)
        if c1 and c2:
            A, B = c1[1], c2[1]
            if A.coef < 0 < B.coef:
                A, B = B, A
            s = 1
            if A.coef < 0 and B.coef < 0:
                s, A, B = -1, _neg_terme(A), _neg_terme(B)
            return {"genre": "cubes", "s": s, "A": A, "B": _abs_terme(B), "signe": 1 if B.coef > 0 else -1}
        return None
    if n == 3:
        for i, j, k in ((0, 1, 2), (0, 2, 1), (1, 2, 0)):
            ri, rj = racine_terme(ctx, termes[i], 2), racine_terme(ctx, termes[j], 2)
            if not (ri and rj and ri[0] == rj[0]):
                continue
            s, A, B = ri[0], ri[1], rj[1]
            deux_ab = sp.expand(2 * A.valeur() * B.valeur())
            milieu = sp.expand(termes[k].valeur())
            if sp.expand(milieu - s * deux_ab) == 0:
                return {"genre": "carre", "s": s, "A": A, "B": B, "signe": 1}
            if sp.expand(milieu + s * deux_ab) == 0:
                return {"genre": "carre", "s": s, "A": A, "B": B, "signe": -1}
        return None
    if n == 4:
        cubes = [racine_terme(ctx, t, 3) for t in termes]
        paires = [(i, j) for i in range(4) for j in range(4) if i != j and cubes[i] and cubes[j]]
        paires.sort(key=lambda ij: (bool(cubes[ij[0]][1].coef < 0), ij))   # A de préférence positif
        for i, j in paires:
            A, B = cubes[i][1], cubes[j][1]
            av, bv = A.valeur(), B.valeur()
            x1, x2 = sp.expand(3 * av ** 2 * bv), sp.expand(3 * av * bv ** 2)
            autres = [sp.expand(termes[k].valeur()) for k in range(4) if k not in (i, j)]
            if ((_egal(sp, autres[0], x1) and _egal(sp, autres[1], x2))
                    or (_egal(sp, autres[0], x2) and _egal(sp, autres[1], x1))):
                return {"genre": "cube_binome", "A": A, "B": B}
        return None
    return None


def _binome(ctx, A, B, signe):
    """(A + signe·B) : expression et écriture, dans l'ordre « A puis B » quand
    c'est possible : 1 − (x−y) s'écrit 1 − x + y, pas −x + y + 1."""
    sp = ctx.sp
    av, bv = sp.expand(A.valeur()), sp.expand(signe * B.valeur())
    e = sp.expand(av + bv)
    if A.monome() and B.monome():
        return e, tex_terme(ctx, A) + (" + " if signe > 0 else " - ") + tex_terme(ctx, B)
    ta, tb = termes_monomes(ctx, av), termes_monomes(ctx, bv)
    cles = lambda ts: {tuple(sorted((str(b), k) for b, k in t.bases)) for t in ts}
    if cles(ta) & cles(tb):   # termes semblables à regrouper : écriture ordonnée
        return e, ctx.tex_poly(e)
    return e, tex_somme(ctx, ta + tb)


def appliquer_identite(m, ctx, T, prof):
    sp = ctx.sp
    A, B = m["A"], m["B"]
    At, Bt = tex_racine(ctx, A), tex_racine(ctx, B)
    genre = m["genre"]

    if genre == "diff_carres":
        e1, t1 = _binome(ctx, A, B, -1)
        e2, t2 = _binome(ctx, A, B, 1)
        if any(len(sp.Add.make_args(sp.expand(x.valeur()))) > 1 for x in (A, B)):
            # A ou B est une somme : on écrit [A − B]·[A + B] tel quel, puis on réduit ; (x+1)² − (x−1)² = 2 · 2x = 4x
            def par(x, tex):
                return rf"\left({tex}\right)" if len(sp.Add.make_args(sp.expand(x.valeur()))) > 1 else tex
            pA, pB = par(A, At), par(B, Bt)
            def facteur(e, tex):
                return tex if len(sp.Add.make_args(e)) == 1 else rf"\left({tex}\right)"
            suite = rf" = {facteur(e1, t1)} \cdot {facteur(e2, t2)}"
            if all(len(termes_monomes(ctx, e)) == 1 for e in (e1, e2) if not e.is_number):
                suite += rf" = {ctx.tex_poly(sp.expand(e1 * e2))}"      # plus rien à factoriser : on conclut
            ctx.dire(rf"On reconnaît une différence de deux carrés (produit remarquable "
                     rf"\(A^2-B^2=(A-B)(A+B)\)) avec \(A={At}\) et \(B={Bt}\) : "
                     rf"\({T} = \left[{pA} - {pB}\right] \cdot \left[{pA} + {pB}\right]{suite}\).")
        else:
            ctx.dire(rf"On reconnaît une différence de deux carrés (produit remarquable "
                     rf"\(A^2-B^2=(A-B)(A+B)\)) avec \(A={At}\) et \(B={Bt}\) : "
                     rf"\({T} = \left({t1}\right)\left({t2}\right)\).")
        ctx.methode("Différence de carrés")
        c1, f1 = fact(e1, ctx, tex_hint=t1, prof=prof + 1, ident=True)
        c2, f2 = fact(e2, ctx, tex_hint=t2, prof=prof + 1, ident=True)
        return combiner(ctx, c1 * c2, f1 + f2)

    if genre == "carre":
        s, sg = m["s"], ("+" if m["signe"] > 0 else "-")
        e, tx = _binome(ctx, A, B, m["signe"])
        if s > 0:
            quoi, formule = "un carré parfait", rf"A^2{sg}2AB+B^2=(A{sg}B)^2"
        else:
            quoi, formule = "l'opposé d'un carré parfait", rf"-\left(A^2{sg}2AB+B^2\right)=-(A{sg}B)^2"
        ctx.dire(rf"On reconnaît {quoi} (produit remarquable \({formule}\)) avec \(A={At}\) et "
                 rf"\(B={Bt}\) : \({T} = {'-' if s < 0 else ''}\left({tx}\right)^{{2}}\).")
        ctx.methode("Carré parfait")
        c, f = fact(e, ctx, tex_hint=tx, prof=prof + 1, ident=True)
        c, f = _puissance_resultat(ctx, c, f, 2)
        return combiner(ctx, s * c, f)

    if genre == "cubes":
        s, sig = m["s"], m["signe"]
        av, bv = A.valeur(), B.valeur()
        e1, t1 = _binome(ctx, A, B, sig)
        e2 = sp.expand(av ** 2 - sig * av * bv + bv ** 2)
        t2 = ctx.tex_poly(e2)
        if sig > 0:
            quoi, formule = "une somme de deux cubes", r"A^3+B^3=(A+B)\left(A^2-AB+B^2\right)"
        else:
            quoi, formule = "une différence de deux cubes", r"A^3-B^3=(A-B)\left(A^2+AB+B^2\right)"
        if s < 0:
            quoi = "l'opposé d'" + quoi
        ctx.dire(rf"On reconnaît {quoi} (produit remarquable \({formule}\)) avec \(A={At}\) et "
                 rf"\(B={Bt}\) : \({T} = {'-' if s < 0 else ''}\left({t1}\right)\left({t2}\right)\).")
        ctx.methode("Somme de cubes" if sig > 0 else "Différence de cubes")
        c1, f1 = fact(e1, ctx, tex_hint=t1, prof=prof + 1, ident=True)
        c2, f2 = fact(e2, ctx, tex_hint=t2, prof=prof + 1, ident=True)
        return combiner(ctx, s * c1 * c2, f1 + f2)

    # cube d'un binôme
    sig = 1 if B.coef > 0 else -1
    Bp = _abs_terme(B)
    Bt = tex_racine(ctx, Bp)
    e, tx = _binome(ctx, A, Bp, sig)
    if sig > 0:
        formule = r"A^3+3A^2B+3AB^2+B^3=(A+B)^3"
    else:
        formule = r"A^3-3A^2B+3AB^2-B^3=(A-B)^3"
    ctx.dire(rf"On reconnaît le cube d'un binôme (produit remarquable \({formule}\)) avec "
             rf"\(A={At}\) et \(B={Bt}\) : \({T} = \left({tx}\right)^{{3}}\).")
    ctx.methode("Cube d'un binôme")
    c, f = fact(e, ctx, tex_hint=tx, prof=prof + 1, ident=True)
    c, f = _puissance_resultat(ctx, c, f, 3)
    return combiner(ctx, c, f)


def identites(P, ctx, ecrits, monos, T, prof):
    listes = [ecrits] if ecrits is not monos else []
    listes.append(monos)
    for termes in listes:
        m = reconnaitre_identite(ctx, termes)
        if m:
            return appliquer_identite(m, ctx, T, prof)
    return None


# ---------- 4.3 une seule lettre ----------
def _coeffs(ctx, P, t):
    """Coefficients (Fractions) par puissance croissante."""
    return [_ratio(c) for c in reversed(ctx.sp.Poly(P, t).all_coeffs())]


def fact_une_variable(P, t, ctx, ecrits, monos, T, prof):
    sp = ctx.sp
    n = sp.degree(P, t)
    if n == 1:
        return sp.Integer(1), [Facteur(P, T, 1)]
    r = identites(P, ctx, ecrits, monos, T, prof)
    if r:
        return r
    coeffs = _coeffs(ctx, P, t)
    if coeffs[-1] < 0:
        Q = sp.expand(-P)
        Q_tex = ctx.tex_poly(Q)
        ctx.dire(rf"On met \(-1\) en évidence : \({T} = -\left({Q_tex}\right)\).")
        ctx.methode("Mise en évidence")
        c, f = fact(Q, ctx, tex_hint=Q_tex, prof=prof + 1)
        return -c, f
    if ctx.contenu(P).q != 1:
        # coefficients fractionnaires : inutile de les rendre entiers si le
        # facteur ne se factorise de toute façon pas
        if n == 2:
            c0, b, a = coeffs
            D = b * b - 4 * a * c0
            carre = D >= 0 and _iroot(D.numerator, 2) is not None and _iroot(D.denominator, 2) is not None
            if D < 0 or (not carre and not ctx.reel):
                return trinome_methodes(P, t, coeffs, ctx, T)
        elif ctx.irreductible(P):
            return sans_methode_irreductible(P, ctx, T, prof, t, coeffs)
        return contenu_fractionnaire(P, ctx, T, prof)
    if n == 2:
        return trinome_methodes(P, t, coeffs, ctx, T)
    if ctx.irreductible(P):
        return sans_methode_irreductible(P, ctx, T, prof, t, coeffs)
    for essai in (changement_variable, groupements_essai, racine_evidente, completer_carre):
        r = essai(P, t, ctx, ecrits, monos, T, prof)
        if r:
            return r
    return repli(P, ctx, T, prof, t, coeffs)


def contenu_fractionnaire(P, ctx, T, prof):
    """Met en évidence le facteur numérique fractionnaire pour travailler avec des
    coefficients entiers (Somme-Produit, zéro évident, groupements…)."""
    sp = ctx.sp
    c = ctx.contenu(P)
    Q = sp.expand(P / c)
    Q_tex = ctx.tex_poly(Q)
    ctx.dire(rf"On met \({qtx(c)}\) en évidence pour travailler avec des coefficients entiers : "
             rf"\({T} = {qtx(c)}\left({Q_tex}\right)\).")
    ctx.methode("Mise en évidence")
    c2, f2 = fact(Q, ctx, tex_hint=Q_tex, prof=prof + 1)
    return combiner(ctx, c * c2, f2)


def diviseurs_entiers(n):
    n = abs(int(n))
    if n == 0 or n > BORNE:
        return []
    ds = []
    for d in range(1, int(math.isqrt(n)) + 1):
        if n % d == 0:
            ds.append(d)
            if d != n // d:
                ds.append(n // d)
    return ds


def somme_produit(b, c0):
    """u + w = b, u·w = c0, u et w entiers. Renvoie (u, w) ou None."""
    if c0 == 0 or abs(c0) > BORNE:
        return None
    for d in diviseurs_entiers(c0):
        for u in (d, -d):
            w = c0 // u
            if u * w == c0 and u + w == b:
                return (u, w)
    return None


def _num_vers_sympy(sp, r):
    if r.q is not None:
        return sp.Rational(r.q.numerator, r.q.denominator)
    a, b, m = r.data
    return sp.Rational(a.numerator, a.denominator) + sp.Rational(b.numerator, b.denominator) * sp.sqrt(m)


def _tex_quad(A, B, m, d):
    """Écriture de (A + B√m)/d, avec A, B entiers."""
    rac = ("" if abs(B) == 1 else str(abs(B))) + r"\sqrt{" + str(m) + "}"
    if A == 0:
        num = ("-" if B < 0 else "") + rac
    else:
        num = str(A) + (" - " if B < 0 else " + ") + rac
    return num if d == 1 else r"\frac{" + num + "}{" + str(d) + "}"


def tex_facteur_racine(r, v):
    """Écriture du facteur (v − r), r = Num.rat(q) ou Num.quad(a, b, m)."""
    if r.q is not None:
        q = r.q
        return v if q == 0 else v + (" - " + qtex(q) if q > 0 else " + " + qtex(-q))
    a, b, m = r.data
    d = a.denominator * b.denominator // math.gcd(a.denominator, b.denominator)
    A, B = int(a * d), int(b * d)
    if d == 1:
        s = v
        if A:
            s += " - " + str(A) if A > 0 else " + " + str(-A)
        rac = ("" if abs(B) == 1 else str(abs(B))) + r"\sqrt{" + str(m) + "}"
        return s + (" - " + rac if B > 0 else " + " + rac)
    if A < 0 or (A == 0 and B < 0):
        return v + " + " + _tex_quad(-A, -B, m, d)
    return v + " - " + _tex_quad(A, B, m, d)


def trinome_methodes(P, t, coeffs, ctx, T):
    """Trinôme ax²+bx+c (a > 0, coefficients entiers premiers entre eux), une fois
    les identités remarquables écartées."""
    sp = ctx.sp
    c0, b, a = coeffs
    v = str(t)
    entiers = all(c.denominator == 1 for c in coeffs)

    if entiers and a == 1:
        r = somme_produit(int(b), int(c0))
        if r:
            u, w = r
            nu, nv = ctx.paire_libre()
            e1, e2 = sp.expand(t + u), sp.expand(t + w)
            f1, f2 = Facteur(e1, ctx.tex_poly(e1)), Facteur(e2, ctx.tex_poly(e2))
            prod = str(u) + r"\times" + (f"({w})" if w < 0 else str(w))
            ctx.dire(rf"Trinôme unitaire \({T}\) (\(a=1\)) : on cherche deux nombres \({nu}\) et "
                     rf"\({nv}\) tels que \({nu}+{nv}={qtex(b)}\) et \({nu} \cdot {nv}={qtex(c0)}\).")
            ctx.dire(rf"On trouve \({nu}={u}\) et \({nv}={w}\), car "
                     rf"\({u}{'+' if w >= 0 else ''}{w}={qtex(b)}\) et \({prod}={qtex(c0)}\).")
            ctx.dire(rf"Méthode Somme-Produit : \({T} = \left({f1.tex}\right)\left({f2.tex}\right)\).")
            ctx.methode("Somme-Produit")
            return combiner(ctx, sp.Integer(1), [f1, f2])
    # a ≠ 1 : pas de zéro « évident » (les zéros p/q ne se testent pas à la main) : on passe à la formule du discriminant

    # la formule (discriminant)
    c_const, facteurs, lignes = trinome([c0, b, a], v, [], entier=True)
    D = b * b - 4 * a * c0
    if D < 0:
        for l in lignes:
            ctx.dire(l)
        ctx.methode("Non factorisable dans ℝ (Δ < 0)")
        return sp.Integer(1), [Facteur(P, T, 1)]
    if len(facteurs) == 1 and len(facteurs[0]["racines"]) == 2:
        # zéros irrationnels
        if not ctx.reel:
            ctx.dire(lignes[0])
            ctx.dire(rf"\(\Delta = {qtex(D)}\) n'est pas un carré parfait : les zéros de ce facteur sont "
                     rf"irrationnels, on le garde tel quel.")
            ctx.marquer()
            return sp.Integer(1), [Facteur(P, T, 1)]
        for l in lignes:
            ctx.dire(l)
        x1, x2 = facteurs[0]["racines"]
        f1 = Facteur(sp.expand(t - _num_vers_sympy(sp, x1)), tex_facteur_racine(x1, v))
        f2 = Facteur(sp.expand(t - _num_vers_sympy(sp, x2)), tex_facteur_racine(x2, v))
        const = sp.Rational(a.numerator, a.denominator)
        res = tex_produit(ctx, const, [f1, f2])
        ctx.dire(rf"D'où \({T} = {res}\) (on écrit \(a\left({v}-{v}_1\right)\left({v}-{v}_2\right)\)).")
        ctx.methode("Formule (discriminant)")
        return const, [f1, f2]
    # zéros rationnels (coefficients trop grands pour les méthodes précédentes) ou zéro double
    for l in lignes:
        ctx.dire(l)
    ctx.methode("Formule (discriminant)")
    out = []
    for f in facteurs:
        e = sp.expand(sum(sp.Rational(c.numerator, c.denominator) * t ** k for k, c in enumerate(f["poly"])))
        out.append(Facteur(e, ctx.tex_poly(e), f["mult"]))
    const = sp.Rational(c_const.numerator, c_const.denominator)
    sans = _forme_sans_fraction(ctx, t, T, v, const, out, [-F(f["poly"][0]) for f in facteurs]) if entiers and len(facteurs) == 2 else None
    if sans:
        return combiner(ctx, *sans)
    return combiner(ctx, const, out)


def _forme_sans_fraction(ctx, t, T, v, const, fractions, racines):
    """Deux zéros rationnels distincts p₁/q₁ et p₂/q₂ : a(x − p₁/q₁)(x − p₂/q₂) = c·q₁(x − p₁/q₁)·q₂(x − p₂/q₂) = c(q₁x − p₁)(q₂x − p₂),
    avec a = c·q₁q₂ ; c vaut ±1 (lemme de Gauss : les coefficients sont premiers entre eux), donc 1 car a > 0. Écrit les deux lignes et
    renvoie (c, facteurs), ou None s'il n'y a aucune fraction à chasser (zéros entiers) ou si c n'est pas entier."""
    sp = ctx.sp
    r1, r2 = sorted(racines)
    q1, q2 = r1.denominator, r2.denominator
    c = F(int(const.p), int(const.q)) / (q1 * q2)
    if (q1 == 1 and q2 == 1) or c.denominator != 1 or any(f.mult != 1 for f in fractions):
        return None
    L = [sp.expand(q * t - r.numerator) for q, r in ((q1, r1), (q2, r2))]
    facts = [Facteur(e, ctx.tex_poly(e)) for e in L]
    c = sp.Integer(c.numerator)
    morceaux = [(rf"{q}" if q != 1 else "") + rf"\left({f.tex}\right)" for q, f in ((q1, fractions[0]), (q2, fractions[1]))]
    ctx.dire(rf"D'où \({T} = {tex_produit(ctx, const, fractions)}\) (on écrit \(a\left({v}-{v}_1\right)\left({v}-{v}_2\right)\)).")
    a_tex = qtex(F(int(const.p), int(const.q)))
    egal = tex_produit(ctx, const, fractions)
    ctx.dire(rf"Sans fraction : on met le dénominateur de chaque zéro dans sa parenthèse, \(q\left({v}-\frac{{p}}{{q}}\right) = q{v}-p\) ; "
             rf"le coefficient \({a_tex}\) vaut \({q1} \cdot {q2}\)" + ("" if c == 1 else rf" (et le facteur restant \({c}\))")
             + rf" : \({egal} = {'' if c == 1 else f'{c} \\cdot '}{morceaux[0]} \cdot {morceaux[1]} = {tex_produit(ctx, c, facts)}\).")
    return c, facts


def changement_variable(P, t, ctx, ecrits, monos, T, prof):
    """a·t^(2k) + b·t^k + c  ->  u = t^k (exercices du type x⁴ − 13x² + 36)."""
    sp = ctx.sp
    termes = sp.Poly(P, t).terms()
    if len(termes) != 3:
        return None
    exps = sorted((m[0] for m, _ in termes), reverse=True)
    if exps[2] != 0 or exps[1] < 2 or exps[0] != 2 * exps[1]:
        return None
    k = exps[1]
    coef = {m[0]: _ratio(c) for m, c in termes}
    a, b, c0 = coef[2 * k], coef[k], coef[0]
    D = b * b - 4 * a * c0
    if D < 0 or _iroot(D.numerator, 2) is None or _iroot(D.denominator, 2) is None:
        return None   # le trinôme en u n'a pas de zéro rationnel : pas de factorisation sur Q par ce chemin
    u = ctx.symbole_libre()
    Q = sp.expand(sp.Rational(a.numerator, a.denominator) * u ** 2
                  + sp.Rational(b.numerator, b.denominator) * u
                  + sp.Rational(c0.numerator, c0.denominator))
    Q_tex = ctx.tex_poly(Q)
    ctx.dire(rf"On pose \({u} = {t}^{{{k}}}\) (changement de variable) : \({T} = {Q_tex}\).")
    ctx.methode("Changement de variable")
    cq, fq = fact(Q, ctx, tex_hint=Q_tex, prof=prof + 1)
    retour = [(sp.expand(f.expr.subs(u, t ** k)), f.mult) for f in fq]
    facts_t = [Facteur(e, ctx.tex_poly(e), m) for e, m in retour]
    ctx.dire(rf"On revient à \({t}\) en remplaçant \({u}\) par \({t}^{{{k}}}\) : "
             rf"\({T} = {tex_produit(ctx, cq, facts_t)}\).")
    ctx.methode("Changement de variable")
    const, out = cq, []
    for f in facts_t:
        c, ff = fact(f.expr, ctx, tex_hint=f.tex, prof=prof + 1)
        c, ff = _puissance_resultat(ctx, c, ff, f.mult)
        const *= c
        out += ff
    return combiner(ctx, const, out)


def racine_entiere(coeffs):
    """Un zéro ENTIER de P (coefficients par puissance croissante) : on teste les diviseurs du terme constant, ± (la méthode du
    cours ; pas de zéros p/q). None s'il n'y en a pas, ou si le terme constant est trop grand."""
    den = 1
    for c in coeffs:
        den = den * c.denominator // math.gcd(den, c.denominator)
    entiers = [int(c * den) for c in coeffs]
    a0 = abs(entiers[0])
    if a0 == 0 or a0 > BORNE:
        return None
    for d in sorted(diviseurs_entiers(a0)):
        for r in (d, -d):
            v = 0
            for c in reversed(entiers):
                v = v * r + c
            if v == 0:
                return F(r)
    return None


def racine_evidente(P, t, ctx, ecrits, monos, T, prof):
    sp = ctx.sp
    coeffs = _coeffs(ctx, P, t)
    r = racine_entiere(coeffs)
    if r is None:
        return None
    p = r.numerator
    L = sp.expand(t - p)
    Q = sp.expand(sp.cancel(P / L))
    Lt, Qt = ctx.tex_poly(L), ctx.tex_poly(Q)
    ctx.dire(rf"\({t} = {p}\) est une racine évidente (le polynôme s'annule en \({t} = {p}\)), donc "
             rf"\({Lt}\) est un facteur ; en divisant : \({T} = \left({Lt}\right)\left({Qt}\right)\).")
    ctx.methode("Racine évidente")
    c2, f2 = fact(Q, ctx, tex_hint=Qt, prof=prof + 1)
    return combiner(ctx, c2, [Facteur(L, Lt)] + f2)


# ---------- 4.4 plusieurs lettres ----------
def fact_plusieurs_variables(P, ctx, ecrits, monos, T, prof):
    sp = ctx.sp
    r = identites(P, ctx, ecrits, monos, T, prof)
    if r:
        return r
    if ctx.irreductible(P):
        return sans_methode_irreductible(P, ctx, T, prof)
    if ctx.contenu(P).q != 1:
        return contenu_fractionnaire(P, ctx, T, prof)
    # les groupements (méthode du cours) avant le Somme-Produit « à plusieurs
    # lettres », qui n'est qu'un prolongement : a²−b²+ac+bc doit se traiter par
    # groupements, comme dans le polycopié.
    r = groupements_essai(P, None, ctx, ecrits, monos, T, prof)
    if r:
        return r
    r = somme_produit_lettres(P, ctx, T)
    if r:
        return r
    r = completer_carre(P, None, ctx, ecrits, monos, T, prof)
    if r:
        return r
    return repli(P, ctx, T, prof)


def somme_produit_lettres(P, ctx, T):
    """Trinôme unitaire en une lettre s, les autres lettres jouant le rôle de
    nombres : x² + 5xy + 6y² = (x + 2y)(x + 3y)."""
    sp = ctx.sp
    for s in _gens(P):
        if sp.degree(P, s) != 2 or sp.expand(sp.Poly(P, s).LC() - 1) != 0:
            continue
        c, lst = sp.factor_list(P)
        if c != 1 or sum(m for _, m in lst) != 2:
            continue
        lins = [sp.expand(f) for f, m in lst for _ in range(m)]
        if not all(sp.degree(f, s) == 1 and sp.expand(sp.Poly(f, s).LC() - 1) == 0 for f in lins):
            continue
        u, w = sp.expand(lins[0] - s), sp.expand(lins[1] - s)
        poly_s = sp.Poly(P, s)
        B = sp.expand(poly_s.coeff_monomial(s))
        C = sp.expand(poly_s.coeff_monomial(1))
        nu, nv = ctx.paire_libre()
        f1, f2 = Facteur(lins[0], ctx.tex_poly(lins[0])), Facteur(lins[1], ctx.tex_poly(lins[1]))
        ctx.dire(rf"Trinôme unitaire en \({s}\) (les autres lettres jouent le rôle de nombres) : on cherche "
                 rf"\({nu}\) et \({nv}\) tels que \({nu}+{nv}={ctx.tex_poly(B)}\) et "
                 rf"\({nu} \cdot {nv}={ctx.tex_poly(C)}\).")
        ctx.dire(rf"On trouve \({nu}={ctx.tex_poly(u)}\) et \({nv}={ctx.tex_poly(w)}\). Méthode Somme-Produit : "
                 rf"\({T} = \left({f1.tex}\right)\left({f2.tex}\right)\).")
        ctx.methode("Somme-Produit")
        return combiner(ctx, sp.Integer(1), [f1, f2])
    return None


# ---------- 4.5 groupements ----------
def _partitions(n, kmax):
    res = []

    def rec(i, blocs):
        if i == n:
            if 2 <= len(blocs) <= kmax:
                res.append([list(b) for b in blocs])
            return
        for b in blocs:
            b.append(i)
            rec(i + 1, blocs)
            b.pop()
        if len(blocs) < kmax:
            blocs.append([i])
            rec(i + 1, blocs)
            blocs.pop()

    rec(0, [])

    def score(p):
        non_contigus = sum(1 for b in p if b != list(range(b[0], b[0] + len(b))))
        return (non_contigus, len(p), max(len(b) for b in p) - min(len(b) for b in p))

    res.sort(key=score)
    return res


def _terme_identite(ctx, m):
    """Le produit donné par une identité, sous forme de Terme structuré."""
    sp = ctx.sp
    A, B, genre = m["A"], m["B"], m["genre"]
    av, bv = A.valeur(), B.valeur()
    if genre == "diff_carres":
        return produit_termes(ctx, terme_depuis_expr(ctx, av - bv), terme_depuis_expr(ctx, av + bv))
    if genre == "carre":
        t = puissance_terme(terme_depuis_expr(ctx, av + m["signe"] * bv), 2)
        t.coef = t.coef * m["s"]
        return t
    if genre == "cubes":
        sig = m["signe"]
        t = produit_termes(ctx, terme_depuis_expr(ctx, av + sig * bv),
                           terme_depuis_expr(ctx, av ** 2 - sig * av * bv + bv ** 2))
        t.coef = t.coef * m["s"]
        return t
    return puissance_terme(terme_depuis_expr(ctx, av + bv), 3)


def _terme_groupe(ctx, groupe):
    """Factorisation « locale » d'un groupe de termes : (brute, avec identité)."""
    sp = ctx.sp
    if len(groupe) == 1:
        return groupe[0], None
    vals = [t.valeur() for t in groupe]
    V = sp.expand(sum(vals))
    if V == 0:
        return None, None
    g = ctx.pgcd(vals)
    if ctx.coef_tete(sp.expand(sp.cancel(vals[0] / g))) < 0:
        g = -g
    R = sp.expand(sp.cancel(V / g))
    cg, bg = ctx.decomposer(g)
    tg = Terme(cg, bg)
    brute = produit_termes(ctx, tg, terme_depuis_expr(ctx, R))
    avec = None
    monos = termes_monomes(ctx, R)
    if len(monos) >= 2:
        m = reconnaitre_identite(ctx, monos)
        if m:
            avec = produit_termes(ctx, tg, _terme_identite(ctx, m))
    return brute, avec


def _contient(ctx, terme, g):
    sp = ctx.sp
    _, bg = ctx.decomposer(g)
    for b, e in bg:
        if not any(it[1] >= e and _egal(sp, it[0], b) for it in terme.bases):
            return False
    return True


def groupements_essai(P, t, ctx, ecrits, monos, T, prof):
    sp = ctx.sp
    listes = []
    if ecrits is not monos and len(ecrits) >= 4:
        listes.append(ecrits)
    if len(monos) >= 4:
        listes.append(monos)
    for termes in listes:
        n = len(termes)
        if n > 8:
            continue
        meilleur = None
        for k, part in enumerate(_partitions(n, 3 if n <= 6 else 2)):
            if k >= MAX_PARTITIONS:
                break
            groupes = [[termes[i] for i in bloc] for bloc in part]
            infos = [_terme_groupe(ctx, g) for g in groupes]
            if any(b is None for b, _ in infos):
                continue
            g = ctx.pgcd([b.valeur() for b, _ in infos])
            if g != 1:
                choix, tous = [], True
                for brute, avec in infos:
                    if _contient(ctx, brute, g):
                        choix.append(brute)
                    elif avec is not None and _contient(ctx, avec, g):
                        choix.append(avec)
                    else:
                        choix.append(brute)
                        tous = False
                if tous:
                    meilleur = (groupes, choix)
                    break
                if meilleur is None:
                    meilleur = (groupes, choix)
                continue
            formes = [avec or brute for brute, avec in infos]
            if reconnaitre_identite(ctx, formes):
                meilleur = (groupes, formes)
                break
        if meilleur is None:
            continue
        groupes, nouveaux = meilleur
        morceaux = []
        for i, g in enumerate(groupes):
            if len(g) == 1:
                s = tex_terme(ctx, g[0], signe=False)
                neg = g[0].coef < 0
            else:
                s, neg = r"\left(" + tex_somme(ctx, g) + r"\right)", False
            morceaux.append((("-" if neg else "") if i == 0 else (" - " if neg else " + ")) + s)
        avant = "".join(morceaux)
        apres = tex_somme(ctx, nouveaux)
        egalite = avant if avant == apres else avant + " = " + apres
        ctx.dire(rf"On groupe les termes : \({T} = {egalite}\).")
        ctx.methode("Groupements")
        return fact(P, ctx, ecrits=nouveaux, tex_hint=apres, prof=prof + 1)
    return None


# ---------- 4.6 compléter le carré ----------
def completer_carre(P, t, ctx, ecrits, monos, T, prof):
    """A² + C² (+ terme du milieu) = (A ± C)² − D² quand il manque juste un carré :
    z⁴ − 3z² + 9 = (z² + 3)² − (3z)², x⁴ + 4 = (x² + 2)² − (2x)² (« Notions élémentaires d'algèbre » §2.2.4)."""
    sp = ctx.sp
    if len(monos) not in (2, 3):
        return None
    for i in range(len(monos)):
        for j in range(i + 1, len(monos)):
            ri, rj = racine_terme(ctx, monos[i], 2), racine_terme(ctx, monos[j], 2)
            if not (ri and rj and ri[0] > 0 and rj[0] > 0):
                continue
            A, C = ri[1], rj[1]
            av, cv = A.valeur(), C.valeur()
            milieu = sp.expand(P - av ** 2 - cv ** 2)
            for sg in (1, -1):
                D2 = sp.expand(sg * 2 * av * cv - milieu)   # P = (A + sg·C)² − D²
                if D2 == 0:
                    continue
                tD = termes_monomes(ctx, D2)
                rD = racine_terme(ctx, tD[0], 2) if len(tD) == 1 else None
                if not rD or rD[0] < 0:
                    continue
                D = rD[1]
                S, S_tex = _binome(ctx, A, C, sg)
                D_tex = tex_terme(ctx, D)
                D_carre = (D_tex if (len(D.bases) == 1 and D.coef == 1 and D.bases[0][1] == 1)
                           else r"\left(" + D_tex + r"\right)")
                ecriture = rf"\left({S_tex}\right)^{{2}} - {D_carre}^{{2}}"
                ctx.dire(rf"On complète le carré (on ajoute et on retire \({ctx.tex_poly(D2)}\)) : "
                         rf"\({T} = {ecriture}\).")
                ctx.methode("Compléter le carré")
                m = {"genre": "diff_carres", "A": terme_depuis_expr(ctx, S), "B": D}
                return appliquer_identite(m, ctx, ecriture, prof)
    return None


# ---------- 4.7 aucune méthode du cours : on le dit, on ne l'affirme jamais sans le justifier ----------
AUCUNE_METHODE = "Aucune méthode du cours"
MAX_DIVISEURS_MONTRES = 6


def _valeurs_testees(coeffs):
    """(diviseurs, [(r, P(r))]) : les diviseurs entiers du terme constant (après dénominateur commun) et les valeurs de P en d puis −d ;
    None si le terme constant est trop grand pour les tester."""
    den = 1
    for c in coeffs:
        den = den * c.denominator // math.gcd(den, c.denominator)
    a0 = abs(int(coeffs[0] * den))
    if a0 == 0 or a0 > BORNE:
        return None
    divs = sorted(diviseurs_entiers(a0))
    valeurs = []
    for d in divs:
        for r in (d, -d):
            v = F(0)
            for c in reversed(coeffs):
                v = v * r + c
            valeurs.append((r, v))
    return divs, valeurs


def _pourquoi_aucune(ctx, T, t=None, coeffs=None):
    """Pourquoi aucune méthode du cours ne conclut. Une seule lettre (degré ≥ 3) : les valeurs de P aux diviseurs entiers du terme
    constant ; sinon, la liste des méthodes essayées."""
    if t is None:
        return (rf"Aucune méthode du cours ne s'applique à \({T}\) (pas de facteur commun, pas d'identité remarquable, pas de groupement) : "
                rf"on ne peut pas conclure avec ces méthodes.")
    essai = _valeurs_testees(coeffs)
    if essai is None:
        return (rf"Le terme constant de \(P({t}) = {T}\) est trop grand pour tester ses diviseurs à la main : "
                rf"la recherche d'une racine entière ne permet pas de conclure.")
    divs, valeurs = essai
    montres = valeurs[:2 * MAX_DIVISEURS_MONTRES]
    suite = ", …" if len(divs) > MAX_DIVISEURS_MONTRES else ""
    ensemble = ", ".join(rf"\pm{d}" for d in divs[:MAX_DIVISEURS_MONTRES]) + suite
    vals = ", ".join(rf"\(P({r}) = {qtex(v)}\)" for r, v in montres) + suite
    reste = " (les autres diviseurs ne l'annulent pas non plus)" if suite else ""
    return (rf"On cherche une racine entière de \(P({t}) = {T}\) parmi les diviseurs du terme constant (\({ensemble}\)) : {vals}. "
            rf"Aucun diviseur entier du terme constant n'annule \(P\){reste} : la recherche d'une racine entière ne permet pas de conclure.")


def _developpement(ctx, c, facts):
    """Chaîne d'égalités qui redéveloppe c·Π facteurs, un facteur après l'autre : (2x − 1)(3x − 1)(5x + 1) = (6x² − 5x + 1)(5x + 1) = 30x³ − 19x² + 1."""
    sp = ctx.sp

    def par(f):
        return (f.tex if f.est_lettre else rf"\left({f.tex}\right)") + (f"^{{{f.mult}}}" if f.mult > 1 else "")
    chaine = [tex_produit(ctx, c, facts)]
    acc = sp.Rational(c)
    for k, f in enumerate(facts):
        acc = sp.expand(acc * f.expr ** f.mult)
        if k == len(facts) - 1:
            chaine.append(ctx.tex_poly(acc))
        elif k > 0 or c != 1 or f.mult > 1:
            chaine.append(rf"\left({ctx.tex_poly(acc)}\right)" + "".join(par(g) for g in facts[k + 1:]))
    return " = ".join(chaine)


def _fin_sans_methode(ctx, prof):
    """Toute l'expression (prof = 0) : la méthode annoncée est « Aucune méthode du cours » ; un facteur : l'étape suit la carte précédente."""
    if prof == 0:
        ctx.methode(AUCUNE_METHODE)
    else:
        ctx.marquer()


def sans_methode_irreductible(P, ctx, T, prof, t=None, coeffs=None):
    """P n'a pas de facteur à coefficients rationnels : on le garde tel quel, après avoir dit pourquoi les méthodes ne concluent pas."""
    ctx.dire(_pourquoi_aucune(ctx, T, t, coeffs))
    ctx.dire(rf"On peut montrer que \({T}\) n'a pas de facteur à coefficients rationnels : on le garde tel quel.")
    _fin_sans_methode(ctx, prof)
    return ctx.sp.Integer(1), [Facteur(P, T, 1)]


def repli(P, ctx, T, prof, t=None, coeffs=None):
    """Aucune méthode du cours ne conclut, mais P se factorise : on le dit, on écrit le résultat et on le vérifie en développant."""
    sp = ctx.sp
    c, lst = sp.factor_list(P)
    c = sp.Rational(c)
    facts = []
    for f, m in lst:
        f = sp.expand(f)
        if f.is_Symbol:
            facts.append(Facteur(f, str(f), m))
            continue
        cf, bf = ctx.normaliser(f)
        c *= cf ** m
        facts.append(Facteur(bf, ctx.tex_poly(bf), m))
    ctx.dire(_pourquoi_aucune(ctx, T, t, coeffs))
    ctx.dire(rf"\({T}\) se factorise quand même : \({T} = {tex_produit(ctx, c, facts)}\).")
    ctx.dire(rf"Vérification : en développant, on retrouve \({T}\) : \({_developpement(ctx, c, facts)}\).")
    _fin_sans_methode(ctx, prof)
    return combiner(ctx, c, facts)


# =====================================================================
# 5. POINT D'ENTRÉE
# =====================================================================
def _produit_ecrit(arbre, ctx, syms, prof=1):
    """L'expression est déjà un produit : on factorise chacun de ses facteurs."""
    sp = ctx.sp
    const, facts = sp.Integer(1), []

    def visiter(n, expo):
        nonlocal const
        n = _sans_parentheses(n)
        k = n[0]
        if k == "num":
            const *= sp.Rational(n[1].numerator, n[1].denominator) ** expo
        elif k == "var":
            facts.append(Facteur(syms[n[1]], n[1], expo))
        elif k == "neg":
            const *= (-1) ** expo
            visiter(n[1], expo)
        elif k == "mul":
            for c in n[1]:
                visiter(c, expo)
        elif k == "div":
            d = _valeur_constante(n[2])
            if d is None:
                raise ErreurSaisie("La division n'est permise que par un nombre "
                                   "(sinon ce n'est pas un polynôme).")
            const /= sp.Rational(d.numerator, d.denominator) ** expo
            visiter(n[1], expo)
        elif k == "pow":
            visiter(n[1], expo * n[2])
        else:   # une somme entre parenthèses
            P = sp.expand(vers_sympy(ctx, syms, n))
            c, ff = fact(P, ctx, ecrits=termes_ecrits(ctx, syms, n), tex_hint=tex_arbre(n), prof=prof)
            c, ff = _puissance_resultat(ctx, c, ff, expo)
            const *= c
            facts.extend(ff)

    avant = len(ctx.etapes)
    visiter(arbre, 1)
    if len(ctx.etapes) > avant:
        ctx.inserer(avant, "L'expression est déjà un produit : on factorise chacun de ses facteurs.")
    return combiner(ctx, const, facts)


def _message_final(ctx, P, T, produit):
    sp = ctx.sp
    if P.is_number:
        return "C'est un nombre : il n'y a rien à factoriser."
    if len(termes_monomes(ctx, P)) == 1:
        return rf"\({T}\) est un monôme (déjà un produit) : il n'y a rien à factoriser."
    if produit:
        return rf"\({T}\) est déjà complètement factorisé."
    if sp.Poly(P, *_gens(P)).total_degree() == 1:
        return rf"\({T}\) est de degré 1 : il n'y a rien à factoriser."
    return rf"Aucune méthode du cours ne s'applique à \({T}\) : on ne peut pas conclure avec ces méthodes."


def _factoriser(entree):
    """(résultat, ctx) : ctx.groupes donne la méthode de chaque étape (T21) ; ctx est None en cas d'erreur."""
    sp = charger_sympy()
    if sp is None:
        return {"ok": False, "erreur": "Le moteur de calcul est encore en cours de chargement, "
                "réessaie dans un instant."}, None
    try:
        arbre = analyser(entree)
        lettres = sorted(lettres_arbre(arbre))
        ctx = Ctx(sp, lettres)
        syms = {l: sp.Symbol(l) for l in lettres}
        P = sp.expand(vers_sympy(ctx, syms, arbre))
        T = tex_arbre(arbre)
        if P == 0:
            return {"ok": False, "erreur": "L'expression vaut 0 : il n'y a rien à factoriser."}, None
        gens = _gens(P)
        ctx.reel = len(gens) == 1 and sp.degree(P, gens[0]) == 2
        a = _sans_parentheses(arbre)
        produit = a[0] != "add"
        if produit:
            const, facts = _produit_ecrit(a, ctx, syms)
        else:
            const, facts = fact(P, ctx, ecrits=termes_ecrits(ctx, syms, a), tex_hint=T)

        # vérification : le résultat redéveloppé doit redonner exactement l'expression
        verif = const
        for f in facts:
            verif = verif * f.expr ** f.mult
        secours = sp.expand(verif - P) != 0
        if secours:
            ctx = Ctx(sp, lettres)
            const, facts = repli(P, ctx, T, 0)

        if not ctx.etapes:
            ctx.dire(_message_final(ctx, P, T, produit))
        if ctx.methodes:
            badge = " · ".join(ctx.methodes)
        elif P.is_number:
            badge = "Rien à factoriser"
        elif produit or len(termes_monomes(ctx, P)) == 1:
            badge = "Déjà factorisé"
        elif sp.Poly(P, *_gens(P)).total_degree() <= 1:
            badge = "Rien à factoriser"
        else:
            badge = AUCUNE_METHODE
        return {
            "ok": True,
            "expr_tex": T,
            "methode": badge,
            "etapes": ctx.etapes,
            "resultat_tex": tex_produit(ctx, const, facts),
            "secours": secours,   # True = une méthode a produit un résultat faux (bug à corriger)
        }, ctx
    except ErreurSaisie as e:
        return {"ok": False, "erreur": str(e)}, None
    except Exception as e:   # ne devrait pas arriver : on le dit plutôt que de planter
        return {"ok": False, "erreur": "Cette expression n'a pas pu être factorisée.",
                "detail": f"{type(e).__name__} : {e}"}, None


def factoriser_expr(entree):
    return _factoriser(entree)[0]


def factoriser_json(entree):
    return json_strict(factoriser_expr(entree))


def apercu_json(entree):
    try:
        return json_strict({"ok": True, "tex": tex_arbre(analyser(entree))})
    except ErreurSaisie as e:
        return json_strict({"ok": False, "erreur": str(e)})


# =====================================================================
# 6. EXERCICES ALÉATOIRES (générés, pas juste tirés d'une liste fixe)
# =====================================================================
def poly_ascii(coeffs):
    """coeffs : liste ascendante [c0, c1, c2, ...] d'entiers. Chaîne saisissable."""
    partes = []
    for k in range(len(coeffs) - 1, -1, -1):
        c = int(coeffs[k])
        if c == 0:
            continue
        mono = "" if k == 0 else ("x" if k == 1 else f"x^{k}")
        coef = str(abs(c)) if (not mono or abs(c) != 1) else ""
        signe = "+" if (c > 0 and partes) else ("-" if c < 0 else "")
        partes.append(signe + coef + mono)
    return "".join(partes) or "0"


def _pmul(p, q):
    r = [0] * (len(p) + len(q) - 1)
    for i, a in enumerate(p):
        for j, b in enumerate(q):
            r[i + j] += a * b
    return r


def _carre_parfait_entier(n):
    if n < 0:
        return False
    r = math.isqrt(n)
    return r * r == n


def _non_nul(a, b):
    return random.choice([v for v in range(a, b + 1) if v != 0])


def genere_exercice(niveau):
    if niveau == "facile":
        while True:
            r1, r2 = random.randint(-9, 9), random.randint(-9, 9)
            if r1 and r2 and r1 != r2:
                break
        return poly_ascii([r1 * r2, -(r1 + r2), 1])

    if niveau == "moyen":
        while True:
            p1, p2 = random.randint(1, 4), random.randint(1, 4)
            if p1 * p2 != 1:
                break
        q1, q2 = _non_nul(-7, 7), _non_nul(-7, 7)
        return poly_ascii([q1 * q2, p1 * q2 + p2 * q1, p1 * p2])

    if niveau == "difficile":
        choix = random.choice(["carre", "diff", "irrationnel"])
        if choix == "carre":
            p, q = random.randint(1, 4), _non_nul(-7, 7)
            return poly_ascii([q * q, 2 * p * q, p * p])
        if choix == "diff":
            sa, sc = random.randint(1, 4), random.randint(1, 8)
            return poly_ascii([-(sc * sc), 0, sa * sa])
        while True:
            a, b, c0 = random.randint(1, 3), random.randint(-8, 8), random.randint(-8, 8)
            D = b * b - 4 * a * c0
            if D > 0 and not _carre_parfait_entier(D):
                break
        return poly_ascii([c0, b, a])

    if niveau == "tresDifficile":
        if random.random() < 0.5:
            while True:
                a, b, c0 = random.choice([1, 1, 2, 3]), random.randint(-6, 6), random.randint(1, 9)
                if b * b - 4 * a * c0 < 0:
                    break
            return poly_ascii([c0, b, a])
        if random.random() < 0.6:
            r1, r2, r3 = _non_nul(-5, 5), _non_nul(-5, 5), _non_nul(-5, 5)
            prod = _pmul(_pmul([-r1, 1], [-r2, 1]), [-r3, 1])
        else:
            r = _non_nul(-4, 4)
            while True:
                b2, c2 = random.randint(-5, 5), random.randint(1, 6)
                if b2 * b2 - 4 * c2 < 0:
                    break
            prod = _pmul([-r, 1], [c2, b2, 1])
        coef = random.choice([1, 1, 2])
        return poly_ascii([coef * v for v in prod])

    return "x^2-1"


def exercice_json(niveau):
    return json_strict({"ok": True, "expr": genere_exercice(niveau)})


if __name__ == "__main__":
    import sys
    for arg in sys.argv[1:] or ["x^2+5x-14"]:
        r = factoriser_expr(arg)
        if not r["ok"]:
            print(arg, "->", "ERREUR :", r["erreur"])
            continue
        print(arg, "->", r["resultat_tex"], "   [", r["methode"], "]")
        for e in r["etapes"]:
            print("    ", e["html"])
