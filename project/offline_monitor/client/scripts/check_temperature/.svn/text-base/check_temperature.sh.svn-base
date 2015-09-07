#!/bin/bash

source `dirname $0`/../common/common.sh

ALARM_INFO="switch temperatue high!"
NORMAL_INFO="$IDC_NAME: `date +"%Y-%m-%d %H:%M:%S"` all switches are ok"

function get_server_ip()
{
    local ip=""
    ip=$(echo $1 | cut -d"." -f1-3)
#    echo "$ip.111"
    echo "$ip.2"
}

flag=0

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
        snmpwalk -cpublic -v2c $line  1.3.6.1.4.1.32353.1.5 2>&1 > tmp.log
        if [[ $? == 0 ]] ; then
            temp_value1=`cat tmp.log | awk -F : '{print $4}' | sed 's/ //g'`
	    
        if [ -n $temp_value1 ] && [ $temp_value1 -gt 60 ] ; then
                flag=1
                vendor=`echo $ip_vendor | awk '{print $2}'`
                version=`echo $ip_vendor | awk '{print $3}'`
                if [ $vendor == "B6220" ] ; then
                    serv_ip=$(get_server_ip $line)
                    ./fix_temperature.tcl $line $serv_ip
                    sleep 90
                    retry=0
                    while [[ $retry < 3 ]]
                    do
                        ((retry++))
                        snmpwalk -cpublic -v2c $line  1.3.6.1.4.1.32353.1.5 2>&1 > tmp.log
                        if [[ $? == 0 ]] ; then
                            temp_value2=`cat tmp.log | awk -F : '{print $4}' | sed 's/ //g'`
                            if [ $temp_value2 -lt 60 ] ; then
                                echo "`date +"%Y-%m-%d %H:%M:%S"` switch $line temperature high, automatic fix it, from ${temp_value1} to ${temp_value2}" >> $LOG_FILE
                                break
                            else
                                send_warning "B6220 Switch high temperature:${temp_value2}. Automatic recovery failed!\n" "$ip_vendor"
                            fi
                        fi
                    done
                else
                     send_warning "Switch high temperature:${temp_value}!\n" "$ip_vendor"
                fi
            fi
        fi
    done < ip.txt    

    if [[ $flag == 0 ]] ; then
        flag=0
        NORMAL_INFO="$IDC_NAME: `date +"%Y-%m-%d %H:%M:%S"` all switches are ok"
        echo "$NORMAL_INFO">>$LOG_FILE
    fi

    rm -rf tmp.log
    rm -rf tmp2.log
    sleep 7200
done
