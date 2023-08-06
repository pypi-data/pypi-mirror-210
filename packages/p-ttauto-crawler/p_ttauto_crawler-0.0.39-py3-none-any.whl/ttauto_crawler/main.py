import sys
import os
import platform
import logging
import urllib3
import datetime
import shutil
from urllib.parse import *
from pkg_resources import parse_version
from ttauto_crawler import utils
from ttauto_crawler import auto_crawler
from ttauto_crawler import txt2proj

def img2video():
    if len(sys.argv) <= 2:
        print('please s')
        return
    dir = sys.argv[2]
    cnt = sys.argv[3]
    if cnt.isdigit() == False:
        print('count is not digit')
        return
    if os.path.exists(dir) == False:
        print(f'path: {dir} not found')
        return
    txt2proj.randomImageCntToVideo(dir, int(cnt))
         
def auto():
    dir = ""
    if len(sys.argv) >= 2:
        dir = sys.argv[2]    
    auto_crawler.autoCrawler(dir)

module_func = {
    "--img2video": img2video,
    "--auto": auto
}

def main():
    urllib3.disable_warnings()
    logFilePath = f"{os.path.dirname(os.path.abspath(__file__))}/log.log"
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

    if len(sys.argv) < 2:
        auto()
        return
    module = sys.argv[1]
    if module in module_func:
        module_func[module]()
        
if __name__ == '__main__':
    main()
