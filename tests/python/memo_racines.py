"""Cache explicite de l'oracle `racines` (tests/python/test_exp_log_m.py), pour les tests (chantier tests-rapides, décision T5).

`racines(s)` rend la même chose que `test_exp_log_m.racines(s)`, mais l'oracle n'est appelé qu'une fois par clé et par processus : le
résultat est gardé, et **chaque appel rend une copie profonde** du résultat gardé (un test qui modifie la liste reçue ne change ni le
cache ni l'appel suivant). Une exception de l'oracle n'est jamais gardée : elle remonte, et l'appel suivant relance l'oracle.

Règles (decisions.md §0 et T5) :
- l'oracle n'est **pas modifié** : ni sa signature, ni son corps, ni sa grille, ni ses tolérances (`test_memo_racines.py` en garde
  l'empreinte) ; ce module l'enveloppe et ne remplace aucun attribut ; seul un test qui appelle `memo_racines.racines` en profite ;
- la clé est un instantané immuable de **tout** ce que l'oracle peut lire (voir `cle`) ; quand l'argument contient autre chose que les
  types prévus, il n'y a pas de clé et l'oracle est appelé directement ;
- `MEMO=0` (variable d'environnement, lue à chaque appel) coupe ce cache entièrement, comme celui de `memo.py` : chaque appel est un
  appel direct de l'oracle, et rien n'est gardé.

Ce module n'importe pas `memo` (la garde de `memo`, `test_memo_garde.py`, porte sur les fichiers qui importent `memo`). Sa propre garde
est dans `test_memo_racines.py`. Le cache est en mémoire, propre à chaque processus (xdist), jamais sur disque."""
import copy
import os
from fractions import Fraction

import moteurs  # noqa: F401  (chemins des moteurs)
import exp_log as el

# Les nœuds que l'oracle (`evaluer`) sait lire, par type exact (une sous-classe n'est pas acceptée) ; leurs champs : tous les
# __slots__ de la classe et de ses parents (ces classes n'ont pas de __dict__).
NOMS_NOEUDS = ("Nb", "Var", "E", "Pi", "Neg", "Op", "Pow", "Fn", "Log", "Defini")
_NOEUDS = tuple(getattr(el, nom) for nom in NOMS_NOEUDS)

_RACINES = {}


class HorsCle(Exception):
    """L'argument contient un objet hors des types prévus : pas de clé, appel direct de l'oracle."""


def actif():
    """Faux si MEMO=0 : le cache est alors coupé (même interrupteur que memo.py)."""
    return os.environ.get("MEMO") != "0"


def oracle():
    """Le module de l'oracle, importé à l'appel (test_exp_log_m importe ce module : pas d'import circulaire au chargement)."""
    import test_exp_log_m
    return test_exp_log_m


def champs(t):
    """Tous les champs (__slots__) d'une classe de nœud, parents compris, dans l'ordre de la hiérarchie."""
    return tuple(nom for c in reversed(t.__mro__) for nom in c.__dict__.get("__slots__", ()))


def figer(v):
    """Instantané immuable et injectif de v : deux instantanés égaux viennent d'objets de mêmes types exacts, aux champs égaux un à un."""
    t = type(v)
    if t in _NOEUDS:
        if hasattr(v, "__dict__"):
            raise HorsCle(t)
        try:
            return (t,) + tuple(figer(getattr(v, nom)) for nom in champs(t))
        except AttributeError as e:                     # champ non rempli
            raise HorsCle(t) from e
    if t is el.Saisie:
        return (t,) + tuple(figer(x) for x in v)
    if t is tuple:
        return (t,) + tuple(figer(x) for x in v)
    if t is Fraction:
        return (t, v.numerator, v.denominator)
    if t is str:
        return (t, v)
    if v is None:
        return (t,)
    raise HorsCle(t)


def contexte(o):
    """Ce dont dépend l'oracle en dehors de son argument : ses fonctions, son contexte mpmath (objet, précision, arrondi) et les classes
    de nœuds que `evaluer` lit dans exp_log au moment de l'appel."""
    return (o.racines, o.ecart, o.evaluer, o.MP, o.MP.prec, o.MP.dps, tuple(o.MP._prec_rounding),
            tuple(getattr(el, nom) for nom in NOMS_NOEUDS), _NOEUDS)


def cle(s):
    """La clé de `racines(s)` ; lève HorsCle si s contient un objet hors des types prévus."""
    try:
        return (contexte(oracle()), figer(s))
    except RecursionError as e:
        raise HorsCle("arbre trop profond") from e


def racines(s):
    """`test_exp_log_m.racines(s)`, gardé par processus ; copie profonde à chaque appel (sauf MEMO=0 ou argument hors clé : appel direct)."""
    o = oracle()
    if not actif():
        return o.racines(s)
    try:
        k = cle(s)
    except HorsCle:
        return o.racines(s)
    if k not in _RACINES:
        _RACINES[k] = copy.deepcopy(o.racines(s))
    return copy.deepcopy(_RACINES[k])


def vider():
    """Oublie tous les résultats gardés (pour les tests de ce module)."""
    _RACINES.clear()
