"""Banc du graphique de l'Étude complète (T19) : prouve qu'un changement de code ne modifie pas le dessin.

Trois niveaux de preuve, du plus strict au plus lâche :
  1. trace des appels canvas : chaque appel de CanvasRenderingContext2D (méthodes et propriétés écrites) avec ses
     arguments arrondis à 1e-4 ; le dessin n'utilise pas measureText, donc la trace ne dépend d'aucune police et
     son empreinte est versionnée (references/graphique-traces.json) et rejouée en CI ;
  2. pixels du canvas seul (toDataURL), comparés à la machine : jamais versionnés, le rendu change d'une machine à l'autre ;
  3. captures de page entière (captures.py), avec une tolérance propre à la page.

Chaque scénario = une fonction × une vue (largeur, thème, devicePixelRatio) × un état (tracé initial, boutons,
molette, glisser, pincer, impression). Le canvas a une largeur CSS fixe par vue : la trace ne dépend pas de la mise en
page. Molette, glisser et pincer passent par le protocole DevTools (événements réels : un événement synthétique ferait
échouer setPointerCapture).

    uv run -q --no-project --python 3.12 --with sympy==1.13.3 --with websockets --with pillow \
        python tests/pages/graphique.py enregistrer /chemin/avant [complet]
    … python tests/pages/graphique.py comparer /chemin/avant /chemin/apres
    … python tests/pages/graphique.py bruit 10 /chemin/bruit [complet]      # mesure : le même code, plusieurs fois
    … python tests/pages/graphique.py references [dossier]                 # réécrit references/graphique-traces.json

Matrice « suite » (test_graphique.py, CI comprise) : 3 fonctions × 2 vues × 8 états. Matrice « complet » (local) :
6 fonctions × 4 vues × 8 états."""
import base64
import hashlib
import json
import os
import re
import sys
import time

sys.path.insert(0, os.path.dirname(__file__))
from navigateur import Navigateur
from rendu import attendre_pret

REFERENCES = os.path.join(os.path.dirname(__file__), "references", "graphique-traces.json")
PAGE = "etude-complete/index.html"

FONCTIONS_SUITE = ["x^2*e^(-x)", "e^(1/x)", "(x^2-1)/(x-1)"]          # extrema ; asymptote verticale ; trou
FONCTIONS_COMPLET = FONCTIONS_SUITE + ["(x^2-1)/(x-3)", "ln(x^2-4)", "x^3-3x"]       # + oblique ; zone hachurée ; extrema entiers
# vue : (largeur de fenêtre, sombre, devicePixelRatio, largeur CSS du canvas)
VUES = {"clair": (1100, False, 1, 700), "360-sombre": (360, True, 1, 300),
        "sombre": (1100, True, 1, 700), "360": (360, False, 1, 300), "dpr2": (1100, False, 2, 700)}
VUES_SUITE = ["clair", "360-sombre"]
VUES_COMPLET = ["clair", "sombre", "360", "dpr2"]
ETATS = ["initial", "plus", "moins", "reset", "molette", "glisser", "pincer", "impression"]

# Injecté avant tout script de la page : enregistre tout ce qui est écrit sur le contexte 2D du canvas.
JS_TRACE = r"""
(() => {
  window.__trace = [];
  const T = window.__trace;
  const ser = v => Array.isArray(v) ? v.map(ser) : typeof v === 'number' ? (Number.isFinite(v) ? Math.round(v * 1e4) / 1e4 : String(v)) : (typeof v === 'object' && v !== null ? String(v) : v);
  const P = CanvasRenderingContext2D.prototype;
  for (const nom of Object.getOwnPropertyNames(P)) {
    if (nom === 'constructor' || nom === 'canvas') continue;
    const d = Object.getOwnPropertyDescriptor(P, nom);
    if (typeof d.value === 'function') {
      Object.defineProperty(P, nom, { ...d, value: function (...a) { T.push([nom, ...a.map(ser)]); return d.value.apply(this, a); } });
    } else if (d.set) {
      Object.defineProperty(P, nom, { ...d, set: function (v) { T.push(['=' + nom, ser(v)]); d.set.call(this, v); } });
    }
  }
  for (const nom of ['width', 'height']) {
    const d = Object.getOwnPropertyDescriptor(HTMLCanvasElement.prototype, nom);
    Object.defineProperty(HTMLCanvasElement.prototype, nom, { ...d, set: function (v) { T.push(['size.' + nom, ser(v)]); d.set.call(this, v); } });
  }
  window.print = () => {};          // l'impression réelle bloquerait ; le clic sur « PDF » redessine déjà en clair avant d'appeler print()
})();
"""


def slug(f):
    return re.sub(r"[^A-Za-z0-9]+", "_", f).strip("_")


def attendre_calme(page, calme=0.8, delai=60):
    """Attend que plus aucun appel canvas n'arrive pendant `calme` secondes (rééchantillonnage terminé)."""
    fin, dernier, depuis = time.time() + delai, -1, time.time()
    while time.time() < fin:
        n = page.evaluer("window.__trace.length")
        if n != dernier:
            dernier, depuis = n, time.time()
        elif time.time() - depuis >= calme:
            return
        time.sleep(0.15)
    raise TimeoutError("le graphique ne se stabilise pas")


def calculer(page, entree):
    page.evaluer("document.querySelector('#cartes').innerHTML = ''")
    page.evaluer(f"document.querySelector('#entree').value = {json.dumps(entree)}; document.querySelector('#calculer').click()")
    page.attendre("document.querySelector('#cartes').children.length > 0 && !document.querySelector('#calculer').disabled", 120)
    page.evaluer("document.querySelector('#tout').click()")
    page.attendre("!document.querySelector('#cartes .cache') && document.querySelector('#graphique')", 20)


def centre(page):
    return page.evaluer("""(() => { const cv = document.querySelector('#graphique'); cv.scrollIntoView({ block: 'center' });
        const r = cv.getBoundingClientRect(); return { x: r.left + r.width / 2, y: r.top + r.height / 2, w: r.width, h: r.height }; })()""")


def cliquer(page, selecteur):
    page.evaluer(f"document.querySelector({selecteur!r}).click()")


def molette(page):
    c = centre(page)
    for dy in (-100, -100):
        page.appel("Input.dispatchMouseEvent", type="mouseWheel", x=c["x"] + 60, y=c["y"] - 30, deltaX=0, deltaY=dy)


def glisser(page):
    c = centre(page)
    x, y = c["x"] - 40, c["y"]
    page.appel("Input.dispatchMouseEvent", type="mouseMoved", x=x, y=y)
    page.appel("Input.dispatchMouseEvent", type="mousePressed", x=x, y=y, button="left", buttons=1, clickCount=1)
    for i in range(1, 7):
        page.appel("Input.dispatchMouseEvent", type="mouseMoved", x=x + 20 * i, y=y + 8 * i, button="left", buttons=1)
    page.appel("Input.dispatchMouseEvent", type="mouseReleased", x=x + 120, y=y + 48, button="left", buttons=0, clickCount=1)


def pincer(page):
    c = centre(page)
    page.appel("Emulation.setTouchEmulationEnabled", enabled=True, maxTouchPoints=2)
    pts = lambda d, dx=0: [{"x": c["x"] - d + dx, "y": c["y"], "id": 0}, {"x": c["x"] + d + dx, "y": c["y"], "id": 1}]
    page.appel("Input.dispatchTouchEvent", type="touchStart", touchPoints=pts(30))
    for d, dx in ((40, 0), (55, 10), (70, 20), (85, 30)):
        page.appel("Input.dispatchTouchEvent", type="touchMove", touchPoints=pts(d, dx))
    page.appel("Input.dispatchTouchEvent", type="touchEnd", touchPoints=[])
    page.appel("Emulation.setTouchEmulationEnabled", enabled=False)


ACTIONS = {
    "initial": lambda p: None,
    "plus": lambda p: cliquer(p, "#zoomPlus"),
    "moins": lambda p: cliquer(p, "#zoomMoins"),
    "reset": lambda p: cliquer(p, "#zoomReset"),
    "molette": molette, "glisser": glisser, "pincer": pincer,
    "impression": lambda p: cliquer(p, "#pdf"),
}


def releve(page, marque):
    """Dernier dessin enregistré depuis `marque` (une écriture de canvas.width ouvre un dessin) et pixels du canvas."""
    r = page.evaluer("""(() => { const t = window.__trace, cv = document.querySelector('#graphique'); let i = -1;
        for (let k = t.length - 1; k >= %d; k--) if (t[k][0] === 'size.width') { i = k; break; }
        return { dessins: t.slice(%d).filter(e => e[0] === 'size.width').length, trace: i < 0 ? null : t.slice(i), png: cv.toDataURL('image/png') }; })()""" % (marque, marque))
    if r["trace"] is None:
        raise RuntimeError("aucun dessin après l'action")
    png = base64.b64decode(r["png"].split(",", 1)[1])
    texte = json.dumps(r["trace"], separators=(",", ":"), ensure_ascii=False)
    return {"trace": r["trace"], "sha": hashlib.sha256(texte.encode()).hexdigest()[:20], "appels": len(r["trace"]),
            "dessins": r["dessins"], "png": png}


def jouer(nav, fonctions, vues, etats=ETATS, dossier=None):
    """Joue la matrice sur la page courante du dépôt ; renvoie {clé: relevé}. Écrit aussi dans `dossier` si donné."""
    page = nav.ouvrir(PAGE, JS_TRACE)
    attendre_pret(page)
    res = {}
    if dossier:
        os.makedirs(dossier, exist_ok=True)
    for f in fonctions:
        calculer(page, f)
        for k, nomvue in enumerate(vues):
            largeur, sombre, dpr, canvas = VUES[nomvue]
            marque = page.evaluer("window.__trace.length")          # « initial » : dernier dessin depuis le changement de vue
            page.taille(largeur, sombre=sombre, dpr=dpr)
            page.evaluer(f"document.querySelector('#graphique').style.width = '{canvas}px'; window.dispatchEvent(new Event('resize'))")
            attendre_calme(page)
            if k > 0:                         # nouvelle vue : on repart du cadrage de départ, rééchantillonné à cette largeur
                cliquer(page, "#zoomReset")
                attendre_calme(page)
            for etat in etats:
                if etat != "initial":         # chaque geste part du cadrage de départ
                    cliquer(page, "#zoomReset")
                    attendre_calme(page)
                    marque = page.evaluer("window.__trace.length")
                    ACTIONS[etat](page)
                    attendre_calme(page)
                cle = f"{slug(f)}--{nomvue}--{etat}"
                res[cle] = rel = releve(page, marque)
                if dossier:
                    with open(os.path.join(dossier, cle + ".json"), "w", encoding="utf-8") as fh:
                        json.dump({"sha": rel["sha"], "appels": rel["appels"], "dessins": rel["dessins"], "trace": rel["trace"]}, fh, separators=(",", ":"), ensure_ascii=False)
                    with open(os.path.join(dossier, cle + ".png"), "wb") as fh:
                        fh.write(rel["png"])
        print(" ", f, flush=True)
    erreurs = [m for t, m in page.console if t == "error"]
    if erreurs:
        print("  erreurs console :", erreurs[:5], flush=True)
    res["__console_erreurs"] = erreurs
    return res


def matrice(complet):
    return (FONCTIONS_COMPLET, VUES_COMPLET) if complet else (FONCTIONS_SUITE, VUES_SUITE)


def enregistrer(dossier, complet=False):
    f, v = matrice(complet)
    with Navigateur() as nav:
        return jouer(nav, f, v, dossier=dossier)


def lire(dossier):
    out = {}
    for n in sorted(os.listdir(dossier)):
        if n.endswith(".json"):
            with open(os.path.join(dossier, n), encoding="utf-8") as fh:
                out[n[:-5]] = json.load(fh)
    return out


def pixels_differents(a, b):
    from PIL import Image, ImageChops
    ia, ib = Image.open(a).convert("RGBA"), Image.open(b).convert("RGBA")
    if ia.size != ib.size:
        return None
    d = ImageChops.difference(ia, ib)
    return sum(1 for p in getattr(d, "get_flattened_data", d.getdata)() if p != (0, 0, 0, 0))


def premier_ecart(ta, tb):
    for i, (x, y) in enumerate(zip(ta, tb)):
        if x != y:
            return i, x, y
    return min(len(ta), len(tb)), None, None


def comparer_dossiers(avant, apres, verbeux=True):
    """Renvoie (clés sans correspondance, clés à trace différente, {clé: pixels différents}, nombre de clés comparées)."""
    a, b = lire(avant), lire(apres)
    manquantes = sorted(set(a) ^ set(b))
    traces, pixels = [], {}
    for cle in sorted(set(a) & set(b)):
        if a[cle]["sha"] != b[cle]["sha"]:
            traces.append(cle)
            if verbeux:
                i, x, y = premier_ecart(a[cle]["trace"], b[cle]["trace"])
                print(f"  trace ≠ {cle} : {a[cle]['appels']} / {b[cle]['appels']} appels, 1er écart à l'appel {i} : {x} / {y}")
        px = pixels_differents(os.path.join(avant, cle + ".png"), os.path.join(apres, cle + ".png"))
        pixels[cle] = px
        if px != 0 and verbeux:
            print(f"  pixels ≠ {cle} : {px}")
    return manquantes, traces, pixels, len(set(a) & set(b))


def comparer(avant, apres, tolerance_pixels=0):
    manquantes, traces, pixels, n = comparer_dossiers(avant, apres)
    graves = [c for c, px in pixels.items() if px is None or px > tolerance_pixels]
    print(f"{n} scénarios comparés : {len(traces)} traces différentes, {len(graves)} canvas au-delà de {tolerance_pixels} px, "
          f"{len(manquantes)} sans correspondance ; écart maximal en pixels : {max([p or 0 for p in pixels.values()] or [0])}")
    return 1 if (traces or graves or manquantes) else 0


def bruit(n, dossier, complet=False):
    """Rejoue n fois le même code (page rechargée à chaque fois) et compare chaque répétition à la première."""
    for i in range(n):
        t = time.time()
        print(f"répétition {i + 1}/{n}", flush=True)
        enregistrer(os.path.join(dossier, f"rep{i:02d}"), complet)
        print(f"  {time.time() - t:.0f} s", flush=True)
    pire_traces = pire_px = 0
    for i in range(1, n):
        manquantes, traces, pixels, total = comparer_dossiers(os.path.join(dossier, "rep00"), os.path.join(dossier, f"rep{i:02d}"))
        pire_traces = max(pire_traces, len(traces))
        pire_px = max(pire_px, max([p if p is not None else 10**9 for p in pixels.values()] or [0]))
    print(f"BRUIT sur {n} répétitions de {total} scénarios : au plus {pire_traces} traces différentes, "
          f"au plus {pire_px} pixels différents sur un canvas")


def empreintes(releves):
    return {c: {"appels": r["appels"], "sha": r["sha"]} for c, r in sorted(releves.items()) if not c.startswith("__")}


def ecrire_references(dossier=None):
    """Réécrit les empreintes versionnées : depuis un dossier déjà enregistré (matrice « suite »), sinon en rejouant."""
    if dossier:
        res = {c: {"appels": r["appels"], "sha": r["sha"]} for c, r in lire(dossier).items()}
        attendues = {f"{slug(f)}--{v}--{e}" for f in FONCTIONS_SUITE for v in VUES_SUITE for e in ETATS}
        assert set(res) == attendues, "le dossier n'est pas un enregistrement de la matrice « suite »"
    else:
        with Navigateur() as nav:
            res = jouer(nav, FONCTIONS_SUITE, VUES_SUITE)
    os.makedirs(os.path.dirname(REFERENCES), exist_ok=True)
    with open(REFERENCES, "w", encoding="utf-8") as fh:
        json.dump(empreintes(res), fh, indent=1, ensure_ascii=False)
        fh.write("\n")
    print(len(empreintes(res)), "empreintes écrites dans", REFERENCES)


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "enregistrer":
        enregistrer(sys.argv[2], "complet" in sys.argv[3:])
    elif cmd == "comparer":
        sys.exit(comparer(sys.argv[2], sys.argv[3]))
    elif cmd == "bruit":
        bruit(int(sys.argv[2]), sys.argv[3], "complet" in sys.argv[4:])
    elif cmd == "references":
        ecrire_references(sys.argv[2] if len(sys.argv) > 2 else None)
    else:
        sys.exit("commandes : enregistrer, comparer, bruit, references")
