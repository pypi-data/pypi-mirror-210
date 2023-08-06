import datetime
import json
import urllib.parse
import time

from lxml import etree
import requests
import json
import os
from mecord_crawler import utils
import logging
import urllib3
import datetime
import shutil
import random
from urllib.parse import *
from PIL import Image
from fake_useragent import UserAgent
import uuid
import calendar
from lxml import etree

rootDir = ""
curGroupId = 0
allCount = 0
successCount = 0
notifyServer = True

def notifyMessage(success, msg):
    try:
        param = {
            "task_id": curGroupId,
            "finish_desc": msg
        }
        s = requests.session()
        s.keep_alive = False
        res = s.post(f"https://alpha.2tianxin.com/common/admin/mecord/update_task_finish", json.dumps(param), verify=False)
        resContext = res.content.decode(encoding="utf8", errors="ignore")
        logging.info(f"notifyMessage res:{resContext}")
        s.close()
    except Exception as e:
        logging.info(f"notifyMessage exception :{e}")

def publish(media_type, post_text, ossurl, cover_url):
    type = 0
    if media_type == "video":
        type = 2
    elif media_type == "image":
        type = 1
    elif media_type == "audio":
        type = 3
    param = {
        "task_id": curGroupId,
        "content": ossurl,
        "content_type": type,
        "info": post_text,
        "cover_url": cover_url
    }
    s = requests.session()
    s.keep_alive = False
    res = s.post(f"https://alpha.2tianxin.com/common/admin/mecord/add_crawler_post", json.dumps(param), verify=False)
    resContext = res.content.decode(encoding="utf8", errors="ignore")
    logging.info(f"publish success {successCount}/{allCount}")
    print(f"publish success {successCount}/{allCount}")
    s.close()


def ossPathWithSize(path):
    w = 0
    h = 0
    if "http" in path:
        w, h = utils.getOssImageSize(path)

    if w > 0 and h > 0:
        if "?" in path:
            return f"{path}&width={w}&height={h}"
        else:
            return urljoin(path, f"?width={w}&height={h}")
    return path


def pathWithSize(path, w, h):
    if w > 0 and h > 0:
        if "?" in path:
            return f"{path}&width={w}&height={h}"
        else:
            return urljoin(path, f"?width={w}&height={h}")
    return path


def localFileWithSize(type, path):
    width = 0
    height = 0
    if type == "image":
        img = Image.open(path)
        imgSize = img.size
        width = img.width
        height = img.height
    elif type == "video":
        w, h, bitrate, fps = utils.videoInfo(path)
        width = w
        height = h

    return int(width), int(height)


def download(oldName, media_type, post_text, media_resource_url, audio_resource_url):
    name = ''.join(str(uuid.uuid4()).split('-'))
    timeoutDuration = 3600
    ext = ".mp4"
    if media_type == "image":
        timeoutDuration = 60
        ext = ".jpg"
    elif media_type == "audio":
        timeoutDuration = 300
        ext = ".mp3"
    savePath = os.path.join(rootDir, f"{name}{ext}")
    if os.path.exists(savePath):
        os.remove(savePath)
    # download
    logging.info(f"download: {media_resource_url}, {audio_resource_url}")
    s = requests.session()
    s.keep_alive = False
    ua = UserAgent()
    download_start_pts = calendar.timegm(time.gmtime())
    file = s.get(media_resource_url, verify=False, headers={'User-Agent': ua.random}, timeout=timeoutDuration)
    with open(savePath, "wb") as c:
        c.write(file.content)
    download_end_pts = calendar.timegm(time.gmtime())
    logging.info(f"download duration={(download_end_pts - download_start_pts)}")
    # merge audio & video
    if len(audio_resource_url) > 0:
        audioPath = os.path.join(rootDir, f"{name}.mp3")
        file1 = s.get(audio_resource_url, timeout=timeoutDuration)
        with open(audioPath, "wb") as c:
            c.write(file1.content)
        tmpPath = os.path.join(rootDir, f"{name}.mp4.mp4")
        utils.ffmpegProcess(f"-i '{savePath}' -i '{audioPath}' -vcodec copy -acodec copy -y '{tmpPath}'")
        if os.path.exists(tmpPath):
            os.remove(savePath)
            os.rename(tmpPath, savePath)
            os.remove(audioPath)
        logging.info(f"merge => {file}, {file1}")

    # upload
    # if isPublishOSS():
    #     # cover
    #     coverPath = ""
    #     if media_type == "video":
    #         utils.processMoov(savePath)
    #         tttempPath = f"{savePath}.jpg"
    #         utils.ffmpegProcess(f"-i {savePath}  -ss 00:00:00.02 -frames:v 1 -y {tttempPath}")
    #         if os.path.exists(tttempPath):
    #             coverPath = tttempPath
    #     elif media_type == "image":
    #         # tttempPath = f"{savePath}.jpg"
    #         # shutil.copyfile(savePath, tttempPath)
    #         coverPath = savePath
    #     savePathW, savePathH = localFileWithSize(media_type, savePath)
    #     url = utils.upload(savePath, curGroupId)
    #     if url == None:
    #         logging.info(f"oss url not found")
    #         return
    #     ossurl = pathWithSize(url, savePathW, savePathH)
    #     cover_url = ""
    #     if os.path.exists(coverPath) and media_type == "video":
    #         coverW, coverH = localFileWithSize("image", coverPath)
    #         coverossurl = utils.upload(coverPath, curGroupId)
    #         cover_url = pathWithSize(coverossurl, coverW, coverH)
    #         os.remove(coverPath)
    #     elif os.path.exists(coverPath) and media_type == "image":
    #         cover_url = ossurl
    # else:
    start_pts = calendar.timegm(time.gmtime())
    ftpList = utils.ftpUpload(savePath, curGroupId)
    end_pts = calendar.timegm(time.gmtime())
    logging.info(f"upload duration={(end_pts - start_pts)}")
    cover_url = ""
    ossurl = ftpList[0]

    # publish
    logging.info(f"upload success, url = {ossurl}, cover = {cover_url}")
    s.close()
    os.remove(savePath)
    if notifyServer:
        publish(media_type, post_text, ossurl, cover_url)


def processPosts(uuid, data):
    global allCount
    global successCount

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
        try:
            allCount += 1
            download(f"{uuid}_{idx}", media_type, post_text, media_resource_url, audio_resource_url)
            successCount += 1
            time.sleep(1)
        except Exception as e:
            print("====================== download+process+upload error! ======================")
            print(e)
            print("======================                                ======================")
            time.sleep(10)  # maybe Max retries
        idx += 1


def aaaapp(multiMedia, url, cursor, page):
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
    s.keep_alive = False
    res = s.post(requestUrl, params=param, verify=False)
    logging.info(f"=== res: {res.content}")
    if len(res.content) > 0:
        data = json.loads(res.content)
        if data["code"] == 200:
            idx = 0
            if multiMedia == False:
                processPosts(f"{curGroupId}_{page}_{idx}", data["data"])
                if allCount > 1000:
                    print("stop mission with out of cnt=1000")
                    return
            else:
                posts = data["data"]["posts"]
                for it in posts:
                    processPosts(f"{curGroupId}_{page}_{idx}", it)
                    if allCount > 1000:
                        print("stop mission with out of cnt=1000")
                        return
                    idx += 1
            if "has_more" in data["data"] and data["data"]["has_more"] == True:
                next_cursor = ""
                if "next_cursor" in data["data"] and len(data["data"]["next_cursor"]) > 0:
                    if "no" not in data["data"]["next_cursor"]:
                        next_cursor = data["data"]["next_cursor"]
                if len(next_cursor) > 0:
                    aaaapp(multiMedia, url, next_cursor, page + 1)
        else:
            if notifyServer:
                notifyMessage(False, data["msg"])
            print(f"=== error aaaapp, context = {res.content}")
            logging.info(f"=== error aaaapp, context = {res.content}")
            if data["code"] == 300:
                print("=== no money, exit now!")
                logging.info("=== no money, exit now!")
                exit(-1)
    else:
        print("=== error aaaapp, context = {res.content}, eixt now!")
        logging.info("=== error aaaapp, context = {res.content}, eixt now!")
        if notifyServer:
            notifyMessage(False, "无法抓取")
        exit(-1)
    s.close()

def do_aaaapp_crawler():
    global allCount
    global successCount
    global notifyServer
    
    s = requests.session()
    s.keep_alive = False
    res = s.get(f"https://alpha.2tianxin.com/common/admin/mecord/get_task?t={random.randint(100, 99999999)}",
                verify=False)
    s.close()
    if len(res.content) > 0:
        data = json.loads(res.content)
        curGroupId = data["id"]
        allCount = 0
        successCount = 0
        notifyServer = True
        start_pts = calendar.timegm(time.gmtime())
        logging.info(f"================ begin {curGroupId} ===================")
        logging.info(f"========== GetTask: {res.content}")
        print(f"=== begin {curGroupId}")
        link_url_list = data["link_url_list"]
        multiMedia = False
        if "is_set" in data:
            multiMedia = data["is_set"]
        for s in link_url_list:
            right_s = s.replace("\n", "").replace(";", "").replace(",", "").strip()
            aaaapp(multiMedia, right_s, "", 0)
            if allCount > 1000:
                print("stop mission with out of cnt=1000")
                break
        notifyMessage(True, "成功")
        current_pts = calendar.timegm(time.gmtime())
        print(f"complate => {curGroupId} rst={successCount}/{allCount} duration={(current_pts - start_pts)}")
        logging.info(f"================ end {curGroupId} ===================")

