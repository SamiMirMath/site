"""Accès aux moteurs Python du site depuis les tests (mêmes fichiers que ceux
chargés par Pyodide). Versions de référence : Python 3.12, SymPy 1.13.3
(= Pyodide 0.27.7)."""
import math
import os
import sys

RACINE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
for dossier in ("ensemble-definition", "moteur", "derivee-variations", "limites-asymptotes",
                "etude-complete", "factorisation", "exponentielles-logarithmes"):
    chemin = os.path.join(RACINE, dossier)
    if chemin not in sys.path:
        sys.path.insert(0, chemin)

import ensemble_def  # noqa: E402

if ensemble_def._sympy() is None:
    raise RuntimeError("SymPy est requis pour les tests (version de référence 1.13.3).")


def derivee_numerique(arbre, x, h=1e-6):
    """f'(x) par différence centrée, avec l'évaluateur de l'arbre (indépendant de SymPy)."""
    a = ensemble_def.evaluer(arbre, x + h)
    b = ensemble_def.evaluer(arbre, x - h)
    if a is None or b is None:
        return None
    return (a - b) / (2 * h)


def proches(a, b, tol=1e-5):
    return abs(a - b) <= tol * (1 + abs(a) + abs(b))


def texte_etape(it):
    """Tout le texte d'une étape de dérivée (`deriv_etapes`) : le html d'un bloc texte ; pour un tableau u, v / u′, v′ (bloc « uv ») ou
    la sous-carte « Dérivée de l'exposant » (bloc « sous_calcul »), toutes ses chaînes mises bout à bout (décisions EC, D7, D8)."""
    if it["type"] == "texte":
        return it["html"]

    def chaines(v):
        if isinstance(v, str):
            yield v
        elif isinstance(v, dict):
            for k, x in v.items():
                if k not in ("type", "style"):
                    yield from chaines(x)
        elif isinstance(v, list):
            for x in v:
                yield from chaines(x)
    return " ".join(chaines(it))
