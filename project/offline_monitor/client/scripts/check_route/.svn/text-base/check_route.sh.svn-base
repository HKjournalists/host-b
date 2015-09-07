#!/bin/bash

source `dirname $0`/../common/common.sh

while [[ 1 ]]
do
    check_iplist_ready
    
    while read line
    do
        if [ -z "$line" ] ; then
            continue
        fi

        ip_vendor=$line
        #line=`echo $line | awk '{print $1}'`
        version=`echo $ip_vendor | awk '{print $3}'`
        
        ver_num=`echo $version | tr -d "."`
        if [ $ver_num -lt 1062 ] ; then
            source check_route_with_fix.sh "$ip_vendor"
        else
            source check_route_only.sh "$ip_vendor"
        fi      
    done < ip.txt
    sleep 3600
done
