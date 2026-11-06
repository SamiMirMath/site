"""
chaine.py — Brique commune « chaînes du corrigé » : équations, relations, « ou », textes, chaînes d'équivalences (⇔) ou d'égalités (=)
avec la propriété qui justifie chaque lien, phrases du corrigé, et leur écriture (TeX d'une ligne, rangées alignées pour la page).

Tirée de l'outil Exponentielles et logarithmes (chantier briques-communes, B2 ; revue de structure, R5), qui la réexporte sous les
mêmes noms (`exp_log.Chaine is chaine.Chaine`, etc.) : la sortie de l'outil est identique à l'octet. Elle s'appuie sur l'arbre de
moteur/expr.py (`tex`). Python pur.

Éléments d'une chaîne : un arbre (moteur/expr.py), `Eq` (g = d), `Rel` (g < d…), `Ou` (x = a ou x = b), `Texte` (TeX déjà écrit), ou
un élément propre à un outil, sous-classe d'`Element`, qui s'écrit lui-même (`ecrire_tex`). Propriété d'un lien : un texte (str), ou
une justification propre à un outil, sous-classe de `Justification`, qui s'écrit elle-même (`ecrire_tex`, `ecrire_rangee`). La brique ne
connaît aucun élément ni aucune propriété d'un outil, sauf les trois propriétés génériques (`PROP_AUTRE_COTE`, `PROP_PRODUIT_NUL`,
`PROP_MISE_EN_EVIDENCE`) ; les autres (`PROP_*` d'Exp-log) restent dans l'outil.

Quatre options de présentation, tirées des corrigés du 2e degré (docs/chantiers/equations-2e-degre/decisions.md, D5, D7, E5, E8,
§ 13.3), désactivées par défaut (la sortie d'Exp-log ne change pas) :
- `etiquette_grise=True` (`tex_chaine`, `rangees_chaine`) : la propriété est une étiquette grise, sans parenthèses (« ME ») ;
- `impossible=True` (`tex_element`, `tex_chaine`, `rangees_chaine`) : dans un « ou », une égalité entre deux nombres différents (le
  facteur constant du produit nul, 6 = 0) porte la mention « impossible » dessous ;
- une ligne de texte au milieu d'une chaîne (`Chaine(…, textes=…)`, `Chaine.ajouter(…, texte_avant=…)`) : une ligne pleine largeur
  entre deux éléments, sans casser l'alignement des ⇔ (`LigneTexte` dans les rangées) ;
- `coupure_ou=True` (`tex_element`, `rangees_chaine`, `bloc_chaine`) : dans un « ou », la ligne ne se coupe qu'après un « ou » (produit
  nul à trois facteurs sur un écran étroit) ; chaque équation reste entière.

Pour la page : `bloc_chaine(c)` donne le bloc « chaine » de moteur/sortie.py (B3 : rangées alignées, lignes pleine largeur, et le membre de
gauche dans sa colonne avec `membre_gauche=True`), que commun/rendu.js affiche ; `bloc_rangees(rangees)` fait de même pour des rangées
déjà écrites (celles de plusieurs chaînes mises bout à bout, par exemple les étapes d'une résolution du 2e degré) ; Exp-log écrit encore
sa grille lui-même (resoudre_el.py, exception nommée de docs/architecture.md, § 5).

Aucun état : aucune variable de module n'est modifiée, les tables sont en lecture seule (règle A7 de docs/architecture.md).
"""
from collections import namedtuple
from html import escape as _echapper
from types import MappingProxyType

import sortie
from expr import Nb, Neg, tex

__all__ = ["Eq", "Rel", "Ou", "Texte", "Element", "Justification", "Chaine", "Message", "LigneTexte", "tex_element", "tex_message",
           "LIENS_TEX", "tex_chaine", "rangees_chaine", "est_impossible", "texte_message", "bloc_chaine", "bloc_rangees",
           "PROP_AUTRE_COTE", "PROP_PRODUIT_NUL", "PROP_MISE_EN_EVIDENCE"]


# =====================================================================
# 1. ÉLÉMENTS D'UNE CHAÎNE
# =====================================================================
class Eq:
    """Une équation g = d (arbres)."""
    __slots__ = ("g", "d", "milieu")

    def __init__(self, g, d, milieu=()):
        """`milieu` : écritures intermédiaires de d, affichées entre g et d (x = 10³ = 1000) ; d est la dernière."""
        self.g, self.d, self.milieu = g, d, list(milieu)

    def __eq__(self, o):
        return isinstance(o, Eq) and (self.g, self.d) == (o.g, o.d)

    def __hash__(self):
        return hash((self.g, self.d))

    def __repr__(self):
        return f"Eq({self.g!r}, {self.d!r})"


class Rel:
    """Une relation d'ordre g < d, g ≤ d, g > d (arbres), par exemple 5^(8x) > 0."""
    SIGNES = MappingProxyType({"<": " < ", ">": " > ", "≤": r" \le ", "≥": r" \ge "})
    __slots__ = ("g", "signe", "d")

    def __init__(self, g, signe, d):
        self.g, self.signe, self.d = g, signe, d


class Texte:
    """Une condition déjà écrite en TeX (x > 0 et x ≠ 1) ; `detail` : un complément en TeX qui s'affiche entre parenthèses, à droite de la
    ligne dans la page (l'encadrement 2⁵ = 32 < 50 < 64 = 2⁶)."""
    __slots__ = ("tex", "detail")

    def __init__(self, tex, detail=None):
        self.tex, self.detail = tex, detail


class Ou:
    """x = a ou x = b : plusieurs équations dont une au moins est vraie."""
    __slots__ = ("eqs",)

    def __init__(self, eqs):
        self.eqs = list(eqs)


class Element:
    """Un élément de chaîne propre à un outil (Exp-log : « u = valeur > 0 », `Positif`) : il s'écrit lui-même. Il n'est le membre de
    gauche d'aucun lien « = » (pas d'alignement sous lui)."""
    __slots__ = ()

    def ecrire_tex(self):
        """TeX de l'élément (appelé par `tex_element`)."""
        raise TypeError(self)


class Justification:
    """Une propriété de lien propre à un outil (Exp-log : « car D ≠ 0 », « on divise les deux membres par Q ») : elle s'écrit elle-même,
    parenthèses comprises, en TeX à la suite de la ligne (`ecrire_tex`, après `\\quad`) et dans la colonne de droite des rangées
    (`ecrire_rangee`, le TeX entre `\\(` et `\\)`). L'option `etiquette_grise` ne la change pas."""
    __slots__ = ()

    def ecrire_tex(self):
        raise TypeError(self)

    def ecrire_rangee(self):
        raise TypeError(self)


# =====================================================================
# 2. CHAÎNE ET PHRASE DU CORRIGÉ
# =====================================================================
class Chaine:
    """Une ligne du corrigé : éléments (arbres, Eq ou Ou) reliés par « = » (expressions) ou « ⇔ » (équations), chaque lien avec
    sa propriété (texte) ou None quand le calcul est évident.

    `note` : un texte qui suit la ligne (« aucune solution ») ; `coche` : la note est suivie de ✓ (Exp-log : « le logarithme est bien
    défini ✓ »). `textes` : {i: [contenu, …]}, des lignes pleine largeur écrites avant l'élément i (1 ≤ i < nombre d'éléments), au
    milieu de la chaîne ; le lien de l'élément i le relie toujours à l'élément i − 1. Un contenu est un `Message`, un texte, ou un
    objet que la page sait afficher (un bloc) : la brique le passe tel quel aux rangées (`LigneTexte`)."""

    def __init__(self, elements, liens=(), props=(), note=None, coche=False, textes=None):
        self.elements, self.liens, self.props, self.note = list(elements), list(liens), list(props), note
        self.coche = coche
        self.textes = {i: list(contenus) for i, contenus in (textes or {}).items()}
        assert len(self.liens) == len(self.props) == len(self.elements) - 1
        assert all(1 <= i < len(self.elements) and contenus for i, contenus in self.textes.items()), self.textes

    def ajouter(self, element, lien, prop=None, texte_avant=None):
        """Ajoute `element`, relié au précédent par `lien` et justifié par `prop` ; `texte_avant` : une ligne pleine largeur (ou une
        liste de lignes) écrite avant lui, au milieu de la chaîne."""
        if texte_avant is not None:
            contenus = texte_avant if isinstance(texte_avant, list) else [texte_avant]
            self.textes.setdefault(len(self.elements), []).extend(contenus)
        self.elements.append(element)
        self.liens.append(lien)
        self.props.append(prop)
        return self


class Message:
    """Une phrase du corrigé qui n'est pas une chaîne d'équations (« 20 n'est pas une puissance de 3 : il faut les logarithmes. ») :
    du texte (str) et des arbres, écrits en TeX dans la page."""
    __slots__ = ("morceaux",)

    def __init__(self, *morceaux):
        self.morceaux = morceaux

    def texte(self):
        return "".join(m if isinstance(m, str) else m.tex if isinstance(m, Texte) else tex(m) for m in self.morceaux)

    def html(self):
        return "".join(_echapper(m, quote=False) if isinstance(m, str)
                       else r"\(" + _echapper(m.tex if isinstance(m, Texte) else tex(m), quote=False) + r"\)" for m in self.morceaux)


LigneTexte = namedtuple("LigneTexte", "contenu")
LigneTexte.__doc__ = """Une rangée pleine largeur au milieu d'une chaîne (option « texte au milieu ») : `contenu` tel que l'outil l'a donné
(`Message`, texte, ou un bloc). Elle n'a ni lien ni propriété : une page qui lit les rangées comme des triplets échoue au lieu de la
mal afficher."""


# =====================================================================
# 3. ÉCRITURE : TEX D'UN ÉLÉMENT, D'UNE LIGNE, RANGÉES ALIGNÉES
# =====================================================================
def _constante(n):
    """La valeur d'un nombre écrit (6, −1), ou None."""
    if isinstance(n, Nb):
        return n.val
    if isinstance(n, Neg) and isinstance(n.a, Nb):
        return -n.a.val
    return None


def est_impossible(e):
    """Vrai pour une égalité entre deux nombres différents (6 = 0, −1 = 0) : le facteur constant d'un produit nul. Rien d'autre."""
    if not isinstance(e, Eq) or e.milieu:
        return False
    g, d = _constante(e.g), _constante(e.d)
    return g is not None and d is not None and g != d


def tex_element(e, impossible=False, coupure_ou=False):
    """TeX d'un élément. `impossible` : dans un « ou », une égalité entre deux nombres différents s'écrit avec « impossible » dessous,
    comme dans le corrigé (`\\underbrace{6 = 0}_{\\text{impossible}}`). `coupure_ou` : dans un « ou », chaque équation est un groupe
    `{…}` (KaTeX ne coupe pas une ligne à l'intérieur) et `\\allowbreak` suit chaque « ou » : sur un écran étroit, la ligne ne se coupe
    qu'après un « ou »."""
    if isinstance(e, Eq):
        return tex(e.g) + "".join(" = " + tex(m) for m in e.milieu) + " = " + tex(e.d)
    if isinstance(e, Element):
        return e.ecrire_tex()
    if isinstance(e, Texte):
        return e.tex + (r" \quad (" + e.detail + ")" if e.detail else "")
    if isinstance(e, Ou):
        membres = [r"\underbrace{" + tex_element(q) + r"}_{\text{impossible}}" if impossible and est_impossible(q)
                   else tex_element(q) for q in e.eqs]
        if coupure_ou:
            return r" \text{ ou } \allowbreak ".join("{" + m + "}" for m in membres)
        return r" \text{ ou } ".join(membres)
    if isinstance(e, Rel):
        return tex(e.g) + Rel.SIGNES[e.signe] + tex(e.d)
    return tex(e)


def tex_message(m):
    """TeX d'une ligne de texte au milieu d'une chaîne : un `Message` (texte dans `\\text{…}`, arbres en TeX) ou un texte."""
    if isinstance(m, str):
        return r"\text{" + m + "}"
    if isinstance(m, Message):
        return "".join(r"\text{" + x + "}" if isinstance(x, str) else x.tex if isinstance(x, Texte) else tex(x) for x in m.morceaux)
    raise TypeError(m)


LIENS_TEX = MappingProxyType({"⇔": r" \iff ", "⇒": r" \Rightarrow ", "≈": r" \approx "})      # « = » pour tout autre lien


def _etiquette_tex(texte, grise):
    return r" \quad \textcolor{gray}{\text{" + texte + "}}" if grise else r" \quad \text{(" + texte + ")}"


def tex_chaine(c, etiquette_grise=False, impossible=False):
    """TeX d'une ligne : la propriété de chaque lien suit l'élément qu'elle justifie, entre parenthèses (`etiquette_grise` : en gris,
    sans parenthèses). Une ligne de texte au milieu de la chaîne s'écrit entre deux `\\quad`, avant le lien."""
    s = tex_element(c.elements[0], impossible)
    for i, (e, lien, prop) in enumerate(zip(c.elements[1:], c.liens, c.props), 1):
        for m in c.textes.get(i, ()):
            s += r" \quad " + tex_message(m) + r" \quad"
        s += LIENS_TEX.get(lien, " = ") + tex_element(e, impossible)
        if isinstance(prop, Justification):
            s += r" \quad " + prop.ecrire_tex()
        elif prop:
            s += _etiquette_tex(prop, etiquette_grise)
    if c.note:
        s += _etiquette_tex(c.note, etiquette_grise) + (r" \; \checkmark" if c.coche else "")
    return s


def _gauche(e):
    """TeX du membre de gauche auquel un lien « = » se rattache : x dans `x = N/D`, l'expression elle-même dans une chaîne de « = »."""
    if isinstance(e, Eq):
        return tex(e.g)
    if isinstance(e, (Element, Texte, Ou, Rel)):
        return None
    return tex(e)


def rangees_chaine(c, etiquette_grise=False, impossible=False, coupure_ou=False):
    """La chaîne en lignes alignées, une étape par ligne comme le corrigé : [(lien, expression, propriété)], les trois en TeX/texte.
    `lien` : « \\iff » ou vide ; `expression` : un élément après un « ⇔ » ; les liens « = » prolongent la ligne (`√2 = 2^(1/2) = 4^(1/4)`)
    jusqu'à une propriété, après laquelle la suite commence une nouvelle ligne `{} = suite`, alignée sous le « = » précédent ;
    `propriété` : le texte entre parenthèses (le TeX y est entre `\\(` et `\\)`), ou None. La page met le lien dans une première colonne,
    l'expression dans la deuxième et la propriété à droite (sous l'expression sur un écran étroit).

    Options : `etiquette_grise` (la propriété et la note sans parenthèses, séparées par « ; » ; le gris est celui de la colonne dans
    la page), `impossible` et `coupure_ou` (voir `tex_element`). Une ligne de texte au milieu de la chaîne est une rangée
    `LigneTexte(contenu)`, avant la rangée de l'élément qu'elle précède ; un lien « = » qui la suit commence une nouvelle ligne."""
    premier = c.elements[0]
    rangees = [["", premier.tex if isinstance(premier, Texte) else tex_element(premier, impossible, coupure_ou),
                r"(\(" + premier.detail + r"\))" if isinstance(premier, Texte) and premier.detail else None]]
    ancre = _gauche(premier)
    for i, (e, lien, prop) in enumerate(zip(c.elements[1:], c.liens, c.props), 1):
        rangees.extend(LigneTexte(m) for m in c.textes.get(i, ()))
        if lien in ("⇔", "⇒"):                                        # ⇒ : l'implication, quand la ligne ne se lit pas dans l'autre sens
            rangees.append([LIENS_TEX[lien].strip(), tex_element(e, impossible, coupure_ou), None])
            ancre = _gauche(e)
        elif not isinstance(rangees[-1], LigneTexte) and rangees[-1][2] is None:   # pas de propriété : la suite d'égalités continue
            rangees[-1][1] += LIENS_TEX.get(lien, " = ") + tex_element(e, impossible, coupure_ou)
        else:                                                         # nouvelle ligne, son « = » sous celui de la ligne d'au-dessus
            cale = r"\phantom{" + ancre + "}" if ancre and len(ancre) <= 30 else ""
            rangees.append(["", cale + LIENS_TEX.get(lien, " = ") + tex_element(e, impossible, coupure_ou), None])
        if isinstance(prop, Justification):
            rangees[-1][2] = prop.ecrire_rangee()
        elif prop:
            rangees[-1][2] = prop if etiquette_grise else "(" + prop + ")"
    if c.note:
        if etiquette_grise:
            note = c.note + (r" \(\checkmark\)" if c.coche else "")
            rangees[-1][2] = note if rangees[-1][2] is None else rangees[-1][2] + " ; " + note
        else:
            note = "(" + c.note + ")" + (r" \(\checkmark\)" if c.coche else "")
            rangees[-1][2] = note if rangees[-1][2] is None else rangees[-1][2] + " " + note
    return [r if isinstance(r, LigneTexte) else tuple(r) for r in rangees]


def texte_message(m):
    """Texte d'une ligne pleine largeur du bloc « chaine » : un `Message` (texte tel quel, arbres en TeX entre \\( et \\)) ou un texte.
    Jamais de HTML : le rendu de la page échappe le texte."""
    if isinstance(m, str):
        return m
    if isinstance(m, Message):
        return "".join(x if isinstance(x, str) else r"\(" + (x.tex if isinstance(x, Texte) else tex(x)) + r"\)" for x in m.morceaux)
    raise TypeError(m)


def bloc_chaine(c, etiquette_grise=False, impossible=False, membre_gauche=False, coupure_ou=False):
    """Le bloc « chaine » de moteur/sortie.py (A4), tiré des rangées de `rangees_chaine` (mêmes options `etiquette_grise`, `impossible`
    et `coupure_ou`) : `bloc_rangees(rangees_chaine(c, …), membre_gauche)`.

    `membre_gauche` : comme le corrigé (« 6x² − 6 = 0 ⇔ 6(x² − 1) = 0 », les ⇔ suivants dessous), le premier élément passe dans la
    colonne de gauche de la première ligne à ⇔ (ou ⇒) ; les lignes pleine largeur écrites avant elle restent au-dessus. Seulement si la
    première rangée n'a pas de propriété et si la ligne suivante commence par un lien ; sinon la chaîne reste telle quelle."""
    return bloc_rangees(rangees_chaine(c, etiquette_grise, impossible, coupure_ou), membre_gauche)


def bloc_rangees(rangees, membre_gauche=False):
    """Le bloc « chaine » de moteur/sortie.py (A4) tiré de rangées déjà écrites (celles de `rangees_chaine`, d'une ou de plusieurs
    chaînes mises bout à bout) : une ligne {lien, expr, prop} par rangée (lien, expression, propriété), une ligne pleine largeur par
    `LigneTexte` (un texte ou un `Message` : `rangee_texte` ; un bloc, dict de moteur/sortie.py : `rangee_bloc`).

    `membre_gauche` : la première rangée-ligne (des lignes pleine largeur peuvent la précéder : phrase de choix et tableau d'abord)
    passe dans la colonne de gauche de la ligne suivante, comme le corrigé (« A ⇔ B »), si elle n'a ni lien ni propriété et si la ligne
    suivante commence par un lien ; les lignes pleine largeur écrites entre elles restent au-dessus. Sinon les rangées restent telles
    quelles."""
    rangees = list(rangees)
    lignes = [i for i, r in enumerate(rangees) if not isinstance(r, LigneTexte)]
    gauche = None
    if membre_gauche and len(lignes) > 1:
        premiere, suivante = rangees[lignes[0]], rangees[lignes[1]]
        if not premiere[0] and premiere[2] is None and suivante[0]:
            gauche = premiere[1]
            del rangees[lignes[0]]
    lignes_du_bloc = []
    for r in rangees:
        if isinstance(r, LigneTexte):
            m = r.contenu
            lignes_du_bloc.append(sortie.rangee_bloc(m) if isinstance(m, dict) else sortie.rangee_texte(texte_message(m)))
        else:
            lignes_du_bloc.append(sortie.rangee(*r, gauche=gauche))
            gauche = None
    return sortie.chaine(lignes_du_bloc)


# =====================================================================
# 4. PROPRIÉTÉS GÉNÉRIQUES (les autres sont propres à chaque outil)
# =====================================================================
PROP_AUTRE_COTE = "on passe un terme de l'autre côté"
PROP_PRODUIT_NUL = "un produit est nul si l'un des facteurs est nul"
PROP_MISE_EN_EVIDENCE = "mise en évidence"
