"""Cache explicite des sorties de l'outil Limites, pour les tests (chantier tests-rapides, décision T4).

`etudier_la(entree, avec_bornes=False)` rend la même chose que `la.etudier(entree, avec_bornes=…)`, mais le moteur n'est appelé
qu'une fois par entrée et par processus : le résultat est gardé, et **chaque appel rend une copie profonde** du résultat gardé
(un test qui modifie ce qu'il reçoit ne change ni le cache ni l'appel suivant). Une exception du moteur n'est jamais gardée :
elle est levée de nouveau, et l'appel suivant relance le moteur.

Règles (decisions.md §0 et T4) :
- le cache est **explicite** : il ne remplace jamais `la.etudier` (aucun attribut du moteur n'est touché) ; seul un test qui appelle
  `memo.etudier_la` en profite ;
- seuls les fichiers de test **sans aucun mock** (ni `unittest.mock`, ni `patch`, ni monkeypatch, ni remplacement d'attribut du
  moteur) importent ce module, décision par fichier entier : `test_memo_garde.py` le vérifie ;
- `MEMO=0` (variable d'environnement, lue à chaque appel) coupe le cache entièrement : chaque appel est un appel direct du moteur,
  et rien n'est gardé.

Le cache est en mémoire, propre à chaque processus (xdist), jamais sur disque. Ce n'est pas une fixture pytest : les tests restent
des `unittest.TestCase`, lançables avec `python -m unittest`."""
import copy
import os

import moteurs  # noqa: F401  (chemins des moteurs + SymPy)
import limites_asymptotes as la

_SORTIES = {}


def actif():
    """Faux si MEMO=0 : le cache est alors coupé."""
    return os.environ.get("MEMO") != "0"


def etudier_la(entree, avec_bornes=False):
    """`la.etudier(entree, avec_bornes=avec_bornes)`, gardé par processus ; copie profonde à chaque appel (sauf MEMO=0 : appel direct)."""
    if not actif():
        return la.etudier(entree, avec_bornes=avec_bornes)
    cle = (entree, avec_bornes)
    if cle not in _SORTIES:
        _SORTIES[cle] = copy.deepcopy(la.etudier(entree, avec_bornes=avec_bornes))
    return copy.deepcopy(_SORTIES[cle])


def vider():
    """Oublie tous les résultats gardés (pour les tests de ce module)."""
    _SORTIES.clear()
