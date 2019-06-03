#!/usr/bin/python3
# __*__ coding: utf-8 __*__

'''
@Author: Simon
@License: (C) Copyright 2013-2018, Best Wonder Corporation Limited.
@Os：Windows 10 x64
@Contact: 763646402@qq.com
@Software: PY PyCharm
@File: add_redis_ip.py
@Time: 2019/6/3 10:38
@Desc: define your website http://www.***.com
'''

import sys
sys.path.append('..')
import requests,json,time,random
from redis.sentinel import Sentinel
from config import sample_conf


headers = {
        'User-Agent': random.choice(sample_conf.USER_AGENTS),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Connection': 'keep-alive',
        'Accept-Encoding': 'gzip, deflate',
    }    
          
def __get_ip():
    '''请在此处添加API'''
    resp = requests.get(url=sample_conf.url).content
    print(resp)
    proxies = json.loads(resp)
    proxies = proxies['data']
    return proxies
    
    
def get_ip():
    '''增加retry操作'''
    retry_times = 10
    while retry_times >0:
        try: 
            proxies = __get_ip()
        except:
            proxies = False
        if proxies:
            return proxies
        else:
            retry_times -= 1

def connect_redis():
    '''连接redis'''
    sentinel = Sentinel(sample_conf.REDIS_SENTINELS)
    r = sentinel.master_for('mymaster', db=sample_conf.DB)
    return r

def add_redis_ip():
    '''往redis中添加IP'''
    try:
        r = connect_redis()
    except Exception as e:
        raise Exception('redis connect fail :',e)
    try:
        proxies = get_ip()
    except:
        proxies = None
        print('获取IP失败，休眠一会！')
    if proxies:
        for proxy in proxies:
            if 'ip' in proxy:
                r.sadd(sample_conf.REDIS_KEY, proxy)
    else:
        time.sleep(sample_conf.idletime)


