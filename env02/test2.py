import ptest.hello
import os

#a = ptest.hello.firstClass()
#a.hello()
#print getattr(a,'name','111')
#print a.__dict__
#print ptest.hello.firstClass.__dict__

def fun1(a,b,):
	print 'a,b'

#fun1('sdaf',1,)


ptest.funca('asdf')
from ptest import funca
funca('11111')


a='asdfasdfsdf\nasdfasdfasdf\n124312341234'
last = a.split('\n')[-1]
print last

print(__file__)
print(os.path.dirname(__file__))
print(os.path.abspath(__file__))
print(os.path.dirname(os.path.abspath(__file__)))
