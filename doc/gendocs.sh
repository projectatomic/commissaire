#!/bin/bash
set -xeuo pipefail
rm -rf _build
rm -rf apidoc
sphinx-apidoc -T -e -o apidoc ../src/commissaire/
if [ -d "../../commissaire-service/" ]; then
  sphinx-apidoc -T -e -o apidoc ../../commissaire-service/src/commissaire_service/
fi
if [ -d "../../commissaire-http/" ]; then
  sphinx-apidoc -T -e -o apidoc ../../commissaire-http/src/commissaire_http/
fi

sphinx-build -b html . _build
