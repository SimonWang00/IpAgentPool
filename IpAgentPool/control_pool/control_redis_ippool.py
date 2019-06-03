#!/usr/bin/python3
# __*__ coding: utf-8 __*__

'''
@Author: Simon
@License: (C) Copyright 2013-2018, Best Wonder Corporation Limited.
@Os：Windows 10 x64
@Contact: 763646402@qq.com
@Software: PY PyCharm 
@File: control_redis_ippool.py
@Time: 2019/6/3 10:38
@Desc: define your website http://www.***.com
'''
import sys
sys.path.append('..')
import time
import asyncio
import datetime
from config import sample_conf
from add_ips.add_redis_ip import add_redis_ip,connect_redis
from check_ips.check_redis_ip import run_check_redis_ip


# @asyncio.coroutine
async def add_process(addflag):
    '''添加代理IP'''
    print('添加IP代理')
    if addflag:
        add_redis_ip()
        print('-->time:%s ,休眠20s后再添加代理IP'%str(time.time()))
        time.sleep(sample_conf.idletime)
        addflag = False

# @asyncio.coroutine
async def check_process(checkflag):
    '''检测代理IP'''
    print('start check')
    if checkflag:
        run_check_redis_ip()
        print('-->time:%s ,休眠180s后再检测代理IP'%str(time.time()))
        time.sleep(sample_conf.checkidletime)
        checkflag = False

# 根据代理池大小去检测
async def start_check_jos():
    r = connect_redis()
    nums = r.scard(sample_conf.REDIS_KEY)
    while True:
        nwt = int(datetime.datetime.now().strftime('%H'))
        # 停止检测IP代理
        if  sample_conf.blacktime_start < nwt < sample_conf.blacktime_end:
            # 休眠十分钟
            print('时间段：%d:00-%d:00，为检测休眠时间'%(sample_conf.blacktime_start,sample_conf.blacktime_end))
            time.sleep(600)
        else:
            # 逻辑控制
            if nums >= sample_conf.poolsize:
                checkflag = True
                addflag = False
            elif nums < 3:
                checkflag = False
                addflag = True
            else:
                checkflag = True
                addflag = True
            await asyncio.ensure_future(check_process(checkflag))
            await asyncio.ensure_future(add_process(addflag))
            nums = r.scard(sample_conf.REDIS_KEY)
            print('-->time:%s restart loops.....' % str(time.time()))

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    tasks = [asyncio.ensure_future(start_check_jos()), ]
    loop.run_until_complete(asyncio.wait(tasks))
    loop.close()
