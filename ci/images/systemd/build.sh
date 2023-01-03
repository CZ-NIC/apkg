#!/bin/bash
# build specified docker image

CURRENT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"
source "${CURRENT_DIR}"/vars.sh "$@"
set -ex

docker build --pull --no-cache -t "${FULL_NAME}" -f "${IMAGE}/Dockerfile" .
