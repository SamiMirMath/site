"""
second_degre.py — Brique commune : équations polynomiales du 2e degré (et ce qui s'y ramène), en Python pur, sans SymPy.

Chantier equations-2e-degre (docs/chantiers/equations-2e-degre/decisions.md, § 13 en tête). **P1 : le calcul** (sections 1 à 6),
**P2b : la rédaction** (section 7 : `resoudre_equation`, `appliquer`, étapes structurées du § 5), la saisie en P3. Tout est exact :
polynômes à coefficients `Fraction` (`Polynome`), nombres p + q√m (`Nombre`, sur `noyau.racine_q` : pas de nouvelle simplification
de k√m/d, § 13.2).

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
    resoudre_equation(g, d, x, …)     la résolution rédigée (§ 5) : {statut, etapes, solutions, S, approx, variantes, message}
    appliquer(methode, P)             une méthode seule, rédigée (Etape), ou None si elle n'aboutit pas
    blocs(resolution)                 les blocs de moteur/sortie.py : la chaîne (bloc_rangees, membre de gauche), S encadré, la ligne ≈
    nb_exact, arbre_polynome,         l'écriture des valeurs exactes en arbres de moteur/expr.py (E11, E14 ; nombres.exact)
    arbre_nombre, termes_developpes

Les facteurs sont des tuples de `Nombre` (ordre croissant) : (5x + √3) est (Nombre(0, 1, 3), Nombre(5)). Les noms de méthodes sont
ceux du § 5 (« ME », « IDREM_DIFF », « IDREM_PLUS », « IDREM_MOINS », « SP », « TATONNEMENT », « FORMULE », « PRODUIT_NUL »,
« ISOLER »), plus « IDREM » (la famille, pour l'ordre du cours) et « ME_PUISSANCE » (la variante E12 : seulement xʲ).

Aucun état : aucune variable de module n'est modifiée (A7) ; les décimaux de l'énoncé sont un paramètre (`decimaux_enonce`).
"""
from fractions import Fraction as F
from functools import cmp_to_key
from math import gcd, isqrt
from types import MappingProxyType

import polynomes
import sortie
from chaine import Chaine, Eq, LigneTexte, Ou, bloc_rangees, rangees_chaine
from expr import Defini, Fn, Nb, Neg, Noeud, Op, Pow, Var, entre_parentheses, nom_tex, tex, variables
from noyau import racine_q, squarefree
from nombres import approx, exact

__all__ = ["Polynome", "Nombre", "HorsBornes", "vers_polynome", "mise_en_evidence", "identite", "essais_sp", "diviseurs_signes",
           "racine_entiere_unique", "racines_formule", "s_applique", "calculer", "chemin", "produit_nul", "redevelopper",
           "verifier_solution", "approx_garantie", "ORDRE_DU_COURS", "ORDRE_PAR_LA_FORMULE", "METHODES",
           "resoudre_equation", "appliquer", "blocs", "nb_exact", "arbre_polynome", "arbre_nombre", "termes_developpes", "Produit",
           "SansLien", "rangees", "OPTIONS_CHAINE", "MESSAGES", "PHRASE_IDENTITE", "PHRASE_EGALITE_FAUSSE"]

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


# =====================================================================
# 7. RÉDACTION (P2b) : étapes structurées du § 5, sur le calcul des sections 1 à 6
# =====================================================================
OPTIONS_CHAINE = MappingProxyType({"etiquette_grise": True, "impossible": True, "coupure_ou": True})   # D5, D7, § 13.3 (« ou »)

MESSAGES = MappingProxyType({                                                       # § 4 et § 13.5 (vouvoiement : aucun verbe à l'élève)
    "hors_cours": "Cette équation ne se résout pas avec les méthodes du cours.",
    "ne_conclut_pas": "Le calcul ne permet pas de conclure avec certitude : cette équation n'est pas résolue ici.",
    "hors_bornes": "Cette équation dépasse ce que l'outil sait traiter.",
    "non_traite": "Cette forme d'équation n'est pas encore traitée par l'outil.",
})
PHRASE_IDENTITE = "Cette égalité est vraie pour tout nombre réel."                  # celle d'Exp-log (§ 13.4), pour P4b
PHRASE_EGALITE_FAUSSE = "Cette égalité est fausse : l'équation n'a aucune solution."    # celle d'Exp-log, pour P4b
PHRASE_SP_TROP = "Le trinôme est unitaire, mais il y a trop de couples à tester : on utilise la formule."      # § 13.5
PHRASE_SP_ECHEC = "Aucun couple ne convient : on utilise la formule."                                         # D3


class _Incoherent(Exception):
    """Une valeur écrite ne vérifie pas son calcul : la résolution ne conclut pas (principe 1)."""


# ---------- écriture des nombres et des polynômes en arbres (moteur/expr.py) ----------
def nb_exact(v, decimaux_enonce=False):
    """Le `Nb` d'une valeur exacte calculée (E14, R13), sans état : écrit comme `nombres.exact(v, decimaux_enonce)` (une fraction ;
    un décimal fini d'au plus 8 décimales si l'énoncé a des décimaux) ; même résultat qu'`exp_log._nb_exact` sous son état
    `_DECIMAUX` (test croisé)."""
    v = _fraction(v)
    s = exact(v, decimaux_enonce)
    if "{,}" not in s:
        return Nb(v)
    return Nb(v, s.lstrip("-").replace(r"\text{’}", "").replace("{,}", ","))


def _signe_et_abs(c):
    return (-1 if c < 0 else 1), abs(c)


def _puissance(X, j):
    return X if j == 1 else Pow(X, Nb(j))


def _monome_abs(c, j, X, dec):
    """|c|·xʲ (c rationnel non nul) en arbre : x², 3x, \\frac{3}{2}x², 5."""
    c = abs(c)
    if j == 0:
        return nb_exact(c, dec)
    return _puissance(X, j) if c == 1 else Op("*", nb_exact(c, dec), _puissance(X, j))


def _somme(termes):
    """[(signe, arbre)] en une somme : le premier terme porte son signe (Neg), les suivants « + » ou « − »."""
    (s, t), reste = termes[0], termes[1:]
    a = Neg(t) if s < 0 else t
    for s, t in reste:
        a = Op("-" if s < 0 else "+", a, t)
    return a


def arbre_polynome(P, inconnue="x", decimaux_enonce=False):
    """L'écriture développée et ordonnée de P (Polynome, ou coefficients exacts en ordre croissant) : 4x² + 2x − 56, x² − 5,
    \\frac{3}{2}x² − 4x − 1 (décimaux de l'énoncé : 0,5x² − 2)."""
    P, X = Polynome(P), Var(inconnue)
    termes = [(_signe_et_abs(c)[0], _monome_abs(c, j, X, decimaux_enonce)) for j, c in reversed(list(enumerate(P))) if c != 0]
    return _somme(termes) if termes else Nb(0)


def arbre_nombre(n, decimaux_enonce=False):
    """L'écriture exacte d'un Nombre (E11) : fraction réduite, signe devant ; p + q√m regroupé en une seule fraction réduite :
    −2 − √5, \\frac{-5 - \\sqrt{17}}{2}, -\\frac{\\sqrt{3}}{5}, 2\\sqrt{2}, \\frac{\\sqrt{2}}{2}."""
    n = nombre(n)
    if n.rationnel:
        return nb_exact(n.p, decimaux_enonce)
    A, B, m, d = n.forme_reduite()
    racine = Fn("sqrt", Nb(m))
    qr = racine if abs(B) == 1 else Op("*", Nb(abs(B)), racine)
    if A == 0:
        t = qr if d == 1 else Op("/", qr, Nb(d))
        return Neg(t) if B < 0 else t
    num = Op("+" if B > 0 else "-", Nb(A), qr)
    return num if d == 1 else Op("/", num, Nb(d))


def _arbre_facteur(f, X, dec):
    """Un facteur (tuple de Nombre, ordre croissant) écrit développé : 2x − 7, 5x + √3, x² − 2x − 2. Seul le terme constant peut être
    irrationnel (Id. rem. avec B = √k)."""
    f = en_nombres(f)
    termes = []
    for j in range(len(f) - 1, -1, -1):
        c = f[j]
        if c == 0:
            continue
        if j > 0:
            if not c.rationnel:
                raise _Incoherent("coefficient irrationnel devant l'inconnue")
            termes.append((_signe_et_abs(c.p)[0], _monome_abs(c.p, j, X, dec)))
        else:
            s = c.signe()
            termes.append((s, arbre_nombre(c if s > 0 else -c, dec)))
    return _somme(termes) if termes else Nb(0)


class Produit(Noeud):
    """Un produit factorisé du corrigé, écrit comme lui : k·xʲ suivi des facteurs entre parenthèses, chacun avec son exposant
    (1 ou 2) : 6(x² − 1), 3x(x − 4), −(y − 1)(y − 9), 3(2x − 1)², (t + 10)(t + 10), 2(x + 4)(2x − 7). Nœud propre à l'outil
    (moteur/expr.py : il s'écrit lui-même)."""
    __slots__ = ("k", "j", "x", "facteurs")

    def __init__(self, k, j, x, facteurs):
        self.k, self.j, self.x, self.facteurs = F(k), j, x, tuple(facteurs)

    def ecrire_tex(self):
        s = "-" if self.k == -1 else "" if self.k == 1 else tex(Nb(self.k))
        if self.j:
            s += nom_tex(self.x) + ("^{" + str(self.j) + "}" if self.j > 1 else "")
        if not self.facteurs:
            return s if s not in ("", "-") else s + "1"
        if s == "" and len(self.facteurs) == 1 and self.facteurs[0][1] == 1:
            return tex(self.facteurs[0][0])
        return s + "".join(entre_parentheses(tex(a)) + ("^{" + str(e) + "}" if e > 1 else "") for a, e in self.facteurs)


def _est_zero(n):
    return isinstance(n, Nb) and n.val == 0


def _constante_ecrite(n):
    """La valeur d'un coefficient écrit (5 ; 3/2 ; −4), ou None."""
    if isinstance(n, Nb):
        return n.val
    if isinstance(n, Op) and n.op == "/" and isinstance(n.a, Nb) and isinstance(n.b, Nb) and n.b.val != 0:
        return n.a.val / n.b.val
    return None


def _monome_ecrit(n, x):
    """(j, k) pour un monôme écrit k·xʲ (5 ; x ; 3x² ; \\frac{3}{2}x² ; −x), ou None."""
    if isinstance(n, Neg):
        m = _monome_ecrit(n.a, x)
        return None if m is None else (m[0], -m[1])
    k = _constante_ecrite(n)
    if k is not None:
        return 0, k
    if isinstance(n, Var) and n.nom == x:
        return 1, F(1)
    if isinstance(n, Pow) and isinstance(n.a, Var) and n.a.nom == x and isinstance(n.b, Nb) and n.b.val.denominator == 1 \
            and n.b.val >= 2:
        return int(n.b.val), F(1)
    if isinstance(n, Op) and n.op == "*":
        k, m = _constante_ecrite(n.a), _monome_ecrit(n.b, x)
        if k is not None and m is not None and m[0] >= 1 and m[1] == 1:
            return m[0], k
    return None


def termes_developpes(arbre, inconnue):
    """[(j, k)] si l'arbre est une somme de monômes k·xʲ écrits développés, en degrés strictement décroissants, sans coefficient nul
    (« 0 » seul : le polynôme nul) ; None sinon (à ramener, à développer ou à réordonner : P3)."""
    def termes(n):
        if isinstance(n, Op) and n.op in "+-":
            g, d = termes(n.a), _monome_ecrit(n.b, inconnue)
            if g is None or d is None:
                return None
            return g + [(d[0], -d[1] if n.op == "-" else d[1])]
        m = _monome_ecrit(n, inconnue)
        return None if m is None else [m]
    t = termes(arbre)
    if t is None:
        return None
    if t == [(0, 0)]:
        return t
    if any(k == 0 for _, k in t) or any(a <= b for (a, _), (b, _) in zip(t, t[1:])):
        return None
    return t


# ---------- rangées : segments de chaîne, lignes pleine largeur, rangées sans lien ----------
class SansLien:
    """Une rangée sans lien {lien: "", expr} au milieu d'un segment (lignes de Δ, √Δ, x₁, x₂ : point 3 du plan) : passée à la chaîne
    comme une ligne pleine largeur, puis rendue en rangée par `rangees`."""
    __slots__ = ("tex",)

    def __init__(self, tex_):
        self.tex = tex_

    def __eq__(self, o):
        return isinstance(o, SansLien) and o.tex == self.tex

    def __hash__(self):
        return hash(self.tex)


def _rangee_libre(contenu):
    return ("", contenu.tex, None) if isinstance(contenu, SansLien) else LigneTexte(contenu)


def rangees(segment):
    """Les rangées d'un segment (`chaine.rangees_chaine` avec OPTIONS_CHAINE), une `SansLien` y devenant la rangée ("", tex, None)."""
    return [_rangee_libre(r.contenu) if isinstance(r, LigneTexte) else r for r in rangees_chaine(segment, **OPTIONS_CHAINE)]


class _Redaction:
    """Écrit les étapes une à une. Une étape est un segment `Chaine([pivot, …])` dont tous les liens sont des ⇔ (le pivot : le
    dernier élément écrit, ou l'énoncé), ses lignes pleine largeur au milieu ; l'énoncé n'est écrit qu'au premier ⇔ (§ 13.3 : pas
    de répétition quand aucun ⇔ ne suit) ; les lignes écrites après le dernier ⇔ d'une étape la terminent."""

    def __init__(self, enonce):
        self.etapes, self.pivot, self.enonce_ecrit = [], enonce, False
        self._courante = None

    def etape(self, phase, methode, cible, parametres):
        self.fermer()
        self._courante = {"phase": phase, "methode": methode, "cible": cible, "parametres": parametres, "lignes": [],
                          "segment": None}
        self._attente, self._segment = [], None
        self.etapes.append(self._courante)

    def texte(self, contenu):
        self._attente.append(contenu)

    def rangee(self, tex_):
        self._attente.append(SansLien(tex_))

    def equiv(self, element, prop=None):
        if self._segment is None:
            self._segment = Chaine([self.pivot])
        self._segment.ajouter(element, "⇔", prop, texte_avant=self._attente or None)
        self._attente, self.pivot = [], element

    def fermer(self):
        e = self._courante
        if e is None:
            return
        lignes = []
        if self._segment is not None:
            r = rangees(self._segment)
            lignes = r if not self.enonce_ecrit else r[1:]
            self.enonce_ecrit = True
        e["lignes"] = lignes + [_rangee_libre(c) for c in self._attente]
        e["segment"] = self._segment
        self._courante, self._attente = None, []


# ---------- phrases et lignes de chaque méthode ----------
def _t(n):
    return tex(n)


def _par(c):
    """Un entier en TeX, entre parenthèses s'il est négatif : (−4)."""
    return "(" + exact(c) + ")" if c < 0 else exact(c)


def _signe_tex(v):
    return (" - " if v < 0 else " + ") + exact(abs(v))


class _Contexte:
    """Ce que les méthodes écrivent autour d'elles : l'inconnue, les décimaux de l'énoncé, le préfixe k·xʲ de la ME déjà faite, les
    phrases de choix (chemin du cours) et le pivot."""

    def __init__(self, inconnue, decimaux_enonce, cours=True):
        self.x, self.X, self.dec, self.cours = inconnue, Var(inconnue), decimaux_enonce, cours
        self.k, self.j, self.apres_me = F(1), 0, False

    def produit(self, facteurs):
        """L'équation « k·xʲ · facteurs = 0 »."""
        return Eq(Produit(self.k, self.j, self.x, facteurs), Nb(0))

    def poly(self, Q):
        return arbre_polynome(Q, self.x, self.dec)

    def facteur(self, f):
        return _arbre_facteur(f, self.X, self.dec)

    def monome(self, k, j):
        s, _ = _signe_et_abs(k)
        t = _monome_abs(k, j, self.X, self.dec)
        return Neg(t) if s < 0 else t


def _ecrire_me(R, ctx, Q, r):
    """E3 : « −6x² + 12x − 6 = 0 ⇔ −6(x² − 2x + 1) = 0 » (ME), précédé de la phrase de a < 0 (D21)."""
    a, facteur = Q[-1], ctx.monome(r["k"], r["j"])
    R.etape("factoriser", "ME", _t(ctx.poly(Q)), {"facteur": r["facteur"], "k": r["k"], "j": r["j"], "reste": r["reste"],
                                                   "facteurs": r["facteurs"]})
    if r["k"] < 0:
        if a == -1:
            R.texte(rf"Le trinôme n'est pas unitaire (\(a = -1\)) : on met d'abord \({_t(facteur)}\) en évidence.")
        else:
            R.texte(rf"Le coefficient de \({_t(_puissance(ctx.X, Q.degre))}\) est négatif (\(a = {exact(a)}\)) : on met d'abord "
                    rf"\({_t(facteur)}\) en évidence.")
    ctx.k, ctx.j, ctx.apres_me = ctx.k * r["k"], ctx.j + r["j"], True
    R.equiv(ctx.produit([(ctx.poly(r["reste"]), 1)]), "ME")


def _ecrire_idrem(R, ctx, Q, r):
    """E5 : A² − B² en étiquette ; A² ± 2AB + B² par une ligne de vérification, puis le carré et sa réécriture (D24). A et B
    encadrés ensemble, comme D29 l'écrit (« avec ⟦A = 4z, B = 9⟧ »)."""
    (k, j), B = r["A"], r["B"]
    A_tex, B_tex = _t(_monome_abs(k, j, ctx.X, ctx.dec)), _t(arbre_nombre(B, ctx.dec))
    R.etape("factoriser", r["methode"], _t(ctx.poly(Q)), {"A": (k, j), "B": B, "facteurs": r["facteurs"]})
    avec = rf"avec \(\fbox{{$A = {A_tex},\ B = {B_tex}$}}\)"
    f1, f2 = (ctx.facteur(f) for f in r["facteurs"])
    if r["methode"] == "IDREM_DIFF":
        R.equiv(ctx.produit([(f1, 1), (f2, 1)]), rf"Id. rem. \(A^{{2}} - B^{{2}}\) {avec}")
        return
    deux_ab = _t(_monome_abs(2 * k * B.p, j, ctx.X, ctx.dec))
    signe = "+" if r["methode"] == "IDREM_PLUS" else "-"
    R.texte(rf"Id. rem. \(A^{{2}} {signe} 2AB + B^{{2}}\) {avec}. Vérification : \(2AB = 2 \cdot {A_tex} \cdot {B_tex} = {deux_ab}\) "
            r"\(\checkmark\)")
    R.equiv(ctx.produit([(f1, 2)]))
    R.equiv(ctx.produit([(f1, 1), (f1, 1)]))


def _choix(ctx, Q, unitaire, methode):
    """E4 (D19) : la phrase de choix, avant le S-P, le tâtonnement ou la formule (seulement sur le chemin du cours)."""
    if methode == "FORMULE":
        return "Pas de ME, pas d'Id. rem. ; les coefficients ne sont pas entiers : on utilise la formule."
    if ctx.apres_me:
        return rf"Le trinôme \({_t(ctx.poly(Q))}\) " + ("est unitaire : S-P." if unitaire else "n'est pas unitaire : tâtonnement.")
    if unitaire:
        return r"Pas de ME, pas d'Id. rem. ; le trinôme est unitaire (\(a = 1\)) : S-P."
    return rf"Pas de ME, pas d'Id. rem. ; \(a = {exact(Q[2])} \neq 1\) : tâtonnement."


def _tableau_sp(b, c, essais):
    return sortie.tableau_essais([(r"produit \(= " + exact(c) + r"\)", 2), ("somme", 1)],
                                 [[exact(u), exact(v), exact(s)] for u, v, s in essais["lignes"]], ok=essais["ok"])


def _ecrire_sp(R, ctx, Q, etape):
    """E6 : phrase de choix, « On cherche deux nombres… », le tableau (✓ par le bloc, D29), puis (x + p)(x + q) dans l'ordre de la
    ligne ✓ ; échec (D3) : le tableau complet, puis la formule ; plus de 12 lignes (§ 13.5) : pas de tableau."""
    c, b, _ = (int(v) for v in Q)
    r = etape["resultat"]
    essais = r["essais"]
    R.etape("factoriser", "SP", _t(ctx.poly(Q)), dict(r, aboutit=etape["aboutit"]))
    if ctx.cours:
        R.texte(_choix(ctx, Q, True, "SP"))
    if essais["trop"]:
        R.texte(PHRASE_SP_TROP)
        return
    R.texte(rf"On cherche deux nombres dont le produit vaut \({exact(c)}\) et la somme vaut \({exact(b)}\) :")
    R.texte(_tableau_sp(b, c, essais))
    if not etape["aboutit"]:
        R.texte(PHRASE_SP_ECHEC)
        return
    p, q, s = essais["lignes"][essais["ok"]]
    if (p * q, p + q) != (c, b) or (Nombre(p), Nombre(1)) != r["facteurs"][0] or (Nombre(q), Nombre(1)) != r["facteurs"][1]:
        raise _Incoherent("ligne ✓ et facteurs du S-P")
    R.equiv(ctx.produit([(ctx.facteur(f), 1) for f in r["facteurs"]]))


def _tex_calcul_tatonnement(a, b, c, r):
    """« 2 · (−4)² − 4 − 28 = 32 − 4 − 28 » (E7 : b · r écrit directement quand b = ±1)."""
    termes, valeurs = [rf"{exact(a)} \cdot {_par(r)}^{{2}}"], [exact(a * r * r)]
    if b:
        termes.append(_signe_tex(b * r) if abs(b) == 1 else (" - " if b < 0 else " + ") + rf"{exact(abs(b))} \cdot {_par(r)}")
        valeurs.append(_signe_tex(b * r))
    termes.append(_signe_tex(c))
    valeurs.append(_signe_tex(c))
    if a * r * r + b * r + c != 0:
        raise _Incoherent("la racine du tâtonnement n'annule pas le trinôme")
    return "".join(termes) + " = " + "".join(valeurs) + " = 0"


def _ecrire_tatonnement(R, ctx, Q, etape):
    """E7 : r et △ encadrés (D29) ; en échec (D1), une seule ligne avec les diviseurs testés, puis la formule."""
    c, b, a = (int(v) for v in Q)
    r = etape["resultat"]
    R.etape("factoriser", "TATONNEMENT", _t(ctx.poly(Q)), dict(r, aboutit=etape["aboutit"]))
    if ctx.cours:
        R.texte(_choix(ctx, Q, False, "TATONNEMENT"))
    X, P_tex = ctx.X, _t(ctx.poly(Q))
    if not etape["aboutit"]:
        positifs = [d for d in r["diviseurs"] if d > 0]
        R.texte(rf"On teste les diviseurs de \({exact(c)}\) (" + ", ".join(rf"\(\pm {exact(d)}\)" for d in positifs)
                + ") : aucun n'est solution. On utilise la formule.")
        return
    racine, triangle = r["r"], r["triangle"]
    if -racine * triangle != c:
        raise _Incoherent("△ du tâtonnement")
    de = rf" de \({P_tex} = 0\)" if ctx.apres_me else ""
    R.texte(rf"\(\fbox{{${_t(X)} = {exact(racine)}$}}\) est solution{de}, car \({_tex_calcul_tatonnement(a, b, c, racine)}\).")
    R.texte(rf"Donc \({P_tex} = ({_t(ctx.facteur(r['facteurs'][0]))})({_t(Op('*', Nb(a), X))} + \triangle)\) avec "
            rf"\({exact(-racine)} \cdot \triangle = {exact(c)}\), donc \(\fbox{{$\triangle = {exact(triangle)}$}}\).")
    R.equiv(ctx.produit([(ctx.facteur(f), 1) for f in r["facteurs"]]))


def _delta_tex(f, dec):
    a, b, c, delta = f["a"], f["b"], f["c"], f["delta"]
    def facteur(v):                                    # 4 · 1 · (−1), 4 · (−1) · 3, 4 · \frac{3}{2} · (−1) : jamais « 4(−1) »
        t = _t(nb_exact(v, dec))
        return entre_parentheses(t) if v < 0 else t
    subst = _t(Pow(nb_exact(b, dec), Nb(2))) + r" - 4 \cdot " + facteur(a) + r" \cdot " + facteur(c)
    s = r"\Delta = b^{2} - 4ac = " + subst
    m = -4 * a * c
    if b != 0 and m != 0:
        s += " = " + exact(b * b, dec) + (" + " + exact(m, dec) if m > 0 else " - " + exact(-m, dec))
    return s + r" = \fbox{$" + exact(delta, dec) + "$}"


def _racine_tex(rd, dec):
    return _t(arbre_nombre(rd, dec))


def _ecrire_formule(R, ctx, Q, f, sur_facteur):
    """E10 (§ 7) : Δ en une ligne, valeur finale encadrée (D29, point 2) ; Δ > 0 : √Δ simplifié, x₁ (avec −√Δ) et x₂ nommés
    (`Defini`), fraction réduite dans la même ligne (E11) ; Δ = 0 : x = −b/(2a) ; Δ < 0 : aucune solution (sur un facteur :
    « … = 0 n'a aucune solution réelle », E9)."""
    dec, X, Q_tex = ctx.dec, ctx.X, _t(ctx.poly(Q))
    a, b, delta = f["a"], f["b"], f["delta"]
    if b * b - 4 * a * f["c"] != delta:
        raise _Incoherent("Δ")
    R.etape("delta_valeur", "FORMULE", Q_tex, f)
    R.rangee(_delta_tex(f, dec))
    R.etape("delta_nombre", "FORMULE", Q_tex, f)
    if delta < 0:
        R.texte(rf"\(\Delta < 0\) : \({Q_tex} = 0\) n'a aucune solution réelle." if sur_facteur
                else r"\(\Delta < 0\) : l'équation n'a aucune solution réelle.")
        return
    deux_a = nb_exact(2 * a, dec)
    if delta == 0:
        R.texte(r"\(\Delta = 0\) : une seule solution.")
        quotient = Op("/", nb_exact(-b, dec), deux_a)
        eg = Eq(X, arbre_nombre(f["x"], dec), [Op("/", Neg(Var("b")), Op("*", Nb(2), Var("a")))]
                + ([quotient] if _t(quotient) != _t(arbre_nombre(f["x"], dec)) else []))
        R.rangee(_t_eq(eg))
        return
    rd = f["racine_delta"]
    ligne = r"\Delta > 0 \text{ : deux solutions.} \quad \sqrt{\Delta} = "
    if rd.rationnel:
        ligne += _racine_tex(rd, dec)
    else:
        sous = r"\sqrt{" + exact(delta, dec) + "}"
        ligne += sous + ("" if sous == _racine_tex(rd, dec) else " = " + _racine_tex(rd, dec))
    R.rangee(ligne)
    rd_arbre = arbre_nombre(rd, dec)
    D = Defini(r"\Delta", nb_exact(delta, dec))
    for nom, signe, valeur in (("x_{1}", "-", f["x1"]), ("x_{2}", "+", f["x2"])):
        if (-b + (-rd if signe == "-" else rd)) / (2 * a) != valeur:
            raise _Incoherent(nom)
        generale = Op("/", Op(signe, Neg(Var("b")), Fn("sqrt", D)), Op("*", Nb(2), Var("a")))
        num = (Neg(rd_arbre) if signe == "-" else rd_arbre) if b == 0 else Op(signe, nb_exact(-b, dec), rd_arbre)
        subst, final = Op("/", num, deux_a), arbre_nombre(valeur, dec)
        R.rangee(_t_eq(Eq(Defini(nom, final), final, [generale] + ([subst] if _t(subst) != _t(final) else []))))


def _t_eq(e):
    return _t(e.g) + "".join(" = " + _t(m) for m in e.milieu) + " = " + _t(e.d)


def _une_ou_plusieurs(eqs):
    return eqs[0] if len(eqs) == 1 else Ou(eqs)


def _ecrire_produit_nul(R, ctx, P, pn, formules):
    """E8 (D7, D14, D20, D24) et E9 : la ligne du produit nul (étiquette « produit nul »), un facteur répété une seule fois ; le
    facteur constant « impossible » ; le monôme 3x = 0 puis x = 0 ; kx = … quand le coefficient de x n'est pas ±1 et que la
    constante n'est pas entière ; un trinôme par la formule (Δ, puis les solutions)."""
    X, dec = ctx.X, ctx.dec
    seul = len(pn["facteurs"]) == 1 and en_nombres(pn["facteurs"][0][0]) == en_nombres(P)
    R.etape("produit_nul", "PRODUIT_NUL", _t(R.pivot.g) if isinstance(R.pivot, Eq) else _t(ctx.poly(P)),
            {"facteurs": [f for f, _, _ in pn["facteurs"]], "solutions": pn["solutions"]})
    nuls, milieu, finals, trinomes = [], [], [], []
    besoin_milieu = False
    for f, genre, sols in pn["facteurs"]:
        if genre == "constante":
            nuls.append(Eq(Nb(f[0].p), Nb(0)))
            continue
        if genre == "monome":
            j = len(f) - 1
            nuls.append(Eq(ctx.monome(f[j].p, j), Nb(0)))
            milieu.append(Eq(X, Nb(0)))
            finals.append(Eq(X, Nb(0)))
        elif genre == "lineaire":
            c0, c1 = f
            nuls.append(Eq(ctx.facteur(f), Nb(0)))
            sol = arbre_nombre(sols[0], dec)
            if c1.p not in (1, -1) and not (c0.rationnel and c0.p.denominator == 1):
                besoin_milieu = True
                milieu.append(Eq(ctx.monome(c1.p, 1), arbre_nombre(-c0, dec)))
            else:
                milieu.append(Eq(X, sol))
            finals.append(Eq(X, sol))
        else:
            Q = rationnel(f)
            nuls.append(Eq(ctx.poly(Q), Nb(0)))
            trinomes.append(Q)
            fo = formules[Q]
            finals += [Eq(X, arbre_nombre(v, dec)) for v in ((fo["x1"], fo["x2"]) if fo["delta"] > 0 else
                                                            (fo["x"],) if fo["delta"] == 0 else ())]
    if not seul:
        R.equiv(_une_ou_plusieurs(nuls), "produit nul")
    if trinomes:
        if len(trinomes) > 1 or besoin_milieu:
            raise _Incoherent("plusieurs trinômes ou kx = … avec la formule (P4b)")
        _ecrire_formule(R, ctx, trinomes[0], formules[trinomes[0]], sur_facteur=True)
    elif besoin_milieu:
        R.equiv(_une_ou_plusieurs(milieu))
    if finals:
        dernier = _une_ou_plusieurs(finals)
        if _t_element(dernier) != _t_element(R.pivot):
            R.equiv(dernier)


def _t_element(e):
    if isinstance(e, Ou):
        return " ou ".join(_t_element(q) for q in e.eqs)
    return _t_eq(e) if isinstance(e, Eq) else _t(e)


# ---------- S et la ligne « soit … ≈ … » (E11, E14) ----------
def _tex_S(solutions, dec, ensemble="fini"):
    if ensemble == "reels":
        return r"S = \mathbb{R}"
    if not solutions:
        return r"S = \varnothing"
    return r"S = \{" + r"\,;\,".join(_t(arbre_nombre(x, dec)) for x in solutions) + r"\}"


def _tex_approx(solutions, noms, x, dec):
    """« soit x₁ ≈ −4,236 et x₂ ≈ 0,236 » (solutions nommées par la formule), « soit x ≈ −1,414 ou x = 0 ou x ≈ 1,414 » ; None
    si toutes les solutions sont rationnelles (≈ seulement pour les irrationnelles, une fois, après S)."""
    if all(s.rationnel for s in solutions):
        return None
    nommees = all(s in noms for s in solutions)
    morceaux = []
    for s in solutions:
        nom = noms[s] if nommees else nom_tex(x)
        valeur = (r" \approx " + approx_garantie(s)) if not s.rationnel else " = " + _t(arbre_nombre(s, dec))
        morceaux.append(r"\(" + nom + valeur + r"\)")
    return "soit " + (" et " if nommees else " ou ").join(morceaux)


def _non_resolu(statut):
    return {"statut": statut, "etapes": [], "solutions": [], "S": None, "approx": None, "variantes": [], "message": MESSAGES[statut]}


def _formule_utilisee(ch):
    return any(e["methode"] == "FORMULE" for e in ch["etapes"])


def resoudre_equation(gauche, droite, inconnue, decimaux_enonce=False, methodes=ORDRE_DU_COURS):
    """La résolution rédigée de « gauche = droite » (arbres de moteur/expr.py) en l'inconnue (§ 5) :

    {statut: "resolu" | "non_traite" | "hors_cours" | "ne_conclut_pas" | "hors_bornes",
     etapes: [Etape], solutions: [Nombre] croissantes, S: TeX, approx: texte « soit … ≈ … » (TeX entre \\( et \\)) ou None,
     variantes: ["formule"] (E12 : le chemin du cours n'utilise pas la formule) ou [], message: texte pour un statut non résolu}
    Etape = {phase, methode, cible (TeX), parametres (calcul exact), lignes (rangées : triplets (lien, expr, prop) et `LigneTexte`),
             segment (la `Chaine` de l'étape, pivot puis ⇔, ou None)}.

    P2b : seulement « P = 0 » développée et ordonnée (`termes_developpes`), de degré 2 ; tout le reste est « non_traite » (ramener et
    développer : P3 ; formes structurées : P4a ; degrés ≠ 2, identité : P4b). Le calcul est celui de `chemin` (garde-fou exact) ;
    une valeur écrite qui ne vérifie pas son calcul donne « ne_conclut_pas ». methodes=ORDRE_PAR_LA_FORMULE : la variante E12."""
    if termes_developpes(gauche, inconnue) is None or not _est_zero(droite) or variables(gauche) - {inconnue}:
        return _non_resolu("non_traite")
    try:
        P = vers_polynome(gauche, inconnue)
        if P.degre != 2:
            return _non_resolu("non_traite")
        ch = chemin(P, methodes)
        if ch["statut"] != "resolu":
            return _non_resolu(ch["statut"])
        res = _rediger(Eq(gauche, droite), P, ch, inconnue, decimaux_enonce, cours=methodes != ORDRE_PAR_LA_FORMULE)
        if methodes == ORDRE_DU_COURS and not _formule_utilisee(ch):
            v = chemin(P, ORDRE_PAR_LA_FORMULE)
            res["variantes"] = ["formule"] if v["statut"] == "resolu" and _formule_utilisee(v) else []
        return res
    except HorsBornes:
        return _non_resolu("hors_bornes")
    except (_Incoherent, ValueError, TypeError, ZeroDivisionError):      # valeur non garantie, écriture qui ne vérifie pas son calcul
        return _non_resolu("ne_conclut_pas")


def _rediger(enonce, P, ch, inconnue, dec, cours):
    R, ctx = _Redaction(enonce), _Contexte(inconnue, dec, cours)
    formules = {e["cible"]: e["resultat"] for e in ch["etapes"] if e["methode"] == "FORMULE"}
    etapes = ch["etapes"]
    for i, e in enumerate(etapes):
        m, Q, r = e["methode"], e["cible"], e["resultat"]
        if m == "ME":
            _ecrire_me(R, ctx, Q, r)
        elif m in IDREM:
            _ecrire_idrem(R, ctx, Q, r)
        elif m == "SP":
            _ecrire_sp(R, ctx, Q, e)
        elif m == "TATONNEMENT":
            _ecrire_tatonnement(R, ctx, Q, e)
        elif m == "FORMULE":
            if i == 0 or etapes[i - 1]["methode"] not in ("SP", "TATONNEMENT"):      # formule choisie d'emblée (D22, ou E12)
                R.etape("factoriser", "FORMULE", _t(ctx.poly(Q)), r)
                if cours:
                    if Q.entiers() or ctx.apres_me:
                        raise _Incoherent("formule d'emblée sur un trinôme à coefficients entiers")
                    R.texte(_choix(ctx, Q, False, "FORMULE"))
        else:
            raise _Incoherent(f"méthode {m} hors de P2b")
    pn = ch["produit_nul"]
    formule_seule = len(pn["facteurs"]) == 1 and pn["facteurs"][0][1] == "formule"
    if formule_seule:
        Q = rationnel(pn["facteurs"][0][0])
        _ecrire_formule(R, ctx, Q, formules[Q], sur_facteur=False)
    else:
        _ecrire_produit_nul(R, ctx, P, pn, formules)
    R.fermer()
    noms = {}
    for f in formules.values():
        if f["delta"] > 0:
            noms[f["x1"]], noms[f["x2"]] = "x_{1}", "x_{2}"
    sols = pn["solutions"]
    return {"statut": "resolu", "etapes": R.etapes, "solutions": sols, "S": _tex_S(sols, dec),
            "approx": _tex_approx(sols, noms, inconnue, dec), "variantes": [], "message": None}


def appliquer(methode, P, inconnue="x", decimaux_enonce=False):
    """Une méthode seule sur « P = 0 » (§ 5 ; pour le futur onglet « S'entraîner ») : l'Etape rédigée (phase « factoriser »,
    lignes de la méthode, sans phrase de choix, l'équation P = 0 en tête), ou None si la méthode n'aboutit pas (`s_applique`). La
    formule donne toutes ses lignes (Δ, puis les solutions) dans une seule étape ; le S-P de plus de 12 lignes, la phrase du § 13.5."""
    P = Polynome(P)
    r = calculer(methode, P)
    if r is None:
        return None
    R, ctx = _Redaction(Eq(arbre_polynome(P, inconnue, decimaux_enonce), Nb(0))), _Contexte(inconnue, decimaux_enonce, cours=False)
    if methode in ("ME", "ME_PUISSANCE"):
        _ecrire_me(R, ctx, P, r)
        R.etapes[-1]["methode"] = methode
    elif methode == "IDREM" or methode in IDREM:
        _ecrire_idrem(R, ctx, P, r)
    elif methode == "SP":
        e = essais_sp(P[1], P[0])
        _ecrire_sp(R, ctx, P, {"resultat": dict(r, essais=e), "aboutit": not e["trop"]})
    elif methode == "TATONNEMENT":
        _ecrire_tatonnement(R, ctx, P, {"resultat": r, "aboutit": True})
    else:
        _ecrire_formule(R, ctx, P, r, sur_facteur=False)
        R.fermer()
        lignes = [l for e in R.etapes for l in e["lignes"]]
        return {"phase": "factoriser", "methode": "FORMULE", "cible": _t(ctx.poly(P)), "parametres": r, "lignes": lignes,
                "segment": None}
    R.fermer()
    return R.etapes[0]


def blocs(resolution):
    """Les blocs de moteur/sortie.py d'une résolution résolue (A4) : la chaîne (`bloc_rangees` de la concaténation des lignes de
    toutes les étapes, membre de gauche dans sa colonne), S encadré (`resultat_lim`, D29, dans une carte normale), puis la ligne
    « soit … ≈ … » (E14). La page est construite uniquement à partir des étapes (§ 5)."""
    if resolution["statut"] != "resolu":
        raise ValueError(f"résolution non résolue : {resolution['statut']}")
    lignes = [r for e in resolution["etapes"] for r in e["lignes"]]
    b = [bloc_rangees(lignes, membre_gauche=True), sortie.resultat_lim(resolution["S"])]
    if resolution["approx"]:
        b.append(sortie.texte(resolution["approx"]))
    return b
