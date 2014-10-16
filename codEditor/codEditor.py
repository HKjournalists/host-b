#!/usr/bin/env python
# -*- coding: utf8 -*-

import re
import os
import sys
import copy

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
    
    def parseArg(self):
        pass

    def ceditor(self):
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

if __name__ == '__main__':
    e = Editor('test.c', 'main', 3, [{'if(flag)' : 'if(1)'}])
    if sys.argv[1] == 're':
        e.recover()
    else:
        e.ceditor()




