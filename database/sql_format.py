# -*- encoding: utf-8 -*-
# @Author: peng wei
# @Time: 2020-09-25 15:41

from common.variable.global_variable import *


def get_sql(database_type, source_data, table_name):
    """
    :param database_type: 数据库类型
    :param source_data: 原始数据
    :param table_name: 表名
    """
    data = source_data.split("|")
    column = ""
    fetch = False
    first_add_column_flag = True
    where_condition = "1 = 1"
    for i in range(len(data))[::2]:
        # 组装结果列
        if first_add_column_flag:
            if data[i].upper().find("_TIME") > -1 or data[i].upper().find("_DATE") > -1:
                if database_type == "mysql":
                    tmp = "CAST({0} AS CHAR) AS {0}".format(data[i], data[i])
                else:
                    tmp = data[i]
            else:
                tmp = data[i]
            column = tmp
            first_add_column_flag = False
        else:
            if data[i].upper().find("_TIME") > -1 or data[i].upper().find("_DATE") > -1:
                if database_type == "mysql":
                    tmp = "CAST({0} AS CHAR) AS {0}".format(data[i], data[i])
                else:
                    tmp = data[i]
                column = column + ', ' + tmp
            else:
                if data[i] == "FetchID":        # FetchID|script_id
                    fetch = data[i+1]
                    set_global_id(data[i+1])
                else:
                    tmp = data[i]
                    column = column + ', ' + tmp

        # 组装where条件
        if data[i] == "FetchID":       # 获取FetchID对应列名的值，一般为id，这一对不组装到sql中
            pass
        else:
            if data[i+1].lower() == "null":      # 对于空值处理
                where_condition += " and {0} is Null".format(data[i])
            elif data[i+1].lower() == "now":   # 表示是本次用例执行期间的时间，需要借助StartTime和EndTime区间来判断
                if database_type in ["oracle", "postgres"]:
                    where_condition += " and to_char({0}, 'yyyymmddhh24miss') between '{1}' and '{2}'".format(
                        data[i], get_global_var("StartTime"), get_global_var("EndTime"))
                else:
                    where_condition += " and {0} between '{1}' and '{2}'".format(
                        data[i], get_global_var("StartTime"), get_global_var("EndTime"))
            elif data[i+1].lower() == "notnull":
                where_condition += " and {0} is not Null".format(data[i])
            elif data[i+1].lower().startswith("contains"):      # 包含
                s = data[i+1][9: len(data[i+1])-1]
                item = s.split("&&")
                for k in item:
                    if database_type == "postgres":
                        if k.find("\\") > -1:
                            where_condition += " and {0} like E'%{1}%'".format(data[i], k.strip())
                        else:
                            where_condition += " and {0} like '%{1}%'".format(data[i], k.strip())
                    else:
                        where_condition += " and {0} like '%{1}%'".format(data[i], k.strip())
            else:
                if database_type == "postgres":
                    if data[i + 1].find("\\") > -1:
                        where_condition += " and {0} = E'{1}'".format(data[i], data[i + 1])
                    else:
                        where_condition += " and {0} = '{1}'".format(data[i], data[i + 1])
                else:
                    where_condition += " and {0} = '{1}'".format(data[i], data[i + 1])

    # 将FetchID对应列放在最后，便于数组取值
    if fetch:
        column = column + ', ' + fetch
    sql = "select {0} from {1} where {2}".format(column, table_name, where_condition)
    result = {
        "column": column,
        "sql": sql
    }

    return result
