#!/bin/bash

source `dirname $0`/../common/common.sh

ALARM_INFO="Switch ntp sync error!"
NORMAL_INFO="$IDC_NAME: `date +"%Y-%m-%d %H:%M:%S"` Switch check ntp sync ok"

while [[ 1 ]]
do
    check_iplist_ready

    while read line
    do
        if [ -z "$line" ] ; then
            continue
        fi

        line=`echo $line | awk '{print $1}'`
        ./check_ntp.tcl $line > tmp.log
        echo -n "$line" >> tmp1.log
        cat -v tmp.log |grep -a "code" >> tmp1.log
    done < ip.txt 

    ip=`cat tmp1.log | grep -a "ERROR" | awk '{print $1}' | awk -F ^ '{print $1}'`
    if [[ x$ip == x"" ]] ; then
        NORMAL_INFO="$IDC_NAME: `date +"%Y-%m-%d %H:%M:%S"` Switch check ntp sync ok"
        echo "$NORMAL_INFO">>$LOG_FILE
    else
        send_warning "$ALARM_INFO" "$ip"
    fi

    rm -rf tmp*.log 
    sleep 86400
done
