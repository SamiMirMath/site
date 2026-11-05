"""Contrôle, après le commit, du rapport écrit par `lancer.py complet --rapport` (chantier tests-rapides, P2, décision T1, audit §M1).

    python3 tests/lancer.py verifier <dossier> [--reference <dossier>] [--commit <rév>] [--suivi <fichier>]

Le chef d'orchestre le lance après le commit d'une partie, sur le dossier que le sous-agent a donné à `complet --rapport`. Il ne relance
aucun test : il vérifie que le lancement noté dans le dossier a bien eu lieu sur le contenu du commit, qu'il était vert et qu'il n'a perdu
aucun test. Code 0 = ACCEPTÉ ; 1 = REFUSÉ (motifs listés) ; 2 = REFUSÉ, dossier ou fichier manquant.

Notations : D = commit de départ du lancement (`head` de rapport.json) ; C = commit vérifié (HEAD, ou `--commit`) ;
M = empreintes (`git hash-object`) des fichiers modifiés ou non suivis au début du lancement ; F = le même relevé à la fin.

(a) Commit. C = D, ou C a un seul parent, D. Chaque fichier changé entre D et C (`git diff --no-renames -z D C`) :
    - a dans C l'empreinte notée dans M (absent de C si noté supprimé), et la même dans F (pas changé pendant le lancement) ;
    - sinon REFUS, sauf sous `docs/` (IGNORES : aucun test ne lit docs/, comme pour la commande `reference` ; par exemple le suivi.md et
      le journal.md du chantier, écrits après le lancement) : le fichier est alors seulement listé comme ignoré.
(b) Autres fichiers. Un fichier de M ou de F qui n'est pas changé entre D et C (modifié, non suivi ou apparu pendant le lancement, puis
    laissé hors du commit) fait REFUSER, sauf sous `docs/` (IGNORES) ou dans PERMIS_HORS_COMMIT (`CLAUDE.md`, que l'enseignant peut être
    en train de modifier et dont aucun test ne lit le contenu ; il reste refusé s'il est dans le commit avec une autre empreinte) : il
    est alors seulement listé comme ignoré. Le verdict liste toujours les fichiers ignorés (« aucun » s'il n'y en a pas).
(c) Résultats. Codes de retour 0 (global, Python, pages ; les pages lancées) ; `CORPUS` et `OUTILS` non définis au lancement ; JUnit et
    listes texte concordants ; puis, comparé au dossier de référence (par défaut tests/reference, la référence du dépôt, rafraîchie
    au P0 de chaque chantier par `lancer.py reference` ; `--reference` en désigne un autre), REFUS si un test collecté ou un résultat
    disparaît, si un test est sauté en plus, si une issue change (seules xfail -> passé et sauté -> passé sont acceptées, et listées)
    ou si un nombre de sous-tests passés baisse sans justification (d). Un test disparu, échoué ou sauté en plus est toujours refusé :
    aucune justification ne l'excuse. Un test ajouté (passé ou xfail), ou un nombre de sous-tests en hausse, est accepté et listé.
(d) Baisse de sous-tests justifiée. Une baisse du nombre de sous-tests passés d'un test (toujours passé) est acceptée, et listée avec sa
    raison, si le suivi.md du chantier la justifie, dans sa section « ## Variations de sous-tests » (jusqu'au titre « ## » suivant),
    par une ligne de la forme (une par test ; « -> » vaut « → ») :
        - `<identifiant pytest complet>` : <avant> → <après> : <raison>
    par exemple « - `tests/python/test_x.py::TestY::test_z` : 120 → 118 : deux entrées en double retirées (F5) ». <avant> et <après>
    sont les nombres de sous-tests passés de la référence et du lancement, exactement ceux que verifier mesure (sa rubrique « sous-tests
    en baisse ») : sinon REFUS. Plusieurs lignes pour un même test sont permises (une par partie) : il suffit qu'une corresponde. Une
    ligne qui commence par « - ` » sans suivre ce format, ou une justification sans baisse correspondante, est listée, sans effet.
    Le suivi.md lu est `--suivi <fichier>`, sinon `docs/chantiers/<branche>/suivi.md` dans l'arbre de travail (branche courante, ou
    celle du lancement notée dans rapport.json si HEAD est détaché). S'il est introuvable, ou sans la section, toute baisse est refusée.

Sans dépendance (Python du système). Ce fichier ne s'appelle pas `test_*.py` : pytest ne le collecte pas."""
import json
import os
import re
import subprocess

import comparer_listes

RACINE = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
REFERENCE = "tests/reference"                 # rafraîchie par `lancer.py reference <dossier>`, jamais automatiquement
IGNORES = re.compile(r"^docs/")                 # aucun test ne lit docs/ (comme HORS_TESTS de `lancer.py reference`)
PERMIS_HORS_COMMIT = frozenset({"CLAUDE.md"})   # ignoré hors du commit seulement
SECTION_VARIATIONS = "## Variations de sous-tests"
LIGNE_VARIATION = re.compile(r"^- `([^`]+)` : (\d+) (?:→|->) (\d+) : (\S.*)$")
ENV_INTERDITS = ("CORPUS", "OUTILS")            # corpus réduit ou outils choisis : la suite n'est plus complète
AMELIORATIONS = {("xfail", "passé"), ("sauté", "passé")}
MAX_LIGNES = 25                                  # au-delà, la liste d'une rubrique est coupée (le compte reste exact)


def git(*args):
    r = subprocess.run(("git",) + args, cwd=RACINE, capture_output=True, text=True)
    return r.returncode, r.stdout.strip()


def noms_git(*args):
    """Noms de fichiers d'une commande git lancée avec `-z` : découpage sur \\0, donc ni guillemets ni échappements octaux (noms à
    espaces ou non ASCII, par exemple « a b.py », « é.py ») ; exception si git échoue (lancer.py s'en sert aussi)."""
    sortie = subprocess.run(("git",) + args, cwd=RACINE, capture_output=True, check=True).stdout
    return [os.fsdecode(n) for n in sortie.split(b"\0") if n]


def court(rev):
    return rev[:7] if rev else "?"


class Verification:
    def __init__(self):
        self.refus = []          # motifs de refus
        self.listes = []         # (titre, éléments) acceptés mais montrés
        self.lignes = []         # résumé
        self.ignores = []        # fichiers ignorés par (a) et (b) : docs/, CLAUDE.md hors du commit (toujours affichés)

    def refuser(self, motif, elements=()):
        self.refus.append((motif, list(elements)))

    def lister(self, titre, elements):
        if elements:
            self.listes.append((titre, list(elements)))


def coupe(elements):
    lignes = [f"      {e}" for e in elements[:MAX_LIGNES]]
    if len(elements) > MAX_LIGNES:
        lignes.append(f"      … et {len(elements) - MAX_LIGNES} autre(s)")
    return lignes


# --- (a) et (b) : le commit et les fichiers ------------------------------------------------------------------------------------

def empreinte_dans(commit, chemin):
    code, sortie = git("rev-parse", "--verify", "-q", f"{commit}:{chemin}")
    return sortie if code == 0 else None


def verifier_commit(v, rapport, commit_demande):
    depart = rapport.get("head")
    m = rapport.get("fichiers_modifies")
    f = rapport.get("fichiers_modifies_fin")
    if not depart or m is None or f is None:
        v.refuser("rapport.json incomplet : head, fichiers_modifies ou fichiers_modifies_fin manquant (lancement interrompu ?)")
        return
    code, commit = git("rev-parse", "--verify", "-q", f"{commit_demande}^{{commit}}")
    if code:
        v.refuser(f"commit introuvable : {commit_demande}")
        return
    if git("cat-file", "-e", f"{depart}^{{commit}}")[0]:
        v.refuser(f"le commit de départ du lancement ({court(depart)}) n'existe pas dans le dépôt")
        return
    if commit == depart:
        changes = []
        lien = "est le commit de départ du lancement (aucun commit depuis)"
    else:
        parents = git("rev-list", "--parents", "-n", "1", commit)[1].split()[1:]
        if parents != [depart]:
            v.refuser(f"(a) {court(commit)} n'est ni le commit de départ du lancement ({court(depart)}) ni son enfant direct "
                      f"(parents : {', '.join(court(p) for p in parents) or 'aucun'}) : le lancement ne porte pas sur ce commit")
            return
        changes = noms_git("diff", "--no-renames", "--name-only", "-z", depart, commit, "--")
        lien = f"enfant direct du commit de départ {court(depart)}"
    v.lignes.append(f"(a) commit {court(commit)} : {lien} ; {len(changes)} fichier(s) changé(s)")

    mauvais, ignores = [], []
    for chemin in changes:
        dans_c = empreinte_dans(commit, chemin)
        if IGNORES.match(chemin):
            if not (chemin in m and m[chemin] == dans_c == f.get(chemin)):
                ignores.append(f"{chemin} : dans le commit, changé après le début du lancement (docs/, aucun test ne le lit)")
            continue
        if chemin not in m:
            mauvais.append(f"{chemin} : dans le commit, mais ni modifié ni non suivi au début du lancement (non testé)")
        elif m[chemin] != dans_c:
            mauvais.append(f"{chemin} : empreinte dans le commit {court(dans_c) if dans_c else 'supprimé'}, "
                           f"au lancement {court(m[chemin]) if m[chemin] else 'supprimé'}")
        elif f.get(chemin, "absent") != m[chemin]:
            mauvais.append(f"{chemin} : changé pendant le lancement (début {court(m[chemin])}, fin {court(f.get(chemin))})")
    if mauvais:
        v.refuser("(a) fichier(s) du commit différent(s) de ce que le lancement a testé", mauvais)
    else:
        v.lignes.append(f"    empreintes conformes pour les {len(changes) - len(ignores)} fichier(s) testé(s)")

    autres = []
    for chemin in sorted(set(m) | set(f)):
        if chemin in changes:
            continue
        if chemin not in m:
            etat = "apparu pendant le lancement"
        elif chemin not in f or f[chemin] != m[chemin]:
            etat = "modifié au début, changé ou retiré pendant le lancement"
        else:
            etat = "modifié ou non suivi pendant le lancement"
        if IGNORES.match(chemin):
            ignores.append(f"{chemin} : {etat}, absent du commit (docs/, aucun test ne le lit)")
        elif chemin in PERMIS_HORS_COMMIT:
            ignores.append(f"{chemin} : {etat}, absent du commit (fichier de l'enseignant, aucun test ne le lit)")
        else:
            autres.append(f"{chemin} : {etat}, absent du commit")
    if autres:
        v.refuser("(b) fichier(s) modifié(s) ou non suivi(s) pendant le lancement, hors du commit, ni sous docs/ ni CLAUDE.md", autres)
    else:
        v.lignes.append("(b) aucun autre fichier modifié ou non suivi pendant le lancement (hors fichiers ignorés)")
    v.ignores.extend(ignores)


# --- (c) : codes et listes --------------------------------------------------------------------------------------------------------

def sous_tests(texte):
    """« 12 » ou « passé:10,échoué:2 » -> {issue: nombre}."""
    if ":" not in texte:
        return {"passé": int(texte)} if int(texte) else {}
    return {k: int(n) for k, n in (p.split(":") for p in texte.split(","))}


def verifier_codes(v, rapport):
    env = rapport.get("environnement")
    if env is None:
        v.lignes.append("(c) environnement du lancement non noté (rapport antérieur à P2)")
    else:
        v.lignes.append("(c) environnement : " + ", ".join(f"{k}={env.get(k) if env.get(k) is not None else '(non défini)'}"
                                                          for k in sorted(env)))
        definis = [k for k in ENV_INTERDITS if env.get(k) not in (None, "")]
        if definis:
            v.refuser("(c) suite non complète : " + ", ".join(f"{k}={env[k]}" for k in definis) + " au lancement")
    py, pa = rapport.get("python") or {}, rapport.get("pages") or {}
    if rapport.get("code") != 0 or py.get("code") != 0 or pa.get("code") != 0 or not pa.get("lancee"):
        v.refuser(f"(c) codes de retour : global {rapport.get('code')}, Python {py.get('code')}, "
                  f"pages {pa.get('code') if pa.get('lancee') else 'non lancées'} (0 exigé partout)")
    for suite, b in (("python", py), ("pages", pa)):
        if b.get("ecarts_junit"):
            v.refuser(f"(c) {suite} : JUnit et extension discordants (rapport.json)", b["ecarts_junit"])


class Justifications:
    """(d) Lignes de la section « Variations de sous-tests » d'un suivi.md : {identifiant: [(avant, après, raison)]}."""

    def __init__(self, chemin):
        self.chemin = chemin
        self.par_test = {}
        self.incomprises = []        # lignes « - ` » de la section qui ne suivent pas le format
        self.utilisees = set()       # identifiants dont une baisse a été examinée
        self.erreur = None           # None, ou pourquoi aucune justification n'est lisible
        try:
            with open(chemin, encoding="utf-8") as fichier:
                texte = fichier.read()
        except OSError:
            self.erreur = "fichier introuvable"
            return
        dans, trouvee = False, False
        for ligne in texte.splitlines():
            if ligne.startswith("## "):
                dans = ligne.rstrip() == SECTION_VARIATIONS
                trouvee = trouvee or dans
                continue
            if not dans:
                continue
            m = LIGNE_VARIATION.match(ligne.rstrip())
            if m:
                self.par_test.setdefault(m.group(1), []).append((int(m.group(2)), int(m.group(3)), m.group(4).strip()))
            elif ligne.startswith("- `"):
                self.incomprises.append(ligne.rstrip())
        if not trouvee:
            self.erreur = f"section « {SECTION_VARIATIONS[3:]} » absente"

    def nombre(self):
        return sum(len(l) for l in self.par_test.values())

    def raison(self, identifiant, avant, apres):
        """La raison d'une ligne aux nombres exacts, ou None."""
        self.utilisees.add(identifiant)
        for a, b, raison in self.par_test.get(identifiant, ()):
            if (a, b) == (avant, apres):
                return raison
        return None

    def autres_nombres(self, identifiant):
        return ", ".join(f"{a} → {b}" for a, b, _ in self.par_test.get(identifiant, ()))

    def sans_effet(self):
        return [f"{i} : {a} → {b} : {r}" for i in sorted(set(self.par_test) - self.utilisees) for a, b, r in self.par_test[i]]


def chemin_suivi(option, rapport):
    """--suivi, sinon docs/chantiers/<branche courante>/suivi.md (branche du lancement si HEAD est détaché)."""
    if option:
        return os.path.abspath(option)
    code, branche = git("rev-parse", "--abbrev-ref", "HEAD")
    if code or branche in ("", "HEAD"):
        branche = rapport.get("branche") or "?"
    return os.path.join(RACINE, "docs", "chantiers", branche, "suivi.md")


def lisible(chemin):
    return os.path.relpath(chemin, RACINE) if os.path.commonpath([chemin, RACINE]) == RACINE else chemin


def verifier_suite(v, dossier, reference, suite, rapport, variables, justifications):
    b = rapport.get(suite) or {}
    collecte = comparer_listes.lire_collecte(dossier, suite)
    resultats = comparer_listes.lire_resultats(dossier, suite)
    ref_collecte = set(comparer_listes.lire_collecte(reference, suite))
    ref_resultats = comparer_listes.lire_resultats(reference, suite)

    # concordance des témoins du dossier : listes texte, rapport.json, JUnit
    par_issue = {}
    for i, (issue, _) in resultats.items():
        par_issue.setdefault(issue, set()).add(i)
    attendu = {"passé": set(b.get("passes", [])), "xfail": set(b.get("xfail", [])), "sauté": set(b.get("sautes", []))}
    attendu.update({k: set(l) for k, l in (b.get("autres") or {}).items()})
    if {k: s for k, s in par_issue.items() if s} != {k: s for k, s in attendu.items() if s} or b.get("collectes") != len(collecte):
        v.refuser(f"(c) {suite} : listes texte et rapport.json discordants (dossier modifié après le lancement ?)")
    junit = os.path.join(dossier, f"{suite}.xml")
    if not os.path.exists(junit):
        v.refuser(f"(c) {suite} : JUnit absent ({suite}.xml)")
    else:
        ecarts = comparer_listes.ecarts_junit(junit, {i: r[0] for i, r in resultats.items()})
        if ecarts:
            v.refuser(f"(c) {suite} : JUnit et listes texte discordants", ecarts)

    v.lignes.append(f"(c) {suite} : {comparer_listes.resume(dossier, suite)}")

    disparus = sorted(ref_collecte - set(collecte)) + [f"{i} (résultat)" for i in sorted(set(ref_resultats) - set(resultats))
                                                       if i in collecte]
    if disparus:
        v.refuser(f"(c) {suite} : test(s) disparu(s) par rapport à la référence", disparus)
    nouveaux = sorted((set(collecte) - ref_collecte) | (set(resultats) - set(ref_resultats)))
    ajoutes, sautes, degrades, ameliores, baisses, justifiees, hausses = [], [], [], [], [], [], []
    for i in nouveaux:
        issue = resultats.get(i, ("non exécuté", "0"))[0]
        (ajoutes if issue in ("passé", "xfail") else sautes if issue == "sauté" else degrades).append(f"{i} (nouveau, {issue})")
    for i in sorted(set(ref_resultats) & set(resultats)):
        (ri, rs), (ni, ns) = ref_resultats[i], resultats[i]
        if ri != ni:
            if (ri, ni) in AMELIORATIONS:
                ameliores.append(f"{i} : {ri} -> {ni}")
            else:
                (sautes if ni == "sauté" else degrades).append(f"{i} : {ri} -> {ni}")
        if i in variables:
            continue
        rp, np_ = sous_tests(rs).get("passé", 0), sous_tests(ns).get("passé", 0)
        if np_ < rp and ri == ni:
            raison = justifications.raison(i, rp, np_)
            if raison is not None:
                justifiees.append(f"{i} : {rp} -> {np_} : {raison}")
            elif justifications.erreur:
                baisses.append(f"{i} : {rp} -> {np_} (suivi.md : {justifications.erreur})")
            elif i in justifications.par_test:
                baisses.append(f"{i} : {rp} -> {np_} (suivi.md donne {justifications.autres_nombres(i)} : nombres différents)")
            else:
                baisses.append(f"{i} : {rp} -> {np_} (aucune ligne pour ce test dans suivi.md)")
        elif np_ < rp:
            baisses.append(f"{i} : {rp} -> {np_} (issue changée : {ri} -> {ni})")
        elif np_ > rp:
            hausses.append(f"{i} : {rp} -> {np_}")
        if any(k != "passé" for k in sous_tests(ns)):
            degrades.append(f"{i} : sous-tests {ns}")
    if sautes:
        v.refuser(f"(c) {suite} : test(s) sauté(s) en plus", sautes)
    if degrades:
        v.refuser(f"(c) {suite} : issue(s) dégradée(s) ou changée(s)", degrades)
    if baisses:
        v.refuser(f"(c) {suite} : nombre de sous-tests passés en baisse, sans justification exacte (d) dans "
                  f"{lisible(justifications.chemin)}", baisses)
    v.lister(f"(d) {suite} : sous-tests en baisse, justifiés dans {lisible(justifications.chemin)} (acceptés)", justifiees)
    v.lister(f"(c) {suite} : test(s) ajouté(s) (acceptés)", ajoutes)
    v.lister(f"(c) {suite} : issue(s) améliorée(s) (acceptées)", ameliores)
    v.lister(f"(c) {suite} : sous-tests en hausse (acceptés)", hausses)
    if not (disparus or nouveaux or sautes or degrades or baisses or justifiees or hausses or ameliores):
        v.lignes.append(f"    identique à la référence, nom par nom (collecte, issues, sous-tests)")


# --- commande ----------------------------------------------------------------------------------------------------------------------

def verifier(dossier, reference=None, commit="HEAD", suivi=None):
    dossier = os.path.abspath(dossier)
    reference = os.path.abspath(reference or os.path.join(RACINE, REFERENCE))
    print(f"verifier {dossier}")
    print(f"  référence : {os.path.relpath(reference, RACINE) if reference.startswith(RACINE) else reference}")
    requis = [os.path.join(dossier, "rapport.json")] + [os.path.join(d, f"{n}-{s}.txt") for d in (dossier, reference)
                                                         for s in comparer_listes.SUITES for n in ("collecte", "resultats")]
    manquants = [p for p in requis if not os.path.exists(p)]
    if manquants:
        for p in manquants:
            print(f"  fichier absent : {p}")
        print("VERDICT : REFUSÉ (code 2) : dossier de rapport ou de référence incomplet")
        return 2
    with open(os.path.join(dossier, "rapport.json"), encoding="utf-8") as fichier:
        rapport = json.load(fichier)
    print(f"  lancement : départ {court(rapport.get('head'))} ({rapport.get('branche')}), {rapport.get('debut')} -> {rapport.get('fin')}, "
          f"code {rapport.get('code')} ; Python {(rapport.get('python') or {}).get('duree_s')} s, "
          f"pages {(rapport.get('pages') or {}).get('duree_s')} s")

    v = Verification()
    verifier_commit(v, rapport, commit)
    verifier_codes(v, rapport)
    variables = comparer_listes.lire_variables(reference)
    justifications = Justifications(chemin_suivi(suivi, rapport))
    for suite in comparer_listes.SUITES:
        verifier_suite(v, dossier, reference, suite, rapport, variables, justifications)
    v.lignes.append(f"(d) suivi : {lisible(justifications.chemin)} : " + (justifications.erreur or
                    f"{justifications.nombre()} justification(s) de baisse de sous-tests"))
    v.lister("(d) ligne(s) de la section « Variations de sous-tests » hors format (sans effet)", justifications.incomprises)
    v.lister("(d) justification(s) sans baisse correspondante (sans effet)", justifications.sans_effet())

    for ligne in v.lignes:
        print("  " + ligne)
    print(f"  fichiers ignorés (docs/ ; CLAUDE.md hors du commit) : {len(v.ignores) or 'aucun'}")
    print("\n".join(coupe(v.ignores)) if v.ignores else "", end="\n" if v.ignores else "")
    for titre, elements in v.listes:
        print(f"  {titre} : {len(elements)}")
        print("\n".join(coupe(elements)))
    if v.refus:
        print(f"  MOTIFS DE REFUS : {len(v.refus)}")
        for motif, elements in v.refus:
            print(f"    - {motif}" + (f" : {len(elements)}" if elements else ""))
            if elements:
                print("\n".join(coupe(elements)))
        print(f"VERDICT : REFUSÉ (code 1) : {len(v.refus)} motif(s) ci-dessus")
        return 1
    print("VERDICT : ACCEPTÉ (code 0)")
    return 0


def main(argv):
    """argv : les arguments après `verifier`."""
    args = list(argv)
    options = {}
    for nom in ("--reference", "--commit", "--suivi"):
        if nom in args:
            i = args.index(nom)
            if i + 1 >= len(args):
                print(__doc__)
                return 2
            options[nom] = args[i + 1]
            del args[i:i + 2]
    if len(args) != 1 or args[0].startswith("--"):
        print(__doc__)
        return 2
    return verifier(args[0], options.get("--reference"), options.get("--commit", "HEAD"), options.get("--suivi"))
