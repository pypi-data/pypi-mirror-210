import os
import string
#!/usr/bin/env python
#coding:utf-8

import time
import json
from os import path

import psutil
import random
from paho.mqtt import client as mqtt_client

broker = '192.168.2.115'  # mqtt代理服务器地址
port = 1883
keepalive = 60     # 与代理通信之间允许的最长时间段（以秒为单位）
topic = "/python/test01"  # 消息主题
client_id = f'python-mqtt-pub-{random.randint(0, 1000)}'  # 客户端id不能重复

def to_M(n):
    '''将B转换为M'''
    u = 1024 * 1024
    m = round(n / u, 2)
    return m

def get_info():
    '''获取系统硬件信息：cpu利用率，cpu个数，系统负载，内存信息等'''
    cpu_percent = psutil.cpu_percent(interval=1)
    cpu_count = psutil.cpu_count()
    sys_loadavg = [round(x / psutil.cpu_count() * 100, 2) for x in psutil.getloadavg()]
    mem = psutil.virtual_memory()
    mem_total, men_free = to_M(mem.total), to_M(mem.free)
    mem_percent = mem.percent
    info = {
        'cpu_percent': cpu_percent,
        'cpu_count' : cpu_count,
        'sys_loadavg': sys_loadavg,
        'mem_total': mem_total,
        'mem_percent': mem_percent,
        'men_free': men_free
    }
    # mqtt只能传输字符串数据
    return json.dumps(info)

def connect_mqtt():
    '''连接mqtt代理服务器'''
    def on_connect(client, userdata, flags, rc):
        '''连接回调函数'''
        # 响应状态码为0表示连接成功
        if rc == 0:
            print("Connected to MQTT OK!")
        else:
            print("Failed to connect, return code %d\n", rc)
    # 连接mqtt代理服务器，并获取连接引用
    client = mqtt_client.Client(client_id)
    client.username_pw_set("test01", "test01")
    client.on_connect = on_connect
    client.connect(broker, port, keepalive)
    return client

def publish(client):
    '''发布消息'''
    while True:
        '''每隔4秒发布一次服务器信息'''
        time.sleep(4)
        msg = get_info()
        result = client.publish(topic, msg)
        status = result[0]
        if status == 0:
            print(f"Send `{msg}` to topic `{topic}`")
        else:
            print(f"Failed to send message to topic {topic}")

def run():
    '''运行发布者'''
    client = connect_mqtt()
    # 运行一个线程来自动调用loop()处理网络事件, 非阻塞
    client.loop_start()
    publish(client)

if __name__ == '__main__':
    # run()
    # print(int(time.mktime(time.localtime(time.time()))))
    # print(os.popen('ls').read())
    # print(os.path.exists("/wewer"))
    # print(os.path.abspath(os.path.dirname(os.path.dirname(__file__))))
    s = 'Hello, world!'
    new_s = s[2:-2]
    print(new_s)