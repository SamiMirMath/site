"""Fonctions aléatoires reproductibles (graine fixe) pour les tests de propriétés.

Les fonctions ressemblent aux exercices de 3e : polynômes à racines entières, ln, √, e^,
quotients, produits. Elles sont écrites comme un élève les saisirait."""
import random


def _coef(c, mono, premier):
    """Terme c·mono écrit pour la saisie : « +3x », « -x^2 », « 5 »."""
    if c == 0:
        return ""
    signe = "-" if c < 0 else ("" if premier else "+")
    a = abs(c)
    if mono and a == 1:
        return signe + mono
    return signe + str(a) + mono


def poly(coeffs):
    """coeffs ascendants entiers -> chaîne « x^2-3x+2 »."""
    out = ""
    for k in range(len(coeffs) - 1, -1, -1):
        mono = "" if k == 0 else ("x" if k == 1 else f"x^{k}")
        out += _coef(coeffs[k], mono, out == "")
    return out or "0"


def _mul(p, q):
    r = [0] * (len(p) + len(q) - 1)
    for i, a in enumerate(p):
        for j, b in enumerate(q):
            r[i + j] += a * b
    return r


class Generateur:
    def __init__(self, graine):
        self.r = random.Random(graine)

    def entier(self, a, b, nonnul=False):
        while True:
            v = self.r.randint(a, b)
            if v or not nonnul:
                return v

    def affine(self):
        return poly([self.entier(-6, 6), self.entier(-3, 3, nonnul=True)])

    def trinome_racines(self):
        p, q = self.entier(-5, 5), self.entier(-5, 5)
        a = self.r.choice([1, 1, 1, -1, 2])
        return poly(_mul([-p * a, a], [-q, 1]))

    def trinome(self):
        return poly([self.entier(-6, 6), self.entier(-5, 5), self.r.choice([1, 1, -1, 2])])

    def polynome(self):
        return self.r.choice([self.affine, self.trinome_racines, self.trinome_racines, self.trinome])()

    def bloc(self):
        """Une « brique » qui porte au plus une condition d'existence."""
        P = self.polynome()
        c = self.entier(-3, 3)
        choix = self.r.randrange(10)
        if choix == 0:
            return f"ln({P})"
        if choix == 1:
            return f"sqrt({P})"
        if choix == 2:
            return f"1/({P})"
        if choix == 3:
            return f"e^({self.affine()})"
        if choix == 4:
            return f"ln({P})+{c}" if c >= 0 else f"ln({P}){c}"
        if choix == 5:
            return f"({self.affine()})/({P})"
        if choix == 6:
            return f"1/(ln({self.affine()}){'+' if c >= 0 else ''}{c})"
        if choix == 7:
            return f"x*ln({self.affine()})"
        if choix == 8:
            return f"1/(e^x-{self.entier(1, 5)})"
        return f"({P})"

    def fonction(self):
        """Une ou deux briques combinées."""
        if self.r.random() < 0.45:
            return self.bloc()
        a, b = self.bloc(), self.bloc()
        op = self.r.choice(["+", "*", "/"])
        return f"({a}){op}({b})"


def fonctions(n, graine=2026):
    g = Generateur(graine)
    vues, out = set(), []
    while len(out) < n:
        f = g.fonction()
        if f not in vues:
            vues.add(f)
            out.append(f)
    return out
