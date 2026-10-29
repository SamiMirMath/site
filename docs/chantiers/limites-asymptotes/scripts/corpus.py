# corpus.py — audit de l'étape 0 du chantier « Limites et asymptotes » (3M).
# Sert à : lancer le moteur actuel (limites-asymptotes/limites_asymptotes.py, `etudier`) sur le corpus de
# docs/reference/limites/ (corrigé du chapitre 8, exercices 3.8, 3.10, 3.11, feuille eˣ), à comparer chaque limite
# à la valeur calculée indépendamment par sympy.limit, et à repérer dans le texte rédigé les méthodes employées
# (BH, CC, MEE, repli, forme indéterminée, tableau de signes…). Ne modifie aucun fichier.
# Lancer, depuis la racine du dépôt (le script ajoute lui-même les dossiers des moteurs au chemin) :
#   uv run -q --no-project --python 3.12 --with sympy==1.13.3 --with mpmath==1.3.0 python -I docs/chantiers/limites-asymptotes/scripts/corpus.py <mode> [identifiants…]
# Modes : « resume » (une ligne par borne : valeur attendue, bornes de l'outil, méthodes repérées), « detail » (+ texte rédigé ;
# ex. `… detail 8.12e Ex5b`), « etudes » (3.10 et 3.11 : bornes et asymptotes), « etudes-detail » (+ texte rédigé).
# Les identifiants (8.11a, Ex5b, 3.8g, Fc…) sont ceux de la première colonne du tableau de audit-etape0.md.
# Écrit le 29.10.2026 .
import sys, os, re, json
R = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))      # racine du dépôt
for d in ("ensemble-definition", "moteur", "limites-asymptotes"):
    sys.path.insert(0, os.path.join(R, d))
import sympy as sp
from limites_asymptotes import etudier
x = sp.Symbol("x", real=True)
E, ln, oo = sp.exp, sp.log, sp.oo
# (id, saisie, cible ('+oo','-oo', (a,'+'|'-'|'2')), expr sympy indépendante)
C = [
 ("8.11a","e^x/ln(x)","+oo",E(x)/ln(x)),
 ("8.11b","x^3*ln(x)",(0,"+"),x**3*ln(x)),
 ("8.11c","x^2*e^x","-oo",x**2*E(x)),
 ("8.11d","x^2*e^(-5x)","+oo",x**2*E(-5*x)),
 ("Ex5a","x^2*e^(-x)","+oo",x**2*E(-x)),
 ("Ex5b","x*e^(1/x)",(0,"+"),x*E(1/x)),
 ("Ex5c","e^(-x)/x^2","-oo",E(-x)/x**2),
 ("Ex5d","e^(-x)/(4x)","+oo",E(-x)/(4*x)),
 ("8.12a","ln(x)/e^(2x)","+oo",ln(x)/E(2*x)),
 ("8.12b","e^(-x)*ln(x^3)","+oo",E(-x)*ln(x**3)),
 ("8.12c","e^(-x)*x","-oo",E(-x)*x),
 ("8.12d","e^x*ln(-x)","-oo",E(x)*ln(-x)),
 ("8.12e","x^3*e^(3x-5)","-oo",x**3*E(3*x-5)),
 ("8.12f","e^(1/x)/x^2",(0,"+"),E(1/x)/x**2),
 ("8.12g","e^(1/x)*x^2",(0,"+"),E(1/x)*x**2),
 ("8.12h","e^(-1/x)/x",(0,"+"),E(-1/x)/x),
 ("Ex6","e^((3x+4)/(x-2))","+oo",E((3*x+4)/(x-2))),
 ("Ex6cours","e^(-(3x+4)/(x-2))","+oo",E(-(3*x+4)/(x-2))),
 ("8.13a","e^(-x)","+oo",E(-x)),
 ("8.13b","e^((x^2-3x+2)/(2x^2))","+oo",E((x**2-3*x+2)/(2*x**2))),
 ("8.13c","e^(-2x/(x^2-5))","+oo",E(-2*x/(x**2-5))),
 ("8.13d","e^((3x^2+2)/(2x))","-oo",E((3*x**2+2)/(2*x))),
 ("8.13e","ln((3x^2-3x+2)/(x^2-5x+2))","+oo",ln((3*x**2-3*x+2)/(x**2-5*x+2))),
 ("8.13f","ln(1/x)","+oo",ln(1/x)),
 ("8.14","ln(1+e^x)/e^x","-oo",ln(1+E(x))/E(x)),
 ("3.8a","ln(x+1)/x",(0,"2"),ln(x+1)/x),
 ("3.8b","ln(cos(x))/x^2",(0,"2"),ln(sp.cos(x))/x**2),
 ("3.8c","(ln(x)-1)/(x-e)",(sp.E,"2"),(ln(x)-1)/(x-sp.E)),
 ("3.8d","ln(x^2-3)/(2-x)",(2,"2"),ln(x**2-3)/(2-x)),
 ("3.8e","ln(x^2+1)/x","-oo",ln(x**2+1)/x),
 ("3.8f","(ln(x)+1)/(1-ln(x))","+oo",(ln(x)+1)/(1-ln(x))),
 ("3.8g","ln(x^2)/ln(x)^2","+oo",ln(x**2)/ln(x)**2),
 ("3.8h","ln(x)/e^x","+oo",ln(x)/E(x)),
 ("3.8g'","(8^x-2^x)/(4x)",(0,"2"),(8**x-2**x)/(4*x)),
 ("3.8h'","log_5(x+2)/(x+1)",(-1,"2"),ln(x+2)/ln(5)/(x+1)),
 ("Fa","(e^x-e^2)/(x-2)",(2,"2"),(E(x)-E(2))/(x-2)),
 ("Fb","(e^x-1)/sin(x)",(0,"2"),(E(x)-1)/sp.sin(x)),
 ("Fc","x*e^x/(1-e^x)",(0,"2"),x*E(x)/(1-E(x))),
 ("Fd","x*e^(1/x)",(0,"+"),x*E(1/x)),
 ("Fe","(e^x+e^(-x))/(2x)","-oo",(E(x)+E(-x))/(2*x)),
 ("Ff","(2e^x-1)/(e^x+2)","+oo",(2*E(x)-1)/(E(x)+2)),
 ("Fg","(x^2+x)*e^x","-oo",(x**2+x)*E(x)),
 ("Fh","e^x/(x^2-2x+3)","+oo",E(x)/(x**2-2*x+3)),
]
ETUDES = [("3.10a","e^(-x^2)"),("3.10b","e^(1/x)"),("3.10c","(x^2-4x+4)e^x"),("3.10d","x/e^x"),("3.10e","(e^x+2)/(1-3e^x)"),
          ("3.11a","x^2*ln(x)"),("3.11b","ln(x^2+1)"),("3.11c","ln(x)/x"),("3.11d","ln(2x/(x+1))"),("3.11e","(ln(x)-2)/(ln(x)-1)")]

def plat(h):
    h = re.sub(r"<[^>]+>", " ", h)
    return re.sub(r"\s+", " ", h).strip()

def drapeaux(t):
    f = []
    for k, m in (("L'Hôpital","BH"),("croissance comparée","CC"),("n'est pas rédigé ici","REPLI"),("mise en évidence","MEE"),
                 ("forme indéterminée","FI"),("tableau de signes","TS"),("non déterminée","ND"),("conjuguée","CONJ"),("factorise","FACT")):
        if k in t: f.append(m)
    return f

def bornes_txt(r):
    out = {}
    for b in r.get("limites_bornes", []):
        if b["type"] == "inf":
            out[("+oo" if b["signe"] > 0 else "-oo")] = b["tex"]
        else:
            out[b["point_tex"]] = (b.get("gauche"), b.get("droite"))
    return out

mode = sys.argv[1] if len(sys.argv) > 1 else "resume"
filtre = sys.argv[2:] 
if mode in ("resume", "detail"):
    for cid, s, cible, ex in C:
        if filtre and cid not in filtre: continue
        if cible == "+oo": att = sp.limit(ex, x, oo)
        elif cible == "-oo": att = sp.limit(ex, x, -oo)
        else:
            a, d = cible
            att = (sp.limit(ex, x, a, "+") if d in "+2" else None, sp.limit(ex, x, a, "-") if d in "-2" else None) if d == "2" else sp.limit(ex, x, a, d)
        try:
            r = etudier(s, avec_bornes=True)
        except Exception as e:
            print(f"## {cid} | {s} | attendu {att} | EXCEPTION {type(e).__name__}: {e}"); continue
        if not r["ok"]:
            print(f"## {cid} | {s} | attendu {att} | ERREUR SAISIE: {r['erreur']}"); continue
        print(f"## {cid} | {s} | ED {r['ed_tex']} | attendu {att} | bornes {bornes_txt(r)}")
        for et in r["etudes"]:
            t = " ".join(plat(i.get("html","")) if i.get("type")!="tableau" else "[TABLEAU]" for i in et["etapes"])
            print(f"   [{et['ou']}] {drapeaux(t)}" + (f"\n      {t}" if mode == "detail" else ""))
else:
    for cid, s in ETUDES:
        if filtre and cid not in filtre: continue
        r = etudier(s, avec_bornes=True)
        if not r["ok"]:
            print(f"## {cid} | {s} | ERREUR: {r['erreur']}"); continue
        print(f"## {cid} | {s} | ED {r['ed_tex']} | bornes {bornes_txt(r)}")
        print("   asymptotes:", [(a['genre'], a.get('ou'), a.get('valeur_tex') or a.get('equation_tex') or a.get('point_tex')) for a in r['asymptotes']])
        for et in r["etudes"]:
            t = " ".join(plat(i.get("html","")) if i.get("type")!="tableau" else "[TABLEAU]" for i in et["etapes"])
            print(f"   [{et['ou']}] {drapeaux(t)}" + (f"\n      {t}" if mode == "etudes-detail" else ""))
