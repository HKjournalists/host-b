#!/bin/sh

RESULT_FILE=all.txt

IDC_INFO=../../config/idc/idc.conf
MONITOR_PATH=/home/nsi/switch/monitor

vendorlist="Celestica Ruijie Quanta Foxconn"
Celestica_modellist="D2020 REDSTONE"
Ruijie_modellist="S6220 B6220 B6220V2"
Quanta_modellist="LY2R LY2"
Foxconn_modellist="2G48S4Q"

#idclist="NMG01 NJ02 QD01 SH01 NB01 YQ01 SZWG"

if [ -z "$1" ] ; then
    idclist="`cat $IDC_INFO`"
else
    idclist=$1
fi

echo "IDC List: $idclist"

rm -rf *.txt

echo  "========================"
echo  "===    for vendor    ==="
echo  "========================"

for vendor in ${vendorlist}
do
    echo "${vendor}"
    modellist=${vendor}_modellist
    for model in ${!modellist} 
    do
        #echo "${vendor}:${model}" >> ${RESULT_FILE}
        xfind "${model}-" | grep -v "Conditions" >> ${RESULT_FILE}
        echo -n "    ${model}: "
        echo `cat ${RESULT_FILE} | grep "${model}-" | grep -v ${vendor} | wc -l`
    done
done

echo  "========================"
echo  "===    for idc       ==="
echo  "========================"

for idc in ${idclist}
do
    if [ ${idc}x = "SZWG01"x ];then
        idc="SZWG"
    fi

    echo -n "${idc}: "
    echo `cat ${RESULT_FILE} | grep ${idc} | wc -l`
    cat ${RESULT_FILE} | grep ${idc} | grep -v CDN | awk '{print $1}'| grep -v -E "224.240|224.243|224.204|224.234|224.237" > ${idc}.txt
    if [ ${idc}x = "SZWG"x ];then
        scp ${idc}.txt nsi@szwg-sys-netadmin00.szwg01:$MONITOR_PATH/ip_all.txt > /dev/null
    else
        scp ${idc}.txt nsi@${idc}-sys-netadmin00.${idc}:$MONITOR_PATH/ip_all.txt > /dev/null
    fi
    for vendor in ${vendorlist}
    do
        modellist=${vendor}_modellist
        for model in ${!modellist}
        do
            echo -n "    ${model}: "
            echo `cat ${RESULT_FILE} | grep ${idc} | grep "${model}-" | grep -v ${vendor} | wc -l`
        done
    done
done

echo  "========================"
echo  "===     Totals       ==="
echo  "========================"

cat ${RESULT_FILE} | grep -E "D2020|d2020|Redstone|REDSTONE|LY2R|ly2r|B6220|b6220" > baidu.txt
cat ${RESULT_FILE} | grep -v -E "D2020|d2020|Redstone|REDSTONE|LY2R|ly2r|B6220|b6220" > others.txt
echo -n "Totals: "
echo `cat ${RESULT_FILE} | wc -l`
echo -n "    Baidu: "
echo `cat baidu.txt | wc -l`
echo -n "    Others: "
echo `cat others.txt | wc -l`
