import findspark

findspark.init()
from pyspark.sql.utils import StreamingQueryException
from pyspark.ml.regression import LinearRegression
from pyspark.mllib.classification import NaiveBayes
from pyspark.mllib.linalg import Vectors
from pyspark.mllib.regression import LabeledPoint
import datetime
import json
from pyspark.sql.functions import lit, col, max, min
from pyspark.sql import SparkSession
from pyspark import SparkConf, SparkContext, SQLContext

from mybase.db import data2Redis
from mybase import globalVar
from myspark.GetData import DateEncoder, set2RedisData, getRoadMonitorData, getMonitorFromKafka


def yesterday_traffic_statics(df):
    # 第一次使用全局变量会执行初始化操作
    globalVar.global_var_yesterday_init()
    # 获取全局变量
    seven_day_ago = globalVar.get_yesterday() - datetime.timedelta(days=7)
    # 调用Spark方法进行数据清洗，获得道路流量情况
    yesterday_roads = df.filter(df['monitor_date'] == globalVar.get_yesterday().strftime('%Y-%m-%d')).groupBy(
        'road_id').count().sort(
        'count', ascending=False).collect()
    # 调用数据传输模块中的方法，将道路情况存入Redis
    data2Redis('yesterdayRoads', json.dumps(set2RedisData(('road_id', 'count'), yesterday_roads)))
    # 调用Spark方法进行数据清洗，获得地区流量情况
    yesterday_areas = df.filter(df['monitor_date'] == globalVar.get_yesterday().strftime('%Y-%m-%d')).groupBy(
        'area_id').count().sort(
        'count', ascending=False).collect()
    # 调用数据传输模块中的方法，将地区情况存入Redis
    data2Redis('yesterdayAreas', json.dumps(set2RedisData(('area_id', 'count'), yesterday_areas)))
    # 调用Spark方法进行数据清洗，一周的情况
    last_week = df.filter((df['monitor_date'] <= globalVar.get_yesterday().strftime('%Y-%m-%d')) & (
            df['monitor_date'] > seven_day_ago.strftime('%Y-%m-%d'))).groupBy(
        'monitor_date').count().sort('monitor_date').collect()
    # 调用数据传输模块，存入Redis，json处理时间需要用DateEncoder类
    data2Redis('lastWeek', json.dumps(set2RedisData(('monitor_date', 'count'), last_week), cls=DateEncoder))
    # 调用Spark方法进行数据清洗，获得昨天超速的情况
    yesterday_speeding_car = df.filter(df['monitor_date'] == globalVar.get_yesterday().strftime('%Y-%m-%d')).filter(
        df['car_speed'] >= 200).sort('action_time', ascending=False).collect()
    # 调用数据传输模块中的方法，将超速情况存入Redis
    data2Redis('yesterday_speeding_car', json.dumps(
        set2RedisData(('monitor_date', 'monitor_id', 'camera_id', 'car_id', 'action_time', 'car_speed',
                       'road_id', 'area_id'), yesterday_speeding_car), cls=DateEncoder))
    # 调用Spark方法进行数据清洗，获得昨天每辆车的速度
    car_speed = df.filter(df['monitor_date'] == globalVar.get_yesterday().strftime('%Y-%m-%d')).select(
        df['car_speed']).rdd.reduce(
        lambda x, y: x + y)
    # 获得平均速度的逻辑
    sum_speed = 0
    for i in range(len(car_speed)):
        avg_speed = sum_speed + car_speed[i]
    yesterday_average_speed = format(sum_speed / len(car_speed), '.2f')
    # 调用数据传输模块中的方法，将平均车速存入Redis
    data2Redis('yesterdayAverageSpeed', yesterday_average_speed)
    # 方法执行成功
    print('yesterday_traffic_statics->redis')


def yesterday_traffic_statics_by_area(df, area_id):
    globalVar.global_var_yesterday_init()
    seven_day_ago = globalVar.get_yesterday() - datetime.timedelta(days=7)
    yesterday_roads = df.filter(df['monitor_date'] == globalVar.get_yesterday().strftime('%Y-%m-%d')).filter(
        df['area_id'] == area_id).groupBy('road_id').count().sort(
        'count', ascending=False).collect()
    data2Redis('yesterdayRoadsByArea' + area_id, json.dumps(set2RedisData(('road_id', 'count'), yesterday_roads)))
    last_week = df.filter((df['monitor_date'] <= globalVar.get_yesterday().strftime('%Y-%m-%d')) & (
            df['monitor_date'] > seven_day_ago.strftime('%Y-%m-%d'))).filter(
        df['area_id'] == area_id).groupBy('monitor_date').count().sort('monitor_date').collect()
    data2Redis('lastWeekByArea' + area_id,
               json.dumps(set2RedisData(('monitor_date', 'count'), last_week), cls=DateEncoder))
    speeding_record = df.filter(df['monitor_date'] == globalVar.get_yesterday().strftime('%Y-%m-%d')).filter(
        df['car_speed'] >= 200).sort('action_time', ascending=False).collect()
    data2Redis('speedingRecordByArea' + area_id,
               json.dumps(
                   set2RedisData(('monitor_date', 'monitor_id', 'camera_id', 'car_id', 'action_time', 'car_speed',
                                  'road_id', 'area_id'), speeding_record), cls=DateEncoder))
    print('yesterday_traffic_statics_by_area' + area_id + '->redis')


def car_statics(df, car_id):
    car_road_traffic = df.filter(df['car_id'] == car_id).groupBy('road_id').count().sort('count',
                                                                                         ascending=False).collect()
    data2Redis('car_road_traffic' + car_id, json.dumps(set2RedisData(('road_id', 'count'), car_road_traffic)))
    car_traffic = df.filter(df['car_id'] == car_id).count()
    data2Redis('car_traffic' + car_id, car_traffic)
    car_speed = df.filter(df['car_id'] == car_id).select(df['car_speed']).rdd.reduce(lambda x, y: x + y)
    avg_speed = 0
    for i in range(len(car_speed)):
        avg_speed = avg_speed + car_speed[i]
    yesterday_average_speed = format(avg_speed / len(car_speed), '.2f')
    data2Redis('car_average_speed' + car_id, yesterday_average_speed)
    speeding_record = df.filter(df['car_id'] == car_id).filter(df['car_speed'] >= 200).sort('action_time',
                                                                                            ascending=False).collect()
    data2Redis('speeding_record_by_car' + car_id,
               json.dumps(
                   set2RedisData(('monitor_date', 'monitor_id', 'camera_id', 'car_id', 'action_time', 'car_speed',
                                  'road_id', 'area_id'), speeding_record), cls=DateEncoder))
    print('car_statics' + car_id + '->redis')


def foreign_car_statics(df):
    globalVar.global_var_yesterday_init()
    seven_day_ago = globalVar.get_yesterday() - datetime.timedelta(days=7)
    yesterday_foreign_car = df.filter(df['monitor_date'] == globalVar.get_yesterday().strftime('%Y-%m-%d')).filter(
        ~df['car_id'].contains('粤')).sort('action_time', ascending=False).collect()
    data2Redis('yesterday_foreign_car', json.dumps(
        set2RedisData(('monitor_date', 'monitor_id', 'camera_id', 'car_id', 'action_time', 'car_speed',
                       'road_id', 'area_id'), yesterday_foreign_car), cls=DateEncoder))
    last_week_foreign_car_count = df.filter((df['monitor_date'] <= globalVar.get_yesterday().strftime('%Y-%m-%d')) & (
            df['monitor_date'] > seven_day_ago.strftime('%Y-%m-%d'))).filter(~df['car_id'].contains('粤')).count()
    data2Redis('last_week_foreign_car_count', last_week_foreign_car_count)
    last_week_foreign_car_area = df.filter((df['monitor_date'] <= globalVar.get_yesterday().strftime('%Y-%m-%d')) & (
            df['monitor_date'] > seven_day_ago.strftime('%Y-%m-%d'))).withColumn('car_area',
                                                                                 lit(df['car_id'].substr(1, 1))).filter(
        ~df['car_id'].contains('粤')).groupBy('car_area').count().sort('count', ascending=False).collect()
    data2Redis('last_week_foreign_car_area',
               json.dumps(set2RedisData(('car_area', 'count'), last_week_foreign_car_area)))
    last_week_foreign_car_road = df.filter((df['monitor_date'] <= globalVar.get_yesterday().strftime('%Y-%m-%d')) & (
            df['monitor_date'] > seven_day_ago.strftime('%Y-%m-%d'))).filter(~df['car_id'].contains('粤')).groupBy(
        'road_id').count().sort('count', ascending=False).collect()
    data2Redis('last_week_foreign_car_road',
               json.dumps(set2RedisData(('road_id', 'count'), last_week_foreign_car_road)))
    last_week_foreign_car = df.filter((df['monitor_date'] <= globalVar.get_yesterday().strftime('%Y-%m-%d')) & (
            df['monitor_date'] > seven_day_ago.strftime('%Y-%m-%d'))).filter(~df['car_id'].contains('粤')).groupBy(
        'monitor_date').count().sort('monitor_date').collect()
    data2Redis('last_week_foreign_car',
               json.dumps(set2RedisData(('monitor_date', 'count'), last_week_foreign_car), cls=DateEncoder))
    print("foreign_car_statics->redis")


def collision_analysis(df):
    globalVar.global_var_yesterday_init()
    seven_day_ago = globalVar.get_yesterday() - datetime.timedelta(days=7)
    collision_detail = df.filter((df['monitor_date'] <= globalVar.get_yesterday().strftime('%Y-%m-%d')) & (
            df['monitor_date'] > seven_day_ago.strftime('%Y-%m-%d'))).filter(df['car_speed'] <= 10).groupBy(
        'monitor_date', 'camera_id', 'action_time', 'area_id', 'road_id').count().sort('action_time',
                                                                                       ascending=False).collect()
    # collision_detail = df.filter((df['monitor_date'] <= yesterday.strftime('%Y-%m-%d')) & (
    #         df['monitor_date'] > seven_day_ago.strftime('%Y-%m-%d'))).filter(df['car_speed'] <= 10).groupBy(
    #     'monitor_date', 'camera_id', 'action_time', 'area_id', 'road_id').count()
    # collision_detail.show()
    # for i in range(len(collision_detail)):
    #     print(collision_detail[i])

    collision_car_count = 0
    collision_matter_list = []
    for i in range(len(collision_detail)):
        if collision_detail[i]['count'] >= 2:
            collision_matter = {}
            collision_car_count = collision_car_count + collision_detail[i]['count']
            collision_matter['action_time'] = collision_detail[i]['action_time'].strftime("%Y-%m-%d %H:%M:%S")
            collision_matter['camera_id'] = collision_detail[i]['camera_id']
            collision_matter['area_id'] = collision_detail[i]['area_id']
            collision_matter['road_id'] = collision_detail[i]['road_id']
            collision_matter['car_list'] = []
            result = df.filter((df['monitor_date'] <= globalVar.get_yesterday().strftime('%Y-%m-%d')) & (
                    df['monitor_date'] > seven_day_ago.strftime('%Y-%m-%d'))).filter(
                (df['action_time'] == collision_detail[i]['action_time']) & (
                        df['camera_id'] == collision_detail[i]['camera_id']) & (
                        df['area_id'] == collision_detail[i]['area_id']) & (
                        df['road_id'] == collision_detail[i]['road_id'])).select('car_id').collect()
            for j in range(len(result)):
                collision_matter['car_list'].append(result[j]['car_id'])
            collision_matter_list.append(collision_matter)
    data2Redis('collision_matter_list', json.dumps(collision_matter_list))
    data2Redis('collision_car_count', collision_car_count)
    print('collision_analysis->redis')


# def getMointorDetailByRoad(df, road_id):
#     result = df.rdd.filter(lambda x: x['road_id'] == road_id).sortBy(lambda x: x['action_time'],
#                                                                      ascending=False).collect()
#     for i in range(len(result)):
#         print(result[i])
#     return result
#
#
# def getCaremaByMonitor(df):
#     result = df.rdd.reduceByKey(lambda x, y: str(x) + ',' + str(y)).collect()
#     for i in range(len(result)):
#         print(result[i])
#     return result


def my_func(x):
    if x > 0.8:
        return 5
    elif x > 0.6:
        return 4
    elif x > 0.4:
        return 3
    elif x > 0.2:
        return 2
    return 1


def my_bayes(df):
    # globalVar.global_var_yesterday_init()
    # seven_day_ago = globalVar.get_yesterday() - datetime.timedelta(days=7)
    # 数据清洗，得到有关数据
    data = df.groupBy('monitor_date', 'area_id', 'road_id').count().sort('count', ascending=False)
    # result = df.groupBy('monitor_date', 'area_id', 'road_id').count().sort('count', ascending=False).collect()
    # result.show()
    # max_count = 0
    #
    # for i in range(len(result)):
    #     if max_count == 0:
    #         max_count = result[i]['count']
    #     print(int(result[i]['monitor_date'].timetuple().tm_yday), result[i]['area_id'], result[i]['road_id'],
    #           my_func(result[i]['count'] / max_count))
    # 获取单条道路的最大值，用于后面的等级划分
    max_count = int(data.select(max('count')).collect()[0]['max(count)'])
    # print(max_count)
    # 将数据划分为结果和特征
    examples = data.rdd.map(
        lambda x: LabeledPoint(my_func(x['count'] / max_count),
                               Vectors.dense(int(x['monitor_date'].timetuple().tm_yday), x['area_id'],
                                             x['road_id'])))
    # 将数据划分为训练集和测试集
    (train, test) = examples.randomSplit([0.8, 0.2])
    # 训练贝叶斯模型
    bayes = NaiveBayes.train(train, lambda_=1.0)
    # 通过预测与测试集进行对比，得到结果的准确情况
    prediction_and_label = test.map(lambda x: (bayes.predict(x.features), x.label))
    # print_predict = prediction_and_label.take(100)
    # print('pre\tlab')
    # for i in range(len(print_predict)):
    #     print(print_predict[i][0], print_predict[i][1])
    # 计算准确率
    machine_learning_accuracy = 1.0 * prediction_and_label.filter(lambda x: x[0] == x[1]).count() / test.count()
    # 调用数据传输模块，将准确率存入Redis中
    data2Redis('machine_learning_accuracy', machine_learning_accuracy)
    # 预测结果
    bayes_predict_result = []
    area_road_list = globalVar.get_area_road_list()
    for i in range(len(area_road_list)):
        for j in range(len(area_road_list[i])):
            bayes_result = {}
            bayes_result['yday'] = globalVar.get_yesterday().timetuple().tm_yday
            bayes_result['area_id'] = i + 1
            bayes_result['road_id'] = area_road_list[i][j]
            bayes_result['predict'] = bayes.predict(
                Vectors.dense([globalVar.get_yesterday().timetuple().tm_yday + 1, i + 1, area_road_list[i][j]]))
            bayes_predict_result.append(bayes_result)
    # result = bayes.predict(Vectors.dense([globalVar.get_yesterday().timetuple().tm_yday, 0, 85]))
    # print('result=', bayes_predict_result)
    # 调用数据传输模块，将预测结果存入Redis中
    data2Redis('bayes_predict_result', json.dumps(bayes_predict_result))


def my_linear_regression(df):
    result = df.groupBy('monitor_date').count().sort('count', ascending=False)
    min_monitor_date = result.select(min('monitor_date')).collect()[0]['min(monitor_date)']
    print(min_monitor_date)
    # result = result.collect()
    # for i in range(len(result)):
    #     print(int((result[i]['monitor_date'] - min_monitor_date).days), result[i]['count'])
    examples = result.rdd.map(
        lambda x: LabeledPoint(x['count'], Vectors.dense(int((x['monitor_date'] - min_monitor_date).days))))
    # print(type(examples))
    (train, test) = examples.randomSplit([0.8, 0.2])
    lrs = LinearRegression(labelCol='count')
    model = lrs.fit(train)
    print(model.weights)
    print(model.intercept)
    print(model.evaluate(14))


# def streamingBySpeed(df):
#     df = df.groupBy(col('road_id')).count().sort('count', ascending=False)
#     df.writeStream.format("console").outputMode("complete").trigger(
#         processingTime='10 seconds').start().awaitTermination()


def my_streaming(df):
    # df = df.filter('car_speed>=100')
    # df.writeStream.format("memory").queryName("monitor_data").trigger(processingTime='5 seconds')
    # .foreach(ForeachWriter()).start().awaitTermination()
    # df.writeStream.trigger(processingTime='5 seconds').count().start().awaitTermination()
    # 判断df是否存在，防止空指针异常
    if df:
        # 通过writeStream的方法每15秒调用一次foreach_batch_function方法
        df.writeStream.trigger(processingTime='15 seconds').foreachBatch(
            foreach_batch_function).start().awaitTermination()


# def foreach_batch_function(df, epoch_id):
#     global real_time_car_count
#     global real_time_car_road_list
#     global real_time_speeding_data_list
#     real_time_car_count = real_time_car_count + df.count()
#     data2Redis('real_time_car_count', real_time_car_count)
#     result = df.groupBy('road_id').count().sort('road_id').collect()
#     print(result)
#     for i in range(len(result)):
#         real_time_car_road_list[int(result[i]['road_id']) - 1]['count'] = \
#             real_time_car_road_list[int(result[i]['road_id']) - 1]['count'] + result[i]['count']
#     data2Redis('real_time_car_road_list', json.dumps(real_time_car_road_list))
#     speeding_datas = df.filter('car_speed>=150').sort('action_time').collect()
#     for i in range(len(speeding_datas)):
#         real_time_speeding_data_list.append(speeding_datas[i])
#     data2Redis('real_time_speeding_data_list', json.dumps(set2RedisData(
#         ('monitor_date', 'monitor_id', 'camera_id', 'car_id', 'action_time', 'car_speed', 'road_id', 'area_id'),
#         real_time_speeding_data_list), cls=DateEncoder))
#     print('foreach_batch_function', epoch_id, '->redis')


def foreach_batch_function(df, epoch_id):
    # 判断该线程的标志
    if globalVar.get_start_streaming_flag():
        # 记录总共实时分析的数据量
        globalVar.set_real_time_car_count(globalVar.get_real_time_car_count() + df.count())
        # 调用数据传输模块，将数据量存入Redis
        data2Redis('real_time_car_count', globalVar.get_real_time_car_count())
        # 实时对数据进行分类
        my_real_time_car_road_list = globalVar.get_real_time_car_road_list()
        result = df.groupBy('road_id').count().sort('road_id').collect()
        for i in range(len(result)):
            my_real_time_car_road_list[int(result[i]['road_id']) - 1]['count'] = \
                my_real_time_car_road_list[int(result[i]['road_id']) - 1]['count'] + result[i]['count']
        globalVar.set_real_time_car_road_list(my_real_time_car_road_list)
        # 调用数据传输模块，将分类后的数据存入Redis
        data2Redis('real_time_car_road_list', json.dumps(my_real_time_car_road_list))
        # 实时将超速情况记录下来
        my_real_time_speeding_data_list = globalVar.get_real_time_speeding_data_list()
        speeding_datas = df.filter('car_speed >= 150').sort('action_time').collect()
        for i in range(len(speeding_datas)):
            my_real_time_speeding_data_list.append(speeding_datas[i])
        globalVar.set_real_time_speeding_data_list(my_real_time_speeding_data_list)
        # 调用数据传输模块，将超速记录存入Redis
        data2Redis('real_time_speeding_data_list', json.dumps(set2RedisData(
            ('monitor_date', 'monitor_id', 'camera_id', 'car_id', 'action_time', 'car_speed', 'road_id', 'area_id'),
            my_real_time_speeding_data_list), cls=DateEncoder))
        # 该方法执行成功
        print('foreach_batch_function', epoch_id, '->redis')
    else:
        # 根据线程标志停止实时分析功能
        globalVar.get_ssc().stop()
        print('foreach_batch_function-->stop stop stop stop stop stop stop stop stop stop stop stop')


def redis_streaming_init():
    data2Redis('real_time_speeding_data_list', '[]')
    data2Redis('real_time_car_count', '0')
    data2Redis('real_time_car_road_list', '[]')


if __name__ == '__main__':
    # global real_time_car_count
    # real_time_car_count = 0
    # global real_time_car_road_list
    # real_time_car_road_list = [{'road_id': 1, 'count': 0}, {'road_id': 2, 'count': 0}, {'road_id': 3, 'count': 0},
    #                            {'road_id': 4, 'count': 0}, {'road_id': 5, 'count': 0}, {'road_id': 6, 'count': 0},
    #                            {'road_id': 7, 'count': 0}, {'road_id': 8, 'count': 0}, {'road_id': 9, 'count': 0}]
    # global real_time_speeding_data_list
    # real_time_speeding_data_list = []

    conf = SparkConf().setMaster('local').setAppName('test')
    sc = SparkContext(conf=conf).getOrCreate()

    # globalVar.global_var_init()
    # ssc = SparkSession.builder.appName("test").getOrCreate()

    sqlc = SQLContext(sc)
    monitor_df = getRoadMonitorData(sqlc)

    # yesterday_traffic_statics(monitor_df)
    # yesterday_traffic_statics_by_area(monitor_df, '3')
    # car_statics(monitor_df, '粤A00001')
    # foreign_car_statics(monitor_df)
    # collision_analysis(monitor_df)
    my_bayes(monitor_df)
    # my_linear_regression(monitor_df)
    # streamingBySpeed(getMonitorFromKafka(ssc))

    # my_streaming(getMonitorFromKafka(ssc))

    sc.stop()
    # today = time.strftime('%Y-%m-%d', time.localtime(time.time()))
    # threeDayAgo = (datetime.datetime.now() - datetime.timedelta(days=7))
    #
    # print(datetime.datetime.now().strftime('%Y-%m-%d'))
