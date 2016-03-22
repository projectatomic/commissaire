#!/bin/bash
set -xeuo pipefail
rm -rf _build
rm -rf apidoc
sphinx-apidoc -T -e -o apidoc ../src/commissaire/
sphinx-build -b html . _build
