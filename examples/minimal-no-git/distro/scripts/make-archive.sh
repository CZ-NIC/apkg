#!/bin/bash
# create archive from current source using git
set -e

VERSION=0.1
OUTPATH=pkg/archives/dev
NAMEVER=apkg-ex-minimal-no-git-v$VERSION
ARCHIVE=$NAMEVER.tar.gz
ARPATH=$OUTPATH/$ARCHIVE

mkdir -p $OUTPATH
tar -czf "$ARPATH" --transform "s#^minimal-no-git#$NAMEVER#" \
    --exclude 'pkg' --exclude '*.gz' \
    -C .. minimal-no-git

# apkg expects stdout to list archive files
echo "archive: '$ARPATH'"
