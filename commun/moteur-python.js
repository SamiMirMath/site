/* Client Python/Pyodide commun aux pages outils.

   Lit moteur/manifeste.json (fichiers Python, module, fonctions appelables, version de Pyodide), télécharge les
   fichiers, lance le worker (commun/worker-pyodide.js) et expose des appels qui renvoient du JSON analysé.

     const moteur = new MoteurPython("ensemble-definition", { surEtat: () => majEtat() });
     await moteur.demarrer();                        // fichiers + Pyodide ; SymPy se charge ensuite en arrière-plan
                                                     // (roues précompilées du site, téléchargées pendant le chargement de Pyodide ;
                                                     //  à défaut, roue du CDN : voir worker-pyodide.js)
     const r = await moteur.appelPy("analyser", "ln(x-1)", 30000);   // rejette Error("delai") après 30 s
     moteur.relancer();                              // après un délai dépassé : nouveau worker, mêmes fichiers
     moteur.sympyOK, moteur.sympyPret                // état de SymPy (Promise)
     moteur.noterActivite();                         // l'élève tape : SymPy attend une pause
     moteur.hater();                                 // un calcul attend SymPy : on le charge sans attendre

   Le worker ne fait qu'une chose à la fois et l'installation puis l'import de SymPy le bloquent 1,5 à 2 s (davantage sur un téléphone) : un aperçu demandé
   pendant ce temps attend. SymPy ne se charge donc qu'après une pause de frappe (CALME_MS sans activité), au plus tard ATTENTE_MAX_MS après le démarrage de
   Python, ou tout de suite si un calcul en a besoin (hater). Le premier aperçu part dès que Python est prêt.
*/
const CALME_MS = 700, ATTENTE_MAX_MS = 8000;
const RACINE = new URL("../", import.meta.url);

export class MoteurPython {
  constructor(outil, { surEtat = () => {} } = {}) {
    this.outil = outil;
    this.surEtat = surEtat;
    this.worker = null;
    this.attente = new Map();
    this.nid = 0;
    this.sympyOK = false;
    this.pret = null;
    this.sympyPret = null;
    this.derniereActivite = 0;
    this.lancerSympy = null;
    this.presse = false;
    this.config = null;
    this.fichiers = null;
    this.indexURL = null;
    this.roues = null;
  }

  /** Télécharge le manifeste puis les fichiers Python de l'outil. */
  async charger() {
    const rep = await fetch(new URL("moteur/manifeste.json", RACINE), { cache: "no-cache" });
    if (!rep.ok) throw new Error("manifeste.json introuvable (" + rep.status + ")");
    const manifeste = await rep.json();
    this.config = manifeste.outils[this.outil];
    if (!this.config) throw new Error("outil absent du manifeste : " + this.outil);
    this.indexURL = "https://cdn.jsdelivr.net/pyodide/v" + manifeste.versions.pyodide + "/full/";
    // SymPy et mpmath précompilés (bytecode), hébergés avec le site ; absents du manifeste : le worker prend les roues du CDN
    this.roues = manifeste.roues ? { pyc: manifeste.roues.pyc, urls: manifeste.roues.fichiers.map(c => new URL(c, RACINE).href) } : null;
    const reponses = await Promise.all(this.config.fichiers.map(c => fetch(new URL(c, RACINE), { cache: "no-cache" })));
    this.fichiers = {};
    for (let i = 0; i < reponses.length; i++) {
      const chemin = this.config.fichiers[i];
      if (!reponses[i].ok) throw new Error(chemin + " introuvable (" + reponses[i].status + ")");
      this.fichiers[chemin.split("/").pop()] = await reponses[i].text();
    }
  }

  async demarrer() {
    await this.charger();
    return this.lancer();
  }

  /** (Re)lance le worker avec les fichiers déjà téléchargés. */
  lancer() {
    if (this.worker) this.worker.terminate();
    this.attente = new Map();
    this.sympyOK = false;
    this.presse = false;
    this.worker = new Worker(new URL("worker-pyodide.js", import.meta.url));
    this.worker.onmessage = e => {
      const p = this.attente.get(e.data.id);
      if (!p) return;
      this.attente.delete(e.data.id);
      e.data.err ? p.ko(new Error(e.data.err)) : p.ok(e.data.r);
    };
    this.pret = this.appel("init", { indexURL: this.indexURL, fichiers: this.fichiers, module: this.config.module, roues: this.roues });
    this.sympyPret = this.pret.then(() => this.attendreCalme()).then(() => this.appel("sympy")).then(() => { this.sympyOK = true; this.surEtat(); })
      .catch(() => { this.surEtat(); });
    return this.pret;
  }

  relancer() {
    return this.lancer();
  }

  noterActivite() { this.derniereActivite = Date.now(); }

  /** Un calcul a besoin de SymPy : plus d'attente. */
  hater() { this.presse = true; if (this.lancerSympy) this.lancerSympy(); }

  /** Se résout après CALME_MS sans activité, après ATTENTE_MAX_MS au plus, ou dès que `hater()` est appelée. */
  attendreCalme() {
    return new Promise(ok => {
      if (this.presse) { ok(); return; }                    // un calcul l'a déjà demandé
      const debut = Date.now();
      let fait = false;
      const fin = () => { if (!fait) { fait = true; this.lancerSympy = null; ok(); } };
      this.lancerSympy = fin;
      const verifier = () => {
        if (fait) return;
        const maintenant = Date.now();
        if (maintenant - Math.max(this.derniereActivite, debut) >= CALME_MS || maintenant - debut >= ATTENTE_MAX_MS) fin();
        else setTimeout(verifier, 100);
      };
      verifier();
    });
  }

  appel(fn, arg, delai) {
    return new Promise((ok, ko) => {
      const id = ++this.nid;
      this.attente.set(id, { ok, ko });
      this.worker.postMessage({ id, fn, arg });
      if (delai) setTimeout(() => { if (this.attente.has(id)) { this.attente.delete(id); ko(new Error("delai")); } }, delai);
    });
  }

  async appelPy(fn, arg, delai) {
    if (!this.config.fonctions.includes(fn)) throw new Error("fonction absente du manifeste : " + fn);
    await this.pret;
    return JSON.parse(await this.appel(fn, arg, delai));
  }
}
