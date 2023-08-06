import os
import requests, json
from urllib3.exceptions import HTTPError

from starsaiot_monit.logger import logger
from os import path
import pkg_resources
from starsaiot_monit.monit.utils.device_utils import get_device_sn,get_device_model,get_pk_version
from starsaiot_monit.monit.utils.local_storage_old import get,put

class Conf:
    def __init__(self):
        logger.info("Conf init ..")

        self._conf_dir = os.path.join(os.getcwd(), path.dirname(path.abspath(__file__)) + "/config")
        # self._monitJson = self.setMonitJson()
        # self.dynamicRegister()

    # def setMonitJson(self):
    #     filePath = (self._conf_dir + '/monit1.json').replace('/', path.sep)
    #     if not os.path.exists(filePath):
    #         file = open(filePath, mode='w')
    #         file.write('{"deviceId": ""}')
    #         file.close()
    #         return {}
    #     with open(filePath, 'r', encoding='utf-8') as f:
    #         return json.loads(f.read())
    #
    # def getMonitJson(self):
    #     filePath = (self._conf_dir + '/monit1.json').replace('/', path.sep)
    #     if self._monitJson == {}:
    #         with open(filePath, 'r', encoding='utf-8') as f:
    #             return json.loads(f.read())
    #     return self._monitJson

    def dynamicRegister(self):
        url = 'http://device.starsaiot.com:9600/hercules/open/api/v1/device/monitor/dynamicRegister'
        data = json.dumps({
            'deviceSn': get_device_sn(),
            'deviceName': '设备-'+get_device_model()+'-'+get_device_sn(),
            'runFirewareVersion': get_pk_version(),
            'devModel': get_device_model(),
            'runAppVersionCode': '0',
            'runAppVersionName': pkg_resources.get_distribution('starsaiot-monit').version,
        })
        # 设置请求头
        headers = {"content-type": "application/json"}
        try:
            response = requests.post(url, data, headers = headers)
            text = json.loads(response.text)
            logger.info(text)
            if(response.status_code == 200 and text['success']):
                # self._monitJson['deviceId'] = text['content']['deviceId']
                # self._monitJson['deviceToken'] = text['content']['deviceToken']
                put("device_id",text['content']['deviceId'])
                put("device_token",text['content']['deviceToken'])
                # with open((self._conf_dir + '/monit1.json').replace('/', os.path.sep), 'w', encoding='utf-8') as f:
                #     f.write(json.dumps(self._monitJson))
                return True
        except Exception as e:
            logger.exception('Dynamic registration exception..')
        return False

monitJson = Conf()