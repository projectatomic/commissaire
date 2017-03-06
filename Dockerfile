FROM fedora:25
MAINTAINER Red Hat, Inc. <container-tools@redhat.com>

# Install required dependencies and commissaire
RUN dnf -y update && dnf -y install --setopt=tsflags=nodocs openssh-clients redhat-rpm-config python3-pip python3-virtualenv git gcc libffi-devel openssl-devel etcd redis; dnf clean all && \
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
sed -i 's|dir /var/lib/redis|dir /data/redis|g' /etc/redis.conf && \
mkdir -p /etc/commissaire /data/{redis,etcd}

# Copy the all-in-one start script
COPY tools/startup-all-in-one.sh /commissaire/
# Copy the etcd init script
COPY tools/etcd_init.sh /commissaire/

# Configuration directory. Use --volume=/path/to/your/configs:/etc/commissaire
VOLUME /etc/commissaire/
# Directory for data
VOLUME /data

# commissaire-server address
EXPOSE 8000
# Run everything from /commissaire
WORKDIR /commissaire
# Execute the all-in-one-script
CMD /commissaire/startup-all-in-one.sh
