#!/bin/bash

source `dirname $0`/../common/common.sh

ALARM_INFO="Switch CPU usage high!"
NORMAL_INFO="$IDC_NAME: `date +"%Y-%m-%d %H:%M:%S"` switch check cpu usage ok"

while [[ 1 ]]
do
    check_iplist_ready
    
    while read line
    do
        if [ -z "$line" ] ; then
            continue
        fi

        ip_vendor=$line
  	line=`echo $line | awk '{print $1}'`
        snmpwalk -cpublic -v2c $line  1.3.6.1.4.1.32353.1.1 2>&1 > tmp.log
        if [[ $? == 0 ]] ; then
	    cpu_usage=`cat tmp.log | awk -F : '{print $4}' | sed 's/ //g'`
	    if [ $cpu_usage -gt 60 ] ; then
                echo "$ip_vendor   CPU:$cpu_usage%%" >> tmp2.log
	    fi
	fi
    done < ip.txt    

    echo >>$LOG_FILE
    if [ -s tmp2.log ] ; then
        ip=`cat tmp2.log`
        send_warning "$ALARM_INFO" "$ip"
    else
        NORMAL_INFO="$IDC_NAME: `date +"%Y-%m-%d %H:%M:%S"` switch check cpu usage ok"
        echo "$NORMAL_INFO">>$LOG_FILE
    fi

    rm -rf tmp.log
    rm -rf tmp2.log
    sleep 7200

done
