# encoding: utf-8
"""
@project: djangoModel->regin_service
@author: 孙楷炎
@Email: sky4834@163.com
@synopsis:
@created_time: 2022/6/10 16:08
"""
from django.core.paginator import Paginator

from ..models import Region
from ..utils.custom_tool import format_params_handle


class RegionService():

    def cn_parse_location_code(self, region_code):
        # 中国行政编码解析 province{2},city(2),district(2),town(3),village(3)三位
        # level？ province ==>>village : 1 ===>> 5
        if not region_code or not len(str(region_code)) == 12:
            return None
        location = {}
        region_code = str(region_code)
        location['province'] = self.get_region_info(region_code[0:2] + "0000000000")

        city = self.get_region_info(region_code[0:4] + "00000000")
        location['city'] = city if not city == location['province'] else None

        district = self.get_region_info(region_code[0:6] + "000000")
        location['district'] = district if not district == city else None

        town = self.get_region_info(region_code[0:9] + "000")
        location['town'] = town if not town == district else None

        village = self.get_region_info(region_code[0:])
        location['village'] = village if not town == village else None

        return location

    def get_region_info(self, code):
        # 查询对应的名称
        json_data = Region.objects.filter(code=code, is_delete=0).to_json()
        if not json_data:
            return None
        else:
            return json_data

    def region_tree(self, code=None):
        search_list = Region.objects.all().to_json()
        self.p_code_map = {}
        for i in search_list:
            if not self.p_code_map.get(i["p_code"], None):
                self.p_code_map[i["p_code"]] = [i]
            else:
                self.p_code_map[i["p_code"]].append(i)

        if code:
            search_list = Region.objects.filter(code=code).to_json()

        tree_map = []
        for i in search_list:
            if not i["p_code"] == 0 and code is None:
                continue

            i["child"] = self.get_child(i["code"])
            tree_map.append(i)

        return tree_map, None

    def get_child(self, code=None, ):
        # 树形数据遍历
        child_list = self.p_code_map.pop(code, [])
        if not child_list:
            return []

        for i in child_list:
            i["child"] = self.get_child(i["code"])
        return child_list

    @staticmethod
    def list(params=None):
        if params is None:
            params = {}
        page = params.pop('page', 1)
        size = params.pop('size', 20)

        params = format_params_handle(
            param_dict=params,
            filter_filed_list=["id", "code", "p_code", "name", "level"],
            alias_dict={'name': "name__contains", }
        )
        list_set = Region.objects.filter(is_delete=0).filter(**params).values()
        count = list_set.count()
        page_set = Paginator(list_set, size).get_page(page)

        return {'count': int(count), "page": int(page), "size": int(size), "list": list(page_set.object_list)}, None

    @staticmethod
    def add(data):
        res = Region.objects.filter(code=data['code'], is_delete=0)
        if res:
            return None, "该数据已存在"
        instance = Region.objects.create(**data)
        return {"id": instance.id}, None

    @staticmethod
    def edit(data):
        id = data.pop('id', None)
        if not id:
            return None, "ID 必传"
        res_obj = Region.objects.filter(id=id, is_delete=0)
        if not res_obj:
            return None, "数据不存在"
        res_obj.update(**data)
        return None, None

    @staticmethod
    def delete(pk=None):
        if pk is None:
            return None, "参数错误"
        res = Region.objects.filter(id=pk)
        if not res.first():
            return None, None
        res.delete()
        return None, None
