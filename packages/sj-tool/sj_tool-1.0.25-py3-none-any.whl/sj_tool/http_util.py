import json
from typing import Dict

import requests


def post(url, data: Dict = None, to_dict=True):
    if data is None:
        data = {}
    response = requests.post(url, data=data)
    if response.status_code == 200:
        text = response.text
        if to_dict:
            return json.loads(text)
        return response.text
    else:
        print("请求失败:", response.status_code)
        if to_dict:
            return {}
        return ""


