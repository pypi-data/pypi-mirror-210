# encoding: utf-8
"""
@project: djangoModel->service_manage_api
@author: 孙楷炎
@Email: sky4834@163.com
@synopsis: 服务治理API
@created_time: 2023/5/7 15:32
"""
from rest_framework.views import APIView

from ..utils.custom_response import util_response
from ..utils.custom_tool import request_params_wrapper
from ..utils.service_manager import ServiceManager


class ServiceManageApis(APIView):
    @request_params_wrapper
    def find_service_test(self, *args, request_params, **kwargs):
        service_id = request_params.get("service_id", 5521)
        name = request_params.get("service_id", "sunkaiyan")
        service_manager = ServiceManager()
        service, err = service_manager.find_service(service_id=service_id)
        if err:
            return util_response(msg=err)
        return util_response(data=service.hello(name=name))
        # return util_response(data=service.hello_rpc(), msg=service.hello_rpc(name=name))
