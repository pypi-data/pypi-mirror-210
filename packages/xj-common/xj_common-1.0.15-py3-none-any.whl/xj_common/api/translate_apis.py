# encoding: utf-8
"""
@project: djangoModel->translate_apis
@author: 孙楷炎
@Email: sky4834@163.com
@synopsis: 分页服务测试接口
@created_time: 2022/11/17 13:53
"""
import json

from rest_framework.views import APIView

from ..services.translate_server import TranslateService
from ..utils.custom_response import util_response
from ..utils.custom_tool import request_params_wrapper


class TranslateApis(APIView):
    @request_params_wrapper
    def get(self, *args, request_params=None, **kwargs, ):
        text_list = request_params.get("text", None)
        if text_list is None:
            return util_response(msg="参数错误", err=1000)
        service = TranslateService()
        data, err = service.translate(text_list)
        return util_response(data=data)

    @request_params_wrapper
    def translate_article(self, *args, request_params=None, **kwargs, ):
        article = request_params.get("article", None)
        if article is None:
            return util_response(msg="参数错误", err=1000)
        app = TranslateService()

        # markdown文章拆分成行文本列表
        old_line_arr = app.article_cut_lines(article)

        # 提取行格式，还有需要翻译的文本
        markdown_symbol_list = []
        translate_list = []
        for line in old_line_arr:
            markdown_symbol, translate_text = app.markdown_paragraph_pick(line)
            markdown_symbol_list.append(markdown_symbol)
            translate_list.append(translate_text)

        # 进行翻译
        result, err = app.translate(translate_list)

        # 还原行文本的行格式
        translated_list = [i["text"] for i in result["data"][0]["translated"]]
        deacidizing_list = []
        for i, j in zip(translated_list, markdown_symbol_list):
            deacidizing_list.append(j + i)

        # 链接还原，还原成文本
        deacidizing = ""
        for i in deacidizing_list:
            deacidizing += app.deacidizing_symbol(i) + "\n"

        # 返回数据
        return util_response(data=deacidizing)
