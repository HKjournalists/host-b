#!/bin/bash

##! @TODO:   读取交换机boot messege
##! @AUTHOR: wangbin19@baidu.com
##! @VERSION: 1.0_build0010

source `dirname $0`/process_clean.sh

SWITCH_IP="192.168.30.25"
CK_BOOTMSG_LOG="ck_xorplus_bootmsg.temp.log"
MATCH_WORDS="Clock"
FULL_WORDS="Clock: inserting leap second 23:59:60 UTC"

MAIL_MEMBER="wangbin19@baidu.com wuxiaoying01@baidu.com\
             zhangpengfei02@baidu.com zhuozecheng01@baidu.com" 
ALERT_TITEL="Switch Alert: "
IDC_NAME="BB"

##! @TODO: 发送警告邮件
##! @AUTHOR: wangbin19@baidu.com
##! @IN: $1 => 警告内容
##! @IN: $2 => 设备信息
##! @IN: $3 => 备注（可选）
##! @OUT: 0 => success; 1 => failed
send_warning()
{
    local alert_type=$0
    alert_type=${alert_type##*/}
    alert_type=${alert_type%.*}
    printf "IDC:\t\t\t${IDC_NAME}\n" > temp_mail
    printf "Date:\t\t`date +"%Y-%m-%d %H:%M:%S"`\n" >> temp_mail
    printf "Alert Type:\t${alert_type}\n" >> temp_mail
    printf "Alert Info:\t$1\n" >> temp_mail
    printf "Switch Info:\n----------------\n$2\n" >> temp_mail
    if [ -n "$3" ]
    then
        printf "\n----------------\n$3\n" >> temp_mail
    fi
    sudo /bin/mail -v -s "${ALERT_TITEL} ${alert_type}" "${MAIL_MEMBER}" < temp_mail
    if [ $? -ne 0 ]
    then
        echo "send mail failed!"
        return 1
    fi
    return 0
}

##! @TODO: 读取交换机boot messege，判断是否包含指定语句
##! @AUTHOR: wangbin19@baidu.com
##! @IN: None
##! @OUT: 0 => success; 1 => failed
function ck_xorplus_bootmsg()
{
    expect check_bootmsg.tcl ${SWITCH_IP} ${MATCH_WORDS} > ${CK_BOOTMSG_LOG} 2>&1
    if [ $? -ne 0 ]
    then
        return 2
    fi
    sed -i -e 's/\xd//g' -e 's/\x0//g' -e 's/\x1b//g' \
           -e 's/\x1//g' -e 's/\[C//g' ${CK_BOOTMSG_LOG}
    if [ $? -ne 0 ]
    then
        return 2
    fi
    grep -q "${FULL_WORDS}" ${CK_BOOTMSG_LOG}
    if [ $? -eq 0 ]
    then
        return 0
    fi
    return 1
}

##! @TODO: 主函数
##! @AUTHOR: wangbin19@baidu.com
##! @IN: None
##! @OUT: 0 => success; 1 => failed
function ck_xorplus_bootmsg_main()
{
    process_clean_entry "sh leapsec_test.sh"
    if [ $? -ne 0 ]
    then
        exit 1
    fi
    sh leapsec_test.sh &
    if [ $? -ne 0 ]
    then
        exit 1
    fi
    echo "leapsec_test.sh is running background"
    sleep 10
    while [[ 1 ]]
    do
        echo "check boot messege"
        ck_xorplus_bootmsg
        if [ $? -eq 0 ]
        then
            process_clean_entry "sh leapsec_test.sh"
            if [ $? -ne 0 ]
            then
                exit 1
            fi
            echo "found leap second! exit~"
            send_warning "Found leap second intserting in swich!" ${SWITCH_IP}
            exit 0
        elif [ $? -eq 2 ]
        then
            echo "tcl script error!"
            exit 1      
        fi
        echo "sleep 65..."
        sleep 65
    done
}

ck_xorplus_bootmsg_main