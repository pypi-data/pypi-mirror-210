#!/usr/bin/python
# coding=utf-8

import paramiko
import os
from starsaiot_monit.logger import logger

sftp_config = {
    "host": "device.starsaiot.com",
    "username": "ftpDevice",
    "password": "@ycwl4173",
    "port": 22
}

class MySftp:
    def __init__(self):
        self.username = sftp_config['username']
        self.password = sftp_config['password']
        self.host = sftp_config['host']
        self.port = sftp_config['port']

    # 建立连接
    def sftp_connect(self):
        client = None
        sftp = None
        try:
            client = paramiko.Transport((self.host, self.port))
        except Exception as error:
            logger.exception(error)
        else:
            try:
                client.connect(username=self.username, password=self.password)
            except Exception as error:
                logger.exception(error)
            else:
                sftp = paramiko.SFTPClient.from_transport(client)
        return client, sftp

    # 断开连接
    def sftp_disconnect(self, client):
        try:
            client.close()
        except Exception as error:
            logger.exception(error)

    # 检查目录
    def _check_local(self, local):
        if not os.path.exists(local):
            try:
                os.mkdir(local)
            except IOError as err:
                logger.exception(err)

    # def sftp_upload(self):
    #     client, sftp = self.sftp_connect()
    #     try:
    #         sftp.put(local, remote)  # 上传文件
    #     except Exception as e:
    #         logger.error('upload exception:', e)
    #     client.close()
