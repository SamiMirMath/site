"""Entrées de test partagées : exemples et exercices lus dans les pages (pour suivre
automatiquement toute modification des listes), cas limites des spécifications,
batterie de factorisation (Amaudruz 2.11-2.16, Javet §2.2)."""
import os
import re

from moteurs import RACINE

NIVEAUX = {"facile", "moyen", "difficile", "tresDifficile"}


def entrees_page(dossier):
    """Chaînes des constantes EXEMPLES et EXOS d'une page outil, triées, sans doublon."""
    with open(os.path.join(RACINE, dossier, "index.html"), encoding="utf-8") as f:
        s = f.read()
    out = set()
    for m in re.finditer(r"const (EXEMPLES|EXOS)=(.*?);\n", s, re.S):
        out |= set(re.findall(r'"([^"]+)"', m.group(2)))
    return sorted(out - NIVEAUX)


# Cas limites cités dans docs/specifications/ (comportement actuel figé par les instantanés,
# y compris les bugs connus : leur correction mettra à jour l'instantané, explicitement).
CAS_LIMITES = {
    "ensemble-definition": [
        "x^(2-2)", "x^(1/2-1/2)", "x^0", "1/(1-1)", "ln(-x^2-1)", "sqrt(-x^2)", "ln(ln(ln(x)))",
        "x^x", "sqrt(x-1)/sqrt(x-1)", "1'000x", "1 000x", "x^(1/3)", "(x-1)^(2/3)", "1/x^(1/3)",
        "ln(x^2)-2ln(x)", "e^x/ln(e^x)", "", "ln(", "x+*2", "sin(x)", "y = ln(x-1)", "2,5x+ln(x)",
    ],
    "derivee-variations": [
        "x^(1/2)", "x^(3/2)", "x^(2/3)", "x^(-1/2)", "(x^2+1)^(1/2)", "sqrt(x^2)", "sqrt(x^2-4)",
        "3(x*ln(x))", "-(x*ln(x))", "(x+1)/(x-1)/2", "x*ln(x)+x", "2(x^2+ln(x))", "-x^2", "3x^2-4x",
        "e^(x^2)", "x^3", "x^x", "x^(2-2)",
    ],
    "limites-asymptotes": [
        "(e^x-1)/x", "x*ln(x^2)", "x/sqrt(x^2)", "e^x/x", "x*e^x", "sqrt(x^2+1)", "(x^2-1)/(x-1)",
        "1/(x^2-2)", "x+ln(x)", "e^(1/x)", "x^(1/2)", "(x^3+1)/(x-2)", "(2x^2+1)/(x^2-1)",
    ],
    "etude-complete": [
        "(e^x-1)/x", "x/sqrt(x^2)", "sqrt(x^2-4)", "x^(2/3)", "e^(1/x)", "3(x*ln(x))",
    ],
}

FACTORISATION = {
    "Amaudruz 2.11": ["xy + y", "ma + ap", "a^3x^2 - a^2x^3", "3a^3b^4 - 12a^2b^3", "y(b - a) - x(b - a)",
                      "2a(a - b) - (a - b)^2", "(x - 2y)(a - b) - (b - a)(2x + y)", "(a + b)^3 - (a + b)^2",
                      "a(a + b) - b(a + b) + (a + b)^2",
                      "(2x + 1)(4x + 3) + (3x - 2)(2x + 1) - (2x + 1)^2"],
    "Amaudruz 2.12": ["a^2b^2 - m^2", "x^4 - y^2", "a^2 - 1/16", "(ax + 2y)^2 - (2x - 3y)^2", "a^2 + 2a + 1",
                      "1 + 2x^2 + x^4", "a^4 + 9b^2 - 6a^2b", "9x^4 + 16y^2 + 24x^2y", "x^2 - x + 1/4",
                      "(a + b)^2 - 2(a + b)c + c^2", "x^12 - 125", "z^3 + 8a^3b^6", "27c^3 + 1/64",
                      "a^3 - 8b^3/27", "z^6 + 27", "64x^6 - 1", "1 + 9a + 27a^2 + 27a^3", "z^3 - 6z^2 + 12z - 8",
                      "x^3 + x^2y + xy^2/3 + y^3/27", "x^3 - 3x^2(a + b) + 3x(a + b)^2 - (a + b)^3"],
    "Amaudruz 2.13": ["x^2 + 5x + 6", "x^2 + 5x + 4", "u^2 - 6u + 8", "x^2 - 2x - 35", "x^2 - 2x - 80",
                      "y^2 + 6y + 8", "6x^2 + 5x + 1", "4z^2 + 5z + 1", "x^2 + x + 1", "16u^2 - 72u + 81",
                      "40x^2 + 3x - 28", "9a^2 + 6a + 1"],
    "Amaudruz 2.14": ["x^4 - 13x^2 + 36", "a^6 + 19a^3 - 216", "x^8 - 257x^4 + 256", "7x^4 - 61x^2 - 18",
                      "64c^6 - 91c^3 + 27", "16x^8 - 641x^4 + 625"],
    "Amaudruz 2.15": ["ax + bx + ay + by", "a + b + ax + bx + ay + by", "ax^2 - ay^2 + bx^2 - by^2",
                      "a^2 - b^2 + ac + bc", "a^3 - a^2 - a + 1", "a^3 + 3a^2 - a - 3", "x^5 - 1 + x^4 - x",
                      "(a + b)^2 + a(a + b) + a^2 - b^2"],
    "Amaudruz 2.16": ["x^3 + 2x^2 + x", "2a^6 - 6a^4 + 6a^2 - 2", "9a^3 - ab^2", "54a^6 - 2", "1 - (x - y)^2",
                      "(x^2 - 1)^2 + 4x^2", "xy - 9x^3y", "(-3x + y - 5z)^2 - (4x - y - 5z)^2",
                      "x^4 + 3x^3 - 8x - 24", "2a^3b - a^2b^2 + b^2 - 2ab", "b^3 - a^3",
                      "x^3 + 8y^3 + 6x^2y + 12xy^2", "8a^4x^3 - 72b^2x^3 - a^4 + 9b^2", "x^3 + 9x - 27 - 3x^2",
                      "d^3 - 8 + 3(d^2 - 4d + 4)", "x^4y^3 + 3x^3y^2 + 3x^2y + x", "x^3y + 7x^2y + 6xy",
                      "16a^4 + 2ab^3", "8c^3 + 6c + 12c^2 + 1", "(y^2 + b^2)^2 - 4b^2y^2"],
    "Amaudruz p.9-12": ["12x^4 - 8x^2 + 16x", "9xy^2 + 18x^2y^4 - 36x^4y^2", "(a + b)^2 - 7(a + b)",
                        "9x^2 + 6x + 1", "4x^2 - 12xy + 9y^2", "81y^2 - 4z^2", "u^3 - 12u^2 + 48u - 64",
                        "8x^3 + 27", "x^2 + 5x - 14", "x^2 + 11x + 30", "2x^2 - x - 1", "9x^2 - 6x + 1",
                        "2x^2 + x + 3", "x^4 - 29x^2 + 100", "27x^6 + 215x^3 - 8", "a^2 + 2ab - c^2 + b^2",
                        "x + y + xy + y^2", "3z^3 + 2z^2 - 12z - 8", "x - x^3"],
    "Javet 2.2": ["2x^2 - 32", "9(x - 3)^2 - 4", "9x^2 + 24x + 16", "x^3 - 4x^2 + 4x", "6x^2 - 6",
                  "48z^2 - 216z + 243", "x^2 - 5", "4(x - 2)^2 - 1", "(x + 1)^2 - 16", "2x^2 + 20x + 42",
                  "-y^2 + 10y - 9", "17x^2 + 288x - 17", "16 - (3x + 2)^2", "x^2 + 6x + 7", "4x^2 - 12x - 11",
                  "x^2 + 5x + 2", "2x^2 - 4x - 4", "3t^2 + 5t + 12", "x^2 - 12", "x^2 - 6x + 7",
                  "2x^2 + 6x + 3", "x^2 + x + 1/4", "3x^2 - 27x", "2x^2 + 198x - 200", "-2x^2 + 9x - 4",
                  "3x^5 - 15x^3 + 12x", "x^3 + x^2 - 2x", "x^3 - 3x^2 - x + 3"],
    "Signalés / régression": ["p^2 - (px)^2", "px + p^2", "(uv)^2 - u", "p^2 - x^2", "4p^2 - 12pq + 9q^2",
                              "x^3 - 8y^3", "2x^3 + 16y^3", "3x^2 - 6x - 7", "x^2 + 4x + 2", "x^2 + 4",
                              "1 - x^2", "-x^2 + 2x - 1", "p^3 - (px)^3", "x^3 - 9x^2 + 23x - 15",
                              "x^2 + 5xy + 6y^2", "(p - x)^2", "(x + 1)(x - 1)", "2(x - y)^2", "(x^2 - 1)(x + 2)",
                              "x + y", "6x^2y", "5", "x^4 + 1", "x^3 - 2", "a^2 - b^2 + c^2", "x^2 + y^2"],
    "Fractions": ["t^2 + t + 1/4", "x^2/2 + x - 3/2", "x^2/4 - 1", "2x/3 + 4/3", "x^3/2 - x/2",
                  "x^2/2 + x - 1", "x^2/3 + x + 1", "0,5x^2 - 2", "y^2/9 - x^2/4", "x^3/8 - 1"],
    "Compléter le carré": ["z^4 - 3z^2 + 9", "x^4 + 4", "4x^4 + 1", "a^4 + a^2b^2 + b^4", "x^4 + x^2 + 1",
                           "x^4 + 64", "x^8 + 4"],
    "Sans méthode du cours (T21)": ["8x^3-12x^2-2x+3", "x^3-2", "30x^3-19x^2+1", "x^2+y^2"],
    "Écritures variées": ["-(x-1)^2", "x(x+1) + (x+1)", "x(a-b) + (b-a)", "(x+1)^2 - (x+1)", "2^3x - 8",
                          "x^2 - 4 = 0", "3(x+2)", "(2x+4)(x-1)", "-x - y", "(x^2 - 1)^2", "(x+1)^2-(x-1)^2",
                          "(x+3)^2-(x-1)^2", "(a+b)^2-(a-b)^2",
                          "x^2-1'000", "sqrt(x)", "x/y"],
}


def entrees_factorisation():
    vues, out = set(), []
    for liste in [entrees_page("factorisation")] + list(FACTORISATION.values()):
        for e in liste:
            if e not in vues:
                vues.add(e)
                out.append(e)
    return out
