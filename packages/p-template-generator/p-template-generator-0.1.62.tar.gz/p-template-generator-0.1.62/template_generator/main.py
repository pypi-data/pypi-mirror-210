import os
import sys
import argparse
import json
from pathlib import Path
import shutil
import urllib3
import logging
import datetime
import platform

from pkg_resources import parse_version
from template_generator import template
from template_generator import template_test
from template_generator import ffmpeg

parser = argparse.ArgumentParser()
parser.add_argument("--test", type=str, default=None, help="测试")
parser.add_argument("--transcoding", type=str, default=None, help="转码")
parser.add_argument("--input", type=str, default=None, help="输入资源")

def testTemplate():
    searchPath = findSearchPath(3)
    template_test.test(searchPath)

def checkJsonParam(data):
    if "input" not in data or "template" not in data or "params" not in data or "output" not in data:
        raise Exception("json key missing")
    inputFiles = data["input"]
    template_path = data["template"]
    output_path = data["output"]
    params = data["params"]
    if len(template_path) <= 0 or len(output_path) <= 0:
        raise Exception("template | output_path is empty")
    for it in inputFiles:
        if os.path.exists(it) == False:
            raise Exception(f"file {it} not found!")
    
def txt2proj():
    txt = sys.argv[2]
    output = sys.argv[3]

    try:
        searchPath = ""
        if len(sys.argv) > 5 and sys.argv[4] == "--i":
            searchPath = sys.argv[5]

        template.generateTemplate(txt, output, searchPath)
    except Exception as e:
        raise e
    
def findSearchPath(begin):
    idx = begin
    while idx < len(sys.argv):
        if sys.argv[idx] == "--i":
            return sys.argv[idx+1]
        idx+=1
    return ""
    
def configTemplate():
    input = sys.argv[2]

    try:
        if os.path.isfile(input):
            with open(input, 'r') as f:
                data = json.load(f)

        if isinstance(data, (dict)):
            checkJsonParam(data)
        elif isinstance(data, (list)):
            for it in data:
                checkJsonParam(it)
        else:
            raise Exception("input file is not [] or {}")
            
        searchPath = ""
        froceAdaptiveSize = False
        idx = 3
        while idx < len(sys.argv):
            if sys.argv[idx] == "--i":
                searchPath = sys.argv[idx+1]
            if sys.argv[idx] == "--adaptiveSize":
                froceAdaptiveSize = True
            idx+=1
        template.executeTemplate(data, searchPath, froceAdaptiveSize)
    except Exception as e:
        raise e

    
def transcoding():
    file = sys.argv[2]
    if os.path.exists(file) == False:
        raise Exception("transcoding file not exist")
    
    searchPath = findSearchPath(3)

    w,h,bitrate,fps = ffmpeg.videoInfo(file)
    if w <= 0 or h <= 0 or bitrate <= 0 or fps <= 0:
        raise Exception("file is not video")

    niceBitrate = min(bitrate, (w * h) * (fps / 30.0) / (540.0 * 960.0 / 4000))

    tmpPath = f"{file}.mp4"
    args_moov = "-movflags faststart"
    args_h264 = "-c:v libx264 -pix_fmt yuv420p"
    args_bitrate = f"-b:v {niceBitrate}k -bufsize {niceBitrate}k"
    command = f'-i {file} {args_moov} {args_h264} {args_bitrate} -y {tmpPath}'
    if ffmpeg.process(command, searchPath):
        os.remove(file)
        os.rename(tmpPath, file)

def doFfmpeg():
    cmd = sys.argv[2]
    if len(cmd) <= 0:
        raise Exception("please set command")
    
    searchPath = findSearchPath(3)

    if ffmpeg.process(cmd, searchPath):
        print("=== success")
    else:
        print("=== fail")

module_func = {
    "--test": testTemplate,
    "--txt2proj": txt2proj,
    "--input": configTemplate,
    "--transcoding": transcoding,
    "--ffmpeg": doFfmpeg
}

def main():
    if len(sys.argv) < 2:
        return
    
    urllib3.disable_warnings()
    logFilePath = f"{os.path.dirname(os.path.abspath(__file__))}/log.log"
    if os.path.exists(logFilePath) and os.stat(logFilePath).st_size > (1024 * 1024 * 5):  # 5m bak file
        d = datetime.datetime.now().strftime('%Y_%m_%d_%H_%M_%S')
        bakFile = logFilePath.replace(".log", f"_{d}.log")
        shutil.copyfile(logFilePath, bakFile)
        os.remove(logFilePath)
    if parse_version(platform.python_version()) >= parse_version("3.9.0"):
        logging.basicConfig(filename=logFilePath, 
                            format='%(asctime)s %(levelname)s %(message)s',
                            datefmt='%a, %d %b %Y %H:%M:%S',
                            encoding="utf-8",
                            level=logging.INFO) 
    else:
        logging.basicConfig(filename=logFilePath, 
                            format='%(asctime)s %(levelname)s %(message)s',
                            datefmt='%a, %d %b %Y %H:%M:%S',
                            level=logging.INFO)

    
    try:
        cnt = len(sys.argv)
        full_command = "template "
        for i in range(cnt):
            full_command += f" {sys.argv[i]}"
        logging.info(f"\n\n================ begin ===================")
        logging.info(full_command)

        module = sys.argv[1]
        if module in module_func:
            module_func[module]()
            logging.info(f"================ success end ===================")
            sys.exit(0)
        else:
            print("Unknown command:", module)
            logging.info(f"================ fail end with [Unknown command] ===================")
            sys.exit(-1)
    except Exception as e:
        print(f"uncatch Exception:{e}")
        logging.info(e)
        logging.info(f"================ fail end with [uncatch Exception] ===================")
        sys.exit(-1)
        
if __name__ == '__main__':
        main()
