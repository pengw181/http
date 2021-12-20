# -*- encoding: utf-8 -*-
# @Author: peng wei
# @Time: 2021/11/16 下午5:15

import os
from common.variable.global_variable import clear_process_var
from config.loads import properties
from common.log.logger import log


def init():

    log.info("启动测试初始化任务..")
    # 清空过程变量值
    clear_process_var()

    log.info("初始化完成.")