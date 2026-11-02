"""Corpus de l'enseignant pour l'outil « Étude complète » (3M) : exemple 7 et exercice 8.15 a–d du corrigé
docs/reference/etude-complete/3MSt_Ch8_EtudesFonctions_Corrige.tex. Chantier « etude-complete », partie P0 (02.11.2026).
Les résultats attendus sont ceux de docs/chantiers/etude-complete/decisions.md, §4 (Ex7) et §5 (a–d).

Chaque fonction est écrite À LA MAIN en mpmath (`f`, et sa dérivée `fp` telle que l'écrit le corrigé) : ni le parseur de l'outil ni SymPy
ne servent à l'oracle. Les valeurs exactes sont données par leur écriture (chaîne lisible, pour l'enseignant) et par leur valeur mpmath ;
les valeurs approchées par la chaîne attendue à l'écran (virgule décimale, règle d'arrondi de decisions.md §2).
Tout est recoupé dans test_corpus_etude_complete.py (oracle mpmath 50 chiffres), puis comparé à la sortie de l'outil.

Champs d'une FONCTION :
- id, saisie (chaîne tapée dans l'outil), role ('exemple' ou 'exercice', D18) ;
- f, fp : fonctions mpmath (fp = dérivée du corrigé ; ZeroDivisionError hors de l'ED) ;
- exclus : valeurs interdites (ED = ℝ privé de ces valeurs) ;
- parite : 'paire', 'impaire' ou 'ni' ; non_symetrique : a ∈ ED avec −a ∉ ED (D4, règle 1), sinon None ;
  contre_exemple : (a, f(a) ≈, f(−a) ≈) pour « pas paire » (D4, règle 3), sinon None ;
- zeros : [(écriture, valeur, ≈)] dans l'ordre croissant ; signe : signes de f sur les intervalles délimités par les zéros et les valeurs
  interdites (de gauche à droite) ;
- f0 : (écriture, valeur, ≈) de f(0), ou None si 0 ∉ ED ;
- limites : [(point, côté, valeur, signe)] ; point '-oo', '+oo' ou nombre ; côté '' en ±∞, '-' ou '+' ; valeur 'oo', '-oo' ou nombre ;
  signe d'approche '+' / '-' pour une limite finie (0⁺, 1⁺…), None pour une limite infinie ;
- regroupe_infini : les chaînes en −∞ et en +∞ sont identiques au symbole près (D16) ;
- extremums : [Extremum] ; global_ : True / False selon D11 ; raison : (point, côté) d'une limite qui dépasse la valeur (« pas global »), sinon None ;
- horizontales : [(côté '-oo' / '+oo', valeur L, position 'au-dessus' / 'au-dessous')] ;
- verticales : [(abscisse, côtés 'gauche' / 'droite' / 'deux')] : côtés où la limite est infinie ;
- ronds_vides : [(x, y)] : points exclus dont la limite est finie d'un côté au moins (D15) ;
- pentes : [(point, côté, valeur, signe)] : lim f′ au point exclu, du côté où f a une limite finie (D14, partie P10 facultative).
"""
from collections import namedtuple

import mpmath

mp = mpmath.mp
mp.dps = 50

Extremum = namedtuple("Extremum", "genre x_ecrit x y_ecrit y approx_x approx_y global_ raison")
Fonction = namedtuple("Fonction", "id saisie role f fp exclus parite non_symetrique contre_exemple zeros signe f0 limites "
                                  "regroupe_infini extremums horizontales verticales ronds_vides pentes")

UN = mp.mpf(1)


# Ex7 : f(x) = e^{(x² + x − 2)/(6x − 12)} ; f′(x) = x(x − 4)/(6(x − 2)²) · e^{g(x)}
def _g7(x):
    return (x ** 2 + x - 2) / (6 * x - 12)


def _f7(x):
    return mp.exp(_g7(x))


def _fp7(x):
    return x * (x - 4) / (6 * (x - 2) ** 2) * mp.exp(_g7(x))


# a : f(x) = e^{−x²} ; f′(x) = −2x e^{−x²}
def _fa(x):
    return mp.exp(-x ** 2)


def _fpa(x):
    return -2 * x * mp.exp(-x ** 2)


# b : f(x) = (x² − 6)e^{−2x} ; f′(x) = −2e^{−2x}(x − 3)(x + 2)
def _fb(x):
    return (x ** 2 - 6) * mp.exp(-2 * x)


def _fpb(x):
    return -2 * mp.exp(-2 * x) * (x - 3) * (x + 2)


# c : f(x) = eˣ(6 − eˣ) ; f′(x) = 2eˣ(3 − eˣ)
def _fc(x):
    return mp.exp(x) * (6 - mp.exp(x))


def _fpc(x):
    return 2 * mp.exp(x) * (3 - mp.exp(x))


# d : f(x) = e^{2/(x² − 4)} ; f′(x) = −4x/(x² − 4)² · e^{2/(x² − 4)}
def _fd(x):
    return mp.exp(2 / (x ** 2 - 4))


def _fpd(x):
    return -4 * x / (x ** 2 - 4) ** 2 * mp.exp(2 / (x ** 2 - 4))


FONCTIONS = [
    Fonction(
        id="Ex7", saisie="e^((x^2+x-2)/(6x-12))", role="exemple", f=_f7, fp=_fp7,
        exclus=[mp.mpf(2)],
        parite="ni", non_symetrique=mp.mpf(-2), contre_exemple=None,
        zeros=[], signe=["+", "+"],
        f0=("e^(1/6)", mp.exp(UN / 6), "1,18"),
        limites=[("-oo", "", 0, "+"), (2, "-", 0, "+"), (2, "+", "oo", None), ("+oo", "", "oo", None)],
        regroupe_infini=False,
        extremums=[
            Extremum("maximum", "0", mp.mpf(0), "e^(1/6)", mp.exp(UN / 6), "0", "1,18", False, (2, "+")),
            Extremum("minimum", "4", mp.mpf(4), "e^(3/2)", mp.exp(UN * 3 / 2), "4", "4,48", False, ("-oo", "")),
        ],
        horizontales=[("-oo", 0, "au-dessus")],
        verticales=[(mp.mpf(2), "droite")],
        ronds_vides=[(mp.mpf(2), 0)],
        pentes=[(2, "-", 0, "-")],
    ),
    Fonction(
        id="a", saisie="e^(-x^2)", role="exercice", f=_fa, fp=_fpa,
        exclus=[],
        parite="paire", non_symetrique=None, contre_exemple=None,
        zeros=[], signe=["+"],
        f0=("1", UN, "1"),
        limites=[("-oo", "", 0, "+"), ("+oo", "", 0, "+")],
        regroupe_infini=True,
        extremums=[Extremum("maximum", "0", mp.mpf(0), "1", UN, "0", "1", True, None)],
        horizontales=[("-oo", 0, "au-dessus"), ("+oo", 0, "au-dessus")],
        verticales=[], ronds_vides=[], pentes=[],
    ),
    Fonction(
        id="b", saisie="(x^2-6)e^(-2x)", role="exercice", f=_fb, fp=_fpb,
        exclus=[],
        parite="ni", non_symetrique=None, contre_exemple=(UN, "-0,68", "-36,95"),
        zeros=[("-√6", -mp.sqrt(6), "-2,45"), ("√6", mp.sqrt(6), "2,45")], signe=["+", "-", "+"],
        f0=("-6", mp.mpf(-6), "-6"),
        limites=[("-oo", "", "oo", None), ("+oo", "", 0, "+")],
        regroupe_infini=False,
        extremums=[
            Extremum("minimum", "-2", mp.mpf(-2), "-2e^4", -2 * mp.exp(4), "-2", "-109,20", True, None),
            Extremum("maximum", "3", mp.mpf(3), "3e^(-6)", 3 * mp.exp(-6), "3", "0,0074", False, ("-oo", "")),
        ],
        horizontales=[("+oo", 0, "au-dessus")],
        verticales=[], ronds_vides=[], pentes=[],
    ),
    Fonction(
        id="c", saisie="e^x(6-e^x)", role="exercice", f=_fc, fp=_fpc,
        exclus=[],
        parite="ni", non_symetrique=None, contre_exemple=(UN, "8,92", "2,07"),
        zeros=[("ln 6", mp.log(6), "1,79")], signe=["+", "-"],
        f0=("5", mp.mpf(5), "5"),
        limites=[("-oo", "", 0, "+"), ("+oo", "", "-oo", None)],
        regroupe_infini=False,
        extremums=[Extremum("maximum", "ln 3", mp.log(3), "9", mp.mpf(9), "1,10", "9", True, None)],
        horizontales=[("-oo", 0, "au-dessus")],
        verticales=[], ronds_vides=[], pentes=[],
    ),
    Fonction(
        id="d", saisie="e^(2/(x^2-4))", role="exercice", f=_fd, fp=_fpd,
        exclus=[mp.mpf(-2), mp.mpf(2)],
        parite="paire", non_symetrique=None, contre_exemple=None,
        zeros=[], signe=["+", "+", "+"],
        f0=("e^(-1/2)", mp.exp(-UN / 2), "0,61"),
        limites=[("-oo", "", 1, "+"), (-2, "-", "oo", None), (-2, "+", 0, "+"), (2, "-", 0, "+"), (2, "+", "oo", None),
                 ("+oo", "", 1, "+")],
        regroupe_infini=True,
        extremums=[Extremum("maximum", "0", mp.mpf(0), "e^(-1/2)", mp.exp(-UN / 2), "0", "0,61", False, (2, "+"))],
        horizontales=[("-oo", 1, "au-dessus"), ("+oo", 1, "au-dessus")],
        verticales=[(mp.mpf(-2), "gauche"), (mp.mpf(2), "droite")],
        ronds_vides=[(mp.mpf(-2), 0), (mp.mpf(2), 0)],
        pentes=[(-2, "+", 0, "+"), (2, "-", 0, "-")],
    ),
]

PAR_ID = {fn.id: fn for fn in FONCTIONS}
