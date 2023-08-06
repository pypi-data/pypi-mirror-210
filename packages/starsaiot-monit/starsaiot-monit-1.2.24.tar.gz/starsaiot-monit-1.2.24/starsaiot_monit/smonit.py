from os import curdir, listdir, mkdir, path

from starsaiot_monit.monit.monit_service import MonitService


def main():
    # if "logs" not in listdir(curdir):
    #     mkdir("logs")
    MonitService(path.dirname(path.abspath(__file__)) + '/config/monit.yaml'.replace('/', path.sep))


def daemon():
    # if "logs" not in listdir(curdir):
    #     mkdir("logs")
    MonitService("/etc/starsaiot_monit/config/monit.yaml".replace('/', path.sep))


if __name__ == '__main__':
    main()