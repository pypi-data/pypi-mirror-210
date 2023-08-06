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
   
def notifyMessage(curGroupId, msg):
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

def downloadImage(media_resource_url, curGroupId):
    name = ''.join(str(uuid.uuid4()).split('-'))
    ext = ".jpg"
    rootDir = os.path.dirname(os.path.abspath(__file__))
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
    file = s.get(media_resource_url, verify=False, headers={'User-Agent': ua.random}, timeout=300)
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
        mecordSession.post(f"https://alpha.2tianxin.com/common/admin/mecord/add_increasing_crawler_post",
                           json.dumps(param), verify=False)

mecordSession = requests.session()
def civitai():
    # https://alpha.2tianxin.com/common/admin/mecord/get_increasing_task
    res = mecordSession.get(
        f"https://alpha.2tianxin.com/common/admin/mecord/get_increasing_task?t={random.randint(100, 99999999)}",
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
                postList = getPostList(modelId, curGroupId, lastCrwalerMaxTime)
                current_pts = calendar.timegm(time.gmtime())
                l = len(postList)
                logging.info(
                    f"================ finnish civitai {curGroupId} duration:{current_pts - start_pts},len(postList):{l} ==============")
            except Exception as e:
                notifyMessage(curGroupId, str(e))
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
            notifyMessage(curGroupId, str(e))
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

