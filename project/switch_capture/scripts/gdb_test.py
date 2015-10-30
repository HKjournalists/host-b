import os
import re
import time
import shlex
import subprocess
import string
import pexpect
import threading
import multiprocessing, signal

'''
child = pexpect.spawn('gdb')
pattern = re.compile(r'%s\(gdb\)' % (os.linesep))
index = child.expect([pattern, pexpect.EOF, pexpect.TIMEOUT], 5)
print child.before
print child.after.strip()
#print index
child.close(force=True)

child = pexpect.spawn('cat pextest')
pattern = re.compile(r'\n\btest\b')
index = child.expect([pattern, pexpect.EOF, pexpect.TIMEOUT], 5)
print child.before.strip()
print '#####################'
print child.after.strip()
child.close(force=True)
'''
class MyProcess(multiprocessing.Process):
    def __init__(self, queue=None, flag=None):
        #threading.Thread.__init__(self)
        super(self.__class__, self).__init__()
        #signal.signal(signal.SIGINT, self.handler)
        self.queue = queue
        self.flag = flag

    def handler(self, signum, frame):
        print('###################signum: %s' % (signum))
        print('###################signum: %s' % (frame))

        

    def run(self):
        while True:
            if self.flag.is_set():
                self.queue.put({'event': 'exit', 'pid': os.getpid()})
                break
            print('%s sleep 10' % (self.pid))
            time.sleep(10)


    def ospf_filter(self):
        print 'ospf!'

    def test(self):
        try:
            a = 1
            b = 2
            return a + b
        finally:
            print 'before return'

if __name__ == '__main__':
    '''
    queue = multiprocessing.Queue() 
    flag = multiprocessing.Event() 
    signal.signal(signal.SIGINT, lambda x, y: flag.set())
    signal.siginterrupt(signal.SIGINT, False)
    ps = {}
    for i in range(5):
        mp = MyProcess(queue ,flag)
        mp.start() 
        ps[mp.pid] = mp
    while True:
        print 'main'
        item = queue.get()
        if item['event'] == 'exit':
            t = ps.pop(item['pid'])
            t.join()
        if not ps:
            break

    regex = r'^.*\.((cc)|(hh)|(h)|(c))$'
    pattern = re.compile(regex)
    dir = '/home/zhangpengfei/switch/tor/xorplus/pica/sif'
    cmd = 'sudo sh /home/wangbin/project/switch_capture/scan.sh %s' % (dir)
    p = subprocess.Popen(shlex.split(cmd), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate()
    temp_dir = '%s/.xorplus_debug_temp' % (dir)
    os.system('sudo mkdir -p %s' % (temp_dir))
    for file in out.split():
        m = pattern.match(file)
        if m is not None:
        #    src_file = os.path.join(dir, file)
        #    con.file_scp('%s:%s' % (self.loc_ip, src_file), 
        #                    self.sw_src_dir, self.loc_user, self.loc_pwd)
        #    self.logger.debug('copy src file %s to switch' % (src_file))
            os.system('sudo cp %s %s' % (file, temp_dir))
    
    filter_dict = {
            'l2_lcmgr': {'pos': [27], 'patt': r'^59$'},
            'l2_sif': {'pos': [27], 'patt': r'^59$'},
            'ip': {'pos': [9], 'patt': r'^59$'},
            'ospf_fea': {'pos': [0, 1], 'patt': r'^020[1-5]$'}
        }
    print filter_dict['l2_lcmgr']['pos']
    print filter_dict['l2_lcmgr']['patt']

    '''
    mp = MyProcess()
    print mp.test()