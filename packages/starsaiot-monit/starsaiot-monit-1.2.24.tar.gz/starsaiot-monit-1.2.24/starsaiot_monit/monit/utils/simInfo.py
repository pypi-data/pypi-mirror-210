# -*- coding: UTF-8 -*-
import os
import platform
import threading
import time
import netifaces
import ping3 as ping3
from yaml import safe_load,dump

CONFIG_PATH = "/etc/starsaiot-monit/config/monit.yaml".replace('/', os.path.sep)

# 模块信息
acminfo = "/etc/qzwirelessinfo/auto_config_mode_info"
# 拨号方式
acd = "/etc/qzwirelessinfo/auto_config_dial"
# IMEI
acsie = "/etc/qzwirelessinfo/auto_config_mode_info_imei"
# IMSI
acimsi = "/etc/qzwirelessinfo/auto_config_sim_imsi"
# ICCID
acsid = "/etc/qzwirelessinfo/auto_config_sim_iccid"
# 信号值
csq = "/etc/qzwirelessinfo/auto_config_mode_csq"

class SimInfo:

    def __init__(self, config_file):
        # True 读取系统文件的数据信息
        # Flase 程序自己cat 串口信息
        self.__mode = True
        if os.path.exists(config_file):
            with open(config_file, encoding="UTF-8") as general_config:
                config = safe_load(general_config)
            if config["monit"].get("simmode"):
                self.__mode = config["monit"].get("simmode")
            else:
                self.__mode = False

        print("拨号方式 ", self.__mode)

        self.__queri_time = 30
        # 模块是否存在
        self.__haveModular=False
        # SIM卡是否存在
        self.__haveSIMCard = False
        # 是否拨号成功
        self.__havePPP = False
        # 默认路由，设备网络出口
        # not-无网络  有线eth0 eth1  4G-wwan0    wifi-wlan0
        self.__defRoute = "not"

        #ping 包延时
        self.__pingDelay = 0

        # 模块端口号
        self.__modularPort = ""
        # 参数文件路径
        self.__ec20file = "/etc/ec20.info"

        # IMEI读取后面不再继续读
        self.__readiImei=False
        # 小区信息读取
        self.__readiLacCi = False
        # IMSI
        self.__readiImsi = False
        # ICCID
        self.__readiIccid = False

        # 模块型号
        self.__modularMode=""
        # 模块版本信息
        self.__modularVersion = ""
        # iccid
        self.__iccid = ""
        # imei
        self.__imei = ""
        # imsi
        self.__imsi = ""
        # lac 字符串类型。位置区编号。2 个字节（十六进制格式）。
        self.__lac=""
        # 字符串类型。小区 ID。16 位（GSM）或 28 位（UMTS/LTE）（十六进制格式）
        self.__ci=""
        # 信号强度
        self.__rssi = 0
        # 运营商
        self.__operator = ""

        sys = platform.system().lower()
        if sys == "linux":
            if self.__mode == False:
                self.thread_getinfo = threading.Thread(target=self.__thread_readfun, daemon=True, name="get 4G info")
                self.thread_getinfo.start()
            else:
                self.thread_getinfo = threading.Thread(target=self.__thread_readfun2, daemon=True, name="get 4G info")
                self.thread_getinfo.start()


    # 检查模块是否存在
    def checkModular(self):
        result = os.popen("ls /dev/ttyUSB*")
        res = result.read()
        if len(res) == 0:
            # print("not 4G modular")
            return False
        else:
            str_list = res.split()
            # print("all port ", len(str_list), str_list)
            if len(str_list)==6:
                if "/dev/ttyUSB4" in str_list:
                    self.__modularPort = "/dev/ttyUSB4"
                    # print("have modular ", self.__modularPort)
                    return True
                else:
                    # print("not find port")
                    return False
            elif len(str_list) == 5:
                if "/dev/ttyUSB3" in str_list:
                    self.__modularPort = "/dev/ttyUSB3"
                    # print("have modular ", self.__modularPort)
                    return True
                else:
                    # print("not find port")
                    return False
            elif len(str_list)==4:
                if "/dev/ttyUSB2" in str_list:
                    self.__modularPort = "/dev/ttyUSB2"
                    # print("have modular ", self.__modularPort)
                    return True
            elif len(str_list) == 3:
                if "/dev/ttyUSB1" in str_list:
                    self.__modularPort = "/dev/ttyUSB1"
                    # print("have modular ", self.__modularPort)
                    return True
                else:
                    # print("not find port")
                    return False

    # cat数据到文件
    def creatInfoFile(self):
        cmd_grep = "ps aux | grep "+self.__modularPort+" | grep -v grep"
        result = os.popen(cmd_grep)
        res = result.read()
        if len(res) == 0:
            # >> 追加保存   > 覆盖保存
            cmd_cat = "sudo cat "+self.__modularPort+" > " + self.__ec20file + " &"
            # print(cmd_cat)
            os.system(cmd_cat)
            # 延时 保证读的程序先起来，不然写AT指令的时候可能收不到数据
            time.sleep(1)

    # 关闭端口
    def clsoePort(self):
        cmd_grep = "ps aux | grep "+self.__modularPort+" | grep -v grep"
        result = os.popen(cmd_grep)
        res = result.read()
        if not (len(res) == 0):
            for line in res.splitlines():
                str_list = line.split()
                killcmd = "sudo kill -9 " + str_list[1]
                # print(" remove pid ", killcmd)
                os.system(killcmd)

    # 发送AT指令
    def setAtcomd(self, atcmod):
        comd = "echo -e \"" + atcmod + "\" > " +self.__modularPort
        # print("query ", comd)
        os.system(comd)
        time.sleep(0.5)



    # 模块是否存在
    def readec20Mode(self):
        # 移远模块
        cmd_grep = "cat " + self.__ec20file + " | grep Quectel"
        result_revi = os.popen(cmd_grep)
        res_revi = result_revi.read()
        self.__modularMode = res_revi.replace(" ", "").replace('\n', '').replace('\r', '')
        print("mode=", self.__modularMode)
        if not (len(res_revi) == 0):
            cmd_grep = "cat " + self.__ec20file + " | grep Revision | awk -F \":\" \'{print $2}\'"
            result_revi = os.popen(cmd_grep)
            res_revi = result_revi.read()
            # print(" Revision ", res_revi)
            if (len(res_revi))==0:
                self.__haveModular=False
            else:
                self.__haveModular = True
                self.__modularVersion=res_revi.replace(" ", "").replace('\n', '').replace('\r', '')
                print("modularVersion=", self.__modularVersion)

    # IMSI
    def readec20InfoImsi(self):
        cmd_grep = "cat " + self.__ec20file
        result = os.popen(cmd_grep)
        res = result.read()
        if not (len(res) == 0):
            # print("IMSI ", res, res.split())
            if len(res.split()) == 2:
                self.__imsi = res.split()[0].strip()
                print("IMSI=", self.__imsi)
                # 根据IMSI获取运营商   460085335308138
                tmp = self.__imsi[3:5]
                tmpyd = ["00", "02", "04", "07", "08"]
                tmplt = ["01", "06", "09"]
                tmpdx = ["05", "03", "11"]
                tmptt = ["20"]
                if tmp in tmpyd:
                    self.__operator="中国移动"
                elif tmp in tmplt:
                    self.__operator = "中国联通"
                elif tmp in tmpdx:
                    self.__operator = "中国电信"
                elif tmp in tmptt:
                    self.__operator = "中国铁通"
                else:
                    self.__operator = "其他运营商"
                self.__readiImsi = True
                print("运营商 ", self.__operator)


    # CIID
    def readec20CIID(self):
        cmd_grep = "cat " + self.__ec20file + " | grep QCCID"
        result = os.popen(cmd_grep)
        res = result.read()
        if not (len(res) == 0):
            # print("QCCID ", res, res.split())
            if len(res.split()) == 2:
                print("iccid=", res.split()[1].strip())
                self.__iccid = res.split()[1].strip()
                self.__haveSIMCard = True

    # 信号值
    def readec20InfoCSQ(self):
        cmd_grep = "cat " + self.__ec20file + " | grep CSQ"
        result = os.popen(cmd_grep)
        res = result.read()
        if not (len(res) == 0):
            # print("CSQ ", res, res.split())
            if len(res.split()) == 2:
                # print("sign=", res.split()[1].strip())
                all = res.split()[1].split(",")
                if len(all) == 2:
                    self.__rssi = int(all[0])
                    # print("rssi=", int(all[0]))
    # 0 小于等于-113 dBm
    # 1 -111 dBm
    # 2~30 -109 ~ -53 dBm
    # 31 大于等于-51 dBm
    # 99 未知或不可测
    # 100 小于等于-116 dBm
    # 101 -115 dBm
    # 102~190 -114 ~ -26 dBm
    # 191 大于等于-25 dBm
    # 199 未知或不可测
    # 100~199 扩展用于 TD-SCDMA 指示接收信号码功率（RSCP）

    # IMEI
    def readec20InfoImei(self):
        cmd_grep = "cat " + self.__ec20file
        result = os.popen(cmd_grep)
        res = result.read()
        # print("imei ", res, res.split())
        if len(res.split()) == 2:
            self.__imei = res.split()[0].strip()
            self.__readiImei = True
            print("imei=", self.__imei)

    # 小区信息
    def readec20InfoLacCi(self):
        cmd_grep = "cat " + self.__ec20file + "| grep CREG | awk -F \":\" \'{print $2}\'"
        result = os.popen(cmd_grep)
        res = result.read()
        tstring = res.split(",")
        if len(tstring) == 5:
            self.__lac = eval(tstring[2].strip())
            self.__ci = eval(tstring[3].strip())
            print("lac ", self.__lac)
            print("ci ", self.__ci)


    def __thread_readfun(self):
        time_prev = 0
        while True:
            time_cur = int(time.time() * 1000)
            if time_prev < time_cur:
                time_prev = time_cur + self.__queri_time * 1000

                second = ping3.ping('www.baidu.com', unit="ms")
                if second == False or second == None:
                    self.__pingDelay = 520
                else:
                    self.__pingDelay=int(second)

                # 默认路由，设备网络出口
                defroute = os.popen("ip route | grep default | awk '{print $5}'").read()
                # print("siminfo ------- 默认路由接口" , defroute.splitlines())
                self.__defroute = defroute.splitlines()
                for line in defroute.splitlines():
                    if "eth0" in line or "eth1" in line or "wwan0" in line:
                        self.__defRoute=line
                        # print(" 默认路由 ", self.__defRoute)
                        break
                # not-无网络  有线eth0 eth1  4G-wwan0    wifi-wlan0
                # self.__defRoute = "not"
                if not self.checkModular():
                    print(" not 4G port, not find port")
                    return
                else:
                    # 模块存在
                    if not self.__haveModular:
                        self.creatInfoFile()
                        self.setAtcomd("ATI\\r\\n")
                        self.clsoePort()
                        self.readec20Mode()

                    if (not self.__haveSIMCard) and self.__haveModular:
                        print("没有找到SIM卡")
                        self.creatInfoFile()
                        self.setAtcomd("AT+QCCID\\r\\n")
                        self.clsoePort()
                        self.readec20CIID()
                        time.sleep(1)
                    if (not self.__readiImsi) and self.__haveSIMCard and self.__haveModular:
                        self.creatInfoFile()
                        self.setAtcomd("AT+CIMI\\r\\n")
                        self.clsoePort()
                        self.readec20InfoImsi()
                        # self.__readiImsi = True
                        time.sleep(1)
                    if (not self.__readiImei) and self.__haveSIMCard and self.__haveModular:
                        self.creatInfoFile()
                        self.setAtcomd("AT+GSN\\r\\n")
                        self.clsoePort()
                        self.readec20InfoImei()
                        # self.__readiImei=True
                        time.sleep(1)
                    if (not self.__readiLacCi) and self.__haveSIMCard and self.__haveModular:
                        self.creatInfoFile()
                        self.setAtcomd("AT+CREG=2\\r\\n")
                        self.setAtcomd("AT+CREG?\\r\\n")
                        self.clsoePort()
                        self.readec20InfoLacCi()
                        self.__readiLacCi = True

                    if self.__haveSIMCard and self.__haveModular:
                        self.creatInfoFile()
                        self.setAtcomd("AT+CSQ\\r\\n")
                        self.clsoePort()
                        self.readec20InfoCSQ()
                        # print(" 网络接口 ", netifaces.interfaces())
                        if 'wwan0' in netifaces.interfaces():
                            # print('4G 拨号成功')
                            self.__havePPP=True
                        else:
                            # print('4G 拨号失败')
                            self.__havePPP = False
            time.sleep(0.1)

    def __thread_readfun2(self):
        print("---------------------")
        time_prev = 0
        while True:
            time_cur = int(time.time() * 1000)
            if time_prev < time_cur:
                time_prev = time_cur + self.__queri_time * 1000
                for i in range(3):
                    second = ping3.ping('www.baidu.com', unit="ms")
                    if second == False or second == None:
                        self.__pingDelay = 520
                    else:
                        self.__pingDelay = int(second)
                    time.sleep(0.1)

                    # 默认路由，设备网络出口
                defroute = os.popen("ip route | grep default").read()
                # print("siminfo ------- 默认路由接口", defroute.splitlines())
                if len(defroute.splitlines()) > 0:
                    if "ppp0" in defroute.splitlines()[0]:
                        self.__defRoute="ppp0"
                        self.__havePPP = True
                    elif "eth0" in defroute.splitlines()[0]:
                        self.__defRoute="eth0"
                        self.__havePPP = False
                    elif "eth1" in defroute.splitlines()[0]:
                        self.__defRoute="eth1"
                        self.__havePPP = False
                    else:
                        self.__defRoute = "not"
                        self.__havePPP = False

                if not self.__haveModular:
                    if os.path.exists(acminfo):
                        with open(acminfo, encoding='utf-8') as file_obj:
                            contents = file_obj.read()
                        print("模块信息", contents.rstrip())
                        modularInfo = contents.rstrip().split("OK")[0]
                        if "Revision" in modularInfo:
                            self.__haveModular = True
                            self.__modularMode = ""
                            self.__modularVersion = modularInfo
                            print("modularInfo: ", modularInfo)
                        else:
                            print(" not 4G port, not find port")
                    else:
                        print(" not 4G port, not find port")

                if self.__haveModular:
                    #模块存在
                    if not self.__readiImsi:
                        if os.path.exists(acimsi):
                            with open(acimsi, encoding='utf-8') as file_obj:
                                contents = file_obj.read()
                            # print("Imei", contents.rstrip())

                            print("===========================")
                            list = contents.rstrip().split("OK")[0].split("\n")
                            arr = []
                            for sss in list:
                                # print(len(sss))
                                if len(sss) > 0:
                                    print(sss.strip())
                                    arr.append(sss.strip())
                            print("===========================")

                            imsi = arr[-1]
                            print("imsi", imsi)
                            self.__imsi = imsi
                            # 根据IMSI获取运营商   460085335308138
                            tmp = self.__imsi[3:5]
                            tmpyd = ["00", "02", "04", "07", "08"]
                            tmplt = ["01", "06", "09"]
                            tmpdx = ["05", "03", "11"]
                            tmptt = ["20"]
                            if tmp in tmpyd:
                                self.__operator = "中国移动"
                            elif tmp in tmplt:
                                self.__operator = "中国联通"
                            elif tmp in tmpdx:
                                self.__operator = "中国电信"
                            elif tmp in tmptt:
                                self.__operator = "中国铁通"
                            else:
                                self.__operator = "其他运营商"
                            self.__readiImsi = True
                            print("IMSI=", self.__imsi)
                            print("运营商 ", self.__operator)
                        else:
                            print("没有 imsi")

                    if not self.__readiImei:
                        if os.path.exists(acsie):
                            with open(acsie, encoding='utf-8') as file_obj:
                                contents = file_obj.read()
                            # print("Imei", contents.rstrip())
                            print("===========================")
                            list = contents.rstrip().split("OK")[0].split("\n")
                            arr = []
                            for sss in list:
                                # print(len(sss))
                                if len(sss) > 0:
                                    print(sss.strip())
                                    arr.append(sss.strip())
                            print("===========================")

                            imei = arr[-1]
                            self.__imei = imei
                            print("Imei", imei)
                            self.__readiImei=True
                        else:
                            print("没有 Imei")

                    if not self.__readiIccid:
                        if os.path.exists(acsid):
                            with open(acsid, encoding='utf-8') as file_obj:
                                contents = file_obj.read()
                            # print("ICCID:", contents.rstrip())
                            print("===========================")
                            list = contents.rstrip().split("OK")[0].split("\n")
                            arr = []
                            for sss in list:
                                # print(len(sss))
                                if len(sss) > 0:
                                    print(sss.strip())
                                    arr.append(sss.strip())
                            print("===========================")

                            iccid = arr[-1].replace("+QCCID:", "")
                            print("ICCID", iccid)
                            self.__iccid=iccid
                            self.__readiIccid=True
                            self.__haveSIMCard = True
                        else:
                            print("没有 iccid ")

                    if self.__readiIccid and self.__readiImsi:
                        if os.path.exists(csq):
                            with open(csq, encoding='utf-8') as file_obj:
                                contents = file_obj.read()
                            print("信号值:", contents.rstrip())
                            print("===========================")
                            list = contents.rstrip().split("OK")[0].split("\n")
                            arr = []
                            for sss in list:
                                # print(len(sss))
                                if len(sss) > 0:
                                    print(sss.strip())
                                    arr.append(sss.strip())
                            print("===========================")
                            signal_arr = arr[-1].replace("+CSQ:", "").split(",")
                            if len(signal_arr) == 2:
                                # print(arr[0], arr[1])
                                self.__rssi = int(signal_arr[0])
                            else:
                                print("信号值 未知参数 ", arr)
            time.sleep(0.1)


    def getModular(self):
        return self.__haveModular

    def getSimCard(self):
        return self.__haveSIMCard

    def getIccid(self):
        return self.__iccid

    def getRssi(self):
        return self.__rssi

    def getIMEI(self):
        return self.__imei

    def getIMSI(self):
        return self.__imsi

    def getLac(self):
        return self.__lac

    def getCi(self):
        return self.__ci

    def getOperator(self):
        return self.__operator

    def getModularMode(self):
        return self.__modularMode

    def getModularVersion(self):
        return self.__modularVersion

    def getHavePPP(self):
        return self.__havePPP

    def getDefRoute(self):
        return self.__defRoute

    def getPingDelay(self):
        return self.__pingDelay


sim_info = SimInfo(CONFIG_PATH)

if __name__ == '__main__':
    while True:
        print("拨号成功 ",sim_info.getHavePPP())
        time.sleep(5)