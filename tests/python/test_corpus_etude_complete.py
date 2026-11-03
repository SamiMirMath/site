"""Chantier « etude-complete », partie P0 : le corpus du corrigé (donnees/corpus_etude_complete.py : Ex7 et 8.15 a–d) contre un oracle
indépendant, puis contre la sortie de l'outil Étude complète.

1. Oracle : chaque résultat attendu du corpus (decisions.md §4–5) est recoupé par mpmath (50 chiffres) sur les fonctions écrites à la main,
   sans le parseur de l'outil ni SymPy : dérivée, ED, parité, zéros et signe, f(0), limites et signe d'approche, extremums (global ou non),
   asymptotes, ronds vides, pentes, valeurs approchées (règle d'arrondi de decisions.md §2).
2. Valeurs de l'outil : ED, extremums, signe de f′, limites du tableau de variations, asymptotes, fenêtre du graphique. Tout est juste
   aujourd'hui (audit-etape0.md, §3) : ces tests doivent rester verts à chaque partie.
3. Rédaction cible : chaque vérification pas encore faite par l'outil est marquée « xfail » STRICT avec le numéro de la partie qui la traitera
   (decisions.md §6). Un test marqué qui se met à passer fait échouer la suite : la partie qui le traite retire la marque. Une marque n'est
   posée que là où le test échoue aujourd'hui (paramètre par paramètre).
"""
import os
import re
import sys
from contextlib import ExitStack
from decimal import Decimal, ROUND_HALF_UP
from functools import lru_cache
from unittest import mock

import mpmath
import pytest

from moteurs import RACINE, ensemble_def  # noqa: F401  (chemins + SymPy)
import etude_complete as ec
import resoudre_ec as rec
from noyau import lire, tex

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "donnees"))
from corpus_etude_complete import FONCTIONS, PAR_ID  # noqa: E402

mp = mpmath.mp
IDS = [fn.id for fn in FONCTIONS]
INF = mp.inf


def xfail(partie, quoi):
    return pytest.mark.xfail(strict=True, reason=f"{partie} : {quoi} (decisions.md §6)")


def avec(ids_marques, marque):
    """Paramètres (une fonction du corpus chacun), la marque posée sur les identifiants donnés seulement."""
    return [pytest.param(i, id=i, marks=[marque] if i in ids_marques else []) for i in IDS]


# ---------------------------------------------------------------------------------------------------------------------------
# Outils de l'oracle (mpmath seul)
# ---------------------------------------------------------------------------------------------------------------------------
def valeur(fn, x):
    """f(x) en mpmath ; None hors de l'ED (division par zéro dans la fonction écrite à la main)."""
    try:
        return fn.f(mp.mpf(x))
    except ZeroDivisionError:
        return None


def nombre(v):
    """Point ou valeur du corpus en mpf (±∞ compris)."""
    if v in ("+oo", "oo"):
        return INF
    if v == "-oo":
        return -INF
    return mp.mpf(v)


def sondes(fn, point, cote, derivee=False):
    """Valeurs de f (ou de f′) en approchant le point : ±10^k en ±∞, a ± 10^−k en un point fini."""
    g = fn.fp if derivee else fn.f
    if point in ("-oo", "+oo"):
        s = 1 if point == "+oo" else -1
        return [g(s * mp.mpf(10) ** k) for k in (1, 2, 3)]
    d = 1 if cote == "+" else -1
    return [g(mp.mpf(point) + d * mp.mpf(10) ** -k) for k in (2, 4, 8, 16)]


def verifier_limite(v, attendu, signe):
    """v : sondes ; attendu : 'oo', '-oo' ou nombre ; signe d'approche '+' / '-' (limite finie)."""
    if attendu in ("oo", "-oo"):
        s = 1 if attendu == "oo" else -1
        assert all(s * x > 0 for x in v), v
        assert abs(v[-1]) > abs(v[0]) and abs(v[-1]) > 10 ** 6, v
        return
    c = mp.mpf(attendu)
    ecarts = [x - c for x in v]
    assert abs(ecarts[-1]) < max(abs(ecarts[0]), mp.mpf(10) ** -30), v
    assert abs(ecarts[-1]) < mp.mpf("0.001") * (1 + abs(c)), v
    s = 1 if signe == "+" else -1
    assert all(s * e > 0 for e in ecarts), (signe, v)


def arrondi(v, exact_entier=False):
    """Valeur approchée affichée (decisions.md §2) : entier exact tel quel ; |v| ≥ 0,01 : 2 décimales ; 10⁻³ ≤ |v| < 0,01 :
    2 chiffres significatifs. Sous 10⁻³ : notation scientifique, format pas encore tranché (question dans suivi.md) et absent du corpus."""
    if exact_entier:
        return str(int(mp.nint(v)))
    d = Decimal(mp.nstr(v, 40, min_fixed=-mp.inf, max_fixed=mp.inf))
    if abs(d) >= Decimal("0.01"):
        q = Decimal("0.01")
    elif abs(d) >= Decimal("0.001"):
        q = Decimal(1).scaleb(d.adjusted() - 1)
    else:
        raise ValueError(f"valeur sous 10⁻³ : {d}")
    return format(d.quantize(q, rounding=ROUND_HALF_UP), "f").replace(".", ",")


def est_entier(v):
    return abs(v - mp.nint(v)) < mp.mpf(10) ** -40


def points_tests(fn):
    """Points de l'ED (dans [−4 ; 6]) utilisés pour la dérivée et la parité."""
    pts = [mp.mpf(k) / 7 for k in range(-28, 43)]
    return [x for x in pts if valeur(fn, x) is not None]


def points_de_coupure(fn):
    return sorted([z[1] for z in fn.zeros] + list(fn.exclus))


def milieux(coupures, pas=1):
    """Un point dans chaque intervalle délimité par les coupures (de gauche à droite)."""
    if not coupures:
        return [mp.mpf(0)]
    return [coupures[0] - pas] + [(a + b) / 2 for a, b in zip(coupures, coupures[1:])] + [coupures[-1] + pas]


def limite_du_corpus(fn, point, cote):
    for p, c, v, s in fn.limites:
        if p == point and c == cote:
            return v, s
    raise KeyError((fn.id, point, cote))


def bornes_de_l_ed(fn):
    """[(point, côté)] : ±∞ et chaque côté de chaque valeur interdite."""
    out = [("-oo", ""), ("+oo", "")]
    for a in fn.exclus:
        out += [(int(a), "-"), (int(a), "+")]
    return out


# ---------------------------------------------------------------------------------------------------------------------------
# 1. Oracle : le corpus est juste
# ---------------------------------------------------------------------------------------------------------------------------
def test_corpus_complet():
    assert IDS == ["Ex7", "a", "b", "c", "d"]
    assert [fn.role for fn in FONCTIONS] == ["exemple"] + ["exercice"] * 4
    for fn in FONCTIONS:
        assert {(p, c) for p, c, _, _ in fn.limites} == set(bornes_de_l_ed(fn)), fn.id


@pytest.mark.parametrize("ident", IDS)
def test_oracle_derivee(ident):
    """f′ du corpus (celle du corrigé) = dérivée numérique de f (mpmath.diff), sur une grille de l'ED."""
    fn = PAR_ID[ident]
    for x in points_tests(fn):
        num = mp.diff(fn.f, x)
        assert abs(fn.fp(x) - num) <= mp.mpf(10) ** -30 * (1 + abs(num)), (ident, x)


@pytest.mark.parametrize("ident", IDS)
def test_oracle_ensemble_de_definition(ident):
    fn = PAR_ID[ident]
    for a in fn.exclus:
        assert valeur(fn, a) is None, (ident, a)
        assert valeur(fn, a + mp.mpf(10) ** -20) is not None and valeur(fn, a - mp.mpf(10) ** -20) is not None
    exclus = set(fn.exclus)
    for k in range(-60, 61):
        x = mp.mpf(k) / 10
        if x not in exclus:
            assert valeur(fn, x) is not None, (ident, x)


@pytest.mark.parametrize("ident", IDS)
def test_oracle_parite(ident):
    """D4 : paire (f(−x) = f(x) partout) ; « ni » par ED non symétrique (règle 1) ou par f(0) ≠ 0 et un contre-exemple (règle 3)."""
    fn = PAR_ID[ident]
    pts = [x for x in points_tests(fn) if valeur(fn, -x) is not None]
    if fn.parite == "paire":
        assert fn.non_symetrique is None and fn.contre_exemple is None
        for x in pts:
            assert abs(fn.f(-x) - fn.f(x)) <= mp.mpf(10) ** -40 * (1 + abs(fn.f(x))), (ident, x)
        return
    assert fn.parite == "ni"
    if fn.non_symetrique is not None:
        a = fn.non_symetrique
        assert valeur(fn, a) is not None and valeur(fn, -a) is None, ident
        assert fn.contre_exemple is None
        return
    # règle 3 : 0 ∈ ED et f(0) ≠ 0 (pas impaire) ; f(−a) ≠ f(a), valeurs arrondies différentes (pas paire)
    assert fn.f0 is not None and abs(fn.f(mp.mpf(0))) > 0, ident
    a, approx_a, approx_moins_a = fn.contre_exemple
    assert arrondi(fn.f(a)) == approx_a and arrondi(fn.f(-a)) == approx_moins_a, ident
    assert approx_a != approx_moins_a, ident


@pytest.mark.parametrize("ident", IDS)
def test_oracle_zeros_et_signe(ident):
    fn = PAR_ID[ident]
    for ecrit, z, approx in fn.zeros:
        assert abs(fn.f(z)) < mp.mpf(10) ** -40, (ident, ecrit)
        assert arrondi(z) == approx, (ident, ecrit)
    coupures = points_de_coupure(fn)
    assert len(fn.signe) == len(coupures) + 1, ident
    for x, s in zip(milieux(coupures), fn.signe):
        assert (fn.f(x) > 0) == (s == "+"), (ident, x)
    # pas d'autre zéro : f garde son signe sur une grille fine de chaque intervalle
    for k in range(-400, 401):
        x = mp.mpf(k) / 50
        v = valeur(fn, x)
        if v is None or any(abs(x - c) < mp.mpf("0.001") for c in coupures):
            continue
        i = sum(1 for c in coupures if c < x)
        assert (v > 0) == (fn.signe[i] == "+"), (ident, x)


@pytest.mark.parametrize("ident", IDS)
def test_oracle_ordonnee_a_l_origine(ident):
    fn = PAR_ID[ident]
    ecrit, v, approx = fn.f0
    assert abs(fn.f(mp.mpf(0)) - v) < mp.mpf(10) ** -40, ident
    assert arrondi(v, est_entier(v)) == approx, ident


@pytest.mark.parametrize("ident", IDS)
def test_oracle_limites(ident):
    fn = PAR_ID[ident]
    for point, cote, attendu, signe in fn.limites:
        assert (signe is None) == (attendu in ("oo", "-oo")), (ident, point, cote)
        verifier_limite(sondes(fn, point, cote), attendu, signe)


@pytest.mark.parametrize("ident", IDS)
def test_oracle_regroupement_infini(ident):
    """D16 : on ne regroupe x → ±∞ que si les deux limites sont égales (condition nécessaire, vérifiable par l'oracle)."""
    fn = PAR_ID[ident]
    if fn.regroupe_infini:
        assert limite_du_corpus(fn, "-oo", "") == limite_du_corpus(fn, "+oo", ""), ident


@pytest.mark.parametrize("ident", IDS)
def test_oracle_extremums(ident):
    """Valeur exacte, f′ = 0, changement de signe de f′ (+ → − : maximum), valeurs approchées, puis global ou non (D11)."""
    fn = PAR_ID[ident]
    for e in fn.extremums:
        assert abs(fn.f(e.x) - e.y) < mp.mpf(10) ** -40, (ident, e.genre)
        assert abs(fn.fp(e.x)) < mp.mpf(10) ** -40, (ident, e.genre)
        h = mp.mpf("0.001")
        avant, apres = fn.fp(e.x - h), fn.fp(e.x + h)
        assert (avant > 0 > apres) if e.genre == "maximum" else (avant < 0 < apres), (ident, e.genre)
        assert arrondi(e.x, est_entier(e.x)) == e.approx_x, (ident, e.genre)
        assert arrondi(e.y, est_entier(e.y)) == e.approx_y, (ident, e.genre)
        # D11 : global si la valeur dépasse strictement toutes les limites aux bornes de l'ED et les autres extremums du même genre
        s = 1 if e.genre == "maximum" else -1
        concurrents = []
        for point, cote, v, _ in fn.limites:
            concurrents.append(((point, cote), s * nombre(v)))
        for autre in fn.extremums:
            if autre is not e and autre.genre == e.genre:
                concurrents.append((None, s * autre.y))
        battu = [qui for qui, v in concurrents if v >= s * e.y]
        assert e.global_ == (not battu), (ident, e.genre, battu)
        if e.global_:
            assert e.raison is None
        else:
            assert e.raison in battu, (ident, e.genre, e.raison, battu)


@pytest.mark.parametrize("ident", IDS)
def test_oracle_asymptotes_et_ronds_vides(ident):
    fn = PAR_ID[ident]
    attendues = []
    for point in ("-oo", "+oo"):
        v, s = limite_du_corpus(fn, point, "")
        if v not in ("oo", "-oo"):
            attendues.append((point, v, "au-dessus" if s == "+" else "au-dessous"))
    assert sorted(attendues) == sorted(fn.horizontales), ident
    verticales, ronds = [], []
    for a in fn.exclus:
        infinis = [c for c in ("-", "+") if limite_du_corpus(fn, int(a), c)[0] in ("oo", "-oo")]
        finies = [limite_du_corpus(fn, int(a), c)[0] for c in ("-", "+") if c not in infinis]
        if infinis:
            verticales.append((a, {("-",): "gauche", ("+",): "droite"}.get(tuple(infinis), "deux")))
        for v in sorted(set(finies)):
            ronds.append((a, v))
    assert verticales == fn.verticales, ident
    assert ronds == fn.ronds_vides, ident


@pytest.mark.parametrize("ident", IDS)
def test_oracle_pentes_aux_points_exclus(ident):
    fn = PAR_ID[ident]
    for point, cote, attendu, signe in fn.pentes:
        assert limite_du_corpus(fn, point, cote)[0] not in ("oo", "-oo"), (ident, point, cote)
        verifier_limite(sondes(fn, point, cote, derivee=True), attendu, signe)


def test_arrondis_de_la_regle():
    assert arrondi(mp.exp(mp.mpf(1) / 6)) == "1,18"
    assert arrondi(3 * mp.exp(-6)) == "0,0074"
    assert arrondi(-2 * mp.exp(4)) == "-109,20"
    assert arrondi(mp.mpf(9), True) == "9"
    with pytest.raises(ValueError):
        arrondi(mp.mpf("0.00045"))


# ---------------------------------------------------------------------------------------------------------------------------
# 2. Valeurs de l'outil (vertes aujourd'hui)
# ---------------------------------------------------------------------------------------------------------------------------
@lru_cache(maxsize=None)
def etude(ident):
    r = ec.etudier(PAR_ID[ident].saisie)
    assert r["ok"], r.get("erreur")
    return r


@lru_cache(maxsize=None)
def sortie(ident):
    s = rec.resoudre(PAR_ID[ident].saisie)
    assert s["ok"], s.get("erreur")
    return s


def nombre_tex(t):
    """Valeur mpmath d'une écriture LaTeX de l'outil (±∞, 0^{+}, entiers, fractions, racines, e^{…}, \\ln(…)) ; ValueError sinon.
    Lecture écrite à la main (ni parseur de l'outil ni SymPy), sur une liste fermée de motifs."""
    t = t.strip()
    if t in (r"+\infty", r"\infty"):
        return INF
    if t == r"-\infty":
        return -INF
    s = re.sub(r"\^\{[+-]\}$", "", t)
    s = s.replace(r"\left(", "(").replace(r"\right)", ")").replace(r"\,", " ")
    s = re.sub(r"\\ln\s*\(", "log(", s)
    s = re.sub(r"\\ln\{\(([^{}]*)\)\}", r"log(\1)", s)
    for _ in range(8):
        s = re.sub(r"\\d?frac\{([^{}]*)\}\{([^{}]*)\}", r"((\1)/(\2))", s)
        s = re.sub(r"\\sqrt\{([^{}]*)\}", r"sqrt(\1)", s)
        s = re.sub(r"e\^\{([^{}]*)\}", r"exp(\1)", s)
        s = re.sub(r"(?<![a-z])e\^(\d)", r"exp(\1)", s)
    s = s.replace(" ", "")
    s = re.sub(r"(?<![a-z])e(?![a-z(])", "exp(1)", s)
    if not re.fullmatch(r"(?:[0-9+\-*/().]|exp|log|sqrt)*", s):
        raise ValueError(t)
    s = re.sub(r"(\d|\))(?=[a-z(])", r"\1*", s)
    s = re.sub(r"\d+", lambda m: f"mpf({m.group()})", s)
    return eval(s, {"__builtins__": {}}, {"exp": mp.exp, "log": mp.log, "sqrt": mp.sqrt, "mpf": mp.mpf})  # noqa: S307


def proches(a, b, tol=mp.mpf(10) ** -9):
    if a in (INF, -INF) or b in (INF, -INF):
        return a == b
    return abs(a - b) <= tol * (1 + abs(b))


def test_lecture_des_ecritures_de_l_outil():
    assert nombre_tex(r"e^{\frac{1}{6}}") == mp.exp(mp.mpf(1) / 6)
    assert proches(nombre_tex(r"- 2 e^{4}"), -2 * mp.exp(4))
    assert proches(nombre_tex(r"\frac{3}{e^{6}}"), 3 * mp.exp(-6))
    assert proches(nombre_tex(r"\ln(3)"), mp.log(3))
    assert proches(nombre_tex(r"e^{- \frac{1}{2}}"), mp.exp(-mp.mpf(1) / 2))
    assert nombre_tex("0^{+}") == 0 and nombre_tex(r"-\infty") == -INF
    with pytest.raises(ValueError):
        nombre_tex(r"x^{2}")


def exclus_de_l_outil(ed_tex):
    if ed_tex.strip() == r"\mathbb{R}":
        return []
    m = re.fullmatch(r"\\mathbb\{R\} \\setminus \\left\\\{(.*)\\right\\\}", ed_tex.strip())
    assert m, ed_tex
    return [nombre_tex(p) for p in m.group(1).replace(r"\,", "").split(";")]


@pytest.mark.parametrize("ident", IDS)
def test_outil_ensemble_de_definition(ident):
    fn = PAR_ID[ident]
    r = etude(ident)
    exclus = exclus_de_l_outil(r["ed_tex"])
    assert len(exclus) == len(fn.exclus) and all(proches(a, b) for a, b in zip(exclus, fn.exclus)), r["ed_tex"]


@pytest.mark.parametrize("ident", IDS)
def test_outil_extremums(ident):
    fn = PAR_ID[ident]
    extrema = etude(ident)["derivee"]["extrema"]
    assert len(extrema) == len(fn.extremums), extrema
    for e_outil, e in zip(sorted(extrema, key=lambda e: e["x_val"]), sorted(fn.extremums, key=lambda e: e.x)):
        assert e_outil["genre"].split()[0] == e.genre, (ident, e_outil)
        assert proches(nombre_tex(e_outil["x_tex"]), e.x) and proches(mp.mpf(e_outil["x_val"]), e.x), (ident, e_outil)
        assert proches(nombre_tex(e_outil["f_tex"]), e.y) and proches(mp.mpf(e_outil["f_val"]), e.y), (ident, e_outil)


@pytest.mark.parametrize("ident", IDS)
def test_outil_signe_de_f_prime(ident):
    """Points critiques du tableau = zéros de f′ et valeurs interdites ; signe de f′ de l'outil = signe de la f′ du corrigé (oracle)."""
    fn = PAR_ID[ident]
    table = etude(ident)["derivee"]["table_signe"]
    crit = [nombre_tex(c) for c in table["crit"]]
    attendus = sorted([e.x for e in fn.extremums] + list(fn.exclus))
    assert len(crit) == len(attendus) and all(proches(a, b) for a, b in zip(crit, attendus)), table["crit"]
    cells = next(l["cells"] for l in table["rows"] if l.get("final"))
    for i, x in enumerate(milieux(crit)):
        assert cells[2 * i] == ("+" if fn.fp(x) > 0 else "-"), (ident, x, cells)


def limites_de_l_outil(r):
    """{(point, côté): écriture} lues dans le tableau de variations de l'EC (T06c)."""
    vl, crit = r["variations_limites"], r["derivee"]["table_signe"]["crit"]
    out = {("-oo", ""): vl["moins_inf"], ("+oo", ""): vl["plus_inf"]}
    for col in vl["colonnes"]:
        a = int(nombre_tex(crit[(col["j"] - 1) // 2]))
        out[(a, "-")], out[(a, "+")] = col["gauche"], col["droite"]
    return out


@pytest.mark.parametrize("ident", IDS)
def test_outil_limites_du_tableau(ident):
    fn = PAR_ID[ident]
    lims = limites_de_l_outil(etude(ident))
    assert set(lims) == set(bornes_de_l_ed(fn)), lims
    for (point, cote), t in lims.items():
        attendu, signe = limite_du_corpus(fn, point, cote)
        assert proches(nombre_tex(t), nombre(attendu)), (ident, point, cote, t)
        if attendu == 0:
            assert t == "0^{" + signe + "}", (ident, point, cote, t)


@pytest.mark.parametrize("ident", avec({"d"}, xfail("P6", "signe d'approche d'une limite finie non nulle (1⁺, D13)")))
def test_outil_signe_d_approche_partout(ident):
    """D13 : toute limite finie s'écrit avec son signe d'approche dans le tableau (0⁺, 1⁺…)."""
    fn = PAR_ID[ident]
    for (point, cote), t in limites_de_l_outil(etude(ident)).items():
        attendu, signe = limite_du_corpus(fn, point, cote)
        if signe is not None:
            assert t.endswith("^{" + signe + "}"), (ident, point, cote, t)


@pytest.mark.parametrize("ident", IDS)
def test_outil_asymptotes(ident):
    fn = PAR_ID[ident]
    asym = etude(ident)["limites"]["asymptotes"]
    horiz = sorted(("+oo" if a["ou"].endswith(r"+\infty") else "-oo", a["valeur_val"]) for a in asym if a["genre"] == "horizontale")
    assert horiz == sorted((cote, float(v)) for cote, v, _ in fn.horizontales), asym
    vert = [a for a in asym if a["genre"] == "verticale"]
    assert sorted(a["point_val"] for a in vert) == [float(a) for a, _ in fn.verticales], asym
    for a in vert:
        cote = dict((float(p), c) for p, c in fn.verticales)[a["point_val"]]
        infini_g = a["gauche_tex"] in (r"+\infty", r"-\infty")
        infini_d = a["droite_tex"] in (r"+\infty", r"-\infty")
        assert (infini_g, infini_d) == {"gauche": (True, False), "droite": (False, True), "deux": (True, True)}[cote], a
    assert not [a for a in asym if a["genre"] not in ("horizontale", "verticale")], asym


def points_a_montrer(fn):
    pts = [(e.x, e.y) for e in fn.extremums] + [(z, mp.mpf(0)) for _, z, _ in fn.zeros]
    if fn.f0 is not None:
        pts.append((mp.mpf(0), fn.f0[1]))
    return pts


@pytest.mark.parametrize("ident", IDS)
def test_outil_fenetre_contient_extremums_zeros_et_f0(ident):
    """§3 : la fenêtre du graphique contient les extremums, les zéros et (0 ; f(0))."""
    g = etude(ident)["graphique"]
    for x, y in points_a_montrer(PAR_ID[ident]):
        assert g["xmin"] < x < g["xmax"] and g["ymin"] < y < g["ymax"], (ident, float(x), float(y), g["xmin"], g["xmax"], g["ymin"], g["ymax"])


# ---------------------------------------------------------------------------------------------------------------------------
# 3. Rédaction cible (xfail strict, numéro de la partie qui la traitera)
# ---------------------------------------------------------------------------------------------------------------------------
def chaines(obj):
    if isinstance(obj, str):
        yield obj
    elif isinstance(obj, dict):
        for v in obj.values():
            yield from chaines(v)
    elif isinstance(obj, list):
        for v in obj:
            yield from chaines(v)


def texte(cartes):
    """Tout le texte des cartes (titres et blocs), apostrophes et signes moins normalisés."""
    return "\n".join(chaines(cartes)).replace("’", "'").replace("−", "-")


def maths(cartes):
    """Le même texte, sans espaces ni \\left / \\right, virgule LaTeX {,} rendue en virgule : pour chercher des formules."""
    t = texte(cartes)
    for a, b in ((r"\left", ""), (r"\right", ""), (r"\,", ""), (r"\;", ""), (r"\!", ""), ("{,}", ","), (r"\dfrac", r"\frac")):
        t = t.replace(a, b)
    return re.sub(r"\s+", "", t)


def cartes_de(ident, *titres):
    return [c for c in sortie(ident)["cartes"] if any(t in c["titre"] for t in titres)]


def derivee_resultat(ident):
    return next(b["tex"] for c in cartes_de(ident, "Dérivée") for b in c["blocs"] if b["type"] == "resultat")


@pytest.mark.parametrize("ident", [i for i in IDS if i != "c"])
def test_P1_une_seule_exponentielle(ident):
    """c est à part : f′ = 2eˣ(3 − eˣ) garde deux eˣ, comme le corrigé."""
    assert derivee_resultat(ident).count("e^{") == 1, derivee_resultat(ident)
    table = etude(ident)["derivee"]["table_signe"]
    assert sum(1 for l in table["rows"] if l["label"].startswith("e^")) == 1, [l["label"] for l in table["rows"]]


@pytest.mark.parametrize("ident", IDS)
def test_P1_parentheses_facteur_negatif(ident):
    t = texte(cartes_de(ident, "Dérivée"))
    assert not re.search(r"\\cdot\s*-", t), t


def test_P1_derivee_de_e_x_une_seule_fois():
    t = maths(cartes_de("c", "Dérivée"))
    assert t.count("(e^{x})'=e^{x}") <= 1, t


def test_P1_forme_exacte_3e_moins_6():
    t = maths(sortie("b")["cartes"])
    assert r"\frac{3}{e^{6}}" not in t and re.search(r"3e\^\{-6\}", t), t


def test_P1_forme_exacte_c():
    r = re.sub(r"\s+", "", derivee_resultat("c").replace(r"\left", "").replace(r"\right", "").replace(r"\,", ""))
    assert r.startswith("f'(x)=2e^{x}") and "(3-e^{x})" in r, r


TITRES = ["1. Domaine de définition", "2. Parité", "3. Zéros, signe, ordonnée à l'origine", "4. Limites et asymptotes",
          "5. Dérivée, tableau de variation, extremums", "6. Graphe"]


@pytest.mark.parametrize("ident", avec(set(IDS), xfail("P2", "six parties titrées dans l'ordre du .tex (D1)")))
def test_P2_six_parties_dans_l_ordre(ident):
    t = texte(sortie(ident)["cartes"])
    positions = [t.find(titre) for titre in TITRES]
    assert -1 not in positions and positions == sorted(positions), positions


@xfail("P2", "analyse calculée une seule fois par etudier(), fenetre() sans nouvel appel (D19, EC-02) ; l'espion compte les calculs "
             "réels : à placer sous le cache s'il est ajouté autour de analyser_complet")
def test_P2_analyse_calculee_une_seule_fois():
    import noyau
    original = noyau.analyser_complet
    appels = []

    def espion(*args, **kwargs):
        appels.append(args)
        return original(*args, **kwargs)

    saisie = PAR_ID["Ex7"].saisie          # un cache par entrée (P2) doit être vidé avant de compter
    with ExitStack() as pile:
        for module in list(sys.modules.values()):
            if getattr(module, "analyser_complet", None) is original:
                pile.enter_context(mock.patch.object(module, "analyser_complet", espion))
        assert ec.etudier(saisie)["ok"]
        apres_etude = len(appels)
        assert ec.fenetre(saisie, -5, 5)["ok"]
        apres_fenetre = len(appels)
    assert (apres_etude, apres_fenetre) == (1, 1), (apres_etude, apres_fenetre)


@pytest.mark.parametrize("ident", avec(set(IDS), xfail("P3", "ED détaillé et encadré (D3)")))
def test_P3_ed_encadre(ident):
    blocs = [b for c in sortie(ident)["cartes"] for b in c["blocs"] if b["type"] in ("resultat", "encadre")]
    assert any(r"\mathbb{R}" in "".join(chaines(b)) for b in blocs), ident


@xfail("P3", "mise en forme et résolution de la condition (D1, D3)")
def test_P3_ex7_mise_en_forme_et_condition():
    m, t = maths(sortie("Ex7")["cartes"]), texte(sortie("Ex7")["cartes"])
    assert "Mise en forme" in t
    for morceau in ("(x+2)(x-1)", "6(x-2)", "g(x)", "6x-12=0", "6x=12", "x=2"):
        assert morceau in m, morceau


@xfail("P3", "résolution de la condition x² − 4 = 0 (D3)")
def test_P3_d_condition():
    m = maths(sortie("d")["cartes"])
    assert "x^{2}-4=0" in m and "x=-2" in m, m


PARITE = {
    "Ex7": ["ni paire ni impaire"], "a": ["f est paire"], "d": ["f est paire"],
    "b": ["ni paire ni impaire", "-0,68", "-36,95"], "c": ["ni paire ni impaire", "8,92", "2,07"],
}
PARITE_MATHS = {"Ex7": [r"-2\in", r"2\notin"], "a": ["(-x)^{2}=x^{2}"], "d": ["(-x)^{2}=x^{2}"], "b": ["f(0)=-6"], "c": ["f(0)=5"]}


@pytest.mark.parametrize("ident", avec(set(IDS), xfail("P4", "parité (D4)")))
def test_P4_parite(ident):
    t, m = texte(sortie(ident)["cartes"]), maths(sortie(ident)["cartes"])
    assert "Parité" in t
    for morceau in PARITE[ident]:
        assert morceau in t, morceau
    for morceau in PARITE_MATHS[ident]:
        assert morceau in m, morceau


def tableau_de_signe_de_f(ident):
    for c in sortie(ident)["cartes"]:
        for b in c["blocs"]:
            if b["type"] == "tableau":
                for l in b.get("rows", []):
                    if l.get("label") == "f(x)" and not l.get("variation"):
                        return [x for x in l["cells"] if x in ("+", "-")]
    return None


@pytest.mark.parametrize("ident", avec(set(IDS), xfail("P5", "zéros, signe et ordonnée à l'origine (D5)")))
def test_P5_zeros_signe_f0(ident):
    fn = PAR_ID[ident]
    t, m = texte(sortie(ident)["cartes"]), maths(sortie(ident)["cartes"])
    assert "strictement positive" in t
    if fn.zeros:
        assert tableau_de_signe_de_f(ident) == fn.signe, tableau_de_signe_de_f(ident)
        for _, _, approx in fn.zeros:
            assert approx.lstrip("-") in m, approx
    else:
        assert "f n'a pas de zéro" in t and "f(x)>0" in m
    assert "f(0)=" in m and fn.f0[2] in m, fn.f0


@pytest.mark.parametrize("ident", avec(set(IDS), xfail("P6", "position du graphe par rapport à l'AH (D13)")))
def test_P6_position_par_rapport_a_l_ah(ident):
    t = texte(sortie(ident)["cartes"])
    assert t.count("au-dessus") >= len(PAR_ID[ident].horizontales), ident


ESSAIS = {"Ex7": ["1,99", "2,01", "-0,06"], "d": ["-2,01", "-1,99", "1,99", "2,01"]}


@pytest.mark.parametrize("ident", [pytest.param(i, id=i, marks=[xfail("P6", "valeur d'essai pour 0⁺ / 0⁻ (D12)")]) for i in ESSAIS])
def test_P6_valeur_d_essai(ident):
    m = maths(sortie(ident)["cartes"])
    for morceau in ESSAIS[ident]:
        assert morceau in m, morceau


@pytest.mark.parametrize("ident", avec({"a", "d"}, xfail("P6", "x → ±∞ regroupés quand les chaînes sont identiques (D16)")))
def test_P6_regroupement_infini(ident):
    m = maths(sortie(ident)["cartes"])
    assert (r"\pm\infty" in m) == PAR_ID[ident].regroupe_infini, ident


@pytest.mark.parametrize("ident", avec({"Ex7", "d"}, xfail("P6", "0⁺ dans la phrase de l'AV et dans le bilan (D13)")))
def test_P6_zero_signe_dans_les_phrases(ident):
    m = maths(sortie(ident)["cartes"])
    assert not re.search(r"f\(x\)(=|\\to)[01]\\\)", m), ident


COTES_AV = {"Ex7": ["seulement du côté droit"], "d": ["seulement du côté gauche", "seulement du côté droit"]}


@pytest.mark.parametrize("ident", [pytest.param(i, id=i, marks=[xfail("P6", "AV d'un seul côté et point exclu (D13)")]) for i in COTES_AV])
def test_P6_av_d_un_seul_cote(ident):
    t, m = texte(sortie(ident)["cartes"]), maths(sortie(ident)["cartes"])
    for morceau in COTES_AV[ident]:
        assert morceau in t, morceau
    assert "rond vide" in t
    for a, y in PAR_ID[ident].ronds_vides:
        assert f"({int(a)};{int(y)})" in m, (a, y)


@xfail("P7a", "dérivée de l'exposant détaillée, sans « (x²)′ = 2x » parasite (D7)")
def test_P7a_derivee_de_l_exposant_ex7():
    t, m = texte(cartes_de("Ex7", "Dérivée")), maths(cartes_de("Ex7", "Dérivée"))
    assert "Dérivée de l'exposant" in t
    assert "(x^{2})'=2x" not in m
    for morceau in ("6x^{2}-24x", "6x(x-4)", "36(x-2)^{2}", r"\frac{x(x-4)}{6(x-2)^{2}}"):
        assert morceau in m, morceau


@pytest.mark.parametrize("ident", [pytest.param(i, id=i, marks=[xfail("P7a", "tableau u, u′, v, v′ (D8)")]) for i in ("Ex7", "b")])
def test_P7a_tableau_u_v(ident):
    blocs = [b for c in cartes_de(ident, "Dérivée") for b in c["blocs"] if b["type"] != "texte"]
    assert any("u'" in "".join(chaines(b)) and "v'" in "".join(chaines(b)) for b in blocs), ident


@xfail("P7a", "on développe d'abord eˣ(6 − eˣ) = 6eˣ − e^{2x} (D7b, reportable)")
def test_P7a_c_developpe_d_abord():
    assert "6e^{x}-e^{2x}" in maths(cartes_de("c", "Dérivée")), maths(cartes_de("c", "Dérivée"))


def tableau_de_variations(ident):
    for c in sortie(ident)["cartes"]:
        for b in c["blocs"]:
            if b["type"] == "tableau" and any(l.get("variation") for l in b.get("rows", [])):
                return b
    return None


@pytest.mark.parametrize("ident", avec(set(IDS), xfail("P7b", "valeurs des extremums dans la ligne f(x) (D10)")))
def test_P7b_valeurs_dans_le_tableau(ident):
    b = tableau_de_variations(ident)
    ligne = next(l for l in b["rows"] if l.get("variation"))
    assert "extremum" not in ligne["cells"], ligne
    contenu = "".join(chaines(b))
    for e in etude(ident)["derivee"]["extrema"]:
        assert e["f_tex"] in contenu, e["f_tex"]


@pytest.mark.parametrize("ident", avec(set(IDS), xfail("P7b", "extremums : point, ≈, raison, global ou non (D11)")))
def test_P7b_extremums(ident):
    fn = PAR_ID[ident]
    t, m = texte(sortie(ident)["cartes"]), maths(sortie(ident)["cartes"])
    for e in fn.extremums:
        assert f"({e.approx_x};{e.approx_y})" in m, (e.approx_x, e.approx_y)
        assert ("Maximum local" if e.genre == "maximum" else "Minimum local") in t
    pas_global = t.lower().count("pas global")
    assert pas_global == sum(1 for e in fn.extremums if not e.global_), pas_global
    assert t.lower().count("global") - pas_global >= sum(1 for e in fn.extremums if e.global_)


def ronds_vides_de_l_outil(r):
    """Ronds vides du graphique : trous des asymptotes (genre « trou ») et liste `ronds_vides` du graphique (ajout prévu en P8)."""
    out = [(a["point_val"], a["valeur_val"]) for a in r["limites"]["asymptotes"] if a["genre"] == "trou"]
    out += [tuple(p) for p in r["graphique"].get("ronds_vides", [])]
    return sorted(out)


@pytest.mark.parametrize("ident", avec({"Ex7", "d"}, xfail("P8", "rond vide à chaque point exclu à limite finie (D15)")))
def test_P8_ronds_vides(ident):
    attendu = sorted((float(a), float(y)) for a, y in PAR_ID[ident].ronds_vides)
    assert ronds_vides_de_l_outil(etude(ident)) == attendu


@pytest.mark.parametrize("ident", avec({"Ex7"}, xfail("P8", "la fenêtre montre l'approche de chaque AH (§3)")))
def test_P8_approche_des_ah_visible(ident):
    """§3 : pour chaque AH y = L en ±∞, un x visible où |f(x) − L| < 5 % de la hauteur de la fenêtre. Le x est pris du côté de
    l'asymptote, au-delà de tous les points à montrer et des valeurs interdites (sinon une branche qui file vers 0 en une valeur
    interdite passerait pour l'approche de l'AH : Ex7 en 2⁻)."""
    fn, g = PAR_ID[ident], etude(ident)["graphique"]
    hauteur = g["ymax"] - g["ymin"]
    reperes = [p[0] for p in points_a_montrer(fn)] + list(fn.exclus)
    for cote, L, _ in fn.horizontales:
        if cote == "-oo":
            a, b = g["xmin"], min(reperes)
        else:
            a, b = max(reperes), g["xmax"]
        xs = [mp.mpf(a) + (mp.mpf(b) - a) * k / 200 for k in range(201)] if b > a else []
        valeurs = [v for v in (valeur(fn, x) for x in xs) if v is not None]
        assert any(abs(v - L) < mp.mpf("0.05") * hauteur for v in valeurs), (ident, cote, a, b)


def exemples_de_la_page():
    with open(os.path.join(RACINE, "etude-complete", "index.html"), encoding="utf-8") as f:
        s = f.read()
    exemples = re.search(r"const EXEMPLES=\[(.*?)\];", s, re.S).group(1)
    exos = re.search(r"const EXOS=\{(.*?)\};", s, re.S).group(1)
    niveaux = {n: re.findall(r'"([^"]+)"', v) for n, v in re.findall(r"(\w+):\[(.*?)\]", exos, re.S)}
    return re.findall(r'"([^"]+)"', exemples), niveaux


def meme_fonction(a, b):
    return tex(lire(a)) == tex(lire(b))


@xfail("P9", "Ex7 en exemple, a–d en exercices difficile / très difficile (D18)")
def test_P9_fonctions_du_corrige_dans_la_page():
    exemples, niveaux = exemples_de_la_page()
    assert any(meme_fonction(PAR_ID["Ex7"].saisie, s) for s in exemples)
    durs = niveaux.get("difficile", []) + niveaux.get("tresDifficile", [])
    for ident in ("a", "b", "c", "d"):
        assert any(meme_fonction(PAR_ID[ident].saisie, s) for s in durs), ident


@pytest.mark.parametrize("ident", avec(set(IDS), xfail("P9", "carte « Bilan de l'étude » (D20)")))
def test_P9_bilan_de_l_etude(ident):
    assert cartes_de(ident, "Bilan de l'étude"), ident


@xfail("P10", "pente au point exclu, « Pour aller plus loin » (D14, facultatif)")
def test_P10_pente_au_point_exclu():
    assert "Pour aller plus loin" in texte(sortie("Ex7")["cartes"])
