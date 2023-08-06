import sys
import os
import subprocess
import json
import random
from pathlib import Path
import shutil
import zipfile
import stat
import logging

from template_generator import binary

def getCommandResult(cmd):
    try:
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        if result.returncode == 0:
            return result.stdout.decode(encoding="utf8", errors="ignore").replace("\n","").strip()
        else:
            return ""
    except subprocess.CalledProcessError as e:
        logging.info(f"getCommandResult fail {e}")
        return ""

def getBinary(searchPath):
    binaryPath = ""
    if sys.platform == "win32":
        binaryPath = os.path.join(os.path.join(binary.skymediaPath(searchPath), "win"), "TemplateProcess.exe")
    elif sys.platform == "linux":
        binaryPath = os.path.join(binary.skymediaPath(searchPath), "linux", "TemplateProcess.out")
        if os.path.exists(binaryPath):
            cmd = subprocess.Popen(f"chmod 755 {binaryPath}", stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
            while cmd.poll() is None:
                print(cmd.stdout.readline().rstrip().decode('utf-8'))
        #check env
        if os.path.exists("/usr/lib/libskycore.so") == False:
            print(f"=== begin setup env")
            setupShell = os.path.join(binary.skymediaPath(searchPath), "linux", "setup.sh")
            if os.path.exists(setupShell):
                print(f"=== sh {setupShell}")
                getCommandResult(f"sh {setupShell}")
            if os.path.exists("/usr/lib/libskycore.so") == False:
                raise Exception("linux environment error")
        if len(getCommandResult("echo $XDG_SESSION_TYPE")) <= 0 and len(getCommandResult("echo $DISPLAY")) <= 0:
            #no x11 or wayland , check Xvfb
            displayShell = os.path.join(binary.skymediaPath(searchPath), "linux", "display.sh")
            if os.path.exists(displayShell):
                print(f"=== sh {displayShell}")
                cmd1 = subprocess.Popen(f"sh {displayShell}", stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
                while cmd1.poll() is None:
                    print(cmd1.stdout.readline().rstrip().decode('utf-8'))

            
    if os.path.exists(binaryPath):
        return os.path.dirname(binaryPath), os.path.basename(binaryPath)
    else:
        return "", ""
    
def resetTemplate(data, searchPath):
    template_path = data["template"]
    if os.path.exists(template_path):
        return
    randomEffectPath = binary.randomEffectPath(searchPath)
    template_path = os.path.join(randomEffectPath, template_path)
    if os.path.exists(template_path):
        data["template"] = template_path
        return
    raise Exception(f"template {template_path} not found")
    
def isAdaptiveSize(data):
    template_path = data["template"]
    templateName = os.path.basename(template_path)
    if "template" in templateName or templateName == "AIGC_1":
        return True
    return False

def maybeMesa():
    if sys.platform == "linux":
        if len(getCommandResult("echo $XDG_SESSION_TYPE")) <= 0 and len(getCommandResult("echo $DISPLAY")) <= 0:
            #no (x11 or wayland) and (xvfb not found)
            return True
        else:
            return False
    else:
        return False

def maybeSoftWare():
    if sys.platform == "linux":
        if os.path.exists("/usr/lib/x86_64-linux-gnu/libnvcuvid.so") and os.path.exists("/usr/lib/x86_64-linux-gnu/libnvidia-encode.so"):
            return False
        else:
            return True
    else:
        return False

def executeTemplate(data, searchPath, useAdaptiveSize):
    binary_dir, binary_file = getBinary(searchPath)
    if len(binary_dir) <= 0:
        raise Exception("binary not found")

    output_path = ""
    if isinstance(data, (dict)):
        output_path = data["output"]
        resetTemplate(data, searchPath)
        useAdaptiveSize = useAdaptiveSize or isAdaptiveSize(data)
    elif isinstance(data, (list)):
        for it in data:
            output_path = it["output"]
            resetTemplate(it, searchPath)
            useAdaptiveSize = useAdaptiveSize or isAdaptiveSize(it)

    inputArgs = os.path.join(os.path.dirname(os.path.abspath(__file__)), f"{random.randint(100,99999999)}.in")
    if os.path.exists(inputArgs):
        os.remove(inputArgs)
    with open(inputArgs, 'w') as f:
        json.dump(data, f)

    extArgs = ""
    #--adaptiveSize
    if useAdaptiveSize:
        extArgs += "--adaptiveSize true "
    #--fontDir
    fontPath = binary.fontPath(searchPath)
    if os.path.exists(fontPath):
        extArgs += f"--fontDir {fontPath} "
    #--subEffectDir
    subPath = binary.subEffectPath(searchPath)
    if os.path.exists(subPath):
        extArgs += f"--subEffectDir {subPath} "
    #--gpu
    if sys.platform == "linux" and maybeMesa():
        extArgs += f"--call_mesa "
    if sys.platform == "linux" and maybeSoftWare():
        extArgs += f"--call_software "

    command = f'{binary_file} --config {inputArgs} {extArgs}'
    print(f"=== executeTemplate => {command}")
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, cwd=binary_dir)
    if result.returncode == 0:
        os.remove(inputArgs)
        #check one output
        if os.path.exists(output_path) == False:
            logging.info(f"output file not found")
            raise Exception("output file not found")
        print(result.stdout.decode(encoding="utf8", errors="ignore"))
    else:
        os.remove(inputArgs)
        err_msg = result.stderr.decode(encoding="utf8", errors="ignore")
        logging.info(f"executeTemplate err {err_msg}")
        print(err_msg)
        raise Exception(f"template process exception!")
    
    
def generateTemplate(config, output, searchPath):        
    binary_dir, binary_file = getBinary(searchPath)
    if len(binary_dir) <= 0:
        raise Exception("binary not found")
    
    if os.path.exists(config) == False:
        raise Exception("input config not exist")

    if os.path.exists(output) == False:
        os.makedirs(output)

    command = f'{binary_file} --project {config} -y {output}'
    print(f"=== generateTemplate => {command}")
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, cwd=binary_dir)
    if result.returncode != 0:
        err_msg = result.stderr.decode(encoding="utf8", errors="ignore")
        logging.info(f"generateTemplate err {err_msg}")
        print(err_msg)
        raise Exception(f"generate template exception!")