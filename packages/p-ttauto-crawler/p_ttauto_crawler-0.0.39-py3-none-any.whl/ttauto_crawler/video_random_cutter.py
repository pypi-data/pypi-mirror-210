import sys
import os
import moviepy.editor as mp
import random
import math
import shutil
import logging
from ttauto_crawler import utils

def clearDir():
    s2 = os.path.join(utils.largeDiskPath(), ".process")
    if os.path.exists(s2):
        shutil.rmtree(s2)

def curLargeDiskProcessDir(curGroupId):
    s = os.path.join(utils.largeDiskPath(), ".process", str(curGroupId))
    if os.path.exists(s) == False:
        os.makedirs(s)
    return s

def get_crop_box(input_file, target_resolution):
    clip = mp.VideoFileClip(input_file)

    width, height = clip.size

    clip.reader.close()
    clip.audio.reader.close_proc()

    aspect_ratio = width / height

    target_width, target_height = target_resolution
    target_aspect_ratio = target_width / target_height
    

    if target_aspect_ratio > aspect_ratio:

        crop_width = width
        crop_height = int(width / target_aspect_ratio)
        x1 = 0
        y1 = (height - crop_height) / 2
    else:
        crop_width = int(height * target_aspect_ratio)
        crop_height = height
        x1 = (width - crop_width) / 2
        y1 = 0
        
    return x1, y1, crop_width, crop_height

def get_video_offsets(input, interval):
    intervals = []
    video = None
    try:
        video = mp.VideoFileClip(input)
    except Exception as e:
        logging.error(f'file: {input}, caught error:{e}')
        if video and video.reader:
            video.reader.close()
        if video and video.audio:
            video.audio.reader.close_proc()

        return []
    except AttributeError as e:
        logging.error(f'file: {input}, caught attribute error:{e}')
        if video and video.reader:
            video.reader.close()
        if video and video.audio:
            video.audio.reader.close_proc()
        return []
    
    duration = video.duration

    # close video reader
    if video.reader:
        video.reader.close()
    if video.audio:
        video.audio.reader.close_proc()
    
    start_time = math.floor(random.uniform(0, duration) * 10 / 10)
    
    s = start_time
    # intervals.append(s)

    while True:
        s -= interval
        if s < 0:
            break
        intervals.append(s)

    s = start_time

    while True:
        s += interval
        if s > duration:
            break
        intervals.append(s-interval)

    intervals.sort()
    return intervals

def get_resolution_of_video(input): 
    clip = mp.VideoFileClip(input)
    ref_resolution = clip.size
    if clip.reader:
        clip.reader.close()
    if clip.audio:
        clip.audio.reader.close_proc()

    return ref_resolution

def get_duration_of_video(input): 
    clip = mp.VideoFileClip(input)
    duration = clip.duration
    if clip.reader:
        clip.reader.close()
    if clip.audio:
        clip.audio.reader.close_proc()

    return duration

def video_cutter(input_dir, curGroupId, video_merge_num, video_merge_second):
    output_dir = curLargeDiskProcessDir(curGroupId)
    interval_indexs = {}
    intervals = {}
    unavailable_videos = []

    videos = [os.path.join(root, filename) for root, _, files in os.walk(input_dir)
            for filename in files if filename.endswith('.mp4')]
    for v in videos:
        interval = get_video_offsets(v, video_merge_second)
        if len(interval) == 0:
            unavailable_videos.append(v)
        else:
            interval_indexs[v] = 0
            intervals[v] = interval
        print(f'file：{os.path.basename(v)}, path:{v}, interval:{interval}.')

    for v in unavailable_videos:
        videos.remove(v)

    while True:
        # Get list of mp4 videos in input directory
         #[f for f in os.listdir(input_dir) if f.endswith('.mp4')]
        # Stop if there are no more videos in the input directory
        if len(videos) == 0:
            break

        # Choose 3 random videos from the input directory
        chosen_videos = []
        
        # Create empty list to store time intervals of selected clips
        selected_intervals_index = []

        # Loop through each chosen video
        while len(videos) > 0 and len(chosen_videos) < video_merge_num:
            video_file = random.sample(videos, k=1)[0]
            print(f'choose video: {video_file}')

            video = mp.VideoFileClip(video_file)
        
            duration = video.duration

            # close video reader
            if video.reader:
                video.reader.close()
            if video.audio:
                video.audio.reader.close_proc()

            index = interval_indexs[video_file]

            selected_intervals_index.append(index)
            index += 1

            chosen_videos.append(video_file)
            if len(intervals[video_file]) <= index:
                videos.remove(video_file)
            else:
                interval_indexs[video_file] = index
        
        print(f'choose videos:{chosen_videos}')

        # Load the first video to use as a reference for output resolution
        
        ref_resolution = get_resolution_of_video(chosen_videos[0])

        clip_list = []
        video_clips = []
        audio_clips = []
        for i, chosen_file in enumerate(chosen_videos):
            # Load the video file using moviepy
            video = mp.VideoFileClip(chosen_file, audio=True)

            index = selected_intervals_index[i]
            start_time = intervals[chosen_file][index]
            # Get the start and end time of the selected interval
            end_time = start_time + video_merge_second
            
            # Select the clip for the interval and add it to the list
            video_clip = video.subclip(start_time, end_time)
 
            
            # If the resolution of the video is different from the reference video, resize and crop it
            if video.size != ref_resolution:
                
                x, y, width, height = get_crop_box(chosen_file, (ref_resolution[0], ref_resolution[1]))
                print(f'Inconsistent resolution, video resolution is {video.size}, target resolution is {ref_resolution}, cutting area is [{x},{y}, {width}, {height}]')
                video_clip = video_clip.crop(x1=x, y1=y, x2=x+width, y2=y+height)
                video_clip = video_clip.resize(ref_resolution)
                
            video_clips.append(video_clip)
            clip_list.append(video)
            # if video.reader:
            #     video.reader.close()
            # if video.audio:
            #     video.audio.reader.close_proc()

                
        # Check if there are any selected clips
        if len(video_clips) == 0:
            break
        
        # Concatenate the selected clips into a single video
        final_clip = mp.concatenate_videoclips(video_clips)
        
        # Generate a random filename for the output video
        output_filename = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz', k=10)) + '.mp4'
        
        # Save the final clip to the output directory
        final_clip.write_videofile(os.path.join(output_dir, output_filename), codec='libx264', audio_codec="aac")

        #release resource
        for clip in video_clips:
            if clip.reader:
                clip.reader.close()
            if clip.audio:
                clip.audio.reader.close_proc() 
        
        for clip in clip_list:
            if clip.reader:
                clip.reader.close()
            if clip.audio:
                clip.audio.reader.close_proc() 

    return output_dir
