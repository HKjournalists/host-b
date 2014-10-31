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
    代码修改工具:
        update:20141031
        C语言if语句替换
        C语言函数替换
        单行删除
        单行插入
        
        
    '''

    def __init__(self):
        self.baklist = []
    
    def run(self):
        parser = argparse.ArgumentParser(description="code editor")
        parser.add_argument('-b', dest = 'bakfile', help = 'bakup file', default = None)
        parser.add_argument('-c', help = 'edit c language file', action = 'store_true')
        parser.add_argument('-f', help = 'edit function', action = 'store_true')
        parser.add_argument('-r', help = 'restore files', action = 'store_true')
        parser.add_argument('-o', '--oldf', dest = 'oldfunc', help = 'the name of the function to be replaced', default = None)
        parser.add_argument('-n', '--newf', dest = 'newfunc', help = 'the name of the new function', default = None)
        parser.add_argument('-s', dest = 'cfile', help = 'the new function \'s source file(.c)', default = None)
        parser.add_argument('-y', dest = 'hfile', help = 'the new function \'s head file(.h)', default = None)
        parser.add_argument('-t', dest = 'tfile', help = 'the old function \'s source file(target file)', default = None)
        args = parser.parse_args()
        if args.c:
            if args.f:
                if args.oldfunc and args.newfunc and args.cfile and args.hfile and args.tfile:
                    targetfiles = []
                    targetfiles.append(args.tfile)
                    self.c_func_rpl(args.oldfunc, args.newfunc, args.cfile, args.hfile, targetfiles)            
            exit()
        elif args.r:
            self.heal_the_world()
            exit()    
        elif args.bakfile is not None:
            print(args.bakfile)

    def fbak(self, flist):
        '''
        文件备份，使用uuid生成随机后缀
        '''
        rdict = {}
        if type(flist) == type('string'):
            f = flist
            bakfile = f + '.tempbak' + str(uuid.uuid1())
            cmd = 'mv -f ' + f + ' ' + bakfile
            p = subprocess.Popen(shlex.split(cmd), stdin = subprocess.PIPE, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
            out, err = p.communicate()
            if err != '':
                print('Error in backup files >> %s\n' % (err.strip())),
                return -1
            rdict[f] = bakfile
            return rdict
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

    def heal_the_world(self):
        for item in os.listdir(os.getcwd()):
            if os.path.isfile(item):
                m = re.match(r'.*.(\w+-){4}\w+', item)
                if m is not None:
                    cmd = 'mv -f ' + m.group() + ' ' + '.'.join(m.group().split('.')[0:-1])
                    p = subprocess.Popen(shlex.split(cmd), stdin = subprocess.PIPE, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
                    out, err = p.communicate()
                    if err != '':
                        print('Error in restore files >> %s' % (err.strip())),    
                        return -1
        return 0

    def getfname(self, file):
        filename = file.split('/')[-1]
        return filename

    def recover(self):
        os.system('mv -f ' + self.file + '.bak_temp' + ' ' + self.file)

    def c_if_rpl(self, file = '', method = '', line = 0, list = [{'if(flag)' : 'if(1)'}]):
        '''
        C语言if语句替换：
        file:需要求改的代码文件名
            type = string
        method:需要修改的语句所处的函数名
            type = string
        line:需要修改的语句位于函数内的相对行数（函数内偏移）
            type = int
        list:一个包含字典类型元素的列表，其中字典元素的key为需要修改的语句字符串（必须与源代码中某一行完全匹配），value为修改后的代码字符串    
            type = [{string:string}, ...]
        '''
        tlist = copy.deepcopy(list)
        output = file + '.temp.codEditor'
        tfdict = self.fbak(file)
        try:
            input = open(tfdict[file], 'r')
            output = open(file, 'w')
            f.seek(0)
            flag = 0
            s = input.readline()   
            while s:
                #print s,
                if flag == 0:               #没有匹配到指定函数时，直接写入output
                    output.write(s) 
                    m = re.match('\w+\s\*?\(?\*?'+ method +'\)?\(.*\){?$', s)
                    if m is not None:       #匹配到指定函数，读取至函数内偏移位置，设置flag
                        for i in range(1, line):
                            output.write(input.readline())
                        flag = 1
                    s = input.readline()
                elif flag == 1:             #从偏移位置开始，匹配tlist内容，发现匹配语句则将修改后的语句写入output
                    if len(tlist) > 0 and s.strip() == tlist[0].keys()[0]:
                        space = ' '*len(re.match('\s+', s).group())
                        output.write('%s%s%s' % (space, tlist[0][s.strip()], os.linesep))        
                        del tlist[0]
                    else:
                        output.write(s)
                    s = input.readline()    
        except IOError, e:
            print str(e)
            return -1
        finally:
            if input is not None:
                input.close()
            elif output is not None:    
                output.close()

    def c_func_rpl(self, oldfunc, newfunc, cfile, hfile, targetfiles, scope=1, startline=0, endline=0):
        '''
        C语言函数替换（参数列表须一致）
        oldfunc:待替换函数名
            type = string
        newfunc:替换后函数名
            type = string  
        cfile:替换函数所在.c文件（暂时无意义，用于编译）
            type = string
        hfile:声明替换函数的.h文件
            type = string
        targefiles:需进行替换的文件列表
            type = [string, ...]  
        scope:替换范围，0表示局部替换，1表示全局替换（暂时没用到）
            type = int 
        startline:开始替换数
            type = int 
        endline:结束替换行数
            type = int 
        '''
        tfdict = self.fbak(targetfiles)
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
                                output.write(tempstr + m.group(2) + m.group(3).replace(oldfunc + '(', newfunc + '('))
                            else:
                                output.write(tempstr + m.group(2) + m.group(3))
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
    
    def linedel(self, filedict):
        '''

        单行删除
        filedict:删除字典，key为文件名，value为行号，如{'test.c', 10}    
            type = {string:int, ...}
        '''
        tfdict = self.fbak(filedict.keys())
        for file, bakfile in tfdict.items():
            input = open(bakfile, 'r')
            output = open(file, 'w')
            flag = filedict[file]
            lnumber = 1
            s = input.readline()
            while s:
                if lnumber == flag:
                    s = input.readline()
                    lnumber += 1
                    continue
                output.write(s)
                s = input.readline()
                lnumber += 1
    
    def lineins(self, file, line, span, str):
        '''
        单行插入
        file:文件名
            type = string
        line:插入行号（原行及以后内容向后顺延）
            type = int
        span:缩进空格数
            type = int
        str:插入内容    
            type = string
        '''    
        tfdict = self.fbak(file)
        input = open(tfdict[file], 'r')
        output = open(file, 'w')
        lnumber = 1
        s = input.readline()
        while s:
            if lnumber == line:
                output.write(' '* span + str + os.linesep)
            output.write(s)
            s = input.readline()
            lnumber += 1

    def linerpl(self, file, line, str):
        tfdict = self.fbak(file)
        input = open(tfdict[file], 'r')
        output = open(file, 'w')
        lnumber = 1
        s = input.readline()
        while s:
            if lnumber != line:
                output.write(s)
            else:
                m = re.match('\s+', s)
                space = ''
                if m is not None:
                    space = ' '*len(m.group())
                output.write(space + str + os.linesep)
            s = input.readline()
            lnumber += 1
  
        
if __name__ == '__main__':
    '''
    调用run()可使用命令行模式 
    '''
    e = Editor()
    #e.c_if_rpl('test.c', 'main', 3, [{'if(flag)' : 'if(1)'}])
    e.c_func_rpl('hi', 'hello', 'testlib.c', 'testlib.h', ['test.c'])
    #e.linedel({'testl.c':9})
    #e.lineins('testl.c', 9, 8, 'abcdefg')
    #e.linerpl('testl.c', 9, 'abcdefg')
    #e.run()

