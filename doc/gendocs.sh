#!/bin/bash
#
# If you want to regenerate service and http apidocs as well, the repositories must be cloned
# in a common parent directory, and the repository directories must be named
# "commissaire-service" and "commissaire-http".

set -xeuo pipefail

rm -rf _build
rm -rf apidoc
sphinx-apidoc -T -e -o apidoc ../src/commissaire/
if [ -d "../../commissaire-service/" ]; then
  sphinx-apidoc -T -e -o apidoc ../../commissaire-service/src/commissaire_service/
else
  echo "Skipping commissaire-service apidoc regeneration due to missing repository..."
fi
if [ -d "../../commissaire-http/" ]; then
  sphinx-apidoc -T -e -o apidoc ../../commissaire-http/src/commissaire_http/
else
  echo "Skipping commissaire-http apidoc regeneration due to missing repository..."
fi

sphinx-build -b html . _build
