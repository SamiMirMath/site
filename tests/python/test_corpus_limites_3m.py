"""Chantier « Limites et asymptotes » 3M, étape 1 : le corpus de l'enseignant (donnees/corpus_limites_3m.py) contre un oracle indépendant.

1. Les valeurs attendues du fichier sont recoupées par mpmath (50 chiffres), sans passer par le moteur ni par son parseur.
2. Chaque valeur que l'outil écrit pour une borne est celle de l'oracle (lecture de l'écriture LaTeX de l'outil).
3. Le signe d'approche 0⁺ / 0⁻ n'est pas encore écrit par l'outil : test marqué « échec attendu » (étape 5 du chantier).
4. Les asymptotes de 3.10 et 3.11.
5. Cliquet sur le nombre de bornes en phrase de repli : il ne doit jamais augmenter."""
import os
import re
import sys
import unittest

import mpmath
import sympy as sp

from moteurs import ensemble_def  # noqa: F401  (chemins + SymPy)
import limites_asymptotes as la

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "donnees"))
from corpus_limites_3m import CAS, ETUDES, PAS_PRIS_EN_CHARGE  # noqa: E402

REPLI = "Le calcul détaillé de cette limite n'est pas rédigé ici"
X = sp.Symbol("x", real=True)
ESPACE = {"x": X, "E": sp.E, "oo": sp.oo, "log": sp.log, "exp": sp.exp, "sqrt": sp.sqrt, "sin": sp.sin, "cos": sp.cos, "pi": sp.pi}


def exact(chaine):
    return sp.sympify(chaine, locals=ESPACE)


# ---------------------------------------------------------------------------------------------------------------------------
# 1. Oracle : les valeurs attendues du fichier sont recoupées numériquement
# ---------------------------------------------------------------------------------------------------------------------------
def sondes(cas):
    """Valeurs de la fonction de référence (SymPy → mpmath, 120 chiffres le temps du calcul) en approchant le point."""
    infini = cas.point in ("+oo", "-oo")
    ks = (1, 2, 3) if infini and "exp" in cas.ref else (4, 8, 16, 30)        # e^(-10^k) s'arrondit à 0 : sondes plus proches, précision plus grande
    with mpmath.workdps(700 if infini and "exp" in cas.ref else 120):
        f = sp.lambdify(X, exact(cas.ref), modules="mpmath")
        if infini:
            signe = 1 if cas.point == "+oo" else -1
            return [f(signe * mpmath.mpf(10) ** k) for k in ks]
        a = mpmath.mpf(str(sp.N(exact(cas.point), 130)))
        d = 1 if cas.cote == "+" else -1
        return [f(a + d * mpmath.mpf(10) ** -k) for k in ks]


class TestOracleDuCorpus(unittest.TestCase):
    def test_valeurs_attendues_confirmees_par_mpmath(self):
        for cas in CAS:
            with self.subTest(id=cas.id, point=cas.point, cote=cas.cote):
                v = sondes(cas)
                attendu = exact(cas.attendu)
                if attendu in (sp.oo, -sp.oo):
                    s = 1 if attendu == sp.oo else -1
                    self.assertTrue(all(s * x > 0 for x in v), v)
                    self.assertGreater(abs(v[-1]), abs(v[0]), v)
                else:
                    cible = mpmath.mpf(str(sp.N(attendu, 50)))
                    ecarts = [abs(x - cible) for x in v]
                    self.assertLess(ecarts[-1], max(ecarts[0], mpmath.mpf(10) ** -30), v)
                    self.assertLess(ecarts[-1], mpmath.mpf("0.05") * (1 + abs(cible)), v)

    def test_signe_d_approche_de_zero_confirme_par_mpmath(self):
        for cas in CAS:
            if cas.signe0 is None:
                continue
            with self.subTest(id=cas.id, point=cas.point, cote=cas.cote):
                v = sondes(cas)
                s = 1 if cas.signe0 == "+" else -1
                self.assertTrue(all(s * x > 0 for x in v), v)

    def test_signe_seulement_pour_les_valeurs_nulles(self):
        for cas in CAS:
            self.assertEqual(cas.signe0 is not None, exact(cas.attendu) == 0, cas.id)


# ---------------------------------------------------------------------------------------------------------------------------
# 2. Valeurs écrites par l'outil
# ---------------------------------------------------------------------------------------------------------------------------
def nombre_depuis_tex(t):
    """Valeur numérique d'un résultat écrit par l'outil : ±\\infty, entier, fraction, e^{k}, \\ln{\\left(a \\right)}, racines. ValueError sinon."""
    t = t.strip()
    if t == r"+\infty":
        return float("inf")
    if t == r"-\infty":
        return float("-inf")
    s = re.sub(r"\^\{[+-]\}$", "", t)                                     # 0^{+}
    s = re.sub(r"\\ln\{\\left\((.*?) \\right\)\}", r"log(\1)", s)
    s = re.sub(r"\\ln\s*(\d+)", r"log(\1)", s)
    s = s.replace(r"\left(", "(").replace(r"\right)", ")")
    for _ in range(6):
        s = re.sub(r"\\d?frac\{([^{}]*)\}\{([^{}]*)\}", r"((\1)/(\2))", s)
        s = re.sub(r"\\sqrt\{([^{}]*)\}", r"sqrt(\1)", s)
        s = re.sub(r"e\^\{([^{}]*)\}", r"exp(\1)", s)
    if "\\" in s or "{" in s:
        raise ValueError(t)
    return float(sp.N(sp.sympify(s.replace("^", "**"), locals={"log": sp.log, "exp": sp.exp, "sqrt": sp.sqrt}), 30))


def valeur_de_l_outil(r, cas):
    """Valeur (tex) que l'outil donne pour la borne du cas ; None si la borne n'a pas de valeur de ce côté."""
    point = exact(cas.point)
    for b in r["limites_bornes"]:
        if point in (sp.oo, -sp.oo):
            if b["type"] == "inf" and b["signe"] == (1 if point == sp.oo else -1):
                return b["tex"]
        elif b["type"] == "fini" and abs(b["point_val"] - float(sp.N(point))) < 1e-9:
            return b["gauche"] if cas.cote == "-" else b["droite"]
    return None


class TestValeursDeLOutil(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.etudes = {}
        for cas in CAS:
            if cas.id not in PAS_PRIS_EN_CHARGE and cas.saisie not in cls.etudes:
                cls.etudes[cas.saisie] = la.etudier(cas.saisie, avec_bornes=True)

    def test_chaque_borne_a_la_valeur_de_l_oracle(self):
        for cas in CAS:
            if cas.id in PAS_PRIS_EN_CHARGE:
                continue
            with self.subTest(id=cas.id, point=cas.point, cote=cas.cote):
                r = self.etudes[cas.saisie]
                self.assertTrue(r["ok"], r.get("erreur"))
                tex = valeur_de_l_outil(r, cas)
                self.assertIsNotNone(tex, "borne absente de l'étude")
                attendu = exact(cas.attendu)
                v = nombre_depuis_tex(tex)
                if attendu in (sp.oo, -sp.oo):
                    self.assertEqual(v, float(attendu), tex)
                else:
                    self.assertAlmostEqual(v, float(sp.N(attendu)), places=9, msg=tex)

    def test_signe_zero_plus_ou_moins_ecrit(self):
        """Refonte de la rédaction (30.10.2026) : la valeur 0 s'écrit 0⁺ ou 0⁻ comme dans le corrigé (R17), cas du corpus compris."""
        for cas in CAS:
            if cas.signe0 is None or cas.id in PAS_PRIS_EN_CHARGE:
                continue
            tex = valeur_de_l_outil(self.etudes[cas.saisie], cas)
            self.assertEqual(tex, "0^{" + cas.signe0 + "}", (cas.id, cas.point, tex))

    def test_fonctions_non_prises_en_charge(self):
        saisies = {c.id: c.saisie for c in CAS}
        for id_, message in PAS_PRIS_EN_CHARGE.items():
            with self.subTest(id=id_):
                r = la.etudier(saisies[id_])
                self.assertFalse(r["ok"])
                self.assertEqual(r["erreur"], message)


# ---------------------------------------------------------------------------------------------------------------------------
# 3. Asymptotes de 3.10 et 3.11
# ---------------------------------------------------------------------------------------------------------------------------
def asymptotes_de_l_outil(r):
    out = set()
    for a in r["asymptotes"]:
        if a["genre"] == "oblique":
            out.add(("oblique", a["ou"], a["equation_tex"]))
            continue
        ou = a["ou"]
        if a["genre"] == "horizontale":
            position = "+oo" if ou.endswith(r"+\infty") else "-oo"
            out.add(("horizontale", position, round(nombre_depuis_tex(a["valeur_tex"]), 9)))
        else:
            valeur = round(nombre_depuis_tex(a["valeur_tex"]), 9) if a["genre"] == "trou" else None
            out.add((a["genre"], round(a["point_val"], 9), valeur))
    return out


def attendues(liste):
    out = set()
    for genre, position, valeur in liste:
        v = None if valeur is None else round(float(sp.N(exact(valeur))), 9)
        p = position if position in ("+oo", "-oo") else round(float(sp.N(exact(position))), 9)
        out.add((genre, p, v))
    return out


class TestAsymptotes(unittest.TestCase):
    def test_exercices_3_10_et_3_11(self):
        for id_, saisie, liste in ETUDES:
            with self.subTest(id=id_, f=saisie):
                r = la.etudier(saisie)
                self.assertTrue(r["ok"], r.get("erreur"))
                self.assertEqual(asymptotes_de_l_outil(r), attendues(liste))


# ---------------------------------------------------------------------------------------------------------------------------
# 4. Cliquet : nombre de bornes en phrase de repli
# ---------------------------------------------------------------------------------------------------------------------------
REPLIS_MAXIMUM = 13        # relevé du 29.10.2026 après la doctrine « BH » (16 avant : 8.12e, Ex5c et 3.8g en +∞ rédigés) ; à baisser quand des replis disparaissent


def bornes_en_repli():
    """[(identifiant, borne)] des bornes du corpus dont l'étude contient la phrase de repli (une étude par saisie, un compte par identifiant)."""
    out, etudes, vus = [], {}, set()
    for cas in CAS:
        if cas.id in PAS_PRIS_EN_CHARGE or cas.id in vus:
            continue
        vus.add(cas.id)
        r = etudes.setdefault(cas.saisie, la.etudier(cas.saisie))
        for e in r["etudes"]:
            if any(REPLI in it.get("html", "") for it in e["etapes"]):
                out.append((cas.id, e["ou"]))
    return out


class TestReplis(unittest.TestCase):
    def test_le_nombre_de_replis_ne_monte_pas(self):
        replis = bornes_en_repli()
        self.assertLessEqual(len(replis), REPLIS_MAXIMUM, replis)


if __name__ == "__main__":
    unittest.main()
