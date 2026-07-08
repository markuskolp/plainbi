# gunicorn config for the plainbi FastAPI backend, replacing the old uWSGI .ini files.
# start with: gunicorn -c gunicorn.conf.py "plainbi_backend.api:create_app()"
import os

# defaults match the combined nginx+backend deployment (nginx proxies to 127.0.0.1
# from inside the same container/network namespace); override via env vars for a
# standalone backend container, e.g. GUNICORN_BIND=0.0.0.0:3001 so it's reachable
# from outside the container
bind = os.environ.get("GUNICORN_BIND", "127.0.0.1:3001")
workers = int(os.environ.get("GUNICORN_WORKERS", "4"))
worker_class = "uvicorn.workers.UvicornWorker"


def post_fork(server, worker):
    """
    Defensive only: we do NOT run gunicorn with --preload, so each worker process
    imports plainbi_backend.api fresh after fork and create_app() builds its own
    config.repoengine/config.dbengine from scratch - there is nothing inherited from
    the master process to dispose of in that mode. This hook is kept as the standard
    SQLAlchemy+gunicorn safety net in case --preload is ever enabled later.
    """
    try:
        from plainbi_backend.config import config
        if hasattr(config, "repoengine"):
            config.repoengine.dispose()
        if hasattr(config, "dbengine"):
            config.dbengine.dispose()
    except Exception:
        pass
