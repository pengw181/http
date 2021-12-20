# -*- encoding: utf-8 -*-
# @Author: peng wei
# @Time: 2021/7/20 上午10:43

import json
import xlrd
import xlwt
from xlutils.copy import copy
from gooflow.precondition import preconditions
from httpServer.request import built, send
from gooflow.compares import compare_data, compare_response
from common.variable.global_variable import *
from config.loads import properties
from datetime import datetime
from gooflow.initiation import init
from common.log.logger import log
from time import sleep


class CaseWorker:

    def __init__(self, case_path, sheet_index=0):

        self.path = case_path
        self.successNum = 0
        self.failNum = 0
        self.skipNum = 0
        self.to_end = False

        # 打开excel，formatting_info=True保留Excel当前格式
        self.rbook = xlrd.open_workbook(self.path, formatting_info=True)

        self.wbook = copy(self.rbook)

        self.rsheets = self.rbook.sheet_by_index(sheet_index)
        self.wsheets = self.wbook.get_sheet(0)

        self.nrows = self.rsheets.nrows
        self.ncols = self.rsheets.ncols
        log.info("Excel行数：{0}, 列数 : {1}".format(self.nrows, self.ncols))
        log.info('-------------------------------------------------------------------------')

    def column_definition(self, row_num):

        column = []
        # 用例名称
        case_name = self.rsheets.cell(row_num, 0).value
        column.append(case_name)

        # 用例级别
        case_level = self.rsheets.cell(row_num, 1).value
        column.append(case_level)

        # 前置条件
        prediction = self.rsheets.cell(row_num, 2).value
        column.append(prediction)

        # 请求url
        req_url = self.rsheets.cell(row_num, 3).value
        column.append(req_url)

        # 请求方式
        req_method = self.rsheets.cell(row_num, 4).value
        column.append(req_method)

        # 请求头
        req_header = self.rsheets.cell(row_num, 5).value
        column.append(req_header)

        # 请求参数
        req_param = self.rsheets.cell(row_num, 6).value
        column.append(req_param)

        # 返回结果类型
        resp_type = self.rsheets.cell(row_num, 7).value
        column.append(resp_type)

        # 预期结果
        resp_compare = self.rsheets.cell(row_num, 8).value
        column.append(resp_compare)

        # 数据比对
        data_compare = self.rsheets.cell(row_num, 9).value
        column.append(data_compare)

        return column

    def worker(self, row_num=1):

        if row_num <= (self.nrows - 1):
            current_column = self.column_definition(row_num)
        else:
            log.info("指定执行行号{0}, 已超过最大行数，不执行.".format(row_num))
            return False

        case_name = current_column[0]
        while len(case_name.strip()) > 0:

            # 定义字体类型1. 字体：红色
            font0 = xlwt.Font()
            font0.colour_index = 2
            font0.bold = True

            style0 = xlwt.XFStyle()
            style0.font = font0

            # 定义字体类型2. 字体：蓝色
            font1 = xlwt.Font()
            font1.colour_index = 4
            font1.bold = True

            style1 = xlwt.XFStyle()
            style1.font = font1

            # 定义字体类型3. 字体：绿色
            font2 = xlwt.Font()
            font2.colour_index = 3
            font2.bold = True

            style2 = xlwt.XFStyle()
            style2.font = font2

            # 设置单元格自动换行
            style3 = xlwt.XFStyle()
            style3.alignment.wrap = 1

            log.info(">>>>> %s" % case_name)

            if case_name.find("UNTEST") > -1:  # 本行不执行
                self.wsheets.write(row_num, 10, "")
                self.wsheets.write(row_num, 11, "NO TEST", style0)
                self.wsheets.write(row_num, 12, "")
                self.wsheets.write(row_num, 13, "")
                self.wsheets.write(row_num, 14, "")
                self.wbook.save(self.path)
                row_num += 1
                self.skipNum += 1
                # 重新获取新一行的用例
                current_column = self.column_definition(row_num)
                case_name = current_column[0]
                log.info("本行用例不执行，跳过\n")
            else:
                if properties.get("runAllTest"):
                    pass
                else:
                    # 判断当前测试用例的级别是否在测试范围内
                    if current_column[1] in properties.get("runTestLevel"):
                        pass
                    else:
                        self.skipNum += 1
                        self.wsheets.write(row_num, 10, "")
                        self.wsheets.write(row_num, 11, "NO TEST", style0)
                        self.wsheets.write(row_num, 12, "")
                        self.wsheets.write(row_num, 13, "")
                        self.wsheets.write(row_num, 14, "")
                        self.wbook.save(self.path)
                        row_num += 1
                        log.info("本行用例级别较低，不执行，跳过")

                        if row_num <= (self.nrows - 1):
                            # 重新获取新一行的用例
                            current_column = self.column_definition(row_num)
                            continue
                        else:  # 执行完最后一条用例，跳出循环，打印执行结果。
                            break

                self.wsheets.write(row_num, 10, "")
                self.wsheets.write(row_num, 11, "RUNNING", style2)
                self.wsheets.write(row_num, 12, "")
                self.wsheets.write(row_num, 13, "")
                self.wsheets.write(row_num, 14, "")
                self.wbook.save(self.path)

                # 开始测试前，做初始工作
                init()

                # 执行前置条件
                set_global_var("StartTime", datetime.now().strftime('%Y%m%d%H%M%S'), False)
                result = preconditions(action=current_column[2])
                if not result:
                    log.info("错误信息: {0}".format(get_global_var("ErrorMsg")))
                    log.error("第{0}行用例执行不通过,预置条件执行失败.\n".format(row_num))
                    self.wsheets.write(row_num, 10, "")
                    self.wsheets.write(row_num, 11, "FAIL", style0)
                    self.wsheets.write(row_num, 12, get_global_var("ErrorMsg"))
                    self.wsheets.write(row_num, 13, get_global_var("StartTime"))
                    self.wsheets.write(row_num, 14, get_global_var("EndTime"))
                    self.wbook.save(self.path)
                    self.failNum += 1
                    if properties.get("continueRunWhenError"):
                        row_num += 1
                        if row_num <= (self.nrows - 1):
                            # 重新获取新一行的用例
                            current_column = self.column_definition(row_num)
                            case_name = current_column[9]
                        else:  # 执行完最后一条用例，跳出循环，打印执行结果。
                            break
                        continue
                    else:
                        break

                # 组装http
                req_url = current_column[3]
                req_method = current_column[4]
                req_header = current_column[5]
                req_param = current_column[6]
                # 替换变量
                req_url = replace_global_var(req_url)
                req_header = replace_global_var(req_header)
                req_param = replace_global_var(req_param)
                url, method, headers, data = built(
                    url=req_url, method=req_method, header=req_header, parameter=req_param)

                # 发送http请求
                result = send(url, method, headers, data)
                # 将接口返回存入"接口返回"列
                response_text = json.dumps(json.loads(get_global_var("ResponseText")), indent=4, ensure_ascii=False)
                self.wsheets.write(row_num, 10, response_text, style3)
                self.wbook.save(self.path)
                if not result:
                    log.info("错误信息: {0}".format(get_global_var("ErrorMsg")))
                    log.error("第{0}行用例执行不通过,操作步骤执行失败.".format(row_num))
                    self.wsheets.write(row_num, 11, "FAIL", style0)
                    self.wsheets.write(row_num, 12, get_global_var("ErrorMsg"))
                    self.wsheets.write(row_num, 13, get_global_var("StartTime"))
                    self.wsheets.write(row_num, 14, get_global_var("EndTime"))
                    self.wbook.save(self.path)
                    self.failNum += 1
                    if properties.get("continueRunWhenError"):
                        row_num += 1
                        if row_num <= (self.nrows - 1):
                            # 重新获取新一行的用例
                            current_column = self.column_definition(row_num)
                            case_name = current_column[0]
                        else:  # 执行完最后一条用例，跳出循环，打印执行结果。
                            break
                        continue
                    else:
                        break

                # 比对http返回结果
                resp_check = current_column[8]
                result = compare_response(resp_check)
                if result:
                    pass
                else:
                    log.info("错误信息: {0}".format(get_global_var("ErrorMsg")))
                    log.error("第{0}行用例执行不通过,http返回结果比对失败.".format(row_num))
                    self.wsheets.write(row_num, 11, "FAIL", style0)
                    self.wsheets.write(row_num, 12, get_global_var("ErrorMsg"), style3)
                    self.wsheets.write(row_num, 13, get_global_var("StartTime"))
                    self.wsheets.write(row_num, 14, get_global_var("EndTime"))
                    self.wbook.save(self.path)
                    self.failNum += 1
                    log.info("！！！警告：此条测试用例执行失败！\n")
                    if properties.get("continueRunWhenError"):
                        row_num += 1
                        if row_num <= (self.nrows - 1):
                            # 重新获取新一行的用例
                            current_column = self.column_definition(row_num)
                            case_name = current_column[0]
                        else:  # 执行完最后一条用例，跳出循环，打印执行结果。
                            break
                        continue
                    else:
                        break

                # 结果校验
                data_check = current_column[9]
                result = compare_data(data_check)
                if result:
                    self.wsheets.write(row_num, 11, "PASS", style1)
                    self.wsheets.write(row_num, 12, "")
                    self.wsheets.write(row_num, 13, get_global_var("StartTime"))
                    self.wsheets.write(row_num, 14, get_global_var("EndTime"))
                    self.wbook.save(self.path)
                    self.successNum += 1
                    log.info("第{0}行用例执行成功！".format(row_num))
                    log.info("已经成功执行{0}条用例！\n".format(self.successNum))
                else:
                    log.info("错误信息: {0}".format(get_global_var("ErrorMsg")))
                    log.error("第{0}行用例执行不通过,结果比对失败.".format(row_num))
                    self.wsheets.write(row_num, 11, "FAIL", style0)
                    self.wsheets.write(row_num, 12, get_global_var("ErrorMsg"), style3)
                    self.wsheets.write(row_num, 13, get_global_var("StartTime"))
                    self.wsheets.write(row_num, 14, get_global_var("EndTime"))
                    self.wbook.save(self.path)
                    self.failNum += 1
                    log.info("！！！警告：此条测试用例执行失败！\n")
                    if properties.get("continueRunWhenError"):
                        row_num += 1
                        if row_num <= (self.nrows - 1):
                            # 重新获取新一行的用例
                            current_column = self.column_definition(row_num)
                            case_name = current_column[0]
                        else:  # 执行完最后一条用例，跳出循环，打印执行结果。
                            break
                        continue
                    else:
                        break

                # 预置条件、操作步骤、比对结果完成后进行操作
                row_num += 1
                self.wbook.save(self.path)
                if row_num <= (self.nrows-1):
                    # 重新获取新一行的用例
                    current_column = self.column_definition(row_num)
                    case_name = current_column[0]
                else:       # 执行完最后一条用例，跳出循环，打印执行结果。
                    break

        log.info("本用例集全部用例执行完成。执行结果：")
        log.info("执行成功数 | %d |" % self.successNum)
        log.info("执行失败数 | %d |" % self.failNum)
        log.info("跳过用例数 | %d |\n" % self.skipNum)
        self.to_end = True
        return False if self.failNum > 0 else True
