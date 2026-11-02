/* Composants interactifs communs (style : commun/composants.css). Module ES :

     import { monterOnglets, champSigne, estTactile, sansClavierSysteme, avecClavierSysteme, monterClavierTactile, monterPave } from "../commun/composants.js";   */

/* ---- Onglets accessibles ----
   `conteneur` contient des <button> : ils reçoivent role="tab", aria-selected et un tabindex mobile (seul l'onglet actif est dans l'ordre de tabulation).
   Flèches gauche/droite (circulaires), Début et Fin déplacent le focus ET activent l'onglet. Ces touches ne remontent pas jusqu'à la page,
   pour qu'un raccourci de page (flèches = pages précédente/suivante) ne se déclenche pas en même temps.
   `surChoix(bouton)` est appelée à chaque activation (clic ou clavier). Renvoie { choisir(bouton|index), actif() }. */
export function monterOnglets(conteneur, surChoix) {
  const onglets = [...conteneur.querySelectorAll("button")].filter((b) => !b.hidden);        // un onglet masqué n'est ni atteint ni activé par les flèches
  conteneur.setAttribute("role", "tablist");
  const choisir = (cible, { focus = false, notifier = true } = {}) => {
    const b = typeof cible === "number" ? onglets[(cible + onglets.length) % onglets.length] : cible;
    onglets.forEach((o) => { const actif = o === b; o.setAttribute("aria-selected", actif ? "true" : "false"); o.tabIndex = actif ? 0 : -1; });
    if (focus) b.focus();
    if (notifier && surChoix) surChoix(b);
  };
  onglets.forEach((b, i) => {
    b.setAttribute("role", "tab");
    b.type = "button";
    b.addEventListener("click", () => choisir(b));
    b.addEventListener("keydown", (e) => {
      const touche = { ArrowRight: i + 1, ArrowLeft: i - 1, Home: 0, End: onglets.length - 1 }[e.key];
      if (touche === undefined) return;
      e.preventDefault(); e.stopPropagation();
      choisir(touche, { focus: true });
    });
  });
  const depart = onglets.find((o) => o.getAttribute("aria-selected") === "true") || onglets[0];
  if (depart) choisir(depart, { notifier: false });
  return { choisir, actif: () => onglets.find((o) => o.getAttribute("aria-selected") === "true") };
}

/* ---- Champ numérique précédé d'un bouton de signe ----
   Le clavier « chiffres » du téléphone (inputmode="decimal") n'a pas de « − » : le signe est porté par le bouton, le champ n'affiche que la valeur absolue.
   La valeur transmise est SIGNÉE : « -3 » ; « - » seul = signe moins et case vide (vaut 0, quel que soit le signe).
   Un tiret (de toute forme) tapé ou collé en tête du champ est retiré du champ et met le bouton sur « − » ; un « + » en tête est simplement retiré.

     champSigne({ valeur, signe: "du coefficient de x₁", nom: "coefficient de x₁", membre: false, attrs: {}, surChange })
       valeur    texte signé de départ (« -2 », « 1/2 », « »)
       signe     complète l'aria-label du bouton : « signe du coefficient de x₁ : plus | moins »
       nom       aria-label du champ
       membre    true : champ plus large (second membre)
       attrs     attributs supplémentaires du champ (data-*, …)
       pave      true : le champ s'écrit avec le pavé de la page (monterPave) ; sur écran tactile, le clavier du système ne s'ouvre pas (sansClavierSysteme)
       surChange(valeurSignee)  appelée à chaque modification
     Renvoie le <span class="champ-signe"> ; ses propriétés .bouton et .champ donnent accès aux deux éléments. */
const SIGNE_EN_TETE = /^\s*([+\-−–—‐‑])\s*/;
const MOINS_EN_TETE = /^\s*[-−–—‐‑]/;

export function champSigne({ valeur = "", signe, nom, membre = false, attrs = {}, pave = false, surChange } = {}) {
  let moins = MOINS_EN_TETE.test(valeur || "");
  const bloc = document.createElement("span");
  bloc.className = "champ-signe" + (membre ? " membre" : "");
  const bouton = document.createElement("button");
  bouton.type = "button";
  const champ = document.createElement("input");
  if (nom) champ.setAttribute("aria-label", nom);
  champ.value = String(valeur || "").replace(SIGNE_EN_TETE, "");
  Object.entries({ inputmode: "decimal", autocomplete: "off", autocorrect: "off", autocapitalize: "off", spellcheck: "false", ...attrs })
    .forEach(([k, v]) => champ.setAttribute(k, v));
  if (pave && estTactile()) sansClavierSysteme(champ);
  const majBouton = () => {
    bouton.textContent = moins ? "−" : "+";
    bouton.dataset.signe = moins ? "-" : "+";
    bouton.setAttribute("aria-label", `signe ${signe} : ${moins ? "moins" : "plus"}`);
  };
  const signee = () => (moins ? "-" : "") + champ.value.trim();
  const prevenir = () => { if (surChange) surChange(signee()); };
  bouton.addEventListener("click", () => { moins = !moins; majBouton(); prevenir(); });
  champ.addEventListener("input", () => {
    const m = SIGNE_EN_TETE.exec(champ.value);
    if (m) { if (m[1] !== "+") moins = true; champ.value = champ.value.slice(m[0].length); majBouton(); }
    prevenir();
  });
  majBouton();
  bloc.append(bouton, champ);
  Object.assign(bloc, { bouton, champ, signee });
  return bloc;
}

/* ---- Clavier de la page ou clavier du système ----
   Sur un écran tactile (pointeur « coarse »), l'élève tape les nombres et les formules avec les touches de la page : le clavier du système ne doit pas s'ouvrir.
     estTactile()                    vrai sur téléphone et tablette
     sansClavierSysteme(champ)       inputmode="none" ; sur iPhone et iPad aussi readonly (iOS ouvre parfois son clavier malgré inputmode="none") : seules les touches écrivent
     avecClavierSysteme(champ)       remet l'état d'origine du champ (saisie inhabituelle : lettres, symboles) */
export const estTactile = () => typeof matchMedia === "function" && matchMedia("(pointer: coarse)").matches;
const SUR_IOS = () => /iPad|iPhone|iPod/.test(navigator.userAgent) || (navigator.platform === "MacIntel" && navigator.maxTouchPoints > 1);     // iPadOS se présente comme un Mac

export function sansClavierSysteme(champ) {
  if (!("modeOrigine" in champ.dataset)) champ.dataset.modeOrigine = champ.getAttribute("inputmode") ?? "";
  champ.setAttribute("inputmode", "none");
  if (SUR_IOS()) champ.readOnly = true;
}
export function avecClavierSysteme(champ) {
  const origine = champ.dataset.modeOrigine;
  if (origine) champ.setAttribute("inputmode", origine); else champ.removeAttribute("inputmode");
  champ.readOnly = false;
}

/* ---- Clavier à touches des outils à saisie de fonction (.clavier, champ #entree) ----
   Sur tactile seulement : coupe le clavier du système sur `champ` et ajoute au bas de `clavier` une rangée « ABC » + « Calculer ▶ ».
   « ABC » rouvre le clavier du système (« 123 » revient aux touches) ; « Calculer ▶ » fait le clic du bouton `lancer` et en suit le libellé et l'état :
   le bouton de la page, devenu doublon, est caché (il reste dans la page : les autres scripts le déclenchent toujours).
   Un appui sur une touche ne retire pas le focus du champ (le curseur reste visible). Sur ordinateur : rien n'est changé, renvoie null. */
export function monterClavierTactile({ clavier, champ, lancer }) {
  if (!estTactile()) return null;
  sansClavierSysteme(champ);
  lancer.hidden = true;
  const bouton = (classe, texte) => { const b = document.createElement("button"); b.type = "button"; b.className = classe; b.textContent = texte; return b; };
  const abc = bouton("abc", "ABC"), calculer = bouton("primary lancer", lancer.textContent);
  let systeme = false;
  const majAbc = () => {
    abc.textContent = systeme ? "123" : "ABC";
    abc.setAttribute("aria-label", systeme ? "Revenir aux touches de la page" : "Ouvrir le clavier du système pour une saisie inhabituelle");
  };
  const majLancer = () => { calculer.textContent = lancer.textContent; calculer.disabled = lancer.disabled; };
  abc.addEventListener("click", () => {
    systeme = !systeme;
    majAbc();
    // Le champ a déjà le focus (les touches le lui rendent) : sans blur(), focus() ne fait rien et iOS n'ouvre pas son clavier. blur() puis focus() dans le même
    // geste (iOS n'ouvre le clavier que pour un focus donné dans un geste de l'élève) ; « 123 » : blur() ferme le clavier, le champ est de nouveau muet.
    champ.blur();
    if (systeme) { avecClavierSysteme(champ); champ.focus(); }
    else { sansClavierSysteme(champ); champ.focus({ preventScroll: true }); }
  });
  calculer.addEventListener("click", () => { if (!lancer.disabled) lancer.click(); });
  new MutationObserver(majLancer).observe(lancer, { attributes: true, attributeFilter: ["disabled"], childList: true, characterData: true, subtree: true });
  clavier.addEventListener("mousedown", (e) => { if (!e.target.closest(".abc")) e.preventDefault(); });           // une touche ne prend pas le focus : le champ le garde (« ABC » : le navigateur fait son travail)
  clavier.addEventListener("click", (e) => { if (e.target.closest("button[data-t], button[data-k]") && document.activeElement !== champ) champ.focus({ preventScroll: true }); });
  majAbc();
  majLancer();
  clavier.append(abc, calculer);
  return { abc, calculer };
}

/* ---- Pavé numérique fixé en bas de l'écran (champs `.champ-signe`, écran tactile seulement) ----
     monterPave({ champs })   `champs()` renvoie les champs dans l'ordre de lecture ; renvoie { fermer } (null hors écran tactile)
   Le pavé apparaît quand un champ `.champ-signe > input` reçoit le focus :
       7 8 9 ⌫  /  4 5 6 ,  /  1 2 3 /  /  0 [Suivant ▶]
   (mêmes places pour 0 à 9, la virgule et ⌫ que le clavier des outils à saisie de fonction ; le signe reste sur le bouton du champ).
   Chaque touche modifie la valeur au curseur puis envoie un événement `input`, comme une frappe : le champ prévient la page. « Suivant ▶ » passe au champ suivant,
   le dernier ferme le pavé. Le pavé se ferme aussi au toucher en dehors de lui et des champs, et à l'appel de `fermer()` (lancement du calcul).
   Le champ actif reste visible au-dessus du pavé : la page gagne en bas la hauteur du pavé (--pave-h) et le champ est amené à l'écran. */
export function monterPave({ champs }) {
  if (!estTactile()) return null;
  const pave = document.createElement("div");
  pave.className = "pave no-print";
  pave.setAttribute("role", "group");
  pave.setAttribute("aria-label", "Pavé numérique");
  pave.hidden = true;
  pave.innerHTML = [
    '<button data-t="7">7</button><button data-t="8">8</button><button data-t="9">9</button><button aria-label="effacer le dernier caractère" data-k="back">⌫</button>',
    '<button data-t="4">4</button><button data-t="5">5</button><button data-t="6">6</button><button aria-label="virgule" data-t=",">,</button>',
    '<button data-t="1">1</button><button data-t="2">2</button><button data-t="3">3</button><button aria-label="barre de fraction" data-t="/">/</button>',
    '<button data-t="0">0</button><button class="primary suivant" data-k="suivant">Suivant ▶</button>',
  ].join("");
  pave.querySelectorAll("button").forEach((b) => { b.type = "button"; });
  document.body.appendChild(pave);
  let actif = null;

  const amener = (champ) => (champ.closest(".champ-signe") || champ).scrollIntoView({ block: "nearest" });        // `scroll-margin-bottom` du bloc : au-dessus du pavé
  const ouvrir = (champ) => {
    actif = champ;
    if (pave.hidden) {
      pave.hidden = false;
      document.documentElement.style.setProperty("--pave-h", pave.offsetHeight + "px");
      document.body.classList.add("avec-pave");
    }
    amener(champ);
  };
  const fermer = () => {
    if (pave.hidden) return;
    pave.hidden = true;
    document.body.classList.remove("avec-pave");
    document.documentElement.style.setProperty("--pave-h", "0px");
    if (actif && document.activeElement === actif) actif.blur();
    actif = null;
  };
  const suivant = () => {
    const liste = champs(), prochain = liste[liste.indexOf(actif) + 1];
    if (!prochain) { fermer(); return; }
    prochain.focus({ preventScroll: true });                          // le focus rappelle `ouvrir`
    prochain.setSelectionRange(prochain.value.length, prochain.value.length);
    amener(prochain);
  };

  pave.addEventListener("mousedown", (e) => e.preventDefault());     // une touche ne prend pas le focus : le champ le garde
  pave.addEventListener("click", (e) => {
    const b = e.target.closest("button");
    if (!b || !actif) return;
    if (b.dataset.k === "suivant") { suivant(); return; }
    if (document.activeElement !== actif) actif.focus({ preventScroll: true });       // le bouton de signe a pu prendre le focus
    const a = actif.selectionStart ?? actif.value.length, z = actif.selectionEnd ?? a;
    if (b.dataset.k === "back") {
      if (a !== z) { actif.value = actif.value.slice(0, a) + actif.value.slice(z); actif.setSelectionRange(a, a); }
      else if (a > 0) { actif.value = actif.value.slice(0, a - 1) + actif.value.slice(a); actif.setSelectionRange(a - 1, a - 1); }
    } else { const t = b.dataset.t; actif.value = actif.value.slice(0, a) + t + actif.value.slice(z); actif.setSelectionRange(a + t.length, a + t.length); }
    actif.dispatchEvent(new Event("input", { bubbles: true }));
  });
  document.addEventListener("focusin", (e) => { if (e.target.matches && e.target.matches(".champ-signe > input")) ouvrir(e.target); });
  document.addEventListener("pointerdown", (e) => { if (!pave.hidden && !e.target.closest(".pave, .champ-signe")) fermer(); });
  return { fermer };
}
