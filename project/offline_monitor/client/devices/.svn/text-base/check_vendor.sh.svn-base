#/bin/sh
while read line
do
    # the version for 192.168.225.79 in QD01 is too old,1.0.1.2
    if [ $line == "192.168.225.79" ];then
         echo "$line LY2R" >> vendor.tmp
    else
        snmpwalk -cpublic -v2c $line  sysdesc > tmp.log
        if [[ $? == 0 ]];then
            echo -n $line " " >> vendor.tmp
            cat tmp.log | awk '{print $16}' >> vendor.tmp
        else
            rm -rf tmp.log
            rm -rf vendor.tmp
            exit 1
        fi
    fi
done < ip_ok_baidu.txt
rm -rf vendor.txt
mv vendor.tmp vendor.txt
rm -rf tmp.log
