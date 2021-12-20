# -*- encoding: utf-8 -*-
# @Author: peng wei
# @Time: 2020-09-10 23:17

import json
from json.decoder import JSONDecodeError
from common.variable.global_variable import *
from datetime import datetime
from time import sleep
from gooflow.checks import check_db_data
from database.SQLHelper import SQLUtil
from httpServer.json_analysis import AnalysisJson
from config.schemaMap import get_schema
from gooflow.codes import store_error_code
from common.log.logger import log


def compare_data(checks):
    """"
    :param: checks：string
    :return: bool
    """

    # 定义一个检查标识
    check_result = True

    if checks:
        check_list = checks.split(chr(10))    # 第一次使用换行拆分比对预期结果单元格内容

        for i in range(len(check_list)):

            log.info("开始处理 {0}".format(check_list[i]))
            set_global_var("EndTime", datetime.now().strftime('%Y%m%d%H%M%S'), False)
            if check_list[i].strip() == "":
                # 为空不匹配，默认成功
                check_result = True
            else:
                my_list = check_list[i].split('|')   # 将数据以竖线分割
                compare_item = my_list[0]       # CheckData

                if compare_item == "CheckData":

                    db_schema_table = my_list[1]
                    # log.info("db_schema_table: {}".format(db_schema_table))
                    # ${Database}.main.tn_process_conf_info
                    tmp = db_schema_table.split(".")
                    table_name = tmp[-1]
                    schema = tmp[-2]
                    db = ".".join(tmp[: -2])
                    count = my_list[2]
                    data = "|".join(my_list[3:])

                    # 自动替换${xx}变量
                    db = replace_global_var(db)
                    log.info("db: {}".format(db))
                    log.info("schema: {}".format(get_schema(schema)))
                    data = replace_global_var(data)
                    log.info("data: {}".format(data))

                    # # 对于字段是json，值里面带有双引号，需要先用\转义
                    # data = data.replace('"', '\\"')
                    # data = data.replace("'", "\\'")

                    # 对于匹配字段里有～的，替换成换行
                    data = data.replace("~", r"\r\n")

                    check_result = check_db_data(db, schema, table_name, data, count)
                    if not check_result.get("status"):
                        store_error_code("{0}表数据不匹配，{1}".format(table_name, check_result.get("data")))
                        check_result = False
                        break

                elif compare_item == "NoCheck":
                    # 不校验，只要前面步骤不报错，直接通过
                    log.info("本条匹配项不做匹配，跳过")
                    pass

                elif compare_item == "Wait":
                    sleep_time = int(my_list[1])
                    log.info("Sleep {} seconds".format(sleep_time))
                    sleep(sleep_time)

                elif compare_item == "GetData":
                    # GetData|${Database}.main|select xx from xx|NodeID
                    # 将sql查询到的结果，赋值给新变量名NodeID，匹配结果中，以${NodeID}使用变量的值
                    db_tmp = my_list[1].split(".")
                    db = db_tmp[0]
                    schema = db_tmp[1]
                    schema = get_schema(schema)
                    sql = my_list[2]
                    # 自动替换${xx}变量
                    db = replace_global_var(db)
                    sql = replace_global_var(sql)

                    sql_util = SQLUtil(db=db, schema=schema)
                    sql_result = sql_util.select(sql)
                    # 将查到的结果，存入全局变量
                    set_global_var(my_list[3].strip(), sql_result)

                else:
                    log.error("非法比对函数: {0}".format(compare_item))
                    store_error_code("无法找到对应比对函数{0}".format(compare_item))
                    check_result = False
                    break

    set_global_var("EndTime", datetime.now().strftime('%Y%m%d%H%M%S'), False)
    # 判断返回结果
    return check_result


def compare_response(checks):
    """
    :param checks: str
    :return: bool
    """

    # 定义一个检查标识
    check_result = True

    if checks:
        j = AnalysisJson(get_global_var("ResponseText"))

        try:
            # 如果是匹配完整数据，将json对象转成dict
            checks = json.loads(checks)
            # 字典完整比较
            log.info("期望返回: \n{0}".format(json.dumps(checks, indent=4, ensure_ascii=False)))
            if len(checks.keys()) != len(j.json2dict.keys()):
                log.info("期望值与实际返回keys不相等")
                store_error_code("期望值与实际返回keys不相等！")
            else:
                # 遍历dict找到第一个
                for key, value in checks.items():
                    if value != j.get_value_by_key(key_name=key):
                        check_result = False
                        log.info("Check【{0}: {1}】 , failed".format(key, value))
                        store_error_code("接口返回校验失败！ {0}:{1}".format(key, value))
                        break
                    else:
                        log.info("Check【{0}: {1}】 , pass".format(key, value))

        except JSONDecodeError:
            # 字典关键信息比较
            msg = checks.split(chr(10))
            for item in msg:
                if item.strip() == "":
                    continue
                # patt = r'([a-zA-Z$.]+)\s*:\s*(.+)'
                patt = r'([a-zA-Z0-9$.\[\]]+)\s*:\s*(.+)'
                p = re.match(patt, item)
                if not p:
                    # 判断填写的预期结果是不是key:value格式
                    check_result = False
                    store_error_code("预期返回结果格式错误！ {0}".format(msg))
                    break
                else:
                    key = p[1]
                    value = p[2]
                    actual_value = j.get_value_by_path(jpath=key)
                    # log.info("actual_value: {0}, type: {1}".format(actual_value, type(actual_value)))
                    if actual_value is None:
                        if value.lower() == "null" or value.lower() == "none":
                            log.info("Check【{0}】, pass".format(item))
                        else:
                            # 根据key没有找到相应的值
                            check_result = False
                            store_error_code("接口返回校验失败！ {0}".format(item))
                            break
                    else:
                        if isinstance(actual_value, bool):
                            if value.lower() == "true":
                                value = True
                            elif value.lower() == "false":
                                value = False
                            else:
                                value = value

                            if isinstance(value, bool):
                                if value ^ actual_value:
                                    check_result = False
                                    log.info("Check【{0}】, fail".format(item))
                                    store_error_code("接口返回校验失败！ {0}".format(item))
                                    break
                                else:
                                    log.info("Check【{0}】, pass".format(item))
                            else:
                                check_result = False
                                log.info("Check【{0}】, fail".format(item))
                                store_error_code("接口返回校验失败！ {0}".format(item))
                                break
                        else:
                            if isinstance(actual_value, int):   # 实际值是int
                                if str(actual_value) != value:
                                    check_result = False
                                    log.info("Check【{0}】, fail".format(item))
                                    store_error_code("接口返回校验失败！ {0}".format(item))
                                    break
                                else:
                                    log.info("Check【{0}】, pass".format(item))
                            else:
                                # 实际值是string
                                if actual_value.find(value) == -1:
                                    # 根据key查找到的value不包含预期的value
                                    check_result = False
                                    log.info("Check【{0}】, fail".format(item))
                                    store_error_code("接口返回校验失败！ {0}".format(item))
                                    break
                                else:
                                    log.info("Check【{0}】, pass".format(item))

    set_global_var("EndTime", datetime.now().strftime('%Y%m%d%H%M%S'), False)

    # 判断返回结果
    return check_result
