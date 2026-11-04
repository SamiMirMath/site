"""T12 — etude-complete/resoudre_ec.py : sortie du format commun, sans rien perdre de l'ancienne,
cartes dans l'ordre de la page (EC-14), et cohérence avec les sorties des outils séparés (EC-01)."""
import json
import unittest

import moteurs  # noqa: F401  (chemins des moteurs)
import etude_complete as ec
import resoudre_dv as rdv
import resoudre_la as rla
import resoudre_ec as rec
import resoudre_ed as red
import ensemble_def as ed
import parties
from noyau import lire
import sortie as so
from aides_sortie import manquantes, valide, blocs_de_type, titres_etude
from cas import entrees_page, CAS_LIMITES

ENTREES = list(dict.fromkeys(entrees_page("etude-complete") + CAS_LIMITES["etude-complete"]))
TECHNIQUE = ("detail", "ok", "genre", "a", "b", "domaine_etude_tex", "ed_deriv_tex", "deriv_detail", "signe_detail", "conclusion")


def affichee(r):
    """La sortie d'`etudier`, études de limites telles qu'elles sont affichées (x → ±∞ regroupés, EC D16)."""
    return dict(r, limites=dict(r["limites"], etudes=rla.etudes_affichees(r["limites"]["etudes"]))) if r.get("ok") else r


def carte(s, titre):
    return next(c for c in s["cartes"] if c["titre"] == titre)


def titres(s):
    return [c["titre"] for c in s["cartes"]]


def lignes_du_bilan(s):
    return carte(s, "Bilan de l'étude")["blocs"][0]["items"]


class TestResoudreEC(unittest.TestCase):
    def test_schema_et_rien_de_perdu(self):
        for entree in ENTREES:
            with self.subTest(entree=entree):
                s = rec.resoudre(entree)
                valide(self, s)
                self.assertEqual(manquantes(affichee(ec.etudier(entree)), s, TECHNIQUE), [])

    def test_ordre_des_cartes_comme_la_page(self):
        for entree in ENTREES:
            ancien = affichee(ec.etudier(entree))
            if not ancien["ok"]:
                continue
            dv, lim = ancien["derivee"], ancien["limites"]
            p = rec.PARTIES
            attendu = [p[0], "Fonction"] + (["Mise en forme"] if parties.mise_en_forme(lire(entree)) else [])
            attendu += [f"Condition {c['num']}" for c in ed.analyser(entree)["conditions"]] + ["Ensemble de définition", p[1]]
            attendu += [c["titre"] for c in parties.cartes_parite(ec.analyse(entree))] + [p[2]]
            attendu += [c["titre"] for c in parties.cartes_zeros_signe(ec.analyse(entree))] + [p[3]]
            if lim.get("tableaux_signe"):
                attendu.append("Tableaux de signes")
            attendu += [t for e in lim["etudes"] for t in titres_etude(e)] + ["Bilan des asymptotes", p[4], "Dérivée"]
            if dv["deriv_resolu"]:
                attendu.append("Signe de f' et variations")
            attendu += [p[5], "Bilan de l'étude", "Graphique"]                 # D20 : le bilan, avant le graphique
            with self.subTest(entree=entree):
                s = rec.resoudre(entree)
                self.assertEqual(titres(s), attendu)
                self.assertEqual([c for c in s["cartes"] if c["style"] == "partie"], [so.partie(t) for t in p])

    def test_partie_5_jamais_vide(self):
        """Question 7 : dérivée hors du cadre, la carte « Dérivée » de l'outil Dérivée et sa phrase ; signe de f′ non étudié, la carte
        d'erreur de l'outil Dérivée (un résultat non traité donne un message clair). Jamais d'intertitre seul."""
        from unittest import mock
        import derivee_variations as dv
        from noyau import NonPrisEnCharge

        def sous(s, titre):
            t = titres(s)
            return s["cartes"][t.index(titre) + 1:t.index(rec.PARTIES[rec.PARTIES.index(titre) + 1])]
        with mock.patch.object(dv, "derivee_narree", side_effect=NonPrisEnCharge("forcé")):
            s = rec.resoudre("x^2-4x+3")
            d = rdv.resoudre("x^2-4x+3")
        valide(self, s)
        self.assertEqual(sous(s, rec.PARTIES[4]), [d["cartes"][1]])
        self.assertEqual(d["cartes"][1]["blocs"], [so.erreur("Cette fonction sort du cadre de l'outil : la dérivée n'a pas été calculée.")])
        self.assertEqual(blocs_de_type(s, "graphique")[0]["extrema"], [])
        self.assertFalse([l for l in lignes_du_bilan(s) if l.endswith("(partie 5)")])    # D20 : partie 5 non conclue, pas de ligne
        with mock.patch.object(dv, "preimage", side_effect=RuntimeError("forcé")):
            s = rec.resoudre("x^2-4x+3")
            d = rdv.resoudre("x^2-4x+3")
        valide(self, s)
        self.assertEqual([c["titre"] for c in sous(s, rec.PARTIES[4])], ["Dérivée", "Signe de f' et variations"])
        self.assertEqual(sous(s, rec.PARTIES[4])[1], d["cartes"][2])
        self.assertEqual(d["cartes"][2]["style"], "erreur")
        self.assertFalse([l for l in lignes_du_bilan(s) if l.endswith("(partie 5)")])

    def test_bilan_avec_la_liste_de_l_outil_derivee(self):
        """D20 : sans rédaction D11 (repli), les lignes du bilan pour la partie 5 sont celles de la liste de l'outil Dérivée, telles que
        la carte « Signe de f′ et variations » les affiche."""
        from unittest import mock
        with mock.patch.object(parties, "partie5", return_value=None):
            s = rec.resoudre("x^2-4x+3")
        valide(self, s)
        liste = [i for b in carte(s, "Signe de f' et variations")["blocs"] if b["type"] == "liste" for i in b["items"]]
        self.assertEqual(liste, [r"minimum local en \(x=2\) : \(f(2)=-1\)"])
        self.assertEqual([l for l in lignes_du_bilan(s) if l.endswith("(partie 5)")], [liste[0] + " (partie 5)"])

    def test_six_parties_dans_l_ordre_du_corrige(self):
        """D1 : les six intertitres, mots et ordre du corrigé .tex."""
        self.assertEqual(rec.PARTIES, ("1. Domaine de définition", "2. Parité", "3. Zéros, signe, ordonnée à l'origine",
                                       "4. Limites et asymptotes", "5. Dérivée, tableau de variation, extremums", "6. Graphe"))

    def test_cartes_identiques_aux_outils_separes(self):
        """EC-01 : dérivée et limites sont les mêmes cartes que dans les outils séparés
        (le tableau de variations ajoute les limites, le rappel ne renvoie pas à l'ED)."""
        for entree in ENTREES:
            if not ec.etudier(entree)["ok"]:
                continue
            with self.subTest(entree=entree):
                s, d, l = rec.resoudre(entree), rdv.resoudre(entree), rla.resoudre(entree)
                self.assertEqual(carte(s, "Dérivée"), d["cartes"][1])
                self.assertEqual([c for c in s["cartes"] if c["titre"] == "Limite"],
                                 [c for c in l["cartes"] if c["titre"] == "Limite"])

    def test_phrases_propres_a_l_etude_complete(self):
        s = rec.resoudre("x^3")
        self.assertEqual(carte(s, "Signe de f' et variations")["blocs"][-1]["html"], "Aucun extremum local.")
        s = rec.resoudre("ln(x)/x")
        self.assertEqual(carte(s, "Fonction")["blocs"], [so.formule("f(x) = \\frac{\\ln(x)}{x}")])     # P3 : l'ED est établi plus bas
        self.assertEqual(carte(s, "Ensemble de définition")["blocs"],
                         [so.resultat("ED = \\left]0 \\,;\\, +\\infty\\right[ = \\left]0 \\,;\\, +\\infty\\right[")])
        self.assertEqual(carte(s, "Bilan des asymptotes")["style"], "normal")

    def test_ed_identique_a_l_outil_ed(self):
        """EC-01 (P3) : partie 1, l'ED encadré est la conclusion de l'outil ED ; une carte par condition, avec le titre et le badge de
        l'outil ED, et ses blocs tels quels quand la chaîne courte (D3) ne s'applique pas."""
        for entree in ENTREES:
            if not ec.etudier(entree)["ok"]:
                continue
            with self.subTest(entree=entree):
                s, r = rec.resoudre(entree), ed.analyser(entree)
                fin = carte(s, "Ensemble de définition")["blocs"]
                self.assertEqual(fin[len(fin) - len(red.blocs_ensemble(r)):], red.blocs_ensemble(r))
                self.assertEqual(blocs_de_type({"cartes": [carte(s, "Ensemble de définition")]}, "resultat"),
                                 [b for b in red.blocs_ensemble(r) if b["type"] == "resultat"])
                for c in r["conditions"]:
                    ce = carte(s, f"Condition {c['num']}")
                    self.assertEqual((ce["badge"], ce.get("detail")), (c["titre"], c.get("detail")))
                    if not any("On résout" in b.get("html", "") for b in ce["blocs"]) and c["cond_tex"] != "x \\neq 0":
                        self.assertEqual(ce["blocs"], red.blocs_condition(c))

    def test_graphique(self):
        s = rec.resoudre("ln(x)/x")
        g = blocs_de_type(s, "graphique")[0]
        ancien = ec.etudier("ln(x)/x")
        self.assertEqual((g["xmin"], g["xmax"]), (ancien["graphique"]["xmin"], ancien["graphique"]["xmax"]))
        self.assertEqual(g["segments"], ancien["graphique"]["segments"])
        self.assertEqual(g["extrema"], ancien["derivee"]["extrema"])
        self.assertEqual(g["asymptotes"], ancien["limites"]["asymptotes"])
        self.assertTrue(g["recalculable"])
        # D15 (P8) : points marqués (zéro x = 1 de ln(x)/x) et ronds vides, ceux d'etudier()
        self.assertEqual((g["points"], g["ronds_vides"]), (ancien["graphique"]["points"], ancien["graphique"]["ronds_vides"]))
        self.assertEqual(g["points"], [{"x_val": 1.0, "f_val": 0.0}])
        s = rec.resoudre("e^((x^2+x-2)/(6x-12))")
        self.assertEqual(blocs_de_type(s, "graphique")[0]["ronds_vides"], [[2.0, 0.0]])
        self.assertIn("ronds vides", blocs_de_type(s, "texte")[-1]["html"])

    def test_limites_dans_le_tableau_de_variations(self):
        s = rec.resoudre("e^(1/x)")
        tab = [b for b in carte(s, "Signe de f' et variations")["blocs"] if b["type"] == "tableau"][-1]
        self.assertEqual(tab["limites"], ec.etudier("e^(1/x)")["variations_limites"])

    def test_erreurs_en_francais(self):
        for entree in ("", "ln(", "x+*2"):
            with self.subTest(entree=entree):
                s = rec.resoudre(entree)
                valide(self, s)
                self.assertFalse(s["ok"])
                self.assertNotIn("Traceback", json.dumps(s))

    def test_json(self):
        self.assertEqual(json.loads(rec.resoudre_json("x^2")), rec.resoudre("x^2"))


if __name__ == "__main__":
    unittest.main()
