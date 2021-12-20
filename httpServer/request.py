# -*- encoding: utf-8 -*-
# @Author: peng wei
# @Time: 2021-04-16 11:42

import requests
import json
from json.decoder import JSONDecodeError
from common.variable.global_variable import *
from common.log.logger import log
from httpServer.json_analysis import AnalysisJson


def built(url, method, header, parameter):

    log.info("开始组装http请求信息")

    # 处理请求url
    url = url.strip()
    log.info("Http request url: {0}".format(url))

    # 处理请求方式
    method = method.upper()
    log.info("Http request method: {0}".format(method))

    # 处理请求头，返回字典
    headers = {}
    if isinstance(header, dict):
        headers = header
    else:
        if header.strip():
            tmp = header.split(chr(10))  # 以换行分割请求头
            for item in tmp:
                if not item.strip():
                    continue
                else:
                    _tmp = item.split(":", 1)      # 以:分割每一行请求头
                    headers[_tmp[0]] = _tmp[1].strip()
    log.info("Http request header: {0}".format(headers))

    # 处理请求参数，返回json或表单
    param_json = {}
    param_form = ""
    param_type = 0      # 0: json; 1: form; 2: other
    if isinstance(parameter, dict):
        data = json.dumps(parameter)
    else:
        if parameter is not None and parameter.strip():
            try:
                parameter = json.loads(parameter)
                data = json.dumps(parameter, ensure_ascii=False)
            except JSONDecodeError:
                tmp = parameter.split(chr(10))       # 以换行分割参数
                for item in tmp:
                    if not item.strip():
                        continue
                    else:
                        patt1 = r'([a-zA-Z]+)\s*:\s*(.+)'
                        patt2 = r'([a-zA-Z]+)\s*=\s*(.+)'
                        p1 = re.match(patt1, item)
                        p2 = re.match(patt2, item)
                        if p1:     # json
                            param_type = 0
                            # param_json[p1[1]] = p1[2].strip()
                            try:
                                v = json.loads(p1[2].strip())
                            except:
                                v = p1[2].strip()
                            param_json[p1[1]] = v
                        elif p2:
                            param_type = 1
                            if param_form == "":
                                param_form = p2[1].strip() + "=" + p2[2].strip()
                            else:
                                param_form = param_form + "&" + p2[1].strip() + "=" + p2[2].strip()
                        else:
                            param_type = 2
                if param_type == 0:
                    data = json.dumps(param_json, ensure_ascii=False)
                elif param_type == 1:
                    data = param_form
                else:
                    data = None
        else:
            data = None
    log.info("Http request data: {0}".format(data))

    return url, method, headers, data


def send(url, method, header=None, data=None):

    log.info("发送http请求...")
    if data is not None:
        data = data.encode("utf-8").decode("latin1")

    # 请求方式为GET
    if method.upper() == "GET":
        response = requests.get(url, headers=header, verify=False, timeout=30)

    # 请求方式为POST
    elif method.upper() == "POST":
        response = requests.post(url, data=data, headers=header, verify=False, timeout=600)

    # 请求方式为PUT
    elif method.upper() == "PUT":
        response = requests.put(url, data=data, headers=header, verify=False, timeout=30)

    # 请求方式为DELETE
    elif method.upper() == "DELETE":
        response = requests.delete(url, headers=header, verify=False, timeout=30)

    # 请求方式为PATCH
    elif method.upper() == "PATCH":
        response = requests.patch(url, data=data, headers=header, verify=False, timeout=30)

    else:
        log.error("Unsupported httpServer method: {0}".format(method))
        return False

    # 查看响应内容，response.text 返回的是Unicode格式的数据
    log.info("收到Response响应text: {0}".format(response.text.strip()))

    # 查看响应内容，response.content返回的字节流数据
    # log.info(response.content)

    # 查看完整url地址
    # log.info(response.url)

    # 查看响应头部字符编码
    # log.info(response.encoding)

    # 查看响应码
    log.info("Response status_code: {0}".format(response.status_code))

    # 判断结果码，返回结果码和响应内容
    if response.status_code != 200 and response.status_code != 204:
        log.error('{0} response code: {1}'.format(method.upper(), response.status_code))
    set_global_var("ResponseCode", response.status_code, False)
    set_global_var("ResponseText", response.text, False)
    response_obj = AnalysisJson(response.text)
    if response_obj.get_value_by_key("authorization"):
        set_global_var("Authorization", response_obj.get_value_by_key("authorization"))
        log.info("Authorization更新: {}".format(get_global_var("Authorization")))
    return True
