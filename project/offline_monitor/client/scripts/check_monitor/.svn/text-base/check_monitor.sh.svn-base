#/bin/sh

source `dirname $0`/../common/common.sh
#source ./common.sh

ALARM_INFO="Monitor process hanged over 15 mins! It will be killed if hanged over 20 mins!"
KILL_INFO="Monitor process hanged over 20 mins, It has been killed!"
NORMAL_INFO="$IDC_NAME: `date +"%Y-%m-%d %H:%M:%S"` All the monitor programs are OK!"

while [[ 1 ]]
do
    ps aux | grep -v grep | grep nsi | grep .tcl | awk '{print $2}'>tcl.id.tmp
    ps aux | grep -v grep | grep nsi | grep "/bin/mail" | grep Alert | awk {'print $2'} >>tcl.id.tmp

    if [ -s tcl.id.tmp ] ; then
        while read id
        do
            run_time_min=`ps -p $id -o pid,start_time,etime,comm | grep "$id" | grep ":" | awk '{print $3}' | awk -F : '{print $(NF-1)}'`
            #echo "$id runtime $run_time_min"
            if [ $run_time_min -gt 20 ] ; then
                ps -p $id -o pid,start_time,etime,command >> err1.tmp
                kill -9 $id
            elif [ $run_time_min -gt 15 ] ; then
                ps -p $id -o pid,start_time,etime,command >> err.tmp
            fi
        done < tcl.id.tmp

        if [ -s err.tmp ] ; then
            err_info="`cat err.tmp`"
            send_warning "$ALARM_INFO" "None" "$err_info"
            echo "$err_info" >> $LOG_FILE
            rm -f err.tmp
        fi

        if [ -s err1.tmp ] ; then
            err1_info="`cat err1.tmp`"
            send_warning "$KILL_INFO" "None" "$err1_info"
            echo "$err1_info" >> $LOG_FILE
            rm -f err1.tmp
        fi

    else
        NORMAL_INFO="$IDC_NAME: `date +"%Y-%m-%d %H:%M:%S"` All the monitor programs are OK!"
        echo "$NORMAL_INFO" >> $LOG_FILE
    fi

    rm -f *.tmp
    sleep 300
done
