"""T22 — Accueil (index.html) et registre des outils (commun/registre.json) : ACC-01, 02, 03, 05, 07.
ACC-04 et ACC-06 sont des tests de page (tests/pages/test_accueil.py) ; ACC-08 (liens ?methode= du simplexe) attend T27."""
import json
import os
import re
import unittest
from html.parser import HTMLParser

from moteurs import RACINE

ANNEES = {"I": "1", "II": "2", "III": "3"}
FILIERES = ("C", "Ms", "Mr")


def lire(chemin):
    with open(os.path.join(RACINE, chemin), encoding="utf-8") as f:
        return f.read()


REGISTRE = json.loads(lire("commun/registre.json"))
ACCUEIL = lire("index.html")


class Cartes(HTMLParser):
    """cellules[(année, filière)] = [(chemin, titre, description)] ; vides = cellules « Outils en préparation. »."""

    def __init__(self):
        super().__init__()
        self.cellules, self.vides = {}, set()
        self.annee = self.filiere = self.carte = self.champ = None

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        classes = (a.get("class") or "").split()
        if tag == "span" and "level-num" in classes:
            self.champ = "annee"
        elif tag == "div" and "track" in classes:
            self.filiere = a["data-track"]
            self.cellules.setdefault((self.annee, self.filiere), [])
        elif tag == "div" and "empty" in classes:
            self.vides.add((self.annee, self.filiere))
            self.champ = "vide"
        elif tag == "div" and "tool" in classes:
            self.carte = {"chemin": None, "titre": "", "description": ""}
        elif tag == "a" and self.carte is not None:
            self.carte["chemin"] = a["href"]
            self.champ = "titre"
        elif tag == "div" and "desc" in classes and self.carte is not None:
            self.champ = "description"

    def handle_endtag(self, tag):
        if tag == "div" and self.champ == "description":
            self.champ = None
            self.cellules[(self.annee, self.filiere)].append((self.carte["chemin"], self.carte["titre"].strip(), self.carte["description"].strip()))
            self.carte = None
        elif tag in ("a", "span", "div") and self.champ in ("titre", "annee", "vide"):
            self.champ = None

    def handle_data(self, data):
        if self.champ == "annee":
            self.annee = ANNEES[data.strip()]
        elif self.champ == "vide":
            self.texte_vide = data.strip()
        elif self.champ in ("titre", "description"):
            self.carte[self.champ] += data


def accueil():
    p = Cartes()
    p.feed(ACCUEIL)
    return p


def attendu():
    """cellules du registre : (année, filière) -> [(chemin, titre, description)] dans l'ordre du registre."""
    cellules = {(a, f): [] for a in ANNEES.values() for f in FILIERES}
    for o in REGISTRE["outils"]:
        for annee, filieres in o["filieres"].items():
            for f in filieres:
                cellules[(annee, f)].append((o["chemin"], o["titre"], o["description"]))
    return cellules


def rapport_contraste(a, b):
    def lum(h):
        h = h.lstrip("#")
        if len(h) == 3:
            h = "".join(c * 2 for c in h)
        c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
        c = [x / 12.92 if x <= 0.03928 else ((x + 0.055) / 1.055) ** 2.4 for x in c]
        return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]
    hi, lo = sorted((lum(a), lum(b)), reverse=True)
    return (hi + 0.05) / (lo + 0.05)


def variables(bloc):
    return dict(re.findall(r"--([a-z-]+):\s*(#[0-9a-fA-F]{3,6})", bloc))


class TestRegistre(unittest.TestCase):
    def test_schema(self):
        ids, chemins = set(), set()
        for o in REGISTRE["outils"]:
            with self.subTest(outil=o["id"]):
                self.assertEqual(set(o) - {"parametres", "descriptions"}, {"id", "chemin", "titre", "description", "filieres"})
                self.assertNotIn(o["id"], ids)
                self.assertNotIn(o["chemin"], chemins)
                ids.add(o["id"])
                chemins.add(o["chemin"])
                self.assertEqual(o["chemin"], o["id"] + "/")
                for annee, filieres in o["filieres"].items():
                    self.assertIn(annee, ANNEES.values())
                    self.assertTrue(filieres and set(filieres) <= set(FILIERES), filieres)
                    self.assertEqual(len(set(filieres)), len(filieres))

    def test_acc02_chaque_chemin_existe(self):
        for o in REGISTRE["outils"]:
            with self.subTest(chemin=o["chemin"]):
                self.assertTrue(os.path.isfile(os.path.join(RACINE, o["chemin"], "index.html")))

    def test_aucun_outil_oublie(self):
        """Chaque dossier à index.html (hors la racine) est au registre ; chaque outil Pyodide du manifeste aussi."""
        dossiers = {d for d in os.listdir(RACINE) if os.path.isfile(os.path.join(RACINE, d, "index.html"))}
        self.assertEqual(dossiers, {o["id"] for o in REGISTRE["outils"]})
        with open(os.path.join(RACINE, "moteur", "manifeste.json"), encoding="utf-8") as f:
            self.assertLessEqual(set(json.load(f)["outils"]), {o["id"] for o in REGISTRE["outils"]})


class TestAccueil(unittest.TestCase):
    def test_acc01_l_accueil_est_le_registre(self):
        p = accueil()
        self.assertEqual(sorted(p.cellules), sorted(attendu()), "une année ou une filière manque dans index.html")
        for cellule, outils in attendu().items():
            with self.subTest(annee=cellule[0], filiere=cellule[1]):
                self.assertEqual(p.cellules[cellule], outils)
                self.assertEqual(cellule in p.vides, not outils, "« Outils en préparation. » exactement quand il n'y a aucun outil")

    def test_acc03_sans_javascript_rien_n_est_masque(self):
        """La feuille de style de l'accueil ne masque #content que sous html[data-js] (posé par le script) ; la porte n'est montrée que sous data-js."""
        css = re.search(r"<style>(.*?)</style>", ACCUEIL, re.S).group(1)
        css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
        regles = re.findall(r"([^{}@]+)\{([^{}]*)\}", css)
        for selecteur, corps in regles:
            if "#content" in selecteur and "display:none" in corps.replace(" ", ""):
                with self.subTest(selecteur=selecteur.strip()):
                    self.assertIn("[data-js]", selecteur)
        # la porte (boutons sans effet sans JavaScript) est cachée par défaut et montrée seulement quand le script a posé data-js
        self.assertTrue(any(s.strip() == "#gate" and "display:none" in c.replace(" ", "") for s, c in regles))
        self.assertTrue(any("#gate" in s and "[data-js]" in s and "display:block" in c.replace(" ", "") for s, c in regles))

    def test_acc05_contraste(self):
        """Texte et fond de l'accueil, clair puis sombre : ≥ 4,5:1 (le doré sert à du texte : étiquettes, ligne d'en-tête)."""
        css = re.search(r"<style>(.*?)</style>", ACCUEIL, re.S).group(1)
        clair = variables(re.search(r":root\{(.*?)\}", css, re.S).group(1))
        sombre = {**clair, **variables(re.search(r"prefers-color-scheme: dark\)\{\s*:root\{(.*?)\}", css, re.S).group(1))}
        for nom, v in (("clair", clair), ("sombre", sombre)):
            for texte in ("ink", "muted", "accent", "accent-ink", "gold"):
                for fond in ("paper", "paper-raised"):
                    with self.subTest(theme=nom, texte=texte, fond=fond):
                        self.assertGreaterEqual(rapport_contraste(v[texte], v[fond]), 4.5, (v[texte], v[fond]))

    def test_acc07_plus_de_fourmi(self):
        self.assertNotIn("fourmi", ACCUEIL.lower())


if __name__ == "__main__":
    unittest.main()
