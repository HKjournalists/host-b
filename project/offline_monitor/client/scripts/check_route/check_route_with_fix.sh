#!/bin/bash

if [ -z "$1" ] ; then
    echo "Invalid IP address!"
    return
else
    IP_ADDR=$1
fi

warn_flag_sysnoc=0
datetime=""
line_index=0
sw_net=0
net_type=0
recovered=0
count_sw=0
count_hw=0

HOST_NAME=`hostname`
SOURCE_NAME=${HOST_NAME%.baidu*}

LOG_FILE=check_route_with_fix.log
ALARM_INFO="switch route table error!"

send_warning_sysnoc()
{
    if [ $2 == "B" ] ; then
        msg=$(echo -e "$datetime Switch $1 route table error,automatic recovery will start!!\n`cat route_ospf_mask_30_excluded.log`")
    else
        if [ $recovered -eq 1 ] ; then
            result="success"
        else
            result="failed"
        fi
        msg=$(echo -e "$datetime Switch $1 route table error,automatic recovery $result!!\n")
    fi
    
    echo "$msg" >> $LOG_FILE
    send_warning "$ALARM_INFO" "$IP_ADDR" "$msg"
}

get_route()
{
    ./check_route_with_fix.tcl $1 > route_raw.log
    wait
	
    sed -i -e 's/\xd//g' -e 's/\x0//g' -e 's/\x1b//g' route_raw.log
    
    grep -q "Int>" route_raw.log
    if [ $? -eq 1 ] ; then
        return 1 
    fi

    grep -q "Total route count" route_raw.log
    if [ $? -eq 1 ] ; then 
        return 2
    fi
    
    sed -n '/show route forward-route/,/Total route count/p' route_raw.log |sed  '1,3d' |sed '$d' > route_hw.log 
    grep -q "ospf" route_raw.log
    if [ $? -eq 1 ] ; then 
        return 2
    fi

    sed -n '/show route table/,/Int>/p' route_raw.log |sed '1d' |sed '$d' > route_sw.log
    grep -q "Total host count" route_raw.log
    if [ $? -eq 1 ] ; then 
        return 2
    fi
    
    sed -n '/show route forward-host/,/Total host count/p' route_raw.log  |sed '1,3d' |sed '$d' > host.log 
    return 0
}

regulate_route_hw()
{
    net=`echo $1 |awk '{print $1}'`
    mask=`echo $1 |awk '{print $2}'`
    nexthop=`echo $1 |awk '{print $4}'`
 
    #get mask_len
    echo $mask |awk -F . '
        BEGIN {
                len=0;
              }
              {
                for(f=1;f<=4;f++)
                {
                    i = 7;
                    while(i >= 0)
                    {
                        if((and($f,lshift(1,i))) != 0)
                        {
                            len++;
                            i--;
                        }
                        else
                        {
                            break;
                        }
                    }
                }
              }
	END {
              print len;
	    }' > mask_len

    mask_len=`cat mask_len`

    echo -e "$net/$mask_len\t$nexthop" >> route_hw1.log 
}

regulate_route_sw()
{
    odd=$[$line_index%2]
    if [ $odd -eq 0 ] ; then 
        net_type=`echo $1 |awk -F '[' '{print $2}' |awk -F '(' '{print $1}'`	
        sw_net=`echo $1 |awk '{print $1}'`	
    else		
        if [ $net_type == "ospf" ] ; then
            nh_ip=`echo $1 |awk '{print $3}'`
            nhi=`cat host.log |grep $nh_ip |awk '{print $3}'`
            echo -e "$sw_net\t$nhi" >> route_sw1.log
        else
            echo -e "$sw_net\t$net_type" >> route_sw1.log
        fi
    fi	
    
    line_index=$[$line_index+1]
}

diff_route()
{
    count_sw=`cat route_sw.log |wc -l`
    count_sw=$[$count_sw/2]
    count_hw=`cat route_hw.log |wc -l`

    if [ $count_sw -eq $count_hw ] ; then
        return 0
    fi

    rm -f route_hw1.log
    while read line1
    do
        regulate_route_hw "$line1"
    done < route_hw.log

    rm -f route_sw1.log
    line_index=0
    while read line2
    do
        regulate_route_sw "$line2"
    done < route_sw.log

    cat route_sw1.log |sort -t " " -n -k 1 |sort -t . -n -k1,1 -k2,2 -k3,3 -k4,4 > route_sw_sort.log
    cat route_hw1.log |sort -t " " -n -k 1 |sort -t . -n -k1,1 -k2,2 -k3,3 -k4,4 > route_hw_sort.log
    diff route_sw_sort.log route_hw_sort.log |grep -E '>|<' > route_diff.log

    cat route_diff.log |grep "ae" |grep "/30" > route_ospf_mask_30.log
    cat route_diff.log |grep "ae" |grep -v "/30" > route_ospf_mask_30_excluded.log
    cat route_diff.log |grep "connected" > route_conn.log

    if [ -s route_ospf_mask_30_excluded.log ] ; then
        echo -e "$datetime ${IDC_NAME} Switch $1 ospf_mask_30_excluded error:\n`cat route_ospf_mask_30_excluded.log`" \
			>> route_ospf_mask_30_excluded.dat
	
	cat route_ospf_mask_30_excluded.log |grep -v '>' |grep -E '0.0.0.0/0|10.0.0.0/8|172.16.0.0/12|192.168.0.0/16' > route_need_recovery.log
        if [ -s route_need_recovery.log ] ; then
            warn_flag_sysnoc=1
        fi
    fi

    if [ -s route_ospf_mask_30.log ] ; then
        echo -e "$datetime ${IDC_NAME} Switch $1 ospf_mask_30 error:\n`cat route_ospf_mask_30.log`" >> route_ospf_mask_30.dat
    fi

    if [ -s route_conn.log ] ; then
        echo -e "$datetime ${IDC_NAME} Switch $1 ${IDC_NAME} Switch connected error:\n`cat route_conn.log`" >> route_conn.dat
    fi

    if [ -s route_diff.log ] ; then 
        echo -e "$datetime ${IDC_NAME} Switch $1 ${IDC_NAME} Switch route table error:\n`cat route_diff.log`" >> route_diff.dat
    fi

    return 1
}

recovery()
{
    recovered=0
    ae_array=(0 0 0 0 0 0)
    
    while read line3
    do
        sw_flag=${line3:0:1}
        if [ $sw_flag == "<" ] ; then
            ae=`echo $line3 |awk '{print $3}'`
            ae_no=${ae:2:1}
            ae_no=$[$ae_no-1]
            ae_array[$ae_no]=$ae
	fi
    done < route_need_recovery.log
    #done < route_ospf_mask_30_excluded.log

    ./recovery.tcl $1 ${ae_array[0]} ${ae_array[1]} ${ae_array[2]} ${ae_array[3]} ${ae_array[4]} ${ae_array[5]}	
    wait

    ./check_route_with_fix.tcl $1 > check.log
    count_sw_A=`cat check.log | grep -a "> to" | wc -l`
    count_hw_A=`cat check.log | grep -a -E "255.|0.0.0.0" | grep -a -E "ae|qe" | wc -l`
	
    if [ $count_sw_A -eq $count_hw_A ] ; then
        recovered=1	
    fi
}

while [[ 1 ]]
do
    line=`echo $IP_ADDR | awk '{print $1}'`

    warn_flag_sysnoc=0
    datetime=$(echo `date +"%Y-%m-%d %H:%M:%S"`)

    for ((k=0;k<3;k++))
    do
        get_route $line
        re=$?
        #return vlaue 0:valid info
        #return value 1:no power or AAA abnormal,retry is unnecessary
        #return value 2:retry at most 3 times to get valid info
        if [ $re -eq 0 -o $re -eq 1 ] ; then
            break
        fi
    done

    #route info in route_raw.log is invalid
    if [ $k -eq 3 ] ; then
        continue
    fi   
      
    diff_route $line
    if [ $warn_flag_sysnoc -eq 1 ] ; then
        send_warning_sysnoc $line B
        python send_alarm_to_walle.py $line 1 $SOURCE_NAME
        recovery $line
        send_warning_sysnoc $line A
        python send_alarm_to_walle.py $line 2 $SOURCE_NAME
    else
        NORMAL_INFO="`date +"%Y-%m-%d %H:%M:%S"` Switch check route ok!"
        echo "$NORMAL_INFO"" Switch: $IP_ADDR" >> $LOG_FILE
    fi
    
    #rm -f route_*.log route_*.dat 
    break
done
