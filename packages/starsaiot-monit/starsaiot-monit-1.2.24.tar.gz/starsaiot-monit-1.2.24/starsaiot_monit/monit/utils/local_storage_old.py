import os
import platform
from threading import Lock,Thread,current_thread
from time import sleep

from json import dumps,load,loads

sys = platform.system().lower()
if sys == "windows":
    local_dir = "D:/etc/starsaiot-monit/local-stroage/".replace('/', os.path.sep)
elif sys == "linux":
    local_dir = "/etc/starsaiot-monit/local-stroage/".replace('/', os.path.sep)
    pass
else:
    pass
data_file = local_dir+'data.json'.replace('/', os.path.sep)
if not os.path.exists(local_dir):
    os.makedirs(local_dir)
    with open(data_file, 'w', encoding='utf-8') as f:
        f.write(str({}))

local_storage_instance = {}
is_init = False

g_lock = Lock()


def init_instance():
    global local_storage_instance
    global is_init
    if not is_init:
        with g_lock:
            if not is_init:
                if not os.path.exists(data_file):
                    json = dumps({}, indent=2)
                    with open(data_file, 'w', encoding='utf-8') as f:
                        f.write(json)
                else:
                    with open(data_file, 'r', encoding='utf-8') as f:
                        try:
                            local_storage_instance = load(f)
                        except Exception as e:
                            pass
            is_init = True


def get(key,default_=None):
    global local_storage_instance
    init_instance()
    if key in local_storage_instance:
        return local_storage_instance.get(key)
    else:
        return default_


def contains(key=None):
    global local_storage_instance
    init_instance()
    return key in local_storage_instance

def remove(key=None):
    global local_storage_instance
    init_instance()
    with g_lock:
        if key in local_storage_instance:
            del local_storage_instance[key]
            json = dumps(local_storage_instance, indent=2)
            with open(data_file, 'w', encoding='utf-8') as f:
                f.write(json)

def put(key,val):
    global local_storage_instance
    init_instance()
    with g_lock:
        local_storage_instance[key]=val
        json = dumps(local_storage_instance, indent=2)
        with open(data_file, 'w', encoding='utf-8') as f:
            f.write(json)


def write_test(a=100):
    while a>0:
        put("b",1)
        print("a="+str(a)+" "+current_thread().name)
        a=a-1

if __name__ == "__main__":


    put("first_run",True)
    print(get("first_run"))
    put("first_run",False)
    print(get("first_run"))
    print(contains("first_run"))
    remove("first_run")
    print(contains("first_run"))

    # print(get("first_run"))
    # Thread(target=write_test,name="1").start();
    # Thread(target=write_test,name="2").start();
    # Thread(target=write_test()).start();
    put("a",1356)


