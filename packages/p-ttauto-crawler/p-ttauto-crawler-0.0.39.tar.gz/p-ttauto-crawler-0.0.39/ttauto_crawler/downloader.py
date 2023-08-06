import sys
import os
import yt_dlp
import json
import time
import requests
import logging
import zipfile
import shutil
from fake_useragent import UserAgent
import calendar
from urlparser import urlparser
from ftplib import FTP
from ttauto_crawler import utils
from ttauto_crawler import ytdlp_downloader
from ttauto_crawler import mecord_downloader

downloadAllCount = 0
maxDownloadCount = 1000
max_retries = 3
rootDir = os.path.dirname(os.path.abspath(__file__))

def clearDir():
    s = os.path.join(rootDir, ".download")
    if os.path.exists(s):
        shutil.rmtree(s)
    s1 = os.path.join(utils.largeDiskPath(), ".download")
    if os.path.exists(s1):
        shutil.rmtree(s1)

def curDownloadDir(curGroupId):
    s = os.path.join(rootDir, ".download", str(curGroupId))
    if os.path.exists(s) == False:
        os.makedirs(s)
    return s

def curFtpDownlaodDir(curGroupId):
    s = os.path.join(utils.largeDiskPath(), ".download", str(curGroupId))
    if os.path.exists(s) == False:
        os.makedirs(s)
    return s

white_list = ["youtube.com"]
def useYtdlp(url):
    for it in white_list:
        if it in url:
            return True
    return False

def downloadFile(curGroupId ,name, media_type, post_text, media_resource_url, audio_resource_url):
    timeoutDuration = 3600
    ext = ".mp4"
    if media_type == "image":
        timeoutDuration = 60
        ext = ".jpg"
    elif media_type == "audio":
        timeoutDuration = 300
        ext = ".mp3"
    savePath = os.path.join(curDownloadDir(curGroupId), f"{name}{ext}")
    if os.path.exists(savePath):
        os.remove(savePath)
    #download
    logging.info(f"download: {media_resource_url}, {audio_resource_url}")
    requests.adapters.DEFAULT_RETRIES = 2
    s = requests.session()
    s.keep_alive = False
    s.headers.update({'Connection':'close'})
    ua = UserAgent()
    download_start_pts = calendar.timegm(time.gmtime())
    file = s.get(media_resource_url, verify=False, headers={'User-Agent': ua.random}, timeout=timeoutDuration)
    time.sleep(1)
    with open(savePath, "wb") as c:
        c.write(file.content)
    download_end_pts = calendar.timegm(time.gmtime())
    logging.info(f"download duration={(download_end_pts - download_start_pts)}")
    #merge audio & video
    if len(audio_resource_url) > 0:
        audioPath = os.path.join(curDownloadDir(curGroupId), f"{name}.mp3")
        file1 = s.get(audio_resource_url)
        with open(audioPath, "wb") as c:
            c.write(file1.content)
        tmpPath = os.path.join(curDownloadDir(curGroupId), f"{name}.mp4.mp4")
        utils.ffmpegProcess(f"-i {savePath} -i {audioPath} -vcodec copy -acodec copy -y {tmpPath}")
        if os.path.exists(tmpPath):
            os.remove(savePath)
            os.rename(tmpPath, savePath)
            os.remove(audioPath)
        logging.info(f"merge => {file}, {file1}")
    s.close()
    
def processPosts(curGroupId, uuid, data):
    global downloadAllCount

    post_text = data["text"]
    medias = data["medias"]
    idx = 0
    for it in medias:
        media_type = it["media_type"]
        media_resource_url = it["resource_url"]
        audio_resource_url = ""
        if "formats" in it:
            formats = it["formats"]
            quelity = 0
            for format in formats:
                if format["quality"] > quelity and format["quality"] <= 1080:
                    quelity = format["quality"]
                    media_resource_url = format["video_url"]
                    audio_resource_url = format["audio_url"]
                    if audio_resource_url == None:
                        audio_resource_url = ""
        try:
            downloadAllCount += 1
            downloadFile(curGroupId, f"{uuid}_{idx}", media_type, post_text, media_resource_url, audio_resource_url)
        except Exception as e:
            print(f"====================== download {media_resource_url} error! ======================")
            print(e)
            print("======================                                ======================")
            time.sleep(10) #maybe Max retries
        idx += 1

def aaaapp(multiMedia, url, cursor, page, curGroupId):
    if len(url) <= 0:
        return
    
    param = {
        "userId": "D042DA67F104FCB9D61B23DD14B27410",
        "secretKey": "b6c8524557c67f47b5982304d4e0bb85",
        "url": url,
        "cursor": cursor,
    }
    requestUrl = "https://h.aaaapp.cn/posts"
    if multiMedia == False:
        requestUrl = "https://h.aaaapp.cn/single_post"
    logging.info(f"=== request: {requestUrl} cursor={cursor}")
    s = requests.session()
    s.headers.update({'Connection':'close'})
    res = s.post(requestUrl, params=param, verify=False)
    with open(os.path.join(curDownloadDir(curGroupId), "config.txt"), mode='a') as configFile:
        configFile.write(f"\n=== request: {requestUrl} cursor={cursor}\n")
        configFile.write(f'\n {res.content} \n')
    if len(res.content) > 0:
        data = json.loads(res.content)
        if data["code"] == 200:
            idx = 0
            if multiMedia == False:
                processPosts(curGroupId, f"{curGroupId}_{page}_{idx}", data["data"])
                if downloadAllCount > maxDownloadCount:
                    print(f"stop mission with out of cnt={maxDownloadCount}")
                    return
            else:
                posts = data["data"]["posts"]
                for it in posts:
                    processPosts(curGroupId, f"{curGroupId}_{page}_{idx}", it)
                    if downloadAllCount > maxDownloadCount:
                        print(f"stop mission with out of cnt={maxDownloadCount}")
                        return
                    idx+=1
            if "has_more" in data["data"] and data["data"]["has_more"] == True:
                next_cursor = ""
                if "next_cursor" in data["data"] and len(str(data["data"]["next_cursor"])) > 0:
                    if "no" not in str(data["data"]["next_cursor"]):
                        next_cursor = str(data["data"]["next_cursor"])
                if len(next_cursor) > 0:
                    aaaapp(multiMedia, url, next_cursor, page+1, curGroupId)
        else:
            print(f"=== error aaaapp, context = {res.content}")
            logging.info(f"=== error aaaapp, context = {res.content}")
            if data["code"] == 300: #cannot request
                print("=== no money, exit now!")
                logging.info("=== no money, exit now!")
                exit(-1)
            if data["code"] == -8: #timeout
                time.sleep(20)
                aaaapp(multiMedia, url, cursor, page, curGroupId)
    else:
        print("=== error aaaapp, context = {res.content}, eixt now!")
        logging.info("=== error aaaapp, context = {res.content}, eixt now!")
        exit(-1)
    s.close()

def ftpdownload(url, curGroupId):
    global downloadAllCount

    if "192.168.3.220" not in url and "192.168.50.113" not in url:
        logging.info(f"no support ftp : {url}")
        raise Exception(f"no support ftp : {url}")
    local_dir = curFtpDownlaodDir(curGroupId)
    urldata = urlparser.urlparse(url)
    ftp = None
    if urldata.hostname == "192.168.3.220":
        ftp = FTP('192.168.3.220', 'xinyu100', 'xinyu100.com')
    else:
        ftp = FTP('192.168.50.113', 'ftpuser', 'ftpuser')
    ftp.cwd(urldata.path[1::])
    file_list = ftp.nlst()
    for file_name in file_list:
        if file_name.endswith('.zip') and not os.path.exists(os.path.join(local_dir, file_name)):
            retry_count = 0
            while retry_count < max_retries:
                try:
                    with open(os.path.join(local_dir, file_name), 'wb') as f:
                        ftp.retrbinary('RETR ' + file_name, f.write)
                    logging.info(f'{file_name} downloaded successfully.')
                    break
                except Exception as e:
                    retry_count += 1
            else:
                logging.info(f'{file_name} download failed after {max_retries} retries.')
                os.remove(os.path.join(local_dir, file_name))
    ftp.quit()

    zip_file_list = os.listdir(local_dir)
    for file_name in file_list:
        if file_name.endswith('.zip'):
            with zipfile.ZipFile(os.path.join(local_dir, file_name), 'r') as zip_ref:
                zip_ref.extractall(os.path.join(local_dir, os.path.splitext(file_name)[0]))
            downloadAllCount += len(os.listdir(os.path.join(local_dir, os.path.splitext(file_name)[0])))
            os.remove(os.path.join(local_dir, file_name))

def cacheDownloadDir(curDownloadDir, curGroupId):
    if len(curDownloadDir) > 0:
        src = curDownloadDir
        dist = os.path.join(os.path.dirname(src), f"{curGroupId}.zip")
        zip = zipfile.ZipFile(dist, "w", zipfile.ZIP_DEFLATED) 
        for rt,dirs,files in os.walk(src):
            for file in files:
                if str(file).startswith("~$"):
                    continue
                if "autoremove" in file:
                    continue
                filepath = os.path.join(rt, file)
                writepath = os.path.relpath(filepath, src)
                zip.write(filepath, writepath)
        zip.close()
        shutil.copyfile(dist, f"d://{curGroupId}.zip")
        os.remove(dist)

def download(url, curGroupId, setDir):
    global downloadAllCount
    global rootDir
    downloadAllCount = 0
    rootDir = setDir
    downloadDir = curDownloadDir(curGroupId)
    retryDownload = max_retries

    while downloadAllCount == 0 and retryDownload != 0:
        if "http" in url or "https" in url:
            print(f"=== http downloading ")
            isMulti = True
            realUrl = url
            if "Single" in url:
                realUrl = url.replace("Single", "")
                isMulti = False
            if useYtdlp(url):
                ytdlp_downloader.download(realUrl, curGroupId, downloadDir, isMulti)
                file_list = os.listdir(downloadDir)
                downloadAllCount = len(file_list)
            else:
                aaaapp(isMulti, realUrl, "", 0, curGroupId)
            cacheDownloadDir(downloadDir, curGroupId)
        elif "mecord://" in url:
            print(f"=== mecord downloading ")
            mecord_downloader.download(url, curGroupId, downloadDir)
            file_list = os.listdir(downloadDir)
            downloadAllCount = len(file_list)
        else:
            print(f"=== ftp downloading ")
            downloadDir = curFtpDownlaodDir(curGroupId)
            ftpdownload(url, curGroupId)
        retryDownload -= 1
        if downloadAllCount == 0:
            time.sleep(20)
    file_list = os.listdir(downloadDir)
    downloadAllCount = len(file_list)
    return downloadDir, downloadAllCount