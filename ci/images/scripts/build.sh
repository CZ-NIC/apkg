#!/bin/sh
# build specified docker image

. ./vars.sh
set -ex
docker build --no-cache -t "$FULL_NAME" "$IMAGE"
