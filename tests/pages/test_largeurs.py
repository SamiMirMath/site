"""Chantier « Mise en page fluide » (30.10.2026) — balayage des largeurs de TOUS les outils du registre (sauf l'accueil).

Pour chaque outil : ouvrir la page, lancer un exemple, puis vérifier à 320, 360, 375, 390, 430, 768 et 1100 px :
  debordement        la page défile horizontalement ;
  hors-ecran         un bouton, champ, liste, résumé ou onglet visible sort de l'écran (hors d'un bloc qui défile lui-même) ;
  cible-44           (≤ 430 px) un de ces éléments a moins de 44 px de haut ;
  insecable-coupe    un bloc `.insecable` est coupé (éléments sur deux lignes, ou bloc plus large que son conteneur ou que l'écran).
Le même parcours vérifie qu'aucune exception non attrapée ni aucune erreur de console ou de journal n'a eu lieu (passage des pages en module ES).

« xfail » au nom de l'outil : le tableau CONNUS liste les échecs actuels, outil par outil. Il est STRICT : un échec absent du tableau fait
échouer la suite (nouvel échec), et une entrée qui ne se produit plus la fait échouer aussi (« corrigé : retirer de CONNUS »).
BALAYAGE_RAPPORT=<fichier> : n'affirme rien et ajoute au fichier une ligne JSON par outil (toutes les fautes, avec l'état et l'élément)."""
import json
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(__file__))
from navigateur import Navigateur
from rendu import OUTIL_M, OUTILS, attendre_pret, page_de

LARGEURS = (320, 360, 375, 390, 430, 768, 1100)
TOUS = OUTILS + ["simplexe"]
CHOISIS = [o for o in os.environ.get("OUTILS", "").split(",") if o] or TOUS

# Échecs connus au 30.10.2026 (rapport initial : docs/chantiers/mise-en-page-fluide/suivi.md) : {outil: {critère: [largeurs]}}.
# À vider au fil de la migration (phases 3 et 4 du chantier) : la suite échoue tant qu'une entrée corrigée y reste.
CONNUS = {}

JS_MESURE = r"""
(async () => {
  await new Promise(r => setTimeout(r, 150));
  const L = innerWidth, fautes = [];
  const nom = n => {
    const t = (n.getAttribute('aria-label') || n.textContent || n.value || '').trim().replace(/\s+/g, ' ').slice(0, 28);
    const c = typeof n.className === 'string' && n.className.trim() ? '.' + n.className.trim().split(/\s+/).join('.') : '';
    return (n.tagName.toLowerCase() + (n.id ? '#' + n.id : '') + c + (t ? ' « ' + t + ' »' : '')).slice(0, 110);
  };
  const visible = n => { const s = getComputedStyle(n); if (s.visibility === 'hidden' || s.display === 'none') return false;
                         const r = n.getBoundingClientRect(); return r.width > 0 && r.height > 0; };
  const defile = n => { for (let m = n.parentElement; m; m = m.parentElement) { const o = getComputedStyle(m).overflowX; if (o === 'auto' || o === 'scroll') return true; } return false; };
  if (document.documentElement.scrollWidth > L)
    fautes.push({critere: 'debordement', cible: 'page', detail: document.documentElement.scrollWidth + ' > ' + L});
  const interactifs = 'button, input:not([type=hidden]), select, textarea, summary, [role=tab]';
  for (const n of document.querySelectorAll(interactifs)) {
    if (!visible(n) || n.closest('.imprime-seulement, .katex')) continue;
    const cible = (n.matches('input[type=checkbox], input[type=radio]') && n.closest('label')) || n;      // case à cocher : l'étiquette est la cible
    const r = cible.getBoundingClientRect();
    if (!defile(n) && (r.left < -1 || r.right > L + 1))
      fautes.push({critere: 'hors-ecran', cible: nom(n), detail: Math.round(r.left) + '…' + Math.round(r.right) + ' sur ' + L});
    if (L <= 430 && r.height < 43.9)
      fautes.push({critere: 'cible-44', cible: nom(n), detail: Math.round(r.height * 10) / 10 + ' px'});
  }
  for (const n of document.querySelectorAll('.insecable')) {
    if (!visible(n)) continue;
    const r = n.getBoundingClientRect(), enfants = [...n.children].map(c => c.getBoundingClientRect()).filter(e => e.width > 0);
    const surDeuxLignes = enfants.some(a => enfants.some(b => a.top >= b.bottom - 1));
    const p = n.parentElement;
    const trop = n.scrollWidth > n.clientWidth + 1 || r.right > L + 1 || r.left < -1 || (!defile(n) && r.width > p.clientWidth + 1 && p.clientWidth > 0);
    if (surDeuxLignes || trop)
      fautes.push({critere: 'insecable-coupe', cible: nom(n), detail: (surDeuxLignes ? 'sur deux lignes' : 'bloc ' + Math.round(r.width) + ' px, conteneur ' + p.clientWidth + ' px, écran ' + L)});
  }
  return fautes;
})()
"""


# Tableaux u, v / u′, v′ visibles : débordement de la carte ou de l'écran, colonnes côte à côte (cote), lignes alignées si côte à côte ou
# colonne v sous la colonne u si empilées (aligne), u au-dessus de u′ (ordre).
JS_UV = r"""
(async () => {
  await new Promise(r => setTimeout(r, 150));
  return [...document.querySelectorAll('#cartes .uv')].filter(u => u.getBoundingClientRect().width > 0).map(u => {
    const r = u.getBoundingClientRect(), carte = u.closest('.card').getBoundingClientRect();
    const cols = [...u.children].map(c => [...c.children].map(d => d.getBoundingClientRect()));
    const cote = Math.abs(cols[0][0].top - cols[1][0].top) < 1;
    return {deborde: r.right > carte.right + 1 || r.left < carte.left - 1 || r.right > innerWidth + 1, cote,
            aligne: cote ? Math.abs(cols[0][1].top - cols[1][1].top) < 1 : cols[1][0].top >= cols[0][1].bottom - 1,
            ordre: cols[0][0].bottom <= cols[0][1].top + 1 && cols[1][0].bottom <= cols[1][1].top + 1};
  });
})()
"""


def erreurs_a_signaler(page):
    """Erreurs de la page, sans le bruit de ressources extérieures (compteur, polices…) ni l'icône de l'onglet."""
    return [e for e in page.erreurs if "favicon" not in e
            and not (e.startswith("journal : ") and "(http" in e and "127.0.0.1" not in e)]


class TestLargeurs(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.nav = Navigateur().__enter__()

    @classmethod
    def tearDownClass(cls):
        cls.nav.__exit__(None, None, None)

    # ---------- mesures ----------
    def balayer(self, page, etat, fautes):
        """Mesure l'état courant de la page à chaque largeur ; ajoute les fautes à `fautes`."""
        try:
            for w in LARGEURS:
                page.taille(w, 800)
                for f in page.evaluer(JS_MESURE):
                    fautes.append({**f, "largeur": w, "etat": etat})
        finally:
            page.taille(1100, 800)

    def conclure(self, nom, page, fautes):
        """Compare les fautes au tableau CONNUS (strict), puis vérifie la console."""
        if os.environ.get("BALAYAGE_RAPPORT"):
            with open(os.environ["BALAYAGE_RAPPORT"], "a", encoding="utf-8") as f:
                f.write(json.dumps({"outil": nom, "fautes": fautes, "erreurs": erreurs_a_signaler(page)}, ensure_ascii=False) + "\n")
            return
        observe = {}
        for f in fautes:
            observe.setdefault(f["critere"], set()).add(f["largeur"])
        connu = {c: set(ws) for c, ws in CONNUS.get(nom, {}).items()}
        nouveaux = {c: sorted(ws - connu.get(c, set())) for c, ws in observe.items() if ws - connu.get(c, set())}
        corriges = {c: sorted(ws - observe.get(c, set())) for c, ws in connu.items() if ws - observe.get(c, set())}
        with self.subTest(outil=nom, controle="nouvel échec"):
            exemples = [f"{f['critere']} {f['largeur']} px [{f['etat']}] {f['cible']} ({f['detail']})"
                        for f in fautes if f["largeur"] in nouveaux.get(f["critere"], [])]
            self.assertEqual(nouveaux, {}, f"{nom} : nouvel échec (largeurs par critère) ; premiers éléments :\n  " + "\n  ".join(exemples[:10]))
        with self.subTest(outil=nom, controle="CONNUS exact"):
            self.assertEqual(corriges, {}, f"{nom} : corrigé, retirer de CONNUS : {corriges}")
        with self.subTest(outil=nom, controle="console"):
            self.assertEqual(erreurs_a_signaler(page), [], f"{nom} : exception ou erreur de console")

    # ---------- outils à cartes (commun/outil.js) ----------
    def balayage_outil_a_cartes(self, outil):
        if outil.replace("-M", "") not in CHOISIS:
            self.skipTest("hors de OUTILS")
        dossier, requete = page_de(outil)
        page = self.nav.ouvrir(f"{dossier}/index.html{requete}")
        attendre_pret(page)
        page.taille(1100, 800)
        page.evaluer("document.querySelector('#exemples button[data-ex]').click()")
        page.attendre("document.querySelector('#cartes').children.length > 0 && !document.querySelector('#calculer').disabled", 120)
        fautes = []
        self.balayer(page, "première carte", fautes)               # le bouton « Étape suivante » flottant est visible
        page.evaluer("document.querySelector('#tout') && !document.querySelector('#tout').disabled && document.querySelector('#tout').click()")
        self.balayer(page, "corrigé complet", fautes)
        self.conclure(outil, page, fautes)

    # ---------- tableau u, v / u′, v′ (D8) et sous-carte « Dérivée de l'exposant » (D7), chantier étude complète P7a ----------
    def test_tableau_uv_et_derivee_de_l_exposant(self):
        """Une saisie dont le tableau u/v est large (Dérivée) et Ex7 (Étude complète : sous-carte et tableau dans la sous-carte) : aucune
        faute du balayage à aucune largeur ; chaque tableau reste dans sa carte ; colonnes côte à côte avec les lignes u | v et u′ | v′
        alignées, ou empilées dans l'ordre u, u′, v, v′ ; côte à côte à 1100 px, empilées à 320 px pour le tableau large."""
        cas = {"derivee-variations": ("(x^3+2x)^4*e^x", True), "etude-complete": ("e^((x^2+x-2)/(6x-12))", False)}
        for outil, (entree, empile_a_320) in cas.items():
            if outil not in CHOISIS:
                continue
            with self.subTest(outil=outil):
                dossier, requete = page_de(outil)
                page = self.nav.ouvrir(f"{dossier}/index.html{requete}")
                attendre_pret(page)
                page.taille(1100, 800)
                page.evaluer(f"document.querySelector('#entree').value = {json.dumps(entree)}; document.querySelector('#calculer').click()")
                page.attendre("document.querySelector('#cartes').children.length > 0 && !document.querySelector('#calculer').disabled", 120)
                page.evaluer("document.querySelector('#tout') && !document.querySelector('#tout').disabled && document.querySelector('#tout').click()")
                fautes = []
                self.balayer(page, "corrigé complet : " + entree, fautes)
                self.assertEqual(fautes, [], fautes[:5])
                mesures = {}
                try:
                    for w in LARGEURS:
                        page.taille(w, 800)
                        mesures[w] = page.evaluer(JS_UV)
                finally:
                    page.taille(1100, 800)
                for w, tableaux in mesures.items():
                    self.assertTrue(tableaux, f"aucun tableau u/v visible à {w} px")
                    for t in tableaux:
                        with self.subTest(largeur=w):
                            self.assertFalse(t["deborde"], t)
                            self.assertTrue(t["aligne"] and t["ordre"], t)
                self.assertTrue(all(t["cote"] for t in mesures[1100]), mesures[1100])
                if empile_a_320:
                    self.assertTrue(any(not t["cote"] for t in mesures[320]), mesures[320])
                if outil == "etude-complete":
                    self.assertTrue(page.evaluer("[...document.querySelectorAll('#cartes .sous-t')].some(t => t.textContent === \"Dérivée de l'exposant\")"))
                self.assertEqual(erreurs_a_signaler(page), [])

    # ---------- simplexe (page autonome) ----------
    def clic(self, page, selecteur):
        page.evaluer(f"document.querySelector({selecteur!r}).click()")

    def balayage_simplexe(self):
        if "simplexe" not in CHOISIS:
            self.skipTest("hors de OUTILS")
        page = self.nav.ouvrir("simplexe/index.html")
        page.attendre("document.readyState === 'complete' && document.querySelector('#objRow input')", 30)
        page.taille(1100, 800)
        fautes = []

        def lancer(selecteur_exemple, application):
            self.clic(page, selecteur_exemple)
            self.clic(page, "#launch")
            self.assertEqual(page.evaluer("document.querySelector('#err').textContent"), "")
            page.attendre(f"!document.querySelector('{application}').hidden", 10)

        self.clic(page, '[data-ex="Exemple 2D"]')
        self.balayer(page, "algébrique : formulaire 2D", fautes)
        self.clic(page, '[data-ex="Exemple 3D"]')
        self.balayer(page, "algébrique : formulaire 3D", fautes)
        lancer('[data-ex="Exemple 3D"]', "#app")
        self.balayer(page, "algébrique 3D : solution", fautes)
        self.clic(page, "#editBtn")
        lancer('[data-ex="Exemple 2D"]', "#app")
        for mode, libelle in (("sol", "solution"), ("sim", "pas à pas"), ("exp", "explorer")):
            self.clic(page, f'[data-mode="{mode}"]')
            self.balayer(page, f"algébrique 2D : {libelle}", fautes)
        self.clic(page, "#editBtn")
        self.clic(page, '[data-meth="para"]')
        self.clic(page, '[data-ex="Parallèles : max"]')
        self.balayer(page, "géométrique : formulaire", fautes)
        lancer('[data-ex="Parallèles : max"]', "#appPara")
        for mode, libelle in (("sol", "solution"), ("sim", "pas à pas")):
            self.clic(page, f'[data-modep="{mode}"]')
            self.balayer(page, f"géométrique : {libelle}", fautes)
        self.conclure("simplexe", page, fautes)

    # ---------- le script de mesure lui-même ----------
    def test_la_mesure_voit_un_bloc_insecable_coupe(self):
        """Auto-test : sur un gabarit, le script signale un `.insecable` plus large que l'écran et ne signale pas un bloc qui tient."""
        if "simplexe" not in CHOISIS:
            self.skipTest("hors de OUTILS")
        page = self.nav.ouvrir("simplexe/index.html")
        page.attendre("document.readyState === 'complete' && document.querySelector('#objRow input')", 30)
        page.taille(360, 800)
        page.evaluer("""new Promise(ok => { const l = document.createElement('link'); l.rel = 'stylesheet'; l.href = '../commun/composants.css';
            l.onload = ok; l.onerror = ok; document.head.appendChild(l); })""")
        page.evaluer("""(() => { const g = document.createElement('div'); g.id = 'gabarit';
            g.innerHTML = '<div class="flux"><span class="insecable" id="petit">a b</span></div>'
              + '<div><span class="insecable" id="large"><b>' + 'm'.repeat(90) + '</b><b>y</b></span></div>';
            document.body.prepend(g); })()""")
        fautes = [f for f in page.evaluer(JS_MESURE) if f["critere"] == "insecable-coupe"]
        self.assertEqual([f["cible"].split(" ")[0] for f in fautes], ["span#large.insecable"], fautes)


def _methode(outil):
    return lambda self: self.balayage_outil_a_cartes(outil)


for _o in OUTILS + [OUTIL_M]:
    setattr(TestLargeurs, "test_balayage_" + _o.replace("-", "_"), _methode(_o))
TestLargeurs.test_balayage_simplexe = lambda self: self.balayage_simplexe()

if __name__ == "__main__":
    unittest.main()
