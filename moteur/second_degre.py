"""
second_degre.py — Brique commune : équations polynomiales du 2e degré (et ce qui s'y ramène), en Python pur, sans SymPy.

Chantier equations-2e-degre (docs/chantiers/equations-2e-degre/decisions.md, § 13 en tête). **P1 : le calcul** (sections 1 à 6),
**P2b : la rédaction** (section 7 : `resoudre_equation`, `appliquer`, étapes structurées du § 5), **P3 : ramener et développer**
(E1, E2 : `ramener` ; la lecture de la saisie est dans equations-2e-degre/equations.py), **P4a : les formes structurées**
(E1.3, E3, E5, E13 : produit déjà nul, facteur commun aux deux membres, Id. rem. sur la forme structurée, sans développer), **P4b :
les degrés ≠ 2** (E13 : degré ≥ 3 par le chemin du cours, le produit écrit suivi facteur par facteur ; degré 1 : isoler ; identité et
égalité fausse ; messages « bicarrée » et « hors du cours »). Tout est exact :
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
    ramener(g, d, x, dec)             E1, E2 : « g = d » ramenée à « P = 0 », lignes de développement et de réduction (P3) ;
                                      forme_structuree(g, d, x) : une structure s'applique sans développer (E1.3) ; P4a
                                      l'écrit (ecrire_enonce : l'énoncé, ses produits côte à côte comme le corrigé)
    resoudre_equation(g, d, x, …)     la résolution rédigée (§ 5) : {statut, etapes, solutions, S, approx, variantes, message}
    bicarree(P)                       ax⁴ + bx² + c sans ME ni Id. rem. : le message « bicarrée » (statut « pas_encore », § 4)
    hors_du_cours(P, chemin)          « hors du cours » seulement s'il est vrai (P5) ; sinon « forme_non_traitee »
    appliquer(methode, P)             une méthode seule, rédigée (Etape), ou None si elle n'aboutit pas
    blocs(resolution)                 les blocs de moteur/sortie.py : la chaîne (bloc_rangees, membre de gauche), S encadré, la ligne ≈
    cartes(resolution)                la page, une carte par étape (R1) : la chaîne coupée aux étapes, pivot en membre de gauche ;
                                      blocs_solution(resolution) : S encadré, la ligne ≈
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
from chaine import Chaine, Eq, LigneTexte, Ou, bloc_rangees, rangees_chaine, texte_message
from expr import Defini, Fn, Nb, Neg, Noeud, Op, Pow, Var, comme_somme, entre_parentheses, nom_tex, tex, variables
from noyau import racine_q, squarefree
from nombres import approx, exact

__all__ = ["Polynome", "Nombre", "HorsBornes", "vers_polynome", "mise_en_evidence", "identite", "essais_sp", "diviseurs_signes",
           "racine_entiere_unique", "racines_formule", "s_applique", "calculer", "chemin", "produit_nul", "redevelopper",
           "verifier_solution", "approx_garantie", "ORDRE_DU_COURS", "ORDRE_PAR_LA_FORMULE", "METHODES",
           "resoudre_equation", "appliquer", "blocs", "cartes", "blocs_solution", "nb_exact", "arbre_polynome", "arbre_nombre", "termes_developpes", "Produit",
           "SansLien", "rangees", "OPTIONS_CHAINE", "MESSAGES", "PHRASE_IDENTITE", "PHRASE_EGALITE_FAUSSE", "ramener",
           "forme_structuree", "PHRASE_RAMENER", "ecrire_enonce", "Groupe", "Crochet", "Juxtaposition", "bicarree", "hors_du_cours"]

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
    "pas_encore": "Cette équation se ramène au 2e degré par un changement de variable : ce sera traité dans une prochaine version.",
    "forme_non_traitee": "Cette forme d'équation n'est pas traitée par l'outil.",      # P5 (question 29) : vrai, là où « hors du cours » ne l'est pas
})
PHRASE_IDENTITE = "Cette égalité est vraie pour tout nombre réel."                  # celle d'Exp-log (§ 13.4), P4b
PHRASE_EGALITE_FAUSSE = "Cette égalité est fausse : l'équation n'a aucune solution."    # celle d'Exp-log, P4b
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
    (« 0 » seul : le polynôme nul) ; None sinon (à ramener, à développer ou à réordonner : `ramener`)."""
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
        self._courante, self._en_tete = None, None

    def etape(self, phase, methode, cible, parametres):
        self.fermer()
        self._courante = {"phase": phase, "methode": methode, "cible": cible, "parametres": parametres, "lignes": [],
                          "segment": None}
        self._attente, self._segment = [], None
        self.etapes.append(self._courante)
        if self._en_tete is not None:                   # une ligne seulement réordonnée appartient à l'étape qui suit (§ 5, E1)
            element, self._en_tete = self._en_tete, None
            self.equiv(element)

    def en_tete(self, element):
        """La première ligne ⇔ de l'étape suivante (E1 : « 5 + x² − 6x = 0 ⇔ x² − 6x + 5 = 0 », sans étiquette)."""
        self._en_tete = element

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
    phrases de choix (chemin du cours) et le pivot ; `ecrits` : les facteurs écrits comme dans la saisie (formes structurées, P4a :
    {facteur (tuple de Nombre) : arbre écrit}), sinon None (écrits développés)."""

    def __init__(self, inconnue, decimaux_enonce, cours=True):
        self.x, self.X, self.dec, self.cours = inconnue, Var(inconnue), decimaux_enonce, cours
        self.k, self.j, self.apres_me = F(1), 0, False
        self.ecrits = None
        self.courants, self.P = None, None

    def suivre(self, P, k=1, j=0, facteurs=None):
        """P4b : suit le produit écrit (préfixe k·xʲ, facteurs [(tuple de Nombre, exposant)] ; par défaut P seul) pour que chaque
        factorisation d'un facteur le remplace sur place (degré ≥ 3, facteurs de degré 2 d'un produit écrit) ; P : le polynôme de
        l'équation (garde-fou de chaque ligne)."""
        self.k, self.j, self.P = F(k), j, en_nombres(P)
        self.courants = [(en_nombres(f), e) for f, e in facteurs] if facteurs is not None else [(en_nombres(P), 1)]

    def produit(self, facteurs):
        """L'équation « k·xʲ · facteurs = 0 »."""
        return Eq(Produit(self.k, self.j, self.x, facteurs), Nb(0))

    def remplacer(self, Q, nouveaux):
        """L'équation du produit écrit dont le facteur Q (chaque occurrence d'exposant 1) est remplacé par `nouveaux`
        [(tuple de Nombre, exposant)] ; sans suivi (appliquer), les seuls `nouveaux`. Garde-fou : le produit écrit se redéveloppe
        en ±P."""
        if self.courants is None:
            return self.produit([(self.facteur(f), e) for f, e in nouveaux])
        Qn, out = en_nombres(Q), []
        for f, e in self.courants:
            out += [(en_nombres(g), h) for g, h in nouveaux] if (f, e) == (Qn, 1) else [(f, e)]
        if out == self.courants:
            raise _Incoherent("facteur introuvable dans le produit écrit")
        self.courants = out
        return self.produit_courant()

    def deplier(self, f):
        """D24 : le carré (f)² du produit écrit réécrit (f)(f)."""
        fn = en_nombres(f)
        out = []
        for g, e in self.courants:
            out += [(g, 1), (g, 1)] if (g, e) == (fn, 2) else [(g, e)]
        self.courants = out
        return self.produit_courant()

    def produit_courant(self):
        """L'équation du produit écrit, relue dans Q(√m) (garde-fou : l'arbre écrit vaut ±P)."""
        eq = self.produit([(self.facteur(f), e) for f, e in self.courants])
        r = _ecrit_en_nombres(eq.g, self.x)
        if r != self.P and r != en_nombres([-c for c in self.P]):
            raise _Incoherent("produit écrit")
        return eq

    def poly(self, Q):
        return arbre_polynome(Q, self.x, self.dec)

    def facteur(self, f):
        ecrit = self.ecrits.get(en_nombres(f)) if self.ecrits else None
        return ecrit if ecrit is not None else _arbre_facteur(f, self.X, self.dec)

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
        if Q.degre != 2:                                                # P4b : pas de « trinôme » ni de a en degré ≠ 2
            R.texte(rf"Le coefficient de \({_t(_puissance(ctx.X, Q.degre))}\) est négatif : on met d'abord \({_t(facteur)}\) en "
                    r"évidence.")
        elif a == -1:
            R.texte(rf"Le trinôme n'est pas unitaire (\(a = -1\)) : on met d'abord \({_t(facteur)}\) en évidence.")
        else:
            R.texte(rf"Le coefficient de \({_t(_puissance(ctx.X, Q.degre))}\) est négatif (\(a = {exact(a)}\)) : on met d'abord "
                    rf"\({_t(facteur)}\) en évidence.")
    ctx.k, ctx.j, ctx.apres_me = ctx.k * r["k"], ctx.j + r["j"], True
    if ctx.courants is None:
        R.equiv(ctx.produit([(ctx.poly(r["reste"]), 1)]), "ME")
    else:
        R.equiv(ctx.remplacer(Q, [(r["reste"], 1)]), "ME")


def _ecrire_idrem(R, ctx, Q, r):
    """E5 : A² − B² en étiquette ; A² ± 2AB + B² par une ligne de vérification, puis le carré et sa réécriture (D24). A et B
    encadrés ensemble, comme D29 l'écrit (« avec ⟦A = 4z, B = 9⟧ »)."""
    (k, j), B = r["A"], r["B"]
    A_tex, B_tex = _t(_monome_abs(k, j, ctx.X, ctx.dec)), _t(arbre_nombre(B, ctx.dec))
    R.etape("factoriser", r["methode"], _t(ctx.poly(Q)), {"A": (k, j), "B": B, "facteurs": r["facteurs"]})
    avec = rf"avec \(\fbox{{$A = {A_tex},\ B = {B_tex}$}}\)"
    g1, g2 = r["facteurs"]
    if r["methode"] == "IDREM_DIFF":
        R.equiv(ctx.remplacer(Q, [(g1, 1), (g2, 1)]), rf"Id. rem. \(A^{{2}} - B^{{2}}\) {avec}")
        ctx.apres_me = True                                             # P4b : un facteur se factorise ensuite (x⁴ − 16)
        return
    deux_ab = _t(_monome_abs(2 * k * B.p, j, ctx.X, ctx.dec))
    signe = "+" if r["methode"] == "IDREM_PLUS" else "-"
    R.texte(rf"Id. rem. \(A^{{2}} {signe} 2AB + B^{{2}}\) {avec}. Vérification : \(2AB = 2 \cdot {A_tex} \cdot {B_tex} = {deux_ab}\) "
            r"\(\checkmark\)")
    R.equiv(ctx.remplacer(Q, [(g1, 2)]))
    if ctx.courants is None:
        R.equiv(ctx.produit([(ctx.facteur(g1), 1), (ctx.facteur(g1), 1)]))
    else:
        R.equiv(ctx.deplier(g1))
    ctx.apres_me = True


def _choix(ctx, Q, unitaire, methode):
    """E4 (D19) : la phrase de choix, avant le S-P, le tâtonnement ou la formule (seulement sur le chemin du cours)."""
    if methode == "FORMULE":
        if ctx.apres_me:                                                # P4b : un facteur d'une Id. rem. (x⁴ − 1/4)
            return rf"Les coefficients du trinôme \({_t(ctx.poly(Q))}\) ne sont pas entiers : on utilise la formule."
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
    R.equiv(ctx.remplacer(Q, [(f, 1) for f in r["facteurs"]]))


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
    R.equiv(ctx.remplacer(Q, [(f, 1) for f in r["facteurs"]]))


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


def _ecrire_produit_nul(R, ctx, P, pn, formules, reecriture=None):
    """E8 (D7, D14, D20, D24) et E9 : la ligne du produit nul (étiquette « produit nul »), un facteur répété une seule fois ; le
    facteur constant « impossible » ; le monôme 3x = 0 puis x = 0 ; kx = … quand le coefficient de x n'est pas ±1 et que la
    constante n'est pas entière ; un trinôme par la formule (Δ, puis les solutions). `reecriture` : la ligne D24 d'un produit écrit
    avec un carré, (x + 1)² = 0 ⇔ (x + 1)(x + 1) = 0 (P4a), en tête de l'étape."""
    X, dec = ctx.X, ctx.dec
    seul = len(pn["facteurs"]) == 1 and en_nombres(pn["facteurs"][0][0]) == en_nombres(P)
    R.etape("produit_nul", "PRODUIT_NUL", _t(R.pivot.g) if isinstance(R.pivot, Eq) else _t(ctx.poly(P)),
            {"facteurs": [f for f, _, _ in pn["facteurs"]], "solutions": pn["solutions"]})
    if reecriture is not None:
        R.equiv(reecriture)
    nuls, milieu, finals, trinomes = [], [], [], []
    besoin_milieu = False
    for f, genre, sols in pn["facteurs"]:
        if genre == "constante":
            nuls.append(Eq(nb_exact(f[0].p, dec), Nb(0)))                # un entier : Nb(k) ; 0,5 de la saisie gardé (P4a)
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
            fo = formules.get(Q) or racines_formule(Q)
            trinomes.append((Q, fo))
            eqs = [Eq(X, arbre_nombre(v, dec)) for v in ((fo["x1"], fo["x2"]) if fo["delta"] > 0 else
                                                        (fo["x"],) if fo["delta"] == 0 else ())]
            milieu += eqs
            finals += eqs
    if not seul:
        R.equiv(_une_ou_plusieurs(nuls), "produit nul")
    for Q, fo in trinomes:                                              # E9 ; P4b : plusieurs trinômes, dans l'ordre du produit
        _ecrire_formule(R, ctx, Q, fo, sur_facteur=True)
    if besoin_milieu and milieu:
        R.equiv(_une_ou_plusieurs(milieu))
    finals = list({_t_eq(e): e for e in finals}.values())             # x = −1 une seule fois (facteurs proportionnels, P4a)
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


# ---------- E1 et E2 : ramener à « … = 0 » et développer (P3) ----------
PHRASE_RAMENER = r"On ramène d'abord l'équation à la forme \(\ldots = 0\) :"       # E1 : seulement si une phrase de choix suit


class _Groupe:
    """Une parenthèse précédée de « − » dans un membre écrit : ses termes signés (une parenthèse précédée de « + » se lit comme ses
    termes)."""
    __slots__ = ("termes",)

    def __init__(self, termes):
        self.termes = termes


def _sans_neg(n, s=1):
    while isinstance(n, Neg):
        n, s = n.a, -s
    return n, s


def _termes_signes(n, s=1):
    """Les termes d'un membre écrit avec leur signe : [(±1, terme)], terme sans « − » devant ; une somme précédée de « − » est un
    `_Groupe`."""
    n, s = _sans_neg(n, s)
    if isinstance(n, Op) and n.op in "+-":
        if s < 0:
            return [(-1, _Groupe(_termes_signes(n)))]
        return _termes_signes(n.a) + _termes_signes(n.b, -1 if n.op == "-" else 1)
    return [(s, n)]


def _monomes_signes(n, x):
    """[(j, k)] (k avec son signe) d'une somme de monômes écrits, ou None."""
    out = []
    for s, t in _termes_signes(n):
        m = None if isinstance(t, _Groupe) else _monome_ecrit(t, x)
        if m is None:
            return None
        out.append((m[0], s * m[1]))
    return out


def _facteurs_du_produit(n):
    if isinstance(n, Op) and n.op == "*":
        return _facteurs_du_produit(n.a) + _facteurs_du_produit(n.b)
    return [n]


def _developper(t, x):
    """E2 : (étiquette, [(j, k)] dans l'ordre écrit des produits) pour un terme à développer, ou None (hors de ce que P3 développe) :
    nombre ou monôme × parenthèse (« distribution ») ; deux parenthèses sans autre facteur (« double distribution », tous les
    produits partiels) ; carré d'un binôme A ± B, A sans signe (Id. rem., développé en A² ± 2AB + B²)."""
    if isinstance(t, Pow) and isinstance(t.b, Nb) and t.b.val == 2:
        termes = _termes_signes(t.a)
        if len(termes) != 2 or termes[0][0] < 0 or any(isinstance(u, _Groupe) for _, u in termes):
            return None
        (_, A), (sb, B) = termes
        ma, mb = _monome_ecrit(A, x), _monome_ecrit(B, x)
        if ma is None or mb is None or ma[0] == mb[0] or 0 in (ma[1], mb[1]):
            return None
        (ja, ka), (jb, kb) = ma, mb
        signe = "+" if sb > 0 else "-"
        return (rf"Id. rem. \((A {signe} B)^{{2}}\) avec \(A = {_t(A)},\ B = {_t(B)}\)",
                [(2 * ja, ka * ka), (ja + jb, 2 * sb * ka * kb), (2 * jb, kb * kb)])
    if not (isinstance(t, Op) and t.op == "*"):
        return None
    j0, k0, sommes = 0, F(1), []
    for f in _facteurs_du_produit(t):
        f, s = _sans_neg(f)
        k0 *= s
        m = _monome_ecrit(f, x)
        if m is not None:
            j0, k0 = j0 + m[0], k0 * m[1]
            continue
        termes = _monomes_signes(f, x) if isinstance(f, Op) and f.op in "+-" else None
        if termes is None:
            return None
        sommes.append(termes)
    if len(sommes) == 1:
        return "distribution", [(j0 + j, k0 * k) for j, k in sommes[0]]
    if len(sommes) == 2 and (j0, k0) == (0, 1):
        return "double distribution", [(j1 + j2, k1 * k2) for j1, k1 in sommes[0] for j2, k2 in sommes[1]]
    return None


def _lire_membre(n, x):
    """(entrées, étiquettes) d'un membre pour la ligne du développement (E2), ou None : entrées ("m", ±1, j, |k|) (monôme) ou
    ("g", −1, [entrées]) (parenthèse précédée de « − » : gardée, ou produit développé écrit entre parenthèses)."""
    entrees, etiquettes = [], []
    for s, t in _termes_signes(n):
        if isinstance(t, _Groupe):
            interieur = []
            for s2, u in t.termes:
                m = None if isinstance(u, _Groupe) else _monome_ecrit(u, x)
                if m is None:
                    return None
                interieur.append(("m", s2, m[0], m[1]))
            entrees.append(("g", -1, interieur))
            continue
        m = _monome_ecrit(t, x)
        if m is not None:
            entrees.append(("m", s, m[0], m[1]))
            continue
        d = _developper(t, x)
        if d is None:
            return None
        etiquettes.append(d[0])
        produits = [("m", -1 if k < 0 else 1, j, abs(k)) for j, k in d[1]]
        entrees += produits if s > 0 else [("g", -1, produits)]
    return entrees, etiquettes


def _sans_groupes(entrees, s=1):
    out = []
    for e in entrees:
        out += _sans_groupes(e[2], s * e[1]) if e[0] == "g" else [("m", s * e[1], e[2], e[3])]
    return out


def _ecrire_entrees(entrees, X, dec):
    termes = [(e[1], _ecrire_entrees(e[2], X, dec) if e[0] == "g" else _monome_abs(e[3], e[2], X, dec)) for e in entrees]
    return _somme(termes) if termes else Nb(0)


def _reduit(entrees):
    """Un membre sans parenthèse est réduit : degrés tous différents, aucun coefficient nul (sauf « 0 » seul)."""
    if entrees == [("m", 1, 0, 0)]:
        return True
    degres = [e[2] for e in entrees]
    return len(set(degres)) == len(degres) and all(e[3] != 0 for e in entrees)


def _est_produit(n, x):
    """Un produit ou une puissance non développés (un monôme écrit, 3x², n'en est pas un)."""
    n, _ = _sans_neg(n)
    return ((isinstance(n, Op) and n.op == "*") or isinstance(n, Pow)) and _monome_ecrit(n, x) is None


def _facteurs_non_monomes(n, x):
    n, _ = _sans_neg(n)
    if isinstance(n, Op) and n.op == "*":
        return _facteurs_non_monomes(n.a, x) + _facteurs_non_monomes(n.b, x)
    if isinstance(n, Pow) and isinstance(n.b, Nb) and n.b.val.denominator == 1 and n.b.val >= 1:
        return _facteurs_non_monomes(n.a, x)
    if not variables(n) or _monome_ecrit(n, x) is not None:
        return []
    return [n]


def _proportionnels(P, Q):
    return P.degre == Q.degre and all(P[-1] * q == Q[-1] * p for p, q in zip(P, Q))


def _carre_de_binome(t):
    """k pour un terme k·(B)² ou (B)² (B une somme écrite, k une constante), sinon None."""
    k = F(1)
    if isinstance(t, Op) and t.op == "*" and not variables(t.a):
        k, t = polynomes.const(t.a), t.b
    if k is None or not (isinstance(t, Pow) and isinstance(t.b, Nb) and t.b.val == 2):
        return None
    base, _ = _sans_neg(t.a)
    return k if isinstance(base, Op) and base.op in "+-" and variables(base) else None


def forme_structuree(gauche, droite, inconnue):
    """Vrai si une structure s'applique sans développer (E1.3) : produit ou puissance égal à 0 (produit nul direct, E13) ; facteur non
    monôme commun aux deux membres, à un facteur constant près (E3, 2.12 e) ; un carré de binôme k(B)² et des constantes de signe
    opposé ou nulles, ou deux carrés de signes opposés sans constante (Id. rem. sur une forme structurée, E5 : 2.9 k, l ; 2.12 h).
    P4a en écrit la résolution (`_rediger_structure`) ; une structure qu'il n'écrit pas (facteurs seulement proportionnels, √k
    irrationnel, cube…) donne « forme_non_traitee » : on ne la développe pas (P4b, P5 ; suivi.md)."""
    x = inconnue
    for a, b in ((gauche, droite), (droite, gauche)):
        if _est_zero(b) and _est_produit(a, x):
            return True
    if _est_produit(gauche, x) or _est_produit(droite, x):
        try:
            fg = [vers_polynome(f, x) for f in _facteurs_non_monomes(gauche, x)]
            fd = [vers_polynome(f, x) for f in _facteurs_non_monomes(droite, x)]
        except (HorsBornes, ValueError):
            fg = fd = []
        if any(_proportionnels(P, Q) for P in fg for Q in fd):
            return True
    constante, carres = F(0), []
    for s, t in _termes_signes(gauche) + [(-s, t) for s, t in _termes_signes(droite)]:
        if isinstance(t, _Groupe):
            return False
        if not variables(t):
            v = polynomes.const(t)
            if v is None:
                return False
            constante += s * v
            continue
        k = _carre_de_binome(t)
        if k is None or k == 0:
            return False
        carres.append(s * k)
    if len(carres) == 1:
        return constante == 0 or (constante > 0) != (carres[0] > 0)
    return len(carres) == 2 and constante == 0 and (carres[0] > 0) != (carres[1] > 0)


def _relire(eq, x):
    return vers_polynome(eq.g, x), vers_polynome(eq.d, x)


def ramener(gauche, droite, inconnue, decimaux_enonce=False):
    """E1 et E2 (P3) : l'équation « gauche = droite » ramenée à « P = 0 », ligne par ligne, sans texte :
    {P: Polynome, pas: [(méthode, parametres, [(Eq, étiquette ou None)])] (méthodes « DEVELOPPER », « RAMENER »), en_tete: Eq ou None
    (la ligne seulement réordonnée, qui appartient à l'étape suivante, § 5)} ; None si une structure de P4a s'applique
    (`forme_structuree` : écrite sans développer par `_rediger_structure`) ou si un terme sort de ce que E2 développe. Chaque ligne
    est relue par `vers_polynome` (garde-fou)."""
    x, X, dec = inconnue, Var(inconnue), decimaux_enonce
    Pg, Pd = vers_polynome(gauche, x), vers_polynome(droite, x)
    if termes_developpes(gauche, x) is not None and _est_zero(droite):            # E1.1 : déjà « P = 0 », développée et ordonnée
        return {"P": Pg, "pas": [], "en_tete": None}
    if forme_structuree(gauche, droite, x):
        return None
    lus = [_lire_membre(gauche, x), _lire_membre(droite, x)]
    if None in lus:
        return None
    (eg, lg), (ed, ld) = lus
    etiquettes = list(dict.fromkeys(lg + ld))                                   # E2 : « ; » entre les étiquettes, sans doublon
    lignes_dev, ligne_red = [], None
    if etiquettes:
        lignes_dev.append((Eq(_ecrire_entrees(eg, X, dec), _ecrire_entrees(ed, X, dec)), " ; ".join(etiquettes)))
    plats = [_sans_groupes(eg), _sans_groupes(ed)]
    if plats != [eg, ed]:
        lignes_dev.append((Eq(_ecrire_entrees(plats[0], X, dec), _ecrire_entrees(plats[1], X, dec)), None))
    if not all(_reduit(m) for m in plats):
        ligne_red = (Eq(arbre_polynome(Pg, x, dec), arbre_polynome(Pd, x, dec)), None)
    for eq, _ in lignes_dev + ([ligne_red] if ligne_red else []):
        if _relire(eq, x) != (Pg, Pd):
            raise _Incoherent("développement")
    D = Polynome([a - b for a, b in zip(list(Pg) + [0] * len(Pd), list(Pd) + [0] * len(Pg))])
    cote = "gauche"
    if D.degre <= 0:                                                            # P4b : identité, égalité fausse (Exp-log)
        final = Eq(nb_exact(Pg[0], dec), nb_exact(Pd[0], dec))                  # les constantes de chaque membre : 1 = 1, 1 = 2
        g_, d_ = _relire(final, x)
        if Polynome([g_[0] - d_[0]]) != D:
            raise _Incoherent("ramener")
    else:
        if not Pd.nul() and D[-1] < 0:                                          # E1.2 : coefficient de tête positif
            D, cote = Polynome([-c for c in D]), "droite"
        final = Eq(arbre_polynome(D, x, dec), Nb(0))
        if _relire(final, x) != (D, Polynome()):
            raise _Incoherent("ramener")
    derniere = (ligne_red or (lignes_dev[-1] if lignes_dev else None) or (Eq(gauche, droite), None))[0]
    a_ecrire = _t_element(final) != _t_element(derniere)
    pas, en_tete = [], None
    if lignes_dev:
        pas.append(("DEVELOPPER", {"developpements": etiquettes}, lignes_dev + ([ligne_red] if ligne_red else [])))
        ligne_red = None
    if a_ecrire and not Pd.nul():
        pas.append(("RAMENER", {"cote": cote, "polynome": D}, ([ligne_red] if ligne_red else []) + [(final, None)]))
    else:
        if ligne_red:
            pas.append(("RAMENER", {"cote": cote, "polynome": D}, [ligne_red]))
        if a_ecrire:
            en_tete = final                                                     # E1 : seulement réordonnée (second membre nul)
    return {"P": D, "pas": pas, "en_tete": en_tete}


def _ecrire_ramener(R, prep, phrase):
    """Les étapes « ramener » (E1, E2) ; la phrase d'E1 en tête de la première, si une phrase de choix suit (E4)."""
    for i, (methode, parametres, lignes) in enumerate(prep["pas"]):
        R.etape("ramener", methode, _t_element(R.pivot), parametres)
        if i == 0 and phrase:
            R.texte(PHRASE_RAMENER)
        for eq, prop in lignes:
            R.equiv(eq, prop)
    if prep["en_tete"] is not None:
        R.en_tete(prep["en_tete"])


# ---------- P4a : formes structurées, sur l'arbre avant tout développement (E1.3, E3, E5, E13) ----------
def _phrase_attention(f_tex):
    """E3 (2.12 e), mot pour mot."""
    return (rf"Attention : on ne divise pas par \({f_tex}\), car ce facteur peut être nul ! On ramène tout dans le membre de gauche, "
            rf"puis on met \({f_tex}\) en évidence.")


class Groupe(Noeud):
    """Une parenthèse du corrigé autour d'une somme, que expr.tex n'écrirait pas : ((x + 1) + 4), (4 + (3x + 2)), [(2 − x) − (x + 3)]."""
    __slots__ = ("a",)

    def __init__(self, a):
        self.a = a

    def ecrire_tex(self):
        return entre_parentheses(tex(self.a))


class Crochet(Noeud):
    """Le crochet de la ME d'un facteur commun (E3, 2.12 e) : (x − 1)[(2 − x) − (x + 3)]."""
    __slots__ = ("a",)

    def __init__(self, a):
        self.a = a

    def ecrire_tex(self):
        s = tex(self.a)
        return r"\left[" + s + r"\right]" if r"\frac" in s else "[" + s + "]"


class Juxtaposition(Noeud):
    """Un produit de la saisie écrit comme le corrigé, ses facteurs côte à côte : (x − 1)(2 − x)(5 − 3x), 2x(x − 3), \\frac{1}{4}(x + 1)²
    (expr.tex écrit « (x − 1)(2 − x) · (5 − 3x) ») ; « · » seulement devant un nombre (x · 3)."""
    __slots__ = ("facteurs",)

    def __init__(self, facteurs):
        self.facteurs = tuple(facteurs)

    def ecrire_tex(self):
        s = ""
        for f in self.facteurs:
            t = tex(f)
            if comme_somme(f):
                t = entre_parentheses(t)
            if s and (t[0].isdigit() or t.startswith(r"\frac")):
                s += r" \cdot "
            s += t
        return s


def _atomes(n):
    """Les facteurs d'un produit écrit (nombres positifs, fractions, lettres, puissances, sommes), ou None."""
    if isinstance(n, Op) and n.op == "*":
        a, b = _atomes(n.a), _atomes(n.b)
        return None if a is None or b is None else a + b
    if (isinstance(n, Nb) and n.val >= 0) or isinstance(n, (Var, Pow)) or (isinstance(n, Op) and n.op in "+-/"):
        return [n]
    return None


def _juxtaposer(n):
    """L'arbre écrit, ses produits (hors des puissances) en `Juxtaposition` : seulement l'écriture des formes structurées (P4a)."""
    if isinstance(n, Op) and n.op in "+-":
        return Op(n.op, _juxtaposer(n.a), _juxtaposer(n.b))
    if isinstance(n, Neg):
        return Neg(_juxtaposer(n.a))
    if isinstance(n, Op) and n.op == "*":
        a = _atomes(n)
        return Juxtaposition(a) if a else n
    return n


def ecrire_enonce(gauche, droite, inconnue):
    """L'énoncé écrit en tête de la chaîne : « gauche = droite » ; une forme structurée (P4a) a ses produits écrits comme le corrigé
    (`Juxtaposition`)."""
    if forme_structuree(gauche, droite, inconnue):
        return Eq(_juxtaposer(gauche), _juxtaposer(droite))
    return Eq(gauche, droite)


def _nadd(a, b, s=1):
    n = max(len(a), len(b))
    a, b = list(a) + [Nombre(0)] * (n - len(a)), list(b) + [Nombre(0)] * (n - len(b))
    return en_nombres([u + s * v for u, v in zip(a, b)])


def _ecrit_en_nombres(n, x):
    """Le polynôme (tuple de Nombre) d'un arbre écrit, dans Q(√m) : la relecture des lignes des formes structurées (garde-fou ;
    polynomes.pq ne lit ni √ ni les nœuds de l'outil). ValueError hors de Nb, l'inconnue, Neg, Op, Pow entier, √ d'une constante
    rationnelle positive, Groupe, Crochet, Juxtaposition, Produit."""
    if isinstance(n, (Groupe, Crochet)):
        return _ecrit_en_nombres(n.a, x)
    if isinstance(n, (Juxtaposition, Produit)):
        r = (Nombre(1),) if isinstance(n, Juxtaposition) else _monome_n(n.k, n.j)
        for a, e in (((f, 1) for f in n.facteurs) if isinstance(n, Juxtaposition) else n.facteurs):
            for _ in range(e):
                r = _pmul(r, _ecrit_en_nombres(a, x))
        return r
    if isinstance(n, Nb):
        return (Nombre(n.val),)
    if isinstance(n, Var) and n.nom == x:
        return (Nombre(0), Nombre(1))
    if isinstance(n, Neg):
        return en_nombres([-c for c in _ecrit_en_nombres(n.a, x)])
    if isinstance(n, Fn) and n.nom == "sqrt" and not variables(n.a):
        v = polynomes.const(n.a)
        if v is not None and v >= 0:
            return (Nombre.racine(v),)
    if isinstance(n, Op):
        a, b = _ecrit_en_nombres(n.a, x), _ecrit_en_nombres(n.b, x)
        if n.op in "+-":
            return _nadd(a, b, 1 if n.op == "+" else -1)
        if n.op == "*":
            return _pmul(a, b)
        if len(b) == 1 and b[0] != 0:
            return en_nombres([c / b[0] for c in a])
    if isinstance(n, Pow) and isinstance(n.b, Nb) and n.b.val.denominator == 1 and 0 <= n.b.val <= DEGRE_MAX:
        r = (Nombre(1),)
        for _ in range(int(n.b.val)):
            r = _pmul(r, _ecrit_en_nombres(n.a, x))
        return r
    raise ValueError(f"arbre non relu : {n!r}")


def _binome_ecrit(n, x):
    """Une somme écrite réduite de degré 1 (x + 1, 2 − x, 3x + 2, 0,5x − 1 : un terme en x et une constante, non nuls) : (Polynome,
    termes signés [(j, k)] dans l'ordre écrit) ; None sinon."""
    if not (isinstance(n, Op) and n.op in "+-"):
        return None
    t = _monomes_signes(n, x)
    if t is None or sorted(j for j, _ in t) != [0, 1] or any(k == 0 for _, k in t):
        return None
    c = dict(t)
    return Polynome([c[0], c[1]]), t


def _trinome_ecrit(n, x):
    """P4b : une somme écrite réduite de degré 2 (x² − 1, 4 − x², x² + x − 1 : monômes de degrés différents, non nuls, au moins
    deux) : (Polynome, termes signés) ; None sinon."""
    if not (isinstance(n, Op) and n.op in "+-"):
        return None
    t = _monomes_signes(n, x)
    if t is None or max(j for j, _ in t) != 2 or len({j for j, _ in t}) != len(t) or any(k == 0 for _, k in t):
        return None
    c = dict(t)
    return Polynome([c.get(0, 0), c.get(1, 0), c[2]]), t


def _produit_ecrit(n, x, trinomes=False):
    """Un produit écrit (E13) : (k, j, [(somme écrite, Polynome, exposant)]) pour k·xʲ·Π(Bᵢ)^eᵢ, les sommes dans l'ordre écrit —
    constantes, monômes, sommes réduites de degré 1 (`_binome_ecrit`) et leurs carrés (D24), et, si `trinomes` (P4b), des sommes
    réduites de degré 2 (`_trinome_ecrit`, exposant 1) ; None sinon (un cube… : non écrit)."""
    k, j, facteurs, pile = F(1), 0, [], [(n, 1)]
    while pile:
        m, s = _sans_neg(*pile.pop())
        if isinstance(m, Op) and m.op == "*":
            pile += [(m.b, 1), (m.a, s)]
            continue
        k *= s
        if not variables(m):
            v = polynomes.const(m)
            if v is None:
                return None
            k *= v
            continue
        mono = _monome_ecrit(m, x)
        if mono is not None:
            j, k = j + mono[0], k * mono[1]
            continue
        base, e = (m.a, 2) if isinstance(m, Pow) and isinstance(m.b, Nb) and m.b.val == 2 else (m, 1)
        b = _binome_ecrit(base, x)
        if b is None and trinomes and e == 1:
            b = _trinome_ecrit(base, x)
        if b is None:
            return None
        facteurs.append((base, b[0], e))
    return None if k == 0 else (k, j, facteurs)


def _membre_en_facteurs(n, x):
    """Un membre écrit en facteurs : un produit (`_produit_ecrit`), ou une somme réduite de degré 1 seule (au signe près)."""
    if _est_produit(n, x):
        return _produit_ecrit(n, x)
    m, s = _sans_neg(n)
    b = _binome_ecrit(m, x)
    return None if b is None else (F(s), 0, [(m, b[0], 1)])


def _poly_facteurs(k, j, facteurs):
    return redevelopper([_monome_n(k, j)] + [en_nombres(P) for _, P, e in facteurs for _ in range(e)])


def _sans_carres(n):
    """D24 dans l'arbre de la saisie : chaque carré d'une somme d'un produit écrit devient (B)(B), le reste tel quel (0,5 gardé)."""
    if isinstance(n, Neg):
        return Neg(_sans_carres(n.a))
    if isinstance(n, Op) and n.op == "*":
        return Op("*", _sans_carres(n.a), _sans_carres(n.b))
    if isinstance(n, Pow) and isinstance(n.b, Nb) and n.b.val == 2 and isinstance(n.a, Op) and n.a.op in "+-":
        return Op("*", n.a, n.a)
    return n


def _carre_ecrit(t, x):
    """Un terme k·(B)² ou (B)² (k constante non nulle, B somme réduite de degré 1) : (signe de k, |k|, B écrit, Polynome de B, termes
    de B) ; None sinon."""
    k = F(1)
    if isinstance(t, Op) and t.op == "*" and not variables(t.a):
        k, t = polynomes.const(t.a), t.b
    if not k or not (isinstance(t, Pow) and isinstance(t.b, Nb) and t.b.val == 2):
        return None
    b = _binome_ecrit(t.a, x)
    return None if b is None else (1 if k > 0 else -1, abs(k), t.a, b[0], b[1])


def _facteur_reduit(f, X, dec):
    """Un facteur réduit de degré 1 (tuple de Nombre) écrit comme le corrigé (E5) : le terme en x d'abord, sauf si son coefficient est
    négatif alors que la constante est positive (2 − 3x, mais −2x − 1) ; constante p + q√m écrite en deux termes (x + 1 − √5)."""
    c0, c1 = en_nombres(f)
    if not c1.rationnel:
        raise _Incoherent("coefficient irrationnel devant l'inconnue")
    terme_x = [((-1 if c1.p < 0 else 1), _monome_abs(c1.p, 1, X, dec))]
    constantes = []
    if c0.p != 0:
        constantes.append(((-1 if c0.p < 0 else 1), nb_exact(abs(c0.p), dec)))
    if c0.q != 0:
        constantes.append(((-1 if c0.q < 0 else 1), arbre_nombre(Nombre._brut(F(0), abs(c0.q), c0.m), dec)))
    return _somme(constantes + terme_x if c1.p < 0 and c0.signe() > 0 else terme_x + constantes)


def _constante_reduite(f, dec):
    """P4b : un facteur constant d'une Id. rem. structurée ((x + 1)² = (x − 3)² : (x + 1 − x + 3) = 4), écrit sans son signe."""
    if not f[0].rationnel:
        raise _Incoherent("facteur constant irrationnel")
    return nb_exact(abs(f[0].p), dec)


def _ligne_produit(facteurs, X, dec):
    """La ligne des facteurs réduits [(tuple de Nombre, arbre écrit)] : (produit écrit, facteurs dans l'ordre de la ligne, D14) ; un
    seul facteur monôme k·x passe en tête, comme une ME (x(x + 1), −3x(x + 1), jamais « (x + 1)(x) »)."""
    monomes = [f for f, _ in facteurs if (len(f) == 2 and f[0] == 0) or len(f) == 1]      # P4b : une constante aussi (4(2x − 2))
    if len(monomes) != 1:
        return Juxtaposition([a for _, a in facteurs]), [f for f, _ in facteurs]
    m = monomes[0]
    autres = [(f, a) for f, a in facteurs if f != m]
    c = m[-1].p
    j = Juxtaposition([_monome_abs(c, len(m) - 1, X, dec)] + [a for _, a in autres])
    return (Neg(j) if c < 0 else j), [m] + [f for f, _ in autres]


class _Structuree:
    """L'écriture d'une forme structurée : la rédaction (`_Redaction`, `_Contexte` avec les facteurs écrits), chaque ligne relue dans
    Q(√m) (±P, P = gauche − droite : garde-fou, principe 1), puis le produit nul et la résolution."""

    def __init__(self, enonce, P, x, dec):
        self.R, self.ctx, self.P, self.x, self.dec = _Redaction(enonce), _Contexte(x, dec), P, x, dec
        self.ctx.ecrits, self.Pn = {}, en_nombres(P)
        self.moins_Pn = en_nombres([-c for c in self.Pn])
        self.relire(enonce)                              # l'énoncé réécrit (Juxtaposition) est relu comme les autres lignes

    def relire(self, eq):
        """eq a le polynôme ±P (gauche − droite), lu dans Q(√m) ; sinon incohérence (« ne_conclut_pas »)."""
        if _nadd(_ecrit_en_nombres(eq.g, self.x), _ecrit_en_nombres(eq.d, self.x), -1) not in (self.Pn, self.moins_Pn):
            raise _Incoherent("ligne d'une forme structurée")

    def equiv(self, eq, prop=None):
        """La ligne ⇔ eq, relue, si elle change le TeX de la précédente."""
        if _t_element(eq) != _t_element(self.R.pivot):
            self.relire(eq)
            self.R.equiv(eq, prop)

    def ramener(self, eqs, phrase=None, cote="gauche"):
        """E1.3 : « on soustrait le second membre sans développer » (étape « ramener », méthode « RAMENER »)."""
        self.R.etape("ramener", "RAMENER", _t_element(self.R.pivot), {"cote": cote, "polynome": self.P if cote == "gauche"
                                                                        else Polynome([-c for c in self.P])})
        if phrase:
            self.R.texte(phrase)
        for eq in eqs:
            self.equiv(eq)

    def fin(self, facteurs, ecrits, reecriture=None):
        """Le produit nul (P2b) sur les facteurs écrits ; garde-fou : facteurs redéveloppés = ±P, chaque solution annule P."""
        if redevelopper(facteurs) not in (self.Pn, self.moins_Pn):
            raise _Incoherent("facteurs d'une forme structurée")
        for f, e in ecrits:
            self.ctx.ecrits.setdefault(en_nombres(f), e)
        pn = produit_nul(facteurs)
        if not all(verifier_solution(self.P, s) for s in pn["solutions"]):
            raise _Incoherent("solutions d'une forme structurée")
        if reecriture is not None:
            self.relire(reecriture)
        _ecrire_produit_nul(self.R, self.ctx, redevelopper(facteurs), pn, {}, reecriture=reecriture)
        self.R.fermer()
        sols = pn["solutions"]
        noms = _noms_formule([racines_formule(rationnel(f)) for f, genre, _ in pn["facteurs"] if genre == "formule"])
        return {"statut": "resolu", "etapes": self.R.etapes, "solutions": sols, "S": _tex_S(sols, self.dec),
                "approx": _tex_approx(sols, noms, self.x, self.dec), "variantes": [], "message": None}


def _ecrire_produit_ecrit(E, arbre, lu):
    """E13 (Az 4.1 d) : un produit écrit égal à 0, produit nul direct ; D24 : un carré réécrit (B)(B) d'abord ; les facteurs écrits
    comme dans la saisie (2 − x = 0), dans l'ordre écrit (D14), la constante et le monôme en tête (« 3 = 0 » impossible, « 2x = 0 »)."""
    k, j, facteurs = lu
    if any(P.degre == 2 for _, P, _ in facteurs):
        return _factoriser_produit_ecrit(E, lu)
    liste = ([_monome_n(k, j)] if (k, j) != (1, 0) else []) + [en_nombres(P) for _, P, e in facteurs for _ in range(e)]
    reecriture = None
    if any(e == 2 for _, _, e in facteurs):
        reecriture = Eq(_juxtaposer(_sans_carres(arbre)), Nb(0))
    return E.fin(liste, [(P, b) for b, P, _ in facteurs], reecriture)


def _factoriser_produit_ecrit(E, lu):
    """P4b : un produit écrit égal à 0 dont un facteur est de degré 2 ((x² − 1)(x + 2) = 0, 3(x² − 4) = 0) : chaque trinôme est
    factorisé par le chemin du cours (D28 : ME, Id. rem., S-P, tâtonnement, formule), sur le produit écrit (`_Contexte.suivre`), les
    tentatives en échec et la formule en dernier ; puis le produit nul (E8, E9). None (« hors du cours ») si un carré accompagne le
    trinôme (D24 sur un produit déjà factorisé : non écrit) ou si un trinôme ne se résout pas."""
    k, j, facteurs = lu
    if any(e != 1 for _, _, e in facteurs):
        return None
    ctx = E.ctx
    for b, P, _ in facteurs:
        ctx.ecrits.setdefault(en_nombres(P), b)
    ctx.suivre(E.P, k, j, [(P, 1) for _, P, _ in facteurs])
    ctx.apres_me = True                                                 # on travaille sur un facteur : il est nommé (E4)
    etapes, vus = [], []
    for _, P, _ in facteurs:
        if P.degre == 2 and P not in vus:
            vus.append(P)
            if _factoriser(P, ORDRE_DU_COURS, etapes) is None:
                return None
    _ecrire_chemin(E.R, ctx, _ordre_d_ecriture(etapes), True)
    liste = ([_monome_n(ctx.k, ctx.j)] if (ctx.k, ctx.j) != (1, 0) else []) + [f for f, e in ctx.courants for _ in range(e)]
    return E.fin(liste, [])


def _commun(gauche, droite, x):
    """E3 (2.12 e) : un facteur de degré 1 **égal** (même polynôme) dans les deux membres écrits en facteurs ; le reste G de la gauche
    et H de la droite, chacun de degré ≤ 1, G − H de degré 1. (facteur écrit, Polynome, G, H) ; G et H : (k, j, facteurs) ; None sinon."""
    lg, ld = _membre_en_facteurs(gauche, x), _membre_en_facteurs(droite, x)
    if lg is None or ld is None:
        return None

    def sans(lu, i):
        k, j, fs = lu
        b, P, e = fs[i]
        return k, j, fs[:i] + ([(b, P, e - 1)] if e > 1 else []) + fs[i + 1:]

    for i, (b, P, _) in enumerate(lg[2]):
        for i2, (_, Q, _) in enumerate(ld[2]):
            if P != Q:
                continue
            G, H = sans(lg, i), sans(ld, i2)
            pg, ph = rationnel(_poly_facteurs(*G)), rationnel(_poly_facteurs(*H))
            if pg.degre <= 1 and ph.degre <= 1 and not rationnel(_nadd(en_nombres(pg), en_nombres(ph), -1)).nul():
                return b, P, G, H                                       # P4b : G − H constant (degré 1 une fois factorisée)
    return None


def _reste_ecrit(lu, X, dec):
    """Le reste G (ou H) d'un membre après le facteur commun, écrit dans le crochet (sans son signe) : (signe, arbre, termes signés
    [(j, k)] une fois les parenthèses enlevées). Une somme seule : (2 − x) ; k·somme : 3(x + 2) ; un monôme ou une constante : x, 2."""
    k, j, fs = lu
    s = -1 if k < 0 else 1
    if not fs:
        return s, _monome_abs(k, j, X, dec), [(j, k)]
    b, P, _ = fs[0]
    termes = [(i, k * c) for i, c in _binome_ecrit(b, X.nom)[1]]
    return s, (Groupe(b) if abs(k) == 1 else Op("*", nb_exact(abs(k), dec), b)), termes


def _ecrire_commun(E, gauche, droite, c):
    """E3 (2.12 e) : l'avertissement, « g − d = 0 » sans développer, la ME du facteur commun avec un crochet, les parenthèses
    enlevées, le facteur réduit (E5), puis le produit nul. Pas de ME faite après coup."""
    b, P, G, H = c
    X, dec, x = E.ctx.X, E.dec, E.x
    d, sd_ = _sans_neg(droite)
    if sd_ < 0:
        diff = Op("+", _juxtaposer(gauche), Groupe(d) if comme_somme(d) else _juxtaposer(d))
    else:
        diff = Op("-", _juxtaposer(gauche), _juxtaposer(droite))
    E.ramener([Eq(diff, Nb(0))], phrase=_phrase_attention(_t(Groupe(b))))
    (sg, ag, tg), (sh, ah, th) = _reste_ecrit(G, X, dec), _reste_ecrit(H, X, dec)
    Q = rationnel(_nadd(_poly_facteurs(*G), _poly_facteurs(*H), -1))
    reduit = _facteur_reduit(en_nombres(Q), X, dec) if Q.degre == 1 else nb_exact(abs(Q[0]), dec)
    E.R.etape("factoriser", "ME", _t(diff), {"facteur": P, "facteurs": [en_nombres(P), en_nombres(Q)]})
    crochet = Op("-" if sh > 0 else "+", Neg(ag) if sg < 0 else ag, ah)
    E.equiv(Eq(Juxtaposition([b, Crochet(crochet)]), Nb(0)), "ME")
    termes = [(-1 if k < 0 else 1, _monome_abs(k, j, X, dec)) for j, k in tg + [(j, -k) for j, k in th]]
    E.equiv(Eq(Juxtaposition([b, _somme(termes)]), Nb(0)))
    ligne, facteurs = _ligne_produit([(en_nombres(P), b), (en_nombres(Q), reduit)], X, dec)
    E.equiv(Eq(ligne, Nb(0)))
    return E.fin(facteurs, [(P, b), (Q, reduit)])


def _terme_idrem(signe, carre, constante, dec, X):
    """A (terme positif) ou B (terme négatif) de l'Id. rem. structurée : {etiquette, l1 (dans (A + B)(A − B)), termes (parenthèses
    enlevées), poly (tuple de Nombre), car (TeX du carré quand √k ≠ 1, pour « car A² = 4(x − 2)² »), r} ; None si A ou B ne s'écrit pas
    (√k irrationnel ; constante A irrationnelle)."""
    if carre is not None:
        _, k, b, Pb, tb, t = carre
        r = polynomes.racine_carree(k)
        if r is None:
            return None
        eti = b if r == 1 else Op("*", nb_exact(r, dec), b)
        return {"etiquette": eti, "l1": Groupe(b) if r == 1 else eti, "r": r,
                "termes": [(-1 if r * c < 0 else 1, _monome_abs(r * c, j, X, dec)) for j, c in tb],
                "poly": en_nombres([r * c for c in Pb]), "car": None if r == 1 else _t(_juxtaposer(t)), "carre": True}
    racine = Nombre.racine(abs(constante))
    if signe > 0 and not racine.rationnel:
        return None
    a = arbre_nombre(racine, dec)
    return {"etiquette": a, "l1": a, "r": 1, "termes": [(1, a)], "poly": (racine,), "car": None, "carre": False}


def _ecrire_carres(E, gauche, droite):
    """E5, Id. rem. sur une forme structurée (2.9 k, l ; 2.12 h) : tout ramené à gauche sans développer (E1.3), les constantes
    regroupées ; un carré k(B)² et une constante de signe opposé, ou deux carrés de signes opposés : A² − B² avec A le terme positif.
    Étiquette en marge, ou ligne de texte « (car A² = …) » quand A ou B doit être justifié (√k ≠ 1, 2.9 k) ; (A + B)(A − B), les
    parenthèses enlevées (seulement après un « − » devant une parenthèse ou quand √k ≠ 1 : 2.9 l n'a pas cette ligne), les facteurs
    réduits (E5). Un seul carré et une constante nulle : produit nul direct (D24). None si la forme n'est pas écrite en P4a."""
    x, X, dec = E.x, E.ctx.X, E.dec
    termes = ([] if _est_zero(gauche) else _termes_signes(gauche)) + \
        ([] if _est_zero(droite) else [(-s, t) for s, t in _termes_signes(droite)])
    constantes, carres = [], []
    for s, t in termes:
        if isinstance(t, _Groupe):
            return None
        if not variables(t):
            v = polynomes.const(t)
            if v is None:
                return None
            constantes.append(s * v)
            continue
        c = _carre_ecrit(t, x)
        if c is None:
            return None
        carres.append((s * c[0],) + c[1:] + (t,))
    c = sum(constantes, F(0))
    if not 1 <= len(carres) <= 2 or (len(carres) == 2 and (c != 0 or carres[0][0] == carres[1][0])):
        return None
    if len(carres) == 1 and c != 0 and (c > 0) == (carres[0][0] > 0):
        return None
    lignes = []
    if not _est_zero(droite):
        lignes.append(Eq(_somme([(s, _juxtaposer(t)) for s, t in termes]), Nb(0)))
    groupe = [(q[0], _juxtaposer(q[-1])) for q in carres] + ([((-1 if c < 0 else 1), nb_exact(abs(c), dec))] if c else [])
    if len(constantes) > 1 or (constantes and c == 0):
        lignes.append(Eq(_somme(groupe), Nb(0)))
    if len(carres) == 1 and c == 0:                                    # k(B)² = 0 : produit nul direct (D24)
        s, k, b, Pb, _, t = carres[0]
        arbre = Neg(t) if s < 0 else t
        lu = _produit_ecrit(arbre, x)
        if lu is None:
            return None
        if lignes:
            E.ramener(lignes)
        return _ecrire_produit_ecrit(E, arbre, lu)
    if len(carres) == 2:
        pos, neg = (carres[0], carres[1]) if carres[0][0] > 0 else (carres[1], carres[0])
        A, B = _terme_idrem(1, pos, None, dec, X), _terme_idrem(-1, neg, None, dec, X)
    else:
        q = carres[0]
        A, B = (_terme_idrem(1, q, None, dec, X), _terme_idrem(-1, None, c, dec, X)) if q[0] > 0 else \
            (_terme_idrem(1, None, c, dec, X), _terme_idrem(-1, q, None, dec, X))
    if A is None or B is None:
        return None
    f1, f2 = _nadd(A["poly"], B["poly"]), _nadd(A["poly"], B["poly"], -1)
    if len(f1) > 2 or len(f2) > 2 or (len(f1), len(f2)) == (1, 1):
        return None
    if lignes:
        E.ramener(lignes)
    a_tex, b_tex = _t(A["etiquette"]), _t(B["etiquette"])
    E.R.etape("factoriser", "IDREM_DIFF", _t(E.R.pivot.g), {"A": a_tex, "B": b_tex, "forme": "structuree", "facteurs": [f1, f2]})
    avec = rf"avec \(\fbox{{$A = {a_tex},\ B = {b_tex}$}}\)"
    car = [rf"\({n}^{{2}} = {T['car']}\)" for n, T in (("A", A), ("B", B)) if T["car"]]
    l1 = Eq(Juxtaposition([Op("+", A["l1"], B["l1"]), Op("-", A["l1"], B["l1"])]), Nb(0))
    if car:
        E.R.texte(rf"Id. rem. \(A^{{2}} - B^{{2}}\) {avec} (car " + " et ".join(car) + ").")
        E.equiv(l1)
    else:
        E.equiv(l1, rf"Id. rem. \(A^{{2}} - B^{{2}}\) {avec}")
    if A["r"] != 1 or B["r"] != 1 or B["carre"]:
        moins = [(-s, t) for s, t in B["termes"]]
        E.equiv(Eq(Juxtaposition([_somme(A["termes"] + B["termes"]), _somme(A["termes"] + moins)]), Nb(0)))
    r1, r2 = (_facteur_reduit(f, X, dec) if len(f) == 2 else _constante_reduite(f, dec) for f in (f1, f2))
    ligne, facteurs = _ligne_produit([(f1, r1), (f2, r2)], X, dec)
    E.equiv(Eq(ligne, Nb(0)))
    return E.fin(facteurs, [(f1, r1), (f2, r2)])


def _ecrire_identite_structuree(E, gauche, droite):
    """P4b : une forme structurée dont les deux membres sont égaux ((x + 1)² = (x + 1)², (x − 1)(x + 2) = (x − 1)(x + 2)) : « g − d = 0 »
    sans développer (E1.3), puis « 0 = 0 » et la phrase de l'identité (Exp-log) ; S = ℝ. (Une égalité fausse ne peut pas venir
    d'une forme structurée : elle donnerait « c = 0 » et la phrase d'Exp-log.)"""
    d, sd_ = _sans_neg(droite)
    if sd_ < 0:
        diff = Op("+", _juxtaposer(gauche), Groupe(d) if comme_somme(d) else _juxtaposer(d))
    else:
        diff = Op("-", _juxtaposer(gauche), Groupe(droite) if comme_somme(droite) else _juxtaposer(droite))
    E.ramener([Eq(diff, Nb(0)), Eq(nb_exact(E.P[0], E.dec), Nb(0))])
    E.R.texte(PHRASE_IDENTITE if E.P.nul() else PHRASE_EGALITE_FAUSSE)
    E.R.fermer()
    ensemble = "reels" if E.P.nul() else "vide"
    return {"statut": "resolu", "etapes": E.R.etapes, "solutions": [], "S": _tex_S([], E.dec, ensemble), "approx": None,
            "variantes": [], "message": None}


def _rediger_structure(gauche, droite, x, dec):
    """P4a : la résolution d'une forme structurée (E1.3 : rien n'est développé), dans cet ordre : produit déjà nul (E13), facteur
    commun aux deux membres (E3), Id. rem. sur la forme structurée (E5) ; P4b : identité, facteur de degré 2 dans un produit, degré 1
    une fois factorisée. None si l'outil ne l'écrit pas (« forme_non_traitee », P5)."""
    P = vers_polynome(Op("-", gauche, droite), x)
    E = _Structuree(ecrire_enonce(gauche, droite, x), P, x, dec)
    if P.degre < 1:
        return _ecrire_identite_structuree(E, gauche, droite)
    for a, b, cote in ((gauche, droite, "gauche"), (droite, gauche, "droite")):
        if _est_zero(b) and _est_produit(a, x):
            lu = _produit_ecrit(a, x, trinomes=True)
            if lu is None:
                return None
            if cote == "droite":
                E.ramener([Eq(_juxtaposer(a), Nb(0))], cote="droite")
            return _ecrire_produit_ecrit(E, a, lu)
    if _est_produit(gauche, x) or _est_produit(droite, x):
        c = _commun(gauche, droite, x)
        if c is not None:
            return _ecrire_commun(E, gauche, droite, c)
    return _ecrire_carres(E, gauche, droite)


def _non_resolu(statut):
    return {"statut": statut, "etapes": [], "solutions": [], "S": None, "approx": None, "variantes": [], "message": MESSAGES[statut]}


def _formule_utilisee(ch):
    return any(e["methode"] == "FORMULE" for e in ch["etapes"])


def bicarree(P):
    """§ 4, § 13.4 : P = ax⁴ + bx² + c (c ≠ 0) auquel ni la ME ni l'Id. rem. ne s'applique (x⁴ − 5x² + 4) : il se ramène au 2e degré
    par un changement de variable (message « bicarrée », statut « pas_encore »). Pris à la lettre : x⁴ − 16 (Id. rem.) n'en est
    pas une, 2x⁴ − 10x² + 8 (ME de 2) non plus (« hors du cours »)."""
    P = Polynome(P)
    return (P.degre == 4 and P[1] == 0 and P[3] == 0 and P[0] != 0 and mise_en_evidence(P) is None
            and identite(P) is None)


def hors_du_cours(P, ch):
    """P5 (question 29 ; CLAUDE.md, rien de faux à l'écran) : « Cette équation ne se résout pas avec les méthodes du cours. » n'est
    écrit que s'il est vrai : P (développé, `chemin` en « hors_cours ») est de degré ≥ 3, à coefficients entiers, n'est pas une
    bicarrée, et aucune méthode du cours n'y aboutit (le chemin de D28 n'a fait au plus qu'une ME de constante : ni xʲ en évidence,
    ni Id. rem.) ; le facteur qui reste n'est pas une bicarrée non plus. Sinon le cas est douteux (2x⁴ − 10x² + 8 : ME puis
    bicarrée ; x⁶ − 64 : Id. rem. puis des facteurs de degré 3 ; 0,5x³ − 2x : ME refusée sur des coefficients non entiers) : le
    message prudent « forme_non_traitee »."""
    P = Polynome(P)
    if P.degre < 3 or not P.entiers() or bicarree(P):
        return False
    reste = P
    for e in ch["etapes"]:
        if not (e["methode"] == "ME" and e["resultat"]["j"] == 0):
            return False
        reste = e["resultat"]["reste"]
    return not bicarree(reste) and mise_en_evidence(reste) is None and identite(reste) is None


def resoudre_equation(gauche, droite, inconnue, decimaux_enonce=False, methodes=ORDRE_DU_COURS):
    """La résolution rédigée de « gauche = droite » (arbres de moteur/expr.py) en l'inconnue (§ 5) :

    {statut: "resolu" | "pas_encore" | "hors_cours" | "forme_non_traitee" | "ne_conclut_pas" | "hors_bornes",
     etapes: [Etape], solutions: [Nombre] croissantes, S: TeX, approx: texte « soit … ≈ … » (TeX entre \\( et \\)) ou None,
     variantes: ["formule"] (E12 : le chemin du cours n'utilise pas la formule) ou [], message: texte pour un statut non résolu}
    Etape = {phase, methode, cible (TeX), parametres (calcul exact), lignes (rangées : triplets (lien, expr, prop) et `LigneTexte`),
             segment (la `Chaine` de l'étape, pivot puis ⇔, ou None)}.

    P4a : une forme structurée (`forme_structuree`, E1.3) est résolue sans développer (`_rediger_structure` : produit déjà nul,
    facteur commun aux deux membres, Id. rem. sur la forme structurée ; chaque ligne relue, garde-fou exact), sans variante. P3 :
    sinon, l'équation est ramenée à « P = 0 » (E1, E2 : `ramener`, étapes de phase « ramener »). P4b : degré 2 et degré ≥ 3 par le
    chemin du cours (`chemin`, E13) ; degré 1 : on isole l'inconnue (D20) ; degré 0 : identité (S = ℝ) ou égalité fausse (S = ∅),
    avec les phrases d'Exp-log. Degré ≥ 3 que le cours ne résout pas : « pas_encore » (bicarrée, `bicarree`) ou « hors_cours »
    (seulement s'il est vrai, `hors_du_cours`) ; une forme que l'outil n'écrit pas (E2 hors de ce qu'il développe, structure non
    écrite) et un degré ≥ 3 douteux : « forme_non_traitee » (P5, question 29 de suivi.md). Le calcul est celui de `chemin` (garde-fou exact) ; une valeur écrite qui ne vérifie pas son calcul donne
    « ne_conclut_pas ». methodes=ORDRE_PAR_LA_FORMULE : la variante E12 (sans effet sur une forme structurée). Une autre lettre que
    l'inconnue : ValueError (la lecture de la saisie, equations-2e-degre/equations.py, la refuse avant)."""
    autres = (variables(gauche) | variables(droite)) - {inconnue}
    if autres:
        raise ValueError(f"autres lettres que l'inconnue {inconnue} : {sorted(autres)}")
    try:
        if forme_structuree(gauche, droite, inconnue):
            res = _rediger_structure(gauche, droite, inconnue, decimaux_enonce)
            return res if res is not None else _non_resolu("forme_non_traitee")
        prep = ramener(gauche, droite, inconnue, decimaux_enonce)
        if prep is None:
            return _non_resolu("forme_non_traitee")
        P = prep["P"]
        if P.degre <= 1:
            return _rediger_bas_degre(Eq(gauche, droite), P, prep, inconnue, decimaux_enonce)
        ch = chemin(P, methodes)
        if ch["statut"] == "hors_cours":
            if bicarree(P):
                return _non_resolu("pas_encore")
            return _non_resolu("hors_cours" if hors_du_cours(P, ch) else "forme_non_traitee")
        if ch["statut"] != "resolu":
            return _non_resolu(ch["statut"])
        res = _rediger(Eq(gauche, droite), P, ch, inconnue, decimaux_enonce, cours=methodes != ORDRE_PAR_LA_FORMULE, prep=prep)
        if methodes == ORDRE_DU_COURS and not _formule_utilisee(ch):
            v = chemin(P, ORDRE_PAR_LA_FORMULE)
            res["variantes"] = ["formule"] if v["statut"] == "resolu" and _formule_utilisee(v) else []
        return res
    except HorsBornes:
        return _non_resolu("hors_bornes")
    except (_Incoherent, ValueError, TypeError, ZeroDivisionError):      # valeur non garantie, écriture qui ne vérifie pas son calcul
        return _non_resolu("ne_conclut_pas")


def _ecrire_isoler(R, ctx, P):
    """Degré 1 (E13, § 13.4, D20) : x = … en une ligne, ou kx = … puis x = … quand le coefficient de x n'est pas ±1 et que la
    constante n'est pas entière (comme le produit nul, E8). Chaque valeur écrite est recalculée."""
    c0, c1 = P
    x = Nombre(-c0 / c1)
    if c1 * x.p + c0 != 0:
        raise _Incoherent("isoler")
    final = Eq(ctx.X, arbre_nombre(x, ctx.dec))
    deja = _t_element(final) == _t_element(R.pivot)
    if deja and R.etapes:
        return [x]                                                      # « … ⇔ x = 0 » : la ligne ramenée suffit (Az 4.1 a)
    R.etape("isoler", "ISOLER", _t(ctx.poly(P)), {"solution": x})
    if deja:
        R.rangee(_t_element(final))                                     # « x = 0 » saisi tel quel : rien à transformer
        return [x]
    if c1 not in (1, -1) and c0.denominator != 1:
        R.equiv(Eq(ctx.monome(c1, 1), nb_exact(-c0, ctx.dec)))
    R.equiv(final)
    return [x]


def _rediger_bas_degre(enonce, P, prep, inconnue, dec):
    """P4b : degré 1 (isoler) ; degré 0 : identité (« Cette égalité est vraie pour tout nombre réel. », S = ℝ) ou égalité fausse
    (« Cette égalité est fausse : l'équation n'a aucune solution. », S = ∅), après les lignes de `ramener` (Exp-log, Az 4.1 g)."""
    R, ctx = _Redaction(enonce), _Contexte(inconnue, dec)
    _ecrire_ramener(R, prep, phrase=False)
    if P.degre == 1:
        sols, ensemble = _ecrire_isoler(R, ctx, P), "fini"
    else:
        if not R.etapes:
            raise _Incoherent("identité sans ligne écrite")
        R.texte(PHRASE_IDENTITE if P.nul() else PHRASE_EGALITE_FAUSSE)
        sols, ensemble = [], "reels" if P.nul() else "vide"
    R.fermer()
    if not all(verifier_solution(P, s) for s in sols):
        raise _Incoherent("solution de degré 1")
    return {"statut": "resolu", "etapes": R.etapes, "solutions": sols, "S": _tex_S(sols, dec, ensemble),
            "approx": _tex_approx(sols, {}, inconnue, dec) if sols else None, "variantes": [], "message": None}


def _en_echec(e):
    """Une étape qui mène à la formule sur son trinôme : S-P ou tâtonnement en échec, ou la formule elle-même."""
    return e["methode"] == "FORMULE" or (e["methode"] in ("SP", "TATONNEMENT") and not e["aboutit"])


def _rediger(enonce, P, ch, inconnue, dec, cours, prep=None):
    """La rédaction du chemin du cours (`chemin`) de « P = 0 », après les étapes « ramener » de `prep`. P4b : le produit écrit est
    suivi (`_Contexte.suivre`) : chaque factorisation d'un facteur le remplace sur place (degré ≥ 3) ; les tentatives en échec et
    la formule d'un facteur sont écrites après les autres factorisations (x⁴ − 16 : l'Id. rem. de x² − 4, puis le S-P de x² + 4 en
    échec), juste avant le produit nul (E9) ; en degré 2 elles sont déjà les dernières (mêmes lignes qu'en P2b)."""
    R, ctx = _Redaction(enonce), _Contexte(inconnue, dec, cours)
    ctx.suivre(P)
    formules = {e["cible"]: e["resultat"] for e in ch["etapes"] if e["methode"] == "FORMULE"}
    etapes = _ordre_d_ecriture(ch["etapes"])
    if prep is not None:
        _ecrire_ramener(R, prep, phrase=cours and bool(etapes) and etapes[0]["methode"] in ("SP", "TATONNEMENT", "FORMULE"))
    _ecrire_chemin(R, ctx, etapes, cours)
    ecrits = ([_monome_n(ctx.k, ctx.j)] if (ctx.k, ctx.j) != (1, 0) else []) + [f for f, e in ctx.courants for _ in range(e)]
    pn = produit_nul(ecrits, formules)                                  # les facteurs dans l'ordre écrit (D14)
    if pn["solutions"] != ch["produit_nul"]["solutions"] or redevelopper(ecrits) != en_nombres(P):
        raise _Incoherent("produit écrit et chemin du cours")
    seul = pn["facteurs"][0][0] if len(pn["facteurs"]) == 1 else None
    if seul is not None and pn["facteurs"][0][1] == "formule" and rationnel(seul) == P:
        _ecrire_formule(R, ctx, P, formules[P], sur_facteur=False)
    else:
        _ecrire_produit_nul(R, ctx, P, pn, formules)
    R.fermer()
    sols = pn["solutions"]
    return {"statut": "resolu", "etapes": R.etapes, "solutions": sols, "S": _tex_S(sols, dec),
            "approx": _tex_approx(sols, _noms_formule(formules.values()), inconnue, dec), "variantes": [], "message": None}


def _noms_formule(formules):
    """x₁, x₂ (E14) : seulement si une seule formule les nomme (Δ > 0)."""
    positifs = [f for f in formules if f["delta"] > 0]
    return {positifs[0]["x1"]: "x_{1}", positifs[0]["x2"]: "x_{2}"} if len(positifs) == 1 else {}


def _ordre_d_ecriture(etapes):
    """Les étapes du chemin dans l'ordre d'écriture : les tentatives en échec et la formule d'un facteur après les autres (P4b)."""
    return [e for e in etapes if not _en_echec(e)] + [e for e in etapes if _en_echec(e)]


def _ecrire_chemin(R, ctx, etapes, cours):
    """Les étapes de factorisation du chemin du cours (ME, Id. rem., S-P, tâtonnement, formule choisie d'emblée), dans l'ordre
    donné, sur le produit écrit suivi par ctx."""
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
            precedente = etapes[i - 1] if i else None
            if precedente is None or precedente["methode"] not in ("SP", "TATONNEMENT") or precedente["cible"] != Q:
                R.etape("factoriser", "FORMULE", _t(ctx.poly(Q)), r)            # formule choisie d'emblée (D22, ou E12)
                if cours:
                    if Q.entiers():
                        raise _Incoherent("formule d'emblée sur un trinôme à coefficients entiers")
                    R.texte(_choix(ctx, Q, False, "FORMULE"))
        else:
            raise _Incoherent(f"méthode {m} hors du chemin du cours")


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
    « soit … ≈ … » (E14) : la chaîne entière (invariant du § 5) ; la page la montre coupée en une carte par étape (`cartes`, R1)."""
    _resolue(resolution)
    lignes = [r for e in resolution["etapes"] for r in e["lignes"]]
    return [bloc_rangees(lignes, membre_gauche=True)] + blocs_solution(resolution)


def _resolue(resolution):
    if resolution["statut"] != "resolu":
        raise ValueError(f"résolution non résolue : {resolution['statut']}")


def blocs_solution(resolution):
    """Les blocs de la fin d'une résolution résolue : S encadré (`resultat_lim`, D29, dans une carte normale), puis la ligne
    « soit … ≈ … » (E14)."""
    _resolue(resolution)
    b = [sortie.resultat_lim(resolution["S"])]
    if resolution["approx"]:
        b.append(sortie.texte(resolution["approx"]))
    return b


def _a_une_rangee(lignes):
    return any(not isinstance(r, LigneTexte) for r in lignes)


def cartes(resolution):
    """La page d'une résolution résolue, une carte par étape (R1, question 36 de suivi.md : la chaîne coupée aux étapes, dévoilées une
    à une) : [{etapes: [indices dans resolution["etapes"]], blocs}], dans l'ordre ; S et la ligne ≈ viennent après (`blocs_solution`).

    - Une étape sans aucune ligne (la formule choisie d'emblée dans la variante E12) rejoint la carte de l'étape suivante (la
      précédente si elle est la dernière) : une carte n'est jamais vide.
    - Une carte dont la première rangée-ligne commence par ⇔ reçoit, en membre de gauche, le pivot de son segment (le dernier élément
      écrit avant elle, `rangees(segment)[0]`) : « 4x² + 2x − 56 = 0 ⇔ 2(2x² + x − 28) = 0 », écrit une seule fois (R5), comme Exp-log
      écrit en tête d'une carte l'équation d'arrivée de la précédente ; la première carte porte l'énoncé dans ses lignes (il passe
      en membre de gauche comme dans `blocs`), et une carte qui commence par les lignes de Δ (sans lien) n'en reçoit pas (§ 13.3 :
      pas de répétition quand aucun ⇔ ne suit ; une ligne de Δ ne passe jamais en membre de gauche, « x = −b/2a = 1 ⇔ x = 0 ou
      x = 1 » serait faux). Bloc : `bloc_rangees`, un bloc « chaine » valide (`sortie.valider`).
    - Une étape sans rangée-ligne (tentative en échec, phrase de choix de la formule seule, « Δ < 0 : … ») : une chaîne sans ligne
      {lien, expr} serait refusée et A4 interdit le HTML dans un bloc texte ; ses lignes pleine largeur sont des blocs `texte` (le
      texte tel quel, TeX entre \\( et \\)) et `tableau_essais`.

    Les rangées des cartes, mises bout à bout (membre de gauche mis à part), sont celles de la chaîne entière de `blocs` (§ 5, testé)."""
    _resolue(resolution)
    groupes, attente = [], []
    for i, e in enumerate(resolution["etapes"]):
        if not e["lignes"]:
            attente.append(i)
            continue
        groupes.append(attente + [i])
        attente = []
    if attente and groupes:
        groupes[-1] += attente
    out = []
    for groupe in groupes:
        etapes = [resolution["etapes"][i] for i in groupe]
        lignes = [r for e in etapes for r in e["lignes"]]
        if _a_une_rangee(lignes):
            premiere = next(r for r in lignes if not isinstance(r, LigneTexte))
            e = next(e for e in etapes if e["lignes"])
            pivot = rangees(e["segment"])[0] if e["segment"] is not None else None
            if premiere[0]:
                lignes = [pivot] + lignes
            blocs_ = [bloc_rangees(lignes, membre_gauche=premiere[0] != "" or premiere == pivot)]
        else:
            blocs_ = [r.contenu if isinstance(r.contenu, dict) else sortie.texte(texte_message(r.contenu)) for r in lignes]
        out.append({"etapes": groupe, "blocs": blocs_})
    return out
