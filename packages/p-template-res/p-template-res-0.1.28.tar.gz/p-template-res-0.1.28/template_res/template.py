import zipfile
import platform
import subprocess
import json
import os
from pathlib import Path
import shutil
import stat
import requests
import hashlib
import mutagen

def getOssResource(rootDir, url, md5, name):
    localFile = os.path.join(rootDir, name)
    localFileIsRemote = False
    if os.path.exists(localFile):
        with open(localFile, 'rb') as fp:
                file_data = fp.read()
        file_md5 = hashlib.md5(file_data).hexdigest()
        if file_md5 == md5:
            localFileIsRemote = True

    if localFileIsRemote == False: #download
        if os.path.exists(localFile):
            os.remove(localFile)
        s = requests.session()
        s.keep_alive = False
        print(f"download {url} ")
        file = s.get(url, verify=False)
        with open(localFile, "wb") as c:
            c.write(file.content)
        s.close()
        fname = name[0:name.index(".")]
        fext = name[name.index("."):]
        unzipDir = os.path.join(rootDir, fname)
        if os.path.exists(unzipDir):
            shutil.rmtree(unzipDir)
        print(f"unzip {url} -> {unzipDir}")
        
        
def updateResources(rootDir):
    getOssResource(rootDir, "http://mecord-m.2tianxin.com/res/template-res_20230517.zip", "9bb0765d04c0bb5c5d10a7c573c503f0", "template_res.zip.py")
    getOssResource(rootDir, "http://mecord-m.2tianxin.com/res/music_20230426.zip", "375b2f1394557f35f132eed417b9fbff", "music.zip.py")
    getOssResource(rootDir, "http://mecord-m.2tianxin.com/res/music-cn_20230426.zip", "205e90cf47eb0587f4ac0cf05d0f30a7", "music-cn.zip.py")

    for root,dirs,files in os.walk(rootDir):
        for file in files:
            if file.find(".") <= 0:
                continue
            name = file[0:file.index(".")]
            ext = file[file.index("."):]
            if ext == ".zip.py" and os.path.exists(os.path.join(root, name)) == False:
                print(f"unzip {os.path.join(root, name)}")
                with zipfile.ZipFile(os.path.join(root, file), "r") as zipf:
                    zipf.extractall(os.path.join(root, name))
        if root != files:
            break
        
def templateDir(rootDir):
    dd = os.path.join(rootDir, "template_res")
    if os.path.exists(dd):
        return dd
    return ""

def musicDir(rootDir):
    dd = os.path.join(rootDir, "music")
    if os.path.exists(dd):
        return dd
    return ""

def savePut(src, dst, name):
    if name in src:
        dst[name] = src[name]

def saveGet(src, name):
    if name in src:
        return src[name]
    return ""

def saveGetI(src, name):
    if name in src:
        return src[name]
    return -1

def inputConfig(data):
    videoCount = 0
    imageCount = 0
    audioCount = 0
    textCount = 0
    list = []
    otherParam = []
    for it in data:
        try:
            if it["type"].lower() == "image":
                imageCount += 1
                list.append({
                    "type": "image",
                    "width": saveGetI(it, "width"),
                    "height": saveGetI(it, "height")
                })
            elif it["type"].lower() == "video":
                videoCount += 1
                list.append({
                    "type": "video",
                    "width": saveGetI(it, "width"),
                    "height": saveGetI(it, "height"),
                    "name": saveGet(it, "name"),
                    "group": saveGet(it, "group")
                })
            elif it["type"].lower() == "audio":
                audioCount += 1
                list.append({
                    "type": "audio",
                    "name": saveGet(it, "name"),
                    "group": saveGet(it, "group")
                })
            elif it["type"].lower() == "text":
                textCount += 1
                list.append({
                    "type": "text",
                    "value": it["value"],
                    "name": saveGet(it, "name"),
                    "group": saveGet(it, "group")
                })
            else:
                dd = {
                    "type": it["type"],
                    "name": saveGet(it, "name"),
                    "group": saveGet(it, "group")
                    }
                savePut(it, dd, "minValue")
                savePut(it, dd, "maxValue")
                if "paramSettingInfo" in it:
                    filterIndex = it["paramSettingInfo"][0]["filterIndex"]
                    paramName = it["paramSettingInfo"][0]["paramName"]
                    objName = it["paramSettingInfo"][0]["paramName"]
                    valueType = it["paramSettingInfo"][0]["valueType"]
                    dd["paramKey"] = f"{filterIndex}:{paramName}"
                    dd["obj"] = objName
                    dd["valueType"] = valueType
                otherParam.append(dd)
        except Exception as e:
            list = []
    return {
        "videoCount":videoCount,
        "imageCount":imageCount,
        "audioCount":audioCount,
        "textCount":textCount,
        "list":list,
        "otherParams":list
    }

def listTemplate(searchPath):
    result = []
    tpDir = ""
    if len(searchPath) <= 0 or os.path.exists(searchPath) == False:
        rootDir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "res")
        updateResources(rootDir)
        tpDir = templateDir(rootDir)
    else:
        tpDir = searchPath
    if len(tpDir) <= 0 or os.path.exists(tpDir) == False:
        print("template resource not found")
        return result
    for root,dirs,files in os.walk(tpDir):
        for dir in dirs:
            projFile = os.path.join(root, dir, "template.proj")
            if os.path.exists(projFile) == False:
                for root,dirs,files in os.walk(os.path.join(root, dir)):
                    for file in files:
                        name, ext = os.path.splitext(file)
                        if ext == ".proj":
                            projFile = os.path.join(root, file)
            with open(projFile, 'r', encoding='utf-8') as f:
                projConfig = json.load(f)
            inputListPath = os.path.join(root, dir, "inputList.conf")
            if "inputList" in projConfig:
                inputListPath = os.path.join(root, dir, projConfig["inputList"])
            if "type" not in projConfig:
                continue
            if os.path.exists(inputListPath) == False:
                continue
            inputList = []
            with open(inputListPath, 'r', encoding='utf-8') as f:
                inputList = json.load(f)
            data = inputConfig(inputList)
            data["name"] = dir
            data["path"] = os.path.join(root, dir)
            result.append(data)
        if root != files:
            break
    return result

def listMusic(searchPath):
    mDir = ""
    if len(searchPath) <= 0 or os.path.exists(searchPath) == False:
        rootDir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "res")
        updateResources(rootDir)
        mDir = musicDir(rootDir)
    else:
        mDir = searchPath
    if len(mDir) <= 0 or os.path.exists(mDir) == False:
        print("music resource not found")
        return
    result = []
    for root,dirs,files in os.walk(mDir):
        for file in files:
            if file.find(".") <= 0:
                continue
            name = file[0:file.index(".")].lower()
            ext = file[file.index("."):].lower()
            if ext in [".mp3",".aac",".wav",".wma",".cda",".flac",".m4a",".mid",".mka",".mp2",".mpa",".mpc",".ape",".ofr",".ogg",".ra",".wv",".tta",".ac3",".dts"]:
                audioPath = os.path.join(root, file)
                f = mutagen.File(audioPath)
                result.append({
                    "name":file,
                    "path":audioPath,
                    "length":f.info.length,
                    "channels":f.info.channels
                })
        if root != files:
            break
    return result