"""
second_degre.py — Brique commune : équations polynomiales du 2e degré (et ce qui s'y ramène), en Python pur, sans SymPy.

Chantier equations-2e-degre (docs/chantiers/equations-2e-degre/decisions.md, § 13 en tête). **P1 : le calcul seul, sans aucun texte**
(la rédaction, `resoudre_equation` et `appliquer` viennent en P2b, la saisie en P3). Tout est exact : polynômes à coefficients
`Fraction` (`Polynome`), nombres p + q√m (`Nombre`, sur `noyau.racine_q` : pas de nouvelle simplification de k√m/d, § 13.2).

    Polynome(coeffs)                  tuple de Fraction, ordre croissant (P[k] : coefficient de xᵏ), sans zéro de tête ; nul : (0,)
    vers_polynome(arbre, inconnue)    polynomes.pq, puis les bornes du § 13.5 (degré ≤ 8, numérateurs et dénominateurs ≤ 9 chiffres)
    Nombre(p, q=0, m=1)               p + q√m (m sans facteur carré), arithmétique et comparaison exactes, forme_reduite (E11),
                                      encadrement (isqrt)
    mise_en_evidence(P, constante)    pgcd, xʲ, −pgcd quand a < 0 (D21) ; rien si les coefficients ne sont pas entiers (§ 13.4)
    identite(P)                       A² − B², A² ± 2AB + B² sur un polynôme développé (E5, D8 ; A = k·xʲ, § 13.4)
    essais_sp(b, c)                   lignes du tableau S-P (E6), arrêt à ✓ ; plus de 12 lignes affichées : « trop » (§ 13.5, point 5)
    diviseurs_signes(c)               ±1, ±2, … (E7, D1), sans borne d'affichage
    racine_entiere_unique(P)          racine entière décidée par Δ (aucune borne silencieuse ; ni somme_produit ni racine_entiere de FA)
    racines_formule(P)                Δ, √Δ, x₁ (avec −√Δ), x₂, ou x quand Δ = 0
    s_applique(methode, P)            « la méthode aboutit » (§ 13.4) ; calculer(methode, P) : son calcul, ou None
    chemin(P, methodes)               l'ordre fixe du cours (D28), tentatives en échec comprises, produit nul, garde-fou
    produit_nul(facteurs)             D14, D24 ; un monôme k·xʲ donne x = 0 (D7, 3x² = 0 ⇔ x = 0)
    redevelopper, verifier_solution   le garde-fou exact, dans Q(√m) (principe 1)
    approx_garantie(x, decimales)     nombres.approx sur les deux bornes d'un encadrement, raffiné jusqu'à l'égalité (E14)

Les facteurs sont des tuples de `Nombre` (ordre croissant) : (5x + √3) est (Nombre(0, 1, 3), Nombre(5)). Les noms de méthodes sont
ceux du § 5 (« ME », « IDREM_DIFF », « IDREM_PLUS », « IDREM_MOINS », « SP », « TATONNEMENT », « FORMULE », « PRODUIT_NUL »,
« ISOLER »), plus « IDREM » (la famille, pour l'ordre du cours) et « ME_PUISSANCE » (la variante E12 : seulement xʲ).
"""
from fractions import Fraction as F
from functools import cmp_to_key
from math import gcd, isqrt

import polynomes
from expr import variables
from noyau import racine_q, squarefree
from nombres import approx

__all__ = ["Polynome", "Nombre", "HorsBornes", "vers_polynome", "mise_en_evidence", "identite", "essais_sp", "diviseurs_signes",
           "racine_entiere_unique", "racines_formule", "s_applique", "calculer", "chemin", "produit_nul", "redevelopper",
           "verifier_solution", "approx_garantie", "ORDRE_DU_COURS", "ORDRE_PAR_LA_FORMULE", "METHODES"]

ORDRE_DU_COURS = ("ME", "IDREM", "SP", "TATONNEMENT", "FORMULE")          # D28 : ordre fixe, même si a = 1
ORDRE_PAR_LA_FORMULE = ("ME_PUISSANCE", "FORMULE")                       # E12 : seulement xʲ en évidence, puis la formule
IDREM = ("IDREM_DIFF", "IDREM_PLUS", "IDREM_MOINS")
METHODES = ORDRE_DU_COURS + ("ME_PUISSANCE",) + IDREM

DEGRE_MAX = polynomes.DEGRE_MAX            # 8, comme EL-M (§ 13.5)
CHIFFRES_MAX = 9                           # numérateur et dénominateur de chaque coefficient (§ 13.5)
LIGNES_SP_MAX = 12                         # lignes affichées du tableau S-P (§ 13.5 ; point 5 : on compte les lignes affichées)
BORNE_RADICANDE = 10 ** 12                 # √q non rationnelle : numérateur × dénominateur de q au plus (noyau.squarefree, < 0,1 s)


class HorsBornes(Exception):
    """L'équation dépasse ce que l'outil sait traiter (§ 13.5) : degré > 8, coefficient de plus de 9 chiffres, radicande trop grand."""


def _fraction(x):
    if isinstance(x, (float, complex, bool)):
        raise TypeError(f"nombre exact attendu (int, Fraction, Decimal, str), pas {type(x).__name__}")
    return F(x)


# =====================================================================
# 1. POLYNÔMES À COEFFICIENTS RATIONNELS
# =====================================================================
class Polynome(tuple):
    """Polynôme à coefficients rationnels : tuple de Fraction, ordre croissant (P[k] : coefficient de xᵏ), sans zéro de tête ;
    le polynôme nul est (0,). Jamais de float."""
    __slots__ = ()

    def __new__(cls, coeffs=(0,)):
        c = [_fraction(x) for x in coeffs]
        while len(c) > 1 and c[-1] == 0:
            c.pop()
        return super().__new__(cls, c or [F(0)])

    @property
    def degre(self):
        return len(self) - 1

    def nul(self):
        return len(self) == 1 and self[0] == 0

    def entiers(self):
        return all(c.denominator == 1 for c in self)

    def monome(self):
        """Un seul terme non nul (k·xʲ, j ≥ 0)."""
        return sum(1 for c in self if c != 0) == 1

    def __repr__(self):
        return "Polynome((" + ", ".join(str(c) for c in self) + ("," if len(self) == 1 else "") + "))"


def vers_polynome(arbre, inconnue):
    """Le polynôme (Polynome) d'un arbre de moteur/expr.py en l'inconnue, par polynomes.pq, puis les bornes du § 13.5.

    ValueError si l'arbre contient une autre lettre (pq les prendrait toutes pour l'inconnue). HorsBornes si pq ne conclut pas
    (polynomes.Hors : la lecture de la saisie, P3, diagnostique avant la racine, le dénominateur et l'exposant ; il ne reste que le
    degré > 8, § 13.5 et point 6 du plan), ou si un coefficient a plus de 9 chiffres au numérateur ou au dénominateur."""
    autres = variables(arbre) - {inconnue}
    if autres:
        raise ValueError(f"autres lettres que l'inconnue {inconnue} : {sorted(autres)}")
    try:
        P = Polynome(polynomes.pq(arbre))
    except polynomes.Hors:
        raise HorsBornes("degré supérieur à 8 ou forme non polynomiale") from None
    if P.degre > DEGRE_MAX:
        raise HorsBornes("degré supérieur à 8")
    for c in P:
        if len(str(abs(c.numerator))) > CHIFFRES_MAX or len(str(c.denominator)) > CHIFFRES_MAX:
            raise HorsBornes("coefficient de plus de 9 chiffres")
    return P


# =====================================================================
# 2. NOMBRES p + q√m
# =====================================================================
class Nombre:
    """p + q√m, p et q rationnels, m entier sans facteur carré (m = 1 et q = 0 pour un rationnel). Écriture unique : deux Nombre
    égaux ont les mêmes (p, q, m). Arithmétique exacte dans Q(√m) ; deux radicandes différents ne se combinent pas (TypeError),
    mais se comparent (encadrements raffinés)."""
    __slots__ = ("p", "q", "m")

    def __init__(self, p=0, q=0, m=1):
        p, q = _fraction(p), _fraction(q)
        if isinstance(m, bool) or not isinstance(m, int) or m < 0:
            raise ValueError(f"radicande entier ≥ 0 attendu, pas {m!r}")
        if q != 0 and m > 1:
            if m > BORNE_RADICANDE:
                raise HorsBornes("radicande trop grand")
            k, m = squarefree(m)
            q *= k
        if q == 0 or m <= 1:
            p, q, m = p + (q if m == 1 else 0), F(0), 1
        self.p, self.q, self.m = p, q, m

    @classmethod
    def _brut(cls, p, q, m):
        """Sans normalisation (m déjà sans facteur carré)."""
        n = object.__new__(cls)
        if q == 0:
            p, m = p, 1
        n.p, n.q, n.m = p, q, m
        return n

    @classmethod
    def racine(cls, q):
        """√q, q rationnel ≥ 0 : rationnel si q est un carré (polynomes.racine_carree), sinon k·√m par noyau.racine_q."""
        q = _fraction(q)
        if q < 0:
            raise ValueError("racine d'un nombre négatif")
        r = polynomes.racine_carree(q)
        if r is not None:
            return cls(r)
        if q.numerator * q.denominator > BORNE_RADICANDE:
            raise HorsBornes("radicande trop grand")
        k, m = racine_q(q)
        return cls._brut(F(0), F(k), m) if m > 1 else cls(k)

    @property
    def rationnel(self):
        return self.q == 0

    def _champ(self, autre):
        autre = nombre(autre)
        if self.q != 0 and autre.q != 0 and self.m != autre.m:
            raise TypeError(f"√{self.m} et √{autre.m} : radicandes différents")
        return autre, (self.m if self.q != 0 else autre.m)

    def __add__(self, autre):
        autre, m = self._champ(autre)
        return Nombre._brut(self.p + autre.p, self.q + autre.q, m)

    __radd__ = __add__

    def __neg__(self):
        return Nombre._brut(-self.p, -self.q, self.m)

    def __sub__(self, autre):
        return self + (-nombre(autre))

    def __rsub__(self, autre):
        return nombre(autre) - self

    def __mul__(self, autre):
        autre, m = self._champ(autre)
        return Nombre._brut(self.p * autre.p + self.q * autre.q * m, self.p * autre.q + self.q * autre.p, m)

    __rmul__ = __mul__

    def inverse(self):
        norme = self.p * self.p - self.q * self.q * self.m          # (p + q√m)(p − q√m), jamais nul pour un Nombre non nul
        if norme == 0:
            raise ZeroDivisionError("division par 0")
        return Nombre._brut(self.p / norme, -self.q / norme, self.m)

    def __truediv__(self, autre):
        return self * nombre(autre).inverse()

    def __rtruediv__(self, autre):
        return nombre(autre) * self.inverse()

    def signe(self):
        """Signe exact (−1, 0, 1) de p + q√m."""
        sp, sq = (self.p > 0) - (self.p < 0), (self.q > 0) - (self.q < 0)
        if sq == 0 or sp == sq:
            return sp or sq
        if sp == 0:
            return sq
        d = self.p * self.p - self.q * self.q * self.m             # |p| comparé à |q|√m
        return sp if d > 0 else sq                                  # d ≠ 0 : √m irrationnel

    def encadrement(self, chiffres=20):
        """(bas, haut) rationnels avec bas ≤ p + q√m ≤ haut et haut − bas ≤ |q|·10^(−chiffres), par isqrt (aucun float)."""
        if self.q == 0:
            return self.p, self.p
        e = 10 ** chiffres
        s = isqrt(self.m * e * e)                                  # s/e ≤ √m < (s + 1)/e
        a, b = self.p + self.q * F(s, e), self.p + self.q * F(s + 1, e)
        return (a, b) if a <= b else (b, a)

    def forme_reduite(self):
        """(A, B, m, d) entiers : p + q√m = (A + B√m)/d, d ≥ 1, pgcd(A, B, d) = 1 (E11 : (−4 − 2√5)/2 = −2 − √5, (4 − √22)/3)."""
        d = self.p.denominator * self.q.denominator // gcd(self.p.denominator, self.q.denominator)
        A, B = int(self.p * d), int(self.q * d)
        g = gcd(gcd(A, B), d)
        return A // g, B // g, self.m, d // g

    def __eq__(self, autre):
        if isinstance(autre, (int, F)) and not isinstance(autre, bool):
            return self.q == 0 and self.p == autre
        if not isinstance(autre, Nombre):
            return NotImplemented
        return (self.p, self.q, self.m) == (autre.p, autre.q, autre.m)

    def __hash__(self):
        return hash(self.p) if self.q == 0 else hash((self.p, self.q, self.m))

    def __lt__(self, autre):
        return comparer(self, autre) < 0

    def __le__(self, autre):
        return comparer(self, autre) <= 0

    def __gt__(self, autre):
        return comparer(self, autre) > 0

    def __ge__(self, autre):
        return comparer(self, autre) >= 0

    def __repr__(self):
        if self.q == 0:
            return f"Nombre({self.p})"
        return f"Nombre({self.p}, {self.q}, {self.m})"


def nombre(x):
    """x en Nombre (int, Fraction, Decimal ou str exacts ; pas de float)."""
    return x if isinstance(x, Nombre) else Nombre(x)


def comparer(x, y):
    """−1, 0 ou 1, exactement : même radicande (ou un rationnel), par le signe de x − y ; sinon par encadrements raffinés (deux
    écritures différentes sont deux valeurs différentes, l'écriture étant unique)."""
    x, y = nombre(x), nombre(y)
    if x == y:
        return 0
    if x.q == 0 or y.q == 0 or x.m == y.m:
        return (x - y).signe()
    chiffres = 10
    while True:
        (a, b), (c, d) = x.encadrement(chiffres), y.encadrement(chiffres)
        if b < c:
            return -1
        if d < a:
            return 1
        chiffres *= 2


def croissant(nombres):
    """Les Nombre distincts, en ordre croissant (S, D14)."""
    distincts = []
    for n in nombres:
        if n not in distincts:
            distincts.append(n)
    return sorted(distincts, key=cmp_to_key(comparer))


# =====================================================================
# 3. POLYNÔMES À COEFFICIENTS NOMBRE (facteurs) ET GARDE-FOU
# =====================================================================
def en_nombres(P):
    """Un polynôme (Polynome, ou suite de coefficients exacts ou de Nombre, ordre croissant) en tuple de Nombre, sans zéro de tête."""
    c = [nombre(x) for x in P]
    while len(c) > 1 and c[-1] == 0:
        c.pop()
    return tuple(c) or (Nombre(0),)


def rationnel(f):
    """Le Polynome d'un facteur à coefficients rationnels, ou None."""
    f = en_nombres(f)
    return Polynome(c.p for c in f) if all(c.q == 0 for c in f) else None


def _monome_n(k, j):
    return (Nombre(0),) * j + (nombre(k),)


def _pmul(a, b):
    r = [Nombre(0)] * (len(a) + len(b) - 1)
    for i, u in enumerate(a):
        for j, v in enumerate(b):
            r[i + j] = r[i + j] + u * v
    return en_nombres(r)


def redevelopper(facteurs):
    """Le produit exact des facteurs (dans Q(√m)), en tuple de Nombre sans zéro de tête."""
    produit = (Nombre(1),)
    for f in facteurs:
        produit = _pmul(produit, en_nombres(f))
    return produit


def verifier_solution(P, x):
    """P(x) = 0 exactement (Horner dans Q(√m)) : chaque solution est substituée exactement dans l'équation (principe 1)."""
    v = Nombre(0)
    for c in reversed(en_nombres(P)):
        v = v * nombre(x) + c
    return v == 0


# =====================================================================
# 4. MÉTHODES (calcul seul)
# =====================================================================
def mise_en_evidence(P, constante=True):
    """ME (E3, D21) : facteur k·xʲ, avec k = pgcd des coefficients (−pgcd si a < 0) et xʲ la plus grande puissance commune ;
    constante=False (variante E12) : seulement xʲ. {k, j, facteur (Polynome k·xʲ), reste (Polynome), facteurs} ou None (rien à
    mettre en évidence, un seul terme, ou coefficients non entiers : § 13.4)."""
    P = Polynome(P)
    if not P.entiers() or sum(1 for c in P if c != 0) < 2:
        return None
    j = next(i for i, c in enumerate(P) if c != 0)
    k = 1
    if constante:
        k = 0
        for c in P:
            k = gcd(k, int(c))
        k = -k if P[-1] < 0 else k
    if k == 1 and j == 0:
        return None
    facteur = Polynome((0,) * j + (k,))
    reste = Polynome(c / k for c in P[j:])
    return {"k": k, "j": j, "facteur": facteur, "reste": reste, "facteurs": [en_nombres(facteur), en_nombres(reste)]}


def identite(P):
    """Id. rem. sur un polynôme développé (E5, D8, § 13.4) : A = k·xʲ (k rationnel > 0, k² = a), degré 2j.
    - A² − B² : P = a·x²ʲ + c, c < 0 ; B = √|c| sous forme simplifiée (2√2, √2/2), irrationnelle seulement si j = 1 ; facteurs (A + B)(A − B) ;
    - A² ± 2AB + B² : P = a·x²ʲ + b·xʲ + c, c = B² > 0 (B rationnel), b = ±2kB ; facteurs (A ± B)(A ± B).
    {methode, A: (k, j), B: Nombre, facteurs} ou None."""
    P = Polynome(P)
    n = P.degre
    if n < 2 or n % 2 or P[n] <= 0:
        return None
    j = n // 2
    k = polynomes.racine_carree(P[n])
    if k is None:
        return None
    termes = {i for i, c in enumerate(P) if c != 0}
    if termes == {n, 0} and P[0] < 0:
        B = Nombre.racine(-P[0])
        if j > 1 and not B.rationnel:
            return None
        plus, moins = (B,) + _monome_n(k, j)[1:], (-B,) + _monome_n(k, j)[1:]
        return {"methode": "IDREM_DIFF", "A": (k, j), "B": B, "facteurs": [plus, moins]}
    if termes == {n, j, 0} and P[0] > 0:
        B = polynomes.racine_carree(P[0])
        if B is None or abs(P[j]) != 2 * k * B:
            return None
        signe = 1 if P[j] > 0 else -1
        facteur = (Nombre(signe * B),) + _monome_n(k, j)[1:]
        return {"methode": "IDREM_PLUS" if signe > 0 else "IDREM_MOINS", "A": (k, j), "B": Nombre(B), "facteurs": [facteur, facteur]}
    return None


def _entier(x, nom):
    x = _fraction(x)
    if x.denominator != 1:
        raise ValueError(f"{nom} entier attendu")
    return int(x)


def _ligne_sp(d, b, c):
    """La ligne du diviseur d (E6) : c > 0, les deux nombres ont le signe de b (positifs si b = 0) ; c < 0, le plus grand en valeur
    absolue a le signe de b (à égalité, le négatif en premier). (u, v), u le plus petit en valeur absolue."""
    e = abs(c) // d
    s = -1 if b < 0 else 1
    if c > 0:
        return s * d, s * e
    if d == e:
        return -d, d
    return -s * d, s * e


def essais_sp(b, c):
    """Tableau S-P de x² + bx + c (E6, D3) : une ligne (u, v, u + v) par diviseur d ≤ √|c| de c (d = 1, 2, …), arrêt à la ligne ✓.
    {lignes, ok (indice de la ligne ✓ ou None), trop (plus de 12 lignes seraient affichées : pas de tableau, § 13.5)} ; quand
    `trop`, les lignes s'arrêtent à la 13e. b et c entiers, c ≠ 0 ; |c| ≥ 10⁹ : HorsBornes."""
    b, c = _entier(b, "b"), _entier(c, "c")
    if c == 0:
        raise ValueError("c = 0 : la ME vient avant le S-P")
    if abs(c) >= 10 ** CHIFFRES_MAX:
        raise HorsBornes("coefficient de plus de 9 chiffres")
    lignes, ok, d = [], None, 1
    while d * d <= abs(c):
        if c % d == 0:
            u, v = _ligne_sp(d, b, c)
            lignes.append((u, v, u + v))
            if u + v == b:
                ok = len(lignes) - 1
                break
            if len(lignes) > LIGNES_SP_MAX:
                break
        d += 1
    return {"lignes": lignes, "ok": ok, "trop": len(lignes) > LIGNES_SP_MAX}


def diviseurs_signes(c):
    """Les diviseurs entiers de c ≠ 0, dans l'ordre des essais du tâtonnement : 1, −1, 2, −2, … (|d| croissant, E7). Sans borne
    d'affichage (§ 13.5) ; |c| ≥ 10⁹ : HorsBornes (hors des bornes de la saisie)."""
    c = abs(_entier(c, "c"))
    if c == 0:
        raise ValueError("c = 0 : la ME vient avant le tâtonnement")
    if c >= 10 ** CHIFFRES_MAX:
        raise HorsBornes("coefficient de plus de 9 chiffres")
    petits = [d for d in range(1, isqrt(c) + 1) if c % d == 0]
    positifs = sorted(set(petits) | {c // d for d in petits})
    return [s * d for d in positifs for s in (1, -1)]


def _delta(P):
    c, b, a = P
    return b * b - 4 * a * c


def _racines_rationnelles(P):
    """Les racines rationnelles d'un trinôme (Δ carré d'un rationnel), décidées par Δ ; [] sinon."""
    c, b, a = P
    r = polynomes.racine_carree(_delta(P)) if _delta(P) >= 0 else None
    return [] if r is None else sorted({(-b - r) / (2 * a), (-b + r) / (2 * a)})


def racine_entiere_unique(P):
    """La racine entière du trinôme P (coefficients entiers, a ≠ 0), décidée par Δ (aucune borne) : la première dans l'ordre des
    essais (|r| croissant, la positive d'abord) ; unique quand P est primitif et a ≠ ±1 (E7). None s'il n'y en a pas."""
    P = Polynome(P)
    if P.degre != 2 or not P.entiers():
        raise ValueError("trinôme à coefficients entiers attendu")
    entieres = [r for r in _racines_rationnelles(P) if r.denominator == 1]
    return int(min(entieres, key=lambda r: (abs(r), r < 0))) if entieres else None


def racines_formule(P):
    """La formule sur un trinôme à coefficients rationnels (E10) : {a, b, c, delta, racine_delta, x1, x2, x, solutions, facteurs}.
    Δ > 0 : x₁ = (−b − √Δ)/(2a), x₂ = (−b + √Δ)/(2a) (nommés selon la formule, même si a < 0 : § 13.4), x = None ; Δ = 0 : x = −b/(2a) ;
    Δ < 0 : aucune solution, facteurs None. solutions : croissantes. facteurs : a(x − x₁)(x − x₂) (Δ ≥ 0), pour le garde-fou."""
    P = Polynome(P)
    if P.degre != 2:
        raise ValueError("trinôme attendu")
    c, b, a = P
    delta = _delta(P)
    r = {"a": a, "b": b, "c": c, "delta": delta, "racine_delta": None, "x1": None, "x2": None, "x": None, "solutions": [],
         "facteurs": None}
    if delta == 0:
        x = Nombre(-b / (2 * a))
        r.update(racine_delta=Nombre(0), x=x, solutions=[x], facteurs=[(Nombre(a),), (-x, Nombre(1)), (-x, Nombre(1))])
    elif delta > 0:
        rd = Nombre.racine(delta)
        x1, x2 = (-b - rd) / (2 * a), (-b + rd) / (2 * a)
        r.update(racine_delta=rd, x1=x1, x2=x2, solutions=croissant([x1, x2]),
                 facteurs=[(Nombre(a),), (-x1, Nombre(1)), (-x2, Nombre(1))])
    return r


def _calcul_sp(P):
    if P.degre != 2:
        return None
    c, b, a = P
    if a != 1 or not P.entiers() or c == 0:
        return None
    entieres = [r for r in _racines_rationnelles(P) if r.denominator == 1]
    if not entieres:
        return None                                              # aucun couple (décidé par Δ)
    u, v = _ligne_sp(int(min(abs(r) for r in entieres)), int(b), int(c))
    return {"essais": essais_sp(b, c), "p": u, "q": v, "facteurs": [(Nombre(u), Nombre(1)), (Nombre(v), Nombre(1))]}


def _calcul_tatonnement(P):
    if P.degre != 2:
        return None
    c, b, a = P
    if not P.entiers() or a < 2 or c == 0:
        return None
    r = racine_entiere_unique(P)
    if r is None:
        return None
    triangle = int(b + a * r)                                    # ax² + bx + c = (x − r)(ax + △), (−r)·△ = c
    return {"diviseurs": diviseurs_signes(c), "r": r, "triangle": triangle,
            "facteurs": [(Nombre(-r), Nombre(1)), (Nombre(triangle), Nombre(a))]}


def calculer(methode, P):
    """Le calcul de la méthode sur P (sans texte), ou None si elle n'aboutit pas (§ 13.4) ; chaque résultat a ses `facteurs`
    (produit exact = P), sauf la formule quand Δ < 0 (facteurs None). Méthodes : METHODES."""
    if methode not in METHODES:
        raise ValueError(f"méthode inconnue : {methode}")
    P = Polynome(P)
    if P.degre < 2:
        return None
    if methode in ("ME", "ME_PUISSANCE"):
        return mise_en_evidence(P, constante=methode == "ME")
    if methode == "IDREM" or methode in IDREM:
        r = identite(P)
        return r if r is not None and methode in ("IDREM", r["methode"]) else None
    if methode == "SP":
        return _calcul_sp(P)
    if methode == "TATONNEMENT":
        return _calcul_tatonnement(P)
    return racines_formule(P) if P.degre == 2 else None


def s_applique(methode, P):
    """« La méthode aboutit » (§ 13.4) : S-P, un couple existe (même si le tableau aurait plus de 12 lignes : le chemin prend alors
    la formule, point 5) ; tâtonnement, une racine entière existe ; Id. rem. et ME, la factorisation existe ; formule, toujours
    (trinôme). Mêmes règles que le chemin du cours (E5, E6, E7, D21, D22)."""
    return calculer(methode, P) is not None


# =====================================================================
# 5. PRODUIT NUL ET CHEMIN DU COURS
# =====================================================================
def produit_nul(facteurs, formules=None):
    """Produit nul (E8, D14, D24) : un facteur répété n'est écrit qu'une fois ; constante → impossible ; monôme k·xʲ → x = 0 ;
    degré 1 → sa racine ; trinôme rationnel → la formule (E9 ; formules : {trinôme : racines_formule déjà calculée}, pour ne pas
    la refaire). {facteurs: [(facteur, genre, solutions)], solutions (croissantes)}."""
    vus, lignes = [], []
    for f in facteurs:
        f = en_nombres(f)
        if f in vus:
            continue
        vus.append(f)
        n = len(f) - 1
        if n == 0:
            lignes.append((f, "constante", []))
        elif sum(1 for c in f if c != 0) == 1:
            lignes.append((f, "monome", [Nombre(0)]))
        elif n == 1:
            lignes.append((f, "lineaire", [-f[0] / f[1]]))
        elif n == 2 and rationnel(f) is not None:
            r = (formules or {}).get(rationnel(f)) or racines_formule(rationnel(f))
            lignes.append((f, "formule", r["solutions"]))
        else:
            raise ValueError(f"facteur non résolu : {f}")
    return {"facteurs": lignes, "solutions": croissant([x for _, _, s in lignes for x in s])}


def _etape(methode, cible, aboutit, resultat):
    return {"methode": methode, "cible": cible, "aboutit": aboutit, "resultat": resultat}


def _factoriser(Q, methodes, etapes):
    """Les facteurs finals de Q (tuples de Nombre ; un trinôme résolu par la formule reste entier, E9), ou None (aucune méthode)."""
    if Q.degre <= 1 or Q.monome():
        return [en_nombres(Q)]
    if "ME" in methodes or "ME_PUISSANCE" in methodes:
        r = mise_en_evidence(Q, constante="ME" in methodes)
        if r is not None:
            etapes.append(_etape("ME", Q, True, r))
            suite = _factoriser(r["reste"], methodes, etapes)
            return None if suite is None else [r["facteurs"][0]] + suite
    if "IDREM" in methodes:
        r = identite(Q)
        if r is not None:
            etapes.append(_etape(r["methode"], Q, True, r))
            finals, deja = [], {}
            for f in r["facteurs"]:
                if f not in deja:
                    g = rationnel(f)
                    deja[f] = _factoriser(g, methodes, etapes) if g is not None and g.degre >= 2 else [f]
                if deja[f] is None:
                    return None
                finals += deja[f]
            return finals
    if Q.degre != 2:
        return None
    c, b, a = Q
    if "SP" in methodes and a == 1 and Q.entiers() and c != 0:
        essais = essais_sp(b, c)
        if essais["ok"] is not None and not essais["trop"]:
            r = _calcul_sp(Q)
            etapes.append(_etape("SP", Q, True, r))
            return list(r["facteurs"])
        etapes.append(_etape("SP", Q, False, {"essais": essais}))      # D3 (échec) ou plus de 12 lignes (§ 13.5)
    elif "TATONNEMENT" in methodes and Q.entiers() and a >= 2 and c != 0:
        r = _calcul_tatonnement(Q)
        if r is not None:
            etapes.append(_etape("TATONNEMENT", Q, True, r))
            return list(r["facteurs"])
        etapes.append(_etape("TATONNEMENT", Q, False, {"diviseurs": diviseurs_signes(c)}))     # D1
    if "FORMULE" in methodes:
        etapes.append(_etape("FORMULE", Q, True, racines_formule(Q)))
        return [en_nombres(Q)]
    return None


def chemin(P, methodes=ORDRE_DU_COURS):
    """Le chemin du cours pour P = 0, sans texte (D28 : ME, Id. rem., S-P, tâtonnement, formule, dans cet ordre).

    {statut: "resolu" | "hors_cours" | "ne_conclut_pas",
     ensemble: "fini" | "reels" (P nul : S = ℝ) | "vide" (constante non nulle) | None,
     etapes: [{methode, cible (Polynome), aboutit, resultat}] (tentatives en échec comprises : S-P, tâtonnement),
     facteurs: facteurs finals (tuples de Nombre, avec leur multiplicité), produit_nul, solutions: [Nombre] croissantes}.
    Garde-fou (principe 1) : chaque factorisation se redéveloppe exactement en sa cible, les facteurs finals en P, et chaque solution
    annule P exactement ; sinon « ne_conclut_pas », sans solutions. Degré ≥ 3 sans ME ni Id. rem. qui aboutisse : « hors_cours »."""
    P = Polynome(P)
    vide = {"etapes": [], "facteurs": [], "produit_nul": None, "solutions": []}
    if P.nul():
        return dict(vide, statut="resolu", ensemble="reels")
    if P.degre == 0:
        return dict(vide, statut="resolu", ensemble="vide")
    etapes = []
    if P.degre == 1:
        x = Nombre(-P[0] / P[1])
        etapes.append(_etape("ISOLER", P, True, {"solution": x}))
        facteurs = [en_nombres(P)]
    else:
        facteurs = _factoriser(P, methodes, etapes)
        if facteurs is None:
            return dict(vide, statut="hors_cours", ensemble=None, etapes=etapes)
    pn = produit_nul(facteurs, {e["cible"]: e["resultat"] for e in etapes if e["methode"] == "FORMULE"})
    if not _garde_fou(P, etapes, facteurs, pn["solutions"]):
        return dict(vide, statut="ne_conclut_pas", ensemble=None, etapes=etapes)
    return {"statut": "resolu", "ensemble": "fini" if pn["solutions"] else "vide", "etapes": etapes, "facteurs": facteurs,
            "produit_nul": pn, "solutions": pn["solutions"]}


def _garde_fou(P, etapes, facteurs, solutions):
    try:
        return _garde_fou_exact(P, etapes, facteurs, solutions)
    except (TypeError, ZeroDivisionError):                       # deux radicandes dans un même produit : le calcul ne conclut pas
        return False


def _garde_fou_exact(P, etapes, facteurs, solutions):
    for e in etapes:
        f = e["resultat"].get("facteurs") if e["aboutit"] else None
        if f is not None and redevelopper(f) != en_nombres(e["cible"]):
            return False
        if e["methode"] == "FORMULE" and e["resultat"]["delta"] >= 0:
            if not all(verifier_solution(e["cible"], x) for x in e["resultat"]["solutions"]):
                return False
    if redevelopper(facteurs) != en_nombres(P):
        return False
    return all(verifier_solution(P, x) for x in solutions)


# =====================================================================
# 6. VALEURS APPROCHÉES (E14)
# =====================================================================
def approx_garantie(x, decimales=3):
    """nombres.approx de x (Nombre), garanti : approx des deux bornes d'un encadrement de x, raffiné jusqu'à ce qu'elles s'écrivent
    pareil (l'arrondi est croissant, donc x s'écrit comme elles). x rationnel : approx de sa valeur exacte. ValueError si
    l'encadrement ne conclut pas (jamais un arrondi douteux)."""
    x = nombre(x)
    if x.rationnel:
        return approx(x.p, decimales)
    chiffres = decimales + 10
    while chiffres <= 4000:
        bas, haut = x.encadrement(chiffres)
        a = approx(bas, decimales)
        if a == approx(haut, decimales):
            return a
        chiffres *= 2
    raise ValueError("valeur approchée non garantie")
