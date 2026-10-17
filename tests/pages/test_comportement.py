"""Tests de pages — comportement commun des cinq outils (socle-commun.md), indépendant de la façon dont la
page est construite : `?f=` (SOC-04), saisie invalide (SOC-06), aperçu sans message rouge pendant la frappe
(SOC-16), délai dépassé puis relance du moteur (SOC-13, au niveau du client commun)."""
import json
import os
import sys
import time
import unittest
from urllib.parse import quote

sys.path.insert(0, os.path.dirname(__file__))
from navigateur import Navigateur
from rendu import OUTILS, attendre_pret

CHOISIS = [o for o in os.environ.get("OUTILS", "").split(",") if o] or OUTILS
EXEMPLE = {"ensemble-definition": "ln(x-1)", "derivee-variations": "x^2", "limites-asymptotes": "1/x",
           "etude-complete": "x^2", "factorisation": "x^2-1"}
INVALIDE = {"ensemble-definition": "ln(", "derivee-variations": "ln(", "limites-asymptotes": "ln(",
            "etude-complete": "ln(", "factorisation": "sqrt(x)"}
ANALYSE = ["ensemble-definition", "derivee-variations", "limites-asymptotes", "etude-complete"]


class TestComportement(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.nav = Navigateur().__enter__()

    @classmethod
    def tearDownClass(cls):
        cls.nav.__exit__(None, None, None)

    def ouvrir(self, outil, requete=""):
        if outil not in CHOISIS:
            self.skipTest("hors de OUTILS")
        page = self.nav.ouvrir(f"{outil}/index.html{requete}")
        attendre_pret(page)
        return page

    def test_soc04_parametre_f(self):
        for outil in OUTILS:
            with self.subTest(outil=outil):
                if outil not in CHOISIS:
                    continue
                page = self.nav.ouvrir(f"{outil}/index.html?f={quote(EXEMPLE[outil])}")
                page.attendre("document.querySelector('#cartes').children.length > 0", 240)
                self.assertEqual(page.evaluer("document.querySelector('#entree').value"), EXEMPLE[outil])
                self.assertFalse(page.evaluer("document.querySelector('#cartes .err')"))

    def test_saisie_et_apercu(self):
        """SOC-06 (saisie invalide) et SOC-16 (aperçu, clavier virtuel), sur une seule page chargée par outil."""
        for outil in OUTILS:
            with self.subTest(outil=outil):
                if outil not in CHOISIS:
                    continue
                page = self.ouvrir(outil)
                self.saisie_invalide(page, outil)
                if outil in ANALYSE:
                    self.apercu_sans_erreur_pendant_la_frappe(page)
                    self.clavier_virtuel(page)

    def saisie_invalide(self, page, outil):
        page.evaluer(f"document.querySelector('#entree').value = {INVALIDE[outil]!r}; document.querySelector('#calculer').click()")
        page.attendre("document.querySelector('#cartes .err')", 60)
        texte = page.evaluer("document.querySelector('#cartes').innerText")
        self.assertTrue(texte.strip())
        for interdit in ("Traceback", "Error", "undefined", "NaN", "[object"):
            self.assertNotIn(interdit, texte)

    def apercu_sans_erreur_pendant_la_frappe(self, page):
        page.evaluer("document.querySelector('#entree').value = ''")
        for c in "ln(x)/x":
            page.taper("#entree", c, pause=0.12)
            self.assertFalse(page.evaluer("document.querySelector('#apercu .err')"), f"message rouge après « {c} »")
        page.attendre("document.querySelector('#apercu .katex')", 10)
        time.sleep(1.0)
        self.assertFalse(page.evaluer("document.querySelector('#apercu .err')"))
        # saisie incomplète : pas d'erreur tout de suite, une erreur après la pause
        page.evaluer("document.querySelector('#entree').value = ''")
        page.taper("#entree", "ln(", pause=0.05)
        time.sleep(0.25)
        self.assertFalse(page.evaluer("document.querySelector('#apercu .err')"), "erreur trop tôt")
        page.attendre("document.querySelector('#apercu .err')", 5)

    def clavier_virtuel(self, page):
        page.evaluer("document.querySelector('#entree').value=''")
        for t in ("ln(", "x", ")", "/", "x"):
            page.evaluer("document.querySelector(" + json.dumps(f'#clavier button[data-t="{t}"]') + ").click()")
            self.assertFalse(page.evaluer("document.querySelector('#apercu .err')"))
        page.attendre("document.querySelector('#apercu .katex')", 10)
        self.assertEqual(page.evaluer("document.querySelector('#entree').value"), "ln(x)/x")

    def test_soc13_delai_depasse_puis_relance(self):
        page = self.ouvrir("ensemble-definition")
        res = page.evaluer("""(async () => {
            const { MoteurPython } = await import('/commun/moteur-python.js');
            const m = new MoteurPython('ensemble-definition');
            await m.demarrer();
            let e1 = null;
            try { await m.appelPy('analyser', 'ln(x-1)', 1); } catch (e) { e1 = e.message; }
            m.relancer();
            const r = await m.appelPy('analyser', 'ln(x-1)', 120000);
            return [e1, r.ok];
        })()""")
        self.assertEqual(res, ["delai", True])


if __name__ == "__main__":
    unittest.main()
