# encoding: utf-8
"""
@project: djangoModel->encyclopedia_api
@author: 孙楷炎
@Email: sky4834@163.com
@synopsis: 百科接口
@created_time: 2023/5/25 8:42
"""
from rest_framework.views import APIView

from ..services.encyclopedia_services import EncyclopediaService
from ..utils.custom_response import util_response
from ..utils.custom_tool import request_params_wrapper
from ..utils.user_wrapper import user_authentication_force_wrapper


class EncyclopediaApis(APIView):

    @user_authentication_force_wrapper
    @request_params_wrapper
    def ask_question(self, *args, request_params=None, user_info, **kwargs):
        if request_params is None:
            request_params = {}
        data, err = EncyclopediaService.ask_question(params=request_params, user_info=user_info)
        if err:
            return util_response(err=1000, msg=err)
        return util_response(data=data)
