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

echo "------------------------------"
echo "Start to clean configure IDC: $IDC_NAME ..."

grep -w "$IDC_NAME" $IDC_LIST_INFO > /dev/null
if [ "$?" != 0 ] ; then
    echo "Can not find $IDC_NAME in idc.conf. Do nothing."
    echo "------------------------------"
    exit
fi

if [ $IDC_NAME = "SZWG01" ] ; then
    IDC_HOSTNAME=szwg-sys-netadmin00.szwg01
else
    IDC_HOSTNAME=$IDC_NAME-sys-netadmin00.$IDC_NAME
fi

rm -f idc.tmp idc.new

cat $IDC_LIST_INFO | tr -s " " "\n" > idc.tmp

while read line
do
    if [ "$line"x = "$IDC_NAME"x ] ; then
        continue
    fi
    echo -n "$line " >> idc.new.tmp
done < idc.tmp

echo "New IDC List: $IDC_LIST"
echo "`cat idc.new.tmp`"

cp -f idc.new.tmp $IDC_LIST_INFO
rm -f *.tmp

./netadmin_clean.tcl $IDC_HOSTNAME > $IDC_HOSTNAME.clean.log

echo "Finished!"
echo "------------------------------"

