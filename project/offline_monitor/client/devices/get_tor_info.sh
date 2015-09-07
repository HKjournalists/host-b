#!/bin/sh

#rm -rf ip_vendor_version.txt ip_ok.txt ip_ok_baidu.txt ip_fail.txt \
#       ip_1062.txt ip_not_1062.txt vendor.txt

while true
do
    sh check_ping_avilable.sh
    if [[ $? == 0 ]];then
        break;
    fi
done
    
while true
do
    sh check_baidu.sh
    if [[ $? == 0 ]];then
        break;
    fi
done

while true
do
    sh check_vendor.sh
    if [[ $? == 0 ]];then
        break;
    fi
done

while true
do
    sh check_version.sh
    if [[ $? == 0 ]];then
        break;
    fi
done
