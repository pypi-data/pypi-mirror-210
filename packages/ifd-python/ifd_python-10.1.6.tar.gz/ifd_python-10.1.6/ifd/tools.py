from .entities import Image, LogResult
import json
import os

def getDictFromBytes(data: bytes):
    data = data.decode("utf-8")
    return json.loads(data)

def getImageFromJson(json_image: str):
    image: Image = Image()
    image.deserialize(json_image)
    return image

def getJsonFromImage(image: Image):
    return image.serialize()

def getLogResultFromJson(json_log: str):
    log: LogResult = LogResult()
    log.deserialize(json_log)
    return log

def getJsonFromLogResult(log: LogResult):
    return log.serialize()
    
def transformImagePath(img_path : str):
    src_image = "/".join(str(img_path).replace("\\","/").strip("/").split('/')[1:])
    src_image = "/".join(src_image.split('/')[1:]) if src_image.split('/')[0] == 'CRI' else src_image
    src_image = os.path.join('/mnt/', src_image)
    return src_image