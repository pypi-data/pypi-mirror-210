# encoding: utf-8
"""
@project: djangoModel->access_level_api
@author: 孙楷炎
@Email: sky4834@163.com
@synopsis: 访问级别列表
@created_time: 2023/4/11 20:54
"""
from rest_framework.views import APIView

from ..services.access_level_services import AccessLevelService
from ..utils.custom_response import util_response


class AccessLevelAPIView(APIView):
    def access_level_list(self, *args, **kwargs):
        access_level_list, err = AccessLevelService.access_level_list()
        if err:
            return util_response(msg=err)
        return util_response(data=access_level_list)
