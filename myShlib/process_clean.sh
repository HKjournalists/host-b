#!/bin/bash

##! @TODO:   验证程存在并将其清理（需要root权限）
##! @AUTHOR: wangbin19@baidu.com
##! @VERSION: 1.0_build0030

set -m
P_CL_F_NAME="process_clean.sh"  #脚本文件名

##! @TODO: 输出帮助信息
##! @AUTHOR: wangbin19@baidu.com
##! @IN: None
##! @OUT: 0 => success;
function process_clean_usage()
{
    echo -e "\n\033[36;1mUSAGE OF $0\033[0m\n" >&2
    echo -e "\033[36;1mSYNOPSIS\033[0m" >&2
    echo -e "\t $0 cmd" >&2
    echo -e "\033[36;1mOPTIONS\033[0m" >&2
    echo -e "\t cmd : program's excute command" >&2
    echo -e "\n" >&2
    return 0
}

##! @TODO: 智能kill进程
##! @AUTHOR: wangbin19@baidu.com
##! @IN: $1 => 进程pid
##! @OUT: 0 => success; 1 => failed
function process_clean_pkill()
{
    local cmd
    if [ ${UID} -eq 0 ]
    then
        cmd="kill"
    else
        cmd="kill"
    fi
    ${cmd} -15 $1 > /dev/null 2>&1
    if [ $? -ne 0 ]
    then
        ${cmd} -2 $1 > /dev/null 2>&1
        if [ $? -ne 0 ]
        then
            ${cmd} -9 $1 > /dev/null 2>&1
            if [ $? -ne 0 ]
            then
                return 1
            fi
        fi
    fi
    return 0
}

##! @TODO: 根据pid结束指定进程及其派生出的所有进程
##! @AUTHOR: wangbin19@baidu.com
##! @IN: $1 => 进程pid
##! @OUT: 0 => success; 1 => failed
function process_clean_recursive_kill()
{
    local pids=(`ps -ef | awk '{if($3 == ppid){print $2;}}' ppid=$1`)
    #echo "${#pids[@]} : ${pids[@]}"
    if [[ -z ${pids} ]]
    then
        #echo "kill child process $1"
        process_clean_pkill $1
        if [ $? -ne 0 ]
        then
            return 1
        fi
        return 0
    else
        local child
        for child in ${pids[@]}
        do
            #echo "recursive_kill ${child}"
            process_clean_recursive_kill ${child} 
        done
        local count=`ps -ef | grep $1 | grep -v "grep" | wc -l`
        if [ ${count} -eq 0 ]
        then
            return 0
        fi    
        #echo "kill process $1"
        process_clean_pkill $1
        if [ $? -ne 0 ]
        then
            return 1
        fi
    fi  
    return 0
}

##! @TODO: 验证程存在，获取pid并将其清理
##! @AUTHOR: wangbin19@baidu.com
##! @IN: $1 => 程序名
##! @OUT: 0 => success; 1 => failed
function process_clean_entry()
{
    echo "clean program : $1"
    local pids=`ps aux | grep "$1" | grep -v grep | grep -v ${P_CL_F_NAME} | awk '{print $2}'`
    #ps ax | awk '{print $1}' | grep $1
    if [[ -z ${pids} ]]
    then
        echo "$1 is not running, no need to clean"
        return 0
    fi
    echo "found processes : ${pids[@]}"
    local pid
    for pid in ${pids[@]}
    do
        process_clean_recursive_kill ${pid}
        if [ $? -ne 0 ]
        then
            echo "clean failed"
            return 1
        fi
    done  
    echo "clean success"
    return 0
}

if [[ ${0##*/} == ${P_CL_F_NAME} ]]
then
    #NOT invoked by source, exam args and call process_clean_entry
    if [ $# -ne 1 ]
    then
        process_clean_usage
        exit 1
    fi
    process_clean_entry "$1"
    if [ $? -ne 0 ]
    then
        exit 1
    fi
    exit 0
fi
#invoked by source, do nothing
#echo "invoked by source"
