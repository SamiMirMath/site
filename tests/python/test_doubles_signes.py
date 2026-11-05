"""Chantier explog-suite, point 2 : garde générale, pour tous les outils. Aucune formule (TeX) ni aucun texte du corpus n'a deux signes
consécutifs : « -- », « −− », « +- », « -+ », « + - », « - - » (espaces, accolades et petites espaces TeX permis entre les deux).

Parcours (sans rien recalculer : les fichiers sont ceux que test_instantanes_resoudre.py et tests/pages/test_rendu.py comparent aux
sorties) :
- instantanés resoudre (tests/python/instantanes/resoudre/*.json) : chaque chaîne à part ; dans un champ HTML, chaque morceau entre deux
  balises, puis chaque formule \\( \\) ou \\[ \\] et le texte qui les entoure (deux cases voisines d'un tableau ne se touchent donc jamais) ;
- références de pages (tests/pages/references/*.json) : chaque formule ⟦…⟧ et chaque case de tableau. Le texte en clair d'une carte y
  colle les cases d'un tableau de signes (« −−0+ ») et les boutons du graphique (« − + ») : il est contrôlé dans l'instantané resoudre,
  auquel la page est égale."""
import glob
import json
import os
import re
import unittest

ICI = os.path.dirname(os.path.abspath(__file__))
INSTANTANES = sorted(glob.glob(os.path.join(ICI, "instantanes", "resoudre", "*.json")))
REFERENCES = sorted(glob.glob(os.path.join(ICI, "..", "pages", "references", "*.json")))
SIGNE = r"[+\-−]"
DOUBLE = re.compile(SIGNE + r"(?:\s|\{|\\[,;:! ])*" + SIGNE)
BALISE = re.compile(r"<[^>]*>")
FORMULE_TEX = re.compile(r"\\\((.*?)\\\)|\\\[(.*?)\\\]", re.S)
FORMULE_PAGE = re.compile(r"⟦(.*?)⟧", re.S)


def _chaines(o, chemin=()):
    if isinstance(o, str):
        yield chemin, o
    elif isinstance(o, dict):
        for k, v in o.items():
            yield from _chaines(v, chemin + (k,))
    elif isinstance(o, list):
        for i, v in enumerate(o):
            yield from _chaines(v, chemin + (i,))


def morceaux_resoudre(s):
    """Les morceaux d'une chaîne de sortie : entre deux balises, chaque formule et chaque texte hors formule."""
    for texte in BALISE.split(s):
        yield from (a or b for a, b in FORMULE_TEX.findall(texte))
        yield FORMULE_TEX.sub(" ", texte)


def morceaux_page(chemin, s):
    """Les formules ⟦…⟧ d'une chaîne de la référence de page ; une case de tableau en entier."""
    if "tableaux" in chemin:
        yield s
    yield from FORMULE_PAGE.findall(s)


def fautes(fichier, morceaux):
    with open(fichier, encoding="utf-8") as f:
        donnees = json.load(f)
    trouvees = []
    for entree, sortie in donnees.items():
        for chemin, s in _chaines(sortie):
            for m in morceaux(chemin, s):
                if DOUBLE.search(m):
                    trouvees.append((entree, m))
    return trouvees


class TestDoublesSignes(unittest.TestCase):
    def test_fichiers_presents(self):
        self.assertGreaterEqual(len(INSTANTANES), 7)
        self.assertGreaterEqual(len(REFERENCES), 8)

    def test_motif(self):
        for faux in ("--2", "−−2", "x +- 1", "x -+ 1", "x + -1", "x - -1", r"x + {-1}", r"x -\,-1", "a ++ b", "a − + b"):
            self.assertRegex(faux, DOUBLE)
        for juste in ("x - (-1)", r"\log(-(-100))", r"x^{-1} + 2", r"-\infty", r"\left(-\frac{1}{2}\right)^{2} - 4", "0^{-}", "x \\pm 1"):
            self.assertNotRegex(juste, DOUBLE)

    def test_instantanes_resoudre(self):
        for fichier in INSTANTANES:
            with self.subTest(fichier=os.path.basename(fichier)):
                self.assertEqual(fautes(fichier, lambda chemin, s: morceaux_resoudre(s)), [])

    def test_references_pages(self):
        for fichier in REFERENCES:
            with self.subTest(fichier=os.path.basename(fichier)):
                self.assertEqual(fautes(fichier, morceaux_page), [])


if __name__ == "__main__":
    unittest.main()
