#!/bin/bash

source `dirname $0`/../common/common.sh

ALARM_INFO="Switch dhcrelay process exit!"
NORMAL_INFO="$IDC_NAME: `date +"%Y-%m-%d %H:%M:%S"` switch check dhcp relay ok"

fix_dhcrelay()
{
    ip_ver=$1
    ip_addr=`echo $ip_ver | awk '{print $1}'`
    #send_warning "dhcrelay process exit, prepare to restart process.." "$ip_ver"
    echo "`date +"%Y-%m-%d %H:%M:%S"` dhcrelay process exit, prepare to restart process. Switch:$ip_ver" >> $LOG_FILE

    for ((j=0;j<3;j++))
    do
        ./fix_dhcrelay.tcl $ip_addr
        sleep 1

        ./check_dhcrelay.tcl $ip_addr > tmp.log
        cat tmp.log  | grep -a dhcrelay > tmp1.log
        if [ -s tmp1.log ] ; then
            ok_flag=1
            rm -f tmp1.log
            #send_warning "dhcrelay process restart successful." "$ip_ver"
            echo "`date +"%Y-%m-%d %H:%M:%S"` dhcrelay process restart successful. Switch:$ip_ver" >> $LOG_FILE
            break
        fi
    done
    
    if [ $ok_flag -eq 0 ] ; then
        echo $ip_ver >> tmp2.log
        echo "`date +"%Y-%m-%d %H:%M:%S"` dhcrelay process restart failed! Switch:$ip_ver" >> $LOG_FILE
        send_warning "dhcrelay process restart failed!" "$ip_ver"
    fi
}

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
        vendor=`echo $ip_vendor | awk '{print $2}'`
        
        ok_flag=0

        for ((i=0;i<3;i++))
        do
            ./check_dhcrelay.tcl $line > tmp.log
            cat tmp.log  | grep -a dhcrelay > tmp1.log
            if [ -s tmp1.log ] ; then
                ok_flag=1
                rm -f tmp1.log
                break
            else
                continue
            fi
        done

        if [ "$ok_flag" -eq 0 ] ; then
            if [ "$vendor"x = "B6220"x ] ; then
                fix_dhcrelay "$ip_vendor"
            else
                echo $ip_vendor >> tmp2.log
            fi
        fi
    done < ip.txt    

    if [ -s tmp2.log ] ; then
        ip=`cat tmp2.log`
        send_warning "$ALARM_INFO" "$ip"
    else
        NORMAL_INFO="$IDC_NAME: `date +"%Y-%m-%d %H:%M:%S"` switch check dhcp relay ok"
        echo "$NORMAL_INFO">>$LOG_FILE
    fi

    rm -f tmp.log
    rm -f tmp2.log
    sleep 21600

done
