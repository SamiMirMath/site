"""Corpus des tests de la rédaction du 2e degré (chantier equations-2e-degre, P2b ; decisions.md §§ 6, 7, 8 et 13).

- `P2B` : les équations que P2b résout, sous la forme « P = 0 » développée et ordonnée : le § 8 (2.9 à 2.12, Javet 2.17, Az 4.1),
  chaque exercice qui demande de ramener ou de développer pris sous sa forme développée (« (dév.) »), les cas limites du § 6, les
  exemples rédigés du § 7 et les précisions du § 13.4.
- `A_VENIR` : les formes que P2b ne traite pas encore, avec la partie qui les traitera (P3 : ramener, développer ; P4a : formes
  structurées ; P4b : degrés ≠ 2, identité, bicarrée), leurs coefficients développés (ordre décroissant, pour l'oracle) et le S
  attendu quand l'oracle ne s'applique pas (S = ℝ). Leurs tests sont des xfail stricts.

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

MESSAGE_BICARREE = ("Cette équation se ramène au 2e degré par un changement de variable : ce sera traité dans une prochaine "
                    "version.")
