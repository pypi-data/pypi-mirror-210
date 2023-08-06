import os
import platform
import subprocess
import time
import json
from threading import Thread
from time import sleep, strftime
from starsaiot_monit.monit.mqtt_connector import MqttConnector
from starsaiot_monit.logger import logger
from starsaiot_monit.conf import Conf
from starsaiot_monit.monit.utils.local_storage import local_storage
from starsaiot_monit.monit.utils.local_storage_old import get
from starsaiot_monit.monit.utils.simInfo import sim_info


class MonitService:
    def __init__(self, config_file=None):
        self.stopped = False
        config = Conf()
        self._msg_id=0
        while True:
            if config.dynamicRegister():
                break
            else:
                sleep(5)

        # self._monitJson = config.getMonitJson()
        self._monitJson = {
            "deviceId":get("device_id"),
            "deviceToken":get("device_token")
        }
        logger.info("Gateway started.")

        self._mqtt_connect = MqttConnector(self._monitJson['deviceId'])
        self._mqtt_connect.open()
        # self.subscribe()
        # self.realtime()
        realtime_thread = Thread(name="realtime thread", daemon=True, target=self.realtime)
        realtime_thread.start()
        self.__simInfo = sim_info
        telemetry_report_thread = Thread(name="telemetryReport thread", daemon=True, target=self.telemetryReport)
        telemetry_report_thread.start()
        self.startUpSendMsg()

        system_cmd_thread = Thread(name="System restart thread", daemon=True, target=self.systemCmd)
        system_cmd_thread.start()


        try:
            while not self.stopped:
                try:
                    sleep(.1)
                except Exception as e:
                    logger.exception(e)
                    break
        except KeyboardInterrupt:
            self.__stop_monit()
        except Exception as e:
            logger.exception(e)
            self.__stop_monit()
            self.__close_connectors()
            logger.info("The monit has been stopped.")

    def realtime(self):
        sleep(2)
        deviceId = self._monitJson['deviceId']
        while self._mqtt_connect._connected:
            current_time = strftime('%Y-%m-%d %H:%M:%S')
            msgId = deviceId + '_' + str(int(time.mktime(time.localtime(time.time()))))
            data = json.dumps({
                "deviceId": deviceId,
                "id": self._msg_id,
                "msgBody": current_time,
                "msgId": msgId,
                "msgKey": "heartbeat",
                "msgTopic": "\/sys\/platform\/device\/realtime",
                "msgVersion": "V3.0.0",
                "sendTime": current_time
            })
            self._mqtt_connect.sendMsg("/sys/platform/device/realtime", data, 0)
            # self._client.publish("/sys/platform/device/realtime", '{}', 0)
            self._msg_id+=1
            sleep(60)

    def __stop_monit(self):
        self.stopped = True
        logger.info("Stopping...")
        self.__close_connectors()
        logger.info("The monit has been stopped.")

    def __close_connectors(self):
        self._mqtt_connect.close()

    def subscribe(self):
        sleep(1)
        self._mqtt_connect.subscribe('/device/log/' + self._monitJson['deviceId'])
        self._mqtt_connect.subscribe('/device/app/' + self._monitJson['deviceId'])
        self._mqtt_connect.subscribe('/device/cmd/monitor/' + self._monitJson['deviceId'])

    def startUpSendMsg(self):
        sleep(30)
        deviceId = self._monitJson['deviceId']
        current_time = strftime('%Y-%m-%d %H:%M:%S')
        msgId = deviceId + '_' + str(int(time.mktime(time.localtime(time.time()))))
        _msg = {}
        msg_body_list = []

        sys = platform.system().lower()
        if sys == "linux":
            msg_body = {
                "attributeKey": "iccid",
                "attributeDisplayName": "iccid",
                "attributeValue": self.__simInfo.getIccid(),
                "attributeDataType": 2
            }
            msg_body_list.append(msg_body)

            def_route = sim_info.getDefRoute()
            if "eth0" in def_route or "eth1" in def_route:
                netType = {
                    "attributeKey": "netType",
                    "attributeDisplayName": "网络类型",
                    "attributeValue": '有线网络',
                    "attributeDataType": 2,
                }
                msg_body_list.append(netType)
            elif "wlan0" in sim_info.getDefRoute():
                # wifi
                pass
            elif "wwan0" in sim_info.getDefRoute() or "ppp0" in sim_info.getDefRoute():
                netType = {
                    "attributeKey": "netType",
                    "attributeDisplayName": "网络类型",
                    "attributeValue": '4G网络',
                    "attributeDataType": 2,
                }
                msg_body_list.append(netType)
        else:
            msg_body = {
                "attributeKey": "iccid",
                "attributeDisplayName": "iccid",
                "attributeValue": 'iccid111',
                "attributeDataType": 2
            }
            msg_body_list.append(msg_body)

        _msg['msgBody'] = msg_body_list
        _msg['deviceId'] = deviceId
        _msg['id'] = 6
        _msg['msgId'] = msgId
        _msg['msgKey'] = 'attrReport'
        _msg['msgTopic'] = '/sys/platform/device/inform'
        _msg['msgVersion'] = 'V3.0.0'
        _msg['sendTime'] = current_time

        data = json.dumps(_msg)
        self._mqtt_connect.sendMsg("/sys/platform/device/inform", data, 0)


    def telemetryReport(self):
        sleep(30)
        #属性的数据类型attributeDataType：1、json 2、字符串  3、数值型 4、布尔值
        __id = 0
        while True:
            deviceId = self._monitJson['deviceId']
            current_time = strftime('%Y-%m-%d %H:%M:%S')
            msgId = deviceId + '_' + str(int(time.mktime(time.localtime(time.time()))))
            _msg = {}
            msg_body_list = []

            sys = platform.system().lower()
            if sys == "linux":
                # 默认路由，设备网络出口
                def_route = sim_info.getDefRoute()
                logger.info("def_route==" + str(def_route))
                if "eth0" in def_route or "eth1" in def_route:
                    local_storage.put_str("telemetry_report_nettype", "1")
                    pingDelay = {
                        "telemetryKey": "wired",
                        "telemetryDisplayName": "有线网络",
                        "telemetryValue": sim_info.getPingDelay(),
                        "telemetryDataType": 3,
                        "reportTime": current_time
                    }
                    msg_body_list.append(pingDelay)
                elif "wlan0" in def_route:
                    # wifi
                    local_storage.put_str("telemetry_report_nettype", "2")
                elif "wwan0" in def_route or "ppp0" in def_route:
                    local_storage.put_str("telemetry_report_nettype", "3")
                    simDB = {
                        "telemetryKey": "simDB",
                        "telemetryDisplayName": "4G信号值",
                        "telemetryValue": sim_info.getRssi(),
                        "telemetryDataType": 3,
                        "reportTime": current_time
                    }
                    msg_body_list.append(simDB)
                else:
                    __elemetry_report_nettype = local_storage.get_str("telemetry_report_nettype")
                    if __elemetry_report_nettype == "1":
                        pingDelay = {
                            "telemetryKey": "wired",
                            "telemetryDisplayName": "有线网络",
                            "telemetryValue": 0,
                            "telemetryDataType": 3,
                            "reportTime": current_time
                        }
                        msg_body_list.append(pingDelay)
                    elif __elemetry_report_nettype == "2":
                        pass
                    elif __elemetry_report_nettype == "3":
                        simDB = {
                            "telemetryKey": "simDB",
                            "telemetryDisplayName": "4G信号值",
                            "telemetryValue": 0,
                            "telemetryDataType": 3,
                            "reportTime": current_time
                        }
                        msg_body_list.append(simDB)

            # pingDelay = {
            #     "telemetryKey": "wired",
            #     "telemetryDisplayName": "有线网络",
            #     "telemetryValue": sim_info.getPingDelay(),
            #     "telemetryDataType": 3,
            #     "reportTime": current_time
            # }
            # msg_body_list.append(pingDelay)

            _msg['msgBody'] = msg_body_list
            _msg['deviceId'] = deviceId
            _msg['id'] = __id
            _msg['msgId'] = msgId
            _msg['msgKey'] = 'tsReport'
            _msg['msgTopic'] = '/sys/platform/device/inform'
            _msg['msgVersion'] = 'V3.0.0'
            _msg['sendTime'] = current_time

            data = json.dumps(_msg)
            __id+=1

            telemetry_report_datas = []
            trds = local_storage.get_str("telemetry_report_datas")
            if trds:
                trds = json.loads(trds)
                for trd in trds:
                    telemetry_report_datas.append(trd)

            print(self._mqtt_connect._connected)

            if sim_info.getPingDelay() != 520 and self._mqtt_connect._connected:
                status = self._mqtt_connect.sendMsg("/sys/platform/device/inform", data, 0)
                if status != 0:
                    # 消息发送失败
                    telemetry_report_datas.append(data)

                telemetry_report_datas_fail = []
                for trdata in telemetry_report_datas:
                    status = self._mqtt_connect.sendMsg("/sys/platform/device/inform", trdata, 0)
                    if status != 0:
                        # 消息发送失败
                        telemetry_report_datas_fail.append(trdata)
                # logger.info(telemetry_report_datas_fail)
                # logger.info(telemetry_report_datas)
                telemetry_report_datas = telemetry_report_datas_fail
                # logger.info(telemetry_report_datas)
            else:
                telemetry_report_datas.append(data)

            if len(telemetry_report_datas) > 0:
                logger.info(telemetry_report_datas)
                local_storage.put_str("telemetry_report_datas", json.dumps(telemetry_report_datas))
            else:
                local_storage.remove("telemetry_report_datas")
            sleep(600)

    def systemCmd(self):
        while True:
            try:
                with open('/etc/starsaiot-gateway/config/restart.txt', 'r', encoding='utf-8') as f:
                    content = f.read()
                    content = content.rstrip()
                # logger.info("/etc/starsaiot-gateway/config/restart.txt %s", content)
                # print(content)
                content_0 = content[0]
                content_last_two = content[-2:]
                if content_0 == '0' and content_last_two == "##":
                    logger.info("设备命令执行")
                    cmd = content[2:-2]
                    logger.info(cmd)
                    if cmd == "reboot":
                        res = "1#restart success##"
                        os.system("sudo echo " + res + " > /etc/starsaiot-gateway/config/restart.txt")
                        with open('/etc/starsaiot-gateway/config/restart.txt', 'w', encoding='utf-8') as f:
                            f.write(res)
                        subprocess.getstatusoutput(cmd)
                    else:
                        status, output = subprocess.getstatusoutput(cmd)
                        res = "1#status:" + str(status) + ";output:" + output + "##"
                        os.system("sudo echo " + res + " > /etc/starsaiot-gateway/config/restart.txt")
                        with open('/etc/starsaiot-gateway/config/restart.txt', 'w', encoding='utf-8') as f:
                            f.write(res)
            except Exception as e:
                pass
                logger.exception(e)
                # logger.info("文件 /etc/starsaiot-gateway/config/restart.txt 不存在")
            sleep(1)