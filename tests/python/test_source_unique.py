"""T16 — Une seule source de textes : les pages migrées vers commun/outil.js ne contiennent plus aucune
phrase de corrigé (elles viennent de resoudre(), en Python), et ni outil.js ni rendu.js non plus.
SOC-10 : boutons à symbole avec aria-label ; #etat et #apercu en aria-live.
À chaque migration (T17 à T20), ajouter la page à MIGREES."""
import os
import re
import unittest

from moteurs import RACINE

MIGREES = ["ensemble-definition", "derivee-variations", "limites-asymptotes", "etude-complete", "factorisation"]
PHRASES = ["conditions d'existence", "condition d'existence", "Condition non résolue", "obtenues numériquement",
           "Contrôle numérique", "Ni logarithme", "aucune condition", "Aucun extremum", "ligneAsymptote",
           "branche parabolique", "Une condition n'a pas pu être résolue"]


def lire(chemin):
    with open(os.path.join(RACINE, chemin), encoding="utf-8") as f:
        return f.read()


class TestSourceUnique(unittest.TestCase):
    def test_aucune_phrase_de_corrige_en_js(self):
        for chemin in [f"{o}/index.html" for o in MIGREES] + ["commun/outil.js", "commun/rendu.js", "commun/graphique.js"]:
            src = lire(chemin)
            for phrase in PHRASES:
                with self.subTest(fichier=chemin, phrase=phrase):
                    self.assertNotIn(phrase, src)

    def test_pages_migrees_sans_rendu_local(self):
        for o in MIGREES:
            src = lire(f"{o}/index.html")
            with self.subTest(outil=o):
                self.assertIn('from "../commun/outil.js"', src)
                for ancien in ("function tableau(", "function afficher(", "function montrer(", "innerHTML=h"):
                    self.assertNotIn(ancien, src)


class TestAccessibilite(unittest.TestCase):
    def test_soc10(self):
        for o in MIGREES:
            src = lire(f"{o}/index.html")
            with self.subTest(outil=o):
                for ident in ("etat", "apercu"):
                    self.assertRegex(src, rf'id="{ident}"[^>]*aria-live="polite"')
                clavier = re.search(r'<div class="clavier" id="clavier">(.*?)</div>', src, re.S).group(1)
                boutons = re.findall(r"<button([^>]*)>([^<]*)</button>", clavier)
                self.assertTrue(boutons)
                for attrs, texte in boutons:
                    if not re.fullmatch(r"[A-Za-z0-9]", texte):         # bouton à symbole
                        self.assertIn("aria-label=", attrs, texte)


class TestDispositionDuClavier(unittest.TestCase):
    """Clavier « calculatrice » à 6 colonnes (chantier Clavier intégré, 02.11.2026) : les trois premières rangées sont les mêmes sur les six outils ;
    seule la dernière change. Les chiffres, la virgule et les opérations ne changent jamais de place, pour que l'élève retrouve ses touches d'un outil à l'autre."""
    TROIS_RANGEES = ["7", "8", "9", "(", ")", "back", "4", "5", "6", "*", "/", "clear", "1", "2", "3", "+", "-", "^"]
    FONCTION = ["0", ",", "x", "ln(", "e^(", "sqrt("]
    PAGES = {
        "ensemble-definition": FONCTION, "derivee-variations": FONCTION, "limites-asymptotes": FONCTION, "etude-complete": FONCTION,
        "factorisation": ["0", ",", "x"],
        "exponentielles-logarithmes": ["0", ",", "x", "=", "e", "ln(", "log(", "log_", "sqrt(", "%", "n", "t", "Q", "C", "V"],
    }

    @staticmethod
    def touches(o):
        clavier = re.search(r'<div class="clavier" id="clavier">(.*?)</div>', lire(f"{o}/index.html"), re.S).group(1)
        return [re.search(r'data-(?:t|k)="([^"]*)"', attrs).group(1) for attrs in re.findall(r"<button([^>]*)>", clavier)]

    def test_les_trois_premieres_rangees_et_la_derniere(self):
        for o, fin in self.PAGES.items():
            with self.subTest(outil=o):
                self.assertEqual(self.touches(o), self.TROIS_RANGEES + fin)

    def test_x_fois_et_virgule_ont_leur_texte_et_leur_nom(self):
        for o in self.PAGES:
            src = lire(f"{o}/index.html")
            with self.subTest(outil=o):
                self.assertIn('<button aria-label="fois" data-t="*">×</button>', src)
                self.assertIn('<button aria-label="divisé par" data-t="/">÷</button>', src)
                self.assertIn('<button aria-label="virgule" data-t=",">,</button>', src)


if __name__ == "__main__":
    unittest.main()
