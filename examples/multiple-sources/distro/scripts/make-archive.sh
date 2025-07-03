#!/bin/bash
# create archive from current source using git
# following protocol introduced in compat level 5
set -e

VERSION=0.1
OUTPATH=pkg/archives/dev
NAMEVER=apkg-ex-multiple-sources-v$VERSION
ARCHIVE=$NAMEVER+repack.tar.gz
ARPATH=$OUTPATH/$ARCHIVE

mkdir -p $OUTPATH
tar -czf "$ARPATH" --transform "s#^multiple-sources#$NAMEVER#" \
    --exclude 'pkg' --exclude 'distro' --exclude '*.gz' \
    -C .. multiple-sources

# apkg expects stdout to describe archive files
echo archive: "$ARPATH"

# we can also indicate the upstream version explicitly,
# if we don't, apkg will use archive's filename
#
# Silly example: we attached a '+repack' to the filename
# and don't want it in the package version
echo version: $VERSION

# we can print whatever we like to stderr
echo "About to prepare the additional (component) archives:" >&2

echo "components:"
# Upstream can be split into several archives, we can use "component" to
# collect them and extract the others where needed
ARPATH="$OUTPATH/files.tar.gz"
tar -czf "$ARPATH" --strip-components=1 -C distro/components/files .
echo "  files: '$ARPATH'"

# A component whose name doesn't match where it needs to be extracted
ARPATH="$OUTPATH/extra-v0.5.tar.gz"
tar -czf "$ARPATH" --strip-components=1 -C distro/components/extra .
echo "  extra: '$ARPATH'"
