import time
import os
import sys
import argparse

from util.constants import *
from caselib import case_template

def run():
    parser = argparse.ArgumentParser(description="parse case info.")
    parser.add_argument('-m', dest='module', help='the module.', default=None)
    parser.add_argument('-c', dest='casename', help='the case name.', default=None)
    result = parser.parse_args()
    if result.module is None:
        print 'error, please specify the module'
        exit()
    if result.casename is None:
        print 'error, please specify the case'
        exit()
    before(result)

def list_case(dir):
    if not os.path.exists(dir):
        print 'dir error'
        return 0
    files = os.listdir(dir)
    cases = []
    for file in files:
        file = file.strip()
        if file == '__init__.py' or file[-3:] == 'pyc' or file[-3:] == 'PYC' or file == 'BaseCase.py':
            continue
            cases.append(file)
    return cases
	
def touch():
    global out
    out[TIME] = '%s'%(time.strftime('%H:%M:%S %d/%m/%Y'))

def getResultString(obj):
    ret= '%s:%s%s' % (PROJECT, ' '*(TITLE-len(PROJECT)), obj.projcet)
    ret= '%s\n%s' % (ret,'%s:%s%s' % (VERSION, ' '*(TITLE-len(VERSION)), obj.version))
    ret= '%s\n%s' % (ret,'%s:%s%s' % (CASE, ' '*(TITLE-len(CASE)), obj.description))
    ret= '%s\n%s' % (ret,'%s:%s%s' % (TIME, ' '*(TITLE-len(TIME)), out[TIME]))
    ret= '%s\n%s' % (ret,'%s:%s%s' % (EXPECTATION, ' '*(TITLE-len(EXPECTATION)), obj.expect_ret))
    ret= '%s\n%s' % (ret,'%s:%s%s' % (RESULT, ' '*(TITLE-len(RESULT)), obj.result))
    ret= '%s\n%s' % (ret,'%s:%s%s' % (MESSAGE, ' '*(TITLE-len(MESSAGE)), obj.msg))
    return ret

def getClass(module, baseClass): 
    for i in dir(module):
        attr = getattr(module, i)
        if type(attr) == type and issubclass(attr, baseClass):
            return attr

def before(case):
    #import module caselib.xxx.xxx_case*
    module = __import__('caselib.' + case.module + '.' + case.casename,{},{},[case.casename])
    #import base module caselib.xxx.xxx_template
    baseModule = __import__('caselib.' + case.module + '.' + case.module + '_template', {}, {}, [case.module + '_template'])
    #base class of all cases
    rootClass = case_template.CaseTemplate
    #CaseTemplate --> XxxTemplate --> XxxCase*
    obj = getClass(module, getClass(baseModule, rootClass))()
    run_case(obj)
    
def run_case(caseObj):
    caseObj.pre()
    caseObj.doTest()
    after(caseObj)

def after(caseObj):
    caseObj.verify()
    #other after actions
    touch()
    print getResultString(caseObj)
    

if __name__ == '__main__':
    run()



























