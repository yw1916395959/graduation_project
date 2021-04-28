import os
from mybase import globalVar
import configparser
import string
import time
import random
import pymysql
import redis


def mysqlConn(sql):
    cf = configparser.ConfigParser()
    cf.read(os.path.dirname(os.path.dirname(__file__)) + "/data/conf.ini")
    db = pymysql.connect(host=cf.get('mysql', 'HOST'), user=cf.get('mysql', 'USER'),
                         password=cf.get('mysql', 'PASSWORD'), database=cf.get('mysql', 'DATABASE'),
                         port=int(cf.get('mysql', 'PORT')))
    cursor = db.cursor()
    cursor.execute(sql)
    print(sql)
    db.commit()
    data = cursor.fetchall()
    db.close()
    cursor.close()
    return data


def data2Redis(data_name, data):
    result = redis.Redis(
        connection_pool=redis.ConnectionPool(host='192.168.17.123', port=6379, decode_responses=True)).set(data_name,
                                                                                                           data)
    print(data_name, '-->', data, '-->', result)
    return result


def redis2Data(data_name):
    result = redis.Redis(
        connection_pool=redis.ConnectionPool(host='192.168.17.123', port=6379, decode_responses=True)).get(data_name)
    print(data_name, '<--', result, '<-- redis')
    return result


def mookData():
    area_name_list = ["京", "沪", "川", "晋", "粤", "粤", "粤", "粤", "粤"]
    area_road_list = globalVar.get_area_road_list()
    monitor_camera_list = [range(1, 10), range(10, 20), range(20, 30), range(30, 40), range(40, 50), range(50, 60),
                           range(60, 70), range(70, 80), range(80, 90), range(90, 100)]
    print('准备开始生成')
    # monitor_id = random.randint(0, 9)
    # camera_id = random.choice(monitor_camera_list[monitor_id])
    # print(monitor_id, camera_id)
    for i in range(random.randint(30, 40)):
        my_time = time.localtime(time.time())
        area_id = random.randint(0, 2)
        monitor_id = random.randint(0, 9)
        sql = "insert into monitor_flow_action values('{0}',{1},{2},'{3}','{4}',{5},{6},{7});".format(
            time.strftime('%Y-%m-%d', my_time), str(monitor_id + 1),
            str(random.choice(monitor_camera_list[monitor_id])),
            random.choice(area_name_list) + random.choice(string.ascii_uppercase) + str(
                random.randint(1, 100000)).zfill(5), time.strftime('%Y-%m-%d %H:%M:%S', my_time),
            str(100 + random.randint(-100, 120)), str(random.choice(area_road_list[area_id])), str(area_id + 1))
        mysqlConn(sql)
        time.sleep(random.random() * 2)
    print("ok")


def mookCameraData():
    monitor_camera_list = [range(1, 10), range(10, 20), range(20, 30), range(30, 40), range(40, 50), range(50, 60),
                           range(60, 70), range(70, 80), range(80, 90), range(90, 100)]
    for i in range(len(monitor_camera_list)):
        for j in range(len(monitor_camera_list[i])):
            mysqlConn(
                "insert into monitor_camera_info values('{0}','{1}');".format(str(i + 1), monitor_camera_list[i][j]))


if __name__ == '__main__':
    mookData()
    # ob=json.loads(redis2Data('dateTraffic'))
    # print(type(ob))
