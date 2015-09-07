#!/bin/bash
##! @TODO:   线下交换机监控主程序
##! @AUTHOR: wangbin19@baidu.com
##! @VERSION: 1.0_build0010

#client目录路径
MONITOR_CLIENT_PATH=/home/wangbin/project/offline_monitor/client
#collect主程序路径
COLLECTD_BIN_PATH=/home/wangbin/soft/collectd/sbin/collectd
#collect日志文件路径
COLLECTD_LOG_PATH=${MONITOR_CLIENT_PATH}/collectd/collectd.log
#collect配置文件路径
COLLECTD_CONF_PATH=${MONITOR_CLIENT_PATH}/collectd/collectd.conf

##! @TODO: 输出帮助信息
##! @AUTHOR: wangbin19@baidu.com
##! @IN: None
##! @OUT: 0 => success;
function monitor_usage()
{
    echo -e "Usage: $0" >&2
    echo -e "\t start 开始监控" >&2
    echo -e "\t stop 终止监控" >&2
    echo -e "\t restart 重启监控" >&2
    return 0
}

##! @TODO: 根据功能调用对应函数
##! @AUTHOR: wangbin19@baidu.com
##! @IN: $1: 执行功能（start、stop、restart）
##! @OUT: 0 => success; 1 => failed
function exec_func()
{
	eval "monitor_$1" 2>/dev/null
	local ret=$?
	if [[ ${ret} -eq 127 ]]
	then
		monitor_usage
		return 1
	elif [[ ${ret} -ne 0 ]]
	then		
		return 1
	fi
	return 0
}

##! @TODO: 开始监控
##! @AUTHOR: wangbin19@baidu.com
##! @IN: None
##! @OUT: 0 => success; 1 => 设置权限失败; 2 => 创建日志文件失败;
function monitor_start()
{
	echo "start monitor"
	if [ ! -f ${COLLECTD_LOG_PATH} ]
	then
		sudo -S touch ${COLLECTD_LOG_PATH}
		if [ $? -ne 0 ]
		then
			echo "can't create log file ${COLLECTD_CONF_PATH} !"
			return 2
		fi
	fi
	sudo -S chmod 777 ${COLLECTD_LOG_PATH}
	if [ $? -ne 0 ]
	then
		echo "can't mod authority of log file!"
		return 1
	fi
	sudo -S ${COLLECTD_BIN_PATH} -C ${COLLECTD_CONF_PATH}
	echo "monitor is running"
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
        #echo "kill child process $1"
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
        #echo "kill process $1"
        sudo kill -9 $1
        if [ $? -ne 0 ]
        then
            return 1
        fi
    fi  
    return 0
}

##! @TODO: 验证程存在并将其清理
##! @AUTHOR: wangbin19@baidu.com
##! @IN: None
##! @OUT: 0 => success; 1 => failed
function monitor_stop()
{
    local pid=`ps aux | grep ${COLLECTD_BIN_PATH} | grep -v grep | awk '{print $2}'`
    if [[ -z ${pid} ]]
    then
        echo "${COLLECTD_BIN_PATH} is not running, no need to clean"
        return 0
    fi
    recursive_kill ${pid}
    if [ $? -ne 0 ]
    then
        echo "stop failed"
        return 1
    fi
    echo "monitor stopped"
    return 0
}

##! @TODO: 重启监控
##! @AUTHOR: wangbin19@baidu.com
##! @IN: None
##! @OUT: 0 => success; 1 => failed
function monitor_restart()
{
	monitor_stop
	if [ $? -ne 0 ]
	then
		return 1
	fi
	monitor_start
	if [ $? -ne 0 ]
	then
		return 1
	fi
	return 0
}

##! @TODO: 主函数
##! @AUTHOR: wangbin19@baidu.com
##! @IN: $1: 执行功能（start、stop、restart）
##! @OUT: 0 => success; 1 => failed
function monitor_main()
{
	if [ $# -ne 1 ]
    then
        monitor_usage
        exit 1
    fi
    exec_func $1
    if [ $? -ne 0 ]
	then
		exit 1
	fi
	exit 0
}

monitor_main $*
