# Dockerfile for PlainBI backend (standalone, no nginx/frontend) - build context is
# this backend/ folder itself, e.g.: cd backend && podman build -t plainbi-backend .
FROM almalinux:8

# Set environment variables
ENV PYTHON_VERSION=3.11

# Install necessary dependencies (DB client libs for mssql/postgres/mysql drivers,
# gcc/pkgconfig to build the wheels that need it - no nginx, this is backend-only)
RUN dnf install -y \
    python${PYTHON_VERSION} \
    python${PYTHON_VERSION}-pip\
    python${PYTHON_VERSION}-devel\
    procps \
    pkgconfig \
    mariadb-devel \
    postgresql \
    libpq \
    libpq-devel \
    gcc \
    unzip \
    && dnf clean all

WORKDIR /opt/app/portal
RUN mkdir -p /opt/app/portal/backend
RUN mkdir -p /opt/app/portal/backend/plainbi_backend
RUN mkdir -p /opt/app/portal/logs

COPY * /opt/app/portal/backend
COPY plainbi_backend/* /opt/app/portal/backend/plainbi_backend

RUN curl -o /opt/app/portal/installclient.zip https://download.oracle.com/otn_software/linux/instantclient/2112000/instantclient-basic-linux.x64-21.12.0.0.0dbru.zip
RUN unzip /opt/app/portal/installclient.zip -d /opt/app/portal

RUN pip${PYTHON_VERSION} install -r backend/requirements.txt

WORKDIR /opt/app/portal/backend

EXPOSE 3001

ENV PYTHONPATH="/opt/app/portal/backend"
ENV PLAINBI_BACKEND_LOGFILE="/opt/app/portal/logs/plainbi_backend.log"
ENV PLAINBI_BACKEND_LOG_DEBUG="true"
ENV PLAINBI_BACKEND_DATE_FORMAT="%Y-%m-%d"
ENV PLAINBI_BACKEND_DATETIME_FORMAT="%Y-%m-%d %H:%M:%S"
# bind to all interfaces so the container's port mapping can reach it - the
# combined nginx+backend deployment overrides this back to 127.0.0.1 instead
ENV GUNICORN_BIND="0.0.0.0:3001"

# secrets/connection strings (PLAINBI_REPOSITORY, PLAINBI_SIMPLE_MODE_CONNECT,
# PLAINBI_JWT_SECRET, PLAINBI_CORS_ORIGINS, ...) are deliberately NOT set here -
# pass them at `podman run -e ...` time instead of baking them into the image

CMD ["gunicorn", "-c", "gunicorn.conf.py", "plainbi_backend.api:create_app()"]


