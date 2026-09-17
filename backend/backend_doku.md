# Plainbi Backend Documentation

## postgres repo lokal (podman)
podman run -d --name plainbi_postgres -e POSTGRES_PASSWORD=plainbi -v /home/e10002068/Projects/plainbi_home/pgdata:/var/lib/postgresql/data -p 5432:5432 postgres


PGPASSWORD=plainbi psql -h localhost -p 5432 -U postgres

Use repo docker.io/library/postgres:latest

## Environment variables

Siehe README.md ("Backend configuration") für die vollständige, aktuelle Liste.

## Endpoints

Siehe endpoints.md für die vollständige, aktuelle Liste aller REST-Endpoints.

## Datasource Konfiguration

We configure the datasource for application and adhoc reports in the repository table "plainbi_datasource"

Column db_type can be

- mssql
- sqlite: then put the file name in "db_host"
- oracle: then use {db_user}:{db_pass}@{db_host}:{db_port}/{db_name}"
- postgres: then postgresql+psycopg2://{db_user}{db_user}:{db_pass}@{host}/{db_name}
- snowflake: siehe README.md ("Snowflake connection handling") für Connection-String-Format und Private-Key-Generierung
- or any valid sqlalchemy connect string
