
SMS_SERVER="-s emp01.baidu.com:15004 -s emp02.baidu.com:15004"
#ALERT_MEMBER="18911728840 18611088822"
#MAIL_MEMBER="tianye09@baidu.com luofeng@baidu.com"
ALERT_MEMBER="13121678482"
MAIL_MEMBER="wangbin19@baidu.com wuxiaoying01@baidu.com zhangpengfei02@baidu.com zhuozecheng01@baidu.com" 

ALERT_TITEL="Switch Alert: "

cd `dirname $0`
SCRIPT_PATH=${PWD}
SCRIPT_NAME=${PWD##*/}
LOG_FILE=$SCRIPT_NAME.log
#IDC_NAME=`hostname | awk -F . '{ print $2 }' | tr "[a-z]" "[A-Z]"`
IDC_NAME="BB"

sms_send()
{
    #for cell_num in $ALERT_MEMBER
    #do
    #    /bin/gsmsend $SMS_SERVER $cell_num@"$1"
    #done
    return 0
}

mail_send()
{
    /bin/mail -v -s "$IDC_NAME $ALERT_TITEL $ALERT_TYPE" "$MAIL_MEMBER" <"$1"
}

send_warning()
{
    #printf "`date +"%Y-%m-%d %H:%M:%S"` Switch:\n$2\n">>$LOG_FILE
    #sms_send "$IDC_NAME:Switch[$2] $ALERT_TYPE Alert at `date +"%Y-%m-%d %H:%M:%S"` $1"

    ALERT_TYPE=$0
    ALERT_TYPE=${ALERT_TYPE##*/}
    ALERT_TYPE=${ALERT_TYPE%.*}
    printf "IDC:\t\t\t$IDC_NAME\n">temp_mail
    printf "Date:\t\t`date +"%Y-%m-%d %H:%M:%S"`\n">>temp_mail
    printf "Alert Type:\t$ALERT_TYPE\n">>temp_mail
    printf "Alert Info:\t$1\n">>temp_mail
    printf "Switch Info:\n----------------\n$2\n">>temp_mail
    #printf "`date +"%Y-%m-%d %H:%M:%S"` Switch:\n$2">temp_mail

    #user extended info
    if [ -n "$3" ] ; then
        printf "\n----------------\n$3\n">>temp_mail
    fi

    mail_send temp_mail

    printf "`date +"%Y-%m-%d %H:%M:%S"` Switch Alert $ALERT_TYPE:\n$2\n">>$LOG_FILE
    sms_send "$IDC_NAME:Switch[$2] $ALERT_TYPE Alert at `date +"%Y-%m-%d %H:%M:%S"` $1"
    #sms_send "IDC:\t\t\t$IDC_NAME\nDate:\t\t`date +"%Y-%m-%d %H:%M:%S"`\nSwitch IP:\t\t$2\nAlert type:\t$ALERT_TYPE\nAlert Info:\t$1\n"
}

check_iplist_ready()
{
    while [[ 1 ]]
    do
        if [ ! -s $SCRIPT_PATH/../../devices/ip_vendor_version.txt ] ; then
            echo "No switch IP info found, waiting..">>$LOG_FILE
            sleep 30
            continue
        else
            cp -f $SCRIPT_PATH/../../devices/ip_vendor_version.txt ip.txt
            sed -i '/^\s*$/d' ip.txt
            skip_ip_mask
            break
        fi
    done
}

skip_ip_mask()
{
    if [ -s ip_mask.txt ] ; then
        while read line
        do
            sed -i '/'"$line"'/d' ip.txt
        done < ip_mask.txt
    fi
}
