import sys
import os
import yt_dlp
import json
from fake_useragent import UserAgent
from ttauto_crawler import utils

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
    
def download(url, curGroupId, downloadDir, isMulti):
    outtmpl = f"{downloadDir}\\{curGroupId}.%(ext)s"
    if isMulti:
        outtmpl = f"{downloadDir}\\{curGroupId}_%(playlist_index)s.%(ext)s"

    options = {
        'ffmpeg_location': utils.ffmpegBinary(""),
        'ignoreerrors': True,
        'restrictfilenames': True,
        'cachedir': False,
        'sleep_interval': 0,
        'max_sleep_interval': 2,
        'format': format_selector,
        'outtmpl': outtmpl,
    }

    ua = UserAgent()
    yt_dlp.utils.std_headers['User-Agent'] = ua.random #'facebookexternalhit/1.1'
    with yt_dlp.YoutubeDL(options) as ydl:
        ydl.download(url)
