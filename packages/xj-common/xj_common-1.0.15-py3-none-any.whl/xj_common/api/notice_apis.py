# encoding: utf-8
"""
@project: djangoModel->notice_apis
@author: 孙楷炎
@Email: sky4834@163.com
@synopsis: 统计API
@created_time: 2023/3/1 15:12
"""
from rest_framework.views import APIView

from ..services.notice_services import NoticeServices
from ..utils.custom_response import util_response
from ..utils.custom_tool import request_params_wrapper


class NoticeApis(APIView):

    @request_params_wrapper
    def notice_list(self, *args, request_params=None, **kwargs):
        if request_params is None:
            request_params = {}
        try:
            need_pagination = bool(request_params.pop("need_pagination", True))
        except Exception as e:
            need_pagination = False
        data, err = NoticeServices.notice_list(params=request_params, need_pagination=need_pagination)
        if err:
            return util_response(err=1001, msg=err)
        return util_response(data=data)

    @request_params_wrapper
    def type_list(self, *args, request_params=None, **kwargs):
        if request_params is None:
            request_params = {}
        try:
            need_pagination = int(request_params.pop("need_pagination", 0))
        except Exception as e:
            need_pagination = 0

        data, err = NoticeServices.notice_type_list(params=request_params, need_pagination=need_pagination)
        if err:
            return util_response(err=1001, msg=err)
        return util_response(data=data)

    @request_params_wrapper
    def notice_add(self, *args, request_params=None, **kwargs):
        if request_params is None:
            request_params = {}
        data, err = NoticeServices.notice_add(params=request_params)
        if err:
            return util_response(err=1001, msg=err)
        return util_response(data=data)

    @request_params_wrapper
    def notice_edit(self, *args, request_params=None, **kwargs):
        if request_params is None:
            request_params = {}
        notice_id = request_params.pop("notice_id", None) or request_params.pop("id", None)
        data, err = NoticeServices.notice_edit(params=request_params, notice_id=notice_id)
        if err:
            return util_response(err=1001, msg=err)
        return util_response(data=data)
