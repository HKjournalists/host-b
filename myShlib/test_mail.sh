#!/bin/bash

##! @TODO:   发送邮件
##! @AUTHOR: wangbin19@baidu.com
##! @VERSION: 1.0_build0010

MAIL_MEMBER="wangbin19@baidu.com" 
ALERT_TITEL="Switch Alert: "
IDC_NAME="BB"
DEV_INFO="192.168.30.25 LY2R 1.0.7.2"

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

send_warning "Found leap second intserting in swich!" "${DEV_INFO}"