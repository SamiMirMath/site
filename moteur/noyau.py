"""
noyau.py — Interface publique du noyau de calcul (ensemble_def.py).

Les moteurs des outils (dérivée, limites, étude complète, factorisation, et les outils à venir)
importent d'ici et jamais de ensemble_def.py : aucun nom commençant par « _ » ne traverse la
frontière du noyau. ensemble_def.py reste intact ; ce fichier ne fait que réexporter.

Trois noms privés du noyau reçoivent un nom public :
    _sympy    → charger_sympy   (module sympy, ou None s'il manque)
    _SP       → SYMPY           (dict partagé : SYMPY["sp"] = sympy, SYMPY["x"] = Symbol x réel)
    _analyser → analyser_complet (comme analyser, mais renvoie (résultat, arbre, ED))
"""
from ensemble_def import (
    # arbre syntaxique et lecture de la saisie
    Nb, X, E, Neg, Op, Fn, lire, tex, par, prec, txt, qtex, ptex,
    valeur_constante, sans_x, aplatir, indice_racine, apercu_json,
    # ensembles de réels (intervalles) et ensemble de définition
    Num, Iv, REELS, inter, fusion, complement, contient, points, ens_tex, domaine,
    # évaluation numérique et résolution
    evaluer, proche, preimage, resoudre_general,
    # polynômes exacts
    pn, deg, peval, pdivlin, pmul, padd, pscal, nul, decomposer, r_norm,
    trinome, racine_rationnelle,
    # tableaux de signes
    signe_facteur, tableau_facteurs,
    # pont vers SymPy
    en_sympy, en_sympy_reel, arbre_depuis_sympy, num_sympy,
    _sympy as charger_sympy, _SP as SYMPY, _analyser as analyser_complet,
    # erreurs et sortie JSON
    ErreurSaisie, NonPrisEnCharge, Incertain, json_strict, ajouter_saisie,
)
