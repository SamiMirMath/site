"""T35 (étape 1) — Paramètre « filière » de l'outil « Exponentielles et logarithmes » (EL-26) : C est le défaut et reste strictement identique,
une filière inconnue donne un message en français. Les étapes suivantes ajoutent ici l'ensemble de définition, le regroupement et la vérification."""
import json
import unittest

import mpmath as mp

import moteurs  # noqa: F401  (chemins des moteurs)
import exp_log as el
import exp_log_m as elm
import resoudre_el as rel
import resoudre_ed
import sortie as so
from cas_el import BATTERIE_E4, BATTERIE_M, IMBRIQUES_BASE_10, entrees_el, entrees_el_m


class TestFiliereParDefaut(unittest.TestCase):
    def test_c_est_le_defaut_pour_toutes_les_entrees(self):
        for entree in entrees_el():
            with self.subTest(entree=entree):
                self.assertEqual(rel.resoudre(entree), rel.resoudre(entree, "C"))
                self.assertEqual(rel.resoudre_json(entree), rel.resoudre_json(entree, "C"))

    def test_l_exercice_par_defaut_est_celui_de_la_filiere_c(self):
        for niveau in ("facile", "moyen", "logarithme", "difficile"):
            for graine in range(20):
                self.assertEqual(el.exercice(niveau, graine), el.exercice(niveau, graine, "C"))
        self.assertTrue(json.loads(el.exercice_json("facile", "C"))["ok"])
        self.assertTrue(json.loads(el.exercice_json("facile"))["ok"])

    def test_la_filiere_m_donne_une_sortie_valide_pour_son_corpus(self):
        for entree in entrees_el_m():
            with self.subTest(entree=entree):
                self.assertEqual(so.valider(rel.resoudre(entree, "M")), [])


class TestFiliereInconnue(unittest.TestCase):
    def test_message_en_francais(self):
        for filiere in ("", "c", "m", "Ms", "3C", None):
            with self.subTest(filiere=filiere):
                s = rel.resoudre("2^x=8", filiere)
                self.assertEqual(s, {"ok": False, "erreur": el.MESSAGE_FILIERE})
                self.assertEqual(json.loads(rel.resoudre_json("2^x=8", filiere)), s)
                self.assertEqual(el.exercice("facile", 1, filiere), {"ok": False, "erreur": el.MESSAGE_FILIERE})
                self.assertEqual(json.loads(el.exercice_json("facile", filiere)), {"ok": False, "erreur": el.MESSAGE_FILIERE})

    def test_le_message_vouvoie(self):
        self.assertNotRegex(el.MESSAGE_FILIERE, r"\b(tu|ton|ta|tes|toi)\b")


class TestCartesEDReutilisables(unittest.TestCase):
    """resoudre_ed expose les blocs d'une condition et de la conclusion « ED = … » (réutilisés par la filière M) ; l'outil ED en garde la sortie."""

    def test_les_cartes_de_l_outil_ed_sont_faites_de_ces_blocs(self):
        import ensemble_def
        for f in ("ln(x)+ln(x-1)", "ln(x^2-4)+ln(x+3)", "ln(x-3)+ln(1-x)", "ln(x)+x^2", "x^2+1"):
            with self.subTest(f=f):
                r = ensemble_def.analyser(f)
                self.assertEqual([resoudre_ed._carte_condition(c)["blocs"] for c in r["conditions"]], [resoudre_ed.blocs_condition(c) for c in r["conditions"]])
                self.assertEqual(resoudre_ed._carte_finale(r)["blocs"], resoudre_ed.blocs_ensemble(r))

    def test_le_cas_sans_condition_et_le_cas_non_resolu(self):
        self.assertEqual(resoudre_ed.blocs_ensemble({"complet": True, "conditions": []}), [so.resultat("ED = \\mathbb{R}")])
        self.assertEqual(resoudre_ed.blocs_ensemble({"complet": False, "conditions": []}),
                         [so.erreur("Une condition n'a pas pu être résolue : l'ED n'est pas calculé.")])


# =====================================================================
# Étape 2 : l'ensemble de définition d'abord, la vérification ensuite (un seul logarithme)
# =====================================================================
MP = mp.MPContext()          # contexte isolé : ne change pas la précision globale de mpmath (les autres tests l'utilisent)
MP.dps = 30


def evaluer(n, x):
    """Oracle indépendant du moteur : valeur d'un arbre avec mpmath, None quand l'expression n'est pas définie (logarithme d'un nombre ≤ 0,
    base d'un logarithme ≤ 0 ou égale à 1, division par 0)."""
    if isinstance(n, el.Nb):
        return MP.mpf(n.val.numerator) / n.val.denominator
    if isinstance(n, el.Var):
        return MP.mpf(x)
    if isinstance(n, el.E):
        return MP.e
    if isinstance(n, el.Defini):
        return evaluer(n.arbre, x)
    if isinstance(n, el.Neg):
        v = evaluer(n.a, x)
        return None if v is None else -v
    if isinstance(n, el.Fn):
        v = evaluer(n.a, x)
        return None if v is None or v < 0 else MP.sqrt(v)
    if isinstance(n, el.Pow):
        a, b = evaluer(n.a, x), evaluer(n.b, x)
        if a is None or b is None or (a == 0 and b < 0) or (a < 0 and b != int(b)):
            return None
        return MP.power(a, b)
    if isinstance(n, el.Op):
        a, b = evaluer(n.a, x), evaluer(n.b, x)
        if a is None or b is None:
            return None
        if n.op == "/":
            return None if b == 0 else a / b
        return a + b if n.op == "+" else a - b if n.op == "-" else a * b
    if isinstance(n, el.Log):
        a = evaluer(n.a, x)
        b = MP.mpf(10) if n.base is None else evaluer(n.base, x)
        if a is None or b is None or a <= 0 or b <= 0 or b == 1:
            return None
        return MP.log(a) / MP.log(b)
    raise TypeError(n)


def ecart(s, x):
    """g(x) − d(x) pour la saisie s, None hors de l'ensemble de définition."""
    g, d = evaluer(s.g, x), evaluer(s.d, x)
    return None if g is None or d is None else g - d


def racines(s):
    """Les racines réelles de g = d trouvées sans le moteur : changements de signe de g − d sur une grille fine et large, bissection, et seulement
    celles où l'écart s'annule vraiment (un pôle change de signe sans s'annuler)."""
    points = sorted({MP.mpf(i) / 40 + MP.mpf("0.000713") for i in range(-2400, 2401)} |
                    {sg * MP.power(10, MP.mpf(k) / 8) for sg in (-1, 1) for k in range(-96, 120)})
    trouvees = []
    for a, b in zip(points, points[1:]):
        fa, fb = ecart(s, a), ecart(s, b)
        if fa is None or fb is None or fa * fb > 0:
            continue
        lo, hi = a, b
        for _ in range(200):
            mid = (lo + hi) / 2
            fm = ecart(s, mid)
            if fm is None:
                break
            if fa * fm <= 0:
                hi = mid
            else:
                lo, fa = mid, fm
        else:
            r = (lo + hi) / 2
            fr = ecart(s, r)
            if fr is not None and abs(fr) < MP.mpf("1e-12") * (1 + abs(r)):
                trouvees.append(r)
    return trouvees


E4_M = [(s, v) for s, v in BATTERIE_E4 if s not in IMBRIQUES_BASE_10]


def solutions_m(entree):
    """Les solutions (floats) retenues par le corrigé M d'une équation, ou None quand la filière M ne la traite pas."""
    s = el.analyser_saisie(entree)
    r = elm.corriger_equation(s.g, s.d, s.inconnue)
    return None if r is None else r


def valeurs(r):
    return sorted(el.valeur(n) for n in r["solutions"])


class TestBatterieM(unittest.TestCase):
    def test_les_solutions_retenues_de_la_batterie(self):
        for entree, attendu in BATTERIE_M:
            with self.subTest(entree=entree):
                r = solutions_m(entree)
                self.assertIsNotNone(r)
                v = valeurs(r)
                self.assertEqual(len(v), len(attendu), (v, attendu))
                for a, b in zip(v, sorted(attendu)):
                    self.assertAlmostEqual(a, b, delta=1e-3 * (1 + abs(b)))

    def test_oracle_les_solutions_sont_exactement_les_racines_dans_l_ensemble_de_definition(self):
        """Chaque solution retenue annule g − d et est dans l'ED ; aucune racine de l'équation de départ n'est perdue (balayage numérique
        indépendant), et chaque candidat rejeté est hors de l'ED."""
        for entree, _ in BATTERIE_M + E4_M:
            r = solutions_m(entree)
            if r is None:
                continue
            with self.subTest(entree=entree):
                s = el.analyser_saisie(entree)
                retenues = [MP.mpf(el.valeur(n)) for n in r["solutions"]]
                for v in retenues:
                    e = ecart(s, v)
                    self.assertIsNotNone(e, "solution hors de l'ensemble de définition")
                    self.assertLess(abs(e), MP.mpf("1e-9") * (1 + abs(v)))
                for rac in racines(s):
                    self.assertTrue(any(abs(rac - v) < MP.mpf("1e-9") * (1 + abs(rac)) for v in retenues), ("racine perdue", rac))

    def test_les_solutions_de_la_3c_sont_celles_de_m_quand_l_ed_ne_rejette_rien(self):
        for entree, attendu in E4_M:
            with self.subTest(entree=entree):
                r = solutions_m(entree)
                self.assertIsNotNone(r)
                v = valeurs(r)
                self.assertEqual(len(v), len(attendu))
                for a, b in zip(v, sorted(attendu)):
                    self.assertAlmostEqual(a, b, delta=1e-3 * (1 + abs(b)))


def cartes(entree):
    s = rel.resoudre(entree, "M")
    assert s["ok"], (entree, s)
    return s["cartes"]


class TestCartesM(unittest.TestCase):
    def test_la_premiere_carte_est_l_ensemble_de_definition(self):
        for entree, _ in BATTERIE_M + E4_M:
            with self.subTest(entree=entree):
                c = cartes(entree)
                self.assertEqual(c[0]["badge"], "Ensemble de définition", entree)
                self.assertEqual(c[0]["titre"], "Étape 1")
                self.assertEqual(c[-1]["titre"], "Solution")

    def test_la_verification_a_une_ligne_par_solution_candidate(self):
        c = cartes("log_x(256)=4")
        self.assertEqual([k["badge"] for k in c[:-1]], ["Ensemble de définition", "Exponentielle des deux membres", "Vérification"])
        lignes = c[2]["blocs"]
        self.assertEqual(len(lignes), 2)
        self.assertIn("x = -4", lignes[0]["html"])
        self.assertIn("rejetée", lignes[0]["html"])
        self.assertIn("base d'un logarithme", lignes[0]["html"])
        self.assertIn("dans l'ensemble de définition", lignes[1]["html"])
        self.assertIn(r"\left\{4\right\}", c[-1]["blocs"][0]["tex"])

    def test_toutes_les_solutions_rejetees(self):
        c = cartes("log_x(1)=2")
        self.assertIn("Aucune solution de l'équation n'est dans l'ensemble de définition.", c[-2]["blocs"][-1]["html"])
        self.assertEqual(c[-1]["blocs"][0]["tex"], r"S = \varnothing")

    def test_ed_vide_la_phrase_est_dans_la_carte_de_l_ed_et_aucune_autre_carte(self):
        c = cartes("log(-x^2-1)=0")
        self.assertEqual([k["titre"] for k in c], ["Étape 1", "Solution"])
        self.assertIn("L'ensemble de définition est vide", c[0]["blocs"][-1]["html"])
        self.assertEqual(c[-1]["blocs"][0]["tex"], r"S = \varnothing")

    def test_aucune_ancienne_carte_condition_ni_verification_de_la_3c(self):
        for entree, _ in BATTERIE_M + E4_M:
            titres = [k["badge"] for k in cartes(entree) if k.get("badge")]
            self.assertNotIn("Condition", titres, entree)
            self.assertEqual(titres.count("Vérification") <= 1, True, entree)

    def test_une_autre_lettre_que_x_ne_laisse_aucun_x_dans_la_carte_de_l_ed(self):
        c = cartes("log(t-3)=1")
        for b in c[0]["blocs"]:
            for v in b.values():
                if isinstance(v, str) and "\\" in v:
                    self.assertNotRegex(v, r"(?<![\\A-Za-z])x(?![A-Za-z])", v)
        self.assertIn("t", c[0]["blocs"][-1]["tex"])

    def test_un_logarithme_imbrique_en_base_10_n_a_pas_le_corrige_de_la_3c(self):
        for entree in IMBRIQUES_BASE_10:
            with self.subTest(entree=entree):
                self.assertEqual(rel.resoudre(entree, "M"), {"ok": False, "erreur": el.MESSAGE_PAS_ENCORE})
                self.assertTrue(rel.resoudre(entree, "C")["ok"])

    def test_les_sorties_m_respectent_le_schema_et_le_json_strict(self):
        for entree, _ in BATTERIE_M + E4_M:
            with self.subTest(entree=entree):
                s = rel.resoudre(entree, "M")
                self.assertEqual(so.valider(s), [])
                self.assertEqual(json.loads(rel.resoudre_json(entree, "M")), s)

    def test_la_filiere_c_n_a_toujours_pas_d_ensemble_de_definition(self):
        for entree, _ in BATTERIE_M + E4_M:
            for k in rel.resoudre(entree, "C").get("cartes", []):
                self.assertNotEqual(k.get("badge"), "Ensemble de définition")

    def test_le_vouvoiement_et_le_vocabulaire(self):
        for entree, _ in BATTERIE_M:
            texte = json.dumps(rel.resoudre(entree, "M"), ensure_ascii=False)
            self.assertNotRegex(texte, r"\b(tu|ton|ta|tes|toi|vérifie|calcule)\b")


if __name__ == "__main__":
    unittest.main()
