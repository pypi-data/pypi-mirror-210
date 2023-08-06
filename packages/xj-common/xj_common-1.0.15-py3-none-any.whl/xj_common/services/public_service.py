# encoding: utf-8
"""
@project: djangoModel->service
@author: 孙楷炎
@Email: sky4834@163.com
@synopsis: 公共模块服务 CURD 封装
@created_time: 2022/6/10 16:04
"""
import json

from django.core import serializers
from django.core.paginator import Paginator


def parse_data(data):
    # 解析请求参数
    requestData = {}
    for k, v in data.items():
        requestData[k] = v if not v == "" else None
    return requestData


def parse_model(res_set, need_all=False):
    json_data = json.loads(serializers.serialize('json', res_set))
    if not json_data:
        return None
    else:
        if not need_all:
            return json_data[0]['fields']
        else:
            return [i['fields'] for i in json_data]


def model_select(request, model, is_need_delete=False, json_parse_key=None):
    # 模型快速分页查询  分页+条件
    page = request.GET.get('page', 1)
    limit = request.GET.get('limit', 20)
    params = parse_data(request.GET)
    if 'page' in params.keys():
        del params['page']
    if 'limit' in params.keys():
        del params['limit']

    if is_need_delete:
        params['is_delete'] = 0
    try:
        list_set = model.objects.filter(**params)
        count = model.objects.filter(**params).count()
    except Exception as e:
        return {'isSuccess': False, 'msg': e.__str__(), 'data': None}
    # 分页数据
    limit_set = Paginator(list_set, limit)
    page_set = limit_set.get_page(page)
    # 数据序列化操作
    json_data = json.loads(serializers.serialize('json', page_set))
    final_res_dict = []
    for i in json_data:
        fields = i['fields']
        fields['id'] = i['pk']
        if not json_parse_key is None:
            fields[json_parse_key] = json.loads(fields[json_parse_key])
        final_res_dict.append(fields)
    # 数据拼装

    result = {'isSuccess': True, 'msg': '加载成功', 'data': final_res_dict}
    result['limit'] = int(limit)
    result['page'] = int(page)
    result['count'] = count
    return result


def model_del(request, model, is_real_delete=True):
    # 删除设备
    id = request.POST.get('id')
    if not id:
        return {'isSuccess': False, 'msg': 'ID不能为空'}
    from_data = parse_data(request.POST)
    if is_real_delete:
        res = model.objects.filter(**from_data)
        if not res:
            return {'isSuccess': False, 'msg': '数据已不存在'}
        res.delete()
    else:
        from_data['is_delete'] = 0
        res = model.objects.filter(**from_data)
        if not res:
            return {'isSuccess': False, 'msg': '数据已不存在'}
        res.update(is_delete=1)

    return {'isSuccess': True, 'msg': '删除成功'}


def model_create(request, model, validate):
    try:
        requestData = parse_data(request.POST)
        validator = validate(requestData)
        is_pass, error = validator.validate()
        if not is_pass:
            return {'isSuccess': False, 'msg': error}
        model.objects.create(**requestData)
    except Exception as e:
        return {'isSuccess': False, 'msg': str(e)}
    return {'isSuccess': True, 'msg': '创建成功'}


def model_update(request, model, is_need_delete=False):
    # 模型修改
    id = request.POST.get('id')
    if not id:
        return {'isSuccess': False, 'msg': 'ID不能为空'}
    from_data = parse_data(request.POST)

    del from_data['id']
    if from_data == {}:
        return {'isSuccess': False, 'msg': '修改项为空'}

    if is_need_delete:
        res = model.objects.filter(id=id, is_delete=0)
    else:
        res = model.objects.filter(id=id)
    if not res:
        return {'isSuccess': False, 'msg': '数据已不存在'}
    try:
        res.update(**from_data)
        return {'isSuccess': True, 'msg': '修改成功'}
    except Exception as e:
        return {'isSuccess': False, 'msg': str(e)}
