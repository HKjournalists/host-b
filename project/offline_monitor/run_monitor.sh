#!/bin/bash

IDC_LIST="`ls config/collectd`"
#echo "$IDC_LIST"

pushd env > /dev/null
for idc in ${IDC_LIST}
do
    ./netadmin_config.sh $idc
done
popd > /dev/null

