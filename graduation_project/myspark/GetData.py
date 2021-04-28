import datetime
import time, json

from pyspark.sql.functions import split
from mybase import db


def getCSVData(sqlc, file_path, schema, sep):
    return sqlc.read.csv(file_path, schema=schema, sep=sep)


# def getRoadMonitorData(sqlc):
#     schema = types.StructType().add('monitor_date', types.DateType()).add('monitor_id', types.LongType()).add(
#         'canera_id', types.LongType()).add('car_id', types.StringType()).add('action_time', types.TimestampType()).add(
#         'car_speed', types.LongType()).add('road_id', types.LongType()).add('area_id', types.LongType())
#     return getCSVData(sqlc, '../data/monitor_flow_action', schema, '\t')


def getRoadMonitorData(sqlc):
    return sqlc.read.format("jdbc").options(url="jdbc:mysql://localhost:3306/graduation_project",
                                            driver="com.mysql.jdbc.Driver",
                                            dbtable="monitor_flow_action", user="root",
                                            password="123456").load()


def getMonitorAndCameraData(sqlc):
    return sqlc.read.format("jdbc").options(url="jdbc:mysql://localhost:3306/graduation_project",
                                            driver="com.mysql.jdbc.Driver",
                                            dbtable="monitor_camera_info", user="root",
                                            password="123456").load()


def getMonitorFromKafka(ssc):
    if ssc:
        df = ssc.readStream.format('kafka').option("kafka.bootstrap.servers", "192.168.17.123:9092").option('subscribe',
                                                                                                            'test').load()
        df = df.select('value').withColumn('monitor_date', split('value', '\t')[0]) \
            .withColumn('monitor_id', split('value', '\t')[1]).withColumn('camera_id', split('value', '\t')[2]) \
            .withColumn('car_id', split('value', '\t')[3]).withColumn('action_time', split('value', '\t')[4]) \
            .withColumn('car_speed', split('value', '\t')[5]).withColumn('road_id', split('value', '\t')[6]) \
            .withColumn('area_id', split('value', '\t')[7]).drop('value')
        return df


def getUser(user_name, user_password):
    return db.mysqlConn(
        "select * from user_info where user_name = '{0}' and user_password = '{1}';".format(user_name, user_password))


def get_monitor_data_count(sqlstr):
    sqlstr = sqlstr[:sqlstr.index('*')] + 'count(*)' + sqlstr[sqlstr.index('*') + 1:]
    return db.mysqlConn(sqlstr)


def getMoniterDataFromMysql(from_date=None, end_date=None, area_id=None, road_id=None, car_id=None, car_speed=None,
                            monitor_id=None, camera_id=None, limit_num=20, page_num=0):
    sqlstr = "select * from monitor_flow_action where 1=1"
    if from_date is not None and from_date != "":
        sqlstr = sqlstr + " and monitor_date >= " + from_date
    if end_date is not None and end_date != "":
        sqlstr = sqlstr + " and monitor_date <= " + end_date
    if area_id is not None and area_id != "" and area_id != "0":
        sqlstr = sqlstr + " and area_id = " + area_id
    if road_id is not None and road_id != "" and road_id != "0":
        sqlstr = sqlstr + " and road_id = " + road_id
    if car_id is not None and car_id != "":
        sqlstr = sqlstr + " and car_id like '%" + car_id + "%'"
    if car_speed is not None and car_speed != "":
        sqlstr = sqlstr + " and car_speed > " + car_speed
    if monitor_id is not None and monitor_id != "":
        sqlstr = sqlstr + " and monitor_id = " + monitor_id
    if camera_id is not None and camera_id != "":
        sqlstr = sqlstr + " and camera_id = " + camera_id
    sqlstr = sqlstr + " order by action_time desc"
    if limit_num is not None and limit_num != "" and limit_num != "0" and limit_num != 0:
        sqlstr = sqlstr + " limit "
        if page_num is not None and page_num != "" and page_num != "0" and page_num != 0:
            sqlstr = sqlstr + str(int(limit_num) * int(page_num)) + ','
        sqlstr = sqlstr + str(limit_num)
    sqlstr = sqlstr + ";"
    return db.mysqlConn(sqlstr)


def set2RedisData(shema, data):
    # shema = ('road_id', 'count')
    mydic = []
    for i in range(len(data)):
        mydic.append(dict(zip(shema, data[i])))
    return mydic


# return render(request, 'monitor_log.html', {'data': json.dumps(mydic, cls=DateEncoder)})

def get_car_by_id(car_id):
    result = db.mysqlConn(
        "select distinct car_id from monitor_flow_action where car_id like '%" + car_id + "%' limit 5;")
    car_list = []
    for i in range(len(result)):
        car_list.append(result[i][0])
    return car_list


class DateEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.strftime("%Y-%m-%d %H:%M:%S")
        elif isinstance(obj, datetime.date):
            return obj.strftime("%Y-%m-%d")
        else:
            return json.JSONEncoder.default(self, obj)


if __name__ == '__main__':
    print(get_car_by_id('粤4'))
