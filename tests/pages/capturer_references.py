"""Enregistre le rendu actuel des pages (références pour les migrations T16 à T20).

    uv run -q --no-project --python 3.12 --with websockets python tests/pages/capturer_references.py [outil …]

À lancer AVANT de modifier le rendu d'une page ; à relancer seulement pour un changement voulu
(puis relire le diff git)."""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from navigateur import Navigateur
from rendu import DOSSIER_REFERENCES, OUTIL_M, OUTILS, capturer_outil


def main(outils):
    os.makedirs(DOSSIER_REFERENCES, exist_ok=True)
    with Navigateur() as nav:
        for outil in outils:
            res = capturer_outil(nav, outil)
            chemin = os.path.join(DOSSIER_REFERENCES, outil + ".json")
            with open(chemin, "w", encoding="utf-8") as f:
                json.dump(res, f, ensure_ascii=False, indent=1, sort_keys=True)
                f.write("\n")
            print(f"{outil} : {len(res)} entrées -> {chemin}", flush=True)


if __name__ == "__main__":
    main(sys.argv[1:] or OUTILS + [OUTIL_M])
