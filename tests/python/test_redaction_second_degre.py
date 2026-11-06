"""Brique moteur/second_degre.py, P2b à P4b du chantier equations-2e-degre : la rédaction (decisions.md §§ 3, 4, 5, 6, 7 et 13 ;
plan, P2b, P3, P4a et P4b).

- Invariants du § 5 : le bloc affiché est `bloc_rangees(concaténation des lignes de toutes les étapes, membre_gauche=True)` (JSON) ;
  les segments des étapes, mis bout à bout, donnent les rangées de la chaîne entière (`rangees_chaine`) ; chaque segment commence
  par le pivot (le dernier élément écrit) et n'a que des ⇔ ; l'énoncé n'est écrit qu'une fois, et seulement si un ⇔ suit (§ 13.3).
  R1 (une carte par étape, question 36 de suivi.md) : les cartes de `cartes`, mises bout à bout, redonnent la chaîne entière (JSON,
  membre de gauche mis à part) ; chaque carte à rangée-ligne est un bloc « chaine » valide, son membre de gauche est le pivot.
- Oracle (`oracle.racines`) sur toutes les solutions du corpus (`corpus_second_degre.RESOLUES`), des variantes « formule » (E12) et des
  polynômes générés de P1 ; chaque solution est substituée exactement dans l'équation (calcul écrit ici).
- Rédaction : le texte rendu de 2.11 h, 2.10 a, Javet 2.17 c et des exemples du § 7 ; E3 à E12, E14 ; D20, D24, D29 ; cas limites
  du § 6 ; vouvoiement (R12) et vocabulaire (C6) de tout texte produit.
- `nb_exact` sans état, croisé avec `exp_log._nb_exact` ; `appliquer` : s_applique ⇔ une étape, qui se redéveloppe.
- P3 : E1 (ramener, réordonner, côté droit, phrase seulement avant une phrase de choix) et E2 (développer en montrant les produits,
  « − (…) » puis sans parenthèses).
- P4a : les formes structurées, sans développer (E1.3) : produit déjà nul (E13), facteur commun aux deux membres (E3), Id. rem. sur la
  forme structurée (E5) ; textes rendus de 2.9 k, 2.9 l, 2.12 e, 2.12 h et Az 4.1 d comparés au corrigé ; chaque ligne relue ; une
  structure que l'outil n'écrit pas reçoit « hors du cours ».
- P4b : degrés ≠ 2 (E13 : ME de xᵏ, Id. rem. de A = x², x⁴ − 16 avec D28 et E9), degré 1 (isoler, D20), identité et égalité fausse
  (phrases d'Exp-log), formes structurées laissées à P4b ; messages définitifs (bicarrée, hors du cours) : aucun statut temporaire.
- Les formes d'`A_VENIR` (toutes les parties sont faites : aucun xfail) et chaque exercice du § 8 (instantané et oracle)."""
import json
import re
import unicodedata
import unittest
from fractions import Fraction as F

import pytest
from mpmath import mp

import moteurs  # noqa: F401  (chemins des moteurs)

import exp_log
import expr
import nombres
import oracle
import second_degre as sd
import sortie
from chaine import Chaine, Eq, LigneTexte, bloc_rangees, tex_element
from aides_sortie import TUTOIEMENT
from corpus_second_degre import (A_VENIR, MESSAGE_BICARREE, NON_RESOLUES, P2B, P3, P4A, P4B, PARTIES_FAITES, RESOLUES, SECTION_8,
                                 STRUCTURES_NON_ECRITES)
from expr import Nb
from second_degre import Nombre
from test_second_degre import GENERES, OracleMixin, egal_au_polynome, valeur_mp
from test_vocabulaire import INTERDITS, chaines

PHASES = {"ramener", "factoriser", "produit_nul", "delta_valeur", "delta_nombre", "isoler"}
METHODES_ETAPE = {"RAMENER", "DEVELOPPER", "ISOLER", "ME", "ME_PUISSANCE", "IDREM_DIFF", "IDREM_PLUS", "IDREM_MOINS", "SP",
                  "TATONNEMENT", "FORMULE", "PRODUIT_NUL"}


def a_des_decimaux(n):
    if isinstance(n, Nb):
        return n.dec is not None
    return any(a_des_decimaux(getattr(n, s)) for s in getattr(n, "__slots__", ()) if isinstance(getattr(n, s), expr.Noeud))


def lire(saisie):
    g, d = expr.lire_membres(saisie)
    lettres = sorted(expr.variables(g) | expr.variables(d))
    return g, d, (lettres[0] if lettres else "x"), a_des_decimaux(g) or a_des_decimaux(d)


def resoudre(saisie, methodes=sd.ORDRE_DU_COURS):
    g, d, x, dec = lire(saisie)
    return sd.resoudre_equation(g, d, x, dec, methodes)


def polynome(saisie):
    """Le polynôme P de « P = 0 », l'équation ramenée : gauche − droite."""
    g, d, x, _ = lire(saisie)
    return sd.vers_polynome(expr.Op("-", g, d), x)


def lignes(res):
    return [r for e in res["etapes"] for r in e["lignes"]]


def textes(res):
    """Les lignes rendues, en texte : « lien | expr | prop » ou le texte pleine largeur (un tableau : « [tableau] »)."""
    out = []
    for r in lignes(res):
        if isinstance(r, LigneTexte):
            out.append("[tableau]" if isinstance(r.contenu, dict) else r.contenu)
        else:
            out.append(" | ".join(x or "" for x in r))
    return out


def toutes():
    """(nom, résolution) du corpus et de ses variantes « formule »."""
    for nom, saisie in RESOLUES.items():
        res = resoudre(saisie)
        yield nom, res
        if res["variantes"]:
            yield nom + " (variante formule)", resoudre(saisie, sd.ORDRE_PAR_LA_FORMULE)


TOUTES = list(toutes())
ENONCES = {nom: tex_element(sd.ecrire_enonce(*lire(RESOLUES[nom.replace(" (variante formule)", "")])[:3]), True, True)
           for nom, _ in TOUTES}
GENERES_2 = [P for P in GENERES if P.degre == 2]


def generees():
    """(nom, P, résolution) des polynômes générés de P1, de degré 2, écrits développés (décimaux de l'énoncé pour une partie)."""
    for i, P in enumerate(GENERES_2):
        dec = i % 3 == 0
        g = sd.arbre_polynome(P, "x", dec)
        ENONCES[f"généré {i}"] = expr.tex(g) + " = 0"
        yield f"généré {i}", P, sd.resoudre_equation(g, Nb(0), "x", dec)


GENEREES = list(generees())


def evaluer(P, x):
    """P(x) exactement, dans Q(√m), avec des couples (a, b) = a + b√m (calcul écrit ici, indépendant de la brique)."""
    m = x.m
    a, b = F(0), F(0)
    for c in reversed(list(P)):
        a, b = a * x.p + b * x.q * m + c, a * x.q + b * x.p
    return a, b


# ---------------------------------------------------------------------------------------------------------------------------
# Invariants du § 5
# ---------------------------------------------------------------------------------------------------------------------------
def contenu(r):
    return r.contenu if isinstance(r, LigneTexte) else sd.SansLien(r[1])


def replier(res):
    """Les segments de toutes les étapes mis bout à bout en une seule chaîne (pivots enchaînés), ses rangées encadrées des lignes
    écrites avant le premier ⇔ et après le dernier."""
    entiere, avant, attente, premier = None, [], [], True
    for e in res["etapes"]:
        seg = e["segment"]
        if seg is None:
            attente += e["lignes"]
            continue
        if entiere is None:
            avant, attente = attente, []
            entiere = Chaine([seg.elements[0]])
        else:
            assert seg.elements[0] is entiere.elements[-1], "le pivot d'un segment est le dernier élément écrit"
        for i, (el, lien, prop) in enumerate(zip(seg.elements[1:], seg.liens, seg.props), 1):
            avant_el = ([contenu(r) for r in attente] if i == 1 else []) + list(seg.textes.get(i, []))
            attente = attente if i > 1 else []
            entiere.ajouter(el, lien, prop, texte_avant=avant_el or None)
        n = len(sd.rangees(seg)) - (0 if premier else 1)
        premier = False
        attente += e["lignes"][n:]
    return avant + (sd.rangees(entiere) if entiere else []) + attente


class TestInvariants(unittest.TestCase):

    def tous(self):
        return TOUTES + [(nom, res) for nom, _, res in GENEREES]

    def test_bloc_affiche_est_la_concatenation_des_lignes(self):
        """§ 5 : la page est construite uniquement à partir des étapes ; le bloc « chaine » est celui des lignes mises bout à bout
        (en JSON), S vient de la résolution ; la sortie est conforme au schéma (sortie.valider)."""
        for nom, res in self.tous():
            with self.subTest(nom=nom):
                self.assertEqual(res["statut"], "resolu")
                b = sd.blocs(res)
                attendu = bloc_rangees(lignes(res), membre_gauche=True)
                self.assertEqual(json.dumps(b[0], sort_keys=True, ensure_ascii=False),
                                 json.dumps(attendu, sort_keys=True, ensure_ascii=False))
                self.assertEqual(b[1], sortie.resultat_lim(res["S"]))
                self.assertEqual(b[2:], [sortie.texte(res["approx"])] if res["approx"] else [])
                s = sortie.sortie_ok("x", [sortie.carte("Résolution", b)])
                self.assertEqual(sortie.valider(s), [])
                json.loads(json.dumps(s, allow_nan=False))

    def test_repliement_des_segments(self):
        """Les segments des étapes, mis bout à bout, donnent les rangées de la chaîne entière (rangees_chaine)."""
        for nom, res in self.tous():
            with self.subTest(nom=nom):
                self.assertEqual(replier(res), lignes(res))

    def test_segments_pivot_puis_equivalences(self):
        """Chaque segment : Chaine([pivot, …]), tous ses liens ⇔, le premier pivot est l'énoncé ; l'énoncé écrit une seule fois, en
        tête de la chaîne, et seulement si un ⇔ suit (§ 13.3) ; aucune ligne ne commence par « = »."""
        for nom, res in self.tous():
            with self.subTest(nom=nom):
                enonce = ENONCES[nom]
                segs = [e["segment"] for e in res["etapes"] if e["segment"] is not None]
                for s in segs:
                    self.assertTrue(s.liens and all(lien == "⇔" for lien in s.liens))
                rangs = [r for r in lignes(res) if not isinstance(r, LigneTexte)]
                ecrit = [r for r in rangs if r == ("", enonce, None)]
                self.assertEqual(len(ecrit), 1 if segs else 0)
                self.assertEqual(bool(segs), any(r[0] for r in rangs))
                if segs:
                    self.assertEqual(rangs[0], ("", enonce, None))
                    self.assertEqual(sd.rangees(segs[0])[0], ("", enonce, None))
                self.assertFalse(any(r[1].lstrip().startswith("=") for r in rangs))

    def test_champs_des_etapes(self):
        for nom, res in self.tous():
            with self.subTest(nom=nom):
                self.assertTrue(res["etapes"])
                for e in res["etapes"]:
                    self.assertEqual(set(e), {"phase", "methode", "cible", "parametres", "lignes", "segment"})
                    self.assertIn(e["phase"], PHASES)
                    self.assertIn(e["methode"], METHODES_ETAPE)
                    self.assertTrue(isinstance(e["cible"], str) and e["cible"])
                    for r in e["lignes"]:
                        self.assertTrue(isinstance(r, LigneTexte) or (isinstance(r, tuple) and len(r) == 3), r)
                self.assertIsNone(res["message"])
                self.assertEqual(res["solutions"], sd.croissant(res["solutions"]))

    def test_une_carte_par_etape(self):
        """R1 (question 36 de suivi.md) : les cartes de la page (`cartes`), mises bout à bout, redonnent la chaîne entière de `blocs`
        (JSON, membre de gauche mis à part) ; chaque carte qui a une rangée-ligne est un seul bloc « chaine » valide, dont le membre de
        gauche, s'il y en a un, est le dernier élément écrit avant elle (l'énoncé pour la première) et n'est écrit qu'une fois ; une
        carte de blocs texte et tableau (sans HTML) seulement pour une étape sans rangée-ligne ; chaque étape a sa carte, dans l'ordre,
        une étape vide rejoint une carte voisine (aucune carte vide) ; S et la ligne ≈ viennent après (`blocs_solution`)."""
        for nom, res in self.tous():
            with self.subTest(nom=nom):
                cartes = sd.cartes(res)
                self.assertEqual([i for c in cartes for i in c["etapes"]], list(range(len(res["etapes"]))))
                concat, dernier = [], ENONCES[nom]
                for c in cartes:
                    etapes = [res["etapes"][i] for i in c["etapes"]]
                    self.assertEqual(len([e for e in etapes if e["lignes"]]), 1)
                    rangs = [r for e in etapes for r in e["lignes"] if not isinstance(r, LigneTexte)]
                    s = sortie.sortie_ok("x", [sortie.carte("Étape 1", c["blocs"], badge="badge")])
                    self.assertEqual(sortie.valider(s), [])
                    if rangs:
                        self.assertEqual([b["type"] for b in c["blocs"]], ["chaine"])
                        rangees = c["blocs"][0]["rangees"]
                        lignes_ = [r for r in rangees if "lien" in r]
                        if "gauche" in lignes_[0]:
                            self.assertEqual(lignes_[0]["gauche"], dernier)
                            self.assertTrue(lignes_[0]["lien"])
                        self.assertEqual(sum("gauche" in r for r in rangees), 1 if "gauche" in lignes_[0] else 0)
                        concat += [{k: v for k, v in r.items() if k != "gauche"} for r in rangees]
                        dernier = next((r["expr"] for r in reversed(lignes_) if r["lien"]), dernier)
                    else:
                        self.assertTrue(c["blocs"])
                        for b in c["blocs"]:
                            self.assertIn(b["type"], ("texte", "tableau_essais"))
                            if b["type"] == "texte":
                                ecarts = []
                                sortie._sans_html(b["html"], "texte", ecarts)
                                self.assertEqual(ecarts, [])
                                self.assertEqual(set(b), {"type", "html"})
                        concat += [{"texte": b["html"]} if b["type"] == "texte" else {"bloc": b} for b in c["blocs"]]
                entiere = [{k: v for k, v in r.items() if k != "gauche"} for r in sd.blocs(res)[0]["rangees"]]
                self.assertEqual(json.dumps(concat, sort_keys=True, ensure_ascii=False),
                                 json.dumps(entiere, sort_keys=True, ensure_ascii=False))
                self.assertEqual(sd.blocs_solution(res), sd.blocs(res)[1:])

    def test_cartes_de_2_11_h(self):
        """R1, exemple cible : cinq cartes (Ramener à 0, Mise en évidence, Tâtonnement, Produit nul, puis Solution), chacune commence
        par l'équation d'arrivée de la précédente en membre de gauche ; la variante « Par la formule » est découpée de même (la formule
        choisie d'emblée, étape vide, rejoint la carte du discriminant)."""
        res = resoudre(RESOLUES["2.11 h"])
        cartes = sd.cartes(res)
        self.assertEqual([[(res["etapes"][i]["phase"], res["etapes"][i]["methode"]) for i in c["etapes"]] for c in cartes],
                         [[("ramener", "RAMENER")], [("factoriser", "ME")], [("factoriser", "TATONNEMENT")],
                          [("produit_nul", "PRODUIT_NUL")]])
        lignes_ = [[(r.get("gauche"), r["lien"], r["expr"]) if "lien" in r else r["texte"] for r in c["blocs"][0]["rangees"]]
                   for c in cartes]
        self.assertEqual(lignes_[0], [("4x^{2} + 2x = 56", r"\iff", "4x^{2} + 2x - 56 = 0")])
        self.assertEqual(lignes_[1], [("4x^{2} + 2x - 56 = 0", r"\iff", "2(2x^{2} + x - 28) = 0")])
        self.assertEqual(lignes_[2][3], ("2(2x^{2} + x - 28) = 0", r"\iff", "2(x + 4)(2x - 7) = 0"))
        self.assertTrue(lignes_[2][0].endswith("n'est pas unitaire : tâtonnement."))
        self.assertEqual([l[0] for l in lignes_[3]], ["2(x + 4)(2x - 7) = 0", None])
        self.assertEqual(lignes_[3][1][2], r"{x = -4} \text{ ou } \allowbreak {x = \frac{7}{2}}")
        self.assertEqual(sd.blocs_solution(res), [sortie.resultat_lim(r"S = \{-4\,;\,\frac{7}{2}\}")])
        formule = resoudre(RESOLUES["2.11 h"], sd.ORDRE_PAR_LA_FORMULE)
        self.assertEqual([[(formule["etapes"][i]["phase"]) for i in c["etapes"]] for c in sd.cartes(formule)],
                         [["ramener"], ["factoriser", "delta_valeur"], ["delta_nombre"]])
        self.assertEqual(formule["etapes"][1]["lignes"], [])

    def test_carte_d_une_etape_sans_rangee(self):
        """R1 : une tentative en échec (S-P de Javet 2.17 c avec son tableau, tâtonnement de 2.12 b), la phrase de choix seule de la
        formule (Javet 2.17 e) et « Δ < 0 : … » sans ⇔ ont chacune leur carte, faite de blocs texte et tableau (une chaîne sans ligne
        {lien, expr} serait refusée) ; la carte suivante ne répète pas l'équation quand elle commence par une ligne de Δ."""
        res = resoudre(RESOLUES["Javet 2.17 c"])
        cartes = sd.cartes(res)
        self.assertEqual([b["type"] for b in cartes[1]["blocs"]], ["texte", "texte", "tableau_essais", "texte"])
        self.assertEqual(cartes[1]["blocs"][-1], sortie.texte("Aucun couple ne convient : on utilise la formule."))
        self.assertEqual([c["blocs"][0]["type"] for c in cartes], ["chaine", "texte", "chaine", "chaine", "chaine"])
        self.assertNotIn("gauche", cartes[3]["blocs"][0]["rangees"][0])
        self.assertNotIn("gauche", cartes[4]["blocs"][0]["rangees"][0])
        res = resoudre(RESOLUES["2.12 b"])
        self.assertEqual([[b["type"] for b in c["blocs"]] for c in sd.cartes(res)], [["texte", "texte"], ["chaine"], ["chaine"]])
        res = resoudre(RESOLUES["Javet 2.17 e"])
        self.assertEqual([[b["type"] for b in c["blocs"]] for c in sd.cartes(res)], [["texte"], ["chaine"], ["chaine"]])
        res = resoudre("3t^2+5t+12=0")
        cartes = sd.cartes(res)
        self.assertEqual(cartes[-1]["blocs"], [sortie.texte(r"\(\Delta < 0\) : l'équation n'a aucune solution réelle.")])
        res = resoudre(RESOLUES["ME de 2x, puis Id. rem. (carré)"], sd.ORDRE_PAR_LA_FORMULE)      # Δ = 0, puis ⇔ x = 0 ou x = 1
        rangees = sd.cartes(res)[-1]["blocs"][0]["rangees"]
        self.assertEqual([r.get("lien") for r in rangees], [None, "", r"\iff"])
        self.assertFalse(any("gauche" in r for r in rangees))      # jamais « x = −b/2a = 1 ⇔ x = 0 ou x = 1 »
        with self.assertRaises(ValueError):
            sd.cartes(resoudre("x^4-5x^2+4=0"))


# ---------------------------------------------------------------------------------------------------------------------------
# Oracle et garde-fou
# ---------------------------------------------------------------------------------------------------------------------------
class TestOracle(OracleMixin, unittest.TestCase):

    def test_corpus_et_variantes(self):
        """Solutions = oracle.racines, et chacune annule exactement l'équation (S, ligne ≈ comprise) ; l'identité et l'égalité fausse
        (P de degré 0, que l'oracle refuse ou n'a pas à résoudre) à part : S = ℝ si et seulement si P est nul, sinon S = ∅ (§ 6)."""
        for nom, res in TOUTES:
            saisie = RESOLUES[nom.replace(" (variante formule)", "")]
            with self.subTest(nom=nom):
                P = polynome(saisie)
                self.assertEqual(res["statut"], "resolu")
                if P.degre == 0:
                    self.assertEqual((res["solutions"], res["S"], res["approx"]),
                                     ([], r"S = \mathbb{R}" if P.nul() else r"S = \varnothing", None))
                    continue
                self.assertSolutionsOracle(P, res["solutions"], nom)
                for x in res["solutions"]:
                    self.assertEqual(evaluer(P, x), (0, 0))

    def test_variante_memes_solutions(self):
        for nom, saisie in RESOLUES.items():
            res = resoudre(saisie)
            if res["variantes"]:
                with self.subTest(nom=nom):
                    self.assertEqual(resoudre(saisie, sd.ORDRE_PAR_LA_FORMULE)["solutions"], res["solutions"])

    def test_polynomes_generes(self):
        for nom, P, res in GENEREES:
            with self.subTest(nom=nom, P=P):
                self.assertEqual(res["statut"], "resolu")
                self.assertSolutionsOracle(P, res["solutions"], nom)
                for x in res["solutions"]:
                    self.assertEqual(evaluer(P, x), (0, 0))

    def test_valeurs_approchees_garanties(self):
        """Chaque « ≈ » de la ligne E14 est la valeur de la solution (mpmath) arrondie à 3 décimales."""
        for nom, res in TOUTES + [(n, r) for n, _, r in GENEREES]:
            if not res["approx"]:
                continue
            with self.subTest(nom=nom):
                ecrites = re.findall(r"\\approx (.*?)\\\)", res["approx"])
                irrationnelles = [x for x in res["solutions"] if not x.rationnel]
                self.assertEqual(len(ecrites), len(irrationnelles))
                for x, t in zip(irrationnelles, ecrites):
                    with mp.workdps(60):
                        v = valeur_mp(x)
                        self.assertEqual(t, nombres.approx(F(str(mp.nstr(v, 50, strip_zeros=False)))))


# ---------------------------------------------------------------------------------------------------------------------------
# Rédaction : textes rendus
# ---------------------------------------------------------------------------------------------------------------------------
IMP = r"\underbrace{%s = 0}_{\text{impossible}}"
OU = r" \text{ ou } \allowbreak "


def ou(*eqs):
    return OU.join("{" + e + "}" for e in eqs)


class TestRedaction(unittest.TestCase):

    def test_2_11_h_exemple_cible(self):
        """§ 7, exemple cible (forme développée) : ME, tâtonnement (r et △ encadrés, D29), produit nul à trois facteurs."""
        res = resoudre(P2B["2.11 h (dév.)"])
        self.assertEqual(textes(res), [
            r" | 4x^{2} + 2x - 56 = 0 | ",
            r"\iff | 2(2x^{2} + x - 28) = 0 | ME",
            r"Le trinôme \(2x^{2} + x - 28\) n'est pas unitaire : tâtonnement.",
            r"\(\fbox{$x = -4$}\) est solution de \(2x^{2} + x - 28 = 0\), car \(2 \cdot (-4)^{2} - 4 - 28 = 32 - 4 - 28 = 0\).",
            r"Donc \(2x^{2} + x - 28 = (x + 4)(2x + \triangle)\) avec \(4 \cdot \triangle = -28\), donc \(\fbox{$\triangle = -7$}\).",
            r"\iff | 2(x + 4)(2x - 7) = 0 | ",
            r"\iff | " + ou(IMP % "2", "x + 4 = 0", "2x - 7 = 0") + " | produit nul",
            r"\iff | " + ou("x = -4", r"x = \frac{7}{2}") + " | "])
        self.assertEqual(res["S"], r"S = \{-4\,;\,\frac{7}{2}\}")
        self.assertIsNone(res["approx"])
        self.assertEqual([(e["phase"], e["methode"], e["cible"]) for e in res["etapes"]], [
            ("factoriser", "ME", "4x^{2} + 2x - 56"), ("factoriser", "TATONNEMENT", "2x^{2} + x - 28"),
            ("produit_nul", "PRODUIT_NUL", "2(x + 4)(2x - 7)")])
        tat = res["etapes"][1]["parametres"]
        self.assertEqual((tat["r"], tat["triangle"]), (-4, -7))
        self.assertEqual(sd.blocs(res)[0]["rangees"][0]["gauche"], "4x^{2} + 2x - 56 = 0")

    def test_2_10_a_phrase_et_tableau_d_abord(self):
        """§ 13.3 : phrase de choix et tableau d'abord, puis l'équation en membre de gauche ; la ligne ✓ (D29) par le bloc."""
        res = resoudre(P2B["2.10 a"])
        self.assertEqual(textes(res), [
            r" | x^{2} - 5x - 36 = 0 | ",
            r"Pas de ME, pas d'Id. rem. ; le trinôme est unitaire (\(a = 1\)) : S-P.",
            r"On cherche deux nombres dont le produit vaut \(-36\) et la somme vaut \(-5\) :",
            "[tableau]",
            r"\iff | (x + 4)(x - 9) = 0 | ",
            r"\iff | " + ou("x + 4 = 0", "x - 9 = 0") + " | produit nul",
            r"\iff | " + ou("x = -4", "x = 9") + " | "])
        b = sd.blocs(res)[0]["rangees"]
        self.assertEqual([list(r) for r in b[:3]], [["texte"], ["texte"], ["bloc"]])
        self.assertEqual(b[2]["bloc"], sortie.tableau_essais([(r"produit \(= -36\)", 2), ("somme", 1)],
                                                             [["1", "-36", "-35"], ["2", "-18", "-16"], ["3", "-12", "-9"],
                                                              ["4", "-9", "-5"]], ok=3))
        self.assertEqual(b[3]["gauche"], "x^{2} - 5x - 36 = 0")

    def test_javet_2_17_c_formule_sur_un_facteur(self):
        """E9 : ME, S-P en échec, produit nul avec le trinôme, puis Δ (valeur encadrée) et ⇔ x = … ; x₁ et x₂ nommés."""
        res = resoudre(P2B["Javet 2.17 c"])
        self.assertEqual(textes(res), [
            r" | 2x^{2} - 4x - 4 = 0 | ",
            r"\iff | 2(x^{2} - 2x - 2) = 0 | ME",
            r"Le trinôme \(x^{2} - 2x - 2\) est unitaire : S-P.",
            r"On cherche deux nombres dont le produit vaut \(-2\) et la somme vaut \(-2\) :",
            "[tableau]",
            "Aucun couple ne convient : on utilise la formule.",
            r"\iff | " + ou(IMP % "2", "x^{2} - 2x - 2 = 0") + " | produit nul",
            r" | \Delta = b^{2} - 4ac = (-2)^{2} - 4 \cdot 1 \cdot (-2) = 4 + 8 = \fbox{$12$} | ",
            r" | \Delta > 0 \text{ : deux solutions.} \quad \sqrt{\Delta} = \sqrt{12} = 2\sqrt{3} | ",
            r" | x_{1} = \frac{-b - \sqrt{\Delta}}{2a} = \frac{2 - 2\sqrt{3}}{2} = 1 - \sqrt{3} | ",
            r" | x_{2} = \frac{-b + \sqrt{\Delta}}{2a} = \frac{2 + 2\sqrt{3}}{2} = 1 + \sqrt{3} | ",
            r"\iff | " + ou(r"x = 1 - \sqrt{3}", r"x = 1 + \sqrt{3}") + " | "])
        self.assertEqual(res["approx"], r"soit \(x_{1} \approx -0{,}732\) et \(x_{2} \approx 2{,}732\)")
        self.assertEqual([e["phase"] for e in res["etapes"]], ["factoriser", "factoriser", "produit_nul", "delta_valeur",
                                                               "delta_nombre"])
        self.assertEqual(res["variantes"], [])

    def test_sp_en_echec_puis_formule_sans_repeter_l_equation(self):
        """§ 7 (x² + 4x − 1) : aucun ⇔ ne suit, l'équation n'est pas répétée (§ 13.3) ; lignes de Δ en rangées sans lien."""
        res = resoudre(P2B["§ 7 x² + 4x − 1"])
        self.assertEqual(textes(res), [
            r"Pas de ME, pas d'Id. rem. ; le trinôme est unitaire (\(a = 1\)) : S-P.",
            r"On cherche deux nombres dont le produit vaut \(-1\) et la somme vaut \(4\) :",
            "[tableau]",
            "Aucun couple ne convient : on utilise la formule.",
            r" | \Delta = b^{2} - 4ac = 4^{2} - 4 \cdot 1 \cdot (-1) = 16 + 4 = \fbox{$20$} | ",
            r" | \Delta > 0 \text{ : deux solutions.} \quad \sqrt{\Delta} = \sqrt{20} = 2\sqrt{5} | ",
            r" | x_{1} = \frac{-b - \sqrt{\Delta}}{2a} = \frac{-4 - 2\sqrt{5}}{2} = -2 - \sqrt{5} | ",
            r" | x_{2} = \frac{-b + \sqrt{\Delta}}{2a} = \frac{-4 + 2\sqrt{5}}{2} = -2 + \sqrt{5} | "])
        self.assertEqual(res["S"], r"S = \{-2 - \sqrt{5}\,;\,-2 + \sqrt{5}\}")
        self.assertEqual(res["approx"], r"soit \(x_{1} \approx -4{,}236\) et \(x_{2} \approx 0{,}236\)")
        self.assertTrue(all(not r.get("lien") for r in sd.blocs(res)[0]["rangees"]))

    def test_tatonnement_en_echec_une_seule_ligne(self):
        """D1, E7 : une seule ligne nomme les diviseurs (|d| croissant), sans calcul d'essai ; puis la formule (2.12 b : √Δ = 1)."""
        res = resoudre(P2B["2.12 b"])
        self.assertEqual(textes(res), [
            r"Pas de ME, pas d'Id. rem. ; \(a = 6 \neq 1\) : tâtonnement.",
            r"On teste les diviseurs de \(1\) (\(\pm 1\)) : aucun n'est solution. On utilise la formule.",
            r" | \Delta = b^{2} - 4ac = 5^{2} - 4 \cdot 6 \cdot 1 = 25 - 24 = \fbox{$1$} | ",
            r" | \Delta > 0 \text{ : deux solutions.} \quad \sqrt{\Delta} = 1 | ",
            r" | x_{1} = \frac{-b - \sqrt{\Delta}}{2a} = \frac{-5 - 1}{12} = -\frac{1}{2} | ",
            r" | x_{2} = \frac{-b + \sqrt{\Delta}}{2a} = \frac{-5 + 1}{12} = -\frac{1}{3} | "])
        res = resoudre(P2B["Javet 2.17 d"])
        self.assertEqual(textes(res)[1], r"On teste les diviseurs de \(12\) (\(\pm 1\), \(\pm 2\), \(\pm 3\), \(\pm 4\), \(\pm 6\), "
                                         r"\(\pm 12\)) : aucun n'est solution. On utilise la formule.")
        self.assertEqual(textes(res)[-1], r"\(\Delta < 0\) : l'équation n'a aucune solution réelle.")
        self.assertEqual(res["S"], r"S = \varnothing")

    def test_x2_plus_4_sp_avec_b_nul(self):
        """§ 6 : S-P avec b = 0 (deux nombres positifs), tableau en échec, puis Δ < 0 (sans calcul intermédiaire 0 − 16)."""
        res = resoudre(P2B["§ 6 x² + 4"])
        b = sd.blocs(res)[0]["rangees"]
        self.assertEqual([c["cases"] for c in b[2]["bloc"]["lignes"]], [["1", "4", "5"], ["2", "2", "4"]])
        self.assertNotIn("ok", json.dumps(b[2]["bloc"]))
        self.assertEqual(textes(res)[4:], [r" | \Delta = b^{2} - 4ac = 0^{2} - 4 \cdot 1 \cdot 4 = \fbox{$-16$} | ",
                                           r"\(\Delta < 0\) : l'équation n'a aucune solution réelle."])

    def test_me_de_moins_6_puis_id_rem(self):
        """§ 6 : −6x² + 12x − 6 = 0 : phrase de a < 0 (E3), Id. rem. avec vérification, D24, « −6 = 0 » impossible."""
        res = resoudre(P2B["§ 6 −6x² + 12x − 6"])
        self.assertEqual(textes(res), [
            r" | -6x^{2} + 12x - 6 = 0 | ",
            r"Le coefficient de \(x^{2}\) est négatif (\(a = -6\)) : on met d'abord \(-6\) en évidence.",
            r"\iff | -6(x^{2} - 2x + 1) = 0 | ME",
            r"Id. rem. \(A^{2} - 2AB + B^{2}\) avec \(\fbox{$A = x,\ B = 1$}\). Vérification : \(2AB = 2 \cdot x \cdot 1 = 2x\) "
            r"\(\checkmark\)",
            r"\iff | -6(x - 1)^{2} = 0 | ",
            r"\iff | -6(x - 1)(x - 1) = 0 | ",
            r"\iff | " + ou(IMP % "-6", "x - 1 = 0") + " | produit nul",
            r"\iff | x = 1 | "])
        res = resoudre(P2B["2.10 e"])
        self.assertEqual(textes(res)[1], r"Le trinôme n'est pas unitaire (\(a = -1\)) : on met d'abord \(-1\) en évidence.")
        self.assertEqual(textes(res)[2], r"\iff | -(y^{2} - 10y + 9) = 0 | ME")
        self.assertEqual(textes(res)[3], r"Le trinôme \(y^{2} - 10y + 9\) est unitaire : S-P.")

    def test_id_rem_carre_sans_me(self):
        """2.9 b : la ligne de vérification avant la chaîne, (t + 10)² puis D24, le facteur une seule fois au produit nul."""
        res = resoudre(P2B["2.9 b"])
        self.assertEqual(textes(res), [
            r" | t^{2} + 20t + 100 = 0 | ",
            r"Id. rem. \(A^{2} + 2AB + B^{2}\) avec \(\fbox{$A = t,\ B = 10$}\). Vérification : \(2AB = 2 \cdot t \cdot 10 = 20t\) "
            r"\(\checkmark\)",
            r"\iff | (t + 10)^{2} = 0 | ",
            r"\iff | (t + 10)(t + 10) = 0 | ",
            r"\iff | t + 10 = 0 | produit nul",
            r"\iff | t = -10 | "])

    def test_id_rem_difference_et_d20(self):
        """E5 (étiquette, A et B dans un seul cadre, D29) ; D20 : kx = … seulement si k ≠ ±1 et la constante n'est pas entière."""
        res = resoudre(P2B["2.9 h"])
        self.assertEqual(textes(res), [
            r" | 9x^{2} - \frac{1}{9} = 0 | ",
            r"\iff | \left(3x + \frac{1}{3}\right)\left(3x - \frac{1}{3}\right) = 0 | Id. rem. \(A^{2} - B^{2}\) avec "
            r"\(\fbox{$A = 3x,\ B = \frac{1}{3}$}\)",
            r"\iff | " + ou(r"3x + \frac{1}{3} = 0", r"3x - \frac{1}{3} = 0") + " | produit nul",
            r"\iff | " + ou(r"3x = -\frac{1}{3}", r"3x = \frac{1}{3}") + " | ",
            r"\iff | " + ou(r"x = -\frac{1}{9}", r"x = \frac{1}{9}") + " | "])
        res = resoudre(P2B["§ 7 25x² − 3"])
        self.assertEqual(textes(res)[3:], [r"\iff | " + ou(r"5x = -\sqrt{3}", r"5x = \sqrt{3}") + " | ",
                                           r"\iff | " + ou(r"x = -\frac{\sqrt{3}}{5}", r"x = \frac{\sqrt{3}}{5}") + " | "])
        self.assertEqual(res["approx"], r"soit \(x \approx -0{,}346\) ou \(x \approx 0{,}346\)")
        res = resoudre(P2B["2.9 d (dév.)"])                     # 2x + 3 = 0 ⇔ x = −3/2 : la constante est entière
        self.assertEqual(textes(res)[-1], r"\iff | " + ou(r"x = -\frac{3}{2}", r"x = \frac{3}{2}") + " | ")
        self.assertEqual(len(textes(res)), 4)
        self.assertIn(r"B = 2\sqrt{2}", textes(resoudre(P2B["§ 13.4 x² − 8"]))[1])                 # § 13.4 : B simplifié
        self.assertIn(r"B = \frac{\sqrt{2}}{2}", textes(resoudre(P2B["§ 13.4 x² − 1/2"]))[1])

    def test_monomes(self):
        """D7 et § 13.4 : 3x² = 0 ⇔ x = 0 ; ME 3x : « 3x = 0 ou x − 4 = 0 », puis « x = 0 ou x = 4 »."""
        self.assertEqual(textes(resoudre(P2B["§ 13.4 3x²"])), [" | 3x^{2} = 0 | ", r"\iff | x = 0 | "])
        self.assertEqual(textes(resoudre(P2B["x²"])), [" | x^{2} = 0 | ", r"\iff | x = 0 | "])
        self.assertEqual(textes(resoudre(P2B["§ 7 3x² − 12x"])), [
            " | 3x^{2} - 12x = 0 | ", r"\iff | 3x(x - 4) = 0 | ME",
            r"\iff | " + ou("3x = 0", "x - 4 = 0") + " | produit nul", r"\iff | " + ou("x = 0", "x = 4") + " | "])
        self.assertEqual(textes(resoudre(P2B["a < 0, ME de −x"]))[1],
                         r"Le trinôme n'est pas unitaire (\(a = -1\)) : on met d'abord \(-x\) en évidence.")

    def test_formule_coefficients_non_entiers(self):
        """D22, E4 : la phrase de choix de la formule ; E11 : fraction réduite dans la même ligne (Javet 2.17 e)."""
        res = resoudre(P2B["Javet 2.17 e"])
        self.assertEqual(textes(res), [
            "Pas de ME, pas d'Id. rem. ; les coefficients ne sont pas entiers : on utilise la formule.",
            r" | \Delta = b^{2} - 4ac = (-4)^{2} - 4 \cdot \frac{3}{2} \cdot (-1) = 16 + 6 = \fbox{$22$} | ",
            r" | \Delta > 0 \text{ : deux solutions.} \quad \sqrt{\Delta} = \sqrt{22} | ",
            r" | x_{1} = \frac{-b - \sqrt{\Delta}}{2a} = \frac{4 - \sqrt{22}}{3} | ",
            r" | x_{2} = \frac{-b + \sqrt{\Delta}}{2a} = \frac{4 + \sqrt{22}}{3} | "])
        self.assertEqual(res["approx"], r"soit \(x_{1} \approx -0{,}230\) et \(x_{2} \approx 2{,}897\)")
        res = resoudre(P2B["Δ = 0, coefficients non entiers"])
        self.assertEqual(textes(res)[-2:], [r"\(\Delta = 0\) : une seule solution.",
                                            r" | x = \frac{-b}{2a} = \frac{-1}{1} = -1 | "])

    def test_decimaux_de_l_enonce(self):
        """E14 : l'énoncé garde son écriture ; un résultat décimal fini reste décimal (0,2x² − 0,5x − 0,3) ; sinon une fraction."""
        res = resoudre(P2B["décimaux, résultats décimaux"])
        self.assertEqual(res["S"], r"S = \{-0{,}5\,;\,3\}")
        self.assertIn(r"\fbox{$0{,}49$}", textes(res)[1])
        self.assertIn(r"\sqrt{\Delta} = 0{,}7", textes(res)[2])
        res = resoudre(P2B["§ 6 0,5x² − 2"])
        self.assertEqual(textes(res)[1], r" | \Delta = b^{2} - 4ac = 0^{2} - 4 \cdot 0{,}5 \cdot (-2) = \fbox{$4$} | ")
        res = resoudre(P2B["décimaux, Id. rem."])
        self.assertEqual(textes(res)[0], r" | 0{,}25x^{2} - 1 = 0 | ")
        self.assertIn(r"\fbox{$A = 0{,}5x,\ B = 1$}", textes(res)[1])
        res = resoudre(P2B["décimaux, a < 0"])
        self.assertIn(r"4 \cdot (-0{,}5) \cdot 1", textes(res)[1])

    def test_sp_de_plus_de_12_lignes(self):
        """§ 13.5 et point 5 du plan : pas de tableau, la phrase, puis la formule."""
        res = resoudre(P2B["§ 13.5 S-P de plus de 12 lignes"])
        self.assertEqual(textes(res)[:2], [r"Pas de ME, pas d'Id. rem. ; le trinôme est unitaire (\(a = 1\)) : S-P.",
                                           sd.PHRASE_SP_TROP])
        self.assertNotIn("[tableau]", textes(res))

    def test_valeurs_approchees_e14(self):
        """E14 : ≈ seulement pour les irrationnelles, une fois, après S ; x₁ et x₂ quand la formule les a nommés ; x ≈ 1 × 10⁻³."""
        res = resoudre(P2B["§ 6 x² + 1000x − 1"])
        self.assertEqual(res["approx"], r"soit \(x_{1} \approx -1\text{’}000{,}001\) et \(x_{2} \approx 1 \times 10^{-3}\)")
        self.assertEqual(resoudre(P2B["2.9 j"])["approx"], r"soit \(x \approx -2{,}236\) ou \(x \approx 2{,}236\)")
        self.assertEqual(resoudre(P2B["Javet 2.17 a"])["approx"], r"soit \(x_{1} \approx -4{,}562\) et \(x_{2} \approx -0{,}438\)")
        self.assertIsNone(resoudre(P2B["2.10 a"])["approx"])

    def test_variante_par_la_formule(self):
        """E12 : proposée seulement si le chemin du cours n'utilise pas la formule ; sans phrase de choix ; Δ = 0 (4x² − 12x + 9) ;
        a < 0 : x₁ avec −√Δ, S croissant (§ 13.4)."""
        self.assertEqual(resoudre(P2B["§ 7 4x² − 12x + 9"])["variantes"], ["formule"])
        self.assertEqual(resoudre(P2B["Javet 2.17 c"])["variantes"], [])
        self.assertEqual(resoudre(P2B["§ 7 3x² − 12x"])["variantes"], [])       # la variante n'aurait pas de formule (c = 0)
        v = resoudre(P2B["§ 7 4x² − 12x + 9"], sd.ORDRE_PAR_LA_FORMULE)
        self.assertEqual(textes(v), [r" | \Delta = b^{2} - 4ac = (-12)^{2} - 4 \cdot 4 \cdot 9 = 144 - 144 = \fbox{$0$} | ",
                                     r"\(\Delta = 0\) : une seule solution.",
                                     r" | x = \frac{-b}{2a} = \frac{12}{8} = \frac{3}{2} | "])
        self.assertEqual(v["etapes"][0]["phase"], "factoriser")
        self.assertEqual(v["etapes"][0]["lignes"], [])
        self.assertEqual(v["variantes"], [])
        v = resoudre("-x^2+2x+1=0", sd.ORDRE_PAR_LA_FORMULE)
        self.assertEqual(textes(v)[2:], [r" | x_{1} = \frac{-b - \sqrt{\Delta}}{2a} = \frac{-2 - 2\sqrt{2}}{-2} = 1 + \sqrt{2} | ",
                                         r" | x_{2} = \frac{-b + \sqrt{\Delta}}{2a} = \frac{-2 + 2\sqrt{2}}{-2} = 1 - \sqrt{2} | "])
        self.assertEqual(textes(v)[0], r" | \Delta = b^{2} - 4ac = 2^{2} - 4 \cdot (-1) \cdot 1 = 4 + 4 = \fbox{$8$} | ")
        self.assertEqual(v["S"], r"S = \{1 - \sqrt{2}\,;\,1 + \sqrt{2}\}")
        self.assertEqual(v["approx"], r"soit \(x_{2} \approx -0{,}414\) et \(x_{1} \approx 2{,}414\)")
        for nom, res in TOUTES:
            if nom.endswith("(variante formule)"):
                with self.subTest(nom=nom):
                    self.assertFalse(any("Pas de ME" in t or "unitaire" in t for t in textes(res)))

    def test_d29_valeurs_encadrees(self):
        """D29 : A et B (un seul cadre), r et △, la valeur finale de Δ ; jamais la vérification, les calculs ni les étiquettes
        « ME » ou « produit nul » ; la ligne ✓ par le bloc (ok)."""
        for nom, res in TOUTES:
            with self.subTest(nom=nom):
                for t in textes(res):
                    for cadre in re.findall(r"\\fbox\{\$(.*?)\$\}", t):
                        self.assertRegex(cadre, r"^(A = .*,\\ B = .*|[a-z] = -?[0-9].*|\\triangle = .*|-?[0-9\\].*)$")
                    if "Vérification" in t:
                        self.assertNotIn("fbox", t.split("Vérification")[1])
                    if t.startswith(r" | \Delta = b^{2}"):
                        self.assertEqual(t.count("fbox"), 1)
                        self.assertTrue(t.endswith("$} | "))
                    if t.startswith(r"\iff"):
                        self.assertNotIn("fbox", t.split(" | ")[1])
                me = [t for t in textes(res) if "en évidence" in t]
                self.assertFalse(any("fbox" in t for t in me))

    def test_vouvoiement_et_vocabulaire(self):
        """R12 et C6 : aucun texte produit (blocs, messages, phrases) ne tutoie ni ne cite une méthode interne."""
        sorties = [sd.blocs(r) for _, r in TOUTES] + [sd.blocs(r) for _, _, r in GENEREES]
        sorties += [list(sd.MESSAGES.values()), [sd.PHRASE_IDENTITE, sd.PHRASE_EGALITE_FAUSSE, sd.PHRASE_SP_TROP]]
        for i, o in enumerate(sorties):
            for t in chaines(o):
                with self.subTest(i=i, texte=t[:60]):
                    self.assertIsNone(INTERDITS.search(t))
                    self.assertIsNone(TUTOIEMENT.search(t))

    def test_phrases_d_exp_log_reprises(self):
        """§ 13.4 : la phrase de l'identité est celle d'Exp-log (et celle de l'égalité fausse), pour P4b."""
        with open(exp_log.__file__, encoding="utf-8") as f:
            source = f.read()
        self.assertIn('"' + sd.PHRASE_IDENTITE + '"', source)
        self.assertIn('"' + sd.PHRASE_EGALITE_FAUSSE + '"', source)


class TestSansEtat(unittest.TestCase):
    """A7 : aucune instruction global, aucun conteneur modifiable au niveau du module (les décimaux de l'énoncé sont un paramètre)."""

    def test_aucun_etat(self):
        import ast
        with open(sd.__file__, encoding="utf-8") as f:
            arbre = ast.parse(f.read())
        self.assertEqual([n.lineno for n in ast.walk(arbre) if isinstance(n, (ast.Global, ast.Nonlocal))], [])
        modifiables = {nom: type(v).__name__ for nom, v in vars(sd).items()
                       if not nom.startswith("__") and isinstance(v, (list, dict, set, bytearray))}
        self.assertEqual(modifiables, {})
        with self.assertRaises(TypeError):
            sd.MESSAGES["hors_cours"] = ""


# ---------------------------------------------------------------------------------------------------------------------------
# Écriture des nombres et des polynômes
# ---------------------------------------------------------------------------------------------------------------------------
VALEURS = [0, 1, -3, 1234, F(1, 3), F(-5, 2), F(1, 10), F(-27, 100), F(19025, 10000), F(12345, 10), F(1, 1000), F(13, 60),
           F(1, 3 * 10 ** 9), F(123456789, 10 ** 9), F(-1, 1024), F(7, 8), F(5, 1)]


class TestEcriture(unittest.TestCase):

    def test_nb_exact_sans_etat_croise_avec_exp_log(self):
        """Même Nb (valeur et écriture) qu'exp_log._nb_exact, hors et sous son état _DECIMAUX ; même TeX que nombres.exact."""
        sous_decimaux = exp_log._avec_decimaux(lambda arbre, v: exp_log._nb_exact(v))
        for v in VALEURS:
            for dec in (False, True):
                with self.subTest(v=v, dec=dec):
                    n = sd.nb_exact(v, dec)
                    ref = sous_decimaux(Nb(F(1, 2), "0,5"), v) if dec else exp_log._nb_exact(v)
                    self.assertEqual((n.val, n.dec), (ref.val, ref.dec))
                    self.assertEqual(expr.tex(n), nombres.exact(v, dec))
        self.assertFalse(exp_log._DECIMAUX)

    def test_arbres(self):
        T = expr.tex
        self.assertEqual(T(sd.arbre_polynome([-56, 2, 4])), "4x^{2} + 2x - 56")
        self.assertEqual(T(sd.arbre_polynome([-1, -4, F(3, 2)])), r"\frac{3}{2}x^{2} - 4x - 1")
        self.assertEqual(T(sd.arbre_polynome([-2, 0, F(1, 2)], "t", True)), "0{,}5t^{2} - 2")
        self.assertEqual(T(sd.arbre_polynome([-9, 10, -1], "y")), "-y^{2} + 10y - 9")
        self.assertEqual(T(sd.arbre_polynome([0])), "0")
        self.assertEqual(T(sd.arbre_nombre(Nombre(-2, -1, 5))), r"-2 - \sqrt{5}")
        self.assertEqual(T(sd.arbre_nombre(Nombre(F(-5, 2), F(1, 2), 17))), r"\frac{-5 + \sqrt{17}}{2}")
        self.assertEqual(T(sd.arbre_nombre(Nombre(0, F(-1, 5), 3))), r"-\frac{\sqrt{3}}{5}")
        self.assertEqual(T(sd.arbre_nombre(Nombre(0, 2, 2))), r"2\sqrt{2}")
        self.assertEqual(T(sd.arbre_nombre(Nombre(F(7, 2)))), r"\frac{7}{2}")
        self.assertEqual(T(sd.arbre_nombre(Nombre(F(-1, 2)), True)), "-0{,}5")

    def test_termes_developpes(self):
        lire_g = lambda s: expr.lire_membres(s)[0]
        self.assertEqual(sd.termes_developpes(lire_g("4x^2+2x-56=0"), "x"), [(2, 4), (1, 2), (0, -56)])
        self.assertEqual(sd.termes_developpes(lire_g("-y^2+10y-9=0"), "y"), [(2, -1), (1, 10), (0, -9)])
        self.assertEqual(sd.termes_developpes(lire_g("(3/2)x^2-x=0"), "x"), [(2, F(3, 2)), (1, -1)])
        for s in ("5+x^2-6x=0", "x^2+x^2=0", "x(x+1)=0", "(x+1)^2=0", "x^2+0x=0", "(2^2)x=0", "x*3=0"):
            with self.subTest(s=s):
                self.assertIsNone(sd.termes_developpes(lire_g(s), "x"))


# ---------------------------------------------------------------------------------------------------------------------------
# appliquer et messages
# ---------------------------------------------------------------------------------------------------------------------------
class TestAppliquer(OracleMixin, unittest.TestCase):

    def test_s_applique_et_appliquer(self):
        """§ 6, méthodes : s_applique vrai ⇒ appliquer rend une étape (phase « factoriser », l'équation P = 0 en tête) dont la
        factorisation se redéveloppe exactement ; formule avec Δ < 0 : S = ∅ par l'oracle ; s_applique faux ⇒ None."""
        polys = {nom: polynome(s) for nom, s in P2B.items()}
        polys.update({f"généré {i}": P for i, P in enumerate(GENERES_2)})
        for nom, P in polys.items():
            for m in sd.METHODES:
                with self.subTest(nom=nom, methode=m):
                    e = sd.appliquer(m, P)
                    self.assertEqual(e is not None, sd.s_applique(m, P))
                    if e is None:
                        continue
                    self.assertEqual(e["phase"], "factoriser")
                    self.assertTrue(e["lignes"])
                    f = e["parametres"].get("facteurs")
                    if m == "FORMULE":
                        self.assertSolutionsOracle(P, e["parametres"]["solutions"], nom)
                    if f is not None:
                        self.assertTrue(egal_au_polynome(f, P), f)
                    else:
                        self.assertEqual((m, e["parametres"]["delta"] < 0), ("FORMULE", True))
                    if any(not isinstance(r, LigneTexte) and r[0] for r in e["lignes"]):         # un ⇔ : l'équation P = 0 en tête
                        self.assertEqual(e["lignes"][0], ("", expr.tex(sd.arbre_polynome(P)) + " = 0", None))
                    json.dumps(bloc_rangees(e["lignes"]), allow_nan=False)


# ---------------------------------------------------------------------------------------------------------------------------
# P3 : ramener (E1) et développer (E2)
# ---------------------------------------------------------------------------------------------------------------------------
PHRASE = r"On ramène d'abord l'équation à la forme \(\ldots = 0\) :"


class TestRamener(unittest.TestCase):

    def test_2_11_h_complet_exemple_cible(self):
        """§ 7, exemple cible, à partir de « 4x² + 2x = 56 » : la ligne ramenée ouvre la chaîne (une ME suit : pas de phrase) ;
        étapes ramener · factoriser (ME) · factoriser (tâtonnement) · produit nul."""
        res = resoudre(P3["2.11 h"])
        self.assertEqual(textes(res), [
            r" | 4x^{2} + 2x = 56 | ",
            r"\iff | 4x^{2} + 2x - 56 = 0 | ",
            r"\iff | 2(2x^{2} + x - 28) = 0 | ME",
            r"Le trinôme \(2x^{2} + x - 28\) n'est pas unitaire : tâtonnement.",
            r"\(\fbox{$x = -4$}\) est solution de \(2x^{2} + x - 28 = 0\), car \(2 \cdot (-4)^{2} - 4 - 28 = 32 - 4 - 28 = 0\).",
            r"Donc \(2x^{2} + x - 28 = (x + 4)(2x + \triangle)\) avec \(4 \cdot \triangle = -28\), donc \(\fbox{$\triangle = -7$}\).",
            r"\iff | 2(x + 4)(2x - 7) = 0 | ",
            r"\iff | " + ou(IMP % "2", "x + 4 = 0", "2x - 7 = 0") + " | produit nul",
            r"\iff | " + ou("x = -4", r"x = \frac{7}{2}") + " | "])
        self.assertEqual(res["S"], r"S = \{-4\,;\,\frac{7}{2}\}")
        self.assertEqual([(e["phase"], e["methode"], e["cible"]) for e in res["etapes"]], [
            ("ramener", "RAMENER", "4x^{2} + 2x = 56"), ("factoriser", "ME", "4x^{2} + 2x - 56"),
            ("factoriser", "TATONNEMENT", "2x^{2} + x - 28"), ("produit_nul", "PRODUIT_NUL", "2(x + 4)(2x - 7)")])
        self.assertEqual(res["etapes"][0]["parametres"]["cote"], "gauche")
        b = sd.blocs(res)[0]["rangees"]
        self.assertEqual((b[0]["gauche"], b[0]["expr"]), ("4x^{2} + 2x = 56", "4x^{2} + 2x - 56 = 0"))

    def test_phrase_seulement_avant_une_phrase_de_choix(self):
        """E1 : la phrase précède l'énoncé quand une phrase de choix (S-P, tâtonnement, formule) suit directement ; rien avant une
        ME ou une Id. rem. ; jamais dans la variante « formule »."""
        avec = {nom for nom, res in TOUTES if PHRASE in textes(res)}
        self.assertEqual(avec, {"2.10 h", "2.10 j", "2.11 f", "E1 côté droit, formule", "E1 décimaux", "E1 fractions, formule",
                                "(x + 1)(x + 3) = 15", "E2 distribution", "E2 distribution, monôme",
                                "E2 « − » devant une distribution", "E2 parenthèse précédée de « − »", "E2 Id. rem. (A + B)²",
                                "E2 Id. rem. (A + B)², Δ < 0", "E2 Id. rem. (A − B)², A constante", "E2 décimaux"})
        for nom, res in TOUTES:
            t = textes(res)
            if PHRASE in t:
                with self.subTest(nom=nom):
                    self.assertEqual(t.index(PHRASE), 1)                        # après l'énoncé, qui passe à sa droite (B3)
                    self.assertEqual(res["etapes"][0]["phase"], "ramener")
                    suite = [x for x in t[2:] if not x.startswith(("\\iff", " | "))]
                    self.assertTrue(suite[0].startswith(("Pas de ME", "Le trinôme")), suite[0])
        res = resoudre(P3["2.10 h"])
        self.assertEqual(textes(res)[:4], [" | x^{2} + 7x = 18 | ", PHRASE, r"\iff | x^{2} + 7x - 18 = 0 | ",
                                           r"Pas de ME, pas d'Id. rem. ; le trinôme est unitaire (\(a = 1\)) : S-P."])
        self.assertEqual(sd.blocs(res)[0]["rangees"][0], {"texte": PHRASE})

    def test_cote_du_coefficient_de_tete_positif(self):
        """E1.2 : tout du côté où le coefficient du terme de plus haut degré devient positif (2.10 j, 2.11 j), à gauche si les deux
        conviennent ; premier membre nul : à droite."""
        for nom, debut, cote in (("2.10 j", r"\iff | x^{2} - 4x - 32 = 0 | ", "droite"),
                                 ("2.11 j", r"\iff | 12u^{2} - 45u - 12 = 0 | ", "droite"),
                                 ("E1 côté droit, formule", r"\iff | x^{2} + 4x + 1 = 0 | ", "droite"),
                                 ("E1 premier membre nul", r"\iff | x^{2} - 4 = 0 | ", "droite"),
                                 ("2.9 f", r"\iff | 196z^{2} + 280z + 100 = 0 | ", "gauche")):
            with self.subTest(nom=nom):
                res = resoudre(P3[nom])
                self.assertIn(debut, textes(res))
                self.assertEqual([(e["methode"], e["parametres"]["cote"]) for e in res["etapes"] if e["phase"] == "ramener"],
                                 [("RAMENER", cote)])

    def test_ligne_seulement_reordonnee(self):
        """E1 (quiz.md, réponse 1) et § 5 : second membre nul, termes dans le désordre : une ligne sans étiquette, qui appartient à
        l'étape suivante (aucune étape « ramener ») ; a < 0 gardé (E1.1), puis la ME de −1 (D21)."""
        res = resoudre(P3["E1 termes dans le désordre"])
        self.assertEqual(textes(res)[:3], [" | 5 + x^{2} - 6x = 0 | ", r"\iff | x^{2} - 6x + 5 = 0 | ",
                                           r"Pas de ME, pas d'Id. rem. ; le trinôme est unitaire (\(a = 1\)) : S-P."])
        self.assertEqual(res["etapes"][0]["methode"], "SP")
        self.assertEqual(res["etapes"][0]["lignes"][:2], [("", "5 + x^{2} - 6x = 0", None), (r"\iff", "x^{2} - 6x + 5 = 0", None)])
        res = resoudre(P3["E1 désordre, a < 0 gardé"])
        self.assertEqual(textes(res)[:4], [" | 10y - y^{2} - 9 = 0 | ", r"\iff | -y^{2} + 10y - 9 = 0 | ",
                                           r"Le trinôme n'est pas unitaire (\(a = -1\)) : on met d'abord \(-1\) en évidence.",
                                           r"\iff | -(y^{2} - 10y + 9) = 0 | ME"])
        self.assertEqual([e["methode"] for e in res["etapes"]][:2], ["ME", "SP"])
        self.assertEqual(res["etapes"][0]["parametres"]["k"], -1)

    def test_double_distribution_x_plus_1_x_plus_3(self):
        """§ 7 : la phrase, les produits partiels (« double distribution »), la réduction sans étiquette, puis E1.2 et le S-P."""
        res = resoudre(P3["(x + 1)(x + 3) = 15"])
        self.assertEqual(textes(res)[:6], [
            r" | (x + 1)(x + 3) = 15 | ", PHRASE,
            r"\iff | x^{2} + 3x + x + 3 = 15 | double distribution",
            r"\iff | x^{2} + 4x + 3 = 15 | ",
            r"\iff | x^{2} + 4x - 12 = 0 | ",
            r"Pas de ME, pas d'Id. rem. ; le trinôme est unitaire (\(a = 1\)) : S-P."])
        self.assertEqual(textes(res)[-3:], [r"\iff | (x - 2)(x + 6) = 0 | ",
                                            r"\iff | " + ou("x - 2 = 0", "x + 6 = 0") + " | produit nul",
                                            r"\iff | " + ou("x = 2", "x = -6") + " | "])
        self.assertEqual(res["S"], r"S = \{-6\,;\,2\}")
        self.assertEqual([(e["phase"], e["methode"]) for e in res["etapes"]], [
            ("ramener", "DEVELOPPER"), ("ramener", "RAMENER"), ("factoriser", "SP"), ("produit_nul", "PRODUIT_NUL")])
        self.assertEqual(res["etapes"][0]["parametres"]["developpements"], ["double distribution"])

    def test_moins_devant_un_produit(self):
        """E2 : le produit développé s'écrit d'abord entre parenthèses, « − (…) », puis sans parenthèses, puis réduit ; second membre
        nul : a < 0 gardé (E1.1), ME de −1."""
        res = resoudre(P3["E2 « − » devant un produit"])
        self.assertEqual(textes(res)[:6], [
            r" | 5 - (x + 1)(x + 3) = 0 | ",
            r"\iff | 5 - (x^{2} + 3x + x + 3) = 0 | double distribution",
            r"\iff | 5 - x^{2} - 3x - x - 3 = 0 | ",
            r"\iff | -x^{2} - 4x + 2 = 0 | ",
            r"Le trinôme n'est pas unitaire (\(a = -1\)) : on met d'abord \(-1\) en évidence.",
            r"\iff | -(x^{2} + 4x - 2) = 0 | ME"])
        res = resoudre(P3["E2 « − » devant une distribution"])
        self.assertEqual(textes(res)[2:6], [
            r"\iff | x^{2} - (x^{2} + x) + 3x^{2} = 4 | distribution", r"\iff | x^{2} - x^{2} - x + 3x^{2} = 4 | ",
            r"\iff | 3x^{2} - x = 4 | ", r"\iff | 3x^{2} - x - 4 = 0 | "])
        res = resoudre(P3["E2 parenthèse précédée de « − »"])
        self.assertEqual(textes(res)[:3], [r" | x^{2} - (2x + 3) = 0 | ", PHRASE, r"\iff | x^{2} - 2x - 3 = 0 | "])
        self.assertEqual(res["etapes"][0]["methode"], "DEVELOPPER")

    def test_id_rem_et_distribution(self):
        """E2 : carré d'un binôme par l'Id. rem. (étiquette « Id. rem. (A ± B)² avec A = …, B = … », sans cadre : A et B se lisent,
        ils ne se trouvent pas) ; nombre ou monôme × parenthèse : « distribution » ; décimaux de l'énoncé gardés."""
        self.assertEqual(textes(resoudre(P3["E2 Id. rem. (A + B)²"]))[2],
                         r"\iff | x^{2} + 6x + 9 = 2x + 14 | Id. rem. \((A + B)^{2}\) avec \(A = x,\ B = 3\)")
        self.assertEqual(textes(resoudre(P3["E2 Id. rem. (A − B)², A constante"]))[2],
                         r"\iff | 9 - 6x + x^{2} = 1 + x | Id. rem. \((A - B)^{2}\) avec \(A = 3,\ B = x\)")
        self.assertEqual(textes(resoudre(P3["E2 distribution, monôme"]))[2:4],
                         [r"\iff | x^{2} - 4x = 5 | distribution", r"\iff | x^{2} - 4x - 5 = 0 | "])
        t = textes(resoudre(P3["E2 décimaux"]))
        self.assertEqual(t[2:4], [r"\iff | 0{,}5x + 1 = x^{2} | distribution", r"\iff | x^{2} - 0{,}5x - 1 = 0 | "])

    def test_az_4_1_g_developpement(self):
        """§ 7 (Az 4.1 g) : Id. rem. et distribution sur la même ligne, étiquettes séparées par « ; », « − (4x² − 4x) » puis sans
        parenthèses, puis 1 = 1 ; l'identité (P4b) : la phrase d'Exp-log, S = ℝ (TestDegres)."""
        g, d = expr.lire_membres("(2x-1)^2-4x(x-1)=1")
        prep = sd.ramener(g, d, "x")
        self.assertTrue(prep["P"].nul())
        methode, parametres, lignes = prep["pas"][0]
        self.assertEqual(methode, "DEVELOPPER")
        self.assertEqual([(tex_element(e), p) for e, p in lignes], [
            ("4x^{2} - 4x + 1 - (4x^{2} - 4x) = 1", r"Id. rem. \((A - B)^{2}\) avec \(A = 2x,\ B = 1\) ; distribution"),
            ("4x^{2} - 4x + 1 - 4x^{2} + 4x = 1", None), ("1 = 1", None)])
        res = resoudre("(2x-1)^2-4x(x-1)=1")
        self.assertEqual((res["statut"], res["S"]), ("resolu", r"S = \mathbb{R}"))

    def test_reduction_et_premier_membre_nul(self):
        self.assertEqual(textes(resoudre(P3["E1 réduction"]))[:3],
                         [" | x^{2} + x^{2} = 8 | ", r"\iff | 2x^{2} = 8 | ", r"\iff | 2x^{2} - 8 = 0 | "])
        self.assertEqual(textes(resoudre(P3["E1 premier membre nul"]))[:2], [" | 0 = x^{2} - 4 | ", r"\iff | x^{2} - 4 = 0 | "])
        self.assertEqual(textes(resoudre(P3["E1 décimaux"]))[:3],
                         [" | 0{,}5x^{2} = 2 | ", PHRASE, r"\iff | 0{,}5x^{2} - 2 = 0 | "])

    def test_chaque_ligne_relue(self):
        """Garde-fou : chaque ligne écrite par `ramener` a les mêmes membres (lignes du développement et de la réduction) ou le même
        P (ligne ramenée), relus par vers_polynome ; une écriture faussée lève une incohérence (« ne_conclut_pas »)."""
        for nom, saisie in P3.items():
            g, d, x, dec = lire(saisie)
            prep = sd.ramener(g, d, x, dec)
            P = polynome(saisie)
            with self.subTest(nom=nom):
                self.assertTrue(prep["P"] == P or prep["P"] == sd.Polynome([-c for c in P]))
                for methode, _, lignes in prep["pas"]:
                    for e, _ in lignes:
                        D = sd.vers_polynome(expr.Op("-", e.g, e.d), x)
                        self.assertTrue(D == P or D == sd.Polynome([-c for c in P]), (nom, tex_element(e)))
        ancien = sd._ecrire_entrees
        try:
            sd._ecrire_entrees = lambda entrees, X, dec: ancien(entrees[:-1] or entrees, X, dec)
            self.assertEqual(resoudre(P3["(x + 1)(x + 3) = 15"])["statut"], "ne_conclut_pas")
        finally:
            sd._ecrire_entrees = ancien
        self.assertEqual(resoudre(P3["(x + 1)(x + 3) = 15"])["statut"], "resolu")


# ---------------------------------------------------------------------------------------------------------------------------
# P4a : formes structurées, sur l'arbre avant tout développement (E1.3, E3, E5, E13)
# ---------------------------------------------------------------------------------------------------------------------------
ATTENTION = (r"Attention : on ne divise pas par \(%s\), car ce facteur peut être nul ! On ramène tout dans le membre de gauche, "
             r"puis on met \(%s\) en évidence.")


class TestStructures(unittest.TestCase):

    def test_2_9_k_car(self):
        """Corrigé 2.9 k : ramener sans développer (E1.3) ; la ligne « Id. rem. … (car A² = 4(x − 2)²) » avant la chaîne (E5), A et B
        dans un seul cadre (D29) ; (2(x − 2) + 1)(2(x − 2) − 1), puis les parenthèses enlevées, puis les facteurs réduits."""
        res = resoudre(P4A["2.9 k"])
        self.assertEqual(textes(res), [
            r" | 4(x - 2)^{2} = 1 | ",
            r"\iff | 4(x - 2)^{2} - 1 = 0 | ",
            r"Id. rem. \(A^{2} - B^{2}\) avec \(\fbox{$A = 2(x - 2),\ B = 1$}\) (car \(A^{2} = 4(x - 2)^{2}\)).",
            r"\iff | (2(x - 2) + 1)(2(x - 2) - 1) = 0 | ",
            r"\iff | (2x - 4 + 1)(2x - 4 - 1) = 0 | ",
            r"\iff | (2x - 3)(2x - 5) = 0 | ",
            r"\iff | " + ou("2x - 3 = 0", "2x - 5 = 0") + " | produit nul",
            r"\iff | " + ou(r"x = \frac{3}{2}", r"x = \frac{5}{2}") + " | "])
        self.assertEqual(res["S"], r"S = \{\frac{3}{2}\,;\,\frac{5}{2}\}")
        self.assertEqual([(e["phase"], e["methode"], e["cible"]) for e in res["etapes"]], [
            ("ramener", "RAMENER", "4(x - 2)^{2} = 1"), ("factoriser", "IDREM_DIFF", "4(x - 2)^{2} - 1"),
            ("produit_nul", "PRODUIT_NUL", "(2x - 3)(2x - 5)")])
        p = res["etapes"][1]["parametres"]
        self.assertEqual((p["A"], p["B"], p["forme"]), ("2(x - 2)", "1", "structuree"))
        self.assertEqual(res["variantes"], [])

    def test_2_9_l_etiquette_sans_ligne_intermediaire(self):
        """Corrigé 2.9 l : étiquette en marge ; ((x + 1) + 4)((x + 1) − 4) donne directement (x + 5)(x − 3) (aucun « − » devant une
        parenthèse, √k = 1)."""
        self.assertEqual(textes(resoudre(P4A["2.9 l"])), [
            r" | (x + 1)^{2} = 16 | ",
            r"\iff | (x + 1)^{2} - 16 = 0 | ",
            r"\iff | ((x + 1) + 4)((x + 1) - 4) = 0 | Id. rem. \(A^{2} - B^{2}\) avec \(\fbox{$A = x + 1,\ B = 4$}\)",
            r"\iff | (x + 5)(x - 3) = 0 | ",
            r"\iff | " + ou("x + 5 = 0", "x - 3 = 0") + " | produit nul",
            r"\iff | " + ou("x = -5", "x = 3") + " | "])

    def test_2_12_h_ordre_du_facteur_reduit(self):
        """Corrigé 2.12 h : A = 4, B = 3x + 2 ; « 4 − (3x + 2) » puis « 4 − 3x − 2 » ; (3x + 6)(2 − 3x) (E5 : la constante d'abord
        quand le coefficient de x est négatif et la constante positive), sans ME après coup ; second membre déjà nul : pas de ligne
        ramenée. Écart au corrigé : A et B en étiquette (E5), pas en ligne de texte."""
        res = resoudre(P4A["2.12 h"])
        self.assertEqual(textes(res), [
            r" | 16 - (3x + 2)^{2} = 0 | ",
            r"\iff | (4 + (3x + 2))(4 - (3x + 2)) = 0 | Id. rem. \(A^{2} - B^{2}\) avec \(\fbox{$A = 4,\ B = 3x + 2$}\)",
            r"\iff | (4 + 3x + 2)(4 - 3x - 2) = 0 | ",
            r"\iff | (3x + 6)(2 - 3x) = 0 | ",
            r"\iff | " + ou("3x + 6 = 0", "2 - 3x = 0") + " | produit nul",
            r"\iff | " + ou("x = -2", r"x = \frac{2}{3}") + " | "])
        self.assertEqual(res["etapes"][0]["phase"], "factoriser")

    def test_2_12_e_facteur_commun(self):
        """Corrigé 2.12 e : l'avertissement (E3), « g − d = 0 », la ME avec un crochet, les parenthèses enlevées, −2x − 1 (E5),
        solutions dans l'ordre des facteurs (D14)."""
        res = resoudre(P4A["2.12 e"])
        self.assertEqual(textes(res), [
            r" | (x - 1)(2 - x) = (x - 1)(x + 3) | ",
            ATTENTION % ("(x - 1)", "(x - 1)"),
            r"\iff | (x - 1)(2 - x) - (x - 1)(x + 3) = 0 | ",
            r"\iff | (x - 1)[(2 - x) - (x + 3)] = 0 | ME",
            r"\iff | (x - 1)(2 - x - x - 3) = 0 | ",
            r"\iff | (x - 1)(-2x - 1) = 0 | ",
            r"\iff | " + ou("x - 1 = 0", "-2x - 1 = 0") + " | produit nul",
            r"\iff | " + ou("x = 1", r"x = -\frac{1}{2}") + " | "])
        self.assertEqual(res["S"], r"S = \{-\frac{1}{2}\,;\,1\}")
        self.assertEqual([(e["phase"], e["methode"]) for e in res["etapes"]], [
            ("ramener", "RAMENER"), ("factoriser", "ME"), ("produit_nul", "PRODUIT_NUL")])
        self.assertEqual(sd.blocs(res)[0]["rangees"][0], {"texte": ATTENTION % ("(x - 1)", "(x - 1)")})
        self.assertEqual(sd.blocs(res)[0]["rangees"][1]["gauche"], "(x - 1)(2 - x) = (x - 1)(x + 3)")

    def test_az_4_1_d_produit_deja_nul(self):
        """E13 : produit nul direct, sans développer ; facteurs écrits comme dans la saisie (2 − x = 0), dans l'ordre écrit (D14) ;
        les produits écrits côte à côte comme le corrigé (expr.tex écrirait « (x − 1)(2 − x) · (5 − 3x) »)."""
        res = resoudre(P4A["Az 4.1 d"])
        self.assertEqual(textes(res), [
            r" | (x - 1)(2 - x)(5 - 3x) = 0 | ",
            r"\iff | " + ou("x - 1 = 0", "2 - x = 0", "5 - 3x = 0") + " | produit nul",
            r"\iff | " + ou("x = 1", "x = 2", r"x = \frac{5}{3}") + " | "])
        self.assertEqual(res["S"], r"S = \{1\,;\,\frac{5}{3}\,;\,2\}")
        self.assertEqual([(e["phase"], e["methode"]) for e in res["etapes"]], [("produit_nul", "PRODUIT_NUL")])

    def test_produit_deja_nul_autres_formes(self):
        """D24 (un carré réécrit (B)(B), le facteur une seule fois), constante « impossible » (−1, 0,5 de la saisie gardé), monôme
        (D7), premier membre nul (E1), D20."""
        self.assertEqual(textes(resoudre(P4A["E13 constante et carré"])), [
            r" | 3(x + 1)^{2} = 0 | ", r"\iff | 3(x + 1)(x + 1) = 0 | ",
            r"\iff | " + ou(IMP % "3", "x + 1 = 0") + " | produit nul", r"\iff | x = -1 | "])
        self.assertEqual(textes(resoudre(P4A["E13 carré, D24"])),
                         [r" | (t + 10)^{2} = 0 | ", r"\iff | (t + 10)(t + 10) = 0 | ", r"\iff | t + 10 = 0 | produit nul",
                          r"\iff | t = -10 | "])
        self.assertEqual(textes(resoudre(P4A["E13 −1 impossible"]))[1],
                         r"\iff | " + ou(IMP % "-1", "x - 1 = 0", "x + 2 = 0") + " | produit nul")
        self.assertEqual(textes(resoudre(P4A["E13 décimaux"]))[1],
                         r"\iff | " + ou(IMP % "0{,}5", "x - 1 = 0", "x + 2 = 0") + " | produit nul")
        self.assertEqual(textes(resoudre(P4A["E13 monôme 2x"]))[1:], [
            r"\iff | " + ou("2x = 0", "x - 3 = 0") + " | produit nul", r"\iff | " + ou("x = 0", "x = 3") + " | "])
        res = resoudre(P4A["E13 premier membre nul"])
        self.assertEqual(textes(res)[:2], [r" | 0 = (x - 3)(2x + 1) | ", r"\iff | (x - 3)(2x + 1) = 0 | "])
        self.assertEqual(res["etapes"][0]["parametres"]["cote"], "droite")
        self.assertEqual(textes(resoudre(P4A["E13 D20"]))[2:], [
            r"\iff | " + ou(r"2x = \frac{1}{3}", "x = -1") + " | ", r"\iff | " + ou(r"x = \frac{1}{6}", "x = -1") + " | "])
        self.assertEqual(textes(resoudre(P4A["E13 carré et facteur"]))[1], r"\iff | (x + 1)(x + 1)(x - 2) = 0 | ")

    def test_id_rem_structuree_autres_formes(self):
        """B = √5 (D8) et ≈ (E14) ; B² justifié aussi (deux carrés) ; constantes regroupées sur leur ligne ; A constant écrit après
        le carré ; un facteur réduit monôme écrit en tête (x(x + 2)) ; constante nulle : produit nul direct (D24)."""
        res = resoudre(P4A["E5 B irrationnel"])
        self.assertEqual(textes(res)[2:4], [
            r"\iff | ((x + 1) + \sqrt{5})((x + 1) - \sqrt{5}) = 0 | Id. rem. \(A^{2} - B^{2}\) avec \(\fbox{$A = x + 1,\ B = \sqrt{5}$}\)",
            r"\iff | (x + 1 + \sqrt{5})(x + 1 - \sqrt{5}) = 0 | "])
        self.assertEqual(res["S"], r"S = \{-1 - \sqrt{5}\,;\,-1 + \sqrt{5}\}")
        self.assertEqual(res["approx"], r"soit \(x \approx -3{,}236\) ou \(x \approx 1{,}236\)")
        self.assertEqual(textes(resoudre(P4A["E5 deux carrés, car"]))[2:6], [
            r"Id. rem. \(A^{2} - B^{2}\) avec \(\fbox{$A = 2(x + 1),\ B = 3(x - 2)$}\) (car \(A^{2} = 4(x + 1)^{2}\) et "
            r"\(B^{2} = 9(x - 2)^{2}\)).",
            r"\iff | (2(x + 1) + 3(x - 2))(2(x + 1) - 3(x - 2)) = 0 | ",
            r"\iff | (2x + 2 + 3x - 6)(2x + 2 - 3x + 6) = 0 | ",
            r"\iff | (5x - 4)(8 - x) = 0 | "])
        self.assertEqual(textes(resoudre(P4A["E5 constantes regroupées"]))[:3], [
            r" | (x + 1)^{2} + 3 = 19 | ", r"\iff | (x + 1)^{2} + 3 - 19 = 0 | ", r"\iff | (x + 1)^{2} - 16 = 0 | "])
        self.assertEqual(textes(resoudre(P4A["E5 A constant, écrit après"]))[1],
                         r"\iff | (2 + (x + 1))(2 - (x + 1)) = 0 | Id. rem. \(A^{2} - B^{2}\) avec \(\fbox{$A = 2,\ B = x + 1$}\)")
        self.assertEqual(textes(resoudre(P4A["E5 facteur monôme"]))[3:], [
            r"\iff | x(x + 2) = 0 | ", r"\iff | " + ou("x = 0", "x + 2 = 0") + " | produit nul",
            r"\iff | " + ou("x = 0", "x = -2") + " | "])
        self.assertEqual(textes(resoudre(P4A["E5 décimaux"]))[2],
                         r"Id. rem. \(A^{2} - B^{2}\) avec \(\fbox{$A = 0{,}5(x + 1),\ B = 1$}\) (car \(A^{2} = 0{,}25(x + 1)^{2}\)).")
        self.assertEqual(textes(resoudre(P4A["E5 constante nulle, D24"]))[2:], [
            r"\iff | (x + 1)^{2} = 0 | ", r"\iff | (x + 1)(x + 1) = 0 | ", r"\iff | x + 1 = 0 | produit nul", r"\iff | x = -1 | "])

    def test_facteur_commun_autres_formes(self):
        """E3 : une somme seule à droite ; « − » devant la droite (on ajoute) ; un reste monôme (crochet sans parenthèses) ; la
        solution répétée écrite une fois."""
        self.assertEqual(textes(resoudre(P4A["E3 somme seule à droite"]))[2:5], [
            r"\iff | (x - 1)(x + 2) - (x - 1) = 0 | ", r"\iff | (x - 1)[(x + 2) - 1] = 0 | ME", r"\iff | (x - 1)(x + 2 - 1) = 0 | "])
        self.assertEqual(textes(resoudre(P4A["E3 « − » devant la droite"]))[2:4], [
            r"\iff | (x - 1)(x + 2) + (x - 1)(x + 3) = 0 | ", r"\iff | (x - 1)[(x + 2) + (x + 3)] = 0 | ME"])
        self.assertEqual(textes(resoudre(P4A["E3 monôme et constante"]))[3:5], [
            r"\iff | (x - 3)[x - 2] = 0 | ME", r"\iff | (x - 3)(x - 2) = 0 | "])
        self.assertEqual(textes(resoudre(P4A["E3 solution répétée"]))[-1], r"\iff | x = -1 | ")
        self.assertEqual(textes(resoudre(P4A["E3 facteur à droite d'abord"]))[3:6], [
            r"\iff | (x + 1)[3 - (x - 2)] = 0 | ME", r"\iff | (x + 1)(3 - x + 2) = 0 | ", r"\iff | (x + 1)(5 - x) = 0 | "])

    def test_aucune_variante_ni_developpement(self):
        """E1.3 : rien n'est développé (aucune étape DEVELOPPER) ; pas de variante « formule » (elle demanderait de développer)."""
        for nom, saisie in P4A.items():
            with self.subTest(nom=nom):
                res = resoudre(saisie)
                self.assertEqual(res["statut"], "resolu")
                self.assertEqual(res["variantes"], [])
                self.assertFalse(any(e["methode"] == "DEVELOPPER" for e in res["etapes"]))

    def test_enonce_ecrit_comme_le_corrigé(self):
        """Les produits de l'énoncé côte à côte (`Juxtaposition`) ; seulement sur une forme structurée (les énoncés de P2b et P3
        restent ceux d'expr.tex, instantanés inchangés)."""
        T = lambda s: tex_element(sd.ecrire_enonce(*lire(s)[:3]))
        self.assertEqual(T("(x-1)(2-x)(5-3x)=0"), "(x - 1)(2 - x)(5 - 3x) = 0")
        self.assertEqual(T("2x(x-3)=0"), "2x(x - 3) = 0")
        self.assertEqual(T("(1/4)(x+1)^2=1"), r"\frac{1}{4}(x + 1)^{2} = 1")
        self.assertEqual(T("x*3*(x+1)=0"), r"x \cdot 3(x + 1) = 0")
        self.assertEqual(T("(3/2)x^2=4x+1"), expr.tex(lire("(3/2)x^2=4x+1")[0]) + " = 4x + 1")

    def test_chaque_ligne_relue(self):
        """Garde-fou (principe 1) : chaque ligne écrite (l'énoncé réécrit compris) est relue dans Q(√m) et vaut ±(gauche − droite) ;
        une ligne faussée exprès (facteur réduit, reste du facteur commun, énoncé) donne « ne_conclut_pas » (jamais un résultat
        douteux)."""
        for nom, saisie in P4A.items():
            g, d, x, _ = lire(saisie)
            P = sd.en_nombres(polynome(saisie))
            moins = sd.en_nombres([-c for c in P])
            res = resoudre(saisie)
            with self.subTest(nom=nom):
                for e in res["etapes"]:
                    seg = e["segment"]
                    for el in (seg.elements if seg else []):            # l'énoncé (pivot du premier segment) compris
                        if isinstance(el, Eq) and (e["phase"] != "produit_nul" or isinstance(el.g, sd.Juxtaposition)):
                            D = sd._nadd(sd._ecrit_en_nombres(el.g, x), sd._ecrit_en_nombres(el.d, x), -1)
                            self.assertIn(D, (P, moins), (nom, tex_element(el)))
        for nom, cible in (("2.9 k", "_facteur_reduit"), ("2.12 e", "_reste_ecrit"), ("Az 4.1 d", "_juxtaposer")):
            ancien = getattr(sd, cible)
            fausse = {"_facteur_reduit": lambda f, X, dec: ancien(sd.en_nombres([f[0] + 1, f[1]]), X, dec),
                      "_reste_ecrit": lambda lu, X, dec: ancien((lu[0] * 2,) + tuple(lu[1:]), X, dec),
                      "_juxtaposer": lambda n: expr.Op("+", ancien(n), expr.Nb(1)) if isinstance(n, expr.Op) and n.op == "*"
                      else ancien(n)}[cible]
            with self.subTest(fausse=cible):
                try:
                    setattr(sd, cible, fausse)
                    self.assertEqual(resoudre(P4A[nom])["statut"], "ne_conclut_pas")
                finally:
                    setattr(sd, cible, ancien)
                self.assertEqual(resoudre(P4A[nom])["statut"], "resolu")


# ---------------------------------------------------------------------------------------------------------------------------
# P4b : degrés ≠ 2, degré 1, identité et égalité fausse, formes structurées laissées à P4b
# ---------------------------------------------------------------------------------------------------------------------------
DELTA = r" | \Delta = b^{2} - 4ac = %s = \fbox{$%s$} | "


class TestDegres(OracleMixin, unittest.TestCase):

    def test_2_12_c_comme_le_corrige(self):
        """Corrigé 2.12 c : ME de x, puis Id. rem. sur le facteur (le produit écrit garde x devant), produit nul à trois facteurs,
        solutions dans l'ordre des facteurs (D14). Écarts voulus : étiquettes D5 (« Id. rem. A² − B² avec … », « produit nul »), A et
        B encadrés (D29)."""
        res = resoudre(P4B["2.12 c"])
        self.assertEqual(textes(res), [
            r" | x^{3} - x = 0 | ",
            r"\iff | x(x^{2} - 1) = 0 | ME",
            r"\iff | x(x + 1)(x - 1) = 0 | Id. rem. \(A^{2} - B^{2}\) avec \(\fbox{$A = x,\ B = 1$}\)",
            r"\iff | " + ou("x = 0", "x + 1 = 0", "x - 1 = 0") + " | produit nul",
            r"\iff | " + ou("x = 0", "x = -1", "x = 1") + " | "])
        self.assertEqual(res["S"], r"S = \{-1\,;\,0\,;\,1\}")
        self.assertEqual([(e["phase"], e["methode"], e["cible"]) for e in res["etapes"]], [
            ("factoriser", "ME", "x^{3} - x"), ("factoriser", "IDREM_DIFF", "x^{2} - 1"),
            ("produit_nul", "PRODUIT_NUL", "x(x + 1)(x - 1)")])
        self.assertEqual(res["variantes"], ["formule"])                 # E12 : ME de x seulement, puis la formule sur x² − 1

    def test_az_4_1_f_monome(self):
        """E13, D7 : ME de x², « x² = 0 » puis « x = 0 »."""
        self.assertEqual(textes(resoudre(P4B["Az 4.1 f"])), [
            r" | x^{3} + 8x^{2} = 0 | ", r"\iff | x^{2}(x + 8) = 0 | ME",
            r"\iff | " + ou("x^{2} = 0", "x + 8 = 0") + " | produit nul", r"\iff | " + ou("x = 0", "x = -8") + " | "])

    def test_x4_moins_16_d28_et_e9(self):
        """§ 13.4 et point 4 du plan (D28) : Id. rem. de A = x², puis celle de x² − 4 ; le tableau S-P de x² + 4 en échec vient
        ensuite, juste avant le produit nul (E9), puis « Δ < 0 : x² + 4 = 0 n'a aucune solution réelle »."""
        res = resoudre(P4B["x⁴ − 16"])
        self.assertEqual(textes(res), [
            r" | x^{4} - 16 = 0 | ",
            r"\iff | (x^{2} + 4)(x^{2} - 4) = 0 | Id. rem. \(A^{2} - B^{2}\) avec \(\fbox{$A = x^{2},\ B = 4$}\)",
            r"\iff | (x^{2} + 4)(x + 2)(x - 2) = 0 | Id. rem. \(A^{2} - B^{2}\) avec \(\fbox{$A = x,\ B = 2$}\)",
            r"Le trinôme \(x^{2} + 4\) est unitaire : S-P.",
            r"On cherche deux nombres dont le produit vaut \(4\) et la somme vaut \(0\) :",
            "[tableau]",
            sd.PHRASE_SP_ECHEC,
            r"\iff | " + ou("x^{2} + 4 = 0", "x + 2 = 0", "x - 2 = 0") + " | produit nul",
            DELTA % (r"0^{2} - 4 \cdot 1 \cdot 4", "-16"),
            r"\(\Delta < 0\) : \(x^{2} + 4 = 0\) n'a aucune solution réelle.",
            r"\iff | " + ou("x = -2", "x = 2") + " | "])
        self.assertEqual([(e["phase"], e["methode"], e["cible"]) for e in res["etapes"]], [
            ("factoriser", "IDREM_DIFF", "x^{4} - 16"), ("factoriser", "IDREM_DIFF", "x^{2} - 4"), ("factoriser", "SP", "x^{2} + 4"),
            ("produit_nul", "PRODUIT_NUL", "(x^{2} + 4)(x + 2)(x - 2)"), ("delta_valeur", "FORMULE", "x^{2} + 4"),
            ("delta_nombre", "FORMULE", "x^{2} + 4")])
        tableau = [r for r in lignes(res) if isinstance(r, LigneTexte) and isinstance(r.contenu, dict)][0].contenu
        self.assertEqual([l["cases"] for l in tableau["lignes"]], [["1", "4", "5"], ["2", "2", "4"]])
        self.assertFalse(any(l.get("ok") for l in tableau["lignes"]))
        self.assertEqual(res["variantes"], [])

    def test_degre_3_autres_formes(self):
        """ME de −x (pas de « trinôme » en degré 3), ME de x puis S-P sur le facteur (phrase de choix d'après une ME), ME puis la
        formule sur le facteur (E9 ; ≈ en x : les solutions ne sont pas toutes nommées), B = √5 (≈)."""
        t = textes(resoudre(P4B["ME de −x en degré 3"]))
        self.assertEqual(t[1:3], [r"Le coefficient de \(x^{3}\) est négatif : on met d'abord \(-x\) en évidence.",
                                  r"\iff | -x(x^{2} - 1) = 0 | ME"])
        self.assertEqual(t[4], r"\iff | " + ou("-x = 0", "x + 1 = 0", "x - 1 = 0") + " | produit nul")
        t = textes(resoudre(P4B["ME de x, puis S-P"]))
        self.assertEqual(t[2], r"Le trinôme \(x^{2} - 5x + 6\) est unitaire : S-P.")
        self.assertEqual(t[5], r"\iff | x(x - 2)(x - 3) = 0 | ")
        res = resoudre(P4B["ME de x, puis formule (E9)"])
        t = textes(res)
        self.assertEqual(t[6:8], [r"\iff | " + ou("x = 0", "x^{2} - 2x - 2 = 0") + " | produit nul",
                                  DELTA % (r"(-2)^{2} - 4 \cdot 1 \cdot (-2) = 4 + 8", "12")])
        self.assertEqual(t[-1], r"\iff | " + ou("x = 0", r"x = 1 - \sqrt{3}", r"x = 1 + \sqrt{3}") + " | ")
        self.assertEqual(res["approx"], r"soit \(x \approx -0{,}732\) ou \(x = 0\) ou \(x \approx 2{,}732\)")
        self.assertEqual(resoudre(P4B["x³ − 5x"])["approx"], r"soit \(x \approx -2{,}236\) ou \(x = 0\) ou \(x \approx 2{,}236\)")
        t = textes(resoudre(P4B["ME de 2x, puis Id. rem. (carré)"]))
        self.assertEqual(t[3:6], [r"\iff | 2x(x - 1)^{2} = 0 | ", r"\iff | 2x(x - 1)(x - 1) = 0 | ",
                                  r"\iff | " + ou("2x = 0", "x - 1 = 0") + " | produit nul"])

    def test_id_rem_de_a_x2_autres_formes(self):
        """Le carré (x² + 1)² réécrit (D24), puis le S-P en échec et Δ < 0 (S = ∅) ; deux tâtonnements en échec, puis deux formules
        dans l'ordre du produit (E9) ; coefficients non entiers : la formule d'emblée sur le facteur, avec sa phrase."""
        res = resoudre(P4B["Id. rem. de A = x², carré, Δ < 0"])
        t = textes(res)
        self.assertEqual(t[2:4], [r"\iff | (x^{2} + 1)^{2} = 0 | ", r"\iff | (x^{2} + 1)(x^{2} + 1) = 0 | "])
        self.assertEqual(t[-3:], [r"\iff | x^{2} + 1 = 0 | produit nul", DELTA % (r"0^{2} - 4 \cdot 1 \cdot 1", "-4"),
                                  r"\(\Delta < 0\) : \(x^{2} + 1 = 0\) n'a aucune solution réelle."])
        self.assertEqual(res["S"], r"S = \varnothing")
        t = textes(resoudre(P4B["Id. rem. de A = 2x², deux tâtonnements en échec"]))
        self.assertEqual(t[2:6], [r"Le trinôme \(2x^{2} + 3\) n'est pas unitaire : tâtonnement.",
                                  r"On teste les diviseurs de \(3\) (\(\pm 1\), \(\pm 3\)) : aucun n'est solution. On utilise la formule.",
                                  r"Le trinôme \(2x^{2} - 3\) n'est pas unitaire : tâtonnement.",
                                  r"On teste les diviseurs de \(-3\) (\(\pm 1\), \(\pm 3\)) : aucun n'est solution. On utilise la formule."])
        self.assertEqual(t[7:9], [DELTA % (r"0^{2} - 4 \cdot 2 \cdot 3", "-24"),
                                  r"\(\Delta < 0\) : \(2x^{2} + 3 = 0\) n'a aucune solution réelle."])
        t = textes(resoudre(P4B["Id. rem. de A = x², coefficients non entiers"]))
        self.assertIn(r"Les coefficients du trinôme \(x^{2} + \frac{1}{2}\) ne sont pas entiers : on utilise la formule.", t)

    def test_degre_1(self):
        """§ 13.4 : on ramène (E1), puis on isole x en une ligne, ou deux quand le coefficient de x n'est pas ±1 et que la constante
        n'est pas entière (D20) ; la ligne ramenée « x = 0 » suffit (Az 4.1 a)."""
        res = resoudre(P4B["degré 1"])
        self.assertEqual(textes(res), [r" | 2x + 4 = 0 | ", r"\iff | x = -2 | "])
        self.assertEqual([(e["phase"], e["methode"]) for e in res["etapes"]], [("isoler", "ISOLER")])
        self.assertEqual(res["etapes"][0]["parametres"]["solution"], Nombre(-2))
        self.assertEqual(textes(resoudre(P4B["degré 1, D20"])),
                         [r" | 3x + \frac{1}{3} = 0 | ", r"\iff | 3x = -\frac{1}{3} | ", r"\iff | x = -\frac{1}{9} | "])
        self.assertEqual(textes(resoudre(P4B["degré 1, décimaux, D20"]))[1:], [r"\iff | 0{,}5x = 1{,}5 | ", r"\iff | x = 3 | "])
        res = resoudre(P4B["degré 1, côté droit"])
        self.assertEqual(textes(res), [r" | x + 1 = 3x - 5 | ", r"\iff | 2x - 6 = 0 | ", r"\iff | x = 3 | "])
        self.assertEqual([(e["phase"], e["methode"]) for e in res["etapes"]], [("ramener", "RAMENER"), ("isoler", "ISOLER")])
        self.assertEqual(res["etapes"][0]["parametres"]["cote"], "droite")
        res = resoudre(P4B["Az 4.1 a"])
        self.assertEqual(textes(res), [r" | 3x + 9 = 2(x + 4) + 1 | ", r"\iff | 3x + 9 = 2x + 8 + 1 | distribution",
                                       r"\iff | 3x + 9 = 2x + 9 | ", r"\iff | x = 0 | "])
        self.assertEqual(res["S"], r"S = \{0\}")
        res = resoudre("x=0")                                            # rien à transformer : la ligne seule (bloc valide)
        self.assertEqual((textes(res), res["S"]), ([r" | x = 0 | "], r"S = \{0\}"))
        self.assertEqual(sortie.valider(sortie.sortie_ok("x", [sortie.carte("Résolution", sd.blocs(res))])), [])

    def test_identite_et_egalite_fausse(self):
        """E13, § 13.4 : les phrases d'Exp-log, après la ligne des constantes (« 1 = 1 », « 1 = 2 », pas « 0 = 0 » ramené), S = ℝ ou
        S = ∅ ; Az 4.1 g comme le § 7 (rien après « 1 = 1 ») ; forme structurée : « g − d = 0 » sans développer, puis « 0 = 0 »."""
        res = resoudre(P4B["Az 4.1 g"])
        self.assertEqual(textes(res)[-2:], [r"\iff | 1 = 1 | ", sd.PHRASE_IDENTITE])
        self.assertEqual((res["S"], res["solutions"], res["approx"]), (r"S = \mathbb{R}", [], None))
        self.assertEqual([e["methode"] for e in res["etapes"]], ["DEVELOPPER"])
        self.assertEqual(textes(resoudre(P4B["identité"])), [r" | x + 1 = x + 1 | ", r"\iff | 1 = 1 | ", sd.PHRASE_IDENTITE])
        self.assertEqual(textes(resoudre(P4B["identité, double distribution"]))[-2:],
                         [r"\iff | -4 = -4 | ", sd.PHRASE_IDENTITE])
        res = resoudre(P4B["égalité fausse"])
        self.assertEqual(textes(res), [r" | x^{2} + 1 = x^{2} + 2 | ", r"\iff | 1 = 2 | ", sd.PHRASE_EGALITE_FAUSSE])
        self.assertEqual(res["S"], r"S = \varnothing")
        self.assertEqual(textes(resoudre(P4B["égalité fausse, réduction"])),
                         [r" | 2x + 3 - 2x = 0 | ", r"\iff | 3 = 0 | ", sd.PHRASE_EGALITE_FAUSSE])
        res = resoudre(P4B["identité structurée, deux carrés"])
        self.assertEqual(textes(res), [r" | (x + 1)^{2} = (x + 1)^{2} | ", r"\iff | (x + 1)^{2} - (x + 1)^{2} = 0 | ",
                                       r"\iff | 0 = 0 | ", sd.PHRASE_IDENTITE])
        self.assertFalse(any(e["methode"] == "DEVELOPPER" for e in res["etapes"]))
        self.assertEqual(textes(resoudre(P4B["identité structurée, facteur commun"]))[1],
                         r"\iff | (x - 1)(x + 2) - (x - 1)(x + 2) = 0 | ")

    def test_formes_structurees_de_p4b(self):
        """Facteur de degré 2 dans un produit déjà nul : factorisé par le cours sur le produit écrit (Id. rem., D21, S-P en échec et
        E9, Δ < 0), sans développer ; degré 1 une fois factorisée : le facteur constant écrit en tête, « 4 = 0 » impossible."""
        self.assertEqual(textes(resoudre(P4B["E13 facteur de degré 2, Id. rem."])), [
            r" | (x^{2} - 1)(x + 2) = 0 | ",
            r"\iff | (x + 1)(x - 1)(x + 2) = 0 | Id. rem. \(A^{2} - B^{2}\) avec \(\fbox{$A = x,\ B = 1$}\)",
            r"\iff | " + ou("x + 1 = 0", "x - 1 = 0", "x + 2 = 0") + " | produit nul",
            r"\iff | " + ou("x = -1", "x = 1", "x = -2") + " | "])
        self.assertEqual(textes(resoudre(P4B["E13 constante et facteur de degré 2"]))[1],
                         r"\iff | 3(x + 2)(x - 2) = 0 | Id. rem. \(A^{2} - B^{2}\) avec \(\fbox{$A = x,\ B = 2$}\)")
        self.assertEqual(textes(resoudre(P4B["E13 facteur de degré 2, a < 0"]))[1:4], [
            r"Le trinôme n'est pas unitaire (\(a = -1\)) : on met d'abord \(-1\) en évidence.",
            r"\iff | -(x^{2} - 4)(x + 1) = 0 | ME",
            r"\iff | -(x + 2)(x - 2)(x + 1) = 0 | Id. rem. \(A^{2} - B^{2}\) avec \(\fbox{$A = x,\ B = 2$}\)"])
        res = resoudre(P4B["E13 facteur de degré 2, S-P en échec (E9)"])
        t = textes(res)
        self.assertEqual(t[:5], [r"Le trinôme \(x^{2} + x - 1\) est unitaire : S-P.",
                                 r"On cherche deux nombres dont le produit vaut \(-1\) et la somme vaut \(1\) :", "[tableau]",
                                 sd.PHRASE_SP_ECHEC, r" | 3(x^{2} + x - 1) = 0 | "])
        self.assertEqual(t[5], r"\iff | " + ou(IMP % "3", "x^{2} + x - 1 = 0") + " | produit nul")
        self.assertEqual(res["approx"], r"soit \(x_{1} \approx -1{,}618\) et \(x_{2} \approx 0{,}618\)")
        self.assertEqual(textes(resoudre(P4B["E13 facteur de degré 2, Δ < 0"]))[-2:],
                         [r"\(\Delta < 0\) : \(x^{2} + 1 = 0\) n'a aucune solution réelle.", r"\iff | x = 2 | "])
        self.assertEqual(textes(resoudre(P4B["E5 deux carrés, degré 1"]))[2:], [
            r"\iff | ((x + 1) + (x - 3))((x + 1) - (x - 3)) = 0 | Id. rem. \(A^{2} - B^{2}\) avec \(\fbox{$A = x + 1,\ B = x - 3$}\)",
            r"\iff | (x + 1 + x - 3)(x + 1 - x + 3) = 0 | ", r"\iff | 4(2x - 2) = 0 | ",
            r"\iff | " + ou(IMP % "4", "2x - 2 = 0") + " | produit nul", r"\iff | x = 1 | "])
        self.assertEqual(textes(resoudre(P4B["E3 facteur commun, degré 1"]))[4:], [
            r"\iff | (x - 1)(x + 2 - x - 5) = 0 | ", r"\iff | -3(x - 1) = 0 | ",
            r"\iff | " + ou(IMP % "-3", "x - 1 = 0") + " | produit nul", r"\iff | x = 1 | "])
        for nom in [n for n in P4B if n.startswith(("E13", "E5", "E3", "identité structurée"))]:
            with self.subTest(nom=nom):
                self.assertFalse(any(e["methode"] == "DEVELOPPER" for e in resoudre(P4B[nom])["etapes"]))

    def test_messages_definitifs(self):
        """§ 4, § 13.4 : « bicarrée » (statut pas_encore) seulement si ni ME ni Id. rem. ne s'applique ; sinon « hors du cours »."""
        for nom, (saisie, statut) in NON_RESOLUES.items():
            with self.subTest(nom=nom):
                res = resoudre(saisie)
                self.assertEqual((res["statut"], res["message"]), (statut, sd.MESSAGES[statut]))
        self.assertTrue(sd.bicarree(polynome("x^4-5x^2+4=0")))
        for saisie in ("x^4-16=0", "2x^4-10x^2+8=0", "x^4+x^2=0", "x^4-5x^3+4=0", "x^3-x+1=0"):
            with self.subTest(saisie=saisie):
                self.assertFalse(sd.bicarree(polynome(saisie)))

    def test_polynomes_generes_de_degre_3_et_4(self):
        """Les polynômes générés de P1 de degré ≥ 3 (xʲ · trinôme · k, A² − B² de A = x²), écrits développés : résolus (oracle,
        substitution exacte, invariants du § 5, sortie conforme) ou un message définitif (hors du cours, bicarrée), jamais un autre
        statut."""
        for i, P in enumerate(G for G in GENERES if G.degre >= 3):
            g = sd.arbre_polynome(P, "x", i % 3 == 0)
            res = sd.resoudre_equation(g, Nb(0), "x", i % 3 == 0)
            with self.subTest(i=i, P=P):
                self.assertIn(res["statut"], ("resolu", "hors_cours", "pas_encore", "forme_non_traitee"))
                if res["statut"] != "resolu":
                    self.assertEqual(res["statut"] == "pas_encore", sd.bicarree(P))
                    if res["statut"] == "hors_cours":
                        self.assertTrue(sd.hors_du_cours(P, sd.chemin(P)))
                    continue
                self.assertSolutionsOracle(P, res["solutions"], f"généré {i}")
                for x in res["solutions"]:
                    self.assertEqual(evaluer(P, x), (0, 0))
                self.assertEqual(replier(res), lignes(res))
                s_ = sortie.sortie_ok("x", [sortie.carte("Résolution", sd.blocs(res))])
                self.assertEqual(sortie.valider(s_), [])

    def test_chaque_produit_ecrit_relu(self):
        """Garde-fou (principe 1) : chaque produit écrit d'un degré ≥ 3 est relu dans Q(√m) et vaut P ; un facteur écrit faussé exprès
        donne « ne_conclut_pas » ; chaque ligne d'un produit relue (ligne ⇔ d'une factorisation) vaut ±P."""
        for nom, saisie in P4B.items():
            P = sd.en_nombres(polynome(saisie))
            moins = sd.en_nombres([-c for c in P])
            g, d, x, _ = lire(saisie)
            for e in resoudre(saisie)["etapes"]:
                if e["phase"] == "factoriser" and e["segment"] is not None:
                    for el in e["segment"].elements[1:]:
                        with self.subTest(nom=nom, ligne=tex_element(el)):
                            D = sd._nadd(sd._ecrit_en_nombres(el.g, x), sd._ecrit_en_nombres(el.d, x), -1)
                            self.assertIn(D, (P, moins))
        ancien = sd._arbre_facteur
        try:
            sd._arbre_facteur = lambda f, X, dec: ancien(sd.en_nombres([f[0] + 1] + list(f[1:])) if len(f) == 3 else f, X, dec)
            for nom in ("x⁴ − 16", "E13 facteur de degré 2, a < 0"):
                self.assertEqual(resoudre(P4B[nom])["statut"], "ne_conclut_pas")
        finally:
            sd._arbre_facteur = ancien
        self.assertEqual(resoudre(P4B["x⁴ − 16"])["statut"], "resolu")


class TestNonResolu(unittest.TestCase):

    def test_aucun_statut_temporaire(self):
        """P4b : plus aucun statut temporaire (« non_traite ») ; chaque entrée analysable a une résolution ou un message définitif du
        § 4 et du § 13.5 (bicarrée, hors du cours, ne conclut pas, bornes), sans étape ni S ; toutes les parties d'A_VENIR sont
        faites. Une autre lettre que l'inconnue (la saisie la refuse avant, P3) : ValueError."""
        self.assertNotIn("non_traite", sd.MESSAGES)
        self.assertEqual(set(sd.MESSAGES), {"hors_cours", "ne_conclut_pas", "hors_bornes", "pas_encore", "forme_non_traitee"})
        self.assertEqual(sd.MESSAGES["pas_encore"], MESSAGE_BICARREE)
        self.assertEqual({partie for _, partie, _, _, _ in A_VENIR.values()} - set(PARTIES_FAITES), set())
        saisies = [(nom, s_, "resolu") for nom, s_ in RESOLUES.items()] + [(nom, s_, st) for nom, (s_, st) in NON_RESOLUES.items()]
        saisies += [(s_, s_, "forme_non_traitee") for s_ in STRUCTURES_NON_ECRITES]
        for nom, saisie, statut in saisies:
            with self.subTest(nom=nom):
                res = resoudre(saisie)
                self.assertEqual(res["statut"], statut)
                if statut != "resolu":
                    self.assertEqual(res["message"], sd.MESSAGES[statut])
                    self.assertEqual((res["etapes"], res["solutions"], res["S"], res["approx"]), ([], [], None, None))
                    with self.assertRaises(ValueError):
                        sd.blocs(res)
        for saisie in ("x^2+y=0", "x^2=y"):
            g, d = expr.lire_membres(saisie)
            with self.assertRaises(ValueError):
                sd.resoudre_equation(g, d, "x")

    def test_structures_sans_developper(self):
        """E1.3 : quand une structure s'applique sans développer (produit nul direct, facteur commun aux deux membres, Id. rem. sur
        une forme structurée), on ne développe pas (`ramener` rend None) : l'outil la résout, ou, s'il ne l'écrit pas, « hors du
        cours » (jamais développée). Sinon, on développe (E2)."""
        oui = ("4(x-2)^2=1", "(x+1)^2=16", "16-(3x+2)^2=0", "(x-1)(2-x)=(x-1)(x+3)", "(x-1)(2-x)(5-3x)=0", "x(x+1)=0",
               "3(x+1)^2=0", "(x+1)^2=(2x-3)^2", "(x-1)(x+2)=x-1", "-(x+1)^2+4=0", "(x+1)^2=5", "2(x-1)=3(1-x)(x+2)",
               "(x^2-1)(x+2)=0", "3(x^2-4)=0", "(x+1)^2=(x-3)^2", "(x-1)(x+2)=(x-1)(x+5)", "(x+1)^2=(x+1)^2")   # P4b
        non = ("(x+1)(x+3)=15", "(x+1)^2=-16", "(2x-1)^2-4x(x-1)=1", "x(x-4)=5", "(x+1)^2+(x-1)^2=10", "(x+1)^2=2x+14",
               "x^2+7x=18", "5-(x+1)(x+3)=0")
        for saisie in oui + non + tuple(STRUCTURES_NON_ECRITES):
            g, d, x, _ = lire(saisie)
            with self.subTest(saisie=saisie):
                self.assertEqual(sd.forme_structuree(g, d, x), saisie not in non)
                if saisie in non:
                    continue
                self.assertIsNone(sd.ramener(g, d, x))
                res = resoudre(saisie)
                if saisie in STRUCTURES_NON_ECRITES:
                    self.assertEqual((res["statut"], res["message"], res["etapes"]),
                                     ("forme_non_traitee", sd.MESSAGES["forme_non_traitee"], []))
                else:
                    self.assertEqual(res["statut"], "resolu")
                    self.assertFalse(any(e["methode"] == "DEVELOPPER" for e in res["etapes"]))

    def test_hors_de_ce_que_e2_developpe(self):
        """E2 ne développe que nombre ou monôme × parenthèse, deux parenthèses, le carré d'un binôme ; le reste reçoit « Cette forme
        d'équation n'est pas traitée par l'outil. », sans étape (P5, question 29 de suivi.md : « hors du cours » y serait faux) ; un
        degré 3 sans ME ni Id. rem. reçoit « hors du cours » (vrai). Ce qui n'est pas de degré 2 une fois ramené est résolu (P4b) :
        degré 1 (isoler), identité."""
        for saisie in ("2(x+1)(x+3)=5", "0,5(x+2)^2=x+3", "(x+1)^3=8+x", "x*3+x^2=1", "(x^2+x+1)^2=x", "x^2/2=1+x", "x^3=x+1"):
            with self.subTest(saisie=saisie):
                g, d, x, _ = lire(saisie)
                if saisie != "x^3=x+1":
                    self.assertIsNone(sd.ramener(g, d, x))
                res = resoudre(saisie)
                self.assertEqual((res["statut"], res["etapes"]), ("hors_cours" if saisie == "x^3=x+1" else "forme_non_traitee", []))
        for saisie, S in (("(x+1)(x+3)=x^2", r"S = \{-\frac{3}{4}\}"), ("x^2+1=x^2+x", r"S = \{1\}"),
                          ("(x+2)(x-2)=x^2-4", r"S = \mathbb{R}")):
            with self.subTest(saisie=saisie):
                res = resoudre(saisie)
                self.assertEqual((res["statut"], res["S"]), ("resolu", S))
                self.assertEqual(res["etapes"][0]["methode"], "DEVELOPPER" if "(" in saisie else "RAMENER")

    def test_hors_du_cours_seulement_si_vrai(self):
        """P5 (question 29 ; CLAUDE.md, rien de faux à l'écran) : « hors du cours » seulement pour un polynôme développé de degré ≥ 3,
        à coefficients entiers, qui n'est pas une bicarrée et sur lequel le chemin du cours (D28) n'a fait au plus qu'une ME de
        constante, le reste n'étant pas une bicarrée ; tout cas douteux (ME de xʲ, Id. rem. puis un facteur de degré ≥ 3, ME puis
        bicarrée, coefficients non entiers) et toute forme que l'outil n'écrit pas : « forme_non_traitee »."""
        for P, attendu in (([-1, -1, 0, 1], True), ([2, 2, 0, 2], True), ([10, -21, 14, -3], True), ([8, 0, -10, 0, 2], False),
                           ([-64, 0, 0, 0, 0, 0, 1], False), ([0, -2, 0, F(1, 2)], False), ([4, 0, -5, 0, 1], False),
                           ([-4, 0, 5, 0, -1], False), ([0, 4, 0, -5, 0, 1], False), ([1, 1, 0, 0, 1], True), ([0, 1, 0, 0, 1], False)):
            with self.subTest(P=P):
                ch = sd.chemin(sd.Polynome(P))
                self.assertEqual(ch["statut"], "hors_cours")
                self.assertEqual(sd.hors_du_cours(P, ch), attendu)
                g = sd.arbre_polynome(sd.Polynome(P), "x", False)
                self.assertEqual(sd.resoudre_equation(g, Nb(0), "x")["statut"],
                                 "pas_encore" if sd.bicarree(P) else "hors_cours" if attendu else "forme_non_traitee")
        for nom, (saisie, statut) in NON_RESOLUES.items():
            with self.subTest(nom=nom):
                res = resoudre(saisie)
                self.assertEqual(res["message"], sd.MESSAGES[statut])
                if statut == "hors_cours":
                    P = polynome(saisie)
                    if P[-1] < 0:
                        P = sd.Polynome([-c for c in P])
                    self.assertTrue(P.degre >= 3 and P.entiers() and not sd.bicarree(P))
                    self.assertTrue(all(e["methode"] == "ME" and e["resultat"]["j"] == 0 for e in sd.chemin(P)["etapes"]))
        self.assertEqual(sd.MESSAGES["forme_non_traitee"], "Cette forme d'équation n'est pas traitée par l'outil.")

    def test_bornes(self):
        """§ 13.5 : un radicande trop grand pour la simplification (question 9 de suivi.md) donne le message des bornes."""
        g, d = expr.lire_membres("(1/9999999)x^2+x+1=0")
        res = sd.resoudre_equation(g, d, "x")
        self.assertEqual((res["statut"], res["message"]), ("hors_bornes", "Cette équation dépasse ce que l'outil sait traiter."))


# ---------------------------------------------------------------------------------------------------------------------------
# Les formes que P2b ne traitait pas (A_VENIR) : toutes traitées (P3, P4a, P4b) ; aucun xfail
# ---------------------------------------------------------------------------------------------------------------------------
def _a_venir():
    """Les formes d'A_VENIR ; celles d'une partie pas encore faite (hors de PARTIES_FAITES) seraient des xfail stricts (aucune
    depuis P4b)."""
    for nom, (saisie, partie, coeffs, S, quoi) in A_VENIR.items():
        ascii_ = unicodedata.normalize("NFKD", nom).encode("ascii", "ignore").decode()
        marques = [] if partie in PARTIES_FAITES else [pytest.mark.xfail(strict=True, reason=f"{partie} : {quoi} (plan, {partie})")]
        yield pytest.param(saisie, coeffs, S, id=partie + "-" + re.sub(r"[^A-Za-z0-9.]+", "_", ascii_).strip("_"), marks=marques)


@pytest.mark.parametrize("saisie, coeffs, S", list(_a_venir()))
def test_a_venir(saisie, coeffs, S):
    res = resoudre(saisie)
    assert res["statut"] == "resolu"
    if S is not None:
        assert res["S"] == S
        return
    attendues = [r for r, _ in oracle.racines(coeffs)]
    assert len(attendues) == len(res["solutions"])
    with mp.workdps(60):
        for x, r in zip(res["solutions"], attendues):
            assert abs(valeur_mp(x) - r) <= mp.mpf(10) ** -40 * max(1, abs(r))


def test_P4b_bicarree():
    """§ 4, § 13.4 : le message « bicarrée » si ni ME ni Id. rem. ne s'applique (x⁴ − 5x² + 4)."""
    res = resoudre("x^4-5x^2+4=0")
    assert (res["statut"], res["message"]) == ("pas_encore", MESSAGE_BICARREE)
