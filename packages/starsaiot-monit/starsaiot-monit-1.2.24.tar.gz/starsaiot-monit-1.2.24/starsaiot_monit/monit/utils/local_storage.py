import os
import platform
import sqlite3 as sq3
from threading import Lock,Thread
import logging.config
from datetime import datetime
from time import sleep
import math
import uuid

log = logging.getLogger('service')
db_version = 1

sys = platform.system().lower()
if sys == "windows":
    db_dir = "D:/etc/starsaiot-monit/local-storage/".replace('/', os.path.sep)
elif sys == "linux":
    db_dir = "/etc/starsaiot-monit/local-storage/".replace('/', os.path.sep)
    pass
else:
    pass

if not os.path.exists(db_dir):
    os.makedirs(db_dir)

db_file_name = 'stroage_' + str(db_version) + ".db";
lock = Lock()

sql_create_table = '''
        CREATE TABLE if not exists stroage(
           s_key                 VARCHAR(128) PRIMARY KEY NOT NULL,
           s_value               TEXT,
           update_time           DATETIME,
           create_time           DATETIME
       );
       '''
class LocalStorage:

    def __init__(self):
        self._conn = None
        self._data = {}
        print("create_LocalStorage >> " + str(id(self)) + ' version=' + str(db_version) + " ")

    def connect(self):
        with lock:
            if self._conn is None:
                try:
                    db_path = db_dir + db_file_name
                    log.info("local_storage.db文件路径：" + db_path)
                    self._conn = sq3.connect(db_path, check_same_thread=False)
                    self._cur = self._conn.cursor()
                    self.crate_tables()
                    self.read_data()
                except Exception as e:
                    log.error("local_storage.db connect error: " + str(e))
                    self._conn = None
                    self._cur = None
                    return False
                finally:
                    pass
            return True

    def crate_tables(self):
        try:
            log.info("local_storage.db.创建表sql：" + sql_create_table)
            self._cur.execute(sql_create_table)
            self._conn.commit()
            log.info("local_storage.db.创建表成功")
        except Exception as e:
            log.error("local_storage创建表异常：" + str(e))
    def read_data(self):
        sql_select_all = "select s_key,s_value,update_time,create_time from stroage"
        self._cur.execute(sql_select_all)
        all = self._cur.fetchall()
        log.info("local_storage.all : "+str(all))
        for row in all:
            self._data[row[0]] = row[1]

    def insert(self,key,value):
        is_conn = self.connect()
        is_in = False
        with lock:
            is_in = self.contains_sql(key)
            if not is_in:
                now = datetime.now()
                values = (key, value,now,now)
                sql_insert = "INSERT INTO stroage " \
                             "(s_key,s_value,update_time,create_time)" \
                             "values" \
                             "(?,?,?,?)"
                if is_conn:
                    # log.info("local_storage获取失败ins sql：" + str(sql_insert) + '  values=' + str(values))
                    self._cur.execute(sql_insert, values)
                    self._conn.commit()
                    pass
                else:
                    log.error("local_storage获取失败ins：" + str(sql_insert))
            else:
                log.info("local_storage获取失败ins is_in：" +'  values=' + str((key,value)))

    def update(self, key, value):
        is_conn = self.connect()
        is_in = False
        with lock:
            is_in = self.contains_sql(key)
            if is_in:
                now = datetime.now()
                values = (value, now,key)
                sql_insert = "update stroage set " \
                             "s_value = ?,update_time=? " \
                             "where s_key = ?"
                if is_conn:
                    # log.info("local_storage upd sql：" + str(sql_insert) + '  values=' + str(values))
                    self._cur.execute(sql_insert, values)
                    self._conn.commit()
                    pass
                else:
                    log.error("local_storage获取失败.conn upd：" + str(sql_insert))
            else:
                log.info("local_storage获取失败upd not_is_in：" + '  values=' + str((key, value)))

    def delete(self, key):
        is_conn = self.connect()
        is_in = False
        with lock:
            is_in = self.contains_sql(key)
            if is_in:
                sql_insert = "delete from stroage " \
                             "where s_key = '"+str(key)+"'"
                if is_conn:
                    # log.info("local_storage获取失败del sql：" + str(sql_insert) )
                    self._cur.execute(sql_insert)
                    self._conn.commit()
                    pass
                else:
                    log.error("local_storage获取失败del：" + str(sql_insert))
            else:
                log.info("local_storage获取失败del not_is_in：" + '  values=' + str(key))

    def get_str(self,key="default_", default_=None):
        return self._data.get(key,default_)

    def contains(self, key="default_"):
        self.connect()
        return key in self._data

    def contains_sql(self, key="default_"):
        # self.connect()
        data = {}
        sql_select_all = "select s_key,s_value,update_time,create_time from stroage"
        self._cur.execute(sql_select_all)
        all = self._cur.fetchall()
        # log.info("local_storage.all : " + str(all))
        for row in all:
            data[row[0]] = row[1]
        return key in data

    def put_str(self,key="default_",val=None):
        self.connect()
        val = str(val)
        if self.contains(key):
            self.update(key,val)
        else:
            self.insert(key,val)
        self._data[key] = val

    def remove(self,key="default_"):
        self.connect()
        self.delete(key)
        if key in self._data:
            del self._data[key]

    def all_data(self):
        self.connect()
        return self._data

local_storage = LocalStorage()

if __name__ == "__main__":
    logging.config.fileConfig("D:/etc/starsaiot-monit/config/logs.conf", disable_existing_loggers=False)
    # from thingsboard_gateway.tb_utility.local_storage import local_storage

    # local_storage.put_str("serial_open_COM5",True)
    # print(local_storage.get_str("first_run"))
    # local_storage.put_str("first_run",False)
    # print(local_storage.get_str("first_run"))
    # print(local_storage.contains("first_run"))
    # local_storage.remove("first_run")
    # print(local_storage.contains("first_run"))

    # print(get("first_run"))
    # Thread(target=write_test,name="1").start();
    # Thread(target=write_test,name="2").start();
    # Thread(target=write_test()).start();
    # print(local_storage.all_data())

    # for key in local_storage.all_data():
    #     if(str(key).startswith("serial_")):
    #         print(key)
    # local_storage.put_str("testing",False)
    # testing = local_storage.get_str('testing')
    #
    # if testing:
    #     print('--'+testing)
    # else:
    #     print("---"+testing)
    local_storage.remove('not_is_in')