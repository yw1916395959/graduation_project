import random
import string
import time

from kafka import KafkaProducer


def kafka_start_produce():
    area_name_list = ["京", "沪", "川", "晋", "粤", "粤", "粤", "粤", "粤"]
    area_road_list = [[4, 7, 8, 9], [2, 3, 4, 5], [1, 4, 5, 6]]
    monitor_camera_list = [range(1, 10), range(10, 20), range(20, 30), range(30, 40), range(40, 50), range(50, 60),
                           range(60, 70), range(70, 80), range(80, 90), range(90, 100)]
    # mytime = time.localtime(
    #     random.randint(time.mktime((2020, 1, 1, 0, 0, 0, 0, 0, 0)), time.mktime((2021, 1, 1, 0, 0, 0, 0, 0, 0))))
    producer = KafkaProducer(bootstrap_servers='192.168.17.123:9092')
    topic = 'test'
    print('准备开始生成')
    for i in range(random.randint(1000, 2000)):
        my_time = time.localtime(time.time())
        area_id = random.randint(0, 2)
        monitor_id = random.randint(0, 9)
        msg = "{0}\t{1}\t{2}\t{3}\t{4}\t{5}\t{6}\t{7}".format(
            time.strftime('%Y-%m-%d', my_time), str(monitor_id + 1),
            str(random.choice(monitor_camera_list[monitor_id])),
            random.choice(area_name_list) + random.choice(string.ascii_uppercase) + str(
                random.randint(1, 100000)).zfill(5), time.strftime('%Y-%m-%d %H:%M:%S', my_time),
            str(100 + random.randint(-100, 120)), str(random.choice(area_road_list[area_id])), str(area_id + 1))
        producer.send(topic, bytes(msg, encoding='utf8'))
        print(msg + '-->kafka')
        time.sleep(random.random() * 2)
    producer.close()


if __name__ == '__main__':
    kafka_start_produce()
