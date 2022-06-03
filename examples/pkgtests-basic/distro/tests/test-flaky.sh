#!/bin/bash

if [[ $(($RANDOM % 2)) -eq 0 ]]; then
    echo 'flaky test OK this time'
    exit 0
else
    echo 'flaky test FAIL this time'
    exit 23
fi
