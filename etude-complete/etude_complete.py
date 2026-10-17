"""
etude_complete.py — Étude complète d'une fonction : ED, dérivée/signe/variations,
limites/asymptotes, et données pour tracer le graphique.

N'invente pas de nouveau calcul mathématique : assemble les trois modules déjà
construits et testés (ensemble_def, derivee_variations, limites_asymptotes). La
seule pièce réellement nouvelle ici est le cadrage automatique et
l'échantillonnage numérique pour le graphique.
"""
import json
import math

from noyau import json_strict, ajouter_saisie, lire, tex, evaluer, fusion, ErreurSaisie, Incertain, analyser_complet, apercu_json
import derivee_variations as dv
import limites_asymptotes as la

__all__ = ["etudier", "etudier_json", "apercu_json", "fenetre_json"]


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


def _cadrage_et_courbe(f, ED, extrema, asymptotes):
    ivs = fusion(ED)
    interet = _bornes_finies(ED) + [e["x_val"] for e in extrema if e.get("x_val") is not None]
    if not interet:
        interet = [0.0]
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

    # Pour estimer la fenêtre en y, on ignore une bande près des DEUX bords de
    # chaque morceau tracé (asymptote verticale, ou simplement bord de la
    # fenêtre choisie) : sinon la branche qui y file (ou juste une croissance
    # rapide, même sans asymptote) écrase l'échelle et noie les extrema. Le
    # tracé réel (segments) garde lui un échantillonnage fin jusqu'au bord.
    segments = []
    ys = []
    for iv in ivs:
        a = iv.lo.val if iv.lo is not None else xmin
        b = iv.hi.val if iv.hi is not None else xmax
        a, b = max(a, xmin), min(b, xmax)
        if b - a < 1e-6:
            continue
        n = max(10, int(400 * (b - a) / max(xmax - xmin, 1e-9)))
        pts = _echantillonner(f, a, b, n)
        segments.append(pts)
        marge_y = (b - a) * 0.2
        for x, v in pts:
            if v is None:
                continue
            if x - a < marge_y or b - x < marge_y:
                continue
            ys.append(v)
    for e in extrema:
        if e.get("f_val") is not None:
            ys.append(e["f_val"])
    for asym in asymptotes:
        if asym.get("genre") == "horizontale" and asym.get("valeur_val") is not None:
            ys.append(asym["valeur_val"])

    ys = [y for y in ys if math.isfinite(y)]
    if not ys:
        ys = [-1.0, 1.0]
    ylo, yhi = min(ys), max(ys)
    yetendue = max(yhi - ylo, 2.0)
    ymarge = yetendue * 0.25
    ymin, ymax = ylo - ymarge, yhi + ymarge

    return {"xmin": xmin, "xmax": xmax, "ymin": ymin, "ymax": ymax, "segments": segments}


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


def etudier(entree):
    try:
        f = lire(entree)
    except ErreurSaisie as e:
        return {"ok": False, "erreur": str(e)}

    res_ed, _, ED = analyser_complet(entree)
    if not res_ed.get("ok"):
        return {"ok": False, "erreur": res_ed["erreur"]}
    if not res_ed.get("complet"):
        return {"ok": False, "erreur": "L'ensemble de définition n'a pas pu être calculé pour cette fonction."}

    r_dv = dv.etudier(entree)
    if not r_dv.get("ok"):
        return r_dv
    r_la = la.etudier(entree, avec_bornes=True)
    if not r_la.get("ok"):
        return r_la
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
    res["graphique"] = _cadrage_et_courbe(f, ED, r_dv.get("extrema", []), r_la.get("asymptotes", []))
    return res


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
    res_ed, _, ED = analyser_complet(entree)
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
