import sys
import os
import time
import requests
import zipfile
import json
from ttauto_crawler import utils
from ttauto_crawler import txt2proj
from ttauto_crawler import downloader
from ttauto_crawler import video_random_cutter
from template_generator import binary as genertor_binary
import logging
import urllib3
import datetime
import shutil
import subprocess
import random
import calendar
from urllib.parse import *

rootDir = ""
curGroupId = 0
allCount = 0
successCount = 0
splitZipCount = 200

def clearDir():
    downloader.clearDir()
    video_random_cutter.clearDir()
    s1 = os.path.join(rootDir, ".out")
    if os.path.exists(s1):
        shutil.rmtree(s1)

def curOutputDir():
    s = os.path.join(rootDir, ".out", str(curGroupId))
    if os.path.exists(s) == False:
        os.makedirs(s)
    return s
    
def notifyMessage(ossurl, count):
    try:
        param = {
            "id": curGroupId,
            "video_path": ossurl,
            "video_num": count
        }
        s = requests.session()
        s.headers.update({'Connection':'close'})
        res = s.post(f"https://beta.2tianxin.com/common/admin/tta/set_task_complete", json.dumps(param), verify=False)
        if res.status_code == 200:
            logging.info(f"notifyMessage success")
        else:
            resContext = res.content.decode(encoding="utf8", errors="ignore")
            logging.info(f"notifyMessage fail! code={res.status_code}, context={resContext}")
            print(f"report error!, postdata = {json.dumps(param)}")
        s.close()
    except Exception as e:
        logging.info(f"notifyMessage exception :{e}")

def secondToDuration(d):
    hour = int(d / 3600)
    sec = float(d % 60)
    min = int((d - sec) % 3600 / 60)
    hour_str = str(hour).rjust(2).replace(" ", "0")
    min_str = str(min).rjust(2).replace(" ", "0")
    sec_str = ""
    if sec >= 10:
        sec_str = str(sec)
    else:
        sec_str = f"0{str(sec)}"
    return f"{hour_str}:{min_str}:{sec_str}"

def processAllImage(data, curDownloadDir, tpname, addRandomText, img2videoCnt):
    src = curDownloadDir
    dst = curOutputDir()
    templateDir = ""
    if len(tpname) > 0:
        templateDir = os.path.join(genertor_binary.randomEffectPath(""), tpname)
    s = []
    for root,dirs,files in os.walk(src):
        for file in files:
            if file.find(".") <= 0:
                continue
            name = file[0:file.index(".")].lower()
            ext = file[file.index("."):].lower()
            if ext in [".jpg", ".png", ".jpeg", ".bmp"]:
                s.append(os.path.join(root, file))
        if root != files:
            break

    idx = 0
    while len(s) > img2videoCnt:
        s1 = []
        allcnt = len(s)
        for i in range(img2videoCnt):
            rd_idx = random.randint(0, allcnt-1)
            tmp_s = s[rd_idx]
            s.remove(tmp_s)
            allcnt -= 1
            s1.append(tmp_s)
        if len(templateDir) > 0:
            data.append({
                    "input":s1,
                    "template": templateDir,
                    "params":{},
                    "output": os.path.join(dst, f"img2video_{idx}.mp4")})
        else:
            gentemplate = txt2proj.imgsToTemplate(s1, addRandomText, False)
            data.append({
                    "input":[],
                    "template": gentemplate,
                    "params":{},
                    "output": os.path.join(dst, f"img2video_{idx}.mp4")})
        idx+=1

def videoToTemplate(data, curDownloadDir, tpname, addRandomText, splitDuration, verticalScreen):
    src = curDownloadDir
    dst = curOutputDir()
    templateDir = ""
    if len(tpname) > 0:
        templateDir = os.path.join(genertor_binary.randomEffectPath(""), tpname)
    for root,dirs,files in os.walk(curDownloadDir):
        for file in files:
            if file.find(".") <= 0:
                continue
            name = file[0:file.index(".")]
            ext = file[file.index("."):]
            if ext == ".mp4":
                w,h,bitrate,fps,video_duration = utils.videoInfo(os.path.join(src, file))
                if w <= 0 or bitrate <= 0:
                    continue
                if verticalScreen == True:
                    h = w * (16.0 / 9.0)
                srcVideo = os.path.join(src, f"{name}{ext}")
                dstVideo = os.path.join(dst, f"{name}_{tpname}{ext}")
                if splitDuration > 0 and video_duration > splitDuration * 1.5:
                    idx = 0
                    while (idx * splitDuration) < video_duration:
                        split_duration = splitDuration
                        if ((idx+1) * splitDuration) > video_duration:
                            split_duration = video_duration - (idx * splitDuration)
                        if split_duration < splitDuration / 2:
                            #ignore too short slice
                            break
                        tmpPath = os.path.join(curDownloadDir, f"{name}_autoremove_{idx}.mp4")
                        dstVideo = os.path.join(dst, f"{name}_{idx}_{tpname}{ext}")
                        if os.path.exists(tmpPath) == False:
                            # -c:v copy -c:a copy  # must be recodec for some undecode bug
                            cmd = f"-ss {secondToDuration(idx * splitDuration)} -i {srcVideo} -t {secondToDuration(split_duration)} -y {tmpPath}"
                            logging.info(f"=============== ffmpeg {cmd}")
                            utils.ffmpegProcess(cmd)
                        if os.path.exists(tmpPath) and os.stat(tmpPath).st_size > 10000: #maybe source video is wrong, check output file is large than 10k
                            realTemplateDir = templateDir
                            if addRandomText and tpname != "template8":
                                if len(templateDir) > 0:
                                    tempDir = txt2proj.newTemplateWithText(templateDir, w, h, split_duration)
                                else:
                                    tempDir = txt2proj.singleVideoToTemplate(tmpPath, True, False, w, h, split_duration)
                                realTemplateDir = tempDir
                            if len(realTemplateDir):
                                data.append({
                                    "input":[tmpPath],
                                    "template": realTemplateDir,
                                    "params":{},
                                    "output": dstVideo})
                            else:
                                shutil.copyfile(tmpPath, dstVideo)
                        idx+=1
                else:
                    realTemplateDir = templateDir
                    if addRandomText:
                        if len(templateDir) > 0:
                            tempDir = txt2proj.newTemplateWithText(templateDir, w, h, video_duration)
                        else:
                            tempDir = txt2proj.singleVideoToTemplate(srcVideo, True, False, w, h, video_duration)
                        realTemplateDir = tempDir
                    if len(realTemplateDir):
                        data.append({
                            "input":[srcVideo],
                            "template": realTemplateDir,
                            "params":{},
                            "output": dstVideo})
                    else:
                        shutil.copyfile(srcVideo, dstVideo)
        if root != files:
            break

def needAdaptiveSize(crawler_template_name, addRandomText, splitDuration, img_to_video, verticalScreen):
    if len(crawler_template_name) > 0 and img_to_video > 0:
        return False
    else:
        return True

def processToVideo(curDownloadDir, crawler_template_name, addRandomText, splitDuration, img_to_video, verticalScreen):
    src = curDownloadDir
    dataFile = os.path.join(src, "params.config")
    data = []
    official_template_list = []
    #videos
    if len(crawler_template_name) > 0:
        for tpname in crawler_template_name:
            templateDir = os.path.join(genertor_binary.randomEffectPath(""), tpname)
            official_template_list.append(templateDir)
            videoToTemplate(data, curDownloadDir, tpname, addRandomText, splitDuration, verticalScreen)
    else:
        videoToTemplate(data, curDownloadDir, "", addRandomText, splitDuration, verticalScreen)
    #imgs
    if img_to_video > 0:
        if len(crawler_template_name) > 0:
            for tpname in crawler_template_name:
                templateDir = os.path.join(genertor_binary.randomEffectPath(""), tpname)
                official_template_list.append(templateDir)
                processAllImage(data, curDownloadDir, tpname, addRandomText, img_to_video)
        else:
            processAllImage(data, curDownloadDir, "", addRandomText, img_to_video)
    #process template
    args = ""
    if needAdaptiveSize(crawler_template_name, addRandomText, splitDuration, img_to_video, verticalScreen):
        args = "--adaptiveSize"
    if len(data) > 0:
        with open(dataFile, 'w') as f:
            json.dump(data, f)
        try:
            print(f"template --input {dataFile} {args}")
            result = subprocess.run(f"template --input {dataFile} {args}", stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
            if result.returncode == 0:
                print("=== process success")
            else:
                print("====================== script error ======================")
                print(result.stdout.decode(encoding="utf8", errors="ignore"))
                print("======================     end      ======================")
        except subprocess.CalledProcessError as e:
            print("====================== process error ======================")
            print(e)
            print("======================      end      ======================")
        for it in data:
            if it["template"] not in official_template_list:
                shutil.rmtree(it["template"])
        os.remove(dataFile)
    
def cacheOutputDir():
    dst = curOutputDir()
    dist1 = os.path.join(os.path.dirname(dst), f"{curGroupId}_out.zip")
    zip1 = zipfile.ZipFile(dist1, "w", zipfile.ZIP_DEFLATED) 
    for rt,dirs,files in os.walk(dst):
        for file in files:
            if str(file).startswith("~$"):
                continue
            filepath = os.path.join(rt, file)
            writepath = os.path.relpath(filepath, dst)
            zip1.write(filepath, writepath)
    zip1.close()
    shutil.copyfile(dist1, f"d://{curGroupId}_out.zip")
    os.remove(dist1)

def process(url, crawler_template_name, addRandomText, splitDuration, img_to_video, video_merge_num, video_merge_second, verticalScreen):
    global successCount
    global allCount
    allCount = 0
    successCount = 0
    ### downlaod
    curDownloadDir, allCount = downloader.download(url, curGroupId, rootDir)
    if video_merge_num > 0 and video_merge_second > 0:
        ### random cutter
        print(f"=== random cutter ")
        curDownloadDir = video_random_cutter.video_cutter(curDownloadDir, curGroupId, video_merge_num, video_merge_second)
    print(f"=== processing video")
    processToVideo(curDownloadDir, crawler_template_name, addRandomText, splitDuration, img_to_video, verticalScreen)
    cacheOutputDir() #cache file to d://
    ### upload + notify
    print(f"=== uploading + notifying ")
    splitCount = 0
    packageIndex = 0
    dist = os.path.join(os.path.dirname(curOutputDir()), f"{curGroupId}_{packageIndex}.zip")
    zip = zipfile.ZipFile(dist, "w", zipfile.ZIP_DEFLATED) 
    for rt,dirs,files in os.walk(curOutputDir()):
        for file in files:
            if str(file).startswith("~$"):
                continue
            filepath = os.path.join(rt, file)
            if os.stat(filepath).st_size < 250000:
                #recheck upload file size , must be large than 250k
                continue
            writepath = os.path.relpath(filepath, curOutputDir())
            zip.write(filepath, writepath)
            splitCount+=1
            successCount+=1
            if splitCount >= splitZipCount and (len(files) - successCount > (splitZipCount / 2)):
                zip.close()
                onePackage_ossurl = utils.ftpUpload(dist)[0]
                print(f"=== sending {packageIndex} package ")
                notifyMessage(onePackage_ossurl, splitCount)
                packageIndex+=1
                splitCount = 0
                dist = os.path.join(os.path.dirname(curOutputDir()), f"{curGroupId}_{packageIndex}.zip")
                zip = zipfile.ZipFile(dist, "w", zipfile.ZIP_DEFLATED)
        if rt != files:
            break
    zip.close()
    if splitCount > 0:
        lastPackage_ossurl = utils.ftpUpload(dist)[0]
        print(f"=== sending last package ")
        notifyMessage(lastPackage_ossurl, splitCount)

def lastTaskFile():
    thisFileDir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(thisFileDir, "last_task.txt")

def removeLastTask():
    file = lastTaskFile()
    if os.path.exists(file):
        os.remove(file)

def getLocalTask():
    file = lastTaskFile()
    data = {}
    if os.path.exists(file):
        with open(file, 'r', encoding='UTF-8') as f:
            data = json.load(f)
    return data

def saveLastTask(data):
    file = lastTaskFile()
    with open(file, 'w') as f:
        json.dump(data, f)

def getTask():
    data = getLocalTask()
    if len(data) == 0:
        s = requests.session()
        s.headers.update({'Connection':'close'})
        res = s.get(f"https://beta.2tianxin.com/common/admin/tta/get_task?t={random.randint(100,99999999)}", verify=False)
        s.close()
        if len(res.content) > 0:
            data = json.loads(res.content)
            saveLastTask(data)
    return data

def autoCrawler(dir):
    global rootDir
    global curGroupId
    
    thisFileDir = os.path.dirname(os.path.abspath(__file__))
    if len(dir) != 0:
        rootDir = dir
    else:
        rootDir = thisFileDir
    while(os.path.exists(os.path.join(thisFileDir, "stop.now")) == False):
        try:
            data = getTask()
            if len(data) > 0 and "id" in data:
                curGroupId = data["id"]
                start_pts = calendar.timegm(time.gmtime())
                logging.info(f"================ begin {curGroupId} ===================")
                logging.info(f"========== GetTask: {data}")
                print(f"=== begin {curGroupId}")
                url = data["url"].replace("\n", "").replace(";", "").replace(",", "").strip()
                template_name_list = data["template_name_list"]
                if template_name_list == None:
                    template_name_list = []
                video_merge_num = int(data["video_merge_num"])
                video_merge_second = int(data["video_merge_second"])
                img_to_video = int(data["img_to_video"])
                split_video = int(data["split_video"])
                add_text = int(data["add_text"])
                verticalScreen = False
                if "VerticalScreen=true" in url:
                    verticalScreen = True
                    url = url.replace("VerticalScreen=true","")

                clearDir()
                process(url, template_name_list, add_text, split_video, img_to_video, video_merge_num, video_merge_second, verticalScreen)

                current_pts = calendar.timegm(time.gmtime())
                print(f"complate => {curGroupId} rst={successCount}/{allCount} duration={(current_pts - start_pts)}")
                logging.info(f"================ end {curGroupId} rst={successCount}/{allCount} duration={(current_pts - start_pts)}===================")
            removeLastTask()
        except Exception as e:
            logging.error("====================== uncatch Exception ======================")
            notifyMessage("", 0)
            logging.error(e)
            logging.error("======================      end      ======================")
        time.sleep(60)
    os.remove(os.path.join(thisFileDir, "stop.now"))
    print(f"stoped !")

# urllib3.disable_warnings()
# logFilePath = f"{os.path.dirname(os.path.abspath(__file__))}/log.log"
# if os.path.exists(logFilePath) and os.stat(logFilePath).st_size > (1024 * 1024 * 5):  # 5m bak file
#     d = datetime.datetime.now().strftime('%Y_%m_%d_%H_%M_%S')
#     bakFile = logFilePath.replace(".log", f"_{d}.log")
#     shutil.copyfile(logFilePath, bakFile)
#     os.remove(logFilePath)
# logging.basicConfig(filename=logFilePath, 
#                     format='%(asctime)s %(levelname)s %(message)s',
#                     datefmt='%a, %d %b %Y %H:%M:%S',
#                     encoding="utf-8",
#                     level=logging.INFO)
# rootDir = os.path.dirname(os.path.abspath(__file__))

# data = {
#     "0":"https://www.instagram.com/cocona_beach/",
# }

# # maxDownloadCount = 2
# splitZipCount = 100
# for k in data:
#     curGroupId = int(k)
#     allCount = 0
#     successCount = 0
#     start_pts = calendar.timegm(time.gmtime())
#     logging.info(f"================ begin {curGroupId} ===================")
#     print(f"=== begin {curGroupId}")
#     url = data[k]
#     crawler_template_name = [ "mecord_cn_1" ] 
#     video_merge_num = 0
#     video_merge_second = 0
#     img_to_video = 5
#     split_video = 0
#     add_text = False
#     verticalScreen = False
#     clearDir()
#     process(url, crawler_template_name, add_text, split_video, img_to_video, video_merge_num, video_merge_second, verticalScreen)
#     current_pts = calendar.timegm(time.gmtime())
#     print(f"complate => {curGroupId} rst={successCount}/{allCount} duration={(current_pts - start_pts)}")
#     logging.info(f"================ end {curGroupId} ===================")


# # print(os.stat("C:\\Users\\123\\AppData\\Local\\Programs\\Python\\Python310\\Lib\\site-packages\\ttauto_crawler\\.download\\1573\\1573_2_11_0_autoremove_1.mp4").st_size)