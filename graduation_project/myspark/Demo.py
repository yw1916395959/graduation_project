import sys
import findspark

findspark.init()
from pyspark.sql.functions import split
from pyspark.sql.session import SparkSession
from pyspark import SparkContext, SparkConf
from pyspark.streaming import StreamingContext
from kafka import KafkaProducer, KafkaConsumer


def test1():
    sc = SparkContext(appName='streamingkafka')
    sc.setLogLevel('WARN')
    ssc = StreamingContext(sc, 5)
    kafkaParams = {'metadata.broker.list': '192.168.17.123:9092'}
    topics = ['test']
    # kafkaStream = KafkaUtils.createDirectStream(ssc=ssc, topics=topics, kafkaParams=kafkaParams).flatMap(
    #     lambda x: str(x).split(' ')).map(
    #     lambda x: (x, 1)).reduceByKey(
    #     lambda x, y: x + y).foreachRDD(lambda x: print(x))


def test2():
    conf = SparkConf().setMaster('local[2]').setAppName('test')
    sc = SparkContext(conf=conf)
    sc.setLogLevel('WARN')
    ssc = StreamingContext(sc, 5)
    lines = ssc.socketTextStream('192.168.17.123', 9999)
    ssc.textFileStream()
    result = lines.map(lambda x: (x, 1)).reduceByKey(lambda x, y: x + y)
    result.pprint()
    ssc.start()
    ssc.awaitTermination()


def test3():
    pass


def cli2kafka():
    producer = KafkaProducer(bootstrap_servers='192.168.17.123:9092')
    topic = 'test'
    producer.send(topic, b'hello world')
    print('ok')
    producer.close()


def kafka2cli():
    consumer = KafkaConsumer('test', group_id='consumer-20210314', bootstrap_servers=['192.168.17.123:9092'])
    print('start')
    for msg in consumer:
        print(msg)

def getDataFromKafka():
    sc = SparkSession.builder.appName("test").getOrCreate()
    df = sc.readStream.format('kafka').option("kafka.bootstrap.servers", "192.168.17.123:9092").option('subscribe',
                                                                                                       'test').load()

    df = df.select('value').withColumn('monitor_date', split('value', '\t')[0]) \
        .withColumn('monitor_id', split('value', '\t')[1]).withColumn('canera_id', split('value', '\t')[2]) \
        .withColumn('car_id', split('value', '\t')[3]).withColumn('action_time', split('value', '\t')[4]) \
        .withColumn('car_speed', split('value', '\t')[5]).withColumn('road_id', split('value', '\t')[6]) \
        .withColumn('area_id', split('value', '\t')[7]).drop('value')
    df = df.filter('car_id=="京C60159"')
    df.writeStream.format("console").trigger(processingTime='5 seconds').start().awaitTermination()
