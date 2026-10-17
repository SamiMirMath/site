/* Web Worker de Pyodide (T15) : la page ne se fige jamais pendant un calcul.
   Messages reçus {id, fn, arg} ; réponses {id, r} ou {id, err}.
     init   : arg = {indexURL, fichiers: {nom: texte}, module}  -> charge Pyodide, écrit les fichiers à plat, importe le module
     sympy  : charge le paquet SymPy de Pyodide
     autre  : appelle <module>.<fn>_json(arg) et renvoie la chaîne JSON
   La version de Pyodide n'est écrite nulle part ici : elle vient de moteur/manifeste.json (indexURL). */
let py = null, module = null;

onmessage = async e => {
  const { id, fn, arg } = e.data;
  try {
    if (fn === "init") {
      importScripts(arg.indexURL + "pyodide.js");
      py = await loadPyodide({ indexURL: arg.indexURL });
      for (const [nom, texte] of Object.entries(arg.fichiers)) py.FS.writeFile(nom, texte);
      module = arg.module;
      py.runPython("import " + module);
      postMessage({ id, r: "ok" });
      return;
    }
    if (fn === "sympy") {
      await py.loadPackage("sympy");
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
