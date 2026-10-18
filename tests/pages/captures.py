"""Captures d'écran des 5 pages (clair, sombre, 360 px, impression ; page vide puis après un calcul),
pour vérifier qu'un changement de CSS ne modifie aucun pixel (T14).

    # avant la modification
    uv run -q --no-project --python 3.12 --with sympy==1.13.3 --with websockets \
        python tests/pages/captures.py enregistrer /chemin/avant
    # après
    … python tests/pages/captures.py enregistrer /chemin/apres
    … python tests/pages/captures.py comparer /chemin/avant /chemin/apres
    # mesure du bruit d'une page : 10 fois le même code
    … python tests/pages/captures.py bruit 10 /chemin/bruit etude-complete

Les captures ne sont PAS versionnées : le rendu des polices change d'une machine à l'autre (CI Linux comprise)."""
import hashlib
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from navigateur import Navigateur
from rendu import OUTILS, attendre_pret

CALCUL = {"ensemble-definition": "ln(x^2-4x)/(x-5)", "derivee-variations": "ln(x)/x", "limites-asymptotes": "(x^2-1)/(x-3)",
          "etude-complete": "x^2*e^(-x)", "factorisation": "x^2+5x-14"}
VUES = {"clair": dict(largeur=1100), "sombre": dict(largeur=1100, sombre=True), "360": dict(largeur=360),
        "360-sombre": dict(largeur=360, sombre=True), "impression": dict(largeur=900, imprimante=True)}


def enregistrer(dossier, outils=None):
    os.makedirs(dossier, exist_ok=True)
    with Navigateur() as nav:
        for outil in outils or OUTILS:
            page = nav.ouvrir(f"{outil}/index.html")
            attendre_pret(page)
            for etat in ("vide", "calcul"):
                if etat == "calcul":
                    page.evaluer(f"document.querySelector('#entree').value = {CALCUL[outil]!r}; document.querySelector('#calculer').click()")
                    page.attendre("document.querySelector('#cartes').children.length > 0 && !document.querySelector('#calculer').disabled", 120)
                    page.evaluer("document.querySelector('#tout').click()")
                    page.attendre("!document.querySelector('#cartes .cache')", 10)
                    page.evaluer("new Promise(r => setTimeout(r, 1500))")        # graphique, badge de contrôle
                for nom, vue in VUES.items():
                    page.taille(**vue)
                    page.evaluer("new Promise(r => setTimeout(r, 400))")
                    page.capture(os.path.join(dossier, f"{outil}--{etat}--{nom}.png"))
            print(outil, flush=True)


def empreintes(dossier):
    return {n: hashlib.sha256(open(os.path.join(dossier, n), "rb").read()).hexdigest() for n in sorted(os.listdir(dossier)) if n.endswith(".png")}


def pixels_differents(chemin_a, chemin_b):
    """Nombre de pixels différents (None si les tailles diffèrent). Demande Pillow (--with pillow)."""
    from PIL import Image, ImageChops
    a, b = Image.open(chemin_a).convert("RGB"), Image.open(chemin_b).convert("RGB")
    if a.size != b.size:
        return None
    d = ImageChops.difference(a, b)
    return sum(1 for p in getattr(d, "get_flattened_data", d.getdata)() if p != (0, 0, 0))


# Tolérance propre à une page, d'après une mesure (mesurer_bruit) ; sinon BRUIT.
# etude-complete : 10 chargements du même code × 10 captures (5 vues, vide et après calcul), le 18.10.2026 : 0 pixel d'écart
# à chaque fois. Plancher de 20 px = le liseré d'antialiasing d'un seul glyphe ; un décalage réel d'un pixel en change des milliers.
BRUIT_PAGE = {"etude-complete": 20}
BRUIT = 400     # un filet d'une colonne arrondi autrement d'une exécution à l'autre : deux mesures identiques du même état en montrent


def bruit_de(nom):
    return BRUIT_PAGE.get(nom.split("--")[0], BRUIT)


def mesurer_bruit(n, dossier, outils):
    """Rejoue n fois les mêmes captures du même code (page rechargée à chaque fois) et compare chacune à la première."""
    for i in range(n):
        print(f"répétition {i + 1}/{n}", flush=True)
        enregistrer(os.path.join(dossier, f"rep{i:02d}"), outils)
    pire = {}
    for i in range(1, n):
        a, b = os.path.join(dossier, "rep00"), os.path.join(dossier, f"rep{i:02d}")
        for nom in sorted(empreintes(a)):
            px = pixels_differents(os.path.join(a, nom), os.path.join(b, nom))
            pire[nom] = max(pire.get(nom, 0), 10**9 if px is None else px)
    for nom, px in pire.items():
        print(f"  {nom} : au plus {px} pixels")
    print(f"BRUIT sur {n} répétitions : au plus {max(pire.values())} pixels sur une capture")


def comparer(avant, apres):
    a, b = empreintes(avant), empreintes(apres)
    differents = [n for n in a if a.get(n) != b.get(n)] + [n for n in b if n not in a]
    graves = []
    for n in differents:
        if n in a and n in b:
            px = pixels_differents(os.path.join(avant, n), os.path.join(apres, n))
            print(f"  ≠ {n} : {px} pixels")
            if px is None or px > bruit_de(n):
                graves.append(n)
        else:
            print(f"  ≠ {n} : absente d'un côté")
            graves.append(n)
    print(f"{len(a)} captures avant, {len(b)} après, {len(differents)} différentes, {len(graves)} au-delà du bruit ({BRUIT} px, {BRUIT_PAGE} px pour certaines pages)")
    return 1 if graves else 0


if __name__ == "__main__":
    if sys.argv[1] == "enregistrer":
        enregistrer(sys.argv[2], sys.argv[3:] or None)
    elif sys.argv[1] == "bruit":
        mesurer_bruit(int(sys.argv[2]), sys.argv[3], sys.argv[4:] or None)
    else:
        sys.exit(comparer(sys.argv[2], sys.argv[3]))
