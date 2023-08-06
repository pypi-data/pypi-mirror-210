# encoding: utf-8
"""
@project: djangoModel->service_register
@author: 孙楷炎
@Email: sky4834@163.com
@synopsis: 对外开放服务调用注册白名单
@created_time: 2023/1/12 14:29
"""
from jsonrpc import jsonrpc_method

import xj_common
from xj_common.utils.service_manager import ServiceManager
from .services import notice_services


# ============= section 微服务测试放啊 start =========================
@jsonrpc_method("hello_rpc")
def hello_rpc(*args, **kwargs):
    return {"msg": "Hi rpc!!!"}


def hello(*args, name="word", **kwargs):
    print(args, kwargs)
    return {"msg": "Hi " + str(name) + "!!!"}


# ============= section 微服务测试放啊 end =========================

# 对外服务白名单
register_list = [
    {
        "service_name": "hello",
        "pointer": hello
    },
    {
        "service_name": "notice_add",
        "pointer": notice_services.NoticeServices.notice_add
    },
    {
        "service_name": "notice_edit",
        "pointer": notice_services.NoticeServices.notice_edit
    },
]

server_manager = ServiceManager()


# 遍历注册
def register():
    for i in register_list:
        setattr(xj_common, i["service_name"], i["pointer"])
        server_manager.put_service(route=i["service_name"], method=i["pointer"])


if __name__ == '__main__':
    register()
