#!/bin/bash

source `dirname $0`/../common/common.sh

ALARM_INFO="arp/host table error!"
#NORMAL_INFO="$IDC_NAME: `date +"%Y-%m-%d %H:%M:%S"` Switch check arp ok!"

date=""

function check_output_validation()
{       
    sed -i -e 's/\xd//g' -e 's/\x0//g' -e 's/\x1b//g' -e 's/\x1//g' -e 's/\[C//g' tmp.log
    grep -q ">" tmp.log
    if [ $? -ne 0 ]; then
        return 1
    fi

    grep -q "Total count" tmp.log
    if [ $? -ne 0 ]; then
        return 1
    fi

    grep -q "Total host count" tmp.log
    if [ $? -ne 0 ]; then
        return 1
    fi

    grep -q "Dynamic entries" tmp.log
    if [ $? -ne 0 ]; then
        return 1
    fi

    grep -q "pica_lcmgr" tmp.log
    if [ $? -ne 0 ]; then
        return 1
    fi

    grep -q -E "yes|no" tmp.log
    if [ $? -ne 0 ]; then
        return 1
    fi

    grep -q -E "L3_ENTRY_ONLY" tmp.log
    if [ $? -ne 0 ]; then
        return 1
    fi

    return 0
}

function filter_port_down_and_identify_error_type()
{
    rm -f diff.log
    touch diff.log
    cp arp_host_diff tmp_diff

    while read differ
    do
        printf "$differ\n" >> diff.log

        sw_hw=`echo $differ |cut -c 1`

        #more entries in hardware, this is normal in most cases
        if [ "$sw_hw" == ">" ]; then
            continue
        fi

        arp=`echo $differ |awk '{print $2}'`
        mac=`cat arp.info |grep "$arp " |awk '{print $2}'`
        vlan=`cat arp.info |grep "$arp " |awk '{print $4}' |sed 's/vlan//g'`
        vlan_tmp=`cat mac.info |grep -i "$mac" |awk '{print $1}'`

        #mac exists
        if [ x"$vlan" == x"$vlan_tmp" ]; then

            vlan_tmp1=`cat egress.info |grep -i "$mac" |awk '{print $3}'`
            #egress not exists in hardware
            if [ x"$vlan" != x"$vlan_tmp1" ]; then
                printf "  possible reason: l3 egress created failed!\n  need to do: manual recovery\n" >> diff.log
            else
                grep -q -E "parity error|L3_ENTRY_ONLY.*Operation failed" tmp.log
                #enter bcmshell print error as "BCM.0> unit 0 L3_ENTRY_ONLY entry 13980 parity error" or
                #cmd "d chg l3_entry_only" caused error as "Read ERROR: table L3_ENTRY_ONLY.ipipe0[11664]: Operation failed" 
                if [ $? -eq 0 ]; then
                    printf "  possible reason: l3 entry parity error!\n  need to do: manual recovery\n" >> diff.log
                #may be normal, caused by port down/up frequently
                else
                    printf "  possible reason: port down/up frequently!\n  need to do: manual confirmation\n" >> diff.log
                fi
            fi
        #mac not exists
        else
            if [ x"$1" == x"B6220V2" ]; then   
                count=15
            else
                count=14
            fi

            if [ $lcmgr_thread_count -eq $count ]; then
                #port down, this is normal
                sed -i '$d' diff.log
                sed -i '/'$arp'$/d' arp_host_diff
            else
                printf "  possible reason: l2 thread exited!\n  need to do: manual recovery\n" >> diff.log
            fi
        fi

    done < tmp_diff
}

function monitor()
{
    for i in $(seq 2)
    do
        ./check_arp.tcl $1 > tmp.log
        wait

        date=`date +"%Y-%m-%d %H:%M:%S"`

        #check the output validation at first to avoid 3a abnormal,if abnormal,try it again.
        check_output_validation
        if [ $? == 0 ]; then
            break
        fi
    done

    arp_count=`cat tmp.log | grep "Total count" | awk -F : '{print $2}' |sed 's/^ //'` 
    host_count=`cat tmp.log | grep 'Total host count' | awk -F : '{print $2}' |sed 's/^ //'`
    if [[ $arp_count == $host_count ]]; then
        #echo "$date $IDC Switch $ip: arp/host ok">>$LOG_FILE
        return 0
    fi

    sed -n '/show arp/,/Int>/p' tmp.log |grep "vlan" > arp.info
    sed -n '/forward-host/,/Total host count/p' tmp.log |grep -v -E 'show|Address|Total|----' > host.info
    sed -n '/ethernet-switching/,/Int>/p' tmp.log |grep -E "ae[1-9]|te-1|qe-1" > mac.info
    sed -n '/l3 egress show/,/BCM.0>/p' tmp.log |grep -E "yes|no" > egress.info

    cat arp.info | awk '{print $1}' | sort -t " " -n -k 1 |sort -t . -n -k1,1 -k2,2 -k3,3 -k4,4 > arp.ip.info
    cat host.info |awk '{print $1}' | sort -t " " -n -k 1 |sort -t . -n -k1,1 -k2,2 -k3,3 -k4,4 > host.ip.info

    lcmgr_thread_count=`sed -n '/pica_lcmgr/{n;p}' tmp.log`

    diff arp.ip.info host.ip.info | grep -E "<|>" > arp_host_diff

    if [ -s arp_host_diff ]; then
        filter_port_down_and_identify_error_type $2
    fi

    if [  ! -s arp_host_diff ]; then                                                                                            
        echo "$date $IDC Switch $ip: filter port down/up,arp/host still ok">>$LOG_FILE
        return 0
    fi
    
    echo -e "$date $IDC Switch $ip: arp/host error:\n`cat diff.log`">>$LOG_FILE

    rm -f *_diff
    rm -f *.info

    return 1
}

while [[ 1 ]]
do
    check_iplist_ready
 
    if [ ! -d log ] ; then
        mkdir log
    fi
    
    while read ip
    do
        if [ -z "$ip" ] ; then
            continue
        fi

        ip_vendor=$ip
        ip=`echo $ip | awk '{print $1}'`
        vendor=`echo $ip | awk '{print $2}'`

        rv=0 
        #when error detected, retry once more time to avoid unnecessary warnning.
        for i in $(seq 2)
        do 
            monitor "$ip" "$vendor"
            rv=$?
            if [ $rv -eq 0 ]; then
                break
            fi
            #save the tmp.log
            cp tmp.log log/"`echo $date |sed -n 's/ /_/p'`"_$ip.log
        done

        if [ $rv -eq 1 ]; then
            #for excessive hosts in hardware, no warning
            grep -v ">" diff.log > diff.warn
            if [ ! -s diff.warn ]; then
                rm -rf diff.*
                rm -rf tmp.log
                continue
            else
                echo -e "==> $ip twice errors,send a warning">>$LOG_FILE
	        warn_info=$(printf "Switch $ip arp/host table error info:\n`cat diff.warn`")
                send_warning "$ALARM_INFO" "$ip_vendor" "$warn_info"
                
	        rm -rf diff.*
                rm -rf tmp.log
            fi
        fi
    done < ip.txt

    #sleep 30 min
    sleep 1800
done
