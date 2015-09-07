#!/bin/bash

##! @TODO:   MTP闰秒测试
##! @AUTHOR: wangbin19@baidu.com
##! @VERSION: 1.0_build0020

LEAP_TIME="2015-07-01 07:50:00"
LEAP_SCRIPT="/home/wuxiaoying/leap_second.pl"
LEAP_LOG="leapsec_test.log"
SWITCH_IP="192.168.30.25"
NTP_SERVER1="192.168.30.111"
NTP_SERVER2="192.168.30.92"

##! @TODO: 验证程存在并将其清理
##! @AUTHOR: wangbin19@baidu.com
##! @IN: $1 => 程序名
##! @OUT: 0 => success; 1 => failed
function ps_clean()
{
    local pid=`ps aux | grep "$1" | grep -v grep | awk '{print $2}'`
    #ps ax | awk '{print $1}' | grep $1
    if [[ -z ${pid} ]]
    then
        echo "$1 is not running, no need to clean"
        return 0
    fi
    recursive_kill ${pid}
    if [ $? -ne 0 ]
    then
        echo "clean failed"
        return 1
    fi
    echo "clean success"
    return 0
}

##! @TODO: 结束指定进程及其派生出的所有进程
##! @AUTHOR: wangbin19@baidu.com
##! @IN: $1 => 进程pid
##! @OUT: 0 => success; 1 => failed
function recursive_kill()
{
    local pids=(`ps -ef | awk '{if($3 == ppid){print $2;}}' ppid=$1`)
    #echo "${#pids[@]} : ${pids[@]}"
    if [[ -z ${pids} ]]
    then
        echo "kill child process $1"
        sudo kill -9 $1
        if [ $? -ne 0 ]
        then
            return 1
        fi
        return 0
    else
        for child in ${pids[@]}
        do
            #echo "recursive_kill ${child}"
            recursive_kill ${child} 
        done
        local count=`ps -ef | grep $1 | grep -v "grep" | wc -l`
        if [ ${count} -eq 0 ]
        then
            return 0
        fi    
        echo "kill process $1"
        sudo kill -9 $1
        if [ $? -ne 0 ]
        then
            return 1
        fi
    fi  
    return 0
}

##! @TODO: 释放端口
##! @AUTHOR: wangbin19@baidu.com
##! @IN: $1 => 端口号
##! @OUT: 0 => success; 1 => failed;
function port_release()
{

    return 0
}

if [ ! -f ${LEAP_LOG} ]
then
    touch ${LEAP_LOG}
    if [ $? -ne 0 ]
    then
        exit 1
    fi
    chmod 777 ${LEAP_LOG}
fi
sudo chmod 777 ${LEAP_SCRIPT}
i=1
while [[ 1 ]]
do
    sudo date -s "${LEAP_TIME}" >> ${LEAP_LOG} 2>&1
    if [ $? -ne 0 ]
    then
        exit 1
    fi
    ps_clean "sudo perl -wT ${LEAP_SCRIPT}" >> ${LEAP_LOG} 2>&1
    if [ $? -ne 0 ]
    then
        exit 1
    fi
    sleep 5
    sudo perl -wT ${LEAP_SCRIPT} >> ${LEAP_LOG} 2>&1 &
    if [ $? -ne 0 ]
    then
        exit 1
    fi
    expect leapsec_test.tcl ${SWITCH_IP} ${NTP_SERVER1} ${NTP_SERVER2} >> ${LEAP_LOG} 2>&1
    if [ $? -ne 0 ]
    then
        exit 1
    fi
    echo "=========================${i}===========================" >> ${LEAP_LOG}
    i=$((i+1))
    sleep 1200
done