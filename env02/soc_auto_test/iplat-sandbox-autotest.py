#!/usr/bin/env python
#-*- coding: utf-8 -*-
import errno
import functools
import socket
from tornado import ioloop, iostream
from multiprocessing import Process
from redis import ConnectionError
import time
import json
import os
import hashlib   #Python2.5 or later version  
import fcntl
import sys
import uuid
import redis
import threading
import struct
import types


#sys.path.append("./logmodule/")
#from LogModule import LogModule

sys.path.append("./lib/soc/util/")
sys.path.append("./lib/")
from zkredis import ZkRedis
from msgqueue import MsgQueue
from LogModule import LogModule

today=time.strftime("%Y-%m-%d", time.localtime())
filename = 'nacs.log.'+str(today)
TEST_ZKHOST="127.0.0.2:2181"
WHITELIST_SWITCH = 0 # 1: no whitelist check, 0: whitelist check
WHITELIST = ('10.65.16.248', # rms.baidu.com
             '10.36.24.12',  # rms bae
             '10.26.40.20',  # rms bae
             '10.26.40.21',  # rms bae
             '10.36.24.11',  # rms bae
             '10.65.24.245',  # rms bae
             '10.36.24.11', # PIS
             '10.36.24.12', # PIS
             '10.26.40.20', # PIS
             '10.26.40.21', # PIS
             '10.81.38.143', # db-sim01
             '10.81.52.109', # test xwin
             '10.40.72.18', # test xwin
             '10.32.19.175',
             '127.0.0.1', #localhost for debug
             '10.32.19.174',
             '192.168.1.14'
            )
#These are the keys that must appear in a request or a task
REQUEST_KEYS = ('APIVersion', 'From', 'task')
TASK_KEYS = ('uuid', 'Request')
TASK_JSON_KEYS = ('opname', 'args') #'attr'
RETURN_MSG_KEYS = ('TaskId', 'status', 'msg') #'Task' is not necessary
#the time a key stays in our dup check set(600s)
DUP_CHECK_TIME = 600

MY_PRIVATEKEY = '20000'

def make_nshead(length):
    nshead = {
        "id" : 0,
        "verison" : 1,
        "log_id" : 0,
        "provider" : "soc-server",
        "magic_num" : 0xfb709394,
        "reserved" : 0,
        "body_len" : length,
    }
    header = []
    for i in ["id", "verison", "log_id", "provider", "magic_num", "reserved", "body_len"]:
        header.append(nshead[i])
    header_p = struct.pack("2HI16s3I", *header)

    return header_p


class Return_task(object):
    def __init__(self):
        self.msgpool=[]
        #HOST = '10.40.72.18'
        #HOST = '10.32.19.94' #bb-nsi-host-d.bb01
        #PORT = 9001
        HOST = 'localhost'
        PORT = 9999
        #PORT = 12345
        #PORT = 19009
        #PORT = 19999
        timeout = 5   
        socket.setdefaulttimeout(timeout)
        self.BUFSIZ = 1024*1024
        self.ADDR = (HOST, PORT)
        self.PRIVATEKEY=MY_PRIVATEKEY
        Process(target=self.return_task).start()
        #self.return_task()

    def _make_nshead(self, length):
        nshead = {
            "id" : 0,
            "verison" : 1,
            "log_id" : 0,
            "provider" : "soc-server",
            "magic_num" : 0xfb709394,
            "reserved" : 0,
            "body_len" : length,
        }
        header = []
        for i in ["id", "verison", "log_id", "provider", "magic_num", "reserved", "body_len"]:
            header.append(nshead[i])
        header_p = struct.pack("2HI16s3I", *header)

        return header_p

    def tcp_conn(self):
        p = True
        failed = False
        while p:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.connect(self.ADDR)
                sock.settimeout(5)
                p=False
            except socket.error, arg:
                if not failed:
                    (errno, err_msg) = arg
                    msg = "Connect server failed: %s, errno=%d" % (err_msg, errno)
                    self.logger(msg,1)
                    failed = True
                time.sleep(10)
        if failed:
            self.logger("Connect server succeeded.")
        return sock

    def send_rms(self,data):
        """send result to RMS
           Note: this function will keep trying util succeed.
           This is OK for now because there is only one client, RMS.
           But in the future, we must change this behavior."""
        if not data:
            return 0
        m = hashlib.md5()
        timestamp = time.strftime("%H%M%S%d%m%y", time.localtime(time.time()))
        print "data type = %s"+str(type(data))
        m.update(data + timestamp + self.PRIVATEKEY)
        my_sig = m.hexdigest().upper()
        head = self._make_nshead(len(data))
        u = data + "&sig=" + my_sig + '&' + timestamp
        sd = head + data
        sock = self.tcp_conn()
        sock.send('%s\r\n' % sd)
        try:
            recv_data = sock.recv(self.BUFSIZ)
        except socket.timeout:
            recv_data = ''
            print 'in send_rms receive timeout'
        if not recv_data:
            sock.close()
            return 0
        sock.close()

    def checkReturnMsg(self, msg):
        """check against the return msg from Q:TaskReturn"""
        new_data = {}
        for key in RETURN_MSG_KEYS:
            if key not in msg:
                return None
            new_data[key] = msg[key]
        return new_data

    def return_task(self):

        self.m = MsgQueue(password="nsi", zkHosts=TEST_ZKHOST)
        self.r = ZkRedis(password="nsi", zk_hosts=TEST_ZKHOST)
        m = self.m
        self.logger('IN check taskreturn')
        q_name='Q:TaskReturn'
        while True:
            try:
                msg = m.dequeue(q_name)
            except Exception, e:
                print "dequeue except: "+ str(e)
                time.sleep(10)
                continue
            print "dequeued msg type %s: %s"%(str(type(msg)), msg)
            #msg='123123123:12321:0'
            try:
                js_msg=json.loads(msg, encoding="utf-8")
            except ValueError:
                self.logger("Invalid json string from Q:TaskReturn :%s"%msg)
                continue
            print "return msg = %s"%js_msg

            js_msg = self.checkReturnMsg(js_msg)
            if js_msg == None:
                continue

            #convert uuid
            extid_val = self.IntId2ExtId(js_msg['TaskId'])
            if extid_val == None:
                err_msg='get extid fail'
                self.logger('ERROR IN return task:'+err_msg,1)
                continue
            (sender,extid) = extid_val.split(':', 1)
            js_msg['uuid'] = extid
            del js_msg['TaskId']

            if js_msg['status'] != 0:
                js_msg['error_code'] = js_msg['status']
                js_msg['status'] = -1
            else:
                js_msg['error_code'] = ''
            msg = json.dumps(js_msg, ensure_ascii=False) + os.linesep
            if type(msg) == types.UnicodeType:
                msg = msg.encode('utf-8')

            print 'taskreturn msg typeis %s, msg is %s'%(str(type(msg)), msg)
            self.logger(msg,1)
            #conn to rms
            self.send_rms(msg)
            #self.stream.write(msg)
            #except Exception,e:
            #    self.logger('ERROR IN replyResult:'+str(e),1)
            #    pass
    def logger(self, msg, flag=0):
        self.msgpool.append(msg)
        if flag != 0:
            try:
                l=LogModule(worker='return_task')
                for msg in self.msgpool:
                    l.info(msg)
                self.msgpool = []
            except Exception, e:
                print "open log file error, filename: "+ filename
                print str(e)

    def IntId2ExtId(self, intid):
        self.logger('IN intid to rmsID Coversion')
        res = None
        if intid:
            r = self.r
            try:
                res = r.hget('Intid2Extid', intid)
            except Exception, e:
                pass

        return res

class Connection(object):
    def __init__(self, connection, address):
        #m is msgqueue,r is redis
        self.stream = iostream.IOStream(connection)
        self.client_address = address[0]
        self.msgpool=[]
        self.logsplit = ' [-] '
        self.PRIVATEKEY = MY_PRIVATEKEY
        self.RequestPool = []
        self.__buffer = ''
        self.HEAD_LEN = 36

    def parse_nshead(self,header):
        return struct.unpack("2HI16s3I", header)

    def dataReceived(self,data) :

        self.__buffer = self.__buffer + data
        rcvdata = str(data)[36:]
        print time.ctime(),"recved: %s\n"%(rcvdata)
        #recv_data =  "recved: %s at %s\n"%(str(data)[36:],time.time())
        file = open("/var/tmp/soctest.ret","w")
        file.write(rcvdata)
        file.flush()
        file.close()
        msg = {'status':0, "msg":"这是一条返回消息"}
        msg = json.dumps(msg, ensure_ascii = False)
        self.stream.write(make_nshead(len(msg))+msg)
        #self.stream.close()

        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect(('127.0.0.1', 10010))
            s.send(rcvdata)
            s.close()
        except socket.error, e:
            (errno, err_msg) = e
            f = open('/home/wangbin/autotest/tcplogs','w')
            f.write("Socket error: %s, errno=%d" % (err_msg, errno))
            
        

    def run(self):
        
        #self.stream.read_bytes(self.HEAD_LEN, self.dataReceived)
        self.stream.read_until('\r\n', self.dataReceived)
        #self.check_queue()

    def ReturnResult(self,res,status):
        self.logger('IN ReturnResult')
        print 'in ReturnResult'
        time.sleep(3)
        print 'in ReturnResult sleep 3s'
        #p = Process(target=self.time)
        #t = threading.Timer(2.0, self.time)
        #p.start()
        #p.join
        print 'in ReturnResult sleep 5s'
        return True

    def clientAuthorize(self, whitelist):
        """ To check if the client ip is in the whitelist"""
        if WHITELIST_SWITCH == 1:
            return True
        try:
            clientip = self.client_address
            if clientip not in whitelist:
                return False
            return True
        except:
            return False

    #TODO: delete DupChk key from redis if following check failed
    def dataDupCheck(self, sig):
        """use redis to store dup check sigs"""
        r=self.r
        try:
            ret = r.setnx("DupChk:" + str(sig), str(sig))
            #reset the expire time of the key no matter whether it's duplicated
            r.expire("DupChk:" + str(sig), DUP_CHECK_TIME)
        except ConnectionError:
            self.replyResult('ERROR:数据库连接失败', 1)
            return False
        except Exception:
            self.replyResult('ERROR: 状态数据库操作失败', 1)
            return False

        if ret == False:
            self.replyResult('ERROR:数据重复，已忽略', 1)
            self.logger('REQUEST DUPLICATED')

        return ret

    def ExtId2IntId(self, data, clientName):
        #self.logger('IN ID Coversion to intid')

        if data['uuid']:
            #redis set
            r = self.r

            rmskey = clientName + ':' + str(data['uuid'])
            try:
                extid_exists = r.hexists('Extid2Intid', rmskey)
            except ConnectionError:
                self.replyResult('ERROR: 状态数据库连接失败', 1)
                return (False, data)
            except Exception:
                self.replyResult('ERROR: 状态数据库操作失败', 1)
                return (False, data)
                
            if extid_exists:
                self.replyResult("ERROR: uuid %s already exists."%str(data['uuid']), 1)
                return (False, data)
            intid = uuid.uuid1().get_hex()

            p = r.pipeline()
            p.hset('Extid2Intid', rmskey, intid)
            p.hset('Intid2Extid', intid, rmskey)
            try:
                p.execute()
            except ConnectionError:
                self.replyResult('ERROR: 状态数据库连接失败', 1)
                return (False, data)
            except Exception:
                self.replyResult('ERROR: 状态数据库操作失败', 1)
                return (False, data)

            data['uuid']=intid
            #print r.keys()
            return (True,data)
        else:
            error_msg = 'no ClientReqId Coversion FAILED'
            self.logger(error_msg)
            self.replyResult(error_msg, 1)
            return (False,data)

    def Taskset(self):
        self.logger('IN task set')
        q_StateMach='Q:Dispatcher'
        while len(self.RequestPool) > 0:
            data=self.RequestPool.pop()
            self.logger(str(data))
            req=data['Request']
            data_one_task={}
            data_one_task['TaskId']=data['uuid']
            data_one_task['Task']=req['opname']
            data_one_task['Args']=req['args']
            
            js_task=json.dumps(data_one_task, ensure_ascii=False)
            self.m.enqueue(q_StateMach, js_task)
            #r.hmset(q_StateMach, data_one_task, False)
            #print m.dequeue(q_StateMach,timeout=-1) 
            #print r.keys('*')
        return True

    def dataDecode(self, data):
        # if data is json format string , add it to RequestPool
        # else, return false
        ## Do something to fix RMS's bug.
        data = data.replace("\\","") # add a replace action for RMS's bug, no '\' in the string.
        data = data.replace("null","\"4096\"") # add a replace action for RMS's bug, null replace as ""
        try:
            newrequest = json.loads(data)
        except ValueError, e:
            self.replyResult("ERROR: 请求不是合法的json字符串", 1)
            return False

        (res,new_data)=self.Checkapi(newrequest)
        if res:
            for task in new_data:
                (res,int_task)=self.ExtId2IntId(task, newrequest['From'])
                if res:
                    #print self.IntId2ExtId('6735181ad01d11e2a6e6001d09242bfd')
                    self.RequestPool.append(int_task)
                else:
                    return False
            return True
        else:
            return False

    def dataCheck(self, data):
        self.logger('IN DATACHECK')

        # Check the client ip first:
        if not self.clientAuthorize(WHITELIST):
            # Not Authorize client, exit
            error_msg = 'ERROR: Client IP not in Whitelist. Pls register your ip.'
            self.replyResult(error_msg, 1)
            return False
        raw_data = data.split('&')
        print "len of raw data=%d"%len(raw_data)
        print raw_data
        if len(raw_data) > 3:
            raw_data[0] = "&".join(raw_data[:-2])
            raw_data[1] = raw_data[-2]
            raw_data[2] = raw_data[-1]
        if len(raw_data) < 3 or not raw_data[1].startswith("sig="):
            error_msg = 'ERROR:命令格式有误'
            self.replyResult(error_msg, 1)
            return False

        self.logger('SIG FORMAT PASSWD')
        js_data = raw_data[0]
        signature = raw_data[1].strip()
        timestamp = raw_data[2].strip()
        m = hashlib.md5()
        #self.logger('YOUR DATA IS')
        #self.logger(js_data) 
        #self.logger('COMPUTING THE MD5 SUM OF')
        #self.logger(js_data + self.PRIVATEKEY)

        # Compute the md5 sum with the private key
        print js_data,timestamp,self.PRIVATEKEY
        m.update(js_data + timestamp + self.PRIVATEKEY)
        my_sig = m.hexdigest().upper()

        if ( 'sig=' + my_sig == signature):
            # Sig is match!

            # Check if this request is a dup one
            #self.logger('SIG POOL:')

            if self.dataDupCheck(my_sig) == False:
                return False
            # Decode json format string to python dict
            if self.dataDecode(js_data):
                return True
            else:
                return False
        else:
            print my_sig, signature
            self.logger('SIG VERIFIED FAILED')
            error_msg = 'ERROR:签名校验失败'
            self.replyResult(error_msg, 1)
            return False
        return False

    def Checkapi(self,data):
        """check whether the request is valid"""
        self.logger('IN APICHECK')

        #Check the presence of the necessary keys
        for key in REQUEST_KEYS:
            if key not in data:
                self.replyResult('ERROR: 缺少必须的参数 "%s"'%key, 1)
                return (False, None)

        new_data=[]
        #TODO: do api decode according to APIVersion
        try:
            data['APIVersion'] = int(data['APIVersion'])
        except ValueError, e:
            self.replyResult('ERROR: Invalid APIVersion "%s"'%data['APIVersion'], 1)
            return (False, None)

        if data['APIVersion'] == 1:
            for task in data['task']:
                for key in TASK_KEYS:
                    if key not in task:
                        self.replyResult('ERROR: 任务缺少必须的参数 "%s"'%key, 1)
                        return (False, None)
                for key in TASK_JSON_KEYS:
                    if key not in task['Request']:
                        self.replyResult('ERROR: 任务json缺少必须的参数 "%s"'%key, 1)
                        return (False, None)
                new_data.append(task)
            return (True,new_data)
        else:
            error_msg = 'APIVersion VERIFIED FAILED'
            self.logger(error_msg)
            self.replyResult(error_msg, 1)
            return (False,None)


    def handle(self, data):
        if data:
            print data
            #self.mirrorInput(data)
            client_addr = self.client_address
            self.logger('Connect coming... Got connection from '+str(client_addr) )
            self.logger( client_addr + self.logsplit + data)

            if self.dataCheck(data):
                if self.Taskset():
                #pass
                #self.process(data)
                    self.replyResult('ok',0)
            else:
                msg = "UNKNOWN DATA FORMAT OR DUPLICATED REQUEST, CONNECTION CLOSED"
                ## Connection closes when write back message.
                #self.replyResult(msg,1)
                self.logger(msg)
            self.logger('One request finishd!',1)
            
        self.stream.close()

            #self.logger(data,1)

    def logger(self, msg, flag=0):
        self.msgpool.append(msg)
        if flag != 0:
            try:
                #print len(self.msgpool)
                l=LogModule(worker='soc_receive')
                for msg in self.msgpool:
                    l.info(msg)
                self.msgpool = []
            except Exception, e:
                print "open log file error, filename: "+ filename
                print str(e)
                raise #TODO Test only


    def logger_old(self, msg, flag=0):
        timestamp = time.strftime("%D %H:%M:%S", time.localtime())
        line = '[CACTI-AOS][%s][%s]%s\n' % (timestamp, 'sig', str(msg))
        print line
        self.msgpool.append(line)
        if flag != 0:
            try:
                f = open(filename, "a")
                ## Lock the file.
                fcntl.flock(f, fcntl.LOCK_EX)
                for line in self.msgpool:
                    f.write(line)
                fcntl.flock(f, fcntl.LOCK_UN)
                f.close()
                self.msgpool = []
            except Exception, e:
                print "open log file error, filename: "+ filename
                print str(e)

    def replyResult(self, data, status):
        #msg = '{"Result":"%s"}'%(data) + os.linesep
        #self.mirrorOutput(data,status)
        try:
            if status == 0:
                new = {'status':0,'msg':data}
                msg = json.dumps(new, ensure_ascii=False) + os.linesep
            else:
                new = {'status':status,'msg':data}
                msg = json.dumps(new, ensure_ascii=False) + os.linesep

            self.logger(msg,1)
            self.stream.write(msg)
        except Exception,e:
            self.logger('ERROR IN replyResult:'+str(e),1)
            pass
 
def connection_ready(sock, fd, events):
    
    while True:
        try:
            connection, address = sock.accept()
        except socket.error, e:
            if e[0] not in (errno.EWOULDBLOCK, errno.EAGAIN):
                raise
            return
        #print 'in connection_ready'
        connection.setblocking(0)
        soc=Connection(connection,address)
        soc.run()
 
if __name__ == '__main__':
#r=ZkRedis(password="nsi", zk_hosts="db-sim-xwin01.db01:6379")
#r=ZkRedis(zk_hosts="db-sim-xwin01.db01:6379")
#print r.keys('*')

    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.setblocking(0)
        sock.bind(("", 10000))
        sock.listen(5000)
    except Exception,e:
        print 'socket error'
        exit

    io_loop = ioloop.IOLoop.instance()
    callback = functools.partial(connection_ready, sock)
    io_loop.add_handler(sock.fileno(), callback, io_loop.READ)
    try:
        io_loop.start()
    except KeyboardInterrupt:
        io_loop.stop()
        print "exited cleanly"
