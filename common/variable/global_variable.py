# -*- encoding: utf-8 -*-
# @Author: peng wei
# @Time: 2021/7/20 上午10:27

import re

global_set = {
    "short_term": {},
    "long_term": {}
}

globalId = ""


def init_global_var():
    global global_set
    global_set["short_term"] = {}
    global_set["long_term"] = {}


def set_global_var(key, value, always_effective=True):
    """
    将运行过程中需要的变量分别存入 global_set 的short_term或long_term
    :param key: 变量名
    :param value: 变量值
    :param always_effective: 是否长期有效，默认是
    :return:
    """
    global global_set
    s = global_set["short_term"]
    l = global_set["long_term"]
    if always_effective:
        if s.__contains__(key):
            s.pop(key)
        l.update({key: value})
    else:
        if l.__contains__(key):
            l.pop(key)
        s.update({key: value})
    # log.debug("添加全局变量：{0}，长期生效：{1}，变量值：{2}".format(key, always_effective, value))
    # log.info("当前全局变量: {}".format(global_set))


def clear_process_var():
    """
    # 在每条测试用例执行之前，清空过程变量，即short_term
    :return:
    """
    global global_set
    global_set["short_term"] = {}


def get_global_var(var_name):
    """
    :param var_name: 根据变量名，返回变量值
    :return:
    """
    global global_set
    result = None
    if global_set.get("long_term").__contains__(var_name):
        result = global_set.get("long_term").get(var_name)
    elif global_set.get("short_term").__contains__(var_name):
        result = global_set.get("short_term").get(var_name)
    if isinstance(result, int):
        result = str(result)
    return result


def get_global_var_names():
    """
    :return: 返回所有变量名list
    """
    global global_set
    var_names = []
    for key in global_set.get("long_term"):
        var_names.append(key)
    for key in global_set.get("short_term"):
        var_names.append(key)
    return var_names


def set_global_id(value):
    global globalId
    if isinstance(value, str):
        tmp1 = value.split("_")     # 将变量以_分割
        tmp2 = ""
        for i in tmp1:
            # 将分割后首字母转成大写，特殊：id转成ID
            if i == "id":
                tmp2 += "ID"
            else:
                tmp2 += i[0].upper() + i[1:].lower()
        globalId = tmp2
    else:
        raise KeyError("globalId只支持字符串")


def replace_global_var(obj):
    """
    使用全局变量的value，替换${xxx}这样的内容
    :param obj: 待替换的内容
    :return:
    """
    global global_set
    for var in get_global_var_names():
        patt = r'\$\{%s\}' % var
        if re.search(patt, obj):
            obj = re.sub(r'\$\{%s\}' % var, get_global_var(var), obj)
    return obj


def get_global_id():
    global globalId
    return globalId
