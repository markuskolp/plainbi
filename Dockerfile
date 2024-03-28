FROM almalinux:8

# Set environment variables
ENV PYTHON_VERSION=3.11

# Install necessary dependencies
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
    nginx \
    gcc \
    unzip \
    && dnf clean all

WORKDIR /opt/app/portal
RUN mkdir -p /opt/app/portal/backend
RUN mkdir -p /opt/app/portal/backend/plainbi_backend
RUN mkdir -p /opt/app/portal/frontend
RUN mkdir -p /opt/app/portal/logs

COPY backend/* /opt/app/portal/backend
COPY backend/plainbi_backend/* /opt/app/portal/backend/plainbi_backend
COPY frontend/* /opt/app/portal/frontend
COPY supervisord.conf /etc/supervisord.conf

RUN curl -o /opt/app/portal/installclient.zip https://download.oracle.com/otn_software/linux/instantclient/2112000/instantclient-basic-linux.x64-21.12.0.0.0dbru.zip
RUN unzip /opt/app/portal/installclient.zip -d /opt/app/portal

RUN pip${PYTHON_VERSION} install -r backend/requirements.txt

RUN pip${PYTHON_VERSION} install supervisor

# replace nginx configuration
COPY nginx_plainbi.conf /etc/nginx/nginx.conf
COPY frontend/build/* /usr/share/nginx/html
RUN mkdir -p /usr/share/nginx/html/static
COPY frontend/build/static/* /usr/share/nginx/html/static
RUN mkdir -p /usr/share/nginx/html/static/css
COPY frontend/build/static/css/* /usr/share/nginx/html/static/css
RUN mkdir -p /usr/share/nginx/html/static/js
COPY frontend/build/static/js/* /usr/share/nginx/html/static/js

# Expose ports
EXPOSE 80
#EXPOSE 3001

ENV PYTHONPATH="/opt/app/portal/backend"
ENV PLAINBI_BACKEND_LOGFILE="/opt/app/portal/logs/plainbi_backend.log"
ENV PLAINBI_BACKEND_LOG_DEBUG="true"

#STOPSIGNAL SIGTERM
#CMD ["nginx", "-g", "daemon off;"]
#CMD python3 /opt/app/portal/backend/plainbi_backend.py -v
CMD ["supervisord", "-n"]


