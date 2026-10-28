"""Tests de pages — comportement commun des cinq outils (socle-commun.md), indépendant de la façon dont la
page est construite : `?f=` (SOC-04), saisie invalide (SOC-06), aperçu sans message rouge pendant la frappe
(SOC-16), étapes (SOC-07), largeur à 360 px (SOC-09), délai dépassé puis relance du moteur (SOC-13), rendu commun
des sorties de resoudre() (commun/rendu.js), libellé pendant le chargement de SymPy (T31), exercice tiré en Python (T20)."""
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
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "python"))
from cas_el import BATTERIE_M_VAR, entrees_el, entrees_el_m  # noqa: E402

RACINE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
CALCUL = {"ensemble-definition": "ln(x^2-4x)/(x-5)", "derivee-variations": "ln(x)/x", "limites-asymptotes": "(x^2-1)/(x-3)",
          "etude-complete": "x^2*e^(-x)", "factorisation": "x^2+5x-14", "exponentielles-logarithmes": "2^(x-1)=3^x"}

CHOISIS = [o for o in os.environ.get("OUTILS", "").split(",") if o] or OUTILS
EXEMPLE = {"ensemble-definition": "ln(x-1)", "derivee-variations": "x^2", "limites-asymptotes": "1/x",
           "etude-complete": "x^2", "factorisation": "x^2-1", "exponentielles-logarithmes": "3^(x+1)=27"}
INVALIDE = {"ensemble-definition": "ln(", "derivee-variations": "ln(", "limites-asymptotes": "ln(",
            "etude-complete": "ln(", "factorisation": "sqrt(x)", "exponentielles-logarithmes": "x<3"}
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

    def test_t20_factorisation_exercice_tire_en_python(self):
        """Factorisation : « Nouveau polynôme » tire un exercice en Python (énoncé « Factoriser : … »), « Afficher le corrigé » donne la carte finale."""
        if "factorisation" not in CHOISIS:
            self.skipTest("hors de OUTILS")
        page = self.ouvrir("factorisation")
        for _ in range(2):
            page.evaluer("document.querySelector('#exoHasard').click()")
            page.attendre("document.querySelector('#exoEnonce annotation')", 30)
            self.assertTrue(page.evaluer("document.querySelector('#exoEnonce annotation').textContent").startswith("Factoriser : "))
        enonce = page.evaluer("document.querySelector('#exoEnonce annotation').textContent")
        page.evaluer("document.querySelector('#exoCorrige').click()")
        page.attendre("document.querySelector('#cartes .card.final .badge')", 60)
        self.assertEqual(page.evaluer("document.querySelector('#entree').value"), "")        # le corrigé ne touche pas à la saisie
        self.assertIn(page.evaluer("document.querySelector('#cartes .card.final .res annotation').textContent").split(" = ")[0].replace(" ", ""),
                      enonce.replace(" ", "").replace("Factoriser:", ""))

    def test_t21_factorisation_une_carte_par_application(self):
        """FA-04 : x⁴ − 13x² + 36 donne 4 cartes d'étape (une par application de méthode) puis le bilan ; « Étape suivante » les montre une à une."""
        if "factorisation" not in CHOISIS:
            self.skipTest("hors de OUTILS")
        page = self.ouvrir("factorisation")
        page.evaluer("document.querySelector('#entree').value = 'x^4-13x^2+36'; document.querySelector('#calculer').click()")
        page.attendre("document.querySelector('#cartes').children.length > 0 && !document.querySelector('#calculer').disabled", 120)
        self.assertEqual(page.evaluer("document.querySelector('#progression').textContent"), "Étape 1 / 5")
        self.assertEqual(page.evaluer("[...document.querySelectorAll('#cartes .card')].map(c => c.querySelector('.badge').textContent)"),
                         ["Changement de variable", "Somme-Produit", "Changement de variable", "Différence de carrés",
                          "Changement de variable · Somme-Produit · Différence de carrés"])
        self.assertEqual(page.evaluer("document.querySelectorAll('#cartes .card:not(.cache)').length"), 1)
        page.evaluer("document.querySelector('#suivant').click()")
        self.assertEqual(page.evaluer("document.querySelectorAll('#cartes .card:not(.cache)').length"), 2)
        page.evaluer("document.querySelector('#tout').click()")
        self.assertEqual(page.evaluer("document.querySelector('#cartes .card:last-child').classList.contains('final')"), True)

    def test_t33_el_exercice_tire_en_python(self):
        """Exponentielles et logarithmes : « Nouvelle équation » tire un exercice en Python (énoncé « Résoudre : … ») de chacun des niveaux
        du pool, et « Afficher le corrigé » donne la carte finale « Solution » (ou une erreur de lecture : jamais)."""
        if "exponentielles-logarithmes" not in CHOISIS:
            self.skipTest("hors de OUTILS")
        page = self.ouvrir("exponentielles-logarithmes")
        for _ in range(6):
            page.evaluer("document.querySelector('#exoHasard').click()")
            page.attendre("document.querySelector('#exoEnonce annotation')", 30)
            enonce = page.evaluer("document.querySelector('#exoEnonce annotation').textContent")
            self.assertTrue(enonce.startswith("Résoudre : "), enonce)
            page.evaluer("document.querySelector('#exoCorrige').click()")
            page.attendre("document.querySelector('#cartes .card.final')", 60)
            self.assertEqual(page.evaluer("document.querySelector('#entree').value"), "")        # le corrigé ne touche pas à la saisie
            self.assertFalse(page.evaluer("document.querySelector('#cartes .err')"), enonce)
            self.assertEqual(page.evaluer("document.querySelector('#cartes .card.final h3').textContent"), "Solution")

    def test_t33_el_clavier_virtuel(self):
        """Le clavier de la page écrit log_10(x)=e : log_, un nombre, parenthèses, =, e, et ln(, sqrt(, virgule."""
        if "exponentielles-logarithmes" not in CHOISIS:
            self.skipTest("hors de OUTILS")
        page = self.ouvrir("exponentielles-logarithmes")
        page.evaluer("document.querySelector('#entree').value=''")
        for t in ("log_", "10", "(", "x", ")", "=", "e"):
            page.evaluer("document.querySelector(" + json.dumps(f'#clavier button[data-t="{t}"]') + ").click()")
        self.assertEqual(page.evaluer("document.querySelector('#entree').value"), "log_10(x)=e")
        page.attendre("document.querySelector('#apercu .katex')", 10)
        self.assertFalse(page.evaluer("document.querySelector('#apercu .err')"))

    def test_t33_el_une_etape_par_ligne_sans_defilement_a_360_px(self):
        """Chaque chaîne de ⇔ est une grille « lien · expression · propriété » : à 360 px, aucune entrée de la batterie ne fait défiler la
        page ni aucun élément du corrigé (le ⇔ à gauche, la propriété sous l'expression), y compris la ligne du discriminant Δ et −99’999’995."""
        if "exponentielles-logarithmes" not in CHOISIS:
            self.skipTest("hors de OUTILS")
        page = self.ouvrir("exponentielles-logarithmes")
        page.taille(360)
        entrees = [e for e in entrees_el() if e.strip()]

        def sans_debordement(e, cle, etat):
            page.evaluer("document.querySelector('#tout') && !document.querySelector('#tout').disabled && document.querySelector('#tout').click()")
            debordements = page.evaluer("""(() => {
                const trop = [...document.querySelectorAll('#cartes *')].filter(n => n.scrollWidth > n.clientWidth + 1 && n.clientWidth > 0
                    && !n.closest('.katex') && getComputedStyle(n).display !== 'inline')
                    .map(n => n.className + ' ' + n.scrollWidth + '>' + n.clientWidth);
                return [document.documentElement.scrollWidth, window.innerWidth, trop.slice(0, 5)];
            })()""")
            self.assertLessEqual(debordements[0], debordements[1], (e, cle, etat, debordements))
            self.assertEqual(debordements[2], [], (e, cle, etat, debordements))

        for e in entrees + ["log(x^2+x+3)=0"]:
            with self.subTest(entree=e):
                self.calculer(page, e)
                for cle in page.evaluer("[...document.querySelectorAll('#variantes:not([hidden]) button')].map(b => b.dataset.variante)") or [None]:
                    if cle:                                                  # sélecteur de méthode : les deux variantes tiennent à 360 px
                        page.evaluer(f"document.querySelector('#variantes button[data-variante=\"{cle}\"]').click()")
                    sans_debordement(e, cle, "départ")
                    if page.evaluer("!!document.querySelector('#option:not([hidden])')"):          # la carte « Interprétation » aussi, case cochée ou non
                        page.evaluer("document.querySelector('#option input').click()")
                        sans_debordement(e, cle, "case inversée")
                        page.evaluer("document.querySelector('#option input').click()")
                if page.evaluer("!!document.querySelector('#variantes:not([hidden])')"):
                    page.evaluer("document.querySelector('#variantes button[data-variante=\"logarithmes\"]').click()")
        page.taille(1100)
        self.calculer(page, "log(5-x)=8")
        self.assertEqual(page.evaluer("document.querySelectorAll('#cartes .chaine').length"), 2)
        # sur grand écran la propriété est à droite de la ligne (3e colonne), sur écran étroit sous l'expression
        self.calculer(page, "2^(x-1)=3^x")
        page.evaluer("document.querySelector('#tout').click()")
        haut = lambda s: page.evaluer(f"(() => {{ const r = document.querySelector('#cartes .chaine {s}').getBoundingClientRect(); return [r.top, r.left]; }})()")
        self.assertAlmostEqual(haut(".ligne:nth-child(2) .prop")[0], haut(".ligne:nth-child(2) .expr")[0], delta=40)       # même ligne
        self.assertGreater(haut(".ligne:nth-child(2) .prop")[1], haut(".ligne:nth-child(2) .expr")[1])
        page.taille(360)
        self.calculer(page, "2^(x-1)=3^x")
        page.evaluer("document.querySelector('#tout').click()")
        self.assertGreater(haut(".ligne:nth-child(2) .prop")[0], haut(".ligne:nth-child(2) .expr")[0])
        self.assertEqual(haut(".ligne:nth-child(2) .prop")[1], haut(".ligne:nth-child(2) .expr")[1])
        page.taille(1100)

    def titres_et_badges(self, page):
        """Le badge (ou le titre) de chaque carte affichée."""
        return page.evaluer("[...document.querySelectorAll('#cartes .card:not(.cache)')].map(c => (c.querySelector('.badge') || c.querySelector('h3')).textContent)")

    def test_t33_el_selecteur_de_methode(self):
        """EL-19 : deux boutons côte à côte au-dessus de la résolution d'une équation exponentielle, « Logarithmes » choisi par défaut ; un clic change
        les cartes sans appeler le moteur ; le choix est gardé d'une équation à l'autre et après rechargement ; ni les équations logarithmiques ni
        les calculs n'ont de sélecteur."""
        if "exponentielles-logarithmes" not in CHOISIS:
            self.skipTest("hors de OUTILS")
        page = self.ouvrir("exponentielles-logarithmes")
        page.evaluer("try { localStorage.clear(); } catch (e) {}")
        self.assertFalse(page.evaluer("!!document.querySelector('#variantes')"))                  # pas de sélecteur avant un calcul
        self.calculer(page, "2^(x-1)=32")
        boutons = page.evaluer("[...document.querySelectorAll('#variantes button')].map(b => [b.textContent, b.getAttribute('aria-pressed'), b.type])")
        self.assertEqual(boutons, [["Même base / définition", "false", "button"], ["Logarithmes", "true", "button"]])
        self.assertEqual(page.evaluer("document.querySelector('#variantes').getAttribute('role')"), "group")
        self.assertEqual(page.evaluer("document.querySelector('#variantes').getAttribute('aria-label')"), "Méthode de résolution")
        # au-dessus de la résolution, côte à côte
        haut = page.evaluer("""(() => { const r = [...document.querySelectorAll('#variantes button')].map(b => b.getBoundingClientRect());
            return [r[0].top, r[1].top, r[0].right <= r[1].left, document.querySelector('#cartes').getBoundingClientRect().top - r[0].bottom]; })()""")
        self.assertEqual(haut[0], haut[1])
        self.assertTrue(haut[2])
        self.assertGreater(haut[3], 0)
        self.assertEqual(self.titres_et_badges(page), ["Logarithme des deux membres"])
        page.evaluer("document.querySelector('#tout').click()")
        self.assertEqual(self.titres_et_badges(page), ["Logarithme des deux membres", "Solution"])
        # un clic : instantané et sans appel au moteur
        page.evaluer("""window.__envois = 0; const o = Worker.prototype.postMessage;
            Worker.prototype.postMessage = function (...a) { window.__envois++; return o.apply(this, a); };""")
        page.evaluer("document.querySelector('#variantes button[data-variante=\"meme_base\"]').click()")
        self.assertEqual(self.titres_et_badges(page), ["Même base", "Solution"])                   # « Tout afficher » : tout reste affiché
        self.assertEqual(page.evaluer("document.querySelector('#variantes button[aria-pressed=true]').textContent"), "Même base / définition")
        self.assertEqual(page.evaluer("window.__envois"), 0)
        self.assertEqual(page.evaluer("document.querySelector('#progression').textContent"), "Étape 2 / 2")
        self.assertEqual(page.evaluer("document.querySelectorAll('#cartes .cache').length"), 0)
        # le choix est gardé d'une équation à l'autre
        self.calculer(page, "3^(x+1)=27")
        self.assertEqual(page.evaluer("document.querySelector('#variantes button[aria-pressed=true]').textContent"), "Même base / définition")
        self.assertEqual(self.titres_et_badges(page)[0], "Même base")
        # méthode A qui ne s'applique pas : le bouton reste cliquable et la carte le dit
        self.calculer(page, "3^x=20")
        page.evaluer("document.querySelector('#tout').click()")
        self.assertIn("n'est pas une puissance de", page.evaluer("document.querySelector('#cartes').textContent"))
        self.assertIn("il faut les logarithmes.", page.evaluer("document.querySelector('#cartes').textContent"))
        self.assertFalse(page.evaluer("!!document.querySelector('#cartes .card.final')"))
        # ni équation logarithmique, ni calcul, ni erreur : pas de sélecteur
        for entree in ("log(x+1)=7", "log_2(50)", "x<3"):
            self.calculer(page, entree)
            self.assertTrue(page.evaluer("document.querySelector('#variantes').hidden"), entree)
        self.calculer(page, "2^(x-1)=32")
        self.assertFalse(page.evaluer("document.querySelector('#variantes').hidden"))
        # le choix est gardé après un rechargement (localStorage)
        self.assertEqual(page.evaluer("localStorage.getItem('variante:exponentielles-logarithmes')"), "meme_base")
        page = self.ouvrir("exponentielles-logarithmes")
        self.calculer(page, "2^(x-1)=32")
        self.assertEqual(page.evaluer("document.querySelector('#variantes button[aria-pressed=true]').textContent"), "Même base / définition")
        page.evaluer("document.querySelector('#variantes button[data-variante=\"logarithmes\"]').click()")
        self.assertEqual(page.evaluer("localStorage.getItem('variante:exponentielles-logarithmes')"), "logarithmes")

    def test_t33_el_selecteur_au_clavier_et_a_360_px(self):
        """Les boutons se prennent au clavier (focus visible, Entrée et Espace), restent côte à côte à 360 px et ne font pas défiler la page."""
        if "exponentielles-logarithmes" not in CHOISIS:
            self.skipTest("hors de OUTILS")
        page = self.ouvrir("exponentielles-logarithmes")
        page.evaluer("try { localStorage.clear(); } catch (e) {}")
        page.taille(360)
        self.calculer(page, "2^(x-1)=3^x")
        page.evaluer("document.querySelector('#tout').click()")
        mesures = page.evaluer("""(() => { const r = [...document.querySelectorAll('#variantes button')].map(b => b.getBoundingClientRect());
            return [r[0].top, r[1].top, r[0].width, r[1].width, r[1].right, document.documentElement.scrollWidth, window.innerWidth,
                    r[0].height >= 36]; })()""")
        self.assertEqual(mesures[0], mesures[1])                                  # côte à côte
        self.assertAlmostEqual(mesures[2], mesures[3], delta=1)
        self.assertLessEqual(mesures[4], mesures[6])
        self.assertLessEqual(mesures[5], mesures[6])
        self.assertTrue(mesures[7])
        # clavier : focus, puis Entrée et Espace déclenchent le bouton
        def touche(key, code, vk):
            for type_ in ("keyDown", "keyUp"):
                params = dict(type=type_, key=key, code=code, windowsVirtualKeyCode=vk)
                if type_ == "keyDown" and key == "Enter":
                    params["text"] = "\r"
                if type_ == "keyDown" and key == " ":
                    params["text"] = " "
                page.appel("Input.dispatchKeyEvent", **params)
        page.evaluer("document.querySelector('#variantes button[data-variante=\"meme_base\"]').focus()")
        self.assertEqual(page.evaluer("document.activeElement.dataset.variante"), "meme_base")
        outline = page.evaluer("getComputedStyle(document.activeElement).outlineStyle")
        self.assertNotEqual(outline, "none")                                      # focus visible (:focus-visible)
        touche("Enter", "Enter", 13)
        page.attendre("document.querySelector('#variantes button[aria-pressed=true]').dataset.variante === 'meme_base'", 5)
        page.evaluer("document.querySelector('#variantes button[data-variante=\"logarithmes\"]').focus()")
        touche(" ", "Space", 32)
        page.attendre("document.querySelector('#variantes button[aria-pressed=true]').dataset.variante === 'logarithmes'", 5)
        page.taille(1100)

    def test_t33_el_selecteur_sans_localstorage(self):
        """localStorage refusé (fenêtre privée, données bloquées) : la page marche, le défaut est « Logarithmes » et le choix reste pour la page."""
        if "exponentielles-logarithmes" not in CHOISIS:
            self.skipTest("hors de OUTILS")
        page = self.nav.ouvrir("exponentielles-logarithmes/index.html", script_initial="""
            for (const m of ['getItem', 'setItem', 'removeItem', 'clear']) Storage.prototype[m] = function () { throw new Error('refusé'); };""")
        attendre_pret(page)
        self.calculer(page, "2^(x-1)=32")
        self.assertEqual(page.evaluer("document.querySelector('#variantes button[aria-pressed=true]').textContent"), "Logarithmes")
        page.evaluer("document.querySelector('#variantes button[data-variante=\"meme_base\"]').click()")
        self.assertEqual(page.evaluer("document.querySelector('#variantes button[aria-pressed=true]').textContent"), "Même base / définition")
        self.calculer(page, "3^x=27")
        self.assertEqual(page.evaluer("document.querySelector('#variantes button[aria-pressed=true]').textContent"), "Même base / définition")
        self.assertFalse(page.evaluer("document.querySelector('#cartes .err')"))

    def test_t33_el_selecteur_a_l_impression(self):
        """L'impression montre la méthode affichée : le sélecteur disparaît, la ligne « Méthode : … » apparaît, seules les cartes de la méthode sont là."""
        if "exponentielles-logarithmes" not in CHOISIS:
            self.skipTest("hors de OUTILS")
        page = self.ouvrir("exponentielles-logarithmes")
        page.evaluer("try { localStorage.clear(); } catch (e) {}")
        self.calculer(page, "2^(x-1)=32")
        affichage = lambda: page.evaluer("""[getComputedStyle(document.querySelector('#variantes')).display,
            getComputedStyle(document.querySelector('#methodeImprimee')).display, document.querySelector('#methodeImprimee').textContent]""")
        self.assertEqual(affichage()[:2], ["flex", "none"])                         # à l'écran : le sélecteur, pas la ligne d'impression
        page.taille(1100, imprimante=True)
        self.assertEqual(affichage(), ["none", "block", "Méthode : Logarithmes"])
        page.taille(1100)
        page.evaluer("document.querySelector('#variantes button[data-variante=\"meme_base\"]').click()")
        page.taille(1100, imprimante=True)
        self.assertEqual(affichage(), ["none", "block", "Méthode : Même base / définition"])
        page.evaluer("document.querySelector('#tout').click()")
        self.assertEqual(page.evaluer("document.querySelectorAll('#cartes .card:not(.cache)').length"), 2)
        page.taille(1100)

    def test_t33_el_selecteur_dans_l_exercice_au_hasard(self):
        """Les exercices au hasard passent par la même page de corrigé : le sélecteur est là pour une équation exponentielle, absent pour une
        équation logarithmique."""
        if "exponentielles-logarithmes" not in CHOISIS:
            self.skipTest("hors de OUTILS")
        page = self.ouvrir("exponentielles-logarithmes")
        page.evaluer("try { localStorage.clear(); } catch (e) {}")
        vus = set()
        for _ in range(14):
            page.evaluer("document.querySelector('#exoHasard').click()")
            page.attendre("document.querySelector('#exoEnonce annotation')", 30)
            enonce = page.evaluer("document.querySelector('#exoEnonce annotation').textContent")
            page.evaluer("document.querySelector('#exoCorrige').click()")
            page.attendre("document.querySelector('#cartes .card.final, #cartes .card:last-child')", 60)
            exponentielle = not re.search(r"\\log|\\ln", enonce)
            self.assertEqual(page.evaluer("!!document.querySelector('#variantes') && !document.querySelector('#variantes').hidden"), exponentielle, enonce)
            vus.add(exponentielle)
            if len(vus) == 2:
                break
        self.assertEqual(vus, {True, False})

    def titres(self, page):
        return page.evaluer("[...document.querySelectorAll('#cartes .card:not(.cache)')].map(c => c.querySelector('h3').childNodes[0].textContent.trim())")

    def test_t33_el_case_probleme_d_application(self):
        """EL-24 : la case « Problème d'application (temps en années) » est pré-cochée avec un paramètre ou l'inconnue n, décochable, ajoute et retire la
        carte « Interprétation » sans appel au moteur, garde son état au changement de méthode, et n'existe pas pour une équation logarithmique."""
        if "exponentielles-logarithmes" not in CHOISIS:
            self.skipTest("hors de OUTILS")
        page = self.ouvrir("exponentielles-logarithmes")
        page.evaluer("try { localStorage.clear(); } catch (e) {}")
        self.assertFalse(page.evaluer("!!document.querySelector('#option')"))                      # pas de case avant un calcul
        self.calculer(page, "3Q=Q(1+3,75/100)^x")
        self.assertEqual(page.evaluer("[document.querySelector('#option').hidden, document.querySelector('#option').textContent.trim(), "
                                      "document.querySelector('#option input').checked, document.querySelector('#option input').type]"),
                         [False, "Problème d'application (temps en années)", True, "checkbox"])
        page.evaluer("document.querySelector('#tout').click()")
        self.assertEqual(self.titres(page), ["Étape 1", "Étape 2", "Étape 3", "Solution", "Interprétation"])
        self.assertIn("Au bout de 29 ans, 10 mois et 4 jours.", page.evaluer("document.querySelector('#cartes .card:last-child').textContent"))
        self.assertEqual(page.evaluer("document.querySelector('#progression').textContent"), "Étape 5 / 5")
        # décocher : la carte disparaît, sans appel au moteur
        page.evaluer("""window.__envois = 0; const o = Worker.prototype.postMessage;
            Worker.prototype.postMessage = function (...a) { window.__envois++; return o.apply(this, a); };""")
        page.evaluer("document.querySelector('#option input').click()")
        self.assertEqual(self.titres(page), ["Étape 1", "Étape 2", "Étape 3", "Solution"])
        self.assertEqual(page.evaluer("document.querySelector('#progression').textContent"), "Étape 4 / 4")
        page.evaluer("document.querySelector('#option input').click()")
        self.assertEqual(self.titres(page)[-1], "Interprétation")
        self.assertEqual(page.evaluer("window.__envois"), 0)
        # le choix est gardé au changement de méthode ; la méthode A, qui ne conclut pas, n'a pas de case
        page.evaluer("document.querySelector('#option input').click()")
        page.evaluer("document.querySelector('#variantes button[data-variante=\"meme_base\"]').click()")
        self.assertTrue(page.evaluer("document.querySelector('#option').hidden"))
        self.assertNotIn("Interprétation", self.titres(page))
        page.evaluer("document.querySelector('#variantes button[data-variante=\"logarithmes\"]').click()")
        self.assertFalse(page.evaluer("document.querySelector('#option').hidden"))
        self.assertFalse(page.evaluer("document.querySelector('#option input').checked"))          # décochée avant : elle le reste
        self.assertNotIn("Interprétation", self.titres(page))
        # recalculer la même équation garde le choix ; une autre équation reprend l'état de départ
        self.calculer(page, "3Q=Q(1+3,75/100)^x")
        self.assertFalse(page.evaluer("document.querySelector('#option input').checked"))
        for entree, coche in [("2000*1,045^n=3805", True), ("2^x=100", False), ("37*e^(-0,02t)=25", False), ("2C=C(1+0,04)^n", True)]:
            self.calculer(page, entree)
            self.assertEqual(page.evaluer("[document.querySelector('#option').hidden, document.querySelector('#option input').checked]"), [False, coche], entree)
            page.evaluer("document.querySelector('#tout').click()")
            self.assertEqual("Interprétation" in self.titres(page), coche, entree)
        # solution négative, S = ∅ : la case est là, la carte ne donne qu'une phrase
        self.calculer(page, "Q/2=Q*1,04^n")
        page.evaluer("document.querySelector('#tout').click()")
        self.assertIn("n'arrive jamais", page.evaluer("document.querySelector('#cartes .card:last-child').textContent"))
        # ni équation logarithmique, ni calcul, ni erreur, ni deux solutions : pas de case
        for entree in ("log(x+1)=7", "log_2(50)", "x<3", "2^(x^2)=8", "4^x=2^(2x)", "(x-1)(2^x-8)=0"):
            self.calculer(page, entree)
            self.assertTrue(page.evaluer("document.querySelector('#option').hidden"), entree)

    def test_t33_el_case_au_clavier_et_a_360_px(self):
        """La case se prend au clavier (focus visible, Espace) et reste lisible à 360 px, sans faire défiler la page."""
        if "exponentielles-logarithmes" not in CHOISIS:
            self.skipTest("hors de OUTILS")
        page = self.ouvrir("exponentielles-logarithmes")
        page.evaluer("try { localStorage.clear(); } catch (e) {}")
        page.taille(360)
        self.calculer(page, "2C=C(1+4,5%)^n")
        page.evaluer("document.querySelector('#tout').click()")
        mesures = page.evaluer("""(() => { const r = document.querySelector('#option').getBoundingClientRect(), c = document.querySelector('#option input').getBoundingClientRect();
            return [r.right <= window.innerWidth, r.left >= 0, c.width >= 20, document.documentElement.scrollWidth <= window.innerWidth,
                    r.bottom <= document.querySelector('#cartes').getBoundingClientRect().top]; })()""")
        self.assertEqual(mesures, [True] * 5)
        self.assertIn("Au bout de 15 ans, 9 mois et 0 jour.", page.evaluer("document.querySelector('#cartes').textContent"))      # report des 30 jours
        page.evaluer("document.querySelector('#option input').focus()")
        self.assertEqual(page.evaluer("document.activeElement.type"), "checkbox")
        self.assertNotEqual(page.evaluer("getComputedStyle(document.querySelector('#option')).outlineStyle"), "none")        # focus visible
        for type_ in ("keyDown", "keyUp"):
            params = dict(type=type_, key=" ", code="Space", windowsVirtualKeyCode=32)
            if type_ == "keyDown":
                params["text"] = " "
            page.appel("Input.dispatchKeyEvent", **params)
        page.attendre("!document.querySelector('#option input').checked", 5)
        self.assertNotIn("Interprétation", self.titres(page))
        page.taille(1100)

    def test_t33_el_case_a_l_impression(self):
        """À l'impression, la case disparaît ; la carte « Interprétation » est imprimée si elle est cochée, absente sinon."""
        if "exponentielles-logarithmes" not in CHOISIS:
            self.skipTest("hors de OUTILS")
        page = self.ouvrir("exponentielles-logarithmes")
        page.evaluer("try { localStorage.clear(); } catch (e) {}")
        self.calculer(page, "3Q=Q(1+3,75/100)^x")
        page.evaluer("document.querySelector('#tout').click()")
        affichage = lambda: page.evaluer("""[getComputedStyle(document.querySelector('#option')).display,
            [...document.querySelectorAll('#cartes .card')].filter(c => getComputedStyle(c).display !== 'none').map(c => c.querySelector('h3').childNodes[0].textContent.trim())]""")
        self.assertEqual(affichage()[0], "flex")
        page.taille(1100, imprimante=True)
        self.assertEqual(affichage(), ["none", ["Étape 1", "Étape 2", "Étape 3", "Solution", "Interprétation"]])
        page.taille(1100)
        page.evaluer("document.querySelector('#option input').click()")
        page.taille(1100, imprimante=True)
        self.assertEqual(affichage(), ["none", ["Étape 1", "Étape 2", "Étape 3", "Solution"]])
        page.taille(1100)

    def test_t33_el_case_dans_l_exercice_au_hasard(self):
        """Un exercice au hasard avec paramètre ou inconnue n a la case pré-cochée : le corrigé se termine par « Interprétation »."""
        if "exponentielles-logarithmes" not in CHOISIS:
            self.skipTest("hors de OUTILS")
        page = self.ouvrir("exponentielles-logarithmes")
        vus = 0
        for _ in range(40):
            page.evaluer("document.querySelector('#exoHasard').click()")
            page.attendre("document.querySelector('#exoEnonce annotation')", 30)
            enonce = page.evaluer("document.querySelector('#exoEnonce annotation').textContent")
            if "^{n}" not in enonce:
                continue
            page.evaluer("document.querySelector('#exoCorrige').click()")
            page.attendre("document.querySelector('#cartes .card.final')", 60)
            page.evaluer("document.querySelector('#tout').click()")
            self.assertTrue(page.evaluer("document.querySelector('#option input').checked"), enonce)
            self.assertEqual(self.titres(page)[-1], "Interprétation", enonce)
            vus += 1
            if vus == 3:
                break
        self.assertGreaterEqual(vus, 1)

    def test_t33_selecteur_absent_des_autres_outils(self):
        """Le sélecteur ne change pas les autres outils : aucun #variantes ni #methodeImprimee dans leur page après un calcul."""
        for outil in OUTILS:
            if outil == "exponentielles-logarithmes" or outil not in CHOISIS:
                continue
            with self.subTest(outil=outil):
                page = self.ouvrir(outil)
                self.calculer(page, CALCUL[outil])
                self.assertFalse(page.evaluer("!!document.querySelector('#variantes') || !!document.querySelector('#methodeImprimee') || !!document.querySelector('#option')"))
                self.assertFalse(page.evaluer("!!document.querySelector('#filiere') || !!document.querySelector('#filiereImprimee')"))          # T35 : pas de filière

    # ---------- T35 : filière M (2Ms, 2Mr) de l'outil « Exponentielles et logarithmes » ----------
    def filiere(self, page):
        """La filière affichée par l'interrupteur (« C » ou « M »)."""
        return page.evaluer("(document.querySelector('#filiere button[aria-pressed=true]') || {dataset: {}}).dataset.filiere")

    def badges(self, page):
        return page.evaluer("[...document.querySelectorAll('#cartes .card')].map(c => (c.querySelector('.badge') || c.querySelector('h3')).textContent)")

    def test_t35_el_filiere_de_depart_url_accueil_puis_defaut(self):
        """EL-33 : ?filiere=M gagne, sinon la filière mémorisée par l'accueil (Ms et Mr → M ; C, « tous » → C), sinon C ; une valeur inconnue est ignorée."""
        if "exponentielles-logarithmes" not in CHOISIS:
            self.skipTest("hors de OUTILS")
        page = self.ouvrir("exponentielles-logarithmes")
        page.evaluer("try { localStorage.clear(); } catch (e) {}")
        for stockage, requete, attendu in [(None, "", "C"), (None, "?filiere=M", "M"), (None, "?filiere=C", "C"), (None, "?filiere=Z", "C"),
                                           ("Ms", "", "M"), ("Mr", "", "M"), ("C", "", "C"), ("tous", "", "C"), ("Ms", "?filiere=C", "C"), ("C", "?filiere=M", "M")]:
            with self.subTest(stockage=stockage, requete=requete):
                script = "try { localStorage.clear(); " + (f"localStorage.setItem('samimir-track', '{stockage}');" if stockage else "") + " } catch (e) {}"
                page = self.nav.ouvrir(f"exponentielles-logarithmes/index.html{requete}", script_initial=script)
                attendre_pret(page)
                self.assertEqual(self.filiere(page), attendu)
                self.assertEqual(page.evaluer("[...document.querySelectorAll('#filiere button')].map(b => b.textContent + ':' + b.getAttribute('aria-pressed'))"),
                                 ["3C:" + str(attendu == "C").lower(), "2M:" + str(attendu == "M").lower()])
                self.assertEqual(page.evaluer("document.querySelector('#rappelM').hidden"), attendu != "M")
                self.assertEqual(page.evaluer("document.querySelector('#rappelC').hidden"), attendu == "M")

    def test_t35_el_interrupteur_recalcule_met_l_url_a_jour_et_change_les_exemples(self):
        if "exponentielles-logarithmes" not in CHOISIS:
            self.skipTest("hors de OUTILS")
        page = self.nav.ouvrir("exponentielles-logarithmes/index.html?f=log(5-x)=8", script_initial="try { localStorage.clear(); } catch (e) {}")
        attendre_pret(page)
        page.attendre("document.querySelector('#cartes').children.length > 0 && !document.querySelector('#calculer').disabled", 120)
        self.assertEqual(self.filiere(page), "C")
        self.assertNotIn("Ensemble de définition", self.badges(page))                       # 3C : pas d'ensemble de définition
        exemples_c = page.evaluer("[...document.querySelectorAll('#exemples button')].map(b => b.dataset.ex)")
        page.evaluer("document.querySelector('#filiere button[data-filiere=M]').click()")
        page.attendre("document.querySelector('#cartes .badge') && /Ensemble/.test(document.querySelector('#cartes .badge').textContent)", 60)
        self.assertEqual(self.filiere(page), "M")
        self.assertEqual(page.evaluer("document.querySelector('#entree').value"), "log(5-x)=8")          # le recalcul ne touche pas à la saisie
        self.assertIn("filiere=M", page.evaluer("location.search"))
        self.assertIn("f=log", page.evaluer("decodeURIComponent(location.search)"))             # les autres paramètres restent
        self.assertEqual(self.badges(page)[0], "Ensemble de définition")
        self.assertEqual(self.badges(page)[-1], "Solution")
        exemples_m = page.evaluer("[...document.querySelectorAll('#exemples button')].map(b => b.dataset.ex)")
        self.assertNotEqual(exemples_c, exemples_m)
        self.assertIn("log(x)+log(x-1)=1", exemples_m)
        self.assertEqual(page.evaluer("document.querySelector('#rappelM').hidden"), False)
        page.evaluer("document.querySelector('#exemples button[data-ex=\"log(x)+log(x-1)=1\"]').click()")
        page.attendre("document.querySelector('#cartes .card.final')", 60)
        self.assertIn("Vérification", self.badges(page))
        page.attendre("!document.querySelector('#calculer').disabled", 60)                         # un clic sur le bouton pendant le calcul de l'exemple serait perdu
        self.calculer(page, "log(5-x)=8")
        page.attendre("/5 - x/.test(document.querySelector('#cartes').textContent)", 60)         # `calculer` rend la main sur les cartes de l'exemple : attendre les nouvelles
        page.evaluer("document.querySelector('#filiere button[data-filiere=C]').click()")        # retour en 3C : la même saisie, sans ensemble de définition
        page.attendre("document.querySelector('#cartes .card.final') && !/Ensemble/.test(document.querySelector('#cartes').textContent)", 60)
        self.assertEqual(self.filiere(page), "C")
        self.assertIn("filiere=C", page.evaluer("location.search"))
        # le calcul d'une nouvelle équation suit la filière choisie
        self.calculer(page, "4^x-2^x-6=0")
        self.assertTrue(page.evaluer("!!document.querySelector('#cartes .err')"))                # 3C : « ne se résout pas avec les méthodes du cours »
        page.evaluer("document.querySelector('#filiere button[data-filiere=M]').click()")
        page.attendre("document.querySelector('#cartes .card') && /Changement de variable/.test(document.querySelector('#cartes').textContent)", 60)
        self.assertTrue(page.evaluer("!!document.querySelector('#variantes') && !document.querySelector('#variantes').hidden"))     # le sélecteur de méthode aussi
        self.assertFalse(page.evaluer("!!document.querySelector('#option:not([hidden])')"))                                           # pas de case d'application

    def test_t35_el_exercice_au_hasard_de_la_filiere_m(self):
        """Le pool M : les six niveaux, chaque exercice se corrige en filière M (carte « Ensemble de définition » pour un logarithme) ; en changeant de
        filière, l'exercice affiché (celui de l'autre pool) disparaît."""
        if "exponentielles-logarithmes" not in CHOISIS:
            self.skipTest("hors de OUTILS")
        page = self.ouvrir("exponentielles-logarithmes", "?filiere=M")
        vus = set()
        for _ in range(14):
            page.evaluer("document.querySelector('#exoHasard').click()")
            page.attendre("document.querySelector('#exoEnonce annotation')", 30)
            enonce = page.evaluer("document.querySelector('#exoEnonce annotation').textContent")
            self.assertTrue(enonce.startswith("Résoudre : "), enonce)
            vus.add(enonce)
            page.evaluer("document.querySelector('#exoCorrige').click()")
            page.attendre("document.querySelector('#cartes .card.final')", 60)
            self.assertFalse(page.evaluer("document.querySelector('#cartes .err')"), enonce)
            self.assertEqual(page.evaluer("document.querySelector('#cartes .card.final h3').textContent"), "Solution")
            texte = page.evaluer("document.querySelector('#cartes').textContent")
            if "ln" in enonce or "log" in enonce:
                self.assertIn("Ensemble de définition", texte, enonce)
        self.assertGreater(len(vus), 6)
        page.evaluer("document.querySelector('#filiere button[data-filiere=C]').click()")
        self.assertEqual(page.evaluer("document.querySelector('#exoCorrige').hidden"), True)
        self.assertIn("Cliquez sur", page.evaluer("document.querySelector('#exoEnonce').textContent"))

    def test_t35_el_interrupteur_au_clavier_et_a_360_px(self):
        """Les deux boutons se prennent au clavier (Entrée, Espace), restent côte à côte à 360 px et ne font pas défiler la page."""
        if "exponentielles-logarithmes" not in CHOISIS:
            self.skipTest("hors de OUTILS")
        page = self.ouvrir("exponentielles-logarithmes")
        page.taille(360)
        mesures = page.evaluer("""(() => { const r = [...document.querySelectorAll('#filiere button')].map(b => b.getBoundingClientRect());
            return [r[0].top, r[1].top, r[0].width, r[1].width, r[1].right, document.documentElement.scrollWidth, window.innerWidth, r[0].height >= 36]; })()""")
        self.assertEqual(mesures[0], mesures[1])
        self.assertAlmostEqual(mesures[2], mesures[3], delta=1)
        self.assertLessEqual(mesures[4], mesures[6])
        self.assertLessEqual(mesures[5], mesures[6])
        self.assertTrue(mesures[7])

        def touche(key, code, vk):
            for type_ in ("keyDown", "keyUp"):
                params = dict(type=type_, key=key, code=code, windowsVirtualKeyCode=vk)
                if type_ == "keyDown" and key == "Enter":
                    params["text"] = "\r"
                if type_ == "keyDown" and key == " ":
                    params["text"] = " "
                page.appel("Input.dispatchKeyEvent", **params)
        page.evaluer("document.querySelector('#filiere button[data-filiere=M]').focus()")
        self.assertNotEqual(page.evaluer("getComputedStyle(document.activeElement).outlineStyle"), "none")
        touche("Enter", "Enter", 13)
        page.attendre("document.querySelector('#filiere button[aria-pressed=true]').dataset.filiere === 'M'", 5)
        page.evaluer("document.querySelector('#filiere button[data-filiere=C]').focus()")
        touche(" ", "Space", 32)
        page.attendre("document.querySelector('#filiere button[aria-pressed=true]').dataset.filiere === 'C'", 5)
        page.taille(1100)

    def test_t35_el_filiere_sans_localstorage(self):
        if "exponentielles-logarithmes" not in CHOISIS:
            self.skipTest("hors de OUTILS")
        page = self.nav.ouvrir("exponentielles-logarithmes/index.html", script_initial="""
            for (const m of ['getItem', 'setItem', 'removeItem', 'clear']) Storage.prototype[m] = function () { throw new Error('refusé'); };""")
        attendre_pret(page)
        self.assertEqual(self.filiere(page), "C")
        page.evaluer("document.querySelector('#filiere button[data-filiere=M]').click()")
        self.calculer(page, "log(x)+log(x-1)=1")
        self.assertEqual(self.badges(page)[0], "Ensemble de définition")

    def test_t35_el_filiere_a_l_impression(self):
        """L'impression montre la filière : l'interrupteur disparaît, la ligne « Filière : 2M » apparaît."""
        if "exponentielles-logarithmes" not in CHOISIS:
            self.skipTest("hors de OUTILS")
        page = self.ouvrir("exponentielles-logarithmes", "?filiere=M")
        self.calculer(page, "log(x)+log(x-1)=1")
        affichage = lambda: page.evaluer("""[getComputedStyle(document.querySelector('#filiere')).display,
            getComputedStyle(document.querySelector('#filiereImprimee')).display, document.querySelector('#filiereImprimee').textContent]""")
        self.assertEqual(affichage()[:2], ["flex", "none"])
        page.taille(1100, imprimante=True)
        self.assertEqual(affichage(), ["none", "block", "Filière : 2M"])
        page.taille(1100)
        page.evaluer("document.querySelector('#filiere button[data-filiere=C]').click()")
        page.taille(1100, imprimante=True)
        self.assertEqual(affichage()[2], "Filière : 3C")
        page.taille(1100)

    def test_t35_el_filiere_m_une_etape_par_ligne_sans_defilement_a_360_px(self):
        """Toutes les entrées M (ensemble de définition avec tableaux de signes, vérification, changement de variable) tiennent à 360 px, dans chaque méthode."""
        if "exponentielles-logarithmes" not in CHOISIS:
            self.skipTest("hors de OUTILS")
        page = self.ouvrir("exponentielles-logarithmes", "?filiere=M")
        page.taille(360)
        entrees = [e for e in entrees_el_m() if e.strip()] + [e for e, _ in BATTERIE_M_VAR]
        for e in dict.fromkeys(entrees):
            with self.subTest(entree=e):
                self.calculer(page, e)
                for cle in page.evaluer("[...document.querySelectorAll('#variantes:not([hidden]) button')].map(b => b.dataset.variante)") or [None]:
                    if cle:
                        page.evaluer(f"document.querySelector('#variantes button[data-variante=\"{cle}\"]').click()")
                    page.evaluer("document.querySelector('#tout') && !document.querySelector('#tout').disabled && document.querySelector('#tout').click()")
                    debordements = page.evaluer("""(() => {
                        const trop = [...document.querySelectorAll('#cartes *')].filter(n => n.scrollWidth > n.clientWidth + 1 && n.clientWidth > 0
                            && !n.closest('.katex') && !n.closest('.tsigne') && getComputedStyle(n).display !== 'inline')
                            .map(n => n.className + ' ' + n.scrollWidth + '>' + n.clientWidth);
                        return [document.documentElement.scrollWidth, window.innerWidth, trop.slice(0, 5)];
                    })()""")                                                  # un tableau de signes défile dans son cadre (.tsigne), comme sur la page de l'ED
                    self.assertLessEqual(debordements[0], debordements[1], (e, cle, debordements))
                    self.assertEqual(debordements[2], [], (e, cle, debordements))
                if page.evaluer("!!document.querySelector('#variantes:not([hidden])')"):
                    page.evaluer("document.querySelector('#variantes button[data-variante=\"logarithmes\"]').click()")
        page.taille(1100)

    def test_t31_libelle_pendant_le_chargement_de_sympy(self):
        """Pages à `sympyAvant` : un calcul lancé avant « Prêt. » affiche « Chargement du moteur de calcul pour cette fonction… »
        (le calcul n'a pas commencé), puis « Calcul en cours… » quand SymPy est là, puis « Prêt. »."""
        for outil in ("derivee-variations", "limites-asymptotes", "etude-complete"):
            with self.subTest(outil=outil):
                if outil not in CHOISIS:
                    continue
                page = self.nav.ouvrir(f"{outil}/index.html")
                page.attendre("document.querySelector('#etat').textContent === 'Chargement du moteur de calcul…' "
                              "&& !document.querySelector('#calculer').disabled", 240, pas=0.02)
                page.evaluer(f"""(() => {{
                    const etat = document.querySelector('#etat'), vu = window.__etats = [];
                    new MutationObserver(() => {{ const t = etat.textContent; if (vu[vu.length - 1] !== t) vu.push(t); }})
                        .observe(etat, {{ childList: true, characterData: true, subtree: true }});
                    document.querySelector('#entree').value = {CALCUL[outil]!r}; document.querySelector('#calculer').click(); }})()""")
                page.attendre("document.querySelector('#cartes').children.length > 0 && !document.querySelector('#calculer').disabled", 120)
                historique = [t for t in page.evaluer("window.__etats")]
                self.assertEqual(historique[-1], "Prêt.")
                historique = [t for i, t in enumerate(historique) if t != "Prêt." or i == len(historique) - 1]   # « Prêt. » passe un instant quand SymPy arrive
                self.assertEqual(historique, ["Chargement du moteur de calcul pour cette fonction…", "Calcul en cours…", "Prêt."])

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
