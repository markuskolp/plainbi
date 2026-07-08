# Plainbi Backend Documentation

The backend is a FastAPI application (`plainbi_backend/api.py`) served by gunicorn/uvicorn in
production, behind nginx. It talks to a "repository" database (holds users, groups, applications,
adhocs, lookups, audit trail, ...) and to one or more "datasource" databases that hold the actual
business data exposed via the generic CRUD endpoints.

## How to start the application

### Local development

```
cd backend
pip install -r requirements.txt
python plainbi_backend.py -v
```

`plainbi_backend.py` is the standalone entry point. It reads configuration the same way the
production app does (see [Environment variables](#environment-variables)) and then runs a plain
`uvicorn.run(...)` dev server (single process, auto-reload disabled). Useful CLI flags:

| Flag | Purpose |
|---|---|
| `-v`, `-vv`, `-vvv` | verbose/debug mode, increasing detail (sets `PLAINBI_VERBOSE`) |
| `-c <file>` | path to a config file (`.env` format) to load |
| `-l <file>` | override the logfile path |
| `-P <port>` | override the port |
| `-d <connstr>` | override `PLAINBI_DATABASE` |
| `-r <connstr>` | override `PLAINBI_REPOSITORY` |
| `-V` | print the backend version and exit |
| `-I` | initialize the repository schema (creates all `plainbi_*` tables) and exit |
| `-u <username> -p <password>` | set/reset a local user's password and exit |
| `-t <connstr>` | test a sqlalchemy connection string and exit |
| `-b <id> <path>` | base64-encode a file into `plainbi_static_file` (e.g. a logo) and exit |

Interactive API docs (Swagger UI) are available at `http://localhost:3001/docs` once running, and
the raw OpenAPI schema at `/openapi.json`.

### Production

Production runs gunicorn with uvicorn workers, in front of which nginx serves the React frontend
and reverse-proxies `/api`, `/login`, `/profile` to the backend:

```
gunicorn -c backend/gunicorn.conf.py "plainbi_backend.api:create_app()"
```

`gunicorn.conf.py` binds `127.0.0.1:3001` with 4 workers by default (override via `GUNICORN_BIND` /
`GUNICORN_WORKERS`). This is what `supervisord.conf` runs inside the combined Docker image (see
repo-root `Dockerfile`, `nginx_plainbi.conf`, `supervisord.conf`), where nginx reverse-proxies to
`127.0.0.1:3001` from inside the same container. Because each gunicorn worker is a separate process,
**`PLAINBI_JWT_SECRET` must be set** to a stable value in production, otherwise every worker
generates its own random JWT signing secret and login tokens only validate on whichever worker
issued them (see below).

### Standalone backend container (no nginx)

nginx is not required to run the backend - gunicorn/uvicorn can serve traffic directly. Use
`backend/Dockerfile` (build context is the `backend/` folder itself):

```
cd backend
podman build -t plainbi-backend .
podman run -p 3001:3001 \
  -e PLAINBI_REPOSITORY="sqlite:////data/plainbi_repo.db" \
  -e PLAINBI_JWT_SECRET="$(openssl rand -hex 32)" \
  -e PLAINBI_CORS_ORIGINS="https://myfrontend.example.com" \
  -v /some/local/dir:/data \
  plainbi-backend
```

The image sets `GUNICORN_BIND=0.0.0.0:3001` so the container's port mapping can reach it (the
combined deployment uses `127.0.0.1:3001` instead, since nginx sits in the same container/network
namespace). The one thing nginx was doing that gunicorn/uvicorn alone does not is making the
frontend and backend same-origin - if they're served from different origins, set
`PLAINBI_CORS_ORIGINS` (see below), otherwise the default (`*`, any origin) applies. Secrets and
connection strings are intentionally not baked into the image - always pass them via `-e` (or
`--env-file`) at `podman run` time.

## Environment variables

Loaded from (in order of precedence): `PLAINBI_BACKEND_CONFIG` file if set, else the first of
`.env`, `~/.env`, `/etc/plainbi.env` that exists, else process environment only.

### Core / repository

| Variable | Purpose |
|---|---|
| `PLAINBI_BACKEND_CONFIG` | path to a config file (`.env` format) to load explicitly |
| `PLAINBI_REPOSITORY` | sqlalchemy connect string for the repository database (sqlite/mssql/postgres/oracle). Required unless `PLAINBI_SIMPLE_MODE_CONNECT` is set |
| `PLAINBI_DATABASE` | optional default datasource connect string for the CRUD API; if unset, falls back to `plainbi_datasource` row with id=1 from the repository |
| `PLAINBI_SIMPLE_MODE_CONNECT` | see [Simple mode](#simple-mode) below |
| `PLAINBI_BACKEND_HOST` | host to bind to (default `0.0.0.0`) |
| `PLAINBI_BACKEND_PORT` | port to bind to (default `3001`) |
| `PLAINBI_JWT_SECRET` | stable secret for signing/verifying JWT login tokens - **required in any multi-process/multi-worker deployment** (gunicorn/uvicorn with >1 worker); if unset, a random secret is generated per process and tokens won't validate across workers |
| `PLAINBI_BACKEND_DATE_FORMAT` | date format used when formatting date columns for output |
| `PLAINBI_BACKEND_DATETIME_FORMAT` | datetime format used when formatting datetime columns for output |
| `PLAINBI_METADATA_CACHE` | `yes`/`true` to enable table-metadata caching (default enabled) |
| `PLAINBI_METADATA_CACHE_TTL` | metadata cache TTL in seconds (default `300`) |
| `PLAINBI_CORS_ORIGINS` | comma-separated CORS allowlist, or `*` (default). Only matters when the frontend isn't served same-origin behind nginx |
| `GUNICORN_BIND` | gunicorn bind address (default `127.0.0.1:3001`; the standalone Dockerfile sets `0.0.0.0:3001`) |
| `GUNICORN_WORKERS` | gunicorn worker process count (default `4`) |
| `PLAINBI_METRICS_DISK_PATH` | filesystem path `/metrics/system` reports disk usage for (default `/`) |

### Logging / debugging

See [Debugging](#debugging--logging) below for how these interact with the runtime `/api/loglevel` endpoint.

| Variable | Purpose |
|---|---|
| `PLAINBI_VERBOSE` | `1`/`2`/`3`, sets debug mode on and the initial debug verbosity level (takes priority over `PLAINBI_BACKEND_LOG_DEBUG`) |
| `PLAINBI_BACKEND_LOG_DEBUG` | `true` to run in debug mode (equivalent to `PLAINBI_VERBOSE=1`) |
| `PLAINBI_BACKEND_LOGFILE` | path to the logfile (in a container, point this at a mounted volume); if unset, logs only go to stdout/stderr |
| `PLAINBI_BACKEND_LOG_ROTATE_WHEN` | rotation interval for the logfile: `midnight` (default), `H`, `D`, `W0`.. see Python's `TimedRotatingFileHandler` docs |
| `PLAINBI_BACKEND_LOG_BACKUP_COUNT` | how many rotated logfiles to keep (default `14`) |

### SSO (Microsoft Entra ID / Azure AD)

| Variable | Purpose |
|---|---|
| `PLAINBI_SSO_APPLICATION_ID` | Azure AD application (client) ID; if unset, SSO login is disabled entirely |
| `PLAINBI_SSO_TENANTID` | Azure AD tenant ID |
| `PLAINBI_SSO_CLIENT_SECRET` | Azure AD client secret |
| `PLAINBI_SSO_AUTHORITY` | Azure AD authority URL |
| `PLAINBI_SSO_REDIRECT_PATH` | OAuth2 redirect URI registered in the Azure AD app |
| `PLAINBI_SSO_APPLIKATION` | (legacy, read but not currently used) |

### LDAP / Active Directory

If `LDAP_HOST` is set, login attempts try LDAP first, then fall back to local (repository)
authentication.

| Variable | Purpose |
|---|---|
| `LDAP_HOST` | LDAP/AD server hostname |
| `LDAP_PORT` | LDAP/AD server port |
| `LDAP_BIND_USER_DN` | service account DN used to bind and search |
| `LDAP_BIND_USER_PASSWORD` | service account password |
| `LDAP_BASE_DN` | search base DN |
| `LDAP_SEARCH_EXPR` | optional custom search filter, `{username}` is substituted |

### Email (`/api/email`)

| Variable | Purpose |
|---|---|
| `SMTP_SERVER` | SMTP server hostname |
| `SMTP_PORT` | SMTP server port |
| `SMTP_USER` | SMTP username / from-address |
| `SMTP_PASSWORD` | SMTP password (omit/leave empty for an unauthenticated relay) |

## Simple mode

Set `PLAINBI_SIMPLE_MODE_CONNECT` to a sqlalchemy connection string to run the backend **without a
repository and without authentication at all** - only the generic CRUD endpoints
(`/api/crud/...`, `/api/metadata/...`) work, straight against that one connection, and every request
succeeds without an `Authorization` header. This is meant for quick, throwaway setups (demos, local
prototyping) where standing up a full repository is unnecessary overhead.

```
PLAINBI_SIMPLE_MODE_CONNECT="sqlite:////path/to/my.db"
```

Notes:
- `PLAINBI_REPOSITORY` becomes optional and is ignored if `PLAINBI_SIMPLE_MODE_CONNECT` is set.
- Every CRUD request runs against this single connection regardless of the `{db}` path segment
  (there's no `plainbi_datasource` table to resolve aliases against).
- There's no audit trail in this mode (nothing to write `plainbi_audit` rows into).
- Repository-backed endpoints (login, profile, adhoc, lookup, settings, `/api/repo/...`) do not
  work in this mode and will return errors if called - this is expected, not a bug.

## Endpoints

All routes below are registered both with and without the leading `/api` where two paths are shown
(matching what the frontend/nginx already expects). "Auth" = requires a valid `Authorization` header
(raw token or `Bearer <token>`); tokens are issued by `/login`/`/login_sso`.

### Misc / status

| Method | Path | Auth | Purpose |
|---|---|---|---|
| GET | `/` | - | HTML welcome page |
| GET | `/version`, `/api/version` | - | backend version string |
| GET | `/api/backend_version`, `/api/db_version`, `/api/dbversion` | - | backend + repository DB version |
| GET | `/api/loglevel/{loglevel}` | - | change log level at runtime, see [Debugging](#debugging--logging) |
| GET | `/status`, `/api/status` | - | status/diagnostics page (loggers, versions, current log levels) |

### Operational / monitoring

Deliberately at bare paths (no `/api` prefix) since these are meant to be probed directly on the
backend's own port (container orchestrator health checks, Zabbix or similar) - `nginx_plainbi.conf`
does not proxy them, so they won't resolve through the public frontend-fronted URL, only directly
against the backend.

| Method | Path | Auth | Purpose |
|---|---|---|---|
| GET | `/ping` | - | fastest possible check - returns plaintext `pong`, no logic, no dependency checks |
| GET | `/health` | - | liveness probe - process/event-loop is up and responding. No dependency checks (see `/health/ready` for those) |
| GET | `/health/ready` | - | readiness probe - checks repository/datasource connectivity; returns `503` if any configured dependency fails |
| GET | `/metrics/system` | - | CPU/RAM/disk/process stats as flat JSON, meant for Zabbix HTTP-agent items via JSONPath (`$.cpu_percent`, `$.memory_percent`, ...); disk path defaults to `/`, override with `PLAINBI_METRICS_DISK_PATH` |

### Utils

| Method | Path | Auth | Purpose |
|---|---|---|---|
| POST | `/api/email` | Auth | send an SMTP email |
| GET | `/api/distinctvalues/{db}/{tabnam}/{colnam}` | Auth | distinct values of a column (for filter dropdowns) |
| POST | `/api/exec/{db}/{procname}` | Auth | execute a stored procedure (MSSQL only) |

### CRUD (generic, against any configured datasource)

`{db}` is a `plainbi_datasource` id or alias (`0`/`repo` = the repository itself). `{tab}` is a
table name, or an id/alias of a `plainbi_customsql` definition if `?customsql=` is used. `{pk}` is
the primary key value(s) (comma-separated for compound keys, or `[base64@...]`-wrapped, or `#`/`@`
to read the pk from the request body instead of the URL).

| Method | Path | Auth | Purpose |
|---|---|---|---|
| GET | `/api/crud/{db}/{tab}` | Auth | list rows (supports `q`, `filter`, `offset`, `limit`, `order_by`, `cols`, `v` (versioned), `customsql`, `format=XLSX\|CSV\|TXT` for downloads) |
| GET | `/api/crud/{db}/{tab}/{pk}` | Auth | get one row |
| POST | `/api/crud/{db}/{tab}/{pk}` | Auth | get one row, with the pk read from the request body |
| POST | `/api/crud/{db}/{tab}` | Auth | insert a row (`?seq=`, `?usercol=`, `?pk=`, `?v` for versioned tables) |
| PUT | `/api/crud/{db}/{tab}/{pk}` | Auth | update a row (returns only the PK columns of the updated row, not the full row) |
| DELETE | `/api/crud/{db}/{tab}/{pk}` | Auth | delete a row (soft-delete/new-version for versioned tables) |

### Metadata

| Method | Path | Auth | Purpose |
|---|---|---|---|
| GET | `/api/metadata/{db}/tables` | Auth | list tables in a datasource |
| GET | `/api/metadata/{db}/table/{tab}` | Auth | column metadata for a table |

### Repository (`plainbi_*` tables)

| Method | Path | Auth | Purpose |
|---|---|---|---|
| GET | `/api/repo/resources` | Auth | applications/adhocs/external resources visible to the current user |
| GET | `/api/repo/groups` | Auth | groups the current user belongs to |
| GET | `/api/repo/group/{gid}/resources` | Auth | resources scoped to one group (`gid="nogroup"` = ungrouped, admins only) |
| GET | `/api/repo/{tab}` | Auth | list rows of repo table `plainbi_{tab}` |
| GET | `/api/repo/{tab}/{pk}` | Auth | get one row from `plainbi_{tab}` |
| POST | `/api/repo/{tab}` | Auth | insert into `plainbi_{tab}` |
| PUT | `/api/repo/{tab}/{pk}` | Auth | update a row in `plainbi_{tab}` |
| DELETE | `/api/repo/{tab}/{pk}` | Auth | delete a row in `plainbi_{tab}` |
| GET | `/api/repo/init_repo` | - | (re-)initialize the repository schema - **handle with care** |
| GET | `/api/repo/application/{appid}/dsdb` | - (unauthenticated by design) | export an application as a `.dsdb` deployment file |
| GET | `/api/repo/lookup/{lkpid}/dsdb` | - (unauthenticated by design) | export a lookup as a `.dsdb` deployment file |

### Lookup

| Method | Path | Auth | Purpose |
|---|---|---|---|
| GET | `/api/repo/lookup/{id}/data` | Auth | resolve a lookup's data (id or alias), supports `q`, `offset`, `limit`, `order_by`, `selected` |

### Adhoc

| Method | Path | Auth | Purpose |
|---|---|---|---|
| GET | `/api/repo/adhoc/{id}/distinctvalues/{colnam}` | Auth | distinct values of a column in an adhoc's result |
| GET, POST | `/api/repo/adhoc/{id}/data` | Auth | run an adhoc's SQL (`?params=`, `?format=JSON\|XLSX\|CSV\|TXT`, `?filter=`, pagination) |

### Authentication

| Method | Path | Auth | Purpose |
|---|---|---|---|
| POST | `/login`, `/api/login` | - | local/LDAP login, returns a JWT `access_token` |
| POST | `/login_sso`, `/api/login_sso` | - | Microsoft Entra ID SSO login |
| POST | `/passwd`, `/api/passwd` | Auth | change a local user's password (admins can change any user's) |
| GET | `/hash_passwd/{pwd}`, `/api/hash_passwd/{pwd}` | - | show the bcrypt hash of a password (testing helper) |
| GET | `/protected`, `/api/protected` | Auth | returns the current username - smoke-test a token |
| GET | `/profile`, `/api/profile` | Auth | current user's profile (roles, groups) |
| GET | `/logout`, `/api/logout` | Auth | logout (stateless - no token blacklist, just a no-op confirmation) |

### Cache

| Method | Path | Auth | Purpose |
|---|---|---|---|
| GET | `/cache`, `/api/cache` | Auth | `?on`/`?off`/`?clear`/`?status` - toggle or inspect metadata/profile caching |
| GET | `/clear_cache`, `/api/clear_cache` | Auth | clear metadata + profile caches |

### Static / settings

| Method | Path | Auth | Purpose |
|---|---|---|---|
| GET | `/api/static/{id}`, `/static/{id}` | - | serve a base64-stored static asset (e.g. logo) by id or alias, no login required |
| GET | `/api/settings.js` | - | frontend settings as a JS snippet (title, colors, SSO sign-in link, ...) |
| GET | `/api/settings` | - | all `plainbi_settings` rows as JSON |
| GET | `/api/setting/{name}` | - | one named setting |

## Debugging / logging

Logging uses Python's standard `logging` module (no loguru or similar - deliberately kept on the
stdlib to avoid touching the hundreds of existing `dbg()`/`err()`/`warn()` call sites). Two things
worth knowing:

**Per-module runtime control.** Every `dbg()`/`err()`/`warn()` call logs through the logger named
after *its own calling module* (`plainbi_backend.api`, `plainbi_backend.db`, `plainbi_backend.utils`,
`plainbi_backend.repo`, ...) - not a single shared logger. That means you can turn up verbosity for
one module while leaving everything else alone, at runtime, with no restart:

```
# turn on the most verbose tracing for db.py only, leave everything else as-is
curl "http://localhost:3001/api/loglevel/DEBUG3?loggers=plainbi_backend.db"

# reset everything back to one global level (also clears all per-module overrides)
curl "http://localhost:3001/api/loglevel/INFO"
```

Valid `{loglevel}` values: `INFO`, `DEBUG`, `DEBUG1` (all equivalent to verbosity level 1),
`DEBUG2`, `DEBUG3` (most verbose - includes a full call-stack trace prefix on every debug line).
`?loggers=` accepts a comma-separated list of logger/module names; omit it to change the level
everywhere and drop any per-module overrides currently in effect.

Check current state (per-logger effective level, plus any active per-module overrides) via:

```
curl "http://localhost:3001/api/status"
```

**Log destinations and rotation.** Logs always go to stdout/stderr. If `PLAINBI_BACKEND_LOGFILE`
is set, they're also written there via a `TimedRotatingFileHandler` (rotates at midnight by
default, keeps 14 backups by default - see `PLAINBI_BACKEND_LOG_ROTATE_WHEN` /
`PLAINBI_BACKEND_LOG_BACKUP_COUNT` above to change either). Note that in a multi-worker gunicorn
deployment, each worker process writes to the same logfile path independently - fine for
append-only line writes, but be aware if you're tailing it and see interleaved output from
multiple workers.

**Start already-verbose from the CLI**: `python plainbi_backend.py -v` / `-vv` / `-vvv` (sets
`PLAINBI_VERBOSE`), or set `PLAINBI_BACKEND_LOG_DEBUG=true` for the equivalent of `-v`.

## Datasource Konfiguration

We configure the datasource for application and adhoc reports in the repository table "plainbi_datasource"

Column db_type can be

- mssql
- sqlite: then put the file nam ein "db_host"
- oracle: then use {db_user}:{db_pass}@{db_host}:{db_port}/{db_name}"
- postgres: then postgresql+psycopg2://{db_user}{db_user}:{db_pass}@{host}/{db_name}
- or any valid sqlalchemy connect string

For snowflake the sqlalchemy connect string for example is
snowflake://plainbi_dev@mmg-dwh/?warehouse=devtest_xs&database=dwh_dev&schema=PUBLIC&role=PUBLIC&authenticator=SNOWFLAKE_JWT&private_key=<a very long key>
<a very long key> is the output of 
```
def get_snowflake_private_key(pem_file_path):
    with open(pem_file_path, 'rb') as key_file:
        private_key = key_file.read()
    p_key = serialization.load_pem_private_key(private_key,password=None)
    der_key = p_key.private_bytes(encoding=serialization.Encoding.DER,format=serialization.PrivateFormat.PKCS8,encryption_algorithm=serialization.NoEncryption())
    base64_key = base64.b64encode(der_key).decode('ascii')
    base64_key = base64_key.replace('\n', '')
    while len(base64_key) % 4 != 0:
        base64_key += '='
    return  urllib.parse.quote_plus(base64_key)
```

## Local dev repo (Postgres via podman)

```
podman run -d --name plainbi_postgres -e POSTGRES_PASSWORD=plainbi -v /home/e10002068/Projects/plainbi_home/pgdata:/var/lib/postgresql/data -p 5432:5432 postgres

PGPASSWORD=plainbi psql -h localhost -p 5432 -U postgres
```

Uses image `docker.io/library/postgres:latest`.
