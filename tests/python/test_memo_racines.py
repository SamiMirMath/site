"""Tests rapides, décision T5 : `memo_racines.racines` (cache explicite de l'oracle `racines` de test_exp_log_m).

- l'oracle `racines` n'est pas modifié : son texte a toujours la même empreinte, et c'est bien lui que le cache appelle ;
- le cache rend une copie profonde, égale au résultat de l'oracle : modifier la liste reçue ne change pas l'appel suivant ;
- cache actif : l'oracle n'est appelé qu'une fois par clé ; `MEMO=0` : l'oracle est vraiment appelé à chaque fois, et rien n'est gardé ;
- la clé : deux saisies égales donnent la même clé, deux saisies différentes deux clés ; un arbre modifié après l'appel donne une
  nouvelle clé (la clé est un instantané, pas une référence) ; un objet hors des types prévus (entier au lieu d'une fraction,
  sous-classe d'un nœud) n'a pas de clé : appel direct ; la précision du contexte mpmath fait partie de la clé.

Les appels de l'oracle sont comptés par `sys.monitoring` (on observe les entrées dans le code de `racines`, sans rien remplacer). La
garde statique (quels fichiers peuvent importer `memo_racines`) est dans `test_memo_racines_garde.py`."""
import hashlib
import inspect
import os
import sys
import types
import unittest
from fractions import Fraction

import mpmath as mp

import moteurs  # noqa: F401  (chemins des moteurs)
import exp_log as el
import memo_racines
import test_exp_log_m as oracle

# Empreinte SHA-256 du texte de `racines` (test_exp_log_m.py, commit 7186b6d) : décision T5, il est interdit de modifier l'oracle.
EMPREINTE_RACINES = "99e567c5e4ee5fce8316f453e908ae4334034d4ae43b2b8f9f84b0c8e1e21383"

# entrées : une racine, une racine après rejet (x = −2 hors de l'ensemble de définition), deux racines, aucune racine
ENTREES = ["2^x=8", "log(x) + log(x-3) = 1", "x^2=4", "e^x=-1"]


class Appels:
    """Compte les entrées dans le code de l'oracle `racines` pendant le bloc `with` : `sys.monitoring` (Python 3.12), événement PY_START
    activé sur ce seul code (observateur seul : rien n'est remplacé, et le reste du code ne paie rien)."""

    def __enter__(self):
        self.n = 0
        self.outil = next(i for i in range(6) if sys.monitoring.get_tool(i) is None)
        sys.monitoring.use_tool_id(self.outil, "test_memo_racines")
        sys.monitoring.register_callback(self.outil, sys.monitoring.events.PY_START, self._voir)
        sys.monitoring.set_local_events(self.outil, oracle.racines.__code__, sys.monitoring.events.PY_START)
        return self

    def _voir(self, code, decalage):
        if code is oracle.racines.__code__:
            self.n += 1

    def __exit__(self, *exc):
        sys.monitoring.set_local_events(self.outil, oracle.racines.__code__, 0)
        sys.monitoring.register_callback(self.outil, sys.monitoring.events.PY_START, None)
        sys.monitoring.free_tool_id(self.outil)
        return False


class Memo:
    """Donne une valeur à la variable MEMO pendant le bloc `with`, puis remet la valeur d'avant (ou l'absence de valeur)."""

    def __init__(self, valeur):
        self.valeur = valeur

    def __enter__(self):
        self.ancienne = os.environ.get("MEMO")
        os.environ["MEMO"] = self.valeur
        return self

    def __exit__(self, *exc):
        if self.ancienne is None:
            os.environ.pop("MEMO", None)
        else:
            os.environ["MEMO"] = self.ancienne
        return False


def saisie(entree):
    return el.analyser_saisie(entree)


class TestOracleIntact(unittest.TestCase):

    def test_racines_n_est_pas_modifiee(self):
        texte = inspect.getsource(oracle.racines)
        self.assertEqual(hashlib.sha256(texte.encode("utf-8")).hexdigest(), EMPREINTE_RACINES)
        self.assertEqual(str(inspect.signature(oracle.racines)), "(s)")
        self.assertEqual(oracle.racines.__module__, "test_exp_log_m")
        self.assertIs(memo_racines.oracle(), oracle)
        self.assertIs(memo_racines.oracle().racines, oracle.racines)


class TestMemoRacines(unittest.TestCase):

    def test_copie_profonde_egale_a_l_oracle(self):
        with Memo("1"):
            memo_racines.vider()
            for entree in ENTREES:
                with self.subTest(entree=entree):
                    attendu = oracle.racines(saisie(entree))
                    r1 = memo_racines.racines(saisie(entree))
                    r2 = memo_racines.racines(saisie(entree))
                    self.assertEqual(r1, attendu)
                    self.assertEqual(r2, attendu)
                    self.assertIsNot(r1, r2)
                    for x in r1 + r2:
                        self.assertIs(type(x), type(oracle.MP.mpf(0)))
                        self.assertIs(x.context, oracle.MP)
                    r1.clear()
                    r2.append(oracle.MP.mpf(7))
                    r3 = memo_racines.racines(saisie(entree))
                    self.assertEqual(r3, attendu)

    def test_cache_actif_l_oracle_n_est_appele_qu_une_fois_par_cle(self):
        with Memo("1"):
            memo_racines.vider()
            with Appels() as a:
                for entree in ENTREES:
                    for _ in range(3):
                        memo_racines.racines(saisie(entree))
            self.assertEqual(a.n, len(ENTREES))
            self.assertEqual(len(memo_racines._RACINES), len(ENTREES))
            self.assertTrue(memo_racines.actif())

    def test_memo_0_appelle_vraiment_l_oracle_a_chaque_fois(self):
        with Memo("0"):
            memo_racines.vider()
            self.assertFalse(memo_racines.actif())
            for entree in ENTREES:
                with self.subTest(entree=entree):
                    with Appels() as a:
                        r = [memo_racines.racines(saisie(entree)) for _ in range(2)]
                    self.assertEqual(a.n, 2)
                    self.assertEqual(memo_racines._RACINES, {})
                    self.assertEqual(r[0], r[1])
                    self.assertIsNot(r[0], r[1])


class TestCle(unittest.TestCase):

    def test_saisies_egales_meme_cle_saisies_differentes_cles_differentes(self):
        cles = [memo_racines.cle(saisie(e)) for e in ENTREES]
        self.assertEqual(cles, [memo_racines.cle(saisie(e)) for e in ENTREES])
        self.assertEqual(len(set(cles)), len(ENTREES))
        # mêmes nombres, autres types ou autres champs : clés différentes
        for a, b in [("2^x=8", "2^x=9"), ("2^x=8", "x^2=8"), ("log(x)=1", "ln(x)=1"), ("2^x=8", "2^y=8"), ("x^(1/2)=3", "sqrt(x)=3")]:
            with self.subTest(a=a, b=b):
                self.assertNotEqual(memo_racines.cle(saisie(a)), memo_racines.cle(saisie(b)))

    def test_un_objet_hors_des_types_prevus_n_a_pas_de_cle(self):
        class Nb2(el.Nb):
            __slots__ = ()
        entier = saisie("2^x=8")
        entier.d.val = 8                                     # un entier à la place de la fraction 8
        sous_classe = el.Saisie("equation", el.Pow(Nb2(2), el.Var("x")), el.Nb(8), "x")
        for s in (entier, sous_classe):
            with self.subTest(s=repr(s)):
                with self.assertRaises(memo_racines.HorsCle):
                    memo_racines.cle(s)
                with Memo("1"):
                    memo_racines.vider()
                    with Appels() as a:
                        r = [memo_racines.racines(s) for _ in range(2)]
                    self.assertEqual(a.n, 2)                 # appel direct à chaque fois
                    self.assertEqual(memo_racines._RACINES, {})
                    self.assertEqual(r[0], oracle.racines(s))
        for v in (0.5, 1, True, mp.mpf(1), b"x", [1], {"a": 1}):
            with self.subTest(v=v):
                with self.assertRaises(memo_racines.HorsCle):
                    memo_racines.figer(v)
        self.assertNotEqual(memo_racines.figer(Fraction(1, 2)), memo_racines.figer("1/2"))

    def test_un_arbre_modifie_apres_l_appel_donne_une_nouvelle_cle(self):
        s = saisie("2^x=8")
        with Memo("1"):
            memo_racines.vider()
            with Appels() as a:
                self.assertEqual(memo_racines.racines(s), [oracle.MP.mpf(3)])
                s.d.val = Fraction(4)                        # 2^x = 4
                self.assertEqual(memo_racines.racines(s), [oracle.MP.mpf(2)])
            self.assertEqual(a.n, 2)
            self.assertEqual(memo_racines.racines(s), oracle.racines(s))

    def test_le_contexte_mpmath_fait_partie_de_la_cle(self):
        autre = mp.MPContext()
        autre.dps = 40
        faux = types.SimpleNamespace(racines=oracle.racines, ecart=oracle.ecart, evaluer=oracle.evaluer, MP=autre)
        self.assertNotEqual(memo_racines.contexte(faux), memo_racines.contexte(oracle))
        self.assertEqual(memo_racines.contexte(oracle), memo_racines.contexte(oracle))


if __name__ == "__main__":
    unittest.main()
