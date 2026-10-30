def bh(haut, dhaut, bas, dbas):
    """Tableau BH du corrigé : « haut : f ⟶ dérivée : f′ » / « bas : g ⟶ dérivée : g′ » (tex)."""
    return {"type": "bh", "haut": haut, "dhaut": dhaut, "bas": bas, "dbas": dbas}


def encadre(genre, titre, lignes):
    """Encadré du corrigé (genre : prediction, attention, piege, autre) ; `lignes` : html (formules entre \\( \\))."""
    return {"type": "encadre", "genre": genre, "titre": titre, "lignes": list(lignes)}


def resultat_lim(tex):
    """Résultat d'une limite, encadré vert (« lim … = … »)."""
    return {"type": "resultat_lim", "tex": tex}


def valeurs(expr, xs, fs):
    """Tableau de valeurs (8.14) : ligne des x et ligne des valeurs de l'expression (tex)."""
    return {"type": "valeurs", "expr": expr, "xs": list(xs), "fs": list(fs)}


def sous_calcul(titre, etapes):
    """Sous-limite calculée à part (« On calcule à part … ») : étapes = [{titre, blocs}]."""
    return {"type": "sous_calcul", "titre": titre, "etapes": list(etapes)}
