import sys, re, json
sys.path.insert(0, "/Users/samimir/site/tests/python")
import moteurs
import resoudre_la as R
for e in sys.argv[1:]:
    s = R.resoudre(e)
    print("=====", e, s.get("erreur"))
    for c in s.get("cartes", []):
        print("--", c["titre"], c.get("titre_tex"), c.get("badge"))
        for b in c["blocs"]:
            if b["type"]=="texte": print("   T:", re.sub(r"\s+"," ",b["html"])[:700])
            else: print("   ", b["type"], str(b)[:200])
