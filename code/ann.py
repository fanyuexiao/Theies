import tensorflow as tf
import numpy as np
import time

class FNN(object):
    def __init__(self, args, sess):
        self.batch_size = args.batch_size
        self.learning_rate = args.learning_rate
        self.epoch = args.epoch
        self.sess = sess
        self.model()

    def model(self):
        self.X = tf.placeholder(tf.float32, [None, 4], name="Input")
        self.Y = tf.placeholder(tf.float32, [None, 2], name="Label")

        self.layer_1 = tf.layers.dense(self.X, 10, tf.nn.relu, name="FNNLayer1")
        self.layer_2 = tf.layers.dense(self.layer_1, 20, tf.nn.relu, name="FNNLayer2")
        self.layer_3 = tf.layers.dense(self.layer_2, 40, tf.nn.relu, name="FNNLayer3")
        self.layer_4 = tf.layers.dense(self.layer_3, 20, tf.nn.relu, name="FNNLayer4")
        self.logits = tf.layers.dense(self.layer_4, 2, tf.nn.relu, name="Logits")

        self.crossEntropy = tf.nn.softmax_cross_entropy_with_logits(labels=self.Y, logits=self.logits, name="CrossEntropy")
        self.optimizer = tf.train.AdamOptimizer(learning_rate=self.learning_rate).minimize(self.crossEntropy)
        self.qProb = tf.nn.softmax(self.logits, name="PredictedProbability")

        # 存储
        self.saver = tf.train.Saver(var_list={v.op.name: v for v in tf.trainable_variables()}, max_to_keep=100)

    def save(self,save_path):
        self.saver.save(self.sess,save_path=save_path)

    def predict(self, Xs, RealP):
        # Xs:l*4
        qProb = self.sess.run(self.qProb, feed_dict={self.X:Xs})
        i = 0
        while i < len(Xs):
            print(Xs[i], "--预测的概率-->",qProb[i][1],RealP[i],)
            i += 1

    def getProb(self, X):
        qProb = self.sess.run(self.qProb, feed_dict={self.X:[X]})
        return qProb[0][1]

    def fitAndTrainEpoch(self, Xs, Ys):
        # Xs:n*m*4 Ys:n*m*2
        for i in range(len(Xs)):
            # if i % 1000 == 0:
            #     print('%.2f' % (i/len(Xs)))
            In,Out = Xs[i],Ys[i]
            self.sess.run(self.optimizer, feed_dict={self.X:In, self.Y:Out})

    def proprecessData(self, XX, YY):
        # XX:nm*4, YY:nm*2
        Xs = [];Ys = [];i = 0;xs = [];ys = []
        while i < len(XX):
            i += 1
            xs.append(XX[i-1]);ys.append(YY[i-1])
            if i % self.batch_size == 0:
                Xs.append(xs);Ys.append(ys)
                xs, ys = [], []
        return np.array(Xs), np.array(Ys)

    def shuffleData(self, Xs, Ys):
        all_index = np.arange(len(Xs))
        np.random.shuffle(all_index)
        x = Xs[all_index]
        y = Ys[all_index]
        return x, y

    def train(self, XX, YY):
        Xs, Ys = self.proprecessData(XX, YY)
        for i in range(self.epoch):
            Xs, Ys = self.shuffleData(Xs, Ys)
            # print("损失函数（之前）：", self.sess.run(self.crossEntropy, feed_dict={self.X:Xs[0],self.Y:Ys[0]}))
            print("第{}个epoch消耗时间：{}".format(i, time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))))
            self.fitAndTrainEpoch(Xs, Ys)
            # print("损失函数（之后）：", self.sess.run(self.crossEntropy, feed_dict={self.X:Xs[0],self.Y:Ys[0]}))

    def restoreModel(self, model_path):
        self.saver.restore(self.sess, save_path=model_path)

class ARGS(object):
    def __init__(self):
        self.batch_size = 512
        self.learning_rate = 0.001
        self.epoch = 12

class DataX1X2X3(object):
    def __init__(self, train_path, test_path):
        self.train_path = train_path
        self.test_path = test_path

    def fromFile(self, path):
        XX = [];YY = [];ZZ = []
        if path != None:
            with open(path) as f:
                for fLine in f:
                    fLine = fLine.split('\n')[0]
                    ss = fLine.split(' ')
                    p0,x1,x2,x3,label = \
                        float(ss[0]), float(ss[1]), float(ss[2]), float(ss[3]), float(ss[4])
                    xx = [p0,x1,x2,x3]
                    yy = ([1,0],[0,1])[label > 0] #前面为1 表示发生；后面为1表示未发生；py三元表达式
                    XX.append(xx);YY.append(yy);ZZ.append(label)
        return XX,YY,ZZ

    def getTrainAndTestDataFromFile(self):
        testXX,testYY,testZZ = self.fromFile(self.test_path)
        trainXX,trainYY,trainZZ = self.fromFile(self.train_path)
        return (trainXX, trainYY, trainZZ), (testXX, testYY, testZZ)


def trainProcess():
    with tf.Session() as sess:
        generateType = 2

        trainDataPath = "../D/trainDataX1X2X3_{}.txt".format(generateType)
        testDataPath = None

        # 初始化模型
        args = ARGS()
        FNNModel = FNN(args, sess)

        # 初始化数据
        dataX1X2X3 = DataX1X2X3(trainDataPath, testDataPath)
        trainData, testData = dataX1X2X3.getTrainAndTestDataFromFile()

        # 初始化 tensorflow
        sess.run(tf.global_variables_initializer())

        # 训练过程
        FNNModel.train(trainData[0], trainData[1])

        # predict
        trainDataPath = "../D/resultData_{}.txt".format(generateType)
        testDataPath = None
        dataX1X2X3 = DataX1X2X3(trainDataPath, testDataPath)
        trainData, testData = dataX1X2X3.getTrainAndTestDataFromFile()
        FNNModel.batch_size = len(trainData)
        FNNModel.predict(trainData[0], trainData[2])

        # 存储模型
        FNNModel.save("../result/model/FNNModel/{}/A0".format(generateType))

def testProcess():
    with tf.Session() as sess:
        generateType = 2

        trainDataPath = "../D/trainDataX1X2X3_{}.txt".format(generateType)
        testDataPath = None

        # 初始化模型
        args = ARGS()
        FNNModel = FNN(args, sess)

        # 初始化 tensorflow
        sess.run(tf.global_variables_initializer())

        # restore模型
        FNNModel.restoreModel("../result/model/FNNModel/{}/A0".format(generateType))

        # predict
        trainDataPath = "../D/resultData_{}.txt".format(generateType)
        testDataPath = None
        dataX1X2X3 = DataX1X2X3(trainDataPath, testDataPath)
        trainData, testData = dataX1X2X3.getTrainAndTestDataFromFile()
        FNNModel.batch_size = len(trainData)
        FNNModel.predict(trainData[0], trainData[2])


if __name__ == "__main__":
    trainProcess()
    #testProcess()



