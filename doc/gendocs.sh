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

# Generate help command output
python ../../commctl/src/commctl/client_script.py user-data --help > examples/commctl-user-data-help.txt
sed -i 's|client_script.py|commctl|g' examples/commctl-user-data-help.txt

python ../../commissaire-http/src/commissaire_http/server/cli.py --help > examples/commissaire-server-cli.rst
sed -i 's|client_script.py|commissaire-server|g' examples/commissaire-server-cli.rst

sphinx-build -b html . _build
