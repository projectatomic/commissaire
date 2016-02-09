FROM fedora
MAINTAINER Red Hat, Inc. <container-tools@redhat.com>

RUN dnf -y update && dnf -y install --setopt=tsflags=nodocs rsync openssh-clients redhat-rpm-config python-pip python-virtualenv git gcc libffi-devel ; dnf clean all

ENV MHM_RELEASE v0.0.0
ENV PYTHONPATH  /commissaire/src/

# TODO: Pull a release?
RUN git clone https://github.com/projectatomic/commissaire.git && \
virtualenv /environment && \
. /environment/bin/activate && \
cd commissaire && \
pip install -U pip && \
pip install -r requirements.txt && \
pip freeze > /installed-python-deps.txt

# Clean up
RUN dnf remove -y gcc git redhat-rpm-config libffi-devel && dnf clean all

EXPOSE 8000
WORKDIR /commissaire
CMD . /environment/bin/activate && python src/commissaire/script.py ${ETCD}
