"""
etude_complete.py — Étude complète d'une fonction : ED, dérivée/signe/variations,
limites/asymptotes, et données pour tracer le graphique.

N'invente pas de nouveau calcul mathématique : assemble les trois modules déjà
construits et testés (ensemble_def, derivee_variations, limites_asymptotes). La
seule pièce réellement nouvelle ici est le cadrage automatique et
l'échantillonnage numérique pour le graphique.
"""
import json

from ensemble_def import lire, tex, evaluer, fusion, ErreurSaisie, _analyser, apercu_json
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
        v = evaluer(f, x)
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

    if not ys:
        ys = [-1.0, 1.0]
    ylo, yhi = min(ys), max(ys)
    yetendue = max(yhi - ylo, 2.0)
    ymarge = yetendue * 0.25
    ymin, ymax = ylo - ymarge, yhi + ymarge

    return {"xmin": xmin, "xmax": xmax, "ymin": ymin, "ymax": ymax, "segments": segments}


def etudier(entree):
    try:
        f = lire(entree)
    except ErreurSaisie as e:
        return {"ok": False, "erreur": str(e)}

    res_ed, _, ED = _analyser(entree)
    if not res_ed.get("ok"):
        return {"ok": False, "erreur": res_ed["erreur"]}
    if not res_ed.get("complet"):
        return {"ok": False, "erreur": "L'ensemble de définition n'a pas pu être calculé pour cette fonction."}

    r_dv = dv.etudier(entree)
    if not r_dv.get("ok"):
        return r_dv
    r_la = la.etudier(entree)
    if not r_la.get("ok"):
        return r_la

    res = {
        "ok": True,
        "f_tex": tex(f),
        "ed_tex": res_ed["ED_tex"],
        "derivee": r_dv,
        "limites": r_la,
    }
    res["graphique"] = _cadrage_et_courbe(f, ED, r_dv.get("extrema", []), r_la.get("asymptotes", []))
    return res


def etudier_json(entree):
    return json.dumps(etudier(entree), ensure_ascii=False)


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
    res_ed, _, ED = _analyser(entree)
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
    return json.dumps(fenetre(p["f"], p["xmin"], p["xmax"], p.get("n", 500)), ensure_ascii=False)


if __name__ == "__main__":
    import sys
    for arg in sys.argv[1:] or ["(x^2-1)/(x-3)"]:
        r = etudier(arg)
        print(json.dumps({k: v for k, v in r.items() if k != "derivee" and k != "limites"},
                         ensure_ascii=False, indent=2))
        print("=" * 60)
