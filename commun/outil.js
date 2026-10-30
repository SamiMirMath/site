/* Page outil générique : monte le comportement commun sur le HTML statique d'une page.

   La page garde son HTML (titre, accroche, saisie, clavier, « Rappel de la méthode », zone #resultat)
   et ses `id` ; elle passe sa config :

     import { monterOutil } from "../commun/outil.js";
     const EXEMPLES = [...]; const EXOS = {...};        // restent déclarés ainsi (tests/python/cas.py les lit)
     monterOutil({ outil: "ensemble-definition", titrePdf: "Corrige-ensemble-de-definition",
                   exemples: EXEMPLES, exos: EXOS, poids: [["facile", .35], ...], apres: async (ctx) => {...} });

   Options : prefixe (« f(x) = », devant l'aperçu et l'énoncé de l'exercice), prefixeExo (devant l'énoncé de l'exercice seulement,
   si différent : « Factoriser : »), exercicePython (nom de la fonction Python qui tire l'exercice d'un niveau, renvoie {ok, expr} ;
   sans elle, le tirage se fait en JS dans `exos`), sympyAvant (attendre SymPy avant tout calcul),
   delaiCalcul (ms, 30000 par défaut : au-delà, « Calcul trop long » et le moteur est relancé),
   greffons (blocs à comportement, voir rendu.js ajouterGreffon : le graphique de commun/graphique.js ; ils reçoivent
   { appelPy, entree } où `entree` est la saisie dont la carte est le corrigé),
   apres({entree, appelPy, derniereCarte, actuel}) appelé après l'affichage d'un corrigé réussi
   (`actuel()` devient faux si un autre calcul a commencé).

   Variantes de résolution : quand la sortie de `resoudre()` porte `variantes` ([{cle, libelle, cartes}]) et `variante_defaut`, le socle affiche
   au-dessus des cartes un bouton par variante (`#variantes`, créé ici, `aria-pressed`) ; un clic remplace les cartes sans appeler le moteur, en
   gardant le nombre de cartes visibles. Le choix est gardé d'une saisie à l'autre (mémoire de la page, et localStorage « variante:<outil> » dans un
   try/catch). Une ligne « Méthode : … » (`#methodeImprimee`) n'apparaît qu'à l'impression.

   Option (case à cocher) : quand la sortie porte `option` ({cle, libelle, cochee, cartes}), le socle affiche sous le sélecteur une case (`#option`, créée
   ici, `no-print`) ; cochée, les cartes de l'option s'ajoutent à la fin des cartes affichées, sans appel au moteur, en gardant le nombre de cartes
   visibles (toutes si toutes l'étaient). `cochee` est l'état de départ ; le choix de l'élève vaut pour l'équation affichée (mémoire de la page,
   gardé au changement de variante, oublié à la saisie suivante : le défaut dépend de l'équation). Une variante qui porte `option: false` n'a pas de case.

   Filières : l'option `filieres` ({ liste: [{ cle, libelle, poids }], param, parAccueil, surFiliere }) ajoute au-dessus de la page deux boutons côte à côte
   (3C / 2M, `#filiere`, `aria-pressed`, au clavier). La filière de départ est celle du paramètre d'URL `param` (« ?filiere=M »), sinon celle que l'accueil a
   mémorisée (`samimir-track` : `parAccueil` = { Ms: "M", Mr: "M" }), sinon la première de la liste. Changer de filière met l'URL à jour (history.replaceState),
   passe `[entrée, filière]` à `resoudre` et `[niveau, filière]` à `exercice`, tire les exercices avec les `poids` de la filière, recalcule l'équation affichée
   et appelle `surFiliere(cle)` (la page montre ou cache ce qui est propre à une filière). Les `exemples` peuvent être un tableau ou { cle: tableau }.
   Une ligne « Filière : … » n'apparaît qu'à l'impression. Sans l'option, rien ne change.

   Bouton flottant : un second « Étape suivante ▶ » (`#suivantFlottant`, créé ici, `no-print`) est fixé en bas à droite de l'écran, pour que l'élève n'ait pas
   à remonter à la barre d'outils. Il déclenche le même clic que `#suivant` (qui reste à sa place) et n'est visible que s'il reste des cartes à montrer.
   La place qu'il prend est réservée par commun/style.css (marge sous `#cartes`, `scroll-margin-bottom` des cartes).

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
  const { outil, prefixe = "f(x) = ", prefixeExo = prefixe, exercicePython = null, titrePdf, exemples = [], exos = {}, poids: poidsDeLaPage = [], sympyAvant = false, delaiCalcul = DELAI_CALCUL, greffons = [], apres, filieres = null } = config;
  let filiere = null, poids = poidsDeLaPage;                               // filière affichée (null : l'outil n'en a pas) et poids de tirage des niveaux
  greffons.forEach(ajouterGreffon);
  const moteur = new MoteurPython(outil, { surEtat: () => majEtat() });
  const appelPy = (fn, arg, delai) => moteur.appelPy(fn, arg, delai);
  let cartes = [], visibles = 0, numCalcul = 0;
  let sortie = null, entreeCourante = "", varianteChoisie = null;          // sortie affichée, saisie dont elle est le corrigé, choix de l'élève (mémoire de la page)
  let optionChoix = null, entreeOption = "";                              // état de la case choisi par l'élève (null : celui de la sortie), pour la saisie entreeOption

  /* ---------- bouton « Étape suivante » flottant ---------- */
  function creerBoutonFlottant() {
    const b = document.createElement("button");
    b.type = "button";
    b.id = "suivantFlottant";
    b.className = "primary flottant no-print";
    b.innerHTML = 'Étape suivante <span aria-hidden="true">▶</span>';
    b.hidden = true;
    b.onclick = () => $("suivant").click();                                    // exactement l'action du bouton de la barre
    document.body.appendChild(b);
    return b;
  }
  const flottant = creerBoutonFlottant();
  function majFlottant() { flottant.hidden = $("resultat").hidden || !cartes.length || visibles >= cartes.length; }

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
  const apercuVide = $("apercu").innerHTML;             // le texte d'attente (« Aperçu de la fonction », « du polynôme ») est celui de la page
  function apercu() {
    clearTimeout(tAp);
    const mon = ++seqAp, box = $("apercu");
    tFrappe = Date.now();
    const neutre = () => { box.innerHTML = dernierApercu ? '<span class="obsolete">' + dernierApercu + "</span>" : apercuVide; };
    if (box.querySelector(".err")) neutre();
    tAp = setTimeout(async () => {
      const s = $("entree").value.trim();
      if (!s) { dernierApercu = ""; box.innerHTML = apercuVide; return; }
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
  function afficherExemples() {
    const liste = Array.isArray(exemples) ? exemples : (exemples[filiere] || []);
    $("exemples").innerHTML = '<span class="hint" style="align-self:center">Exemples :</span>' + liste.map(s => `<button data-ex="${s}">${s}</button>`).join("");
  }
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
    // SymPy pas encore chargé : le calcul n'a pas commencé, on le dit (« Calcul en cours… » viendrait ensuite)
    const attendSympy = sympyAvant && !moteur.sympyOK;
    $("etat").textContent = attendSympy ? "Chargement du moteur de calcul pour cette fonction…" : "Calcul en cours…";
    const delai = window.__delaiCalcul || delaiCalcul;
    let r;
    try {
      if (attendSympy) { await moteur.sympyPret; $("etat").textContent = "Calcul en cours…"; }
      const arg = filiere ? [s, filiere] : s;
      r = await appelPy("resoudre", arg, delai);
      if (r.besoin_sympy) {
        $("etat").textContent = "Chargement du moteur de calcul pour cette fonction…";
        await moteur.sympyPret;
        if (moteur.sympyOK) r = await appelPy("resoudre", arg, delai);
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
    sortie = r;
    entreeCourante = entree;
    const barre = $("variantes");
    if (barre) barre.hidden = true;
    if (entree !== entreeOption) { optionChoix = null; entreeOption = entree; }          // une nouvelle équation reprend l'état de départ de la case
    if ($("option")) $("option").hidden = true;
    if (!r.ok) {
      const box = $("cartes");
      box.innerHTML = "";
      cartes = [];
      box.appendChild(rendreErreur(r));
      $("suivant").disabled = $("tout").disabled = true;
      $("progression").textContent = "";
      majFlottant();
      return;
    }
    if (r.variantes) barreVariantes(r);
    if (r.option) caseOption();
    poserCartes(1, true);
  }

  /* Les cartes de la sortie (ou de la variante choisie, avec les cartes de l'option si la case est cochée), `n` visibles. */
  function cartesDeLaSortie() {
    const base = sortie.variantes ? varianteAffichee(sortie).cartes : sortie.cartes;
    return optionCochee() ? base.concat(sortie.option.cartes) : base;
  }
  function poserCartes(n, defiler) {
    const box = $("cartes");
    box.innerHTML = "";
    const contexte = { appelPy, entree: entreeCourante };
    if (sortie.entete) box.appendChild(rendreCarte(sortie.entete, contexte));       // toujours visible, hors du compteur d'étapes
    cartes = cartesDeLaSortie().map(c => rendreCarte(c, contexte));
    cartes.forEach(c => { c.classList.add("cache"); box.appendChild(c); });
    visibles = 0;
    montrer(n, defiler);
  }

  /* ---------- variantes de résolution (sélecteur de méthode) ---------- */
  const cleStockage = "variante:" + outil;
  function varianteMemorisee() {
    if (varianteChoisie) return varianteChoisie;
    try { return localStorage.getItem(cleStockage); } catch (e) { return null; }       // stockage absent ou refusé : le défaut
  }
  function varianteAffichee(r) {
    const cle = varianteMemorisee();
    return r.variantes.find(v => v.cle === cle) || r.variantes.find(v => v.cle === r.variante_defaut) || r.variantes[0];
  }
  function barreVariantes(r) {
    let barre = $("variantes");
    if (!barre) {
      barre = document.createElement("div");
      barre.id = "variantes";
      $("resultat").insertBefore(barre, $("resultat").firstChild);
      const imprimee = document.createElement("div");
      imprimee.id = "methodeImprimee";
      imprimee.className = "imprime-seulement";
      $("resultat").insertBefore(imprimee, $("cartes"));
    }
    barre.className = "variantes no-print";
    barre.setAttribute("role", "group");
    barre.setAttribute("aria-label", "Méthode de résolution");
    barre.hidden = false;
    barre.innerHTML = "";
    for (const v of r.variantes) {
      const b = document.createElement("button");
      b.type = "button";
      b.dataset.variante = v.cle;
      b.textContent = v.libelle;
      b.onclick = () => choisirVariante(v.cle);
      barre.appendChild(b);
    }
    marquerVariante(varianteAffichee(r));
  }
  function marquerVariante(v) {
    document.querySelectorAll("#variantes button").forEach(b => b.setAttribute("aria-pressed", String(b.dataset.variante === v.cle)));
    $("methodeImprimee").textContent = "Méthode : " + v.libelle;
  }
  function choisirVariante(cle) {
    if (!sortie || !sortie.variantes) return;
    const v = sortie.variantes.find(x => x.cle === cle);
    if (!v || v === varianteAffichee(sortie)) return;
    varianteChoisie = cle;
    try { localStorage.setItem(cleStockage, cle); } catch (e) { /* le choix reste en mémoire pour cette page */ }
    marquerVariante(v);
    majOption();                                      // la case suit la variante (une méthode qui ne conclut pas n'a pas d'interprétation)
    const toutAffiche = visibles >= cartes.length, total = cartesDeLaSortie().length;
    poserCartes(toutAffiche ? total : Math.min(Math.max(visibles, 1), total), false);       // pas de défilement : l'élève reste où il est
  }

  /* ---------- option (case à cocher) ---------- */
  function optionDisponible() {
    return !!sortie && !!sortie.option && !(sortie.variantes && varianteAffichee(sortie).option === false);
  }
  function optionCochee() {
    return optionDisponible() && (optionChoix === null ? sortie.option.cochee : optionChoix);
  }
  function majOption() {
    const lab = $("option");
    if (!lab) return;
    lab.hidden = !optionDisponible();
    if (!lab.hidden) {
      lab.querySelector("input").checked = optionCochee();
      lab.querySelector("span").textContent = sortie.option.libelle;
    }
  }
  function caseOption() {
    if (!$("option")) {
      const lab = document.createElement("label"), coche = document.createElement("input"), texte = document.createElement("span");
      lab.id = "option";
      lab.className = "option no-print";
      coche.type = "checkbox";
      lab.append(coche, texte);
      if ($("variantes")) $("variantes").after(lab); else $("resultat").prepend(lab);
      coche.addEventListener("change", () => basculerOption(coche.checked));
    }
    majOption();
  }
  function basculerOption(coche) {
    if (!sortie || !optionDisponible()) return;
    optionChoix = coche;
    const toutAffiche = visibles >= cartes.length, total = cartesDeLaSortie().length;
    poserCartes(toutAffiche ? total : Math.min(Math.max(visibles, 1), total), toutAffiche && coche);       // cochée avec tout affiché : la carte ajoutée est montrée
  }

  function montrer(n, defiler = n === 1) {
    visibles = Math.min(cartes.length, visibles + n);
    cartes.forEach((c, i) => c.classList.toggle("cache", i >= visibles));
    $("suivant").disabled = $("tout").disabled = visibles >= cartes.length;
    $("progression").textContent = `Étape ${visibles} / ${cartes.length}`;
    majFlottant();
    const der = cartes[visibles - 1];
    if (der && defiler) der.scrollIntoView({ behavior: "smooth", block: "nearest" });
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

  /* ---------- exercice au hasard (tirage par niveaux : en JS dans `exos`, ou en Python avec `exercicePython`) ---------- */
  function tirerNiveau() {
    let r = Math.random(), acc = 0;
    for (const [n, p] of poids) { acc += p; if (r <= acc) return n; }
    return poids.length ? poids[0][0] : null;
  }
  let exoCourant = null;
  const exoVide = $("exoEnonce") ? $("exoEnonce").innerHTML : "";                // le texte d'attente de la carte « Exercice au hasard »
  async function nouvelExercice() {
    if (!moteur.worker) return;
    $("resultat").hidden = true;
    $("cartes").innerHTML = "";
    cartes = [];
    majFlottant();
    $("exoCorrige").hidden = false;
    $("exoCorrige").textContent = "Afficher le corrigé ▶";
    const box = $("exoEnonce");
    box.innerHTML = '<span class="muted">Chargement…</span>';
    try {
      let s;
      do {
        if (exercicePython) s = (await appelPy(exercicePython, filiere ? [tirerNiveau(), filiere] : tirerNiveau(), 5000)).expr;
        else { const pool = exos[tirerNiveau()]; s = pool[Math.floor(Math.random() * pool.length)]; }
      } while (s === exoCourant);
      exoCourant = s;
      const r = await appelPy("apercu", s, 5000);
      box.innerHTML = r.ok ? K(prefixeExo + r.tex) : '<span class="err">' + r.erreur + "</span>";
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

  /* ---------- filières (3C / 2M) ---------- */
  function filiereDeDepart() {
    const cles = filieres.liste.map(f => f.cle);
    const demandee = new URLSearchParams(location.search).get(filieres.param || "filiere");
    if (demandee && cles.includes(demandee)) return demandee;
    try {
      const accueil = localStorage.getItem("samimir-track");                       // C, Ms, Mr ou tous : choisie sur l'accueil
      const cle = filieres.parAccueil && filieres.parAccueil[accueil];
      if (cle && cles.includes(cle)) return cle;
    } catch (e) { /* stockage absent ou refusé */ }
    return filieres.liste[0].cle;
  }
  function reglerFiliere(cle, majUrl) {
    const f = filieres.liste.find(x => x.cle === cle);
    filiere = f.cle;
    poids = f.poids || poidsDeLaPage;
    document.querySelectorAll("#filiere button").forEach(b => b.setAttribute("aria-pressed", String(b.dataset.filiere === filiere)));
    $("filiereImprimee").textContent = "Filière : " + f.libelle;
    if (majUrl) {
      try {
        const u = new URL(location.href);
        u.searchParams.set(filieres.param || "filiere", filiere);
        history.replaceState(null, "", u);
      } catch (e) { /* l'URL reste telle quelle */ }
    }
    afficherExemples();
    if (filieres.surFiliere) filieres.surFiliere(filiere);
  }
  function monterFiliere() {
    const barre = document.createElement("div");
    barre.id = "filiere";
    barre.className = "variantes no-print";
    barre.setAttribute("role", "group");
    barre.setAttribute("aria-label", "Filière");
    for (const f of filieres.liste) {
      const b = document.createElement("button");
      b.type = "button";
      b.dataset.filiere = f.cle;
      b.textContent = f.libelle;
      b.onclick = () => changerFiliere(f.cle);
      barre.appendChild(b);
    }
    const colonne = document.querySelector(".narrow") || $("entree").closest(".card").parentNode;
    colonne.insertBefore(barre, colonne.firstChild);
    const imprimee = document.createElement("div");
    imprimee.id = "filiereImprimee";
    imprimee.className = "imprime-seulement";
    $("resultat").insertBefore(imprimee, $("resultat").firstChild);
    reglerFiliere(filiereDeDepart(), false);
  }
  function changerFiliere(cle) {
    if (cle === filiere) return;
    reglerFiliere(cle, true);
    exoCourant = null;                                                           // l'exercice affiché vient du pool de l'autre filière
    if ($("exoEnonce")) $("exoEnonce").innerHTML = exoVide;
    if ($("exoCorrige")) $("exoCorrige").hidden = true;
    if (sortie && entreeCourante && !$("calculer").disabled) calculer(entreeCourante);            // l'équation affichée est corrigée pour la nouvelle filière
  }

  if (filieres) monterFiliere(); else afficherExemples();
  document.querySelectorAll("details").forEach(math);
  demarrer();
}
