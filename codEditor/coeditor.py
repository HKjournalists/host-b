#!/usr/bin/env python
# -*- coding: utf8 -*-

import re
import os
import sys
import copy
import argparse
import subprocess
import uuid
import shlex

class Editor(object):
    '''
    代码修改工具：
        file:需要求改的代码文件名
        method:需要修改的语句所处的函数名
        line:需要修改的语句位于函数内的相对行数（函数内偏移）
        list:一个包含字典类型元素的列表，其中字典元素的key为需要修改的语句字符串（必须与源代码中某一行完全匹配），value为修改后的代码字符串
    代码修改步骤：    
        1.从代码文件第一行开始，读取每一行并匹配函数名，同时将每一行写入output文件，直至函数内偏移位置（函数名所在的行+line行）
        2.从函数内偏移开始，按照列表中元素顺序依次寻找匹配的代码进行修改，同时写入output文件（若有修改则写入修改后内容）
        3.备份原始代码文件，用output覆盖原始代码文件
        4.测试结束后执行recover函数恢复原始代码文件
    '''

    def __init__(self, file = '', method = '', line = 0, list = [{'if(flag)' : 'if(1)'}]):
        self.file = file
        self.method = method
        self.line = line
        self.list = list
    
    def run(self):
        parser = argparse.ArgumentParser(description="code editor")
        parser.add_argument('-c', help = 'use -c option to edit c language file', action = 'store_true')
        parser.add_argument('-f', help = 'use -f option to edit function', action = 'store_true')
        parser.add_argument('-o', '--oldf', dest = 'oldfunc', help = 'the name of the function to be replaced', default = None)
        parser.add_argument('-n', '--newf', dest = 'newfunc', help = 'the name of the new function', default = None)
        parser.add_argument('-s', dest = 'cfile', help = 'source file', default = None)
        parser.add_argument('-y', dest = 'hfile', help = 'the new function\'s .h file', default = None)
        parser.add_argument('-t', dest = 'tfile', help = 'target file', default = None)
        args = parser.parse_args()
        if args.c:
            if args.f:
                if args.oldfunc and args.newfunc and args.cfile and args.hfile and args.tfile:
                    targetfiles = []
                    targetfiles.append(args.tfile)
                    self.c_func_replace(args.oldfunc, args.newfunc, args.cfile, args.hfile, targetfiles)            
        exit()
        #if result.casename is None:
        #    print 'error, please specify the case'
    
    def fbak(self, flist):
        rdict = {}
        for f in flist:
            bakfile = f + '.tempbak' + str(uuid.uuid1())
            cmd = 'mv -f ' + f + ' ' + bakfile
            p = subprocess.Popen(shlex.split(cmd), stdin = subprocess.PIPE, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
            out, err = p.communicate()
            if err != '':
                print('Error in backup files >> %s\nnow roll back!' % (err.strip())),
                self.frecover(rdict)
                return rdict
            rdict[f] = bakfile
        return rdict
    
    def frecover(self, fdict):
        if len(fdict.keys()) == 0:
            return 0
        for refile, f in fdict.items():
            cmd = 'mv -f ' + f + ' ' + refile
            p = subprocess.Popen(shlex.split(cmd), stdin = subprocess.PIPE, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
            out, err = p.communicate()
            if err != '':
                print('Error in recover files : %s' % (err)),
        return 0    

    def getfname(self, file):
        filename = file.split('/')[-1]
        return filename

    def c_if_replace(self):
        list = copy.deepcopy(self.list)
        output = self.file + '.temp.codEditor'
        #filename = self.file.split('/')[-1]
        #path = self.file[: -len(filename)]
        try:
            f = open(self.file, 'r+')
            out = open(output, 'w')
            f.seek(0)
            flag = 0
            s = f.readline()   
            while s:
                #print s,
                if flag == 0:               #没有匹配到指定函数时，直接写入output
                    out.write(s) 
                    m = re.match('\w+\s\*?\(?\*?'+ self.method +'\)?\(.*\){?$', s)
                    if m is not None:       #匹配到指定函数，读取至函数内偏移位置，设置flag
                        for i in range(1, self.line):
                            out.write(f.readline())
                        flag = 1
                    s = f.readline()
                elif flag == 1:             #从偏移位置开始，匹配list内容，发现匹配语句则将修改后的语句写入output
                    if len(list) > 0 and s.strip() == list[0].keys()[0]:
                        space = ' '*len(re.match('\s+', s).group())
                        out.write('%s%s%s' % (space, list[0][s.strip()], os.linesep))        
                        del list[0]
                    else:
                        out.write(s)
                    s = f.readline()    
        except IOError, e:
            print str(e)
            return -1
        finally:
            if f is not None:
                f.close()
            elif out is not None:    
                out.close()
        os.system('\cp ' + self.file + ' ' + self.file + '.bak_temp' + '&& mv -f ' + output + ' ' + self.file)
    
    def recover(self):
        os.system('mv -f ' + self.file + '.bak_temp' + ' ' + self.file)

    def c_func_replace(self, oldfunc, newfunc, cfile, hfile, targetfiles, scope=1, startline=0, endline=0):
        tfdict = self.fbak(targetfiles)
        print tfdict
        for file, bakfile in tfdict.items():
            try:
                input = open(bakfile, 'r')
                output = open(file, 'w')
                flag = 0
                s = input.readline()
                while s and re.match(r'^#include .*', s.strip()) is None:
                    output.write(s)
                    s = input.readline() 
                while s and re.match(r'^#include .*', s.strip()) is not None and flag == 0:
                    if re.match(r'^#include ["<]?' + hfile + r'[">]?', s.strip()) is not None:
                        flag = 1
                    output.write(s)
                    s = input.readline()
                if flag == 0:
                    output.write('#include "' + self.getfname(hfile) + '"' + os.linesep)
                while s:
                    if re.match(r'^\w+$', s.strip()) is not None:
                        output.write(s)
                        s = input.readline()
                        if re.macth(r'^' + oldfunc + r'\(.*\)[ \t]*[;|\{]?$', s.strip()) is not None: 
                            output.write(s)
                        elif re.match(r'^'+ oldfunc + r'\(.*\)[ \t]*\{.*$', s.strip()) is not None:
                            output.write(s)
                    elif re.match(r'^\w+\s+'+ oldfunc + r'\(.*\)[ \t]*[;|\{]?$', s.strip()) is not None:
                        output.write(s)
                    elif re.match(r'^\w+\s+'+ oldfunc + r'\(.*\)[ \t]*\{.*$', s.strip()) is not None:
                        output.write(s)
                    elif re.match(r'.*\W+('+ oldfunc + r')\(.*|^(' + oldfunc + r')\(.*' , s.strip()) is not None:
                        m = re.match('(.*)("[\w\W]*")(.*\n)', s)
                        if m is not None:
                            if re.match(r'.*\W+'+ oldfunc + r'\(.*|^' + oldfunc + r'\(.*', m.group(1)) is not None:
                                tempstr = m.group(1).replace(oldfunc + '(', newfunc + '(')
                            else:
                                tempstr = m.group(1)
                            if re.match(r'.*\W+'+ oldfunc + r'\(.*', m.group(3)) is not None:
                                tempstr = tempstr + m.group(2) + m.group(3).replace(oldfunc + '(', newfunc + '(')
                            else:
                                tempstr = tempstr + m.group(2) + m.group(3)
                            output.write(tempstr)
                        else:
                            output.write(s.replace(oldfunc + '(', newfunc + '('))
                    else:
                        output.write(s)
                    s = input.readline()
            except (IOError, AttributeError), e:
                print str(e)
                self.frecover(tfdict)
                return -1
            finally:
                if input is not None:
                    input.close()
                if output is not None:
                    output.close()

        

if __name__ == '__main__':
    e = Editor('test.c', 'main', 3, [{'if(flag)' : 'if(1)'}])
    #if sys.argv[1] == 're':
    #    e.recover()
    #else:
    #    e.c_if_replace()
    e.c_func_replace('hi', 'hello', 'testlib.c', 'testlib.h', ['test.c'])
    #e.run()


