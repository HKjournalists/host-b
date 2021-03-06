#!/bin/bash

source `dirname $0`/../common/common.sh

ALARM_INFO="Switch OSPF All DOWN!"
NORMAL_INFO="$IDC_NAME: `date +"%Y-%m-%d %H:%M:%S"` switch ospf neighbor all down"

while [[ 1 ]]
do
    check_iplist_ready

    while read line
    do
        if [ -z "$line" ]
        then
            continue
        fi

        ip_vendor=$line
  	    line=`echo $line | awk '{print $1}'`
        #get the ecmp route of 10.0.0.0
        snmpwalk -cpublic -v2c $line 1.3.6.1.2.1.4.24.4.1.1.10.0.0.0 2>&1 > tmp.log
        #snmpwalk -cpublic -v2c 192.168.30.25  1.3.6.1.2.1.14.10.1.6 2>&1 > tmp.log
        if [[ $? == 0 ]] ; 
        then
	        ecmp_nexthops=`cat tmp.log | grep "255.0.0.0.0" | wc -l`
    	    if [[ $ecmp_nexthops == 0 ]] 
            then
                echo $ip_vendor >> tmp2.log 
    	    fi
	    fi
    done < ip.txt    

    echo >>$LOG_FILE
    if [ -s tmp2.log ] ; then
        ip=`cat tmp2.log`
        send_warning "$ALARM_INFO" "$ip"
    else
        NORMAL_INFO="$IDC_NAME: `date +"%Y-%m-%d %H:%M:%S"` switch ospf neighbor OK"
        echo "$NORMAL_INFO">>$LOG_FILE
    fi

    rm -rf tmp.log
    rm -rf tmp2.log
    sleep 3600

done
