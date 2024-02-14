# Plainbi Backend Documentation


## postgres repo lokal
podman run -d --name plainbi_postgres -e POSTGRES_PASSWORD=plainbi -v /home/e10002068/Projects/plainbi_home/pgdata:/var/lib/postgresql/data -p 5432:5432 postgres


PGPASSWORD=plainbi psql -h localhost -p 5432 -U postgres

Use repo docker.io/library/postgres:latest

