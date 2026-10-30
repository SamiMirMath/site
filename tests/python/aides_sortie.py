"""Aides communes aux tests du format de sortie commun (T12) et au vouvoiement des textes destinés à l'élève."""
import ast
import json
import re

import sortie as so

# Vouvoiement : l'enseignant vouvoie ses élèves. Trois familles, pour limiter les faux positifs :
#  - pronoms et possessifs de la 2e personne du singulier (tu, ton, ta, tes, toi) ;
#  - impératifs en -e/-s peu ambigus, n'importe où (« choisis », « ouvre », « mets »…) ;
#  - impératifs en début de phrase ou de chaîne, avec la majuscule : une phrase française ne commence pas par un verbe conjugué à la
#    3e personne sans sujet (« Écris… », « Utilise… ») ; « on utilise » au milieu d'une phrase n'est donc jamais signalé.
_IMPERATIFS_DEBUT = ("Choisis|Saisis|Écris|Ouvre|Mets|Tape|Clique|Essaie|Vérifie|Utilise|Ajoute|Regarde|Rappelle|Retiens|Pense|Observe|"
                     "Calcule|Résous|Cherche|Prends|Fais|Donne|Simplifie|Développe|Factorise|Dérive|Trace|Complète|Lis|Relis|Reprends|"
                     "Recommence|Reviens|Appuie|Sélectionne|Trouve|Conserve|Corrige|Réessaie|Recharge|Patiente|Attends|Passe|Compare|"
                     "Évite|Commence|Continue|Vois|Rédige|Justifie|Explique")
TUTOIEMENT = re.compile(
    r"(?i:\b(?:tu|ton|ta|tes|toi|toi-même)\b)"
    r"|(?i:\b(?:choisis|saisis|écris|ouvre|mets|essaie|clique|réessaie|retiens|reviens|appuie|patiente)\b)"
    r"|(?:^|[.:;!?»)]\s+|[«(]\s*)(?:" + _IMPERATIFS_DEBUT + r")\b(?![-\w])", re.M)


def chaines_litterales(chemin):
    """[(ligne, texte)] des littéraux texte d'un fichier Python, docstrings exclues : ce que l'élève peut lire (messages d'erreur,
    phrases du corrigé). Les morceaux d'une f-string sont des littéraux séparés."""
    with open(chemin, encoding="utf-8") as f:
        arbre = ast.parse(f.read())
    docstrings = set()
    for n in ast.walk(arbre):
        if isinstance(n, (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) and n.body:
            premier = n.body[0]
            if isinstance(premier, ast.Expr) and isinstance(premier.value, ast.Constant) and isinstance(premier.value.value, str):
                docstrings.add(id(premier.value))
    return [(n.lineno, n.value) for n in ast.walk(arbre)
            if isinstance(n, ast.Constant) and isinstance(n.value, str) and id(n) not in docstrings]


def chaines(v, exclure=()):
    """Toutes les chaînes d'une ancienne sortie (hors clés exclues)."""
    if isinstance(v, str):
        return [v]
    if isinstance(v, dict):
        if v.get("type") == "descente":          # rédaction descendante des limites : ses blocs deviennent des cartes « Étape n » (testées à part)
            return []
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


def titres_etude(etude):
    """Titres des cartes que produit une borne d'une étude de limites : « Limite » seule (ancienne rédaction) ou, pour chaque rédaction
    descendante, « Limite » (l'énoncé) puis « Étape n : titre. » ; les lignes qui suivent rejoignent la dernière étape."""
    items = etude["etapes"]
    if not any(i.get("type") == "descente" for i in items):
        return ["Limite"]
    out, attente = [], False
    for it in items:
        if it.get("type") == "descente":
            if attente:
                out.append("Limite")
                attente = False
            out.append("Limite")
            out += [f"Étape {i} : {e['titre']}." for i, e in enumerate(it["etapes"], 1)]
        elif not (out and out[-1].startswith("Étape")):
            attente = True
    return out + (["Limite"] if attente else [])
