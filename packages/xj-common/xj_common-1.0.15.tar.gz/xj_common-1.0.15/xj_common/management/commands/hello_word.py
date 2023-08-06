# encoding: utf-8
"""
@project: djangoModel->test.py
@author: 孙楷炎
@Email: sky4834@163.com
@synopsis: 测试脚本 say hello
@created_time: 2023/4/17 21:09
"""

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    # 帮助文本, 一般备注命令的用途及如何使用。
    help = "Print Hello World!"

    # 给命令添加一个名为name的参数
    def add_arguments(self, parser):
        parser.add_argument('name')

    # 核心业务逻辑，通过options字典接收name参数值，拼接字符串后输出
    def handle(self, *args, **options):
        msg = 'Hello World ! ' + options['name']
        self.stdout.write(msg)
        # 此时当你再次运行`python manage.py hello_world John`命令时，你将得到如下输出结果：
