"""Tests de pages — comportement commun des cinq outils (socle-commun.md), indépendant de la façon dont la
page est construite : `?f=` (SOC-04), saisie invalide (SOC-06), aperçu sans message rouge pendant la frappe
(SOC-16), étapes (SOC-07), largeur à 360 px (SOC-09), délai dépassé puis relance du moteur (SOC-13), rendu commun
des sorties de resoudre() (commun/rendu.js)."""
import json
import os
import re
import sys
import time
import unittest
from urllib.parse import quote

sys.path.insert(0, os.path.dirname(__file__))
from navigateur import Navigateur
from rendu import DOSSIER_REFERENCES, JS_CAPTURE, OUTILS, attendre_pret

RACINE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
CALCUL = {"ensemble-definition": "ln(x^2-4x)/(x-5)", "derivee-variations": "ln(x)/x", "limites-asymptotes": "(x^2-1)/(x-3)",
          "etude-complete": "x^2*e^(-x)", "factorisation": "x^2+5x-14"}

CHOISIS = [o for o in os.environ.get("OUTILS", "").split(",") if o] or OUTILS
EXEMPLE = {"ensemble-definition": "ln(x-1)", "derivee-variations": "x^2", "limites-asymptotes": "1/x",
           "etude-complete": "x^2", "factorisation": "x^2-1"}
INVALIDE = {"ensemble-definition": "ln(", "derivee-variations": "ln(", "limites-asymptotes": "ln(",
            "etude-complete": "ln(", "factorisation": "sqrt(x)"}
ANALYSE = ["ensemble-definition", "derivee-variations", "limites-asymptotes", "etude-complete"]


def sans_espace_entre_formules(cartes):
    """Les cartes sans l'espace entre deux formules (⟧ ⟦) dans le texte : la page d'origine en mettait un entre la formule
    et la ligne « ED = … », invisible (même écart que pour les pages Dérivée et Limites, T17 et T18). Les autres espaces,
    et tous les autres champs, restent comparés tels quels."""
    return [dict(c, texte=re.sub(r"⟧\s+⟦", "⟧⟦", c["texte"])) for c in cartes]


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

    def calculer(self, page, entree):
        page.evaluer(f"document.querySelector('#entree').value = {entree!r}; document.querySelector('#calculer').click()")
        page.attendre("document.querySelector('#cartes').children.length > 0 && !document.querySelector('#calculer').disabled", 120)

    def test_soc07_etapes(self):
        """« Étape suivante » révèle exactement une carte, « Tout afficher » toutes ; le compteur est juste."""
        for outil in OUTILS:
            with self.subTest(outil=outil):
                if outil not in CHOISIS:
                    continue
                page = self.ouvrir(outil)
                self.calculer(page, CALCUL[outil])
                etat = lambda: page.evaluer("""(() => {
                    const m = document.querySelector('#progression').textContent.match(/(\\d+) \\/ (\\d+)/);
                    return [+m[1], +m[2], document.querySelectorAll('#cartes .cache').length];
                })()""")
                k, m, caches = etat()
                self.assertEqual((k, caches), (1, m - 1))
                while k < m:
                    page.evaluer("document.querySelector('#suivant').click()")
                    k2, m2, c2 = etat()
                    self.assertEqual((k2, m2, c2), (k + 1, m, m - k - 1))
                    k = k2
                self.assertTrue(page.evaluer("document.querySelector('#suivant').disabled"))
                # « Tout afficher » depuis le début
                self.calculer(page, CALCUL[outil])
                page.evaluer("document.querySelector('#tout').click()")
                self.assertEqual(etat(), [m, m, 0])

    def test_soc09_pas_de_defilement_horizontal_a_360_px(self):
        for outil in OUTILS:
            with self.subTest(outil=outil):
                if outil not in CHOISIS:
                    continue
                page = self.ouvrir(outil)
                page.taille(360)
                self.calculer(page, CALCUL[outil])
                page.evaluer("document.querySelector('#tout').click()")
                time.sleep(1.0)
                largeur = page.evaluer("[document.documentElement.scrollWidth, window.innerWidth]")
                self.assertLessEqual(largeur[0], largeur[1], largeur)
                page.taille(1100)

    def test_soc13_page_delai_depasse_puis_relance(self):
        """Page migrée (commun/outil.js) : délai dépassé → message, moteur relancé, le calcul suivant réussit."""
        page = self.ouvrir("ensemble-definition")
        page.evaluer("window.__delaiCalcul = 1")
        self.calculer(page, "ln(x-1)")
        self.assertIn("trop de temps", page.evaluer("document.querySelector('#cartes .err').textContent"))
        page.evaluer("window.__delaiCalcul = 0")
        attendre_pret(page)                                            # nouveau moteur prêt
        self.calculer(page, "ln(x-1)")
        self.assertFalse(page.evaluer("document.querySelector('#cartes .err')"))
        self.assertTrue(page.evaluer("!!document.querySelector('#cartes .card.final')"))

    def test_rendu_commun_des_instantanes(self):
        """commun/rendu.js rend sans exception, sans « undefined » ni « [object », chaque sortie de resoudre()
        des cinq outils (instantanés de tests/python/instantanes/resoudre)."""
        page = self.ouvrir("ensemble-definition")
        dossier = os.path.join(RACINE, "tests", "python", "instantanes", "resoudre")
        for outil in OUTILS:
            with open(os.path.join(dossier, outil + ".json"), encoding="utf-8") as f:
                sorties = [v for v in json.load(f).values() if "exception" not in v]
            with self.subTest(outil=outil):
                res = page.evaluer("""(async (sorties) => {
                    const { rendreCarte, rendreErreur } = await import('/commun/rendu.js');
                    const vus = [];
                    for (const s of sorties) {
                        const els = s.ok ? [s.entete, ...s.cartes].filter(Boolean).map(rendreCarte) : [rendreErreur(s)];
                        for (const el of els) vus.push(el.innerHTML + el.textContent);
                    }
                    return vus.filter(h => /undefined|\\[object|NaN/.test(h)).length + ':' + vus.length;
                })(""" + json.dumps(sorties) + ")")
                mauvais, total = res.split(":")
                self.assertEqual(mauvais, "0", res)
                self.assertGreater(int(total), 0)

    def test_rendu_commun_de_l_etude_complete_egal_a_l_ancienne_page(self):
        """EC (T19) : rendre avec commun/rendu.js les sorties de resoudre() de l'Étude complète donne les mêmes cartes
        que la page d'origine, enregistrées dans references/etude-complete.json (classes, titres, textes, formules,
        tableaux avec les limites dans la ligne de variation, listes). La carte du graphique (dernière) est exclue :
        elle est vérifiée par le banc du graphique."""
        page = self.ouvrir("ensemble-definition")                       # n'importe quelle page qui charge KaTeX et rendu.js
        with open(os.path.join(RACINE, "tests", "python", "instantanes", "resoudre", "etude-complete.json"), encoding="utf-8") as f:
            sorties = {e: s for e, s in json.load(f).items() if s.get("ok")}
        with open(os.path.join(DOSSIER_REFERENCES, "etude-complete.json"), encoding="utf-8") as f:
            references = json.load(f)
        self.assertGreater(len(sorties), 10)
        for entree, sortie in sorties.items():
            with self.subTest(entree=entree):
                page.evaluer("document.querySelector('#cartes').innerHTML = ''")
                page.evaluer("""(async (s) => {
                    const { rendreCarte } = await import('/commun/rendu.js');
                    for (const c of [s.entete, ...s.cartes].filter(Boolean)) document.querySelector('#cartes').appendChild(rendreCarte(c));
                })(""" + json.dumps(sortie) + ")")
                rendu = page.evaluer(JS_CAPTURE)["cartes"]
                attendu = references[entree]["cartes"]
                self.assertEqual(len(rendu), len(attendu))
                self.assertEqual(rendu[-1]["titre"], "Graphique")
                self.assertEqual(sans_espace_entre_formules(rendu[:-1]), sans_espace_entre_formules(attendu[:-1]))

    def test_soc13_delai_depasse_puis_relance(self):
        page = self.ouvrir("ensemble-definition")
        res = page.evaluer("""(async () => {
            const { MoteurPython } = await import('/commun/moteur-python.js');
            const m = new MoteurPython('ensemble-definition');
            await m.demarrer();
            let e1 = null;
            try { await m.appelPy('resoudre', 'ln(x-1)', 1); } catch (e) { e1 = e.message; }
            m.relancer();
            const r = await m.appelPy('resoudre', 'ln(x-1)', 120000);
            return [e1, r.ok];
        })()""")
        self.assertEqual(res, ["delai", True])


if __name__ == "__main__":
    unittest.main()
