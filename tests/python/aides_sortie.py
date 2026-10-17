"""Aides communes aux tests du format de sortie commun (T12)."""
import json

import sortie as so


def chaines(v, exclure=()):
    """Toutes les chaînes d'une ancienne sortie (hors clés exclues)."""
    if isinstance(v, str):
        return [v]
    if isinstance(v, dict):
        return [s for k, x in v.items() if k not in exclure for s in chaines(x, exclure)]
    if isinstance(v, (list, tuple)):
        return [s for x in v for s in chaines(x, exclure)]
    return []


def tout_le_texte(sortie):
    """Toutes les chaînes d'une sortie de `resoudre`, mises bout à bout."""
    return "\n".join(chaines(sortie))


def manquantes(ancien, nouveau, exclure=("detail", "ok", "secours")):
    """Chaînes de l'ancienne sortie absentes de la nouvelle (hors champs techniques)."""
    texte = tout_le_texte(nouveau)
    return [s for s in chaines(ancien, exclure) if s and s not in texte]


def cartes_et_entete(sortie):
    return ([sortie["entete"]] if "entete" in sortie else []) + sortie["cartes"]


def blocs_de_type(sortie, type_):
    return [b for c in cartes_et_entete(sortie) for b in c["blocs"] if b["type"] == type_]


def en_json(sortie):
    return json.dumps(sortie, ensure_ascii=False, allow_nan=False)


def valide(test, sortie):
    test.assertEqual(so.valider(sortie), [])
    en_json(sortie)
