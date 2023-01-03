#!/bin/sh

# fail early
set -e


# run build scripts in the correct order (be careful, containers from some directories depend on containers from other directories)
for dir in test systemd full; do
	echo "Building $dir"
	cd $dir
	./update.sh $(ls -p | grep / | sed 's#/##')
	cd ..
done
