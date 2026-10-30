"""Tests de page — « Programmation linéaire » (simplexe/index.html, page autonome sans Pyodide) :
A. formulaire vide à l'ouverture, les exemples ne remplissent qu'au clic ; B. saisie des négatifs et des fractions au clavier du
téléphone ; C. vue « Solution complète » (cartes à la suite, figures paresseuses) pour les deux méthodes (chantier du 30.10.2026)."""
import itertools
import json
import time
from fractions import Fraction
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(__file__))
from navigateur import Navigateur

CHOISI = not os.environ.get("OUTILS") or "simplexe" in os.environ["OUTILS"].split(",")

CHAMPS = "[...document.querySelectorAll('#objRow input, #consRows input')]"
LARGEURS = (360, 1100)


def optimum_exact(c, rows, sens):
    """Valeur optimale (Fraction) de sens(c·x) sous rows = [(a, op, b)] et x ≥ 0, par énumération exacte des sommets (le problème est supposé borné)."""
    n = len(c)
    cons = [([Fraction(x) for x in a], Fraction(b), op) for a, op, b in rows]
    cons += [([Fraction(int(i == j)) for j in range(n)], Fraction(0), ">=") for i in range(n)]
    meilleur = None
    for combo in itertools.combinations(range(len(cons)), n):
        M = [cons[i][0][:] + [cons[i][1]] for i in combo]
        for col in range(n):                                                        # Gauss-Jordan exact
            piv = next((r for r in range(col, n) if M[r][col] != 0), None)
            if piv is None:
                break
            M[col], M[piv] = M[piv], M[col]
            M[col] = [x / M[col][col] for x in M[col]]
            for r in range(n):
                if r != col and M[r][col] != 0:
                    M[r] = [x - M[r][col] * y for x, y in zip(M[r], M[col])]
        else:
            x = [M[i][n] for i in range(n)]
            if all((sum(ai * xi for ai, xi in zip(a, x)) <= b) if op == "<=" else (sum(ai * xi for ai, xi in zip(a, x)) >= b) for a, b, op in cons):
                v = sum(Fraction(ci) * xi for ci, xi in zip(c, x))
                if meilleur is None or (v > meilleur if sens == "max" else v < meilleur):
                    meilleur = v
    return meilleur


def format_nb(v):
    """Notation de nb() dans la page (méthode algébrique) : entier avec ’ entre les milliers, sinon deux décimales à la virgule, « − » pour le signe."""
    f = float(v)
    t = f"{round(f):,}".replace(",", "’") if abs(f - round(f)) < 1e-9 else f"{f:.2f}".replace(".", ",")
    return t.replace("-", "−")


def format_plain(v):
    """Notation de plain() (méthode géométrique) : entier, ou fraction n/d."""
    return str(v.numerator) if v.denominator == 1 else f"{v.numerator}/{v.denominator}"


@unittest.skipUnless(CHOISI, "hors de OUTILS")
class TestSimplexe(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.nav = Navigateur().__enter__()

    @classmethod
    def tearDownClass(cls):
        cls.nav.__exit__(None, None, None)

    def ouvrir(self, largeur=1100, requete=""):
        page = self.nav.ouvrir(f"simplexe/index.html{requete}")
        page.attendre("document.readyState === 'complete' && document.querySelector('#objRow input')", 30)
        page.taille(largeur, 800)
        return page

    def clic(self, page, selecteur):
        page.evaluer(f"document.querySelector({selecteur!r}).click()")

    def defile_horizontalement(self, page):
        return page.evaluer("document.documentElement.scrollWidth - innerWidth") > 0

    # ---------- A. aucun champ prérempli ----------
    def test_a_formulaire_vide_a_l_ouverture_et_exemple_au_clic(self):
        for largeur in LARGEURS:
            with self.subTest(largeur=largeur):
                page = self.ouvrir(largeur)
                # fonction économique vide, trois contraintes vides (≤), 2 variables, « Maximiser », méthode algébrique
                self.assertEqual(page.evaluer(f"{CHAMPS}.map(i => i.value)"), [""] * (2 + 3 * 3))
                self.assertEqual(page.evaluer("document.querySelectorAll('#objRow input').length"), 2)
                self.assertEqual(page.evaluer("document.querySelectorAll('#consRows .coefs').length"), 3)
                self.assertEqual(page.evaluer("[...document.querySelectorAll('#consRows .opb')].map(b => b.textContent)"), ["≤"] * 3)
                self.assertEqual(page.evaluer("[...document.querySelectorAll('.row button.on')].map(b => b.textContent.trim())"),
                                 ["2Mr/OS · Méthode algébrique", "2 variables (polygone)", "Maximiser"])
                self.assertFalse(self.defile_horizontalement(page))
                # un exemple ne remplit qu'au clic
                self.clic(page, '[data-ex="Exemple 2D"]')
                self.assertEqual(page.evaluer(f"{CHAMPS}.map(i => i.value)"), ["100", "120", "3", "4", "4200", "1", "3", "2400", "2", "2", "2600"])
                self.clic(page, '[data-ex="Exemple 3D"]')
                self.assertEqual(page.evaluer("document.querySelectorAll('#objRow input').length"), 3)
                self.assertEqual(page.evaluer("document.querySelector('#objRow input').value"), "6")
                self.assertFalse(self.defile_horizontalement(page))

    def test_a_lancer_a_vide_donne_des_messages_clairs_au_vouvoiement(self):
        page = self.ouvrir(360)
        for methode in ("simplexe", "para"):
            with self.subTest(methode=methode):
                self.clic(page, f'[data-meth="{methode}"]')
                self.clic(page, "#launch")
                self.assertEqual(page.evaluer("document.querySelector('#err').textContent"),
                                 "✗ Fonction économique vide : entrez au moins un coefficient non nul.")
                page.evaluer("(() => { const i = document.querySelector('#objRow input'); i.value = '2'; i.dispatchEvent(new Event('input')); })()")
                self.clic(page, "#launch")
                msg = page.evaluer("document.querySelector('#err').textContent")
                self.assertTrue(msg.startswith("✗ Il faut au moins une contrainte"), msg)
                self.assertIn("remplissez", msg)
                self.assertTrue(page.evaluer("document.querySelector('#app').hidden && document.querySelector('#appPara').hidden"))
                self.clic(page, '[data-ex="Exemple 2D"]' if methode == "simplexe" else '[data-ex="Parallèles : max"]')
                page.evaluer("[...document.querySelectorAll('#consRows input')].forEach(i => { i.value = ''; i.dispatchEvent(new Event('input')); })")
                self.clic(page, "#launch")
                msg = page.evaluer("document.querySelector('#err').textContent")
                self.assertTrue(msg.startswith("✗ Il faut au moins une contrainte"), msg)
                page.evaluer("location.reload()")                       # saisie remise à zéro pour la méthode suivante
                page.attendre("document.readyState === 'complete' && document.querySelector('#objRow input')", 30)

    def test_a_modifier_le_probleme_garde_la_saisie(self):
        for methode, exemple, apres in (("simplexe", "Exemple 2D", "#app"), ("para", "Parallèles : max", "#appPara")):
            with self.subTest(methode=methode):
                page = self.ouvrir(360)
                self.clic(page, f'[data-ex="{exemple}"]')
                page.evaluer("(() => { const i = document.querySelector('#objRow input'); i.value = '7'; i.dispatchEvent(new Event('input')); })()")
                saisie = page.evaluer(f"{CHAMPS}.map(i => i.value)")
                self.clic(page, "#launch")
                self.assertFalse(page.evaluer(f"document.querySelector({apres!r}).hidden"))
                self.clic(page, "#editBtn" if methode == "simplexe" else "#editBtnP")
                self.assertFalse(page.evaluer("document.querySelector('#formCard').hidden"))
                self.assertEqual(page.evaluer(f"{CHAMPS}.map(i => i.value)"), saisie)
                self.assertEqual(saisie[0], "7")
                if methode == "simplexe":                                # un redessin du formulaire (changement de variables) garde aussi les valeurs
                    self.clic(page, "[data-dim='3']")
                    self.assertEqual(page.evaluer("document.querySelector('#objRow input').value"), "7")

    # ---------- B. négatifs et fractions au clavier du téléphone ----------
    def test_b_lire_nombre_accepte_toutes_les_variantes_du_signe_moins(self):
        page = self.ouvrir(360)
        lire = "(t => { const f = lireNombre(t, 'x'); return f === null ? null : f.n.toString() + '/' + f.d.toString(); })(%s)"
        for texte, attendu in (("-3", "-3/1"), ("\u22123", "-3/1"), ("\u20133", "-3/1"), ("\u20143", "-3/1"), ("\u20103", "-3/1"), ("\u20113", "-3/1"),
                               ("-1/2", "-1/2"), ("\u22121/2", "-1/2"), ("-0,5", "-1/2"), ("-0.5", "-1/2"), ("0,5", "1/2"), ("1/2", "1/2"), ("+3", "3/1"),
                               (" - 3 ", "-3/1"), ("", None), ("   ", None)):
            with self.subTest(texte=texte):
                self.assertEqual(page.evaluer(lire % repr(texte).replace("'", '"')), attendu)
        for texte in ("3-", "--3", "1/-2", "1/2/3", "abc", "3\u2212\u22122", "1/0,5"):
            with self.subTest(refuse=texte):
                self.assertTrue(page.evaluer("(t => { try { lireNombre(t, 'x'); return false; } catch (e) { return e instanceof ErreurSaisie; } })(%s)" % repr(texte).replace("'", '"')))

    def test_b_aucun_champ_n_a_inputmode_decimal_et_aide_sous_le_formulaire(self):
        attendus = {"inputmode": "text", "autocomplete": "off", "autocorrect": "off", "autocapitalize": "off", "spellcheck": "false"}
        page = self.ouvrir(360)
        for methode, dim in (("simplexe", "2"), ("simplexe", "3"), ("para", "2")):
            with self.subTest(methode=methode, dim=dim):
                self.clic(page, f'[data-meth="{methode}"]')
                self.clic(page, f'[data-dim="{dim}"]')
                champs = page.evaluer(f"{CHAMPS}.map(i => Object.fromEntries(Object.keys({attendus!r}).map(a => [a, i.getAttribute(a)])))")
                self.assertEqual(len(champs), (2 if dim == "2" else 3) * 4 + 3)       # (fonction + 3 contraintes) × variables + 3 seconds membres
                for c in champs:
                    self.assertEqual(c, attendus)
                self.assertEqual(page.evaluer("document.querySelectorAll('input[inputmode=decimal], input[inputmode=numeric]').length"), 0)
                aide = page.evaluer("document.querySelector('#hint').textContent")
                self.assertTrue(aide.startswith("Nombres : 3, −2, 0,5 ou 1/2 ; case vide = 0."), aide)
                self.assertTrue(aide.endswith(")."), aide)                    # la suite propre à chaque méthode est gardée
                self.assertIn("graphique" if methode == "para" else "algébrique", aide)
        with open(os.path.join(os.path.dirname(__file__), "..", "..", "simplexe", "index.html"), encoding="utf-8") as f:
            self.assertNotRegex(f.read(), r'inputmode="(decimal|numeric)"')

    def test_b_negatifs_et_fractions_saisis_au_clavier(self):
        """Saisie par insertion de texte (comme un clavier de téléphone) : tiret demi-cadratin, signe moins, fraction ; le problème se lance."""
        for largeur in LARGEURS:
            with self.subTest(largeur=largeur):
                page = self.ouvrir(largeur)
                self.clic(page, '[data-meth="para"]')
                ligne = "#consRows .coefs:nth-child(1)"
                champs = [('#objRow input[data-j="0"]', "\u22123"), ('#objRow input[data-j="1"]', "1/2"),
                          (ligne + ' input[data-j="0"]', "1"), (ligne + ' input[data-j="1"]', "\u20131"), (ligne + " .rhs", "\u20142")]
                for selecteur, texte in champs:
                    page.taper(selecteur, texte, pause=0.01)
                    self.assertEqual(page.evaluer(f"document.querySelector({selecteur!r}).value"), texte)
                self.clic(page, "#launch")
                self.assertEqual(page.evaluer("document.querySelector('#err').textContent"), "")
                self.assertFalse(page.evaluer("document.querySelector('#appPara').hidden"))
                resume = page.evaluer("document.querySelector('#sumTxtP').innerHTML")
                self.assertIn('f = −3\u2009<i class="v">x</i> + <span class="fr"><span>1</span><span>2</span></span>', resume)     # −3 et 1/2 lus
                legende = page.evaluer("document.querySelector('#legendP').textContent")
                self.assertIn("x − y ≤ −2", legende)                           # coefficient −1 et second membre −2 lus
                self.assertFalse(self.defile_horizontalement(page))

    # ---------- C. solution complète ----------
    PIXELS = """(cv => { const d = cv.getContext('2d').getImageData(0, 0, cv.width, cv.height).data; let n = 0;
        for (let i = 4; i < d.length; i += 4) if (d[i] !== d[0] || d[i + 1] !== d[1] || d[i + 2] !== d[2]) n++; return n; })"""
    DEBORDEMENT = """(() => {
        const defile = n => { for (let m = n; m; m = m.parentElement) { const o = getComputedStyle(m).overflowX; if (o === 'auto' || o === 'scroll') return true; } return false; };
        const trop = [...document.querySelectorAll('.sol *')].filter(n => n.scrollWidth > n.clientWidth + 1 && n.clientWidth > 0 && !(n instanceof SVGElement)
            && getComputedStyle(n).display !== 'inline' && !defile(n)).map(n => n.tagName + '.' + n.className + ' ' + n.scrollWidth + '>' + n.clientWidth);
        return [document.documentElement.scrollWidth, innerWidth, trop.slice(0, 5)];
    })()"""

    def lancer_exemple(self, page, nom=None, probleme=None):
        if nom:
            self.clic(page, f'[data-ex="{nom}"]')
        else:
            page.evaluer(f"S = {json.dumps(probleme)}; dessinerFormulaire()")
        self.clic(page, "#launch")
        self.assertEqual(page.evaluer("document.querySelector('#err').textContent"), "")

    def verifier_figures(self, page, hauteur=800):
        """Les figures sont dessinées à l'approche de l'écran, pas toutes d'un coup ; chacune est non vide ; deux figures consécutives diffèrent."""
        total = page.evaluer("document.querySelectorAll('canvas.fig').length")
        self.assertGreaterEqual(total, 2)
        dessinees = page.evaluer("document.querySelectorAll('canvas.fig[data-dessine]').length")
        self.assertGreaterEqual(dessinees, 1)
        if total >= 6:
            self.assertLess(dessinees, total, "toutes les figures sont dessinées d'emblée : pas de rendu paresseux")
        for i in range(total):
            page.evaluer(f"document.querySelectorAll('canvas.fig')[{i}].scrollIntoView({{block: 'center'}})")
            page.attendre(f"document.querySelectorAll('canvas.fig')[{i}].dataset.dessine", 10)
            self.assertGreater(page.evaluer(f"{self.PIXELS}(document.querySelectorAll('canvas.fig')[{i}])"), 200, f"figure {i + 1} vide")
        images = page.evaluer("[...document.querySelectorAll('canvas.fig')].map(c => c.toDataURL())")
        for a, b in zip(images, images[1:]):
            self.assertNotEqual(a, b, "deux figures identiques de suite")
        return total

    def controle_solution_complete(self, page, largeur, para, attendu, nonborne=False, infinite=False, trois_d=False):
        onglet = "data-modep" if para else "data-mode"
        zone, grille = ("#solP", "#gridP") if para else ("#sol", "#gridSim")
        # vue par défaut
        self.assertEqual(page.evaluer(f"document.querySelector('[{onglet}=\"sol\"]').textContent"), "Solution complète")
        self.assertEqual(page.evaluer(f"[...document.querySelectorAll('[{onglet}]')].filter(b => b.offsetParent).map(b => b.textContent + '|' + b.classList.contains('on'))"),
                         ["Solution complète|true", "Pas à pas|false"] + ([] if para else ["Explorer|false"]))
        self.assertFalse(page.evaluer(f"document.querySelector({zone!r}).hidden"))
        self.assertTrue(page.evaluer(f"document.querySelector({grille!r}).hidden"))
        # une carte par étape, autant que dans le rapport imprimable (même source)
        cartes = page.evaluer(f"document.querySelectorAll('{zone} .carte-sol').length")
        self.assertGreaterEqual(cartes, 3)
        page.evaluer("window.print = () => {}")
        self.clic(page, "#printBtnP" if para else "#printBtn")
        self.assertEqual(page.evaluer("document.querySelectorAll('#rapport .bloc').length"), cartes)
        # dernière carte et résultat : la valeur optimale
        derniere = page.evaluer(f"[...document.querySelectorAll('{zone} .carte-sol')].pop().textContent")
        verdict = page.evaluer(f"document.querySelector('{zone} .verdict').textContent")
        if nonborne:
            self.assertIn("NON BORNÉ", derniere)
            self.assertIn("NON BORNÉ", verdict)
        else:
            self.assertIn(f"de f = {attendu}", derniere)
            self.assertIn(f"de f = {attendu}", verdict)
        if infinite:
            self.assertIn("infinité de solutions", derniere)
            self.assertIn("infinité", verdict)
        self.assertEqual(page.evaluer(f"document.querySelector('{zone}').lastElementChild.textContent.trim()"), "↑ Haut de la page")
        self.assertEqual("Faites tourner le polyèdre dans l'onglet Pas à pas." in page.evaluer(f"document.querySelector({zone!r}).textContent"), trois_d)
        # pas de défilement horizontal, les formules longues défilent dans leur bloc
        d = page.evaluer(self.DEBORDEMENT)
        self.assertLessEqual(d[0], d[1], d)
        self.assertEqual(d[2], [], d)
        self.verifier_figures(page)
        d = page.evaluer(self.DEBORDEMENT)
        self.assertLessEqual(d[0], d[1], d)
        # « ↑ Haut de la page »
        page.evaluer(f"document.querySelector('{zone} .haut').scrollIntoView(); document.querySelector('{zone} .haut').click()")
        page.attendre("scrollY === 0", 10)
        self.assertEqual([m for t, m in page.console if t == "error"], [])
        return cartes

    def pas_a_pas(self, page, para, attendu, nonborne=False):
        """« Pas à pas » : l'ancien comportement (boutons d'étapes, animation, résultat final) ; la vue défilante est cachée."""
        self.clic(page, '[data-modep="sim"]' if para else '[data-mode="sim"]')
        self.assertTrue(page.evaluer(f"document.querySelector({'#solP' if para else '#sol'!r}).hidden"))
        self.assertFalse(page.evaluer(f"document.querySelector({'#gridP' if para else '#gridSim'!r}).hidden"))
        suivant, corps = ("#bNextP", "#pageBodyP") if para else ("#bNext", "#pageBody")
        anim = "PS.anim" if para else "ST.anim"
        self.assertTrue(page.evaluer("[...document.querySelectorAll('canvas#cvp, canvas#cv')].some(c => c.offsetParent && c.clientWidth > 100)"))
        for _ in range(200):
            page.attendre(f"!{anim}", 15)
            if page.evaluer(f"document.querySelector({suivant!r}).disabled"):
                break
            self.clic(page, suivant)
        else:
            self.fail("le pas à pas ne se termine pas")
        page.attendre(f"!{anim}", 15)
        texte = page.evaluer(f"document.querySelector({corps!r}).textContent")
        self.assertIn("NON BORNÉ" if nonborne else f"de f = {attendu}", texte)
        self.assertEqual([m for t, m in page.console if t == "error"], [])

    def test_c_solution_complete_methode_algebrique(self):
        for largeur in LARGEURS:
            for nom, trois_d in (("Exemple 2D", False), ("Exemple 3D", True)):
                with self.subTest(largeur=largeur, exemple=nom):
                    page = self.ouvrir(largeur)
                    ex = json.loads(page.evaluer(f"JSON.stringify(EXEMPLES[{nom!r}])"))
                    n = ex["n"]
                    opt = optimum_exact([Fraction(x) for x in ex["f"][:n]], [([Fraction(x) for x in r["a"][:n]], r["op"], Fraction(r["b"])) for r in ex["rows"]], ex["sens"])
                    self.lancer_exemple(page, nom)
                    self.controle_solution_complete(page, largeur, False, format_nb(opt), trois_d=trois_d)
                    self.pas_a_pas(page, False, format_nb(opt))

    def test_c_solution_complete_methode_algebrique_non_borne(self):
        page = self.ouvrir(360)
        self.lancer_exemple(page, probleme={"meth": "simplexe", "n": 2, "sens": "max", "f": ["1", "1", ""], "rows": [{"a": ["1", "-1", ""], "op": "<=", "b": "1"}]})
        self.controle_solution_complete(page, 360, False, None, nonborne=True)

    def test_c_solution_complete_methode_geometrique(self):
        for largeur in LARGEURS:
            for nom in ("Parallèles : max", "Parallèles : min avec ≥", "Parallèles : coefficient de y négatif"):
                with self.subTest(largeur=largeur, exemple=nom):
                    page = self.ouvrir(largeur)
                    ex = json.loads(page.evaluer(f"JSON.stringify(EXEMPLES[{nom!r}])"))
                    opt = optimum_exact([Fraction(x) for x in ex["f"][:2]], [([Fraction(x) for x in r["a"][:2]], r["op"], Fraction(r["b"])) for r in ex["rows"]], ex["sens"])
                    self.lancer_exemple(page, nom)
                    self.controle_solution_complete(page, largeur, True, format_plain(opt))
                    self.pas_a_pas(page, True, format_plain(opt))

    def test_c_solution_complete_methode_geometrique_non_borne_et_infinite(self):
        page = self.ouvrir(360)
        self.lancer_exemple(page, probleme={"meth": "para", "n": 2, "sens": "max", "f": ["1", "1", ""], "rows": [{"a": ["1", "-1", ""], "op": "<=", "b": "2"}]})
        self.controle_solution_complete(page, 360, True, None, nonborne=True)
        page = self.ouvrir(360)
        self.lancer_exemple(page, probleme={"meth": "para", "n": 2, "sens": "max", "f": ["2", "2", ""],
                                            "rows": [{"a": ["1", "1", ""], "op": "<=", "b": "4"}, {"a": ["1", "0", ""], "op": "<=", "b": "3"}]})
        self.controle_solution_complete(page, 360, True, "8", infinite=True)

    def test_c_figures_suivent_le_theme_et_la_largeur(self):
        page = self.ouvrir(360)
        self.lancer_exemple(page, "Exemple 2D")
        page.attendre("document.querySelector('canvas.fig').dataset.dessine", 10)
        avant = page.evaluer("document.querySelector('canvas.fig').toDataURL()")
        page.taille(360, 800, sombre=True)
        page.attendre("document.querySelector('canvas.fig').dataset.dessine", 10)
        fin = time.time() + 5
        while time.time() < fin and page.evaluer("document.querySelector('canvas.fig').toDataURL()") == avant:
            time.sleep(0.1)
        self.assertNotEqual(page.evaluer("document.querySelector('canvas.fig').toDataURL()"), avant, "la figure n'a pas pris les couleurs du thème sombre")
        page.taille(700, 800)
        page.attendre("(c => c.dataset.dessine && c.width === c.clientWidth)(document.querySelector('canvas.fig'))", 5)
        self.assertGreater(page.evaluer("document.querySelector('canvas.fig').width"), 500)
        self.assertEqual([m for t, m in page.console if t == "error"], [])

    def test_c_les_onglets_s_activent_au_clavier(self):
        """Entrée sur un onglet active l'onglet (le raccourci « étape suivante » ne le détourne pas) ; le défilement à l'Espace reste libre dans la vue défilante."""
        page = self.ouvrir(1100)
        self.lancer_exemple(page, "Exemple 2D")
        self.clic(page, '[data-mode="sim"]')
        page.evaluer("document.querySelector('[data-mode=\"sol\"]').focus()")
        page.appel("Input.dispatchKeyEvent", type="keyDown", key="Enter", code="Enter", windowsVirtualKeyCode=13, text="\r")
        page.appel("Input.dispatchKeyEvent", type="keyUp", key="Enter", code="Enter", windowsVirtualKeyCode=13)
        page.attendre("!document.querySelector('#sol').hidden", 5)
        self.assertTrue(page.evaluer("document.querySelector('#gridSim').hidden"))
        self.assertEqual(page.evaluer("document.querySelector('#sol').hidden || ST.sub"), 0)             # aucun pas n'a été avancé


if __name__ == "__main__":
    unittest.main()
