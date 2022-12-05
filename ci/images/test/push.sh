#!/bin/bash
# upload docker image into apkg registry

IMAGE=$1

if [ -z "$IMAGE" ]; then
    echo "usage: $0 IMAGE"
    exit 1
fi
set -ex
docker push "registry.nic.cz/packaging/apkg/ci/$IMAGE:apkg"
