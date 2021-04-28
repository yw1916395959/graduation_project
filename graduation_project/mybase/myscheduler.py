import findspark

findspark.init()
from myspark.kafkaProducer import kafka_start_produce
from mybase import globalVar
from myspark.DataAnalysisUtil import my_streaming, redis_streaming_init, yesterday_traffic_statics, \
    yesterday_traffic_statics_by_area, foreign_car_statics, my_bayes, collision_analysis
from pyspark import SparkConf, SparkContext, SQLContext
from pyspark.sql import SparkSession
import threading
from myspark.GetData import getRoadMonitorData, getMonitorFromKafka
from apscheduler.events import EVENT_JOB_EXECUTED, EVENT_JOB_ERROR
from apscheduler.schedulers.blocking import BlockingScheduler


def tick(a, b):
    print('Tick ! The time is:{0}'.format(a), '---', b)


def my_listener(e):
    if e.exception:
        print('任务出错了!!!')


def test(func):
    scheduler = BlockingScheduler()
    # scheduler.add_job(func=func, trigger='interval', seconds=20, id=func.__name__)
    scheduler.add_job(tick, 'cron', hour=19, minute=23)
    scheduler.add_listener(my_listener, EVENT_JOB_EXECUTED | EVENT_JOB_ERROR)
    try:
        scheduler.start()
    except(KeyboardInterrupt, SystemExit):
        pass


# def test2(func):
#     scheduler = BlockingScheduler()
#     scheduler.add_job(func=func, args=['abc', 'aaa'], trigger='interval', seconds=5, id=func.__name__)
#     scheduler.add_listener(my_listener, EVENT_JOB_EXECUTED | EVENT_JOB_ERROR)
#     try:
#         scheduler.start()
#     except(KeyboardInterrupt, SystemExit):
#         pass


def my_interval_scheduler(scheduler, func, args, minutes):
    scheduler.add_job(func=func, args=args, trigger='interval', minutes=minutes, id=func.__name__)
    scheduler.add_listener(my_listener, EVENT_JOB_EXECUTED | EVENT_JOB_ERROR)
    try:
        scheduler.start()
    except(KeyboardInterrupt, SystemExit):
        pass


def my_cron_scheduler(scheduler, func, args, hour=0, minute=0, second=0):
    scheduler.add_job(func=func, args=args, trigger='cron', day_of_week='0-6', hour=hour, minute=minute, second=second,
                      id=func.__name__)
    scheduler.add_listener(my_listener, EVENT_JOB_EXECUTED | EVENT_JOB_ERROR)
    try:
        scheduler.start()
    except(KeyboardInterrupt, SystemExit):
        pass


class MyStreamingThread(threading.Thread):
    def __init__(self):
        self.__flag = threading.Event()
        self.__flag.set()
        globalVar.set_start_streaming_flag(True)
        threading.Thread.__init__(self)
        if not globalVar.get_ssc():
            globalVar.set_ssc(SparkSession.builder.appName("test").getOrCreate())
        print('MyStreamingThread---start')

    def run(self):
        if self.__flag.is_set():
            while globalVar.get_start_streaming_flag():
                my_streaming(getMonitorFromKafka(globalVar.get_ssc()))
                print('222222222222222222222222222222222222222222222')
                # self.__flag.wait()
            else:
                self.stop()
                self.__flag.wait()

    def stop(self):
        # if not globalVar.get_ssc():
        #     globalVar.get_ssc().stop(True, True)
        #     print('ssc---stop')
        self.__flag.clear()
        print('MyStreamingThread---stop')


def my_streaming_scheduler():
    redis_streaming_init()
    globalVar.global_var_init()
    globalVar.set_my_streaming_thread(MyStreamingThread())
    globalVar.get_my_streaming_thread().start()


def my_streaming_scheduler_stop():
    globalVar.set_start_streaming_flag(False)
    # if not globalVar.get_my_streaming_thread():
    #     globalVar.get_my_streaming_thread().stop()


# def streaming_scheduler():
#     globalVar.global_var_init()
#     scheduler = BlockingScheduler()
#     ssc = SparkSession.builder.appName("test").getOrCreate()
#     df = getMonitorFromKafka(ssc)
#     my_interval_scheduler(scheduler=scheduler, func=test, args=[df], minutes=1)
#     t2 = threading.Thread(target=kafka_start_produce)
#     t1 = threading.Thread(target=my_streaming, args=(df,))
#     t2.start()
#     t1.start()
#     # my_streaming()


class MyDataAnalysisThread(threading.Thread):
    def __init__(self):
        self.__flag = threading.Event()
        self.__flag.set()
        threading.Thread.__init__(self)
        if not globalVar.get_sc():
            globalVar.set_sc(SparkContext(conf=SparkConf().setMaster('local').setAppName('test')).getOrCreate())
        if not globalVar.get_monitor_df():
            globalVar.set_monitor_df(getRoadMonitorData(SQLContext(globalVar.get_sc())))
        print('MyDataAnalysisThread---start')

    def run(self):
        while self.__flag.is_set():
            my_data_analysis(globalVar.get_monitor_df())
            self.__flag.wait()

    def stop(self):
        self.__flag.clear()
        if globalVar.get_sc():
            globalVar.get_sc().stop()
        print('MyDataAnalysisThread---stop')


def my_data_analysis(monitor_df):
    # 全局变量中任务调度模块的相关变量初始化
    globalVar.global_var_my_scheduler_init()
    # 每天1点开始分析昨日的数据
    my_cron_scheduler(scheduler=globalVar.get_my_scheduler(), func=yesterday_traffic_statics, args=[monitor_df], hour=1)
    # 每天2点15分开始分析昨日地区编号为1的数据
    my_cron_scheduler(scheduler=globalVar.get_my_scheduler(), func=yesterday_traffic_statics_by_area,
                      args=[monitor_df, '1'], hour=2, minute=15)
    # 每天2点30分开始分析昨日地区编号为2的数据
    my_cron_scheduler(scheduler=globalVar.get_my_scheduler(), func=yesterday_traffic_statics_by_area,
                      args=[monitor_df, '2'], hour=2, minute=30)
    # 每天2点45分开始分析昨日地区编号为3的数据
    my_cron_scheduler(scheduler=globalVar.get_my_scheduler(), func=yesterday_traffic_statics_by_area,
                      args=[monitor_df, '3'], hour=2, minute=45)
    # 每天3点开始分析外地车的数据
    my_cron_scheduler(scheduler=globalVar.get_my_scheduler(), func=foreign_car_statics, args=[monitor_df], hour=3)
    # 每天4点开始进行碰撞分析
    my_cron_scheduler(scheduler=globalVar.get_my_scheduler(), func=collision_analysis, args=[monitor_df], hour=4)
    # 每天5点开始训练贝叶斯模型并预测第二天的道路拥挤情况
    my_cron_scheduler(scheduler=globalVar.get_my_scheduler(), func=my_bayes, args=[monitor_df], hour=5)


if __name__ == '__main__':
    # streaming_scheduler()
    # my_data_analysis()
    MyDataAnalysisThread().start()
# if __name__ == '__main__':
#     test2(tick)

# if __name__ == '__main__':
#     scheduler = BlockingScheduler()
#     conf = SparkConf().setMaster('local').setAppName('test')
#     sc = SparkContext(conf=conf).getOrCreate()
#     sqlc = SQLContext(sc)
#     # ss = SparkSession.builder.appName("test").getOrCreate()
#     monitor_df = getRoadMonitorData(sqlc)
#     my_interval_scheduler(scheduler=scheduler, func=test, args=[monitor_df], minutes=1)
#     # getMointorDetailByArea(monitor_df, 1)
#
#     sc.stop()
