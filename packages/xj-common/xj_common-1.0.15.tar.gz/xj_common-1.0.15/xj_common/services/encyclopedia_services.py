# encoding: utf-8
"""
@project: djangoModel->encyclopedia_services
@author: 孙楷炎
@Email: sky4834@163.com
@synopsis: 百科接口，基于chatgpt引擎开放的接口
@created_time: 2023/5/24 22:31
"""

import requests

from config.config import JConfig
from ..models import Encyclopedia
from ..utils.custom_tool import force_transform_type

config = JConfig()
open_api_key = config.get("xj_common", "open_api_key", "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")
headers = {
    'Authorization': f"Bearer {open_api_key}",
}


class EncyclopediaService():
    @staticmethod
    def ask_question(params: dict = None, user_info: dict = None):
        params, is_pass = force_transform_type(variable=params, var_type="dict", default={})
        question = params.get("question")
        if not user_info.get("user_id"):
            return None, "不是一个有效用户ID"

        temperature = params.get("temperature", 0.8)
        temperature, is_pass = force_transform_type(variable=temperature, var_type="float", default=0.8)
        temperature = temperature if 1 >= temperature > 0.2 else 0.8

        if not question:
            return None, "没有收到您的问题"
        json_data = {
            'model': 'gpt-3.5-turbo',
            'messages': [
                {
                    'role': 'user',
                    'content': question,
                },
            ],
            'temperature': temperature,
        }
        proxies_port = config.getint("main", "proxies_port", 10809)
        proxies = {
            'http': 'http://127.0.0.1:' + str(proxies_port),
            'https': 'http://127.0.0.1:' + str(proxies_port)
        }
        response = requests.post('https://api.openai.com/v1/chat/completions', headers=headers, json=json_data, proxies=proxies)
        res_json = response.json()
        encyclopedia_obj = Encyclopedia(
            user_id=user_info.get("user_id"),
            question=question,
            snapshot=res_json.get("choices"),
        )
        encyclopedia_obj.save()
        return res_json, None
