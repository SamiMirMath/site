"""Corpus de l'enseignant pour l'outil « Limites et asymptotes » (3M) : corrigé du chapitre 8 (exercices 8.11 à 8.14, exemples 5 et 6),
exercices 3.8, 3.10, 3.11 et feuille eˣ (docs/reference/limites/). Chantier « Limites et asymptotes », étape 1 (29.10.2026).

Une ligne de CAS = une limite : identifiant, saisie de l'outil, expression SymPy INDÉPENDANTE du parseur de l'outil (`ref`), point
('+oo', '-oo' ou nombre exact SymPy), côté ('' en ±∞, '+' ou '-'), valeur exacte attendue (chaîne SymPy : 'oo', '-oo', '0', 'log(3)'…) et,
quand la valeur est 0, le signe d'approche ('+' pour 0⁺, '-' pour 0⁻) calculé par SymPy à partir de 1/f.
Les valeurs de ce fichier sont elles-mêmes recoupées par mpmath (50 chiffres) dans test_corpus_limites_3m.py.

PAS_PRIS_EN_CHARGE : identifiants dont la fonction (cos, sin, log_a) n'est pas encore lue par l'outil (message attendu, voir le test).
ETUDES : asymptotes attendues pour les exercices 3.10 et 3.11 : (genre, position, valeur) ; position = '+oo', '-oo' ou l'abscisse exacte,
valeur = ordonnée de l'asymptote horizontale ou du trou (None sinon).
"""
from collections import namedtuple

Cas = namedtuple("Cas", "id saisie ref point cote attendu signe0")


def cas(*champs):
    return Cas(*champs)


CAS = [
    cas('8.11a', 'e^x/ln(x)', 'exp(x)/log(x)', '+oo', '', 'oo', None),
    cas('8.11b', 'x^3*ln(x)', 'x**3*log(x)', '0', '+', '0', '-'),
    cas('8.11c', 'x^2*e^x', 'x**2*exp(x)', '-oo', '', '0', '+'),
    cas('8.11d', 'x^2*e^(-5x)', 'x**2*exp(-5*x)', '+oo', '', '0', '+'),
    cas('Ex5a', 'x^2*e^(-x)', 'x**2*exp(-x)', '+oo', '', '0', '+'),
    cas('Ex5b', 'x*e^(1/x)', 'x*exp(1/x)', '0', '+', 'oo', None),
    cas('Ex5c', 'e^(-x)/x^2', 'exp(-x)/x**2', '-oo', '', 'oo', None),
    cas('Ex5d', 'e^(-x)/(4x)', 'exp(-x)/(4*x)', '+oo', '', '0', '+'),
    cas('8.12a', 'ln(x)/e^(2x)', 'exp(-2*x)*log(x)', '+oo', '', '0', '+'),
    cas('8.12b', 'e^(-x)*ln(x^3)', 'exp(-x)*log(x**3)', '+oo', '', '0', '+'),
    cas('8.12c', 'e^(-x)*x', 'x*exp(-x)', '-oo', '', '-oo', None),
    cas('8.12d', 'e^x*ln(-x)', 'exp(x)*log(-x)', '-oo', '', '0', '+'),
    cas('8.12e', 'x^3*e^(3x-5)', 'x**3*exp(3*x - 5)', '-oo', '', '0', '-'),
    cas('8.12f', 'e^(1/x)/x^2', 'exp(1/x)/x**2', '0', '+', 'oo', None),
    cas('8.12g', 'e^(1/x)*x^2', 'x**2*exp(1/x)', '0', '+', 'oo', None),
    cas('8.12h', 'e^(-1/x)/x', 'exp(-1/x)/x', '0', '+', '0', '+'),
    cas('Ex6', 'e^((3x+4)/(x-2))', 'exp((3*x + 4)/(x - 2))', '+oo', '', 'exp(3)', None),
    cas('Ex6cours', 'e^(-(3x+4)/(x-2))', 'exp((-3*x - 4)/(x - 2))', '+oo', '', 'exp(-3)', None),
    cas('8.13a', 'e^(-x)', 'exp(-x)', '+oo', '', '0', '+'),
    cas('8.13b', 'e^((x^2-3x+2)/(2x^2))', 'exp((x**2 - 3*x + 2)/(2*x**2))', '+oo', '', 'exp(1/2)', None),
    cas('8.13c', 'e^(-2x/(x^2-5))', 'exp(-2*x/(x**2 - 5))', '+oo', '', '1', None),
    cas('8.13d', 'e^((3x^2+2)/(2x))', 'exp((3*x**2 + 2)/(2*x))', '-oo', '', '0', '+'),
    cas('8.13e', 'ln((3x^2-3x+2)/(x^2-5x+2))', 'log((3*x**2 - 3*x + 2)/(x**2 - 5*x + 2))', '+oo', '', 'log(3)', None),
    cas('8.13f', 'ln(1/x)', 'log(1/x)', '+oo', '', '-oo', None),
    cas('8.14', 'ln(1+e^x)/e^x', 'exp(-x)*log(exp(x) + 1)', '-oo', '', '1', None),
    cas('3.8a', 'ln(x+1)/x', 'log(x + 1)/x', '0', '-', '1', None),
    cas('3.8a', 'ln(x+1)/x', 'log(x + 1)/x', '0', '+', '1', None),
    cas('3.8b', 'ln(cos(x))/x^2', 'log(cos(x))/x**2', '0', '-', '-1/2', None),
    cas('3.8b', 'ln(cos(x))/x^2', 'log(cos(x))/x**2', '0', '+', '-1/2', None),
    cas('3.8c', '(ln(x)-1)/(x-e)', '(log(x) - 1)/(x - E)', 'E', '-', 'exp(-1)', None),
    cas('3.8c', '(ln(x)-1)/(x-e)', '(log(x) - 1)/(x - E)', 'E', '+', 'exp(-1)', None),
    cas('3.8d', 'ln(x^2-3)/(2-x)', 'log(x**2 - 3)/(2 - x)', '2', '-', '-4', None),
    cas('3.8d', 'ln(x^2-3)/(2-x)', 'log(x**2 - 3)/(2 - x)', '2', '+', '-4', None),
    cas('3.8e', 'ln(x^2+1)/x', 'log(x**2 + 1)/x', '-oo', '', '0', '-'),
    cas('3.8f', '(ln(x)+1)/(1-ln(x))', '(log(x) + 1)/(1 - log(x))', '+oo', '', '-1', None),
    cas('3.8g', 'ln(x^2)/ln(x)^2', 'log(x**2)/log(x)**2', '+oo', '', '0', '+'),
    cas('3.8h', 'ln(x)/e^x', 'exp(-x)*log(x)', '+oo', '', '0', '+'),
    cas("3.8g'", '(8^x-2^x)/(4x)', '(-2**x + 8**x)/(4*x)', '0', '-', 'log(2)/2', None),
    cas("3.8g'", '(8^x-2^x)/(4x)', '(-2**x + 8**x)/(4*x)', '0', '+', 'log(2)/2', None),
    cas("3.8h'", 'log_5(x+2)/(x+1)', 'log(x + 2)/((x + 1)*log(5))', '-1', '-', '1/log(5)', None),
    cas("3.8h'", 'log_5(x+2)/(x+1)', 'log(x + 2)/((x + 1)*log(5))', '-1', '+', '1/log(5)', None),
    cas('Fa', '(e^x-e^2)/(x-2)', '(exp(x) - exp(2))/(x - 2)', '2', '-', 'exp(2)', None),
    cas('Fa', '(e^x-e^2)/(x-2)', '(exp(x) - exp(2))/(x - 2)', '2', '+', 'exp(2)', None),
    cas('Fb', '(e^x-1)/sin(x)', '(exp(x) - 1)/sin(x)', '0', '-', '1', None),
    cas('Fb', '(e^x-1)/sin(x)', '(exp(x) - 1)/sin(x)', '0', '+', '1', None),
    cas('Fc', 'x*e^x/(1-e^x)', 'x*exp(x)/(1 - exp(x))', '0', '-', '-1', None),
    cas('Fc', 'x*e^x/(1-e^x)', 'x*exp(x)/(1 - exp(x))', '0', '+', '-1', None),
    cas('Fd', 'x*e^(1/x)', 'x*exp(1/x)', '0', '+', 'oo', None),
    cas('Fe', '(e^x+e^(-x))/(2x)', '(exp(x) + exp(-x))/(2*x)', '-oo', '', '-oo', None),
    cas('Ff', '(2e^x-1)/(e^x+2)', '(2*exp(x) - 1)/(exp(x) + 2)', '+oo', '', '2', None),
    cas('Fg', '(x^2+x)*e^x', '(x**2 + x)*exp(x)', '-oo', '', '0', '+'),
    cas('Fh', 'e^x/(x^2-2x+3)', 'exp(x)/(x**2 - 2*x + 3)', '+oo', '', 'oo', None),
]

PAS_PRIS_EN_CHARGE = {
    "3.8b": "La fonction cos n'est pas encore prise en charge par cet outil.",
    "Fb": "La fonction sin n'est pas encore prise en charge par cet outil.",
    "3.8h'": "La fonction log_a (logarithme de base a) n'est pas encore prise en charge par cet outil.",
}

ETUDES = [
    ("3.10a", "e^(-x^2)", [("horizontale", "-oo", "0"), ("horizontale", "+oo", "0")]),
    ("3.10b", "e^(1/x)", [("horizontale", "-oo", "1"), ("horizontale", "+oo", "1"), ("verticale", "0", None)]),
    ("3.10c", "(x^2-4x+4)e^x", [("horizontale", "-oo", "0")]),
    ("3.10d", "x/e^x", [("horizontale", "+oo", "0")]),
    ("3.10e", "(e^x+2)/(1-3e^x)", [("horizontale", "-oo", "2"), ("horizontale", "+oo", "-1/3"), ("verticale", "-log(3)", None)]),
    ("3.11a", "x^2*ln(x)", [("trou", "0", "0")]),
    ("3.11b", "ln(x^2+1)", []),
    ("3.11c", "ln(x)/x", [("verticale", "0", None), ("horizontale", "+oo", "0")]),
    ("3.11d", "ln(2x/(x+1))", [("horizontale", "-oo", "log(2)"), ("horizontale", "+oo", "log(2)"), ("verticale", "-1", None),
                               ("verticale", "0", None)]),
    ("3.11e", "(ln(x)-2)/(ln(x)-1)", [("trou", "0", "1"), ("horizontale", "+oo", "1"), ("verticale", "E", None)]),
]
