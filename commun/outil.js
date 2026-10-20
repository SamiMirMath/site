/* Page outil générique (T16) : monte le comportement commun sur le HTML statique d'une page.

   La page garde son HTML (titre, accroche, saisie, clavier, « Rappel de la méthode », zone #resultat)
   et ses `id` ; elle passe sa config :

     import { monterOutil } from "../commun/outil.js";
     const EXEMPLES = [...]; const EXOS = {...};        // restent déclarés ainsi (tests/python/cas.py les lit)
     monterOutil({ outil: "ensemble-definition", titrePdf: "Corrige-ensemble-de-definition",
                   exemples: EXEMPLES, exos: EXOS, poids: [["facile", .35], ...], apres: async (ctx) => {...} });

   Options : prefixe (« f(x) = », devant l'aperçu), sympyAvant (attendre SymPy avant tout calcul),
   delaiCalcul (ms, 30000 par défaut : au-delà, « Calcul trop long » et le moteur est relancé),
   greffons (blocs à comportement, voir rendu.js ajouterGreffon : le graphique de commun/graphique.js ; ils reçoivent
   { appelPy, entree } où `entree` est la saisie dont la carte est le corrigé),
   apres({entree, appelPy, derniereCarte, actuel}) appelé après l'affichage d'un corrigé réussi
   (`actuel()` devient faux si un autre calcul a commencé).

   Les textes d'interface (états, compteur d'étapes, messages de délai) sont écrits ici une seule fois.
   Les textes du corrigé viennent de `resoudre()` (Python) et sont rendus par commun/rendu.js.
   Test : `window.__delaiCalcul` (ms) remplace le délai de 30 s. */
import { MoteurPython } from "./moteur-python.js";
import { K, math, ajouterGreffon, rendreCarte, rendreErreur } from "./rendu.js";

const $ = id => document.getElementById(id);
const PAUSE_ERREUR = 500;
const DELAI_CALCUL = 30000;      // par défaut ; la config peut le changer (delaiCalcul)

export function monterOutil(config) {
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", () => demarrerOutil(config));
  else demarrerOutil(config);
}

function demarrerOutil(config) {
  const { outil, prefixe = "f(x) = ", titrePdf, exemples = [], exos = {}, poids = [], sympyAvant = false, delaiCalcul = DELAI_CALCUL, greffons = [], apres } = config;
  greffons.forEach(ajouterGreffon);
  const moteur = new MoteurPython(outil, { surEtat: () => majEtat() });
  const appelPy = (fn, arg, delai) => moteur.appelPy(fn, arg, delai);
  let cartes = [], visibles = 0, numCalcul = 0;

  function majEtat() { $("etat").textContent = moteur.sympyOK ? "Prêt." : "Chargement du moteur de calcul…"; }

  async function demarrer() {
    try {
      await moteur.demarrer();
      majEtat();
      $("calculer").disabled = false;
      if ($("exoHasard")) $("exoHasard").disabled = false;
      apercu();
      const q = new URLSearchParams(location.search).get("f");
      if (q) { $("entree").value = q; calculer(); }
    } catch (e) {
      console.error(e);
      $("etat").innerHTML = '<span class="err">Impossible de charger l\'outil de calcul.</span> Vérifiez votre connexion internet, puis rechargez la page.';
    }
  }

  /* ---------- saisie ---------- */
  /* Aperçu de la saisie : jamais de message d'erreur rouge pendant la frappe. Dès qu'on tape, une erreur affichée
     est effacée (on garde le dernier aperçu valide, estompé). L'erreur n'est montrée qu'après une pause d'environ
     0,5 s sans frappe, et seulement si la réponse correspond bien à la dernière saisie ; un aperçu valide s'affiche
     tout de suite et remplace tout message. Une réponse perdue (moteur occupé, délai dépassé) ne laisse rien d'obsolète. */
  let tAp = null, seqAp = 0, tFrappe = 0, dernierApercu = "";
  function apercu() {
    clearTimeout(tAp);
    const mon = ++seqAp, box = $("apercu");
    tFrappe = Date.now();
    const neutre = () => { box.innerHTML = dernierApercu ? '<span class="obsolete">' + dernierApercu + "</span>" : '<span class="muted">Aperçu de la fonction</span>'; };
    if (box.querySelector(".err")) neutre();
    tAp = setTimeout(async () => {
      const s = $("entree").value.trim();
      if (!s) { dernierApercu = ""; box.innerHTML = '<span class="muted">Aperçu de la fonction</span>'; return; }
      if (!moteur.worker) return;
      let r;
      try { r = await appelPy("apercu", s, 5000); } catch (e) { if (mon === seqAp && box.querySelector(".err")) neutre(); return; }
      if (mon !== seqAp) return;                        // une saisie plus récente est en cours
      if (r.ok) { dernierApercu = K(prefixe + r.tex); box.innerHTML = dernierApercu; return; }
      const reste = PAUSE_ERREUR - (Date.now() - tFrappe);
      if (reste > 0) await new Promise(ok => setTimeout(ok, reste));
      if (mon !== seqAp) return;
      box.innerHTML = '<span class="err">' + r.erreur + "</span>";
    }, 150);
  }
  $("entree").addEventListener("input", apercu);
  $("entree").addEventListener("keydown", e => { if (e.key === "Enter" && !$("calculer").disabled) calculer(); });
  $("clavier").addEventListener("click", e => {
    const b = e.target.closest("button");
    if (!b) return;
    const inp = $("entree");
    const a = inp.selectionStart ?? inp.value.length, z = inp.selectionEnd ?? a;
    if (b.dataset.k === "clear") { inp.value = ""; }
    else if (b.dataset.k === "back") {
      if (a !== z) inp.value = inp.value.slice(0, a) + inp.value.slice(z);
      else if (a > 0) { inp.value = inp.value.slice(0, a - 1) + inp.value.slice(a); inp.setSelectionRange(a - 1, a - 1); }
    } else { const t = b.dataset.t; inp.value = inp.value.slice(0, a) + t + inp.value.slice(z); inp.setSelectionRange(a + t.length, a + t.length); }
    apercu();
  });
  $("exemples").innerHTML = '<span class="hint" style="align-self:center">Exemples :</span>' + exemples.map(s => `<button data-ex="${s}">${s}</button>`).join("");
  $("exemples").addEventListener("click", e => {
    const b = e.target.closest("button");
    if (!b) return;
    $("entree").value = b.dataset.ex;
    apercu();
    if (!$("calculer").disabled) calculer();
  });
  $("calculer").onclick = () => calculer();

  /* ---------- calcul et affichage ---------- */
  async function calculer(force) {
    const s = (typeof force === "string" ? force : $("entree").value).trim();
    if (!s || !moteur.worker) return;
    const moi = ++numCalcul;
    $("calculer").disabled = true;
    $("etat").textContent = "Calcul en cours…";
    const delai = window.__delaiCalcul || delaiCalcul;
    let r;
    try {
      if (sympyAvant) await moteur.sympyPret;
      r = await appelPy("resoudre", s, delai);
      if (r.besoin_sympy) {
        $("etat").textContent = "Chargement du moteur de calcul pour cette fonction…";
        await moteur.sympyPret;
        if (moteur.sympyOK) r = await appelPy("resoudre", s, delai);
      }
    } catch (e) {
      if (e.message === "delai") { $("etat").textContent = "Calcul trop long : le calcul a été relancé."; moteur.relancer(); }
      r = { ok: false, erreur: e.message === "delai" ? `Le calcul a pris trop de temps (plus de ${delaiCalcul / 1000} s). Essayez une écriture plus simple.` : (console.error(e), "Une erreur s'est produite : réessayez ou simplifiez l'écriture.") };
    }
    $("calculer").disabled = false;
    majEtat();
    if (moi !== numCalcul) return;
    afficher(r, s);
    if (r.ok && apres) {
      try { await apres({ entree: s, appelPy, derniereCarte: () => cartes[cartes.length - 1], actuel: () => moi === numCalcul }); } catch (e) { /* le contrôle est facultatif */ }
    }
  }

  function afficher(r, entree) {
    $("resultat").hidden = false;
    const box = $("cartes");
    box.innerHTML = "";
    cartes = [];
    if (!r.ok) {
      box.appendChild(rendreErreur(r));
      $("suivant").disabled = $("tout").disabled = true;
      $("progression").textContent = "";
      return;
    }
    const contexte = { appelPy, entree };
    if (r.entete) box.appendChild(rendreCarte(r.entete, contexte));       // toujours visible, hors du compteur d'étapes
    cartes = r.cartes.map(c => rendreCarte(c, contexte));
    cartes.forEach(c => { c.classList.add("cache"); box.appendChild(c); });
    visibles = 0;
    montrer(1);
  }

  function montrer(n) {
    visibles = Math.min(cartes.length, visibles + n);
    cartes.forEach((c, i) => c.classList.toggle("cache", i >= visibles));
    $("suivant").disabled = $("tout").disabled = visibles >= cartes.length;
    $("progression").textContent = `Étape ${visibles} / ${cartes.length}`;
    const der = cartes[visibles - 1];
    if (der && n === 1) der.scrollIntoView({ behavior: "smooth", block: "nearest" });
  }
  $("suivant").onclick = () => montrer(1);
  $("tout").onclick = () => montrer(cartes.length);
  const titreOrigine = document.title;
  window.addEventListener("afterprint", () => { document.title = titreOrigine; });
  $("pdf").onclick = () => {
    montrer(cartes.length);
    document.title = titrePdf;
    window.print();
  };

  /* ---------- exercice au hasard (tirage JS par niveaux, jusqu'à T13) ---------- */
  function tirerNiveau() {
    let r = Math.random(), acc = 0;
    for (const [n, p] of poids) { acc += p; if (r <= acc) return n; }
    return poids.length ? poids[0][0] : null;
  }
  let exoCourant = null;
  async function nouvelExercice() {
    if (!moteur.worker) return;
    let s;
    do { const pool = exos[tirerNiveau()]; s = pool[Math.floor(Math.random() * pool.length)]; } while (s === exoCourant);
    exoCourant = s;
    $("resultat").hidden = true;
    $("cartes").innerHTML = "";
    cartes = [];
    $("exoCorrige").hidden = false;
    $("exoCorrige").textContent = "Afficher le corrigé ▶";
    const box = $("exoEnonce");
    box.innerHTML = '<span class="muted">Chargement…</span>';
    try {
      const r = await appelPy("apercu", s, 5000);
      box.innerHTML = r.ok ? K(prefixe + r.tex) : '<span class="err">' + r.erreur + "</span>";
    } catch (e) { box.innerHTML = '<span class="err">Erreur de chargement.</span>'; }
    math(box);
  }
  if ($("exoHasard")) $("exoHasard").onclick = nouvelExercice;
  if ($("exoCorrige")) {
    $("exoCorrige").onclick = async () => {
      if (!exoCourant) return;
      await calculer(exoCourant);
      $("resultat").scrollIntoView({ behavior: "smooth", block: "start" });
    };
  }

  document.querySelectorAll("details").forEach(math);
  demarrer();
}
