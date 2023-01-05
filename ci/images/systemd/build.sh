#!/bin/sh
# build specified docker image

. ./vars.sh
set -ex
docker build --pull --no-cache -t "${FULL_NAME}" -f "${IMAGE}/Dockerfile" .
