"""T14 — commun/style.css : les cinq pages outils partagent la même feuille et ne redéfinissent
ni les variables de couleur ni les règles communes (SOC-02)."""
import os
import re
import unittest

from moteurs import RACINE

OUTILS = ["ensemble-definition", "derivee-variations", "limites-asymptotes", "etude-complete", "factorisation"]
LIEN = '<link rel="stylesheet" href="../commun/style.css">'


def lire(chemin):
    with open(os.path.join(RACINE, chemin), encoding="utf-8") as f:
        return f.read()


class TestStyleCommun(unittest.TestCase):
    def test_pages_chargent_la_feuille_commune_avant_leur_style(self):
        for outil in OUTILS:
            with self.subTest(outil=outil):
                page = lire(outil + "/index.html")
                self.assertEqual(page.count(LIEN), 1)
                style = page.find("<style>")
                self.assertTrue(style == -1 or page.index(LIEN) < style, "la feuille commune doit précéder le <style> de la page")

    def test_pages_ne_redefinissent_pas_le_socle(self):
        variables = re.findall(r"--([\w-]+)\s*:", lire("commun/style.css"))
        regles = {r.strip() for r in re.findall(r"^([.#a-z][^{\n]*)\{", lire("commun/style.css"), re.M)}
        for outil in OUTILS:
            with self.subTest(outil=outil):
                m = re.search(r"<style>\n(.*?)</style>", lire(outil + "/index.html"), re.S)
                css = m.group(1) if m else ""
                self.assertNotIn(":root", css)
                for v in set(variables):
                    self.assertNotRegex(css, r"--%s\s*:" % re.escape(v))
                for r in re.findall(r"^([.#a-z][^{\n]*)\{", css, re.M):
                    if r.strip() in ("details ol", "details li", ".rappel", ".verif", "#graphique", ".final .res"):
                        continue                         # règles propres à une page, listées ici
                    self.assertNotIn(r.strip(), regles, f"« {r.strip()} » est déjà dans commun/style.css")

    def test_plus_de_tableaux_css_a_la_racine(self):
        self.assertFalse(os.path.exists(os.path.join(RACINE, "tableaux.css")))


if __name__ == "__main__":
    unittest.main()
