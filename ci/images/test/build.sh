#!/bin/bash
# build specified docker image

IMAGE=$1

if [ -z "$IMAGE" ]; then
    echo "usage: $0 IMAGE"
    exit 1
fi
set -ex
docker build --no-cache -t "registry.nic.cz/packaging/apkg/ci/$IMAGE:apkg" "$IMAGE"
