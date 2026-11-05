"""T12 — moteur/sortie.py : le validateur du format de sortie commun accepte les sorties
conformes et refuse les écarts (type inconnu, clé inconnue, case hors vocabulaire, ligne de
mauvaise longueur, trace Python dans un message d'erreur)."""
import copy
import unittest

import moteurs  # noqa: F401  (chemins des moteurs)
import sortie as so


def tableau(cells=("+", "0", "-")):
    return {"type": "tableau", "var": "x", "crit": ["1"],
            "rows": [{"label": "x - 1", "cells": list(cells), "final": True}]}


def exemple():
    return so.sortie_ok("f(x) = x", [
        so.carte("Condition 1", [
            so.texte("On résout \\(x > 0\\)."),
            so.formule("x > 0"),
            tableau(),
            so.liste(["a", "b"], style="bilan"),
            so.resultat("E_1 = \\mathbb{R}"),
        ], badge="logarithme"),
        so.carte("Fin", [so.erreur("Condition non résolue.")], style="erreur"),
    ], entete=so.carte("Rappel", [so.formule("f(x) = x")]), besoin_sympy=False)


class TestValidateur(unittest.TestCase):
    def test_sortie_conforme(self):
        self.assertEqual(so.valider(exemple()), [])

    def test_sortie_erreur_conforme(self):
        self.assertEqual(so.valider(so.sortie_erreur("Entrez une expression.")), [])
        self.assertEqual(so.valider(so.sortie_erreur("Oups.", detail="KeyError: 'x'")), [])

    def test_erreur_sans_message_ou_avec_trace(self):
        self.assertTrue(so.valider({"ok": False}))
        self.assertTrue(so.valider(so.sortie_erreur("")))
        self.assertTrue(so.valider(so.sortie_erreur("Traceback (most recent call last):")))

    def test_ok_avec_erreur(self):
        s = exemple()
        s["erreur"] = "x"
        self.assertTrue(so.valider(s))

    def _refuse(self, modifier, fragment):
        s = copy.deepcopy(exemple())
        modifier(s)
        ecarts = so.valider(s)
        self.assertTrue(any(fragment in e for e in ecarts), ecarts)

    def test_type_de_bloc_inconnu(self):
        self._refuse(lambda s: s["cartes"][0]["blocs"].append({"type": "video"}), "type de bloc inconnu")

    def test_cle_inconnue(self):
        self._refuse(lambda s: s["cartes"][0]["blocs"][0].update(couleur="rouge"), "clé « couleur » inconnue")
        self._refuse(lambda s: s["cartes"][0].update(autre=1), "clé « autre » inconnue")
        self._refuse(lambda s: s.update(autre=1), "clé « autre » inconnue")

    def test_cle_manquante(self):
        self._refuse(lambda s: s["cartes"][0]["blocs"][1].pop("tex"), "clé « tex » manquante")

    def test_style_inconnu(self):
        self._refuse(lambda s: s["cartes"][0].update(style="rose"), "style « rose » inconnu")
        self._refuse(lambda s: s["cartes"][0]["blocs"][3].update(style="x"), "style « x » inconnu")

    def test_intertitre_de_partie(self):
        """Style « partie » (Étude complète, D1) : un titre seul, sans bloc ni autre clé."""
        self.assertEqual(so.partie("2. Parité"), {"titre": "2. Parité", "style": "partie", "blocs": []})
        self.assertEqual(so.valider(so.sortie_ok("f", [so.partie("1. Domaine"), so.carte("t", [so.texte("a")])])), [])
        self._refuse(lambda s: s["cartes"].insert(0, so.carte("1. Domaine", [so.texte("a")], style="partie")), "intertitre")
        self._refuse(lambda s: s["cartes"].insert(0, dict(so.partie("1. Domaine"), badge="b")), "intertitre")

    def test_case_hors_vocabulaire(self):
        self._refuse(lambda s: s["cartes"][0]["blocs"][2]["rows"][0]["cells"].__setitem__(1, "?"), "hors vocabulaire")

    def test_cases_du_vocabulaire(self):
        for c in ("+", "-", "0", "|", "||", "x", "asym", "extremum", "", "\\nearrow", "val:\\frac{1}{2}"):
            b = tableau((c, "0", "-"))
            self.assertEqual(so.valider(so.sortie_ok("f", [so.carte("t", [b])])), [], c)

    def test_ligne_de_mauvaise_longueur(self):
        self._refuse(lambda s: s["cartes"][0]["blocs"][2]["rows"][0].update(cells=["+", "-"]), "2 cases, 3 attendues")

    def test_texte_vide(self):
        self._refuse(lambda s: s["cartes"][0]["blocs"][0].update(html=""), "html vide")

    def test_detail_technique_sur_la_carte(self):
        s = exemple()
        s["cartes"][0]["detail"] = "ValueError : boum"
        self.assertEqual(so.valider(s), [])
        self.assertEqual(so.carte("t", [], detail="d")["detail"], "d")

    def test_titre_masque(self):
        c = so.carte("Fonction", [so.formule("f")], titre_masque=True)
        self.assertIs(c["titre_masque"], True)
        self.assertNotIn("titre_masque", so.carte("t", []))
        self.assertEqual(so.valider(so.sortie_ok("f", [c])), [])
        c["titre_masque"] = "oui"
        self.assertTrue(so.valider(so.sortie_ok("f", [c])))

    def test_tableau_uv(self):
        """Bloc « uv » (décisions EC, D8) : quatre formules non vides ; aussi dans la sous-carte d'un sous_calcul (dérivée de l'exposant).
        Le tableau de l'outil Dérivée (derivee_variations.bloc_uv) est exactement ce bloc."""
        import derivee_variations as dv
        from moteurs import ensemble_def as ed
        b = so.uv("u = x^{2} - 6", "u' = 2x", "v = e^{-2x}", "v' = -2e^{-2x}")
        self.assertEqual(b, {"type": "uv", "u": "u = x^{2} - 6", "du": "u' = 2x", "v": "v = e^{-2x}", "dv": "v' = -2e^{-2x}"})
        self.assertEqual(dv.bloc_uv(ed.lire("x^2-6"), ed.lire("2x"), ed.lire("e^(-2x)"), ed.lire("-2e^(-2x)")), b)
        self.assertEqual(so.valider(so.sortie_ok("f", [so.carte("Dérivée", [b])])), [])
        sous = so.sous_calcul("Dérivée de l'exposant", [{"titre": "règle du quotient", "blocs": [b]}])
        self.assertEqual(so.valider(so.sortie_ok("f", [so.carte("Dérivée", [sous])])), [])
        for cle in ("u", "du", "v", "dv"):
            with self.subTest(cle=cle):
                self.assertTrue(so.valider(so.sortie_ok("f", [so.carte("Dérivée", [dict(b, **{cle: ""})])])))
                sans = {k: v for k, v in b.items() if k != cle}
                self.assertTrue(so.valider(so.sortie_ok("f", [so.carte("Dérivée", [sans])])))
                mauvais = so.sous_calcul("t", [{"titre": "e", "blocs": [dict(b, **{cle: ""})]}])
                self.assertTrue(so.valider(so.sortie_ok("f", [so.carte("Dérivée", [mauvais])])))

    def test_limites_du_tableau(self):
        s = exemple()
        s["cartes"][0]["blocs"][2]["limites"] = {"colonnes": [], "moins_inf": "1", "plus_inf": "1", "non_determinees": []}
        self.assertEqual(so.valider(s), [])
        s["cartes"][0]["blocs"][2]["limites"]["x"] = 1
        self.assertTrue(so.valider(s))


def chaine_bloc():
    """Bloc « chaine » (B3) : membre de gauche, étiquettes, une ligne de texte et un tableau pleine largeur au milieu, d'autres ⇔ après."""
    return so.chaine([
        so.rangee("\\iff", "6(x^{2} - 1) = 0", prop="ME", gauche="6x^{2} - 6 = 0"),
        so.rangee_texte("Id. rem. \\(A^{2} - B^{2}\\) avec \\(A = x\\), \\(B = 1\\) ; \\(x < y\\) n'est pas du HTML"),
        so.rangee_bloc(tableau()),
        so.rangee("\\iff", "6(x + 1)(x - 1) = 0"),
        so.rangee_bloc(so.texte("Le <strong>produit</strong> est nul :")),
        so.rangee("\\iff", "\\underbrace{6 = 0}_{\\text{impossible}} \\text{ ou } x + 1 = 0", prop="produit nul"),
        so.rangee("\\Rightarrow", "x = -1"),
        so.rangee("", "\\phantom{x} = 1", prop="(on calcule)"),
    ])


class TestBlocChaine(unittest.TestCase):
    """Bloc « chaine » (chantier briques-communes, B3 ; A4) : constructeurs et schéma. Rendu : tests/pages/test_bloc_chaine.py ; depuis
    une chaîne de moteur/chaine.py : test_chaine.TestBlocChaine."""

    def sortie(self, b):
        return so.sortie_ok("x", [so.carte("t", [b])])

    def _refuse(self, modifier, fragment):
        b = copy.deepcopy(chaine_bloc())
        modifier(b)
        ecarts = so.valider(self.sortie(b))
        self.assertTrue(any(fragment in e for e in ecarts), ecarts)

    def test_constructeurs(self):
        self.assertEqual(so.rangee("\\iff", "x = 1"), {"lien": "\\iff", "expr": "x = 1"})
        self.assertEqual(so.rangee("\\iff", "x = 1", prop="ME", gauche="2x = 2"),
                         {"lien": "\\iff", "expr": "x = 1", "prop": "ME", "gauche": "2x = 2"})
        self.assertEqual(so.rangee_texte("a"), {"texte": "a"})
        self.assertEqual(so.rangee_bloc(so.formule("x")), {"bloc": {"type": "formule", "tex": "x"}})
        self.assertEqual(so.chaine((so.rangee("", "x"),)), {"type": "chaine", "rangees": [{"lien": "", "expr": "x"}]})
        self.assertEqual(so.BLOCS["chaine"], ({"rangees"}, set()))
        self.assertEqual(so.BLOCS_DANS_CHAINE, ("texte", "formule", "tableau"))

    def test_conforme(self):
        self.assertEqual(so.valider(self.sortie(chaine_bloc())), [])
        for genre in so.BLOCS_DANS_CHAINE:
            bloc = {"texte": so.texte("a"), "formule": so.formule("x"), "tableau": tableau()}[genre]
            with self.subTest(genre=genre):
                self.assertEqual(so.valider(self.sortie(so.chaine([so.rangee("", "x"), so.rangee_bloc(bloc)]))), [])
        sous = so.sous_calcul("Dérivée", [{"titre": "u", "blocs": [chaine_bloc()]}])           # aussi dans un sous-calcul
        self.assertEqual(so.valider(self.sortie(sous)), [])

    def test_html_interdit(self):
        for cle in ("expr", "prop", "gauche"):
            with self.subTest(cle=cle):
                self._refuse(lambda b, cle=cle: b["rangees"][0].update({cle: '<span class="x">a</span>'}), "HTML interdit")
        self._refuse(lambda b: b["rangees"][1].update(texte="a <b>gras</b>"), "HTML interdit")
        self._refuse(lambda b: b["rangees"][1].update(texte="a &amp; b"), "HTML interdit")
        self._refuse(lambda b: b["rangees"][1].update(texte="a &#60; b"), "HTML interdit")
        self._refuse(lambda b: b["rangees"][3].update(expr="x</div>"), "HTML interdit")

    def test_bloc_imbrique(self):
        for interdit in ({"type": "video"}, so.chaine([so.rangee("", "x")]), so.resultat("x"), so.liste(["a"]), "texte", None):
            with self.subTest(bloc=interdit):
                self._refuse(lambda b, i=interdit: b["rangees"].__setitem__(2, {"bloc": i}), "non permis dans une chaîne")
        self._refuse(lambda b: b["rangees"][2]["bloc"]["rows"][0]["cells"].__setitem__(1, "?"), "hors vocabulaire")     # validé récursivement
        self._refuse(lambda b: b["rangees"][4]["bloc"].update(html=""), "html vide")

    def test_rangee_mal_formee(self):
        self._refuse(lambda b: b["rangees"].append({}), "rangée mal formée")
        self._refuse(lambda b: b["rangees"].append("x = 1"), "rangée mal formée")
        self._refuse(lambda b: b["rangees"].append(["\\iff", "x = 1", None]), "rangée mal formée")
        self._refuse(lambda b: b["rangees"].append({"texte": "a", "bloc": so.formule("x")}), "rangée mal formée")
        self._refuse(lambda b: b["rangees"].append({"texte": "a", "expr": "x"}), "clé « texte » inconnue")
        self._refuse(lambda b: b["rangees"].append({"lien": "\\iff"}), "clé « expr » manquante")
        self._refuse(lambda b: b["rangees"].append({"expr": "x"}), "clé « lien » manquante")
        self._refuse(lambda b: b["rangees"][3].update(couleur="gris"), "clé « couleur » inconnue")
        self._refuse(lambda b: b["rangees"][3].update(lien="⇔"), "lien « ⇔ » inconnu")
        self._refuse(lambda b: b["rangees"][3].update(lien="="), "lien « = » inconnu")
        self._refuse(lambda b: b["rangees"][3].update(expr=""), "texte non vide attendu")
        self._refuse(lambda b: b["rangees"][3].update(prop=""), "texte non vide attendu")
        self._refuse(lambda b: b["rangees"][3].update(prop=None), "texte non vide attendu")
        self._refuse(lambda b: b["rangees"][1].update(texte=""), "texte non vide attendu")
        self._refuse(lambda b: b.update(couleur=1), "clé « couleur » inconnue")

    def test_gauche_seulement_sur_la_premiere_ligne_avec_un_lien(self):
        self._refuse(lambda b: b["rangees"][3].update(gauche="x"), "gauche seulement sur la première ligne")
        self._refuse(lambda b: b["rangees"][0].update(lien=""), "gauche seulement sur la première ligne")
        b = so.chaine([so.rangee_texte("a"), so.rangee("\\iff", "x = 1", gauche="2x = 2")])           # après une ligne pleine : permis
        self.assertEqual(so.valider(self.sortie(b)), [])

    def test_liste_de_rangees(self):
        self._refuse(lambda b: b.update(rangees=[]), "liste non vide")
        self._refuse(lambda b: b.update(rangees="x"), "liste non vide")
        self._refuse(lambda b: b.update(rangees=[so.rangee_texte("a")]), "au moins une ligne")
        self._refuse(lambda b: b.pop("rangees"), "clé « rangees » manquante")


def avec_variantes():
    a = [so.carte("Étape 1", [so.texte("a")], badge="Méthode A"), so.carte("Solution", [so.resultat("S = \\{1\\}")], style="final")]
    b = [so.carte("Étape 1", [so.texte("b")], badge="Méthode B"), so.carte("Solution", [so.resultat("S = \\{1\\}")], style="final")]
    return so.sortie_ok_variantes("x = 1", [so.variante("a", "Méthode A", a), so.variante("b", "Méthode B", b)], "b")


class TestVariantes(unittest.TestCase):
    """SOC-17 : plusieurs résolutions d'une même entrée (facultatif, premier usage : Exponentielles et logarithmes)."""

    def test_sortie_conforme(self):
        s = avec_variantes()
        self.assertEqual(so.valider(s), [])
        self.assertEqual(s["variante_defaut"], "b")
        self.assertEqual(s["cartes"], s["variantes"][1]["cartes"])
        self.assertEqual([v["cle"] for v in s["variantes"]], ["a", "b"])

    def _refuse(self, modifier, fragment):
        s = copy.deepcopy(avec_variantes())
        modifier(s)
        ecarts = so.valider(s)
        self.assertTrue(any(fragment in e for e in ecarts), ecarts)

    def test_cle_manquante(self):
        self._refuse(lambda s: s["variantes"][0].pop("libelle"), "clé « libelle » manquante")
        self._refuse(lambda s: s["variantes"][0].pop("cartes"), "clé « cartes » manquante")
        self._refuse(lambda s: s["variantes"][0].update(autre=1), "clé « autre » inconnue")

    def test_cles_identiques(self):
        self._refuse(lambda s: s["variantes"][0].update(cle="b"), "même clé")

    def test_defaut_inconnu_ou_absent(self):
        self._refuse(lambda s: s.update(variante_defaut="z"), "variante_defaut « z » inconnue")
        self._refuse(lambda s: s.pop("variante_defaut"), "vont ensemble")
        self._refuse(lambda s: s.pop("variantes"), "vont ensemble")

    def test_cartes_differentes_de_celles_du_defaut(self):
        self._refuse(lambda s: s.update(cartes=s["variantes"][0]["cartes"]), "variante par défaut")

    def test_carte_invalide_dans_une_variante(self):
        self._refuse(lambda s: s["variantes"][0]["cartes"][0].update(style="rose"), "style « rose » inconnu")

    def test_liste_vide(self):
        self._refuse(lambda s: s.update(variantes=[]), "liste non vide")

    def test_sortie_sans_variantes_inchangee(self):
        s = exemple()
        self.assertNotIn("variantes", s)
        self.assertNotIn("variante_defaut", s)


def avec_option(cochee=False):
    a = [so.carte("Étape 1", [so.texte("a")], badge="Méthode A"), so.carte("Solution", [so.resultat("S = \\{1\\}")], style="final")]
    b = [so.carte("Étape 1", [so.texte("b")], badge="Méthode B"), so.carte("Solution", [so.resultat("S = \\{1\\}")], style="final")]
    plus = so.carte("Interprétation", [so.resultat("\\text{Au bout de 1 an.}")], style="final")
    return so.sortie_ok_variantes("x = 1", [so.variante("a", "Méthode A", a, option=False), so.variante("b", "Méthode B", b)], "b",
                                  option=so.option("interpretation", "Problème d'application", [plus], cochee))


class TestOption(unittest.TestCase):
    """SOC-18 : une case à cocher dont les cartes s'ajoutent aux cartes affichées (facultatif, premier usage : Exponentielles et logarithmes)."""

    def _refuse(self, modifier, fragment):
        s = copy.deepcopy(avec_option())
        modifier(s)
        ecarts = so.valider(s)
        self.assertTrue(any(fragment in e for e in ecarts), ecarts)

    def test_sortie_conforme(self):
        for cochee in (False, True):
            s = avec_option(cochee)
            self.assertEqual(so.valider(s), [])
            self.assertIs(s["option"]["cochee"], cochee)
            self.assertEqual(s["variantes"][0]["option"], False)
            self.assertNotIn("option", s["variantes"][1])

    def test_sans_variantes(self):
        c = [so.carte("Solution", [so.resultat("S = \\{1\\}")], style="final")]
        s = so.sortie_ok("x = 1", c, option=so.option("interpretation", "Problème d'application", c, True))
        self.assertEqual(so.valider(s), [])

    def test_cle_manquante_ou_inconnue(self):
        for cle in ("cle", "libelle", "cochee", "cartes"):
            self._refuse(lambda s, cle=cle: s["option"].pop(cle), f"clé « {cle} » manquante")
        self._refuse(lambda s: s["option"].update(autre=1), "clé « autre » inconnue")

    def test_cochee_est_un_booleen(self):
        self._refuse(lambda s: s["option"].update(cochee="oui"), "cochee doit être un booléen")
        self._refuse(lambda s: s["option"].update(cochee=1), "cochee doit être un booléen")

    def test_textes_non_vides(self):
        self._refuse(lambda s: s["option"].update(cle=""), "cle et libelle")
        self._refuse(lambda s: s["option"].update(libelle=""), "cle et libelle")

    def test_cartes_valides_et_non_vides(self):
        self._refuse(lambda s: s["option"].update(cartes=[]), "liste non vide")
        self._refuse(lambda s: s["option"]["cartes"][0].update(style="rose"), "style « rose » inconnu")

    def test_option_d_une_variante(self):
        self._refuse(lambda s: s["variantes"][0].update(option=True), "option doit être false")
        self._refuse(lambda s: s.pop("option"), "sans que la sortie en ait une")

    def test_sortie_sans_option_inchangee(self):
        for s in (exemple(), avec_variantes()):
            self.assertNotIn("option", s)
            self.assertTrue(all("option" not in v for v in s.get("variantes", [])))


if __name__ == "__main__":
    unittest.main()
