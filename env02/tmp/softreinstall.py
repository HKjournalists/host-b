import traceback
import time

from soc.operations.baseoperation import BaseOperation
from soc.util.ssh_session import *
from soc.constants import SOFT_REINSTALL
from soc.constants.SSH import SSH_DEFAULT_USER,SSH_DEFAULT_PASSWORD


class Softreinstall(BaseOperation):
    def download_file(self,ssh,file,server):
        try:
            ret = ssh.ssh('wget -nv -q -w 10 -t 10 -O /boot/%s http://%s/tftpboot/%s'%(file,server,file), ret_code=True, timeout=60)
            if ret == '0':
                self.download_res=0
            else:
                self.download_res=1
        except Exception:
            self.download_res=1
        return

    def work(self):
        # intial return values
        self.ret_code = 0
        self.download_res = 1
        self.extra_args = {}
        self.msg = ''
        dhcpserver=SOFT_REINSTALL.dhcpserver
        dhcpserver_backup=SOFT_REINSTALL.dhcpserver_backup

        # check args first
        try:
            self.hostname = self.args['hostname']
        except KeyError,e:
            self.set_result(SOFT_REINSTALL.ARGS_MISSING_ERROR,{}, 'key %s missing in args' % str(e).replace('\'',''))
            return

        # Initialize ssh
        ssh = ssh_session(SSH_DEFAULT_USER,self.hostname,SSH_DEFAULT_PASSWORD)
        # check ssh first
        try:
            ssh.ssh('test')
        except Exception,e:
            errmsg = str(e)
            self.set_result(SOFT_REINSTALL.SSH_ERROR,{},'ssh precheck failed: %s' % errmsg)
            return

        try:
            for file in ('bzImage.3212','image_new.cpio.gz'):
                self.download_file(ssh,file,dhcpserver)
                if self.download_res == 1:
                    self.download_file(ssh,file,dhcpserver_backup)
                if self.download_res == 1:
                    raise
            ssh.ssh('sed -i \'/hiddenmenu/a title soft reinstall\\n \\troot (hd0,1)\\n \\tkernel /boot/bzImage.3212\\n \\tinitrd /boot/image_new.cpio.gz\' \
                        /boot/grub/grub.conf', timeout=60)
        except Exception,e:
            self.set_result(SOFT_REINSTALL.WGET_ERROR,{},'update grub failed : %s'%str(e))
            return

        # send reboot -f command
        try:
            ssh.ssh('reboot -f')
        except Exception,e:
            self.set_result(SOFT_REINSTALL.SUCCESS,{},'reboot command success')
            return
        else:
            self.set_result(SOFT_REINSTALL.REBOOT_COMMAND_FAILED_ERROR,{},'reboot command failed, ssh still alive')

if __name__ == '__main__':
    request = {}
    request['Task'] = 'finalcheck'
    request['ReturnQ'] = 'Q:Test'
    request['TaskId'] = '54c26432-a87a-11e2-b179-80fb06af0ed4'
    request['Op'] = 'finalcheck'
    request['debug'] = True
    if len(sys.argv) != 1:
        args = eval(sys.argv[1])
    else:
        args = {'home1_size': 'all', 'home_raid_high': 'default', 'make_big_fs': 'normal', 'home1_make_big_fs': 'normal', 'home1_name': '/home', 'from_budget': '1', 'home_quantity': '1', 'is_install_pkgname': 'rhel4u3', 'network_adaptor': [], 'home1_filesystem': 'EXT2', 'disk': [{'disk_quantity': '6', 'disk_size': '300G'}], 'root_size': '9G', 'HP_rw_ratio': '50', 'is_harddisk_raid': '1', 'producer': '15', 'is_host_machine': '0', 'hostname': 'bb-atm-ur-sandbox05.bb01', 'raid_level': '5', 'bios': [{'ht_stat': 'off'}], 'swap': 'on', 'memory': [{'mem_size': '8G', 'mem_quantity': '16'}], 'department': '83', 'serial_number': 'NC01162641', 'main_in_ip': '10.23.41.43', 'home1_blocksize': '4096', 'is_install_system': '1', 'main_in_ip_netmask': '255.255.255.128', 'secondary_ip': '', 'server_type': 'unknow', 'home1_has_journal': '', 'raid_stripesize': '128', 'flash': '', 'mac': 'F8:0F:41:F6:20:15;F8:0F:41:F6:20:14', 'process_id': '2374165_server_online', 'home_count': '1', 'home1_enable_extent': '', 'ssd': [], 'model': '172', 'kernel_version': '2.6.32_1-9-0-0', 'outer_ip': 'aaa', 'item_type': '3290', 'operating_item': 'so5333', 'NCSI': '0', 'share_ilo_ip': '0', 'zipcard': 'no', 'sa': 'zhangchunyu@baidu.com', 'os': 'linux', 'keep_home': 'no'}
    request['Args'] = args
    print args.keys()
    print args['hostname']
    print 'request',request
    w = Softreinstall(**request)
    w.work()
