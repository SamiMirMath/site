"""Application du moteur sur serveur, serveur/app.py (chantier moteur-serveur, P1 ; decisions.md, T1 à T4, T8, T14, § 4 ; A10).

L'application WSGI est appelée dans ce processus, sans réseau (wsgiref.validate vérifie le protocole), sans cache de test (memo.py) :
- à l'octet avec l'appel direct de `<fn>_json`, sur le corpus réduit des pages (tests/pages/rendu.py, REDUIT), pour chaque outil du
  manifeste, chaque fonction et chaque filière ; `exercice` avec une graine fixée (T8) ; `fenetre` sur quelques fenêtres ;
- deux ordres mélangés entre outils, dans ce seul processus (T2, T8) ;
- les codes 400, 404, 405, 413 et 500 (la réponse 500 ne contient pas la saisie), /api/sante en GET et HEAD avec ses 503, les
  en-têtes, les fonctions « anciennes », le démarrage (préchargement, versions, sys.path) ;
- le délai de gunicorn dépasse le plus grand délai de calcul des pages (T3) ; le journal ne contient ni la saisie ni le message de
  l'exception (T14) ; A10 (aucun nom de module d'outil dans le code du serveur ; ses imports : test_imports.py, TestServeur) ;
- la liste blanche publique (T4, serveur/liste_publique.py) sur l'arbre du dépôt.
Le dump par HTTP (tests/outils/dump_sorties.py --serveur) complète ce test sur tout le corpus, avec un vrai serveur."""
import ast
import copy
import datetime
import importlib.util
import io
import json
import os
import random
import re
import subprocess
import sys
import tarfile
import tempfile
import unittest
from unittest import mock
from wsgiref.util import setup_testing_defaults
from wsgiref.validate import validator

from moteurs import RACINE
import outils_du_site

sys.path.insert(0, os.path.join(RACINE, "tests", "pages"))
import rendu  # noqa: E402  (corpus réduit des pages)


def charger(nom, chemin):
    spec = importlib.util.spec_from_file_location(nom, os.path.join(RACINE, chemin))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


app = charger("app", "serveur/app.py")
liste_publique = charger("liste_publique", "serveur/liste_publique.py")
dump_sorties = charger("dump_sorties", "tests/outils/dump_sorties.py")      # niveaux des exercices, lus dans la page
MANIFESTE = outils_du_site.manifeste()
APPLICATION = app.application
JSON = "application/json; charset=utf-8"
HORS_CORPUS = ("exercice", "fenetre")         # comparées à part (graine, fenêtres)
FENETRES = [("e^(1/x)", -5, 5, 200), ("e^(1/x)", 0.1, 3, 80), ("x^2*e^(-x)", -1, 6, 500), ("x^2*e^(-x)", 2, 2.5, 10),
            ("ln(", -5, 5, 100), ("e^(1/x)", 3, -3, 100)]
N_EXERCICES = 3                                # tirages comparés par niveau et par filière


class Entree(io.BytesIO):
    """wsgi.input qui refuse d'être lu (413 : le corps n'est jamais lu)."""

    def read(self, *args):
        raise AssertionError("corps lu alors qu'il devait être refusé")


def requete(methode, chemin, corps=None, type_contenu="application/json", longueur=None, entree=None, application=None, valider=True):
    """(code, en-têtes {nom en minuscules: valeur}, corps en octets) d'une requête à l'application, validée par wsgiref.validate
    (sauf `valider=False` : CONTENT_LENGTH illisible ou négatif, que le validateur refuse avant l'application)."""
    environ = {"REQUEST_METHOD": methode, "PATH_INFO": chemin, "SCRIPT_NAME": "", "QUERY_STRING": ""}
    if corps is not None:
        brut = corps if isinstance(corps, bytes) else json.dumps(corps, ensure_ascii=False).encode("utf-8")
        environ["wsgi.input"] = io.BytesIO(brut)
        environ["CONTENT_LENGTH"] = str(len(brut) if longueur is None else longueur)
    elif longueur is not None:
        environ["CONTENT_LENGTH"] = str(longueur)
    if entree is not None:
        environ["wsgi.input"] = entree
    if type_contenu is not None:
        environ["CONTENT_TYPE"] = type_contenu
    setup_testing_defaults(environ)
    recu = {}

    def start_response(statut, entetes, exc_info=None):
        recu["code"] = int(statut.split()[0])
        recu["entetes"] = {n.lower(): v for n, v in entetes}
        return lambda _: None

    application = application or APPLICATION
    reponse = (validator(application) if valider else application)(environ, start_response)
    try:
        sortie = b"".join(reponse)
    finally:
        if hasattr(reponse, "close"):
            reponse.close()
    return recu["code"], recu["entetes"], sortie


def poster(outil, fn, arg, application=None):
    return requete("POST", f"/api/{outil}/{fn}", arg, application=application)


def module_de(outil):
    return sys.modules[MANIFESTE[outil]["module"]]


def filieres(outil):
    """[None] si resoudre n'a pas de filière ; sinon la valeur par défaut et celles du registre (comme dump_sorties.py)."""
    return dump_sorties.filieres(outil, module_de(outil), {o["id"]: o for o in outils_du_site.registre()})


def corpus_reduit(outil):
    return list(dict.fromkeys(rendu.REDUIT[outil] + [e for v, o in outils_du_site.variantes().items() if o == outil
                                                     for e in rendu.REDUIT[v]]))


def appels_du_corpus():
    """[(graine, outil, fn, arguments)] : corpus réduit, toutes fonctions de la page et filières, exercices, fenêtres."""
    appels = []
    for outil, entree in MANIFESTE.items():
        fonctions = [f for f in entree["fonctions"] if f not in entree.get("anciennes", [])]
        for fn in fonctions:
            if fn in HORS_CORPUS:
                continue
            for filiere in (filieres(outil) if fn == "resoudre" else [None]):
                for e in corpus_reduit(outil):
                    appels.append((None, outil, fn, (e,) if filiere is None else (e, filiere)))
        if "exercice" in fonctions:
            for filiere, niveaux in dump_sorties.niveaux_de_page(outil).items():
                for niveau in niveaux:
                    for k in range(N_EXERCICES):
                        appels.append((repr((outil, filiere, niveau, k)), outil, "exercice",
                                       (niveau,) if filiere is None else (niveau, filiere)))
        if "fenetre" in fonctions:
            for f, xmin, xmax, n in FENETRES:
                appels.append((None, outil, "fenetre", (json.dumps({"f": f, "xmin": xmin, "xmax": xmax, "n": n}),)))
    return appels


def direct(appel):
    graine, outil, fn, args = appel
    random.seed(graine)
    return getattr(module_de(outil), fn + "_json")(*args).encode("utf-8")


def par_l_application(appel):
    graine, outil, fn, args = appel
    random.seed(graine)
    code, entetes, corps = poster(outil, fn, args[0] if len(args) == 1 else list(args))
    if code != 200:
        raise AssertionError(f"{appel} : code {code}")
    return corps


class TestAOctet(unittest.TestCase):
    """Réponse 200 = la chaîne brute de `<fn>_json`, à l'octet (T1, T8)."""

    @classmethod
    def setUpClass(cls):
        cls.appels = appels_du_corpus()

    def test_le_corpus_couvre_chaque_fonction_et_chaque_filiere(self):
        vus = {(o, fn) for _, o, fn, _ in self.appels}
        attendus = {(o, fn) for o, e in MANIFESTE.items() for fn in e["fonctions"] if fn not in e.get("anciennes", [])}
        self.assertEqual(vus, attendus)
        for outil in MANIFESTE:
            with self.subTest(outil=outil):
                vues = {a[1] if len(a) > 1 else None for _, o, fn, a in self.appels if o == outil and fn == "resoudre"}
                self.assertEqual(vues, set(filieres(outil)))
        self.assertIn(("exponentielles-logarithmes", "M"), {(o, a[-1]) for _, o, fn, a in self.appels if fn == "exercice"})

    def test_corpus_reduit(self):
        for appel in self.appels:
            with self.subTest(appel=appel[1:]):
                self.assertEqual(par_l_application(appel), direct(appel))

    def test_la_graine_fixe_l_exercice(self):
        """Le test des exercices n'est pas vide : des graines différentes donnent des exercices différents."""
        for outil in [o for o, e in MANIFESTE.items() if "exercice" in e["fonctions"]]:
            with self.subTest(outil=outil):
                sorties = {direct(a) for a in self.appels if a[1] == outil and a[2] == "exercice"}
                self.assertGreater(len(sorties), 1)

    def test_deux_ordres_melanges_entre_outils(self):
        """Ni un outil ni un appel précédent ne change la sortie d'un autre (un seul processus pour tous : T2)."""
        attendu = {i: direct(a) for i, a in enumerate(self.appels)}
        for graine in (1, 2):
            ordre = list(range(len(self.appels)))
            random.Random(graine).shuffle(ordre)
            outils = [self.appels[i][1] for i in ordre]
            self.assertGreater(sum(a != b for a, b in zip(outils, outils[1:])), len(MANIFESTE), "ordre mélangé entre outils")
            for i in ordre:
                with self.subTest(ordre=graine, appel=self.appels[i][1:]):
                    self.assertEqual(par_l_application(self.appels[i]), attendu[i])

    def test_chaine_jamais_re_serialisee(self):
        brut = '{"ok" :true,  "tex":"\\u00e9 é \\/",\n"n": 1.50}'
        with mock.patch.object(module_de("factorisation"), "apercu_json", lambda e: brut):
            code, entetes, corps = poster("factorisation", "apercu", "x")
        self.assertEqual((code, corps), (200, brut.encode("utf-8")))


class TestCodes(unittest.TestCase):
    """Codes d'erreur de T1 ; le corps d'une erreur est fixe et ne contient jamais la saisie."""

    def verifier(self, code_attendu, reponse, allow=None, tete=False):
        """`tete` : réponse à HEAD, sans corps, avec la longueur du corps de GET."""
        code, entetes, corps = reponse
        self.assertEqual(code, code_attendu)
        self.assertEqual(entetes["content-type"], JSON)
        self.assertEqual(entetes["cache-control"], "no-store")
        self.assertEqual(entetes.get("allow"), allow)
        if tete:
            self.assertEqual(corps, b"")
            corps = json.dumps({"erreur": app.ERREURS[code_attendu]}).encode("utf-8")
        self.assertEqual(entetes["content-length"], str(len(corps)))
        if code_attendu != 200:
            self.assertEqual(json.loads(corps), {"erreur": app.ERREURS[code_attendu]})

    def test_404_hors_du_manifeste(self):
        chemins = ["/", "/api", "/api/", "/api/sante/", "/api/inconnu/resoudre", "/api/factorisation/inconnue",
                   "/api/factorisation/resoudre/", "/api/factorisation/resoudre_json", "/api/simplexe/resoudre",
                   "/api/../moteur/manifeste.json", "/moteur/manifeste.json", "/api/factorisation/__init__",
                   "/api/Factorisation/resoudre", "/api/factorisation//resoudre", "/api/factorisation/resoudre?x=1",
                   "/factorisation/resoudre_fa.py"]
        for outil, entree in MANIFESTE.items():                 # une fonction du module, hors de sa liste au manifeste
            for nom in dir(module_de(outil)):
                if nom.endswith("_json") and nom[:-5] not in entree["fonctions"] and re.fullmatch(r"[a-z_]+", nom[:-5]):
                    chemins.append(f"/api/{outil}/{nom[:-5]}")
            if "fenetre" not in entree["fonctions"]:
                chemins.append(f"/api/{outil}/fenetre")
        for chemin in chemins:
            with self.subTest(chemin=chemin):
                self.verifier(404, requete("POST", chemin, "x"))

    def test_la_liste_blanche_est_le_manifeste(self):
        """Une fonction retirée du manifeste n'est plus appelable, même si le module l'a encore."""
        manifeste = copy.deepcopy(outils_du_site.lire(outils_du_site.MANIFESTE))
        manifeste["outils"]["factorisation"]["fonctions"].remove("apercu")
        reduite = app.Application(manifeste=manifeste)
        self.verifier(404, poster("factorisation", "apercu", "x^2-1", application=reduite))
        self.verifier(200, poster("factorisation", "resoudre", "x^2-1", application=reduite))

    def test_405_methode(self):
        for methode in ("GET", "HEAD", "PUT", "DELETE", "OPTIONS", "PATCH"):
            with self.subTest(methode=methode):
                self.verifier(405, requete(methode, "/api/factorisation/resoudre"), allow="POST", tete=methode == "HEAD")
        for methode in ("POST", "PUT", "DELETE", "OPTIONS"):
            with self.subTest(sante=methode):
                self.verifier(405, requete(methode, "/api/sante", "x"), allow="GET, HEAD")

    def test_413_corps_trop_long(self):
        self.verifier(413, requete("POST", "/api/equations-2e-degre/apercu", "1" * (app.TAILLE_MAX - 1)))
        self.verifier(413, requete("POST", "/api/equations-2e-degre/apercu", longueur=app.TAILLE_MAX + 1, entree=Entree()))
        self.verifier(413, requete("POST", "/api/equations-2e-degre/apercu", longueur=10 ** 9, entree=Entree()))
        self.verifier(200, requete("POST", "/api/equations-2e-degre/apercu", "1" * (app.TAILLE_MAX - 2)))     # 4096 octets

    def test_400_requete_illisible(self):
        chemin = "/api/exponentielles-logarithmes/resoudre"
        cas = {
            "type text/plain": dict(corps="x", type_contenu="text/plain"),
            "type absent": dict(corps="x", type_contenu=None),
            "type application/jsonx": dict(corps="x", type_contenu="application/jsonx"),
            "longueur absente": dict(entree=io.BytesIO(b'"x"')),
            "longueur illisible": dict(corps="x", longueur="abc", valider=False),
            "longueur négative": dict(corps="x", longueur=-1, valider=False),
            "corps plus court que la longueur": dict(corps=b'"x"', longueur=10),
            "corps vide": dict(corps=b""),
            "UTF-8 invalide": dict(corps=b'"\xff"'),
            "BOM": dict(corps='﻿"x"'.encode("utf-8")),
            "JSON invalide": dict(corps=b'"x'),
            "nombre": dict(corps=3),
            "null": dict(corps=None, longueur=4, entree=io.BytesIO(b"null")),
            "objet": dict(corps={"f": "x"}),
            "tableau vide": dict(corps=[]),
            "tableau avec un nombre": dict(corps=["x", 2]),
            "tableau imbriqué": dict(corps=[["x"], "C"]),
            "NaN": dict(corps=b"NaN"),
            "trop d'arguments": dict(corps=["x", "C", "en trop"]),
        }
        for nom, options in cas.items():
            with self.subTest(cas=nom):
                self.verifier(400, requete("POST", chemin, **options))
        self.verifier(400, poster("factorisation", "apercu", ["x", "y"]))
        self.verifier(200, requete("POST", chemin, "x", type_contenu="Application/JSON; charset=utf-8"))
        self.verifier(200, requete("POST", chemin, ["x", "M"]))

    def test_500_sans_la_saisie(self):
        saisie = "x^2-SAISIE-ELEVE-91827"

        def piege(entree):
            raise ValueError(f"message avec {entree}")
        with mock.patch.object(module_de("factorisation"), "resoudre_json", piege), self.assertLogs("serveur", "ERROR") as journal:
            code, entetes, corps = poster("factorisation", "resoudre", saisie)
        self.verifier(500, (code, entetes, corps))
        self.assertNotIn(b"SAISIE", corps)
        ligne, = journal.output
        self.assertNotIn("SAISIE", ligne)
        self.assertNotIn("message avec", ligne)
        self.assertIn("outil=factorisation fonction=resoudre type=builtins.ValueError pile=", ligne)
        self.assertRegex(ligne, r"serveur/app\.py:\d+:calcul > tests/python/test_serveur\.py:\d+:piege$")

    def test_500_vraie_exception_et_sortie_qui_n_est_pas_une_chaine(self):
        with self.assertLogs("serveur", "ERROR") as journal:
            self.verifier(500, poster("etude-complete", "fenetre", "pas du JSON SAISIE"))
            with mock.patch.object(module_de("factorisation"), "apercu_json", lambda e: {"ok": True}):
                self.verifier(500, poster("factorisation", "apercu", "x"))
        self.assertEqual(len(journal.output), 2)
        self.assertIn("type=json.decoder.JSONDecodeError", journal.output[0])
        self.assertIn("etude-complete/etude_complete.py", journal.output[0])
        self.assertIn("type=builtins.TypeError", journal.output[1])
        for ligne in journal.output:
            self.assertNotIn("SAISIE", ligne)
            self.assertNotIn("Expecting value", ligne)
            self.assertNotIn("résultat", ligne)

    def test_journal_borne_pour_une_recursion(self):
        def profond(k):
            if k == 0:
                raise RecursionError("SAISIE")
            return profond(k - 1)
        with mock.patch.object(module_de("factorisation"), "apercu_json", lambda e: profond(500)), \
                self.assertLogs("serveur", "ERROR") as journal:
            self.verifier(500, poster("factorisation", "apercu", "x"))
        ligne, = journal.output
        self.assertEqual(ligne.count(" > "), app.CADRES_MAX)
        self.assertIn("cadres …", ligne)
        self.assertNotIn("SAISIE", ligne)

    def test_fonctions_anciennes_acceptees(self):
        manifeste = copy.deepcopy(outils_du_site.lire(outils_du_site.MANIFESTE))
        for entree in manifeste["outils"].values():
            entree["anciennes"] = [f for f in entree["fonctions"] if f == "apercu"]
        ancienne = app.Application(manifeste=manifeste)
        for outil in MANIFESTE:
            with self.subTest(outil=outil):
                code, _, corps = poster(outil, "apercu", "x^2-1", application=ancienne)
                self.assertEqual((code, corps), (200, module_de(outil).apercu_json("x^2-1").encode("utf-8")))


class TestSante(unittest.TestCase):
    """/api/sante (T1) : version, état de la machine, vrai calcul ; 503 sinon ; GET et HEAD."""
    VERSION = "976bc7b"

    def setUp(self):
        self.dossier = tempfile.TemporaryDirectory()
        self.etat = os.path.join(self.dossier.name, "etat.json")
        self.ecrire({"certificat_expire": self.dans(60), "disque_pourcent": 42.5})

    def tearDown(self):
        self.dossier.cleanup()

    @staticmethod
    def dans(jours):
        return (datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=jours)).isoformat()

    def ecrire(self, contenu):
        with open(self.etat, "w", encoding="utf-8") as f:
            f.write(contenu if isinstance(contenu, str) else json.dumps(contenu))

    def demander(self, methode="GET", **env):
        env = {app.VARIABLE_VERSION: self.VERSION, app.VARIABLE_ETAT: self.etat, **env}
        with mock.patch.dict(os.environ, {k: v for k, v in env.items() if v is not None}, clear=False):
            for k, v in env.items():
                if v is None:
                    os.environ.pop(k, None)
            return requete(methode, "/api/sante", type_contenu=None)

    def raison(self, reponse):
        code, entetes, corps = reponse
        self.assertEqual(code, 503)
        self.assertEqual(entetes["content-type"], JSON)
        self.assertEqual(entetes["cache-control"], "no-store")
        return json.loads(corps)["raison"]

    def test_tout_va_bien_get_et_head(self):
        code, entetes, corps = self.demander()
        self.assertEqual((code, json.loads(corps)), (200, {"ok": True, "version": self.VERSION}))
        self.assertEqual((entetes["content-type"], entetes["cache-control"]), (JSON, "no-store"))
        code_h, entetes_h, corps_h = self.demander("HEAD")
        self.assertEqual((code_h, corps_h, entetes_h), (200, b"", entetes))
        self.assertEqual(entetes_h["content-length"], str(len(corps)))
        self.assertEqual(self.demander(**{app.VARIABLE_VERSION: "0" * 40})[0], 200)

    def test_503_version(self):
        for version in (None, "", "abc", "976BC7B", "976bc7b ", "0" * 41, "976bc7g"):
            with self.subTest(version=version):
                self.assertEqual(self.raison(self.demander(**{app.VARIABLE_VERSION: version})), "version")
        code, entetes, corps = self.demander("HEAD", **{app.VARIABLE_VERSION: None})
        self.assertEqual((code, corps), (503, b""))

    def test_503_etat_absent_ou_illisible(self):
        self.assertEqual(self.raison(self.demander(**{app.VARIABLE_ETAT: None})), "etat_absent")
        self.assertEqual(self.raison(self.demander(**{app.VARIABLE_ETAT: ""})), "etat_absent")
        self.assertEqual(self.raison(self.demander(**{app.VARIABLE_ETAT: self.etat + ".absent"})), "etat_absent")
        self.assertEqual(self.raison(self.demander(**{app.VARIABLE_ETAT: self.dossier.name})), "etat_illisible")
        bons = {"certificat_expire": self.dans(60), "disque_pourcent": 10}
        illisibles = ["", "{", "[]", "null", json.dumps({"disque_pourcent": 10}), json.dumps({"certificat_expire": self.dans(60)}),
                      json.dumps({**bons, "certificat_expire": "bientôt"}),
                      json.dumps({**bons, "certificat_expire": self.dans(60)[:19]}),          # sans fuseau
                      json.dumps({**bons, "certificat_expire": 1893456000}),
                      json.dumps({**bons, "disque_pourcent": "10"}), json.dumps({**bons, "disque_pourcent": True}),
                      json.dumps({**bons, "disque_pourcent": None}), json.dumps({**bons, "disque_pourcent": -1}),
                      json.dumps({**bons, "disque_pourcent": 101}), json.dumps(bons).replace("10}", "NaN}")]
        for contenu in illisibles:
            with self.subTest(etat=contenu):
                self.ecrire(contenu)
                self.assertEqual(self.raison(self.demander()), "etat_illisible")

    def test_503_certificat_disque_et_fichier_perime(self):
        for jours, attendu in ((14.01, 200), (13.99, 503), (1, 503), (-3, 503)):
            with self.subTest(certificat=jours):
                self.ecrire({"certificat_expire": self.dans(jours), "disque_pourcent": 10})
                reponse = self.demander()
                self.assertEqual(reponse[0], attendu)
                if attendu == 503:
                    self.assertEqual(self.raison(reponse), "certificat")
        for disque, attendu in ((0, 200), (89.9, 200), (90, 503), (100, 503)):
            with self.subTest(disque=disque):
                self.ecrire({"certificat_expire": self.dans(60), "disque_pourcent": disque})
                reponse = self.demander()
                self.assertEqual(reponse[0], attendu)
                if attendu == 503:
                    self.assertEqual(self.raison(reponse), "disque")
        self.ecrire({"certificat_expire": self.dans(60), "disque_pourcent": 10})
        ancien = os.stat(self.etat).st_mtime - app.AGE_MAX_ETAT_S - 60
        os.utime(self.etat, (ancien, ancien))
        self.assertEqual(self.raison(self.demander()), "etat_perime")

    def test_503_calcul(self):
        module = module_de(app.CALCUL_DE_SANTE[0])
        with mock.patch.object(module, "resoudre_json", lambda e: '{"ok": false}'):
            self.assertEqual(self.raison(self.demander()), "calcul")
        with mock.patch.object(module, "resoudre_json", lambda e: '[1]'), self.assertLogs("serveur", "ERROR"):
            self.assertEqual(self.raison(self.demander()), "calcul")

        def piege(entree):
            raise ZeroDivisionError(entree)
        with mock.patch.object(module, "resoudre_json", piege), self.assertLogs("serveur", "ERROR") as journal:
            self.assertEqual(self.raison(self.demander()), "calcul")
            self.assertEqual(self.demander("HEAD")[0::2], (503, b""))
        self.assertEqual(len(journal.output), 2)
        for ligne in journal.output:
            self.assertNotIn("x^2-1", ligne)
            self.assertIn("type=builtins.ZeroDivisionError", ligne)

    def test_le_calcul_de_sante_est_un_vrai_calcul_ok(self):
        outil, fn, entree = app.CALCUL_DE_SANTE
        self.assertIn(fn, MANIFESTE[outil]["fonctions"])
        self.assertIs(json.loads(getattr(module_de(outil), fn + "_json")(entree))["ok"], True)


class TestDemarrage(unittest.TestCase):
    """Préchargement (T3), versions, sys.path dans l'ordre de moteurs.py, délai de gunicorn."""

    def test_dossiers_dans_l_ordre_de_moteurs_py(self):
        self.assertEqual(app.dossiers_moteurs(outils_du_site.lire(outils_du_site.MANIFESTE)), outils_du_site.dossiers_moteurs())

    def test_processus_neuf_prechargement_et_sys_path(self):
        """Dans un processus neuf, sans moteurs.py : chaque .py du manifeste et SymPy sont chargés dès l'import de l'application, et
        les dossiers des moteurs sont en tête de sys.path dans l'ordre de moteurs.py (le dernier en premier)."""
        code = ("import importlib.util, json, sys\n"
                f"spec = importlib.util.spec_from_file_location('app', {os.path.join(RACINE, 'serveur', 'app.py')!r})\n"
                "m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)\n"
                "print(json.dumps({'modules': sorted(sys.modules), 'path': sys.path}))\n")
        r = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, timeout=240, cwd=tempfile.gettempdir(),
                           env=dict(os.environ, PYTHONHASHSEED="0"))
        self.assertEqual(r.returncode, 0, r.stderr)
        sortie = json.loads(r.stdout)
        attendus = {os.path.splitext(os.path.basename(f))[0] for e in MANIFESTE.values() for f in e["fichiers"]}
        self.assertIn("exp_log_m", attendus)
        self.assertEqual(attendus - set(sortie["modules"]), set())
        self.assertIn("sympy", sortie["modules"])
        self.assertIn("mpmath", sortie["modules"])
        dossiers = [os.path.join(RACINE, d) for d in outils_du_site.dossiers_moteurs()]
        self.assertEqual(sortie["path"][:len(dossiers)], dossiers[::-1])

    def test_un_module_absent_empeche_le_demarrage(self):
        manifeste = copy.deepcopy(outils_du_site.lire(outils_du_site.MANIFESTE))
        manifeste["outils"]["factorisation"]["fichiers"].append("factorisation/module_absent_p1.py")
        with self.assertRaises(ModuleNotFoundError):
            app.Application(manifeste=manifeste)

    def test_une_fonction_absente_empeche_le_demarrage(self):
        manifeste = copy.deepcopy(outils_du_site.lire(outils_du_site.MANIFESTE))
        manifeste["outils"]["factorisation"]["fonctions"].append("absente")
        with self.assertRaisesRegex(RuntimeError, "resoudre_fa.absente_json absente"):
            app.Application(manifeste=manifeste)

    def test_le_calcul_de_sante_hors_du_manifeste_empeche_le_demarrage(self):
        manifeste = copy.deepcopy(outils_du_site.lire(outils_du_site.MANIFESTE))
        del manifeste["outils"][app.CALCUL_DE_SANTE[0]]
        with self.assertRaisesRegex(RuntimeError, "/api/sante"):
            app.Application(manifeste=manifeste)

    def test_versions(self):
        versions = outils_du_site.lire(outils_du_site.MANIFESTE)["versions"]
        app.verifier_versions(versions)
        for nom, fausse in (("sympy", "1.13.2"), ("mpmath", "1.3.1"), ("python", "3.11")):
            with self.subTest(nom=nom), self.assertRaisesRegex(RuntimeError, nom):
                app.verifier_versions({**versions, nom: fausse})
        with self.assertRaises(ModuleNotFoundError):
            app.verifier_versions({"paquet_absent_p1": "1.0"})

    def test_delai_de_gunicorn_plus_grand_que_les_delais_des_pages(self):
        """T3 : le serveur attend toujours plus longtemps que la page (délai par défaut de commun/outil.js, delaiCalcul des pages)."""
        with open(os.path.join(RACINE, "commun", "outil.js"), encoding="utf-8") as f:
            delais = [int(v) for v in re.findall(r"const DELAI_CALCUL = (\d+);", f.read())]
        self.assertEqual(len(delais), 1, "délai par défaut introuvable dans commun/outil.js")
        pages = 0
        for o in outils_du_site.registre():
            with open(os.path.join(RACINE, o["chemin"], "index.html"), encoding="utf-8") as f:
                trouves = [int(v) for v in re.findall(r"\bdelaiCalcul\s*:\s*(\d+)", f.read())]
            pages += bool(trouves)
            delais += trouves
        self.assertGreaterEqual(pages, 1, "aucun delaiCalcul lu dans les pages")
        self.assertGreater(app.DELAI_GUNICORN_S * 1000, max(delais))


class TestA10(unittest.TestCase):
    """A10 : le code du serveur ne nomme aucun module d'outil ; un nom d'outil n'apparaît que dans CALCUL_DE_SANTE (T1)."""

    def test_aucun_module_d_outil_nomme(self):
        with open(os.path.join(RACINE, "serveur", "app.py"), encoding="utf-8") as f:
            arbre = ast.parse(f.read())
        docstrings = {id(n.body[0].value) for n in ast.walk(arbre)
                      if isinstance(n, (ast.Module, ast.FunctionDef, ast.ClassDef)) and n.body
                      and isinstance(n.body[0], ast.Expr) and isinstance(n.body[0].value, ast.Constant)}
        modules = {e["module"] for e in MANIFESTE.values()} | {os.path.splitext(os.path.basename(f))[0]
                                                               for e in MANIFESTE.values() for f in e["fichiers"]}
        sante = next(n for n in ast.walk(arbre) if isinstance(n, ast.Assign)
                     and any(isinstance(c, ast.Name) and c.id == "CALCUL_DE_SANTE" for c in n.targets))
        dans_sante = {id(n) for n in ast.walk(sante)}
        for n in ast.walk(arbre):
            noms = []
            if isinstance(n, ast.Constant) and isinstance(n.value, str) and id(n) not in docstrings:
                noms = [n.value]
            elif isinstance(n, ast.Name):
                noms = [n.id]
            elif isinstance(n, ast.Attribute):
                noms = [n.attr]
            elif isinstance(n, ast.alias):
                noms = [n.name, n.asname]
            for nom in noms:
                with self.subTest(nom=nom, ligne=getattr(n, "lineno", None)):
                    self.assertNotIn(nom, modules)
                    if id(n) not in dans_sante:
                        self.assertFalse(any(o in (nom or "") for o in MANIFESTE), "nom d'outil hors de CALCUL_DE_SANTE")


class TestListePublique(unittest.TestCase):
    """T4 : la liste publique (git ls-files filtré) ne contient ni moteur, ni documentation, ni test (utilisée en P6)."""

    INTERDITS = ("moteur/", "docs/", "tests/", "serveur/", ".github/")
    EXTENSIONS_INTERDITES = (".py", ".pyc", ".md", ".json")

    @classmethod
    def setUpClass(cls):
        cls.publics = liste_publique.fichiers_publics(RACINE)
        cls.suivis = set(subprocess.run(["git", "ls-files"], cwd=RACINE, capture_output=True, text=True, check=True,
                                        timeout=60).stdout.splitlines())

    def test_arbre_du_depot(self):
        archive = io.BytesIO()
        with tarfile.open(fileobj=archive, mode="w") as tar:
            for chemin in self.publics:
                tar.add(os.path.join(RACINE, chemin), arcname=chemin)
        archive.seek(0)
        with tarfile.open(fileobj=archive) as tar:
            noms = tar.getnames()
        self.assertEqual(noms, self.publics)
        for nom in noms:
            with self.subTest(fichier=nom):
                self.assertIn(nom, self.suivis)
                self.assertFalse(nom.endswith(self.EXTENSIONS_INTERDITES))
                self.assertNotIn("__pycache__", nom.split("/"))
                self.assertFalse(nom.startswith(self.INTERDITS))
                self.assertTrue(nom.endswith((".html", ".css", ".js")))

    def test_le_site_est_complet(self):
        attendus = {"index.html"} | {o["chemin"] + "index.html" for o in outils_du_site.registre()}
        attendus |= {n for n in self.suivis if n.startswith("commun/") and n.endswith((".html", ".css", ".js"))}
        self.assertEqual(attendus - set(self.publics), set())
        self.assertIn("commun/outil.js", self.publics)
        self.assertNotIn("commun/registre.json", self.publics)

    def test_pieges(self):
        dossiers = {"commun", "factorisation"}
        for chemin in ("index.html", "commun/outil.js", "commun/style.css", "factorisation/index.html", "factorisation/a/b.js"):
            with self.subTest(public=chemin):
                self.assertTrue(liste_publique.est_public(chemin, dossiers))
        for chemin in ("factorisation/factorisation.py", "factorisation/__pycache__/x.js", "commun/.cache/x.js", ".github/x.js",
                       "moteur/manifeste.json", "moteur/a.js", "docs/a.html", "tests/pages/a.js", "serveur/a.js", "README.md",
                       "commun/registre.json", "autre/index.html", "factorisation/x.pyc", "a.js", "commun/x.html.py",
                       "commun", "factorisation/LISEZMOI.md"):
            with self.subTest(prive=chemin):
                self.assertFalse(liste_publique.est_public(chemin, dossiers))
        self.assertFalse(liste_publique.est_public("moteur/a.js", {"moteur"}))

    def test_registre_vers_un_dossier_interdit(self):
        for chemin in ("moteur/", "docs/", "tests/", "serveur/", ".github/", "a/b/", "/", "__pycache__/"):
            with self.subTest(chemin=chemin), tempfile.TemporaryDirectory() as d:
                os.makedirs(os.path.join(d, "commun"))
                with open(os.path.join(d, "commun", "registre.json"), "w", encoding="utf-8") as f:
                    json.dump({"outils": [{"chemin": "factorisation/"}, {"chemin": chemin}]}, f)
                with self.assertRaises(ValueError):
                    liste_publique.dossiers_des_pages(d)


if __name__ == "__main__":
    unittest.main()
