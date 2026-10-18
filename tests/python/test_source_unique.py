"""T16 — Une seule source de textes : les pages migrées vers commun/outil.js ne contiennent plus aucune
phrase de corrigé (elles viennent de resoudre(), en Python), et ni outil.js ni rendu.js non plus.
SOC-10 : boutons à symbole avec aria-label ; #etat et #apercu en aria-live.
À chaque migration (T17 à T20), ajouter la page à MIGREES."""
import os
import re
import unittest

from moteurs import RACINE

MIGREES = ["ensemble-definition", "derivee-variations", "limites-asymptotes"]
PHRASES = ["conditions d'existence", "condition d'existence", "Condition non résolue", "obtenues numériquement",
           "Contrôle numérique", "Ni logarithme", "aucune condition", "Aucun extremum", "ligneAsymptote",
           "branche parabolique", "Une condition n'a pas pu être résolue"]


def lire(chemin):
    with open(os.path.join(RACINE, chemin), encoding="utf-8") as f:
        return f.read()


class TestSourceUnique(unittest.TestCase):
    def test_aucune_phrase_de_corrige_en_js(self):
        for chemin in [f"{o}/index.html" for o in MIGREES] + ["commun/outil.js", "commun/rendu.js"]:
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


if __name__ == "__main__":
    unittest.main()
