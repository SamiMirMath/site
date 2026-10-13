"""T01 — Instantanés : la sortie complète de chaque moteur, pour chaque entrée de cas.py,
est comparée à une référence enregistrée dans instantanes/<outil>.json.

Une différence = un changement de comportement. S'il est voulu (correction de bug,
nouvelle formulation), régénérer explicitement puis relire le diff git :

    REGENERER=1 uv run -q --no-project --python 3.12 --with sympy==1.13.3 \
        python -m unittest discover -s tests/python -p test_instantanes.py
"""
import hashlib
import json
import math
import os
import unittest

from moteurs import ensemble_def as ed
import derivee_variations as dv
import limites_asymptotes as la
import etude_complete as ec
import factorisation as fa
from cas import CAS_LIMITES, entrees_page, entrees_factorisation

DOSSIER = os.path.join(os.path.dirname(__file__), "instantanes")
REGENERER = os.environ.get("REGENERER") == "1"

OUTILS = {
    "ensemble-definition": (ed.analyser, lambda: entrees_page("ensemble-definition") + CAS_LIMITES["ensemble-definition"]),
    "derivee-variations": (dv.etudier, lambda: entrees_page("derivee-variations") + CAS_LIMITES["derivee-variations"]),
    "limites-asymptotes": (la.etudier, lambda: entrees_page("limites-asymptotes") + CAS_LIMITES["limites-asymptotes"]),
    "etude-complete": (ec.etudier, lambda: entrees_page("etude-complete") + CAS_LIMITES["etude-complete"]),
    "factorisation": (fa.factoriser_expr, entrees_factorisation),
}


def normaliser(v):
    """Arrondit les flottants à 9 chiffres significatifs : les dernières décimales de
    math.log/exp peuvent différer d'une plateforme à l'autre (macOS / Linux de la CI)."""
    if isinstance(v, float):
        if not math.isfinite(v) or v == 0:
            return v
        return float(f"{v:.9g}")
    if isinstance(v, dict):
        return {k: normaliser(x) for k, x in v.items()}
    if isinstance(v, (list, tuple)):
        return [normaliser(x) for x in v]
    return v


def resumer_segments(v):
    """Les points du graphique (des milliers) sont remplacés par un résumé : nombre de
    points, extrémités et empreinte des valeurs arrondies à 6 chiffres significatifs.
    Un changement reste détecté sans rendre l'instantané illisible."""
    if isinstance(v, dict):
        out = {}
        for k, x in v.items():
            if k == "segments" and isinstance(x, list):
                out[k] = [{"n": len(seg), "premier": seg[0] if seg else None, "dernier": seg[-1] if seg else None,
                           "empreinte": hashlib.sha256(json.dumps(
                               [[None if c is None else float(f"{c:.6g}") for c in pt] for pt in seg]
                           ).encode()).hexdigest()[:16]} for seg in x]
            else:
                out[k] = resumer_segments(x)
        return out
    if isinstance(v, list):
        return [resumer_segments(x) for x in v]
    return v


def sortie(fn, entree):
    try:
        return normaliser(resumer_segments(fn(entree)))
    except Exception as e:   # comportement actuel figé, y compris les plantages connus
        return {"exception": type(e).__name__, "message": str(e)}


def calculer(outil):
    fn, entrees = OUTILS[outil]
    vues, res = set(), {}
    for e in entrees():
        if e not in vues:
            vues.add(e)
            res[e] = sortie(fn, e)
    return res


class TestInstantanes(unittest.TestCase):
    def verifier_outil(self, outil):
        chemin = os.path.join(DOSSIER, outil + ".json")
        actuel = calculer(outil)
        if REGENERER:
            os.makedirs(DOSSIER, exist_ok=True)
            with open(chemin, "w", encoding="utf-8") as f:
                json.dump(actuel, f, ensure_ascii=False, indent=1, sort_keys=True)
                f.write("\n")
            self.skipTest(f"instantané régénéré : {chemin}")
        self.assertTrue(os.path.exists(chemin), f"instantané absent : lancer avec REGENERER=1 ({chemin})")
        with open(chemin, encoding="utf-8") as f:
            reference = json.load(f)
        self.assertEqual(sorted(actuel), sorted(reference),
                         "liste des entrées modifiée (exemples d'une page ?) : régénérer avec REGENERER=1")
        for entree in actuel:
            with self.subTest(outil=outil, entree=entree):
                self.assertEqual(actuel[entree], reference[entree])

    def test_ensemble_definition(self):
        self.verifier_outil("ensemble-definition")

    def test_derivee_variations(self):
        self.verifier_outil("derivee-variations")

    def test_limites_asymptotes(self):
        self.verifier_outil("limites-asymptotes")

    def test_etude_complete(self):
        self.verifier_outil("etude-complete")

    def test_factorisation(self):
        self.verifier_outil("factorisation")


if __name__ == "__main__":
    unittest.main()
