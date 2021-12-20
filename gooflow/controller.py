import xlrd
import xlwt
from xlutils.copy import copy
from datetime import datetime
from time import sleep
from gooflow.caseWorker import CaseWorker
from config.loads import properties
from common.log.logger import log


def case_run(filenum, rownum):

    # 根据当前测试应用名，打开相应的测试用例集
    application = properties.get("application")
    if application is None:
        raise Exception("!!! application未设置.")
    path = properties.get("testCaseControllerPath") + application + "/controller.xls"
    log.info("打开{0},开始获取测试用例文件名".format(path))
    # 打开excel，formatting_info=True保留Excel当前格式
    rbook = xlrd.open_workbook(path, formatting_info=True)

    wbook = copy(rbook)

    rsheets = rbook.sheet_by_name('Sheet1')
    wsheets = wbook.get_sheet(0)
    nrows = rsheets.nrows

    row_num = filenum
    str1 = rsheets.cell(row_num, 0).value
    str2 = rsheets.cell(row_num, 1).value

    while len(str1) > 0:

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

        if not str2 or str2 == "否":
            log.info("用例文件{0}已设置不执行，跳过.".format(str1))
            wsheets.write(row_num, 2, "NO TEST", style1)
            wsheets.write(row_num, 3, "")
            wsheets.write(row_num, 4, "")
            row_num += 1
            if row_num < nrows:
                str1 = rsheets.cell(row_num, 0).value
                str2 = rsheets.cell(row_num, 1).value
            else:
                break
        else:
            str1 = rsheets.cell(row_num, 0).value
            start_time = datetime.now().strftime('%Y%m%d%H%M%S')
            wsheets.write(row_num, 2, "RUNNING", style2)
            wsheets.write(row_num, 3, start_time)
            wsheets.write(row_num, 4, "")
            wbook.save(path)

            filename = properties.get("testCasePath") + application + "/" + str1
            log.info("获取到测试用例文件：{0}".format(filename))
            action = CaseWorker(case_path=filename)
            result = action.worker(row_num=rownum)

            if result:
                style = style1
                status = "PASS"
            else:
                style = style0
                status = "FAIL"
            end_time = datetime.now().strftime('%Y%m%d%H%M%S')
            wsheets.write(row_num, 2, status, style)
            wsheets.write(row_num, 4, end_time)
            wbook.save(path)
            if not result:
                break
            else:
                rownum = 1
                row_num += 1
                if row_num == nrows:
                    break
                else:
                    sleep(3)
                    str1 = rsheets.cell(row_num, 0).value
                    str2 = rsheets.cell(row_num, 1).value
    log.info("----------------------本测试执行完成----------------------")
