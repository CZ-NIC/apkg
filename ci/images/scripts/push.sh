#!/bin/sh
# upload docker image into apkg registry

. ./vars.sh
set -ex
docker push "$FULL_NAME"
