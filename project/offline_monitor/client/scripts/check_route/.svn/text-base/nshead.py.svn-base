#!/usr/bin/evn python


import struct

def make_nshead(length):
    nshead = {
        "id" : 0,
        "verison" : 1,
        "log_id" : 0,
        "provider" : "UDA",
        "magic_num" : 0xfb709394,
        "reserved" : 0,
        "body_len" : length,
        }
    header = []
    for i in ["id", "verison", "log_id", "provider", "magic_num", "reserved", "body_len"]:
        header.append(nshead[i])
    header_p = struct.pack("2HI16s3I", *header)
    
    return header_p

def parse_nshead(header):
    return struct.unpack("2HI16s3I", header)
