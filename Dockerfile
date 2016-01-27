FROM fedora
MAINTAINER Red Hat, Inc. <container-tools@redhat.com>

RUN dnf -y update && dnf -y install --setopt=tsflags=nodocs redhat-rpm-config python-pip python-virtualenv git gcc libffi-devel && dnf clean all

ENV MHM_RELEASE v0.0.0
ENV PYTHONPATH  /commissaire/src/

RUN git clone https://github.com/projectatomic/commissaire.git && \
cd commissaire && \
pip install -U pip && \
pip install -r requirements.txt && \
pip freeze > /installed-python-deps.txt

EXPOSE 8000
WORKDIR /commissaire
CMD python src/commissaire/script.py ${ETCD}
