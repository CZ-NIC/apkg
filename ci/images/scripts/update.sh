#!/bin/sh
# build and upload docker image(s) into apkg registry
#
# this is a simple wrapper around build.sh and update.sh
#
# to build & upload all images: ./update.sh */

if [ "$#" -lt 1 ]; then
    echo "usage: $0 IMAGE..."
    exit 1
fi

set -e

for ARG in "$@"
do
    IMAGE=${ARG%/}
    echo "Building $IMAGE..."
    ./build.sh $IMAGE
    echo "Pushing $IMAGE..."
    ./push.sh $IMAGE
done
