import sys
import os
import subprocess
import json
import shutil
import zipfile
from template_generator import template
from template_generator import binary

def updateRes(rootDir):
    for root,dirs,files in os.walk(rootDir):
        for file in files:
            if file.find(".") <= 0:
                continue
            name = file[0:file.index(".")]
            ext = file[file.index("."):]
            if ext == ".zip.py" and os.path.exists(os.path.join(root, name)) == False:
                for dir in dirs:
                    shutil.rmtree(os.path.join(root, dir))
                with zipfile.ZipFile(os.path.join(root, file), "r") as zipf:
                    zipf.extractall(os.path.join(root, name))
                return
        if root != files:
            break

def test(searchPath):
    rootDir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test")
    updateRes(rootDir)
    config = {
        "input":[
            os.path.join(rootDir, "res", "1.png"),
            os.path.join(rootDir, "res", "2.png"),
            os.path.join(rootDir, "res", "3.png"),
            os.path.join(rootDir, "res", "4.png"),
            ],
        "template":os.path.join(rootDir, "res", "tp"),
        "params":{},
        "output":os.path.join(rootDir, "res", "out.mp4")
        }
    with open(os.path.join(rootDir, "res", "param.config"), 'w') as f:
        json.dump(config, f)

    command = f'template --input {os.path.join(rootDir, "res", "param.config")}'
    print(f"test template command => {command}")
    cmd = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    while cmd.poll() is None:
        print(cmd.stdout.readline().rstrip().decode('utf-8'))
