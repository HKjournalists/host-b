#/bin/sh
while read line
do
    # the version for 192.168.225.79 in QD01 is too old,1.0.1.2
    if [ $line == "192.168.225.79" ];then
        echo "$line" >> ip_not_1062.tmp
    else
        echo -n "$line : " > tmp.log
        snmpwalk -cpublic -v2c $line sysdesc  >> tmp.log
        if [[ $? == 0 ]];then
            cat tmp.log | grep 1.0.6.2 | awk '{print $1}' >> ip_1062.tmp
            cat tmp.log | grep -v 1.0.6.2 | awk '{print $1}' >> ip_not_1062.tmp 
        else
            rm -rf tmp.log
            rm -rf ip_ok_tmp.txt
            rm -rf ip_1062.tmp
            rm -rf ip_not_1062.tmp
            exit 1
        fi
    fi
done < ip_ok_baidu.txt

while read line
do
    ip=`echo $line | awk '{print $1}'`
    echo -n "$line " >> ip_vendor_version.tmp
    
    # the version for 192.168.225.79 in QD01 is too old,1.0.1.2
    if [ $ip == "192.168.225.79" ];then
        echo "1.0.1.2" >> ip_vendor_version.tmp
    else
        snmpwalk -cpublic -v2c $ip sysdesc  > tmp.log
        if [[ $? == 0 ]];then
            cat tmp.log | awk '{print $9}' | awk -F @ '{print $1}' >> ip_vendor_version.tmp
        else
            rm -rf tmp.log
            rm -rf ip_vendor_version.tmp
            exit 1
        fi
    fi
done < vendor.txt

rm -rf ip_1062.txt
rm -rf ip_not_1062.txt
mv ip_1062.tmp ip_1062.txt
mv ip_not_1062.tmp ip_not_1062.txt
mv ip_vendor_version.tmp ip_vendor_version.txt
rm -rf tmp.log
