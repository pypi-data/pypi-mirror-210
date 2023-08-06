# encoding: utf-8
"""
@project: djangoModel->main
@author: 孙楷炎
@Email: sky4834@163.com
@synopsis: 任务调度器
@created_time: 2022/7/26 13:28
"""
import os
import sys
import time

import schedule

sys.path.append("D:\\PySet\\djangoModel")
os.environ.setdefault('DJANGO_SETTINGS_MODULE', "main.settings")
import django

django.setup()

from command.bxtx_enroll_timer import ClockService

clocker = ClockService()
# 任务注册
schedule.every(2).seconds.do(clocker.check_end_clock)

while True:
    # 定时任务守护程序
    schedule.run_pending()
    time.sleep(1)
