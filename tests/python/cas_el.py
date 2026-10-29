"""T33 — Entrées de test de l'outil « Exponentielles et logarithmes » (batterie EL-01) : exercices du chapitre 2 du polycopié 3C
(2.13 à 2.27, exemples p. 22-23, 26, 28-29) et d'autres formes de chaque méthode, avec la solution attendue. Partagées par
test_exp_log.py (moteur, oracle mpmath), test_instantanes_resoudre.py (instantané de l'adaptateur) et test_json_strict.py."""
from fractions import Fraction as F

# (saisie, solutions exactes) : exercices 2.13 a-o du polycopié et exemples p. 22-23
BATTERIE_E1 = [
    ("7^(2x+1)=7^9", [F(4)]), ("3^x=27", [F(3)]), ("10^x=1/100", [F(-2)]), ("2*3^(x-1)=18", [F(3)]),
    ("4^(-x)=2^6", [F(-3)]), ("4^x=8", [F(3, 2)]), ("3^x=9^(2x+3)", [F(-2)]), ("10^(x+2)=(10^2)^x", [F(2)]),
    ("5^(3x+2)=(5^x)^2", [F(-2)]), ("11^(2x+1)=1", [F(-1, 2)]), ("2^(x+7)=4^(5x+2)", [F(1, 3)]),
    ("8^(3x+2)=1/16", [F(-10, 9)]), ("(25^x)^2=5^0*5^(x+3)", [F(1)]), ("2^x=2*4^(x-1)", [F(1)]),
    ("2^(x^2)*4^x=8", [F(-3), F(1)]),
    ("3^(x+1)-27=0", [F(2)]), ("10^(2x)=0,01", [F(-1)]), ("3*2^(x^2+1)=96", [F(-2), F(2)]), ("4^(3x+1)=8", [F(1, 6)]),
    # autres formes de la même méthode
    ("18=2*3^(x-1)", [F(3)]), ("3(2^x+1)=9", [F(1)]), ("-2^x=-8", [F(3)]), ("5-2^x=1", [F(2)]), ("2^x/4=2", [F(3)]),
    ("(1/2)^x=8", [F(-3)]), ("9^x=1/3", [F(-1, 2)]), ("2^(x/2)=8", [F(6)]), ("2^(-x)=8", [F(-3)]), ("4^x=16", [F(2)]),
    ("1,5^x=2,25", [F(2)]), ("2^(x^2)=8^x", [F(0), F(3)]), ("2^(x+1)=2*2^x", None), ("2^(x+1)=2^(x+3)", []),
    ("2^(x^2)=2^(x-5)", []), ("9^(x^2)=3^(x+1)", [F(-1, 2), F(1)]),
    # la base e : e^A = e^B ⇔ A = B (27.10.2026)
    ("e^x=e^3", [F(3)]), ("e^x=e^(x+1)", []), ("e^(2x)=e^5", [F(5, 2)]), ("e^(x^2)=e^(2x+3)", [F(-1), F(3)]),
]

SANS_E1 = ["3^x=20", "2^x=0", "2^x=-4", "5^(8x)=-25", "e^x=7", "2^x+3^x=5", "x^2=4", "log(x)=2", "3^x=2^x", "2^x=3^(x+1)",
           "2^(x^3)=8", "2^(x^2)*3^x=6", "x*2^x=8", "x^x=4", "sqrt(2)^x=4", "3^x=2"]

# (saisie, solutions arrondies à 10⁻³) : exercices 2.18, 2.21, 2.23 (solutions p. 38-39), p. 26, p. 28-29, 2.26, 2.27, 2.32
BATTERIE_E2 = [
    ("10^x=8", [0.903]), ("10^x=0,65", [-0.187]), ("10^(2x)=0,7", [-0.077]), ("10^x*(10^x-4)=0", [0.602]), ("10^(3x)=25", [0.466]),
    ("(10^(-x)-1)*(10^(-x)-8)=0", [-0.903, 0.0]),
    ("e^x=7", [1.946]), ("3e^x=0,65", [-1.529]), ("x=ln(3)", [1.099]), ("2x=ln(0,1)", [-1.151]), ("e^(-0,01x)=0,7", [35.667]),
    ("2^x=100", [6.644]), ("10^x=5", [0.699]), ("3^(x-1)=10", [3.096]), ("5^(2x+3)=7", [-0.895]), ("1,04^x=100", [117.417]),
    ("4^(x-4)=20", [6.161]), ("5^(8x)=-25", []), ("12^x=49", [1.566]),
    ("3^x=20", [2.727]), ("4^(2x+1)=60", [0.977]), ("1,0325^n=3", [34.35]), ("0,8^n=0,5", [3.106]), ("37*e^(-0,02t)=25", [19.602]),
    ("2000*1,045^n=3805", [14.612]), ("1,0375^n=3", [29.842]), ("e^(0,05t)=2", [13.863]),
    # autres formes
    ("2*3^x=-6", []), ("10^x=0", []), ("3*2^x=5", [0.737]), ("-2^x=-10", [3.322]), ("e^x=1", [0.0]), ("(1/2)^x=3", [-1.585]),
    ("2^(-x)=3", [-1.585]), ("20=2*3^x+2", [2.0]), ("100=2^x", [6.644]), ("5^x/2=3", [1.113]),
    ("exp(x)=7", [1.946]), ("2^(x/2)=5", [4.644]),
]

SANS_E2 = ["x*2^x=8", "2^x+3^x=5", "x^x=4", "2^(x^3)=8",
           "x^2=4", "2x+1=9", "sqrt(2)^x=3", "2*10^x=0*x"]

# (saisie, solution arrondie à 10⁻³) : exercice 2.24 a-c du corrigé, p. 26 n° 3, puis d'autres formes
BATTERIE_E3 = [
    ("2^(x-1)=3^x", -1.710), ("4^(x+1)=6^(3x)", 0.348), ("2^(x+4)=3^(x-1)", 9.548), ("2^x=3^(x+1)", -2.710),
    ("3^x=2^x", 0.0), ("2^(-x)=3^x", 0.0), ("3^(x+1)=2^x", -2.710), ("5^(2x+1)=3^(x+2)", 0.277), ("2^(1-x)=3^(x+1)", -0.226),
    ("2^(x-1)=5^(x+1)", -2.513), ("2^(x/2)=3^(x-1)", 1.461), ("(1/2)^x=3^(x+1)", -0.613), ("1,5^x=2^(x+1)", -2.409),
    ("10^x=3^(x+1)", 0.912), ("10^(x-1)=3^x", 1.912), ("0,1^x=2^(x+1)", -0.231), ("3^(2x)=2^(3x+1)", 5.885),
    ("7^(x+2)=2^(3-x)", -0.687), ("2^(-x)=3^(1-x)", 2.710),
    # facteurs constants (k·a^f = m·b^h) et base e (ln des deux membres)
    ("2*2^x=3^x", 1.710), ("3*2^x=5*3^(x-1)", 1.450), ("10*2^x=3^x", 5.679), ("2*2^(x-1)=3^x", 0.0), ("0,5*3^x=2^(x+1)", 3.419),
    ("5*10^x=2^x", -1.0), ("3^x*2=5*2^x", 2.260),
    ("e^x=2^x", 0.0), ("e^x=2^(x+1)", 2.259), ("2*e^x=3^x", 7.029), ("e^(2x)=3^(x-1)", -1.219), ("3^(x+1)=e^x", -11.141),
]

SANS_E3 = ["x*2^x=8", "2^x+3^x=5", "2^(x^3)=3^x", "x^x=3^x", "2^x+1=3^x", "2^x=3^x+x"]

# (saisie, solutions) : exercices 2.15 e-g j-l, 2.18 c d f, 2.21 d, 2.22 a-c du corrigé, puis d'autres formes
BATTERIE_E4 = [
    ("log(x)=3", [1000.0]), ("log(x)=-1", [0.1]), ("log(x)=-4", [0.0001]), ("log(x)=0", [1.0]), ("log(log(log(x)))=0", [1e10]),
    ("log(5-x)=8", [-99999995.0]), ("log(x)=1,5", [31.623]), ("log(x)=-0,27", [0.537]), ("2log(x)-5=0", [316.228]),
    ("ln(x)=3", [20.086]), ("log2(x)=4", [16.0]), ("2log_3(x)=10", [243.0]), ("log_x(256)=4", [4.0]),
    # autres formes
    ("log_2(x)=4", [16.0]), ("ln(x)=0", [1.0]), ("ln(x)=1", [2.718]), ("3=log(x)", [1000.0]), ("log(x)+1=3", [100.0]),
    ("log(x)/2=1", [100.0]), ("-log(x)=2", [0.01]), ("log(x^2)=2", [-10.0, 10.0]), ("log(2x+1)=3", [499.5]), ("8=log(2x+1)", [49999999.5]),
    ("log(x^2-3x)=1", [-2.0, 5.0]), ("log(x^2+x+3)=0", []), ("log(x^2+x+3)+1=1", []), ("ln(2-x)=1", [-0.718]), ("log(-3-x)=1", [-13.0]), ("log(3-2x)=1", [-3.5]),
    ("log(-x)=2", [-100.0]), ("log_x(16)=2", [4.0]), ("log_x(81)=4", [3.0]), ("log_x(8)=3", [2.0]), ("log_x(1/8)=3", [0.5]),
    ("log_x(1/16)=4", [0.5]),
    # base inconnue dont la racine n'est pas exacte : √255, 2^(1/3), 12^(1/4), √(5/2), x = 7
    ("log_x(255)=2", [15.969]), ("log_x(2)=3", [1.260]), ("log_x(12)=4", [1.861]), ("log_x(5/2)=2", [1.581]), ("log_x(7)=1", [7.0]), ("log(log(x))=1", [1e10]),
    # puissance rationnelle d'un entier qui est un rationnel : 8^(2/3) = 4, 9^(3/2) = 27 (Javet 3.5 b c)
    ("log8(x)=2/3", [4.0]), ("log_9(x)=3/2", [27.0]), ("log_0,01(x)=1/2", [0.1]), ("log_4(x)=-3/2", [0.125]), ("log_8(x)=1/3", [2.0]),
    ("log5(x)=-2", [0.04]), ("ln(ln(x))=0", [2.718]), ("log(log(x-1))=0", [11.0]),
]

# (saisie, valeur exacte rationnelle ou None, valeur approchée) : exercices 2.15 a-d h i, 2.20 a-h et d'autres formes
BATTERIE_C1 = [
    ("log(1000000)", F(6)), ("log(1)", F(0)), ("log(1/100000)", F(-5)), ("log(0,001)", F(-3)), ("log(sqrt(10))", F(1, 2)), ("log(0,01)", F(-2)),
    ("log2(64)", F(6)), ("log_8(64)", F(2)), ("log_5(1/25)", F(-2)), ("log_5(0,2)", F(-1)), ("log_7(1)", F(0)), ("log_20(20)", F(1)),
    ("log_2(1/8)", F(-3)), ("log_4(sqrt(2))", F(1, 4)),
    # autres formes
    ("log_9(27)", F(3, 2)), ("log_8(2)", F(1, 3)), ("log_4(8)", F(3, 2)), ("log_25(sqrt(5))", F(1, 4)), ("log_2(0,125)", F(-3)), ("log(10^3)", F(3)),
    ("log(10^(1/2))", F(1, 2)), ("log_27(1/9)", F(-2, 3)), ("log_2(sqrt(8))", F(3, 2)), ("log_100(10)", F(1, 2)), ("log_1,5(2,25)", F(2)),
    ("ln(1)", F(0)), ("ln(e)", F(1)), ("ln(e^3)", F(3)), ("log_10(1000)", F(3)),
    ("log_2(50)", 5.644), ("log(50)", 1.699), ("ln(7)", 1.946), ("log_3(10)", 2.096), ("log_2(sqrt(3))", 0.792), ("log_5(0,3)", -0.748),
    ("log_4(0,3)", -0.868), ("log(2)", 0.301), ("log_6(2)", 0.387), ("log_2(10)", 3.322), ("log_3(sqrt(2))", 0.315),
]


# (saisie, solutions arrondies à 10⁻³) : formes trouvées par la chasse aux trous du 27.10.2026, corrigées ensuite, groupe par groupe
BATTERIE_AUDIT = [
    # Δ = 0, x² · log(a) = 0, jamais « + − » (F1 à F4)
    ("2^(x^2)=1", [0.0]), ("1=5^(x^2)", [0.0]), ("1/2=2^(x^2-1)", [0.0]), ("2^(x^2)=2^(2x-1)", [1.0]), ("0,5^(x^2)*0,5^(2x-3)=16", [-1.0]),
    ("4^(x^2)=2^(4x-2)", [1.0]), ("3x-1=-ln(7)", [-0.315]),
    # isoler les exponentielles : un terme de l'autre côté, les deux membres par −1, le dénominateur (T1, T5)
    ("2^x-3^(x+1)=0", [-2.710]), ("4^x-2^(x+1)=0", [1.0]), ("2^x-2^(2x-3)=0", [3.0]), ("0=2*3^x-5*2^x", [2.260]), ("-3^x+e^x=0", [0.0]),
    ("2^x+3^(x+1)=0", []), ("e^x+2^x=0", []), ("-2^x-5^x=0", []), ("3^(x+1)/2^x=1", [-2.710]), ("-2^x=-3^(x+1)", [-2.710]),
    ("-3*2^x=-5*3^x", [-1.260]), ("(2^x-3^x)(5^x-25)=0", [0.0, 2.0]),
    # exponentielle au dénominateur (T2) ; None : tout réel ; la méthode A seule quand la méthode B diviserait par un coefficient nul
    ("8/2^x=2", [2.0]), ("100/10^x=0,1", [3.0]), ("3/e^x=6", [-0.693]), ("2^x/3^x=1", [0.0]), ("1/2^x=8", [-3.0]), ("5^x/5^(2x-1)=1/25", [3.0]),
    ("3*2^x/4^x=5", [-0.737]), ("2^(x+1)/2^x=2", None), ("2^(2x)/4^(x-1)=8", []), ("4^x=2^(2x)", None),
    # exposant du 2e degré, second membre quelconque (T3) : P(x) = log(c)/log(a), puis x² = k ou le discriminant
    ("2^(x^2)=5", [-1.524, 1.524]), ("2^(x^2-1)=5", [-1.823, 1.823]), ("2^(x^2+x)=5", [-2.104, 1.104]), ("2^(x^2)=1/2", []),
    ("e^(x^2)=2", [-0.833, 0.833]), ("2^(x^2)=3^x", [0.0, 1.585]), ("e^(-x^2)=0,5", [-0.833, 0.833]), ("3^(x^2+1)=7", [-0.878, 0.878]),
    ("2^(x^2)*3^x=6", [-2.585, 1.0]), ("10^(x^2)=5", [-0.836, 0.836]), ("5*2^(x^2)-3=7", [-1.0, 1.0]), ("2^(x^2-3x+2)=3", [0.145, 2.855]),
    ("2^(x^2)*2^x=1/4", []), ("2^(x^2)*3^(x^2)=1", [0.0]),
    # base inconnue, exposant négatif ou nul, argument 1 (T7)
    ("log_x(8)=-1", [0.125]), ("log_x(4)=-2", [0.5]), ("log_x(1/9)=-2", [3.0]), ("log_x(2)=-3", [0.794]), ("log_x(5)=0", []), ("log_x(1)=0", None),
    ("log_x(1)=2", []), ("log_x(1)=3", []), ("log_x(1)=-1", []),
    # argument négatif ou nul : une base admissible est > 0, donc xᵏ > 0 et n = xᵏ est impossible
    ("log_x(-8)=3", []), ("log_x(0)=2", []), ("log_x(-4)=-1", []), ("log_x(-4)=1", []), ("log_x(-2)=1/2", []), ("log_x(-1)=0", []),
    # produit nul polynôme × exponentielle (T8)
    ("x*2^x=0", [0.0]), ("10^x*(x-4)=0", [4.0]), ("(x^2-1)*e^x=0", [-1.0, 1.0]), ("3x*2^x=0", [0.0]), ("(x^2+1)*2^x=0", []),
    ("(x-1)(2^x-8)=0", [1.0, 3.0]), ("2^x*(x+2)*(3^x-9)=0", [-2.0, 2.0]),
    # log(x²) = c par l'exponentielle des deux membres, x² = 10^c ⇔ x = ±√(10^c) (T4 limité)
    ("log(x^2)=-1", [-0.316, 0.316]), ("ln(x^2)=1", [-1.649, 1.649]), ("log_2(x^2)=-1", [-0.707, 0.707]), ("log(x^2)=1,5", [-5.623, 5.623]),
    ("log(x^2)=1/2", [-1.778, 1.778]), ("2ln(x^2)-5=0", [-3.490, 3.490]), ("ln(ln(x^2))=1", [-3.893, 3.893]),
    # exposants ² et ³ saisis au clavier d'un téléphone (D3)
    ("2^(x²)*4^x=8", [-3.0, 1.0]), ("log(x²)=2", [-10.0, 10.0]), ("9^(x²)=3^(x+1)", [-0.5, 1.0]), ("e^(x²)=e^(2x+3)", [-1.0, 3.0]),
    # produit ou quotient de puissances de 10 ou de e : la méthode A fusionne (aᵐ / aⁿ = aᵐ⁻ⁿ) puis conclut par la définition
    # mise en évidence : somme de termes de même base dont les exposants diffèrent d'un entier (D1)
    ("2^x+2^(x+1)=12", [2.0]), ("2^x+2^x=8", [2.0]), ("3^(x+1)+3^x=36", [2.0]), ("2^(x+2)-2^x=12", [2.0]), ("5^x+5^(x+1)+5^(x+2)=155", [1.0]),
    ("2^x+2^(x+1)+3=15", [2.0]), ("12=2^x+2^(x+1)+3", [1.585]), ("2*2^x+2^(x+1)=16", [2.0]), ("2^x+3*2^x=16", [2.0]), ("2^(x+1)-2^x=4", [2.0]),
    ("3^(x+1)-3^x=18", [2.0]), ("e^x+e^x=8", [1.386]), ("e^x+2e^x=9", [1.099]), ("10^x+10^(x+1)=110", [1.0]), ("2^(2x)+2^(2x+1)=48", [2.0]),
    ("2^(x^2)+2^(x^2+1)=12", [-1.414, 1.414]), ("0,5^x+0,5^(x+1)=1,5", [0.0]), ("2^(x+1)+2^(x-1)=10", [2.0]), ("3*2^x+2^(x+2)=28", [2.0]),
    ("2^x+2^(x+1)+2^(x+2)=28", [2.0]), ("4^x+4^(x+1)=20", [1.0]), ("2^x/2+2^x=12", [3.0]),
    ("2^x-2^x=0", None), ("2^x-2^x=3", []), ("2^x-2^(x+1)=4", []), ("2^x-2^(x+1)=0", []), ("-2^x-2^(x+1)=12", []), ("2^(x+1)-2^(x+1)=0", None),
    # solutions en ordre croissant, x₁ < x₂ même quand le coefficient de x² est négatif
    ("e^(x/2)/e^(x^2+x)=1/4", [-1.454, 0.954]), ("10^(-x)/10^(x^2)=1/4", [-1.423, 0.423]), ("e^(-x^2+3x)=2", [0.252, 2.748]),
    ("2^(-x^2)=1/2", [-1.0, 1.0]), ("2^(-x^2+x)=3^x", [-0.585, 0.0]), ("3^(-x^2)*2^x=1", [-0.0, 0.631]),
    # mise en évidence en base e : le coefficient (1 + e) est irrationnel, x = ln(5/(1 + e))
    ("e^x+e^(x+1)=5", [0.296]), ("5=e^x+e^(x+1)", [0.296]), ("3+e^x+e^(x+2)=10", [-0.181]), ("e^(x^2)+e^(x^2+1)=5", [-0.544, 0.544]),
    ("e^(x+1)-e^x=3", [0.557]), ("2e^x+e^(x+1)=8", [0.528]), ("e^x+e^(x+1)-e^x=3", [0.099]), ("e^x-e^(x+1)=5", []), ("e^(x+1)-e^x=0", []),
    ("e^(x+1)-2e^(x+1)=3", []), ("e^x+e^(x+1)+e^(x+1)=4", [-0.476]),
    ("3^x+3^(x+2)=30", [1.0]), ("2^x+2^(x-1)=6", [2.0]), ("7*2^x+2^(x+3)=60", [2.0]), ("2^x/3+2^(x+1)/3=2", [1.0]),
    # regroupement : équation dont chaque terme est k·a^P, au plus deux bases, des deux côtés (D4)
    ("2^x-3^(x+1)=3^x", [-3.419]), ("2^x+2^(x+1)=2^(x+2)", []), ("2^(x+1)=2^x+3^x+3^(x+1)", [-3.419]), ("3^x+2^x=2*3^x", [0.0]),
    ("5*2^x=3^x+2^(x+1)", [2.710]), ("2^x+3^x=2^(x+1)+3^(x-1)", [1.0]), ("4*3^x-3^(x+1)=2^x", [0.0]), ("2^(2x)-3^x=3^(x+1)", [4.819]),
    ("2^x-2^x=3^x-3^x", None), ("2^x-3^x=2^x-3^(x+1)", []), ("3*2^x-2^(x+1)=2*3^x-3^x", [0.0]), ("2^x+2^(x+1)=3^x+3^(x+1)", [-0.71]),
    ("e^x+2e^x=2^x", [-3.58]), ("2^x=3*2^x-2^(x+1)+3^x", []), ("0=2^x+3^(x+1)-2^(x+2)+3^x", [-0.71]),
    ("e^(2x)/e^x=5", [1.609]), ("10^(2x)/10^x=3", [0.477]), ("e^x*e^(x+1)=5", [0.305]), ("e^(3x)/e^(x-1)=7", [0.473]),
]

# Problèmes d'application (T33, 28.10.2026) : base écrite avec un taux (carte « Calculer la base »), valeurs vérifiées avec mpmath
BATTERIE_APPLICATIONS = [
    ("3=(1+3,75/100)^x", [29.842]), ("3=(1+3,75%)^x", [29.842]), ("3 = (1 + 3,75 %)^x", [29.842]), ("2=(1+0,04)^n", [17.673]),
    ("(1+0,035)^n=2", [20.149]), ("0,5=(1-20/100)^n", [3.106]), ("2000*(1+0,045)^n=3805", [14.612]), ("1500*(1+4,5%)^t=3000", [15.747]),
    ("4=(1+0,5/100)^n", [277.951]), ("0,25=(1-5/100)^n", [27.027]), ("-2=(1+0,04)^n", []), ("2=1,0375^x", [18.828]),
    # avec un paramètre (capital, valeur initiale) : la carte « Simplifier par Q » ; l'inconnue est la lettre de l'exposant
    ("3Q=Q(1+3,75/100)^x", [29.842]), ("3Q = Q*(1+3,75%)^x", [29.842]), ("2C=C(1+0,04)^n", [17.673]), ("C0*1,05^n=2*C0", [14.207]),
    ("C_0*1,05^n=2C_0", [14.207]), ("V0/2=V0(1-20/100)^n", [3.106]), ("V_0/4=V_0*(1-5%)^n", [27.027]), ("Q/2=Q*1,04^n", [-17.673]),
    ("-2Q=Q*1,04^n", []), ("Q*1,04^n=Q", [0.0]), ("5Q/2=Q*(1+3,5%)^t", [26.635]), ("2C=C*(1+4,5%)^n", [15.747]),
]

# Aucune méthode ne s'applique (EL-11) : un vrai hors-programme, ou une forme du programme que l'outil ne gère pas encore
HORS_PROGRAMME = ["x*2^x=8", "2^x+3^x=5", "2^x+3^x+1=5", "2^x-3^(x+1)=3^x+1", "e^x+e^(x+1)=2^x", "x^x=4", "2^x=x+1", "2^(sqrt(x))=4", "2^(1/x)=4", "x/2^x=1", "x*e^x=1", "2^x=3^x+x",
                  "log(x)=x-1", "ln(x)=x", "x*log(x)=1", "e^x=ln(x)", "log(x)=2^x", "log(x)/x=1", "ln(x)+x=2",
                  # pour les 3C, le 2e degré en a^x et les exposants qui ne diffèrent pas d'un entier (la mise en évidence est au programme)
                  "4^x-2^x-6=0", "9^x-3^x=6", "e^(2x)-3e^x+2=0",
                  "e^x+e^(-x)=3", "2^(2x)-5*2^x+4=0", "2^x+1=3^x"]
PAS_ENCORE = ["log(x)=log(5)", "log(x^2+1)=-1",
              "log(x)+log(x-1)=1", "2^(x^3)=8", "2^(x^3)=3^x", "5^(x^3+1)=7", "log(x)+log(2)=1", "log(x)-log(2)=1"]

# Équations sans exponentielle ni logarithme : le message dit ce que l'outil traite
SANS_EXP_LOG = ["x^2=4", "2x+1=9", "sqrt(x)=3", "(x+1)^3=8", "x^3-x=0", "3x=6", "x/2=1"]

# Calculs que l'outil ne traite pas (message de calcul) et saisies refusées à la lecture
CALCULS_NON_RESOLUS = ["2log(5)", "log(2)+log(3)", "log_2(e)", "log(0)", "log(-5)", "ln(0)", "2+3", "5", "e", "sqrt(2)"]
ERREURS_DE_LECTURE = ["", "2e=5", "x+y=3", "x<3", "2^x>=3", "log_1(x)=2", "log x = 2", "3^x=2=1", "=3", "3^x=", "e^-0,02t=1", "sin(x)=0", "cos(x)=1", "tan(x)=2", "lg(x)=2", "2lg(x)=4", "sin x = 0", "2 000^x=3",
                      "(x+1=3", "x+1)=3"]


# Filière M (T35) : équations propres aux 2M (ensemble de définition, regroupement, vérification, changement de variable) ; complétée aux étapes 2 à 4.
# (saisie, solutions arrondies à 10⁻³ après la vérification contre l'ED) ; étape 2 : un seul logarithme, l'ED d'abord puis la vérification
BATTERIE_M = [
    ("log(x-3)=1", [13.0]), ("log(x^2-x)=1", [-2.702, 3.702]), ("ln(x-1)=2", [8.389]), ("log(5+x)=1", [5.0]), ("log(2-x)=0", [1.0]),
    ("log(x+0,5)=1", [9.5]), ("log(t-3)=1", [13.0]), ("log(x^2)=-1", [-0.316, 0.316]),
    # ED vide : S = ∅ tout de suite
    ("log(-x^2-1)=0", []), ("ln(-x^2-x-1)=2", []),
    # base inconnue : x > 0 et x ≠ 1, la solution négative est rejetée par la vérification
    ("log_x(9)=-2", [0.333]), ("log_x(4)=2", [2.0]), ("log_x(1)=2", []), ("log_x(27)=3", [3.0]), ("log_x(1/8)=3", [0.5]),
    # étape 3, exemples du plan : sommes, différences, constante d'un côté, log(x²) intact
    ("log(x)+log(x-1)=1", [3.702]), ("log(x+1)+log(2x)=log(3)", [0.823]), ("log(5+x)=log(4-x)+1", [3.182]), ("log(x^2)+log(3)=10", [-57735.027, 57735.027]),
    ("3log(x)=2log(8)", [4.0]), ("log2(3x-4)+log2(10x-4)=2log2(5x-2)", [6.0]), ("log(x-3)+log(1-x)=0", []), ("ln(x)+ln(x-1)=0", [1.618]),
    # polycopié Javet 2M, exercices 3.11 et 3.12 (solutions p. VIII) ; brochure Amaudruz 2M, 7.9
    ("log(9x+5)-log(x)=1", [5.0]), ("log(x)=log(16)+2log(3)-2log(2)-1/2*log(9)", [12.0]), ("log(x)=4log(5)+log(1/5)-3log(3)+1/3*log(27)", [13.889]),
    ("log(x+2)-log(3)=log(2x-1)+log(7)", [0.561]), ("log(x+2)+log(x-1)=log(18)", [4.0]), ("log(2x-3)+log(3x+10)=4log(2)", [2.0]),
    ("log2(x^2-4)=2log2(x+3)", [-2.167]), ("log3(35-x^3)=3log3(5-x)", [2.0, 3.0]), ("log(x^2-7)=2log(x+3)", [-2.667]),
    ("log(20)+log(x^2-9)-log(x+3)=1+log(2x+6)", []), ("3ln(x)=ln(125)", [5.0]), ("2log(x-2)=log(3x-8)", [3.0, 4.0]),
    ("log2(x+1)-log2(3)=log2(2x-3)+log2(7)", [1.561]), ("ln(2x-5)+ln(3x+7)=4ln(2)", [3.0]), ("log7(20)+log7(x^2-4)-log7(x-2)=1+log7(2x+4)", []),
    # autres formes : coefficients, différences, deux membres, solution rejetée, constantes absorbées
    ("2log(x)-log(x+1)=0", [1.618]), ("log(x)+log(x)=2", [10.0]), ("log(x)=log(5)", [5.0]), ("log(x^2)=log(x)", [1.0]), ("log(x)+log(x-2)=log(3)", [3.0]),
    ("log(x)+log(x+3)=2", [8.612]), ("log(x)+log(x-1)+3=5", [10.512]), ("1=log(x)+log(x-1)", [3.702]),
    ("log(x)-log(x-1)=log(2)", [2.0]), ("2log(x)=log(x+6)", [3.0]), ("-log(x)+log(x+1)=log(2)", [1.0]), ("log3(x)+log3(x-2)=1", [3.0]),
    ("ln(x)+ln(x+1)=ln(6)", [2.0]), ("log(x^2)-log(x)=1", [10.0]), ("log(x-1)=log(3)+log(x)-log(2)", []),
    ("log(x^2)+log(5)=-1", [-0.141, 0.141]), ("2log(x)+log(3)=log(1/4)", [0.289]),
    # logarithmes imbriqués (1c, 29.10.2026) : l'ED est calculé couche par couche, toutes bases (log, log_a avec a > 1 ou a < 1, ln mêlé à log)
    ("log(log(x))=1", [1e10]), ("log(log(log(x)))=0", [1e10]), ("log(log(x-1))=0", [11.0]), ("log_2(log_2(x))=1", [4.0]), ("log_3(log_3(x))=0", [3.0]),
    ("log_0,5(log_0,5(x))=1", [0.707]), ("log_0,5(log_0,5(x))=0", [0.5]), ("log(ln(x))=0", [2.718]), ("ln(log(x))=0", [10.0]), ("log(log(2x))=0", [5.0]),
    ("log_2(log_2(x-1))=1", [5.0]), ("ln(ln(ln(x)))=0", [15.154]), ("log(log(3-x))=-1", [1.741]), ("2log(log(x))=1", [1453.04]), ("log(ln(ln(x)))=0", [15.154]),
]

# deux termes seulement : pas un trinôme en t = aˣ, la filière M suit la méthode de la 3C (même base ou logarithmes), sortie identique ;
# Javet 2.2 b c, Amaudruz 6.1 a e g
BATTERIE_M_DEUX_TERMES = [
    ("(3^(x-1))^3=9*3^(x-2)", [1.5]), ("2^(x+6)=2^(3x+4)", [1.0]), ("2^x-16*2^(3x+2)=0", [-3.0]), ("4^(x+2)-8^x=0", [4.0]), ("27^(x+2)=3^(5x+8)", [-1.0]),
    ("3^x=3*9^(x-1)", [1.0]), ("4^x=16^(2x+5)", [-10 / 3]), ("2^x+2^(x+1)=12", [2.0]),
]

# 2ᵉ degré en aˣ (filière M seulement) : (saisie, solutions arrondies à 10⁻³), les deux méthodes donnent le même S ; Amaudruz 6.1 c i j k l, 7.8 i
BATTERIE_M_VAR = [
    ("3^x+9^x=90", [2.0]), ("4^x-2^x-6=0", [1.585]), ("e^(2x)-3e^x+2=0", [0.0, 0.693]), ("e^(4x)-29e^(2x)=-100", [0.693, 1.609]),
    ("3*2^(2(x+1))-10*2^(x+2)=32", [2.0]), ("2*2^(6x-1)+3*2^(3x+1)+9=0", []), ("3^(x+1)+3^(-x)=4", [-1.0, 0.0]), ("2^(2x+2)-7*2^(x+1)=8", [2.0]),
    ("4^x+2^x=2", [0.0]), ("2^x+2^(-x)=2", [0.0]), ("9^x-4*3^(x+1)+27=0", [1.0, 2.0]), ("25^x-6*5^x+5=0", [0.0, 1.0]), ("2^(2x)-5*2^x+4=0", [0.0, 2.0]),
    ("2^(2t)-3*2^t=-2", [0.0, 1.0]), ("0,25^x-0,5^x-2=0", [-1.0]), ("e^x-6+8e^(-x)=0", [0.693, 1.386]), ("4^x=2^(x+1)+3", [1.585]),
    ("8^x-2*4^x-8*2^x=0", [2.0]), ("4^x+3*2^x=-4", []),
]
# au programme M, reconnues, mais avec des racines irrationnelles : pas encore ; en 3C : hors programme
M_VAR_PAS_ENCORE = ["e^x+e^(-x)=3", "4^x-2^x-1=0", "2^x+2^(-x)=3", "3^x+3^(-x)-6*3^(-3x)=0"]

# T36 (29.10.2026), partie B : exposants 1/x, √x, ±ln x (Javet 2.2 i, 3.15 d e f ; Amaudruz 7.8 d). (saisie, solutions arrondies à 10⁻³) ; les deux méthodes
# donnent le même S, sauf la méthode « même base / définition » quand le second membre n'est pas une puissance de la base (message)
BATTERIE_M_EXPOSANTS = [
    ("e^(6/x)=e^(x-1)", [-2.0, 3.0]), ("e^(2/x)=e^(x+1)", [-2.0, 1.0]), ("e^(2/x)=e^(1/x+1)", [1.0]), ("3^(1/x)=3^2", [0.5]), ("3^(1/x)=3^(-1)", [-1.0]),
    ("3^(-1/x)=20", [-0.367]), ("10^(1/x)=3", [2.096]), ("e^(1/x)=2", [1.443]), ("2^(1/x)=8", [0.333]), ("2^(3/(x+1))=5", [0.292]), ("3^(2/x)=81", [0.5]),
    ("5^(x/(x-1))=25", [2.0]), ("2^(x/(x-1))=3", [2.710]), ("e^((x+1)/x)=e^3", [0.5]),
    ("7^(sqrt(x))=3", [0.319]), ("2^(sqrt(x)+1)=8", [4.0]), ("e^(sqrt(x))=e^2", [4.0]), ("10^(sqrt(x))=1000", [9.0]),
    ("7^(sqrt(x))=-3", []), ("7^(sqrt(x)+1)=3", []), ("7^(sqrt(x))=7^(-1)", []),
    ("e^(-ln(x))=3", [0.333]), ("e^(-ln(x))=0,2", [5.0]), ("2^(-log_2(x))=3", [0.333]), ("10^(-log(x))=4", [0.25]), ("e^(ln(x-1))=3", [4.0]),
    ("e^(-ln(x-1))=3", [1.333]), ("e^(-ln(x))=-2", []),
]

# T36, partie C : base polynomiale du 1er degré, argument constant (Amaudruz 7.3 b, 7.7 e, 7.7 i) ; k entier non nul
BATTERIE_M_BASE_POLYNOMIALE = [
    ("log_(2x)(1296)=4", [3.0]), ("log_(5x)(1000)=3", [2.0]), ("log_(x+1)(5)=16", [0.106]), ("log_(3x)(1/8)=-3", [0.667]), ("log_(x-1)(27)=3", [4.0]),
    ("log_(-x)(4)=2", [-2.0]), ("log_(2x)(9)=2", [1.5]), ("log_(x+2)(16)=2", [2.0]), ("log_(2x-1)(25)=2", [3.0]), ("log_(x+1)(8)=3", [1.0]),
    ("2=log_(x+1)(9)", [2.0]), ("log_(x+3)(1)=2", []), ("log_(2x)(5)=2", [1.118]), ("log_(x+4)(1/16)=-2", [0.0]), ("log_(3-x)(125)=3", [-2.0]),
]

# T36, partie D : bicarré en t = aˣ (exposants de t : −3, −1, 1 ou 1, 3, 5 …), Javet ex. 4 et 2.4 b : t⁴ − 10t² + 9 = 0 ; u = t² > 0
BATTERIE_M_BICARRE = [
    ("9*3^(-3x)-10*3^(-x)+3^x=0", [0.0, 1.0]), ("4*2^(-3x)-5*2^(-x)+2^x=0", [0.0, 1.0]), ("5^(3x)-26*5^x+25*5^(-x)=0", [0.0, 1.0]),
    ("e^(3x)-5*e^x+4*e^(-x)=0", [0.0, 0.693]), ("2^(3x)-10*2^x+9*2^(-x)=0", [0.0, 1.585]), ("3^x-3*3^(-x)-4*3^(-3x)=0", [0.631]),
    ("3^x+3*3^(-x)+2*3^(-3x)=0", []), ("3^x+3^(-x)+3^(-3x)=0", []), ("0,5^x-5*0,5^(-x)+4*0,5^(-3x)=0", [0.0, -1.0]),
]

# T36, partie E : base inconnue et exposant rationnel log_x(n) = p/q (Javet 3.5 e) ; x = n^(q/p), x > 0 et x ≠ 1
BATTERIE_M_BASE_RATIONNELLE = [
    ("log_x(32)=5/3", [8.0]), ("log_x(5)=2/3", [11.180]), ("log_x(1/8)=-3/2", [4.0]), ("5/3=log_x(32)", [8.0]), ("log_x(1)=1/2", []), ("log_x(8)=-2/3", [0.044]),
    ("log_x(9)=3/2", [4.327]), ("log_x(27)=3/2", [9.0]), ("log_x(16)=4/3", [8.0]), ("log_x(4)=1/2", [16.0]), ("log_x(0,25)=-1/2", [16.0]), ("log_x(2)=3/4", [2.520]),
]

# T36, partie F : second membre irrationnel (e³, √10) d'un regroupement, P(x) = K du 1er ou du 2ᵉ degré ou xⁿ = K ; ln, log et log_a
BATTERIE_M_IRRATIONNEL = [
    ("ln(x)+ln(x+1)=3", [4.009]), ("log(x)+log(x+1)=1/2", [1.347]), ("ln(x)+ln(x-1)=1", [2.223]), ("ln(x^3)=2", [1.948]), ("ln(x^4)=2", [-1.649, 1.649]),
    ("ln(x)+ln(2)=3", [10.043]), ("log_2(x)+log_2(x+1)=1/2", [0.790]), ("ln(x)+ln(x+2)=1", [0.928]), ("2ln(x)+ln(3)=5", [7.034]), ("ln(x-1)+ln(x+1)=2", [2.896]),
    ("log(x^2-1)=1/2", [-2.040, 2.040]), ("ln(x)+ln(x-3)=2", [4.605]), ("log_3(x)+log_3(x+2)=1/2", [0.653]), ("ln(x^2+x)=3", [-5.009, 4.009]),
    ("ln(x)+ln(x+1)=-1", [0.286]), ("ln(2x)+ln(x)=1", [1.166]), ("ln(x^5)=3", [1.822]), ("ln(x^6)=1", [-1.181, 1.181]), ("log(x^3)=1/2", [1.468]),
]

# T36, partie G1 : exposant avec le carré d'une somme (Amaudruz 6.1 b) : la 3C ne le développe pas, la filière M oui
BATTERIE_M_CARRE_DANS_L_EXPOSANT = [
    ("7^(8x^2+4)=7^((2-3x)^2)", [0.0, 12.0]), ("2^(x^2+1)=2^((x+1)^2)", [0.0]), ("3^(x^2)=3^((x-2)^2)", [1.0]), ("5^(x^2-1)=5^((x-3)^2)", [1.667]),
    ("e^(x^2+x)=e^((x+2)^2)", [-1.333]), ("2^((x-1)^2)=2^(x^2+4)", [-1.5]),
]

# T36, partie G2 : second membre à calculer (quotient de sommes de logarithmes en base 10, Amaudruz 7.4 b)
BATTERIE_M_SECOND_MEMBRE_CALCULE = [
    ("log(x)=(log(20)+log(100)-log(2))/(log(5000)-log(5)+log(0,1))", [31.623]), ("log(x)=(log(20)+log(5))/(log(50)-log(5))", [100.0]),
    ("log(x+1)=(log(2)+log(500))/(log(50)-log(5))", [999.0]), ("(log(4)+log(25))/(log(2)+log(5))=log(x)", [100.0]), ("log(x)=(log(2)+log(5))/(log(20)+log(500))", [1.778]),
    ("log(x)=(log(8)+log(125))/(log(10)+log(100)-log(10))", [31.623]),
]

# T36, partie G3 : xᵏ·(a + b·log x) = 0, la solution x = 0 est rejetée par l'ensemble de définition (Amaudruz 7.8 b)
BATTERIE_M_PRODUIT_X_LOG = [
    ("x-x*ln(x)=0", [2.718]), ("2x+3x*log(x)=0", [0.215]), ("x^2*ln(x)=x^2", [2.718]), ("x*log_2(x)=3x", [8.0]), ("x*ln(x)=0", [1.0]), ("-x*ln(x)-x=0", [0.368]),
    ("3x-x*log(x)=0", [1000.0]), ("x*ln(x)=2x", [7.389]), ("5x^3=x^3*log(x)", [100000.0]), ("x*log(x)+x=0", [0.1]),
]

# identités sur l'ensemble de définition : S = ED (solutions None)
M_TOUT_L_ED = ["log(x)=log(x)", "log(x)+log(x-1)=log(x^2-x)", "2log(x)=log(x^2)+log(1)"]
# formes du programme M que l'outil ne traite pas encore, et vrais hors-programme
M_PAS_ENCORE = ["3^(2sqrt(x)-1)=5", "2^(sqrt(x)-1)=3", "ln(x)-ln(x+1)=1", "ln(x^3)+ln(2)=1", "log(x)=ln(2)", "log(1/x)=2", "log(x)*log(x-1)=1", "ln(x)=2ln(x+1)+1", "log(sqrt(x))=1"]
M_HORS_PROGRAMME = ["log(x)=x-1", "x*log(x)=1", "x*ln(x)=x^2", "x*ln(x)+1=0", "e^x=ln(x)", "log(x)+2^x=3"]



def entrees_el_m():
    """Entrées de l'instantané de la filière M : les équations logarithmiques de la 3C (avec ensemble de définition en M) et BATTERIE_M."""
    return list(dict.fromkeys([s for s, _ in BATTERIE_E4] + [s for s, _ in BATTERIE_M] + M_TOUT_L_ED + M_PAS_ENCORE + M_HORS_PROGRAMME
                                  + [s for s, _ in BATTERIE_M_VAR] + M_VAR_PAS_ENCORE + [s for s, _ in BATTERIE_M_DEUX_TERMES]
                                  + [s for s, _ in BATTERIE_M_EXPOSANTS] + [s for s, _ in BATTERIE_M_BASE_POLYNOMIALE]
                                  + [s for s, _ in BATTERIE_M_BICARRE] + [s for s, _ in BATTERIE_M_BASE_RATIONNELLE]
                                  + [s for s, _ in BATTERIE_M_IRRATIONNEL] + [s for s, _ in BATTERIE_M_CARRE_DANS_L_EXPOSANT]
                                  + [s for s, _ in BATTERIE_M_SECOND_MEMBRE_CALCULE]
                                  + [s for s, _ in BATTERIE_M_PRODUIT_X_LOG]))


def entrees_el():
    """Toutes les entrées de l'outil, sans doublon, dans l'ordre : équations résolues, calculs, messages, erreurs de lecture."""
    saisies = [s for batterie in (BATTERIE_E1, BATTERIE_E2, BATTERIE_E3, BATTERIE_E4, BATTERIE_C1, BATTERIE_AUDIT, BATTERIE_APPLICATIONS) for s, _ in batterie]
    saisies += SANS_E1 + SANS_E2 + SANS_E3 + HORS_PROGRAMME + PAS_ENCORE + SANS_EXP_LOG + CALCULS_NON_RESOLUS + ERREURS_DE_LECTURE
    return list(dict.fromkeys(saisies))
