#!/bin/bash
##! @TODO:   简易测试框架
##! @AUTHOR: wangbin19@baidu.com
##! @VERSION: 1.0_build0001
##! @FILEIN: ./tester.conf
##! @FILEOUT: ./mini_tester_result.log

#全局变量
set -m
SCRIPT_VERSION="1.0_build0010"
BASE_PATH=$(cd `dirname $0`; pwd)
#MT_FINAL_LOG="${BASE_PATH}/${LOG_RESULT_PATH}"
PROGRAM_NAME="mini_http_server"  #待测项目主程序名
PROGRAM_PORT="65001" #待测项目端口

##! @TODO: 输出帮助信息
##! @AUTHOR: wangbin19@baidu.com
##! @IN: None
##! @OUT: 0 => success;
function mini_tester_usage()
{
    echo -e "Usage: $0" >&2
    echo -e "\t-c 配置文件" >&2
    echo -e "\t-h 帮助信息" >&2
    echo -e "\t-v 版本信息" >&2
    return 0
}

##! @TODO: 初始化函数，包括读取配置文件、下载项目文件、配置环境、开始测试工作
##! @AUTHOR: wangbin19@baidu.com
##! @IN: $1: 配置文件名
##! @OUT: 0 => success
##! @OUT: 1 => 后续函数执行失败
##! @OUT: 2 => 找不到配置文件
##! @OUT: 3 => 全局变量初始化失败
function mini_tester_start()
{
    local cfg=$1
    if [[ ! -f ${cfg} ]]
    then
        cfg="${BASE_PATH}/../conf/${1##*./}"
        if [[ ! -f ${cfg} ]]
        then
            echo "can't find config file" >&2
            return 2
        fi
    fi
    #source "${BASE_PATH}/${1##*./}"
    source ${cfg}
    #参数检查
    declare -a cfg_arr
    cfg_arr=(MUT_PATH QUERY_LIST_PATH QUERY_LIST_NAME QUERY_LIST_MD5 \
                   RESPONSE_PATH LOG_RESULT_PATH)
    local i
    for i in ${cfg_arr[*]}
    do 
        #echo -n "${i}="
        i=`eval echo $\`echo "${i}"\``
        #echo "${i}"
        if [[ "${i}" == "" ]]
        then 
            echo "can't init global variable ${i}, please check the config file"
            return 3
        fi
    done               
    local put_name=${MUT_PATH##*/}            #待测项目压缩包文件名
    local put_path="${BASE_PATH}/${put_name%%.*}"  #待测项目的根目录路径
    rm -rf ${put_name} ${put_path} ${QUERY_LIST_NAME} ${QUERY_LIST_MD5}
    mini_tester_download ${put_name}
    if [[ $? -ne 0 ]]
    then
        return 1
    fi
    mini_tester_run ${put_path} ${PROGRAM_NAME}
    if [[ $? -ne 0 ]]
    then
        return 1
    fi
    return 0
}

##! @TODO: 下载待测项目文件，验证MD5，解压缩文件
##! @AUTHOR: wangbin19@baidu.com
##! @IN: $1 => 待测项目压缩包本地文件名
##! @OUT: 0 => success
##! @OUT: 1 => 下载文件失败
##! @OUT: 2 => MD5检查失败
##! @OUT: 3 => 解压缩失败
function mini_tester_download()
{
    mini_tester_wget "./$1" "${MUT_PATH}"
    if [[ $? -ne 0 ]]
    then
        return 1
    fi  
    mini_tester_wget "./${QUERY_LIST_NAME}" "${QUERY_LIST_PATH}${QUERY_LIST_NAME}"
    if [[ $? -ne 0 ]]
    then
        return 1
    fi
    mini_tester_wget "./${QUERY_LIST_MD5}" "${QUERY_LIST_PATH}${QUERY_LIST_MD5}"
    if [[ $? -ne 0 ]]
    then
        return 1
    fi
    md5sum -c "${QUERY_LIST_NAME}.md5" > /dev/null
    if [[ $? -ne 0 ]]
    then
        echo "md5 check failed" >&2
        return 2
    fi
    tar -xzf ./$1
    if [[ $? -ne 0 ]]
    then
        echo "uncompress failed" >&2
        return 3
    fi
    return 0
}

##! @TODO: wget下载文件
##! @AUTHOR: wangbin19@baidu.com
##! @IN: $1 => 本地文件名
##! @IN: $1 => 带下载文件url
##! @OUT: 0 => success
##! @OUT: 1 => 下载文件失败
function mini_tester_wget()
{
    echo "downloading files $2" >&2
    wget -q -t 5 -O $1 $2
    if [[ $? -ne 0 ]]
    then
        echo "download $2 failed!" >&2
        rm -f $1
        return 1
    fi  
    return 0
}

##! @TODO: 对port和data_path两项配置进行本地化，执行测试主体
##! @AUTHOR: wangbin19@baidu.com
##! @IN: $1 => 待测项目的根目录路径
##! @IN: $2 => 待测项目的主程序名
##! @OUT: 0 => success
##! @OUT: 1 => 后续脚本执行失败
##! @OUT: 2 => 找不到配置文件
##! @OUT: 3 => 环境设置失败
function mini_tester_run()
{
    #逐行读取数据文件，过滤非法数据
    local data_file="$1/data/name_id_value_dict"
    echo ${data_file}
    if [[ ! -f ${data_file} ]]
    then
        echo "can't find name_id_value_dict" >&2
        return 2
    fi
    local log_path="$1/log/server.log"
    #if [[ ! -f ${log_path} ]]
    #then
    #    echo "can't find server.log" >&2
    #    return 2
    #fi
    #local data_file_bak="${data_file}.bak"
    local port=${PROGRAM_PORT}   #寻找可用端口
    declare -a rets
    while [[ ${port} -le 65535 ]]   
    do
        netstat -nta | grep -q ${port}
        rets=(${PIPESTATUS[*]})
        #echo "${rets[*]}"
        if [[ ${rets[0]} -eq 0 && ${rets[1]} -eq 1 ]]
        then
            echo "find an available port: ${port}"
            break
        fi
        port=`expr ${port} + 1`
    done
    if [[ ${port} -eq 65536 ]]  #没有查到可用端口
    then
        echo "can't find an available port!" >&2
        return 3
    fi
    #将数据文件路径中的反斜线替换为转义字符，用于通过sed修改data_path属性
    data_file=$(echo "${data_file}" | sed 's/\//\\&/g')  
    sed -i -e "s/port.*/port: ${port}/g" \
           -e "s/data_path.*/data_path: ${data_file}/g" $1/conf/server.conf
    if [[ $? -ne 0 ]]
    then
        echo "edit program's config file failed" >&2
        return 3
    fi
    mini_tester_exec $1 $2
    if [[ $? -ne 0 ]]
    then
        return 1
    fi
    mini_tester_do_test ${port} $1 $2
    if [[ $? -ne 0 ]]
    then
        return 1
    fi
    mini_tester_parse_result ${log_path} 
    if [[ $? -ne 0 ]]
    then
        return 1
    fi
    return 0
}

##! @TODO: 执行程序
##! @AUTHOR: wangbin19@baidu.com
##! @IN: $1 => 待测项目的根目录路径
##! @IN: $2 => 待测项目的主程序名
##! @OUT: 0 => success
##! @OUT: 1 => 参数错误
##! @OUT: 2 => 执行程序错误
function mini_tester_exec()
{
    if [[ ! -d $1 ]]
    then
        echo "$1 is not a directory"
        return 1
    fi
    if [[ -z $2 ]]
    then
        echo "$2 not exists"
        return 1
    fi
    local pid=$(pgrep -f "$2" | wc -l)
    if [[ ${pid} -ne 0 ]]
    then
        mini_tester_clean $2
        if [[ $? -ne 0 ]]
        then
            echo "kill exsiting processes failed!" >&2
            return 2
        fi
    fi
    #按照题目说明，待测项目主程序只需要直接执行即可。但实际测试发现若在bin目录中执行程序，
    #程序执行失败并提示找不到conf文件夹中的文件，因此需要将其复制到项目根目录下才能正常执行。
    cp "$1/bin/$2" "$1/"
    if [[ $? -ne 0 ]]
    then
        echo "copy main program to project's base path failed!" >&2
        return 2
    fi
    cd $1
    chmod 777 $2
    if [[ $? -ne 0 ]]
    then
        echo "chmod failed!" >&2
        return 2
    fi
    sleep 2
    #执行待测程序（使用eval计算出$2的值，否则稍后kill进程时会输出多余信息）
    eval "./$2" >/dev/null 2>&1 &  
    sleep 2
    pid=$(pgrep -f $2)  #确认是否成功运行
    if [[ -z ${pid} ]]
    then
        echo "excute program failed!" >&2
        return 2
    fi
    echo "program is running"
    cd ${BASE_PATH}
    return 0
}

##! @TODO: 清理进程
##! @AUTHOR: wangbin19@baidu.com
##! @IN: $1 => 待测清理的程序名
##! @OUT: 0 => success; 1 => failed
function mini_tester_clean()
{
    #pgrep -f $1 | xargs -I {} kill -2 {}
    #if [[ ${PIPESTATUS[0]} -ne 0 || ${PIPESTATUS[1]} -ne 0 ]]
    kill -2 `pgrep -f "$1"`
    if [[ $? -ne 0 ]]
    then
        return 1
    fi
    local count=$(pgrep -f "$1" | wc -l)
    if [[ ${count} -ne 0 ]]
    then
        kill -9 `pgrep -f $1`  #强制结束进程
        if [[ $? -ne 0 ]]
        then
            return 1
        fi
    fi
    return 0
}

##! @TODO: 进行测试，包括向程序发送请求词表、保存返回结果、结束程序并分析
##! @AUTHOR: wangbin19@baidu.com
##! @IN: $1 => 待测项目主程序监听的端口号
##! @IN: $2 => 待测项目的根目录路径
##! @IN: $3 => 待测项目的主程序名
##! @OUT: 0 => success
##! @OUT: 1 => 参数出错
##! @OUT: 2 => 发送请求时出错
##! @OUT: 3 => 停止程序失败
function mini_tester_do_test()
{
    if [[ $1 -lt 1024 || $1 -gt 65535 ]]
    then
        echo "illegal port : $1"
        return 1
    fi
    if [[ ! -d $2 ]]
    then
        echo "$2 is not a directory"
        return 1
    fi
    if [[ -z $3 ]]
    then
        echo "$3 not exists"
        return 1
    fi
    rm -rf ${RESPONSE_PATH}
    if [[ $? -ne 0 ]]
    then
        return 1
    fi
    touch ${RESPONSE_PATH}
    local url_base="http://127.0.0.1"
    local line
    while read line
    do
        curl -s "${url_base}:$1$line" >> ${RESPONSE_PATH} 2>/dev/null
        if [[ $? -ne 0 ]]
        then
            echo "query failed : ${url_base}:$1$line"
            return 2
        fi
    done < ${QUERY_LIST_NAME}
    mini_tester_clean $3
    if [[ $? -ne 0 ]]
    then
        echo "stop program failed!" >&2
        return 3
    fi
    echo "program completed"
    return 0
}

##! @TODO: 分析测试结果
##! @AUTHOR: wangbin19@baidu.com
##! @IN: $1 => 待测项目日志路径
##! @OUT: 0 => success; 1 => failed
function mini_tester_parse_result()
{
    rm -rf ${LOG_RESULT_PATH} 
    if [[ $? -ne 0 ]]
    then
        echo "rm log files failed!" >&2
        return 1
    fi
    touch ${LOG_RESULT_PATH}
    eval `awk 'BEGIN {
            total_query = 0;
            succ_query = 0;
            value_count = 0;
            value_sum = 0;
            date_flag = 0;
        }
        {
            if (NF == 13) {   
                #print $0;
                total_query += 1; 
                if (split($8, succ, "=") == 2) {
                    succ_query += succ[2];  
                }
                if (split($11, name, "=") == 2 && name[2] != null) {
                    str = name[2];      
                    names[str] += 1; 
                }
                if (split($13, val, "=") == 2 && val[2] != null) {
                    value_count += 1; 
                    value_sum += val[2];          
                }
                if (date_flag == 1) {
                    date["end"]=$2" "$3;   
                }
                else {
                    date["start"] = $2" "$3;   
                    date_flag = 1;           
                }               
            }
        }
        END {
            count = 0
            for (i in names) {
                count += 1;
            }
            printf("local total_query=%d\n", total_query);
            printf("local value_avg=%.2f\n", value_sum / value_count);
            printf("local succ_rate=%.2f%\n", succ_query / total_query * 100.0);
            printf("local name_num=%d\n", count);
            printf("local start_time=\"%s\"\n", date["start"]);
            printf("local end_time=\"%s\"\n", date["end"]);
        }' $1`
    local year=`date +%Y`
    start_time=`date -d "${year}-${start_time%:}" +%s`
    end_time=`date -d "${year}-${end_time%:}" +%s`
    local cost=`expr ${end_time} - ${start_time}`
    local qps=`expr ${total_query} / ${cost}`
    echo "qps=${qps}" >> ${LOG_RESULT_PATH}
    echo "value_avg=${value_avg}" >> ${LOG_RESULT_PATH}
    echo "succ_rate=${succ_rate}" >> ${LOG_RESULT_PATH}
    echo "name_num=${name_num}" >> ${LOG_RESULT_PATH}
    echo "test complete, result has been saved in ${LOG_RESULT_PATH}"
    return 0
}

##! @TODO: 主函数
##! @AUTHOR: wangbin19@baidu.com
##! @IN: $1: 选项（-c、-v、-h）
##! @IN: $2: 选项为-c时的配置文件路径
##! @OUT: 0 => success; 1 => failed
function mini_tester_main() 
{
    if [[ $# -eq 0 ]]
    then
        mini_tester_usage
        return 1
    fi
    while getopts c:hv OPTION        
    do
        case $OPTION in
            c) local cfg_file="${OPTARG}"
            ;;
            h) mini_tester_usage; return 0
            ;;
            v) echo "$0 ${SCRIPT_VERSION}" >&2; return 0
            ;;
            \?) mini_tester_usage; return 1
            ;;
        esac
    done
    if [[ "${cfg_file}" == "" ]]
    then
        echo -e "错误：未指定配置文件\n原因：缺少参数 -c" >&2
        return 1
    fi
    mini_tester_start ${cfg_file}
    if [[ $? -ne 0 ]]
    then
        return 1
    fi
    return 0
}

if [[ ${0##*/} == "mini_tester.sh" ]]
then
    #NOT invoked by source
    mini_tester_main $*
fi








