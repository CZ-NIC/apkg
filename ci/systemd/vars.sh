#!/bin/bash
# define common variables for image build scripts

REGISTRY="registry.nic.cz/packaging/apkg"
IMAGE=$1
if [ -z "${IMAGE}" ]; then
    echo "image name not provided"
    exit 1
fi
TAG="latest"
FULL_NAME="${REGISTRY}/systemd/${IMAGE}:${TAG}"
