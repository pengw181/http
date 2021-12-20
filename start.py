#!/usr/bin/env python

# -*- encoding: utf-8 -*-

# @Author: peng wei

# @Time: 2020-09-10 23:30

# @Contact: pw@henghaodata.com

from gooflow.controller import case_run
from common.variable.global_variable import *
from config.loads import properties
from config.serviceInit import service_init
import urllib3

urllib3.disable_warnings()


def main():
    # runAllTest为true时，runTestLevel不生效；runAllTest为false时，只执行runTestLevel指定级别的用例
    properties["runAllTest"] = True
    # 用例执行失败，是否继续执行下一条
    properties["continueRunWhenError"] = False
    # 设置测试用例覆盖级别
    properties["runTestLevel"] = ["高", "中", "低"]

    # 常用变量赋值
    set_global_var("BelongID", "440100")
    set_global_var("DomainID", "AiSeeCore")
    set_global_var("LoginUser", "admin")
    set_global_var("LoginPwd", "admin")
    set_global_var("Belong", "广州市")
    set_global_var("Domain", "广州市核心网")

    # 业务变量初始化
    service_init()

    # 开始运行，第一个数字为读取第几个测试用例文件（从1开始），第二个数字为读取测试用例的第几行（从1开始）
    case_run(1, 58)


if __name__ == "__main__":
    main()
