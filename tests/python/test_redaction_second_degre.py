"""Brique moteur/second_degre.py, P2b et P3 du chantier equations-2e-degre : la rédaction (decisions.md §§ 3, 5, 6, 7 et 13 ; plan,
P2b et P3).

- Invariants du § 5 : le bloc affiché est `bloc_rangees(concaténation des lignes de toutes les étapes, membre_gauche=True)` (JSON) ;
  les segments des étapes, mis bout à bout, donnent les rangées de la chaîne entière (`rangees_chaine`) ; chaque segment commence
  par le pivot (le dernier élément écrit) et n'a que des ⇔ ; l'énoncé n'est écrit qu'une fois, et seulement si un ⇔ suit (§ 13.3).
- Oracle (`oracle.racines`) sur toutes les solutions du corpus (`corpus_second_degre.RESOLUES`), des variantes « formule » (E12) et des
  polynômes générés de P1 ; chaque solution est substituée exactement dans l'équation (calcul écrit ici).
- Rédaction : le texte rendu de 2.11 h, 2.10 a, Javet 2.17 c et des exemples du § 7 ; E3 à E12, E14 ; D20, D24, D29 ; cas limites
  du § 6 ; vouvoiement (R12) et vocabulaire (C6) de tout texte produit.
- `nb_exact` sans état, croisé avec `exp_log._nb_exact` ; `appliquer` : s_applique ⇔ une étape, qui se redéveloppe.
- P3 : E1 (ramener, réordonner, côté droit, phrase seulement avant une phrase de choix) et E2 (développer en montrant les produits,
  « − (…) » puis sans parenthèses) ; les formes structurées (P4a) restent « non_traite ».
- Ce qui n'est pas encore traité : xfail stricts nommés par leur partie (P4a, P4b)."""
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
from corpus_second_degre import A_VENIR, MESSAGE_BICARREE, P2B, P3, PARTIES_FAITES, RESOLUES
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
ENONCES = {nom: tex_element(Eq(*lire(RESOLUES[nom.replace(" (variante formule)", "")])[:2]), True, True) for nom, _ in TOUTES}
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


# ---------------------------------------------------------------------------------------------------------------------------
# Oracle et garde-fou
# ---------------------------------------------------------------------------------------------------------------------------
class TestOracle(OracleMixin, unittest.TestCase):

    def test_corpus_et_variantes(self):
        """Solutions = oracle.racines, et chacune annule exactement l'équation (S, ligne ≈ comprise)."""
        for nom, res in TOUTES:
            saisie = RESOLUES[nom.replace(" (variante formule)", "")]
            with self.subTest(nom=nom):
                P = polynome(saisie)
                self.assertEqual(res["statut"], "resolu")
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
            sd.MESSAGES["non_traite"] = ""


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
        parenthèses, puis 1 = 1 ; l'identité elle-même vient en P4b (le test xfail « P4b » de A_VENIR)."""
        g, d = expr.lire_membres("(2x-1)^2-4x(x-1)=1")
        prep = sd.ramener(g, d, "x")
        self.assertTrue(prep["P"].nul())
        methode, parametres, lignes = prep["pas"][0]
        self.assertEqual(methode, "DEVELOPPER")
        self.assertEqual([(tex_element(e), p) for e, p in lignes], [
            ("4x^{2} - 4x + 1 - (4x^{2} - 4x) = 1", r"Id. rem. \((A - B)^{2}\) avec \(A = 2x,\ B = 1\) ; distribution"),
            ("4x^{2} - 4x + 1 - 4x^{2} + 4x = 1", None), ("1 = 1", None)])
        self.assertEqual(resoudre("(2x-1)^2-4x(x-1)=1")["statut"], "non_traite")

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


class TestNonResolu(unittest.TestCase):

    def test_formes_pas_encore_traitees(self):
        """Ce qui n'est pas encore traité (parties hors de PARTIES_FAITES) donne « non_traite », avec un message clair, sans aucune
        étape (jamais un résultat douteux)."""
        for nom, (saisie, partie, _, _, _) in A_VENIR.items():
            if partie in PARTIES_FAITES:
                continue
            with self.subTest(nom=nom, partie=partie):
                res = resoudre(saisie)
                self.assertEqual(res["statut"], "non_traite")
                self.assertEqual(res["message"], sd.MESSAGES["non_traite"])
                self.assertEqual((res["etapes"], res["solutions"], res["S"], res["approx"]), ([], [], None, None))
                with self.assertRaises(ValueError):
                    sd.blocs(res)
        for saisie in ("x^2+y=0", "x^2=y"):
            g, d = expr.lire_membres(saisie)
            self.assertEqual(sd.resoudre_equation(g, d, "x")["statut"], "non_traite")

    def test_structures_laissees_a_p4a(self):
        """E1.3 : quand une structure s'applique sans développer (produit nul direct, facteur commun aux deux membres, Id. rem. sur
        une forme structurée), P3 ne développe pas : « non_traite » jusqu'en P4a. Sinon, on développe (E2)."""
        oui = ("4(x-2)^2=1", "(x+1)^2=16", "16-(3x+2)^2=0", "(x-1)(2-x)=(x-1)(x+3)", "(x-1)(2-x)(5-3x)=0", "x(x+1)=0",
               "3(x+1)^2=0", "(x+1)^2=(2x-3)^2", "(x-1)(x+2)=x-1", "-(x+1)^2+4=0", "(x+1)^2=5", "2(x-1)=3(1-x)(x+2)")
        non = ("(x+1)(x+3)=15", "(x+1)^2=-16", "(2x-1)^2-4x(x-1)=1", "x(x-4)=5", "(x+1)^2+(x-1)^2=10", "(x+1)^2=2x+14",
               "x^2+7x=18", "5-(x+1)(x+3)=0")
        for saisie in oui + non:
            g, d, x, _ = lire(saisie)
            with self.subTest(saisie=saisie):
                self.assertEqual(sd.forme_structuree(g, d, x), saisie in oui)
                if saisie in oui:
                    self.assertIsNone(sd.ramener(g, d, x))
                    self.assertEqual(resoudre(saisie)["statut"], "non_traite")

    def test_hors_de_ce_que_e2_developpe(self):
        """E2 ne développe que nombre ou monôme × parenthèse, deux parenthèses, le carré d'un binôme ; le reste, et tout ce qui n'est
        pas de degré 2 une fois ramené (P4b), reste « non_traite », sans étape."""
        for saisie in ("2(x+1)(x+3)=5", "0,5(x+2)^2=x+3", "(x+1)^3=8+x", "x*3+x^2=1", "(x^2+x+1)^2=x", "x^2/2=1+x",
                       "(x+1)(x+3)=x^2", "x^3=x+1", "x^2+1=x^2+x", "(x+2)(x-2)=x^2-4"):
            with self.subTest(saisie=saisie):
                res = resoudre(saisie)
                self.assertEqual((res["statut"], res["etapes"]), ("non_traite", []))

    def test_bornes(self):
        """§ 13.5 : un radicande trop grand pour la simplification (question 9 de suivi.md) donne le message des bornes."""
        g, d = expr.lire_membres("(1/9999999)x^2+x+1=0")
        res = sd.resoudre_equation(g, d, "x")
        self.assertEqual((res["statut"], res["message"]), ("hors_bornes", "Cette équation dépasse ce que l'outil sait traiter."))


# ---------------------------------------------------------------------------------------------------------------------------
# Ce que les parties suivantes traiteront (xfail stricts)
# ---------------------------------------------------------------------------------------------------------------------------
def _a_venir():
    """Les formes d'A_VENIR ; celles d'une partie pas encore faite (hors de PARTIES_FAITES) sont des xfail stricts."""
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


@pytest.mark.xfail(strict=True, reason="P4b : message « bicarrée » si ni ME ni Id. rem. ne s'applique (§ 13.4, plan P4b)")
def test_P4b_bicarree():
    res = resoudre("x^4-5x^2+4=0")
    assert (res["statut"], res["message"]) == ("pas_encore", MESSAGE_BICARREE)
