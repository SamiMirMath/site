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
*/
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
    this.worker = new Worker(new URL("worker-pyodide.js", import.meta.url));
    this.worker.onmessage = e => {
      const p = this.attente.get(e.data.id);
      if (!p) return;
      this.attente.delete(e.data.id);
      e.data.err ? p.ko(new Error(e.data.err)) : p.ok(e.data.r);
    };
    this.pret = this.appel("init", { indexURL: this.indexURL, fichiers: this.fichiers, module: this.config.module, roues: this.roues });
    this.sympyPret = this.pret.then(() => this.appel("sympy")).then(() => { this.sympyOK = true; this.surEtat(); })
      .catch(() => { this.surEtat(); });
    return this.pret;
  }

  relancer() {
    return this.lancer();
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
