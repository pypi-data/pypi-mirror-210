import os
import re

import requests
import parsel


def mkDir(save_path: str):
    if not os.path.exists(save_path):
        os.mkdir(save_path)
    return save_path


def getPageSource(url: str, headers: dict):
    resp = requests.get(url, headers)
    if resp.status_code == 200:
        resp.encoding = resp.apparent_encoding
        return resp.text


def parse_by_parsel(html: str):
    selector = parsel.Selector(html)
    return selector


def modify_file_name(old_name: str, replace=""):
    pattern = r"[\/\\\:\*\?\"\？\<\>\|]"  # '/ \ : * ? " < > |'
    new_name = re.sub(pattern, replace, old_name)
    return new_name


def save_imageData(save_path: str, img_name: str, img_src: str):
    img_data = requests.get(img_src).content
    with open(save_path + img_name, mode="wb") as fp:
        fp.write(img_data)
        print(f"[INFO] The Image [{img_name}] Have Been Saved.")
