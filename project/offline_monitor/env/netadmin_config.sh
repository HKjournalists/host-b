#!/bin/sh

if [ -z "$1" ] ; then
    echo "usage: $0 IDC_NAME"
    echo "example: $0 SH01"
    exit 1
fi

IDC_LIST_INFO=../config/idc/idc.conf
IDC_NAME=$1
#IDC_NAME=`echo "$1" | awk -F . '{ print $2 }'`
#IDC_NAME=$(echo $IDC_NAME | tr "[a-z]" "[A-Z]")

if [ ! -s "../config/collectd/$IDC_NAME/collectd.conf" ] ; then
    echo "------------------------------"
    echo "Configure IDC: $IDC_NAME Failed!"
    echo "Please mkdir ../config/collectd/$IDC_NAME and set collectd.conf first!"
    echo "------------------------------"
    exit 1
fi

if [ $IDC_NAME = "SZWG01" ] ; then
    IDC_HOSTNAME=szwg-sys-netadmin00.szwg01
else
    IDC_HOSTNAME=$IDC_NAME-sys-netadmin00.$IDC_NAME
fi

IDC_LIST="`cat $IDC_LIST_INFO`"

grep -i "$IDC_NAME" $IDC_LIST_INFO > /dev/null
if [ "$?" != 0 ] ; then
    echo "$IDC_LIST $IDC_NAME" > $IDC_LIST_INFO
    echo "------------------------------"
    echo "(1) New IDC Server found: IDC Name:$IDC_NAME, netadmin host name:$IDC_HOSTNAME"
    echo "(2) Start to configure new netadmin server $IDC_HOSTNAME environment, please wait..."
    ./netadmin_mkdir.tcl $IDC_HOSTNAME > $IDC_HOSTNAME.log

    grep -i "run_monitor.sh" $IDC_HOSTNAME.log
    if [ "$?" = 0 ] ; then
        echo "    $IDC_HOSTNAME already configured! Continue."
        exit 0
    fi

    pushd ../info/get_tor_list/ > /dev/null
    ./get_tor_list.sh $IDC_NAME > get_tor_list.log
    popd > /dev/null
    echo "    Done!"

    echo "(3) Configure $IDC_HOSTNAME switch monitor, please wait... "
    ./netadmin_config.tcl "$IDC_HOSTNAME" >> $IDC_HOSTNAME.log
    echo "    Finished!"
    echo "------------------------------"
fi

echo "$IDC_NAME is already configured!"
