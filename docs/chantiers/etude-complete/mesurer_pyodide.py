"""Chantier « etude-complete », partie P9 : temps de l'Étude complète dans Pyodide (page réelle) et captures à 390 px.

Navigateur, serveur HTTP et copie locale de Pyodide des tests de pages (tests/pages/navigateur.py) ; KaTeX vient de jsDelivr (réseau).
Une page neuve par mesure : le cache de l'analyse (D19) ferait mesurer une deuxième fois un calcul déjà fait. Temps mesuré dans la
page (performance.now()) : du clic sur « Calculer ▶ » à la dernière carte affichée (bouton « Calculer » rendu, dernière carte =
« Graphique »). Une commande par fonction (limite de 5 minutes par commande, règle de l'enseignant) :

    timeout 300 uv run -q --no-project --python 3.12 --with sympy==1.13.3 --with mpmath==1.3.0 --with websockets \
        python docs/chantiers/etude-complete/mesurer_pyodide.py Ex7 [--n 3] [--capture docs/chantiers/etude-complete/captures]

Identifiants : Ex7, a, b, c, d (corpus du corrigé), e1x (e^(1/x)), x1 (x/(x²+1)) ; ou une saisie. Avec --capture : après la
première mesure, « Tout afficher », puis une capture PNG de la page entière à 390 px (`<identifiant>-390.png`). --n 0 : capture seule.
"""
import argparse
import base64
import json
import os
import statistics
import sys

RACINE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, os.path.join(RACINE, "tests", "pages"))
from navigateur import Navigateur  # noqa: E402
from rendu import attendre_pret  # noqa: E402

SAISIES = {"Ex7": "e^((x^2+x-2)/(6x-12))", "a": "e^(-x^2)", "b": "(x^2-6)e^(-2x)", "c": "e^x(6-e^x)", "d": "e^(2/(x^2-4))",
           "e1x": "e^(1/x)", "x1": "x/(x^2+1)"}
LARGEUR = 390

JS_MESURE = r"""
(async () => {
  const cartes = document.querySelector('#cartes'), bouton = document.querySelector('#calculer');
  cartes.innerHTML = '';
  document.querySelector('#entree').value = %s;
  const t0 = performance.now();
  bouton.click();
  await new Promise((ok, ko) => {
    const fin = t0 + 120000;
    (function attendre() {
      if (cartes.children.length > 0 && !bouton.disabled) return ok();
      if (performance.now() > fin) return ko(new Error('délai de 120 s dépassé'));
      setTimeout(attendre, 5);
    })();
  });
  const t1 = performance.now();
  const n = cartes.children.length, h = cartes.children[n - 1].querySelector('h3');
  return {ms: t1 - t0, cartes: n, derniere: h ? h.textContent : null};
})()
"""


def capturer(page, chemin):
    page.evaluer("document.querySelector('#tout') && !document.querySelector('#tout').disabled && document.querySelector('#tout').click()")
    page.attendre("!document.querySelector('#cartes .cache')", 10)
    page.evaluer("new Promise(r => setTimeout(r, 1500))")                     # graphique, polices de KaTeX
    hauteur = page.evaluer("Math.ceil(document.documentElement.scrollHeight)")
    d = page.appel("Page.captureScreenshot", format="png", captureBeyondViewport=True,
                   clip={"x": 0, "y": 0, "width": LARGEUR, "height": hauteur, "scale": 1})["data"]
    with open(chemin, "wb") as f:
        f.write(base64.b64decode(d))
    return hauteur


def main():
    p = argparse.ArgumentParser()
    p.add_argument("fonction")
    p.add_argument("--n", type=int, default=3)
    p.add_argument("--capture")
    a = p.parse_args()
    saisie = SAISIES.get(a.fonction, a.fonction)
    temps = []
    with Navigateur() as nav:
        for i in range(max(a.n, 1)):
            page = nav.ouvrir("etude-complete/index.html")               # page neuve : Pyodide rechargé, cache D19 vide
            attendre_pret(page)
            page.taille(LARGEUR, 900)
            r = page.evaluer(JS_MESURE % json.dumps(saisie))
            if r["derniere"] != "Graphique":
                raise SystemExit(f"{a.fonction} : la dernière carte est « {r['derniere']} », pas « Graphique » ({r})")
            if i < a.n:
                temps.append(r["ms"] / 1000)
                print(f"{a.fonction} mesure {i + 1} : {r['ms'] / 1000:.2f} s ({r['cartes']} cartes)", flush=True)
            if a.capture and i == 0:
                os.makedirs(a.capture, exist_ok=True)
                chemin = os.path.join(a.capture, f"{a.fonction}-{LARGEUR}.png")
                print(f"capture : {chemin} ({capturer(page, chemin)} px de haut)", flush=True)
            if page.erreurs:
                print("erreurs de la page :", page.erreurs, flush=True)
    if temps:
        print(json.dumps({"fonction": a.fonction, "saisie": saisie, "mesures_s": [round(t, 2) for t in temps],
                          "mediane_s": round(statistics.median(temps), 2)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
