#!/bin/bash
#
# Generates a changelog for a release

set -euo pipefail

if [ $# -ne 2 ]; then
    echo "You must provide the repo directory and the previous tag."
    echo "Example: ./tools/gen-changelog.sh . 0.0.0"
    exit 1
fi

REPODIR=$1
LASTTAG=$2
NEWCHANGELOG=`mktemp`

pushd $REPODIR
VERSION=`python setup.py --version`
echo "# `basename $PWD` v$VERSION" >> $NEWCHANGELOG
echo '```' >> $NEWCHANGELOG
git log $LASTTAG..HEAD --pretty="* %h: %s" >> $NEWCHANGELOG
echo '```' >> $NEWCHANGELOG
if [ -e CHANGELOG.md ]; then
    echo "" >> $NEWCHANGELOG
    cat CHANGELOG.md >> $NEWCHANGELOG
fi
mv $NEWCHANGELOG CHANGELOG.md
rm -f $NEWCHANGELOG
popd
