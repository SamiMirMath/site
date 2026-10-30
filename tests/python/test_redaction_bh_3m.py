"""Refonte de la rédaction des limites (3M, 30.10.2026) : la rédaction descendante est contrôlée contre les transcriptions du corrigé
(docs/specifications/redaction-limites-3m.md, section 3 : le contrat des tests ; les PDF de cours ne servent jamais aux tests).

Trois familles :
  - CONTRAT : pour chaque exercice du corrigé (8.11 à 8.14, exemples 5 et 6), la suite des titres d'étapes, le nombre de BH, les dérivées
    haut / bas, la prédiction, le résultat signé et la confirmation. Les écarts de formulation mineurs sont listés dans
    docs/chantiers/limites-asymptotes/suivi-refonte.md.
  - STRUCTURE : règles R1 à R17 vérifiées sur tout le corpus (tableau BH avant la chaîne, forme revérifiée avant chaque BH, R14…).
  - TRANSVERSE : valeurs contre le corpus de l'enseignant, signe 0⁺/0⁻, nombre de replis, aucune alerte, cartes « Étape n » consécutives.
"""
import os
import re
import sys
import unittest

from moteurs import ensemble_def  # noqa: F401  (chemins + SymPy)
import limites_asymptotes as la
import redaction_bh as rb
import resoudre_la as rla
import sortie as so
from cas import entrees_page

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "donnees"))
from corpus_limites_3m import CAS, PAS_PRIS_EN_CHARGE  # noqa: E402

INF = r"x \to +\infty"
MINF = r"x \to -\infty"
BH_SIGNE = r"\overset{\text{BH}}{=}"
REPLI = "n'est pas rédigé ici"


def descentes(saisie, ou):
    r = la.etudier(saisie)
    assert r["ok"], r
    return [i for e in r["etudes"] if e["ou"] == ou for i in e["etapes"] if i.get("type") == "descente"]


def titres(d):
    return [e["titre"] for e in d["etapes"]]


def blocs(d, type_=None):
    return [b for e in d["etapes"] for b in e["blocs"] if type_ is None or b["type"] == type_]


def derivees(d):
    return [(b["dhaut"], b["dbas"]) for b in blocs(d, "bh")]


def resultat(d):
    return [b["tex"] for b in blocs(d, "resultat_lim")][-1]


def prediction(d):
    return next((b for b in blocs(d, "encadre") if b["genre"] == "prediction"), None)


def confirmation(d):
    return next((b["html"] for b in blocs(d, "texte") if b.get("style") == "confirme"), None)


PODIUM = "✓ Le calcul confirme la prédiction du podium."
CALCULATRICE = "La calculatrice avait bien « deviné » : le calcul le confirme."

# (id corrigé, saisie, borne, rang de la rédaction dans la borne, titres, dérivées (haut, bas) par BH, résultat final, confirmation)
CONTRAT = [
    ("8.11a", "e^x/ln(x)", INF, 0, ["on remplace", "BH", "on simplifie", "on remplace"],
     [("e^{x}", r"\frac{1}{x}")], r"= +\infty", PODIUM),
    ("8.11b", "x^3*ln(x)", r"x \to 0^+", 0,
     ["on remplace", "on transforme le produit en quotient", "on vérifie la forme", "BH", "on simplifie", "on remplace"],
     [(r"\frac{1}{x}", r"-3x^{-4} = -\frac{3}{x^{4}}")], r"= 0^{-}", PODIUM),
    ("8.11c", "x^2*e^x", MINF, 0,
     ["on remplace", "on transforme le produit en quotient", "on vérifie la forme", "BH (1re fois)", "BH (2e fois)", "on remplace"],
     [("2x", "-e^{-x}"), ("2", "e^{-x}")], r"= 0^{+}", PODIUM),
    ("8.11d", "x^2*e^(-5x)", INF, 0,
     ["on remplace", "on transforme le produit en quotient", "on vérifie la forme", "BH (1re fois)", "BH (2e fois)", "on remplace"],
     [("2x", "5e^{5x}"), ("2", "25e^{5x}")], r"= 0^{+}", PODIUM),
    ("Ex5a", "x^2*e^(-x)", INF, 0,
     ["on remplace", "on transforme le produit en quotient", "on vérifie la forme", "BH (1re fois)", "BH (2e fois)", "on remplace"],
     [("2x", "e^{x}"), ("2", "e^{x}")], r"= 0^{+}", PODIUM),
    ("Ex5b", "x*e^(1/x)", r"x \to 0", 1,
     ["on remplace", "on transforme le produit en quotient", "on vérifie la forme", "BH", "on remplace"],
     [(r"-\frac{1}{x^{2}}\,e^{\frac{1}{x}}", r"-\frac{1}{x^{2}}")], r"= +\infty", PODIUM),
    ("Ex5c", "e^(-x)/x^2", MINF, 0, ["on remplace", "BH (1re fois)", "BH (2e fois)", "on remplace"],
     [("-e^{-x}", "2x"), ("e^{-x}", "2")], r"= +\infty", PODIUM),
    ("Ex5d", "e^(-x)/(4x)", INF, 0, ["on remplace", "on conclut directement"], [], r"\dfrac{0^{+}}{+\infty} = 0^{+}", None),
    ("8.12a", "ln(x)/e^(2x)", INF, 0, ["on remplace", "BH", "on simplifie", "on remplace"],
     [(r"\frac{1}{x}", "2e^{2x}")], r"= 0^{+}", PODIUM),
    ("8.12b", "e^(-x)*ln(x^3)", INF, 0,
     ["on remplace", "on simplifie le logarithme", "on transforme le produit en quotient", "on vérifie la forme", "BH", "on simplifie",
      "on remplace"], [(r"\frac{3}{x}", "e^{x}")], r"= 0^{+}", PODIUM),
    ("8.12c", "e^(-x)*x", MINF, 0, ["on remplace", "on conclut directement"], [], r"= -\infty", None),
    ("8.12d", "e^x*ln(-x)", MINF, 0,
     ["on remplace", "on transforme le produit en quotient", "on vérifie la forme", "BH", "on simplifie", "on remplace"],
     [(r"\frac{1}{x}", "-e^{-x}")], r"= 0^{+}", PODIUM),
    ("8.12e", "x^3*e^(3x-5)", MINF, 0,
     ["on remplace", "on sort la constante", "on transforme le produit en quotient", "on vérifie la forme", "BH (1re fois)",
      "BH (2e fois)", "BH (3e fois)", "on remplace", "on n'oublie pas la constante"],
     [("3x^{2}", "-3e^{-3x}"), ("-2x", "-3e^{-3x}"), ("2", "-9e^{-3x}")], r"= 0^{-}", PODIUM),
    ("8.12f", "e^(1/x)/x^2", r"x \to 0", 0, ["on remplace", "on conclut directement"], [], r"\dfrac{+\infty}{0^{+}} = +\infty", None),
    ("8.12g", "e^(1/x)*x^2", r"x \to 0", 1,
     ["on remplace", "on transforme le produit en quotient", "on vérifie la forme", "BH", "on simplifie", "on remplace"],
     [(r"-\frac{1}{x^{2}}\,e^{\frac{1}{x}}", "-2x^{-3} = -\\frac{2}{x^{3}}")], r"= +\infty", PODIUM),
    ("8.12h", "e^(-1/x)/x", r"x \to 0", 1, ["on remplace", "on réécrit", "BH", "on remplace"],
     [(r"-\frac{1}{x^{2}}", r"-\frac{1}{x^{2}}\,e^{\frac{1}{x}}")], r"= 0^{+}", PODIUM),
    ("Ex6", "e^((3x+4)/(x-2))", INF, 0, ["limite de l'exposant, à part", "on applique l'exponentielle"], [], r"= e^{3} \approx 20{,}09", PODIUM),
    ("8.13a", "e^(-x)", INF, 0, ["on remplace"], [], r"= 0^{+}", None),
    ("8.13b", "e^((x^2-3x+2)/(2x^2))", INF, 0, ["limite de l'exposant, à part", "on applique l'exponentielle"], [],
     r"= \sqrt{e} \approx 1{,}65", PODIUM),
    ("8.13c", "e^(-2x/(x^2-5))", INF, 0, ["limite de l'exposant, à part", "on applique l'exponentielle"], [], r"= e^{0} = 1", PODIUM),
    ("8.13d", "e^((3x^2+2)/(2x))", MINF, 0, ["limite de l'exposant, à part", "on applique l'exponentielle"], [], r"= e^{-\infty} = 0^{+}", PODIUM),
    ("8.13e", "ln((3x^2-3x+2)/(x^2-5x+2))", INF, 0, ["limite de l'intérieur du ln", "on applique le logarithme"], [], r"\approx 1{,}10", PODIUM),
    ("8.13f", "ln(1/x)", INF, 0, ["on remplace"], [], r"= -\infty", None),
    ("8.14", "ln(1+e^x)/e^x", MINF, 0, ["on remplace", "BH", "on simplifie", "on remplace"],
     [(r"\frac{e^{x}}{1 + e^{x}}", "e^{x}")], r"= 1", CALCULATRICE),
]


class TestContratDuCorrige(unittest.TestCase):
    def test_chaque_exercice_du_corrige(self):
        for id_, saisie, ou, rang, titres_attendus, derivees_attendues, fin, conf in CONTRAT:
            with self.subTest(exercice=id_):
                d = descentes(saisie, ou)[rang]
                self.assertEqual(titres(d), titres_attendus)
                self.assertEqual(sum(t.startswith("BH") for t in titres(d)), len(derivees_attendues))
                self.assertEqual(derivees(d), derivees_attendues)
                self.assertTrue(resultat(d).endswith(fin), resultat(d))
                self.assertEqual(confirmation(d), conf)
                self.assertEqual(prediction(d) is not None, conf is not None)
                self.assertEqual(d["alertes"], [])

    def test_prediction_du_podium_8_11a(self):
        lignes = prediction(descentes("e^x/ln(x)", INF)[0])["lignes"]
        self.assertIn("Au haut : \\(e^{x}\\). Au bas : \\(\\ln(x)\\).", lignes[0])
        self.assertIn("l'exponentielle bat le logarithme : c'est le <b>haut</b> qui gagne", lignes[0])
        self.assertEqual(lignes[1], "Signe : haut > 0, bas > 0, donc quotient > 0.")
        self.assertEqual(lignes[2], "<b>On s'attend à :</b> \\(+\\infty\\)")

    def test_prediction_avec_t_en_zero_plus(self):
        lignes = prediction(descentes("x*e^(1/x)", r"x \to 0")[1])["lignes"]
        self.assertTrue(lignes[0].startswith("On pense à \\(t = \\dfrac{1}{x}\\)"), lignes)
        self.assertIn("Au haut : \\(e^{t}\\). Au bas : \\(t\\).", lignes[1])

    def test_8_14_podium_inapplicable_et_tableau_de_valeurs(self):
        d = descentes("ln(1+e^x)/e^x", MINF)[0]
        enc = prediction(d)
        self.assertIn("ne peut pas aider", enc["lignes"][0])
        (v,) = blocs(d, "valeurs")
        self.assertEqual(v["xs"], ["-1", "-10", "-20", "-25", "-30"])
        self.assertEqual(v["fs"], ["0{,}8515", "0{,}99998", r"\approx 1", r"\approx 1", r"\approx 1"])

    def test_8_12h_le_piege_puis_on_reecrit(self):
        d = descentes("e^(-1/x)/x", r"x \to 0")[1]
        piege = next(b for b in blocs(d, "encadre") if b["genre"] == "piege")
        self.assertEqual(piege["titre"], "Le piège")
        self.assertIn("BH tourne en rond", piege["lignes"][1])
        self.assertIn(r"x^{2}", piege["lignes"][1])
        self.assertEqual(titres(d)[1], "on réécrit")

    def test_8_12e_constante_sortie_puis_rappelee(self):
        d = descentes("x^3*e^(3x-5)", MINF)[0]
        txt = rb.texte_des_etapes(d["etapes"])
        self.assertIn(r"e^{3x - 5} = e^{3x}\cdot e^{-5}", txt)
        self.assertIn("constante positive", txt)
        self.assertIn(r"e^{-5} \cdot 0^{-} = 0^{-}", txt)

    def test_attention_8_12c_et_ex5d(self):
        for saisie, ou in [("e^(-x)*x", MINF), ("e^(-x)/(4x)", INF)]:
            with self.subTest(f=saisie):
                att = [b for b in blocs(descentes(saisie, ou)[0], "encadre") if b["genre"] == "attention"]
                self.assertEqual(len(att), 1)
        self.assertIn("ne faut pas</b> utiliser BH", [b for b in blocs(descentes("e^(-x)/(4x)", INF)[0], "encadre")][0]["lignes"][0])


class TestStructure(unittest.TestCase):
    """Règles du corrigé sur toutes les rédactions descendantes du corpus et des exemples de la page."""
    ENTREES = list(dict.fromkeys([c.saisie for c in CAS if c.id not in PAS_PRIS_EN_CHARGE] + entrees_page("limites-asymptotes")))

    @classmethod
    def toutes(cls):
        for saisie in cls.ENTREES:
            r = la.etudier(saisie)
            if not r["ok"]:
                continue
            for e in r["etudes"]:
                for i in e["etapes"]:
                    if i.get("type") == "descente":
                        yield saisie, e["ou"], i

    def test_au_moins_cent_redactions_descendantes(self):
        self.assertGreaterEqual(sum(1 for _ in self.toutes()), 100)

    def test_le_tableau_bh_precede_la_chaine(self):
        """R9 : « haut : … ⟶ dérivée : … » avant la chaîne « lim … =^BH lim … »."""
        for saisie, ou, d in self.toutes():
            for e in d["etapes"]:
                if not e["titre"].startswith("BH"):
                    continue
                with self.subTest(f=saisie, ou=ou, etape=e["titre"]):
                    types = [(b["type"], BH_SIGNE in b.get("html", "")) for b in e["blocs"]]
                    ibh = [i for i, (t, _) in enumerate(types) if t == "bh"]
                    ichaine = [i for i, (t, c) in enumerate(types) if c]
                    self.assertEqual(len(ibh), 1)
                    self.assertEqual(len(ichaine), 1)
                    self.assertLess(ibh[0], ichaine[0])

    def test_forme_revérifiée_avant_chaque_nouveau_bh(self):
        """R11 : un BH suivi d'un autre BH annonce « encore indéterminée » avec ses signes."""
        for saisie, ou, d in self.toutes():
            ets = d["etapes"]
            for i, e in enumerate(ets[:-1]):
                if not e["titre"].startswith("BH"):
                    continue
                suivant = ets[i + 1]["titre"]
                avec_forme = "encore" in rb.texte_des_etapes([e]) and "indéterminée" in rb.texte_des_etapes([e])
                if suivant.startswith("BH"):
                    with self.subTest(f=saisie, ou=ou, etape=e["titre"]):
                        self.assertTrue(avec_forme)

    def test_r14_aucune_forme_indeterminee_suivie_d_une_valeur(self):
        for saisie, ou, d in self.toutes():
            for ligne in rb.texte_des_etapes(d["etapes"]).split("\n"):
                with self.subTest(f=saisie, ou=ou):
                    self.assertFalse(rb.viole_r14(ligne), ligne)

    def test_aucune_croissance_comparee_ni_limite_de_reference(self):
        for saisie, ou, d in self.toutes():
            t = rb.texte_des_etapes(d["etapes"])
            self.assertNotIn("croissance comparée", t, saisie)
            self.assertNotIn("limite de référence", t, saisie)

    def test_podium_seulement_dans_les_encadres_et_la_confirmation(self):
        for saisie, ou, d in self.toutes():
            for e in d["etapes"]:
                for b in e["blocs"]:
                    if b["type"] == "encadre" and b["genre"] == "prediction":
                        continue
                    if (b["type"] == "texte" and b.get("style") == "confirme") or b["type"] == "sous_calcul":
                        continue
                    self.assertNotIn("podium", rb.texte_des_etapes([{"titre": "", "blocs": [b]}]), (saisie, ou))

    def test_aucune_alerte_et_prediction_toujours_confirmee(self):
        """Une prédiction du podium est affichée seulement si le calcul la confirme (sinon elle est retirée et une alerte est levée : bug)."""
        for saisie, ou, d in self.toutes():
            with self.subTest(f=saisie, ou=ou):
                self.assertEqual(d["alertes"], [])
                if prediction(d) is not None and not blocs(d, "valeurs"):
                    self.assertEqual(confirmation(d), PODIUM)

    def test_le_dernier_pas_porte_le_resultat_encadre(self):
        for saisie, ou, d in self.toutes():
            with self.subTest(f=saisie, ou=ou):
                self.assertEqual(sum(b["type"] == "resultat_lim" for b in blocs(d)), 1)
                self.assertTrue(any(b["type"] == "resultat_lim" for b in d["etapes"][-1]["blocs"]))

    def test_les_deux_signes_zero_sont_ecrits(self):
        """R17 : 0⁺ / 0⁻ dès que le signe est connu, y compris dans le résultat (cas du corpus dont la valeur est 0)."""
        for c in CAS:
            if c.id in PAS_PRIS_EN_CHARGE or c.attendu != "0" or not c.signe0 or c.cote != "":
                continue
            for saisie, ou, d in self.toutes():
                if saisie != c.saisie or ou != (MINF if c.point == "-oo" else INF):
                    continue
                with self.subTest(id=c.id):
                    self.assertTrue(resultat(d).endswith("0^{+}" if c.signe0 == "+" else "0^{-}"), resultat(d))

    def test_ln_de_x_cube_est_simplifie_avant_bh(self):
        t = titres(descentes("e^(-x)*ln(x^3)", INF)[0])
        self.assertLess(t.index("on simplifie le logarithme"), t.index("on transforme le produit en quotient"))

    def test_ln_reste_en_haut_avec_sa_remarque(self):
        for saisie, ou in [("x^3*ln(x)", r"x \to 0^+"), ("e^x*ln(-x)", MINF), ("e^(-x)*ln(x^3)", INF)]:
            t = rb.texte_des_etapes(descentes(saisie, ou)[0]["etapes"])
            self.assertIn("Pourquoi garder", t, saisie)

    def test_les_derivees_composees_sont_expliquees(self):
        t = rb.texte_des_etapes(descentes("e^x*ln(-x)", MINF)[0]["etapes"])
        self.assertIn(r"avec \(u = -x\)", t)
        t = rb.texte_des_etapes(descentes("ln(1+e^x)/e^x", MINF)[0]["etapes"])
        self.assertIn(r"avec \(u = 1 + e^{x}\)", t)
        t = rb.texte_des_etapes(descentes("e^(-1/x)/x", r"x \to 0")[1]["etapes"])
        self.assertIn("u'e^{u}", t)


class TestCartes(unittest.TestCase):
    """Les étapes deviennent des cartes « Étape n : titre. », numérotées sans trou, dans une sortie valide."""

    def test_cartes_etape_numerotees_et_sortie_valide(self):
        for saisie in TestStructure.ENTREES:
            with self.subTest(f=saisie):
                s = rla.resoudre(saisie)
                self.assertEqual(so.valider(s), [])
                n = 0
                for c in s["cartes"]:
                    m = re.match(r"Étape (\d+) : ", c["titre"])
                    if m:
                        n += 1
                        self.assertEqual(int(m.group(1)), n)
                    else:
                        n = 0                       # nouvelle borne : la numérotation repart de 1

    def test_les_encadres_sont_valides(self):
        s = rla.resoudre("e^(-1/x)/x")
        genres = {b["genre"] for c in s["cartes"] for b in c["blocs"] if b["type"] == "encadre"}
        self.assertTrue({"prediction", "piege"} <= genres, genres)


class TestTransverse(unittest.TestCase):
    def test_au_plus_13_replis_sur_le_corpus(self):
        replis = 0
        for c in {(c.saisie) for c in CAS if c.id not in PAS_PRIS_EN_CHARGE}:
            r = la.etudier(c)
            replis += sum(REPLI in i.get("html", "") for e in r["etudes"] for i in e["etapes"] if i.get("type") != "descente")
        self.assertLessEqual(replis, 13, replis)

    def test_r14_sur_les_ancienne_redactions_conservees(self):
        """L'ancienne rédaction qui prend le relais ne contient jamais « forme indéterminée = valeur » : sinon le repli s'affiche."""
        for saisie in TestStructure.ENTREES:
            r = la.etudier(saisie)
            for e in r["etudes"]:
                for i in e["etapes"]:
                    if i.get("type") == "texte":
                        self.assertFalse(rb.viole_r14(i["html"]), (saisie, e["ou"]))

    def test_valeurs_infinies_contre_le_corpus(self):
        for c in CAS:
            if c.id in PAS_PRIS_EN_CHARGE or c.attendu not in ("oo", "-oo") or c.cote != "":
                continue
            ou = INF if c.point == "+oo" else MINF
            attendu = "+\\infty" if c.attendu == "oo" else "-\\infty"
            for d in descentes(c.saisie, ou):
                with self.subTest(id=c.id):
                    self.assertTrue(resultat(d).endswith(attendu), resultat(d))

    def test_signe_zero_etudie_par_la_prediction(self):
        for saisie, ou, attendu in [("x^2*e^x", MINF, "0^{+}"), ("x^3*e^(3x-5)", MINF, "0^{-}"), ("e^x*ln(-x)", MINF, "0^{+}")]:
            self.assertTrue(resultat(descentes(saisie, ou)[0]).endswith(attendu))


if __name__ == "__main__":
    unittest.main()
