#!/bin/bash
# define common variables for image build scripts

IMAGE=$1
if [ -z "${IMAGE}" ]; then
    echo "ERROR: please provide IMAGE name as argument"
    exit 1
fi
IMAGE_GROUP="lxc"
REGISTRY="registry.nic.cz"
REGISTRY_BASE="$REGISTRY/packaging/apkg/$IMAGE_GROUP"
TAG="latest"
FULL_NAME="${REGISTRY_BASE}/${IMAGE}:${TAG}"
