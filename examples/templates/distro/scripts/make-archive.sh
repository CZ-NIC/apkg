#!/bin/bash
# create archive containing only README.md in a directory
set -e

VERSION=1.0
OUTPATH=pkg/archives/dev
NAMEVER=apkg-example-templates-v$VERSION
TOPDIR=templates
ARCHIVE=$NAMEVER.tar.gz
ARPATH=$OUTPATH/$ARCHIVE

mkdir -p "$OUTPATH"
mkdir -p "$NAMEVER"
cp README.md "$NAMEVER/"
tar -czvf "$ARPATH" "$NAMEVER"
rm -rf  "$NAMEVER"

# apkg expects stdout to list archive files
echo $ARPATH
