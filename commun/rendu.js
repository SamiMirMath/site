/* Rendu commun du format de sortie des outils (T16) : une carte de moteur/sortie.py devient du HTML.

   Aucun texte de corrigé n'est composé ici : tout vient de `resoudre()` (Python). Ce module ne fait que
   choisir les classes CSS (commun/style.css) et dessiner les tableaux de signes.

   Règles de rendu (une seule fois, ici) :
     carte      classes « card » ; + « cond » si elle a un badge ; + « final » si style « final ».
                style « erreur » : « card err » avec le seul message (pas de titre).
                titre : <h3>titre<span class="badge">badge</span></h3> (titre_tex en formule) ;
                sans badge, <h3> simple ; titre_masque : aucun titre affiché.
     texte      style etape (défaut) → .etape ; discret → .muted ; indice → .hint
     formule    carte sans titre affiché → .enonce ; sinon → .c (cadre grisé)
     resultat   .res
     erreur     .res.err ; dans une carte « final » → .err (le .res y est vert)
     liste      <ul class="extrema|bilan">
     tableau    tableau de signes ou de variations (voir cellule())
   Un bloc de type inconnu n'est pas affiché (message dans la console), jamais une exception.
   `ajouterBloc(type, fn)` enregistre un rendu supplémentaire (le graphique, en T19). */

const DELIMITEURS = [{ left: "\\(", right: "\\)", display: false }, { left: "\\[", right: "\\]", display: true }];

export function K(tex) {
  try { return katex.renderToString(tex, { throwOnError: false, strict: "ignore" }); } catch (e) { return tex; }
}

export function math(el) {
  if (window.renderMathInElement) renderMathInElement(el, { delimiters: DELIMITEURS, throwOnError: false, strict: "ignore" });
}

/* Valeur d'une limite : « ? » telle quelle, sinon une formule ; rien si elle est absente. */
function valeurLimite(v) {
  return v == null ? "" : v === "?" ? "?" : K(v);
}

/* Colonne interdite avec limites (tableau.limites.colonnes) : limite à gauche et à droite du trait. Chaque moitié
   contient aussi, invisible, la valeur de l'autre (`i`) pour que les deux moitiés aient la même largeur et que le trait
   reste centré. */
function celluleLimites(c) {
  const g = valeurLimite(c.gauche), d = valeurLimite(c.droite);
  return `<td class="vi"><div class="lm"><span class="lg">${g}<i aria-hidden="true">${d}</i></span>` +
    `<span class="ld">${d}<i aria-hidden="true">${g}</i></span></div></td>`;
}

function cellule(s, j, limites) {
  if (s === "asym" && limites[j]) return celluleLimites(limites[j]);
  if (s === "+") return '<td class="p">+</td>';
  if (s === "-") return '<td class="m">−</td>';
  if (s === "||" || s === "asym") return '<td class="vi"></td>';
  if (s === "|") return '<td class="bar"></td>';
  if (s === "x") return '<td class="hors" aria-label="hors de l\'ensemble de définition"></td>';
  if (s === "\\nearrow" || s === "\\searrow" || s === "\\rightarrow") return `<td>${K(s)}</td>`;
  if (s.startsWith("val:")) return `<td class="pt">${K(s.slice(4))}</td>`;
  if (s === "extremum") return '<td class="pt">•</td>';
  return `<td>${s}</td>`;
}

/* Tableau de signes ou de variations. `limites` (Étude complète seulement) : valeurs en ±∞ dans les cases du bord de la
   ligne de variation, et des deux côtés d'une colonne interdite (case « asym »). */
export function rendreTableau(t) {
  const lim = t.limites || null;
  const parColonne = {};
  ((lim && lim.colonnes) || []).forEach(c => { parColonne[c.j] = c; });
  let h = '<div class="tsigne"><table><tr><td class="lab">' + K(t.var) + "</td><td>" + K("-\\infty") + "</td>";
  for (const c of t.crit) h += "<td></td><td>" + K(c) + "</td>";
  h += "<td></td><td>" + K("+\\infty") + "</td></tr>";
  for (const r of t.rows) {
    const classe = r.final ? "final" : r.variation ? "variation" : "";
    const bord = v => `<td>${r.variation && lim ? valeurLimite(v) : ""}</td>`;
    h += `<tr class="${classe}"><td class="lab">${K(r.label)}</td>${bord(lim && lim.moins_inf)}` +
      r.cells.map((c, j) => cellule(c, j, parColonne)).join("") + bord(lim && lim.plus_inf) + "</tr>";
  }
  return h + "</table></div>";
}

const STYLE_TEXTE = {
  etape: h => `<div class="etape">${h}</div>`,
  discret: h => `<div class="muted" style="margin-top:4px">${h}</div>`,
  indice: h => `<div class="hint">${h}</div>`,
};

const BLOCS = {
  texte: b => {
    if (b.detail) console.error(b.detail);
    return STYLE_TEXTE[b.style || "etape"](b.html);
  },
  formule: (b, c) => `<div class="${c.titre_masque ? "enonce" : "c"}">${K(b.tex)}</div>`,
  resultat: b => `<div class="res">${K(b.tex)}</div>`,
  erreur: (b, c) => `<div class="${c.style === "final" ? "err" : "res err"}">${b.texte}</div>`,
  liste: b => `<ul class="${b.style || ""}">` + b.items.map(i => `<li>${i}</li>`).join("") + "</ul>",
  tableau: b => rendreTableau(b),
};

export function ajouterBloc(type, fn) {
  BLOCS[type] = fn;
}

function titre(c) {
  if (c.titre_masque) return "";
  const t = c.titre_tex ? K(c.titre_tex) : c.titre;
  return c.badge ? `<h3>${t}<span class="badge">${c.badge}</span></h3>` : `<h3 style="margin:0 0 10px">${t}</h3>`;
}

export function rendreCarte(c) {
  const d = document.createElement("div");
  if (c.detail) console.error(c.detail);
  if (c.style === "erreur") {
    d.className = "card err";
    d.textContent = c.blocs.filter(b => b.type === "erreur").map(b => b.texte).join(" ");
    return d;
  }
  d.className = "card" + (c.badge ? " cond" : "") + (c.style === "final" ? " final" : "");
  let h = titre(c);
  for (const b of c.blocs) {
    const fn = BLOCS[b.type];
    if (fn) h += fn(b, c);
    else console.error("bloc non affiché : type inconnu « " + b.type + " »");
  }
  d.innerHTML = h;
  math(d);
  return d;
}

/** Sortie ok:false d'un moteur : le message seul, dans une carte d'erreur. */
export function rendreErreur(sortie) {
  const d = document.createElement("div");
  d.className = "card err";
  d.textContent = sortie.erreur;
  if (sortie.detail) console.error(sortie.detail);
  return d;
}
