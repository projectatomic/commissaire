#!/bin/bash
set -xeuo pipefail
rm -rf _build
rm -rf apidoc
sphinx-apidoc -T -e -o apidoc ../src/commissaire/
# TODO: Add the other repos here to get full api docs
sphinx-build -b html . _build
