#!/usr/bin/env python

import redis
import os
login_redis = 'redis-cli -h %s -p %s -a %s ' %('127.0.0.1', '6379', 'nsi')
print 'socapi'
os.system(login_redis + 'keys socapi:* | ' + 'xargs ' + login_redis + 'del   ')
print 'ReqMeta'
os.system(login_redis + 'keys ReqMeta:* | ' + 'xargs ' + login_redis + 'del   ')
print 'TaskSet'
os.system(login_redis + 'keys TaskSet:* | ' + 'xargs ' + login_redis + 'del   ')
print 'Task'
os.system(login_redis + 'keys Task:* | ' + 'xargs ' + login_redis + 'del   ')
print 'Q'
os.system(login_redis + 'keys Q:* | ' + 'xargs ' + login_redis + 'del    ')
print 'TimeOut'
os.system(login_redis + 'keys TimeOut:* | ' + 'xargs ' + login_redis + 'del    ')
print 'ExtId2IntId'
os.system(login_redis + 'keys ExtId2IntId | ' + 'xargs ' + login_redis + 'del   ')
print 'PxeIdMap'
os.system(login_redis + 'keys PxeIdMap | ' + 'xargs ' + login_redis + 'del   ')
