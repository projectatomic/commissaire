FROM fedora:25
MAINTAINER Red Hat, Inc. <container-tools@redhat.com>

ENV MHM_RELEASE v0.1.0
ENV PYTHONPATH  /commissaire/src/

# Install required dependencies and commissaire
RUN dnf -y update && dnf -y install --setopt=tsflags=nodocs rsync openssh-clients redhat-rpm-config python3-pip python3-virtualenv git gcc libffi-devel openssl-devel etcd redis; dnf clean all && \
git clone https://github.com/projectatomic/commissaire-service.git && \
git clone https://github.com/projectatomic/commissaire-http.git && \
virtualenv-3 /environment && \
. /environment/bin/activate && \
cd commissaire-service && \
pip install -U pip && \
pip install -r requirements.txt && \
pip install . && \
cd ../commissaire-http && \
pip install -r requirements.txt && \
pip install . && \
cd .. && \
pip freeze > /installed-python-deps.txt && \
dnf remove -y gcc git redhat-rpm-config libffi-devel && \
dnf clean all && \
mkdir -p /etc/commissaire

# Add the all-in-one start script
ADD tools/startup-all-in-one.sh /commissaire/
# Add the etcd init script
ADD tools/etcd_init.sh /commissaire/

# Configuration directory. Use --volume=/path/to/your/configs:/etc/commissaire
VOLUME /etc/commissaire/

# commissaire-server address
EXPOSE 8000
WORKDIR /commissaire
CMD /commissaire/startup-all-in-one.sh
