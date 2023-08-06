import subprocess
import os
import sys
import time
import http.client
import json
import logging
import calendar
from pathlib import Path
import shutil
import zipfile
import platform
import requests
import hashlib
import ftplib
import random
from PIL import Image
from io import BytesIO
from template_res import template

cacheConfig = []

def imageTemplate(cnt):
    global cacheConfig

    useList = []
    list = []
    if len(cacheConfig) == 0:
        list = template.listTemplate("")
    else:
        list = cacheConfig
    for it in list:
        if it["videoCount"] == 0 and it["imageCount"] > cnt:
            useList.append(it)
    if len(useList) > 0:
        rd_idx = random.randint(0, len(useList)-1)
        return useList[rd_idx]["name"]
    else:
        return ""

def videoTemplate(cnt):
    global cacheConfig
    
    useList = []
    list = []
    if len(cacheConfig) == 0:
        list = template.listTemplate("")
    else:
        list = cacheConfig
    for it in list:
        if it["videoCount"] == cnt and it["imageCount"] == 0:
            useList.append(it)
    if len(useList) > 0:
        rd_idx = random.randint(0, len(useList)-1)
        return useList[rd_idx]["name"]
    else:
        return ""
