#!/bin/bash
MAIL_MEMBER="sti@baidu.com -c hqc@baidu.com -c sysnocer@baidu.com" 
#MAIL_MEMBER="tianye09@baidu.com" 

IDC_INFO=../../config/idc/idc.conf
MONITOR_PATH=/home/nsi/switch/monitor/devices

idclist="`cat $IDC_INFO`"
#idclist="NMG01 NJ02 QD01 SH01 NB01 YQ01 SZWG"

modellist="D2020 S6220 B6220 B6220V2 LY2R"

mail_send()
{
    cat $1 | mutt -s "baidu tor switch list" $MAIL_MEMBER -a ./*.txt
}

while [[ 1 ]]
do
    printf "`date`\n\n" >> temp_mail
    for idc in ${idclist}
    do
        if [ ${idc}x = "SZWG01"x ];then
            scp nsi@szwg-sys-netadmin00.szwg01:$MONITOR_PATH/ip_vendor_version.txt ${idc}.txt > /dev/null
        else
            scp nsi@${idc}-sys-netadmin00.${idc}:$MONITOR_PATH/ip_vendor_version.txt ${idc}.txt > /dev/null
        fi
        sync

        cat ${idc}.txt >> all.txt
        printf "\033[31;49;1m%s\033[0m\n" "${idc}:"  
        printf "%s\n" "${idc}:" >> temp_mail 
        for model in ${modellist}
        do
           printf "%4s%-5s%3s" "" ${model} ":"
           printf "%4s%-5s%3s" "" ${model} ":" >> temp_mail
           printf "%2s\033[31;49;1m%-3s\033[0m\n" "" `cat ${idc}.txt | grep -w ${model} | wc -l` 
           printf "%2s%-3s\n" "" `cat ${idc}.txt | grep -w ${model} | wc -l`  >> temp_mail
        done

        printf "%4s\033[34;49;1m%-5s\033[0m%3s" "" "Total" ":"
        printf "%4s%-5s%3s" "" "Total" ":" >> temp_mail
        printf "%2s\033[34;49;1m%3s\033[0m\n" "" `cat ${idc}.txt | wc -l`
        printf "%2s%3s\n" "" `cat ${idc}.txt | wc -l` >> temp_mail
        printf "\n"   
        printf "\n" >> temp_mail
    done
    
    printf "\033[31;49;1m%s\033[0m\n" "Total:" 
    printf "%s\n" "Total:" >> temp_mail 
    for model in ${modellist}
    do
       printf "%4s%-5s%3s" "" ${model} ":"
       printf "%4s%-5s%3s" "" ${model} ":" >> temp_mail
       printf "%2s\033[31;49;1m%-3s\033[0m\n" "" `cat all.txt | grep -w ${model} | wc -l`
       printf "%2s%-3s\n" "" `cat all.txt | grep -w ${model} | wc -l`   >> temp_mail
    done
    printf "%4s\033[34;49;1m%-5s\033[0m%3s" "" "Total" ":"
    printf "%4s%-5s%3s" "" "Total" ":" >> temp_mail
    printf "%2s\033[34;49;1m%3s\033[0m\n" "" `cat all.txt | wc -l`
    printf "%2s%3s\n" "" `cat all.txt | wc -l` >> temp_mail
    echo " "

    rm -rf all.txt
    mail_send temp_mail
    rm -rf temp_mail
    
    exit 0
done
