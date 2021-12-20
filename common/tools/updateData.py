# -*- encoding: utf-8 -*-
# @Author: peng wei
# @Time: 2021/11/16 下午5:30

import json
from json.decoder import JSONDecodeError
from common.log.logger import log


def update_json(obj, new_dict):
    """
    :param obj: json对象
    :param new_dict: dict，要更新的内容
    :return: 返回替换后的完整json

    {
        "attach_content": {
            "ftp_server_cfg_id": "f01d8cda-e5ed-48cf-bd19-5116b9d6087a",
            "catalog_path": "/pw",
            "catalog_isKeyword": "0",
            "file": "",
            "fileType": "csv",
            "file_choose_type": "1",
            "file_regex_templ_id": "4771FAD2-BA97-4857-A72E-8EF3D912EC50",
            "file_regex_expr": "",
            "file_regex_json": ""
        },
        "attach_source": "4"
    }
    """
    try:
        json2dict = json.loads(obj)

        def round_dict(d):
            # log.info("d: {}".format(d))
            if isinstance(d, dict):
                for x in range(len(d)):
                    temp_key = list(d.keys())[x]
                    temp_value = d[temp_key]
                    # log.info("temp_key: {}".format(temp_key))
                    # log.info("temp_value: {}".format(temp_value))
                    if temp_key == list(new_dict.keys())[0]:
                        log.info("找到key：{}".format(temp_key))
                        d.update(new_dict)
                        break
                    else:
                        round_dict(temp_value)

        round_dict(json2dict)
        return json.dumps(json2dict)
    except JSONDecodeError as e:
        raise e


def update_dict(obj, key, value):

    # 定义输出结果，默认为初始值
    replace_result = obj

    if obj.__contains__(key):
        obj[key] = value
    else:
        # 遍历每个key对应的value，从value继续寻找key
        for _key, _value in obj.items():
            if type(_value).__name__ != "dict":
                pass
            else:
                # 循环调用自身
                update_dict(obj=_value, key=key, value=value)
    return replace_result
