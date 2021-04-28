
import findspark

findspark.init()
import configparser

from pyspark import SparkConf, SparkContext, SQLContext

from myspark.DataAnalysisUtil import getMointorDetailByRoad
from myspark.GetData import getRoadMonitorData

if __name__ == '__main__':
    # cf = configparser.ConfigParser()
    # cf.read("/data/conf.ini")
    # print(cf.get('mysql', 'HOST'))
    conf = SparkConf().setMaster('local').setAppName('test')
    sc = SparkContext(conf=conf).getOrCreate()
    sqlc = SQLContext(sc)
    result = getMointorDetailByRoad(getRoadMonitorData(sqlc), 1)
    sc.stop()