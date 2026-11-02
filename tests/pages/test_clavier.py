"""Tests de pages — clavier intégré des outils à saisie de fonction (chantier « Clavier intégré », partie 1).

Sur écran tactile (émulé : `(pointer: coarse)`), l'élève tape avec les touches de la page : le champ n'ouvre pas le clavier du système, une rangée « ABC » +
« Calculer ▶ » est ajoutée. Sur ordinateur, la saisie au clavier est inchangée. Le résultat obtenu aux touches doit être celui de la saisie directe."""
import json
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(__file__))
from navigateur import Navigateur
from rendu import JS_CAPTURE, attendre_pret

CHOISIS = [o for o in os.environ.get("OUTILS", "").split(",") if o]
LARGEURS = (320, 360, 375, 390, 430, 768, 1100)
ANDROID = ("Mozilla/5.0 (Linux; Android 14; Pixel 8) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/156.0.0.0 Mobile Safari/537.36", "Linux armv8l")
IPHONE = ("Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.0 Mobile/15E148 Safari/604.1", "iPhone")

# Touches (data-t) qui écrivent chaque formule, dans l'ordre de la frappe.
TOUCHES_1 = ["(", "x", "^", "2", "-", "1", ")", "/", "(", "x", "-", "3", ")"]                  # (x^2-1)/(x-3)
TOUCHES_2 = ["e^(", "-", "x", ")", "/", "(", "4", "x", ")"]                                      # e^(-x)/(4x)
FORMULE_1, FORMULE_2 = "(x^2-1)/(x-3)", "e^(-x)/(4x)"


def corrige(page):
    """Attend le corrigé, l'affiche en entier et renvoie ses cartes (rendu normalisé de commun/rendu.js)."""
    page.attendre("document.querySelector('#cartes').children.length > 0 && !document.querySelector('#calculer').disabled", 120)
    page.evaluer("document.querySelector('#tout').click()")
    return page.evaluer(JS_CAPTURE)["cartes"]


@unittest.skipUnless(not CHOISIS or "limites-asymptotes" in CHOISIS, "hors de OUTILS")
class TestClavierIntegre(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.nav = Navigateur().__enter__()

    @classmethod
    def tearDownClass(cls):
        cls.nav.__exit__(None, None, None)

    def ouvrir(self, tactile, largeur=390, outil="limites-asymptotes", agent=ANDROID):
        page = self.nav.ouvrir(f"{outil}/index.html", tactile=tactile, agent=agent if tactile else None)
        page.attendre("document.readyState === 'complete' && document.querySelector('#clavier')", 30)
        page.taille(largeur, 800)
        attendre_pret(page)
        return page

    def valeur(self, page):
        return page.evaluer("document.querySelector('#entree').value")

    def attendre_valeur(self, page, attendu):
        """Le clic d'un appui du doigt est fabriqué par le navigateur après coup (lent quand la machine est chargée) : on attend l'effet avant de le lire."""
        try:
            page.attendre(f"document.querySelector('#entree').value === {json.dumps(attendu)}", 10)
        except TimeoutError:
            pass
        self.assertEqual(self.valeur(page), attendu)

    def toucher_valeur(self, page, selecteur, attendu):
        page.toucher(selecteur)
        self.attendre_valeur(page, attendu)

    def ecrire(self, page, liste, depart=""):
        """Appuie sur les touches `liste` (curseur en fin de champ) ; le champ contient, après chacune, ce qu'il contenait plus son texte."""
        courant = depart
        for t in liste:
            courant += t
            self.toucher_valeur(page, f'#clavier button[data-t="{t}"]', courant)

    def attendre_etat(self, page, attendu):
        js = "(e => [e.getAttribute('inputmode'), e.readOnly, document.querySelector('#clavier .abc').textContent])(document.querySelector('#entree'))"
        try:
            page.attendre(f"JSON.stringify({js}) === {json.dumps(json.dumps(attendu))}", 10)
        except TimeoutError:
            pass
        self.assertEqual(page.evaluer(js), attendu)

    def test_a_deux_formules_aux_touches_donnent_le_corrige_de_la_saisie_directe(self):
        """Tactile, 390 px : (x^2-1)/(x-3) puis e^(-x)/(4x) uniquement avec les touches et « Calculer ▶ » ; mêmes cartes qu'en saisie directe sur ordinateur."""
        page = self.ouvrir(tactile=True)
        self.assertEqual(page.evaluer("matchMedia('(pointer: coarse)').matches"), True)
        self.assertEqual(page.evaluer("document.querySelector('#entree').getAttribute('inputmode')"), "none")
        self.assertEqual(page.evaluer("document.querySelectorAll('#clavier button.abc, #clavier button.lancer').length"), 2)
        tactile = {}
        for formule, touches in ((FORMULE_1, TOUCHES_1), (FORMULE_2, TOUCHES_2)):
            self.toucher_valeur(page, '#clavier button[data-k="clear"]', "")
            self.ecrire(page, touches)
            self.assertEqual(self.valeur(page), formule)
            page.toucher("#clavier button.lancer")
            tactile[formule] = corrige(page)
            self.assertEqual(self.valeur(page), formule)                              # le corrigé ne touche pas à la saisie
        self.assertEqual([e for e in page.erreurs if "favicon" not in e], [])
        direct = self.ouvrir(tactile=False, largeur=1100)
        for formule in (FORMULE_1, FORMULE_2):
            direct.evaluer("document.querySelector('#entree').value = ''")
            direct.taper("#entree", formule)
            direct.evaluer("document.querySelector('#calculer').click()")
            with self.subTest(formule=formule):
                self.assertEqual(tactile[formule], corrige(direct))

    def test_b_la_touche_fois_insere_une_etoile_et_les_touches_agissent_au_curseur(self):
        page = self.ouvrir(tactile=True)
        self.ecrire(page, ["2", "*", "x"])
        self.assertEqual(self.valeur(page), "2*x")
        self.assertEqual(page.evaluer("document.querySelector('#clavier button[data-t=\"*\"]').textContent"), "×")
        self.assertEqual(page.evaluer("document.querySelector('#clavier button[data-t=\"/\"]').textContent"), "÷")
        self.assertEqual(page.evaluer("document.querySelector('#clavier button[data-t=\",\"]').getAttribute('aria-label')"), "virgule")
        page.evaluer("document.querySelector('#entree').setSelectionRange(1, 1)")           # curseur entre le 2 et l'étoile
        self.toucher_valeur(page, '#clavier button[data-t="0"]', "20*x")
        self.toucher_valeur(page, '#clavier button[data-k="back"]', "2*x")
        self.toucher_valeur(page, '#clavier button[data-t=","]', "2,*x")
        self.toucher_valeur(page, '#clavier button[data-t="5"]', "2,5*x")
        page.evaluer("document.querySelector('#calculer').click()")
        page.attendre("document.querySelector('#cartes').children.length > 0 && !document.querySelector('#calculer').disabled", 120)
        self.assertFalse(page.evaluer("document.querySelector('#cartes .err')"), "2,5*x doit être comprise (virgule décimale)")

    def test_c_abc_rouvre_le_clavier_du_systeme_et_123_revient_aux_touches(self):
        """Android : inputmode="none" ; iPhone : en plus readonly (iOS ouvre parfois son clavier malgré inputmode="none"). « ABC » remet le champ comme il était, « 123 » revient aux touches."""
        for nom, agent, readonly in (("Android", ANDROID, False), ("iPhone", IPHONE, True)):
            page = self.ouvrir(tactile=True, agent=agent)
            with self.subTest(appareil=nom):
                self.attendre_etat(page, ["none", readonly, "ABC"])
                page.toucher("#clavier button.abc")
                self.attendre_etat(page, [None, False, "123"])
                self.ecrire(page, ["7"])                                               # les touches écrivent aussi pendant que le clavier du système est ouvert
                page.toucher("#clavier button.abc")
                self.attendre_etat(page, ["none", readonly, "ABC"])
                self.ecrire(page, ["8"], depart="7")

    def test_d_calculer_suit_le_bouton_de_la_page(self):
        """« Calculer ▶ » porte le libellé du bouton de la page et reste grisé tant que celui-ci l'est (moteur en chargement ou calcul en cours)."""
        page = self.nav.ouvrir("factorisation/index.html", tactile=True)
        page.attendre("document.readyState === 'complete' && document.querySelector('#clavier .lancer')", 30)
        self.assertEqual(page.evaluer("document.querySelector('#clavier .lancer').textContent"), "Factoriser ▶")
        attendre_pret(page)
        self.assertFalse(page.evaluer("document.querySelector('#clavier .lancer').disabled"))
        page.evaluer("document.querySelector('#calculer').disabled = true")
        page.attendre("document.querySelector('#clavier .lancer').disabled", 5)

    def test_e_ordinateur_saisie_inchangee(self):
        """Sur ordinateur : ni rangée « ABC », ni inputmode, ni readonly ; les touches et la frappe écrivent comme avant."""
        page = self.ouvrir(tactile=False, largeur=1100)
        self.assertEqual(page.evaluer("matchMedia('(pointer: coarse)').matches"), False)
        self.assertEqual(page.evaluer("document.querySelectorAll('#clavier button.abc, #clavier button.lancer').length"), 0)
        self.assertEqual(page.evaluer("(e => [e.hasAttribute('inputmode'), e.readOnly])(document.querySelector('#entree'))"), [False, False])
        page.taper("#entree", "x^2")
        page.evaluer("document.querySelector('#clavier button[data-t=\"+\"]').click()")
        page.evaluer("document.querySelector('#clavier button[data-t=\"1\"]').click()")
        self.assertEqual(self.valeur(page), "x^2+1")

    def test_f_touches_de_44_px_sans_defilement_horizontal_de_320_a_1100_px(self):
        """Tactile, clavier à 5 rangées (limites) et à 7 rangées (exponentielles) : pas de défilement horizontal de 320 à 1100 px, touches de 44 px de haut
        (et de large dès 360 px ; 40 px à 320 px, filet de sécurité) ; chaque touche reste dans l'écran."""
        for outil in ("limites-asymptotes", "exponentielles-logarithmes"):
            if CHOISIS and outil not in CHOISIS:
                continue
            page = self.ouvrir(tactile=True, outil=outil)
            for largeur in LARGEURS:
                page.taille(largeur, 800)
                m = page.evaluer("""(() => { const r = [...document.querySelectorAll('#clavier button')].map(b => b.getBoundingClientRect());
                    return { debord: document.documentElement.scrollWidth - innerWidth, n: r.length, h: Math.min(...r.map(x => x.height)), l: Math.min(...r.map(x => x.width)),
                             dehors: r.filter(x => x.left < -0.5 || x.right > innerWidth + 0.5).length }; })()""")
                with self.subTest(outil=outil, largeur=largeur):
                    self.assertLessEqual(m["debord"], 0)
                    self.assertGreaterEqual(m["h"], 43.9)
                    self.assertGreaterEqual(m["l"], 43.9 if largeur >= 360 else 39.9)
                    self.assertEqual(m["dehors"], 0)
