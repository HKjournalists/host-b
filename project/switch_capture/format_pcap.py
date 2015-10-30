# -*- coding: utf8 -*-
#!/usr/bin/env python

################################################################################
#
# Copyright (c) 2015 Baidu.com, Inc. All Rights Reserved
#
################################################################################
"""
将日志中的十六进制格式转化为pcap文件的格式，方便查看

Authors: zhangpengfei02@baidu.com
Date:    2015/10/27 16:50:35
Todo:    加入异常判断
"""


import re
import time
import sys
import binascii

"""----------------------------------------------------------------"""
""" Do not edit below this line unless you know what you are doing """
"""----------------------------------------------------------------"""

#Global header for pcap 2.4
pcap_global_header =   ('D4 C3 B2 A1'   
                        '02 00'         #File format major revision (i.e. pcap <2>.4)  
                        '04 00'         #File format minor revision (i.e. pcap 2.<4>)   
                        '00 00 00 00'     
                        '00 00 00 00'     
                        'FF FF 00 00'     
                        '01 00 00 00')

#pcap packet header that must preface every packet
pcap_packet_header =   ('AA AA AA AA'   #Frame timestamp (seconds)  
                        'BB BB BB BB'   #Frame timestamp (micro seconds)  
                        'XX XX XX XX'   #Frame Size (little endian) 
                        'YY YY YY YY')  #Frame Size (little endian)

eth_header =   ('00 00 00 00 00 00'     #Source Mac    
                '00 00 00 00 00 00'     #Dest Mac  
                '08 00')                #Protocol (0x0800 = IP)

ip_header =    ('45'                    #IP version and header length (multiples of 4 bytes)   
                '00'                      
                'XX XX'                 #Length - will be calculated and replaced later
                '00 00'                   
                '40 00 01'                
                '59'                    #Protocol (0x59 = OSPF)          
                'YY YY'                 #Checksum - will be calculated and replaced later      
                '7F 00 00 01'           #Source IP (Default: 127.0.0.1)         
                'E0 00 00 05')          #Dest IP (Default: 225.0.0.5) 


# caculate mirco seconds ,ps: you can also get the seconds 
def get_mircosec(format_birth):
    tup_birth = time.strptime(format_birth, "%Y-%m-%d %H:%M:%S,%f")
    birth_secds = time.mktime(tup_birth)
    pattern = re.compile(r',(\d+)')
    if pattern.search(format_birth) == None:
        mirco_secds = int(birth_secds) * 1000
    else:
        res = pattern.search(format_birth).groups()
        mirco_secds = int(birth_secds) * 1000 + int(res[0])
    return mirco_secds

# read the src file and return a list about packet                
def get_pkt_list(orig_pkt_txt):
    packet_list = []
    with open(orig_pkt_txt,'r') as f:
        tmp_list = []
        for line in f:
            tmp_line = line[:-1].strip()
            if not tmp_line:
                tmp_str = ''.join(tmp_list)
                packet_list.append(tmp_str)
                tmp_list = []
                continue
            pattern = re.compile(r'(0x\w+:\s+)(.*)')
            if pattern.search(tmp_line) == None:
                #pattern_date_proto = re.compile(r'\[(\d+-\d+-\d+\s+\d+:\d+:\d+,\d+)\]\s+\[(\w+)\]')
                pattern_date_proto = re.compile(r'^\[INFO\].*\[(\d+-\d+-\d+\s+\d+:\d+:\d+,\d+)\].*layer:(\w+)')
                if pattern_date_proto.search(tmp_line) == None:
                    continue
                res_date_proto = pattern_date_proto.search(tmp_line).groups()
                date = res_date_proto[0]
                proto = res_date_proto[1]
                mirco_secds = get_mircosec(date)
                tmp_list.append(str(mirco_secds))
                tmp_list.append(' ')
                tmp_list.append(proto)
                continue
            res = pattern.search(tmp_line).groups()
            q = res[1].split()
            pattern_0x = re.compile(r'(0x(\w+))')
            for i in q:
                if pattern_0x.search(i) == None:
                    continue
                res_0x = pattern_0x.search(i).groups()
                tmp_list.append(' ')
                tmp_list.append(res_0x[1])
    if len(tmp_list) != 0:
        tmp_str = ''.join(tmp_list)
        packet_list.append(tmp_str)
    return packet_list

# caculate byte nums        
def getByteLength(str1):
    return len(''.join(str1.split())) / 2

# finaly,the data is writing in pcap file by str
def writeByteStringToFile(bytestring, filename):
    bytelist = bytestring.split()  
    bytes = binascii.a2b_hex(''.join(bytelist))
    bitout = open(filename, 'wb')
    bitout.write(bytes)

# set each packet header use for pcap format
def set_pcap_pkt_hdr(packet_time,packet_type,packet_data):
    hex_sec_time = "%08x"%(int(packet_time)/1000)
    reverse_hex_sec = hex_sec_time[6:] + hex_sec_time[4:6] + hex_sec_time[2:4] + hex_sec_time[:2]

    hex_msec_time = "%08x"%(int(packet_time)%1000)
    reverse_hex_msec = hex_msec_time[6:] + hex_msec_time[4:6] + hex_msec_time[2:4] + hex_msec_time[:2]

    if packet_type == 'l2':
        pcap_len = getByteLength(packet_data)
    elif packet_type == 'ip':
        pcap_len = getByteLength(packet_data) + getByteLength(eth_header)
    elif packet_type == 'ospf':
        pcap_len = getByteLength(packet_data) + getByteLength(ip_header) + getByteLength(eth_header) 
    else:
        pcap_len = getByteLength(packet_data)

    hex_str = "%08x"%pcap_len
    reverse_hex_str = hex_str[6:] + hex_str[4:6] + hex_str[2:4] + hex_str[:2]

    pcaph = pcap_packet_header.replace('AA AA AA AA',reverse_hex_sec)
    pcaph = pcaph.replace('BB BB BB BB',reverse_hex_msec)
    pcaph = pcaph.replace('XX XX XX XX',reverse_hex_str)
    pcaph = pcaph.replace('YY YY YY YY',reverse_hex_str)
    return pcaph

# set each packet content
def set_pcap_pkt_content(packet_type,packet_data):
    if packet_type == 'l2':
        return packet_data
    elif packet_type == 'ip':
        return eth_header + packet_data
    elif packet_type == 'ospf':
        ip_len = getByteLength(packet_data) + getByteLength(ip_header)
        ip_hdr = ip_header.replace('XX XX',"%04x"%ip_len)
        checksum = ip_checksum(ip_hdr.replace('YY YY','00 00'))
        ip_hdr = ip_hdr.replace('YY YY',"%04x"%checksum)
        return eth_header + ip_hdr + packet_data
    else:
        return packet_data

#Splits the string into a list of tokens every n characters
def splitN(str1,n):
    return [str1[start:start+n] for start in range(0, len(str1), n)]

#Calculates and returns the IP checksum based on the given IP Header
def ip_checksum(iph):
    #split into bytes    
    words = splitN(''.join(iph.split()),4)
    csum = 0;
    for word in words:
        csum += int(word, base=16)
    csum += (csum >> 16)
    csum = csum & 0xFFFF ^ 0xFFFF
    return csum

# generate pcap file
def generatePCAP(txt_file, pcap_file): 
    pkt_list = get_pkt_list(txt_file)
    bytestring = pcap_global_header
    for packet in pkt_list:
        pattern = re.compile(r'(\d+) (\w+) (.*)')
        res = pattern.search(packet).groups()
        packet_time = res[0]
        packet_type = res[1]
        packet_data = res[2]

        pcaph = set_pcap_pkt_hdr(packet_time, packet_type, packet_data)
        packet_content = set_pcap_pkt_content(packet_type, packet_data)
        bytestring += pcaph + packet_content
    writeByteStringToFile(bytestring, pcap_file)


"""------------------------------------------"""
""" End of functions, execution starts here: """
"""------------------------------------------"""

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print 'usage: pcapgen.py input_file output_file'
        exit(0)

    generatePCAP(sys.argv[1],sys.argv[2])

