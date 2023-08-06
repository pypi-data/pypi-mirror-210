import sys
import os
import time
import platform
import logging
import urllib3
import datetime
import shutil
from urllib.parse import *

from pkg_resources import parse_version
from mecord_crawler import utils
from mecord_crawler import aaaapp_crawler
from mecord_crawler import civitai_crawler
from mecord_crawler import group_crawler

def main():
    global rootDir
    global curGroupId
    global env

    urllib3.disable_warnings()
    d = datetime.datetime.now().strftime('%Y_%m_%d_%H_%M_%S')

    thisFileDir = os.path.dirname(os.path.abspath(__file__))
    logFilePath = f"{thisFileDir}/log.log"
    if os.path.exists(logFilePath) and os.stat(logFilePath).st_size > (1024 * 1024 * 5):  # 5m bak file
        d = datetime.datetime.now().strftime('%Y_%m_%d_%H_%M_%S')
        bakFile = logFilePath.replace(".log", f"_{d}.log")
        shutil.copyfile(logFilePath, bakFile)
        os.remove(logFilePath)
    if parse_version(platform.python_version()) >= parse_version("3.9.0"):
        logging.basicConfig(filename=logFilePath, 
                            format='%(asctime)s %(levelname)s %(message)s',
                            datefmt='%a, %d %b %Y %H:%M:%S',
                            encoding="utf-8",
                            level=logging.INFO) 
    else:
        logging.basicConfig(filename=logFilePath, 
                            format='%(asctime)s %(levelname)s %(message)s',
                            datefmt='%a, %d %b %Y %H:%M:%S',
                            level=logging.INFO)

    if len(sys.argv) > 1:
        if sys.argv[1] == "test_request":
            curGroupId = 0
            aaaapp_crawler.aaaapp(False, "https://www.instagram.com/meowbot_iv/", "", 0)
            return
        elif sys.argv[1] == "test_ffmpeg":
            utils.ffmpegTest()
            return
        elif sys.argv[1] == "normal":
            env = sys.argv[1]
        else:
            print(f"not found {sys.argv[1]}")
            return

    rootDir = os.path.dirname(os.path.abspath(__file__))
    print(f"current domain is alpha.2tianxin.com")
    while (os.path.exists(os.path.join(rootDir, "stop.now")) == False):
        try:
            # #默认爬虫
            # aaaapp_crawler.do_aaaapp_crawler()
            # # C站爬虫
            # civitai_crawler.civitai()
            #组爬虫，从外网爬整个人的数据导入到mecord里
            group_crawler.runtask()

        except Exception as e:
            civitai_crawler.notifyMessage(False, str(e))
            logging.error("====================== uncatch Exception ======================")
            logging.error(e)
            logging.error("======================      end      ======================")
        time.sleep(60*60)
        exit(-1)
    os.remove(os.path.join(thisFileDir, "stop.now"))
    print(f"stoped !")


if __name__ == '__main__':
    main()
    # getPostList(14171,187,0)