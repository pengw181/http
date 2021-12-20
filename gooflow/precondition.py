from time import sleep
from datetime import datetime
from database.SQLHelper import SQLUtil
from gooflow.codes import store_error_code
from common.variable.global_variable import *
from common.tools.updateData import update_json
from common.log.logger import log
from config.loads import db_config
from httpServer.request import built, send
from config.schemaMap import get_schema


def preconditions(action):
    """
    :param action: 可以设置全局变量，可以执行sql
    :return: 执行结果，true/false
    """

    # 多条sql语句按换行分隔
    pre_list = action.split(chr(10))
    run_flag = False

    if len(pre_list) == 0:  # 预置条件为空
        run_flag = True
    else:
        # 预置条件不为空，拆成多条执行
        for i in range(len(pre_list)):
            if pre_list[i] != "":
                # 替换${Database}变量
                pre_list[i] = replace_global_var(pre_list[i])
                if pre_list[i].lower().startswith("global"):
                    # 变量赋值，加入到global_set
                    log.info("开始设置全局变量：{0}".format(pre_list[i]))
                    try:
                        var_set = pre_list[i].split("|", 2)
                        set_global_var(var_set[1].strip(), var_set[2].strip())
                        run_flag = True
                    except Exception:
                        run_flag = False
                elif pre_list[i].lower().startswith("updatejson"):
                    # 更新json字段的值
                    try:
                        each_pre = pre_list[i].split("|", 3)
                        json_obj = replace_global_var(each_pre[1])
                        key = each_pre[2]
                        value = each_pre[3]
                        log.info("key: {}".format(key))
                        log.info("value: {}".format(value))
                        log.info("开始更新json：{0}".format(json_obj))
                        json_obj = update_json(json_obj, {key: value})
                        log.info("更新json成功，更新后为：{}".format(json_obj))
                        set_global_var(str(each_pre[1])[2:-1], json_obj, False)
                        run_flag = True
                    except Exception:
                        log.error("json更新异常")
                        run_flag = False
                elif pre_list[i].startswith("apiInit"):
                    # WebApi业务刷新接口，当数据库变更后，需要刷新
                    log.info("开始调用业务刷新接口")
                    req_url = get_global_var("SystemUrl") + "/WebAPI/restful/init/apiInit?apiInitPwd={}".format(
                        get_global_var("ApiInitPwd"))
                    req_header = {"Content-Type": "application/json"}
                    url, method, headers, data = built(url=req_url, method='POST', header=req_header, parameter=None)
                    run_flag = send(url, method, headers, data)
                    log.info("调用业务刷新接口结束，调用结果: {}".format(run_flag))
                    sleep(2)
                elif pre_list[i].startswith("wait"):
                    # 等待
                    each_pre = pre_list[i].split('|')
                    wait_time = int(each_pre[1])
                    log.info("等待{}秒".format(wait_time))
                    sleep(wait_time)
                    run_flag = True
                elif pre_list[i].startswith(get_global_var("Database")):
                    this_pre_action = pre_list[i]
                    each_pre = this_pre_action.split('|')
                    # 数据库操作
                    db = get_global_var("Database")
                    if db_config.get(db):
                        # 如果db.ini已配置数据库信息
                        schema = str(each_pre[0])[len(db)+1:]
                        sql = each_pre[1]
                        # 替换变量
                        sql = replace_global_var(sql)
                        log.info("{0}【{1}】执行sql语句：{2}".format(db, get_schema(schema), sql))
                        sql_util = SQLUtil(db=db, schema=schema)
                        if sql.find("select") == 0 or sql.find("SELECT") == 0:      # 查询
                            sql_result = sql_util.select(sql)
                        else:   # 修改或删除
                            sql_result = sql_util.update(sql)
                        log.info("成功执行sql语句：{}".format(sql))
                        # 将第3个参数加入全局变量字典
                        if len(each_pre) > 2:
                            if isinstance(sql_result, str):
                                set_global_var(each_pre[2], sql_result)
                                log.info("给变量{0}赋值：{1}".format(each_pre[2], sql_result))
                        run_flag = True
                    else:
                        raise KeyError("db.ini未配置对应数据库信息，请检查")
                else:
                    each_pre = pre_list[i].split('|')
                    try:
                        # 对特定数据库做操作
                        db_tmp = each_pre[0].split(".", 2)
                        db = db_tmp[0] + '.' + db_tmp[1]
                        schema = db_tmp[2]
                        if db_config.get(db):
                            sql = each_pre[1]
                            # 替换变量
                            sql = replace_global_var(sql)
                            log.info("{0}【{1}】执行sql语句：{2}".format(db, get_schema(schema), sql))
                            sql_util = SQLUtil(db=db, schema=schema)
                            if sql.find("select") == 0 or sql.find("SELECT") == 0:  # 查询
                                sql_result = sql_util.select(sql)
                            else:  # 修改或删除
                                sql_result = sql_util.update(sql)
                            log.info("成功执行sql语句：{}".format(sql))
                            # 将第3个参数加入全局变量字典
                            if len(each_pre) > 2:
                                if isinstance(sql_result, str):
                                    set_global_var(each_pre[2], sql_result)
                                    log.info("给变量{0}赋值：{1}".format(each_pre[2], sql_result))
                            run_flag = True
                    except:
                        log.error("不支持的预置操作: {0}".format(each_pre[0]))
                        store_error_code("预置条件输入错误: {0}".format(each_pre))
                        run_flag = False
            else:
                # 存在空白行，结束循环
                run_flag = True
                break

            if not run_flag:  # 预置条件执行失败，会执行到空行，结束执行预置条件
                break

        log.info("预置条件全部执行完成")
    set_global_var("EndTime", datetime.now().strftime('%Y%m%d%H%M%S'), False)
    sleep(1)
    return run_flag
