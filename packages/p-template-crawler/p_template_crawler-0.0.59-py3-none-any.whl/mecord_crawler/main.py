import sys
import os
import time
import urllib.parse

import requests
import json
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
env = ""


def domain():
    if env == "normal":
        return "api.mecordai.com"
    else:
        return "alpha.2tianxin.com"


def isPublishOSS():
    if env == "normal":
        return True
    else:
        return False


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
        res = s.post(f"https://{domain()}/common/admin/mecord/update_task_finish", json.dumps(param), verify=False)
        resContext = res.content.decode(encoding="utf8", errors="ignore")
        logging.info(f"notifyMessage res:{resContext}")
        s.close()
    except Exception as e:
        logging.info(f"notifyMessage exception :{e}")


def notifyMessageV2(curGroupId, msg):
    try:
        param = {
            "task_id": curGroupId,
            "finish_desc": msg
        }
        s = requests.session()
        s.keep_alive = False
        res = s.post(f"https://{domain()}/common/admin/mecord/update_task_finish", json.dumps(param), verify=False)
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
    res = s.post(f"https://{domain()}/common/admin/mecord/add_crawler_post", json.dumps(param), verify=False)
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


def downloadImage(media_resource_url, curGroupId):
    name = ''.join(str(uuid.uuid4()).split('-'))
    ext = ".jpg"
    savePath = os.path.join(rootDir, f"{name}{ext}")
    if os.path.exists(savePath):
        os.remove(savePath)
    # download
    logging.info(f"download: {media_resource_url}")
    s = requests.session()
    s.keep_alive = False
    ua = UserAgent()
    download_start_pts = calendar.timegm(time.gmtime())
    # http下载
    file = s.get(media_resource_url, verify=False, headers={'User-Agent': ua.random}, timeout=120)
    with open(savePath, "wb") as c:
        c.write(file.content)
    download_end_pts = calendar.timegm(time.gmtime())
    logging.info(f"download duration={(download_end_pts - download_start_pts)}")

    start_pts = calendar.timegm(time.gmtime())
    # ftp上传
    ftpList = utils.ftpUpload(savePath, curGroupId)
    end_pts = calendar.timegm(time.gmtime())
    logging.info(f"upload duration={(end_pts - start_pts)}")
    cover_url = ""
    ossurl = ftpList[0]

    logging.info(f"upload success, url = {ossurl}, cover = {cover_url}")
    s.close()
    os.remove(savePath)
    return ossurl


def download(oldName, media_type, post_text, media_resource_url, audio_resource_url):
    name = ''.join(str(uuid.uuid4()).split('-'))
    ext = ".mp4"
    if media_type == "image":
        ext = ".jpg"
    elif media_type == "audio":
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
    file = s.get(media_resource_url, verify=False, headers={'User-Agent': ua.random}, timeout=120)
    with open(savePath, "wb") as c:
        c.write(file.content)
    download_end_pts = calendar.timegm(time.gmtime())
    logging.info(f"download duration={(download_end_pts - download_start_pts)}")
    # merge audio & video
    if len(audio_resource_url) > 0:
        audioPath = os.path.join(rootDir, f"{name}.mp3")
        file1 = s.get(audio_resource_url, timeout=120)
        with open(audioPath, "wb") as c:
            c.write(file1.content)
        tmpPath = os.path.join(rootDir, f"{name}.mp4.mp4")
        utils.ffmpegProcess(f"-i {savePath} -i {audioPath} -vcodec copy -acodec copy -y {tmpPath}")
        if os.path.exists(tmpPath):
            os.remove(savePath)
            os.rename(tmpPath, savePath)
            os.remove(audioPath)
        logging.info(f"merge => {file}, {file1}")

    # upload
    if isPublishOSS():
        # cover
        coverPath = ""
        if media_type == "video":
            utils.processMoov(savePath)
            tttempPath = f"{savePath}.jpg"
            utils.ffmpegProcess(f"-i {savePath}  -ss 00:00:00.02 -frames:v 1 -y {tttempPath}")
            if os.path.exists(tttempPath):
                coverPath = tttempPath
        elif media_type == "image":
            # tttempPath = f"{savePath}.jpg"
            # shutil.copyfile(savePath, tttempPath)
            coverPath = savePath
        savePathW, savePathH = localFileWithSize(media_type, savePath)
        url = utils.upload(savePath, curGroupId)
        if url == None:
            logging.info(f"oss url not found")
            return
        ossurl = pathWithSize(url, savePathW, savePathH)
        cover_url = ""
        if os.path.exists(coverPath) and media_type == "video":
            coverW, coverH = localFileWithSize("image", coverPath)
            coverossurl = utils.upload(coverPath, curGroupId)
            cover_url = pathWithSize(coverossurl, coverW, coverH)
            os.remove(coverPath)
        elif os.path.exists(coverPath) and media_type == "image":
            cover_url = ossurl
    else:
        start_pts = calendar.timegm(time.gmtime())
        if media_type == "video":
            utils.processMoov(savePath)
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


def dosom(gid, multiMedia, url):
    global rootDir
    global curGroupId
    global env
    global allCount
    global successCount
    global notifyServer

    curGroupId = gid
    allCount = 0
    successCount = 0
    notifyServer = False
    env = "test"
    print(f"=== begin {curGroupId}")
    right_s = url.replace("\n", "").replace(";", "").replace(",", "").strip()
    aaaapp(multiMedia, right_s, "", 0)
    if allCount > 1000:
        print("stop mission with out of cnt=1000")
        return
    print(f"complate => {curGroupId} rst={successCount}/{allCount}")


def main():
    global rootDir
    global curGroupId
    global env
    global allCount
    global successCount
    global notifyServer

    urllib3.disable_warnings()
    d = datetime.datetime.now().strftime('%Y_%m_%d_%H_%M_%S')
    thisFileDir = os.path.dirname(os.path.abspath(__file__))
    logging.basicConfig(filename=f"{thisFileDir}/mecord_crawler_{d}.log",
                        format='%(asctime)s %(filename)s [line:%(lineno)d] %(levelname)s %(message)s',
                        datefmt='%a, %d %b %Y %H:%M:%S',
                        encoding="utf-8",
                        level=logging.DEBUG)

    if len(sys.argv) > 1:
        if sys.argv[1] == "test_request":
            curGroupId = 0
            aaaapp(False, "https://www.instagram.com/meowbot_iv/", "", 0)
            return
        elif sys.argv[1] == "test_ffmpeg":
            utils.ffmpegTest()
            return
        elif sys.argv[1] == "normal":
            env = sys.argv[1]
        else:
            print(f"not found {sys.argv[1]}")
            return

    rootDir = thisFileDir
    print(f"current domain is {domain()}")
    while (os.path.exists(os.path.join(thisFileDir, "stop.now")) == False):
        try:
            s = requests.session()
            s.keep_alive = False
            res = s.get(f"https://{domain()}/common/admin/mecord/get_task?t={random.randint(100, 99999999)}",
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

            # C站爬虫
            civitai()

        except Exception as e:
            notifyMessage(False, str(e))
            logging.error("====================== uncatch Exception ======================")
            logging.error(e)
            logging.error("======================      end      ======================")
        time.sleep(10)
    os.remove(os.path.join(thisFileDir, "stop.now"))
    print(f"stoped !")


def addCivitai(curGroupId,imageList):
    reqList = []
    for image in imageList:
        if "image_url" not in image:
            continue
        imageUrl = downloadImage(image['image_url'], curGroupId)
        tagList = []
        if "tag_list" in image:
            tagList = image['tag_list']

        extra = dict()
        if "meta" in image and image["meta"]:
            meta = image["meta"]
            if 'prompt' in meta:
                extra["Prompt TXT2IMG"] = meta["prompt"]
            if 'sampler' in meta:
                extra["Sampler"] = meta['sampler']
            if 'negativePrompt' in meta:
                extra["Negative prompt"] = meta["negativePrompt"]
            if 'Model' in meta:
                extra["Model"] = meta['Model']
            if 'steps' in meta:
                extra['steps'] = str(meta['steps'])
            if 'cfgScale' in meta:
                extra["CFG scale"] = str(meta['cfgScale'])
            if 'seed' in meta:
                extra["Seed"] = str(meta['seed'])

        req = {
            "task_id": curGroupId,
            "content": imageUrl,
            "content_type": 1,
            # "info": post_text,
            'tag_list': tagList,
            "extra": extra,
        }
        reqList.append(req)

    if len(reqList) > 0:
        param = {
            "req_list": reqList,
            "task_id": curGroupId,
        }
        mecordSession.post(f"https://{domain()}/common/admin/mecord/add_increasing_crawler_post",
                           json.dumps(param), verify=False)

mecordSession = requests.session()
def civitai():
    # https://alpha.2tianxin.com/common/admin/mecord/get_increasing_task
    res = mecordSession.get(
        f"https://{domain()}/common/admin/mecord/get_increasing_task?t={random.randint(100, 99999999)}",
        verify=False)
    if len(res.content) > 0:
        dataList = json.loads(res.content)
        for data in dataList:
            curGroupId = data["id"]
            try:
                lastCrwalerMaxTime = data["last_crwaler_max_time"]
                if not lastCrwalerMaxTime:
                    lastCrwalerMaxTime = 0
                logging.info(f"================ begin civitai {curGroupId} ===================")
                start_pts = calendar.timegm(time.gmtime())
                modelId = data["model_id"]
                postList = getPostList(modelId,curGroupId, lastCrwalerMaxTime)
                current_pts = calendar.timegm(time.gmtime())
                l = len(postList)
                logging.info(
                    f"================ finnish civitai {curGroupId} duration:{current_pts - start_pts},len(postList):{l} ==============")
            except Exception as e:
                notifyMessageV2(curGroupId, str(e))
                logging.error("====================== uncatch Exception ======================")
                logging.error(e)
                logging.error("======================      end      ======================")


def getCivitaiCookies():
    # civitaiSession.headers.update({"Connection": "close"})
    res = civitaiSession.get("https://civitai.com", verify=False)
    cookies = dict()
    for cookie in res.cookies:
        # print(cookie.name, ' : ', cookie.value)
        cookies[cookie.name] = cookie.value
        # print()
    return cookies


def getPostList(modelId,curGroupId, lastCrwalerMaxTime):
    postList = []
    nextCursor = None
    while True:
        nextCursor, itemList = pageGetPostList(modelId, nextCursor)
        postList.extend(itemList)
        if not nextCursor:
            break
        time.sleep(1)
    retPostList = []
    for post in postList:
        date_string = post["createdAt"]
        fmt = "%Y-%m-%dT%H:%M:%S.%fZ"
        date = datetime.datetime.strptime(date_string, fmt)
        second = int(date.timestamp())
        if second >= lastCrwalerMaxTime:
            retPostList.append(post)

    for post in retPostList:
        imageList = getPostImageList(modelId, post)
        post["image_list"] = imageList
        try:
            addCivitai(curGroupId, imageList)
        except Exception as e:
            notifyMessageV2(curGroupId, str(e))
            logging.error("====================== uncatch Exception ======================")
            logging.error(e)
            logging.error("======================      end      ======================")
    return retPostList


civitaiSession = requests.session()
# civitaiSession.keep_alive = False


def civitaiGet(url):
    headers = {
        'authority': 'civitai.com',
        'accept': '*/*',
        'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'content-type': 'application/json',
        # Requests sorts cookies= alphabetically
        # 'cookie': '__Host-next-auth.csrf-token=c24cb43f564bfc8262fa2e64a983cfb6552fddc9188d99d7bef5adff6491a84e%7C568b464ad211ed1b2919435aa49e1d5187310912ad66166cf88142ebb0d61f39; __stripe_mid=33d81019-67b7-4e7e-a489-5eb91bb99ecf8e3367; filters=%7B%22model%22%3A%7B%22sort%22%3A%22Highest%20Rated%22%7D%2C%22post%22%3A%7B%22sort%22%3A%22Most%20Reactions%22%7D%2C%22image%22%3A%7B%22sort%22%3A%22Newest%22%7D%2C%22question%22%3A%7B%22sort%22%3A%22Newest%22%7D%2C%22browsingMode%22%3A%22SFW%22%2C%22period%22%3A%22Day%22%7D; __Secure-next-auth.callback-url=https%3A%2F%2Fcivitai.com%2Fmodels%2Fcreate; __stripe_sid=f76f505a-7ede-4714-9207-9ca90fceb5fbb3b76c',
        'if-modified-since': 'Fri, 07 Apr 2023 09:32:02 GMT',
        'referer': 'https://civitai.com/models/7240/meinamix',
        'sec-ch-ua': '"Google Chrome";v="111", "Not(A:Brand";v="8", "Chromium";v="111"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36',
    }
    cookies = getCivitaiCookies()
    # civitaiSession.headers.update({"Connection": "close"})
    res = civitaiSession.get(url, timeout=30,
                             cookies=cookies, headers=headers,verify=False)
    return res.content


def pageGetPostList(modelId, cursor):
    u = getPostQueryUrl(modelId, cursor)

    content = civitaiGet(u)

    if len(content) > 0:
        data = json.loads(content)
        result = data["result"]
        data = result["data"]
        j = data["json"]
        nextCursor = j["nextCursor"]
        items = j["items"]
        return nextCursor, items
    return None, []


def getPostQueryUrl(modelId, cursor):
    pp = None
    if cursor:
        pp = '''{
                       "period": "Day",
                       "sort": "Newest",
                       "modelId": %d,
                       "limit": 50,
                       "cursor": %d
                   }''' % (modelId, cursor)
        pp = '''{"json":{"period":"Day","sort":"Newest","modelId":%d,"limit":50,"cursor":%d}}''' % (modelId, cursor)
    else:
        pp = '''{"json": {"period": "Day", "sort": "Newest", "modelId": %d, "limit": 50, "cursor": null},
             "meta": {"values": {"cursor": ["undefined"]}}}''' % modelId

    logging.info(f"getPostQueryUrl============>{pp}")
    o = {"input": pp}
    t = urllib.parse.urlencode(o)
    u = "https://civitai.com/api/trpc/image.getImagesAsPostsInfinite?" + t
    return u


def getPostImageUrl(modelId, postId):
    pp = '{"json":{"period":"Day","sort":"Newest","modelId":%d,"postId":%d,"cursor":null},"meta":{"values":{"cursor":["undefined"]}}}' % (
        modelId, postId)
    logging.info(f"getPostImageUrl============>{pp}")
    o = {"input": pp}
    t = urllib.parse.urlencode(o)
    u = "https://civitai.com/api/trpc/image.getInfinite?" + t
    return u


def getVotableTagsUrl(imageId):
    pp = '{"0":{"json":{"id":%d,"type":"image"}},"1":{"json":{"entityId":%d,"entityType":"image","limit":3,"cursor":null},"meta":{"values":{"cursor":["undefined"]}}},"2":{"json":{"entityId":%d,"entityType":"image"}},"3":{"json":{"entityId":%d,"entityType":"image"}},"4":{"json":{"id":%d}}}' % (
        imageId, imageId, imageId, imageId, imageId)
    logging.info(f"getVotableTagsUrl============>{pp}")
    o = {"input": pp, "batch": 1}
    t = urllib.parse.urlencode(o)
    u = 'https://civitai.com/api/trpc/tag.getVotableTags,commentv2.getInfinite,commentv2.getCount,commentv2.getThreadDetails,image.getResources?' + t
    return u


def getPostImageList(modelId, item):
    postId = item["postId"]
    url = getPostImageUrl(modelId, postId)
    content = civitaiGet(url)

    data = json.loads(content)
    result = data["result"]
    data = result["data"]
    j = data["json"]
    items = j["items"]
    for item in items:
        votableTagsUrl = getVotableTagsUrl(item["id"])
        content = civitaiGet(votableTagsUrl)
        data = json.loads(content)
        data = data[0]
        result = data["result"]
        data = result["data"]
        j = data["json"]
        tagList = []
        for it in j:
            tagList.append(it["name"].upper())
        item["tag_list"] = tagList
        item["image_url"] = "https://imagecache.civitai.com/xG1nkqKTMzGDvpLrqFT7WA/%s/width=%d/%s.jpeg" % (
            item["url"], item["width"], item["name"])

    return items


if __name__ == '__main__':
    main()
    # getPostList(14171,187,0)