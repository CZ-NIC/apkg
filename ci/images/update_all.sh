#!/bin/sh

# fail early
set -e

IMAGES=$@

# run build scripts in the correct order (be careful, containers from some directories depend on containers from other directories)
for dir in test systemd full; do
	echo "Building $dir"
	cd $dir
	if [ -n "$IMAGES" ]; then
		images=$IMAGES
	else
		images=$(ls -p | grep / | sed 's#/##')
	fi
	./update.sh $images
	cd ..
done
