"""Chantier « Mise en page fluide » — commun/composants.css et commun/composants.js : les composants existent, la feuille n'utilise
aucune largeur d'écran en pixels, seulement les variables du socle, et ne redéfinit aucune règle de commun/style.css."""
import os
import re
import unittest

from moteurs import RACINE


def lire(chemin):
    with open(os.path.join(RACINE, chemin), encoding="utf-8") as f:
        return f.read()


CSS = lire("commun/composants.css")
JS = lire("commun/composants.js")
STYLE = lire("commun/style.css")


class TestComposants(unittest.TestCase):
    def test_composants_demandes_sont_presents(self):
        for classe in (".champ-signe", ".onglets", ".carte-etape", ".bouton-flottant", ".insecable", ".flux", ".conteneur-fluide", ".cadre-fluide",
                       ".uv", ".uv-col", ".chaine"):
            with self.subTest(classe=classe):
                self.assertIn(classe + "{", CSS)

    def test_champ_signe_mesures(self):
        self.assertRegex(CSS, r"\.champ-signe>input\{[^}]*width:4\.5ch")
        self.assertRegex(CSS, r"\.champ-signe\.membre>input\{width:7ch\}")
        self.assertRegex(CSS, r"\.champ-signe>button\{[^}]*min-height:44px")
        self.assertRegex(CSS, r'\.champ-signe>button\[data-signe="-"\]\{color:var\(--bad\)\}')
        self.assertRegex(CSS, r"\.carte-etape\{[^}]*padding:clamp\(10px,3vw,18px\)")

    def test_bouton_flottant_cache_a_l_impression_et_44_px(self):
        self.assertIn("safe-area-inset-bottom", CSS)
        self.assertRegex(CSS, r"@media print\{\s*\.bouton-flottant\{display:none")
        self.assertRegex(CSS, r"\.bouton-flottant\{[^}]*min-height:max\(44px")

    def test_tableau_uv_replie_par_retour_a_la_ligne(self):
        """Tableau u, v / u′, v′ (D8) : les deux colonnes passent l'une sous l'autre par retour à la ligne (aucune largeur fixe), une case
        trop large défile seule, et commun/rendu.js le dessine avec ces classes."""
        self.assertRegex(CSS, r"\.uv\{[^}]*display:flex;flex-wrap:wrap")
        self.assertRegex(CSS, r"\.uv\{[^}]*max-width:100%")
        self.assertRegex(CSS, r"\.uv-col\{[^}]*grid-template-rows:1fr 1fr")
        self.assertRegex(CSS, r"\.uv-col>div\{[^}]*overflow-x:auto")
        for regle in re.findall(r"\.uv[\w>-]*\{[^}]*\}", CSS):
            self.assertNotRegex(regle, r"width:\s*\d+px")                    # aucune largeur fixe en pixels
        rendu = lire("commun/rendu.js")
        self.assertIn('uv: b => `<div class="uv"><div class="uv-col">', rendu)

    def test_aucune_largeur_d_ecran_en_pixels(self):
        for requete in re.findall(r"@(?:media|container)\s*([^{]*)\{", CSS):
            with self.subTest(requete=requete.strip()):
                self.assertNotRegex(requete, r"\d\s*px", "une requête @media/@container ne s'écrit pas en pixels")

    def test_seules_les_variables_du_socle_sont_utilisees(self):
        connues = set(re.findall(r"--([\w-]+)\s*:", STYLE)) | set(re.findall(r"--([\w-]+)\s*:", CSS))
        for v in set(re.findall(r"var\(--([\w-]+)", CSS)):
            with self.subTest(variable=v):
                self.assertIn(v, connues)

    def test_ne_redefinit_aucune_regle_de_style_css(self):
        regles = {r.strip() for r in re.findall(r"^([.#a-z][^{\n]*)\{", STYLE, re.M)}
        for r in re.findall(r"^\s*([.#a-z\[][^{\n]*)\{", CSS, re.M):
            with self.subTest(regle=r.strip()):
                self.assertNotIn(r.strip(), regles)

    def test_module_exporte_onglets_et_champ_signe(self):
        self.assertIn("export function monterOnglets", JS)
        self.assertIn("export function champSigne", JS)
        for attendu in ('"tablist"', '"tab"', "ArrowRight", "ArrowLeft", "Home", "End", "aria-selected", 'inputmode: "decimal"'):
            with self.subTest(attendu=attendu):
                self.assertIn(attendu, JS)


if __name__ == "__main__":
    unittest.main()
