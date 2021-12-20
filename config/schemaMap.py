# -*- encoding: utf-8 -*-
# @Author: peng wei
# @Time: 2021/11/16 下午5:22

from config.loads import properties


def get_schema(schema):
    if properties.get("environment") == "v3.maria":
        # 9100
        schema_map = {
            "main": "aisee1",
            "sso": "sso",
            "nu": "nu",
            "dashboard": "dashboard"
        }
    elif properties.get("environment") == "gmcc.oracle":
        # 9990
        schema_map = {
            "main": "gd_gz",
            "sso": "sso",
            "nu": "nu",
            "dashboard": "dashboard"
        }
    elif properties.get("environment") == "v31.postgres":
        # 9312
        schema_map = {
            "main": "aisee1",
            "sso": "sso",
            "webapi": "webapi",
            "dashboard": "dashboard"
        }
    else:
        # 默认
        schema_map = {
            "main": "aisee1",
            "sso": "sso",
            "nu": "nu",
            "webapi": "webapi",
            "dashboard": "dashboard"
        }

    return schema_map.get(schema)
