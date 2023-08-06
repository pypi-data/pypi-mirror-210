import os
import platform
import logging
import logging.handlers as handlers
from os import path
from datetime import datetime

sys = platform.system().lower()
if sys == "windows":
    log_dir = "D:/etc/starsaiot-monit/logs/".replace('/', os.path.sep)
elif sys == "linux":
    log_dir = "/var/log/starsaiot-monit/logs/".replace('/', os.path.sep)
    pass
else:
    pass

def get_log_dir():
    return log_dir

class logFilter(object):
    def __init__(self, level):
        self.__level = level

    def filter(self, logRecord):
        return logRecord.levelno <= self.__level


class CustomLogging(object):
    def __init__(self, name):
        self.logger = logging.getLogger(name)
        self.logger.parent.setLevel(logging.DEBUG)
        self.logger.root.setLevel(logging.DEBUG)
        # log存放的目录
        # self.log_path = os.path.join(
        #     os.getcwd(), path.dirname(path.abspath(__file__)) + "/logs", datetime.now().strftime("%Y-%m-%d"))
        # self.log_path = os.path.join(os.getcwd(), path.dirname(path.abspath(__file__)) + "/logs")
        self.log_path = log_dir
        # log格式化输出
        self.log_formatter = logging.Formatter(
            '%(asctime)s-%(levelname)s : %(message)s', '%Y-%m-%d %H:%M:%S')
        # 控制台输出
        self.set_console_logger()
        # 文件输出日志
        self.set_file_logger()

    def set_console_logger(self):
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)
        console_handler.setFormatter(self.log_formatter)
        self.logger.addHandler(console_handler)

    def set_file_logger(self):
        if not os.path.exists(self.log_path):
            os.makedirs(self.log_path)

        strDate = datetime.now().strftime("%Y-%m-%d")

        messageHandle = handlers.RotatingFileHandler(os.path.join(self.log_path, "mlog_" + strDate + ".log"),
                                                     maxBytes=1024*1024*30, backupCount=50, encoding="utf-8", delay=False)
        messageHandle.setLevel(logging.INFO)
        # messageHandle.addFilter(logFilter(logging.INFO))
        messageHandle.setFormatter(self.log_formatter)
        self.logger.addHandler(messageHandle)

        errorHandle = handlers.RotatingFileHandler(os.path.join(self.log_path, "error_" + strDate + ".log"),
                                               maxBytes=1024*1024*30, backupCount=50, encoding="utf-8", delay=False)
        errorHandle.setLevel(logging.ERROR)
        # errorHandle.addFilter(logFilter(logging.ERROR))
        errorHandle.setFormatter(self.log_formatter)
        self.logger.addHandler(errorHandle)

    def get_logger(self):
        return self.logger
logger = CustomLogging(__name__).get_logger()

if __name__ == "__main__":
    logger.info("Log Info...")
    logger.error("Log Error... %s", 5)


