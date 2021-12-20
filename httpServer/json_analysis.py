# -*- encoding: utf-8 -*-
# @Author: peng wei
# @Time: 2021-04-23 14:13

import json
import re
from jsonpath import jsonpath
from common.log.logger import log


class AnalysisJson:

    def __init__(self, obj):
        """
        :param obj: json
        """
        # 将json对象转成dict
        self.json2dict = json.loads(obj)

    def get_value_by_key(self, key_name, dict_obj=None):
        """
        :param key_name: key
        :param dict_obj: dict
        :return: 只要找到1个，就返回value，不再继续查找；否则返回None
        """

        if dict_obj is None:
            dict_obj = self.json2dict

        if isinstance(dict_obj, dict):
            for key, value in dict_obj.items():
                if key_name == key:
                    return value
                else:
                    if isinstance(value, dict) or isinstance(value, list):
                        result = self.get_value_by_key(dict_obj=value, key_name=key_name)
                        if result:
                            return result
        elif isinstance(dict_obj, list):
            # 如果子节点是数组，循环数组
            for child in dict_obj:
                if isinstance(child, dict) or isinstance(child, list):
                    result = self.get_value_by_key(dict_obj=child, key_name=key_name)
                    if result:
                        return result

    def get_values_by_key(self, key_name, dict_obj=None):
        """
        未完
        :param key_name:
        :param dict_obj:
        :return: 返回所有找到的value
        """

        if dict_obj is None:
            dict_obj = self.json2dict

        # 定义取值列表
        value_list = []

        if isinstance(dict_obj, dict):
            for key, value in dict_obj.items():
                if key_name == key:
                    value_list.append(value)
                else:
                    if isinstance(value, dict) or isinstance(value, list):
                        result = self.get_value_by_key(dict_obj=value, key_name=key_name)
                        if result:
                            return result
        elif isinstance(dict_obj, list):
            # 如果子节点是数组，循环数组
            for child in dict_obj:
                if isinstance(child, dict) or isinstance(child, list):
                    result = self.get_value_by_key(dict_obj=child, key_name=key_name)
                    if result:
                        return result

    def get_value_by_path(self, jpath):
        """
        通过jsonpath的方式，层级深入遍历dict
        :param jpath: $或$.a.b.c，每个xpath只能对应一个子节点
                    如果子节点是数组，需要深入数组查找
        :return: 根据子节点深入遍历json，找到则返回value，否则返回None
        """
        global value
        if jpath == "$":
            value = self.json2dict
        else:
            flag = True
            child_tmp = []
            obj = self.json2dict
            while flag:
                # log.info("jpath: {}".format(jpath))
                value = jsonpath(obj, jpath)     # jsonpath 找不到会返回false
                if value is False:
                    # 如果为false，退回到上一个节点
                    p = jpath.rindex(".")
                    child_tmp.append(jpath[p+1:])
                    jpath = jpath[0: p]
                    if jpath == "$":
                        flag = False
                else:
                    if isinstance(value, list):
                        value = value[0]
                    # log.info("value: {}".format(value))
                    # log.info("child_tmp: {}".format(child_tmp))
                    # 如果找到，需要判断child_tmp是否为空，不为空需要进入child_tmp中的子节点继续
                    if len(child_tmp) == 0:
                        flag = False
                    else:
                        if isinstance(value, list):
                            # 父节点不加索引，则根据子节点的索引确定，索引从0开始
                            patt = r'[A-Za-z0-9]+(\[\d+\])?'
                            # 由于加入到child_tmp的元素是倒序，所以根据child_tmp最后一个元素的索引来决定取value的第几个元素作为根节点
                            first_child_index = re.match(patt, child_tmp[-1]).group(1)
                            if first_child_index is None:
                                # 如果子节点后不带[1]类似的，则默认取第一个
                                index = 0
                            else:
                                child_index = re.match(r'\[(\d+)\]', first_child_index).group(1)
                                child_tmp[-1] = child_tmp[-1].replace(first_child_index, "")
                                # 使用指定序号（从1开始）
                                index = int(child_index)
                            obj = value[index]
                        elif isinstance(value, dict):
                            # 父节点加了索引，则获取对应索引下的子节点，子节点不需要带索引，索引从0开始
                            patt = r'([A-Za-z0-9]+)\[\d+\]'
                            child_name = re.match(patt, child_tmp[-1]).group(1)
                            if child_name:
                                child_tmp[-1] = child_name
                            obj = value
                        # log.info("obj: {}".format(obj))
                        # 重新设置新的path
                        tmp = child_tmp
                        tmp.reverse()
                        jpath = "$." + ".".join(tmp)
                        child_tmp.pop()
        return value


if __name__ == "__main__":
    test_dict = {
        "success": True,
        "message": "查询成功！",
        "data": {
            "baseinfo": [
                {
                    "result": "ok",
                    "step": 1,
                    "expdesc": "初始化浏览器驱动"
                },
                {
                    "result": "ok",
                    "step": 2,
                    "expdesc": "打开首页:http://192.168.88.116:9100/AiSee/html/portal/portal.html"
                }
            ],
            "opts": [
                {
                    "result": "ok",
                    "step": 1,
                    "expdesc": "休眠:休眠5秒，循环次数【1】休眠时间【5】秒"
                },
                {
                    "result": "ok",
                    "step": 2,
                    "expdesc": "单击:点击核心网:/html/body/div[1]/div/div[3]/div/div/div[1]/div[1]/img"
                },
                {
                    "result": "ok",
                    "step": 3,
                    "expdesc": "休眠:休眠5秒，循环次数【1】休眠时间【5】秒"
                },
                {
                    "result": "ok",
                    "step": 4,
                    "expdesc": "单击:点击常用信息管理://span[text()='常用信息管理']"
                },
                {
                    "result": "ok",
                    "step": 5,
                    "expdesc": "单击:点击文件目录管理://span[text()='文件目录管理']"
                },
                {
                    "result": "ok",
                    "step": 6,
                    "expdesc": "单击:点击个人目录://span[text()='个人目录']"
                },
                {
                    "result": "ok",
                    "step": 7,
                    "expdesc": "跳转iframe:跳转iframe://iframe[@src='/VisualModeler/html/commonInfo/catalogPersonalDef.html']"
                },
                {
                    "result": "false",
                    "step": 8,
                    "expdesc": "element not interactable\n  (Session info: chrome=78.0.3904.108)\nBuild info: version: 'unknown', revision: 'unknown', time: 'unknown'\nSystem info: host: 'qa-aisee-app-v3-b1-3.novalocal', ip: '192.168.88.49', os.name: 'Linux', os.arch: 'amd64', os.version: '3.10.0-1062.9.1.el7.x86_64', java.version: '1.8.0_121'\nDriver info: org.openqa.selenium.chrome.ChromeDriver\nCapabilities {acceptInsecureCerts: false, browserName: chrome, browserVersion: 78.0.3904.108, chrome: {chromedriverVersion: 78.0.3904.70 (edb9c9f3de024..., userDataDir: /tmp/.com.google.Chrome.HnS0xu}, goog:chromeOptions: {debuggerAddress: localhost:34299}, javascriptEnabled: true, networkConnectionEnabled: false, pageLoadStrategy: normal, platform: LINUX, platformName: LINUX, proxy: Proxy(), setWindowRect: true, strictFileInteractability: false, timeouts: {implicit: 0, pageLoad: 300000, script: 30000}, unhandledPromptBehavior: accept}\nSession ID: 9a3b0d81dd2cf78c458f3d81b7ab9301"
                }
            ],
            "login": [
                {
                    "result": "ok",
                    "step": 1,
                    "expdesc": "用户名:pw，userId"
                },
                {
                    "result": "ok",
                    "step": 2,
                    "expdesc": [
                        {
                            "aaa": 1
                        },
                        {
                            "aaa": 2
                        },
                        {
                            "aaa": 3
                        }
                    ]
                },
                {
                    "result": "ok",
                    "step": 3,
                    "expdesc": "单击登录按钮:loginButton"
                }
            ]
        },
        "msg": "查询成功！",
        "code": "200000",
        "sn": None
    }

    dict2json = json.dumps(test_dict)
    j = AnalysisJson(dict2json)
    result = j.get_value_by_path("$.data.login[1].expdesc.aaa[2]")
    log.info("找到结果: {}".format(result))