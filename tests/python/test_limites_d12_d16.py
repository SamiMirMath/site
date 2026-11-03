"""Chantier « etude-complete », partie P6 (03.11.2026) : décisions D12, D13, D16 de docs/chantiers/etude-complete/decisions.md, portée
EC + outil Limites (une seule rédaction, dans l'outil Limites, reprise telle quelle par l'Étude complète).

- D16 : ordre des bornes (−∞, valeurs interdites de gauche à droite, +∞) ; x → −∞ et x → +∞ regroupés en « x → ±∞ » seulement si les deux
  chaînes sont identiques au symbole près.
- D12 : le signe 0⁺ / 0⁻ d'un bas qui tend vers 0 (forme k/0, rédaction descendante) justifié par une valeur d'essai, avec ses garde-fous.
- D13 : 1⁺ / 1⁻ (e^{0⁺} = 1⁺), position du graphe par rapport à l'AH quand le signe d'approche est démontré, AV d'un seul côté et point
  exclu, 0⁺ / 0⁻ dans le bilan.
Les valeurs écrites sont recoupées par mpmath (oracle indépendant du moteur).
"""
import re
import unittest
from fractions import Fraction as F
from unittest import mock

import mpmath

from moteurs import ensemble_def  # noqa: F401  (chemins + SymPy)
import limites_asymptotes as la
import redaction_bh as rb
import resoudre_la as rla
from noyau import lire
from cas import entrees_page, CAS_LIMITES

MINF, INF = r"x \to -\infty", r"x \to +\infty"
ENTREES = list(dict.fromkeys(entrees_page("limites-asymptotes") + CAS_LIMITES["limites-asymptotes"] + entrees_page("etude-complete")
                             + CAS_LIMITES["etude-complete"] + ["e^(-x^2)", "e^(2/(x^2-4))", "e^((x^2+x-2)/(6x-12))", "(x^2-6)e^(-2x)",
                                                               "e^x(6-e^x)", "ln(x)/(x-1)", "1/(x(x-2))"]))
mp = mpmath.mp


def textes(r, ou):
    out = []
    for e in r["etudes"]:
        if e["ou"] == ou:
            for it in e["etapes"]:
                out.append(rb.texte_des_etapes(it["etapes"]) if it.get("type") == "descente" else it["html"])
    return "\n".join(out)


def cles(r):
    """Position de chaque étude sur la droite réelle (r = etudier(…, avec_bornes=True), une borne par étude) : (−∞ | a | +∞, côté)."""
    out = []
    for e, b in zip(r["etudes"], r["limites_bornes"]):
        if b["type"] == "inf":
            out.append((b["signe"] * float("inf"), 0))
        else:
            out.append((b["point_val"], 1 if e["ou"].endswith("^+") else 0))
    return out


def valeur_mp(saisie, x):
    return la._val_mp(mp, lire(saisie), x)


class TestOrdreDesBornes(unittest.TestCase):
    """D16 : −∞, puis les valeurs interdites croissantes (la gauche avant la droite), puis +∞ ; le bilan suit le même ordre."""

    def test_ordre_des_etudes(self):
        for entree in ENTREES:
            r = la.etudier(entree, avec_bornes=True)
            if not r.get("ok"):
                continue
            with self.subTest(f=entree):
                self.assertEqual(len(r["etudes"]), len(r["limites_bornes"]))
                self.assertEqual(cles(r), sorted(cles(r)))

    def test_exemples(self):
        self.assertEqual([e["ou"] for e in la.etudier("ln(x)/(x-1)")["etudes"]],
                         [r"x \to 0^+", r"x \to 1", INF])
        self.assertEqual([e["ou"] for e in la.etudier("e^(2/(x^2-4))")["etudes"]],
                         [MINF, r"x \to -2", r"x \to 2", INF])
        self.assertEqual([a["ou"] for a in la.etudier("e^(2/(x^2-4))")["asymptotes"]],
                         [MINF, r"x \to -2", r"x \to 2", INF])


class TestRegroupementDeLInfini(unittest.TestCase):
    """D16 : « x → ±∞ » seulement si les deux chaînes sont identiques au symbole près (et les conclusions au côté près)."""

    def test_regroupees_et_non_regroupees(self):
        for entree, attendu in [("e^(-x^2)", True), ("e^(2/(x^2-4))", True), ("e^((x^2+x-2)/(6x-12))", False),
                                ("(x^2-6)e^(-2x)", False), ("e^x(6-e^x)", False), ("e^(1/x)", False), ("(x^2-1)/(x-3)", False)]:
            with self.subTest(f=entree):
                ous = [e["ou"] for e in rla.etudes_affichees(la.etudier(entree)["etudes"])]
                self.assertEqual(r"x \to \pm\infty" in ous, attendu, ous)
                self.assertEqual(MINF in ous or INF in ous, not attendu, ous)

    def test_propriete_sur_le_corpus(self):
        """Un regroupement remplace exactement les deux études : mêmes étapes au symbole près, même limite (oracle mpmath) des deux côtés."""
        vus = 0
        for entree in ENTREES:
            r = la.etudier(entree, avec_bornes=True)
            if not r.get("ok"):
                continue
            aff = rla.etudes_affichees(r["etudes"])
            if not any(e["ou"] == r"x \to \pm\infty" for e in aff):
                self.assertEqual(aff, r["etudes"])
                continue
            vus += 1
            with self.subTest(f=entree):
                g, d = (next(e for e in r["etudes"] if e["ou"] == ou) for ou in (MINF, INF))
                self.assertEqual(rla._neutre(rla._sans_conclusion(g)), rla._neutre(rla._sans_conclusion(d)))
                self.assertEqual(len(aff), len(r["etudes"]) - 1)
                bornes = [b for b in r["limites_bornes"] if b["type"] == "inf"]
                self.assertEqual(bornes[0]["tex"], bornes[-1]["tex"])
                v = [valeur_mp(entree, s * mp.mpf(10) ** 6) for s in (-1, 1)]
                self.assertLess(abs(v[0] - v[1]), mp.mpf("1e-3") * (1 + abs(v[0])))
        self.assertGreaterEqual(vus, 3)

    def test_cartes(self):
        s = rla.resoudre("e^(-x^2)")
        limites = [c for c in s["cartes"] if c["titre"] == "Limite"]
        self.assertEqual([c["titre_tex"] for c in limites], [r"x \to \pm\infty"])
        tout = "\n".join(b.get("html", b.get("tex", "")) for c in s["cartes"] for b in c["blocs"])
        self.assertIn(r"\lim_{x\to \pm\infty} e^{-x^{2}} = 0^{+}", tout)
        self.assertIn(r"Asymptote horizontale : \(y = 0\) (des deux côtés). \(f(x) \to 0^{+}\) : le graphe est au-dessus.", tout)
        avant_bilan = re.sub(r"\s", "", tout.split("Asymptote horizontale (")[0])
        self.assertNotIn(r"x\to-\infty", avant_bilan)                 # plus aucune limite écrite en −∞ ni en +∞ seule
        self.assertNotIn(r"x\to+\infty", avant_bilan)


class TestValeurDEssai(unittest.TestCase):
    """D12 : « bas : 6x − 12 → 0 ; avec x = 1,99 : 6 · 1,99 − 12 = −0,06 < 0, donc 0⁻ » et ses garde-fous."""

    def test_ex7_et_d(self):
        t = textes(la.etudier("e^((x^2+x-2)/(6x-12))"), r"x \to 2")
        self.assertIn(r"Haut de l'exposant : \(x^{2} + x - 2 \to 2^{2} + 2 - 2 = 4\) (pas 0, donc pas indéterminée).", t)
        self.assertIn(r"Bas de l'exposant : \(6x - 12 \to 0\) ; avec \(x = 1{,}99\) : \(6 \cdot 1{,}99 - 12 = -0{,}06 < 0\), "
                      r"donc \(0^{-}\).", t)
        self.assertIn(r"avec \(x = 2{,}01\) : \(6 \cdot 2{,}01 - 12 = 0{,}06 > 0\), donc \(0^{+}\)", t)
        t = textes(la.etudier("e^(2/(x^2-4))"), r"x \to -2")
        self.assertIn(r"avec \(x = -2{,}01\) : \(\left(-2{,}01\right)^{2} - 4 = 0{,}0401 > 0\), donc \(0^{+}\)", t)
        self.assertIn(r"avec \(x = -1{,}99\) : \(\left(-1{,}99\right)^{2} - 4 = -0{,}0399 < 0\), donc \(0^{-}\)", t)
        self.assertNotIn("Haut de l'exposant", t)                     # haut constant (2) : rien à remplacer

    def test_quotient_hors_exposant(self):
        t = textes(la.etudier("ln(x^2-4x)/(x-5)"), r"x \to 5")
        self.assertIn(r"Bas : \(x - 5 \to 0\) ; avec \(x = 4{,}99\) : \(4{,}99 - 5 = -0{,}01 < 0\), donc \(0^{-}\)", t)

    def test_les_valeurs_ecrites_sont_justes(self):
        """Oracle : chaque « avec x = t : … = v » du corpus est du bon côté du point, à 0,01 au plus, v a le signe écrit et celui du 0."""
        motif = re.compile(r"avec \\\(x = (-?[\d{},]+)\\\) : \\\((.*?) = (-?[\d{},]+) ([<>]) 0\\\), donc \\\(0\^\{([+-])\}\\\)")
        vus = 0
        for entree in ENTREES:
            r = la.etudier(entree, avec_bornes=True)
            if not r.get("ok"):
                continue
            for e, b in zip(r["etudes"], r["limites_bornes"]):
                for it in e["etapes"]:
                    if it.get("type") != "descente" or b["type"] != "fini":
                        continue
                    cote = re.search(r"\^\{([+-])\}", it["enonce_tex"]).group(1)
                    for m in motif.finditer(rb.texte_des_etapes(it["etapes"])):
                        vus += 1
                        with self.subTest(f=entree, ou=e["ou"], t=m.group(1)):
                            t = F(m.group(1).replace("{,}", "."))
                            v = F(m.group(3).replace("{,}", "."))
                            self.assertEqual(m.group(4), ">" if v > 0 else "<")
                            self.assertEqual(m.group(5), "+" if v > 0 else "-")
                            self.assertEqual(float(t) > b["point_val"], cote == "+")
                            self.assertLessEqual(abs(float(t) - b["point_val"]), 0.01 + 1e-12)
        self.assertGreaterEqual(vus, 6)

    def borne(self, a):
        return {"type": "fini", "point": la.Num.rat(F(a)), "cote": "deux"}

    def essai(self, bas, a, d, f=None, bornes=()):
        pt = la.Pt(self.borne(a), d)
        D = lire(bas)
        B = rb.lim(D, pt)
        with mock.patch.object(la, "_BORNES_FINIES", list(bornes)):
            return rb.valeur_d_essai(D, pt, lire(f) if f else lire("1/(" + bas + ")"), B)

    def test_autre_zero_proche(self):
        """Un autre zéro du bas à 0,005 de a : le point d'essai se rapproche (2,001), jamais au-delà de ce zéro."""
        t = self.essai("(x-2)(200x-401)", 2, 1)
        self.assertIn(r"x = 2{,}001", t)
        self.assertIn("donc \\(0^{-}\\)", t)                          # (2,001 − 2)(400,2 − 401) < 0
        self.assertLess(float(mp.mpf("2.001") - 2) * float(200 * mp.mpf("2.001") - 401), 0)

    def test_autre_valeur_interdite_proche(self):
        t = self.essai("6x-12", 2, -1, f="e^(1/(6x-12))", bornes=[1.995, 2.0])
        self.assertIn(r"x = 1{,}999", t)

    def test_cas_sans_valeur_d_essai(self):
        self.assertIsNone(self.essai("x", 0, -1))                                  # x → 0⁻ se lit directement
        self.assertIsNone(self.essai("e^x-1", 0, 1))                               # bas non polynomial
        self.assertIsNone(self.essai("3x-1", F(1, 3), 1))                          # point sans écriture décimale finie
        t = textes(la.etudier("e^(1/(x^2-2))"), r"x \to \sqrt{2}")                   # point irrationnel : écriture habituelle
        self.assertNotIn("avec \\(x =", t)
        self.assertIn("0^{-}", t)

    def test_signe_contredit_aucune_valeur_d_essai(self):
        pt = la.Pt(self.borne(2), -1)
        B = rb.lim(lire("6x-12"), pt)
        B_faux = la.Lim.fin(0, -B.ap)
        self.assertIsNone(rb.valeur_d_essai(lire("6x-12"), pt, lire("1/(6x-12)"), B_faux))


class TestSigneDApprocheEtConclusions(unittest.TestCase):
    """D13 : 1⁺ / 1⁻ confirmé par une sonde, position du graphe, AV d'un seul côté, 0⁺ dans le bilan."""

    def test_un_plus(self):
        r = la.etudier("e^(2/(x^2-4))", avec_bornes=True)
        t = textes(r, INF)
        self.assertIn(r"e^{0^{+}} = 1^{+}\) (\(e^{t} > 1\) pour \(t > 0\))", t)
        self.assertIn(r"\lim_{x\to +\infty} e^{\frac{2}{x^{2} - 4}} = 1^{+}", t)
        self.assertEqual([b["tex"] for b in r["limites_bornes"] if b["type"] == "inf"], ["1^{+}", "1^{+}"])
        self.assertIn(r"Asymptote horizontale : \(y = 1\) (à droite). \(f(x) \to 1^{+}\) : le graphe est au-dessus.", t)
        self.assertGreater(valeur_mp("e^(2/(x^2-4))", mp.mpf(10) ** 4), 1)                # oracle

    def test_un_moins_et_au_dessous(self):
        r = la.etudier("e^(1/x)")
        t = textes(r, MINF)
        self.assertIn(r"e^{0^{-}} = 1^{-}\) (\(e^{t} < 1\) pour \(t < 0\))", t)
        self.assertIn(r"Asymptote horizontale : \(y = 1\) (à gauche). \(f(x) \to 1^{-}\) : le graphe est au-dessous.", t)
        self.assertLess(valeur_mp("e^(1/x)", -mp.mpf(10) ** 4), 1)                        # oracle
        self.assertEqual([a.get("position") for a in r["asymptotes"] if a["genre"] == "horizontale"], ["au-dessous", "au-dessus"])

    def test_sonde_en_desaccord(self):
        """Si la sonde ne confirme pas le signe de f − 1 : ni 1⁺, ni position (l'AH reste)."""
        with mock.patch.object(rb, "ecart_confirme", return_value=False):
            r = la.etudier("e^(2/(x^2-4))", avec_bornes=True)
        t = textes(r, INF)
        self.assertNotIn("1^{+}", t)
        self.assertNotIn("au-dessus", t)
        self.assertIn(r"Asymptote horizontale : \(y = 1\) (à droite).", t)
        self.assertEqual([b["tex"] for b in r["limites_bornes"] if b["type"] == "inf"], ["1", "1"])
        self.assertNotIn("position", [k for a in r["asymptotes"] for k in a])

    def test_sonde(self):
        pt = la.Pt({"type": "inf", "signe": 1})
        self.assertTrue(rb.ecart_confirme(lire("e^(2/(x^2-4))"), pt, 1, 1))
        self.assertFalse(rb.ecart_confirme(lire("e^(2/(x^2-4))"), pt, 1, -1))
        self.assertFalse(rb.ecart_confirme(lire("e^(-2/(x^2-4))"), pt, 1, 1))

    def test_position_seulement_si_le_signe_est_demontre(self):
        """La position n'est écrite que si le tableau de variations porte ℓ⁺ / ℓ⁻ ; elle est juste (oracle mpmath, ±10⁴)."""
        vus = 0
        for entree in ENTREES:
            r = la.etudier(entree, avec_bornes=True)
            if not r.get("ok"):
                continue
            bornes = {b["signe"]: b["tex"] for b in r["limites_bornes"] if b["type"] == "inf"}
            for a in r["asymptotes"]:
                if a["genre"] != "horizontale":
                    continue
                s = 1 if a["ou"] == INF else -1
                with self.subTest(f=entree, ou=a["ou"]):
                    signe = bornes[s][-2] if bornes[s].endswith(("^{+}", "^{-}")) else None
                    self.assertEqual(a.get("position"), {"+": "au-dessus", "-": "au-dessous", None: None}[signe])
                    if a.get("position"):
                        vus += 1
                        ecart = valeur_mp(entree, s * mp.mpf(10) ** 4) - mp.mpf(a["valeur_val"])
                        self.assertEqual(ecart > 0, a["position"] == "au-dessus")
        self.assertGreaterEqual(vus, 8)

    def test_av_d_un_seul_cote(self):
        r = la.etudier("e^(2/(x^2-4))")
        t = textes(r, r"x \to -2")
        self.assertIn(r"Asymptote verticale : \(x = -2\), seulement du côté gauche. À droite, \(f(x) \to 0^{+}\) : le graphe s'approche "
                      r"du point \((-2\,;\,0)\), qui n'appartient pas au graphe (rond vide).", t)
        av = [a for a in r["asymptotes"] if a["genre"] == "verticale"]
        self.assertEqual([(a["gauche_tex"], a["droite_tex"]) for a in av], [(r"+\infty", "0^{+}"), ("0^{+}", r"+\infty")])

    def test_autre_cote_non_determine(self):
        """L'autre côté « ? » : pas de « seulement » (une limite inconnue pourrait être infinie)."""
        r = la.etudier("e^(1/x)")
        borne = {"type": "fini", "point": la.Num.rat(F(0)), "cote": "deux"}
        items = []
        la._bilan_deux_cotes(borne["point"], r"x \to 0", ("?", r"+\infty"), (None, None), items)
        self.assertNotIn("seulement", items[-1]["html"])
        self.assertIn("(du côté droit)", items[-1]["html"])
        self.assertTrue(r["ok"])


if __name__ == "__main__":
    unittest.main()
