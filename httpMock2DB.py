
import sys
from datetime import datetime
import pymysql
import flask
import json
from werkzeug.routing import BaseConverter

app = flask.Flask(__name__)


class RegexConverter(BaseConverter):
    def __init__(self, url_map, *items):
        super(RegexConverter, self).__init__(url_map)
        self.regex = items[0]


app.url_map.converters['regex'] = RegexConverter


@app.route('/mock/http/<regex("[a-zA-Z0-9]+"):callType>', methods=['GET', 'POST', 'DELETE', 'PUT', 'HEAD', 'OPTIONS'])
def mock(callType):

    print("callType: {}".format(callType))

    req_method = flask.request.method
    print("req_method: {}".format(req_method))

    req_time = datetime.now().replace(microsecond=0)
    print("req_time: {}".format(req_time))

    req_head = flask.request.headers
    # print("req_head: {}".format(req_head))
    print("req_head: {}".format(json.dumps(dict(req_head))))

    req_data = flask.request.data
    # print("req_data: {}".format(req_data))
    req_data = str(req_data, encoding="utf-8")
    print("req_data: {}".format(req_data))

    req_args = flask.request.args
    print("req_args: {}".format(req_args))

    auth = flask.request.authorization
    print("auth: {}".format(flask.request.authorization))
    if auth:
        print(auth.username)
        print(auth.password)

    connection = pymysql.connect(host='192.168.88.116',
                                 port=3306,
                                 user='aisee1',
                                 password='aisee1_pass',
                                 db='aisee1',
                                 charset='utf8mb4')
    try:
        with connection.cursor() as cursor:
            sql = '''insert into pw_interface_db(pk, method, head, body, auth, call_type, update_time) 
            values(UUID(), '{0}', '{1}', '{2}', '{3}', '{4}', '{5}')'''.format(req_method, req_head, req_data, auth, callType, req_time)
            cursor.execute(sql)
            connection.commit()
    finally:
        connection.close()
    return "Interface request date save to database successfully!"


if __name__ == '__main__':
    try:
        port = int(sys.argv[1])
    except (IndexError, ValueError):
        port = 5009
    app.run(host='0.0.0.0', port=port, debug=True)
