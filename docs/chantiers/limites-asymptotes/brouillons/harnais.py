import sys, re, json, time
SP = "/private/tmp/claude-501/-Users-samimir-site/5986dd92-7195-422e-b742-61e244ea36c4/scratchpad"
sys.path.insert(0, SP)
sys.path.insert(0, "/Users/samimir/site/tests/python")
import moteurs
import sortie as so
ns = {}
exec(open(SP + "/sortie_ajouts.py", encoding="utf-8").read(), vars(so))
import limites_asymptotes as LA
import redaction_bh as RB
orig = LA._narrer_limite
etats = {}
def txtbloc(b):
    t = b["type"]
    if t == "texte": return re.sub(r"\s+", " ", b["html"])
    if t == "bh": return f"BH: haut {b['haut']} -> {b['dhaut']} | bas {b['bas']} -> {b['dbas']}"
    if t == "encadre": return f"[{b['genre']}] " + " // ".join(re.sub(r"\s+"," ",l) for l in b["lignes"])
    return f"{t}: " + str({k:v for k,v in b.items() if k!='type'})
def wrap(f, pt, ref, vtex, items, alternative=None, label="f(x)", prefixe=None):
    if label == "f(x)" and prefixe is None:
        t0 = time.time()
        try:
            d = RB.descente(f, pt, ref)
        except Exception as e:
            print(f"  ## ABANDON ({pt.tex()}): {type(e).__name__}: {e}")
            return orig(f, pt, ref, vtex, items, alternative, label, prefixe)
        print(f"  == DESCENTE en {pt.tex()} ({time.time()-t0:.1f}s) alertes={d['alertes']}")
        for i, e in enumerate(d["etapes"], 1):
            print(f"  Etape {i} : {e['titre']}")
            for b in e["blocs"]: print("      ", txtbloc(b)[:900])
        return
    return orig(f, pt, ref, vtex, items, alternative, label, prefixe)
LA._narrer_limite = wrap
for e in sys.argv[1:]:
    print("=====", e)
    r = LA.etudier(e)
    if not r["ok"]: print(r["erreur"])
