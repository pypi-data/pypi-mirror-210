import sys
import os
import yt_dlp
import json
import time
import requests
import calendar
import logging
import random
import uuid
import yt_dlp
import urllib3
import datetime
from PIL import Image
from urllib.parse import *
from ftplib import FTP
from urlparser import urlparser
from fake_useragent import UserAgent
from mecord_crawler import utils
from mecord_crawler import template_utils
from mecord_crawler import aaaapp_crawler

def downloadDir(curGroupId):
    this_dir = os.path.dirname(os.path.abspath(__file__))
    s = os.path.join(this_dir, ".download", str(curGroupId))
    if os.path.exists(s) == False:
        os.makedirs(s)
    return s

firstMediaCover = ""
groupCacheConfig = {}
filename = "mecord_group_crawler_config.txt"
local_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)
def ftpClient():
    ftp = FTP('192.168.3.220', 'xinyu100', 'xinyu100.com')
    if ftp == None:
        raise Exception("no ftp!")
    return ftp

def groupConfig():
    ftp = ftpClient()
    ftp.cwd("mecord/")
    file_list = ftp.nlst()
    if filename in file_list:
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

def pathWithSize(path, w, h):
    if w > 0 and h > 0:
        if "?" in path:
            return f"{path}&width={w}&height={h}"
        else:
            return urljoin(path, f"?width={w}&height={h}")
    return path

def download(media_type, post_text, media_resource_url, audio_resource_url, curTaskId):
    name = ''.join(str(uuid.uuid4()).split('-'))
    timeoutDuration = 3600
    ext = ".mp4"
    if media_type == "image":
        timeoutDuration = 60
        ext = ".jpg"
    elif media_type == "audio":
        timeoutDuration = 300
        ext = ".mp3"
    savePath = os.path.join(downloadDir(curTaskId), f"{name}{ext}")
    if os.path.exists(savePath):
        os.remove(savePath)
    # download
    logging.info(f"download: {media_resource_url}, {audio_resource_url}")
    s = requests.session()
    s.keep_alive = False
    ua = UserAgent()
    file = s.get(media_resource_url, verify=False, headers={'User-Agent': ua.random}, timeout=timeoutDuration)
    with open(savePath, "wb") as c:
        c.write(file.content)
    # merge audio & video
    if len(audio_resource_url) > 0:
        audioPath = os.path.join(downloadDir(curTaskId), f"{name}.mp3")
        file1 = s.get(audio_resource_url, timeout=timeoutDuration)
        with open(audioPath, "wb") as c:
            c.write(file1.content)
        tmpPath = os.path.join(downloadDir(curTaskId), f"{name}.mp4.mp4")
        utils.ffmpegProcess(f"-i \"{savePath}\" -i \"{audioPath}\" -vcodec copy -acodec copy -y \"{tmpPath}\"")
        if os.path.exists(tmpPath):
            os.remove(savePath)
            os.rename(tmpPath, savePath)
            os.remove(audioPath)
        logging.info(f"merge => {file}, {file1}")

    # cover & sourceFile
    coverPath = ""
    if media_type == "video":
        utils.processMoov(savePath)
        tttempPath = f"{savePath}.jpg"
        utils.ffmpegProcess(f"-i \"{savePath}\" -ss 00:00:00.02 -frames:v 1 -y \"{tttempPath}\"")
        if os.path.exists(tttempPath):
            coverPath = tttempPath
    elif media_type == "image":
        coverPath = savePath
    savePathW, savePathH = localFileWithSize(media_type, savePath)
    url = utils.uploadWithDir(f"g/{curTaskId}", savePath)
    if url == None:
        logging.info(f"oss url not found")
        return
    ossurl = pathWithSize(url, savePathW, savePathH)
    cover_url = ""
    if os.path.exists(coverPath) and media_type == "video":
        coverW, coverH = localFileWithSize("image", coverPath)
        coverossurl = utils.uploadWithDir(f"g/{curTaskId}", coverPath)
        cover_url = pathWithSize(coverossurl, coverW, coverH)
        os.remove(coverPath)
    elif os.path.exists(coverPath) and media_type == "image":
        cover_url = ossurl
    s.close()
    os.remove(savePath)
    return ossurl, cover_url
    
def updateUser(task_id, group_id, url, userConfig):
    global firstMediaCover
    if group_id <= 0:
        #create
        randomName = ''.join(str(uuid.uuid4()).split('-'))
        coverPathTmp = os.path.join(downloadDir(task_id), f"cover_{randomName}.jpg")
        s = requests.session()
        s.keep_alive = False
        coverOss = ""
        if userConfig["avatar"] != None:
            js_res = s.get(userConfig["avatar"])
            with open(coverPathTmp, "wb") as c:
                c.write(js_res.content)
            coverOss = utils.uploadWithDir("cover", coverPathTmp)
            os.remove(coverPathTmp)
        elif len(firstMediaCover)>0:
            coverOss = firstMediaCover
        param = {
            "name": userConfig["username"],
            "icon": coverOss,
            "description": ""
        }
        s1 = requests.session()
        s1.keep_alive = False
        res = s1.post(f"https://api.mecordai.com/proxymsg/crawler/create_group", json.dumps(param), verify=False)
        if res.status_code == 200:
            result = json.loads(res.content)
            group_id = result["body"]["info"]["id"]
        else:
            raise Exception(f"create_group fail!, msg={res}, param={param}")
        if group_id > 0:
            param1 = {
                "id": int(task_id),
                "group_id": group_id,
                "group_name": userConfig["username"]
            }
            s2 = requests.session()
            s2.keep_alive = False
            res = s2.post(f"https://alpha.2tianxin.com/common/admin/mecord/update_auto_crawler", json.dumps(param1), verify=False)
            if res.status_code != 200:
                logging.info("update_auto_crawler fail!")
        else:
            raise Exception("group_id is empty")
    return group_id

def mediatype2mecord(media_type):
    if media_type == "image":
        return 1
    elif media_type == "audio":
        return 3
    elif media_type == "video":
        return 2
    return 4
    
def processPosts(taskid, group_id):
    global groupCacheConfig
    if taskid not in groupCacheConfig:
        groupCacheConfig[taskid] = {}

    post_list = []
    for k in groupCacheConfig[taskid]:
        if isinstance(groupCacheConfig[taskid][k], (dict)):
            uuid = groupCacheConfig[taskid][k]
            uuid["group_id"] = group_id
            if uuid["post"][0]["content_type"] == mediatype2mecord("image"):
                if len(uuid["post"]) > 2:#large than 2 pics use template
                    needTemplate = (random.randint(0,5) == 2)
                    imgTemplate = template_utils.imageTemplate(len(uuid["post"]))
                    if needTemplate and len(imgTemplate) > 0:
                        uuid["post"][0]["info"][0] += f"<tid:{imgTemplate}>"
                    # else:
                    #     uuid["info"][0] += "<tid:0>"
                    #     image_gallery["post"].append(uuid)
            else:
                needTemplate = (random.randint(0,5) == 2)
                videoTemplate = template_utils.videoTemplate(1)
                if needTemplate and len(videoTemplate) > 0:
                    uuid["post"][0]["info"][0] += f"<tid:{videoTemplate}>"
                # else:
                #     uuid["info"][0] += "<tid:0>"
                # normal_gallery["post"].append(uuid)
            post_list.append(uuid)
        groupCacheConfig[taskid][k] = ""

    if len(post_list) == 0:
        #ignore post
        return
    param = { "param": post_list } 
    logging.info(f"send post to mecord: {param}")
    s = requests.session()
    s.keep_alive = False
    s.headers.update({'Connection':'close'})
    res = s.post("https://api.mecordai.com/proxymsg/crawler/create_post_batch", json.dumps(param), verify=False)
    if res.status_code == 200 and len(res.content) > 0:
        logging.info(f"send post success, param={param}")
    else:
        logging.info(f"send post fail, res = {res}, param={param}")
        
def downloadPosts(task_id, uuid, data):
    global groupCacheConfig
    if task_id not in groupCacheConfig:
        groupCacheConfig[task_id] = {}
    if uuid in groupCacheConfig[task_id]:
        return
        
    post_text = data["text"]
    medias = data["medias"]
    groupCacheConfig[task_id][uuid] = {
        "gallery_name": post_text, #utils.randomGellaryText()
        "group_id":0,
        "post":[]
    }
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
            mecordType = mediatype2mecord(media_type)
            ossurl, cover_url = download(media_type, post_text, media_resource_url, audio_resource_url, task_id)
            global firstMediaCover
            if len(firstMediaCover) <= 0:
                firstMediaCover = cover_url
            groupCacheConfig[task_id][uuid]["post"].append({
                "widget_id": 107,
                "content": [ ossurl ],
                "info": [post_text], #"<tid:0>"表示视频直接发
                "content_type": mecordType,
                "cover_url": cover_url,
                "title": post_text,
                "generate_params": "",
            })
            time.sleep(1)
        except Exception as e:
            print("====================== download+process+upload error! ======================")
            print(e)
            print("======================                                ======================")
            time.sleep(10)  # maybe Max retries
        idx += 1

def aaaapp(task_id, group_id, url, cursor = "", page = 0):
    if len(url) <= 0:
        return

    param = {
        "userId": "D042DA67F104FCB9D61B23DD14B27410",
        "secretKey": "b6c8524557c67f47b5982304d4e0bb85",
        "url": url,
        "cursor": cursor,
    }
    requestUrl = "https://h.aaaapp.cn/posts"
    logging.info(f"=== request: {requestUrl} param={param}")
    s = requests.session()
    s.keep_alive = False
    res = s.post(requestUrl, params=param, verify=False)
    logging.info(f"=== res: {res.content}")
    if len(res.content) > 0:
        data = json.loads(res.content)
        if data["code"] == 200:
            posts = data["data"]["posts"]
            for it in posts:
                post_id = it["id"]
                downloadPosts(task_id, f"{group_id}_{post_id}", it)

            if page == 0:
                group_id = updateUser(task_id, group_id, url, data["data"]["user"])

            if "has_more" in data["data"] and data["data"]["has_more"] == True:
                next_cursor = ""
                if "next_cursor" in data["data"] and len(data["data"]["next_cursor"]) > 0:
                    if "no" not in data["data"]["next_cursor"]:
                        next_cursor = data["data"]["next_cursor"]
                if len(next_cursor) > 0:
                    aaaapp(task_id, group_id, url, next_cursor, page + 1)
        else:
            print(f"=== error aaaapp, context = {res.content}")
            logging.info(f"=== error aaaapp, context = {res.content}")
            if data["code"] == 300:
                print("=== no money, exit now!")
                logging.info("=== no money, exit now!")
                exit(-1)
    else:
        print(f"=== error aaaapp, context = {res.content}, eixt now!")
        logging.info(f"=== error aaaapp, context = {res.content}, eixt now!")
        exit(-1)
    s.close()

def format_selector(ctx):
    formats = ctx.get('formats')[::-1]
    best_video = next(f for f in formats
                      if f['vcodec'] != 'none' and f['acodec'] != 'none' and f['ext'] == 'mp4' and f['audio_channels'] > 0)
    yield {
        'format_id': f'{best_video["format_id"]}',
        'ext': best_video['ext'],
        'requested_formats': [best_video],
        'protocol': f'{best_video["protocol"]}'
    }
    
def ytdlpdownload(task_id, group_id, url):
    outtmpl = f"{downloadDir(task_id)}\\{group_id}_%(playlist_index)s.%(ext)s"
    binary_dir, binary_file = utils.ffmpegBinary()
    options = {
        'ffmpeg_location': os.path.join(binary_dir, binary_file),
        'ignoreerrors': True,
        'restrictfilenames': True,
        'cachedir': False,
        'sleep_interval': 0,
        'max_sleep_interval': 2,
        'format': format_selector,
        'outtmpl': outtmpl,
        'writedescription': True,
        'writethumbnail':True,
        'writesubtitles':True,
        'writeinfojson':True
    }

    ua = UserAgent()
    yt_dlp.utils.std_headers['User-Agent'] = ua.random #'facebookexternalhit/1.1'
    with yt_dlp.YoutubeDL(options) as ydl:
        ydl.download(url)

    for root,dirs,files in os.walk(downloadDir(task_id)):
        for file in files:
            if file.find(".") <= 0:
                continue
            name = file[0:file.index(".")]
            ext = file[file.index("."):]
            if ext == ".mp4":
                coverPath = ""
                savePath = os.path.join(root,file)
                utils.processMoov(savePath)
                tttempPath = f"{savePath}.jpg"
                utils.ffmpegProcess(f"-i \"{savePath}\" -ss 00:00:00.02 -frames:v 1 -y \"{tttempPath}\"")
                if os.path.exists(tttempPath):
                    coverPath = tttempPath

                savePathW, savePathH = localFileWithSize("video", savePath)
                ossurl = utils.uploadWithDir(f"g/{task_id}", savePath)
                ossurl = pathWithSize(ossurl, savePathW, savePathH)
                cover_url = ""
                if os.path.exists(coverPath):
                    coverW, coverH = localFileWithSize("image", coverPath)
                    coverossurl = utils.uploadWithDir(f"g/{task_id}", coverPath)
                    cover_url = pathWithSize(coverossurl, coverW, coverH)
                    os.remove(coverPath)

                if task_id not in groupCacheConfig:
                    groupCacheConfig[task_id] = {}
                
                post_text = ""
                mp4uuid = ""
                mp4ConfigPath = os.path.join(root, f"{name}.info.json")
                if os.path.exists(mp4ConfigPath):
                    with open(mp4ConfigPath, 'r', encoding='UTF-8') as f:
                        mp4Config = json.load(f)
                    post_text = mp4Config["title"]
                    mp4uuid = mp4Config["id"]
                if mp4uuid in groupCacheConfig[task_id]:
                    continue
                groupCacheConfig[task_id][mp4uuid] = [{
                    "widget_id": 107,
                    "content": [ ossurl ],
                    "info": [post_text], #"<tid:0>"表示视频直接发
                    "content_type": 2,
                    "cover_url": cover_url,
                    "title": post_text,
                    "generate_params": "",
                }]
                os.remove(savePath)
        if root != files:
            break
    # if page == 0:
    #     group_id = updateUser(task_id, group_id, url, data["data"]["user"])

white_list = ["youtube.com"]
def useYtdlp(url):
    # for it in white_list:
    #     if it in url:
    #         return True
    return False

def runtask():
    global groupCacheConfig

    s = requests.session()
    s.keep_alive = False
    res = s.get(
        f"https://alpha.2tianxin.com/common/admin/mecord/get_auto_crawler?t={random.randint(100, 99999999)}",
        verify=False)
    if len(res.content) > 0:
        dataList = json.loads(res.content)
        for data in dataList:
            taskid = 6#str(data["id"])
            link_url = "https://www.tiktok.com/@menteinfalivel?lang=zh-Hans" #data["link_url"]
            group_id = 0
            if "group_id" in data:
                group_id = data["group_id"]
            group_id = 100138
            try:
                logging.info(f"================ begin group-crawler {taskid}:{group_id} ===================")
                start_pts = calendar.timegm(time.gmtime())
                groupCacheConfig = groupConfig()
                if useYtdlp(link_url):
                    ytdlpdownload(taskid, group_id, link_url)
                else:
                    aaaapp(taskid, group_id, link_url)
                processPosts(taskid, group_id)
                saveGroupConfig(groupCacheConfig)
                current_pts = calendar.timegm(time.gmtime())
                logging.info(
                    f"================ finish group-crawler {taskid}:{group_id} duration:{current_pts - start_pts} ==============")
            except Exception as e:
                logging.error("====================== uncatch Exception ======================")
                logging.error(e)
                logging.error("======================      end      ======================")
        logging.info(f"================ finish group-crawler all ===================")


# urllib3.disable_warnings()
# logFilePath = f"{os.path.dirname(os.path.abspath(__file__))}/log.log"
# logging.basicConfig(filename=logFilePath, 
#                     format='%(asctime)s %(levelname)s %(message)s',
#                     datefmt='%a, %d %b %Y %H:%M:%S',
#                     level=logging.INFO)
# runtask()