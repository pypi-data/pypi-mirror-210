import os
import platform
import hashlib

sys = platform.system().lower()
if sys == "windows":
    mac_dir = "D:/etc/starsaiot-monit/eth0/address".replace('/', os.path.sep)
    model_dir = "D:/etc/starsaiot-monit/device-tree/compatible".replace('/', os.path.sep)
    pk_dir = "D:/etc/starsaiot-monit/issue".replace('/', os.path.sep)
elif sys == "linux":
    mac_dir = "/sys/class/net/eth0/address".replace('/', os.path.sep)
    model_dir = "/proc/device-tree/compatible".replace('/', os.path.sep)
    pk_dir = "/etc/issue".replace('/', os.path.sep)
    pass
else:
    pass


def get_mac():
    with open(mac_dir, 'r', encoding='utf-8') as f:
        content = f.read()
    content = content.strip().lower()
    return content


def get_device_sn():
    mac = get_mac();
    # mac_md5 = hashlib.md5(mac.encode()).hexdigest()
    device_sn = mac.replace(":","")
    return device_sn;


def get_device_model():
    with open(model_dir, 'r', encoding='utf-8') as f:
        content = f.read()
    content = content.strip()
    arr = (content.split(',')[1]).split('-')
    model_str = arr[0] + '-' + arr[1]
    model_str = model_str.upper()
    return model_str;

def get_pk_version():
    with open(pk_dir, 'r', encoding='utf-8') as f:
        content = f.read()
    content = content.strip()
    return content;



if __name__ == "__main__":
    print("mac:" + get_mac())
    print()
    print("device_sn:" + get_device_sn())
    print()
    print("model:" + get_device_model())
    print()
    print("pk_version:" + get_pk_version())
