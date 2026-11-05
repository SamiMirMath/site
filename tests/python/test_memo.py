"""Tests rapides, décision T4 : `memo.etudier_la` (cache explicite des sorties de l'outil Limites).

- il rend une copie profonde, égale à la sortie du moteur : modifier ce qu'il rend ne change pas l'appel suivant, et deux appels ne
  partagent aucun dictionnaire ni aucune liste ;
- cache actif : le moteur n'est appelé qu'une fois par entrée ;
- `MEMO=0` : le moteur est vraiment appelé à chaque fois, et rien n'est gardé.

Les appels du moteur sont comptés par `sys.setprofile` (on observe les entrées dans le code de `la.etudier`, sans rien remplacer). La
garde statique (quels fichiers peuvent importer `memo`) est dans `test_memo_garde.py`."""
import os
import sys
import unittest

import moteurs  # noqa: F401  (chemins des moteurs + SymPy)
import limites_asymptotes as la
import memo

# quelques entrées : rationnelle, transcendantes, trou, saisie refusée (sortie {"ok": False, …})
ENTREES = [("1/(x-2)", False), ("ln(x)/x", False), ("(x^2-1)/(x-1)", False), ("e^(1/x)", False), ("(x^2-1)/(x-3)", True),
           ("x+", False)]


class Appels:
    """Compte les entrées dans le code de `la.etudier` pendant le bloc `with` (observateur seul : rien n'est remplacé)."""

    def __enter__(self):
        self.n = 0
        self.ancien = sys.getprofile()
        sys.setprofile(self._voir)
        return self

    def _voir(self, frame, evenement, arg):
        if evenement == "call" and frame.f_code is la.etudier.__code__:
            self.n += 1

    def __exit__(self, *exc):
        sys.setprofile(self.ancien)
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


def conteneurs(v, vus=None):
    """Identités de tous les dictionnaires, listes et ensembles contenus dans v (v compris)."""
    vus = set() if vus is None else vus
    if isinstance(v, (dict, list, set)) and id(v) not in vus:
        vus.add(id(v))
        for x in (list(v.keys()) + list(v.values())) if isinstance(v, dict) else list(v):
            conteneurs(x, vus)
    return vus


def saccager(v):
    """Vide en profondeur tous les dictionnaires et listes de v (ce qu'un test maladroit pourrait faire de son résultat)."""
    if isinstance(v, dict):
        for x in v.values():
            saccager(x)
        v.clear()
        v["saccagé"] = True
    elif isinstance(v, list):
        for x in v:
            saccager(x)
        v.clear()
        v.append("saccagé")


class TestMemo(unittest.TestCase):

    def appels_par_etude(self, entree, avec_bornes):
        """Nombre d'entrées dans `la.etudier` pour un appel direct (1 si le moteur ne s'appelle pas lui-même)."""
        with Appels() as a:
            la.etudier(entree, avec_bornes=avec_bornes)
        self.assertGreaterEqual(a.n, 1)
        return a.n

    def test_copie_profonde_egale_au_moteur(self):
        with Memo("1"):
            memo.vider()
            for entree, avec_bornes in ENTREES:
                with self.subTest(f=entree, avec_bornes=avec_bornes):
                    attendu = la.etudier(entree, avec_bornes=avec_bornes)
                    r1 = memo.etudier_la(entree, avec_bornes=avec_bornes)
                    self.assertEqual(r1, attendu)
                    r2 = memo.etudier_la(entree, avec_bornes=avec_bornes)
                    self.assertEqual(r2, attendu)
                    self.assertFalse(conteneurs(r1) & conteneurs(r2), "deux appels partagent un dictionnaire ou une liste")
                    saccager(r1)
                    saccager(r2)
                    r3 = memo.etudier_la(entree, avec_bornes=avec_bornes)
                    self.assertEqual(r3, attendu)
                    self.assertEqual(r3, la.etudier(entree, avec_bornes=avec_bornes))

    def test_cache_actif_le_moteur_n_est_appele_qu_une_fois(self):
        for entree, avec_bornes in ENTREES:
            with self.subTest(f=entree, avec_bornes=avec_bornes):
                n = self.appels_par_etude(entree, avec_bornes)
                with Memo("1"):
                    memo.vider()
                    with Appels() as a:
                        for _ in range(3):
                            memo.etudier_la(entree, avec_bornes=avec_bornes)
                    self.assertEqual(a.n, n)
                    self.assertIn((entree, avec_bornes), memo._SORTIES)

    def test_memo_0_appelle_vraiment_le_moteur_a_chaque_fois(self):
        for entree, avec_bornes in ENTREES:
            with self.subTest(f=entree, avec_bornes=avec_bornes):
                n = self.appels_par_etude(entree, avec_bornes)
                with Memo("0"):
                    memo.vider()
                    self.assertFalse(memo.actif())
                    with Appels() as a:
                        r = [memo.etudier_la(entree, avec_bornes=avec_bornes) for _ in range(3)]
                    self.assertEqual(a.n, 3 * n)
                    self.assertEqual(memo._SORTIES, {})
                    self.assertEqual(r[0], la.etudier(entree, avec_bornes=avec_bornes))
                    self.assertIsNot(r[0], r[1])


if __name__ == "__main__":
    unittest.main()
