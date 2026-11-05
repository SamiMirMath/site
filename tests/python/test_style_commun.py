"""T14 — commun/style.css : les pages outils construites par monterOutil partagent la même feuille et ne redéfinissent
ni les variables de couleur ni les règles communes (SOC-02)."""
import os
import re
import unittest

import outils_du_site
from moteurs import RACINE

OUTILS = outils_du_site.outils_pyodide()      # les pages construites par monterOutil (le simplexe, page autonome, a sa propre feuille)
LIEN = '<link rel="stylesheet" href="../commun/style.css">'
LIEN_COMPOSANTS = '<link rel="stylesheet" href="../commun/composants.css">'      # composants de mise en page fluide, après la feuille commune


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
                self.assertEqual(page.count(LIEN_COMPOSANTS), 1)
                self.assertLess(page.index(LIEN), page.index(LIEN_COMPOSANTS))
                self.assertTrue(style == -1 or page.index(LIEN_COMPOSANTS) < style)

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
                    if r.strip() in ("details li", ".rappel", ".verif", ".final .res"):
                        continue                         # règles propres à une page, listées ici
                    self.assertNotIn(r.strip(), regles, f"« {r.strip()} » est déjà dans commun/style.css")

    def test_grille_chaine_et_listes_des_rappels_dans_les_feuilles_communes(self):
        """Chantier briques-communes, B4 : la grille .chaine (Exp-log et bloc « chaine ») est dans commun/composants.css, les listes
        numérotées d'un <details> (details ol) dans commun/style.css, et aucune page ne garde de règle qui les touche (pas de CSS en
        double)."""
        self.assertIn("\n.chaine{display:grid;", lire("commun/composants.css"))
        self.assertIn(".etape:has(>.chaine){container-type:inline-size}", lire("commun/composants.css"))
        self.assertIn("\ndetails ol,details ul{margin:.4em 0 0;padding-left:1.2em}\n", lire("commun/style.css"))
        for outil in OUTILS + ["simplexe"]:
            with self.subTest(outil=outil):
                m = re.search(r"<style>\n(.*?)</style>", lire(outil + "/index.html"), re.S)
                css = re.sub(r"/\*.*?\*/", "", m.group(1) if m else "", flags=re.S)
                for selecteur in re.findall(r"([^{}]+)\{", css):
                    if selecteur.strip().startswith("@"):
                        continue
                    for s in selecteur.split(","):
                        self.assertNotIn(".chaine", s, f"règle « {s.strip()} » : la grille .chaine est dans commun/composants.css")
                        self.assertNotRegex(s, r"\bdetails\b.*\bol\b", f"règle « {s.strip()} » : details ol est dans commun/style.css")

    def test_aucune_largeur_d_ecran_en_pixels_dans_les_styles_locaux(self):
        """Mise en page fluide (30.10.2026) : un style local ne dispose pas le contenu selon la largeur de l'écran ; il passe à la ligne tout seul ou utilise @container."""
        for outil in OUTILS + ["simplexe"]:
            with self.subTest(outil=outil):
                m = re.search(r"<style>\n(.*?)</style>", lire(outil + "/index.html"), re.S)
                css = m.group(1) if m else ""
                for requete in re.findall(r"@(?:media|container)\s*([^{]*)\{", css):
                    if "print" in requete or "prefers-" in requete:
                        continue
                    self.assertNotRegex(requete, r"\d\s*px", f"requête en pixels : @media/@container {requete.strip()}")

    def test_plus_de_tableaux_css_a_la_racine(self):
        self.assertFalse(os.path.exists(os.path.join(RACINE, "tableaux.css")))


if __name__ == "__main__":
    unittest.main()
