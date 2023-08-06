# encoding: utf-8
"""
@project: djangoModel->translate_server
@author: 孙楷炎
@Email: sky4834@163.com
@synopsis: 翻译公共服务
@created_time: 2022/11/17 11:20
"""
import hashlib
import json
import random
import re
import time

import requests

appKey = "z7EtfGBkVNN2OnQC49vd4ns1"
app_sercet = "CIvWKy78t6T9d56vORQvItx9tHLCsLqK"


def replace():
    pass


class TranslateService():
    old_text_arr = []
    replace_symbol = {}

    def get_sign(self, form_data):
        # 第一步
        sorted_form_data = {}
        for i in sorted(form_data):
            sorted_form_data[i] = form_data[i]

        # 第二步
        old_txt = sorted_form_data["text"]
        text = ""
        for t in old_txt:
            text += t
        sorted_form_data["text"] = text

        # 第三步
        urlencode_str = ""
        for k, v in sorted_form_data.items():
            if not urlencode_str == "":
                urlencode_str += "&"
            urlencode_str += k + "=" + v

        # 第四步
        md5_str = urlencode_str + "&" + app_sercet

        # 第五步
        m1 = hashlib.md5()
        m1.update(md5_str.encode("utf-8"))
        sign = m1.hexdigest()

        sorted_form_data["sign"] = sign
        sorted_form_data["text"] = old_txt
        return sorted_form_data

    def translate(self, text_arr, source="zh", target="en"):
        # 完成sign 数据拼接
        form_data = {
            "appKey": "z7EtfGBkVNN2OnQC49vd4ns1",
            'source': source,
            'target': target,
            'text': text_arr
        }
        form_data = self.get_sign(form_data)
        # 发送请求
        session = requests.session()
        header = {
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36"
        }
        return session.post(url="https://dev-web.tangpafanyi.com/transaction/api/text/tran", headers=header, data=json.dumps(form_data)).json(), None

    def article_cut_lines(self, article):
        return article.split("\n")

    def markdown_paragraph_pick(self, text):
        # 段落文本解析
        # 满足下面条件则拿出初步翻译的文本进行替换
        find_patt = ""
        translate_patt_list = [
            "(^#{1,6}\s)([^\n]*)?",  # 标题
            "(^\>\s)([^\n]*)?",  # 引用
            "(^\s*\*\s\[x?\])([^\n]*)?",  # 任务列表
            "(^\s*\d*\.\s)([^\n]*)?",  # 有序列表
            "(^\s*\*\s)([^\n^]*)?",  # 无序列表
            "(^\s*\-\s)([^\n^]*)?",  # 脑图
        ]
        for patt in translate_patt_list:
            res = re.match(patt, text)
            if not res:
                continue
            find_patt, res_str = res.groups()
            res_str = self.__replace_symbol(res_str)
            return find_patt, res_str

        return find_patt, self.__replace_symbol(text)

    def __replace_symbol(self, text):
        # 替换符号
        replace = re.findall("\([^\n^\)]*?\)", text)
        for i in replace:
            name = self.random_name()
            self.replace_symbol[name] = i
            text = text.replace(i, name)
        return text

    def deacidizing_symbol(self, text):
        # 翻译完成官员符号
        for k, v in self.replace_symbol.items():
            text = text.replace(k, v)
        return text

    # 随机替换字符串
    def random_name(self):
        return "{{" + str(random.randint(9999, 100000)) + str(int(round(time.time() * 1000)))[-3:-1] + "}}"

#
# if __name__ == '__main__':
#     app = TranslateService()
#     article = """
#     [Vditor - 浏览器端的 Markdown 编辑器](https://ld246.com/article/1549638745630) 是一款**所见即所得**编辑器，支持 *Markdown*。
#
#     * 不熟悉 Markdown 可使用工具栏或~~快捷键~~进行排版
#       * 熟悉 Markdown 可直接**排版**，也*可切换*为分屏预~~览打~~算
#
#     更多细节和用法请参考 [Vditor - 浏览器端的 Markdown 编辑器](https://ld246.com/article/1549638745630)，同时也欢迎向我们提出建议或报告问题，谢谢 ❤️
#
#     ## 教程
#
#     这是一篇讲解如何正确使用 **Markdown** 的排版示例，学会这个很有必要，能让你的文章有更佳清晰的排版。
#
#     > 引用文本：Markdown is a text formatting syntax inspired
#     """
#
#     old_line_arr = app.article_cut_lines(article)
#
#     markdown_symbol_list = []
#     translate_list = []
#
#     for line in old_line_arr:
#         markdown_symbol, translate_text = app.markdown_paragraph_pick(line)
#         markdown_symbol_list.append(markdown_symbol)
#         translate_list.append(translate_text)
#
#     result, err = app.translate(translate_list)
#     translated_list = [i["text"] for i in result["data"][0]["translated"]]
#     deacidizing_list = []
#     for i, j in zip(translated_list, markdown_symbol_list):
#         deacidizing_list.append(j + i)
#
#     deacidizing = ""
#     for i in deacidizing_list:
#         deacidizing += app.deacidizing_symbol(i) + "\n"
#     print(deacidizing)
