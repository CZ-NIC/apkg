#!/bin/sh
# build specified docker image

source vars.sh
set -ex
docker build --pull --no-cache -t "${FULL_NAME}" -f "${IMAGE}/Dockerfile" .
