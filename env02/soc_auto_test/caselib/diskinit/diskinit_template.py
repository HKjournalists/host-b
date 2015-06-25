#!/bin/bash

from caselib import case_template
from util import ssh_tools

class DiskInitTemplate(case_template.CaseTemplate):
    
    def pre(self):
        if self.setup_clean_redis == True:
            #print 'clean redis!'
            self.utilObj.clredis()
        else:
            #print 'skip clean redis!' 
        ssh = ssh_tools.SshConnect(self.ip, 'root', 'SYSserverpasswd1999@baidu.com')
        ssh.sftp('/home/wangbin/autotest/scripts/diskinit_pre.sh', '/tmp/diskinit_pre.sh')
        ssh.sendCmd('cd /tmp ; sh diskinit_pre.sh')
        

