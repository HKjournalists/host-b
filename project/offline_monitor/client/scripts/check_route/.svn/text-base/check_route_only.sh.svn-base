#!/bin/bash

if [ -z "$1" ] ; then
    echo "Invalid IP address!"
    return
else
    IP_ADDR=$1
fi

LOG_FILE=check_route_only.log
ALARM_INFO="switch sw/hw route table error!"
NORMAL_INFO="`date +"%Y-%m-%d %H:%M:%S"` Switch check route ok!"

date=""

monitor()
{
        rm -rf *_diff

        ip=$1
        ./check_route_only.tcl $ip > tmp.log
        wait

        date=`date +"%Y-%m-%d %H:%M:%S"`
        dos2unix tmp.log &>/dev/null
        #cat -v tmp.log | tr -d "^@" | grep -a "\[" | grep -a "\]" | awk -F / '{print $1}' | sort > route.sw
        cat -v tmp.log | tr -d "^@" | grep -a -E "\[ospf|\[static|\[connected" | awk -F / '{print $1}' | sort > route.sw
        cat -v tmp.log | tr -d "^@" | grep -a -E "te-|qe|ae|connected" | grep -a -v "\[" | awk '{print $1}' | sort > route.hw
		
        diff route.sw route.hw | grep -a -E "<|>" > ${ip}_diff
        if [ ! -s ${ip}_diff ] ; then
            rm -rf ${ip}_diff
            rm -rf route.hw
            rm -rf route.sw
            return 0
        fi

        sw_count=`cat route.sw | wc -l`
        hw_count=`cat route.hw | wc -l`
        echo "`date +"%Y-%m-%d %H:%M:%S"` Switch $ip sw_route:${hw_count} hw_route:${sw_count}" >> route_number.log
        if [[ $sw_count == 0 ]] ; then
            echo "< FFFFFF" > ${ip}_diff
        fi
		
        if [[ $hw_count == 0 ]] ; then
            echo "> FFFFFF" > ${ip}_diff
        fi
	    
        if [ -s ${ip}_diff ] ; then
            echo -n "Sw count:$sw_count" >> ${ip}_diff
            echo " Hw count:$hw_count" >> ${ip}_diff
            cp -f ${ip}_diff ip_tmp_diff
        fi

        rm -rf route.sw
        rm -rf route.hw

        return 1
}

while [[ 1 ]]
do
    if [ ! -d log ] ; then
        mkdir log
    fi

    line=`echo $IP_ADDR | awk '{print $1}'`
   
    rv=0
    for i in $(seq 2)   
    do
        monitor $line
        rv=$?
        if [ $rv -eq 0 ] ; then
            break
        fi
        #save the tmp.log
        cp tmp.log log/"`echo $date |sed -n 's/ /_/p'`"_$line.log
        sleep 30
    done

    if [ $rv -eq 1 ] ; then
        warn_info=$(printf "\nRoute table diff info:\n`cat ip_tmp_diff`")
        send_warning "$ALARM_INFO" "$IP_ADDR" "$warn_info"
        rm -f ip_tmp_diff
    else
        NORMAL_INFO="`date +"%Y-%m-%d %H:%M:%S"` Switch check route ok!"
        echo "$NORMAL_INFO"" Switch: $IP_ADDR" >> $LOG_FILE
    fi

    rm -rf tmp.log
    break
done
