#!/usr/bin/python3
# __*__ coding: utf-8 __*__

'''
@Author: Simon
@License: (C) Copyright 2013-2018, Best Wonder Corporation Limited.
@Os：Windows 10 x64
@Contact: 763646402@qq.com
@Software: PY PyCharm
@File: check_redis_ip.py
@Time: 2019/6/3 10:38
@Desc: define your website http://www.***.com
'''
from gevent import monkey;monkey.patch_all()
import sys
import random
sys.path.append('..')
from config import sample_conf
import gevent,time,requests,json,re
from add_ips.add_redis_ip import connect_redis

# 连接redis
redis = connect_redis()

# 加载请求头
def get_header():
    return {
        'User-Agent': random.choice(sample_conf.USER_AGENTS),
        'Accept': 'text/static,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Connection': 'keep-alive',
        'Accept-Encoding': 'gzip, deflate',
    }

# 检测IP
def check_redis_ip(data):
    info = data['data']
    infos = str(info, "utf-8")
    infos = re.sub('\'', '\"', infos)
    info_ip = json.loads(infos)
    ip = info_ip.get('ip')
    port = info_ip.get('port')
    proxy = 'http://' + ip + ':' + str(port)
    proxys = 'https://' + ip + ':' + str(port)
    url = 'http://jxj.beijing.gov.cn/'
    try:
        r = requests.get(url=url, headers=get_header(), timeout=2, proxies={'http': proxy,'https':proxys})
        # print(r.status_code)
        if r.ok:
            pass
        else:
            redis.srem('proxies', info)
            print('删除成功', proxy)
    except Exception as e:
        redis.srem('proxies', info)
        print('异常删除成功', proxy)

# redis中开始检测IP
def run_check_redis_ip():
    try:
        datas = redis.srandmember('proxies',sample_conf.poolsize)
    except:
        datas = redis.srandmember('proxies', sample_conf.poolsize)
    for data in datas:
        gevent.spawn(check_redis_ip, {'data':data})
        time.sleep(0.05)

