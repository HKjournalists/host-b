#!/bin/bash

source `dirname $0`/../common/common.sh
ALARM_INFO="Switch alive check error,fix it now!"
#NORMAL_INFO="$IDC_NAME: `date +"%Y-%m-%d %H:%M:%S"` Switch check alive ok"

while [[ 1 ]]
do
    check_iplist_ready

    cat ip.txt | awk '{print $1}' | xargs -n 1 ping -c 1 > tmp.log
    cat tmp.log | grep -B 1  "100% packet loss" | grep statistics | awk '{print $2}' > tmp2.log

    echo >>$LOG_FILE
    if [ -s tmp2.log ] ; then
        grep "`cat tmp2.log | awk '{print $1}'`" ip.txt > warn_ip.tmp
        ip=`cat warn_ip.tmp`
        send_warning "$ALARM_INFO" "$ip"
    else
        NORMAL_INFO="$IDC_NAME: `date +"%Y-%m-%d %H:%M:%S"` Switch check alive ok!"
        echo "$NORMAL_INFO">>$LOG_FILE
    fi

    rm -f tmp.log
    rm -f tmp2.log
    rm -f warn_ip.tmp
    sleep 30
done
