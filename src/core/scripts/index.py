
from core.scripts.txt2Img import txt2img
from core.scripts.img2Img import img2img
from core.scripts.inpaint import inpaint

scripts = {
    "txt2img": txt2img,
    "img2img": img2img,
    "inpaint": inpaint
}

def get_index_scripts():
    return scripts

def get_index_script_names():
    return list(scripts.keys())