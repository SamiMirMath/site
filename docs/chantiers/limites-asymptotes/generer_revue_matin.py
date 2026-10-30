"""Génère docs/chantiers/limites-asymptotes/revue-matin.html : pour chaque exercice du corrigé (8.11 à 8.14, exemples 5 et 6), la rédaction
produite par l'outil (rendu réel, cartes dépliées), en regard la transcription du corrigé (docs/specifications/redaction-limites-3m.md) et
les écarts signalés ; en tête, un tableau récapitulatif (exercice, rédaction nouvelle / ancienne / repli, écarts).

    uv run -q --no-project --python 3.12 --with sympy==1.13.3 --with mpmath==1.3.0 python docs/chantiers/limites-asymptotes/generer_revue_matin.py

Le rendu reproduit commun/rendu.js (mêmes classes, même feuille de style commun/style.css, copiée dans la page) ; les formules sont composées
par KaTeX (CDN)."""
import html
import os
import re
import sys

RACINE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, os.path.join(RACINE, "tests", "python"))
sys.path.insert(0, os.path.join(RACINE, "tests", "python", "donnees"))
from moteurs import ensemble_def  # noqa: E402,F401
import limites_asymptotes as la  # noqa: E402
import redaction_bh as rb  # noqa: E402
from corpus_limites_3m import CAS, PAS_PRIS_EN_CHARGE  # noqa: E402

INF = r"x \to +\infty"
MINF = r"x \to -\infty"
# (id, saisie, borne, rang de la rédaction dans la borne)
EXERCICES = [
    ("8.11a", "e^x/ln(x)", INF, 0), ("8.11b", "x^3*ln(x)", r"x \to 0^+", 0), ("8.11c", "x^2*e^x", MINF, 0), ("8.11d", "x^2*e^(-5x)", INF, 0),
    ("Ex5a", "x^2*e^(-x)", INF, 0), ("Ex5b", "x*e^(1/x)", r"x \to 0", 1), ("Ex5c", "e^(-x)/x^2", MINF, 0), ("Ex5d", "e^(-x)/(4x)", INF, 0),
    ("8.12a", "ln(x)/e^(2x)", INF, 0), ("8.12b", "e^(-x)*ln(x^3)", INF, 0), ("8.12c", "e^(-x)*x", MINF, 0), ("8.12d", "e^x*ln(-x)", MINF, 0),
    ("8.12e", "x^3*e^(3x-5)", MINF, 0), ("8.12f", "e^(1/x)/x^2", r"x \to 0", 0), ("8.12g", "e^(1/x)*x^2", r"x \to 0", 1),
    ("8.12h", "e^(-1/x)/x", r"x \to 0", 1), ("Ex6", "e^((3x+4)/(x-2))", INF, 0), ("8.13a", "e^(-x)", INF, 0),
    ("8.13b", "e^((x^2-3x+2)/(2x^2))", INF, 0), ("8.13c", "e^(-2x/(x^2-5))", INF, 0), ("8.13d", "e^((3x^2+2)/(2x))", MINF, 0),
    ("8.13e", "ln((3x^2-3x+2)/(x^2-5x+2))", INF, 0), ("8.13f", "ln(1/x)", INF, 0), ("8.14", "ln(1+e^x)/e^x", MINF, 0),
]
ECARTS = {
    "8.11a": "« on remplace » au lieu de « on remplace à nouveau » (étape 4).",
    "Ex5a": "Deux étapes BH détaillées (comme 8.11 c) ; le corrigé les condense en une seule ligne « BH deux fois ».",
    "8.12d": "« BH » puis « on simplifie » en deux étapes ; le corrigé : « BH et simplification » ; forme finale −1/(x e^(−x)) au lieu de 1/((−x)e^(−x)).",
    "8.12e": "Pas d'écart de structure.",
    "8.12f": "Seul le côté 0⁺ du corrigé est rédigé en descente ; l'autre côté (0⁻) garde l'ancienne rédaction ou le repli.",
    "8.12g": "La citation de l'exemple 5 b) devient « On calcule à part… » avec le sous-calcul complet (R1) ; l'encadré « Autre méthode » n'est pas produit.",
    "8.12b": "Pas d'écart de structure.",
    "8.14": "« BH et simplification » en deux étapes ; la partie (a) devient l'étape « on remplace » ; le tableau de valeurs précède le calcul.",
    "8.13a": "Une seule carte « on remplace » (pas de prédiction) comme le corrigé.",
    "8.13f": "L'« Autre façon : ln(1/x) = −ln(x) » n'est pas produite.",
    "8.11b": "Pas d'écart de structure ; la remarque sur le graphe de ln en 0⁺ n'est pas produite.",
}
SPEC = os.path.join(RACINE, "docs", "specifications", "redaction-limites-3m.md")
CSS = open(os.path.join(RACINE, "commun", "style.css"), encoding="utf-8").read()


# ---------------------------------------------------------------------------------------------------------------------
def transcriptions():
    """{id: (titre, [lignes markdown])} lu dans la section 3 de la spécification."""
    sec, out, cle = None, {}, None
    for ligne in open(SPEC, encoding="utf-8").read().split("\n"):
        m = re.match(r"### (Exercice|Exemple) ([\d.]+)", ligne)
        if m:
            sec = ("Ex" + m.group(2)) if m.group(1) == "Exemple" else m.group(2)
            cle = None
            if sec == "8.14":
                cle = "8.14"
                out[cle] = ("8.14", [])
            continue
        m = re.match(r"\*\*([a-h])\) (.*)\*\*$", ligne)
        if m and sec:
            cle = sec + m.group(1) if sec != "Ex6" else sec
            out[cle] = (m.group(2), [])
            continue
        if sec == "Ex6" and ligne.startswith("**lim"):
            cle = "Ex6"
            out[cle] = (ligne.strip("*"), [])
            continue
        if ligne.startswith("## "):
            cle = None
        if cle and ligne.strip():
            out[cle][1].append(ligne)
    return out


def md(ligne):
    t = html.escape(ligne.strip())
    t = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", t)
    t = re.sub(r"_(.+?)_", r"<i>\1</i>", t)
    return t


def transcription_html(lignes):
    out, ouvert = [], False
    for l in lignes:
        if l.startswith("- "):
            if not ouvert:
                out.append("<ul>")
                ouvert = True
            out.append("<li>" + md(l[2:]) + "</li>")
        else:
            if ouvert:
                out.append("</ul>")
                ouvert = False
            out.append("<p>" + md(l) + "</p>")
    if ouvert:
        out.append("</ul>")
    return "\n".join(out)


def titres_corrige(lignes):
    return [m.group(1) for l in lignes for m in [re.match(r"- E\d+ \[(.*?)\]", l)] if m]


SYNONYMES = {"quotient": "on transforme le produit en quotient", "on transforme en quotient": "on transforme le produit en quotient",
             "on remplace à nouveau": "on remplace", "exponentielle": "on applique l'exponentielle", "logarithme": "on applique le logarithme",
             "limite de l'exposant": "limite de l'exposant, à part", "la forme": "on vérifie la forme", "bh et simplification": "bh|on simplifie",
             "bh deux fois": "bh|bh", "on conclut directement": "on conclut directement"}


def normaliser(titres):
    """Titres comparables : sans numéro de BH, synonymes du corrigé ramenés au vocabulaire de l'outil."""
    out = []
    for t in titres:
        t = re.sub(r" \(\d\w* fois\)", "", t.strip().rstrip(".").lower())
        t = SYNONYMES.get(t, t)
        out += t.split("|")
    return [t for t in out if not t.startswith("les dérivées")]


# ---------------------------------------------------------------------------------------------------------------------
# Rendu des blocs (miroir de commun/rendu.js)
# ---------------------------------------------------------------------------------------------------------------------
def K(t):
    return "\\(" + t + "\\)"


def rendre_bloc(b):
    t = b["type"]
    if t == "texte":
        st = b.get("style", "etape")
        classe = {"etape": "etape", "discret": "muted", "indice": "hint", "confirme": "confirme"}[st]
        return f'<div class="{classe}">{b["html"]}</div>'
    if t == "bh":
        return ('<div class="bh"><table><tr><td>haut : ' + K(b["haut"]) + "</td><td>" + K("\\longrightarrow") + "</td><td>dérivée : " + K(b["dhaut"])
                + "</td></tr><tr><td>bas : " + K(b["bas"]) + "</td><td>" + K("\\longrightarrow") + "</td><td>dérivée : " + K(b["dbas"]) + "</td></tr></table></div>")
    if t == "encadre":
        return (f'<div class="enc enc-{b["genre"]}"><div class="enc-t">{b["titre"]}</div><div class="enc-c">'
                + "".join(f"<p>{l}</p>" for l in b["lignes"]) + "</div></div>")
    if t == "resultat_lim":
        return f'<div class="rbox">{K(b["tex"])}</div>'
    if t == "valeurs":
        return ('<div class="vals"><table><tr><td>' + K("x") + "</td>" + "".join(f"<td>{K(x)}</td>" for x in b["xs"]) + "</tr><tr><td>"
                + K(b["expr"]) + "</td>" + "".join(f"<td>{K(v)}</td>" for v in b["fs"]) + "</tr></table></div>")
    if t == "sous_calcul":
        return (f'<div class="sous"><div class="sous-t">{b["titre"]}</div>'
                + "".join(f'<div class="sous-e">Étape {i} : {e["titre"]}.</div>' + "".join(rendre_bloc(x) for x in e["blocs"])
                          for i, e in enumerate(b["etapes"], 1)) + "</div>")
    return f'<div class="etape">[{t}]</div>'


def rendre_descente(d, enonce):
    cartes = [f'<div class="card"><div class="etape">\\[{enonce}\\]</div></div>']
    for i, e in enumerate(d["etapes"], 1):
        cartes.append(f'<div class="card"><h3 style="margin:0 0 10px">Étape {i} : {e["titre"]}.</h3>' + "".join(rendre_bloc(b) for b in e["blocs"]) + "</div>")
    return "\n".join(cartes)


def statut_borne(item):
    if item.get("type") == "descente":
        return "nouvelle"
    return "repli" if "n'est pas rédigé ici" in item.get("html", "") else "ancienne"


# ---------------------------------------------------------------------------------------------------------------------
def main():
    trans = transcriptions()
    lignes_tab, sections = [], []
    for id_, saisie, ou, rang in EXERCICES:
        r = la.etudier(saisie)
        etude = [e for e in r["etudes"] if e["ou"] == ou]
        items = [i for e in etude for i in e["etapes"] if i.get("type") != "tableau" and not i.get("html", "").startswith(("Asymptote", "Limite finie"))]
        descentes = [i for i in items if i.get("type") == "descente"]
        titre_c, lig = trans.get(id_, ("", []))
        corrige = titres_corrige(lig)
        if len(descentes) > rang:
            d = descentes[rang]
            mine = [e["titre"] for e in d["etapes"]]
            statut = "nouvelle"
            auto = "" if not corrige or normaliser(mine) == normaliser(corrige) else \
                "Titres : outil " + " → ".join(mine) + " / corrigé " + " → ".join(corrige) + "."
            rendu = rendre_descente(d, d["enonce_tex"])
            alertes = d["alertes"]
        else:
            d, statut, rendu, alertes = None, "ancienne / repli", '<div class="card"><div class="etape">Pas de rédaction descendante pour cette borne.</div></div>', []
            mine, auto = [], ""
            statut = statut_borne(items[0]) if items else "absente"
        ecart = (ECARTS.get(id_, "") + " " + (auto if id_ not in ECARTS else "")).strip() or "—"
        css = {"nouvelle": "ok", "ancienne": "warn", "repli": "bad"}.get(statut, "warn")
        lignes_tab.append(f'<tr><td><a href="#{id_}">{id_}</a></td><td>{html.escape(saisie)}</td><td>{K(ou)}</td>'
                          f'<td class="{css}">{statut}</td><td>{html.escape(ecart)}</td></tr>')
        sections.append(f'<section id="{id_}"><h2>{id_} — {html.escape(saisie)} <small>({K(ou)}) · {statut}</small></h2>'
                        f'<div class="deux"><div class="col"><h3>Rédaction de l\'outil</h3>{rendu}</div>'
                        f'<div class="col"><h3>Corrigé (transcription)</h3><div class="card trans">{transcription_html(lig)}</div>'
                        f'<p class="ecarts"><b>Écarts :</b> {html.escape(ecart)}'
                        + (f' <b class="bad">Alertes : {html.escape(str(alertes))}</b>' if alertes else "") + "</p></div></div></section>")
    # --- le reste du corpus ---
    bilan = {}
    for c in CAS:
        if c.id in PAS_PRIS_EN_CHARGE or c.saisie in bilan:
            continue
        r = la.etudier(c.saisie)
        n = {"nouvelle": 0, "ancienne": 0, "repli": 0}
        for e in r["etudes"]:
            for i in e["etapes"]:
                if i.get("type") == "descente" or (i.get("type") == "texte" and i.get("html", "").startswith(("\\[", "Le calcul détaillé"))):
                    n[statut_borne(i)] += 1
        bilan[c.saisie] = (c.id, n)
    tab2 = "".join(f"<tr><td>{i}</td><td>{html.escape(s)}</td><td>{n['nouvelle']}</td><td>{n['ancienne']}</td><td>{n['repli']}</td></tr>"
                   for s, (i, n) in bilan.items())
    tot = [sum(n[k] for _, n in bilan.values()) for k in ("nouvelle", "ancienne", "repli")]
    page = f"""<!DOCTYPE html>
<html lang="fr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Revue du matin — rédaction des limites</title>
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/katex.min.css">
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/katex.min.js"></script>
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/contrib/auto-render.min.js"
  onload="renderMathInElement(document.body,{{delimiters:[{{left:'\\\\(',right:'\\\\)',display:false}},{{left:'\\\\[',right:'\\\\]',display:true}}],throwOnError:false,strict:'ignore'}})"></script>
<style>
{CSS}
body{{background:var(--bg);color:var(--fg);font-family:system-ui,sans-serif;margin:0;padding:16px}}
.wrap{{max-width:1300px;margin:0 auto}} .card{{background:var(--card);border:1px solid var(--border);border-radius:10px;padding:14px 18px;margin:10px 0}}
table.recap{{border-collapse:collapse;width:100%;font-size:.92rem}} table.recap td,table.recap th{{border:1px solid var(--border);padding:4px 8px;text-align:left;vertical-align:top}}
.ok{{color:var(--good);font-weight:700}} .warn{{color:var(--autre);font-weight:700}} .bad{{color:var(--bad);font-weight:700}}
.deux{{display:grid;grid-template-columns:1fr 1fr;gap:16px}} @media(max-width:900px){{.deux{{grid-template-columns:1fr}}}}
.col{{min-width:0}} .trans{{font-size:.92rem}} .trans p{{margin:.3em 0}} section{{margin:28px 0;border-top:2px solid var(--border);padding-top:8px}}
.ecarts{{font-size:.9rem}} small{{color:var(--muted);font-weight:400}}
</style></head><body><div class="wrap">
<h1>Revue du matin — rédaction des limites (3M)</h1>
<p>Branche <code>refonte-redaction-3m</code>. Chaque section : à gauche la rédaction produite par l'outil (rendu réel, cartes dépliées), à droite la
transcription du corrigé et les écarts. Suivi : <code>docs/chantiers/limites-asymptotes/suivi-refonte.md</code> ; décisions à valider :
<code>docs/a-valider.md</code>.</p>
<h2>Tableau récapitulatif</h2>
<table class="recap"><tr><th>Exercice</th><th>Saisie</th><th>Borne</th><th>Rédaction</th><th>Écarts</th></tr>
{''.join(lignes_tab)}</table>
<h2>Le reste du corpus (par saisie : nombre de bornes en rédaction nouvelle / ancienne / repli)</h2>
<p>Total : <b class="ok">{tot[0]} nouvelles</b>, <b class="warn">{tot[1]} anciennes</b>, <b class="bad">{tot[2]} replis</b>.</p>
<table class="recap"><tr><th>Id</th><th>Saisie</th><th>Nouvelle</th><th>Ancienne</th><th>Repli</th></tr>{tab2}</table>
{''.join(sections)}
</div></body></html>"""
    chemin = os.path.join(os.path.dirname(__file__), "revue-matin.html")
    with open(chemin, "w", encoding="utf-8") as f:
        f.write(page)
    print(chemin, len(page) // 1024, "Ko")


if __name__ == "__main__":
    main()
