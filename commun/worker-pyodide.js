/* Web Worker de Pyodide (T15) : la page ne se fige jamais pendant un calcul.
   Messages reçus {id, fn, arg} ; réponses {id, r} ou {id, err}.
     init   : arg = {indexURL, fichiers: {nom: texte}, module, roues}  -> charge Pyodide, écrit les fichiers à plat, importe le module
     sympy  : charge SymPy (et mpmath) : les roues précompilées du site (arg.roues = {pyc, urls}, téléchargées pendant le chargement de
              Pyodide) si leur bytecode est celui de ce Python, sinon le paquet SymPy du CDN de Pyodide (plus lent : tout est compilé à l'import)
     autre  : appelle <module>.<fn>_json(arg) et renvoie la chaîne JSON
   La version de Pyodide n'est écrite nulle part ici : elle vient de moteur/manifeste.json (indexURL). */
let py = null, module = null, roues = null, magique = null;

onmessage = async e => {
  const { id, fn, arg } = e.data;
  try {
    if (fn === "init") {
      if (arg.roues) {              // le téléchargement part tout de suite, en même temps que celui de Pyodide
        magique = arg.roues.pyc;
        roues = Promise.all(arg.roues.urls.map(async u => {
          const r = await fetch(u);
          if (!r.ok) throw new Error(u + " : " + r.status);
          return r.arrayBuffer();
        }));
        roues.catch(() => {});      // l'échec n'est traité qu'à l'appel « sympy » (repli sur le CDN)
      }
      importScripts(arg.indexURL + "pyodide.js");
      py = await loadPyodide({ indexURL: arg.indexURL });
      for (const [nom, texte] of Object.entries(arg.fichiers)) py.FS.writeFile(nom, texte);
      module = arg.module;
      py.runPython("import " + module);
      postMessage({ id, r: "ok" });
      return;
    }
    if (fn === "sympy") {
      if (!(await installerRouesPrecompilees())) await py.loadPackage("sympy");
      py.runPython("import sympy");
      postMessage({ id, r: "ok" });
      return;
    }
    py.globals.set("arg_js", arg);
    postMessage({ id, r: py.runPython(module + "." + fn + "_json(arg_js)") });
  } catch (err) {
    postMessage({ id, err: String(err) });
  }
};

/** Installe les roues précompilées dans site-packages. Faux (rien d'installé de travers) si elles manquent, ne se téléchargent pas ou
 *  ont un bytecode d'une autre version de Python : l'appelant prend alors le paquet du CDN. */
async function installerRouesPrecompilees() {
  if (!roues) return false;
  try {
    if (py.runPython("import importlib.util\nimportlib.util.MAGIC_NUMBER.hex()") !== magique) return false;
    const octets = await roues;
    const dossier = py.runPython("import site\nsite.getsitepackages()[0]");
    for (const o of octets) py.unpackArchive(o, "zip", { extractDir: dossier });
    py.runPython("import importlib\nimportlib.invalidate_caches()");
    return true;
  } catch (e) {
    return false;
  }
}
