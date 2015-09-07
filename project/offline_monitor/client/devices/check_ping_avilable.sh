#/bin/sh

cp -f /home/wangbin/project/monitor/client/ip_all.txt /home/wangbin/project/monitor/client/devices/ip_all.txt
cat ip_all.txt | grep 192.168. | xargs -n 1 ping -c 1 -w 1 > ping.log
cat ping.log | grep -B 1  "100% packet loss" | grep statistics | awk '{print $2}' > ip_fail.txt
cat ping.log  | grep "64 bytes from" | awk '{print $4}'| awk -F : '{print $1}' > ip_ok.txt
rm -rf ping.log
