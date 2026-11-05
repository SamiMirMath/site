"""Chantier fondations, F6 — copie locale de KaTeX (tests/pages/katex-local/) et garde-fou réseau des tests de pages : KaTeX et ses polices
viennent de la copie, aucune requête ne quitte la machine, et une requête extérieure non servie localement fait échouer.

    python3 tests/pages/katex_local.py     # télécharge la copie si elle manque"""
import base64
import hashlib
import io
import json
import os
import shutil
import sys
import tarfile
import tempfile
import time
import unittest
from unittest import mock

sys.path.insert(0, os.path.dirname(__file__))
import katex_local
import pyodide_local
from navigateur import ErreurReseau, Navigateur
from rendu import attendre_pret

POLICE_CHARGEE = "[...document.fonts].some(f => f.family === 'KaTeX_Main' && f.status === 'loaded')"


class TestKatexLocal(unittest.TestCase):
    def copie(self, t):
        copie = os.path.join(t, "copie")
        shutil.copytree(katex_local.DOSSIER, copie)
        return copie

    def test_version_et_fichiers_de_la_copie_egaux_a_ceux_des_pages(self):
        """La copie a la version des pages, chaque fichier qu'une page demande, et chaque police que nomme la feuille de style."""
        e = katex_local.verifier()
        version = katex_local.version_attendue()
        self.assertEqual(e["version"], version)
        demandes = set(katex_local.references_des_pages()[version])
        self.assertEqual(demandes, {"dist/katex.min.css", "dist/katex.min.js", "dist/contrib/auto-render.min.js"})
        with open(os.path.join(katex_local.DOSSIER, "dist", "katex.min.css"), encoding="utf-8") as f:
            polices = katex_local.polices_de_la_feuille("dist/katex.min.css", f.read())
        self.assertEqual(len(polices), 60)                               # 20 polices × (woff2, woff, ttf)
        self.assertEqual(set(e["fichiers"]), demandes | polices)

    def test_une_copie_absente_fait_echouer_avec_la_commande(self):
        with tempfile.TemporaryDirectory() as t:
            with self.assertRaisesRegex(RuntimeError, r"copie locale de KaTeX absente : lancer  python3 tests/pages/katex_local\.py"):
                katex_local.verifier(t)

    def test_une_copie_d_une_autre_version_fait_echouer(self):
        with tempfile.TemporaryDirectory() as t:
            copie = self.copie(t)
            e = katex_local.lire_empreintes(copie)
            e["version"] = "0.0.0"
            with open(os.path.join(copie, katex_local.EMPREINTES), "w", encoding="utf-8") as f:
                json.dump(e, f)
            with self.assertRaisesRegex(RuntimeError, r"0\.0\.0.*supprimer .* puis relancer"):
                katex_local.verifier(copie)

    def test_une_copie_incomplete_ou_abimee_fait_echouer(self):
        with tempfile.TemporaryDirectory() as t:
            copie = self.copie(t)
            os.remove(os.path.join(copie, "dist", "fonts", "KaTeX_Main-Regular.woff2"))
            with self.assertRaisesRegex(RuntimeError, r"incomplète \(dist/fonts/KaTeX_Main-Regular\.woff2\)"):
                katex_local.verifier(copie)
        with tempfile.TemporaryDirectory() as t:
            copie = self.copie(t)
            with open(os.path.join(copie, "dist", "katex.min.js"), "ab") as f:
                f.write(b"\n")
            with self.assertRaisesRegex(RuntimeError, r"dist/katex\.min\.js \(empreinte différente\)"):
                katex_local.verifier(copie)

    def test_les_pages_doivent_utiliser_une_seule_version(self):
        with tempfile.TemporaryDirectory() as racine:
            for nom, v in (("a", "0.16.11"), ("b", "0.16.12")):
                os.makedirs(os.path.join(racine, nom))
                with open(os.path.join(racine, nom, "index.html"), "w", encoding="utf-8") as f:
                    f.write(f'<script src="https://cdn.jsdelivr.net/npm/katex@{v}/dist/katex.min.js"></script>')
            with self.assertRaisesRegex(RuntimeError, "une seule version de KaTeX"):
                katex_local.version_attendue(racine)


class TestTelechargementVerifie(unittest.TestCase):
    """Le téléchargement vérifie le paquet npm (SHA-512 du registre) et chaque fichier extrait (SHA-256 donné par jsDelivr) ; un écart
    n'écrit rien (empreintes.json, écrit en dernier, absent : la copie reste « absente »). Réseau simulé."""
    CSS = b".k{font-family:KaTeX_Main}@font-face{src:url(fonts/KaTeX_Main-Regular.woff2) format(\"woff2\")}"
    JS = b"window.katex={};"
    POLICE = b"wOF2 police"

    def paquet(self):
        tampon = io.BytesIO()
        with tarfile.open(fileobj=tampon, mode="w:gz") as archive:
            for chemin, octets in (("dist/katex.min.css", self.CSS), ("dist/katex.min.js", self.JS),
                                   ("dist/fonts/KaTeX_Main-Regular.woff2", self.POLICE)):
                info = tarfile.TarInfo("package/" + chemin)
                info.size = len(octets)
                archive.addfile(info, io.BytesIO(octets))
        return tampon.getvalue()

    def lancer(self, jsdelivr_faux=False, integrite_fausse=False):
        paquet = self.paquet()
        integrite = "sha512-" + base64.b64encode(hashlib.sha512(b"autre chose" if integrite_fausse else paquet).digest()).decode()
        empreinte = lambda o: base64.b64encode(hashlib.sha256(o).digest()).decode()
        reponses = {
            "https://registry.npmjs.org/katex/9.9.9": json.dumps(
                {"version": "9.9.9", "dist": {"tarball": "https://registry.npmjs.org/katex/-/katex-9.9.9.tgz", "integrity": integrite}}).encode(),
            "https://registry.npmjs.org/katex/-/katex-9.9.9.tgz": paquet,
            "https://data.jsdelivr.com/v1/packages/npm/katex@9.9.9?structure=flat": json.dumps({"files": [
                {"name": "/dist/katex.min.css", "hash": empreinte(self.CSS)},
                {"name": "/dist/katex.min.js", "hash": empreinte(b"autre" if jsdelivr_faux else self.JS)},
                {"name": "/dist/fonts/KaTeX_Main-Regular.woff2", "hash": empreinte(self.POLICE)}]}).encode(),
        }

        class Reponse(io.BytesIO):
            headers = {}

            def __enter__(self):
                return self

            def __exit__(self, *a):
                return False
        with tempfile.TemporaryDirectory() as racine:
            os.makedirs(os.path.join(racine, "outil"))
            with open(os.path.join(racine, "outil", "index.html"), "w", encoding="utf-8") as f:
                f.write('<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@9.9.9/dist/katex.min.css">'
                        '<script defer src="https://cdn.jsdelivr.net/npm/katex@9.9.9/dist/katex.min.js"></script>')
            copie = os.path.join(racine, "copie")
            with mock.patch.object(pyodide_local.urllib.request, "urlopen", lambda url, timeout: Reponse(reponses[url])), \
                    mock.patch.object(pyodide_local.time, "sleep"), mock.patch("builtins.print"):
                try:
                    katex_local.telecharger(copie, racine)
                    resultat = katex_local.verifier(copie, racine)
                except RuntimeError as e:
                    resultat = e
            ecrit = os.path.exists(os.path.join(copie, katex_local.EMPREINTES))
        return resultat, ecrit

    def test_paquet_et_fichiers_conformes(self):
        e, ecrit = self.lancer()
        self.assertTrue(ecrit)
        self.assertEqual(set(e["fichiers"]), {"dist/katex.min.css", "dist/katex.min.js", "dist/fonts/KaTeX_Main-Regular.woff2"})
        self.assertEqual(e["fichiers"]["dist/katex.min.js"], hashlib.sha256(self.JS).hexdigest())

    def test_un_fichier_different_de_jsdelivr_est_refuse(self):
        e, ecrit = self.lancer(jsdelivr_faux=True)
        self.assertRegex(str(e), r"dist/katex\.min\.js : les octets du paquet npm diffèrent de ceux que sert jsDelivr")
        self.assertFalse(ecrit)

    def test_un_paquet_d_une_autre_empreinte_est_refuse(self):
        e, ecrit = self.lancer(integrite_fausse=True)
        self.assertRegex(str(e), r"téléchargement impossible après 5 essais : .*katex-9\.9\.9\.tgz \(empreinte SHA-512 différente")
        self.assertFalse(ecrit)


class TestGardeFouReseau(unittest.TestCase):
    def test_katex_et_ses_polices_viennent_de_la_copie_locale(self):
        """Une page d'outil : KaTeX (feuille, script, auto-render) et les polices qu'il emploie sont servis par la copie ; aucune requête refusée."""
        with Navigateur() as nav:
            page = nav.ouvrir("factorisation/index.html?f=x^2-1")
            attendre_pret(page)
            page.attendre(POLICE_CHARGEE, 30)
            self.assertGreater(page.evaluer("document.querySelectorAll('.katex').length"), 0)
            servies = set(nav.intercepteur.servies)
            self.assertLessEqual({"katex/dist/katex.min.css", "katex/dist/katex.min.js", "katex/dist/contrib/auto-render.min.js",
                                  "katex/dist/fonts/KaTeX_Main-Regular.woff2"}, servies)
            self.assertEqual(nav.intercepteur.refusees, [])
            self.assertEqual(nav.fuites(), [])

    def test_accueil_sans_reseau(self):
        """L'accueil : la feuille Google Fonts est servie vide (police de repli), la balise GoatCounter aussi ; rien d'autre n'est demandé dehors.
        Ses <link rel="preconnect"> ne demandent qu'une connexion, refusée par le puits et notée à part (pas une requête)."""
        with Navigateur() as nav:
            page = nav.ouvrir("index.html")
            page.attendre("document.readyState === 'complete'", 30)
            fin = time.time() + 15
            while not nav.intercepteur.comptage and time.time() < fin:
                time.sleep(0.05)
            self.assertEqual([u.split("?")[0] for u in nav.intercepteur.polices], ["https://fonts.googleapis.com/css2"])
            self.assertEqual(nav.intercepteur.comptage, ["http://gc.zgo.at/count.js"])
            self.assertEqual(page.evaluer("document.fonts.size"), 0)                  # feuille vide : aucune police déclarée
            self.assertEqual(nav.fuites(), [])

    def test_une_requete_exterieure_forcee_fait_echouer(self):
        """Contre-épreuve : une requête HTTPS (intercepteur) et une requête HTTP (puits) vers un hôte sans copie locale sont refusées, notées,
        et la sortie du Navigateur (tearDownClass, fin du `with`) échoue en les nommant."""
        nav = Navigateur().__enter__()
        try:
            page = nav.ouvrir("index.html")
            page.attendre("document.readyState === 'complete'", 30)
            # HTTPS : refusée par l'intercepteur (erreur réseau dans la page) ; HTTP : refusée par le puits (403, réponse opaque en no-cors)
            etats = page.evaluer("Promise.allSettled([fetch('https://exemple.invalid/a.js'), "
                                 "fetch('http://exemple.invalid/b.png', {mode: 'no-cors'}).then(r => r.status)]).then(r => r.map(x => x.status + ' ' + (x.value ?? '')))")
            self.assertEqual(etats, ["rejected ", "fulfilled 0"])
            self.assertEqual(nav.intercepteur.fuites, ["https://exemple.invalid/a.js"])
            self.assertEqual(nav.puits.fuites, ["GET http://exemple.invalid/b.png"])
        except BaseException:
            nav.__exit__(*sys.exc_info())
            raise
        with self.assertRaisesRegex(ErreurReseau, r"https://exemple\.invalid/a\.js ; GET http://exemple\.invalid/b\.png"):
            nav.__exit__(None, None, None)


if __name__ == "__main__":
    unittest.main()
