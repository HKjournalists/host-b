#!/bin/bash

source `dirname $0`/../common/common.sh

LASTLOGFILE=last.log
ALARM_INFO="Switch lcmgr threads number error!"
NORMAL_INFO="$IDC_NAME: `date +"%Y-%m-%d %H:%M:%S"` Switch check thread number ok"

touch  $LASTLOGFILE
> $LASTLOGFILE

fix_counter_thread()
{
    ip_ver=$1
    ip_addr=`echo $ip_ver | awk '{print $1}'`
    send_warning "counter thread exit, prepare to restart thread.." "$ip_ver"

    for ((i=0;i<3;i++))
    do
        ./fix_threads_num.tcl $ip_addr
        sleep 1

        ./check_threads_num.tcl $ip_addr > tmp.log
        dos2unix tmp.log &>/dev/null
        cat -v tmp.log |grep -a -B1 "$ exit" tmp.log  | grep -a -v "exit" | grep -a -v "\--" > tmp1.log
        dos2unix tmp1.log &>/dev/null
        number=`cat -v tmp1.log | tr -d "^@"`
        interval=`grep -a "Interval" tmp.log | awk -F = '{print $2}'`

        if [ $interval -gt 0 ] ; then
            recovery_flag=1
            send_warning "counter thread recovery (interval=$interval) successful." "$ip_ver"
            break
        fi
    done

    if [ $recovery_flag -eq 0 ] ; then
        send_warning "counter thread recovery (interval=$interval) failed!" "$ip_ver"
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
        version=`echo $ip_vendor | awk '{print $3}'`
        vendor=`echo $ip_vendor | awk '{print $2}'`

        ./check_threads_num.tcl $line > tmp.log
        dos2unix tmp.log &>/dev/null
        cat -v tmp.log |grep -a -B1 "$ exit" tmp.log  | grep -a -v "exit" | grep -a -v "\--" > tmp1.log
        dos2unix tmp1.log &>/dev/null
        number=`cat -v tmp1.log | tr -d "^@"`
        interval=`grep -a "Interval" tmp.log | awk -F = '{print $2}'`

        if [ x"$vendor" == x"B6220V2" ];then
             count=13
        else
             count=12
        fi

        if [ $number -lt $count ] ; then
            recovery_flag=0
            if [ $interval -eq 0 ] ; then
                fix_counter_thread "$ip_vendor"
            fi

            if [ $recovery_flag -eq 0 ] || [ $number -lt $count ] ; then
                echo "$line threads_number:$number version:$version vendor:$vendor ctr interval:$interval" >> tmp2.log
            fi
        fi
        echo "$line threads_number:$number version:$version vendor:$vendor ctr interval:$interval" >> threads_number.log
    done < ip.txt 

    if [ ! -f tmp2.log ] ; then
        NORMAL_INFO="$IDC_NAME: `date +"%Y-%m-%d %H:%M:%S"` Switch check thread number ok"
        echo "$NORMAL_INFO">>$LOG_FILE
    else
        if [ ! -s $LASTLOGFILE ] ; then
            cp tmp2.log $LASTLOGFILE
        fi

        diff tmp2.log $LASTLOGFILE
        if [[ $? == 0 ]] ; then
            ip=`cat tmp2.log`
            echo "`date +"%Y-%m-%d %H:%M:%S"` Switch:" >> $LOG_FILE
            echo "$ip" >> $LOG_FILE
        else
            diff tmp2.log $LASTLOGFILE >> tmp3.log
            echo "new:" >> tmp4.log
            cat tmp3.log | grep "<" | awk -F "<" '{print $2}' >> tmp4.log
            echo "old:" >> tmp4.log
            cat $LASTLOGFILE >> tmp4.log
            cp tmp2.log $LASTLOGFILE
            ip=`cat tmp4.log`
            send_warning "$ALARM_INFO" "$ip"
        fi
    fi

    rm -rf tmp*.log
    sleep 21600
done
