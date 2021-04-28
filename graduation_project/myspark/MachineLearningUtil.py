import findspark

findspark.init()
from pyspark.mllib.classification import NaiveBayes
from pyspark import SparkConf, SparkContext
from pyspark.ml.regression import LinearRegression
from pyspark.mllib.linalg import Vectors
from pyspark.mllib.regression import LabeledPoint, LinearRegressionWithSGD


def my_linear_regression():
    conf = SparkConf().setMaster('local').setAppName('test')
    sc = SparkContext(conf=conf).getOrCreate()
    data = sc.textFile('abc.txt')
    examples = data.map(lambda line: LabeledPoint(float(line.split(',')[0]), line.split(",")[1].split(" ")))
    print(type(examples))
    train, test = examples.randomSplit([0.8, 0.2])
    print(train.count(), test.count())
    lin_reg = LinearRegressionWithSGD(featuresCol='features', labelCol='Price')
    lin_mod = lin_reg.fit(train)
    # print('Coefficients:' + str(lin_mod.coefficients))
    # print('Intercept:' + str(lin_mod.intercept))
    sc.stop()


def my_lambda(line):
    for i in len(line):
        return line[i][0] == line[i][1]


def my_bayes():
    conf = SparkConf().setMaster('local').setAppName('test')
    sc = SparkContext(conf=conf).getOrCreate()
    data = sc.textFile('aaa.txt')
    examples = data.map(
        lambda line: LabeledPoint(float(line.split(',')[0]), Vectors.dense(line.split(",")[1].split(" "))))
    train, test = examples.randomSplit([0.5, 0.5])
    bayes = NaiveBayes.train(train, lambda_=1.0)
    prediction_and_label = test.map(lambda x: (bayes.predict(x.features), x.label))
    print(prediction_and_label.count())
    print('lllllllllllllll')
    print_predict = prediction_and_label.take(100)
    print('pre\tlab')
    for i in range(len(print_predict)):
        print(print_predict[i][0], print_predict[i][1])
    acc = 1.0 * prediction_and_label.filter(lambda x: x[0] == x[1]).count() / test.count()
    print(acc)
    # print(predictionAndLabel.count(), test.count())
    result = bayes.predict(Vectors.dense([0, 0, 85]))
    print('result=', result)
    # print('Coefficients:' + str(lin_mod.coefficients))
    # print('Intercept:' + str(lin_mod.intercept))
    sc.stop()


if __name__ == '__main__':
    # my_linear_regression()
    my_bayes()
