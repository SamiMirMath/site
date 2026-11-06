"""Oracle numérique indépendant des moteurs : évalue l'arbre d'une fonction en haute
précision (mpmath, 50 chiffres) avec ses propres règles de définition. Ni `evaluer`
(arrondi des compensations) ni SymPy ne sont utilisés.

Conventions (celles du cours, cf. docs/specifications/ensemble-definition.md) :
ln(u) : u > 0 ; √u : u ≥ 0 ; quotient : dénominateur ≠ 0 ;
u^(p/q) constant, q impair : défini sur ℝ (racine réelle) ; q pair : u ≥ 0 ;
exposant négatif : u ≠ 0 ; exposant non constant : u > 0 ; u^0 = 1 (y compris 0^0).

`racines(coeffs)` (briques-communes B6, pour le 2e degré) : racines réelles d'un polynôme à coefficients rationnels, avec leur
multiplicité, par mpmath et Fraction seuls (docstring de la fonction)."""
from decimal import Decimal
from fractions import Fraction as F
from math import lcm

import mpmath

from moteurs import ensemble_def as ed

mp = mpmath.mp
mp.dps = 50


def _constante(n):
    v = ed.valeur_constante(n)
    if v is None:
        return None
    return F(v) if not isinstance(v, float) else F(0)


def _sans_x(n):
    if isinstance(n, ed.X):
        return False
    if isinstance(n, (ed.Nb, ed.E)):
        return True
    if isinstance(n, (ed.Neg, ed.Fn)):
        return _sans_x(n.a)
    return _sans_x(n.a) and _sans_x(n.b)


def valeur(n, x):
    """Valeur de l'arbre n en x (mpf) ; None si non définie."""
    x = mp.mpf(x)
    return _val(n, x)


def _val(n, x):
    if isinstance(n, ed.Nb):
        return mp.mpf(n.v.numerator) / n.v.denominator
    if isinstance(n, ed.X):
        return x
    if isinstance(n, ed.E):
        return mp.e
    if isinstance(n, ed.Neg):
        a = _val(n.a, x)
        return None if a is None else -a
    if isinstance(n, ed.Fn):
        a = _val(n.a, x)
        if a is None:
            return None
        if n.nom == "ln":
            return mp.log(a) if a > 0 else None
        if n.nom == "sqrt":
            return mp.sqrt(a) if a >= 0 else None
        return mp.exp(a)
    a = _val(n.a, x)
    if a is None:
        return None
    if n.op == "^":
        e = _constante(n.b)
        if e is None:
            b = _val(n.b, x)
            if b is None:
                return None
            if _sans_x(n.b):               # exposant constant irrationnel (ou rationnel non évident)
                if abs(b) < mp.mpf("1e-40"):
                    return mp.mpf(1)       # exposant nul : u⁰ = 1
                if a == 0:
                    return mp.mpf(0) if b > 0 else None
            if a <= 0:
                return None
            return mp.exp(b * mp.log(a))
        if e == 0:
            return mp.mpf(1)
        if a == 0:
            return mp.mpf(0) if e > 0 else None
        if e.denominator == 1:
            return a ** int(e)
        if a < 0:
            if e.denominator % 2 == 0:
                return None
            r = (-a) ** (mp.mpf(e.numerator) / e.denominator)
            return -r if e.numerator % 2 else r
        return a ** (mp.mpf(e.numerator) / e.denominator)
    b = _val(n.b, x)
    if b is None:
        return None
    if n.op == "+":
        return a + b
    if n.op == "-":
        return a - b
    if n.op == "*":
        return a * b
    if b == 0:
        return None
    return a / b


def definie(n, x):
    return valeur(n, x) is not None


def derivee(n, x, h=mp.mpf("1e-20")):
    """f'(x) par différence centrée en haute précision (erreur ~ h², négligeable)."""
    a, b = valeur(n, mp.mpf(x) + h), valeur(n, mp.mpf(x) - h)
    if a is None or b is None:
        return None
    return (a - b) / (2 * h)


# --- racines d'un polynôme (briques-communes B6) -----------------------------------------------------------------------------
# Indépendant des moteurs : ni `ed`, ni aucun module de moteur/ ou d'un outil, ni SymPy ; Fraction (calcul exact des coefficients)
# et mpmath seulement. Le contexte global de mpmath n'est changé que le temps du calcul (mp.workdps).

SEUIL_RACINES = mp.mpf("1e-20")    # |Im| < SEUIL : racine réelle ; deux racines à moins de SEUIL : un seul groupe (multiplicité)
CHIFFRES_RACINES = 50              # chiffres des racines rendues


def _racines_coefficient(c):
    """Le coefficient c en Fraction exacte (types acceptés : voir `racines`)."""
    if isinstance(c, bool) or isinstance(c, float):
        raise TypeError(f"coefficient {c!r} : un {type(c).__name__} est refusé (un float n'est pas le décimal écrit : "
                        "passer int, Fraction, Decimal ou str)")
    if isinstance(c, (int, F)):
        return F(c)
    if isinstance(c, Decimal):
        if not c.is_finite():
            raise ValueError(f"coefficient {c!r} : valeur non finie")
        return F(c)
    if isinstance(c, str):
        try:
            return F(c.strip())
        except (ValueError, ZeroDivisionError) as e:
            raise ValueError(f"coefficient {c!r} : nombre illisible (écrire « 1.5 » ou « -3/4 »)") from e
    raise TypeError(f"coefficient {c!r} : type {type(c).__name__} refusé (int, Fraction, Decimal ou str)")


def _racines_entiers(coeffs):
    """Coefficients exacts, tête nulle retirée, multipliés par le PPCM des dénominateurs (mêmes racines, entiers exacts)."""
    if not isinstance(coeffs, (list, tuple)):
        raise TypeError(f"coefficients : liste ou tuple attendu, pas {type(coeffs).__name__}")
    fr = [_racines_coefficient(c) for c in coeffs]
    while fr and fr[0] == 0:
        fr.pop(0)
    if not fr:
        raise ValueError("polynôme nul : tout réel est racine (l'identité se traite à part)")
    m = lcm(*(c.denominator for c in fr))
    return [int(c * m) for c in fr]


def _racines_derivee(a):
    n = len(a) - 1
    return [c * (n - i) for i, c in enumerate(a[:-1])]


def _racines_valeur(a, x):
    """(P(x), Σ|aᵢ||x|ⁱ) : la valeur et son échelle naturelle (ce que l'arrondi peut laisser)."""
    v, s, ax = mp.zero, mp.zero, abs(x)
    for c in a:
        v = v * x + c
        s = s * ax + abs(c)
    return v, s


def _racines_sturm(a):
    """Nombre exact de racines réelles distinctes de P (suite de Sturm en Fraction : changements de signe en −∞ et en +∞)."""
    def reste(u, v):
        u = list(u)
        while len(u) >= len(v):
            q = u[0] / v[0]
            u = [x - q * y for x, y in zip(u, v + [0] * (len(u) - len(v)))][1:]
        while u and u[0] == 0:
            u.pop(0)
        return u

    suite = [[F(c) for c in a], [F(c) for c in _racines_derivee(a)]]
    while len(suite[-1]) > 1:
        r = reste(suite[-2], suite[-1])
        if not r:
            break
        suite.append([-c for c in r])

    def changements(signes):
        signes = [s for s in signes if s != 0]
        return sum(1 for s, t in zip(signes, signes[1:]) if s != t)

    plus = [(p[0] > 0) - (p[0] < 0) for p in suite]
    moins = [s if (len(p) - 1) % 2 == 0 else -s for s, p in zip(plus, suite)]
    return changements(moins) - changements(plus)


def _racines_complexes(a):
    """Toutes les racines (complexes) du polynôme à coefficients entiers a, degré ≥ 1 : valeurs propres de la matrice compagne
    (QR de mpmath : converge aussi pour une racine multiple, alors que polyroots peut ne pas converger)."""
    n = len(a) - 1
    if n == 1:
        return [mp.mpf(-a[1]) / a[0]]
    m = mp.zeros(n, n)
    for i in range(1, n):
        m[i, i - 1] = 1
    for i in range(n):
        m[i, n - 1] = mp.mpf(-a[n - i]) / a[0]
    return list(mp.eig(m, left=False, right=False))


def _racines_groupes(zs):
    """Groupes de racines : deux racines à moins de SEUIL_RACINES sont dans le même groupe (de proche en proche)."""
    parent = list(range(len(zs)))

    def chef(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    for i in range(len(zs)):
        for j in range(i + 1, len(zs)):
            if abs(zs[i] - zs[j]) < SEUIL_RACINES:
                parent[chef(i)] = chef(j)
    groupes = {}
    for i, z in enumerate(zs):
        groupes.setdefault(chef(i), []).append(z)
    return list(groupes.values())


def _racines_verifier(a, r, m, petit):
    """Raffine r, racine réelle de multiplicité m, par Newton sur P⁽ᵐ⁻¹⁾ (où elle est simple), puis contre-vérifie :
    |P⁽ᵏ⁾(r)| petit devant son échelle pour k < m, et |P⁽ᵐ⁾(r)| non petit (multiplicité pas sous-comptée). Rend r, ou None."""
    derivees = [a]
    for _ in range(m):
        derivees.append(_racines_derivee(derivees[-1]))
    q, dq = derivees[m - 1], derivees[m]
    for _ in range(200):
        v, _ = _racines_valeur(q, r)
        d, _ = _racines_valeur(dq, r)
        if d == 0:
            break
        pas = v / d
        r -= pas
        if abs(pas) <= mp.eps * (1 + abs(r)):
            break
    for k in range(m):
        v, s = _racines_valeur(derivees[k], r)
        if abs(v) > petit * s:
            return None
    v, s = _racines_valeur(derivees[m], r)
    if abs(v) <= petit * s:
        return None
    return r


def racines(coeffs):
    """Racines réelles du polynôme P, avec leur multiplicité, par mpmath et Fraction seuls (oracle indépendant des moteurs).

    - coeffs : liste ou tuple des coefficients, **du plus haut degré au terme constant** (ordre de `mpmath.polyroots`) :
      [17, 288, -17] est 17x² + 288x − 17. Types acceptés : int, Fraction, Decimal fini, str lue exactement par Fraction (« 1.5 »,
      « -3/4 », « 1e-3 »). Refusés (TypeError) : float (0.1 n'est pas le décimal écrit ; un float exact comme 0.5 aussi, pour
      une règle simple), bool, et tout autre type (mpf, complexe, SymPy) ; un texte illisible ou un Decimal non fini : ValueError.
    - Coefficients de tête nuls : retirés ([0, 1, -1] est x − 1). Polynôme nul (ou liste vide) : ValueError (tout réel est racine ;
      l'identité se traite à part). Constante non nulle : [] (aucune racine).
    - Résultat : liste triée de couples (racine réelle `mpf`, arrondie à 50 chiffres ; multiplicité `int`). Les racines non réelles
      ne sont pas rendues : x² + 1 donne [] (« aucune solution réelle ») ; la somme des multiplicités vaut donc le degré si et
      seulement si toutes les racines sont réelles.

    Méthode : coefficients exacts rendus entiers (PPCM des dénominateurs) ; les termes constants nuls sont retirés d'abord (racine 0,
    de multiplicité exacte le nombre de termes retirés : la contre-vérification relative ci-dessous ne conclut pas en 0, chantier du
    2e degré, Q11), le reste porte sur le quotient ; toutes les racines complexes (valeurs propres de la
    matrice compagne, `mp.eig`) à une précision interne de 30 × degré + 40 chiffres ; une racine de multiplicité m n'y est connue
    qu'à environ 10^(−précision/m) près (≤ 10⁻³⁰ pour toute m ≤ degré), bien sous les seuils. Deux racines à moins de 10⁻²⁰ sont
    regroupées (de proche en proche) ; la taille du groupe est la multiplicité. Un groupe est réel si chacun de ses membres a
    |Im| < 10⁻²⁰, non réel si aucun ; un groupe mélangé fait refuser (ValueError : l'oracle ne conclut pas). Contre-vérification de
    chaque racine réelle : la moyenne du groupe est raffinée par Newton sur P⁽ᵐ⁻¹⁾ (racine simple), puis |P⁽ᵏ⁾(r)| (k < m) doit être
    petit devant Σ|aᵢ||r|ⁱ (10^(−précision/2)) et |P⁽ᵐ⁾(r)| ne pas l'être ; enfin, le nombre de racines réelles distinctes est
    celui de la suite de Sturm, calculée exactement (Fraction) : aucune racine réelle n'est perdue ni ajoutée. Sinon ValueError.
    Seuils absolus : deux racines
    distinctes plus proches que 10⁻²⁰ seraient comptées comme une racine multiple (cas hors du corpus du 2e degré). Le contexte
    global de mpmath (précision, arrondi) est le même avant et après l'appel, même en cas d'erreur."""
    a = _racines_entiers(coeffs)
    zero = 0                                     # racine nulle (termes constants nuls, multiplicité connue) : retirée d'abord, car la
    while a[-1] == 0:                            # contre-vérification relative à Σ|aᵢ||r|ⁱ ne peut pas conclure en r = 0 (Q11 du 2e degré)
        a.pop()
        zero += 1
    n = len(a) - 1
    if n == 0:
        return [(mp.mpf(0), zero)] if zero else []
    chiffres = 30 * n + 40
    trouvees = []
    with mp.workdps(chiffres):
        petit = mp.mpf(10) ** (-(chiffres // 2))
        for groupe in _racines_groupes(_racines_complexes(a)):
            reels = [abs(mp.im(z)) < SEUIL_RACINES for z in groupe]
            if not any(reels):
                continue
            if not all(reels):
                raise ValueError(f"groupe de racines à la fois réelles et non réelles : l'oracle ne conclut pas ({coeffs!r})")
            m = len(groupe)
            r = _racines_verifier(a, mp.fsum(mp.re(z) for z in groupe) / m, m, petit)
            if r is None:
                raise ValueError(f"racine de multiplicité {m} non confirmée : l'oracle ne conclut pas ({coeffs!r})")
            trouvees.append((r, m))
    if len(trouvees) != _racines_sturm(a):
        raise ValueError(f"nombre de racines réelles différent de celui de la suite de Sturm : l'oracle ne conclut pas ({coeffs!r})")
    if zero:
        trouvees.append((mp.mpf(0), zero))
    with mp.workdps(CHIFFRES_RACINES):
        return sorted((+r, m) for r, m in trouvees)
