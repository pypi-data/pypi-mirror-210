# encoding: utf-8
"""
@project: djangoModel->validate
@author: 孙楷炎
@Email: sky4834@163.com
@synopsis:
@created_time: 2022/6/10 16:12
"""
import json

from django import forms


class Validate(forms.Form):
    """检验基类，子类编写规则，调用父类的validate方法"""

    def validate(self):
        """
        request 请求参数验证
        :return {'code': 'err': self.errors}:
        """
        if self.is_valid():
            return True, None
        else:
            error = json.dumps(self.errors)
            error = json.loads(error)
            temp_error = {}
            # 统一展示小写 提示，中文转义回来
            for k, v in error.items():
                temp_error[k.lower()] = v[0]
            return False, temp_error


class RegionValidate(Validate):
    code = forms.CharField(
        required=True,
        error_messages={
            "required": "code 必填",
        })
    level = forms.CharField(
        required=True,
        error_messages={
            "required": "level 必填",
        })
    p_code = forms.CharField(
        required=True,
        error_messages={
            "required": "p_code 必填",
        })
    name = forms.CharField(
        required=True,
        error_messages={
            "required": "name 必填",
        })
