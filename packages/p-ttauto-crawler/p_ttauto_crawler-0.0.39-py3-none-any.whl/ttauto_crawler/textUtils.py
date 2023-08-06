import sys
import os
import time
import requests
import zipfile
import json
from ttauto_crawler import utils
from ttauto_crawler import binary
import shutil
import subprocess
import random
from urllib.parse import *
from PIL import Image
from fake_useragent import UserAgent
import mutagen

def allTexts(searchName):
    txt = []
    binDir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bin")
    for root,dirs,files in os.walk(binDir):
        for file in files:
            if file.find(".") <= 0:
                continue
            name = file[0:file.index(".")]
            ext = file[file.index("."):]
            if ext == ".txt.py" and searchName == name:
                with open(os.path.join(root, file), "r", encoding="UTF-8") as f:
                    txt = f.readlines()
        if root != files:
            break
    return txt

def randomText():
    txt = allTexts("randomText")
    txt_len = len(txt)
    rd_idx = random.randint(0, txt_len-1)
    return txt[rd_idx]

def randomMultiText():
    txt = allTexts("multiRandomText")
    txt_len = len(txt)
    rd_idx = random.randint(0, txt_len-1)
    return txt[rd_idx]