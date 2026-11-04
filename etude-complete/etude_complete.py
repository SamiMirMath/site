"""
etude_complete.py — Étude complète d'une fonction : ED, dérivée/signe/variations,
limites/asymptotes, et données pour tracer le graphique.

N'invente pas de nouveau calcul mathématique : assemble les trois modules déjà
construits et testés (ensemble_def, derivee_variations, limites_asymptotes) et les
parties propres à l'Étude complète (parties.py : zéros et f(0) de la partie 3, ronds
vides, chacun avec ses garde-fous). La seule pièce réellement nouvelle ici est le
cadrage automatique et l'échantillonnage numérique pour le graphique (D15).
"""
import json
import math
from functools import lru_cache

from noyau import (json_strict, ajouter_saisie, lire, tex, evaluer, fusion, proche, ErreurSaisie, Incertain, analyser_complet, apercu_json,
                   SYMPY)
import derivee_variations as dv
import limites_asymptotes as la
import parties

__all__ = ["etudier", "etude_et_partie3", "etudier_json", "apercu_json", "fenetre_json", "vider_cache"]


def _bornes_finies(ED):
    pts = []
    for iv in fusion(ED):
        if iv.lo is not None:
            pts.append(iv.lo.val)
        if iv.hi is not None:
            pts.append(iv.hi.val)
    return pts


def _echantillonner(f, a, b, n):
    if b - a < 1e-9:
        return []
    pad = (b - a) * 0.004
    pts = []
    for i in range(n):
        x = a + pad + (b - a - 2 * pad) * i / (n - 1) if n > 1 else (a + b) / 2
        try:
            v = evaluer(f, x)
        except (Incertain, OverflowError):
            v = None  # valeur hors de portée des flottants (e^800…) : point omis
        pts.append([x, v if (v is not None and abs(v) < 1e7) else None])
    return pts


APPROCHE = 0.05             # decisions.md §3 : un x visible où |f(x) − L| < 5 % de la hauteur de la fenêtre, pour chaque AH y = L
ELARGIR = 0.25              # côté d'une AH élargi de 25 % de la largeur de la fenêtre…
ELARGISSEMENTS = 6          # … au plus 6 fois (fenêtre au plus 3,8 fois plus large) ; sinon le cadrage sans élargissement
TRACE_AU_DELA = 1.0         # courbe tracée sur une largeur de fenêtre de plus de chaque côté (voir _cadrage_et_courbe)


def _fenetre_x(ivs, interet):
    """[xmin ; xmax] autour des abscisses d'intérêt (marge d'une demi-étendue, étendue d'au moins 4), coupée près d'une borne finie
    de l'ED aux extrémités."""
    lo, hi = min(interet), max(interet)
    etendue = max(hi - lo, 4.0)
    marge = etendue * 0.5
    xmin, xmax = lo - marge, hi + marge
    if ivs and ivs[0].lo is not None:
        xmin = max(xmin, ivs[0].lo.val - etendue * 0.15)
    if ivs and ivs[-1].hi is not None:
        xmax = min(xmax, ivs[-1].hi.val + etendue * 0.15)
    if xmax - xmin < 2.0:
        milieu = (xmax + xmin) / 2
        xmin, xmax = milieu - 1.0, milieu + 1.0
    return xmin, xmax


def _morceaux(f, ivs, a0, b0, largeur):
    """Courbe sur [a0 ; b0] : [(a, b, points)], un morceau [a ; b] par intervalle de l'ED, 400 points par `largeur` (celle de la
    fenêtre)."""
    out = []
    for iv in ivs:
        a = iv.lo.val if iv.lo is not None else a0
        b = iv.hi.val if iv.hi is not None else b0
        a, b = max(a, a0), min(b, b0)
        if b - a < 1e-6:
            continue
        out.append((a, b, _echantillonner(f, a, b, max(10, int(400 * (b - a) / max(largeur, 1e-9))))))
    return out


def _courbe_et_hauteur(f, ivs, xmin, xmax, ys_interet):
    """(segments, ymin, ymax) pour la fenêtre [xmin ; xmax].

    Pour estimer la fenêtre en y, on ignore une bande près des DEUX bords de chaque morceau tracé (asymptote verticale, ou simplement
    bord de la fenêtre choisie) : sinon la branche qui y file (ou juste une croissance rapide, même sans asymptote) écrase l'échelle et
    noie les extrema. Les autres échantillons sont ramenés dans [min − e ; max + e] des ordonnées d'intérêt (points à montrer, AH ;
    e = max(étendue / 4 ; 1)) : une branche qui file vers ±∞ au-delà des points à montrer ne fixe pas l'échelle (c : y allait de −51 à
    21 pour des points entre 0 et 9). Le tracé réel (segments) garde lui un échantillonnage fin jusqu'au bord."""
    morceaux = _morceaux(f, ivs, xmin, xmax, xmax - xmin)
    segments = [pts for _, _, pts in morceaux]
    ys = []
    for a, b, pts in morceaux:
        marge_y = (b - a) * 0.2
        for x, v in pts:
            if v is None:
                continue
            if x - a < marge_y or b - x < marge_y:
                continue
            ys.append(v)
    ys = [y for y in ys if math.isfinite(y)]
    interet = [y for y in ys_interet if y is not None and math.isfinite(y)]
    if interet:
        bas, haut = min(interet), max(interet)
        e = max((haut - bas) / 4, 1.0)
        ys = [min(max(y, bas - e), haut + e) for y in ys] + interet
    if not ys:
        ys = [-1.0, 1.0]
    ylo, yhi = min(ys), max(ys)
    yetendue = max(yhi - ylo, 2.0)
    ymarge = yetendue * 0.25
    return segments, ylo - ymarge, yhi + ymarge


def _approche_visible(segments, L, sens, repere, hauteur):
    """§3 : un échantillon du côté de l'AH (sens −1 : x ≤ repère, +1 : x ≥ repère), au-delà de tous les points à montrer et des
    valeurs interdites (repère), à moins de 5 % de la hauteur de la fenêtre de L (lecture retenue, question 3 de suivi.md)."""
    return any(v is not None and sens * (x - repere) >= 0 and abs(v - L) < APPROCHE * hauteur for seg in segments for x, v in seg)


def _cadrage_et_courbe(f, ED, extrema, asymptotes, points=(), ronds=()):
    """Fenêtre et courbe du graphique (D15, decisions.md §3). La fenêtre contient les points à montrer : extremums, `points` (zéros et
    (0 ; f(0)), donnés par la partie 3), `ronds` (ronds vides), les trous de l'outil Limites et les bornes finies de l'ED ; pour
    chaque AH y = L en ±∞, le côté de
    l'AH est élargi (25 % de la largeur à chaque fois, 6 fois au plus) jusqu'à ce qu'un échantillon au-delà de tous ces points soit à
    moins de 5 % de la hauteur de L ; si cela n'arrive pas, la fenêtre reste celle des points à montrer."""
    ivs = fusion(ED)
    trous = [(a.get("point_val"), a.get("valeur_val")) for a in asymptotes if a.get("genre") == "trou"]
    montres = [(e.get("x_val"), e.get("f_val")) for e in extrema] + [(p["x_val"], p["f_val"]) for p in points] + \
              [(x, y) for x, y in ronds] + trous
    interet = _bornes_finies(ED) + [x for x, _ in montres if x is not None]
    if not interet:
        interet = [0.0]
    ys_interet = [y for _, y in montres]
    ah = []
    for asym in asymptotes:
        if asym.get("genre") == "horizontale" and asym.get("valeur_val") is not None:
            ys_interet.append(asym["valeur_val"])
            ah.append((1 if asym.get("ou", "").endswith(r"+\infty") else -1, asym["valeur_val"]))
    reperes = {-1: min(interet), 1: max(interet)}
    depart = _fenetre_x(ivs, interet)
    xmin, xmax = depart
    for _ in range(ELARGISSEMENTS + 1):
        segments, ymin, ymax = _courbe_et_hauteur(f, ivs, xmin, xmax, ys_interet)
        manquent = {sens for sens, L in ah if not _approche_visible(segments, L, sens, reperes[sens], ymax - ymin)}
        if not manquent:
            break
        largeur = xmax - xmin
        xmin -= ELARGIR * largeur if -1 in manquent else 0
        xmax += ELARGIR * largeur if 1 in manquent else 0
    else:
        xmin, xmax = depart
        segments, ymin, ymax = _courbe_et_hauteur(f, ivs, xmin, xmax, ys_interet)
    # À échelle égale (commun/graphique.js), l'écran montre souvent plus large que [xmin ; xmax] (c : x de −5 à 7 à 360 px pour une
    # fenêtre de −2 à 3,8) : la courbe est tracée une largeur de plus de chaque côté, pour que la fin de l'approche d'une AH se voie
    # au lieu d'un vide. La fenêtre (et donc le cadrage) ne change pas.
    largeur = xmax - xmin
    segments = [pts for _, _, pts in _morceaux(f, ivs, xmin - TRACE_AU_DELA * largeur, xmax + TRACE_AU_DELA * largeur, largeur)]
    return {"xmin": xmin, "xmax": xmax, "ymin": ymin, "ymax": ymax, "segments": segments,
            "points": [dict(p) for p in points], "ronds_vides": [list(r) for r in ronds]}


def points_marques(partie3, extrema):
    """D15 : les zéros et (0 ; f(0)) de la partie 3 (ceux que ses cartes écrivent : rien en cas de doute), sans ceux qui sont déjà
    marqués comme extremums (Ex7 : (0 ; f(0)) est le maximum) ni les doublons (x²e^{−x} : le zéro 0 est aussi (0 ; f(0)))."""
    candidats = [(z, 0.0) for z in partie3["zeros"]] + ([(0.0, partie3["f0"])] if partie3["f0"] is not None else [])
    out = []
    for x, y in candidats:
        deja = [(e.get("x_val"), e.get("f_val")) for e in extrema] + [(p["x_val"], p["f_val"]) for p in out]
        if not any(a is not None and b is not None and proche(x, a) and proche(y, b) for a, b in deja):
            out.append({"x_val": x, "f_val": y})
    return out


def limites_du_tableau(table, bornes):
    """T06c : limites à écrire sur la ligne f(x) du tableau de variations. Les valeurs sont celles de la
    partie Limites (`bornes`, même calcul) ; ici on ne fait que les placer.
    - colonnes : pour chaque valeur interdite (double barre), la limite à gauche et à droite, `None` du
      côté d'une zone hors de l'ED (hachurée) ;
    - moins_inf / plus_inf : limite en −∞ / +∞ quand l'ED y va ;
    - non_determinees : bornes (tex) dont la limite est « ? » (phrase sous le tableau)."""
    cells = next(l["cells"] for l in table["rows"] if l.get("variation"))
    crit = table["crit"]
    res = {"colonnes": [], "moins_inf": None, "plus_inf": None, "non_determinees": []}
    for b in bornes:
        if b["type"] == "inf":
            res["moins_inf" if b["signe"] < 0 else "plus_inf"] = b["tex"]
            if b["tex"] == "?":
                res["non_determinees"].append(r"-\infty" if b["signe"] < 0 else r"+\infty")
            continue
        if b["point_tex"] not in crit:
            continue
        j = 2 * crit.index(b["point_tex"]) + 1
        col = {"j": j, "gauche": None, "droite": None}
        for cote, voisine, signe in (("gauche", j - 1, "-"), ("droite", j + 1, "+")):
            if b.get(cote) is not None and cells[voisine] != "x":
                col[cote] = b[cote]
                if b[cote] == "?":
                    res["non_determinees"].append(f"{b['point_tex']}^{{{signe}}}")
        res["colonnes"].append(col)
    return res


@lru_cache(maxsize=16)
def _analyse_en_cache(saisie, avec_sympy):
    """D19, EC-02 : l'analyse (ED) d'une saisie n'est calculée qu'une fois, pour etudier() (et les outils Dérivée et Limites qu'elle
    appelle) comme pour chaque fenetre() du zoom. `avec_sympy` fait partie de la clé : un résultat obtenu sans SymPy n'est jamais
    resservi une fois SymPy chargé. Le résultat est partagé : personne ne le modifie."""
    return analyser_complet(saisie)


def _cle(entree):
    return " ".join(str(entree).split()), "sp" in SYMPY


def analyse(entree):
    """analyser_complet(entree), en cache par entrée normalisée (espaces réduits : ils ne font que séparer les symboles)."""
    return _analyse_en_cache(*_cle(entree))


def vider_cache():
    _analyse_en_cache.cache_clear()


def etude_et_partie3(entree):
    """(résultat d'etudier(), partie 3 ou None) : la partie 3 (zéros, signe, f(0) : `parties.partie3`) est calculée une seule fois
    par étude ; `etudier()` en prend les zéros et f(0) pour le graphique (D15), `resoudre` les cartes (pas de second calcul)."""
    try:
        f = lire(entree)
    except ErreurSaisie as e:
        return {"ok": False, "erreur": str(e)}, None

    a = analyse(entree)
    res_ed, _, ED = a
    if not res_ed.get("ok"):
        return {"ok": False, "erreur": res_ed["erreur"]}, None
    if not res_ed.get("complet"):
        return {"ok": False, "erreur": "L'ensemble de définition n'a pas pu être calculé pour cette fonction."}, None

    r_dv = dv.etudier(entree, analyse=a)
    if not r_dv.get("ok"):
        return r_dv, None
    r_la = la.etudier(entree, avec_bornes=True, analyse=a)
    if not r_la.get("ok"):
        return r_la, None
    bornes = r_la.pop("limites_bornes")    # hors de la partie Limites, qui reste celle de l'outil séparé

    res = {
        "ok": True,
        "f_tex": tex(f),
        "ed_tex": res_ed["ED_tex"],
        "derivee": r_dv,
        "limites": r_la,
    }
    ajouter_saisie(res, f)
    if r_dv.get("signe_resolu"):
        res["variations_limites"] = limites_du_tableau(r_dv["table_signe"], bornes)
    extrema, asymptotes = r_dv.get("extrema", []), r_la.get("asymptotes", [])
    p3 = parties.partie3(a)                                                     # zéros et f(0) : ceux des cartes de la partie 3
    ronds = parties.ronds_vides(a, bornes, asymptotes)                          # D15 : points exclus à limite finie
    res["graphique"] = _cadrage_et_courbe(f, ED, extrema, asymptotes, points_marques(p3, extrema), ronds)
    return res, p3


def etudier(entree):
    return etude_et_partie3(entree)[0]


def etudier_json(entree):
    return json_strict(etudier(entree))


def fenetre(entree, xmin, xmax, n_total=500):
    """Rééchantillonne f sur une fenêtre [xmin, xmax] donnée (zoom/déplacement du
    graphique) : mêmes coupures par morceau de l'ED que le cadrage initial, sans
    refaire tout le reste de l'étude. `n_total` est le nombre de points visé pour
    toute la fenêtre — à appeler avec la fenêtre VISIBLE (pas une zone élargie en
    cache), sinon la densité près du centre s'appauvrit quand on dézoome."""
    try:
        f = lire(entree)
    except ErreurSaisie as e:
        return {"ok": False, "erreur": str(e)}
    res_ed, _, ED = analyse(entree)                 # en cache : l'ED n'est pas recalculé à chaque zoom (EC-02)
    if not res_ed.get("ok") or not res_ed.get("complet"):
        return {"ok": False, "erreur": "ED indisponible."}
    segments = []
    for iv in fusion(ED):
        a = iv.lo.val if iv.lo is not None else xmin
        b = iv.hi.val if iv.hi is not None else xmax
        a, b = max(a, xmin), min(b, xmax)
        if b - a < 1e-6:
            continue
        n = max(10, int(n_total * (b - a) / max(xmax - xmin, 1e-9)))
        segments.append(_echantillonner(f, a, b, n))
    return {"ok": True, "segments": segments}


def fenetre_json(arg_json):
    p = json.loads(arg_json)
    return json_strict(fenetre(p["f"], p["xmin"], p["xmax"], p.get("n", 500)))


if __name__ == "__main__":
    import sys
    for arg in sys.argv[1:] or ["(x^2-1)/(x-3)"]:
        r = etudier(arg)
        print(json.dumps({k: v for k, v in r.items() if k != "derivee" and k != "limites"},
                         ensure_ascii=False, indent=2))
        print("=" * 60)
