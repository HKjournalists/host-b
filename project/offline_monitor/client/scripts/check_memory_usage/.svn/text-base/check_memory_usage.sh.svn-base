#!/bin/bash

source `dirname $0`/../common/common.sh

ALARM_INFO="Switch free memory usage low!"
NORMAL_INFO="$IDC_NAME: `date +"%Y-%m-%d %H:%M:%S"` Switch memory usage ok"

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
        snmpwalk -cpublic -v2c $line  1.3.6.1.4.1.32353.1.4 2>&1 > tmp.log
        if [[ $? == 0 ]] ; then
	    free_usage=`cat tmp.log | awk -F : '{print $4}' | sed 's/ //g' | sed 's/"//g' | sed 's/KB//g'`
            #echo $free_usage
            if [ "$free_usage" -lt "550000" ] ; then
                echo "$ip_vendor   free memory:${free_usage}KB" >> tmp2.log
	    fi
	fi
    done < ip.txt    

    echo >>$LOG_FILE
    if [ -s tmp2.log ] ; then
        ip=`cat tmp2.log`
        send_warning "$ALARM_INFO" "$ip"
    else
        NORMAL_INFO="$IDC_NAME: `date +"%Y-%m-%d %H:%M:%S"` Switch memory usage ok"
        echo "$NORMAL_INFO">>$LOG_FILE
    fi

    rm -rf tmp.log
    rm -rf tmp2.log
    sleep 7200

done
