#/bin/sh
while read line
do
    # the version for 192.168.225.79 in QD01 is too old,1.0.1.2
    if [ $line == "192.168.225.79" ];then
         echo $line  >> ip_ok_baidu.tmp
    else
        echo -n $line >> tmp.log
        snmpwalk -cpublic -v2c $line  sysdesc > tmp.log
        if [[ $? == 0 ]];then
            cat tmp.log | grep Baidu > /dev/null 
            if [[ $? == 0 ]];then
                echo $line >> ip_ok_baidu.tmp
            fi
        else
            rm -rf tmp.log
            rm -rf ip_ok_baidu.tmp
            exit 1
        fi
    fi
done < ip_ok.txt
rm -rf ip_ok_baidu.txt
mv ip_ok_baidu.tmp ip_ok_baidu.txt
rm -rf tmp.log
