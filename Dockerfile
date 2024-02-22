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
COPY backend/* /opt/app/portal/backend
COPY backend/plainbi_backend/* /opt/app/portal/backend/plainbi_backend
COPY frontend/* /opt/app/portal/frontend

RUN curl -o /opt/app/portal/installclient.zip https://download.oracle.com/otn_software/linux/instantclient/2112000/instantclient-basic-linux.x64-21.12.0.0.0dbru.zip
RUN unzip /opt/app/portal/installclient.zip -d /opt/app/portal


RUN pip${PYTHON_VERSION} install -r backend/requirements.txt

# Expose ports
EXPOSE 80
EXPOSE 3001

ENV PYTHONPATH="/opt/app/portal/backend"

#STOPSIGNAL SIGTERM
#CMD ["nginx", "-g", "daemon off;"]

#CMD ["env"]

CMD python3 /opt/app/portal/backend/plainbi_backend.py -v


