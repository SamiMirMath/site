"""Corpus des tests de la rédaction du 2e degré (chantier equations-2e-degre, P2b à P4b ; decisions.md §§ 6, 7, 8 et 13).

- `P2B` : les équations que P2b résout, sous la forme « P = 0 » développée et ordonnée : le § 8 (2.9 à 2.12, Javet 2.17, Az 4.1),
  chaque exercice qui demande de ramener ou de développer pris sous sa forme développée (« (dév.) »), les cas limites du § 6, les
  exemples rédigés du § 7 et les précisions du § 13.4.
- `P3` : les équations que P3 ramène à « P = 0 » (E1) ou développe d'abord (E2), de degré 2 : les exercices du § 8 sous leur forme
  d'énoncé (dont 2.11 h, l'exemple cible) et d'autres formes (côté droit, réduction, décimaux, fractions, « − » devant un produit…).
- `P4A` : les formes structurées que P4a résout sans développer (E1.3) : produit déjà nul (E13, Az 4.1 d), facteur commun aux deux
  membres (E3, 2.12 e), Id. rem. sur la forme structurée (E5 : 2.9 k, 2.9 l, 2.12 h), et d'autres formes de chacune.
- `P4B` : les degrés ≠ 2 (E13) : ME de xᵏ en degré ≥ 3 (2.12 c, Az 4.1 f), Id. rem. de A = x² (x⁴ − 16, D28 et E9), degré 1
  (isoler, D20), identité et égalité fausse (Az 4.1 g, phrases d'Exp-log), et les formes structurées laissées à P4b (facteur de degré 2
  dans un produit déjà nul, degré 1 une fois factorisée, identité).
- `RESOLUES` : `P2B`, `P3`, `P4A` et `P4B`.
- `NON_RESOLUES` : ce qui reçoit un message définitif (§ 4, § 13.5) : bicarrée (« pas_encore »), hors du cours (degré ≥ 3 que le
  cours ne résout pas, seulement quand c'est vrai : `second_degre.hors_du_cours`), forme non traitée par l'outil (les formes que
  l'outil n'écrit pas et les degrés ≥ 3 douteux : P5, question 29 de suivi.md) ; avec le statut attendu.
- `STRUCTURES_NON_ECRITES` : des formes où une structure s'applique (`forme_structuree`) mais que l'outil n'écrit pas : « forme non
  traitée par l'outil » (P5), sans développer (suivi.md, questions de P4a, P4b et 29).
- `SECTION_8` : les noms des exercices du § 8 (chacun a un instantané et le contrôle de l'oracle).
- `A_VENIR` : les formes que P2b ne traitait pas, avec la partie qui les traite (P3 : ramener, développer ; P4a : formes
  structurées ; P4b : degrés ≠ 2, identité, bicarrée), leurs coefficients développés (ordre décroissant, pour l'oracle) et le S
  attendu quand l'oracle ne s'applique pas (S = ℝ). Toutes les parties sont faites (`PARTIES_FAITES`) : aucun xfail.

Les saisies sont lues par `expr.lire_membres` (lexique commun) ; les décimaux de l'énoncé sont ceux de la saisie."""

P2B = {
    "2.9 a": "6x^2-6=0",
    "2.9 b": "t^2+20t+100=0",
    "2.9 c": "48z^2-216z+243=0",
    "2.9 d (dév.)": "4x^2-9=0",
    "2.9 e": "8x^2-112x+392=0",
    "2.9 f (dév.)": "196z^2+280z+100=0",
    "2.9 g": "t^2+t+1/4=0",
    "2.9 h": "9x^2-1/9=0",
    "2.9 i": "18z^2+72z+72=0",
    "2.9 j": "x^2-5=0",
    "2.9 k (dév.)": "4x^2-16x+15=0",
    "2.9 l (dév.)": "x^2+2x-15=0",
    "2.10 a": "x^2-5x-36=0",
    "2.10 b": "x^2+3x-18=0",
    "2.10 c": "2z^2+24z+64=0",
    "2.10 d": "x^2+7x+6=0",
    "2.10 e": "-y^2+10y-9=0",
    "2.10 f": "t^2+11t+30=0",
    "2.10 g": "x^2-11x+10=0",
    "2.10 h (dév.)": "x^2+7x-18=0",
    "2.10 i": "x^2+18x+45=0",
    "2.10 j (dév.)": "x^2-4x-32=0",
    "2.11 a": "2x^2+13x+15=0",
    "2.11 b": "9x^2+8x-1=0",
    "2.11 c": "5y^2-54y-72=0",
    "2.11 d": "2x^2-x-28=0",
    "2.11 e": "3x^2+2x-1=0",
    "2.11 f (dév.)": "4t^2+7t-2=0",
    "2.11 g": "17x^2+288x-17=0",
    "2.11 h (dév.)": "4x^2+2x-56=0",
    "2.11 i": "3x^2-8x-35=0",
    "2.11 j (dév.)": "12u^2-45u-12=0",
    "2.12 a": "x^2-8x+12=0",
    "2.12 b": "6x^2+5x+1=0",
    "2.12 d": "6x^2+16x-6=0",
    "2.12 e (dév.)": "-2x^2+x+1=0",
    "2.12 f": "t^2+8t-48=0",
    "2.12 g (dév.)": "x^2-16=0",
    "2.12 h (dév.)": "-9x^2-12x+12=0",
    "Javet 2.17 a": "x^2+5x+2=0",
    "Javet 2.17 b": "x^2+4x+2=0",
    "Javet 2.17 c": "2x^2-4x-4=0",
    "Javet 2.17 d": "3t^2+5t+12=0",
    "Javet 2.17 e": "(3/2)x^2-4x-1=0",
    "Javet 2.17 f": "(5/4)s^2+3s+1=0",
    "Az 4.1 c": "x^2+7x+12=0",
    "Az 4.1 e": "3x^2+4=0",
    "(x + 1)(x + 3) = 15 (dév.)": "x^2+4x-12=0",
    # cas limites du § 6
    "§ 6 x² + 1000x − 1": "x^2+1000x-1=0",
    "§ 6 −6x² + 12x − 6": "-6x^2+12x-6=0",
    "§ 6 0,5x² − 2": "0,5x^2-2=0",
    "§ 6 x² + 4": "x^2+4=0",
    # exemples rédigés du § 7
    "§ 7 3x² − 12x": "3x^2-12x=0",
    "§ 7 12x² − 12x + 3": "12x^2-12x+3=0",
    "§ 7 25x² − 3": "25x^2-3=0",
    "§ 7 x² − x − 42": "x^2-x-42=0",
    "§ 7 3x² + 10x − 8": "3x^2+10x-8=0",
    "§ 7 x² + 4x − 1": "x^2+4x-1=0",
    "§ 7 4x² − 12x + 9": "4x^2-12x+9=0",
    "§ 7 2x² + x + 3": "2x^2+x+3=0",
    # § 13.4 et § 13.5
    "§ 13.4 3x²": "3x^2=0",
    "§ 13.4 x² − 8": "x^2-8=0",
    "§ 13.4 x² − 1/2": "x^2-1/2=0",
    "§ 13.5 S-P de plus de 12 lignes": "x^2+55453x+720720=0",
    # décimaux de l'énoncé (E14), a < 0, Δ = 0 sur le chemin du cours
    "décimaux, résultats décimaux": "0,2x^2-0,5x-0,3=0",
    "décimaux, Id. rem.": "0,25x^2-1=0",
    "décimaux, formule": "1,5x^2-6=0",
    "décimaux, a < 0": "-0,5x^2+x+1=0",
    "a < 0, ME de −x": "-x^2+5x=0",
    "a < 0, ME de −3": "-3x^2+3x+18=0",
    "Δ = 0, coefficients non entiers": "(1/2)x^2+x+1/2=0",
    "x²": "x^2=0",
}

P3 = {
    # § 8, sous la forme de l'énoncé (E1)
    "2.9 d": "4x^2=9",
    "2.9 f": "196z^2+280z=-100",
    "2.10 h": "x^2+7x=18",
    "2.10 j": "4x+32=x^2",
    "2.11 f": "4t^2+7t=2",
    "2.11 h": "4x^2+2x=56",
    "2.11 j": "45u+12=12u^2",
    "2.12 g": "x^2=16",
    # E1 : réordonner, côté droit, réduction, second membre nul à gauche, décimaux, fractions
    "E1 termes dans le désordre": "5+x^2-6x=0",
    "E1 désordre, a < 0 gardé": "10y-y^2-9=0",
    "E1 côté droit, formule": "x^2-4x=2x^2+1",
    "E1 premier membre nul": "0=x^2-4",
    "E1 réduction": "x^2+x^2=8",
    "E1 décimaux": "0,5x^2=2",
    "E1 fractions, formule": "(3/2)x^2=4x+1",
    # E2 : développer (§ 7 et autres formes)
    "(x + 1)(x + 3) = 15": "(x+1)(x+3)=15",
    "E2 distribution": "2(x+3)=x^2",
    "E2 distribution, monôme": "x(x-4)=5",
    "E2 « − » devant un produit": "5-(x+1)(x+3)=0",
    "E2 « − » devant une distribution": "x^2-x(x+1)+3x^2=4",
    "E2 parenthèse précédée de « − »": "x^2-(2x+3)=0",
    "E2 Id. rem. (A + B)²": "(x+3)^2=2x+14",
    "E2 Id. rem. (A + B)², Δ < 0": "(x+1)^2=-16",
    "E2 Id. rem. (A − B)², A constante": "(3-x)^2=1+x",
    "E2 « − » devant une double distribution": "-(x+1)(x-2)=x",
    "E2 décimaux": "0,5(x+2)=x^2",
}

P4A = {
    # § 8 : Id. rem. sur la forme structurée (E5), facteur commun (E3), produit déjà nul (E13)
    "2.9 k": "4(x-2)^2=1",
    "2.9 l": "(x+1)^2=16",
    "2.12 e": "(x-1)(2-x)=(x-1)(x+3)",
    "2.12 h": "16-(3x+2)^2=0",
    "Az 4.1 d": "(x-1)(2-x)(5-3x)=0",
    # produit déjà nul : monôme, D24, constante « impossible », premier membre nul, décimaux, D20
    "E13 monôme facteur": "x(x+1)=0",
    "E13 monôme 2x": "2x(x-3)=0",
    "E13 carré, D24": "(t+10)^2=0",
    "E13 constante et carré": "3(x+1)^2=0",
    "E13 −1 impossible": "-(x-1)(x+2)=0",
    "E13 premier membre nul": "0=(x-3)(2x+1)",
    "E13 carré et facteur": "(x+1)^2*(x-2)=0",
    "E13 décimaux": "0,5(x-1)(x+2)=0",
    "E13 D20": "(2x-1/3)(x+1)=0",
    # Id. rem. sur la forme structurée
    "E5 B irrationnel": "(x+1)^2=5",
    "E5 car, B irrationnel": "4(x-2)^2=3",
    "E5 A constant, écrit après": "-(x+1)^2+4=0",
    "E5 deux carrés": "(x+1)^2=(2x-3)^2",
    "E5 deux carrés, car": "4(x+1)^2=9(x-2)^2",
    "E5 constantes regroupées": "(x+1)^2+3=19",
    "E5 déjà = 0": "(x+1)^2-16=0",
    "E5 fraction": "(1/4)(x+1)^2=1",
    "E5 décimaux": "0,25(x+1)^2=1",
    "E5 facteur monôme": "(x+1)^2=1",
    "E5 constante nulle, D24": "(x+1)^2+3=3",
    # facteur commun aux deux membres
    "E3 somme seule à droite": "(x-1)(x+2)=x-1",
    "E3 monôme et constante": "x(x-3)=2(x-3)",
    "E3 carré du facteur": "(x+2)^2=3(x+2)",
    "E3 « − » devant la droite": "(x-1)(x+2)=-(x-1)(x+3)",
    "E3 deux facteurs communs": "(x-1)(x+2)=3(x-1)(x+2)",
    "E3 facteur à droite d'abord": "3(x+1)=(x+1)(x-2)",
    "E3 facteur monôme": "(x+1)^2=x+1",
    "E3 solution répétée": "(x+1)^2=4(x+1)^2",
}

P4B = {
    # § 8 : degrés ≠ 2 (E13)
    "2.12 c": "x^3-x=0",
    "Az 4.1 f": "x^3+8x^2=0",
    "Az 4.1 g": "(2x-1)^2-4x(x-1)=1",
    # degré ≥ 3 : ME de xᵏ, puis la méthode suivante sur le facteur ; Id. rem. de A = x² (§ 13.4, D28, E9)
    "x⁴ − 16": "x^4-16=0",
    "x³ − 5x": "x^3-5x=0",
    "ME de −x en degré 3": "-x^3+x=0",
    "ME de x, puis S-P": "x^3-5x^2+6x=0",
    "ME de x, puis formule (E9)": "x^3-2x^2-2x=0",
    "ME de 2x, puis Id. rem. (carré)": "2x^3-4x^2+2x=0",
    "ME de x², puis tâtonnement": "2x^4+x^3-28x^2=0",
    "ME de x, puis deux Id. rem.": "x^5-16x=0",
    "Id. rem. de A = x², carré, Δ < 0": "x^4+2x^2+1=0",
    "Id. rem. de A = 2x², deux tâtonnements en échec": "4x^4-9=0",
    "Id. rem. de A = x², coefficients non entiers": "x^4-1/4=0",
    "degré 3 ramené": "x^3=4x",
    # degré 1 : ramener, puis isoler (D20)
    "degré 1": "2x+4=0",
    "degré 1, D20": "3x+1/3=0",
    "degré 1, décimaux, D20": "0,5x-1,5=0",
    "degré 1, côté droit": "x+1=3x-5",
    "degré 1, x² s'annule": "x^2+1=x^2+x",
    "degré 1, double distribution": "(x+1)(x+3)=x^2",
    "Az 4.1 a": "3x+9=2(x+4)+1",
    # identité et égalité fausse (phrases d'Exp-log, § 13.4)
    "identité": "x+1=x+1",
    "identité, double distribution": "(x+2)(x-2)=x^2-4",
    "égalité fausse": "x^2+1=x^2+2",
    "égalité fausse, réduction": "2x+3-2x=0",
    # formes structurées laissées à P4b : facteur de degré 2 dans un produit déjà nul, degré 1 une fois factorisée, identité
    "E13 facteur de degré 2, Id. rem.": "(x^2-1)(x+2)=0",
    "E13 constante et facteur de degré 2": "3(x^2-4)=0",
    "E13 facteur de degré 2, a < 0": "(4-x^2)(x+1)=0",
    "E13 facteur de degré 2, S-P en échec (E9)": "3(x^2+x-1)=0",
    "E13 facteur de degré 2, Δ < 0": "(x^2+1)(x-2)=0",
    "E13 premier membre nul, facteur de degré 2": "0=(x^2-4)x",
    "E5 deux carrés, degré 1": "(x+1)^2=(x-3)^2",
    "E3 facteur commun, degré 1": "(x-1)(x+2)=(x-1)(x+5)",
    "identité structurée, deux carrés": "(x+1)^2=(x+1)^2",
    "identité structurée, facteur commun": "(x-1)(x+2)=(x-1)(x+2)",
}

RESOLUES = {**P2B, **P3, **P4A, **P4B}

PARTIES_FAITES = ("P3", "P4a", "P4b")

MESSAGE_BICARREE = ("Cette équation se ramène au 2e degré par un changement de variable : ce sera traité dans une prochaine "
                    "version.")

# nom : (saisie, statut attendu) — des messages définitifs (§ 4, § 13.5), jamais un statut temporaire
NON_RESOLUES = {
    "bicarrée": ("x^4-5x^2+4=0", "pas_encore"),
    "bicarrée sans terme en x²": ("x^4+4=0", "pas_encore"),
    "bicarrée ramenée": ("x^4=5x^2-4", "pas_encore"),
    "bicarrée après une ME (§ 13.4 à la lettre)": ("2x^4-10x^2+8=0", "forme_non_traitee"),
    "degré 3 sans ME ni Id. rem.": ("x^3=x+1", "hors_cours"),
    "Az 4.1 d développé": ("-3x^3+14x^2-21x+10=0", "hors_cours"),
    "Id. rem., puis un facteur de degré 3": ("x^6-64=0", "forme_non_traitee"),
    "ME non entière en degré 3 (question 10)": ("0,5x^3-2x=0", "forme_non_traitee"),
    # ce que E2 ne développe pas (suivi.md, P3 et P4b)
    "E2 nombre et deux parenthèses": ("2(x+1)(x+3)=5", "forme_non_traitee"),
    "E2 k(B)² et des termes en x": ("0,5(x+2)^2=x+3", "forme_non_traitee"),
    "E2 cube": ("(x+1)^3=8+x", "forme_non_traitee"),
    "E2 monôme écrit à l'envers": ("x*3+x^2=1", "forme_non_traitee"),
    "E2 carré d'un trinôme": ("(x^2+x+1)^2=x", "forme_non_traitee"),
    "E2 division par un nombre": ("x^2/2=1+x", "forme_non_traitee"),
    "Az 4.1 b": ("(3x-2)/6=(x+1)/4+5", "forme_non_traitee"),
    "Az 4.1 h": ("x^2+1-(10-x^2)/8=(6x-3)/4", "forme_non_traitee"),
}

# saisie : ce qui manque (une structure s'applique, l'outil ne l'écrit pas : « forme_non_traitee », jamais développée)
STRUCTURES_NON_ECRITES = {
    "2(x-1)=3(1-x)(x+2)": "facteurs seulement proportionnels (x − 1, 1 − x)",
    "(x-1)(x+2)=2x-2": "facteur commun écrit développé à droite (2x − 2)",
    "2(x+1)^2=8": "√k irrationnel (A = √2(x + 1))",
    "-(x+1)^2+5=0": "A constant irrationnel (√5)",
    "(x+1)^3=0": "cube",
    "(x+1+2)(x-1)=0": "facteur non réduit",
    "(x^2-1)^2=0": "carré d'un facteur de degré 2 (D24 sur un produit déjà factorisé)",
    "(x+1)^2*(x^2-4)=0": "carré et facteur de degré 2 dans le même produit",
}

# les exercices du § 8 (noms du corpus)
SECTION_8 = (["2.9 " + c for c in "abcdefghijkl"] + ["2.10 " + c for c in "abcdefghij"] + ["2.11 " + c for c in "abcdefghij"]
             + ["2.12 " + c for c in "abcdefgh"] + ["Javet 2.17 " + c for c in "abcdef"] + ["Az 4.1 " + c for c in "cdefg"]
             + ["(x + 1)(x + 3) = 15"])

# nom : (saisie, partie, coefficients développés (ordre décroissant) ou None, S attendu en TeX ou None, ce qui manque)
A_VENIR = {
    "2.9 d": ("4x^2=9", "P3", [4, 0, -9], None, "ramener (E1)"),
    "2.9 f": ("196z^2+280z=-100", "P3", [196, 280, 100], None, "ramener (E1)"),
    "2.10 h": ("x^2+7x=18", "P3", [1, 7, -18], None, "ramener, avec la phrase (E1)"),
    "2.10 j": ("4x+32=x^2", "P3", [1, -4, -32], None, "ramener à droite (E1)"),
    "2.11 f": ("4t^2+7t=2", "P3", [4, 7, -2], None, "ramener, avec la phrase (E1)"),
    "2.11 h": ("4x^2+2x=56", "P3", [4, 2, -56], None, "ramener (E1)"),
    "2.11 j": ("45u+12=12u^2", "P3", [12, -45, -12], None, "ramener à droite (E1)"),
    "2.12 g": ("x^2=16", "P3", [1, 0, -16], None, "ramener (E1)"),
    "E1 termes dans le désordre": ("5+x^2-6x=0", "P3", [1, -6, 5], None, "réordonner (E1, quiz.md réponse 1)"),
    "(x + 1)(x + 3) = 15": ("(x+1)(x+3)=15", "P3", [1, 4, -12], None, "développer (E2, double distribution)"),
    "2.9 k": ("4(x-2)^2=1", "P4a", [4, -16, 15], None, "Id. rem. sur la forme structurée (E5)"),
    "2.9 l": ("(x+1)^2=16", "P4a", [1, 2, -15], None, "Id. rem. sur la forme structurée (E5)"),
    "2.12 e": ("(x-1)(2-x)=(x-1)(x+3)", "P4a", [-2, 1, 1], None, "facteur commun aux deux membres (E3)"),
    "2.12 h": ("16-(3x+2)^2=0", "P4a", [-9, -12, 12], None, "Id. rem. sur la forme structurée (E5)"),
    "Az 4.1 d": ("(x-1)(2-x)(5-3x)=0", "P4a", [3, -14, 21, -10], None, "produit déjà factorisé (E13)"),
    "2.12 c": ("x^3-x=0", "P4b", [1, 0, -1, 0], None, "ME de x en degré 3 (E13)"),
    "Az 4.1 f": ("x^3+8x^2=0", "P4b", [1, 8, 0, 0], None, "ME de x² en degré 3 (E13)"),
    "x⁴ − 16": ("x^4-16=0", "P4b", [1, 0, 0, 0, -16], None, "Id. rem. en degré 4, puis E9 (§ 13.4)"),
    "x³ − 5x": ("x^3-5x=0", "P4b", [1, 0, -5, 0], None, "ME de x, puis Id. rem. avec B = √5"),
    "degré 1": ("2x+4=0", "P4b", [2, 4], None, "isoler (D20, E13)"),
    "Az 4.1 g": ("(2x-1)^2-4x(x-1)=1", "P4b", None, r"S = \mathbb{R}", "développer puis identité (E13, § 13.4)"),
}
