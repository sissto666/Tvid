import os
import json


# 日志级别
os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = "--disable-logging --log-level=3"

BASE_DIR = os.getcwd()

browser_data_file = os.path.join(BASE_DIR, 'browser_data')

bookmark_file = os.path.join(BASE_DIR,  'user_data', 'bookmarks.json')

config_json_file = os.path.join(BASE_DIR,  'config.json')

ico = os.path.join(BASE_DIR, 'user_data','logo.ico')

os.makedirs(browser_data_file, exist_ok=True)

os.makedirs(os.path.dirname(bookmark_file), exist_ok=True)

if not os.path.exists(bookmark_file):
    bookmarks_object = open(bookmark_file, mode='w', encoding='utf-8')
else:
    bookmarks_object = open(bookmark_file, mode='r', encoding='utf-8')

# 内存中书签
try:
    bookmarks_data = json.load(bookmarks_object)
except:
    bookmarks_data = {}


def read_and_write_to_bookmarks(file, new_dic=None):
    global bookmarks_data
    _object = open(file, mode='w', encoding='utf-8')
    if new_dic:
        merged_data = {**bookmarks_data, **new_dic}
    else:
        merged_data = bookmarks_data
    bookmarks_data = merged_data
    json.dump(merged_data, _object, indent=4, ensure_ascii=False)


try:
    with open(config_json_file, mode='r', encoding='utf-8') as json_object:
        parameter = json.load(json_object)
except:
    parameter = {
        # 窗口透明度
        'opacity': 0.75,
        # 长宽比
        'aspect_ratio': 16/9,
        # 默认主页
        'default_url': 'https://www.bilibili.com',
        # 用户代理
        'UserAgent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    }

def save_parameter(**kwargs):
    global parameter
    for key,value in kwargs.items():
        parameter[key] = value
    with open(config_json_file, mode='w', encoding='utf-8') as json_object:
         json.dump(parameter, json_object, ensure_ascii=False, indent=4)