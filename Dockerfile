FROM fedora
MAINTAINER Red Hat, Inc. <container-tools@redhat.com>

ENV MHM_RELEASE v0.0.1rc3
ENV PYTHONPATH  /commissaire/src/
ENV EXTRA_ARGS  ""

# Install required dependencies and commissaire
RUN dnf -y update && dnf -y install --setopt=tsflags=nodocs rsync openssh-clients redhat-rpm-config python-pip python-virtualenv git gcc libffi-devel ; dnf clean all && \
git clone https://github.com/projectatomic/commissaire.git && \
virtualenv /environment && \
. /environment/bin/activate && \
cd commissaire && \
pip install -U pip && \
pip install -r requirements.txt && \
pip freeze > /installed-python-deps.txt  && \
dnf remove -y gcc git redhat-rpm-config libffi-devel && dnf clean all

EXPOSE 8000
WORKDIR /commissaire
CMD . /environment/bin/activate && python src/commissaire/script.py -e ${ETCD} -k ${KUBE} ${EXTRA_ARGS}
