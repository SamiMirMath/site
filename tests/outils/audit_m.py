"""Audit de la filière M (T35 étape 8, étendu en T36) : corpus généré de formes M, oracle numpy + bissection (indépendant du moteur).
Hors collecte (ni pytest ni unittest ne lisent ce dossier). Lancement, depuis la racine du dépôt :

    uv run -q --no-project --python 3.12 --with sympy==1.13.3 --with mpmath==1.3.0 --with numpy python tests/outils/audit_m.py [famille|-] [max] [sortie.json]

écrit le JSON (par défaut resultats_m.json à côté du script, non versionné) et imprime les effectifs par famille et par verdict. Pour comparer
« avant / après » un chantier : lancer deux fois avec deux fichiers de sortie, puis  python tests/outils/audit_m.py comparer avant.json apres.json.
Verdicts : OK (S = racines dans l'ED), message (le moteur refuse avec un message prévu), FAUX (écart avec l'oracle), exception."""
import json, math, random, sys, collections, itertools, os
sys.path[:0] = [os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "python")]
import numpy as np
import moteurs
import exp_log as el, exp_log_m as elm, resoudre_el as rel

rng = random.Random(20261028)

# ---------------------------------------------------------------- corpus
def lin(p, q):
    t = "x" if p == 1 else "-x" if p == -1 else f"{p}x"
    return t if q == 0 else f"{t}{q:+d}"

def L(base, a):
    return f"log({a})" if base == "10" else f"ln({a})" if base == "e" else f"log_{base}({a})"

familles = collections.defaultdict(list)
BASES = ["10", "e", "2", "3"]
for _ in range(600):                         # sommes
    b = rng.choice(BASES); a1, a2 = rng.randint(-4, 4), rng.randint(-4, 4); c = rng.choice([0, 1, 2, 3]) if b != "e" else rng.choice([0])
    familles["somme"].append(f"{L(b, lin(1, a1))}+{L(b, lin(1, a2))}={c}")
for _ in range(400):                         # différences
    b = rng.choice(BASES); p, q, r, s = rng.randint(1, 3), rng.randint(-3, 6), rng.randint(1, 3), rng.randint(-3, 6); c = rng.choice([0, 1, 2]) if b != "e" else 0
    familles["difference"].append(f"{L(b, lin(p, q))}-{L(b, lin(r, s))}={c}")
for _ in range(500):                         # log = log (+ constante)
    b = rng.choice(BASES); p, q, r, s = rng.randint(-3, 3) or 1, rng.randint(-5, 8), rng.randint(-3, 3) or 1, rng.randint(-5, 8)
    c = rng.choice(["", "+1", "-1", "+2"]) if b != "e" else ""
    familles["egal"].append(f"{L(b, lin(p, q))}={L(b, lin(r, s))}{c}")
for _ in range(400):                         # k·log
    b = rng.choice(BASES); k = rng.choice([2, 3, 4]); p, q, r, s = rng.randint(1, 2), rng.randint(-4, 4), rng.randint(1, 3), rng.randint(-6, 12)
    familles["kfois"].append(f"{k}{L(b, lin(p, q))}={L(b, lin(r, s))}")
    familles["kfois"].append(f"{k}{L(b, 'x')}={L(b, str(rng.randint(2, 30)))}")
for _ in range(300):                         # log(x²) et carrés
    b = rng.choice(["10", "e", "2"]); k = rng.randint(2, 9); c = rng.choice([0, 1, 2, -1]) if b != "e" else 0
    familles["carre"] += [f"{L(b, 'x^2')}+{L(b, str(k))}={c}", f"{L(b, 'x^2')}-{L(b, 'x')}={c}", f"{L(b, 'x^2')}={L(b, lin(rng.randint(1, 4), rng.randint(-3, 6)))}"]
for _ in range(300):                         # trois logarithmes
    b = rng.choice(["10", "2", "e"]); a1, a2, a3 = (rng.randint(-3, 3) for _ in range(3)); k = rng.randint(2, 6)
    familles["trois"].append(f"{L(b, lin(1, a1))}+{L(b, lin(1, a2))}={L(b, lin(1, a3))}+{L(b, str(k))}")
for _ in range(200):                         # ED vide
    a, bb = rng.randint(-6, 2), rng.randint(-4, 4)
    familles["vide"].append(f"log(x+{a})+log({bb}-x)={rng.choice([0, 1])}".replace("+-", "-"))
for _ in range(200):                         # constantes seules à droite, plusieurs logs
    b = rng.choice(["10", "2"]); k = rng.randint(2, 5)
    familles["constantes"].append(f"{L(b, 'x')}={rng.randint(1, 3)}{L(b, str(k))}+{L(b, str(rng.randint(2, 6)))}-{L(b, str(rng.randint(2, 4)))}")
for _ in range(300):                         # changement de variable
    a = rng.choice([2, 3, 5]); t1, t2 = rng.choice([a ** i for i in range(0, 4)]), rng.choice([a ** i for i in range(0, 4)] + [-1, -2, -3, -4])
    s, p = t1 + t2, t1 * t2; k = rng.choice([1, 2, 3])
    sg = lambda v: f"{v:+d}"
    familles["variable"].append(f"{k}*{a*a}^x{sg(-k*s)}*{a}^x{sg(k*p)}=0".replace("+-", "-").replace("-0*", "-0*") if s else f"{k}*{a*a}^x{sg(k*p)}=0")
    familles["variable"].append(f"{a}^(x+{rng.randint(1, 3)})+{a}^(-x)={rng.randint(3, 40)}")
    familles["variable"].append(f"e^(2x){sg(-(t1+abs(t2)))}*e^x{sg(t1*abs(t2))}=0")
for _ in range(300):                         # base inconnue et divers
    m, k = rng.choice([2, 3, 4, 5, 6]), rng.randint(1, 5)
    familles["base"].append(f"log_x({m ** k})={rng.choice([-2, -1, 1, 2, 3, k])}")
    familles["base"].append(f"log(x^2-{rng.randint(1, 9)})=2log(x+{rng.randint(1, 4)})")
# ---------------------------------------------------------------- familles ajoutées en T36 (variantes ln, log et log_a de chaque gabarit)
BASES_T36 = ["10", "e", "2", "3", "0,5"]
for _ in range(400):                         # logarithmes imbriqués, 2 et 3 couches, argument du 1er degré
    b = rng.choice(BASES_T36); c = rng.choice([0, 1, 2, -1]); a = rng.randint(-3, 3); p = rng.choice([1, 1, 2, -1])
    familles["imbriques"].append(f"{L(b, L(b, lin(p, a)))}={c}")
    familles["imbriques"].append(f"{L(b, L(b, L(b, lin(p, a))))}={rng.choice([0, 1])}")
for _ in range(500):                         # exposants c/x, a + b√x, e^(−ln x)
    b = rng.choice(["e", "2", "3", "5"]); c = rng.randint(1, 14); a = rng.randint(-5, 5); n = rng.randint(2, 30)
    exposant_a = f"{c}/x"
    familles["exposants"].append(f"{b}^({exposant_a})={b}^(x{a:+d})".replace("+0)", ")") if a else f"{b}^({exposant_a})={b}^x")
    familles["exposants"].append(f"{b}^(-{rng.randint(1, 4)}/x)={n}")
    familles["exposants"].append(f"{b}^(sqrt(x))={n}")
    familles["exposants"].append(f"{b}^(sqrt(x)+{rng.randint(1, 3)})={n}")
    familles["exposants"].append(f"{b}^(sqrt(x))=-{rng.randint(1, 5)}")
    lg = {"e": "ln", "2": "log_2", "3": "log_3", "5": "log_5"}[b]
    familles["exposants"].append(f"{b}^(-{lg}(x))={rng.choice(['0,2', '3', '0,5', '4', '1/3'])}")
for _ in range(500):                         # base polynomiale log_(px)(n) = k, log_(x+b)(n) = k
    p = rng.choice([2, 3, 4, 5, 6]); k = rng.choice([2, 3, 4, 5]); n = rng.choice([(p * r) ** k for r in (1, 2, 3)] + [rng.randint(2, 40)])
    familles["base_polynomiale"].append(f"log_({p}x)({n})={k}")
    familles["base_polynomiale"].append(f"log_(x{rng.choice([1, 2, 3]):+d})({rng.randint(2, 30)})={rng.choice([2, 3, 4, 16])}")
    familles["base_polynomiale"].append(f"log_({p}x)({n})=-{rng.randint(1, 3)}")
for _ in range(400):                         # bicarrés en t (exposants de t : -3, -1, 1)
    b = rng.choice(["2", "3", "5", "e"]); r1, r2 = rng.randint(1, 4), rng.randint(1, 4)
    u1, u2 = r1 * r1, r2 * r2
    familles["bicarre"].append(f"{u1 * u2}*{b}^(-3x)-{u1 + u2}*{b}^(-x)+{b}^x=0".replace("1*", "", 1) if u1 * u2 == 1 else f"{u1 * u2}*{b}^(-3x)-{u1 + u2}*{b}^(-x)+{b}^x=0")
    familles["bicarre"].append(f"{b}^x+{b}^(-x)-{rng.randint(2, 12)}*{b}^(-3x)=0")
    familles["bicarre"].append(f"{b}^(3x)-{u1 + u2}*{b}^x+{u1 * u2}*{b}^(-x)=0")
for _ in range(400):                         # base inconnue et exposant rationnel log_x(n) = p/q
    q = rng.choice([2, 3, 4]); p = rng.choice([1, 2, 3, 5]) * rng.choice([1, -1]); r = rng.choice([2, 3, 4, 5]); n = r ** q if rng.random() < .7 else rng.choice([5, 6, 7, 10, 12])
    if p % q: familles["base_rationnelle"].append(f"log_x({n})={p}/{q}")
    familles["base_rationnelle"].append(f"log_x({r ** abs(p)})={q}/{abs(p)}")
for _ in range(600):                         # somme de deux logarithmes à second membre rationnel quelconque
    b = rng.choice(["10", "e", "2", "3"]); a = rng.randint(-3, 4); c = rng.choice(["1", "2", "3", "-1", "1/2", "3/2", "5/2", "-1/2"])
    familles["somme_c"].append(f"{L(b, 'x')}+{L(b, lin(1, a))}={c}".replace("+-", "-"))
    familles["somme_c"].append(f"{L(b, lin(1, a))}+{L(b, lin(2, rng.randint(-3, 3)))}={c}".replace("+-", "-"))
for _ in range(300):                         # x^k = c par logarithme
    b = rng.choice(["10", "e", "2"]); k = rng.choice([2, 3, 4, 5]); c = rng.choice(["1", "2", "3", "1/2", "-1"])
    familles["puissance_c"].append(f"{L(b, f'x^{k}')}={c}")
    familles["puissance_c"].append(f"{k}{L(b, 'x')}={c}")
for _ in range(300):                         # produits x^k (a + b log x) = 0
    b = rng.choice(["10", "e", "2"]); a, c = rng.randint(1, 6), rng.randint(1, 4); k = rng.choice([1, 2])
    xk = "x" if k == 1 else "x^2"
    familles["produit"] += [f"{xk}-{xk}*{L(b, 'x')}=0", f"{a}{xk}-{c}{xk}*{L(b, 'x')}=0", f"{xk}*{L(b, 'x')}+{a}{xk}=0", f"{xk}*{L(b, 'x')}={xk}"]
familles["isoles"] += ["7^(8x^2+4)=7^((2-3x)^2)", "7^(8x^2+4)=7^(2-3x)^2", "2^(x^2+1)=2^((x+1)^2)", "3^(x^2)=3^((x-2)^2)",
                       "log(x)=(log(20)+log(100)-log(2))/(log(5000)-log(5)+log(0,1))", "log(x)=(log(20)+log(5))/(log(50)-log(5))",
                       "e^x=pi", "e^x=3pi", "log(sqrt(x))=sqrt(log(x))", "x*ln(x)=1", "ln(x)=x"]
ITEMS = [(f, e) for f, es in familles.items() for e in dict.fromkeys(es)]

# ---------------------------------------------------------------- oracle numpy
GRILLE = np.unique(np.concatenate([np.arange(-60, 60, 0.0031) + 1e-4, np.geomspace(1e-6, 1e8, 3000), -np.geomspace(1e-6, 1e8, 3000)]))

def ev(n, x):
    with np.errstate(all="ignore"):
        if isinstance(n, el.Nb): return np.full_like(x, float(n.val))
        if isinstance(n, el.Var): return x
        if isinstance(n, el.E): return np.full_like(x, math.e)
        if isinstance(n, el.Neg): return -ev(n.a, x)
        if isinstance(n, el.Fn): return np.sqrt(ev(n.a, x))
        if isinstance(n, el.Pow):
            a, b = ev(n.a, x), ev(n.b, x)
            return np.where(a > 0, np.power(np.where(a > 0, a, 1.0), b), np.where((a < 0) & (b == np.round(b)), np.power(a, b), np.nan))
        if isinstance(n, el.Op):
            a, b = ev(n.a, x), ev(n.b, x)
            return a + b if n.op == "+" else a - b if n.op == "-" else a * b if n.op == "*" else np.where(b != 0, a / np.where(b != 0, b, 1), np.nan)
        if isinstance(n, el.Log):
            a = ev(n.a, x); base = np.full_like(x, 10.0) if n.base is None else ev(n.base, x)
            ok = (a > 0) & (base > 0) & (base != 1)
            return np.where(ok, np.log(np.where(a > 0, a, 1.0)) / np.log(np.where(ok, base, 2.0)), np.nan)
    raise TypeError(n)

def racines_numeriques(s):
    f = lambda x: ev(s.g, x) - ev(s.d, x)
    grille = GRILLE
    v = f(grille)
    # bords de l'ensemble de définition : la grille est resserrée du côté défini (une racine peut être à 10⁻³ du bord, log(x) − log(3x − 1) = 2)
    bords = np.where(np.isnan(v[:-1]) != np.isnan(v[1:]))[0]
    if len(bords):
        pas = np.geomspace(1e-9, 3e-3, 60)
        extra = [grille[i] + pas if np.isnan(v[i]) else grille[i + 1] - pas for i in bords[:40]]
        grille = np.unique(np.concatenate([grille] + extra))
        v = f(grille)
    sol = []
    idx = np.where(np.isfinite(v[:-1]) & np.isfinite(v[1:]) & (v[:-1] * v[1:] <= 0))[0]
    for i in idx:
        a, b = grille[i], grille[i + 1]; fa = float(v[i])
        if fa == 0: sol.append(a); continue
        for _ in range(100):
            m = (a + b) / 2; fm = float(f(np.array([m]))[0])
            if not math.isfinite(fm): break
            if fa * fm <= 0: b = m
            else: a, fa = m, fm
        else:
            r = (a + b) / 2; fr = float(f(np.array([r]))[0])
            sc = max(abs(float(ev(s.g, np.array([r]))[0])), abs(float(ev(s.d, np.array([r]))[0])), 1.0)
            if math.isfinite(fr) and abs(fr) < 1e-7 * sc: sol.append(r)
    # racines tangentes (double : pas de changement de signe) : les dix plus petits minima locaux de |f|, affinés par recherche ternaire
    a_ = np.abs(v)
    minima = np.where(np.isfinite(a_[1:-1]) & (a_[1:-1] <= a_[:-2]) & (a_[1:-1] <= a_[2:]))[0] + 1
    for i in minima[np.argsort(a_[minima])[:10]]:
        lo, hi = grille[i - 1], grille[i + 1]
        for _ in range(70):
            m1, m2 = lo + (hi - lo) / 3, hi - (hi - lo) / 3
            f1, f2 = abs(float(f(np.array([m1]))[0])), abs(float(f(np.array([m2]))[0]))
            if not (math.isfinite(f1) and math.isfinite(f2)): break
            lo, hi = (lo, m2) if f1 < f2 else (m1, hi)
        r = (lo + hi) / 2; fr = float(f(np.array([r]))[0])
        sc = max(abs(float(ev(s.g, np.array([r]))[0])), abs(float(ev(s.d, np.array([r]))[0])), 1.0)
        if math.isfinite(fr) and abs(fr) < 1e-9 * sc and not any(abs(r - t) < 1e-6 * (1 + abs(r)) for t in sol): sol.append(r)
    out = []
    for r in sorted(sol):
        if not out or abs(r - out[-1]) > 1e-6 * (1 + abs(r)): out.append(r)
    return out

def solutions_du_moteur(e):
    s = el.analyser_saisie(e)
    v = elm.variantes_changement(s.g, s.d, s.inconnue)
    if v is not None: return s, v[el.METHODE_LOGARITHMES]
    r = elm.corriger_equation(s.g, s.d, s.inconnue)
    if r is None:                                # équation exponentielle de la 3C : résolue sans ensemble de définition
        v = el.variantes_equation(s.g, s.d, s.inconnue, s.parametres)
        r = v[el.METHODE_LOGARITHMES] if v is not None else el.corriger_equation(s.g, s.d, s.inconnue, parametres=s.parametres)
    return s, r

def verdict(e):
    try:
        out = rel.resoudre(e, "M")
    except Exception as ex:
        return "exception", f"{type(ex).__name__}: {ex}"
    if not out["ok"]:
        return "message", out["erreur"]
    s, r = solutions_du_moteur(e)
    if r is None: return "autre", "sortie ok sans résultat M"
    if r["solutions"] is None: return "OK", "S = ED"
    mot = sorted(el.valeur(n) for n in r["solutions"])
    num = racines_numeriques(s)
    # une racine du moteur hors de la grille (|x| > 1e7) est contrôlée en la substituant : f(r) ≈ 0
    lointaines = [r for r in mot if abs(r) > 1e7]
    mot_grille = [r for r in mot if abs(r) <= 1e7]
    if all(abs(float(ev(s.g, np.array([r]))[0]) - float(ev(s.d, np.array([r]))[0])) < 1e-6 * (1 + abs(float(ev(s.d, np.array([r]))[0]))) for r in lointaines):
        mot = mot_grille
        num = [r for r in num if abs(r) <= 1e7]
    if len(mot) == len(num) and all(abs(a - b) < 1e-5 * (1 + abs(a)) for a, b in zip(mot, num)): return "OK", ""
    return "FAUX", f"moteur {mot} / oracle {num}"

def comparer(avant, apres):
    """Tableau avant / après par famille, et la liste des entrées dont le verdict change (surtout message → OK ; tout FAUX ou exception est signalé)."""
    a, b = json.load(open(avant)), json.load(open(apres))
    compte = collections.defaultdict(lambda: collections.Counter())
    for e, (f, v, _) in b.items():
        compte[f][(a.get(e, [f, "absent", ""])[1], v)] += 1
    for f in sorted(compte):
        print(f"{f:18s}", {f"{x}→{y}": n for (x, y), n in sorted(compte[f].items())})
    graves = [(e, b[e]) for e in b if b[e][1] in ("FAUX", "exception", "autre")]
    print("FAUX / exception / autre après :", len(graves))
    for e, r in graves[:40]:
        print("  ", e, r)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "comparer":
        comparer(sys.argv[2], sys.argv[3])
        sys.exit(0)
    filtre = sys.argv[1] if len(sys.argv) > 1 and sys.argv[1] != "-" else None
    maxi = int(sys.argv[2]) if len(sys.argv) > 2 and sys.argv[2] != "-" else None
    sortie = sys.argv[3] if len(sys.argv) > 3 else os.path.join(os.path.dirname(os.path.abspath(__file__)), "resultats_m.json")
    items = [(f, e) for f, e in ITEMS if filtre is None or f == filtre][:maxi]
    res, compte = {}, collections.Counter()
    for f, e in items:
        v, d = verdict(e)
        res[e] = [f, v, d]; compte[(f, v)] += 1
    json.dump(res, open(sortie, "w"), ensure_ascii=False, indent=1)
    for f in sorted({f for f, _ in items}):
        print(f"{f:12s}", {v: n for (g, v), n in sorted(compte.items()) if g == f})
    print("TOTAL", len(items), {v: sum(n for (g, w), n in compte.items() if w == v) for v in ("OK", "message", "FAUX", "exception", "autre")})
