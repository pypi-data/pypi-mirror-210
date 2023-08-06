# encoding: utf-8
"""
@project: djangoModel->notice_services
@author: 孙楷炎
@Email: sky4834@163.com
@synopsis: 消息提醒服务
@created_time: 2023/3/1 11:08
"""

from django.core.paginator import Paginator, EmptyPage
from django.db.models import F

from ..models import NoticeType, Notice
from ..utils.custom_tool import format_params_handle


class NoticeServices():
    """消息提醒服务类"""

    @staticmethod
    def notice_type_list(params: dict = None, need_pagination: int = 0):
        if params is None:
            params = {}
        page = params.pop("page", 1)
        size = params.pop("size", 10)
        # 参数过滤
        params = format_params_handle(
            param_dict=params,
            filter_filed_list=["id", "value", "name", "notice_type_id"],
            alias_dict={"notice_type_id": "id"}
        )

        notice_type_obj = NoticeType.objects.filter(**params).values("id", "value", "name", "description")
        # 不许分页直接返回
        if not need_pagination:
            notice_type_list = list(notice_type_obj)
            return notice_type_list, None

        total = notice_type_obj.count()
        paginator = Paginator(notice_type_obj, size)
        try:
            notice_type_obj = paginator.page(page)
        except EmptyPage:
            notice_type_obj = paginator.page(paginator.num_pages)
        except Exception as e:
            return None, f'{str(e)}'

        return {"page": int(page), "size": int(size), "total": total, "list": list(notice_type_obj.object_list)}, None

    @staticmethod
    def notice_list(params: dict = None, need_pagination: bool = True):
        if params is None:
            params = {}
        page = params.pop("page", 1)
        size = params.pop("size", 10)
        # 参数过滤
        params = format_params_handle(
            param_dict=params,
            filter_filed_list=[
                "id", "id_list", "notice_id_list", "notice_type_value", "notice_type_id", "notice_type_id_list", "thread_id", "thread_id_list",
                "from_user_id", "from_user_id_list", "to_user_id", "to_user_id_list", "to_role_id", "to_role_id_list", "status",
                "created_time_start", "created_time_end" "read_time_start", "read_time_end", "expire_time_start", "expire_time_end"
            ],
            alias_dict={
                "notice_id_list": "id__in",
                "id_list": "id__in",
                "notice_type_id_list": "notice_type_id__in",
                "thread_id_list": "thread_id__in",
                "from_user_id_list": "from_user_id__in",
                "to_user_id_list": "to_user_id__in",
                "to_role_id_list": "to_role_id__in",
                "created_time_start": "created_time__gte",
                "created_time_end": "created_time__lte",
                "read_time_start": "read_time__get",
                "read_time_end": "read_time__lte",
                "expire_time_start": "expire_time__gte",
                "expire_time_end": "expire_time__lte",
            }
        )

        notice_obj = Notice.objects.filter(**params).annotate(
            notice_type_name=F("notice_type__name"),
            notice_type_value=F("notice_type__value"),
        ).values()
        # 不许分页直接返回
        if not need_pagination:
            if not params:
                return None, "无法搜索，参数错误"
            notice_obj_list = list(notice_obj)
            return notice_obj_list, None

        total = notice_obj.count()
        paginator = Paginator(notice_obj, size)
        try:
            notice_obj = paginator.page(page)
        except EmptyPage:
            notice_obj = paginator.page(paginator.num_pages)
        except Exception as e:
            return None, f'{str(e)}'

        return {"page": int(page), "size": int(size), "total": total, "list": list(notice_obj.object_list)}, None

    @staticmethod
    def notice_edit(params: dict = None, notice_id: int = None, search_params: dict = None):
        """
        提醒修改
        :param params: 要修改的参数
        :param notice_id: 根据ID修改数据
        :param search_params: 根据查询参数，查询单条或者多条数据。两者二选一，不可以同时使用
        :return: data,err
        """
        # 参数为空判断
        notice_id = notice_id or params.pop("notice_id", None)
        if not notice_id and not search_params:
            return None, "找不到可修改的数据"

        # 需要修改的字段过滤
        filter_params = format_params_handle(
            param_dict=params,
            filter_filed_list=[
                "notice_type", "notice_title", "notice_content", "link", "files", "status",
                "created_time", "read_time", "expire_time", "thread_id", "from_user_id",
                "to_user_id", "to_role_id",
            ],
        )
        if params is None:
            return {"msg": "数据并未发生修改"}, None

        # 搜索字段
        search_params = format_params_handle(
            param_dict=search_params,
            filter_filed_list=[
                "id", "id_list", "notice_id_list", "notice_type", "notice_type_id", "notice_type_id_list", "thread_id", "thread_id_list",
                "from_user_id", "from_user_id_list", "to_user_id", "to_user_id_list", "to_role_id", "to_role_id_list", "status",
                "created_time_start", "created_time_end" "read_time_start", "read_time_end", "expire_time_start", "expire_time_end"
            ],
            alias_dict={
                "notice_id_list": "id__in",
                "id_list": "id__in",
                "notice_type_id_list": "notice_type_id__in",
                "thread_id_list": "thread_id__in",
                "from_user_id_list": "from_user_id__in",
                "to_user_id_list": "to_user_id__in",
                "to_role_id_list": "to_role_id__in",
                "created_time_start": "created_time__gte",
                "created_time_end": "created_time__lte",
                "read_time_start": "read_time__get",
                "read_time_end": "read_time__lte",
                "expire_time_start": "expire_time__gte",
                "expire_time_end": "expire_time__lte",
            }
        ) if (search_params and isinstance(search_params, dict)) else None

        # 找到要修改的数据
        notice_obj = None
        if notice_id:
            notice_obj = Notice.objects.filter(id=notice_id)
        if search_params:
            notice_obj = Notice.objects.filter(**search_params)

        if not notice_obj:
            return {"msg": "没有找到要修改的数据"}, None

        # 数据修改
        try:
            notice_obj.update(**filter_params)
        except Exception as e:
            return None, "修改异常:" + str(e)

        return None, None

    @staticmethod
    def notice_add(notice_type_value: str = None, notice_params: dict = None, **kwargs):
        """
        添加提醒
        :param notice_type_value: 信息类型Value
        :param notice_params: 其他的系统参数
        :param kwargs: 聚名参数
        :return: data,err
        """
        if notice_params is None:
            notice_params = {}
        if kwargs is None:
            kwargs = {}

        # 这样做的目的是为了,流程自动化调用该服务.
        notice_params.update(kwargs)
        if notice_type_value:
            notice_type_id = NoticeType.objects.filter(value=notice_type_value).values("id").first()
            notice_params.setdefault("notice_type_id", notice_type_id)

        # 参数校验
        if not notice_params.get("to_user_id") and not notice_params.get("to_role_id"):
            return None, "msg:请检查参数;tip:找不到可发送的对象"

        # 需要修改的字段过滤
        filter_params = format_params_handle(
            param_dict=notice_params,
            filter_filed_list=[
                "notice_type", "notice_type_id", "notice_title", "notice_content", "link", "files",
                "created_time", "read_time", "expire_time", "thread_id", "from_user_id",
                "to_user_id", "to_role_id",
            ],
            alias_dict={"notice_type": "notice_type_id"}
        )

        filter_params["status"] = 0
        try:
            Notice.objects.create(**filter_params)
        except Exception as e:
            return None, "修改异常:" + str(e)
        return None, None
