# -*- encoding: utf-8 -*-
# @Author: peng wei
# @Time: 2021/11/29 下午2:41

from common.variable.global_variable import *
from config.loads import properties


def service_init():
    # 设置当前默认数据库
    set_global_var("Database", "v31.postgres")

    # 设置当前environment，mongodb用到，必须项
    properties["environment"] = "v31.postgres"

    # 设置当前测试应用名称，必须项，与测试用例目录名一致。aisee、visualmodeler、crawler等
    properties["application"] = "webapi"

    # 第三方系统测试系统ip
    set_global_var("SystemUrl", "http://192.168.88.116:9312")

    # 当前数据库类型
    set_global_var("DatabaseType", "postgres")

    # webapi业务刷新密钥
    set_global_var("ApiInitPwd", "LOsXeDCuDbGXob3432WIzg==")



