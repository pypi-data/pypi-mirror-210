import sys
import os
import subprocess
import json
import random
from pathlib import Path
import shutil
import zipfile
import stat
import requests
import platform
import logging

from template_generator import binary

def ffmpegBinary(searchPath):        
    binaryFile = ""
    if sys.platform == "win32":
        binaryFile = os.path.join(binary.ffmpegPath(searchPath), "win", "ffmpeg.exe")
    elif sys.platform == "linux":
        machine = platform.machine().lower()
        if machine == "x86_64" or machine == "amd64":
            machine = "amd64"
        else:
            machine = "arm64"
        binaryFile = os.path.join(binary.ffmpegPath(searchPath), "linux", machine, "ffmpeg")
    elif sys.platform == "darwin":
        binaryFile = os.path.join(binary.ffmpegPath(searchPath), "darwin", "ffmpeg")
    
    if len(binaryFile) > 0 and sys.platform != "win32":
        cmd = subprocess.Popen(f"chmod 755 {binaryFile}", stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        while cmd.poll() is None:
            print(cmd.stdout.readline().rstrip().decode('utf-8'))
    return binaryFile

def videoInfo(file):
    w = 0
    h = 0
    bitrate = 0
    fps = 0

    ffmpeg = ffmpegBinary()
    command = f'{ffmpeg} -i {file}'
    print(f"ffmpegProcess: {command}")
    try:
        result = subprocess.run(command, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE, shell=True)
        str = ""
        if result.returncode == 0:
            str = result.stdout.decode(encoding="utf8", errors="ignore")
        else:
            str = result.stderr.decode(encoding="utf8", errors="ignore")
        if str.find("yuv420p") > 0 and str.find("fps") > 0:
            s1 = str[str.find("yuv420p"):str.find("fps")+3].replace(' ', "")
            s1_split = s1.split(",")
            for s1_it in s1_split:
                s2 = s1_it
                if s2.find("[") > 0:
                    s2 = s2[0:s2.find("[")]
                if s2.find("(") > 0:
                    s2 = s2[0:s2.find("[")]
                if s2.find("x") > 0:
                    sizes = s2.split("x")
                    if len(sizes) > 1:
                        w = sizes[0]
                        h = sizes[1]
                if s2.find("kb/s") > 0:
                    bitrate = s2[0:s2.find("kb/s")]
                if s2.find("fps") > 0:
                    fps = s2[0:s2.find("fps")]
    except subprocess.CalledProcessError as e:
        print("====================== process error ======================")
        print(e)
        print("======================      end      ======================")
    return float(w),float(h),float(bitrate),float(fps)

def process(args, searchPath):
    binary = ffmpegBinary(searchPath)
    command = f'{binary} {args}'
    print(f"ffmpegProcess: {command}")
    try:
        result = subprocess.run(command, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE, shell=True)
        if result.returncode == 0:
            print(result.stdout.decode(encoding="utf8", errors="ignore"))
            return True
        else:
            print("====================== ffmpeg error ======================")
            print(result.stderr.decode(encoding="utf8", errors="ignore"))
            print("======================     end      ======================")
    except subprocess.CalledProcessError as e:
        print("====================== process error ======================")
        print(e)
        print("======================      end      ======================")
    return False