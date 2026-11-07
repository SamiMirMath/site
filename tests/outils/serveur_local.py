"""Serveur local du moteur, sans gunicorn (chantier moteur-serveur, P1) : l'application de serveur/app.py servie par
wsgiref.simple_server sur 127.0.0.1, pour `dump_sorties.py --serveur` (et, en P3, les essais des pages).

    python3 tests/outils/serveur_local.py [--port N]

Le script se relance sous la commande `uv` de tests/lancer.py (Python 3.12, SymPy 1.13.3, mpmath 1.3.0), avec PYTHONHASHSEED=0.
Port 0 par défaut : le système en choisit un libre. Une fois l'application chargée (préchargement de tous les modules du manifeste),
il écrit une ligne « serveur_local : http://127.0.0.1:<port> » sur la sortie standard, puis sert jusqu'à Ctrl-C ou SIGTERM.

Un seul calcul à la fois, comme un processus synchrone de gunicorn (jamais de fils : état de module, `random`). Aucun journal
d'accès (T14) ; les erreurs de l'application vont sur la sortie d'erreur (journal « serveur »). Les variables MOTEUR_VERSION et
MOTEUR_ETAT de /api/sante sont lues dans l'environnement : absentes, /api/sante répond 503 (les calculs, eux, répondent).

Ce fichier ne s'appelle pas test_*.py : ni pytest ni unittest ne le collectent."""
import importlib.util
import os
import sys

ICI = os.path.dirname(os.path.abspath(__file__))
RACINE = os.path.abspath(os.path.join(ICI, "..", ".."))
APP = os.path.join(RACINE, "serveur", "app.py")
FILE_D_ATTENTE = 64            # connexions en attente (5 par défaut dans socketserver) : les processus du dump attendent leur tour


def relancer_sous_uv(argv):
    """Remplace ce processus par `uv run … python serveur_local.py` (exec : même PID, donc SIGTERM ou Ctrl-C atteint uv, qui le
    transmet au serveur ; aucun processus ne reste derrière un `kill` du lanceur)."""
    sys.path.insert(0, os.path.join(RACINE, "tests"))
    import lancer
    uv = lancer.UV[:lancer.UV.index("python") + 1]
    env = dict(os.environ, SERVEUR_LOCAL_UV="1", PYTHONHASHSEED="0")
    os.chdir(RACINE)
    os.execvpe(uv[0], uv + [os.path.abspath(__file__)] + argv, env)


def charger_application():
    spec = importlib.util.spec_from_file_location("app", APP)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.application


def principal(argv):
    port = 0
    if len(argv) == 2 and argv[0] == "--port" and argv[1].isdigit():
        port = int(argv[1])
    elif argv:
        print("usage : python3 tests/outils/serveur_local.py [--port N]", file=sys.stderr)
        return 2
    if os.environ.get("SERVEUR_LOCAL_UV") != "1":
        return relancer_sous_uv(argv)

    from wsgiref.simple_server import WSGIRequestHandler, WSGIServer, make_server

    class Gestionnaire(WSGIRequestHandler):
        def log_message(self, *args):          # aucun journal d'accès (T14)
            pass

    class Serveur(WSGIServer):
        request_queue_size = FILE_D_ATTENTE

    application = charger_application()
    with make_server("127.0.0.1", port, application, server_class=Serveur, handler_class=Gestionnaire) as serveur:
        print(f"serveur_local : http://127.0.0.1:{serveur.server_port}", flush=True)
        try:
            serveur.serve_forever()
        except KeyboardInterrupt:
            pass
    return 0


if __name__ == "__main__":
    sys.exit(principal(sys.argv[1:]))
