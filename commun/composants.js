/* Composants interactifs communs (style : commun/composants.css). Module ES :

     import { monterOnglets, champSigne } from "../commun/composants.js";                                          */

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
       surChange(valeurSignee)  appelée à chaque modification
     Renvoie le <span class="champ-signe"> ; ses propriétés .bouton et .champ donnent accès aux deux éléments. */
const SIGNE_EN_TETE = /^\s*([+\-−–—‐‑])\s*/;
const MOINS_EN_TETE = /^\s*[-−–—‐‑]/;

export function champSigne({ valeur = "", signe, nom, membre = false, attrs = {}, surChange } = {}) {
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
