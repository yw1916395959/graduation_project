import findspark
from pyspark.sql.functions import split

findspark.init()
from pyspark.sql import SparkSession

if __name__ == '__main__':
    ssc = SparkSession.builder.appName("test").getOrCreate()
    df = ssc.readStream.format('memory').load()
    df.filter('car_speed >= 150').show()
    df = df.sql_ctx('select * from monitor_data')
