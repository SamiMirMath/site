"""Chantier « etude-complete » : temps natif de etudier() sur les 5 fonctions du corpus (Ex7, a–d), à noter dans suivi.md à chaque partie.

Chaque mesure se fait dans un processus neuf (le cache par entrée prévu en P2, D19, ne fausse donc rien) : import des moteurs, un premier
etudier() de chauffe sur une autre fonction (SymPy déjà chargé), puis UN appel chronométré. Trois processus par fonction, on garde la médiane.

    uv run -q --no-project --python 3.12 --with sympy==1.13.3 --with mpmath==1.3.0 python docs/chantiers/etude-complete/mesurer_temps.py
"""
import os
import statistics
import subprocess
import sys

RACINE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
FONCTIONS = [("Ex7", "e^((x^2+x-2)/(6x-12))"), ("a", "e^(-x^2)"), ("b", "(x^2-6)e^(-2x)"), ("c", "e^x(6-e^x)"), ("d", "e^(2/(x^2-4))")]
MESURE = """
import sys, time
sys.path.insert(0, {tests!r})
from moteurs import ensemble_def
import etude_complete as ec
ec.etudier("x^3-3x")
t = time.perf_counter()
r = ec.etudier({saisie!r})
print(time.perf_counter() - t if r["ok"] else -1)
"""


def mesurer(saisie, n=3):
    temps = []
    for _ in range(n):
        code = MESURE.format(tests=os.path.join(RACINE, "tests", "python"), saisie=saisie)
        sortie = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, check=True,
                                env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"})
        temps.append(float(sortie.stdout.strip().splitlines()[-1]))
    return statistics.median(temps)


if __name__ == "__main__":
    for ident, saisie in FONCTIONS:
        print(f"{ident}\t{saisie}\t{mesurer(saisie):.2f} s", flush=True)
