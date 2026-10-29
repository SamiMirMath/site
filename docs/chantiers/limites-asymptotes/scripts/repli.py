# repli.py — audit de l'étape 0 du chantier « Limites et asymptotes » (3M).
# Sert à : afficher la raison technique (clé `detail`, « Abandon : … ») de chaque phrase de repli
# « Le calcul détaillé de cette limite n'est pas rédigé ici » pour les cas du corpus qui y tombent
# (Ex5c, 8.12e, 8.12f, 8.12h, 3.8g, 3.8g′, Ex5b, 8.13e). Ne modifie aucun fichier.
# Lancer, depuis la racine du dépôt :
#   uv run -q --no-project --python 3.12 --with sympy==1.13.3 --with mpmath==1.3.0 python -I docs/chantiers/limites-asymptotes/scripts/repli.py
# Sortie : une ligne « saisie [borne] -> raison » par repli. Pour changer de saisies, modifier la liste de la boucle `for s in [...]`.
# Écrit le 29.10.2026 .
import sys, os
R = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))      # racine du dépôt
for d in ("ensemble-definition", "moteur", "limites-asymptotes"):
    sys.path.insert(0, os.path.join(R, d))
from limites_asymptotes import etudier
for s in ["e^(-x)/x^2","x^3*e^(3x-5)","e^(1/x)/x^2","e^(-1/x)/x","ln(x^2)/ln(x)^2","(8^x-2^x)/(4x)","x*e^(1/x)","ln((3x^2-3x+2)/(x^2-5x+2))"]:
    r = etudier(s)
    for et in r["etudes"]:
        for i in et["etapes"]:
            if i.get("detail"):
                print(f"{s} [{et['ou']}] -> {str(i['detail'])[:260]}")
