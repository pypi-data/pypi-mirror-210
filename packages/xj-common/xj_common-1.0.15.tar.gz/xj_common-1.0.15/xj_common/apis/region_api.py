# encoding: utf-8
"""
@project: djangoModel->region_api
@author: 孙楷炎
@Email: sky4834@163.com
@synopsis:
@created_time: 2022/12/6 10:56
"""

from django.views.decorators.http import require_http_methods
from rest_framework.views import APIView

from ..services.regin_service import RegionService
from ..utils.custom_response import util_response
from ..utils.custom_tool import parse_data
from ..validate import RegionValidate


# =============== 地区操作 =======================
class RegionAPIS(APIView):
    # 查询列表
    @require_http_methods(["GET"])
    def get_region_tree(self):
        params = parse_data(self)
        p_code = params.get("code", None)
        service = RegionService()
        region_tree, err = service.region_tree(p_code)
        if err:
            return util_response(err=1000, msg=err)
        return util_response(data=region_tree)

    # 查询列表
    @require_http_methods(["GET"])
    def region_list(self):
        params = parse_data(self)
        print(params)
        data, err = RegionService.list(params=params)
        if err:
            return util_response(err=1000, msg=err)
        return util_response(data=data)

    @require_http_methods(["POST"])
    def region_add(self, ):
        data = parse_data(self)
        validator = RegionValidate(data)
        is_valid, error = validator.validate()
        if not is_valid:
            return util_response(err=1000, msg=error)

        res, err = RegionService.add(data)

        if err:
            return util_response(err=1001, msg=err)
        return util_response(data=res)

    @require_http_methods(["PUT"])
    def region_edit(self):
        data = parse_data(self)
        res, err = RegionService.edit(data)
        if err:
            return util_response(err=1000, msg=err)
        return util_response()

    @require_http_methods(["DELETE"])
    def region_del(self):
        params = parse_data(self)
        pk = params.get("id", None) or params.get("pk", None)
        data, err = RegionService.delete(pk)
        if not err is None:
            return util_response(err=1000, msg=err)
        return util_response()


class RegionCodeParse(APIView):

    def parse_code(self, code):
        # 解析code
        service = RegionService()
        res = service.cn_parse_location_code(code)
        return util_response()
