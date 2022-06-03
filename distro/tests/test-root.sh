#!/bin/bash

user=`whoami`
if [ "$user" != "root" ]; then
    echo "Running as user $user, not root."
    exit 1
fi
echo "Running as root."
