#!/bin/bash


function loop()
{
	port=65530
	while [ ${port} -le 65535 ]
	do
		port=1
	done			
}

#./mini_http_server/bin/mini_http_server &
#sleep 1
#echo -e "\n"
#jobs -l | grep mini_http_server | awk '{print $3}'
function fread()
{
	local line
	while read line
	do
		echo $line
	done < tester.conf
	local line
    while read line
    do
        echo $line
    done < ${data_file}
}
function awkfun()
{
	local file="mini_http_server/data/name_id_value_dict"
	echo ${file}
	awk 'BEGIN{
        }
        {
            if(NF == 3 && $2~/^[1-9][0-9]*$/){  
                printf("%s %s %s\n", $1, $2, $3);  
            }
        }
        END{
        }' ${file} >> log
}

function parselog()
{
	echo $1
	eval `awk 'BEGIN{
            total_query = 0;
            succ_query = 0;
            value_count = 0;
            value_sum = 0;
            date_flag = 0;
        }
        {
            if (NF == 13) {   
            	#print $0;
                total_query += 1;  #总请求数
                if (split($8, succ, "=") == 2) {
                    succ_query += succ[2];  
                }
                if (split($11, name, "=") == 2) {
                    str = name[2];
                    names[str] += 1;      
                }
                if (split($13, val, "=") == 2) {
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
        END{
        	count = 0
        	for (i in names) {
        		count += 1;
        	}
            #printf("total_query=%d\n", total_query);
            #printf("succ_query=%d\n", succ_query);
            #printf("value_count=%d\n", value_count);
            #printf("value_sum=%.2f\n", value_sum);
            printf("local value_avg=%.2f\n", value_sum / value_count);
            printf("local succ_rate=%.2f%\n", succ_query / total_query * 100.0);
            printf("local name_num=%d\n", count);
            printf("local start_time=%s\n", date["start"]);
            printf("local end_time=%s\n", date["end"]);
        }' $1`
}

function temp()
{
    
    mv ${data_file} ${data_file_bak}
    if [ $? -ne 0 ]
    then
        echo "back up name_id_value_dict failed" >&2
        return 1
    fi
    touch ${data_file}
    awk '{
            if(NF == 3 && $2~/^[1-9][0-9]*$/){  
                printf("%s %s %s\n", $1, $2, $3);  
            }
        }' ${data_file_bak} >> ${data_file}

    eval `awk '
        BEGIN{
            FS="=";
        }
        {
            if($0 !~ /^#.*$/ && NF == 2){   #跳过无效行和注释行
                printf("%s=%s;", $1, $2);  #读取配置文件并创建全局变量
            }
        }
        END{
            printf("\n");
        }' $1`
    return 0
}

function awk2()
{
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
                if (split($13, val, "=") == 2) {
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
                printf("echo %s", names[i]);
                count += 1;
            }
            
        }' $1`
}

dirname $1