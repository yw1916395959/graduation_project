import findspark

findspark.init()
from pyspark import SparkConf, SparkContext, SQLContext

from myspark.DataAnalysisUtil import streamingBySpeed

from pyspark.sql.session import SparkSession

from myspark.GetData import getMonitorFromKafka, getRoadMonitorData

if __name__ == '__main__':
    conf = SparkConf().setMaster('local').setAppName('test')
    sc = SparkContext(conf=conf).getOrCreate()
    sqlc = SQLContext(sc)
    # sc = SparkSession.builder.appName("test").getOrCreate()
    monitor_df = getRoadMonitorData(sqlc)

    # schema = types.StructType().add('monitor_date', types.DateType()).add('monitor_id', types.LongType()).add(
    #     'canera_id', types.LongType()).add('car_id', types.StringType()).add('action_time', types.TimestampType()).add(
    #     'car_speed', types.LongType()).add('road_id', types.LongType()).add('area_id', types.LongType())
    # monitor_df = sqlc.read.csv('../data/monitor_flow_action', schema, '\t')
    # schema = types.StructType().add('monitor_id', types.LongType()).add('canera_id', types.LongType())
    # carema_df = sqlc.read.csv('../data/monitor_camera_info', schema=schema, sep="\t")

    # carema_df = getMonitorAndCameraData(sqlc)

    # top5Roads(monitor_df)

    # getMonitorDetailByDateRange(monitor_df, datetime.date(2018, 11, 5), datetime.date(2018, 11, 6))

    # getMointorDetailByArea(monitor_df, 7)

    # getMointorDetailByArea(monitor_df, '京C60159')

    # mayBadCarema(monitor_df, carema_df)

    # getSpeedingCar(monitor_df, 200)

    # getCaremaByMonitor(carema_df)

    # getMointorDetailByRoad(monitor_df, 35)

    # streamingBySpeed(getMonitorFromKafka(sc), 200)

    sc.stop()
    # pass
