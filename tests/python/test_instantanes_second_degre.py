"""Instantanés de la rédaction du 2e degré (chantier equations-2e-degre, dès P2b : decisions.md § 13.2 ; plan, P2b).

Pour chaque équation de `corpus_second_degre.P2B` : la résolution de `second_degre.resoudre_equation` (statut, étapes : phase,
méthode, cible ; S, ligne ≈, variantes) et ses blocs de moteur/sortie.py (`second_degre.blocs` : ce que la page affichera), plus la
variante « formule » (E12) quand elle est proposée. Comparés à une référence enregistrée **hors d'`instantanes/`** jusqu'en P5 :
tests/python/donnees/equations-2e-degre/instantanes.json (dump_sorties.py et les contrôles d'`instantanes/` ne la voient pas
encore : ce fichier contrôle donc lui-même le JSON strict et le vocabulaire).

Une différence = un changement de rédaction. S'il est voulu, régénérer explicitement puis relire le diff git :

    REGENERER=1 uv run -q --no-project --python 3.12 --with sympy==1.13.3 --with mpmath==1.3.0 --with pytest \\
        python -m pytest tests/python/test_instantanes_second_degre.py
"""
import json
import math
import os
import unittest

import moteurs  # noqa: F401  (chemins des moteurs)

import expr
import second_degre as sd
import sortie
from aides_sortie import TUTOIEMENT
from corpus_second_degre import P2B
from test_instantanes import normaliser
from test_vocabulaire import INTERDITS, chaines

ICI = os.path.dirname(os.path.abspath(__file__))
CHEMIN = os.path.join(ICI, "donnees", "equations-2e-degre", "instantanes.json")
REGENERER = os.environ.get("REGENERER") == "1"


def _decimaux(n):
    if isinstance(n, expr.Nb):
        return n.dec is not None
    return any(_decimaux(getattr(n, s)) for s in getattr(n, "__slots__", ()) if isinstance(getattr(n, s), expr.Noeud))


def resume(res):
    """Ce qui est figé d'une résolution : tout ce que la page affichera (blocs), et la structure des étapes (§ 5)."""
    r = {"statut": res["statut"], "message": res["message"], "variantes": res["variantes"]}
    if res["statut"] == "resolu":
        r.update(S=res["S"], approx=res["approx"], etapes=[[e["phase"], e["methode"], e["cible"]] for e in res["etapes"]],
                 blocs=sd.blocs(res))
    return r


def instantane(saisie):
    g, d = expr.lire_membres(saisie)
    lettres = sorted(expr.variables(g) | expr.variables(d))
    x, dec = lettres[0], _decimaux(g) or _decimaux(d)
    res = sd.resoudre_equation(g, d, x, dec)
    out = {"saisie": saisie, "cours": resume(res)}
    if res["variantes"]:
        out["formule"] = resume(sd.resoudre_equation(g, d, x, dec, sd.ORDRE_PAR_LA_FORMULE))
    return normaliser(out)


def calculer():
    return {nom: instantane(saisie) for nom, saisie in P2B.items()}


def refuse(constante):
    raise AssertionError(f"constante JSON non standard : {constante}")


def non_finis(o):
    if isinstance(o, float):
        return not math.isfinite(o)
    if isinstance(o, dict):
        return any(non_finis(v) for v in o.values())
    if isinstance(o, list):
        return any(non_finis(v) for v in o)
    return False


class TestInstantanesSecondDegre(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.actuel = calculer()

    def test_instantanes(self):
        if REGENERER:
            os.makedirs(os.path.dirname(CHEMIN), exist_ok=True)
            with open(CHEMIN, "w", encoding="utf-8") as f:
                json.dump(self.actuel, f, ensure_ascii=False, indent=1, sort_keys=True, allow_nan=False)
                f.write("\n")
            self.skipTest(f"instantané régénéré : {CHEMIN}")
        self.assertTrue(os.path.exists(CHEMIN), f"instantané absent : lancer avec REGENERER=1 ({CHEMIN})")
        with open(CHEMIN, encoding="utf-8") as f:
            reference = json.load(f)
        self.assertEqual(sorted(self.actuel), sorted(reference), "liste des entrées modifiée : régénérer avec REGENERER=1")
        for nom in self.actuel:
            with self.subTest(entree=nom):
                self.assertEqual(self.actuel[nom], reference[nom])

    def test_json_strict(self):
        """Le fichier est du JSON strict (pas de NaN ni d'Infinity : la page appelle JSON.parse), comme test_json_strict."""
        with open(CHEMIN, encoding="utf-8") as f:
            data = json.loads(f.read(), parse_constant=refuse)
        self.assertFalse(non_finis(data))
        json.dumps(self.actuel, allow_nan=False)

    def test_sorties_conformes(self):
        """Les blocs figés forment une sortie conforme au schéma commun (sortie.valider), dans une carte normale."""
        for nom, v in self.actuel.items():
            for cle in ("cours", "formule"):
                if cle in v and v[cle]["statut"] == "resolu":
                    with self.subTest(entree=nom, chemin=cle):
                        s = sortie.sortie_ok("x", [sortie.carte("Résolution", v[cle]["blocs"])])
                        self.assertEqual(sortie.valider(s), [])

    def test_vocabulaire(self):
        """C6 et R12 (test_vocabulaire ne lit pas encore ce fichier) : aucun mot interdit, aucun tutoiement."""
        with open(CHEMIN, encoding="utf-8") as f:
            data = json.load(f)
        for nom, v in data.items():
            with self.subTest(entree=nom):
                for t in chaines(v):
                    self.assertIsNone(INTERDITS.search(t), t[:160])
                    self.assertIsNone(TUTOIEMENT.search(t), t[:160])


if __name__ == "__main__":
    unittest.main()
