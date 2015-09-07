#!/bin/bash

if [ -z "$1" ] ; then
    echo "usage: $0 IDC_NAME"
    echo "example: $0 SH01"
    exit 1
fi

pushd env > /dev/null
./netadmin_clean_config.sh $1
popd > /dev/null

