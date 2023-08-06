import sys
import os
import yt_dlp
import json
import time
import requests
import calendar
import logging
from ftplib import FTP
from urlparser import urlparser
from fake_useragent import UserAgent
from ttauto_crawler import utils

filename = "mecord_group.txt"
local_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)
def ftpClient():
    ftp = None
    try:
        ftp = FTP('192.168.50.113', 'ftpuser', 'ftpuser')
    except:
        ftp = FTP('192.168.3.220', 'xinyu100', 'xinyu100.com')
    if ftp == None:
        raise Exception("no ftp!")
    return ftp

def groupConfig():
    ftp = ftpClient()
    ftp.cwd("mecord/")
    file_list = ftp.nlst()
    if len(file_list) > 0:
        with open(local_file, 'wb') as f:
            ftp.retrbinary('RETR ' + filename, f.write)
    else:
        with open(local_file, 'w') as f:
            json.dump({}, f)
    ftp.quit()
    
    with open(local_file, 'r') as f:
        data = json.load(f)
    return data

def saveGroupConfig(data):
    ftp = ftpClient()
    ftp.cwd("mecord/")
    file_list = ftp.nlst()
    with open(local_file, 'w') as f:
        json.dump(data, f)
    with open(local_file, 'rb') as file:
        ftp.storbinary(f'STOR {filename}', file)
    ftp.quit()

def downloadFile(content_type, name, url, downloadDir):
    timeoutDuration = 3600
    ext = ".mp4"
    # content_type 
    # 1=图片
    # 2=视频
    # 3=音频
    # 4=文字
    if content_type == 1:
        timeoutDuration = 60
        ext = ".jpg"
    savePath = os.path.join(downloadDir, f"{name}{ext}")
    if os.path.exists(savePath):
        os.remove(savePath)
    #download
    requests.adapters.DEFAULT_RETRIES = 2
    s = requests.session()
    s.keep_alive = False
    s.headers.update({'Connection':'close'})
    ua = UserAgent()
    download_start_pts = calendar.timegm(time.gmtime())
    file = s.get(url, verify=False, headers={'User-Agent': ua.random}, timeout=timeoutDuration)
    time.sleep(1)
    with open(savePath, "wb") as c:
        c.write(file.content)
    download_end_pts = calendar.timegm(time.gmtime())
    logging.info(f"download duration={(download_end_pts - download_start_pts)}")
    s.close()

def requestMecord(downloadDir, curGroupId, mecord_group, start_id):
    param = {
        "group_id": mecord_group,
        "start_id": start_id,
        "size": 30
    }
    max_id = start_id
    s = requests.session()
    s.keep_alive = False
    s.headers.update({'Connection':'close'})
    res = s.get("https://mecord-beta.2tianxin.com/proxymsg/crawler/post_list", params=param, verify=False)
    if res.status_code == 200 and len(res.content) > 0:
        data = json.loads(res.content)
        if data["code"] == 0:
            post = data["body"]["post"]
            for it in post:
                # content_type 
                # 1=图片
                # 2=视频
                # 3=音频
                # 4=文字
                if it["content_type"] == 1 or it["content_type"] == 2:
                    name = it["name"]
                    id = it["id"]
                    idx = 0
                    for it_url in it["content"]:
                        downloadFile(it["content_type"], f"{curGroupId}_{id}_{idx}", it_url, downloadDir)
                        idx += 1
            max_id = data["body"]["max_id"]
            if len(post) > 0: 
                #next page
                max_id = requestMecord(downloadDir, curGroupId, mecord_group, max_id)
    return max_id

def download(url, curGroupId, downloadDir):
    urldata = urlparser.urlparse(url)
    mecord_groups = urldata.hostname.split(",")
    groupCacheConfig = groupConfig()
    for g in mecord_groups:
        s = requests.session()
        s.headers.update({'Connection':'close'})
        start_id = 0
        if g in groupCacheConfig:
            start_id = groupCacheConfig[g]
        new_start_id = requestMecord(downloadDir, curGroupId, g, start_id)
        groupCacheConfig[g] = new_start_id
    saveGroupConfig(groupCacheConfig)
