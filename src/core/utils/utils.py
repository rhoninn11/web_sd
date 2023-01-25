

import json
def obj2json2bytes(obj, verbose=False):
    json_txt = json.dumps(obj)
    data_len = len(json_txt)
    if verbose:
        print(f" +++o2j2d-verb: {json_txt} {data_len}")
    obj_bytes = bytes(json_txt, 'utf-8')
    len_bytes = data_len.to_bytes(4, 'little')
    data_to_send = len_bytes + obj_bytes
    return data_to_send

def bytes2json2obj(data):
    json_text = data.decode("utf-8")
    data = {}
    try:
        data = json.loads(json_text)
    except:
        print("był błąd")
    return data

import pickle
def obj2pickle2bytes(obj, verbose=False):
    pickled_obj = pickle.dumps(obj)
    data_len = len(pickled_obj)
    len_bytes = data_len.to_bytes(4, 'little')
    data_to_send = len_bytes + pickled_obj
    return data_to_send

def bytes2pickle2obj(data):
    obj = pickle.loads(data)
    return obj

def file2json2obj(json_file):
    data = None
    with open(json_file, 'r', encoding='utf-8') as j_file:
        json_content = j_file.read()
        data = json.loads(json_content)
    return data

def obj2json2file(obj, json_file_path):
    with open(json_file_path, 'w') as outfile:
        json.dump(obj, outfile, indent=4)
    return

import base64
from PIL import Image
def pil2simple_data(pil_img):
    img_bytes = pil_img.tobytes()
    img_base64 = base64.b64encode(img_bytes)
    simple_data =  {
        "img64": img_base64.decode('ascii'),
        "x": pil_img.size[0],
        "y": pil_img.size[1],
        "mode": pil_img.mode
    }
    return simple_data

def simple_data2pil(simple_data):
    pil_img_bytes = base64.b64decode(simple_data["img64"].encode("ascii"))
    pil_img_size = (simple_data["x"], simple_data["y"])
    pil_img_mode = simple_data["mode"]

    pil_img = Image.frombytes(pil_img_mode, pil_img_size, pil_img_bytes)
    return pil_img

import numpy
import time 
def numpy2pil(numpy_img):
    tic = time.perf_counter()
    rgbA = numpy_img*255
    rgbA = numpy.flipud(rgbA)
    rgb = rgbA[:,:,:-1] #strip off alpha
    rgb = rgb.astype(numpy.uint8)
    toc = time.perf_counter()
    pil_img = Image.fromarray(rgb)
    # print(F"+++ processing time: {toc - tic}")

    return pil_img

def pil2numpy(pil_img):
    pil_img = pil_img.convert('RGBA')
    numpy_img = numpy.asarray(pil_img)
    # numpy_img = numpy.flipud(numpy_img)

    return numpy_img